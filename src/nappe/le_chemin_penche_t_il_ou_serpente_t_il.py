#!/usr/bin/env python3
"""Le chemin du marcheur penche-t-il sur le rayon, ou serpente-t-il autour ?

⭐⭐⭐⭐ POURQUOI CE FICHIER EXISTE, ET POURQUOI IL NE COUTE PAS UNE LECTURE DE PLUS. `136` mesure
que le compte de feuilles du marcheur est JUSTE et que ce qui manque au dérouleur est la conversion
feuilles → rayons, qui vaut 1,186 au lieu de un. Ce 1,186 est un CUMUL : le chemin parcouru divisé
par l'étendue radiale traversée, sur cinquante feuilles. Personne n'était allé voir de quoi il est
fait. Or les deux courses de `133` portent, pas par pas, la direction que le marcheur a prise — donc
l'angle entre ce pas et le rayon se lit sans ouvrir le volume une fois de plus.

⭐⭐⭐ ET LA QUESTION A DEUX REPONSES QUE LE CUMUL NE SEPARE PAS. Un chemin plus long qu'une
traversée radiale peut PENCHER — chaque pas oblique du même côté, le marcheur glisse le long de la
feuille en la traversant — ou SERPENTER — des pas obliques de part et d'autre, qui s'annulent. Les
deux rendent exactement le même 1,186, et ils ne veulent pas du tout dire la même chose pour le
graal : un penchant se corrige par une rotation connue, un serpentement est du bruit qui ne se
transporte pas d'un rouleau à l'autre.

⚠⚠ CE QUI SERAIT TAUTOLOGIQUE ET QUI N'EST DONC PAS UN VERDICT ICI. `chemin / étendue` et la
moyenne de `1/cos(θ)` sur les pas sont la MEME quantité écrite deux fois : les publier côte à côte
et constater qu'elles s'accordent ne mesurerait rien. Ce qui se mesure est la FORME de la
distribution de θ, la COHERENCE de la part non radiale, et sa répartition entre l'azimut et l'axe —
trois choses qu'un rapport cumulé ne porte pas.

⭐⭐⭐ LE CONTROLE QUI REND LE NOMBRE LISIBLE EST UNE FIXTURE DONT L'INCLINAISON EST CONNUE. Un
instrument qui rendrait 25° sur n'importe quoi ne dirait rien du rouleau. `VolumeFabriqueEnSpirale`
a une normale inclinée sur le rayon de `atan(pas / 2πρ)` — 0,394° à 4 mm, 0,088° à 18 — et une pile
plane n'en a aucune ; le même instrument doit y lire des dixièmes de degré, et suivre la loi du
rayon. `VolumeFabriqueOndulee(par_feuille=True)` fournit l'autre bout : une normale qui varie d'une
feuille à l'autre, donc un serpentement, à obliquité comparable.

⚠ L'AXE DU ROULEAU EST PRIS COMME LE z DU VOLUME, ET C'EST MESURE PLUTOT QUE SUPPOSE. Les radiaux
que `107` a posés viennent de la courbe de l'ombilic ; s'ils sont perpendiculaires au z du volume,
alors l'axe du rouleau est ce z dans ce repère, et une décomposition cylindrique est licite.
`laxe_du_rouleau_est_il_le_z` le publie, et la batterie fait échouer le contrôle sur un repère où
ce n'est pas vrai.

⚠⚠ POURQUOI CYLINDRIQUE ET NON SPHERIQUE. `135` et `136` mesurent le rayon comme la distance à un
POINT — l'axe d'une bande au sens de `107`. Un pas qui glisse le long de l'axe du rouleau éloigne
alors de ce point sans rien traverser, donc il est compté comme du rayon. En projetant l'axe hors
du rayon, un glissement axial redevient ce qu'il est : de la marche le long de la feuille. L'écart
entre les deux lectures est publié plutôt que tu.

Usage :
    uv run python src/nappe/le_chemin_penche_t_il_ou_serpente_t_il.py --verifier
    uv run python src/nappe/le_chemin_penche_t_il_ou_serpente_t_il.py \\
        --json docs/mesures/le_chemin_penche_t_il_ou_serpente_t_il.json
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

MESURES = RACINE / "docs" / "mesures"
COURSES = (MESURES / "la_course_a_cap.json", MESURES / "la_re_course_large.json")
CESSE = MESURES / "ou_la_matiere_cesse_de_se_lire.json"
NORMALE = MESURES / "la_normale_nest_pas_le_rayon.json"
VOXEL_UM = 2.4
# ⚠ L'axe du rouleau dans le volume fin : le premier indice de (z, y, x). Ce n'est pas une
# convention gratuite — `laxe_du_rouleau_est_il_le_z` la mesure sur les radiaux de `107`.
AXE_DU_ROULEAU = np.array([1.0, 0.0, 0.0])
PAS_MINIMUM = 5
RAYONS_DE_LA_FIXTURE_MM = (4.0, 10.0, 18.0)


def laxe_du_rouleau_est_il_le_z(courses) -> dict:
    """Les radiaux de `107` sont-ils perpendiculaires au z du volume ?

    ⚠⚠ C'EST LA CONDITION DE TOUT CE QUI SUIT, et elle se mesure. Les radiaux viennent de la
    courbe de l'ombilic (`90`), transportée dans le volume fin ; s'ils tombent tous dans le plan
    perpendiculaire au z du volume, l'axe du rouleau EST ce z ici, et le repère cylindrique est
    celui du rouleau. Sinon la décomposition axial / azimutal mesure autre chose que ce qu'elle
    prétend, et elle doit être refusée plutôt que lue.
    """
    angles = []
    for course in courses:
        for ligne in course.get("lignes", []):
            for cel in ligne.get("detail", []):
                r = np.asarray(cel["radial_zyx"], dtype=float)
                r = r / max(float(np.linalg.norm(r)), 1e-12)
                angles.append(abs(float(np.degrees(np.arcsin(np.clip(abs(r @ AXE_DU_ROULEAU),
                                                                     -1.0, 1.0))))))
    if not angles:
        return {"decidable": False, "pourquoi": "aucun radial"}
    a = np.asarray(angles)
    return {"decidable": True, "radiaux": len(a),
            "angle_au_plan_perpendiculaire_a_z_median_deg": round(float(np.median(a)), 3),
            "angle_max_deg": round(float(a.max()), 3),
            # ⚠ Un degré : la résolution avec laquelle la courbe de l'ombilic est posée. Au-delà,
            # « l'axe est le z » cesse d'être une lecture et devient une approximation qu'il
            # faudrait porter dans chaque nombre.
            "laxe_du_rouleau_est_le_z_du_volume": bool(a.max() < 1.0)}


def coherence_dun_axe(net_um: float, parcouru_um: float, voxel_um: float) -> float | None:
    """Le déplacement NET d'un axe divisé par le chemin PARCOURU sur ce même axe.

    ⭐ Un chemin qui dérive toujours du même côté de cet axe rend un ; un chemin qui oblique
    alternativement rend zéro. C'est la même idée que la cohérence tangentielle, posée sur UN axe
    au lieu des deux ensemble — et c'est cette séparation qui rend comparables deux matières dont
    les rôles des axes sont échangés.

    ⚠⚠ REND `None` QUAND L'AXE NE PORTE RIEN, jamais zéro et jamais un. La borne se DERIVE : un axe
    dont le chemin parcouru tient sous ce qu'un voxel exprime n'a pas de direction lisible, et lui
    attribuer une cohérence ferait lire du bruit de quantification comme une dérive.
    """
    if parcouru_um < voxel_um:
        return None
    return round(abs(net_um) / parcouru_um, 3)


def penchant(depart_zyx, axe_zyx, etapes, voxel_um: float = VOXEL_UM) -> dict:
    """Pas par pas : l'angle au rayon, la part axiale, la part azimutale — et la cohérence.

    ⭐⭐⭐⭐ LA COHERENCE EST CE QUI SEPARE UN PENCHANT D'UN SERPENTEMENT, et elle est indépendante
    de l'angle. C'est le déplacement tangentiel NET divisé par le chemin tangentiel PARCOURU :
    un chemin qui penche toujours du même côté rend un ; un chemin qui oblique alternativement de
    part et d'autre rend zéro. Deux marches d'angle médian identique peuvent donc rendre l'une et
    l'autre, ce que la batterie vérifie plutôt que de l'affirmer.

    ⭐⭐⭐⭐ ET LA COHERENCE SE DECOMPOSE PAR AXE, PARCE QU'ELLE MELANGE DEUX CHOSES. La cohérence
    tangentielle est la norme d'une somme de vecteurs : un chemin dont la part axiale ne change
    jamais de signe et dont la part azimutale alterne rend le même nombre qu'un chemin où les rôles
    sont échangés. Or c'est exactement l'axe sur lequel deux matières peuvent différer, et moyenner
    dessus est le péché capital de ce dépôt. Les deux cohérences par axe sont donc rendues À CÔTÉ,
    jamais à la place — chacune est le déplacement NET de cet axe divisé par le chemin PARCOURU sur
    ce même axe, donc bornée entre zéro et un.

    ⚠⚠ LA PART AZIMUTALE SE SOMME EN SCALAIRE, JAMAIS EN VECTEUR. `phi_hat` tourne avec la marche :
    additionner des vecteurs azimutaux replierait la rotation du repère dans la réponse, et un
    chemin qui dérive toujours dans le même sens autour du rouleau paraîtrait alterner.

    ⚠⚠ UN AXE QUI NE PORTE RIEN N'A PAS DE COHERENCE — ni un, ni zéro. Le seuil n'est pas choisi,
    il se DERIVE : l'axe ne porte rien quand son chemin parcouru tombe sous ce qu'UN VOXEL exprime.
    En dessous, `None` est rendu, et l'appelant doit refuser de conclure.

    ⚠ Le repère est cylindrique autour de l'axe du rouleau : `rho` est la distance à la DROITE
    passant par l'axe de la bande et parallèle au z du volume, jamais au point lui-même. Le rayon
    sphérique est rendu à côté, pour que l'écart aux lectures de `135` et `136` soit visible.
    """
    p = np.asarray(depart_zyx, dtype=float).copy()
    a = np.asarray(axe_zyx, dtype=float)
    th, axial, azimutal, rayons, avances, glissements = [], [], [], [], [], []
    tangent_net = np.zeros(3)
    tangent_parcouru = 0.0
    axial_net_um = azimutal_net_um = 0.0
    axial_parcouru_um = azimutal_parcouru_um = 0.0
    for e in etapes:
        d = np.asarray(e["direction"], dtype=float)
        d = d / max(float(np.linalg.norm(d)), 1e-12)
        u = p - a
        u_cyl = u - (u @ AXE_DU_ROULEAU) * AXE_DU_ROULEAU
        rho = float(np.linalg.norm(u_cyl))
        rho_hat = u_cyl / max(rho, 1e-12)
        phi_hat = np.cross(AXE_DU_ROULEAU, rho_hat)
        cr = float(d @ rho_hat)
        th.append(float(np.degrees(np.arccos(np.clip(cr, -1.0, 1.0)))))
        axial.append(float(d @ AXE_DU_ROULEAU))
        azimutal.append(float(d @ phi_hat))
        rayons.append(rho * voxel_um)
        av = float(e["avance_um"])
        avances.append(av)
        # ⚠ Le glissement le long de l'axe pour CE pas, en micrometres. C'est la quantite qu'un
        # derouleur qui travaille tranche par tranche ignore : il transfere entre deux z sans le
        # savoir. Elle se compte sur l'avance reelle, jamais sur le pas nominal.
        glissements.append(abs(float(d @ AXE_DU_ROULEAU)) * av)
        t = d - cr * rho_hat
        tangent_net = tangent_net + t * av
        tangent_parcouru += float(np.linalg.norm(t)) * av
        axial_net_um += axial[-1] * av
        azimutal_net_um += azimutal[-1] * av
        axial_parcouru_um += abs(axial[-1]) * av
        azimutal_parcouru_um += abs(azimutal[-1]) * av
        p = p + d * (av / voxel_um)
    if not th:
        return {"decidable": False, "pourquoi": "aucun pas"}
    u = p - a
    u_cyl = u - (u @ AXE_DU_ROULEAU) * AXE_DU_ROULEAU
    th = np.asarray(th)
    avances = np.asarray(avances)
    return {"decidable": True, "pas": len(th), "angles_deg": [round(x, 2) for x in th],
            "angle_median_deg": round(float(np.median(th)), 2),
            "angle_q1_deg": round(float(np.percentile(th, 25)), 2),
            "angle_q3_deg": round(float(np.percentile(th, 75)), 2),
            "pas_au_dela_de_90_deg": int((th > 90.0).sum()),
            "axial_median": round(float(np.median(axial)), 3),
            "glissement_axial_median_um": round(float(np.median(glissements)), 1),
            "axial_absolu_median": round(float(np.median(np.abs(axial))), 3),
            "azimutal_absolu_median": round(float(np.median(np.abs(azimutal))), 3),
            "coherence_tangentielle": round(
                float(np.linalg.norm(tangent_net) / max(tangent_parcouru, 1e-12)), 3),
            "coherence_axiale": coherence_dun_axe(axial_net_um, axial_parcouru_um, voxel_um),
            "coherence_azimutale": coherence_dun_axe(azimutal_net_um, azimutal_parcouru_um,
                                                     voxel_um),
            "chemin_axial_um": round(axial_parcouru_um, 1),
            "chemin_azimutal_um": round(azimutal_parcouru_um, 1),
            "chemin_um": round(float(avances.sum()), 1),
            "rayon_depart_um": round(rayons[0], 1),
            "etendue_cylindrique_um": round(float(np.linalg.norm(u_cyl)) * voxel_um - rayons[0], 1),
            "etendue_spherique_um": round(float(np.linalg.norm(u)) * voxel_um
                                          - float(np.linalg.norm(np.asarray(depart_zyx, dtype=float)
                                                                 - a)) * voxel_um, 1),
            "position_fin_zyx": [float(x) for x in p]}


def marches_arrivees(course: dict, sortis: set[int]) -> list[tuple[dict, dict, int]]:
    """Les marches que `135` a déclarées SORTIES DU ROULEAU, avec leur bande.

    ⚠⚠ La restriction est celle de `136`, et c'est elle qui rend la question posable : une marche
    arrêtée au plafond est revenue sur elle-même, donc son « angle au rayon » mélange une traversée
    et un demi-tour. Ce que le graal demande est l'angle d'une traversée.
    """
    out, i = [], 0
    for ligne in course.get("lignes", []):
        for cel in ligne.get("detail", []):
            m = i
            i += 1
            if m not in sortis:
                continue
            out.append((ligne, cel, m))
    return out


def la_forme_du_penchant(rangs: list[dict]) -> dict:
    """La distribution de l'angle, sa cohérence, et de quel côté la part non radiale tombe.

    ⭐⭐⭐ LE SIGNE DE LA PART AXIALE EST UN CONTROLE, PAS UNE DESCRIPTION. Si le glissement le long
    de l'axe venait de l'instrument — une anisotropie du volume, un biais du chercheur de direction
    — il aurait le MEME signe partout. S'il vient de la matière, chaque bande choisit son côté. Le
    test des signes le tranche, et il peut échouer.

    ⚠ La part des pas au-delà de 90° est publiée à part : ce sont les pas qui REVIENNENT vers
    l'axe. Sur une traversée ils devraient être nuls, et leur compte dit ce que le cap fait.
    """
    from scipy import stats  # noqa: PLC0415

    if len(rangs) < 3:
        return {"decidable": False, "pourquoi": f"{len(rangs)} marche(s), il en faut trois"}
    tous = np.concatenate([np.asarray(r["angles_deg"]) for r in rangs])
    coh = np.asarray([r["coherence_tangentielle"] for r in rangs])
    ax = np.asarray([r["axial_median"] for r in rangs])
    positifs = int((ax > 0).sum())
    # ⚠ Ce que coute la lecture SPHERIQUE de `135` et `136` : un glissement le long de l'axe
    # eloigne du point sans rien traverser, donc il gonfle l'etendue radiale. Le rapport est
    # publie plutot que tu, et il va dans le sens qui RENFORCE `136` — une etendue plus petite
    # rend un espacement implique par le rayon plus petit encore.
    cyl = np.asarray([r["etendue_cylindrique_um"] for r in rangs], dtype=float)
    sph = np.asarray([r["etendue_spherique_um"] for r in rangs], dtype=float)
    bon = cyl > 0.0
    rapport = sph[bon] / cyl[bon]
    return {"decidable": True, "marches": len(rangs), "pas": int(tous.size),
            "angle_median_deg": round(float(np.median(tous)), 2),
            "angle_q1_deg": round(float(np.percentile(tous, 25)), 2),
            "angle_q3_deg": round(float(np.percentile(tous, 75)), 2),
            "angle_p90_deg": round(float(np.percentile(tous, 90)), 2),
            "pas_au_dela_de_90_deg": int((tous > 90.0).sum()),
            "part_des_pas_au_dela_de_90": round(float((tous > 90.0).mean()), 4),
            "coherence_mediane": round(float(np.median(coh)), 3),
            "coherence_min": round(float(coh.min()), 3),
            "axial_absolu_median": round(float(np.median(
                [r["axial_absolu_median"] for r in rangs])), 3),
            "glissement_axial_median_um": round(float(np.median(
                [r["glissement_axial_median_um"] for r in rangs])), 1),
            "azimutal_absolu_median": round(float(np.median(
                [r["azimutal_absolu_median"] for r in rangs])), 3),
            "etendue_cylindrique_mediane_um": round(float(np.median(cyl)), 1),
            "etendue_spherique_mediane_um": round(float(np.median(sph)), 1),
            "le_rayon_spherique_surestime_letendue_de": (round(float(np.median(rapport)), 4)
                                                         if rapport.size else None),
            "et_au_plus_de": (round(float(rapport.max()), 4) if rapport.size else None),
            "bandes_qui_glissent_vers_les_z_croissants": positifs,
            "p_du_signe_axial": round(float(stats.binomtest(positifs, len(ax)).pvalue), 4),
            "le_glissement_axial_a_un_sens_prefere": bool(
                stats.binomtest(positifs, len(ax)).pvalue < 0.05),
            # ⭐⭐ Le verdict qui n'est PAS tautologique : la part non radiale est-elle un penchant
            # (cohérente) ou un serpentement (incohérente) ? Le partage est à un demi, c'est-à-dire
            # au point où le déplacement net vaut la moitié du chemin tangentiel.
            "le_chemin_penche": bool(float(np.median(coh)) > 0.5),
            "le_chemin_serpente": bool(float(np.median(coh)) <= 0.5)}


def le_penchant_saccorde_t_il_au_maillage(rangs: list[dict], maillage: dict) -> dict:
    """Le penchant du marcheur vaut-il l'obliquité que les humains ont tracée ?

    ⭐⭐⭐⭐ DEUX INSTRUMENTS QUI NE PARTAGENT AUCUNE HYPOTHESE. L'un lit l'intensité du volume et
    rend une direction de pas ; l'autre est la normale d'une surface segmentée à la main, mesurée
    par `la_normale_nest_pas_le_rayon` bande par bande. S'ils donnent le même angle au rayon,
    l'obliquité est dans la matière et non dans le marcheur.

    ⚠⚠ DEUX VERDICTS SEPARES, ET ILS NE DISENT PAS LA MEME CHOSE. Le NIVEAU (test apparié) dit si
    les deux mesurent la même quantité en gros ; la PLACE (rangs) dit s'ils s'accordent bande par
    bande. Les confondre ferait passer un accord de niveau pour un accord local — le piège que
    `136` a payé avec un rho de 0,8952 qui ne prouvait pas la cause qu'on lui prêtait.

    ⚠ La portée du test des rangs est faible ici et c'est dit : les angles du maillage tiennent
    dans neuf degrés quand ceux du marcheur en couvrent trente. Un rang comparé sur une étendue
    aussi inégale se mène surtout par le bruit.
    """
    from scipy import stats  # noqa: PLC0415

    paires = [(r["angle_median_deg"], maillage[r["bande"]])
              for r in rangs if r["bande"] in maillage]
    if len(paires) < 3:
        return {"decidable": False, "pourquoi": f"{len(paires)} bande(s) appariée(s)"}
    m = np.asarray([x[0] for x in paires], dtype=float)
    g = np.asarray([x[1] for x in paires], dtype=float)
    d = m - g
    rho, p_rho = stats.spearmanr(m, g)
    p_app = float(stats.wilcoxon(d).pvalue) if np.any(d) else None
    return {"decidable": True, "paires": len(paires),
            "penchant_median_deg": round(float(np.median(m)), 2),
            "maillage_median_deg": round(float(np.median(g)), 2),
            "etendue_du_maillage_deg": [round(float(g.min()), 2), round(float(g.max()), 2)],
            "etendue_du_penchant_deg": [round(float(m.min()), 2), round(float(m.max()), 2)],
            "ecart_median_deg": round(float(np.median(d)), 2),
            "p_apparie": None if p_app is None else round(p_app, 5),
            "rho_de_spearman": round(float(rho), 4), "p_du_rang": round(float(p_rho), 5),
            # ⚠ Un ecart strictement nul rend le Wilcoxon indefini — il n'a aucun rang a
            # ordonner. C'est l'accord le plus FORT possible, pas un indecidable, et le lire
            # comme un desaccord ferait echouer le seul cas ou les deux instruments coincident.
            "le_niveau_est_indiscernable": bool(p_app is None or p_app >= 0.05),
            "les_rangs_saccordent": bool(p_rho < 0.05 and rho > 0.0)}


def le_cap_change_t_il_le_penchant(avec: dict, sans: dict) -> dict:
    """Le cap réduit-il le penchant, et les retours vers l'axe ?

    ⚠ Deux verdicts séparés, parce que ce sont deux effets : moins pencher et moins revenir en
    arrière ne sont pas la même chose, et `133` a mesuré que le cap redresse la marche sans dire
    laquelle des deux il faisait.
    """
    if not (avec.get("decidable") and sans.get("decidable")):
        return {"decidable": False, "pourquoi": "une des deux courses n'est pas décidable"}
    return {"decidable": True,
            "angle_median_avec_cap_deg": avec["angle_median_deg"],
            "angle_median_sans_cap_deg": sans["angle_median_deg"],
            "coherence_avec_cap": avec["coherence_mediane"],
            "coherence_sans_cap": sans["coherence_mediane"],
            "part_au_dela_de_90_avec_cap": avec["part_des_pas_au_dela_de_90"],
            "part_au_dela_de_90_sans_cap": sans["part_des_pas_au_dela_de_90"],
            "le_cap_reduit_le_penchant": bool(avec["angle_median_deg"] < sans["angle_median_deg"]),
            "le_cap_supprime_les_retours": bool(avec["pas_au_dela_de_90_deg"] == 0
                                                and sans["pas_au_dela_de_90_deg"] > 0)}


def _barres():
    """Les barres calibrées dont le marcheur a besoin — les mêmes que la course."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    return (longueurs, mu, sd, barre, nul_du_tenseur(demi=20)["accord_des_moities_p1_deg"],
            max(x["p99"] for x in C.accord_du_bruit_pur().values()), C)


def _marcher_et_pencher(vol, depart, direction0, axe, barres, pas_max: int, cap: float,
                        demi: int = 20) -> dict:
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415

    longueurs, mu, sd, barre, bm, bi, C = barres
    etapes = marcher(vol, depart, direction0, longueurs, mu, sd, barre, bm, bi, C.VOXEL_FIN_UM,
                     pas_max=pas_max, demi=demi, fils=1, memoire_du_cap=cap)
    pas = [e for e in etapes if "avance_um" in e]
    return penchant(depart, axe, pas, C.VOXEL_FIN_UM)


def _inclinaison_de_la_spirale(rayon_um: float, pas_um: float) -> float:
    """L'angle entre la normale d'une spirale d'Archimede et le rayon, a ce rayon.

    ⚠ Elle DECROIT en 1/rho : une marche qui traverse huit millimetres ne rencontre donc pas UNE
    inclinaison mais un intervalle, et comparer sa lecture a la seule inclinaison du DEPART serait
    lui reprocher d'avoir avance.
    """
    return float(np.degrees(np.arctan(pas_um / (2.0 * np.pi * max(rayon_um, 1e-9)))))


def la_fixture_tranche_t_elle(pas_max: int = 40, rayons_mm=RAYONS_DE_LA_FIXTURE_MM,
                              caps=(0.0, 0.75), amplitude_um: float = 47.469,
                              longueur_donde_um: float = 393.6) -> dict:
    """Le même instrument, sur des matières dont l'inclinaison est CONNUE.

    ⭐⭐⭐⭐ SANS CE BLOC, « LE CHEMIN PENCHE DE VINGT-CINQ DEGRES » NE DIT RIEN DU ROULEAU. Un
    instrument qui rendrait le même angle sur n'importe quelle matière mesurerait le marcheur.
    La spirale du dépôt a une normale inclinée sur le rayon d'un angle analytique qui DECROIT avec
    le rayon ; l'instrument doit y lire des dixièmes de degré et suivre cette loi.

    ⭐⭐⭐ ET L'AUTRE BOUT EST LE SERPENTEMENT. `VolumeFabriqueOndulee(par_feuille=True)`, calibrée
    par `134` sur le désaccord des moitiés réel, a une normale qui change d'une feuille à l'autre :
    elle doit rendre un angle franc et une cohérence BASSE, là où le rouleau rend un angle franc et
    une cohérence HAUTE. C'est ce couple qui rend la distinction mesurable plutôt que verbale.

    ⚠ Le départ de la spirale est recalé sur une phase ENTIERE. Une cellule qui tombe entre deux
    feuilles ne correspond à aucune polarité du gabarit, et l'instrument mesurerait alors sa propre
    erreur de mise en place — le défaut que la fixture de `100` a payé.
    """
    from combien_de_pas_la_matiere_porte import (VolumeFabriqueEnSpirale,  # noqa: PLC0415
                                                 VolumeFabriqueOndulee)

    barres = _barres()
    C = barres[-1]
    # ⚠ Le champ est élargi et le centre déporté : à dix-huit millimètres la feuille de départ
    # tombe hors d'un cube de quatre mille voxels, et une marche qui sort du champ au premier pas
    # ne mesure rien. Le volume est analytique, donc l'élargir ne coûte pas de mémoire.
    centre = (6000.0, 6000.0)
    forme = (4000, 16000, 16000)
    spirales = []
    for r_mm in rayons_mm:
        r_vx = r_mm * 1000.0 / C.VOXEL_FIN_UM
        # ⚠ Sur l'axe +y l'angle vaut π/2, donc la phase y vaut -1/4 : le rayon de référence est
        # décalé d'un quart de pas pour que le départ tombe sur une feuille.
        vol = VolumeFabriqueEnSpirale(C.PAS_UM, r0_um=r_mm * 1000.0 - 0.25 * C.PAS_UM,
                                      centre_yx_vx=centre, forme=forme)
        depart = np.array([2000.0, centre[0] + r_vx, centre[1]])
        radial = np.array([0.0, 1.0, 0.0])
        axe = depart - radial * r_vx
        normale = vol.normale_locale(depart).reshape(3)
        analytique = float(np.degrees(np.arccos(np.clip(abs(normale @ radial), -1.0, 1.0))))
        ligne = {"rayon_mm": r_mm, "phase_du_depart": round(float(vol.phase(depart.reshape(1, 3))[0]), 6),
                 "inclinaison_analytique_deg": round(analytique, 3), "par_cap": []}
        for cap in caps:
            p = _marcher_et_pencher(vol, depart, radial, axe, barres, pas_max, cap)
            # ⭐⭐ L'inclinaison AU BOUT de la marche, calculee sur le rayon reellement atteint :
            # c'est elle qui, avec celle du depart, borne ce que l'instrument DOIT lire.
            fin = (_inclinaison_de_la_spirale(p["rayon_depart_um"] + p["etendue_cylindrique_um"],
                                              C.PAS_UM) if p.get("decidable") else None)
            ligne["par_cap"].append({"memoire_du_cap": cap, "pas": p.get("pas", 0),
                                     "angle_median_deg": p.get("angle_median_deg"),
                                     "inclinaison_analytique_a_larrivee_deg": (
                                         None if fin is None else round(fin, 3)),
                                     "coherence_tangentielle": p.get("coherence_tangentielle")})
        spirales.append(ligne)
    piles = []
    for amp in (0.0, amplitude_um):
        vol = VolumeFabriqueOndulee(C.PAS_UM, amplitude_um=amp,
                                    longueur_donde_um=longueur_donde_um, par_feuille=True)
        depart = np.array([2000.0, 2000.0, 2000.0])
        normale = vol.normale_locale(depart).reshape(3)
        # ⚠ Une pile plane n'a pas d'axe : l'axe est CONSTRUIT comme `107` le fait pour une bande,
        # à un rayon de dix millimètres le long de la normale. Une marche qui suit la normale part
        # donc radialement de ce point, et tout ce qui s'en écarte est mesuré comme tel.
        axe = depart - normale * (10000.0 / C.VOXEL_FIN_UM)
        ligne = {"amplitude_um": amp, "longueur_donde_um": longueur_donde_um, "par_cap": []}
        for cap in caps:
            p = _marcher_et_pencher(vol, depart, normale, axe, barres, pas_max, cap)
            ligne["par_cap"].append({"memoire_du_cap": cap, "pas": p.get("pas", 0),
                                     "angle_median_deg": p.get("angle_median_deg"),
                                     "coherence_tangentielle": p.get("coherence_tangentielle")})
        piles.append(ligne)
    plate = next((x for x in piles if x["amplitude_um"] == 0.0), None)
    froissee = next((x for x in piles if x["amplitude_um"] > 0.0), None)
    out = {"spirales": spirales, "piles": piles, "pas_max": pas_max}
    # ⭐⭐ LES VERDICTS DU CONTROLE, CALCULES. Ils doivent pouvoir échouer : une pile plane qui
    # rendrait un angle franc, ou une spirale qui ne suivrait pas sa propre loi, diraient que
    # l'instrument fabrique le penchant qu'il mesure.
    angles_spirale = [min(c["angle_median_deg"] for c in s["par_cap"] if c["angle_median_deg"] is not None)
                      for s in spirales if any(c["angle_median_deg"] is not None for c in s["par_cap"])]
    out["la_spirale_reste_sous_un_degre"] = bool(angles_spirale and max(angles_spirale) < 1.0)
    out["la_spirale_suit_la_loi_du_rayon"] = bool(
        len(angles_spirale) == len(spirales) and len(angles_spirale) >= 2
        and all(angles_spirale[i] >= angles_spirale[i + 1] for i in range(len(angles_spirale) - 1)))
    # ⭐⭐⭐ LA BORNE QUI MORD, ET ELLE EST DERIVEE PLUTOT QUE CHOISIE. La marche s'eloigne de
    # l'axe et l'inclinaison de la spirale DECROIT en 1/rho, donc l'angle lu ne peut pas depasser
    # celui du DEPART — et il doit rester positif. Lire au-dessus du depart voudrait dire que
    # l'instrument ajoute de l'obliquite a une matiere qui en a moins a mesure qu'on avance.
    # ⚠⚠ CE QUE CETTE BORNE N'EST PAS : « la lecture tombe dans l'intervalle [arrivee ; depart] ».
    # Je l'avais d'abord ecrite ainsi, et la mesure l'a refusee — a huit pas la lecture tombe SOUS
    # l'intervalle (0,25 pour [0,293 ; 0,394]), a quarante elle y tombe parce que l'intervalle est
    # devenu large. Un controle satisfait par la LARGEUR de sa borne ne controle rien.
    sous = []
    for sp in spirales:
        for c2 in sp["par_cap"]:
            a2 = c2.get("angle_median_deg")
            if a2 is None:
                continue
            sous.append(0.0 <= a2 <= sp["inclinaison_analytique_deg"])
    out["marches_de_spirale"] = len(sous)
    out["marches_sous_linclinaison_du_depart"] = int(sum(sous))
    out["la_spirale_nest_jamais_lue_au_dessus_de_son_depart"] = bool(sous and all(sous))
    if plate and froissee:
        a_plate = [c["angle_median_deg"] for c in plate["par_cap"] if c["angle_median_deg"] is not None]
        a_fr = [c["angle_median_deg"] for c in froissee["par_cap"]
                if c["angle_median_deg"] is not None]
        coh_fr = [c["coherence_tangentielle"] for c in froissee["par_cap"]
                  if c["coherence_tangentielle"] is not None]
        out["la_pile_plane_ne_penche_pas"] = bool(a_plate and max(a_plate) < 1.0)
        out["penchant_de_la_pile_froissee_deg"] = (round(float(max(a_fr)), 2) if a_fr else None)
        out["coherence_de_la_pile_froissee"] = (round(float(max(coh_fr)), 3) if coh_fr else None)
        # ⚠⚠ CE QUE LA FIXTURE NE TRANCHE PAS, ET IL FAUT LE DIRE PLUTOT QUE LE LISSER. Sous un
        # cap, une pile FROISSEE rend une coherence tangentielle du meme ordre que le rouleau :
        # une ride est plus longue qu'un pas, donc le cap la lisse en un penchant apparent. La
        # coherence dit donc qu'un chemin penche a l'echelle d'une marche ; elle ne dit PAS si
        # c'est parce que les feuilles sont inclinees ou parce qu'elles sont froissees. C'est
        # exactement la fixture que `R4-P28` demande et qui n'existe pas : une normale a angle
        # FIXE du rayon.
        out["la_coherence_separe_le_froisse_du_penche"] = bool(
            coh_fr and max(coh_fr) < 0.75)
    return out


def mesurer(courses=COURSES, cesse: Path = CESSE, normale: Path = NORMALE,
            avec_fixture: bool = True) -> dict:
    """Les deux courses de `133`, marche arrivée par marche arrivée, plus le contrôle sur fixture."""
    if not cesse.is_file():
        return {"message": f"absent : {cesse} — lancer `ou_la_matiere_cesse_de_se_lire`"}
    ce = json.loads(cesse.read_text(encoding="utf-8"))
    sortis = {c["source"]: {a["marche"] for a in c.get("arrets", [])
                            if a.get("verdict", {}).get("sorti_du_rouleau")}
              for c in ce.get("par_course", [])}
    maillage = {}
    if normale.is_file():
        n = json.loads(normale.read_text(encoding="utf-8"))
        maillage = {(int(x["de"]), int(x["a"])): float(x["angle_deg"])
                    for x in n.get("le_pas_dans_les_deux_directions", {}).get("lignes", [])}
    chargees = []
    for cp in courses:
        cp = Path(cp)
        if cp.is_file():
            chargees.append((cp, json.loads(cp.read_text(encoding="utf-8"))))
    if not chargees:
        return {"message": "aucune course trouvée"}
    out = {"sources": [cp.name for cp, _ in chargees], "voxel_um": VOXEL_UM,
           "bandes_du_maillage": len(maillage),
           "laxe": laxe_du_rouleau_est_il_le_z([c for _, c in chargees]), "par_course": []}
    for cp, course in chargees:
        rangs = []
        for ligne, cel, m in marches_arrivees(course, sortis.get(cp.name, set())):
            etapes = [e for e in cel.get("etapes", []) if "avance_um" in e]
            if len(etapes) < PAS_MINIMUM:
                continue
            dep = np.asarray(cel["depart_zyx"], dtype=float)
            rad = np.asarray(cel["radial_zyx"], dtype=float)
            axe = dep - rad * (float(ligne["rayon_mm"]) * 1000.0 / VOXEL_UM)
            p = penchant(dep, axe, etapes, VOXEL_UM)
            if not p.get("decidable"):
                continue
            p.pop("position_fin_zyx", None)
            rangs.append({**p, "marche": m, "bande": (int(ligne["de"]), int(ligne["a"])),
                          "rayon_mm": float(ligne["rayon_mm"])})
        forme = la_forme_du_penchant(rangs)
        out["par_course"].append({
            "source": cp.name, "memoire_du_cap": course.get("memoire_du_cap", 0.0),
            "marches_arrivees": len(rangs),
            # ⚠⚠ LES ANGLES PAS A PAS SONT PUBLIES, et la premiere version les dépouillait
            # « pour alleger ». C'est la mesure elle-meme : sans eux le JSON ne porte que des
            # medianes, donc la distribution — le seul objet de ce fichier — n'est plus
            # re-derivable, et la figure qui la dessine n'a rien a dessiner. Mille angles font
            # quinze kilo-octets.
            "marches": rangs,
            "la_forme_du_penchant": forme,
            "le_penchant_saccorde_t_il_au_maillage":
                le_penchant_saccorde_t_il_au_maillage(rangs, maillage)})
    if len(out["par_course"]) == 2:
        a = next((c for c in out["par_course"] if c["memoire_du_cap"]), None)
        s = next((c for c in out["par_course"] if not c["memoire_du_cap"]), None)
        if a and s:
            out["le_cap_change_t_il_le_penchant"] = le_cap_change_t_il_le_penchant(
                a["la_forme_du_penchant"], s["la_forme_du_penchant"])
    if avec_fixture:
        out["la_fixture_tranche_t_elle"] = la_fixture_tranche_t_elle()
    return out


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    a = r["laxe"]
    print(f"axe du rouleau : {a['radiaux']} radiaux de `107` à "
          f"{a['angle_au_plan_perpendiculaire_a_z_median_deg']}° du plan perpendiculaire à z "
          f"(max {a['angle_max_deg']}°) → "
          + ("★ l'axe du rouleau est le z du volume" if a["laxe_du_rouleau_est_le_z_du_volume"]
             else "⚠ ce n'est PAS le z : la décomposition cylindrique est refusée"))
    for c in r["par_course"]:
        f, m = c["la_forme_du_penchant"], c["le_penchant_saccorde_t_il_au_maillage"]
        print(f"\n{c['source']} (λ = {c['memoire_du_cap']}) · {c['marches_arrivees']} marches arrivées")
        for x in c["marches"]:
            print(f"   r0 {x['rayon_mm']:>5.2f} mm · {x['pas']:>3} pas · penchant "
                  f"{x['angle_median_deg']:>6.2f}° [{x['angle_q1_deg']:>5.2f} ; {x['angle_q3_deg']:>6.2f}] · "
                  f"cohérence {x['coherence_tangentielle']:.3f} · axial {x['axial_median']:+.3f} · "
                  f"retours {x['pas_au_dela_de_90_deg']}")
        if not f.get("decidable"):
            print(f"   ⚠ {f.get('pourquoi')}")
            continue
        print(f"   ★ penchant {f['angle_median_deg']}° [{f['angle_q1_deg']} ; {f['angle_q3_deg']}], "
              f"p90 {f['angle_p90_deg']}° sur {f['pas']} pas · "
              f"retours vers l'axe {f['pas_au_dela_de_90_deg']} ({f['part_des_pas_au_dela_de_90']})")
        print(f"   ★ cohérence {f['coherence_mediane']} (min {f['coherence_min']}) → "
              + ("LE CHEMIN PENCHE" if f["le_chemin_penche"] else "LE CHEMIN SERPENTE"))
        print(f"   ★ étendue radiale : {f['etendue_cylindrique_mediane_um']} µm en cylindrique "
              f"contre {f['etendue_spherique_mediane_um']} en sphérique — la lecture de `135` et "
              f"`136` surestime de {f['le_rayon_spherique_surestime_letendue_de']} "
              f"(au plus {f['et_au_plus_de']})")
        print(f"   ★ part axiale {f['axial_absolu_median']} contre azimutale "
              f"{f['azimutal_absolu_median']} · glissement axial "
              f"{f['glissement_axial_median_um']} µm par pas · sens préféré : "
              f"{f['bandes_qui_glissent_vers_les_z_croissants']}/{f['marches']} vers les z "
              f"croissants, p {f['p_du_signe_axial']}")
        if m.get("decidable"):
            print(f"   ★ contre le maillage humain : {m['penchant_median_deg']}° contre "
                  f"{m['maillage_median_deg']}°, écart {m['ecart_median_deg']:+}°, "
                  f"p apparié {m['p_apparie']} · rangs rho {m['rho_de_spearman']:+} p {m['p_du_rang']}")
    cc = r.get("le_cap_change_t_il_le_penchant")
    if cc and cc.get("decidable"):
        print(f"\n★★ le cap : penchant {cc['angle_median_sans_cap_deg']}° → "
              f"{cc['angle_median_avec_cap_deg']}°, cohérence {cc['coherence_sans_cap']} → "
              f"{cc['coherence_avec_cap']}, retours {cc['part_au_dela_de_90_sans_cap']} → "
              f"{cc['part_au_dela_de_90_avec_cap']}")
    fx = r.get("la_fixture_tranche_t_elle")
    if fx:
        print("\nfixture — le même instrument sur une matière connue :")
        for s in fx["spirales"]:
            lus = " / ".join(f"{c['angle_median_deg']}" for c in s["par_cap"])
            fins = " / ".join(str(c.get("inclinaison_analytique_a_larrivee_deg"))
                              for c in s["par_cap"])
            print(f"   spirale r {s['rayon_mm']:>4.1f} mm · inclinaison analytique "
                  f"{s['inclinaison_analytique_deg']}° au départ, {fins}° à l'arrivée · lu {lus}°")
        for p in fx["piles"]:
            lus = " / ".join(f"{c['angle_median_deg']}° coh {c['coherence_tangentielle']}"
                             for c in p["par_cap"])
            print(f"   pile amplitude {p['amplitude_um']:>7.3f} µm · {lus}")
        print(f"   ★ spirale sous un degré : {fx.get('la_spirale_reste_sous_un_degre')} · "
              f"suit la loi du rayon : {fx.get('la_spirale_suit_la_loi_du_rayon')} · "
              f"jamais lue au-dessus de son départ : "
              f"{fx.get('la_spirale_nest_jamais_lue_au_dessus_de_son_depart')} "
              f"({fx.get('marches_sous_linclinaison_du_depart')}"
              f"/{fx.get('marches_de_spirale')}) · "
              f"pile plane sans penchant : {fx.get('la_pile_plane_ne_penche_pas')}")
        print(f"   ⚠⚠ la cohérence sépare le froissé du penché : "
              f"{fx.get('la_coherence_separe_le_froisse_du_penche')} — une pile froissée rend "
              f"{fx.get('penchant_de_la_pile_froissee_deg')}° à cohérence "
              f"{fx.get('coherence_de_la_pile_froissee')}")


def _course_fabriquee(directions, avance_um: float = 173.0, r0_mm: float = 10.0,
                      radial=(0.0, 0.0, 1.0)) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """Une marche dont on CONNAIT l'angle au rayon — le départ, l'axe, et les pas."""
    dep = np.array([2000.0, 2000.0, 2000.0])
    rad = np.asarray(radial, dtype=float)
    axe = dep - rad * (r0_mm * 1000.0 / VOXEL_UM)
    return dep, axe, [{"direction": list(map(float, d)), "avance_um": avance_um} for d in directions]


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    z = AXE_DU_ROULEAU
    rad = np.array([0.0, 0.0, 1.0])
    phi = np.cross(z, rad)

    # ---- le repère lui-même
    dep, axe, pas = _course_fabriquee([rad] * 8)
    p = penchant(dep, axe, pas)
    v("une marche purement radiale penche de zéro", p["decidable"] and p["angle_median_deg"] == 0.0,
      f"{p.get('angle_median_deg')}°")
    v("... et son étendue cylindrique vaut le chemin",
      abs(p["etendue_cylindrique_um"] - p["chemin_um"]) < 1.0,
      f"{p['etendue_cylindrique_um']} pour {p['chemin_um']}")
    # ⚠⚠ LE PREMIER PAS EST EXACT, LA MEDIANE NE PEUT PAS L'ETRE, et confondre les deux ferait
    # passer une propriete du repere pour une erreur. Un marcheur qui oblique fait TOURNER le
    # rayon sous lui : au bout de huit pas a 50°, l'arc parcouru vaut plusieurs degres, donc
    # l'angle au rayon COURANT a baisse d'autant. La borne de la mediane est donc derivee de
    # l'arc, jamais choisie.
    for th in (10.0, 30.0, 50.0):
        d = np.cos(np.radians(th)) * rad + np.sin(np.radians(th)) * phi
        _, _, pa = _course_fabriquee([d] * 8)
        q = penchant(dep, axe, pa)
        v(f"un penchant azimutal de {th:.0f}° est lu EXACTEMENT au premier pas",
          abs(q["angles_deg"][0] - th) < 1e-6, f"{q['angles_deg'][0]}°")
        arc = np.degrees(8 * 173.0 * np.sin(np.radians(th)) / 10000.0)
        v(f"... et sa mediane a baisse de moins que l'arc parcouru ({arc:.1f}°)",
          0.0 <= th - q["angle_median_deg"] <= arc,
          f"{q['angle_median_deg']}° pour {th}°")
    # ⚠⚠ LA SONDE DU REPERE : un pas purement AXIAL ne traverse rien, donc il doit être lu à 90°
    # du rayon. Avec un rayon sphérique — la lecture de `135` et `136` — il ne l'est pas, et un
    # glissement le long du rouleau passerait pour de la traversée.
    _, _, pax = _course_fabriquee([z] * 8)
    q = penchant(dep, axe, pax)
    v("sonde du repère : un pas purement axial est lu à 90° du rayon",
      abs(q["angle_median_deg"] - 90.0) < 1e-6, f"{q['angle_median_deg']}°")
    v("... et son étendue cylindrique est nulle, quand la sphérique ne l'est pas",
      abs(q["etendue_cylindrique_um"]) < 1.0 and q["etendue_spherique_um"] > 10.0,
      f"cyl {q['etendue_cylindrique_um']} µm, sph {q['etendue_spherique_um']} µm")

    # ---- penchant contre serpentement, à obliquité IDENTIQUE
    th = 30.0
    d_plus = np.cos(np.radians(th)) * rad + np.sin(np.radians(th)) * phi
    d_moins = np.cos(np.radians(th)) * rad - np.sin(np.radians(th)) * phi
    _, _, penche = _course_fabriquee([d_plus] * 12)
    _, _, serpente = _course_fabriquee([d_plus if i % 2 else d_moins for i in range(12)])
    a, b = penchant(dep, axe, penche), penchant(dep, axe, serpente)
    # ⚠ Les deux partent du MEME angle au premier pas ; seule celle qui penche fait tourner le
    # rayon, donc sa mediane baisse un peu. Ce qui est compare ici est la coherence, pas l'angle.
    v("⚠⚠ deux marches de MEME angle initial se distinguent par la cohérence",
      abs(a["angles_deg"][0] - b["angles_deg"][0]) < 1e-6
      and a["coherence_tangentielle"] > 0.9 and b["coherence_tangentielle"] < 0.3,
      f"{a['angles_deg'][0]}° coh {a['coherence_tangentielle']} contre "
      f"{b['angles_deg'][0]}° coh {b['coherence_tangentielle']}")
    # ⚠ Sonde : sans la pondération par l'avance, une marche dont les longs pas penchent d'un côté
    # et les courts de l'autre paraîtrait serpenter. Le déplacement, lui, est porté par les longs.
    longs = [{"direction": list(map(float, d_plus)), "avance_um": 300.0} for _ in range(6)]
    courts = [{"direction": list(map(float, d_moins)), "avance_um": 30.0} for _ in range(6)]
    c = penchant(dep, axe, longs + courts)
    v("sonde : la cohérence est pondérée par l'avance, pas comptée par pas",
      c["coherence_tangentielle"] > 0.7, f"coh {c['coherence_tangentielle']}")

    # ---- ⭐⭐⭐⭐ la cohérence tangentielle MOYENNE sur l'axe où la différence vit
    # Deux marches MIROIR : l'une garde son signe axial et alterne en azimut, l'autre l'inverse.
    # Les deux parts valent sin(30°)/sqrt(2) chacune, donc la geometrie est symetrique et la
    # coherence TANGENTIELLE doit rendre le meme nombre. Si les deux coherences PAR AXE ne se
    # renversaient pas, la decomposition n'apporterait rien.
    demi = np.sin(np.radians(th)) / np.sqrt(2.0)
    base = np.cos(np.radians(th)) * rad
    ax_tient = [base + demi * z + (1 if i % 2 else -1) * demi * phi for i in range(12)]
    az_tient = [base + (1 if i % 2 else -1) * demi * z + demi * phi for i in range(12)]
    _, _, ea = _course_fabriquee(ax_tient)
    _, _, eb = _course_fabriquee(az_tient)
    ca, cb = penchant(dep, axe, ea), penchant(dep, axe, eb)
    # ⚠⚠ LE MIROIR N'EST PAS EXACT, ET LA SONDE L'A DIT : l'axe qui alterne est le z FIXE dans une
    # marche et le `phi_hat` QUI TOURNE dans l'autre, donc les deux geometries ne sont pas la meme
    # a une rotation pres. Ce qui se compare est donc l'ECART que chaque grandeur met entre les
    # deux marches, jamais leur egalite — et aucun seuil n'entre : les trois ecarts sont mesures.
    ecart_tangentiel = abs(ca["coherence_tangentielle"] - cb["coherence_tangentielle"])
    ecart_axial = abs(ca["coherence_axiale"] - cb["coherence_axiale"])
    ecart_azimutal = abs(ca["coherence_azimutale"] - cb["coherence_azimutale"])
    v("⭐⭐⭐⭐ les deux cohérences PAR AXE se renversent entre deux marches miroir",
      ca["coherence_axiale"] > cb["coherence_axiale"]
      and ca["coherence_azimutale"] < cb["coherence_azimutale"],
      f"axiale {ca['coherence_axiale']}/{cb['coherence_axiale']} · "
      f"azimutale {ca['coherence_azimutale']}/{cb['coherence_azimutale']}")
    v("... et la cohérence TANGENTIELLE les sépare MOINS que chacun des deux axes",
      ecart_tangentiel < ecart_axial and ecart_tangentiel < ecart_azimutal,
      f"tangentielle {ecart_tangentiel:.3f} contre axiale {ecart_axial:.3f} et "
      f"azimutale {ecart_azimutal:.3f}")
    # ⚠⚠ Un axe qui ne porte rien n'a PAS de coherence. Une marche purement radiale ne porte ni
    # l'un ni l'autre, et rendre zero la ferait lire comme un serpentement parfait.
    pr = penchant(dep, axe, pas)
    v("⚠⚠ un axe qui ne porte rien rend `None`, jamais zéro",
      pr["coherence_axiale"] is None and pr["coherence_azimutale"] is None,
      f"axiale {pr['coherence_axiale']}, azimutale {pr['coherence_azimutale']}")
    pz = penchant(dep, axe, pax)
    v("... et une marche purement axiale rend UN sur son axe et `None` sur l'autre",
      pz["coherence_axiale"] == 1.0 and pz["coherence_azimutale"] is None,
      f"axiale {pz['coherence_axiale']}, azimutale {pz['coherence_azimutale']}")
    # ⚠⚠ LA BORNE SE DERIVE, ET LA SONDE LE VERIFIE DES DEUX COTES : un voxel exprime 2,4 µm, donc
    # deux pas dont la part axiale parcourt 2,08 µm sont muets et 2,77 µm ne le sont plus.
    sous = penchant(dep, axe, _course_fabriquee([rad + 0.006 * z] * 2)[2])
    sur = penchant(dep, axe, _course_fabriquee([rad + 0.008 * z] * 2)[2])
    v("sonde de la borne : sous un voxel de chemin l'axe est muet, au-dessus il parle",
      sous["coherence_axiale"] is None and sur["coherence_axiale"] is not None,
      f"{sous['chemin_axial_um']} µm muet, {sur['chemin_axial_um']} µm lu "
      f"({sur['coherence_axiale']}) · un voxel = {VOXEL_UM} µm")

    # ---- axial contre azimutal
    d_ax = np.cos(np.radians(th)) * rad + np.sin(np.radians(th)) * z
    _, _, axiale = _course_fabriquee([d_ax] * 8)
    q = penchant(dep, axe, axiale)
    v("un penchant purement axial est vu axial et pas azimutal",
      q["axial_absolu_median"] > 0.45 and q["azimutal_absolu_median"] < 1e-6,
      f"axial {q['axial_absolu_median']}, azimutal {q['azimutal_absolu_median']}")
    _, _, azimutale = _course_fabriquee([d_plus] * 8)
    q2 = penchant(dep, axe, azimutale)
    v("... et un penchant purement azimutal l'inverse",
      q2["azimutal_absolu_median"] > 0.45 and abs(q2["axial_absolu_median"]) < 1e-6,
      f"axial {q2['axial_absolu_median']}, azimutal {q2['azimutal_absolu_median']}")

    # ---- les retours vers l'axe
    d_retour = -rad
    _, _, retours = _course_fabriquee([rad, rad, d_retour, rad])
    q = penchant(dep, axe, retours)
    v("un pas qui revient vers l'axe est compté au-delà de 90°",
      q["pas_au_dela_de_90_deg"] == 1, f"{q['pas_au_dela_de_90_deg']}")

    # ---- l'axe du rouleau
    ok = {"lignes": [{"de": 1, "a": 2, "rayon_mm": 4.0,
                      "detail": [{"radial_zyx": [0.0, 0.0, 1.0]}, {"radial_zyx": [0.0, 1.0, 0.0]}]}]}
    ko = {"lignes": [{"de": 1, "a": 2, "rayon_mm": 4.0,
                      "detail": [{"radial_zyx": [0.5, 0.0, 0.866]}]}]}
    v("le contrôle de l'axe passe sur des radiaux perpendiculaires à z",
      laxe_du_rouleau_est_il_le_z([ok])["laxe_du_rouleau_est_le_z_du_volume"])
    v("⚠ ... et il ECHOUE sur un repère où l'axe n'est pas z",
      not laxe_du_rouleau_est_il_le_z([ko])["laxe_du_rouleau_est_le_z_du_volume"],
      f"{laxe_du_rouleau_est_il_le_z([ko])['angle_max_deg']}°")
    v("... et sans radial il est indécidable",
      not laxe_du_rouleau_est_il_le_z([{"lignes": []}])["decidable"])

    # ---- l'agrégation
    # ⚠⚠ HUIT MARCHES ET PAS QUATRE. Un Wilcoxon apparie sur quatre paires ne peut pas descendre
    # sous p = 0,125 quel que soit l'ecart : une batterie batie dessus verifierait que le test est
    # sans puissance, pas qu'il rejette. Huit paires donnent p = 0,0078 au mieux.
    rangs = []
    for i, ang in enumerate((20.0, 22.0, 25.0, 27.0, 30.0, 32.0, 35.0, 37.0)):
        d = np.cos(np.radians(ang)) * rad + np.sin(np.radians(ang)) * phi
        _, _, pa = _course_fabriquee([d] * 10)
        # ⚠ Le signe axial alterne : la fixture doit pouvoir rendre « aucun sens préféré ».
        pa = [{"direction": list(map(float, d + ((-1) ** i) * 0.2 * z)), "avance_um": 173.0}
              for _ in range(10)]
        r = penchant(dep, axe, pa)
        rangs.append({**r, "marche": i, "bande": (10 * i, 10 * i + 5), "rayon_mm": 4.0 + i})
    f = la_forme_du_penchant(rangs)
    v("la forme agrège la distribution de tous les pas",
      f["decidable"] and f["pas"] == 80 and 20.0 < f["angle_median_deg"] < 40.0,
      f"{f['pas']} pas, médiane {f['angle_median_deg']}°")
    v("... et déclare un chemin qui PENCHE quand la cohérence est haute", f["le_chemin_penche"],
      f"cohérence {f['coherence_mediane']}")
    v("... et ne trouve aucun sens axial préféré quand les signes alternent",
      not f["le_glissement_axial_a_un_sens_prefere"],
      f"{f['bandes_qui_glissent_vers_les_z_croissants']}/8, p {f['p_du_signe_axial']}")
    v("moins de trois marches est indécidable", not la_forme_du_penchant(rangs[:2])["decidable"])
    serp = []
    for i in range(4):
        pa = [{"direction": list(map(float, d_plus if k % 2 else d_moins)), "avance_um": 173.0}
              for k in range(10)]
        serp.append({**penchant(dep, axe, pa), "marche": i, "bande": (i, i), "rayon_mm": 4.0})
    fs = la_forme_du_penchant(serp)
    v("⚠ ... et un chemin qui SERPENTE est déclaré tel, au même angle médian",
      fs["le_chemin_serpente"] and abs(fs["angle_median_deg"] - f["angle_median_deg"]) < 12.0,
      f"{fs['angle_median_deg']}° coh {fs['coherence_mediane']} contre {f['angle_median_deg']}° "
      f"coh {f['coherence_mediane']}")

    # ---- l'accord au maillage
    maillage = {r["bande"]: r["angle_median_deg"] for r in rangs}
    acc = le_penchant_saccorde_t_il_au_maillage(rangs, maillage)
    v("un maillage identique au penchant est indiscernable ET accordé en rangs",
      acc["decidable"] and acc["le_niveau_est_indiscernable"] and acc["les_rangs_saccordent"],
      f"p apparié {acc['p_apparie']}, rho {acc['rho_de_spearman']}")
    decale = {k: v2 + 25.0 for k, v2 in maillage.items()}
    acc2 = le_penchant_saccorde_t_il_au_maillage(rangs, decale)
    v("⚠ ... un maillage décalé de 25° est distingué en NIVEAU tout en gardant les rangs",
      not acc2["le_niveau_est_indiscernable"] and acc2["les_rangs_saccordent"],
      f"p apparié {acc2['p_apparie']}, rho {acc2['rho_de_spearman']}")
    inverse = {k: 100.0 - v2 for k, v2 in maillage.items()}
    acc3 = le_penchant_saccorde_t_il_au_maillage(rangs, inverse)
    v("⚠⚠ ... et un maillage de rangs INVERSES est refusé en rangs",
      not acc3["les_rangs_saccordent"], f"rho {acc3['rho_de_spearman']}")
    v("moins de trois paires est indécidable",
      not le_penchant_saccorde_t_il_au_maillage(rangs[:2], maillage)["decidable"])

    # ---- le cap
    cap = le_cap_change_t_il_le_penchant(f, fs)
    v("le cap est jugé sur deux effets séparés", cap["decidable"]
      and "le_cap_reduit_le_penchant" in cap and "le_cap_supprime_les_retours" in cap)
    v("... et une course indécidable ne rend pas un verdict",
      not le_cap_change_t_il_le_penchant(f, {"decidable": False})["decidable"])

    # ---- la fixture, en version courte : elle doit SEPARER la spirale de la pile froissée
    fx = la_fixture_tranche_t_elle(pas_max=8, rayons_mm=(4.0, 18.0), caps=(0.75,))
    v("la fixture : la spirale reste sous un degré", fx["la_spirale_reste_sous_un_degre"],
      " / ".join(f"{s['rayon_mm']} mm → {s['par_cap'][0]['angle_median_deg']}° "
                 f"(analytique {s['inclinaison_analytique_deg']}°)" for s in fx["spirales"]))
    v("la fixture : une pile plane ne penche pas", fx["la_pile_plane_ne_penche_pas"])
    v("⚠⚠ la fixture : la spirale n'est JAMAIS lue au-dessus de l'inclinaison de son départ",
      fx["la_spirale_nest_jamais_lue_au_dessus_de_son_depart"],
      " / ".join(f"{s['inclinaison_analytique_deg']}→"
                 f"{s['par_cap'][0]['inclinaison_analytique_a_larrivee_deg']}, lu "
                 f"{s['par_cap'][0]['angle_median_deg']}" for s in fx["spirales"]))
    # ⚠⚠ LA LIMITE EST ASSERTEE DANS LE SENS OU ELLE EST VRAIE. Sous un cap, la pile froissee
    # rend une coherence HAUTE : la mesure ne separe donc pas le froisse du penche, et la
    # batterie le fige plutot que de laisser le document affirmer le contraire un jour.
    v("⚠⚠ la fixture : sous un cap, la cohérence NE sépare PAS le froissé du penché",
      not fx["la_coherence_separe_le_froisse_du_penche"],
      f"cohérence {fx['coherence_de_la_pile_froissee']} sur une pile froissée, "
      f"{fx['piles'][0]['par_cap'][0]['coherence_tangentielle']} à plat")
    froissee = fx["piles"][1]["par_cap"][0]["angle_median_deg"]
    spirale = max(s["par_cap"][0]["angle_median_deg"] for s in fx["spirales"])
    v("⚠⚠ la fixture SEPARE les deux matières par l'angle, d'un ordre de grandeur au moins",
      froissee > 10.0 * spirale, f"{froissee}° contre {spirale}°")

    # ---- l'affichage
    import contextlib, io  # noqa: PLC0415
    faux = {"sources": ["f.json"], "voxel_um": VOXEL_UM, "bandes_du_maillage": len(maillage),
            "laxe": laxe_du_rouleau_est_il_le_z([ok]),
            "par_course": [{"source": "f.json", "memoire_du_cap": 0.75, "marches_arrivees": len(rangs),
                            "marches": [{k: v2 for k, v2 in r.items() if k != "angles_deg"}
                                        for r in rangs],
                            "la_forme_du_penchant": f,
                            "le_penchant_saccorde_t_il_au_maillage": acc}],
            "le_cap_change_t_il_le_penchant": cap, "la_fixture_tranche_t_elle": fx}
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher(faux)
    sortie = tampon.getvalue()
    v("l'affichage tourne sur un résultat complet",
      "LE CHEMIN PENCHE" in sortie and "maillage humain" in sortie and "fixture" in sortie)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "mesure de `135` absente"})
    v("... et une mesure absente est dite, jamais dessinée", "⚠" in tampon.getvalue())
    v("une mesure sans `135` refuse plutôt que de deviner",
      "message" in mesurer(cesse=RACINE / "docs" / "mesures" / "absent_de_l_arbre.json"))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--sans-fixture", action="store_true",
                   help="ne pas lancer le contrôle sur matière fabriquée")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(avec_fixture=not a.sans_fixture)
    afficher(r)
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
