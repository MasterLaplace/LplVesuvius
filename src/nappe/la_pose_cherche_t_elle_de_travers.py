#!/usr/bin/env python3
"""La mâchoire n'échoue pas parce qu'elle est LARGE, elle échoue parce qu'elle cherche DE TRAVERS.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL FERME UNE BOUCLE ENTRE TROIS TRANCHES. `149` établit que la pince
meurt d'ARRÊT et que c'est la POSE qui échoue — 21 refus de pose médians contre 0 refus de
contrainte. `148` mesure que le cap incline la normale EMPLOYÉE de **40,569°** sur la matière que
`140` retient. Il restait à savoir si ces deux faits sont le même : une pose le long d'une normale
inclinée de quarante degrés réussit-elle encore ?

⭐⭐⭐ ET LA PREMIÈRE HYPOTHÈSE EST RÉFUTÉE AVANT LA SECONDE. La plus évidente était la LARGEUR : une
mâchoire s'étend latéralement, et sur un froissement plus court qu'elle ses appuis tombent sur des
profondeurs très différentes. ⚠ `142` a bien balayé la largeur — mais sur une spirale ÉCRASÉE, sans
aucun froissement, donc la question n'avait jamais été posée. Elle l'est ici, et la réponse est non :
la pose réussit à TOUTES les largeurs, sur toutes les matières.

⭐⭐ CE QUI LA FAIT ÉCHOUER EST L'INCLINAISON, et la mesure la quantifie sans aucune marche : on pose
à un départ FRAIS, le long d'une normale qu'on incline soi-même, et on compte. Une pose ne coûte que
quelques lectures, donc cette mesure est mille fois moins chère qu'une grille.

⚠⚠ ET LA RÉPARATION SYMÉTRIQUE DE `148` EST MESURÉE ICI : `148` avait fait AVANCER le suiveur sur la
lecture en laissant les mâchoires sur le mélange. L'autre moitié — POSER sur la lecture en laissant
la marche au cap — n'avait jamais été essayée.

Usage :
    uv run python src/nappe/la_pose_cherche_t_elle_de_travers.py --verifier
    uv run python src/nappe/la_pose_cherche_t_elle_de_travers.py \\
        --json docs/mesures/la_pose_cherche_t_elle_de_travers.json
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

from la_pince_tient_elle_la_feuille import (BRAS, LARGEUR_DE_REFERENCE,  # noqa: E402
                                            LONGUEUR_DONDE_UM, MATIERES, RAYON_MM, _matiere,
                                            _PAS, _resumer_un_bras, _tourner, _VOXEL, poser,
                                            un_depart, une_case, une_reussite)
from un_cap_qui_lit_la_cause import le_discriminant  # noqa: E402
from un_cap_qui_tourne import apparie  # noqa: E402

FENETRE = 32
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
POSES = 60
LARGEURS = (0.0625, 0.125, 0.25, 0.375)
INCLINAISONS_DEG = (0.0, 10.0, 20.0, 30.0, 40.0, 50.0)
# (nom, pose_sur_la_lecture)
VARIANTES = (("pose sur le mélange (`144`)", False), ("pose sur la lecture", True))
LE_PRECEDENT = RACINE / "docs" / "mesures" / "lire_la_cause_sous_le_bruit.json"
LE_PENCHANT = RACINE / "docs" / "mesures" / "la_memoire_fait_elle_avancer_de_travers.json"


def _nom(ecr: float, amp: float) -> str:
    causes = []
    if ecr > 0.0:
        causes.append("écrasée")
    if amp > 0.0:
        causes.append(f"froissée {amp:g} µm")
    return "spirale nue" if not causes else "spirale " + " et ".join(causes)


def la_pose_resiste_t_elle(matieres=MATIERES, largeurs=LARGEURS,
                           inclinaisons=INCLINAISONS_DEG, poses: int = POSES) -> dict:
    """Une pose réussit-elle, selon la largeur de la mâchoire et l'inclinaison de sa normale ?

    ⭐⭐⭐⭐ LA MESURE NE MARCHE PAS, ELLE POSE — ET C'EST CE QUI LA REND POSSIBLE. `149` établit que
    ce qui tue une marche est le refus de POSE ; une pose se teste seule, à un départ frais, pour
    quelques lectures. Mille fois moins cher qu'une grille de marches, et la question est la même.

    ⚠⚠ L'INCLINAISON EST IMPOSÉE, PAS OBSERVÉE : on tourne la normale d'un angle CONNU avant de
    poser. Observer l'inclinaison d'une marche et son échec ensemble ne dirait pas lequel cause
    l'autre ; l'imposer le dit.

    ⚠ Les départs sont ceux d'`un_depart`, donc recalés EXACTEMENT sur une feuille : ce que la
    mesure isole est bien la pose, pas la qualité du point de départ.
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
                "poses": int(poses), "par_largeur": [], "par_inclinaison": []}
        for lg in largeurs:
            n = sum(1 for d0, n0 in departs
                    if poser(vol, d0, n0, float(lg) * pas_um, pas_um, voxel_um, True) is not None)
            bloc["par_largeur"].append({
                "largeur_en_pas": float(lg), "largeur_um": round(float(lg) * pas_um, 1),
                "reussies": int(n),
                "part_pour_mille": int(round(1000.0 * n / max(int(poses), 1)))})
        for deg in inclinaisons:
            n = sum(1 for d0, n0 in departs
                    if poser(vol, d0, _tourner(n0, np.radians(float(deg))),
                             LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, True) is not None)
            bloc["par_inclinaison"].append({
                "inclinaison_deg": float(deg), "reussies": int(n),
                "part_pour_mille": int(round(1000.0 * n / max(int(poses), 1)))})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "largeur_de_reference": float(LARGEUR_DE_REFERENCE),
            "largeurs": [float(x) for x in largeurs],
            "inclinaisons_deg": [float(x) for x in inclinaisons],
            "par_matiere": out}


def la_largeur_est_elle_en_cause(pose: dict) -> dict:
    """La largeur de la mâchoire empêche-t-elle la pose ?

    ⭐⭐⭐ L'ÉNONCÉ EST EXACT ET IL PEUT ÉCHOUER : si la largeur était en cause, la pose réussirait
    STRICTEMENT MOINS à la largeur de référence qu'à la plus étroite, et sur les matières froissées
    d'abord. Une seule matière qui n'y obéit pas suffit à réfuter.

    ⚠ `142` a balayé la largeur, mais sur une spirale ÉCRASÉE sans froissement : la question posée
    ici ne l'avait jamais été.
    """
    if not pose.get("decidable"):
        return {"decidable": False, "raison": "aucune pose mesurée"}
    etroite = min(pose["largeurs"])
    ref = pose["largeur_de_reference"]
    par = []
    for m in pose["par_matiere"]:
        e = next((x for x in m["par_largeur"] if x["largeur_en_pas"] == etroite), None)
        r = next((x for x in m["par_largeur"] if x["largeur_en_pas"] == ref), None)
        if e is None or r is None:
            continue
        par.append({"nom": m["nom"], "froissee": bool(m["amplitude_um"] > 0.0),
                    "etroite_pour_mille": e["part_pour_mille"],
                    "reference_pour_mille": r["part_pour_mille"],
                    "la_reference_pose_moins": bool(r["part_pour_mille"]
                                                    < e["part_pour_mille"])})
    froissees = [x for x in par if x["froissee"]]
    return {"decidable": bool(par), "largeur_etroite": etroite, "largeur_de_reference": ref,
            "par_matiere": par,
            "la_largeur_est_en_cause": bool(froissees
                                            and all(x["la_reference_pose_moins"]
                                                    for x in froissees))}


def linclinaison_est_elle_en_cause(pose: dict, penchant: dict | None) -> dict:
    """L'inclinaison de la normale empêche-t-elle la pose — et à l'angle que `148` mesure ?

    ⭐⭐⭐⭐ DEUX ÉNONCÉS, ET LE SECOND EST CELUI QUI FERME LA BOUCLE. Le premier : la pose réussit
    strictement moins à la plus forte inclinaison qu'à zéro, sur toutes les matières. Le second : à
    l'inclinaison que `148` mesure RÉELLEMENT sur la matière du rouleau, la pose y réussit déjà
    moins qu'à normale droite — c'est ce qui relie l'arrêt de `149` au penchant de `148`.

    ⚠ L'angle de `148` est LU, jamais recopié : sans sa mesure, le second énoncé est indécidable et
    le dit.
    """
    if not pose.get("decidable"):
        return {"decidable": False, "raison": "aucune pose mesurée"}
    fort = max(pose["inclinaisons_deg"])
    par = []
    for m in pose["par_matiere"]:
        z = next((x for x in m["par_inclinaison"] if x["inclinaison_deg"] == 0.0), None)
        f = next((x for x in m["par_inclinaison"] if x["inclinaison_deg"] == fort), None)
        if z is None or f is None:
            continue
        par.append({"nom": m["nom"], "droite_pour_mille": z["part_pour_mille"],
                    "penchee_pour_mille": f["part_pour_mille"],
                    "elle_pose_moins": bool(f["part_pour_mille"] < z["part_pour_mille"])})
    out = {"decidable": bool(par), "inclinaison_forte_deg": fort, "par_matiere": par,
           "pencher_fait_echouer_la_pose": bool(par and all(x["elle_pose_moins"] for x in par))}
    # ⭐ L'angle que `148` mesure sur la matière du rouleau, et ce que la pose y devient.
    if penchant:
        v = next((x for x in penchant.get("juger", {}).get("par_variante", [])
                  if x.get("fenetre") and not x.get("avance_sur_la_lecture")), None)
        if v is not None:
            dure = next((m for m in v.get("par_matiere", []) if "100" in m["nom"]), None)
            mat = next((m for m in pose["par_matiere"] if m["amplitude_um"] == 100.0), None)
            if dure is not None and mat is not None:
                angle = float(dure["inclinaison_mediane_deg"])
                proche = min(mat["par_inclinaison"],
                             key=lambda x: abs(x["inclinaison_deg"] - angle))
                droite = next(x for x in mat["par_inclinaison"] if x["inclinaison_deg"] == 0.0)
                out["ce_que_148_mesure"] = {
                    "matiere": mat["nom"], "inclinaison_deg": round(angle, 3),
                    "inclinaison_mesuree_la_plus_proche_deg": proche["inclinaison_deg"],
                    "pose_a_cet_angle_pour_mille": proche["part_pour_mille"],
                    "pose_a_normale_droite_pour_mille": droite["part_pour_mille"],
                    "la_pose_y_echoue_deja": bool(proche["part_pour_mille"]
                                                  < droite["part_pour_mille"])}
    return out


def _filtre(lecture: bool):
    def f(c):
        return (bool(c.get("pose_sur_la_lecture", False)) is bool(lecture)
                and int(c.get("fenetre_du_cap", 0)) == FENETRE
                and not c.get("corrige_le_bruit") and not c.get("avance_sur_la_lecture")
                and not str(c.get("cap_tournant", "")) and not c.get("enroulement_du_cap")
                and not str(c.get("fenetre_elargie", "")))
    return f


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    cases = []
    for m in matieres:
        for b in bruits:
            for nom, lec in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=FENETRE, pose_sur_la_lecture=bool(lec))
                c["variante"] = nom
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(FENETRE),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"nom": n, "lecture": bool(x)} for n, x in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _compte_arrets(cases, bras: str) -> int:
    return sum(1 for c in cases for x in c["bras"][bras]["suivis"]
               if x.get("decidable") and not x.get("tour_boucle"))


def _med(cases, bras: str, cle: str, dec: int = 3):
    xs = [x[cle] for c in cases for x in c["bras"][bras]["suivis"]
          if x.get("decidable") and x.get(cle) is not None]
    return round(float(statistics.median(xs)), dec) if xs else None


def par_variante(grille: dict) -> dict:
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["lecture"])
        cases = [c for c in grille["cases"] if f(c)]
        if not cases:
            continue
        d = le_discriminant(grille, f)["par_bruit"]
        bloc = {**v, "cases": len(cases),
                "bruits_ou_elle_separe": [x["bruit"] for x in d if x["la_lecture_separe"]],
                "par_bruit": d}
        for nom in BRAS:
            bloc[nom] = {
                "reussites": int(sum(c["bras"][nom].get("reussites") or 0 for c in cases)),
                "arretees": _compte_arrets(cases, nom),
                # ⚠⚠ cle source `poses_impossibles`, nom publie inchange : cf. `168`.
                "poses_refusees_medianes": _med(cases, nom, "poses_impossibles", 1),
                "inclinaison_mediane_deg": (
                    None if _med(cases, nom, "inclinaison_mediane_mdeg", 1) is None
                    else round(_med(cases, nom, "inclinaison_mediane_mdeg", 1) / 1000.0, 3))}
        bloc["par_matiere"] = [
            {"nom": nom,
             "arretees": _compte_arrets([c for c in cases if c["nom"] == nom], "la pince"),
             **{n: int(sum(c["bras"][n].get("reussites") or 0
                           for c in cases if c["nom"] == nom)) for n in BRAS}}
            for nom in dict.fromkeys(c["nom"] for c in cases)]
        out.append(bloc)
    return {"par_variante": out}


def poser_sur_la_lecture_repare(grille: dict, pv: list[dict], bras: str = "la pince") -> dict:
    """Poser sur la lecture plutôt que sur le mélange répare-t-il ?

    ⭐⭐⭐ C'est la moitié SYMÉTRIQUE de celle que `148` a mesurée : là, le suiveur AVANÇAIT sur la
    lecture et les mâchoires restaient sur le mélange ; ici les mâchoires SE POSENT sur la lecture
    et la marche reste au cap.

    ⚠⚠ La victoire est JOINTE depuis `147`, et « elle arrête moins » est un énoncé SÉPARÉ.
    """
    temoin = next((x for x in pv if not x["lecture"]), None)
    repare = next((x for x in pv if x["lecture"]), None)
    if temoin is None or repare is None:
        return {"decidable": False, "raison": "il faut les deux variantes"}
    ap = apparie(grille, _filtre(False), _filtre(True), bras)
    return {"decidable": True, "bras": bras,
            "reussites_du_temoin": temoin[bras]["reussites"],
            "reussites_de_la_reparation": repare[bras]["reussites"],
            "arretees_du_temoin": temoin[bras]["arretees"],
            "arretees_de_la_reparation": repare[bras]["arretees"],
            "inclinaison_du_temoin_deg": temoin[bras]["inclinaison_mediane_deg"],
            "inclinaison_de_la_reparation_deg": repare[bras]["inclinaison_mediane_deg"],
            "apparie": ap,
            "elle_arrete_moins": bool(repare[bras]["arretees"] < temoin[bras]["arretees"]),
            "elle_repare": bool(repare[bras]["reussites"] > temoin[bras]["reussites"]
                                and ap.get("elle_ne_perd_rien") is True)}


def les_temoins_internes(grille: dict, precedent: dict | None) -> dict:
    """La pose sur le MÉLANGE est la règle de `144` : elle doit rendre 114 · 107 · 108."""
    if not precedent:
        return {"decidable": False, "raison": "la mesure de `145` est absente, le témoin manque"}
    ref = next((v for v in precedent.get("juger", {}).get("par_variante", [])
                if v.get("bloc") == 1 and not v.get("corrige")), None)
    ici = next((x for x in par_variante(grille)["par_variante"] if not x["lecture"]), None)
    if ref is None or ici is None:
        return {"decidable": False, "raison": "la variante de référence manque d'un côté"}
    par_bras = {n: {"ici": ici[n]["reussites"], "dans_145": ref[n]["reussites"],
                    "identique": bool(ici[n]["reussites"] == ref[n]["reussites"])} for n in BRAS}
    return {"decidable": True, "nom": ici["nom"], **par_bras,
            "le_protocole_est_le_meme": bool(all(par_bras[n]["identique"] for n in BRAS))}


def juger(grille: dict, precedent: dict | None, penchant: dict | None = None,
          pose: dict | None = None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    ps = pose if pose is not None else la_pose_resiste_t_elle()
    return {"decidable": True, "par_variante": pv,
            "les_temoins_internes": les_temoins_internes(grille, precedent),
            "la_pose_resiste_t_elle": ps,
            "la_largeur_est_elle_en_cause": la_largeur_est_elle_en_cause(ps),
            "linclinaison_est_elle_en_cause": linclinaison_est_elle_en_cause(ps, penchant),
            "poser_sur_la_lecture_repare": poser_sur_la_lecture_repare(grille, pv)}


def mesurer(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, departs: int = DEPARTS,
            tours: float = TOURS, precedent: Path = LE_PRECEDENT,
            penchant: Path = LE_PENCHANT) -> dict:
    grille = sur_la_grille(matieres, bruits, variantes, departs, tours)
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    pen = json.loads(Path(penchant).read_text()) if Path(penchant).exists() else None
    return {"sur_la_grille": grille,
            "le_precedent": str(Path(precedent).name) if ref else None,
            "le_penchant": str(Path(penchant).name) if pen else None,
            "juger": juger(grille, ref, pen)}


def reagreger(r: dict, precedent: Path = LE_PRECEDENT, penchant: Path = LE_PENCHANT) -> dict:
    """Recalcule les résumés et les verdicts depuis les suivis rangés — sans remarcher.

    ⚠ Les poses, elles, sont REMESURÉES : elles ne coûtent rien et ne sont pas rangées.
    """
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    pen = json.loads(Path(penchant).read_text()) if Path(penchant).exists() else None
    r["juger"] = juger(r["sur_la_grille"], ref, pen)
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    t = j["les_temoins_internes"]
    if t.get("decidable"):
        marque = "★" if t["le_protocole_est_le_meme"] else "✗"
        print(f"{marque} témoin interne — « {t['nom']} » doit reproduire `144` : "
              + " · ".join(f"{n} {t[n]['ici']} contre {t[n]['dans_145']}" for n in BRAS))
    p_ = j["la_pose_resiste_t_elle"]
    if p_.get("decidable"):
        print(f"\n   poses réussies pour mille, {p_['poses_par_case']} poses par case :")
        print(f"   {'matière':>34} | " + " | ".join(f"l={x:g}" for x in p_["largeurs"]))
        for m in p_["par_matiere"]:
            print(f"   {m['nom']:>34} | "
                  + " | ".join(f"{x['part_pour_mille']:>5}" for x in m["par_largeur"]))
        print(f"\n   {'matière':>34} | "
              + " | ".join(f"{x:g}°" for x in p_["inclinaisons_deg"]))
        for m in p_["par_matiere"]:
            print(f"   {m['nom']:>34} | "
                  + " | ".join(f"{x['part_pour_mille']:>4}" for x in m["par_inclinaison"]))
    lg = j["la_largeur_est_elle_en_cause"]
    if lg.get("decidable"):
        marque = "★" if lg["la_largeur_est_en_cause"] else "✗"
        print(f"\n{marque} la LARGEUR de la mâchoire est-elle en cause ? "
              f"{lg['la_largeur_est_en_cause']} — à {lg['largeur_de_reference']} pas contre "
              f"{lg['largeur_etroite']}")
    inc = j["linclinaison_est_elle_en_cause"]
    if inc.get("decidable"):
        marque = "★★★★" if inc["pencher_fait_echouer_la_pose"] else "✗"
        print(f"{marque} l'INCLINAISON de la normale est-elle en cause ? "
              f"{inc['pencher_fait_echouer_la_pose']} — à {inc['inclinaison_forte_deg']:g}° "
              f"contre 0°")
        c_ = inc.get("ce_que_148_mesure")
        if c_ is not None:
            print(f"   ⭐ ce que `148` mesure sur « {c_['matiere']} » : la normale y penche de "
                  f"{c_['inclinaison_deg']}°, et la pose y réussit "
                  f"{c_['pose_a_cet_angle_pour_mille']} ‰ à "
                  f"{c_['inclinaison_mesuree_la_plus_proche_deg']:g}° contre "
                  f"{c_['pose_a_normale_droite_pour_mille']} ‰ à normale droite — elle échoue "
                  f"déjà : {c_['la_pose_y_echoue_deja']}")
    print(f"\n   {'règle':>28} | {'réussites':>9} | {'arrêtées':>8} | {'refus pose':>10} | "
          f"{'penche':>8}")
    for x in j["par_variante"]:
        b = x["la pince"]
        print(f"   {x['nom']:>28} | {b['reussites']:>9d} | {b['arretees']:>8d} | "
              f"{b['poses_refusees_medianes']:>10} | {b['inclinaison_mediane_deg']:>8}")
    e_ = j["poser_sur_la_lecture_repare"]
    if e_.get("decidable"):
        ap = e_["apparie"]
        marque = "★★★★" if e_["elle_repare"] else "✗"
        print(f"\n{marque} poser sur la LECTURE répare-t-il ? {e_['elle_repare']} — "
              f"{e_['reussites_de_la_reparation']} réussites contre {e_['reussites_du_temoin']}")
        if ap.get("decidable"):
            print(f"   apparié : {ap['gains']} gagnées, {ap['pertes']} perdues, "
                  f"solde {ap['solde']:+d} sur {ap['paires']} départs")
        print(f"   elle arrête moins : {e_['elle_arrete_moins']} — "
              f"{e_['arretees_de_la_reparation']} contre {e_['arretees_du_temoin']}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- ⭐⭐ la largeur et l'inclinaison, sur des poses fabriquees
    def pose_de(par_largeur, par_inclinaison, amp=100.0, nom="spirale froissée 100 µm"):
        return {"decidable": True, "poses_par_case": 10,
                "largeur_de_reference": 0.25, "largeurs": [0.0625, 0.25],
                "inclinaisons_deg": [0.0, 50.0],
                "par_matiere": [{"nom": nom, "ecrasement": 0.0, "amplitude_um": amp, "poses": 10,
                                 "par_largeur": [{"largeur_en_pas": l, "largeur_um": 1.0,
                                                  "reussies": n, "part_pour_mille": n * 100}
                                                 for l, n in par_largeur],
                                 "par_inclinaison": [{"inclinaison_deg": d, "reussies": n,
                                                      "part_pour_mille": n * 100}
                                                     for d, n in par_inclinaison]}]}

    large_coupable = pose_de([(0.0625, 9), (0.25, 4)], [(0.0, 9), (50.0, 9)])
    v("⭐⭐⭐ la largeur est en cause quand la référence pose STRICTEMENT moins que l'étroite",
      la_largeur_est_elle_en_cause(large_coupable)["la_largeur_est_en_cause"] is True,
      "400 ‰ contre 900 ‰")
    v("⭐⭐⭐ ... et elle ne l'est PAS quand la référence pose autant",
      la_largeur_est_elle_en_cause(
          pose_de([(0.0625, 9), (0.25, 9)], [(0.0, 9), (50.0, 9)]))
      ["la_largeur_est_en_cause"] is False,
      "c'est exactement ce que la mesure rend sur la vraie matière")
    v("⚠ une matière LISSE ne compte pas dans ce verdict : la largeur ne peut être en cause que "
      "là où il y a un froissement à traverser",
      la_largeur_est_elle_en_cause(
          pose_de([(0.0625, 9), (0.25, 4)], [(0.0, 9), (50.0, 9)], amp=0.0,
                  nom="spirale nue"))["la_largeur_est_en_cause"] is False)
    v("sans pose mesurée, le verdict de la largeur est indécidable",
      not la_largeur_est_elle_en_cause({"decidable": False})["decidable"])

    penche = pose_de([(0.0625, 9), (0.25, 9)], [(0.0, 9), (50.0, 2)])
    inc = linclinaison_est_elle_en_cause(penche, None)
    v("⭐⭐⭐⭐ l'inclinaison est en cause quand la pose réussit STRICTEMENT moins penchée",
      inc["pencher_fait_echouer_la_pose"] is True, "200 ‰ contre 900 ‰")
    v("⭐⭐⭐ ... et le verdict échoue si UNE SEULE matière n'y obéit pas",
      linclinaison_est_elle_en_cause(
          pose_de([(0.0625, 9), (0.25, 9)], [(0.0, 2), (50.0, 9)]), None)
      ["pencher_fait_echouer_la_pose"] is False,
      "une conclusion unanime ou pas de conclusion")
    v("⚠ sans la mesure de `148`, le lien à l'angle réellement employé est absent, jamais supposé",
      "ce_que_148_mesure" not in inc)
    p148 = {"juger": {"par_variante": [
        {"nom": "cap statique", "fenetre": FENETRE, "avance_sur_la_lecture": False,
         "par_matiere": [{"nom": "spirale froissée 100 µm", "inclinaison_mediane_deg": 40.569}]}]}}
    inc2 = linclinaison_est_elle_en_cause(penche, p148)
    v("⭐⭐⭐⭐ avec `148`, l'angle RÉELLEMENT employé est rapproché de la pose qu'il permet",
      inc2["ce_que_148_mesure"]["inclinaison_deg"] == 40.569
      and inc2["ce_que_148_mesure"]["la_pose_y_echoue_deja"] is True,
      "c'est ce qui relie l'arrêt de `149` au penchant de `148`")
    v("⭐⭐ ... et ce lien peut être NÉGATIF : un angle auquel la pose ne souffre pas le dit",
      linclinaison_est_elle_en_cause(
          pose_de([(0.0625, 9), (0.25, 9)], [(0.0, 9), (50.0, 9)]), p148)
      ["ce_que_148_mesure"]["la_pose_y_echoue_deja"] is False)

    # ---- la grille et le verdict apparié
    def suivi(deg, boucle, derive):
        return {"decidable": True, "depart_deg": float(deg), "tour_boucle": boucle,
                "derive_en_feuilles": derive, "poses_impossibles": 0 if boucle else 20,
                "inclinaison_mediane_mdeg": 9000, "memoire_mediane": 0.5}

    def case(lec, nom, etats):
        sv = [suivi(60 * i, b, d) for i, (b, d) in enumerate(etats)]
        return {"ecrasement": 0.0, "amplitude_um": 100.0 if "100" in nom else 0.0, "bruit": 0.0,
                "nom": nom, "departs": len(sv), "fenetre_du_cap": FENETRE, "bloc_du_cap": 1,
                "corrige_le_bruit": False, "enroulement_du_cap": False, "cap_tournant": "",
                "avance_sur_la_lecture": False, "fenetre_elargie": "",
                "pose_sur_la_lecture": lec,
                "bras": {b: {"reussites": sum(1 for x in sv if une_reussite(x)),
                             "memes_feuilles": 0, "tours_boucles": 0, "suivis": sv}
                         for b in BRAS}}

    VAR = [{"nom": "pose sur le mélange (`144`)", "lecture": False},
           {"nom": "pose sur la lecture", "lecture": True}]

    def grille_de(temoin, lecture):
        return {"fenetre": FENETRE, "departs": len(temoin), "variantes": VAR,
                "cases": [case(False, "froissée 100 µm", temoin),
                          case(True, "froissée 100 µm", lecture)]}

    v("le filtre distingue les deux poses, et écarte les variantes des tranches voisines",
      _filtre(False)(case(False, "x", [(True, 0.1)]))
      and _filtre(True)(case(True, "x", [(True, 0.1)]))
      and not _filtre(False)({**case(False, "x", [(True, 0.1)]), "fenetre_elargie": "mesuree"})
      and not _filtre(False)({**case(False, "x", [(True, 0.1)]),
                              "avance_sur_la_lecture": True}))

    g = grille_de([(False, 0.1), (False, 0.1), (True, 0.1)],
                  [(True, 0.1), (True, 0.1), (True, 0.1)])
    pv = par_variante(g)["par_variante"]
    v("les réussites et les arrêts sortent par variante",
      pv[0]["la pince"]["reussites"] == 1 and pv[0]["la pince"]["arretees"] == 2
      and pv[1]["la pince"]["reussites"] == 3 and pv[1]["la pince"]["arretees"] == 0)
    e_ = poser_sur_la_lecture_repare(g, pv)
    v("⭐⭐⭐⭐ poser sur la lecture répare quand elle ajoute des réussites SANS en perdre",
      e_["decidable"] and e_["elle_repare"] is True and e_["apparie"]["pertes"] == 0,
      "3 contre 1, 2 gagnées, 0 perdue")
    v("⭐⭐⭐ et « elle arrête moins » est un énoncé SÉPARÉ de « elle répare »",
      e_["elle_arrete_moins"] is True)
    dep = grille_de([(False, 0.1), (True, 0.1), (True, 0.1)],
                    [(True, 0.1), (True, 0.1), (False, 0.1)])
    v("⭐⭐⭐⭐ ... et elle ne répare PAS en déplaçant, même à total égal",
      poser_sur_la_lecture_repare(dep, par_variante(dep)["par_variante"])["elle_repare"] is False,
      "le solde seul est satisfait par un déplacement, depuis `147`")
    v("sans la variante de référence, le verdict est indécidable",
      not poser_sur_la_lecture_repare(g, [x for x in pv if x["lecture"]])["decidable"])
    v("un jugement sans case est indécidable", not juger({"cases": []}, None)["decidable"])

    ref = {"juger": {"par_variante": [
        {"nom": "brute", "bloc": 1, "corrige": False, **{n: {"reussites": 1} for n in BRAS}}]}}
    t = les_temoins_internes(g, ref)
    v("⭐⭐ le témoin interne compare la pose de référence à ce que `145` publie",
      t["decidable"] and t["le_protocole_est_le_meme"] is True)
    faux = json.loads(json.dumps(ref))
    faux["juger"]["par_variante"][0]["la pince"]["reussites"] = 9
    v("⭐⭐⭐ ... et il DIT quand le module partagé a bougé",
      les_temoins_internes(g, faux)["le_protocole_est_le_meme"] is False)
    v("sans `145`, le témoin est indécidable", not les_temoins_internes(g, None)["decidable"])

    # ---- ⭐ de bout en bout, sur les vraies matières
    ps = la_pose_resiste_t_elle(matieres=((0.2782, 0.0), (0.2782, 100.0)),
                                largeurs=(0.0625, 0.25), inclinaisons=(0.0, 50.0), poses=24)
    v("⭐⭐ une pose se mesure sans marcher, et la mesure rend bien deux matières",
      ps["decidable"] and len(ps["par_matiere"]) == 2 and ps["poses_par_case"] == 24)
    dure = next(m for m in ps["par_matiere"] if m["amplitude_um"] == 100.0)
    droite = next(x for x in dure["par_inclinaison"] if x["inclinaison_deg"] == 0.0)
    penchee = next(x for x in dure["par_inclinaison"] if x["inclinaison_deg"] == 50.0)
    v("⭐⭐⭐⭐ sur la matière du rouleau, pencher la normale de cinquante degrés fait s'effondrer "
      "la pose",
      penchee["part_pour_mille"] < droite["part_pour_mille"],
      f"{penchee['part_pour_mille']} ‰ contre {droite['part_pour_mille']} ‰ à normale droite")
    etroite = next(x for x in dure["par_largeur"] if x["largeur_en_pas"] == 0.0625)
    large = next(x for x in dure["par_largeur"] if x["largeur_en_pas"] == 0.25)
    v("⭐⭐⭐ ... alors que l'ÉLARGIR ne l'effondre pas : la largeur n'est pas ce qui empêche de "
      "se poser",
      large["part_pour_mille"] > 0.5 * etroite["part_pour_mille"],
      f"{large['part_pour_mille']} ‰ à {0.25} pas contre {etroite['part_pour_mille']} ‰ à 0,0625")
    v("⚠ et la largeur de référence est celle du module partagé, jamais posée ici",
      ps["largeur_de_reference"] == LARGEUR_DE_REFERENCE)

    une = une_case((0.2782, 100.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                   fenetre_du_cap=FENETRE, pose_sur_la_lecture=True)
    v("... et la variante voyage jusque dans la case", une["pose_sur_la_lecture"] is True)

    petit = {"sur_la_grille": {"cases": [
        une_case((0.2782, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                 fenetre_du_cap=FENETRE),
        une_case((0.2782, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                 fenetre_du_cap=FENETRE, pose_sur_la_lecture=True)],
        "departs": 1, "tours": 0.05, "fenetre": FENETRE, "bruits": [0.0],
        "largeur_en_pas": LARGEUR_DE_REFERENCE,
        "variantes": [{"nom": n, "lecture": bool(x)} for n, x in VARIANTES]}}
    petit["juger"] = juger(petit["sur_la_grille"], None, None, ps)
    v("⭐ réagréger depuis les suivis rangés rend le MÊME verdict de marche, sans remarcher",
      reagreger(json.loads(json.dumps(petit)), Path("/inexistant.json"),
                Path("/inexistant.json"))["juger"]["poser_sur_la_lecture_repare"]
      == petit["juger"]["poser_sur_la_lecture_repare"])

    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "précédent absent"})
    v("un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--tours", type=float, default=TOURS)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    p.add_argument("--precedent", type=Path, default=LE_PRECEDENT)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger is not None:
        r = reagreger(json.loads(a.reagreger.read_text()), a.precedent)
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        afficher(r)
        return 0
    r = mesurer(departs=int(a.departs), tours=float(a.tours), precedent=a.precedent)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    afficher(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
