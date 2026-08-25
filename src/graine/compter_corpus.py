#!/usr/bin/env python3
"""Compter ce que chaque artefact de corpus contient REELLEMENT.

⚠ Pourquoi ce script existe. Trois documents annoncaient des tailles de corpus qui ne
correspondaient pas a leur propre artefact : « Scroll 1 (72 segments) » pour un fichier
de 80 entrees, « 12 segments » pour un tableau de 11 lignes, « treillis 6 x 12, 72
points » pour un artefact ou `sondees` vaut 50. Le 72 existe bien -- mais dans une AUTRE
campagne, celle des fibres. Un compte recopie d'un document a l'autre migre entre corpus
sans que rien ne le signale.

Ce script rend, pour chaque artefact versionne : le nombre d'entrees, les valeurs
distinctes des compteurs par entree, et les rouleaux representes. Un document qui cite un
de ces nombres peut le retrouver ici en une commande.

Usage :
    python3 src/graine/compter_corpus.py [--json sortie.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

# ⚠ Les compteurs PAR ENTREE (combien de fenetres sondees dans un segment) sont ceux qui
# migrent le plus facilement vers une phrase qui parle de SEGMENTS. On les sort donc a
# part, avec leur nom, pour qu'une confusion saute aux yeux.
COMPTEURS = ("sondees", "utilisables", "voisins_compares", "layers", "avec_matiere")


def rouleau_de(entree: dict) -> str:
    """Le rouleau d'une entree, deduit du chemin zarr ou du nom de segment."""
    s = str(entree.get("zarr") or entree.get("segment") or "")
    m = re.search(r"(PHerc[0-9A-Za-z]+|Scroll\d+)", s)
    if m:
        return m.group(1)
    # ⚠ Un segment de Scroll 1 est nomme par un horodatage seul : l'absence de prefixe
    # est donc une information, pas un echec de lecture.
    return "Scroll1 (horodatage seul)" if re.fullmatch(r"\d{14}", s) else "?"


def examiner(chemin: Path) -> dict | None:
    try:
        d = json.loads(chemin.read_text(encoding="utf-8"))
    except Exception:
        return None
    items = d if isinstance(d, list) else (
        d.get("segments") or d.get("results") or
        (list(d.values())[0] if len(d) == 1 and isinstance(list(d.values())[0], list) else None))
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        return None
    info = {"fichier": str(chemin.relative_to(RACINE)), "entrees": len(items)}
    for c in COMPTEURS:
        # ⚠ Un compteur peut porter une LISTE dans certains artefacts (par ex. les
        # couches sondees enumerees plutot que comptees). On garde alors sa longueur, et
        # on le DIT, plutot que de planter ou de la confondre avec un scalaire.
        brut = [i.get(c) for i in items if i.get(c) is not None]
        listes = [len(v) for v in brut if isinstance(v, list)]
        vals = [v for v in brut if not isinstance(v, list)]
        if listes:
            u = Counter(listes)
            info[c] = (f"liste de {listes[0]} éléments (constant)" if len(u) == 1
                       else f"listes de {min(listes)}–{max(listes)} éléments")
            continue
        if vals:
            u = Counter(vals)
            info[c] = (f"{vals[0]} (constant)" if len(u) == 1
                       else f"{min(vals)}–{max(vals)}, {len(u)} valeurs")
    r = Counter(rouleau_de(i) for i in items)
    info["rouleaux"] = dict(r.most_common(4))
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    a = ap.parse_args()

    lignes = [x for x in (examiner(p) for p in sorted((RACINE / "docs").glob("*.json")))
              if x]
    if not lignes:
        print("aucun artefact de corpus lisible")
        return 1

    for l in lignes:
        print(f"\n{l['fichier']}  —  {l['entrees']} entrées")
        for c in COMPTEURS:
            if c in l:
                print(f"    {c:<18} {l[c]}")
        print(f"    rouleaux           {l['rouleaux']}")

    print(f"\n{len(lignes)} artefact(s) de corpus")
    # ⚠ Le piege nomme, puisque c'est la raison d'etre du script.
    print("⚠ un compteur PAR ENTREE (sondees, utilisables…) n'est PAS un nombre de segments")

    if a.json:
        Path(a.json).write_text(json.dumps(lignes, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
