"""Ce qu'un marcheur qui ÉCOUTE livre — la règle de `163`, branchée pour de bon.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `162` mesure que la pose DIT quand elle a sauté, `163` que son premier
refus tombe un à deux pas **avant** le saut. Les deux mesurent la règle sur des marches qui
**n'écoutent pas** : elles lisent des tableaux enregistrés. Ici la marche **s'arrête** dessus, pour
la première fois, et la question devient celle du livrable : **que remet un marcheur qui écoute, et
que remet-il de moins qu'un marcheur qui n'écoute pas ?**

⚠⚠⚠ ET C'EST LA QUESTION DU GRAAL SOUS SA FORME UTILE. Un marcheur qui n'écoute pas livre une
trajectoire dont il ignore où elle a cessé d'être vraie — `163` mesure **25** marches qui sautent
**sans que rien ne le dise** sur la pince. Une telle trajectoire n'est pas à moitié bonne : elle est
**inutilisable en entier**, faute de savoir où la couper. Un marcheur qui écoute en livre une plus
courte, et **sûre**.

⚠⚠ LES DEUX LECTURES SONT PUBLIÉES, et c'est délibéré. La longueur **BRUTE** compte tous les pas
livrés, la longueur **UTILISABLE** ne compte que ceux d'une livraison dont rien ne dit qu'elle a
sauté. La seconde est celle qui répond à la question, la première est celle qui empêche de croire
que l'arrêt est gratuit.

⚠⚠⚠ LA VICTOIRE EST JOINTE, ET SON SECOND AXE EST LE SEUL QUI PUISSE ÉCHOUER. Une marche qui écoute
est un PRÉFIXE de la même marche qui n'écoute pas — même fixture, même suiveur, arrêt plus tôt —
donc elle ne peut jamais devenir fausse en s'arrêtant : le gain en fiabilité est acquis par
construction, et le compter comme une victoire serait un contrôle incapable d'échouer. Ce qui peut
échouer, et qu'il faut donc compter, c'est la **longueur perdue** sur les départs qui allaient bien.

Usage :
    uv run python src/nappe/ce_quun_marcheur_qui_ecoute_livre.py --verifier
    uv run python src/nappe/ce_quun_marcheur_qui_ecoute_livre.py \\
        --json docs/mesures/ce_quun_marcheur_qui_ecoute_livre.json
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


def _marcher(vol, k, departs, pas_um, voxel_um, avance_um, bras, ecoute: bool):
    _n, deux, contrainte, rejeter = bras
    depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), RAYON_MM, voxel_um, pas_um)
    vol.lectures = 0
    return suivre(vol, depart, n0, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, deux,
                  contrainte, avance_um, vol.centre_yx_vx, tours=TOURS, fenetre_du_cap=FENETRE,
                  rejeter=rejeter, derouler_exactement=True, refuser_la_pose=ecoute)


def une_livraison(x: dict) -> dict | None:
    """Ce qu'UNE marche remet : sa longueur, et si quelque chose dit qu'elle a sauté.

    ⚠⚠ « FIABLE » NE VEUT PAS DIRE « VRAIE », il veut dire QUE RIEN NE DIT LE CONTRAIRE. C'est
    exactement ce dont un livrable dispose : la fixture sait si la marche a sauté, le marcheur non.
    La distinction est publiée — `a_saute` vient de la fixture, `sest_arretee_dessus` du marcheur —
    pour qu'on ne confonde jamais ce qu'on sait avec ce qu'il saurait.
    """
    if not x.get("decidable") or x.get("pas") is None:
        return None
    saute = x.get("pas_qui_sautent")
    return {"pas": int(x["pas"]),
            "a_saute": (None if saute is None else bool(int(saute) > 0)),
            "sest_arretee_dessus": bool(x.get("fin") == "la pose se contredit"),
            "poses_refusees": int(x.get("poses_refusees", 0))}


def _apparier(sans: dict, avec: dict) -> dict | None:
    """Un départ, marché deux fois — et l'invariant qui rend la comparaison lisible.

    ⚠⚠⚠ LA MARCHE QUI ÉCOUTE EST UN PRÉFIXE DE CELLE QUI N'ÉCOUTE PAS : même fixture, même
    suiveur, arrêt plus tôt. C'est ce qui interdit qu'elle devienne fausse en s'arrêtant, donc ce
    qui rend « aucune fiabilité perdue » vrai PAR CONSTRUCTION — et donc impropre à servir de
    victoire. L'invariant est ASSERTÉ plutôt que supposé : s'il tombe, c'est que l'arrêt a changé
    la marche au lieu de la couper, et toute la comparaison serait à refaire.
    """
    a, b = une_livraison(sans), une_livraison(avec)
    if a is None or b is None:
        return None
    return {"pas_sans": a["pas"], "pas_avec": b["pas"],
            "a_saute_sans": a["a_saute"], "a_saute_avec": b["a_saute"],
            "sest_arretee_dessus": b["sest_arretee_dessus"],
            "est_un_prefixe": bool(b["pas"] <= a["pas"]),
            # ⚠ La longueur PERDUE n'a de sens que si la marche s'est arretee sur la pose : une
            # marche qui finit son tour des deux cotes n'a rien perdu.
            "pas_perdus": int(a["pas"] - b["pas"])}


def _resume(paires: list[dict]) -> dict:
    """Ce qu'un paquet de départs dit du livrable.

    ⚠⚠ LA LONGUEUR UTILISABLE EST CELLE DES LIVRAISONS DONT RIEN NE DIT QU'ELLES ONT SAUTÉ. Sans la
    règle, une marche qui saute en silence n'est pas à moitié bonne : rien ne dit où la couper,
    donc elle ne vaut RIEN. Avec la règle, une marche arrêtée sur la pose vaut toute sa longueur.
    """
    ps = [p for p in paires if p is not None]
    if not ps:
        return {"decidable": False, "raison": "aucun départ apparié", "departs": len(paires)}
    # ⚠ Sans la regle, le marcheur ne dispose d'AUCUN signal : sa livraison est utilisable
    # seulement si elle n'a pas saute, ce qu'il ne peut pas savoir. C'est bien le point.
    util_sans = sum(p["pas_sans"] for p in ps if p["a_saute_sans"] is False)
    util_avec = sum(p["pas_avec"] for p in ps
                    if p["a_saute_avec"] is False or p["sest_arretee_dessus"])
    # ⚠⚠ Une livraison arretee sur la pose ET qui a quand meme saute est comptee comme FAUSSE :
    # la regle a parle trop tard, donc ce qu'elle remet contient deja du faux.
    fausses_avec = sum(1 for p in ps if p["a_saute_avec"] is True)
    return {"decidable": True, "departs": len(paires), "apparies": len(ps),
            "prefixes": int(sum(1 for p in ps if p["est_un_prefixe"])),
            "livraisons_qui_sautent_sans": int(sum(1 for p in ps if p["a_saute_sans"] is True)),
            "livraisons_qui_sautent_avec": int(fausses_avec),
            "livraisons_arretees_sur_la_pose": int(sum(1 for p in ps
                                                       if p["sest_arretee_dessus"])),
            # ⭐⭐⭐ LE SEUL AXE QUI PUISSE ECHOUER : les departs qui allaient bien et que l'arret
            # raccourcit. Le gain en fiabilite, lui, est acquis par construction.
            "departs_raccourcis_pour_rien": int(sum(1 for p in ps if p["sest_arretee_dessus"]
                                                    and p["a_saute_sans"] is False)),
            "pas_livres_sans": int(sum(p["pas_sans"] for p in ps)),
            "pas_livres_avec": int(sum(p["pas_avec"] for p in ps)),
            "pas_utilisables_sans": int(util_sans),
            "pas_utilisables_avec": int(util_avec),
            "pas_perdus_median": (int(statistics.median(
                [p["pas_perdus"] for p in ps if p["sest_arretee_dessus"]]))
                if any(p["sest_arretee_dessus"] for p in ps) else None),
            # ⚠⚠⚠ DEUX MEDIANES, PARCE QUE CE SONT DEUX QUESTIONS. La premiere porte sur TOUS les
            # arrets, y compris ceux qui ont sauve la marche : ce qu'ils abandonnent n'est pas une
            # perte. La seconde ne porte que sur les marches qui allaient BIEN, et c'est elle
            # seule qui chiffre le COUT. Les confondre fait lire « 596 pas perdus » la ou zero
            # marche saine a ete coupee — defaut trouve a l'oeil sur la figure, pas par la
            # batterie.
            "pas_perdus_pour_rien_median": (int(statistics.median(
                [p["pas_perdus"] for p in ps
                 if p["sest_arretee_dessus"] and p["a_saute_sans"] is False]))
                if any(p["sest_arretee_dessus"] and p["a_saute_sans"] is False for p in ps)
                else None)}


def le_livrable(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    """Ce que chaque bras livre, avec et sans l'oreille, matière par matière."""
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    pas_um, voxel_um, avance_um = _cadre()
    cases = []
    for b in bras:
        for ecr, amp in matieres:
            for bruit in bruits:
                vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit,
                               LONGUEUR_DONDE_UM, RAYON_MM)
                paires = [_apparier(
                    _marcher(vol, k, departs, pas_um, voxel_um, avance_um, b, False),
                    _marcher(vol, k, departs, pas_um, voxel_um, avance_um, b, True))
                    for k in range(int(departs))]
                cases.append({"bras": b[0], "nom": _nom(ecr, amp), "ecrasement": float(ecr),
                              "amplitude_um": float(amp), "bruit": float(bruit),
                              **_resume(paires)})
    return {"decidable": bool(cases), "cases": cases, "bras": [b[0] for b in bras],
            "bruits": [float(b) for b in bruits], "departs": int(departs)}


def _cumuler(cs: list[dict], nom: str) -> dict:
    """Les comptes d'un groupe — des SOMMES, et la médiane des médianes à part."""
    dec = [c for c in cs if c.get("decidable")]
    cles = ("apparies", "prefixes", "livraisons_qui_sautent_sans", "livraisons_qui_sautent_avec",
            "livraisons_arretees_sur_la_pose", "departs_raccourcis_pour_rien",
            "pas_livres_sans", "pas_livres_avec", "pas_utilisables_sans", "pas_utilisables_avec")
    out = {"nom": nom, "cases": len(cs), "cases_decidables": len(dec),
           **{k: int(sum(c.get(k, 0) for c in dec)) for k in cles}}
    for cle in ("pas_perdus_median", "pas_perdus_pour_rien_median"):
        pe = [c[cle] for c in dec if c.get(cle) is not None]
        out[cle] = int(statistics.median(pe)) if pe else None
    # ⭐⭐⭐⭐ LE RAPPORT QUI REPOND : combien de pas UTILISABLES l'oreille achete-t-elle ? Il se
    # recalcule des sommes, jamais en moyennant des rapports de cases.
    out["ce_que_loreille_achete"] = (
        round(out["pas_utilisables_avec"] / out["pas_utilisables_sans"], 4)
        if out["pas_utilisables_sans"] else None)
    out["tous_prefixes"] = bool(out["prefixes"] == out["apparies"])
    return out


def par_matiere(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["nom"] == nom], nom)
            for nom in dict.fromkeys(c["nom"] for c in d["cases"])]


def par_bras(d: dict) -> list[dict]:
    return [_cumuler([c for c in d["cases"] if c["bras"] == b], b)
            for b in dict.fromkeys(c["bras"] for c in d["cases"])]


def hors_controle(cases: list[dict], nom: str) -> dict:
    """Le même cumul, mais sans la matière de CONTRÔLE.

    ⚠⚠⚠ UN RAPPORT QUI CONTIENT UN TERME IDENTIQUE DES DEUX CÔTÉS EST TIRÉ VERS UN PAR
    CONSTRUCTION, et plus ce terme est gros, moins le rapport dit quoi que ce soit. La spirale nue
    livre **46068** pas des deux côtés — l'oreille n'y change rien, c'est tout l'objet du contrôle
    — donc elle pèse dans le dénominateur ET dans le numérateur sans jamais pouvoir les séparer.
    Un rapport par bras qui l'inclut mesure surtout la taille du contrôle.

    ⚠⚠ Le contrôle n'est pas RETIRÉ de la mesure : il reste publié, et c'est lui qui autorise à
    lire le reste. Ce qui est retiré, c'est sa contribution à un RAPPORT qu'il ne peut que diluer.
    """
    return _cumuler([c for c in cases if c.get("nom") != _nom(*LA_SPIRALE_NUE)], nom)


def juger(d: dict) -> dict:
    """Ce que l'oreille achète, et le contrôle qui rend la réponse lisible."""
    if not d.get("decidable"):
        return {"decidable": False, "raison": "aucune case mesurée"}
    mat, bras = par_matiere(d), par_bras(d)
    tout = _cumuler(d["cases"], "tout")
    nue = next((m for m in mat if m["nom"] == _nom(*LA_SPIRALE_NUE)), None)
    # ⚠⚠⚠ LE CONTROLE A DEUX MOITIES. Sur la spirale nue rien ne saute, donc l'oreille ne doit RIEN
    # changer : aucune marche arretee, et la meme longueur livree des deux cotes. La seconde moitie
    # est la plus dure — elle interdit a l'arret de couter quoi que ce soit la ou il n'y a rien a
    # sauver.
    controle = {"nom": nue["nom"] if nue else None,
                "livraisons_arretees_sur_la_pose": (nue["livraisons_arretees_sur_la_pose"]
                                                    if nue else None),
                "pas_livres_sans": nue["pas_livres_sans"] if nue else None,
                "pas_livres_avec": nue["pas_livres_avec"] if nue else None}
    controle["il_est_neutre"] = bool(
        nue is not None and controle["livraisons_arretees_sur_la_pose"] == 0
        and controle["pas_livres_sans"] == controle["pas_livres_avec"])
    return {"decidable": True, "par_matiere": mat, "par_bras": bras, "tout": tout,
            "le_controle_de_la_spirale_nue": controle,
            # ⚠⚠ L'INVARIANT DE PREFIXE EST PUBLIE : s'il tombe, l'arret a change la marche au lieu
            # de la couper, et toute la comparaison serait a refaire.
            "toute_marche_qui_ecoute_est_un_prefixe": bool(tout["tous_prefixes"]),
            "ce_que_loreille_achete_par_bras": {g["nom"]: g["ce_que_loreille_achete"]
                                                for g in bras},
            # ⚠⚠⚠ ET LE MÊME RAPPORT SANS LE CONTRÔLE, parce que celui-ci contribue à l'identique
            # des deux côtés et ne peut donc que tirer vers UN.
            "hors_controle": hors_controle(d["cases"], "hors contrôle"),
            "ce_que_loreille_achete_par_bras_hors_controle": {
                b: hors_controle([c for c in d["cases"] if c["bras"] == b],
                                 b)["ce_que_loreille_achete"]
                for b in dict.fromkeys(c["bras"] for c in d["cases"])},
            "departs_raccourcis_pour_rien_par_bras": {g["nom"]: g["departs_raccourcis_pour_rien"]
                                                      for g in bras}}


def mesurer(matieres=MATIERES, bruits=BRUITS, bras=BRAS, departs: int = DEPARTS) -> dict:
    d = le_livrable(matieres, bruits, bras, departs)
    return {"livrable": d, "juger": juger(d)}


def reagreger(r: dict) -> dict:
    r["juger"] = juger(r["livrable"])
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
    marque = "★" if c["il_est_neutre"] else "✗"
    print(f"{marque} contrôle — sur la spirale NUE l'oreille ne change RIEN : "
          f"{c['livraisons_arretees_sur_la_pose']} marche arrêtée, "
          f"{c['pas_livres_sans']} pas livrés contre {c['pas_livres_avec']}")
    prefixe = "★" if j["toute_marche_qui_ecoute_est_un_prefixe"] else "✗"
    print(f"{prefixe} invariant — toute marche qui écoute est un PRÉFIXE de celle qui n'écoute pas")
    for titre, groupes in (("par bras", j["par_bras"]), ("par matière", j["par_matiere"])):
        print(f"\n   — {titre} —")
        print(f"   {'':>22} | {'sautent sans':>12} | {'sautent avec':>12} | "
              f"{'utiles sans':>11} | {'utiles avec':>11} | {'×':>7} | {'perdus':>6}")
        for g in groupes:
            r_ = g["ce_que_loreille_achete"]
            print(f"   {_court(g['nom']):>22} | "
                  f"{g['livraisons_qui_sautent_sans']:>4}/{g['apparies']:<7} | "
                  f"{g['livraisons_qui_sautent_avec']:>4}/{g['apparies']:<7} | "
                  f"{g['pas_utilisables_sans']:>11} | {g['pas_utilisables_avec']:>11} | "
                  f"{'—' if r_ is None else format(r_, 'g'):>7} | "
                  f"{g['departs_raccourcis_pour_rien']:>6}")
    print("\n★★★★ ce que l'oreille achète, en pas UTILISABLES, bras par bras :")
    hors = j.get("ce_que_loreille_achete_par_bras_hors_controle", {})
    for nom, gain in j["ce_que_loreille_achete_par_bras"].items():
        perdus = j["departs_raccourcis_pour_rien_par_bras"][nom]
        print(f"      {_court(nom):>22} : ×{gain}   hors contrôle ×{hors.get(nom)}   "
              f"({perdus} départs raccourcis pour rien)")
    print("   ⚠ le premier rapport inclut la spirale nue, qui livre autant des DEUX côtés :")
    print("     un terme identique au numérateur et au dénominateur ne peut que tirer vers un.")


def _suivi(pas: int, saute=None, fin: str = "tour bouclé") -> dict:
    return {"decidable": True, "pas": int(pas), "fin": fin, "poses_refusees": 0,
            **({} if saute is None else {"pas_qui_sautent": int(saute)})}


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

    print("— ce qu'une livraison dit, et ce qu'elle ne dit pas —")
    l1 = une_livraison(_suivi(300, 0))
    v("⭐⭐⭐ « fiable » veut dire QUE RIEN NE DIT LE CONTRAIRE, pas « vraie »",
      l1["a_saute"] is False and l1["sest_arretee_dessus"] is False)
    v("⚠⚠ une marche sans décompte de sauts ne PRÉTEND rien — elle ne vaut pas « propre »",
      une_livraison(_suivi(300))["a_saute"] is None)
    v("⚠ une marche indécidable n'est pas une livraison vide, elle n'en est pas une",
      une_livraison({"decidable": False}) is None)
    v("⭐⭐⭐ l'arrêt sur la pose se lit dans la RAISON, jamais deviné",
      une_livraison(_suivi(300, 0, "la pose se contredit"))["sest_arretee_dessus"] is True
      and une_livraison(_suivi(300, 0, "plafond de pas"))["sest_arretee_dessus"] is False)

    print("\n— l'invariant de préfixe est asserté, jamais supposé —")
    p = _apparier(_suivi(900, 0), _suivi(700, 0, "la pose se contredit"))
    v("⭐⭐⭐⭐ la marche qui écoute est un PRÉFIXE, et l'invariant le dit",
      p["est_un_prefixe"] is True and p["pas_perdus"] == 200)
    v("⭐⭐⭐⭐ ... et il TOMBE si l'arrêt a allongé la marche au lieu de la couper",
      _apparier(_suivi(700, 0), _suivi(900, 0))["est_un_prefixe"] is False,
      "ce serait que l'arrêt a changé la marche, pas qu'il l'a coupée")

    print("\n— la longueur UTILISABLE n'est pas la longueur livrée —")
    # ⚠⚠⚠ LA FIXTURE DOIT SEPARER LES DEUX LECTURES : un depart qui saute EN SILENCE livre
    # beaucoup de pas et ZERO pas utilisable, parce que rien ne dit ou le couper.
    muette = _apparier(_suivi(900, 3), _suivi(900, 3))
    sauvee = _apparier(_suivi(900, 1), _suivi(400, 0, "la pose se contredit"))
    propre = _apparier(_suivi(800, 0), _suivi(800, 0))
    coupee = _apparier(_suivi(800, 0), _suivi(500, 0, "la pose se contredit"))
    r = _resume([muette, sauvee, propre, coupee])
    v("⭐⭐⭐⭐ une livraison qui saute en silence ne vaut RIEN, quelle que soit sa longueur",
      r["pas_utilisables_sans"] == 800 + 800
      and r["pas_livres_sans"] == 900 + 900 + 800 + 800,
      f"{r['pas_utilisables_sans']} utilisables pour {r['pas_livres_sans']} livrés")
    v("⭐⭐⭐⭐ ... et l'oreille rend utilisable ce qui ne l'était pas",
      r["pas_utilisables_avec"] == 400 + 800 + 500,
      "la marche sauvée vaut ses 400 pas, là où elle en valait zéro")
    v("⚠⚠ une marche arrêtée sur la pose mais qui a QUAND MÊME sauté est comptée fausse",
      _resume([_apparier(_suivi(900, 2), _suivi(600, 1, "la pose se contredit"))]
              )["livraisons_qui_sautent_avec"] == 1,
      "la règle a parlé trop tard, donc ce qu'elle remet contient déjà du faux")
    # ⚠⚠⚠ LE SEUL AXE QUI PUISSE ECHOUER : une marche qui allait bien et qu'on raccourcit.
    v("⭐⭐⭐⭐ le seul axe qui puisse échouer est la longueur perdue sur un départ qui allait bien",
      r["departs_raccourcis_pour_rien"] == 1 and r["livraisons_arretees_sur_la_pose"] == 2,
      "deux arrêts, dont un seul sur une marche qui n'en avait pas besoin")
    # ⚠⚠⚠ ET LES DEUX MEDIANES NE DISENT PAS LA MEME CHOSE : celle de TOUS les arrets melange ce
    # qu'une marche sauvee abandonne — qui n'est pas une perte — et ce qu'une marche saine perd.
    # La figure affichait la premiere sous le titre de la seconde, et seul l'oeil l'a vu.
    v("⭐⭐⭐⭐ la médiane du COÛT ne porte que sur les marches qui allaient bien",
      r["pas_perdus_median"] == 400 and r["pas_perdus_pour_rien_median"] == 300,
      f"tous arrêts {r['pas_perdus_median']}, pour rien {r['pas_perdus_pour_rien_median']}")
    v("⚠⚠ ... et sans une seule marche coupée pour rien, cette médiane n'existe PAS",
      _resume([muette, sauvee])["pas_perdus_pour_rien_median"] is None
      and _resume([muette, sauvee])["pas_perdus_median"] == 500,
      "un arrêt qui sauve abandonne des pas, il n'en PERD pas")
    v("⚠ sans un seul départ apparié, le résumé le DIT",
      _resume([None, None])["decidable"] is False)

    print("\n— le cumul recalcule des SOMMES —")
    ca = _resume([muette, sauvee])
    cb = _resume([propre, coupee])
    cum = _cumuler([ca, cb], "deux")
    # ⚠⚠ L'ATTENDU SE DERIVE DES DEUX CASES.
    v("⭐⭐⭐ le rapport se recalcule des sommes, jamais en moyennant deux rapports",
      abs(cum["ce_que_loreille_achete"]
          - round(cum["pas_utilisables_avec"] / cum["pas_utilisables_sans"], 4)) < 1e-9
      and abs(cum["ce_que_loreille_achete"]
              - statistics.mean([ca["pas_utilisables_avec"] / max(ca["pas_utilisables_sans"], 1),
                                 cb["pas_utilisables_avec"] / cb["pas_utilisables_sans"]])) > 1e-3,
      f"{cum['ce_que_loreille_achete']}")
    v("⚠⚠ sans un seul pas utilisable SANS l'oreille, le rapport n'existe pas",
      _cumuler([_resume([muette])], "seule")["ce_que_loreille_achete"] is None,
      "diviser par zéro n'est pas un gain infini, c'est une absence de référence")

    print("\n— le contrôle a DEUX moitiés —")
    def case(nom, bras_, paires):
        return {"bras": bras_, "nom": nom, "ecrasement": 0.0, "amplitude_um": 0.0,
                "bruit": 0.0, **_resume(paires)}
    bon = {"decidable": True, "bras": ["p"], "bruits": [0.0], "departs": 2,
           "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [propre, propre]),
                     case("dure", "p", [muette, sauvee, coupee])]}
    j = juger(bon)
    v("⭐⭐⭐⭐ le contrôle tient quand l'oreille ne change RIEN sur la spirale nue",
      j["le_controle_de_la_spirale_nue"]["il_est_neutre"] is True)
    v("⭐⭐⭐⭐ ... et il TOMBE si elle y raccourcit ne serait-ce qu'une marche",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [propre, coupee]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_neutre"] is False,
      "la seconde moitié interdit à l'arrêt de coûter là où il n'y a rien à sauver")
    # ⚠⚠⚠ ET LA SECONDE MOITIE DOIT ETRE DECISIVE TOUTE SEULE, sinon elle n'est pas testee : la
    # fixture precedente declare AUSSI un arret sur la pose, donc la premiere moitie suffisait a
    # faire tomber le controle. Ici la longueur change SANS qu'aucun arret ne soit declare — ce
    # qui voudrait dire que l'oreille a change la marche autrement qu'en la coupant.
    sournoise = _apparier(_suivi(800, 0), _suivi(500, 0, "plafond de pas"))
    v("⭐⭐⭐⭐ ... et la SECONDE moitié tombe seule quand la longueur change sans arrêt déclaré",
      juger({**bon, "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [propre, sournoise]),
                              bon["cases"][1]]}
            )["le_controle_de_la_spirale_nue"]["il_est_neutre"] is False
      and _resume([propre, sournoise])["livraisons_arretees_sur_la_pose"] == 0,
      "aucun arrêt déclaré, et pourtant 300 pas de moins")
    # ⚠⚠⚠ UN RAPPORT DILUE PAR SON PROPRE CONTROLE : la fixture le montre avec des nombres
    # choisis pour que l'inclusion INVERSE le sens, ce qui est le cas reel.
    # ⚠⚠ LA FIXTURE PORTE UNE MARCHE PROPRE DANS LA MATIERE DURE, sans quoi le rapport hors
    # controle n'EXISTE pas (aucun pas utilisable sans l'oreille) et la sonde LEVE au lieu de
    # rendre faux — le piege de `157`, paye une fois de plus.
    dilue = {"decidable": True, "bras": ["p"], "bruits": [0.0], "departs": 2,
             "cases": [case(_nom(*LA_SPIRALE_NUE), "p", [propre] * 20),
                       case("dure", "p", [muette, muette, sauvee, propre])]}
    jd = juger(dilue)
    avec_ = jd["tout"].get("ce_que_loreille_achete")
    sans_ = jd["hors_controle"].get("ce_que_loreille_achete")
    v("⭐⭐⭐⭐ un rapport qui inclut le contrôle est tiré vers UN par construction",
      avec_ is not None and sans_ is not None and abs(avec_ - 1.0) < abs(sans_ - 1.0),
      f"avec le contrôle ×{avec_}, sans ×{sans_}")
    v("⚠⚠ ... et le contrôle n'est pas retiré de la MESURE, seulement de ce RAPPORT",
      jd["le_controle_de_la_spirale_nue"]["il_est_neutre"] is True
      and jd["tout"]["pas_utilisables_sans"] > jd["hors_controle"]["pas_utilisables_sans"])

    v("⭐⭐⭐ l'invariant de préfixe est publié au niveau du jugement",
      j["toute_marche_qui_ecoute_est_un_prefixe"] is True
      and juger({**bon, "cases": [case("x", "p", [_apparier(_suivi(700, 0), _suivi(900, 0))])]}
                )["toute_marche_qui_ecoute_est_un_prefixe"] is False)

    print("\n— `mesurer`, `reagreger`, `afficher` —")
    petite = mesurer(matieres=(LA_SPIRALE_NUE,), bruits=(0.0,), bras=(BRAS[0],), departs=2)
    v("⭐⭐⭐⭐ sur la spirale NUE la mesure réelle ne raccourcit AUCUNE marche",
      petite["juger"]["le_controle_de_la_spirale_nue"]["il_est_neutre"] is True,
      f"{petite['juger']['le_controle_de_la_spirale_nue']}")
    v("⭐⭐⭐ ... et toute marche qui écoute y est bien un préfixe",
      petite["juger"]["toute_marche_qui_ecoute_est_un_prefixe"] is True)
    # ⚠⚠⚠ ET SUR UNE MATIERE QUI SAUTE, LA REGLE DOIT REELLEMENT ARRETER. Sans ce controle, la
    # batterie ne verifiait JAMAIS sur donnees reelles que le branchement fonctionne : la spirale
    # nue ne declenche rien, donc debrancher l'arret n'y changeait rien et la sonde par cassure
    # passait au vert. C'est la sonde qui l'a dit, pas la relecture.
    dure = mesurer(matieres=(MATIERES[3],), bruits=(8.0,), bras=(BRAS[0],), departs=1)
    cas_dur = dure["livrable"]["cases"][0]
    v("⭐⭐⭐⭐ sur une matière qui saute, la règle ARRÊTE vraiment la marche",
      cas_dur["livraisons_arretees_sur_la_pose"] >= 1
      and cas_dur["pas_livres_avec"] < cas_dur["pas_livres_sans"],
      f"{cas_dur['pas_livres_sans']} pas livrés sans l'oreille, "
      f"{cas_dur['pas_livres_avec']} avec")
    avant = json.loads(json.dumps(petite["livrable"]))
    r2 = reagreger(json.loads(json.dumps(petite)))
    v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["livrable"] == avant)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"juger": j, "livrable": bon})
    sortie = tampon.getvalue()
    v("⚠ `afficher` rend le contrôle, l'invariant, les deux tableaux et le verdict",
      "contrôle" in sortie and "PRÉFIXE" in sortie and "par bras" in sortie
      and "par matière" in sortie and "achète" in sortie, f"{len(sortie)} caractères")
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
