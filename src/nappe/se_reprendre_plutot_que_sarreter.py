"""Se reprendre plutôt que s'arrêter — ce que `164` laissait ouvert.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `164` mesure qu'un marcheur qui **s'arrête** sur une pose qui se
contredit livre cinq fois plus d'utilisable sur la matière du rouleau — mais il **s'arrête**, et il
paie **22** départs raccourcis pour rien sur la pince. Or ce dépôt a déjà son idiome pour une pose
qui ne va pas : **halver l'avance et réessayer**, ce que la contrainte de `142` fait depuis toujours.
L'hypothèse est que les mâchoires s'accrochent au mauvais interstice **parce que le pas est allé trop
loin** ; un pas plus court atterrirait dans le bon.

⚠⚠ TROIS MARCHEURS, LE MÊME ÉNONCÉ, TROIS MOMENTS. Le **sourd** n'écoute pas. Celui qui
**s'arrête** refuse la pose et finit là. Celui qui **se reprend** halve son avance et réessaie,
jusqu'à ce que l'avance tombe sous le voxel — en dessous, le lecteur ne peut plus exprimer le
déplacement, donc la boucle s'épuise d'elle-même et ne peut pas tourner sans fin.

⚠⚠⚠ ET LA REPRISE PEUT PERDRE, SUR LES DEUX AXES. Elle continue là où l'arrêt s'était arrêté, donc
elle peut sauter plus loin : `162` mesure un rappel de **0,9196**, pas de 1. Une reprise qui livre
une trajectoire contaminée là où l'arrêt en livrait une courte et sûre est une **perte**, et c'est
elle qu'il faut compter. La victoire est **jointe** — au moins autant d'utilisable sur **chaque**
départ apparié, et davantage sur au moins un.

⚠⚠ CONTRÔLE OBLIGATOIRE : sur la spirale NUE rien ne se contredit, donc les **trois** marcheurs
doivent livrer exactement la même chose. Une reprise qui y changerait un seul pas mesurerait son
propre bruit.

Usage :
    uv run python src/nappe/se_reprendre_plutot_que_sarreter.py --verifier
    uv run python src/nappe/se_reprendre_plutot_que_sarreter.py \\
        --json docs/mesures/se_reprendre_plutot_que_sarreter.json
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
                                            RAYON_MM, _matiere, _nom, _PAS, _VOXEL,
                                            ce_que_vaut_une_livraison, suivre, un_depart)

BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
FENETRE = 32
BRAS = (("la pince de `144`", True, True, False),
        ("une mâchoire avec rejet", False, False, True))
# (nom, les mots-clés que `suivre` reçoit) — le même énoncé à trois moments.
MARCHEURS = (("sourd", {}),
             ("sarrete", {"refuser_la_pose": True}),
             ("se_reprend", {"reprendre_la_pose": True}))
LA_SPIRALE_NUE = (0.0, 0.0)


def _cadre():
    return _PAS(), _VOXEL(), AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, bras, kw):
    _n, deux, contrainte, rejeter = bras
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True, **kw)


# ⭐⭐⭐⭐ CE QU'UNE LIVRAISON VAUT EST DIT UNE SEULE FOIS, dans le module partage, a cote du
# predicat joint de `147`. Il etait ecrit ici ; `166` en avait besoin, et deux definitions sous un
# seul nom auraient laisse deux tranches mesurer deux choses.
utilisable = ce_que_vaut_une_livraison


def _apparier(marches: dict) -> dict | None:
    """Un départ, marché trois fois — et ce que chaque marcheur en remet."""
    out = {}
    for nom, x in marches.items():
        u = utilisable(x)
        if u is None:
            return None
        out[nom] = {"pas": int(x["pas"]), "utilisable": u,
                    "contaminee": bool(int(x.get("pas_qui_sautent", 0)) > 0),
                    "reprises": int(x.get("poses_reprises", 0)),
                    "epuisee": bool(x.get("fin") == "la pince ne peut plus avancer")}
    # ⭐⭐⭐ LES DEUX ISSUES QUI DECIDENT, et elles sont exclusives : la reprise RECUPERE ce que
    # l'arret jetait, ou elle le PERD en allant trop loin.
    a, r = out["sarrete"], out["se_reprend"]
    out["reprise_recupere"] = bool(r["utilisable"] > a["utilisable"])
    out["reprise_perd"] = bool(r["utilisable"] < a["utilisable"])
    out["identiques"] = bool(len({m["pas"] for m in
                                  (out["sourd"], out["sarrete"], out["se_reprend"])}) == 1)
    return out


def _resume(paires: list[dict]) -> dict:
    """Ce qu'un paquet de départs dit des trois marcheurs."""
    ps = [p for p in paires if p is not None]
    if not ps:
        return {"decidable": False, "raison": "aucun départ apparié", "departs": len(paires)}
    out = {"decidable": True, "departs": len(paires), "apparies": len(ps),
           "departs_identiques": int(sum(1 for p in ps if p["identiques"])),
           "reprises": int(sum(p["se_reprend"]["reprises"] for p in ps)),
           "reprises_epuisees": int(sum(1 for p in ps if p["se_reprend"]["epuisee"]
                                        and p["se_reprend"]["reprises"] > 0)),
           "reprise_recupere": int(sum(1 for p in ps if p["reprise_recupere"])),
           "reprise_perd": int(sum(1 for p in ps if p["reprise_perd"]))}
    for nom in ("sourd", "sarrete", "se_reprend"):
        out[nom] = {"pas": int(sum(p[nom]["pas"] for p in ps)),
                    "utilisable": int(sum(p[nom]["utilisable"] for p in ps)),
                    "contaminees": int(sum(1 for p in ps if p[nom]["contaminee"]))}
    return out


def lepreuve(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    """Ce que chacun des trois marcheurs livre, matière par matière."""
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    cases = []
    for b in bras:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                paires = [_apparier({nom: _marcher(vol, k, departs, pas_um, voxel_um,
                                                   avance_um, b, kw)
                                     for nom, kw in MARCHEURS})
                          for k in range(int(departs))]
                cases.append({"bras": b[0], "nom": _nom(ecr, amp), "ecrasement": float(ecr),
                              "amplitude_um": float(amp), "bruit": float(bruit),
                              **_resume(paires)})
    return {"decidable": bool(cases), "cases": cases, "bras": [b[0] for b in bras],
            "marcheurs": [m[0] for m in MARCHEURS], "bruits": [float(b) for b in bruits],
            "departs": int(departs)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    dec = [c for c in cs if c.get("decidable")]
    cles = ("apparies", "departs_identiques", "reprises", "reprises_epuisees",
            "reprise_recupere", "reprise_perd")
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           **{k: int(sum(c.get(k, 0) for c in dec)) for k in cles}}
    for m in ("sourd", "sarrete", "se_reprend"):
        parts = [c[m] for c in dec if c.get(m) is not None]
        out[m] = {k: int(sum(p[k] for p in parts))
                  for k in ("pas", "utilisable", "contaminees")} if parts else None
    # ⭐⭐⭐⭐ LA VICTOIRE EST JOINTE : la reprise ne l'emporte que si elle recupere sur au moins un
    # depart ET n'en perd aucun. Chaque moitie prise seule est satisfaite par un marcheur inutile
    # — celui qui ne se reprend JAMAIS ne perd aucun depart.
    out["la_reprise_lemporte"] = bool(out["reprise_recupere"] > 0 and out["reprise_perd"] == 0)
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_bras(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["bras"] == b], b)
            for b in dict.fromkeys(c["bras"] for c in d["cases"])]


def _nom_de(g: dict) -> str:
    return str(g["nom"])


def _croiser(d: dict, bras: str) -> list[dict]:
    """Les groupes matière d'UN SEUL bras — le croisement que `161` a rendu obligatoire."""
    cases = [c for c in d["cases"] if c["bras"] == bras]
    return [_cumuler([c for c in cases if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in cases)]


def juger(d: dict) -> dict:
    """Où la reprise l'emporte sur l'arrêt, et le contrôle qui rend la réponse lisible."""
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, bras = par_matiere(d), par_bras(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    # ⚠⚠⚠ LE CONTROLE EST UNE IDENTITE, PAS UNE ABSENCE. Sur la spirale nue rien ne se contredit,
    # donc les TROIS marcheurs doivent livrer EXACTEMENT la meme chose — pas « a peu pres », pas
    # « aucun arret », mais le meme nombre de pas. C'est plus dur qu'un compte a zero, et c'est ce
    # qui interdit a la reprise de mesurer son propre bruit.
    controle = {"nom": nue["nom"] if nue else None,
                "departs_identiques": nue["departs_identiques"] if nue else None,
                "apparies": nue["apparies"] if nue else None,
                "reprises": nue["reprises"] if nue else None}
    controle["il_est_identique"] = bool(
        nue is not None and controle["apparies"] > 0
        and controle["departs_identiques"] == controle["apparies"]
        and controle["reprises"] == 0)
    return {"decidable": True, "par_matiere": mat, "par_bras": bras,
            "tout": _cumuler(d["cases"], "tout"),
            "le_controle_de_la_spirale_nue": controle,
            "la_reprise_lemporte_par_bras": {g["nom"]: g["la_reprise_lemporte"] for g in bras},
            "matieres_ou_la_reprise_lemporte": [m["nom"] for m in mat
                                                if m["la_reprise_lemporte"]],
            # ⚠⚠⚠ UN VERDICT PAR MATIERE MET LES DEUX BRAS EN COMMUN, et c'est la leçon que `161`
            # a payee : la pince ne perd AUCUN depart pendant que deux matieres en affichent
            # douze et quinze, tous venus de la machoire seule. Un verdict confondu efface donc
            # la reponse de l'instrument LIVRE. Le croisement est publie pour que le tableau par
            # matiere ne se lise jamais seul.
            "matieres_ou_la_reprise_lemporte_par_bras": {
                b: [_nom_de(c) for c in _croiser(d, b) if c["la_reprise_lemporte"]]
                for b in dict.fromkeys(c["bras"] for c in d["cases"])},
            # ⚠⚠ ET LE CROISEMENT LUI-MEME EST PUBLIE, pas seulement ses gagnants. Une garde qui
            # aurait besoin de ces nombres devrait sinon IMPORTER ce module pour les recalculer —
            # une garde qui importe ce qu'elle garde — alors qu'elle doit LIRE la mesure.
            "par_bras_et_matiere": {b: _croiser(d, b)
                                    for b in dict.fromkeys(c["bras"] for c in d["cases"])}}


def mesurer(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    d = lepreuve(matieres, bruits, bras, departs)
    return {"epreuve": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    r["juger"] = juger(r["epreuve"])
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
    marque = "★" if c["il_est_identique"] else "✗"
    print(f"{marque} contrôle — sur la spirale NUE les TROIS marcheurs livrent la même chose : "
          f"{c['departs_identiques']}/{c['apparies']} départs identiques, {c['reprises']} reprise")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —  (pas utilisables · livraisons contaminées)")
        entetes = ("sourd", "s'arrête", "se reprend")
        print(f"   {'':>22} | " + " | ".join(f"{h:>17}" for h in entetes)
              + f" | {'récup':>5} | {'perd':>4}")
        for g in groupes:
            cells = []
            for m in ("sourd", "sarrete", "se_reprend"):
                t = g.get(m)
                cells.append(f"{'—':>17}" if t is None
                             else f"{t['utilisable']:>10} · {t['contaminees']:<4}")
            tient = "★" if g["la_reprise_lemporte"] else " "
            print(f" {tient} {_court(g['nom']):>22} | " + " | ".join(cells)
                  + f" | {g['reprise_recupere']:>5} | {g['reprise_perd']:>4}")
    print("\n★★★★ où la REPRISE l'emporte sur l'arrêt (récupère au moins un départ, n'en perd "
          "aucun) :")
    for nom, gagne in j["la_reprise_lemporte_par_bras"].items():
        noms = j.get("matieres_ou_la_reprise_lemporte_par_bras", {}).get(nom, [])
        print(f"      {_court(nom):>22} : {'OUI' if gagne else 'non'} en tout — "
              f"{', '.join(_court(n) for n in noms) if noms else 'aucune matière'}")
    tous = j["matieres_ou_la_reprise_lemporte"]
    print(f"   ⚠ toutes matières et DEUX BRAS confondus : "
          f"{', '.join(_court(n) for n in tous) if tous else 'nulle part'} — un verdict confondu")
    print("     efface la réponse de l'instrument livré, comme `161` l'a payé.")


def _suivi(pas: int, saute: int = 0, reprises: int = 0, fin: str = "tour bouclé") -> dict:
    return {"decidable": True, "pas": int(pas), "pas_qui_sautent": int(saute),
            "poses_reprises": int(reprises), "fin": fin}


def _trois(sourd, sarrete, reprend) -> dict | None:
    return _apparier({"sourd": sourd, "sarrete": sarrete, "se_reprend": reprend})


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

    print("— une livraison contaminée vaut ZÉRO, l'énoncé de `164` repris mot pour mot —")
    v("⭐⭐⭐ une livraison propre vaut ses pas, une contaminée vaut zéro",
      utilisable(_suivi(900, 0)) == 900 and utilisable(_suivi(900, 3)) == 0)
    v("⚠⚠ une marche sans décompte de sauts ne PRÉTEND rien",
      utilisable({"decidable": True, "pas": 900}) is None)
    v("⚠ une marche indécidable n'est pas une livraison vide", utilisable({"decidable": False})
      is None)

    print("\n— les deux issues qui décident sont EXCLUSIVES —")
    recup = _trois(_suivi(900, 2), _suivi(400, 0, fin="la pose se contredit"), _suivi(900, 0, 1))
    perd = _trois(_suivi(900, 2), _suivi(400, 0, fin="la pose se contredit"), _suivi(900, 2, 1))
    egal = _trois(_suivi(900, 0), _suivi(900, 0), _suivi(900, 0))
    v("⭐⭐⭐⭐ la reprise RÉCUPÈRE quand elle livre plus d'utilisable que l'arrêt",
      recup["reprise_recupere"] is True and recup["reprise_perd"] is False,
      "900 utilisables contre 400")
    v("⭐⭐⭐⭐ ... et elle PERD quand elle va trop loin et se contamine",
      perd["reprise_perd"] is True and perd["reprise_recupere"] is False,
      "zéro utilisable contre les 400 que l'arrêt livrait, sûrs")
    v("⚠⚠ les deux ne peuvent pas être vraies ensemble, ni sur un départ identique",
      not (egal["reprise_recupere"] or egal["reprise_perd"]) and egal["identiques"] is True)

    print("\n— la victoire est JOINTE —")
    r = _resume([recup, egal])
    v("⭐⭐⭐⭐ elle l'emporte en récupérant au moins un départ ET en n'en perdant aucun",
      _cumuler([r], "un")["la_reprise_lemporte"] is True
      and r["reprise_recupere"] == 1 and r["reprise_perd"] == 0)
    # ⚠⚠⚠ CHAQUE MOITIE PRISE SEULE EST SATISFAITE PAR UN MARCHEUR INUTILE : celui qui ne se
    # reprend JAMAIS ne perd aucun depart, donc « aucune perte » seul ne vaut rien.
    jamais = _resume([egal, egal])
    v("⭐⭐⭐⭐ ... et un marcheur qui ne se reprend JAMAIS ne perd rien, ce qui ne suffit pas",
      _cumuler([jamais], "un")["la_reprise_lemporte"] is False
      and jamais["reprise_perd"] == 0,
      "la moitié qui flatte est satisfaite par l'inaction")
    v("⭐⭐⭐ ... et une seule perte la fait tomber, même avec des récupérations",
      _cumuler([_resume([recup, recup, perd])], "un")["la_reprise_lemporte"] is False)

    print("\n— les reprises épuisées sont comptées —")
    epuisee = _trois(_suivi(500, 9), _suivi(1, 0, fin="la pose se contredit"),
                     _suivi(1, 0, 6, "la pince ne peut plus avancer"))
    re = _resume([epuisee])
    v("⭐⭐⭐ une reprise qui s'épuise est COMPTÉE, pas confondue avec une reprise qui a marché",
      re["reprises_epuisees"] == 1 and re["reprises"] == 6,
      "six halvings, puis plus d'avance exprimable")
    v("⚠⚠ ... et une marche épuisée SANS s'être reprise n'est pas une reprise épuisée",
      _resume([_trois(_suivi(500, 0), _suivi(500, 0),
                      _suivi(500, 0, 0, "la pince ne peut plus avancer"))]
              )["reprises_epuisees"] == 0,
      "elle a buté sur la matière, pas sur ses propres reprises")
    v("⚠ sans un seul départ apparié, le résumé le DIT",
      _resume([None])["decidable"] is False)

    print("\n— le contrôle est une IDENTITÉ, pas une absence —")
    def case(nom, bras_, paires):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0,
                "bruit": 0.0, **_resume(paires)}
    bon = {"decidable": True, "bras": ["p"], "marcheurs": ["sourd", "sarrete", "se_reprend"],
           "bruits": [0.0], "departs": 2,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [egal, egal]),
                     case("dure", "p", [recup, egal])]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand les trois marcheurs livrent EXACTEMENT la même chose",
      j["le_controle_de_la_spirale_nue"]["il_est_identique"] is True)
    v("⭐⭐⭐⭐ ... et il TOMBE dès qu'un seul départ diffère, fût-ce d'un pas",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p",
                                   [egal, _trois(_suivi(900, 0), _suivi(900, 0),
                                                 _suivi(899, 0, 1))]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_identique"] is False,
      "un pas de moins suffit : c'est plus dur qu'un compte d'arrêts à zéro")
    # ⚠⚠⚠ ET LA MOITIE « IDENTIQUES » DOIT TOMBER TOUTE SEULE, sinon elle n'est pas testee : la
    # fixture precedente porte AUSSI une reprise, donc le compte de reprises suffisait. Ici la
    # marche qui S'ARRETE diffère, sans qu'aucune reprise n'ait eu lieu — ce qui voudrait dire que
    # quelque chose s'arrete la ou rien ne se contredit. C'est le meme trou que `164` a paye, et
    # je ne l'avais pas reporte.
    sournois = _trois(_suivi(900, 0), _suivi(800, 0, fin="la pose se contredit"),
                      _suivi(900, 0, 0))
    v("⭐⭐⭐⭐ ... et la moitié « identiques » tombe SEULE, sans aucune reprise pour l'aider",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [egal, sournois]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_identique"] is False
      and _resume([egal, sournois])["reprises"] == 0,
      "zéro reprise, et pourtant un départ qui diffère")
    v("⭐⭐⭐ la victoire se lit par matière, et la spirale nue ne la gagne pas",
      j["matieres_ou_la_reprise_lemporte"] == ["dure"],
      "rien à récupérer là où rien ne se contredit")
    # ⚠⚠⚠ ET LE CROISEMENT BRAS × MATIERE EXISTE, parce qu'un verdict par matiere met les bras en
    # commun : la mesure reelle montre la pince ne perdant AUCUN depart pendant que deux matieres
    # en affichent douze et quinze, tous venus de l'autre bras. C'est la leçon de `161`.
    deux_bras = {**bon, "bras": ["p", "s"],
                 "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [egal, egal]),
                           case("dure", "p", [recup, egal]),
                           case("dure", "s", [perd, egal])]}
    jc = juger(deux_bras)
    v("⭐⭐⭐⭐ le croisement bras × matière existe, et il sépare ce que la matière seule confond",
      jc["matieres_ou_la_reprise_lemporte_par_bras"]["p"] == ["dure"]
      and jc["matieres_ou_la_reprise_lemporte_par_bras"]["s"] == []
      and jc["matieres_ou_la_reprise_lemporte"] == [],
      "la matière « dure » ne gagne pour personne une fois les bras confondus, "
      "alors qu'elle gagne pour la pince")

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    v("⭐⭐⭐⭐ sur la spirale NUE la mesure réelle rend les trois marcheurs IDENTIQUES",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_identique"] is True,
      f"{petite['juger']['le_controle_de_la_spirale_nue']}")
    # ⚠⚠⚠ ET SUR UNE MATIERE QUI SE CONTREDIT, LA REPRISE DOIT REELLEMENT HALVER ET REESSAYER.
    # Sans ce controle la batterie ne l'exerçait JAMAIS sur donnees reelles — la spirale nue ne
    # declenche rien, donc debrancher le halving n'y changeait rien et la sonde par cassure
    # passait au vert. C'est exactement le trou que `164` avait paye.
    dure = mesurer(matieres=(MATIERES[3],), bruits=(8.0,), bras=(BRAS[0],), departs=1)
    cas_dur = dure["epreuve"]["cases"][0]
    v("⭐⭐⭐⭐ sur une matière qui se contredit, la reprise récupère ce que l'arrêt jetait",
      cas_dur["reprises"] >= 1
      and cas_dur["se_reprend"]["pas"] > cas_dur["sarrete"]["pas"],
      f"{cas_dur['reprises']} reprise(s), {cas_dur['sarrete']['pas']} pas en s'arrêtant "
      f"contre {cas_dur['se_reprend']['pas']} en se reprenant")
    # ⚠⚠⚠ ET LE CONTROLE PRECEDENT NE SEPARE PAS UNE REPRISE QUI HALVE D'UNE REPRISE QUI ACCEPTE :
    # les deux peuvent livrer le meme nombre de pas. Ce qui les separe est que la marche qui se
    # reprend doit DIFFERER de la marche SOURDE — sinon elle n'a rien fait d'autre que compter.
    # Sur la matiere du rouleau la difference est franche : la reprise s'y epuise.
    rouleau = mesurer(matieres=(MATIERES[4],), bruits=(8.0,), bras=(BRAS[0],), departs=1)
    cas_r = rouleau["epreuve"]["cases"][0]
    v("⭐⭐⭐⭐ ... et la marche qui se reprend DIFFÈRE de la marche sourde, sinon elle n'a rien fait",
      cas_r["reprises"] >= 1
      and (cas_r["se_reprend"]["pas"] != cas_r["sourd"]["pas"]
           or cas_r["se_reprend"]["contaminees"] != cas_r["sourd"]["contaminees"]),
      f"sourde {cas_r['sourd']['pas']} pas et {cas_r['sourd']['contaminees']} contaminée(s), "
      f"reprise {cas_r['se_reprend']['pas']} pas et "
      f"{cas_r['se_reprend']['contaminees']} contaminée(s)")

    avant = json.loads(json.dumps(petite["epreuve"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["epreuve"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "epreuve": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, les deux tableaux et le verdict",
      "contrôle" in sortie and "par bras" in sortie and "par matière" in sortie
      and "REPRISE" in sortie, f"{len(sortie)} caractères")
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
