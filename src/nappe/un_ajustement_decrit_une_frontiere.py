"""Un ajustement décrit UNE frontière — et la fenêtre de la campagne en contient trois.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `174` livre une recette réparée qui tombe exactement sur la frontière
d'une marche, et `R4-P30` demande pourquoi elle décroche à sept longueurs sur huit. L'hypothèse
inscrite dans la porte était que le profil d'intensité de la feuille abaisse la cohérence près d'un
interstice. ✗ **Elle est réfutée d'entrée : la cohérence vaut un partout sur cette fixture.**

⭐⭐⭐⭐ LA CAUSE EST STRUCTURELLE ET ELLE EST DANS LE NOM. Un ajustement en DEUX segments décrit UNE
frontière. À une frontière il est exact — part atteinte un, et la coupe tombe dessus. Dès deux, il
n'a plus de modèle : aucune paire de segments ne décrit trois blocs homogènes, et la part atteinte
le DIT. Ce n'est donc pas un défaut de la recette, c'est sa définition.

⚠⚠⚠ ET C'EST L'INVERSE DE L'EXPLICATION Nº 3 DE `14` : la fenêtre de la campagne — **109** couches
à 2,4 µm, soit **1,512** feuille — n'est pas trop COURTE pour porter une bascule, elle est trop
LONGUE pour qu'une description en deux segments s'y applique. Elle contient plusieurs frontières.

⚠⚠ UNE PART ATTEINTE DE UN NE SUFFIT PAS, ET LA MESURE LE MONTRE : une fenêtre qui ne contient
AUCUNE frontière rend elle aussi un — l'ajustement y coupe n'importe où et les deux parts sont
homogènes. Ce qui sépare « une frontière trouvée » de « rien à trouver » est la BASCULE, et les deux
conditions sont donc exigées ensemble.

⚠ CONTRÔLE OBLIGATOIRE : le nombre de frontières d'une fenêtre est lu sur la FIXTURE elle-même,
par `angle_du_pli_deg`, jamais recalculé ici. Deux réponses à « où le pli change » seraient deux
géométries, et la relation mesurée porterait sur leur désaccord.

Usage :
    uv run python src/nappe/un_ajustement_decrit_une_frontiere.py --verifier
    uv run python src/nappe/un_ajustement_decrit_une_frontiere.py \\
        --json docs/mesures/un_ajustement_decrit_une_frontiere.json
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

from la_coupe_cherchee_trouve_t_elle_la_frontiere import (  # noqa: E402
    ANGLE_DU_PREMIER_PLI_DEG, COUCHES_DE_LA_CAMPAGNE, la_coupe_par_ajustement)
from quelle_fenetre_lit_une_bascule import (LONGUEUR_DE_FIBRE_UM,  # noqa: E402
                                            courbe_de_la_fixture)

DECALAGES = 12
CONTRASTE = 0.5
LONGUEURS_EN_FEUILLES = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0)
# ⚠ Le balayage fin cherche la fenetre UTILE : assez longue pour que le temoin des deux cotes soit
# lisible, assez courte pour ne porter qu'une frontiere. Les bornes sont larges expres — c'est la
# mesure qui doit dire ou elle se ferme, pas le balayage.
COUCHES_FINES = tuple(range(16, 45, 2))


def _volume(voxel_um: float, pas_um: float, plis: int = 2):
    from combien_de_pas_la_matiere_porte import VolumeFabriqueAFibres  # noqa: PLC0415

    return VolumeFabriqueAFibres(
        pas_um, longueur_de_fibre_um=LONGUEUR_DE_FIBRE_UM, contraste_des_fibres=CONTRASTE,
        angle_du_premier_pli_deg=ANGLE_DU_PREMIER_PLI_DEG, plis_par_feuille=int(plis),
        voxel_um=voxel_um, forme=(4000, 4000, 4000))


def frontieres_de_la_fenetre(couches: int, decalage_um: float, voxel_um: float,
                             pas_um: float, plis: int = 2) -> list[int]:
    """Les couches où le pli change, lues sur la FIXTURE et jamais recalculées.

    ⚠⚠ C'EST `angle_du_pli_deg` QUI REPOND, pas une arithmetique ecrite ici. Deux reponses a « ou
    le pli change » seraient deux geometries, et la relation mesuree porterait sur leur desaccord
    plutot que sur l'ajustement.

    ⚠ La profondeur d'une couche se compte depuis le DEBUT de la fenetre, decalage compris : c'est
    ainsi que `courbe_de_la_fixture` echantillonne, et lire autrement compterait les frontieres
    d'une autre fenetre.
    """
    vol = _volume(voxel_um, pas_um, plis)
    prof = (float(decalage_um) + np.arange(int(couches)) * float(voxel_um)) / float(pas_um)
    feuille = np.floor(prof)
    angles = vol.angle_du_pli_deg(feuille, prof - feuille)
    return [int(i) for i in range(1, int(couches)) if float(angles[i]) != float(angles[i - 1])]


def une_cellule(couches: int, decalage_um: float, voxel_um: float, pas_um: float,
                plis: int = 2) -> dict:
    """Une fenêtre : combien de frontières elle contient, et ce que l'ajustement y rend."""
    fr = frontieres_de_la_fenetre(couches, decalage_um, voxel_um, pas_um, plis)
    c = courbe_de_la_fixture(couches, decalage_um, CONTRASTE, plis, voxel_um, pas_um)
    aj = la_coupe_par_ajustement(c)
    # ⚠⚠⚠ UNE FRONTIERE TROP PRES DU BORD N'EST PAS ATTEIGNABLE, ET LA BORNE SE DERIVE : le temoin
    # exige quatre couches dans CHAQUE MOITIE de CHAQUE part, donc une coupe vaut au moins huit et
    # au plus `couches - 8`. Une frontiere hors de cet intervalle ne peut pas etre trouvee, quelle
    # que soit la qualite de l'ajustement — et la compter comme un echec de la recette ferait lire
    # une contrainte de fenetre comme un defaut d'instrument.
    atteignables = [int(x) for x in fr if 8 <= int(x) <= int(couches) - 8]
    out = {"couches": int(couches), "decalage_um": round(float(decalage_um), 3),
           "frontieres": [int(x) for x in fr], "combien_de_frontieres": len(fr),
           "frontieres_atteignables": atteignables,
           "combien_datteignables": len(atteignables),
           "lisible": aj is not None}
    if aj is None:
        return out
    ecart = (min(abs(aj["coupe"] - x) for x in atteignables) if atteignables else None)
    out.update({"coupe": int(aj["coupe"]), "part_atteinte": aj["part_atteinte"],
                "bascule_deg": aj["bascule_deg"], "temoin_deg": aj["temoin_deg"],
                "ecart_a_la_frontiere_la_plus_proche": ecart,
                "la_coupe_tombe_sur_une_frontiere": bool(ecart is not None and ecart <= 1),
                "la_bascule_depasse_le_temoin": aj["la_bascule_depasse_le_temoin"],
                # ⚠⚠ LES DEUX CONDITIONS ENSEMBLE. Une fenetre SANS frontiere rend elle aussi une
                # part atteinte de un — l'ajustement y coupe n'importe ou et les deux parts sont
                # homogenes — donc la part seule ne distingue pas « trouvee » de « rien a trouver ».
                "elle_lit_une_frontiere": bool(
                    ecart is not None and ecart <= 1 and aj["la_bascule_depasse_le_temoin"])})
    return out


def balayer(voxel_um: float, pas_um: float, longueurs=LONGUEURS_EN_FEUILLES,
            decalages: int = DECALAGES, plis: int = 2) -> dict:
    """La grille longueur × décalage, avec le nombre de frontières de chaque fenêtre."""
    cellules = []
    for f in longueurs:
        couches = max(16, int(round(float(f) * float(pas_um) / float(voxel_um))))
        for k in range(int(decalages)):
            dec = float(pas_um) * k / float(decalages)
            cellules.append({"demande_en_feuilles": float(f),
                             **une_cellule(couches, dec, voxel_um, pas_um, plis)})
    return {"decidable": bool(cellules), "cellules": cellules,
            "longueurs": [float(f) for f in longueurs], "decalages": int(decalages)}


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def la_relation(grille: dict) -> dict:
    """La part atteinte, groupée par NOMBRE DE FRONTIÈRES dans la fenêtre.

    ⭐⭐⭐⭐ C'EST L'ÉNONCÉ DE LA TRANCHE, ET IL EST ORDINAL. On ne demande pas si la part est
    « grande » : on demande si elle vaut un tant qu'il y a au plus une frontière, et si elle tombe
    dès qu'il y en a deux. Aucun seuil n'y entre, et le groupe est lu sur la fixture.
    """
    # ⚠⚠⚠ LA RELATION NE PORTE QUE SUR LES FENETRES DONT TOUTES LES FRONTIERES SONT ATTEIGNABLES,
    # et la restriction est dite. Une frontiere trop pres du bord fait chuter la part pour une
    # raison de FENETRE et non de modele ; les melanger ferait lire une contrainte geometrique
    # comme un defaut de l'ajustement. Les cellules ecartees sont comptees a cote.
    par = {}
    ecartees = 0
    for c in grille["cellules"]:
        if c["combien_datteignables"] != c["combien_de_frontieres"]:
            ecartees += 1
            continue
        cle = c["combien_de_frontieres"]
        if not c.get("lisible"):
            par.setdefault(cle, {"illisibles": 0, "parts": [], "sur": 0, "cellules": 0})
            par[cle]["illisibles"] += 1
            par[cle]["cellules"] += 1
            continue
        d = par.setdefault(cle, {"illisibles": 0, "parts": [], "sur": 0, "cellules": 0})
        d["cellules"] += 1
        d["parts"].append(c["part_atteinte"])
        d["sur"] += int(c["la_coupe_tombe_sur_une_frontiere"])
    lignes = []
    for n in sorted(par):
        d = par[n]
        lignes.append({"frontieres": int(n), "cellules": d["cellules"],
                       "illisibles": d["illisibles"], "lisibles": len(d["parts"]),
                       "part_mediane": _med(d["parts"]),
                       "part_minimale": round(min(d["parts"]), 3) if d["parts"] else None,
                       "coupes_sur_une_frontiere": d["sur"],
                       "toutes_les_parts_valent_un": bool(
                           d["parts"] and all(x == 1.0 for x in d["parts"]))})
    a_une = [x for x in lignes if x["frontieres"] <= 1]
    au_dela = [x for x in lignes if x["frontieres"] >= 2]
    return {"decidable": bool(lignes), "lignes": lignes,
            "cellules_ecartees_car_une_frontiere_est_hors_datteinte": int(ecartees),
            "jusqua_une_frontiere_la_part_vaut_un": bool(
                a_une and all(x["toutes_les_parts_valent_un"] for x in a_une)),
            "au_dela_elle_decroche": bool(
                au_dela and all(not x["toutes_les_parts_valent_un"] for x in au_dela)),
            "part_mediane_a_une_frontiere": next(
                (x["part_mediane"] for x in lignes if x["frontieres"] == 1), None),
            "part_mediane_a_deux_frontieres": next(
                (x["part_mediane"] for x in lignes if x["frontieres"] == 2), None)}


def ou_tombe_la_coupe(grille: dict) -> dict:
    """Quand la fenêtre porte exactement UNE frontière atteignable, la coupe tombe-t-elle dessus ?

    ⭐⭐⭐⭐ C'EST UNE AUTRE QUESTION QUE LA PART ATTEINTE, ET ELLE SE GROUPE AUTREMENT. La part dit
    si DEUX SEGMENTS décrivent la fenêtre ; celle-ci dit si la coupe trouve la frontière quand il
    n'y en a qu'une à trouver. Les mélanger ferait répondre à l'une avec le groupe de l'autre.

    ⚠ « Atteignable » est dérivé du témoin : une coupe vaut au moins huit et au plus `couches − 8`,
    parce que le témoin exige quatre couches dans chaque moitié de chaque part.
    """
    une = [c for c in grille["cellules"]
           if c["combien_datteignables"] == 1 and c.get("lisible")]
    return {"decidable": bool(une), "cellules": len(une),
            "coupes_sur_la_frontiere": int(sum(1 for c in une
                                               if c["la_coupe_tombe_sur_une_frontiere"])),
            "ecart_median": _med([c["ecart_a_la_frontiere_la_plus_proche"] for c in une
                                  if c["ecart_a_la_frontiere_la_plus_proche"] is not None]),
            "elle_tombe_toujours_dessus": bool(
                une and all(c["la_coupe_tombe_sur_une_frontiere"] for c in une))}


def sans_frontiere(grille: dict) -> dict:
    """Le contrôle qui sépare « trouvée » de « rien à trouver ».

    ⚠⚠⚠ UNE FENÊTRE SANS FRONTIÈRE REND UNE PART ATTEINTE DE UN. C'est pour cela que la part seule
    ne conclut pas : ce qui la sépare d'une frontière trouvée est la BASCULE, qui y vaut zéro. Sans
    ce contrôle, « part atteinte un » se lirait comme une réussite partout où la matière est
    homogène.
    """
    vides = [c for c in grille["cellules"]
             if c["combien_datteignables"] == 0 and c.get("lisible")]
    return {"decidable": bool(vides), "cellules": len(vides),
            "part_mediane": _med([c["part_atteinte"] for c in vides]),
            "bascule_mediane_deg": _med([c["bascule_deg"] for c in vides]),
            "combien_lisent_une_frontiere": int(sum(1 for c in vides
                                                    if c["elle_lit_une_frontiere"])),
            "aucune_ne_lit_de_frontiere": bool(
                vides and not any(c["elle_lit_une_frontiere"] for c in vides))}


def la_fenetre_utile(voxel_um: float, pas_um: float, couches=COUCHES_FINES,
                     decalages: int = DECALAGES, plis: int = 2) -> dict:
    """Y a-t-il une longueur qui, à TOUS les décalages, porte une frontière ET la trouve ?

    ⭐⭐⭐⭐ LA FENÊTRE UTILE EST BORNÉE DES DEUX CÔTÉS, et les deux bornes se DÉRIVENT. Trop courte,
    une part n'a pas les quatre couches que le témoin exige de chaque moitié ; trop longue, la
    fenêtre porte plus d'une frontière et deux segments ne la décrivent plus. Le balayage ne choisit
    rien : il dit où elle se ferme.

    ⚠⚠ « À TOUS LES DÉCALAGES » est la forme jointe du dépôt, et elle est ici obligatoire : la phase
    de la fenêtre dans la feuille n'est pas connue sur données réelles.
    """
    lignes = []
    for n in couches:
        cellules = [une_cellule(int(n), float(pas_um) * k / float(decalages), voxel_um, pas_um,
                                plis) for k in range(int(decalages))]
        une_seule = [c for c in cellules if c["combien_datteignables"] == 1]
        lisent = [c for c in cellules if c.get("elle_lit_une_frontiere")]
        lignes.append({
            "couches": int(n), "epaisseur_um": round(float(n) * voxel_um, 1),
            "en_plis": round(float(n) * voxel_um / (float(pas_um) / float(plis)), 3),
            "decalages": int(decalages),
            "avec_une_seule_frontiere": len(une_seule),
            "avec_plusieurs": int(sum(1 for c in cellules
                                      if c["combien_datteignables"] >= 2)),
            "sans_frontiere": int(sum(1 for c in cellules
                                      if c["combien_datteignables"] == 0)),
            "illisibles": int(sum(1 for c in cellules if not c.get("lisible"))),
            "lisent_une_frontiere": len(lisent),
            # ⚠⚠ UNE LONGUEUR EST UTILE QUAND CHAQUE DECALAGE PORTE EXACTEMENT UNE FRONTIERE ET LA
            # TROUVE. Une fenetre qui n'en porte aucune a certains decalages n'est pas fautive, mais
            # elle ne lit rien la : elle ne peut donc pas servir seule.
            "elle_est_utile": bool(len(une_seule) == int(decalages)
                                   and len(lisent) == int(decalages))})
    utiles = [x["couches"] for x in lignes if x["elle_est_utile"]]
    return {"decidable": bool(lignes), "lignes": lignes, "longueurs_utiles": utiles,
            "la_plus_courte_utile": min(utiles) if utiles else None,
            "la_plus_longue_utile": max(utiles) if utiles else None}


def le_recouvrement(voxel_um: float, pas_um: float, couches=COUCHES_FINES,
                    decalages: int = DECALAGES, plis: int = 2) -> dict:
    """DEUX fenêtres décalées d'une demi-longueur suffisent-elles là où une seule échoue ?

    ⭐⭐⭐⭐ C'EST LA MOITIÉ CONSTRUCTIVE. Une fenêtre unique échoue à certains décalages non parce
    que la matière n'a pas de frontière, mais parce que la frontière y tombe trop près d'un bord.
    Deux fenêtres décalées d'une DEMI-LONGUEUR mettent ce bord au milieu de l'autre : ce qui est
    hors d'atteinte pour l'une ne l'est pas pour l'autre.

    ⚠⚠ LE DÉCALAGE EST DÉRIVÉ, PAS CHOISI : une demi-longueur est la seule valeur qui envoie
    exactement le bord d'une fenêtre au centre de la suivante. Un autre pas laisserait une bande où
    aucune des deux ne peut lire, et il faudrait alors justifier ce pas plutôt que cette bande.

    ⚠ On compte un décalage comme lu dès qu'UNE des deux fenêtres y lit une frontière — c'est ce
    qu'un recouvrement veut dire — et jamais leur moyenne.
    """
    lignes = []
    for n in couches:
        lus = 0
        for k in range(int(decalages)):
            dec = float(pas_um) * k / float(decalages)
            a = une_cellule(int(n), dec, voxel_um, pas_um, plis)
            b = une_cellule(int(n), dec + float(n) * voxel_um / 2.0, voxel_um, pas_um, plis)
            lus += int(bool(a.get("elle_lit_une_frontiere") or b.get("elle_lit_une_frontiere")))
        lignes.append({"couches": int(n), "decalages": int(decalages),
                       "decalage_de_la_seconde_um": round(float(n) * voxel_um / 2.0, 1),
                       "decalages_lus": int(lus),
                       "elles_lisent_partout": bool(lus == int(decalages))})
    bonnes = [x["couches"] for x in lignes if x["elles_lisent_partout"]]
    return {"decidable": bool(lignes), "lignes": lignes, "longueurs_qui_couvrent": bonnes,
            "la_plus_courte_qui_couvre": min(bonnes) if bonnes else None}


def la_fenetre_de_la_campagne(voxel_um: float, pas_um: float,
                              couches: int = COUCHES_DE_LA_CAMPAGNE,
                              decalages: int = DECALAGES, plis: int = 2) -> dict:
    """Combien de frontières la fenêtre de `14` porte, et ce que l'ajustement y rend.

    ⚠⚠⚠ C'EST LA JONCTION, ET ELLE RETOURNE L'EXPLICATION Nº 3 DE `14` : la fenêtre n'est pas trop
    COURTE pour porter une bascule, elle est trop LONGUE pour qu'une description en deux segments
    s'y applique.
    """
    cellules = [une_cellule(int(couches), float(pas_um) * k / float(decalages), voxel_um, pas_um,
                            plis) for k in range(int(decalages))]
    combien = [c["combien_datteignables"] for c in cellules]
    lisibles = [c for c in cellules if c.get("lisible")]
    return {"decidable": bool(cellules), "couches": int(couches),
            "epaisseur_um": round(float(couches) * voxel_um, 1),
            "en_feuilles": round(float(couches) * voxel_um / float(pas_um), 3),
            "en_plis": round(float(couches) * voxel_um / (float(pas_um) / float(plis)), 3),
            "decalages": int(decalages),
            "frontieres_minimum": int(min(combien)), "frontieres_maximum": int(max(combien)),
            "part_mediane": _med([c["part_atteinte"] for c in lisibles]),
            "lisent_une_frontiere": int(sum(1 for c in cellules
                                            if c.get("elle_lit_une_frontiere"))),
            "elle_porte_plus_dune_frontiere": bool(min(combien) >= 2)}


def juger(relation: dict, vide: dict, utile: dict, campagne: dict,
          ou: dict | None = None, recouvrement: dict | None = None) -> dict:
    """Ce que les quatre mesures disent ensemble, sans les fondre en un chiffre."""
    return {
        "decidable": bool(relation.get("decidable") and campagne.get("decidable")),
        "jusqua_une_frontiere_la_part_vaut_un": bool(
            relation.get("jusqua_une_frontiere_la_part_vaut_un")),
        "au_dela_elle_decroche": bool(relation.get("au_dela_elle_decroche")),
        "part_mediane_a_une_frontiere": relation.get("part_mediane_a_une_frontiere"),
        "part_mediane_a_deux_frontieres": relation.get("part_mediane_a_deux_frontieres"),
        "une_fenetre_sans_frontiere_rend_une_part_de_un": bool(
            vide.get("decidable") and vide.get("part_mediane") == 1.0),
        "et_elle_ne_lit_pourtant_aucune_frontiere": bool(vide.get("aucune_ne_lit_de_frontiere")),
        "longueurs_utiles": utile.get("longueurs_utiles") or [],
        "longueurs_qui_couvrent_a_deux_fenetres": (recouvrement or {}).get(
            "longueurs_qui_couvrent") or [],
        "la_plus_courte_qui_couvre": (recouvrement or {}).get("la_plus_courte_qui_couvre"),
        "la_fenetre_de_la_campagne_en_plis": campagne.get("en_plis"),
        "frontieres_de_la_campagne": [campagne.get("frontieres_minimum"),
                                      campagne.get("frontieres_maximum")],
        "la_campagne_porte_plus_dune_frontiere": bool(
            campagne.get("elle_porte_plus_dune_frontiere")),
        # ⚠⚠⚠ LE VERDICT EST JOINT ET IL A TROIS MOITIES : la part vaut un jusqu'a une frontiere,
        # elle decroche au-dela, et la fenetre de la campagne en porte plus d'une. La premiere sans
        # la deuxieme ne dirait pas que c'est structurel ; les deux sans la troisieme ne diraient
        # rien de `14`.
        # ⚠⚠ DEUX QUESTIONS DIFFERENTES, DEUX GROUPES : la part atteinte dit si DEUX SEGMENTS
        # decrivent la fenetre ; celle-ci dit si la coupe trouve la frontiere quand il n'y en a
        # qu'une a trouver. Les fondre ferait repondre a l'une avec le groupe de l'autre.
        "la_coupe_tombe_toujours_sur_la_frontiere_unique": bool(
            (ou or {}).get("elle_tombe_toujours_dessus")),
        "cellules_sur_une_frontiere_unique": (ou or {}).get("cellules"),
        "un_ajustement_decrit_une_frontiere": bool(
            relation.get("jusqua_une_frontiere_la_part_vaut_un")
            and relation.get("au_dela_elle_decroche")
            and campagne.get("elle_porte_plus_dune_frontiere"))}


def mesurer() -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = C.VOXEL_FIN_UM, C.PAS_UM
    grille = balayer(vx, pas)
    relation = la_relation(grille)
    vide = sans_frontiere(grille)
    ou = ou_tombe_la_coupe(grille)
    utile = la_fenetre_utile(vx, pas)
    recouvrement = le_recouvrement(vx, pas)
    campagne = la_fenetre_de_la_campagne(vx, pas)
    return {"voxel_um": float(vx), "pas_um": float(pas),
            "couches_par_pli": round(float(pas) / 2.0 / float(vx), 1),
            "la_grille": grille, "la_relation": relation, "sans_frontiere": vide,
            "ou_tombe_la_coupe": ou,
            "la_fenetre_utile": utile, "le_recouvrement": recouvrement,
            "la_campagne": campagne,
            "le_verdict": juger(relation, vide, utile, campagne, ou, recouvrement)}


def afficher(r: dict) -> None:
    rel, vi, ut, ca, v = (r["la_relation"], r["sans_frontiere"], r["la_fenetre_utile"],
                          r["la_campagne"], r["le_verdict"])
    print("UN AJUSTEMENT DÉCRIT UNE FRONTIÈRE")
    print(f"  pas {r['pas_um']} µm, voxel {r['voxel_um']} µm → un pli = "
          f"{r['couches_par_pli']} couches")
    print()
    print("  LA RELATION · la part atteinte, groupée par nombre de frontières dans la fenêtre")
    for x in rel["lignes"]:
        marq = "★" if x["toutes_les_parts_valent_un"] else "✗"
        print(f"   {marq} {x['frontieres']} frontière(s) · {x['cellules']:>3} cellules "
              f"({x['illisibles']} illisibles) · part médiane {str(x['part_mediane']):>6} "
              f"(min {str(x['part_minimale']):>6}) · coupes sur une frontière "
              f"{x['coupes_sur_une_frontiere']}/{x['lisibles']}")
    print(f"   ★ jusqu'à une frontière la part vaut un : "
          f"{rel['jusqua_une_frontiere_la_part_vaut_un']} · au-delà elle décroche : "
          f"{rel['au_dela_elle_decroche']}")
    print()
    print(f"  SANS FRONTIÈRE · {vi['cellules']} cellules · part médiane {vi['part_mediane']} · "
          f"bascule médiane {vi['bascule_mediane_deg']}°")
    marq = "★" if vi["aucune_ne_lit_de_frontiere"] else "✗"
    print(f"   {marq} et pourtant AUCUNE ne lit de frontière : "
          f"{vi['combien_lisent_une_frontiere']}/{vi['cellules']}")
    print()
    print("  LA FENÊTRE UTILE · bornée des deux côtés")
    for x in ut["lignes"]:
        marq = "★" if x["elle_est_utile"] else "✗"
        print(f"   {marq} {x['couches']:>3} couches ({x['epaisseur_um']:>6.1f} µm, "
              f"{x['en_plis']:.2f} pli) · une seule frontière "
              f"{x['avec_une_seule_frontiere']:>2}/{x['decalages']} · plusieurs "
              f"{x['avec_plusieurs']:>2} · aucune {x['sans_frontiere']:>2} · illisibles "
              f"{x['illisibles']:>2} · lisent {x['lisent_une_frontiere']:>2}")
    print(f"   ★ longueurs utiles : {ut['longueurs_utiles']}")
    print()
    rc = r.get("le_recouvrement") or {}
    print()
    print("  LE RECOUVREMENT · deux fenêtres décalées d'une demi-longueur")
    for x in rc.get("lignes", []):
        marq = "★" if x["elles_lisent_partout"] else "✗"
        print(f"   {marq} {x['couches']:>3} couches · seconde à "
              f"{x['decalage_de_la_seconde_um']:>6.1f} µm · lues "
              f"{x['decalages_lus']:>2}/{x['decalages']}")
    print(f"   ★ longueurs qui couvrent : {rc.get('longueurs_qui_couvrent')}")
    print()
    print(f"  LA CAMPAGNE · {ca['couches']} couches = {ca['epaisseur_um']} µm = "
          f"{ca['en_feuilles']} feuille = {ca['en_plis']} pli")
    marq = "✗" if ca["elle_porte_plus_dune_frontiere"] else "★"
    print(f"   {marq} elle porte entre {ca['frontieres_minimum']} et "
          f"{ca['frontieres_maximum']} frontières · part médiane {ca['part_mediane']} · "
          f"lisent {ca['lisent_une_frontiere']}/{ca['decalages']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("jusqua_une_frontiere_la_part_vaut_un", "au_dela_elle_decroche",
                "longueurs_qui_couvrent_a_deux_fenetres", "la_plus_courte_qui_couvre",
                "part_mediane_a_une_frontiere", "part_mediane_a_deux_frontieres",
                "une_fenetre_sans_frontiere_rend_une_part_de_un",
                "et_elle_ne_lit_pourtant_aucune_frontiere", "longueurs_utiles",
                "la_fenetre_de_la_campagne_en_plis", "frontieres_de_la_campagne",
                "la_campagne_porte_plus_dune_frontiere",
                "un_ajustement_decrit_une_frontiere"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415
    vx, pas = C.VOXEL_FIN_UM, C.PAS_UM
    pli = pas / 2.0 / vx

    # ---- les frontieres sont lues sur la FIXTURE
    # ⚠⚠ L'ATTENDU SE DERIVE DE LA GEOMETRIE : un pli fait `pas/2` micrometres, donc une fenetre de
    # `n` couches en traverse au plus `n·voxel/(pas/2)`, et jamais davantage.
    for n in (18, 36, 54, 109):
        pires = max(len(frontieres_de_la_fenetre(n, pas * k / 12.0, vx, pas))
                    for k in range(12))
        v(f"une fenêtre de {n} couches ne porte jamais plus de frontières que de demi-plis",
          pires <= int(np.ceil(n / pli)),
          f"{pires} au pire, plafond {int(np.ceil(n / pli))}")
    # ⚠ Une fenetre plus courte qu'un pli en porte au plus une.
    v("⚠ une fenêtre plus courte qu'un pli n'en porte jamais plus d'une",
      all(len(frontieres_de_la_fenetre(int(pli) - 2, pas * k / 12.0, vx, pas)) <= 1
          for k in range(12)))
    # ⚠⚠ ET ELLES VIENNENT DE `angle_du_pli_deg` : changer le nombre de plis change le compte.
    a_deux = len(frontieres_de_la_fenetre(72, 0.0, vx, pas, plis=2))
    a_quatre = len(frontieres_de_la_fenetre(72, 0.0, vx, pas, plis=4))
    v("⚠⚠ les frontières viennent de la fixture : quatre plis en donnent plus que deux",
      a_quatre > a_deux, f"{a_deux} à deux plis, {a_quatre} à quatre")

    # ---- une cellule, et les deux conditions
    une = une_cellule(54, 0.0, vx, pas)
    # ⚠⚠⚠ LA BORNE D'ATTEIGNABILITE SE VERIFIE PAR SA REGLE, des deux cotes : une frontiere a la
    # couche sept n'est pas atteignable, une a la couche huit l'est.
    bords = une_cellule(54, 0.0, vx, pas)
    v("⚠⚠⚠ une frontière hors de [8, couches − 8] n'est pas atteignable",
      [x for x in range(54) if 8 <= x <= 46] and
      all((8 <= x <= 54 - 8) == (x in bords["frontieres_atteignables"])
          for x in bords["frontieres"]),
      f"frontières {bords['frontieres']}, atteignables {bords['frontieres_atteignables']}")
    proche = next((une_cellule(54, pas * k / 24.0, vx, pas) for k in range(24)
                   if une_cellule(54, pas * k / 24.0, vx, pas)["frontieres"]
                   and min(une_cellule(54, pas * k / 24.0, vx, pas)["frontieres"]) < 8), None)
    v("... et il existe un décalage où une frontière tombe hors d'atteinte",
      proche is not None and proche["combien_datteignables"] < proche["combien_de_frontieres"],
      f"{proche and proche['frontieres']} dont {proche and proche['frontieres_atteignables']}")
    v("⭐⭐⭐⭐ à UNE frontière, la part vaut un et la coupe tombe dessus",
      une["combien_de_frontieres"] == 1 and une["part_atteinte"] == 1.0
      and une["la_coupe_tombe_sur_une_frontiere"] and une["elle_lit_une_frontiere"],
      f"{une['combien_de_frontieres']} frontière(s), part {une.get('part_atteinte')}, coupe "
      f"{une.get('coupe')} pour {une['frontieres']}")
    # ⚠⚠⚠ LE CONTROLE QUI SEPARE « TROUVEE » DE « RIEN A TROUVER ».
    vide = une_cellule(18, 0.0, vx, pas)
    v("⚠⚠⚠ une fenêtre SANS frontière rend elle aussi une part de un",
      vide["combien_de_frontieres"] == 0 and vide["part_atteinte"] == 1.0,
      f"part {vide.get('part_atteinte')}, bascule {vide.get('bascule_deg')}°")
    v("... mais sa BASCULE vaut zéro, donc elle ne lit aucune frontière",
      vide["bascule_deg"] == 0.0 and not vide["elle_lit_une_frontiere"])

    # ---- la relation, sur une grille reduite
    g = balayer(vx, pas, longueurs=(0.5, 0.75, 1.5), decalages=6)
    rel = la_relation(g)
    v("la relation groupe les cellules par nombre de frontières",
      rel["decidable"] and {x["frontieres"] for x in rel["lignes"]} >= {1, 2},
      f"{[x['frontieres'] for x in rel['lignes']]}")
    v("⭐⭐⭐⭐ jusqu'à une frontière la part vaut un, et au-delà elle décroche",
      rel["jusqua_une_frontiere_la_part_vaut_un"] and rel["au_dela_elle_decroche"],
      f"part à une {rel['part_mediane_a_une_frontiere']}, à deux "
      f"{rel['part_mediane_a_deux_frontieres']}")
    vi = sans_frontiere(g)
    v("⚠ le contrôle sans frontière ne lit jamais de frontière",
      not vi["decidable"] or vi["aucune_ne_lit_de_frontiere"],
      f"{vi.get('combien_lisent_une_frontiere')}/{vi.get('cellules')}")
    # ⚠⚠⚠ TROIS SONDES SONT PASSEES AU VERT, ET CES TROIS CONTROLES SONT CE QUI LES FAIT TOMBER.
    # Chacune portait sur une condition qui ne retirait RIEN sur les cellules assertees : une
    # condition qui n'ecarte jamais rien est une condition que rien ne teste. Ce qui se verifie ici
    # n'est donc pas une valeur mais le fait que la condition TRAVAILLE.
    lisibles = [c for c in g["cellules"] if c.get("lisible")]
    sur = int(sum(1 for c in lisibles if c["la_coupe_tombe_sur_une_frontiere"]))
    lisent = int(sum(1 for c in lisibles if c["elle_lit_une_frontiere"]))
    v("⚠⚠⚠ la condition de BASCULE écarte réellement des cellules",
      lisent < sur, f"{lisent} lisent pour {sur} coupes sur une frontière")
    # ⚠⚠ ET LA TOLERANCE D'UNE COUCHE DOIT ECARTER : ce qui se teste n'est pas qu'il existe des
    # coupes loin d'une frontiere, mais qu'elles ne COMPTENT PAS. Une tolerance large les compterait
    # toutes, et l'ecart resterait pourtant le meme.
    ecartees = int(sum(1 for c in lisibles
                       if c["ecart_a_la_frontiere_la_plus_proche"] is not None
                       and c["ecart_a_la_frontiere_la_plus_proche"] > 1
                       and not c["la_coupe_tombe_sur_une_frontiere"]))
    v("⚠⚠⚠ ... et une coupe à plus d'une couche NE COMPTE PAS comme sur la frontière",
      ecartees > 0, f"{ecartees} coupes écartées pour cette raison")
    # ⚠⚠⚠ ET « AU-DELA ELLE DECROCHE » DOIT LIRE TOUS LES GROUPES. Le verifier en recopiant
    # `all(...)` ici serait une SECONDE DEFINITION, libre de diverger — et une premiere version le
    # faisait, donc la sonde passait. Ce qui se teste est la FONCTION, sur une grille fabriquee ou
    # un groupe tient et l'autre non.
    def _cellule(fr, part):
        return {"combien_de_frontieres": fr, "combien_datteignables": fr, "lisible": True,
                "part_atteinte": part, "la_coupe_tombe_sur_une_frontiere": True}

    fabrique = la_relation({"cellules": [_cellule(1, 1.0), _cellule(2, 1.0), _cellule(3, 0.4)]})
    v("⚠⚠⚠ ... et « au-delà elle décroche » tombe dès qu'UN groupe au-delà tient encore un",
      fabrique["au_dela_elle_decroche"] is False,
      f"groupes {[x['frontieres'] for x in fabrique['lignes']]}")
    tous = la_relation({"cellules": [_cellule(1, 1.0), _cellule(2, 0.5), _cellule(3, 0.4)]})
    v("... et il tient quand ils décrochent tous", tous["au_dela_elle_decroche"] is True)

    # ---- la fenetre de la campagne
    ca = la_fenetre_de_la_campagne(vx, pas, decalages=6)
    v("⭐⭐⭐⭐ la fenêtre de la campagne porte PLUS d'une frontière à tous les décalages",
      ca["elle_porte_plus_dune_frontiere"],
      f"entre {ca['frontieres_minimum']} et {ca['frontieres_maximum']} sur "
      f"{ca['en_plis']} plis")
    v("⚠ et c'est l'inverse d'une fenêtre trop courte : elle fait plus d'un pli",
      ca["en_plis"] > 1.0, f"{ca['en_plis']} pli")

    # ---- le recouvrement : la moitie CONSTRUCTIVE
    rc = le_recouvrement(vx, pas, couches=(20, 36), decalages=6)
    court, long_ = rc["lignes"][0], rc["lignes"][1]
    v("⭐⭐⭐⭐ deux fenêtres décalées lisent plus de décalages qu'une seule",
      long_["decalages_lus"] > court["decalages_lus"],
      f"{long_['couches']} couches : {long_['decalages_lus']}/{long_['decalages']} contre "
      f"{court['decalages_lus']}/{court['decalages']} à {court['couches']}")
    # ⚠⚠ ET LE DECALAGE EST BIEN UNE DEMI-LONGUEUR, pas une valeur libre : le verifier par la
    # REGLE plutot que par un recompte.
    v("⚠⚠ la seconde fenêtre est décalée d'exactement une demi-longueur",
      all(abs(x["decalage_de_la_seconde_um"] - x["couches"] * vx / 2.0) < 1e-6
          for x in rc["lignes"]),
      f"{[x['decalage_de_la_seconde_um'] for x in rc['lignes']]}")

    # ---- le verdict est JOINT
    faux = juger({**rel, "au_dela_elle_decroche": False}, vi, {"longueurs_utiles": []}, ca)
    v("⚠⚠ le verdict tombe si la part ne décroche pas au-delà d'une frontière",
      faux["un_ajustement_decrit_une_frontiere"] is False)
    faux2 = juger(rel, vi, {"longueurs_utiles": []},
                  {**ca, "elle_porte_plus_dune_frontiere": False})
    v("... et il tombe aussi si la fenêtre de la campagne n'en portait qu'une",
      faux2["un_ajustement_decrit_une_frontiere"] is False)
    v("... et il tient quand les trois moitiés tiennent",
      juger(rel, vi, {"longueurs_utiles": []}, ca)[
          "un_ajustement_decrit_une_frontiere"] is True)

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
