"""The criterion that needs no referent: how many sheets of `m7` a jump crosses, point by point (`R4-F531`), and the
zero threshold that holds it (`R4-F538`).

Along the normal of each point laid on the surface a jump gives, `m7` is read three steps and a quarter on each side.
The count is the number of runs of sheet passed between the one that carries the point and the one that carries the
surface the jump leaves: one if they follow each other, zero if it is the same run, two if a run lies between them. A
jump crosses one sheet only if at least 50 of its points are counted and at least three quarters of those cross
one; it is held if, besides, fewer than 50 of its counted points cross none.

Ported from `les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.py` (slice `345`),
`le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.py` (`352`) and
`sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.py` (`355`) on the `experimental` branch.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np

from vesuve.chain.surface import ReadValues, Surface, to_prediction_indices
from vesuve.transfer.surfaces import normals

TOLERANCE_IN_STEPS = 0.25    # a run further than this from an end does not carry it
REACH_IN_STEPS = 3.25        # how far each side of the point `m7` is read
ONE_SHEET_SHARE = 0.75
MINIMUM_COUNTED = 50
ZERO_LIMIT = 50              # a jump with this many points that cross no sheet is not held
MAXIMUM_POINTS = 1200        # the points laid that the count takes, evenly spaced on the grid
LATERAL_PHERCPARIS4 = 10.0   # voxels of level 2: a point with no surface this close in front of it is not counted


@dataclass(frozen=True)
class Counts:
    """What the count read, point by point, for the points it took."""
    points: np.ndarray        # (n, 3) the points laid taken, in (x, y, z)
    normals: np.ndarray       # (n, 3)
    gaps: np.ndarray          # (n,) signed distance along the normal to the departure surface, NaN if none in front
    in_front: np.ndarray      # (n,) the departure surface is in front of the point and within reach
    counts: list              # (n,) the sheets crossed, None where the point is not counted
    cells: np.ndarray         # (n,) index of each point's cell in the arrival grid, flattened


def sheets_between(seen: np.ndarray, depths: np.ndarray, gap: float, tolerance: float) -> int | None:
    """The runs passed along a ray, from the one that carries depth 0 to the one that carries `gap`: 1 if they follow each
    other, 0 if it is the same; None if either end has no run within `tolerance`."""
    if not seen.any():
        return None
    edges = np.flatnonzero(np.diff(np.concatenate([[0], seen.astype(np.int8), [0]])))
    runs = [(depths[a], depths[b - 1]) for a, b in zip(edges[::2], edges[1::2])]

    def which(x: float) -> int | None:
        distances = [0.0 if lo <= x <= hi else min(abs(lo - x), abs(hi - x)) for lo, hi in runs]
        k = int(np.argmin(distances))
        return k if distances[k] <= tolerance else None

    first, second = which(0.0), which(gap)
    return None if first is None or second is None else abs(second - first)


def gaps_to(cloud: np.ndarray, points: np.ndarray, point_normals: np.ndarray, lateral: float) -> np.ndarray:
    """The signed gap along the normal of each of `points` to the nearest point of `cloud`; NaN for a point with no cloud point
    within `lateral` voxels sideways."""
    from scipy.spatial import cKDTree

    if not len(points) or not len(cloud):
        return np.full(len(points), np.nan)
    _, nearest = cKDTree(cloud).query(points)
    delta = cloud[nearest] - points
    along = np.einsum("ij,ij->i", delta, point_normals)
    sideways = np.linalg.norm(delta - along[:, None] * point_normals, axis=-1)
    return np.where(sideways <= lateral, along, np.nan)


def count_sheets(departure: Surface, arrival: Surface | None, read_values: ReadValues, step: float,
                 lateral: float = LATERAL_PHERCPARIS4) -> Counts | None:
    """The points laid of `arrival` that the count takes, at most `MAXIMUM_POINTS`, with their normals; for each, its gap to
    `departure` along its normal if it is in front, and the sheets of `m7` it passes, None if it is not counted. None if
    either surface has no point laid, or none has a normal."""
    if arrival is None or not arrival.valid.any() or not departure.valid.any():
        return None
    arrival_normals, has_normal = normals(arrival.points, arrival.valid)
    laid = arrival.valid & has_normal
    points, point_normals, cells = arrival.points[laid], arrival_normals[laid], np.flatnonzero(laid)
    if not len(points):
        return None
    if len(points) > MAXIMUM_POINTS:
        k = np.linspace(0, len(points) - 1, MAXIMUM_POINTS).round().astype(int)
        points, point_normals, cells = points[k], point_normals[k], cells[k]
    gaps = gaps_to(departure.points[departure.valid], points, point_normals, lateral)
    tolerance = TOLERANCE_IN_STEPS * step
    half = float(np.ceil(REACH_IN_STEPS * step))
    depths = np.arange(-half, half + 1.0)
    in_front = np.isfinite(gaps) & (np.abs(gaps) + tolerance <= half)
    counts: list = [None] * len(points)
    if in_front.any():
        along = points[in_front][:, None, :] + depths[None, :, None] * point_normals[in_front][:, None, :]
        seen = read_values(to_prediction_indices(along)) > 0
        for i, ray, gap in zip(np.flatnonzero(in_front), seen, gaps[in_front]):
            counts[i] = sheets_between(ray, depths, float(gap), tolerance)
    return Counts(points, point_normals, gaps, in_front, counts, cells)


def summarise(counts: Counts | None) -> dict:
    """What a count publishes: the points taken, those in front, those counted, how many cross 0, 1, 2 sheets or more, and the
    share that cross one."""
    if counts is None:
        return {"points": 0, "in_front": 0, "counted": 0, "counts": {}, "one_sheet_share": None}
    counted = [c for c in counts.counts if c is not None]
    tally = Counter(counted)
    return {"points": int(len(counts.points)), "in_front": int(counts.in_front.sum()), "counted": len(counted),
            "counts": {str(k): v for k, v in sorted(tally.items())},
            "one_sheet_share": round(tally[1] / len(counted), 4) if counted else None}


def crosses_one_sheet(summary: dict, share: float = ONE_SHEET_SHARE) -> bool:
    """A jump crosses one sheet only if enough of its points are counted and at least `share` of them cross one."""
    return bool(summary["counted"] >= MINIMUM_COUNTED and summary["one_sheet_share"] is not None
                and summary["one_sheet_share"] >= share)


def holds(summary: dict) -> bool:
    """The criterion: the jump crosses one sheet, and fewer than `ZERO_LIMIT` of its counted points cross none."""
    return bool(crosses_one_sheet(summary) and summary["counts"].get("0", 0) < ZERO_LIMIT)


def count_and_summarise(departure: Surface, arrival: Surface | None, read_values: ReadValues, step: float,
                        lateral: float = LATERAL_PHERCPARIS4) -> dict:
    """The summary of the count of `arrival` against `departure`."""
    return summarise(count_sheets(departure, arrival, read_values, step, lateral))
