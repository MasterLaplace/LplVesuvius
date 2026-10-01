"""The chain of windings (`R4-F543`, `R4-F551`): what each jump keeps, and what the next jump starts from. The order of its
decisions on injected operations, offline; the whole chain against the research's on fabricated sheets with
`VESUVE_RESEARCH`."""
from __future__ import annotations

import numpy as np
import pytest

from conftest import research
from vesuve.chain import chain as ch
from vesuve.chain import criterion, growth
from vesuve.chain.surface import Surface

GOOD = {"points": 100, "in_front": 100, "counted": 100, "counts": {"1": 100}, "one_sheet_share": 1.0}
BAD = {"points": 100, "in_front": 100, "counted": 100, "counts": {"0": 90, "1": 10}, "one_sheet_share": 0.1}


def plane(z: float, n: int = 11) -> Surface:
    grid = np.zeros((n, n, 3))
    for a in range(n):
        for b in range(n):
            grid[a, b] = (10.0 * b, 10.0 * a, z)
    return Surface(grid, np.ones((n, n), dtype=bool))


def jump_up(surface: Surface) -> growth.Jump:
    return growth.Jump(Surface(surface.points + np.array([0.0, 0.0, 20.0]), surface.valid.copy()),
                       np.full(surface.valid.shape, 20.0), (5, 5), np.full(surface.valid.shape, 20.0))


class Recorder:
    def __init__(self, counts):
        self.counts, self.relaunches, self.regrowths, self.departures = list(counts), [], [], []

    def operations(self, with_regrowth: bool = False):
        def relaunch(point, normal):
            self.relaunches.append(point)
            return growth.Grown(plane(float(point[2])), np.zeros((11, 11)), np.zeros((11, 11), dtype=bool))

        def regrow(winding, point, normal):
            self.regrowths.append(point)
            return growth.Grown(plane(float(point[2]) + 0.0), np.zeros((11, 11)), np.zeros((11, 11), dtype=bool))

        def count(departure, arrival):
            self.departures.append(float(departure.points[0, 0, 2]))
            return self.counts[(len(self.departures) - 1) % len(self.counts)]
        return ch.Operations(jump_up, relaunch, regrow if with_regrowth else None, count)


def test_a_winding_the_criterion_holds_is_kept_and_the_next_jump_starts_from_it():
    r = Recorder([GOOD])
    chain = ch.grow_chain(plane(0.0), r.operations(), jumps=3)
    assert [k.origin for k in chain] == [ch.FROM_THE_WINDING] * 3 and not r.relaunches
    assert r.departures == [0.0, 20.0, 40.0] and ch.held_in_a_row(chain) == 3
    assert all(k.holds for k in chain) and chain[2].points == 121


def test_a_winding_the_criterion_refuses_is_relaunched_from_its_seed_and_that_is_counted_and_continues():
    r = Recorder([BAD])
    chain = ch.grow_chain(plane(0.0), r.operations(), jumps=3)
    assert [k.origin for k in chain] == [ch.FROM_A_RELAUNCH] * 3 and len(r.relaunches) == 3
    assert chain[0].count == BAD and chain[0].winding_count == BAD and ch.held_in_a_row(chain) == 0
    assert r.departures[::2] == [0.0, 20.0, 40.0]


def test_a_winding_refused_then_a_relaunch_held_counts_the_surface_kept_and_not_the_winding():
    appels = [BAD, GOOD]
    r = Recorder(appels)
    chain = ch.grow_chain(plane(0.0), r.operations(), jumps=1)
    assert chain[0].origin == ch.FROM_A_RELAUNCH and chain[0].count == GOOD and chain[0].winding_count == BAD
    assert chain[0].holds and ch.held_in_a_row(chain) == 1


def test_a_held_winding_is_grown_again_and_the_regrowth_is_kept_if_it_is_held_too():
    r = Recorder([GOOD])
    chain = ch.grow_chain(plane(0.0), r.operations(with_regrowth=True), jumps=2)
    assert [k.origin for k in chain] == [ch.FROM_THE_REGROWTH] * 2 and len(r.regrowths) == 2
    assert r.departures == [0.0, 0.0, 20.0, 20.0]


def test_a_regrowth_that_is_not_held_leaves_the_winding_kept():
    r = Recorder([GOOD, BAD])
    chain = ch.grow_chain(plane(0.0), r.operations(with_regrowth=True), jumps=1)
    assert chain[0].origin == ch.FROM_THE_WINDING and chain[0].count == GOOD and len(r.regrowths) == 1


def test_a_winding_with_nothing_laid_ends_the_chain():
    empty = lambda surface: growth.Jump(Surface(surface.points, np.zeros_like(surface.valid)), np.full((11, 11), np.nan), None,  # noqa: E731
                                        np.full((11, 11), np.nan))
    chain = ch.grow_chain(plane(0.0), ch.Operations(empty, None, None, lambda d, a: GOOD), jumps=3)
    assert len(chain) == 1 and chain[0].origin is None and chain[0].points == 0 and chain[0].kept is None
    assert chain[0].count == criterion.summarise(None) and not chain[0].holds and ch.held_in_a_row(chain) == 0


def test_a_relaunch_with_nothing_laid_ends_the_chain():
    r = Recorder([BAD])
    ops = r.operations()
    nothing = lambda point, normal: growth.Grown(Surface(plane(0.0).points, np.zeros((11, 11), dtype=bool)),  # noqa: E731
                                                  np.zeros((11, 11)), np.zeros((11, 11), dtype=bool))
    chain = ch.grow_chain(plane(0.0), ch.Operations(ops.jump, nothing, None, ops.count), jumps=5)
    assert len(chain) == 1 and chain[0].origin == ch.FROM_A_RELAUNCH and chain[0].points == 0


def test_the_relaunch_seed_is_the_laid_point_with_a_normal_nearest_the_barycentre():
    surface = plane(5.0, 9)
    point, normal = ch.relaunch_seed(surface)
    assert np.allclose(point, (40.0, 40.0, 5.0)) and np.allclose(normal, (0.0, 0.0, 1.0))
    assert ch.relaunch_seed(Surface(surface.points, np.zeros((9, 9), dtype=bool))) is None


def test_held_in_a_row_stops_at_the_first_refused_jump():
    """The third jump leaves the surface at height 40: its winding is refused, relaunched, and the relaunch is refused too;
    the fourth, from 60, is held again; only the first two are in a row."""
    r = Recorder([GOOD])
    ops = r.operations()
    refuse_at_40 = lambda departure, arrival: BAD if abs(departure.points[0, 0, 2] - 40.0) < 1e-9 else GOOD  # noqa: E731
    chain = ch.grow_chain(plane(0.0), ch.Operations(ops.jump, ops.relaunch, None, refuse_at_40), jumps=4)
    assert [k.holds for k in chain] == [True, True, False, True] and ch.held_in_a_row(chain) == 2


def test_the_margin_of_a_chain_is_one_mesh():
    assert ch.MARGIN == 1 and ch.JUMPS == 8


def layered(step: float, wobble: float, missing=None):
    def read(index: np.ndarray) -> np.ndarray:
        z, y, x = (index[..., k].astype(float) for k in range(3))
        shift = wobble * np.sin(x / 47.0) * np.cos(y / 61.0)
        phase = (z - 120.0 - shift) / step
        sheet = (np.abs(phase - np.rint(phase)) * step) <= 1.3
        if missing is not None:
            sheet &= ~missing(np.rint(phase), x)
        return sheet.astype(np.uint8)
    return read


def _research_chain(read, side, regrow, margin):
    import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle  # noqa: F401
    import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306
    import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357
    import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321
    import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322
    import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333
    import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356
    seed = (500.0, 300.0, 120.0)
    start = m322.la_nappe_de_paris4(seed, (0.0, 0.0, 1.0), read)

    def jump(surface, valid):
        with m321.le_rouleau_de_paris4():
            return m306.le_saut_croissant(surface, valid, side, read, tolerance=m322.LA_TOLERANCE_L2)
    relaunch = lambda p, n: m322.la_nappe_de_paris4(p, n, read)  # noqa: E731
    regrower = (lambda p, n, s, o: m333.la_nappe_de_la_spire_de_paris4(s, o, p, n, read, marge=margin)) if regrow else None
    return start, m356.la_chaine_mixte(start, relaunch, jump, read, compter=m357.compter4, regrandir=regrower)


@research
@pytest.mark.parametrize("side,regrow,missing", [
    (1.0, True, None), (-1.0, True, None), (1.0, False, None),
    (1.0, True, lambda k, x: (k == 4) & ((x < 470) | (x > 520)))])
def test_the_chain_is_the_research_s_jump_for_jump(side, regrow, missing):
    read = layered(growth.PHERCPARIS4.step, 4.0, missing)
    start, theirs = _research_chain(read, side, regrow, 1)
    ours = ch.grow_chain(Surface(start["la_nappe"], start["valide"]),
                         ch.operations_for(read, growth.PHERCPARIS4, side, regrowth=regrow))
    assert len(ours) == len(theirs) > 3
    summary = lambda c: {"points": c["les_points"], "in_front": c["les_en_face"], "counted": c["les_mesures"],  # noqa: E731
                         "counts": c["les_comptes"], "one_sheet_share": c["la_part_dune_feuille"]}
    origins = {"the winding": "la spire", "the regrowth": "la croissance", "a relaunch": "la relance", None: None}
    for mine, other in zip(ours, theirs):
        assert origins[mine.origin] == other["depuis"] and mine.points == other["les_points"]
        assert mine.winding_count == summary(other["le_compte_de_la_spire"]) and mine.count == summary(other["le_compte"])
        assert np.array_equal(mine.jump.surface.points, other["le_saut"]["la_spire"])
        assert np.array_equal(mine.departure.points, other["le_depart"]["la_nappe"])
        if other["la_relance"] is not None:
            assert np.array_equal(mine.kept.points, other["la_relance"]["la_nappe"])
            assert np.array_equal(mine.kept.valid, other["la_relance"]["valide"])
    assert sum(k.points for k in ours) > 0 and (regrow or {k.origin for k in ours} <= {ch.FROM_THE_WINDING, ch.FROM_A_RELAUNCH})


@research
def test_the_chains_of_the_fabricated_world_exercise_every_decision():
    seen = set()
    for side, regrow, missing in ((1.0, True, None), (1.0, True, lambda k, x: (k == 4) & ((x < 470) | (x > 520)))):
        read = layered(growth.PHERCPARIS4.step, 4.0, missing)
        start, _ = _research_chain(read, side, regrow, 1)
        seen |= {k.origin for k in ch.grow_chain(Surface(start["la_nappe"], start["valide"]),
                                                 ch.operations_for(read, growth.PHERCPARIS4, side))}
    assert seen >= {ch.FROM_THE_REGROWTH, ch.FROM_A_RELAUNCH}, seen
