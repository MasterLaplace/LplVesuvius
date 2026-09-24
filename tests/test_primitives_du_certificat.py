"""Chaque primitive du certificat contre celle du producteur, sur des entrées construites pour ses cas limites.

Les égalités (deux ailes de même aire, deux troisièmes lignes à la même distance), les trous juste
au-delà de ce que `225` franchit, et les marges de départage de signes opposés : le segment réel n'en
porte aucun, donc ce sont des entrées fabriquées qui les exercent, et un test de couverture qui vérifie
qu'elles le font.
"""
from __future__ import annotations

import numpy as np
import pytest

from conftest import recherche
from vesuve.treillis import boucle, certificat as cert, geometrie as geo

pytestmark = recherche


def _presences(n=40):
    """Des présences pleines (égalités), trouées au hasard, et trouées symétriquement (égalités décalées)."""
    rng = np.random.default_rng(7)
    out = []
    for i in range(n):
        gy, gx = int(rng.integers(40, 70)), int(rng.integers(40, 70))
        A = np.ones((gy, gx), dtype=bool)
        if i % 4 == 1:
            for _ in range(int(rng.integers(1, 5))):
                r, c = int(rng.integers(0, gy)), int(rng.integers(0, gx))
                A[r:r + int(rng.integers(1, 6)), c:c + int(rng.integers(1, 6))] = False
        elif i % 4 == 2:  # un trou au milieu d'une colonne : deux ailes de même longueur, décalées
            c = int(rng.integers(gx // 2, gx - 6))
            m = gy // 2
            A[m - 1:m + 2, c] = False
        elif i % 4 == 3:  # une rangée trouée au milieu : deux ailes de même largeur en haut et en bas
            r = int(rng.integers(gy // 2, gy - 6))
            A[r, gx // 2 - 1:gx // 2 + 2] = False
        out.append(A)
    return out


def test_le_plus_grand_rectangle_est_celui_du_producteur():
    from ou_sarrete_le_segment import le_plus_grand_rectangle
    for A in _presences():
        for k in (3, 5, 9):
            r = le_plus_grand_rectangle(A, k)
            assert geo.le_plus_grand_rectangle(A, k) == (list(r) if r is not None else None)


def test_deux_rectangles_egaux_se_departagent_comme_chez_le_producteur():
    """Deux moitiés identiques séparées par une rangée ou une colonne vide : même chemin, même aire, et
    c'est le plus petit début qui gagne."""
    from ou_sarrete_le_segment import le_plus_grand_rectangle
    for coupe in ("rangee", "colonne"):
        A = np.ones((61, 61), dtype=bool)
        if coupe == "rangee":
            A[30, :] = False
        else:
            A[:, 30] = False
        leur = list(le_plus_grand_rectangle(A, 9))
        assert geo.le_plus_grand_rectangle(A, 9) == leur
        assert (leur[0] < 30) if coupe == "rangee" else (leur[2] < 30)


def test_laile_est_celle_du_producteur_egalites_comprises():
    from le_segment_au_dela_du_rectangle_se_relie_t_il import laile, les_tenues
    egalites = 0
    for A in _presences():
        for k in (3, 5, 7, 9):
            rect = geo.le_plus_grand_rectangle(A, 9)
            if rect is None:
                continue
            t = les_tenues(A, k)
            for cote in geo.LES_COTES:
                for exclues in ([], [(rect[3] + 12, 9)], [(rect[0] - 10, 5)]):
                    leur = laile(A, rect, cote, k, t, exclues=exclues)["les_coins"]
                    assert geo.laile(A, rect, cote, k, geo.les_tenues(A, k), exclues=exclues) == leur
                    egalites += int(leur is not None)
    assert egalites > 100


def _ailes_construites():
    """Des ailes posées à la main : sur une présence pleine, les deux côtés offrent une troisième ligne à
    la même distance (le côté du rectangle doit gagner) ; avec une coupe qui traverse tout le côté du
    rectangle, seul l'extérieur en offre une."""
    out = []
    for cote, co in (("droite", [10, 60, 30, 45]), ("gauche", [10, 60, 30, 45]), ("haut", [30, 45, 10, 60]),
                     ("bas", [30, 45, 10, 60])):
        for coupe in (False, True):
            A = np.ones((80, 80), dtype=bool)
            if coupe:
                r0, r1, c0, c1 = co
                if cote == "droite":
                    A[35, :c0] = False
                elif cote == "gauche":
                    A[35, c1 + 1:] = False
                elif cote == "haut":
                    A[r1 + 1:, 35] = False
                else:
                    A[:r0, 35] = False
            out.append((A, co, cote))
    return out


def test_la_troisieme_ligne_est_celle_du_producteur_a_egalite_de_distance():
    from laquelle_des_deux_colonnes_derive import la_troisieme_ligne
    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_tenues
    issues = set()
    for A, co, cote in _ailes_construites():
        for k in (3, 5, 9):
            leur = la_troisieme_ligne(A, co, cote, k, les_tenues(A, k))
            assert geo.la_troisieme_ligne(A, co, cote, k, geo.les_tenues(A, k)) == leur
            if leur is not None:
                issues.add(leur["du_cote_du_rectangle"])
    assert issues == {True, False}  # les deux issues de l'égalité sont vues


def _pas_troues(rng, coins, k, trou):
    """Des pas pour les quatre côtés d'une boucle, avec un trou de majorité de `trou` coutures sur un côté."""
    r0, r1, c0, c1 = coins
    pas = {}
    for sens, centre, de, a, _s, nom in boucle.les_cotes(coins):
        lignes = {}
        for l_ in geo.les_lignes(centre, k):
            s = {x: round(float(rng.normal(0.1, 1.5)) * 16) / 16 for x in range(de, a)}
            if nom == "droite" and trou:
                for x in range(de + 5, de + 5 + trou):
                    s.pop(x, None)
            lignes[l_] = s
        pas[(sens, centre)] = lignes
    return pas


@pytest.mark.parametrize("trou", [0, 16, 17, 18, 27])
def test_une_largeur_est_celle_du_producteur_au_bord_de_ce_qui_se_franchit(trou):
    from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import une_largeur_du_segment
    rng = np.random.default_rng(trou)
    coins = [10, 70, 20, 90]
    for k in (3, 5, 9):
        pas = _pas_troues(rng, coins, k, trou)
        leur = une_largeur_du_segment(pas, coins, k, "le_maillage", 17, 20261105, 99)
        mien = boucle.une_largeur_du_segment(pas, coins, k, 17, 20261105, 99)
        assert mien["fermable"] == leur["fermable"] == (trou <= 17)
        if leur["fermable"]:
            for cle in ("la_fermeture_en_voxels", "sous_le_demi_pli", "la_dispersion_du_pas_en_voxels", "le_nul"):
                assert mien[cle] == leur[cle], cle


def test_le_verdict_des_trois_est_celui_du_producteur_marges_melees():
    from laquelle_des_deux_colonnes_derive import le_verdict_des_trois
    rng = np.random.default_rng(3)
    tl = {"la_ligne": 30, "le_sens": "colonnes", "la_plus_proche": 40, "la_plus_loin": 55,
          "du_cote_du_rectangle": True, "lecart": 10}
    signes = set()
    for _ in range(300):
        par = {n: {"par_largeur": {"9": {"fermable": bool(rng.random() > 0.05),
                                         "la_fermeture_en_voxels": round(float(rng.normal(0, 20)), 4),
                                         "le_nul": {"la_fermeture_mediane_en_valeur_absolue":
                                                    round(float(rng.uniform(0, 15)), 4)}}}}
               for n in ("laile", "letroite", "la_large")}
        leur = le_verdict_des_trois(tl, par, 9)
        leur.pop("ce_qui_reste_a_mesurer", None)
        mien = cert.le_verdict_des_trois(tl, par, 9)
        assert mien == leur
        if leur.get("les_marges"):
            signes.add(tuple(sorted(m >= 0 for m in leur["les_marges"].values())))
    assert (False, True) in signes  # une marge positive et une négative : le cas que « toutes » tranche
