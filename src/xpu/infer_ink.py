#!/usr/bin/env python3
"""Detection d'encre par fenetre glissante, a partir des couches publiees.

Reprend EXACTEMENT la convention d'accumulation de la soumission gagnante 2023 :
la sortie 4x4 du modele est remontee en 64x64 par interpolation bilineaire, cumulee
dans une carte, avec un compteur de recouvrement, puis divisee. Toute autre
convention produirait une carte qui n'est comparable a rien de publie.

Le pas de balayage est un PARAMETRE et non une constante, parce que c'est le seul
reglage qui echange du temps contre de la resolution : la reference utilise
tile_size // 3 = 21, une variante publiee utilise 32, et l'ecart entre les deux
n'est chiffre nulle part.

⭐ UN SEUL fichier pour les deux appareils, et `--device auto` par defaut : XPU s'il y en a
un, CPU sinon, et la raison du choix est IMPRIMEE. C'est ce qui remplace le dossier
`inference/`, qui portait un second environnement CPU pour la seule raison de rejouer le
temoin du ×4,5 iGPU.

⚠⚠ Et le temoin est PLUS solide en mode qu'en dossier. Deux dossiers, c'etaient deux
constructions de torch differentes -- generique d'un cote, `2.9.1+xpu` de l'autre -- donc la
comparaison melangeait l'appareil ET la build. Ici `--device cpu` contre `--device xpu`
change UNE variable, et c'est ce qu'un temoin doit faire. Mesure du 2026-08-25 : la build
`+xpu` execute le chemin CPU sans rien de special.

⚠ « auto » retombe, « xpu » REFUSE. Voir `choisir_appareil`.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np
import tifffile

TILE = 64
"""Cote de la fenetre, impose par le modele (`window_size` de sa config)."""

FRAMES = 26
"""Nombre de couches attendu par le modele (`num_frames`)."""


class InferenceError(RuntimeError):
    """Leve quand une precondition n'est pas tenue."""


MODULES_DU_MODELE = ("torch", "transformers", "timesformer_pytorch")
"""Ce qu'il faut pour CHARGER le modele, et que les dependances de base ne portent pas.

⚠⚠ Ces modules ne sont pas dans `[project.dependencies]` et c'est deliberate : la racine
annonce « numpy et pas grand-chose », et torch seul installe ~700 Mio -- mesure du 2026-08-27,
contre 3,8 Gio si on le prend sur l'index par defaut, qui ajoute 2,7 Gio de runtime CUDA
qu'aucun peripherique d'ici ne peut executer. Mais
tant que rien ne le DISAIT, l'outil promettait de tourner et rendait un `ModuleNotFoundError`
nu -- mesure du 2026-08-27 : arguments valides, modele present dans `data/models/`, et une
trace de pile pour toute explication. Une promesse d'outil autonome qu'on ne peut pas
executer est une promesse fausse, et ce depot l'a deja paye a la racine du `pyproject`.

⚠ Le troisieme n'apparait dans AUCUN import de ce fichier : `timesformer_pytorch` est
importe par le code du modele lui-meme, charge par `trust_remote_code`. Lister les seuls
imports visibles ici aurait donc rendu un refus complet suivi, une fois repare, d'une
seconde trace de pile -- un remede qui ne repare pas du premier coup.
"""


def modules_manquants(present) -> list[str]:
    """Ceux des modules du modele que cet environnement n'a pas, dans l'ordre declare.

    ⚠ La disponibilite est un ARGUMENT et non une interrogation, pour la meme raison que
    dans `choisir_appareil` : c'est ce qui rend le refus testable dans un environnement qui,
    justement, ne les a pas.
    """
    return [nom for nom in MODULES_DU_MODELE if not present(nom)]


def exiger_les_modules(manquants: list[str]) -> None:
    """Refuse en NOMMANT ce qui manque et la commande qui le repare.

    Un refus muet envoie deviner, et deviner est ce que ce depot paie en boucle.
    """
    if not manquants:
        return
    raise InferenceError(
        "module(s) absent(s) pour charger le modele : " + ", ".join(manquants)
        + " -- ils ne sont pas dans les dependances de base (torch installe ~700 Mio) ;"
        + " remede : uv sync --extra encre"
    )


def choisir_appareil(demande: str, xpu_disponible: bool) -> tuple[str, str]:
    """L'appareil retenu et la RAISON de ce choix, dite au lieu d'etre devinee.

    ⚠⚠ La regle qui fait la difference entre un pipeline adaptatif et un pipeline
    silencieux : « auto » RETOMBE, « xpu » REFUSE. Demander explicitement le GPU et
    obtenir le CPU sans le savoir ferait publier un temps mesure sur l'autre appareil --
    c'est exactement la panne que le repli est cense eviter, deplacee d'un cran.

    ⭐ Prend la disponibilite en ARGUMENT plutot que d'interroger torch : la regle se teste
    alors sur une machine sans GPU, et sur une machine sans torch du tout.
    """
    if demande == "xpu":
        if not xpu_disponible:
            raise InferenceError(
                "--device xpu demande, mais aucun XPU n'est disponible. "
                "Utiliser --device auto pour retomber sur le CPU, ou --device cpu pour l'exiger."
            )
        return "xpu", "demande explicitement"
    if demande == "cpu":
        return "cpu", "demande explicitement"
    if demande != "auto":
        raise InferenceError(f"appareil inconnu : {demande}")
    if xpu_disponible:
        return "xpu", "detecte"
    return "cpu", "repli, aucun XPU detecte"


def indices_des_couches(start: int, pas: int = 1) -> list[int]:
    """Les indices que la pile lira -- une seule reponse a « quelle couche ».

    ⚠ Elle est SEPAREE de la lecture parce qu'une sonde qui passe par le disque s'arrete a
    la premiere couche absente : elle ne verrait donc jamais la deuxieme, c'est-a-dire
    justement celle ou un pas se distingue d'un autre. Un controle qui ne peut pas
    distinguer pas=1 de pas=2 est un controle qui ne controle rien.
    """
    if pas < 1:
        raise InferenceError(f"pas de couches {pas} : un pas est un entier positif")
    return [start + index * pas for index in range(FRAMES)]


def load_layer_stack(layers_dir: Path, start: int, crop: tuple[int, int, int, int],
                     pas: int = 1) -> np.ndarray:
    """Charge FRAMES couches sur une fenetre, en (frames, h, w).

    Les couches sont lues par fenetre et non en entier : une couche fait 6655 x
    35653 en uint16, soit 474 Mo, donc les 26 tiendraient 12 Go pour une region
    qui en demande quelques dizaines de mebioctets.

    ⚠⚠ `pas` prend une couche sur `pas`, donc EPAISSIT la fenetre de profondeur sans
    changer le nombre d'images que le modele mange. C'est la seule facon de faire varier la
    grandeur que `36` §5bis a laissee confondue avec la resolution en plan : a 8,64 µm,
    26 couches couvrent 225 µm la ou l'entrainement en voyait 62. Le defaut est 1, donc
    aucun appel existant ne bouge.
    """
    top, left, height, width = crop
    stack = np.zeros((FRAMES, height, width), dtype=np.float32)
    for index, couche in enumerate(indices_des_couches(start, pas)):
        path = layers_dir / f"{couche:02d}.tif"
        if not path.is_file():
            raise InferenceError(f"couche absente : {path}")
        with tifffile.TiffFile(path) as handle:
            page = handle.pages[0]
            full = page.asarray()
            stack[index] = full[top : top + height, left : left + width].astype(np.float32)
            del full
    # Le modele a ete entraine sur des entrees normalisees a [0, 1] depuis du
    # uint16 ; garder l'echelle brute donnerait des activations hors domaine.
    return stack / 65535.0


def infer(
    stack: np.ndarray,
    model,
    stride: int,
    batch_size: int,
    threads: int,
    device: str = "cpu",
) -> tuple[np.ndarray, int, float]:
    """Balaie la fenetre et rend (carte d'encre, nombre de fenetres, secondes).

    Le peripherique est un parametre : l'iGPU Arc rend le meme resultat que le CPU
    a 4.9e-6 pres (bruit fp32, verifie) pour 4.5 fois moins de temps. La
    synchronisation explicite avant de chronometrer n'est pas cosmetique -- sans
    elle on mesure le temps de mise en file, pas celui du calcul.
    """
    import torch
    import torch.nn.functional as F

    torch.set_num_threads(threads)
    _, height, width = stack.shape
    if height < TILE or width < TILE:
        raise InferenceError(f"fenetre {height}x{width} plus petite que la tuile {TILE}")

    prediction = np.zeros((height, width), dtype=np.float32)
    overlap = np.zeros((height, width), dtype=np.float32)

    positions = [
        (y, x)
        for y in range(0, height - TILE + 1, stride)
        for x in range(0, width - TILE + 1, stride)
    ]

    if device == "xpu":
        torch.xpu.synchronize()
    started = time.perf_counter()
    with torch.no_grad():
        for begin in range(0, len(positions), batch_size):
            chunk = positions[begin : begin + batch_size]
            batch = np.stack([stack[:, y : y + TILE, x : x + TILE] for y, x in chunk])
            tensor = torch.from_numpy(batch).unsqueeze(1).to(device)
            output = model(tensor)
            upscaled = (
                F.interpolate(output.float(), scale_factor=16, mode="bilinear")
                .squeeze(1)
                .cpu()
                .numpy()
            )
            for (y, x), tile in zip(chunk, upscaled):
                prediction[y : y + TILE, x : x + TILE] += tile
                overlap[y : y + TILE, x : x + TILE] += 1.0
    if device == "xpu":
        torch.xpu.synchronize()
    elapsed = time.perf_counter() - started

    prediction /= np.clip(overlap, 1.0, None)
    # Les bords que le balayage n'atteint jamais restent a zero et sont ecartes :
    # une moyenne qui les inclurait melangerait « pas d'encre » et « pas regarde ».
    prediction[overlap == 0] = np.nan
    return prediction, len(positions), elapsed


def verifier() -> int:
    """Auto-test HORS LIGNE : ni torch, ni GPU, ni modele. C'est pourquoi le choix
    d'appareil prend la disponibilite en argument plutot que de l'interroger."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    a, r = choisir_appareil("auto", True)
    v("auto prend le XPU quand il y en a un", a == "xpu" and r)
    a, r = choisir_appareil("auto", False)
    v("auto RETOMBE sur le CPU sinon", a == "cpu")
    v("... et la raison le dit, au lieu de le taire", "repli" in r)

    v("cpu explicite reste sur le CPU meme si un XPU est la",
      choisir_appareil("cpu", True)[0] == "cpu")
    v("xpu explicite prend le XPU quand il y en a un",
      choisir_appareil("xpu", True)[0] == "xpu")

    # ⚠⚠ Le controle qui donne son sens au repli : « auto » et « xpu » doivent DIVERGER
    # quand le GPU manque. S'ils retombaient tous les deux, le refus ne servirait a rien et
    # un temps mesure sur CPU pourrait etre publie comme un temps GPU.
    try:
        choisir_appareil("xpu", False)
        v("xpu explicite REFUSE plutot que de retomber", False)
    except InferenceError as e:
        v("xpu explicite REFUSE plutot que de retomber", True)
        v("... et le refus nomme le remede", "--device auto" in str(e))

    try:
        choisir_appareil("gpu", True)
        v("un appareil inconnu est refuse", False)
    except InferenceError:
        v("un appareil inconnu est refuse", True)

    # Le drapeau declare exactement les trois mots que la fonction sait traiter : un
    # quatrieme choix dans argparse serait accepte a la ligne de commande et refuse ici.
    import argparse as _a
    p = _a.ArgumentParser()
    p.add_argument("--device", default="auto", choices=("auto", "cpu", "xpu"))
    mots = p._actions[-1].choices
    v("les mots du drapeau sont ceux que la regle traite",
      set(mots) == {"auto", "cpu", "xpu"})
    ok = True
    for m in mots:
        try:
            choisir_appareil(m, True)
        except InferenceError:
            ok = False
    v("... et chacun est traite sans lever quand l'appareil est la", ok)

    # --- Le refus quand l'environnement n'a pas de quoi charger le modele -------------
    # ⚠ Ces controles portent sur le COMPORTEMENT et non sur le texte du fichier : une
    # sonde qui grep une chaine contenue dans le script qui la contient ne peut pas
    # echouer, et ce depot vient de payer ce piege sur le lanceur de VC3D.
    v("rien ne manque quand les deux modules sont la",
      modules_manquants(lambda _: True) == [])
    v("les deux sont nommes quand aucun n'est la",
      modules_manquants(lambda _: False) == list(MODULES_DU_MODELE))
    v("un seul absent n'en nomme qu'un",
      modules_manquants(lambda nom: nom != "torch") == ["torch"])
    v("l'ordre est celui de la declaration, pas celui du hasard",
      modules_manquants(lambda _: False) == [m for m in MODULES_DU_MODELE])

    ok = True
    try:
        exiger_les_modules([])
    except InferenceError:
        ok = False
    v("un environnement complet ne leve pas", ok)

    try:
        exiger_les_modules(["torch"])
        v("un environnement incomplet REFUSE", False)
    except InferenceError as e:
        v("un environnement incomplet REFUSE", True)
        v("... et le refus nomme le module manquant", "torch" in str(e))
        v("... et il nomme la commande qui repare", "uv sync --extra encre" in str(e))

    # ⚠⚠ Le controle qui donne son sens aux precedents : le refus doit tomber AVANT que
    # quoi que ce soit ne soit lu. Mesure : `main()` refuse dans un environnement nu, sur
    # une commande dont tous les arguments sont valides, sans toucher aux couches.
    v("le module expose le refus a main(), pas seulement a l'appelant",
      "exiger_les_modules" in main.__code__.co_names)

    # --- le pas de profondeur ---------------------------------------------------------
    v("sans pas, les couches sont consecutives",
      indices_des_couches(15, 1) == list(range(15, 15 + FRAMES)))
    v("un pas de 2 saute une couche sur deux",
      indices_des_couches(15, 2) == [15 + 2 * i for i in range(FRAMES)])
    v("... et un pas de 2 lit donc DEUX FOIS plus loin qu'un pas de 1",
      indices_des_couches(0, 2)[-1] == 2 * indices_des_couches(0, 1)[-1])
    v("la premiere couche reste celle qu'on a demandee, quel que soit le pas",
      {indices_des_couches(15, p)[0] for p in (1, 2, 3)} == {15})
    v("le modele mange toujours le meme nombre d'images",
      all(len(indices_des_couches(0, p)) == FRAMES for p in (1, 2, 3)))
    try:
        indices_des_couches(15, 0)
        v("un pas nul est refuse", False)
    except InferenceError:
        v("un pas nul est refuse", True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detection d'encre CPU sur une region, a partir des couches rendues.",
    )
    parser.add_argument("layers", nargs="?", type=Path, help="repertoire contenant NN.tif")
    parser.add_argument("--model", type=Path, help="repertoire du modele")
    parser.add_argument("--start-layer", type=int, default=15, help="premiere couche (defaut: 15)")
    parser.add_argument("--top", type=int)
    parser.add_argument("--left", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--stride", type=int, default=21, help="pas de balayage (defaut: 21)")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "xpu"),
                        help="auto retombe sur le CPU si aucun XPU ; xpu REFUSE plutot que de retomber")
    parser.add_argument("--verifier", action="store_true", help="auto-test hors ligne")
    parser.add_argument("--out", type=Path, help="sortie .npy")
    args = parser.parse_args()
    if args.verifier:
        return verifier()
    manquants = [n for n in ("layers", "model", "top", "left", "height", "width", "out")
                 if getattr(args, n) is None]
    if manquants:
        parser.error("manquant(s) : " + ", ".join(manquants))

    try:
        exiger_les_modules(modules_manquants(lambda nom: importlib.util.find_spec(nom) is not None))
    except InferenceError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 3

    from transformers import AutoModel

    try:
        stack = load_layer_stack(
            args.layers, args.start_layer, (args.top, args.left, args.height, args.width)
        )
    except InferenceError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    import torch

    try:
        appareil, raison = choisir_appareil(
            args.device, hasattr(torch, "xpu") and torch.xpu.is_available())
    except InferenceError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2
    print(f"appareil          : {appareil} ({raison})")

    model = AutoModel.from_pretrained(str(args.model), trust_remote_code=True).eval()
    model = model.to(appareil)
    prediction, windows, elapsed = infer(
        stack, model, args.stride, args.batch_size, args.threads, appareil
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.out, prediction)
    covered = np.isfinite(prediction)
    print(f"pas de balayage   : {args.stride}")
    print(f"fenetres          : {windows}")
    print(f"duree             : {elapsed:.1f} s  ({elapsed / max(windows, 1) * 1000:.0f} ms/fenetre)")
    print(f"pixels couverts   : {int(covered.sum())} / {prediction.size}")
    print(f"encre  min/med/max: {np.nanmin(prediction):.3f} / "
          f"{np.nanmedian(prediction):.3f} / {np.nanmax(prediction):.3f}")
    print(f"sortie            : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
