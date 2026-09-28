"""E6: the loop certificate, chained without a hand — what replaces the human of the transfer.

A loop of consensus bands that stays under the half sheet at EVERY cut of its profile, cut at the reach
that sees (29 rows, `245`), certifies that its two paths did not change winding: the chunks it surrounds
are on the rectangle's winding, in the sense that no one-winding gap is seen there (`R4-F404`). The
procedure (`246` §1): the largest rectangle, then on each side the widest wing, cut at the reach that sees,
decided by a third line when it crosses, and the neighbouring portions queued again.

This module returns in addition what `246` did not publish: the per-chunk MASK (0 absent, 1 present not
certified, 2 certified), and it says, when it happens, that wings are counted around a rectangle that is
not itself judged.
"""
from __future__ import annotations

import numpy as np

from vesuve.lattice import geometry as geo
from vesuve.lattice import loop
from vesuve.transport import ABSENT

LIMIT_PER_SIDE = 64
REPRODUCTION_TOLERANCE = 0.5e-4 + 1e-6


# ── requests, and what serves them ───────────────────────────────────────────────────────────────

def request(direction: str, centre: int, start: int, end: int, k: int) -> dict:
    return {"key": f"{direction}_{int(centre)}_{int(start)}_{int(end)}_{int(k)}", "direction": direction,
            "centre": int(centre), "lines": geo.band_lines(int(centre), int(k)), "start": int(start), "end": int(end)}


def cost(d: dict) -> int:
    """In chunks: what a band asks to read."""
    return len(d["lines"]) * (int(d["end"]) - int(d["start"]) + 1)


def definition(x: dict) -> tuple:
    return (x["direction"], int(x["centre"]), tuple(int(l_) for l_ in x["lines"]), int(x["start"]), int(x["end"]))


class Readings:
    """The bands read, indexed by direction and centre. A request is served by bands of the same direction
    and centre, whose lines contain its own, and which together cover each of its seams; a band of nine
    lines therefore serves a request of seven."""

    def __init__(self, bands=()):
        self.index: dict = {}
        for x in bands:
            self.index.setdefault((x["direction"], int(x["centre"])), []).append(x)

    def serve(self, d: dict) -> list[dict] | None:
        lines = {int(x) for x in d["lines"]}
        candidates = sorted((x for x in self.index.get((d["direction"], int(d["centre"])), [])
                             if lines <= {int(l_) for l_ in x["lines"]}),
                            key=lambda x: (int(x["start"]), -int(x["end"])))
        taken, reached = [], int(d["start"])
        for x in candidates:
            if int(x["start"]) <= reached < int(x["end"]):
                taken.append(x)
                reached = int(x["end"])
            if reached >= int(d["end"]):
                return taken
        return taken if reached >= int(d["end"]) and taken else None


def served_steps(served: dict) -> dict:
    """`{(direction, centre): {line: {seam: step}}}`. A band served with no seam read keeps its key, empty:
    the analysis sees holes there, not a missing band."""
    steps: dict = {}
    for d, xs in served.values():
        key = (d["direction"], int(d["centre"]))
        steps.setdefault(key, {})
        for x in xs:
            for l_, s in (x.get("along") or {}).items():
                steps[key].setdefault(int(l_), {}).update({int(c): float(t[0]) for c, t in s.items()})
    return steps


def sides_of_a_loop(corners, k: int) -> list[dict]:
    r0, r1, c0, c1 = (int(x) for x in corners)
    return [request(geo.ROWS, r0, c0, c1, k), request(geo.ROWS, r1, c0, c1, k),
            request(geo.COLUMNS, c0, r0, r1, k), request(geo.COLUMNS, c1, r0, r1, k)]


def _serve(requests: list[dict], readings: Readings) -> tuple[dict, list[dict]]:
    served, missing = {}, []
    for d in requests:
        xs = readings.serve(d)
        if xs is None:
            missing.append(d)
        else:
            served[d["key"]] = (d, xs)
    return served, missing


# ── checking a fresh reading ─────────────────────────────────────────────────────────────────────

def domain(direction: str, lines, start: int, end: int) -> dict:
    """The seams a band reads, by family: `h` (row, left column), `v` (upper row, column)."""
    L = [int(x) for x in lines]
    if direction == geo.ROWS:
        return {"h": {(r, c) for r in L for c in range(int(start), int(end))},
                "v": {(r, c) for r in L[:-1] for c in range(int(start), int(end) + 1)}}
    return {"v": {(r, c) for c in L for r in range(int(start), int(end))},
            "h": {(r, c) for r in range(int(start), int(end) + 1) for c in L[:-1]}}


def band_steps(x: dict) -> dict:
    ll = {(int(a), int(b)): float(t[0]) for a, s in x["along"].items() for b, t in s.items()}
    tt = {(int(r), int(c)): float(t[0]) for r, s in x["across"].items() for c, t in s.items()}
    if x["direction"] == geo.ROWS:
        return {"h": ll, "v": tt}
    return {"v": {(r, c): p for (c, r), p in ll.items()}, "h": tt}


def source(x: dict) -> dict:
    return {"domain": domain(x["direction"], x["lines"], x["start"], x["end"]), "steps": band_steps(x)}


class ReadingRefused(Exception):
    """A fresh band does not fall back on what is published: two different readers, the measurement stops."""


def _check_one(n: str, N: dict, sources: dict, tolerance: float) -> int:
    seen = 0
    for s in sorted(sources):
        S = sources[s]
        for f in ("h", "v"):
            if f not in N["steps"] or f not in S["steps"]:
                continue
            for key in sorted(N["domain"][f] & S["domain"][f]):
                mine, theirs = key in N["steps"][f], key in S["steps"][f]
                if mine != theirs:
                    raise ReadingRefused(f"seam {f} {key} is read by {n} and not by {s}, or the other way round")
                if not mine:
                    continue
                e = abs(N["steps"][f][key] - S["steps"][f][key])
                if e > float(tolerance):
                    raise ReadingRefused(f"seam {f} {key} of {n} does not fall back on {s} (gap {e:.4g} voxel)")
                seen += 1
    return seen


def unchecked_bands(fresh: dict, sources: dict, tolerance: float = REPRODUCTION_TOLERANCE) -> set:
    """Chained reproduction: a fresh band is checked by a published source it crosses, or by a fresh band
    ALREADY checked. A band that crosses nothing stays unchecked (its loops are not judged); a disagreement
    raises `ReadingRefused`."""
    new = {c: source(x) for c, x in fresh.items()}
    remaining, checked, progress = sorted(new), [], True
    while remaining and progress:
        progress = False
        for b in list(remaining):
            src = {**sources, **{f"fresh {c}": new[c] for c in checked}}
            if _check_one(b, new[b], src, tolerance) == 0:
                continue
            remaining.remove(b)
            checked.append(b)
            progress = True
    return {definition(fresh[c]) for c in remaining}


def presence_holds(A: np.ndarray, fresh: dict) -> None:
    """Each line read counts as many absent chunks as the bucket's list; otherwise, refusal."""
    for c, b in fresh.items():
        for l_ in b["lines"]:
            x = (b.get("readings") or {}).get(str(l_))
            if x is None:
                raise ReadingRefused(f"line {l_} of {c} has no reading")
            read = int((x.get("refused") or {}).get(ABSENT, 0))
            if b["direction"] == geo.ROWS:
                listed = int((~A[int(l_), int(b["start"]):int(b["end"]) + 1]).sum())
            else:
                listed = int((~A[int(b["start"]):int(b["end"]) + 1, int(l_)]).sum())
            if read != listed:
                raise ReadingRefused(f"line {l_} of {c}: {read} absent chunks when read, {listed} in the list")


# ── judging a loop, deciding a wing ──────────────────────────────────────────────────────────────

def judge(corners, side: str, k: int, reach: int, table, readings: Readings, ctx: dict) -> dict:
    """A loop cut at the reach that sees, judged at its width: under, crosses, open, unseen, or to read."""
    def is_read(direction, y, start, end, k_):
        return readings.serve(request(direction, y, start, end, k_)) is not None
    cutting = geo.hand_free_cuts(corners, side, reach, k, table, is_read)
    direction, (start, end) = cutting["direction"], cutting["bounds"]
    requests = sides_of_a_loop(corners, k) + [request(direction, c, start, end, k) for c in cutting["cuts"][1:-1]]
    served, missing = _serve(requests, readings)
    base = {"corners": [int(x) for x in corners], "width": int(k), "cutting": cutting}
    if missing:
        return {**base, "state": "to read", "requests": missing, "cost": sum(cost(d) for d in missing)}
    nc = ctx.get("unchecked") or set()
    if any(definition(x) in nc for _d, xs in served.values() for x in xs):
        return {**base, "state": "unchecked"}
    steps = served_steps(served)
    arg = (ctx["longest"], ctx["seed"], ctx["draws"], k)
    whole = loop.analyse_up_to(steps, corners, *arg)
    by_sub_loop = [{"between": geo.between(side, sb), "corners": sb, **loop.analyse_up_to(steps, sb, *arg)}
                   for sb in geo.sub_loops(side, corners, cutting["cuts"])]
    refusal = loop.nesting(by_sub_loop, whole, side)
    if refusal is not None:
        return {**base, "state": "undecidable", "reason": refusal}
    vt = loop.verdict_of_the_slices(cutting, by_sub_loop, ctx["half"], k)
    x = whole["by_width"][str(k)]
    opened = (not x["closable"]) or bool(vt["open_sub_loops"])
    crosses = (not opened) and (bool(vt["crosses"]) or not x["under_half_sheet"])
    unseen = (not opened) and (not crosses) and bool(vt["gaps_beyond_reach"])
    state = "open" if opened else ("crosses" if crosses else ("unseen" if unseen else "under"))
    return {**base, "state": state, "closure": x.get("closure_voxels"),
            "profile": loop.profile(by_sub_loop, k), "peak": vt.get("peak")}


def tie_break(A: np.ndarray, corners, side: str, k: int, table, readings: Readings, ctx: dict) -> dict:
    """Which line of the wing drifts? The third line of `236`: among the wing, the narrow and the wide loop,
    the tightest does not use the faulty line, if each of the other two exceeds it by more than its noise."""
    tl = geo.third_line(A, corners, side, k, table)
    if tl is None:
        return {"state": "nothing decides", "third_line": None}
    direction, _d, _e, lo, hi = geo.wing_lines(side, corners)
    loops = geo.three_loops(tl, lo, hi)
    requests, seen = [], set()
    for co in loops.values():
        for d in sides_of_a_loop(co, k):
            if d["key"] not in seen:
                seen.add(d["key"])
                requests.append(d)
    served, missing = _serve(requests, readings)
    if missing:
        return {"state": "to read", "third_line": tl, "requests": missing, "cost": sum(cost(d) for d in missing)}
    nc = ctx.get("unchecked") or set()
    if any(definition(x) in nc for _d, xs in served.values() for x in xs):
        return {"state": "unchecked", "third_line": tl}
    steps = served_steps(served)
    by_loop = {name: {"corners": co, **loop.analyse_up_to(steps, co, ctx["longest"], ctx["seed"], ctx["draws"], k)}
               for name, co in loops.items()}
    refusal = loop.nesting_of_the_three(by_loop, direction, tl["nearest"])
    if refusal is not None:
        return {"state": "undecidable", "third_line": tl, "reason": refusal}
    verdict = verdict_of_the_three(tl, by_loop, k)
    return {"state": "decided" if verdict["drifting_line"] is not None else "not decided",
            "third_line": tl, "verdict": verdict}


def verdict_of_the_three(tl: dict, by_loop: dict, k: int) -> dict:
    """At the wing's width: the tightest of the three loops, and the line it does not use, if each of the
    other two exceeds it by more than the median of its own null."""
    xs = {n: by_loop[n]["by_width"][str(k)] for n in ("wing", "narrow", "wide")}
    opened = [n for n, x in xs.items() if not x["closable"]]
    verdict = {"width_judged": int(k), "open_loops": opened, "tightest": None, "decides": False, "drifting_line": None}
    if opened:
        return verdict
    L = {n: abs(float(x["closure_voxels"])) for n, x in xs.items()}
    tightest = min(("wing", "narrow", "wide"), key=lambda n: L[n])
    margins = {n: round(L[n] - L[tightest] - float(xs[n]["null"]["median_absolute_closure"]), 4)
               for n in L if n != tightest}
    decides = all(m >= 0 for m in margins.values())
    line = geo.left_out(tightest, tl)
    verdict.update({"tightest": tightest, "margins": margins, "decides": bool(decides),
                    "drifting_line": line if decides else None,
                    "is_a_wing_column": bool(decides) and line != int(tl["line"])})
    return verdict


# ── the procedure ────────────────────────────────────────────────────────────────────────────────

def unroll(A: np.ndarray, readings: Readings, ctx: dict) -> dict:
    """The whole procedure on what `readings` serves: the journal, the loops that hold, what is to read."""
    A = np.asarray(A, dtype=bool)
    scale = sorted(geo.WIDTHS, reverse=True)
    k1, reach = scale[0], int(ctx["reach"])
    tables = {k: geo.holding_table(A, k) for k in scale}
    rect = geo.largest_rectangle(A, k1)
    if rect is None:
        return {"rectangle": None, "journal": [], "holding_loops": [], "requests": []}
    journal, holding, requests = [], [], {}

    def _note(j):
        for d in j.get("requests") or []:
            requests.setdefault(d["key"], d)
    jr = judge(rect, "right", k1, reach, tables[k1], readings, ctx)
    _note(jr)
    journal.append({"loop": "the rectangle", **jr})
    if jr["state"] == "under":
        holding.append((list(rect), k1))
    for side in geo.SIDES:
        to_see, excluded, n = [geo.whole_side(rect, side)], [], 0
        while to_see and n < LIMIT_PER_SIDE:
            lo, hi = to_see.pop(0)
            n += 1
            found = None
            for k in scale:  # the widest width at which a wing holds
                co = geo.wing(A, geo.portion(rect, side, lo, hi), side, k, tables[k], excluded=excluded)
                if co:
                    found = (k, [int(x) for x in co])
                    break
            e = {"loop": "the wing", "side": side, "portion": [int(lo), int(hi)],
                 "excluded": [list(x) for x in excluded]}
            if found is None:
                journal.append({**e, "state": "no wing"})
                continue
            k, co = found
            j = judge(co, side, k, reach, tables[k], readings, ctx)
            _note(j)
            e.update(j)
            ya, yb = geo.between(side, co)
            neighbours = [(p, q) for p, q in ((lo, ya), (yb, hi)) if q > p]
            if j["state"] == "under":
                holding.append((co, k))
                to_see = neighbours + to_see
            elif j["state"] == "crosses":
                dp = tie_break(A, co, side, k, tables[k], readings, ctx)
                _note(dp)
                e["tie_break"] = dp
                x = geo.outer_line(side, co)
                line = (dp.get("verdict") or {}).get("drifting_line")
                if dp["state"] == "decided" and line == x and [x, k] not in [list(y) for y in excluded]:
                    excluded.append((x, k))  # the outer band drifts: the same portion is searched without it
                    to_see = [(lo, hi)] + to_see
                else:
                    to_see = neighbours + to_see
            else:
                to_see = neighbours + to_see
            journal.append(e)
    return {"rectangle": list(rect), "journal": journal,
            "holding_loops": [{"corners": co, "width": int(k)} for co, k in holding],
            "requests": sorted(requests.values(), key=lambda d: (cost(d), d["key"]))}


# ── the mask, and the verdict ────────────────────────────────────────────────────────────────────

ABSENT_FROM_MASK, PRESENT, CERTIFIED = 0, 1, 2


def mask(A: np.ndarray, loops) -> np.ndarray:
    """Per chunk: 0 absent from the bucket, 1 present but not certified, 2 surrounded by a loop that holds."""
    A = np.asarray(A, dtype=bool)
    M = np.zeros(A.shape, dtype=bool)
    for b in loops:
        M |= geo.surrounded(A.shape, b["corners"], b["width"])
    out = np.where(A, PRESENT, ABSENT_FROM_MASK).astype(np.uint8)
    out[A & M] = CERTIFIED
    return out


def certify(A: np.ndarray, published: list[dict], ctx: dict, fresh: dict | None = None,
            sources: dict | None = None) -> dict:
    """The procedure on what is published and read. `ctx`: longest, seed, draws, half, reach.

    Fresh bands are first checked against presence and against what is published; a band that does not
    fall back raises `ReadingRefused`, a band that crosses nothing stays unchecked.
    """
    A = np.asarray(A, dtype=bool)
    fresh = dict(fresh or {})
    ctx = dict(ctx)
    if fresh:
        presence_holds(A, fresh)
        src = dict(sources or {})
        for i, x in enumerate(published):
            src[f"published {i}"] = source(x)
        ctx["unchecked"] = unchecked_bands(fresh, src)
    r = unroll(A, Readings(list(published) + list(fresh.values())), ctx)
    rect_judged = bool(r["journal"]) and r["journal"][0]["state"] == "under"
    wings = [b for b in r["holding_loops"] if b["corners"] != r["rectangle"]]
    return {**r, "left_to_read": sum(cost(d) for d in r["requests"]),
            "coverage": geo.loop_coverage(A, [(b["corners"], b["width"]) for b in r["holding_loops"]]),
            "mask": mask(A, r["holding_loops"]),
            "wings_around_an_unjudged_rectangle": (not rect_judged) and bool(wings)}
