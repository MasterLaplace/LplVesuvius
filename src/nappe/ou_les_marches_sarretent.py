#!/usr/bin/env python3
"""La pince ne meurt pas de dérive, elle meurt d'ARRÊT — et la fenêtre dit pourquoi.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL COMMENCE PAR UN COMPTE QUE PERSONNE N'AVAIT FAIT. `142` à `148`
ont toutes travaillé sur l'identité de la feuille : quelle mémoire, quelle lecture, quel cap. Or les
suivis que `148` range disent où les marches finissent, et le compte est sans appel — sur les échecs
de la pince munie du cap de `144`, **49 sont des marches qui s'ARRÊTENT** et **13** seulement
finissent sur la mauvaise feuille. Quatre échecs sur cinq sont d'une autre nature que celle qu'on
traitait.

⭐⭐⭐ ET LA CAUSE EST DANS LES MÊMES DONNÉES : ce sont les POSES qui échouent, pas la contrainte. Une
marche arrêtée compte **21** refus de pose médians et **0** refus de contrainte, et elle s'arrête à
**6 %** du tour. Trente et une des quarante-neuf sont sur la matière que `140` retient — toutes, sans
exception.

⭐⭐⭐⭐ ET L'EXPLICATION EST GÉOMÉTRIQUE ET EXACTE. `142` a donné à la recherche d'un interstice une
fenêtre large d'UNE épaisseur, centrée sur l'attente : elle contient exactement un interstice, donc
elle le contient tant qu'il n'a pas bougé de plus d'une DEMI-épaisseur. Or un froissement le DÉPLACE.
Mesuré sur la fixture : à 42,4 µm d'amplitude le déplacement ne dépasse jamais la demi-épaisseur,
à 100 µm il la dépasse sur une part non nulle de la matière. La fenêtre est structurellement trop
étroite pour la matière du rouleau, et c'est pour ça que personne n'y a jamais bouclé un tour.

⭐⭐ LA RÉPARATION NE DEMANDE AUCUNE CONSTANTE : élargir la fenêtre de ce que le suiveur a DÉJÀ VU —
de combien l'interstice qu'il vient de trouver s'écarte de la demi-épaisseur où il l'attendait —
plafonné à une demi-épaisseur NOMINALE, parce qu'au-delà la fenêtre atteindrait l'interstice voisin.

Usage :
    uv run python src/nappe/ou_les_marches_sarretent.py --verifier
    uv run python src/nappe/ou_les_marches_sarretent.py --json docs/mesures/ou_les_marches_sarretent.json
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
                                            _PAS, _resumer_un_bras, _VOXEL, une_case,
                                            une_reussite)
from un_cap_qui_lit_la_cause import le_discriminant  # noqa: E402
from un_cap_qui_tourne import apparie  # noqa: E402

FENETRE = 32
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
POINTS_DE_MATIERE = 20000
GRAINE_DES_POINTS = 7
# (nom, fenetre_elargie) — deux façons de lire « de combien l'interstice a bougé », et
# ⚠ chacune est contaminée à sa manière : `149` mesure laquelle, et combien ça coûte.
VARIANTES = (("fenêtre nominale (`144`)", ""),
             ("élargie sur la mesurée", "mesuree"),
             ("élargie sur la nominale", "nominale"))
LE_PRECEDENT = RACINE / "docs" / "mesures" / "lire_la_cause_sous_le_bruit.json"
LES_ARRETS = RACINE / "docs" / "mesures" / "la_memoire_fait_elle_avancer_de_travers.json"


def ou_les_marches_sarretent(precedent: dict | None, bras: str = "la pince") -> dict:
    """De quoi les marches meurent, sur les suivis que `148` range — sans une marche de plus.

    ⭐⭐⭐⭐ C'EST LE COMPTE QUI DÉPLACE LE TRAVAIL. Un échec peut être de deux natures, et elles
    n'appellent pas le même remède : la marche BOUCLE son tour en revenant sur une autre feuille —
    c'est un problème d'identité, celui que `142` à `148` traitent — ou elle ne boucle pas du tout,
    parce qu'elle s'est ARRÊTÉE. Les compter séparément est la seule façon de savoir lequel domine.

    ⚠ Et la cause d'un arrêt se lit dans les mêmes suivis : `poses_refusees` compte les fois où la
    mâchoire n'a trouvé aucun interstice encadré, `refus` les fois où la contrainte de `142` a
    refusé le saut. Ce sont deux mécanismes différents, et les publier ensemble dirait « ça
    s'arrête » sans dire de quoi.
    """
    if not precedent:
        return {"decidable": False, "raison": "la mesure de `148` est absente"}
    g = precedent.get("sur_la_grille", {})
    cases = [c for c in g.get("cases", [])
             if int(c.get("fenetre_du_cap", 0)) == FENETRE
             and not c.get("avance_sur_la_lecture") and not c.get("corrige_le_bruit")
             and not str(c.get("cap_tournant", "")) and not c.get("enroulement_du_cap")]
    if not cases:
        return {"decidable": False, "raison": "`148` ne publie pas le cap statique de `144`"}
    arrets, mauvaises, bouclees, poses_ratees = [], [], [], 0
    par_matiere: dict[str, list[int]] = {}
    for c in cases:
        for x in c["bras"][bras]["suivis"]:
            cle = c["nom"]
            par_matiere.setdefault(cle, [0, 0])
            par_matiere[cle][1] += 1
            if not x.get("decidable"):
                poses_ratees += 1
                continue
            if une_reussite(x):
                bouclees.append(x)
            elif x.get("tour_boucle"):
                mauvaises.append(x)
            else:
                arrets.append(x)
                par_matiere[cle][0] += 1

    def med(xs, cle, dec=3):
        v = [x[cle] for x in xs if x.get(cle) is not None]
        return round(float(statistics.median(v)), dec) if v else None

    return {"decidable": True, "bras": bras, "source": "`148`, cap statique de `144`",
            "marches": sum(v[1] for v in par_matiere.values()),
            "bouclees_sur_la_bonne_feuille": len(bouclees),
            "arretees": len(arrets), "sur_une_autre_feuille": len(mauvaises),
            "poses_impossibles_au_depart": poses_ratees,
            "les_arrets_dominent": bool(len(arrets) > len(mauvaises)),
            "une_marche_arretee": {
                "part_du_tour_atteinte": med(arrets, "part_du_tour", 4),
                "poses_refusees": med(arrets, "poses_refusees", 1),
                "refus_de_contrainte": med(arrets, "refus", 1),
                "pas": med(arrets, "pas", 1)},
            "une_marche_bouclee": {
                "part_du_tour_atteinte": med(bouclees, "part_du_tour", 4),
                "poses_refusees": med(bouclees, "poses_refusees", 1),
                "refus_de_contrainte": med(bouclees, "refus", 1),
                "pas": med(bouclees, "pas", 1)},
            # ⚠ « C'est la pose qui échoue » est un ÉNONCÉ, pas une impression : les refus de pose
            # d'une marche arrêtée dépassent ses refus de contrainte.
            "cest_la_pose_qui_echoue": bool(
                (med(arrets, "poses_refusees", 1) or 0.0)
                > (med(arrets, "refus", 1) or 0.0)),
            "par_matiere": [{"nom": n, "arretees": v[0], "marches": v[1]}
                            for n, v in sorted(par_matiere.items())]}


def la_fenetre_contient_elle_linterstice(matieres=MATIERES, points: int = POINTS_DE_MATIERE,
                                         graine: int = GRAINE_DES_POINTS) -> dict:
    """Une fenêtre d'UNE épaisseur contient-elle l'interstice que le froissement a déplacé ?

    ⭐⭐⭐⭐ L'ÉNONCÉ EST GÉOMÉTRIQUE ET IL N'A AUCUN SEUIL. La fenêtre de `142` est centrée sur la
    demi-épaisseur et large d'une épaisseur : elle va de zéro à une épaisseur. Un interstice déplacé
    de `d` s'y trouve donc si et seulement si `|d|` reste sous la DEMI-épaisseur — au-delà il sort
    par un bord, et `linterstice` refuse à juste titre un minimum non encadré.

    ⚠ Le déplacement se lit DIRECTEMENT sur la fixture, qui le fabrique : aucune estimation, aucune
    marche. Ce qui est mesuré est la part de la matière que la fenêtre ne peut pas atteindre.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    demi = 0.5 * pas_um
    rng = np.random.default_rng(int(graine))
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    cy, cx = None, None
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        cy, cx = vol.centre_yx_vx
        th = rng.uniform(-np.pi, np.pi, int(points))
        r = RAYON_MM * 1000.0 / voxel_um
        p = np.stack([np.full(th.size, 2000.0), cy + r * np.sin(th), cx + r * np.cos(th)], axis=1)
        d = np.abs(np.asarray(vol._deplacement_um(p * voxel_um), dtype=np.float64))
        out.append({"nom": f"{'spirale nue' if not (ecr or amp) else 'spirale'}"
                           f"{' écrasée' if ecr else ''}"
                           f"{f' et froissée {amp:g} µm' if (ecr and amp) else ''}"
                           f"{f' froissée {amp:g} µm' if (amp and not ecr) else ''}",
                    "amplitude_um": float(amp),
                    "deplacement_median_um": round(float(np.median(d)), 3),
                    "deplacement_max_um": round(float(d.max()), 3),
                    "part_hors_fenetre_pour_mille": int(round(1000.0 * float(np.mean(d >= demi)))),
                    "la_fenetre_la_contient": bool(float(d.max()) < demi)})
    return {"decidable": bool(out), "points": int(points), "graine": int(graine),
            "demi_epaisseur_um": round(demi, 3),
            "par_matiere": out,
            "matieres_hors_datteinte": [x["nom"] for x in out if not x["la_fenetre_la_contient"]],
            "la_fenetre_est_trop_etroite_quelque_part":
                bool(any(not x["la_fenetre_la_contient"] for x in out))}


def _filtre(elargie: str):
    def f(c):
        return (str(c.get("fenetre_elargie", "")) == str(elargie)
                and int(c.get("fenetre_du_cap", 0)) == FENETRE
                and not c.get("corrige_le_bruit") and not c.get("avance_sur_la_lecture")
                and not str(c.get("cap_tournant", "")) and not c.get("enroulement_du_cap"))
    return f


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    cases = []
    for m in matieres:
        for b in bruits:
            for nom, el in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=FENETRE, fenetre_elargie=str(el))
                c["variante"] = nom
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(FENETRE),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"nom": n, "elargie": str(e)} for n, e in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _compte(cases, bras: str, quoi: str) -> int:
    n = 0
    for c in cases:
        for x in c["bras"][bras]["suivis"]:
            if not x.get("decidable"):
                continue
            if quoi == "arretees" and not x.get("tour_boucle"):
                n += 1
            elif quoi == "autre_feuille" and x.get("tour_boucle") and not une_reussite(x):
                n += 1
    return n


def _med(cases, bras: str, cle: str, dec: int = 3):
    xs = [x[cle] for c in cases for x in c["bras"][bras]["suivis"]
          if x.get("decidable") and x.get(cle) is not None]
    return round(float(statistics.median(xs)), dec) if xs else None


def par_variante(grille: dict) -> dict:
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["elargie"])
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
                "arretees": _compte(cases, nom, "arretees"),
                "sur_une_autre_feuille": _compte(cases, nom, "autre_feuille"),
                "part_du_tour_mediane": _med(cases, nom, "part_du_tour", 4),
                "poses_refusees_medianes": _med(cases, nom, "poses_refusees", 1),
                "marge_mediane_um": _med(cases, nom, "marge_mediane_um", 3)}
        bloc["par_matiere"] = [
            {"nom": nom,
             "arretees": _compte([c for c in cases if c["nom"] == nom], "la pince", "arretees"),
             "part_du_tour_mediane": _med([c for c in cases if c["nom"] == nom], "la pince",
                                          "part_du_tour", 4),
             **{n: int(sum(c["bras"][n].get("reussites") or 0
                           for c in cases if c["nom"] == nom)) for n in BRAS}}
            for nom in dict.fromkeys(c["nom"] for c in cases)]
        out.append(bloc)
    return {"par_variante": out}


def elargir_repare_t_il(grille: dict, pv: list[dict], bras: str = "la pince") -> dict:
    """Élargir la fenêtre répare-t-il — et fait-elle d'abord ce qu'elle prétend ?

    ⭐⭐⭐ DEUX ÉNONCÉS SÉPARÉS, ET C'EST EXPRÈS. « Elle arrête moins de marches » est ce que le
    mécanisme prédit ; « elle rend plus de réussites sans en perdre » est ce qui compte pour le
    graal. Les confondre laisserait passer une règle qui gagne pour une autre raison que la sienne.

    ⚠⚠ La victoire est JOINTE depuis `147` : plus de réussites ET aucune perdue sur les départs
    appariés. Un solde seul est satisfait par un déplacement.

    ⚠ Les deux élargissements sont jugés SÉPARÉMENT et aucun n'est choisi après coup : ils sont
    nommés dans `VARIANTES` avant la mesure, et chacun porte sa contamination dans son nom.
    """
    temoin = next((x for x in pv if not x["elargie"]), None)
    larges = [x for x in pv if x["elargie"]]
    if temoin is None or not larges:
        return {"decidable": False, "raison": "il faut la fenêtre nominale et au moins une élargie"}

    def dure(x):
        return next((m for m in x["par_matiere"] if "100" in m["nom"]), {})

    contre = []
    for x in larges:
        ap = apparie(grille, _filtre(temoin["elargie"]), _filtre(x["elargie"]), bras)
        contre.append({
            "nom": x["nom"], "elargie": x["elargie"],
            "reussites": x[bras]["reussites"], "arretees": x[bras]["arretees"],
            "marge_mediane_um": x[bras]["marge_mediane_um"],
            "apparie": ap,
            "elle_arrete_moins": bool(x[bras]["arretees"] < temoin[bras]["arretees"]),
            "elle_selargit_vraiment": bool(x[bras]["marge_mediane_um"] is not None
                                           and x[bras]["marge_mediane_um"] > 0.0),
            "elle_repare": bool(x[bras]["reussites"] > temoin[bras]["reussites"]
                                and ap.get("elle_ne_perd_rien") is True),
            "sur_la_matiere_de_140": {
                "arretees": dure(x).get("arretees"),
                "part_du_tour": dure(x).get("part_du_tour_mediane"),
                "reussites": dure(x).get("la pince")}})
    meilleure = max(contre, key=lambda y: y["reussites"])
    return {"decidable": True, "bras": bras,
            "le_temoin": {"nom": temoin["nom"], "reussites": temoin[bras]["reussites"],
                          "arretees": temoin[bras]["arretees"],
                          "marge_mediane_um": temoin[bras]["marge_mediane_um"],
                          "sur_la_matiere_de_140": {
                              "arretees": dure(temoin).get("arretees"),
                              "part_du_tour": dure(temoin).get("part_du_tour_mediane"),
                              "reussites": dure(temoin).get("la pince")}},
            "par_regle": contre,
            "la_meilleure": meilleure["nom"],
            "toutes_selargissent_vraiment": bool(all(y["elle_selargit_vraiment"] for y in contre)),
            "une_fenetre_elargie_repare": bool(meilleure["elle_repare"]),
            "une_fenetre_elargie_arrete_moins": bool(any(y["elle_arrete_moins"] for y in contre))}


def les_temoins_internes(grille: dict, precedent: dict | None) -> dict:
    """La fenêtre NOMINALE est la règle de `144` : elle doit rendre 114 · 107 · 108."""
    if not precedent:
        return {"decidable": False, "raison": "la mesure de `145` est absente, le témoin manque"}
    ref = next((v for v in precedent.get("juger", {}).get("par_variante", [])
                if v.get("bloc") == 1 and not v.get("corrige")), None)
    ici = next((x for x in par_variante(grille)["par_variante"] if not x["elargie"]), None)
    if ref is None or ici is None:
        return {"decidable": False, "raison": "la variante nominale manque d'un côté"}
    par_bras = {n: {"ici": ici[n]["reussites"], "dans_145": ref[n]["reussites"],
                    "identique": bool(ici[n]["reussites"] == ref[n]["reussites"])} for n in BRAS}
    return {"decidable": True, "nom": ici["nom"], **par_bras,
            "le_protocole_est_le_meme": bool(all(par_bras[n]["identique"] for n in BRAS))}


def juger(grille: dict, precedent: dict | None, arrets: dict | None = None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    return {"decidable": True, "par_variante": pv,
            "les_temoins_internes": les_temoins_internes(grille, precedent),
            "ou_les_marches_sarretent": ou_les_marches_sarretent(arrets),
            "la_fenetre_contient_elle_linterstice": la_fenetre_contient_elle_linterstice(),
            "elargir_repare_t_il": elargir_repare_t_il(grille, pv)}


def mesurer(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, departs: int = DEPARTS,
            tours: float = TOURS, precedent: Path = LE_PRECEDENT,
            arrets: Path = LES_ARRETS) -> dict:
    grille = sur_la_grille(matieres, bruits, variantes, departs, tours)
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    ar = json.loads(Path(arrets).read_text()) if Path(arrets).exists() else None
    return {"sur_la_grille": grille,
            "le_precedent": str(Path(precedent).name) if ref else None,
            "les_arrets": str(Path(arrets).name) if ar else None,
            "juger": juger(grille, ref, ar)}


def reagreger(r: dict, precedent: Path = LE_PRECEDENT, arrets: Path = LES_ARRETS) -> dict:
    """Recalcule les résumés et les verdicts depuis les suivis rangés — sans remarcher."""
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    ar = json.loads(Path(arrets).read_text()) if Path(arrets).exists() else None
    r["juger"] = juger(r["sur_la_grille"], ref, ar)
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
    o = j["ou_les_marches_sarretent"]
    if o.get("decidable"):
        marque = "★" if o["les_arrets_dominent"] else "✗"
        print(f"\n{marque} de quoi les marches de `148` meurent-elles : {o['arretees']} ARRÊTÉES "
              f"contre {o['sur_une_autre_feuille']} sur une autre feuille, pour "
              f"{o['bouclees_sur_la_bonne_feuille']} réussies sur {o['marches']}")
        a_, b_ = o["une_marche_arretee"], o["une_marche_bouclee"]
        print(f"   arrêtée : {a_['part_du_tour_atteinte']} de tour, {a_['poses_refusees']} refus "
              f"de POSE, {a_['refus_de_contrainte']} refus de CONTRAINTE, {a_['pas']} pas")
        print(f"   bouclée : {b_['part_du_tour_atteinte']} de tour, {b_['poses_refusees']} refus "
              f"de POSE, {b_['refus_de_contrainte']} refus de CONTRAINTE, {b_['pas']} pas")
        print(f"   c'est la POSE qui échoue : {o['cest_la_pose_qui_echoue']}")
    f_ = j["la_fenetre_contient_elle_linterstice"]
    if f_.get("decidable"):
        print(f"\n   le froissement déplace-t-il l'interstice hors d'une fenêtre d'une épaisseur "
              f"(demi-épaisseur {f_['demi_epaisseur_um']} µm) :")
        for x in f_["par_matiere"]:
            print(f"     {x['nom']:>34} : déplacement médian {x['deplacement_median_um']:>7} µm, "
                  f"max {x['deplacement_max_um']:>7} µm, hors fenêtre "
                  f"{x['part_hors_fenetre_pour_mille']:>3} ‰ — contenue : "
                  f"{x['la_fenetre_la_contient']}")
    print(f"\n   {'règle':>26} | {'réussites':>9} | {'arrêtées':>8} | {'autre f.':>8} | "
          f"{'part tour':>9} | {'marge µm':>8}")
    for x in j["par_variante"]:
        b = x["la pince"]
        print(f"   {x['nom']:>26} | {b['reussites']:>9d} | {b['arretees']:>8d} | "
              f"{b['sur_une_autre_feuille']:>8d} | {b['part_du_tour_mediane']:>9} | "
              f"{b['marge_mediane_um']:>8}")
    e_ = j["elargir_repare_t_il"]
    if e_.get("decidable"):
        marque = "★★★★" if e_["une_fenetre_elargie_repare"] else "✗"
        t_ = e_["le_temoin"]
        print(f"\n{marque} élargir la fenêtre répare-t-il ? {e_['une_fenetre_elargie_repare']} — "
              f"le témoin « {t_['nom']} » rend {t_['reussites']} réussites et {t_['arretees']} "
              f"arrêts")
        for y in e_["par_regle"]:
            ap = y["apparie"]
            print(f"     « {y['nom']} » : {y['reussites']} réussites, {y['arretees']} arrêts, "
                  f"marge {y['marge_mediane_um']} µm — "
                  f"{ap.get('gains')} gagnées pour {ap.get('pertes')} perdues, "
                  f"arrête moins {y['elle_arrete_moins']}, répare {y['elle_repare']}")
            d_ = y["sur_la_matiere_de_140"]
            print(f"         sur la matière de `140` : {d_['arretees']} arrêtées, part du tour "
                  f"{d_['part_du_tour']}, réussites {d_['reussites']} — contre "
                  f"{t_['sur_la_matiere_de_140']['arretees']}, "
                  f"{t_['sur_la_matiere_de_140']['part_du_tour']}, "
                  f"{t_['sur_la_matiere_de_140']['reussites']}")
        print(f"   toutes s'élargissent vraiment : {e_['toutes_selargissent_vraiment']}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    v("le filtre distingue les trois fenêtres, et il les distingue par leur NOM",
      _filtre("")({"fenetre_elargie": "", "fenetre_du_cap": FENETRE, "corrige_le_bruit": False,
                   "avance_sur_la_lecture": False, "cap_tournant": "",
                   "enroulement_du_cap": False})
      and not _filtre("mesuree")({"fenetre_elargie": "nominale", "fenetre_du_cap": FENETRE,
                                  "corrige_le_bruit": False, "avance_sur_la_lecture": False,
                                  "cap_tournant": "", "enroulement_du_cap": False}),
      "« mesurée » et « nominale » sont deux estimateurs, pas deux réglages du même")

    # ---- ⭐⭐⭐⭐ de quoi les marches meurent : arrêt ou mauvaise feuille
    def suivi(deg, fin, part, halts, refus, boucle, derive):
        return {"decidable": True, "depart_deg": float(deg), "fin": fin, "part_du_tour": part,
                "poses_refusees": halts, "refus": refus, "pas": 100, "tour_boucle": boucle,
                "derive_en_feuilles": derive, "marge_mediane_um": 0.0}

    def case148(nom, suivis):
        return {"nom": nom, "bruit": 0.0, "departs": len(suivis), "fenetre_du_cap": FENETRE,
                "corrige_le_bruit": False, "avance_sur_la_lecture": False, "cap_tournant": "",
                "enroulement_du_cap": False,
                "bras": {b: {"suivis": list(suivis)} for b in BRAS}}

    arrete = suivi(0, "la pince ne peut plus avancer", 0.06, 21, 0, False, 0.1)
    ailleurs = suivi(60, "tour bouclé", 1.0, 0, 0, True, 3.0)
    reussie = suivi(120, "tour bouclé", 1.0, 0, 0, True, 0.1)
    p148 = {"sur_la_grille": {"cases": [case148("A", [arrete, arrete, ailleurs, reussie])]}}
    o = ou_les_marches_sarretent(p148)
    v("⭐⭐⭐⭐ les trois destins d'une marche sont comptés SÉPARÉMENT",
      o["decidable"] and o["arretees"] == 2 and o["sur_une_autre_feuille"] == 1
      and o["bouclees_sur_la_bonne_feuille"] == 1,
      "arrêtée, bouclée ailleurs, bouclée juste — trois remèdes différents")
    v("⭐⭐⭐ et « les arrêts dominent » est un énoncé qui peut échouer",
      o["les_arrets_dominent"] is True
      and ou_les_marches_sarretent({"sur_la_grille": {"cases": [
          case148("A", [arrete, ailleurs, ailleurs])]}})["les_arrets_dominent"] is False)
    v("⭐⭐⭐ « c'est la POSE qui échoue » compare les deux refus, il ne les additionne pas",
      o["cest_la_pose_qui_echoue"] is True
      and ou_les_marches_sarretent({"sur_la_grille": {"cases": [case148("A", [
          suivi(0, "la pince ne peut plus avancer", 0.06, 1, 30, False, 0.1)])]}})
      ["cest_la_pose_qui_echoue"] is False,
      "une pince qui meurt de sa contrainte et une qui meurt de sa fenêtre n'ont pas le même "
      "remède")
    v("⚠ une pose impossible au départ est comptée à part, jamais comme un arrêt",
      ou_les_marches_sarretent({"sur_la_grille": {"cases": [case148("A", [
          {"decidable": False}])]}})["poses_impossibles_au_depart"] == 1)
    v("sans `148`, le compte est indécidable", not ou_les_marches_sarretent(None)["decidable"])
    v("... et une mesure de `148` sans cap statique aussi",
      not ou_les_marches_sarretent({"sur_la_grille": {"cases": [
          {**case148("A", [reussie]), "cap_tournant": "taux"}]}})["decidable"])

    # ---- ⭐⭐⭐⭐ la fenêtre contient-elle l'interstice
    f_ = la_fenetre_contient_elle_linterstice(points=4000)
    v("⭐⭐ la demi-épaisseur est DÉRIVÉE du pas, jamais posée",
      abs(f_["demi_epaisseur_um"] - 0.5 * _PAS()) < 1e-9, f"{f_['demi_epaisseur_um']} µm")
    nue = next(x for x in f_["par_matiere"] if x["amplitude_um"] == 0.0)
    moyen = next(x for x in f_["par_matiere"] if x["amplitude_um"] == 42.4)
    fort = next(x for x in f_["par_matiere"] if x["amplitude_um"] == 100.0)
    v("⭐⭐ une matière LISSE ne déplace rien, donc la fenêtre la contient",
      nue["deplacement_max_um"] == 0.0 and nue["la_fenetre_la_contient"] is True)
    v("⭐⭐⭐⭐ à 42,4 µm le déplacement reste sous la demi-épaisseur, à 100 µm il la dépasse",
      moyen["la_fenetre_la_contient"] is True and fort["la_fenetre_la_contient"] is False
      and fort["part_hors_fenetre_pour_mille"] > 0,
      f"max {moyen['deplacement_max_um']} µm contre {fort['deplacement_max_um']} µm pour une "
      f"demi-épaisseur de {f_['demi_epaisseur_um']} µm")
    v("⭐⭐ le déplacement maximal d'une matière est BORNÉ par son amplitude, et c'est la fixture "
      "qui le dit",
      all(x["deplacement_max_um"] <= x["amplitude_um"] + 1e-6 for x in f_["par_matiere"]),
      "aucune matière ne déplace plus que ce qu'on lui a demandé")
    v("⚠ et la matière du rouleau est nommée comme hors d'atteinte",
      f_["la_fenetre_est_trop_etroite_quelque_part"] is True
      and any("100" in n for n in f_["matieres_hors_datteinte"]))

    # ---- la grille et le verdict
    def suiviG(deg, boucle, derive, marge):
        return {"decidable": True, "depart_deg": float(deg), "tour_boucle": boucle,
                "derive_en_feuilles": derive, "part_du_tour": 1.0 if boucle else 0.06,
                "poses_refusees": 0 if boucle else 20, "marge_mediane_um": marge,
                "memoire_mediane": 0.5}

    def caseG(el, nom, etats, marge):
        sv = [suiviG(60 * i, b, d, marge) for i, (b, d) in enumerate(etats)]
        return {"ecrasement": 0.0, "amplitude_um": 100.0 if "100" in nom else 0.0, "bruit": 0.0,
                "nom": nom, "departs": len(sv), "fenetre_du_cap": FENETRE, "bloc_du_cap": 1,
                "corrige_le_bruit": False, "enroulement_du_cap": False, "cap_tournant": "",
                "avance_sur_la_lecture": False, "fenetre_elargie": str(el),
                "bras": {b: {"reussites": sum(1 for x in sv if une_reussite(x)),
                             "memes_feuilles": 0, "tours_boucles": 0, "suivis": sv}
                         for b in BRAS}}

    VAR = [{"nom": "fenêtre nominale (`144`)", "elargie": ""},
           {"nom": "élargie sur la mesurée", "elargie": "mesuree"}]

    def grille_de(nom_etats, el_etats, marge=12.0):
        return {"fenetre": FENETRE, "departs": len(nom_etats), "variantes": VAR,
                "cases": [caseG("", "é+f 100 µm", nom_etats, 0.0),
                          caseG("mesuree", "é+f 100 µm", el_etats, marge)]}

    g = grille_de([(False, 0.1), (False, 0.1), (True, 0.1)],
                  [(True, 0.1), (True, 0.1), (True, 0.1)])
    pv = par_variante(g)["par_variante"]
    v("les réussites, les arrêts et la marge sortent par règle",
      pv[0]["la pince"]["reussites"] == 1 and pv[0]["la pince"]["arretees"] == 2
      and pv[1]["la pince"]["reussites"] == 3 and pv[1]["la pince"]["marge_mediane_um"] == 12.0)
    e_ = elargir_repare_t_il(g, pv)
    v("⭐⭐⭐⭐ élargir répare quand elle ajoute des réussites SANS en perdre",
      e_["decidable"] and e_["une_fenetre_elargie_repare"] is True
      and e_["par_regle"][0]["apparie"]["pertes"] == 0,
      "3 contre 1, 2 gagnées, 0 perdue")
    v("⭐⭐⭐ et « elle arrête moins » est un énoncé SÉPARÉ de « elle répare »",
      e_["par_regle"][0]["elle_arrete_moins"] is True)
    dep = grille_de([(False, 0.1), (True, 0.1), (True, 0.1)],
                    [(True, 0.1), (True, 0.1), (False, 0.1)])
    v("⭐⭐⭐⭐ ... et elle ne répare PAS en déplaçant, même à total égal",
      elargir_repare_t_il(dep, par_variante(dep)["par_variante"])
      ["une_fenetre_elargie_repare"] is False,
      "le solde seul est satisfait par un déplacement, depuis `147`")
    fige = grille_de([(False, 0.1), (False, 0.1), (True, 0.1)],
                     [(True, 0.1), (True, 0.1), (True, 0.1)], marge=0.0)
    v("⭐⭐⭐ une fenêtre annoncée élargie dont la marge est NULLE est démasquée",
      elargir_repare_t_il(fige, par_variante(fige)["par_variante"])
      ["toutes_selargissent_vraiment"] is False,
      "sinon « ça ne change rien » se confondrait avec « rien n'a été essayé »")
    v("sans la fenêtre nominale, le verdict est indécidable",
      not elargir_repare_t_il(g, [x for x in pv if x["elargie"]])["decidable"])
    v("un jugement sans case est indécidable", not juger({"cases": []}, None)["decidable"])

    ref = {"juger": {"par_variante": [
        {"nom": "brute", "bloc": 1, "corrige": False, **{n: {"reussites": 1} for n in BRAS}}]}}
    t = les_temoins_internes(g, ref)
    v("⭐⭐ le témoin interne compare la fenêtre nominale à ce que `145` publie",
      t["decidable"] and t["le_protocole_est_le_meme"] is True)
    faux = json.loads(json.dumps(ref))
    faux["juger"]["par_variante"][0]["la pince"]["reussites"] = 9
    v("⭐⭐⭐ ... et il DIT quand le module partagé a bougé",
      les_temoins_internes(g, faux)["le_protocole_est_le_meme"] is False)
    v("sans `145`, le témoin est indécidable",
      not les_temoins_internes(g, None)["decidable"])

    # ---- ⭐ de bout en bout, sur les deux matières que la fenêtre départage
    nominale = une_case((0.2782, 100.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                        fenetre_du_cap=FENETRE)
    elargie = une_case((0.2782, 100.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                       fenetre_du_cap=FENETRE, fenetre_elargie="mesuree")
    lisse_n = une_case((0.2782, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                       fenetre_du_cap=FENETRE)
    lisse_e = une_case((0.2782, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                       fenetre_du_cap=FENETRE, fenetre_elargie="mesuree")

    def lu(c, cle):
        xs = [x[cle] for x in c["bras"]["la pince"]["suivis"]
              if x.get("decidable") and x.get(cle) is not None]
        return xs[0] if xs else None

    v("⭐⭐⭐ sur la matière du rouleau, la fenêtre élargie va bien plus loin avant de s'arrêter",
      lu(elargie, "part_du_tour") > lu(nominale, "part_du_tour"),
      f"{lu(elargie, 'part_du_tour')} de tour contre {lu(nominale, 'part_du_tour')}")
    v("⭐⭐ et la marge qu'elle emploie est PLAFONNÉE à une demi-épaisseur nominale",
      lu(elargie, "marge_mediane_um") <= 0.5 * _PAS() + 1e-9,
      f"{lu(elargie, 'marge_mediane_um')} µm pour un plafond de {0.5 * _PAS()} µm")
    v("⭐⭐ sur une matière LISSE elle ne s'élargit presque pas : rien ne l'y appelle",
      lu(lisse_e, "marge_mediane_um") < 0.05 * _PAS(),
      f"{lu(lisse_e, 'marge_mediane_um')} µm")
    v("⚠ et la fenêtre NOMINALE ne s'élargit jamais, ce qui est ce qui rend le témoin possible",
      lu(nominale, "marge_mediane_um") == 0.0 and lu(lisse_n, "marge_mediane_um") == 0.0)
    v("... et la variante voyage jusque dans la case",
      elargie["fenetre_elargie"] == "mesuree" and nominale["fenetre_elargie"] == "")

    petit = {"sur_la_grille": {"cases": [nominale, elargie], "departs": 1, "tours": 0.05,
                               "fenetre": FENETRE, "bruits": [0.0],
                               "largeur_en_pas": LARGEUR_DE_REFERENCE,
                               "variantes": [{"nom": n, "elargie": str(e)}
                                             for n, e in VARIANTES[:2]]}}
    petit["juger"] = juger(petit["sur_la_grille"], None, None)
    v("⭐ réagréger depuis les suivis rangés rend le MÊME verdict, sans remarcher",
      reagreger(json.loads(json.dumps(petit)), Path("/inexistant.json"),
                Path("/inexistant.json"))["juger"] == petit["juger"])

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
