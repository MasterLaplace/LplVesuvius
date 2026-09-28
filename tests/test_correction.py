"""The hand-free correction of the transfer: the published numbers, block by block, and where it does not hold.

`275` ran the procedure of `265` on the 340 candidate blocks of segment `20230702185753` and published 163 misses made
right for 41 rights made misses; `281` ran it on the band `w028-037` and published 15 for 25. The port replays both
from the embedded inputs alone, writes the corrected transfer the research wrote byte for byte, and each rule it
depends on is checked against the research function that applied it.
"""
from __future__ import annotations

import hashlib
import io
import json

import numpy as np
import pytest

from conftest import MEASURES, research
from vesuve import embedded
from vesuve.research import to_english
from vesuve.transfer import correction as c

SEGMENT, BAND = "20230702185753", "20260623142658-w028-037"
PUBLISHED = {SEGMENT: "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json",
             BAND: "la_procedure_sans_juge_tient_elle_sur_la_bande.json"}
# The blocks `275` §3 lists, where the net gain is at least 3 either way: a broken rule shows on them.
SHOWN = [(16, 256), (64, 160), (320, 176), (320, 192), (240, 240), (336, 128), (48, 160), (176, 208), (240, 224),
         (16, 192), (160, 160)]


def _replay(name: str) -> dict:
    k = embedded.correction(name)
    return {**c.correct_segment(k["transfer"], k["judges"], k["tables"], k["candidates"],
                                k["context"]["slip_voxels"], k["surfaces"]), "inputs": k}


def _digest(a: np.ndarray) -> str:
    buf = io.BytesIO()
    np.save(buf, a, allow_pickle=False)
    return hashlib.sha256(buf.getvalue()).hexdigest()


@pytest.fixture(scope="module")
def segment():
    return _replay(SEGMENT)


@pytest.fixture(scope="module")
def band():
    return _replay(BAND)


def test_the_segment_replays_what_275_published(segment):
    p = segment["pooled"]
    assert (p["blocks"], p["corrected_points"], p["misses_made_right"], p["rights_made_misses"], p["net_gain"]) == \
        (340, 495, 163, 41, 122)
    assert (p["before"], p["after"], p["scored_points"]) == (0.9339, 0.9374, 34917)
    assert (p["blocks_up"], p["blocks_down"], p["blocks_unchanged"]) == (42, 11, 287)
    assert segment["whole_segment"]["before"]["share_on_the_right_winding"] == 0.9303
    assert segment["whole_segment"]["after"]["share_on_the_right_winding"] == 0.9334
    assert f"{segment['sign_test']['on_points']:.3g}" == "2.04e-18"   # `290`, `R4-F471`
    assert f"{segment['sign_test']['on_blocks']:.3g}" == "2.25e-05"


def test_the_corrected_transfer_is_the_one_the_research_wrote(segment, band):
    """The digest of what `275` and `281` saved travels with the embedded inputs: this runs without the research."""
    for got in (segment, band):
        assert _digest(got["tau1"]) == got["inputs"]["context"]["provenance"]["corrected_transfer"]


def test_on_the_segment_every_correction_is_within_the_validated_geometry(segment):
    """339 blocks have neighbours along both axes; the 340th, (368, 240), corrects nothing, so what is delivered is
    exactly what the research wrote."""
    outside = [(b["row"], b["column"]) for b in segment["blocks"] if not b["validated_geometry"]]
    assert outside == [(368, 240)]
    assert np.array_equal(segment["claimed"], segment["tau1"], equal_nan=True)


def test_on_the_band_the_procedure_does_not_hold_and_nothing_is_claimed(band):
    p = band["pooled"]
    assert (p["blocks"], p["corrected_points"], p["misses_made_right"], p["rights_made_misses"]) == (84, 61, 15, 25)
    assert band["sign_test"]["on_points"] > 0.05 and band["sign_test"]["on_blocks"] > 0.05
    assert not any(b["validated_geometry"] for b in band["blocks"])  # one row of blocks: east-west only
    assert not np.array_equal(band["tau1"], band["inputs"]["transfer"], equal_nan=True)  # the research did correct
    assert np.array_equal(band["claimed"], band["inputs"]["transfer"], equal_nan=True)   # the program does not


def test_the_judge_never_decides(band):
    """The judges only score: replaced by noise, they change the counts and not one corrected point."""
    k = band["inputs"]
    rng = np.random.default_rng(1)
    noise = [j + rng.normal(0, 50, j.shape) for j in k["judges"]]
    other = c.correct_segment(k["transfer"], noise, k["tables"], k["candidates"], k["context"]["slip_voxels"],
                              k["surfaces"])
    assert np.array_equal(other["tau1"], band["tau1"], equal_nan=True)
    assert other["pooled"]["misses_made_right"] != band["pooled"]["misses_made_right"]


def _shown_blocks() -> list[dict]:
    k = embedded.correction(SEGMENT)
    err = c.judged_error(k["transfer"], k["judges"])
    return [c.correct_block(by, bx, k["candidates"], k["tables"], k["transfer"], err, k["context"]["slip_voxels"],
                            k["surfaces"])[0] for by, bx in SHOWN]


def _counts(blocks):
    return [(b["corrected_points"], b["misses_made_right"], b["rights_made_misses"]) for b in blocks]


def test_a_block_that_anchors_on_itself_is_caught(monkeypatch):
    """The anchor leaves the block out, so its own slip cannot pull it; putting the block back changes the counts."""
    honest = _counts(_shown_blocks())
    monkeypatch.setattr(c, "neighbourhood_anchor",
                        lambda diff, y0, x0, by, bx, side=c.BLOCK: float(np.nanmedian(diff)))
    assert _counts(_shown_blocks()) != honest


def test_a_fixed_threshold_instead_of_the_mixture_is_caught(monkeypatch):
    """`261` corrected every point beyond half a sheet; `264` weighs slipped against right. They do not agree."""
    honest = _counts(_shown_blocks())
    monkeypatch.setattr(c, "decide", lambda gap, mixture: np.isfinite(gap) & (np.abs(np.nan_to_num(gap)) >= c.HALF_SHEET))
    assert _counts(_shown_blocks()) != honest


@research
@pytest.mark.parametrize("name", [SEGMENT, BAND])
def test_every_block_replays_its_published_decision(name, segment, band):
    got = {SEGMENT: segment, BAND: band}[name]
    published = to_english(json.loads((MEASURES / PUBLISHED[name]).read_text()))
    assert len(published["blocks"]) == len(got["blocks"])
    keys = ("row", "column", "decidable", "neighbours", "anchor_voxels", "before", "after", *c.COUNTS)
    for a, b in zip(got["blocks"], published["blocks"]):
        assert {k: a.get(k) for k in keys} == {k: b.get(k) for k in keys}, f"block ({a['row']}, {a['column']}) differs"
    assert {k: got["pooled"][k] for k in ("blocks", "before", "after", *c.COUNTS, "net_gain")} == \
        {k: published["pooled"][k] for k in ("blocks", "before", "after", *c.COUNTS, "net_gain")}


# ── Each rule against the research function that applied it, on inputs the publications never saw ───────────────

@research
def test_the_mixture_and_the_decision_are_the_research_s():
    from la_marche_sait_elle_ou_ne_pas_corriger import la_decision, le_melange
    rng = np.random.default_rng(20260928)
    for trial in range(40):
        x = rng.normal(0, rng.uniform(2, 20), (16, 16))
        slipped = rng.random((16, 16)) < rng.uniform(0, 0.3)
        x[slipped] += rng.choice([-69.458, 69.458], slipped.sum())
        x[rng.random((16, 16)) < 0.05] = np.nan
        ours, theirs = c.slip_mixture(x, 69.458), le_melange(x, 69.458)
        assert ours["_w"] == theirs["_w"] and ours["_s"] == theirs["_s"]
        gap = rng.normal(0, 40, (30, 30))
        assert np.array_equal(c.decide(gap, ours), la_decision(gap, theirs))


@research
def test_the_walk_and_the_anchor_are_the_research_s():
    from la_spire_produite_se_lit_elle_dans_le_treillis import la_marche_du_bloc
    from le_voisinage_dit_il_quel_niveau_est_le_bon import lancre_du_voisinage
    rng = np.random.default_rng(7)
    for trial in range(10):
        side, by, bx = 12, 32, 48
        h = {r: {c_: rng.normal(0, 5) for c_ in range(bx, bx + side) if rng.random() > 0.1} for r in range(by, by + side)}
        v = {r: {c_: rng.normal(0, 5) for c_ in range(bx, bx + side) if rng.random() > 0.1} for r in range(by, by + side)}
        ours = c.block_depth(h, v, by, bx, side)
        theirs = la_marche_du_bloc({r: {k: (x, 0.0, 16) for k, x in s.items()} for r, s in h.items()},
                                   {r: {k: (x, 0.0, 16) for k, x in s.items()} for r, s in v.items()}, by, bx, side)
        assert np.array_equal(ours["depth"], theirs["la_profondeur"], equal_nan=True)
        assert ours["seams"] == theirs["les_coutures"]
        diff = rng.normal(0, 10, (48, 48))
        diff[rng.random((48, 48)) < 0.2] = np.nan
        assert c.neighbourhood_anchor(diff, 0, 0, 16, 16) == lancre_du_voisinage(diff, 0, 0, 16, 16)


@research
def test_the_mesh_points_the_judge_and_the_sign_test_are_the_research_s():
    from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points
    from la_spire_produite_se_lit_elle_dans_le_treillis import lerreur_jugee
    from les_gains_publies_se_distinguent_ils_du_hasard import le_test_du_signe
    rng = np.random.default_rng(3)
    for by, bx in ((0, 0), (16, 32), (48, 160)):
        m = rng.normal(0, 10, (16, 16))
        m[rng.random((16, 16)) < 0.1] = np.nan
        ours, theirs = c.to_mesh_points(m, by, bx, (80, 160)), la_carte_aux_points(m, by, bx, (80, 160))
        assert np.array_equal(ours[0], theirs[0], equal_nan=True) and np.array_equal(ours[1], theirs[1])
    tau = rng.normal(0, 40, (60, 60))
    judges = [tau + rng.normal(0, 30, tau.shape) for _ in range(2)]
    judges[1][rng.random(tau.shape) < 0.1] = np.nan
    assert np.array_equal(c.judged_error(tau, judges), lerreur_jugee(tau, judges), equal_nan=True)
    for a, b in ((163, 41), (15, 25), (0, 0), (7, 4), (84, 33)):
        assert c.sign_test(a, b) == le_test_du_signe(a, b)
