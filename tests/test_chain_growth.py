"""Growing a surface from `m7`, jumping to the next winding, and growing a held winding again by one mesh (`R4-F551`).
Offline on fabricated sheets; against the research's functions with `VESUVE_RESEARCH`."""
from __future__ import annotations

import numpy as np
import pytest

from conftest import research
from vesuve.chain import growth as g
from vesuve.chain.surface import Surface

SCALE = g.PHERCPARIS4
SEED = (500.0, 300.0, 120.0)
UP = np.array([0.0, 0.0, 1.0])


def layered(step: float = SCALE.step, wobble: float = 0.0, base: float = 120.0, thickness: float = 2.5):
    """A prediction of parallel sheets `step` apart, whose height wobbles with x and y by `wobble` voxels."""
    def read(index: np.ndarray) -> np.ndarray:
        z, y, x = (index[..., k].astype(float) for k in range(3))
        shift = wobble * np.sin(x / 47.0) * np.cos(y / 61.0)
        return (((z - base - shift) % step) < thickness).astype(np.uint8)
    return read


def flat_plane(z: float, n: int = 31, spacing: float = 10.0, x0: float = 350.0, y0: float = 150.0) -> Surface:
    grid = np.zeros((n, n, 3))
    for a in range(n):
        for b in range(n):
            grid[a, b] = (x0 + spacing * b, y0 + spacing * a, z)
    return Surface(grid, np.ones((n, n), dtype=bool))


def test_the_plane_is_perpendicular_to_the_normal_and_centred_on_the_seed():
    grid, n = g.plane(SEED, (0.0, 0.0, 5.0))
    assert grid.shape == (65, 65, 3) and np.allclose(n, UP) and np.allclose(grid[32, 32], SEED)
    assert np.allclose(grid[..., 2], 120.0) and np.isclose(np.linalg.norm(grid[0, 1] - grid[0, 0]), 10.0)
    tilted, n = g.plane(SEED, (1.0, 2.0, 3.0))
    assert np.isclose(np.linalg.norm(n), 1.0) and np.allclose((tilted.reshape(-1, 3) - SEED) @ n, 0.0)


def test_the_centres_of_the_runs_along_each_ray():
    seen = np.zeros((2, 11), dtype=bool)
    seen[0, 2:5] = True
    seen[0, 8:10] = True
    depths = np.arange(-5.0, 6.0)
    first, second = g.sheet_centres(seen, depths)
    assert np.allclose(first, [-2.0, 3.5]) and len(second) == 0


def test_the_sheet_after_its_own_is_the_first_run_beyond_the_one_at_depth_zero():
    depths = np.arange(0.0, 41.0)
    seen = np.zeros((3, 41), dtype=bool)
    seen[0, 0:3] = True
    seen[0, 18:21] = True
    seen[1, 18:21] = True
    seen[1, 36:39] = True
    got = g.sheet_after_own(depths, seen)
    assert got[0] == 19.0 and got[1] == 19.0 and np.isnan(got[2])


def test_a_ray_that_sees_its_own_sheet_takes_the_run_after_it_and_one_that_does_not_the_first_beyond_three_voxels():
    depths = np.arange(0.0, 41.0)
    own_and_next = np.zeros((1, 41), dtype=bool)
    own_and_next[0, 0:3] = True
    own_and_next[0, 18:21] = True
    next_only = np.zeros((1, 41), dtype=bool)
    next_only[0, 18:21] = True
    not_own = np.zeros((1, 41), dtype=bool)
    not_own[0, 5:9] = True
    not_own[0, 20:23] = True
    assert g.sheet_after_own(depths, own_and_next)[0] == 19.0 and g.sheet_after_own(depths, next_only)[0] == 19.0
    assert g.sheet_after_own(depths, not_own)[0] == 6.5


def test_the_growth_from_a_seed_lays_the_whole_plane_on_a_flat_sheet():
    grown = g.grow_from_seed(SEED, UP, layered(), SCALE)
    assert grown.surface.valid.all() and np.allclose(grown.surface.points[..., 2], 121.0, atol=1.0)
    assert not grown.seeded.any()


def test_the_growth_stops_where_the_sheet_is_further_than_a_quarter_step_from_what_its_neighbours_found():
    def torn(index):
        z, x = index[..., 0], index[..., 2]
        return ((np.abs(z - 120) <= 1) & (x < 500) | (np.abs(z - 134) <= 1) & (x >= 500)).astype(np.uint8)
    grown = g.grow_from_seed(SEED, UP, torn, SCALE)
    assert grown.surface.valid[:33].all() and not grown.surface.valid[34:].any()


def test_a_jump_goes_to_the_next_sheet_along_the_normal_on_either_side():
    surface = flat_plane(121.0)
    up = g.jump(surface, 1.0, layered(), SCALE)
    down = g.jump(surface, -1.0, layered(), SCALE)
    interior = np.zeros((31, 31), dtype=bool)
    interior[1:-1, 1:-1] = True       # the border has no normal
    assert np.array_equal(up.surface.valid, interior) and np.array_equal(down.surface.valid, interior)
    assert np.allclose(up.surface.points[interior][:, 2], 139.5, atol=0.5)
    assert np.allclose(down.surface.points[interior][:, 2], 103.0, atol=0.5)
    assert up.start == (15, 15) and np.allclose(up.steps[interior], 18.5, atol=0.5)


def test_a_jump_where_no_ray_sees_a_next_sheet_gives_nothing():
    got = g.jump(flat_plane(120.0), 1.0, lambda index: np.zeros(index.shape[:-1]), SCALE)
    assert not got.surface.valid.any() and got.start is None and np.isnan(got.steps).all()


def _patch(side: int):
    small = np.zeros((65, 65), dtype=bool)
    small[32 - side:32 + side + 1, 32 - side:32 + side + 1] = True
    return small


def _winding_on_the_plane() -> Surface:
    grid, _ = g.plane(SEED, UP)
    laid = _patch(2)
    return Surface(grid + np.array([0.0, 0.0, 1.0]), laid)


@pytest.mark.parametrize("margin,cells", [(0, 25), (1, 49), (2, 81)])
def test_the_regrowth_lays_the_seeds_and_the_margin_around_them_and_nothing_more(margin, cells):
    """Five by five seeds on a flat sheet: a margin of one mesh gives 7 × 7, two meshes 9 × 9 (the regrowth of `335`)."""
    grown = g.regrow(_winding_on_the_plane(), SEED, UP, layered(), SCALE, margin=margin)
    assert grown.surface.valid.sum() == cells and grown.seeded.sum() == 25 and grown.touched == 25
    assert grown.surface.valid[32 - 2 - margin:32 + 3 + margin, 32 - 2 - margin:32 + 3 + margin].all()


def test_without_a_margin_the_regrowth_lays_the_whole_plane():
    grown = g.regrow(_winding_on_the_plane(), SEED, UP, layered(), SCALE)
    assert grown.surface.valid.all()


def test_a_point_of_the_winding_on_no_sheet_seeds_nothing():
    grid, _ = g.plane(SEED, UP)
    off_sheet = Surface(grid + np.array([0.0, 0.0, 9.0]), _patch(2))
    grown = g.regrow(off_sheet, SEED, UP, layered(), SCALE, margin=1)
    assert not grown.seeded.any() and not grown.surface.valid.any()


def test_each_cell_takes_the_laid_point_that_falls_nearest_its_centre_and_the_first_on_a_tie():
    grid, n = g.plane(SEED, UP)
    points = np.zeros((2, 2, 3))
    points[0, 0] = grid[10, 10] + np.array([0.0, 0.0, 7.0])
    points[0, 1] = grid[10, 10] + np.array([2.0, 0.0, 9.0])       # further from the cell's centre, so it loses
    points[1, 0] = grid[20, 20] + np.array([0.0, 0.0, 3.0])
    points[1, 1] = grid[0, 0] + np.array([500.0, 0.0, 0.0])      # outside the plane
    got = g.targets(Surface(points, np.ones((2, 2), dtype=bool)), grid, n)
    assert got[10, 10] == 7.0 and got[20, 20] == 3.0 and np.isfinite(got).sum() == 2


def test_the_cells_allowed_are_within_the_margin_diagonals_counted():
    one = np.zeros((9, 9), dtype=bool)
    one[4, 4] = True
    assert np.array_equal(g.allowed_cells(one, 2), np.pad(np.ones((5, 5), dtype=bool), 2))
    assert np.array_equal(g.allowed_cells(one, 0), one)
    assert not g.allowed_cells(np.zeros((9, 9), dtype=bool), 2).any()


def test_the_scale_of_a_scroll_gives_its_tolerance_and_its_reach():
    assert np.isclose(g.PHERCPARIS4.step, 18.0208, atol=1e-3) and np.isclose(g.PHERCPARIS4.tolerance, 4.5052, atol=1e-3)
    assert np.isclose(g.PHERCPARIS4.half_reach, 27.03, atol=1e-2)
    assert g.PHERC0358.step == 20.0 and g.PHERC0358.tolerance == 5.0 and g.PHERC0358.half_reach == 30.0


def _undulating():
    return layered(wobble=4.0)


@research
def test_the_growth_from_a_seed_is_the_research_s_at_both_scrolls():
    import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321
    import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322
    import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305
    read = _undulating()
    ours = g.grow_from_seed(SEED, np.array([0.0, 0.0, 1.0]), read, g.PHERCPARIS4)
    theirs = m322.la_nappe_de_paris4(SEED, np.array([0.0, 0.0, 1.0]), read)
    assert np.array_equal(ours.surface.points, theirs["la_nappe"]) and np.array_equal(ours.surface.valid, theirs["valide"])
    assert np.array_equal(ours.offsets, theirs["le_decalage"], equal_nan=True) and ours.surface.valid.sum() > 1000
    read0 = layered(step=20.0, wobble=4.0)
    ours0 = g.grow_from_seed(SEED, np.array([0.0, 0.0, 1.0]), read0, g.PHERC0358)
    theirs0 = m305.la_nappe_croissante(SEED, np.array([0.0, 0.0, 1.0]), read0)
    assert np.array_equal(ours0.surface.points, theirs0["la_nappe"]) and np.array_equal(ours0.surface.valid, theirs0["valide"])
    assert m321.LE_PAS_L2 == g.PHERCPARIS4.step


@research
@pytest.mark.parametrize("margin", [None, 1, 2])
def test_the_regrowth_is_the_research_s_with_and_without_a_margin(margin):
    import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333
    read = _undulating()
    seed_grown = g.grow_from_seed(SEED, UP, read, SCALE)
    patch = Surface(seed_grown.surface.points, _patch(6))
    ours = g.regrow(patch, SEED, UP, read, SCALE, margin=margin)
    theirs = m333.la_nappe_de_la_spire_de_paris4(patch.points, patch.valid, SEED, UP, read, marge=margin)
    assert np.array_equal(ours.surface.points, theirs["la_nappe"]) and np.array_equal(ours.surface.valid, theirs["valide"])
    assert np.array_equal(ours.seeded, theirs["les_semes"]) and ours.touched == theirs["les_mailles_touchees"]
    assert ours.seeded.sum() == theirs["les_semis"] == 169
    assert ours.surface.valid.sum() > 169


@research
def test_the_jump_is_the_research_s_on_both_sides_at_both_scrolls():
    import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306
    import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321
    import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322
    surface = flat_plane(120.0)
    surface = Surface(surface.points + np.stack([np.zeros((31, 31)), np.zeros((31, 31)),
                                                 2.0 * np.sin(np.arange(31) / 5.0)[None, :].repeat(31, 0)], axis=-1),
                      surface.valid)
    for side in (1.0, -1.0):
        read = _undulating()
        ours = g.jump(surface, side, read, g.PHERCPARIS4)
        with m321.le_rouleau_de_paris4():
            theirs = m306.le_saut_croissant(surface.points, surface.valid, side, read, tolerance=m322.LA_TOLERANCE_L2)
        assert np.array_equal(ours.surface.points, theirs["la_spire"]) and np.array_equal(ours.surface.valid, theirs["valide"])
        assert np.array_equal(ours.steps, theirs["le_pas"], equal_nan=True) and list(ours.start) == theirs["le_depart"]
        assert np.array_equal(ours.next_sheets, theirs["les_suivantes"], equal_nan=True) and ours.surface.valid.sum() > 500
        read0 = layered(step=20.0, wobble=4.0)
        ours0 = g.jump(surface, side, read0, g.PHERC0358)
        theirs0 = m306.le_saut_croissant(surface.points, surface.valid, side, read0)
        assert np.array_equal(ours0.surface.points, theirs0["la_spire"]) and np.array_equal(ours0.surface.valid, theirs0["valide"])


def test_a_cell_aims_at_the_median_of_its_laid_neighbours_not_their_mean():
    """Seven neighbours at 0 and one outlier at 18: the median is 0, the mean 2.25. A sheet at 4 is out of reach of the
    median within 2.1 and in reach of the mean."""
    offsets = np.zeros((3, 3))
    offsets[0, 0] = 18.0
    laid = np.ones((3, 3), dtype=bool)
    laid[1, 1] = False
    centres = [np.array([0.0])] * 9
    centres[4] = np.array([4.0])
    _, laid_after = g.extend(centres, (3, 3), offsets.copy(), laid.copy(), tolerance=2.1)
    assert not laid_after[1, 1]
    centres[4] = np.array([0.5])
    _, laid_after = g.extend(centres, (3, 3), offsets.copy(), laid.copy(), tolerance=2.1)
    assert laid_after[1, 1]


def test_two_points_of_the_winding_in_the_same_cell_give_the_first_in_the_order_of_the_winding():
    grid, n = g.plane(SEED, UP)
    points = np.stack([grid[10, 10] + np.array([0.0, 0.0, 7.0]), grid[10, 10] + np.array([0.0, 0.0, 9.0])])[None]
    got = g.targets(Surface(points, np.ones((1, 2), dtype=bool)), grid, n)
    assert got[10, 10] == 7.0
