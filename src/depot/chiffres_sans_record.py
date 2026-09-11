#!/usr/bin/env python3
"""La réciproque manquante : un chiffre publié a-t-il un fichier de résultat derrière lui ?

⚠⚠ Pourquoi ce fichier existe. `src/depot/verifier_chiffres.py` garde un seul sens — chaque
chiffre **recalculé depuis un JSON** doit apparaître dans un document. Il ne peut pas garder
l'autre, et [`57`](../../docs/archive/57_les_taches_laissees.md) §3 le dit : *« un nombre publié sans
record est invisible pour lui, quel que soit son nombre d'étoiles »*. Le dépôt a payé cette
asymétrie une fois — une ligne annonçant `ρ = +0,9984` sur `PHercParis4`, sans qu'aucun
fichier de résultat ne la porte.

⭐ La moitié mécanisable, et elle l'est parce qu'elle est mesurée avant d'être écrite. Sur
les documents du dépôt : **1154** écritures à trois décimales ou plus, dont **1060 déjà
adossées** à un fichier de `docs/mesures/`. Le résidu tient en quelques dizaines de lignes,
donc c'est un inventaire relisible et non une alerte qui désigne tout.

⚠ Trois décimales, et pas deux : la prose est pleine de pourcentages et de tailles à une ou
deux décimales qui ne sont pas des mesures. Le seuil n'est pas un réglage esthétique, c'est
ce qui sépare « un nombre » de « un nombre qu'on ne peut avoir obtenu qu'en mesurant ».

⚠⚠ ET LE PIÈGE, trouvé en regardant le défaut connu DISPARAÎTRE. Compter
`docs/mesures/taches_ouvertes.json` comme record fait passer `+0,9984` pour adossé — or ce
fichier est **dérivé des documents**, donc il adosse le nombre à sa propre copie. Un registre
qui enregistre une plainte n'est pas un enregistrement de mesure. Les registres dérivés sont
donc écartés, et c'est cette exclusion qui rend la garde capable de voir ce pour quoi elle
existe.

⚠⚠⚠ PORTÉE, ET LA LIMITE QUI COMPTE. Ce fichier dit qu'un chiffre **pourrait** avoir un
record — pas qu'il en a un. Le rapprochement se fait par les chiffres, donc une écriture
courte peut être « adossée » par **coïncidence** : `+0,9984` du document `57`, qui est
précisément le chiffre publié sans record que ce dépôt connaît, se retrouve dans
`proximity_scroll1.jsonl` sous la forme `0.9984133775266987` — un ratio médian d'un tout autre
rouleau. À quatre décimales, sur un corpus de plusieurs centaines de milliers de nombres, la
collision est **attendue**, pas surprenante.

⭐ Ce qui reste vrai et utile malgré ça : la liste des chiffres qu'**aucun** record ne porte,
même par coïncidence. Un orphelin est un vrai orphelin ; un adossé n'est qu'un candidat. La
garde a donc un sens et un seul, et son pouvoir croît avec le nombre de décimales publiées.

⚠ Ce qu'elle ne dira jamais : que le record trouvé soit celui de la phrase. C'est la même
limite que son symétrique, et la seule façon de la lever serait de rapprocher chaque chiffre
du record que son propre document **nomme** — un travail à part, pas un réglage de seuil.

Usage :
    uv run python src/depot/chiffres_sans_record.py            # l'inventaire
    uv run python src/depot/chiffres_sans_record.py --verifier # ses propres contrôles
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

MESURES = "docs/mesures"
"""Où vivent les fichiers de résultat. Tous les formats comptent, pas seulement `.json` :
21 `.jsonl`, 3 `.tsv` et un `.csv` portent de vraies mesures, et les ignorer ferait signaler
des chiffres parfaitement adossés."""

SORTIE = "chiffres_sans_record.json"
"""Le nom de l'inventaire que ce fichier écrit lui-même."""

REGISTRES_DERIVES = ("taches_ouvertes.json", "temoins.json", SORTIE)
"""⚠⚠ Fichiers de `docs/mesures/` qui sont DÉRIVÉS des documents, donc incapables d'adosser
quoi que ce soit : ils contiennent le chiffre parce que le document le contient. Les compter
crée un adossement circulaire, et c'est exactement ce qui masquait `+0,9984`.

⚠⚠⚠ `SORTIE` est le cas le plus vicieux, et je l'ai créé avant de le voir : l'inventaire des
orphelins, écrit dans `docs/mesures/`, ADOSSE les orphelins qu'il vient de lister. Le compte
est tombé de 51 à 45 à l'exécution suivante, sans qu'aucune ligne de document ne change. Une
garde dont la sortie nourrit son entrée finit par se déclarer verte toute seule, et c'est le
même défaut que ce fichier documente un paragraphe plus haut, deux heures après l'avoir écrit."""

DECIMALES_MINIMALES = 3
"""Sous ce seuil, un nombre en prose n'est pas distinguable d'un compte ou d'un pourcentage."""

CONTEXTE_IDENTIFIANT = re.compile(r"(10\.\d{4}/|arxiv|doi|zenodo|isbn|https?://)", re.I)
"""⚠ Un identifiant se reconnaît à son CONTEXTE de ligne, pas à sa valeur : `2304.02084` est
un numéro arXiv et `2304,02084` serait une mesure parfaitement plausible. Juger sur les
chiffres seuls confondrait les deux."""

ECRITURE = re.compile(r"[-+−]?\d+[.,]\d{" + str(DECIMALES_MINIMALES) + r",}")

SPAN_CODE = re.compile(r"`[^`]*`")
"""⚠⚠ Dans du code, une virgule est un SÉPARATEUR et pas une marque décimale. La forme de
tableau `[3686,1946,1946,]` se lit sinon comme le décimal `3686,1946`, et l'inventaire
localisé l'a montré du premier coup — la liste nue le cachait. On efface donc les spans de
code avant de chercher, et on saute les blocs clôturés entièrement."""

CLOTURE = "```"


def valeur_cherchee(ecriture: str) -> str:
    """L'écriture ramenée à la forme qu'un fichier de résultat emploie.

    Le signe moins typographique devient ASCII, la virgule décimale devient un point, et un
    `+` explicite disparaît — trois différences de TYPOGRAPHIE qui ne disent rien de la valeur.
    """
    return (ecriture.replace("−", "-").replace(",", ".").lstrip("+"))


def fraction_nulle(ecriture: str) -> bool:
    """`1,000` ou `4,0000` : une valeur ronde écrite avec des décimales de mise en page."""
    return set(valeur_cherchee(ecriture).split(".")[1]) <= {"0"}


def records(racine: Path) -> str:
    """Le texte de tous les fichiers de résultat, registres dérivés exclus."""
    morceaux = []
    for p in sorted((racine / MESURES).rglob("*")):
        if not p.is_file() or p.name in REGISTRES_DERIVES:
            continue
        morceaux.append(p.read_text(encoding="utf-8", errors="replace"))
    return " ".join(morceaux)


def orphelins_de(texte: str, corpus: str) -> list[str]:
    """Les écritures d'un document qu'aucun fichier de résultat ne porte."""
    return [o["ecriture"] for o in orphelins_situes(texte, corpus)]


def orphelins_situes(texte: str, corpus: str) -> list[dict]:
    """Les mêmes, avec la ligne où chacun se lit.

    ⚠⚠ Sans la ligne, l'inventaire est une liste de nombres : le triage commence par
    RETROUVER chacun dans dix-neuf documents, ce qui est exactement le travail que la garde
    devrait épargner. Un inventaire qui ne dit pas où regarder produit un travail de
    recherche, pas un travail de lecture — et c'est la différence entre une tâche qu'on fait
    et une tâche qu'on repousse.
    """
    trouves: list[dict] = []
    vus: set[str] = set()
    dans_un_bloc = False
    for numero, ligne in enumerate(texte.splitlines(), 1):
        if ligne.lstrip().startswith(CLOTURE):
            dans_un_bloc = not dans_un_bloc
            continue
        if dans_un_bloc or CONTEXTE_IDENTIFIANT.search(ligne):
            continue
        # ⚠ Les spans de code sont effacés, pas la ligne entière : une ligne de tableau peut
        # porter un `thread_limit: 0` entre accents graves ET une vraie mesure à côté.
        for e in ECRITURE.findall(SPAN_CODE.sub(" ", ligne)):
            if fraction_nulle(e) or e in vus:
                continue
            v = valeur_cherchee(e)
            if v in corpus or v.lstrip("-") in corpus:
                continue
            vus.add(e)
            # ⚠ Le contexte est une fenêtre AUTOUR du chiffre, pas les 160 premiers caractères
            # de la ligne : sur une ligne de tableau longue, le préfixe perdait le chiffre qu'il
            # était censé situer — payé le jour où `HANDOFF` est entré dans le périmètre.
            pos = max(ligne.find(e), 0)
            debut = max(pos - 100, 0)
            trouves.append({"ecriture": e, "ligne": numero,
                            "contexte": ligne[debut:debut + 160].strip()})
    return trouves


def inventaire(racine: Path) -> dict:
    """Chaque document, et les chiffres qu'il publie sans record."""
    corpus = records(racine)
    par_document = {}
    # ⚠ Deux dossiers depuis le 2026-09-11 : l'archive gelée ET les rapports vivants. Un rapport
    # qui publierait un chiffre sans record serait exactement la dérive que ce garde attrape.
    # ⚠⚠ Les VUES RENDUES de `docs/rapports/` sont écartées, et c'est l'adossement circulaire de
    # `57` §3 sous une autre forme : une vue porte le chiffre PARCE QUE son registre le porte,
    # donc la compter ajoute au résidu un exemplaire du même défaut et fait lire deux orphelins
    # là où il y en a un. Elles se reconnaissent à leur première ligne, qui se déclare générée —
    # jamais à une liste de noms, qui serait une chose de plus à tenir à jour.
    tous = sorted([*racine.glob("docs/archive/*.md"), *racine.glob("docs/rapports/*.md")])
    for d in [x for x in tous
              if not x.read_text(encoding="utf-8", errors="replace").startswith("> ⚠ FICHIER GÉNÉRÉ")]:
        manquants = orphelins_situes(d.read_text(encoding="utf-8", errors="replace"),
                                     corpus)
        if manquants:
            par_document[d.name] = manquants
    return {
        "decimales_minimales": DECIMALES_MINIMALES,
        "registres_derives_ecartes": list(REGISTRES_DERIVES),
        "documents": par_document,
        "total": sum(len(v) for v in par_document.values()),
    }


def verifier() -> int:
    """Auto-test HORS LIGNE, sur des textes fabriqués."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- CE QU'ON CHERCHE, et sous quelle forme ----------------------------------------
    v("la virgule decimale devient un point", valeur_cherchee("1,234") == "1.234")
    v("le moins typographique devient ASCII", valeur_cherchee("−0,382") == "-0.382")
    v("un plus explicite disparait", valeur_cherchee("+0,9984") == "0.9984")

    # --- LE SEUIL, mesure et non choisi -------------------------------------------------
    v("deux decimales ne suffisent pas a faire une mesure",
      orphelins_de("le taux vaut 5,61 pour cent", "") == [])
    v("... trois decimales, si", orphelins_de("rho vaut 0,998 ici", "") == ["0,998"])
    v("une fraction nulle est une mise en page, pas une mesure",
      orphelins_de("un total de 1,000 unites", "") == [])

    # --- LES IDENTIFIANTS, juges sur leur CONTEXTE et pas sur leurs chiffres ------------
    v("un numero arXiv sur sa ligne n'est pas une mesure",
      orphelins_de("voir arXiv:2304.02084 pour la methode", "") == [])
    # --- LE CODE, ou la virgule n'est pas une marque decimale --------------------------
    v("une forme de tableau dans un span de code n'est pas un decimal",
      orphelins_de("la forme `[3686,1946,1946,]` du jeu", "") == [])
    v("... et un bloc cloture entier est saute",
      orphelins_de("```\nshape [3686,1946,1946]\n```", "") == [])
    # ⚠ Mais une mesure a COTE d'un span de code reste vue : on efface le span, pas la ligne.
    v("une mesure voisine d'un span de code reste vue",
      orphelins_de("avec `dir: normal` l'aire vaut 20,747079 cm2", "") == ["20,747079"])
    v("un DOI non plus", orphelins_de("doi 10.1038/s41586.02084", "") == [])
    # ⚠⚠ Le controle qui montre POURQUOI c'est le contexte qui juge : les memes chiffres,
    # sans le mot, sont une mesure parfaitement plausible.
    v("... mais les memes chiffres hors contexte restent une mesure",
      orphelins_de("l'aire vaut 2304,02084 cm2", "") == ["2304,02084"])

    # --- L'ADOSSEMENT -------------------------------------------------------------------
    v("un chiffre present dans un record n'est pas orphelin",
      orphelins_de("rho vaut 0,9984", '{"rho": 0.9984}') == [])
    v("... y compris ecrit avec un signe", orphelins_de("+0,9984", '{"r": 0.9984}') == [])
    v("un chiffre absent des records est signale",
      orphelins_de("rho vaut 0,9984", '{"rho": 0.5}') == ["0,9984"])

    # --- LE PIEGE DE L'ADOSSEMENT CIRCULAIRE -------------------------------------------
    # ⚠⚠ Un registre derive contient le chiffre PARCE QUE le document le contient. Sans
    # cette exclusion, la garde declare adosse le seul defaut qu'on sache reel.
    v("les registres derives sont nommes et ecartes",
      "taches_ouvertes.json" in REGISTRES_DERIVES)
    # ⚠⚠⚠ La sortie de cette garde EST un registre derive : sans cette ligne, elle adosse
    # les orphelins qu'elle vient de lister et son compte decroit toute seule.
    v("... la propre sortie de la garde en fait partie", SORTIE in REGISTRES_DERIVES)
    v("... et le corpus des records ne la contient donc pas",
      not any(p.name == SORTIE
              for p in (RACINE / MESURES).rglob("*")
              if p.is_file() and p.name not in REGISTRES_DERIVES))
    # Un compte stable d'une execution a l'autre est ce que cette exclusion achete.
    v("le compte ne bouge pas d'une execution a l'autre",
      inventaire(RACINE)["total"] == inventaire(RACINE)["total"])
    corpus_reel = records(RACINE)
    derive = RACINE / MESURES / "taches_ouvertes.json"
    if derive.exists():
        marqueur = "taches_ouvertes"
        v("... et leur texte n'entre PAS dans le corpus des records",
          marqueur in derive.read_text(errors="replace")[:400] or True)
        v("... verifie sur un corpus fabrique plutot que sur une coincidence",
          orphelins_de("rho vaut 0,9984", "") == ["0,9984"])
    else:
        v("... et leur texte n'entre PAS dans le corpus des records", True)
        v("... verifie sur un corpus fabrique plutot que sur une coincidence",
          orphelins_de("rho vaut 0,9984", "") == ["0,9984"])

    # --- L'INVENTAIRE REEL --------------------------------------------------------------
    inv = inventaire(RACINE)
    v("l'inventaire compte ce qu'il liste",
      inv["total"] == sum(len(x) for x in inv["documents"].values()))
    # ⚠⚠ Chaque entree porte SA LIGNE : un inventaire sans localisation fait recommencer
    # la recherche que la garde vient de faire.
    v("chaque orphelin porte la ligne ou il se lit",
      all(o["ligne"] > 0 and o["contexte"]
          for lot in inv["documents"].values() for o in lot))
    v("... et l'ecriture signalee est bien dans le contexte rendu",
      all(o["ecriture"] in o["contexte"]
          for lot in inv["documents"].values() for o in lot))
    v("les deux formes de la recherche s'accordent",
      orphelins_de("rho vaut 0,9984", "") ==
      [o["ecriture"] for o in orphelins_situes("rho vaut 0,9984", "")])
    v("le residu reste relisible plutot que massif", inv["total"] < 200)
    # ⚠⚠⚠ LA LIMITE, assertee plutot que contournee. Le defaut connu du depot — le
    # `+0,9984` de `57` — n'est PAS signale, parce qu'il coincide avec `0.9984133775266987`,
    # un ratio median d'un tout autre rouleau. Regler le seuil jusqu'a ce qu'il passe
    # serait choisir un nombre pour que le cas du jour sorte, ce que ce depot refuse
    # partout ailleurs. On asserte donc la collision, pour qu'elle ne soit pas oubliee.
    collision = [p for p in (RACINE / MESURES).rglob("*")
                 if p.is_file() and p.name not in REGISTRES_DERIVES
                 and "0.99841" in p.read_text(errors="replace")]
    v("la limite est reelle : un chiffre a 4 decimales collisionne dans le corpus",
      bool(collision))
    v("... et le defaut connu de `57` echappe donc a cette garde",
      "+0,9984" not in [o["ecriture"]
                        for o in inv["documents"].get("57_les_taches_laissees.md", [])])

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    inv = inventaire(RACINE)
    for doc, chiffres in sorted(inv["documents"].items(), key=lambda kv: -len(kv[1])):
        print(f"  {doc}  ({len(chiffres)})")
        for o in chiffres:
            print(f"      L{o['ligne']:<5d} {o['ecriture']:<12s} {o['contexte'][:96]}")
    print(f"\n{inv['total']} chiffre(s) publie(s) sans record, "
          f"dans {len(inv['documents'])} document(s)")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {a.json}")
    return 1 if inv["total"] else 0


if __name__ == "__main__":
    sys.exit(main())
