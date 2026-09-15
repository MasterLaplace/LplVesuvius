"""Réessayer AILLEURS plutôt que plus court — ce que `165` laissait ouvert.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET DEUX FAITS ÉTABLIS LE DÉSIGNENT. `165` mesure que raccourcir le pas
répare une pose qui se contredit **quand la contradiction vient d'un pas allé trop loin**, et qu'elle
**s'épuise** sur la matière du rouleau — la pince y bute **21** fois sous le voxel. Or `148` mesure
que le cap y incline la normale de plus de quarante degrés : la mâchoire cherche son interstice **de
travers**, et aucune longueur de pas ne corrige une **direction**.

⭐⭐⭐ L'AUTRE DIRECTION N'EST PAS CHOISIE, ELLE EST DÉJÀ LÀ. `suivre` connaît deux normales : celle
que le **cap** a décidée, et la dernière que la **matière** a rendue. Le mode `pose_sur_la_lecture`
emploie la seconde en permanence ; ici on emploie celle que le mode **n'emploie pas**, et seulement
quand la pose se contredit. Deux directions exactes, aucun angle choisi.

⚠⚠ L'ORDRE EST DÉLIBÉRÉ : d'abord l'autre direction **au même pas**, seulement ensuite raccourcir.
Raccourcir d'abord jetterait de la longueur pour un défaut qui n'en vient pas, et `165` mesure que
ce défaut existe.

⚠⚠⚠ ET CELA PEUT COÛTER. Une pose posée le long d'une autre normale n'est pas la même pose : elle
peut se poser plus loin, donc changer de feuille là où raccourcir aurait tenu. La victoire est
**jointe** — au moins un départ récupéré, aucun perdu — et elle se compare au marcheur de `165`, pas
au sourd.

⚠⚠ CONTRÔLE OBLIGATOIRE : sur la spirale NUE rien ne se contredit, donc les **trois** marcheurs
livrent exactement la même chose et l'autre direction n'est **jamais** essayée.

Usage :
    uv run python src/nappe/reessayer_ailleurs_plutot_que_plus_court.py --verifier
    uv run python src/nappe/reessayer_ailleurs_plutot_que_plus_court.py \\
        --json docs/mesures/reessayer_ailleurs_plutot_que_plus_court.json
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
# ⚠ Le marcheur de reference n'est PAS le sourd mais celui de `165` : la question est ce que
# l'autre direction ajoute a ce qui est deja acquis, jamais ce qu'elle ajoute a rien.
MARCHEURS = (("sourd", {}),
             ("plus_court", {"reprendre_la_pose": True}),
             ("ailleurs", {"reprendre_la_pose": True, "reprendre_ailleurs": True}))
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


def _apparier(marches: dict) -> dict | None:
    """Un départ, marché trois fois, et ce que chacun remet."""
    out = {}
    for nom, x in marches.items():
        u = ce_que_vaut_une_livraison(x)
        if u is None:
            return None
        out[nom] = {"pas": int(x["pas"]), "utilisable": u,
                    "contaminee": bool(int(x.get("pas_qui_sautent", 0)) > 0),
                    "raccourcissements": int(x.get("poses_reprises", 0)),
                    "detours": int(x.get("poses_reprises_ailleurs", 0)),
                    "epuisee": bool(x.get("fin") == "la pince ne peut plus avancer")}
    # ⚠⚠ LA COMPARAISON EST CONTRE `165`, PAS CONTRE LE SOURD : la question est ce que l'autre
    # direction AJOUTE a ce qui est deja acquis.
    c, a = out["plus_court"], out["ailleurs"]
    out["le_detour_recupere"] = bool(a["utilisable"] > c["utilisable"])
    out["le_detour_perd"] = bool(a["utilisable"] < c["utilisable"])
    out["identiques"] = bool(len({m["pas"] for m in out.values()
                                  if isinstance(m, dict)}) == 1)
    return out


def _resume(paires: list[dict]) -> dict:
    ps = [p for p in paires if p is not None]
    if not ps:
        return {"decidable": False, "raison": "aucun départ apparié", "departs": len(paires)}
    out = {"decidable": True, "departs": len(paires), "apparies": len(ps),
           "departs_identiques": int(sum(1 for p in ps if p["identiques"])),
           "detours": int(sum(p["ailleurs"]["detours"] for p in ps)),
           # ⚠ Les detours du marcheur de `165` DOIVENT valoir zero : il n'a pas cette faculte.
           # Le publier est un controle, pas une redondance.
           "detours_du_plus_court": int(sum(p["plus_court"]["detours"] for p in ps)),
           "le_detour_recupere": int(sum(1 for p in ps if p["le_detour_recupere"])),
           "le_detour_perd": int(sum(1 for p in ps if p["le_detour_perd"])),
           "epuisees_plus_court": int(sum(1 for p in ps if p["plus_court"]["epuisee"])),
           "epuisees_ailleurs": int(sum(1 for p in ps if p["ailleurs"]["epuisee"]))}
    for nom in ("sourd", "plus_court", "ailleurs"):
        out[nom] = {"pas": int(sum(p[nom]["pas"] for p in ps)),
                    "utilisable": int(sum(p[nom]["utilisable"] for p in ps)),
                    "contaminees": int(sum(1 for p in ps if p[nom]["contaminee"])),
                    "raccourcissements": int(sum(p[nom]["raccourcissements"] for p in ps))}
    return out


def lepreuve(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
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
    cles = ("apparies", "departs_identiques", "detours", "detours_du_plus_court",
            "le_detour_recupere", "le_detour_perd", "epuisees_plus_court", "epuisees_ailleurs")
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           **{k: int(sum(c.get(k, 0) for c in dec)) for k in cles}}
    for m in ("sourd", "plus_court", "ailleurs"):
        parts = [c[m] for c in dec if c.get(m) is not None]
        out[m] = ({k: int(sum(p[k] for p in parts))
                   for k in ("pas", "utilisable", "contaminees", "raccourcissements")}
                  if parts else None)
    out["le_detour_lemporte"] = bool(out["le_detour_recupere"] > 0 and out["le_detour_perd"] == 0)
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_bras(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["bras"] == b], b)
            for b in dict.fromkeys(c["bras"] for c in d["cases"])]


def _croiser(d: dict, bras: str) -> list[dict]:
    """Les groupes matière d'UN SEUL bras — le croisement que `161` a rendu obligatoire."""
    cases = [c for c in d["cases"] if c["bras"] == bras]
    return [_cumuler([c for c in cases if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in cases)]


def juger(d: dict) -> dict:
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, bras = par_matiere(d), par_bras(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    # ⚠⚠⚠ LE CONTROLE A TROIS MOITIES, et la troisieme est neuve : les trois marcheurs doivent
    # livrer la MEME chose, aucun detour ne doit y etre tente, et le marcheur de `165` ne doit
    # JAMAIS en compter — il n'a pas cette faculte, donc un detour chez lui voudrait dire que le
    # compteur fuit d'un marcheur a l'autre.
    controle = {"nom": nue["nom"] if nue else None,
                "departs_identiques": nue["departs_identiques"] if nue else None,
                "apparies": nue["apparies"] if nue else None,
                "detours": nue["detours"] if nue else None}
    controle["il_est_identique"] = bool(
        nue is not None and controle["apparies"] > 0
        and controle["departs_identiques"] == controle["apparies"]
        and controle["detours"] == 0)
    tout = _cumuler(d["cases"], "tout")
    return {"decidable": True, "par_matiere": mat, "par_bras": bras, "tout": tout,
            "le_controle_de_la_spirale_nue": controle,
            # ⚠⚠ UN COMPTEUR QUI FUIT D'UN MARCHEUR A L'AUTRE rendrait toute la comparaison
            # illisible, et rien d'autre ne le verrait.
            "le_plus_court_ne_detourne_jamais": bool(tout["detours_du_plus_court"] == 0),
            "le_detour_lemporte_par_bras": {g["nom"]: g["le_detour_lemporte"] for g in bras},
            "par_bras_et_matiere": {b: _croiser(d, b)
                                    for b in dict.fromkeys(c["bras"] for c in d["cases"])},
            "matieres_ou_le_detour_lemporte_par_bras": {
                b: [str(c["nom"]) for c in _croiser(d, b) if c["le_detour_lemporte"]]
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
    print(f"{marque} contrôle — sur la spirale NUE : {c['departs_identiques']}/{c['apparies']} "
          f"départs identiques, {c['detours']} détour tenté")
    fuite = "★" if j["le_plus_court_ne_detourne_jamais"] else "✗"
    print(f"{fuite} contrôle — le marcheur de `165` ne compte JAMAIS de détour "
          f"({j['tout']['detours_du_plus_court']})")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —  (pas utilisables · contaminées)")
        entetes = ("sourd", "plus court", "ailleurs")
        print(f"   {'':>22} | " + " | ".join(f"{h:>16}" for h in entetes)
              + f" | {'récup':>5} | {'perd':>4} | {'détours':>7}")
        for g in groupes:
            cells = [f"{g[m]['utilisable']:>9} · {g[m]['contaminees']:<4}"
                     if g.get(m) else f"{'—':>16}"
                     for m in ("sourd", "plus_court", "ailleurs")]
            tient = "★" if g["le_detour_lemporte"] else " "
            print(f" {tient} {_court(g['nom']):>22} | " + " | ".join(cells)
                  + f" | {g['le_detour_recupere']:>5} | {g['le_detour_perd']:>4} | "
                  f"{g['detours']:>7}")
    print("\n★★★★ où le DÉTOUR l'emporte sur le simple raccourcissement :")
    for nom, gagne in j["le_detour_lemporte_par_bras"].items():
        noms = j["matieres_ou_le_detour_lemporte_par_bras"].get(nom, [])
        print(f"      {_court(nom):>22} : {'OUI' if gagne else 'non'} en tout — "
              f"{', '.join(_court(n) for n in noms) if noms else 'aucune matière'}")
    t = j["tout"]
    print(f"\n   épuisements : {t['epuisees_plus_court']} en raccourcissant, "
          f"{t['epuisees_ailleurs']} en détournant")


def _suivi(pas: int, saute: int = 0, rac: int = 0, det: int = 0,
           fin: str = "tour bouclé") -> dict:
    return {"decidable": True, "pas": int(pas), "pas_qui_sautent": int(saute),
            "poses_reprises": int(rac), "poses_reprises_ailleurs": int(det), "fin": fin}


def _trois(sourd, court, ailleurs) -> dict | None:
    return _apparier({"sourd": sourd, "plus_court": court, "ailleurs": ailleurs})


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415
    import statistics  # noqa: PLC0415,F401

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    print("— la comparaison est contre `165`, jamais contre le sourd —")
    recup = _trois(_suivi(900, 5), _suivi(100, 0, 9), _suivi(400, 0, 4, 6))
    perd = _trois(_suivi(900, 5), _suivi(400, 0, 4), _suivi(900, 2, 2, 8))
    egal = _trois(_suivi(900, 0), _suivi(900, 0), _suivi(900, 0))
    v("⭐⭐⭐⭐ le détour RÉCUPÈRE quand il livre plus d'utilisable que le raccourcissement seul",
      recup["le_detour_recupere"] is True and recup["le_detour_perd"] is False,
      "400 contre 100, et le sourd n'entre pas dans la comparaison")
    v("⭐⭐⭐⭐ ... et il PERD quand il va plus loin et se contamine",
      perd["le_detour_perd"] is True and perd["le_detour_recupere"] is False,
      "zéro utilisable contre les 400 sûrs du raccourcissement")
    v("⚠⚠ le SOURD ne décide de rien, même quand il livre le plus de pas",
      recup["sourd"]["pas"] == 900 and recup["sourd"]["utilisable"] == 0
      and recup["le_detour_recupere"] is True,
      "900 pas contaminés valent zéro, et ne changent pas le verdict")
    v("⚠ les deux issues sont exclusives, et un départ identique n'en est aucune",
      not (egal["le_detour_recupere"] or egal["le_detour_perd"])
      and egal["identiques"] is True)

    print("\n— le compteur de détours ne fuit pas d'un marcheur à l'autre —")
    r = _resume([recup, egal])
    v("⭐⭐⭐⭐ le marcheur qui raccourcit seul ne compte JAMAIS de détour",
      r["detours_du_plus_court"] == 0 and r["detours"] == 6,
      "sinon le compteur fuirait et la comparaison serait illisible")
    fuite = _resume([_trois(_suivi(900, 0), _suivi(900, 0, 2, 3), _suivi(900, 0, 1, 4))])
    v("⭐⭐⭐ ... et une fuite se VOIT, elle ne se devine pas",
      fuite["detours_du_plus_court"] == 3)

    print("\n— la victoire est JOINTE —")
    v("⭐⭐⭐⭐ elle l'emporte en récupérant au moins un départ ET en n'en perdant aucun",
      _cumuler([r], "un")["le_detour_lemporte"] is True)
    v("⭐⭐⭐⭐ ... et un détour qui n'est JAMAIS tenté ne perd rien, ce qui ne suffit pas",
      _cumuler([_resume([egal, egal])], "un")["le_detour_lemporte"] is False,
      "la moitié qui flatte est satisfaite par l'inaction")
    v("⭐⭐⭐ ... et une seule perte la fait tomber",
      _cumuler([_resume([recup, recup, perd])], "un")["le_detour_lemporte"] is False)

    print("\n— les épuisements sont comptés des DEUX côtés —")
    ep = _resume([_trois(_suivi(900, 5), _suivi(19, 0, 26, 0, "la pince ne peut plus avancer"),
                         _suivi(54, 0, 53, 71, "la pince ne peut plus avancer"))])
    v("⭐⭐⭐ un épuisement se compte pour chaque marcheur, pas une fois pour les deux",
      ep["epuisees_plus_court"] == 1 and ep["epuisees_ailleurs"] == 1,
      "c'est leur comparaison qui dit si le détour repousse le mur")
    v("⚠ sans un seul départ apparié, le résumé le DIT",
      _resume([None])["decidable"] is False)

    print("\n— le contrôle a TROIS moitiés —")
    def case(nom, bras_, paires):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0,
                "bruit": 0.0, **_resume(paires)}
    bon = {"decidable": True, "bras": ["p"], "marcheurs": ["sourd", "plus_court", "ailleurs"],
           "bruits": [0.0], "departs": 2,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [egal, egal]),
                     case("dure", "p", [recup, egal])]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand les trois livrent la même chose et qu'aucun détour n'est tenté",
      j["le_controle_de_la_spirale_nue"]["il_est_identique"] is True
      and j["le_plus_court_ne_detourne_jamais"] is True)
    sournois = _trois(_suivi(900, 0), _suivi(800, 0, 1), _suivi(900, 0))
    v("⭐⭐⭐⭐ ... et la moitié « identiques » tombe SEULE, sans aucun détour pour l'aider",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [egal, sournois]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_identique"] is False
      and _resume([egal, sournois])["detours"] == 0,
      "zéro détour, et pourtant un départ qui diffère")
    v("⭐⭐⭐⭐ ... et la moitié « détours » tombe SEULE, sans qu'aucun départ ne diffère",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p",
                                   [egal, _trois(_suivi(900, 0), _suivi(900, 0),
                                                 _suivi(900, 0, 0, 3))]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_identique"] is False,
      "même nombre de pas, et pourtant trois détours tentés là où rien ne se contredit")
    v("⭐⭐⭐ le croisement bras × matière existe et sépare ce que la matière confond",
      j["matieres_ou_le_detour_lemporte_par_bras"]["p"] == ["dure"])

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    v("⭐⭐⭐⭐ sur la spirale NUE la mesure réelle ne tente AUCUN détour",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_identique"] is True,
      f"{petite['juger']['le_controle_de_la_spirale_nue']}")
    # ⚠⚠⚠ ET SUR UNE MATIERE QUI SE CONTREDIT, LE DETOUR DOIT REELLEMENT ETRE TENTE. Sans ce
    # controle la batterie ne l'exercerait JAMAIS sur donnees reelles — c'est le trou que `164` et
    # `165` ont paye tous les deux.
    # ⚠⚠ LA FIXTURE EST DIMENSIONNEE SUR L'EFFET : a UN seul depart, le detour est bien tente six
    # fois et ne change RIEN — ce qui est une mesure, pas un defaut. Il faut quatre departs pour
    # que la difference existe, et l'assertion porte alors sur ce qui bouge reellement.
    dure = mesurer(matieres=(MATIERES[4],), bruits=(8.0,), bras=(BRAS[0],), departs=4)
    cas = dure["epreuve"]["cases"][0]
    v("⭐⭐⭐⭐ sur une matière qui se contredit, le détour est réellement tenté",
      cas["detours"] >= 1 and cas["detours_du_plus_court"] == 0,
      f"{cas['detours']} détours tentés, {cas['detours_du_plus_court']} chez celui qui raccourcit")
    v("⭐⭐⭐⭐ ... et il CHANGE la marche, sinon il n'a fait que compter",
      cas["ailleurs"]["pas"] != cas["plus_court"]["pas"]
      or cas["ailleurs"]["contaminees"] != cas["plus_court"]["contaminees"],
      f"raccourci {cas['plus_court']['pas']} pas, détourné {cas['ailleurs']['pas']} pas")
    # ⚠⚠⚠ UN CONTROLE NE DOIT PAS REVENDIQUER PLUS QU'IL NE PROUVE, et j'ai failli en ecrire un.
    # Il s'appelait « le detour garde le MEME pas » et comparait les raccourcissements : or une
    # sonde qui fait halver le detour AUSSI rend ce compte plus BAS encore (11 → 5 sain, 11 → 0
    # casse), donc l'assertion passait des deux cotes. Mesure a l'appui, pas raisonnement.
    #
    # ⚠⚠ LA LIMITE EST NOMMEE PLUTOT QUE CONTOURNEE : une batterie de bout en bout ne peut PAS
    # distinguer un detour pris a pleine avance d'un detour pris a demi-avance, parce que les deux
    # produisent des marches egalement plausibles — seule la comparaison de DEUX versions du code
    # les separe, et une batterie n'a qu'une version. Ce qui est asserte ici est donc ce qui est
    # reellement observable : un detour EPARGNE des raccourcissements.
    moyenne = mesurer(matieres=(MATIERES[2],), bruits=(8.0,), bras=(BRAS[0],), departs=4)
    cm = moyenne["epreuve"]["cases"][0]
    v("⭐⭐⭐ un détour ÉPARGNE des raccourcissements — ce qui est observable, et rien de plus",
      cm["detours"] >= 1
      and cm["ailleurs"]["raccourcissements"] < cm["plus_court"]["raccourcissements"],
      f"{cm['plus_court']['raccourcissements']} raccourcissements sans détour, "
      f"{cm['ailleurs']['raccourcissements']} avec, pour {cm['detours']} détours")
    avant = json.loads(json.dumps(petite["epreuve"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["epreuve"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "epreuve": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend les deux contrôles, les deux tableaux et le verdict",
      sortie.count("contrôle") >= 2 and "par bras" in sortie and "par matière" in sortie
      and "DÉTOUR" in sortie and "épuisements" in sortie, f"{len(sortie)} caractères")
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
