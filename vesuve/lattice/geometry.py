"""The geometry of the certificate: which bands hold, where to put the loops, where to cut them.

Everything here derives from the presence grid `A` alone (true where the chunk exists in the bucket)
and reads no step. That is what makes the procedure hand-free: the rectangle, the wings, the third
line and the cuts are functions of presence, never of a result that was read (`246` §1).

Port of `src/nappe/` on the `experimental` branch: `ou_sarrete_le_segment.py` (holding, rectangle),
`le_segment_au_dela_du_rectangle_se_relie_t_il.py` (wings, coverage), `laquelle_des_deux_colonnes_derive.py`
(third line), `ou_laile_de_droite_se_separe.py` and `le_rectangle_entre_ses_coupes.py` (cuts).
"""
from __future__ import annotations

import bisect

import numpy as np

WIDTHS = (3, 5, 7, 9)  # the scale of `218`
SIDES = ("top", "right", "bottom", "left")
ROWS, COLUMNS = "rows", "columns"


def band_lines(centre: int, k: int) -> list[int]:
    """The `k` contiguous lines of a band centred on `centre`."""
    start = int(centre) - int(k) // 2
    return list(range(start, start + int(k)))


# ── what holds ───────────────────────────────────────────────────────────────────────────────────

def holding_bands(A: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """`on_row[r, s]`: the band of rows centred on r has its k lines present on both sides of the
    horizontal seam s; `on_column[s, c]` likewise for the vertical seam s."""
    A = np.asarray(A, dtype=bool)
    gy, gx = A.shape
    h = int(k) // 2
    H = (A[:, :-1] & A[:, 1:]).astype(int)
    V = (A[:-1, :] & A[1:, :]).astype(int)
    on_row = np.zeros((gy, gx - 1), dtype=bool)
    ch = np.vstack([np.zeros((1, gx - 1), dtype=int), np.cumsum(H, axis=0)])
    for r in range(h, gy - h):
        on_row[r] = (ch[r + h + 1] - ch[r - h]) >= int(k)
    on_column = np.zeros((gy - 1, gx), dtype=bool)
    cv = np.hstack([np.zeros((gy - 1, 1), dtype=int), np.cumsum(V, axis=1)])
    for c in range(h, gx - h):
        on_column[:, c] = (cv[:, c + h + 1] - cv[:, c - h]) >= int(k)
    return on_row, on_column


def holding_table(A: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """The seams where a band does not hold, cumulated, to answer `holds` in constant time."""
    on_row, on_column = holding_bands(A, k)
    PR = np.hstack([np.zeros((on_row.shape[0], 1), dtype=int), np.cumsum(~on_row, axis=1)])
    PC = np.vstack([np.zeros((1, on_column.shape[1]), dtype=int), np.cumsum(~on_column, axis=0)])
    return PR, PC


def holds(table, direction: str, centre: int, start: int, end: int) -> bool:
    """Does the band `(direction, centre)` hold at every seam of `[start, end)`?"""
    PR, PC = table
    if int(end) <= int(start):
        return False
    if direction == ROWS:
        return int(PR[int(centre), int(end)] - PR[int(centre), int(start)]) == 0
    return int(PC[int(end), int(centre)] - PC[int(start), int(centre)]) == 0


def largest_rectangle(A: np.ndarray, k: int) -> list[int] | None:
    """`[r0, r1, c0, c1]` whose four bands of k lines hold, by longest path `(r1 - r0) + (c1 - c0)`,
    then largest area, then smallest r0, then smallest c0."""
    A = np.asarray(A, dtype=bool)
    gy, gx = A.shape
    h = int(k) // 2
    on_row, on_column = holding_bands(A, k)
    bad = np.vstack([np.zeros((1, gx), dtype=int), np.cumsum(~on_column, axis=0)])
    centres = np.zeros(gx, dtype=bool)
    centres[h:gx - h] = True
    best, best_key = None, None
    rows = [r for r in range(h, gy - h) if on_row[r].any()]
    for i, r0 in enumerate(rows):
        for r1 in reversed(rows[i + 1:]):
            if best_key is not None and (r1 - r0) + (gx - 1) < best_key[0]:
                break
            both = on_row[r0] & on_row[r1]
            if not both.any():
                continue
            valid = np.flatnonzero(((bad[r1] - bad[r0]) == 0) & centres)
            if len(valid) < 2:
                continue
            broken = np.concatenate(([0], np.cumsum(~both)))
            group = broken[valid]
            cut = np.flatnonzero(np.diff(group)) + 1
            starts = np.concatenate(([0], cut))
            ends = np.concatenate((cut, [len(valid)])) - 1
            spans = valid[ends] - valid[starts]
            j = int(np.argmax(spans))
            if spans[j] <= 0:
                continue
            c0, c1 = int(valid[starts[j]]), int(valid[ends[j]])
            key = ((r1 - r0) + (c1 - c0), (r1 - r0) * (c1 - c0), -r0, -c0)
            if best_key is None or key > best_key:
                best, best_key = [int(r0), int(r1), c0, c1], key
    return best


# ── the wings ────────────────────────────────────────────────────────────────────────────────────

def _wing_corners(side: str, corners, start: int, end: int, outside: int) -> list[int]:
    r0, r1, c0, c1 = (int(x) for x in corners)
    return {"right": [start, end, c1, outside], "left": [start, end, outside, c0],
            "top": [outside, r0, start, end], "bottom": [r1, outside, start, end]}[side]


def wing(A: np.ndarray, corners, side: str, k: int, table, excluded=()) -> list[int] | None:
    """The largest wing on one side of a portion: largest area, then longest path, then smallest start,
    then the nearest outer band; or none.

    The outer band is at least k lines from the inner one, and shares no line with an excluded band
    `(centre, width)`.
    """
    gy, gx = np.asarray(A).shape
    h = int(k) // 2
    r0, r1, c0, c1 = (int(x) for x in corners)
    if side in ("right", "left"):
        inside, lo, hi = (c1 if side == "right" else c0), r0, r1
        outside_range = range(c1 + k, gx - h) if side == "right" else range(h, c0 - k + 1)
        across, outer = ROWS, COLUMNS
    else:
        inside, lo, hi = (r0 if side == "top" else r1), c0, c1
        outside_range = range(h, r0 - k + 1) if side == "top" else range(r1 + k, gy - h)
        across, outer = COLUMNS, ROWS
    best, best_key = None, None
    for x in outside_range:
        if any(abs(int(x) - int(c_)) < (int(k) + int(K)) // 2
               for c_, K in ((e if isinstance(e, (list, tuple)) else (e, k)) for e in excluded)):
            continue
        a_, b_ = min(inside, x), max(inside, x)
        ys = [y for y in range(lo, hi + 1) if holds(table, across, y, a_, b_)]
        for ya in ys:
            j0 = bisect.bisect_left(ys, ya + int(k))
            if j0 >= len(ys) or not holds(table, outer, x, ya, ys[j0]):
                continue
            g, d = j0, len(ys) - 1
            while g < d:  # the farthest the outer band still holds: it holds by prefixes
                m = (g + d + 1) // 2
                if holds(table, outer, x, ya, ys[m]):
                    g = m
                else:
                    d = m - 1
            yb, span = ys[g], b_ - a_
            key = ((yb - ya) * span, (yb - ya) + span, -ya, -span)
            if best_key is None or key > best_key:
                best, best_key = (ya, yb, x), key
    if best is None:
        return None
    ya, yb, x = best
    return _wing_corners(side, corners, ya, yb, x)


def portion(rect, side: str, lo: int, hi: int) -> list[int]:
    r0, r1, c0, c1 = (int(x) for x in rect)
    return [int(lo), int(hi), c0, c1] if side in ("right", "left") else [r0, r1, int(lo), int(hi)]


def whole_side(rect, side: str) -> tuple[int, int]:
    r0, r1, c0, c1 = (int(x) for x in rect)
    return (r0, r1) if side in ("right", "left") else (c0, c1)


def outer_line(side: str, corners) -> int:
    r0, r1, c0, c1 = (int(x) for x in corners)
    return {"right": c1, "left": c0, "top": r0, "bottom": r1}[side]


# ── the third line (`236`) ───────────────────────────────────────────────────────────────────────

def wing_lines(side: str, corners) -> tuple[str, int, int, int, int]:
    """`(direction, inner, outer, lo, hi)` of the two long sides of a wing."""
    a0, a1, b0, b1 = (int(x) for x in corners)
    return {"right": (COLUMNS, b0, b1, a0, a1), "left": (COLUMNS, b1, b0, a0, a1),
            "top": (ROWS, a1, a0, b0, b1), "bottom": (ROWS, a0, a1, b0, b1)}[side]


def corners_between(direction: str, p: int, q: int, lo: int, hi: int) -> list[int]:
    return [int(lo), int(hi), int(p), int(q)] if direction == COLUMNS else [int(p), int(q), int(lo), int(hi)]


def third_line(A: np.ndarray, corners, side: str, k: int, table) -> dict | None:
    """The nearest line parallel to a long side (on a tie, on the rectangle's side), that holds along the
    whole length of the wing with its two end bands."""
    A = np.asarray(A, dtype=bool)
    k, h = int(k), int(k) // 2
    direction, inside, outside, lo, hi = wing_lines(side, corners)
    across = ROWS if direction == COLUMNS else COLUMNS
    bound = A.shape[1] if direction == COLUMNS else A.shape[0]
    low, high = min(inside, outside), max(inside, outside)
    best, best_key = None, None
    for c in list(range(h, low - k + 1)) + list(range(high + k, bound - h)):
        nearest = low if c < low else high
        a_, b_ = min(c, nearest), max(c, nearest)
        if not (holds(table, direction, c, lo, hi) and holds(table, across, lo, a_, b_)
                and holds(table, across, hi, a_, b_)):
            continue
        key = (abs(c - nearest), 0 if nearest == inside else 1)
        if best_key is None or key < best_key:
            best, best_key = {"line": int(c), "direction": direction, "nearest": int(nearest),
                              "farthest": int(outside if nearest == inside else inside),
                              "on_rectangle_side": nearest == inside, "gap": int(abs(c - nearest))}, key
    return best


def three_loops(tl: dict, lo: int, hi: int) -> dict:
    """The wing, the narrow one (third line and nearest side), the wide one (up to the farthest)."""
    direction, c, p, f = tl["direction"], int(tl["line"]), int(tl["nearest"]), int(tl["farthest"])
    return {"wing": corners_between(direction, min(p, f), max(p, f), lo, hi),
            "narrow": corners_between(direction, min(c, p), max(c, p), lo, hi),
            "wide": corners_between(direction, min(c, f), max(c, f), lo, hi)}


def left_out(name: str, tl: dict) -> int:
    """The line one of the three loops does not use."""
    return {"wing": int(tl["line"]), "narrow": int(tl["farthest"]), "wide": int(tl["nearest"])}[name]


# ── the cuts (`235`, `238`, `245`) ───────────────────────────────────────────────────────────────

def across_the_wing(side: str, corners) -> tuple[str, int, int, int, int]:
    """`(direction, lo, hi, start, end)`: the cuts are `direction` bands centred from lo to hi, spanning start to end."""
    a0, a1, b0, b1 = (int(x) for x in corners)
    if side in ("right", "left"):
        return ROWS, a0, a1, b0, b1
    return COLUMNS, b0, b1, a0, a1


def sub_loops(side: str, corners, cuts) -> list[list[int]]:
    a0, a1, b0, b1 = (int(x) for x in corners)
    if side in ("right", "left"):
        return [[int(cuts[j]), int(cuts[j + 1]), b0, b1] for j in range(len(cuts) - 1)]
    return [[a0, a1, int(cuts[j]), int(cuts[j + 1])] for j in range(len(cuts) - 1)]


def between(side: str, sb) -> list[int]:
    """The two cuts that bound a sub-loop, along the wing."""
    return [int(x) for x in (sb[:2] if side in ("right", "left") else sb[2:])]


def splitting_lines(cuts, reach: int) -> list[int]:
    """Each interval between two cuts, split into the fewest equal parts that do not exceed the reach."""
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        n = -(-(int(b) - int(a)) // int(reach))
        out += [int(a) + (i * (int(b) - int(a))) // n for i in range(1, n)]
    return out


def gaps_beyond(cuts, reach: int) -> list[list[int]]:
    return [[int(a), int(b)] for a, b in zip(cuts[:-1], cuts[1:]) if int(b) - int(a) > int(reach)]


def hand_free_cuts(corners, side: str, reach: int, k: int, table, read) -> dict:
    """The cuts already read first, at least k lines from the previous one and from the end; then each gap
    beyond the reach, split into the fewest equal parts that do not exceed it, where the band holds."""
    k = int(k)
    direction, lo, hi, start, end = across_the_wing(side, corners)
    kept = [int(lo)]
    for y in range(int(lo) + 1, int(hi)):
        if y - kept[-1] >= k and int(hi) - y >= k and holds(table, direction, y, start, end) \
                and read(direction, y, start, end, k):
            kept.append(y)
    already = kept[1:]
    kept.append(int(hi))
    cuts = [int(lo)]
    for a_, b_ in zip(kept[:-1], kept[1:]):
        for y in splitting_lines([a_, b_], reach):
            if y - cuts[-1] >= k and b_ - y >= k and holds(table, direction, y, start, end):
                cuts.append(int(y))
        cuts.append(int(b_))
    return {"direction": direction, "bounds": [int(start), int(end)], "cuts": cuts, "cuts_already_read": already,
            "sub_loops": len(cuts) - 1,
            "largest_gap": max(b - a_ for a_, b in zip(cuts[:-1], cuts[1:])),
            "gaps_beyond_reach": gaps_beyond(cuts, reach)}


# ── the coverage ─────────────────────────────────────────────────────────────────────────────────

def surrounded(shape, corners, k: int) -> np.ndarray:
    """The chunks a loop surrounds, its bands included."""
    gy, gx = (int(x) for x in shape)
    h = int(k) // 2
    r0, r1, c0, c1 = (int(x) for x in corners)
    M = np.zeros((gy, gx), dtype=bool)
    M[max(0, r0 - h):min(gy, r1 + h + 1), max(0, c0 - h):min(gx, c1 + h + 1)] = True
    return M


def loop_coverage(A: np.ndarray, loops) -> dict:
    """The share of the footprint the loops surround, each at its width."""
    A = np.asarray(A, dtype=bool)
    M = np.zeros(A.shape, dtype=bool)
    for co, k in loops:
        M |= surrounded(A.shape, co, k)
    n, total = int((A & M).sum()), int(A.sum())
    return {"count": n, "of": total, "share": round(n / total, 4) if total else 0.0}
