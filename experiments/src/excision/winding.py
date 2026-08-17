#!/usr/bin/env python3
"""Monotonie radiale du numero de spire : la mesure ORDINALE du saut de spire.

L'idee, due a l'auteur : le long d'un rayon partant du centre du rouleau, on
traverse les feuilles dans un ORDRE, et cet ordre doit etre strictement croissant.
Un saut de spire le viole.

Pourquoi c'est superieur a toutes les mesures metriques essayees avant : elle est
ORDINALE, donc elle n'a besoin d'AUCUNE reference locale. Or l'espacement entre
feuilles varie de 101 a 303 um selon l'endroit et croit de 28 % du coeur vers
l'exterieur -- c'est exactement ce qui a fait echouer la metrique de proximite, qui
doit se normaliser par un voisinage. Un ordre, lui, est insensible au tassement.

Le centre n'est pas lu dans un fichier : il est DERIVE de la trace, en cherchant
celui qui rend l'angle monotone le long du deroulement. C'est ce qui definit une
spirale, et ca se verifie (rho mesure a +0,999 sur une trace reelle) au lieu de se
supposer -- l'ombilic publie par ThaumatoAnakalyptor est dans un repere qui ne
correspond pas a celui de ces traces.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tifffile

MISSING = -1.0


class WindingError(RuntimeError):
    """Leve quand la geometrie ne permet pas la mesure."""


def load_trace(mesh_dir: Path):
    planes = []
    for axis in ("x", "y", "z"):
        path = mesh_dir / f"{axis}.tif"
        if not path.is_file():
            raise WindingError(f"plan absent : {path}")
        planes.append(tifffile.imread(path))
    x, y, z = planes
    valid = (x != MISSING) & (y != MISSING) & (z != MISSING)
    if not valid.any():
        raise WindingError(f"aucune cellule valide dans {mesh_dir}")
    rows, cols = np.nonzero(valid)
    return x[valid], y[valid], z[valid], rows, cols


def derive_centre(x, y, cols, sample, seed=0):
    """Centre qui rend l'angle monotone le long du deroulement.

    Une trace de rouleau EST une spirale autour de son axe : le seul centre pour
    lequel l'angle croit regulierement avec la colonne est le bon. On le cherche
    donc par cette propriete, qu'on peut ensuite verifier -- plutot que de faire
    confiance a un fichier dont le repere n'est pas garanti.
    """
    from scipy.optimize import minimize
    from scipy.stats import spearmanr

    xs, ys, cs = x[sample], y[sample], cols[sample]
    order = np.argsort(cs)

    def cost(centre):
        angle = np.unwrap(np.arctan2(ys - centre[1], xs - centre[0])[order])
        return -abs(spearmanr(np.arange(angle.size), angle).statistic)

    best = None
    for gx in np.linspace(x.min(), x.max(), 5):
        for gy in np.linspace(y.min(), y.max(), 5):
            found = minimize(
                cost, [gx, gy], method="Nelder-Mead",
                options={"maxiter": 300, "xatol": 5, "fatol": 1e-4},
            )
            if best is None or found.fun < best.fun:
                best = found
    return float(best.x[0]), float(best.x[1]), float(-best.fun)


def winding_numbers(x, y, cols, centre):
    """Numero de spire de chaque point, continu, depuis le deroulement.

    L'angle est deroule dans l'ordre de la PARAMETRISATION et non dans celui du
    plan : c'est le seul ordre qui suit la feuille. Deroule dans l'ordre du plan,
    on recollerait deux spires voisines en une seule.
    """
    cx, cy = centre
    order = np.argsort(cols, kind="stable")
    angle = np.empty(x.size)
    angle[order] = np.unwrap(np.arctan2(y[order] - cy, x[order] - cx))
    return angle / (2.0 * np.pi)


def radial_violations(x, y, z, winding, centre, rays: int, tolerance: float,
                      min_points: int, slab: float = 60.0):
    """Compte les inversions d'ordre le long de rayons partant du centre.

    ⚠ Le test se fait PAR TRANCHE et non globalement. Un rayon depuis l'axe est une
    notion EN COUPE : melanger des points de z differents compare des spires qui
    n'ont aucune raison de s'ordonner entre elles. Mesure de la faute : sans le
    decoupage, une trace a ZERO croisement rendait 42,9 % de violations -- un
    resultat qui ne pouvait venir que de la methode, puisque la trace est saine.

    Sur un rayon, les points rencontres en s'eloignant du centre doivent avoir un
    numero de spire croissant. Une inversion est un endroit ou la surface revient
    vers une spire deja depassee : la signature geometrique du saut de spire.

    La tolerance existe parce qu'une feuille a une EPAISSEUR et que deux points de
    la meme feuille peuvent s'inverser de facon insignifiante. Elle est exprimee en
    tours, donc elle ne depend pas du tassement local.
    """
    cx, cy = centre
    radius = np.hypot(x - cx, y - cy)
    theta = np.arctan2(y - cy, x - cx)
    slabs = np.floor((z - z.min()) / slab).astype(np.int64)

    checked = 0
    violations = 0
    worst = 0.0
    slabs_used = 0
    for slab_id in np.unique(slabs):
        here = slabs == slab_id
        if here.sum() < min_points * 4:
            continue
        slabs_used += 1
        for index in range(rays):
            target = -np.pi + 2.0 * np.pi * index / rays
            # Bande angulaire etroite : un secteur, pas un rayon exact, sinon on
            # n'attrape presque aucun point sur un maillage discret.
            delta = np.abs(np.angle(np.exp(1j * (theta - target))))
            band = here & (delta < (np.pi / rays))
            if band.sum() < min_points:
                continue
            order = np.argsort(radius[band])
            sequence = winding[band][order]
            drops = np.diff(sequence)
            checked += drops.size
            bad = drops < -tolerance
            violations += int(bad.sum())
            if bad.any():
                worst = max(worst, float(-drops[bad].min()))

    return {
        "rays": rays,
        "slabs_used": slabs_used,
        "pairs_checked": checked,
        "violations": violations,
        "violation_rate": float(violations / checked) if checked else float("nan"),
        "worst_drop_turns": worst,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monotonie radiale du numero de spire (mesure ordinale).",
        epilog="Ne demande ni volume, ni modele, ni ombilic publie.",
    )
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--sample", type=int, default=40000)
    parser.add_argument("--rays", type=int, default=720)
    parser.add_argument(
        "--tolerance", type=float, default=0.25,
        help="recul tolere, en tours (defaut: 0.25 = un quart de spire)",
    )
    parser.add_argument("--min-points", type=int, default=20)
    parser.add_argument(
        "--slab", type=float, default=60.0,
        help="epaisseur de tranche en voxels ; le test radial est une notion EN COUPE",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--label", default="")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        x, y, z, _, cols = load_trace(args.mesh)
    except WindingError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    generator = np.random.default_rng(args.seed)
    take = min(args.sample, x.size)
    sample = generator.choice(x.size, take, replace=False)

    cx, cy, quality = derive_centre(x, y, cols, sample, args.seed)
    # Un centre mal derive rendrait tout le reste sans valeur : on refuse plutot
    # que de rapporter des violations qui ne mesureraient que le mauvais centre.
    if quality < 0.9:
        print(
            f"erreur : centre peu fiable (monotonie {quality:.3f} < 0.9). "
            "Cette trace ne se lit pas comme une spirale.",
            file=sys.stderr,
        )
        return 3

    xs, ys, zs, cs = x[sample], y[sample], z[sample], cols[sample]
    winding = winding_numbers(xs, ys, cs, (cx, cy))
    report = {
        "label": args.label or args.mesh.parent.parent.name,
        "points": int(take),
        "centre": [cx, cy],
        "spiral_quality": quality,
        "turns_spanned": float(winding.max() - winding.min()),
        **radial_violations(xs, ys, zs, winding, (cx, cy), args.rays, args.tolerance,
                            args.min_points, args.slab),
    }

    if args.as_json:
        json.dump(report, sys.stdout)
        sys.stdout.write("\n")
        return 0
    for key, value in report.items():
        print(f"{key:20} {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
