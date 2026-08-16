#!/usr/bin/env python3
"""Mesure ce que les cellules excisees par `windcheck` echantillonnaient dans le CT.

La reparation de `windcheck` n'est pas un deplacement : elle marque des cellules
invalides et laisse toutes les autres bit-identiques. La trace propre est donc
l'originale MOINS quelques cellules, et la seule question qui decide si cette
reparation retire de la donnee fausse ou du papyrus ordinaire est :

    ces cellules echantillonnaient-elles autre chose que du papyrus ?

Une feuille de papyrus est plus dense que l'interstice entre deux spires, donc la
question se tranche dans le volume, sans modele et sans etiquette.

Ce module ECHANTILLONNE ; il ne conclut pas. La comparaison des distributions est
faite en aval, sur la sortie machine.

Voir docs/04_experience_excision.md pour la conception et le critere de refutation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tifffile

MISSING = -1.0
"""Marqueur de cellule absente dans un tifxyz, sur les trois plans de coordonnees."""


class SamplingError(RuntimeError):
    """Leve quand une precondition de la mesure n'est pas tenue.

    Toujours preferee a un retour degrade : une mesure qui continue sur une
    precondition fausse produit un nombre, et un nombre se lit comme un resultat.
    """


def read_coordinate_planes(mesh_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Lit les trois plans de coordonnees d'un tifxyz."""
    planes = []
    for axis in ("x", "y", "z"):
        path = mesh_dir / f"{axis}.tif"
        if not path.is_file():
            raise SamplingError(f"plan de coordonnees absent : {path}")
        planes.append(tifffile.imread(path))
    if planes[0].shape != planes[1].shape or planes[1].shape != planes[2].shape:
        raise SamplingError(f"plans de formes differentes dans {mesh_dir}")
    return planes[0], planes[1], planes[2]


def valid_cells(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Cellules presentes : aucune des trois coordonnees ne porte le marqueur."""
    return (x != MISSING) & (y != MISSING) & (z != MISSING)


def excised_cells(original: Path, transformed: Path) -> dict:
    """Isole les cellules retirees, et VERIFIE que le reste est intact.

    Les deux controles ci-dessous ne sont pas decoratifs : ils separent « la
    reparation a retire des cellules » de « mon lecteur lit mal ». Sans eux, une
    inversion d'axes ou un decalage de grille se lirait comme une decouverte.
    """
    ox, oy, oz = read_coordinate_planes(original)
    tx, ty, tz = read_coordinate_planes(transformed)
    if ox.shape != tx.shape:
        raise SamplingError(f"grilles de tailles differentes : {ox.shape} vs {tx.shape}")

    valid_original = valid_cells(ox, oy, oz)
    valid_transformed = valid_cells(tx, ty, tz)

    appeared = int((~valid_original & valid_transformed).sum())
    if appeared:
        raise SamplingError(
            f"{appeared} cellules APPARUES apres reparation : une excision ne cree "
            "jamais de cellule, donc la paire de maillages n'est pas ce qu'on croit"
        )

    retained = valid_original & valid_transformed
    for name, before, after in (("x", ox, tx), ("y", oy, ty), ("z", oz, tz)):
        if not np.array_equal(before[retained].view(np.uint32), after[retained].view(np.uint32)):
            raise SamplingError(
                f"les coordonnees {name} des cellules retenues ne sont pas "
                "bit-identiques : le certificat garantit qu'elles le sont, donc "
                "c'est la lecture qui est fausse, pas la reparation"
            )

    return {
        "shape": ox.shape,
        "excised": valid_original & ~valid_transformed,
        "retained": retained,
        "coordinates": (ox, oy, oz),
    }


def matched_controls(
    excised: np.ndarray,
    retained: np.ndarray,
    per_excised: int,
    radius: int,
    seed: int,
) -> np.ndarray:
    """Tire des cellules retenues dans le VOISINAGE de grille des cellules excisees.

    Comparer les cellules excisees a l'ensemble de la trace melangerait l'effet
    cherche avec un effet de position : une trace n'a pas la meme intensite en son
    centre et sur ses bords. Le temoin est donc apparie en voisinage, ce qui retire
    cette explication concurrente au lieu de la laisser ouverte.
    """
    rows, cols = np.nonzero(excised)
    if rows.size == 0:
        raise SamplingError("aucune cellule excisee : rien a comparer")

    generator = np.random.default_rng(seed)
    height, width = excised.shape
    chosen = np.zeros_like(retained, dtype=bool)

    for row, col in zip(rows, cols):
        row_lo, row_hi = max(0, row - radius), min(height, row + radius + 1)
        col_lo, col_hi = max(0, col - radius), min(width, col + radius + 1)
        window = np.zeros_like(retained, dtype=bool)
        window[row_lo:row_hi, col_lo:col_hi] = True
        candidates = np.flatnonzero((retained & window & ~chosen).ravel())
        if candidates.size == 0:
            continue
        take = min(per_excised, candidates.size)
        chosen.ravel()[generator.choice(candidates, take, replace=False)] = True

    return chosen


def sample_volume(array, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Echantillonne au plus proche voisin, sans interpolation.

    Pas d'interpolation, pour deux raisons qui vont dans le meme sens : elle
    lisserait justement le contraste qu'on cherche entre une feuille et un
    interstice, et elle rendrait la mesure dependante d'un ordre de calcul en
    virgule flottante, donc non reproductible d'une machine a l'autre.
    """
    depth, height, width = array.shape
    values = np.full(x.size, -1, dtype=np.int16)
    for index, (xi, yi, zi) in enumerate(zip(x, y, z)):
        zz, yy, xx = int(round(float(zi))), int(round(float(yi))), int(round(float(xi)))
        if 0 <= zz < depth and 0 <= yy < height and 0 <= xx < width:
            values[index] = int(array[zz, yy, xx])
    return values


def open_volume(url: str, level: str):
    """Ouvre un niveau de la pyramide OME-Zarr, en lecture anonyme."""
    import fsspec
    import zarr

    group = zarr.open(fsspec.get_mapper(url, anon=True), mode="r")
    if level not in list(group.array_keys()):
        raise SamplingError(f"niveau {level} absent de {url}")
    return group[level]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Echantillonne le CT aux cellules excisees et a un temoin apparie.",
        epilog=(
            "Sortie machine sur stdout (--json) ou tableau lisible. "
            "Voir docs/04_experience_excision.md pour l'hypothese nulle et les controles."
        ),
    )
    parser.add_argument("original", type=Path, help="repertoire .tifxyz d'origine")
    parser.add_argument("transformed", type=Path, help="repertoire .tifxyz repare")
    parser.add_argument("--volume", required=True, help="URL s3:// du volume OME-Zarr")
    parser.add_argument("--level", default="0", help="niveau de la pyramide (defaut: 0)")
    parser.add_argument(
        "--controls-per-excised", type=int, default=16,
        help="cellules temoins tirees par cellule excisee (defaut: 16)",
    )
    parser.add_argument(
        "--radius", type=int, default=12,
        help="rayon du voisinage de grille ou tirer le temoin (defaut: 12)",
    )
    parser.add_argument("--seed", type=int, default=42, help="graine du tirage (defaut: 42)")
    parser.add_argument("--segment", default="", help="etiquette portee par chaque ligne")
    parser.add_argument("--json", action="store_true", dest="as_json", help="sortie machine")
    args = parser.parse_args()

    try:
        found = excised_cells(args.original, args.transformed)
    except SamplingError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    excised = found["excised"]
    retained = found["retained"]
    ox, oy, oz = found["coordinates"]

    try:
        controls = matched_controls(
            excised, retained, args.controls_per_excised, args.radius, args.seed
        )
        array = open_volume(args.volume, args.level)
    except SamplingError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    rows = []
    for label, selection in (("excised", excised), ("control", controls)):
        indices = np.flatnonzero(selection.ravel())
        if indices.size == 0:
            continue
        values = sample_volume(
            array, ox.ravel()[indices], oy.ravel()[indices], oz.ravel()[indices]
        )
        for flat_index, value in zip(indices, values):
            rows.append(
                {
                    "segment": args.segment or args.original.parent.parent.name,
                    "population": label,
                    "row": int(flat_index // excised.shape[1]),
                    "col": int(flat_index % excised.shape[1]),
                    "intensity": int(value),
                }
            )

    if args.as_json:
        json.dump(rows, sys.stdout)
        sys.stdout.write("\n")
        return 0

    for row in rows:
        print(f"{row['segment']}\t{row['population']}\t{row['row']}\t{row['col']}\t{row['intensity']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
