#!/usr/bin/env python3
"""Chaque ⏳ des documents est-il CLASSÉ — et son classement tient-il encore ?

⚠⚠ POURQUOI CE FICHIER EXISTE. Le dépôt porte **41 sabliers** répartis sur 18 documents.
Certains sont de vraies tâches ouvertes, d'autres sont des **titres de section** dans un
récit daté, un autre est la **légende** d'un registre. Rien ne les distinguait, donc la
question « reste-t-il du travail laissé de côté ? » n'avait pas de réponse mécanique — elle
se répondait en relisant dix-huit documents, ce que personne ne refait.

⭐ Le partage est celui que ce dépôt applique déjà à `murs_et_causes` : l'**inventaire** est
DÉRIVÉ des documents, donc il ne peut pas pourrir ; le **verdict** sur chaque marqueur est un
jugement, donc il vit dans un registre — et les deux se vérifient l'un contre l'autre.

  ⭐⭐ Un marqueur sans entrée de registre est **non classé** : le contrôle échoue.
     Une entrée dont l'ancre a disparu du document est **périmée** : le contrôle échoue.

C'est ce double sens qui empêche la liste de mentir. Un registre seul dériverait du texte ;
un scan seul ne dirait jamais si un sablier est une tâche ou un titre de chapitre.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
REGISTRE = RACINE / "docs" / "registres" / "taches.tsv"
SABLIER = "⏳"

ETATS = ("ouverte", "faite", "perimee", "recit", "legende")
"""Ce qu'un sablier peut être.

- `ouverte`  : du travail qui reste, et personne ne l'a fait
- `faite`    : le travail a été fait ; le sablier n'a pas suivi
- `perimee`  : la question a cessé de se poser (une mesure l'a dépassée)
- `recit`    : un titre de section ou une phrase d'un récit daté, jamais une tâche
- `legende`  : le caractère lui-même, expliqué dans la légende d'un registre
"""

COLONNES = ("doc", "ancre", "etat", "raison")


def marqueurs(racine: Path = RACINE) -> list[tuple[str, int, str]]:
    """(document, ligne, texte) pour chaque sablier de l'arbre — DÉRIVÉ, jamais listé.

    ⚠ `HANDOFF.md` en fait partie : c'est le document de passation, donc l'endroit le plus
    probable pour qu'une tâche soit laissée et oubliée.
    """
    out = []
    cibles = sorted((racine / "docs").glob("*.md")) + [racine / "HANDOFF.md"]
    for f in cibles:
        if not f.is_file():
            continue
        for n, ligne in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if SABLIER in ligne:
                out.append((str(f.relative_to(racine)), n, ligne.strip()))
    return out


DOCS_DE_BACKLOG = ("docs/18_batch_produire.md", "docs/22_batch_repliquer.md",
                   "docs/29_ce_qui_reste.md")
"""Les documents qui portent un backlog NUMÉROTÉ (`| I1 | … |`, `| M7 | … |`).

⚠ `06_mesures_a_faire.md` et `31_roadmap.md` en ont l'air par leur nom et n'en portent pas :
ils écrivent en prose. Les y chercher rendrait zéro et se lirait comme « rien à faire », ce
qui est le contraire d'un résultat. Mesuré avant d'écrire cette liste."""

LIGNE_ITEM = __import__("re").compile(r"^\|\s*\*{0,2}([A-Z]\d+(?:bis|ter)?)\*{0,2}\s*\|(.*)$")


def items(racine: Path = RACINE) -> list[dict]:
    """Les items numérotés des documents de backlog, avec leur état LU dans leur ligne.

    ⚠⚠ L'état est dérivé des marques de la ligne, jamais d'une liste tenue à côté. Et les
    marques ne veulent PAS toutes dire la même chose — ma première version comptait `❌` et
    `⚠` comme « ouvert », donc elle annonçait neuf tâches restantes là où sept étaient
    **répondues**, négativement ou avec une réserve. Une question à laquelle on a répondu
    « non » est close, pas en attente :

      `✅` / barré  → **fait**
      `⏳`          → **ouvert**, la seule classe qui demande du travail
      `❌`          → **repondu_non** : la mesure a dit non, la question est close
      `➡`          → **sans_objet** : elle a cessé de se poser
      `⚠`          → **reserve** : répondue, avec une nuance à lire
      rien         → **indecidable**, jamais « fait » — compter le silence comme un succès
                     est exactement la façon dont un backlog se déclare fini sans l'être
    """
    out = []
    for d in DOCS_DE_BACKLOG:
        f = racine / d
        if not f.is_file():
            continue
        for n, l in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = LIGNE_ITEM.match(l)
            if not m:
                continue
            item, reste = m.group(1), m.group(2)
            if "✅" in reste or "~~" in reste:
                etat = "fait"
            elif "⏳" in reste:
                etat = "ouvert"
            elif "❌" in reste:
                etat = "repondu_non"
            elif "➡" in reste:
                etat = "sans_objet"
            elif "⚠" in reste:
                etat = "reserve"
            else:
                etat = "indecidable"
            out.append({"doc": d, "ligne": n, "item": item, "etat": etat,
                        "texte": reste.strip()[:160]})
    return out


def lire_registre(chemin: Path = REGISTRE) -> list[dict]:
    """Le registre, ou une liste vide s'il n'existe pas encore."""
    if not chemin.is_file():
        return []
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    if not lignes:
        return []
    entetes = lignes[0].split("\t")
    out = []
    for l in lignes[1:]:
        if not l.strip():
            continue
        champs = l.split("\t")
        out.append(dict(zip(entetes, champs + [""] * (len(entetes) - len(champs)))))
    return out


def apparier(marques, entrees) -> dict:
    """Croise l'inventaire dérivé et le registre, dans les DEUX sens.

    ⚠ L'ancre est une sous-chaîne de la ligne, jamais un numéro de ligne : un numéro se
    décale à la première insertion au-dessus, et le registre se mettrait alors à désigner
    autre chose sans que rien ne change de couleur.
    """
    non_classes, perimees, classes = [], [], []
    restants = list(entrees)
    for doc, n, texte in marques:
        trouve = None
        for e in restants:
            if e.get("doc") == doc and e.get("ancre") and e["ancre"] in texte:
                trouve = e
                break
        if trouve is None:
            non_classes.append((doc, n, texte))
        else:
            classes.append((doc, n, texte, trouve))
            restants.remove(trouve)
    for e in restants:
        perimees.append(e)
    return {"classes": classes, "non_classes": non_classes, "perimees": perimees}


def resume(appariement: dict) -> dict[str, int]:
    """Combien de marqueurs par état."""
    compte: dict[str, int] = {}
    for _, _, _, e in appariement["classes"]:
        etat = e.get("etat", "?")
        compte[etat] = compte.get(etat, 0) + 1
    return compte


def verifier() -> int:
    """Le registre se garde lui-même, dans les deux sens."""
    import tempfile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "docs" / "registres").mkdir(parents=True)
        (r / "docs" / "01_x.md").write_text(
            f"une ligne\n{SABLIER} une tache qui reste\nune autre\n", encoding="utf-8")
        (r / "HANDOFF.md").write_text(f"## {SABLIER} un titre de recit\n", encoding="utf-8")

        m = marqueurs(r)
        v("les sabliers des documents sont trouves", len(m) == 2, str(m))
        v("... y compris dans HANDOFF.md", any(x[0] == "HANDOFF.md" for x in m), str(m))
        v("... avec leur numero de ligne", m[0][1] == 2, str(m[0]))

        reg = r / "docs" / "registres" / "taches.tsv"
        reg.write_text("doc\tancre\tetat\traison\n"
                       "docs/01_x.md\tune tache qui reste\touverte\tpas commencee\n",
                       encoding="utf-8")
        a = apparier(m, lire_registre(reg))
        v("un marqueur classe est apparie", len(a["classes"]) == 1, str(a["classes"]))
        # ⚠⚠ LE controle qui compte : un sablier sans entree ne doit pas passer inapercu,
        # sinon la question « reste-t-il du travail ? » redevient une relecture a la main.
        v("... et un marqueur SANS entree est signale non classe",
          len(a["non_classes"]) == 1 and a["non_classes"][0][0] == "HANDOFF.md",
          str(a["non_classes"]))

        reg.write_text("doc\tancre\tetat\traison\n"
                       "docs/01_x.md\tune tache qui reste\touverte\tpas commencee\n"
                       "docs/01_x.md\tune ancre qui a disparu\tfaite\tx\n", encoding="utf-8")
        a = apparier(m, lire_registre(reg))
        # ⚠⚠ L autre sens : une entree dont l ancre n est plus dans le document decrit un
        # texte qui n existe plus. Sans ce controle le registre derive du texte en silence.
        v("une entree dont l'ancre a disparu est signalee perimee",
          len(a["perimees"]) == 1 and a["perimees"][0]["etat"] == "faite", str(a["perimees"]))

        v("le resume compte par etat", resume(a) == {"ouverte": 1}, str(resume(a)))

    # --- les items numerotes ---
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "docs").mkdir(parents=True)
        (r / "docs" / "22_batch_repliquer.md").write_text(
            "| P1 | ~~fait~~ |\n| Q3 | ⏳ a faire |\n| Q2 | sans marque |\n"
            "| **R2** | ✅ fini |\nligne qui n est pas un item\n", encoding="utf-8")
        it = items(r)
        v("un item barre est fait", it[0]["etat"] == "fait", str(it[0]))
        v("... un item a sablier est ouvert", it[1]["etat"] == "ouvert", str(it[1]))
        # ⚠⚠ LE controle qui compte : une ligne SANS marque n est pas « faite ». Compter le
        # silence comme un succes est la facon dont un backlog se declare fini sans l etre.
        v("... et un item SANS marque est indecidable", it[2]["etat"] == "indecidable",
          str(it[2]))
        # ⚠⚠ Une question repondue NEGATIVEMENT est close, pas en attente. Ma premiere
        # version comptait `❌` comme ouvert et annoncait donc du travail qui n existait pas.
        (r / "docs" / "29_ce_qui_reste.md").write_text(
            "| A1 | ❌ non, mesure faite |\n| A2 | ➡️ sans objet |\n| A3 | ⚠ repondu, nuance |\n",
            encoding="utf-8")
        it2 = [x for x in items(r) if x["doc"].endswith("29_ce_qui_reste.md")]
        v("un ❌ est une reponse, pas une attente", it2[0]["etat"] == "repondu_non", str(it2[0]))
        v("... un ➡ est sans objet", it2[1]["etat"] == "sans_objet", str(it2[1]))
        v("... et un ⚠ est une reserve", it2[2]["etat"] == "reserve", str(it2[2]))
        v("... donc AUCUN des trois ne compte comme ouvert",
          not any(x["etat"] == "ouvert" for x in it2), str([x["etat"] for x in it2]))
        v("... les asterisques du gras ne cassent pas l id", it[3]["item"] == "R2", str(it[3]))
        v("... et une ligne qui n est pas un item est ignoree", len(it) == 4, str(len(it)))

    # --- contre le VRAI depot ---
    reels = marqueurs(RACINE)
    v("le depot porte des marqueurs a classer", len(reels) > 10, str(len(reels)))
    a = apparier(reels, lire_registre())
    v("aucun sablier n'est NON CLASSE", not a["non_classes"],
      "; ".join(f"{d}:{n}" for d, n, _ in a["non_classes"][:4]))
    v("aucune entree de registre n'est perimee", not a["perimees"],
      "; ".join(f"{e.get('doc')}:{e.get('ancre','')[:30]}" for e in a["perimees"][:4]))
    for e in lire_registre():
        if e.get("etat") not in ETATS:
            v(f"etat inconnu dans le registre : {e.get('etat')}", False)
            break
    else:
        v("chaque entree porte un etat connu", True)
    # ⚠ Une raison vide rend l entree inutilisable : « perimee » sans dire par quoi ne
    # permet pas de la contester.
    v("chaque entree porte une raison",
      all(e.get("raison", "").strip() for e in lire_registre()),
      "; ".join(e.get("ancre", "")[:24] for e in lire_registre() if not e.get("raison", "").strip())[:80])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    # ⚠⚠⚠ Le verdict imprimait « ALL PASS » et rendait 0 INCONDITIONNELLEMENT :
    # cette batterie était verte quoi que disent ses contrôles. Trente-neuf
    # fichiers du dépôt portaient le même défaut, corrigé le 2026-08-27.
    print(f"{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ouvertes", action="store_true", help="ne montrer que ce qui RESTE")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    m = marqueurs()
    app = apparier(m, lire_registre())
    r = resume(app)
    print(f"{len(m)} sablier(s) dans {len({x[0] for x in m})} document(s)")
    for etat in ETATS:
        if r.get(etat):
            print(f"  {r[etat]:>4}  {etat}")
    if app["non_classes"]:
        print(f"\n⚠ {len(app['non_classes'])} NON CLASSÉ(S) — la question « reste-t-il du "
              f"travail ? » n'a pas de réponse tant qu'ils sont là :")
        for doc, n, texte in app["non_classes"]:
            print(f"    {doc}:{n}  {texte[:90]}")
    if app["perimees"]:
        print(f"\n⚠ {len(app['perimees'])} entrée(s) de registre PÉRIMÉE(S) — leur ancre a "
              f"disparu du document :")
        for e in app["perimees"]:
            print(f"    {e.get('doc')}  « {e.get('ancre','')[:60]} »")

    its = items()
    ouv_i = [x for x in its if x["etat"] == "ouvert"]
    ind_i = [x for x in its if x["etat"] == "indecidable"]
    par_etat: dict[str, int] = {}
    for x in its:
        par_etat[x["etat"]] = par_etat.get(x["etat"], 0) + 1
    print(f"\n{len(its)} item(s) numeroté(s) dans {len(DOCS_DE_BACKLOG)} document(s) de "
          f"backlog : " + ", ".join(f"{v} {k}" for k, v in sorted(par_etat.items())))
    for x in ouv_i + ind_i:
        print(f"    [{x['etat']:<12}] {x['doc']}:{x['ligne']}  {x['item']}  {x['texte'][:80]}")

    ouvertes = [(d, n, t, e) for d, n, t, e in app["classes"] if e.get("etat") == "ouverte"]
    print(f"\n{len(ouvertes)} tâche(s) OUVERTE(S) :")
    for doc, n, texte, e in ouvertes:
        print(f"    {doc}:{n}")
        print(f"        {e.get('raison', '')}")
    if a.json:
        import json
        a.json.write_text(json.dumps({
            "sabliers": len(m), "par_etat": r,
            "non_classes": [{"doc": d, "ligne": n} for d, n, _ in app["non_classes"]],
            "ouvertes": [{"doc": d, "ligne": n, "raison": e.get("raison", "")}
                         for d, n, _, e in ouvertes],
            "items": {"total": len(its), "ouverts": len(ouv_i),
                      "indecidables": len(ind_i)}}, indent=1, ensure_ascii=False),
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
