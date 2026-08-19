#!/usr/bin/env python3
"""Deux traces d'un même rouleau, côte à côte, à la MÊME échelle physique.

⚠⚠ **La comparaison ne veut rien dire si les deux vignettes ne sont pas à la même échelle.**
Les deux rendus ne font pas la même taille — 29 mm de côté pour l'un, 45 mm pour l'autre —
et les réduire chacun à la largeur d'une colonne ferait passer une surface deux fois plus
grande pour une surface identique. Le facteur est donc calculé en **millimètres par pixel**,
et une règle graduée est dessinée sous chaque vignette.

⚠ La normalisation d'intensité est faite **dans l'emprise** et **indépendamment** pour
chaque vignette : une pile rendue est majoritairement du vide, donc une normalisation
globale écraserait le papyrus contre le fond. C'est ce que fait déjà `regarder_rendu.py`,
et pour la même raison.

⚠ Réduire une image **moyenne** les pixels et efface les traits fins. Ces vignettes servent
à voir la **forme** de la surface — bande continue ou plaques écartelées — jamais à juger
une lettre. Le détail à pleine résolution est une autre figure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def vignette(dossier: Path, couche: int, largeur: int):
    """Une couche, normalisée dans son emprise, en niveaux de gris."""
    import tifffile

    fichiers = sorted(dossier.glob("*.tif"))
    if not fichiers:
        raise RuntimeError(f"aucune couche dans {dossier}")
    choisi = fichiers[min(couche, len(fichiers) - 1)]
    plan = tifffile.imread(choisi).astype(np.float32)
    emprise = plan > 0
    if not emprise.any():
        raise RuntimeError(f"{choisi} est vide")
    bas, haut = np.percentile(plan[emprise], (1.0, 99.0))
    norme = np.clip((plan - bas) / max(haut - bas, 1e-9), 0.0, 1.0)
    norme[~emprise] = 0.0
    from PIL import Image
    image = Image.fromarray((norme * 255).astype(np.uint8), mode="L").convert("RGB")
    facteur = largeur / image.width
    return image.resize((largeur, max(1, int(round(image.height * facteur)))),
                        Image.LANCZOS), plan.shape


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deux traces cote a cote, a la meme echelle physique.")
    parser.add_argument("sortie", type=Path)
    parser.add_argument("--trace", action="append", nargs=4, required=True,
                        metavar=("DOSSIER", "TITRE", "SOUS_TITRE", "VOXEL_UM"),
                        help="a repeter. ⚠ VOXEL_UM sert a l'echelle COMMUNE")
    parser.add_argument("--couche", type=int, default=30,
                        help="indice dans la pile. ⚠ 30 est la surface tracee d'une pile "
                             "de 61 -- verifie, pas suppose (docs/25)")
    parser.add_argument("--mm-par-colonne", type=float, default=48.0,
                        help="largeur physique que represente une colonne")
    parser.add_argument("--colonne-px", type=int, default=560)
    parser.add_argument("--legende", default="")
    args = parser.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    ecart, marge, entete, pied = 28, 26, 74, 82
    vignettes = []
    for dossier, titre, sous, voxel in args.trace:
        um = float(voxel)
        # ⚠ L'echelle est physique et COMMUNE : chaque vignette occupe la fraction de la
        # colonne que sa taille reelle merite. Une surface deux fois plus grande doit
        # apparaitre deux fois plus grande.
        import tifffile
        premier = sorted(Path(dossier).glob("*.tif"))[0]
        with tifffile.TiffFile(premier) as h:
            lignes, colonnes = h.pages[0].shape
        mm = colonnes * um / 1000.0
        largeur = max(40, int(round(args.colonne_px * mm / args.mm_par_colonne)))
        img, forme = vignette(Path(dossier), args.couche, largeur)
        vignettes.append({"img": img, "titre": titre, "sous": sous,
                          "mm": mm, "mm_haut": forme[0] * um / 1000.0, "um": um})

    hauteur_v = max(v["img"].height for v in vignettes)
    largeur_t = marge * 2 + args.colonne_px * len(vignettes) + ecart * (len(vignettes) - 1)
    hauteur_t = entete + hauteur_v + pied
    toile = Image.new("RGB", (largeur_t, hauteur_t), (255, 255, 255))
    art = ImageDraw.Draw(toile)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except OSError:
        f_t = f_n = ImageFont.load_default()

    for i, v in enumerate(vignettes):
        x0 = marge + i * (args.colonne_px + ecart)
        art.text((x0, 16), v["titre"], fill=(20, 20, 20), font=f_t)
        art.text((x0, 38), v["sous"], fill=(150, 90, 20), font=f_n)
        y0 = entete
        toile.paste(v["img"], (x0, y0))
        art.rectangle([x0 - 1, y0 - 1, x0 + v["img"].width, y0 + v["img"].height],
                      outline=(190, 190, 190))
        # Regle graduee : 10 mm, a l'echelle COMMUNE.
        px10 = args.colonne_px * 10.0 / args.mm_par_colonne
        yr = y0 + hauteur_v + 20
        art.line([x0, yr, x0 + px10, yr], fill=(40, 40, 40), width=2)
        art.line([x0, yr - 4, x0, yr + 4], fill=(40, 40, 40), width=2)
        art.line([x0 + px10, yr - 4, x0 + px10, yr + 4], fill=(40, 40, 40), width=2)
        art.text((x0 + px10 + 8, yr - 7), "10 mm", fill=(70, 70, 70), font=f_n)
        art.text((x0, yr + 14),
                 f"{v['mm']:.1f} × {v['mm_haut']:.1f} mm  ·  voxel {v['um']:g} µm",
                 fill=(110, 110, 110), font=f_n)

    if args.legende:
        art.text((marge, hauteur_t - 22), args.legende, fill=(70, 70, 70), font=f_n)

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(args.sortie)
    print(f"ecrit : {args.sortie}  ({largeur_t}x{hauteur_t})")
    for v in vignettes:
        print(f"  {v['titre']:32} {v['mm']:6.1f} x {v['mm_haut']:5.1f} mm  "
              f"-> {v['img'].width} px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
