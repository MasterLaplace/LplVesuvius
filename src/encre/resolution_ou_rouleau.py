#!/usr/bin/env python3
"""M1ter — la resolution EN PLAN suffit-elle a rendre le modele d'encre inerte ?

⚠⚠ Pourquoi ce fichier existe. `36` §5bis a repondu negativement a « l'encre est-elle
lisible a 9 µm ? » : sur `PHerc1447` a 8,64 µm, le modele du Grand Prize 2023 sort une
constante -- sigma 45 fois plus petit que sur le temoin ou il marche. Mais la mesure
laissait TROIS causes en lice, et `29` M1ter les porte encore : la resolution, ce
rouleau-ci, ou un papyrus vierge. `46` §3 a ferme la troisieme. Ce fichier attaque la
premiere, et il le fait sur le rouleau ou le modele MARCHE : on lui redonne, sur Scroll 1,
l'echantillonnage en plan de `PHerc1447`, et on regarde si sigma s'effondre.

⭐ Le mot « resolution » cachait DEUX grandeurs, et c'est la moitie du travail que de les
separer :

1. **l'echantillonnage en plan** -- une tuile de 64 px couvre 154 µm de papyrus a 2,4 µm et
   553 µm a 8,64 µm. C'est ce que ce fichier mesure.
2. **l'epaisseur de la fenetre de profondeur** -- 26 couches couvrent 62 µm a 2,4 µm et
   225 µm a 8,64 µm. ⚠ Ce fichier n'y touche PAS, deliberement : l'atteindre sur Scroll 1
   demanderait 94 couches a 2,4 µm, et ce segment n'en publie que 26. Une mesure qui ferait
   varier les deux ensemble ne dirait laquelle des deux joue -- c'est exactement le defaut
   que la comparaison publiee porte, et le reproduire ne le corrigerait pas.

⭐ **Le grossissement est une MOYENNE de bloc, jamais une decimation.** Un detecteur plus
grossier integre sur sa cellule ; prendre un pixel sur f en jetant les autres ajoute un
repliement qu'aucun scan reel ne porte, donc ferait paraitre la degradation pire qu'elle
n'est et prouverait autre chose que ce qu'on demande.

⚠⚠ **Et le controle sans lequel l'echelle ne veut rien dire.** Moyenner reduit la variance
par construction : une carte plus grossiere a un sigma plus petit meme si le modele n'a rien
perdu. Chaque barreau est donc lu contre son sigma ATTENDU -- celui qu'on obtient en
moyennant la carte du barreau natif par le meme facteur. Le rapport mesure / attendu est ce
qui separe « le modele a perdu l'encre » de « les pixels sont plus gros ».

⚠ Ce que ca n'etablira pas, quel que soit le resultat : qu'il y a ou non de l'encre sur
`PHerc1447`. Ca dit si l'echantillonnage en plan SUFFIT a expliquer l'inertie mesuree la-bas.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "xpu"))

import comparer_encre  # noqa: E402  -- une seule definition de sigma dans le depot
import infer_ink  # noqa: E402  -- une seule lecture de pile, et un seul choix d'appareil

VOXEL_UM = 2.4
"""Pas des couches de Scroll 1 (campagne ESRF), en micrometres."""

CIBLE_UM = 8.64
"""Pas de `PHerc1447`, le rouleau ou le modele est inerte. Encadre par les barreaux 3 et 4."""

QUESTION = "M1ter — l'echantillonnage en plan suffit-il a rendre le modele inerte ?"
"""Dite une seule fois : le rapport et l'aide en portaient deux copies libres de diverger."""

ANCRES = {
    "modele_marche": {"nom": "Scroll 1 entier (AUC 0,925, 2,4 µm)", "sigma": 0.7711818814277649},
    "modele_inerte": {"nom": "PHerc1447 (prix, 8,64 µm)", "sigma": 0.017066892236471176},
}
"""Les deux sigma publies (`docs/mesures/m1ter_encre_a_9um.json`), pour situer un barreau.

⚠ Ils portent sur des etendues autres que la fenetre d'ici : ils situent, ils ne bornent pas.
"""


class RefusMesure(RuntimeError):
    """Levee quand une precondition de comparabilite n'est pas tenue."""


def verifier_echelle(cote_natif: int, facteurs: list[int], tuile: int) -> None:
    """Refuse une echelle ou les barreaux ne seraient pas comparables.

    Trois conditions, et chacune repond a une facon precise de se tromper :

    1. **1 doit etre dans les facteurs.** Sans le barreau natif il n'y a ni temoin positif ni
       carte de reference pour le sigma attendu : une echelle plate de bout en bout serait
       indistinguable d'un harnais casse.
    2. **le cote natif doit etre divisible par chaque facteur**, sinon les barreaux ne
       couvrent pas la meme etendue de papyrus et on compare deux regions.
    3. **chaque entree doit rester au moins aussi grande que la tuile**, sinon le modele n'a
       aucune fenetre a poser et le barreau ne rend rien.
    """
    if 1 not in facteurs:
        raise RefusMesure("le facteur 1 est le temoin positif : sans lui l'echelle ne mesure rien")
    for f in facteurs:
        if f < 1:
            raise RefusMesure(f"facteur {f} : un grossissement est un entier positif")
        if cote_natif % f:
            raise RefusMesure(
                f"cote {cote_natif} non divisible par {f} : les barreaux ne couvriraient pas "
                "la meme etendue de papyrus")
        if cote_natif // f < tuile:
            raise RefusMesure(
                f"facteur {f} : entree {cote_natif // f} px plus petite que la tuile {tuile}")


def depart_centre(centre: int, pas: int, frames: int) -> int:
    """Le depart qui centre une fenetre de `frames` images au pas `pas` sur `centre`.

    ⚠⚠ C'est la contrepartie exacte, sur l'axe profondeur, de l'etendue commune que les
    barreaux du plan partagent. A depart FIXE, deux pas partagent leur bord proche et non
    leur milieu : le barreau epais irait chercher sa matiere ailleurs dans l'empilement, et
    on comparerait deux regions de la feuille plutot que deux epaisseurs de la meme.
    """
    return centre - (frames - 1) * pas // 2


def verifier_profondeur(dossier: Path, start: int, pas: list[int], frames: int) -> None:
    """Refuse une echelle de profondeur dont une marche sortirait de la pile publiee.

    ⚠ Le refus est PREALABLE et non decouvert a la lecture : un pas trop grand echoue
    aujourd'hui sur « couche absente » au milieu du barreau, apres avoir paye les
    precedents. Dire d'avance ce qui ne tient pas coute une seconde.
    """
    if 1 not in pas:
        raise RefusMesure("le pas 1 est le temoin positif : sans lui l'echelle ne mesure rien")
    disponibles = {int(q.stem) for q in dossier.glob("*.tif") if q.stem.isdigit()}
    if not disponibles:
        raise RefusMesure(f"aucune couche NN.tif dans {dossier}")
    for k in pas:
        if k < 1:
            raise RefusMesure(f"pas {k} : un pas est un entier positif")
        dernier = start + (frames - 1) * k
        if dernier not in disponibles:
            raise RefusMesure(
                f"pas {k} : il faudrait la couche {dernier}, et la pile s'arrete a "
                f"{max(disponibles)} -- {frames} images a ce pas demandent "
                f"{(frames - 1) * k + 1} couches")


def moyenner_par_bloc(image: np.ndarray, f: int) -> np.ndarray:
    """Moyenne f x f, ce que fait un detecteur dont la cellule est f fois plus large.

    Accepte (h, w) et (frames, h, w) : les couches se grossissent en plan, jamais en
    profondeur -- c'est toute la separation que ce fichier existe pour tenir.
    """
    if f == 1:
        return image.astype(np.float32, copy=False)
    if image.ndim == 2:
        h, w = image.shape
        return image[: h - h % f, : w - w % f].reshape(h // f, f, w // f, f).mean((1, 3))
    n, h, w = image.shape
    return image[:, : h - h % f, : w - w % f].reshape(n, h // f, f, w // f, f).mean((2, 4))


def sigma_attendu_par_moyennage(carte_native: np.ndarray, f: int) -> float:
    """Le sigma qu'on aurait si le modele n'avait RIEN perdu et que seuls les pixels grossissent.

    ⚠⚠ Sans lui l'echelle ne veut rien dire : moyenner reduit la variance par construction,
    donc un barreau grossier a un sigma plus petit meme sur une carte parfaite. C'est le
    RAPPORT mesure / attendu qui separe « le modele a perdu l'encre » de « les pixels sont
    plus gros ».

    ⚠ Les pixels non couverts sont mis a NaN AVANT de moyenner, jamais apres : les compter
    comme des zeros ferait plonger la moyenne des blocs de bord et gonflerait l'attendu,
    donc flatterait le modele exactement la ou il est le moins observe.
    """
    import warnings

    x = carte_native.astype(np.float32, copy=True)
    x[~np.isfinite(x) | (x <= comparer_encre.SENTINELLE)] = np.nan
    if f > 1:
        h, w = x.shape
        bloc = x[: h - h % f, : w - w % f].reshape(h // f, f, w // f, f)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # un bloc entierement non couvert
            x = np.nanmean(bloc, axis=(1, 3))
    v = x[np.isfinite(x)]
    return float(v.std()) if v.size else float("nan")


def fenetre_la_plus_encree(carte: np.ndarray, cote: int, pas: int) -> tuple[int, int, float]:
    """Le coin (haut, gauche) de la fenetre `cote` x `cote` ou la carte PUBLIEE varie le plus.

    ⚠ Choisir la fenetre sur la prediction publiee et non sur les couches est assume : il
    faut de l'encre dans la fenetre pour qu'une echelle ait la moindre amplitude a perdre.
    Le choix ne favorise aucun barreau -- tous lisent la MEME fenetre --, il garantit
    seulement que l'echelle a quelque chose a mesurer.
    """
    h, w = carte.shape
    meilleur = (0, 0, -1.0)
    for top in range(0, h - cote + 1, pas):
        for left in range(0, w - cote + 1, pas):
            bloc = carte[top : top + cote, left : left + cote]
            v = bloc[np.isfinite(bloc)]
            s = float(v.std()) if v.size else -1.0
            if s > meilleur[2]:
                meilleur = (top, left, s)
    return meilleur


def barreau(f: int, prediction: np.ndarray, carte_native: np.ndarray, chemin: Path,
            fenetres: int | None = None, secondes: float | None = None,
            facteur_attendu: int | None = None, pas_couches: int = 1,
            facteur_plan: int | None = None) -> dict:
    """Une marche de l'echelle, lue de la MEME facon qu'elle vienne du modele ou du disque.

    ⚠ `sigma` passe par `comparer_encre.statistiques`, pas par un `std` ecrit ici : ce depot
    a une seule definition de « l'ecart-type d'une carte d'encre », et deux repondraient un
    jour deux choses au sujet du meme fichier.
    """
    stats = comparer_encre.statistiques(chemin)
    attendu = sigma_attendu_par_moyennage(carte_native, f if facteur_attendu is None else facteur_attendu)
    return {
        "facteur": f,
        "echantillonnage_um": round(VOXEL_UM * (f if facteur_plan is None else facteur_plan), 3),
        "profondeur_um": round(VOXEL_UM * pas_couches * infer_ink.FRAMES, 1),
        "entree_px": int(prediction.shape[-1]),
        "fenetres": fenetres,
        "secondes": None if secondes is None else round(secondes, 1),
        "sigma": stats["sigma"],
        "sigma_attendu_par_moyennage": attendu,
        "rapport_mesure_sur_attendu": (stats["sigma"] / attendu) if attendu else None,
        "etendue": stats["etendue"],
        "median": stats["median"],
        "n_pixels_couverts": stats["n"],
    }


def dire(b: dict) -> None:
    """Une marche, sur une ligne."""
    r = b["rapport_mesure_sur_attendu"]
    if r is None:
        print(f"  x{b['facteur']} : attendu nul, rapport indefini")
        return
    print(f"  x{b['facteur']}  plan {b['echantillonnage_um']:>5.2f} µm  "
          f"profondeur {b['profondeur_um']:>6.1f} µm  entree {b['entree_px']:>4} px  "
          f"sigma {b['sigma']:.4f}  attendu {b['sigma_attendu_par_moyennage']:.4f}  "
          f"rapport {r:.3f}")


def verifier() -> int:
    """Auto-test HORS LIGNE : ni torch, ni modele, ni couche."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- la moyenne de bloc ---------------------------------------------------------
    a = np.arange(16, dtype=np.float32).reshape(4, 4)
    v("facteur 1 rend l'image telle quelle", np.array_equal(moyenner_par_bloc(a, 1), a))
    b = moyenner_par_bloc(a, 2)
    v("facteur 2 rend une image deux fois plus petite", b.shape == (2, 2))
    v("... et chaque valeur est la MOYENNE du bloc, pas un echantillon",
      abs(float(b[0, 0]) - float(a[:2, :2].mean())) < 1e-6)
    v("... ce qui differe d'une decimation", abs(float(b[0, 0]) - float(a[0, 0])) > 1e-6)

    pile = np.stack([a, a * 2.0])
    p2 = moyenner_par_bloc(pile, 2)
    v("une pile se grossit en plan", p2.shape == (2, 2, 2))
    v("... et JAMAIS en profondeur -- le nombre de couches ne bouge pas",
      p2.shape[0] == pile.shape[0])

    # ⚠ Le controle qui donne son sens au sigma attendu : moyenner REDUIT la dispersion,
    # donc un barreau grossier a un sigma plus petit sans qu'aucun modele n'ait rien perdu.
    bruit = np.random.default_rng(0).normal(size=(64, 64)).astype(np.float32)
    v("moyenner reduit la dispersion, donc il FAUT un attendu",
      float(moyenner_par_bloc(bruit, 4).std()) < 0.6 * float(bruit.std()))

    # --- le sigma attendu, celui qui donne une echelle au sigma mesure -----------------
    lisse = np.tile(np.linspace(0.0, 1.0, 32, dtype=np.float32), (32, 1))
    v("une carte lisse ne perd presque rien au moyennage",
      sigma_attendu_par_moyennage(lisse, 4) > 0.97 * float(lisse.std()))
    v("... alors qu'une carte de bruit en perd beaucoup",
      sigma_attendu_par_moyennage(bruit, 4) < 0.6 * float(bruit.std()))
    v("le barreau natif est son propre attendu, donc son rapport vaut 1",
      abs(sigma_attendu_par_moyennage(lisse, 1) - float(lisse.std())) < 1e-6)

    # ⚠⚠ Les pixels non couverts doivent etre ECARTES et non comptes comme des zeros : les
    # compter ferait plonger la moyenne des blocs de bord et gonflerait l'attendu, donc
    # flatterait le modele exactement la ou il est le moins observe.
    troue = lisse.copy()
    troue[:8, :] = np.nan
    v("les pixels non couverts sont ecartes, pas comptes comme zero",
      abs(sigma_attendu_par_moyennage(troue, 4)
          - sigma_attendu_par_moyennage(lisse[8:, :], 4)) < 0.02)
    v("... et une carte entierement non couverte le DIT au lieu de rendre zero",
      np.isnan(sigma_attendu_par_moyennage(np.full((16, 16), np.nan, dtype=np.float32), 2)))

    # --- les refus ------------------------------------------------------------------
    ok = True
    try:
        verifier_echelle(1008, [1, 2, 3, 4], 64)
    except RefusMesure:
        ok = False
    v("une echelle comparable est acceptee", ok)

    for nom, args in (
        ("sans le barreau natif, l'echelle est refusee", (1008, [2, 4], 64)),
        ("un cote non divisible est refuse", (1000, [1, 3], 64)),
        ("une entree plus petite que la tuile est refusee", (128, [1, 4], 64)),
        ("un facteur nul est refuse", (1008, [1, 0], 64)),
    ):
        try:
            verifier_echelle(*args)
            v(nom, False)
        except RefusMesure:
            v(nom, True)

    # --- les refus de l'axe profondeur ------------------------------------------------
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        rep = Path(d)
        for i in range(65):
            (rep / f"{i:02d}.tif").write_bytes(b"")
        ok = True
        try:
            verifier_profondeur(rep, 0, [1, 2], 26)
        except RefusMesure:
            ok = False
        v("un pas qui tient dans la pile est accepte", ok)
        for nom, args_ in (
            ("un pas qui sortirait de la pile est refuse", (rep, 15, [1, 3], 26)),
            ("... et le refus le dit AVANT de payer les barreaux precedents",
             (rep, 40, [1, 2], 26)),
            ("sans le pas 1, l'echelle de profondeur est refusee", (rep, 15, [2], 26)),
        ):
            try:
                verifier_profondeur(*args_)
                v(nom, False)
            except RefusMesure:
                v(nom, True)
        try:
            verifier_profondeur(rep / "vide", 15, [1], 26)
            v("un repertoire sans couche est refuse", False)
        except RefusMesure:
            v("un repertoire sans couche est refuse", True)

    v("un depart centre place le milieu de la fenetre sur la couche demandee",
      depart_centre(32, 1, 26) + (26 - 1) // 2 == 32)
    v("... et deux pas differents partagent ce milieu, pas leur bord",
      abs((depart_centre(32, 2, 26) + (26 - 1) * 2 // 2)
          - (depart_centre(32, 1, 26) + (26 - 1) // 2)) <= 1)
    v("... alors qu'a depart fixe ils partagent le bord et divergent au milieu",
      abs((0 + (26 - 1) * 2 // 2) - (0 + (26 - 1) // 2)) > 1)

    # --- le choix de fenetre ---------------------------------------------------------
    carte = np.zeros((32, 32), dtype=np.float32)
    carte[16:32, 16:32] = np.random.default_rng(1).normal(size=(16, 16))
    top, left, s = fenetre_la_plus_encree(carte, 16, 16)
    v("la fenetre retenue est celle qui varie le plus", (top, left) == (16, 16) and s > 0)
    v("... et une carte plate n'en privilegie aucune",
      fenetre_la_plus_encree(np.zeros((32, 32), dtype=np.float32), 16, 16)[:2] == (0, 0))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=QUESTION)
    p.add_argument("layers", nargs="?", type=Path, help="repertoire des couches (NN.tif)")
    p.add_argument("--model", type=Path, help="repertoire du modele")
    p.add_argument("--carte-publiee", type=Path,
                   help="prediction publiee du meme segment, pour choisir la fenetre")
    p.add_argument("--start-layer", type=int, default=15)
    p.add_argument("--cote", type=int, default=1008,
                   help="cote de la fenetre NATIVE, identique pour tous les barreaux")
    p.add_argument("--axe", default="plan", choices=("plan", "profondeur"),
                   help="quelle des deux grandeurs que le mot « resolution » confondait")
    p.add_argument("--facteurs", default="1,2,3,4",
                   help="grossissements en plan, ou pas de couches ; 1 est obligatoire")
    p.add_argument("--pas-couches", type=int, default=1,
                   help="axe plan : epaissir AUSSI la fenetre de profondeur, pour croiser "
                        "les deux grandeurs et voir si leurs effets se multiplient")
    p.add_argument("--centre-couche", type=int,
                   help="axe profondeur : la couche sur laquelle CENTRER chaque barreau")
    p.add_argument("--top", type=int, help="coin de la fenetre, sinon choisi sur la carte publiee")
    p.add_argument("--left", type=int)
    p.add_argument("--stride", type=int, default=21)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--threads", type=int, default=16)
    p.add_argument("--device", default="auto", choices=("auto", "cpu", "xpu"))
    p.add_argument("--sorties", type=Path, help="repertoire ou deposer les cartes .npy")
    p.add_argument("--json", type=Path, help="rapport")
    p.add_argument("--depuis", type=Path,
                   help="recalculer le rapport depuis des cartes deja rendues, sans modele")
    p.add_argument("--verifier", action="store_true")
    args = p.parse_args()
    if args.verifier:
        return verifier()

    # ⭐ Refaire le rapport a partir des SEULS enregistrements, sans modele ni couche. Une
    # mesure qu'on ne peut relire qu'en la refaisant n'est pas verifiable, et ce depot a deja
    # paye de republier un chiffre plutot que de le recalculer.
    if args.depuis is not None:
        cartes = sorted(args.depuis.glob("barreau_x*.npy"),
                        key=lambda q: int(q.stem.split("x")[-1]))
        if not cartes:
            print(f"erreur : aucune carte barreau_x*.npy dans {args.depuis}", file=sys.stderr)
            return 2
        natif = next((q for q in cartes if q.stem.endswith("x1")), None)
        if natif is None:
            print("erreur : le barreau natif (x1) manque, donc l'attendu n'a pas de reference",
                  file=sys.stderr)
            return 2
        carte_native = np.load(natif)
        barreaux = []
        for q in cartes:
            f = int(q.stem.split("x")[-1])
            barreaux.append(barreau(f, np.load(q), carte_native, q,
                                    facteur_attendu=1 if args.axe == "profondeur" else f,
                                    pas_couches=f if args.axe == "profondeur" else args.pas_couches,
                                    facteur_plan=1 if args.axe == "profondeur" else f))
            dire(barreaux[-1])
        rapport = {"question": QUESTION, "axe": args.axe, "source": str(args.depuis),
                   "ancres": ANCRES, "barreaux": barreaux}
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(rapport, indent=2, ensure_ascii=False) + "\n")
            print(f"rapport           : {args.json}")
        return 0

    manquants = [n for n in ("layers", "model", "sorties") if getattr(args, n) is None]
    if args.carte_publiee is None and (args.top is None or args.left is None):
        manquants.append("carte-publiee (ou --top et --left)")
    if manquants:
        p.error("manquant(s) : " + ", ".join(manquants))

    try:
        infer_ink.exiger_les_modules(
            infer_ink.modules_manquants(lambda n: __import__("importlib.util", fromlist=["util"]).find_spec(n) is not None))
    except infer_ink.InferenceError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 3

    facteurs = sorted({int(x) for x in args.facteurs.split(",")})
    try:
        if args.axe == "plan":
            verifier_echelle(args.cote, facteurs, infer_ink.TILE)
            verifier_profondeur(
                args.layers,
                depart_centre(args.centre_couche, args.pas_couches, infer_ink.FRAMES)
                if args.centre_couche is not None else args.start_layer,
                [1, args.pas_couches] if args.pas_couches != 1 else [1], infer_ink.FRAMES)
        else:
            verifier_echelle(args.cote, [1], infer_ink.TILE)
            for k in facteurs:
                depart = (depart_centre(args.centre_couche, k, infer_ink.FRAMES)
                          if args.centre_couche is not None else args.start_layer)
                verifier_profondeur(args.layers, depart, [1, k] if k != 1 else [1],
                                    infer_ink.FRAMES)
    except RefusMesure as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    if args.top is not None and args.left is not None:
        top, left, sigma_fenetre = args.top, args.left, None
        print(f"fenetre donnee    : top={top} left={left} cote={args.cote}")
    else:
        carte = np.load(args.carte_publiee, mmap_mode="r")
        top, left, sigma_fenetre = fenetre_la_plus_encree(
            np.asarray(carte), args.cote, args.cote // 2)
        print(f"fenetre retenue   : top={top} left={left} cote={args.cote} "
              f"(sigma de la carte publiee : {sigma_fenetre:.4f})")

    import torch
    appareil, raison = infer_ink.choisir_appareil(
        args.device, hasattr(torch, "xpu") and torch.xpu.is_available())
    print(f"appareil          : {appareil} ({raison})")

    from transformers import AutoModel
    model = AutoModel.from_pretrained(str(args.model), trust_remote_code=True).eval().to(appareil)

    args.sorties.mkdir(parents=True, exist_ok=True)
    crop = (top, left, args.cote, args.cote)
    depart_plan = (depart_centre(args.centre_couche, args.pas_couches, infer_ink.FRAMES)
                   if args.centre_couche is not None else args.start_layer)
    natif = (infer_ink.load_layer_stack(args.layers, depart_plan, crop, args.pas_couches)
             if args.axe == "plan" else None)

    barreaux, carte_native = [], None
    for f in facteurs:
        if args.axe == "plan":
            pile = moyenner_par_bloc(natif, f)
        else:
            # ⚠ La pile est RELUE a chaque pas : ce sont d'autres couches, pas une vue de la
            # meme. C'est toute la difference entre epaissir la fenetre et la moyenner.
            depart = (depart_centre(args.centre_couche, f, infer_ink.FRAMES)
                      if args.centre_couche is not None else args.start_layer)
            pile = infer_ink.load_layer_stack(args.layers, depart, crop, f)
        prediction, fenetres, secondes = infer_ink.infer(
            pile, model, args.stride, args.batch_size, args.threads, appareil)
        chemin = args.sorties / f"barreau_x{f}.npy"
        np.save(chemin, prediction)
        if f == 1:
            carte_native = prediction
        # ⚠⚠ Sur l'axe PROFONDEUR la grille de sortie ne bouge pas d'un pixel, donc il n'y a
        # aucun moyennage a corriger : l'attendu est le sigma natif lui-meme, et le rapport
        # se lit directement comme « ce qui reste de la reponse ». Passer le facteur ici
        # aurait corrige une reduction de variance qui n'a pas lieu.
        barreaux.append(barreau(f, prediction, carte_native, chemin, fenetres, secondes,
                                facteur_attendu=1 if args.axe == "profondeur" else f,
                                pas_couches=f if args.axe == "profondeur" else args.pas_couches,
                                facteur_plan=1 if args.axe == "profondeur" else f))
        dire(barreaux[-1])

    rapport = {
        "question": QUESTION,
        "axe": args.axe,
        "segment": args.layers.name,
        "voxel_um": VOXEL_UM,
        "cible_um": CIBLE_UM,
        "fenetre": {"top": top, "left": left, "cote": args.cote,
                    "sigma_carte_publiee": sigma_fenetre},
        "couche_depart": args.start_layer,
        "couches": infer_ink.FRAMES,
        "ancres": ANCRES,
        "barreaux": barreaux,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(rapport, indent=2, ensure_ascii=False) + "\n")
        print(f"rapport           : {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
