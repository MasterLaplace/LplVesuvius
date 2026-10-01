"""What a chain says of itself, and where its criterion was not validated.

A chain is judged by the criterion of `criterion.py`, which needs no referent. That criterion was measured against the
published windings of one segment, and only there; anywhere else it is the only judge, and this report says so, with the
facts that carry each statement (`R4-F538`, `R4-F551`, `R4-F552`).
"""
from __future__ import annotations

from collections import Counter

from vesuve.chain.chain import Link, held_in_a_row

SCOPE = {
    "validated": [
        {"where": "PHercParis4, seeds 4 to 8, both sides, eight jumps",
         "what": "the strict reading against the published windings finds 27 of the 28 judged jumps right, and 24 of 24 on "
                 "seeds 4, 5, 6 and 8; the only wrong jump is on seed 7, whose first readable surface already straddles two "
                 "windings",
         "fact": "R4-F551"},
        {"where": "PHercParis4, seeds 4 to 8",
         "what": "the criterion holds 39 of the 44 sound jumps that do not straddle and 24 of the 66 others: it separates them "
                 "only in part, and the zero threshold does most of the work",
         "fact": "R4-F538"},
    ],
    "not_validated": [
        {"where": "PHercParis4, seeds 1 to 3",
         "what": "the published windings overlap there, and the criterion holds 17 of the 21 wrong jumps",
         "fact": "R4-F538"},
        {"where": "PHerc0358 and any scroll with no published winding",
         "what": "nothing but the criterion judges the chain: it holds 1, 1, 3, 4 and 5 jumps in a row on the five sides "
                 "followed, 3 in median, and nothing says whether those surfaces are on their sheet",
         "fact": "R4-F552"},
        {"where": "a prediction that misses a sheet between two surfaces",
         "what": "a jump that crosses two sheets is counted as crossing one",
         "fact": "R4-F531"},
    ],
    "possible_next_steps": [
        {"what": "trimming the run a surface falls back on before counting: every validated surface is read on the right "
                 "winding, and one count too many is corrected", "fact": "R4-F586"},
        {"what": "the agreement of three chains at the counts of m7: more surfaces validated without one on the wrong winding",
         "fact": "R4-F571"},
    ],
}


def describe(chain: list[Link]) -> dict:
    """One chain, jump by jump: where each kept surface comes from, its points, whether the criterion holds it; how many jumps
    in a row it holds; and the scope of what that is worth."""
    origins = Counter(link.origin for link in chain if link.origin is not None)
    return {"jumps": [{"jump": h, "origin": link.origin, "points": link.points, "held": link.holds,
                       "counted": link.count["counted"], "one_sheet_share": link.count["one_sheet_share"],
                       "points_at_zero": link.count["counts"].get("0", 0)} for h, link in enumerate(chain, 1)],
            "held_in_a_row": held_in_a_row(chain), "origins": dict(origins), "scope": SCOPE,
            "judged_by": "the criterion that needs no referent (`R4-F531`, `R4-F538`); no published winding takes part"}
