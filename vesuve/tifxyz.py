"""The tifxyz format: three float32 images (x, y, z) of a surface grid, and its `meta.json`.

The contract is the one `villa` reads (`lasagna/approval_inpaint.py:_load_tifxyz_arrays`): three 2D tifs of the
same shape, `meta.json` with `format`, `scale`, `bbox`, `uuid`, `type`, and optional channels such as
`approval.tif`. ⚠ An invalid vertex is -1 or not finite: that is VC3D's sentinel. The research had two answers
(-1 in some readers, 0 in others); there is only one here.
"""
from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tifffile

INVALID = -1.0


@dataclass
class Surface:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    meta: dict

    @property
    def shape(self) -> tuple[int, int]:
        return self.x.shape

    def valid(self) -> np.ndarray:
        return np.isfinite(self.x) & np.isfinite(self.y) & np.isfinite(self.z) & ~(
            (self.x == INVALID) & (self.y == INVALID) & (self.z == INVALID))


def read(source, transport=None) -> Surface:
    """A local folder, or a URL read by `transport` (a folder of the bucket, for instance)."""
    def data(name):
        if transport is None:
            return (Path(source) / name).read_bytes()
        r = transport.get(f"{str(source).rstrip('/')}/{name}")
        if r.body is None:
            raise FileNotFoundError(f"{source}/{name}: {r.reason}")
        return r.body
    meta = json.loads(data("meta.json"))
    x, y, z = (tifffile.imread(io.BytesIO(data(f"{c}.tif"))).astype(np.float32) for c in "xyz")
    if not (x.shape == y.shape == z.shape and x.ndim == 2):
        raise ValueError(f"x, y, z of shapes {x.shape}, {y.shape}, {z.shape}: this is not a tifxyz")
    return Surface(x, y, z, meta)


def write(surface: Surface, folder: Path, approval: np.ndarray | None = None) -> Path:
    """Writes the tifxyz; `approval` (uint8, same shape) becomes `approval.tif`, 255 approved, 0 otherwise."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, a in (("x", surface.x), ("y", surface.y), ("z", surface.z)):
        tifffile.imwrite(folder / f"{name}.tif", np.ascontiguousarray(a, dtype=np.float32))
    ok = surface.valid()
    meta = dict(surface.meta)
    if ok.any():
        pts = np.stack([surface.x[ok], surface.y[ok], surface.z[ok]], axis=1)
        meta["bbox"] = [pts.min(axis=0).tolist(), pts.max(axis=0).tolist()]
    meta.setdefault("format", "tifxyz")
    meta.setdefault("type", "seg")
    (folder / "meta.json").write_text(json.dumps(meta, indent=4))
    if approval is not None:
        if approval.shape != surface.shape:
            raise ValueError(f"approval {approval.shape} against surface {surface.shape}")
        tifffile.imwrite(folder / "approval.tif", np.where(approval > 0, 255, 0).astype(np.uint8))
    return folder


def restrict(surface: Surface, keep: np.ndarray) -> Surface:
    """The same surface, the vertices outside `keep` set to the sentinel."""
    x, y, z = (np.where(keep, a, INVALID).astype(np.float32) for a in (surface.x, surface.y, surface.z))
    return Surface(x, y, z, dict(surface.meta))


def chunk_mask_to_grid(mask: np.ndarray, shape: tuple[int, int], chunk_side: int, scale: float) -> np.ndarray:
    """A mask per chunk of the surface volume (cy, cx) carried onto the tifxyz grid: cell (i, j) of the tifxyz is
    pixel (i / scale, j / scale) of the volume, hence chunk (i / (scale × side), …)."""
    gy, gx = mask.shape
    i = np.minimum((np.arange(shape[0]) / (scale * chunk_side)).astype(int), gy - 1)
    j = np.minimum((np.arange(shape[1]) / (scale * chunk_side)).astype(int), gx - 1)
    return mask[np.ix_(i, j)]
