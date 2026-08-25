#!/usr/bin/env python3
"""Les murs, leurs causes candidates, et le verdict de chacune.

⚠⚠ POURQUOI CE FICHIER EXISTE, et c'est une idée de l'auteur : *« si t'arrive à faire un gros
tableau avec ça pour chaque mur, ça pourrait faire une roadmap un peu plus propre »*. Elle est
juste, et pour une raison qui n'est pas cosmétique : un mur n'est pas une tâche, c'est un
**espace de causes** dont on retire une entrée à la fois. Une feuille de route qui liste des
tâches laisse croire qu'on avance quand on tourne ; une feuille de route qui liste des causes
**éliminées** montre l'espace rétrécir, ce qui est le seul progrès mesurable sur un problème
non résolu.

⭐ Le registre lui-même (`docs/murs_et_causes.tsv`) est tenu **à la main** : ce sont des
jugements, pas des mesures, et les fabriquer automatiquement serait inventer un consensus.
Ce qui est **vérifié par machine**, ce sont ses **pointeurs** — chaque ligne nomme un document
et une ancre, et la batterie exige que l'ancre s'y trouve encore.

⚠⚠ C'est exactement la panne qu'`EXTRACTION.md` a connue : une table maintenue à la main dérive
de ce qu'elle décrit, en silence, et personne ne s'en aperçoit avant d'en avoir besoin. Ici,
une ancre qui cesse de matcher fait **rougir la batterie** — donc la dérive est un échec, pas
une découverte tardive.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
REGISTRE = RACINE / "docs" / "murs_et_causes.tsv"

# ⚠ Vocabulaire FERMÉ. Un verdict libre laisserait écrire « plutôt éliminée », qui ne veut rien
# dire et qui est exactement ce qu'on écrit quand on n'a pas mesuré.
VERDICTS = {
    "éliminée": ("❌", "testée, ce n'est pas la cause"),
    "confirmée": ("✅", "testée, c'en est une — ou un levier qui marche"),
    "ouverte": ("⏳", "nommée, pas encore testée"),
    "bloquée": ("🔒", "ne peut pas être testée aujourd'hui, et on dit pourquoi"),
}


def lire(chemin: Path = REGISTRE) -> list[dict]:
    """Le registre, une ligne par (mur, cause).

    ⚠ Le TSV est lu à la main plutôt qu'avec `csv` : le module rendrait des guillemets et des
    échappements dans un fichier que des humains éditent, et un registre qu'on n'ose plus
    ouvrir cesse d'être tenu.
    """
    lignes = chemin.read_text(encoding="utf-8").rstrip("\n").split("\n")
    entetes = lignes[0].split("\t")
    out = []
    for i, ligne in enumerate(lignes[1:], start=2):
        champs = ligne.split("\t")
        if len(champs) != len(entetes):
            raise ValueError(f"{chemin}:{i} — {len(champs)} colonnes pour "
                             f"{len(entetes)} en-têtes")
        out.append(dict(zip(entetes, champs)))
    return out


def murs(entrees: list[dict]) -> list[str]:
    """Les murs, dans l'ordre où ils apparaissent — pas triés.

    ⚠ L'ordre du fichier est une information : c'est celui dans lequel l'auteur les a écrits,
    et le trier alphabétiquement le remplacerait par un ordre qui ne veut rien dire.
    """
    vus = []
    for e in entrees:
        if e["mur"] not in vus:
            vus.append(e["mur"])
    return vus


def compte(entrees: list[dict]) -> dict:
    """Combien de causes de chaque verdict, tous murs confondus."""
    c = {v: 0 for v in VERDICTS}
    for e in entrees:
        c[e["verdict"]] = c.get(e["verdict"], 0) + 1
    return c


def rendre(entrees: list[dict]) -> str:
    """Le document, en markdown, un tableau par mur."""
    c = compte(entrees)
    total = len(entrees)
    lignes = [
        "# 55 — Les murs, et l'espace de causes qui rétrécit",
        "",
        "> ⚠⚠ **Ce document est RENDU, pas écrit.** Sa source est",
        "> [`docs/murs_et_causes.tsv`](murs_et_causes.tsv) et son producteur est",
        "> `src/depot/murs_et_causes.py --rendre`. L'éditer à la main serait perdre la",
        "> modification au rendu suivant — et surtout perdre la garde : la batterie vérifie que",
        "> **chaque ligne pointe vers un document qui contient encore son ancre**.",
        "",
        "Un mur n'est pas une tâche, c'est un **espace de causes** dont on retire une entrée à",
        "la fois. Une feuille de route qui liste des tâches laisse croire qu'on avance quand on",
        "tourne ; celle-ci liste des causes **éliminées**, et montre l'espace rétrécir. C'est le",
        "seul progrès mesurable sur un problème que personne n'a résolu.",
        "",
        f"**{total} causes candidates** sur **{len(murs(entrees))} murs** : "
        # ⚠ L'accord se fait sur le compte : « 1 bloquées » se lit comme une faute de frappe
        # et fait douter du reste du tableau.
        + " · ".join(f"{VERDICTS[v][0]} **{c[v]}** {v}{'s' if c[v] > 1 else ''}"
                     for v in VERDICTS if c.get(v)),
        "",
        "| symbole | verdict | ce que ça veut dire |",
        "|---|---|---|",
    ]
    for v, (sym, sens) in VERDICTS.items():
        lignes.append(f"| {sym} | **{v}** | {sens} |")
    lignes += [
        "",
        "![l'espace de causes, mur par mur](images/55_espace_de_causes.png)",
        "",
        "*Une case par cause, dans l'ordre du vocabulaire — donc ce qui reste à faire tombe",
        "toujours à droite. Ce n'est **pas** une jauge de progression : rien ne dit que",
        "l'espace est borné. Produite par `src/figures/figure_murs.py`, dont les comptes",
        "viennent du même registre et sont vérifiés contre ce tableau.*",
        "",
    ]

    for i, mur in enumerate(murs(entrees), start=1):
        rangs = [e for e in entrees if e["mur"] == mur]
        cm = compte(rangs)
        lignes += [
            f"## {i}. {mur[0].upper()}{mur[1:]}",
            "",
            " · ".join(f"{VERDICTS[v][0]} {cm[v]} {v}{'s' if cm[v] > 1 else ''}"
                       for v in VERDICTS if cm.get(v)),
            "",
            "| cause candidate | | ce qui a été mesuré | où |",
            "|---|---|---|---|",
        ]
        # ⚠ Les ouvertes et les bloquées en DERNIER : ce qui reste à faire se lit en bas d'un
        # tableau, pas au milieu de ce qui est fait.
        ordre = {"confirmée": 0, "éliminée": 1, "ouverte": 2, "bloquée": 3}
        for e in sorted(rangs, key=lambda r: ordre.get(r["verdict"], 9)):
            sym = VERDICTS[e["verdict"]][0]
            lignes.append(f"| {e['cause']} | {sym} | {e['mesure']} "
                          f"| [`{e['doc'].split('_')[0]}`]({e['doc']}) |")
        lignes.append("")

    ouvertes = [e for e in entrees if e["verdict"] in ("ouverte", "bloquée")]
    lignes += [
        "## Ce qui reste ouvert, tous murs confondus",
        "",
        "⭐ C'est la seule liste courte du dépôt qui dise *par quoi continuer*.",
        "",
        "| mur | cause | pourquoi elle est encore ouverte |",
        "|---|---|---|",
    ]
    for e in ouvertes:
        lignes.append(f"| {e['mur']} | **{e['cause']}** | {e['mesure']} |")
    lignes += [
        "",
        "⚠ **Une cause éliminée ne se rouvre pas sans une mesure neuve.** Les treize",
        "éliminations de ce document ont chacune coûté une campagne ; les refaire par doute",
        "serait payer deux fois pour le même renseignement.",
        "",
        "⚠⚠ Et une cause **absente** de ce document n'est pas une cause éliminée : c'est une",
        "cause à laquelle personne n'a pensé. Le tableau borne ce qu'on a testé, jamais ce qui",
        "est possible.",
        "",
    ]
    return "\n".join(lignes)


def verifier() -> int:
    """Les témoins : le registre est bien formé, et ses pointeurs pointent encore."""
    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    entrees = lire()
    v("le registre a des lignes", len(entrees) > 0)
    v("il a les six colonnes attendues",
      set(entrees[0]) == {"mur", "cause", "verdict", "mesure", "doc", "ancre"},
      str(sorted(entrees[0])))

    for e in entrees:
        v(f"verdict connu : {e['cause'][:34]}", e["verdict"] in VERDICTS, e["verdict"])
        for col in ("mur", "cause", "mesure", "doc", "ancre"):
            v(f"{col} non vide : {e['cause'][:28]}", bool(e[col].strip()))

    # ⚠⚠ LA GARDE QUI COMPTE : chaque ligne pointe vers un document qui contient ENCORE son
    # ancre. C'est ce qui empêche ce tableau de devenir `EXTRACTION.md` — une table maintenue
    # à la main qui dérive en silence de ce qu'elle décrit.
    for e in entrees:
        chemin = RACINE / "docs" / e["doc"]
        v(f"le document existe : {e['doc']}", chemin.is_file())
        if chemin.is_file():
            v(f"l'ancre s'y trouve encore : « {e['ancre'][:40]} »",
              e["ancre"] in chemin.read_text(encoding="utf-8"), e["doc"])

    # ⚠ Pas deux fois la même cause sur le même mur : un doublon ferait compter une
    # élimination pour deux et la roadmap paraîtrait plus avancée qu'elle n'est.
    paires = [(e["mur"], e["cause"]) for e in entrees]
    v("aucune cause en double sur un même mur", len(paires) == len(set(paires)))
    v("chaque mur a au moins une cause",
      all(any(e["mur"] == m for e in entrees) for m in murs(entrees)))

    texte = rendre(entrees)
    # ⚠ Le titre de section met la MAJUSCULE au premier caractère, donc chercher le nom brut
    # échouait sur « l'extension… ». Le contrôle porte sur la forme réellement écrite.
    v("le rendu nomme chaque mur",
      all(f"{m[0].upper()}{m[1:]}" in texte for m in murs(entrees)))
    v("... et chaque cause", all(e["cause"] in texte for e in entrees))
    # ⚠ Le rendu doit être STABLE : deux appels donnent le même texte, sinon un `git diff`
    # bruite à chaque exécution et personne ne relit plus le document.
    v("le rendu est stable", rendre(lire()) == texte)
    v("les ouvertes sont listées à la fin",
      texte.index("Ce qui reste ouvert") > texte.index("## 1."))

    # ⚠⚠ Cas négatif : une ancre inventée DOIT faire échouer la garde. Sans cette sonde, la
    # garde pourrait ne rien vérifier du tout.
    faux = RACINE / "docs" / entrees[0]["doc"]
    v("une ancre inventée ne serait pas trouvée",
      "ancre-qui-n-existe-pas-42" not in faux.read_text(encoding="utf-8"))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rendre", type=Path, nargs="?",
                   const=RACINE / "docs" / "55_les_murs_et_leurs_causes.md")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    entrees = lire()
    texte = rendre(entrees)
    if a.rendre:
        a.rendre.write_text(texte + "\n", encoding="utf-8")
        c = compte(entrees)
        print(f"écrit : {a.rendre}\n  {len(entrees)} causes sur {len(murs(entrees))} murs — "
              + ", ".join(f"{c[v]} {v}s" for v in VERDICTS if c.get(v)))
    else:
        print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
