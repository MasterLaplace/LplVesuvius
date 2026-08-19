#!/usr/bin/env python3
"""Regarder un rendu de surface — chercher de l'encre visible à l'œil, sans modèle.

⚠⚠ **Ce fichier existe à cause d'une phrase du règlement de First Letters** : *« Sometimes
ink is visible **directly in the flattened render, with no model at all** — usually bright
areas. If that's already enough legible letters, **that by itself qualifies for the
prize**. »* Donc avant d'entraîner quoi que ce soit, on **regarde**.

Ce que fait ce fichier, et rien de plus :

1. rapporte les statistiques de chaque couche — une pile rendue est majoritairement du
   vide, donc la moyenne brute ne dit rien et il faut l'**emprise** ;
2. produit une image PNG **normalisée dans l'emprise**, à une échelle lisible ;
3. mesure, sur chaque couche, la part de pixels **brillants** au sens de la distribution
   de cette couche — un seuil absolu ne se transporterait pas d'un rendu à l'autre.

⚠ Ce fichier ne détecte PAS d'encre. Il rend une pile regardable et dit **où regarder**.
Décider qu'une forme est une lettre est le travail d'un œil, puis d'un papyrologue.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Statistiques et apercu PNG d'une pile de couches rendues.")
    parser.add_argument("dossier", type=Path)
    parser.add_argument("--png-dir", type=Path, default=None)
    parser.add_argument("--largeur", type=int, default=1600,
                        help="largeur de l'apercu. ⚠ Reduire une image MOYENNE les pixels "
                             "et efface les traits fins : l'apercu sert a reperer, jamais "
                             "a juger une lettre")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    import tifffile
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    fichiers = sorted(args.dossier.glob("*.tif"))
    if not fichiers:
        print(f"aucun .tif dans {args.dossier}", file=sys.stderr)
        return 1

    print(f"{len(fichiers)} couches")
    print(f"{'couche':>8} {'emprise':>9} {'moy':>7} {'ecart':>7} {'p99/p50':>8} "
          f"{'part brillante':>14}")
    lignes = []
    for f in fichiers:
        a = tifffile.imread(f)
        emprise = a[a > 0]
        if emprise.size < 1000:
            print(f"{f.stem:>8} {'vide':>9}")
            continue
        p50, p99 = np.percentile(emprise, [50, 99])
        # ⚠ « Brillant » est defini par la distribution DE CETTE COUCHE : la mediane plus
        # trois ecarts. Un seuil en niveaux de gris ne se transporterait pas d'un rendu a
        # l'autre -- c'est la regle nº 1 du depot.
        seuil = p50 + 3.0 * emprise.std()
        part = float((emprise > seuil).mean())
        lignes.append({"couche": f.stem, "emprise_px": int(emprise.size),
                       "moyenne": float(emprise.mean()), "ecart_type": float(emprise.std()),
                       "contraste_p99_p50": float(p99 / p50) if p50 else float("nan"),
                       "part_brillante": part})
        print(f"{f.stem:>8} {emprise.size / a.size:>8.1%} {emprise.mean():>7.1f} "
              f"{emprise.std():>7.1f} {p99 / max(p50, 1e-9):>8.2f} {part:>13.3%}")

        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            lo, hi = np.percentile(emprise, [1, 99])
            vue = np.clip((a.astype(np.float32) - lo) / max(hi - lo, 1e-6), 0, 1)
            vue[a == 0] = 0.0
            im = Image.fromarray((vue * 255).astype(np.uint8))
            if im.width > args.largeur:
                h = int(im.height * args.largeur / im.width)
                im = im.resize((args.largeur, h), Image.LANCZOS)
            im.save(args.png_dir / f"{f.stem}.png")

    if lignes:
        meilleure = max(lignes, key=lambda l: l["contraste_p99_p50"])
        print(f"\ncouche au plus fort contraste : {meilleure['couche']} "
              f"(p99/p50 = {meilleure['contraste_p99_p50']:.2f})")
        print("⚠ le contraste le plus fort n'est pas une preuve d'encre — c'est ou "
              "commencer a regarder.")
    if args.out:
        args.out.write_text(json.dumps(lignes, indent=2) + "\n")
        print(f"ecrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
