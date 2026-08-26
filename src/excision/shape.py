#!/usr/bin/env python3
"""Deux questions de FORME sur une coupe : le dommage, et l'ecrasement.

`degradation` — **la theorie du dommage de l'auteur**, rendue falsifiable.

    « La fumee est passee par le trou central, donc les toutes premieres couches du
    coeur sont abimees ; mais le rouleau est plus dense au centre donc il a mieux
    resiste ; les couches externes ont pris le plus, et sur de plus grandes longueurs
    puisque la circonference croit avec le rayon. »

    Prediction : le dommage en fonction du rayon n'est **pas monotone** mais en **U**
    — mauvais au coeur immediat, bon dans la couronne intermediaire, mauvais dehors.

    ⚠ L'indicateur n'est pas « l'intensite », qui melange la matiere et le vide. C'est
    le **contraste feuille/interstice** : une feuille intacte se detache de son voisin
    par un mur net, une feuille degradee se fond dedans. Mesure par la profondeur
    mediane des creux entre pics, normalisee par la hauteur des pics -- donc sans
    dimension, comparable d'un rayon a l'autre, ce qu'une difference brute ne serait
    pas.

`ellipticite` — pourquoi le rayon lu varie de 21,3 a 25,1 mm le long de z alors qu'un
rouleau est UNE feuille enroulee N fois et que toute coupe traverse les memes N
spires. Deux lectures : la section est **ecrasee** (elliptique, donc un rayon median
sur 36 rayons lit plus petit), ou il y a **perte de matiere**. Le rapport des axes les
separe : une ellipse garde son perimetre approximatif, une perte le reduit.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

BASE_VOXEL_UM = 7.91
FULL_DEPTH = 20820
SHEET_UM = 40.0


def load_plane(volume: str, level: str, z_full: int):
    import fsspec
    import zarr

    group = zarr.open(fsspec.get_mapper(volume, anon=True), mode="r")
    array = group[level]
    scale = FULL_DEPTH / array.shape[0]
    return np.asarray(array[int(z_full / scale)]).astype(np.float32), scale


def radial_contrast(plane, centre, voxel, reach_um, step_deg, bands, prominence):
    """Contraste feuille/interstice par tranche de rayon.

    ⚠ Le contraste est rapporte a la hauteur du pic, donc **sans dimension**. Une
    difference brute d'intensite melangerait la degradation avec la simple densite de
    matiere, qui varie elle aussi avec le rayon -- et on mesurerait alors surtout que
    le coeur est plus tasse.
    """
    from scipy.signal import find_peaks

    height, width = plane.shape
    cx, cy = centre
    reach = int(reach_um / voxel)
    smooth = max(1, int(round(SHEET_UM / voxel)))
    min_gap = max(1, int(round(SHEET_UM * 1.8 / voxel)))

    edges = np.linspace(0, reach, bands + 1)
    collected = [[] for _ in range(bands)]
    for degrees in range(0, 360, step_deg):
        theta = np.deg2rad(degrees)
        radii = np.arange(0.0, reach, 1.0)
        xs = np.rint(cx + radii * np.cos(theta)).astype(np.int64)
        ys = np.rint(cy + radii * np.sin(theta)).astype(np.int64)
        inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
        profile = plane[ys[inside], xs[inside]]
        if profile.size < 50:
            continue
        smoothed = np.convolve(profile, np.ones(smooth) / smooth, mode="same")
        peaks, _ = find_peaks(smoothed, prominence=prominence, distance=min_gap)
        for a, b in zip(peaks, peaks[1:]):
            trough = float(smoothed[a:b].min())
            crest = float((smoothed[a] + smoothed[b]) / 2.0)
            if crest <= 0:
                continue
            middle = (a + b) / 2.0
            band = int(np.searchsorted(edges, middle, side="right") - 1)
            if 0 <= band < bands:
                collected[band].append((crest - trough) / crest)

    rows = []
    for index, values in enumerate(collected):
        if len(values) < 30:
            continue
        values = np.asarray(values)
        rows.append({
            "band": index,
            "radius_mm_low": float(edges[index] * voxel / 1000.0),
            "radius_mm_high": float(edges[index + 1] * voxel / 1000.0),
            "contrast": float(np.median(values)),
            "samples": int(values.size),
        })
    return rows


def ellipticity(plane, centre, voxel, reach_um, step_deg, threshold):
    """Rapport des axes de la section, et son perimetre approche.

    ⚠⚠ **La portee doit depasser largement le rayon attendu, et c'est un piege paye.**
    Une premiere mesure rendait un axe long de 22,7 mm sur les HUIT coupes -- soit
    exactement la portee demandee. Elle saturait contre son propre plafond, donc le
    rapport d'axes n'etait qu'un rapport entre le vrai petit axe et ma constante, et
    le verdict qui en decoulait (« perte de matiere ») ne mesurait rien. Une valeur
    identique sur toutes les coupes est le symptome a reconnaitre.
    """
    height, width = plane.shape
    cx, cy = centre
    reach = int(reach_um / voxel)
    outer = []
    for degrees in range(0, 360, step_deg):
        theta = np.deg2rad(degrees)
        radii = np.arange(0.0, reach, 1.0)
        xs = np.rint(cx + radii * np.cos(theta)).astype(np.int64)
        ys = np.rint(cy + radii * np.sin(theta)).astype(np.int64)
        inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
        profile = plane[ys[inside], xs[inside]]
        body = np.flatnonzero(profile > threshold)
        outer.append((degrees, float(body.max()) if body.size else 0.0))
    angles = np.array([a for a, _ in outer])
    radii = np.array([r for _, r in outer]) * voxel / 1000.0
    good = radii > 0
    if good.sum() < 8:
        return {}
    # Refuser plutot que de rendre un chiffre sature : au-dela de 95 % de la portee,
    # on ne mesure plus le rouleau mais la limite qu'on s'est donnee.
    ceiling = reach * voxel / 1000.0
    if float(radii[good].max()) > 0.95 * ceiling:
        return {"saturated": True, "ceiling_mm": ceiling,
                "radius_median_mm": float(np.median(radii[good]))}
    a_max = float(np.percentile(radii[good], 90))
    a_min = float(np.percentile(radii[good], 10))
    # ⚠⚠ VRAIE longueur d'arc, avec le terme dr/dtheta -- et c'est un piege paye.
    # Une premiere version calculait somme(r * dtheta), qui vaut exactement
    # 2*pi*rayon_moyen : elle ne portait AUCUNE information independante du rayon,
    # donc comparer sa dispersion a celle du rayon revenait a comparer une grandeur
    # a elle-meme. Le test etait circulaire et son verdict sans valeur.
    # En polaire, ds = sqrt(r^2 + (dr/dtheta)^2) dtheta : c'est le terme derive qui
    # distingue une section deformee d'un cercle plus petit.
    step = np.deg2rad(step_deg)
    r_good = radii[good]
    dr = np.gradient(np.concatenate([r_good, r_good[:1]]))[:-1] / step
    perimeter = float(np.sum(np.sqrt(r_good ** 2 + dr ** 2) * step))
    return {"radius_median_mm": float(np.median(radii[good])),
            "axis_long_mm": a_max, "axis_short_mm": a_min,
            "axis_ratio": a_max / max(a_min, 1e-9),
            "perimeter_mm": perimeter,
            "angles_used": int(good.sum())}


def main() -> int:
    parser = argparse.ArgumentParser(description="Forme d'une coupe : dommage radial et ecrasement.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("degradation", "ellipticite"):
        p = sub.add_parser(name)
        p.add_argument("volume")
        p.add_argument("--centre", default="PHerc0172")
        p.add_argument("--level", default="0")
        p.add_argument("--slices", default="6967")
        p.add_argument("--reach-um", type=float, default=22700.0)
        p.add_argument("--step-deg", type=int, default=10)
        p.add_argument("--prominence", type=float, default=8.0)
        p.add_argument("--bands", type=int, default=10)
        p.add_argument("--threshold", type=float, default=12.0)
        p.add_argument("--json")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from radial import load_centre

    data = load_centre(args.centre)
    zs = [int(v) for v in args.slices.split(",")]

    out = []
    for z in zs:
        plane, scale = load_plane(args.volume, args.level, z)
        voxel = BASE_VOXEL_UM * scale
        centre = (data["cx"] / scale, data["cy"] / scale)
        if args.command == "degradation":
            rows = radial_contrast(plane, centre, voxel, args.reach_um,
                                   args.step_deg, args.bands, args.prominence)
            out.append({"slice": z, "bands": rows})
            print(f"z = {z}   contraste feuille/interstice par tranche de rayon")
            print(f"  {'rayon (mm)':>14}{'contraste':>11}{'n':>8}")
            for r in rows:
                bar = "#" * int(r["contrast"] * 60)
                print(f"  {r['radius_mm_low']:5.1f}-{r['radius_mm_high']:<8.1f}"
                      f"{r['contrast']:>11.3f}{r['samples']:>8}  {bar}")
            if len(rows) >= 3:
                c = np.array([r["contrast"] for r in rows])
                lo = int(np.argmin(c))
                print()
                print(f"  minimum de contraste : bande {lo} "
                      f"({rows[lo]['radius_mm_low']:.1f}-{rows[lo]['radius_mm_high']:.1f} mm)")
                # ⚠ Un U demande que le minimum soit A L'INTERIEUR, pas a un bord :
                # un profil monotone a lui aussi un minimum, a l'une des extremites.
                interior = 0 < lo < len(rows) - 1
                print(f"  forme : {'U — minimum INTERIEUR' if not interior else 'monotone ou en cloche'}"
                      if False else
                      f"  le minimum est {'a un BORD -> profil monotone, PAS un U' if not interior else 'a l INTERIEUR -> compatible avec un U inverse'}")
        else:
            row = ellipticity(plane, centre, voxel, args.reach_um, args.step_deg, args.threshold)
            row["slice"] = z
            out.append(row)
            print(f"z = {z:6d}  rayon median {row['radius_median_mm']:5.1f} mm  "
                  f"axes {row['axis_short_mm']:5.1f} / {row['axis_long_mm']:5.1f} mm  "
                  f"rapport {row['axis_ratio']:4.2f}  perimetre {row['perimeter_mm']:6.1f} mm")

    if args.command == "ellipticite" and len(out) > 1:
        ratio = np.array([r["axis_ratio"] for r in out])
        perim = np.array([r["perimeter_mm"] for r in out])
        med = np.array([r["radius_median_mm"] for r in out])
        print()
        print(f"rapport d'axes : {ratio.min():.2f} a {ratio.max():.2f}")
        print(f"perimetre      : {perim.min():.1f} a {perim.max():.1f} mm "
              f"(cv {perim.std() / perim.mean():.3f})")
        print(f"rayon median   : {med.min():.1f} a {med.max():.1f} mm "
              f"(cv {med.std() / med.mean():.3f})")
        print()
        # ⚠ C'est le PERIMETRE qui separe les deux hypotheses : un ecrasement
        # conserve la matiere donc la longueur du contour, une perte la reduit.
        cv_p = perim.std() / perim.mean()
        cv_r = med.std() / med.mean()
        print(f"dispersion : perimetre {cv_p:.3f}  contre rayon median {cv_r:.3f}  "
              f"(rapport {cv_p / max(cv_r, 1e-9):.2f})")
        if cv_p < cv_r * 0.5:
            print("-> le contour est BIEN PLUS stable que le rayon : ECRASEMENT")
        elif cv_p > cv_r * 0.9:
            print("-> le contour suit le rayon : PERTE DE MATIERE")
        else:
            print("-> intermediaire : les deux jouent, ni l'un ni l'autre n'est ecarte")

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2) + "\n")
        print(f"\necrit : {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
