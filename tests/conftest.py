"""Ce que les tests partagent : où vit le code de recherche qui sert d'oracle, et le réseau."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Le code de recherche est l'ORACLE des tests de parité : il a produit chaque nombre publié, donc
# une réécriture qui ne rend pas ses sorties sur les mêmes entrées n'est pas une réécriture.
LA_RECHERCHE = Path(os.environ.get("VESUVE_RECHERCHE", Path(__file__).resolve().parents[2]))
LES_MESURES = LA_RECHERCHE / "docs" / "mesures"


def la_recherche_est_la() -> bool:
    return (LA_RECHERCHE / "src" / "nappe" / "la_couverture_sans_main.py").exists()


if la_recherche_est_la():
    for famille in sorted((LA_RECHERCHE / "src").iterdir()):
        if famille.is_dir() and str(famille) not in sys.path:
            sys.path.insert(0, str(famille))

recherche = pytest.mark.skipif(not la_recherche_est_la(),
                               reason=f"le code de recherche (l'oracle) n'est pas sous {LA_RECHERCHE}")
reseau = pytest.mark.skipif(os.environ.get("VESUVE_RESEAU") != "1",
                            reason="lit le bucket public : lancer avec VESUVE_RESEAU=1")
