"""Chaque commande `vesuve` du README est acceptée par le programme : une doc qui cite un drapeau renommé casse ici."""
from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest

from vesuve import cli

ICI = Path(__file__).resolve().parents[1]


def les_commandes() -> list[list[str]]:
    out = []
    for page in (ICI / "README.md", ICI / "exemples" / "README.md"):
        for bloc in re.findall(r"```bash\n(.*?)```", page.read_text(), flags=re.S):
            for ligne in bloc.splitlines():
                ligne = ligne.split("#")[0].strip()
                m = re.match(r"(?:uv run )?vesuve (.+)", ligne)
                if m:
                    out.append(shlex.split(m.group(1)))
    return out


def test_le_readme_cite_des_commandes():
    assert len(les_commandes()) >= 4  # une page sans commande ne vérifierait rien


@pytest.mark.parametrize("argv", les_commandes(), ids=lambda a: " ".join(a))
def test_chaque_commande_du_readme_est_acceptee(argv, monkeypatch):
    appels = []
    for nom in ("_grand_prize", "_progress", "_first_letters", "_paris4_title", "_demo", "_lire"):
        monkeypatch.setattr(cli, nom, lambda a, *r, _n=nom: appels.append(_n) or 0)
    assert cli.main(argv) == 0 and appels  # l'analyse passe, et un verbe est atteint sans rien exécuter
