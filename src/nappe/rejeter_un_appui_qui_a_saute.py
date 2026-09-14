"""Un appui qui a sauté d'interstice : le rejeter, plutôt que d'élargir ou de rétrécir.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `154` mesure qu'il reste un **facteur 2,84** à prendre sur la matière du
rouleau **à taille égale**, donc un défaut d'instrument qui n'est ni la taille ni la dimension de la
mâchoire. Deux voies évidentes se contredisaient — rétrécir, qu'un balayage sous le voxel a réfuté
(`R4-F121`), et élargir la fenêtre, qu'une grille a réfuté (`R4-F114`). Ce fichier les mesure
**ensemble** pour la première fois, puis essaie la seule des quatre pistes de `153` que rien n'avait
fermée : **rejeter les appuis aberrants**.

⭐⭐⭐ ET LE REJET S'ÉNONCE EXACTEMENT, SANS AUCUN SEUIL. Les interstices sont espacés d'**une**
épaisseur, donc « cet appui est à plus d'une **demi**-épaisseur de la médiane de sa mâchoire » et
« cet appui est sur un **autre** interstice » sont le MÊME énoncé. C'est le raisonnement du refus de
la pince, qui bascule exactement à un demi-pas, appliqué aux appuis plutôt qu'aux pas.

⚠⚠ ET LA MÉDIANE PLUTÔT QUE LA MOYENNE. Un appui posé sur l'interstice voisin déplace une moyenne
d'un tiers d'épaisseur sur trois appuis, donc il **emporterait la référence qui doit le juger** —
c'est le motif « toute quantité que la correction enfle elle-même est impropre à décider de cette
correction », payé deux fois dans `149`. La médiane y échappe, et la batterie le montre sur un cas
où les deux règles ne rendent pas le même verdict.

⚠⚠⚠ ET LE RÉSUMÉ N'EST PAS UNE MÉDIANE APPARIÉE. La population est **bimodale** : la grande majorité
des poses n'a aucun appui aberrant et rend un écart exactement nul, une minorité est fortement
améliorée. Une médiane appariée y vaut zéro et ne dirait rien. Ce qui se publie est donc le
**compte** — combien de poses le rejet touche, et ce qu'il leur fait.

Usage :
    uv run python src/nappe/rejeter_un_appui_qui_a_saute.py --verifier
    uv run python src/nappe/rejeter_un_appui_qui_a_saute.py \\
        --json docs/mesures/rejeter_un_appui_qui_a_saute.json
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
                                            _matiere, _nom, _PAS, _VOXEL, poser, un_depart,
                                            une_machoire, une_machoire_en_croix)

POSES = 40
LARGEURS = (0.008, 0.0625, 0.25, 0.5)
MARGES_UM = (0.0, 10.0, 20.0, 43.25, 86.5)
LECHELLE = RACINE / "docs" / "mesures" / "jusquou_une_machoire_peut_elle_etre_juste.json"


def la_fenetre_et_la_largeur_ensemble(matieres=MATIERES, largeurs=LARGEURS, marges=MARGES_UM,
                                      poses: int = POSES) -> dict:
    """Rétrécir la mâchoire et élargir sa fenêtre se compensent-ils ?

    ⭐⭐⭐ LES DEUX N'AVAIENT JAMAIS ÉTÉ BOUGÉS ENSEMBLE. `153` balaye la largeur à fenêtre fixe et
    `R4-F114` la fenêtre à largeur fixe ; l'hypothèse qu'une mâchoire ÉTROITE puisse se permettre
    une fenêtre LARGE — ses appuis étant proches, leurs interstices le sont aussi — demandait la
    grille entière, et elle ne coûte que des poses.

    ⚠ Le nombre de poses réussies est publié à côté de l'erreur : « elle se pose plus souvent » et
    « elle est plus juste » sont deux énoncés, et une fenêtre large peut acheter le premier en
    payant le second.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        departs = [un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um, pas_um)
                   for k in range(int(poses))]
        bloc = {"nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
                "poses": int(poses), "cases": []}
        for lg in largeurs:
            for mg in marges:
                err = []
                for d0, vrai in departs:
                    e = poser(vol, d0, vrai, float(lg) * pas_um, pas_um, voxel_um, True,
                              marge_um=float(mg))
                    if e is not None:
                        err.append(_ecart_deg(e["normale"], vrai))
                bloc["cases"].append({
                    "largeur_en_pas": float(lg), "marge_um": float(mg),
                    "posees": len(err),
                    "erreur_mediane_deg": (round(float(np.median(err)), 3) if err else None)})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "largeurs": [float(x) for x in largeurs], "marges_um": [float(x) for x in marges],
            "par_matiere": out}


def le_recensement_des_aberrants(matieres=MATIERES, poses: int = POSES,
                                 largeur_en_pas: float = LARGEUR_DE_REFERENCE) -> dict:
    """Combien d'appuis sont sur un AUTRE interstice que la médiane de leur mâchoire ?

    ⭐⭐ C'EST LE RECENSEMENT QUI DIT S'IL Y A QUELQUE CHOSE À REJETER. Un rejet écrit sans lui
    serait une règle dont on ignore si elle tire jamais — et `R4-L10` du dépôt dit qu'un chemin qui
    ne se déclenche jamais n'est pas du code mort mais un chiffre qu'on n'a pas regardé.

    ⚠ L'étalement est publié en médiane, p90 et maximum : un p90 supérieur à la demi-épaisseur dit
    qu'une mâchoire sur dix a ses appuis répartis sur deux interstices, ce qu'aucune médiane ne dit.

    ⚠⚠ ET LE PÉRIMÈTRE EST CELUI DU REJET, PAS UN SOUS-ENSEMBLE. Ma première version ne recensait
    que la mâchoire du HAUT, en segment, alors que le rejet s'applique aux DEUX mâchoires et aux
    DEUX formes — d'où « zéro aberrant » à côté de « six poses touchées » sur une même matière, ce
    qui se lit comme une contradiction et n'en est pas une, seulement deux populations. Un
    recensement qui ne recense pas ce que la règle rejette ne peut pas décider si elle a de quoi
    tirer.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        etal, aberrants, total, machoires = [], 0, 0, 0
        for k in range(int(poses)):
            d0, vrai = un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um, pas_um)
            # ⚠⚠ LES QUATRE MACHOIRES QUE LE REJET VOIT : haut et bas, en segment et en croix.
            for sens in (+1.0, -1.0):
                for forme in (une_machoire, une_machoire_en_croix):
                    m = forme(vol, d0, vrai, sens, float(largeur_en_pas) * pas_um, pas_um,
                              voxel_um)
                    if m is None:
                        continue
                    machoires += 1
                    e = np.asarray(m["ecarts_um"], dtype=np.float64)
                    etal.append(float(e.max() - e.min()))
                    aberrants += int(np.sum(np.abs(e - float(np.median(e))) >= 0.5 * pas_um))
                    total += int(e.size)
        a = np.asarray(etal) if etal else None
        out.append({
            "nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
            "machoires": int(machoires), "appuis": int(total), "aberrants": int(aberrants),
            "etalement_median_um": (round(float(np.median(a)), 3) if a is not None else None),
            "etalement_p90_um": (round(float(np.percentile(a, 90)), 3) if a is not None else None),
            "etalement_max_um": (round(float(a.max()), 3) if a is not None else None),
            "il_y_a_quelque_chose_a_rejeter": bool(aberrants > 0)})
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "demi_epaisseur_um": round(0.5 * pas_um, 2),
            "largeur_en_pas": float(largeur_en_pas), "par_matiere": out}


def le_rejet_repare_t_il(matieres=MATIERES, poses: int = POSES,
                         largeur_en_pas: float = LARGEUR_DE_REFERENCE) -> dict:
    """Rejeter les appuis aberrants rend-il la normale plus juste, et sur combien de poses ?

    ⚠⚠⚠ LE RÉSUMÉ EST UN COMPTE, PAS UNE MÉDIANE APPARIÉE. La population est bimodale : la plupart
    des poses n'ont aucun aberrant, donc leur écart apparié vaut exactement zéro, et la médiane d'une
    majorité de zéros est zéro quel que soit l'effet sur la minorité. C'est « une médiane sur un
    mélange n'est pas un résumé » sous une forme neuve, et le remède est de compter.

    ⚠ Les poses TOUCHÉES sont isolées et leur effet publié à part : c'est la seule population sur
    laquelle la règle a quelque chose à dire.
    """
    pas_um, voxel_um = _PAS(), _VOXEL()
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee)
    out = []
    for ecr, amp in matieres:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, 0.0, LONGUEUR_DONDE_UM,
                       RAYON_MM)
        largeur_um = float(largeur_en_pas) * pas_um
        bloc = {"nom": _nom(ecr, amp), "ecrasement": float(ecr), "amplitude_um": float(amp),
                "poses": int(poses), "par_bras": []}
        for nom, croix in (("segment", False), ("croix", True)):
            sans, avec, touchees, mieux, pire = [], [], [], 0, 0
            n_sans, n_avec = 0, 0
            for k in range(int(poses)):
                d0, vrai = un_depart(vol, 2.0 * np.pi * k / int(poses), RAYON_MM, voxel_um,
                                     pas_um)
                a_ = poser(vol, d0, vrai, largeur_um, pas_um, voxel_um, True, en_croix=croix)
                b_ = poser(vol, d0, vrai, largeur_um, pas_um, voxel_um, True, en_croix=croix,
                           rejeter=True)
                if a_ is not None:
                    n_sans += 1
                    sans.append(_ecart_deg(a_["normale"], vrai))
                if b_ is not None:
                    n_avec += 1
                    avec.append(_ecart_deg(b_["normale"], vrai))
                if a_ is None or b_ is None:
                    continue
                ea, eb = _ecart_deg(a_["normale"], vrai), _ecart_deg(b_["normale"], vrai)
                # ⚠⚠⚠ UNE POSE EST TOUCHEE QUAND UN APPUI A ETE REJETE, et ça se lit sur le
                # compte que la pose publie. Ma premiere version comparait les deux normales a
                # 1e-9 — une tolerance SOUS la reproductibilite de la decomposition sur un tableau
                # recopie — et comptait donc du bruit numerique : dix poses « touchees » sur la
                # spirale ecrasee, pour zero mieux et zero pire. Le compte est exact et n'a aucun
                # seuil.
                if int(b_.get("rejetes", 0)) > 0:
                    touchees.append(eb - ea)
                    if eb < ea:
                        mieux += 1
                    elif eb > ea:
                        pire += 1
            bloc["par_bras"].append({
                "bras": nom, "posees_sans_rejet": int(n_sans), "posees_avec_rejet": int(n_avec),
                "erreur_sans_rejet_deg": (round(float(np.median(sans)), 3) if sans else None),
                "erreur_avec_rejet_deg": (round(float(np.median(avec)), 3) if avec else None),
                "poses_touchees": len(touchees), "mieux": int(mieux), "pire": int(pire),
                "effet_median_sur_les_touchees_deg": (round(float(np.median(touchees)), 3)
                                                      if touchees else None)})
        out.append(bloc)
    return {"decidable": bool(out), "poses_par_case": int(poses),
            "largeur_en_pas": float(largeur_en_pas), "par_matiere": out}


def _echelles_de_154(ech: dict | None) -> dict:
    """Les échelles que `154` a mesurées, LUES et jamais recopiées."""
    if not ech or not ech.get("juger", {}).get("decidable"):
        return {}
    return {x["nom"]: max(x["variation_le_long_de_t_deg"],
                          x["variation_le_long_de_n_croix_t_deg"] or 0.0)
            for x in ech["juger"]["par_matiere"]}


def juger(grille: dict, recensement: dict, rejet: dict, ech: dict | None) -> dict:
    """Trois énoncés SÉPARÉS, et le troisième se compare à l'échelle de `154`.

    ⭐⭐⭐⭐ (1) Rétrécir et élargir ne se compensent pas : il n'existe aucune case de la grille où
    élargir la fenêtre paie, à aucune largeur. (2) Il y a bien quelque chose à rejeter, et c'est
    rare. (3) Le rejet répare, sur la minorité qu'il touche — et le rapport à l'échelle de `154`
    dit de combien l'instrument s'est rapproché de sa matière.
    """
    if not (grille.get("decidable") and recensement.get("decidable") and rejet.get("decidable")):
        return {"decidable": False, "raison": "une des trois mesures manque"}
    out = {"decidable": True}
    # (1) la grille : elargir paie-t-il quelque part ?
    par = []
    for m in grille["par_matiere"]:
        lignes = [c for c in m["cases"] if c["erreur_mediane_deg"] is not None]
        if not lignes:
            continue
        meilleure = min(lignes, key=lambda c: c["erreur_mediane_deg"])
        # ⚠ « Elargir paie » se lit A LARGEUR FIXEE : comparer la meilleure case a la pire
        # melangerait les deux axes, et c'est l'axe ou la difference vit.
        paie = []
        for lg in grille["largeurs"]:
            col = [c for c in lignes if abs(c["largeur_en_pas"] - lg) < 1e-12]
            if len(col) < 2:
                continue
            sans = next((c for c in col if c["marge_um"] == 0.0), None)
            if sans is None:
                continue
            paie.append(any(c["erreur_mediane_deg"] < sans["erreur_mediane_deg"]
                            for c in col if c["marge_um"] > 0.0))
        par.append({
            "nom": m["nom"], "amplitude_um": m["amplitude_um"],
            "meilleure_largeur_en_pas": meilleure["largeur_en_pas"],
            "meilleure_marge_um": meilleure["marge_um"],
            "meilleure_erreur_deg": meilleure["erreur_mediane_deg"],
            "largeurs_ou_elargir_paie": int(sum(1 for x in paie if x)),
            "largeurs_testees": len(paie)})
    out["par_matiere_grille"] = par
    out["elargir_ne_paie_a_aucune_largeur"] = bool(
        par and all(x["largeurs_ou_elargir_paie"] == 0 for x in par))
    out["la_meilleure_case_est_sans_marge"] = bool(
        par and all(x["meilleure_marge_um"] == 0.0 for x in par))
    # (2) le recensement
    lisses = [m for m in recensement["par_matiere"] if m["amplitude_um"] == 0.0]
    deux_causes = [m for m in recensement["par_matiere"]
                   if m["ecrasement"] > 0.0 and m["amplitude_um"] > 0.0]
    out["les_aberrants_nexistent_que_sous_les_deux_causes"] = bool(
        lisses and deux_causes
        and all(not m["il_y_a_quelque_chose_a_rejeter"] for m in lisses)
        and all(m["il_y_a_quelque_chose_a_rejeter"] for m in deux_causes))
    # (3) le rejet, et l'echelle de `154`
    echelles = _echelles_de_154(ech)
    lignes = []
    for m in rejet["par_matiere"]:
        for b in m["par_bras"]:
            e = echelles.get(m["nom"])
            lignes.append({
                "nom": m["nom"], "amplitude_um": m["amplitude_um"], "bras": b["bras"],
                "erreur_sans_rejet_deg": b["erreur_sans_rejet_deg"],
                "erreur_avec_rejet_deg": b["erreur_avec_rejet_deg"],
                "poses_touchees": b["poses_touchees"], "mieux": b["mieux"], "pire": b["pire"],
                "effet_median_sur_les_touchees_deg": b["effet_median_sur_les_touchees_deg"],
                "echelle_de_154_deg": (round(e, 3) if e else None),
                "sans_rejet_au_dessus_de_lechelle": (
                    round(b["erreur_sans_rejet_deg"] / e, 2)
                    if e and e > 0.0 and b["erreur_sans_rejet_deg"] is not None else None),
                "avec_rejet_au_dessus_de_lechelle": (
                    round(b["erreur_avec_rejet_deg"] / e, 2)
                    if e and e > 0.0 and b["erreur_avec_rejet_deg"] is not None else None)})
    out["par_bras"] = lignes
    touchees = [x for x in lignes if x["poses_touchees"] > 0]
    out["le_rejet_ne_degrade_jamais_une_pose_touchee"] = bool(
        touchees and all(x["pire"] == 0 for x in touchees))
    dure = next((x for x in lignes if x["amplitude_um"] == 100.0 and x["bras"] == "croix"), None)
    if dure and dure["avec_rejet_au_dessus_de_lechelle"] is not None:
        out["sur_la_matiere_du_rouleau"] = {
            "bras": "croix", "erreur_sans_rejet_deg": dure["erreur_sans_rejet_deg"],
            "erreur_avec_rejet_deg": dure["erreur_avec_rejet_deg"],
            "poses_touchees": dure["poses_touchees"], "mieux": dure["mieux"],
            "pire": dure["pire"],
            "echelle_de_154_deg": dure["echelle_de_154_deg"],
            "sans_rejet_au_dessus_de_lechelle": dure["sans_rejet_au_dessus_de_lechelle"],
            "avec_rejet_au_dessus_de_lechelle": dure["avec_rejet_au_dessus_de_lechelle"],
            # ⭐⭐⭐⭐ L'ENONCE QUI COMPTE, ET IL PEUT ECHOUER : la croix se RAPPROCHE de l'echelle
            # de sa matiere. Si le rejet la laissait ou l'eloignait, il tomberait.
            "elle_se_rapproche_de_son_echelle": bool(
                dure["avec_rejet_au_dessus_de_lechelle"]
                < dure["sans_rejet_au_dessus_de_lechelle"])}
    return out


def mesurer(matieres=MATIERES, largeurs=LARGEURS, marges=MARGES_UM, poses: int = POSES,
            echelle: Path = LECHELLE) -> dict:
    e = json.loads(echelle.read_text()) if echelle.is_file() else None
    g = la_fenetre_et_la_largeur_ensemble(matieres, largeurs, marges, poses)
    r = le_recensement_des_aberrants(matieres, poses)
    j = le_rejet_repare_t_il(matieres, poses)
    return {"grille": g, "recensement": r, "rejet": j, "juger": juger(g, r, j, e),
            "echelle_lue": bool(e)}


def reagreger(r: dict, echelle: Path = LECHELLE) -> dict:
    e = json.loads(echelle.read_text()) if echelle.is_file() else None
    r["juger"] = juger(r["grille"], r["recensement"], r["rejet"], e)
    r["echelle_lue"] = bool(e)
    return r


def afficher(r: dict) -> None:
    g, rc, rj, j = r["grille"], r["recensement"], r["rejet"], r["juger"]
    dure = next((m for m in g["par_matiere"] if m["amplitude_um"] == 100.0), None)
    if dure is not None:
        print("\n⭐⭐⭐ LA LARGEUR ET LA FENÊTRE ENSEMBLE — matière du rouleau, erreur / poses")
        print(f"   {'largeur':>10} " + "".join(f"{m:>13.1f}" for m in g["marges_um"]))
        for lg in g["largeurs"]:
            col = [c for c in dure["cases"] if abs(c["largeur_en_pas"] - lg) < 1e-12]
            s = "".join(("        —    " if c["erreur_mediane_deg"] is None
                         else f"{c['erreur_mediane_deg']:>8.2f}°/{c['posees']:<3d}") for c in col)
            print(f"   {lg:>10.4f} {s}")
    print("\n⭐⭐ LE RECENSEMENT DES APPUIS ABERRANTS")
    print(f"   demi-épaisseur {rc['demi_epaisseur_um']} µm")
    print(f"   {'matière':<32} {'étal. méd':>10} {'p90':>9} {'max':>10} {'aberrants':>12}")
    for m in rc["par_matiere"]:
        print(f"   {m['nom']:<32} {m['etalement_median_um']:>8.2f}µm "
              f"{m['etalement_p90_um']:>7.2f}µm {m['etalement_max_um']:>8.2f}µm "
              f"{m['aberrants']:>6d} / {m['appuis']:<5d}")
    print("\n⭐⭐⭐⭐ LE REJET RÉPARE-T-IL, ET SUR COMBIEN DE POSES ?")
    print(f"   {'matière':<28} {'bras':>8} {'sans':>9} {'avec':>9} {'touchées':>9} "
          f"{'mieux':>6} {'pire':>5} {'/échelle':>16}")
    for x in j["par_bras"]:
        a_ = "—" if x["sans_rejet_au_dessus_de_lechelle"] is None \
            else f"{x['sans_rejet_au_dessus_de_lechelle']:.2f}"
        b_ = "—" if x["avec_rejet_au_dessus_de_lechelle"] is None \
            else f"{x['avec_rejet_au_dessus_de_lechelle']:.2f}"
        print(f"   {x['nom']:<28} {x['bras']:>8} {x['erreur_sans_rejet_deg']:>8.3f}° "
              f"{x['erreur_avec_rejet_deg']:>8.3f}° {x['poses_touchees']:>9} {x['mieux']:>6} "
              f"{x['pire']:>5}   {a_:>5} → {b_:<5}")
    if not j.get("decidable"):
        print(f"\n⚠ {j.get('raison')}")
        return
    print(f"\n   élargir ne paie à AUCUNE largeur : "
          f"{'OUI' if j['elargir_ne_paie_a_aucune_largeur'] else 'non'}"
          f"  ·  la meilleure case est sans marge : "
          f"{'OUI' if j['la_meilleure_case_est_sans_marge'] else 'non'}")
    print(f"   les aberrants n'existent que sous les DEUX causes : "
          f"{'OUI' if j['les_aberrants_nexistent_que_sous_les_deux_causes'] else 'non'}"
          f"  ·  le rejet ne dégrade jamais une pose touchée : "
          f"{'OUI' if j['le_rejet_ne_degrade_jamais_une_pose_touchee'] else 'non'}")
    d = j.get("sur_la_matiere_du_rouleau")
    if d:
        print(f"\n⭐⭐⭐⭐ SUR LA MATIÈRE DU ROULEAU, la croix passe de "
              f"{d['erreur_sans_rejet_deg']}° à {d['erreur_avec_rejet_deg']}°")
        print(f"   soit {d['sans_rejet_au_dessus_de_lechelle']}× → "
              f"{d['avec_rejet_au_dessus_de_lechelle']}× son échelle de "
              f"{d['echelle_de_154_deg']}°  ·  elle s'en rapproche : "
              f"{'OUI' if d['elle_se_rapproche_de_son_echelle'] else 'non'}")
        print(f"   {d['poses_touchees']} poses touchées, {d['mieux']} mieux, {d['pire']} pire")


def verifier() -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        # ⚠ Le compte est DÉRIVÉ, jamais écrit à la main.
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- ⭐⭐ (1) la grille
    # ⚠⚠ LA FIXTURE EST DIMENSIONNEE SUR L'EFFET, PAS L'INVERSE. Ma premiere version tournait sur
    # dix poses et les deux medianes y TOMBAIENT EGALES — non parce que l'effet n'existe pas, mais
    # parce qu'une mediane sur dix valeurs ne separe pas deux degres. C'est « une sonde courte ne
    # borne pas une mesure longue » appliquee a une batterie, et le remede est de la rendre assez
    # longue, jamais de choisir la case qui raconte.
    g = la_fenetre_et_la_largeur_ensemble(matieres=((0.2782, 100.0),),
                                          largeurs=(0.008, 0.5), marges=(0.0, 86.5), poses=24)
    cases = {(c["largeur_en_pas"], c["marge_um"]): c for c in g["par_matiere"][0]["cases"]}
    v("une grille rend une case par couple largeur-marge", len(cases) == 4, f"{len(cases)}")
    v("⭐⭐⭐ élargir la fenêtre FAIT POSER PLUS SOUVENT",
      cases[(0.5, 86.5)]["posees"] >= cases[(0.5, 0.0)]["posees"],
      f"{cases[(0.5, 0.0)]['posees']} → {cases[(0.5, 86.5)]['posees']} poses")
    v("⭐⭐⭐ ... et PLUS FAUX, aux deux largeurs",
      all(cases[(lg, 86.5)]["erreur_mediane_deg"] > cases[(lg, 0.0)]["erreur_mediane_deg"]
          for lg in (0.008, 0.5)),
      " · ".join(f"{lg:g} : {cases[(lg, 0.0)]['erreur_mediane_deg']}° → "
                 f"{cases[(lg, 86.5)]['erreur_mediane_deg']}°" for lg in (0.008, 0.5))
      + " — les deux énoncés sont séparés")

    # ---- ⭐⭐ (2) le recensement
    # ⚠⚠ MEME RAISON, ET ELLE EST PLUS FORTE ICI : un aberrant est RARE — la mesure en compte cinq
    # sur cent cinq appuis — donc douze poses peuvent legitimement n'en porter aucun, et le controle
    # passerait alors pour la mauvaise raison. Le recensement ne coute qu'une machoire par depart.
    rc = le_recensement_des_aberrants(matieres=((0.0, 0.0), (0.2782, 100.0)), poses=40)
    nue, dur = rc["par_matiere"]
    v("⭐⭐ sur une spirale nue il n'y a RIEN à rejeter",
      nue["aberrants"] == 0 and not nue["il_y_a_quelque_chose_a_rejeter"],
      f"{nue['aberrants']} aberrant sur {nue['appuis']} appuis")
    v("⭐⭐⭐ ... et sur la matière du rouleau il y a quelque chose",
      dur["aberrants"] > 0,
      f"{dur['aberrants']} sur {dur['appuis']} · étalement p90 {dur['etalement_p90_um']} µm "
      f"pour une demi-épaisseur de {rc['demi_epaisseur_um']}")
    v("⚠ la demi-épaisseur est celle du pas, jamais un nombre posé",
      abs(rc["demi_epaisseur_um"] - 0.5 * _PAS()) < 0.01, f"{rc['demi_epaisseur_um']} µm")

    # ---- ⭐⭐⭐⭐ (3) le rejet
    rj = le_rejet_repare_t_il(matieres=((0.0, 0.0), (0.2782, 100.0)), poses=12)
    n_seg = rj["par_matiere"][0]["par_bras"][0]
    d_crx = rj["par_matiere"][1]["par_bras"][1]
    v("⭐⭐ sur une spirale nue le rejet ne touche AUCUNE pose",
      n_seg["poses_touchees"] == 0, "il n'y a rien à rejeter, donc rien n'est rejeté")
    v("⭐⭐⭐ ... et sur la matière du rouleau il en touche une minorité",
      0 < d_crx["poses_touchees"] < d_crx["posees_sans_rejet"],
      f"{d_crx['poses_touchees']} sur {d_crx['posees_sans_rejet']} posées")
    v("⚠ mieux plus pire ne dépasse jamais les poses touchées",
      all(b["mieux"] + b["pire"] <= b["poses_touchees"]
          for m in rj["par_matiere"] for b in m["par_bras"]),
      "un effet exactement nul n'est ni l'un ni l'autre")

    # ---- ⚠⚠⚠ LE VERDICT PEUT-IL DIRE NON ? Trois fixtures, une par énoncé.
    ech = json.loads(LECHELLE.read_text()) if LECHELLE.is_file() else None
    j = juger(g, rc, rj, ech)
    v("⭐⭐⭐⭐ le jugement compare le rejet à l'échelle que `154` a mesurée",
      j["decidable"] and any(x["echelle_de_154_deg"] is not None for x in j["par_bras"])
      if ech else j["decidable"],
      "sans elle le rapport serait indécidable et le dirait")
    faux_g = json.loads(json.dumps(g))
    for c in faux_g["par_matiere"][0]["cases"]:
        if c["marge_um"] > 0.0:
            c["erreur_mediane_deg"] = 0.001
    jf = juger(faux_g, rc, rj, ech)
    v("⭐⭐⭐ le verdict DIT NON quand élargir paie quelque part",
      jf["elargir_ne_paie_a_aucune_largeur"] is False
      and jf["la_meilleure_case_est_sans_marge"] is False,
      "sinon l'énoncé serait vrai quelle que soit la mesure")
    faux_rc = json.loads(json.dumps(rc))
    faux_rc["par_matiere"][0]["aberrants"] = 3
    faux_rc["par_matiere"][0]["il_y_a_quelque_chose_a_rejeter"] = True
    v("⭐⭐⭐ ... et NON quand une matière lisse porte des aberrants",
      juger(g, faux_rc, rj, ech)["les_aberrants_nexistent_que_sous_les_deux_causes"] is False)
    faux_rj = json.loads(json.dumps(rj))
    for m in faux_rj["par_matiere"]:
        for b in m["par_bras"]:
            if b["poses_touchees"] > 0:
                b["pire"] = 1
    v("⭐⭐⭐ ... et NON quand le rejet dégrade une pose touchée",
      juger(g, rc, faux_rj, ech)["le_rejet_ne_degrade_jamais_une_pose_touchee"] is False)
    v("⚠ une mesure manquante rend le jugement indécidable, jamais à moitié vrai",
      juger({"decidable": False}, rc, rj, ech)["decidable"] is False)

    # ---- ⚠⚠ LE CHEMIN QUI PUBLIE EST EXERCÉ, matière injectée et jamais le découpage.
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as dossier:
        absent = Path(dossier) / "pas_dechelle.json"
        r = mesurer(matieres=((0.0, 0.0),), largeurs=(0.25,), marges=(0.0,), poses=6,
                    echelle=absent)
        v("⭐⭐ `mesurer` rend les trois mesures et dit qu'il n'a pas lu `154`",
          all(r[k]["decidable"] for k in ("grille", "recensement", "rejet"))
          and r["echelle_lue"] is False,
          "un fichier absent se DIT, il ne se devine pas")
        v("⚠ ... et sans `154` le rapport à l'échelle n'est pas calculé",
          all(x["avec_rejet_au_dessus_de_lechelle"] is None for x in r["juger"]["par_bras"]))
        avant = json.loads(json.dumps(r["rejet"]))
        r2 = reagreger(json.loads(json.dumps(r)), echelle=absent)
        v("⭐⭐⭐ `reagreger` ne touche PAS un seul nombre mesuré", r2["rejet"] == avant,
          "il relit le verdict, il ne remesure rien")
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(r2)
        v("⚠ `afficher` rend le recensement et le rejet",
          "RECENSEMENT DES APPUIS" in tampon.getvalue()
          and "LE REJET RÉPARE" in tampon.getvalue(),
          f"{len(tampon.getvalue())} caractères")

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
