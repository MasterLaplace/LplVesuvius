#!/usr/bin/env python3
"""Convertir un `.ppm` de Volume Cartographer en `tifxyz`.

⚠ **Ce n'etait pas un blocage, seulement une prudence mal placee.** J'avais note que le
`tifxyz` de `20230909121925` « n'existe nulle part en telechargement » et classe la
tache D comme bloquee. C'est vrai du corpus windcheck, qui est un jeu **curate**. Mais
le `.ppm` publie a cote du segment porte **exactement la meme information** : pour
chaque pixel de la surface aplatie, sa position 3D. La conversion est une lecture
d'en-tete et trois ecritures.

Format PPM de VC, verifie sur le fichier reel :

    width: 3882          <- largeur de la grille, = celle des couches rendues
    height: 11591        <- hauteur, idem
    dim: 6               <- x, y, z, nx, ny, nz
    ordered: true
    type: double
    version: 1
    <>                   <- fin d'en-tete, puis les donnees brutes

⚠ **Les cellules absentes changent de convention** : VC ecrit (0, 0, 0) pour un pixel
non mappe, `tifxyz` ecrit **-1**. Recopier tel quel mettrait toutes les cellules vides
a l'origine du volume, ou elles seraient lues comme de la vraie geometrie -- et une
mesure de proximite y verrait des milliers de points « anormalement proches » les uns
des autres.

⚠ **Sortie en float32 et non float64** : `tifxyz` est lu comme tel par tout ce depot,
et 2,2 Go de double deviennent 540 Mo par plan. La precision d'un float32 est de ~1e-7
en relatif, soit un centieme de voxel sur des coordonnees de l'ordre de 10 000 : sans
consequence pour une geometrie mesuree au voxel.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HEADER_END = b"<>\n"
MISSING = -1.0


def read_header(handle) -> dict:
    """Lire l'en-tete cle: valeur jusqu'au marqueur `<>`."""
    fields: dict[str, str] = {}
    while True:
        line = handle.readline()
        if not line:
            raise ValueError("fin de fichier avant le marqueur d'en-tete `<>`")
        if line == HEADER_END or line.strip() == b"<>":
            return fields
        if b":" in line:
            key, value = line.decode("ascii", "replace").split(":", 1)
            fields[key.strip()] = value.strip()


def convert(ppm_path: Path, out_dir: Path, chunk_rows: int = 512) -> dict:
    with ppm_path.open("rb") as handle:
        fields = read_header(handle)
        width = int(fields["width"])
        height = int(fields["height"])
        dim = int(fields["dim"])
        if fields.get("type") != "double":
            raise ValueError(f"type non gere : {fields.get('type')}")
        if dim < 3:
            raise ValueError(f"dim = {dim} : il faut au moins x, y, z")

        out_dir.mkdir(parents=True, exist_ok=True)
        planes = {axis: np.empty((height, width), dtype=np.float32) for axis in "xyz"}

        # ⚠ Lecture PAR BANDES : le fichier fait 2,2 Go en double et le tenir entier
        # en memoire n'apporte rien -- la conversion est ligne a ligne.
        row_bytes = width * dim * 8
        missing = 0
        for start in range(0, height, chunk_rows):
            rows = min(chunk_rows, height - start)
            raw = handle.read(rows * row_bytes)
            if len(raw) != rows * row_bytes:
                raise ValueError(f"fichier tronque a la ligne {start}")
            block = np.frombuffer(raw, dtype=np.float64).reshape(rows, width, dim)
            empty = ~np.any(block[:, :, :3] != 0.0, axis=2)
            missing += int(empty.sum())
            for index, axis in enumerate("xyz"):
                values = block[:, :, index].astype(np.float32)
                values[empty] = MISSING
                planes[axis][start:start + rows] = values

    import tifffile

    for axis, data in planes.items():
        tifffile.imwrite(out_dir / f"{axis}.tif", data)
    return {"width": width, "height": height, "dim": dim,
            "cells": width * height, "missing": missing}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convertir un .ppm de Volume Cartographer en tifxyz (x/y/z.tif).",
        epilog="Les cellules non mappees passent de (0,0,0) a -1, convention tifxyz.",
    )
    parser.add_argument("ppm", type=Path)
    parser.add_argument("out", type=Path, help="repertoire de sortie (recevra x/y/z.tif)")
    parser.add_argument("--chunk-rows", type=int, default=512)
    args = parser.parse_args()

    if not args.ppm.is_file():
        print(f"erreur : {args.ppm} absent", file=sys.stderr)
        return 2
    try:
        report = convert(args.ppm, args.out, args.chunk_rows)
    except ValueError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 3

    filled = report["cells"] - report["missing"]
    print(f"{report['width']} x {report['height']}  (dim {report['dim']})")
    print(f"cellules remplies : {filled} / {report['cells']} "
          f"({filled / report['cells'] * 100:.1f} %)")
    print(f"ecrit : {args.out}/x.tif, y.tif, z.tif")
    return 0


if __name__ == "__main__":
    sys.exit(main())
