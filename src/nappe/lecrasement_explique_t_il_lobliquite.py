#!/usr/bin/env python3
"""L'ecrasement du rouleau explique-t-il l'obliquite du chemin ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET POURQUOI IL EST LE DERNIER CANDIDAT. `136` mesure que le chemin
d'une traversee vaut **1,186** fois son etendue radiale ; `137` que ce chemin penche de **25,48°**
sur le rayon, d'un penchant COHERENT (0,925). `139` a elimine les deux explications evidentes : une
inclinaison uniforme est impossible sur un objet qui croise une feuille par tour, et un froissement
de l'amplitude mesuree ne fait payer que 1,0078 — celle qu'il faudrait replie les feuilles les unes
sur les autres. Ce qui reste est deja mesure ailleurs : **le rouleau est ECRASE**. `90` le mesure,
et `135` lit une surface exterieure qui va de **16,8 a 29,75 mm** selon le rayon, ce qui est
precisement pourquoi `116` ne trouvait pas de frontiere RADIALE.

⭐⭐⭐ ET UN ECRASEMENT DONNE CE QU'UN FROISSEMENT NE DONNE PAS : UNE INCLINAISON COHERENTE. Sur une
section elliptique, la normale d'une feuille et la direction du centre different d'un angle qui
tourne avec l'angle polaire, de periode `pi` — donc constant a l'echelle d'une marche. Un
froissement, lui, alterne. C'est la coherence qui separe les deux, et `137` l'a mesuree.

⚠⚠ TROIS GRANDEURS DOIVENT TOMBER ENSEMBLE, ET C'EST CE QUI REND LA MESURE CAPABLE D'ECHOUER. Une
fixture qui reproduirait le rapport en se trompant sur le penchant, ou le penchant en se trompant
sur la coherence, n'expliquerait rien — elle aurait seulement un parametre de plus. Le verdict porte
donc sur les trois a la fois : rapport **1,186**, penchant **25,48°**, coherence **0,925**.

⚠ L'ecrasement n'est PAS ajuste pour que ca tombe : il est calcule depuis les deux rayons que `135`
publie. Ce qui est balaye autour de lui sert a voir la pente, pas a choisir la reponse.

Usage :
    uv run python src/nappe/lecrasement_explique_t_il_lobliquite.py --verifier
    uv run python src/nappe/lecrasement_explique_t_il_lobliquite.py \\
        --json docs/mesures/lecrasement_explique_t_il_lobliquite.json
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

# ⚠ Les deux rayons de surface que `135` publie, d'ou l'ecrasement se DERIVE — jamais un chiffre
# pose a la main pour que la mesure tombe juste.
SURFACE_MIN_MM = 16.8
SURFACE_MAX_MM = 29.75
# ⚠ Les trois grandeurs du rouleau, passees en parametres : ce sont les nombres d'AUTRES tranches
# (`136` et `137`), et ils doivent pouvoir changer sans qu'on touche a ce fichier.
RAPPORT_DU_ROULEAU = 1.186
PENCHANT_DU_ROULEAU_DEG = 25.48
COHERENCE_DU_ROULEAU = 0.925
LONGUEUR_DONDE_UM = 393.6
RAYON_MM = 10.0
CENTRE_YX_VX = (6000.0, 6000.0)
FORME = (4000, 16000, 16000)
PAS_MAX = 40
DEPARTS = 10


def lecrasement_que_la_surface_impose(surface_min_mm: float = SURFACE_MIN_MM,
                                      surface_max_mm: float = SURFACE_MAX_MM) -> dict:
    """L'aplatissement qu'une surface exterieure allant de `min` a `max` impose.

    ⚠ L'aplatissement `e` est defini par `(1+e)/(1-e) = max/min`, donc
    `e = (max - min) / (max + min)`. C'est le seul parametre de la fixture, et il vient d'une
    mesure — `135` §3 — et non d'un ajustement.
    """
    if not 0.0 < surface_min_mm <= surface_max_mm:
        return {"decidable": False, "pourquoi": "deux rayons de surface positifs et ordonnes"}
    e = (surface_max_mm - surface_min_mm) / (surface_max_mm + surface_min_mm)
    return {"decidable": True, "surface_min_mm": float(surface_min_mm),
            "surface_max_mm": float(surface_max_mm),
            "rapport_des_axes": round(float(surface_max_mm / surface_min_mm), 3),
            "ecrasement": round(float(e), 4)}


def _barres():
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    return (longueurs, mu, sd, barre, nul_du_tenseur(demi=20)["accord_des_moities_p1_deg"],
            max(x["p99"] for x in C.accord_du_bruit_pur().values()), C)


def une_marche(vol, angle_rad: float, barres, rayon_mm: float = RAYON_MM,
               pas_max: int = PAS_MAX) -> dict | None:
    """Une marche partie d'une phase ENTIERE, et les trois grandeurs qu'elle rend.

    ⚠ Le rayon est CIRCULAIRE, mesure depuis le centre — jamais le rayon elliptique de la fixture.
    C'est ce qu'un dérouleur mesure, et c'est ce que `136` a mesure sur le rouleau : confondre les
    deux ferait disparaitre l'effet qu'on cherche.
    """
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415

    longueurs, mu, sd, barre, barre_moities, barre_interstice, C = barres
    z = np.array([1.0, 0.0, 0.0])
    # ⚠ Le centre vient du VOLUME, jamais de la constante de module. Les deux s'accordent pour les
    # fixtures de ce fichier, donc rien n'y change ; mais un appelant qui pose sa spirale ailleurs
    # (`141` l'elargit pour tenir soixante-quinze pas) mesurait son etendue radiale autour d'un axe
    # qui n'etait pas le sien, et `etendue <= 0` rendait la marche INDECIDABLE sans rien dire.
    cy, cx = vol.centre_yx_vx
    r_vx = float(rayon_mm) * 1000.0 / C.VOXEL_FIN_UM
    radial = np.array([0.0, np.sin(angle_rad), np.cos(angle_rad)])
    p0 = np.array([2000.0, cy + r_vx * np.sin(angle_rad), cx + r_vx * np.cos(angle_rad)])
    ph = float(vol.phase(p0.reshape(1, 3))[0])
    depart = p0 + radial * ((round(ph) - ph) * vol.pas_um / C.VOXEL_FIN_UM)
    n0 = vol.normale_locale(depart).reshape(3)
    etapes = marcher(vol, depart, n0, longueurs, mu, sd, barre, barre_moities, barre_interstice,
                     C.VOXEL_FIN_UM, pas_max=pas_max, demi=20, fils=1, memoire_du_cap=0.75)
    pas = [e for e in etapes if "avance_um" in e]
    if len(pas) < pas_max // 2:
        return None
    axe = np.array([depart[0], cy, cx])

    def rho(q):
        u = q - axe
        u = u - (u @ z) * z
        return float(np.linalg.norm(u))

    p, chemin = depart.copy(), 0.0
    angles, normales = [], []
    tangent_net, tangent_parcouru = np.zeros(3), 0.0
    r0 = rho(p)
    for e in pas:
        d = np.asarray(e["direction"], dtype=float)
        d = d / max(float(np.linalg.norm(d)), 1e-12)
        u = p - axe
        u = u - (u @ z) * z
        rh = u / max(float(np.linalg.norm(u)), 1e-12)
        n = vol.normale_locale(p).reshape(3)
        normales.append(float(np.degrees(np.arccos(np.clip(abs(float(n @ rh)), -1.0, 1.0)))))
        cr = float(d @ rh)
        angles.append(float(np.degrees(np.arccos(np.clip(cr, -1.0, 1.0)))))
        t = d - cr * rh
        a = float(e["avance_um"])
        tangent_net = tangent_net + t * a
        tangent_parcouru += float(np.linalg.norm(t)) * a
        chemin += a
        p = p + d * (a / C.VOXEL_FIN_UM)
    etendue = (rho(p) - r0) * C.VOXEL_FIN_UM
    if etendue <= 0.0:
        return None
    ang = np.asarray(angles)
    return {"angle_deg": round(float(np.degrees(angle_rad)), 1), "pas": len(pas),
            # ⚠ Les angles PAS A PAS, sous le meme nom que dans `137` : c'est la seule facon de
            # comparer la forme d'une queue a armes egales, et une mediane ne la porte pas.
            "angles_deg": [round(float(a), 2) for a in angles],
            "chemin_um": round(chemin, 1), "etendue_radiale_um": round(etendue, 1),
            "rapport": round(chemin / etendue, 4),
            "penchant_median_deg": round(float(np.median(ang)), 2),
            "penchant_p90_deg": round(float(np.percentile(ang, 90)), 2),
            "inclinaison_de_la_normale_deg": round(float(np.median(normales)), 2),
            "rapport_predit": round(float(
                1.0 / np.mean(np.cos(np.radians(np.asarray(normales))))), 4),
            "coherence_tangentielle": round(
                float(np.linalg.norm(tangent_net) / max(tangent_parcouru, 1e-12)), 3)}


def sur_la_spirale(lots, rayon_mm: float = RAYON_MM, departs: int = DEPARTS,
                   pas_max: int = PAS_MAX, longueur_donde_um: float = LONGUEUR_DONDE_UM,
                   graine: int = 3) -> dict:
    """Les trois grandeurs, pour chaque couple (ecrasement, amplitude).

    ⭐⭐ Les trois matieres du balayage sont l'ECRASEMENT seul, le FROISSEMENT seul et LES DEUX :
    c'est la seule facon de dire si l'un des deux suffit, et `139` a deja montre que le second ne
    suffit pas.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpiraleFroissee  # noqa: PLC0415
    from une_inclinaison_uniforme_est_elle_possible import la_phase_recule_t_elle  # noqa: PLC0415

    barres = _barres()
    C = barres[-1]
    out = []
    for ecrasement, amplitude in lots:
        vol = VolumeFabriqueEnSpiraleFroissee(
            C.PAS_UM, amplitude_um=float(amplitude), longueur_donde_um=float(longueur_donde_um),
            ecrasement=float(ecrasement), r0_um=float(rayon_mm) * 1000.0,
            centre_yx_vx=CENTRE_YX_VX, forme=FORME, graine=graine)
        marches = [m for m in (une_marche(vol, 2.0 * np.pi * k / int(departs), barres,
                                          rayon_mm, pas_max) for k in range(int(departs)))
                   if m is not None]
        bloc = {"ecrasement": float(ecrasement), "amplitude_um": float(amplitude),
                "rapport_des_axes": round(vol.rapport_des_axes(), 3),
                "inclinaison_max_du_froissement_deg": round(vol.inclinaison_max_deg(), 2),
                "marches": marches, **la_phase_recule_t_elle(vol)}
        if marches:
            for cle, nom in (("rapport", "rapport"), ("penchant_median_deg", "penchant"),
                             ("penchant_p90_deg", "penchant_p90"),
                             ("coherence_tangentielle", "coherence"),
                             ("rapport_predit", "rapport_predit"),
                             ("inclinaison_de_la_normale_deg", "inclinaison_de_la_normale")):
                bloc[f"{nom}_median"] = round(float(np.median([m[cle] for m in marches])), 4)
        out.append(bloc)
    return {"rayon_mm": float(rayon_mm), "longueur_donde_um": float(longueur_donde_um),
            "pas_max": int(pas_max), "departs": int(departs), "lots": out}


def juger(ecrase: dict, balayage: dict, rapport: float = RAPPORT_DU_ROULEAU,
          penchant: float = PENCHANT_DU_ROULEAU_DEG,
          coherence: float = COHERENCE_DU_ROULEAU) -> dict:
    """Quelle matiere reproduit les TROIS grandeurs du rouleau a la fois ?

    ⭐⭐⭐⭐ LE VERDICT PORTE SUR TROIS QUANTITES ENSEMBLE, et c'est ce qui le rend refutable. Une
    fixture qui reproduirait le rapport en se trompant sur la coherence n'expliquerait rien. La
    distance publiee est l'ecart RELATIF le plus grand des trois : c'est la grandeur la moins bien
    reproduite qui juge, jamais la moyenne, qui laisserait une erreur grossiere se faire pardonner
    par deux accords.

    ⚠ Aucun seuil n'est pose sur cette distance : le fichier publie QUELLE matiere est la plus
    proche et de combien, et le lecteur voit les trois ecarts. Ce qui est verdict, en revanche,
    c'est qu'aucune des deux causes PRISES SEULE n'y arrive.
    """
    lots = [x for x in balayage.get("lots", []) if "rapport_median" in x]
    if not lots or not ecrase.get("decidable"):
        return {"decidable": False, "pourquoi": "une des deux moities n'a rien rendu"}

    def distance(x):
        return max(abs(x["rapport_median"] - rapport) / rapport,
                   abs(x["penchant_median"] - penchant) / penchant,
                   abs(x["coherence_median"] - coherence) / coherence)

    out = {"decidable": True, "rapport_du_rouleau": float(rapport),
           "penchant_du_rouleau_deg": float(penchant),
           "coherence_du_rouleau": float(coherence),
           "ecrasement_mesure": ecrase["ecrasement"],
           "rapport_des_axes_mesure": ecrase["rapport_des_axes"], "par_lot": []}
    for x in lots:
        out["par_lot"].append({
            "ecrasement": x["ecrasement"], "amplitude_um": x["amplitude_um"],
            "rapport": x["rapport_median"], "penchant": x["penchant_median"],
            "coherence": x["coherence_median"],
            "distance_la_pire_des_trois": round(distance(x), 4)})
    meilleur = min(lots, key=distance)
    out.update({"le_plus_proche_ecrasement": meilleur["ecrasement"],
                "le_plus_proche_amplitude_um": meilleur["amplitude_um"],
                "le_plus_proche_rapport": meilleur["rapport_median"],
                "le_plus_proche_penchant": meilleur["penchant_median"],
                "le_plus_proche_coherence": meilleur["coherence_median"],
                "le_plus_proche_distance": round(distance(meilleur), 4)})
    seul_e = [x for x in lots if x["amplitude_um"] == 0.0 and x["ecrasement"] > 0.0]
    seul_f = [x for x in lots if x["ecrasement"] == 0.0 and x["amplitude_um"] > 0.0]
    deux = [x for x in lots if x["ecrasement"] > 0.0 and x["amplitude_um"] > 0.0]
    for nom, lot in (("ecrasement_seul", seul_e), ("froissement_seul", seul_f),
                     ("les_deux", deux)):
        if lot:
            m = min(lot, key=distance)
            out[f"meilleure_distance_{nom}"] = round(distance(m), 4)
    # ⭐⭐ LE VERDICT : la composition fait-elle mieux que chacune des deux causes SEULE ? C'est la
    # seule chose que ce balayage peut trancher, et elle peut etre fausse.
    if all(f"meilleure_distance_{n}" in out
           for n in ("ecrasement_seul", "froissement_seul", "les_deux")):
        out["les_deux_font_mieux_que_chacune_seule"] = bool(
            out["meilleure_distance_les_deux"] < out["meilleure_distance_ecrasement_seul"]
            and out["meilleure_distance_les_deux"] < out["meilleure_distance_froissement_seul"])
    # ⚠ Et la coherence est ce qui separe les deux causes : l'ecrasement en donne trop, le
    # froissement pas assez. Le dire chiffres a l'appui.
    if seul_e and seul_f:
        out["coherence_ecrasement_seul"] = max(x["coherence_median"] for x in seul_e)
        out["coherence_froissement_seul"] = min(x["coherence_median"] for x in seul_f)
    return out


def mesurer(lots=None, departs: int = DEPARTS, pas_max: int = PAS_MAX) -> dict:
    ecrase = lecrasement_que_la_surface_impose()
    e = ecrase["ecrasement"]
    if lots is None:
        # ⚠ Le balayage tient l'ecrasement MESURE au centre et regarde de part et d'autre : ce qui
        # est cherche est la pente, pas un ajustement.
        lots = ((0.0, 0.0), (e, 0.0), (2 * e, 0.0), (0.0, 42.4), (0.0, 100.0),
                (e, 42.4), (e, 100.0), (2 * e, 100.0))
    balayage = sur_la_spirale(lots, departs=departs, pas_max=pas_max)
    return {"lecrasement_que_la_surface_impose": ecrase,
            "rapport_du_rouleau": RAPPORT_DU_ROULEAU,
            "penchant_du_rouleau_deg": PENCHANT_DU_ROULEAU_DEG,
            "coherence_du_rouleau": COHERENCE_DU_ROULEAU,
            "sur_la_spirale": balayage, "juger": juger(ecrase, balayage)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    e = r["lecrasement_que_la_surface_impose"]
    print(f"la surface extérieure va de {e['surface_min_mm']} à {e['surface_max_mm']} mm (`135`) → "
          f"rapport des axes {e['rapport_des_axes']}, écrasement {e['ecrasement']}")
    b = r["sur_la_spirale"]
    print(f"\nspirale (rayon {b['rayon_mm']} mm, λ {b['longueur_donde_um']} µm, {b['pas_max']} pas, "
          f"{b['departs']} départs) — le rouleau vaut {r['rapport_du_rouleau']} · "
          f"{r['penchant_du_rouleau_deg']}° · {r['coherence_du_rouleau']} :")
    print(f"   {'écrasement':>10} {'amplitude':>10} {'axes':>7} {'rapport':>8} {'prédit':>8} "
          f"{'penchant':>9} {'cohérence':>10} {'distance':>9}")
    dist = {(x["ecrasement"], x["amplitude_um"]): x["distance_la_pire_des_trois"]
            for x in r.get("juger", {}).get("par_lot", [])}
    for x in b["lots"]:
        if "rapport_median" not in x:
            print(f"   {x['ecrasement']:>10.4f} {x['amplitude_um']:>10.1f}   aucune marche")
            continue
        d = dist.get((x["ecrasement"], x["amplitude_um"]))
        print(f"   {x['ecrasement']:>10.4f} {x['amplitude_um']:>10.1f} {x['rapport_des_axes']:>7.3f} "
              f"{x['rapport_median']:>8.4f} {x['rapport_predit_median']:>8.4f} "
              f"{x['penchant_median']:>8.2f}° {x['coherence_median']:>10.3f} "
              f"{(f'{d:.4f}' if d is not None else '—'):>9}"
              + ("  ✗ les feuilles se croisent" if x["les_feuilles_se_croisent"] else ""))
    j = r.get("juger", {})
    if j.get("decidable"):
        print(f"\n★★★ le plus proche des trois grandeurs : écrasement "
              f"{j['le_plus_proche_ecrasement']}, amplitude {j['le_plus_proche_amplitude_um']} µm → "
              f"{j['le_plus_proche_rapport']} · {j['le_plus_proche_penchant']}° · "
              f"{j['le_plus_proche_coherence']} (distance {j['le_plus_proche_distance']})")
        if "les_deux_font_mieux_que_chacune_seule" in j:
            print(f"★★★★ les deux causes ensemble font mieux que chacune seule : "
                  f"{j['les_deux_font_mieux_que_chacune_seule']} — écrasement seul "
                  f"{j['meilleure_distance_ecrasement_seul']}, froissement seul "
                  f"{j['meilleure_distance_froissement_seul']}, les deux "
                  f"{j['meilleure_distance_les_deux']}")
        if "coherence_ecrasement_seul" in j:
            print(f"★★ et c'est la COHÉRENCE qui les sépare : écrasement seul "
                  f"{j['coherence_ecrasement_seul']}, froissement seul "
                  f"{j['coherence_froissement_seul']}, le rouleau {j['coherence_du_rouleau']}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- l'écrasement que la surface impose
    e = lecrasement_que_la_surface_impose()
    v("l'écrasement se dérive des deux rayons de surface de `135`",
      e["decidable"] and abs(e["rapport_des_axes"] - 29.75 / 16.8) < 1e-3,
      f"e = {e['ecrasement']}, rapport {e['rapport_des_axes']}")
    v("... et il redonne exactement le rapport des axes",
      abs((1 + e["ecrasement"]) / (1 - e["ecrasement"]) - e["rapport_des_axes"]) < 2e-3)
    v("une surface ronde donne un écrasement nul",
      lecrasement_que_la_surface_impose(10.0, 10.0)["ecrasement"] == 0.0)
    # ⚠⚠ LA SONDE : deux rayons dans le mauvais ordre, ou negatifs, doivent etre REFUSES. Sans elle
    # un ecrasement negatif passerait pour une ellipse tournee d'un quart de tour.
    v("⚠⚠ sonde : deux rayons mal ordonnés sont refusés",
      not lecrasement_que_la_surface_impose(29.75, 16.8)["decidable"])
    v("... et un rayon nul aussi", not lecrasement_que_la_surface_impose(0.0, 10.0)["decidable"])

    # ---- le jugement sur TROIS grandeurs
    def lot(ec, amp, rap, pen, coh, croisent=False):
        return {"ecrasement": ec, "amplitude_um": amp, "rapport_des_axes": 1.0,
                "inclinaison_max_du_froissement_deg": 0.0, "marches": [{}],
                "les_feuilles_se_croisent": croisent,
                "part_du_rayon_ou_la_phase_recule": 0.0, "et_au_plus": 0.0,
                "rapport_median": rap, "penchant_median": pen, "coherence_median": coh,
                "penchant_p90_median": pen + 8.0, "rapport_predit_median": rap,
                "inclinaison_de_la_normale_median": pen}

    parfait = lot(0.3, 100.0, RAPPORT_DU_ROULEAU, PENCHANT_DU_ROULEAU_DEG, COHERENCE_DU_ROULEAU)
    j = juger(e, {"lots": [lot(0.28, 0.0, 1.05, 20.0, 0.999), lot(0.0, 42.4, 1.005, 4.3, 0.392),
                           parfait]})
    v("le verdict trouve la matière la plus proche des TROIS grandeurs",
      j["decidable"] and abs(j["le_plus_proche_distance"]) < 1e-9,
      f"écrasement {j['le_plus_proche_ecrasement']}, amplitude "
      f"{j['le_plus_proche_amplitude_um']} µm, distance {j['le_plus_proche_distance']}")
    # ⚠ La comparaison se fait sur la valeur ARRONDIE que le fichier publie : exiger l'egalite au
    # flottant pres ferait echouer un controle juste a cause du `round` de la publication.
    v("... et la distance est la PIRE des trois, jamais leur moyenne",
      [x for x in j["par_lot"] if x["amplitude_um"] == 0.0][0]["distance_la_pire_des_trois"]
      == round(max(abs(1.05 - 1.186) / 1.186, abs(20.0 - 25.48) / 25.48,
                   abs(0.999 - 0.925) / 0.925), 4))
    # ⚠⚠ LA SONDE QUI REND LA DISTANCE UTILE : une matiere qui reproduit DEUX grandeurs sur trois
    # et rate la troisieme doit etre PLUS LOIN qu'une qui les approche toutes. Une moyenne lui
    # pardonnerait.
    deux_sur_trois = lot(0.5, 50.0, RAPPORT_DU_ROULEAU, PENCHANT_DU_ROULEAU_DEG, 0.30)
    presque = lot(0.4, 60.0, 1.15, 24.0, 0.90)
    j2 = juger(e, {"lots": [deux_sur_trois, presque]})
    v("⚠⚠ sonde : deux grandeurs justes et une fausse est PLUS LOIN que trois approchées",
      j2["le_plus_proche_amplitude_um"] == 60.0,
      f"{[x['distance_la_pire_des_trois'] for x in j2['par_lot']]}")
    v("le verdict compare les deux causes seules à leur composition",
      j["les_deux_font_mieux_que_chacune_seule"],
      f"écrasement seul {j['meilleure_distance_ecrasement_seul']}, froissement seul "
      f"{j['meilleure_distance_froissement_seul']}, les deux {j['meilleure_distance_les_deux']}")
    # ⚠⚠ ET LA SONDE INVERSE : si la composition faisait MOINS bien, le verdict doit basculer.
    j3 = juger(e, {"lots": [lot(0.28, 0.0, 1.186, 25.48, 0.925), lot(0.0, 42.4, 1.005, 4.3, 0.392),
                            lot(0.3, 100.0, 1.4, 40.0, 0.5)]})
    v("⚠⚠ sonde : une composition moins bonne fait basculer le verdict",
      not j3["les_deux_font_mieux_que_chacune_seule"])
    v("... et la cohérence des deux causes seules est publiée à côté de celle du rouleau",
      j["coherence_ecrasement_seul"] == 0.999 and j["coherence_froissement_seul"] == 0.392)
    v("aucun lot rend indécidable", not juger(e, {"lots": []})["decidable"])
    v("un écrasement indécidable rend indécidable",
      not juger({"decidable": False}, {"lots": [parfait]})["decidable"])

    # ⚠ Le chemin qui produit le nombre publié est ATTEINT, sur trois matières et peu de pas.
    court = sur_la_spirale(((0.0, 0.0), (e["ecrasement"], 0.0), (e["ecrasement"], 100.0)),
                           departs=3, pas_max=10)
    lots = court["lots"]
    v("l'assemblage marche sur les trois matières", all("rapport_median" in x for x in lots),
      " · ".join(f"e={x['ecrasement']:.3f} A={x['amplitude_um']:.0f} → {x['rapport_median']}"
                 for x in lots))
    v("⚠ ... et une spirale ronde et lisse ne coûte rien",
      abs(lots[0]["rapport_median"] - 1.0) < 0.01 and lots[0]["penchant_median"] < 1.0,
      f"{lots[0]['rapport_median']} · {lots[0]['penchant_median']}°")
    v("⚠⚠ ... et un écrasement SEUL rend une cohérence quasi parfaite",
      lots[1]["coherence_median"] > 0.99, f"{lots[1]['coherence_median']}")
    v("⚠⚠ ... que le froissement ajouté FAIT BAISSER, comme sur le rouleau",
      lots[2]["coherence_median"] < lots[1]["coherence_median"],
      f"{lots[2]['coherence_median']} contre {lots[1]['coherence_median']}")

    # ---- l'affichage
    import contextlib, io  # noqa: PLC0415
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"lecrasement_que_la_surface_impose": e,
                  "rapport_du_rouleau": RAPPORT_DU_ROULEAU,
                  "penchant_du_rouleau_deg": PENCHANT_DU_ROULEAU_DEG,
                  "coherence_du_rouleau": COHERENCE_DU_ROULEAU,
                  "sur_la_spirale": court, "juger": juger(e, court)})
    sortie = tampon.getvalue()
    v("l'affichage tourne sur un résultat complet",
      "écrasement" in sortie and "cohérence" in sortie)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "fixture injoignable"})
    v("... et un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


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
