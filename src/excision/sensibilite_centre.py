#!/usr/bin/env python3
"""L'invariant rayon/feuilles survit-il à un centre faux ? — la question de `06` §2.3.

`06` §2.3 voulait revérifier l'onde radiale avec le **vrai ombilic**, en soupçonnant le
centre dérivé d'être biaisé. Deux faits l'ont remplacée :

1. ⚠ **`umbilicus.txt` n'existe pas.** Vérifié sur le bucket ouvert, préfixe par
   préfixe : zéro occurrence du mot pour PHercParis4, PHerc0139, PHerc1667 et Scroll1.
   Le fichier noté dans `06` n'est pas à une autre adresse — il n'est pas publié.
2. ⭐ **Le centre n'est pas un barycentre**, contrairement à ce que `06` §2.3 dit. Il est
   ajusté sur la condition qu'une trace de rouleau est une **spirale** : le seul centre
   admissible est celui qui rend l'angle monotone le long de la trace, et la mesure
   refuse en dessous de 0,9 de monotonie. Celui de PHerc0172 vaut **1,000**.

Reste la vraie question, qui ne demande aucun fichier : **de combien le centre doit-il
être faux pour que l'invariant bouge ?** Un résultat robuste à un centre déplacé de
plusieurs écarts inter-feuilles n'a plus besoin d'ombilic ; un résultat fragile n'aurait
jamais dû être publié.

⚠ C'est une analyse de **sensibilité**, pas une validation : elle ne dit pas que le
centre est juste, elle dit ce que ça coûterait qu'il ne le soit pas.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from radial import (VOXEL_UM, count_sheets, load_centre, open_volume,  # noqa: E402
                    ray_profile, spiral_length_mm)


def _rapport_sur_plan(plane, centre: dict, z: int, args) -> dict:
    """Compte de feuilles sur un plan DEJA LU — copie de `radial.slice_report` sans la
    lecture, pour que le meme plan serve a tous les centres essayes."""
    counts, radii = [], []
    for degrees in range(0, 360, args.step_deg):
        profile = ray_profile(plane, centre["cx"], centre["cy"], degrees, args.reach)
        if profile.size < 500:
            continue
        peaks, _, smoothed = count_sheets(profile, args.prominence, args.min_gap)
        body = np.flatnonzero(smoothed > args.body_threshold)
        outer = int(body.max()) if body.size else 0
        counts.append(int((peaks <= outer).sum()) if outer else len(peaks))
        radii.append(outer)
    if not counts:
        return {}
    return {"turns_median": int(np.median(counts)),
            "outer_radius_mm": float(np.median(radii) * VOXEL_UM / 1000.0)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="De combien le centre doit-il etre faux pour que l'invariant bouge ?")
    parser.add_argument("name", help="centre derive (data/axes/<name>.json)")
    parser.add_argument("volume")
    parser.add_argument("--level", default="0",
                        help="⚠⚠ Le NIVEAU 0 par defaut, et c'est deliberé. Les seuils "
                             "`--prominence` et `--min-gap` sont cales au niveau 0 ; a un "
                             "niveau reduit ils comptent 42 feuilles la ou il y en a 176, "
                             "parce que reduire MOYENNE les voxels et remonte le fond "
                             "(piege nº 1 du depot). Une sensibilite mesuree au niveau 2 "
                             "porte alors sur une grandeur qui n'est pas celle publiee")
    parser.add_argument("--slices", type=int, default=6)
    parser.add_argument("--decalages", type=float, nargs="+",
                        default=[0, 10, 25, 50, 100, 200],
                        help="perturbations du centre, en VOXELS du niveau demande")
    parser.add_argument("--reach", type=float, default=4500.0)
    parser.add_argument("--step-deg", type=int, default=20)
    parser.add_argument("--prominence", type=float, default=8.0)
    parser.add_argument("--min-gap", type=int, default=10)
    parser.add_argument("--body-threshold", type=float, default=12.0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    centre = load_centre(args.name)
    array = open_volume(args.volume, args.level)
    facteur = 2 ** int(args.level)
    reglage = SimpleNamespace(reach=args.reach, step_deg=args.step_deg,
                              prominence=args.prominence, min_gap=args.min_gap,
                              body_threshold=args.body_threshold)

    z_lo = int(centre["z_min"] / facteur)
    z_hi = int(centre["z_max"] / facteur)
    tranches = [int(z) for z in np.linspace(z_lo + 1, z_hi - 1, args.slices)]
    voxel_um = VOXEL_UM * facteur

    print(f"volume {array.shape} niveau {args.level} | {len(tranches)} tranches | "
          f"voxel {voxel_um:.2f} um")
    print(f"⚠ un ecart inter-feuilles vaut ~142,8 um, soit "
          f"{142.8 / voxel_um:.1f} voxels a ce niveau\n")
    print(f"{'decalage':>9} {'en um':>8} {'feuilles':>9} {'rayon mm':>9} "
          f"{'invariant um':>13} {'ecart %':>8}")

    # ⚠⚠ LE PLAN EST LU UNE FOIS PAR TRANCHE, pas une fois par decalage. Un plan au
    # niveau 0 fait des milliers de chunks ; la premiere version bouclait sur les
    # decalages a l'exterieur et relisait donc le meme plan cinq fois. Mesure : bloquee
    # a 0 % de CPU pendant onze minutes, sans une ligne de sortie. Le centre change,
    # le volume non.
    par_decalage: dict[float, list[tuple[float, float]]] = {d: [] for d in args.decalages}
    for z in tranches:
        plane = array[z]
        print(f"  tranche z={z} lue", flush=True)
        for d in args.decalages:
            # ⚠ Le decalage est applique en DIAGONALE : deplacer le centre selon un seul
            # axe est le cas le plus favorable, parce que la moitie des rayons le
            # compensent.
            faux = {"cx": centre["cx"] / facteur + d / np.sqrt(2),
                    "cy": centre["cy"] / facteur + d / np.sqrt(2)}
            rep = _rapport_sur_plan(plane, faux, z, reglage)
            if rep:
                par_decalage[d].append((rep["turns_median"], rep["outer_radius_mm"]))

    lignes, reference = [], None
    for d in args.decalages:
        mesures = par_decalage[d]
        if not mesures:
            print(f"{d:>9.0f} {'—':>8} {'aucune tranche mesurable':>44}")
            continue
        tours_m = float(np.median([m[0] for m in mesures]))
        rayon_m = float(np.median([m[1] for m in mesures]))
        invariant = rayon_m * 1000.0 / tours_m if tours_m else float("nan")
        if reference is None:
            reference = invariant
        ecart = 100.0 * (invariant - reference) / reference if reference else float("nan")
        print(f"{d:>9.0f} {d * voxel_um:>8.0f} {tours_m:>9.1f} {rayon_m:>9.2f} "
              f"{invariant:>13.1f} {ecart:>+8.2f}", flush=True)
        lignes.append({"decalage_vx": float(d), "decalage_um": float(d * voxel_um),
                       "feuilles_medianes": tours_m, "rayon_mm": rayon_m,
                       "invariant_um": invariant, "ecart_pct": ecart})

    if lignes:
        pires = max(abs(l["ecart_pct"]) for l in lignes)
        print(f"\n⇒ ecart maximal de l'invariant sur toute la plage : {pires:.2f} %")
        print("  (a comparer au cv de 1,8 % mesure le long de z avec le bon centre)")

    if args.out:
        args.out.write_text(json.dumps(
            {"centre": args.name, "niveau": args.level, "voxel_um": voxel_um,
             "tranches": tranches, "mesures": lignes}, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
