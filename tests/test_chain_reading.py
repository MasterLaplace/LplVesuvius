"""Judging a chain against the published windings, strictly (`R4-F551`), the seeds it starts from, and the reader of the
prediction. Offline on fabricated windings; against the research's functions and on the published windings with
`VESUVE_RESEARCH` and `VESUVE_DATA`."""
from __future__ import annotations

import numpy as np
import pytest

from conftest import DATA, research
from vesuve.chain import reading as r
from vesuve.chain import seeds
from vesuve.chain.prediction import PredictionReader
from vesuve.remote_zarr import RemoteArray
from vesuve.transport import InMemoryTransport

PUBLISHED = DATA / "tours_publies_5753"
TURNS = {0: "20260602225659-5753_0", -1: "20260603005223-5753_-1", -2: "20260603024952-5753_-2",
         -3: "20260603042357-5753_-3", -4: "20260603145540-5753_-4", -5: "20260603190005-5753_-5",
         -6: "20260603185441-5753_-6", -7: "20260602204401-5753_-7"}


def flat_turn(z: float, n: int = 40, spacing: float = 10.0) -> r.PublishedTurn:
    grid = np.zeros((n, n, 3))
    for a in range(n):
        for b in range(n):
            grid[a, b] = (spacing * b, spacing * a, z)
    return r.PublishedTurn(grid.reshape(-1, 3), np.tile([0.0, 0.0, 1.0], (n * n, 1)))


def surface_at(z: float, n: int = 20) -> np.ndarray:
    return flat_turn(z, n).points


TURNS_AT = {0: flat_turn(0.0), -1: flat_turn(-72.0), -2: flat_turn(-144.0), -3: flat_turn(-216.0)}


def test_a_surface_on_a_published_winding_finds_it_and_not_the_next_and_does_not_read_the_far_ones():
    """Windings more than the margin (100 voxels) away from the surface's box have no vertex read: not read, not absent."""
    got = r.read_against(surface_at(1.0), TURNS_AT)
    assert got == {0: r.FOUND, -1: r.NOT_FOUND, -2: r.NOT_READ, -3: r.NOT_READ}


def test_a_surface_between_two_windings_finds_neither():
    got = r.read_against(surface_at(-36.0), TURNS_AT)
    assert r.found_turns(got) == [] and got[0] == r.NOT_FOUND


def test_a_surface_with_too_few_vertices_facing_it_is_not_read():
    far = surface_at(0.0) + np.array([5000.0, 0.0, 0.0])
    assert set(r.read_against(far, TURNS_AT).values()) == {r.NOT_READ}
    assert r.coincidence(np.full(100, np.nan))["reading"] == r.NOT_READ
    assert r.coincidence(np.zeros(4))["reading"] == r.NOT_READ and r.coincidence(np.zeros(5))["reading"] == r.FOUND


def test_a_winding_is_found_only_if_half_the_vertices_and_the_median_are_within_a_quarter_step():
    assert r.coincidence(np.concatenate([np.full(51, 1.0), np.full(49, 40.0)]))["reading"] == r.FOUND
    assert r.coincidence(np.concatenate([np.full(49, 1.0), np.full(51, 40.0)]))["reading"] == r.NOT_FOUND
    assert r.coincidence(np.concatenate([np.full(40, 1.0), np.full(60, 40.0)]))["share_within_a_quarter_step"] == 0.4
    assert r.coincidence(np.full(10, r.QUARTER_STEP + 1.0))["reading"] == r.NOT_FOUND
    assert r.coincidence(np.full(10, -r.QUARTER_STEP + 1.0))["reading"] == r.FOUND


def found(*turns):
    return {t: (r.FOUND if t in turns else r.NOT_FOUND) for t in range(0, -8, -1)}


def test_a_jump_to_the_next_winding_is_right_and_two_windings_or_another_is_wrong():
    assert r.justness(found(-1), found(-2), -1) == r.RIGHT
    assert r.justness(found(-1), found(0), 1) == r.RIGHT
    assert r.justness(found(-1), found(-2, -3), -1) == r.WRONG_TWO_TURNS
    assert r.justness(found(-1), found(-4), -1) == r.WRONG_ANOTHER_TURN
    assert r.justness(found(-1), found(), -1) == r.WRONG_MISSED_TURN


def test_a_jump_is_not_judged_without_exactly_one_turn_before_or_beyond_the_judged_windings():
    assert r.justness(found(-1, -2), found(-3), -1) == r.NOT_JUDGED
    assert r.justness(found(), found(-3), -1) == r.NOT_JUDGED
    assert r.justness(found(-6), found(-7), -1) == r.NOT_JUDGED
    assert r.justness(found(0), found(1), 1) == r.NOT_JUDGED
    unread = {**found(), -2: r.NOT_READ}
    assert r.justness(found(-1), unread, -1) == r.NOT_JUDGED


def test_the_jumps_of_a_side_are_judged_in_order_and_tallied():
    surfaces = [found(0), found(-1), found(-2), found(-4)]
    got = r.judge_jumps(surfaces, "moins")
    assert got == [r.RIGHT, r.RIGHT, r.WRONG_ANOTHER_TURN]
    assert r.tally(got + [r.NOT_JUDGED]) == {"judged": 3, "right": 2, "share": 0.6667}
    assert r.tally([r.NOT_JUDGED]) == {"judged": 0, "right": 0, "share": None}
    assert r.judge_jumps([found(-2), found(-1)], "plus") == [r.RIGHT]


def test_the_vertices_read_are_those_inside_the_box_of_the_surface_widened():
    turn = flat_turn(0.0, 100)
    vertices, _ = r.nearby_vertices(turn, np.array([[100.0, 100.0, 0.0], [200.0, 200.0, 0.0]]))
    assert vertices[:, 0].min() == 0.0 and vertices[:, 0].max() == 300.0 and len(vertices) == 31 * 31
    assert len(r.nearby_vertices(turn, np.zeros((0, 3)))[0]) == 0


def test_the_seeds_are_valid_with_a_normal_and_away_from_the_edge_and_spread_over_the_candidates():
    valid = np.ones((60, 80), dtype=bool)
    has_normal = np.ones((60, 80), dtype=bool)
    got = seeds.choose_seeds(valid, has_normal)
    assert len(got) == 8 and all(8 <= i < 52 and 8 <= j < 72 for i, j in got) and len(set(got)) == 8
    has_normal[:, :40] = False
    assert all(j >= 40 for _, j in seeds.choose_seeds(valid, has_normal))
    assert seeds.choose_seeds(np.zeros((60, 80), dtype=bool), has_normal) == []
    assert seeds.choose_seeds(valid[:10, :10], has_normal[:10, :10]) == []


def _array(volume: np.ndarray, chunk, absent=(), unreadable=()):
    import json
    url = "https://example.invalid/m7.zarr"
    bodies = {f"{url}/0/.zarray": json.dumps({"shape": list(volume.shape), "chunks": list(chunk), "dtype": "|u1",
                                              "compressor": None, "fill_value": 0, "order": "C",
                                              "dimension_separator": "/"}).encode()}
    grid = [-(-n // c) for n, c in zip(volume.shape, chunk)]
    for i in range(grid[0]):
        for j in range(grid[1]):
            for k in range(grid[2]):
                if (i, j, k) in absent:
                    continue
                block = np.zeros(chunk, dtype=np.uint8)
                part = volume[i * chunk[0]:(i + 1) * chunk[0], j * chunk[1]:(j + 1) * chunk[1], k * chunk[2]:(k + 1) * chunk[2]]
                block[:part.shape[0], :part.shape[1], :part.shape[2]] = part
                bodies[f"{url}/0/{i}/{j}/{k}"] = b"\x00" if (i, j, k) in unreadable else block.tobytes()
    return RemoteArray(url, InMemoryTransport(bodies), 0)


def test_the_prediction_is_read_at_each_index_in_zyx_across_chunks_and_zero_outside():
    volume = np.random.default_rng(1).integers(1, 255, (10, 12, 14)).astype(np.uint8)
    reader = PredictionReader(_array(volume, (4, 5, 6)))
    index = np.array([[[0, 0, 0], [9, 11, 13]], [[5, 6, 7], [3, 4, 5]], [[-1, 0, 0], [10, 0, 0]]])
    got = reader(index)
    assert got.shape == (3, 2) and got[0, 0] == volume[0, 0, 0] and got[0, 1] == volume[9, 11, 13]
    assert got[1, 0] == volume[5, 6, 7] and got[1, 1] == volume[3, 4, 5] and got[2, 0] == 0 and got[2, 1] == 0
    assert reader(np.zeros((0, 3), dtype=np.int64)).shape == (0,)


def test_a_chunk_absent_from_the_bucket_is_empty_and_one_that_cannot_be_read_stops_the_reading():
    volume = np.full((8, 8, 8), 7, dtype=np.uint8)
    absent = PredictionReader(_array(volume, (4, 4, 4), absent=((0, 0, 0),)))
    assert absent(np.array([[1, 1, 1], [5, 5, 5]])).tolist() == [0, 7]
    broken = PredictionReader(_array(volume, (4, 4, 4), unreadable=((0, 0, 0),)))
    with pytest.raises(RuntimeError, match="could not be read"):
        broken(np.array([[1, 1, 1]]))


def test_a_chunk_is_read_once_while_it_is_kept():
    reader = PredictionReader(_array(np.ones((8, 8, 8), dtype=np.uint8), (4, 4, 4)), kept=2)
    reader(np.array([[1, 1, 1], [2, 2, 2]]))
    reader(np.array([[1, 1, 1]]))
    assert reader.reads == 1
    reader(np.array([[5, 1, 1], [1, 5, 1]]))
    reader(np.array([[1, 1, 1]]))
    assert reader.reads == 4


@research
def test_the_coincidence_and_the_justness_are_the_research_s():
    from la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies import les_lectures as research_readings
    from la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 import la_coincidence as research_coincidence
    from le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux import la_justesse as research_justness
    rng = np.random.default_rng(2)
    for scale in (1.0, 3.0, 30.0):
        gaps = rng.normal(0.0, scale, 120)
        gaps[::7] = np.nan
        theirs = research_coincidence(gaps)
        ours = r.coincidence(gaps)
        assert ours["facing"] == theirs["les_sommets_en_face"] and ours["reading"] == {
            "retrouve": r.FOUND, "ne retrouve pas": r.NOT_FOUND, "non lue": r.NOT_READ}[theirs["la_lecture"]]
    tours = {k: {"points": t.points, "normales": t.normals} for k, t in TURNS_AT.items()}
    points = surface_at(1.0)
    theirs = research_readings(points, tours)
    assert {k: {"retrouve": r.FOUND, "ne retrouve pas": r.NOT_FOUND, "non lue": r.NOT_READ}[v["la_lecture"]]
            for k, v in theirs.items()} == r.read_against(points, TURNS_AT)
    words = {"retrouve": r.FOUND, "ne retrouve pas": r.NOT_FOUND, "non lue": r.NOT_READ}
    cases = [(found(-1), found(-2)), (found(-1), found(-2, -3)), (found(-1), found(-4)), (found(-1), found()),
             (found(-1, -2), found(-3)), (found(-6), found(-7)), (found(-1), {**found(), -2: r.NOT_READ}), (found(0), found(-1))]
    back = {v: k for k, v in words.items()}
    for before, after in cases:
        for sense in (1, -1):
            french = lambda s: {t: back[x] for t, x in s.items()}  # noqa: E731
            expected = research_justness(french(before), french(after), sense)
            got = r.justness(before, after, sense)
            assert {"juste": r.RIGHT, "non jugé": r.NOT_JUDGED, "faux : deux tours": r.WRONG_TWO_TURNS,
                    "faux : un autre tour": r.WRONG_ANOTHER_TURN, "faux : le tour manqué": r.WRONG_MISSED_TURN}[expected] == got


@research
def test_the_seeds_are_the_research_s_on_the_reduced_mesh_of_the_segment():
    import tifffile
    from la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 import les_graines as research_seeds
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz
    folder = DATA / "rendu_spire_voisine" / "le_segment_reduit" / "maillage"
    if not folder.is_dir():
        pytest.skip(f"the research's reduced mesh is not under {DATA}")
    points, valid, _ = lire_tifxyz(folder)
    n, has_normal = les_normales(points, valid)
    assert seeds.choose_seeds(valid, has_normal) == research_seeds(points, valid, has_normal) and len(research_seeds(points, valid, has_normal)) == 8
    assert tifffile is not None


@research
def test_the_published_windings_are_read_as_the_research_reads_them():
    from la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies import lire_un_tour as research_turn
    if not (PUBLISHED / TURNS[-3]).is_dir():
        pytest.skip(f"the published windings are not under {PUBLISHED}")
    ours = r.read_turn(PUBLISHED / TURNS[-3])
    theirs = research_turn(-3)
    assert np.array_equal(ours.points, theirs["points"]) and np.array_equal(ours.normals, theirs["normales"])


def test_a_vertex_with_no_surface_within_40_voxels_sideways_does_not_face_it():
    """One point of surface, vertices 45 voxels apart: only the ones within 40 voxels sideways face it, and they are too few to
    read the winding; with a lateral reach of 80 they would."""
    turns = {0: flat_turn(0.0, 10, 45.0)}
    assert r.read_against(np.array([[200.0, 200.0, 1.0]]), turns) == {0: r.NOT_READ}
    assert r.LATERAL == 40.0
