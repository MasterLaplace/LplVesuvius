"""The text of the produced winding: where the segment passes over it, the ink it carries is the ink read there.

A segment that makes more than one turn passes, in places, over the very winding that the transfer produced from it
(`R4-F411`). The ink map the team published for the segment says, at that place, what text the produced winding must
carry. Our reading of the produced winding is compared with that map there, against two controls on the same pixels:
the map under the block itself (the text of the starting winding, which the produced winding must not copy) and the map
at the facing point shifted by one letter. The reading is first calibrated on the reference. This is a judge that knows
nothing of the transfer; it exists only where the segment passes over the winding it produced, a median share of
0.0222 of a block (`R4-F477`).

Ported from `le_tour_produit_porte_t_il_le_texte_du_segment.py` (slice `296`) on the `experimental` branch. What it
reads is the ink as the model read it, one array per block (`reading`): reading the ink with
`scrollprize/ink_canonical_2um` (1.55 GB, torch) is not done here.
"""
from __future__ import annotations

import importlib.util
import warnings
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Mapping

import numpy as np

CHUNK = 128                 # voxels: the side of a chunk
BLOCK = 16                  # chunks: the side of a block, 2048 voxels
REDUCTION = 8               # the published map is reduced 8 times: a chunk is 16 pixels of it
FAR_ON_THE_SURFACE = 30     # mesh cells: a facing point nearer than this on the surface is the same sheet, a bit further
HALF_SHEET = 36.0           # voxels
SHIFT = 64                  # pixels of the map: the second control, 1.2 mm, more than a letter
NEAREST_CANDIDATES = 64     # nearest points of the segment examined for a facing point
JUDGED_BLOCKS = 6
CALIBRATION_BLOCK = (176, 144)
CALIBRATION_THRESHOLD = 0.8     # below it the reading does not find the published map on the reference
MINIMUM_PIXELS = 10_000
EXCLUDED_BLOCKS = frozenset((176, 64 + BLOCK * k) for k in range(6))
"""The blocks of the band the research looked at before it wrote the rule: it chose them by eye on the published map,
and the calibration block is one of them. The judged blocks are chosen outside it."""

MODEL = "scrollprize/ink_canonical_2um"
MODEL_FILE = "r152_3ddec_v2_l5_epoch13.ckpt"
CALIBRATION_FILE = "calibration.npy"

CARRIES = "the produced winding carries the segment's text where it passes over it"
DOES_NOT_CARRY = "the produced winding does not carry the segment's text where it passes over it"
UNDECIDABLE_CALIBRATION = "undecidable: the reading does not find the published map on the reference"
UNDECIDABLE_PIXELS = "undecidable: too few pixels judged where the segment passes over it"


@dataclass(frozen=True)
class Meshes:
    """The reference (the segment, reduced) and the produced winding on the same mesh grid."""
    reference: np.ndarray        # (h, w, 3) voxels
    reference_valid: np.ndarray  # (h, w)
    produced: np.ndarray
    produced_valid: np.ndarray
    spacing: float               # voxels between two mesh points of the grid

    @cached_property
    def reference_cells(self) -> tuple[np.ndarray, np.ndarray]:
        """The row and the column of each valid point of the reference, in the order of `reference_tree`."""
        return np.nonzero(self.reference_valid)

    @cached_property
    def reference_tree(self):
        from scipy.spatial import cKDTree

        return cKDTree(self.reference[self.reference_valid])


def validity(points: np.ndarray) -> np.ndarray:
    """A mesh point exists when it is finite and not the -1 sentinel of tifxyz on any axis."""
    return np.isfinite(points).all(axis=-1) & (points != -1.0).all(axis=-1)


def facing_points(meshes: Meshes, rows, columns, far: float = FAR_ON_THE_SURFACE,
                  candidates: int = NEAREST_CANDIDATES) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For each produced point of `rows` × `columns`, the nearest point of the reference in 3D among the `candidates`
    nearest, taken farther than `far` mesh cells on the surface: its row, its column and its gap in voxels (NaN where
    there is none)."""
    reference_rows, reference_columns = meshes.reference_cells
    rows, columns = np.asarray(rows), np.asarray(columns)
    facing_row = np.full((len(rows), len(columns)), np.nan)
    facing_column, gap = facing_row.copy(), facing_row.copy()
    a, b = np.nonzero(meshes.produced_valid[np.ix_(rows, columns)])
    if len(a) == 0:
        return facing_row, facing_column, gap
    i, j = rows[a], columns[b]
    distance, index = meshes.reference_tree.query(meshes.produced[i, j], k=min(candidates, len(reference_rows)))
    far_enough = np.hypot(reference_rows[index] - i[:, None], reference_columns[index] - j[:, None]) > far
    found = far_enough.any(axis=1)
    first = np.argmax(far_enough, axis=1)
    chosen = index[np.arange(len(i)), first]
    a, b, chosen, first = a[found], b[found], chosen[found], first[found]
    facing_row[a, b] = reference_rows[chosen]
    facing_column[a, b] = reference_columns[chosen]
    gap[a, b] = distance[np.flatnonzero(found), first]
    return facing_row, facing_column, gap


def block_cells(row: int, column: int, blocks: int, spacing: float) -> tuple[np.ndarray, np.ndarray]:
    """The mesh rows and columns that cover `blocks` blocks from (`row`, `column`), edges included."""
    first_row, last_row = row * CHUNK / spacing, (row + BLOCK) * CHUNK / spacing
    first_column, last_column = column * CHUNK / spacing, (column + BLOCK * blocks) * CHUNK / spacing
    return (np.arange(int(np.floor(first_row)), int(np.ceil(last_row)) + 1),
            np.arange(int(np.floor(first_column)), int(np.ceil(last_column)) + 1))


def near_share(gap: np.ndarray, half_sheet: float = HALF_SHEET) -> float:
    """Among the points that have a facing point, the share whose facing point is within half a sheet."""
    known = np.isfinite(gap)
    return float((gap[known] < half_sheet).mean()) if known.any() else 0.0


def blocks_to_judge(shares: Mapping[tuple[int, int], float], excluded=EXCLUDED_BLOCKS,
                    count: int = JUDGED_BLOCKS) -> list[tuple[int, int]]:
    """The `count` blocks of the largest near share, outside `excluded`; on a tie, in the order of the blocks."""
    candidates = ((block, share) for block, share in shares.items() if block not in excluded)
    return [block for block, _ in sorted(candidates, key=lambda t: (-t[1], t[0]))[:count]]


def coverage(meshes: Meshes, candidates, excluded=EXCLUDED_BLOCKS) -> dict:
    """What the judge can see, from the two meshes alone and before any ink is read: the near share of each candidate
    block, their median, and the blocks the judge would read."""
    shares = {}
    for block in sorted(candidates):
        rows, columns = block_cells(*block, 1, meshes.spacing)
        shares[block] = near_share(facing_points(meshes, rows, columns)[2])
    chosen = blocks_to_judge(shares, excluded)
    values = np.array(list(shares.values())) if shares else np.zeros(1)
    return {"blocks_examined": len(shares), "median_near_share": round(float(np.median(values)), 4),
            "blocks_with_a_near_share_of_half_or_more": int((values >= 0.5).sum()),
            "blocks_with_any_near_share": int((values > 0).sum()),
            "judged_blocks": [list(b) for b in chosen], "judged_near_shares": [round(shares[b], 4) for b in chosen],
            "shares": shares}


def reduce_ink(reading: np.ndarray, factor: int = REDUCTION) -> np.ndarray:
    """The mean over each `factor` × `factor` square, NaN left out; an edge remainder is left aside."""
    h, w = reading.shape[0] // factor, reading.shape[1] // factor
    with np.errstate(invalid="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(reading[:h * factor, :w * factor].reshape(h, factor, w, factor), axis=(1, 3))


def published_under(published: np.ndarray, row: int, column: int, blocks: int) -> np.ndarray:
    """The published map under `blocks` blocks, as it is."""
    side = CHUNK * BLOCK // REDUCTION
    y0, x0 = row * CHUNK // REDUCTION, column * CHUNK // REDUCTION
    return published[y0:y0 + side, x0:x0 + side * blocks]


def _pixels_in_mesh_cells(row, column, blocks, rows, columns, spacing):
    side = CHUNK * BLOCK // REDUCTION
    py, px = np.mgrid[0:side, 0:side * blocks].astype(float)
    return ((row * CHUNK + (py + 0.5) * REDUCTION) / spacing - rows[0],
            (column * CHUNK + (px + 0.5) * REDUCTION) / spacing - columns[0])


def published_facing(published, facing_row, facing_column, rows, columns, row, column, blocks, spacing,
                     shift: int = 0) -> np.ndarray:
    """The published map read at the facing point of each pixel of the band; NaN where there is none."""
    from scipy.ndimage import map_coordinates

    mesh_row, mesh_column = _pixels_in_mesh_cells(row, column, blocks, rows, columns, spacing)
    known = np.isfinite(facing_row)
    r = map_coordinates(np.where(known, facing_row, -1e6), [mesh_row, mesh_column], order=1)
    c = map_coordinates(np.where(known, facing_column, -1e6), [mesh_row, mesh_column], order=1)
    exists = (r >= 0) & (c >= 0)
    per_cell = spacing / REDUCTION
    read = map_coordinates(published, [r * per_cell, c * per_cell + shift], order=1, cval=np.nan)
    read[~exists] = np.nan
    return read


def gap_per_pixel(gap, rows, columns, row, column, blocks, spacing) -> np.ndarray:
    """The gap of the facing point to the nearest mesh point, for each pixel of the band."""
    from scipy.ndimage import map_coordinates

    mesh_row, mesh_column = _pixels_in_mesh_cells(row, column, blocks, rows, columns, spacing)
    return map_coordinates(np.where(np.isfinite(gap), gap, 1e6), [mesh_row, mesh_column], order=0)


def correlation(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None,
                minimum: int = MINIMUM_PIXELS) -> tuple[float | None, int]:
    """The Pearson correlation over the pixels where both are known (and `mask` is true); None under `minimum` pixels
    or where one of them is flat."""
    known = np.isfinite(a) & np.isfinite(b)
    if mask is not None:
        known &= mask
    n = int(known.sum())
    if n < minimum or np.std(a[known]) == 0 or np.std(b[known]) == 0:
        return None, n
    return round(float(np.corrcoef(a[known], b[known])[0, 1]), 4), n


def _compared(reading, published, meshes, row, column, blocks) -> dict:
    rows, columns = block_cells(row, column, blocks, meshes.spacing)
    facing_row, facing_column, gap = facing_points(meshes, rows, columns)
    small = reduce_ink(reading)
    facing = published_facing(published, facing_row, facing_column, rows, columns, row, column, blocks, meshes.spacing)
    shifted = published_facing(published, facing_row, facing_column, rows, columns, row, column, blocks, meshes.spacing,
                               SHIFT)
    under = published_under(published, row, column, blocks)
    h, w = min(small.shape[0], facing.shape[0]), min(small.shape[1], facing.shape[1])
    near = gap_per_pixel(gap, rows, columns, row, column, blocks, meshes.spacing)[:h, :w] < HALF_SHEET
    return {"near_share": near_share(gap), "median_gap_voxels": float(np.nanmedian(gap)) if np.isfinite(gap).any() else None,
            "read": small[:h, :w], "facing": facing[:h, :w], "under": under[:h, :w], "shifted": shifted[:h, :w],
            "near": near}


def _correlations(read, facing, under, shifted, near) -> dict:
    out = {}
    for name, mask in (("within_half_a_sheet", near), ("beyond", ~near)):
        c, n = correlation(read, facing, mask)
        out[name] = {"pixels": n, "facing": c, "control_under_the_block": correlation(read, under, mask)[0],
                     "control_shifted": correlation(read, shifted, mask)[0]}
    return out


def calibrate(reading: np.ndarray, published: np.ndarray, block: tuple[int, int] = CALIBRATION_BLOCK) -> dict:
    """Our reading of the reference, against the published map at the same place."""
    small = reduce_ink(reading)
    under = published_under(published, *block, 1)[:small.shape[0], :small.shape[1]]
    c, n = correlation(small, under)
    return {"block": list(block), "correlation": c, "pixels": n}


def outcome(calibration_correlation: float | None, within_half_a_sheet: dict) -> dict:
    """The declared outcome: carries if the correlation within half a sheet beats both controls; does not if a control
    equals it; undecidable if the calibration does not hold or too few pixels are judged."""
    if calibration_correlation is None or calibration_correlation < CALIBRATION_THRESHOLD:
        return {"outcome": UNDECIDABLE_CALIBRATION, "decidable": False}
    c = within_half_a_sheet.get("facing")
    t1, t2 = within_half_a_sheet.get("control_under_the_block"), within_half_a_sheet.get("control_shifted")
    if c is None or t1 is None or t2 is None or within_half_a_sheet.get("pixels", 0) < MINIMUM_PIXELS:
        return {"outcome": UNDECIDABLE_PIXELS, "decidable": False}
    if c > t1 and c > t2:
        return {"outcome": CARRIES, "decidable": True}
    return {"outcome": DOES_NOT_CARRY, "decidable": True}


def judge(meshes: Meshes, published: np.ndarray, calibration_reading: np.ndarray,
          readings: Mapping[tuple[int, int], np.ndarray], blocks: list[tuple[int, int]]) -> dict:
    """The calibration, then the correlations of each judged block and of all of them together, and the outcome.

    The blocks are pooled the way the research pooled them: every pixel of every block together, within half a sheet
    and beyond."""
    calibration = calibrate(calibration_reading, published)
    per_block, pooled = [], {k: [] for k in ("read", "facing", "under", "shifted", "near")}
    for block in blocks:
        c = _compared(readings[block], published, meshes, *block, 1)
        per_block.append({"block": list(block), "near_share": round(c["near_share"], 4),
                          **_correlations(c["read"], c["facing"], c["under"], c["shifted"], c["near"])})
        for key in pooled:
            pooled[key].append(c[key].ravel())
    together = {k: np.concatenate(v) for k, v in pooled.items()}
    reunited = _correlations(together["read"], together["facing"], together["under"], together["shifted"],
                             together["near"])
    return {"calibration": calibration, "blocks": per_block, "pooled": reunited,
            **outcome(calibration["correlation"], reunited["within_half_a_sheet"])}


def reading_file(block: tuple[int, int]) -> str:
    """The name of the file that holds our reading of the produced winding under `block`."""
    return f"produced_{block[0]}_{block[1]}.npy"


def load_readings(directory: Path, blocks) -> tuple[np.ndarray, dict]:
    """The readings of the ink a folder holds: the calibration block read on the reference, and each judged block read on
    the produced winding. Each is the model's output for the block, a 2048 × 2048 array. A missing file is named, and so is one that is not a 2-D array."""
    directory = Path(directory)
    wanted = [CALIBRATION_FILE, *(reading_file(b) for b in blocks)]
    missing = [name for name in wanted if not (directory / name).is_file()]
    if missing:
        raise FileNotFoundError(f"{directory} lacks {', '.join(missing)}")

    def read(name: str) -> np.ndarray:
        try:
            reading = np.load(directory / name, allow_pickle=False)
        except (OSError, ValueError, EOFError) as x:
            raise ValueError(f"{directory / name} is not a NumPy array: {x}") from x
        if reading.ndim != 2:
            raise ValueError(f"{directory / name} has {reading.ndim} dimensions: a reading is a 2-D array")
        return reading
    return read(CALIBRATION_FILE), {b: read(reading_file(b)) for b in blocks}


def why_the_model_cannot_read(cache: Path) -> str | None:
    """What stops this machine from reading the ink with `scrollprize/ink_canonical_2um`: torch, and the model's file
    under `cache/models/`. None when neither is missing."""
    problems = []
    if importlib.util.find_spec("torch") is None:
        problems.append("torch is not installed")
    model = Path(cache) / "models" / "ink_canonical_2um" / MODEL_FILE
    if not model.is_file():
        problems.append(f"the model is not at {model}")
    return "; ".join(problems) or None
