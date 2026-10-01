"""The transfer to the next winding, computed here: count the sheets along each normal, then let the neighbours vote.

At one point of the surface in eight along each grid axis, the prediction (`m7`) is sampled along the point's normal,
from the surface out to three steps. Its sheets are the runs of samples it marks; the next winding starts from the
centre of the first run after the surface's own, and the neighbours then vote it onto a sheet the ray sees. This is the
rule of `247`, which `248` repeats jump after jump: on segment `20230702185753`, where its rules were written, it lands
on the right winding for 0.9214 of the 39865 points that have a judge, of the 62815 points of the one-in-eight grid, where a fixed step lands for 0.7613
(`R4-F412`); on the central slice of the band `w028-037`, where they were not, for 0.915 against 0.8208 (`R4-F413`).

Ported from `le_transfert_retrouve_t_il_la_spire_voisine.py` (`les_echantillons_longs`, `la_feuille_suivante`,
`les_centres`, `le_consensus`, `le_vote_itere`) and `le_transfert_enchaine_tient_il_les_spires.py` (`lire_le_rayon`) on
the `experimental` branch. The vote is vectorised over the points; it takes the same decisions as the research's loop.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import numpy as np

from vesuve.remote_zarr import BUCKET, RemoteArray
from vesuve.transport import ABSENT

MESH = 8               # one point in eight along each grid axis
OWN_SHEET = 12.0       # voxels: a run starting this close to the surface is the surface's own sheet
REACH_IN_STEPS = 3.0   # how far along the normal the next sheet is looked for
VOTE_SQUARE = 3        # the neighbours that vote: a square of meshes around each point
VOTE_ROUNDS = 30
VOTE_REST = 1e-3       # the vote stops when fewer points than this share change
VOTE_MOVE = 0.5        # voxels: a point whose depth moves by more than this has changed
READ_THREADS = 16


@dataclass(frozen=True)
class Rays:
    """What the prediction sees along the normal of each point of the transfer's mesh, and where each point sits."""
    depths: np.ndarray         # (samples,) signed depths along the normal, voxels
    seen: np.ndarray           # (points, samples) the prediction marks a sheet there
    rows: np.ndarray           # (points,) row of each point on the transfer's grid
    columns: np.ndarray        # (points,) column of each point on the transfer's grid
    grid: tuple[int, int]
    side: float                # +1 or -1: the side of the surface the next winding is looked for on
    step: float                # voxels: the sheet-to-sheet step the fixed-step rule would use
    half_sheet: float          # voxels
    prediction: str
    path: str
    level: int
    factor: int                # the ratio of the volume's shape to the prediction's


def grid_of(rays: Rays):
    """The function that lays one value per point on the transfer's grid, NaN where there is no point."""
    def on_grid(values: np.ndarray) -> np.ndarray:
        g = np.full(rays.grid, np.nan)
        g[rays.rows, rays.columns] = values
        return g
    return on_grid


def depths(side: float, reach: float) -> np.ndarray:
    """The depths sampled along a normal: every voxel from the surface out to `reach`, on `side`."""
    return side * np.arange(0.0, np.floor(reach) + 1.0)


def rays_of_mesh(points: np.ndarray, valid: np.ndarray,
                 mesh: int = MESH) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, tuple[int, int]]:
    """The points of the mesh, one in `mesh`, that have a normal: their positions, normals, grid rows and columns,
    and the grid's shape."""
    from vesuve.transfer.surfaces import normals

    n, has_normal = normals(points, valid)
    on_mesh = np.zeros_like(has_normal)
    on_mesh[::mesh, ::mesh] = True
    ii, jj = np.nonzero(has_normal & on_mesh)
    shape = valid[::mesh, ::mesh].shape
    return points[ii, jj], n[ii, jj], ii // mesh, jj // mesh, (int(shape[0]), int(shape[1]))


def _runs(seen_row: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    edges = np.flatnonzero(np.diff(np.concatenate([[0], seen_row.astype(np.int8), [0]])))
    return edges[::2], edges[1::2]


def sheet_centres(t: np.ndarray, seen: np.ndarray) -> list[np.ndarray]:
    """The centre of every run of sheet samples along each ray: (t[a] + t[b - 1]) / 2 for a run [a, b)."""
    out = []
    for row in seen:
        starts, ends = _runs(row)
        out.append((t[starts] + t[ends - 1]) / 2.0)
    return out


def next_sheet(t: np.ndarray, seen: np.ndarray, own: float = OWN_SHEET) -> np.ndarray:
    """The centre of the first run after the surface's own along each ray; NaN where the ray sees none.

    The own sheet is the first run that starts within `own` voxels of the surface. A ray that does not see it takes
    the first run that starts beyond `own`.
    """
    out = np.full(seen.shape[0], np.nan)
    distance = np.abs(t)
    for k, row in enumerate(seen):
        starts, ends = _runs(row)
        if not len(starts):
            continue
        own_runs = np.flatnonzero(distance[starts] <= own)
        after = starts >= ends[own_runs[0]] if len(own_runs) else distance[starts] > own
        if after.any():
            first = np.flatnonzero(after)[0]
            out[k] = (t[starts[first]] + t[ends[first] - 1]) / 2.0
    return out


def consensus(grid: np.ndarray, square: int = VOTE_SQUARE) -> np.ndarray:
    """The median of the values seen in a square around each cell, where a majority of the square is seen; NaN
    elsewhere."""
    h, w = grid.shape
    r = square // 2
    padded = np.pad(grid, r, constant_values=np.nan)
    stack = np.stack([padded[i:i + h, j:j + w] for i in range(square) for j in range(square)])
    seen = np.isfinite(stack).sum(axis=0)
    with np.errstate(all="ignore"):
        median = np.nanmedian(np.where(seen[None] > 0, stack, 0.0), axis=0)
    return np.where(seen >= square * square // 2 + 1, median, np.nan)


def _padded(centres: list[np.ndarray]) -> np.ndarray:
    widest = max((len(c) for c in centres), default=0)
    out = np.full((len(centres), max(widest, 1)), np.nan)
    for k, c in enumerate(centres):
        out[k, :len(c)] = c
    return out


def vote(centres: list[np.ndarray], start: np.ndarray, rays: Rays,
         rounds: int = VOTE_ROUNDS) -> tuple[np.ndarray, list[int]]:
    """Every point of the mesh aims at the consensus of the points around it, all at once from the previous round's
    depths, and takes the sheet its ray sees nearest to that aim when it lies within half a sheet; otherwise it keeps
    the aim. Returns the final depths and the points that moved by more than half a voxel, per round."""
    on_grid = grid_of(rays)
    table = _padded(centres)
    current = np.asarray(start, dtype=float).copy()
    changes = []
    for _ in range(rounds):
        aim = consensus(on_grid(current))[rays.rows, rays.columns]
        aim = np.where(np.isfinite(aim), aim, current)
        distance = np.abs(table - aim[:, None])
        nearest = np.argmin(np.where(np.isnan(distance), np.inf, distance), axis=1)
        gap = distance[np.arange(len(aim)), nearest]
        new = np.where(gap < rays.half_sheet, table[np.arange(len(aim)), nearest], aim)
        changed = int((np.abs(new - current) > VOTE_MOVE).sum())
        changes.append(changed)
        current = new
        if changed < VOTE_REST * len(current):
            break
    return current, changes


def own_sheet_seen(t: np.ndarray, seen: np.ndarray, own: float = OWN_SHEET) -> np.ndarray:
    """Whether each ray sees the surface's own sheet: a run that starts within `own` voxels of it, on the side read."""
    near = np.abs(t) <= own
    starts = seen & ~np.concatenate([np.zeros((seen.shape[0], 1), dtype=bool), seen[:, :-1]], axis=1)
    return (starts & near[None, :]).any(axis=1)


def produce(rays: Rays) -> dict:
    """The transfer to the next winding on the transfer's grid, NaN where there is no point, with how the vote went,
    how many rays see the surface's own sheet, and how many saw no next sheet (they start from the fixed step)."""
    following = next_sheet(rays.depths, rays.seen)
    start = np.where(np.isfinite(following), following, rays.side * rays.step)
    depth, changes = vote(sheet_centres(rays.depths, rays.seen), start, rays)
    return {"transfer": grid_of(rays)(depth), "rounds": len(changes), "changes": changes,
            "own_sheet_seen": int(own_sheet_seen(rays.depths, rays.seen).sum()),
            "without_next_sheet": int(np.isnan(following).sum()), "points": int(rays.seen.shape[0])}


def share_on_the_right_winding(transfer: np.ndarray, judge: np.ndarray, half_sheet: float) -> float:
    """Where the judge has a depth, the share of points whose transfer lands within half a sheet of it; a point with no
    transfer counts as a miss (`247`, `juger`)."""
    noted = np.isfinite(judge)
    error = transfer[noted] - judge[noted]
    return round(float((np.abs(np.where(np.isfinite(error), error, np.inf)) < half_sheet).mean()), 4)


def prediction(transport, rays: Rays) -> RemoteArray:
    """The published prediction the rays sample, read from the public bucket."""
    return RemoteArray(f"{BUCKET}/{rays.path}", transport, rays.level)


CHUNK_INDEX_BITS = 21


def unique_chunks(indices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The distinct rows of `indices` (n, 3) in lexicographic order, and for each row which one it is.

    The three indices are packed in one 63-bit integer before the sort, because sorting rows (`np.unique(axis=0)`) made the
    cost of a whole reading. An index negative or beyond 2**21 - 1 is sorted as rows, which gives the same answer.
    """
    if len(indices) and (indices.min() < 0 or indices.max() >= 1 << CHUNK_INDEX_BITS):
        keys, which = np.unique(indices, axis=0, return_inverse=True)
        return keys, which.ravel()
    bits = CHUNK_INDEX_BITS
    packed = (indices[:, 0] << (2 * bits)) | (indices[:, 1] << bits) | indices[:, 2]
    unique, which = np.unique(packed, return_inverse=True)
    mask = (1 << bits) - 1
    return np.stack([unique >> (2 * bits), (unique >> bits) & mask, unique & mask], axis=1), which.ravel()


def read_samples(array: RemoteArray, points: np.ndarray, normals_: np.ndarray, rays: Rays,
                 threads: int = READ_THREADS) -> np.ndarray:
    """What `array` marks along the normal of each point, at the depths of `rays`, one chunk at a time.

    A chunk absent from the bucket is empty prediction; a chunk that cannot be read stops the reading with its reason,
    since an unread chunk is not an empty one.
    """
    index = np.floor((points[:, None, :] + rays.depths[None, :, None] * normals_[:, None, :])[..., ::-1]
                     / rays.factor).astype(np.int64)
    flat = index.reshape(-1, 3)
    shape, chunks = np.asarray(array.shape), np.asarray(array.chunks)
    inside = np.flatnonzero(np.all((flat >= 0) & (flat < shape), axis=1))
    values = np.zeros(len(flat), dtype=bool)
    keys, which = unique_chunks(flat[inside] // chunks)
    order = np.argsort(which, kind="stable")
    members_of = np.split(inside[order], np.flatnonzero(np.diff(which[order])) + 1)

    def read_one(k: int):
        key = tuple(int(x) for x in keys[k])
        got = array.chunk(*key)
        if got.block is None:
            if got.reason == ABSENT:
                return
            raise RuntimeError(f"chunk {key} of {rays.prediction} could not be read: {got.reason}")
        members = members_of[k]
        local = flat[members] - keys[k] * chunks
        values[members] = got.block[local[:, 0], local[:, 1], local[:, 2]] > 0

    with ThreadPoolExecutor(max_workers=threads) as pool:
        list(pool.map(read_one, range(len(keys))))
    return values.reshape(index.shape[:2])
