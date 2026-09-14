"""Le déroulage de la phase suppose ce qu'on voudrait lui demander.

⚠⚠⚠ POURQUOI CE FICHIER. `158` laisse une question exacte : les quatre feuilles que treize marches
perdent en bouclant leur tour sont-elles un FLUAGE ou des SAUTS ? La série de phases de `suivre` y
répond « zéro saut », et la réponse est **fabriquée par l'instrument** : le déroulage fait
`d - round(d)`, donc il choisit l'entier qui rend chaque pas le plus PETIT et replie d'office tout
pas franchissant plus d'une demi-feuille. Demander à cette série si un pas dépasse la demi-feuille,
c'est demander à une règle graduée jusqu'à cinquante centimètres si quelque chose dépasse cinquante
centimètres. Sa propre docstring le dit d'ailleurs comme une HYPOTHÈSE.

⭐⭐⭐⭐ ET L'ENTIER SE LIT, IL NE SE DEVINE PAS. La phase vaut
`(u - r0)/pas + froissement/pas - theta/2pi` : sa SEULE coupure est en `theta`, et le pas angulaire
d'une marche vaut l'avance sur le rayon — de l'ordre du centième de radian, donc sans aucune
ambiguïté. L'entier à ajouter se lit sur l'angle. ⚠⚠ Et il faut l'angle que la FIXTURE emploie :
sur une section écrasée `cylindriques` rend un angle ELLIPTIQUE, et prendre l'angle circulaire du
compteur de tour serait faux exactement sur la matière qui compte.

⭐⭐⭐ ET C'EST UN ARBITRE QUI TRANCHE, PAS UN RAISONNEMENT. Trois raisonnements successifs se sont
contredits ici — la borne de l'avance disait qu'un pas de deux feuilles est impossible, le
recentrage des mâchoires disait que si, l'écrasement disait peut-être. L'arbitre échantillonne le
segment entre deux centres jusqu'à ce que la réponse cesse de bouger : un chemin assez fin n'a aucun
entier à choisir. Le nombre d'échantillons se DOUBLE au lieu d'être posé, sinon ce serait un seuil.

⚠⚠ ET CE FICHIER MESURE AUSSI CE QUE LA CORRECTION CHANGE À CE QUI EST DÉJÀ PUBLIÉ. Publier un
déroulage exact sans dire ce qu'il déplace serait la moitié d'un travail.

Usage :
    uv run python src/nappe/le_deroulage_suppose_ce_quon_lui_demande.py --verifier
    uv run python src/nappe/le_deroulage_suppose_ce_quon_lui_demande.py \\
        --json docs/mesures/le_deroulage_suppose_ce_quon_lui_demande.json
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
                                            RAYON_MM, _matiere, _nom, _PAS, _VOXEL, suivre,
                                            un_depart)

BRUITS = (0.0, 8.0, 16.0)
DEPARTS = 12
TOURS = 1.0
FENETRE = 32
# (nom, deux, contrainte, rejeter) — la barre de `144`, puis les deux instruments de `156` dont
# `157` a comparé les totaux.
REGLES = (("la pince de `144`", True, True, False),
          ("la pince avec rejet", True, True, True),
          ("une mâchoire avec rejet", False, False, True))
# ⚠ Les départs sur lesquels l'arbitre est lancé : il coûte cher et ne sert qu'à TRANCHER, donc il
# tourne sur un échantillon NOMMÉ plutôt que sur la grille entière. Ils sont pris tous les quatre
# départs pour couvrir le tour, et non choisis après coup.
DEPARTS_ARBITRES = (0, 4, 8)
LA_DEMI_FEUILLE = 0.5


def _cadre():
    return _PAS(), _VOXEL(), AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _une_marche(vol, k, departs, pas_um, voxel_um, avance_um, regle, arbitre=False):
    _nom_, deux, contrainte, rejeter = regle
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True, juger_le_deroulage=bool(arbitre))


def _reussite(x, cle: str) -> bool:
    """La réussite JOINTE, lue sur l'une OU l'AUTRE dérive.

    ⚠⚠ Le prédicat n'est pas réécrit : c'est celui du module partagé, avec la dérive qu'on lui
    donne. Un second prédicat divergerait de `une_reussite` au premier changement, et c'est lui qui
    décide de tout depuis `143`.
    """
    d = x.get(cle)
    return bool(x.get("decidable") and x.get("tour_boucle") and d is not None
                and abs(float(d)) < LA_DEMI_FEUILLE)


def la_portee(matieres=MATIERES, bruits=BRUITS, regles=REGLES, departs: int = DEPARTS) -> dict:
    """OÙ le déroulage se trompe, et ce que la correction change aux comptes déjà publiés.

    ⚠⚠ LES DEUX QUESTIONS SE MESURENT DANS LA MÊME PASSE, et c'est voulu : « combien de pas sont
    repliés à tort » et « combien de réussites cela déplace » sont deux lectures d'une même marche,
    et les séparer ferait marcher deux fois pour rien.

    ⚠ La réussite est comptée SOUS LES DEUX dérives sur le MÊME départ, donc l'appariement est
    exact par construction et ne coûte rien.
    """
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    cases = []
    for nom_regle, deux, contrainte, rejeter in regles:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                dec = touchees = replies = 0
                r_replie = r_exact = 0
                plus_grand = 0.0
                for k in range(int(departs)):
                    x = _une_marche(vol, k, departs, pas_um, voxel_um, avance_um,
                                    (nom_regle, deux, contrainte, rejeter))
                    if not x.get("decidable"):
                        continue
                    dec += 1
                    n = int(x.get("pas_replies_a_tort", 0))
                    replies += n
                    touchees += 1 if n else 0
                    r_replie += 1 if _reussite(x, "derive_en_feuilles") else 0
                    r_exact += 1 if _reussite(x, "derive_exacte_en_feuilles") else 0
                    if x.get("plus_grand_pas_en_feuilles") is not None:
                        plus_grand = max(plus_grand, float(x["plus_grand_pas_en_feuilles"]))
                cases.append({"regle": nom_regle, "nom": _nom(ecr, amp),
                              "ecrasement": float(ecr), "amplitude_um": float(amp),
                              "bruit": float(bruit), "departs": int(departs),
                              "decidables": dec, "marches_touchees": touchees,
                              "pas_replies_a_tort": replies,
                              "reussites_repliees": r_replie, "reussites_exactes": r_exact,
                              "plus_grand_pas_en_feuilles": round(plus_grand, 6)})
    return {"decidable": bool(cases), "cases": cases,
            "regles": [r[0] for r in regles], "bruits": [float(b) for b in bruits],
            "departs": int(departs)}


def larbitre(matieres=MATIERES, bruits=BRUITS, regles=REGLES,
             departs_arbitres=DEPARTS_ARBITRES, departs: int = DEPARTS) -> dict:
    """Lequel des deux déroulages la MATIÈRE soutient-elle, pas à pas et sans rien supposer.

    ⚠⚠⚠ C'EST LE SEUL CONTRÔLE QUI PUISSE TRANCHER, parce qu'il ne choisit aucun entier : un chemin
    échantillonné assez finement change de phase par sous-pas bien en deçà d'une demi-feuille, et
    l'entier de chaque sous-pas est alors sans ambiguïté. Le raisonnement, lui, a produit trois
    réponses contradictoires ici.

    ⚠ Un cas sans litige ne compte ni pour ni contre : il est SAUTÉ et non compté comme un accord,
    sans quoi la grande majorité des marches — celles où les deux déroulages disent la même chose —
    noierait le verdict sous des unanimités qui ne tranchent rien.
    """
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    lignes = []
    for nom_regle, deux, contrainte, rejeter in regles:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                for k in departs_arbitres:
                    x = _une_marche(vol, k, departs, pas_um, voxel_um, avance_um,
                                    (nom_regle, deux, contrainte, rejeter), arbitre=True)
                    n = int(x.get("pas_litigieux", 0)) if x.get("decidable") else 0
                    if not n:
                        continue
                    lignes.append({
                        "regle": nom_regle, "nom": _nom(ecr, amp), "bruit": float(bruit),
                        "depart_deg": round(360.0 * k / int(departs), 1), "litiges": n,
                        "pour_lexact": int(x["litiges_que_le_chemin_donne_a_lexact"]),
                        "pour_le_replie": int(x["litiges_que_le_chemin_donne_au_replie"]),
                        "non_tranches": int(x.get("litiges_non_tranches", 0)),
                        "plus_grand_pas_mesure_en_feuilles":
                            x["plus_grand_pas_mesure_en_feuilles"]})
    if not lignes:
        return {"decidable": False, "raison": "aucun pas litigieux à arbitrer"}
    return {"decidable": True, "cas": lignes,
            "litiges": int(sum(y["litiges"] for y in lignes)),
            "pour_lexact": int(sum(y["pour_lexact"] for y in lignes)),
            "pour_le_replie": int(sum(y["pour_le_replie"] for y in lignes)),
            # ⚠⚠ LES PAS QUE L'ARBITRE N'A PAS TRANCHES SONT PUBLIES, jamais rangés d'un côté :
            # son plafond est déclaré, donc son atteinte doit l'être aussi.
            "non_tranches": int(sum(y["non_tranches"] for y in lignes)),
            "marches_arbitrees": len(lignes),
            "le_chemin_donne_raison_a_lexact": bool(
                sum(y["pour_le_replie"] for y in lignes) == 0
                and sum(y["pour_lexact"] for y in lignes) > 0)}


def juger(portee: dict, arbitre: dict) -> dict:
    """Ce que la correction déplace, règle par règle — et ce qu'elle ne déplace pas.

    ⚠⚠ UNE BARRE QUI NE BOUGE PAS EST UN RÉSULTAT AUSSI FORT QU'UNE BARRE QUI BOUGE, et il se
    publie avec le compte de marches TOUCHÉES à côté : « rien n'a bougé » sur zéro marche touchée ne
    dit rien, sur cinquante-quatre il dit que le défaut n'atteint pas ce verdict-là.
    """
    if not portee.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    par_regle = []
    for nom in portee["regles"]:
        cs = [c for c in portee["cases"] if c["regle"] == nom]
        if not cs:
            continue
        par_regle.append({
            "regle": nom,
            "decidables": int(sum(c["decidables"] for c in cs)),
            "marches_touchees": int(sum(c["marches_touchees"] for c in cs)),
            "pas_replies_a_tort": int(sum(c["pas_replies_a_tort"] for c in cs)),
            "reussites_repliees": int(sum(c["reussites_repliees"] for c in cs)),
            "reussites_exactes": int(sum(c["reussites_exactes"] for c in cs)),
            "la_correction_deplace": int(sum(c["reussites_exactes"] for c in cs)
                                         - sum(c["reussites_repliees"] for c in cs)),
            "plus_grand_pas_en_feuilles": round(
                max(c["plus_grand_pas_en_feuilles"] for c in cs), 6)})
    # ⭐⭐ LES MATIÈRES QUE LE DÉFAUT N'ATTEINT PAS, lues et non choisies : celles dont aucune marche
    # n'est touchée, sous aucune règle et aucun bruit. C'est la borne de portée du défaut.
    intactes = sorted({c["nom"] for c in portee["cases"]}
                      - {c["nom"] for c in portee["cases"] if c["marches_touchees"]})
    sans_bruit = [c for c in portee["cases"] if c["bruit"] == 0.0 and c["marches_touchees"]]
    return {"decidable": True, "par_regle": par_regle,
            "matieres_intactes": intactes,
            "matieres_touchees_sans_bruit": sorted({c["nom"] for c in sans_bruit}),
            "la_barre_de_144_bouge": bool(
                par_regle and par_regle[0]["la_correction_deplace"] != 0),
            "une_machoire_passe_derriere_la_pince": bool(
                len(par_regle) >= 3
                and par_regle[2]["reussites_repliees"] > par_regle[1]["reussites_repliees"]
                and par_regle[2]["reussites_exactes"] < par_regle[1]["reussites_exactes"]),
            "larbitre": {k: arbitre.get(k) for k in
                         ("decidable", "litiges", "pour_lexact", "pour_le_replie",
                          "non_tranches", "marches_arbitrees",
                          "le_chemin_donne_raison_a_lexact")}}


def mesurer(matieres=MATIERES, bruits=BRUITS, regles=REGLES, departs: int = DEPARTS,
            departs_arbitres=DEPARTS_ARBITRES) -> dict:
    p = la_portee(matieres, bruits, regles, departs)
    a = larbitre(matieres, bruits, regles, departs_arbitres, departs)
    return {"portee": p, "arbitre": a, "juger": juger(p, a)}


def reagreger(r: dict) -> dict:
    """Recalcule le verdict depuis les cases rangées — sans remarcher."""
    r["juger"] = juger(r["portee"], r["arbitre"])
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    j = r["juger"]
    if not j.get("decidable"):
        print(f"⚠ {j.get('raison', 'indécidable')}")
        return
    a = j["larbitre"]
    marque = "★★★★" if a.get("le_chemin_donne_raison_a_lexact") else "✗"
    print(f"{marque} le CHEMIN tranche : {a.get('litiges')} pas litigieux, "
          f"{a.get('pour_lexact')} pour le déroulage exact, {a.get('pour_le_replie')} pour le "
          f"replié")
    print(f"\n   {'règle':>24} | {'déc.':>4} | {'touchées':>8} | {'pas':>6} | "
          f"{'repliées':>8} | {'exactes':>7} | {'écart':>5}")
    for x in j["par_regle"]:
        print(f"   {x['regle']:>24} | {x['decidables']:>4d} | {x['marches_touchees']:>8d} | "
              f"{x['pas_replies_a_tort']:>6d} | {x['reussites_repliees']:>8d} | "
              f"{x['reussites_exactes']:>7d} | {x['la_correction_deplace']:>+5d}")
    print(f"\n   matières qu'aucune marche touchée n'atteint : {j['matieres_intactes']}")
    print(f"   matières touchées DÈS le bruit nul : {j['matieres_touchees_sans_bruit']}")
    print(f"\n{'✗' if j['la_barre_de_144_bouge'] else '★★★★'} la barre de `144` bouge-t-elle ? "
          f"{j['la_barre_de_144_bouge']}")
    print(f"{'★★★' if j['une_machoire_passe_derriere_la_pince'] else '·'} une mâchoire seule "
          f"passe-t-elle DERRIÈRE la pince une fois le déroulage corrigé ? "
          f"{j['une_machoire_passe_derriere_la_pince']}")


def _case(regle: str, nom: str, bruit: float, dec: int, touchees: int, replies: int,
          r_replie: int, r_exact: int, plus_grand: float = 0.0) -> dict:
    return {"regle": regle, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0,
            "bruit": float(bruit), "departs": 12, "decidables": dec,
            "marches_touchees": touchees, "pas_replies_a_tort": replies,
            "reussites_repliees": r_replie, "reussites_exactes": r_exact,
            "plus_grand_pas_en_feuilles": float(plus_grand)}


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    from la_pince_tient_elle_la_feuille import (_le_chemin_du_pas,  # noqa: PLC0415
                                                _le_deroulage_exact, _le_pas_mesure)

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    print("— le repliement ne PEUT PAS rendre un pas au-delà d'une demi-feuille —")
    # ⭐⭐⭐⭐ La borne est une propriete de `d - round(d)`, pas une observation : quelle que soit la
    # serie, le repliement rend toujours un pas dans [-0,5 ; +0,5]. C'est exactement pour ca qu'il
    # ne peut pas repondre a la question de `158`.
    series = ([0.0, 0.8, 1.6, 2.4], [0.0, -1.3, -2.6], [0.0, 0.49, 0.98], [0.0, 3.7])
    replies = []
    for p_ in series:
        d_ = np.diff(np.asarray(p_, dtype=np.float64))
        replies.extend(np.abs(d_ - np.round(d_)).tolist())
    v("⭐⭐⭐⭐ le repliement borne TOUT pas à une demi-feuille, quelle que soit la série",
      max(replies) <= LA_DEMI_FEUILLE + 1e-12,
      f"le plus grand pas replié vaut {max(replies):.6f}")
    ex = _le_deroulage_exact([0.0, 0.8, 1.6], [0.0, 0.01, 0.02])
    v("⭐⭐⭐ ... alors que le déroulage exact en rend un de 0,8",
      ex["plus_grand_pas_en_feuilles"] == 0.8 and ex["pas_replies_a_tort"] == 2)

    print("\n— l'arbitre, et ce qu'il refuse de trancher —")
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    pas_um, voxel_um, _av = _cadre()
    vol = _matiere(VolumeFabriqueEnSpiraleFroissee, 0.0, 0.0, 0.0, LONGUEUR_DONDE_UM, RAYON_MM)
    cy, cx = vol.centre_yx_vx
    a_ = np.array([2000.0, cy, cx + RAYON_MM * 1000.0 / voxel_um])
    b_ = a_ + np.array([0.0, 0.0, 1.4 * pas_um / voxel_um])
    vrai = float(vol.phase(b_.reshape(1, 3))[0]) - float(vol.phase(a_.reshape(1, 3))[0])
    mesure, tranche = _le_pas_mesure(vol, a_, b_)
    v("⭐⭐⭐⭐ l'arbitre retrouve le pas VRAI, que le repliement écraserait",
      abs(mesure - vrai) < 1e-9 and abs(vrai) > 1.0 and tranche,
      f"{mesure:.6f} contre {vrai - round(vrai):.6f} replié")
    v("⚠⚠⚠ ... et il ne conclut QUE lorsque plus aucun sous-pas n'est replié",
      _le_chemin_du_pas(vol, a_, b_, 2)[1] > 0
      and abs(_le_chemin_du_pas(vol, a_, b_, 2)[0] - vrai) > 1e-9,
      f"à deux sous-pas, {_le_chemin_du_pas(vol, a_, b_, 2)[1]} replis et "
      f"{_le_chemin_du_pas(vol, a_, b_, 2)[0]:.6f}")

    print("\n— la réussite se lit sur la dérive qu'on lui donne —")
    x = {"decidable": True, "tour_boucle": True, "derive_en_feuilles": 0.2,
         "derive_exacte_en_feuilles": 1.2}
    v("⭐⭐⭐ le MÊME prédicat sur deux dérives rend deux verdicts",
      _reussite(x, "derive_en_feuilles") is True
      and _reussite(x, "derive_exacte_en_feuilles") is False)
    v("⚠ une marche qui ne boucle pas n'est une réussite sous AUCUNE des deux",
      not _reussite({**x, "tour_boucle": False}, "derive_en_feuilles")
      and not _reussite({**x, "tour_boucle": False}, "derive_exacte_en_feuilles"))
    v("⚠⚠ une dérive absente n'est pas une dérive nulle",
      not _reussite({"decidable": True, "tour_boucle": True}, "derive_exacte_en_feuilles"))

    print("\n— le verdict —")
    # Une barre qui ne bouge pas malgre des marches touchees, et une regle dont le total se retourne.
    p = {"decidable": True, "regles": ["barre", "pince", "seule"],
         "bruits": [0.0, 8.0], "departs": 12,
         "cases": [_case("barre", "dure", 0.0, 12, 5, 30, 8, 8),
                   _case("barre", "dure", 8.0, 12, 4, 20, 4, 4),
                   _case("pince", "dure", 0.0, 12, 3, 10, 9, 8),
                   _case("pince", "dure", 8.0, 12, 2, 8, 6, 5),
                   _case("seule", "dure", 0.0, 12, 6, 40, 11, 6),
                   _case("seule", "dure", 8.0, 12, 5, 30, 6, 4),
                   _case("barre", "simple", 0.0, 12, 0, 0, 12, 12),
                   _case("pince", "simple", 0.0, 12, 0, 0, 12, 12),
                   _case("seule", "simple", 0.0, 12, 0, 0, 12, 12)]}
    a = {"decidable": True, "litiges": 150, "pour_lexact": 150, "pour_le_replie": 0,
         "le_chemin_donne_raison_a_lexact": True}
    j = juger(p, a)
    par = {x["regle"]: x for x in j["par_regle"]}
    v("⭐⭐⭐⭐ une barre TOUCHÉE qui ne bouge pas est un résultat, et il se publie avec le compte",
      j["la_barre_de_144_bouge"] is False and par["barre"]["marches_touchees"] == 9
      and par["barre"]["la_correction_deplace"] == 0,
      f"{par['barre']['marches_touchees']} marches touchées, écart "
      f"{par['barre']['la_correction_deplace']:+d}")
    v("⭐⭐⭐ ... et un total qui MENAIT et passe derrière est signalé",
      par["seule"]["reussites_repliees"] > par["pince"]["reussites_repliees"]
      and par["seule"]["reussites_exactes"] < par["pince"]["reussites_exactes"]
      and j["une_machoire_passe_derriere_la_pince"] is True,
      f"{par['seule']['reussites_repliees']} → {par['seule']['reussites_exactes']} contre "
      f"{par['pince']['reussites_repliees']} → {par['pince']['reussites_exactes']}")
    v("⚠⚠ les matières qu'AUCUNE marche touchée n'atteint sont LUES, pas choisies",
      j["matieres_intactes"] == ["simple"], f"{j['matieres_intactes']}")
    v("⚠ ... et celles qui sont touchées DÈS le bruit nul le sont aussi",
      j["matieres_touchees_sans_bruit"] == ["dure"])
    p2 = {**p, "cases": [{**c, "reussites_exactes": c["reussites_repliees"]}
                         for c in p["cases"]]}
    v("⚠⚠ le contrôle mord : si la correction ne déplace rien nulle part, rien n'est signalé",
      juger(p2, a)["une_machoire_passe_derriere_la_pince"] is False
      and juger(p2, a)["la_barre_de_144_bouge"] is False)

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=((0.0, 0.0),), bruits=(0.0,), regles=(REGLES[0],), departs=2,
                     departs_arbitres=(0,))
    v("⚠ sur une spirale NUE, aucun pas n'est replié à tort",
      petite["portee"]["decidable"]
      and all(c["pas_replies_a_tort"] == 0 for c in petite["portee"]["cases"]))
    v("⚠⚠ ... donc l'arbitre n'a RIEN à trancher, et il le DIT au lieu de rendre zéro sur zéro",
      petite["arbitre"]["decidable"] is False)
    avant = json.loads(json.dumps(petite["portee"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["portee"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "portee": p, "arbitre": a})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend l'arbitre, le tableau et les deux verdicts",
      "litigieux" in sortie and "règle" in sortie and "barre de `144`" in sortie,
      f"{len(sortie)} caractères")
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
