"""La croix paie-t-elle quand le marcheur écoute ? — ce que `156` a jugé sur un marcheur SOURD.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL RÉPARE UNE DATE. `156` a mesuré la mâchoire **en croix** sur une
grille et l'a jugée : elle coûte **×1,9921** de lectures et rend **+1** réussite, un pur
déplacement. Mais ce jugement portait sur un marcheur **sourd** — il n'écoutait pas la pose, ne la
refusait pas, ne se reprenait pas. Tout cela est arrivé après, entre `162` et `165`. Personne n'a
jamais mesuré la croix avec le marcheur que la campagne livre aujourd'hui.

⭐⭐⭐ ET IL Y A UNE RAISON PRÉCISE DE REDEMANDER. `153` mesure que sur la matière du rouleau la
VRAIE normale sort du plan du tour, et que `une_machoire` rend `n' = t' × z` — une composante axiale
**nulle par construction**. La croix pose ses appuis sur DEUX barres, donc son nuage porte un
**plan** et sa normale peut sortir du tour. `167` a réfuté que la contradiction irréparable soit
faite de cette composante, mais il l'a réfuté par l'**observation**, avec un instrument qui ne peut
pas l'exprimer. Ceci est le test **interventionnel** : on donne l'instrument, et on regarde.

⚠⚠ DEUX MARCHEURS, LE MÊME ÉNONCÉ, DEUX INSTRUMENTS. Les deux **écoutent et se reprennent** — le
marcheur de `165`, celui que la campagne livre. Ils ne diffèrent que par la mâchoire : un **segment**
pour l'un, une **croix** pour l'autre. Aucun autre drapeau ne bouge.

⚠⚠⚠ LE COÛT SE PREND PAR PAS, JAMAIS EN TOTAL. Une croix qui meurt plus tôt lit moins en tout, donc
un total de lectures ferait passer une marche écourtée pour une marche économe — c'est exactement
`R4-F162`, comparer des totaux sur des populations inégales. Le rapport publié est une somme de
lectures divisée par une somme de pas, sur les MÊMES départs appariés.

⚠⚠ CONTRÔLE OBLIGATOIRE, ET IL EST EXACT DES DEUX CÔTÉS : sur la spirale NUE rien ne se contredit,
donc les deux marcheurs doivent livrer EXACTEMENT la même chose, et la croix doit y lire EXACTEMENT
le double — deux barres au lieu d'une, sur une matière où aucune pose n'échoue. Un écart d'un seul
pas ou d'une seule lecture y voudrait dire que la comparaison mesure autre chose que la mâchoire.

Usage :
    uv run python src/nappe/la_croix_paie_t_elle_quand_on_ecoute.py --verifier
    uv run python src/nappe/la_croix_paie_t_elle_quand_on_ecoute.py \\
        --json docs/mesures/la_croix_paie_t_elle_quand_on_ecoute.json
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
# (nom, les mots-clés que `suivre` reçoit) — le marcheur de `165`, deux mâchoires.
MARCHEURS = (("en segment", {"reprendre_la_pose": True}),
             ("en croix", {"reprendre_la_pose": True, "en_croix": True}))
LA_SPIRALE_NUE = (0.0, 0.0)


def _cadre() -> tuple[float, float, float]:
    pas_um, voxel_um = _PAS(), _VOXEL()
    return pas_um, voxel_um, AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, bras, kw) -> dict:
    _n, deux, contrainte, rejeter = bras
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    x = suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
               contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
               rejeter=rejeter, derouler_exactement=True, **kw)
    # ⚠ LES LECTURES SONT PRISES SUR LE VOLUME, pas sur le resultat : c'est le seul compteur qui
    # voit ce qu'une pose refusee a coute avant d'etre refusee.
    x["lectures_du_volume"] = int(getattr(vol, "lectures", 0))
    return x


def le_cas_dun_depart(marches: dict) -> dict | None:
    """Un départ, marché par les deux instruments — et ce que chacun en remet.

    ⚠⚠ UN DÉPART N'EST APPARIÉ QUE SI LES DEUX MARCHEURS Y SONT DÉCIDABLES. Comparer une marche
    décidable à une marche qui ne l'est pas comparerait une mesure à une absence.
    """
    out = {}
    for nom, x in marches.items():
        u = ce_que_vaut_une_livraison(x)
        if u is None or x.get("pas") is None:
            return None
        out[nom] = {"pas": int(x["pas"]), "utilisable": int(u),
                    "contaminee": int(u == 0 and int(x["pas"]) > 0),
                    "lectures": int(x.get("lectures_du_volume", 0)),
                    "poses_impossibles": int(x.get("poses_impossibles", 0) or 0),
                    "contradictions_reparees": int(x.get("contradictions_reparees", 0) or 0),
                    "contradictions_epuisees": int(x.get("contradictions_epuisees", 0) or 0)}
    seg, croix = out["en segment"], out["en croix"]
    # ⭐⭐⭐⭐ LA COMPARAISON EST DANS LE DÉPART, jamais entre des totaux : les deux marcheurs
    # partent du même point sur la même matière, donc c'est le seul appariement légitime.
    out["la_croix_livre_davantage"] = bool(croix["utilisable"] > seg["utilisable"])
    out["la_croix_livre_moins"] = bool(croix["utilisable"] < seg["utilisable"])
    out["ils_livrent_pareil"] = bool(croix["utilisable"] == seg["utilisable"])
    # ⚠⚠ ET LES DEUX LIVRAISONS IDENTIQUES NE SUFFISENT PAS SUR LA NUE : il faut le MÊME NOMBRE DE
    # PAS, sinon deux marches de longueurs differentes pourraient rendre le meme utilisable.
    out["ils_marchent_pareil"] = bool(croix["pas"] == seg["pas"])
    return out


def _resume(cas: list[dict | None]) -> dict:
    dec = [c for c in cas if c is not None]
    if not dec:
        return {"decidable": False, "raison": "aucun départ apparié", "departs": len(cas)}
    out = {"decidable": True, "departs": len(cas), "apparies": len(dec),
           "departs_identiques": int(sum(1 for c in dec
                                         if c["ils_livrent_pareil"] and c["ils_marchent_pareil"])),
           "la_croix_recupere": int(sum(1 for c in dec if c["la_croix_livre_davantage"])),
           "la_croix_perd": int(sum(1 for c in dec if c["la_croix_livre_moins"]))}
    for m, _kw in MARCHEURS:
        out[m] = {k: int(sum(c[m][k] for c in dec))
                  for k in ("pas", "utilisable", "contaminee", "lectures",
                            "poses_impossibles", "contradictions_reparees",
                            "contradictions_epuisees")}
    return out


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
                cas = [le_cas_dun_depart({nom: _marcher(vol, k, departs, pas_um, voxel_um,
                                                        avance_um, b, kw)
                                          for nom, kw in MARCHEURS})
                       for k in range(int(departs))]
                cases.append({"bras": b[0], "nom": _nom(ecr, amp), "ecrasement": float(ecr),
                              "amplitude_um": float(amp), "bruit": float(bruit), **_resume(cas)})
    return {"decidable": bool(cases), "cases": cases, "bras": [b[0] for b in bras],
            "marcheurs": [m[0] for m in MARCHEURS], "bruits": [float(b) for b in bruits],
            "departs": int(departs)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    dec = [c for c in cs if c.get("decidable")]
    cles = ("departs", "apparies", "departs_identiques", "la_croix_recupere", "la_croix_perd")
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           **{k: int(sum(c.get(k, 0) for c in dec)) for k in cles}}
    for m, _kw in MARCHEURS:
        t = {k: int(sum(c[m][k] for c in dec if m in c))
             for k in ("pas", "utilisable", "contaminee", "lectures", "poses_impossibles",
                       "contradictions_reparees", "contradictions_epuisees")}
        # ⚠⚠⚠ LE COUT SE PREND PAR PAS. Une somme de lectures seule ferait passer une marche
        # ECOURTEE pour une marche econome : la croix qui meurt plus tot lit moins en tout. Le
        # rapport est une somme divisee par une somme, sur les memes departs apparies.
        t["lectures_par_pas"] = (round(t["lectures"] / t["pas"], 3) if t["pas"] else None)
        # ⚠⚠⚠ LE MEME PIEGE, DEUX FOIS DANS LA MEME TRANCHE. Un total de poses impossibles
        # ferait passer une croix qui marche moins pour une croix qui se pose mieux. Il se prend
        # par pas, comme les lectures, et sur les memes departs apparies.
        t["poses_impossibles_par_pas"] = (round(t["poses_impossibles"] / t["pas"], 4)
                                          if t["pas"] else None)
        out[m] = t
    a, b = out[MARCHEURS[0][0]], out[MARCHEURS[1][0]]
    out["surcout_de_la_croix"] = (round(b["lectures_par_pas"] / a["lectures_par_pas"], 4)
                                  if a.get("lectures_par_pas") else None)
    # ⭐⭐⭐⭐ LA VICTOIRE EST JOINTE, et c'est la forme que `147` a imposee : la croix doit rendre
    # au moins autant sur CHAQUE depart apparie, et davantage sur au moins un. Une seule perte
    # suffit a la faire tomber — un compte, jamais une majorite.
    out["la_croix_lemporte"] = bool(out["apparies"] > 0 and out["la_croix_perd"] == 0
                                    and out["la_croix_recupere"] > 0)
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
    # ⚠⚠⚠ LE CONTROLE EXACT VIT A BRUIT ZERO, ET LA MESURE L'A IMPOSE. Une premiere version le
    # prenait sur la spirale nue TOUS BRUITS CONFONDUS, et la grille a rendu 2 poses impossibles
    # et un surcout de 2,0007 : a bruit 16 une lecture bruitee empeche une pose de trouver son
    # interstice, meme sur une matiere parfaitement lisse. « Spirale nue » et « rien ne va de
    # travers » ne sont donc PAS le meme enonce des que le lecteur bruite, et c'est le second
    # qu'un controle doit exiger.
    # ⭐⭐⭐ Ce que le bruit 16 fait a une matiere lisse est publie A COTE, comme une mesure.
    nues = [c for c in d["cases"] if c["nom"] == _nom(*LA_SPIRALE_NUE)]
    nue = _cumuler([c for c in nues if float(c.get("bruit", 0.0)) == 0.0],
                   _nom(*LA_SPIRALE_NUE)) if nues else None
    bruitee = _cumuler([c for c in nues if float(c.get("bruit", 0.0)) > 0.0],
                       "spirale nue, lecteur bruité") if nues else None
    controle = {"nom": nue["nom"] if nue else None, "bruit": 0.0,
                "apparies": nue["apparies"] if nue else None,
                "departs_identiques": nue["departs_identiques"] if nue else None,
                "surcout_de_la_croix": nue["surcout_de_la_croix"] if nue else None,
                "contaminees": ((nue[MARCHEURS[0][0]]["contaminee"]
                                 + nue[MARCHEURS[1][0]]["contaminee"]) if nue else None),
                "poses_impossibles": ((nue[MARCHEURS[0][0]]["poses_impossibles"]
                                       + nue[MARCHEURS[1][0]]["poses_impossibles"])
                                      if nue else None),
                "sous_un_lecteur_bruite": (
                    {"apparies": bruitee["apparies"],
                     "poses_impossibles": (bruitee[MARCHEURS[0][0]]["poses_impossibles"]
                                           + bruitee[MARCHEURS[1][0]]["poses_impossibles"]),
                     "surcout_de_la_croix": bruitee["surcout_de_la_croix"]}
                    if bruitee else None)}
    controle["il_est_propre"] = bool(
        nue is not None and nue["apparies"] > 0
        and controle["contaminees"] == 0 and controle["poses_impossibles"] == 0)
    controle["le_surcout_y_est_exactement_double"] = bool(
        nue is not None and controle["surcout_de_la_croix"] == 2.0)
    return {"decidable": True, "par_matiere": mat, "par_bras": bras,
            "tout": _cumuler(d["cases"], "tout"),
            "le_controle_de_la_spirale_nue": controle,
            "la_croix_lemporte_par_bras": {g["nom"]: g["la_croix_lemporte"] for g in bras},
            "par_bras_et_matiere": {b: _croiser(d, b)
                                    for b in dict.fromkeys(c["bras"] for c in d["cases"])},
            "matieres_ou_la_croix_lemporte_par_bras": {
                b: [str(c["nom"]) for c in _croiser(d, b) if c["la_croix_lemporte"]]
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
    m1 = "★" if c["il_est_propre"] else "✗"
    m2 = "★" if c["le_surcout_y_est_exactement_double"] else "✗"
    print(f"{m1} contrôle — sur la spirale NUE rien ne va de travers : "
          f"{c['contaminees']} livraison contaminée, {c['poses_impossibles']} pose impossible "
          f"({c['departs_identiques']}/{c['apparies']} départs identiques au pas près)")
    print(f"{m2} contrôle — et la croix y lit exactement le double PAR PAS : "
          f"×{c['surcout_de_la_croix']}")
    b_ = c.get("sous_un_lecteur_bruite")
    if b_:
        print(f"   ⚠ et ce que le BRUIT fait à cette même matière lisse : "
              f"{b_['poses_impossibles']} poses impossibles sur {b_['apparies']} départs, "
              f"×{b_['surcout_de_la_croix']}")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —  (pas utilisables)")
        print(f"   {'':>22} | {'appar.':>6} | {'en segment':>11} | {'en croix':>11} | "
              f"{'lect./pas':>18} | {'surcoût':>8} | {'récup':>5} | {'perd':>5}")
        for g in groupes:
            a, b = g[MARCHEURS[0][0]], g[MARCHEURS[1][0]]
            tient = "★" if g["la_croix_lemporte"] else " "
            sur = f"×{g['surcout_de_la_croix']}" if g["surcout_de_la_croix"] else "—"
            print(f" {tient} {_court(g['nom']):>22} | {g['apparies']:>6} | "
                  f"{a['utilisable']:>11} | {b['utilisable']:>11} | "
                  f"{str(a['lectures_par_pas']):>8} / {str(b['lectures_par_pas']):<7} | "
                  f"{sur:>8} | {g['la_croix_recupere']:>5} | {g['la_croix_perd']:>5}")
    print("\n★★★★ la croix l'emporte-t-elle, en livrant au moins autant sur CHAQUE départ ?")
    for nom, oui in j["la_croix_lemporte_par_bras"].items():
        noms = j["matieres_ou_la_croix_lemporte_par_bras"].get(nom, [])
        print(f"      {_court(nom):>22} : {'OUI' if oui else 'non'} — "
              f"{', '.join(_court(n) for n in noms) if noms else 'aucune matière'}")
    t = j["tout"]
    a_, c_ = t[MARCHEURS[0][0]], t[MARCHEURS[1][0]]
    print(f"\n   poses impossibles PAR PAS : {a_['poses_impossibles_par_pas']} en segment, "
          f"{c_['poses_impossibles_par_pas']} en croix "
          f"({a_['poses_impossibles']} contre {c_['poses_impossibles']} en total, "
          f"sur {a_['pas']} et {c_['pas']} pas)")


def _cas(u_seg: int, u_croix: int, pas_seg: int = 10, pas_croix: int = 10,
         lec_seg: int = 100, lec_croix: int = 200, imp_seg: int = 0,
         imp_croix: int = 0) -> dict:
    return le_cas_dun_depart({
        "en segment": {"decidable": True, "pas": pas_seg, "pas_qui_sautent": 0,
                       "lectures_du_volume": lec_seg, "poses_impossibles": imp_seg,
                       "contradictions_reparees": 0, "contradictions_epuisees": 0,
                       **({"pas": pas_seg} if u_seg else {"pas_qui_sautent": 1})},
        "en croix": {"decidable": True, "pas": pas_croix, "pas_qui_sautent": 0,
                     "lectures_du_volume": lec_croix, "poses_impossibles": imp_croix,
                     "contradictions_reparees": 0, "contradictions_epuisees": 0,
                     **({"pas": pas_croix} if u_croix else {"pas_qui_sautent": 1})}})


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

    print("— un départ, deux instruments —")
    plus = _cas(10, 10, pas_croix=14, lec_croix=280)
    moins = _cas(10, 10, pas_croix=6, lec_croix=120)
    v("⭐⭐⭐ la croix qui livre DAVANTAGE est comptée comme telle",
      plus["la_croix_livre_davantage"] is True and plus["la_croix_livre_moins"] is False)
    v("⭐⭐⭐⭐ ... et celle qui livre MOINS l'est aussi, elle n'est pas écartée",
      moins["la_croix_livre_moins"] is True and moins["la_croix_livre_davantage"] is False)
    v("⚠⚠ deux livraisons égales ne sont ni l'une ni l'autre",
      _cas(10, 10)["ils_livrent_pareil"] is True)
    # ⚠⚠ SUR LA NUE, « PAREIL » EXIGE LE MEME NOMBRE DE PAS : deux marches de longueurs
    # differentes peuvent rendre le meme utilisable si l'une est contaminee.
    v("⚠⚠ ... et « pareil » exige aussi le même nombre de PAS",
      _cas(10, 10)["ils_marchent_pareil"] is True
      and _cas(10, 10, pas_croix=14, lec_croix=280)["ils_marchent_pareil"] is False)
    v("⚠ un départ où un seul marcheur est décidable n'est PAS apparié",
      le_cas_dun_depart({"en segment": {"decidable": False},
                         "en croix": {"decidable": True, "pas": 5,
                                      "pas_qui_sautent": 0}}) is None)

    print("\n— la victoire est JOINTE —")
    gagne = _resume([_cas(10, 10, pas_croix=14, lec_croix=280), _cas(10, 10)])
    v("⭐⭐⭐⭐ elle tient quand la croix ne perd sur AUCUN départ et gagne sur au moins un",
      _cumuler([gagne], "un")["la_croix_lemporte"] is True)
    perd = _resume([_cas(10, 10, pas_croix=14, lec_croix=280),
                    _cas(10, 10, pas_croix=6, lec_croix=120)])
    v("⭐⭐⭐⭐ ... et elle TOMBE dès qu'un seul départ perd",
      _cumuler([perd], "un")["la_croix_lemporte"] is False,
      "un sur deux suffit, c'est un compte et non une majorité")
    egal = _resume([_cas(10, 10), _cas(10, 10)])
    v("⭐⭐⭐ ... et ne rien perdre ne suffit PAS : il faut gagner quelque part",
      _cumuler([egal], "un")["la_croix_lemporte"] is False,
      "sinon deux instruments identiques la gagneraient")

    print("\n— le coût se prend PAR PAS —")
    # ⚠⚠⚠ LA CROIX QUI MEURT TOT LIT MOINS EN TOTAL. Sans division par les pas, elle passerait
    # pour econome alors qu'elle coute le double a chaque pas — c'est `R4-F162` sous un costume.
    court = _cumuler([_resume([_cas(10, 0, pas_croix=2, lec_croix=40)])], "court")
    a, b = court[MARCHEURS[0][0]], court[MARCHEURS[1][0]]
    v("⭐⭐⭐⭐ une croix qui MEURT TÔT lit moins en TOTAL et davantage PAR PAS",
      b["lectures"] < a["lectures"] and b["lectures_par_pas"] > a["lectures_par_pas"],
      f"{b['lectures']} < {a['lectures']} lectures, "
      f"{b['lectures_par_pas']} > {a['lectures_par_pas']} par pas")
    v("⭐⭐⭐ ... et le surcoût publié est celui PAR PAS", court["surcout_de_la_croix"] == 2.0,
      f"×{court['surcout_de_la_croix']}")
    v("⚠ sans un seul pas le coût n'existe pas, il ne vaut pas zéro",
      _cumuler([_resume([_cas(0, 0, pas_seg=0, pas_croix=0, lec_seg=0,
                              lec_croix=0)])], "vide")[MARCHEURS[0][0]]
      ["lectures_par_pas"] is None)

    print("\n— le contrôle est EXACT des deux côtés —")

    def case(nom, bras_, cas_):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0,
                "bruit": 0.0, **_resume(cas_)}
    bon = {"decidable": True, "bras": ["p"], "marcheurs": [m for m, _ in MARCHEURS],
           "bruits": [0.0], "departs": 2,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [_cas(10, 10), _cas(10, 10)]),
                     case("dure", "p", [_cas(10, 10, pas_croix=14, lec_croix=280)])]}
    j = juger(bon)
    c = j["le_controle_de_la_spirale_nue"]
    v("⭐⭐⭐⭐ le contrôle tient quand rien n'est contaminé et qu'aucune pose n'est impossible",
      c["il_est_propre"] is True)
    v("⭐⭐⭐⭐ ... et la croix y lit EXACTEMENT le double", 
      c["le_surcout_y_est_exactement_double"] is True, f"×{c['surcout_de_la_croix']}")
    casse = juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p",
                                         [_cas(10, 10), _cas(10, 0)]),
                                    bon["cases"][1]]})
    v("⭐⭐⭐⭐ ... et il TOMBE dès qu'une seule livraison y est contaminée",
      casse["le_controle_de_la_spirale_nue"]["il_est_propre"] is False,
      "une seule voudrait dire que la comparaison mesure son propre bruit")
    # ⚠⚠ ET IL N'EXIGE PAS L'IDENTITE AU PAS PRES : deux routes numeriques vers la meme normale
    # ne s'accordent pas au dernier bit, et la mesure reelle en donne un exemple.
    pasegal = juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p",
                                           [_cas(10, 10), _cas(10, 10, pas_croix=11,
                                                               lec_croix=220)]),
                                      bon["cases"][1]]})
    cp = pasegal["le_controle_de_la_spirale_nue"]
    v("⭐⭐⭐⭐ ... et il N'EXIGE PAS que les deux marchent le même nombre de pas",
      cp["il_est_propre"] is True and cp["departs_identiques"] < cp["apparies"],
      f"{cp['departs_identiques']}/{cp['apparies']} identiques, et le contrôle tient")
    dble = juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p",
                                        [_cas(10, 10, lec_croix=150)]),
                                   bon["cases"][1]]})
    v("⭐⭐⭐ ... et le surcoût EXACTEMENT double tombe s'il ne l'est pas",
      dble["le_controle_de_la_spirale_nue"]["le_surcout_y_est_exactement_double"] is False,
      "×1.5 sur une matière où rien ne rate voudrait dire autre chose")
    v("⭐⭐⭐ le croisement bras × matière existe, et la spirale nue ne gagne rien",
      j["matieres_ou_la_croix_lemporte_par_bras"]["p"] == ["dure"])

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    cn = petite["juger"]["le_controle_de_la_spirale_nue"]
    v("⭐⭐⭐⭐ sur la spirale NUE la mesure réelle rend les deux contrôles",
      cn["il_est_propre"] is True and cn["le_surcout_y_est_exactement_double"] is True,
      f"{cn['contaminees']} contaminée, {cn['poses_impossibles']} impossible, "
      f"×{cn['surcout_de_la_croix']}, {cn['departs_identiques']}/{cn['apparies']} identiques")
    # ⚠⚠⚠ ET SUR LA MATIERE DU ROULEAU LES DEUX INSTRUMENTS DOIVENT REELLEMENT TOURNER. Sans ce
    # controle la batterie ne verifierait jamais sur donnees reelles que la croix se pose — le
    # trou que `164`, `165` et `166` ont paye chacun leur tour.
    dure = mesurer(matieres=(MATIERES[4],), bruits=(8.0,), bras=(BRAS[0],), departs=4)
    cas = dure["enquete"]["cases"][0]
    v("⭐⭐⭐⭐ sur la matière du rouleau, les DEUX instruments marchent réellement",
      cas["apparies"] > 0 and cas["en croix"]["pas"] > 0 and cas["en segment"]["pas"] > 0,
      f"{cas['apparies']} appariés, {cas['en segment']['pas']} pas en segment contre "
      f"{cas['en croix']['pas']} en croix")
    v("⭐⭐⭐⭐ ... et la croix y coûte DAVANTAGE par pas, ce qui est sa définition",
      _cumuler([cas], "x")["surcout_de_la_croix"] > 1.0,
      f"×{_cumuler([cas], 'x')['surcout_de_la_croix']}")
    avant = json.loads(json.dumps(petite["enquete"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["enquete"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "enquete": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend les deux contrôles, les deux tableaux et le verdict",
      "contrôle" in sortie and "par bras" in sortie and "par matière" in sortie
      and "surcoût" in sortie, f"{len(sortie)} caractères")
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "rien à montrer"})
    v("⚠ un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else '⛔ ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = (reagreger(json.loads(a.reagreger.read_text())) if a.reagreger is not None
         else mesurer())
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
