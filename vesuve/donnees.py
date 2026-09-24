"""Ce que le logiciel embarque de la recherche, par segment, et comment le relire.

Les fichiers sous `donnees/segments/<segment>/` sont extraits de `docs/mesures/` par
`outils/extraire_du_depot.py`, et un test exige qu'ils égalent une extraction fraîche : l'embarqué ne
peut pas dériver de sa source sans que la suite le dise.
"""
from __future__ import annotations

import gzip
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

LA_RACINE = Path(__file__).resolve().parent / "donnees" / "segments"


def les_segments_embarques() -> list[str]:
    return sorted(p.name for p in LA_RACINE.iterdir() if (p / "contexte.json").exists())


def _lire(chemin: Path):
    brut = chemin.read_bytes()
    return json.loads(gzip.decompress(brut) if chemin.suffix == ".gz" else brut)


@lru_cache(maxsize=8)
def le_segment(segment: str) -> dict:
    """{contexte, presence (A booléen), bandes publiées, sources de contrôle} d'un segment embarqué."""
    d = LA_RACINE / segment
    if not (d / "contexte.json").exists():
        raise FileNotFoundError(f"le segment {segment} n'est pas embarqué ; embarqués : {les_segments_embarques()}")
    presence = _lire(d / "presence.json.gz")
    A = np.array([[c == "1" for c in r] for r in presence["les_rangees"]], dtype=bool)
    sources = {nom: {"domaine": {f: {tuple(c) for c in s} for f, s in S["domaine"].items()},
                     "pas": {f: {(r, c): p for r, c, p in s} for f, s in S["pas"].items()}}
               for nom, S in _lire(d / "sources_de_controle.json.gz").items()}
    return {"contexte": _lire(d / "contexte.json"), "presence": A,
            "bandes": _lire(d / "bandes_publiees.json.gz")["les_bandes"], "sources": sources}
