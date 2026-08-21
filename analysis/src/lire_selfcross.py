#!/usr/bin/env python3
"""Lire un rapport `vc_tifxyz_selfcross` -- en refusant un verdict qui n'a rien mesure.

⚠⚠ Pourquoi ce fichier existe, et pourquoi il existe UNE fois. Six scripts de ce depot
lisaient le meme rapport avec le meme extrait de trois lignes :

    d = json.load(open(chemin)); sum(c['transverse'] for c in d['census'])

Aucun ne regardait `pairs_tested`. Or l'outil peut rendre
`clean_of_transverse_self_intersection: true` avec **zero paire testee** : son filtre
`--maxedge` (60 voxels par defaut) jette les quads dont une arete depasse le seuil, et sur
un maillage assez grossier il les jette **tous**. Mesure : `docs/sensibilite_maillage.json`
-- une surface qui porte 72 auto-intersections est declaree propre, `pairs_tested = 0`,
5202 quads jetes.

⭐ Un tel « propre » n'est pas un verdict, c'est une absence de mesure. Un portail construit
sur `--fail-on-crossing` laisserait passer n'importe quelle surface.

La lecture est donc **refusee** dans ce cas plutot que rendue avec une reserve : une valeur
rendue est une valeur qui finit dans un tableau, et une reserve qui voyage a cote d'un
nombre finit par ne plus voyager avec lui.

Usage :
    python3 analysis/src/lire_selfcross.py rapport.json           # imprime le compte
    python3 analysis/src/lire_selfcross.py rapport.json --champ paires
    python3 analysis/src/lire_selfcross.py --verifier             # temoin hors ligne
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class RapportVide(Exception):
    """Le rapport declare un verdict sans avoir teste la moindre paire de quads."""


def lire(chemin: str | Path) -> dict:
    """Rendre les comptes d'un rapport selfcross, ou lever si rien n'a ete teste."""
    d = json.loads(Path(chemin).read_text())
    census = d.get("census") or []
    r = {
        "transverse": sum(c.get("transverse", 0) for c in census),
        "paires": sum(c.get("pairs_tested", 0) for c in census),
        "jetes": sum(c.get("quads_dropped_for_edge_length", 0) for c in census),
        "coplanaire": sum(c.get("coplanar", 0) for c in census),
        "rasant": sum(c.get("grazing", 0) for c in census),
        "declare_propre": bool(d.get("clean_of_transverse_self_intersection")),
        "maxedge": (d.get("parameters") or {}).get("maxedge"),
    }
    if r["paires"] == 0:
        raise RapportVide(
            f"{chemin} : aucune paire testée ({r['jetes']} quads jetés pour longueur "
            f"d'arête, maxedge={r['maxedge']}). Le verdict « propre » ne mesure rien.")
    return r


def auditer(racine: Path) -> int:
    """Parcourir un arbre et nommer tout rapport dont le verdict ne mesure rien.

    ⚠ Existe parce que la question « un de nos chiffres publies depend-il d'un verdict
    vide ? » se repond par un nombre, pas par une conviction. Elle a ete posee le
    2026-08-20 sur l'arbre entier, et la reponse etait non -- mais elle etait *verifiee*.
    """
    vides, filtres, lus = [], [], 0
    for f in sorted(racine.rglob("*.json")):
        try:
            d = json.loads(f.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        if not isinstance(d, dict) or "clean_of_transverse_self_intersection" not in d:
            continue
        lus += 1
        try:
            r = lire(f)
        except RapportVide:
            vides.append(f)
            continue
        if r["jetes"]:
            filtres.append((f, r["jetes"], r["transverse"]))

    print(f"{lus} rapports selfcross sous {racine}")
    if vides:
        print(f"\n⚠⚠ {len(vides)} rapport(s) déclarent un verdict sans avoir testé une seule "
              f"paire — leur « propre » ne mesure rien :")
        for f in vides:
            print(f"     {f}")
    else:
        print("  ✅ aucun verdict rendu sur zéro paire testée")
    if filtres:
        print(f"\n⚠ {len(filtres)} rapport(s) où le filtre --maxedge a jeté des quads : le "
              f"compte porte sur une partie de la surface seulement :")
        for f, jetes, tr in filtres:
            print(f"     {f}  ({jetes} quads jetés, {tr} croisements sur le reste)")
    else:
        print("  ✅ aucun rapport où le filtre a jeté un quad")
    return 1 if vides else 0


def verifier() -> int:
    """Temoin hors ligne : le refus doit se declencher, et ne se declencher que la."""
    import tempfile

    echecs, controles = 0, 0

    def verifie(nom: str, condition: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not condition:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    def rapport(paires: int, jetes: int, transverse: int, propre: bool) -> str:
        f = Path(tempfile.mkdtemp()) / "r.json"
        f.write_text(json.dumps({
            "clean_of_transverse_self_intersection": propre,
            "parameters": {"maxedge": 60},
            "census": [{"pairs_tested": paires, "quads_dropped_for_edge_length": jetes,
                        "transverse": transverse, "coplanar": 0, "grazing": 0}]}))
        return str(f)

    r = lire(rapport(751169, 0, 240, False))
    verifie("un rapport plein se lit", r["transverse"] == 240 and r["paires"] == 751169)
    verifie("le drapeau propre est rendu tel quel", r["declare_propre"] is False)

    r = lire(rapport(32255, 0, 0, True))
    verifie("un vrai zéro se lit comme zéro", r["transverse"] == 0)
    verifie("... et reste déclaré propre", r["declare_propre"] is True)

    # ⭐ Le cas qui justifie le fichier : declare propre, rien de teste, tout jete.
    vide = rapport(0, 5202, 0, True)
    try:
        lire(vide)
        verifie("un rapport sans paire testée est REFUSÉ", False, "aucune exception")
    except RapportVide as e:
        verifie("un rapport sans paire testée est REFUSÉ", True)
        verifie("le refus nomme le nombre de quads jetés", "5202" in str(e), str(e))
        verifie("le refus nomme le maxedge", "maxedge=60" in str(e), str(e))

    # Le census peut avoir plusieurs entrees (deux triangulations) : elles s'additionnent.
    f = Path(tempfile.mkdtemp()) / "r.json"
    f.write_text(json.dumps({
        "clean_of_transverse_self_intersection": False,
        "parameters": {"maxedge": 60},
        "census": [{"pairs_tested": 10, "quads_dropped_for_edge_length": 0, "transverse": 159},
                   {"pairs_tested": 10, "quads_dropped_for_edge_length": 0, "transverse": 81}]}))
    verifie("les deux triangulations s'additionnent", lire(f)["transverse"] == 240)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rapport", nargs="?")
    ap.add_argument("--champ", default="transverse",
                    choices=["transverse", "paires", "jetes", "coplanaire", "rasant"])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--grille", action="store_true",
                    help="imprimer « colonnes lignes » de la grille au lieu du compte")
    ap.add_argument("--auditer", type=Path,
                    help="parcourir un arbre et nommer tout verdict rendu sur zéro paire")
    a = ap.parse_args()

    if a.verifier:
        return verifier()
    if a.auditer:
        return auditer(a.auditer)
    if not a.rapport:
        ap.error("donner un rapport, ou --verifier")
    if a.grille:
        # ⚠ Pourquoi ce mode : un maillage produit par `mode: gen_neighbor` n'a PAS de
        # `area_cm2` dans son meta.json (verifie : bbox, format, scale, source,
        # target_volume, type, uuid, vc_gsfs_*). Le rapport de selfcross, lui, porte
        # `grid_cols`/`grid_rows`, donc la taille de la surface est deja la — il suffit de
        # ne pas la jeter. Sans ca une campagne d'enchainement affiche « ? cm² » a chaque
        # spire et on ne peut pas dire si les spires gardent leur taille.
        import json as _json
        d = _json.loads(Path(a.rapport).read_text(encoding="utf-8"))
        c, r = d.get("grid_cols"), d.get("grid_rows")
        if not c or not r:
            print("rapport sans grid_cols/grid_rows", file=sys.stderr)
            return 3
        print(f"{c} {r}")
        return 0
    try:
        print(lire(a.rapport)[a.champ])
    except RapportVide as e:
        print(f"REFUS : {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
