"""The judge of the text of the produced winding (`296`, `R4-F477`): where the segment passes over the winding produced
from it, our reading of that winding is compared with the segment's published ink map.

Offline: the rules on fabricated surfaces, the coverage of the embedded segment. With the research's code and data
(`VESUVE_RESEARCH`, `VESUVE_DATA`): each function against the research's, and the three correlations of `R4-F477` on the
research's own readings of the ink."""
from __future__ import annotations

import json

import numpy as np
import pytest

from conftest import DATA, MEASURES, research
from vesuve import embedded, images
from vesuve.transfer import ink_judge as ij

SEGMENT = "20230702185753"
READINGS = DATA / "encre_du_tour_voisin"
PUBLISHED_MAP = READINGS / "carte_publiee_ds8.jpg"
JUDGED = [(144, 176), (176, 192), (224, 192), (192, 144), (144, 160), (160, 176)]


def two_turns() -> ij.Meshes:
    """A segment that makes two turns: two flat sheets 73 voxels apart, carried by distant columns of the grid. The
    produced winding sits 73 voxels above the first turn, on the second turn."""
    h, w = 10, 80
    reference = np.zeros((h, w, 3))
    valid = np.zeros((h, w), dtype=bool)
    for i in range(h):
        for j in range(20):
            reference[i, j] = (j * 20.0, i * 20.0, 0.0)
            reference[i, j + 50] = (j * 20.0, i * 20.0, 73.0)
    valid[:, :20] = True
    valid[:, 50:70] = True
    produced = reference.copy()
    produced[..., 2] += 73.0
    produced_valid = valid.copy()
    produced_valid[:, 50:] = False
    return ij.Meshes(reference, valid, produced, produced_valid, spacing=160.0)


def test_the_facing_point_of_the_produced_winding_is_the_second_turn_of_the_segment():
    gap = ij.facing_points(two_turns(), range(10), range(20), far=30)
    row, column, distance = gap
    assert np.nanmax(distance) < 1e-9
    assert np.all(column == np.arange(20)[None, :] + 50) and np.all(row == np.arange(10)[:, None])


def test_without_a_point_far_on_the_surface_there_is_no_facing_point():
    assert np.isnan(ij.facing_points(two_turns(), range(10), range(20), far=1000)[2]).all()


def test_the_same_sheet_taken_further_is_a_whole_sheet_away_not_within_half_a_sheet():
    meshes = two_turns()
    one_turn = ij.Meshes(meshes.reference, meshes.reference_valid & (np.arange(80) < 50)[None, :], meshes.produced,
                         meshes.produced_valid, meshes.spacing)
    assert np.nanmin(ij.facing_points(one_turn, range(10), range(20), far=3)[2]) > ij.HALF_SHEET


def test_a_failed_transfer_that_fell_back_on_its_own_sheet_is_not_judged_against_it():
    meshes = two_turns()
    failed = ij.Meshes(meshes.reference, meshes.reference_valid, meshes.reference + [0, 0, 10.0], meshes.produced_valid,
                       meshes.spacing)
    _, column, gap = ij.facing_points(failed, range(10), range(20), far=30)
    assert np.all(column >= 50) and np.nanmin(gap) > ij.HALF_SHEET


def test_the_near_share_counts_the_points_within_half_a_sheet_among_those_that_have_a_facing_point():
    assert ij.near_share(np.array([1.0, 50.0, np.nan, 10.0])) == 2 / 3
    assert ij.near_share(np.array([np.nan])) == 0.0


def test_the_blocks_judged_are_the_largest_near_shares_outside_the_excluded_band_and_in_block_order_on_a_tie():
    shares = {(16, 0): 0.2, (16, 16): 0.9, (32, 0): 0.9, (32, 16): 0.5, (48, 0): 0.95}
    assert ij.blocks_to_judge(shares, {(48, 0)}, 3) == [(16, 16), (32, 0), (32, 16)]


def test_a_block_of_the_band_the_research_chose_by_eye_is_never_judged():
    """The exclusion rule: the band was looked at before the rule was written, so it cannot be a witness of it. The
    probe is in the test: the same shares, without the exclusion, would judge the excluded block first."""
    shares = {(176, 80): 0.99, (176, 144): 0.98, (16, 0): 0.4, (32, 0): 0.3}
    assert ij.blocks_to_judge(shares, count=4) == [(16, 0), (32, 0)]
    assert ij.blocks_to_judge(shares, excluded=frozenset(), count=4)[:2] == [(176, 80), (176, 144)]
    assert (176, 144) in ij.EXCLUDED_BLOCKS == {(176, 64 + 16 * k) for k in range(6)}
    assert ij.CALIBRATION_BLOCK in ij.EXCLUDED_BLOCKS


def test_the_reduction_is_a_mean_by_square_and_leaves_nan_out():
    x = np.arange(64, dtype=float).reshape(8, 8)
    assert np.allclose(ij.reduce_ink(x, 4), [[13.5, 17.5], [45.5, 49.5]])
    x[0, 0] = np.nan
    assert np.isclose(ij.reduce_ink(x, 4)[0, 0], 216 / 15)


def test_the_correlation_is_one_for_equal_maps_and_is_not_given_under_the_minimum():
    a = np.random.default_rng(0).random((200, 200))
    assert ij.correlation(a, a)[0] == 1.0
    assert ij.correlation(a[:10, :10], a[:10, :10])[0] is None
    assert ij.correlation(a, a, a > 0.5, minimum=1)[1] == int((a > 0.5).sum())
    assert ij.correlation(np.ones((200, 200)), a)[0] is None


def test_the_cells_of_a_band_cover_its_pixels_edges_included():
    rows, columns = ij.block_cells(176, 64, 2, 160.0)
    assert rows[0] * 160 <= 176 * 128 and rows[-1] * 160 >= 192 * 128
    assert columns[0] * 160 <= 64 * 128 and columns[-1] * 160 >= 96 * 128


def test_a_facing_point_that_is_the_point_itself_reads_the_map_under_the_band_and_the_shifted_control_64_pixels_on():
    rows, columns = ij.block_cells(176, 64, 2, 160.0)
    published = np.add.outer(np.arange(6400.0), np.arange(4600.0) * 0.001)
    row, column = np.meshgrid(rows.astype(float), columns.astype(float), indexing="ij")
    read = ij.published_facing(published, row, column, rows, columns, 176, 64, 2, 160.0)
    under = ij.published_under(published, 176, 64, 2)
    assert read.shape == under.shape and np.nanmax(np.abs(read - under)) < 0.51
    shifted = ij.published_facing(published, row, column, rows, columns, 176, 64, 2, 160.0, ij.SHIFT)
    assert np.nanmax(np.abs((shifted - read) - ij.SHIFT * 0.001)) < 1e-6
    assert ij.published_under(published, 176, 144, 1).shape == (256, 256)


def _compared(calibration: float | None, pixels: int = 20000, facing=0.8, under=0.1, shifted=0.3):
    return ij.outcome(calibration, {"pixels": pixels, "facing": facing, "control_under_the_block": under,
                                    "control_shifted": shifted})


def test_the_outcome_carries_when_the_facing_correlation_beats_both_controls():
    assert _compared(0.95) == {"outcome": ij.CARRIES, "decidable": True}


def test_the_outcome_does_not_carry_when_a_control_equals_the_facing_correlation():
    assert _compared(0.95, shifted=0.85) == {"outcome": ij.DOES_NOT_CARRY, "decidable": True}
    assert _compared(0.95, under=0.8)["outcome"] == ij.DOES_NOT_CARRY


def test_the_outcome_is_undecidable_without_a_calibration_or_without_pixels():
    assert _compared(0.5)["outcome"] == ij.UNDECIDABLE_CALIBRATION
    assert _compared(None)["outcome"] == ij.UNDECIDABLE_CALIBRATION
    assert _compared(0.95, pixels=100)["outcome"] == ij.UNDECIDABLE_PIXELS
    assert _compared(0.95, shifted=None)["outcome"] == ij.UNDECIDABLE_PIXELS
    assert not _compared(0.95, pixels=100)["decidable"]


def test_the_embedded_segment_gives_the_coverage_of_r4_f477_from_its_two_meshes_alone():
    """The research's six blocks and their near shares, and the median of the 340 blocks: 0.0222."""
    meshes, candidates = embedded.ink_judge_meshes(SEGMENT), embedded.correction(SEGMENT)["candidates"]
    c = ij.coverage(meshes, candidates)
    assert c["blocks_examined"] == len(candidates) == 340
    assert c["median_near_share"] == 0.0222
    assert [tuple(b) for b in c["judged_blocks"]] == JUDGED
    assert c["judged_near_shares"] == [0.7511, 0.7333, 0.7156, 0.6889, 0.6714, 0.6476]
    assert not set(map(tuple, c["judged_blocks"])) & ij.EXCLUDED_BLOCKS
    assert c["blocks_with_a_near_share_of_half_or_more"] == 13 and c["blocks_with_any_near_share"] == 196


def test_the_readings_are_read_from_a_folder_that_names_what_it_lacks(tmp_path):
    with pytest.raises(FileNotFoundError) as lacks:
        ij.load_readings(tmp_path, JUDGED[:2])
    assert "calibration.npy" in str(lacks.value) and "produced_144_176.npy" in str(lacks.value)
    np.save(tmp_path / "calibration.npy", np.ones((2, 2)))
    for block in JUDGED[:2]:
        np.save(tmp_path / ij.reading_file(block), np.full((2, 2), block[0]))
    calibration, readings = ij.load_readings(tmp_path, JUDGED[:2])
    assert calibration.shape == (2, 2) and sorted(readings) == sorted(JUDGED[:2]) and readings[(176, 192)][0, 0] == 176


def test_the_model_cannot_read_without_torch_or_without_its_file(tmp_path, monkeypatch):
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    why = ij.why_the_model_cannot_read(tmp_path)
    assert "torch is not installed" in why and str(tmp_path) in why and ij.MODEL_FILE in why
    monkeypatch.setattr("importlib.util.find_spec", lambda name: object())
    assert ij.why_the_model_cannot_read(tmp_path) == f"the model is not at {tmp_path / 'models' / 'ink_canonical_2um' / ij.MODEL_FILE}"
    monkeypatch.undo()
    model = tmp_path / "models" / "ink_canonical_2um"
    model.mkdir(parents=True)
    (model / ij.MODEL_FILE).write_bytes(b"")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: object())
    assert ij.why_the_model_cannot_read(tmp_path) is None


@research
def test_the_embedded_meshes_are_the_ones_the_research_rendered():
    import tifffile
    for role, surface in (("reference", "le_segment_reduit"), ("produced", "la_spire_produite")):
        folder = DATA / "rendu_spire_voisine" / surface / "maillage"
        if not folder.is_dir():
            pytest.skip(f"the research's rendered meshes are not under {DATA}")
        points = np.stack([tifffile.imread(folder / f"{c}.tif") for c in "xyz"], axis=-1)
        meshes = embedded.ink_judge_meshes(SEGMENT)
        assert np.array_equal(getattr(meshes, role), points.astype(np.float64))
        assert meshes.spacing == 1.0 / json.loads((folder / "meta.json").read_text())["scale"][0]


@research
def test_each_geometric_rule_is_the_research_s_on_the_embedded_meshes():
    """Function against function, on the blocks the research judged and on a block it did not."""
    from le_tour_produit_porte_t_il_le_texte_du_segment import la_part_proche as research_near_share
    from le_tour_produit_porte_t_il_le_texte_du_segment import les_blocs_de_la_partie_b as research_blocks
    from le_tour_produit_porte_t_il_le_texte_du_segment import les_mailles_dune_bande as research_cells
    from le_tour_produit_porte_t_il_le_texte_du_segment import les_vis_a_vis as research_facing
    meshes = embedded.ink_judge_meshes(SEGMENT)
    for block in JUDGED[:3] + [(16, 32), (176, 64)]:
        rows, columns = ij.block_cells(*block, 1, meshes.spacing)
        theirs_rows, theirs_columns = research_cells(*block, 1, meshes.spacing)
        assert np.array_equal(rows, theirs_rows) and np.array_equal(columns, theirs_columns)
        ours = ij.facing_points(meshes, rows, columns)
        theirs = research_facing(meshes.reference, meshes.reference_valid, meshes.produced, meshes.produced_valid,
                                 rows, columns)
        for a, b in zip(ours, theirs):
            assert np.array_equal(a, b, equal_nan=True)
        assert ij.near_share(ours[2]) == research_near_share(theirs[2])
    shares = {(16, 0): 0.2, (16, 16): 0.9, (32, 0): 0.9, (176, 80): 0.99}
    assert ij.blocks_to_judge(shares, ij.EXCLUDED_BLOCKS, 3) == research_blocks(shares, ij.EXCLUDED_BLOCKS, 3)


@research
def test_each_pixel_rule_is_the_research_s_on_a_synthetic_map():
    from le_tour_produit_porte_t_il_le_texte_du_segment import correlation as research_correlation
    from le_tour_produit_porte_t_il_le_texte_du_segment import la_carte_au_vis_a_vis as research_facing_map
    from le_tour_produit_porte_t_il_le_texte_du_segment import la_carte_sous as research_under
    from le_tour_produit_porte_t_il_le_texte_du_segment import lecart_au_pixel as research_gap_pixels
    from le_tour_produit_porte_t_il_le_texte_du_segment import reduire as research_reduce
    meshes = embedded.ink_judge_meshes(SEGMENT)
    published = np.random.default_rng(296).random((4200, 3600)).astype(np.float32)
    block = (144, 176)
    rows, columns = ij.block_cells(*block, 1, meshes.spacing)
    row, column, gap = ij.facing_points(meshes, rows, columns)
    ours = ij.published_facing(published, row, column, rows, columns, *block, 1, meshes.spacing)
    theirs = research_facing_map(published, row, column, rows, columns, *block, 1, meshes.spacing)
    assert np.array_equal(ours, theirs, equal_nan=True)
    shifted = ij.published_facing(published, row, column, rows, columns, *block, 1, meshes.spacing, ij.SHIFT)
    assert np.array_equal(shifted, research_facing_map(published, row, column, rows, columns, *block, 1, meshes.spacing,
                                                        ij.SHIFT), equal_nan=True)
    assert np.array_equal(ij.published_under(published, *block, 1), research_under(published, *block, 1))
    assert np.array_equal(ij.gap_per_pixel(gap, rows, columns, *block, 1, meshes.spacing),
                          research_gap_pixels(gap, rows, columns, *block, 1, meshes.spacing))
    reading = np.random.default_rng(1).random((2048, 2048)).astype(np.float32)
    assert np.array_equal(ij.reduce_ink(reading), research_reduce(reading))
    assert ij.correlation(ij.reduce_ink(reading), ours[:256, :256]) == research_correlation(research_reduce(reading),
                                                                                           theirs[:256, :256])


@research
def test_the_outcome_is_the_research_s_on_each_branch():
    from le_tour_produit_porte_t_il_le_texte_du_segment import le_verdict as research_outcome

    def theirs(calibration, within):
        return research_outcome({"letalonnage": {"la_correlation": calibration},
                                 "la_partie_b": {"reunie": {"a_moins_dun_demi_feuillet": within}}})["decidable"]
    for calibration, pixels, shifted in ((0.95, 20000, 0.3), (0.95, 20000, 0.85), (0.5, 20000, 0.3), (0.95, 100, 0.3)):
        within = {"les_pixels": pixels, "au_vis_a_vis": 0.8, "temoin_sous_le_bloc": 0.1, "temoin_decale": shifted}
        ours = _compared(calibration, pixels, shifted=shifted)
        assert ours["decidable"] == theirs(calibration, within)


@research
def test_the_research_s_readings_give_back_the_three_correlations_of_r4_f477(tmp_path):
    """The model is not run: the readings it made for the research are read, under the names this program expects.
    0.8331 against 0.1166 and 0.1037 on the six blocks, after a calibration at 0.9593."""
    if not (PUBLISHED_MAP.exists() and (READINGS / "etalon_reference.npy").exists()):
        pytest.skip(f"the research's ink readings and the published map are not under {READINGS}")
    (tmp_path / "calibration.npy").symlink_to(READINGS / "etalon_reference.npy")
    for block in JUDGED:
        (tmp_path / ij.reading_file(block)).symlink_to(READINGS / f"partie_b_produite_{block[0]}_{block[1]}.npy")
    calibration, readings = ij.load_readings(tmp_path, JUDGED)
    published = images.read_image(PUBLISHED_MAP.read_bytes()).astype(np.float32)
    got = ij.judge(embedded.ink_judge_meshes(SEGMENT), published, calibration, readings, JUDGED)
    assert got["calibration"] == {"block": [176, 144], "correlation": 0.9593, "pixels": 65536}
    assert got["pooled"]["within_half_a_sheet"] == {"pixels": 290992, "facing": 0.8331,
                                                     "control_under_the_block": 0.1166, "control_shifted": 0.1037}
    assert got["pooled"]["beyond"] == {"pixels": 102224, "facing": 0.8164, "control_under_the_block": 0.111,
                                       "control_shifted": 0.124}
    assert got["outcome"] == ij.CARRIES and got["decidable"]
    measured = json.loads((MEASURES / "le_tour_produit_porte_t_il_le_texte_du_segment.json").read_text())
    assert [b["block"] for b in got["blocks"]] == [b["le_bloc"] for b in measured["la_partie_b"]["les_blocs"]]
    assert [b["near_share"] for b in got["blocks"]] == [b["la_part_proche"] for b in measured["la_partie_b"]["les_blocs"]]
    assert [b["within_half_a_sheet"]["pixels"] for b in got["blocks"]] == [
        b["a_moins_dun_demi_feuillet"]["les_pixels"] for b in measured["la_partie_b"]["les_blocs"]]


def _grand_prize(tmp_path, monkeypatch, bodies=None, **options) -> dict:
    from vesuve.grand_prize.pipeline import run
    from vesuve.transport import InMemoryTransport
    monkeypatch.setattr("vesuve.grand_prize.pipeline.Transport", lambda **_: InMemoryTransport(bodies or {}))
    run(output=tmp_path / "out", cache=tmp_path / "cache", surface=False, **options)
    return {s["id"]: s for s in json.loads((tmp_path / "out" / "report.json").read_text())["stages"]}


def _published_map_body(tmp_path, data: bytes) -> dict:
    from vesuve.lattice.segment import published_ink_map_path
    from vesuve.remote import Remote
    from vesuve.transport import InMemoryTransport
    path = published_ink_map_path(embedded.segment(SEGMENT)["context"])
    return {Remote(tmp_path / "cache", InMemoryTransport({})).url(path): data}


def test_without_ink_readings_the_stage_gives_the_coverage_and_says_it_judges_nothing_else(tmp_path, monkeypatch):
    stages = _grand_prize(tmp_path, monkeypatch, ink=False)
    t = stages["TJ"]
    assert t["state"] == "partial" and "--ink-readings" in t["reason"] and "no text is judged" in t["reason"]
    assert "does not read the ink with scrollprize/ink_canonical_2um itself" in t["reason"]
    out = t["outputs"]
    assert out["blocks_examined"] == 340 and out["median_near_share"] == 0.0222
    assert [tuple(b) for b in out["judged_blocks"]] == JUDGED
    assert "nothing" in out["where_it_judges"] and "passes over" in out["where_it_judges"]
    order = list(stages)
    assert order[order.index("TJ") - 1] == "T"
    assert stages["E9"]["state"] == "done"


def test_the_stage_says_why_the_model_cannot_read_and_the_pipeline_goes_on(tmp_path, monkeypatch):
    monkeypatch.setattr("vesuve.grand_prize.pipeline.ij.why_the_model_cannot_read",
                        lambda cache: "torch is not installed; the model is not at X")
    stages = _grand_prize(tmp_path, monkeypatch, ink=False)
    assert "torch is not installed; the model is not at X" in stages["TJ"]["reason"]
    assert "does not read the ink with scrollprize/ink_canonical_2um itself" in stages["TJ"]["reason"]
    assert stages["T"]["state"] != "stopped" and stages["E9"]["state"] == "done"


def test_a_readings_folder_that_lacks_a_file_is_named_and_the_coverage_is_kept(tmp_path, monkeypatch):
    (tmp_path / "readings").mkdir()
    stages = _grand_prize(tmp_path, monkeypatch, ink=False, ink_readings=tmp_path / "readings")
    t = stages["TJ"]
    assert t["state"] == "partial" and "calibration.npy" in t["reason"] and "produced_144_176.npy" in t["reason"]
    assert t["outputs"]["median_near_share"] == 0.0222


def test_a_published_map_that_cannot_be_obtained_is_said_and_the_coverage_is_kept(tmp_path, monkeypatch):
    folder = tmp_path / "readings"
    folder.mkdir()
    np.save(folder / "calibration.npy", np.zeros((2, 2)))
    for block in JUDGED:
        np.save(folder / ij.reading_file(block), np.zeros((2, 2)))
    stages = _grand_prize(tmp_path, monkeypatch, ink=False, ink_readings=folder)
    assert stages["TJ"]["state"] == "partial" and "published ink map" in stages["TJ"]["reason"]
    assert stages["TJ"]["outputs"]["median_near_share"] == 0.0222


def test_with_readings_and_the_map_the_stage_reports_the_outcome_and_the_equations_it_applied(tmp_path, monkeypatch):
    import io

    from PIL import Image
    folder = tmp_path / "readings"
    folder.mkdir()
    np.save(folder / "calibration.npy", np.zeros((2, 2)))
    for block in JUDGED:
        np.save(folder / ij.reading_file(block), np.zeros((2, 2)))
    jpeg = io.BytesIO()
    Image.fromarray(np.zeros((8, 8), dtype=np.uint8)).save(jpeg, format="JPEG")
    seen = {}

    def canned(meshes, published, calibration, readings, blocks):
        seen.update(blocks=blocks, published=published.shape, readings=sorted(readings), dtype=str(published.dtype))
        return {"calibration": {"block": [176, 144], "correlation": 0.96, "pixels": 65536}, "blocks": [],
                "pooled": {"within_half_a_sheet": {"pixels": 20000, "facing": 0.8, "control_under_the_block": 0.1,
                                                   "control_shifted": 0.1}, "beyond": {}},
                "outcome": ij.CARRIES, "decidable": True}
    monkeypatch.setattr("vesuve.grand_prize.pipeline.ij.judge", canned)
    stages = _grand_prize(tmp_path, monkeypatch, bodies=_published_map_body(tmp_path, jpeg.getvalue()), ink=False,
                          ink_readings=folder)
    t = stages["TJ"]
    assert t["state"] == "done" and t["outputs"]["outcome"] == ij.CARRIES
    assert t["outputs"]["pooled"]["within_half_a_sheet"]["facing"] == 0.8
    assert [q["id"] for q in t["equations"]] == ["JT1", "JT2", "JT3"]
    assert seen["blocks"] == JUDGED and seen["published"] == (8, 8) and seen["dtype"] == "float32"
    assert "carries the segment" in t["outputs"]["what_it_says"] and "nothing" in t["outputs"]["where_it_judges"]


def test_an_undecidable_outcome_makes_the_stage_partial_and_says_why(tmp_path, monkeypatch):
    import io

    from PIL import Image
    folder = tmp_path / "readings"
    folder.mkdir()
    np.save(folder / "calibration.npy", np.zeros((2, 2)))
    for block in JUDGED:
        np.save(folder / ij.reading_file(block), np.zeros((2, 2)))
    jpeg = io.BytesIO()
    Image.fromarray(np.zeros((8, 8), dtype=np.uint8)).save(jpeg, format="JPEG")
    monkeypatch.setattr("vesuve.grand_prize.pipeline.ij.judge", lambda *a: {
        "calibration": {"correlation": 0.5}, "blocks": [], "pooled": {"within_half_a_sheet": {}, "beyond": {}},
        "outcome": ij.UNDECIDABLE_CALIBRATION, "decidable": False})
    stages = _grand_prize(tmp_path, monkeypatch, bodies=_published_map_body(tmp_path, jpeg.getvalue()), ink=False,
                          ink_readings=folder)
    assert stages["TJ"]["state"] == "partial" and ij.UNDECIDABLE_CALIBRATION in stages["TJ"]["reason"]


@research
def test_the_stage_gives_back_the_three_correlations_of_r4_f477_on_the_research_s_readings(tmp_path, monkeypatch):
    """The criterion of the issue: with the research's data, the stage gives back 0.8331, 0.1166 and 0.1037 on the same
    six blocks. The ink is not read again: the readings the model made for the research are given under their names."""
    if not (PUBLISHED_MAP.exists() and (READINGS / "etalon_reference.npy").exists()):
        pytest.skip(f"the research's ink readings and the published map are not under {READINGS}")
    folder = tmp_path / "readings"
    folder.mkdir()
    (folder / "calibration.npy").symlink_to(READINGS / "etalon_reference.npy")
    for block in JUDGED:
        (folder / ij.reading_file(block)).symlink_to(READINGS / f"partie_b_produite_{block[0]}_{block[1]}.npy")
    stages = _grand_prize(tmp_path, monkeypatch, bodies=_published_map_body(tmp_path, PUBLISHED_MAP.read_bytes()),
                          ink=False, ink_readings=folder)
    t = stages["TJ"]
    assert t["state"] == "done" and t["outputs"]["outcome"] == ij.CARRIES
    assert t["outputs"]["calibration"]["correlation"] == 0.9593
    assert t["outputs"]["pooled"]["within_half_a_sheet"] == {"pixels": 290992, "facing": 0.8331,
                                                              "control_under_the_block": 0.1166,
                                                              "control_shifted": 0.1037}


def test_the_command_line_hands_the_readings_folder_to_the_pipeline(monkeypatch):
    from vesuve import cli
    seen = {}

    def run(segment, output, cache, **options):
        seen.update(options)
        return type("R", (), {"stopped": False})()
    monkeypatch.setattr("vesuve.grand_prize.pipeline.run", run)
    assert cli.main(["grand-prize", "--ink-readings", "some/folder", "--no-ink", "--no-surface"]) == 0
    assert str(seen["ink_readings"]) == "some/folder"


def test_a_readings_file_that_is_not_a_2d_array_is_named_and_the_pipeline_goes_on(tmp_path, monkeypatch):
    folder = tmp_path / "readings"
    folder.mkdir()
    (folder / "calibration.npy").write_bytes(b"not an array")
    for block in JUDGED:
        np.save(folder / ij.reading_file(block), np.zeros(4))
    with pytest.raises(ValueError, match="calibration.npy is not a NumPy array"):
        ij.load_readings(folder, JUDGED)
    np.save(folder / "calibration.npy", np.zeros((2, 2)))
    with pytest.raises(ValueError, match="1 dimensions"):
        ij.load_readings(folder, JUDGED)
    stages = _grand_prize(tmp_path, monkeypatch, ink=False, ink_readings=folder)
    assert stages["TJ"]["state"] == "partial" and "no text is judged" in stages["TJ"]["reason"]
    assert stages["E9"]["state"] == "done"


def two_turns_of_blocks() -> ij.Meshes:
    """Two turns on a grid that holds a whole block: the first turn on columns 0 to 13 of rows 0 to 13, the second 73
    voxels above it on columns 50 to 63, so the winding produced from the first turn faces the second, at a gap of 0.
    Rows 14 to 39 hold nothing produced."""
    h, w = 40, 64
    reference = np.zeros((h, w, 3))
    valid = np.zeros((h, w), dtype=bool)
    for i in range(14):
        for j in range(14):
            reference[i, j] = (j * 160.0, i * 160.0, 0.0)
            reference[i, j + 50] = (j * 160.0, i * 160.0, 73.0)
    valid[:14, :14] = True
    valid[:14, 50:64] = True
    produced = reference.copy()
    produced[..., 2] += 73.0
    produced_valid = valid.copy()
    produced_valid[:, 50:] = False
    return ij.Meshes(reference, valid, produced, produced_valid, spacing=160.0)


def test_the_exclusion_reaches_the_blocks_the_coverage_chooses():
    """The block of the largest near share is in the excluded band: it must not be judged. Without the exclusion it is
    chosen first (the other block has no produced point, hence a near share of 0)."""
    meshes = two_turns_of_blocks()
    candidates = {(0, 0), (32, 0)}
    assert ij.coverage(meshes, candidates, excluded=frozenset())["judged_blocks"] == [[0, 0], [32, 0]]
    assert ij.coverage(meshes, candidates, excluded={(0, 0)})["judged_blocks"] == [[32, 0]]
    assert ij.coverage(meshes, candidates)["shares"] == {(0, 0): 1.0, (32, 0): 0.0}


def _smooth(shape, seed: int) -> np.ndarray:
    from scipy.ndimage import gaussian_filter
    field = gaussian_filter(np.random.default_rng(seed).random(shape), 6)
    return ((field - field.min()) / (field.max() - field.min()) * 255).astype(np.float32)


def _text_world():
    """A published map whose text under block (0, 0), at the facing point of the produced winding (1000 pixels on, on
    the second turn) and at the control shifted by 64 pixels differ; the reading of the calibration block is the map
    under it."""
    published = _smooth((3200, 2600), 296)
    calibration = np.kron(published[2816:3072, 2304:2560], np.ones((8, 8), dtype=np.float32))
    facing_text = np.kron(published[0:256, 1000:1256], np.ones((8, 8), dtype=np.float32))
    starting_text = np.kron(published[0:256, 0:256], np.ones((8, 8), dtype=np.float32))
    return published, calibration, facing_text, starting_text


def test_a_reading_that_is_the_text_at_the_facing_point_is_judged_to_carry_it():
    published, calibration, facing_text, _ = _text_world()
    judged = ij.judge(two_turns_of_blocks(), published, calibration, {(0, 0): facing_text}, [(0, 0)])
    assert judged["calibration"]["correlation"] > 0.95 and judged["calibration"]["pixels"] == 65536
    near = judged["pooled"]["within_half_a_sheet"]
    assert near["pixels"] > 60000 and near["facing"] > 0.95
    assert near["control_under_the_block"] < 0.5 and near["control_shifted"] < 0.5
    assert judged["outcome"] == ij.CARRIES and judged["blocks"][0]["near_share"] == 1.0


def test_a_reading_that_copies_the_text_of_the_starting_winding_is_judged_not_to_carry_it():
    published, calibration, _, starting_text = _text_world()
    judged = ij.judge(two_turns_of_blocks(), published, calibration, {(0, 0): starting_text}, [(0, 0)])
    near = judged["pooled"]["within_half_a_sheet"]
    assert near["control_under_the_block"] > 0.95 and near["facing"] < near["control_under_the_block"]
    assert judged["outcome"] == ij.DOES_NOT_CARRY and judged["decidable"]


def test_a_reading_that_does_not_find_the_published_map_on_the_reference_decides_nothing():
    published, _, facing_text, _ = _text_world()
    noise = np.random.default_rng(0).random((2048, 2048)).astype(np.float32)
    judged = ij.judge(two_turns_of_blocks(), published, noise, {(0, 0): facing_text}, [(0, 0)])
    assert judged["calibration"]["correlation"] < ij.CALIBRATION_THRESHOLD
    assert judged["outcome"] == ij.UNDECIDABLE_CALIBRATION and not judged["decidable"]


def test_the_correlations_are_taken_apart_by_the_half_sheet_mask():
    """Within the mask the facing map is the reading; beyond it, noise: the two correlations must not be the same."""
    rng = np.random.default_rng(3)
    read = rng.random((300, 300))
    near = np.zeros((300, 300), dtype=bool)
    near[:, :150] = True
    facing = np.where(near, read, rng.random((300, 300)))
    got = ij._correlations(read, facing, rng.random((300, 300)), rng.random((300, 300)), near)
    assert got["within_half_a_sheet"]["pixels"] == 45000 == got["beyond"]["pixels"]
    assert got["within_half_a_sheet"]["facing"] == 1.0 and abs(got["beyond"]["facing"]) < 0.1
