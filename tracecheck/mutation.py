#!/usr/bin/env python3
"""Chaque détecteur doit porter du poids : le débrancher doit faire ROUGIR selftest.

⚠ Pourquoi ce fichier existe, et pourquoi il n'est pas redondant avec `selftest.py`.
Un contrôle par injection attrape un détecteur **aveugle** — on lui donne un défaut
connu et on exige qu'il le voie. Il n'attrape PAS un détecteur **absent**, parce qu'une
suite qui n'assertit jamais sur la sortie d'un détecteur ne peut pas distinguer « n'a
rien trouvé, correctement » de « n'a jamais été consulté ». La distinction compte le plus
pour le détecteur le plus faible, qui est exactement celui dont le silence ressemble le
plus à un corpus propre.

L'idée et sa formulation viennent de `enisme/tifxyz-surgeon`
(`tests/test_mutation.py`), dont l'auteur a découvert qu'il pouvait supprimer **trois de
ses quatre détecteurs** sans qu'aucun test ne le remarque. Voir `docs/28` §7.

C'est un test SUR LES TESTS : il remplace tour à tour chaque fonction porteuse par un
bouchon dégénéré et exige que `selftest.py` échoue. Un bouchon qui laisse la suite au
vert désigne une fonction dont **aucune assertion ne dépend** — donc une fonction qu'on
pourrait supprimer sans que rien ne le dise.

    python3 tracecheck/mutation.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent


def interprete() -> list[str]:
    """L'interpreteur qui a numpy.

    ⚠ Ce n'est pas forcement `sys.executable` : le python systeme de cette machine n'a
    pas numpy, et `src/outils/temoins.sh` lance ses batteries par `uv run python` DEPUIS
    `experiments/`, dont l'environnement l'a. Un script qui suppose son propre
    interpreteur declarerait ici « la suite de reference est deja rouge » sur une suite
    parfaitement verte -- ce qui est le pire des diagnostics : faux, et confiant.
    """
    import subprocess as sp
    essais = [
        ([sys.executable], None),
        (["uv", "run", "python"], RACINE / "experiments"),
        (["uv", "run", "python"], RACINE / "inference_xpu"),
    ]
    for cmd, cwd in essais:
        try:
            r = sp.run(cmd + ["-c", "import numpy"], capture_output=True,
                       cwd=str(cwd) if cwd else None, timeout=120)
        except Exception:
            continue
        if r.returncode == 0:
            return cmd, (str(cwd) if cwd else None)
    sys.exit("aucun interpreteur avec numpy — impossible de muter quoi que ce soit")

# Le bouchon de chaque fonction. ⚠ Il doit être DÉGÉNÉRÉ, pas cassé : lever une exception
# ferait echouer la suite pour la mauvaise raison — on veut prouver qu'une réponse
# *neutre et plausible* est détectée, pas qu'un plantage l'est.
BOUCHONS = {
    "judge": "lambda *a, **k: {'windows': 0, 'verdict': 'clean'}",
    "planarity_map": "lambda block, k, smooth=1: __import__('numpy').zeros("
                     "(block.shape[0]//k, block.shape[1]//k, block.shape[2]//k), 'float32')",
    "_neighbourhood": "lambda value, valid: (value, valid)",
    "lit_voxel": "lambda block, k, iz, iy, ix: True",
    "decode": "lambda raw, meta, expected: raw[:expected]",
    "chunk_key": "lambda meta, level, cy, cx, cz=0: f'{level}/0.0.0'",
    "find_surface_volume": "lambda *a, **k: None",
}

PREAMBULE = """
import runpy, sys
from pathlib import Path
sys.path.insert(0, {ici!r})
import tracecheck as T
T.{nom} = {bouchon}
runpy.run_path({selftest!r}, run_name='__main__')
"""


def main() -> int:
    selftest = ICI / "selftest.py"
    py, cwd = interprete()
    print(f"interprete : {' '.join(py)}" + (f"  (depuis {cwd})" if cwd else ""))
    ref = subprocess.run(py + [str(selftest)], capture_output=True, text=True, cwd=cwd)
    if "ALL PASS" not in ref.stdout:
        print("la suite de reference est DEJA rouge — rien a muter")
        print(ref.stdout[-800:])
        return 1
    # ⚠⚠ NE PAS reimprimer la ligne de reference telle quelle. Elle contient "ALL PASS",
    # et `src/outils/temoins.sh` declare une batterie verte en cherchant CETTE chaine dans la
    # sortie -- puis affiche le PREMIER match. Une reference recopiee rendait donc la
    # batterie verte meme si la mutation echouait, et lui faisait afficher les 38 checks
    # du selftest au lieu des 7 de la mutation. Deuxieme fois en une heure que ce piege
    # se paie ; la chaine magique ne doit apparaitre QU'a la ligne de verdict.
    ligne = [l for l in ref.stdout.splitlines() if "ALL PASS" in l][0]
    print(f"reference : {ligne.replace('ALL PASS', 'suite verte')}\n")

    survivants = []
    for nom, bouchon in BOUCHONS.items():
        code = PREAMBULE.format(ici=str(ICI), nom=nom, bouchon=bouchon,
                                selftest=str(selftest))
        r = subprocess.run(py + ["-c", code], capture_output=True, text=True, cwd=cwd)
        rouge = "ALL PASS" not in r.stdout
        print(f"  {'✅' if rouge else '❌'} {nom:<22} "
              f"{'la suite rougit' if rouge else 'LA SUITE RESTE VERTE — aucune assertion n en depend'}")
        if not rouge:
            survivants.append(nom)

    print()
    if survivants:
        # ⚠ NE PAS imprimer "ALL PASS" ici : src/outils/temoins.sh cherche cette chaine pour
        # declarer une batterie verte, et l'imprimer en echec rendrait CE controle
        # incapable d'echouer -- exactement le defaut qu'il existe pour attraper.
        print(f"{len(survivants)} detecteur(s) sans assertion : {survivants}")
        return 3
    print(f"ALL PASS (0 failures, {len(BOUCHONS)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
