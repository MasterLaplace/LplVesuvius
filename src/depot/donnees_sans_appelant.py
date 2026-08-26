#!/usr/bin/env python3
"""Quel dossier de `data/` plus rien ne nomme — et ce qu'il pèse.

⚠⚠ POURQUOI CE FICHIER EXISTE, ET POURQUOI IL NE DÉPLACE RIEN. Le plan du grand ménage
(`docs/56`) proposait de ranger `data/` par ROULEAU. Quatre mesures l'ont contredit :
`data/` est **entièrement gitignoré** (zéro fichier suivi, donc qui clone le dépôt ne le
reçoit pas), **11 dossiers sur 81** seulement nomment un rouleau, `data/trace/` groupe déjà
par rouleau *à l'intérieur*, et le déplacement coûterait 296 citations et 177 Gio. Ranger là
n'achèterait rien de visible.

⭐ La question que `data/` pose vraiment, à cette taille, n'est pas « où est-ce rangé » mais
**« qu'est-ce que je peux effacer »**. C'est celle-ci que ce fichier répond.

⚠⚠⚠ NOMMER N'EST PAS EFFACER, et ce script n'efface jamais. Un dossier que rien ne nomme
peut être une entrée téléchargée une fois et jamais citée, ou le résultat d'une campagne qu'on
n'a pas encore écrite. Dire « périmé » et remplacer sont deux actes — la même discipline que
`fraicheur_des_figures.py`, qui ne touche jamais `docs/images/`.

⚠ Et la nuance qui rend le verdict utilisable : un dossier nommé **seulement dans un journal**
n'est pas nommé par du code vivant. Un journal enregistre ce qui a tourné ce jour-là ; il
prouve un usage PASSÉ, pas un besoin PRÉSENT. Les deux sont donc rapportés séparément, parce
que les confondre ferait effacer ce qui permet de recouper une campagne déjà publiée.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DONNEES = "data"
JOURNAUX = "docs/journaux"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appelants import index_des_lignes  # noqa: E402


def dossiers(racine: Path = RACINE) -> list[str]:
    """Les entrées de premier niveau de `data/`, triées.

    ⚠ Les noms qui commencent par un point sont sautés : `data/.lances` est la trace des
    lancements, gérée par `lancer.sh` et par sa propre rétention. La classer ici la
    proposerait à l'effacement à chaque passage, alors qu'elle a déjà un propriétaire.
    """
    d = racine / DONNEES
    if not d.is_dir():
        return []
    return sorted(e.name for e in d.iterdir() if not e.name.startswith("."))


def qui_nomme(textes: dict[str, str], nom: str) -> list[str]:
    """Les fichiers qui nomment `data/<nom>`.

    ⚠ La recherche porte sur le CHEMIN complet, jamais sur le nom nu. `data/out` et `data/`
    `trace` portent des noms qui sont des mots courants : chercher « out » les déclarerait
    vivants depuis n'importe quelle prose. C'est la même discipline que le préfixe d'un
    identifiant, qui n'en est un que si un document en définit un membre.
    """
    cible = f"{DONNEES}/{nom}"
    return sorted(f for f, t in textes.items() if cible in t)


def journaux(racine: Path = RACINE) -> dict[str, str]:
    """Le texte des journaux de run. ⚠ Lus à part parce que `index_des_lignes` ne lit pas les
    `.log` — et c'est voulu : un journal n'appelle rien, il se souvient."""
    d = racine / JOURNAUX
    if not d.is_dir():
        return {}
    out = {}
    for f in sorted(d.glob("*.log")):
        try:
            out[str(f.relative_to(racine))] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return out


def poids(chemin: Path) -> int:
    """Les octets qu'effacer ce dossier libérerait, chaque inode compté UNE fois.

    ⚠ Compter deux fois un fichier en double lien annoncerait un gain qui n'arrivera pas —
    c'est la mesure que `poids_recuperable.py` a dû corriger sur le cache de `uv`, où `du`
    surestimait d'un facteur quatre.
    """
    vus, total = set(), 0
    pile = [chemin]
    while pile:
        d = pile.pop()
        try:
            entrees = list(d.iterdir())
        except OSError:
            continue
        for e in entrees:
            try:
                st = e.lstat()
            except OSError:
                continue
            if e.is_dir() and not e.is_symlink():
                pile.append(e)
            elif st.st_ino not in vus:
                vus.add(st.st_ino)
                total += st.st_size
    return total


def classer(racine: Path = RACINE, textes: dict[str, str] | None = None,
            traces: dict[str, str] | None = None) -> dict[str, list[str]]:
    """`{vivants, en_journal_seulement, orphelins}` — les dossiers de `data/` par classe."""
    textes = index_des_lignes(racine) if textes is None else textes
    traces = journaux(racine) if traces is None else traces
    out: dict[str, list[str]] = {"vivants": [], "en_journal_seulement": [], "orphelins": []}
    for nom in dossiers(racine):
        if qui_nomme(textes, nom):
            out["vivants"].append(nom)
        elif qui_nomme(traces, nom):
            out["en_journal_seulement"].append(nom)
        else:
            out["orphelins"].append(nom)
    return out


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

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        for nom in ("vivant", "souvenu", "oublie", "out"):
            (r / DONNEES / nom).mkdir(parents=True)
        (r / JOURNAUX).mkdir(parents=True)
        (r / "campagne.sh").write_text(f"SOURCE=$PWD/{DONNEES}/vivant lplv rendre\n",
                                       encoding="utf-8")
        (r / JOURNAUX / "hier.log").write_text(f"lu depuis {DONNEES}/souvenu\n",
                                               encoding="utf-8")
        # ⚠⚠ La prose qui contient le MOT « out » sans nommer le chemin : c est le piege
        # exact des noms courts, et il classerait un dossier vivant a tort.
        (r / "prose.md").write_text("le rendu est out of range, on sort\n", encoding="utf-8")

        c = classer(r)
        v("un dossier lancé par un script est vivant", c["vivants"] == ["vivant"], str(c))
        v("... un dossier nommé seulement par un journal est à part",
          c["en_journal_seulement"] == ["souvenu"], str(c))
        v("... et les autres sont orphelins", c["orphelins"] == ["oublie", "out"], str(c))
        # ⚠ Le mot nu ne suffit pas : sans cette regle, `data/out` passerait pour vivant
        # depuis n importe quelle prose contenant « out ».
        v("un mot courant ne rend pas un dossier vivant", "out" in c["orphelins"], str(c))

        (r / "doc.md").write_text(f"voir `{DONNEES}/out/` pour les cartes\n", encoding="utf-8")
        c2 = classer(r)
        v("... mais le chemin complet, si", "out" in c2["vivants"], str(c2))

        # Le poids : chaque inode UNE fois, meme sous deux liens.
        gros = r / DONNEES / "oublie" / "a.bin"
        gros.write_bytes(b"x" * 1000)
        (r / DONNEES / "oublie" / "b.bin").hardlink_to(gros)
        p = poids(r / DONNEES / "oublie")
        v("le poids compte un inode une seule fois", p == 1000, str(p))
        (r / DONNEES / "oublie" / "c.bin").write_bytes(b"y" * 500)
        v("... et additionne les inodes distincts", poids(r / DONNEES / "oublie") == 1500,
          str(poids(r / DONNEES / "oublie")))
        v("un dossier vide pèse zéro", poids(r / DONNEES / "vivant") == 0)

    # ⚠ Sur CE depot : le classement doit couvrir tous les dossiers, sans en perdre ni en
    # inventer. Un classement qui en oublie un le declare implicitement vivant.
    reel = classer(RACINE)
    total = sum(len(x) for x in reel.values())
    v("le classement couvre tout data/", total == len(dossiers(RACINE)),
      f"{total} contre {len(dossiers(RACINE))}")

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Ce que data/ contient et que plus rien ne nomme. N'EFFACE JAMAIS.")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--tout", action="store_true", help="lister aussi les dossiers vivants")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    c = classer()
    base = RACINE / DONNEES

    def bloc(titre, noms, note):
        if not noms:
            return 0
        peses = sorted(((poids(base / n), n) for n in noms), reverse=True)
        somme = sum(x for x, _ in peses)
        print(f"\n{titre} — {len(noms)} dossier(s), {somme / 2**30:.1f} Gio")
        print(f"  {note}")
        for o, n in peses:
            print(f"    {o / 2**30:>8.2f} Gio  {DONNEES}/{n}")
        return somme

    print(f"{DONNEES}/ — {len(dossiers())} dossiers de premier niveau")
    gain = bloc("ORPHELINS", c["orphelins"],
                "aucun script, aucun document ne les nomme")
    gain += bloc("EN JOURNAL SEULEMENT", c["en_journal_seulement"],
                 "un journal se souvient d'eux ; aucun code vivant ne les nomme")
    if a.tout:
        bloc("VIVANTS", c["vivants"], "nommés par un script ou un document")
    else:
        print(f"\n{len(c['vivants'])} dossier(s) vivants, non listés (--tout pour les voir)")
    print(f"\n⚠ {gain / 2**30:.1f} Gio candidats — NOMMÉS, jamais effacés. "
          f"Un dossier que rien ne nomme peut être une entrée qu'on n'a pas encore citée.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
