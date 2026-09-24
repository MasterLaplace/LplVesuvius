"""L'embarqué égale une extraction fraîche, et il suffit à rejouer le certificat sans l'arbre de recherche."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from conftest import LA_RECHERCHE, LES_MESURES, recherche
from vesuve import donnees
from vesuve.treillis import certificat as cert

ICI = Path(__file__).resolve().parents[1]


@recherche
def test_lembarque_egale_une_extraction_fraiche(tmp_path):
    spec = importlib.util.spec_from_file_location("extraire", ICI / "outils" / "extraire_du_depot.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.extraire(LA_RECHERCHE, tmp_path)
    for f in ("presence.json.gz", "bandes_publiees.json.gz", "sources_de_controle.json.gz"):
        assert (tmp_path / f).read_bytes() == (donnees.LA_RACINE / m.LE_SEGMENT / f).read_bytes(), \
            f"{f} est périmé : relancer outils/extraire_du_depot.py"
    frais = json.loads((tmp_path / "contexte.json").read_text())
    embarque = donnees.le_segment(m.LE_SEGMENT)["contexte"]
    frais["la_provenance"].pop("le_commit_de_la_recherche")
    embarque = {**embarque, "la_provenance": {k: v for k, v in embarque["la_provenance"].items()
                                              if k != "le_commit_de_la_recherche"}}
    assert frais == embarque, "contexte.json est périmé : relancer outils/extraire_du_depot.py"


def test_le_certificat_se_rejoue_depuis_lembarque_seul():
    """Sans l'arbre de recherche : c'est ce que l'image Docker fera."""
    s = donnees.le_segment("20230702185753")
    r = cert.certifier(s["presence"], s["bandes"], s["contexte"]["la_procedure"])
    assert r["la_couverture"] == {"combien": 6333, "sur": 97771, "la_part": 0.0648}
    assert r["ce_qui_reste_a_lire"] == 24263 and len(r["les_demandes"]) == 111


@recherche
def test_le_rejeu_depuis_lembarque_egale_la_publication():
    s = donnees.le_segment("20230702185753")
    r = cert.certifier(s["presence"], s["bandes"], s["contexte"]["la_procedure"])
    publie = json.loads((LES_MESURES / "la_couverture_sans_main.json").read_text())
    assert r["les_demandes"] == publie["les_demandes"]
    assert r["les_boucles_qui_tiennent"] == publie["les_boucles_qui_tiennent"]
