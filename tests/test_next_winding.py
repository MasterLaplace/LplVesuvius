"""The transfer to the next winding, computed here from what the prediction sees along each normal.

`247` counted the sheets of the prediction `m7` along each point's normal, took the first one after the segment's own,
and let the neighbours vote; `248` chained that jump on the band `w028-037`. The research saved the transfers that rule
produced, and the correction of 0.2.0 replayed them. Here the rule runs on the embedded samples of the prediction and
gives those transfers back to within a millionth of a voxel; each rule it depends on is checked against the research
function that applied it, and a broken rule (a fixed step, no vote) loses the right winding as `247` published.
"""
from __future__ import annotations

import numpy as np
import pytest

from conftest import network, research
from vesuve import embedded
from vesuve.transfer import correction
from vesuve.transfer import next_winding as nw

SEGMENT, BAND = "20230702185753", "20260623142658-w028-037"


@pytest.fixture(scope="module")
def produced():
    return {name: nw.produce(embedded.rays(name)) for name in (SEGMENT, BAND)}


@pytest.mark.parametrize("name", [SEGMENT, BAND])
def test_the_transfer_is_the_one_the_research_saved(produced, name):
    """Point for point: the same NaN where there is no point, and the same depth elsewhere within a millionth of a
    voxel. The band's was saved as a dot product of the moved point with the normal, hence its rounding."""
    got, kept = produced[name]["transfer"], embedded.correction(name)["transfer"]
    assert got.shape == kept.shape
    assert np.array_equal(np.isnan(got), np.isnan(kept))
    assert np.isfinite(kept).sum() > 30000
    assert np.nanmax(np.abs(got - kept)) < 1e-6


def test_the_vote_ran_the_rounds_247_published(produced):
    assert produced[SEGMENT]["rounds"] == 8   # `247`, `les_changements_par_tour_de_la_suivante`, m7, side plus


def test_the_rule_lands_on_the_right_winding_as_247_published(produced):
    """Judged by the segment's own next layer, as `247` judged it (`R4-F412`): 0.9214 for the next sheet and the vote,
    0.9119 for the next sheet alone, 0.7613 for a fixed step that reads nothing."""
    r, judge = embedded.rays(SEGMENT), embedded.correction(SEGMENT)["judges"][0]
    on_grid = nw.grid_of(r)
    alone = nw.next_sheet(r.depths, r.seen)
    fixed = np.full(r.seen.shape[0], r.side * r.step)
    shares = [nw.share_on_the_right_winding(x, judge, r.half_sheet) for x in
              (produced[SEGMENT]["transfer"], on_grid(alone), on_grid(fixed))]
    assert shares == [0.9214, 0.9119, 0.7613]


def test_a_broken_rule_loses_the_right_winding(produced):
    """The first sheet seen instead of the one after the segment's own, or the vote on a fixed step, is not the rule."""
    r, judge = embedded.rays(SEGMENT), embedded.correction(SEGMENT)["judges"][0]
    on_grid = nw.grid_of(r)
    first = np.array([c[0] if len(c) else np.nan for c in nw.sheet_centres(r.depths, r.seen)])
    fixed_start = nw.vote(nw.sheet_centres(r.depths, r.seen), np.full(len(first), r.side * r.step), r)[0]
    right = nw.share_on_the_right_winding(produced[SEGMENT]["transfer"], judge, r.half_sheet)
    for broken in (first, fixed_start):
        assert nw.share_on_the_right_winding(on_grid(broken), judge, r.half_sheet) < right - 0.005


def test_the_produced_transfer_replays_the_correction(produced):
    """The correction of 0.2.0 run on the transfer computed here gives back what `275` published: 163 for 41."""
    k = embedded.correction(SEGMENT)
    got = correction.correct_segment(produced[SEGMENT]["transfer"], k["judges"], k["tables"], k["candidates"],
                                     k["context"]["slip_voxels"], k["surfaces"])
    p = got["pooled"]
    assert (p["blocks"], p["misses_made_right"], p["rights_made_misses"], p["net_gain"]) == (340, 163, 41, 122)


def test_without_a_next_sheet_a_ray_starts_from_the_step(produced):
    r = embedded.rays(SEGMENT)
    alone = nw.next_sheet(r.depths, r.seen)
    assert produced[SEGMENT]["without_next_sheet"] == int(np.isnan(alone).sum()) > 0
    assert produced[SEGMENT]["points"] == r.seen.shape[0]


def test_the_runs_of_a_ray():
    t = np.arange(0.0, 10.0)
    seen = np.array([[1, 1, 0, 0, 1, 1, 1, 0, 0, 1]], dtype=bool)
    assert [list(c) for c in nw.sheet_centres(t, seen)] == [[0.5, 5.0, 9.0]]
    assert list(nw.next_sheet(t, seen, own=1.0)) == [5.0]                      # the own sheet touches |t| <= own
    assert list(nw.next_sheet(t, seen, own=0.0)) == [5.0]
    nothing = np.zeros((1, 10), dtype=bool)
    assert np.isnan(nw.next_sheet(t, nothing)).all() and nw.sheet_centres(t, nothing)[0].size == 0
    late = np.array([[0, 0, 0, 1, 1, 0, 0, 0, 1, 0]], dtype=bool)
    assert list(nw.next_sheet(t, late, own=1.0)) == [3.5]                      # no own sheet: the first beyond it


def test_the_consensus_needs_a_majority():
    g = np.full((3, 3), np.nan)
    g[0, :] = 1.0
    g[1, :2] = 2.0
    assert nw.consensus(g)[1, 1] == 1.0          # five of nine seen: median of 1, 1, 1, 2, 2
    g[1, 1] = np.nan
    assert np.isnan(nw.consensus(g)[1, 1])       # four of nine: no majority


@research
def test_each_rule_is_the_research_s(produced):
    """On the embedded samples of the band: the next sheet, the consensus and the vote, function against function."""
    from le_transfert_retrouve_t_il_la_spire_voisine import la_feuille_suivante as research_next_sheet
    from le_transfert_retrouve_t_il_la_spire_voisine import le_consensus as research_consensus
    from le_transfert_retrouve_t_il_la_spire_voisine import le_vote_itere as research_vote
    from le_transfert_retrouve_t_il_la_spire_voisine import les_centres as research_centres
    r = embedded.rays(BAND)
    ours = nw.next_sheet(r.depths, r.seen)
    theirs = research_next_sheet(r.depths, r.seen)
    assert np.array_equal(np.isnan(ours), np.isnan(theirs)) and np.allclose(ours, theirs, equal_nan=True)
    rng = np.random.default_rng(247)
    g = np.where(rng.random((40, 60)) < 0.3, np.nan, rng.normal(70.0, 20.0, (40, 60)))
    assert np.array_equal(nw.consensus(g), research_consensus(g), equal_nan=True)
    on_grid = nw.grid_of(r)
    start = np.where(np.isfinite(ours), ours, r.side * r.step)
    theirs_vote, theirs_changes = research_vote(research_centres(r.depths, r.seen), start, on_grid, r.rows, r.columns)
    ours_vote, ours_changes = nw.vote(nw.sheet_centres(r.depths, r.seen), start, r)
    assert np.array_equal(ours_vote, theirs_vote) and ours_changes == theirs_changes


@network
def test_the_samples_read_from_the_bucket_are_the_embedded_ones(tmp_path):
    """The rays rebuilt from the published mesh sit where the embedded ones sit, and the public prediction read along
    them gives back the embedded samples."""
    from vesuve.remote import Remote
    from vesuve.transfer import surfaces
    from vesuve.transport import Transport
    r, k = embedded.rays(SEGMENT), embedded.correction(SEGMENT)
    transport = Transport()
    try:
        mesh = Remote(tmp_path, transport).tifxyz_folder(k["context"]["render"]["mesh"])
        points, valid, _ = surfaces.read_points(mesh)
        p, n, gi, gj, shape = nw.rays_of_mesh(points, valid)
        assert np.array_equal(gi, r.rows) and np.array_equal(gj, r.columns) and shape == r.grid
        some = slice(0, 300)
        assert np.array_equal(nw.read_samples(nw.prediction(transport, r), p[some], n[some], r), r.seen[some])
    finally:
        transport.close()
