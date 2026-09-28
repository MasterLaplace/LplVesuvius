"""The ported procedure against the research's, on footprints MADE to exercise every rule.

The replay on the real segment does not exercise every rule: no tie between two wings, no hole in a judged loop,
deciding margins far from zero. A probe that broke one of them stayed green. Here each scenario makes a presence
(full for the ties, holed for the edges), a winding field (smooth, plus a column that DRIFTS below a row to make
loops cross and be decided), and chunks refused at random to make majority holes. Both procedures replay the same
reading rounds, and must return the same journal at every round. The research reads and writes French bands; the
port reads the same bands through `vesuve.research`.
"""
from __future__ import annotations

import copy

import numpy as np
import pytest

from conftest import research
from vesuve.lattice import certificate as cert
from vesuve.research import to_english

pytestmark = research

CONTEXT = {"longest": 17, "seed": 20261105, "draws": 49, "half": 36.0, "reach": 29}
RESEARCH_CONTEXT = {"plus_long": 17, "graine": 20261105, "tirages": 49, "demi": 36.0, "portee": 29,
                    "regle": "le_maillage"}


def _scenario(seed: int):
    rng = np.random.default_rng(seed)
    gy, gx = int(rng.integers(70, 110)), int(rng.integers(60, 90))
    A = np.ones((gy, gx), dtype=bool)
    if seed % 3:  # torn edges and holes, otherwise a full presence that makes ties
        A[: int(rng.integers(0, 6)), :] = False
        A[:, gx - int(rng.integers(0, 6)):] = False
        for _ in range(int(rng.integers(1, 6))):
            r, c = int(rng.integers(0, gy)), int(rng.integers(0, gx))
            A[r:r + int(rng.integers(1, 8)), c:c + int(rng.integers(1, 8))] = False
    # The winding field: a gentle slope, and a column that drifts below a row.
    r_ = np.arange(gy)[:, None]
    c_ = np.arange(gx)[None, :]
    w = 0.05 * r_ + 0.03 * c_ + rng.normal(0, 0.2, size=(gy, gx))
    # Like column 260 of the segment: a whole region of columns whose vertical step drifts below a row, enough for
    # the cumulative closure of a loop along it to cross the half sheet.
    drift = {"column": int(rng.integers(gx // 2, gx - 12)), "row": int(rng.integers(10, gy // 2)),
             "per_seam": float(rng.choice([0.0, 0.35, 0.7]))}
    refused = rng.random((gy, gx)) < rng.uniform(0.0, 0.12)
    return A, w, drift, refused, rng


def _reader(A, w, drift, refused, rng):
    """A band read on the made field, in the research's French layout: the true step plus a noise of each line."""
    def step_v(r, c):
        x = w[r + 1, c] - w[r, c]
        if abs(c - drift["column"]) <= 4 and r >= drift["row"]:
            x += drift["per_seam"]
        return x

    def read(d):
        lines, start, end = d["les_lignes"], int(d["de"]), int(d["a"])
        along = {}
        for l_ in lines:
            direction = 0 if d["le_sens"] == "rangees" else 1  # an integer: the hash of a string changes per process
            noise = np.random.default_rng([direction, l_, start, end]).normal(0, 1.2, size=end - start + 1)
            s = {}
            for i, x in enumerate(range(start, end)):
                (p, q) = ((l_, x), (l_, x + 1)) if d["le_sens"] == "rangees" else ((x, l_), (x + 1, l_))
                if not (A[p] and A[q]) or refused[p] or refused[q]:
                    continue
                v = (w[l_, x + 1] - w[l_, x]) if d["le_sens"] == "rangees" else step_v(x, l_)
                s[str(x)] = [round(round((v + noise[i]) * 16) / 16, 4), 0.0, 16]
            along[str(l_)] = s
        return {"le_sens": d["le_sens"], "le_centre": d["le_centre"], "les_lignes": list(lines), "de": start, "a": end,
                "le_long": along, "en_travers": {}, "les_lectures": {}}
    return read


def _without_prose(journal):
    """The verdict sentence the research recites, and the refusal reasons, are prose in two languages: the rest is
    compared."""
    j = copy.deepcopy(journal)
    for e in j:
        e.pop("reason", None)
        tb = e.get("tie_break") or {}
        tb.pop("reason", None)
        v = tb.get("verdict")
        if v:
            v.pop("ce_qui_reste_a_mesurer", None)
    return j


@pytest.mark.parametrize("seed", range(12))
def test_both_procedures_return_the_same_journal_at_every_round(seed):
    import la_couverture_sans_main as ref
    A, w, drift, refused, rng = _scenario(seed)
    read = _reader(A, w, drift, refused, rng)
    bands, rounds = [], 0
    for rounds in range(1, 7):
        a = to_english(ref.derouler(A, ref.Lectures(bands), RESEARCH_CONTEXT))
        b = cert.unroll(A, cert.Readings(to_english(bands)), CONTEXT)
        assert b["rectangle"] == a["rectangle"]
        assert _without_prose(b["journal"]) == _without_prose(a["journal"]), f"round {rounds}"
        assert b["holding_loops"] == a["holding_loops"]
        assert b["requests"] == a["requests"]
        if not a["requests"]:
            break
        research_requests = ref.derouler(A, ref.Lectures(bands), RESEARCH_CONTEXT)["les_demandes"]
        bands = bands + [read(d) for d in research_requests]
    assert a["rectangle"] is not None  # a scenario without a rectangle would exercise nothing


def test_the_scenarios_exercise_the_rules_the_segment_does_not():
    """Without this check, a corpus of trivial scenarios would leave the probes green."""
    import la_couverture_sans_main as ref
    states, tie_breaks, holes = set(), 0, 0
    for seed in range(12):
        A, w, drift, refused, rng = _scenario(seed)
        read = _reader(A, w, drift, refused, rng)
        bands = []
        for _ in range(6):
            a = to_english(ref.derouler(A, ref.Lectures(bands), RESEARCH_CONTEXT))
            states |= {e["state"] for e in a["journal"]}
            tie_breaks += sum(1 for e in a["journal"] if e.get("tie_break"))
            if not a["requests"]:
                break
            bands = bands + [read(d) for d in ref.derouler(A, ref.Lectures(bands), RESEARCH_CONTEXT)["les_demandes"]]
        holes += int(refused.sum())
    assert {"under", "crosses"} <= states, states
    assert tie_breaks >= 1 and holes > 0
