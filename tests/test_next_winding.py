"""The transfer to the next winding, computed here from what the prediction sees along each normal.

`247` counted the sheets of the prediction `m7` along each point's normal, took the first one after the segment's own,
and let the neighbours vote; `248` chained that jump on the band `w028-037`. The research saved the transfers that rule
produced, and the correction of 0.2.0 replayed them. Here the rule runs on the embedded samples of the prediction and
gives those transfers back to within a millionth of a voxel; each rule it depends on is checked against the research
function that applied it, and a broken rule (a fixed step, no vote) loses the right winding as `247` published.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from conftest import network, research
from vesuve import embedded
from vesuve.transfer import correction
from vesuve.transfer import next_winding as nw
from vesuve.transport import InMemoryTransport

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


def _grand_prize_offline(tmp_path, monkeypatch, **options) -> dict:
    from vesuve.grand_prize.pipeline import run
    monkeypatch.setattr("vesuve.grand_prize.pipeline.Transport", lambda **_: InMemoryTransport({}))
    run(output=tmp_path, cache=tmp_path / "cache", ink=False, surface=False, **options)
    return {s["id"]: s for s in json.loads((tmp_path / "report.json").read_text())["stages"]}


def test_the_grand_prize_computes_the_transfer_then_corrects_it(tmp_path, monkeypatch):
    stages = _grand_prize_offline(tmp_path, monkeypatch)
    n, t = stages["TN"], stages["T"]
    assert n["state"] == "done" and n["outputs"]["same_as_the_research_transfer"] is True
    assert n["outputs"]["share_on_the_right_winding"]["next_sheet_then_vote"] == 0.9214
    assert n["outputs"]["share_on_the_right_winding"]["fixed_step"] == 0.7613
    assert [q["id"] for q in n["equations"]] == ["NW1", "NW2", "NW3"]
    assert t["outputs"]["whose_transfer"] == "computed here in stage TN" and t["outputs"]["net_gain"] == 122
    assert n["outputs"]["control_band_same_as_the_research_transfer"] is True
    assert n["outputs"]["own_sheet_seen_within_12_voxels"] == {"rays": 41791, "share": 0.6653}


def test_a_transfer_the_embedded_tables_do_not_describe_is_not_corrected_with_them(tmp_path, monkeypatch):
    """The embedded step tables were rendered from the research's transfer: a transfer computed differently (here, the
    fixed step) cannot be corrected with them. Stage N says it differs, and stage T corrects the transfer the tables
    describe, saying so, until --render makes tables for the other one."""
    real = nw.produce

    def fixed_step(rays):
        got = real(rays)
        return {**got, "transfer": nw.grid_of(rays)(np.full(rays.seen.shape[0], rays.side * rays.step))}
    monkeypatch.setattr("vesuve.grand_prize.pipeline.nw.produce", fixed_step)
    stages = _grand_prize_offline(tmp_path, monkeypatch)
    assert stages["TN"]["state"] == "partial" and "differs from the research's" in stages["TN"]["reason"]
    t = stages["T"]["outputs"]
    assert t["whose_transfer"].startswith("the research's") and "--render" in t["whose_transfer"]
    assert t["net_gain"] == 122
    band = t["control_band"]["pooled"]
    assert (band["misses_made_right"], band["rights_made_misses"]) == (15, 25)   # `281`, on the research's transfer
    assert stages["TN"]["outputs"]["control_band_same_as_the_research_transfer"] is False


def test_without_the_network_reading_the_prediction_is_partial_and_the_correction_says_whose_transfer(tmp_path,
                                                                                                      monkeypatch):
    stages = _grand_prize_offline(tmp_path, monkeypatch, read_prediction=True)
    assert stages["TN"]["state"] == "partial" and "could not be computed here" in stages["TN"]["reason"]
    assert stages["T"]["outputs"]["whose_transfer"] == "the research's, embedded"


def _fabricated_prediction(volume: np.ndarray, chunk: tuple, absent=(), unreadable=()):
    """An uncompressed zarr level 0 in memory: every chunk but those `absent` or `unreadable` (bytes of the wrong
    size), at the declared separator. The edge chunks are padded with ones, so a sample read past the volume's
    shape would show."""
    import json as _json

    from vesuve.remote_zarr import RemoteArray
    url = "https://example.invalid/prediction.zarr"
    bodies = {f"{url}/0/.zarray": _json.dumps({"shape": list(volume.shape), "chunks": list(chunk), "dtype": "|u1",
                                               "compressor": None, "fill_value": 0, "order": "C",
                                               "dimension_separator": "/"}).encode()}
    grid = [-(-n // c) for n, c in zip(volume.shape, chunk)]
    cz, cy, cx = chunk
    for i in range(grid[0]):
        for j in range(grid[1]):
            for k in range(grid[2]):
                if (i, j, k) in absent:
                    continue
                block = np.ones(chunk, dtype=np.uint8)
                part = volume[i * cz:(i + 1) * cz, j * cy:(j + 1) * cy, k * cx:(k + 1) * cx]
                block[:part.shape[0], :part.shape[1], :part.shape[2]] = part
                bodies[f"{url}/0/{i}/{j}/{k}"] = b"\x00" if (i, j, k) in unreadable else block.tobytes()
    return RemoteArray(url, InMemoryTransport(bodies), 0)


def _rays_for(points, normals, samples: int, factor: int = 1):
    return nw.Rays(depths=nw.depths(1.0, samples - 1), seen=np.zeros((len(points), samples), dtype=bool),
                   rows=np.zeros(len(points), dtype=np.intp), columns=np.arange(len(points)), grid=(1, len(points)),
                   side=1.0, step=4.0, half_sheet=2.0, prediction="fabricated", path="", level=0, factor=factor)


def test_the_prediction_is_read_along_each_normal_in_zyx_across_chunks():
    """Each sample is the voxel floor((x + t n) / f) in (z, y, x) order, whichever chunk holds it; outside the volume
    and in an absent chunk the prediction marks nothing."""
    rng = np.random.default_rng(6)
    volume = (rng.random((12, 10, 9)) < 0.3).astype(np.uint8)
    points = np.array([[0.5, 1.5, 0.5], [2.5, 0.5, 1.5], [8.5, 9.5, 11.5], [1.5, 2.5, 3.5]])   # (x, y, z)
    normals_ = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.6, 0.8]])
    chunk = (4, 3, 5)
    for factor in (1, 2):
        rays = _rays_for(points * factor, normals_, samples=9 * factor, factor=factor)
        got = nw.read_samples(_fabricated_prediction(volume, chunk), points * factor, normals_, rays, threads=2)
        idx = np.floor((points[:, None, :] * factor + rays.depths[None, :, None] * normals_[:, None, :])
                       / factor).astype(int)[..., ::-1]
        inside = np.all((idx >= 0) & (idx < np.array(volume.shape)), axis=-1)
        expected = np.zeros(inside.shape, dtype=bool)
        expected[inside] = volume[idx[inside][:, 0], idx[inside][:, 1], idx[inside][:, 2]] > 0
        assert got.dtype == bool and np.array_equal(got, expected), factor
        assert expected.any() and (~inside).any() and len({tuple(k) for k in idx[inside] // chunk}) > 3
    rays = _rays_for(points, normals_, samples=9)
    idx = np.floor(points[:, None, :] + rays.depths[None, :, None] * normals_[:, None, :]).astype(int)[..., ::-1]
    hole = nw.read_samples(_fabricated_prediction(volume, chunk, absent={(0, 0, 0)}), points[:1], normals_[:1],
                           _rays_for(points[:1], normals_[:1], 9))
    in_first = np.all(idx[0] // chunk == 0, axis=-1)
    full = nw.read_samples(_fabricated_prediction(volume, chunk), points[:1], normals_[:1], _rays_for(points[:1],
                                                                                                   normals_[:1], 9))
    assert not hole[0][in_first].any() and np.array_equal(hole[0][~in_first], full[0][~in_first])


def test_a_chunk_that_cannot_be_read_stops_the_reading():
    volume = np.ones((8, 8, 8), dtype=np.uint8)
    points, normals_ = np.array([[0.5, 0.5, 0.5]]), np.array([[0.0, 0.0, 1.0]])
    with pytest.raises(RuntimeError, match="could not be read"):
        nw.read_samples(_fabricated_prediction(volume, (4, 4, 4), unreadable={(1, 0, 0)}), points, normals_,
                        _rays_for(points, normals_, 8))


def test_the_depths_of_embedded_rays_follow_their_side_and_their_step(tmp_path):
    """A file written on the minus side stores a step of -1: its depths go 0, -1, -2, and not nowhere."""
    import gzip
    import io
    import json as _json
    from vesuve.embedded import rays_from

    def write(name, a):
        buf = io.BytesIO()
        np.save(buf, a, allow_pickle=False)
        (tmp_path / name).write_bytes(gzip.compress(buf.getvalue()))
    write("rays_seen.npy.gz", np.packbits(np.zeros((2, 217), dtype=bool), axis=1))
    write("rays_grid.npy.gz", np.array([[0, 0], [0, 1]], dtype=np.int32))
    (tmp_path / "rays.json").write_text(_json.dumps({
        "prediction": "m7", "path": "p", "level": 0, "factor": 4, "side": "minus", "samples": 217,
        "depth_step_voxels": -1.0, "step_voxels": 72.08333333333334, "half_sheet_voxels": 36.0, "points": 2,
        "grid": [1, 2]}))
    r = rays_from(tmp_path)
    assert r.side == -1.0 and np.array_equal(r.depths, -np.arange(217.0))


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


SPOT_CHECK_RAYS = 100


def rays_that_see_something(rays, count: int = SPOT_CHECK_RAYS) -> np.ndarray:
    """`count` rays spread evenly over the rays whose embedded samples mark at least one sheet: reading the first rays
    of the mesh compares mostly empty prediction with empty prediction (13 of the first 300 see anything)."""
    seeing = np.flatnonzero(rays.seen.any(axis=1))
    return seeing[np.linspace(0, len(seeing) - 1, count).round().astype(np.intp)]


@pytest.mark.parametrize("name", [SEGMENT, BAND])
def test_the_spot_check_rays_all_see_something_and_cover_the_surface(name):
    r = embedded.rays(name)
    chosen = rays_that_see_something(r)
    seeing = np.flatnonzero(r.seen.any(axis=1))
    assert len(seeing) > 10 * SPOT_CHECK_RAYS
    assert len(np.unique(chosen)) == SPOT_CHECK_RAYS
    assert r.seen[chosen].any(axis=1).all()
    assert chosen[0] == seeing[0] and chosen[-1] == seeing[-1]
    assert np.ptp(r.rows[chosen]) > 0.5 * np.ptp(r.rows) and np.ptp(r.columns[chosen]) > 0.5 * np.ptp(r.columns)


@network
def test_the_samples_read_from_the_bucket_are_the_embedded_ones(tmp_path):
    """The rays rebuilt from the published mesh sit where the embedded ones sit, and the public prediction read along
    spread rays that really see a sheet gives back the embedded samples.

    Downloads the mesh (55 MB) and the prediction chunks under 100 rays: about 100 chunks, or a few times more where a
    ray crosses a chunk boundary, of the 1780 the whole segment needs (about 630 MB). An estimate, not a measure: about
    90 MB in all, perhaps a few times more."""
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
        some = rays_that_see_something(r)
        assert np.array_equal(nw.read_samples(nw.prediction(transport, r), p[some], n[some], r), r.seen[some])
    finally:
        transport.close()
