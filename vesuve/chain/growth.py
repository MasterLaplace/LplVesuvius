"""Growing a surface from `m7`: a plane laid on a seed finds the sheets along its normals and grows from the seed; the
jump gives the next winding the same way from a surface; a held winding is grown again from its own points, by one mesh
at most (`R4-F551`).

Ported from `une_nappe_tiree_de_m7_suit_elle_sa_feuille.py` (slice `300`), `une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.py`
(`305`), `la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.py` (`306`) and
`la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse.py` (`333`, with the margin of `335`) on the
`experimental` branch. The research changes module constants for the time of a block to run at another scroll's step;
here the step is a parameter, `Scale`.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from vesuve.chain.surface import ReadValues, Surface, to_prediction_indices
from vesuve.transfer.surfaces import normals

PLANE_SIDE = 65              # points per side of the plane laid on a seed
PLANE_SPACING = 10.0         # voxels between two points of the plane
OWN_SHEET = 3.0              # voxels: a run that touches this depth, or depth zero, is the surface's own sheet
JUMP_REACH_IN_STEPS = 3.0
NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


@dataclass(frozen=True)
class Scale:
    """The sheet-to-sheet step of a scroll, in voxels of the prediction level read, and what follows from it."""
    step: float

    @property
    def tolerance(self) -> float:
        """A quarter step: a sheet further than this from where the growth aims is not taken."""
        return self.step / 4.0

    @property
    def half_reach(self) -> float:
        """How far each side of the plane the sheets are looked for: a step and a half."""
        return 1.5 * self.step


PHERCPARIS4 = Scale(step=173.0 / 2.4 / 4.0)     # 18.02 voxels of 9.6 µm
PHERC0358 = Scale(step=187.24 / 9.362)          # 20 voxels of 9.362 µm


@dataclass(frozen=True)
class Grown:
    """A surface grown from `m7`, with what it grew from."""
    surface: Surface
    offsets: np.ndarray        # (h, w) along the normal of the plane, NaN where nothing is laid
    seeded: np.ndarray         # (h, w) the cells that were seeds, before the growth
    touched: int = 0           # cells the winding it grew from fell on


@dataclass(frozen=True)
class Jump:
    """The next winding of a surface, point by point."""
    surface: Surface
    steps: np.ndarray          # (h, w) the step each point took along its normal
    start: tuple[int, int] | None
    next_sheets: np.ndarray    # (h, w) the first sheet after its own that each point sees, NaN if none


def plane(seed_xyz, normal_xyz, side: int = PLANE_SIDE, spacing: float = PLANE_SPACING) -> tuple[np.ndarray, np.ndarray]:
    """A plane of `side` × `side` points perpendicular to the normal and centred on the seed; and the unit normal."""
    n = np.asarray(normal_xyz, dtype=float)
    n = n / np.linalg.norm(n)
    a = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    k = (np.arange(side) - (side - 1) / 2.0) * spacing
    grid = (np.asarray(seed_xyz, dtype=float)[None, None, :] + k[:, None, None] * v[None, None, :]
            + k[None, :, None] * u[None, None, :])
    return grid, n


def sheet_centres(seen: np.ndarray, depths: np.ndarray) -> list[np.ndarray]:
    """The centres of the runs of sheet along each ray."""
    out = []
    for ray in seen:
        if not ray.any():
            out.append(np.empty(0))
            continue
        edges = np.flatnonzero(np.diff(np.concatenate([[0], ray.astype(np.int8), [0]])))
        out.append(np.array([(depths[a] + depths[b - 1]) / 2.0 for a, b in zip(edges[::2], edges[1::2])]))
    return out


def sheet_after_own(depths: np.ndarray, seen: np.ndarray, own: float = OWN_SHEET) -> np.ndarray:
    """The centre of the first run after the one that touches `|depth| <= own` or depth zero; without such a run, the first
    beyond; NaN where the ray sees none."""
    out = np.full(seen.shape[0], np.nan)
    absolute = np.abs(depths)
    for k, ray in enumerate(seen):
        if not ray.any():
            continue
        edges = np.flatnonzero(np.diff(np.concatenate([[0], ray.astype(np.int8), [0]])))
        runs = list(zip(edges[::2], edges[1::2]))
        own_runs = [(a, b) for a, b in runs if absolute[a] <= own or absolute[b - 1] <= own
                    or (depths[a] <= 0 <= depths[b - 1]) or (depths[b - 1] <= 0 <= depths[a])]
        after = [(a, b) for a, b in runs if absolute[a] > own] if not own_runs else \
            [(a, b) for a, b in runs if a >= own_runs[0][1]]
        if after:
            a, b = after[0]
            out[k] = (depths[a] + depths[b - 1]) / 2.0
    return out


def extend(centres: list[np.ndarray], shape: tuple, offsets: np.ndarray, laid: np.ndarray, tolerance: float,
           allowed: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Breadth-first growth from every point already laid at once, in the order of the grid: each point takes the sheet nearest
    the median of its laid neighbours, within `tolerance`; otherwise it is looked at again when one more neighbour is laid.
    With `allowed`, only those points are laid. Changes and returns `offsets` and `laid`."""
    h, w = shape
    queue = deque((int(a), int(b)) for a, b in zip(*np.nonzero(laid)))
    while queue:
        i, j = queue.popleft()
        for di, dj in NEIGHBOURS:
            a, b = i + di, j + dj
            if not (0 <= a < h and 0 <= b < w) or laid[a, b] or (allowed is not None and not allowed[a, b]):
                continue
            around = [offsets[a + x, b + y] for x, y in NEIGHBOURS
                      if 0 <= a + x < h and 0 <= b + y < w and laid[a + x, b + y]]
            aim = float(np.median(around))
            runs = centres[a * w + b]
            if not len(runs):
                continue
            m = int(np.argmin(np.abs(runs - aim)))
            if abs(runs[m] - aim) <= tolerance:
                offsets[a, b], laid[a, b] = runs[m], True
                queue.append((a, b))
    return offsets, laid


def grow(centres: list[np.ndarray], shape: tuple, start: tuple[int, int], tolerance: float, half_reach: float,
         aim_at_start: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """The growth from one point: it takes the sheet nearest `aim_at_start` within `half_reach`, and the rest follows."""
    h, w = shape
    offsets = np.full(shape, np.nan)
    laid = np.zeros(shape, dtype=bool)
    i0, j0 = start
    runs = centres[i0 * w + j0]
    if not len(runs):
        return offsets, laid
    k = int(np.argmin(np.abs(runs - aim_at_start)))
    if abs(runs[k] - aim_at_start) > half_reach:
        return offsets, laid
    offsets[i0, j0], laid[i0, j0] = runs[k], True
    return extend(centres, shape, offsets, laid, tolerance)


def _centres_on_plane(grid: np.ndarray, normal: np.ndarray, read_values: ReadValues, scale: Scale):
    shape = grid.shape[:2]
    points = grid.reshape(-1, 3)
    depths = np.arange(-np.floor(scale.half_reach), np.floor(scale.half_reach) + 1.0)
    along = points[:, None, :] + depths[None, :, None] * normal[None, None, :]
    return shape, points, sheet_centres(read_values(to_prediction_indices(along)) > 0, depths)


def grow_from_seed(seed_xyz, normal_xyz, read_values: ReadValues, scale: Scale) -> Grown:
    """The plane laid on the seed, the sheets of `m7` along each of its points, then the growth from the central point."""
    grid, normal = plane(seed_xyz, normal_xyz)
    shape, points, centres = _centres_on_plane(grid, normal, read_values, scale)
    offsets, laid = grow(centres, shape, (shape[0] // 2, shape[1] // 2), scale.tolerance, scale.half_reach)
    surface = (points + np.nan_to_num(offsets.ravel())[:, None] * normal[None, :]).reshape(shape + (3,))
    return Grown(Surface(surface, laid), offsets, np.zeros(shape, dtype=bool))


def targets(winding: Surface, grid: np.ndarray, normal: np.ndarray, spacing: float = PLANE_SPACING) -> np.ndarray:
    """For each cell of the plane `grid`, the offset along `normal` of the laid point of the winding that falls nearest its
    centre; NaN where none falls. On a tie, the first in the order of the winding."""
    shape = grid.shape[:2]
    target = np.full(shape, np.nan)
    points = winding.points[winding.valid]
    if not len(points):
        return target
    rows = (grid[1, 0] - grid[0, 0]) / spacing
    columns = (grid[0, 1] - grid[0, 0]) / spacing
    d = points - grid[0, 0]
    a, b, height = d @ rows / spacing, d @ columns / spacing, d @ normal
    ia, ib = np.rint(a).astype(np.int64), np.rint(b).astype(np.int64)
    inside = (ia >= 0) & (ia < shape[0]) & (ib >= 0) & (ib < shape[1])
    if not inside.any():
        return target
    k = np.flatnonzero(inside)
    distance = (a[k] - ia[k]) ** 2 + (b[k] - ib[k]) ** 2
    order = k[np.lexsort((np.arange(len(k)), distance))]
    _, firsts = np.unique(ia[order] * shape[1] + ib[order], return_index=True)
    kept = order[firsts]
    target[ia[kept], ib[kept]] = height[kept]
    return target


def allowed_cells(seeded: np.ndarray, margin: int) -> np.ndarray:
    """The cells within `margin` cells of a seeded cell, diagonals counted."""
    from scipy.ndimage import binary_dilation

    if margin <= 0 or not seeded.any():
        return seeded.copy()
    return binary_dilation(seeded, structure=np.ones((3, 3), dtype=bool), iterations=int(margin))


def regrow(winding: Surface, seed_xyz, normal_xyz, read_values: ReadValues, scale: Scale, margin: int | None = None) -> Grown:
    """A plane laid on a seed of the winding; each cell where a point of the winding falls takes the sheet of `m7` nearest
    that point's offset, within `tolerance`; then the growth from all those cells. With `margin`, the growth lays nothing
    further than `margin` cells from a seeded cell: one mesh is the regrowth of `R4-F551`."""
    grid, normal = plane(seed_xyz, normal_xyz)
    shape, points, centres = _centres_on_plane(grid, normal, read_values, scale)
    target = targets(winding, grid, normal).ravel()
    offsets = np.full(shape, np.nan)
    laid = np.zeros(shape, dtype=bool)
    for k in np.flatnonzero(np.isfinite(target)):
        runs = centres[k]
        if not len(runs):
            continue
        m = int(np.argmin(np.abs(runs - target[k])))
        if abs(runs[m] - target[k]) <= scale.tolerance:
            offsets.flat[k], laid.flat[k] = runs[m], True
    seeded = laid.copy()
    allowed = None if margin is None else allowed_cells(seeded, margin)
    offsets, laid = extend(centres, shape, offsets, laid, scale.tolerance, allowed)
    surface = (points + np.nan_to_num(offsets.ravel())[:, None] * normal[None, :]).reshape(shape + (3,))
    return Grown(Surface(surface, laid), offsets, seeded, int(np.isfinite(target).sum()))


def jump_start(next_sheets: np.ndarray, shape: tuple) -> tuple[int, int] | None:
    """The point nearest the centre of the grid that sees a sheet after its own; on a tie, the first in the order of the grid."""
    h, w = shape
    found = np.isfinite(next_sheets.reshape(shape))
    if not found.any():
        return None
    i, j = np.nonzero(found)
    k = int(np.argmin((i - (h - 1) / 2.0) ** 2 + (j - (w - 1) / 2.0) ** 2))
    return int(i[k]), int(j[k])


def jump(surface: Surface, side: float, read_values: ReadValues, scale: Scale) -> Jump:
    """From each point laid of a surface, along its recomputed normal on `side` (+1 or -1), the sheets of `m7` over three steps;
    the start takes the first sheet after its own, then the growth. The winding it gives is the next one."""
    shape = surface.valid.shape
    point_normals, has_normal = normals(surface.points, surface.valid)
    q, nq = surface.points.reshape(-1, 3), point_normals.reshape(-1, 3)
    depths = side * np.arange(0.0, JUMP_REACH_IN_STEPS * scale.step + 1.0)
    along = q[:, None, :] + depths[None, :, None] * nq[:, None, :]
    seen = (read_values(to_prediction_indices(along)) > 0) & has_normal.reshape(-1)[:, None]
    after = sheet_after_own(depths, seen)
    start = jump_start(after, shape)
    if start is None:
        return Jump(Surface(surface.points.copy(), np.zeros(shape, dtype=bool)), np.full(shape, np.nan), None,
                    after.reshape(shape))
    centres = sheet_centres(seen, depths)
    steps, laid = grow(centres, shape, start, scale.tolerance, scale.tolerance,
                       aim_at_start=float(after[start[0] * shape[1] + start[1]]))
    points = (q + np.nan_to_num(steps.ravel())[:, None] * nq).reshape(shape + (3,))
    return Jump(Surface(points, laid), steps, start, after.reshape(shape))
