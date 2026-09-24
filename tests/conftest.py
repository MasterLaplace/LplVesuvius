"""Ce que les tests partagent : où vit le code de recherche qui sert d'oracle, et le réseau."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Le code de recherche est l'ORACLE des tests de parité : il a produit chaque nombre publié, donc
# une réécriture qui ne rend pas ses sorties sur les mêmes entrées n'est pas une réécriture. Il vit sur la
# branche `experimental` ; `VESUVE_RECHERCHE` pointe une copie de travail de cette branche, par exemple
# `git worktree add ../LplVesuvius-experimental experimental`.
_LA_RACINE = os.environ.get("VESUVE_RECHERCHE")
LA_RECHERCHE = Path(_LA_RACINE) if _LA_RACINE else Path("VESUVE_RECHERCHE-non-defini")
LES_MESURES = LA_RECHERCHE / "docs" / "mesures"
# Les données lourdes (piles, modèles) ne sont pas versionnées : `VESUVE_DONNEES` pointe le `data/` qui les porte.
LES_DONNEES = Path(os.environ.get("VESUVE_DONNEES", LA_RECHERCHE / "data"))


def la_recherche_est_la() -> bool:
    return _LA_RACINE is not None and (LA_RECHERCHE / "src" / "nappe" / "la_couverture_sans_main.py").exists()


if la_recherche_est_la():
    for famille in sorted((LA_RECHERCHE / "src").iterdir()):
        if famille.is_dir() and str(famille) not in sys.path:
            sys.path.insert(0, str(famille))

recherche = pytest.mark.skipif(
    not la_recherche_est_la(),
    reason=(f"le code de recherche (l'oracle) n'est pas sous {LA_RECHERCHE}" if _LA_RACINE else
            "VESUVE_RECHERCHE n'est pas défini : le pointer sur une copie de travail de la branche experimental"))
reseau = pytest.mark.skipif(os.environ.get("VESUVE_RESEAU") != "1",
                            reason="lit le bucket public : lancer avec VESUVE_RESEAU=1")
