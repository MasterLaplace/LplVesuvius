"""The two surfaces the correction walks: the segment reduced to the transfer's mesh, and the produced winding.

The transfer gives, at one point of the segment in eight along each grid axis, the distance to the next winding
along the segment's normal (`247`, `248`). To walk the lattice on both, each is written as a tifxyz that
`vc_render_tifxyz` renders like the published surface volume: the REDUCED segment, one point in eight, which
measures what the mesh alone costs, and the PRODUCED winding, each of those points pushed by its transfer.

Ported from `la_spire_voisine_est_elle_a_un_pas.py` (`les_normales`) and `la_spire_produite_se_lit_elle_dans_le_treillis.py`
(`le_maillage_reduit`, `le_maillage_produit`, `ecrire_tifxyz`) on the `experimental` branch.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

MESH = 8   # the transfer keeps one point in eight along each grid axis
INVALID = -1.0


def read_points(folder: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """The points (h, w, 3) of a tifxyz in float64, their validity, and the grid spacing in voxels (1 / scale)."""
    import tifffile

    x, y, z = (tifffile.imread(Path(folder) / f"{c}.tif").astype(np.float64) for c in "xyz")
    points = np.stack([x, y, z], axis=-1)
    valid = np.isfinite(points).all(axis=-1) & (x != INVALID) & (y != INVALID) & (z != INVALID)
    meta = json.loads((Path(folder) / "meta.json").read_text())
    return points, valid, 1.0 / float(meta["scale"][0])


def normals(points: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The unit normal of each interior point, by centred differences on the grid.

    The orientation is the grid's (du × dv), hence the same over the whole surface: that is what makes a signed
    distance comparable from one point to the next.
    """
    n = np.zeros_like(points)
    ok = np.zeros(valid.shape, dtype=bool)
    du = points[1:-1, 2:] - points[1:-1, :-2]
    dv = points[2:, 1:-1] - points[:-2, 1:-1]
    c = np.cross(du, dv)
    norm = np.linalg.norm(c, axis=-1)
    interior = (valid[1:-1, 1:-1] & valid[1:-1, 2:] & valid[1:-1, :-2] & valid[2:, 1:-1]
                & valid[:-2, 1:-1] & (norm > 0))
    n[1:-1, 1:-1][interior] = c[interior] / norm[interior][:, None]
    ok[1:-1, 1:-1] = interior
    return n, ok


def reduced_mesh(points: np.ndarray, valid: np.ndarray, mesh: int = MESH) -> tuple[np.ndarray, np.ndarray]:
    """The segment, one point in `mesh`: what the transfer sees of it, and -1 outside it."""
    r, v = points[::mesh, ::mesh], valid[::mesh, ::mesh]
    return np.where(v[..., None], r, INVALID), v


def produced_mesh(points: np.ndarray, valid: np.ndarray, tau: np.ndarray,
                  mesh: int = MESH) -> tuple[np.ndarray, np.ndarray]:
    """The produced winding: each point of the mesh pushed by `tau` voxels along the segment's normal.

    ⚠ This is exactly the first jump of `248`: the normal is the segment's, not recomputed. Where the normal or `tau`
    is missing, the point is -1, as the format wants.
    """
    n, ok = normals(points, valid)
    r, n8, ok8 = points[::mesh, ::mesh], n[::mesh, ::mesh], ok[::mesh, ::mesh]
    if tau.shape != ok8.shape:
        raise ValueError(f"the transfer map is {tau.shape}, the mesh {ok8.shape}")
    good = ok8 & np.isfinite(tau)
    q = r + np.where(good, tau, 0.0)[..., None] * n8
    return np.where(good[..., None], q, INVALID), good


def write_for_render(folder: Path, points: np.ndarray, valid: np.ndarray, scale: float, name: str) -> Path:
    """A tifxyz folder: three float32 grids and the `meta.json` that `vc_render_tifxyz` reads."""
    import tifffile

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for a, c in enumerate("xyz"):
        tifffile.imwrite(folder / f"{c}.tif", points[..., a].astype(np.float32))
    p = points[valid]
    meta = {"bbox": [p.min(axis=0).tolist(), p.max(axis=0).tolist()], "format": "tifxyz",
            "scale": [float(scale), float(scale)], "type": "seg", "uuid": name}
    (folder / "meta.json").write_text(json.dumps(meta, indent=2))
    return folder


def the_two_surfaces(segment_folder: Path, tau: np.ndarray, output: Path, mesh: int = MESH) -> dict:
    """Write the reduced segment and the produced winding under `output`, and say where they are.

    Their scale puts one mesh point every `spacing × mesh` pixels of the render, the pixel being one voxel of the
    published surface volume.
    """
    points, valid, spacing = read_points(segment_folder)
    scale = 1.0 / (spacing * mesh)
    reference, rv = reduced_mesh(points, valid, mesh)
    produced, pv = produced_mesh(points, valid, tau, mesh)
    return {"reference": write_for_render(Path(output) / "reference" / "mesh", reference, rv, scale, "reference"),
            "produced": write_for_render(Path(output) / "produced" / "mesh", produced, pv, scale, "produced"),
            "points": {"reference": int(rv.sum()), "produced": int(pv.sum())}, "scale": scale}
