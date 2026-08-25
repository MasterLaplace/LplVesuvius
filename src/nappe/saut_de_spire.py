#!/usr/bin/env python3
"""Détecter les sauts de spire d'une trace, en lisant la phase d'enroulement publiée.

⚠⚠ **La quantité qui rend le saut de spire NOMMABLE.** `docs/00` §2 le dit : *« ce qui
manque entre les deux familles de mailleurs est le numéro d'enroulement — la seule
quantité qui rende le sheet switching nommable : deux points d'une même feuille le
partagent, un saut l'incrémente »*. Et le tableau des goulots de `2026_open_problems`
demande, pour les sauts de spire : *« stronger local continuity constraints and
**conservative failure detection** »*.

Cette quantité **est publiée** : le groupe `lasagna` de chaque rouleau expose un canal
`cos` — le cosinus de la phase d'enroulement, par voxel, en OME-Zarr. Quatre rouleaux
l'ont, dont les trois qui ont des traces, donc la mesure est **validable**.

⚠ **Mesuré avant de théoriser** : la période de ce champ vaut **3 à 7 fois le pas
inter-feuilles** (614 à 1228 µm pour un pas de ~170 µm), pas une période par feuille. Il
est donc **diffusé et lisse** — et c'est ce qu'il faut : un saut d'une spire y déplace la
valeur d'une **fraction** de période, donc il laisse une marche. Une période par feuille
rendrait un saut d'exactement une spire **invisible**, ce qui est le pire cas possible.

**Le principe.** Sur une trace correcte, la phase varie **continûment** d'une cellule à
sa voisine. Un saut de spire est une **discontinuité**. On échantillonne donc la phase
le long de la paramétrisation et on mesure la taille des marches.

⚠ **La discontinuité se mesure entre cellules ADJACENTES dans la paramétrisation**, pas
en 3D : deux cellules voisines dans l'image sont censées être voisines sur la feuille,
et c'est exactement cette promesse qu'un saut brise.

⚠ **Les lectures sont groupées par chunk** : un chunk fait 32³ voxels et 32 Ko
compressés, et le redemander par point ferait des milliers de requêtes pour une seule
trace.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def load_mesh(mesh_dir: Path):
    """Positions 3D d'une trace tifxyz, avec leurs coordonnées de grille."""
    import tifffile

    planes = [tifffile.imread(mesh_dir / f"{a}.tif") for a in ("x", "y", "z")]
    x, y, z = planes
    valid = (x != -1.0) & (y != -1.0) & (z != -1.0)
    rows, cols = np.nonzero(valid)
    return np.column_stack([x[valid], y[valid], z[valid]]), rows, cols


def read_phase(url: str, level: int, meta: dict, points: np.ndarray,
               reduction: float, timeout: float):
    """Phase lue aux positions données. Rend NaN là où le chunk manque.

    ⚠ Les points sont regroupés PAR CHUNK et chaque chunk n'est demandé qu'une fois.
    """
    depth, hy, hx = meta["chunks"]
    shape = meta["shape"]
    # tifxyz donne (x, y, z) ; le zarr est indexé (z, y, x).
    voxel = points[:, ::-1] / reduction
    index = np.floor(voxel).astype(np.int64)
    inside = np.all((index >= 0) & (index < np.asarray(shape)), axis=1)
    out = np.full(points.shape[0], np.nan)
    keys = np.column_stack([index[:, 0] // depth, index[:, 1] // hy, index[:, 2] // hx])
    seen: dict[tuple, np.ndarray | None] = {}
    for position in np.flatnonzero(inside):
        key = tuple(int(v) for v in keys[position])
        if key not in seen:
            raw = get(f"{url}/{chunk_key(meta, level, key[1], key[2], key[0])}", timeout)
            data = decode(raw, meta, depth * hy * hx) if raw is not None else None
            seen[key] = (np.frombuffer(data, dtype=np.dtype(meta["dtype"]))
                         .reshape(depth, hy, hx) if data is not None else None)
        block = seen[key]
        if block is None:
            continue
        iz, iy, ix = index[position]
        out[position] = float(block[iz % depth, iy % hy, ix % hx])
    return out, len(seen)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sauts de spire d'une trace, via la phase d'enroulement publiee.",
        epilog="Une discontinuite entre cellules voisines EST un saut de feuille.",
    )
    parser.add_argument("mesh", type=Path, help="repertoire .tifxyz")
    parser.add_argument("cos", help="cle S3 du .ome.zarr du canal cos")
    parser.add_argument("--level", type=int, default=3)
    parser.add_argument("--reduction", type=float, default=8.0,
                        help="rapport entre les voxels du maillage et ceux du canal lu")
    parser.add_argument("--sample", type=int, default=4000)
    parser.add_argument("--run", type=int, default=48,
                        help="longueur du segment CONTIGU lu sur chaque ligne. Un saut "
                             "de feuille se voit entre voisins, donc les cellules "
                             "comparees doivent l'etre")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--label", default="")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    url = args.cos if args.cos.startswith("http") else f"{BUCKET}/{args.cos}"
    try:
        meta = array_meta(url, args.level, args.timeout)
    except RuntimeError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    points, rows, cols = load_mesh(args.mesh)
    generator = np.random.default_rng(args.seed)
    # ⚠ On tire des LIGNES entieres de la parametrisation, pas des points isoles : la
    # grandeur mesuree est un ecart entre VOISINS, et des points tires au hasard n'ont
    # pas de voisin.
    unique_rows = np.unique(rows)
    take = min(max(4, args.sample // args.run), unique_rows.size)
    chosen = generator.choice(unique_rows, take, replace=False)

    steps = []
    chunks_lus = 0
    for r in chosen:
        line = np.flatnonzero(rows == r)
        if line.size < 8:
            continue
        # ⚠⚠ UN SEGMENT CONTIGU, pas un sous-echantillonnage de la ligne entiere. La
        # premiere version prenait une cellule sur 40, donc les points compares etaient
        # a quarante colonnes l'un de l'autre -- et la grandeur mesuree n'etait plus la
        # continuite entre VOISINS, qui est la seule chose qu'un saut de feuille brise.
        # Mon propre docstring disait « adjacentes » pendant que le code faisait
        # l'inverse, et la mesure ne separait rien.
        order = np.argsort(cols[line])
        line = line[order]
        if line.size > args.run:
            start = int(generator.integers(0, line.size - args.run))
            line = line[start:start + args.run]
        phase, n = read_phase(url, args.level, meta, points[line], args.reduction,
                              args.timeout)
        chunks_lus += n
        good = np.isfinite(phase)
        if good.sum() < 4:
            continue
        # ⚠ L'ecart est ramene au pas de colonne parcouru : deux cellules distantes de
        # dix colonnes ont le droit de differer plus que deux voisines.
        gaps = np.abs(np.diff(phase[good]))
        span = np.abs(np.diff(cols[line][good])).astype(float)
        steps.append(gaps / np.maximum(span, 1.0))

    if not steps:
        print("erreur : aucune ligne exploitable", file=sys.stderr)
        return 3
    steps = np.concatenate(steps)
    label = args.label or args.mesh.parent.parent.name
    report = {"label": label, "lignes": len(chosen), "marches": int(steps.size),
              "chunks_lus": chunks_lus,
              "marche_mediane": float(np.median(steps)),
              "marche_p95": float(np.percentile(steps, 95)),
              "marche_p99": float(np.percentile(steps, 99)),
              "marche_max": float(steps.max())}
    print(f"{label[:36]:36} marches {steps.size:6d}  "
          f"mediane {report['marche_mediane']:6.2f}  p95 {report['marche_p95']:7.2f}  "
          f"p99 {report['marche_p99']:7.2f}  max {report['marche_max']:8.2f}  "
          f"({chunks_lus} chunks)")
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
