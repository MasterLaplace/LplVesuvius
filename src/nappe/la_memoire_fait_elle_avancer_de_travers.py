#!/usr/bin/env python3
"""Ce que la mémoire coûte : elle fait AVANCER DE TRAVERS.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `143` mesure que la mémoire échange de la fidélité contre de la distance
— bonnes feuilles **121 → 105**, tours bouclés **93 → 125** — et cet échange n'a jamais eu
d'explication. `147` vient d'éliminer la plus évidente : ce n'est **pas** le freinage de
l'enroulement, puisque faire tourner le cap à l'enroulement ne fait que déplacer des réussites. La
cause est donc ailleurs, et il en reste une que personne n'a regardée.

⭐⭐⭐ LE CANDIDAT EST MÉCANIQUE. Un cap MÉLANGE la normale, donc la normale employée n'est plus
perpendiculaire à la feuille. Or `suivre` tire sa direction de marche de cette normale-là
(`tangente = Z × normale`) : une normale inclinée incline la TANGENTE d'autant, et une part du pas
traverse la feuille au lieu de la longer. La pince ne s'en aperçoit pas — ses mâchoires se
raccrochent au pas suivant — mais elle paie ce raccrochage, et c'est peut-être là que la fidélité
s'en va.

⭐⭐ LA MESURE EST EXACTE ET NE COÛTE AUCUNE LECTURE. Ce que le pas aurait traversé si les mâchoires
ne se raccrochaient pas, c'est la phase du point visé moins celle du point courant — en feuilles,
déroulée. Ni `phase` ni `normale_locale` ne comptent une lecture, donc `lectures` reste le nombre que
les tranches précédentes publient. ⚠ Le suiveur ne voit jamais ces deux quantités : c'est une mesure
SUR lui, pas une entrée POUR lui.

⭐⭐⭐ ET LA RÉPARATION NE DEMANDE AUCUNE CONSTANTE. Si c'est bien la tangente qui est inclinée, il
suffit de la tirer de la normale que la matière vient de RENDRE plutôt que de la normale mélangée —
ce qui sépare « ce que le cap lisse » de « où le marcheur va », sans rien changer à ce que les
mâchoires emploient. Une seule chose bouge.

⚠⚠ LE TÉMOIN EST INTERNE ET IL EST DOUBLE : la variante « cap statique » EST la règle de `144`, donc
elle doit rendre 114 · 107 · **108** ; et la variante « sans cap » est le bras libre que `143`
mesure. Sans le second, « le cap fait traverser » n'aurait rien à quoi se comparer.

Usage :
    uv run python src/nappe/la_memoire_fait_elle_avancer_de_travers.py --verifier
    uv run python src/nappe/la_memoire_fait_elle_avancer_de_travers.py \\
        --json docs/mesures/la_memoire_fait_elle_avancer_de_travers.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_pince_tient_elle_la_feuille import (BRAS, LARGEUR_DE_REFERENCE,  # noqa: E402
                                            MATIERES, _resumer_un_bras, une_case, une_reussite)
from un_cap_qui_lit_la_cause import le_discriminant  # noqa: E402
from un_cap_qui_tourne import apparie  # noqa: E402

FENETRE = 32
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
# (nom, fenetre_du_cap, avance_sur_la_lecture)
VARIANTES = (("sans cap", 0, False),
             ("cap statique (`144`)", FENETRE, False),
             ("avance sur la lecture", FENETRE, True))
LE_PRECEDENT = RACINE / "docs" / "mesures" / "lire_la_cause_sous_le_bruit.json"
LE_CAP_POSE = RACINE / "docs" / "mesures" / "la_pince_garde_t_elle_son_cap.json"


def _filtre(fenetre: int, avance: bool):
    def f(c):
        return (int(c.get("fenetre_du_cap", 0)) == int(fenetre)
                and bool(c.get("avance_sur_la_lecture", False)) is bool(avance)
                and not bool(c.get("corrige_le_bruit", False))
                and not str(c.get("cap_tournant", ""))
                and not bool(c.get("enroulement_du_cap", False)))
    return f


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    cases = []
    for m in matieres:
        for b in bruits:
            for nom, fen, av in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=int(fen), avance_sur_la_lecture=bool(av))
                c["variante"] = nom
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(FENETRE),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"nom": n, "fenetre": f, "avance_sur_la_lecture": a}
                          for n, f, a in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _mediane(cases, bras: str, cle: str) -> float | None:
    """La médiane d'un diagnostic sur des marches, en unité PLEINE et à trois décimales.

    ⚠ Une donnée absente est SAUTÉE et non lue comme un zéro : une marche qui ne se pose pas n'a
    traversé aucune feuille, ce qui n'est pas la même chose qu'une marche qui a traversé zéro.

    ⚠⚠ TROIS DÉCIMALES N'EST PAS UNE MISE EN FORME, C'EST CE QUI REND LE NOMBRE RETROUVABLE. `147`
    a appris qu'un flottant arrondi sous `1e-4` sort du JSON en NOTATION SCIENTIFIQUE et devient
    introuvable dans son propre record ; arrondi au millième, il vaut zéro ou au moins `0.001`, que
    `json.dumps` écrit toujours en clair. ⚠ Et les suivis, eux, gardent leurs millièmes ENTIERS :
    ils ne sont publiés dans aucun document, et un entier est retrouvable quelle que soit sa taille.
    """
    xs = [x[cle] for c in cases for x in c["bras"][bras]["suivis"]
          if x.get("decidable") and x.get(cle) is not None]
    return round(statistics.median(xs) / 1000.0, 3) if xs else None


def _derive_mediane_feuilles(cases, bras: str) -> float | None:
    xs = [abs(float(x["derive_en_feuilles"])) for c in cases for x in c["bras"][bras]["suivis"]
          if x.get("decidable") and x.get("derive_en_feuilles") is not None]
    return round(statistics.median(xs), 3) if xs else None


def par_variante(grille: dict) -> dict:
    """Pour chaque règle : ce qu'elle fait marcher, et ce qu'elle traverse en chemin.

    ⚠ « Sépare » n'est pas réécrit : c'est le calcul de `144`, appelé avec un filtre.
    """
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["fenetre"], v["avance_sur_la_lecture"])
        cases = [c for c in grille["cases"] if f(c)]
        if not cases:
            continue
        # ⚠ Sans cap la mémoire vaut zéro partout, donc « l'écart entre matières » n'a rien à
        # départager : la lecture n'est publiée que pour les variantes qui en emploient une.
        d = le_discriminant(grille, f)["par_bruit"] if v["fenetre"] else []
        bloc = {**v, "cases": len(cases),
                "bruits_ou_elle_separe": [x["bruit"] for x in d if x["la_lecture_separe"]],
                "par_bruit": d}
        for nom in BRAS:
            bloc[nom] = {
                "reussites": int(sum(c["bras"][nom].get("reussites") or 0 for c in cases)),
                "memes_feuilles": int(sum(c["bras"][nom].get("memes_feuilles") or 0
                                          for c in cases)),
                "tours_boucles": int(sum(c["bras"][nom].get("tours_boucles") or 0
                                         for c in cases)),
                "inclinaison_mediane_deg": _mediane(cases, nom, "inclinaison_mediane_mdeg"),
                "traversee_absolue_feuilles": _mediane(cases, nom,
                                                       "traversee_absolue_mfeuilles"),
                "traversee_cumulee_feuilles": _mediane(cases, nom,
                                                       "traversee_cumulee_mfeuilles"),
                "derive_mediane_feuilles": _derive_mediane_feuilles(cases, nom)}
        bloc["par_matiere"] = [
            {"nom": nom,
             "inclinaison_mediane_deg": _mediane([c for c in cases if c["nom"] == nom],
                                                 "la pince", "inclinaison_mediane_mdeg"),
             "traversee_absolue_feuilles": _mediane([c for c in cases if c["nom"] == nom],
                                                    "la pince", "traversee_absolue_mfeuilles"),
             **{n: int(sum(c["bras"][n].get("reussites") or 0
                           for c in cases if c["nom"] == nom)) for n in BRAS}}
            for nom in dict.fromkeys(c["nom"] for c in cases)]
        out.append(bloc)
    return {"par_variante": out}


def le_cap_fait_il_traverser(grille: dict, pv: list[dict], bras: str = "la pince") -> dict:
    """Un cap fait-il traverser la feuille — et OÙ ?

    ⭐⭐⭐⭐ LA QUESTION SE POSE PAR MATIÈRE, ET MA PREMIÈRE VERSION L'A POSÉE SUR UNE MÉDIANE DE
    GRILLE. Elle répondait « non », et pour la pire des raisons : la médiane MOYENNE sur l'axe où la
    différence vit. Les deux moitiés de la grille vont en sens contraire, et leur mélange n'a aucun
    sens.

    ⭐⭐⭐ LE PARTAGE N'EST PAS CHOISI, C'EST LE PARAMÈTRE QUI DÉFINIT LA MATIÈRE : elle porte un
    froissement (`amplitude_um > 0`) ou elle n'en porte pas. Et le mécanisme prédit les deux sens
    à la fois, ce qui est exactement ce qui le rend réfutable :
    - sur une matière LISSE, la seule chose qu'un cap supprime est le bruit de lecture, qui n'est
      pas la forme de la feuille — donc il fait traverser MOINS ;
    - sur une matière FROISSÉE, il supprime aussi la rotation RÉELLE de la feuille, donc la tangente
      cesse de la longer — et il fait traverser PLUS.

    ⚠⚠ LA CONCLUSION EST UNANIME OU ELLE N'EST PAS : toutes les matières lisses d'un côté, toutes
    les froissées de l'autre. Une majorité serait un seuil déguisé.
    """
    sans = next((x for x in pv if not x["fenetre"]), None)
    avec = next((x for x in pv if x["fenetre"] and not x["avance_sur_la_lecture"]), None)
    if sans is None or avec is None:
        return {"decidable": False, "raison": "il faut un bras sans cap et un bras avec"}
    froissees = {c["nom"]: float(c["amplitude_um"]) > 0.0 for c in grille["cases"]}
    par_matiere = []
    for m in avec["par_matiere"]:
        s_ = next((z for z in sans["par_matiere"] if z["nom"] == m["nom"]), None)
        if s_ is None or s_["traversee_absolue_feuilles"] is None \
                or m["traversee_absolue_feuilles"] is None:
            continue
        par_matiere.append({
            "nom": m["nom"], "froissee": bool(froissees.get(m["nom"], False)),
            "sans_cap_feuilles": s_["traversee_absolue_feuilles"],
            "avec_cap_feuilles": m["traversee_absolue_feuilles"],
            "sans_cap_deg": s_["inclinaison_mediane_deg"],
            "avec_cap_deg": m["inclinaison_mediane_deg"],
            "il_fait_traverser_plus": bool(m["traversee_absolue_feuilles"]
                                           > s_["traversee_absolue_feuilles"])})
    if not par_matiere:
        return {"decidable": False, "raison": "aucune matière lisible des deux côtés"}
    fr = [x for x in par_matiere if x["froissee"]]
    li = [x for x in par_matiere if not x["froissee"]]
    return {"decidable": bool(fr and li), "bras": bras, "par_matiere": par_matiere,
            "matieres_froissees": len(fr), "matieres_lisses": len(li),
            "sur_les_froissees_il_fait_traverser_plus":
                bool(fr and all(x["il_fait_traverser_plus"] for x in fr)),
            "sur_les_lisses_il_fait_traverser_moins":
                bool(li and all(not x["il_fait_traverser_plus"] for x in li)),
            "le_mecanisme_tient": bool(fr and li
                                       and all(x["il_fait_traverser_plus"] for x in fr)
                                       and all(not x["il_fait_traverser_plus"] for x in li)),
            # ⚠ La MÉDIANE DE GRILLE est publiée à côté, et elle dit l'INVERSE : c'est elle qui
            # moyenne sur l'axe où la différence vit, et la garder est ce qui rend le partage
            # verifiable plutot qu'affirme.
            "sur_la_grille_entiere": {
                "sans_cap_feuilles": sans[bras]["traversee_absolue_feuilles"],
                "avec_cap_feuilles": avec[bras]["traversee_absolue_feuilles"],
                "elle_dit_linverse": bool(
                    avec[bras]["traversee_absolue_feuilles"] is not None
                    and sans[bras]["traversee_absolue_feuilles"] is not None
                    and (avec[bras]["traversee_absolue_feuilles"]
                         > sans[bras]["traversee_absolue_feuilles"])
                    != bool(fr and all(x["il_fait_traverser_plus"] for x in fr)))},
            # ⚠ Ce que les machoires rattrapent : la traversee absolue depasse de loin la derive,
            # sinon le raccrochage ne servirait a rien et la marche partirait droit.
            "les_machoires_rattrapent": bool(
                avec[bras]["derive_mediane_feuilles"] is not None
                and avec[bras]["traversee_absolue_feuilles"]
                > avec[bras]["derive_mediane_feuilles"]),
            "avec_cap": {"traversee_absolue_feuilles": avec[bras]["traversee_absolue_feuilles"],
                         "derive_mediane_feuilles": avec[bras]["derive_mediane_feuilles"],
                         "inclinaison_mediane_deg": avec[bras]["inclinaison_mediane_deg"]},
            "sans_cap": {"traversee_absolue_feuilles": sans[bras]["traversee_absolue_feuilles"],
                         "derive_mediane_feuilles": sans[bras]["derive_mediane_feuilles"],
                         "inclinaison_mediane_deg": sans[bras]["inclinaison_mediane_deg"]}}


def avancer_sur_la_lecture_repare(grille: dict, pv: list[dict],
                                  bras: str = "la pince") -> dict:
    """Tirer la tangente de la LECTURE au lieu du mélange : est-ce que ça répare ?

    ⭐⭐⭐ LA VICTOIRE EST JOINTE, COMME DEPUIS `147` : plus de réussites que le témoin statique ET
    aucune perdue sur les départs appariés. Un total seul est satisfait par un DÉPLACEMENT.

    ⚠ Et un second énoncé, indépendant du premier : la réparation doit d'abord faire ce qu'elle
    prétend, c'est-à-dire TRAVERSER MOINS. Une règle qui gagnerait des réussites en traversant
    autant gagnerait pour une autre raison que celle qu'on lui prête.
    """
    temoin = next((x for x in pv if x["fenetre"] and not x["avance_sur_la_lecture"]), None)
    repare = next((x for x in pv if x["fenetre"] and x["avance_sur_la_lecture"]), None)
    if temoin is None or repare is None:
        return {"decidable": False, "raison": "il faut le témoin statique et la réparation"}
    ap = apparie(grille, _filtre(temoin["fenetre"], False), _filtre(repare["fenetre"], True), bras)
    return {"decidable": True, "bras": bras,
            "reussites_du_temoin": temoin[bras]["reussites"],
            "reussites_de_la_reparation": repare[bras]["reussites"],
            "traversee_du_temoin_feuilles": temoin[bras]["traversee_absolue_feuilles"],
            "traversee_de_la_reparation_feuilles": repare[bras]["traversee_absolue_feuilles"],
            "apparie": ap,
            "elle_traverse_moins": bool(
                repare[bras]["traversee_absolue_feuilles"] is not None
                and temoin[bras]["traversee_absolue_feuilles"] is not None
                and repare[bras]["traversee_absolue_feuilles"]
                < temoin[bras]["traversee_absolue_feuilles"]),
            "elle_repare": bool(
                repare[bras]["reussites"] > temoin[bras]["reussites"]
                and ap.get("elle_ne_perd_rien") is True)}


def les_temoins_internes(grille: dict, precedent: dict | None,
                         cap_pose: dict | None) -> dict:
    """Deux témoins, et le second est gratuit.

    ⚠⚠ Le cap statique EST la règle de `144`, donc il doit rendre 114 · 107 · 108. Et la variante
    SANS CAP est exactement le bras à mémoire nulle que `143` publie case par case : ses réussites,
    ses bonnes feuilles et ses tours bouclés doivent retomber sur les siens, sur les trois bras.
    Neuf nombres qui ne peuvent pas s'accorder par hasard.
    """
    out: dict = {"decidable": False, "par_source": []}
    pv = par_variante(grille)["par_variante"]
    ici = next((x for x in pv if x["fenetre"] and not x["avance_sur_la_lecture"]), None)
    sans = next((x for x in pv if not x["fenetre"]), None)
    if precedent is not None and ici is not None:
        ref = next((v for v in precedent.get("juger", {}).get("par_variante", [])
                    if v.get("bloc") == 1 and not v.get("corrige")), None)
        if ref is not None:
            out["par_source"].append({
                "source": "`144` par `145`", "nom": ici["nom"],
                **{n: {"ici": ici[n]["reussites"], "la_bas": ref[n]["reussites"],
                       "identique": bool(ici[n]["reussites"] == ref[n]["reussites"])}
                   for n in BRAS}})
    if cap_pose is not None and sans is not None:
        cases = cap_pose.get("juger", {}).get("par_case", [])
        if cases:
            bloc = {"source": "`143`, mémoire nulle", "nom": sans["nom"]}
            for n in BRAS:
                la_bas = {c_: int(sum(c[n][f"sans_cap_{c_}"] for c in cases))
                          for c_ in ("reussites", "memes_feuilles", "tours_boucles")}
                bloc[n] = {"ici": {c_: sans[n][c_] for c_ in la_bas}, "la_bas": la_bas,
                           "identique": bool(all(sans[n][c_] == la_bas[c_] for c_ in la_bas))}
            out["par_source"].append(bloc)
    out["decidable"] = bool(out["par_source"])
    out["le_protocole_est_le_meme"] = bool(
        out["par_source"] and all(x[n]["identique"] for x in out["par_source"] for n in BRAS))
    return out


def juger(grille: dict, precedent: dict | None, cap_pose: dict | None = None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    return {"decidable": True, "par_variante": pv,
            "les_temoins_internes": les_temoins_internes(grille, precedent, cap_pose),
            "le_cap_fait_il_traverser": le_cap_fait_il_traverser(grille, pv),
            "avancer_sur_la_lecture_repare": avancer_sur_la_lecture_repare(grille, pv)}


def mesurer(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, departs: int = DEPARTS,
            tours: float = TOURS, precedent: Path = LE_PRECEDENT) -> dict:
    grille = sur_la_grille(matieres, bruits, variantes, departs, tours)
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    cap = json.loads(LE_CAP_POSE.read_text()) if LE_CAP_POSE.exists() else None
    return {"sur_la_grille": grille,
            "le_precedent": str(Path(precedent).name) if ref else None,
            "le_cap_pose": str(LE_CAP_POSE.name) if cap else None,
            "juger": juger(grille, ref, cap)}


def reagreger(r: dict, precedent: Path = LE_PRECEDENT,
              cap_pose: Path = LE_CAP_POSE) -> dict:
    """Recalcule les résumés et le verdict depuis les suivis rangés — sans remarcher."""
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    cap = json.loads(Path(cap_pose).read_text()) if Path(cap_pose).exists() else None
    r["juger"] = juger(r["sur_la_grille"], ref, cap)
    return r


def _deg(v) -> str:
    return "—" if v is None else f"{v:.3f}°"


def _f(v) -> str:
    return "—" if v is None else f"{v:+.3f}"


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    g = r["sur_la_grille"]
    t = j["les_temoins_internes"]
    if t.get("decidable"):
        marque = "★" if t["le_protocole_est_le_meme"] else "✗"
        print(f"{marque} témoins internes :")
        for x in t["par_source"]:
            det = []
            for n in BRAS:
                ici, la_bas = x[n]["ici"], x[n]["la_bas"]
                if isinstance(ici, dict):
                    det.append(f"{n} " + "/".join(str(ici[c]) for c in ici)
                               + " contre " + "/".join(str(la_bas[c]) for c in la_bas))
                else:
                    det.append(f"{n} {ici} contre {la_bas}")
            print(f"     « {x['nom']} » contre {x['source']} : " + " · ".join(det))
    print(f"\n   fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour — la pince :")
    print(f"   {'règle':>24} | {'réussites':>9} | {'feuilles':>8} | {'tours':>5} | "
          f"{'penche':>8} | {'traverse':>9} | {'dérive':>8}")
    for x in j["par_variante"]:
        b = x["la pince"]
        print(f"   {x['nom']:>24} | {b['reussites']:>9d} | {b['memes_feuilles']:>8d} | "
              f"{b['tours_boucles']:>5d} | {_deg(b['inclinaison_mediane_deg']):>8}"
              f" | {_f(b['traversee_absolue_feuilles']):>9} | "
              f"{_f(b['derive_mediane_feuilles']):>8}")
    c_ = j["le_cap_fait_il_traverser"]
    if c_.get("decidable"):
        marque = "★★★★" if c_["le_mecanisme_tient"] else "✗"
        print(f"\n{marque} le cap fait-il AVANCER DE TRAVERS ? {c_['le_mecanisme_tient']} — "
              f"plus sur les {c_['matieres_froissees']} froissées "
              f"({c_['sur_les_froissees_il_fait_traverser_plus']}), moins sur les "
              f"{c_['matieres_lisses']} lisses ({c_['sur_les_lisses_il_fait_traverser_moins']})")
        for y in c_["par_matiere"]:
            fl = "froissée" if y["froissee"] else "lisse   "
            print(f"     {y['nom']:>34} {fl} : {_f(y['sans_cap_feuilles'])} sans cap → "
                  f"{_f(y['avec_cap_feuilles'])} avec "
                  f"({'plus' if y['il_fait_traverser_plus'] else 'moins'}), "
                  f"penche {_deg(y['sans_cap_deg'])} → {_deg(y['avec_cap_deg'])}")
        sg = c_["sur_la_grille_entiere"]
        print(f"   ⚠ la médiane de GRILLE dit l'inverse ({sg['elle_dit_linverse']}) : "
              f"{_f(sg['sans_cap_feuilles'])} sans cap contre {_f(sg['avec_cap_feuilles'])} "
              f"avec — elle moyenne sur l'axe où la différence vit")
        print(f"   les mâchoires rattrapent : {c_['les_machoires_rattrapent']} — "
              f"{_f(c_['avec_cap']['traversee_absolue_feuilles'])} feuille traversée pour "
              f"{_f(c_['avec_cap']['derive_mediane_feuilles'])} perdue")
    a_ = j["avancer_sur_la_lecture_repare"]
    if a_.get("decidable"):
        ap = a_["apparie"]
        marque = "★★★★" if a_["elle_repare"] else "✗"
        print(f"\n{marque} avancer sur la LECTURE répare-t-il ? {a_['elle_repare']} — "
              f"{a_['reussites_de_la_reparation']} réussites contre "
              f"{a_['reussites_du_temoin']}")
        if ap.get("decidable"):
            print(f"   apparié : {ap['gains']} gagnées, {ap['pertes']} perdues, "
                  f"solde {ap['solde']:+d} sur {ap['paires']} départs")
        print(f"   elle traverse moins : {a_['elle_traverse_moins']} — "
              f"{_f(a_['traversee_de_la_reparation_feuilles'])} contre "
              f"{_f(a_['traversee_du_temoin_feuilles'])} feuille")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def suivi(deg, ok, incl, trav):
        return {"decidable": True, "depart_deg": float(deg), "memoire_mediane": 0.5,
                "tour_boucle": bool(ok), "derive_en_feuilles": 0.1 if ok else 3.0,
                "inclinaison_mediane_mdeg": incl, "traversee_absolue_mfeuilles": trav,
                "traversee_cumulee_mfeuilles": 0}

    def case(fen, av, nom, oks, incl, trav, amp=0.0):
        return {"ecrasement": 0.0, "amplitude_um": float(amp), "bruit": 0.0, "nom": nom,
                "departs": len(oks), "fenetre_du_cap": fen, "bloc_du_cap": 1,
                "corrige_le_bruit": False, "enroulement_du_cap": False, "cap_tournant": "",
                "avance_sur_la_lecture": av,
                "bras": {b: {"reussites": int(sum(oks)), "memes_feuilles": int(sum(oks)),
                             "tours_boucles": int(sum(oks)),
                             "suivis": [suivi(60 * i, o, incl, trav)
                                        for i, o in enumerate(oks)]} for b in BRAS}}

    v("le filtre distingue les trois règles",
      _filtre(0, False)(case(0, False, "A", [1], 100, 100))
      and _filtre(FENETRE, False)(case(FENETRE, False, "A", [1], 100, 100))
      and _filtre(FENETRE, True)(case(FENETRE, True, "A", [1], 100, 100))
      and not _filtre(FENETRE, False)(case(FENETRE, True, "A", [1], 100, 100)))
    v("⚠ il écarte les cases de `145`, `146` et `147` : une correction, une mémoire d'enroulement "
      "ou un cap tournant ne sont pas cette grille",
      not _filtre(FENETRE, False)({**case(FENETRE, False, "A", [1], 1, 1),
                                   "corrige_le_bruit": True})
      and not _filtre(FENETRE, False)({**case(FENETRE, False, "A", [1], 1, 1),
                                       "cap_tournant": "taux"})
      and not _filtre(FENETRE, False)({**case(FENETRE, False, "A", [1], 1, 1),
                                       "enroulement_du_cap": True}))

    VAR = [{"nom": "sans cap", "fenetre": 0, "avance_sur_la_lecture": False},
           {"nom": "cap statique (`144`)", "fenetre": FENETRE, "avance_sur_la_lecture": False},
           {"nom": "avance sur la lecture", "fenetre": FENETRE, "avance_sur_la_lecture": True}]

    def grille_de(t_lisse_sans, t_lisse_avec, t_froissee_sans, t_froissee_avec,
                  oks_sans=(1, 1, 0, 0), oks_cap=(1, 1, 1, 0), oks_rep=(1, 1, 1, 1),
                  incl_sans=3900, incl_cap=9300):
        return {"fenetre": FENETRE, "departs": len(oks_sans), "variantes": VAR,
                "cases": [
                    case(0, False, "lisse", list(oks_sans), incl_sans, t_lisse_sans, 0.0),
                    case(0, False, "froissée", list(oks_sans), incl_sans, t_froissee_sans, 42.4),
                    case(FENETRE, False, "lisse", list(oks_cap), incl_cap, t_lisse_avec, 0.0),
                    case(FENETRE, False, "froissée", list(oks_cap), incl_cap, t_froissee_avec,
                         42.4),
                    case(FENETRE, True, "lisse", list(oks_rep), incl_cap, t_lisse_avec, 0.0),
                    case(FENETRE, True, "froissée", list(oks_rep), incl_cap, t_froissee_avec,
                         42.4)]}

    #     lisse : 40 → 5 (moins) · froissée : 10 → 20 (plus). Le mécanisme tient, ET la
    #     mediane de grille dit l'INVERSE — c'est la fixture qui doit le fabriquer, pas la prose.
    g = grille_de(40000, 5000, 10000, 20000)
    pv = par_variante(g)["par_variante"]
    v("les réussites et les deux diagnostics sortent par règle",
      pv[0]["la pince"]["reussites"] == 4 and pv[1]["la pince"]["reussites"] == 6
      and pv[1]["la pince"]["inclinaison_mediane_deg"] == 9.3)
    v("⚠ un bras SANS cap ne publie aucune lecture à séparer : sa mémoire vaut zéro partout",
      pv[0]["par_bruit"] == [] and pv[0]["bruits_ou_elle_separe"] == [])

    c_ = le_cap_fait_il_traverser(g, pv)
    v("⭐⭐⭐⭐ le mécanisme tient quand le cap fait traverser PLUS sur les froissées et MOINS sur "
      "les lisses",
      c_["decidable"] and c_["le_mecanisme_tient"] is True,
      "lisse 40 → 5, froissée 10 → 20")
    v("⭐⭐⭐⭐ ... et il ne tient PAS si une seule des deux moitiés manque",
      le_cap_fait_il_traverser(
          grille_de(40000, 5000, 10000, 5000),
          par_variante(grille_de(40000, 5000, 10000, 5000))["par_variante"]
      )["le_mecanisme_tient"] is False
      and le_cap_fait_il_traverser(
          grille_de(40000, 50000, 10000, 20000),
          par_variante(grille_de(40000, 50000, 10000, 20000))["par_variante"]
      )["le_mecanisme_tient"] is False,
      "une conclusion unanime ou pas de conclusion — une majorité serait un seuil déguisé")
    v("⭐⭐⭐ la médiane de GRILLE peut dire l'inverse, et le producteur le DIT",
      c_["sur_la_grille_entiere"]["elle_dit_linverse"] is True,
      "moyenner sur l'axe où la différence vit est exactement ce que ce dépôt proscrit")
    v("⭐⭐ les mâchoires rattrapent : la traversée absolue dépasse la dérive",
      c_["les_machoires_rattrapent"] is True)
    v("sans bras sans cap, le diagnostic est indécidable",
      not le_cap_fait_il_traverser(g, [x for x in pv if x["fenetre"]])["decidable"])
    v("... et sans matière froissée aussi",
      not le_cap_fait_il_traverser(
          {"cases": [c for c in g["cases"] if c["amplitude_um"] == 0.0]},
          par_variante({**g, "cases": [c for c in g["cases"]
                                       if c["amplitude_um"] == 0.0]})["par_variante"]
      )["decidable"])

    a_ = avancer_sur_la_lecture_repare(g, pv)
    v("⭐⭐⭐⭐ la réparation gagne quand elle ajoute des réussites SANS en perdre",
      a_["decidable"] and a_["elle_repare"] is True
      and a_["apparie"]["gains"] == 2 and a_["apparie"]["pertes"] == 0,
      "8 contre 6, 2 gagnées, 0 perdue")
    dep = grille_de(40000, 5000, 10000, 20000, oks_rep=(1, 1, 0, 1))
    v("⭐⭐⭐⭐ ... et elle ne gagne PAS en déplaçant, même à total égal",
      avancer_sur_la_lecture_repare(
          dep, par_variante(dep)["par_variante"])["elle_repare"] is False,
      "le solde seul est satisfait par un déplacement, depuis `147`")
    v("⭐⭐ et « elle traverse moins » est un énoncé SÉPARÉ de « elle répare »",
      a_["elle_traverse_moins"] is False,
      "gagner des réussites en traversant autant serait gagner pour une autre raison")
    v("sans témoin statique, la réparation est indécidable",
      not avancer_sur_la_lecture_repare(g, [x for x in pv if not x["fenetre"]])["decidable"])
    v("un jugement sans case est indécidable", not juger({"cases": []}, None)["decidable"])
    v("⚠ une donnée absente est SAUTÉE, pas lue comme un zéro",
      _mediane([{"bras": {"la pince": {"suivis": [
          {"decidable": False, "inclinaison_mediane_mdeg": None},
          {"decidable": True, "inclinaison_mediane_mdeg": 42}]}}}],
          "la pince", "inclinaison_mediane_mdeg") == 0.042)
    v("... et une case sans rien de lisible ne rend rien plutôt que zéro",
      _mediane([{"bras": {"la pince": {"suivis": [
          {"decidable": False, "inclinaison_mediane_mdeg": None}]}}}],
          "la pince", "inclinaison_mediane_mdeg") is None)

    # ---- ⭐⭐ les DEUX témoins internes, et chacun doit savoir échouer
    ref = {"juger": {"par_variante": [
        {"nom": "brute", "bloc": 1, "corrige": False, **{n: {"reussites": 6} for n in BRAS}}]}}
    cap = {"juger": {"par_case": [
        {n: {"sans_cap_reussites": 4, "sans_cap_memes_feuilles": 4,
             "sans_cap_tours_boucles": 4} for n in BRAS}]}}
    t = les_temoins_internes(g, ref, cap)
    v("⭐⭐ les deux témoins internes comparent `144` par `145` ET `143` à mémoire nulle",
      t["decidable"] and len(t["par_source"]) == 2 and t["le_protocole_est_le_meme"] is True,
      "neuf nombres du côté de `143` : réussites, bonnes feuilles et tours bouclés sur trois bras")
    faux = json.loads(json.dumps(ref))
    faux["juger"]["par_variante"][0]["la pince"]["reussites"] = 9
    v("⭐⭐⭐ ... et le premier DIT quand le module partagé a bougé",
      les_temoins_internes(g, faux, cap)["le_protocole_est_le_meme"] is False)
    faux2 = json.loads(json.dumps(cap))
    faux2["juger"]["par_case"][0]["la pince"]["sans_cap_tours_boucles"] = 9
    v("⭐⭐⭐ ... et le second aussi, sur un compteur que le premier ne regarde même pas",
      les_temoins_internes(g, ref, faux2)["le_protocole_est_le_meme"] is False,
      "les tours bouclés — un témoin qui ne regarderait que les réussites raterait ce changement")
    v("sans aucun précédent, les témoins sont indécidables",
      not les_temoins_internes(g, None, None)["decidable"])

    # ---- ⭐ de bout en bout, sur une vraie matière froissée
    froissee = une_case((0.0, 42.4), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                        fenetre_du_cap=FENETRE)
    libre = une_case((0.0, 42.4), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05)
    lecture = une_case((0.0, 42.4), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                       fenetre_du_cap=FENETRE, avance_sur_la_lecture=True)

    def lu(c, cle):
        xs = [x[cle] for x in c["bras"]["la pince"]["suivis"]
              if x.get("decidable") and x.get(cle) is not None]
        return xs[0] if xs else None

    v("⭐⭐⭐ sur une vraie marche froissée, un cap fait pencher la normale et traverser la feuille",
      lu(froissee, "inclinaison_mediane_mdeg") > lu(libre, "inclinaison_mediane_mdeg")
      and lu(froissee, "traversee_absolue_mfeuilles")
      > lu(libre, "traversee_absolue_mfeuilles"),
      f"{lu(froissee, 'inclinaison_mediane_mdeg')} mdeg et "
      f"{lu(froissee, 'traversee_absolue_mfeuilles')} mfeuilles avec cap, contre "
      f"{lu(libre, 'inclinaison_mediane_mdeg')} et "
      f"{lu(libre, 'traversee_absolue_mfeuilles')} sans")
    v("⚠⚠ le diagnostic ne coûte AUCUNE lecture : `lectures` est le nombre des tranches "
      "précédentes",
      lu(froissee, "lectures") == lu(lecture, "lectures"),
      f"{lu(froissee, 'lectures')} des deux côtés")
    v("... et la variante voyage jusque dans la case",
      lecture["avance_sur_la_lecture"] is True and froissee["avance_sur_la_lecture"] is False)

    petit = {"sur_la_grille": {"cases": [libre, froissee, lecture], "departs": 1, "tours": 0.05,
                               "fenetre": FENETRE, "bruits": [0.0],
                               "largeur_en_pas": LARGEUR_DE_REFERENCE,
                               "variantes": [{"nom": n, "fenetre": f, "avance_sur_la_lecture": a}
                                             for n, f, a in VARIANTES]}}
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
