"""What a chain says of itself, and where its criterion was not validated."""
from __future__ import annotations

import numpy as np

from vesuve.chain import chain as ch
from vesuve.chain import growth, report
from vesuve.chain.surface import Surface

GOOD = {"points": 100, "in_front": 100, "counted": 100, "counts": {"1": 100}, "one_sheet_share": 1.0}
BAD = {"points": 100, "in_front": 100, "counted": 100, "counts": {"0": 90, "1": 10}, "one_sheet_share": 0.1}


def link(origin, count, points=10) -> ch.Link:
    surface = Surface(np.zeros((3, 3, 3)), np.ones((3, 3), dtype=bool))
    jump = growth.Jump(surface, np.zeros((3, 3)), (1, 1), np.zeros((3, 3)))
    return ch.Link(jump, surface, origin, count, count, points, surface if origin else None)


def test_a_chain_is_described_jump_by_jump_with_its_scope():
    got = report.describe([link(ch.FROM_THE_REGROWTH, GOOD, 50), link(ch.FROM_A_RELAUNCH, BAD, 20), link(None, BAD, 0)])
    assert [j["origin"] for j in got["jumps"]] == [ch.FROM_THE_REGROWTH, ch.FROM_A_RELAUNCH, None]
    assert [j["held"] for j in got["jumps"]] == [True, False, False] and got["held_in_a_row"] == 1
    assert got["jumps"][1]["points_at_zero"] == 90 and got["jumps"][0]["points"] == 50
    assert got["origins"] == {ch.FROM_THE_REGROWTH: 1, ch.FROM_A_RELAUNCH: 1} and got["scope"] is report.SCOPE


def test_the_scope_says_where_the_criterion_was_not_validated_and_cites_its_facts():
    unvalidated = {x["where"]: x for x in report.SCOPE["not_validated"]}
    seeds_one_to_three = unvalidated["PHercParis4, seeds 1 to 3"]
    assert "17 of the 21 wrong jumps" in seeds_one_to_three["what"] and seeds_one_to_three["fact"] == "R4-F538"
    other = unvalidated["PHerc0358 and any scroll with no published winding"]
    assert "nothing but the criterion judges" in other["what"] and other["fact"] == "R4-F552"
    assert "1, 1, 3, 4 and 5 jumps in a row" in other["what"]


def test_the_scope_says_where_it_was_validated_and_what_is_left_for_later():
    validated = {x["fact"]: x for x in report.SCOPE["validated"]}
    assert "27 of the 28" in validated["R4-F551"]["what"] and "seed 7" in validated["R4-F551"]["what"]
    assert "39 of the 44" in validated["R4-F538"]["what"] and "24 of the 66" in validated["R4-F538"]["what"]
    assert {x["fact"] for x in report.SCOPE["possible_next_steps"]} == {"R4-F586", "R4-F571"}
    assert all(x["fact"].startswith("R4-F") for k in report.SCOPE.values() for x in k)
