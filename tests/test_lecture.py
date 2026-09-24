"""E4 : lire une bande, hors ligne sur un volume fabriqué, puis contre une bande publiée."""
from __future__ import annotations

import json

import numpy as np
import pytest

from conftest import LES_MESURES, recherche, reseau
from vesuve.journal import Journal
from vesuve.noyau import Indecidable
from vesuve.transport import Transport, TransportEnMemoire
from vesuve.treillis.digest import CacheDeDigests
from vesuve.treillis.lecture import LecteurDeBandes
from vesuve.zarr_distant import LE_BUCKET, TableauDistant

URL = "https://exemple.invalid/volume.zarr"
NZ, COTE = 109, 128


def _chunk(cy: int, cx: int) -> bytes:
    """Un chunk dont la feuille descend de 3 couches par colonne et remonte de 2 par rangée."""
    z = np.arange(NZ)[:, None, None]
    y = np.arange(COTE)[None, :, None]
    centre = 40 + 3 * cx - 2 * cy
    v = 110 + 100 * np.exp(-((z - centre) / 2.5) ** 2) + 30 * np.sin(y / 3.0) + 0 * np.arange(COTE)[None, None, :]
    return np.clip(np.round(v), 0, 255).astype(np.uint8).tobytes()


def _volume(absents=(), pannes=()):
    meta = {"shape": [NZ, 5 * COTE, 6 * COTE], "chunks": [NZ, COTE, COTE], "dtype": "|u1",
            "compressor": None, "dimension_separator": "/", "fill_value": 0, "order": "C", "zarr_format": 2}
    corps = {f"{URL}/0/.zarray": json.dumps(meta).encode()}
    for cy in range(5):
        for cx in range(6):
            cle = f"{URL}/0/0/{cy}/{cx}"
            if (cy, cx) in pannes:
                corps[cle] = None
            elif (cy, cx) not in absents:
                corps[cle] = _chunk(cy, cx)
    return TableauDistant(URL, TransportEnMemoire(corps))


BANDE = {"le_sens": "rangees", "le_centre": 2, "les_lignes": [1, 2, 3], "de": 0, "a": 5}


def test_une_bande_rend_les_pas_du_volume_fabrique():
    lu = LecteurDeBandes(_volume(), None, fils=4).lire(BANDE)
    assert set(lu["le_long"]) == {"1", "2", "3"}
    for ligne in lu["le_long"].values():
        assert set(ligne) == {"0", "1", "2", "3", "4"}  # cinq coutures entre six colonnes
        assert all(x == [3.0, 0.0, 16] for x in ligne.values())
    assert set(lu["en_travers"]) == {"1", "2"}  # entre les lignes 1-2 et 2-3, clé = rangée du dessus
    assert all(x == [-2.0, 0.0, 16] for s in lu["en_travers"].values() for x in s.values())


def test_une_colonne_se_lit_dans_lautre_sens():
    bande = {"le_sens": "colonnes", "le_centre": 2, "les_lignes": [1, 2, 3], "de": 0, "a": 4}
    lu = LecteurDeBandes(_volume(), None, fils=4).lire(bande)
    assert all(x == [-2.0, 0.0, 16] for s in lu["le_long"].values() for x in s.values())
    assert set(lu["le_long"]["2"]) == {"0", "1", "2", "3"}
    # en travers d'une bande de colonnes : clé = rangée, puis colonne de gauche
    assert set(lu["en_travers"]) == {"0", "1", "2", "3", "4"}
    assert all(x == [3.0, 0.0, 16] for s in lu["en_travers"].values() for x in s.values())


def test_un_chunk_absent_est_compte_et_coupe_ses_deux_coutures():
    lu = LecteurDeBandes(_volume(absents={(2, 3)}), None, fils=4).lire(BANDE)
    assert lu["les_lectures"]["2"]["refuses"] == {"absent du dépôt": 1}
    assert set(lu["le_long"]["2"]) == {"0", "1", "4"}
    assert "3" not in lu["en_travers"]["1"] and "3" not in lu["en_travers"]["2"]


def test_un_fil_tombe_refuse_la_bande_entiere():
    with pytest.raises(Indecidable, match="réseau"):
        LecteurDeBandes(_volume(pannes={(3, 1)}), None, fils=4).lire(BANDE)


def test_le_cache_sert_un_chunk_sans_le_relire(tmp_path):
    t = _volume()
    cache = CacheDeDigests(tmp_path, URL)
    premier = LecteurDeBandes(t, cache, fils=4).lire(BANDE)
    avant = len(t.transport.demandes)
    second = LecteurDeBandes(t, cache, fils=4)
    assert second.lire(BANDE) == premier
    assert len(t.transport.demandes) == avant and second.chunks_lus == 0


def test_une_panne_ne_se_met_jamais_en_cache(tmp_path):
    cache = CacheDeDigests(tmp_path, URL)
    with pytest.raises(Indecidable):
        LecteurDeBandes(_volume(pannes={(3, 1)}), cache, fils=4).lire(BANDE)
    assert cache.lire(3, 1) is None and cache.lire(3, 0) is not None


# ── contre une bande publiée, sur le vrai volume ──────────────────────────────────────────────

def _la_plus_petite_bande_publiee():
    from la_couverture_sans_main import LES_LECTURES_PUBLIEES
    meilleure = None
    for chemin in LES_LECTURES_PUBLIEES:
        for b in (json.loads(chemin.read_text()).get("les_bandes") or {}).values():
            n = len(b["les_lignes"]) * (int(b["a"]) - int(b["de"]) + 1)
            if len(b["les_lignes"]) >= 3 and int(b["a"]) - int(b["de"]) >= 8 and (meilleure is None or n < meilleure[0]):
                meilleure = (n, b)
    return meilleure[1]


@recherche
@reseau
def test_une_bande_publiee_se_relit_a_lidentique(tmp_path):
    publiee = _la_plus_petite_bande_publiee()
    cle = next(l.split("\t")[1] for l in (LES_MESURES / "volumes_surface_PHercParis4.txt").read_text().splitlines()
               if l.startswith("20230702185753\t") and "/2.4um-" in l)
    t = TableauDistant(f"{LE_BUCKET}/{cle}", Transport())
    lue = LecteurDeBandes(t, CacheDeDigests(tmp_path, t.url), fils=16, journal=Journal()).lire(publiee)
    assert lue["le_long"] == publiee["le_long"]
    assert lue["en_travers"] == publiee["en_travers"]
    for ligne, lecture in publiee["les_lectures"].items():
        assert lue["les_lectures"][ligne]["refuses"] == lecture["refuses"]
