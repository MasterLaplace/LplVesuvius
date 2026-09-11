#!/usr/bin/env python3
"""Ranger `docs/` par NATURE — et refuser tant qu'un écrivain vise encore l'ancien endroit.

⚠⚠ POURQUOI CE FICHIER EXISTE. `docs/` porte **522 fichiers à plat** : 58 documents noyés
sous 347 mesures, 79 journaux et une poignée de registres. `ls docs/` ne dit plus rien, et
surtout **rien ne distingue un document d'une sortie de campagne**.

Le déplacement lui-même est un `git mv`, et `src/depot/deplacer.py` sait déjà réécrire les
citations et refuser d'en laisser une pendante. Ce qui manque, et qui mérite du code, ce sont
les deux choses que `deplacer.py` ne peut pas savoir :

  ⭐ 1. QUELLE est la nature d'un fichier — et une nature n'est pas une extension, c'est un
       USAGE. Mesuré le 2026-08-26 : les `.json` sont cités **77 fois** dans les documents,
       les `.log` **zéro fois**. Un journal se consulte après une panne ; une mesure se cite
       comme un résultat. Ce sont deux choses, et les mélanger empêche de purger l'une sans
       risquer l'autre.

  ⭐⭐ 2. Qu'aucun ÉCRIVAIN ne vise encore l'ancien endroit. C'est le danger que ce fichier
       existe pour écarter, et il est pire qu'une citation pendante : une citation morte se
       voit, alors qu'un script qui recrée `docs/<nom>.json` après le rangement produit **deux
       fichiers pour une mesure**, dont un périmé, sans le moindre symptôme. C'est « deux
       réponses à une question », le motif que ce dépôt paie en boucle.

⚠ Ce fichier ne déplace RIEN. Il produit une carte `{ancien: dossier}` que `deplacer.py`
applique — un seul outil sait bouger des fichiers, et c'est celui qui sait refuser.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

DOCUMENT = "document"
MESURE = "mesure"
JOURNAL = "journal"
REGISTRE = "registre"

DESTINATIONS = {
    DOCUMENT: "docs",
    MESURE: "docs/mesures",
    JOURNAL: "docs/journaux",
    REGISTRE: "docs/archive/registres",
}
"""Où chaque nature va vivre. ⚠ `document` reste à la racine : c'est ce que « docs » veut
dire, et un `docs/documents/` mettrait le contenu du dossier à un niveau de son nom.

⚠ Depuis le 2026-09-11 les documents numérotés sont GELÉS dans `docs/archive/` et la synthèse
vivante est dans `docs/rapports/` ; les quatre registres tenus à la main ont suivi l'archive.
Ce classement ne dit donc plus où un `.md` doit aller — seulement qu'un `.md` à la racine
n'est ni une mesure, ni un journal, ni un registre."""

PAR_EXTENSION = {
    ".md": DOCUMENT,
    ".json": MESURE, ".jsonl": MESURE, ".csv": MESURE, ".tsv": MESURE,
    ".txt": MESURE, ".xml": MESURE,
    ".log": JOURNAL,
}
"""⚠ L'extension n'est qu'un RACCOURCI vers la nature, pas sa définition. Le partage vient
d'une mesure d'usage : `.json` et `.txt` sont cités comme des résultats (81 citations),
`.log` ne l'est jamais (0). Le jour où un `.log` est cité, c'est la classification qui a tort,
et `journaux_cites()` le dit."""

REGISTRES = ("murs_et_causes.tsv",)
"""Les fichiers de `docs/` qu'un HUMAIN maintient, et qu'aucune campagne ne réécrit.

⚠⚠ Les nommer plutôt que les dériver est un choix : ils sont peu nombreux, et une dérivation
« ce que personne n'écrit » serait plus de code et fausse le jour où un fichier n'est
simplement lu par rien encore. Mais le nommage se VÉRIFIE — `registres_ecrits()` cherche les
formes d'écriture et `verifier()` échoue si l'un d'eux en est la cible, c'est-à-dire a cessé
d'être un registre.

⚠ Et c'est ce contrôle qui a corrigé ma première liste : j'y avais mis `verbes.json`, qui est
lu par `lplv` comme une entrée — mais qui est PRODUIT par `./lplv --verbes --json`. Un
fichier lu comme une entrée n'est pas pour autant maintenu à la main, et le classer en
registre l'aurait mis hors de portée d'une purge de sorties alors que c'en est une. La
promesse de vérification était écrite dans cette docstring et le contrôle n'existait pas :
c'est exactement ce que ce dépôt appelle une vérification qu'on annonce sans l'écrire."""

MESURE_TEMOIN, JOURNAL_TEMOIN = "t.json", "c.log"
"""⚠ Les noms des fixtures, gardés en constantes pour que le mot « docs/ » ne soit
jamais suivi d'un nom de fichier en clair dans ce module. Sans ça, ce fichier est sa
propre première alerte : `mentions_a_lancien_endroit()` trouve ses exemples et les
rapporte comme des chemins à réparer, ce qui apprend à ne plus lire le rapport."""

DOC_TEMOIN = "31_roadmap.md"
"""⚠ Un nom de document RÉEL, gardé dans une constante pour la même raison que `REGISTRES` :
le citer en clair dans une fixture en ferait une cible de réécriture."""

INTOUCHABLES = ("README.md",)
"""⚠ Un `README.md` se rend là où il est. Le déplacer casse un affichage sans casser un test."""


def nature(nom: str) -> str | None:
    """La nature d'un fichier de `docs/`, ou `None` si ce fichier n'est pas classable.

    ⚠ `None` n'est pas une erreur : c'est un aveu. Une extension inconnue doit rester où elle
    est plutôt que d'atterrir dans un dossier choisi au hasard.
    """
    if nom in REGISTRES:
        return REGISTRE
    return PAR_EXTENSION.get(Path(nom).suffix)


def a_deplacer(nature_: str | None) -> bool:
    """Une nature dont la destination n'est pas la racine de `docs/`."""
    return nature_ is not None and DESTINATIONS[nature_] != "docs"


def carte(racine: Path = RACINE) -> dict[str, str]:
    """`{chemin_ancien: dossier_nouveau}`, prête pour `deplacer.plan_depuis`.

    ⚠ Seulement les fichiers à la RACINE de `docs/`. Les sous-dossiers de campagne
    (`docs/champ_PHerc0172/`…) sont déjà rangés, par rouleau : les réétaler par nature les
    déferait.
    """
    out = {}
    for f in sorted((racine / "docs").iterdir()):
        if not f.is_file() or f.name in INTOUCHABLES:
            continue
        n = nature(f.name)
        if a_deplacer(n):
            out[f"docs/{f.name}"] = DESTINATIONS[n]
    return out


def extensions_qui_demenagent() -> tuple[str, ...]:
    """Les suffixes dont un fichier ne doit plus apparaître à la racine de `docs/`."""
    return tuple(sorted(e for e, n in PAR_EXTENSION.items() if a_deplacer(n)))


def mentions_a_lancien_endroit(racine: Path = RACINE) -> list[tuple[str, str]]:
    """Les endroits qui NOMMENT encore `docs/<nom>.<ext>` pour une extension déménagée.

    Lecteurs et écrivains, sans les distinguer — le nom d'un fichier déplacé ne doit plus
    apparaître nulle part, quel que soit ce qu'on comptait en faire.

    ⚠⚠ C'est le contrôle qui donne son sens au rangement. Une citation pendante se voit à la
    première lecture ; un écrivain non réparé recrée le fichier à l'ancien endroit et le
    dépôt se retrouve avec **deux fichiers pour une mesure**, l'un frais et l'autre mort,
    sans qu'aucune sortie ne change.

    ⚠ Il cherche la FORME textuelle d'un chemin sous `docs/`. Un chemin assemblé à l'exécution
    (`racine / "docs" / nom`) lui échappe par construction — c'est `deplacer.construits()`
    qui nomme cette classe-là, et `verifier_chiffres.DOSSIER_MESURES` qui l'a supprimée là
    où elle comptait le plus.
    """
    import re

    exts = "|".join(e.lstrip(".") for e in extensions_qui_demenagent())
    motif = re.compile(rf"docs/([A-Za-z0-9_.-]+\.(?:{exts}))")
    trouves = []
    for f in _textes(racine):
        try:
            texte = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in motif.finditer(texte):
            ligne = texte[:m.start()].count("\n") + 1
            trouves.append((f"{f.relative_to(racine)}:{ligne}", m.group(1)))
    return trouves


def _est_une_redirection(ligne: str, position: int) -> bool:
    """Ce `>` est-il une redirection shell, ou une citation Markdown ?

    ⚠⚠ Les deux s'écrivent `>` et rien d'autre ne les distingue que ce qui les précède. Une
    citation commence la ligne — éventuellement après une indentation, et éventuellement
    après un guillemet, parce que la prose Markdown de ce dépôt vit aussi dans des chaînes
    Python. Deux faux positifs mesurés avant cette règle, tous deux sur la ligne qui explique
    justement qu'un document est RENDU.
    """
    avant = ligne[:position].lstrip().lstrip("\"'`")
    return avant.strip() != ""


def registres_ecrits(racine: Path = RACINE) -> list[tuple[str, str]]:
    """Les endroits qui écrivent un fichier nommé dans `REGISTRES` — donc qui le produisent.

    ⚠ Un registre produit n'est pas un registre : il doit redevenir une mesure, sinon une
    purge des sorties l'épargnera à tort et il vieillira sans que rien ne le dise.
    """
    import re

    noms = "|".join(re.escape(n) for n in REGISTRES)
    par_drapeau = re.compile(rf"(?:--json|--sortie|--out)\s+[\"']?[^\"'\s]*({noms})")
    par_ecriture = re.compile(rf"write_text\(\s*[\"']?[^\"'\s]*({noms})")
    par_redirection = re.compile(rf"(>)\s*[\"']?[^\"'\s]*({noms})")
    trouves = []
    for f in _textes(racine):
        try:
            texte = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for num, ligne in enumerate(texte.splitlines(), 1):
            for motif in (par_drapeau, par_ecriture):
                for m in motif.finditer(ligne):
                    trouves.append((f"{f.relative_to(racine)}:{num}", m.group(1)))
            for m in par_redirection.finditer(ligne):
                if _est_une_redirection(ligne, m.start(1)):
                    trouves.append((f"{f.relative_to(racine)}:{num}", m.group(2)))
    return trouves


def _ignores(racine: Path, chemins: list[str]) -> set[str]:
    """Ceux de ces chemins que git ignore. ⚠ `check-ignore` juge un CHEMIN, pas un fichier :
    il répond donc aussi pour une destination qui n'existe pas encore, ce qui est exactement
    ce qu'il faut pour décider AVANT de déplacer."""
    import subprocess

    if not chemins:
        return set()
    r = subprocess.run(["git", "-C", str(racine), "check-ignore", "--stdin"],
                       input="\n".join(chemins), capture_output=True, text=True)
    return set(r.stdout.splitlines())


def ignores_rompus(racine: Path = RACINE, plan: dict[str, str] | None = None) -> list[str]:
    """Les fichiers aujourd'hui IGNORÉS dont la destination ne le serait plus.

    ⚠⚠ C'est la panne silencieuse du rangement, et elle va dans le sens le plus coûteux :
    `.gitignore` dit `/docs/*.log`, une règle ANCRÉE à la racine de `docs/`. Déplacer les 79
    journaux vers `docs/journaux/` les fait sortir de la règle, donc **entrer dans le dépôt**
    — 79 traces de run versionnées sans que personne ne l'ait demandé, et sans le moindre
    message. Un fichier ignoré avant doit rester ignoré après ; sinon c'est `.gitignore` qu'il
    faut changer, pas le plan.
    """
    plan = carte(racine) if plan is None else plan
    avant = _ignores(racine, sorted(plan))
    if not avant:
        return []
    apres = _ignores(racine, [f"{plan[a]}/{Path(a).name}" for a in sorted(avant)])
    return sorted(a for a in avant if f"{plan[a]}/{Path(a).name}" not in apres)


def journaux_cites(racine: Path = RACINE) -> list[str]:
    """Les journaux qu'un document cite — donc mal classés, ou cités pour un chiffre.

    ⚠ Un chiffre dont la source est un journal n'est vérifiable par personne : un journal
    n'a pas de forme. Le trouver veut dire qu'il faut publier la mesure, pas déplacer le log.
    """
    import re

    motif = re.compile(r"docs/([A-Za-z0-9_.-]+\.log)")
    vus = set()
    for f in sorted((racine / "docs" / "archive").glob("*.md")):
        vus.update(motif.findall(f.read_text(encoding="utf-8", errors="replace")))
    return sorted(vus)


def _textes(racine: Path) -> list[Path]:
    """Les fichiers où une citation de chemin peut vivre. ⚠ Même périmètre que
    `deplacer.tous_les_textes`, élagué à la traversée pour ne pas descendre dans `.venv`."""
    gardes = (".py", ".sh", ".md", ".toml", ".txt", ".tsv", ".json", ".yaml", ".yml")
    ignores = {".git", ".venv", "__pycache__", ".lances", "data", "repos", "build", "site"}
    out, pile = [], [racine]
    while pile:
        d = pile.pop()
        try:
            entrees = list(d.iterdir())
        except OSError:
            continue
        for e in entrees:
            if e.is_dir():
                if e.name not in ignores:
                    pile.append(e)
            elif e.suffix in gardes:
                out.append(e)
    return sorted(out)


def resume(racine: Path = RACINE) -> dict[str, int]:
    """Combien de fichiers de chaque nature à la racine de `docs/`."""
    compte: dict[str, int] = {}
    for f in (racine / "docs").iterdir():
        if not f.is_file():
            continue
        n = nature(f.name) or "inclassable"
        compte[n] = compte.get(n, 0) + 1
    return compte


def verifier() -> int:
    """Le classement se garde lui-même."""
    import tempfile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("un document est un document", nature(DOC_TEMOIN) == DOCUMENT)
    v("une mesure est une mesure", nature("table_champ.json") == MESURE)
    v("un journal est un journal", nature("clone.log") == JOURNAL)
    # ⚠⚠ Le registre GAGNE sur l extension : `murs_et_causes.tsv` est un `.tsv`, donc la
    # table le classerait en mesure, donc une purge des sorties emporterait un fichier
    # maintenu a la main. C est la seule raison d avoir deux natures produites differemment.
    v("un registre bat son extension", nature("murs_et_causes.tsv") == REGISTRE)
    v("... et un fichier PRODUIT n en est pas un", nature("verbes.json") == MESURE)
    v("une extension inconnue n est pas classee", nature("x.bin") is None)
    v("... donc elle ne bouge pas", not a_deplacer(nature("x.bin")))
    v("un document ne bouge pas non plus", not a_deplacer(DOCUMENT))
    v("une mesure bouge", a_deplacer(MESURE))

    v("les extensions qui demenagent sont dites", ".json" in extensions_qui_demenagent())
    v("... et .md n en est pas", ".md" not in extensions_qui_demenagent())

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "docs").mkdir()
        # ⚠⚠ Le nom du registre est DÉRIVÉ de la constante, jamais réécrit ici. Écrire
        # Le chemin complet d un registre REEL, ecrit en clair, serait une cible de
        # `deplacer.py`, qui le reecrirait en rangeant -- et mangerait la fixture de sa
        # propre batterie, ce que ce depot a deja paye une fois.
        registre = REGISTRES[0]
        for nom in (DOC_TEMOIN, "README.md", MESURE_TEMOIN, JOURNAL_TEMOIN, registre,
                    "x.bin"):
            (r / "docs" / nom).write_text("x", encoding="utf-8")
        (r / "docs" / "champ_PHerc0172").mkdir()
        (r / "docs" / "champ_PHerc0172" / "dedans.json").write_text("x", encoding="utf-8")
        c = carte(r)
        v("la carte prend la mesure", c.get(f"docs/{MESURE_TEMOIN}") == "docs/mesures",
          str(c))
        v("... le journal", c.get(f"docs/{JOURNAL_TEMOIN}") == "docs/journaux")
        v("... le registre", c.get(f"docs/{registre}") == "docs/archive/registres")
        v("... et laisse le document", f"docs/{DOC_TEMOIN}" not in c)
        v("... et le README", "docs/README.md" not in c)
        v("... et l inclassable", "docs/x.bin" not in c)
        # ⚠ Un sous-dossier de campagne est deja range PAR ROULEAU : le reetaler par nature
        # le deferait, et c est exactement ce qu une marche recursive ferait sans le dire.
        v("... et ne descend pas dans un sous-dossier de campagne",
          not any("champ_PHerc0172" in k for k in c), str(list(c)))
        r2 = resume(r)
        v("le resume compte l inclassable", r2.get("inclassable") == 1, str(r2))
        v("... et le README compte comme document", r2.get(DOCUMENT) == 2, str(r2))

        # La sonde : un script qui vise encore l ancien endroit doit ressortir. C est le
        # cas le PIRE -- un ecrivain non repare recree le fichier a cote du fichier range.
        (r / "campagne.sh").write_text(f"lplv mesurer --sortie docs/{MESURE_TEMOIN}\n",
                                      encoding="utf-8")
        e = mentions_a_lancien_endroit(r)
        v("un chemin vers l ancien endroit est nomme", any("campagne.sh" in a for a, _ in e),
          str(e))
        v("... avec le fichier qu il vise", any(b == MESURE_TEMOIN for _, b in e), str(e))
        (r / "campagne.sh").write_text(
            f"lplv mesurer --sortie {DESTINATIONS[MESURE]}/{MESURE_TEMOIN}\n", encoding="utf-8")
        v("... et repare, il se tait", mentions_a_lancien_endroit(r) == [], str(mentions_a_lancien_endroit(r)))
        # ⚠⚠ La promesse de la docstring de REGISTRES, EXECUTEE : un registre qu un script
        # produit a cesse d en etre un. C est ce controle qui a sorti `verbes.json` de la
        # liste -- il est lu comme une entree et pourtant produit par `lplv --verbes`.
        (r / "produit.sh").write_text(f"lplv recenser --json docs/{registre}\n",
                                      encoding="utf-8")
        v("un registre qu on ECRIT est nomme",
          any("produit.sh" in a for a, _ in registres_ecrits(r)), str(registres_ecrits(r)))
        (r / "produit.sh").write_text(f"lplv recenser > docs/{registre}\n", encoding="utf-8")
        v("... par redirection aussi",
          any("produit.sh" in a for a, _ in registres_ecrits(r)), str(registres_ecrits(r)))
        # ⚠ Et la citation Markdown qui s ecrit avec le meme caractere ne compte pas, meme
        # quand elle vit dans une chaine Python -- c est la forme exacte des deux faux
        # positifs mesures.
        (r / "prose.md").write_text(f"> [`docs/{registre}`]({registre}) est la source\n",
                                    encoding="utf-8")
        (r / "dans_du_code.py").write_text(f'    "> [`docs/{registre}`]({registre}) rendu",\n',
                                           encoding="utf-8")
        v("... mais une citation Markdown n est pas une redirection",
          not any("prose.md" in a or "dans_du_code.py" in a for a, _ in registres_ecrits(r)),
          str(registres_ecrits(r)))
        (r / "prose.md").unlink()
        (r / "dans_du_code.py").unlink()
        (r / "produit.sh").write_text(f"lplv lire {registre}\n", encoding="utf-8")
        v("... et une simple LECTURE ne l est pas", registres_ecrits(r) == [],
          str(registres_ecrits(r)))
        (r / "produit.sh").unlink()
        v("aucun registre de ce depot n est produit par un script",
          registres_ecrits(RACINE) == [], str(registres_ecrits(RACINE)))

        # ⚠⚠ La regle gitignore ANCREE : c est la panne silencieuse du rangement, et elle
        # va dans le sens le plus couteux -- des traces de run qui ENTRENT dans le depot.
        import subprocess as _sp
        _sp.run(["git", "-C", str(r), "init", "-q"], capture_output=True)
        (r / ".gitignore").write_text("/docs/*.log\n", encoding="utf-8")
        v("un ignore que le deplacement romprait est nomme",
          ignores_rompus(r) == [f"docs/{JOURNAL_TEMOIN}"], str(ignores_rompus(r)))
        (r / ".gitignore").write_text("/docs/*.log\n/docs/journaux/\n", encoding="utf-8")
        v("... et la regle reparee, il se tait", ignores_rompus(r) == [],
          str(ignores_rompus(r)))
        v("aucun ignore de ce depot ne serait rompu", ignores_rompus(RACINE) == [],
          str(ignores_rompus(RACINE)[:3]))

        # ⚠ Un `.md` n est PAS un ecrivain a reparer : les documents ne demenagent pas.
        (r / "d.md").write_text(f"voir docs/{DOC_TEMOIN}\n", encoding="utf-8")
        v("... et un chemin de document ne compte pas", mentions_a_lancien_endroit(r) == [])

    # ⚠⚠ Les deux controles qui portent sur CE depot, et pas sur une fixture. Le premier
    # est celui qui empeche le rangement de se defaire : un script qui recrée une mesure a la
    # racine de `docs/` produit un second fichier a cote du fichier range, l un frais et
    # l autre mort, sans qu aucune sortie ne change.
    restes = sorted(f.name for f in (RACINE / "docs").iterdir()
                    if f.is_file() and a_deplacer(nature(f.name)))
    v("aucune mesure ni journal ne traine a la racine de docs/", restes == [],
      ", ".join(restes[:5]))
    # ⚠ Les traces sont exclues NOMMEMENT : un chemin ecrit dans un resultat ou un journal
    # enregistre ce qui a tourne ce jour-la, et le reecrire falsifierait la mesure.
    dus = [(a, b) for a, b in mentions_a_lancien_endroit(RACINE)
           if not a.startswith((DESTINATIONS[MESURE] + "/", DESTINATIONS[JOURNAL] + "/"))]
    v("aucun script ne nomme encore l ancien endroit", dus == [],
      ", ".join(f"{a} ({b})" for a, b in dus[:3]))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    # ⚠⚠⚠ Le verdict imprimait « ALL PASS » et rendait 0 INCONDITIONNELLEMENT :
    # cette batterie était verte quoi que disent ses contrôles. Trente-neuf
    # fichiers du dépôt portaient le même défaut, corrigé le 2026-08-27.
    print(f"{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description="Classer docs/ par nature, et dire ce qui bloque.")
    p.add_argument("--verifier", action="store_true", help="lancer la batterie hors ligne")
    p.add_argument("--carte", action="store_true", help="ecrire la carte en JSON sur la sortie")
    a = p.parse_args()

    if a.verifier:
        return verifier()
    if a.carte:
        import json
        print(json.dumps(carte(), ensure_ascii=False, indent=2))
        return 0

    r = resume()
    print(f"docs/ a la racine — {sum(r.values())} fichiers")
    for n in (DOCUMENT, MESURE, JOURNAL, REGISTRE, "inclassable"):
        if r.get(n):
            dest = DESTINATIONS.get(n, "docs (inchange)")
            print(f"  {r[n]:>4}  {n:<12} -> {dest}")

    cites = journaux_cites()
    if cites:
        print(f"\n⚠ {len(cites)} journal/journaux CITE(S) par un document — un chiffre dont "
              f"la source est un journal n'est verifiable par personne :")
        for c in cites:
            print(f"    {c}")

    e = mentions_a_lancien_endroit()
    print(f"\n{len(e)} endroit(s) nomment encore un fichier a la racine de docs/ :")
    for endroit, quoi in e[:20]:
        print(f"    {endroit:<52} {quoi}")
    if len(e) > 20:
        print(f"    ... et {len(e) - 20} autres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
