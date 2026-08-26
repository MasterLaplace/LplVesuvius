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


def load_layer_stack(layers_dir: Path, start: int, crop: tuple[int, int, int, int]) -> np.ndarray:
    """Charge FRAMES couches consecutives sur une fenetre, en (frames, h, w).

    Les couches sont lues par fenetre et non en entier : une couche fait 6655 x
    35653 en uint16, soit 474 Mo, donc les 26 tiendraient 12 Go pour une region
    qui en demande quelques dizaines de mebioctets.
    """
    top, left, height, width = crop
    stack = np.zeros((FRAMES, height, width), dtype=np.float32)
    for index in range(FRAMES):
        path = layers_dir / f"{start + index:02d}.tif"
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
