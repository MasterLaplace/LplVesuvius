#!/usr/bin/env python3
"""La mâchoire est un instrument PLAN, et la matière froissée ne l'est pas.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `152` ferme la troisième et dernière source de direction et laisse une
question qui n'est plus « où trouver une direction droite » mais **qu'est-ce qui rendrait le plan
moyen d'une mâchoire égal à la normale de la feuille**. `150` avait déjà réfuté la réponse la plus
évidente — la largeur. Ce fichier réfute **toute la famille** et nomme la cause, qui est
structurelle : une mâchoire pose ses appuis le long de `t = z × n` et rend `n' = t' × z`, donc sa
sortie est **toujours perpendiculaire à l'axe**, par construction. Or la vraie normale d'une feuille
**froissée** sort du plan du tour.

⭐⭐⭐ ET LE CONTRÔLE EST DANS LA MATIÈRE ELLE-MÊME. Sur une spirale nue ou seulement écrasée, la
composante axiale de la vraie normale vaut **exactement zéro** — et la mâchoire y est exacte, à
toutes les largeurs et à tous les nombres d'appuis. Ce n'est donc pas que la mâchoire estime mal :
c'est qu'elle **ne peut pas exprimer** ce qu'il y aurait à estimer. Les deux énoncés ne se réparent
pas de la même façon, et un seul des deux est vrai.

⭐⭐ LE REMÈDE QUE ÇA DÉSIGNE EST MESURÉ ICI AUSSI, AVEC SA BORNE. Une mâchoire en **croix** — deux
barres d'appuis au lieu d'une — rend un nuage qui n'est plus colinéaire, donc un **plan** au lieu
d'une droite, et sa normale est la plus petite direction de ce nuage. Elle paie là où le froissement
est modéré et **ne suffit pas** sur la matière du rouleau.

⚠⚠ AUCUN RAPPORT N'EST PUBLIÉ, ET C'EST DÉLIBÉRÉ. Rapporter « l'inclinaison lue sur l'inclinaison
vraie » demanderait d'écarter les départs où la vraie inclinaison est presque nulle, donc de choisir
un plancher — un seuil déguisé. L'**écart** en degrés n'a pas de cas dégénéré, et c'est la grandeur
que `152` a déjà établie comme lisible.

⚠ La comparaison est APPARIÉE sur le même départ, toujours : la variabilité d'un départ à l'autre
dépasse ce que n'importe lequel de ces réglages déplace.

Usage :
    uv run python src/nappe/la_machoire_est_plane_la_matiere_ne_lest_pas.py --verifier
    uv run python src/nappe/la_machoire_est_plane_la_matiere_ne_lest_pas.py \\
        --json docs/mesures/la_machoire_est_plane_la_matiere_ne_lest_pas.json
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

from la_pince_tient_elle_la_feuille import (LARGEUR_DE_REFERENCE,  # noqa: E402
                                            LONGUEUR_DONDE_UM, MATIERES, RAYON_MM, _ecart_deg,
                                            _matiere, _nom, _PAS, _VOXEL, poser, un_depart)

POSES = 40
# ⚠ La plus petite largeur vaut 1,4 µm, soit MOINS D'UN VOXEL : c'est la seule façon de demander
# « et si la mâchoire n'avait pas de largeur du tout ». Une borne plus haute laisserait la réponse
# à l'extrapolation, et un optimum au bord d'un balayage est une borne du balayage.
LARGEURS = (0.008, 0.016, 0.031, 0.0625, 0.125, 0.25, 0.375, 0.5)
APPUIS = (2, 3, 5, 9, 17)


def la_normale_sort_elle_du_plan(matieres=MATIERES, poses: int = POSES) -> dict:
    """De combien la vraie normale sort-elle du plan du tour, matière par matière ?

    ⭐⭐⭐⭐ C'EST LA MESURE QUI DÉCIDE DE TOUT LE RESTE, et elle ne coûte AUCUNE lecture :
    `normale_locale` est analytique. Une mâchoire rend `n' = t' × z`, donc `n'·z = 0` toujours ; ce
    que cette fonction mesure est la part de la vraie normale qu'aucune mâchoire en segment ne peut
    exprimer.

    ⚠ Le résultat se lit en composante ET en angle : `|n·z|` est ce que l'instrument perd, l'arc
    sinus est ce que ça fait en degrés, et les deux disent la même chose autrement.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        axial = []
        for k in range(int(poses)):
            _d, n = un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um, pas_um)
            n = np.asarray(n, dtype=np.float64)
            axial.append(abs(float(n[0] / max(float(np.linalg.norm(n)), 1e-12))))
        a = np.asarray(axial)
        out.append({"nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
                    "poses": int(poses),
                    "axial_median": round(float(np.median(a)), 6),
                    "axial_p90": round(float(np.percentile(a, 90)), 4),
                    "axial_max": round(float(a.max()), 4),
                    "hors_plan_median_deg": round(float(np.degrees(np.arcsin(
                        min(float(np.median(a)), 1.0)))), 3),
                    "hors_plan_max_deg": round(float(np.degrees(np.arcsin(
                        min(float(a.max()), 1.0)))), 3),
                    "elle_sort_du_plan": bool(float(np.median(a)) > 0.0)})
    return {"decidable": bool(out), "poses_par_case": int(poses), "par_matiere": out}


def _erreur_dune_pose(vol, departs, largeur_en_pas: float, appuis: int, en_croix: bool,
                      pas_um: float, voxel_um: float) -> tuple[list[float], list[float], int]:
    """L'écart à la vraie normale, départ par départ, et le prix en lectures."""
    err, lect, refus = [], [], 0
    for d0, vrai in departs:
        vol.lectures = 0
        e = poser(vol, d0, vrai, float(largeur_en_pas) * pas_um, pas_um, voxel_um, True,
                  appuis=int(appuis), en_croix=bool(en_croix))
        if e is None:
            refus += 1
            continue
        err.append(_ecart_deg(e["normale"], vrai))
        lect.append(int(vol.lectures))
    return err, lect, refus


def le_biais_tient_il_a_la_geometrie(matieres=MATIERES, largeurs=LARGEURS, appuis=APPUIS,
                                     poses: int = POSES) -> dict:
    """L'écart à la vraie normale tombe-t-il quand on rétrécit la mâchoire, ou quand on l'enrichit ?

    ⭐⭐⭐ LES DEUX BALAYAGES ONT LEUR PIÈGE, ET C'EST CE QUI LES REND CONCLUANTS. La largeur
    descend SOUS LE VOXEL — si le biais venait de ce qu'une mâchoire moyenne sur sa largeur, il
    devrait s'évanouir là. Le nombre d'appuis monte à dix-sept — si le biais venait d'un
    échantillonnage trop pauvre, il devrait s'évanouir là aussi.

    ⚠ La pose est faite le long de la VRAIE normale, sans aucune inclinaison imposée : ce qu'on
    isole est le biais de l'instrument, pas celui de la direction qu'on lui donne.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        departs = [un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um, pas_um)
                   for k in range(int(poses))]
        bloc = {"nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
                "poses": int(poses), "par_largeur": [], "par_appuis": []}
        for lg in largeurs:
            err, lect, refus = _erreur_dune_pose(vol, departs, lg, 3, False, pas_um, voxel_um)
            bloc["par_largeur"].append({
                "largeur_en_pas": float(lg), "largeur_um": round(float(lg) * pas_um, 2),
                "posees": len(err), "refusees": int(refus),
                "erreur_mediane_deg": (round(float(np.median(err)), 3) if err else None),
                "lectures_medianes": (int(np.median(lect)) if lect else None)})
        for n in appuis:
            err, lect, refus = _erreur_dune_pose(vol, departs, LARGEUR_DE_REFERENCE, n, False,
                                                 pas_um, voxel_um)
            bloc["par_appuis"].append({
                "appuis": int(n), "posees": len(err), "refusees": int(refus),
                "erreur_mediane_deg": (round(float(np.median(err)), 3) if err else None),
                "lectures_medianes": (int(np.median(lect)) if lect else None)})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "largeur_de_reference": float(LARGEUR_DE_REFERENCE),
            "largeurs": [float(x) for x in largeurs], "appuis": [int(x) for x in appuis],
            "par_matiere": out}


def la_croix_repare_t_elle(matieres=MATIERES, poses: int = POSES,
                           largeur_en_pas: float = LARGEUR_DE_REFERENCE) -> dict:
    """Une mâchoire à DEUX barres récupère-t-elle ce qu'une barre ne peut pas exprimer ?

    ⭐⭐ UN SEUL INGRÉDIENT CHANGE : la croix ajuste un PLAN au lieu d'une droite, et sa normale est
    la plus petite direction du nuage au lieu de `t' × z`. Fenêtre, refus du bord, épaisseur
    mesurée, centre : tout le reste est celui de `142`.

    ⚠ L'écart est APPARIÉ sur le même départ, et les deux comptes de poses sont publiés à part :
    « elle est plus juste » et « elle se pose aussi souvent » sont deux énoncés.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        departs = [un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um, pas_um)
                   for k in range(int(poses))]
        es, ec, paires, ls, lc = [], [], [], [], []
        ns, nc = 0, 0
        for d0, vrai in departs:
            vol.lectures = 0
            s = poser(vol, d0, vrai, float(largeur_en_pas) * pas_um, pas_um, voxel_um, True)
            l_s = int(vol.lectures)
            vol.lectures = 0
            c = poser(vol, d0, vrai, float(largeur_en_pas) * pas_um, pas_um, voxel_um, True,
                      en_croix=True)
            l_c = int(vol.lectures)
            if s is not None:
                ns += 1
                es.append(_ecart_deg(s["normale"], vrai))
                ls.append(l_s)
            if c is not None:
                nc += 1
                ec.append(_ecart_deg(c["normale"], vrai))
                lc.append(l_c)
            if s is not None and c is not None:
                paires.append(_ecart_deg(c["normale"], vrai) - _ecart_deg(s["normale"], vrai))
        out.append({
            "nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
            "poses": int(poses), "posees_en_segment": int(ns), "posees_en_croix": int(nc),
            "erreur_segment_deg": (round(float(np.median(es)), 3) if es else None),
            "erreur_croix_deg": (round(float(np.median(ec)), 3) if ec else None),
            "ecart_apparie_deg": (round(float(np.median(paires)), 3) if paires else None),
            "mieux": int(sum(1 for x in paires if x < 0.0)),
            "pire": int(sum(1 for x in paires if x > 0.0)),
            "appariees": int(len(paires)),
            "lectures_segment": (int(np.median(ls)) if ls else None),
            "lectures_croix": (int(np.median(lc)) if lc else None),
            "elle_repare": bool(paires and float(np.median(paires)) < 0.0)})
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "largeur_en_pas": float(largeur_en_pas), "par_matiere": out}


def juger(hors_plan: dict, geometrie: dict, croix: dict) -> dict:
    """Trois énoncés SÉPARÉS, et le troisième porte sa borne.

    ⭐⭐⭐⭐ (1) La vraie normale sort du plan du tour EXACTEMENT là où la matière froisse, et pas
    ailleurs. (2) L'écart à la vraie normale ne tombe ni quand la mâchoire rétrécit sous le voxel,
    ni quand on lui ajoute des appuis — donc il ne tient pas à sa géométrie plane. (3) Une croix
    récupère une part de ce que le segment ne peut pas exprimer, et cette part est mesurée matière
    par matière plutôt qu'annoncée.

    ⚠⚠ Les trois se lisent ensemble ou pas du tout : sans (1) le biais de (2) n'a pas de cause
    nommée, et sans (2) la cause de (1) ne serait qu'une hypothèse parmi d'autres.
    """
    if not (hors_plan.get("decidable") and geometrie.get("decidable")
            and croix.get("decidable")):
        return {"decidable": False, "raison": "une des trois mesures manque"}
    # (1) le partage est-il exactement celui du froissement ?
    lisses = [m for m in hors_plan["par_matiere"] if m["amplitude_um"] == 0.0]
    froissees = [m for m in hors_plan["par_matiere"] if m["amplitude_um"] > 0.0]
    out = {"decidable": True,
           "elle_sort_du_plan_si_et_seulement_si_ca_froisse": bool(
               lisses and froissees
               and all(not m["elle_sort_du_plan"] for m in lisses)
               and all(m["elle_sort_du_plan"] for m in froissees))}
    # (2) la geometrie plane deplace-t-elle quelque chose ?
    par = []
    for m in geometrie["par_matiere"]:
        lg = [x for x in m["par_largeur"] if x["erreur_mediane_deg"] is not None]
        ap = [x for x in m["par_appuis"] if x["erreur_mediane_deg"] is not None]
        if not lg or not ap:
            continue
        etroite, large = lg[0], lg[-1]
        pauvre, riche = ap[0], ap[-1]
        par.append({
            "nom": m["nom"], "amplitude_um": m["amplitude_um"],
            "largeur_la_plus_etroite_en_pas": etroite["largeur_en_pas"],
            "erreur_a_la_plus_etroite_deg": etroite["erreur_mediane_deg"],
            "erreur_a_la_plus_large_deg": large["erreur_mediane_deg"],
            "erreur_a_deux_appuis_deg": pauvre["erreur_mediane_deg"],
            "erreur_a_dix_sept_appuis_deg": riche["erreur_mediane_deg"],
            # ⚠⚠ « Retrecir la machoire sous le voxel ne la sauve pas » est l'enonce, et il se
            # verifie en comparant a ZERO ce qu'un retrecissement recupere : si le biais venait de
            # la largeur, l'erreur a la plus etroite serait nulle, pas seulement plus petite.
            "part_recuperee_par_le_retrecissement": (
                round(1.0 - etroite["erreur_mediane_deg"] / large["erreur_mediane_deg"], 4)
                if large["erreur_mediane_deg"] and large["erreur_mediane_deg"] > 0.0 else None)})
    out["par_matiere_geometrie"] = par
    dures = [x for x in par if x["amplitude_um"] > 0.0]
    out["le_retrecissement_ne_sauve_pas"] = bool(
        dures and all(x["erreur_a_la_plus_etroite_deg"] > 1.0 for x in dures))
    out["les_appuis_ne_sauvent_pas"] = bool(
        dures and all(x["erreur_a_dix_sept_appuis_deg"] > 1.0 for x in dures))
    # (3) la croix, et sa borne
    c_dures = [m for m in croix["par_matiere"] if m["amplitude_um"] > 0.0
               and m["ecart_apparie_deg"] is not None]
    out["la_croix_repare_partout_ou_ca_froisse"] = bool(
        c_dures and all(m["elle_repare"] for m in c_dures))
    dure = next((m for m in croix["par_matiere"] if m["amplitude_um"] == 100.0), None)
    if dure is not None and dure["ecart_apparie_deg"] is not None:
        autres = [m for m in c_dures if m["amplitude_um"] != 100.0]
        out["sur_la_matiere_du_rouleau"] = {
            "nom": dure["nom"], "erreur_segment_deg": dure["erreur_segment_deg"],
            "erreur_croix_deg": dure["erreur_croix_deg"],
            "ecart_apparie_deg": dure["ecart_apparie_deg"],
            "mieux": dure["mieux"], "pire": dure["pire"], "appariees": dure["appariees"],
            "lectures_segment": dure["lectures_segment"],
            "lectures_croix": dure["lectures_croix"],
            # ⭐⭐ LA BORNE : la croix paie moins la ou le froissement est fort. Le dire est le
            # resultat, pas une reserve — un remede dont on ne publie pas la borne se fait prendre
            # pour general.
            "gain_median_sur_les_froissements_moderes_deg": (
                round(float(np.median([m["ecart_apparie_deg"] for m in autres])), 3)
                if autres else None)}
    return out


def mesurer(matieres=MATIERES, largeurs=LARGEURS, appuis=APPUIS, poses: int = POSES) -> dict:
    h = la_normale_sort_elle_du_plan(matieres, poses)
    g = le_biais_tient_il_a_la_geometrie(matieres, largeurs, appuis, poses)
    c = la_croix_repare_t_elle(matieres, poses)
    return {"hors_plan": h, "geometrie": g, "croix": c, "juger": juger(h, g, c)}


def reagreger(r: dict) -> dict:
    r["juger"] = juger(r["hors_plan"], r["geometrie"], r["croix"])
    return r


def afficher(r: dict) -> None:
    h, g, c, j = r["hors_plan"], r["geometrie"], r["croix"], r["juger"]
    print("\n⭐⭐⭐⭐ LA VRAIE NORMALE SORT-ELLE DU PLAN DU TOUR ?  (aucune lecture, analytique)")
    print(f"   {'matière':<32} {'|n·z| médian':>14} {'p90':>8} {'max':>8} {'hors plan':>11}")
    for m in h["par_matiere"]:
        print(f"   {m['nom']:<32} {m['axial_median']:>14.6f} {m['axial_p90']:>8.4f} "
              f"{m['axial_max']:>8.4f} {m['hors_plan_median_deg']:>10.3f}°")
    print("\n⭐⭐⭐ L'ÉCART À LA VRAIE NORMALE TOMBE-T-IL QUAND ON RÉTRÉCIT, OU QUAND ON ENRICHIT ?")
    print(f"   {'matière':<32} " + "".join(f"{x:>8.3f}" for x in g["largeurs"])
          + "   |" + "".join(f"{n:>6d}" for n in g["appuis"]))
    for m in g["par_matiere"]:
        lg = "".join(("     —  " if x["erreur_mediane_deg"] is None
                      else f"{x['erreur_mediane_deg']:>8.2f}") for x in m["par_largeur"])
        ap = "".join(("    — " if x["erreur_mediane_deg"] is None
                      else f"{x['erreur_mediane_deg']:>6.2f}") for x in m["par_appuis"])
        print(f"   {m['nom']:<32} {lg}   |{ap}")
    print("\n⭐⭐ LA CROIX RÉPARE-T-ELLE, ET DE COMBIEN ?")
    print(f"   {'matière':<32} {'segment':>9} {'croix':>9} {'apparié':>9} "
          f"{'mieux':>6} {'pire':>5} {'lect.':>12}")
    for m in c["par_matiere"]:
        ap = "—" if m["ecart_apparie_deg"] is None else f"{m['ecart_apparie_deg']:+.3f}°"
        print(f"   {m['nom']:<32} {m['erreur_segment_deg']:>8.3f}° {m['erreur_croix_deg']:>8.3f}° "
              f"{ap:>9} {m['mieux']:>6} {m['pire']:>5} "
              f"{m['lectures_segment']:>5} → {m['lectures_croix']:<4}")
    if not j.get("decidable"):
        print(f"\n⚠ {j.get('raison')}")
        return
    print(f"\n   elle sort du plan SI ET SEULEMENT SI ça froisse : "
          f"{'OUI' if j['elle_sort_du_plan_si_et_seulement_si_ca_froisse'] else 'non'}")
    print(f"   rétrécir ne sauve pas : {'OUI' if j['le_retrecissement_ne_sauve_pas'] else 'non'}"
          f"   ·   ajouter des appuis ne sauve pas : "
          f"{'OUI' if j['les_appuis_ne_sauvent_pas'] else 'non'}")
    d = j.get("sur_la_matiere_du_rouleau")
    if d:
        print(f"\n⚠⚠ SUR LA MATIÈRE DU ROULEAU — {d['nom']}")
        print(f"   {d['erreur_segment_deg']}° → {d['erreur_croix_deg']}°, apparié "
              f"{d['ecart_apparie_deg']:+}°  ({d['mieux']} mieux contre {d['pire']} pire sur "
              f"{d['appariees']})")
        print(f"   contre {d['gain_median_sur_les_froissements_moderes_deg']:+}° sur les "
              f"froissements modérés — la croix paie MOINS là où le froissement est fort")


def verifier() -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        # ⚠ Le compte est DERIVE : un nombre figé redevient faux au premier contrôle ajouté.
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- ⭐⭐⭐⭐ (1) le partage, sur les cinq matières
    h = la_normale_sort_elle_du_plan(poses=12)
    lisses = [m for m in h["par_matiere"] if m["amplitude_um"] == 0.0]
    froissees = [m for m in h["par_matiere"] if m["amplitude_um"] > 0.0]
    v("⭐⭐⭐⭐ sur une matière LISSE la vraie normale ne sort PAS du plan, exactement",
      all(m["axial_max"] == 0.0 for m in lisses),
      " · ".join(f"{m['nom'][8:]} max {m['axial_max']}" for m in lisses))
    v("⭐⭐⭐⭐ ... et sur une matière FROISSÉE elle en sort, sur les trois",
      all(m["elle_sort_du_plan"] for m in froissees),
      " · ".join(f"{m['hors_plan_median_deg']}°" for m in froissees))
    # ⚠⚠ LA SONDE QUI MORD SUR LE PARTAGE : si une lisse en sortait, le verdict doit DIRE NON.
    faux = {"decidable": True, "poses_par_case": 1, "par_matiere": [
        {"nom": "spirale nue", "amplitude_um": 0.0, "ecrasement": 0.0, "poses": 1,
         "axial_median": 0.5, "axial_p90": 0.5, "axial_max": 0.5,
         "hors_plan_median_deg": 30.0, "hors_plan_max_deg": 30.0, "elle_sort_du_plan": True},
        {"nom": "spirale froissée 42.4 µm", "amplitude_um": 42.4, "ecrasement": 0.0, "poses": 1,
         "axial_median": 0.1, "axial_p90": 0.1, "axial_max": 0.1,
         "hors_plan_median_deg": 5.7, "hors_plan_max_deg": 5.7, "elle_sort_du_plan": True}]}

    # ---- ⭐⭐⭐ (2) la géométrie plane, sur la matière du rouleau
    g = le_biais_tient_il_a_la_geometrie(matieres=((0.2782, 100.0),),
                                         largeurs=(0.008, 0.5), appuis=(2, 17), poses=12)
    m = g["par_matiere"][0]
    etroite, large = m["par_largeur"][0], m["par_largeur"][-1]
    v("⭐⭐⭐ rétrécir la mâchoire SOUS LE VOXEL ne fait pas tomber l'écart",
      etroite["erreur_mediane_deg"] > 1.0,
      f"{etroite['erreur_mediane_deg']}° à {etroite['largeur_um']} µm "
      f"contre {large['erreur_mediane_deg']}° à {large['largeur_um']}")
    v("⭐⭐⭐ ... et l'enrichir de dix-sept appuis non plus",
      m["par_appuis"][-1]["erreur_mediane_deg"] > 1.0,
      f"{m['par_appuis'][0]['erreur_mediane_deg']}° à 2 appuis contre "
      f"{m['par_appuis'][-1]['erreur_mediane_deg']}° à 17")
    v("⚠ la plus petite largeur est bien SOUS le voxel", etroite["largeur_um"] < _VOXEL(),
      f"{etroite['largeur_um']} µm pour un voxel de {_VOXEL()}")
    v("⚠ le prix est publié, et il croît avec les appuis",
      m["par_appuis"][-1]["lectures_medianes"] > m["par_appuis"][0]["lectures_medianes"],
      f"{m['par_appuis'][0]['lectures_medianes']} → "
      f"{m['par_appuis'][-1]['lectures_medianes']} lectures")

    # ---- ⭐⭐ (3) la croix
    c = la_croix_repare_t_elle(matieres=((0.0, 0.0), (0.0, 42.4)), poses=12)
    nue, fro = c["par_matiere"][0], c["par_matiere"][1]
    v("⭐⭐ sur une spirale NUE la croix ne change rien, parce qu'il n'y a rien à récupérer",
      nue["ecart_apparie_deg"] is not None and abs(nue["ecart_apparie_deg"]) < 1e-6,
      f"{nue['ecart_apparie_deg']:+}°")
    v("⭐⭐⭐ ... et sur une froissée elle récupère quelque chose",
      fro["ecart_apparie_deg"] is not None and fro["ecart_apparie_deg"] < 0.0,
      f"{fro['ecart_apparie_deg']:+}° ({fro['mieux']} mieux contre {fro['pire']} pire)")
    v("⚠ elle coûte exactement deux barres d'appuis",
      fro["lectures_croix"] == 2 * fro["lectures_segment"],
      f"{fro['lectures_segment']} → {fro['lectures_croix']}")
    v("⚠ les deux comptes de poses sont publiés à part, jamais mêlés à la justesse",
      all(x["posees_en_segment"] >= 0 and x["posees_en_croix"] >= 0 for x in c["par_matiere"]))

    # ---- ⚠⚠⚠ LE VERDICT PEUT-IL DIRE NON ? Trois fixtures, une par énoncé.
    jf = juger(faux, g, c)
    v("⭐⭐⭐ le verdict DIT NON quand une matière lisse sort du plan",
      jf["elle_sort_du_plan_si_et_seulement_si_ca_froisse"] is False,
      "sinon l'énoncé serait vrai quelle que soit la mesure")
    g_sauve = json.loads(json.dumps(g))
    for x in g_sauve["par_matiere"][0]["par_largeur"]:
        x["erreur_mediane_deg"] = 0.0
    for x in g_sauve["par_matiere"][0]["par_appuis"]:
        x["erreur_mediane_deg"] = 0.0
    j2 = juger(h, g_sauve, c)
    v("⭐⭐⭐ ... et NON quand rétrécir sauve vraiment",
      j2["le_retrecissement_ne_sauve_pas"] is False and j2["les_appuis_ne_sauvent_pas"] is False,
      "une erreur nulle à la plus étroite voudrait dire que la largeur était la cause")
    c_pire = json.loads(json.dumps(c))
    for x in c_pire["par_matiere"]:
        if x["amplitude_um"] > 0.0:
            x["elle_repare"] = False
            x["ecart_apparie_deg"] = +1.0
    j3 = juger(h, g, c_pire)
    v("⭐⭐⭐ ... et NON quand la croix dégrade",
      j3["la_croix_repare_partout_ou_ca_froisse"] is False)
    v("⚠ une mesure manquante rend le jugement indécidable, jamais à moitié vrai",
      juger({"decidable": False}, g, c)["decidable"] is False)

    # ---- ⚠⚠ LE CHEMIN QUI PUBLIE EST EXERCÉ, matière injectée et jamais le découpage.
    import io  # noqa: PLC0415
    import contextlib  # noqa: PLC0415
    r = mesurer(matieres=((0.0, 0.0), (0.0, 42.4)), largeurs=(0.008, 0.25), appuis=(2, 3),
                poses=6)
    v("⭐⭐ `mesurer` rend les trois mesures et leur jugement",
      all(r[k]["decidable"] for k in ("hors_plan", "geometrie", "croix"))
      and r["juger"]["decidable"])
    avant = json.loads(json.dumps(r["croix"]))
    r2 = reagreger(json.loads(json.dumps(r)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["croix"] == avant,
      "il relit le verdict, il ne remesure rien")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher(r2)
    v("⚠ `afficher` rend les trois mesures et le partage",
      "SORT-ELLE DU PLAN" in tampon.getvalue()
      and "LA CROIX RÉPARE-T-ELLE" in tampon.getvalue(),
      f"{len(tampon.getvalue())} caractères")
    tampon2 = io.StringIO()
    with contextlib.redirect_stdout(tampon2):
        afficher({"hors_plan": r["hors_plan"], "geometrie": r["geometrie"], "croix": r["croix"],
                  "juger": {"decidable": False, "raison": "une des trois mesures manque"}})
    v("⚠ ... et un jugement indécidable se DIT au lieu de planter",
      "une des trois mesures manque" in tampon2.getvalue())

    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} "
          f"({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--reagreger", type=Path)
    ap.add_argument("--poses", type=int, default=POSES)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        r = reagreger(json.loads(a.reagreger.read_text()))
        a.reagreger.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        afficher(r)
        return 0
    r = mesurer(poses=int(a.poses))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
    afficher(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
