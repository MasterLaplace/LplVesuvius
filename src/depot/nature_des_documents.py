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
       voit, alors qu'un script qui recrée `docs/x.json` après le rangement produit **deux
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
    REGISTRE: "docs/registres",
}
"""Où chaque nature va vivre. ⚠ `document` reste à la racine : c'est ce que « docs » veut
dire, et un `docs/documents/` mettrait le contenu du dossier à un niveau de son nom."""

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

REGISTRES = ("murs_et_causes.tsv", "verbes.json")
"""Les fichiers de `docs/` qu'un HUMAIN maintient, et qu'aucune campagne ne réécrit.

⚠⚠ Les nommer plutôt que les dériver est un choix, parce qu'ils sont deux : une dérivation
« ce que personne n'écrit » serait plus de code, plus fragile, et fausse le jour où un tel
fichier n'est simplement lu par rien encore. Mais le nommage se VÉRIFIE — `verifier()` échoue
si l'un d'eux devient une cible d'écriture, c'est-à-dire cesse d'être un registre."""

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

    ⚠ Il cherche la FORME textuelle `docs/x.json`. Un chemin assemblé à l'exécution
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


def journaux_cites(racine: Path = RACINE) -> list[str]:
    """Les journaux qu'un document cite — donc mal classés, ou cités pour un chiffre.

    ⚠ Un chiffre dont la source est un journal n'est vérifiable par personne : un journal
    n'a pas de forme. Le trouver veut dire qu'il faut publier la mesure, pas déplacer le log.
    """
    import re

    motif = re.compile(r"docs/([A-Za-z0-9_.-]+\.log)")
    vus = set()
    for f in sorted((racine / "docs").glob("*.md")):
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
    v("... et l autre aussi", nature("verbes.json") == REGISTRE)
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
        for nom in (DOC_TEMOIN, "README.md", "t.json", "c.log", registre, "x.bin"):
            (r / "docs" / nom).write_text("x", encoding="utf-8")
        (r / "docs" / "champ_PHerc0172").mkdir()
        (r / "docs" / "champ_PHerc0172" / "dedans.json").write_text("x", encoding="utf-8")
        c = carte(r)
        v("la carte prend la mesure", c.get("docs/t.json") == "docs/mesures", str(c))
        v("... le journal", c.get("docs/c.log") == "docs/journaux")
        v("... le registre", c.get(f"docs/{registre}") == "docs/registres")
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
        (r / "campagne.sh").write_text("lplv mesurer --sortie docs/t.json\n", encoding="utf-8")
        e = mentions_a_lancien_endroit(r)
        v("un chemin vers l ancien endroit est nomme", any("campagne.sh" in a for a, _ in e),
          str(e))
        v("... avec le fichier qu il vise", any(b == "t.json" for _, b in e), str(e))
        (r / "campagne.sh").write_text("lplv mesurer --sortie docs/mesures/t.json\n",
                                       encoding="utf-8")
        v("... et repare, il se tait", mentions_a_lancien_endroit(r) == [], str(mentions_a_lancien_endroit(r)))
        # ⚠ Un `.md` n est PAS un ecrivain a reparer : les documents ne demenagent pas.
        (r / "d.md").write_text(f"voir docs/{DOC_TEMOIN}\n", encoding="utf-8")
        v("... et un chemin de document ne compte pas", mentions_a_lancien_endroit(r) == [])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


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
