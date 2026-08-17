#!/usr/bin/env python3
"""Jusqu'a quelle resolution les spires restent-elles separables ?

**L'enjeu est un facteur 60 sur la donnee.** Le rouleau en pleine resolution fait
~2,1 Tio ; son niveau 2 de pyramide en fait **33 Gio**. Si les feuilles y restent
separables, tout le travail geometrique change d'echelle de faisabilite.

⚠⚠ **Ce test doit se faire SANS seuil de matiere, et c'est la lecon.** Une premiere
version reutilisait le seuil `intensite > 12` de `radial.py compter`, et rendait
« 53 feuilles au niveau 1 contre 158 au niveau 0 » -- une chute catastrophique qui
n'existe pas. Reduire un volume MOYENNE les voxels, donc remonte le fond et deplace
la distribution d'intensite : un seuil absolu cale sur le niveau 0 ne veut plus rien
dire ailleurs. Ce qu'il mesurait etait son propre decalage, pas la separabilite.

Ce fichier compare donc, a chaque niveau :

- la **meme portee physique** (en millimetres, pas en voxels) ;
- les **memes angles** ;
- un lissage a l'echelle d'**une feuille** (40 um), converti en voxels du niveau ;
- un ecart minimal entre murs d'une **demi-feuille physique**.

La seule chose qui change est alors la resolution, ce qui est la question posee.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

FULL_DEPTH = 20820
BASE_VOXEL_UM = 7.91
SHEET_UM = 40.0
"""Epaisseur d'une feuille : fixe le lissage, a toutes les resolutions."""


def walls_at_level(group, level: str, centre: tuple, z_full: int,
                   reach_um: float, step_deg: int, prominence: float) -> dict:
    array = group[level]
    scale = FULL_DEPTH / array.shape[0]
    voxel = BASE_VOXEL_UM * scale
    plane = np.asarray(array[int(z_full / scale)]).astype(np.float32)
    height, width = plane.shape
    cx, cy = centre[0] / scale, centre[1] / scale
    reach = int(reach_um / voxel)

    smooth = max(1, int(round(SHEET_UM / voxel)))
    min_gap = max(1, int(round(SHEET_UM * 1.8 / voxel)))

    counts, spacings = [], []
    for degrees in range(0, 360, step_deg):
        theta = np.deg2rad(degrees)
        radii = np.arange(0.0, reach, 1.0)
        xs = np.rint(cx + radii * np.cos(theta)).astype(np.int64)
        ys = np.rint(cy + radii * np.sin(theta)).astype(np.int64)
        inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
        profile = plane[ys[inside], xs[inside]]
        if profile.size < 50:
            continue
        from scipy.signal import find_peaks

        smoothed = np.convolve(profile, np.ones(smooth) / smooth, mode="same")
        peaks, _ = find_peaks(smoothed, prominence=prominence, distance=min_gap)
        counts.append(len(peaks))
        if len(peaks) > 2:
            spacings.append(float(np.diff(peaks).mean() * voxel))
    if not counts:
        return {}
    return {"level": level, "voxel_um": voxel, "reduction": scale,
            "walls_median": int(np.median(counts)),
            "walls_min": int(min(counts)), "walls_max": int(max(counts)),
            "spacing_um": float(np.median(spacings)) if spacings else float("nan")}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Jusqu'a quelle resolution les spires restent-elles separables ?",
        epilog="⚠ Sans seuil de matiere : un seuil absolu ne se transporte pas d'un niveau a l'autre.",
    )
    parser.add_argument("volume")
    parser.add_argument("--centre", default="PHerc0172")
    parser.add_argument("--slice", type=int, default=6967)
    parser.add_argument("--reach-um", type=float, default=22700.0)
    parser.add_argument("--levels", default="0,1,2,3,4")
    parser.add_argument("--step-deg", type=int, default=10)
    parser.add_argument("--prominence", type=float, default=8.0)
    parser.add_argument("--json")
    args = parser.parse_args()

    import fsspec
    import zarr

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from excision.radial import load_centre

    centre_data = load_centre(args.centre)
    centre = (centre_data["cx"], centre_data["cy"])
    group = zarr.open(fsspec.get_mapper(args.volume, anon=True), mode="r")

    rows = []
    base = None
    print(f"{'niveau':>7}{'voxel um':>10}{'murs':>7}{'espacement':>12}{'% niveau 0':>12}"
          f"{'volume':>10}")
    print("-" * 58)
    for level in args.levels.split(","):
        row = walls_at_level(group, level.strip(), centre, args.slice,
                             args.reach_um, args.step_deg, args.prominence)
        if not row:
            continue
        if base is None:
            base = row["walls_median"]
        row["fraction_of_full"] = row["walls_median"] / base
        # 2,1 Tio au niveau 0, divise par le cube de la reduction
        row["volume_gib"] = 2100.0 / (row["reduction"] ** 3)
        rows.append(row)
        print(f"{row['level']:>7}{row['voxel_um']:>10.1f}{row['walls_median']:>7}"
              f"{row['spacing_um']:>11.0f}u{row['fraction_of_full'] * 100:>11.0f}%"
              f"{row['volume_gib']:>9.0f}G")

    print()
    print("Lecture : la question n'est pas « le compte baisse-t-il » — il baisse")
    print("toujours un peu — mais OU EST LA FALAISE. Au-dessus, le niveau est")
    print("utilisable pour du travail geometrique ; en dessous, les spires fusionnent.")
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=2) + "\n")
        print(f"\necrit : {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
