"""La procédure portée contre celle du producteur, sur des empreintes FABRIQUÉES pour exercer chaque règle.

Le rejeu sur le segment réel n'exerce pas toutes les règles : aucune égalité entre deux ailes, aucun
trou dans une boucle jugée, des marges de départage loin de zéro. Une sonde qui cassait l'une d'elles
restait donc verte. Ici chaque scénario fabrique une présence (pleine pour les égalités, trouée pour
les bords), un champ de spire (lisse, plus une colonne qui DÉRIVE sous une rangée pour faire franchir
et départager), et des chunks refusés au hasard pour faire des trous de majorité. Les deux procédures
rejouent les mêmes tours de lecture, et doivent rendre le même journal à chaque tour.
"""
from __future__ import annotations

import copy

import numpy as np
import pytest

from conftest import recherche
from vesuve.treillis import certificat as cert

pytestmark = recherche

LE_CONTEXTE = {"plus_long": 17, "graine": 20261105, "tirages": 49, "demi": 36.0, "portee": 29}


def _scenario(graine: int):
    rng = np.random.default_rng(graine)
    gy, gx = int(rng.integers(70, 110)), int(rng.integers(60, 90))
    A = np.ones((gy, gx), dtype=bool)
    if graine % 3:  # des bords déchirés et des trous, sinon une présence pleine qui fait des égalités
        A[: int(rng.integers(0, 6)), :] = False
        A[:, gx - int(rng.integers(0, 6)):] = False
        for _ in range(int(rng.integers(1, 6))):
            r, c = int(rng.integers(0, gy)), int(rng.integers(0, gx))
            A[r:r + int(rng.integers(1, 8)), c:c + int(rng.integers(1, 8))] = False
    # Le champ de spire : une pente douce, et une colonne qui dérive sous une rangée.
    r_ = np.arange(gy)[:, None]
    c_ = np.arange(gx)[None, :]
    w = 0.05 * r_ + 0.03 * c_ + rng.normal(0, 0.2, size=(gy, gx))
    # Comme la colonne 260 du segment : toute une région de colonnes dont le pas vertical dérive sous une
    # rangée, assez pour que le cumul d'une boucle qui la longe franchisse le demi-feuillet.
    derive = {"colonne": int(rng.integers(gx // 2, gx - 12)), "rangee": int(rng.integers(10, gy // 2)),
              "par_couture": float(rng.choice([0.0, 0.35, 0.7]))}
    refuses = rng.random((gy, gx)) < rng.uniform(0.0, 0.12)
    return A, w, derive, refuses, rng


def _lecteur(A, w, derive, refuses, rng):
    """Une bande lue sur le champ fabriqué : le pas vrai plus un bruit propre à chaque ligne, au 1/16."""
    def pas_v(r, c):
        x = w[r + 1, c] - w[r, c]
        if abs(c - derive["colonne"]) <= 4 and r >= derive["rangee"]:
            x += derive["par_couture"]
        return x

    def lire(d):
        lignes, de, a = d["les_lignes"], int(d["de"]), int(d["a"])
        le_long = {}
        for l_ in lignes:
            sens = 0 if d["le_sens"] == "rangees" else 1  # un entier : le hash d une chaîne change à chaque processus
            bruit = np.random.default_rng([sens, l_, de, a]).normal(0, 1.2, size=a - de + 1)
            s = {}
            for i, x in enumerate(range(de, a)):
                (p, q) = ((l_, x), (l_, x + 1)) if d["le_sens"] == "rangees" else ((x, l_), (x + 1, l_))
                if not (A[p] and A[q]) or refuses[p] or refuses[q]:
                    continue
                v = (w[l_, x + 1] - w[l_, x]) if d["le_sens"] == "rangees" else pas_v(x, l_)
                s[str(x)] = [round(round((v + bruit[i]) * 16) / 16, 4), 0.0, 16]
            le_long[str(l_)] = s
        return {"le_sens": d["le_sens"], "le_centre": d["le_centre"], "les_lignes": list(lignes), "de": de, "a": a,
                "le_long": le_long, "en_travers": {}, "les_lectures": {}}
    return lire


def _sans_prose(journal):
    j = copy.deepcopy(journal)
    for e in j:
        v = (e.get("le_departage") or {}).get("le_verdict")
        if v:
            v.pop("ce_qui_reste_a_mesurer", None)
    return j


@pytest.mark.parametrize("graine", range(12))
def test_les_deux_procedures_rendent_le_meme_journal_a_chaque_tour(graine):
    import la_couverture_sans_main as ref
    A, w, derive, refuses, rng = _scenario(graine)
    lire = _lecteur(A, w, derive, refuses, rng)
    bandes, tours, etats = [], 0, set()
    for tours in range(1, 7):
        a = ref.derouler(A, ref.Lectures(bandes), {**LE_CONTEXTE, "regle": "le_maillage"})
        b = cert.derouler(A, cert.Lectures(bandes), LE_CONTEXTE)
        assert b["le_rectangle"] == a["le_rectangle"]
        assert _sans_prose(b["le_journal"]) == _sans_prose(a["le_journal"]), f"tour {tours}"
        assert b["les_boucles_qui_tiennent"] == a["les_boucles_qui_tiennent"]
        assert b["les_demandes"] == a["les_demandes"]
        etats |= {e["letat"] for e in a["le_journal"]}
        if not a["les_demandes"]:
            break
        bandes = bandes + [lire(d) for d in a["les_demandes"]]
    assert a["le_rectangle"] is not None  # un scénario sans rectangle n'exercerait rien


def test_les_scenarios_exercent_les_regles_que_le_segment_nexerce_pas():
    """Sans ce contrôle, un corpus de scénarios triviaux laisserait les sondes vertes."""
    import la_couverture_sans_main as ref
    etats, departages, trous = set(), 0, 0
    for graine in range(12):
        A, w, derive, refuses, rng = _scenario(graine)
        lire = _lecteur(A, w, derive, refuses, rng)
        bandes = []
        for _ in range(6):
            a = ref.derouler(A, ref.Lectures(bandes), {**LE_CONTEXTE, "regle": "le_maillage"})
            etats |= {e["letat"] for e in a["le_journal"]}
            departages += sum(1 for e in a["le_journal"] if e.get("le_departage"))
            if not a["les_demandes"]:
                break
            bandes = bandes + [lire(d) for d in a["les_demandes"]]
        trous += int(refuses.sum())
    assert {"dessous", "franchit"} <= etats, etats
    assert departages >= 1 and trous > 0
