"""Jusqu'où une mâchoire PEUT-elle être juste, et y est-elle déjà ?

⭐⭐⭐⭐ POURQUOI CE FICHIER. `153` établit que le biais d'une mâchoire est structurel — elle rend
`n' = t' × z`, donc elle ne peut pas exprimer la composante axiale que porte une feuille froissée —
et mesure le remède : une mâchoire en CROIX récupère **−5,702°** et **−5,143°** sur les froissements
modérés et **−1,499°** seulement sur la matière du rouleau. La borne était mesurée sans être
expliquée. Ce fichier l'explique en comparant ce que l'instrument rend à l'ÉCHELLE de ce qu'il doit
moyenner.

⭐⭐⭐ L'ÉCHELLE SE CALCULE SANS UNE SEULE LECTURE. Une mâchoire ajuste une surface sur un patch de
largeur `2w` ; la normale y varie, et cette variation se lit analytiquement par `normale_locale`.
Comparer l'erreur de l'instrument à la variation de la matière sur son propre patch dit s'il reste
quelque chose à gagner à taille égale — et la réponse n'est pas la même selon la matière.

⚠⚠ CE QUE CE RAPPORT EST, ET CE QU'IL N'EST PAS. Ce n'est PAS une borne inférieure : pour un patch
symétrique d'une surface lisse, le plan des moindres carrés a la normale du centre au premier ordre,
donc un instrument peut être plus juste que la variation qu'il couvre. C'est une ÉCHELLE — l'ordre
de grandeur que l'instrument doit moyenner. Un rapport proche de un dit que l'instrument travaille à
l'échelle de sa matière ; un rapport de trois dit qu'il reste un facteur trois à prendre à taille
égale, donc un défaut d'instrument encore à trouver.

⭐⭐ ET LA SECONDE BARRE DE LA CROIX A SON PROPRE AXE. La variation le long de `n × t` — la direction
que le segment ne visite jamais — vaut EXACTEMENT ZÉRO sur les matières lisses et davantage que
celle le long de `t` sur les froissées. C'est le contrôle de `153` vu de l'autre bout : la croix ne
peut récupérer que là où cet axe porte quelque chose.

⚠ Les erreurs ne sont PAS recalculées ici : elles sont LUES dans la mesure de `153`. Les recalculer
en ferait deux réponses à une question, et la seconde serait libre de dériver de la première.

Usage :
    uv run python src/nappe/jusquou_une_machoire_peut_elle_etre_juste.py --verifier
    uv run python src/nappe/jusquou_une_machoire_peut_elle_etre_juste.py \\
        --json docs/mesures/jusquou_une_machoire_peut_elle_etre_juste.json
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
                                            LONGUEUR_DONDE_UM, MATIERES, RAYON_MM, Z, _ecart_deg,
                                            _matiere, _nom, _PAS, _VOXEL, un_depart, une_machoire)

POSES = 40
DISTANCES_UM = (1.38, 5.0, 10.81, 21.62, 43.25, 86.5, 173.0, 393.6)
LARGEURS = (0.0625, 0.125, 0.25, 0.375, 0.5)
LE_PLAN = RACINE / "docs" / "mesures" / "la_machoire_est_plane_la_matiere_ne_lest_pas.json"


def _axes(normale):
    """Les deux axes d'une mâchoire : celui du segment, et celui que la croix ajoute.

    ⚠ Le second est `n × t`, qui est DANS la feuille et porte l'axe du rouleau — pas `z` tout court,
    qui sortirait de la feuille dès que la normale penche.
    """
    n = np.asarray(normale, dtype=np.float64)
    n = n / max(float(np.linalg.norm(n)), 1e-12)
    t = np.cross(Z, n)
    nt = float(np.linalg.norm(t))
    if nt < 1e-9:
        return None
    t = t / nt
    return n, t, np.cross(n, t)


def la_normale_varie_t_elle_sur_la_machoire(matieres=MATIERES, distances=DISTANCES_UM,
                                            poses: int = POSES) -> dict:
    """De combien la vraie normale tourne-t-elle sur la largeur d'une mâchoire ?

    ⭐⭐⭐ AUCUNE LECTURE : `normale_locale` est analytique, donc cette mesure est gratuite et
    exacte. C'est l'échelle que l'instrument doit moyenner, et elle se compare directement à ce
    qu'il rend.

    ⚠ Les deux axes sont mesurés séparément parce qu'ils ne disent pas la même chose : `t` est ce
    que le segment visite, `n × t` est ce que seule la croix visite.
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
                "poses": int(poses), "par_distance": []}
        for s in distances:
            le_long_de_t, le_long_de_c, sautes = [], [], 0
            for p0, vrai in departs:
                a = _axes(vrai)
                if a is None:
                    sautes += 1
                    continue
                n, t, c = a
                for axe, cible in ((t, le_long_de_t), (c, le_long_de_c)):
                    q = (np.asarray(p0, dtype=np.float64)
                         + axe * (float(s) / voxel_um)).reshape(1, 3)
                    # ⚠ Hors du volume la question n'a pas de réponse : on SAUTE et on COMPTE,
                    # plutôt que de lire un zéro là où il n'y a rien.
                    if not bool(vol.dans_le_volume(q)[0]):
                        sautes += 1
                        continue
                    cible.append(_ecart_deg(n, vol.normale_locale(q).reshape(3)))
            bloc["par_distance"].append({
                "distance_um": float(s), "sautes": int(sautes),
                "le_long_de_t_deg": (round(float(np.median(le_long_de_t)), 3)
                                     if le_long_de_t else None),
                "le_long_de_n_croix_t_deg": (round(float(np.median(le_long_de_c)), 3)
                                             if le_long_de_c else None)})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "demi_largeur_de_reference_um": round(LARGEUR_DE_REFERENCE * pas_um, 2),
            "longueur_donde_um": float(LONGUEUR_DONDE_UM),
            "distances_um": [float(x) for x in distances], "par_matiere": out}


def letalement_des_appuis(matieres=MATIERES, largeurs=LARGEURS, poses: int = POSES) -> dict:
    """De combien les appuis d'une mâchoire trouvent-ils leur interstice à des profondeurs
    différentes, et quelle inclinaison cet étalement implique-t-il ?

    ⭐⭐ UNE MÂCHOIRE DONT LES APPUIS EXTRÊMES TROUVENT LEUR INTERSTICE À `D` L'UN DE L'AUTRE PENCHE
    D'AU MOINS `arctan(D / 2w)` — c'est de la géométrie, pas un modèle. La mesure dit de combien
    `D` vaut sur chaque matière, donc ce que l'instrument subit avant même d'ajuster quoi que ce
    soit.

    ⚠⚠ ET LE RAPPORT À L'ERREUR EST PUBLIÉ SANS ÊTRE ANNONCÉ JUSTE : `arctan(D/2w)` suppose que les
    deux profondeurs extrêmes sont portées par les deux appuis extrêmes, ce qui n'est vrai que
    parfois — avec trois appuis, l'étalement peut se jouer entre le centre et un bord, donc sur `w`
    et non `2w`. La formule capture donc un ORDRE et pas un niveau, et le rapport mesuré le dit.
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
                "poses": int(poses), "par_largeur": []}
        for lg in largeurs:
            w_um = float(lg) * pas_um
            etal, refus = [], 0
            for d0, vrai in departs:
                m = une_machoire(vol, d0, vrai, +1.0, w_um, pas_um, voxel_um)
                if m is None:
                    refus += 1
                    continue
                x = m["ecarts_um"]
                etal.append(float(max(x) - min(x)))
            d_ = float(np.median(etal)) if etal else None
            bloc["par_largeur"].append({
                "largeur_en_pas": float(lg), "demi_largeur_um": round(w_um, 2),
                "machoires": len(etal), "refusees": int(refus),
                "etalement_um": (round(d_, 3) if d_ is not None else None),
                "inclinaison_impliquee_deg": (
                    round(float(np.degrees(np.arctan(d_ / (2.0 * w_um)))), 3)
                    if d_ is not None else None)})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "largeurs": [float(x) for x in largeurs], "par_matiere": out}


def _erreurs_de_153(plan: dict | None) -> dict:
    """Les erreurs que `153` a mesurées, LUES et jamais recopiées.

    ⚠ Sans sa mesure, la comparaison est indécidable et le dit. Un nombre recopié à la main
    redeviendrait faux le jour où `153` se recalcule.
    """
    if not plan or not plan.get("croix", {}).get("decidable"):
        return {}
    return {m["nom"]: {"segment_deg": m["erreur_segment_deg"], "croix_deg": m["erreur_croix_deg"]}
            for m in plan["croix"]["par_matiere"]
            if m.get("erreur_segment_deg") is not None and m.get("erreur_croix_deg") is not None}


def juger(variation: dict, etalement: dict, plan: dict | None) -> dict:
    """L'instrument travaille-t-il déjà à l'échelle de sa matière, ou reste-t-il à prendre ?

    ⭐⭐⭐⭐ LE SEGMENT ET LA CROIX NE COUVRENT PAS LE MÊME PATCH, donc ils ne se comparent pas à la
    même échelle : le segment ne visite que `t`, la croix visite les deux axes. L'échelle de la
    croix est donc la PLUS GRANDE des deux variations — ce n'est pas un réglage, c'est ce que
    « la variation sur le patch » veut dire quand le patch a deux directions.

    ⚠ Le rapport est publié matière par matière, jamais moyenné : `R4-F119` a déjà montré qu'une
    médiane sur les cinq moyenne sur l'axe où la différence vit.
    """
    if not (variation.get("decidable") and etalement.get("decidable")):
        return {"decidable": False, "raison": "une des deux mesures manque"}
    err = _erreurs_de_153(plan)
    if not err:
        return {"decidable": False, "raison": "la mesure de `153` n'est pas lue, rien à comparer"}
    ref = variation["demi_largeur_de_reference_um"]
    par = []
    for m in variation["par_matiere"]:
        d = next((x for x in m["par_distance"] if abs(x["distance_um"] - ref) < 1e-6), None)
        e = err.get(m["nom"])
        if d is None or e is None or d["le_long_de_t_deg"] is None:
            continue
        v_t, v_c = d["le_long_de_t_deg"], d["le_long_de_n_croix_t_deg"]
        echelle_croix = max(v_t, v_c if v_c is not None else 0.0)
        par.append({
            "nom": m["nom"], "amplitude_um": m["amplitude_um"],
            "variation_le_long_de_t_deg": v_t,
            "variation_le_long_de_n_croix_t_deg": v_c,
            "erreur_du_segment_deg": e["segment_deg"], "erreur_de_la_croix_deg": e["croix_deg"],
            # ⚠ Un rapport ne se calcule pas contre une variation nulle : sur une matière lisse il
            # n'y a rien à moyenner, donc la question n'a pas de sens et se dit plutôt que de
            # rendre un infini.
            "le_segment_au_dessus_de_son_echelle": (round(e["segment_deg"] / v_t, 2)
                                                    if v_t > 0.0 else None),
            "la_croix_au_dessus_de_son_echelle": (round(e["croix_deg"] / echelle_croix, 2)
                                                  if echelle_croix > 0.0 else None),
            "echelle_de_la_croix_deg": round(echelle_croix, 3)})
    out = {"decidable": bool(par), "demi_largeur_de_reference_um": ref, "par_matiere": par}
    # ⭐⭐⭐⭐ LE PARTAGE : la croix est-elle A l'echelle de la matiere, ou au-dessus ?
    dure = next((x for x in par if x["amplitude_um"] == 100.0), None)
    moderees = [x for x in par if 0.0 < x["amplitude_um"] < 100.0]
    if dure and moderees and dure["la_croix_au_dessus_de_son_echelle"] is not None:
        mod = [x["la_croix_au_dessus_de_son_echelle"] for x in moderees
               if x["la_croix_au_dessus_de_son_echelle"] is not None]
        out["sur_la_matiere_du_rouleau"] = {
            "nom": dure["nom"],
            "croix_au_dessus_de_son_echelle": dure["la_croix_au_dessus_de_son_echelle"],
            "sur_les_froissements_moderes": [round(float(x), 2) for x in mod],
            "mediane_des_moderes": round(float(np.median(mod)), 2) if mod else None,
            # ⚠⚠ L'ENONCE EST UNE COMPARAISON, PAS UN SEUIL : la croix est PLUS au-dessus de son
            # echelle sur la matiere du rouleau que sur chacune des moderees. Il peut echouer, et
            # il echoue des qu'une moderee la depasse.
            "elle_est_plus_au_dessus_la_bas": bool(
                mod and all(dure["la_croix_au_dessus_de_son_echelle"] > x for x in mod))}
    # ⚠ La seconde barre ne porte quelque chose QUE la ou ca froisse — le controle de `153` vu de
    # l'autre bout, et il peut echouer.
    lisses = [x for x in par if x["amplitude_um"] == 0.0]
    froissees = [x for x in par if x["amplitude_um"] > 0.0]
    out["le_second_axe_ne_porte_rien_sur_les_lisses"] = bool(
        lisses and all(x["variation_le_long_de_n_croix_t_deg"] == 0.0 for x in lisses))
    out["le_second_axe_porte_sur_les_froissees"] = bool(
        froissees and all((x["variation_le_long_de_n_croix_t_deg"] or 0.0) > 0.0
                          for x in froissees))
    # ⭐ Et l'etalement des appuis : il ordonne les matieres comme l'erreur, sans en donner le niveau.
    e_ref = next((x for x in etalement["par_matiere"][0]["par_largeur"]
                  if abs(x["largeur_en_pas"] - LARGEUR_DE_REFERENCE) < 1e-9), None)
    if e_ref is not None:
        lignes = []
        for m in etalement["par_matiere"]:
            x = next((y for y in m["par_largeur"]
                      if abs(y["largeur_en_pas"] - LARGEUR_DE_REFERENCE) < 1e-9), None)
            e = err.get(m["nom"])
            if x is None or e is None or x["inclinaison_impliquee_deg"] is None:
                continue
            lignes.append({
                "nom": m["nom"], "amplitude_um": m["amplitude_um"],
                "etalement_um": x["etalement_um"],
                "inclinaison_impliquee_deg": x["inclinaison_impliquee_deg"],
                "erreur_du_segment_deg": e["segment_deg"],
                "rapport": (round(e["segment_deg"] / x["inclinaison_impliquee_deg"], 2)
                            if x["inclinaison_impliquee_deg"] > 0.0 else None)})
        out["etalement_a_la_largeur_de_reference"] = lignes
        rapports = [x["rapport"] for x in lignes
                    if x["rapport"] is not None and x["amplitude_um"] > 0.0]
        out["letalement_ordonne_sans_donner_le_niveau"] = bool(
            len(rapports) > 1 and min(rapports) > 1.5)
    return out


def mesurer(matieres=MATIERES, distances=DISTANCES_UM, largeurs=LARGEURS, poses: int = POSES,
            plan: Path = LE_PLAN) -> dict:
    p = json.loads(plan.read_text()) if plan.is_file() else None
    v = la_normale_varie_t_elle_sur_la_machoire(matieres, distances, poses)
    e = letalement_des_appuis(matieres, largeurs, poses)
    return {"variation": v, "etalement": e, "juger": juger(v, e, p), "plan_lu": bool(p)}


def reagreger(r: dict, plan: Path = LE_PLAN) -> dict:
    p = json.loads(plan.read_text()) if plan.is_file() else None
    r["juger"] = juger(r["variation"], r["etalement"], p)
    r["plan_lu"] = bool(p)
    return r


def afficher(r: dict) -> None:
    v, e, j = r["variation"], r["etalement"], r["juger"]
    print("\n⭐⭐⭐ DE COMBIEN LA VRAIE NORMALE TOURNE-T-ELLE SUR LA LARGEUR ?  (analytique, gratuit)")
    print(f"   demi-largeur de référence {v['demi_largeur_de_reference_um']} µm · "
          f"longueur d'onde {v['longueur_donde_um']} µm")
    for axe, cle in (("le long de t   (le segment)", "le_long_de_t_deg"),
                     ("le long de nxt (la croix)  ", "le_long_de_n_croix_t_deg")):
        print(f"\n   {axe}")
        print(f"   {'matière':<32} " + "".join(f"{s:>8.1f}" for s in v["distances_um"]))
        for m in v["par_matiere"]:
            xs = "".join(("     —  " if x[cle] is None else f"{x[cle]:>8.2f}")
                         for x in m["par_distance"])
            print(f"   {m['nom']:<32} {xs}")
    print("\n⭐⭐ L'ÉTALEMENT DES APPUIS, ET L'INCLINAISON QU'IL IMPLIQUE")
    print(f"   {'matière':<32} {'étalement':>11} {'arctan(D/2w)':>14} {'erreur segment':>16} "
          f"{'rapport':>9}")
    for x in j.get("etalement_a_la_largeur_de_reference", []):
        r_ = "—" if x["rapport"] is None else f"{x['rapport']:.2f}"
        print(f"   {x['nom']:<32} {x['etalement_um']:>9.2f} µm {x['inclinaison_impliquee_deg']:>13.2f}°"
              f" {x['erreur_du_segment_deg']:>15.3f}° {r_:>9}")
    if not j.get("decidable"):
        print(f"\n⚠ {j.get('raison')}")
        return
    print("\n⭐⭐⭐⭐ L'INSTRUMENT EST-IL DÉJÀ À L'ÉCHELLE DE SA MATIÈRE ?")
    print(f"   {'matière':<32} {'var. t':>8} {'var. nxt':>10} {'segment':>9} {'croix':>9} "
          f"{'seg/éch':>8} {'crx/éch':>8}")
    for x in j["par_matiere"]:
        s_ = "—" if x["le_segment_au_dessus_de_son_echelle"] is None \
            else f"{x['le_segment_au_dessus_de_son_echelle']:.2f}"
        c_ = "—" if x["la_croix_au_dessus_de_son_echelle"] is None \
            else f"{x['la_croix_au_dessus_de_son_echelle']:.2f}"
        print(f"   {x['nom']:<32} {x['variation_le_long_de_t_deg']:>7.2f}° "
              f"{x['variation_le_long_de_n_croix_t_deg']:>9.2f}° "
              f"{x['erreur_du_segment_deg']:>8.3f}° {x['erreur_de_la_croix_deg']:>8.3f}° "
              f"{s_:>8} {c_:>8}")
    d = j.get("sur_la_matiere_du_rouleau")
    if d:
        print(f"\n⚠⚠ SUR LA MATIÈRE DU ROULEAU — {d['nom']}")
        print(f"   la croix est à {d['croix_au_dessus_de_son_echelle']}× son échelle, contre "
              f"{d['sur_les_froissements_moderes']} sur les froissements modérés "
              f"(médiane {d['mediane_des_moderes']}×)")
        print(f"   elle est plus au-dessus là-bas : "
              f"{'OUI' if d['elle_est_plus_au_dessus_la_bas'] else 'non'}")
    print(f"\n   le second axe ne porte rien sur les lisses : "
          f"{'OUI' if j['le_second_axe_ne_porte_rien_sur_les_lisses'] else 'non'}"
          f"  ·  il porte sur les froissées : "
          f"{'OUI' if j['le_second_axe_porte_sur_les_froissees'] else 'non'}")


def verifier() -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        # ⚠ Le compte est DÉRIVÉ : un nombre figé redevient faux au premier contrôle ajouté.
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    pas_um = _PAS()

    # ---- ⭐⭐⭐ (1) la variation, et son contrôle sur les matières lisses
    var = la_normale_varie_t_elle_sur_la_machoire(distances=(43.25,), poses=12)
    lisses = [m for m in var["par_matiere"] if m["amplitude_um"] == 0.0]
    froissees = [m for m in var["par_matiere"] if m["amplitude_um"] > 0.0]
    v("⭐⭐⭐ le SECOND axe ne porte exactement RIEN sur les matières lisses",
      all(m["par_distance"][0]["le_long_de_n_croix_t_deg"] == 0.0 for m in lisses),
      "c'est le contrôle de `153` vu de l'autre bout : la croix n'y a rien à récupérer")
    v("⭐⭐⭐ ... et il porte quelque chose sur les trois froissées",
      all((m["par_distance"][0]["le_long_de_n_croix_t_deg"] or 0.0) > 0.0 for m in froissees),
      " · ".join(f"{m['par_distance'][0]['le_long_de_n_croix_t_deg']}°" for m in froissees))
    v("⚠ la demi-largeur de référence est celle du module partagé",
      abs(var["demi_largeur_de_reference_um"] - LARGEUR_DE_REFERENCE * pas_um) < 0.01,
      f"{var['demi_largeur_de_reference_um']} µm")
    grand = la_normale_varie_t_elle_sur_la_machoire(matieres=((0.0, 42.4),),
                                                    distances=(5.0, 43.25), poses=12)
    d5, d43 = grand["par_matiere"][0]["par_distance"]
    v("⭐⭐ la normale tourne d'autant plus qu'on s'éloigne, sur les deux axes",
      d43["le_long_de_t_deg"] > d5["le_long_de_t_deg"]
      and d43["le_long_de_n_croix_t_deg"] > d5["le_long_de_n_croix_t_deg"],
      f"t {d5['le_long_de_t_deg']}° → {d43['le_long_de_t_deg']}° · "
      f"nxt {d5['le_long_de_n_croix_t_deg']}° → {d43['le_long_de_n_croix_t_deg']}°")

    # ---- ⭐⭐ (2) l'étalement
    eta = letalement_des_appuis(matieres=((0.0, 0.0), (0.2782, 100.0)),
                                largeurs=(LARGEUR_DE_REFERENCE,), poses=12)
    nue, dure = eta["par_matiere"][0]["par_largeur"][0], eta["par_matiere"][1]["par_largeur"][0]
    v("⭐⭐ sur une spirale nue les appuis trouvent leur interstice à la MÊME profondeur",
      nue["etalement_um"] is not None and nue["etalement_um"] < 1.0,
      f"{nue['etalement_um']} µm — la feuille y est lisse, donc il n'y a rien à étaler")
    v("⭐⭐⭐ ... et sur la matière du rouleau ils s'étalent de plusieurs microns",
      dure["etalement_um"] is not None and dure["etalement_um"] > 5.0,
      f"{dure['etalement_um']} µm, soit {dure['inclinaison_impliquee_deg']}° d'inclinaison "
      f"impliquée")
    v("⚠ l'inclinaison impliquée est DÉRIVÉE de l'étalement et de la largeur, jamais mesurée",
      abs(dure["inclinaison_impliquee_deg"]
          - float(np.degrees(np.arctan(dure["etalement_um"]
                                       / (2.0 * dure["demi_largeur_um"]))))) < 0.01)

    # ---- ⭐⭐⭐⭐ (3) le verdict, contre la mesure de `153`
    plan = json.loads(LE_PLAN.read_text()) if LE_PLAN.is_file() else None
    j = juger(var, eta, plan)
    if plan is None:
        v("⚠ sans la mesure de `153`, le jugement est indécidable et le DIT",
          j["decidable"] is False, j.get("raison", ""))
    else:
        v("⭐⭐⭐⭐ le jugement compare l'erreur de `153` à l'échelle de la matière",
          j["decidable"] and len(j["par_matiere"]) >= 3,
          f"{len(j['par_matiere'])} matières comparées")
        # ⭐⭐⭐ LE CONTROLE QUI REND LE RAPPORT LISIBLE, et ma premiere version l'avait a l'envers :
        # la normale tourne le long de `t` MEME sur une spirale lisse, parce que la spirale courbe.
        # L'echelle n'y est donc pas nulle, et le rapport s'y calcule — il vaut presque zero, ce qui
        # est exactement ce que dit la docstring : sur un patch symetrique d'une surface lisse, le
        # plan des moindres carres est bien meilleur que la variation qu'il couvre. Sans ce point
        # bas, « un rapport de un veut dire a la limite » n'aurait rien contre quoi se lire.
        bas = [x["le_segment_au_dessus_de_son_echelle"] for x in j["par_matiere"]
               if x["amplitude_um"] == 0.0]
        v("⭐⭐⭐ sur une matière LISSE l'instrument est très en dessous de son échelle",
          bas and all(x is not None and x < 0.2 for x in bas),
          f"{bas} — un plan ajusté sur un patch symétrique bat la variation qu'il couvre")
        v("⚠ ... et le rapport se calcule sur les froissées aussi",
          all(x["la_croix_au_dessus_de_son_echelle"] is not None
              for x in j["par_matiere"] if x["amplitude_um"] > 0.0))
        # ⚠⚠ Et il ne se calcule PAS contre une echelle nulle : la sonde le verifie en en fabriquant
        # une, parce qu'aucune matiere de la grille ne rend zero le long de `t`.
        nul = json.loads(json.dumps(var))
        for m in nul["par_matiere"]:
            m["par_distance"][0]["le_long_de_t_deg"] = 0.0
            m["par_distance"][0]["le_long_de_n_croix_t_deg"] = 0.0
        jn = juger(nul, eta, plan)
        v("⚠⚠ contre une échelle NULLE, le rapport n'est pas calculé plutôt que rendu infini",
          all(x["le_segment_au_dessus_de_son_echelle"] is None
              and x["la_croix_au_dessus_de_son_echelle"] is None
              for x in jn["par_matiere"]),
          "une division par zéro rendrait un nombre qui a l'air d'une mesure")

    # ---- ⚠⚠⚠ LE VERDICT PEUT-IL DIRE NON ? Deux fixtures, une par énoncé.
    faux_var = json.loads(json.dumps(var))
    for m in faux_var["par_matiere"]:
        if m["amplitude_um"] == 0.0:
            m["par_distance"][0]["le_long_de_n_croix_t_deg"] = 3.0
    jf = juger(faux_var, eta, plan)
    v("⭐⭐⭐ le verdict DIT NON quand le second axe porte quelque chose sur une lisse",
      jf.get("le_second_axe_ne_porte_rien_sur_les_lisses") is False,
      "sinon l'énoncé serait vrai quelle que soit la mesure")
    if plan is not None and "sur_la_matiere_du_rouleau" in j:
        faux_plan = json.loads(json.dumps(plan))
        for m in faux_plan["croix"]["par_matiere"]:
            if m["amplitude_um"] == 100.0:
                m["erreur_croix_deg"] = 0.1
        j2 = juger(var, eta, faux_plan)
        v("⭐⭐⭐ ... et NON quand la croix est à l'échelle sur la matière du rouleau",
          j2["sur_la_matiere_du_rouleau"]["elle_est_plus_au_dessus_la_bas"] is False,
          "une croix devenue juste là-bas retirerait tout l'énoncé")
    v("⚠ une mesure manquante rend le jugement indécidable, jamais à moitié vrai",
      juger({"decidable": False}, eta, plan)["decidable"] is False)

    # ---- ⚠⚠ LE CHEMIN QUI PUBLIE EST EXERCÉ, matière injectée et jamais le découpage.
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as dossier:
        absent = Path(dossier) / "pas_de_plan.json"
        r = mesurer(matieres=((0.0, 0.0), (0.0, 42.4)), distances=(5.0, 43.25),
                    largeurs=(LARGEUR_DE_REFERENCE,), poses=6, plan=absent)
        v("⭐⭐ `mesurer` rend les deux mesures et dit qu'il n'a pas lu `153`",
          r["variation"]["decidable"] and r["etalement"]["decidable"]
          and r["plan_lu"] is False and r["juger"]["decidable"] is False,
          "un fichier absent se DIT, il ne se devine pas")
        avant = json.loads(json.dumps(r["etalement"]))
        r2 = reagreger(json.loads(json.dumps(r)), plan=absent)
        v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["etalement"] == avant,
          "il relit le verdict, il ne remesure rien")
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(r2)
        v("⚠ `afficher` rend les deux mesures et dit que le jugement manque",
          "LA VRAIE NORMALE TOURNE" in tampon.getvalue()
          and "rien à comparer" in tampon.getvalue(),
          f"{len(tampon.getvalue())} caractères")

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
