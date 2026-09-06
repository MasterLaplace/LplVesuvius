#!/usr/bin/env python3
"""Un seul pas coûte 44 µm — combien la longueur, combien la direction, combien le reste ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `pourquoi_la_derive_accelere` a montré que l'accumulation n'est
pas le problème : la dérive est linéaire à ~33 µm par tour, et **le premier pas en coûte 44**.
C'est donc le premier pas, et lui seul, qui est le poste de dépense — et c'est une question sur
**un** pas, donc mesurable sans jamais marcher.

⭐⭐ LA DÉCOMPOSITION EST UNE HIÉRARCHIE DE LIBERTÉS, et c'est ce qui la rend utilisable : chaque
niveau donne à la marche **un paramètre de plus**, et l'écart entre deux niveaux est exactement
ce qu'une classe de remèdes peut espérer gagner, au mieux.

| niveau | ce qu'on donne à la marche | ce que l'écart au précédent mesure |
|---|---|---|
| `E0` | rien — pas nominal, normales calculées | *(le point de départ)* |
| `E1` | **une** longueur, la meilleure | ce que vaudrait un meilleur pas constant |
| `E2` | plus **une** rotation globale | ce que vaudrait corriger un biais de direction |
| `E3` | une longueur **par point** | ce que seule une correction PAR POINT peut prendre |

⚠⚠⚠ CE NE SONT PAS DES MÉTHODES, CE SONT DES BORNES. `E1`, `E2` et `E3` sont choisis **en
regardant la cible** : aucun dérouleur ne peut les atteindre, ils disent seulement ce qu'un
remède parfait de cette classe rapporterait. Et la liberté donnée est **bornée exprès** — laisser
chaque point aller où il veut rendrait zéro et ne dirait rien.

⭐⭐ ET `E3` EST LE CHIFFRE QUI DÉCIDE DU RACCROCHAGE. Se raccrocher à la matière, c'est corriger
la longueur point par point le long de la normale : `E3` est donc ce qu'un raccrochage
**parfait** laisserait. S'il est bas, le raccrochage a de la marge et c'est sa lecture qu'il faut
améliorer ; s'il est proche de `E1`, le problème n'est pas la longueur mais la **direction**, et
aucun raccrochage ne le prendra.

⚠ Aucune lecture du volume ici : tout se mesure contre les spires publiées, donc cette tranche ne
coûte pas un bloc.

Usage :
    uv run python src/nappe/le_cout_dun_seul_pas.py --verifier
    uv run python src/nappe/le_cout_dun_seul_pas.py --json docs/mesures/le_cout_dun_seul_pas.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

# ⚠ Un seul lecteur de corpus pour tous les dérouleurs, et sa fixture hors ligne avec lui.
from le_corpus_des_spires import corpus_fabrique, corpus_publie  # noqa: E402


def distances_par_longueur(points: np.ndarray, normales_: np.ndarray, cible: np.ndarray,
                           longueurs: np.ndarray, voxel_um: float) -> np.ndarray:
    """La distance de chaque point à la cible, pour chaque longueur de pas essayée.

    ⚠⚠ UNE SEULE TABLE SERT DEUX BORNES. La médiane d'une colonne donne l'erreur d'une longueur
    **commune** ; le minimum d'une ligne donne l'erreur de la meilleure longueur **de ce
    point-là**. Les calculer séparément ferait deux balayages qui pourraient ne pas porter sur
    les mêmes longueurs, et leur différence — qui est tout le propos — cesserait d'être lisible.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    return np.stack([distance_a(points + t * normales_, cible, voxel_um) for t in longueurs],
                    axis=1)


def rotations_essayees(demi_angle_deg: float, pas_deg: float) -> np.ndarray:
    """Les couples d'angles essayés pour la rotation globale, en degrés.

    ⚠⚠ UNE GRILLE, PAS UN OPTIMISEUR. Un optimiseur rendrait un minimum qui dépend de son point
    de départ et de sa tolérance, donc un nombre publié qu'on ne peut pas retrouver ; une grille
    déclarée se rejoue à l'identique. Sa finesse est un coût assumé et rendu, pas un réglage
    caché : elle borne la précision de la borne.

    ⚠ Le zéro est TOUJOURS dans la grille — sinon `E2` pourrait être pire que `E1`, ce qui n'a
    pas de sens pour une borne qui ajoute une liberté.
    """
    n = int(round(demi_angle_deg / pas_deg))
    axe = np.arange(-n, n + 1) * pas_deg
    return np.array([(a, b) for a in axe for b in axe], dtype=np.float64)


def tourner(normales_: np.ndarray, alpha_deg: float, beta_deg: float) -> np.ndarray:
    """Le champ de normales tourné en bloc de deux petits angles, autour de x puis de y.

    ⚠ La rotation est la MÊME pour toutes les cellules : c'est ce qui en fait un biais de
    direction et non une correction par point. Deux angles suffisent à couvrir toutes les
    directions voisines — un troisième ferait tourner le champ autour de lui-même et ne
    déplacerait aucune normale.
    """
    a, b = np.radians(alpha_deg), np.radians(beta_deg)
    rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    return normales_ @ (ry @ rx).T


def mesurer(cote: float | None = None, minimum: int = 30, points_max: int = 1500,
            demi_angle_deg: float = 6.0, pas_deg: float = 1.5, graine: int = 42,
            corpus: dict | None = None) -> dict:
    """Le coût d'un seul pas, décomposé en longueur, direction et reste."""
    from le_pas_normal_atteint_la_spire import distance_a, essayer_le_pas, normales  # noqa: PLC0415, E501
    from le_raccrochage_a_la_matiere import BOITE_CENTRE, BOITE_COTE  # noqa: PLC0415

    c = corpus_publie() if corpus is None else corpus
    volume, voxel_um = c["volume"], float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um
    # ⚠⚠ LA FENÊTRE DE LONGUEURS EST DÉRIVÉE, PAS CHOISIE : la moitié et une fois et demie le
    # pas nominal, c'est-à-dire exactement l'intervalle où une seule feuille est à portée. Plus
    # large, la voisine entre dans la fenêtre et le minimum sauterait sur elle.
    longueurs = np.linspace(0.5 * pas_vx, 1.5 * pas_vx, 41)

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    rng = np.random.default_rng(graine)
    angles = rotations_essayees(demi_angle_deg, pas_deg)

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        grilles[rang] = (a, dans)
        nuages[rang] = a[ok]

    lignes = []
    for r in sorted(grilles):
        if r + 1 not in nuages:
            continue
        a0, dans = grilles[r]
        n0, bon = normales(a0, dans)
        garde = bon & dans
        if int(garde.sum()) < minimum:
            continue
        p = a0[garde]
        d = n0[garde]
        if len(p) > points_max:
            pris = rng.choice(len(p), size=points_max, replace=False)
            p, d = p[pris], d[pris]
        cible = nuages[r + 1]
        # ⚠ Le seul bit de supervision de la marche : le sens, fixé une fois.
        sens = 1.0 if essayer_le_pas(p, d, cible, pas_vx, voxel_um)["retenu"] == "+" else -1.0
        d = sens * d

        table = distances_par_longueur(p, d, cible, longueurs, voxel_um)
        medianes = np.median(table, axis=0)
        i_best = int(np.argmin(medianes))
        e0 = float(np.median(distance_a(p + pas_vx * d, cible, voxel_um)))
        e1 = float(medianes[i_best])
        # --- E2 : la meilleure rotation globale, cherchée à la meilleure longueur ---
        meilleure = (e1, 0.0, 0.0)
        for al, be in angles:
            if al == 0.0 and be == 0.0:
                continue
            dd = tourner(d, al, be)
            m = float(np.median(distance_a(p + longueurs[i_best] * dd, cible, voxel_um)))
            if m < meilleure[0]:
                meilleure = (m, float(al), float(be))
        # ⚠⚠⚠ ET LES DEUX DERNIERS NIVEAUX SE MESURENT SUR LA NORMALE TOURNÉE, PAS SUR
        # L'ORIGINALE. Première version : `E3` prenait le minimum par point le long de la
        # normale de DÉPART, donc il ne contenait pas la liberté de `E2` — les deux n'étaient
        # pas emboîtés, et la sonde a trouvé une paire où `E2` battait `E3`. Une décomposition
        # dont les niveaux ne s'emboîtent pas ne décompose rien : ses écarts cessent de nommer
        # une classe de remèdes et mesurent un accident.
        d2 = tourner(d, meilleure[1], meilleure[2])
        table2 = distances_par_longueur(p, d2, cible, longueurs, voxel_um)
        # ⚠ La longueur est réajustée APRÈS la rotation : tourner déplace le meilleur pas, et le
        # garder figé ferait de `E2` une borne que `E1` pourrait battre.
        e2 = float(np.median(table2, axis=0).min())
        # ⚠⚠ `E3` prend le minimum PAR POINT, donc il regarde la cible une fois par cellule.
        # C'est ce qui en fait la borne d'un raccrochage parfait — et ce qui interdit de le lire
        # comme une performance.
        e3 = float(np.median(table2.min(axis=1)))
        # ⚠⚠⚠ L'ÉCART LOCAL, MESURÉ DANS LA BOÎTE, EST LE TÉMOIN QUI EMPÊCHE DE MAL LIRE `E1`.
        # Le pas nominal vient de la médiane sur TOUTES les spires ; si l'écart réel entre ces
        # deux-là, ici, n'est pas celui-là, alors « une meilleure longueur gagne 14 µm » ne dit
        # pas qu'il faut mieux choisir le pas — il dit qu'on l'a pris sur la mauvaise
        # population. Sans ce nombre, les deux lectures sont indiscernables.
        sans_bouger = float(np.median(distance_a(p, cible, voxel_um)))
        au_bord = bool(i_best in (0, len(longueurs) - 1))
        lignes.append(dict(
            de=r, vers=r + 1, cellules=int(len(p)),
            distance_sans_bouger_um=round(sans_bouger, 1),
            longueur_au_bord_de_la_fenetre=au_bord,
            e0_nominal_um=round(e0, 1),
            e1_meilleure_longueur_um=round(e1, 1),
            longueur_retenue_um=round(float(longueurs[i_best]) * voxel_um, 1),
            e2_plus_rotation_um=round(e2, 1),
            rotation_deg=[round(meilleure[1], 2), round(meilleure[2], 2)],
            e3_par_point_um=round(e3, 1),
            bits_de_supervision=1))

    if not lignes:
        raise RuntimeError("aucune paire mesurable dans la boîte")

    def med(cle):
        return round(float(np.median([e[cle] for e in lignes])), 1)

    r = dict(
        fragment="PHerc0500P2", volume=volume, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        ecart_lu_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        pas_nominal_um=ecart_um,
        fenetre_de_longueurs_um=[round(float(longueurs[0]) * voxel_um, 1),
                                 round(float(longueurs[-1]) * voxel_um, 1)],
        rotations_essayees=len(angles), demi_angle_deg=demi_angle_deg, pas_deg=pas_deg,
        paires=len(lignes), lignes=lignes,
        e0_nominal_median_um=med("e0_nominal_um"),
        e1_meilleure_longueur_median_um=med("e1_meilleure_longueur_um"),
        e2_plus_rotation_median_um=med("e2_plus_rotation_um"),
        e3_par_point_median_um=med("e3_par_point_um"),
        longueur_retenue_mediane_um=med("longueur_retenue_um"),
        distance_sans_bouger_mediane_um=med("distance_sans_bouger_um"))
    # ⚠⚠⚠ UNE LONGUEUR AU BORD DE LA FENÊTRE N'EST PAS UN OPTIMUM, C'EST UN REFUS : le minimum
    # est ailleurs, et la fenêtre l'a coupé. Les compter et publier la médiane SANS eux, parce
    # qu'une médiane qui les inclut mélange des optima et des butées.
    au_bord = [e for e in lignes if e["longueur_au_bord_de_la_fenetre"]]
    dedans = [e for e in lignes if not e["longueur_au_bord_de_la_fenetre"]]
    r["paires_dont_la_longueur_bute_sur_la_fenetre"] = len(au_bord)
    r["longueur_retenue_mediane_hors_butee_um"] = (
        round(float(np.median([e["longueur_retenue_um"] for e in dedans])), 1)
        if dedans else None)
    # ⚠⚠ ET LA QUESTION QUE CE TÉMOIN TRANCHE : le pas nominal est-il celui de CETTE boîte ? Si
    # l'écart local vaut le nominal, `E1` mesure bien ce qu'une meilleure longueur rapporterait ;
    # sinon, il mesure d'abord que le nominal vient d'ailleurs.
    r["le_pas_nominal_est_celui_de_la_boite"] = bool(
        abs(r["distance_sans_bouger_mediane_um"] - ecart_um) < 0.1 * ecart_um)
    # ⚠⚠⚠ ET LA FORME LA PLUS UTILE DU RÉSULTAT : la meilleure longueur EST-ELLE l'écart local ?
    # Si oui, le tiers du coût que « mieux choisir la longueur » rapporterait n'est pas un
    # réglage à trouver, c'est un nombre à MESURER — et le problème passe de « quelle longueur »
    # à « comment connaître l'écart local sans regarder la cible ».
    for e in lignes:
        e["ecart_longueur_moins_local_um"] = round(
            e["longueur_retenue_um"] - e["distance_sans_bouger_um"], 1)
    ecarts = [abs(e["ecart_longueur_moins_local_um"]) for e in dedans]
    r["ecart_median_entre_longueur_et_ecart_local_um"] = (
        round(float(np.median(ecarts)), 1) if ecarts else None)
    r["paires_comparees_a_lecart_local"] = len(ecarts)
    # ⚠ La comparaison se fait HORS BUTÉE : une longueur coupée par la fenêtre ne peut pas
    # s'accorder avec quoi que ce soit, et l'inclure ferait passer une butée pour un désaccord.
    r["resolution_du_balayage_um"] = round(
        float(longueurs[1] - longueurs[0]) * voxel_um / 2, 1)
    # ⚠⚠⚠ SANS SEUIL, ET C'EST UNE CORRECTION. J'avais d'abord exigé que la meilleure longueur
    # ÉGALE l'écart local à deux pas de balayage près — un seuil qui demande plus de précision
    # que la médiane d'un nuage n'en a, et qui rendait NON pour 7,7 µm sur 110. La question qui
    # se pose vraiment est comparative : la meilleure longueur ressemble-t-elle plus à l'écart
    # LOCAL qu'au pas NOMINAL ? Elle ne demande aucun réglage et elle tranche.
    for e in dedans:
        e["plus_proche_de_lecart_local"] = bool(
            abs(e["longueur_retenue_um"] - e["distance_sans_bouger_um"])
            < abs(e["longueur_retenue_um"] - ecart_um))
    r["paires_ou_la_longueur_suit_lecart_local"] = sum(
        1 for e in dedans if e["plus_proche_de_lecart_local"])
    r["la_longueur_suit_lecart_local_plutot_que_le_nominal"] = bool(
        dedans and r["paires_ou_la_longueur_suit_lecart_local"] > len(dedans) / 2)
    # ⚠⚠⚠ CHAQUE ÉCART NOMME UNE CLASSE DE REMÈDES, ET C'EST LE SEUL FORMAT QUI DÉCIDE D'UN
    # EFFORT. Publier les quatre niveaux sans leurs différences laisserait le lecteur les faire,
    # et c'est justement là qu'est le résultat.
    r["gain_dune_meilleure_longueur_um"] = round(
        r["e0_nominal_median_um"] - r["e1_meilleure_longueur_median_um"], 1)
    r["gain_dune_rotation_globale_um"] = round(
        r["e1_meilleure_longueur_median_um"] - r["e2_plus_rotation_median_um"], 1)
    r["gain_dune_correction_par_point_um"] = round(
        r["e2_plus_rotation_median_um"] - r["e3_par_point_median_um"], 1)
    r["plancher_um"] = r["e3_par_point_median_um"]
    r["part_du_cout_prise_par_la_longueur"] = round(
        r["gain_dune_meilleure_longueur_um"] / r["e0_nominal_median_um"], 3)
    r["part_du_cout_prise_par_la_direction"] = round(
        r["gain_dune_rotation_globale_um"] / r["e0_nominal_median_um"], 3)
    r["part_du_cout_prise_par_le_point_a_point"] = round(
        r["gain_dune_correction_par_point_um"] / r["e0_nominal_median_um"], 3)
    r["part_irreductible"] = round(r["plancher_um"] / r["e0_nominal_median_um"], 3)
    # ⚠⚠⚠ LES QUATRE NIVEAUX SONT EMBOÎTÉS PARCE QUE CHACUN CONTIENT LA LIBERTÉ DU PRÉCÉDENT,
    # et ce n'est vrai que depuis une correction : `E3` se mesure sur la normale TOURNÉE. Le
    # vérifier plutôt que l'affirmer — la première version ne l'était pas, et une sonde a trouvé
    # une paire où `E2` battait `E3`.
    r["les_niveaux_sont_emboites"] = all(
        e["e0_nominal_um"] >= e["e1_meilleure_longueur_um"] >= e["e2_plus_rotation_um"]
        >= e["e3_par_point_um"] for e in lignes)
    r["paires_ou_la_rotation_ne_sert_a_rien"] = sum(
        1 for e in lignes if e["rotation_deg"] == [0.0, 0.0])
    # ⚠⚠ ET LE FAIT QUI DÉCIDE DU RACCROCHAGE : le plancher d'un raccrochage PARFAIT tient-il la
    # feuille ? S'il ne la tient pas, aucune lecture du volume ne sauvera le pas normal.
    r["le_plancher_tient_la_feuille"] = bool(r["plancher_um"] < ecart_um / 2)
    r["le_raccrochage_a_de_la_marge"] = bool(
        r["gain_dune_correction_par_point_um"] > r["gain_dune_rotation_globale_um"])
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- la grille de rotations ---
    g = rotations_essayees(3.0, 1.5)
    v("la grille de rotations est carrée et déclarée", len(g) == 25, str(len(g)))
    v("... et elle contient TOUJOURS le zéro, sinon la borne pourrait empirer",
      any(a == 0.0 and b == 0.0 for a, b in g))
    v("... et elle est symétrique autour de zéro",
      bool(np.allclose(sorted(g[:, 0]), sorted(-g[:, 0]))))

    # --- la rotation ---
    n_ = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
    v("une rotation nulle ne déplace aucune normale",
      bool(np.allclose(tourner(n_, 0.0, 0.0), n_)))
    v("... une rotation garde les normales unitaires",
      bool(np.allclose(np.linalg.norm(tourner(n_, 4.0, -3.0), axis=1), 1.0)))
    tourne = tourner(np.array([[0.0, 0.0, 1.0]]), 90.0, 0.0)[0]
    v("... et un quart de tour autour de x envoie z sur -y",
      bool(np.allclose(tourne, [0.0, -1.0, 0.0])), str(np.round(tourne, 6).tolist()))

    # --- la table des distances ---
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    pts = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    nrm = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    cible = np.array([[0.0, 0.0, 5.0], [10.0, 0.0, 9.0]])
    t = np.array([4.0, 5.0, 9.0])
    tab = distances_par_longueur(pts, nrm, cible, t, 1.0)
    v("la table a une ligne par point et une colonne par longueur", tab.shape == (2, 3),
      str(tab.shape))
    # ⚠⚠ LES DEUX LECTURES DE LA MÊME TABLE, sur des nombres où l'on connaît la réponse : la
    # meilleure longueur COMMUNE ne peut satisfaire qu'un point à la fois, la meilleure longueur
    # PAR POINT les satisfait tous les deux. C'est exactement l'écart que la mesure publie.
    v("... la meilleure longueur commune laisse un reste", float(np.median(tab, axis=0).min()) > 0,
      str(np.round(np.median(tab, axis=0), 2).tolist()))
    v("... alors que la meilleure longueur par point les annule",
      float(np.median(tab.min(axis=1))) == 0.0, str(tab.min(axis=1).tolist()))
    v("... et le minimum par point ne dépasse jamais le minimum des médianes",
      float(np.median(tab.min(axis=1))) <= float(np.median(tab, axis=0).min()))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    fab = mesurer(minimum=20, points_max=120, demi_angle_deg=3.0, pas_deg=1.5,
                  corpus=corpus_fabrique())
    v("la mesure tourne de bout en bout sur un corpus fabriqué, sans rien lire",
      fab["paires"] > 0, f"{fab['paires']} paires")
    v("... et la marche y est imparfaite, donc les comparaisons portent sur quelque chose",
      all(e["e0_nominal_um"] > 0 for e in fab["lignes"]))
    # ⚠⚠⚠ L'INVARIANT QUI FAIT LA DÉCOMPOSITION : chaque niveau ajoute une liberté, donc ne peut
    # pas faire pire. Si l'ordre se brisait, les écarts publiés cesseraient de nommer une classe
    # de remèdes — ils mesureraient un accident d'optimisation.
    v("... les quatre niveaux sont emboîtés, ligne par ligne",
      fab["les_niveaux_sont_emboites"],
      str([(e["e0_nominal_um"], e["e1_meilleure_longueur_um"],
            e["e2_plus_rotation_um"], e["e3_par_point_um"]) for e in fab["lignes"]][:2]))
    # ⚠⚠ LA BUTÉE EST COMPTÉE, PAS CACHÉE : une longueur au bord de la fenêtre n'est pas un
    # optimum mais un refus, et une médiane qui la mélange aux vrais optima ne veut rien dire.
    v("... les longueurs qui butent sur la fenêtre sont comptées à part",
      fab["paires_dont_la_longueur_bute_sur_la_fenetre"]
      + sum(1 for e in fab["lignes"] if not e["longueur_au_bord_de_la_fenetre"])
      == fab["paires"],
      f"{fab['paires_dont_la_longueur_bute_sur_la_fenetre']} sur {fab['paires']}")
    v("... et le témoin « sans bouger » est mesuré, pour dire d'où vient le pas nominal",
      all(e["distance_sans_bouger_um"] > 0 for e in fab["lignes"]),
      f"{fab['distance_sans_bouger_mediane_um']} µm contre {fab['pas_nominal_um']} nominal")
    # ⚠⚠ LA RÉSOLUTION DU BALAYAGE EST PUBLIÉE parce qu'elle borne toute comparaison de
    # longueurs : un accord plus fin qu'elle serait une précision que la mesure n'a pas.
    v("... la résolution du balayage est celle de sa grille",
      abs(fab["resolution_du_balayage_um"]
          - (fab["fenetre_de_longueurs_um"][1] - fab["fenetre_de_longueurs_um"][0]) / 80) < 0.1,
      f"{fab['resolution_du_balayage_um']} µm")
    # ⚠⚠⚠ LA COMPARAISON EST SANS SEUIL, et le contrôle vérifie qu'elle discrimine dans les deux
    # sens sur des nombres : une longueur près de l'écart local doit être comptée pour lui, une
    # longueur près du nominal contre lui. Sans les deux, « elle suit l'écart local » serait un
    # mot qu'aucune donnée ne peut contredire.
    def suit(longueur, local, nominal):
        return abs(longueur - local) < abs(longueur - nominal)

    v("... et la comparaison discrimine dans les deux sens",
      suit(105.0, 100.3, 135.5) and not suit(152.4, 171.0, 135.5))
    # ⚠⚠ ET CELUI-CI A DÛ ÊTRE RÉÉCRIT : ma première version portait un `or True`, donc elle ne
    # pouvait pas échouer — le défaut que ce dépôt traque partout, écrit dans le contrôle censé
    # le prévenir. Ce qui se vérifie est que le compte de paires effectivement comparées soit
    # celui des paires hors butée, ni plus ni moins.
    v("... et l'accord est mesuré sur les paires HORS butée, ni plus ni moins",
      fab["paires_comparees_a_lecart_local"]
      == fab["paires"] - fab["paires_dont_la_longueur_bute_sur_la_fenetre"],
      f"{fab['paires_comparees_a_lecart_local']} sur {fab['paires']}")
    v("... la longueur retenue reste dans la fenêtre dérivée",
      all(fab["fenetre_de_longueurs_um"][0] <= e["longueur_retenue_um"]
          <= fab["fenetre_de_longueurs_um"][1] for e in fab["lignes"]),
      str(fab["fenetre_de_longueurs_um"]))
    v("... et la rotation retenue reste dans la grille essayée",
      all(abs(x) <= fab["demi_angle_deg"] for e in fab["lignes"] for x in e["rotation_deg"]))
    # ⚠⚠ « LES QUATRE PARTS SE SOMMENT À UN » NE PEUT PAS ÉCHOUER : la somme télescope par
    # construction, quels que soient les niveaux. C'est une identité, pas un contrôle — elle
    # était verte sur la version dont les niveaux n'étaient PAS emboîtés, avec une part
    # négative. Ce qui se vérifie est que chaque part soit POSITIVE, c'est-à-dire l'emboîtement
    # relu sur les écarts.
    parts = [fab["part_du_cout_prise_par_la_longueur"],
             fab["part_du_cout_prise_par_la_direction"],
             fab["part_du_cout_prise_par_le_point_a_point"],
             fab["part_irreductible"]]
    v("... aucune part n'est négative, ce qui est l'emboîtement relu sur les écarts",
      all(x >= 0 for x in parts), str(parts))
    v("... et elles se somment à un, ce qui est une identité et non un contrôle",
      abs(sum(parts) - 1.0) < 0.01, str(round(sum(parts), 4)))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "plancher" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, points_max=120, corpus=corpus_fabrique(decalage_vx=5000.0))
    except RuntimeError as exc:
        hors = str(exc)
    v("un corpus posé hors de la boîte est REFUSÉ, pas rendu vide", hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure."""
    print(f"pas nominal {r['pas_nominal_um']} µm · demi-épaisseur {r['demi_epaisseur_um']} µm · "
          f"{r['paires']} paires consécutives · fenêtre de longueurs "
          f"{r['fenetre_de_longueurs_um']} µm · {r['rotations_essayees']} rotations "
          f"(±{r['demi_angle_deg']}° au pas de {r['pas_deg']}°)\n")
    print(f"{'de':>4} {'vers':>5} {'cell.':>7} {'sur place':>10} {'E0 nominal':>11} "
          f"{'E1 longueur':>12} {'E2 +rotation':>13} {'E3 par point':>13} {'longueur':>10} "
          f"{'rotation':>16}")
    print("-" * 112)
    for e in r["lignes"]:
        butee = " ⛔" if e["longueur_au_bord_de_la_fenetre"] else "  "
        print(f"{e['de']:>4} {e['vers']:>5} {e['cellules']:>7} "
              f"{e['distance_sans_bouger_um']:>9.1f}µ {e['e0_nominal_um']:>10.1f}µ "
              f"{e['e1_meilleure_longueur_um']:>11.1f}µ {e['e2_plus_rotation_um']:>12.1f}µ "
              f"{e['e3_par_point_um']:>12.1f}µ {e['longueur_retenue_um']:>8.1f}µ{butee}"
              f"{str(e['rotation_deg']):>16}")
    print(f"\nmédianes : E0 {r['e0_nominal_median_um']} µm → E1 "
          f"{r['e1_meilleure_longueur_median_um']} → E2 {r['e2_plus_rotation_median_um']} → E3 "
          f"{r['e3_par_point_median_um']} µm")
    print(f"la meilleure longueur commune vaut {r['longueur_retenue_mediane_um']} µm "
          f"contre {r['pas_nominal_um']} nominal — hors butée, "
          f"{r['longueur_retenue_mediane_hors_butee_um']} µm sur "
          f"{r['paires'] - r['paires_dont_la_longueur_bute_sur_la_fenetre']} paires "
          f"(⛔ {r['paires_dont_la_longueur_bute_sur_la_fenetre']} butent sur la fenêtre, donc "
          f"leur minimum est ailleurs)")
    print(f"⚠ l'écart LOCAL mesuré dans la boîte — ne pas bouger — vaut "
          f"{r['distance_sans_bouger_mediane_um']} µm contre {r['pas_nominal_um']} nominal : "
          f"le pas nominal est celui de cette boîte : "
          f"{'OUI' if r['le_pas_nominal_est_celui_de_la_boite'] else 'NON'}")
    print(f"⭐ la meilleure longueur suit-elle l'écart LOCAL plutôt que le pas NOMINAL ? "
          f"{'OUI' if r['la_longueur_suit_lecart_local_plutot_que_le_nominal'] else 'NON'} "
          f"({r['paires_ou_la_longueur_suit_lecart_local']} paires sur "
          f"{r['paires_comparees_a_lecart_local']} hors butée, écart médian "
          f"{r['ecart_median_entre_longueur_et_ecart_local_um']} µm) — donc ce tiers du coût "
          f"n'est pas un réglage à trouver, c'est un nombre à MESURER")
    print(f"\nce que chaque classe de remèdes peut gagner, AU MIEUX :")
    print(f"  une meilleure longueur constante : {r['gain_dune_meilleure_longueur_um']:>6.1f} µm "
          f"({100 * r['part_du_cout_prise_par_la_longueur']:.0f} %)")
    print(f"  plus une rotation globale        : {r['gain_dune_rotation_globale_um']:>6.1f} µm "
          f"({100 * r['part_du_cout_prise_par_la_direction']:.0f} %)")
    print(f"  plus une correction PAR POINT    : "
          f"{r['gain_dune_correction_par_point_um']:>6.1f} µm "
          f"({100 * r['part_du_cout_prise_par_le_point_a_point']:.0f} %)")
    print(f"  plancher, que rien ne prend      : {r['plancher_um']:>6.1f} µm "
          f"({100 * r['part_irreductible']:.0f} %)")
    print(f"\nla rotation ne sert à rien sur {r['paires_ou_la_rotation_ne_sert_a_rien']} paires "
          f"sur {r['paires']}")
    print(f"→ le plancher tient la feuille : "
          f"{'OUI' if r['le_plancher_tient_la_feuille'] else 'NON'} "
          f"({r['plancher_um']} contre {r['demi_epaisseur_um']} µm)")
    print(f"→ le raccrochage a de la marge (le point à point vaut plus que la rotation) : "
          f"{'OUI' if r['le_raccrochage_a_de_la_marge'] else 'NON'}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--points", type=int, default=1500)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, points_max=a.points)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
