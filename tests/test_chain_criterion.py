"""The criterion that needs no referent (`R4-F531`, `R4-F538`): the sheets of `m7` a jump crosses, point by point, and the
zero threshold. Offline on fabricated surfaces; against the research's functions with `VESUVE_RESEARCH`."""
from __future__ import annotations

import numpy as np
import pytest

from conftest import research
from vesuve.chain import criterion as c
from vesuve.chain.surface import Surface

STEP = 18.0


def plane(z: float, n: int = 11, spacing: float = 10.0) -> Surface:
    grid = np.zeros((n, n, 3))
    for a in range(n):
        for b in range(n):
            grid[a, b] = (spacing * b, spacing * a, z)
    return Surface(grid, np.ones((n, n), dtype=bool))


def sheets_at(*heights: float, thickness: float = 1.0):
    """A prediction with a sheet of `thickness` voxels each side at each height, whatever x and y are."""
    def read(index: np.ndarray) -> np.ndarray:
        z = index[..., 0]
        return sum((np.abs(z - h) <= thickness).astype(float) for h in heights)
    return read


def test_the_next_sheet_is_one_sheet_crossed_and_the_same_sheet_is_none():
    seen = np.zeros(21, dtype=bool)
    depths = np.arange(-10.0, 11.0)
    seen[9:12] = True
    seen[18:21] = True
    assert c.sheets_between(seen, depths, 8.0, 2.0) == 1
    assert c.sheets_between(seen, depths, 0.5, 2.0) == 0
    seen[14] = True
    assert c.sheets_between(seen, depths, 9.0, 2.0) == 2


def test_an_end_with_no_run_at_a_quarter_step_is_not_counted_and_a_ray_without_sheet_neither():
    depths = np.arange(-10.0, 11.0)
    seen = np.zeros(21, dtype=bool)
    assert c.sheets_between(seen, depths, 8.0, 2.0) is None
    seen[9:12] = True
    assert c.sheets_between(seen, depths, 8.0, 2.0) is None
    assert c.sheets_between(seen, depths, 8.0, 12.0) == 0


def test_a_point_with_no_departure_point_in_front_of_it_has_no_gap():
    departure = np.array([[0.0, 0.0, 10.0], [100.0, 0.0, 10.0]])
    arrival, normal = np.array([[0.0, 0.0, 0.0], [50.0, 0.0, 0.0]]), np.array([[0.0, 0.0, 1.0]] * 2)
    got = c.gaps_to(departure, arrival, normal, lateral=20.0)
    assert got[0] == 10.0 and np.isnan(got[1])
    assert np.isnan(c.gaps_to(departure[:0], arrival, normal, 20.0)).all()


def test_a_jump_to_the_next_sheet_crosses_one_and_is_held():
    got = c.count_and_summarise(plane(0.0), plane(STEP), sheets_at(0.0, STEP), STEP)
    assert got["counts"] == {"1": 81} and got["one_sheet_share"] == 1.0 and got["counted"] == 81
    assert c.crosses_one_sheet(got) and c.holds(got)


def test_a_jump_over_a_sheet_crosses_two_and_is_not_held():
    got = c.count_and_summarise(plane(0.0), plane(2 * STEP), sheets_at(0.0, STEP, 2 * STEP), STEP)
    assert got["counts"] == {"2": 81} and not c.crosses_one_sheet(got) and not c.holds(got)


def test_a_jump_that_stays_on_its_sheet_crosses_none_and_is_not_held():
    got = c.count_and_summarise(plane(0.0), plane(0.5), sheets_at(0.0, STEP), STEP)
    assert got["counts"] == {"0": 81} and not c.holds(got)


def test_fewer_than_fifty_counted_points_do_not_hold():
    got = c.count_and_summarise(plane(0.0, 6), plane(STEP, 6), sheets_at(0.0, STEP), STEP)
    assert got["counted"] == 16 and got["one_sheet_share"] == 1.0 and not c.crosses_one_sheet(got)


def test_a_jump_that_crosses_one_sheet_but_leaves_fifty_points_at_zero_is_not_held():
    """The zero threshold does most of the work (`R4-F538`): 100 points on the same sheet of 1100 counted is 91 % at one,
    and the threshold alone refuses it."""
    summary = {"points": 1200, "in_front": 1200, "counted": 1200, "counts": {"0": 100, "1": 1100}, "one_sheet_share": 0.9167}
    assert c.crosses_one_sheet(summary) and not c.holds(summary)
    below = {**summary, "counts": {"0": 49, "1": 1151}, "one_sheet_share": 0.9592}
    assert c.holds(below)
    assert not c.holds({**below, "counts": {"0": 50, "1": 1150}})


def test_three_quarters_of_the_counted_points_must_cross_one_sheet():
    counted = {"points": 100, "in_front": 100, "counted": 100}
    assert c.crosses_one_sheet({**counted, "counts": {"1": 75, "2": 25}, "one_sheet_share": 0.75})
    assert not c.crosses_one_sheet({**counted, "counts": {"1": 74, "2": 26}, "one_sheet_share": 0.74})


def test_the_count_takes_at_most_1200_points_spread_over_the_grid():
    got = c.count_sheets(plane(0.0, 40), plane(STEP, 40), sheets_at(0.0, STEP), STEP)
    assert len(got.points) == c.MAXIMUM_POINTS and got.cells[0] == 41 and got.cells[-1] == 40 * 38 + 38
    assert len(np.unique(got.cells)) == c.MAXIMUM_POINTS


def test_a_surface_with_no_point_laid_gives_no_count():
    empty = Surface(plane(0.0).points, np.zeros((11, 11), dtype=bool))
    assert c.count_sheets(plane(0.0), empty, sheets_at(0.0), STEP) is None
    assert c.count_sheets(empty, plane(STEP), sheets_at(0.0), STEP) is None
    assert c.count_sheets(plane(0.0), None, sheets_at(0.0), STEP) is None
    assert c.summarise(None) == {"points": 0, "in_front": 0, "counted": 0, "counts": {}, "one_sheet_share": None}


def test_the_count_reads_the_prediction_in_z_y_x_along_the_normal():
    seen_at = []

    def read(index: np.ndarray) -> np.ndarray:
        seen_at.append(index)
        return sheets_at(0.0, STEP)(index)
    c.count_sheets(plane(0.0), plane(STEP), read, STEP)
    index = seen_at[0]
    assert index.shape[-1] == 3 and index.dtype == np.int64
    assert index[..., 0].min() == STEP - 59 and index[..., 0].max() == STEP + 59    # z, 3.25 steps = 59 voxels each side
    assert index[..., 2].min() == 10 and index[..., 2].max() == 90                  # x, the interior of the grid


def _mixed_world(seed: int):
    rng = np.random.default_rng(seed)
    departure, arrival = plane(0.0, 30, 6.0), plane(0.0, 30, 6.0)
    jitter = rng.choice([0.0, STEP, 2 * STEP, 0.5], size=(30, 30), p=[0.1, 0.65, 0.15, 0.1])
    return departure, Surface(arrival.points + np.stack([np.zeros((30, 30)), np.zeros((30, 30)), jitter], axis=-1),
                              arrival.valid), sheets_at(0.0, STEP, 2 * STEP)


@research
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_the_counts_are_the_research_s_on_a_surface_that_crosses_every_number_of_sheets(seed):
    from les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux import (
        les_comptes_point_par_point as research_counts,
        le_resume as research_summary,
        tient as research_tient,
    )
    departure, arrival, read = _mixed_world(seed)
    ours = c.count_sheets(departure, arrival, read, STEP)
    theirs = research_counts({"la_nappe": departure.points, "valide": departure.valid},
                             {"la_nappe": arrival.points, "valide": arrival.valid}, read, STEP)
    assert ours.counts == theirs["les_comptes"] and ours.counts.count(None) < len(ours.counts)
    assert np.array_equal(ours.points, theirs["les_points"]) and np.array_equal(ours.cells, theirs["les_mailles"])
    assert np.array_equal(ours.gaps, theirs["les_ecarts"], equal_nan=True)
    summary = research_summary(theirs)
    assert c.summarise(ours) == {"points": summary["les_points"], "in_front": summary["les_en_face"],
                                 "counted": summary["les_mesures"], "counts": summary["les_comptes"],
                                 "one_sheet_share": summary["la_part_dune_feuille"]}
    assert set(ours.counts) - {None} >= {0, 1, 2}
    assert c.crosses_one_sheet(c.summarise(ours)) == research_tient(summary)


@research
def test_the_criterion_is_the_research_s_threshold_and_all():
    from sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart import tenue as research_holds
    cases = [{"counted": 100, "one_sheet_share": 0.8, "counts": {"1": 80, "0": 20}},
             {"counted": 100, "one_sheet_share": 0.8, "counts": {"1": 80, "0": 50}},
             {"counted": 49, "one_sheet_share": 1.0, "counts": {"1": 49}},
             {"counted": 100, "one_sheet_share": 0.7, "counts": {"1": 70, "2": 30}},
             {"counted": 0, "one_sheet_share": None, "counts": {}}]
    for case in cases:
        theirs = {"les_mesures": case["counted"], "la_part_dune_feuille": case["one_sheet_share"],
                  "les_comptes": case["counts"]}
        assert c.holds(case) == research_holds(theirs)


def test_a_point_whose_sheet_is_further_than_a_quarter_step_from_it_is_not_counted():
    """The arrival sits 5 voxels from the edge of its nearest run, more than a quarter step (4.5): nothing is counted."""
    far = c.count_and_summarise(plane(0.0), plane(STEP + 6.0), sheets_at(0.0, STEP), STEP)
    near = c.count_and_summarise(plane(0.0), plane(STEP + 3.0), sheets_at(0.0, STEP), STEP)
    assert far["counted"] == 0 and far["in_front"] == 81
    assert near["counted"] == 81 and near["counts"] == {"1": 81}
