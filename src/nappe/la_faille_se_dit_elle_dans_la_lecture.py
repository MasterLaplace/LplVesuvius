#!/usr/bin/env python3
"""Une faille de l'empilement se dit-elle dans ce que la marche LIT ?

⚠⚠⚠ POURQUOI CE FICHIER. `127` mesure qu'un lien latéral supprime la déchirure de bruit **en
cassant le décrochement réel** : il ne distingue pas les deux. `R4-P25` demande donc un lien qui
sait **quand se relâcher**, et pour se relâcher il faut un signal disponible **au pas**, pas après.
Ce fichier va chercher ce signal là où il devrait être : dans ce que la marche lit déjà.

⭐⭐⭐⭐ **ET LE TÉMOIN DE `127` NE POUVAIT PAS POSER LA QUESTION**, ce qui est la raison d'être de
la fixture neuve. Il décalait les **départs** des marches ; la matière, elle, restait continue.
Une pile continue n'a aucune faille à annoncer, donc l'absence de signal n'y aurait rien prouvé.
`VolumeFabriqueAvecFaille` rompt l'empilement lui-même.

⚠⚠⚠ **ET LA PREMIÈRE CHOSE QUE LA FIXTURE DIT EST QU'UNE FAILLE D'UNE FEUILLE N'EXISTE PAS.** Le
saut est une **phase**, donc il est périodique : décaler les feuilles d'exactement un pas rend un
volume **identique au bit près**. Ce n'est pas une limite de la fixture, c'est une propriété de
l'objet — une pile périodique ne porte aucune information sur le NUMÉRO d'une feuille, seulement
sur la position dans la feuille.

⚠ Deux questions, et la seconde n'a de sens que si la première répond oui :
  1. la faille existe-t-elle dans la matière, et pour quelles tailles ?
  2. quand elle existe, se dit-elle dans ce que la marche lit, et à quelle distance ?

⚠ Aucune lecture distante. Rien ici ne touche le vrai volume.

  uv run python src/nappe/la_faille_se_dit_elle_dans_la_lecture.py --verifier
  uv run python src/nappe/la_faille_se_dit_elle_dans_la_lecture.py \
      --json docs/mesures/la_faille_se_dit_elle_dans_la_lecture.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from le_marcheur_reste_t_il_verrouille import _outils  # noqa: E402

SAUTS = (0.25, 0.5, 0.75, 1.0)
"""Les tailles de faille comparées, en feuilles.

⚠⚠ Quatre valeurs et non un balayage fin : la question est de savoir POUR QUELLES TAILLES la
faille existe et se lit, pas de trouver la taille la plus visible. 1,0 est le cas qui compte —
c'est la déchirure que `124` mesure et que `91` voit au bord du rouleau — et 0,5 est le maximum
de discontinuité qu'une phase puisse porter."""

DISTANCES_VX = (0, 5, 10, 15, 20, 25, 30, 45)
"""La distance de la marche au plan de faille, en voxels.

⚠⚠ Elles ne sont pas choisies : le cube de lecture a un demi-côté de `demi` voxels (20 par
défaut), donc la faille est DANS le cube en deçà de 20 et dehors au-delà. 0 est le cas
particulier qui compte — la faille passe par le centre, c'est-à-dire exactement là où
`accord_des_moities` COUPE son cube, donc les deux moitiés sont chacune d'un côté et propres.

⚠ 25 et 30 encadrent la prédiction géométrique : le cube va de `centre − demi` à `centre + demi`
inclus, donc un plan à exactement `demi` est sa face et se lit encore, et à `demi + 1` il ne se lit
plus du tout. Sans les deux, la portée serait un intervalle de dix voxels où tout peut se loger."""

GRAINES = (3, 11, 29, 53, 97, 131, 179, 223, 271, 313, 367, 419)
PAS = 24
SIGNAUX = ("planarite", "desaccord_des_moities_deg", "accord_de_linterstice",
           "score_du_balayage")
"""Les quantités interrogées — celles que la marche produit DÉJÀ.

⭐⭐ Aucun instrument neuf : un signal qui exigerait une seconde lecture ne serait pas disponible
au pas, donc il ne pourrait pas relâcher un lien au moment où il faut. Et ce serait un second
lecteur, libre de ne pas s'accorder avec le premier."""


def la_faille_existe_t_elle(sauts=SAUTS, pas_um: float | None = None,
                            points: int = 2000, graine: int = 7) -> list[dict]:
    """La matière change-t-elle, et de combien, quand on injecte une faille de cette taille ?

    ⭐⭐⭐⭐ C'EST LA QUESTION AVANT LA QUESTION, et elle se répond sans marcher. Chercher un
    signal d'une faille qui n'existe pas rendrait « aucun signal » pour la raison la plus banale
    qui soit. On compare donc, point par point, la pile rompue à la pile intacte.

    ⚠ Les points sont tirés DE PART ET D'AUTRE du plan, sinon on mesurerait le côté qui n'a pas
    bougé et toute faille paraîtrait nulle.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique, VolumeFabriqueAvecFaille
    import combien_dinterstices_traverses as C

    p_um = C.PAS_UM if pas_um is None else float(pas_um)
    r = np.random.default_rng(graine)
    z0 = 2000.0
    p = np.column_stack([r.uniform(z0 - 60, z0 + 60, points),
                         r.uniform(1900, 2100, points),
                         r.uniform(1900, 2100, points)])
    intacte = VolumeFabrique(p_um, obliquite_deg=35.0, forme=(4000, 4000, 4000))
    v0 = intacte.lire(p)
    out = []
    for s in sauts:
        rompue = VolumeFabriqueAvecFaille(p_um, s * p_um, z0, obliquite_deg=35.0,
                                          forme=(4000, 4000, 4000))
        d = np.abs(rompue.lire(p) - v0)
        out.append({"saut_en_feuilles": round(float(s), 3),
                    "saut_um": round(float(s * p_um), 2),
                    "ecart_maximal": round(float(d.max()), 6),
                    "ecart_median": round(float(np.median(d)), 6),
                    # ⭐⭐⭐⭐ Le verdict : au-delà de l'arrondi, la matière a-t-elle seulement
                    # changé ? ⚠ Le plancher est celui du FLOTTANT, pas un seuil réglé : le résidu
                    # d'un saut d'une feuille vaut ~2e-12 sur un contraste de 40, et une
                    # demi-feuille en déplace ~37. Trois décades au-dessus du résidu, dix sous le
                    # signal : aucun choix raisonnable dans cet intervalle ne change la réponse.
                    "la_matiere_change": bool(d.max() > 1e-9)})
    return out


def _une_marche(o, pile, depart, pas: int, demi: int) -> dict:
    """Une marche, résumée par le PIRE et par la médiane de chaque signal sur ses pas.

    ⚠⚠ LE RÉSUMÉ EST PAR MARCHE, PAS PAR PAS, et c'est la réserve de grappe du dépôt : les pas
    d'une même marche lisent des cubes qui se recouvrent, donc les compter comme indépendants
    gonflerait n d'un facteur vingt. L'unité décisive est la marche.

    ⚠⚠⚠ ET LE PIRE EST RENDU PARCE QUE LA MÉDIANE SEULE M'A FAIT RATER LE SIGNAL. Une faille ne
    touche qu'un pas — celui où la marche la rencontre — donc une médiane sur vingt-quatre le
    noie : ma première lecture rendait « 0,00 » de désaccord là où le pas fautif en portait
    **86**. C'est le péché capital du dépôt, moyenner sur l'axe où vit la différence, commis sur
    ma propre mesure. Les deux sont publiés : la médiane dit ce que la marche lit d'ordinaire, le
    pire dit si elle a vu quelque chose.
    """
    from combien_de_pas_la_matiere_porte import marcher

    e = marcher(pile, depart, np.array([0.0, 0.0, 1.0]), o["longueurs"], o["mu"], o["sd"],
                o["barre"], o["barre_moities"], o["barre_interstice"], o["C"].VOXEL_FIN_UM,
                pas_max=pas, demi=demi)
    lus = [x for x in e if "confirme" in x]
    out = {"pas": len(lus)}
    for nom in SIGNAUX:
        vals = [x[nom] for x in lus if x.get(nom) is not None and np.isfinite(x[nom])]
        out[nom] = round(float(np.median(vals)), 4) if vals else None
        # ⚠ La planarite est un contraste : son cas grave est le BAS, pas le haut. Prendre le
        # maximum partout rendrait le pire d'un signal et le meilleur de l'autre sous un seul nom.
        out[nom + "_pire"] = (round(float(min(vals) if nom == "planarite" else max(vals)), 4)
                              if vals else None)
    out["part_refusee"] = (round(sum(1 for x in lus if not x.get("oriente")) / len(lus), 4)
                           if lus else None)
    out["part_refusee_pire"] = out["part_refusee"]
    out["taux"] = (round(sum(1 for x in lus if x.get("confirme")) / len(lus), 4)
                   if lus else None)
    out["taux_pire"] = out["taux"]
    return out


def _wilcoxon(ecarts) -> float | None:
    """Le p apparié, ou None si la série est dégénérée.

    ⚠ Une série toute nulle n'a aucune paire informative : rendre 1,0 se lirait comme « testé et
    non significatif » alors que rien n'a été testé. `115` a payé exactement ça.
    """
    x = np.asarray([v for v in ecarts if v is not None and np.isfinite(v)], dtype=np.float64)
    x = x[x != 0.0]
    if len(x) < 3:
        return None
    from scipy.stats import wilcoxon  # noqa: PLC0415
    return float(wilcoxon(x).pvalue)


def le_signal_par_distance(sauts=SAUTS, distances=DISTANCES_VX, graines=GRAINES,
                           pas: int = PAS, demi: int = 20, obliquite_deg: float = 35.0,
                           bruit: float = 8.0) -> dict:
    """Ce que la marche lit, selon sa distance au plan de faille — apparié à la pile INTACTE.

    ⭐⭐⭐⭐ LE TEST EST APPARIÉ : la même graine de bruit est marchée sur la pile rompue et sur la
    pile intacte, au même endroit. Comparer deux endroits mesurerait surtout le bruit local ;
    comparer deux graines mesurerait laquelle est tombée sur un tirage clément.

    ⚠⚠ La marche intacte est calculée UNE FOIS par (distance, graine) et partagée par les quatre
    tailles de faille : elle n'en dépend pas. La recalculer quatre fois serait quatre occasions
    d'obtenir quatre références d'une seule situation.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique, VolumeFabriqueAvecFaille

    o = _outils(demi)
    C = o["C"]
    cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    z0 = 2000.0
    base = np.array([z0, 2000.0, 2000.0])

    # ⚠ Le départ est recalé sur une feuille de la pile INTACTE : partir entre deux feuilles
    # ferait payer au premier pas un rattrapage que la faille n'a pas causé.
    ref = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, forme=(cote, cote, cote))
    proj = float(base @ ref.normale) * C.VOXEL_FIN_UM
    base = base + ref.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)

    intactes: dict[tuple[int, int], dict] = {}
    for g in graines:
        pile = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, bruit=bruit, graine=g,
                              forme=(cote, cote, cote))
        for d in distances:
            dep = base + np.array([float(d), 0.0, 0.0])
            intactes[(d, g)] = _une_marche(o, pile, dep, pas, demi)

    out = {"obliquite_deg": obliquite_deg, "bruit": bruit, "pas": pas, "demi_cube_voxels": demi,
           "graines": list(graines), "distances_vx": list(distances),
           "voxel_um": C.VOXEL_FIN_UM, "pas_um": C.PAS_UM,
           # ⚠⚠ LA BARRE VOYAGE AVEC LES DEGRÉS, sinon « 88° » ne veut rien dire : c'est le p1
           # du bruit pur, donc la valeur sous laquelle un cube sans structure descend une fois
           # sur cent. Un angle publié sans elle se lit comme une opinion sur ce qui est grand.
           "barre_daccord_des_moities_deg": round(float(o["barre_moities"]), 4),
           "par_saut": []}
    for s in sauts:
        lignes = []
        for g in graines:
            pile = VolumeFabriqueAvecFaille(C.PAS_UM, s * C.PAS_UM, z0,
                                            obliquite_deg=obliquite_deg, bruit=bruit,
                                            graine=g, forme=(cote, cote, cote))
            for d in distances:
                dep = base + np.array([float(d), 0.0, 0.0])
                lignes.append({"distance_vx": d, "graine": g,
                               "rompue": _une_marche(o, pile, dep, pas, demi),
                               "intacte": intactes[(d, g)]})
        par_distance = []
        for d in distances:
            lot = [x for x in lignes if x["distance_vx"] == d]
            # ⚠ Borne INCLUSIVE : le cube s'étend de `centre − demi` à `centre + demi`, donc un
            # plan à exactement `demi` est sa face et il est lu. La mesure le confirme — le signal
            # est entier à 20 et nul à 25 — mais la borne vient de la géométrie, pas du tableau.
            bloc = {"distance_vx": d, "marches": len(lot),
                    "dans_le_cube": bool(d <= demi)}
            for nom in (*SIGNAUX, *(x + "_pire" for x in SIGNAUX), "part_refusee", "taux"):
                ec = [(x["rompue"][nom] - x["intacte"][nom])
                      for x in lot
                      if x["rompue"][nom] is not None and x["intacte"][nom] is not None]
                if not ec:
                    continue
                bloc[nom] = {"rompue": round(float(np.median(
                                 [x["rompue"][nom] for x in lot
                                  if x["rompue"][nom] is not None])), 4),
                             "intacte": round(float(np.median(
                                 [x["intacte"][nom] for x in lot
                                  if x["intacte"][nom] is not None])), 4),
                             "ecart_median": round(float(np.median(ec)), 4),
                             "p": _wilcoxon(ec)}
                if bloc[nom]["p"] is not None:
                    bloc[nom]["p"] = round(bloc[nom]["p"], 4)
            par_distance.append(bloc)
        out["par_saut"].append({"saut_en_feuilles": round(float(s), 3),
                                "par_distance": par_distance, "detail": lignes})
    return out


def ou_tombe_le_pas_refuse(saut_en_feuilles: float = 0.5, distance_vx: int = 10,
                           graines=GRAINES, pas: int = PAS, demi: int = 20,
                           obliquite_deg: float = 35.0, bruit: float = 8.0) -> dict:
    """A QUEL RANG le pas refuse tombe-t-il ?

    ⭐⭐⭐⭐ SANS CETTE QUESTION LE SIGNAL NE VEUT RIEN DIRE. La faille est presente a TOUS les
    pas — la marche garde sa distance au plan — et pourtant un seul pas de plus est refuse. Ou il
    tombe decide de ce que le signal est : au premier rang c'est un artefact de DEPART, celui d'une
    marche recalee sur la pile intacte et posee a cote de sa feuille du cote rompu, donc rien qu'un
    lien pourrait utiliser en cours de route ; reparti sur la course, c'est une garde qui parle
    quand elle voit.

    ⚠ La mediane des rangs ne suffirait pas : deux marches qui refusent l'une au rang 0 et l'autre
    au rang 20 rendent la meme mediane qu'une population centree au milieu. Ce qui est rendu est
    donc la PART des refus qui tombent au premier rang, plus la liste des rangs.

    ⚠⚠⚠ ET L'EXCURSION LATERALE EST RENDUE A COTE, PARCE QUE SANS ELLE LE RANG NE SE LIT PAS.
    Rien ne retient la position de la marche DANS le plan de la feuille : elle avance le long de la
    normale, et sa composante z n'est contrainte par personne. Si elle glisse de plus d'un
    demi-cube, la faille sort de sa vue et « un seul pas refuse » ne veut plus dire « la garde ne
    parle qu'une fois » mais « la marche est partie ». Les deux lectures sont opposees et le
    tableau des rangs seul ne les distingue pas.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique, VolumeFabriqueAvecFaille, marcher

    o = _outils(demi)
    C = o["C"]
    cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    z0 = 2000.0
    base = np.array([z0, 2000.0, 2000.0])
    ref = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, forme=(cote, cote, cote))
    proj = float(base @ ref.normale) * C.VOXEL_FIN_UM
    base = base + ref.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
    dep = base + np.array([float(distance_vx), 0.0, 0.0])
    rangs: list[int] = []
    excursions: list[float] = []
    excursions_intactes: list[float] = []
    rangs_sortie: list[int | None] = []
    # ⭐⭐⭐⭐ LE PREMIER PAS EST LE PAS DE LA RENCONTRE, donc c'est lui qu'il faut regarder :
    # tout le reste de la marche se passe ailleurs, la faille l'ayant deja chassee.
    premier: dict[str, list[float]] = {"desaccord": [], "avance": [], "part_z": [],
                                       "desaccord_intact": [], "avance_intacte": [],
                                       "part_z_intacte": []}
    marches = 0
    for g in graines:
        pile = VolumeFabriqueAvecFaille(C.PAS_UM, saut_en_feuilles * C.PAS_UM, z0,
                                        obliquite_deg=obliquite_deg, bruit=bruit, graine=g,
                                        forme=(cote, cote, cote))
        e = marcher(pile, dep, np.array([0.0, 0.0, 1.0]), o["longueurs"], o["mu"], o["sd"],
                    o["barre"], o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                    pas_max=pas, demi=demi, rendre_position=True)
        lus = [x for x in e if "confirme" in x]
        marches += 1
        rangs.extend(i for i, x in enumerate(lus) if not x.get("oriente"))
        # ⚠ L'excursion est comptee sur l'axe z SEUL : c'est celui qui porte la distance au plan
        # de faille. La distance parcourue totale melangerait l'avance, qui est voulue.
        zs = [dep[0]] + [x["position_zyx"][0] for x in lus if "position_zyx" in x]
        excursions.append(round(float(max(zs) - min(zs)), 2))
        # ⭐⭐⭐⭐ LE TÉMOIN : la MÊME marche sur la pile INTACTE. Sans lui, « la marche s'éloigne
        # de 105 voxels » ne distingue pas « la faille l'éjecte » de « une marche vagabonde », et
        # les deux lectures mènent à des conclusions opposées.
        pi = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, bruit=bruit, graine=g,
                            forme=(cote, cote, cote))
        ei = marcher(pi, dep, np.array([0.0, 0.0, 1.0]), o["longueurs"], o["mu"], o["sd"],
                     o["barre"], o["barre_moities"], o["barre_interstice"], C.VOXEL_FIN_UM,
                     pas_max=pas, demi=demi, rendre_position=True)
        zi = [dep[0]] + [x["position_zyx"][0] for x in ei
                         if "confirme" in x and "position_zyx" in x]
        excursions_intactes.append(round(float(max(zi) - min(zi)), 2))
        # ⚠ `part_z` est la part de l'avance prise PERPENDICULAIREMENT au plan de faille. Sur une
        # pile saine elle est nulle : l'empilement n'a aucune composante z. Une valeur proche de 1
        # dit que la marche a pris le plan de faille POUR une feuille et l'a traversee.
        for src, cle in ((lus, ""), ([x for x in ei if "confirme" in x], "_intact")):
            if not src:
                continue
            x0 = src[0]
            premier["desaccord" + cle].append(float(x0["desaccord_des_moities_deg"]))
            premier[("avance" if not cle else "avance_intacte")].append(
                float(x0["avance_um"]))
            premier[("part_z" if not cle else "part_z_intacte")].append(
                abs(float(x0["direction"][0])))
        rangs_sortie.append(next((i for i, x in enumerate(lus)
                                  if "position_zyx" in x
                                  and abs(x["position_zyx"][0] - dep[0]) > demi), None))
    au_premier = sum(1 for r in rangs if r == 0)
    sorties = [r for r in rangs_sortie if r is not None]
    return {"saut_en_feuilles": saut_en_feuilles, "distance_vx": distance_vx,
            "marches": marches, "pas": pas, "refus": len(rangs), "rangs": sorted(rangs),
            "au_premier_rang": au_premier,
            "part_au_premier_rang": (round(au_premier / len(rangs), 4) if rangs else None),
            # ⭐⭐⭐⭐ Le verdict : le refus est-il autre chose qu'un artefact de depart ?
            "le_refus_est_un_artefact_de_depart": bool(rangs) and au_premier == len(rangs),
            "au_premier_pas": {
                "desaccord_deg": round(float(np.median(premier["desaccord"])), 2),
                "desaccord_deg_intact": round(float(np.median(premier["desaccord_intact"])), 2),
                "avance_um": round(float(np.median(premier["avance"])), 1),
                "avance_um_intacte": round(float(np.median(premier["avance_intacte"])), 1),
                "part_perpendiculaire_au_plan": round(float(np.median(premier["part_z"])), 4),
                "part_perpendiculaire_au_plan_intacte": round(
                    float(np.median(premier["part_z_intacte"])), 4),
                # ⭐⭐⭐⭐ Le verdict : la marche a-t-elle pris la faille pour une feuille ?
                # Elle avance perpendiculairement au plan de faille, ce que l'empilement ne lui
                # demande jamais — sa normale n'a aucune composante sur cet axe.
                "la_marche_prend_la_faille_pour_une_feuille": bool(
                    np.median(premier["part_z"]) > 0.9
                    and np.median(premier["part_z_intacte"]) < 0.2)},
            "excursion_laterale_vx": sorted(excursions),
            "excursion_laterale_mediane_vx": round(float(np.median(excursions)), 2),
            "excursion_laterale_intacte_mediane_vx": round(float(
                np.median(excursions_intactes)), 2),
            "excursion_laterale_intacte_max_vx": round(float(max(excursions_intactes)), 2),
            # ⭐⭐⭐⭐ Le verdict : c'est la faille qui éjecte, pas la marche qui vagabonde.
            "la_faille_ejecte_la_marche": bool(
                np.median(excursions) > 3.0 * max(1e-9, np.median(excursions_intactes))
                and np.median(excursions_intactes) < demi),
            "demi_cube_voxels": demi,
            # ⚠⚠ Combien de marches s'eloignent de plus d'un demi-cube, et a quel rang : au-dela,
            # la faille n'est plus dans ce qu'elles lisent.
            "marches_qui_sortent_du_cube": len(sorties),
            "rang_median_de_sortie": (round(float(np.median(sorties)), 1) if sorties else None)}


def juger(existence: list[dict], signal: dict, alpha: float = 0.01) -> dict:
    """Croise les deux questions : la faille existe-t-elle, et se dit-elle.

    ⭐⭐⭐⭐ LE VERDICT NE PEUT PAS ÊTRE RENDU PAR LA SECONDE QUESTION SEULE. « Aucun signal » se
    lit comme une panne du lecteur alors que c'est, pour un saut d'une feuille, l'absence de ce
    qu'il faudrait lire. Les deux réponses sont donc rendues côte à côte, par taille de faille.

    ⚠ `alpha` n'est pas un seuil réglé sur ce qui passe : c'est le même 0,01 que le dépôt applique
    partout, choisi avant la mesure. Ce qui est publié est le p, pas le verdict seul.

    ⚠⚠ Une taille dont la matière NE change PAS est déclarée `invisible_par_construction`, et pas
    « non détectée » : les deux se ressemblent dans un tableau et ne veulent pas dire la même
    chose. L'une est une propriété de l'objet, l'autre serait une limite du lecteur.
    """
    par_taille = {x["saut_en_feuilles"]: x for x in existence}
    out = []
    for bloc in signal.get("par_saut", []):
        s = bloc["saut_en_feuilles"]
        ex = par_taille.get(s)
        existe = bool(ex and ex["la_matiere_change"])
        vues = []
        for d in bloc["par_distance"]:
            for nom in (*(x + "_pire" for x in SIGNAUX), "part_refusee"):
                v = d.get(nom)
                if v and v["p"] is not None and v["p"] < alpha and v["ecart_median"] != 0.0:
                    vues.append({"distance_vx": d["distance_vx"], "signal": nom,
                                 "ecart_median": v["ecart_median"], "p": v["p"]})
        out.append({"saut_en_feuilles": s,
                    "la_matiere_change": existe,
                    "ecart_maximal_de_matiere": ex["ecart_maximal"] if ex else None,
                    "signaux_qui_voient": vues,
                    "portee_maximale_vx": max((x["distance_vx"] for x in vues), default=None),
                    "invisible_par_construction": not existe,
                    "la_faille_se_dit": bool(existe and vues)})
    return {"alpha": alpha, "par_saut": out,
            # ⭐⭐⭐⭐ La question du graal en un booléen : la déchirure que `124` mesure vaut UNE
            # feuille, donc c'est celle-là qu'un lien devrait savoir respecter.
            "une_feuille_se_dit": next((x["la_faille_se_dit"] for x in out
                                        if abs(x["saut_en_feuilles"] - 1.0) < 1e-9), None)}


def mesurer(pas: int = PAS, graines=GRAINES, distances=DISTANCES_VX, demi: int = 20) -> dict:
    """Tout, analytique."""
    ex = la_faille_existe_t_elle()
    sig = le_signal_par_distance(graines=graines, distances=distances, pas=pas, demi=demi)
    return {"la_faille_existe_t_elle": ex, "le_signal_par_distance": sig,
            # ⚠ La sonde des rangs tourne A COTE du balayage et pas dedans : elle repond a « ce
            # que le signal EST », pas a « y a-t-il un signal ». Les fondre rendrait un tableau
            # dont une colonne repond a une autre question que les autres.
            "ou_tombe_le_pas_refuse": ou_tombe_le_pas_refuse(graines=graines, pas=pas,
                                                            demi=demi),
            "verdict": juger(ex, sig)}


def afficher(r: dict) -> None:
    print("la matière change-t-elle ?\n")
    print("   saut (feuilles)   écart max   écart médian   la matière change")
    for x in r["la_faille_existe_t_elle"]:
        print(f"   {x['saut_en_feuilles']:>15.3f}   {x['ecart_maximal']:>9.6f}"
              f"   {x['ecart_median']:>12.6f}   {x['la_matiere_change']!s:>17}")
    s = r["le_signal_par_distance"]
    print(f"\n{len(s['graines'])} graines · obliquité {s['obliquite_deg']}° · bruit {s['bruit']}"
          f" · {s['pas']} pas · cube ±{s['demi_cube_voxels']} voxels")
    for bloc in s["par_saut"]:
        print(f"\n  saut {bloc['saut_en_feuilles']} feuille(s) — écart apparié à la pile intacte")
        print("     d(vx)  cube   désaccord° médian   désaccord° PIRE    part refusée")
        for d in bloc["par_distance"]:
            def c(nom):
                v = d.get(nom)
                if not v:
                    return f"{'—':>18}"
                p = "     —" if v["p"] is None else f"{v['p']:.4f}"
                return f"{v['ecart_median']:>+8.4f} p{p:>7}"
            print(f"     {d['distance_vx']:>5}  {'dedans' if d['dans_le_cube'] else 'dehors':>6}"
                  f"  {c('desaccord_des_moities_deg')}  "
                  f"{c('desaccord_des_moities_deg_pire')}  {c('part_refusee')}")
    o = r.get("ou_tombe_le_pas_refuse")
    if o:
        print(f"\n  ou tombe le pas refuse (saut {o['saut_en_feuilles']}, d {o['distance_vx']} vx,"
              f" {o['marches']} marches de {o['pas']} pas)")
        print(f"    {o['refus']} refus, dont {o['au_premier_rang']} au premier rang "
              f"({o['part_au_premier_rang']}) · rangs {o['rangs']}")
        q = o["au_premier_pas"]
        print(f"    ⭐ au premier pas : désaccord {q['desaccord_deg']}° contre "
              f"{q['desaccord_deg_intact']}° intacte · avance {q['avance_um']} µm contre "
              f"{q['avance_um_intacte']} · part perpendiculaire au plan "
              f"{q['part_perpendiculaire_au_plan']} contre "
              f"{q['part_perpendiculaire_au_plan_intacte']}")
        print(f"    ⭐ la marche prend la faille pour une feuille : "
              f"{q['la_marche_prend_la_faille_pour_une_feuille']}")
        print(f"    ⚠ excursion latérale : {o['excursion_laterale_mediane_vx']} vx contre "
              f"{o['excursion_laterale_intacte_mediane_vx']} sur pile intacte "
              f"(max {o['excursion_laterale_intacte_max_vx']}) · demi-cube "
              f"{o['demi_cube_voxels']}")
        print(f"    ⭐ la faille éjecte la marche : {o['la_faille_ejecte_la_marche']} · "
              f"{o['marches_qui_sortent_du_cube']}/{o['marches']} sortent, rang médian "
              f"{o['rang_median_de_sortie']}")
    print("\n  verdict")
    for x in r["verdict"]["par_saut"]:
        if x["invisible_par_construction"]:
            print(f"   saut {x['saut_en_feuilles']} : ⚠ INVISIBLE PAR CONSTRUCTION — "
                  f"la matière est identique (écart max {x['ecart_maximal_de_matiere']})")
        else:
            print(f"   saut {x['saut_en_feuilles']} : la matière change "
                  f"(écart max {x['ecart_maximal_de_matiere']}) · se dit : "
                  f"{x['la_faille_se_dit']} · portée {x['portee_maximale_vx']} vx · "
                  f"{len(x['signaux_qui_voient'])} lecture(s) qui voient")
    print(f"\n   ⭐ une faille d'UNE feuille se dit : {r['verdict']['une_feuille_se_dit']}")


def verifier() -> int:
    """La batterie, hors ligne, sur peu de pas pour rester rapide."""
    from combien_de_pas_la_matiere_porte import VolumeFabrique, VolumeFabriqueAvecFaille
    import combien_dinterstices_traverses as C

    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    r = np.random.default_rng(5)
    p = np.column_stack([r.uniform(1940, 2060, 400), r.uniform(1950, 2050, 400),
                         r.uniform(1950, 2050, 400)])
    intacte = VolumeFabrique(C.PAS_UM, obliquite_deg=35.0)
    nulle = VolumeFabriqueAvecFaille(C.PAS_UM, 0.0, 2000.0, obliquite_deg=35.0)
    v("une faille NULLE rend la pile intacte", np.allclose(intacte.lire(p), nulle.lire(p)))
    demi_f = VolumeFabriqueAvecFaille(C.PAS_UM, 0.5 * C.PAS_UM, 2000.0, obliquite_deg=35.0)
    ecart = np.abs(demi_f.lire(p) - intacte.lire(p))
    v("... alors qu'une demi-feuille change la matière", ecart.max() > 1.0,
      f"{ecart.max():.3f}")
    # ⭐⭐⭐⭐ LE FAIT DU FICHIER : un saut d'UNE feuille rend la matière identique, parce que le
    # saut est une phase et que la phase est périodique.
    # ⚠⚠ ET CE N'EST PAS « IDENTIQUE AU BIT PRÈS », ce que j'avais d'abord écrit : additionner un
    # pas à une projection de plusieurs milliers de microns arrondit, donc il reste un résidu. Ce
    # qui est asserté est donc la SEPARATION — le résidu contre le signal d'une demi-feuille — et
    # pas une égalité exacte qu'un flottant ne peut pas tenir. Un seuil absolu ici serait un
    # nombre choisi pour que le calcul du jour passe.
    une_f = VolumeFabriqueAvecFaille(C.PAS_UM, C.PAS_UM, 2000.0, obliquite_deg=35.0)
    residu = float(np.abs(une_f.lire(p) - intacte.lire(p)).max())
    v("⭐ une faille d'UNE feuille laisse la matière inchangée à l'arrondi près",
      residu < float(ecart.max()) * 1e-9, f"résidu {residu:.3e} contre {ecart.max():.3f}")
    v("... et le résidu est sous le quantum d'une lecture entiere", residu < 1e-6,
      f"{residu:.3e}")
    deux = float(np.abs(VolumeFabriqueAvecFaille(C.PAS_UM, 2 * C.PAS_UM, 2000.0,
                                                 obliquite_deg=35.0).lire(p)
                        - intacte.lire(p)).max())
    v("... et DEUX feuilles aussi, donc c'est bien la périodicité",
      deux < float(ecart.max()) * 1e-9, f"{deux:.3e}")
    # ⚠ Sonde : le côté qui n'a pas bougé ne doit RIEN voir, sinon la faille serait globale.
    gauche = p[p[:, 0] <= 2000.0]
    v("le côté intact ne bouge pas", np.allclose(demi_f.lire(gauche), intacte.lire(gauche)))
    v("... et le côté rompu, lui, bouge",
      not np.allclose(demi_f.lire(p[p[:, 0] > 2000.0]), intacte.lire(p[p[:, 0] > 2000.0])))
    v("la faille garde la normale et le pas de la pile",
      demi_f.normale.tolist() == intacte.normale.tolist()
      and demi_f.pas_um == intacte.pas_um)
    v("le saut est rendu en feuilles", abs(demi_f.saut_en_feuilles - 0.5) < 1e-12)

    # ⭐⭐⭐⭐ ET L'INVISIBILITÉ N'EST PAS UNE AFFAIRE DE PAS CONSTANT, CE QUI ÉLARGIT LE FAIT.
    # Ce qui la cause est que la pile soit une fonction de la PHASE SEULE, périodique de période 1 :
    # `f(phase + 1) = f(phase)` quelle que soit la façon dont le pas varie avec la profondeur. La
    # pile à pas variable de `122` le vérifie — deux points distants d'exactement une feuille EN
    # PHASE y lisent la même chose — donc un rouleau dont l'espacement varie d'un facteur cinq
    # (`118`) ne porte pas davantage l'identité d'une feuille.
    from combien_de_pas_la_matiere_porte import VolumeFabriqueAPasVariable  # noqa: PLC0415

    dep = np.array([2000.0, 2000.0, 2000.0])
    proj0 = float(dep @ np.array([0.0, 0.0, 1.0])) * C.VOXEL_FIN_UM
    pv = VolumeFabriqueAPasVariable(C.PAS_UM, -0.04, proj0_um=proj0)
    a = pv.recale(dep)
    # ⚠ `recale` pose un point SUR une feuille ; le point posé sur la feuille suivante est celui
    # qu'on obtient en recalant un point déjà avancé d'environ un pas. Compter en microns le long
    # de la normale ne marcherait pas : sur une pile à pas variable une feuille ne mesure pas
    # partout la même chose, et c'est précisément le cas qu'on veut couvrir.
    b = pv.recale(a + pv.normale * (pv.pas_local_um(
        float(a @ pv.normale) * C.VOXEL_FIN_UM) / C.VOXEL_FIN_UM))
    ecart_vx = float(np.linalg.norm(b - a))
    v("les deux points sont bien une feuille plus loin", ecart_vx > 10.0, f"{ecart_vx:.1f} vx")
    v("⭐ sur une pile à PAS VARIABLE aussi, une feuille de décalage rend la même lecture",
      abs(float(pv.lire(a.reshape(1, 3))[0]) - float(pv.lire(b.reshape(1, 3))[0])) < 0.5,
      f"{float(pv.lire(a.reshape(1, 3))[0]):.3f} contre "
      f"{float(pv.lire(b.reshape(1, 3))[0]):.3f}")
    # ⚠ Sonde : une DEMI-feuille plus loin, la lecture doit être franchement différente, sinon
    # le contrôle ci-dessus serait satisfait par une pile qui rend la même chose partout.
    c_ = a + pv.normale * (0.5 * pv.pas_local_um(
        float(a @ pv.normale) * C.VOXEL_FIN_UM) / C.VOXEL_FIN_UM)
    v("... alors qu'une demi-feuille plus loin, non",
      abs(float(pv.lire(a.reshape(1, 3))[0]) - float(pv.lire(c_.reshape(1, 3))[0])) > 50.0,
      f"{float(pv.lire(c_.reshape(1, 3))[0]):.3f}")

    ex = la_faille_existe_t_elle(sauts=(0.5, 1.0), points=400, graine=5)
    v("l'existence est mesurée pour chaque taille", len(ex) == 2)
    v("... une demi-feuille existe", ex[0]["la_matiere_change"])
    v("... une feuille entière n'existe pas", not ex[1]["la_matiere_change"],
      f"{ex[1]['ecart_maximal']}")

    # ⚠ Les points doivent tomber DES DEUX CÔTÉS, sinon toute faille paraîtrait nulle.
    ex0 = la_faille_existe_t_elle(sauts=(0.5,), points=400, graine=5)
    v("les points d'épreuve traversent le plan", ex0[0]["ecart_maximal"] > 1.0)

    # ⭐⭐⭐ Le verdict croisé, sondé sur des moitiés fabriquées : il doit distinguer « la matière
    # ne change pas » de « le lecteur ne voit rien », qui se ressemblent dans un tableau.
    def _sig(p_val, ecart):
        return {"par_saut": [{"saut_en_feuilles": 1.0, "par_distance": [
            {"distance_vx": 10, "dans_le_cube": True,
             "desaccord_des_moities_deg_pire": {"rompue": 86.2, "intacte": 5.0,
                                                "ecart_median": ecart, "p": p_val}}]}]}

    inex = [{"saut_en_feuilles": 1.0, "saut_um": 173.0, "ecart_maximal": 0.0,
             "ecart_median": 0.0, "la_matiere_change": False}]
    exi = [{**inex[0], "ecart_maximal": 12.0, "la_matiere_change": True}]
    j = juger(inex, _sig(0.0001, -0.2))["par_saut"][0]
    v("⭐ une faille inexistante est dite INVISIBLE PAR CONSTRUCTION",
      j["invisible_par_construction"] and not j["la_faille_se_dit"])
    j = juger(exi, _sig(0.0001, -0.2))["par_saut"][0]
    v("... une faille réelle et vue est dite vue", j["la_faille_se_dit"])
    j = juger(exi, _sig(0.5, -0.2))["par_saut"][0]
    v("... une faille réelle et NON vue est dite non vue, pas inexistante",
      not j["la_faille_se_dit"] and not j["invisible_par_construction"])
    j = juger(exi, _sig(None, 0.0))["par_saut"][0]
    v("... et un p ABSENT ne compte pas comme une vue", not j["la_faille_se_dit"])

    # ⭐⭐⭐ La sonde des rangs sur DEUX graines : elle doit voir des refus, les situer, et rendre
    # l'excursion des deux côtés. ⚠ Sans le témoin intact, « la marche s'éloigne » ne distingue
    # pas une éjection d'un vagabondage ordinaire.
    o_ = ou_tombe_le_pas_refuse(graines=(3, 11), pas=8)
    v("la sonde des rangs voit des refus", o_["refus"] >= 1, f"{o_['refus']}")
    v("... et elle les situe", len(o_["rangs"]) == o_["refus"])
    v("... et elle rend l'excursion des DEUX piles",
      o_["excursion_laterale_mediane_vx"] is not None
      and o_["excursion_laterale_intacte_mediane_vx"] is not None)
    q_ = o_["au_premier_pas"]
    v("⭐ au premier pas, la marche part perpendiculairement au plan de faille",
      q_["part_perpendiculaire_au_plan"] > 0.9, f"{q_['part_perpendiculaire_au_plan']}")
    v("... alors que sur pile intacte elle n'a aucune raison d'y aller",
      q_["part_perpendiculaire_au_plan_intacte"] < 0.2,
      f"{q_['part_perpendiculaire_au_plan_intacte']}")
    v("... et le désaccord y dépasse franchement celui de la pile intacte",
      q_["desaccord_deg"] > 4.0 * q_["desaccord_deg_intact"],
      f"{q_['desaccord_deg']} contre {q_['desaccord_deg_intact']}")
    v("... et la pile intacte s'éloigne moins que la pile rompue",
      o_["excursion_laterale_intacte_mediane_vx"] < o_["excursion_laterale_mediane_vx"],
      f"{o_['excursion_laterale_intacte_mediane_vx']} contre "
      f"{o_['excursion_laterale_mediane_vx']}")

    v("une série dégénérée ne rend pas un p", _wilcoxon([0.0] * 8) is None)
    v("... alors qu'une série réelle en rend un", _wilcoxon([0.3] * 8) is not None)

    # ⚠ Une marche doit réellement avancer sur la pile rompue, sinon tout écart mesuré serait
    # celui d'une marche qui n'a pas eu lieu.
    o = _outils(20)
    cote = int(4000 + 8 * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    pile = VolumeFabriqueAvecFaille(C.PAS_UM, 0.5 * C.PAS_UM, 2000.0, obliquite_deg=35.0,
                                    bruit=8.0, graine=3, forme=(cote, cote, cote))
    m = _une_marche(o, pile, np.array([2010.0, 2000.0, 2000.0]), 6, 20)
    v("une marche avance sur la pile rompue", m["pas"] >= 3, f"{m['pas']}")
    v("... et rend une médiane pour chaque signal",
      all(m[nom] is not None for nom in SIGNAUX))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--pas", type=int, default=PAS)
    p.add_argument("--graines", type=int, default=len(GRAINES))
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(pas=a.pas, graines=GRAINES[:a.graines])
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
