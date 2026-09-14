#!/usr/bin/env python3
"""Un cap qui LIT la cause vaut-il mieux qu'un cap posé ?

⭐⭐⭐⭐ POURQUOI CE FICHIER. `143` mesure que le bon réglage de cap DÉPEND de la cause : sans cap la
pince gagne sur l'écrasement (10 réussites contre 1), avec cap une mâchoire gagne sur le froissement.
Un réglage unique existe — 0,75 — mais il coûte, et il ne franchit pas la barre de `140`. La question
suivante est donc si un suiveur peut LIRE, sur son propre chemin, laquelle des deux causes domine, et
régler sa mémoire lui-même.

⭐⭐⭐ LA RÈGLE EST UN ÉNONCÉ, PAS UN AJUSTEMENT, et c'est ce qui la rend réfutable. La normale d'un
suiveur tourne franchement quand la cause PERSISTE — un écrasement a une période d'un demi-tour — et
elle alterne quand la cause ALTERNE, un froissement se renversant en quelques pas. La cohérence des
incréments de rotation, `c = |somme| / somme des valeurs absolues`, sépare donc les deux, et la
mémoire vaut `m = 1 - c` : ce qui tourne franchement est lisible et le cap ne sert à rien, ce qui
alterne ne l'est pas et le cap doit tenir. Aucune constante n'y est réglée ; seule la LONGUEUR de la
fenêtre reste un paramètre, et elle est balayée.

⚠⚠ CE QUI REND LA MESURE CAPABLE D'ÉCHOUER, ET C'EST LE CŒUR DU FICHIER. Une règle adaptative qui
rendrait la MÊME mémoire sur toutes les matières serait un cap fixe déguisé — et elle passerait
inaperçue si l'on ne regardait que le score. On publie donc l'ÉCART entre les mémoires lues sur les
différentes matières, à bruit donné : c'est lui qui dit si la règle lit la cause ou autre chose.

⚠ Et le témoin est `143` lui-même : le meilleur réglage FIXE y est mesuré (100 réussites pour la
pince, 117 pour une mâchoire). Ce fichier ne le remarche pas, il le relit.

Usage :
    uv run python src/nappe/un_cap_qui_lit_la_cause.py --verifier
    uv run python src/nappe/un_cap_qui_lit_la_cause.py \\
        --json docs/mesures/un_cap_qui_lit_la_cause.json
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

# ⚠ Balayée, jamais posée : la fenêtre est le seul paramètre de la règle. ⚠⚠ Et le balayage va
# au-delà de son optimum : ma première version s'arrêtait à 32, qui se trouvait être la meilleure —
# un optimum au BORD d'un balayage n'est pas un optimum, c'est une borne du balayage.
FENETRES = (4, 8, 16, 32, 64, 128)
BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
LE_FIXE = RACINE / "docs" / "mesures" / "la_pince_garde_t_elle_son_cap.json"


def sur_la_grille(matieres=MATIERES, bruits=BRUITS, fenetres=FENETRES, departs: int = DEPARTS,
                  tours: float = TOURS) -> dict:
    """La même grille que `143`, mais avec une mémoire LUE au lieu de posée."""
    cases = [une_case(m, b, LARGEUR_DE_REFERENCE, departs, tours=tours, fenetre_du_cap=f)
             for m in matieres for b in bruits for f in fenetres]
    return {"departs": int(departs), "tours": float(tours),
            "bruits": [float(b) for b in bruits], "fenetres": [int(f) for f in fenetres],
            "largeur_en_pas": float(LARGEUR_DE_REFERENCE), "cases": cases}


def _memoires_lues(case: dict, bras: str = "la pince") -> list[float]:
    """Les mémoires que ce bras a réellement employées, une par départ."""
    return [s["memoire_mediane"] for s in case["bras"][bras].get("suivis", [])
            if s.get("decidable") and s.get("memoire_mediane") is not None]


def _memoire_lue(case: dict, bras: str = "la pince") -> float | None:
    """La mémoire médiane que ce bras a réellement employée sur cette case."""
    vals = _memoires_lues(case, bras)
    return round(float(np.median(vals)), 4) if vals else None


def le_discriminant(grille: dict, filtre=None, bras: str = "la pince") -> dict:
    """La règle lit-elle la CAUSE, ou autre chose ?

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE QUI REND LE FICHIER CAPABLE D'ÉCHOUER. Une règle qui rendrait la même
    mémoire partout serait un cap fixe déguisé, et son score seul ne le dirait pas. On publie donc,
    à bruit donné, l'ÉCART entre les mémoires lues sur les différentes matières : large, la règle
    sépare les causes ; nul, elle lit quelque chose qui ne dépend pas d'elles.

    ⚠ La comparaison se fait à RÉGLAGE FIXÉ, et c'est à quoi sert `filtre` : mélanger deux réglages
    ferait passer pour un écart entre matières ce qui est un écart entre réglages. Le filtre est un
    prédicat sur la case, pour que le même calcul serve à découper par fenêtre ici et par variante
    ailleurs — écrire deux fois « entre contre dans » serait deux réponses à une même question.
    """
    cases = [c for c in grille.get("cases", []) if filtre is None or filtre(c)]
    par_bruit: dict = {}
    for c in cases:
        par_bruit.setdefault(c["bruit"], []).append(c)
    out = []
    for bruit, cs in sorted(par_bruit.items()):
        lues = [(c["nom"], _memoire_lue(c, bras)) for c in cs]
        vals = [v for _n, v in lues if v is not None]
        if not vals:
            continue
        # ⚠⚠ LA COMPARAISON EST EXACTE ET SANS CONSTANTE : la lecture sépare les causes quand
        # l'écart ENTRE matières dépasse la dispersion DANS une matière. Ma première version
        # comparait l'écart à la moitié de lui-même sans bruit — un seuil choisi, c'est-à-dire le
        # péché nº 1 de ce dépôt.
        # ⚠⚠ LES DEUX CÔTÉS SONT ARRONDIS AVANT D'ÊTRE COMPARÉS. L'écart entre matières se calcule
        # sur des médianes arrondies à quatre décimales ; sans le même arrondi ici, une égalité se
        # tranchait par de la poussière flottante. Sur les vraies données le producteur arrondit
        # déjà des deux côtés, mais s'appuyer sur cette coïncidence est ce que ce dépôt proscrit.
        dedans = [float(np.max(m) - np.min(m)) for c in cs
                  if len(m := np.round(_memoires_lues(c, bras), 4)) > 1]
        entre = float(np.max(vals) - np.min(vals))
        dans = float(np.median(dedans)) if dedans else 0.0
        out.append({"bruit": bruit, "matieres": len(vals),
                    "memoire_la_plus_basse": round(float(np.min(vals)), 4),
                    "memoire_la_plus_haute": round(float(np.max(vals)), 4),
                    "ecart_entre_matieres": round(entre, 4),
                    "dispersion_dans_une_matiere": round(dans, 4),
                    "la_lecture_separe": bool(entre > dans),
                    "par_matiere": [{"nom": n, "memoire": v} for n, v in lues]})
    return {"bras": bras, "par_bruit": out}


def contre_le_fixe(grille: dict, fixe: dict | None) -> dict:
    """Le cap lu bat-il le meilleur cap POSÉ, que `143` a déjà mesuré ?

    ⚠ Le témoin n'est pas remarché : `143` publie le meilleur réglage fixe et son score. Le
    remarcher serait deux réponses à une même question.
    """
    par_f: dict = {}
    for c in grille.get("cases", []):
        par_f.setdefault(c["fenetre_du_cap"], []).append(c)
    out = {"par_fenetre": []}
    for f, cases in sorted(par_f.items()):
        ligne = {"fenetre": f, "cases": len(cases)}
        for nom in BRAS:
            ligne[nom] = {
                "reussites": int(sum(c["bras"][nom].get("reussites") or 0 for c in cases)),
                "memes_feuilles": int(sum(c["bras"][nom].get("memes_feuilles") or 0
                                          for c in cases)),
                "tours_boucles": int(sum(c["bras"][nom].get("tours_boucles") or 0
                                         for c in cases))}
        out["par_fenetre"].append(ligne)
    if not fixe:
        out["decidable"] = False
        out["raison"] = "la mesure de `143` est absente, il n'y a pas de témoin"
        return out
    ref = fixe.get("juger", {}).get("un_reglage_unique", {})
    out["decidable"] = True
    for nom in BRAS:
        r = ref.get(nom)
        if r is None or not out["par_fenetre"]:
            continue
        meilleur = max(out["par_fenetre"], key=lambda x: (x[nom]["reussites"], -x["fenetre"]))
        out[nom] = {"meilleure_fenetre": meilleur["fenetre"],
                    "reussites_lues": meilleur[nom]["reussites"],
                    "memoire_posee": r["memoire_unique"],
                    "reussites_posees": r["reussites"],
                    "le_cap_lu_fait_mieux": bool(meilleur[nom]["reussites"] > r["reussites"]),
                    "ecart": meilleur[nom]["reussites"] - r["reussites"]}
    return out


def juger(grille: dict, fixe: dict | None) -> dict:
    if not grille.get("cases"):
        return {"decidable": False, "raison": "aucune case à juger"}
    contre = contre_le_fixe(grille, fixe)
    disc = {int(f): le_discriminant(grille, lambda c, f=f: c["fenetre_du_cap"] == int(f))
            for f in grille["fenetres"]}
    out = {"decidable": True, "contre_le_fixe": contre,
           "le_discriminant": {str(f): d for f, d in disc.items()}}
    # ⭐⭐ Le fait qui décide : jusqu'à quel bruit la lecture sépare-t-elle encore les causes ? On
    # ne choisit PAS une fenêtre pour répondre — on publie la réponse pour toutes, et le résumé est
    # le bruit le plus fort qu'UNE fenêtre franchit, avec la plus courte qui y arrive.
    # ⚠ Ma première version retenait « la fenêtre qui sépare le mieux sans bruit », et elle rendait
    # une lecture pessimiste : celle qui sépare le mieux à bruit nul n'est pas celle qui résiste le
    # mieux au bruit. Choisir une fenêtre pour raconter est déjà un choix de trop.
    par_bruit: dict = {}
    for f, dd in disc.items():
        for x in dd["par_bruit"]:
            par_bruit.setdefault(x["bruit"], []).append((int(f), x))
    resume = []
    for bruit, lignes in sorted(par_bruit.items()):
        gagnantes = sorted(f for f, x in lignes if x["la_lecture_separe"])
        meilleur = max(lignes, key=lambda t: (t[1]["ecart_entre_matieres"]
                                              - t[1]["dispersion_dans_une_matiere"], -t[0]))
        resume.append({
            "bruit": bruit, "fenetres_ou_elle_separe": gagnantes,
            "elle_separe": bool(gagnantes),
            "meilleure_fenetre": meilleur[0],
            "ecart_entre_matieres": meilleur[1]["ecart_entre_matieres"],
            "dispersion_dans_une_matiere": meilleur[1]["dispersion_dans_une_matiere"],
            "memoire_la_plus_basse": meilleur[1]["memoire_la_plus_basse"],
            "memoire_la_plus_haute": meilleur[1]["memoire_la_plus_haute"],
            "par_matiere": meilleur[1]["par_matiere"]})
    franchis = [x["bruit"] for x in resume if x["elle_separe"]]
    out["la_lecture_survit_elle_au_bruit"] = {
        "par_bruit": resume,
        "bruits_ou_elle_separe": franchis,
        "le_bruit_le_plus_fort_ou_elle_separe": (max(franchis) if franchis else None),
        # ⚠ Le minimum porte sur les FENÊTRES, pas sur les listes de fenêtres : ma première
        # version comparait des listes entre elles et rendait `[4, 8]` là où la réponse est 4.
        "la_fenetre_qui_y_arrive": (min(f for x in resume if x["bruit"] == max(franchis)
                                        for f in x["fenetres_ou_elle_separe"])
                                    if franchis else None),
        "elle_separe_partout": bool(len(franchis) == len(resume)),
        "elle_separe_sans_bruit": bool(resume and resume[0]["elle_separe"])}
    return out


def mesurer(matieres=MATIERES, bruits=BRUITS, fenetres=FENETRES, departs: int = DEPARTS,
            tours: float = TOURS, fixe: Path = LE_FIXE) -> dict:
    grille = sur_la_grille(matieres, bruits, fenetres, departs, tours)
    ref = json.loads(Path(fixe).read_text()) if Path(fixe).exists() else None
    return {"sur_la_grille": grille, "le_temoin_fixe": str(Path(fixe).name) if ref else None,
            "juger": juger(grille, ref)}


def reagreger(r: dict, fixe: Path = LE_FIXE) -> dict:
    """Recalcule les résumés et le verdict depuis les suivis rangés — sans remarcher."""
    for c in r["sur_la_grille"]["cases"]:
        for nom in BRAS:
            suivis = c["bras"][nom]["suivis"]
            c["bras"][nom] = {"suivis": suivis, **_resumer_un_bras(suivis, int(c["departs"]))}
    ref = json.loads(Path(fixe).read_text()) if Path(fixe).exists() else None
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
    print(f"la mémoire LUE par la règle `m = 1 - cohérence des rotations`, fenêtre balayée de "
          f"{min(g['fenetres'])} à {max(g['fenetres'])} pas, {g['departs']} départs par case.")
    c = j["contre_le_fixe"]
    print(f"\n   contre le meilleur cap POSÉ que `143` mesure "
          f"({r.get('le_temoin_fixe') or 'témoin absent'}) :")
    if c.get("decidable"):
        for nom in BRAS:
            x = c.get(nom)
            if x is None:
                continue
            marque = "★" if x["le_cap_lu_fait_mieux"] else "✗"
            print(f"     {marque} {nom:>22} : lu {x['reussites_lues']} réussites "
                  f"(fenêtre {x['meilleure_fenetre']}) contre posé {x['reussites_posees']} "
                  f"(mémoire {x['memoire_posee']:.2f}) — écart {x['ecart']:+d}")
    else:
        print(f"     ⚠ {c.get('raison')}")
    print(f"\n   réussites par fenêtre, sur les {c['par_fenetre'][0]['cases']} cases :")
    for x in c["par_fenetre"]:
        print(f"     fenêtre {x['fenetre']:>3} : "
              + " · ".join(f"{NOMS.get(n, n)} {x[n]['reussites']:>3d}" for n in BRAS))
    s = j.get("la_lecture_survit_elle_au_bruit")
    if s is not None:
        print(f"\n   ⭐ la règle lit-elle la CAUSE ? (à chaque bruit, la fenêtre qui sépare le "
              f"mieux)")
        print(f"     {'bruit':>6} | {'fen.':>5} | {'mém. la plus basse':>19} | "
              f"{'la plus haute':>14} | {'écart entre':>12} | {'dispersion dans':>16} | sépare")
        for x in s["par_bruit"]:
            print(f"     {x['bruit']:>6g} | {x['meilleure_fenetre']:>5} | "
                  f"{x['memoire_la_plus_basse']:>19.4f} | {x['memoire_la_plus_haute']:>14.4f} | "
                  f"{x['ecart_entre_matieres']:>12.4f} | "
                  f"{x['dispersion_dans_une_matiere']:>16.4f} | "
                  f"{('oui, fenêtres ' + str(x['fenetres_ou_elle_separe'])) if x['elle_separe'] else 'NON'}")
        marque = "★★★★" if s["elle_separe_partout"] else "✗"
        print(f"\n{marque} la lecture sépare les causes à tous les bruits : "
              f"{s['elle_separe_partout']} — elle sépare jusqu'au bruit "
              f"{s['le_bruit_le_plus_fort_ou_elle_separe']} (fenêtre "
              f"{s['la_fenetre_qui_y_arrive']}), et pas au-delà")


NOMS = {"une machoire": "une mâchoire", "deux machoires libres": "deux libres",
        "la pince": "la pince"}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def case(fen, bruit, nom, mems, r=6, ecr=0.0, amp=0.0):
        return {"ecrasement": ecr, "amplitude_um": amp, "bruit": bruit, "nom": nom,
                "departs": len(mems), "memoire_du_cap": 0.0, "fenetre_du_cap": fen,
                "bras": {b: {"reussites": r, "memes_feuilles": r, "tours_boucles": r,
                             "suivis": [{"decidable": True, "memoire_mediane": m}
                                        for m in mems]} for b in BRAS}}

    # ---- la mémoire lue
    c = case(8, 0.0, "x", [0.1, 0.2, 0.3])
    v("les mémoires lues sortent une par départ", len(_memoires_lues(c)) == 3)
    v("... et leur médiane est la mémoire de la case", _memoire_lue(c) == 0.2)
    v("une case sans suivi décidable ne rend aucune mémoire",
      _memoire_lue({"bras": {"la pince": {"suivis": []}}}) is None)

    # ---- ⭐⭐ le discriminant, dans les deux sens
    separe = {"cases": [case(8, 0.0, "A", [0.00, 0.02, 0.01]),
                        case(8, 0.0, "B", [0.70, 0.72, 0.71])], "fenetres": [8]}
    d = le_discriminant(separe, lambda c: c["fenetre_du_cap"] == 8)["par_bruit"][0]
    v("⭐⭐ la lecture SÉPARE quand l'écart entre matières dépasse la dispersion dans une",
      d["la_lecture_separe"] is True,
      f"entre {d['ecart_entre_matieres']} contre dans {d['dispersion_dans_une_matiere']}")
    brouille = {"cases": [case(8, 0.0, "A", [0.40, 0.90, 0.65]),
                          case(8, 0.0, "B", [0.42, 0.92, 0.67])], "fenetres": [8]}
    d2 = le_discriminant(brouille, lambda c: c["fenetre_du_cap"] == 8)["par_bruit"][0]
    v("⭐⭐ ... et elle NE sépare PAS quand les matières se recouvrent",
      d2["la_lecture_separe"] is False,
      f"entre {d2['ecart_entre_matieres']} contre dans "
      f"{d2['dispersion_dans_une_matiere']} — un cap fixe déguisé passerait ici")
    v("le discriminant compare à RÉGLAGE fixé, par un filtre sur la case",
      le_discriminant({"cases": [case(4, 0.0, "A", [0.1]), case(8, 0.0, "A", [0.9])],
                       "fenetres": [4, 8]},
                      lambda c: c["fenetre_du_cap"] == 4)["par_bruit"][0]["memoire_la_plus_haute"]
      == 0.1, "sinon un écart entre réglages passerait pour un écart entre matières")

    # ---- le témoin fixe, relu et jamais remarché
    grille = {"cases": [case(8, 0.0, "A", [0.1], r=9), case(16, 0.0, "A", [0.1], r=5)],
              "fenetres": [8, 16], "departs": 1}
    fixe = {"juger": {"un_reglage_unique": {
        n: {"memoire_unique": 0.75, "reussites": 7} for n in BRAS}}}
    cf = contre_le_fixe(grille, fixe)
    v("le cap lu est comparé au meilleur cap posé de `143`",
      cf["decidable"] and cf["la pince"]["reussites_posees"] == 7)
    v("... et la meilleure fenêtre est celle qui réussit le plus",
      cf["la pince"]["meilleure_fenetre"] == 8 and cf["la pince"]["reussites_lues"] == 9)
    v("⭐ le verdict dit franchement quand le cap lu fait mieux",
      cf["la pince"]["le_cap_lu_fait_mieux"] is True and cf["la pince"]["ecart"] == 2)
    cf2 = contre_le_fixe({"cases": [case(8, 0.0, "A", [0.1], r=3)], "fenetres": [8]}, fixe)
    v("... et quand il fait moins bien",
      cf2["la pince"]["le_cap_lu_fait_mieux"] is False and cf2["la pince"]["ecart"] == -4)
    v("⚠ sans le témoin de `143`, la comparaison est indécidable et le dit",
      not contre_le_fixe(grille, None)["decidable"])

    # ---- le jugement
    v("un jugement sans case est indécidable", not juger({"cases": []}, None)["decidable"])
    gj = {"cases": separe["cases"] + [case(4, 0.0, "A", [0.3]), case(4, 0.0, "B", [0.31])],
          "fenetres": [4, 8]}
    jj = juger(gj, fixe)
    v("⭐⭐ le résumé ne CHOISIT aucune fenêtre : il dit à quels bruits une fenêtre sépare",
      jj["la_lecture_survit_elle_au_bruit"]["bruits_ou_elle_separe"] == [0.0],
      f"{jj['la_lecture_survit_elle_au_bruit']['bruits_ou_elle_separe']}")
    # ⚠ L'attendu est DÉRIVÉ de ce que la grille contient, jamais posé : j'avais écrit 8 alors que
    # la fenêtre 4 sépare aussi dans cette fixture, donc la réponse est 4.
    sep = jj["la_lecture_survit_elle_au_bruit"]["par_bruit"][0]["fenetres_ou_elle_separe"]
    v("... et il nomme la PLUS COURTE fenêtre qui franchit le bruit le plus fort",
      jj["la_lecture_survit_elle_au_bruit"]["la_fenetre_qui_y_arrive"] == min(sep),
      f"{jj['la_lecture_survit_elle_au_bruit']['la_fenetre_qui_y_arrive']} pour des fenêtres "
      f"qui séparent {sep}")
    deux_bruits = {"cases": separe["cases"]
                   + [case(8, 8.0, "A", [0.40, 0.90]), case(8, 8.0, "B", [0.42, 0.92])],
                   "fenetres": [8]}
    jd = juger(deux_bruits, fixe)["la_lecture_survit_elle_au_bruit"]
    v("⭐⭐ ... et un bruit où AUCUNE fenêtre ne sépare est dit franchement",
      jd["bruits_ou_elle_separe"] == [0.0] and jd["elle_separe_partout"] is False,
      f"{jd['bruits_ou_elle_separe']}")
    v("le bruit le plus fort franchi est celui que la mesure donne, pas le plus grand testé",
      jd["le_bruit_le_plus_fort_ou_elle_separe"] == 0.0)

    # ---- ⭐ la règle elle-même, de bout en bout sur une vraie matière
    vraie = une_case((0.0, 42.4), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                     fenetre_du_cap=8)
    lisse = une_case((0.0, 0.0), 0.0, LARGEUR_DE_REFERENCE, departs=1, tours=0.05,
                     fenetre_du_cap=8)
    v("⭐⭐ sur une vraie matière FROISSÉE la règle lit une mémoire, sur une spirale NUE elle n'en "
      "lit aucune",
      (_memoire_lue(vraie) or 0.0) > (_memoire_lue(lisse) or 0.0),
      f"froissée {_memoire_lue(vraie)} contre nue {_memoire_lue(lisse)}")
    v("... et la spirale nue en lit exactement zéro", _memoire_lue(lisse) == 0.0,
      "une rotation franche ne demande aucun cap")

    # ---- réagréger
    petit = {"sur_la_grille": {"cases": [vraie], "departs": 1, "tours": 0.05, "bruits": [0.0],
                               "fenetres": [8], "largeur_en_pas": LARGEUR_DE_REFERENCE}}
    petit["juger"] = juger(petit["sur_la_grille"], None)
    v("⭐ réagréger depuis les suivis rangés rend le MÊME verdict, sans remarcher",
      reagreger(json.loads(json.dumps(petit)), Path("/inexistant.json"))["juger"]
      == petit["juger"])

    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "témoin absent"})
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
