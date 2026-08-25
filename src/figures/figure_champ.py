#!/usr/bin/env python3
"""Le champ de correction en image — la preuve visuelle que le concours réclame.

⚠ La page `Prizes` demande explicitement, pour le déroulement virtuel : *« show visually
that papyrus fibers are visible on your output surface, and **it doesn't jump across
sheets** »*. `docs/20` mesure ce saut ; ce fichier le montre.

Deux panneaux, et le second est ce qui rend le premier lisible :

| panneau | ce qu'on voit |
|---|---|
| **mesuré** | l'écart pic↔trace de chaque fenêtre, en couleur divergente |
| **mélangé** | les **mêmes** valeurs, réattribuées au hasard aux mêmes fenêtres |

Si le premier montre des plages et le second de la neige, l'erreur est **structurée** —
et c'est exactement ce qu'un chiffre de corrélation dit sans le montrer.

⚠ **Tracé à la main avec PIL, sans matplotlib** : il est absent de cet environnement, et
l'ajouter pour dessiner deux damiers ferait dépendre une figure d'une pile graphique
entière. Même choix que `figure_profondeur.py`.

⚠ **L'échelle de couleur est PARTAGÉE** par les deux panneaux et bornée par le pas
inter-feuilles : sans ça le mélange se re-normaliserait sur sa propre étendue et
paraîtrait aussi contrasté que le vrai champ.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from champ_correction import BUCKET, grille_ecarts  # noqa: E402

CELL, MARGE, ENTRE = 22, 46, 40


def couleur(v: float, borne: float) -> tuple[int, int, int]:
    """Divergente : bleu = trace trop en surface, rouge = trop en profondeur.

    ⚠ Le zéro est **blanc cassé et non gris** : un gris se confondrait avec les fenêtres
    sans matière, qui sont un fait tout à fait différent — « la trace est juste ici » et
    « il n'y a rien ici » ne doivent pas se ressembler.
    """
    t = max(-1.0, min(1.0, v / borne))
    if t >= 0:
        return (245, int(245 - 165 * t), int(245 - 195 * t))
    return (int(245 + 190 * t), int(245 + 120 * t), 245)


def panneau(image, grille: np.ndarray, ox: int, oy: int, borne: float, titre: str,
            police):
    from PIL import ImageDraw

    art = ImageDraw.Draw(image)
    h, w = grille.shape
    for i in range(h):
        for j in range(w):
            v = grille[i, j]
            x, y = ox + j * CELL, oy + i * CELL
            if not np.isfinite(v):
                # ⚠ Hachure claire, pas une couleur de l'echelle : une fenetre sans
                # matiere n'a pas d'ecart, et lui en peindre un serait inventer.
                art.rectangle([x, y, x + CELL - 1, y + CELL - 1], fill=(232, 232, 230))
                art.line([x, y + CELL - 1, x + CELL - 1, y], fill=(206, 206, 204))
            else:
                art.rectangle([x, y, x + CELL - 1, y + CELL - 1], fill=couleur(v, borne))
    art.rectangle([ox - 1, oy - 1, ox + w * CELL, oy + h * CELL], outline=(140, 140, 140))
    art.text((ox, oy - 20), titre, fill=(30, 30, 30), font=police)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rendre le champ de correction d'un segment, avec son temoin.")
    parser.add_argument("zarr")
    parser.add_argument("sortie", type=Path)
    parser.add_argument("--level", type=int, default=0)
    parser.add_argument("--cote", type=int, default=6)
    parser.add_argument("--blocs", type=int, default=4)
    parser.add_argument("--voxel-um", type=float, required=True)
    parser.add_argument("--pas-um", type=float, required=True,
                        help="pas inter-feuilles DE CE ROULEAU — il borne l'echelle de "
                             "couleur, donc « saturé » veut dire « une feuille d'ecart »")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--fils", type=int, default=16)
    args = parser.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    url = args.zarr if args.zarr.startswith("http") else f"{BUCKET}/{args.zarr}"
    segment = (args.zarr.split("/segments/")[1].split("/")[0]
               if "/segments/" in args.zarr else args.zarr)
    grille, depth, sondees, coins = grille_ecarts(url, args.level, args.cote, args.blocs,
                                                  args.timeout, args.fils)

    # ⚠⚠ On dessine LES BLOCS, pas leur boite englobante. Les blocs sont posés loin les
    # uns des autres sur un canevas immense : une premiere version a rendu une image de
    # 6522 x 3092 pixels dont 142 fenetres sur 55596 portaient une valeur — c'est-à-dire
    # 99,7 % de hachure. La cohérence se lit DANS un bloc, donc c'est le bloc qui est
    # l'unité d'affichage, séparé de ses voisins par un espace.
    tuiles = []
    for (oy, ox) in coins:
        bloc = grille[oy:oy + args.cote, ox:ox + args.cote]
        if np.isfinite(bloc).sum() >= 4:
            tuiles.append(bloc * args.voxel_um)
    if not tuiles:
        print("aucun bloc avec assez de matiere", file=sys.stderr)
        return 1
    # Les tuiles sont juxtaposees avec une colonne de separation NON FINIE : elle se
    # dessine en hachure, donc l'oeil ne peut pas la lire comme une valeur.
    sep = np.full((args.cote, 1), np.nan)
    vue = np.concatenate([t for tuile in tuiles for t in (tuile, sep)][:-1], axis=1)

    rng = np.random.default_rng(0)
    valeurs = vue[np.isfinite(vue)]
    melange = vue.copy()
    for (y, x), v in zip(np.argwhere(np.isfinite(vue)), rng.permutation(valeurs)):
        melange[y, x] = v

    h, w = vue.shape
    largeur = 2 * MARGE + 2 * w * CELL + ENTRE
    hauteur = 2 * MARGE + h * CELL + 62
    image = Image.new("RGB", (largeur, hauteur), (255, 255, 255))
    try:
        police = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except OSError:
        police = ImageFont.load_default()

    panneau(image, vue, MARGE, MARGE + 22, args.pas_um, "mesure", police)
    panneau(image, melange, MARGE + w * CELL + ENTRE, MARGE + 22, args.pas_um,
            "les memes valeurs, melangees", police)

    art = ImageDraw.Draw(image)
    art.text((MARGE, 12), f"{segment} — ecart pic d'intensite / surface tracee",
             fill=(20, 20, 20), font=police)
    art.text((MARGE, MARGE + 22 + h * CELL + 12),
             f"bleu : trace trop en surface   ·   rouge : trop en profondeur   ·   "
             f"sature a +/- {args.pas_um:.0f} um = UNE feuille   ·   "
             f"hachure : pas de matiere   ·   {len(tuiles)} blocs de {args.cote}x{args.cote} "
             f"fenetres, pris a des endroits differents du segment",
             fill=(80, 80, 80), font=police)
    art.text((MARGE, MARGE + 22 + h * CELL + 30),
             "⚠ le panneau de droite est le temoin : memes valeurs, memes fenetres, "
             "attribution au hasard.",
             fill=(80, 80, 80), font=police)

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.sortie)
    print(f"ecrit : {args.sortie}  ({largeur}x{hauteur}, {int(np.isfinite(vue).sum())} "
          f"fenetres sur {vue.size})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
