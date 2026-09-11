#!/usr/bin/env python3
"""Les registres transverses : les `.tsv` POSSÈDENT, les rapports racontent, les vues sont rendues.

⚠⚠ POURQUOI CE FICHIER EXISTE, ET POURQUOI LE SENS A ÉTÉ INVERSÉ. Les §1 (les faits), §5 (les
contradictions), §6 (les lois) et §8 (les portes) des six rapports étaient des **tables** — donc de
la donnée écrite en prose. Tant qu'elle y vivait, elle n'était ni cherchable, ni triable, ni
modifiable ailleurs qu'en éditant un document de six cents lignes, et chaque rapport payait la
moitié de sa longueur pour la porter.

  ⭐ La donnée vit donc dans des `.tsv`, **et c'est eux la source**. Un rapport garde ce qu'un
  tableau ne sait pas dire : la fiche, les mouvements et leurs figures, la chronologie, ce que la
  campagne dit des prix, les sources pour un article. Il se lit alors en entier.

⚠ Le premier dessin faisait l'inverse — les rapports possédaient, les registres étaient dérivés —
et c'était le mauvais sens : il gardait la donnée dans la prose ET en écrivait une copie. Deux
exemplaires du même texte, dont l'un est plus difficile à interroger que l'autre. La correction
vient de l'auteur.

**Le contrat, en trois lignes :**

| | |
|---|---|
| `REGISTRE_*.tsv` | **la source.** Tenue à la main, versionnée, greppable, triable |
| `docs/rapports/R*.md` | la **lecture** : ce qui ne tient pas dans une table |
| `FILS_ROUGES.md`, `PORTES_OUVERTES.md` | des **vues rendues** depuis les `.tsv`, jamais éditées |

  ⭐⭐ Et la garde qui empêche le retour en arrière : **un rapport qui réintroduit une table de
     faits ou de contradictions fait échouer le contrôle.** Sans elle, la prose reprendrait la
     donnée un lot à la fois, et on se retrouverait avec deux sources libres de diverger — ce
     que ce dépôt a déjà payé trois fois (`75` D3, `80`, `87` §3).

  ./lplv registres              # ce que les registres portent, et ce qui cloche
  ./lplv registres --ecrire     # rend les deux vues markdown depuis les .tsv
  ./lplv registres --extraire   # MIGRATION, une seule fois : les tables des rapports → .tsv
  ./lplv registres --verifier   # ses propres contrôles, hors ligne
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
RAPPORTS = RACINE / "docs" / "rapports"

STATUTS = ("établi", "borné", "réfuté", "rétracté", "ouvert")
"""Les cinq statuts qu'un fait a le droit de porter, et leur ordre est celui de la carte.

⚠ `borné` n'est pas un `établi` faible : il dit qu'on tient une **borne** et pas une valeur, ce
qui est une information différente pour qui décide. Les confondre ferait lire « effet < 0,6 % »
comme « effet mesuré à 0,6 % »."""

SCHEMA: dict[str, tuple[str, ...]] = {
    "REGISTRE_faits.tsv": ("id", "campagne", "enonce", "valeur", "statut", "note", "source",
                           "producteur"),
    "REGISTRE_contradictions.tsv": ("id", "campagne", "a", "b", "c", "statut"),
    "REGISTRE_lois.tsv": ("id", "campagne", "titre", "texte"),
    "REGISTRE_portes.tsv": ("id", "campagne", "prix", "texte"),
    "REGISTRE_anteriorite.tsv": ("id", "resultat", "anteriorite", "statut"),
}
"""Les cinq registres et leurs colonnes.

⚠⚠ Il n'y a **pas** de colonne `rapport:ligne`. Le premier dessin en portait une, et elle aurait
pourri au premier lot : un numéro de ligne désigne un endroit d'un document qui bouge à chaque
édition, donc une ancre qui a l'air juste et ne l'est plus. Ce qui ancre un fait est sa
**source** — `archive/NN §k` — qui, elle, est gelée."""

VUES = ("REGISTRE_faits.md", "REGISTRE_contradictions.md", "FILS_ROUGES.md",
        "PORTES_OUVERTES.md", "ANTERIORITE.md")
"""Ce qui est rendu depuis les `.tsv`, et donc jamais édité à la main — un par registre.

⚠⚠ **Il y en a eu deux, et c'était trop peu.** J'avais écrit qu'un fait et une contradiction « se
lisent en colonnes, on les trie et on les grep », donc qu'ils n'avaient pas besoin de vue. Faux :
un `.tsv` dont les cellules font deux cents caractères ne se lit ni dans un terminal ni sur une
page. Les deux plus gros registres — 130 faits et 231 contradictions — se retrouvaient donc sans
**aucune** forme lisible, et le dossier était réellement moins complet qu'avant la bascule. Ce
n'est pas la donnée qui manquait, c'est sa lecture.

⚠ Une vue n'est pas une seconde source : elle est **générée**, elle le dit en première ligne, et
un contrôle échoue si elle ne correspond plus."""

PREFIXE_GENERE = "> ⚠ FICHIER GÉNÉRÉ depuis les `REGISTRE_*.tsv` — ne pas éditer à la main."

SOURCE = re.compile(r"`(\d{2,3}|HANDOFF)`")
r"""Ce qui compte comme une citation de preuve dans la colonne « source ».

⚠⚠ **Deux chiffres ne suffisent pas**, et le premier run l'a dit : l'archive va jusqu'à `114`,
donc une borne à `\d{2}` déclarait sans source les cinq faits de `R4` qui citent `104`, `106`,
`110`, `111` et `114` — c'est-à-dire précisément les documents les plus récents de la campagne du
graal. Une garde qui rate les entrées neuves est pire qu'une garde absente : elle vieillit en
silence."""


# ─────────────────────────────────────────────────────────────────────────────
# Lire et écrire les registres — la source
# ─────────────────────────────────────────────────────────────────────────────

def lire(nom: str, racine: Path = RACINE) -> list[dict]:
    """Un registre, ligne par ligne. Un fichier absent rend une liste vide.

    ⚠ Une ligne dont le compte de colonnes est faux est **gardée** avec la marque `mal_formee`.
    La jeter ferait disparaître une entrée sans que rien ne le dise, ce qui est exactement la
    panne qu'un registre existe pour ne pas avoir.
    """
    f = racine / "docs" / "rapports" / nom
    if not f.is_file():
        return []
    colonnes = SCHEMA[nom]
    out = []
    for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if not l.strip() or l.startswith("#"):
            continue
        champs = l.split("\t")
        if champs == list(colonnes):
            continue
        if len(champs) != len(colonnes):
            out.append({"ligne": n,
                        "mal_formee": f"{len(champs)} colonnes au lieu de {len(colonnes)}"})
            continue
        e = dict(zip(colonnes, champs))
        e["ligne"] = n
        e["mal_formee"] = ""
        out.append(e)
    return out


def tous(racine: Path = RACINE) -> dict[str, list[dict]]:
    """Les cinq registres d'un coup."""
    return {nom: lire(nom, racine) for nom in SCHEMA}


def ecrire(nom: str, lignes: list[dict], racine: Path = RACINE) -> None:
    """Écrit un registre, en-tête de colonnes compris.

    ⚠ Chaque cellule est purgée de ses tabulations et de ses retours à la ligne : une cellule qui
    en porte un décale toutes les colonnes suivantes, et un TSV décalé se lit **sans erreur**.
    """
    colonnes = SCHEMA[nom]

    def propre(x: str) -> str:
        return re.sub(r"[\t\r\n]+", " ", str(x)).strip()

    corps = ["\t".join(colonnes)]
    corps += ["\t".join(propre(e.get(c, "")) for c in colonnes) for e in lignes]
    (racine / "docs" / "rapports" / nom).write_text("\n".join(corps) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Lire les rapports — pour la migration, et pour la garde anti-retour
# ─────────────────────────────────────────────────────────────────────────────

def rapports(racine: Path = RACINE) -> list[Path]:
    """Les rapports de campagne, dans l'ordre R1 → R6.

    ⚠ `00_carte.md` et `PRIX.md` sont exclus **par leur forme** et pas par une liste
    d'exceptions : une liste serait une septième chose à tenir à jour le jour où un R7 apparaît.
    """
    return sorted((racine / "docs" / "rapports").glob("R[0-9]_*.md"))


def campagne(rapport: Path) -> str:
    """`R3` depuis `R3_graine_et_traceur.md`."""
    return rapport.name.split("_", 1)[0]


def sections(texte: str) -> dict[int, tuple[int, list[str]]]:
    """Les sections `## N.` d'un rapport → {N: (ligne de l'entête, lignes du corps)}."""
    lignes = texte.splitlines()
    bornes = [(int(m.group(1)), n) for n, l in enumerate(lignes, 1)
              if (m := re.match(r"^## (\d+)\.", l))]
    out: dict[int, tuple[int, list[str]]] = {}
    for i, (num, debut) in enumerate(bornes):
        fin = bornes[i + 1][1] - 1 if i + 1 < len(bornes) else len(lignes)
        out[num] = (debut, lignes[debut:fin])
    return out


ENTETES = ("#", "A", "résultat du dépôt", "id")
"""Les premières cellules qui désignent une ligne d'ENTÊTE et jamais une donnée.

⚠⚠ Une section peut porter PLUSIEURS tables — `R4` §1 en avait deux, la seconde pour la campagne
`0500P2`. Sauter seulement la première ligne d'entête lisait donc la seconde comme une donnée, et
le registre gagnait un fait dont l'énoncé est le mot « fait ». Un entête se reconnaît à ce qu'il
EST, pas à sa position."""


def cellules(ligne: str) -> list[str] | None:
    """Les cellules d'une ligne de table markdown, ou `None` si ce n'en est pas une."""
    l = ligne.strip()
    if not l.startswith("|") or not l.endswith("|"):
        return None
    champs = [c.strip() for c in l[1:-1].split("|")]
    if all(re.fullmatch(r":?-{2,}:?", c) for c in champs if c):
        return None
    return champs


def table(corps: list[str], colonnes: int) -> list[list[str]]:
    """Les lignes de données d'une table markdown, entêtes et séparateurs écartés."""
    out = []
    for l in corps:
        c = cellules(l)
        if c is None or c[0] in ENTETES or len(c) != colonnes:
            continue
        out.append(c)
    return out


def statut_et_note(cellule: str) -> tuple[str, str]:
    """`« établi ; X rétracté »` → `("établi", "X rétracté")`.

    ⚠ Le statut est le **premier** mot du vocabulaire rencontré, et la suite est une note. Un
    rapport écrit souvent « établi ; tel énoncé rétracté » : prendre le dernier mot connu
    classerait le fait dans le statut de ce qu'il **corrige**.
    """
    brut = re.sub(r"\*\*|\*|`", "", cellule).strip()
    for s in STATUTS:
        if brut.startswith(s):
            return s, brut[len(s):].lstrip(" ;:—-").strip()
    return "", brut


ITEM_NUMEROTE = re.compile(r"^(\d+)\.\s+(.*)$")
TITRE_GRAS = re.compile(r"\*\*(.+?)\*\*")
PRIX_ENTETE = re.compile(r"^\*\*(.+?)\*\*$")


def extraire(racine: Path = RACINE) -> dict[str, list[dict]]:
    """Les tables des rapports, sous la forme des registres — la MIGRATION, une seule fois.

    ⚠⚠ Cette fonction ne sert qu'à basculer la propriété. Une fois les tables retirées des
    rapports, elle rend des listes vides, et c'est le signe que la bascule a eu lieu — pas une
    panne. C'est pour ça qu'`--extraire` **refuse** d'écraser un registre existant : la seconde
    exécution effacerait la source avec le vide qu'elle vient de lire.
    """
    faits: list[dict] = []
    contras: list[dict] = []
    lois: list[dict] = []
    portes: list[dict] = []
    ant: list[dict] = []

    for f in rapports(racine):
        camp = campagne(f)
        s = sections(f.read_text(encoding="utf-8"))

        for c in table(s[1][1] if 1 in s else [], 5):
            statut, note = statut_et_note(c[3])
            src, _, prod = c[4].partition("·")
            faits.append({"campagne": camp, "enonce": c[1], "valeur": c[2], "statut": statut,
                          "note": note, "source": src.strip(), "producteur": prod.strip()})

        for c in table(s[5][1] if 5 in s else [], 4):
            contras.append({"campagne": camp, "a": c[0], "b": c[1], "c": c[2], "statut": c[3]})

        if camp == "R6":
            for c in table(s[4][1] if 4 in s else [], 3):
                ant.append({"resultat": c[0], "anteriorite": c[1], "statut": c[2]})

        courant: dict | None = None
        for l in (s[6][1] if 6 in s else []):
            m = ITEM_NUMEROTE.match(l)
            if m:
                if courant:
                    lois.append(courant)
                courant = {"campagne": camp, "texte": m.group(2).strip()}
            elif courant is not None and l.startswith("   ") and l.strip():
                courant["texte"] += " " + l.strip()
        if courant:
            lois.append(courant)

        prix = ""
        courant = None
        for l in (s[8][1] if 8 in s else []):
            m = PRIX_ENTETE.match(l.strip())
            if m and not l.startswith(" "):
                if courant:
                    portes.append(courant)
                    courant = None
                prix = m.group(1).strip()
                continue
            if l.startswith("- "):
                if courant:
                    portes.append(courant)
                courant = {"campagne": camp, "prix": prix, "texte": l[2:].strip()}
            elif courant is not None and l.startswith("  ") and l.strip():
                courant["texte"] += " " + l.strip()
            elif courant is not None and not l.strip():
                portes.append(courant)
                courant = None
        if courant:
            portes.append(courant)

    for e in lois:
        t = TITRE_GRAS.search(e["texte"])
        e["titre"] = (t.group(1) if t else e["texte"].split(".")[0]).strip(" .")
        e["texte"] = re.sub(r"^\*\*.+?\*\*\s*", "", e["texte"]).strip()

    # ⚠ Les identifiants sont attribués À LA FIN, par campagne : les numéroter au fil de la
    # lecture rendrait `R2-F01` dépendant du fait que `R1` ait été lu avant, donc d'un ordre de
    # glob. Un identifiant qui change parce qu'un fichier a été renommé n'est pas un identifiant.
    for suite, lettre in ((faits, "F"), (contras, "C"), (lois, "L"), (portes, "P")):
        compte: dict[str, int] = {}
        for e in suite:
            compte[e["campagne"]] = compte.get(e["campagne"], 0) + 1
            e["id"] = f"{e['campagne']}-{lettre}{compte[e['campagne']]:02d}"
    for i, e in enumerate(ant, 1):
        e["id"] = f"A{i:02d}"

    return {"REGISTRE_faits.tsv": faits, "REGISTRE_contradictions.tsv": contras,
            "REGISTRE_lois.tsv": lois, "REGISTRE_portes.tsv": portes,
            "REGISTRE_anteriorite.tsv": ant}


TABLES_INTERDITES = (
    ("| # | fait | valeur | statut |", "REGISTRE_faits.tsv"),
    ("| A | B | C | statut |", "REGISTRE_contradictions.tsv"),
    ("| résultat du dépôt | antériorité | statut |", "REGISTRE_anteriorite.tsv"),
)
"""Les entêtes qu'un rapport n'a plus le droit de porter, et où la donnée vit désormais.

⭐⭐ C'est la garde qui empêche le retour en arrière. Sans elle, la prose reprendrait la donnée un
lot à la fois — et on se retrouverait avec deux sources libres de diverger, ce que ce dépôt a
payé trois fois (`75` D3, `80`, `87` §3)."""


def non_porte(racine: Path = RACINE) -> list[str]:
    """Ce qu'un rapport porte encore et qu'AUCUN registre ne transporte.

    ⭐⭐ C'est le contrôle qui autorise une suppression, et il n'y en a pas d'autre. Retirer une
    table d'un rapport parce qu'« elle a été migrée » sur la foi d'un compte, c'est faire
    confiance à un total ; deux ensembles de 130 lignes peuvent avoir le même total et ne pas
    porter les mêmes lignes. La comparaison se fait donc **énoncé par énoncé**.

    ⚠ La comparaison porte sur le texte **normalisé** (espaces repliés) et non sur les octets :
    une cellule traverse le TSV en perdant ses retours à la ligne, donc exiger l'égalité stricte
    signalerait comme perdu tout ce qui a été correctement transporté.
    """
    def norme(x: str) -> str:
        return re.sub(r"\s+", " ", x).strip()

    reg = tous(racine)
    connus = {
        "fait": {norme(e["enonce"]) for e in reg["REGISTRE_faits.tsv"] if not e["mal_formee"]},
        "contradiction": {norme(e["a"]) for e in reg["REGISTRE_contradictions.tsv"]
                          if not e["mal_formee"]},
        "antériorité": {norme(e["resultat"]) for e in reg["REGISTRE_anteriorite.tsv"]
                        if not e["mal_formee"]},
        "loi": {norme(e["titre"]) for e in reg["REGISTRE_lois.tsv"] if not e["mal_formee"]},
        "porte": {norme(e["texte"])[:80] for e in reg["REGISTRE_portes.tsv"]
                  if not e["mal_formee"]},
    }
    out = []
    for f in rapports(racine):
        s = sections(f.read_text(encoding="utf-8"))
        for c in table(s[1][1] if 1 in s else [], 5):
            if norme(c[1]) not in connus["fait"]:
                out.append(f"{f.name} fait NON PORTÉ : {c[1][:70]}")
        for c in table(s[5][1] if 5 in s else [], 4):
            if norme(c[0]) not in connus["contradiction"]:
                out.append(f"{f.name} contradiction NON PORTÉE : {c[0][:70]}")
        if campagne(f) == "R6":
            for c in table(s[4][1] if 4 in s else [], 3):
                if norme(c[0]) not in connus["antériorité"]:
                    out.append(f"{f.name} antériorité NON PORTÉE : {c[0][:70]}")
        for e in extraire_une(f, 6):
            if norme(e) not in connus["loi"]:
                out.append(f"{f.name} loi NON PORTÉE : {e[:70]}")
        for e in extraire_une(f, 8):
            if norme(e)[:80] not in connus["porte"]:
                out.append(f"{f.name} porte NON PORTÉE : {e[:70]}")
    return out


def extraire_une(f: Path, num: int) -> list[str]:
    """Les titres des lois (§6) ou les textes des portes (§8) d'un rapport, pour la comparaison."""
    s = sections(f.read_text(encoding="utf-8"))
    if num not in s:
        return []
    out = []
    courant: str | None = None
    for l in s[num][1]:
        if num == 6:
            m = ITEM_NUMEROTE.match(l)
            if m:
                if courant:
                    out.append(courant)
                courant = m.group(2).strip()
            elif courant is not None and l.startswith("   ") and l.strip():
                courant += " " + l.strip()
        else:
            if PRIX_ENTETE.match(l.strip()) and not l.startswith(" "):
                if courant:
                    out.append(courant)
                    courant = None
                continue
            if l.startswith("- "):
                if courant:
                    out.append(courant)
                courant = l[2:].strip()
            elif courant is not None and l.startswith("  ") and l.strip():
                courant += " " + l.strip()
            elif courant is not None and not l.strip():
                out.append(courant)
                courant = None
    if courant:
        out.append(courant)
    if num == 6:
        finis = []
        for e in out:
            t = TITRE_GRAS.search(e)
            finis.append((t.group(1) if t else e.split(".")[0]).strip(" ."))
        return finis
    return out


def tables_revenues(racine: Path = RACINE) -> list[str]:
    """Les rapports qui ont réintroduit une table dont la donnée appartient à un registre."""
    out = []
    for f in rapports(racine):
        for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for entete, registre in TABLES_INTERDITES:
                if l.strip().startswith(entete):
                    out.append(f"{f.name}:{n} — cette table appartient à {registre}")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Rendre les deux vues
# ─────────────────────────────────────────────────────────────────────────────

def _entete(titre: str, source: str, chapeau: str) -> list[str]:
    """Le bandeau commun des vues : ce que c'est, d'où ça vient, comment le régénérer."""
    return [PREFIXE_GENERE + " Régénérer : `./lplv registres --ecrire`.", ">",
            f"> Source : `docs/rapports/{source}`.", "", f"# {titre}", "", chapeau, ""]


def rendre(racine: Path = RACINE) -> dict[str, str]:
    """Les cinq vues markdown, en mémoire — écrire est une décision séparée."""
    reg = tous(racine)
    faits = [e for e in reg["REGISTRE_faits.tsv"] if not e["mal_formee"]]
    contras = [e for e in reg["REGISTRE_contradictions.tsv"] if not e["mal_formee"]]
    ant = [e for e in reg["REGISTRE_anteriorite.tsv"] if not e["mal_formee"]]
    lois = [e for e in reg["REGISTRE_lois.tsv"] if not e["mal_formee"]]
    portes = [e for e in reg["REGISTRE_portes.tsv"] if not e["mal_formee"]]

    par_statut: dict[str, int] = {}
    for e in faits:
        par_statut[e["statut"]] = par_statut.get(e["statut"], 0) + 1
    md_f = _entete("Les faits, et ce qu'ils valent aujourd'hui", "REGISTRE_faits.tsv",
                   f"**{len(faits)} faits**, un par ligne, avec la valeur qui les porte, le statut "
                   f"qu'ils ont aujourd'hui, la source qui les prouve et le producteur qui les "
                   f"recalcule. Répartition : "
                   + ", ".join(f"**{par_statut.get(x, 0)}** {x}" for x in STATUTS) + ".")
    for camp in sorted({e["campagne"] for e in faits}):
        dedans = [e for e in faits if e["campagne"] == camp]
        md_f += [f"## {camp} — {len(dedans)} faits", "",
                 "| id | fait | valeur | statut | source · producteur |", "|---|---|---|---|---|"]
        for e in dedans:
            note = f" ; {e['note']}" if e["note"] else ""
            prod = f" · {e['producteur']}" if e["producteur"] else ""
            md_f.append(f"| `{e['id']}` | {e['enonce']} | {e['valeur']} | "
                        f"{e['statut']}{note} | {e['source']}{prod} |")
        md_f.append("")

    md_c = _entete("Les contradictions, et qui a tranché", "REGISTRE_contradictions.tsv",
                   f"**{len(contras)} disputes** que ce dépôt a eues avec lui-même, et comment "
                   f"chacune s'est finie. Une ligne : *A a dit · B a dit · C tranche · statut*. "
                   f"Les lire coûte moins cher que de les repayer.")
    for camp in sorted({e["campagne"] for e in contras}):
        dedans = [e for e in contras if e["campagne"] == camp]
        md_c += [f"## {camp} — {len(dedans)} lignes", "",
                 "| id | A a dit | B a dit | C tranche | statut |", "|---|---|---|---|---|"]
        for e in dedans:
            md_c.append(f"| `{e['id']}` | {e['a']} | {e['b']} | {e['c']} | {e['statut']} |")
        md_c.append("")

    md_a = _entete("L'antériorité — ce que le domaine avait déjà publié", "REGISTRE_anteriorite.tsv",
                   f"**{len(ant)} rencontres** entre un résultat de ce dépôt et la littérature. "
                   f"À lire avant de revendiquer quoi que ce soit, et pour citer.")
    md_a += ["| id | résultat du dépôt | antériorité | statut |", "|---|---|---|---|"]
    for e in ant:
        md_a.append(f"| `{e['id']}` | {e['resultat']} | {e['anteriorite']} | {e['statut']} |")
    md_a.append("")

    md_l = _entete("Les fils rouges — les lois que ce dépôt a payées", "REGISTRE_lois.tsv",
                   f"**{len(lois)} mécanismes** qui traversent les campagnes. Chacun a été payé au "
                   f"moins une fois, et le prix est dans le rapport qui le porte.")
    for camp in sorted({e["campagne"] for e in lois}):
        dedans = [e for e in lois if e["campagne"] == camp]
        md_l += [f"## {camp} — {len(dedans)} lois", ""]
        for e in dedans:
            md_l += [f"**{e['id']} · {e['titre']}**", "", e["texte"], ""]

    # ⚠⚠ Un entête de §8 portait DEUX informations — le prix, et ce que cette campagne lui
    # apporte : « Grand Prize — le graal », « Grand Prize — le référent ». Les traiter comme des
    # groupes distincts éclatait le Grand Prize en quatre sections dont aucune ne disait combien
    # de portes il reste, c'est-à-dire la seule question qu'on pose à cette page.
    groupes: dict[str, list[dict]] = {}
    for e in portes:
        prix, _, angle = (e["prix"] or "(non classé par prix)").partition("—")
        groupes.setdefault(prix.strip(), []).append({**e, "angle": angle.strip()})
    md_p = _entete("Les portes ouvertes, classées par prix", "REGISTRE_portes.tsv",
                   f"**{len(portes)} portes** que les six campagnes laissent. Le classement est "
                   f"celui du rapport qui la laisse ; une porte sans prix est une porte que "
                   f"personne n'a classée, et elle est gardée telle quelle.")
    for prix in sorted(groupes, key=lambda x: (x.startswith("("), x)):
        md_p += [f"## {prix} — {len(groupes[prix])} portes", ""]
        for e in groupes[prix]:
            angle = f" *({e['angle']})*" if e["angle"] else ""
            md_p.append(f"- **{e['id']}**{angle} · {e['texte']}")
        md_p.append("")

    return {"REGISTRE_faits.md": "\n".join(md_f),
            "REGISTRE_contradictions.md": "\n".join(md_c),
            "ANTERIORITE.md": "\n".join(md_a),
            "FILS_ROUGES.md": "\n".join(md_l),
            "PORTES_OUVERTES.md": "\n".join(md_p)}


def perimes(racine: Path = RACINE) -> list[str]:
    """Les vues qui ne correspondent plus aux registres — absentes comprises.

    ⚠ Une vue **absente** est signalée comme périmée et pas comme « rien à faire » : les deux se
    réparent par la même commande, et les distinguer inviterait à lire la seconde comme un état
    normal.
    """
    out = []
    for nom, contenu in rendre(racine).items():
        f = racine / "docs" / "rapports" / nom
        if not f.is_file() or f.read_text(encoding="utf-8") != contenu:
            out.append(nom)
    return out


def defauts(racine: Path = RACINE) -> dict[str, list[str]]:
    """Ce qui cloche dans les registres eux-mêmes, et dans le contrat avec les rapports."""
    out: dict[str, list[str]] = {"lignes_mal_formees": [], "statuts_inconnus": [],
                                 "faits_sans_source": [], "identifiants_doublons": [],
                                 "tables_revenues": tables_revenues(racine)}
    vus: set[str] = set()
    for nom, lignes in tous(racine).items():
        for e in lignes:
            if e["mal_formee"]:
                out["lignes_mal_formees"].append(f"{nom}:{e['ligne']} ({e['mal_formee']})")
                continue
            if e["id"] in vus:
                out["identifiants_doublons"].append(f"{nom}:{e['ligne']} {e['id']}")
            vus.add(e["id"])
            if nom == "REGISTRE_faits.tsv":
                if e["statut"] not in STATUTS:
                    out["statuts_inconnus"].append(f"{nom}:{e['ligne']} « {e['statut'][:30]} »")
                if not SOURCE.search(e["source"]):
                    out["faits_sans_source"].append(f"{nom}:{e['ligne']} {e['enonce'][:50]}")
    return out


def verifier() -> int:
    """Le module se garde lui-même, hors ligne, sur des registres FABRIQUÉS.

    ⚠⚠ Les contrôles ne portent pas sur les vrais registres : un contrôle qui lit l'arbre mesure
    ce que l'arbre contient aujourd'hui, donc il passe au vert le jour où un registre disparaît.
    Les sondes, elles, remettent chaque défaut et exigent le rouge.
    """
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "docs" / "rapports").mkdir(parents=True)
        ecrire("REGISTRE_faits.tsv", [
            {"id": "R1-F01", "campagne": "R1", "enonce": "le premier fait", "valeur": "**12,3**",
             "statut": "établi", "note": "", "source": "`08` §2", "producteur": "`a.py`"},
            {"id": "R1-F02", "campagne": "R1", "enonce": "le second", "valeur": "4",
             "statut": "borné", "note": "« X » rétracté", "source": "`114` §1",
             "producteur": "`b.py`"}], r)
        ecrire("REGISTRE_contradictions.tsv", [
            {"id": "R1-C01", "campagne": "R1", "a": "`08` dit ceci", "b": "`09` dit cela",
             "c": "la mesure tranche", "statut": "tranché"}], r)
        ecrire("REGISTRE_lois.tsv", [
            {"id": "R1-L01", "campagne": "R1", "titre": "Une loi", "texte": "Sa raison."},
            {"id": "R2-L01", "campagne": "R2", "titre": "Une autre", "texte": "Courte."}], r)
        ecrire("REGISTRE_portes.tsv", [
            {"id": "R1-P01", "campagne": "R1", "prix": "Grand Prize — le graal",
             "texte": "une porte"},
            {"id": "R1-P02", "campagne": "R1", "prix": "", "texte": "une porte sans prix"}], r)
        ecrire("REGISTRE_anteriorite.tsv", [
            {"id": "A01", "resultat": "un résultat", "anteriorite": "un papier",
             "statut": "publié"}], r)

        reg = tous(r)
        v("les deux faits sont relus", len(reg["REGISTRE_faits.tsv"]), 2)
        v("la valeur traverse le TSV", reg["REGISTRE_faits.tsv"][0]["valeur"], "**12,3**")
        v("la note de statut aussi", reg["REGISTRE_faits.tsv"][1]["note"], "« X » rétracté")
        v("les cinq registres sont lus", sorted(reg), sorted(SCHEMA))

        d0 = defauts(r)
        v("aucune ligne mal formée", d0["lignes_mal_formees"], [])
        v("aucun statut inconnu", d0["statuts_inconnus"], [])
        v("un document à trois chiffres compte comme une source", d0["faits_sans_source"], [])
        v("aucun identifiant en double", d0["identifiants_doublons"], [])
        v("aucune table revenue dans un rapport", d0["tables_revenues"], [])

        vues = rendre(r)
        v("les cinq vues sont rendues", sorted(vues), sorted(VUES))
        v("la vue des faits montre l'énoncé, pas seulement l'identifiant",
          "le premier fait" in vues["REGISTRE_faits.md"], True)
        v("... et sa valeur", "**12,3**" in vues["REGISTRE_faits.md"], True)
        v("... et sa note de statut", "« X » rétracté" in vues["REGISTRE_faits.md"], True)
        v("la vue des contradictions montre les trois voix",
          all(x in vues["REGISTRE_contradictions.md"]
              for x in ("`08` dit ceci", "`09` dit cela", "la mesure tranche")), True)
        v("la vue de l'antériorité montre le papier",
          "un papier" in vues["ANTERIORITE.md"], True)
        v("chaque vue se déclare générée",
          all(x.startswith(PREFIXE_GENERE) for x in vues.values()), True)
        v("la vue des portes groupe par PRIX, pas par entête",
          "## Grand Prize — 1 portes" in vues["PORTES_OUVERTES.md"], True)
        v("... et garde l'angle de la campagne",
          "*(le graal)*" in vues["PORTES_OUVERTES.md"], True)
        v("une porte sans prix est gardée, pas rangée d'office",
          "(non classé par prix)" in vues["PORTES_OUVERTES.md"], True)
        v("une vue absente est périmée", sorted(perimes(r)), sorted(VUES))
        v("aucune vue n'est un registre (sinon la garde anti-retour se mordrait la queue)",
          [x for x in VUES if x.replace(".md", ".tsv") in SCHEMA and x.endswith(".tsv")], [])
        for nom, contenu in vues.items():
            (r / "docs" / "rapports" / nom).write_text(contenu, encoding="utf-8")
        v("... et cesse de l'être une fois écrite", perimes(r), [])

        # ⚠⚠ LES SONDES. Une batterie verte au premier essai ne prouve rien (`61`) : chaque
        # défaut est remis, et le contrôle doit rougir.
        f = r / "docs" / "rapports" / "REGISTRE_faits.tsv"
        original = f.read_text(encoding="utf-8")

        f.write_text(original.replace("\tétabli\t", "\tpresque\t"), encoding="utf-8")
        v("sonde : un statut hors vocabulaire est signalé",
          len(defauts(r)["statuts_inconnus"]), 1)

        f.write_text(original.replace("\t`08` §2\t", "\tsans source\t"), encoding="utf-8")
        v("sonde : un fait sans source est signalé", len(defauts(r)["faits_sans_source"]), 1)

        f.write_text(original.replace("R1-F02", "R1-F01"), encoding="utf-8")
        v("sonde : un identifiant en double est signalé",
          len(defauts(r)["identifiants_doublons"]), 1)

        f.write_text(original.replace("le premier fait\t", "le premier\tfait\t"), encoding="utf-8")
        v("sonde : une colonne de trop est signalée, jamais sautée",
          len(defauts(r)["lignes_mal_formees"]), 1)
        v("... et la ligne n'est pas comptée comme un fait",
          len([x for x in lire("REGISTRE_faits.tsv", r) if not x["mal_formee"]]), 1)

        f.write_text(original, encoding="utf-8")
        v("tout revient au vert une fois le registre restauré",
          [x for x in defauts(r).values() if x], [])

        # ⭐⭐ LA garde du nouvel arrangement : une table revenue dans un rapport.
        essai = r / "docs" / "rapports" / "R1_essai.md"
        essai.write_text("# R1\n\n## 1. Faits\n\n| # | fait | valeur | statut | source |\n"
                         "|--:|---|---|---|---|\n| 1 | x | y | établi | `08` |\n",
                         encoding="utf-8")
        v("sonde : un rapport qui réintroduit la table des faits est signalé",
          len(defauts(r)["tables_revenues"]), 1)
        v("... et la garde NOMME le registre propriétaire",
          "REGISTRE_faits.tsv" in defauts(r)["tables_revenues"][0], True)

        essai.write_text("# R1\n\n## 2. Mouvements\n\nde la prose, et un renvoi à `R1-F01`.\n",
                         encoding="utf-8")
        v("... et un rapport qui renvoie au registre passe", defauts(r)["tables_revenues"], [])

        # ⚠ La migration, exercée dans le sens où elle sert : une table de rapport devient des
        # lignes de registre, et un rapport sans table n'en produit aucune.
        essai.write_text("# R1\n\n## 1. Faits\n\n| # | fait | valeur | statut | source · producteur |\n"
                         "|--:|---|---|---|---|\n"
                         "| 1 | un fait migré | 7 | établi | `08` §1 · `x.py` |\n"
                         "\n## 6. Lois\n\n1. **Un titre.** Le corps.\n"
                         "\n## 8. Portes\n\n**Grand Prize**\n- une porte\n", encoding="utf-8")
        mig = extraire(r)
        v("la migration lit le fait", len(mig["REGISTRE_faits.tsv"]), 1)
        v("... avec son producteur", mig["REGISTRE_faits.tsv"][0]["producteur"], "`x.py`")
        v("... et son identifiant est dérivé de la campagne",
          mig["REGISTRE_faits.tsv"][0]["id"], "R1-F01")
        v("la migration lit la loi et lui donne un titre",
          mig["REGISTRE_lois.tsv"][0]["titre"], "Un titre")
        v("... sans recopier le titre dans le corps",
          mig["REGISTRE_lois.tsv"][0]["texte"], "Le corps.")
        v("la migration lit la porte et son prix",
          mig["REGISTRE_portes.tsv"][0]["prix"], "Grand Prize")
        essai.unlink()
        v("un rapport sans table ne produit aucune ligne",
          sum(len(x) for x in extraire(r).values()), 0)

        # ⚠ Le contrôle du contrôle : une ligne de séparation ne doit jamais devenir une donnée.
        v("une ligne de tirets n'est pas une donnée", cellules("|---|---|"), None)
        v("une ligne hors table non plus", cellules("du texte"), None)
        v("une vraie ligne l'est", cellules("| a | b |"), ["a", "b"])

    # ⚠⚠ Le verdict et la sortie viennent du MÊME compteur, et c'est le garde-fou du dépôt qui
    # l'a exigé : ma première version imprimait le compte puis rendait le littéral `0`, soit
    # exactement le défaut de `61` — une batterie verte quoi que disent ses contrôles — écrit
    # dans le module qui sert à ranger ce défaut. Trouvé par
    # `batteries_incapables_dechouer.py` au premier passage, pas par relecture.
    print(f"{'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ecrire", action="store_true", help="rendre les vues markdown")
    p.add_argument("--extraire", action="store_true",
                   help="MIGRATION : les tables des rapports → les .tsv (refuse d'écraser)")
    p.add_argument("--comparer", action="store_true",
                   help="ce qu'un rapport porte encore et qu'aucun registre ne transporte")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    if a.comparer:
        manque = non_porte()
        for x in manque:
            print(f"  ⚠ {x}")
        print(f"\n{len(manque)} entrée(s) de rapport que les registres ne portent pas")
        if not manque:
            print("✅ tout ce que les rapports portent encore est dans un registre —\n"
                  "   les tables peuvent être retirées sans rien perdre")
        return 1 if manque else 0

    if a.extraire:
        deja = [n for n in SCHEMA if (RAPPORTS / n).is_file()]
        if deja:
            print("⚠ refus : ces registres existent déjà, et ce sont EUX la source —\n    "
                  + "\n    ".join(deja))
            print("    les réécrire depuis les rapports effacerait ce qu'ils portent.")
            return 2
        for nom, lignes in extraire().items():
            ecrire(nom, lignes)
            print(f"  {len(lignes):>4}  {nom}")
        print("\n✅ migration faite. Les tables peuvent maintenant QUITTER les rapports.")
        return 0

    reg = tous()
    par_statut: dict[str, int] = {}
    for e in reg["REGISTRE_faits.tsv"]:
        if not e["mal_formee"]:
            par_statut[e["statut"]] = par_statut.get(e["statut"], 0) + 1
    print("les registres, qui sont la source :")
    for nom, lignes in reg.items():
        print(f"  {len(lignes):>4}  {nom}")
    print("      " + ", ".join(f"{par_statut.get(s, 0)} {s}" for s in STATUTS))

    d = defauts()
    if any(d.values()):
        print("\n⚠ ce qui cloche :")
        for cle, valeurs in d.items():
            for x in valeurs:
                print(f"    {cle:<22} {x}")

    p_ = perimes()
    if p_:
        print(f"\n⚠ {len(p_)} vue(s) à (re)générer : " + ", ".join(sorted(p_)))
        print("    ./lplv registres --ecrire")
    else:
        print(f"\n✅ les {len(VUES)} vues sont à jour")

    if a.ecrire:
        for nom, contenu in rendre().items():
            (RAPPORTS / nom).write_text(contenu, encoding="utf-8")
        print(f"\n✅ {len(VUES)} vues écrites dans docs/rapports/")

    if a.json:
        import json
        a.json.write_text(json.dumps(
            {nom: len(lignes) for nom, lignes in reg.items()}
            | {"par_statut": par_statut, "defauts": d, "vues_perimees": sorted(p_)},
            indent=1, ensure_ascii=False), encoding="utf-8")
    return 1 if any(d.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
