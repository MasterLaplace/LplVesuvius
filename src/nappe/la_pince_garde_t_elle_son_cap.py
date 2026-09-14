#!/usr/bin/env python3
"""Une pince qui garde son CAP passe-t-elle la ou aucune ne passe ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET POURQUOI C'EST LA MESURE QUI LE NOMME. Le depot tient deux
instruments qui ne se remplacent pas. `139` mesure que le CAP recupere **73 %** de l'obliquite d'un
froissement et `140` qu'il enleve ce qui ALTERNE, pas ce qui PERSISTE. `142` mesure l'inverse pour la
PINCE : elle tient contre l'ecrasement — la cause qui persiste — et elle PERD sur les matieres
froissees, parce qu'elle exige de voir ses deux interstices et qu'un froissement assez raide lui en
cache un. Et aucun des deux ne passe seul la matiere que `140` retient. La question suivante n'est
donc pas « lequel », c'est leur COMPOSITION.

⭐⭐⭐ LE CAP AGIT SUR LA NORMALE, ET IL NE PEUT PAS AGIR AILLEURS. Dans le plan du tour, la
direction perpendiculaire a la normale est UNIQUE au signe pres : une memoire posee sur la tangente
serait reprojetee sur la normale courante et n'aurait aucun effet. Ce qu'un cap peut retenir est
l'ORIENTATION — ce qui est aussi ce que fait le rouleau physique dont vient l'idee : il a de
l'inertie, il ne colle pas a chaque ondulation.

⚠⚠ LA MEMOIRE EST BALAYEE, JAMAIS POSEE. `137` a marche a 0,75 ; recopier ce nombre ici serait
choisir le reglage d'une autre mesure parce qu'il etait la. Le balayage porte de 0 (le suiveur de
`142`, au bit) a 0,9, et c'est la pente qu'on regarde.

⚠⚠ ET LA QUESTION QUI DECIDE VRAIMENT EST CELLE D'UN REGLAGE UNIQUE. Un derouleur ne peut pas
choisir sa memoire feuille par feuille : il lui faut UNE valeur. On mesure donc si la meilleure
memoire GLOBALE fait aussi bien que la meilleure memoire de chaque case — et si elle ne le fait pas,
alors l'instrument doit savoir quelle cause domine, ce que `140` rend lisible depuis l'ecrasement.

⚠ La barre a franchir est nommee d'avance : sur la matiere que `140` retient — ecrasee ET froissee a
100 µm, dont le froissement incline la normale de **57,94°** — AUCUN bras ne boucle un tour a memoire
nulle. Si un cap ne change pas ca, il faut le dire.

Usage :
    uv run python src/nappe/la_pince_garde_t_elle_son_cap.py --verifier
    uv run python src/nappe/la_pince_garde_t_elle_son_cap.py \\
        --json docs/mesures/la_pince_garde_t_elle_son_cap.json
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

from la_pince_tient_elle_la_feuille import (BRAS, LARGEUR_DE_REFERENCE,  # noqa: E402
                                            MATIERES, _resumer_un_bras, une_case)

# ⚠ De 0 — le suiveur de `142` exactement — a 0,9. Balayee, jamais posee.
MEMOIRES = (0.0, 0.25, 0.5, 0.75, 0.9)
# ⚠ Les deux bouts du balayage de `142` plus son milieu : ce fichier balaie la MEMOIRE, et `142`
# publie deja le balayage complet du bruit a memoire nulle.
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, memoires=MEMOIRES, departs: int = DEPARTS,
                  tours: float = TOURS) -> dict:
    """Chaque matiere, chaque bruit, chaque memoire — les trois bras a chaque fois.

    ⚠ Les trois bras sont gardes a toutes les memoires, et pas seulement la pince. Sans eux on ne
    pourrait pas dire si le cap sauve la PINCE ou s'il sauve n'importe quel suiveur — auquel cas la
    pince n'ajouterait rien.
    """
    cases = [une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours, memoire_du_cap=mem)
             for m in matieres for b in bruits for mem in memoires]
    return {"departs": int(departs), "tours": float(tours),
            "bruits": [float(b) for b in bruits], "memoires": [float(m) for m in memoires],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _couple(bras: dict) -> tuple[int, int]:
    """Ce qui ordonne un bras : les REUSSITES d'abord, la bonne feuille ensuite.

    ⭐⭐⭐ UNE REUSSITE EST JOINTE : boucler le tour ET revenir sur la meme feuille. Ma premiere
    version comptait les deux separement, et la mesure a montre ce que ca laisse passer — la barre
    de `140` a ete declaree franchie par une marche qui bouclait son tour en revenant sur une AUTRE
    feuille, une seule bonne feuille sur douze. Un controle satisfait par autre chose que ce qu'il
    demande ne controle rien.

    ⚠ Le compte joint est aussi la garde anti-tautologie : un bras qui refuse tout n'a aucune
    reussite, puisqu'il ne boucle rien. La bonne feuille departage ensuite, parce qu'un suiveur qui
    tient sa feuille sans finir son tour vaut mieux qu'un qui la perd.
    """
    return (int(bras.get("reussites") or 0), int(bras.get("memes_feuilles") or 0))


def la_meilleure_memoire(grille: dict) -> dict:
    """Pour chaque matiere et chaque bruit, la memoire qui sert le mieux chaque bras."""
    par_cle: dict = {}
    for c in grille["cases"]:
        cle = (c["ecrasement"], c["amplitude_um"], c["bruit"])
        par_cle.setdefault(cle, []).append(c)
    out = []
    for (ecr, amp, bruit), cases in sorted(par_cle.items()):
        cases = sorted(cases, key=lambda c: c["memoire_du_cap"])
        bloc = {"ecrasement": ecr, "amplitude_um": amp, "bruit": bruit,
                "nom": cases[0]["nom"], "departs": cases[0]["departs"]}
        for nom in BRAS:
            # ⚠ A egalite de couple, la PLUS PETITE memoire gagne : un cap qui n'apporte rien ne
            # doit pas etre credite de ce que la matiere donnait deja.
            meilleure = max(cases, key=lambda c: (*_couple(c["bras"][nom]),
                                                  -c["memoire_du_cap"]))
            sans = cases[0]
            bloc[nom] = {
                "memoire": meilleure["memoire_du_cap"],
                "reussites": meilleure["bras"][nom].get("reussites"),
                "memes_feuilles": meilleure["bras"][nom].get("memes_feuilles"),
                "tours_boucles": meilleure["bras"][nom].get("tours_boucles"),
                "sans_cap_reussites": sans["bras"][nom].get("reussites"),
                "sans_cap_memes_feuilles": sans["bras"][nom].get("memes_feuilles"),
                "sans_cap_tours_boucles": sans["bras"][nom].get("tours_boucles"),
                "le_cap_sert": bool(_couple(meilleure["bras"][nom])
                                    > _couple(sans["bras"][nom]))}
        out.append(bloc)
    return {"par_case": out}


def un_reglage_unique(grille: dict) -> dict:
    """Existe-t-il UNE memoire qui vaut la meilleure de chaque case ?

    ⭐⭐ C'EST LA QUESTION QUI DECIDE POUR LE GRAAL. Un derouleur ne regle pas sa memoire feuille
    par feuille : il lui faut une valeur, et elle doit tenir sur toute la matiere. On additionne donc
    les bonnes feuilles sur toutes les cases — chaque case pese le meme nombre de departs, donc la
    somme ne cache aucune ponderation — et on compare le meilleur reglage UNIQUE a la somme des
    meilleurs reglages case par case.

    ⚠ L'ecart entre les deux est ce qu'un reglage unique COUTE. S'il est nul, une valeur suffit ;
    s'il est grand, l'instrument doit savoir quelle cause domine, ce que `140` rend lisible.
    """
    par_mem: dict = {}
    for c in grille["cases"]:
        par_mem.setdefault(c["memoire_du_cap"], []).append(c)
    out = {"par_memoire": [], "cases": len(grille["cases"]) // max(len(par_mem), 1)}
    for mem, cases in sorted(par_mem.items()):
        ligne = {"memoire": mem, "cases": len(cases)}
        for nom in BRAS:
            ligne[nom] = {
                "reussites": int(sum(c["bras"][nom].get("reussites") or 0 for c in cases)),
                "memes_feuilles": int(sum(c["bras"][nom].get("memes_feuilles") or 0
                                          for c in cases)),
                "tours_boucles": int(sum(c["bras"][nom].get("tours_boucles") or 0
                                         for c in cases))}
        out["par_memoire"].append(ligne)
    meilleures = la_meilleure_memoire(grille)["par_case"]
    for nom in BRAS:
        if not out["par_memoire"]:
            continue
        unique = max(out["par_memoire"],
                     key=lambda x: (x[nom]["reussites"], x[nom]["memes_feuilles"], -x["memoire"]))
        parfait = sum(int(b[nom]["reussites"] or 0) for b in meilleures)
        out[nom] = {"memoire_unique": unique["memoire"],
                    "reussites": unique[nom]["reussites"],
                    "memes_feuilles": unique[nom]["memes_feuilles"],
                    "tours_boucles": unique[nom]["tours_boucles"],
                    "reussites_au_mieux_par_case": parfait,
                    "ce_que_coute_un_reglage_unique": parfait - unique[nom]["reussites"]}
    return out


def la_barre(grille: dict, ecrasement: float = 0.2782, amplitude_um: float = 100.0) -> dict:
    """La matiere que `140` retient : un cap y fait-il boucler un tour a quelqu'un ?

    ⚠ La barre est nommee AVANT la mesure et elle est binaire : a memoire nulle, aucun bras ne
    boucle un tour sur cette matiere. Un cap qui ne change pas ca doit le dire.
    """
    cases = [c for c in grille["cases"]
             if c["ecrasement"] == ecrasement and c["amplitude_um"] == amplitude_um]
    if not cases:
        return {"decidable": False, "raison": "la matière de `140` n'est pas dans la grille"}
    reussites = max((int(c["bras"][n].get("reussites") or 0) for c in cases for n in BRAS),
                    default=0)
    meilleur = max(cases, key=lambda c: max(int(c["bras"][n].get("reussites") or 0)
                                            for n in BRAS))
    bras = max(BRAS, key=lambda n: int(meilleur["bras"][n].get("reussites") or 0))
    return {"decidable": True, "ecrasement": ecrasement, "amplitude_um": amplitude_um,
            "cases": len(cases), "departs": cases[0]["departs"],
            "reussites_au_mieux": reussites,
            "memoire_du_mieux": meilleur["memoire_du_cap"],
            # ⚠ QUEL bras franchit compte autant que le fait qu'un bras franchisse : si c'est une
            # seule machoire, la composition n'a rien demontre.
            "bras_du_mieux": bras,
            "la_barre_est_franchie": bool(reussites > 0),
            "tours_boucles_au_mieux": max(
                (int(c["bras"][n].get("tours_boucles") or 0) for c in cases for n in BRAS),
                default=0),
            "memes_feuilles_au_mieux": max(
                (int(c["bras"][n].get("memes_feuilles") or 0) for c in cases for n in BRAS),
                default=0)}


def la_contrainte_tire_t_elle(grille: dict) -> dict:
    """Le refus tire-t-il encore quand le cap monte, ou devient-il inerte ?

    ⭐⭐⭐⭐ C'EST LA QUESTION QUI CORRIGE MA PROPRE PREDICTION. J'attendais que le cap et la
    contrainte se COMPLETENT — l'un contre ce qui alterne, l'autre contre ce qui persiste. La mesure
    dit qu'ils se REMPLACENT : un cap assez fort empeche la situation meme que le refus existe pour
    attraper, donc le refus cesse de tirer et les deux bras marchent a l'identique.

    ⚠ « A l'identique » se mesure sur les SUIVIS pas a pas, pas sur les comptes : deux bras peuvent
    rendre les memes totaux par des chemins differents. Le seul champ ecarte est `saut_median_um`,
    que la pince publie et que le bras libre ne calcule jamais — comparer un champ qu'un seul des
    deux produit dirait qu'ils different alors qu'ils ont marche pareil.
    """
    par_mem: dict = {}
    for c in grille.get("cases", []):
        par_mem.setdefault(c["memoire_du_cap"], []).append(c)

    def sans_saut(xs):
        return [{k: v for k, v in x.items() if k != "saut_median_um"} for x in xs]

    out = []
    for mem, cases in sorted(par_mem.items()):
        # ⚠ Une case sans suivis rangés ne se juge pas sur les refus : elle est SAUTEE et comptee,
        # jamais lue comme « zero refus ». Un compte qui vaudrait zero faute de donnee serait un
        # controle incapable d'echouer.
        lisibles = [c for c in cases if "suivis" in c["bras"]["la pince"]
                    and "suivis" in c["bras"]["deux machoires libres"]]
        refus = sum(int(x.get("refus") or 0) for c in lisibles
                    for x in c["bras"]["la pince"]["suivis"] if x.get("decidable"))
        memes = sum(1 for c in lisibles
                    if sans_saut(c["bras"]["la pince"]["suivis"])
                    == sans_saut(c["bras"]["deux machoires libres"]["suivis"]))
        out.append({"memoire": mem, "cases": len(lisibles),
                    "cases_sans_suivis": len(cases) - len(lisibles), "refus": int(refus),
                    "cases_marchees_a_lidentique": int(memes)})
    inertes = [x["memoire"] for x in out if x["refus"] == 0 and x["cases"] > 0]
    return {"par_memoire": out,
            "memoire_ou_la_contrainte_devient_inerte": min(inertes) if inertes else None,
            "refus_sans_cap": out[0]["refus"] if out else None}


def juger(grille: dict) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    par_case = la_meilleure_memoire(grille)["par_case"]
    unique = un_reglage_unique(grille)
    out = {"decidable": True, "par_case": par_case, "un_reglage_unique": unique,
           "la_contrainte_tire_t_elle": la_contrainte_tire_t_elle(grille),
           "la_barre": la_barre(grille)}
    # ⚠ « Le cap sert » se compte par BRAS : s'il sert autant a une machoire qu'a la pince, la
    # pince n'ajoute rien et il faut le lire.
    for nom in BRAS:
        out[f"cases_ou_le_cap_sert_{nom}"] = sum(1 for b in par_case if b[nom]["le_cap_sert"])
    # ⚠ La case de tete est DERIVEE : celle ou le cap change le plus le couple de la pince.
    avec = [(b, (b["la pince"]["reussites"] - b["la pince"]["sans_cap_reussites"],
                 b["la pince"]["memes_feuilles"] - b["la pince"]["sans_cap_memes_feuilles"]))
            for b in par_case]
    if avec:
        tete = max(avec, key=lambda x: (x[1][0], x[1][1]))
        out["la_case_ou_le_cap_change_le_plus"] = {
            **tete[0]["la pince"], "nom": tete[0]["nom"], "bruit": tete[0]["bruit"],
            "ecrasement": tete[0]["ecrasement"], "amplitude_um": tete[0]["amplitude_um"],
            "departs": tete[0]["departs"],
            "reussites_gagnees": tete[1][0], "feuilles_gagnees": tete[1][1]}
    return out


def mesurer(matieres=MATIERES, bruits=BRUITS, memoires=MEMOIRES, departs: int = DEPARTS,
            tours: float = TOURS) -> dict:
    grille = sur_la_grille(matieres, bruits, memoires, departs, tours)
    return {"sur_la_grille": grille, "juger": juger(grille)}


def reagreger(r: dict) -> dict:
    """Recalcule les resumes et le verdict depuis les suivis ranges — sans remarcher."""
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    r["juger"] = juger(r["sur_la_grille"])
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    g = r["sur_la_grille"]
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    print(f"la mémoire du cap, balayée de {min(g['memoires']):g} à {max(g['memoires']):g} — "
          f"un tour, {g['departs']} départs par case.")
    print("une RÉUSSITE est jointe : boucler le tour ET revenir sur la même feuille. "
          "« sans cap → au mieux » :")
    print(f"   {'matière':>28} {'bruit':>6} | {'mém.':>5} | {'une mâchoire':>14} | "
          f"{'deux libres':>14} | {'la pince':>14}")
    for b in j["par_case"]:
        ligne = f"   {b['nom'].replace('spirale ', ''):>28} {b['bruit']:>6g} |"
        ligne += f" {b['la pince']['memoire']:>5.2f} |"
        for nom in BRAS:
            x = b[nom]
            marque = "★" if x["le_cap_sert"] else " "
            ligne += (f" {x['sans_cap_reussites']:>2d}→{x['reussites']:>2d}r "
                      f"{x['sans_cap_memes_feuilles']:>2d}→{x['memes_feuilles']:>2d}f{marque}|")
        print(ligne.rstrip("|"))
    print(f"\n   le cap sert dans : " + " · ".join(
        f"{nom} {j[f'cases_ou_le_cap_sert_{nom}']}/{len(j['par_case'])}" for nom in BRAS))
    u = j["un_reglage_unique"]
    print(f"\n   un réglage UNIQUE, sur les {len(j['par_case'])} cases "
          f"({u['cases']} départs par mémoire) :")
    for nom in BRAS:
        x = u.get(nom)
        if x is None:
            continue
        print(f"     {nom:>22} : mémoire {x['memoire_unique']:.2f} → "
              f"{x['reussites']} réussites ({x['memes_feuilles']} bonnes feuilles, "
              f"{x['tours_boucles']} tours) ; au mieux case par case "
              f"{x['reussites_au_mieux_par_case']}, donc un réglage unique coûte "
              f"{x['ce_que_coute_un_reglage_unique']}")
    ct = j.get("la_contrainte_tire_t_elle", {})
    if ct.get("par_memoire"):
        print(f"\n   la contrainte tire-t-elle encore ? (refus de la pince, et cases où elle "
              f"marche exactement comme un bras LIBRE)")
        for x in ct["par_memoire"]:
            print(f"     mémoire {x['memoire']:>5.2f} : {x['refus']:>4d} refus · "
                  f"{x['cases_marchees_a_lidentique']:>2d}/{x['cases']} cases à l'identique")
        if ct.get("memoire_ou_la_contrainte_devient_inerte") is not None:
            print(f"     ★★★★ la contrainte devient INERTE à partir de "
                  f"{ct['memoire_ou_la_contrainte_devient_inerte']:.2f} : le cap empêche la "
                  f"situation même que le refus existe pour attraper")
    print(f"\n   la pente de la mémoire, pour la pince :")
    for x in u["par_memoire"]:
        print(f"     {x['memoire']:>5.2f} : {x['la pince']['reussites']:>3d} réussites, "
              f"{x['la pince']['memes_feuilles']:>3d} bonnes feuilles, "
              f"{x['la pince']['tours_boucles']:>3d} tours")
    t = j.get("la_case_ou_le_cap_change_le_plus")
    if t is not None:
        print(f"\n★★★★ là où le cap change le plus la pince — {t['nom']}, bruit {t['bruit']:g} :")
        print(f"     sans cap {t['sans_cap_reussites']}/{t['departs']} réussites "
              f"({t['sans_cap_memes_feuilles']} bonnes feuilles) ; à mémoire {t['memoire']:.2f}, "
              f"{t['reussites']}/{t['departs']} ({t['memes_feuilles']} feuilles) — "
              f"+{t['reussites_gagnees']} réussites")
    b_ = j["la_barre"]
    if b_.get("decidable"):
        marque = "★★★★" if b_["la_barre_est_franchie"] else "✗"
        print(f"\n{marque} la barre de `140` (écrasée et froissée {b_['amplitude_um']:g} µm) est "
              f"franchie : {b_['la_barre_est_franchie']} — au mieux "
              f"{b_['reussites_au_mieux']} réussite(s) sur {b_['departs']} "
              f"(par « {b_['bras_du_mieux']} », à mémoire {b_['memoire_du_mieux']:.2f}) ; "
              f"{b_['tours_boucles_au_mieux']} tours bouclés et "
              f"{b_['memes_feuilles_au_mieux']} bonnes feuilles au mieux, mais jamais ensemble")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- ⭐⭐ une mémoire NULLE rend exactement le suiveur de `142`
    sans = une_case((0.2782, 0.0), 8.0, LARGEUR_DE_REFERENCE, departs=2, tours=0.1)
    nul = une_case((0.2782, 0.0), 8.0, LARGEUR_DE_REFERENCE, departs=2, tours=0.1,
                   memoire_du_cap=0.0)
    v("⭐⭐ une mémoire NULLE rend exactement le suiveur de `142`, au bit",
      all(sans["bras"][n]["suivis"] == nul["bras"][n]["suivis"] for n in BRAS),
      "le chemin du mélange n'est pris que si la mémoire est non nulle")
    avec = une_case((0.2782, 0.0), 8.0, LARGEUR_DE_REFERENCE, departs=2, tours=0.1,
                    memoire_du_cap=0.9)
    v("... et une mémoire non nulle change bien quelque chose",
      any(avec["bras"][n]["suivis"] != nul["bras"][n]["suivis"] for n in BRAS))
    v("la mémoire voyage jusque dans la case", avec["memoire_du_cap"] == 0.9)

    # ---- ⭐ une mémoire de UN fige l'orientation, donc le suiveur ne tourne plus
    fige = une_case((0.0, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.25,
                    memoire_du_cap=1.0)
    libre = une_case((0.0, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.25,
                     memoire_du_cap=0.0)
    v("⭐ une mémoire de UN fige l'orientation : sur une spirale NUE le suiveur cesse de suivre",
      fige["bras"]["la pince"].get("tours_boucles", 0)
      < libre["bras"]["la pince"].get("tours_boucles", 0),
      "c'est la borne haute du balayage, et elle doit coûter")

    # ---- le couple qui ordonne
    v("⭐⭐ le couple met les RÉUSSITES avant tout le reste",
      _couple({"reussites": 5, "memes_feuilles": 5})
      > _couple({"reussites": 4, "memes_feuilles": 12}))
    v("... et la bonne feuille départage à égalité de réussites",
      _couple({"reussites": 5, "memes_feuilles": 9})
      > _couple({"reussites": 5, "memes_feuilles": 8}))
    v("⭐⭐ un bras qui boucle son tour sur la MAUVAISE feuille ne réussit rien",
      _couple({"reussites": 0, "memes_feuilles": 1, "tours_boucles": 12})
      < _couple({"reussites": 1, "memes_feuilles": 1, "tours_boucles": 1}),
      "c'est le défaut que la mesure a révélé dans ma première barre")
    v("un bras vide rend un couple nul", _couple({}) == (0, 0))

    # ---- la meilleure mémoire, sur une grille fabriquée
    def case(mem, m1, t1, m3, t3, ecr=0.0, amp=0.0, bruit=0.0, r1=None, r3=None):
        # ⚠ Une réussite ne peut pas dépasser le nombre de tours bouclés ni de bonnes feuilles :
        # les fixtures du test respectent la contrainte plutôt que d'inventer des comptes.
        def bras(m, t, r):
            return {"memes_feuilles": m, "tours_boucles": t,
                    "reussites": min(m, t) if r is None else r}
        return {"ecrasement": ecr, "amplitude_um": amp, "bruit": bruit, "nom": "x",
                "departs": 12, "memoire_du_cap": mem,
                "bras": {"une machoire": bras(m1, t1, r1),
                         "deux machoires libres": bras(m1, t1, r1),
                         "la pince": bras(m3, t3, r3)}}

    g = {"cases": [case(0.0, 4, 4, 2, 0), case(0.5, 4, 4, 9, 6), case(0.9, 4, 4, 9, 6)]}
    b = la_meilleure_memoire(g)["par_case"][0]
    v("la meilleure mémoire d'un bras est celle de son meilleur couple",
      b["la pince"]["memoire"] == 0.5, f"{b['la pince']['memoire']}")
    # ⚠ Ma première version répétait mot pour mot l'assertion précédente, donc elle ne testait
    # rien de plus. Celle-ci vérifie que l'égalité EXISTE avant de vérifier qui la gagne.
    egales = [c for c in g["cases"] if _couple(c["bras"]["la pince"]) == (6, 9)]
    v("⭐ ... et à égalité de couple c'est la PLUS PETITE mémoire qui gagne",
      len(egales) == 2 and b["la pince"]["memoire"] == min(c["memoire_du_cap"] for c in egales),
      f"{len(egales)} mémoires à égalité, retenue {b['la pince']['memoire']} — un cap qui "
      f"n'apporte rien ne doit pas être crédité de ce que la matière donnait déjà")
    v("« le cap sert » compare bien au sans-cap",
      b["la pince"]["le_cap_sert"] is True and b["une machoire"]["le_cap_sert"] is False)

    # ---- ⭐⭐ ce que coûte un réglage unique
    g2 = {"cases": [case(0.0, 0, 0, 9, 9, amp=1.0), case(0.9, 0, 0, 2, 2, amp=1.0),
                    case(0.0, 0, 0, 2, 2, amp=2.0), case(0.9, 0, 0, 9, 9, amp=2.0)]}
    u = un_reglage_unique(g2)
    v("⭐⭐ un réglage unique coûte quand l'optimum change d'une matière à l'autre",
      u["la pince"]["ce_que_coute_un_reglage_unique"] == 7,
      f"au mieux par case {u['la pince']['reussites_au_mieux_par_case']}, "
      f"unique {u['la pince']['reussites']}")
    g3 = {"cases": [case(0.0, 0, 0, 2, 2, amp=1.0), case(0.9, 0, 0, 9, 9, amp=1.0),
                    case(0.0, 0, 0, 2, 2, amp=2.0), case(0.9, 0, 0, 9, 9, amp=2.0)]}
    v("... et il ne coûte rien quand l'optimum est le même partout",
      un_reglage_unique(g3)["la pince"]["ce_que_coute_un_reglage_unique"] == 0)

    # ---- la barre, et elle est binaire
    g4 = {"cases": [case(0.0, 0, 0, 3, 0, ecr=0.2782, amp=100.0),
                    case(0.9, 0, 0, 4, 0, ecr=0.2782, amp=100.0)]}
    bb = la_barre(g4)
    v("la barre de `140` n'est pas franchie quand personne ne boucle",
      bb["decidable"] and bb["la_barre_est_franchie"] is False
      and bb["reussites_au_mieux"] == 0)
    # ⚠⚠ LA SONDE QUI COMPTE : un bras qui boucle son tour en revenant sur une AUTRE feuille ne
    # franchit rien. C'est exactement ce que ma première barre acceptait.
    g4b = {"cases": [case(0.0, 1, 12, 0, 0, ecr=0.2782, amp=100.0, r1=0)]}
    v("⭐⭐ ... ni quand un bras boucle en revenant sur la MAUVAISE feuille",
      la_barre(g4b)["la_barre_est_franchie"] is False
      and la_barre(g4b)["tours_boucles_au_mieux"] == 12,
      "douze tours bouclés, aucune réussite")
    g5 = {"cases": [case(0.0, 0, 0, 3, 0, ecr=0.2782, amp=100.0),
                    case(0.9, 0, 0, 4, 2, ecr=0.2782, amp=100.0)]}
    v("... et elle l'est dès qu'un bras boucle SUR SA FEUILLE, à la mémoire qui le fait",
      la_barre(g5)["la_barre_est_franchie"] is True
      and la_barre(g5)["memoire_du_mieux"] == 0.9
      and la_barre(g5)["bras_du_mieux"] == "la pince")
    v("une grille sans la matière de `140` est indécidable, jamais devinée",
      not la_barre({"cases": [case(0.0, 4, 4, 4, 4)]})["decidable"])

    # ---- le jugement
    v("un jugement sans case est indécidable", not juger({"cases": []})["decidable"])
    jg = juger(g2)
    v("la case de tête est celle où le cap change le plus la pince",
      jg["la_case_ou_le_cap_change_le_plus"]["reussites_gagnees"] == 7,
      f"{jg['la_case_ou_le_cap_change_le_plus']['reussites_gagnees']}")
    v("⭐ le cap est compté par BRAS, pas globalement",
      jg["cases_ou_le_cap_sert_une machoire"] == 0
      and jg["cases_ou_le_cap_sert_la pince"] == 1,
      "s'il servait autant à une mâchoire qu'à la pince, la pince n'ajouterait rien")

    # ---- rejouer depuis les suivis rangés
    petit = {"sur_la_grille": {"cases": [avec], "departs": 2, "tours": 0.1,
                               "bruits": [8.0], "memoires": [0.9], "largeur_en_pas": 0.25}}
    petit["juger"] = juger(petit["sur_la_grille"])
    refait = reagreger(json.loads(json.dumps(petit)))
    v("⭐ réagréger depuis les suivis rangés rend le MÊME verdict, sans remarcher",
      refait["juger"] == petit["juger"])

    # ---- ⭐⭐ la contrainte devient-elle inerte ?
    def suivi(refus, marque=0.0):
        return {"decidable": True, "refus": refus, "derive_en_feuilles": marque,
                "tour_boucle": True, "saut_median_um": 1.0}

    def duo(refus_pince, meme):
        c = case(0.0, 12, 12, 12, 12)
        c["bras"]["la pince"]["suivis"] = [suivi(refus_pince)]
        c["bras"]["deux machoires libres"]["suivis"] = [
            {**suivi(0, 0.0 if meme else 9.9), "saut_median_um": None}]
        return c

    ct = la_contrainte_tire_t_elle({"cases": [duo(7, False)]})
    v("le refus de la pince est compté", ct["par_memoire"][0]["refus"] == 7)
    v("... et une case où les deux bras diffèrent n'est pas dite identique",
      ct["par_memoire"][0]["cases_marchees_a_lidentique"] == 0)
    ct2 = la_contrainte_tire_t_elle({"cases": [duo(0, True)]})
    v("⭐⭐ sans refus et à suivi égal, les deux bras sont dits marcher à l'identique",
      ct2["par_memoire"][0]["cases_marchees_a_lidentique"] == 1,
      "le champ que seule la pince publie est écarté de la comparaison")
    v("... et la mémoire où la contrainte devient inerte est la PLUS PETITE sans refus",
      la_contrainte_tire_t_elle({"cases": [
          {**duo(3, False), "memoire_du_cap": 0.0},
          {**duo(0, True), "memoire_du_cap": 0.5},
          {**duo(0, True), "memoire_du_cap": 0.9}]})
      ["memoire_ou_la_contrainte_devient_inerte"] == 0.5)
    v("... et elle est indécidable si le refus tire partout",
      la_contrainte_tire_t_elle({"cases": [duo(1, False)]})
      ["memoire_ou_la_contrainte_devient_inerte"] is None)
    v("⭐ une case sans suivis rangés est SAUTÉE et comptée, jamais lue comme zéro refus",
      la_contrainte_tire_t_elle({"cases": [case(0.0, 12, 12, 12, 12)]})
      ["memoire_ou_la_contrainte_devient_inerte"] is None
      and la_contrainte_tire_t_elle({"cases": [case(0.0, 12, 12, 12, 12)]})
      ["par_memoire"][0]["cases_sans_suivis"] == 1)

    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "fixture injoignable"})
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
