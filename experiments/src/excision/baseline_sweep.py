#!/usr/bin/env python3
"""La ligne de base « locale » de `proximity.py` n'est pas locale. Balayer les remedes.

⚠⚠ **LE DEFAUT, MESURE ET NON SUPPOSE** (`docs/06` §3.2). La reference « locale »
est une fenetre de **±150 colonnes de la parametrisation**. Sur une trace reelle un
tour fait **309 colonnes** : la fenetre couvre donc **96,9 % d'un tour entier**, et le
rayon y varie de **8,62 mm**, soit 59,5 % de l'etendue radiale. Normaliser par ca ne
normalise rien -- c'est une moyenne de tout le rouleau deguisee en voisinage.

Or l'espacement entre feuilles **depend du rayon** : le tassement n'est pas le meme au
coeur et au bord. Une reference qui melange les rayons compare une cellule du coeur a
la moyenne du bord.

**Le remede de principe** : la grandeur mesuree est une **distance 3D**, donc son
voisinage de reference doit etre 3D. Une boule autour de la cellule est locale en
rayon par construction, sans avoir besoin de connaitre l'axe du rouleau -- ce que
`06` §2.3 n'a toujours pas etabli.

⚠ **Ce fichier balaye une FAMILLE, il ne choisit pas un gagnant.** Le depot a deja
paye le piege inverse : un seuil retenu parce qu'il donnait le meilleur chiffre est un
seuil ajuste apres coup. Ce qui se defend, c'est un **plateau** (§3.7 : la correlation
tient de 0,15 a 0,40, donc le choix n'est pas critique) ; ce qui ne se defend pas,
c'est un pic. On rapporte donc toutes les variantes, l'ancienne comprise.

⚠ **Une seule passe couteuse.** Les distances au non-adjacent le plus proche sont
calculees UNE fois par trace ; toutes les lignes de base s'en deduisent pour rien.
Recalculer par variante multiplierait le cout par huit sans rien apprendre.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from excision.proximity import (  # noqa: E402
    ProximityError,
    load_trace,
    local_baseline,
    nearest_non_adjacent,
)

COLUMN_WINDOWS = (150, 100, 50, 20, 10)
"""Fenetres en colonnes. 150 est CELLE D'AUJOURD'HUI : elle reste dans le balayage
pour que l'ancienne mesure soit comparable, pas par indulgence."""

BALL_RADII = (400.0, 200.0, 100.0)
"""Rayons de boule 3D, en voxels. 400 voxels = 3,2 mm, soit une poignee d'epaisseurs
de feuille -- assez pour contenir des voisins, petit devant les 8,62 mm de variation
radiale que la fenetre de 150 colonnes embrasse."""

MIN_NEIGHBOURS = 8
"""Meme plancher que `local_baseline` : sous 8 valeurs, une mediane n'est pas une
mediane. Une cellule qui n'en a pas assez ne recoit PAS de reference -- une absence,
jamais une valeur par defaut."""


def ball_baseline(points: np.ndarray, sample: np.ndarray, distances: np.ndarray,
                  radius: float) -> np.ndarray:
    """Reference locale prise dans une BOULE 3D et non dans la parametrisation.

    ⚠ La boule est centree sur la cellule et prise parmi les cellules ECHANTILLONNEES,
    les seules a porter une distance. Elle contient donc les cellules des feuilles
    voisines, ce qui est voulu : leur distance au non-adjacent EST l'espacement local.
    """
    from scipy.spatial import cKDTree

    positions = points[sample]
    tree = cKDTree(positions)
    baseline = np.full(sample.size, np.nan)
    for index, neighbours in enumerate(tree.query_ball_point(positions, r=radius)):
        values = distances[np.asarray(neighbours, dtype=np.int64)]
        values = values[~np.isnan(values)]
        if values.size >= MIN_NEIGHBOURS:
            baseline[index] = np.median(values)
    return baseline


def summarise(distances: np.ndarray, baseline: np.ndarray) -> dict:
    """Les grandeurs de `proximity.py`, pour une reference donnee."""
    usable = ~np.isnan(distances) & ~np.isnan(baseline) & (baseline > 0)
    if usable.sum() < 100:
        return {"usable": int(usable.sum())}
    ratio = distances[usable] / baseline[usable]
    return {
        "usable": int(usable.sum()),
        "fraction_below_third": float((ratio < 1 / 3).mean()),
        "fraction_below_half": float((ratio < 0.5).mean()),
        "shortfall": float(np.maximum(0.0, 1.0 - ratio).mean()),
        "ratio_p5": float(np.percentile(ratio, 5)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Balayer les definitions de reference locale de proximity.py.",
        epilog="Rapporte TOUTES les variantes, l'ancienne comprise. Ne choisit pas.",
    )
    parser.add_argument("root", type=Path, help="repertoire des traces tifxyz")
    parser.add_argument("out", type=Path, help="sortie JSON Lines")
    parser.add_argument("--sample", type=int, default=20000)
    parser.add_argument("--apart", type=int, default=200)
    parser.add_argument("--search-radius", type=float, default=80.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 = toutes")
    args = parser.parse_args()

    # ⚠ La disposition du corpus windcheck est <trace>/mesh/<nom>.tifxyz/{x,y,z}.tif :
    # le repertoire porte le nom de la trace ET celui du volume sur lequel elle a ete
    # tracee. Chercher `mesh/x.tif` rendait « plan absent » sur les 55 traces, ce qui
    # ressemble a un corpus vide et n'est qu'un chemin devine.
    traces = []
    for entry in sorted(args.root.iterdir()):
        if not entry.is_dir():
            continue
        found = sorted(entry.glob("mesh/*.tifxyz/x.tif")) or sorted(entry.glob("x.tif"))
        if found:
            traces.append((entry.name, found[0].parent))
    if args.limit:
        traces = traces[: args.limit]
    print(f"{len(traces)} traces sous {args.root}")

    handle = args.out.open("w")
    for order, (name, mesh) in enumerate(traces, 1):
        try:
            points, _, cols = load_trace(mesh)
        except ProximityError as error:
            print(f"  [{order}/{len(traces)}] {name} : {error}")
            continue

        generator = np.random.default_rng(args.seed)
        take = min(args.sample, points.shape[0])
        sample = generator.choice(points.shape[0], take, replace=False)
        # ⚠ LA passe couteuse, faite une seule fois. Tout le balayage en decoule.
        distances = nearest_non_adjacent(points, cols, sample, args.apart, args.search_radius)
        if np.isnan(distances).sum() > take - 100:
            print(f"  [{order}/{len(traces)}] {name} : trop peu de mesures")
            continue

        record = {"label": name, "cells": int(points.shape[0]),
                  "measured": int((~np.isnan(distances)).sum()), "variants": {}}
        for window in COLUMN_WINDOWS:
            record["variants"][f"colonnes_{window}"] = summarise(
                distances, local_baseline(cols, sample, distances, window))
        for radius in BALL_RADII:
            record["variants"][f"boule_{int(radius)}"] = summarise(
                distances, ball_baseline(points, sample, distances, radius))
        handle.write(json.dumps(record) + "\n")
        handle.flush()
        ancien = record["variants"]["colonnes_150"].get("fraction_below_third", float("nan"))
        neuf = record["variants"]["boule_200"].get("fraction_below_third", float("nan"))
        print(f"  [{order}/{len(traces)}] {name:16} "
              f"colonnes_150 {ancien * 100:6.3f} %   boule_200 {neuf * 100:6.3f} %", flush=True)
    handle.close()
    print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
