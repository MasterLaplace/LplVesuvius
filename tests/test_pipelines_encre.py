"""First Letters et le titre de Paris 4, sur des données fabriquées dont on connaît la réponse."""
from __future__ import annotations

import json

import numpy as np
import tifffile
from PIL import Image

from vesuve.first_letters.pipeline import lancer as first_letters
from vesuve.paris4_title import pipeline as p4


def _pile(dossier, cote=700, couches=31):
    """Une surface ronde de papyrus : des fibres horizontales, et 0 hors du papyrus comme un vrai rendu."""
    dossier.mkdir(parents=True)
    rng = np.random.default_rng(0)
    y, x = np.mgrid[:cote, :cote]
    papyrus = (y - cote / 2) ** 2 + (x - cote / 2) ** 2 < (0.48 * cote) ** 2
    for i in range(couches):
        a = 120 + 30 * np.sin(y / 3.0) + rng.normal(0, 10, (cote, cote))
        tifffile.imwrite(dossier / f"{i:02d}.tif", np.where(papyrus, np.clip(a, 1, 255), 0).astype(np.uint8))
    return papyrus


def _carte_lignee(papyrus, periode=24):
    """Des logits : des rangées d'encre tous les `periode` pixels, du bruit ailleurs."""
    rng = np.random.default_rng(1)
    y = np.arange(papyrus.shape[0])[:, None] * np.ones(papyrus.shape)
    c = np.where((y % periode) < 5, 3.0, -3.0) + rng.normal(0, 0.5, papyrus.shape)
    return np.where(papyrus, c, np.nan).astype(np.float32)


def test_first_letters_trace_les_rangees_dune_carte_lignee_et_le_melange_les_perd(tmp_path):
    papyrus = _pile(tmp_path / "couches")
    np.save(tmp_path / "carte.npy", _carte_lignee(papyrus))
    (tmp_path / "20250101000000-essai.tifxyz").mkdir()
    r = first_letters(tmp_path / "couches", tmp_path / "20250101000000-essai.tifxyz", "PHerc1447", tmp_path / "s",
                      cote_mm=4.0, carte=tmp_path / "carte.npy")
    d = json.loads((tmp_path / "s" / "rapport.json").read_text())
    f6 = next(e for e in d["les_etages"] if e["id"] == "F6")
    assert f6["sorties"]["les_rangees"]["le_reel"]["periodique"]
    assert abs(f6["sorties"]["les_rangees"]["le_reel"]["periode_px"] - 24) <= 1
    assert not f6["sorties"]["les_rangees"]["le_melange"]["periodique"]
    ex = {x["lexigence"]: x["letat"] for x in d["les_exigences"]}
    assert ex["rangées annotées"] == "atteinte" and ex["dix lettres dans 4 cm²"] == "non mesurée"
    assert (tmp_path / "s" / "20250101000000-essai_encre.png").exists() and not r.arrete


def test_first_letters_refuse_un_rouleau_qui_nest_pas_eligible(tmp_path):
    _pile(tmp_path / "couches", cote=200)
    r = first_letters(tmp_path / "couches", tmp_path / "x.tifxyz", "PHercParis4", tmp_path / "s")
    assert r.arrete and r.donnees["larret"]["letage"] == "F0"


def _bande(dossier, largeur=4490, hauteur=1600):
    """Une bande déroulée : trois colonnes pleines, puis une colonne COURTE, puis rien jusqu'au cœur (à droite)."""
    rng = np.random.default_rng(2)
    carte = np.full((hauteur, largeur), 40, dtype=np.uint8) + rng.integers(0, 30, (hauteur, largeur)).astype(np.uint8)
    for c0, lignes in ((200, 40), (1100, 40), (2000, 40), (2900, 8)):
        for k in range(lignes):
            r = 60 + k * 36
            carte[r:r + 12, c0:c0 + 700] = 230
    Image.fromarray(carte).save(dossier / "20260101000000-w010-027.jpg")
    # Le maillage : 20 × 449 cellules sur une spirale dont le rayon DÉCROÎT vers la droite.
    m = dossier / "maillages" / "20260101000000"
    m.mkdir(parents=True)
    j = np.arange(449)[None, :] * np.ones((20, 1))
    theta, rayon = j / 449 * 12 * np.pi, 6.0 - 3.0 * j / 449  # mm
    v = 0.045532
    z = (40.0 + np.arange(20)[:, None] * 2.0 + 0 * j) / v
    x = (46.3 + rayon * np.cos(theta)) / v
    y = (56.3 + rayon * np.sin(theta)) / v
    for nom, a in (("x", x), ("y", y), ("z", z)):
        tifffile.imwrite(m / f"{nom}.tif", a.astype(np.float32))
    return dossier / "maillages"


def test_le_titre_se_cherche_sous_la_derniere_colonne_courte(tmp_path):
    maillages = _bande(tmp_path)
    p4.lancer(tmp_path, tmp_path / "s", maillages=maillages)
    lieux = json.loads((tmp_path / "s" / "candidats.json").read_text())
    assert len(lieux) == 1
    c0, c1 = lieux[0]["la_derniere_colonne_px"]
    assert 2800 <= c0 <= 2950 and 3550 <= c1 <= 3700  # la colonne courte, pas l'avant-dernière
    assert lieux[0]["sa_hauteur_ecrite"] < 0.3  # huit lignes en haut
    d = json.loads((tmp_path / "s" / "rapport.json").read_text())
    t2 = next(e for e in d["les_etages"] if e["id"].startswith("T2"))
    assert t2["sorties"]["le_coeur_est_du_cote"] == "droite de la carte"
