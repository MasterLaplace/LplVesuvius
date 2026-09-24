"""Les frontières du logiciel, vérifiées et non seulement dessinées.

Un prix n'importe jamais un autre prix ; ce qu'ils partagent vit dans un module partagé (`treillis/` pour le
Grand Prize et l'audit, `rendu/` pour First Letters et le titre) ou dans le commun. Et le noyau C ne dépend de
rien : c'est lui que tout le reste appelle.
"""
from __future__ import annotations

import ast
from pathlib import Path

LE_PAQUET = Path(__file__).resolve().parents[1] / "vesuve"
LES_PRIX = ("grand_prize", "first_letters", "paris4_title", "progress")


def _imports(fichier: Path) -> set[str]:
    out = set()
    for n in ast.walk(ast.parse(fichier.read_text())):
        if isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
        elif isinstance(n, ast.Import):
            out |= {a.name for a in n.names}
    return out


def test_un_prix_nimporte_jamais_un_autre_prix():
    vus = 0
    for prix in LES_PRIX:
        for f in (LE_PAQUET / prix).glob("*.py"):
            for m in _imports(f):
                autres = [p for p in LES_PRIX if p != prix and m.startswith(f"vesuve.{p}")]
                assert not autres, f"{f.relative_to(LE_PAQUET)} importe {m}"
            vus += 1
    assert vus >= 8


def test_les_modules_partages_nimportent_aucun_prix():
    for dossier in ("treillis", "rendu"):
        for f in (LE_PAQUET / dossier).glob("*.py"):
            for m in _imports(f):
                assert not any(m.startswith(f"vesuve.{p}") for p in LES_PRIX), f"{f.name} importe {m}"


def test_le_noyau_c_ne_depend_que_de_la_bibliotheque_standard():
    for f in (LE_PAQUET.parent / "noyau" / "src").glob("*.c"):
        for ligne in f.read_text().splitlines():
            if ligne.startswith("#include"):
                assert ligne.split()[1].strip('<>"') in {"vesuve.h", "math.h", "stdlib.h", "stdint.h", "stddef.h",
                                                         "string.h"}, f"{f.name} : {ligne}"
