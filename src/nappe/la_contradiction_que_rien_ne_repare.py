"""De quoi est faite la contradiction que rien ne répare ? — ce que `166` laissait ouvert.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `165` mesure que raccourcir le pas répare une pose qui se contredit, et
qu'elle **s'épuise** sur la matière du rouleau ; `166` mesure que changer de **direction** ne la
répare pas davantage. Il reste donc une contradiction que **ni la longueur ni la direction** ne
réparent, et rien ne disait ce qu'elle est.

⭐⭐⭐⭐ L'HYPOTHÈSE VIENT DE `153`, ET ELLE EST GRATUITE À TESTER. Sur la matière du rouleau la
**vraie** normale sort du plan du tour — `R4-F120` mesure `|n·z| = 0,278624`, soit 16,178° hors
plan — alors que `une_machoire` rend `n' = t' × z`, donc une composante axiale **nulle par
construction**. La mâchoire ne peut pas **exprimer** ce qu'il y aurait à estimer. Si la
contradiction irréparable est exactement celle-là, elle doit sortir du plan **davantage** que celles
qu'on répare.

⚠⚠ LA QUANTITÉ EST ANALYTIQUE ET NE COÛTE AUCUNE LECTURE : `vol.normale_locale` est exacte, donc
ce que la fixture sait est comparé à ce que le marcheur fait, sans qu'aucune lecture ne soit
dépensée pour le savoir.

⚠⚠⚠ ET LA COMPARAISON EST APPARIÉE DANS LA MARCHE. Une marche qui s'épuise porte les **deux**
populations — les contradictions qu'elle a réparées, et celles qui l'ont arrêtée. Comparer leurs
médianes **dans la même marche** est le seul appariement disponible, et c'est celui que `161` a
rendu obligatoire.

⚠⚠ LES MARCHES QUI NE S'ÉPUISENT PAS N'ONT QU'UNE population, donc elles ne s'apparient pas. Ce
qu'elles disent est publié **à part** et nommé comme non apparié, jamais mélangé au compte.

⚠ CONTRÔLE OBLIGATOIRE : sur la spirale NUE aucune pose ne se contredit, donc les deux populations
sont **vides** et la comparaison doit le dire — jamais rendre zéro.

Usage :
    uv run python src/nappe/la_contradiction_que_rien_ne_repare.py --verifier
    uv run python src/nappe/la_contradiction_que_rien_ne_repare.py \\
        --json docs/mesures/la_contradiction_que_rien_ne_repare.json
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

from la_pince_tient_elle_la_feuille import (AVANCE_EN_LONGUEUR_DONDE,  # noqa: E402
                                            LARGEUR_DE_REFERENCE, LONGUEUR_DONDE_UM, MATIERES,
                                            RAYON_MM, _matiere, _nom, _PAS, _VOXEL, suivre,
                                            un_depart)

BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
FENETRE = 32
BRAS = (("la pince de `144`", True, True, False),
        ("une mâchoire avec rejet", False, False, True))
LA_SPIRALE_NUE = (0.0, 0.0)


def _cadre():
    return _PAS(), _VOXEL(), AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, bras):
    _n, deux, contrainte, rejeter = bras
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True, reprendre_la_pose=True)


def le_cas_dune_marche(x: dict) -> dict | None:
    """Ce qu'UNE marche dit des deux populations, et laquelle elle porte.

    ⚠⚠ TROIS CAS, ET ILS NE SE MÉLANGENT PAS : une marche **appariable** porte les deux
    populations et permet la comparaison ; une marche **réparée seulement** n'en porte qu'une et ne
    s'apparie pas ; une marche **muette** n'a rencontré aucune contradiction.
    """
    if not x.get("decidable"):
        return None
    rep = x.get("hors_plan_des_contradictions_reparees")
    epu = x.get("hors_plan_des_contradictions_epuisees")
    out = {"reparees": int(x.get("contradictions_reparees", 0)),
           "epuisees": int(x.get("contradictions_epuisees", 0)),
           "hors_plan_reparees": rep, "hors_plan_epuisees": epu}
    if rep is not None and epu is not None:
        out["cas"] = "appariable"
        # ⭐⭐⭐⭐ L'APPARIEMENT EST DANS LA MARCHE : les deux medianes viennent du MEME suiveur, sur
        # la MEME matiere, au MEME bruit. C'est le seul appariement disponible, et `161` l'exige.
        out["lepuisee_sort_davantage"] = bool(epu > rep)
        out["elles_sont_egales"] = bool(epu == rep)
    elif rep is not None:
        out["cas"] = "reparee_seulement"
    elif epu is not None:
        out["cas"] = "epuisee_seulement"
    else:
        out["cas"] = "muette"
    return out


def _resume(xs: list[dict]) -> dict:
    cs = [c for c in (le_cas_dune_marche(x) for x in xs) if c is not None]
    if not cs:
        return {"decidable": False, "raison": "aucune marche décidable", "departs": len(xs)}
    app = [c for c in cs if c["cas"] == "appariable"]
    base = {"decidable": True, "departs": len(xs), "decidables": len(cs),
            "marches_appariables": len(app),
            "marches_reparees_seulement": int(sum(1 for c in cs
                                                  if c["cas"] == "reparee_seulement")),
            "marches_epuisees_seulement": int(sum(1 for c in cs
                                                  if c["cas"] == "epuisee_seulement")),
            "marches_muettes": int(sum(1 for c in cs if c["cas"] == "muette")),
            "contradictions_reparees": int(sum(c["reparees"] for c in cs)),
            "contradictions_epuisees": int(sum(c["epuisees"] for c in cs))}
    if not app:
        # ⚠⚠ C'EST LE CAS DU CONTROLE : rien a apparier, et le dire est la bonne reponse.
        base["apparie"] = False
        base["raison"] = "aucune marche ne porte les deux populations"
    else:
        base["apparie"] = True
        base["lepuisee_sort_davantage"] = int(sum(1 for c in app if c["lepuisee_sort_davantage"]))
        base["elles_sont_egales"] = int(sum(1 for c in app if c["elles_sont_egales"]))
        base["lepuisee_sort_moins"] = int(sum(1 for c in app if not c["lepuisee_sort_davantage"]
                                              and not c["elles_sont_egales"]))
        # ⚠⚠ LES NIVEAUX SONT DES MEDIANES DE MEDIANES, publiees a cote du compte et jamais a sa
        # place : c'est le COMPTE apparie qui tranche, le niveau dit seulement a quelle echelle.
        base["hors_plan_reparees"] = round(float(statistics.median(
            [c["hors_plan_reparees"] for c in app])), 6)
        base["hors_plan_epuisees"] = round(float(statistics.median(
            [c["hors_plan_epuisees"] for c in app])), 6)
    # ⚠ Ce que disent les marches NON appariees est publie A PART et nomme comme tel.
    seuls = [c["hors_plan_reparees"] for c in cs if c["cas"] == "reparee_seulement"]
    base["hors_plan_des_marches_non_appariees"] = (
        round(float(statistics.median(seuls)), 6) if seuls else None)
    return base


def lenquete(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    cases = []
    for b in bras:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                xs = [_marcher(vol, k, departs, pas_um, voxel_um, avance_um, b)
                      for k in range(int(departs))]
                cases.append({"bras": b[0], "nom": _nom(ecr, amp), "ecrasement": float(ecr),
                              "amplitude_um": float(amp), "bruit": float(bruit), **_resume(xs)})
    return {"decidable": bool(cases), "cases": cases, "bras": [b[0] for b in bras],
            "bruits": [float(b) for b in bruits], "departs": int(departs)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    dec = [c for c in cs if c.get("decidable")]
    cles = ("decidables", "marches_appariables", "marches_reparees_seulement",
            "marches_epuisees_seulement", "marches_muettes", "contradictions_reparees",
            "contradictions_epuisees")
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           **{k: int(sum(c.get(k, 0) for c in dec)) for k in cles}}
    app = [c for c in dec if c.get("apparie")]
    if app:
        for k in ("lepuisee_sort_davantage", "elles_sont_egales", "lepuisee_sort_moins"):
            out[k] = int(sum(c[k] for c in app))
        for k in ("hors_plan_reparees", "hors_plan_epuisees"):
            out[k] = round(float(statistics.median([c[k] for c in app])), 6)
    # ⚠⚠ COMPARER 392/176 A 1100/73 SERAIT COMPARER DES TOTAUX SUR DES POPULATIONS INEGALES :
    # les deux bras ne rencontrent pas le meme nombre de contradictions. La PART est la seule
    # forme sous laquelle deux bras se comparent, et elle repond a une question bien posee :
    # ce bras ayant rencontre une contradiction, combien de fois n'a-t-il pas su la reparer ?
    vues = out["contradictions_reparees"] + out["contradictions_epuisees"]
    out["contradictions_rencontrees"] = int(vues)
    out["part_des_contradictions_epuisees"] = (
        round(out["contradictions_epuisees"] / vues, 6) if vues else None)
    ns = [c["hors_plan_des_marches_non_appariees"] for c in dec
          if c.get("hors_plan_des_marches_non_appariees") is not None]
    out["hors_plan_des_marches_non_appariees"] = (
        round(float(statistics.median(ns)), 6) if ns else None)
    # ⭐⭐⭐⭐ LA REVENDICATION EST UN COMPTE APPARIE, jamais une comparaison de niveaux : la
    # contradiction irreparable sort-elle davantage du plan DANS LA MEME MARCHE ?
    out["elle_sort_davantage"] = bool(out.get("marches_appariables", 0) > 0
                                      and out.get("lepuisee_sort_moins", 0) == 0
                                      and out.get("lepuisee_sort_davantage", 0) > 0)
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_bras(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["bras"] == b], b)
            for b in dict.fromkeys(c["bras"] for c in d["cases"])]


def _croiser(d: dict, bras: str) -> list[dict]:
    cases = [c for c in d["cases"] if c["bras"] == bras]
    return [_cumuler([c for c in cases if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in cases)]


def juger(d: dict) -> dict:
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, bras = par_matiere(d), par_bras(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    # ⚠⚠⚠ LE CONTROLE EST UNE ABSENCE TOTALE : sur la spirale nue AUCUNE pose ne se contredit,
    # donc les deux populations sont vides et il n'y a rien a comparer. Une seule contradiction y
    # voudrait dire que la regle mesure son propre bruit.
    controle = {"nom": nue["nom"] if nue else None,
                "contradictions_reparees": nue["contradictions_reparees"] if nue else None,
                "contradictions_epuisees": nue["contradictions_epuisees"] if nue else None,
                "marches_appariables": nue["marches_appariables"] if nue else None,
                "decidables": nue["decidables"] if nue else None}
    controle["il_est_vide"] = bool(
        nue is not None and controle["contradictions_reparees"] == 0
        and controle["contradictions_epuisees"] == 0
        and controle["marches_appariables"] == 0)
    return {"decidable": True, "par_matiere": mat, "par_bras": bras,
            "tout": _cumuler(d["cases"], "tout"),
            "le_controle_de_la_spirale_nue": controle,
            "elle_sort_davantage_par_bras": {g["nom"]: g["elle_sort_davantage"] for g in bras},
            "par_bras_et_matiere": {b: _croiser(d, b)
                                    for b in dict.fromkeys(c["bras"] for c in d["cases"])},
            "matieres_ou_elle_sort_davantage_par_bras": {
                b: [str(c["nom"]) for c in _croiser(d, b) if c["elle_sort_davantage"]]
                for b in dict.fromkeys(c["bras"] for c in d["cases"])}}


def mesurer(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    d = lenquete(matieres, bruits, bras, departs)
    return {"enquete": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    r["juger"] = juger(r["enquete"])
    return r


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    c = j["le_controle_de_la_spirale_nue"]
    marque = "★" if c["il_est_vide"] else "✗"
    print(f"{marque} contrôle — sur la spirale NUE aucune pose ne se contredit : "
          f"{c['contradictions_reparees']} réparée, {c['contradictions_epuisees']} épuisée, "
          f"{c['marches_appariables']} marche appariable")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —")
        print(f"   {'':>22} | {'appar.':>6} | {'contradictions':>16} | {'part épu.':>9} | "
              f"{'hors plan rép.':>14} | {'hors plan épu.':>14} | {'+ / = / -':>11}")
        for g in groupes:
            part = g["part_des_contradictions_epuisees"]
            dit = f"{part:>9.6f}" if part is not None else f"{'—':>9}"
            if not g.get("marches_appariables"):
                print(f"   {_court(g['nom']):>22} | {'—':>6} | "
                      f"{g['contradictions_reparees']:>7}/{g['contradictions_epuisees']:<8} | "
                      f"{dit} | {'(rien à apparier)':>14} | {'':>14} | {'—':>11}")
                continue
            tient = "★" if g["elle_sort_davantage"] else " "
            print(f" {tient} {_court(g['nom']):>22} | {g['marches_appariables']:>6d} | "
                  f"{g['contradictions_reparees']:>7}/{g['contradictions_epuisees']:<8} | "
                  f"{dit} | "
                  f"{g['hors_plan_reparees']:>14.6f} | {g['hors_plan_epuisees']:>14.6f} | "
                  f"{g['lepuisee_sort_davantage']:>3}/{g['elles_sont_egales']:>3}/"
                  f"{g['lepuisee_sort_moins']:>3}")
    print("\n★★★★ la contradiction que rien ne répare sort-elle DAVANTAGE du plan, "
          "dans la même marche ?")
    for nom, oui in j["elle_sort_davantage_par_bras"].items():
        noms = j["matieres_ou_elle_sort_davantage_par_bras"].get(nom, [])
        print(f"      {_court(nom):>22} : {'OUI' if oui else 'non'} — "
              f"{', '.join(_court(n) for n in noms) if noms else 'aucune matière'}")


def _suivi(rep=None, epu=None, nrep=0, nepu=0) -> dict:
    return {"decidable": True,
            "hors_plan_des_contradictions_reparees": rep,
            "hors_plan_des_contradictions_epuisees": epu,
            "contradictions_reparees": int(nrep), "contradictions_epuisees": int(nepu)}


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

    print("— trois cas, et ils ne se mélangent pas —")
    v("⭐⭐⭐ une marche qui porte les DEUX populations est appariable",
      le_cas_dune_marche(_suivi(0.31, 0.45, 20, 21))["cas"] == "appariable")
    v("⭐⭐⭐⭐ ... et une qui n'en porte qu'une ne s'apparie PAS, elle est nommée",
      le_cas_dune_marche(_suivi(0.17, None, 15, 0))["cas"] == "reparee_seulement"
      and le_cas_dune_marche(_suivi(None, 0.45, 0, 3))["cas"] == "epuisee_seulement",
      "une seule population ne se compare à rien")
    v("⚠⚠ une marche sans aucune contradiction est MUETTE, pas une comparaison nulle",
      le_cas_dune_marche(_suivi())["cas"] == "muette")
    v("⚠ une marche indécidable n'est pas un cas", le_cas_dune_marche({"decidable": False}) is None)

    print("\n— l'appariement est DANS la marche —")
    plus = le_cas_dune_marche(_suivi(0.318571, 0.453282, 20, 21))
    moins = le_cas_dune_marche(_suivi(0.45, 0.31, 20, 21))
    egal = le_cas_dune_marche(_suivi(0.30, 0.30, 5, 5))
    v("⭐⭐⭐⭐ l'épuisée sort davantage quand sa médiane dépasse celle des réparées",
      plus["lepuisee_sort_davantage"] is True and plus["elles_sont_egales"] is False)
    v("⭐⭐⭐ ... et l'inverse se compte aussi, il n'est pas écarté",
      moins["lepuisee_sort_davantage"] is False and moins["elles_sont_egales"] is False)
    # ⚠⚠ UN ECART EXACTEMENT NUL N'EST NI L'UN NI L'AUTRE, l'enonce du depot depuis `161`.
    v("⚠⚠ un écart exactement nul est compté à part, jamais avec « sort moins »",
      egal["elles_sont_egales"] is True and egal["lepuisee_sort_davantage"] is False)

    print("\n— le résumé compte, il ne moyenne pas —")
    xs = [_suivi(0.31, 0.45, 20, 21), _suivi(0.20, 0.60, 3, 2), _suivi(0.17, None, 15, 0),
          _suivi()]
    r = _resume(xs)
    v("⭐⭐⭐ les marches non appariées sont comptées à part, jamais dans l'appariement",
      r["marches_appariables"] == 2 and r["marches_reparees_seulement"] == 1
      and r["marches_muettes"] == 1)
    v("⭐⭐⭐⭐ le verdict est un COMPTE de marches, pas une comparaison de niveaux",
      r["lepuisee_sort_davantage"] == 2 and r["lepuisee_sort_moins"] == 0)
    v("⚠⚠ ... et ce que disent les marches non appariées est publié À PART et nommé",
      abs(r["hors_plan_des_marches_non_appariees"] - 0.17) < 1e-9)
    v("⚠ sans une seule marche appariable, le résumé le DIT",
      _resume([_suivi(0.17, None, 15, 0)])["apparie"] is False
      and _resume([_suivi(0.17, None, 15, 0)])["decidable"] is True)
    v("⚠⚠ ... et sans aucune marche décidable non plus",
      _resume([{"decidable": False}])["decidable"] is False)

    print("\n— la victoire exige que RIEN ne sorte moins —")
    v("⭐⭐⭐⭐ elle tient quand aucune marche appariée ne contredit la revendication",
      _cumuler([r], "un")["elle_sort_davantage"] is True)
    contre = _resume([_suivi(0.31, 0.45, 20, 21), _suivi(0.45, 0.31, 20, 21)])
    v("⭐⭐⭐⭐ ... et elle TOMBE dès qu'une seule marche sort moins",
      _cumuler([contre], "un")["elle_sort_davantage"] is False,
      "une sur deux suffit, c'est un compte et non une majorité")
    v("⭐⭐⭐ ... et une matière sans rien à apparier ne la gagne pas",
      _cumuler([_resume([_suivi()])], "un")["elle_sort_davantage"] is False,
      "rien à comparer n'est pas une victoire")

    print("\n— le contrôle est une absence TOTALE —")
    def case(nom, bras_, xs_):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0,
                "bruit": 0.0, **_resume(xs_)}
    bon = {"decidable": True, "bras": ["p"], "bruits": [0.0], "departs": 2,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [_suivi(), _suivi()]),
                     case("dure", "p", [_suivi(0.31, 0.45, 20, 21)])]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand AUCUNE pose ne se contredit sur la spirale nue",
      j["le_controle_de_la_spirale_nue"]["il_est_vide"] is True)
    v("⭐⭐⭐⭐ ... et il TOMBE dès qu'une seule contradiction y apparaît",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [_suivi(0.01, None, 1, 0)]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_vide"] is False,
      "une seule voudrait dire que la règle mesure son propre bruit")
    v("⭐⭐⭐ le croisement bras × matière existe, et la spirale nue ne gagne rien",
      j["matieres_ou_elle_sort_davantage_par_bras"]["p"] == ["dure"])

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    v("⭐⭐⭐⭐ sur la spirale NUE la mesure réelle ne trouve AUCUNE contradiction",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] is True,
      f"{petite['juger']['le_controle_de_la_spirale_nue']}")
    # ⚠⚠⚠ ET SUR LA MATIERE DU ROULEAU, LES DEUX POPULATIONS DOIVENT EXISTER REELLEMENT. Sans ce
    # controle la batterie ne vérifierait jamais sur donnees reelles que l'enregistrement marche —
    # le trou que `164`, `165` et `166` ont paye chacun leur tour.
    dure = mesurer(matieres=(MATIERES[4],), bruits=(8.0,), bras=(BRAS[0],), departs=4)
    cas = dure["enquete"]["cases"][0]
    v("⭐⭐⭐⭐ sur la matière du rouleau, les DEUX populations existent réellement",
      cas["contradictions_reparees"] > 0 and cas["contradictions_epuisees"] > 0
      and cas["marches_appariables"] > 0,
      f"{cas['contradictions_reparees']} réparées, {cas['contradictions_epuisees']} épuisées, "
      f"{cas['marches_appariables']} marches appariables")
    # ⚠⚠⚠ CE CONTROLE N'ATTEND AUCUNE DIRECTION, ET C'EST DELIBERE : asserter que l'epuisee sort
    # davantage reviendrait a ecrire la conclusion dans l'instrument qui doit la trancher, et une
    # seule case suffirait a la faire passer. Ce qu'il exige est que la comparaison soit RENDUE et
    # que la partition des marches appariees soit COMPLETE — une marche qui disparaitrait d'une
    # branche rendrait un verdict que rien ne contredit.
    v("⭐⭐⭐⭐ ... et la comparaison y est RENDUE, sans qu'aucune marche appariée ne disparaisse",
      cas["lepuisee_sort_davantage"] + cas["elles_sont_egales"] + cas["lepuisee_sort_moins"]
      == cas["marches_appariables"],
      f"{cas['hors_plan_reparees']} réparées contre {cas['hors_plan_epuisees']} épuisées, "
      f"{cas['lepuisee_sort_davantage']}/{cas['elles_sont_egales']}/"
      f"{cas['lepuisee_sort_moins']} sur {cas['marches_appariables']}")

    print("\n— la part est la seule forme sous laquelle deux bras se comparent —")
    maigre = _resume([_suivi(0.31, 0.45, 3, 1)])
    gras = _resume([_suivi(0.31, 0.45, 90, 10)])
    a, b = _cumuler([maigre], "maigre"), _cumuler([gras], "gras")
    v("⭐⭐⭐⭐ un bras qui épuise DEUX FOIS MOINS en compte peut épuiser DAVANTAGE en part",
      b["contradictions_epuisees"] > a["contradictions_epuisees"]
      and b["part_des_contradictions_epuisees"] < a["part_des_contradictions_epuisees"],
      f"{a['contradictions_epuisees']}/{a['contradictions_rencontrees']} = "
      f"{a['part_des_contradictions_epuisees']} contre {b['contradictions_epuisees']}/"
      f"{b['contradictions_rencontrees']} = {b['part_des_contradictions_epuisees']}")
    v("⭐⭐⭐ la part se prend sur les contradictions RENCONTRÉES, jamais sur les marches",
      a["contradictions_rencontrees"] == 4 and abs(a["part_des_contradictions_epuisees"]
                                                   - 0.25) < 1e-9)
    # ⚠⚠ ZERO EST UNE VALEUR SIGNIFIANTE : « ce bras n'a rien epuise » et « ce bras n'a rencontre
    # aucune contradiction » sont deux faits differents, et une part nulle les confondrait.
    v("⚠⚠ sans une seule contradiction rencontrée la part n'existe pas, elle ne vaut pas zéro",
      _cumuler([_resume([_suivi()])], "vide")["part_des_contradictions_epuisees"] is None
      and _cumuler([_resume([_suivi(0.2, None, 7, 0)])],
                   "rien épuisé")["part_des_contradictions_epuisees"] == 0.0)
    avant = json.loads(json.dumps(petite["enquete"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["enquete"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "enquete": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, les deux tableaux et le verdict",
      "contrôle" in sortie and "par bras" in sortie and "par matière" in sortie
      and "hors plan" in sortie, f"{len(sortie)} caractères")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "rien à montrer"})
    v("⚠ un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else '⛔ ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = (reagreger(json.loads(a.reagreger.read_text())) if a.reagreger is not None
         else mesurer(departs=int(a.departs)))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    afficher(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
