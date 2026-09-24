"""Le balayage du modèle d'encre porté, contre celui du producteur, sur une petite fenêtre réelle.

Sauté quand torch, le modèle ou la pile manquent : le groupe `encre` est optionnel, et le rapport de First
Letters dit « l'encre du modèle n'est pas calculée » plutôt que de rendre une carte vide.
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pytest

from conftest import LES_DONNEES, recherche

LE_MODELE = LES_DONNEES / "models" / "timesformer_GP_scroll1"
LA_PILE = LES_DONNEES / "couches" / "1447_20250702235910"

pytestmark = [recherche, pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="torch absent"),
              pytest.mark.skipif(not (LE_MODELE / "config.json").exists() or not LA_PILE.exists(),
                                 reason="le modèle ou la pile de PHerc1447 manque")]


def test_la_carte_dencre_est_celle_du_producteur():
    import infer_ink as ref
    from vesuve.rendu import modele
    fenetre = (1200, 1500, 160, 160)
    m = modele.charger(LE_MODELE)
    pile = modele.la_pile(LA_PILE, 2, fenetre)
    assert np.array_equal(pile, ref.load_layer_stack(LA_PILE, 2, fenetre))
    mien, n = modele.inferer(pile, m, pas=21, lot=4, fils=8)
    leur, n_ref, _ = ref.infer(pile, m, 21, 4, 8, "cpu", progression=False)
    assert n == n_ref == 25
    assert np.array_equal(np.isnan(mien), np.isnan(leur))
    assert np.allclose(mien, leur, atol=1e-5, equal_nan=True)
