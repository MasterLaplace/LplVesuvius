#!/usr/bin/env python3
"""Deux marches jumelles, parties de la meme feuille, y sont-elles encore a l'arrivee ?

⭐⭐⭐⭐ C'EST LA QUESTION DE `R4-P26`, ET C'EST AUSSI LE TRAVAIL DE L'HUMAIN. Le graal demande de
transferer de spire a spire ; ce que l'humain corrige, `68` et `84` le disent, c'est le transfert
d'une spire a la suivante. Autrement dit : deux points voisins d'une meme feuille restent-ils sur
une meme feuille quand on les suit ? `128` a etabli qu'une pile PERIODIQUE ne porte aucune identite
de feuille — un decalage d'une feuille y rend un volume identique — donc sur une telle matiere deux
jumelles ne peuvent pas se separer. Le vrai rouleau n'est pas periodique, et `134` a fabrique la
premiere matiere qui ne l'est pas non plus.

⭐⭐⭐ LA MESURE A DEUX MOITIES QUI N'ONT PAS LE MEME SUJET. La DERIVE VRAIE est une propriete de la
MATIERE : deux sondes parties de la meme feuille finissent-elles sur la meme ? Elle n'est
connaissable que sur une fixture, dont la phase est analytique. La DERIVE LUE est une propriete de
l'INSTRUMENT : le compteur du marcheur, dont `136` a etabli qu'il est juste, voit-il cette
separation ? Les publier separement est ce qui empeche de lire l'aveuglement d'un compteur comme une
propriete du rouleau.

⚠⚠ LE CONTROLE DOIT PORTER DU BRUIT, SINON IL EST INCAPABLE D'ECHOUER. Sur une pile periodique SANS
bruit, deux jumelles parties de la meme phase lisent une matiere litteralement identique, donc leurs
marches le sont aussi et la derive vaut zero par construction — une verification satisfaite par
l'egalite de ses entrees. Le bruit est porte par le VOXEL (`126`), donc deux jumelles ecartees lisent
des voxels differents et peuvent diverger : c'est seulement alors que « elles ne se separent pas »
dit quelque chose.

⭐⭐ ET L'ERREUR DE COMPTAGE S'ANNULE ENTRE JUMELLES. Chaque marche compte les feuilles a quelques
pourcents pres (`136`) ; sur une pile periodique cette erreur est la MEME pour les deux, donc la
DIFFERENCE est exacte la ou chaque compte ne l'est pas. Une paire est donc un instrument plus fin
qu'une marche seule — ce qui est precisement l'argument de la PINCE.

⚠ L'ECART LATERAL EST PRIS DANS LE PLAN DE LA FEUILLE, perpendiculairement a la normale LUE au
depart — jamais au rayon, qui en est a vingt-cinq degres (`137`). Un ecart pris sur le rayon
poserait les deux jumelles sur deux feuilles differentes avant meme le premier pas.

⭐⭐⭐⭐ ET L'ECART BALAYE UN VOXEL, LE POINT QUI DECIDE. Une derive qui CROIT avec l'ecart lateral
est une propriete de la matiere ; une derive qui ne croit pas mais reste grande est une propriete
du marcheur. A UN voxel les deux cubes de lecture partagent quarante colonnes sur quarante et une :
si les jumelles derivent quand meme, le marcheur amplifie une difference de deux micrometres et
demi, et aucune paire ne peut plus arbitrer une question a l'echelle d'une feuille.

⚠⚠ LA PREMIERE CAMPAGNE N'AVAIT PAS CE POINT, et elle ne pouvait donc pas conclure : elle a
mesure que la derive du rouleau ne croit pas avec l'ecart (rho -0,1375, p 0,3974) — mais la fixture
dit que la derive LUE ne sait pas voir une croissance meme quand la derive VRAIE en a une (rho
+0,3409 sur la vraie, +0,1705 sur la lue). Une absence de tendance lue ne valait donc pas une
absence de structure. L'ecart d'un voxel ne demande pas une tendance : il demande si deux marches
qui lisent presque les memes voxels divergent.

⚠⚠ CE QUE CE FICHIER NE MESURE PAS, ET POURQUOI. J'ai d'abord cherche la REPRODUCTIBILITE de
l'espacement local — deux jumelles lisent-elles le meme espacement au meme pas ? La mesure est
confondue : sur une pile PERIODIQUE, dont l'espacement vrai est constant, les deux jumelles
correlent quand meme (r +0,14 a +0,33) a des ecarts ou elles ne partagent AUCUN voxel, parce
qu'elles sont comparees au meme rang de pas et que l'estimateur d'espacement depend de la phase ou
le pas tombe. Une correlation qui survit sur une matiere sans identite de feuille ne peut pas servir
a prouver qu'il y en a une.

Usage :
    uv run python src/nappe/deux_marches_jumelles_lisent_elles_la_meme_feuille.py --verifier
    uv run python src/nappe/deux_marches_jumelles_lisent_elles_la_meme_feuille.py \\
        --json docs/mesures/deux_marches_jumelles.json
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

DEMI = 20
LARGEUR_DU_CUBE_VX = 2 * DEMI + 1
# ⚠ Les ecarts sont choisis AUTOUR de la largeur du cube de lecture, pas au hasard : en deca les
# deux jumelles partagent des voxels, au-dela elles n'en partagent aucun. C'est la seule frontiere
# que la mesure ait, et elle vient de l'instrument.
# ⚠⚠ UN VOXEL EST LE POINT QUI DECIDE, et la premiere campagne ne l'avait pas. A cet ecart les
# deux cubes de lecture partagent quarante colonnes sur quarante et une : si les jumelles derivent
# QUAND MEME, ce n'est pas la matiere qui varie lateralement, c'est le marcheur qui amplifie une
# difference de deux micrometres et demi. Sans ce point, « la derive ne croit pas avec l'ecart »
# reste indecidable — la fixture montre que la derive LUE ne sait pas voir une croissance meme
# quand la derive VRAIE en a une (rho +0,34 sur la vraie, +0,17 sur la lue).
ECARTS_VX = (1, 4, 16, LARGEUR_DU_CUBE_VX, 2 * LARGEUR_DU_CUBE_VX)
PAS_MAX = 25
BRUIT = 8.0
AMPLITUDE_UM = 47.469
LONGUEUR_DONDE_UM = 393.6
POSITIONS = 10


def un_axe_dans_la_feuille(normale) -> np.ndarray:
    """Une direction unitaire DANS le plan de la feuille, choisie sans arbitraire.

    ⚠ Le premier axe du volume est projete hors de la normale ; s'il lui est colineaire — ce qui
    arrive quand la feuille est perpendiculaire a z — le deuxieme prend sa place. Deux appels sur
    la meme normale rendent donc le meme axe, ce qui est ce qui fait d'une paire un objet.
    """
    n = np.asarray(normale, dtype=float)
    # ⚠ Une normale degeneree est REFUSEE, jamais normalisee en douce : diviser par un plancher
    # rendrait un axe parfaitement valide pour une feuille qui n'existe pas, et la paire serait
    # posee dans une direction que rien n'a mesuree.
    norme = float(np.linalg.norm(n))
    if not np.isfinite(norme) or norme < 1e-9:
        raise ValueError("normale degeneree : aucun plan de feuille")
    n = n / norme
    for base in (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]),
                 np.array([0.0, 0.0, 1.0])):
        t = base - float(base @ n) * n
        if float(np.linalg.norm(t)) > 1e-6:
            return t / float(np.linalg.norm(t))
    raise ValueError("aucun axe dans la feuille : la normale n'est pas unitaire")


def poser_les_jumelles(lecteur, depart, ecart_vx: float, demi: int = DEMI,
                       fils: int = 1) -> dict:
    """Les deux departs et leurs directions, lues DANS la matiere — jamais donnees.

    ⚠⚠ LA MEME PROCEDURE SUR LA FIXTURE ET SUR LE ROULEAU. La tentation, sur une fixture, est de
    recaler la seconde jumelle sur la phase exacte de la premiere : c'est de la verite de terrain,
    et le rouleau n'en a pas. Le decalage de phase au depart est donc MESURE et publie la ou il est
    connaissable, jamais corrige.
    """
    from combien_de_pas_la_matiere_porte import direction_de_la_matiere  # noqa: PLC0415

    a = np.asarray(depart, dtype=float)
    na, des_a, _ = direction_de_la_matiere(lecteur, a, demi=demi, fils=fils)
    if na is None:
        return {"decidable": False, "pourquoi": "la matiere ne montre pas de direction au depart"}
    t = un_axe_dans_la_feuille(na)
    b = a + t * float(ecart_vx)
    nb, des_b, _ = direction_de_la_matiere(lecteur, b, demi=demi, fils=fils)
    if nb is None:
        return {"decidable": False, "pourquoi": "la matiere ne montre rien a la jumelle"}
    # ⚠ Le SENS d'un vecteur propre est arbitraire : la seconde direction est retournee vers la
    # premiere, sinon une jumelle partirait a l'oppose et la paire ne mesurerait rien.
    if float(nb @ na) < 0.0:
        nb = -nb
    # ⚠⚠ LE DESACCORD DES DEUX MOITIES DU CUBE EST PUBLIE PLUTOT QUE GARDE. C'est la garde de
    # `100` : au-dela de la barre calibree, la direction lue n'est pas digne de foi. Ici elle n'est
    # pas REFUSEE — refuser les departs douteux choisirait les paires qui se comportent bien, ce
    # qui est la facon la plus discrete de fabriquer un resultat — mais elle est portee par chaque
    # paire, pour qu'on puisse demander si la derive suit la mauvaise lecture du depart.
    return {"decidable": True, "a": a, "b": b, "na": na, "nb": nb,
            "axe_dans_la_feuille": t, "ecart_vx": float(ecart_vx),
            "desaccord_au_depart_deg": (None if des_a is None else round(float(des_a), 3)),
            "desaccord_a_la_jumelle_deg": (None if des_b is None else round(float(des_b), 3))}


def une_marche(lecteur, depart, direction0, barres, pas_max: int = PAS_MAX,
               demi: int = DEMI, memoire_du_cap: float = 0.75, fils: int = 1) -> dict:
    """Une marche, et le cumul de feuilles qu'elle croit avoir franchies.

    ⚠ Le cumul est la somme des `feuilles_franchies` PAS A PAS, la meme quantite que `136` a
    validee sur une fixture a direction imposee. Une fraction absente compte pour zero et le pas
    est compte a part : un cumul qui avalerait les absences se lirait comme une marche plus courte.
    """
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415

    longueurs, mu, sd, barre, barre_moities, barre_interstice, C = barres
    etapes = marcher(lecteur, np.asarray(depart, dtype=float), np.asarray(direction0, dtype=float),
                     longueurs, mu, sd, barre, barre_moities, barre_interstice, C.VOXEL_FIN_UM,
                     pas_max=pas_max, demi=demi, fils=fils, memoire_du_cap=memoire_du_cap)
    pas = [e for e in etapes if "avance_um" in e]
    p = np.asarray(depart, dtype=float).copy()
    cumul, cumuls, sans_fraction = 0.0, [], 0
    for e in pas:
        d = np.asarray(e["direction"], dtype=float)
        d = d / max(float(np.linalg.norm(d)), 1e-12)
        p = p + d * (float(e["avance_um"]) / C.VOXEL_FIN_UM)
        f = e.get("feuilles_franchies")
        if f is None:
            sans_fraction += 1
        else:
            cumul += float(f)
        cumuls.append(cumul)
    return {"pas": len(pas), "cumul_de_feuilles": cumuls, "pas_sans_fraction": sans_fraction,
            "position_fin": p, "feuilles": cumul}


def la_derive(a: dict, b: dict) -> dict:
    """L'ecart entre les deux comptes, pas par pas et a l'arrivee.

    ⭐⭐ C'est la quantite qui compte pour le graal : combien de feuilles separent, a l'arrivee,
    deux sondes parties de la meme. Un dérouleur qui transfere de spire a spire se decale d'autant.
    """
    n = min(a["pas"], b["pas"])
    if n < 1:
        return {"decidable": False, "pourquoi": "une des deux marches n'a fait aucun pas"}
    ca = np.asarray(a["cumul_de_feuilles"][:n])
    cb = np.asarray(b["cumul_de_feuilles"][:n])
    d = ca - cb
    return {"decidable": True, "pas_communs": n,
            "feuilles_a": round(float(ca[-1]), 3), "feuilles_b": round(float(cb[-1]), 3),
            "derive_lue": round(float(d[-1]), 3),
            "derive_lue_max": round(float(np.abs(d).max()), 3)}


def la_derive_vraie(lecteur, a: dict, b: dict, depart_a, depart_b) -> dict:
    """La derive que la MATIERE impose, lue dans la phase analytique de la fixture.

    ⚠ N'existe que sur une fixture : `_projection_um` divise par le pas est l'indice de feuille
    exact en tout point. Le rouleau n'a pas cet oracle, et c'est pourquoi la fixture porte
    l'argument.
    """
    if not hasattr(lecteur, "_projection_um"):
        return {"decidable": False, "pourquoi": "cette matiere n'a pas de phase analytique"}

    def phase(p):
        return float(lecteur._projection_um(  # noqa: SLF001
            np.asarray(p, dtype=float).reshape(1, 3))[0]) / lecteur.pas_um

    p0a, p0b = phase(depart_a), phase(depart_b)
    va = phase(a["position_fin"]) - p0a
    vb = phase(b["position_fin"]) - p0b
    # ⚠⚠ LE SENS DU GRADIENT DE PHASE EST ARBITRAIRE, et le confondre avec un sens de marche fait
    # rendre une traversee NEGATIVE la ou le compteur, lui, ne compte que des feuilles franchies.
    # Ma premiere version comparait `feuilles` a `va` signe et trouvait un compte de +8,47 pour
    # une traversee de -8,15. La direction que la matiere montre est un vecteur propre : son signe
    # ne dit rien. Les deux jumelles marchent dans le MEME sens (`poser_les_jumelles` retourne la
    # seconde vers la premiere), donc orienter sur la premiere rend les trois nombres comparables.
    sens = 1.0 if va >= 0.0 else -1.0
    va, vb = va * sens, vb * sens
    return {"decidable": True,
            "decalage_de_phase_au_depart": round((p0b - p0a) * sens, 4),
            "traversee_vraie_a": round(va, 3), "traversee_vraie_b": round(vb, 3),
            "derive_vraie": round(va - vb, 3),
            "erreur_de_comptage_a": round(a["feuilles"] - va, 3),
            "erreur_de_comptage_b": round(b["feuilles"] - vb, 3)}


def _barres():
    """Les barres calibrees dont le marcheur a besoin — les memes que la course."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    return (longueurs, mu, sd, barre, nul_du_tenseur(demi=DEMI)["accord_des_moities_p1_deg"],
            max(x["p99"] for x in C.accord_du_bruit_pur().values()), C)


def une_paire(lecteur, depart, ecart_vx: float, barres, pas_max: int = PAS_MAX,
              demi: int = DEMI, memoire_du_cap: float = 0.75, fils: int = 1) -> dict | None:
    """Une paire de jumelles : les poser, les marcher, lire leur derive."""
    pose = poser_les_jumelles(lecteur, depart, ecart_vx, demi=demi, fils=fils)
    if not pose["decidable"]:
        return None
    a = une_marche(lecteur, pose["a"], pose["na"], barres, pas_max, demi, memoire_du_cap, fils)
    b = une_marche(lecteur, pose["b"], pose["nb"], barres, pas_max, demi, memoire_du_cap, fils)
    d = la_derive(a, b)
    if not d["decidable"]:
        return None
    out = {"ecart_vx": float(ecart_vx), "ecart_um": round(float(ecart_vx) * 2.4, 1), **d,
           "pas_a": a["pas"], "pas_b": b["pas"],
           "desaccord_au_depart_deg": pose.get("desaccord_au_depart_deg"),
           "desaccord_a_la_jumelle_deg": pose.get("desaccord_a_la_jumelle_deg")}
    v = la_derive_vraie(lecteur, a, b, pose["a"], pose["b"])
    if v.get("decidable"):
        out.update({k: v[k] for k in v if k != "decidable"})
    return out


def sur_une_pile(amplitude_um: float, bruit: float = BRUIT, positions: int = POSITIONS,
                 ecarts=ECARTS_VX, pas_max: int = PAS_MAX, graine: int = 3) -> dict:
    """Les jumelles sur une pile fabriquee, a plusieurs ecarts et plusieurs positions.

    ⭐⭐⭐ DEUX PILES ET DEUX REPONSES CONNUES. A amplitude nulle la pile est PERIODIQUE : la
    matiere est une fonction de la phase seule, donc elle ne porte aucune identite de feuille et la
    derive VRAIE doit etre nulle — avec du bruit, donc sans que les deux entrees soient identiques.
    `par_feuille` a amplitude non nulle donne a chaque feuille son propre froissement : la matiere
    distingue la feuille n de la feuille n+1, donc la derive vraie doit CESSER d'etre nulle.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabriqueOndulee  # noqa: PLC0415

    barres = _barres()
    vol = VolumeFabriqueOndulee(barres[-1].PAS_UM, amplitude_um=amplitude_um,
                                longueur_donde_um=LONGUEUR_DONDE_UM, par_feuille=True,
                                bruit=bruit, graine=graine)
    rng = np.random.default_rng(1000 + int(graine))
    centres = [np.array([2000.0, 2000.0, 2000.0]) + rng.uniform(-400.0, 400.0, 3)
               for _ in range(positions)]
    lignes = []
    for ecart in ecarts:
        for c in centres:
            r = une_paire(vol, c, ecart, barres, pas_max=pas_max)
            if r is not None:
                lignes.append(r)
    return {"amplitude_um": amplitude_um, "bruit": bruit, "longueur_donde_um": LONGUEUR_DONDE_UM,
            "par_feuille": True, "positions": positions, "pas_max": pas_max,
            "paires": lignes, "resume": resumer(lignes)}


def resumer(lignes: list[dict]) -> dict:
    """La derive lue et, quand elle existe, la derive vraie — par ecart puis en tout."""
    if not lignes:
        return {"decidable": False, "pourquoi": "aucune paire"}
    out = {"decidable": True, "paires": len(lignes), "par_ecart": []}
    for ecart in sorted({x["ecart_vx"] for x in lignes}):
        lot = [x for x in lignes if x["ecart_vx"] == ecart]
        lu = np.abs([x["derive_lue"] for x in lot])
        bloc = {"ecart_vx": ecart, "ecart_um": lot[0]["ecart_um"], "paires": len(lot),
                "dans_le_cube_de_lecture": bool(ecart < LARGEUR_DU_CUBE_VX),
                "derive_lue_mediane": round(float(np.median(lu)), 3),
                "derive_lue_p90": round(float(np.percentile(lu, 90)), 3)}
        vrais = [x["derive_vraie"] for x in lot if "derive_vraie" in x]
        if vrais:
            v = np.abs(vrais)
            bloc.update({"derive_vraie_mediane": round(float(np.median(v)), 3),
                         "derive_vraie_p90": round(float(np.percentile(v, 90)), 3),
                         "decalage_au_depart_median": round(float(np.median(
                             np.abs([x["decalage_de_phase_au_depart"] for x in lot]))), 4)})
        out["par_ecart"].append(bloc)
    lu = np.abs([x["derive_lue"] for x in lignes])
    out["derive_lue_mediane"] = round(float(np.median(lu)), 3)
    out["derive_lue_p90"] = round(float(np.percentile(lu, 90)), 3)
    # ⭐⭐ LA PART DES PAIRES QUI DEPASSENT UNE FEUILLE, et c'est la forme qui compte pour le graal :
    # un derouleur n'a pas besoin de savoir de combien deux sondes se sont separees en moyenne, il a
    # besoin de savoir si elles sont encore sur la MEME feuille. Une mediane le cache, une part le
    # dit. ⚠ Une feuille n'est pas un seuil regle : c'est l'unite que le transfert de spire a spire
    # manipule.
    out["part_des_paires_au_dela_dune_feuille"] = round(float((lu > 1.0).mean()), 3)
    mx = np.array([x["derive_lue_max"] for x in lignes], dtype=float)
    bon = lu > 0.05
    if bon.any():
        # ⚠ Un rapport proche de un veut dire une divergence QUI SE CREUSE ; bien au-dessus, deux
        # marches qui se croisent en chemin. Ce n'est pas la meme panne pour un derouleur.
        out["max_sur_finale_median"] = round(float(np.median(mx[bon] / lu[bon])), 2)
    vrais = [x for x in lignes if "derive_vraie" in x]
    if vrais:
        v = np.abs([x["derive_vraie"] for x in vrais])
        out["derive_vraie_mediane"] = round(float(np.median(v)), 3)
        out["derive_vraie_p90"] = round(float(np.percentile(v, 90)), 3)
        e = np.abs([x["erreur_de_comptage_a"] for x in vrais]
                   + [x["erreur_de_comptage_b"] for x in vrais])
        out["erreur_de_comptage_mediane"] = round(float(np.median(e)), 3)
        out["traversee_mediane"] = round(float(np.median(
            [abs(x["traversee_vraie_a"]) for x in vrais])), 2)
    return out


def doù_vient_la_derive(lignes: list[dict]) -> dict:
    """La derive suit-elle l'ECART LATERAL, ou le DESACCORD au depart ?

    ⭐⭐⭐⭐ C'EST LA QUESTION QUI SEPARE LES DEUX LECTURES D'UNE MEME DERIVE. Si elle croit avec
    l'ecart lateral, elle est une propriete de la MATIERE : plus loin, moins la meme feuille. Si
    elle ne croit pas mais suit le desaccord des moities au depart, elle est une propriete de
    l'INSTRUMENT : une direction mal lue envoie la marche ailleurs. Et si elle ne suit ni l'un ni
    l'autre en restant grande, c'est que le marcheur amplifie une difference que rien ne mesure.

    ⚠⚠ ET L'ABSENCE DE CROISSANCE NE PROUVE RIEN TOUTE SEULE, ce que la fixture dit : sur la pile
    par feuille la derive VRAIE croit avec l'ecart (rho +0,34) et la derive LUE ne le voit pas
    (rho +0,17). L'instrument est donc trop grossier pour qu'un rho nul sur le rouleau vaille une
    absence. C'est pourquoi l'ecart d'UN voxel existe : il ne demande pas une tendance, il demande
    si deux marches qui lisent presque les memes voxels derivent quand meme.
    """
    from scipy import stats  # noqa: PLC0415

    if len(lignes) < 6:
        return {"decidable": False, "pourquoi": f"{len(lignes)} paire(s)"}
    e = np.asarray([x["ecart_vx"] for x in lignes], dtype=float)
    lu = np.abs([x["derive_lue"] for x in lignes])
    out = {"decidable": True, "paires": len(lignes)}
    rho, p = stats.spearmanr(e, lu)
    out.update({"rho_ecart_lateral": round(float(rho), 4), "p_ecart_lateral": round(float(p), 5),
                "la_derive_croit_avec_lecart": bool(p < 0.05 and rho > 0.0)})
    vrais = [x for x in lignes if "derive_vraie" in x]
    if len(vrais) >= 6:
        rv, pv = stats.spearmanr([x["ecart_vx"] for x in vrais],
                                 np.abs([x["derive_vraie"] for x in vrais]))
        out.update({"rho_ecart_lateral_sur_la_vraie": round(float(rv), 4),
                    "p_ecart_lateral_sur_la_vraie": round(float(pv), 5),
                    "la_derive_VRAIE_croit_avec_lecart": bool(pv < 0.05 and rv > 0.0)})
    des = [x for x in lignes if x.get("desaccord_au_depart_deg") is not None]
    if len(des) >= 6:
        rd, pd_ = stats.spearmanr([max(x["desaccord_au_depart_deg"],
                                       x["desaccord_a_la_jumelle_deg"] or 0.0) for x in des],
                                  np.abs([x["derive_lue"] for x in des]))
        out.update({"rho_desaccord_au_depart": round(float(rd), 4),
                    "p_desaccord_au_depart": round(float(pd_), 5),
                    "la_derive_suit_le_desaccord": bool(pd_ < 0.05 and rd > 0.0)})
    au_plus_pres = [x for x in lignes if x["ecart_vx"] == min(e)]
    if au_plus_pres:
        out["ecart_le_plus_petit_vx"] = float(min(e))
        out["derive_a_lecart_le_plus_petit"] = round(float(np.median(
            np.abs([x["derive_lue"] for x in au_plus_pres]))), 3)
    return out


def le_compteur_voit_il_la_separation(lignes: list[dict]) -> dict:
    """La derive LUE suit-elle la derive VRAIE, paire par paire ?

    ⚠⚠ DEUX VERDICTS SEPARES, ET ILS NE DISENT PAS LA MEME CHOSE. Le RANG dit si le compteur voit
    l'ordre des separations ; le NIVEAU dit s'il en voit la taille. Un compteur qui rangerait
    parfaitement les paires en sous-estimant chaque derive de moitie serait utile et faux, et le
    dire d'un seul chiffre le cacherait.
    """
    from scipy import stats  # noqa: PLC0415

    lot = [x for x in lignes if "derive_vraie" in x]
    if len(lot) < 6:
        return {"decidable": False, "pourquoi": f"{len(lot)} paire(s) a verite connue"}
    v = np.abs([x["derive_vraie"] for x in lot])
    lu = np.abs([x["derive_lue"] for x in lot])
    if float(np.std(v)) < 1e-9 or float(np.std(lu)) < 1e-9:
        return {"decidable": True, "paires": len(lot), "rho_de_spearman": None, "p_du_rang": None,
                "aucune_variation": True,
                "derive_vraie_mediane": round(float(np.median(v)), 3),
                "derive_lue_mediane": round(float(np.median(lu)), 3),
                "le_compteur_voit_le_rang": False, "le_compteur_voit_le_niveau": False}
    rho, p = stats.spearmanr(v, lu)
    d = lu - v
    p_app = float(stats.wilcoxon(d).pvalue) if np.any(d) else None
    return {"decidable": True, "paires": len(lot), "aucune_variation": False,
            "rho_de_spearman": round(float(rho), 4), "p_du_rang": round(float(p), 6),
            "derive_vraie_mediane": round(float(np.median(v)), 3),
            "derive_lue_mediane": round(float(np.median(lu)), 3),
            "ecart_median": round(float(np.median(d)), 3),
            "p_apparie": None if p_app is None else round(p_app, 5),
            "le_compteur_voit_le_rang": bool(p < 0.05 and rho > 0.0),
            "le_compteur_voit_le_niveau": bool(p_app is None or p_app >= 0.05)}


def sur_le_rouleau(bandes_max: int | None = None, ecarts=ECARTS_VX, pas_max: int = PAS_MAX,
                   par_bande: int = 1, fils: int = 64) -> dict:
    """Les jumelles sur le vrai volume, aux departs de `107`.

    ⚠ Le rouleau n'a pas de phase analytique, donc SEULE la derive lue y est connaissable. C'est
    pourquoi les deux piles fabriquees portent l'argument : elles calibrent ce qu'une derive lue
    vaut quand la matiere ne distingue pas ses feuilles, et quand elle les distingue.
    """
    from le_compte_suit_il_le_pas import departs_de_107  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    barres = _barres()
    C = barres[-1]
    # ⚠⚠ TOUTES LES BANDES SONT DEMANDEES, PUIS LA SELECTION SE FAIT APRES. `departs_de_107`
    # estime l'axe sur la CONCATENATION des nuages qu'on lui laisse : en lui passant `bandes_max`
    # on lui ferait poser un autre axe, donc d'autres radiaux et d'autres departs que ceux des
    # courses de `133`. Le premier essai a rendu « cache incomplet » sur une seule bande, ce qui
    # l'a dit tout de suite ; a quatre bandes il aurait repondu, et faux.
    dep = departs_de_107(None)
    if "message" in dep:
        return {"message": dep["message"]}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}
    brut = json.loads((RACINE / "docs" / "mesures" / "le_compte_suit_il_le_pas.json").read_text())\
        if (RACINE / "docs" / "mesures" / "le_compte_suit_il_le_pas.json").is_file() else {}
    rayons = {(int(x["de"]), int(x["a"])): x.get("rayon_mm") for x in brut.get("lignes", [])}
    cles = list(dep["par_bande"])[:bandes_max] if bandes_max else list(dep["par_bande"])
    taches = [(cle, j, ecart) for cle in cles
              for j in range(min(par_bande, len(dep["par_bande"][cle]["departs"])))
              for ecart in ecarts]
    t0 = maintenant()
    lignes = []
    for i, (cle, j, ecart) in enumerate(taches):
        depart = dep["par_bande"][cle]["departs"][j]
        r = une_paire(vol, depart, ecart, barres, pas_max=pas_max, fils=fils)
        if r is not None:
            lignes.append({**r, "bande": [int(cle[0]), int(cle[1])],
                           "rayon_mm": rayons.get(cle)})
        avancement(i + 1, len(taches), "paires sur le rouleau", t0)
    return {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "pas_max": pas_max,
            "paires": lignes, "resume": resumer(lignes),
            "secondes": round(maintenant() - t0, 1)}


def les_trois_matieres_sont_elles_distinctes(periodique: dict, par_feuille: dict,
                                             rouleau: dict | None) -> dict:
    """Les trois lots de derives lues viennent-ils de la meme loi ?

    ⚠⚠ COMPARER DEUX MEDIANES N'EST PAS COMPARER DEUX LOTS, et ici ca compte : la derive de la
    pile periodique a une queue LOURDE (mediane 0,255 mais p90 au-dela de sept feuilles), donc une
    mediane trois fois plus grande ailleurs pourrait n'etre que la meme loi echantillonnee
    autrement. Un test de rang sur les lots entiers repond, et il peut ne rien trouver.

    ⚠ Le test est UNILATERAL — « plus grand que » — parce que la question l'est : on demande si une
    matiere separe ses jumelles DAVANTAGE, pas si elle en differe.
    """
    from scipy import stats  # noqa: PLC0415

    lots = {}
    for nom, bloc in (("periodique", periodique), ("par_feuille", par_feuille),
                      ("rouleau", rouleau)):
        if bloc and bloc.get("paires"):
            lots[nom] = np.abs([x["derive_lue"] for x in bloc["paires"]])
    if len(lots) < 2:
        return {"decidable": False, "pourquoi": f"{len(lots)} lot(s)"}
    out = {"decidable": True, "lots": {k: len(v) for k, v in lots.items()}, "comparaisons": []}
    for haut, bas in (("rouleau", "periodique"), ("rouleau", "par_feuille"),
                      ("par_feuille", "periodique")):
        if haut not in lots or bas not in lots:
            continue
        p_ = float(stats.mannwhitneyu(lots[haut], lots[bas], alternative="greater").pvalue)
        out["comparaisons"].append({
            "plus_grand": haut, "que": bas, "p_de_rang": float(f"{p_:.3g}"),
            "mediane_du_plus_grand": round(float(np.median(lots[haut])), 3),
            "mediane_de_lautre": round(float(np.median(lots[bas])), 3),
            "il_separe_davantage": bool(p_ < 0.05)})
    return out


def juger(periodique: dict, par_feuille: dict, rouleau: dict | None) -> dict:
    """Ce que les trois matieres disent ensemble.

    ⭐⭐⭐⭐ LES DEUX PILES SONT LES DEUX BOUTS D'UNE ECHELLE, ET LE ROULEAU SE LIT DESSUS. Une
    derive lue seule ne veut rien dire ; entre « ce que rend une matiere qui ne distingue pas ses
    feuilles » et « ce que rend une matiere qui les distingue », elle se lit.

    ⚠⚠ ET LE PLANCHER N'EST PAS ZERO. Sur la pile periodique, une paire sur dix se separe quand
    meme de plus d'une feuille, par le seul bruit : deux jumelles qui tombent d'accord sur tout
    sauf un pas comptent un pas de plus l'une que l'autre. Une paire isolee ne decide donc rien —
    c'est une distribution qui decide, et le p90 est publie a cote de la mediane pour ca.
    """
    rp, rf = periodique.get("resume", {}), par_feuille.get("resume", {})
    if not (rp.get("decidable") and rf.get("decidable")):
        return {"decidable": False, "pourquoi": "une des deux piles n'a rendu aucune paire"}
    out = {"decidable": True,
           "derive_vraie_periodique": rp.get("derive_vraie_mediane"),
           "derive_vraie_par_feuille": rf.get("derive_vraie_mediane"),
           "derive_lue_periodique": rp.get("derive_lue_mediane"),
           "derive_lue_par_feuille": rf.get("derive_lue_mediane"),
           "plancher_du_bruit_p90_periodique": rp.get("derive_lue_p90"),
           "traversee_mediane_periodique": rp.get("traversee_mediane"),
           "traversee_mediane_par_feuille": rf.get("traversee_mediane")}
    # ⭐⭐ Les deux verdicts de la fixture, calcules : la pile periodique NE SEPARE PAS, et la pile
    # par feuille SEPARE. Le second sans le premier serait satisfait par un instrument qui separe
    # tout le monde.
    vp, vf = rp.get("derive_vraie_mediane"), rf.get("derive_vraie_mediane")
    if vp is not None and vf is not None:
        out["la_pile_periodique_ne_separe_pas"] = bool(vp < 0.1)
        out["la_pile_par_feuille_separe"] = bool(vf > 5.0 * max(vp, 1e-9))
        out["combien_de_fois_plus"] = round(float(vf / max(vp, 1e-9)), 1)
    if rouleau and rouleau.get("resume", {}).get("decidable"):
        rr = rouleau["resume"]
        out["derive_lue_du_rouleau"] = rr.get("derive_lue_mediane")
        out["derive_lue_du_rouleau_p90"] = rr.get("derive_lue_p90")
        lp, lf = rp.get("derive_lue_mediane"), rf.get("derive_lue_mediane")
        lr = rr.get("derive_lue_mediane")
        if None not in (lp, lf, lr):
            # ⚠ Le rouleau est place SUR l'echelle des deux piles, jamais juge dans l'absolu :
            # zero veut dire « comme une matiere periodique », un « comme une matiere qui distingue
            # ses feuilles ». Au-dela d'un, il en distingue davantage qu'elle.
            out["ou_tombe_le_rouleau_sur_lechelle"] = round(float((lr - lp) / max(lf - lp, 1e-9)), 3)
    return out


def mesurer(bandes_max: int | None = None, positions: int = POSITIONS, pas_max: int = PAS_MAX,
            avec_rouleau: bool = True, par_bande: int = 1, fils: int = 64) -> dict:
    periodique = sur_une_pile(0.0, positions=positions, pas_max=pas_max)
    par_feuille = sur_une_pile(AMPLITUDE_UM, positions=positions, pas_max=pas_max)
    out = {"ecarts_vx": list(ECARTS_VX), "largeur_du_cube_vx": LARGEUR_DU_CUBE_VX,
           "pas_max": pas_max, "bruit": BRUIT,
           "la_pile_periodique": periodique, "la_pile_par_feuille": par_feuille,
           "le_compteur_voit_il_la_separation": {
               "sur_la_pile_periodique": le_compteur_voit_il_la_separation(periodique["paires"]),
               "sur_la_pile_par_feuille": le_compteur_voit_il_la_separation(par_feuille["paires"])},
           "dou_vient_la_derive": {
               "sur_la_pile_periodique": doù_vient_la_derive(periodique["paires"]),
               "sur_la_pile_par_feuille": doù_vient_la_derive(par_feuille["paires"])}}
    rouleau = None
    if avec_rouleau:
        rouleau = sur_le_rouleau(bandes_max=bandes_max, pas_max=pas_max, par_bande=par_bande,
                                 fils=fils)
        out["le_rouleau"] = rouleau
        if "message" in rouleau:
            rouleau = None
        else:
            out["dou_vient_la_derive"]["sur_le_rouleau"] = doù_vient_la_derive(rouleau["paires"])
    out["les_trois_matieres_sont_elles_distinctes"] = les_trois_matieres_sont_elles_distinctes(
        periodique, par_feuille, rouleau)
    out["juger"] = juger(periodique, par_feuille, rouleau)
    return out


def reagreger(chemin: Path) -> dict:
    """Recalculer tous les verdicts depuis les PAIRES deja mesurees, sans remarcher.

    ⭐⭐⭐ IL EXISTE PARCE QU'UNE CAMPAGNE COUTE QUATRE-VINGTS MINUTES DE LECTURE. Ajouter une
    question aux memes paires ne demande pas de remarcher, et remarcher pour ca donnerait d'autres
    marches — donc une autre mesure, pas la meme enrichie. C'est le `--reagreger` de `133`.
    """
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if "message" in d:
        return d
    for cle in ("la_pile_periodique", "la_pile_par_feuille", "le_rouleau"):
        bloc = d.get(cle)
        if bloc and bloc.get("paires"):
            bloc["resume"] = resumer(bloc["paires"])
    per, pf = d.get("la_pile_periodique") or {}, d.get("la_pile_par_feuille") or {}
    rou = d.get("le_rouleau") or None
    if rou and "message" in rou:
        rou = None
    d["le_compteur_voit_il_la_separation"] = {
        "sur_la_pile_periodique": le_compteur_voit_il_la_separation(per.get("paires", [])),
        "sur_la_pile_par_feuille": le_compteur_voit_il_la_separation(pf.get("paires", []))}
    d["dou_vient_la_derive"] = {
        "sur_la_pile_periodique": doù_vient_la_derive(per.get("paires", [])),
        "sur_la_pile_par_feuille": doù_vient_la_derive(pf.get("paires", []))}
    if rou:
        d["dou_vient_la_derive"]["sur_le_rouleau"] = doù_vient_la_derive(rou["paires"])
    d["les_trois_matieres_sont_elles_distinctes"] = les_trois_matieres_sont_elles_distinctes(
        per, pf, rou)
    d["juger"] = juger(per, pf, rou)
    return d


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    for cle, nom in (("la_pile_periodique", "pile PÉRIODIQUE (aucune identité de feuille)"),
                     ("la_pile_par_feuille", "pile PAR FEUILLE (la matière les distingue)"),
                     ("le_rouleau", "le ROULEAU")):
        bloc = r.get(cle)
        if not bloc:
            continue
        if "message" in bloc:
            print(f"\n{nom} : ⚠ {bloc['message']}")
            continue
        s = bloc.get("resume", {})
        if not s.get("decidable"):
            print(f"\n{nom} : ⚠ {s.get('pourquoi')}")
            continue
        print(f"\n{nom} · {s['paires']} paires")
        for b in s["par_ecart"]:
            dedans = "dans le cube" if b["dans_le_cube_de_lecture"] else "hors du cube"
            vrai = (f" · vraie {b['derive_vraie_mediane']} (p90 {b['derive_vraie_p90']})"
                    if "derive_vraie_mediane" in b else "")
            dec = (f" · départ décalé de {b['decalage_au_depart_median']}"
                   if "decalage_au_depart_median" in b else "")
            print(f"   écart {b['ecart_vx']:>5.0f} vx ({b['ecart_um']:>6.1f} µm, {dedans}) · "
                  f"{b['paires']:>2} paires · dérive lue {b['derive_lue_mediane']} "
                  f"(p90 {b['derive_lue_p90']}){vrai}{dec}")
        if "derive_vraie_mediane" in s:
            print(f"   ★ dérive VRAIE {s['derive_vraie_mediane']} (p90 {s['derive_vraie_p90']}) · "
                  f"LUE {s['derive_lue_mediane']} (p90 {s['derive_lue_p90']}) · erreur de comptage "
                  f"{s['erreur_de_comptage_mediane']} sur {s['traversee_mediane']} feuilles")
        else:
            print(f"   ★ dérive LUE {s['derive_lue_mediane']} (p90 {s['derive_lue_p90']})")
    for cle, nom in (("sur_la_pile_periodique", "périodique"),
                     ("sur_la_pile_par_feuille", "par feuille")):
        c = r.get("le_compteur_voit_il_la_separation", {}).get(cle, {})
        if c.get("decidable") and not c.get("aucune_variation"):
            print(f"\nle compteur sur la pile {nom} : rho {c['rho_de_spearman']:+} p "
                  f"{c['p_du_rang']} · vraie {c['derive_vraie_mediane']} contre lue "
                  f"{c['derive_lue_mediane']}, p apparié {c['p_apparie']}")
    for cle, nom in (("sur_la_pile_periodique", "périodique"),
                     ("sur_la_pile_par_feuille", "par feuille"), ("sur_le_rouleau", "le rouleau")):
        o = (r.get("dou_vient_la_derive") or {}).get(cle, {})
        if not o.get("decidable"):
            continue
        bout = (f" · à l'écart le plus petit ({o['ecart_le_plus_petit_vx']:.0f} vx) elle vaut "
                f"{o['derive_a_lecart_le_plus_petit']}" if "derive_a_lecart_le_plus_petit" in o
                else "")
        vraie = (f" · la VRAIE croît : {o['la_derive_VRAIE_croit_avec_lecart']} "
                 f"(rho {o['rho_ecart_lateral_sur_la_vraie']:+}, p "
                 f"{o['p_ecart_lateral_sur_la_vraie']})"
                 if "rho_ecart_lateral_sur_la_vraie" in o else "")
        des = (f" · suit le désaccord au départ : {o['la_derive_suit_le_desaccord']} "
               f"(rho {o['rho_desaccord_au_depart']:+}, p {o['p_desaccord_au_depart']})"
               if "rho_desaccord_au_depart" in o else "")
        print(f"\nd'où vient la dérive, {nom} : croît avec l'écart "
              f"{o['la_derive_croit_avec_lecart']} (rho {o['rho_ecart_lateral']:+}, p "
              f"{o['p_ecart_lateral']}){vraie}{des}{bout}")
    t = r.get("les_trois_matieres_sont_elles_distinctes", {})
    if t.get("decidable"):
        for c in t["comparaisons"]:
            print(f"\n{c['plus_grand']} contre {c['que']} : sépare davantage "
                  f"{c['il_separe_davantage']} (p de rang {c['p_de_rang']}) · médianes "
                  f"{c['mediane_du_plus_grand']} contre {c['mediane_de_lautre']}")
    j = r.get("juger", {})
    if j.get("decidable"):
        print(f"\n★★★ la pile périodique ne sépare pas : {j.get('la_pile_periodique_ne_separe_pas')} "
              f"({j.get('derive_vraie_periodique')}) · la pile par feuille sépare : "
              f"{j.get('la_pile_par_feuille_separe')} ({j.get('derive_vraie_par_feuille')}), "
              f"{j.get('combien_de_fois_plus')} fois plus")
        if j.get("derive_lue_du_rouleau") is not None:
            print(f"★★★★ le rouleau lit {j['derive_lue_du_rouleau']} (p90 "
                  f"{j['derive_lue_du_rouleau_p90']}) entre {j['derive_lue_periodique']} "
                  f"(périodique) et {j['derive_lue_par_feuille']} (par feuille) → il tombe à "
                  f"{j['ou_tombe_le_rouleau_sur_lechelle']} sur l'échelle")


class _PileSansPhase:
    """Un lecteur qui n'a PAS de phase analytique — pour que l'absence d'oracle soit exercee."""

    def __init__(self, pas_um: float = 173.0, voxel_um: float = 2.4) -> None:
        self.pas_um, self.voxel_um, self.remplissage = pas_um, voxel_um, 0
        self.forme = (4000, 4000, 4000)

    def dans_le_volume(self, p):
        p = np.asarray(p).reshape(-1, 3)
        return np.all((p >= 0) & (p < np.asarray(self.forme)), axis=1)

    def lire(self, points, fils=1):
        del fils
        q = np.asarray(points, dtype=np.float64).reshape(-1, 3)
        return 100.0 + 40.0 * np.cos(2 * np.pi * q[:, 2] * self.voxel_um / self.pas_um)


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from combien_de_pas_la_matiere_porte import VolumeFabriqueOndulee  # noqa: PLC0415

    # ---- l'axe dans la feuille
    for n in (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0]),
              np.array([0.0, 0.6, 0.8])):
        t = un_axe_dans_la_feuille(n)
        v("l'axe est unitaire et perpendiculaire à la normale",
          abs(float(np.linalg.norm(t)) - 1.0) < 1e-12 and abs(float(t @ n)) < 1e-12,
          f"n={np.round(n, 2).tolist()} t={np.round(t, 3).tolist()}")
    v("... et il est le même à chaque appel",
      np.allclose(un_axe_dans_la_feuille([0.0, 0.6, 0.8]), un_axe_dans_la_feuille([0.0, 0.6, 0.8])))
    v("... et une normale non unitaire est refusée plutôt que devinée",
      _leve(lambda: un_axe_dans_la_feuille([0.0, 0.0, 0.0]), ValueError))

    barres = _barres()
    C = barres[-1]
    plate = VolumeFabriqueOndulee(C.PAS_UM, amplitude_um=0.0, longueur_donde_um=LONGUEUR_DONDE_UM,
                                  par_feuille=True, bruit=BRUIT, graine=3)
    centre = np.array([2000.0, 2000.0, 2000.0])

    # ---- poser les jumelles
    pose = poser_les_jumelles(plate, centre, 16.0)
    v("les jumelles sont posées à l'écart demandé", pose["decidable"]
      and abs(float(np.linalg.norm(pose["b"] - pose["a"])) - 16.0) < 1e-9,
      f"{float(np.linalg.norm(pose['b'] - pose['a'])):.6f} vx")

    def phase(vol, p):
        return float(vol._projection_um(np.asarray(p, dtype=float).reshape(1, 3))[0]) / vol.pas_um

    dphi = abs(phase(plate, pose["b"]) - phase(plate, pose["a"]))
    v("⚠⚠ ... DANS le plan de la feuille : elles partent de la MÊME feuille", dphi < 0.01,
      f"décalage {dphi:.6f} feuille")
    # ⚠⚠ LA SONDE QUI REND LE CONTROLE PRECEDENT CAPABLE D'ECHOUER : le meme ecart pris le long de
    # la NORMALE met les deux jumelles sur deux feuilles differentes. Sans elle, « elles partent de
    # la meme feuille » serait satisfait par n'importe quel ecart assez petit.
    le_long = centre + pose["na"] * 16.0
    dphi_faux = abs(phase(plate, le_long) - phase(plate, centre))
    v("⚠⚠ sonde : le même écart pris le long de la NORMALE les sépare d'une fraction de feuille",
      dphi_faux > 0.1, f"décalage {dphi_faux:.4f} feuille contre {dphi:.6f} dans la feuille")
    v("... et une matière muette rend indécidable plutôt qu'une paire",
      not poser_les_jumelles(_PileSansPhase(), np.array([10.0, 10.0, 10.0]), 4.0)["decidable"])

    # ---- une marche et son cumul
    a = une_marche(plate, pose["a"], pose["na"], barres, pas_max=8)
    v("une marche rend un cumul croissant, un par pas",
      a["pas"] == len(a["cumul_de_feuilles"]) and a["pas"] > 0
      and all(a["cumul_de_feuilles"][i] <= a["cumul_de_feuilles"][i + 1] + 1e-9
              for i in range(a["pas"] - 1)),
      f"{a['pas']} pas, {a['feuilles']:.2f} feuilles")
    vraie = la_derive_vraie(plate, a, a, pose["a"], pose["a"])
    v("le compte d'une marche s'accorde à la traversée vraie à mieux qu'un quart de feuille par pas",
      vraie["decidable"] and abs(vraie["erreur_de_comptage_a"]) < 0.25 * a["pas"],
      f"compté {a['feuilles']:.2f} pour {vraie['traversee_vraie_a']:.2f} vraies")

    # ---- la dérive
    v("deux marches identiques ne dérivent pas", la_derive(a, a)["derive_lue"] == 0.0)
    b_ = {"pas": a["pas"], "cumul_de_feuilles": [x + 2.0 for x in a["cumul_de_feuilles"]],
          "pas_sans_fraction": 0, "position_fin": a["position_fin"], "feuilles": a["feuilles"] + 2.0}
    v("... et deux marches décalées de deux feuilles dérivent de deux",
      abs(la_derive(a, b_)["derive_lue"] + 2.0) < 1e-9, f"{la_derive(a, b_)['derive_lue']}")
    v("... une marche sans pas rend indécidable",
      not la_derive(a, {"pas": 0, "cumul_de_feuilles": []})["decidable"])
    v("⚠ une matière sans phase analytique n'a PAS de dérive vraie, et le dit",
      not la_derive_vraie(_PileSansPhase(), a, a, pose["a"], pose["a"])["decidable"])

    # ---- l'agrégation
    faux = [{"ecart_vx": float(e), "ecart_um": round(e * 2.4, 1), "derive_lue": d,
             "derive_lue_max": abs(d), "derive_vraie": d * 2.0, "traversee_vraie_a": 30.0,
             "traversee_vraie_b": 30.0, "decalage_de_phase_au_depart": 0.001,
             "erreur_de_comptage_a": 0.5, "erreur_de_comptage_b": -0.5, "pas_communs": 25,
             "feuilles_a": 30.0, "feuilles_b": 30.0 - d, "pas_a": 25, "pas_b": 25}
            for e in ECARTS_VX for d in (0.1, 0.4, 0.8, 1.2, 2.0, 0.3, 0.9)]
    s = resumer(faux)
    # ⚠ L'attendu est DERIVE de `ECARTS_VX` et de la largeur du cube, jamais recopie a la main :
    # une liste ecrite en dur redevient fausse le jour ou un ecart est ajoute, et elle l'a ete.
    attendu_cube = [e < LARGEUR_DU_CUBE_VX for e in ECARTS_VX]
    v("le résumé range par écart et marque le cube de lecture", s["decidable"]
      and len(s["par_ecart"]) == len(ECARTS_VX)
      and [b["dans_le_cube_de_lecture"] for b in s["par_ecart"]] == attendu_cube,
      f"{[b['ecart_vx'] for b in s['par_ecart']]} → {attendu_cube}")
    v("... et il publie la vraie à côté de la lue", "derive_vraie_mediane" in s
      and abs(s["derive_vraie_mediane"] - 2.0 * s["derive_lue_mediane"]) < 1e-9)
    v("... et aucune paire rend indécidable", not resumer([])["decidable"])

    # ---- le compteur voit-il ?
    c = le_compteur_voit_il_la_separation(faux)
    v("le compteur qui voit l'ordre mais pas le niveau est dit tel",
      c["decidable"] and c["le_compteur_voit_le_rang"] and not c["le_compteur_voit_le_niveau"],
      f"rho {c['rho_de_spearman']}, p apparié {c['p_apparie']}")
    exact = [{**x, "derive_vraie": x["derive_lue"]} for x in faux]
    ce = le_compteur_voit_il_la_separation(exact)
    v("⚠ ... et un compteur exact voit l'ordre ET le niveau",
      ce["le_compteur_voit_le_rang"] and ce["le_compteur_voit_le_niveau"],
      f"rho {ce['rho_de_spearman']}, p apparié {ce['p_apparie']}")
    melange = [{**x, "derive_vraie": y["derive_lue"] * 3.0}
               for x, y in zip(faux, list(reversed(faux)))]
    cm = le_compteur_voit_il_la_separation(melange)
    v("⚠⚠ ... et un compteur dont les rangs sont inversés est refusé",
      not cm["le_compteur_voit_le_rang"], f"rho {cm['rho_de_spearman']}")
    v("moins de six paires à vérité connue est indécidable",
      not le_compteur_voit_il_la_separation(faux[:3])["decidable"])
    plat = [{**x, "derive_vraie": 0.0, "derive_lue": 0.0} for x in faux]
    v("⚠ ... et une variation nulle est dite, jamais lue comme un accord",
      le_compteur_voit_il_la_separation(plat)["aucune_variation"])

    # ---- d'où vient la dérive
    croissante = [{**x, "derive_lue": 0.1 * x["ecart_vx"], "derive_vraie": 0.2 * x["ecart_vx"],
                   "desaccord_au_depart_deg": 1.0, "desaccord_a_la_jumelle_deg": 1.0}
                  for x in faux]
    o = doù_vient_la_derive(croissante)
    v("une dérive qui croît avec l'écart est dite telle",
      o["decidable"] and o["la_derive_croit_avec_lecart"] and o["la_derive_VRAIE_croit_avec_lecart"],
      f"rho {o['rho_ecart_lateral']}, p {o['p_ecart_lateral']}")
    v("... et elle est publiée à l'écart le plus petit",
      o["ecart_le_plus_petit_vx"] == float(min(ECARTS_VX)),
      f"{o['ecart_le_plus_petit_vx']} vx → {o['derive_a_lecart_le_plus_petit']}")
    plate_ = [{**x, "derive_lue": 2.5, "derive_vraie": 2.5,
               "desaccord_au_depart_deg": 1.0 + 0.5 * i,
               "desaccord_a_la_jumelle_deg": 1.0 + 0.5 * i} for i, x in enumerate(faux)]
    o2 = doù_vient_la_derive(plate_)
    v("⚠⚠ ... et une dérive qui ne croît PAS avec l'écart est refusée",
      not o2["la_derive_croit_avec_lecart"], f"rho {o2['rho_ecart_lateral']}")
    suit = [{**x, "derive_lue": 0.3 * i, "desaccord_au_depart_deg": float(i),
             "desaccord_a_la_jumelle_deg": float(i)} for i, x in enumerate(faux)]
    o3 = doù_vient_la_derive(suit)
    v("⚠ ... et une dérive qui suit le DESACCORD au départ est dite telle",
      o3["la_derive_suit_le_desaccord"], f"rho {o3['rho_desaccord_au_depart']}")
    v("moins de six paires est indécidable", not doù_vient_la_derive(faux[:3])["decidable"])

    # ---- les trois matieres se separent-elles ?
    def lot(valeurs):
        return {"paires": [{**faux[0], "derive_lue": v} for v in valeurs]}

    petit = lot([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4])
    moyen = lot([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1])
    grand = lot([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5])
    t = les_trois_matieres_sont_elles_distinctes(petit, moyen, grand)
    trouve = {(c["plus_grand"], c["que"]): c["il_separe_davantage"] for c in t["comparaisons"]}
    v("trois lots ordonnés sont dits distincts dans le bon sens", t["decidable"]
      and all(trouve.values()), f"{trouve}")
    # ⚠⚠ LA SONDE : trois lots IDENTIQUES ne doivent se separer d'aucun cote. Sans elle, un test
    # qui rendrait toujours « oui » passerait le controle precedent.
    meme = lot([0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7])
    t2 = les_trois_matieres_sont_elles_distinctes(meme, lot([0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7]),
                                                 lot([0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7]))
    v("⚠⚠ sonde : trois lots identiques ne se séparent d'aucun côté",
      not any(c["il_separe_davantage"] for c in t2["comparaisons"]),
      f"{[c['p_de_rang'] for c in t2['comparaisons']]}")
    # ⚠ Et le test est UNILATERAL : un lot PLUS PETIT ne doit pas etre declare « separe davantage ».
    t3 = les_trois_matieres_sont_elles_distinctes(grand, moyen, petit)
    v("⚠ ... et un lot plus petit n'est jamais dit séparer davantage",
      not any(c["il_separe_davantage"] for c in t3["comparaisons"]
              if c["plus_grand"] == "rouleau"),
      f"{[(c['plus_grand'], c['que'], c['p_de_rang']) for c in t3['comparaisons']]}")
    v("un seul lot est indécidable",
      not les_trois_matieres_sont_elles_distinctes(petit, {}, None)["decidable"])
    v("la part au-delà d'une feuille est publiée",
      abs(resumer(lot([0.5, 0.5, 2.0, 2.0])["paires"])["part_des_paires_au_dela_dune_feuille"]
          - 0.5) < 1e-9)

    # ---- le verdict des deux piles
    p_ = {"resume": {"decidable": True, "paires": 20, "derive_vraie_mediane": 0.03,
                     "derive_lue_mediane": 0.11, "derive_lue_p90": 1.9, "traversee_mediane": 24.0}}
    f_ = {"resume": {"decidable": True, "paires": 20, "derive_vraie_mediane": 0.98,
                     "derive_lue_mediane": 0.62, "derive_lue_p90": 2.1, "traversee_mediane": 24.0}}
    j = juger(p_, f_, {"resume": {"decidable": True, "derive_lue_mediane": 0.40,
                                  "derive_lue_p90": 1.5}})
    v("la pile périodique ne sépare pas, la pile par feuille sépare",
      j["la_pile_periodique_ne_separe_pas"] and j["la_pile_par_feuille_separe"],
      f"{j['derive_vraie_periodique']} contre {j['derive_vraie_par_feuille']}, "
      f"{j['combien_de_fois_plus']} fois plus")
    v("... et le rouleau est placé SUR l'échelle des deux piles",
      abs(j["ou_tombe_le_rouleau_sur_lechelle"] - (0.40 - 0.11) / (0.62 - 0.11)) < 1e-3,
      f"{j['ou_tombe_le_rouleau_sur_lechelle']}")
    # ⚠⚠ LA SONDE DU VERDICT : une pile periodique qui separerait doit faire ECHOUER le premier
    # verdict. Sans elle, « elle ne separe pas » serait une affirmation et non une mesure.
    jf = juger({"resume": {**p_["resume"], "derive_vraie_mediane": 0.9}}, f_, None)
    v("⚠⚠ sonde : une pile périodique qui sépare fait ÉCHOUER le verdict",
      not jf["la_pile_periodique_ne_separe_pas"] and not jf["la_pile_par_feuille_separe"],
      f"{jf['combien_de_fois_plus']} fois plus")
    v("... et une pile sans paire rend indécidable",
      not juger({"resume": {"decidable": False}}, f_, None)["decidable"])

    # ⚠ Le chemin qui produit le nombre publie est ATTEINT, sur les deux piles fabriquees : une
    # batterie qui teste les briques sans jamais les assembler ne peut pas echouer la ou ca compte.
    court_p = sur_une_pile(0.0, positions=3, pas_max=10)
    court_f = sur_une_pile(AMPLITUDE_UM, positions=3, pas_max=10)
    v("l'assemblage tourne sur les deux piles et rend des paires",
      len(court_p["paires"]) > 0 and len(court_f["paires"]) > 0,
      f"{len(court_p['paires'])} et {len(court_f['paires'])} paires")
    vp = court_p["resume"].get("derive_vraie_mediane")
    vf = court_f["resume"].get("derive_vraie_mediane")
    v("⚠⚠ ... et la pile PAR FEUILLE sépare ses jumelles plus que la périodique",
      vp is not None and vf is not None and vf > vp, f"{vp} contre {vf}")

    # ---- la reagregation : les memes paires, les memes verdicts, sans remarcher
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as dtmp:
        chemin = Path(dtmp) / "m.json"
        avant = {"ecarts_vx": list(ECARTS_VX), "largeur_du_cube_vx": LARGEUR_DU_CUBE_VX,
                 "pas_max": 25, "bruit": BRUIT,
                 "la_pile_periodique": {"paires": court_p["paires"], "resume": {}},
                 "la_pile_par_feuille": {"paires": court_f["paires"], "resume": {}},
                 "juger": {"decidable": False}}
        chemin.write_text(json.dumps(avant, ensure_ascii=False, default=float), encoding="utf-8")
        apres = reagreger(chemin)
        v("la réagrégation recalcule les résumés sans remarcher",
          apres["la_pile_periodique"]["resume"].get("decidable")
          and apres["juger"].get("decidable"),
          f"{apres['la_pile_periodique']['resume'].get('paires')} paires relues")
        v("... et elle rend les MÊMES résumés que la mesure",
          apres["la_pile_periodique"]["resume"] == court_p["resume"]
          and apres["la_pile_par_feuille"]["resume"] == court_f["resume"])
        # ⚠ Une mesure qui n'a rien rendu ne se reagrege pas en un verdict : elle se repasse.
        chemin.write_text(json.dumps({"message": "volume injoignable"}), encoding="utf-8")
        v("⚠ ... et un JSON porteur d'un message ressort tel quel",
          "message" in reagreger(chemin))

    # ---- l'affichage
    import contextlib, io  # noqa: PLC0415
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"ecarts_vx": list(ECARTS_VX), "largeur_du_cube_vx": LARGEUR_DU_CUBE_VX,
                  "la_pile_periodique": {"resume": resumer(faux)},
                  "la_pile_par_feuille": {"resume": resumer(faux)},
                  "le_rouleau": {"message": "volume injoignable"},
                  "le_compteur_voit_il_la_separation": {"sur_la_pile_periodique": c,
                                                        "sur_la_pile_par_feuille": ce},
                  "juger": j})
    sortie = tampon.getvalue()
    v("l'affichage tourne sur un résultat complet",
      "PÉRIODIQUE" in sortie and "sur l'échelle" in sortie and "volume injoignable" in sortie)
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "départs de `107` indisponibles"})
    v("... et une mesure absente est dite, jamais dessinée", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f, exc) -> bool:
    """L'appel leve-t-il bien cette exception ?"""
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
    p.add_argument("--bandes", type=int, default=None, help="combien de bandes du rouleau")
    p.add_argument("--positions", type=int, default=POSITIONS)
    p.add_argument("--pas-max", type=int, default=PAS_MAX)
    p.add_argument("--par-bande", type=int, default=1)
    p.add_argument("--fils", type=int, default=64)
    p.add_argument("--sans-rouleau", action="store_true")
    p.add_argument("--reagreger", type=Path, default=None,
                   help="recalculer les verdicts depuis un JSON deja mesure, sans remarcher")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger is not None:
        r = reagreger(a.reagreger)
    else:
        r = mesurer(bandes_max=a.bandes, positions=a.positions, pas_max=a.pas_max,
                    avec_rouleau=not a.sans_rouleau, par_bande=a.par_bande, fils=a.fils)
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
