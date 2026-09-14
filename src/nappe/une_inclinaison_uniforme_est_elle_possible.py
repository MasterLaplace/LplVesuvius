#!/usr/bin/env python3
"""Une inclinaison uniforme est-elle possible sur un rouleau, et un froissement suffit-il ?

⭐⭐⭐⭐ POURQUOI CE FICHIER EXISTE, ET POURQUOI IL COMMENCE PAR REFUSER CE QU'ON LUI DEMANDE.
`R4-P28` reclame « une spirale dont la normale soit a un angle FIXE du rayon » pour expliquer le
**1,186** que `136` mesure entre le chemin d'une traversee et son etendue radiale. Cette matiere
n'existe pas, et c'est de la geometrie et non une limite d'imagination : un rouleau croise UNE
feuille par tour, or une inclinaison uniforme `alpha` en fait croiser `2.pi.rho.sin(alpha)/s`. A
trente-quatre degres et dix millimetres, deux cent quatorze. L'inclinaison uniforme qu'un
enroulement autorise vaut quelques DIXIEMES de degre — exactement celle de la spirale d'Archimede
(`R4-F16` : 0,09°).

⭐⭐⭐⭐ DONC LES TRENTE-QUATRE DEGRES MESURES LOCALEMENT SONT UN VAGABONDAGE, et la question devient
mesurable : un vagabondage de cette amplitude suffit-il a faire payer 1,186 a un marcheur ? La
fixture qui repond est une spirale FROISSEE, dont la normale est analytique, donc dont le cout est
PREDICTIBLE — `1/<cos(theta)>` sur les normales rencontrees. Une fixture dont la reponse se calcule
est une fixture ou la mesure peut echouer.

⚠⚠ ET CE QUI SERAIT TAUTOLOGIQUE, DONC CE QUI N'EST PAS UN VERDICT ICI. Le rapport chemin sur
etendue et la moyenne de `1/cos` sur les pas sont presque la meme quantite ecrite deux fois — c'est
l'avertissement de `137`. Ce qui se mesure ici n'est pas leur accord mais l'AMPLITUDE qu'il faut
donner au froissement pour atteindre un rapport donne, et ce que cette amplitude fait a la matiere.

⭐⭐⭐ LE CONTROLE QUI TRANCHE EST QUE LA MATIERE CESSE D'ETRE UNE PILE. Au-dela d'une amplitude de
l'ordre de l'espacement, la phase RECULE le long du rayon : deux feuilles voisines se croisent, et
un empilement dont les feuilles se traversent n'est plus un empilement. Si l'amplitude qu'il faut
pour reproduire le rouleau est de ce cote-la, le froissement est refute comme explication.

Usage :
    uv run python src/nappe/une_inclinaison_uniforme_est_elle_possible.py --verifier
    uv run python src/nappe/une_inclinaison_uniforme_est_elle_possible.py \\
        --json docs/mesures/une_inclinaison_uniforme_est_elle_possible.json
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

# ⚠ Les rayons sont ceux de la campagne (`107`), pas des ronds choisis : l'inclinaison qu'un
# enroulement autorise depend du rayon, donc elle se publie la ou les marches ont eu lieu.
RAYONS_MM = (4.07, 10.51, 18.62)
# ⚠ L'espacement voyage en PAIRE, comme `136` l'impose : 164 µm par les transferts humains, 182,4
# par l'atlas (`R4-F14`). Un verdict qui ne tiendrait que pour l'un des deux n'est pas un verdict.
ESPACEMENTS_UM = (164.0, 182.4)
INCLINAISON_MESUREE_DEG = 34.06
LONGUEUR_DONDE_UM = 393.6
AMPLITUDES_UM = (0.0, 42.4, 100.0, 200.0, 400.0)
RAYON_DE_LA_FIXTURE_MM = 10.0
CENTRE_YX_VX = (6000.0, 6000.0)
FORME = (4000, 16000, 16000)
PAS_MAX = 40
DEPARTS = 8


def feuilles_par_tour(rayon_um: float, espacement_um: float, inclinaison_deg: float) -> float:
    """Combien de feuilles une inclinaison UNIFORME fait croiser en un tour a ce rayon.

    ⭐⭐ En tournant une fois a rayon `rho` on parcourt `2.pi.rho` tangentiellement ; si la normale
    fait `alpha` avec le rayon, la composante NORMALE de ce deplacement vaut `2.pi.rho.sin(alpha)`,
    donc on croise ce nombre divise par l'espacement. C'est toute la demonstration.
    """
    return float(2.0 * np.pi * float(rayon_um) * np.sin(np.radians(float(inclinaison_deg)))
                 / float(espacement_um))


def linclinaison_quun_enroulement_autorise(rayon_um: float, espacement_um: float,
                                           feuilles_par_tour_: float = 1.0) -> float:
    """L'inclinaison uniforme compatible avec un enroulement qui croise N feuilles par tour.

    ⚠ Un rouleau en croise UNE par definition — c'est ce que veut dire « enroule ». Le parametre
    existe pour que la batterie puisse demander autre chose et voir la reponse bouger.
    """
    v = float(feuilles_par_tour_) * float(espacement_um) / (2.0 * np.pi * float(rayon_um))
    if not -1.0 <= v <= 1.0:
        return float("nan")
    return float(np.degrees(np.arcsin(v)))


def linclinaison_uniforme_est_elle_possible(rayons_mm=RAYONS_MM, espacements=ESPACEMENTS_UM,
                                            inclinaison_deg: float = INCLINAISON_MESUREE_DEG
                                            ) -> dict:
    """Ce qu'une inclinaison uniforme couterait, et ce qu'un enroulement autorise.

    ⚠⚠ LE VERDICT PORTE SUR LA FOURCHETTE ENTIERE DES DEUX INSTRUMENTS. Un ecart qui ne tiendrait
    qu'a 164 µm et pas a 182,4 ne serait pas un ecart, c'est le piege que `136` a paye.
    """
    lignes = []
    for r_mm in rayons_mm:
        for esp in espacements:
            r_um = float(r_mm) * 1000.0
            lignes.append({
                "rayon_mm": float(r_mm), "espacement_um": float(esp),
                "feuilles_par_tour_a_linclinaison_mesuree": round(
                    feuilles_par_tour(r_um, esp, inclinaison_deg), 2),
                "inclinaison_autorisee_deg": round(
                    linclinaison_quun_enroulement_autorise(r_um, esp), 4)})
    autorisees = [x["inclinaison_autorisee_deg"] for x in lignes]
    croisees = [x["feuilles_par_tour_a_linclinaison_mesuree"] for x in lignes]
    return {"decidable": True, "inclinaison_mesuree_deg": float(inclinaison_deg),
            "lignes": lignes,
            "inclinaison_autorisee_min_deg": round(float(min(autorisees)), 4),
            "inclinaison_autorisee_max_deg": round(float(max(autorisees)), 4),
            "feuilles_par_tour_min": round(float(min(croisees)), 2),
            "feuilles_par_tour_max": round(float(max(croisees)), 2),
            "combien_de_fois_trop_grande": round(
                float(inclinaison_deg / max(max(autorisees), 1e-12)), 1),
            # ⭐⭐ Le verdict, calcule : l'inclinaison mesuree localement depasse-t-elle ce qu'un
            # enroulement autorise, a TOUS les rayons et pour LES DEUX espacements ?
            "une_inclinaison_uniforme_est_impossible": bool(inclinaison_deg > max(autorisees))}


def le_cout_dun_vagabondage(angles_deg) -> dict:
    """Ce qu'une normale qui vagabonde coute en chemin, pour une etendue radiale donnee.

    ⚠ Un marcheur qui suit la normale parcourt `N.s` pour croiser `N` feuilles et gagne
    `N.s.<cos(theta)>` en rayon : le rapport chemin sur etendue vaut donc `1/<cos>`. ⚠⚠ `<1/cos>`
    est une AUTRE quantite, plus grande, et la difference n'est pas un detail — elle explose quand
    un angle approche le droit. Les deux sont publiees.
    """
    a = np.asarray(angles_deg, dtype=float)
    if a.size == 0:
        return {"decidable": False, "pourquoi": "aucun angle"}
    c = np.cos(np.radians(a))
    return {"decidable": True, "angles": int(a.size),
            "angle_median_deg": round(float(np.median(np.abs(a))), 2),
            "un_sur_cos_moyen": round(float(1.0 / np.mean(c)), 4),
            "moyenne_de_un_sur_cos": round(float(np.mean(1.0 / np.maximum(c, 1e-3))), 4),
            "un_sur_cos_de_la_mediane": round(
                float(1.0 / np.cos(np.radians(np.median(np.abs(a))))), 4)}


def _barres():
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    return (longueurs, mu, sd, barre, nul_du_tenseur(demi=20)["accord_des_moities_p1_deg"],
            max(x["p99"] for x in C.accord_du_bruit_pur().values()), C)


def la_phase_recule_t_elle(volume, rayons_um=(8000.0, 14000.0), directions: int = 16,
                           echantillons: int = 3000) -> dict:
    """La matiere est-elle encore une PILE, ou ses feuilles se croisent-elles ?

    ⭐⭐⭐⭐ C'EST LE CONTROLE QUI TRANCHE, et il ne demande aucune marche. Le long d'un rayon, la
    phase d'un empilement doit CROITRE : chaque pas vers l'exterieur franchit de la feuille. Si elle
    RECULE quelque part, deux feuilles voisines se sont croisees a cet endroit, et un empilement
    dont les feuilles se traversent n'est plus un empilement. Une amplitude qui reproduirait le
    rouleau de ce cote-la ne serait donc pas une explication, ce serait une autre matiere.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    cy, cx = volume.centre_yx_vx
    parts = []
    for th in np.linspace(0.0, 2.0 * np.pi, int(directions), endpoint=False):
        r = np.linspace(rayons_um[0], rayons_um[1], int(echantillons)) / C.VOXEL_FIN_UM
        p = np.stack([np.full_like(r, 2000.0), cy + r * np.sin(th), cx + r * np.cos(th)], axis=1)
        d = np.diff(volume.phase(p))
        parts.append(float((d <= 0.0).mean()))
    parts = np.asarray(parts)
    return {"part_du_rayon_ou_la_phase_recule": round(float(np.median(parts)), 4),
            "et_au_plus": round(float(parts.max()), 4),
            "les_feuilles_se_croisent": bool(parts.max() > 0.0)}


def sur_la_spirale_froissee(amplitudes=AMPLITUDES_UM, rayon_mm: float = RAYON_DE_LA_FIXTURE_MM,
                            longueur_donde_um: float = LONGUEUR_DONDE_UM,
                            departs: int = DEPARTS, pas_max: int = PAS_MAX,
                            graine: int = 3) -> dict:
    """Ce qu'un marcheur paie sur une spirale dont le froissement a une amplitude CONNUE.

    ⭐⭐⭐ DEUX NOMBRES PAR AMPLITUDE, ET C'EST LEUR ECART QUI EST LA MESURE. Le PREDIT est
    `1/<cos>` sur les normales que la marche a rencontrees — ce qu'un marcheur qui suivrait la
    normale exactement paierait. Le MESURE est son chemin divise par son etendue radiale. Un
    marcheur a cap ne suit pas la normale : il la moyenne, donc il paie moins, et de combien est
    une propriete du cap qu'aucune tranche n'avait chiffree.

    ⚠ Le depart est recale sur une phase ENTIERE le long du rayon : une cellule qui tombe entre
    deux feuilles ne correspond a aucune polarite du gabarit, et la mesure porterait alors sur sa
    propre erreur de mise en place — le defaut que la fixture de `100` a paye.
    """
    from combien_de_pas_la_matiere_porte import (VolumeFabriqueEnSpiraleFroissee,  # noqa: PLC0415
                                                 marcher)

    barres = _barres()
    longueurs, mu, sd, barre, barre_moities, barre_interstice, C = barres
    z = np.array([1.0, 0.0, 0.0])
    cy, cx = CENTRE_YX_VX
    r_vx = float(rayon_mm) * 1000.0 / C.VOXEL_FIN_UM
    lots = []
    for amp in amplitudes:
        vol = VolumeFabriqueEnSpiraleFroissee(
            C.PAS_UM, amplitude_um=float(amp), longueur_donde_um=float(longueur_donde_um),
            r0_um=float(rayon_mm) * 1000.0, centre_yx_vx=CENTRE_YX_VX, forme=FORME, graine=graine)
        marches = []
        for k in range(int(departs)):
            th = 2.0 * np.pi * k / int(departs)
            radial = np.array([0.0, np.sin(th), np.cos(th)])
            p0 = np.array([2000.0, cy + r_vx * np.sin(th), cx + r_vx * np.cos(th)])
            ph = float(vol.phase(p0.reshape(1, 3))[0])
            depart = p0 + radial * ((round(ph) - ph) * vol.pas_um / C.VOXEL_FIN_UM)
            n0 = vol.normale_locale(depart).reshape(3)
            etapes = marcher(vol, depart, n0, longueurs, mu, sd, barre, barre_moities,
                             barre_interstice, C.VOXEL_FIN_UM, pas_max=pas_max, demi=20, fils=1,
                             memoire_du_cap=0.75)
            pas = [e for e in etapes if "avance_um" in e]
            if len(pas) < pas_max // 2:
                continue
            axe = np.array([depart[0], cy, cx])

            def rho(q, axe=axe):
                u = q - axe
                u = u - (u @ z) * z
                return float(np.linalg.norm(u))

            p, chemin, angles = depart.copy(), 0.0, []
            r0 = rho(p)
            for e in pas:
                d = np.asarray(e["direction"], dtype=float)
                d = d / max(float(np.linalg.norm(d)), 1e-12)
                u = p - axe
                u = u - (u @ z) * z
                rh = u / max(float(np.linalg.norm(u)), 1e-12)
                n = vol.normale_locale(p).reshape(3)
                angles.append(float(np.degrees(np.arccos(np.clip(abs(float(n @ rh)), -1.0, 1.0)))))
                chemin += float(e["avance_um"])
                p = p + d * (float(e["avance_um"]) / C.VOXEL_FIN_UM)
            etendue = (rho(p) - r0) * C.VOXEL_FIN_UM
            if etendue <= 0.0:
                continue
            cout = le_cout_dun_vagabondage(angles)
            marches.append({"depart_deg": round(float(np.degrees(th)), 1), "pas": len(pas),
                            "chemin_um": round(chemin, 1), "etendue_radiale_um": round(etendue, 1),
                            "rapport_mesure": round(chemin / etendue, 4),
                            "rapport_predit": cout["un_sur_cos_moyen"],
                            "inclinaison_mediane_deg": cout["angle_median_deg"]})
        lignes = {"amplitude_um": float(amp),
                  "amplitude_sur_espacement": round(float(amp) / C.PAS_UM, 2),
                  "inclinaison_max_deg": round(vol.inclinaison_max_deg(), 2),
                  "marches": marches, **la_phase_recule_t_elle(vol)}
        if marches:
            lignes.update({
                "rapport_mesure_median": round(float(np.median(
                    [m["rapport_mesure"] for m in marches])), 4),
                "rapport_predit_median": round(float(np.median(
                    [m["rapport_predit"] for m in marches])), 4),
                "inclinaison_mediane_deg": round(float(np.median(
                    [m["inclinaison_mediane_deg"] for m in marches])), 2)})
        lots.append(lignes)
    return {"rayon_mm": float(rayon_mm), "longueur_donde_um": float(longueur_donde_um),
            "espacement_de_la_fixture_um": float(C.PAS_UM), "pas_max": int(pas_max),
            "departs": int(departs), "lots": lots}


def juger(uniforme: dict, fixture: dict, rapport_du_rouleau: float = 1.186) -> dict:
    """Ce que les deux moities disent ensemble du 1,186 du rouleau.

    ⭐⭐⭐⭐ DEUX EXPLICATIONS SONT MISES A L'EPREUVE ET TOMBENT. L'inclinaison UNIFORME est refusee
    par l'enroulement lui-meme ; le FROISSEMENT est refuse par la mesure, parce que l'amplitude
    qu'il faudrait replie les feuilles les unes sur les autres.

    ⚠ Le rapport du rouleau est celui que `136` publie, passe en parametre et jamais code en dur :
    un nombre d'une autre tranche doit pouvoir etre change sans toucher au verdict.
    """
    lots = [x for x in fixture.get("lots", []) if "rapport_mesure_median" in x]
    if not lots or not uniforme.get("decidable"):
        return {"decidable": False, "pourquoi": "une des deux moities n'a rien rendu"}
    out = {"decidable": True, "rapport_du_rouleau": float(rapport_du_rouleau),
           "une_inclinaison_uniforme_est_impossible":
               uniforme["une_inclinaison_uniforme_est_impossible"],
           "inclinaison_autorisee_max_deg": uniforme["inclinaison_autorisee_max_deg"],
           "feuilles_par_tour_a_linclinaison_mesuree": uniforme["feuilles_par_tour_max"]}
    # ⭐⭐ Le lot dont l'inclinaison maximale reproduit celle que le maillage mesure.
    vise = min(lots, key=lambda x: abs(x["inclinaison_max_deg"] - INCLINAISON_MESUREE_DEG))
    out.update({"amplitude_a_linclinaison_mesuree_um": vise["amplitude_um"],
                "inclinaison_max_de_ce_lot_deg": vise["inclinaison_max_deg"],
                "rapport_a_linclinaison_mesuree": vise["rapport_mesure_median"],
                "rapport_predit_a_linclinaison_mesuree": vise["rapport_predit_median"]})
    # ⭐⭐⭐⭐ Le premier lot qui atteint le rapport du rouleau, et ce que sa matiere est devenue.
    atteint = [x for x in lots if x["rapport_mesure_median"] >= rapport_du_rouleau]
    if atteint:
        premier = min(atteint, key=lambda x: x["amplitude_um"])
        out.update({"amplitude_qui_atteint_le_rouleau_um": premier["amplitude_um"],
                    "amplitude_sur_espacement": premier["amplitude_sur_espacement"],
                    "part_du_rayon_ou_la_phase_recule": premier["part_du_rayon_ou_la_phase_recule"],
                    "a_cette_amplitude_les_feuilles_se_croisent": premier["les_feuilles_se_croisent"]})
    else:
        # ⚠ Aucune amplitude essayee n'y arrive : le dire, jamais extrapoler.
        plus_haut = max(lots, key=lambda x: x["rapport_mesure_median"])
        out.update({"aucune_amplitude_essayee_natteint_le_rouleau": True,
                    "rapport_le_plus_haut_atteint": plus_haut["rapport_mesure_median"],
                    "a_lamplitude_um": plus_haut["amplitude_um"]})
    # ⭐⭐ Le verdict : le froissement explique-t-il le rouleau SANS cesser d'etre une pile ?
    sains = [x for x in lots if not x["les_feuilles_se_croisent"]]
    meilleur_sain = max(sains, key=lambda x: x["rapport_mesure_median"]) if sains else None
    if meilleur_sain is not None:
        out["rapport_le_plus_haut_sans_croiser"] = meilleur_sain["rapport_mesure_median"]
        out["a_lamplitude_sans_croiser_um"] = meilleur_sain["amplitude_um"]
        out["le_froissement_explique_le_rouleau"] = bool(
            meilleur_sain["rapport_mesure_median"] >= rapport_du_rouleau)
    # ⭐ Et de combien le cap recupere l'obliquite du champ de normales.
    ecarts = [(x["rapport_predit_median"] - x["rapport_mesure_median"])
              / max(x["rapport_predit_median"] - 1.0, 1e-9)
              for x in lots if x["rapport_predit_median"] > 1.001]
    if ecarts:
        out["part_de_lobliquite_que_le_cap_recupere"] = round(float(np.median(ecarts)), 3)
    return out


def mesurer(amplitudes=AMPLITUDES_UM, departs: int = DEPARTS, pas_max: int = PAS_MAX) -> dict:
    uniforme = linclinaison_uniforme_est_elle_possible()
    fixture = sur_la_spirale_froissee(amplitudes=amplitudes, departs=departs, pas_max=pas_max)
    return {"inclinaison_mesuree_deg": INCLINAISON_MESUREE_DEG,
            "espacements_um": list(ESPACEMENTS_UM), "rayons_mm": list(RAYONS_MM),
            "linclinaison_uniforme_est_elle_possible": uniforme,
            "sur_la_spirale_froissee": fixture, "juger": juger(uniforme, fixture)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    u = r["linclinaison_uniforme_est_elle_possible"]
    print(f"une inclinaison UNIFORME de {u['inclinaison_mesuree_deg']}° ferait croiser "
          f"{u['feuilles_par_tour_min']} à {u['feuilles_par_tour_max']} feuilles par tour ; "
          f"un rouleau en croise UNE")
    for x in u["lignes"]:
        print(f"   r {x['rayon_mm']:>5.2f} mm · espacement {x['espacement_um']:>5.1f} µm → "
              f"{x['feuilles_par_tour_a_linclinaison_mesuree']:>8.2f} feuilles par tour · "
              f"inclinaison autorisée {x['inclinaison_autorisee_deg']:.4f}°")
    print(f"   ★ une inclinaison uniforme est impossible : "
          f"{u['une_inclinaison_uniforme_est_impossible']} — l'autorisée va de "
          f"{u['inclinaison_autorisee_min_deg']} à {u['inclinaison_autorisee_max_deg']}°, soit "
          f"{u['combien_de_fois_trop_grande']} fois moins que la mesurée")

    f = r["sur_la_spirale_froissee"]
    print(f"\nla spirale FROISSÉE (rayon {f['rayon_mm']} mm, λ {f['longueur_donde_um']} µm, "
          f"espacement {f['espacement_de_la_fixture_um']} µm, {f['pas_max']} pas) :")
    print(f"   {'amplitude':>9} {'A/espac':>8} {'incl max':>9} {'incl méd':>9} "
          f"{'MESURÉ':>8} {'PRÉDIT':>8} {'phase recule':>13}")
    for x in f["lots"]:
        mes = x.get("rapport_mesure_median")
        pre = x.get("rapport_predit_median")
        imd = x.get("inclinaison_mediane_deg")
        print(f"   {x['amplitude_um']:>9.1f} {x['amplitude_sur_espacement']:>8.2f} "
              f"{x['inclinaison_max_deg']:>9.2f} "
              f"{(f'{imd:.2f}' if imd is not None else '—'):>9} "
              f"{(f'{mes:.4f}' if mes is not None else '—'):>8} "
              f"{(f'{pre:.4f}' if pre is not None else '—'):>8} "
              f"{x['part_du_rayon_ou_la_phase_recule']:>12.1%}"
              + ("  ✗ les feuilles se croisent" if x["les_feuilles_se_croisent"] else ""))

    j = r.get("juger", {})
    if j.get("decidable"):
        print(f"\n★★★ à l'inclinaison mesurée ({j['inclinaison_max_de_ce_lot_deg']}°, amplitude "
              f"{j['amplitude_a_linclinaison_mesuree_um']} µm) le marcheur paie "
              f"{j['rapport_a_linclinaison_mesuree']} — le rouleau lui coûte "
              f"{j['rapport_du_rouleau']}")
        if j.get("amplitude_qui_atteint_le_rouleau_um") is not None:
            print(f"★★★★ il faut {j['amplitude_qui_atteint_le_rouleau_um']} µm d'amplitude "
                  f"({j['amplitude_sur_espacement']} fois l'espacement) pour l'atteindre, et là la "
                  f"phase recule sur {j['part_du_rayon_ou_la_phase_recule']:.1%} du rayon : les "
                  f"feuilles se croisent")
        else:
            print(f"★★★★ aucune amplitude essayée n'atteint le rouleau : au plus "
                  f"{j['rapport_le_plus_haut_atteint']} à {j['a_lamplitude_um']} µm")
        if "le_froissement_explique_le_rouleau" in j:
            print(f"★★★★ le froissement explique le rouleau SANS que les feuilles se croisent : "
                  f"{j['le_froissement_explique_le_rouleau']} — au plus "
                  f"{j['rapport_le_plus_haut_sans_croiser']} à "
                  f"{j['a_lamplitude_sans_croiser_um']} µm")
        if j.get("part_de_lobliquite_que_le_cap_recupere") is not None:
            print(f"★★ le cap récupère {j['part_de_lobliquite_que_le_cap_recupere']:.1%} de "
                  f"l'obliquité que le champ de normales imposerait")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- le compte de feuilles par tour, et son inverse
    v("une inclinaison nulle ne fait croiser aucune feuille par tour",
      abs(feuilles_par_tour(10000.0, 164.0, 0.0)) < 1e-12)
    a = linclinaison_quun_enroulement_autorise(10000.0, 164.0)
    v("l'inclinaison autorisée fait croiser EXACTEMENT une feuille par tour",
      abs(feuilles_par_tour(10000.0, 164.0, a) - 1.0) < 1e-9, f"{a:.4f}° → "
      f"{feuilles_par_tour(10000.0, 164.0, a):.9f} feuille")
    v("... et elle décroît avec le rayon, comme l'enroulement l'impose",
      linclinaison_quun_enroulement_autorise(4000.0, 164.0)
      > linclinaison_quun_enroulement_autorise(22000.0, 164.0),
      f"{linclinaison_quun_enroulement_autorise(4000.0, 164.0):.4f}° à 4 mm contre "
      f"{linclinaison_quun_enroulement_autorise(22000.0, 164.0):.4f}° à 22")
    v("doubler le rayon double le compte à inclinaison égale",
      abs(feuilles_par_tour(20000.0, 164.0, 10.0)
          - 2.0 * feuilles_par_tour(10000.0, 164.0, 10.0)) < 1e-9)
    # ⚠ Une demande impossible — plus de feuilles par tour que la circonference n'en contient —
    # rend « pas de nombre », jamais un angle plausible.
    v("⚠ une demande impossible rend un refus, jamais un angle",
      not np.isfinite(linclinaison_quun_enroulement_autorise(10000.0, 164.0, 1e6)))

    u = linclinaison_uniforme_est_elle_possible()
    v("l'inclinaison mesurée dépasse ce qu'un enroulement autorise, à tous les rayons",
      u["une_inclinaison_uniforme_est_impossible"]
      and len(u["lignes"]) == len(RAYONS_MM) * len(ESPACEMENTS_UM),
      f"{u['inclinaison_autorisee_min_deg']} à {u['inclinaison_autorisee_max_deg']}° autorisés "
      f"contre {u['inclinaison_mesuree_deg']} mesurés")
    # ⚠⚠ LA SONDE : une inclinaison DANS la fourchette autorisée doit rendre le verdict FAUX.
    # Sans elle, « c'est impossible » serait une affirmation que rien ne peut contredire.
    u2 = linclinaison_uniforme_est_elle_possible(inclinaison_deg=0.05)
    v("⚠⚠ sonde : une inclinaison assez petite est déclarée POSSIBLE",
      not u2["une_inclinaison_uniforme_est_impossible"],
      f"0,05° contre {u2['inclinaison_autorisee_max_deg']}° autorisés")

    # ---- le coût d'un vagabondage
    v("un vagabondage nul ne coûte rien", le_cout_dun_vagabondage([0.0] * 10)["un_sur_cos_moyen"]
      == 1.0)
    c = le_cout_dun_vagabondage([30.0] * 10)
    v("un angle constant coûte exactement 1/cos", abs(c["un_sur_cos_moyen"]
      - 1.0 / np.cos(np.radians(30.0))) < 1e-4, f"{c['un_sur_cos_moyen']}")
    # ⚠⚠ DEUX MOYENNES QUI NE SONT PAS LA MEME, et c'est pour ca que les deux sont publiees.
    # L'inegalite de Jensen donne `<1/cos> >= 1/<cos>`, avec EGALITE si et seulement si tous les
    # angles sont egaux. La borne est donc l'inegalite elle-meme, jamais un facteur choisi — ma
    # premiere version exigeait « au moins 1,2 fois » et a echoue a 1,098, ce qui n'aurait rien
    # dit de faux sur la matiere et tout sur le seuil.
    etale = le_cout_dun_vagabondage(list(np.linspace(-70.0, 70.0, 101)))
    v("⚠⚠ ... et Jensen : sur une distribution étalée, <1/cos> dépasse strictement 1/<cos>",
      etale["moyenne_de_un_sur_cos"] > etale["un_sur_cos_moyen"],
      f"1/<cos> {etale['un_sur_cos_moyen']} contre <1/cos> {etale['moyenne_de_un_sur_cos']}")
    egal = le_cout_dun_vagabondage([25.0] * 40)
    v("⚠⚠ ... et elles sont ÉGALES quand tous les angles le sont",
      abs(egal["moyenne_de_un_sur_cos"] - egal["un_sur_cos_moyen"]) < 1e-9,
      f"{egal['un_sur_cos_moyen']}")
    serre = le_cout_dun_vagabondage([30.0, 30.0, 30.0, 30.0])
    v("⚠ ... deux distributions de même MÉDIANE coûtent différemment",
      abs(serre["un_sur_cos_de_la_mediane"]
          - le_cout_dun_vagabondage([0.0, 0.0, 30.0, 70.0, 70.0])["un_sur_cos_de_la_mediane"]) < 1e-9
      and abs(serre["un_sur_cos_moyen"]
              - le_cout_dun_vagabondage([0.0, 0.0, 30.0, 70.0, 70.0])["un_sur_cos_moyen"]) > 0.05)
    v("aucun angle est indécidable", not le_cout_dun_vagabondage([])["decidable"])

    # ---- la matière est-elle encore une pile ?
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpiraleFroissee  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    kw = {"r0_um": 10000.0, "centre_yx_vx": CENTRE_YX_VX, "forme": FORME}
    plate = VolumeFabriqueEnSpiraleFroissee(C.PAS_UM, amplitude_um=0.0, **kw)
    v("sur une spirale lisse la phase ne recule jamais le long du rayon",
      not la_phase_recule_t_elle(plate)["les_feuilles_se_croisent"])
    # ⚠⚠ LA SONDE : une amplitude bien au-dela de l'espacement DOIT faire reculer la phase. Sans
    # elle, « la phase ne recule pas » serait satisfait par un controle qui ne regarde rien.
    repliee = VolumeFabriqueEnSpiraleFroissee(C.PAS_UM, amplitude_um=400.0,
                                              longueur_donde_um=LONGUEUR_DONDE_UM, **kw)
    rp = la_phase_recule_t_elle(repliee)
    v("⚠⚠ sonde : au-delà de l'espacement, la phase RECULE et les feuilles se croisent",
      rp["les_feuilles_se_croisent"] and rp["part_du_rayon_ou_la_phase_recule"] > 0.05,
      f"{rp['part_du_rayon_ou_la_phase_recule']:.1%} du rayon, au plus {rp['et_au_plus']:.1%}")

    # ---- la fixture elle-même, et ce qui la rend digne de foi
    froissee = VolumeFabriqueEnSpiraleFroissee(C.PAS_UM, amplitude_um=42.4,
                                               longueur_donde_um=LONGUEUR_DONDE_UM, **kw)
    # ⚠ LE CONTRAT DE LA FIXTURE — qu'a amplitude nulle elle SOIT la spirale d'Archimede au bit,
    # et que sa normale analytique SOIT le gradient de sa phase aux differences pres — est verifie
    # par la batterie du module qui la PORTE (`combien_de_pas_la_matiere_porte`). Le refaire ici
    # serait deux endroits ou la meme propriete peut se contredire.
    v("... et son inclinaison maximale est celle qu'elle annonce",
      abs(froissee.inclinaison_max_deg()
          - np.degrees(np.arctan(2.0 * np.pi * 42.4 / LONGUEUR_DONDE_UM))) < 1e-9,
      f"{froissee.inclinaison_max_deg():.2f}°")

    # ⚠ Le chemin qui produit le nombre publié est ATTEINT, sur deux amplitudes et peu de pas.
    court = sur_la_spirale_froissee(amplitudes=(0.0, 200.0), departs=3, pas_max=10)
    lots = court["lots"]
    v("l'assemblage marche sur la fixture et rend un rapport par amplitude",
      all("rapport_mesure_median" in x for x in lots),
      " · ".join(f"{x['amplitude_um']:.0f} µm → {x.get('rapport_mesure_median')}" for x in lots))
    v("⚠ ... et à amplitude nulle le rapport vaut UN : une spirale lisse ne coûte rien",
      abs(lots[0]["rapport_mesure_median"] - 1.0) < 0.01,
      f"{lots[0]['rapport_mesure_median']}")
    v("⚠⚠ ... et une amplitude qui replie les feuilles coûte davantage",
      lots[1]["rapport_mesure_median"] > lots[0]["rapport_mesure_median"]
      and lots[1]["les_feuilles_se_croisent"],
      f"{lots[1]['rapport_mesure_median']} contre {lots[0]['rapport_mesure_median']}")

    # ---- le verdict
    def lot(amp, mes, pre, croisent, incl):
        return {"amplitude_um": amp, "amplitude_sur_espacement": round(amp / 173.0, 2),
                "inclinaison_max_deg": incl, "rapport_mesure_median": mes,
                "rapport_predit_median": pre, "les_feuilles_se_croisent": croisent,
                "part_du_rayon_ou_la_phase_recule": 0.09 if croisent else 0.0,
                "marches": [{}]}

    faux = {"lots": [lot(0.0, 1.0, 1.0, False, 0.0), lot(42.4, 1.008, 1.026, False, 34.09),
                     lot(200.0, 1.20, 1.44, True, 72.61)]}
    j = juger(u, faux)
    v("le verdict nomme l'amplitude qui atteint le rouleau et ce qu'elle fait à la matière",
      j["decidable"] and j["amplitude_qui_atteint_le_rouleau_um"] == 200.0
      and j["a_cette_amplitude_les_feuilles_se_croisent"], f"{j.get('amplitude_sur_espacement')}")
    v("... et il dit que le froissement n'explique PAS le rouleau sans replier les feuilles",
      not j["le_froissement_explique_le_rouleau"],
      f"au plus {j['rapport_le_plus_haut_sans_croiser']} sans croiser")
    # ⚠⚠ LA SONDE DU VERDICT : si une amplitude SAINE atteignait le rouleau, il doit basculer.
    faux2 = {"lots": [lot(0.0, 1.0, 1.0, False, 0.0), lot(42.4, 1.25, 1.30, False, 34.09)]}
    j2 = juger(u, faux2)
    v("⚠⚠ sonde : un froissement sain qui atteint le rouleau fait basculer le verdict",
      j2["le_froissement_explique_le_rouleau"], f"{j2['rapport_le_plus_haut_sans_croiser']}")
    faux3 = {"lots": [lot(0.0, 1.0, 1.0, False, 0.0), lot(42.4, 1.008, 1.026, False, 34.09)]}
    j3 = juger(u, faux3)
    v("⚠ ... et si aucune amplitude n'y arrive, il le dit au lieu d'extrapoler",
      j3.get("aucune_amplitude_essayee_natteint_le_rouleau") is True,
      f"au plus {j3['rapport_le_plus_haut_atteint']}")
    v("la part de l'obliquité que le cap récupère est publiée",
      j["part_de_lobliquite_que_le_cap_recupere"] is not None,
      f"{j['part_de_lobliquite_que_le_cap_recupere']}")
    v("une moitié absente rend indécidable", not juger(u, {"lots": []})["decidable"])

    # ---- l'affichage
    import contextlib, io  # noqa: PLC0415
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"inclinaison_mesuree_deg": INCLINAISON_MESUREE_DEG,
                  "espacements_um": list(ESPACEMENTS_UM), "rayons_mm": list(RAYONS_MM),
                  "linclinaison_uniforme_est_elle_possible": u,
                  "sur_la_spirale_froissee": {**court, "lots": faux["lots"]}, "juger": j})
    sortie = tampon.getvalue()
    v("l'affichage tourne sur un résultat complet",
      "feuilles par tour" in sortie and "les feuilles se croisent" in sortie)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "fixture injoignable"})
    v("... et un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f, exc) -> bool:
    try:
        f()
    except exc:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--pas-max", type=int, default=PAS_MAX)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(departs=a.departs, pas_max=a.pas_max)
    afficher(r)
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False, default=float))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
