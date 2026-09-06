#!/usr/bin/env python3
"""La batterie atteint-elle le chemin qui PRODUIT le nombre publié ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Le 2026-09-05, un patch appliqué à moitié a laissé
`derouler_des_deux_bords.py` avec un enregistrement qui référençait trois variables
inexistantes — et **la batterie est restée verte**, parce qu'elle n'appelait pas `mesurer`.
Elle testait les briques une par une, jamais leur assemblage, et l'assemblage est exactement
ce qui produit le nombre qu'on publie.

⭐ Une batterie verte sur un module dont le seul chemin non testé est celui qui produit le
nombre publié est une batterie qui **ne peut pas échouer là où ça compte**. C'est le cousin
de « une vérification incapable d'échouer » — celle-ci peut échouer, mais pas sur ce qui
compte — et il ne se voit pas en lisant le verdict, qui est vert et sincère.

## La règle, et ce qu'elle ne prétend pas

⚠⚠ La règle est une propriété du **graphe d'appels du module**, donc elle se lit sans rien
exécuter : on ferme les appels depuis `main`, on ferme les appels depuis `verifier`, et ce
que le premier atteint sans que le second l'atteigne est le chemin non couvert. `main` est le
point d'entrée réel du module — c'est lui qui produit le nombre publié —, donc c'est bien la
différence qui mesure la dette.

⚠ La portée est **les modules qui publient une mesure**. Un script qui ne publie rien peut
laisser du code hors de sa batterie sans que ce soit la faute nommée ici, et l'y compter
gonflerait le chiffre avec des cas qui ne sont pas celui-là.

⚠⚠ CE QUE ÇA NE MESURE PAS, et il faut le dire : le graphe ne suit que les appels **par nom**
à des fonctions du module. Un appel indirect — passé en argument, résolu par un dictionnaire —
n'est pas vu, donc une fonction peut être comptée non couverte alors qu'elle tourne. L'erreur
va dans le sens prudent : la dette est **surestimée**, jamais cachée.

⚠ Et une fonction couverte n'est pas une fonction testée : ce contrôle dit qu'elle est
ATTEINTE par la batterie, pas que quoi que ce soit y est vérifié. Prétendre l'inverse ferait
de ce fichier la vérification trop confiante qu'il existe pour traquer.

Usage :
    uv run python src/depot/le_chemin_du_nombre_publie.py
    uv run python src/depot/le_chemin_du_nombre_publie.py \\
        --json docs/mesures/le_chemin_du_nombre_publie.json
    uv run python src/depot/le_chemin_du_nombre_publie.py --verifier
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
IGNORES = {".git", "__pycache__", "build", "data", "scroll", ".venv", "node_modules"}


def fonctions_du_module(arbre: ast.Module) -> dict[str, ast.FunctionDef]:
    """Les fonctions définies au niveau du module, par nom.

    ⚠ Seulement au niveau du module : une fonction imbriquée n'est appelable que par celle qui
    la contient, donc elle est couverte exactement quand sa mère l'est, et la compter à part
    ferait deux nœuds pour un seul chemin.
    """
    return {n.name: n for n in arbre.body if isinstance(n, ast.FunctionDef)}


def appels_de(fonction: ast.FunctionDef, connues: set[str]) -> set[str]:
    """Les fonctions du module que celle-ci appelle par leur nom."""
    out = set()
    for n in ast.walk(fonction):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in connues:
            out.add(n.func.id)
    return out


def atteintes_depuis(depart: str, defs: dict[str, ast.FunctionDef]) -> set[str]:
    """La fermeture des appels depuis `depart`, `depart` **exclu**.

    ⚠ Le départ est exclu pour que la différence entre deux fermetures ne contienne jamais
    `main` lui-même : le point d'entrée n'est pas un chemin, c'est ce qui en ouvre un.
    """
    vus, pile = set(), [depart]
    while pile:
        courant = pile.pop()
        for suivant in appels_de(defs[courant], set(defs)):
            if suivant not in vus:
                vus.add(suivant)
                pile.append(suivant)
    return vus - {depart}


def publie_une_mesure(source: str, arbre: ast.Module) -> bool:
    """Ce module ÉCRIT-il une mesure, ou se contente-t-il d'en lire une ?

    ⚠⚠⚠ LA DISTINCTION EST TOUT L'INTÉRÊT DE LA PORTÉE, et ma première règle la ratait :
    elle acceptait n'importe quelle mention littérale de `docs/mesures`, donc elle comptait
    comme publieur un module qui ne fait que **lire** l'écart entre spires. Trouvé en voyant
    `le_corpus_des_spires.py` — un pur lecteur, dont la seule fonction non couverte est celle
    qui lit le dépôt distant — apparaître dans la liste des modules en dette. Un lecteur n'a pas
    de nombre publié, donc le défaut nommé ici ne peut pas lui arriver, et l'y compter gonflait
    le chiffre avec des cas qui ne sont pas celui-là.

    ⚠⚠ Le signe retenu est donc l'ÉCRITURE, sous ses deux formes, parce que ce dépôt publie
    deux sortes d'artefacts : un module **sérialise et écrit** un fichier (une mesure), ou il
    **enregistre une image** (une figure). Exiger la première seule effacerait les figures de la
    portée — or `dessiner` était la deuxième branche la plus souvent laissée dehors, et c'est
    exactement le même défaut : un dessin que personne n'exerce.

    ⚠ Sérialiser pour AFFICHER n'est pas publier : les deux signes de la première forme sont
    exigés ensemble.
    """
    noms = {getattr(n.func, "attr", None) for n in ast.walk(arbre) if isinstance(n, ast.Call)}
    mesure = bool(noms & {"dumps", "dump"}) and bool(noms & {"write_text", "write"})
    return mesure or "save" in noms


def juger(chemin: Path) -> dict | None:
    """Le verdict pour un fichier, ou `None` s'il est hors de portée."""
    try:
        source = chemin.read_text(encoding="utf-8")
        arbre = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return None
    defs = fonctions_du_module(arbre)
    if "verifier" not in defs or "main" not in defs:
        return None
    if not publie_une_mesure(source, arbre):
        return None
    produit = atteintes_depuis("main", defs)
    couvert = atteintes_depuis("verifier", defs) | {"verifier"}
    non_couvert = sorted(produit - couvert)
    # ⚠⚠ CE QUE `main` APPELLE DIRECTEMENT ET QUE LA BATTERIE N'ATTEINT PAS est la TÊTE du
    # chemin non couvert, et c'est le chiffre qui décide de l'effort : une fonction d'aide
    # laissée dehors est rattrapée en couvrant sa mère, alors qu'une tête de chemin est une
    # branche entière que rien n'exerce. Les deux comptés ensemble se liraient pareil.
    en_tete = sorted(appels_de(defs["main"], set(defs)) & set(non_couvert))
    return dict(fichier=str(chemin.relative_to(RACINE)),
                fonctions=len(defs), atteintes_par_main=len(produit),
                atteintes_par_la_batterie=len(couvert - {"verifier"}),
                non_couvert=non_couvert, en_tete_de_chemin=en_tete,
                en_dette=bool(non_couvert))


def mesurer(racine: Path | None = None) -> dict:
    """Le dépôt entier, fichier par fichier."""
    racine = RACINE if racine is None else racine
    lignes = []
    for chemin in sorted(racine.rglob("*.py")):
        if IGNORES & set(chemin.relative_to(racine).parts):
            continue
        verdict = juger(chemin)
        if verdict is not None:
            lignes.append(verdict)
    en_dette = [e for e in lignes if e["en_dette"]]
    # ⚠ Le compte des fonctions non couvertes est rendu à côté du compte de modules : un dépôt
    # où cent modules laissent une fonction dehors et un dépôt où un module en laisse cent
    # n'ont pas la même dette, et un seul nombre les confondrait.
    return dict(
        modules_qui_publient=len(lignes),
        modules_en_dette=len(en_dette),
        fonctions_non_couvertes=sum(len(e["non_couvert"]) for e in en_dette),
        # ⚠⚠ CE QUI N'EST PAS PUBLIÉ ICI, ET POURQUOI. J'avais d'abord compté « les modules
        # dont la tête de chemin est dehors » — 67 sur 67. Ce n'est pas un constat, c'est une
        # IDENTITÉ : la couverture se propage vers le bas, donc si une fonction quelconque est
        # hors de portée, celle que `main` appelle en premier sur ce chemin l'est forcément.
        # Un nombre qui ne peut prendre qu'une valeur se lit comme une découverte et n'en est
        # pas une. Ce qui reste informatif est le NOM de ces têtes : il dit quelle branche du
        # dépôt n'est jamais exercée.
        tetes_de_chemin={
            nom: sum(1 for e in en_dette if nom in e["en_tete_de_chemin"])
            for nom in sorted({n for e in en_dette for n in e["en_tete_de_chemin"]})},
        par_famille={
            f: dict(publient=sum(1 for e in lignes if e["fichier"].split("/")[1] == f),
                    en_dette=sum(1 for e in en_dette if e["fichier"].split("/")[1] == f))
            for f in sorted({e["fichier"].split("/")[1] for e in lignes})},
        part_en_dette=(round(len(en_dette) / len(lignes), 3) if lignes else None),
        lignes=lignes)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def defs_de(texte: str) -> dict[str, ast.FunctionDef]:
        return fonctions_du_module(ast.parse(texte))

    # --- la fermeture des appels ---
    d = defs_de("def a():\n b()\ndef b():\n c()\ndef c():\n pass\ndef d():\n pass\n")
    v("la fermeture suit les appels en chaîne", atteintes_depuis("a", d) == {"b", "c"},
      str(sorted(atteintes_depuis("a", d))))
    v("... et n'inclut pas son propre départ", "a" not in atteintes_depuis("a", d))
    v("... et ne va pas chercher ce que personne n'appelle", "d" not in atteintes_depuis("a", d))
    boucle = defs_de("def a():\n b()\ndef b():\n a()\n")
    v("une récursion mutuelle ne boucle pas à l'infini",
      atteintes_depuis("a", boucle) == {"b"}, str(sorted(atteintes_depuis("a", boucle))))
    v("... et le départ réapparaît quand il est vraiment rappelé",
      "a" in atteintes_depuis("b", boucle))

    # --- la portée ---
    sans = "def main():\n mesurer()\ndef mesurer():\n pass\n"
    v("un module qui ne publie rien n'est pas compté",
      not publie_une_mesure(sans, ast.parse(sans)))
    ecrit = 'import json\np.write_text(json.dumps(r))\n'
    v("... un module qui sérialise ET écrit est compté",
      publie_une_mesure(ecrit, ast.parse(ecrit)))
    # ⚠⚠ LE CAS QUI A FAIT RESSERRER LA RÈGLE : un pur LECTEUR de `docs/mesures` était compté
    # publieur, donc rangé en dette pour une fonction qu'aucune batterie ne peut exercer.
    lecteur = ('import json\nW = "docs/mesures/x.json"\n'
               'print(json.dumps(json.loads(open(W).read())))\n')
    v("... mais un module qui LIT une mesure et n'écrit rien ne l'est pas",
      not publie_une_mesure(lecteur, ast.parse(lecteur)))
    affiche = 'import json\nprint(json.dumps(r))\n'
    v("... et sérialiser pour afficher n'est pas publier",
      not publie_une_mesure(affiche, ast.parse(affiche)))
    # ⚠ Une figure publie une IMAGE : l'exclure ferait sortir de la portée la deuxième branche
    # la plus souvent laissée dehors, alors que c'est le même défaut.
    image = "toile.save(sortie)\n"
    v("... une figure qui enregistre une image est comptée",
      publie_une_mesure(image, ast.parse(image)))

    # --- le verdict, sur deux modules fabriqués ---
    # ⚠⚠ La dette est écrite dans la fixture, pas cherchée : `enregistrer` n'est atteint que
    # par `main`. Sans les deux cas, « aucun module en dette » et « ce contrôle ne regarde
    # rien » rendraient la même chose.
    dette = ('import json\n'
             'def enregistrer(r):\n pass\n'
             'def mesurer():\n enregistrer(1)\n'
             'def verifier():\n return 0\n'
             'def main():\n mesurer()\n'
             'S.write_text(json.dumps(1))\n')
    saine = dette.replace("def verifier():\n return 0\n",
                          "def verifier():\n mesurer()\n return 0\n")
    tmp = RACINE / "build" / "chemin_du_nombre_publie"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "en_dette.py").write_text(dette, encoding="utf-8")
    (tmp / "saine.py").write_text(saine, encoding="utf-8")
    (tmp / "sans_batterie.txt").write_text(dette.replace("def verifier():\n return 0\n", ""),
                                           encoding="utf-8")
    jd, js = juger(tmp / "en_dette.py"), juger(tmp / "saine.py")
    v("un module sans batterie est hors de portée, pas compté sain",
      juger(tmp / "sans_batterie.txt") is None)
    v("un module dont la batterie n'atteint pas sa mesure est signalé",
      jd is not None and jd["en_dette"], str(jd and jd["non_couvert"]))
    v("... et les fonctions manquantes sont nommées",
      jd is not None and jd["non_couvert"] == ["enregistrer", "mesurer"],
      str(jd and jd["non_couvert"]))
    # ⚠ `enregistrer` n'est PAS une tête de chemin : `main` ne l'appelle pas, `mesurer` si.
    # Confondre les deux ferait lire une fonction d'aide comme une branche entière.
    v("... et la TÊTE du chemin non couvert est distinguée de ce qui pend dessous",
      jd is not None and jd["en_tete_de_chemin"] == ["mesurer"],
      str(jd and jd["en_tete_de_chemin"]))
    v("un module dont la batterie appelle sa mesure ne l'est PAS",
      js is not None and not js["en_dette"], str(js and js["non_couvert"]))
    r = mesurer(tmp)
    v("le balayage rend les deux, et n'en compte qu'un en dette",
      (r["modules_qui_publient"], r["modules_en_dette"]) == (2, 1), str(r["part_en_dette"]))
    v("... et il nomme la branche que personne n'exerce",
      r["tetes_de_chemin"] == {"mesurer": 1}, str(r["tetes_de_chemin"]))
    v("... et le compte de fonctions non couvertes ne se confond pas avec celui des modules",
      r["fonctions_non_couvertes"] == 2, str(r["fonctions_non_couvertes"]))
    # ⚠ L'affichage est exercé sur ce résultat fabriqué, et c'est le même remède que celui
    # que ce fichier recommande : sorti de `main`, il tourne hors ligne, donc une clé renommée
    # lève ici plutôt que le jour de la publication.
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(r)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et nomme le module en dette",
      souci is None and "en_dette.py" in tampon.getvalue(), souci or "")
    for f in list(tmp.glob("*.py")) + list(tmp.glob("*.txt")):
        f.unlink()

    # --- ce fichier ne doit pas porter la dette qu'il mesure ---
    moi = juger(Path(__file__).resolve())
    v("l'instrument lui-même atteint sa propre mesure",
      moi is not None and not moi["en_dette"], str(moi and moi["non_couvert"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible du balayage."""
    print(f"{r['modules_qui_publient']} module(s) publient une mesure · "
          f"**{r['modules_en_dette']} en dette** ({r['part_en_dette']}) · "
          f"{r['fonctions_non_couvertes']} fonction(s) hors de portée de leur batterie\n")
    tetes = sorted(r["tetes_de_chemin"].items(), key=lambda kv: -kv[1])[:6]
    print("  têtes de chemin jamais exercées : "
          + ", ".join(f"{n} ({c})" for n, c in tetes) + "\n")
    for f, d in r["par_famille"].items():
        print(f"  {f:<10} {d['en_dette']:>3} en dette sur {d['publient']:>3}")
    print()
    for e in sorted((x for x in r["lignes"] if x["en_dette"]),
                    key=lambda x: -len(x["non_couvert"])):
        print(f"  {len(e['non_couvert']):>3} · {e['fichier']}")
        print(f"        {', '.join(e['non_couvert'])}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
