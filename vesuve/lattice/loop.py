"""The arithmetic of a loop: the consensus of its sides, its closure, its null, its profile.

A loop with corners `(r0, r1, c0, c1)` has four sides, each a band. Along a side, the CONSENSUS step at
each seam is the median of the lines present, if there is a majority of them (`k // 2 + 1`). A majority
hole of at most 17 seams is crossed at zero step (the "mesh" rule of `225`); longer, the loop is open at
that width. The closure is

    L = H(r0; c0 → c1) + V(c1; r0 → r1) − H(r1; c0 → c1) − V(c0; r0 → r1)

and the loop is under the half sheet when |L| < 36 voxels (`R4-F393`). Port of `src/nappe/` on the
`experimental` branch: `le_consensus_traverse_t_il_la_rangee.py`, `quest_ce_qui_franchit_le_trou_de_majorite.py`,
`deux_chemins_*.py`, `une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py`,
`une_aile_plus_etroite_tient_elle.py`, `ou_laile_de_droite_se_separe.py`, `sous_laile_qui_evite_la_colonne.py`.
"""
from __future__ import annotations

import numpy as np

from vesuve import core
from vesuve.lattice.geometry import COLUMNS, ROWS, WIDTHS, band_lines

HALF_SHEET = 36.0
ROUNDING = 5e-5  # a closure is published to four decimals
# ⚠ The order in which the four sides seed the null. The research sorted its French side names (bas, droite,
# gauche, haut), and each side's seed is offset by its rank: sorting the English names instead would swap left
# and right, and every published null would move.
NULL_ORDER = ("bottom", "right", "left", "top")


def majority(k: int) -> int:
    return int(k) // 2 + 1


def loop_sides(corners) -> list[tuple]:
    """`(direction, centre, start, end, sign, name)`: the path by the row first minus the one by the column."""
    r0, r1, c0, c1 = corners
    return [(ROWS, r0, c0, c1, +1, "top"), (COLUMNS, c1, r0, r1, +1, "right"),
            (ROWS, r1, c0, c1, -1, "bottom"), (COLUMNS, c0, r0, r1, -1, "left")]


def consensus(steps: dict, minimum: int) -> dict:
    """The median step at each seam where at least `minimum` lines were read, and nothing else."""
    seams = sorted(set().union(*[set(x) for x in steps.values()]))
    out = {}
    for c in seams:
        v = [steps[r][c] for r in steps if c in steps[r]]
        if len(v) >= int(minimum):
            out[int(c)] = float(np.median(v))
    return out


def holes(cons: dict, start: int, end: int) -> list[list[int]]:
    """The runs of seams without a consensus in `[start, end)`: `[start, length]`."""
    out, first = [], None
    for s in range(int(start), int(end)):
        if s not in cons:
            if first is None:
                first = s
        elif first is not None:
            out.append([first, s - first])
            first = None
    if first is not None:
        out.append([first, int(end) - first])
    return out


def at_width(steps: dict, centre: int, k: int) -> dict:
    """The centred lines of width k, and those alone."""
    keep = set(band_lines(centre, k))
    return {l_: s for l_, s in steps.items() if l_ in keep}


def bridged_consensus(steps_k: dict, k: int, start: int, end: int) -> tuple[dict, list]:
    """The consensus at one width, its holes crossed at zero step ("the mesh")."""
    cons = consensus(steps_k, majority(k))
    found = holes(cons, start, end)
    for first, n in found:
        cons = {**cons, **{int(s): 0.0 for s in range(int(first), int(first) + int(n))}}
    return cons, found


def block_sums(steps, draws: int, seed: int) -> np.ndarray:
    """The null: the sum of a walk made of the side's CENTRED steps, drawn by blocks of ⌈n^(1/3)⌉.

    ⚠ In numpy and not in the core: this null reproduces bit for bit only in numpy's summation order,
    and the seed it consumes is declared by the measurement.
    """
    a = np.asarray(steps, dtype=float)
    a = a - float(np.mean(a))
    n = len(a)
    b = max(1, min(core.block_length(max(1, n)), n))
    k = -(-n // b)
    lengths = np.full(k, b)
    lengths[-1] = n - b * (k - 1)
    starts = np.random.default_rng(int(seed)).integers(0, n - b + 1, size=(int(draws), k))
    cs = np.concatenate(([0.0], np.cumsum(a)))
    return (cs[starts + lengths] - cs[starts]).sum(axis=1)


def at_one_width(steps_by_band: dict, corners, k: int, seed: int, draws: int, half: float = HALF_SHEET) -> dict:
    """At one width: the closure, its spread, and the null of its four sides drawn by blocks."""
    side_steps, sides, L = {}, [], 0.0
    for direction, centre, start, end, sign, name in loop_sides(corners):
        cons, _h = bridged_consensus(at_width(steps_by_band[(direction, centre)], centre, k), k, start, end)
        s = float(sum(float(cons[x]) for x in range(int(start), int(end))))
        L += sign * s
        side_steps[name] = (sign, [float(cons[x]) for x in range(int(start), int(end))])
        sides.append({"side": name, "sum_voxels": round(s, 4)})
    centred = [np.asarray(p, dtype=float) - float(np.mean(p)) for _s, p in side_steps.values()]
    spread = float(np.sqrt(sum(float(np.dot(c, c)) for c in centred) / sum(len(c) for c in centred)))
    null = sum(side_steps[name][0] * block_sums(side_steps[name][1], draws, int(seed) + 101 * i)
               for i, name in enumerate(NULL_ORDER))
    an = np.abs(np.asarray(null, dtype=float))
    return {"width": int(k), "closure_voxels": round(float(L), 4),
            "under_half_sheet": bool(abs(L) < float(half)), "sides": sides,
            "step_spread_voxels": round(spread, 4),
            "null": {"median_absolute_closure": round(float(np.median(an)), 4),
                     "share_under_half_sheet": round(float(np.mean(an < float(half))), 4),
                     "share_under_closure": round(float(np.mean(an <= abs(L))), 4)}}


def at_one_width_of_the_segment(steps_by_band: dict, corners, k: int, longest: int, seed: int, draws: int) -> dict:
    """At one width: open if a hole exceeds what `225` crossed, otherwise closed and judged."""
    found = []
    for direction, centre, start, end, _sign, name in loop_sides(corners):
        cons = consensus(at_width(steps_by_band[(direction, centre)], centre, k), majority(k))
        found += [{"side": name, "start": int(d), "length": int(n)} for d, n in holes(cons, start, end)]
    too_long = [t for t in found if t["length"] > int(longest)]
    if too_long:
        return {"closable": False, "width": int(k), "holes": found, "holes_too_long": too_long}
    return {**at_one_width(steps_by_band, corners, k, seed, draws), "closable": True, "holes": found}


def analyse_up_to(steps: dict, corners, longest: int, seed: int, draws: int, k: int) -> dict:
    """The instrument at each width of the scale up to k: beyond, the bands do not have the lines."""
    return {"width_judged": int(k),
            "by_width": {str(w): at_one_width_of_the_segment(steps, corners, w, longest, seed, draws)
                         for w in WIDTHS if w <= int(k)}}


# ── nesting and profile ──────────────────────────────────────────────────────────────────────────

def long_sides(side: str) -> tuple[str, str]:
    return ("left", "right") if side in ("right", "left") else ("top", "bottom")


def nesting(by_sub_loop: list[dict], whole: dict, side: str) -> str | None:
    """Where neither the loop nor its sub-loops have a hole on their long sides, the sub-loops sum to the
    loop, up to rounding. Returns the reason for a refusal, or None."""
    longs = long_sides(side)

    def _holed(x):
        return any(t["side"] in longs for t in x["holes"])
    for k in sorted(whole["by_width"], key=int):
        xa, xs = whole["by_width"][k], [sb["by_width"][k] for sb in by_sub_loop]
        if not xa["closable"] or _holed(xa) or any(not x["closable"] or _holed(x) for x in xs):
            continue
        s = float(sum(float(x["closure_voxels"]) for x in xs))
        if abs(s - float(xa["closure_voxels"])) > ROUNDING * (len(xs) + 1) + 1e-9:
            return (f"at {k} lines, the sub-loops sum to {round(s, 4)} voxels and the loop closes at "
                    f"{xa['closure_voxels']}: the nesting does not hold")
    return None


def profile(by_sub_loop: list[dict], k: int) -> list[dict]:
    """The cumulative closure, cut after cut, as long as no sub-loop is open."""
    cum, out = 0.0, []
    for sb in by_sub_loop:
        x = sb["by_width"][str(k)]
        if not x["closable"]:
            return out
        cum += float(x["closure_voxels"])
        out.append({"cut": int(sb["between"][1]), "cumulative_voxels": round(cum, 4)})
    return out


def verdict_of_the_slices(cutting: dict, by_sub_loop: list[dict], half: float, k: int) -> dict:
    """Open, or does it cross the half sheet at a cut, and where is its peak."""
    opened = [sb["between"] for sb in by_sub_loop if not sb["by_width"][str(k)]["closable"]]
    base = {"gaps_beyond_reach": [list(x) for x in cutting["gaps_beyond_reach"]]}
    if opened:
        return {**base, "open_sub_loops": opened, "crosses": False, "peak": None}
    prof = profile(by_sub_loop, k)
    crossing = [p for p in prof if abs(float(p["cumulative_voxels"])) >= float(half)]
    return {**base, "open_sub_loops": [], "crosses": bool(crossing),
            "peak": max(prof, key=lambda p: abs(float(p["cumulative_voxels"])))}


# ── the three loops (`236`) ──────────────────────────────────────────────────────────────────────

def ends(direction: str) -> tuple[str, str]:
    return ("top", "bottom") if direction == COLUMNS else ("left", "right")


def nesting_of_the_three(by_loop: dict, direction: str, junction: int) -> str | None:
    """Where no hole touches the junction on an end, the wide loop is the sum of the other two."""
    loop_ends = ends(direction)

    def _touches(t):
        return t["side"] in loop_ends and int(t["start"]) <= int(junction) <= int(t["start"]) + int(t["length"])
    for k in sorted(by_loop["wing"]["by_width"], key=int):
        xs = {n: by_loop[n]["by_width"][k] for n in ("wing", "narrow", "wide")}
        if any(not x["closable"] or any(_touches(t) for t in x["holes"]) for x in xs.values()):
            continue
        s = float(xs["wing"]["closure_voxels"]) + float(xs["narrow"]["closure_voxels"])
        if abs(s - float(xs["wide"]["closure_voxels"])) > 3 * ROUNDING + 1e-9:
            return (f"at {k} lines, the wing and the narrow loop sum to {round(s, 4)} voxels and the wide one "
                    f"closes at {xs['wide']['closure_voxels']}: the nesting does not hold")
    return None
