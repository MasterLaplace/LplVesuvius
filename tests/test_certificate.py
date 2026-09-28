"""E6: the hand-free procedure, replayed from the published readings, returns the published journal.

`docs/mesures/la_couverture_sans_main.json` (on the `experimental` branch) is what `246` published by replaying its
112 bands. The ported procedure, on the same bands, the same presence and the same context, must return the same
journal entry by entry, the same loops, the same requests and the same coverage. The research writes French; its
output is read through `vesuve.research`, the one border between the two languages.
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pytest

from conftest import MEASURES, research
from vesuve.lattice import certificate as cert
from vesuve.lattice import geometry as geo
from vesuve.research import to_english

pytestmark = research


def _inputs():
    """The presence, the published bands and the context, read back by the chain's own readers."""
    from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import ce_que_225_a_publie
    from la_couverture_sans_main import ce_que_245_a_publie, les_lectures_publiees
    from ou_sarrete_le_segment import la_grille_de_presence
    from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu
    presence = json.loads((MEASURES / "ou_sarrete_le_segment.json").read_text())["la_presence"]
    p224, p225, p245 = ce_que_224_a_rendu(), ce_que_225_a_publie(), ce_que_245_a_publie()
    ctx = {"longest": int(max(p225["les_longueurs_essayees"])), "seed": int(p224["graine"]),
           "draws": int(p224["tirages"]), "half": 36.0, "reach": int(p245["la_portee_qui_voit"])}
    return la_grille_de_presence(presence), to_english(les_lectures_publiees()["les_bandes"]), ctx


def _without_prose(x):
    """The published journal carries a verdict sentence the port does not recite: everything else is compared."""
    x = copy.deepcopy(x)
    for e in x:
        v = (e.get("tie_break") or {}).get("verdict")
        if v:
            v.pop("ce_qui_reste_a_mesurer", None)
    return x


@pytest.fixture(scope="module")
def replay():
    A, published, ctx = _inputs()
    return A, ctx, cert.certify(A, published, ctx), to_english(json.loads((MEASURES / "la_couverture_sans_main.json").read_text()))


def test_the_context_is_the_one_the_chain_publishes(replay):
    _A, ctx, _r, _p = replay
    assert ctx == {"longest": 17, "seed": 20261105, "draws": 999, "half": 36.0, "reach": 29}


def test_the_rectangle_and_the_journal_fall_back_entry_by_entry(replay):
    _A, _ctx, r, published = replay
    assert r["rectangle"] == published["rectangle"] == [26, 384, 22, 243]
    assert len(r["journal"]) == len(published["journal"]) == 38
    for i, (a, b) in enumerate(zip(_without_prose(r["journal"]), _without_prose(published["journal"]))):
        assert a == b, f"entry {i} of the journal differs"


def test_the_loops_the_requests_and_the_coverage_fall_back(replay):
    _A, _ctx, r, published = replay
    assert r["holding_loops"] == published["holding_loops"]
    assert r["requests"] == published["requests"]
    assert r["left_to_read"] == published["left_to_read"] == 24263
    assert r["coverage"] == published["coverage"] == {"count": 6333, "of": 97771, "share": 0.0648}


def test_the_mask_counts_exactly_the_coverage(replay):
    A, _ctx, r, _p = replay
    m = r["mask"]
    assert m.shape == A.shape and m.dtype == np.uint8
    assert int((m == cert.CERTIFIED).sum()) == r["coverage"]["count"]
    assert int((m != cert.ABSENT_FROM_MASK).sum()) == int(A.sum()) == 97771
    assert not np.any((m == cert.CERTIFIED) & ~A)  # an absent chunk is never certified


def test_wings_count_around_a_rectangle_that_is_not_judged(replay):
    """The fact `246` did not state: the rectangle is "to read", and three wings count all the same."""
    _A, _ctx, r, _p = replay
    assert r["journal"][0]["state"] == "to read"
    assert r["wings_around_an_unjudged_rectangle"] is True


def test_the_hand_finds_its_coverage_again_with_the_loops_of_243():
    A, _published, _ctx = _inputs()
    p243 = to_english(json.loads((MEASURES / "une_aile_plus_etroite_tient_elle.json").read_text()))
    loops = [(b["corners"], b["width"]) for b in p243["holding_loops"]]
    assert geo.loop_coverage(A, loops) == {"count": 89678, "of": 97771, "share": 0.9172}


def test_a_reading_that_does_not_fall_back_is_refused():
    A, published, ctx = _inputs()
    wrong = copy.deepcopy(next(b for b in published if b["direction"] == "rows"))
    line = next(iter(wrong["along"]))
    seam = next(iter(wrong["along"][line]))
    wrong["along"][line][seam][0] += 1.0  # a step that no longer falls back on the published band
    with pytest.raises(cert.ReadingRefused, match="does not fall back"):
        cert.certify(A, published, ctx, fresh={"wrong": wrong})
