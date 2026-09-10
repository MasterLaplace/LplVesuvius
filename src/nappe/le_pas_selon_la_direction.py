#!/usr/bin/env python3
"""Y a-t-il une direction ou la periode est MINIMALE ? — l'eventail, avec le selecteur corrige.

⚠⚠⚠ POURQUOI CE FICHIER, ET DEUX TRANCHES L'IMPOSENT. `100` a balaye la periode dans DEUX
directions — le rayon et la normale du maillage, separees de 34° — et rend un rapport median de
**1,018** la ou un empilement parallele en predit **1,184**. Or un empilement de feuilles PARALLELES
ne PEUT PAS avoir la meme periode dans deux directions ecartees de 34° : sa periode apparente vaut
`p0 / cos(theta)`, minimale le long de sa normale et plus grande partout ailleurs.

⛔⛔ ET `105` A MONTRE QUE CETTE MESURE A ETE FAITE AVEC UN SELECTEUR BIAISE, qui lit un cran trop
haut. Le biais est multiplicatif, donc il ne s'annule PAS dans un rapport de deux valeurs
quantifiees differemment : refaire la comparaison avec le selecteur corrige est donc la premiere
chose a faire, et elle est faite ici, APPARIEE sur les memes lectures.

⭐⭐⭐ MAIS DEUX DIRECTIONS NE DECIDENT PAS D'UNE COURBE, ET C'EST L'ARGUMENT DU FICHIER. `p0/cos`
demande plus de deux points pour se distinguer d'une constante. On balaie donc un EVENTAIL de
directions dans le plan qui contient le rayon et la normale, et on lit la FORME de `p(theta)`.

⭐⭐⭐ LES DEUX MODELES SONT AJUSTES A ARMES EGALES — UN PARAMETRE LIBRE CHACUN. L'angle de la
normale n'est pas ajuste : il est FIXE par la direction que `101` mesure sur la meme cellule, par un
instrument qui ne partage rien avec celui-ci (une covariance de gradients contre une periodicite).
C'est ce qui empeche le modele parallele de gagner en s'offrant un degre de liberte de plus — la
faute que `101` a evitee en refutant l'axe decale.

⭐⭐ ET LA DIRECTION DU MINIMUM EST UN SECOND INSTRUMENT POUR LA NORMALE. Elle est rendue A PART de
la comparaison, parce qu'elle ajuste un parametre de plus ; la melanger rendrait la comparaison
inequitable.

⛔ UNE EXPLICATION EST DEJA REFUTEE, ET ELLE ETAIT LA PLUS PLAUSIBLE : une famille de feuilles qui
TOURNE le long de la sonde. Le taux de franchissement local vaut `cos(angle)/pas`, donc une sonde
qui traverse une famille tournante integre un taux variable. Mesure sur une pile fabriquee
tournante : le rapport MONTE (1,200 a 1,524 pour une rotation de 0 a 25°/100 µm), il ne descend
pas vers 1. La coherence limitee de l'orientation n'explique donc pas `100`.

Usage :
    uv run python src/nappe/le_pas_selon_la_direction.py --verifier
    uv run python src/nappe/le_pas_selon_la_direction.py --bandes 28 --cellules 3 \\
        --json docs/mesures/le_pas_selon_la_direction.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

# ⚠ L'eventail est declare AVANT tout resultat : un demi-angle qu'on resserre jusqu'a ce que la
# courbe plaise serait le seuil regle sur ce qui passe. ±50° est impose par la fenetre du balayage
# (86,5 a 346,0 µm) : au-dela, `p0/cos` en sort et la reponse serait une BUTEE lue comme mesure.
DEMI_ANGLE_DEG = 50.0
DIRECTIONS = 21
CELLULES_PAR_BANDE = 3
DEMI = 20


def eventail(normale_zyx: np.ndarray, radial_zyx: np.ndarray,
             demi_angle_deg: float = DEMI_ANGLE_DEG,
             combien: int = DIRECTIONS) -> tuple[np.ndarray, np.ndarray]:
    """Les directions du plan (normale, rayon), reperees par leur angle A LA NORMALE.

    ⭐⭐ LE PLAN EST CELUI QUI CONTIENT LES DEUX DIRECTIONS DEJA MESUREES, et pas un plan
    quelconque : c'est ce qui rend `99` (le rayon) et `101` (la normale) lisibles comme deux POINTS
    de la courbe rendue ici, au lieu de trois mesures sans rapport.

    ⚠ La seconde base est le rayon ORTHOGONALISE contre la normale. Prendre le rayon tel quel
    donnerait un repere oblique, donc un angle qui ne serait pas celui qu'on croit lire.
    """
    u = np.asarray(normale_zyx, dtype=np.float64)
    u = u / max(np.linalg.norm(u), 1e-12)
    w0 = np.asarray(radial_zyx, dtype=np.float64)
    # ⚠⚠⚠ LA NORMALE EST ORIENTEE VERS LE RAYON, ET SANS CELA L'EVENTAIL SONDE LE MAUVAIS DEMI-PLAN.
    # Un vecteur propre n'a PAS de sens — `101` le dit et compare des directions au produit scalaire
    # ABSOLU pour cette raison. Sans orientation, une cellule sur deux voit son eventail bascule et
    # le rayon tombe au-dela de ±50°, donc hors de portee. Mesure avant correction : le rayon etait
    # hors de l'eventail sur **61 %** des cellules, et l'angle median sortait a 67,8° la ou `101`
    # publie 34,59.
    if float(w0 @ u) < 0.0:
        u = -u
    w = w0 - float(w0 @ u) * u
    n = np.linalg.norm(w)
    if n < 1e-9:
        # ⚠ Rayon et normale colineaires : le plan n'est pas defini. On le DIT plutot que de
        # fabriquer un plan arbitraire, dont l'angle rendu ne voudrait rien dire.
        return np.zeros(0), np.zeros((0, 3))
    w = w / n
    angles = np.linspace(-demi_angle_deg, demi_angle_deg, combien)
    a = np.deg2rad(angles)
    return angles, np.cos(a)[:, None] * u[None, :] + np.sin(a)[:, None] * w[None, :]


def angle_du_rayon(normale_zyx: np.ndarray, radial_zyx: np.ndarray) -> float:
    """Ou tombe le RAYON sur l'axe de l'eventail — donc ou `99` a mesure son pas."""
    u = np.asarray(normale_zyx, dtype=np.float64)
    u = u / max(np.linalg.norm(u), 1e-12)
    r = np.asarray(radial_zyx, dtype=np.float64)
    r = r / max(np.linalg.norm(r), 1e-12)
    # ⚠ Meme orientation que `eventail`, sinon l'angle rendu ne serait pas celui de l'eventail.
    if float(r @ u) < 0.0:
        u = -u
    w = r - float(r @ u) * u
    n = np.linalg.norm(w)
    return 0.0 if n < 1e-9 else float(np.rad2deg(np.arctan2(n, float(r @ u))))


def profil_dune_famille_tournante(alpha0_deg: float, rotation_deg_par_100um: float,
                                  pas_um: float, longueur_um: float, n: int) -> np.ndarray:
    """Le profil le long d'une sonde DROITE traversant une famille de feuilles qui TOURNE.

    ⭐⭐⭐ ELLE PORTE LA REFUTATION DE L'EXPLICATION LA PLUS PLAUSIBLE, donc elle vit dans le module
    et pas dans la batterie. Le taux de franchissement local vaut `cos(angle)/pas` ; la phase est
    son integrale le long du trajet, ce qu'un gabarit d'UNE periode ajuste en moyenne. Si une
    orientation incoherente ecrasait le rapport vers un, elle le ferait ICI, ou tout est connu.

    ⚠ La phase est integree ANALYTIQUEMENT et non sommee pas a pas : une somme discrete
    introduirait sa propre erreur, qu'on lirait comme un effet de la rotation.
    """
    s = np.linspace(0.0, float(longueur_um), int(n))
    a0 = np.deg2rad(float(alpha0_deg))
    r = np.deg2rad(float(rotation_deg_par_100um)) / 100.0
    phase = (s * np.cos(a0) if abs(r) < 1e-12
             else (np.sin(a0 + r * s) - np.sin(a0)) / r)
    return 100.0 + 40.0 * np.cos(2 * np.pi * phase / float(pas_um))


def _mediane(v) -> float | None:
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], dtype=np.float64)
    return float(np.median(v)) if len(v) else None


# ⚠⚠⚠ LE PLANCHER DU RESIDU, ET IL EXISTE POUR EVITER UN FAUX ABSENT. Un ajustement PARFAIT rend
# un residu nul, donc un rapport infini — que la premiere version rendait `None`, c'est-a-dire
# « pas de donnee » la ou la reponse est « infiniment mieux ». Une mediane qui saute ces
# cellules-la ecarterait precisement les meilleures. Le plancher vaut un dixieme du cran du
# balayage : sous cette valeur un residu n'est pas distinguable de zero, puisque la reponse
# elle-meme est quantifiee.
PLANCHER_DU_RESIDU_UM = 0.865

# ⚠⚠⚠ COMBIEN DE FOIS LE RESIDU SUR LA MATIERE PEUT DEPASSER CELUI SUR UNE PILE FABRIQUEE avant
# qu'on cesse de dire que le modele la decrit. Trois est genereux et declare d'avance ; la mesure
# rend vingt, donc aucun reglage ne sauverait le verdict. ⭐ ET C'EST LE BON REPERE, ce qui est une
# CORRECTION de ma premiere version : j'y comparais le residu a l'amplitude de la courbe, ce qui
# laissait passer un ajustement vingt fois pire que sur une reponse connue. Le repere d'un
# instrument est ce que CE MEME instrument obtient sur du connu, pas une part de son propre signal.
FOIS_LE_RESIDU_FABRIQUE_TOLERE = 3.0

# ⚠⚠⚠ LA PART DE L'AMPLITUDE AU-DELA DE LAQUELLE UN MODELE NE DECRIT PLUS LA COURBE. Elle est
# declaree AVANT tout resultat, et elle existe pour empecher une conclusion que ce depot
# recenserait aussitot : *une comparaison entre deux modeles dont AUCUN n'est juste*. « Le
# parallele perd » ne veut pas dire « la texture est isotrope » — il faut encore que l'isotrope,
# lui, decrive quelque chose. Un modele dont le residu depasse un tiers de l'amplitude de la
# courbe n'en decrit pas la forme, il en donne le niveau moyen.
PART_DE_LAMPLITUDE_TOLEREE = 1.0 / 3.0


def ajuster_les_deux_modeles(angles_deg, pas_um, en_butee, decalage_deg: float = 0.0) -> dict:
    """L'empilement PARALLELE contre la texture ISOTROPE, un parametre libre chacun.

    ⭐⭐⭐ A ARMES EGALES, ET C'EST LA CONDITION QUI REND LA COMPARAISON HONNETE. Le modele parallele
    s'ecrit `p(theta) = p0 / cos(theta - theta_n)` ; `theta_n` n'est PAS ajuste, il vaut zero parce
    que l'eventail est deja repere depuis la normale que `101` a mesuree sur cette cellule. Les deux
    modeles n'ont donc qu'un parametre : `p0`. Laisser `theta_n` libre offrirait au modele parallele
    un degre de liberte de plus et il gagnerait souvent par accident.

    ⚠⚠ L'AJUSTEMENT EST MEDIAN, PAS MOINDRES CARRES, et la raison est dans les donnees : le balayage
    est DISCRET (cran de 8,65 µm) et une butee produit une valeur aberrante. Une somme de carres
    suivrait l'aberration ; une mediane ne la suit pas.

    ⚠ `decalage_deg` sert au CONTROLE NEGATIF : il fait tourner la normale supposee. Le modele
    parallele doit CESSER de gagner quand elle est fausse, sinon sa victoire ne dit rien.
    """
    a = np.asarray(angles_deg, dtype=np.float64)
    p = np.asarray([np.nan if x is None else x for x in pas_um], dtype=np.float64)
    b = np.asarray(en_butee, dtype=bool)
    bon = np.isfinite(p) & ~b
    if bon.sum() < 4:
        return {"utilisables": int(bon.sum()), "decidable": False,
                "pourquoi": "moins de quatre directions utilisables"}
    aa, pp = a[bon], p[bon]
    c = np.cos(np.deg2rad(aa - decalage_deg))
    # ⚠ Une direction a plus de 78° de la normale supposee a un cosinus quasi nul : `p0 = p·cos`
    # y est numeriquement instable. Elle est ecartee de l'AJUSTEMENT, et comptee.
    sain = np.abs(c) > 0.2
    if sain.sum() < 4:
        return {"utilisables": int(bon.sum()), "decidable": False,
                "pourquoi": "trop de directions rasantes après décalage"}
    p0_par = float(np.median(pp[sain] * np.abs(c[sain])))
    p0_iso = float(np.median(pp))
    res_par = float(np.median(np.abs(pp[sain] - p0_par / np.abs(c[sain]))))
    res_iso = float(np.median(np.abs(pp - p0_iso)))
    return {
        "utilisables": int(bon.sum()), "en_butee": int(b.sum()),
        "ecartees_rasantes": int((~sain).sum()),
        "decidable": True, "decalage_deg": round(float(decalage_deg), 2),
        "pas_du_modele_parallele_um": round(p0_par, 1),
        "pas_du_modele_isotrope_um": round(p0_iso, 1),
        "residu_parallele_um": round(res_par, 2),
        "residu_isotrope_um": round(res_iso, 2),
        # ⭐⭐⭐ LE CHIFFRE DU FICHIER : au-dessus de un, l'empilement parallele explique mieux ;
        # au-dessous, la texture est isotrope et le balayage ne suit PAS une famille de feuilles.
        "gain_du_modele_parallele": round(res_iso / max(res_par, PLANCHER_DU_RESIDU_UM), 3),
        # ⚠ Le plancher a-t-il mordu ? Le dire evite de lire un gain plafonne comme une mesure.
        "residu_sous_le_plancher": bool(res_par < PLANCHER_DU_RESIDU_UM),
        "le_modele_parallele_gagne": bool(res_par < res_iso),
    }


def direction_du_minimum(angles_deg, pas_um, en_butee) -> dict:
    """Ou `p(theta)` est MINIMALE — la normale lue dans le PAS et non dans le gradient.

    ⭐⭐⭐ C'EST UN SECOND INSTRUMENT POUR LA DIRECTION, ET IL NE PARTAGE RIEN AVEC `101`. Le tenseur
    de structure lit une covariance de GRADIENTS ; ceci lit une PERIODICITE. Deux instruments qui
    n'ont pas la meme facon de se tromper, donc leur accord est une information.

    ⚠⚠ L'ARGMIN BRUT SERAIT DOMINE PAR LE CRAN DU BALAYAGE : plusieurs directions partagent la meme
    valeur quantifiee, donc « la premiere la plus basse » serait un tirage. On prend le BARYCENTRE
    des directions au minimum, ce qui est defini meme en cas d'egalite — et on publie COMBIEN de
    directions y sont, parce qu'un barycentre sur dix-huit directions n'est pas une direction.
    """
    a = np.asarray(angles_deg, dtype=np.float64)
    p = np.asarray([np.nan if x is None else x for x in pas_um], dtype=np.float64)
    b = np.asarray(en_butee, dtype=bool)
    bon = np.isfinite(p) & ~b
    if bon.sum() < 4:
        return {"decidable": False, "pourquoi": "moins de quatre directions utilisables"}
    aa, pp = a[bon], p[bon]
    bas = pp <= pp.min() + 1e-9
    return {"decidable": True, "directions_au_minimum": int(bas.sum()),
            "directions_lues": int(bon.sum()),
            "angle_du_minimum_deg": round(float(np.mean(aa[bas])), 2),
            "pas_au_minimum_um": round(float(pp.min()), 1),
            "pas_au_maximum_um": round(float(pp.max()), 1),
            "amplitude_um": round(float(pp.max() - pp.min()), 1)}


def balayer_un_eventail(lecteur, p_fin: np.ndarray, normale, radial, longueurs, mu, sd,
                        barre: float, voxel_fin_um: float,
                        demi_angle_deg: float = DEMI_ANGLE_DEG,
                        combien: int = DIRECTIONS, fils: int = 32) -> dict:
    """Le pas que la matiere montre dans CHAQUE direction de l'eventail, en UNE seule lecture.

    ⭐⭐⭐ LES VINGT ET UNE DIRECTIONS SONT LUES ENSEMBLE, ET C'EST `103` QUI L'IMPOSE : le cout
    d'une lecture distante suit les PLAGES d'octets plus un FIXE par appel (plancher de 3,76 s).
    Vingt et un appels separes paieraient donc vingt et un planchers — quatre-vingts secondes par
    cellule contre quelques-unes. Une mesure qui coute vingt fois son prix n'est pas une mesure
    plus sure, c'est une mesure qu'on ne lancera pas sur le corpus.

    ⭐⭐⭐ ET LE SELECTEUR EST CELUI QUE `105` A CORRIGE. `100` a mesure ses deux directions avec
    `pas_montre_calibre`, qui lit un cran trop haut ; le selecteur a DEUX ROLES — le calibre garde,
    le brut choisit parmi les admis — est importe et non recopie. Les deux sont rendus cote a cote,
    parce que leur ECART est ce qui dit si l'anomalie de `100` etait l'instrument.

    ⚠ Une direction non admise ou en butee est ECARTEE de l'ajustement, jamais ecretee : une butee
    dit « au moins ceci », et la lire comme une mesure serait la faute de `99`.
    """
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from le_balayage_rend_il_le_pas_injecte import choisir  # noqa: PLC0415

    angles, dirs = eventail(normale, radial, demi_angle_deg, combien)
    if not len(angles):
        return {"message": "rayon et normale colinéaires : le plan n'est pas défini"}
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    pas_vx = float(longueurs[-1]) / voxel_fin_um
    t = np.linspace(0.0, 1.0, n_long)
    seg = (p_fin[None, None, :]
           + dirs[:, None, :] * (pas_vx * t)[None, :, None])
    zyx = np.rint(seg).astype(np.int64)
    dedans = lecteur.dans_le_volume(zyx.reshape(-1, 3)).reshape(len(dirs), n_long).all(axis=1)
    out = {"angles_deg": [round(float(x), 2) for x in angles],
           "angle_du_rayon_deg": round(angle_du_rayon(normale, radial), 2),
           "sorties": int((~dedans).sum()),
           "calibre": [None] * len(dirs), "deux_roles": [None] * len(dirs),
           "ecartees": [True] * len(dirs)}
    if not dedans.any():
        out["part_admise"] = 0.0
        return out
    v = lecteur.lire(zyx[dedans].reshape(-1, 3), fils=fils).reshape(int(dedans.sum()), n_long)
    fini = np.isfinite(v).all(axis=1)
    ou = np.where(dedans)[0][fini]
    out["sorties"] = int(len(dirs) - len(ou))
    if not len(ou):
        out["part_admise"] = 0.0
        return out
    profs = M.profils_emboites(v[fini], longueurs)
    lu_c, sc_c, k_c, _ = choisir(profs, longueurs, mu, sd, "calibre", barre)
    lu_d, _, _, _ = choisir(profs, longueurs, mu, sd, "deux_roles", barre)
    bord = M.touche_un_bord(k_c, len(longueurs))
    admis = sc_c > barre
    for pos, idx in enumerate(ou):
        out["calibre"][idx] = round(float(lu_c[pos]), 1)
        out["deux_roles"][idx] = round(float(lu_d[pos]), 1)
        out["ecartees"][idx] = bool(bord[pos]) or not bool(admis[pos])
    out["part_admise"] = round(float(admis.mean()), 3)
    return out


def controle_fabrique(longueurs, mu, sd, barre: float, obliquites=(25.0, 40.0),
                      rotations=(0.0, 5.0, 10.0, 25.0),
                      decalage_faux_deg: float = 40.0) -> dict:
    """Ce que l'eventail rend sur des piles dont on CONNAIT la normale, droites puis TOURNANTES.

    ⭐⭐⭐ SANS LA PREMIERE MOITIE LE RESULTAT REEL NE VAUT RIEN. Si l'instrument ne voit pas
    l'anisotropie d'une pile FABRIQUEE parallele — ou `p(theta) = p0/cos(theta)` est vrai par
    construction — alors une courbe plate sur le vrai volume ne prouve pas que la matiere est
    isotrope, elle prouve seulement que l'instrument est aveugle.

    ⭐⭐⭐ ET LA SECONDE MOITIE REFUTE L'EXPLICATION LA PLUS PLAUSIBLE de l'anomalie de `100` : une
    famille de feuilles dont l'orientation n'est pas coherente sur la longueur de la sonde. Sur une
    pile TOURNANTE le rapport MONTE au lieu de descendre vers un.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from le_balayage_rend_il_le_pas_injecte import choisir  # noqa: PLC0415
    from combien_de_pas_la_matiere_porte import VolumeFabrique  # noqa: PLC0415

    out = {"decalage_faux_deg": decalage_faux_deg, "empilements": [], "tournantes": []}
    x_hat = np.array([0.0, 0.0, 1.0])
    for th in obliquites:
        vf = VolumeFabrique(C.PAS_UM, obliquite_deg=float(th))
        dep = np.array([2000.0, 2000.0, 2000.0])
        # ⚠⚠ RECALAGE DU DEPART SUR LA FAMILLE DE PLANS, faute de quoi le controle mesurerait sa
        # propre mise en place — le defaut que la fixture de `100` a paye et que j'ai repaye ici
        # en construisant la premiere version de ce controle.
        proj = float(dep @ vf.normale) * C.VOXEL_FIN_UM
        dep = dep + vf.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
        e = balayer_un_eventail(vf, dep, vf.normale, x_hat, longueurs, mu, sd, barre,
                                C.VOXEL_FIN_UM)
        if "message" in e:
            out["empilements"].append({"obliquite_deg": float(th), **e})
            continue
        juste = ajuster_les_deux_modeles(e["angles_deg"], e["deux_roles"], e["ecartees"])
        faux = ajuster_les_deux_modeles(e["angles_deg"], e["deux_roles"], e["ecartees"],
                                        decalage_deg=decalage_faux_deg)
        mini = direction_du_minimum(e["angles_deg"], e["deux_roles"], e["ecartees"])
        # ⭐⭐ LA PREDICTION EST EXTERIEURE : `p(theta) = pas_nominal / cos(theta)`, ecrite d'avance
        # et non ajustee. L'ecart median a cette prediction dit si l'instrument voit l'anisotropie,
        # independamment de tout ajustement.
        a = np.asarray(e["angles_deg"], dtype=np.float64)
        p = np.asarray([np.nan if x is None else x for x in e["deux_roles"]], dtype=np.float64)
        bon = np.isfinite(p) & ~np.asarray(e["ecartees"], dtype=bool)
        pred = C.PAS_UM / np.cos(np.deg2rad(a))
        out["empilements"].append({
            "obliquite_deg": float(th), "sorties": e["sorties"],
            "angle_du_rayon_deg": e["angle_du_rayon_deg"],
            "ecart_median_a_la_prediction_um": (
                round(float(np.median(np.abs(p[bon] - pred[bon]))), 2) if bon.sum() else None),
            "ajustement_juste": juste, "ajustement_decale": faux, "minimum": mini,
            # ⭐ La courbe elle-meme est gardee : une figure qui affirme « l'instrument voit
            # l'anisotropie » sans la MONTRER demande de la croire sur parole.
            "angles_deg": e["angles_deg"], "pas_um": e["deux_roles"],
            "prediction_um": [round(float(C.PAS_UM / np.cos(np.deg2rad(x))), 1)
                              for x in e["angles_deg"]]})

    # --- la pile TOURNANTE, qui refute l'explication par l'incoherence d'orientation ---------
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    for rot in rotations:
        lus = {}
        for nom_a, a0 in (("le_long_de_la_normale", 0.0), ("a_trente_quatre_degres", 34.0)):
            v = profil_dune_famille_tournante(a0, rot, C.PAS_UM, float(longueurs[-1]), n_long)
            profs = M.profils_emboites(v.reshape(1, n_long), longueurs)
            lu, _, _, _ = choisir(profs, longueurs, mu, sd, "deux_roles", barre)
            lus[nom_a] = round(float(lu[0]), 1)
        out["tournantes"].append({
            "rotation_deg_par_100um": float(rot),
            "rotation_sur_la_sonde_deg": round(rot * float(longueurs[-1]) / 100.0, 1),
            **lus,
            "rapport": round(lus["a_trente_quatre_degres"]
                             / max(lus["le_long_de_la_normale"], 1e-9), 3)})
    if len(out["tournantes"]) >= 2:
        # ⭐⭐⭐ LE VERDICT DE LA REFUTATION : si une orientation incoherente ecrasait le rapport
        # vers un, il DESCENDRAIT quand la rotation monte. Il monte.
        r0 = out["tournantes"][0]["rapport"]
        rn = out["tournantes"][-1]["rapport"]
        out["une_famille_tournante_ecrase_le_rapport"] = bool(rn < r0)
        out["le_rapport_monte_avec_la_rotation"] = bool(rn > r0)

    vus = [x for x in out["empilements"] if x.get("ajustement_juste", {}).get("decidable")]
    if vus:
        out["linstrument_voit_lanisotropie"] = bool(
            all(x["ajustement_juste"]["le_modele_parallele_gagne"] for x in vus))
        out["le_minimum_tombe_sur_la_normale"] = bool(
            all(abs(x["minimum"]["angle_du_minimum_deg"]) <= 5.0 for x in vus))
        out["une_fausse_normale_fait_perdre_le_modele"] = bool(
            all(not x["ajustement_decale"].get("le_modele_parallele_gagne", True)
                or (x["ajustement_decale"]["gain_du_modele_parallele"]
                    < x["ajustement_juste"]["gain_du_modele_parallele"]) for x in vus))
    return out


def mesurer(cellules: int = CELLULES_PAR_BANDE, demi: int = DEMI, graine: int = 271,
            bandes_max: int | None = None, fils: int = 32,
            demi_angle_deg: float = DEMI_ANGLE_DEG,
            directions: int = DIRECTIONS) -> dict:
    """L'eventail sur le vrai volume, autour de la normale que `101` mesure sur chaque cellule.

    ⭐⭐⭐ LA NORMALE VIENT DE `101`, PAS DU MAILLAGE, et c'est la seconde difference avec `100`.
    Le tenseur de structure lit la matiere ; le maillage est un trace humain, et `101` a mesure
    treize degres entre les deux. Reperer l'eventail depuis une direction fausse deplacerait le
    minimum sans que rien ne le dise.

    ⚠ Une cellule dont le tenseur ne donne pas de direction est SAUTEE et comptee, jamais remplacee
    par la normale du maillage : melanger deux origines de direction ferait deux mesures sous un
    seul nom.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_normale_nest_pas_le_rayon as N  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from combien_de_pas_la_matiere_porte import direction_de_la_matiere  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415
    from transformations_de_volume import (appliquer, appliquer_direction,  # noqa: PLC0415
                                           matrice)
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}
    if not M.ALIGNEMENT.is_file():
        return {"message": f"alignement des bandes absent : {M.ALIGNEMENT}"}
    al = {(x["de"], x["a"]): x for x in json.loads(M.ALIGNEMENT.read_text())["lignes"]}

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    barre_moities = nul_du_tenseur(demi=demi)["accord_des_moities_p1_deg"]

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = time.time()
    lignes, sans_direction = [], 0
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 1:
            continue
        p0 = a[ind[:, 0], ind[:, 1]]
        c0 = N.centre_interpole(p0[:, 2], bords, cx, cy)
        rad_fin = appliquer_direction(m, N.direction_radiale(p0, c0))
        departs = appliquer(m, p0)
        cellules_lues = []
        for j in range(len(departs)):
            d_mat, desaccord, _ = direction_de_la_matiere(vol, departs[j], demi, fils)
            if d_mat is None or not (np.isfinite(desaccord) and desaccord < barre_moities):
                sans_direction += 1
                continue
            e = balayer_un_eventail(vol, departs[j], d_mat, rad_fin[j], longueurs, mu, sd,
                                    barre, C.VOXEL_FIN_UM, demi_angle_deg, directions, fils)
            if "message" in e:
                sans_direction += 1
                continue
            cel = {"angles_deg": e["angles_deg"],
                   "angle_du_rayon_deg": e["angle_du_rayon_deg"],
                   "desaccord_des_moities_deg": round(float(desaccord), 2),
                   "part_admise": e["part_admise"], "sorties": e["sorties"]}
            for nom in ("calibre", "deux_roles"):
                cel[nom] = {
                    "pas_um": e[nom],
                    "ajustement": ajuster_les_deux_modeles(e["angles_deg"], e[nom],
                                                           e["ecartees"]),
                    "minimum": direction_du_minimum(e["angles_deg"], e[nom], e["ecartees"]),
                    # ⭐⭐ LES DEUX POINTS DE `100`, EXTRAITS DE LA MEME COURBE : la normale
                    # (angle 0) et le rayon (angle mesure). Les relire ici plutot que de refaire
                    # une mesure a part garantit qu'ils portent sur les MEMES lectures.
                    **_les_deux_points_de_100(e["angles_deg"], e[nom], e["ecartees"],
                                              e["angle_du_rayon_deg"]),
                }
            cellules_lues.append(cel)
        if not cellules_lues:
            continue
        lignes.append({"de": x["de"], "a": x["a"],
                       "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
                       "cellules": len(cellules_lues), "detail": cellules_lues})
        avancement(len(lignes), len(bandes), "bandes", depart)

    if not lignes:
        return {"message": "aucune cellule lisible dans le volume fin"}
    return agreger({
        "fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "pas_nominal_um": C.PAS_UM,
        "demi_angle_deg": demi_angle_deg, "directions": directions,
        "cellules_par_bande": cellules, "demi_cube_voxels": demi,
        "barre_du_nul_calibre": round(float(barre), 4),
        "barre_daccord_des_moities_deg": barre_moities,
        "cran_du_balayage_um": round(float(longueurs[1] - longueurs[0]), 2),
        "cellules_sans_direction": sans_direction,
        "secondes": round(time.time() - depart, 1),
        "bandes": len(lignes), "lignes": lignes,
        "controle_fabrique": controle_fabrique(longueurs, mu, sd, barre),
    })


def _les_deux_points_de_100(angles_deg, pas_um, ecartees, angle_rayon_deg) -> dict:
    """Les deux directions que `100` a comparees, relues sur la MEME courbe.

    ⭐⭐ ELLES SORTENT DE L'EVENTAIL PLUTOT QUE D'UNE MESURE A PART, et c'est ce qui rend la
    comparaison avec `100` legitime : memes lectures, meme garde, meme selecteur. Refaire une
    mesure separee comparerait deux populations, faute que ce depot a deja payee.

    ⚠ Le rayon ne tombe pas exactement sur une direction de l'eventail : on prend la plus proche,
    et on publie DE COMBIEN elle en differe. Interpoler inventerait une precision.
    """
    a = np.asarray(angles_deg, dtype=np.float64)
    p = np.asarray([np.nan if x is None else x for x in pas_um], dtype=np.float64)
    e = np.asarray(ecartees, dtype=bool)
    i_n = int(np.argmin(np.abs(a)))
    # ⚠⚠⚠ SI LE RAYON TOMBE HORS DE L'EVENTAIL, ON REFUSE. Ecreter sur la direction du bord ferait
    # publier un angle de FENETRE comme un angle de MATIERE — la faute que ce depot recense sous
    # « une limite de grille publiee comme une limite materielle ». Avant cette garde, 61 % des
    # cellules rendaient le bord a 50° et un `1/cos` de 1,556 qui n'etait qu'un aveu de portee.
    if not (a.min() - 1e-9 <= float(angle_rayon_deg) <= a.max() + 1e-9):
        return {"les_deux_points_de_100": None,
                "rayon_hors_de_leventail": True,
                "angle_du_rayon_deg": round(float(angle_rayon_deg), 2)}
    i_r = int(np.argmin(np.abs(a - float(angle_rayon_deg))))
    if e[i_n] or e[i_r] or not np.isfinite(p[i_n]) or not np.isfinite(p[i_r]):
        return {"les_deux_points_de_100": None}
    return {"les_deux_points_de_100": {
        "pas_le_long_de_la_normale_um": round(float(p[i_n]), 1),
        "pas_le_long_du_rayon_um": round(float(p[i_r]), 1),
        "angle_du_rayon_deg": round(float(angle_rayon_deg), 2),
        "angle_de_la_direction_prise_deg": round(float(a[i_r]), 2),
        "rapport_rayon_sur_normale": round(float(p[i_r] / max(p[i_n], 1e-9)), 3),
        "un_sur_cos": round(float(1.0 / max(np.cos(np.deg2rad(a[i_r] - a[i_n])), 1e-9)), 3)}}


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des cellules — meme partage que `100` a `105`."""
    cel = [c for x in r["lignes"] for c in x["detail"]]
    r["resume"] = {"cellules": len(cel), "bandes": len(r["lignes"]),
                   "cellules_sans_direction": r.get("cellules_sans_direction", 0)}
    for nom in ("calibre", "deux_roles"):
        aj = [c[nom]["ajustement"] for c in cel if c[nom]["ajustement"].get("decidable")]
        mi = [c[nom]["minimum"] for c in cel if c[nom]["minimum"].get("decidable")]
        deux = [c[nom]["les_deux_points_de_100"] for c in cel
                if c[nom]["les_deux_points_de_100"] is not None]
        d = {"cellules_decidables": len(aj)}
        if aj:
            d.update({
                "gain_median_du_modele_parallele": round(float(np.median(
                    [x["gain_du_modele_parallele"] for x in aj])), 3),
                # ⚠ Combien de cellules ont un residu SOUS le plancher, donc un gain plafonne :
                # sans ce compte, un gain median eleve pourrait n'etre qu'un plafond.
                "cellules_au_plancher_du_residu": int(sum(
                    1 for x in aj if x.get("residu_sous_le_plancher"))),
                # ⭐⭐⭐ LE CHIFFRE DU FICHIER : sur quelle PART des cellules le modele parallele
                # bat-il l'isotrope ? Une mediane de gains cacherait qu'une moitie perd.
                "part_ou_le_parallele_gagne": round(float(np.mean(
                    [x["le_modele_parallele_gagne"] for x in aj])), 3),
                "residu_parallele_median_um": round(float(np.median(
                    [x["residu_parallele_um"] for x in aj])), 2),
                "residu_isotrope_median_um": round(float(np.median(
                    [x["residu_isotrope_um"] for x in aj])), 2),
                "pas_du_modele_parallele_median_um": round(float(np.median(
                    [x["pas_du_modele_parallele_um"] for x in aj])), 1),
                "pas_du_modele_isotrope_median_um": round(float(np.median(
                    [x["pas_du_modele_isotrope_um"] for x in aj])), 1),
            })
        if mi:
            d.update({
                # ⭐⭐ LA NORMALE LUE DANS LE PAS, contre celle que `101` lit dans le gradient :
                # l'eventail est repere depuis `101`, donc un minimum a zero EST leur accord.
                "angle_du_minimum_median_deg": round(float(np.median(
                    [x["angle_du_minimum_deg"] for x in mi])), 2),
                "angle_du_minimum_ecart_absolu_median_deg": round(float(np.median(
                    [abs(x["angle_du_minimum_deg"]) for x in mi])), 2),
                "amplitude_mediane_um": round(float(np.median(
                    [x["amplitude_um"] for x in mi])), 1),
                # ⚠ Un minimum partage par presque toutes les directions n'est pas un minimum :
                # c'est une courbe plate, et le publier comme une direction serait un tirage.
                "directions_au_minimum_mediane": round(float(np.median(
                    [x["directions_au_minimum"] for x in mi])), 1),
                "directions_lues_mediane": round(float(np.median(
                    [x["directions_lues"] for x in mi])), 1),
            })
        hors = sum(1 for c in cel if c[nom].get("rayon_hors_de_leventail"))
        d["cellules_dont_le_rayon_est_hors_de_leventail"] = hors
        if deux:
            d.update({
                "rapport_median_de_100": round(float(np.median(
                    [x["rapport_rayon_sur_normale"] for x in deux])), 3),
                "un_sur_cos_median": round(float(np.median(
                    [x["un_sur_cos"] for x in deux])), 3),
                "cellules_a_deux_points": len(deux),
            })
        # ⭐⭐⭐ LA COURBE MEDIANE, ANGLE PAR ANGLE, ET C'EST ELLE QUE LA FIGURE MONTRE. Le verdict
        # porte sur la FORME de `p(theta)` ; une part de victoires ne la montre pas. ⚠ La mediane
        # est prise par angle sur les cellules dont la direction n'est pas ecartee, et le COMPTE
        # est publie a cote — une mediane sur trois cellules n'est pas une courbe.
        angles = cel[0]["angles_deg"] if cel else []
        courbe = []
        for i, ang in enumerate(angles):
            vals = [c[nom]["pas_um"][i] for c in cel
                    if c[nom]["pas_um"][i] is not None
                    and not c[nom]["ajustement"].get("decidable", False) is False]
            vals = [x for x in vals if x is not None]
            courbe.append({"angle_deg": ang,
                           "pas_median_um": (round(float(np.median(vals)), 1) if vals else None),
                           "cellules": len(vals)})
        d["courbe_mediane"] = courbe
        r[nom] = d
    # ⭐⭐⭐ LE REPERE DU RESIDU EST CELUI DE LA PILE FABRIQUEE, ET CE VERDICT PASSE AVANT TOUS LES
    # AUTRES. Le meme instrument, le meme selecteur, la meme longueur de sonde : sur une pile dont
    # la reponse est connue le residu vaut moins d'un micron. Un residu vingt fois plus grand sur la
    # matiere ne se rachete pas en battant marginalement une constante.
    fab = None
    for e in r.get("controle_fabrique", {}).get("empilements", []):
        j = e.get("ajustement_juste", {})
        if j.get("decidable"):
            fab = j["residu_parallele_um"] if fab is None else min(fab, j["residu_parallele_um"])
    for nom in ("calibre", "deux_roles"):
        d = r.get(nom, {})
        if fab is not None and d.get("residu_parallele_median_um") is not None:
            d["residu_sur_pile_fabriquee_um"] = round(float(fab), 2)
            d["combien_de_fois_pire_que_la_pile_fabriquee"] = round(
                d["residu_parallele_median_um"] / max(fab, PLANCHER_DU_RESIDU_UM), 1)
            d["le_modele_parallele_decrit_la_matiere"] = bool(
                d["combien_de_fois_pire_que_la_pile_fabriquee"]
                <= FOIS_LE_RESIDU_FABRIQUE_TOLERE)
    # ⭐⭐⭐ AUCUN DES DEUX MODELES NE DECRIT-IL LA COURBE ? Ce verdict passe AVANT les autres,
    # parce qu'il les rend lisibles : si les deux residus depassent le tiers de l'amplitude, dire
    # « l'isotrope gagne » serait dire « le moins faux des deux faux ».
    for nom in ("calibre", "deux_roles"):
        d = r.get(nom, {})
        amp = d.get("amplitude_mediane_um")
        if amp and d.get("residu_parallele_median_um") is not None:
            seuil = PART_DE_LAMPLITUDE_TOLEREE * amp
            d["seuil_de_description_um"] = round(seuil, 2)
            d["le_parallele_decrit_la_courbe"] = bool(d["residu_parallele_median_um"] <= seuil)
            d["lisotrope_decrit_la_courbe"] = bool(d["residu_isotrope_median_um"] <= seuil)
            d["aucun_des_deux_ne_decrit_la_courbe"] = bool(
                not d["le_parallele_decrit_la_courbe"] and not d["lisotrope_decrit_la_courbe"])
    # ⭐⭐⭐ LES DEUX VERDICTS, CALCULES, ET CHACUN PEUT ECHOUER SEPAREMENT.
    dr = r.get("deux_roles", {})
    ca = r.get("calibre", {})
    r["resume"]["la_matiere_est_un_empilement_parallele"] = bool(
        dr.get("part_ou_le_parallele_gagne", 0.0) > 0.5
        and dr.get("le_parallele_decrit_la_courbe", False)
        # ⭐⭐⭐ ET SURTOUT : le modele doit decrire la matiere AUSSI BIEN qu'il decrit une pile
        # connue, a un facteur trois pres. Battre une constante de 36 % quand la meme mesure sur du
        # connu rend un facteur vingt n'est pas la decrire.
        and dr.get("le_modele_parallele_decrit_la_matiere", False))
    # ⚠⚠⚠ LA MEDIANE SIGNEE DES MINIMA S'ANNULE PAR SYMETRIE, ET LA LIRE COMME UN ACCORD EST UNE
    # FAUTE QUE J'AI FAITE. Elle vaut 2,5° pendant que la mediane ABSOLUE vaut 25,0° : les minima
    # sont disperses sur tout l'eventail, et leur moyenne tombe pres de zero parce que la
    # dispersion est symetrique — pas parce qu'ils s'accordent avec `101`. L'accord se juge donc
    # sur l'ecart ABSOLU, et le seuil est le pas de l'eventail (5° ici), pas un nombre choisi.
    pas_de_leventail = (2.0 * r.get("demi_angle_deg", DEMI_ANGLE_DEG)
                        / max(r.get("directions", DIRECTIONS) - 1, 1))
    r["resume"]["pas_de_leventail_deg"] = round(pas_de_leventail, 2)
    if dr.get("angle_du_minimum_ecart_absolu_median_deg") is not None:
        r["resume"]["ecart_absolu_median_du_minimum_deg"] = dr[
            "angle_du_minimum_ecart_absolu_median_deg"]
        r["resume"]["le_minimum_saccorde_avec_101"] = bool(
            dr["angle_du_minimum_ecart_absolu_median_deg"] <= 2.0 * pas_de_leventail)
    for cle in ("residu_sur_pile_fabriquee_um", "combien_de_fois_pire_que_la_pile_fabriquee",
                "le_modele_parallele_decrit_la_matiere"):
        if cle in dr:
            r["resume"][cle] = dr[cle]
    for cle in ("le_parallele_decrit_la_courbe", "lisotrope_decrit_la_courbe",
                "aucun_des_deux_ne_decrit_la_courbe", "seuil_de_description_um"):
        if cle in dr:
            r["resume"][cle] = dr[cle]
    if dr.get("rapport_median_de_100") is not None and ca.get("rapport_median_de_100") is not None:
        # ⭐⭐ L'ANOMALIE DE `100` ETAIT-ELLE L'INSTRUMENT ? On compare le rapport rendu par les
        # deux selecteurs sur les MEMES lectures : s'il bouge, l'anomalie est instrumentale.
        r["resume"]["rapport_avec_le_selecteur_de_100"] = ca["rapport_median_de_100"]
        r["resume"]["rapport_avec_le_selecteur_corrige"] = dr["rapport_median_de_100"]
        r["resume"]["un_sur_cos_attendu"] = dr.get("un_sur_cos_median")
        att = dr.get("un_sur_cos_median", 1.0)
        # ⚠⚠⚠ « LE SELECTEUR DEPLACE LE RAPPORT » N'EST PAS « L'ANOMALIE ETAIT L'INSTRUMENT », et
        # ma premiere version confondait les deux : elle repondait OUI des que la correction
        # rapprochait le rapport de sa prediction, meme d'un dixieme. Les deux sont publies
        # separement, et le second exige que l'ecart RESTANT tombe sous la resolution.
        r["resume"]["de_combien_le_selecteur_deplace_le_rapport"] = round(
            dr["rapport_median_de_100"] - ca["rapport_median_de_100"], 3)
        r["resume"]["ecart_restant_a_la_prediction"] = round(
            dr["rapport_median_de_100"] - att, 3)
        # ⚠ La resolution d'un rapport de deux valeurs quantifiees au cran de 8,65 µm sur ~173
        # vaut environ 7 % : c'est la borne sous laquelle un ecart n'est plus lisible.
        cran = r.get("cran_du_balayage_um", 8.65)
        reso = 2.0 * cran / max(dr.get("pas_du_modele_parallele_median_um", 173.0), 1e-9)
        r["resume"]["resolution_du_rapport"] = round(reso, 3)
        r["resume"]["lanomalie_de_100_survit_a_la_correction"] = bool(
            abs(dr["rapport_median_de_100"] - att) > reso)
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    s = r["resume"]
    print(f"{r['fragment']} · éventail de {r['directions']} directions sur ±{r['demi_angle_deg']}° "
          f"autour de la normale de `101` · {s['bandes']} bandes, {s['cellules']} cellules "
          f"({s['cellules_sans_direction']} sans direction)")
    print("\n              cellules  parallèle gagne  gain médian  résidu ∥  résidu iso  "
          "minimum   amplitude")
    for nom in ("calibre", "deux_roles"):
        d = r.get(nom, {})
        if not d.get("cellules_decidables"):
            continue
        print(f"  {nom:>11}  {d['cellules_decidables']:8d}  "
              f"{d['part_ou_le_parallele_gagne']:15.3f}  "
              f"{d['gain_median_du_modele_parallele']:11.3f}  "
              f"{d['residu_parallele_median_um']:8.2f}  {d['residu_isotrope_median_um']:10.2f}  "
              f"{d.get('angle_du_minimum_median_deg', float('nan')):7.2f}°  "
              f"{d.get('amplitude_mediane_um', float('nan')):9.1f}")
    print(f"\nLES DEUX POINTS DE `100`, RELUS SUR LES MÊMES LECTURES")
    for nom in ("calibre", "deux_roles"):
        d = r.get(nom, {})
        if d.get("rapport_median_de_100") is None:
            continue
        print(f"  {nom:>11} : rapport rayon/normale {d['rapport_median_de_100']:.3f} "
              f"contre {d['un_sur_cos_median']:.3f} prédit par 1/cos "
              f"({d['cellules_a_deux_points']} cellules)")
    if "lanomalie_de_100_survit_a_la_correction" in s:
        print(f"   le sélecteur déplace le rapport de "
              f"{s['de_combien_le_selecteur_deplace_le_rapport']:+.3f} ; il reste "
              f"{s['ecart_restant_a_la_prediction']:+.3f} à la prédiction, pour une résolution "
              f"de {s['resolution_du_rapport']:.3f}")
        print(f"   ★ l'anomalie de `100` SURVIT à la correction : "
              f"{s['lanomalie_de_100_survit_a_la_correction']}")
    if "aucun_des_deux_ne_decrit_la_courbe" in s:
        print(f"\n⚠⚠ L'UN DES DEUX MODÈLES DÉCRIT-IL SEULEMENT LA COURBE ? (seuil : "
              f"{s['seuil_de_description_um']} µm, le tiers de l'amplitude)")
        print(f"   parallèle : {s['le_parallele_decrit_la_courbe']} · "
              f"isotrope : {s['lisotrope_decrit_la_courbe']} · "
              f"AUCUN DES DEUX : {s['aucun_des_deux_ne_decrit_la_courbe']}")
    if "combien_de_fois_pire_que_la_pile_fabriquee" in s:
        print(f"\n⚠⚠⚠ LE REPÈRE DU RÉSIDU EST LA PILE FABRIQUÉE, PAS L'AMPLITUDE : le même "
              f"instrument")
        print(f"   ajuste une pile CONNUE à {s['residu_sur_pile_fabriquee_um']} µm et la matière "
              f"à {r['deux_roles']['residu_parallele_median_um']} µm,")
        print(f"   soit ×{s['combien_de_fois_pire_que_la_pile_fabriquee']} pire. Le modèle "
              f"décrit-il la matière ? {s['le_modele_parallele_decrit_la_matiere']}")
    print(f"\n★★★ LA MATIÈRE EST-ELLE UN EMPILEMENT PARALLÈLE ? "
          f"{'OUI' if s['la_matiere_est_un_empilement_parallele'] else 'NON'}")
    d = r.get("deux_roles", {})
    if d.get("directions_au_minimum_mediane") is not None:
        print(f"   ⚠ {d['directions_au_minimum_mediane']:.1f} direction(s) au minimum sur "
              f"{d['directions_lues_mediane']:.1f} lues — une courbe plate en aurait beaucoup")
    if "le_minimum_saccorde_avec_101" in s:
        print(f"\n⚠⚠⚠ LE MINIMUM S'ACCORDE-T-IL AVEC `101` ? "
              f"{s['le_minimum_saccorde_avec_101']}")
        print(f"   médiane SIGNÉE {d['angle_du_minimum_median_deg']:+.2f}° mais médiane ABSOLUE "
              f"{s['ecart_absolu_median_du_minimum_deg']:.2f}°, pour un pas d'éventail de "
              f"{s['pas_de_leventail_deg']:.1f}°")
        print("   → une médiane signée près de zéro sur une distribution DISPERSÉE se lit comme "
              "un accord")
        print("     alors qu'elle n'est que la symétrie de la dispersion. C'est l'écart ABSOLU "
              "qui juge.")

    c = r.get("controle_fabrique", {})
    for e in c.get("empilements", []):
        j = e.get("ajustement_juste", {})
        # ⚠ L'affichage est lance par la batterie sur des fixtures partielles : il lit avec `.get`
        # plutot que d'exiger des champs, sinon la batterie planterait sur sa propre fixture au
        # lieu de garder ce que l'utilisateur voit — la lecon de `93`.
        if not j.get("decidable") or "gain_du_modele_parallele" not in j:
            continue
        print(f"\nEMPILEMENT FABRIQUÉ à {e['obliquite_deg']:.0f}° — gain "
              f"×{j['gain_du_modele_parallele']}, minimum à "
              f"{e.get('minimum', {}).get('angle_du_minimum_deg')}°, écart à p₀/cos "
              f"{e.get('ecart_median_a_la_prediction_um')} µm")
    if c.get("tournantes"):
        print("\nPILE FABRIQUÉE QUI TOURNE — l'explication la plus plausible, réfutée")
        for t in c["tournantes"]:
            print(f"   {t['rotation_deg_par_100um']:5.1f}°/100 µm "
                  f"({t['rotation_sur_la_sonde_deg']:5.1f}° sur la sonde) : "
                  f"normale {t['le_long_de_la_normale']:6.1f} · à 34° "
                  f"{t['a_trente_quatre_degres']:6.1f} · rapport {t['rapport']:.3f}")
        print(f"   ★ le rapport MONTE avec la rotation : "
              f"{c.get('le_rapport_monte_avec_la_rotation')} — une orientation incohérente "
              f"n'écrase donc PAS le rapport vers un")
    for cle, nom in (("linstrument_voit_lanisotropie", "l'instrument voit l'anisotropie"),
                     ("le_minimum_tombe_sur_la_normale", "le minimum tombe sur la normale"),
                     ("une_fausse_normale_fait_perdre_le_modele",
                      "une fausse normale fait perdre le modèle")):
        if cle in c:
            print(f"   ★ {nom} : {c[cle]}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === L'EVENTAIL EST BIEN LE PLAN QU'ON CROIT ============================================
    u = np.array([0.0, 0.0, 1.0])
    w = np.array([0.0, 1.0, 1.0])
    ang, dirs = eventail(u, w, 50.0, 21)
    v("l'éventail rend autant de directions que demandé", len(ang) == 21 and len(dirs) == 21)
    v("... centré sur la normale, qui est la direction d'angle nul",
      float(np.abs(dirs[10] @ u)) > 0.9999, f"{float(dirs[10] @ u):.6f}")
    v("... et toutes ses directions sont unitaires",
      float(np.max(np.abs(np.linalg.norm(dirs, axis=1) - 1.0))) < 1e-9)
    # ⚠⚠ LE PLAN DOIT CONTENIR LES DEUX DIRECTIONS, sinon l'angle rendu n'est pas celui qu'on lit.
    normale_du_plan = np.cross(dirs[0], dirs[-1])
    v("... et le plan de l'éventail contient le rayon",
      abs(float(normale_du_plan @ w)) < 1e-9, f"{float(normale_du_plan @ w):.2e}")
    # ⚠ Rayon colineaire a la normale : le plan n'existe pas, et il faut le DIRE.
    vide, _ = eventail(u, u * 3.0, 50.0, 21)
    v("un rayon colinéaire à la normale rend un éventail VIDE, pas un plan arbitraire",
      len(vide) == 0)
    v("l'angle du rayon est mesuré depuis la normale",
      abs(angle_du_rayon(u, w) - 45.0) < 1e-6, f"{angle_du_rayon(u, w):.3f}°")
    # ⚠⚠⚠ LA NORMALE EST ORIENTEE VERS LE RAYON, ET C'EST LE CONTROLE QUI MANQUAIT. Un vecteur
    # propre n'a pas de sens ; sans orientation, une cellule sur deux voit son eventail bascule et
    # le rayon tomber hors de portee. Mesure avant correction : 61 % des cellules.
    v("une normale de signe opposé rend le MÊME angle de rayon",
      abs(angle_du_rayon(-u, w) - angle_du_rayon(u, w)) < 1e-9,
      f"{angle_du_rayon(-u, w):.3f}° contre {angle_du_rayon(u, w):.3f}°")
    a_p, d_p = eventail(u, w, 50.0, 21)
    a_m, d_m = eventail(-u, w, 50.0, 21)
    v("... et le MÊME éventail, direction pour direction",
      float(np.max(np.abs(d_p - d_m))) < 1e-12, f"écart max {float(np.max(np.abs(d_p - d_m))):.2e}")
    # ⭐ Et l'angle rendu reste dans [0, 90] : au-dela, c'est le signe qui parle, pas la geometrie.
    v("... l'angle rendu restant dans [0, 90] quel que soit le signe",
      0.0 <= angle_du_rayon(-u, w) <= 90.0, f"{angle_du_rayon(-u, w):.3f}°")
    # ⚠⚠⚠ ET UN RAYON HORS DE L'EVENTAIL EST REFUSE, PAS ECRETE : ecreter publierait un angle de
    # FENETRE comme un angle de MATIERE.
    hors = _les_deux_points_de_100(np.linspace(-50.0, 50.0, 21),
                                   [173.0] * 21, [False] * 21, 68.0)
    v("un rayon hors de l'éventail est refusé, pas écrêté sur le bord",
      hors["les_deux_points_de_100"] is None and hors.get("rayon_hors_de_leventail") is True,
      f"angle demandé {hors.get('angle_du_rayon_deg')}°")

    # === LE PROFIL D'UNE FAMILLE TOURNANTE ==================================================
    # ⭐⭐ A ROTATION NULLE IL DOIT REDONNER LA PILE DROITE, sinon la refutation qu'il porte
    # mesurerait sa propre erreur de mise en place.
    n = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    L = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(L)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(L, mu, sd).values())
    from le_balayage_rend_il_le_pas_injecte import choisir  # noqa: PLC0415
    for a0 in (0.0, 34.0, 45.0):
        p = profil_dune_famille_tournante(a0, 0.0, C.PAS_UM, float(L[-1]), n)
        lu, _, _, _ = choisir(M.profils_emboites(p.reshape(1, -1), L), L, mu, sd,
                              "deux_roles", barre)
        att = C.PAS_UM / np.cos(np.deg2rad(a0))
        v(f"à rotation nulle, une sonde à {a0:.0f}° lit p₀/cos",
          abs(float(lu[0]) - att) <= float(L[1] - L[0]), f"{float(lu[0]):.1f} pour {att:.1f}")

    # === LES DEUX MODELES, A ARMES EGALES ===================================================
    a = np.linspace(-50.0, 50.0, 21)
    # ⭐ Une courbe PARFAITEMENT parallele : le modele parallele doit gagner largement.
    p_par = list(173.0 / np.cos(np.deg2rad(a)))
    d = ajuster_les_deux_modeles(a, p_par, [False] * 21)
    v("sur une courbe p₀/cos, le modèle parallèle gagne",
      d["le_modele_parallele_gagne"] is True and d["gain_du_modele_parallele"] > 3.0,
      f"×{d['gain_du_modele_parallele']}")
    # ⭐⭐⭐ ET SUR UNE COURBE PLATE, IL DOIT PERDRE. Sans ce controle le verdict serait un oui
    # deguise : une courbe a un parametre bat souvent une constante par accident.
    d = ajuster_les_deux_modeles(a, [190.0] * 21, [False] * 21)
    v("... et sur une courbe plate, il perd",
      d["le_modele_parallele_gagne"] is False, f"×{d['gain_du_modele_parallele']}")
    # ⚠⚠ LE CONTROLE NEGATIF : une NORMALE FAUSSE doit faire perdre le modele parallele.
    d = ajuster_les_deux_modeles(a, p_par, [False] * 21, decalage_deg=40.0)
    v("une normale fausse fait perdre le modèle parallèle",
      d["le_modele_parallele_gagne"] is False, f"×{d['gain_du_modele_parallele']}")
    # ⚠ Moins de quatre directions : il faut AVOUER, pas rendre un verdict.
    d = ajuster_les_deux_modeles(a[:3], p_par[:3], [False] * 3)
    v("moins de quatre directions rend « indécidable », pas un verdict",
      d["decidable"] is False, d.get("pourquoi", ""))
    # ⚠ Les butees sont ECARTEES, pas ecretees.
    ec = [False] * 21
    ec[0] = ec[-1] = True
    d = ajuster_les_deux_modeles(a, p_par, ec)
    v("les directions écartées ne comptent pas dans l'ajustement",
      d["utilisables"] == 19 and d["en_butee"] == 2, f"{d['utilisables']} utilisables")

    # === LA DIRECTION DU MINIMUM ============================================================
    m = direction_du_minimum(a, p_par, [False] * 21)
    v("le minimum d'une courbe p₀/cos tombe sur la normale",
      abs(m["angle_du_minimum_deg"]) < 1e-6, f"{m['angle_du_minimum_deg']}°")
    v("... et une seule direction y est",
      m["directions_au_minimum"] == 1, str(m["directions_au_minimum"]))
    # ⚠⚠⚠ UNE COURBE PLATE N'A PAS DE MINIMUM, et le dire est ce qui empeche de lire un tirage
    # comme une direction : toutes les directions y sont, et le compte le montre.
    m = direction_du_minimum(a, [190.0] * 21, [False] * 21)
    v("une courbe plate met TOUTES les directions au minimum, ce qui se voit au compte",
      m["directions_au_minimum"] == 21 and m["amplitude_um"] == 0.0,
      f"{m['directions_au_minimum']}/{m['directions_lues']}")

    # === LES DEUX POINTS DE `100` ===========================================================
    d = _les_deux_points_de_100(a, p_par, [False] * 21, 35.0)["les_deux_points_de_100"]
    v("les deux points de `100` sortent de la MÊME courbe",
      abs(d["pas_le_long_de_la_normale_um"] - 173.0) < 1e-6)
    # ⭐⭐ SUR UNE COURBE PARALLELE, LE RAPPORT DOIT EGALER 1/cos — c'est l'identite que `100`
    # teste, et elle doit tenir ici sinon la comparaison avec `100` ne voudrait rien dire.
    v("... et sur une courbe parallèle leur rapport égale 1/cos",
      abs(d["rapport_rayon_sur_normale"] - d["un_sur_cos"]) < 0.01,
      f"{d['rapport_rayon_sur_normale']} contre {d['un_sur_cos']}")
    # ⚠ Le rayon ne tombe pas sur une direction de l'eventail : la plus proche est prise et
    # l'ecart est PUBLIE, jamais interpole.
    # ⚠ Les DEUX angles sont publies, qu'ils different ou non : 35° tombe exactement sur une
    # direction de l'eventail, donc exiger qu'ils different serait exiger un desaccord. Ce qui
    # compte est qu'on puisse LIRE l'ecart, et un cas hors grille le montre.
    v("... et l'angle réellement pris est publié à côté de celui demandé",
      "angle_de_la_direction_prise_deg" in d and "angle_du_rayon_deg" in d,
      f"{d['angle_de_la_direction_prise_deg']}° pour {d['angle_du_rayon_deg']}° demandés")
    hg = _les_deux_points_de_100(a, p_par, [False] * 21, 33.0)["les_deux_points_de_100"]
    v("... et un angle hors de la grille est arrondi à la direction voisine, sans interpoler",
      hg["angle_de_la_direction_prise_deg"] == 35.0 and hg["angle_du_rayon_deg"] == 33.0,
      f"{hg['angle_de_la_direction_prise_deg']}° pour {hg['angle_du_rayon_deg']}° demandés")
    v("une direction écartée fait rendre « absent » plutôt qu'un rapport",
      _les_deux_points_de_100(a, p_par, ec, -50.0)["les_deux_points_de_100"] is None)

    # === LE CONTROLE FABRIQUE, SUR LE VRAI CHEMIN ===========================================
    cf = controle_fabrique(L, mu, sd, barre)
    v("l'instrument voit l'anisotropie d'une pile fabriquée",
      cf["linstrument_voit_lanisotropie"] is True)
    v("... son minimum tombe sur la normale", cf["le_minimum_tombe_sur_la_normale"] is True)
    v("... et une fausse normale lui fait perdre le modèle",
      cf["une_fausse_normale_fait_perdre_le_modele"] is True)
    # ⭐⭐⭐ LA REFUTATION QUE LE FICHIER PORTE : une famille TOURNANTE ne rapproche pas le
    # rapport de un, elle l'en ELOIGNE. L'incoherence d'orientation n'explique donc pas `100`.
    v("une famille qui tourne n'écrase PAS le rapport vers un",
      cf["une_famille_tournante_ecrase_le_rapport"] is False
      and cf["le_rapport_monte_avec_la_rotation"] is True,
      str([t["rapport"] for t in cf["tournantes"]]))

    # === L'AGREGATION =======================================================================
    def cel(pas, ang_rayon=35.0, pas_calibre=None):
        """Une cellule fabriquee. ⚠ `pas_calibre` permet de donner aux DEUX selecteurs des
        courbes differentes, ce qu'il faut pour eprouver le verdict sur l'anomalie de `100`."""
        e = [False] * len(pas)
        par = {"calibre": pas_calibre if pas_calibre is not None else pas, "deux_roles": pas}
        return {"angles_deg": list(a), "angle_du_rayon_deg": ang_rayon,
                "desaccord_des_moities_deg": 3.0, "part_admise": 1.0, "sorties": 0,
                **{nom: {"pas_um": par[nom],
                         "ajustement": ajuster_les_deux_modeles(a, par[nom], e),
                         "minimum": direction_du_minimum(a, par[nom], e),
                         **_les_deux_points_de_100(a, par[nom], e, ang_rayon)}
                   for nom in ("calibre", "deux_roles")}}
    # ⚠⚠ LE CONTROLE FABRIQUE FAIT PARTIE DE LA FIXTURE, et ma premiere version l'oubliait : le
    # verdict principal exige desormais un repere de residu, donc sans lui il repond NON pour une
    # raison qui n'est pas celle qu'on teste.
    faux = {"lignes": [{"de": 1, "a": 2, "rayon_mm": 5.0, "cellules": 2,
                        "detail": [cel(p_par), cel([190.0] * 21)]}],
            "cellules_sans_direction": 1, "directions": 21, "demi_angle_deg": 50.0,
            "fragment": "X", "pas_nominal_um": 173.0, "cran_du_balayage_um": 8.65,
            "controle_fabrique": {"empilements": [
                {"obliquite_deg": 25.0,
                 "ajustement_juste": {"decidable": True, "residu_parallele_um": 1.0}}]}}
    g = agreger(faux)
    v("l'agrégat rend la PART des cellules où le parallèle gagne, pas seulement un gain médian",
      g["deux_roles"]["part_ou_le_parallele_gagne"] == 0.5,
      str(g["deux_roles"]["part_ou_le_parallele_gagne"]))
    v("... et le verdict en découle plutôt que d'être décrété",
      g["resume"]["la_matiere_est_un_empilement_parallele"] is False)
    faux["lignes"][0]["detail"] = [cel(p_par), cel(p_par)]
    v("... et il peut dire OUI",
      agreger(faux)["resume"]["la_matiere_est_un_empilement_parallele"] is True)
    # ⭐⭐⭐ LE VERDICT QUI PASSE AVANT LES AUTRES : si AUCUN des deux modèles ne décrit la courbe,
    # dire « l'isotrope gagne » serait dire « le moins faux des deux faux ». Une courbe en dents
    # de scie n'est ni parallèle ni plate, et les deux résidus doivent le montrer.
    dents = list(190.0 + 60.0 * np.sign(np.sin(np.deg2rad(a) * 9.0)))
    faux["lignes"][0]["detail"] = [cel(dents), cel(dents)]
    g2 = agreger(faux)["resume"]
    v("une courbe qu'aucun des deux modèles ne décrit est dite telle quelle",
      g2["aucun_des_deux_ne_decrit_la_courbe"] is True,
      f"seuil {g2['seuil_de_description_um']} µm")
    v("... et le verdict « empilement parallèle » exige que le modèle DÉCRIVE la courbe",
      g2["la_matiere_est_un_empilement_parallele"] is False)
    faux["lignes"][0]["detail"] = [cel(p_par), cel(p_par)]
    g3 = agreger(faux)["resume"]
    v("... alors qu'une vraie courbe parallèle est bien décrite",
      g3["le_parallele_decrit_la_courbe"] is True
      and g3["aucun_des_deux_ne_decrit_la_courbe"] is False)
    v("les cellules sans direction sont comptées, pas remplacées",
      g["resume"]["cellules_sans_direction"] == 1)

    # === LE REPERE DU RESIDU EST LA PILE FABRIQUEE, PAS L'AMPLITUDE =========================
    # ⚠⚠⚠ C'EST UNE CORRECTION DE MA PREMIERE VERSION, qui comparait le residu a l'amplitude de la
    # courbe et laissait donc passer un ajustement vingt fois pire que sur une reponse connue. Le
    # repere d'un instrument est ce que CE MEME instrument obtient sur du connu.
    faux["lignes"][0]["detail"] = [cel(p_par), cel(p_par)]
    g4 = agreger(faux)["resume"]
    v("un ajustement aussi bon que sur la pile fabriquée décrit la matière",
      g4["le_modele_parallele_decrit_la_matiere"] is True,
      f"×{g4['combien_de_fois_pire_que_la_pile_fabriquee']}")
    # ⭐⭐⭐ ET LE VERDICT DOIT POUVOIR DIRE NON : une courbe qui bat marginalement une constante
    # tout en etant vingt fois pire que sur du connu n'est pas decrite par le modele.
    tordu = list(173.0 / np.cos(np.deg2rad(a))
                 + 25.0 * np.sign(np.sin(np.deg2rad(a) * 7.0)))
    faux["lignes"][0]["detail"] = [cel(tordu), cel(tordu)]
    g5 = agreger(faux)["resume"]
    v("... et le refuser quand l'ajustement est bien pire que sur du connu",
      g5["le_modele_parallele_decrit_la_matiere"] is False
      and g5["la_matiere_est_un_empilement_parallele"] is False,
      f"×{g5['combien_de_fois_pire_que_la_pile_fabriquee']}")

    # === LA MEDIANE SIGNEE D'UN ANGLE N'EST PAS UN ACCORD ==================================
    # ⚠⚠⚠ C'EST LA FAUTE QUE J'AI FAITE EN LISANT LA PREMIERE SORTIE : des minima DISPERSES et
    # symetriques ont une mediane signee proche de zero, ce qui se lit comme « ils tombent sur la
    # normale ». Seul l'ecart ABSOLU le dit. Deux jeux de fixtures l'eprouvent.
    faux["lignes"][0]["detail"] = [cel(p_par), cel(p_par)]
    g6 = agreger(faux)["resume"]
    v("des minima réellement sur la normale s'accordent avec `101`",
      g6["le_minimum_saccorde_avec_101"] is True,
      f"écart absolu médian {g6['ecart_absolu_median_du_minimum_deg']}°")
    # ⭐ Deux cellules dont les minima sont a -40° et +40° : mediane signee ZERO, accord FAUX.
    def decale(sens):
        c = list(173.0 / np.cos(np.deg2rad(a - sens * 40.0)))
        return cel(c)
    faux["lignes"][0]["detail"] = [decale(-1), decale(+1)]
    g7 = agreger(faux)["resume"]
    v("... mais des minima dispersés symétriquement ne s'accordent PAS, malgré une médiane nulle",
      g7["le_minimum_saccorde_avec_101"] is False,
      f"médiane signée {agreger(faux)['deux_roles']['angle_du_minimum_median_deg']:+.1f}° "
      f"mais absolue {g7['ecart_absolu_median_du_minimum_deg']}°")

    # === « LE SELECTEUR DEPLACE » N'EST PAS « L'ANOMALIE ETAIT L'INSTRUMENT » ================
    # ⚠⚠⚠ Ma premiere version repondait « l'anomalie etait l'instrument » des que la correction
    # rapprochait le rapport de sa prediction, meme d'un dixieme. Les deux sont desormais separes,
    # et le second exige que l'ecart RESTANT tombe sous la resolution du rapport.
    def deux(rap_cal, rap_dr, ang=30.0):
        """Deux courbes qui rendent des rapports rayon/normale CHOISIS, sur la meme geometrie.

        ⚠ Elles sont construites comme des COURBES et non comme des agregats ecrits a la main :
        `agreger` re-derive tout depuis les lignes, donc des dicts poses a la main seraient
        ecrases — ma premiere version faisait exactement cela et le test ne testait rien.
        """
        i_n = int(np.argmin(np.abs(a)))
        i_r = int(np.argmin(np.abs(a - ang)))
        courbes = {}
        for nom, rap in (("calibre", rap_cal), ("deux_roles", rap_dr)):
            c = list(173.0 / np.cos(np.deg2rad(a)))
            c[i_n], c[i_r] = 173.0, 173.0 * rap
            courbes[nom] = c
        return {**faux, "lignes": [{"de": 1, "a": 2, "rayon_mm": 5.0, "cellules": 1,
                                    "detail": [cel(courbes["deux_roles"], ang,
                                                   courbes["calibre"])]}]}
    # ⚠ Un rapport corrige qui atteint la prediction : l'anomalie ne survit PAS.
    q = agreger(deux(0.929, 1.155))["resume"]
    v("un rapport corrigé qui atteint la prédiction fait disparaître l'anomalie",
      q["lanomalie_de_100_survit_a_la_correction"] is False,
      f"reste {q['ecart_restant_a_la_prediction']:+.3f} pour une résolution de "
      f"{q['resolution_du_rapport']:.3f}")
    # ⭐ Et un rapport qui se rapproche SANS atteindre : l'anomalie survit, et le deplacement est
    # publie a cote pour qu'on ne lise pas l'un pour l'autre.
    q = agreger(deux(0.929, 1.000))["resume"]
    v("... alors qu'un rapprochement partiel la laisse survivre",
      q["lanomalie_de_100_survit_a_la_correction"] is True
      and q["de_combien_le_selecteur_deplace_le_rapport"] > 0.0,
      f"déplacement {q['de_combien_le_selecteur_deplace_le_rapport']:+.3f}, "
      f"reste {q['ecart_restant_a_la_prediction']:+.3f}")
    v("l'affichage tourne sur ce résultat", afficher(g) is None)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--demi", type=int, default=DEMI)
    p.add_argument("--fils", type=int, default=32)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = agreger(json.loads(a.json.read_text()))
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, demi=a.demi, bandes_max=a.bandes, fils=a.fils)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
