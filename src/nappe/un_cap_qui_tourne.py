#!/usr/bin/env python3
"""Un cap qui TOURNE — parce qu'un cap qui ne tourne pas combat l'enroulement.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `143` mesure que la mémoire échange de la fidélité contre de la distance
— bonnes feuilles **121 → 105**, tours bouclés **93 → 125** — et cet échange a été lu jusqu'ici comme
une propriété de la matière. Il ne l'est peut-être pas. La mémoire de `143` retient une ORIENTATION
fixe : à mémoire 0,8 le suiveur garde quatre cinquièmes de sa direction précédente, donc il résiste
aussi à la rotation que le tour lui IMPOSE — `2π` sur un tour entier. Un cap statique ne se contente
pas de lisser le froissement, il freine l'enroulement.

⭐⭐⭐ CE FICHIER MET ENSEMBLE LES DEUX INGRÉDIENTS QUE `146` A NOMMÉS. L'enroulement dit COMBIEN de
rotation est due — `avance / rayon`, que le suiveur calcule seul, sans comparer quoi que ce soit. La
moyenne des incréments dit ce qui tourne RÉELLEMENT et de façon cohérente. Trois règles les isolent :

    à l'enroulement   le cap tourne de `avance / rayon`             (l'absolu seul)
    au taux lu        le cap tourne de la moyenne de la fenêtre     (l'estimation seule)
    au taux planché   la moyenne, jamais moins que l'enroulement    (les deux)

⚠⚠ CE N'EST PAS LE PIÈGE DE `144`. Retirer la moyenne des incréments avant d'en lire la cohérence
détruit la persistance qu'on veut détecter, et `144` l'a dit avant sa mesure. Ici la moyenne n'est
retirée de RIEN : la mémoire reste `m = 1 − c` sur les incréments bruts, et la moyenne ne sert qu'à
PRÉDIRE le pas suivant. Lire et prédire ne sont pas le même usage d'une même quantité.

⭐⭐ LA VARIABLE EST UNIQUE. Les trois règles tournantes emploient la mémoire de `144`, inchangée :
la seule chose qui bouge entre le témoin et elles est que le cap tourne. Ce qui se mesure est donc
cet unique changement, et rien d'autre.

⚠⚠ LES DEUX TÉMOINS SONT INTERNES ET ILS SONT AUSSI LA PREUVE DU REFACTOR : les variantes « cap
statique » SONT les règles de `144` et `145`, qui passent par le module partagé que ce fichier
modifie. Si elles ne rendent pas 114 · 107 · 108 et 115 · 98 · 97, c'est le module partagé qui a
bougé, et aucune comparaison ne vaut.

Usage :
    uv run python src/nappe/un_cap_qui_tourne.py --verifier
    uv run python src/nappe/un_cap_qui_tourne.py --json docs/mesures/un_cap_qui_tourne.json
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

from la_pince_tient_elle_la_feuille import (AVANCE_EN_LONGUEUR_DONDE, BRAS,  # noqa: E402
                                            LARGEUR_DE_REFERENCE, LONGUEUR_DONDE_UM, MATIERES,
                                            RAYON_MM, _PAS, _resumer_un_bras, une_case,
                                            une_reussite)
from un_cap_qui_lit_la_cause import le_discriminant  # noqa: E402

FENETRE = 32
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
# (nom, corrige_le_bruit, cap_tournant)
VARIANTES = (("cap statique (`144`)", False, ""),
             ("cap statique corrigé (`145`)", True, ""),
             ("tournant à l'enroulement", False, "enroulement"),
             ("tournant au taux lu", False, "taux"),
             ("tournant au taux planché", False, "taux_planche"))
# ⚠ La matière que `140` retient comme celle du rouleau, et sur laquelle personne n'a jamais réussi
# un transfert depuis `142`. Elle est NOMMÉE ici pour que la barre soit lue, pas choisie après coup.
LA_MATIERE_DE_140 = (0.2782, 100.0)
LE_PRECEDENT = RACINE / "docs" / "mesures" / "lire_la_cause_sous_le_bruit.json"


def _filtre(corrige: bool, cap: str):
    def f(c):
        return (bool(c["corrige_le_bruit"]) is bool(corrige)
                and str(c.get("cap_tournant", "")) == str(cap)
                and int(c.get("bloc_du_cap", 1)) == 1
                and not bool(c.get("enroulement_du_cap", False)))
    return f


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    cases = []
    for m in matieres:
        for b in bruits:
            for nom, corrige, cap in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=int(fenetre), corrige_le_bruit=bool(corrige),
                             cap_tournant=str(cap))
                c["variante"] = nom
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(fenetre),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"nom": n, "corrige": c, "cap": k} for n, c, k in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _taux_median(cases, bras: str) -> float | None:
    """Le taux RÉELLEMENT employé — la garde contre un cap tournant qui ne tournerait pas.

    ⚠ Une donnée absente ne se lit pas comme un zéro : un suivi indécidable est SAUTÉ, pas compté
    comme un cap immobile.
    """
    xs = [x["taux_median_rad"] for c in cases for x in c["bras"][bras]["suivis"]
          if x.get("decidable") and x.get("taux_median_rad") is not None]
    return round(statistics.median(xs), 6) if xs else None


def par_variante(grille: dict) -> dict:
    """Pour chaque règle : ce qu'elle fait marcher, ce qu'elle sépare, et de combien elle tourne.

    ⚠ « Sépare » n'est pas réécrit : c'est le calcul de `144`, appelé avec un filtre.
    """
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["corrige"], v["cap"])
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
                                         for c in cases)),
                "taux_median_rad": _taux_median(cases, nom)}
        # ⭐ OÙ ça change : les réussites matière par matière, tous bruits confondus. Un total
        # sur la grille ne dit pas si une règle gagne partout un peu ou beaucoup quelque part.
        bloc["par_matiere"] = [
            {"nom": nom,
             # ⚠ Le taux par matière est publié parce que l'énoncé porte dessus : sur une spirale
             # NUE la moyenne des incréments DOIT valoir l'enroulement, et un nombre lu dans une
             # batterie n'est pas un nombre publié.
             "taux_median_rad": _taux_median([c for c in cases if c["nom"] == nom], "la pince"),
             **{n: int(sum(c["bras"][n].get("reussites") or 0
                           for c in cases if c["nom"] == nom)) for n in BRAS}}
            for nom in dict.fromkeys(c["nom"] for c in cases)]
        # ⭐ La barre de `140`, lue et non choisie : la matière du rouleau, tous bruits confondus.
        dures = [c for c in cases
                 if (round(c["ecrasement"], 4), round(c["amplitude_um"], 1))
                 == (round(LA_MATIERE_DE_140[0], 4), round(LA_MATIERE_DE_140[1], 1))]
        bloc["sur_la_matiere_de_140"] = {
            "cases": len(dures),
            **{n: int(sum(c["bras"][n].get("reussites") or 0 for c in dures)) for n in BRAS}}
        out.append(bloc)
    return {"par_variante": out}


def apparie(grille: dict, temoin, autre, bras: str = "la pince") -> dict:
    """Le MÊME départ sous deux règles : ce qui est gagné, ce qui est perdu, et le solde.

    ⭐⭐⭐⭐ UN SOLDE NE DIT PAS CE QU'IL A COÛTÉ. « 110 contre 108 » est compatible avec deux
    réussites gagnées et rien de perdu, comme avec dix gagnées et huit perdues — ce ne sont pas les
    mêmes faits, et le second dirait qu'une règle déplace les réussites au lieu d'en ajouter. Les
    départs sont identiques d'une règle à l'autre (même matière, même bruit, même angle de départ),
    donc l'appariement est exact et ne coûte aucune marche.

    ⚠ « Réussite » n'est pas réécrit : c'est `une_reussite` du module partagé, le prédicat JOINT.
    """
    def par_depart(f):
        out = {}
        for c in grille["cases"]:
            if not f(c):
                continue
            for x in c["bras"][bras]["suivis"]:
                out[(c["nom"], float(c["bruit"]), float(x.get("depart_deg", -1.0)))] = une_reussite(x)
        return out

    a_, b_ = par_depart(temoin), par_depart(autre)
    communs = sorted(set(a_) & set(b_))
    if not communs:
        return {"decidable": False, "raison": "aucun départ commun aux deux règles"}
    gains = [k for k in communs if b_[k] and not a_[k]]
    pertes = [k for k in communs if a_[k] and not b_[k]]
    return {"decidable": True, "paires": len(communs), "gains": len(gains),
            "pertes": len(pertes), "solde": len(gains) - len(pertes),
            "elle_ne_perd_rien": not pertes,
            "matieres_gagnees": sorted({k[0] for k in gains}),
            "matieres_perdues": sorted({k[0] for k in pertes})}


def le_taux_lu_retrouve_t_il_lenroulement(grille: dict) -> dict:
    """Sur une spirale NUE et sans bruit, la moyenne des incréments DOIT valoir `avance / rayon`.

    ⭐⭐⭐ C'EST L'ÉNONCÉ QUI AUTORISE TOUT LE RESTE, et il se vérifie sur la mesure elle-même plutôt
    que dans une batterie : si la moyenne lue ne retrouvait pas l'enroulement là où il n'y a rien
    d'autre à trouver, « tourner au taux lu » et « tourner à l'enroulement » ne seraient pas deux
    règles d'une même famille, et les comparer ne voudrait rien dire.

    ⚠⚠ LA BORNE EST DÉRIVÉE DE L'EXCURSION DU RAYON, PAS CHOISIE — et ma première dérivation était
    FAUSSE, la mesure l'a dit. J'avais borné l'excursion à ce qu'une FENÊTRE fait croître le rayon,
    en oubliant deux choses plus grandes : le départ est RECALÉ sur la feuille la plus proche, donc
    il s'écarte du rayon nominal de jusqu'à une demi-épaisseur, et une marche fait un TOUR entier,
    donc le rayon croît d'un pas de feuille de plus. Le rayon parcourt
    `[r − pas/2, r + 3 pas/2]`, et l'enroulement varie d'autant. On ne peut pas exiger un accord
    plus serré que l'excursion de la quantité elle-même.

    ⚠ Ce défaut est passé inaperçu dans la batterie parce qu'elle marche UN départ sur un
    vingtième de tour : ni le recalage ni la croissance n'y ont la place de se voir.
    """
    avance = AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM
    rayon = RAYON_MM * 1000.0
    enroulement = avance / rayon
    cases = [c for c in grille["cases"]
             if str(c.get("cap_tournant", "")) == "taux" and float(c["bruit"]) == 0.0
             and float(c["ecrasement"]) == 0.0 and float(c["amplitude_um"]) == 0.0]
    lu = _taux_median(cases, "la pince") if cases else None
    if lu is None:
        return {"decidable": False, "raison": "aucune marche au taux lu sur une spirale nue sans bruit"}
    pas = _PAS()
    borne = max(avance / (rayon - 0.5 * pas) - enroulement,
                enroulement - avance / (rayon + 1.5 * pas))
    # ⚠⚠ EN MICRO-RADIANS ENTIERS, ET C'EST UNE GARDE QUI L'A EXIGÉ. Arrondi en radians, l'écart
    # vaut 7,4e-05 — et `json.dumps` écrit un tel nombre en NOTATION SCIENTIFIQUE, donc il devient
    # introuvable pour qui cherche « 0,000074 » dans le fichier de résultat, garde comprise. Un
    # chiffre qu'aucun lecteur ne peut retrouver dans son propre record n'est pas publié.
    return {"decidable": True, "matiere": "spirale nue", "bruit": 0.0, "unite": "micro-radian",
            "taux_lu_urad": int(round(abs(lu) * 1e6)),
            "enroulement_derive_urad": int(round(enroulement * 1e6)),
            "ecart_urad": int(round(abs(abs(lu) - enroulement) * 1e6)),
            "borne_derivee_urad": int(round(borne * 1e6)),
            "il_le_retrouve": bool(abs(abs(lu) - enroulement) <= borne)}


def les_temoins_internes(grille: dict, precedent: dict | None) -> dict:
    """Les deux caps STATIQUES doivent reproduire `144` et `145` exactement.

    ⚠⚠ C'est aussi la preuve que le module partagé n'a pas bougé en gagnant le cap tournant : un
    refactor d'une classe partagée doit PROUVER que les mesures publiées sont inchangées, et un
    témoin qui retombe au nombre près est cette preuve.
    """
    if not precedent:
        return {"decidable": False, "raison": "la mesure de `145` est absente, les témoins manquent"}
    refs = {}
    for v in precedent.get("juger", {}).get("par_variante", []):
        if v.get("bloc") == 1 and not v.get("corrige"):
            refs["cap statique (`144`)"] = v
        elif v.get("bloc") == 1 and v.get("corrige"):
            refs["cap statique corrigé (`145`)"] = v
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


def le_cap_tourne_t_il(pv: list[dict], apparies: list[dict] | None = None) -> dict:
    """Un cap qui tourne bat-il le cap statique — et tourne-t-il vraiment ?

    ⭐⭐⭐⭐ LA VICTOIRE EST JOINTE, ET LA MESURE A DÛ ME L'APPRENDRE. Ma première version comparait
    des TOTAUX : plus de réussites que le témoin, donc gagné. Or un total est satisfait par un
    DÉPLACEMENT — « 110 contre 108 » s'est révélé être huit réussites gagnées contre six perdues sur
    cent quatre-vingts départs, c'est-à-dire une règle qui change quatorze départs et en remporte
    huit. Ce n'est pas l'effet revendiqué. C'est exactement le piège que `143` a payé quand sa barre
    a été franchie par une marche qui bouclait son tour sur une AUTRE feuille : un verdict satisfait
    par autre chose que ce qu'il demande ne contrôle rien.

    ⭐⭐⭐ L'ÉNONCÉ CORRIGÉ, ET IL EST EXACT PLUTÔT QUE SEUILLÉ : une règle l'emporte si elle rend
    plus de réussites que le témoin ET n'en perd AUCUNE sur les départs appariés. C'est ce que
    revendique le mécanisme — un cap statique freine l'enroulement, donc le faire tourner à
    l'enroulement enlève un coût SYSTÉMATIQUE, et un coût systématique enlevé ne se paie nulle part.
    Des pertes disent que l'effet n'est pas celui-là.

    ⚠⚠ ET LA GARDE QUI EMPÊCHE L'AUTRE FAUX : un cap annoncé tournant dont le taux médian serait NUL
    serait un cap statique déguisé, et il rendrait alors exactement le témoin — un résultat
    « identique » qu'on lirait comme « ça ne change rien » alors que rien n'aurait été essayé.
    """
    statique = next((x for x in pv if not x["cap"] and not x["corrige"]), None)
    if statique is None:
        return {"decidable": False, "raison": "le témoin statique manque"}
    tournants = [x for x in pv if x["cap"]]
    if not tournants:
        return {"decidable": False, "raison": "aucune règle tournante"}
    ap = {y["nom"]: y for y in (apparies or []) if y.get("decidable")}
    contre = [{"nom": x["nom"], "cap": x["cap"],
               "reussites_de_la_pince": x["la pince"]["reussites"],
               "taux_median_rad": x["la pince"]["taux_median_rad"],
               "le_cap_tourne_vraiment": bool(x["la pince"]["taux_median_rad"] is not None
                                              and abs(x["la pince"]["taux_median_rad"]) > 0.0),
               "bruits_ou_elle_separe": x["bruits_ou_elle_separe"],
               "sur_la_matiere_de_140": x["sur_la_matiere_de_140"]["la pince"],
               "gains": ap.get(x["nom"], {}).get("gains"),
               "pertes": ap.get(x["nom"], {}).get("pertes"),
               "solde": ap.get(x["nom"], {}).get("solde"),
               "elle_ne_perd_rien": ap.get(x["nom"], {}).get("elle_ne_perd_rien"),
               "elle_bat_le_statique": bool(
                   x["la pince"]["reussites"] > statique["la pince"]["reussites"]
                   and ap.get(x["nom"], {}).get("elle_ne_perd_rien") is True)}
              for x in tournants]
    meilleure = max(contre, key=lambda y: y["reussites_de_la_pince"])
    return {"decidable": True,
            "le_statique": {"nom": statique["nom"],
                            "reussites_de_la_pince": statique["la pince"]["reussites"],
                            "taux_median_rad": statique["la pince"]["taux_median_rad"],
                            "bruits_ou_elle_separe": statique["bruits_ou_elle_separe"],
                            "sur_la_matiere_de_140": statique["sur_la_matiere_de_140"]["la pince"]},
            "par_regle": contre,
            "la_meilleure": meilleure["nom"],
            "toutes_tournent_vraiment": bool(all(y["le_cap_tourne_vraiment"] for y in contre)),
            "un_cap_qui_tourne_bat_le_statique": bool(meilleure["elle_bat_le_statique"]),
            # ⚠ La barre de `140` est une question à part : la battre sur la grille entière ne dit
            # rien de la matière sur laquelle personne n'a jamais réussi un transfert.
            "la_barre_de_140_est_franchie": bool(meilleure["sur_la_matiere_de_140"] > 0)}


def juger(grille: dict, precedent: dict | None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    # ⭐⭐ Le solde apparié vient AVANT le verdict, parce que le verdict en dépend : un total seul
    # est satisfait par un déplacement de réussites.
    temoin = next((x for x in pv if not x["cap"] and not x["corrige"]), None)
    apparies = ([{"nom": x["nom"], **apparie(grille, _filtre(temoin["corrige"], temoin["cap"]),
                                             _filtre(x["corrige"], x["cap"]))}
                 for x in pv if x["cap"]] if temoin is not None else [])
    return {"decidable": True, "par_variante": pv,
            "apparie_au_statique": apparies,
            "le_taux_lu_retrouve_t_il_lenroulement": le_taux_lu_retrouve_t_il_lenroulement(grille),
            "les_temoins_internes": les_temoins_internes(grille, precedent),
            "le_cap_tourne_t_il": le_cap_tourne_t_il(pv, apparies)}


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
    t = j["les_temoins_internes"]
    if t.get("decidable"):
        marque = "★" if t["le_protocole_est_le_meme"] else "✗"
        print(f"{marque} témoins internes — `144` et `145` doivent se reproduire à travers le "
              f"module partagé :")
        for x in t["par_variante"]:
            print(f"     {x['nom']:>28} : "
                  + " · ".join(f"{n} {x[n]['ici']} contre {x[n]['dans_145']}" for n in BRAS))
    print(f"\n   fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour :")
    print(f"   {'règle':>28} | {'réussites':>9} | {'taux médian':>11} | "
          f"{'`140`':>5} | bruits où elle sépare")
    for x in j["par_variante"]:
        tx = x["la pince"]["taux_median_rad"]
        print(f"   {x['nom']:>28} | {x['la pince']['reussites']:>9d} | "
              f"{'—' if tx is None else f'{tx:>11.6f}'} | "
              f"{x['sur_la_matiere_de_140']['la pince']:>5d} | {x['bruits_ou_elle_separe']}")
    print("\n   l'écart entre matières contre la dispersion dans une :")
    for x in j["par_variante"]:
        print(f"     {x['nom']:>28} : " + " · ".join(
            f"bruit {y['bruit']:g} {y['ecart_entre_matieres']:.4f}/"
            f"{y['dispersion_dans_une_matiere']:.4f}"
            f"{'✓' if y['la_lecture_separe'] else '✗'}" for y in x["par_bruit"]))
    e_ = j.get("le_taux_lu_retrouve_t_il_lenroulement", {})
    if e_.get("decidable"):
        marque = "★" if e_["il_le_retrouve"] else "✗"
        print(f"\n{marque} sur une spirale NUE sans bruit, le taux LU retrouve l'enroulement : "
              f"{e_['taux_lu_urad']} µrad par pas contre {e_['enroulement_derive_urad']} dérivés, "
              f"écart {e_['ecart_urad']} pour une borne dérivée de {e_['borne_derivee_urad']}")
    ap = j.get("apparie_au_statique")
    if ap:
        print("\n   le MÊME départ sous les deux règles — gains, pertes, solde :")
        for x in ap:
            if x.get("decidable"):
                print(f"     {x['nom']:>28} : {x['gains']:>2d} gagnées, {x['pertes']:>2d} perdues, "
                      f"solde {x['solde']:+d} sur {x['paires']} départs")
    c_ = j["le_cap_tourne_t_il"]
    if c_.get("decidable"):
        marque = "★★★★" if c_["un_cap_qui_tourne_bat_le_statique"] else "✗"
        m_ = next(y for y in c_["par_regle"] if y["nom"] == c_["la_meilleure"])
        print(f"\n{marque} un cap qui TOURNE bat-il le cap statique ? "
              f"{c_['un_cap_qui_tourne_bat_le_statique']} — la meilleure est "
              f"« {c_['la_meilleure']} », {m_['reussites_de_la_pince']} contre "
              f"{c_['le_statique']['reussites_de_la_pince']}, mais {m_['gains']} gagnées pour "
              f"{m_['pertes']} perdues")
        print(f"   tous les caps tournants tournent vraiment : {c_['toutes_tournent_vraiment']}")
        print(f"   la barre de `140` est franchie : {c_['la_barre_de_140_est_franchie']}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def case(corrige, cap, bruit, nom, mems, r=6, taux=0.01, ecr=0.0, amp=0.0):
        return {"ecrasement": ecr, "amplitude_um": amp, "bruit": bruit, "nom": nom,
                "departs": len(mems), "fenetre_du_cap": FENETRE, "bloc_du_cap": 1,
                "corrige_le_bruit": corrige, "enroulement_du_cap": False, "cap_tournant": cap,
                "bras": {b: {"reussites": r, "memes_feuilles": r, "tours_boucles": r,
                             "suivis": [{"decidable": True, "memoire_mediane": m,
                                         "taux_median_rad": taux} for m in mems]}
                         for b in BRAS}}

    v("le filtre distingue un cap statique d'un cap tournant",
      _filtre(False, "")(case(False, "", 0.0, "x", [0.1]))
      and not _filtre(False, "taux")(case(False, "", 0.0, "x", [0.1]))
      and _filtre(False, "taux")(case(False, "taux", 0.0, "x", [0.1])))
    v("... et il ne confond pas les trois règles tournantes",
      not _filtre(False, "enroulement")(case(False, "taux_planche", 0.0, "x", [0.1])))
    v("⚠ le filtre écarte une case de `146` : l'enroulement y était une MÉMOIRE, ici c'est un TAUX",
      not _filtre(False, "")({**case(False, "", 0.0, "x", [0.1]),
                              "enroulement_du_cap": True}))

    grille = {"fenetre": FENETRE, "departs": 2,
              "variantes": [{"nom": "cap statique (`144`)", "corrige": False, "cap": ""},
                            {"nom": "tournant au taux lu", "corrige": False, "cap": "taux"}],
              "cases": [case(False, "", 0.0, "A", [0.10, 0.12], r=9, taux=0.0),
                        case(False, "", 0.0, "B", [0.70, 0.72], r=9, taux=0.0),
                        case(False, "", 0.0, "dure", [0.5, 0.5], r=0, taux=0.0,
                             ecr=LA_MATIERE_DE_140[0], amp=LA_MATIERE_DE_140[1]),
                        case(False, "taux", 0.0, "A", [0.40, 0.90], r=6, taux=0.0098),
                        case(False, "taux", 0.0, "B", [0.42, 0.92], r=6, taux=0.0098),
                        case(False, "taux", 0.0, "dure", [0.5, 0.5], r=3, taux=0.0098,
                             ecr=LA_MATIERE_DE_140[0], amp=LA_MATIERE_DE_140[1])]}
    pv = par_variante(grille)["par_variante"]
    v("les réussites, le taux employé et la séparation sortent par règle",
      pv[0]["la pince"]["reussites"] == 18 and pv[0]["la pince"]["taux_median_rad"] == 0.0
      and pv[1]["la pince"]["reussites"] == 15
      and pv[1]["la pince"]["taux_median_rad"] == 0.0098)
    v("⭐ la barre de `140` est LUE sur la matière du rouleau, jamais sur la grille entière",
      pv[0]["sur_la_matiere_de_140"]["la pince"] == 0
      and pv[1]["sur_la_matiere_de_140"]["la pince"] == 3
      and pv[0]["sur_la_matiere_de_140"]["cases"] == 1,
      "18 réussites au total et zéro sur la matière qui compte")

    j = juger(grille, None)
    c_ = j["le_cap_tourne_t_il"]
    v("⭐⭐ une règle tournante qui rend MOINS de réussites ne bat pas le statique",
      c_["un_cap_qui_tourne_bat_le_statique"] is False, "15 contre 18")
    v("⭐⭐ ... mais elle franchit la barre de `140`, et c'est une question à part",
      c_["la_barre_de_140_est_franchie"] is True,
      "les deux verdicts ne peuvent pas se satisfaire l'un l'autre")
    v("⭐⭐ le cap tournant est déclaré tournant parce que son taux n'est pas nul",
      c_["toutes_tournent_vraiment"] is True
      and c_["le_statique"]["taux_median_rad"] == 0.0)

    # ---- ⭐⭐⭐⭐ LA VICTOIRE EST JOINTE : un total est satisfait par un DÉPLACEMENT
    def suivi(deg, ok, taux):
        return {"decidable": True, "depart_deg": float(deg), "memoire_mediane": 0.5,
                "taux_median_rad": taux, "tour_boucle": bool(ok),
                "derive_en_feuilles": 0.1 if ok else 3.0}

    def case_ap(cap, nom, oks, taux):
        return {"ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0, "nom": nom,
                "departs": len(oks), "fenetre_du_cap": FENETRE, "bloc_du_cap": 1,
                "corrige_le_bruit": False, "enroulement_du_cap": False, "cap_tournant": cap,
                "bras": {b: {"reussites": int(sum(oks)), "memes_feuilles": int(sum(oks)),
                             "tours_boucles": int(sum(oks)),
                             "suivis": [suivi(60 * i, o, taux) for i, o in enumerate(oks)]}
                         for b in BRAS}}

    def grille_ap(oks_temoin, oks_tournant):
        return {"fenetre": FENETRE, "departs": len(oks_temoin),
                "variantes": [{"nom": "cap statique (`144`)", "corrige": False, "cap": ""},
                              {"nom": "tournant à l'enroulement", "corrige": False,
                               "cap": "enroulement"}],
                "cases": [case_ap("", "A", oks_temoin, 0.0),
                          case_ap("enroulement", "A", oks_tournant, 0.0099)]}

    #     témoin  : 3 réussites · tournante : 4 réussites, mais UNE perdue en chemin
    deplace = juger(grille_ap([1, 1, 1, 0, 0], [1, 1, 0, 1, 1]), None)
    ap_ = deplace["apparie_au_statique"][0]
    v("⭐⭐⭐ le solde apparié sépare ce qui est AJOUTÉ de ce qui est DÉPLACÉ",
      ap_["gains"] == 2 and ap_["pertes"] == 1 and ap_["solde"] == 1 and ap_["paires"] == 5,
      "4 réussites contre 3, mais 2 gagnées pour 1 perdue")
    v("⭐⭐⭐⭐ ... et une règle qui DÉPLACE des réussites ne gagne pas, même avec un total "
      "supérieur",
      deplace["le_cap_tourne_t_il"]["un_cap_qui_tourne_bat_le_statique"] is False,
      "c'est le piège que `143` a payé : un verdict satisfait par autre chose que ce qu'il demande")
    ajoute_ = juger(grille_ap([1, 1, 1, 0, 0], [1, 1, 1, 1, 0]), None)
    v("⭐⭐⭐⭐ ... alors qu'une règle qui en AJOUTE sans rien perdre gagne",
      ajoute_["le_cap_tourne_t_il"]["un_cap_qui_tourne_bat_le_statique"] is True
      and ajoute_["apparie_au_statique"][0]["pertes"] == 0,
      "4 contre 3, 1 gagnée, 0 perdue")
    egal = juger(grille_ap([1, 1, 1, 0, 0], [1, 1, 1, 0, 0]), None)
    v("... et une règle qui ne change rien ne gagne pas non plus",
      egal["le_cap_tourne_t_il"]["un_cap_qui_tourne_bat_le_statique"] is False
      and egal["apparie_au_statique"][0]["gains"] == 0)
    v("⚠ « réussite » n'est pas réécrit ici : c'est le prédicat JOINT du module partagé",
      une_reussite(suivi(0, True, 0.0)) and not une_reussite(suivi(0, False, 0.0))
      and not une_reussite({"decidable": False, "tour_boucle": True,
                            "derive_en_feuilles": 0.0}))
    v("sans départ commun, le solde apparié est indécidable",
      not apparie(grille_ap([1], [1]), _filtre(False, "taux"), _filtre(False, ""))["decidable"])

    fige = json.loads(json.dumps(grille))
    for c in fige["cases"]:
        if c["cap_tournant"]:
            for b in BRAS:
                for x in c["bras"][b]["suivis"]:
                    x["taux_median_rad"] = 0.0
    v("⭐⭐⭐ ... et un cap annoncé tournant dont le taux est NUL est démasqué",
      juger(fige, None)["le_cap_tourne_t_il"]["toutes_tournent_vraiment"] is False,
      "sinon « ça ne change rien » se confondrait avec « rien n'a été essayé »")

    gagne = json.loads(json.dumps(grille))
    for c in gagne["cases"]:
        if c["cap_tournant"]:
            for b in BRAS:
                c["bras"][b]["reussites"] = 11
    v("⭐⭐ une règle tournante qui rend PLUS de réussites bat le statique",
      juger(gagne, None)["le_cap_tourne_t_il"]["un_cap_qui_tourne_bat_le_statique"] is True,
      "22 contre 18")
    v("sans témoin statique, le verdict est indécidable",
      not le_cap_tourne_t_il([{"nom": "t", "corrige": False, "cap": "taux",
                               "la pince": {"reussites": 1, "taux_median_rad": 0.1}}])["decidable"])
    v("... et sans règle tournante aussi",
      not le_cap_tourne_t_il([{"nom": "s", "corrige": False, "cap": "",
                               "la pince": {"reussites": 1, "taux_median_rad": 0.0},
                               "bruits_ou_elle_separe": [],
                               "sur_la_matiere_de_140": {"la pince": 0}}])["decidable"])
    v("un jugement sans case est indécidable", not juger({"cases": []}, None)["decidable"])
    v("⚠ un suivi indécidable est SAUTÉ, pas lu comme un cap immobile",
      _taux_median([{"bras": {"la pince": {"suivis": [
          {"decidable": False, "taux_median_rad": None},
          {"decidable": True, "taux_median_rad": 0.02}]}}}], "la pince") == 0.02)
    v("... et une case sans aucun suivi lisible ne rend rien plutôt que zéro",
      _taux_median([{"bras": {"la pince": {"suivis": [
          {"decidable": False, "taux_median_rad": None}]}}}], "la pince") is None)

    # ---- les témoins internes
    ref = {"juger": {"par_variante": [
        {"nom": "brute", "bloc": 1, "corrige": False, **{n: {"reussites": 18} for n in BRAS}},
        {"nom": "corrigée", "bloc": 1, "corrige": True, **{n: {"reussites": 99} for n in BRAS}}]}}
    t = les_temoins_internes(grille, ref)
    v("⭐⭐ le témoin interne compare le cap statique à ce que `145` publie",
      t["decidable"] and t["le_protocole_est_le_meme"] is True)
    faux = json.loads(json.dumps(ref))
    faux["juger"]["par_variante"][0]["la pince"]["reussites"] = 7
    v("⭐⭐⭐ ... et il DIT quand le module partagé a bougé",
      les_temoins_internes(grille, faux)["le_protocole_est_le_meme"] is False,
      "c'est la preuve que le cap tournant n'a rien déplacé de publié")
    v("sans `145`, les témoins sont indécidables",
      not les_temoins_internes(grille, None)["decidable"])

    # ---- ⭐ de bout en bout, sur une vraie matière
    nue = une_case((0.0, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                   fenetre_du_cap=FENETRE, cap_tournant="taux")
    statique = une_case((0.0, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                        fenetre_du_cap=FENETRE)

    def taux(c):
        xs = [x["taux_median_rad"] for x in c["bras"]["la pince"]["suivis"]
              if x.get("decidable") and x.get("taux_median_rad") is not None]
        return xs[0] if xs else None

    # ⚠⚠ PAS DE `or` POUR UN DÉFAUT : `0.0 or 1.0` vaut 1.0 en Python, et zéro est précisément la
    # valeur qu'un cap statique doit rendre ici.
    v("⭐⭐ sur une vraie marche, le cap tournant tourne du côté de la marche",
      taux(nue) is not None and taux(nue) != 0.0, f"{taux(nue)} rad par pas")
    v("⭐⭐ ... et le cap statique ne tourne pas du tout",
      taux(statique) is not None and taux(statique) == 0.0, f"{taux(statique)}")
    # ⚠⚠ La borne n'est pas choisie : c'est le producteur qui la dérive, et la batterie l'appelle
    # au lieu d'en poser une seconde. Un « à un pour cent près » aurait été un seuil.
    e2 = le_taux_lu_retrouve_t_il_lenroulement(
        {"fenetre": FENETRE, "cases": [nue]})
    v("⭐⭐⭐ et sur une spirale NUE ce taux retrouve l'enroulement, sous une borne DÉRIVÉE",
      e2["decidable"] and e2["il_le_retrouve"] is True,
      f"{e2['taux_lu_urad']} µrad contre {e2['enroulement_derive_urad']} dérivés, écart "
      f"{e2['ecart_urad']} pour une borne de {e2['borne_derivee_urad']}")
    v("⭐⭐ ... et cette vérification SAIT échouer",
      le_taux_lu_retrouve_t_il_lenroulement(
          {"fenetre": FENETRE,
           "cases": [{**nue, "bras": {b: {"suivis": [
               {**x, "taux_median_rad": (x["taux_median_rad"] or 0.0) * 2.0}
               for x in nue["bras"][b]["suivis"]]} for b in BRAS}}]})["il_le_retrouve"] is False,
      "un taux double de l'enroulement doit être refusé")
    v("sans marche au taux lu sur une spirale nue, l'énoncé est indécidable",
      not le_taux_lu_retrouve_t_il_lenroulement(
          {"fenetre": FENETRE, "cases": [statique]})["decidable"])
    v("... et la variante voyage jusque dans la case", nue["cap_tournant"] == "taux")

    petit = {"sur_la_grille": {"cases": [nue], "departs": 1, "tours": 0.05, "fenetre": FENETRE,
                               "bruits": [0.0], "largeur_en_pas": LARGEUR_DE_REFERENCE,
                               "variantes": [{"nom": "tournant au taux lu", "corrige": False,
                                              "cap": "taux"}]}}
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
