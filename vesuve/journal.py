"""Le journal : une ligne par événement, sur la sortie d'erreur, jamais sur la sortie standard.

Une ligne porte un CODE stable (qu'on filtre), des champs `clé=valeur` (qu'on agrège), et
l'identifiant du run (qu'on corrèle). Le niveau se règle sans rien reconstruire :
`VESUVE_JOURNAL=DEBUG|INFO|WARN|ERROR` (INFO par défaut).

⚠ Le journal n'est pas un canal de résultat : ce qu'un pipeline conclut va dans son `rapport.json`,
et rien ne relit jamais ces lignes pour décider quoi que ce soit.
"""
from __future__ import annotations

import os
import sys
import uuid
from typing import TextIO

NIVEAUX = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}


class Journal:
    """Un journal injecté : les tests lui donnent un flux, les pipelines celui du processus."""

    def __init__(self, flux: TextIO | None = None, niveau: str | None = None, run: str | None = None):
        self.flux = flux if flux is not None else sys.stderr
        choisi = (niveau or os.environ.get("VESUVE_JOURNAL", "INFO")).upper()
        if choisi not in NIVEAUX:
            raise ValueError(f"niveau de journal inconnu {choisi!r} : attendu l'un de {sorted(NIVEAUX)}")
        self.seuil = NIVEAUX[choisi]
        self.run = run or uuid.uuid4().hex[:8]

    def _ecrire(self, niveau: str, code: str, champs: dict) -> None:
        if NIVEAUX[niveau] < self.seuil:
            return
        morceaux = [f"{niveau:<5}", code, f"run={self.run}"]
        for cle, valeur in champs.items():
            texte = str(valeur)
            morceaux.append(f"{cle}={texte!r}" if (" " in texte or "=" in texte or not texte) else f"{cle}={texte}")
        print(" ".join(morceaux), file=self.flux, flush=True)

    def debug(self, code: str, **champs) -> None:
        self._ecrire("DEBUG", code, champs)

    def info(self, code: str, **champs) -> None:
        self._ecrire("INFO", code, champs)

    def warn(self, code: str, **champs) -> None:
        self._ecrire("WARN", code, champs)

    def error(self, code: str, **champs) -> None:
        self._ecrire("ERROR", code, champs)
