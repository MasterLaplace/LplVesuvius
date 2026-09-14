#!/usr/bin/env python3
"""Un suiveur n'a rien à quoi se comparer — d'où une référence qu'il CALCULE.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL COMMENCE PAR UN OBSTACLE. `145` établit que la lecture corrigée
SÉPARE les matières jusqu'à bruit 16, et nomme la suite : un instrument à deux étages, qui
diagnostique la cause puis conduit. ⚠⚠ Mais « séparer » est un énoncé sur une COMPARAISON, et un
suiveur ne voit qu'une matière. Les données publiées par `145` le montrent sans mesure nouvelle : une
spirale **nue** à bruit 8 rend **0,7537**, une spirale écrasée **ET** froissée sans aucun bruit rend
**0,7733**, et la nue à bruit 16 rend **0,8206** quand un froissement seul sans bruit rend **0,7886**.
Une matière sans aucune cause lit donc PLUS HAUT qu'une matière qui en porte deux : aucun seuil
absolu ne peut les distinguer, et un suiveur n'a que ce nombre.

⭐⭐⭐ CE QUI MANQUE EST UNE RÉFÉRENCE ABSOLUE, ET LE SUIVEUR EN POSSÈDE UNE. Sa normale tourne de
`avance / rayon` par pas du seul fait de l'enroulement — il connaît son avance, puisqu'il la choisit,
et son rayon, puisqu'il connaît l'axe. Ce qui excède cette rotation-là n'est ni lisible ni voulu.
D'où une troisième règle, sans comparaison et sans constante ajustée :

    m = 1 − min(enroulement / rotation moyenne observée, 1)

⚠ Elle lit une AMPLITUDE et non un signe : une alternance de même amplitude que l'enroulement ne lui
demande rien, là où la cohérence y verrait une cause. C'est une différence de nature, pas un réglage,
et la batterie l'asserte.

⚠⚠ LES DEUX TÉMOINS SONT INTERNES : les variantes « brute » et « corrigée » SONT les règles de `144`
et `145`, et la mesure doit les reproduire. Sinon c'est le protocole qui a bougé.

Usage :
    uv run python src/nappe/un_suiveur_na_rien_a_quoi_se_comparer.py --verifier
    uv run python src/nappe/un_suiveur_na_rien_a_quoi_se_comparer.py \\
        --json docs/mesures/un_suiveur_na_rien_a_quoi_se_comparer.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_pince_tient_elle_la_feuille import (BRAS, LARGEUR_DE_REFERENCE,  # noqa: E402
                                            MATIERES, _resumer_un_bras, une_case)
from un_cap_qui_lit_la_cause import le_discriminant  # noqa: E402

FENETRE = 32
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
# (nom, bloc, corrige, enroulement)
VARIANTES = (("brute (`144`)", 1, False, False),
             ("corrigée (`145`)", 1, True, False),
             ("enroulement", 1, False, True))
LE_PRECEDENT = RACINE / "docs" / "mesures" / "lire_la_cause_sous_le_bruit.json"


def les_lectures_se_recouvrent(precedent: dict | None) -> dict:
    """Un seuil ABSOLU peut-il séparer les causes, sur les lectures que `145` publie ?

    ⭐⭐⭐⭐ C'EST L'OBSTACLE, ET IL SE DÉMONTRE SANS MESURE NOUVELLE. « La lecture sépare » est un
    énoncé sur une comparaison ENTRE matières ; un suiveur n'en voit qu'une. Si une matière SANS
    cause rend, à un bruit, une lecture supérieure ou égale à celle d'une matière AVEC cause à un
    autre bruit, alors aucun seuil absolu ne peut les distinguer — et c'est exactement ce qu'il faut
    pour bâtir un diagnostic.

    ⚠ « Sans cause » veut dire la spirale nue : ni écrasement, ni froissement. Le bruit n'est pas une
    cause de la matière, c'est ce qui empêche de la lire.
    """
    if not precedent:
        return {"decidable": False, "raison": "la mesure de `145` est absente"}
    var = next((v for v in precedent.get("juger", {}).get("par_variante", [])
                if v.get("bloc") == 1 and v.get("corrige")), None)
    if var is None:
        return {"decidable": False, "raison": "`145` ne publie pas la variante corrigée"}
    lectures = [{"nom": m["nom"], "bruit": y["bruit"], "memoire": m["memoire"],
                 "sans_cause": "nue" in m["nom"]}
                for y in var["par_bruit"] for m in y["par_matiere"]
                if m.get("memoire") is not None]
    inversions = [{"sans_cause": a["nom"], "bruit_sans_cause": a["bruit"], "lecture_sans": a["memoire"],
                   "avec_cause": b["nom"], "bruit_avec_cause": b["bruit"],
                   "lecture_avec": b["memoire"]}
                  for a in lectures if a["sans_cause"]
                  for b in lectures if not b["sans_cause"] and a["memoire"] >= b["memoire"]]
    return {"decidable": True, "source": var["nom"], "lectures": len(lectures),
            "inversions": len(inversions),
            "un_seuil_absolu_separe": not inversions,
            "la_pire": max(inversions, key=lambda x: x["lecture_sans"] - x["lecture_avec"],
                           default=None),
            "par_inversion": inversions}


def _filtre(bloc: int, corrige: bool, enroulement: bool):
    def f(c):
        return (c["bloc_du_cap"] == int(bloc)
                and bool(c["corrige_le_bruit"]) is bool(corrige)
                and bool(c.get("enroulement_du_cap", False)) is bool(enroulement))
    return f


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    cases = []
    for m in matieres:
        for b in bruits:
            for nom, bloc, corrige, enr in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=int(fenetre), bloc_du_cap=int(bloc),
                             corrige_le_bruit=bool(corrige), enroulement_du_cap=bool(enr))
                c["variante"] = nom
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(fenetre),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"nom": n, "bloc": b, "corrige": c, "enroulement": e}
                          for n, b, c, e in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def par_variante(grille: dict) -> dict:
    """Pour chaque règle : les réussites, et à quels bruits elle sépare encore.

    ⚠ « Sépare » n'est pas réécrit : c'est le calcul de `144`, appelé avec un filtre.
    """
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["bloc"], v["corrige"], v["enroulement"])
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
                "memes_feuilles": int(sum(c["bras"][nom].get("memes_feuilles") or 0
                                          for c in cases)),
                "tours_boucles": int(sum(c["bras"][nom].get("tours_boucles") or 0
                                         for c in cases))}
        out.append(bloc)
    return {"par_variante": out}


def les_temoins_internes(grille: dict, precedent: dict | None) -> dict:
    """Les variantes « brute » et « corrigée » doivent reproduire `145` exactement."""
    if not precedent:
        return {"decidable": False, "raison": "la mesure de `145` est absente, les témoins manquent"}
    refs = {}
    for v in precedent.get("juger", {}).get("par_variante", []):
        if v.get("bloc") == 1 and not v.get("corrige"):
            refs["brute (`144`)"] = v
        elif v.get("bloc") == 1 and v.get("corrige"):
            refs["corrigée (`145`)"] = v
    pv = {x["nom"]: x for x in par_variante(grille)["par_variante"]}
    out = {"decidable": bool(refs), "par_variante": []}
    for nom, ref in refs.items():
        ici = pv.get(nom)
        if ici is None:
            continue
        out["par_variante"].append({
            "nom": nom,
            **{n: {"ici": ici[n]["reussites"], "dans_145": ref[n]["reussites"],
                   "identique": bool(ici[n]["reussites"] == ref[n]["reussites"])} for n in BRAS}})
    out["le_protocole_est_le_meme"] = bool(
        out["par_variante"]
        and all(x[n]["identique"] for x in out["par_variante"] for n in BRAS))
    return out


def juger(grille: dict, precedent: dict | None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    out = {"decidable": True, "par_variante": pv,
           "les_temoins_internes": les_temoins_internes(grille, precedent),
           "les_lectures_se_recouvrent": les_lectures_se_recouvrent(precedent)}
    # ⭐ La règle de l'enroulement contre les deux qu'elle doit battre — et sur les deux axes que
    # `145` a montrés contraires : ce qu'elle sait LIRE et ce qu'elle fait MARCHER.
    absolue = next((x for x in pv if x["enroulement"]), None)
    if absolue is not None:
        out["la_regle_de_lenroulement"] = {
            "nom": absolue["nom"],
            "bruits_ou_elle_separe": absolue["bruits_ou_elle_separe"],
            "reussites_de_la_pince": absolue["la pince"]["reussites"],
            "contre": [{"nom": x["nom"],
                        "bruits_ou_elle_separe": x["bruits_ou_elle_separe"],
                        "reussites_de_la_pince": x["la pince"]["reussites"],
                        "elle_lit_plus_loin": bool(
                            max(absolue["bruits_ou_elle_separe"], default=-1.0)
                            > max(x["bruits_ou_elle_separe"], default=-1.0)),
                        "elle_marche_mieux": bool(
                            absolue["la pince"]["reussites"] > x["la pince"]["reussites"])}
                       for x in pv if not x["enroulement"]]}
        # ⚠⚠ « Faire les deux » est un ÉNONCÉ, et ma première version l'écrivait `… or True`,
        # c'est-à-dire une condition qui ne peut pas échouer — dans le producteur, cette fois.
        # Elle fait les deux quand elle marche mieux que TOUTES les autres ET lit AU MOINS aussi
        # loin que chacune : `145` a montré que ces deux-là s'opposent, donc les tenir ensemble
        # est exactement ce qui serait neuf.
        contre = out["la_regle_de_lenroulement"]["contre"]
        loin = max(absolue["bruits_ou_elle_separe"], default=-1.0)
        out["la_regle_de_lenroulement"]["elle_fait_les_deux"] = bool(
            contre and all(y["elle_marche_mieux"] for y in contre)
            and all(loin >= max(x["bruits_ou_elle_separe"], default=-1.0)
                    for x in pv if not x["enroulement"]))
    return out


def mesurer(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
            departs: int = DEPARTS, tours: float = TOURS, precedent: Path = LE_PRECEDENT) -> dict:
    grille = sur_la_grille(matieres, bruits, variantes, fenetre, departs, tours)
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    return {"sur_la_grille": grille,
            "le_precedent": str(Path(precedent).name) if ref else None,
            "juger": juger(grille, ref)}


def reagreger(r: dict, precedent: Path = LE_PRECEDENT) -> dict:
    """Recalcule les résumés et le verdict depuis les suivis rangés — sans remarcher."""
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    ref = json.loads(Path(precedent).read_text()) if Path(precedent).exists() else None
    r["juger"] = juger(r["sur_la_grille"], ref)
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    g = r["sur_la_grille"]
    o = j["les_lectures_se_recouvrent"]
    if o.get("decidable"):
        marque = "★" if o["un_seuil_absolu_separe"] else "✗"
        print(f"{marque} un seuil ABSOLU sépare-t-il les causes, sur les lectures de `145` ? "
              f"{o['un_seuil_absolu_separe']} — {o['inversions']} inversion(s) sur "
              f"{o['lectures']} lectures")
        p_ = o.get("la_pire")
        if p_ is not None:
            print(f"   la pire : « {p_['sans_cause']} » à bruit {p_['bruit_sans_cause']:g} lit "
                  f"{p_['lecture_sans']:.4f}, et « {p_['avec_cause']} » à bruit "
                  f"{p_['bruit_avec_cause']:g} lit {p_['lecture_avec']:.4f} — une matière SANS "
                  f"cause lit plus haut qu'une matière qui en porte")
    t = j["les_temoins_internes"]
    if t.get("decidable"):
        marque = "★" if t["le_protocole_est_le_meme"] else "✗"
        print(f"\n{marque} témoins internes — les règles de `144` et `145` doivent se reproduire :")
        for x in t["par_variante"]:
            print(f"     {x['nom']:>18} : "
                  + " · ".join(f"{n} {x[n]['ici']} contre {x[n]['dans_145']}" for n in BRAS))
    print(f"\n   fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour :")
    print(f"   {'règle':>18} | {'réussites (pince)':>18} | bruits où elle sépare")
    for x in j["par_variante"]:
        print(f"   {x['nom']:>18} | {x['la pince']['reussites']:>18d} | "
              f"{x['bruits_ou_elle_separe']}")
    print(f"\n   l'écart entre matières contre la dispersion dans une :")
    for x in j["par_variante"]:
        print(f"     {x['nom']:>18} : " + " · ".join(
            f"bruit {y['bruit']:g} {y['ecart_entre_matieres']:.4f}/"
            f"{y['dispersion_dans_une_matiere']:.4f}"
            f"{'✓' if y['la_lecture_separe'] else '✗'}" for y in x["par_bruit"]))
    a_ = j.get("la_regle_de_lenroulement")
    if a_ is not None:
        print(f"\n   « {a_['nom']} » : {a_['reussites_de_la_pince']} réussites, sépare aux bruits "
              f"{a_['bruits_ou_elle_separe']}")
        for y in a_["contre"]:
            print(f"     contre « {y['nom']} » ({y['reussites_de_la_pince']} réussites, "
                  f"{y['bruits_ou_elle_separe']}) : marche mieux {y['elle_marche_mieux']}, "
                  f"lit plus loin {y['elle_lit_plus_loin']}")
        marque = "★★★★" if a_["elle_fait_les_deux"] else "✗"
        print(f"\n{marque} elle fait les DEUX — marcher mieux et lire aussi loin : "
              f"{a_['elle_fait_les_deux']}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- ⭐⭐ l'obstacle, sur des lectures fabriquées
    def precedent(lectures):
        return {"juger": {"par_variante": [{
            "nom": "corrigée", "bloc": 1, "corrige": True,
            "par_bruit": [{"bruit": b, "par_matiere": [{"nom": n, "memoire": m}
                                                       for n, m in mm]}
                          for b, mm in lectures]}]}}

    propre = precedent([(0.0, [("spirale nue", 0.10), ("spirale froissée", 0.80)]),
                        (8.0, [("spirale nue", 0.20), ("spirale froissée", 0.90)])])
    o = les_lectures_se_recouvrent(propre)
    v("⭐⭐ un seuil absolu sépare quand aucune lecture sans cause n'atteint une lecture avec",
      o["decidable"] and o["un_seuil_absolu_separe"] is True and o["inversions"] == 0)
    croise = precedent([(0.0, [("spirale nue", 0.10), ("spirale froissée", 0.80)]),
                        (8.0, [("spirale nue", 0.85), ("spirale froissée", 0.90)])])
    o2 = les_lectures_se_recouvrent(croise)
    v("⭐⭐ ... et il ne sépare PLUS dès qu'une matière SANS cause lit plus haut qu'une avec",
      o2["un_seuil_absolu_separe"] is False and o2["inversions"] == 1,
      f"{o2['inversions']} inversion(s) — c'est exactement l'obstacle de `145`")
    v("... et la pire inversion est nommée",
      o2["la_pire"]["sans_cause"] == "spirale nue"
      and o2["la_pire"]["bruit_sans_cause"] == 8.0)
    v("sans `145`, l'obstacle est indécidable et le dit",
      not les_lectures_se_recouvrent(None)["decidable"])
    v("... et une mesure de `145` sans variante corrigée aussi",
      not les_lectures_se_recouvrent({"juger": {"par_variante": []}})["decidable"])

    # ---- le filtre et les variantes
    def case(bloc, corrige, enr, bruit, nom, mems, r=6):
        return {"ecrasement": 0.0, "amplitude_um": 0.0, "bruit": bruit, "nom": nom,
                "departs": len(mems), "fenetre_du_cap": FENETRE, "bloc_du_cap": bloc,
                "corrige_le_bruit": corrige, "enroulement_du_cap": enr,
                "bras": {b: {"reussites": r, "memes_feuilles": r, "tours_boucles": r,
                             "suivis": [{"decidable": True, "memoire_mediane": m}
                                        for m in mems]} for b in BRAS}}

    v("le filtre distingue les trois règles",
      _filtre(1, False, False)(case(1, False, False, 0.0, "x", [0.1]))
      and not _filtre(1, False, True)(case(1, False, False, 0.0, "x", [0.1]))
      and not _filtre(1, True, False)(case(1, False, False, 0.0, "x", [0.1])))

    grille = {"fenetre": FENETRE, "departs": 2,
              "variantes": [{"nom": "brute (`144`)", "bloc": 1, "corrige": False,
                             "enroulement": False},
                            {"nom": "enroulement", "bloc": 1, "corrige": False,
                             "enroulement": True}],
              "cases": [case(1, False, False, 0.0, "A", [0.10, 0.12], r=9),
                        case(1, False, False, 0.0, "B", [0.70, 0.72], r=9),
                        case(1, False, True, 0.0, "A", [0.40, 0.90], r=6),
                        case(1, False, True, 0.0, "B", [0.42, 0.92], r=6)]}
    pv = par_variante(grille)["par_variante"]
    v("les réussites et la séparation sortent par règle",
      pv[0]["la pince"]["reussites"] == 18 and pv[0]["bruits_ou_elle_separe"] == [0.0]
      and pv[1]["la pince"]["reussites"] == 12 and pv[1]["bruits_ou_elle_separe"] == [])

    # ---- ⭐⭐ « faire les deux » est un énoncé qui peut échouer
    j1 = juger(grille, None)
    v("⭐⭐ une règle qui marche MOINS bien ne fait pas les deux",
      j1["la_regle_de_lenroulement"]["elle_fait_les_deux"] is False,
      "12 réussites contre 18, et elle ne sépare nulle part")
    grille2 = json.loads(json.dumps(grille))
    for c in grille2["cases"]:
        if c["enroulement_du_cap"]:
            for b in BRAS:
                c["bras"][b]["reussites"] = 12
            c["bras"]["la pince"]["suivis"] = [{"decidable": True, "memoire_mediane": m}
                                               for m in ([0.10, 0.12] if c["nom"] == "A"
                                                         else [0.70, 0.72])]
            for b in BRAS:
                c["bras"][b]["suivis"] = c["bras"]["la pince"]["suivis"]
    j2 = juger(grille2, None)
    v("⭐⭐ ... et une règle qui marche mieux ET lit aussi loin, oui",
      j2["la_regle_de_lenroulement"]["elle_fait_les_deux"] is True,
      f"{j2['la_regle_de_lenroulement']['reussites_de_la_pince']} réussites, sépare "
      f"{j2['la_regle_de_lenroulement']['bruits_ou_elle_separe']}")

    # ---- les témoins internes
    ref = {"juger": {"par_variante": [
        {"nom": "brute", "bloc": 1, "corrige": False,
         **{n: {"reussites": 18} for n in BRAS}},
        {"nom": "corrigée", "bloc": 1, "corrige": True,
         **{n: {"reussites": 99} for n in BRAS}}]}}
    t = les_temoins_internes(grille, ref)
    v("⭐⭐ le témoin interne compare « brute » à ce que `145` publie",
      t["decidable"] and t["le_protocole_est_le_meme"] is True,
      f"{t['par_variante'][0]['la pince']}")
    faux = json.loads(json.dumps(ref))
    faux["juger"]["par_variante"][0]["la pince"]["reussites"] = 7
    v("⭐⭐ ... et il DIT quand le protocole a bougé",
      les_temoins_internes(grille, faux)["le_protocole_est_le_meme"] is False)
    v("sans `145`, les témoins sont indécidables",
      not les_temoins_internes(grille, None)["decidable"])
    v("un jugement sans case est indécidable", not juger({"cases": []}, None)["decidable"])

    # ---- ⭐ la règle absolue, de bout en bout sur une vraie matière
    nue = une_case((0.0, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                   fenetre_du_cap=FENETRE, enroulement_du_cap=True)
    froissee = une_case((0.0, 42.4), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                        fenetre_du_cap=FENETRE, enroulement_du_cap=True)

    def lue(c):
        xs = [x["memoire_mediane"] for x in c["bras"]["la pince"]["suivis"]
              if x.get("decidable") and x.get("memoire_mediane") is not None]
        return xs[0] if xs else None

    # ⚠⚠ PAS DE `or` POUR UN DÉFAUT : `0.0 or 1.0` vaut 1.0 en Python, et zéro est précisément la
    # valeur que cette règle doit rendre sur une spirale nue. Ma première version l'avalait et
    # déclarait l'échec d'un résultat juste.
    v("⭐⭐ sur une spirale NUE, la rotation vaut l'enroulement : la règle ne demande rien",
      lue(nue) is not None and lue(nue) < 0.05, f"{lue(nue)}")
    v("⭐⭐ ... et sur une matière FROISSÉE elle demande davantage",
      lue(froissee) is not None and lue(nue) is not None and lue(froissee) > lue(nue),
      f"froissée {lue(froissee)} contre nue {lue(nue)}")
    v("... et la variante voyage jusque dans la case", nue["enroulement_du_cap"] is True)

    # ---- réagréger
    petit = {"sur_la_grille": {"cases": [froissee], "departs": 1, "tours": 0.05,
                               "fenetre": FENETRE, "bruits": [0.0],
                               "largeur_en_pas": LARGEUR_DE_REFERENCE,
                               "variantes": [{"nom": "enroulement", "bloc": 1, "corrige": False,
                                              "enroulement": True}]}}
    petit["juger"] = juger(petit["sur_la_grille"], None)
    v("⭐ réagréger depuis les suivis rangés rend le MÊME verdict, sans remarcher",
      reagreger(json.loads(json.dumps(petit)), Path("/inexistant.json"))["juger"]
      == petit["juger"])

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
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger is not None:
        r = reagreger(json.loads(a.reagreger.read_text()))
        afficher(r)
        a.reagreger.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.reagreger}")
        return 0
    r = mesurer(departs=a.departs, tours=a.tours)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
