#!/usr/bin/env python3
"""Combien de spires une seule surface publiee traverse-t-elle ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA VERITE DE TERRAIN DU GOULOT. L'objectif est de
derouler automatiquement, et son goulot est le **transfert de spire a spire** — ce que l'etat de
l'art paie ~25 h d'humain par spire. Une surface publiee qui ne couvre qu'UNE spire ne contient
donc aucun transfert : elle donne la reponse en morceaux deja separes, jamais un franchissement.
Une surface qui en couvre dix-huit en contient **dix-sept**.

⭐⭐⭐ MESURE : `PHercParis4` est le SEUL objet du corpus publie dont les surfaces traversent plus
d'une spire. Ses 120 spires sont publiees en **28 bandes** — `w010-027`, `w028-037`, …,
`w128-129` — soit **92 franchissements de spire contenus dans une seule maille**. `PHerc0172`
(44 spires), `PHerc0139` (37), `PHerc1667` (19), `PHerc0500P2` (13) et `PHercMANBp` (9) publient
**une spire par surface, sans exception**, donc **zero** franchissement.

⭐⭐ ET LA LONGUEUR DES BANDES DECROIT AVEC LE RANG, sans une seule inversion : 18, 10, 8, 7, 6,
5, 5, puis des 4, des 3 et des 2. Une bande est ce qu'une passe humaine a produit d'un coup, donc
cette suite est la courbe de cout du deroulage manuel, lue sans rien mesurer soi-meme.
⚠ Ce que la suite ne dit PAS : dans quel sens va le rang. La circonference croit vers l'exterieur,
donc une passe d'effort constant y couvre moins de spires — ce qui expliquerait la decroissance —
mais rien ici ne l'etablit, et l'ecrire comme un fait serait une lecture, pas une mesure.

⚠ Ce fichier ne remesure rien et ne telecharge rien : il relit l'index cache et compte. Il partage
son lecteur de rangs avec `les_spires_consecutives_publiees` — deux lecteurs de la meme convention
de nommage finiraient par ne pas s'accorder sur ce qu'est une bande.

Usage :
    uv run python src/depot/une_surface_combien_de_spires.py
    uv run python src/depot/une_surface_combien_de_spires.py --verifier
    uv run python src/depot/une_surface_combien_de_spires.py \\
        --json docs/mesures/une_surface_combien_de_spires.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "depot"))

# ⚠ LE LECTEUR DE RANGS EST PARTAGE, jamais recopie : `les_spires_consecutives_publiees` porte
# deja la regle (un intervalle se deplie, un nombre isole n'est pas un rang) et ses sondes.
from les_spires_consecutives_publiees import (  # noqa: E402
    INDEX, charger_index, les_treize, rangs_du_suffixe,
)

SPIRES_DU_PRIX = 31


def bandes(echantillon: dict) -> dict:
    """Les bandes distinctes publiees, chacune avec ses revisions.

    Une **bande** est l'intervalle de spires qu'une surface couvre. Deux segments qui couvrent le
    meme intervalle sont deux revisions d'une meme bande, pas deux bandes : les compter deux fois
    doublerait le corpus de `PHercParis4` sans qu'une seule spire de plus soit publiee.

    ⚠⚠ LA BANDE EST LUE PAR LE LECTEUR PARTAGE, PAS PAR UN PREFIXE. Ma premiere version exigeait
    que le nom COMMENCE par la bande, pour ecarter un `w4` glisse dans un commentaire de
    revision — et elle a silencieusement efface `PHerc0500P2`, dont les surfaces s'appellent
    `0500P2-wrap01_0919`. C'est le controle « l'objet courant publie une spire par surface » qui
    l'a dit, en levant sur une clef absente. Le risque du faux positif est deja tenu par le
    lecteur partage et ses sondes : un rang se nomme par `w`/`wrap`, jamais par un nombre isole.

    ⚠ Un nom qui mentionnerait deux fois une spire donne UNE bande, du plus petit au plus grand
    rang — ce qui est exactement ce qu'une bande veut dire.
    """
    out: dict[tuple[int, int], list[str]] = {}
    for seg in echantillon.get("segments", {}).values():
        sx = seg.get("suffix", "")
        r = rangs_du_suffixe(sx)
        if not r:
            continue
        out.setdefault((min(r), max(r)), []).append(sx)
    return out


def decroissance(spans: list[int]) -> dict:
    """Combien de fois la longueur des bandes REMONTE quand on avance dans les rangs.

    ⭐ Zero inversion sur vingt-huit bandes n'est pas une tendance, c'est une monotonie — et une
    monotonie se refute d'une seule inversion, donc elle se mesure plutot qu'elle ne s'affirme.
    """
    inversions = sum(1 for a, b in zip(spans, spans[1:]) if b > a)
    return {"bandes": len(spans), "inversions": inversions,
            "monotone": inversions == 0 and len(spans) > 2,
            "du_premier_au_dernier": [spans[0], spans[-1]] if spans else []}


def mesurer(chemin: Path = INDEX) -> dict:
    """Comment chaque objet EMPAQUETTE ses spires, et combien de franchissements il publie."""
    ech = charger_index(chemin)
    treize = set(les_treize())
    lignes = []
    for nom, e in ech.items():
        b = bandes(e)
        if not b:
            continue
        spans = [hi - lo + 1 for (lo, hi) in sorted(b)]
        couvertes = len({r for lo, hi in b for r in range(lo, hi + 1)})
        # ⚠⚠ LES BORNES DE RANG, PARCE QU'UN AXE RELATIF MENT. Le corpus de `PHercParis4`
        # commence a la dixieme spire, pas a la premiere : dessiner ses bandes sur un axe qui
        # part de zero ferait lire un corpus qui commence au coeur.
        borne_basse = min(lo for lo, _ in b)
        borne_haute = max(hi for _, hi in b)
        lignes.append({
            "nom": nom,
            "du_prix": nom in treize,
            "bandes": len(b),
            "spires_couvertes": couvertes,
            "spires_par_surface": round(couvertes / len(b), 2),
            "bande_la_plus_longue": max(spans),
            # ⭐⭐ LA GRANDEUR QUI COMPTE POUR L'OBJECTIF : un franchissement contenu dans une
            # seule maille est une verite de terrain du transfert de spire a spire. Une surface
            # d'une seule spire n'en contient aucun, quel que soit le nombre de surfaces.
            "franchissements_dans_une_maille": sum(s - 1 for s in spans),
            "revisions": sum(len(v) for v in b.values()),
            "bornes": [borne_basse, borne_haute],
            # ⚠ Les bandes PAVENT-elles l'intervalle, ou laissent-elles un trou ? Le compte de
            # spires couvertes ne le dit pas : douze bandes peuvent couvrir douze spires en
            # sautant deux rangs. Le trou est publie plutot qu'a deduire.
            "trous": borne_haute - borne_basse + 1 - couvertes,
            "spans": spans,
            "decroissance": decroissance(spans),
        })
    lignes.sort(key=lambda r: (-r["franchissements_dans_une_maille"], -r["spires_couvertes"]))
    porteurs = [r["nom"] for r in lignes if r["franchissements_dans_une_maille"] > 0]
    return {
        "index": str(chemin.relative_to(RACINE)),
        "spires_du_prix": SPIRES_DU_PRIX,
        "objets_avec_bandes": len(lignes),
        "lignes": lignes,
        "objets_qui_publient_un_franchissement": porteurs,
        "objets_a_une_spire_par_surface": [r["nom"] for r in lignes
                                           if r["bande_la_plus_longue"] == 1],
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mécanique, sur des noms fabriqués -------------------------------------------------
    faux = {"segments": {
        "1": {"suffix": "w010-027"}, "2": {"suffix": "w010-027"},
        "3": {"suffix": "w028-037"}, "4": {"suffix": "w040_2026013015_flatboi"},
        "5": {"suffix": "auto_grown_20251115002740308_5_flatboi"},
        # ⚠ Le nom PREFIXE du fragment, qui a fait disparaître `PHerc0500P2` en silence.
        "6": {"suffix": "0500P2-wrap07_0919"}}}
    b = bandes(faux)
    # ⚠⚠ DEUX REVISIONS D'UNE MEME BANDE NE SONT PAS DEUX BANDES : les compter deux fois
    # doublerait un corpus sans qu'une spire de plus soit publiée.
    v("deux révisions d'une même bande n'en font qu'une", len(b) == 4, str(sorted(b)))
    # ⚠⚠ UN NOM PREFIXE DU FRAGMENT OUVRE SA BANDE : c'est l'oubli qui a effacé l'objet courant.
    v("un nom préfixé du fragment ouvre quand même sa bande", (7, 7) in b, str(sorted(b)))
    v("... et les révisions sont gardées", len(b[(10, 27)]) == 2, str(b.get((10, 27))))
    v("une bande d'une seule spire est une bande", (40, 40) in b, str(sorted(b)))
    # ⚠ Le faux positif du dépôt : un indice de morceau n'est pas un rang.
    v("un auto_grown n'ouvre aucune bande", (5, 5) not in b, str(sorted(b)))

    v("la décroissance compte les remontées", decroissance([5, 4, 4, 6, 2])["inversions"] == 1)
    v("... et une suite décroissante est monotone", decroissance([5, 4, 3])["monotone"])
    # ⚠ Deux points ne font pas une monotonie : une suite trop courte ne peut pas la refuser.
    v("... mais deux points ne suffisent pas à l'affirmer",
      not decroissance([5, 4])["monotone"])

    r = mesurer()
    par = {x["nom"]: x for x in r["lignes"]}

    # ⚠⚠ UNE BATTERIE QUI LEVE NE DIT PAS COMBIEN DE CONTROLES ONT TOURNE. Les deux sondes de
    # cette tranche ont fait disparaitre un objet de la mesure, et la batterie est morte sur une
    # clef absente au lieu de rapporter un echec — donc tous les controles suivants n'ont pas eu
    # lieu, sans que le compte le dise. Un objet manquant est un ECHEC NOMME, pas une exception.
    def ligne(nom):
        if nom in par:
            return par[nom]
        v(f"l'objet {nom} est dans la mesure", False, "absent de l'index lu")
        return {"bandes": -1, "spires_couvertes": -1, "bande_la_plus_longue": -1,
                "franchissements_dans_une_maille": -1, "spans": [],
                "decroissance": {"monotone": False, "du_premier_au_dernier": []}}

    # --- le verdict sur le dépôt réel --------------------------------------------------------
    # ⭐⭐⭐ UN SEUL OBJET PUBLIE UN FRANCHISSEMENT, et c'est ce que l'objectif doit reproduire.
    v("un seul objet publie des franchissements dans une maille",
      r["objets_qui_publient_un_franchissement"] == ["PHercParis4"],
      str(r["objets_qui_publient_un_franchissement"]))
    v("... et il en publie 92, en 28 bandes",
      (ligne("PHercParis4")["franchissements_dans_une_maille"],
       ligne("PHercParis4")["bandes"]) == (92, 28), str(ligne("PHercParis4")))
    v("... pour 120 spires couvertes", ligne("PHercParis4")["spires_couvertes"] == 120)
    # ⚠ L'identité qui rend le compte lisible : franchissements = couvertes − bandes.
    # ⚠⚠ LES BANDES DE `PHercParis4` PAVENT SANS TROU : sans ce contrôle, « 120 spires en 28
    # bandes » serait vrai d'un corpus qui saute des rangs, et la figure les dessinerait collées.
    v("les bandes de PHercParis4 pavent leur intervalle sans trou",
      ligne("PHercParis4")["trous"] == 0
      and ligne("PHercParis4")["bornes"] == [10, 129],
      f"trous={ligne('PHercParis4')['trous']} bornes={ligne('PHercParis4')['bornes']}")
    v("le compte de franchissements est celui de l'identité",
      all(x["franchissements_dans_une_maille"] == x["spires_couvertes"] - x["bandes"]
          for x in r["lignes"]))
    # ⚠⚠ TOUS LES AUTRES DONNENT LA REPONSE EN MORCEAUX DEJA SEPARES.
    v("tous les autres publient une spire par surface",
      set(r["objets_a_une_spire_par_surface"])
      == {x["nom"] for x in r["lignes"]} - {"PHercParis4"},
      str(r["objets_a_une_spire_par_surface"]))
    v("... y compris le témoin de la carte et l'objet des 775 heures",
      ligne("PHerc0139")["bande_la_plus_longue"] == 1
      and ligne("PHerc1667")["bande_la_plus_longue"] == 1)
    v("... et l'objet courant", ligne("PHerc0500P2")["bande_la_plus_longue"] == 1)
    # ⭐⭐ LA DECROISSANCE, mesurée et pas affirmée : zéro inversion sur vingt-huit bandes.
    v("la longueur des bandes décroît sans une seule inversion",
      ligne("PHercParis4")["decroissance"]["monotone"],
      str(ligne("PHercParis4")["decroissance"]))
    v("... de 18 au premier rang à 2 au dernier",
      ligne("PHercParis4")["decroissance"]["du_premier_au_dernier"] == [18, 2],
      str(ligne("PHercParis4")["spans"]))
    # ⚠⚠⚠ ET LA BANDE LA PLUS LONGUE RESTE SOUS LES 31 DU PRIX : même le meilleur corpus publié
    # ne contient pas une marche entière, il contient dix-sept franchissements d'affilée.
    v("la plus longue bande reste sous les 31 spires du prix",
      ligne("PHercParis4")["bande_la_plus_longue"] < SPIRES_DU_PRIX,
      f"{par['PHercParis4']['bande_la_plus_longue']} contre {SPIRES_DU_PRIX}")
    # ⚠ Aucun des treize du prix n'a de bande du tout — le recoupement de `81` par ce chemin.
    v("aucun des treize rouleaux du prix ne publie une seule bande",
      not any(x["du_prix"] for x in r["lignes"]),
      str([x["nom"] for x in r["lignes"] if x["du_prix"]]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    print(f"{r['objets_avec_bandes']} objets publient au moins une bande · le prix demande "
          f"{r['spires_du_prix']} spires\n")
    print(f"{'objet':16} {'bandes':>7} {'spires':>7} {'sp/surf':>8} {'la + longue':>12} "
          f"{'franchissements':>16}")
    for x in r["lignes"]:
        print(f"{x['nom']:16} {x['bandes']:>7} {x['spires_couvertes']:>7} "
              f"{x['spires_par_surface']:>8} {x['bande_la_plus_longue']:>12} "
              f"{x['franchissements_dans_une_maille']:>16}")
    p4 = next((x for x in r["lignes"] if x["nom"] == "PHercParis4"), None)
    if p4:
        print(f"\nles bandes de PHercParis4, dans l'ordre des rangs : "
              f"{' '.join(str(s) for s in p4['spans'])}")
        d = p4["decroissance"]
        print(f"  {d['inversions']} remontée(s) sur {d['bandes']} bandes — "
              f"{'monotone' if d['monotone'] else 'non monotone'}")
    print(f"\n⭐ publient un franchissement dans une seule maille : "
          f"{', '.join(r['objets_qui_publient_un_franchissement']) or 'aucun'}")
    print(f"⛔ donnent la réponse en morceaux déjà séparés : "
          f"{', '.join(r['objets_a_une_spire_par_surface'])}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
