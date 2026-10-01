"""Judging a surface of the chain against the published windings, strictly (`R4-F551`: 27 of the 28 judged jumps).

A surface is read against each published winding of the segment: it finds one if at least half of the vertices that face it
sit within a quarter step of it, with a median gap within a quarter step. A jump is right if the surface it leaves finds
exactly one winding, and the surface it gives finds exactly the next one on its side. The published windings are the
referent: nothing of this is available on a scroll with no trace, which is why it only judges; it takes no part in a
decision of the chain.

Ported from `la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.py` (slice `329`),
`la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4.py` (`321`, `la_coincidence`),
`jugee_strictement_jusquou_la_chaine_bornee_descend_elle.py` (`340`) and
`le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.py` (`344`, `la_justesse`) on the `experimental` branch.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from vesuve.chain.criterion import gaps_to
from vesuve.transfer.surfaces import normals

STEP_AT_FULL_RESOLUTION = 173.0 / 2.4       # voxels of 2.4 µm
QUARTER_STEP = STEP_AT_FULL_RESOLUTION / 4.0
LATERAL = 40.0                               # voxels: a vertex with no surface this close in front of it does not face it
MINIMUM_FACING = 5
MARGIN = 100.0                               # voxels: the published winding is read inside the surface's box, widened
JUDGED_TURNS = tuple(range(0, -7, -1))      # 5753_0 to 5753_-6; 5753_-7 is shifted (`R4-F522`)
SIDE = {"plus": 1, "moins": -1}
FOUND, NOT_FOUND, NOT_READ = "found", "not found", "not read"
RIGHT, NOT_JUDGED = "right", "not judged"
WRONG_TWO_TURNS, WRONG_ANOTHER_TURN, WRONG_MISSED_TURN = "wrong: two turns", "wrong: another turn", "wrong: the turn missed"


@dataclass(frozen=True)
class PublishedTurn:
    """A published winding of the segment: its vertices with a normal, and their normals."""
    points: np.ndarray
    normals: np.ndarray


def read_turn(folder: Path) -> PublishedTurn:
    """The vertices and normals of a published winding stored as a tifxyz (the 2.4 µm mesh)."""
    import tifffile

    folder = Path(folder)
    x, y, z = (tifffile.imread(folder / f"{c}.tif").astype(np.float64) for c in "xyz")
    points = np.stack([x, y, z], axis=-1)
    valid = np.isfinite(points).all(axis=-1) & (x != -1.0) & (y != -1.0) & (z != -1.0)
    n, has_normal = normals(points, valid)
    laid = valid & has_normal
    return PublishedTurn(points[laid], n[laid])


def nearby_vertices(turn: PublishedTurn, points: np.ndarray, margin: float = MARGIN) -> tuple[np.ndarray, np.ndarray]:
    """The vertices of the winding, with their normals, inside the bounding box of `points` widened by `margin`."""
    if not len(points):
        return np.zeros((0, 3)), np.zeros((0, 3))
    low, high = points.min(axis=0) - margin, points.max(axis=0) + margin
    inside = ((turn.points >= low) & (turn.points <= high)).all(axis=1)
    return turn.points[inside], turn.normals[inside]


def coincidence(gaps: np.ndarray) -> dict:
    """What the gaps say of a surface that should sit on a winding: found if it is within a quarter step of it."""
    gaps = gaps[np.isfinite(gaps)]
    if len(gaps) < MINIMUM_FACING:
        return {"facing": int(len(gaps)), "reading": NOT_READ}
    median = float(np.median(gaps))
    part = float((np.abs(gaps) <= QUARTER_STEP).mean())
    found = abs(median) <= QUARTER_STEP and part >= 0.5
    return {"facing": int(len(gaps)), "median_gap": round(median, 2), "share_within_a_quarter_step": round(part, 4),
            "reading": FOUND if found else NOT_FOUND}


def read_against(points: np.ndarray, turns: dict[int, PublishedTurn]) -> dict[int, str]:
    """For each published winding, whether the surface (points in voxels of the 2.4 µm volume) finds it."""
    out = {}
    for rank, turn in turns.items():
        vertices, vertex_normals = nearby_vertices(turn, points)
        out[rank] = coincidence(gaps_to(points, vertices, vertex_normals, LATERAL))["reading"]
    return out


def found_turns(readings: dict) -> list[int]:
    """The windings a surface finds, from the first (0) down."""
    return sorted((int(t) for t, reading in readings.items() if reading == FOUND), reverse=True)


def justness(before: dict, after: dict, sense: int) -> str:
    """What the strict reading says of a jump from the surface `before` to `after`, each read as {turn: reading}, on `sense`
    (+1 or -1): right if `after` finds exactly the turn expected, wrong if it finds two turns, another turn, or misses the
    turn; not judged if `before` does not find exactly one turn, or the expected one is outside the judged windings."""
    first = found_turns(before)
    if len(first) != 1:
        return NOT_JUDGED
    expected = first[0] + sense
    if expected not in JUDGED_TURNS:
        return NOT_JUDGED
    second = found_turns(after)
    if second == [expected]:
        return RIGHT
    if expected in second:
        return WRONG_TWO_TURNS
    if second:
        return WRONG_ANOTHER_TURN
    return WRONG_MISSED_TURN if {int(t): r for t, r in after.items()}.get(expected) == NOT_FOUND else NOT_JUDGED


def judge_jumps(readings: list[dict], side: str) -> list[str]:
    """The justness of each jump of a side, from the readings of the starting surface and of each surface kept, in order."""
    return [justness(before, after, SIDE[side]) for before, after in zip(readings, readings[1:])]


def tally(judgements: list[str]) -> dict:
    """The jumps judged, the right ones, and their share."""
    judged = [j for j in judgements if j != NOT_JUDGED]
    right = sum(j == RIGHT for j in judged)
    return {"judged": len(judged), "right": right, "share": round(right / len(judged), 4) if judged else None}
