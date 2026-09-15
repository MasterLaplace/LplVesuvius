"""La pose dit-elle quand elle a sauté ? — la porte `R4-P29`, mise à l'épreuve.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `161` conclut que sur la pince ce qui fait sauter un pas est le
**recentrage** et non l'avance : les mâchoires se raccrochent loin, donc elles se sont accrochées
au **mauvais interstice à la pose**. `155` ne traite ce défaut qu'au niveau des **appuis**. La porte
`R4-P29` demande s'il existe un énoncé **exact**, sans seuil, qui refuse une pose entière. Ce
fichier en met **trois** à l'épreuve, tous déjà dans le vocabulaire du dépôt.

⭐⭐⭐ LES TROIS ÉNONCÉS, ET AUCUN N'EST UN SEUIL CHOISI :

- **absolu** : « le centre a bougé de plus d'une **demi-épaisseur nominale** le long de la normale »
  — l'énoncé que `142`, `155` et `160` emploient déjà contre la géométrie nominale ;
- **relatif** : « ... de plus d'une demi-épaisseur **au-delà de la médiane** des pas de cette
  marche » — l'énoncé que `155` emploie pour dire qu'un appui est aberrant, appliqué au pas ;
- **étalement** : « les appuis de cette pose **ne tiennent pas le même interstice** », c'est-à-dire
  que l'étalement des profondeurs d'une mâchoire dépasse une demi-épaisseur.

⚠⚠ LES DEUX PREMIERS REGARDENT OÙ LE CENTRE EST ALLÉ, LE TROISIÈME SI LA MÂCHOIRE EST D'ACCORD
AVEC ELLE-MÊME. Ce sont deux axes indépendants, donc deux chances différentes de voir, et c'est la
raison d'éprouver les trois plutôt que d'en choisir un.

⚠⚠⚠ LE VERDICT EST UNE DOMINATION JOINTE, JAMAIS UN RAPPEL SEUL. Un énoncé qui refuserait TOUTES
les poses aurait un rappel parfait et ne vaudrait rien ; un énoncé qui n'en refuse aucune a une
précision indéfinie et ne vaut rien non plus. Un énoncé ne l'emporte donc que s'il a **à la fois**
un meilleur rappel et une meilleure précision — la victoire jointe que le dépôt exige depuis `147`.
S'il n'y a pas de dominant, la mesure le **dit** au lieu d'élire le moins mauvais.

⚠⚠⚠ ET LE VERDICT EST PAR BRAS. `161` a payé qu'un verdict pris sur les cases confondues efface la
réponse de l'instrument livré.

⚠⚠ CONTRÔLE OBLIGATOIRE ET VIDE. Sur la spirale NUE aucun pas ne saute (`R4-F145`), donc le rappel
n'y existe pas — il n'est pas nul, il n'est pas défini. Et aucune des trois règles ne doit y
refuser une seule pose : une règle qui refuserait là où rien ne se passe mesurerait son propre bruit.

Usage :
    uv run python src/nappe/la_pose_dit_elle_quand_elle_a_saute.py --verifier
    uv run python src/nappe/la_pose_dit_elle_quand_elle_a_saute.py \\
        --json docs/mesures/la_pose_dit_elle_quand_elle_a_saute.json
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
# (nom, deux, contrainte, rejeter) — les deux mêmes bras que `160` et `161`.
BRAS = (("la pince de `144`", True, True, False),
        ("une mâchoire avec rejet", False, False, True))
# ⚠ L'ordre est celui du raisonnement : les deux énoncés de DÉPLACEMENT d'abord, celui de
# COHÉRENCE ensuite, parce que c'est l'ordre dans lequel la question s'est posée.
ENONCES = ("absolu", "relatif", "etalement")
LA_SPIRALE_NUE = (0.0, 0.0)


def _cadre():
    return _PAS(), _VOXEL(), AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, bras):
    _n, deux, contrainte, rejeter = bras
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True)


def _taux(vus: int, manques: int, a_tort: int) -> dict:
    """Rappel et précision, et RIEN quand la question ne se pose pas.

    ⚠⚠ UN RAPPEL SANS UN SEUL SAUT N'EST PAS NUL, IL N'EXISTE PAS, et une précision sans un seul
    refus non plus. Rendre zéro ferait lire « cette règle ne voit rien » là où il n'y avait rien à
    voir, ce qui est le contraire de ce que la mesure dit.
    """
    sautent = int(vus) + int(manques)
    refuses = int(vus) + int(a_tort)
    return {"sauts": sautent, "vus": int(vus), "manques": int(manques), "refus_a_tort": int(a_tort),
            "poses_refusees": refuses,
            "rappel": (round(vus / sautent, 4) if sautent else None),
            "precision": (round(vus / refuses, 4) if refuses else None)}


def _resume(xs: list[dict]) -> dict:
    """Ce qu'un paquet de marches dit des trois énoncés.

    ⚠ Les comptes se SOMMENT parce que la question porte sur des PAS, pas sur des marches : « ce
    pas a-t-il changé de feuille » et « cette règle l'a-t-elle vu » sont deux faits sur un pas.
    Ce qui ne se somme jamais, c'est un rappel ou une précision — ils se recalculent des comptes.
    """
    dec = [x for x in xs if x.get("decidable") and x.get("pas_examines") is not None]
    sans = sum(1 for x in xs if x.get("decidable") and x.get("pas_examines") is None)
    base = {"marches": len(xs), "decidables": len(dec), "marches_sans_un_pas": int(sans),
            "pas_examines": int(sum(int(x["pas_examines"]) for x in dec))}
    if not dec:
        return {**base, "decidable": False, "raison": "aucune marche décidable qui ait fait un pas"}
    out = {**base, "decidable": True}
    for regle in ENONCES:
        if any(x.get(f"sauts_vus_par_l_{regle}") is None for x in dec):
            continue
        out[regle] = _taux(sum(int(x[f"sauts_vus_par_l_{regle}"]) for x in dec),
                           sum(int(x[f"sauts_manques_par_l_{regle}"]) for x in dec),
                           sum(int(x[f"refus_a_tort_de_l_{regle}"]) for x in dec))
    # ⚠⚠ L'ÉTALEMENT N'EST PAS TOUJOURS LISIBLE : une mâchoire absente ou à un seul appui ne peut
    # pas se contredire. Ces poses sont COMPTÉES, jamais lues comme des poses cohérentes.
    out["poses_sans_etalement_lisible"] = int(sum(
        int(x.get("poses_sans_etalement_lisible", 0)) for x in dec))
    for cle, nom in (("mediane_du_recentrage_um", "recentrage_median_um"),
                     ("etalement_median_um", "etalement_median_um")):
        vals = [float(x[cle]) for x in dec if x.get(cle) is not None]
        out[nom] = round(float(statistics.median(vals)), 3) if vals else None
    return out


def linterrogatoire(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    """Ce que chaque énoncé voit, matière par matière et bras par bras."""
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
                              "amplitude_um": float(amp), "bruit": float(bruit),
                              "departs": int(departs), **_resume(xs)})
    return {"decidable": bool(cases), "cases": cases, "bras": [b[0] for b in bras],
            "enonces": list(ENONCES), "bruits": [float(b) for b in bruits],
            "departs": int(departs)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    """Les comptes d'un groupe — des sommes de COMPTES, et les taux recalculés d'elles."""
    dec = [c for c in cs if c.get("decidable")]
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           "decidables": int(sum(c.get("decidables", 0) for c in cs)),
           "pas_examines": int(sum(c.get("pas_examines", 0) for c in dec)),
           "poses_sans_etalement_lisible": int(sum(
               c.get("poses_sans_etalement_lisible", 0) for c in dec))}
    for regle in ENONCES:
        parts = [c[regle] for c in dec if c.get(regle) is not None]
        if not parts:
            continue
        out[regle] = _taux(sum(p["vus"] for p in parts), sum(p["manques"] for p in parts),
                           sum(p["refus_a_tort"] for p in parts))
    for cle in ("recentrage_median_um", "etalement_median_um"):
        vals = [c[cle] for c in dec if c.get(cle) is not None]
        out[cle] = round(float(statistics.median(vals)), 3) if vals else None
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_bras(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["bras"] == b], b)
            for b in dict.fromkeys(c["bras"] for c in d["cases"])]


def _domine(a: dict, b: dict) -> bool:
    """`a` domine `b` : meilleur rappel ET meilleure précision, les deux définis.

    ⚠⚠⚠ UNE DOMINATION EST JOINTE, JAMAIS UN AXE SEUL. Un énoncé qui refuse toutes les poses a un
    rappel parfait et ne vaut rien ; un énoncé qui n'en refuse aucune a une précision indéfinie et
    ne vaut rien non plus. Exiger les deux rend ces deux dégénérescences inéligibles par
    construction plutôt que par une garde ajoutée après coup.

    ⚠⚠ UN TAUX INDÉFINI NE DOMINE RIEN ET N'EST DOMINÉ PAR RIEN : on ne compare pas un nombre à
    une absence.
    """
    if a is None or b is None:
        return False
    for cle in ("rappel", "precision"):
        if a.get(cle) is None or b.get(cle) is None:
            return False
    return bool(a["rappel"] > b["rappel"] and a["precision"] > b["precision"])


def _inertes(g: dict) -> list[str]:
    """Les énoncés qui n'ont refusé AUCUNE pose là où il y avait des sauts à voir.

    ⚠⚠⚠ UN ÉNONCÉ INERTE EST NOMMÉ, JAMAIS SILENCIEUSEMENT ÉCARTÉ. Il n'a pas de précision à
    défendre, donc il ne domine rien et rien ne le domine — et laissé dans la comparaison il
    BLOQUE toute domination, ce qui rend le verdict incapable d'être positif. C'est un défaut que
    cette batterie a attrapé au premier passage.
    """
    return [r for r in ENONCES
            if g.get(r) is not None and g[r]["sauts"] > 0 and g[r]["poses_refusees"] == 0]


def _le_dominant(g: dict) -> str | None:
    """L'énoncé qui domine tous les autres ÉLIGIBLES, ou rien s'il n'y en a pas.

    ⚠⚠ EST ÉLIGIBLE UN ÉNONCÉ QUI AGIT : il y a des sauts à voir, et il refuse au moins une pose.
    Un énoncé qui n'agit pas n'est pas un concurrent, c'est une abstention — et `_inertes` la
    nomme pour que l'abstention n'ait pas l'air d'une égalité.
    """
    inertes = set(_inertes(g))
    eligibles = [r for r in ENONCES
                 if g.get(r) is not None and g[r]["sauts"] > 0 and r not in inertes]
    for r in eligibles:
        if all(_domine(g[r], g[a]) for a in eligibles if a != r):
            return r
    return None


def juger(d: dict) -> dict:
    """Quel énoncé voit, bras par bras — et le contrôle VIDE qui rend la réponse lisible."""
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, bras = par_matiere(d), par_bras(d)
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    # ⚠⚠⚠ LE CONTRÔLE A DEUX MOITIÉS ET IL FAUT LES DEUX. Qu'aucun pas ne saute est ce que
    # `R4-F145` mesure déjà ; ce que CETTE tranche doit vérifier, c'est qu'aucune des trois règles
    # n'y refuse une seule pose. Une règle qui refuserait là où rien ne se passe mesurerait son
    # propre bruit, et tout le reste du tableau ne voudrait plus rien dire.
    controle = {"nom": nue["nom"] if nue else None,
                "sauts": (nue.get(ENONCES[0], {}) or {}).get("sauts") if nue else None,
                "poses_refusees": ({r: (nue.get(r, {}) or {}).get("poses_refusees")
                                    for r in ENONCES} if nue else {}),
                "pas_examines": nue["pas_examines"] if nue else None}
    controle["il_est_vide"] = bool(
        nue is not None and controle["sauts"] == 0
        and all(v == 0 for v in controle["poses_refusees"].values() if v is not None)
        and any(v is not None for v in controle["poses_refusees"].values()))
    return {"decidable": True, "par_matiere": mat, "par_bras": bras,
            "tout": _cumuler(d["cases"], "tout"),
            "le_controle_de_la_spirale_nue": controle,
            # ⭐⭐⭐⭐ ET LA RÉPONSE : sur chaque bras, un énoncé domine-t-il les deux autres ?
            "le_dominant_par_bras": {g["nom"]: _le_dominant(g) for g in bras},
            "les_inertes_par_bras": {g["nom"]: _inertes(g) for g in bras},
            # ⭐⭐⭐⭐ ET L'INERTIE SE LIT AUSSI PAR MATIERE, la ou elle est la plus parlante : sur
            # une matiere ou le deplacement ne depasse JAMAIS une demi-epaisseur, les deux
            # enonces de deplacement ne refusent pas une seule pose, pendant que la pose, elle,
            # se contredit. Un enonce inerte n'a pas « rate » les sauts : il n'a rien tente.
            "le_dominant_par_matiere": {g["nom"]: _le_dominant(g) for g in mat},
            "les_inertes_par_matiere": {g["nom"]: _inertes(g) for g in mat},
            "le_meilleur_rappel_par_bras": {
                g["nom"]: max((r for r in ENONCES
                               if (g.get(r) or {}).get("rappel") is not None),
                              key=lambda r: g[r]["rappel"], default=None)
                for g in bras}}


def mesurer(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    d = linterrogatoire(matieres, bruits, bras, departs)
    return {"interrogatoire": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    """Recalcule le verdict depuis les cases rangées — sans remarcher."""
    r["juger"] = juger(r["interrogatoire"])
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
    refus = " · ".join(f"{k} {v}" for k, v in c["poses_refusees"].items())
    print(f"{marque} contrôle — sur la spirale NUE, {c['sauts']} saut sur {c['pas_examines']} pas, "
          f"et AUCUNE règle ne refuse : {refus}")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —")
        print(f"   {'':>22} | {'pas':>7} | " + " | ".join(f"{r_:>22}" for r_ in ENONCES))
        for g in groupes:
            cells = []
            for r_ in ENONCES:
                t = g.get(r_)
                if t is None or t["sauts"] == 0:
                    cells.append(f"{'(aucun saut)':>22}")
                    continue
                ra = "—" if t["rappel"] is None else f"{t['rappel']:.3f}"
                pr = "—" if t["precision"] is None else f"{t['precision']:.3f}"
                cells.append(f"{'r ' + ra + ' p ' + pr:>22}")
            print(f"   {_court(g['nom']):>22} | {g['pas_examines']:>7d} | " + " | ".join(cells))
    print("\n★★★★ l'énoncé qui DOMINE (meilleur rappel ET meilleure précision), bras par bras :")
    for nom, dom in j["le_dominant_par_bras"].items():
        best = j["le_meilleur_rappel_par_bras"][nom]
        dit = dom if dom else f"aucun — le meilleur rappel est « {best} », au prix de sa précision"
        print(f"      {_court(nom):>22} : {dit}")


def _suivi(pas: int, table: dict, etalement_lisible: bool = True) -> dict:
    """Une marche dont les trois tables de confusion sont connues.

    `table` : {regle: (vus, manques, a_tort)}.
    """
    out = {"decidable": True, "pas_examines": int(pas),
           "poses_sans_etalement_lisible": 0 if etalement_lisible else int(pas),
           "mediane_du_recentrage_um": 9.9, "etalement_median_um": 40.0}
    for regle, (v_, m_, t_) in table.items():
        out[f"sauts_vus_par_l_{regle}"] = int(v_)
        out[f"sauts_manques_par_l_{regle}"] = int(m_)
        out[f"refus_a_tort_de_l_{regle}"] = int(t_)
    return out


def verifier() -> int:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    from la_pince_tient_elle_la_feuille import _le_deroulage_exact  # noqa: PLC0415

    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    print("— les trois énoncés sortent du même suiveur et comptent les mêmes sauts —")
    # Quatre pas : le 1er et le 3e franchissent plus d'une demi-feuille.
    ph = [0.0, 0.8, 1.1, 2.5, 2.6]
    an = [0.0, 0.01, 0.02, 0.03, 0.04]
    t_ = np.array([1.0, 0.0, 0.0])
    n_ = np.array([0.0, 1.0, 0.0])
    centres = [np.array([0.0, 0.0, 0.0]), np.array([1.0, 200.0, 0.0]),
               np.array([2.0, 210.0, 0.0]), np.array([3.0, 400.0, 0.0]),
               np.array([4.0, 405.0, 0.0])]
    reperes = [(t_, n_)] * 4
    # ⚠ Les etalements sont ceux des poses OU L'ON ARRIVE : un par pas.
    ex = _le_deroulage_exact(ph, an, centres, 1.0, None, reperes, 173.0, [200.0, 5.0, 200.0, 5.0])
    v("⭐⭐⭐ les trois énoncés comptent le MÊME nombre de sauts",
      len({ex[f"sauts_vus_par_l_{r}"] + ex[f"sauts_manques_par_l_{r}"] for r in ENONCES}) == 1,
      f"{ {r: ex[f'sauts_vus_par_l_{r}'] + ex[f'sauts_manques_par_l_{r}'] for r in ENONCES} }")
    v("⭐⭐⭐⭐ l'ÉTALEMENT ne regarde pas le déplacement du tout",
      ex["sauts_vus_par_l_etalement"] == 2 and ex["refus_a_tort_de_l_etalement"] == 0,
      "les deux poses étalées sont exactement celles où le pas saute")
    v("⚠⚠ ... et une pose SANS étalement lisible ne refuse rien, elle est COMPTÉE",
      _le_deroulage_exact(ph, an, centres, 1.0, None, reperes, 173.0,
                          [None, None, None, None])["poses_sans_etalement_lisible"] == 4
      and _le_deroulage_exact(ph, an, centres, 1.0, None, reperes, 173.0,
                              [None, None, None, None])["poses_refusees_par_l_etalement"] == 0)
    # ⚠⚠ LA BORNE EST STRICTE, comme la demi-feuille de `160` : un etalement d'exactement une
    # demi-epaisseur ne refuse PAS.
    juste = _le_deroulage_exact(ph, an, centres, 1.0, None, reperes, 173.0, [86.5] * 4)
    v("⚠⚠ un étalement d'exactement une demi-épaisseur ne refuse PAS — la borne est stricte",
      juste["poses_refusees_par_l_etalement"] == 0)
    v("⚠ sans épaisseur nominale, aucune règle n'est publiée — on ne devine pas la borne",
      "sauts_vus_par_l_absolu" not in _le_deroulage_exact(ph, an, centres, 1.0, None, reperes))

    print("\n— rappel et précision, et ce qui n'existe pas —")
    t = _taux(3, 1, 1)
    v("⚠ rappel et précision se calculent des comptes", t["rappel"] == 0.75 and t["precision"] == 0.75)
    v("⭐⭐⭐⭐ un rappel SANS UN SEUL SAUT n'est pas nul, il n'existe pas",
      _taux(0, 0, 0)["rappel"] is None and _taux(0, 0, 0)["sauts"] == 0)
    v("⭐⭐⭐ ... et une précision sans un seul REFUS non plus",
      _taux(0, 5, 0)["precision"] is None and _taux(0, 5, 0)["rappel"] == 0.0,
      "voir zéro saut sur cinq est un rappel de zéro, ne refuser aucune pose n'est pas une précision")

    print("\n— la domination est JOINTE —")
    v("⭐⭐⭐⭐ un énoncé ne domine qu'avec un meilleur rappel ET une meilleure précision",
      _domine(_taux(9, 1, 1), _taux(5, 5, 5)) is True
      and _domine(_taux(9, 1, 20), _taux(5, 5, 1)) is False,
      "rappel 0,9 contre 0,5 ne suffit pas si la précision tombe")
    # ⚠⚠⚠ LES DEUX DEGENERESCENCES SONT INELIGIBLES PAR CONSTRUCTION.
    tout_refuser = _taux(10, 0, 990)
    rien_refuser = _taux(0, 10, 0)
    v("⭐⭐⭐⭐ refuser TOUTES les poses donne un rappel parfait et ne domine rien",
      tout_refuser["rappel"] == 1.0 and _domine(tout_refuser, _taux(5, 5, 1)) is False)
    v("⭐⭐⭐ ... et n'en refuser AUCUNE ne domine rien non plus, faute de précision",
      rien_refuser["precision"] is None and _domine(rien_refuser, _taux(5, 5, 1)) is False
      and _domine(_taux(5, 5, 1), rien_refuser) is False,
      "on ne compare pas un nombre à une absence")
    g = {"absolu": _taux(1, 9, 1), "relatif": _taux(0, 10, 0), "etalement": _taux(9, 1, 9)}
    v("⚠⚠ quand l'un voit beaucoup plus mais refuse beaucoup plus à tort, il n'y a PAS de dominant",
      _le_dominant(g) is None,
      f"étalement rappel {g['etalement']['rappel']} précision {g['etalement']['precision']} "
      f"contre {g['absolu']['rappel']} et {g['absolu']['precision']}")
    v("⭐⭐ ... et quand il y en a un, il est nommé",
      _le_dominant({"absolu": _taux(1, 9, 9), "etalement": _taux(9, 1, 1)}) == "etalement")

    print("\n— le résumé somme des COMPTES, jamais des taux —")
    xs = [_suivi(100, {"absolu": (1, 9, 1), "relatif": (0, 10, 0), "etalement": (9, 1, 9)}),
          _suivi(10, {"absolu": (1, 0, 0), "relatif": (1, 0, 0), "etalement": (1, 0, 0)})]
    r = _resume(xs)
    # ⚠⚠ L'ATTENDU SE DERIVE DE LA FIXTURE : ecrit en dur il devient faux a la premiere retouche.
    attendu = (1 + 1) / ((1 + 1) + (9 + 0))
    v("⭐⭐⭐ un rappel de groupe se recalcule des comptes, jamais en moyennant des rappels",
      abs(r["absolu"]["rappel"] - round(attendu, 4)) < 1e-9
      and abs(r["absolu"]["rappel"] - statistics.mean([0.1, 1.0])) > 1e-6,
      f"{r['absolu']['rappel']} et non {statistics.mean([0.1, 1.0])}, la moyenne des deux rappels")
    # ⚠⚠⚠ ET `_cumuler` DOIT LA MEME CHOSE, ce que rien ne verifiait : c'est LUI qui produit les
    # chiffres par bras et par matiere que le document publie, et une sonde qui le cassait passait
    # au vert parce que la seule assertion portait sur `_resume`. Une garde qui ne couvre pas le
    # producteur du chiffre publie ne protege rien.
    ca = {"decidable": True, "decidables": 1, "pas_examines": 100,
          "poses_sans_etalement_lisible": 0, "recentrage_median_um": 9.9,
          "etalement_median_um": 40.0, "absolu": _taux(1, 9, 1)}
    cb = {**ca, "pas_examines": 10, "absolu": _taux(1, 0, 0)}
    cum = _cumuler([ca, cb], "deux")
    v("⭐⭐⭐⭐ `_cumuler` recalcule lui aussi des COMPTES, jamais en moyennant des taux",
      abs(cum["absolu"]["rappel"] - round((1 + 1) / ((1 + 1) + (9 + 0)), 4)) < 1e-9
      and abs(cum["absolu"]["rappel"]
              - statistics.mean([ca["absolu"]["rappel"], cb["absolu"]["rappel"]])) > 1e-6,
      f"{cum['absolu']['rappel']} et non "
      f"{statistics.mean([ca['absolu']['rappel'], cb['absolu']['rappel']])}")
    v("⚠⚠ ... et une case indécidable n'entre dans aucun compte cumulé",
      _cumuler([ca, cb, {"decidable": False}], "trois")["absolu"] == cum["absolu"]
      and _cumuler([ca, cb, {"decidable": False}], "trois")["cases_decidables"] == 2)

    v("⚠ une marche qui n'a fait aucun pas est SAUTÉE et comptée",
      _resume(xs + [{"decidable": True}])["marches_sans_un_pas"] == 1
      and _resume(xs + [{"decidable": True}])["decidables"] == len(xs))
    v("⚠⚠ ... et sans aucune marche décidable le résumé le DIT",
      _resume([{"decidable": True}])["decidable"] is False)

    print("\n— le contrôle de la spirale nue a DEUX moitiés —")
    def case(nom, bras_, table, pas=1000, dec=12):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                "departs": dec, **_resume([_suivi(pas, table)] * dec)}
    rien = {r: (0, 0, 0) for r in ENONCES}
    dur = {"absolu": (1, 9, 1), "relatif": (0, 10, 0), "etalement": (9, 1, 9)}
    bon = {"decidable": True, "bras": ["p", "s"], "enonces": list(ENONCES), "bruits": [0.0],
           "departs": 12,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", rien), case("dure", "p", dur),
                     case("dure", "s", {"absolu": (1, 9, 9), "relatif": (0, 10, 0),
                                        "etalement": (9, 1, 1)})]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand la spirale nue ne saute pas ET ne refuse rien",
      j["le_controle_de_la_spirale_nue"]["il_est_vide"] is True)
    # ⚠⚠⚠ ET C'EST LA SECONDE MOITIE QUI EST NEUVE : une regle qui refuse la ou rien ne saute
    # mesure son propre bruit, et rien avant cette tranche ne le verifiait.
    bruyant = {**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", {**rien, "etalement": (0, 0, 4)})]
               + bon["cases"][1:]}
    v("⭐⭐⭐⭐ ... et il TOMBE si une règle refuse une pose là où AUCUN pas ne saute",
      juger(bruyant)["le_controle_de_la_spirale_nue"]["il_est_vide"] is False,
      "aucun saut, et pourtant des refus — la règle mesurerait son propre bruit")
    v("⭐⭐⭐ le verdict est PAR BRAS, et les deux bras peuvent se contredire",
      j["le_dominant_par_bras"]["p"] is None and j["le_dominant_par_bras"]["s"] == "etalement",
      f"{j['le_dominant_par_bras']}")
    # ⚠⚠⚠ UN ENONCE INERTE BLOQUAIT TOUTE DOMINATION, donc le verdict ne pouvait JAMAIS etre
    # positif. Attrape par cette batterie au premier passage : `relatif` ne refuse aucune pose,
    # n'a donc pas de precision, et rien ne pouvait le dominer. Il est desormais NOMME et ecarte.
    v("⭐⭐⭐⭐ un énoncé qui ne refuse AUCUNE pose est nommé INERTE, pas traité en concurrent",
      j["les_inertes_par_bras"]["s"] == ["relatif"]
      and j["le_dominant_par_bras"]["s"] == "etalement",
      "laissé dans la comparaison il rendait le verdict incapable d'être positif")
    v("⚠⚠ ... et une règle qui n'avait aucun saut à voir n'est pas inerte, elle est hors sujet",
      _inertes({r: _taux(0, 0, 0) for r in ENONCES}) == [])
    # ⭐⭐⭐ L'INERTIE SE LIT PAR MATIERE AUSSI, et c'est la qu'elle tranche : un enonce peut n'etre
    # inerte que sur une matiere, donc l'agregat par bras la cache.
    v("⭐⭐⭐ l'inertie se lit aussi PAR MATIÈRE, où un agrégat par bras la cacherait",
      j["les_inertes_par_matiere"]["dure"] == ["relatif"]
      and j["le_dominant_par_matiere"][_nom(*LA_SPIRALE_NUE)] is None,
      "une matière sans aucun saut n'a ni inerte ni dominant, elle est hors sujet")
    v("⚠⚠ ... et quand aucun ne domine, le MEILLEUR RAPPEL est nommé à part, jamais élu",
      j["le_meilleur_rappel_par_bras"]["p"] == "etalement"
      and j["le_dominant_par_bras"]["p"] is None)

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    v("⭐⭐⭐ sur la spirale NUE la mesure réelle ne refuse aucune pose",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] is True,
      f"{petite['juger']['le_controle_de_la_spirale_nue']['poses_refusees']}")
    avant = json.loads(json.dumps(petite["interrogatoire"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["interrogatoire"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "interrogatoire": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, les deux tableaux et le verdict",
      "contrôle" in sortie and "par bras" in sortie and "par matière" in sortie
      and "aucun" in sortie and "etalement" in sortie, f"{len(sortie)} caractères")
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
