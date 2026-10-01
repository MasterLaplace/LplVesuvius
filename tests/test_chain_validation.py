"""The chain on the real prediction of PHercParis4, against what the research published and against the research's own
chain (`R4-F543`, `R4-F551`): seeds 4 to 8, both sides, eight jumps, judged strictly against the published windings.

Needs the research's working copy (`VESUVE_RESEARCH`) and its data (`VESUVE_DATA`: the cache of `m7` chunks at level 2, the
reduced mesh of the segment, the published windings). The whole chain takes minutes: `VESUVE_HEAVY=1`.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pytest

import chain_real as real
from conftest import DATA, MEASURES, research
from vesuve.chain import chain as ch
from vesuve.chain import growth, reading, seeds
from vesuve.chain.surface import Surface

MIXED = {"the winding": "la spire", "the regrowth": "la croissance", "a relaunch": "la relance", None: None}
JUSTNESS = {"juste": reading.RIGHT, "non jugé": reading.NOT_JUDGED, "faux : deux tours": reading.WRONG_TWO_TURNS,
            "faux : un autre tour": reading.WRONG_ANOTHER_TURN, "faux : le tour manqué": reading.WRONG_MISSED_TURN}
SIDES = {"plus": 1.0, "moins": -1.0}
CLEAN_SEEDS = (4, 5, 6, 7, 8)

data_here = pytest.mark.skipif(not (DATA / "nappe_paris4" / "m7" / "m7_L2").is_dir(),
                               reason=f"the research's cache of m7 chunks is not under {DATA}")
heavy = pytest.mark.skipif(os.environ.get("VESUVE_HEAVY") != "1", reason="minutes of reading and growing: VESUVE_HEAVY=1")


def start_of(seed_rank: int, reader, mesh):
    points, valid, normal, has_normal = mesh
    i, j = seeds.choose_seeds(valid, has_normal)[seed_rank - 1]
    return growth.grow_from_seed(points[i, j] / real.FACTOR, normal[i, j], reader, growth.PHERCPARIS4)


def readings_of(surface: Surface, turns) -> dict:
    return reading.read_against(surface.points[surface.valid] * real.FACTOR, turns)


@research
@data_here
def test_the_starting_surface_of_each_seed_is_the_research_s():
    import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322
    mesh = real.mesh_of_the_segment(DATA)
    points, valid, normal, has_normal = mesh
    for rank, (i, j) in enumerate(seeds.choose_seeds(valid, has_normal), 1):
        if rank not in (1, 4, 7):
            continue
        ours = start_of(rank, real.reader(DATA), mesh)
        theirs = m322.la_nappe_de_paris4(points[i, j] / real.FACTOR, normal[i, j], _research_reader())
        assert np.array_equal(ours.surface.points, theirs["la_nappe"]) and np.array_equal(ours.surface.valid, theirs["valide"])
        assert ours.surface.valid.sum() > 500


def _research_reader():
    import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321
    import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    prediction = json.loads(real.ZARRAY)
    lire, _ = lecteur_du_depot(prediction, DATA / "nappe_paris4" / "m7", "m7_L2", m321.LA_PREDICTION, 0)
    return lambda idx: m300.lire_m7(idx, (prediction, lire))


def _chains(sides=("plus", "moins"), ranks=tuple(range(1, 9))):
    reader, mesh, turns = real.reader(DATA), real.mesh_of_the_segment(DATA), real.published_turns(DATA)
    for rank in ranks:
        start = start_of(rank, reader, mesh)
        for side in sides:
            operations = ch.operations_for(reader, growth.PHERCPARIS4, SIDES[side])
            links = ch.grow_chain(start.surface, operations)
            surfaces = [readings_of(start.surface, turns)] + [
                readings_of(k.kept, turns) if k.kept is not None else {t: reading.NOT_READ for t in turns} for k in links]
            yield rank, side, start, links, reading.judge_jumps(surfaces, side)


@research
@data_here
@heavy
def test_the_chain_of_seeds_4_to_8_is_the_chain_the_research_published_and_27_of_28_jumps_are_right():
    published = json.loads((MEASURES / "regrandir_dune_seule_maille_evite_il_le_decalage.json").read_text())
    expected = {(c["le_rang"], c["le_cote"]): c["les_sauts"] for c in published["les_cotes"]}
    judged = []
    for rank, side, _, links, justnesses in _chains():
        sauts = expected[(rank, side)]
        assert len(links) == len(sauts), (rank, side)
        for h, (link, saut, just) in enumerate(zip(links, sauts, justnesses), 1):
            where = (rank, side, h)
            assert MIXED[link.origin] == saut["depuis"], where
            assert link.points == saut["les_points"], where
            assert link.holds == saut["tenu"], where
            assert JUSTNESS[saut["la_justesse"]] == just, where
        if rank in CLEAN_SEEDS:
            judged += justnesses
    assert reading.tally(judged) == {"judged": 28, "right": 27, "share": 0.9643}


@research
@data_here
@heavy
@pytest.mark.parametrize("rank", [4, 7])
def test_the_chain_is_the_research_s_surface_for_surface(rank):
    import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306
    import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357
    import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321
    import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322
    import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333
    import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356
    lv = _research_reader()
    mesh = real.mesh_of_the_segment(DATA)
    ours = {side: (start, links) for _, side, start, links, _ in _chains(ranks=(rank,))}
    for side, cote in SIDES.items():
        start, links = ours[side]
        theirs_start = m322.la_nappe_de_paris4(*_seed_of(rank, mesh), lv)
        assert np.array_equal(start.surface.points, theirs_start["la_nappe"])

        def jump(surface, valid, cote=cote):
            with m321.le_rouleau_de_paris4():
                return m306.le_saut_croissant(surface, valid, cote, lv, tolerance=m322.LA_TOLERANCE_L2)
        theirs = m356.la_chaine_mixte(
            theirs_start, lambda p, n: m322.la_nappe_de_paris4(p, n, lv), jump, lv, compter=m357.compter4,
            regrandir=lambda p, n, s, o: m333.la_nappe_de_la_spire_de_paris4(s, o, p, n, lv, marge=1))
        assert len(links) == len(theirs) and len(links) > 3
        for mine, other in zip(links, theirs):
            assert MIXED[mine.origin] == other["depuis"] and mine.points == other["les_points"]
            assert np.array_equal(mine.jump.surface.points, other["le_saut"]["la_spire"])
            if other["la_relance"] is not None:
                assert np.array_equal(mine.kept.points, other["la_relance"]["la_nappe"])
                assert np.array_equal(mine.kept.valid, other["la_relance"]["valide"])


def _seed_of(rank: int, mesh):
    points, valid, normal, has_normal = mesh
    i, j = seeds.choose_seeds(valid, has_normal)[rank - 1]
    return points[i, j] / real.FACTOR, normal[i, j]
