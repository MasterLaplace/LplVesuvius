"""Each primitive of the certificate against the research's, on inputs built for its edge cases.

Ties (two wings of the same area, two third lines at the same distance), holes just beyond what `225` crosses, and
deciding margins of opposite signs: the real segment carries none of them, so made inputs exercise them, and a
coverage test checks that they do. The research speaks French; its outputs go through `vesuve.research`.
"""
from __future__ import annotations

import numpy as np
import pytest

from conftest import research
from vesuve.lattice import certificate as cert
from vesuve.lattice import geometry as geo
from vesuve.lattice import loop
from vesuve.research import VALUES, to_english

pytestmark = research
FRENCH_SIDE = {v: k for k, v in VALUES.items() if k in ("haut", "droite", "bas", "gauche")}


def _presences(n=40):
    """Full presences (ties), holed at random, and holed symmetrically (shifted ties)."""
    rng = np.random.default_rng(7)
    out = []
    for i in range(n):
        gy, gx = int(rng.integers(40, 70)), int(rng.integers(40, 70))
        A = np.ones((gy, gx), dtype=bool)
        if i % 4 == 1:
            for _ in range(int(rng.integers(1, 5))):
                r, c = int(rng.integers(0, gy)), int(rng.integers(0, gx))
                A[r:r + int(rng.integers(1, 6)), c:c + int(rng.integers(1, 6))] = False
        elif i % 4 == 2:  # a hole in the middle of a column: two wings of the same length, shifted
            c = int(rng.integers(gx // 2, gx - 6))
            m = gy // 2
            A[m - 1:m + 2, c] = False
        elif i % 4 == 3:  # a row holed in the middle: two wings of the same width at the top and the bottom
            r = int(rng.integers(gy // 2, gy - 6))
            A[r, gx // 2 - 1:gx // 2 + 2] = False
        out.append(A)
    return out


def test_the_largest_rectangle_is_the_research_one():
    from ou_sarrete_le_segment import le_plus_grand_rectangle
    for A in _presences():
        for k in (3, 5, 9):
            r = le_plus_grand_rectangle(A, k)
            assert geo.largest_rectangle(A, k) == (list(r) if r is not None else None)


def test_two_equal_rectangles_are_decided_as_in_the_research():
    """Two identical halves separated by an empty row or column: same path, same area, and the smallest start
    wins."""
    from ou_sarrete_le_segment import le_plus_grand_rectangle
    for cut in ("row", "column"):
        A = np.ones((61, 61), dtype=bool)
        if cut == "row":
            A[30, :] = False
        else:
            A[:, 30] = False
        theirs = list(le_plus_grand_rectangle(A, 9))
        assert geo.largest_rectangle(A, 9) == theirs
        assert (theirs[0] < 30) if cut == "row" else (theirs[2] < 30)


def test_the_wing_is_the_research_one_ties_included():
    from le_segment_au_dela_du_rectangle_se_relie_t_il import laile, les_tenues
    ties = 0
    for A in _presences():
        for k in (3, 5, 7, 9):
            rect = geo.largest_rectangle(A, 9)
            if rect is None:
                continue
            t = les_tenues(A, k)
            for side in geo.SIDES:
                for excluded in ([], [(rect[3] + 12, 9)], [(rect[0] - 10, 5)]):
                    theirs = laile(A, rect, FRENCH_SIDE[side], k, t, exclues=excluded)["les_coins"]
                    assert geo.wing(A, rect, side, k, geo.holding_table(A, k), excluded=excluded) == theirs
                    ties += int(theirs is not None)
    assert ties > 100


def _built_wings():
    """Wings put by hand: on a full presence, both sides offer a third line at the same distance (the rectangle's
    side must win); with a cut across the whole side of the rectangle, only the outside offers one."""
    out = []
    for side, co in (("right", [10, 60, 30, 45]), ("left", [10, 60, 30, 45]), ("top", [30, 45, 10, 60]),
                     ("bottom", [30, 45, 10, 60])):
        for cut in (False, True):
            A = np.ones((80, 80), dtype=bool)
            if cut:
                r0, r1, c0, c1 = co
                if side == "right":
                    A[35, :c0] = False
                elif side == "left":
                    A[35, c1 + 1:] = False
                elif side == "top":
                    A[r1 + 1:, 35] = False
                else:
                    A[:r0, 35] = False
            out.append((A, co, side))
    return out


def test_the_third_line_is_the_research_one_at_equal_distance():
    from laquelle_des_deux_colonnes_derive import la_troisieme_ligne
    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_tenues
    outcomes = set()
    for A, co, side in _built_wings():
        for k in (3, 5, 9):
            theirs = to_english(la_troisieme_ligne(A, co, FRENCH_SIDE[side], k, les_tenues(A, k)))
            assert geo.third_line(A, co, side, k, geo.holding_table(A, k)) == theirs
            if theirs is not None:
                outcomes.add(theirs["on_rectangle_side"])
    assert outcomes == {True, False}  # both outcomes of the tie are seen


def _holed_steps(rng, corners, k, hole):
    """Steps for the four sides of a loop, with a majority hole of `hole` seams on one side, keyed the research's
    way: `(rangees|colonnes, centre)`."""
    steps = {}
    for direction, centre, start, end, _s, name in loop.loop_sides(corners):
        lines = {}
        for l_ in geo.band_lines(centre, k):
            s = {x: round(float(rng.normal(0.1, 1.5)) * 16) / 16 for x in range(start, end)}
            if name == "right" and hole:
                for x in range(start + 5, start + 5 + hole):
                    s.pop(x, None)
            lines[l_] = s
        steps[("rangees" if direction == geo.ROWS else "colonnes", centre)] = lines
    return steps


@pytest.mark.parametrize("hole", [0, 16, 17, 18, 27])
def test_one_width_is_the_research_one_at_the_edge_of_what_is_crossed(hole):
    from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import une_largeur_du_segment
    rng = np.random.default_rng(hole)
    corners = [10, 70, 20, 90]
    for k in (3, 5, 9):
        steps = _holed_steps(rng, corners, k, hole)
        theirs = to_english(une_largeur_du_segment(steps, corners, k, "le_maillage", 17, 20261105, 99))
        mine = loop.at_one_width_of_the_segment({(VALUES[d], c): v for (d, c), v in steps.items()}, corners, k, 17,
                                                20261105, 99)
        assert mine["closable"] == theirs["closable"] == (hole <= 17)
        if mine["closable"]:
            for key in ("closure_voxels", "under_half_sheet", "step_spread_voxels", "null"):
                assert mine[key] == theirs[key], key


def test_the_verdict_of_the_three_is_the_research_one_margins_mixed():
    from laquelle_des_deux_colonnes_derive import le_verdict_des_trois
    rng = np.random.default_rng(3)
    tl = {"la_ligne": 30, "le_sens": "colonnes", "la_plus_proche": 40, "la_plus_loin": 55,
          "du_cote_du_rectangle": True, "lecart": 10}
    signs = set()
    for _ in range(300):
        by_loop = {n: {"par_largeur": {"9": {"fermable": bool(rng.random() > 0.05),
                                             "la_fermeture_en_voxels": round(float(rng.normal(0, 20)), 4),
                                             "le_nul": {"la_fermeture_mediane_en_valeur_absolue":
                                                        round(float(rng.uniform(0, 15)), 4)}}}}
                   for n in ("laile", "letroite", "la_large")}
        theirs = le_verdict_des_trois(tl, by_loop, 9)
        theirs.pop("ce_qui_reste_a_mesurer", None)
        mine = cert.verdict_of_the_three(to_english(tl), to_english(by_loop), 9)
        assert mine == to_english(theirs)
        if theirs.get("les_marges"):
            signs.add(tuple(sorted(m >= 0 for m in theirs["les_marges"].values())))
    assert (False, True) in signs  # a positive and a negative margin: the case "all" decides

