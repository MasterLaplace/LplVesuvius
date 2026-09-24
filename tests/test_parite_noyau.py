"""Le noyau C contre la fonction même qui a produit chaque nombre publié.

Chaque test tire des milliers d'entrées, les donne aux deux, et exige la MÊME sortie. Une égalité
approchée n'est admise que là où le producteur lui-même arrondit ou accumule en float32, et c'est
dit à l'endroit.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from conftest import LES_MESURES, recherche
from vesuve import noyau

pytestmark = recherche

LA_GRAINE = 20260924


def _profils_de_papyrus(rng, n=109, feuilles=3):
    """Deux profils de bord réalistes : des feuilles brillantes dans un milieu à 115-130, décalées.

    Le profil est une MOYENNE de seize voxels entiers, donc un multiple de 1/16 : la même forme que
    ce que le producteur passe à `un_pas`.
    """
    z = np.arange(n)
    decalage = int(rng.integers(-40, 41))
    centres = rng.uniform(10, n - 10, size=feuilles)

    def colonne(dz):
        v = 120.0 + rng.normal(0, 6, size=(16, n))
        for c in centres:
            v += 90.0 * np.exp(-((z - c - dz) / rng.uniform(1.5, 3.0)) ** 2)
        return np.clip(np.round(v), 0, 255).astype(np.uint8).sum(axis=0) / 16.0

    return colonne(0), colonne(decalage)


def test_le_pas_dune_coupe_est_celui_du_producteur():
    from la_derive_saccumule_t_elle import un_pas
    rng = np.random.default_rng(LA_GRAINE)
    compares = 0
    for _ in range(3000):
        a, b = _profils_de_papyrus(rng)
        leur = un_pas(a.reshape(-1, 1), b.reshape(-1, 1), 1, 36)
        if not leur["decidable"]:
            with pytest.raises(noyau.Indecidable):
                noyau.pas_dune_coupe(a, b, 36)
            continue
        pas, sature = noyau.pas_dune_coupe(a, b, 36)
        assert (pas, sature) == (leur["le_pas_en_voxels"], leur["il_sature"])
        compares += 1
    assert compares > 2900  # un corpus vide ne prouverait rien


def test_un_bord_plat_est_indecidable_des_deux_cotes():
    from la_derive_saccumule_t_elle import un_pas
    a, b = np.full(109, 120.0), np.linspace(100, 140, 109)
    assert un_pas(a.reshape(-1, 1), b.reshape(-1, 1), 1, 36)["decidable"] is False
    with pytest.raises(noyau.Indecidable):
        noyau.pas_dune_coupe(a, b, 36)


def test_le_pas_dune_couture_est_celui_du_producteur():
    from combien_de_rangees_faut_il_pour_lire_le_pas import le_pas_de_k_rangees
    rng = np.random.default_rng(LA_GRAINE + 1)
    compares = 0
    for _ in range(400):
        coupes = list(range(4, 128, 8))
        droits, gauches, lisible = {}, {}, []
        a2, b2 = np.zeros((16, 109)), np.zeros((16, 109))
        for i, r in enumerate(coupes):
            a, b = _profils_de_papyrus(rng)
            a2[i], b2[i] = a, b
            ok = bool(rng.random() > 0.15)  # une coupe absente d'un des deux chunks
            lisible.append(ok)
            if ok:
                droits[r], gauches[r] = a, b
        leur = le_pas_de_k_rangees(droits, gauches, coupes, 36)
        if not leur["decidable"]:
            with pytest.raises(noyau.Indecidable):
                noyau.pas_dune_couture(a2, b2, lisible, 36)
            continue
        pas, desaccord, n = noyau.pas_dune_couture(a2, b2, lisible, 36)
        # Le producteur arrondit à quatre décimales avec `round` ; on applique le même.
        assert (round(pas, 4), round(desaccord, 4), n) == (
            leur["le_pas_en_voxels"], leur["le_desaccord_en_voxels"], leur["les_rangees"])
        compares += 1
    assert compares > 350


def test_les_profils_de_bord_sont_les_moyennes_du_producteur():
    from combien_de_rangees_faut_il_pour_lire_le_pas import (les_bords_droit_et_gauche, les_bords_haut_et_bas,
                                                            les_rangees_a_lire)
    rng = np.random.default_rng(LA_GRAINE + 2)
    bloc = rng.integers(0, 256, size=(109, 128, 128), dtype=np.uint8)
    coupes = les_rangees_a_lire(128, 16)
    dr, ga = les_bords_droit_et_gauche(bloc, coupes, 16)
    ba, ha = les_bords_haut_et_bas(bloc, coupes, 16)
    s = noyau.profils_de_bord(bloc, coupes, 16)
    for i, c in enumerate(coupes):
        # Une somme de seize entiers divisée par seize est exacte en double : l'égalité est STRICTE.
        assert np.array_equal(s["droit"][i] / 16.0, dr[c])
        assert np.array_equal(s["gauche"][i] / 16.0, ga[c])
        assert np.array_equal(s["bas"][i] / 16.0, ba[c])
        assert np.array_equal(s["haut"][i] / 16.0, ha[c])


def test_le_filtre_de_texture_retient_ce_que_le_producteur_retient():
    """⚠ Le producteur accumule ses gradients en float32, le noyau en entiers exacts : une couche au
    plancher près peut basculer. Le corpus est donc RESSERRÉ autour du plancher, le test compte les
    couches qui y tombent (sans elles il ne vérifierait rien), et il compte les bascules au lieu de
    les cacher."""
    from le_creux_borne_t_il_la_marche import la_courbe_dun_bloc
    from fiber_orientation import orientation_profile
    rng = np.random.default_rng(LA_GRAINE + 3)
    y = np.arange(128)[None, :, None]
    pres_du_plancher, bascules_de_couche, bascules_de_chunk = 0, 0, 0
    for _ in range(60):
        # Des stries dont la force varie avec la couche, autour de celle qui met la cohérence au
        # plancher : dans un bruit de sigma 20, <gy^2> gagne 0,2146 A^2 sur 800, donc 0,15 tombe
        # vers A = 36. Chaque cube traverse le plancher.
        force = np.linspace(rng.uniform(25, 34), rng.uniform(38, 48), 109)[:, None, None]
        bloc = rng.normal(120, 20, size=(109, 128, 128)) + force * np.sin(y / 3.0)
        bloc = np.clip(np.round(bloc), 0, 255).astype(np.uint8)
        _, coh = orientation_profile(bloc)
        coh = np.asarray(coh)
        pres_du_plancher += int((np.abs(coh - 0.15) < 0.005).sum())
        couches, retenu = noyau.filtre_de_texture(bloc, 0.15)
        bascules_de_couche += abs(couches - int((coh > 0.15).sum()))
        courbe, _ = la_courbe_dun_bloc(bloc)
        bascules_de_chunk += int((courbe is not None) != retenu)
    assert pres_du_plancher >= 50, f"seulement {pres_du_plancher} couches au plancher : le test ne teste rien"
    assert bascules_de_couche == 0
    assert bascules_de_chunk == 0


def test_la_longueur_de_bloc_est_celle_du_producteur():
    from pourquoi_lerreur_declaree_est_trop_petite import la_longueur_de_bloc
    for n in range(1, 10001):
        assert noyau.longueur_de_bloc(n) == min(la_longueur_de_bloc(n), n)


def test_le_nombre_de_fresnel_est_celui_du_producteur():
    from nombre_de_fresnel import nombre_de_fresnel
    rng = np.random.default_rng(LA_GRAINE + 4)
    for _ in range(2000):
        p, d, e = rng.uniform(0.5, 50), rng.uniform(0, 12), rng.uniform(20, 150)
        assert noyau.nombre_de_fresnel(p, d, e) == nombre_de_fresnel(p, d, e)


def test_le_nombre_de_fresnel_rend_ce_que_la_mesure_publie():
    m = json.loads((LES_MESURES / "nombre_de_fresnel.json").read_text())
    vus = 0
    for scan in m["scans"]:
        if all(scan.get(k) is not None for k in ("pas_um", "distance_m", "energie_kev", "fresnel")):
            # Le JSON porte la valeur à pleine précision : l'égalité est stricte.
            assert noyau.nombre_de_fresnel(scan["pas_um"], scan["distance_m"], scan["energie_kev"]) == scan["fresnel"]
            vus += 1
    assert vus >= 50


def test_laire_sous_la_courbe_est_celle_du_producteur():
    from evaluate_segment import auc
    rng = np.random.default_rng(LA_GRAINE + 5)
    for _ in range(200):
        n = int(rng.integers(2, 3000))
        scores = np.round(rng.normal(size=n), int(rng.integers(0, 3)))  # des ex aequo, exprès
        verite = rng.random(n) < rng.uniform(0.05, 0.95)
        leur = auc(scores, verite)
        if np.isnan(leur):
            with pytest.raises(noyau.Indecidable):
                noyau.aire_sous_la_courbe(scores, verite)
            continue
        assert noyau.aire_sous_la_courbe(scores, verite) == pytest.approx(leur, abs=1e-12)


def test_la_longueur_tenable_rend_le_budget_publie():
    m = json.loads((LES_MESURES / "le_budget_de_la_nappe.json").read_text())
    budgets = m["les_budgets"]
    vus = 0

    def parcourir(x):
        nonlocal vus
        if isinstance(x, dict):
            if "la_dispersion_en_voxels" in x and "la_longueur_tenable_en_coutures" in x:
                # La dispersion publiée est arrondie à quatre décimales : la longueur recalculée
                # depuis elle retombe à 0,01 près, pas au bit.
                assert round(noyau.longueur_tenable(float(x["le_demi_pli_en_voxels"]), x["la_dispersion_en_voxels"]), 2) == \
                    pytest.approx(x["la_longueur_tenable_en_coutures"], abs=0.011)
                vus += 1
            for v in x.values():
                parcourir(v)
        elif isinstance(x, list):
            for v in x:
                parcourir(v)
    parcourir(budgets)
    assert vus >= 4
