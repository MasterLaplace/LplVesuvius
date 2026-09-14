#!/usr/bin/env python3
"""Poser DEUX FOIS : le second temps redresse-t-il la normale, et à quel prix ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST LA SEULE PISTE QUE `150` N'AIT PAS FERMÉE. Les mâchoires ont
besoin d'une direction DROITE et FRAÎCHE. Les deux sources disponibles sont épuisées : le MÉLANGE du
cap est frais et penché — `148` mesure **40,569°** sur la matière du rouleau, et `150` que la pose y
tombe à **633 ‰** contre 917 à normale droite ; la LECTURE PRÉCÉDENTE est droite et date d'un quart
de période — `150` mesure 96 réussites contre 108. La troisième source n'emprunte ni l'une ni
l'autre : **poser une première fois pour LIRE la normale ici et maintenant, puis poser une seconde
fois dessus**. Aucune constante n'entre, c'est deux appels au lieu d'un.

⚠⚠⚠ ET LA PREMIÈRE CHOSE À DIRE EST UN THÉORÈME, PAS UNE MESURE. Le second temps n'a lieu que si le
premier a rendu quelque chose, donc `P(deux temps) <= P(un temps)` **par construction**. Une pose en
deux temps ne peut pas réussir plus souvent qu'une pose simple, et aller le « mesurer » sur une
grille serait payer une grille pour retrouver une conjonction. Ce que le second temps peut acheter
n'est donc PAS un taux de pose : c'est la **justesse de la normale rendue**, qui décide de la pose
SUIVANTE. C'est cette justesse que ce fichier mesure.

⭐⭐⭐ ET LA MESURE NE MARCHE PAS, ELLE POSE. `149` établit que ce qui tue une marche est le refus de
pose ; `150` a montré qu'une pose se teste seule, à un départ recalé, pour quelques lectures — mille
fois moins cher qu'une grille. La question se pose donc à la pose AVANT de payer quoi que ce soit.

⚠⚠ LE NIVEAU DE L'ERREUR PORTE UN BIAIS, LA DIFFÉRENCE APPARIÉE N'EN PORTE PAS. Une mâchoire de
demi-largeur `w` suit le plan MOYEN de la feuille sur `w`, jamais sa normale ponctuelle — c'est
pourquoi `le_prix_dune_normale` ne se mesure que sur une spirale sans froissement. Sur une matière
froissée, l'écart à la normale ponctuelle contient donc un biais qu'aucune pose ne peut enlever.
Mais ce biais est le MÊME aux deux temps, puisque c'est la même mâchoire au même point : seule la
différence **appariée sur le même départ** est lisible, et c'est elle qui porte le verdict. Le niveau
est publié pour être lu, jamais pour décider.

⚠ UN TROISIÈME TEMPS EST POSÉ, ET IL NE COÛTE RIEN À LA MESURE. Il ne sert pas à proposer un bras à
trois temps : il dit si la pose est une ITÉRATION qui converge ou une correction à un coup. Les deux
se ressemblent sur deux points et pas sur trois.

Usage :
    uv run python src/nappe/la_pose_en_deux_temps.py --verifier
    uv run python src/nappe/la_pose_en_deux_temps.py \\
        --json docs/mesures/la_pose_en_deux_temps.json
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

from la_pince_tient_elle_la_feuille import (LARGEUR_DE_REFERENCE,  # noqa: E402
                                            LONGUEUR_DONDE_UM, MATIERES, RAYON_MM, _ecart_deg,
                                            _matiere, _nom, _PAS, _tourner, _VOXEL, poser,
                                            un_depart)

POSES = 60
INCLINAISONS_DEG = (0.0, 10.0, 20.0, 30.0, 40.0, 50.0)
TEMPS = 3
LE_PENCHANT = RACINE / "docs" / "mesures" / "la_memoire_fait_elle_avancer_de_travers.json"


def _poser_n_fois(vol, depart, graine_normale, largeur_um: float, pas_um: float,
                  voxel_um: float, temps: int = TEMPS) -> tuple[list, list[int]]:
    """Poser `temps` fois de suite, chacune sur la normale que la précédente a rendue.

    ⚠⚠ LE CENTRE NE BOUGE PAS. Repartir du centre trouvé changerait deux choses à la fois — la
    direction et le point — et aucune ne serait imputable. Le suiveur n'a pas avancé entre les
    temps ; seule sa direction a été relue.

    Rend la liste des états (elle s'arrête au premier refus) et le compte de lectures de chaque
    temps, pour que le prix soit publié plutôt qu'estimé.
    """
    etats, lectures = [], []
    n = np.asarray(graine_normale, dtype=np.float64)
    for _ in range(int(temps)):
        vol.lectures = 0
        e = poser(vol, depart, n, largeur_um, pas_um, voxel_um, True)
        lectures.append(int(vol.lectures))
        if e is None:
            break
        etats.append(e)
        n = e["normale"]
    return etats, lectures


def le_second_temps_redresse_t_il(matieres=MATIERES, inclinaisons=INCLINAISONS_DEG,
                                  poses: int = POSES, temps: int = TEMPS) -> dict:
    """De combien le second temps redresse-t-il la normale, et combien de poses il coûte.

    ⭐⭐⭐ LA COMPARAISON EST APPARIÉE SUR LE DÉPART, et c'est ce qui la rend lisible malgré le biais
    du plan moyen : les deux temps sont la même mâchoire au même point, donc leur différence ne
    porte que ce que le second temps a changé.

    ⚠ Les départs sont ceux d'`un_depart`, recalés EXACTEMENT sur une feuille, et la normale qu'il
    rend est la VRAIE normale locale — analytique, donc elle ne coûte aucune lecture.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    largeur_um = LARGEUR_DE_REFERENCE * pas_um
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        departs = [un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um, pas_um)
                   for k in range(int(poses))]
        bloc = {"nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
                "poses": int(poses), "par_inclinaison": []}
        for deg in inclinaisons:
            e1s, e2s, e3s, paires, paires3, cv = [], [], [], [], [], []
            n1, n2, n3 = 0, 0, 0
            l1, l2 = [], []
            for d0, vrai in departs:
                graine = _tourner(vrai, np.radians(float(deg)))
                etats, lect = _poser_n_fois(vol, d0, graine, largeur_um, pas_um, voxel_um, temps)
                if len(etats) >= 1:
                    n1 += 1
                    l1.append(lect[0])
                    e1s.append(_ecart_deg(etats[0]["normale"], vrai))
                if len(etats) >= 2:
                    n2 += 1
                    l2.append(lect[0] + lect[1])
                    e2s.append(_ecart_deg(etats[1]["normale"], vrai))
                    # ⚠⚠ LA PAIRE SE PREND SUR LE MÊME DÉPART, jamais entre deux médianes : la
                    # variabilité d'un départ à l'autre dépasse largement ce que le second temps
                    # déplace, donc une différence de médianes serait décidée par le tirage.
                    paires.append(_ecart_deg(etats[1]["normale"], vrai)
                                  - _ecart_deg(etats[0]["normale"], vrai))
                    cv.append(_ecart_deg(etats[1]["normale"], etats[0]["normale"]))
                if len(etats) >= 3:
                    n3 += 1
                    e3s.append(_ecart_deg(etats[2]["normale"], vrai))
                    # ⚠⚠ LE TROISIEME TEMPS S'APPARIE AUSSI. Comparer la mediane a trois temps a
                    # celle a deux serait comparer deux POPULATIONS : celles qui survivent au
                    # troisieme temps ne sont pas celles qui survivent au second, et une mediane
                    # sur un melange n'est pas un resume.
                    paires3.append(_ecart_deg(etats[2]["normale"], vrai)
                                   - _ecart_deg(etats[1]["normale"], vrai))
            # ⚠ Une case sans aucune pose ne se lit pas comme une case à zéro degré d'erreur :
            # elle est SAUTÉE et comptée, parce qu'un `None` publié comme `0.0` ferait lire une
            # pose parfaite là où il n'y a eu aucune pose.
            bloc["par_inclinaison"].append({
                "inclinaison_deg": float(deg),
                "posees_un_temps": int(n1), "posees_deux_temps": int(n2),
                "posees_trois_temps": int(n3),
                "part_un_temps_pour_mille": int(round(1000.0 * n1 / max(int(poses), 1))),
                "part_deux_temps_pour_mille": int(round(1000.0 * n2 / max(int(poses), 1))),
                "perdues_au_second_temps": int(n1 - n2),
                "erreur_un_temps_deg": (round(float(np.median(e1s)), 3) if e1s else None),
                "erreur_deux_temps_deg": (round(float(np.median(e2s)), 3) if e2s else None),
                "erreur_trois_temps_deg": (round(float(np.median(e3s)), 3) if e3s else None),
                "ecart_apparie_deg": (round(float(np.median(paires)), 3) if paires else None),
                "ecart_apparie_du_troisieme_deg": (round(float(np.median(paires3)), 3)
                                                   if paires3 else None),
                "redressees": int(sum(1 for x in paires if x < 0.0)),
                "degradees": int(sum(1 for x in paires if x > 0.0)),
                "appariees": int(len(paires)),
                "deplacement_du_second_temps_deg": (round(float(np.median(cv)), 3) if cv
                                                    else None),
                "lectures_un_temps": (int(np.median(l1)) if l1 else None),
                "lectures_deux_temps": (int(np.median(l2)) if l2 else None)})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses), "temps": int(temps),
            "largeur_de_reference": float(LARGEUR_DE_REFERENCE),
            "inclinaisons_deg": [float(x) for x in inclinaisons],
            "par_matiere": out}


def langle_que_148_mesure(penchant: dict | None) -> float | None:
    """L'inclinaison que `148` mesure sur la matière du rouleau — LUE, jamais recopiée.

    ⚠ Sans sa mesure, le verdict décisif est indécidable et le dit. Un angle recopié à la main
    redeviendrait faux le jour où `148` se recalcule.
    """
    if not penchant:
        return None
    v = next((x for x in penchant.get("juger", {}).get("par_variante", [])
              if x.get("fenetre") and not x.get("avance_sur_la_lecture")), None)
    if v is None:
        return None
    dure = next((m for m in v.get("par_matiere", []) if "100" in m["nom"]), None)
    return None if dure is None else float(dure["inclinaison_mediane_deg"])


def juger(redresse: dict, penchant: dict | None) -> dict:
    """Le second temps redresse-t-il, et que coûte-t-il — deux énoncés SÉPARÉS.

    ⭐⭐⭐⭐ LE VERDICT DÉCISIF EST UNE SEULE CASE : la matière que `140` retient, à l'inclinaison
    que `148` mesure vraiment. C'est là que la pince meurt, donc c'est là que la question se pose.

    ⚠⚠ ET « IL REDRESSE » NE VEUT PAS DIRE « IL FAUT LE PRENDRE ». Le prix est un compte de poses
    PERDUES — celles qui survivent au premier temps et pas au second — et il s'énonce à part. Les
    mélanger ferait un verdict que ni l'un ni l'autre ne soutient.

    ⚠ L'unanimité se lit sur les matières qui FROISSENT : `R4-F108` établit qu'un cap ne s'engage
    que là, donc c'est le seul endroit où l'inclinaison du cap existe.
    """
    if not redresse.get("decidable"):
        return {"decidable": False, "raison": "aucune pose mesurée"}
    fort = max(redresse["inclinaisons_deg"])
    par = []
    for m in redresse["par_matiere"]:
        f = next((x for x in m["par_inclinaison"] if x["inclinaison_deg"] == fort), None)
        if f is None or f["ecart_apparie_deg"] is None:
            continue
        par.append({"nom": m["nom"], "amplitude_um": m["amplitude_um"],
                    "ecart_apparie_deg": f["ecart_apparie_deg"],
                    "redressees": f["redressees"], "degradees": f["degradees"],
                    "appariees": f["appariees"],
                    "perdues_au_second_temps": f["perdues_au_second_temps"],
                    "il_redresse": bool(f["ecart_apparie_deg"] < 0.0)})
    froissees = [x for x in par if x["amplitude_um"] > 0.0]
    out = {"decidable": bool(par), "inclinaison_forte_deg": fort, "par_matiere": par,
           "il_redresse_partout": bool(par and all(x["il_redresse"] for x in par)),
           "il_redresse_sur_les_froissees": bool(froissees
                                                 and all(x["il_redresse"] for x in froissees)),
           "poses_perdues_au_total": int(sum(x["perdues_au_second_temps"] for x in par))}
    # ⭐⭐⭐⭐ LE PARTAGE PAR CAUSE, ET C'EST LUI QUI PORTE L'ENONCE. Une mediane sur les cinq
    # matieres moyennerait sur l'axe ou la difference vit. Le parametre qui DEFINIT la matiere est
    # le couple (ecrasement, froissement), et les deux ensemble ne se lisent pas comme chacun seul.
    # ⚠ La conclusion est UNANIME ou nulle : une seule matiere du groupe qui n'obeit pas suffit.
    out["par_cause"] = []
    for nom, choisir in (("une cause au plus",
                          lambda x: not (x["ecrasement"] > 0.0 and x["amplitude_um"] > 0.0)),
                         ("écrasée ET froissée",
                          lambda x: x["ecrasement"] > 0.0 and x["amplitude_um"] > 0.0)):
        lignes = []
        for m in redresse["par_matiere"]:
            if not choisir(m):
                continue
            for x in m["par_inclinaison"]:
                if x["ecart_apparie_deg"] is not None and x["inclinaison_deg"] > 0.0:
                    lignes.append(x["ecart_apparie_deg"])
        if not lignes:
            continue
        out["par_cause"].append({
            "cause": nom, "cases": len(lignes),
            "ecart_apparie_median_deg": round(float(np.median(lignes)), 3),
            "cases_qui_redressent": int(sum(1 for y in lignes if y < 0.0)),
            "cases_qui_degradent": int(sum(1 for y in lignes if y > 0.0)),
            # ⚠⚠ UN ECART EXACTEMENT NUL N'EST NI L'UN NI L'AUTRE, donc l'unanimite se lit
            # « aucune ne degrade » et non « toutes redressent » : une case sans rien a redresser
            # ferait sinon tomber l'unanimite d'un groupe qui n'a jamais degrade.
            "unanime": bool(sum(1 for y in lignes if y > 0.0) == 0
                            or sum(1 for y in lignes if y < 0.0) == 0),
            "il_redresse": bool(sum(1 for y in lignes if y > 0.0) == 0
                                and any(y < 0.0 for y in lignes))})
    # ⚠ Les deux groupes disent-ils des choses OPPOSEES ? C'est l'enonce du fichier, et il peut
    # etre faux : si les deux redressent, ou si aucun n'est unanime, il n'y a rien a partager.
    g = {x["cause"]: x for x in out["par_cause"]}
    a_, b_ = g.get("une cause au plus"), g.get("écrasée ET froissée")
    # ⚠ L'enonce ne revendique PAS l'unanimite des deux groupes : un groupe peut porter une case
    # qui va dans l'autre sens sans que le partage cesse d'etre vrai. Ce qu'il revendique est que
    # l'un ne degrade JAMAIS et que l'autre degrade EN MEDIANE — deux enonces verifiables et
    # tombant tous les deux si la mesure change de sens.
    out["les_deux_causes_ensemble_sont_a_part"] = bool(
        a_ and b_ and a_["il_redresse"] and b_["ecart_apparie_median_deg"] > 0.0)
    angle = langle_que_148_mesure(penchant)
    if angle is None:
        out["a_langle_du_cap"] = {"decidable": False,
                                  "raison": "l'angle de `148` n'est pas mesuré ici"}
        return out
    mat = next((m for m in redresse["par_matiere"] if m["amplitude_um"] == 100.0), None)
    if mat is None:
        out["a_langle_du_cap"] = {"decidable": False, "raison": "la matière de `140` est absente"}
        return out
    proche = min(mat["par_inclinaison"], key=lambda x: abs(x["inclinaison_deg"] - angle))
    out["a_langle_du_cap"] = {
        "decidable": proche["ecart_apparie_deg"] is not None,
        "matiere": mat["nom"], "inclinaison_du_cap_deg": round(angle, 3),
        "inclinaison_mesuree_la_plus_proche_deg": proche["inclinaison_deg"],
        "erreur_un_temps_deg": proche["erreur_un_temps_deg"],
        "erreur_deux_temps_deg": proche["erreur_deux_temps_deg"],
        "erreur_trois_temps_deg": proche["erreur_trois_temps_deg"],
        "ecart_apparie_deg": proche["ecart_apparie_deg"],
        "redressees": proche["redressees"], "degradees": proche["degradees"],
        "appariees": proche["appariees"],
        "perdues_au_second_temps": proche["perdues_au_second_temps"],
        "part_un_temps_pour_mille": proche["part_un_temps_pour_mille"],
        "part_deux_temps_pour_mille": proche["part_deux_temps_pour_mille"],
        "lectures_un_temps": proche["lectures_un_temps"],
        "lectures_deux_temps": proche["lectures_deux_temps"],
        "il_redresse": bool(proche["ecart_apparie_deg"] is not None
                            and proche["ecart_apparie_deg"] < 0.0)}
    # ⭐⭐ ITÉRATION OU CORRECTION À UN COUP : un troisième temps qui déplace encore autant que le
    # second dit une itération ; un troisième qui ne bouge plus dit une correction à un coup. Les
    # deux ne se réparent pas de la même façon, et deux points ne les distinguent pas.
    #
    # ⚠⚠ IL SE LIT APPARIÉ, comme le second. La médiane à trois temps porte sur les poses qui ont
    # survécu à trois temps, celle à deux temps sur celles qui ont survécu à deux : leur différence
    # mêlerait un effet et un changement de population.
    out["a_langle_du_cap"]["le_troisieme_temps_ajoute_deg"] = \
        proche.get("ecart_apparie_du_troisieme_deg")
    return out


def mesurer(matieres=MATIERES, inclinaisons=INCLINAISONS_DEG, poses: int = POSES,
            temps: int = TEMPS, penchant: Path = LE_PENCHANT) -> dict:
    p = json.loads(penchant.read_text()) if penchant.is_file() else None
    redresse = le_second_temps_redresse_t_il(matieres, inclinaisons, poses, temps)
    return {"redresse": redresse, "juger": juger(redresse, p),
            "penchant_lu": bool(p)}


def reagreger(r: dict, penchant: Path = LE_PENCHANT) -> dict:
    p = json.loads(penchant.read_text()) if penchant.is_file() else None
    r["juger"] = juger(r["redresse"], p)
    r["penchant_lu"] = bool(p)
    return r


def afficher(r: dict) -> None:
    red, jug = r["redresse"], r["juger"]
    print("\n⭐ LE SECOND TEMPS REDRESSE-T-IL LA NORMALE ? — écart à la vraie normale, en degrés")
    print(f"   {red['poses_par_case']} poses par case, largeur de référence, départs recalés\n")
    print(f"   {'matière':<32} {'incl.':>6} {'1 temps':>9} {'2 temps':>9} "
          f"{'apparié':>9} {'redr.':>6} {'dégr.':>6} {'perdues':>8}")
    for m in red["par_matiere"]:
        for x in m["par_inclinaison"]:
            e1 = "—" if x["erreur_un_temps_deg"] is None else f"{x['erreur_un_temps_deg']:.3f}°"
            e2 = "—" if x["erreur_deux_temps_deg"] is None else f"{x['erreur_deux_temps_deg']:.3f}°"
            ap = "—" if x["ecart_apparie_deg"] is None else f"{x['ecart_apparie_deg']:+.3f}°"
            print(f"   {m['nom']:<32} {x['inclinaison_deg']:>5.0f}° {e1:>9} {e2:>9} "
                  f"{ap:>9} {x['redressees']:>6} {x['degradees']:>6} "
                  f"{x['perdues_au_second_temps']:>8}")
    if not jug.get("decidable"):
        print(f"\n⚠ {jug.get('raison')}")
        return
    d = jug.get("a_langle_du_cap", {})
    if d.get("decidable"):
        print(f"\n⭐⭐⭐⭐ À L'ANGLE QUE `148` MESURE — {d['matiere']}, "
              f"{d['inclinaison_du_cap_deg']}° (mesuré à {d['inclinaison_mesuree_la_plus_proche_deg']}°)")
        print(f"   erreur   {d['erreur_un_temps_deg']}° → {d['erreur_deux_temps_deg']}° "
              f"→ {d['erreur_trois_temps_deg']}°  ⚠ trois populations, à lire jamais à décider")
        print(f"   apparié  second temps {d['ecart_apparie_deg']:+}°   "
              f"troisième temps {d['le_troisieme_temps_ajoute_deg']:+}°")
        print(f"   poses    {d['part_un_temps_pour_mille']} ‰ → {d['part_deux_temps_pour_mille']} ‰"
              f"   ({d['perdues_au_second_temps']} perdues au second temps)")
        print(f"   lectures {d['lectures_un_temps']} → {d['lectures_deux_temps']}")
        print(f"\n   {'⭐ il REDRESSE' if d['il_redresse'] else '⛔ il ne redresse PAS'}"
              f" — {d['redressees']} redressées contre {d['degradees']} dégradées "
              f"sur {d['appariees']} appariées")
    else:
        print(f"\n⚠ angle du cap indécidable : {d.get('raison')}")
    if jug.get("par_cause"):
        print("\n⭐⭐⭐ LE PARTAGE PAR CAUSE — écart apparié médian, inclinaisons non nulles")
        for c in jug["par_cause"]:
            print(f"   {c['cause']:<22} {c['ecart_apparie_median_deg']:+7.3f}°  "
                  f"{c['cases_qui_redressent']:>2} redressent · "
                  f"{c['cases_qui_degradent']:>2} dégradent  sur {c['cases']:>2} cases"
                  f"{'  (unanime)' if c['unanime'] else ''}")
        print(f"\n   les deux causes ensemble sont à part : "
              f"{'OUI' if jug['les_deux_causes_ensemble_sont_a_part'] else 'non'}")
    print(f"\n   unanimité sur les froissées : "
          f"{'oui' if jug['il_redresse_sur_les_froissees'] else 'non'}"
          f" · poses perdues au total {jug['poses_perdues_au_total']}")


def verifier() -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        # ⚠ Le compte est DERIVE, jamais ecrit a la main : un nombre figé redevient faux au premier
        # contrôle ajouté, et il ne le dit pas.
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)

    # ---- ⭐⭐ le mécanisme lui-même, sur une matière dont la réponse est connue
    nue = _matiere(VolumeFabriqueEnSpiraleFroissee, 0.0, 0.0, 0.0, LONGUEUR_DONDE_UM, RAYON_MM)
    d0, vrai = un_depart(nue, 0.0, RAYON_MM, voxel_um, pas_um)
    etats, lect = _poser_n_fois(nue, d0, _tourner(vrai, np.radians(30.0)),
                                LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, 3)
    v("⭐ trois temps se posent, et chacun part de la normale du précédent", len(etats) == 3,
      f"{len(etats)} états")
    v("⭐⭐ sur une spirale nue le premier temps redresse déjà presque tout",
      len(etats) >= 1 and _ecart_deg(etats[0]["normale"], vrai) < 1.0,
      f"{_ecart_deg(etats[0]['normale'], vrai):.4f}° pour une graine à 30°")
    v("... et le second finit le travail",
      len(etats) >= 2
      and _ecart_deg(etats[1]["normale"], vrai) <= _ecart_deg(etats[0]["normale"], vrai),
      f"{_ecart_deg(etats[0]['normale'], vrai):.4f}° → {_ecart_deg(etats[1]['normale'], vrai):.4f}°")
    v("⚠ et chaque temps coûte le même nombre de lectures",
      len(set(lect)) == 1 and lect[0] > 0, f"{lect}")

    # ---- ⚠⚠⚠ LA SONDE QUI MORD : une normale DÉJÀ juste n'a rien à corriger, donc les trois
    # temps doivent rendre le MÊME état. Une implémentation qui repartirait du centre trouvé au
    # lieu du centre du départ échouerait ici, et c'est exactement le bug qu'on veut exclure.
    memes, _ = _poser_n_fois(nue, d0, vrai, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, 3)
    v("⭐⭐⭐ sur une normale déjà juste, les trois temps rendent la MÊME normale",
      len(memes) == 3 and all(_ecart_deg(memes[0]["normale"], x["normale"]) < 1e-9
                              for x in memes),
      "sinon le second temps déplacerait le centre, pas seulement la direction")
    v("... et le MÊME centre",
      len(memes) == 3
      and all(float(np.linalg.norm(np.asarray(memes[0]["centre_vx"])
                                   - np.asarray(x["centre_vx"]))) < 1e-9 for x in memes))

    # ---- ⚠⚠ le refus se propage : si le premier temps échoue, la liste est VIDE et pas courte
    loin = np.array([1e9, 1e9, 1e9])
    rien, _l = _poser_n_fois(nue, loin, vrai, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, 3)
    v("⚠ hors du volume, aucun temps ne se pose et la liste est vide", rien == [],
      f"{len(rien)} états")

    # ---- ⭐⭐ l'agrégat : une case fabriquée, dont la réponse est connue
    petit = le_second_temps_redresse_t_il(matieres=((0.0, 0.0),), inclinaisons=(0.0, 30.0),
                                          poses=6, temps=3)
    v("une case rend une ligne par inclinaison",
      petit["decidable"] and len(petit["par_matiere"][0]["par_inclinaison"]) == 2)
    z = petit["par_matiere"][0]["par_inclinaison"][0]
    v("⭐⭐ à inclinaison NULLE sur une spirale nue, l'écart apparié est nul",
      z["ecart_apparie_deg"] is not None and abs(z["ecart_apparie_deg"]) < 1e-3,
      f"{z['ecart_apparie_deg']}° — il n'y a rien à redresser")
    t30 = petit["par_matiere"][0]["par_inclinaison"][1]
    v("⭐⭐⭐ ... et à 30° il est NÉGATIF, donc le second temps redresse",
      t30["ecart_apparie_deg"] is not None and t30["ecart_apparie_deg"] <= 0.0,
      f"{t30['ecart_apparie_deg']:+}°")
    v("⚠ le compte des appariées ne dépasse jamais celui des posées à un temps",
      all(x["appariees"] <= x["posees_un_temps"]
          and x["posees_deux_temps"] <= x["posees_un_temps"]
          for x in petit["par_matiere"][0]["par_inclinaison"]),
      "c'est la conjonction, et elle doit se voir dans les comptes")
    v("⚠ le troisième temps est apparié lui aussi, et il ne se publie que s'il existe",
      all((x["ecart_apparie_du_troisieme_deg"] is None) == (x["posees_trois_temps"] == 0)
          for x in petit["par_matiere"][0]["par_inclinaison"]),
      "une case sans troisième pose ne rend pas zéro, elle rend rien")
    v("⚠ redressées plus dégradées ne dépasse jamais les appariées",
      all(x["redressees"] + x["degradees"] <= x["appariees"]
          for x in petit["par_matiere"][0]["par_inclinaison"]),
      "un écart exactement nul n'est ni l'un ni l'autre")
    v("⚠ le prix est publié, et deux temps lisent deux fois un temps",
      all(x["lectures_deux_temps"] == 2 * x["lectures_un_temps"]
          for x in petit["par_matiere"][0]["par_inclinaison"]
          if x["lectures_un_temps"] and x["lectures_deux_temps"]))

    # ---- ⚠⚠⚠ LE VERDICT PEUT-IL ÉCHOUER ? On lui donne une case où le second temps DÉGRADE.
    faux = {"decidable": True, "inclinaisons_deg": [0.0, 50.0], "poses_par_case": 6, "temps": 3,
            "par_matiere": [{"nom": "spirale écrasée et froissée 100 µm", "amplitude_um": 100.0,
                             "ecrasement": 0.2782, "poses": 6, "par_inclinaison": [
                                 {"inclinaison_deg": 0.0, "ecart_apparie_deg": 0.0,
                                  "redressees": 0, "degradees": 0, "appariees": 6,
                                  "perdues_au_second_temps": 0, "erreur_un_temps_deg": 1.0,
                                  "erreur_deux_temps_deg": 1.0, "erreur_trois_temps_deg": 1.0,
                                  "part_un_temps_pour_mille": 1000,
                                  "part_deux_temps_pour_mille": 1000,
                                  "lectures_un_temps": 100, "lectures_deux_temps": 200},
                                 {"inclinaison_deg": 50.0, "ecart_apparie_deg": +0.5,
                                  "redressees": 1, "degradees": 5, "appariees": 6,
                                  # ⚠ La difference des MEDIANES vaut +0,1 (2,6 − 2,5) et la
                                  # paire vaut −0,4 : les deux sont de SIGNE OPPOSE, expres.
                                  "ecart_apparie_du_troisieme_deg": -0.4,
                                  "perdues_au_second_temps": 2, "erreur_un_temps_deg": 2.0,
                                  "erreur_deux_temps_deg": 2.5, "erreur_trois_temps_deg": 2.6,
                                  "part_un_temps_pour_mille": 1000,
                                  "part_deux_temps_pour_mille": 667,
                                  "lectures_un_temps": 100, "lectures_deux_temps": 200}]}]}
    penchant_faux = {"juger": {"par_variante": [
        {"fenetre": 32, "avance_sur_la_lecture": False,
         "par_matiere": [{"nom": "spirale écrasée et froissée 100 µm",
                          "inclinaison_mediane_deg": 50.0}]}]}}
    jf = juger(faux, penchant_faux)
    v("⭐⭐⭐ le verdict DIT NON quand le second temps dégrade",
      jf["decidable"] and not jf["il_redresse_partout"]
      and not jf["a_langle_du_cap"]["il_redresse"],
      f"{jf['a_langle_du_cap']['ecart_apparie_deg']:+}°")
    v("... et il compte les poses perdues", jf["poses_perdues_au_total"] == 2,
      f"{jf['poses_perdues_au_total']}")
    # ⚠⚠⚠ LA SONDE QUI MORD SUR LE TROISIEME TEMPS : la fixture porte une difference de medianes
    # (+0,1) et une paire (−0,4) de SIGNES OPPOSES. Un verdict qui lirait les medianes rendrait
    # +0,1, et il se ferait decider par un changement de population au lieu d'un effet.
    v("⭐⭐⭐ le troisième temps se lit APPARIÉ, jamais en différence de médianes",
      jf["a_langle_du_cap"]["le_troisieme_temps_ajoute_deg"] == -0.4,
      f"{jf['a_langle_du_cap']['le_troisieme_temps_ajoute_deg']} — les médianes diraient +0.1")
    # ---- ⭐⭐⭐ LE PARTAGE PAR CAUSE, et ses deux sondes
    def _cause(ecr, amp, ecarts):
        return {"nom": _nom(ecr, amp), "amplitude_um": amp, "ecrasement": ecr, "poses": 6,
                "par_inclinaison": [
                    {"inclinaison_deg": float(10 * (i + 1)), "ecart_apparie_deg": e,
                     "ecart_apparie_du_troisieme_deg": 0.0, "redressees": 3, "degradees": 3,
                     "appariees": 6, "perdues_au_second_temps": 0, "erreur_un_temps_deg": 1.0,
                     "erreur_deux_temps_deg": 1.0, "erreur_trois_temps_deg": 1.0,
                     "posees_un_temps": 6, "posees_deux_temps": 6, "posees_trois_temps": 6,
                     "part_un_temps_pour_mille": 1000, "part_deux_temps_pour_mille": 1000,
                     "lectures_un_temps": 100, "lectures_deux_temps": 200}
                    for i, e in enumerate(ecarts)]}

    partage = juger({"decidable": True, "inclinaisons_deg": [10.0, 20.0], "poses_par_case": 6,
                     "temps": 3, "par_matiere": [_cause(0.0, 0.0, [0.0, -0.2]),
                                                 _cause(0.3, 50.0, [+0.4, +0.6])]}, None)
    g = {x["cause"]: x for x in partage["par_cause"]}
    v("⭐⭐ un écart exactement NUL ne casse pas l'unanimité d'un groupe qui n'a jamais dégradé",
      g["une cause au plus"]["unanime"] and g["une cause au plus"]["il_redresse"],
      "un zéro n'est ni une amélioration ni une dégradation")
    v("⭐⭐⭐ ... et les deux causes ENSEMBLE se lisent à part",
      partage["les_deux_causes_ensemble_sont_a_part"] is True,
      f"{g['une cause au plus']['ecart_apparie_median_deg']:+} contre "
      f"{g['écrasée ET froissée']['ecart_apparie_median_deg']:+}")
    # ⚠⚠⚠ LA SONDE QUI MORD : si les deux groupes redressent, il n'y a RIEN à partager, et le
    # verdict doit le dire. Sans elle, « les deux causes sont à part » serait vrai par construction.
    pareil = juger({"decidable": True, "inclinaisons_deg": [10.0, 20.0], "poses_par_case": 6,
                    "temps": 3, "par_matiere": [_cause(0.0, 0.0, [-0.1, -0.2]),
                                                _cause(0.3, 50.0, [-0.4, -0.6])]}, None)
    v("⭐⭐⭐ le partage DIT NON quand les deux groupes vont dans le même sens",
      pareil["les_deux_causes_ensemble_sont_a_part"] is False,
      "sinon l'énoncé serait vrai quelle que soit la mesure")

    v("⚠ sans la mesure de `148`, l'angle du cap est déclaré indécidable et ne se devine pas",
      juger(faux, None)["a_langle_du_cap"]["decidable"] is False)
    v("⚠ ... et le reste du verdict reste décidable sans lui",
      juger(faux, None)["decidable"] is True,
      "un angle manquant ne doit pas effacer ce qui est mesuré")

    # ---- ⚠⚠ LE CHEMIN QUI PUBLIE LE NOMBRE EST EXERCÉ, pas seulement les fonctions de calcul.
    # `mesurer`, `reagreger` et `afficher` sont ce qui écrit et rend le JSON publié ; une batterie
    # qui ne les atteint pas laisse la moitié qui PUBLIE sans garde, ce que `R5-F04` chiffre à 67
    # modules sur 160. La matière est INJECTÉE — une matière, deux inclinaisons, six poses — et
    # jamais le découpage : les nombres publiés ne bougent pas d'une virgule.
    import io  # noqa: PLC0415
    import contextlib  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as dossier:
        absent = Path(dossier) / "pas_de_penchant.json"
        r = mesurer(matieres=((0.0, 0.0),), inclinaisons=(0.0, 30.0), poses=4, temps=3,
                    penchant=absent)
        v("⭐⭐ `mesurer` rend un jugement et dit qu'il n'a pas lu le penchant",
          r["juger"]["decidable"] and r["penchant_lu"] is False,
          "un fichier absent se DIT, il ne se devine pas")
        chemin = Path(dossier) / "mesure.json"
        chemin.write_text(json.dumps(r, ensure_ascii=False))
        avant = json.loads(chemin.read_text())["redresse"]
        r2 = reagreger(json.loads(chemin.read_text()), penchant=absent)
        # ⚠⚠ UN REAGREGAT NE RECALCULE PAS LA MESURE, il relit le verdict : si la partie mesurée
        # bougeait, `--reagreger` serait une seconde mesure sous un nom qui promet le contraire.
        v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré",
          r2["redresse"] == avant, "il relit le verdict, il ne remesure rien")
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(r2)
        sortie = tampon.getvalue()
        v("⚠ `afficher` rend le partage par cause et le dit sans le dessiner",
          "LE PARTAGE PAR CAUSE" in sortie and "écart apparié médian" in sortie,
          f"{len(sortie)} caractères")
        # ⚠ Un jugement indecidable doit s'AFFICHER comme tel, jamais planter ni se taire.
        tampon2 = io.StringIO()
        with contextlib.redirect_stdout(tampon2):
            afficher({"redresse": {"decidable": False, "poses_par_case": 0, "par_matiere": []},
                      "juger": {"decidable": False, "raison": "aucune pose mesurée"}})
        v("⚠ ... et un jugement indécidable se DIT au lieu de planter",
          "aucune pose mesurée" in tampon2.getvalue())

    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} "
          f"({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--reagreger", type=Path)
    ap.add_argument("--poses", type=int, default=POSES)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        r = reagreger(json.loads(a.reagreger.read_text()))
        a.reagreger.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        afficher(r)
        return 0
    r = mesurer(poses=int(a.poses))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
    afficher(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
