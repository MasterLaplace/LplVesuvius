#!/usr/bin/env python3
"""Quel artefact versionne n'a AUCUN producteur dans l'arbre ?

⚠ La regle centrale du depot : *un chiffre publie dont le calcul n'est pas dans l'arbre
n'est pas un resultat, c'est une anecdote.* Elle porte sur les chiffres ; elle vaut aussi
pour les ARTEFACTS qui les portent. Un fichier de mesure versionne dont le script est
reste dans un terminal est un resultat qu'on ne peut ni rejouer, ni verifier, ni corriger.

⚠⚠ Ce script existe parce que le cas s'est produit : `docs/06` §3.2 nomme
`baseline_sweep.py` et `variant_correlate.py` comme les outils d'une mesure, et **aucun
des deux n'est dans l'arbre**. Dix-sept artefacts `docs/sweep_*.jsonl` en dependent.

Un artefact est considere comme PRODUIT si son nom -- ou le motif dont il derive --
apparait dans un script de `src/`. C'est une heuristique volontairement
LARGE : elle ne prouve pas qu'un script produit vraiment le fichier, elle prouve seulement
que quelque chose dans l'arbre le nomme. Un artefact qu'elle signale n'a donc, lui,
vraiment aucun producteur -- c'est le sens utile de l'alerte.

Usage :
    python3 src/depot/artefacts_orphelins.py [--verifier]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
# ⚠ `experiments/src` en fait partie : `docs/11` nomme
# `experiments/src/excision/sensibilite_centre.py`, et l'omettre faisait signaler comme
# orphelin un artefact parfaitement produit. Une liste de sources trop etroite fabrique
# des faux positifs, et un audit qui en fabrique cesse d'etre lu.
SOURCES = ("src", "tracecheck", "experiments/src", "inference_xpu/src")
SUFFIXES = (".json", ".jsonl", ".tsv", ".txt")

# ⚠ Ces artefacts sont produits par une chaine externe (VC3D, un outil `vc_*`) ou sont des
# entrees plutot que des sorties. Les exclure est une DECISION, pas un oubli : chacun est
# nomme, et la raison avec.
EXEMPTS = {
    "docs/mesures/excision_samples.tsv": "sortie de l'experience d'excision (experiments/src/excision)",
    "src/outils/repos.tsv": "manifeste ecrit a la main, pas une mesure",
}


def corpus_scripts() -> str:
    parts = []
    for d in SOURCES:
        for f in (RACINE / d).rglob("*"):
            if f.suffix in (".py", ".sh") and "__pycache__" not in str(f):
                parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def artefacts() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True)
    return [RACINE / l for l in out.stdout.splitlines()
            if l.startswith(("docs/", "data/")) and Path(l).suffix in SUFFIXES]


def nomme_par(nom: str, src: str) -> bool:
    """Le nom, ou la racine dont il derive, apparait-il dans un script ?

    ⚠ Un artefact s'appelle souvent `sweep_PHerc0139.jsonl` alors que le script ecrit
    `sweep_$SCROLL.jsonl`. On teste donc le nom entier, puis des prefixes de plus en plus
    courts, jusqu'a une racine d'au moins quatre caracteres -- en dessous, un prefixe
    matche n'importe quoi et l'heuristique cesserait de pouvoir signaler quoi que ce soit.
    """
    if nom in src:
        return True
    tige = Path(nom).stem
    while len(tige) >= 4:
        if re.search(r"\b" + re.escape(tige), src):
            return True
        coupe = max(tige.rfind("_"), tige.rfind("-"))
        if coupe < 4:
            break
        tige = tige[:coupe]
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verifier", action="store_true",
                    help="sortie 3 s'il existe un artefact orphelin non exempte")
    a = ap.parse_args()

    src = corpus_scripts()
    tous = artefacts()
    orphelins = []
    for f in tous:
        rel = str(f.relative_to(RACINE))
        if rel in EXEMPTS:
            continue
        # ⚠ Un artefact par SEGMENT s'appelle d'apres l'horodatage du segment, que
        # AUCUN script ne peut contenir -- le script ecrit `<dossier>/<segment>.json`,
        # et c'est le DOSSIER qu'il nomme. Chercher le nom de fichier seul signalait
        # 389 orphelins sur 568, dont la quasi-totalite est produite : une alerte qui
        # designe les deux tiers du corpus ne designe rien.
        if nomme_par(f.name, src):
            continue
        if f.parent != RACINE / "docs" and nomme_par(f.parent.name, src):
            continue
        orphelins.append(rel)

    print(f"{len(tous)} artefacts versionnés, {len(EXEMPTS)} exemptés, "
          f"**{len(orphelins)} sans producteur**\n")
    for o in sorted(orphelins):
        print(f"  ⚠ {o}")
    if EXEMPTS:
        print("\n  exemptés, avec la raison :")
        for k, v in EXEMPTS.items():
            print(f"    {k} — {v}")

    if not a.verifier:
        return 0
    print()
    if orphelins:
        print(f"{len(orphelins)} artefact(s) dont le calcul n'est pas dans l'arbre")
        return 3
    print(f"ALL PASS (0 failures, {len(tous)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
