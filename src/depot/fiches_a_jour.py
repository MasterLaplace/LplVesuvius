#!/usr/bin/env python3
"""La fiche de lecture décrit-elle encore le document qu'elle résume ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `docs/archive/registres/fiches_de_lecture.md` est ce que tout le monde
lit **à la place** des documents — c'est son but, et c'est aussi son danger : une fiche périmée
ne ressemble pas à une fiche périmée, elle ressemble à un résumé. Rien ne la comparait à sa
source, donc elle pouvait décrire un document qui avait changé de trente-cinq lignes sans que
quoi que ce soit le dise.

⭐⭐ CE QUE CE CONTRÔLE PEUT ET NE PEUT PAS FAIRE, dit d'emblée. Il compare le **compte de
lignes** enregistré au compte réel : c'est un **indice**, pas une preuve. Un document peut
changer de sens sans changer de taille, et gagner une ligne sans rien changer du tout. Ce qu'il
attrape est la classe la plus fréquente ici — une section ajoutée, une correction insérée, un
tableau étendu — après quoi c'est à un humain de relire.

⚠ C'est pourquoi `--corriger` ne touche QUE le nombre. Le résumé et les conclusions sont un
jugement ; les réécrire mécaniquement produirait une fiche qui a l'air à jour et ne l'est pas,
c'est-à-dire exactement la panne que ce fichier existe pour rendre visible. Le nombre corrigé
sans relecture reste un mensonge plus petit, donc `--corriger` **nomme** les fiches à relire.

Usage :
    uv run python src/depot/fiches_a_jour.py
    uv run python src/depot/fiches_a_jour.py --corriger
    uv run python src/depot/fiches_a_jour.py --verifier
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
REGISTRE = RACINE / "docs" / "archive" / "registres" / "fiches_de_lecture.md"

# ⚠ Ancré sur le début de ligne ET sur l'enchaînement titre → ligne de compte : un `### docs/…`
# cité au fil d'une phrase ne porte pas ce champ, et un `- **lignes**` isolé n'appartient à
# aucune fiche. Les deux ensemble ne peuvent désigner qu'une entrée de registre.
#
# ⚠⚠ ET LA QUEUE DE LIGNE EST CAPTURÉE, PAS EXIGÉE VIDE. Ma première version fermait sur `$`
# juste après le nombre : les **dix** fiches qui portent une remarque derrière lui — « ⚠ (438
# quand la fiche a été écrite …) », « (mesuré) » — étaient invisibles au contrôle, donc les
# seules fiches dont on savait déjà qu'elles avaient bougé étaient précisément celles qu'il ne
# regardait pas. Un contrôle aveugle à sa population la plus à risque ne contrôle rien.
#
# ⚠ Cette queue est de l'HISTOIRE (ce que valait le compte quand la fiche a été écrite, et ce
# qui l'a fait bouger). `--corriger` ne réécrit que le nombre et la recopie telle quelle.
#
# ⚠⚠⚠ ET LA LIGNE VIDE ENTRE LES DEUX EST TOLÉRÉE — mesuré le 2026-09-05 : **sept** fiches
# (43 à 49, écrites d'un même lot) séparent leur titre de leur compte par une ligne vide, et
# elles étaient donc **invisibles au contrôle**. Pas « en dérive » : invisibles. `48` annonçait
# 342 lignes pour un document qui en faisait 405 et le registre disait « 0 en dérive ».
#
#   ⭐ Un garde-fou ne doit pas dépendre d'un blanc. Le séparateur est CAPTURÉ et recopié tel
#     quel par `--corriger`, plutôt que normalisé : réécrire la mise en page de sept fiches
#     pour satisfaire une regex serait faire changer les données par le contrôle.
#
# ⚠ Au plus UNE ligne vide : en accepter davantage laisserait un `### …md` cité au fil d'une
# phrase s'apparier avec le compte d'une fiche située plus bas.
ENTREE = re.compile(r"^### (\S+\.md)\n(\n?)- \*\*lignes\*\* : (\d+)(.*)$", re.M)


def lignes_reelles(chemin: Path) -> int | None:
    """
    @brief Le compte de lignes du document, ou None s'il n'existe plus.

    ⚠ `splitlines()` et non `count("\\n")` : un fichier dont la dernière ligne n'a pas de retour
    chariot en perdrait une, et l'écart de un se lirait comme une dérive réelle.
    """
    if not chemin.is_file():
        return None
    return len(chemin.read_text(encoding="utf-8").splitlines())


def auditer(texte: str, racine: Path) -> list[dict]:
    """
    @brief Chaque fiche, son compte enregistré, et le compte réel de sa source.

    ⚠ Rend TOUTES les fiches, y compris celles qui s'accordent : un appelant qui ne recevrait
    que les dérives ne pourrait pas dire « zéro dérive » de « zéro fiche lue », et ce dépôt a
    déjà payé cette confusion (une panne totale qui ressemble à une population vide).
    """
    out = []
    for chemin, blanc, note, queue in ENTREE.findall(texte):
        reel = lignes_reelles(racine / chemin)
        out.append(dict(chemin=chemin, note=int(note), reel=reel, queue=queue, blanc=blanc,
                        ecart=None if reel is None else reel - int(note)))
    return out


TITRE = re.compile(r"^### (\S+\.md)$", re.M)


def sans_fiche(texte: str, racine: Path) -> list[str]:
    """
    @brief Les documents de `docs/` que le registre ne résume pas du tout.

    ⚠⚠⚠ LE POINT AVEUGLE SYMÉTRIQUE, et il valait dix documents. Ce fichier comparait chaque
    fiche à sa source et rapportait « 63 fiches, 0 en dérive » — parfaitement vrai, et
    parfaitement muet sur le fait que **les dix documents les plus récents n'avaient aucune
    fiche**. Un registre qu'on lit à la place des documents doit dire ce qu'il ne couvre pas,
    sinon son silence se lit comme une couverture complète.

    ⚠ `docs/archive/*.md` seulement, sans les sous-dossiers : `registres/` contient le registre
    lui-même. Depuis le 2026-09-11 les documents numérotés vivent là, gelés, et les rapports
    de `docs/rapports/` ne sont pas fichés : le registre est aussi gelé que ce qu'il décrit.
    """
    fiches = set(TITRE.findall(texte))
    return [str(q.relative_to(racine)) for q in sorted((racine / "docs" / "archive").glob("*.md"))
            if str(q.relative_to(racine)) not in fiches]


def corriger(texte: str, audit: list[dict]) -> tuple[str, int]:
    """
    @brief Réécrit les comptes qui ont dérivé — et **rien d'autre**.

    ⚠⚠ Le remplacement est ancré sur le couple (titre, ligne de compte) et non sur le nombre
    seul : le même nombre apparaît des dizaines de fois ailleurs dans le registre, et un
    remplacement global irait le changer dans une conclusion mesurée.
    """
    corrigees = 0
    for e in audit:
        if e["reel"] is None or e["ecart"] == 0:
            continue
        blanc = e.get("blanc", "")
        avant = f"### {e['chemin']}\n{blanc}- **lignes** : {e['note']}{e['queue']}"
        apres = f"### {e['chemin']}\n{blanc}- **lignes** : {e['reel']}{e['queue']}"
        if avant in texte:
            texte = texte.replace(avant, apres, 1)
            corrigees += 1
    return texte, corrigees


def _verifier() -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "docs" / "archive").mkdir(parents=True)
        (d / "docs" / "archive" / "a.md").write_text("un\ndeux\ntrois\n", encoding="utf-8")
        (d / "docs" / "archive" / "b.md").write_text("seule\n", encoding="utf-8")
        registre = ("### docs/archive/a.md\n- **lignes** : 3\n- **nature** : X\n\n"
                    "### docs/archive/b.md\n- **lignes** : 9\n- **nature** : Y\n\n"
                    "### docs/archive/parti.md\n- **lignes** : 4\n")
        audit = auditer(registre, d)
        v("les trois fiches sont lues, pas seulement celles qui dérivent",
          len(audit) == 3, str(len(audit)))
        v("une fiche à jour a un écart nul",
          [e for e in audit if e["chemin"] == "docs/archive/a.md"][0]["ecart"] == 0)
        v("... une fiche périmée porte son écart signé",
          [e for e in audit if e["chemin"] == "docs/archive/b.md"][0]["ecart"] == -8)
        # ⚠⚠ « Le document a disparu » et « la fiche est périmée » sont DEUX faits, et les
        # confondre ferait corriger un compte vers zéro sur un fichier absent.
        v("... et un document disparu n'est pas une dérive mais une absence",
          [e for e in audit if e["chemin"] == "docs/archive/parti.md"][0]["reel"] is None)

        # ⚠⚠ ET LE POINT AVEUGLE SYMÉTRIQUE : un document sans fiche du tout. Le registre se
        # lit À LA PLACE des documents, donc son silence sur dix d'entre eux se lisait comme
        # une couverture complète.
        (d / "docs" / "archive" / "jamais_lu.md").write_text("x\n", encoding="utf-8")
        v("un document sans fiche est nommé",
          sans_fiche(registre, d) == ["docs/archive/jamais_lu.md"], str(sans_fiche(registre, d)))
        v("... et un document qui EN a une ne l'est pas",
          "docs/archive/a.md" not in sans_fiche(registre, d))
        # ⚠ Un titre suivi d'autre chose que la fin de ligne n'est pas une entrée de registre :
        # sans l'ancrage, une mention en prose ferait passer un document pour résumé.
        v("... et une mention en prose ne compte pas comme une fiche",
          "docs/archive/jamais_lu.md" in sans_fiche(registre + "voir ### docs/archive/jamais_lu.md ici\n", d))
        (d / "docs" / "archive" / "jamais_lu.md").unlink()

        # ⚠⚠⚠ LA FICHE À LIGNE VIDE, et c'est le point aveugle qui valait sept fiches. Le
        # registre sépare parfois le titre de son compte par une ligne vide (43 à 49, écrites
        # d'un même lot) : la version précédente exigeait l'enchaînement immédiat, donc ces
        # sept-là n'étaient pas « en dérive », elles étaient INVISIBLES — et trois d'entre
        # elles dérivaient réellement, dont `48` de soixante-trois lignes.
        aere = ("### docs/archive/a.md\n\n- **lignes** : 3\n- **nature** : X\n\n"
                "### docs/archive/b.md\n\n- **lignes** : 9\n")
        audit_aere = auditer(aere, d)
        v("une fiche dont le compte est séparé par une LIGNE VIDE est vue",
          len(audit_aere) == 2, str(len(audit_aere)))
        v("... et sa dérive est mesurée comme les autres",
          [e for e in audit_aere if e["chemin"] == "docs/archive/b.md"][0]["ecart"] == -8)
        # ⚠ Le séparateur est RECOPIÉ : sans ça l'ancrage écrit n'existerait pas dans le texte
        # et `--corriger` ne corrigerait rien, en silence.
        recolle_aere, n_aere = corriger(aere, audit_aere)
        v("... et --corriger la répare en gardant sa ligne vide",
          n_aere == 1 and "### docs/archive/b.md\n\n- **lignes** : 1\n" in recolle_aere,
          repr(recolle_aere[-40:]))
        # ⚠⚠ Au plus UNE ligne vide : au-delà, un `### …md` cité en prose pourrait s'apparier
        # avec le compte d'une fiche située plus bas, et le contrôle attribuerait une dérive
        # au mauvais document.
        v("... mais DEUX lignes vides ne s'apparient pas",
          auditer("### docs/archive/a.md\n\n\n- **lignes** : 3\n", d) == [])

        neuf, n = corriger(registre, audit)
        v("--corriger ne touche que les comptes qui ont dérivé", n == 1, str(n))
        v("... et il écrit le bon", "### docs/archive/b.md\n- **lignes** : 1" in neuf)
        v("... sans toucher la fiche à jour", "### docs/archive/a.md\n- **lignes** : 3" in neuf)
        v("... ni celle dont le document a disparu",
          "### docs/archive/parti.md\n- **lignes** : 4" in neuf)
        # ⚠⚠⚠ LE CONTRÔLE QUI COMPTE, ET SA PREMIÈRE VERSION NE DISCRIMINAIT RIEN. Le même
        # nombre existe ailleurs dans le registre ; un remplacement non ancré irait le changer
        # dans une conclusion mesurée. Ma fixture d'abord écrite plaçait la prose APRÈS la ligne
        # de compte, donc un `replace(str(note), str(reel), 1)` consommait la bonne occurrence
        # et la prose survivait — la sonde passait au vert sur le code saboté.
        #
        # ⚠⚠ Le remède n'est pas une fixture plus rusée mais un INVARIANT DE STRUCTURE : hors
        # des lignes de compte, le registre doit sortir **identique**. Aucun sabotage du
        # remplacement ne peut satisfaire ça, et il n'y a pas de piège à deviner.
        piege = ("### docs/archive/a.md\n- **lignes** : 3\n"
                 "- **conclusions** :\n  - le seuil vaut 9 segments sur 9.\n\n"
                 "### docs/archive/b.md\n- **lignes** : 9\n- **nature** : 9 pages\n")
        recolle, _ = corriger(piege, auditer(piege, d))
        def hors_compte(t):
            return [l for l in t.splitlines() if not l.startswith("- **lignes** : ")]
        v("hors des lignes de compte, le registre sort IDENTIQUE",
          hors_compte(recolle) == hors_compte(piege),
          " | ".join(hors_compte(recolle)))
        v("... et la ligne de compte, elle, est bien réécrite",
          "- **lignes** : 1" in recolle, recolle.replace("\n", " | "))
        # ⚠⚠ LA QUEUE EST DE L'HISTOIRE ET ELLE SURVIT. Dix fiches du registre portent derrière
        # leur nombre ce qu'il valait quand la fiche a été écrite et ce qui l'a fait bouger ;
        # une correction qui l'effacerait remplacerait une trace par un chiffre.
        avec = ("### docs/archive/b.md\n- **lignes** : 9 ⚠ (7 quand la fiche a été écrite)\n")
        garde, _ = corriger(avec, auditer(avec, d))
        v("... et la remarque derrière le nombre est recopiée telle quelle",
          garde == "### docs/archive/b.md\n- **lignes** : 1 ⚠ (7 quand la fiche a été écrite)\n",
          garde.replace("\n", " | "))
        v("... et une fiche à queue est bien LUE (elle échappait au contrôle)",
          [e["chemin"] for e in auditer(avec, d)] == ["docs/archive/b.md"])
        # ⚠ La ligne de compte doit suivre IMMÉDIATEMENT le titre : un `- **lignes**` orphelin
        # n'appartient à aucune fiche, et le compter en inventerait une.
        # ⚠⚠ La fixture d'un titre « cité au fil d'une phrase » ne discriminait pas non plus :
        # sans ligne de compte derrière lui, même un motif laxiste rendait []. Il faut une
        # mention EN PROSE suivie, plus loin, d'une VRAIE fiche — un motif non ancré rattache
        # alors le compte de la seconde au nom de la première.
        v("un compte sans titre au-dessus n'est pas une fiche",
          auditer("- **lignes** : 12\n", d) == [])
        melange = auditer("voir docs/archive/a.md plus haut\n\n### docs/archive/b.md\n- **lignes** : 9\n", d)
        v("... et une mention en prose ne capte pas le compte de la fiche suivante",
          [e["chemin"] for e in melange] == ["docs/archive/b.md"],
          str([e["chemin"] for e in melange]))

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--corriger", action="store_true",
                   help="réécrire les comptes de lignes qui ont dérivé")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return 1 if _verifier() else 0

    texte = REGISTRE.read_text(encoding="utf-8")
    audit = auditer(texte, RACINE)
    orphelins = sans_fiche(texte, RACINE)
    derives = [e for e in audit if e["ecart"] not in (0, None)]
    absents = [e for e in audit if e["reel"] is None]
    for e in absents:
        print(f"  ABSENT   {e['chemin']}   (fiche : {e['note']} lignes)")
    for e in sorted(derives, key=lambda x: -abs(x["ecart"])):
        print(f"  {e['chemin']:56s} fiche {e['note']:>5d}  réel {e['reel']:>5d}  "
              f"écart {e['ecart']:+d}")
    for q in orphelins:
        print(f"  SANS FICHE  {q}")
    print(f"\n{len(audit)} fiche(s), {len(derives)} en dérive, {len(absents)} absente(s), "
          f"{len(orphelins)} document(s) sans fiche")

    if a.corriger and derives:
        neuf, n = corriger(texte, audit)
        REGISTRE.write_text(neuf, encoding="utf-8")
        print(f"\n{n} compte(s) corrigé(s) dans {REGISTRE}")
        # ⚠⚠ NOMMÉES, parce que corriger le nombre ne relit pas le document. Une fiche dont la
        # source a bougé de plusieurs sections peut porter un résumé faux avec un compte juste,
        # ce qui est pire qu'avant : le seul signal visible a disparu.
        print("  ⚠ à RELIRE — le compte est corrigé, le résumé ne l'est pas :")
        for e in sorted(derives, key=lambda x: -abs(x["ecart"])):
            print(f"      {e['chemin']}   ({e['ecart']:+d} lignes)")
        return 0
    return 1 if (derives or absents or orphelins) else 0


if __name__ == "__main__":
    sys.exit(main())
