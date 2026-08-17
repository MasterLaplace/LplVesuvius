#!/usr/bin/env python3
"""Rendre une carte d'encre en images lisibles par un humain.

Trois choix qui ne sont pas cosmetiques :

1. **Le gris uni est reserve au « pas regarde ».** Les pixels que le balayage
   n'atteint pas ne sont ni du fond ni de l'absence d'encre, et les peindre en
   blanc ferait croire a un papyrus vierge la ou personne n'a mesure.
2. **L'echelle est fixee par quantiles et non par le min/max.** Une seule valeur
   extreme suffirait a ecraser tout le reste dans un gris uniforme -- et la sortie
   du modele porte une queue longue (q99 a +2,44 pour une mediane a -1,13).
3. **La reduction se fait par MAXIMUM et non par moyenne.** Un trait d'encre fait
   quelques pixels de large ; le moyenner avec son voisinage clair le fait
   disparaitre, donc une reduction en moyenne montrerait moins de texte qu'il n'y
   en a. Le maximum garde le trait au prix d'un fond plus bruite -- c'est le bon
   compromis quand la question est « y a-t-il des lettres ».
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

UNSEEN_GREY = 128
"""Gris du « pas regarde ». Choisi au milieu pour ne ressembler ni a l'encre ni au fond."""


def reduce_max(array: np.ndarray, factor: int) -> np.ndarray:
    """Reduction par maximum sur des blocs carres, en gardant les NaN separes.

    Un bloc entierement non couvert reste NaN ; un bloc partiellement couvert prend
    le maximum de ce qui a ete regarde. Melanger les deux perdrait la distinction
    que la couleur du §1 existe pour porter.
    """
    if factor <= 1:
        return array
    height = (array.shape[0] // factor) * factor
    width = (array.shape[1] // factor) * factor
    blocks = array[:height, :width].reshape(
        height // factor, factor, width // factor, factor
    )
    with np.errstate(invalid="ignore"):
        return np.nanmax(blocks, axis=(1, 3))


def to_image(scores: np.ndarray, low_q: float, high_q: float, invert: bool) -> np.ndarray:
    """Carte de scores -> niveaux de gris 8 bits, avec le gris du non-couvert."""
    covered = np.isfinite(scores)
    if not covered.any():
        raise ValueError("aucun pixel couvert")
    low = float(np.quantile(scores[covered], low_q))
    high = float(np.quantile(scores[covered], high_q))
    if high <= low:
        high = low + 1e-6
    normalised = np.clip((scores - low) / (high - low), 0.0, 1.0)
    # L'encre est SOMBRE, comme sur un papyrus : l'oeil lit une trace d'encre, pas
    # une carte de chaleur, et l'inversion evite de reapprendre a lire l'image.
    grey = (255.0 * (1.0 - normalised)) if invert else (255.0 * normalised)
    out = np.full(scores.shape, UNSEEN_GREY, dtype=np.uint8)
    out[covered] = grey[covered].astype(np.uint8)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rendre une carte d'encre .npy en PNG.",
        epilog="Reduction par maximum : un trait fin survit, contrairement a une moyenne.",
    )
    parser.add_argument("prediction", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--reduce", type=int, default=1, help="facteur de reduction (defaut: 1)")
    parser.add_argument("--top", type=int, default=0)
    parser.add_argument("--left", type=int, default=0)
    parser.add_argument("--height", type=int, default=0, help="0 = jusqu'en bas")
    parser.add_argument("--width", type=int, default=0, help="0 = jusqu'a droite")
    parser.add_argument("--low", type=float, default=0.02, help="quantile bas de l'echelle")
    parser.add_argument("--high", type=float, default=0.995, help="quantile haut de l'echelle")
    parser.add_argument(
        "--no-invert", action="store_false", dest="invert",
        help="rendre l'encre CLAIRE au lieu de sombre",
    )
    parser.add_argument(
        "--rotate", type=int, default=0, choices=[0, 90, 180, 270],
        help="rotation en degres, anti-horaire (defaut: 0)",
    )
    args = parser.parse_args()

    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    scores = np.load(args.prediction)
    height = args.height or scores.shape[0] - args.top
    width = args.width or scores.shape[1] - args.left
    crop = scores[args.top : args.top + height, args.left : args.left + width]
    if crop.size == 0:
        print("erreur : decoupe vide", file=sys.stderr)
        return 2

    # ⚠ L'echelle est calculee sur la DECOUPE et non sur le segment entier : une
    # region pale rendue a l'echelle du segment paraitrait vide alors qu'elle porte
    # du contraste. C'est la meme raison qui fait rejeter un seuil absolu ailleurs
    # dans ce depot.
    reduced = reduce_max(crop, args.reduce)
    image = to_image(reduced, args.low, args.high, args.invert)
    # ⚠ La rotation vient APRES le rendu et n'a aucun effet sur les nombres : ce
    # segment est une bande dont les lignes de texte courent dans le sens long, donc
    # sans elle un lecteur doit tourner la tete. Ca n'est pas cosmetique -- un
    # papyrologue juge des formes de lettres, et une lettre couchee ne se juge pas.
    if args.rotate:
        image = np.rot90(image, k=args.rotate // 90)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(args.out)

    covered = float(np.isfinite(reduced).mean() * 100.0)
    print(f"{args.out}  {image.shape[1]} x {image.shape[0]}  couvert {covered:.1f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
