"""Là où le rouleau se laisse suivre — et le prix de la question elle-même.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P39` QUI LE NOMME. `190` rend un fait sans explication :
**6** chunks sur **21** voient une marche qui choisit sa couche tenir sa feuille au-delà du hasard,
contre **1,575** attendus — c'est réel, le taux de faux est mesuré — et rien ne dit de quoi ces
six-là sont faits. Or un déroulage n'a pas besoin qu'un critère marche partout : il a besoin de
SAVOIR OÙ IL MARCHE. Une surface qui sait où elle est fiable peut avancer là et demander de l'aide
ailleurs ; une surface qui l'ignore se trompe en silence, et `190` montre qu'elle se trompe avec un
indicateur de qualité qui MONTE.

⚠⚠⚠ ET LE PIÈGE EST TOUTE LA TRANCHE, PAS UN DÉTAIL DE MÉTHODE. Chercher ce qui sépare six chunks de
quinze parmi une liste d'observables EST une maximisation, donc elle trouvera TOUJOURS quelque chose
— c'est la leçon de `186` (l'optimum exact suit du bruit pur) et de `174` (maximiser l'écart le
trouve où il n'est pas). Trois règles, et elles sont dans le code :

1. **La liste des observables est DÉCLARÉE, fermée, et son nombre est publié.** Elle est écrite une
   fois, en tête de fichier, et chaque entrée nomme la mesure publiée d'où elle vient. Un observable
   ajouté après avoir vu les résultats serait une liberté non comptée.
2. **La liberté du choix est PAYÉE par une statistique de FAMILLE** : le maximum de séparation sur
   toute la liste doit dépasser celui que rendent DIX-NEUF mélanges de l'étiquette « retient » sur
   les mêmes chunks. C'est la statistique de `179`, de `176` et de `190`, et elle donne le même taux
   de faux garanti : un sur vingt.
3. **Le PLANCHER DE DÉTECTION est publié** : la plus grande séparation que les mélanges eux-mêmes
   atteignent. C'est ce que six chunks contre quinze permettent de voir, et rien en dessous ne peut
   être établi ici, quoi qu'on mesure.

⚠⚠ ET DEUX OBSERVABLES SONT EXCLUS DÉLIBÉRÉMENT : la part franchie et la plus basse des tirages sont
les INGRÉDIENTS de l'étiquette. Les mettre dans la liste ferait une vérification qui ne peut pas
échouer. Ils servent de face POSITIVE à l'étalon, où c'est exactement leur rôle.

Usage :
    uv run python src/nappe/la_ou_le_rouleau_se_laisse_suivre.py --verifier
    uv run python src/nappe/la_ou_le_rouleau_se_laisse_suivre.py \\
        --json docs/mesures/la_ou_le_rouleau_se_laisse_suivre.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_recette_posee_sur_le_rouleau import PERMUTATIONS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261001
CE_QUE_LE_CHOIX_A_RENDU = "une_surface_qui_choisit_sa_couche"
LETIQUETTE = "le_choix_retient_la_marche"

# ⚠⚠⚠ LA LISTE EST DECLAREE ICI, FERMEE, ET SON NOMBRE EST PUBLIE. Chaque entree est un nombre
# PUBLIE par une tranche anterieure, lu verbatim dans son fichier de mesure et jamais re-derive.
# Ajouter une entree apres avoir vu les resultats serait une liberte non comptee ; en retirer une
# apres coup le serait tout autant.
LES_OBSERVABLES = (
    # `180` — de quoi la frontiere du rouleau est faite
    ("le_rouleau_creuse_t_il", "profondeur", "la profondeur du creux (`180`)"),
    ("le_rouleau_creuse_t_il", "excedent", "l'excédent du creux sur ses mélanges (`180`)"),
    ("le_rouleau_creuse_t_il", "statistique", "la statistique de famille du creux (`180`)"),
    ("le_rouleau_creuse_t_il", "coherence_mediane", "la cohérence médiane du chunk (`180`)"),
    ("le_rouleau_creuse_t_il", "coherence_minimale", "la cohérence minimale du chunk (`180`)"),
    ("le_rouleau_creuse_t_il", "largeur", "la largeur du creux (`180`)"),
    ("le_rouleau_creuse_t_il", "couche", "la couche où le creux tombe (`180`)"),
    # `187` — ce qu'un ruban fait a cet endroit
    ("un_ruban_qui_saute_perd_il_sa_fibre", "pas_a_plat", "la longueur suivable à plat (`187`)"),
    ("un_ruban_qui_saute_perd_il_sa_fibre", "ce_que_le_saut_coute",
     "ce que le saut coûte au ruban (`187`)"),
    ("un_ruban_qui_saute_perd_il_sa_fibre", "ce_que_la_derive_coute",
     "ce que la dérive coûte au ruban (`187`)"),
    ("un_ruban_qui_saute_perd_il_sa_fibre", "montee", "la montée dérivée des frontières (`187`)"),
    # `188` — jusqu'ou la profondeur porte
    ("jusquou_une_surface_peut_elle_deriver", "portee_en_couches",
     "la portée en profondeur (`188`)"),
    ("jusquou_une_surface_peut_elle_deriver", "excedent_maximal",
     "l'excédent maximal sur le mélange (`188`)"),
    ("jusquou_une_surface_peut_elle_deriver", "sommet_en_couches",
     "la montée où l'excédent culmine (`188`)"),
    # `189` — ce que le transfert rend
    ("lempilement_se_repete_t_il", "lectures_par_barreau",
     "les lectures par barreau (`189`)"),
    ("lempilement_se_repete_t_il", "profondeurs_montantes",
     "les profondeurs communes montantes (`189`)"),
    # `190` — les conditions de la marche, JAMAIS ses resultats
    (CE_QUE_LE_CHOIX_A_RENDU, "plafond_du_ruban", "le plafond lu dans la matière (`190`)"),
    (CE_QUE_LE_CHOIX_A_RENDU, "marches", "le nombre de couches texturées (`190`)"),
    (CE_QUE_LE_CHOIX_A_RENDU, "frontieres", "le nombre de frontières lues (`190`)"),
)

# ⚠⚠ CE QUI EST EXCLU, ET POURQUOI : ces trois-la sont les INGREDIENTS de l'etiquette, donc les
# mettre dans la liste ferait une verification qui ne peut pas echouer. Ils servent de face POSITIVE
# a l'etalon, ou c'est exactement leur role.
LES_EXCLUS = ("la part franchie en choisissant", "la plus basse des parts du hasard",
              "ce que le choix retient")


def _med(v):
    return round(float(statistics.median(v)), 4) if v else None


def les_chunks_dune_mesure(nom: str, racine: Path = MESURES) -> dict:
    """Les enregistrements par chunk d'une mesure publiée, indexés par (segment, ligne, colonne).

    ⭐ C'EST CE QUI REND LA JOINTURE POSSIBLE : toutes les tranches du rouleau lisent le MÊME
    treillis et enregistrent leurs chunks sous les mêmes coordonnées. Rien n'a été ajouté ici pour
    ça ; la clef existait déjà dans chaque mesure.
    """
    f = racine / f"{nom}.json"
    if not f.is_file():
        return {}
    d = json.loads(f.read_text(encoding="utf-8"))
    out = {}
    for s in (d.get("les_segments") or []):
        for c in (s.get("chunks") or s.get("lignes") or []):
            if c.get("chunk"):
                out[(str(s.get("segment")), int(c["chunk"][0]), int(c["chunk"][1]))] = c
    return out


def joindre(observables=LES_OBSERVABLES, racine: Path = MESURES) -> dict:
    """La table : une ligne par chunk étiqueté, une colonne par observable déclaré.

    ⚠⚠ UN CHUNK ABSENT D'UNE SOURCE EST REFUSÉ POUR CET OBSERVABLE-LÀ, jamais remplacé par une
    valeur par défaut. Une colonne complétée serait une colonne dont une partie ne vient d'aucune
    mesure, et la séparation qu'elle rendrait serait celle du remplissage.

    ⚠ Le nombre de frontières est une LONGUEUR DE LISTE et non un nombre publié à part : c'est la
    seule entrée dérivée, et elle l'est d'un champ que `190` enregistre tel quel.
    """
    base = les_chunks_dune_mesure(CE_QUE_LE_CHOIX_A_RENDU, racine)
    cles = sorted(k for k, c in base.items() if c.get(LETIQUETTE) is not None)
    if not cles:
        return {"decidable": False, "raison": "aucun chunk étiqueté"}
    etiquettes = [bool(base[k][LETIQUETTE]) for k in cles]
    sources = {}
    colonnes = []
    for mesure, cle, nom in observables:
        if mesure not in sources:
            sources[mesure] = les_chunks_dune_mesure(mesure, racine)
        src = sources[mesure]
        valeurs = []
        for k in cles:
            c = src.get(k)
            v = None if c is None else c.get(cle)
            if isinstance(v, list):
                v = len(v)
            valeurs.append(float(v) if isinstance(v, (int, float)) and not isinstance(v, bool)
                           else None)
        colonnes.append({"mesure": mesure, "cle": cle, "nom": nom, "valeurs": valeurs,
                         "chunks_couverts": int(sum(1 for x in valeurs if x is not None))})
    return {"decidable": True, "chunks": [list(k) for k in cles], "etiquettes": etiquettes,
            "chunks_etiquetes": len(cles), "chunks_qui_retiennent": int(sum(etiquettes)),
            "observables_declares": len(observables), "colonnes": colonnes}


def laire_sous_la_courbe(valeurs, etiquettes) -> float | None:
    """La probabilité qu'un chunk qui retient se classe au-dessus d'un chunk qui ne retient pas.

    ⭐ C'EST UNE STATISTIQUE DE RANG, ET C'EST CE QU'IL FAUT AVEC SIX CONTRE QUINZE. Elle ne suppose
    aucune forme de distribution, elle est insensible à une valeur aberrante, et elle vaut **0,5**
    quand l'observable ne sait rien de l'étiquette.

    ⚠ Les égalités comptent une demie : sans cela un observable constant rendrait **0** ou **1** —
    une séparation parfaite pour une colonne qui ne dit rien.
    """
    a = [float(v) for v, e in zip(valeurs, etiquettes) if v is not None and e]
    b = [float(v) for v, e in zip(valeurs, etiquettes) if v is not None and not e]
    if not a or not b:
        return None
    n = 0.0
    for x in a:
        for y in b:
            n += 1.0 if x > y else (0.5 if x == y else 0.0)
    return round(n / (len(a) * len(b)), 4)


def la_separation(valeurs, etiquettes) -> float | None:
    """L'écart à l'indifférence — la seule quantité que le maximum de famille compare.

    ⚠ Elle est SYMÉTRIQUE parce que la question ne dit pas dans quel sens un observable devrait
    séparer : un creux plus PROFOND ou plus PLAT là où ça tient sont deux réponses également
    intéressantes, et n'en admettre qu'une serait un choix déguisé en mesure. Le sens est publié à
    côté, jamais confondu avec la force.
    """
    auc = laire_sous_la_courbe(valeurs, etiquettes)
    return None if auc is None else round(abs(float(auc) - 0.5), 4)


def le_maximum_de_la_famille(colonnes, etiquettes) -> dict:
    """Le meilleur observable de la liste, et sa séparation — sur toute la liste, jamais sur une."""
    lus = []
    for c in colonnes:
        s = la_separation(c["valeurs"], etiquettes)
        if s is None:
            continue
        lus.append({"nom": c["nom"], "mesure": c["mesure"], "cle": c["cle"],
                    "aire": laire_sous_la_courbe(c["valeurs"], etiquettes), "separation": s,
                    "chunks_couverts": c["chunks_couverts"]})
    if not lus:
        return {"decidable": False, "raison": "aucun observable lisible"}
    meilleur = max(lus, key=lambda x: x["separation"])
    # ⚠⚠ UN OBSERVABLE QUE SA SOURCE NE REND NULLE PART EST NOMMÉ, jamais retiré en silence : il a
    # été DÉCLARÉ, donc il compte dans la liberté qu'on s'est donnée, et taire son absence
    # laisserait croire que la liste essayée est plus courte qu'elle ne l'est.
    muets = [c["nom"] for c in colonnes
             if la_separation(c["valeurs"], etiquettes) is None]
    return {"decidable": True, "observables_lus": len(lus), "le_meilleur": meilleur,
            "observables_sans_lecture": muets,
            "la_separation_maximale": meilleur["separation"], "tous": lus}


def contre_le_melange_des_etiquettes(colonnes, etiquettes, tirages: int = PERMUTATIONS,
                                     graine: int = GRAINE) -> dict:
    """Le nul : la MÊME étiquette, mélangée sur les MÊMES chunks, et le maximum repris à chaque fois.

    ⭐⭐⭐⭐ C'EST CE QUI PAIE LA LIBERTÉ DU CHOIX DE L'OBSERVABLE. Le mélange garde six chunks
    étiquetés sur vingt et un et détruit seulement le LIEN entre l'étiquette et la matière ; le
    maximum est repris sur TOUTE la liste à chaque tirage, donc ce qui est comparé est « le meilleur
    de dix-neuf observables » contre « le meilleur de dix-neuf observables quand il n'y a rien à
    trouver ».

    ⚠⚠ Prendre le maximum d'un seul observable contre son propre mélange ne paierait RIEN : c'est
    justement le choix de l'observable qui est la liberté, et `179` a mesuré qu'une liberté non
    payée triple le taux de faux.

    ⭐ Le plus grand maximum des mélanges est le PLANCHER DE DÉTECTION : c'est ce que vingt et un
    chunks dont six retiennent permettent de voir, et rien en dessous ne peut être établi ici.
    """
    r = np.random.default_rng(int(graine))
    e = np.asarray(etiquettes, dtype=bool)
    maxima = []
    for _ in range(int(tirages)):
        melange = list(r.permutation(e))
        m = le_maximum_de_la_famille(colonnes, melange)
        if m.get("decidable"):
            maxima.append(float(m["la_separation_maximale"]))
    if not maxima:
        return {"decidable": False, "raison": "aucun mélange lisible"}
    return {"decidable": True, "tirages": int(tirages),
            "le_plus_grand_maximum": round(max(maxima), 4),
            "le_maximum_median": _med(maxima),
            "les_maxima": [round(x, 4) for x in maxima]}


def juger_une_liste(colonnes, etiquettes, tirages: int = PERMUTATIONS,
                    graine: int = GRAINE) -> dict:
    """Le maximum de la liste contre celui de ses mélanges — la règle, écrite une seule fois."""
    obs = le_maximum_de_la_famille(colonnes, etiquettes)
    if not obs.get("decidable"):
        return {"decidable": False, "raison": obs.get("raison")}
    nul = contre_le_melange_des_etiquettes(colonnes, etiquettes, tirages, graine)
    if not nul.get("decidable"):
        return {"decidable": False, "raison": nul.get("raison")}
    return {"decidable": True, **obs, "le_nul": nul,
            "le_plancher_de_detection": nul["le_plus_grand_maximum"],
            # ⭐ L'AIRE QU'IL FAUDRAIT ATTEINDRE, dite en aire et non en ecart : c'est la forme sous
            # laquelle un lecteur la compare a celle d'un observable, et la calculer dans le
            # document en ferait un chiffre sans producteur.
            "laire_a_depasser": round(0.5 + float(nul["le_plus_grand_maximum"]), 4),
            # ⭐⭐⭐⭐ LA REGLE : le meilleur des observables doit depasser le meilleur de TOUS les
            # melanges. Un seul melange battu ne dirait rien ; c'est la famille qui price le choix.
            "un_observable_separe": bool(
                float(obs["la_separation_maximale"]) > float(nul["le_plus_grand_maximum"]))}


def _colonne(nom: str, valeurs) -> dict:
    return {"mesure": "étalon", "cle": nom, "nom": nom,
            "valeurs": [None if v is None else float(v) for v in valeurs],
            "chunks_couverts": int(sum(1 for v in valeurs if v is not None))}


def sur_letalon(table: dict, combien: int, tirages: int = PERMUTATIONS,
                graine: int = GRAINE) -> dict:
    """Deux listes dont la réponse est CONNUE, sur les MÊMES chunks et la MÊME étiquette.

    ⭐⭐⭐⭐ LA FACE POSITIVE PORTE L'INGRÉDIENT DE L'ÉTIQUETTE, noyé dans autant de colonnes de bruit
    que la liste déclarée en compte. L'instrument DOIT l'y retrouver : s'il ne le peut pas, il ne
    pourrait rien trouver du tout et son silence sur le rouleau ne voudrait rien dire.

    ⭐⭐⭐⭐ LA FACE NÉGATIVE N'EST QUE DU BRUIT, en même nombre. L'instrument NE DOIT RIEN y trouver :
    c'est le prix de la liberté, et c'est très exactement ce qu'une maximisation non payée
    trouverait quand même.

    ⚠⚠ Les deux listes ont la MÊME taille que la liste déclarée : la statistique de famille dépend
    du nombre d'observables, donc un étalon plus court serait un étalon plus facile.
    """
    e = table["etiquettes"]
    n = len(e)
    r = np.random.default_rng(int(graine) + 7)
    bruit = [_colonne(f"du bruit pur {i}", list(r.normal(0.0, 1.0, n)))
             for i in range(int(combien))]
    # ⚠ L'INGREDIENT DE L'ETIQUETTE, ET IL EST BRUITE : une colonne qui SERAIT l'etiquette rendrait
    # une separation de 0,5 exactement, ce qu'aucun observable reel ne peut atteindre. Ce qu'il faut
    # est une colonne qui la porte AVEC du bruit, donc une separation forte mais pas parfaite.
    porteuse = [(1.0 if x else 0.0) + float(v)
                for x, v in zip(e, r.normal(0.0, 0.6, n))]
    avec = [_colonne("l'ingrédient de l'étiquette, bruité", porteuse)] + bruit[:int(combien) - 1]
    return {"combien_dobservables": int(combien),
            "avec_lingredient": juger_une_liste(avec, e, tirages, graine),
            "rien_que_du_bruit": juger_une_liste(bruit, e, tirages, graine),
            "letalon_separe_les_deux": bool(
                juger_une_liste(avec, e, tirages, graine).get("un_observable_separe")
                and not juger_une_liste(bruit, e, tirages, graine).get("un_observable_separe"))}


def mesurer(tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    table = joindre()
    if not table.get("decidable"):
        return {"message": f"la table ne se construit pas : {table.get('raison')} ; "
                           "relancer `190` d'abord"}
    verdict = juger_une_liste(table["colonnes"], table["etiquettes"], tirages, graine)
    etalon = sur_letalon(table, table["observables_declares"], tirages, graine)
    return {"graine": int(GRAINE), "tirages": int(tirages),
            "letiquette": LETIQUETTE, "la_mesure_etiquetee": CE_QUE_LE_CHOIX_A_RENDU,
            "les_exclus": list(LES_EXCLUS),
            "chunks_etiquetes": table["chunks_etiquetes"],
            "chunks_qui_retiennent": table["chunks_qui_retiennent"],
            "observables_declares": table["observables_declares"],
            "la_table": {k: v for k, v in table.items() if k != "colonnes"},
            "les_colonnes": [{k: v for k, v in c.items() if k != "valeurs"}
                             for c in table["colonnes"]],
            "letalon": etalon,
            "le_verdict": {**verdict,
                           "chunks_etiquetes": table["chunks_etiquetes"],
                           "chunks_qui_retiennent": table["chunks_qui_retiennent"],
                           "observables_declares": table["observables_declares"],
                           "letalon_separe_les_deux": bool(
                               etalon.get("letalon_separe_les_deux"))}}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("LÀ OÙ LE ROULEAU SE LAISSE SUIVRE — ET LE PRIX DE LA QUESTION")
    print(f"  {r['chunks_qui_retiennent']} chunks qui retiennent sur {r['chunks_etiquetes']} · "
          f"{r['observables_declares']} observables DÉCLARÉS · {r['tirages']} mélanges de "
          f"l'étiquette")
    print()
    print("  L'ÉTALON — sur les mêmes chunks et la même étiquette")
    for nom, cle in (("la liste porte l'ingrédient de l'étiquette", "avec_lingredient"),
                     ("la liste n'est que du bruit", "rien_que_du_bruit")):
        x = e.get(cle) or {}
        if not x.get("decidable"):
            print(f"     {nom:<44} — {x.get('raison')}")
            continue
        print(f"     {nom:<44} sépare {x['un_observable_separe']} · maximum "
              f"{x['la_separation_maximale']} contre un plancher de "
              f"{x['le_plancher_de_detection']} · « {x['le_meilleur']['nom']} »")
    print()
    print("  LES OBSERVABLES, DU PLUS SÉPARANT AU MOINS")
    for x in sorted(v.get("tous") or [], key=lambda y: -y["separation"]):
        print(f"     {x['separation']:>7} · aire {x['aire']:>7} · {x['chunks_couverts']:>3} chunks "
              f"· {x['nom']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks_etiquetes", "chunks_qui_retiennent", "observables_declares",
                "observables_lus", "observables_sans_lecture", "la_separation_maximale",
                "le_plancher_de_detection", "laire_a_depasser", "letalon_separe_les_deux",
                "un_observable_separe"):
        print(f"     {cle:<36} {v.get(cle)}")
    print(f"     {'le_meilleur':<36} {v.get('le_meilleur')}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⚠⚠⚠ LA LISTE EST FERMEE ET DECLAREE, ET SON NOMBRE EST CE QUE LA FAMILLE PAIE.
    v("★ la liste des observables est fermée", isinstance(LES_OBSERVABLES, tuple),
      type(LES_OBSERVABLES).__name__)
    v("aucun observable n'est déclaré deux fois",
      len({(m, c) for m, c, _n in LES_OBSERVABLES}) == len(LES_OBSERVABLES),
      str(len(LES_OBSERVABLES)))
    v("★★★ aucun observable n'est un INGRÉDIENT de l'étiquette",
      not any(c in ("part_qui_franchit", "la_plus_basse_des_parts_du_hasard",
                    "ce_que_le_choix_retient", LETIQUETTE)
              for _m, c, _n in LES_OBSERVABLES),
      str([c for _m, c, _n in LES_OBSERVABLES]))
    v("chaque observable nomme la tranche d'où il vient",
      all("`" in n for _m, _c, n in LES_OBSERVABLES))

    # ⭐⭐ L'AIRE SOUS LA COURBE EST UNE STATISTIQUE DE RANG, ET SES TROIS CAS SE VERIFIENT.
    v("★★ une séparation parfaite rend une aire de 1",
      laire_sous_la_courbe([3.0, 4.0, 1.0, 2.0], [True, True, False, False]) == 1.0)
    v("★★ une séparation parfaite inversée rend 0",
      laire_sous_la_courbe([1.0, 2.0, 3.0, 4.0], [True, True, False, False]) == 0.0)
    v("★★★ une colonne CONSTANTE rend exactement l'indifférence",
      laire_sous_la_courbe([7.0] * 4, [True, True, False, False]) == 0.5,
      str(laire_sous_la_courbe([7.0] * 4, [True, True, False, False])))
    v("et la séparation est symétrique",
      la_separation([3.0, 4.0, 1.0, 2.0], [True, True, False, False])
      == la_separation([1.0, 2.0, 3.0, 4.0], [True, True, False, False]))
    v("une colonne sans aucun chunk d'un des deux camps est refusée",
      laire_sous_la_courbe([1.0, 2.0], [True, True]) is None)
    v("★★ un observable que sa source ne rend nulle part est NOMMÉ",
      "observables_sans_lecture" in le_maximum_de_la_famille(
          [_colonne("muet", [None, None, None, None]),
           _colonne("lisible", [3.0, 4.0, 1.0, 2.0])], [True, True, False, False]),
      "")
    v("★★ et il y est bien listé",
      le_maximum_de_la_famille(
          [_colonne("muet", [None, None, None, None]),
           _colonne("lisible", [3.0, 4.0, 1.0, 2.0])],
          [True, True, False, False])["observables_sans_lecture"] == ["muet"])
    j_ = juger_une_liste([_colonne("a", [3.0, 4.0, 1.0, 2.0])], [True, True, False, False], 3, 1)
    v("★★ l'aire à dépasser est une demie plus le plancher",
      abs(float(j_["laire_a_depasser"]) - 0.5 - float(j_["le_plancher_de_detection"])) < 1e-9,
      f"{j_['laire_a_depasser']} pour un plancher de {j_['le_plancher_de_detection']}")
    v("les trous ne comptent pas",
      laire_sous_la_courbe([3.0, None, 1.0, None], [True, True, False, False]) == 1.0)

    # ⚠⚠ LA JOINTURE SE FAIT SUR LA CLEF DE CHUNK, ET UN CHUNK ABSENT EST UN TROU, JAMAIS UN DEFAUT.
    base = les_chunks_dune_mesure(CE_QUE_LE_CHOIX_A_RENDU)
    v("les chunks de `190` se relisent", len(base) > 0, str(len(base)))
    v("et ils sont indexés par (segment, ligne, colonne)",
      all(isinstance(k, tuple) and len(k) == 3 for k in base))
    v("une mesure absente rend une table vide",
      les_chunks_dune_mesure("nexiste_pas_du_tout") == {})
    table = joindre()
    v("la table se construit", table.get("decidable"), str(table.get("raison")))
    if table.get("decidable"):
        v("★ elle porte une colonne par observable déclaré",
          len(table["colonnes"]) == len(LES_OBSERVABLES),
          f"{len(table['colonnes'])} pour {len(LES_OBSERVABLES)}")
        v("chaque colonne a autant de valeurs que de chunks étiquetés",
          all(len(c["valeurs"]) == table["chunks_etiquetes"] for c in table["colonnes"]))
        v("★★ les deux camps sont non vides",
          0 < table["chunks_qui_retiennent"] < table["chunks_etiquetes"],
          f"{table['chunks_qui_retiennent']} sur {table['chunks_etiquetes']}")
        # ⚠⚠ UNE COLONNE PARTIELLEMENT COUVERTE EST LEGITIME : `187` lit moins de chunks que `190`,
        # et la permutation en tient compte toute seule puisqu'elle porte sur l'etiquette.
        v("une colonne peut être partiellement couverte",
          any(c["chunks_couverts"] < table["chunks_etiquetes"] for c in table["colonnes"]),
          str(sorted({c["chunks_couverts"] for c in table["colonnes"]})))

    # ⭐⭐⭐⭐ LA FAMILLE PAIE LE CHOIX, ET LES DEUX FACES DE L'ETALON LE VERIFIENT.
    if table.get("decidable"):
        e = table["etiquettes"]
        n = len(e)
        r = np.random.default_rng(12345)
        bruit = [_colonne(f"bruit {i}", list(r.normal(0.0, 1.0, n))) for i in range(6)]
        parfaite = [_colonne("l'étiquette elle-même", [1.0 if x else 0.0 for x in e])]
        j_b = juger_une_liste(bruit, e, 19, 4242)
        j_p = juger_une_liste(parfaite + bruit[:5], e, 19, 4242)
        v("★★★★ sur du bruit pur, aucun observable ne sépare",
          not j_b.get("un_observable_separe"),
          f"{j_b.get('la_separation_maximale')} contre {j_b.get('le_plancher_de_detection')}")
        v("★★★★ et une colonne qui PORTE l'étiquette est retrouvée",
          j_p.get("un_observable_separe"),
          f"{j_p.get('la_separation_maximale')} contre {j_p.get('le_plancher_de_detection')} "
          f"— « {(j_p.get('le_meilleur') or {}).get('nom')} »")
        v("★★★ et c'est bien ELLE que l'instrument nomme",
          (j_p.get("le_meilleur") or {}).get("nom") == "l'étiquette elle-même",
          str((j_p.get("le_meilleur") or {}).get("nom")))
        # ⚠⚠⚠ LE PLANCHER DE DETECTION CROIT AVEC LE NOMBRE D'OBSERVABLES : c'est la liberte qu'on
        # se donne, et une liste plus longue coute plus cher. Sans cette propriete, la famille ne
        # paierait rien.
        # ⚠⚠⚠ ET C'EST LA SONDE QUI EXERCE LA DECISION CENTRALE : le nul reprend le maximum sur
        # TOUTE la liste a chaque tirage, donc le plancher doit MONTER STRICTEMENT quand la liste
        # s'allonge. Une premiere version comparait avec `>=`, et un nul qui ne paierait qu'UN seul
        # observable — la panne exacte que cette regle existe pour empecher — la satisfaisait :
        # les deux planchers etaient alors egaux. C'etait une verification incapable d'echouer.
        court = juger_une_liste(bruit[:1], e, 19, 4242)
        v("★★★★ le plancher de détection monte STRICTEMENT quand la liste s'allonge",
          float(j_b["le_plancher_de_detection"]) > float(court["le_plancher_de_detection"]),
          f"{court['le_plancher_de_detection']} à 1 observable contre "
          f"{j_b['le_plancher_de_detection']} à 6")
        # ⚠⚠⚠ ET LA REGLE REFUTEE EST PORTEE COMME CONTROLE NOMME, avec son ecart mesure : un nul
        # qui ne paierait qu'un observable abaisse le plancher de la vraie liste et rendrait donc
        # une separation la ou la famille n'en voit aucune.
        if table.get("decidable"):
            faible = contre_le_melange_des_etiquettes(table["colonnes"][:1], e, 19, GRAINE)
            plein = contre_le_melange_des_etiquettes(table["colonnes"], e, 19, GRAINE)
            v("★★★★ un nul qui ne paierait QU'UN observable abaisse le plancher de la vraie liste",
              float(faible["le_plus_grand_maximum"]) < float(plein["le_plus_grand_maximum"]),
              f"{faible['le_plus_grand_maximum']} contre {plein['le_plus_grand_maximum']}")
        # ⚠⚠ LE MELANGE GARDE LE MEME NOMBRE D'ETIQUETTES : sinon il changerait la taille des deux
        # camps et le nul ne serait plus celui de la question posee.
        nul = contre_le_melange_des_etiquettes(bruit, e, 5, 999)
        v("le nul rend un maximum par tirage", len(nul["les_maxima"]) == 5, str(nul["les_maxima"]))

    et = sur_letalon(table, 6, 19, 4242) if table.get("decidable") else {}
    v("★★★★ l'étalon sépare ses deux faces", bool(et.get("letalon_separe_les_deux")),
      f"avec l'ingrédient "
      f"{(et.get('avec_lingredient') or {}).get('un_observable_separe')} · bruit seul "
      f"{(et.get('rien_que_du_bruit') or {}).get('un_observable_separe')}")

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "la_ou_le_rouleau_se_laisse_suivre.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return len(echecs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
