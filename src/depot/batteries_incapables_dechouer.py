#!/usr/bin/env python3
"""Une batterie peut-elle seulement ÉCHOUER ?

⚠⚠⚠ Pourquoi ce fichier existe. `src/encre/typographie.py` imprimait « ALL PASS » et rendait
**0 inconditionnellement** : quels que soient ses contrôles, elle sortait verte, et
`temoins.sh` la comptait verte depuis toujours. Trouvé le 2026-08-27 par accident, en sondant
un tout autre correctif — la sonde a rendu la phrase `ALL PASS (2 failures, 28 checks)`, qui
se contredit elle-même.

⭐ C'est LE défaut que ce dépôt traque partout ailleurs, et il vivait dans l'instrument qui
sert à le traquer. Une vérification qui ne peut pas échouer est pire qu'aucune : elle occupe
la place d'une vraie et rend un compte de contrôles qui rassure.

## La règle, et pourquoi elle a dû être resserrée

⚠⚠ **Premier jet, trop faible, et il a raté le cas qui l'a fait naître** : « tous les `return`
rendent le littéral 0 ». Or `typographie.py` porte un `return 1` sur un tout autre chemin —
un refus d'argument — et rendait quand même `0` après avoir compté ses échecs. La sonde qui
remettait le défaut d'origine rendait **0 batterie signalée**, c'est-à-dire exactement la
panne que ce fichier existe pour attraper, chez lui.

⭐ La règle qui décide vraiment est plus étroite et colle au défaut : **la sortie qui SUIT le
verdict imprimé doit dépendre du compteur d'échecs.** Un `return 0` littéral juste après un
`print("ALL PASS …")` est une batterie verte par construction, quoi que ses contrôles aient
trouvé. C'est une propriété de l'arbre syntaxique, donc elle se lit sans exécuter.

⚠ La portée est dite : **les batteries Python**. Une batterie en shell se juge autrement, et
prétendre le contraire ferait passer ce contrôle pour plus large qu'il n'est.

⚠ Et un `verifier()` qui ne rend RIEN du tout (aucun `return`) est aussi signalé : Python
rend alors `None`, que `sys.exit` traite comme un succès.

Usage :
    uv run python src/depot/batteries_incapables_dechouer.py
    uv run python src/depot/batteries_incapables_dechouer.py --verifier
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def sorties_de(fonction: ast.FunctionDef) -> list[ast.Return]:
    """Les `return` de CETTE fonction, sans descendre dans les fonctions imbriquées.

    ⚠ Ne pas descendre est le point : un `verifier()` définit souvent un helper `v(...)`
    qui, lui, rend `None`. Compter ses `return` ferait signaler toutes les batteries du
    dépôt — l'alerte qui désigne tout et ne désigne rien.
    """
    trouves = []
    for noeud in ast.walk(fonction):
        if isinstance(noeud, ast.Return):
            # ⚠ On vérifie que le `return` appartient bien à `fonction` et non à une
            # fonction définie dedans, en remontant le chemin des parents annotés.
            if getattr(noeud, "_proprietaire", None) is fonction:
                trouves.append(noeud)
    return trouves


def annoter_proprietaires(fonction: ast.FunctionDef) -> None:
    """Marque chaque `return` avec la fonction qui le contient réellement."""
    def descendre(noeud, proprietaire):
        for enfant in ast.iter_child_nodes(noeud):
            if isinstance(enfant, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                descendre(enfant, enfant)
                continue
            if isinstance(enfant, ast.Return):
                enfant._proprietaire = proprietaire
            descendre(enfant, proprietaire)
    descendre(fonction, fonction)


def _est_le_verdict(noeud: ast.AST) -> bool:
    """Ce nœud imprime-t-il le verdict d'une batterie ?"""
    if not (isinstance(noeud, ast.Expr) and isinstance(noeud.value, ast.Call)):
        return False
    appel = noeud.value
    if not (isinstance(appel.func, ast.Name) and appel.func.id == "print"):
        return False
    texte = " ".join(ast.dump(a) for a in appel.args)
    return "ALL PASS" in texte or "temoins passent" in texte or "témoins passent" in texte


def peut_echouer(source: str) -> tuple[bool, str]:
    """(la batterie peut-elle échouer, la raison). Une source sans `verifier` est ignorée.

    ⚠ Ce qui est jugé est la sortie qui SUIT le verdict imprimé, pas l'ensemble des `return`
    de la fonction : une batterie a presque toujours un `return 1` ailleurs, sur un refus
    d'argument, et le compter suffisait à la déclarer saine.
    """
    try:
        arbre = ast.parse(source)
    except SyntaxError as e:
        return True, f"illisible ({e.msg})"
    for noeud in ast.walk(arbre):
        if not (isinstance(noeud, ast.FunctionDef) and noeud.name == "verifier"):
            continue
        annoter_proprietaires(noeud)
        sorties = sorties_de(noeud)
        if not sorties:
            return False, "aucun `return` : Python rend None, que sys.exit lit comme un succès"

        # Le verdict, puis ce que la fonction rend juste après lui.
        for bloc in ast.walk(noeud):
            corps = getattr(bloc, "body", None)
            if not isinstance(corps, list):
                continue
            for i, instruction in enumerate(corps):
                if not _est_le_verdict(instruction):
                    continue
                suite = corps[i + 1:]
                retours = [x for x in suite if isinstance(x, ast.Return)]
                if not retours:
                    return False, "rien n'est rendu après le verdict : Python rend None"
                r = retours[0]
                if r.value is None:
                    return False, "un `return` nu suit le verdict, donc None"
                if isinstance(r.value, ast.Constant):
                    return False, (f"la sortie qui suit le verdict est le littéral "
                                   f"{r.value.value!r} : le compte d'échecs est jeté")
                return True, "la sortie qui suit le verdict dépend du compte d'échecs"
        # Pas de verdict imprimé : on retombe sur la règle large.
        for r in sorties:
            if r.value is not None and not (isinstance(r.value, ast.Constant)
                                            and r.value.value == 0):
                return True, "pas de verdict imprimé, mais une sortie peut être non nulle"
        return False, "aucune sortie ne peut valoir autre chose que zéro"
    return True, "pas de fonction `verifier`"


def batteries(racine: Path) -> list[tuple[str, bool, str]]:
    """Chaque fichier Python de `src/` qui gère `--verifier`, et son verdict."""
    out = []
    for f in sorted(racine.glob("src/*/*.py")):
        texte = f.read_text(encoding="utf-8", errors="replace")
        if 'add_argument("--verifier"' not in texte:
            continue
        ok, raison = peut_echouer(texte)
        out.append((str(f.relative_to(racine)), ok, raison))
    return out


def verifier() -> int:
    """Auto-test HORS LIGNE, sur des sources fabriquées."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    honnete = "def verifier():\n    e = 0\n    return 1 if e else 0\n"
    v("une batterie qui rend 1 sur echec peut echouer", peut_echouer(honnete)[0])

    # ⚠⚠ Le cas EXACT trouve le 2026-08-27 : le compte est tenu, imprime, et jete — ET la
    # fonction porte un `return 1` ailleurs, sur un refus d'argument. C'est ce `return 1` qui
    # faisait passer la premiere version de ce controle a cote.
    aveugle = ("def verifier():\n"
               "    e = 3\n"
               "    if e < 0:\n"
               "        return 1\n"
               "    print(f'ALL PASS ({e} failures)')\n"
               "    return 0\n")
    ok, raison = peut_echouer(aveugle)
    v("le compte imprime puis jete ne peut PAS echouer", not ok)
    v("... et la raison le dit", "jeté" in raison)
    v("... meme quand un `return 1` existe AILLEURS dans la fonction",
      not peut_echouer(aveugle)[0])
    honnete_verdict = ("def verifier():\n"
                       "    e = 0\n"
                       "    print(f'ALL PASS ({e} failures)')\n"
                       "    return 1 if e else 0\n")
    v("le meme corps, sortie liee au compte, peut echouer", peut_echouer(honnete_verdict)[0])

    muette = "def verifier():\n    print('ok')\n"
    ok, raison = peut_echouer(muette)
    v("une batterie sans return ne peut pas echouer non plus", not ok)
    v("... et la raison nomme None", "None" in raison)

    nu = "def verifier():\n    if 1:\n        return\n    return 0\n"
    v("un `return` nu est traite comme None", not peut_echouer(nu)[0])

    # ⚠⚠ LE controle qui empeche l'alerte de tout designer : un `verifier` contient presque
    # toujours un helper interne qui rend None, et le compter ferait signaler tout le depot.
    avec_helper = ("def verifier():\n"
                   "    def v(nom, cond):\n"
                   "        if not cond:\n"
                   "            return\n"
                   "        return None\n"
                   "    return 1 if 0 else 0\n")
    v("un helper interne qui rend None ne fait pas condamner la batterie",
      peut_echouer(avec_helper)[0])

    v("une source sans `verifier` n'est pas jugee", peut_echouer("x = 1\n")[0])
    v("une source illisible est signalee comme telle",
      "illisible" in peut_echouer("def (\n")[1])

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    lignes = batteries(RACINE)
    aveugles = [(f, r) for f, ok, r in lignes if not ok]
    for f, r in aveugles:
        print(f"  ⚠⚠ {f} — {r}")
    print(f"{len(lignes)} batteries Python, **{len(aveugles)} incapables d'échouer**")
    return 1 if aveugles else 0


if __name__ == "__main__":
    sys.exit(main())
