"""L'angle publié est-il celui des fibres ? — un nombre juste sous un nom faux.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL VIENT D'UNE SONDE AVANT UNE TRANCHE. En préparant l'alarme des
fibres, j'ai posé le tenseur de structure sur un motif dont la direction des crêtes était CHOISIE.
Il a rendu un angle à **90° des crêtes**. Or `fiber_orientation.py` écrit dans son propre en-tête
que la formule donne « la direction le long de laquelle l'image varie le MOINS », et
`14_direction_des_fibres.md` répète cette lecture en publiant des angles ABSOLUS.

⚠⚠ LA FORME CLOSE DONNE LE PLUS GRAND VECTEUR PROPRE, PAS LE PLUS PETIT. Pour le tenseur
`J = [[Jxx, Jxy], [Jxy, Jyy]]`, l'angle `½·atan2(2·Jxy, Jxx − Jyy)` est celui du vecteur propre
DOMINANT, c'est-à-dire la direction du GRADIENT — donc la perpendiculaire à la structure. La
direction des fibres est à quatre-vingt-dix degrés de là.

⭐⭐⭐⭐ ET LA VALEUR RENDUE N'EST PAS CHANGÉE, DÉLIBÉRÉMENT. Les courbes publiées
(`fibres_scroll1.json`, `fibres_corpus.json`) portent ces angles ; corriger la formule déplacerait
des nombres déjà publiés pour réparer un NOM. Ce module mesure donc ce que le décalage atteint et ce
qu'il n'atteint pas, et `direction_des_fibres_deg` nomme la conversion là où quelqu'un en a besoin.

⚠⚠⚠ CE QUI EST EN JEU N'EST PAS UNE CONCLUSION MAIS UNE DESCRIPTION. Tout ce que la campagne des
fibres publie d'autre est un ÉCART — désaccord entre voisins, bascule en profondeur, parts au-delà
d'un angle — et un écart est invariant par un décalage constant. C'est mesuré ici plutôt qu'affirmé,
sur les courbes stockées et sur un balayage dense. Ce qui est atteint est l'angle lui-même, et tout
raisonnement qui le compare à une référence EXTÉRIEURE.

⚠ CONTRÔLE OBLIGATOIRE : un motif sans texture n'a pas de direction, seulement une cohérence nulle.
L'écart y est celui de deux angles aléatoires, donc il ne dit rien — à dire, jamais à chiffrer.

Usage :
    uv run python src/nappe/langle_publie_est_il_celui_des_fibres.py --verifier
    uv run python src/nappe/langle_publie_est_il_celui_des_fibres.py \\
        --json docs/mesures/langle_publie_est_il_celui_des_fibres.json
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

from fiber_orientation import (angular_gap, circular_mean,  # noqa: E402
                               orientation_profile)

MESURES = RACINE / "docs" / "mesures"
LES_CAMPAGNES = ("fibres_scroll1.json", "fibres_corpus.json", "fibres_1667.json")
# ⚠ Les angles de crete sont CHOISIS sur la grille : a 0, 45, 90 et 135 degres un motif
# echantillonne sur un reseau carre n'est pas discretise, donc l'ecart mesure est celui de la
# formule et pas celui du pixel. Les autres sont gardes a cote pour que la discretisation soit
# VISIBLE plutot que evitee.
CRETES_EXACTES = (0.0, 45.0, 90.0, 135.0)
CRETES_OBLIQUES = (15.0, 30.0, 60.0, 75.0, 105.0, 120.0)
COTE = 96
PERIODE_DU_MOTIF = 8.0
LE_QUART_DE_TOUR = 90.0


def direction_des_fibres_deg(angle_deg):
    """La direction des FIBRES, depuis l'angle que `orientation_profile` rend.

    ⭐ C'est la conversion, et elle est écrite UNE FOIS. `orientation_profile` rend la direction du
    gradient — celle le long de laquelle l'image varie le PLUS — donc les fibres sont à un quart de
    tour de là. Un appelant qui referait le calcul chez lui serait une seconde réponse à « où
    pointent les fibres », libre de diverger d'un signe.

    ⚠ Une orientation est modulo 180° : ajouter ou retrancher le quart de tour donne le même
    résultat, et c'est pour cela qu'aucun signe n'entre.
    """
    return (np.asarray(angle_deg, dtype=float) + LE_QUART_DE_TOUR) % 180.0


def un_motif_de_cretes(angle_deg: float, cote: int = COTE,
                       periode: float = PERIODE_DU_MOTIF) -> np.ndarray:
    """Une image dont les crêtes courent à un angle CHOISI — la réponse est connue d'avance.

    ⚠⚠ ELLE NE DOIT RIEN A LA FIXTURE DU DÉPÔT. Si le décalage venait de la convention d'axes de
    `VolumeFabriqueAFibres`, un motif construit ici le montrerait à zéro : c'est le seul moyen de
    savoir si c'est la formule qui décale ou le volume qui est monté de travers.

    ⚠ L'angle se compte depuis l'axe **2** vers l'axe **1**, parce que `orientation_profile` dérive
    `gx` sur l'axe 2 et `gy` sur l'axe 1. Poser la convention ailleurs mesurerait l'indexation.
    """
    i, j = np.meshgrid(np.arange(cote), np.arange(cote), indexing="ij")
    th = np.deg2rad(float(angle_deg))
    # ⚠ La matiere varie EN TRAVERS des cretes : une crete court le long de la direction demandee.
    s = -np.sin(th) * j + np.cos(th) * i
    return np.cos(2.0 * np.pi * s / float(periode))[None, :, :]


def ce_que_la_formule_rend(angles=CRETES_EXACTES, cote: int = COTE) -> dict:
    """Pour chaque direction de crête choisie, l'angle rendu et son écart à elle."""
    lignes = []
    for a in angles:
        ang, coh = orientation_profile(un_motif_de_cretes(a, cote))
        lu = float(ang[0])
        lignes.append({"cretes_deg": float(a), "angle_rendu_deg": round(lu, 3),
                       "ecart_aux_cretes_deg": round(float((lu - a) % 180.0), 3),
                       "coherence": round(float(coh[0]), 3),
                       "les_fibres_lues_deg": round(float(direction_des_fibres_deg(lu)), 3),
                       "la_conversion_retombe_sur_les_cretes": bool(
                           angular_gap(float(direction_des_fibres_deg(lu)), float(a)) < 1e-6)})
    return {"decidable": bool(lignes), "lignes": lignes,
            "cote": int(cote), "periode": float(PERIODE_DU_MOTIF)}


def _median(v):
    return round(float(statistics.median(v)), 3) if v else None


def le_verdict_du_motif(r: dict) -> dict:
    """La formule rend-elle les crêtes, ou leur perpendiculaire ?

    ⚠⚠ L'ÉNONCÉ EST EXACT ET SANS SEUIL : on ne demande pas si l'écart est « grand », on demande
    s'il vaut le quart de tour pour TOUTES les directions choisies. Une formule qui rendrait la
    direction des crêtes donnerait zéro partout ; une qui rendrait n'importe quoi donnerait des
    écarts qui varient avec l'angle.
    """
    if not r.get("decidable"):
        return {"decidable": False, "raison": "aucune direction mesurée"}
    ecarts = [x["ecart_aux_cretes_deg"] for x in r["lignes"]]
    return {"decidable": True, "directions": len(ecarts),
            "ecart_median_deg": _median(ecarts),
            "ecart_min_deg": round(min(ecarts), 3), "ecart_max_deg": round(max(ecarts), 3),
            "toutes_a_un_quart_de_tour": bool(
                all(abs(e - LE_QUART_DE_TOUR) < 1e-6 for e in ecarts)),
            "aucune_sur_les_cretes": bool(all(angular_gap(e, 0.0) > 1.0 for e in ecarts)),
            "la_conversion_retombe_partout": bool(
                all(x["la_conversion_retombe_sur_les_cretes"] for x in r["lignes"]))}


def sur_la_fixture_a_deux_plis(pas_um: float, voxel_um: float, couches: int = 128,
                               cote: int = 64, angle_du_premier_pli_deg: float = 30.0) -> dict:
    """La même question sur la fixture du dépôt, dont les deux plis sont perpendiculaires.

    ⭐⭐⭐⭐ ELLE PORTE LES DEUX MOITIÉS DU RÉSULTAT D'UN COUP : l'angle ABSOLU de chaque pli est
    décalé du quart de tour, et l'ÉCART entre les deux plis vaut quatre-vingt-dix degrés quand même.
    C'est exactement ce qui fait qu'un nom peut être faux sans qu'aucun écart publié ne bouge.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabriqueAFibres  # noqa: PLC0415

    vol = VolumeFabriqueAFibres(pas_um, longueur_de_fibre_um=30.0, contraste_des_fibres=0.5,
                                angle_du_premier_pli_deg=float(angle_du_premier_pli_deg),
                                plis_par_feuille=2, voxel_um=voxel_um,
                                forme=(4000, 4000, 4000))
    centre = np.array([2000.0, 2000.0, 2000.0])
    pas_vx = voxel_um / vol.voxel_um
    d = (np.arange(couches) - couches / 2.0) * pas_vx
    a = (np.arange(cote) - cote / 2.0) * pas_vx
    D, I, J = np.meshgrid(d, a, a, indexing="ij")
    pts = (centre[None, None, None, :] + D[..., None] * vol.normale
           + I[..., None] * vol.e2 + J[..., None] * vol.e1)
    bloc = vol.lire(pts.reshape(-1, 3)).reshape(couches, cote, cote)
    ang, coh = orientation_profile(bloc)
    proj = ((centre + d[:, None] * vol.normale) @ vol.normale) * vol.voxel_um / vol.pas_um
    feuille = np.floor(proj)
    dans = proj - feuille
    attendu = vol.angle_du_pli_deg(feuille, dans)
    out = {"decidable": True, "couches": int(couches), "cote": int(cote),
           "voxel_um": float(voxel_um), "angle_du_premier_pli_deg": float(
               angle_du_premier_pli_deg), "par_pli": []}
    for rang in (0, 1):
        m = dans * vol.plis_par_feuille >= rang
        m &= dans * vol.plis_par_feuille < rang + 1
        if not m.any():
            continue
        lu = circular_mean(ang[m], coh[m])
        att = float(np.median(attendu[m]))
        out["par_pli"].append({
            "pli": rang, "couches": int(m.sum()), "angle_attendu_deg": round(att, 3),
            "angle_rendu_deg": round(float(lu), 3),
            "ecart_a_lattendu_deg": round(float(angular_gap(lu, att)), 3),
            "les_fibres_lues_deg": round(float(direction_des_fibres_deg(lu)), 3),
            "ecart_des_fibres_a_lattendu_deg": round(
                float(angular_gap(float(direction_des_fibres_deg(lu)), att)), 3)})
    if len(out["par_pli"]) == 2:
        p0, p1 = out["par_pli"]
        out["ecart_entre_les_plis_deg"] = round(
            float(angular_gap(p0["angle_rendu_deg"], p1["angle_rendu_deg"])), 3)
        out["ecart_entre_les_plis_apres_conversion_deg"] = round(
            float(angular_gap(p0["les_fibres_lues_deg"], p1["les_fibres_lues_deg"])), 3)
        out["lecart_ne_bouge_pas"] = bool(
            abs(out["ecart_entre_les_plis_deg"]
                - out["ecart_entre_les_plis_apres_conversion_deg"]) < 1e-6)
    return out


def _bascule_dune_courbe(courbe, plancher: float = 0.15) -> float | None:
    """La bascule en profondeur d'UNE courbe, par la recette de `fiber_orientation.survey`.

    ⚠⚠ C'EST LA MEME RECETTE, PAS UNE SECONDE. Le plancher de cohérence, le découpage en deux
    moitiés, la moyenne en angle double et l'écart modulo 180° sont ceux du producteur ; en écrire
    une variante ici ferait comparer deux définitions au lieu de deux lectures d'une seule.
    """
    a = np.asarray([x[0] for x in courbe], dtype=float)
    c = np.asarray([x[1] for x in courbe], dtype=float)
    if a.size < 8:
        return None
    fort = c > plancher
    moitie = a.size // 2
    haut, bas = fort[:moitie], fort[moitie:]
    if haut.sum() < 4 or bas.sum() < 4:
        return None
    return float(angular_gap(circular_mean(a[:moitie][haut], c[:moitie][haut]),
                             circular_mean(a[moitie:][bas], c[moitie:][bas])))


def ce_quun_quart_de_tour_atteint(campagnes=LES_CAMPAGNES, racine: Path = MESURES) -> dict:
    """Sur les campagnes STOCKÉES : quelles grandeurs bougent si l'angle tourne d'un quart ?

    ⭐⭐⭐⭐ C'EST LA PORTÉE DU DÉFAUT, ET ELLE SE MESURE PLUTÔT QUE S'ARGUMENTE. Un écart est
    invariant par un décalage constant et un angle ne l'est pas ; le dire est facile, le compter
    sur les artefacts réellement publiés l'est moins et c'est ce qui décide combien de nombres sont
    à reprendre.

    ⚠⚠ LA COURBE EST LE SEUL ARTEFACT ATTEINT, et elle est publiée : chaque segment en porte une,
    couche par couche, sous le nom d'une orientation de fibres. Le compte est rendu à côté du reste.
    """
    segments, courbes, angles, bascules_egales, bascules_lues = 0, 0, 0, 0, 0
    fichiers = []
    for nom in campagnes:
        chemin = racine / nom
        if not chemin.is_file():
            fichiers.append({"fichier": nom, "present": False})
            continue
        d = json.loads(chemin.read_text(encoding="utf-8"))
        lot = d if isinstance(d, list) else [d]
        n_seg = n_cou = n_ang = 0
        for s in lot:
            if not isinstance(s, dict):
                continue
            n_seg += 1
            c = s.get("courbe") or []
            if not c:
                continue
            n_cou += 1
            n_ang += len(c)
            avant = _bascule_dune_courbe(c)
            apres = _bascule_dune_courbe([[float(direction_des_fibres_deg(a)), w] for a, w in c])
            if avant is None or apres is None:
                continue
            bascules_lues += 1
            if abs(avant - apres) < 1e-9:
                bascules_egales += 1
        segments += n_seg
        courbes += n_cou
        angles += n_ang
        fichiers.append({"fichier": nom, "present": True, "segments": n_seg,
                         "courbes": n_cou, "angles_absolus": n_ang})
    return {"decidable": bool(fichiers), "fichiers": fichiers,
            "segments": segments, "courbes": courbes,
            # ⚠ C'est le nombre d'angles ABSOLUS publies sous le nom d'une orientation de fibres,
            # donc le nombre exact de valeurs dont la LECTURE change, et d'elles seules.
            "angles_absolus_publies": angles,
            "bascules_relues": bascules_lues, "bascules_inchangees": bascules_egales,
            "la_bascule_ne_bouge_jamais": bool(bascules_lues and
                                               bascules_egales == bascules_lues)}


def un_ecart_est_il_invariant(pas: int = 360, graine: int = 11) -> dict:
    """Un balayage dense : un écart survit-il au quart de tour, et une moyenne le suit-elle ?

    ⚠⚠ DEUX PROPRIÉTÉS DISTINCTES ET IL FAUT LES DEUX. L'écart doit être INVARIANT — il ne bouge
    pas — et la moyenne doit être ÉQUIVARIANTE — elle tourne du même quart. Une formule qui
    n'aurait que la première laisserait les angles moyens se mélanger ; une qui n'aurait que la
    seconde ferait bouger toutes les dispersions publiées.
    """
    r = np.random.default_rng(int(graine))
    a = r.uniform(0.0, 180.0, int(pas))
    b = r.uniform(0.0, 180.0, int(pas))
    w = r.uniform(0.1, 1.0, int(pas))
    ecarts = [abs(angular_gap(float(x), float(y))
                  - angular_gap(float(direction_des_fibres_deg(x)),
                                float(direction_des_fibres_deg(y)))) for x, y in zip(a, b)]
    m0 = circular_mean(a, w)
    m1 = circular_mean(np.asarray(direction_des_fibres_deg(a)), w)
    return {"decidable": True, "paires": int(pas),
            "pire_ecart_apres_le_quart_de_tour": round(float(max(ecarts)), 12),
            "lecart_est_invariant": bool(max(ecarts) < 1e-9),
            "moyenne_avant_deg": round(float(m0), 6), "moyenne_apres_deg": round(float(m1), 6),
            "la_moyenne_tourne_du_meme_quart": bool(
                angular_gap(float(m1), float((m0 + LE_QUART_DE_TOUR) % 180.0)) < 1e-9)}


def juger(motif: dict, fixture: dict, portee: dict, invariance: dict) -> dict:
    """Ce que les quatre mesures disent ensemble, sans jamais les fondre en un chiffre."""
    return {
        "decidable": bool(motif.get("decidable") and invariance.get("decidable")),
        "la_formule_rend_la_perpendiculaire": bool(motif.get("toutes_a_un_quart_de_tour")),
        "la_conversion_retombe_sur_les_fibres": bool(motif.get("la_conversion_retombe_partout")),
        "la_fixture_le_confirme": bool(
            fixture.get("decidable") and fixture.get("lecart_ne_bouge_pas")
            and all(x["ecart_des_fibres_a_lattendu_deg"] < x["ecart_a_lattendu_deg"]
                    for x in fixture.get("par_pli", []))),
        "aucun_ecart_publie_ne_bouge": bool(portee.get("la_bascule_ne_bouge_jamais")
                                            and invariance.get("lecart_est_invariant")),
        "angles_absolus_a_relire": int(portee.get("angles_absolus_publies") or 0),
        # ⚠⚠ LE VERDICT EST JOINT ET IL A DEUX MOITIES : le nom est faux ET aucun ecart ne bouge.
        # L'une sans l'autre changerait ce qu'il faut faire — reecrire une prose, ou refaire une
        # campagne.
        "un_nombre_juste_sous_un_nom_faux": bool(
            motif.get("toutes_a_un_quart_de_tour")
            and portee.get("la_bascule_ne_bouge_jamais")
            and invariance.get("lecart_est_invariant"))}


def mesurer() -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    motif = ce_que_la_formule_rend()
    verdict_motif = le_verdict_du_motif(motif)
    # ⚠ Les obliques portent LEUR verdict aussi : le document publie leur intervalle, et un
    # intervalle calcule dans la prose serait un nombre sans producteur.
    oblique = ce_que_la_formule_rend(CRETES_OBLIQUES)
    oblique = {**oblique, **le_verdict_du_motif(oblique)}
    fixture = sur_la_fixture_a_deux_plis(C.PAS_UM, C.VOXEL_FIN_UM)
    portee = ce_quun_quart_de_tour_atteint()
    invariance = un_ecart_est_il_invariant()
    return {"le_motif": {**motif, **verdict_motif},
            "les_obliques": oblique, "la_fixture": fixture,
            "la_portee": portee, "linvariance": invariance,
            "le_verdict": juger(verdict_motif, fixture, portee, invariance)}


def afficher(r: dict) -> None:
    m, o, f = r["le_motif"], r["les_obliques"], r["la_fixture"]
    p, inv, v = r["la_portee"], r["linvariance"], r["le_verdict"]
    print("L'ANGLE PUBLIÉ EST-IL CELUI DES FIBRES ?")
    print()
    print(f"  LE MOTIF ÉLÉMENTAIRE · {m['cote']}×{m['cote']}, période {m['periode']:.0f}")
    for x in m["lignes"]:
        print(f"   crêtes à {x['cretes_deg']:6.1f}°  →  rendu {x['angle_rendu_deg']:7.2f}°  "
              f"écart {x['ecart_aux_cretes_deg']:6.2f}°  ·  converti "
              f"{x['les_fibres_lues_deg']:7.2f}°  ·  retombe : "
              f"{x['la_conversion_retombe_sur_les_cretes']}")
    print(f"   ★ toutes à un quart de tour : {m['toutes_a_un_quart_de_tour']} · "
          f"aucune sur les crêtes : {m['aucune_sur_les_cretes']} · "
          f"la conversion retombe partout : {m['la_conversion_retombe_partout']}")
    print(f"   ⚠ les obliques, où la grille discrétise : écarts "
          f"{[x['ecart_aux_cretes_deg'] for x in o['lignes']]}")
    print()
    print(f"  LA FIXTURE À DEUX PLIS · {f['couches']} couches, côté {f['cote']}, "
          f"voxel {f['voxel_um']} µm, premier pli à {f['angle_du_premier_pli_deg']}°")
    for x in f.get("par_pli", []):
        print(f"   pli {x['pli']} ({x['couches']} couches) · attendu "
              f"{x['angle_attendu_deg']:6.2f}° · rendu {x['angle_rendu_deg']:7.2f}° "
              f"(écart {x['ecart_a_lattendu_deg']:5.2f}°) · converti "
              f"{x['les_fibres_lues_deg']:6.2f}° (écart "
              f"{x['ecart_des_fibres_a_lattendu_deg']:5.2f}°)")
    if "ecart_entre_les_plis_deg" in f:
        print(f"   ★ écart entre les deux plis : {f['ecart_entre_les_plis_deg']}° avant, "
              f"{f['ecart_entre_les_plis_apres_conversion_deg']}° après · il ne bouge pas : "
              f"{f['lecart_ne_bouge_pas']}")
    print()
    print(f"  LA PORTÉE · {p['segments']} segments, {p['courbes']} courbes, "
          f"{p['angles_absolus_publies']} angles absolus publiés")
    for x in p["fichiers"]:
        print(f"   {x['fichier']:<26} " + ("absent" if not x["present"] else
              f"{x['segments']} segments · {x['courbes']} courbes · "
              f"{x['angles_absolus']} angles"))
    print(f"   ★ bascules relues {p['bascules_relues']}, inchangées {p['bascules_inchangees']} "
          f"→ la bascule ne bouge jamais : {p['la_bascule_ne_bouge_jamais']}")
    print(f"   ★ sur {inv['paires']} paires tirées, pire écart après le quart de tour : "
          f"{inv['pire_ecart_apres_le_quart_de_tour']} · la moyenne tourne du même quart : "
          f"{inv['la_moyenne_tourne_du_meme_quart']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("la_formule_rend_la_perpendiculaire", "la_conversion_retombe_sur_les_fibres",
                "la_fixture_le_confirme", "aucun_ecart_publie_ne_bouge",
                "un_nombre_juste_sous_un_nom_faux"):
        print(f"     {cle:<40} {v.get(cle)}")
    print(f"     {'angles_absolus_a_relire':<40} {v.get('angles_absolus_a_relire')}")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- la conversion, et elle est une involution modulo 180
    v("la conversion est un quart de tour, et deux quarts font l'identité",
      float(direction_des_fibres_deg(37.0)) == 127.0
      and abs(float(direction_des_fibres_deg(direction_des_fibres_deg(37.0))) - 37.0) < 1e-9)
    v("... et elle reste dans [0, 180[", float(direction_des_fibres_deg(170.0)) == 80.0,
      f"{float(direction_des_fibres_deg(170.0))}")

    # ---- le motif élémentaire : la réponse est CHOISIE
    m = ce_que_la_formule_rend()
    j = le_verdict_du_motif(m)
    v("⭐⭐⭐⭐ sur un motif dont les crêtes sont CHOISIES, la formule rend leur perpendiculaire",
      j["toutes_a_un_quart_de_tour"],
      " · ".join(f"{x['cretes_deg']:.0f}°→{x['angle_rendu_deg']:.1f}°" for x in m["lignes"]))
    v("... donc AUCUNE direction rendue ne tombe sur ses crêtes", j["aucune_sur_les_cretes"],
      f"écarts {j['ecart_min_deg']} à {j['ecart_max_deg']}")
    v("... et la conversion les y ramène, toutes", j["la_conversion_retombe_partout"])
    # ⚠⚠ LE CONTROLE QUI SEPARE LA FORMULE DE LA GRILLE : sur les obliques la discrétisation
    # ajoute son propre écart, donc un contrôle qui les mélangerait mesurerait le pixel.
    ob = le_verdict_du_motif(ce_que_la_formule_rend(CRETES_OBLIQUES))
    v("⚠⚠ sur les obliques la grille discrétise, et c'est pour cela que le verdict ne les emploie "
      "pas", not ob["toutes_a_un_quart_de_tour"] and ob["ecart_max_deg"] > LE_QUART_DE_TOUR,
      f"écarts {ob['ecart_min_deg']} à {ob['ecart_max_deg']}")
    # ⚠ Un motif SANS texture n'a pas de direction — controle vide.
    plat = orientation_profile(np.zeros((1, COTE, COTE)))
    v("⚠ contrôle vide : un motif sans texture rend une cohérence nulle, donc aucune direction",
      float(plat[1][0]) == 0.0, f"cohérence {float(plat[1][0])}")

    # ---- la fixture : les deux moitiés du résultat d'un coup
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    f = sur_la_fixture_a_deux_plis(C.PAS_UM, C.VOXEL_FIN_UM)
    v("la fixture rend bien ses deux plis", len(f.get("par_pli", [])) == 2,
      f"{len(f.get('par_pli', []))} plis")
    v("⭐⭐⭐⭐ l'angle ABSOLU de chaque pli est plus proche de l'attendu APRÈS conversion",
      all(x["ecart_des_fibres_a_lattendu_deg"] < x["ecart_a_lattendu_deg"]
          for x in f["par_pli"]),
      " · ".join(f"pli {x['pli']} {x['ecart_a_lattendu_deg']}° → "
                 f"{x['ecart_des_fibres_a_lattendu_deg']}°" for x in f["par_pli"]))
    v("⭐⭐⭐⭐ ... et l'ÉCART entre les deux plis, lui, ne bouge pas",
      f.get("lecart_ne_bouge_pas"),
      f"{f.get('ecart_entre_les_plis_deg')}° avant, "
      f"{f.get('ecart_entre_les_plis_apres_conversion_deg')}° après")

    # ---- l'invariance, sur un balayage dense
    inv = un_ecart_est_il_invariant()
    v("⭐⭐⭐ un écart est INVARIANT par le quart de tour, sur un balayage dense",
      inv["lecart_est_invariant"],
      f"{inv['paires']} paires, pire écart {inv['pire_ecart_apres_le_quart_de_tour']}")
    v("⭐⭐⭐ ... et une moyenne en angle double est ÉQUIVARIANTE, elle tourne du même quart",
      inv["la_moyenne_tourne_du_meme_quart"],
      f"{inv['moyenne_avant_deg']}° → {inv['moyenne_apres_deg']}°")

    # ---- la portée, sur les campagnes stockées
    p = ce_quun_quart_de_tour_atteint()
    v("les campagnes stockées sont lues", p["decidable"] and p["segments"] > 0,
      f"{p['segments']} segments, {p['courbes']} courbes")
    v("⭐⭐⭐⭐ la bascule en profondeur est IDENTIQUE avant et après le quart de tour, partout",
      p["la_bascule_ne_bouge_jamais"],
      f"{p['bascules_inchangees']} sur {p['bascules_relues']}")
    v("⚠⚠ et ce qui est atteint est COMPTÉ : les angles absolus publiés",
      p["angles_absolus_publies"] > 0, f"{p['angles_absolus_publies']} angles")
    # ⚠⚠ UNE RECETTE QUI NE LIT PAS LA COHERENCE NE PEUT PAS ECHOUER SUR UNE COURBE PLATE : la
    # sonde le verifie en donnant une courbe sans couche assez texturee.
    v("une courbe sans couche texturée ne rend pas de bascule, elle rend `None`",
      _bascule_dune_courbe([[10.0, 0.0]] * 40) is None)
    v("... et une courbe trop courte non plus", _bascule_dune_courbe([[10.0, 0.9]] * 4) is None)

    # ---- le verdict est JOINT
    jj = juger(j, f, p, inv)
    v("⚠⚠ le verdict est JOINT : le nom est faux ET aucun écart publié ne bouge",
      jj["un_nombre_juste_sous_un_nom_faux"] is True
      and jj["la_formule_rend_la_perpendiculaire"] and jj["aucun_ecart_publie_ne_bouge"])
    faux = juger({**j, "toutes_a_un_quart_de_tour": False}, f, p, inv)
    v("... et il tombe si l'une des deux moitiés tombe",
      faux["un_nombre_juste_sous_un_nom_faux"] is False)

    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {controles} checks)")
    else:
        print(f"ALL PASS (0 failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
