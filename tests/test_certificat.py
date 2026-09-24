"""E6 : la procédure sans main, rejouée depuis les lectures publiées, rend le journal publié.

`docs/mesures/la_couverture_sans_main.json` est ce que `246` a publié en rejouant ses 112 bandes. La
procédure portée, sur les mêmes bandes, la même présence et le même contexte, doit rendre le même
journal entrée par entrée, les mêmes boucles, les mêmes demandes et la même couverture.
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pytest

from conftest import LES_MESURES, recherche
from vesuve.treillis import certificat as cert
from vesuve.treillis import geometrie as geo

pytestmark = recherche


def _entrees():
    """La présence, les bandes publiées et le contexte, relus par les lecteurs mêmes de la chaîne."""
    from la_couverture_sans_main import ce_que_245_a_publie, les_lectures_publiees
    from ou_sarrete_le_segment import la_grille_de_presence
    from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import ce_que_225_a_publie
    from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu
    presence = json.loads((LES_MESURES / "ou_sarrete_le_segment.json").read_text())["la_presence"]
    p224, p225, p245 = ce_que_224_a_rendu(), ce_que_225_a_publie(), ce_que_245_a_publie()
    ctx = {"plus_long": int(max(p225["les_longueurs_essayees"])), "graine": int(p224["graine"]),
           "tirages": int(p224["tirages"]), "demi": 36.0, "portee": int(p245["la_portee_qui_voit"])}
    return la_grille_de_presence(presence), les_lectures_publiees()["les_bandes"], ctx


def _sans_prose(x):
    """Le journal publié porte une phrase de verdict que le port ne récite pas : tout le reste est comparé."""
    x = copy.deepcopy(x)
    for e in x:
        v = (e.get("le_departage") or {}).get("le_verdict")
        if v:
            v.pop("ce_qui_reste_a_mesurer", None)
    return x


@pytest.fixture(scope="module")
def rejeu():
    A, publiees, ctx = _entrees()
    return A, ctx, cert.certifier(A, publiees, ctx), json.loads((LES_MESURES / "la_couverture_sans_main.json").read_text())


def test_le_contexte_est_celui_que_la_chaine_publie(rejeu):
    _A, ctx, _r, _p = rejeu
    assert ctx == {"plus_long": 17, "graine": 20261105, "tirages": 999, "demi": 36.0, "portee": 29}


def test_le_rectangle_et_le_journal_retombent_entree_par_entree(rejeu):
    _A, _ctx, r, publie = rejeu
    assert r["le_rectangle"] == publie["le_rectangle"] == [26, 384, 22, 243]
    assert len(r["le_journal"]) == len(publie["le_journal"]) == 38
    for i, (a, b) in enumerate(zip(_sans_prose(r["le_journal"]), _sans_prose(publie["le_journal"]))):
        assert a == b, f"l'entrée {i} du journal diffère"


def test_les_boucles_les_demandes_et_la_couverture_retombent(rejeu):
    _A, _ctx, r, publie = rejeu
    assert r["les_boucles_qui_tiennent"] == publie["les_boucles_qui_tiennent"]
    assert r["les_demandes"] == publie["les_demandes"]
    assert r["ce_qui_reste_a_lire"] == publie["ce_qui_reste_a_lire"] == 24263
    assert r["la_couverture"] == publie["la_couverture"] == {"combien": 6333, "sur": 97771, "la_part": 0.0648}


def test_le_masque_compte_exactement_la_couverture(rejeu):
    A, _ctx, r, _p = rejeu
    m = r["le_masque"]
    assert m.shape == A.shape and m.dtype == np.uint8
    assert int((m == cert.CERTIFIE).sum()) == r["la_couverture"]["combien"]
    assert int((m != cert.ABSENT_DU_MASQUE).sum()) == int(A.sum()) == 97771
    assert not np.any((m == cert.CERTIFIE) & ~A)  # un chunk absent n'est jamais certifié


def test_des_ailes_comptent_autour_dun_rectangle_qui_nest_pas_juge(rejeu):
    """Le fait que `246` ne disait pas : le rectangle est « à lire », et trois ailes comptent quand même."""
    _A, _ctx, r, _p = rejeu
    assert r["le_journal"][0]["letat"] == "à lire"
    assert r["les_ailes_autour_dun_rectangle_non_juge"] is True


def test_la_main_retrouve_sa_couverture_avec_les_boucles_de_243():
    A, _publiees, _ctx = _entrees()
    p243 = json.loads((LES_MESURES / "une_aile_plus_etroite_tient_elle.json").read_text())
    boucles = [(b["les_coins"], b["la_largeur"]) for b in p243["les_boucles_qui_tiennent"]]
    assert geo.la_couverture_des_boucles(A, boucles) == {"combien": 89678, "sur": 97771, "la_part": 0.9172}


def test_une_lecture_qui_ne_retombe_pas_est_refusee():
    A, publiees, ctx = _entrees()
    fausse = copy.deepcopy(next(b for b in publiees if b["le_sens"] == "rangees"))
    ligne = next(iter(fausse["le_long"]))
    couture = next(iter(fausse["le_long"][ligne]))
    fausse["le_long"][ligne][couture][0] += 1.0  # un pas qui ne retombe plus sur la bande publiée
    with pytest.raises(cert.LectureRefusee, match="ne retombe pas"):
        cert.certifier(A, publiees, ctx, neuves={"fausse": fausse})
