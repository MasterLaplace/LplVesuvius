"""La croix marche-t-elle le tour ? — la première grille depuis `142` qui paie un instrument réparé.

⭐⭐⭐⭐ POURQUOI CETTE GRILLE, ET POURQUOI MAINTENANT. Toutes les grilles depuis `142` ont payé un
**réglage** — une mémoire, une fenêtre, un cap qui tourne — et toutes ont déplacé des réussites sans
en ajouter. Trois tranches viennent de changer autre chose : `153` a montré que la mâchoire en
segment **ne peut pas exprimer** une normale sortie du plan du tour, ce que la matière du rouleau
impose et elle seule ; `154` a mesuré de combien il restait à prendre, en divisant l'erreur par
l'échelle de la matière ; `155` a trouvé ce qui le prend, en écartant les appuis tombés sur un autre
interstice. C'est la première fois qu'un changement d'instrument **rapproche la pose de son
échelle** — de **2,84×** à **1,23×** — au lieu de déplacer des réussites, donc c'est la première
fois qu'une grille vaut son prix.

⚠⚠ ET L'ATTENTE SE DIT AVANT LA MESURE, SINON ELLE SE LIT APRÈS COUP. `149` mesure que la pince ne
meurt pas de dérive mais d'**arrêt**, et que c'est la **pose** qui échoue : vingt et un refus de
pose contre zéro refus de contrainte. `150` mesure que cette pose tombe à **633 ‰** à l'angle où le
cap incline la normale. Une pose plus juste devrait donc **arrêter moins**. C'est l'énoncé que cette
grille peut confirmer ou réfuter — et « elle arrête moins » n'est PAS « elle réussit plus ». Les
deux se comptent à part, parce qu'une marche peut cesser de s'arrêter et finir sur la mauvaise
feuille.

⚠⚠ LA BARRE EST CELLE DE `144`, LUE ET NON CHOISIE : **108** réussites pour la pince et **49**
marches arrêtées, au meilleur réglage de cap (mémoire LUE, fenêtre 32). Elle est **remesurée ici**
plutôt que recopiée, pour deux raisons : le témoin frais prouve que le passage de `en_croix` et
`rejeter` à travers `suivre` n'a rien déplacé, et il donne le contrôle qui manque autrement — une
marche sans rejet doit écarter **zéro** appui.

⚠⚠⚠ ET LA VICTOIRE EST JOINTE, comme depuis `147` : plus de réussites ET aucune perdue sur les
départs APPARIÉS. Un total seul est satisfait par un déplacement, et ce module ne réécrit ni
l'appariement (`apparie`, de `147`) ni le prédicat de réussite (`une_reussite`, du module partagé).

Usage :
    uv run python src/nappe/la_croix_marche_t_elle_le_tour.py --verifier
    uv run python src/nappe/la_croix_marche_t_elle_le_tour.py \\
        --json docs/mesures/la_croix_marche_t_elle_le_tour.json
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
                                            MATIERES, _resumer_un_bras, une_case,
                                            une_reussite)
from un_cap_qui_tourne import apparie  # noqa: E402

FENETRE = 32
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
# (nom, en_croix, rejeter) — le témoin d'abord, parce qu'il est la barre.
VARIANTES = (("la pince de `144`", False, False),
             ("la croix (`153`)", True, False),
             ("le rejet (`155`)", False, True),
             ("la croix et le rejet", True, True))
# ⚠ La matière que `140` retient comme celle du rouleau, et sur laquelle personne n'a jamais réussi
# un transfert depuis `142`. Elle est NOMMÉE ici pour que la barre soit lue, pas choisie après coup.
LA_MATIERE_DE_140 = (0.2782, 100.0)
LE_PRECEDENT = RACINE / "docs" / "mesures" / "un_cap_qui_tourne.json"
# ⚠ Le nom que `147` donne à son témoin statique. Il est écrit ici parce que c'est la clé qui relie
# les deux records, et une clé devinée à la lecture serait un témoin absent déguisé en témoin vert.
LE_TEMOIN_DE_147 = "cap statique (`144`)"


def _filtre(en_croix: bool, rejeter: bool):
    """⚠ Une clé absente vaut FAUX : un record d'avant `156` ne connaît pas ces deux mots."""
    def f(c):
        return (bool(c.get("en_croix", False)) is bool(en_croix)
                and bool(c.get("rejeter", False)) is bool(rejeter))
    return f


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
                  departs: int = DEPARTS, tours: float = TOURS) -> dict:
    """Les quatre instruments sur la MÊME grille, au meilleur réglage de cap de `144`.

    ⚠ Le cap ne bouge pas d'une variante à l'autre : mémoire LUE, fenêtre 32, sans correction du
    bruit et sans cap tournant. Bouger deux choses à la fois rendrait un gain imputable à rien.
    """
    cases = []
    for m in matieres:
        for b in bruits:
            for nom, croix, rejet in variantes:
                c = une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours,
                             fenetre_du_cap=int(fenetre), en_croix=bool(croix),
                             rejeter=bool(rejet))
                c["variante"] = nom
                cases.append(c)
    return {"departs": int(departs), "tours": float(tours), "fenetre": int(fenetre),
            "bruits": [float(b) for b in bruits],
            "variantes": [{"nom": n, "en_croix": bool(c), "rejeter": bool(r)}
                          for n, c, r in variantes],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _lectures_medianes(cases, bras: str) -> int | None:
    """Le PRIX, et il se lit sur les marches et non sur une pose isolée.

    ⚠ Une donnée absente se SAUTE et ne se lit pas comme un zéro : une marche indécidable n'a pas
    lu gratuitement, elle n'a pas marché.
    """
    xs = [int(x["lectures"]) for c in cases for x in c["bras"][bras]["suivis"]
          if x.get("decidable") and x.get("lectures") is not None]
    return int(statistics.median(xs)) if xs else None


def par_variante(grille: dict) -> dict:
    """Pour chaque instrument : ce qu'il fait réussir, ce qu'il arrête, ce qu'il écarte, ce qu'il
    coûte.

    ⚠⚠ « Réussites », « arrêts » et « appuis rejetés » sont TROIS énoncés et non un verdict : une
    marche peut cesser de s'arrêter en finissant sur la mauvaise feuille, et une règle peut écarter
    beaucoup d'appuis sans rien changer au tour.
    """
    out = []
    for v in grille["variantes"]:
        f = _filtre(v["en_croix"], v["rejeter"])
        cases = [c for c in grille["cases"] if f(c)]
        if not cases:
            continue
        bloc = {**v, "cases": len(cases)}
        for nom in BRAS:
            bloc[nom] = {
                "reussites": int(sum(c["bras"][nom].get("reussites") or 0 for c in cases)),
                "memes_feuilles": int(sum(c["bras"][nom].get("memes_feuilles") or 0
                                          for c in cases)),
                "tours_boucles": int(sum(c["bras"][nom].get("tours_boucles") or 0
                                         for c in cases)),
                "arrets": int(sum(c["bras"][nom].get("arrets") or 0 for c in cases)),
                "poses_manquees": int(sum(c["bras"][nom].get("poses_manquees") or 0
                                          for c in cases)),
                "appuis_rejetes": int(sum(c["bras"][nom].get("appuis_rejetes") or 0
                                          for c in cases)),
                "marches_qui_rejettent": int(sum(c["bras"][nom].get("marches_qui_rejettent") or 0
                                                 for c in cases)),
                "lectures_medianes": _lectures_medianes(cases, nom)}
        # ⭐ OÙ ça change : les réussites matière par matière, tous bruits confondus. Un total sur
        # la grille ne dit pas si un instrument gagne partout un peu ou beaucoup quelque part.
        bloc["par_matiere"] = [
            {"nom": nom,
             **{n: int(sum(c["bras"][n].get("reussites") or 0
                           for c in cases if c["nom"] == nom)) for n in BRAS}}
            for nom in dict.fromkeys(c["nom"] for c in cases)]
        dures = [c for c in cases
                 if (round(c["ecrasement"], 4), round(c["amplitude_um"], 1))
                 == (round(LA_MATIERE_DE_140[0], 4), round(LA_MATIERE_DE_140[1], 1))]
        bloc["sur_la_matiere_de_140"] = {
            "cases": len(dures),
            **{n: int(sum(c["bras"][n].get("reussites") or 0 for c in dures)) for n in BRAS},
            "arrets": int(sum(c["bras"]["la pince"].get("arrets") or 0 for c in dures)),
            "appuis_rejetes": int(sum(c["bras"]["la pince"].get("appuis_rejetes") or 0
                                      for c in dures))}
        out.append(bloc)
    return {"par_variante": out}


def le_gain_par_bruit(grille: dict) -> dict:
    """OÙ le gain vit, et la réponse n'était pas celle que `155` faisait attendre.

    ⭐⭐⭐⭐ `155` recense les appuis aberrants sur des matières SANS BRUIT et conclut qu'ils
    demandent les DEUX causes physiques. Une marche, elle, lit un volume BRUITÉ : une lecture
    bruitée peut poser un appui sur l'interstice voisin exactement comme un froissement, et
    l'énoncé du rejet — « à plus d'une demi-épaisseur de la médiane de sa mâchoire » — ne demande
    pas quelle cause l'y a mis. Ce découpage est donc la question que `155` ne pouvait pas poser.

    ⚠⚠ Il est APPARIÉ à chaque niveau de bruit, jamais lu sur des totaux : un total par bruit
    serait satisfait par un déplacement de réussites d'une matière à l'autre dans le même bruit.
    """
    out = []
    for b in grille["bruits"]:
        ligne = {"bruit": float(b), "par_instrument": []}
        for v in grille["variantes"]:
            if not v["en_croix"] and not v["rejeter"]:
                continue

            def a_ce_bruit(regle, b=b):
                def f(c):
                    return regle(c) and abs(float(c["bruit"]) - float(b)) < 1e-12
                return f

            ap = apparie(grille, a_ce_bruit(_filtre(False, False)),
                         a_ce_bruit(_filtre(v["en_croix"], v["rejeter"])))
            cases_t = [c for c in grille["cases"]
                       if a_ce_bruit(_filtre(False, False))(c)]
            cases_a = [c for c in grille["cases"]
                       if a_ce_bruit(_filtre(v["en_croix"], v["rejeter"]))(c)]
            ligne["par_instrument"].append({
                "nom": v["nom"],
                "gains": ap.get("gains"), "pertes": ap.get("pertes"),
                "solde": ap.get("solde"), "paires": ap.get("paires"),
                "arrets_du_temoin": int(sum(c["bras"]["la pince"].get("arrets") or 0
                                            for c in cases_t)),
                "arrets": int(sum(c["bras"]["la pince"].get("arrets") or 0 for c in cases_a)),
                "appuis_rejetes": int(sum(c["bras"]["la pince"].get("appuis_rejetes") or 0
                                          for c in cases_a))})
        out.append(ligne)
    return {"par_bruit": out}


def le_temoin_interne(grille: dict, precedent: dict | None) -> dict:
    """La barre de `144` est-elle REPRODUITE par le module partagé une fois modifié ?

    ⭐⭐⭐ C'est le seul contrôle qui puisse dire qu'ajouter deux mots à `suivre` n'a rien déplacé.
    À `en_croix` et `rejeter` faux, le chemin doit être celui de `147` jusqu'au bit, donc les
    réussites et les arrêts du témoin frais doivent égaler ceux du record de `147`.

    ⚠ Un record absent se DIT et ne se devine pas : sans lui, il n'y a pas de barre, et annoncer
    une victoire contre une barre absente serait une victoire contre rien.
    """
    if precedent is None:
        return {"decidable": False, "raison": "le record de `147` est absent"}
    vieux = [c for c in precedent.get("sur_la_grille", {}).get("cases", [])
             if str(c.get("variante", "")) == LE_TEMOIN_DE_147]
    if not vieux:
        return {"decidable": False,
                "raison": f"aucune case « {LE_TEMOIN_DE_147} » dans le record de `147`"}
    neufs = [c for c in grille["cases"] if _filtre(False, False)(c)]
    if not neufs:
        return {"decidable": False, "raison": "aucun témoin frais dans cette grille"}
    par_bras = {}
    for nom in BRAS:
        par_bras[nom] = {
            "ici": int(sum(c["bras"][nom].get("reussites") or 0 for c in neufs)),
            "dans_147": int(sum(c["bras"][nom].get("reussites") or 0 for c in vieux))}
    arrets_ici = int(sum(c["bras"]["la pince"].get("arrets") or 0 for c in neufs))
    # ⚠ Le record de `147` ne publie pas d'arrêts : il est antérieur au champ. L'arrêt s'y compte
    # donc sur les suivis rangés, qui eux sont là — c'est la même définition, lue à la source.
    arrets_147 = int(sum(1 for c in vieux for x in c["bras"]["la pince"]["suivis"]
                         if x.get("fin") == "la pince ne peut plus avancer"))
    return {"decidable": True, "cases_ici": len(neufs), "cases_dans_147": len(vieux),
            "par_bras": par_bras, "arrets_ici": arrets_ici, "arrets_dans_147": arrets_147,
            # ⚠⚠ Et le témoin doit AUSSI n'écarter aucun appui : c'est ce qui prouve que le mot
            # `rejeter` fait quelque chose, plutôt que d'être passé et ignoré.
            "appuis_rejetes_ici": int(sum(c["bras"]["la pince"].get("appuis_rejetes") or 0
                                          for c in neufs)),
            "le_protocole_est_le_meme": bool(
                all(par_bras[n]["ici"] == par_bras[n]["dans_147"] for n in BRAS)
                and arrets_ici == arrets_147)}


def le_verdict(pv: list[dict], apparies: list[dict], par_bruit: list[dict] | None = None) -> dict:
    """La victoire JOINTE, l'arrêt compté À PART, et le prix publié.

    ⚠⚠⚠ UN TOTAL SEUL EST SATISFAIT PAR UN DÉPLACEMENT — c'est pourquoi la victoire exige de ne
    rien perdre sur les départs appariés, et pourquoi ce module ne réécrit pas l'appariement.

    ⚠⚠ « Elle arrête moins » est un énoncé SÉPARÉ, et il est celui que `149` et `150` font
    attendre. Il se publie qu'il aille dans le sens de la victoire ou non : une prédiction qui ne
    serait lue que lorsqu'elle se réalise ne serait pas une prédiction.
    """
    temoin = next((x for x in pv if not x["en_croix"] and not x["rejeter"]), None)
    if temoin is None:
        return {"decidable": False, "raison": "le témoin manque"}
    autres = [x for x in pv if x["en_croix"] or x["rejeter"]]
    if not autres:
        return {"decidable": False, "raison": "aucun instrument à comparer"}
    ap = {y["nom"]: y for y in (apparies or []) if y.get("decidable")}
    # ⭐⭐⭐⭐ OÙ la victoire est JOINTE, et c'est LU et non choisi : l'ensemble des niveaux de
    # bruit où l'instrument gagne des réussites sans en perdre aucune. Un niveau qui ne gagne ni
    # ne perd n'y entre pas — « elle ne change rien » n'est pas « elle gagne ».
    joints: dict = {}
    for ligne in (par_bruit or []):
        for y in ligne.get("par_instrument", []):
            if y.get("gains") and not y.get("pertes"):
                joints.setdefault(y["nom"], []).append(float(ligne["bruit"]))
    contre = [{"nom": x["nom"], "en_croix": x["en_croix"], "rejeter": x["rejeter"],
               "reussites_de_la_pince": x["la pince"]["reussites"],
               "arrets_de_la_pince": x["la pince"]["arrets"],
               "poses_manquees_de_la_pince": x["la pince"]["poses_manquees"],
               "appuis_rejetes": x["la pince"]["appuis_rejetes"],
               "marches_qui_rejettent": x["la pince"]["marches_qui_rejettent"],
               "lectures_medianes": x["la pince"]["lectures_medianes"],
               # ⚠ Le prix de CHAQUE instrument, et non du seul meilleur : c'est le couple
               # « ce qu'il coûte / ce qu'il achète » qui porte le fait de cette tranche, et une
               # moitié seule se lirait comme un niveau.
               "prix": (None if not (temoin["la pince"]["lectures_medianes"]
                                     and x["la pince"]["lectures_medianes"])
                        else round(x["la pince"]["lectures_medianes"]
                                   / temoin["la pince"]["lectures_medianes"], 4)),
               "sur_la_matiere_de_140": x["sur_la_matiere_de_140"]["la pince"],
               "gains": ap.get(x["nom"], {}).get("gains"),
               "pertes": ap.get(x["nom"], {}).get("pertes"),
               "solde": ap.get(x["nom"], {}).get("solde"),
               "elle_ne_perd_rien": ap.get(x["nom"], {}).get("elle_ne_perd_rien"),
               # ⚠ Le rejet RÉELLEMENT exercé : une règle annoncée qui n'écarterait jamais rien
               # serait la marche d'avant, déguisée.
               "le_rejet_sexerce": (None if not x["rejeter"]
                                    else bool(x["la pince"]["appuis_rejetes"] > 0)),
               "elle_arrete_moins": bool(x["la pince"]["arrets"]
                                         < temoin["la pince"]["arrets"]),
               "bruits_ou_elle_gagne_jointement": joints.get(x["nom"], []),
               "elle_bat_le_temoin": bool(
                   x["la pince"]["reussites"] > temoin["la pince"]["reussites"]
                   and ap.get(x["nom"], {}).get("elle_ne_perd_rien") is True)}
              for x in autres]
    meilleure = max(contre, key=lambda y: y["reussites_de_la_pince"])
    prix = (None if not (temoin["la pince"]["lectures_medianes"]
                         and meilleure["lectures_medianes"])
            else round(meilleure["lectures_medianes"]
                       / temoin["la pince"]["lectures_medianes"], 4))
    return {"decidable": True,
            "le_temoin": {"nom": temoin["nom"],
                          "reussites_de_la_pince": temoin["la pince"]["reussites"],
                          "arrets_de_la_pince": temoin["la pince"]["arrets"],
                          "poses_manquees_de_la_pince": temoin["la pince"]["poses_manquees"],
                          "lectures_medianes": temoin["la pince"]["lectures_medianes"],
                          "appuis_rejetes": temoin["la pince"]["appuis_rejetes"],
                          "sur_la_matiere_de_140": temoin["sur_la_matiere_de_140"]["la pince"]},
            "par_instrument": contre,
            "la_meilleure": meilleure["nom"],
            "un_instrument_repare_bat_le_temoin": bool(meilleure["elle_bat_le_temoin"]),
            "la_meilleure_arrete_moins": bool(meilleure["elle_arrete_moins"]),
            "le_prix_de_la_meilleure": prix,
            "bruits_ou_la_meilleure_gagne_jointement": joints.get(meilleure["nom"], []),
            "tous_les_rejets_sexercent": bool(
                all(y["le_rejet_sexerce"] for y in contre if y["rejeter"])),
            # ⚠ La barre de `140` est une question à part : la battre sur la grille entière ne dit
            # rien de la matière sur laquelle personne n'a jamais réussi un transfert.
            "la_barre_de_140_est_franchie": bool(meilleure["sur_la_matiere_de_140"] > 0)}


def juger(grille: dict, precedent: dict | None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    pv = par_variante(grille)["par_variante"]
    temoin = next((x for x in pv if not x["en_croix"] and not x["rejeter"]), None)
    apparies = ([{"nom": x["nom"],
                  **apparie(grille, _filtre(temoin["en_croix"], temoin["rejeter"]),
                            _filtre(x["en_croix"], x["rejeter"]))}
                 for x in pv if x["en_croix"] or x["rejeter"]] if temoin is not None else [])
    gb = le_gain_par_bruit(grille)
    return {"decidable": True, "par_variante": pv, "apparie_au_temoin": apparies,
            "le_gain_par_bruit": gb,
            "le_temoin_interne": le_temoin_interne(grille, precedent),
            "le_verdict": le_verdict(pv, apparies, gb["par_bruit"])}


def mesurer(matieres=MATIERES, bruits=BRUITS, variantes=VARIANTES, fenetre: int = FENETRE,
            departs: int = DEPARTS, tours: float = TOURS,
            precedent: Path = LE_PRECEDENT) -> dict:
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
    t = j["le_temoin_interne"]
    if t.get("decidable"):
        marque = "★" if t["le_protocole_est_le_meme"] else "✗"
        print(f"{marque} témoin interne — la barre de `144` doit se reproduire à travers `suivre` "
              f"une fois `en_croix` et `rejeter` ajoutés :")
        print("     " + " · ".join(f"{n} {t['par_bras'][n]['ici']} contre "
                                   f"{t['par_bras'][n]['dans_147']}" for n in BRAS))
        print(f"     arrêts {t['arrets_ici']} contre {t['arrets_dans_147']} · "
              f"appuis rejetés sans rejet {t['appuis_rejetes_ici']}")
    else:
        print(f"⚠ témoin interne indécidable — {t.get('raison')}")
    print(f"\n   fenêtre {g['fenetre']}, {g['departs']} départs par case, "
          f"{len(g['cases'])} cases, un tour :")
    print(f"   {'instrument':>22} | {'réuss.':>6} | {'arrêts':>6} | {'pose ✗':>6} | "
          f"{'rejetés':>7} | {'lectures':>9} | {'`140`':>5}")
    for x in j["par_variante"]:
        p = x["la pince"]
        # ⚠ Une donnée absente se DIT, elle ne se lit pas comme un zéro.
        lus = p["lectures_medianes"]
        lus = "—" if lus is None else f"{lus:d}"
        print(f"   {x['nom']:>22} | {p['reussites']:>6d} | {p['arrets']:>6d} | "
              f"{p['poses_manquees']:>6d} | {p['appuis_rejetes']:>7d} | {lus:>9} | "
              f"{x['sur_la_matiere_de_140']['la pince']:>5d}")
    ap = j.get("apparie_au_temoin")
    if ap:
        print("\n   le MÊME départ sous les deux instruments — gains, pertes, solde :")
        for x in ap:
            if x.get("decidable"):
                print(f"     {x['nom']:>22} : {x['gains']:>2d} gagnées, {x['pertes']:>2d} perdues, "
                      f"solde {x['solde']:+d} sur {x['paires']} départs")
    gb = j.get("le_gain_par_bruit", {}).get("par_bruit")
    if gb:
        print("\n   où le gain vit — apparié À CHAQUE niveau de bruit :")
        for x in gb:
            print(f"     bruit {x['bruit']:>4g} : " + " · ".join(
                f"{y['nom']} {y['gains']:+d}/{-y['pertes']:+d} "
                f"arrêts {y['arrets_du_temoin']}→{y['arrets']}"
                for y in x["par_instrument"]))
    v = j["le_verdict"]
    if v.get("decidable"):
        marque = "★★★★" if v["un_instrument_repare_bat_le_temoin"] else "✗"
        m_ = next(y for y in v["par_instrument"] if y["nom"] == v["la_meilleure"])
        print(f"\n{marque} un instrument RÉPARÉ bat-il la pince de `144` ? "
              f"{v['un_instrument_repare_bat_le_temoin']} — la meilleure est "
              f"« {v['la_meilleure']} », {m_['reussites_de_la_pince']} contre "
              f"{v['le_temoin']['reussites_de_la_pince']}, avec {m_['gains']} gagnées pour "
              f"{m_['pertes']} perdues")
        print(f"   elle arrête moins — l'énoncé SÉPARÉ que `149` et `150` font attendre : "
              f"{v['la_meilleure_arrete_moins']} ({m_['arrets_de_la_pince']} contre "
              f"{v['le_temoin']['arrets_de_la_pince']})")
        print(f"   le prix : {m_['lectures_medianes']} lectures médianes contre "
              f"{v['le_temoin']['lectures_medianes']}, soit ×{v['le_prix_de_la_meilleure']}")
        print(f"   ... et elle gagne JOINTEMENT aux bruits "
              f"{v['bruits_ou_la_meilleure_gagne_jointement']} — lus, pas choisis")
        print(f"   tous les rejets s'exercent vraiment : {v['tous_les_rejets_sexercent']}")
        print(f"   la barre de `140` est franchie : {v['la_barre_de_140_est_franchie']}")


def _suivi(depart_deg: float, reussi: bool, arrete: bool = False, rejetes: int = 0) -> dict:
    """Un suivi FACTICE, pour éprouver le verdict sans marcher.

    ⚠ Il passe par `une_reussite` comme tout le reste : une fixture qui fabriquerait la réussite
    autrement éprouverait sa propre convention et non celle du dépôt.
    """
    return {"depart_deg": float(depart_deg), "decidable": True,
            "tour_boucle": bool(reussi), "derive_en_feuilles": 0.0 if reussi else 3.0,
            "part_du_tour": 1.0 if reussi else 0.4, "refus": 0, "pas": 10,
            "lectures": 1000 + int(rejetes), "appuis_rejetes": int(rejetes),
            "fin": "la pince ne peut plus avancer" if arrete else "tour bouclé"}


def _case_factice(nom: str, variante: str, en_croix: bool, rejeter: bool, suivis) -> dict:
    """Une case FACTICE dont les résumés passent par `_resumer_un_bras` du module partagé."""
    ecr, amp = (LA_MATIERE_DE_140 if nom == "dure" else (0.0, 0.0))
    return {"nom": nom, "ecrasement": float(ecr), "amplitude_um": float(amp), "bruit": 0.0,
            "departs": len(suivis), "variante": variante, "en_croix": bool(en_croix),
            "rejeter": bool(rejeter),
            "bras": {b: {"suivis": suivis, **_resumer_un_bras(suivis, len(suivis))}
                     for b in BRAS}}


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from la_pince_tient_elle_la_feuille import suivre  # noqa: PLC0415
    from la_pince_tient_elle_la_feuille import (LONGUEUR_DONDE_UM,  # noqa: PLC0415
                                                AVANCE_EN_LONGUEUR_DONDE, RAYON_MM, _matiere,
                                                _PAS, _VOXEL, un_depart)
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um = _PAS(), _VOXEL()
    avance_um = AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM
    largeur_um = LARGEUR_DE_REFERENCE * pas_um

    # ⚠⚠⚠ LA FIXTURE EST DIMENSIONNÉE SUR L'EFFET, ET ELLE A DÛ L'ÊTRE. À bruit nul la pince ne
    # franchit PAS le premier pas sur la matière du rouleau — mesuré : `pas=0` — donc une marche
    # qui ne marche pas n'écarte aucun appui, et toute sonde du rejet y passerait au vert pour la
    # raison exactement inverse de celle qu'elle annonce. C'est le piège de `155`, repayé : une
    # fixture trop courte ne porte pas l'effet qu'elle prétend éprouver.
    BRUIT, TOURS_SONDE = 8.0, 0.15

    def marcher(matiere, **kw):
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, matiere[0], matiere[1], BRUIT,
                       LONGUEUR_DONDE_UM, RAYON_MM)
        depart, n0 = un_depart(vol, 0.0, RAYON_MM, voxel_um, pas_um)
        vol.lectures = 0
        return suivre(vol, depart, n0, largeur_um, pas_um, voxel_um, True, True, avance_um,
                      vol.centre_yx_vx, tours=TOURS_SONDE, fenetre_du_cap=FENETRE, **kw)

    print("— `suivre` passe-t-il enfin les deux mots ? —")
    droit = marcher(LA_MATIERE_DE_140)
    croix = marcher(LA_MATIERE_DE_140, en_croix=True)
    # ⚠⚠ D'ABORD prouver que les deux marches ont MARCHÉ, ensuite qu'elles diffèrent : une sonde
    # qui compare deux marches immobiles passe quoi qu'il arrive.
    v("⚠ les deux marches de la sonde marchent vraiment",
      droit["decidable"] and croix["decidable"] and droit["pas"] > 0 and croix["pas"] > 0,
      f"{droit['pas']} pas contre {croix['pas']}")
    v("⭐⭐⭐ `en_croix` traverse `suivre` — la marche N'EST PAS la même",
      droit["derive_en_feuilles"] != croix["derive_en_feuilles"],
      f"{droit['derive_en_feuilles']} contre {croix['derive_en_feuilles']} feuilles")
    # ⚠⚠⚠ ET LA SONDE PRÉCÉDENTE NE MORD PAS SUR LES PAS. Vérifié en cassant le code : n'ôter
    # `en_croix` qu'à la pose DU PAS laisse la marche différer quand même, parce que la pose de
    # DÉPART l'a encore et qu'elle change tout ce qui suit. Un suiveur qui poserait la croix au
    # départ puis le segment à chaque pas passerait donc au vert. Ce qui isole le pas est son
    # PRIX : la différence de lectures entre une marche bornée à zéro pas et une bornée à un.
    def cout(matiere, pas_max, **kw):
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, matiere[0], matiere[1], BRUIT,
                       LONGUEUR_DONDE_UM, RAYON_MM)
        depart, n0 = un_depart(vol, 0.0, RAYON_MM, voxel_um, pas_um)
        vol.lectures = 0
        r = suivre(vol, depart, n0, largeur_um, pas_um, voxel_um, True, True, avance_um,
                   vol.centre_yx_vx, tours=1.0, pas_max=pas_max, fenetre_du_cap=FENETRE, **kw)
        return int(r["lectures"])

    pose_d, pose_c = cout(LA_MATIERE_DE_140, 0), cout(LA_MATIERE_DE_140, 0, en_croix=True)
    pas_d = cout(LA_MATIERE_DE_140, 1) - pose_d
    pas_c = cout(LA_MATIERE_DE_140, 1, en_croix=True) - pose_c
    v("⭐⭐⭐⭐ `en_croix` traverse jusqu'aux PAS — la croix lit EXACTEMENT deux barres, au départ "
      "comme au pas",
      pose_c == 2 * pose_d and pas_c == 2 * pas_d and pas_d > 0,
      f"pose {pose_d} → {pose_c} lectures, pas {pas_d} → {pas_c}")
    avec = marcher(LA_MATIERE_DE_140, en_croix=True, rejeter=True)
    v("⭐⭐⭐ `rejeter` traverse `suivre` — sans lui la marche n'écarte RIEN",
      croix["appuis_rejetes"] == 0, f"{croix['appuis_rejetes']} appuis")
    v("⭐⭐⭐ ... et avec lui elle en écarte, sur la matière du rouleau",
      avec["appuis_rejetes"] > 0, f"{avec['appuis_rejetes']} appuis")
    v("⚠ un compte d'appuis est ENTIER", isinstance(avec["appuis_rejetes"], int))
    # ⭐⭐ L'énoncé de `155` porte sur la mâchoire en SEGMENT : un appui aberrant y demande les DEUX
    # causes. Il se vérifie donc à segment, sur deux matières qui marchent toutes les deux — sans
    # quoi « elle n'écarte rien » serait satisfait par une marche qui ne marche pas.
    seule = marcher((0.0, 42.4), rejeter=True)
    deux_causes = marcher(LA_MATIERE_DE_140, rejeter=True)
    v("⭐⭐ sous UNE seule cause le segment n'écarte rien, sous DEUX il écarte — `155` dans la marche",
      seule["decidable"] and deux_causes["decidable"]
      and seule["pas"] > 0 and deux_causes["pas"] > 0
      and seule["appuis_rejetes"] == 0 and deux_causes["appuis_rejetes"] > 0,
      f"{seule['appuis_rejetes']} sur la froissée seule contre "
      f"{deux_causes['appuis_rejetes']} sur celle du rouleau")

    print("\n— la case et la grille les passent-elles ? —")
    c_droit = une_case(LA_MATIERE_DE_140, BRUIT, LARGEUR_DE_REFERENCE, departs=1,
                       tours=TOURS_SONDE, fenetre_du_cap=FENETRE)
    c_croix = une_case(LA_MATIERE_DE_140, BRUIT, LARGEUR_DE_REFERENCE, departs=1,
                       tours=TOURS_SONDE, fenetre_du_cap=FENETRE, en_croix=True, rejeter=True)
    v("⭐⭐ `une_case` passe les deux mots à `suivre` — la case n'est PAS la même",
      c_droit["bras"]["la pince"]["suivis"][0].get("derive_en_feuilles")
      != c_croix["bras"]["la pince"]["suivis"][0].get("derive_en_feuilles")
      and c_croix["bras"]["la pince"]["appuis_rejetes"] > 0,
      f"{c_croix['bras']['la pince']['appuis_rejetes']} appuis écartés dans la case")
    v("⚠ ... et elle les RANGE, sinon aucun filtre ne pourrait les relire",
      c_droit["en_croix"] is False and c_croix["en_croix"] is True
      and c_croix["rejeter"] is True)
    v("⚠ `_resumer_un_bras` publie le compte d'appuis écartés et le compte d'arrêts",
      "appuis_rejetes" in c_croix["bras"]["la pince"]
      and "arrets" in c_croix["bras"]["la pince"])
    v("⚠ une clé absente vaut FAUX — un record d'avant `156` reste lisible",
      _filtre(False, False)({"nom": "x"}) and not _filtre(True, False)({"nom": "x"}))

    print("\n— le verdict est-il JOINT, et l'arrêt compté À PART ? —")
    temoin = [_case_factice("dure", "témoin", False, False,
                            [_suivi(0, True), _suivi(90, True), _suivi(180, False, arrete=True),
                             _suivi(270, False, arrete=True)])]
    # Deux gagnées, une perdue : le solde est positif et la victoire NE DOIT PAS l'être.
    deplace = [_case_factice("dure", "déplace", True, False,
                             [_suivi(0, False, arrete=True), _suivi(90, True),
                              _suivi(180, True), _suivi(270, True, rejetes=0)])]
    # Une gagnée, rien de perdu, et elle arrête moins.
    ajoute = [_case_factice("dure", "ajoute", False, True,
                            [_suivi(0, True), _suivi(90, True), _suivi(180, True, rejetes=4),
                             _suivi(270, False, arrete=True)])]
    g = {"departs": 4, "tours": 1.0, "fenetre": FENETRE, "bruits": [0.0],
         "variantes": [{"nom": "témoin", "en_croix": False, "rejeter": False},
                       {"nom": "déplace", "en_croix": True, "rejeter": False},
                       {"nom": "ajoute", "en_croix": False, "rejeter": True}],
         "largeur_en_pas": float(LARGEUR_DE_REFERENCE),
         "cases": temoin + deplace + ajoute}
    j = juger(g, None)
    ver = j["le_verdict"]
    par = {x["nom"]: x for x in ver["par_instrument"]}
    v("⭐⭐⭐⭐ un SOLDE positif ne suffit pas — « déplace » gagne 2, perd 1, et ne gagne PAS",
      par["déplace"]["solde"] == 1 and par["déplace"]["pertes"] == 1
      and par["déplace"]["elle_bat_le_temoin"] is False,
      f"solde {par['déplace']['solde']:+d} pour {par['déplace']['pertes']} perdue")
    v("⭐⭐⭐ ... alors qu'« ajoute » gagne une réussite sans rien perdre, et elle gagne",
      par["ajoute"]["gains"] == 1 and par["ajoute"]["pertes"] == 0
      and par["ajoute"]["elle_bat_le_temoin"] is True)
    v("⭐⭐ « elle arrête moins » est un énoncé SÉPARÉ — « déplace » arrête moins et ne gagne pas",
      par["déplace"]["elle_arrete_moins"] is True
      and par["déplace"]["elle_bat_le_temoin"] is False,
      f"{par['déplace']['arrets_de_la_pince']} arrêts contre "
      f"{ver['le_temoin']['arrets_de_la_pince']}")
    v("⚠⚠ un rejet annoncé qui n'écarterait rien serait la marche d'avant, déguisée",
      par["ajoute"]["le_rejet_sexerce"] is True
      and par["déplace"]["le_rejet_sexerce"] is None
      and ver["tous_les_rejets_sexercent"] is True)
    muet = [_case_factice("dure", "muet", False, True,
                          [_suivi(0, True), _suivi(90, True), _suivi(180, True), _suivi(270, True)])]
    g2 = {**g, "variantes": [g["variantes"][0], {"nom": "muet", "en_croix": False,
                                                 "rejeter": True}],
          "cases": temoin + muet}
    v("⚠⚠ ... et le contrôle mord : une variante qui rejette sans jamais rien écarter est signalée",
      juger(g2, None)["le_verdict"]["tous_les_rejets_sexercent"] is False)
    v("⚠ le prix est publié en lectures médianes, rapporté au témoin",
      ver["le_prix_de_la_meilleure"] is not None and ver["le_prix_de_la_meilleure"] > 0.0)

    print("\n— où le gain vit, bruit par bruit —")
    # Deux niveaux de bruit : au premier l'instrument gagne sans perdre, au second il gagne ET
    # perd, au troisième il ne bouge rien. Un seul des trois est une victoire JOINTE.
    def bruite(c, b):
        return {**c, "bruit": float(b)}

    t2 = [bruite(_case_factice("dure", "témoin", False, False,
                               [_suivi(0, True), _suivi(90, False, arrete=True),
                                _suivi(180, False, arrete=True), _suivi(270, True)]), b)
          for b in (0.0, 7.0, 9.0)]
    a2 = [bruite(_case_factice("dure", "mixte", False, True,
                               [_suivi(0, True), _suivi(90, True, rejetes=2),
                                _suivi(180, False, arrete=True), _suivi(270, True)]), 0.0),
          bruite(_case_factice("dure", "mixte", False, True,
                               [_suivi(0, False, arrete=True), _suivi(90, True, rejetes=2),
                                _suivi(180, True), _suivi(270, True)]), 7.0),
          bruite(_case_factice("dure", "mixte", False, True,
                               [_suivi(0, True), _suivi(90, False, arrete=True),
                                _suivi(180, False, arrete=True), _suivi(270, True, rejetes=1)]),
                 9.0)]
    g3 = {"departs": 4, "tours": 1.0, "fenetre": FENETRE, "bruits": [0.0, 7.0, 9.0],
          "variantes": [{"nom": "témoin", "en_croix": False, "rejeter": False},
                        {"nom": "mixte", "en_croix": False, "rejeter": True}],
          "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": t2 + a2}
    j3 = juger(g3, None)
    lignes = {x["bruit"]: x["par_instrument"][0] for x in j3["le_gain_par_bruit"]["par_bruit"]}
    # ⚠⚠ L'ATTENDU SE DÉRIVE DES FIXTURES, IL NE S'ÉCRIT PAS À LA MAIN. Vérifié à mes dépens :
    # ma première version comptait « +1/−1 » au bruit 7 là où la fixture dit +2/−1, et c'est
    # l'attendu qui avait tort. Un nombre recopié d'un comptage mental n'est pas un attendu.
    def attendu(b):
        t_ = next(c for c in t2 if abs(c["bruit"] - b) < 1e-12)
        a_ = next(c for c in a2 if abs(c["bruit"] - b) < 1e-12)
        avant_ = {x["depart_deg"]: une_reussite(x) for x in t_["bras"]["la pince"]["suivis"]}
        apres_ = {x["depart_deg"]: une_reussite(x) for x in a_["bras"]["la pince"]["suivis"]}
        gag = sum(1 for k in avant_ if apres_[k] and not avant_[k])
        per = sum(1 for k in avant_ if avant_[k] and not apres_[k])
        return gag, per

    v("⭐⭐⭐ le gain est apparié À CHAQUE bruit — gagner ici et perdre là ne se compense pas",
      all((lignes[b]["gains"], lignes[b]["pertes"]) == attendu(b) for b in (0.0, 7.0, 9.0))
      and attendu(0.0)[1] == 0 and attendu(7.0)[1] > 0,
      " · ".join(f"bruit {b:g} {lignes[b]['gains']:+d}/{-lignes[b]['pertes']:+d}"
                 for b in (0.0, 7.0, 9.0)))
    joints = j3["le_verdict"]["par_instrument"][0]["bruits_ou_elle_gagne_jointement"]
    v("⭐⭐⭐⭐ ... et seul le bruit qui gagne SANS PERDRE est une victoire jointe",
      joints == [0.0], f"{joints}")
    v("⚠⚠ ... « elle ne change rien » N'EST PAS « elle gagne » — le bruit muet est exclu",
      9.0 not in joints and lignes[9.0]["arrets"] == lignes[9.0]["arrets_du_temoin"])

    print("\n— le témoin interne —")
    v("⚠ un record absent se DIT, il ne se devine pas",
      j["le_temoin_interne"]["decidable"] is False)
    faux = {"sur_la_grille": {"cases": [
        {**temoin[0], "variante": LE_TEMOIN_DE_147,
         "bras": {b: {"suivis": [_suivi(0, True)],
                      **_resumer_un_bras([_suivi(0, True)], 1)} for b in BRAS}}]}}
    t = juger(g, faux)["le_temoin_interne"]
    v("⭐⭐⭐ ... et un témoin qui NE se reproduit PAS est signalé",
      t["decidable"] is True and t["le_protocole_est_le_meme"] is False,
      f"{t['par_bras']['la pince']['ici']} ici contre "
      f"{t['par_bras']['la pince']['dans_147']} dans `147`")
    vrai = {"sur_la_grille": {"cases": [{**temoin[0], "variante": LE_TEMOIN_DE_147}]}}
    t2 = juger(g, vrai)["le_temoin_interne"]
    v("⭐⭐ ... et un témoin qui se reproduit passe, arrêts compris",
      t2["le_protocole_est_le_meme"] is True
      and t2["arrets_ici"] == t2["arrets_dans_147"] == 2)
    # ⚠⚠⚠ ET LE CONTRÔLE DES ARRÊTS DOIT MORDRE SÉPARÉMENT. Un record qui rendrait les mêmes
    # réussites en s'arrêtant un nombre de fois différent N'EST PAS le même protocole, et vérifié
    # en cassant le code : sans ce cas, retirer la comparaison des arrêts laisse la batterie verte.
    suivis_boiteux = [_suivi(0, True), _suivi(90, True), _suivi(180, False, arrete=True),
                      _suivi(270, False, arrete=False)]
    boiteux = {"sur_la_grille": {"cases": [
        {**temoin[0], "variante": LE_TEMOIN_DE_147,
         "bras": {b: {"suivis": suivis_boiteux,
                      **_resumer_un_bras(suivis_boiteux, 4)} for b in BRAS}}]}}
    t3 = juger(g, boiteux)["le_temoin_interne"]
    v("⭐⭐⭐ ... et mêmes réussites avec des arrêts différents N'EST PAS le même protocole",
      all(t3["par_bras"][n]["ici"] == t3["par_bras"][n]["dans_147"] for n in BRAS)
      and t3["arrets_ici"] != t3["arrets_dans_147"]
      and t3["le_protocole_est_le_meme"] is False,
      f"{t3['arrets_ici']} arrêts ici contre {t3['arrets_dans_147']}")

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    r = mesurer(matieres=(LA_MATIERE_DE_140,), bruits=(BRUIT,),
                variantes=(("témoin", False, False), ("la croix et le rejet", True, True)),
                departs=1, tours=TOURS_SONDE, precedent=Path("/introuvable.json"))
    v("⚠ `mesurer` rend la grille et dit qu'il n'a pas lu de précédent",
      r["juger"]["decidable"] and r["le_precedent"] is None)
    avant = json.loads(json.dumps(r["sur_la_grille"]["cases"][0]["bras"]["la pince"]["suivis"]))
    r2 = reagreger(json.loads(json.dumps(r)), precedent=Path("/introuvable.json"))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré",
      r2["sur_la_grille"]["cases"][0]["bras"]["la pince"]["suivis"] == avant,
      "il relit le verdict, il ne remarche pas")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "sur_la_grille": g})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le tableau, l'appariement, l'arrêt et le prix",
      "instrument" in sortie and "gagnées" in sortie and "elle arrête moins" in sortie
      and "le prix" in sortie, f"{len(sortie)} caractères")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "précédent absent"})
    v("⚠ un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else '⛔ ÉCHEC'} ({echecs} failures, {controles} checks)")
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
