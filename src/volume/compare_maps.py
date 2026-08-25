#!/usr/bin/env python3
"""Deux cartes d'encre du MEME segment disent-elles la meme chose ?

⚠⚠ Ne du test de `docs/12` : l'inference de Scroll 4 a ete relancee sur une fenetre de
couches recentree (`--start-layer 0` au lieu de 15), parce que le profil de profondeur
montre que la surface n'est pas dans la fenetre lue. La question est binaire -- **est-ce
que regarder ailleurs change ce qui sort ?**

⚠ **Le controle qui rend la reponse lisible** : les deux fenetres PARTAGENT 11 couches
sur 26 (15 a 25). Une ressemblance partielle est donc attendue et ne prouve rien ; ce
qui trancherait, c'est une ressemblance **aussi forte que celle d'une carte avec
elle-meme**, ou au contraire une carte franchement differente.

Trois grandeurs, et elles echouent differemment :

1. la **correlation de rang** entre les deux, sur les pixels couverts des deux cotes --
   une carte deplacee mais de meme forme la garderait haute ;
2. l'**accord de seuil** (part des pixels classes pareil a logit 0) -- c'est ce que la
   suite consomme reellement ;
3. la **fraction d'encre par bande**, parce que c'est ce que le juge voit.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def load(path: Path) -> np.ndarray:
    return np.asarray(np.load(path, mmap_mode="r"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comparer deux cartes d'encre du meme segment.",
        epilog="Les fenetres de couches se recouvrant, une ressemblance partielle est attendue.",
    )
    parser.add_argument("a", type=Path)
    parser.add_argument("b", type=Path)
    parser.add_argument("--band", type=int, default=1024)
    parser.add_argument("--sample", type=int, default=2_000_000,
                        help="pixels tires pour la correlation de rang (defaut: 2 M)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    first, second = load(args.a), load(args.b)
    if first.shape != second.shape:
        print(f"erreur : formes differentes {first.shape} vs {second.shape}", file=sys.stderr)
        return 2

    # ⚠ Seuls les pixels couverts DES DEUX COTES entrent : un NaN d'un cote rendrait
    # la comparaison dependante de la couverture, pas du contenu.
    both = np.isfinite(first) & np.isfinite(second)
    generator = np.random.default_rng(args.seed)
    flat = np.flatnonzero(both.ravel())
    take = min(args.sample, flat.size)
    pick = generator.choice(flat, take, replace=False)
    x = first.ravel()[pick]
    y = second.ravel()[pick]

    from scipy.stats import spearmanr

    rho = float(spearmanr(x, y).statistic)
    agree = float(((x > 0) == (y > 0)).mean())
    ink_a = float((first[both] > 0).mean())
    ink_b = float((second[both] > 0).mean())

    rows = first.shape[0]
    bands = []
    for top in range(0, rows - args.band + 1, args.band):
        mask = both[top:top + args.band]
        if mask.sum() < 1000:
            continue
        bands.append((top,
                      float((first[top:top + args.band][mask] > 0).mean()),
                      float((second[top:top + args.band][mask] > 0).mean())))

    print(f"{args.a.name}  vs  {args.b.name}")
    print(f"  pixels couverts des deux cotes : {int(both.sum())}")
    print(f"  correlation de rang            : {rho:+.4f}   (sur {take} pixels)")
    print(f"  accord de classement a logit 0 : {agree * 100:.2f} %")
    print(f"  encre predite                  : {ink_a * 100:.3f} %  vs  {ink_b * 100:.3f} %")
    print(f"\n  {'bande':>7} {'A':>9} {'B':>9} {'ecart':>8}")
    for top, a, b in bands:
        print(f"  {top:>7} {a * 100:>8.2f}% {b * 100:>8.2f}% {(b - a) * 100:>+7.2f}")

    report = {"a": str(args.a), "b": str(args.b), "rho": rho, "accord": agree,
              "encre_a": ink_a, "encre_b": ink_b,
              "bandes": [{"top": t, "a": a, "b": b} for t, a, b in bands]}
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
