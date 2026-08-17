#!/usr/bin/env python3
"""Les sites suspects persistent-ils le long de z, ou sont-ils du bruit de coupe ?

Une coupe unique a rendu **4 cellules anormales**, groupees vers 17 mm de rayon sur un
secteur d'environ 50 degres. Groupees dans UNE coupe, ca peut encore etre une
coincidence : un rouleau abime a des irregularites partout, et quatre cellules sur
1392 tirees au hasard tombent parfois cote a cote.

Ce que la troisieme dimension tranche : **un degat physique occupe une hauteur**.
Une soudure entre deux feuilles ne s'arrete pas net a la coupe d'a cote ; du bruit de
detection, si.

⚠ **L'hypothese nulle est calculee, pas supposee.** On compare le regroupement observe
a ce que donnerait un placement aleatoire des memes nombres de cellules dans les memes
grilles -- sinon « elles sont proches » est une impression, pas une mesure. C'est le
meme reflexe que partout ici : un controle qui ne peut pas echouer ne prouve rien.

Compose `radial.deplier` et `fusions.densite`, qui ont chacun leur propre temoin.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from excision.fusions import doubling_density, gap_map  # noqa: E402
from excision.radial import (  # noqa: E402
    VOXEL_UM,
    load_centre,
    open_volume,
    unwrap_polar,
)


def anomalous_cells(polar: np.ndarray, args) -> tuple:
    """Cellules anormales d'une coupe depliee, et le taux de fond qui les qualifie."""
    ratios, radii, columns = gap_map(polar, args.prominence, args.min_gap,
                                     args.smooth, args.band)
    rate, total, width, rcell, acell = doubling_density(
        ratios, radii, columns, args.doubling, args.radial_cell,
        args.angular_cell, args.min_radius)
    valid = np.isfinite(rate)
    background = float(np.nanmedian(rate))
    high = float(np.nanpercentile(rate[valid], 90))
    threshold = background + args.excess * (high - background)
    index = np.flatnonzero(valid & (rate > threshold))
    cells = [{"radius_mm": float((int(k) // width) * rcell * VOXEL_UM / 1000.0),
              "column": int((int(k) % width) * acell),
              "rate": float(rate[k])} for k in index]
    return cells, background, int(valid.sum())


def colocation(per_slice: list[list[dict]], radial_mm: float, angular: int) -> dict:
    """Combien de paires de cellules, prises dans DEUX coupes differentes, coincident.

    ⚠ Les paires sont comptees entre coupes distinctes uniquement : deux cellules
    voisines dans la MEME coupe sont deja ce que la coupe unique montrait, et les
    compter ici ferait passer le resultat d'hier pour une confirmation.
    """
    pairs = 0
    close = 0
    for i in range(len(per_slice)):
        for j in range(i + 1, len(per_slice)):
            for a in per_slice[i]:
                for b in per_slice[j]:
                    pairs += 1
                    if (abs(a["radius_mm"] - b["radius_mm"]) <= radial_mm
                            and abs(a["column"] - b["column"]) <= angular):
                        close += 1
    return {"pairs": pairs, "colocated": close,
            "fraction": close / pairs if pairs else float("nan")}


def null_model(per_slice: list[list[dict]], radial_span: tuple, angular_span: int,
               radial_mm: float, angular: int, trials: int, seed: int) -> dict:
    """Ce que le meme regroupement donnerait si les cellules etaient placees au hasard.

    Le hasard respecte le NOMBRE de cellules par coupe et l'etendue ou elles peuvent
    tomber ; il ne respecte pas leurs positions, qui sont justement la question.
    """
    generator = np.random.default_rng(seed)
    fractions = []
    for _ in range(trials):
        fake = []
        for cells in per_slice:
            fake.append([{"radius_mm": float(generator.uniform(*radial_span)),
                          "column": int(generator.integers(0, angular_span))}
                         for _ in cells])
        fractions.append(colocation(fake, radial_mm, angular)["fraction"])
    fractions = np.asarray([f for f in fractions if np.isfinite(f)])
    if fractions.size == 0:
        return {"trials": 0}
    return {"trials": int(fractions.size),
            "mean": float(fractions.mean()),
            "p95": float(np.percentile(fractions, 95))}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Les sites suspects tiennent-ils le long de z ?",
        epilog="Un degat physique occupe une hauteur ; du bruit de detection, non.",
    )
    parser.add_argument("name")
    parser.add_argument("volume")
    parser.add_argument("out", help="sortie JSON")
    parser.add_argument("--level", default="0")
    parser.add_argument("--slices", type=int, default=5)
    parser.add_argument("--z-min", type=int, default=-1)
    parser.add_argument("--z-max", type=int, default=-1)
    parser.add_argument("--reach", type=float, default=3000.0)
    parser.add_argument("--prominence", type=float, default=8.0)
    parser.add_argument("--min-gap", type=int, default=10)
    parser.add_argument("--smooth", type=int, default=5)
    parser.add_argument("--band", type=float, default=400.0)
    parser.add_argument("--doubling", type=float, default=1.7)
    parser.add_argument("--min-radius", type=float, default=600.0,
                        help="coupe validee : sous 600 vx le depliage est degenere")
    parser.add_argument("--radial-cell", type=float, default=60.0)
    parser.add_argument("--angular-cell", type=int, default=500)
    parser.add_argument("--excess", type=float, default=3.0)
    parser.add_argument("--match-radial-mm", type=float, default=1.0,
                        help="deux cellules coincident si leurs rayons different de moins")
    parser.add_argument("--match-angular", type=int, default=1000,
                        help="…et leurs colonnes de moins que ceci")
    parser.add_argument("--null-trials", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    centre = load_centre(args.name)
    array = open_volume(args.volume, args.level)
    lo = args.z_min if args.z_min >= 0 else int(centre["z_min"])
    hi = args.z_max if args.z_max >= 0 else int(centre["z_max"])
    zs = [int(round(v)) for v in np.linspace(lo, hi, args.slices)]
    print(f"volume {array.shape} | {len(zs)} coupes de {lo} a {hi}")

    per_slice, records = [], []
    for z in zs:
        polar = unwrap_polar(array[z], centre["cx"], centre["cy"], args.reach)
        cells, background, valid = anomalous_cells(polar, args)
        per_slice.append(cells)
        records.append({"slice": z, "background_rate": background,
                        "valid_cells": valid, "anomalous": cells})
        radii = [c["radius_mm"] for c in cells]
        print(f"  z={z:6d}  fond {background * 100:4.1f} %  "
              f"anormales {len(cells):3d}  "
              f"rayons {min(radii):.1f}-{max(radii):.1f} mm" if cells
              else f"  z={z:6d}  fond {background * 100:4.1f} %  anormales 0", flush=True)
        Path(args.out).write_text(json.dumps({"slices": records}, indent=2) + "\n")

    observed = colocation(per_slice, args.match_radial_mm, args.match_angular)
    all_radii = [c["radius_mm"] for cells in per_slice for c in cells]
    if not all_radii:
        print("\naucune cellule anormale : rien a tester")
        return 0
    null = null_model(per_slice, (min(all_radii), max(all_radii)),
                      int(2 * np.pi * args.reach), args.match_radial_mm,
                      args.match_angular, args.null_trials, args.seed)

    print()
    print(f"paires INTER-COUPES : {observed['pairs']}")
    print(f"  coincidentes (< {args.match_radial_mm} mm et < {args.match_angular} colonnes) : "
          f"{observed['colocated']}  soit {observed['fraction'] * 100:.1f} %")
    if null.get("trials"):
        print(f"  au HASARD (memes nombres, memes etendues, {null['trials']} tirages) : "
              f"{null['mean'] * 100:.1f} %  (p95 = {null['p95'] * 100:.1f} %)")
        verdict = ("les sites TIENNENT le long de z"
                   if observed["fraction"] > null["p95"]
                   else "indistinguable du hasard -- bruit de coupe")
        print()
        print(f"VERDICT : {verdict}")
    Path(args.out).write_text(json.dumps(
        {"slices": records, "observed": observed, "null": null}, indent=2) + "\n")
    print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
