"""La coupe cherchée trouve-t-elle la frontière ? — non, elle trouve le déséquilibre.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL CORRIGE LA TRANCHE PRÉCÉDENTE. `173` mesure que la recette de `14`
ne lit pas une bascule qui existe, et qu'une coupe **cherchée** la lit partout. Cette tranche devait
la poser sur le vrai rouleau ; `R4-P30` exigeait d'abord son contrôle. Le contrôle l'a réfutée.

⚠⚠⚠ `la_meilleure_coupe` MAXIMISE L'ÉCART, DONC ELLE CHOISIT LA COUPE LA PLUS DÉSÉQUILIBRÉE. Sur une
marche dont la frontière est à la couche **54**, elle coupe à la couche **8** : les huit premières
couches sont pures, donc leur moyenne est franche, et tout le reste est un mélange presque équilibré
dont la résultante vaut **0,089** — une moyenne sans direction, mais parfaitement définie. L'écart
entre une direction franche et une direction arbitraire vaut ce qu'on veut, et il vaut souvent un
quart de tour. Le quatre-vingt-dix degrés de `173` était donc juste **au mauvais endroit**.

⚠⚠ ET LE CONTRÔLE PAR PERMUTATION NE LA RATTRAPE PAS : mélanger les couches conserve le multiensemble
des angles, donc la coupe la plus déséquilibrée trouve encore une part pure et un mélange. Mesuré :
la même valeur sur la courbe ordonnée et sur ses mélanges.

⭐⭐⭐⭐ LE REMÈDE A DEUX PIÈCES, ET AUCUNE N'EST UN SEUIL.
  • **Une moyenne sans résultante n'est pas une direction.** La borne se DÉRIVE : `n` directions
    tirées au hasard rendent une résultante de l'ordre de `1/√n`, donc une tranche qui n'y arrive
    pas n'a rien à dire. C'est la règle que `orientation_profile` applique déjà couche par couche —
    « sans la cohérence, du bruit se lit comme une direction » — posée un étage plus haut.
  • **La coupe s'obtient en AJUSTANT DEUX SEGMENTS, pas en maximisant l'écart.** On retient la coupe
    qui rend la résultante TOTALE la plus grande, c'est-à-dire celle qui laisse les deux parts aussi
    dirigées que possible. Sur une marche, elle tombe exactement sur la frontière.

⚠⚠ CE QUE CETTE TRANCHE NE FAIT PAS, ET C'EST DÉLIBÉRÉ : elle ne touche PAS au vrai rouleau. On ne
pointe pas un instrument réfuté sur la matière, et `R4-P30` reste donc ouverte.

⚠ ET ELLE NE CORRIGE PAS `la_meilleure_coupe` EN PLACE : `173` publie ses nombres, et les tourner
réparerait un défaut en déplaçant des mesures déjà écrites. La recette réparée porte un autre nom,
les deux sont mesurées côte à côte, et c'est l'écart entre elles qui est le résultat.

Usage :
    uv run python src/nappe/la_coupe_cherchee_trouve_t_elle_la_frontiere.py --verifier
    uv run python src/nappe/la_coupe_cherchee_trouve_t_elle_la_frontiere.py \\
        --json docs/mesures/la_coupe_cherchee_trouve_t_elle_la_frontiere.json
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

from fiber_orientation import angular_gap  # noqa: E402
from quelle_fenetre_lit_une_bascule import (LONGUEURS_EN_FEUILLES,  # noqa: E402
                                            courbe_de_la_fixture, la_meilleure_coupe,
                                            la_paire)

PLANCHER_DE_COHERENCE = 0.15
COUCHES_MINIMALES = 4
PERMUTATIONS = 19
GRAINE = 20260916
# ⚠ La marche de reference : cent neuf couches, la profondeur du volume de surface a 2,4 µm, et une
# frontiere posee a la couche 54 — donc la reponse est connue AVANT la mesure.
COUCHES_DE_LA_CAMPAGNE = 109
# ⚠⚠⚠ LA FRONTIERE N'EST PAS AU MILIEU, ET C'EST DELIBERE. Une premiere version la posait a la
# couche 54, qui est exactement la ou la coupe AVEUGLE coupe une fenetre de 109 couches : la
# fixture donnait alors raison a la recette qu'elle devait mettre a l'epreuve, et la ligne
# « aveugle » se lisait comme une reussite. Une fixture complaisante est une verification incapable
# d'echouer, et la batterie exige maintenant que la frontiere soit ailleurs.
FRONTIERE = 37
ANGLE_DU_PREMIER_PLI_DEG = 20.0
LE_QUART_DE_TOUR = 90.0


def la_direction_dune_tranche(courbe, debut: int, fin: int,
                              plancher: float = PLANCHER_DE_COHERENCE,
                              minimum: int = COUCHES_MINIMALES) -> dict | None:
    """L'angle d'une tranche, sa RÉSULTANTE, et `None` quand elle n'a pas de direction.

    ⭐⭐⭐⭐ LA RÉSULTANTE EST CE QUI MANQUAIT. Une moyenne d'orientations rend toujours un angle,
    même quand les directions s'annulent : c'est exactement l'avertissement que
    `fiber_orientation` porte couche par couche — « un angle calculé sur une zone sans texture est
    un angle aléatoire mais bien défini » — et il vaut aussi pour la moyenne d'une tranche.

    ⚠⚠ LA BORNE SE DÉRIVE, ELLE N'EST PAS CHOISIE : `n` directions tirées au hasard rendent une
    résultante de l'ordre de `1/√n`. Une tranche qui n'y arrive pas n'est pas dirigée, et lui
    attribuer un angle ferait lire une annulation comme une direction.

    ⚠ La moyenne est en ANGLE DOUBLE, comme partout : une orientation est modulo 180°.
    """
    ang = np.asarray([x[0] for x in courbe[debut:fin]], dtype=float)
    w = np.asarray([x[1] for x in courbe[debut:fin]], dtype=float)
    fort = w > plancher
    n = int(fort.sum())
    if n < int(minimum):
        return None
    d = np.radians(2.0 * ang[fort])
    poids = w[fort]
    x = float((poids * np.cos(d)).sum())
    y = float((poids * np.sin(d)).sum())
    norme = float(np.hypot(x, y))
    resultante = norme / float(poids.sum())
    if resultante <= 1.0 / np.sqrt(n):
        return None
    return {"angle_deg": float(np.degrees(np.arctan2(y, x)) / 2.0) % 180.0,
            "resultante": resultante, "norme": norme, "couches": n,
            "poids": float(poids.sum())}


def la_paire_ajustee(courbe, coupe: int) -> dict | None:
    """Ce qu'une coupe rend : l'écart, le témoin des DEUX côtés, et la qualité de l'ajustement.

    ⚠⚠ LE TÉMOIN SE LIT DES DEUX CÔTÉS, pas seulement du premier. Une dérive dérive dans les deux
    parts ; un témoin qui ne regarderait que la première laisserait passer la moitié de l'énoncé.
    Le témoin retenu est le PIRE des deux, parce qu'une part qui se contredit suffit à dire que la
    coupe ne sépare pas deux choses homogènes.

    ⚠ `None` dès qu'une tranche n'a pas de direction : une coupe dont un côté ne dit rien n'est pas
    une coupe à moitié bonne, c'est une coupe illisible.
    """
    n = len(courbe)
    a = la_direction_dune_tranche(courbe, 0, coupe)
    b = la_direction_dune_tranche(courbe, coupe, n)
    if a is None or b is None:
        return None
    temoins = []
    for debut, fin in ((0, coupe), (coupe, n)):
        milieu = (debut + fin) // 2
        u = la_direction_dune_tranche(courbe, debut, milieu)
        w = la_direction_dune_tranche(courbe, milieu, fin)
        if u is None or w is None:
            return None
        temoins.append(float(angular_gap(u["angle_deg"], w["angle_deg"])))
    # ⚠⚠⚠ CE BOOLEEN PEUT CONTREDIRE LES DEUX NOMBRES IMPRIMES A COTE DE LUI, ET `176` LE MESURE.
    # Il compare les valeurs NON ARRONDIES : sur une fenetre homogene la bascule et le temoin valent
    # tous deux zero, et un reste de virgule flottante de l'ordre de 1e-15 tranche en faveur de la
    # bascule. Le module publie alors « bascule 0,0 · temoin 0,0 · depasse True ».
    # ⚠⚠ LA VALEUR N'EST PAS CORRIGEE ICI, DELIBEREMENT : `174` et `175` publient des comptes qui en
    # derivent, et les tourner reparerait un defaut en deplacant des mesures deja ecrites. La
    # comparaison reparee vit dans `la_recette_posee_sur_le_rouleau.la_bascule_est_lisible`, qui
    # lit les nombres PUBLIES.
    return {"coupe": int(coupe), "couches": n,
            "bascule_deg": round(float(angular_gap(a["angle_deg"], b["angle_deg"])), 3),
            "temoin_deg": round(float(max(temoins)), 3),
            "resultante_avant": round(a["resultante"], 3),
            "resultante_apres": round(b["resultante"], 3),
            "resultante_totale": a["norme"] + b["norme"],
            "poids_total": a["poids"] + b["poids"],
            "la_bascule_depasse_le_temoin": bool(max(temoins)
                                                 < angular_gap(a["angle_deg"], b["angle_deg"]))}


def la_coupe_par_ajustement(courbe) -> dict | None:
    """La coupe qui laisse les deux parts aussi DIRIGÉES que possible — un ajustement, pas un écart.

    ⭐⭐⭐⭐ C'EST LA RÉPARATION. Maximiser l'écart récompense une coupe dont un côté n'a pas de
    direction, parce que l'écart à une direction arbitraire est arbitrairement grand. Maximiser la
    résultante TOTALE récompense l'inverse : la coupe qui rend les deux parts cohérentes. Sur une
    marche, c'est la frontière, et le vérifier ne demande aucun seuil — on compare la coupe rendue
    à celle qu'on a construite.

    ⚠ La part ATTEINTE de la résultante — le total divisé par la somme des cohérences — est bornée
    entre zéro et un et vaut un sur une marche franche. C'est elle qui se compare aux permutations,
    parce qu'elle mesure l'AJUSTEMENT et non l'écart.
    """
    n = len(courbe)
    if n < 16:
        return None
    lus = [x for x in (la_paire_ajustee(courbe, k)
                       for k in range(COUCHES_MINIMALES, n - COUCHES_MINIMALES + 1)) if x]
    if not lus:
        return None
    meilleur = max(lus, key=lambda x: x["resultante_totale"])
    return {**meilleur, "coupes_lues": len(lus),
            "part_atteinte": round(meilleur["resultante_totale"]
                                   / max(meilleur["poids_total"], 1e-12), 3)}


def contre_les_permutations(courbe, permutations: int = PERMUTATIONS,
                            graine: int = GRAINE) -> dict:
    """L'ajustement réel, et le même ajustement sur des couches MÉLANGÉES.

    ⭐⭐⭐⭐ MÉLANGER DÉTRUIT L'ORDRE EN PROFONDEUR ET RIEN D'AUTRE : chaque couche garde son angle et
    sa cohérence, donc la liberté de choisir une coupe est exactement la même. Ce qui se compare est
    la PART ATTEINTE — l'ajustement — et pas l'écart : c'est précisément parce que l'écart survit au
    mélange que `173` s'est trompée.

    ⚠ La graine est fixe et dérivée du numéro de permutation, donc deux exécutions rendent le même
    compte. Un tirage libre ferait d'une mesure une anecdote.
    """
    reelle = la_coupe_par_ajustement(courbe)
    if reelle is None:
        return {"decidable": False, "raison": "aucune coupe lisible",
                "permutations": int(permutations)}
    parts, refuses = [], 0
    for k in range(int(permutations)):
        r = np.random.default_rng(int(graine) + k)
        ordre = r.permutation(len(courbe))
        m = la_coupe_par_ajustement([courbe[i] for i in ordre])
        if m is None:
            refuses += 1
            continue
        parts.append(float(m["part_atteinte"]))
    return {"decidable": True, **reelle,
            "permutations": int(permutations), "permutations_lues": len(parts),
            "permutations_refusees": int(refuses),
            "part_mediane_des_permutations": (round(float(statistics.median(parts)), 3)
                                              if parts else None),
            "part_maximale_des_permutations": (round(float(max(parts)), 3) if parts else None),
            # ⚠⚠ UNE PERMUTATION REFUSEE COMPTE COMME DEPASSEE : un melange dont aucune coupe n'est
            # lisible est un melange que l'ajustement n'explique pas, donc le reel fait mieux.
            "depasse_toutes_les_permutations": bool(
                all(reelle["part_atteinte"] > x for x in parts))}


def une_marche(couches: int = COUCHES_DE_LA_CAMPAGNE, frontiere: int = FRONTIERE,
               angle: float = ANGLE_DU_PREMIER_PLI_DEG) -> list:
    """Une courbe dont la frontière est CHOISIE — donc la coupe rendue peut être fausse."""
    return ([[float(angle), 0.9]] * int(frontiere)
            + [[(float(angle) + LE_QUART_DE_TOUR) % 180.0, 0.9]] * (int(couches) - int(frontiere)))


def une_derive(couches: int = COUCHES_DE_LA_CAMPAGNE, etendue: float = 170.0) -> list:
    """Une orientation qui TOURNE lentement avec la profondeur — ni marche, ni bruit."""
    return [[float(x), 0.9] for x in np.linspace(0.0, float(etendue), int(couches))]


def une_marche_puis_une_derive(couches: int = COUCHES_DE_LA_CAMPAGNE,
                               frontiere: int = FRONTIERE,
                               angle: float = ANGLE_DU_PREMIER_PLI_DEG,
                               etendue: float = 120.0) -> list:
    """Une part HOMOGÈNE, puis une part qui TOURNE — la matière où le témoin d'un seul côté ment.

    ⭐⭐⭐⭐ ELLE EXISTE PARCE QU'UNE SONDE EST PASSÉE AU VERT. Neutraliser le témoin du second côté
    laissait la batterie verte : sur une marche et sur une dérive franche, les deux côtés disent la
    même chose, donc rien n'exigeait qu'on lise le second. Ici la première part est parfaitement
    homogène — un témoin d'un seul côté y rend zéro et déclare une marche propre — pendant que la
    seconde tourne de part en part.
    """
    n = int(couches) - int(frontiere)
    return ([[float(angle) % 180.0, 0.9]] * int(frontiere)
            + [[(float(angle) + LE_QUART_DE_TOUR + x) % 180.0, 0.9]
               for x in np.linspace(0.0, float(etendue), n)])


def du_bruit(couches: int = COUCHES_DE_LA_CAMPAGNE, graine: int = 5) -> list:
    """Des orientations tirées au hasard — aucune direction, aucune frontière."""
    r = np.random.default_rng(int(graine))
    return [[float(a), 0.9] for a in r.uniform(0.0, 180.0, int(couches))]


def ou_tombe_la_coupe(couches: int = COUCHES_DE_LA_CAMPAGNE,
                      frontiere: int = FRONTIERE) -> dict:
    """Sur une marche dont la frontière est CONNUE, où chaque recette coupe-t-elle ?

    ⭐⭐⭐⭐ C'EST LA MESURE QUI RÉFUTE `173`. La frontière est construite, donc « la coupe rendue
    est-elle la bonne » n'a pas besoin d'un seuil : on compare deux entiers.
    """
    c = une_marche(couches, frontiere)
    ancienne = la_meilleure_coupe(c)
    neuve = la_coupe_par_ajustement(c)
    aveugle = la_paire(c)
    out = {"decidable": bool(ancienne and neuve), "couches": int(couches),
           "frontiere": int(frontiere), "par_recette": {}}
    for nom, lu in (("aveugle", aveugle), ("meilleure", ancienne), ("ajustee", neuve)):
        if not lu or (isinstance(lu, dict) and lu.get("decidable") is False):
            out["par_recette"][nom] = {"decidable": False}
            continue
        out["par_recette"][nom] = {
            "decidable": True, "coupe": int(lu["coupe"]),
            "ecart_a_la_frontiere": int(abs(int(lu["coupe"]) - int(frontiere))),
            "elle_tombe_sur_la_frontiere": bool(int(lu["coupe"]) == int(frontiere)),
            "bascule_deg": lu["bascule_deg"], "temoin_deg": lu["temoin_deg"],
            **({"resultante_avant": lu["resultante_avant"],
                "resultante_apres": lu["resultante_apres"],
                "part_atteinte": lu.get("part_atteinte")} if nom == "ajustee" else {})}
    return out


def ce_que_le_melange_laisse(couches: int = COUCHES_DE_LA_CAMPAGNE,
                             frontiere: int = FRONTIERE,
                             permutations: int = PERMUTATIONS) -> dict:
    """Ce que chaque recette rend sur la marche ORDONNÉE et sur ses MÉLANGES.

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE QUE `R4-P30` EXIGEAIT, ET IL DÉPARTAGE LES DEUX RECETTES. L'écart
    maximisé survit au mélange — le multiensemble des angles ne change pas, donc une part pure et un
    mélange restent trouvables. L'ajustement, lui, ne survit pas : sans ordre en profondeur, aucune
    coupe ne laisse deux parts dirigées.
    """
    c = une_marche(couches, frontiere)
    ancienne = la_meilleure_coupe(c)
    ecarts, refuses = [], 0
    for k in range(int(permutations)):
        r = np.random.default_rng(int(GRAINE) + k)
        m = la_meilleure_coupe([c[i] for i in r.permutation(len(c))])
        if m is None or not m.get("decidable"):
            refuses += 1
            continue
        ecarts.append(float(m["bascule_deg"]))
    neuve = contre_les_permutations(c, permutations)
    return {"decidable": bool(ancienne and neuve.get("decidable")),
            "permutations": int(permutations),
            "la_meilleure_coupe": {
                "bascule_reelle_deg": ancienne["bascule_deg"] if ancienne else None,
                "permutations_lues": len(ecarts), "permutations_refusees": int(refuses),
                "bascule_mediane_des_permutations_deg": (
                    round(float(statistics.median(ecarts)), 3) if ecarts else None),
                "bascule_maximale_des_permutations_deg": (
                    round(float(max(ecarts)), 3) if ecarts else None),
                "elle_depasse_toutes_les_permutations": bool(
                    ancienne and ecarts and all(ancienne["bascule_deg"] > x for x in ecarts))},
            "la_coupe_ajustee": {
                "part_atteinte": neuve.get("part_atteinte"),
                "permutations_lues": neuve.get("permutations_lues"),
                "permutations_refusees": neuve.get("permutations_refusees"),
                "part_mediane_des_permutations": neuve.get("part_mediane_des_permutations"),
                "part_maximale_des_permutations": neuve.get("part_maximale_des_permutations"),
                "elle_depasse_toutes_les_permutations": neuve.get(
                    "depasse_toutes_les_permutations")}}


def les_trois_matieres(couches: int = COUCHES_DE_LA_CAMPAGNE,
                       frontiere: int = FRONTIERE) -> dict:
    """La marche, la dérive et le bruit, lus par la recette ajustée.

    ⚠⚠ LA DÉRIVE EST LA LIMITE DE CET INSTRUMENT ET ELLE EST MESURÉE PLUTÔT QUE TUE : une
    orientation qui tourne de part en part a un ajustement en deux segments qui la lit comme une
    marche. Ce qui l'en distingue est le TÉMOIN, qui vaut zéro sur une marche et nettement plus sur
    une dérive — mais c'est un nombre à lire, pas un verdict, et le prétendre serait choisir un
    seuil.
    """
    lignes = {}
    for nom, c in (("marche", une_marche(couches, frontiere)),
                   ("derive", une_derive(couches)),
                   ("marche_puis_derive", une_marche_puis_une_derive(couches, frontiere)),
                   ("bruit", du_bruit(couches))):
        lu = la_coupe_par_ajustement(c)
        lignes[nom] = ({"decidable": False, "raison": "aucune coupe lisible"} if lu is None
                       else {"decidable": True, "coupe": lu["coupe"],
                             "bascule_deg": lu["bascule_deg"], "temoin_deg": lu["temoin_deg"],
                             "part_atteinte": lu["part_atteinte"],
                             "resultante_avant": lu["resultante_avant"],
                             "resultante_apres": lu["resultante_apres"],
                             "la_bascule_depasse_le_temoin": lu["la_bascule_depasse_le_temoin"]})
    # ⭐⭐⭐⭐ LE TEMOIN A LA JONCTION, DES DEUX COTES ET D'UN SEUL. C'est le nombre qui justifie
    # de lire le second cote, et il doit avoir un PRODUCTEUR : le calculer dans une batterie en
    # ferait un chiffre de sonde, donc impubliable.
    mpd = une_marche_puis_une_derive(couches, frontiere)
    a_la_jonction = la_paire_ajustee(mpd, int(frontiere))
    u = la_direction_dune_tranche(mpd, 0, int(frontiere) // 2)
    w = la_direction_dune_tranche(mpd, int(frontiere) // 2, int(frontiere))
    dun_cote = (None if (u is None or w is None)
                else round(float(angular_gap(u["angle_deg"], w["angle_deg"])), 3))
    return {"decidable": True, "par_matiere": lignes,
            "le_temoin_a_la_jonction": {
                "coupe": int(frontiere), "dun_seul_cote_deg": dun_cote,
                "des_deux_cotes_deg": (a_la_jonction or {}).get("temoin_deg"),
                "le_second_cote_est_lu": bool(
                    a_la_jonction is not None and dun_cote is not None
                    and a_la_jonction["temoin_deg"] > dun_cote)},
            "le_bruit_est_refuse": bool(not lignes["bruit"]["decidable"]),
            "la_marche_tombe_sur_sa_frontiere": bool(
                lignes["marche"]["decidable"] and lignes["marche"]["coupe"] == int(frontiere)),
            # ⚠⚠ DIT PLUTOT QUE TU : l'instrument ne separe PAS une derive d'une marche par un
            # verdict. Les deux temoins sont publies cote a cote et c'est au lecteur de voir que
            # l'un vaut zero et l'autre non.
            "la_derive_nest_pas_separee_par_un_verdict": bool(
                lignes["derive"]["decidable"]
                and lignes["derive"]["la_bascule_depasse_le_temoin"])}


def ce_que_173_avait_lu(voxel_um: float, pas_um: float, longueurs=LONGUEURS_EN_FEUILLES,
                        decalages: int = 12) -> dict:
    """Le balayage des longueurs de `173`, relu par la recette AJUSTÉE.

    ⭐⭐⭐⭐ C'EST LA CORRECTION CHIFFRÉE. `173` publie que la coupe cherchée lit la bascule à six
    longueurs sur huit ; la question est ce que la recette réparée y lit, sur exactement la même
    fixture et aux mêmes décalages. Les deux lectures sont rendues côte à côte.

    ⚠⚠ ET « LIT LA BASCULE » GAGNE UNE TROISIÈME CONDITION : la coupe doit tomber sur la FRONTIÈRE
    de la feuille, que la fixture connaît. Sans elle, une coupe juste au mauvais endroit compterait
    pour une réussite — c'est exactement ce que `173` a compté.
    """
    lignes = []
    for f in longueurs:
        couches = max(16, int(round(float(f) * float(pas_um) / float(voxel_um))))
        par = {"aveugle": 0, "meilleure": 0, "ajustee": 0, "sur_la_frontiere": 0, "lus": 0}
        for k in range(int(decalages)):
            dec = float(pas_um) * k / float(decalages)
            c = courbe_de_la_fixture(couches, dec, 0.5, 2, voxel_um, pas_um)
            # ⚠ La frontiere attendue : la premiere couche dont la profondeur depasse un demi-pas
            # apres le decalage. Elle se DERIVE de la geometrie, jamais du resultat.
            reste = (float(pas_um) / 2.0 - dec) % float(pas_um)
            attendue = int(round(reste / float(voxel_um)))
            par["lus"] += 1
            av = la_paire(c)
            if av.get("decidable") and av["la_bascule_depasse_le_temoin"]:
                par["aveugle"] += 1
            me = la_meilleure_coupe(c)
            if me and me.get("decidable") and me["la_bascule_depasse_le_temoin"]:
                par["meilleure"] += 1
            aj = la_coupe_par_ajustement(c)
            if aj and aj["la_bascule_depasse_le_temoin"]:
                par["ajustee"] += 1
                if abs(aj["coupe"] - attendue) <= 1:
                    par["sur_la_frontiere"] += 1
        lignes.append({"demande_en_feuilles": float(f), "couches": couches, **par})
    return {"decidable": bool(lignes), "lignes": lignes, "decalages": int(decalages),
            "fiables": {r: [x["demande_en_feuilles"] for x in lignes if x[r] == x["lus"]]
                        for r in ("aveugle", "meilleure", "ajustee")},
            "fiables_sur_la_frontiere": [x["demande_en_feuilles"] for x in lignes
                                         if x["sur_la_frontiere"] == x["lus"]]}


def juger(coupe: dict, melange: dict, matieres: dict, relecture: dict) -> dict:
    """Ce que les quatre mesures disent ensemble, sans les fondre en un chiffre."""
    p = coupe.get("par_recette") or {}
    return {
        "decidable": bool(coupe.get("decidable") and melange.get("decidable")),
        "la_meilleure_coupe_tombe_sur_la_frontiere": bool(
            (p.get("meilleure") or {}).get("elle_tombe_sur_la_frontiere")),
        "la_coupe_ajustee_tombe_sur_la_frontiere": bool(
            (p.get("ajustee") or {}).get("elle_tombe_sur_la_frontiere")),
        "ecart_a_la_frontiere_de_la_meilleure": (p.get("meilleure") or {}).get(
            "ecart_a_la_frontiere"),
        "lecart_survit_au_melange": bool(
            not (melange.get("la_meilleure_coupe") or {}).get(
                "elle_depasse_toutes_les_permutations")),
        "lajustement_ne_survit_pas_au_melange": bool(
            (melange.get("la_coupe_ajustee") or {}).get("elle_depasse_toutes_les_permutations")),
        "le_bruit_est_refuse": bool(matieres.get("le_bruit_est_refuse")),
        "la_derive_nest_pas_separee_par_un_verdict": bool(
            matieres.get("la_derive_nest_pas_separee_par_un_verdict")),
        "longueurs_fiables_de_173": (relecture.get("fiables") or {}).get("meilleure"),
        "longueurs_fiables_sur_la_frontiere": relecture.get("fiables_sur_la_frontiere"),
        # ⚠⚠⚠ LE VERDICT EST JOINT ET IL A TROIS MOITIES : l'ancienne recette manque la frontiere,
        # son ecart survit au melange, et la reparee tombe dessus. L'une sans les autres ne dirait
        # pas s'il faut corriger l'instrument ou refaire la mesure.
        "la_meilleure_coupe_est_refutee": bool(
            coupe.get("decidable")
            and not (p.get("meilleure") or {}).get("elle_tombe_sur_la_frontiere")
            and not (melange.get("la_meilleure_coupe") or {}).get(
                "elle_depasse_toutes_les_permutations")
            and (p.get("ajustee") or {}).get("elle_tombe_sur_la_frontiere"))}


def mesurer() -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    coupe = ou_tombe_la_coupe()
    melange = ce_que_le_melange_laisse()
    matieres = les_trois_matieres()
    relecture = ce_que_173_avait_lu(C.VOXEL_FIN_UM, C.PAS_UM)
    return {"couches": COUCHES_DE_LA_CAMPAGNE, "frontiere": FRONTIERE,
            "permutations": PERMUTATIONS, "graine": GRAINE,
            "ou_tombe_la_coupe": coupe, "le_melange": melange,
            "les_trois_matieres": matieres, "la_relecture_de_173": relecture,
            "le_verdict": juger(coupe, melange, matieres, relecture)}


def afficher(r: dict) -> None:
    c, m, t, rl, v = (r["ou_tombe_la_coupe"], r["le_melange"], r["les_trois_matieres"],
                      r["la_relecture_de_173"], r["le_verdict"])
    print("LA COUPE CHERCHÉE TROUVE-T-ELLE LA FRONTIÈRE ?")
    print(f"  une marche de {r['couches']} couches dont la frontière est à la couche "
          f"{r['frontiere']}")
    print()
    print("  OÙ CHAQUE RECETTE COUPE")
    for nom, x in c["par_recette"].items():
        if not x.get("decidable"):
            print(f"   ✗ {nom:<10} illisible")
            continue
        marq = "★" if x["elle_tombe_sur_la_frontiere"] else "✗"
        sup = ""
        if nom == "ajustee":
            sup = (f" · résultantes {x['resultante_avant']}/{x['resultante_apres']} · part "
                   f"atteinte {x['part_atteinte']}")
        print(f"   {marq} {nom:<10} coupe {x['coupe']:>3} (écart {x['ecart_a_la_frontiere']:>3}) · "
              f"bascule {x['bascule_deg']:>6} · témoin {x['temoin_deg']:>6}{sup}")
    print()
    a, b = m["la_meilleure_coupe"], m["la_coupe_ajustee"]
    print(f"  CE QUE LE MÉLANGE LAISSE · {m['permutations']} permutations")
    print(f"   ✗ l'écart maximisé     réel {a['bascule_reelle_deg']} · permutations médiane "
          f"{a['bascule_mediane_des_permutations_deg']} max "
          f"{a['bascule_maximale_des_permutations_deg']} · dépasse toutes : "
          f"{a['elle_depasse_toutes_les_permutations']}")
    print(f"   ★ l'ajustement         réel {b['part_atteinte']} · permutations médiane "
          f"{b['part_mediane_des_permutations']} max {b['part_maximale_des_permutations']} · "
          f"refusées {b['permutations_refusees']}/{m['permutations']} · dépasse toutes : "
          f"{b['elle_depasse_toutes_les_permutations']}")
    print()
    print("  LES TROIS MATIÈRES, par la recette ajustée")
    for nom, x in t["par_matiere"].items():
        if not x["decidable"]:
            print(f"   ✗ {nom:<8} refusée — {x['raison']}")
            continue
        print(f"   {'★' if nom == 'marche' else '⚠'} {nom:<8} coupe {x['coupe']:>3} · bascule "
              f"{x['bascule_deg']:>7} · témoin {x['temoin_deg']:>7} · part atteinte "
              f"{x['part_atteinte']} · résultantes {x['resultante_avant']}/"
              f"{x['resultante_apres']}")
    print()
    print(f"  LA RELECTURE DE `173` · {rl['decalages']} décalages par longueur")
    for x in rl["lignes"]:
        print(f"     {x['demande_en_feuilles']:>5.2f} f ({x['couches']:>3} c) · aveugle "
              f"{x['aveugle']:>2}/{x['lus']} · meilleure {x['meilleure']:>2}/{x['lus']} · "
              f"ajustée {x['ajustee']:>2}/{x['lus']} · SUR LA FRONTIÈRE "
              f"{x['sur_la_frontiere']:>2}/{x['lus']}")
    print(f"   ★ fiables : {rl['fiables']}")
    print(f"   ★ fiables ET sur la frontière : {rl['fiables_sur_la_frontiere']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("la_meilleure_coupe_tombe_sur_la_frontiere", "ecart_a_la_frontiere_de_la_meilleure",
                "lecart_survit_au_melange", "la_coupe_ajustee_tombe_sur_la_frontiere",
                "lajustement_ne_survit_pas_au_melange", "le_bruit_est_refuse",
                "la_derive_nest_pas_separee_par_un_verdict",
                "longueurs_fiables_de_173", "longueurs_fiables_sur_la_frontiere",
                "la_meilleure_coupe_est_refutee"):
        print(f"     {cle:<46} {v.get(cle)}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- la direction d'une tranche, et la borne DERIVEE
    pure = [[20.0, 0.9]] * 32
    d = la_direction_dune_tranche(pure, 0, 32)
    v("une tranche pure rend son angle et une résultante de un",
      d is not None and abs(d["angle_deg"] - 20.0) < 1e-9 and abs(d["resultante"] - 1.0) < 1e-9,
      f"{d and round(d['resultante'], 3)}")
    # ⚠⚠ DEUX DIRECTIONS PERPENDICULAIRES EN NOMBRE EGAL S'ANNULENT EN ANGLE DOUBLE : leur moyenne
    # n'a PAS de direction, et c'est exactement le trou par lequel `173` est passee.
    annule = [[20.0, 0.9]] * 16 + [[110.0, 0.9]] * 16
    v("⭐⭐⭐⭐ deux directions perpendiculaires en nombre égal n'ont PAS de moyenne",
      la_direction_dune_tranche(annule, 0, 32) is None)
    r0 = np.random.default_rng(3)
    hasard = [[float(a), 0.9] for a in r0.uniform(0.0, 180.0, 64)]
    v("⚠ et des directions tirées au hasard non plus",
      la_direction_dune_tranche(hasard, 0, 64) is None)
    v("⚠ une tranche trop courte n'est pas lisible",
      la_direction_dune_tranche(pure, 0, 3) is None)
    # ⚠⚠ LA BORNE SE DERIVE : la sonde la verifie des deux cotes sur une tranche construite pour
    # tomber juste au-dessus et juste en dessous de 1/sqrt(n).
    n = 36
    for part, attendu in ((0.75, True), (0.55, False)):
        k = int(round(part * n))
        melange = [[0.0, 0.9]] * k + [[90.0, 0.9]] * (n - k)
        lu = la_direction_dune_tranche(melange, 0, n)
        # la resultante vaut |2p - 1| en angle double, donc 0,5 a p=0,75 et 0,1 a p=0,55
        v(f"sonde de la borne : à {part:.2f} de directions concordantes la tranche "
          f"{'parle' if attendu else 'se tait'}",
          (lu is not None) == attendu,
          f"résultante {lu and round(lu['resultante'], 3)} · borne {1.0 / np.sqrt(n):.3f}")

    # ---- ou tombe la coupe : la mesure qui refute
    c = ou_tombe_la_coupe()
    v("la marche de référence a sa frontière à la couche construite",
      c["frontiere"] == FRONTIERE and c["couches"] == COUCHES_DE_LA_CAMPAGNE)
    # ⚠⚠⚠ HYGIENE DE LA FIXTURE : si la frontiere tombait la ou la coupe aveugle coupe, la fixture
    # donnerait raison a la recette qu'elle met a l'epreuve.
    v("⚠⚠⚠ ... et elle n'est PAS là où la coupe aveugle coupe",
      c["frontiere"] != c["couches"] // 2,
      f"frontière {c['frontiere']}, coupe aveugle {c['couches'] // 2}")
    v("... donc la coupe aveugle la manque aussi",
      not c["par_recette"]["aveugle"]["elle_tombe_sur_la_frontiere"],
      f"coupe {c['par_recette']['aveugle']['coupe']} pour {c['frontiere']}")
    v("⭐⭐⭐⭐ la coupe AJUSTÉE tombe exactement sur la frontière",
      c["par_recette"]["ajustee"]["elle_tombe_sur_la_frontiere"],
      f"coupe {c['par_recette']['ajustee']['coupe']} pour {c['frontiere']}")
    v("⭐⭐⭐⭐ ... et l'ancienne, celle de `173`, ne tombe PAS dessus",
      not c["par_recette"]["meilleure"]["elle_tombe_sur_la_frontiere"],
      f"coupe {c['par_recette']['meilleure']['coupe']} pour {c['frontiere']}, écart "
      f"{c['par_recette']['meilleure']['ecart_a_la_frontiere']}")
    v("⚠ et elle rend pourtant un quart de tour, donc son nombre était juste au mauvais endroit",
      abs(c["par_recette"]["meilleure"]["bascule_deg"] - LE_QUART_DE_TOUR) < 1e-6,
      f"{c['par_recette']['meilleure']['bascule_deg']}°")

    # ---- le melange : ce qui survit et ce qui ne survit pas
    m = ce_que_le_melange_laisse(permutations=9)
    v("⭐⭐⭐⭐ l'écart maximisé SURVIT au mélange, donc il ne mesure pas l'ordre en profondeur",
      not m["la_meilleure_coupe"]["elle_depasse_toutes_les_permutations"],
      f"réel {m['la_meilleure_coupe']['bascule_reelle_deg']}° contre permutation max "
      f"{m['la_meilleure_coupe']['bascule_maximale_des_permutations_deg']}°")
    v("⭐⭐⭐⭐ ... quand l'AJUSTEMENT, lui, n'y survit pas",
      m["la_coupe_ajustee"]["elle_depasse_toutes_les_permutations"],
      f"part {m['la_coupe_ajustee']['part_atteinte']} contre permutation max "
      f"{m['la_coupe_ajustee']['part_maximale_des_permutations']} · refusées "
      f"{m['la_coupe_ajustee']['permutations_refusees']}/9")

    # ---- les trois matieres, dont la limite DITE
    t = les_trois_matieres()
    v("⚠ contrôle vide : du bruit est REFUSÉ, il ne rend pas une coupe",
      t["le_bruit_est_refuse"])
    v("la marche tombe sur sa frontière", t["la_marche_tombe_sur_sa_frontiere"])
    # ⚠⚠ LA LIMITE EST MESUREE PLUTOT QUE TUE : une derive passe le meme test qu'une marche, et ce
    # qui les separe est un NOMBRE a lire — le temoin — pas un verdict.
    # ⚠⚠⚠ LE TEMOIN DES DEUX COTES EST ASSERTE ICI, ET NULLE PART AILLEURS. Une sonde qui ne
    # lisait que la premiere part a laisse la batterie verte : sur une marche et sur une derive
    # franche les deux cotes disent la meme chose. Sur une marche SUIVIE d'une derive, la premiere
    # part est homogene — le temoin d'un seul cote y rend zero et declare une marche propre.
    # ⚠ L'ENONCE PORTE SUR L'ESTIMATEUR A LA JONCTION, pas sur l'endroit ou l'ajustement tombe :
    # ce qui se teste est que le temoin LIT le second cote, et cela se lit a la coupe ou la matiere
    # est construite pour que les deux cotes disent des choses differentes.
    jonction = t["le_temoin_a_la_jonction"]
    v("⭐⭐⭐⭐ sur une marche SUIVIE d'une dérive, le témoin d'un seul côté rend zéro",
      jonction["dun_seul_cote_deg"] == 0.0, f"{jonction['dun_seul_cote_deg']}° sur la première part")
    v("⭐⭐⭐⭐ ... et celui des DEUX côtés, lui, la voit", jonction["le_second_cote_est_lu"],
      f"témoin {jonction['des_deux_cotes_deg']}° contre "
      f"{jonction['dun_seul_cote_deg']}° d'un seul côté")
    v("⚠⚠ la limite est DITE : une dérive n'est pas séparée d'une marche par un verdict",
      t["la_derive_nest_pas_separee_par_un_verdict"]
      and t["par_matiere"]["derive"]["temoin_deg"] > t["par_matiere"]["marche"]["temoin_deg"],
      f"témoin {t['par_matiere']['marche']['temoin_deg']}° sur la marche contre "
      f"{t['par_matiere']['derive']['temoin_deg']}° sur la dérive")

    # ---- le verdict est JOINT
    faux = juger({**c, "par_recette": {**c["par_recette"],
                                       "ajustee": {**c["par_recette"]["ajustee"],
                                                   "elle_tombe_sur_la_frontiere": False}}},
                 m, t, {"fiables": {}, "fiables_sur_la_frontiere": []})
    v("⚠⚠ le verdict tombe si la recette réparée ne trouve pas non plus la frontière",
      faux["la_meilleure_coupe_est_refutee"] is False)
    vrai = juger(c, m, t, {"fiables": {}, "fiables_sur_la_frontiere": []})
    v("... et il tient quand les trois moitiés tiennent",
      vrai["la_meilleure_coupe_est_refutee"] is True)

    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {controles} checks)")
    else:
        print(f"ALL PASS (0 failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
