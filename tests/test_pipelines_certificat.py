"""Les pipelines Grand Prize et Progress, hors ligne, sur le segment embarqué."""
from __future__ import annotations

import json

import numpy as np
import tifffile

from vesuve import formulaire
from vesuve.grand_prize.pipeline import lancer as grand_prize
from vesuve.progress.pipeline import lancer as progress
from vesuve.transport import TransportEnMemoire


def _hors_ligne(monkeypatch):
    """Aucun octet ne sort : le transport ne connaît aucune URL, donc tout ce qui est distant est absent."""
    monkeypatch.setattr("vesuve.grand_prize.pipeline.Transport", lambda **_: TransportEnMemoire({}))
    monkeypatch.setattr("vesuve.progress.pipeline.Transport", lambda **_: TransportEnMemoire({}))


def test_le_grand_prize_hors_ligne_rend_son_certificat_et_dit_ce_quil_ne_produit_pas(tmp_path, monkeypatch):
    _hors_ligne(monkeypatch)
    r = grand_prize(sortie=tmp_path, cache=tmp_path / "cache")
    d = json.loads((tmp_path / "rapport.json").read_text())
    etages = {e["id"]: e for e in d["les_etages"]}
    assert [e["id"] for e in d["les_etages"]] == ["E0", "E1", "E2", "B", "E4", "E4L", "E6", "E7", "E8", "E9"]
    assert etages["E2"]["equations"][0]["valeur"] == 36
    assert round(min(q["valeur"] for q in etages["B"]["equations"] if q["id"] == "N5"), 2) == 112.08
    assert round(next(q["valeur"] for q in etages["B"]["equations"] if q["id"] == "N7"), 4) == 2.3394  # R4-F343
    assert etages["E6"]["sorties"]["les_chunks_a_lire"] == 24263
    assert etages["E8"]["etat"] == "sauté" and "absent" in etages["E8"]["raison"]  # jamais une image vide
    m = tifffile.imread(tmp_path / "masque_par_chunk.tif")
    assert m.shape == (396, 285) and int((m == 2).sum()) == 6333
    exigences = {x["lexigence"]: x["letat"] for x in d["les_exigences"]}
    assert exigences["100 % du recto déroulé"] == "non atteinte"
    assert exigences["un maillage par colonne, `column_NN.tifxyz`"] == "non atteinte"
    assert not r.arrete


def test_laudit_designe_la_colonne_260(tmp_path, monkeypatch):
    _hors_ligne(monkeypatch)
    progress(sortie=tmp_path, cache=tmp_path / "cache")
    cas = json.loads((tmp_path / "cas_dechec.json").read_text())
    assert len(cas) == 1 and cas[0]["la_ligne_qui_derive"] == 260
    assert cas[0]["les_coupes_au_dela_du_demi_feuillet"] == [163, 173, 203]  # les deux traversées de `245`
    m = tifffile.imread(tmp_path / "masque_daudit.tif")
    assert int((m == 3).sum()) > 0 and not np.any((m == 3) & (m == 2))


def test_une_bande_donnee_qui_ne_retombe_pas_arrete_le_grand_prize(tmp_path, monkeypatch):
    _hors_ligne(monkeypatch)
    from vesuve import donnees
    b = json.loads(json.dumps(next(x for x in donnees.le_segment("20230702185753")["bandes"] if x["le_sens"] == "rangees")))
    ligne = next(iter(b["le_long"]))
    b["le_long"][ligne][next(iter(b["le_long"][ligne]))][0] += 2.0
    (tmp_path / "fausse.json").write_text(json.dumps({"les_bandes": {"fausse": b}}))
    r = grand_prize(sortie=tmp_path / "s", cache=tmp_path / "cache", lectures=[tmp_path / "fausse.json"])
    assert r.arrete and r.donnees["larret"]["letage"] == "E4"


def test_chaque_equation_qui_porte_un_calcul_le_fait():
    for e in formulaire.LE_FORMULAIRE.values():
        assert e.fait and e.latex and e.source
    assert formulaire.equation("N5").calcul(36.0, 3.4004) > 112


def test_le_formulaire_publie_est_celui_que_le_code_rend():
    from pathlib import Path
    from vesuve.cli import formulaire_en_markdown
    publie = Path(__file__).resolve().parents[1] / "FORMULAIRE.md"
    assert publie.read_text() == formulaire_en_markdown(), "FORMULAIRE.md est périmé : `vesuve formules --markdown`"
