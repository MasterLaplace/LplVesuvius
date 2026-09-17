"""Jusqu'où une surface peut-elle dériver avant que la matière cesse de se lire ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P36` QUI LE NOMME. `187` a fermé la voie du témoin de saut
et, ce faisant, a rendu un nombre que rien n'avait mesuré : sur le rouleau une dérive en profondeur de
seize couches coûte **6,625** pas de longueur suivable sur un ruban qui en atteint **21,75** à plat.
Ce n'est pas le saut qui casse la fibre, c'est le MOUVEMENT. La question devient donc : jusqu'où une
surface peut-elle dériver avant que la matière cesse de se lire ?

⭐⭐⭐⭐ ET LA RÉPONSE EST UNE LONGUEUR, PAS UN VERDICT. On fait de la montée du ruban une ÉCHELLE et
l'on regarde à quel barreau la matière réelle cesse de rendre plus qu'une matière dont l'ordre des
couches est mélangé. Ce point-là n'est pas un seuil choisi : c'est le CROISEMENT de deux courbes
mesurées, et il a une unité — la portée en profondeur de la texture, en micromètres.

⚠⚠⚠ LE CONTRÔLE EST LE MÉLANGE DE L'ORDRE DES COUCHES, ET IL PRICE EXACTEMENT LA BONNE CHOSE. Il
garde chaque couche intacte — même texture, même direction de fibres — et détruit seulement le fait
que deux couches voisines appartiennent à la même feuille. Une décroissance qui SURVIVRAIT au mélange
serait celle du ruban et non celle de la matière.

⭐⭐⭐⭐ ET L'ÉTALON ORDONNE TROIS MATIÈRES DONT L'ESPACEMENT DES FRONTIÈRES EST CONNU : deux plis par
feuille (une frontière tous les demi-pas), un seul pli avec des feuilles INDÉPENDANTES (une frontière
par pas), et un seul pli sans feuilles indépendantes — qui n'a AUCUNE frontière d'orientation et qui
est le contrôle vide de toute cette famille depuis `179`. La portée lue doit croître dans cet ordre,
et la dernière ne doit jamais être atteinte. Un instrument qui rendrait la même portée aux trois
mesurerait sa propre échelle.

⚠⚠⚠ ET LES DEUX PIÈGES DE `187` SONT ÉCRITS D'AVANCE : le plafond du ruban se lit dans la MATIÈRE —
c'est la longueur qu'une fibre y survit à plat — et le plancher se lit dans CHAQUE COUCHE. Sans le
premier la traversée arrive après la mort de la crête ; sans le second on mesure le profil de densité
de la feuille et non la fibre.

Usage :
    uv run python src/nappe/jusquou_une_surface_peut_elle_deriver.py --verifier
    uv run python src/nappe/jusquou_une_surface_peut_elle_deriver.py \\
        --json docs/mesures/jusquou_une_surface_peut_elle_deriver.json
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

from fiber_orientation import orientation_profile  # noqa: E402
from jusquou_suit_on_une_fibre import DEPARTS_PAR_COUCHE, les_departs  # noqa: E402
from la_coherence_creuse_t_elle_a_la_frontiere import (CONTRASTE_DE_LA_FIXTURE,  # noqa: E402
                                                       PLIS_DE_LA_FIXTURE)
from la_coupe_cherchee_trouve_t_elle_la_frontiere import COUCHES_DE_LA_CAMPAGNE  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PLANCHER_DE_COHERENCE, SEGMENTS, les_chunks,
                                             les_volumes)
from langle_publie_est_il_celui_des_fibres import direction_des_fibres_deg  # noqa: E402
from quelle_fenetre_lit_une_bascule import bloc_de_la_fixture  # noqa: E402
from suit_on_plus_loin_quand_le_voxel_est_plus_fin import le_plafond  # noqa: E402
from un_ruban_qui_saute_perd_il_sa_fibre import (le_plafond_du_ruban,  # noqa: E402
                                                 les_profondeurs_de_depart, un_ruban)
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20260928
DECALAGE_DE_LA_FIXTURE_UM = 0.0
# ⚠⚠ LE RASOIR, ET C'EST UN CHOIX DE FORME QUI S'IMPOSE : la question porte sur la PORTÉE de la
# texture en profondeur et non sur la douceur d'une frontière, et un recouvrement est BORNÉ par
# l'épaisseur d'un pli — il ne pourrait donc pas rester le même le long d'une échelle de plis. Le
# rasoir est la frontière que `179` nomme comme contrôle vide, et il est le seul qui vaille pour
# tous les barreaux.
RECOUVREMENT_DE_LA_FIXTURE_UM = 0.0
# ⚠⚠⚠ L'ÉCHELLE EST UNE ÉCHELLE DE VITESSES, ET IL A FALLU LA MESURE POUR LE COMPRENDRE. Une
# première version faisait varier le nombre de PLIS de `VolumeFabriqueAFibres` en croyant faire
# varier l'espacement des frontières — or ce volume étale un DEMI-TOUR par feuille quel que soit le
# nombre de plis, donc huit plis et deux plis tournent à la MÊME vitesse et les trois matières ont
# rendu la même chose. Ce qui gouverne la portée n'est pas l'espacement, c'est la VITESSE à laquelle
# la direction des fibres change en profondeur.
# ⚠ Le même QUART DE TOUR étalé sur un doublement de couches : le tour total s'annule dans la
# comparaison et ce qui reste est la vitesse — l'identité que `179` emploie pour départager deux
# escaliers. Zéro est la matière qui ne tourne pas, et c'est le contrôle vide.
COUCHES_DUN_QUART_DE_TOUR = (4, 16, 64)


def lechelle_des_montees(voxel_um: float, pas_um: float) -> list[int]:
    """Les montées de l'échelle : zéro, puis les puissances de deux jusqu'à un pas de feuille.

    ⚠⚠ LE PLAFOND EST LE PAS ENTRE DEUX FEUILLES, parce que c'est la distance qu'un transfert de
    spire à spire demande de franchir : une échelle qui s'arrêterait avant ne pourrait pas dire si la
    matière porte assez loin pour lui.

    ⚠ ET LA FORME EST UN DOUBLEMENT parce que la réponse cherchée est un ORDRE DE GRANDEUR : une
    échelle linéaire dépenserait presque tous ses barreaux là où rien ne bouge. Zéro est le barreau
    de référence — c'est la marche à plat de `185`.

    ⚠⚠⚠ ET LE PAS LUI-MÊME EST AJOUTÉ COMME DERNIER BARREAU, ARRONDI VERS LE HAUT, parce qu'un
    doublement ne tombe pas dessus : sans lui l'échelle s'arrête à **64** couches, soit **153,6** µm,
    et l'énoncé « la portée franchit-elle un pas entre deux feuilles » deviendrait une vérification
    qui ne peut pas RÉUSSIR — le pendant exact d'une vérification qui ne peut pas échouer. ⚠ Et
    l'arrondi est vers le HAUT pour la même raison : à **72** couches on est encore à **172,8** µm,
    donc sous le pas. C'est la règle que `185` emploie déjà pour son plafond.
    """
    plafond = int(np.ceil(float(pas_um) / float(voxel_um)))
    out, m = [0], 1
    while m <= plafond:
        out.append(int(m))
        m *= 2
    if out[-1] != plafond:
        out.append(int(plafond))
    return out


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def les_departs_par_couche(bloc: np.ndarray, coherences, combien: int,
                           plancher: float = PLANCHER_DE_COHERENCE) -> dict:
    """Les départs de chaque couche texturée, calculés UNE fois pour toute l'échelle.

    ⚠ Ils ne dépendent pas de la montée : les recalculer à chaque barreau coûterait sans rien
    changer, et surtout ferait dépendre du barreau une chose qui n'en dépend pas.
    """
    out = {}
    for k in range(len(coherences)):
        if float(coherences[k]) <= float(plancher):
            continue
        d = les_departs(bloc[k], combien)
        if d:
            out[int(k)] = d
    return out


def un_barreau(bloc: np.ndarray, angles, coherences, montee: int, departs_par_couche: dict,
               plafond: int, plancher_de_coherence: float = PLANCHER_DE_COHERENCE,
               profondeurs_par_signe: dict | None = None) -> dict:
    """Un barreau de l'échelle : tous les rubans de cette montée, marchés en UN passage.

    ⚠⚠ LES DEUX SENS DE MONTÉE SONT LUS. Une segmentation dérive vers l'intérieur comme vers
    l'extérieur ; n'en lire qu'un ferait dépendre le résultat du sens où le bloc a été empilé. ⚠ À
    montée NULLE les deux sens sont le même ruban, donc un seul est marché — le compter deux fois
    donnerait au barreau de référence un poids que les autres n'ont pas.

    ⚠⚠ L'ANGLE EST CELUI DE LA COUCHE DE DÉPART, tenu fixe le long du ruban : c'est ce qu'un pipeline
    connaît, et c'est la règle de `187`.

    ⭐ `profondeurs_par_signe` IMPOSE LE MÊME JEU DE DÉPARTS À TOUS LES BARREAUX, et c'est ce qui rend
    une COURBE comparable d'un barreau à l'autre. Sans lui, une montée qui approche la hauteur du bloc
    n'a plus que quelques profondeurs admissibles, donc la forme de la courbe mêlerait ce que la
    matière porte et ce que l'échantillon a rétréci. Absent, le comportement est celui de `188` :
    chaque barreau prend ce qu'il peut.
    """
    lus: list[int] = []
    for signe in (1, -1):
        m = int(signe) * int(montee)
        impose = (profondeurs_par_signe or {}).get(int(signe))
        admissibles = (les_profondeurs_de_depart(coherences, m, plancher_de_coherence)
                       if impose is None
                       else [int(k) for k in impose if 0 <= int(k) + m < len(coherences)])
        departs, kk, aa = [], [], []
        for k in admissibles:
            d = departs_par_couche.get(int(k))
            if not d:
                continue
            ang = float(direction_des_fibres_deg(float(angles[k])))
            for x in d:
                departs.append(x)
                kk.append(float(k))
                aa.append(ang)
        if departs:
            lus += un_ruban(bloc, departs, np.asarray(kk), np.asarray(aa), m, plafond)
        if int(montee) == 0:
            break
    return {"montee": int(montee), "rubans": len(lus), "pas_median": _med(lus)}


def lechelle_sur_un_bloc(bloc: np.ndarray, angles, coherences, montees, combien: int,
                         plafond_max: int, plancher_de_coherence: float = PLANCHER_DE_COHERENCE,
                         graine: int = GRAINE) -> dict:
    """L'échelle entière sur un bloc, et la MÊME échelle sur ce bloc aux couches mélangées.

    ⭐⭐⭐⭐ LE MÉLANGE EST LE NUL, ET C'EST LUI QUI DONNE À LA PORTÉE SON SENS. Mélanger l'ordre des
    couches garde chaque couche intacte et ne détruit que la contiguïté : la portée est donc la
    profondeur au-delà de laquelle marcher dans la vraie matière ne vaut pas mieux que marcher dans
    des couches tirées au hasard.

    ⚠⚠ LE PLAFOND DU RUBAN EST LU DANS LA MATIÈRE, et le MÊME sert aux deux échelles : c'est la
    longueur qu'une fibre survit à plat ici. Un plafond plus grand ferait arriver la dérive après la
    mort de la crête, ce que `187` a payé ; deux plafonds différents rendraient les deux courbes
    incomparables.
    """
    pl = le_plafond_du_ruban(bloc, angles, coherences, combien, plafond_max,
                             plancher_de_coherence)
    if not pl:
        return {"decidable": False, "raison": "aucune couche texturée"}
    r = np.random.default_rng(int(graine))
    ordre = r.permutation(bloc.shape[0])
    melange = bloc[ordre]
    ang_m, coh_m = np.asarray(angles)[ordre], np.asarray(coherences)[ordre]
    dep = les_departs_par_couche(bloc, coherences, combien, plancher_de_coherence)
    dep_m = les_departs_par_couche(melange, coh_m, combien, plancher_de_coherence)
    barreaux = []
    for m in montees:
        vrai = un_barreau(bloc, angles, coherences, m, dep, pl, plancher_de_coherence)
        faux = un_barreau(melange, ang_m, coh_m, m, dep_m, pl, plancher_de_coherence)
        barreaux.append({
            "montee": int(m), "rubans": vrai["rubans"],
            "pas_median": vrai["pas_median"], "pas_median_melange": faux["pas_median"],
            "excedent": (round(float(vrai["pas_median"]) - float(faux["pas_median"]), 3)
                         if vrai["pas_median"] is not None and faux["pas_median"] is not None
                         else None)})
    return {"decidable": True, "plafond_du_ruban": int(pl), "barreaux": barreaux}


def la_portee_en_profondeur(barreaux) -> dict:
    """La montée à partir de laquelle la vraie matière ne rend plus que des couches mélangées.

    ⭐⭐⭐⭐ CE N'EST PAS UN SEUIL, C'EST UN CROISEMENT. Les deux courbes partent ensemble — à montée
    nulle le ruban ne quitte pas sa couche, donc mélanger l'ordre ne change rien — puis la vraie
    matière garde de l'avance tant que ses couches voisines se ressemblent. Le premier barreau où
    cette avance s'annule EST la portée.

    ⚠ Une échelle où l'avance ne s'annule jamais ne rend PAS une portée : elle rend « au-delà du
    dernier barreau », ce qui est une borne et se publie comme telle.

    ⚠⚠⚠ ET UNE MATIÈRE QUE LE MÉLANGE NE DÉGRADE JAMAIS N'A PAS DE PORTÉE À LIRE, c'est la troisième
    issue et elle a coûté une sonde. Si l'avance ne devient positive à AUCUN barreau, alors mélanger
    l'ordre des couches n'enlève rien — ce que rend une pile dont toutes les couches sont identiques,
    où le mélange est l'identité — et « l'avance s'annule au premier barreau » se lirait comme une
    portée nulle alors que la matière porte partout. Le refus est la seule réponse juste.
    """
    lus = [b for b in barreaux if b["excedent"] is not None]
    if not lus:
        return {"decidable": False, "raison": "aucun barreau lisible"}
    sommet = max(range(len(lus)), key=lambda i: float(lus[i]["excedent"]))
    if float(lus[sommet]["excedent"]) <= 0.0:
        return {"decidable": False, "raison": "la matière et son mélange ne se séparent jamais",
                "excedent_maximal": float(lus[sommet]["excedent"]),
                "dernier_barreau": int(lus[-1]["montee"])}
    # ⚠⚠⚠ LE CROISEMENT SE CHERCHE APRÈS LE SOMMET, ET UNE PREMIÈRE VERSION LE CHERCHAIT DEPUIS LE
    # DÉBUT. L'avance de la vraie matière MONTE d'abord — à petite montée le mélange n'a pas encore
    # eu le temps de détruire grand-chose — puis retombe. Chercher depuis le premier barreau rendait
    # une portée d'UNE couche à une matière qui tourne lentement, c'est-à-dire l'inverse de ce qu'elle
    # porte, parce qu'un excédent nul par quantification au tout début arrêtait la recherche.
    for b in lus[sommet:]:
        if int(b["montee"]) > 0 and float(b["excedent"]) <= 0.0:
            return {"decidable": True, "portee_en_couches": int(b["montee"]),
                    "au_dela_de_lechelle": False,
                    "excedent_a_la_portee": float(b["excedent"]),
                    "excedent_maximal": float(lus[sommet]["excedent"]),
                    "sommet_en_couches": int(lus[sommet]["montee"]),
                    "dernier_barreau": int(lus[-1]["montee"])}
    return {"decidable": True, "portee_en_couches": None, "au_dela_de_lechelle": True,
            "excedent_a_la_portee": None,
            "excedent_maximal": float(lus[sommet]["excedent"]),
            "sommet_en_couches": int(lus[sommet]["montee"]),
            "excedent_au_dernier_barreau": float(lus[-1]["excedent"]),
            "dernier_barreau": int(lus[-1]["montee"])}


def une_pile_qui_tourne(couches: int, sur: int, cote: int = 64,
                        longueur_de_fibre_vox: float = 12.0) -> np.ndarray:
    """Une pile dont les fibres tournent d'un QUART DE TOUR sur `sur` couches. `sur=0` ne tourne pas.

    ⚠⚠ ELLE EST CONSTRUITE ICI ET NON REPRISE DE `VolumeFabriqueAFibres`, ET LA RAISON EST MESURÉE :
    ce volume-là étale un demi-tour par FEUILLE quel que soit son nombre de plis, donc sa vitesse
    angulaire est fixée par le pas et il ne peut pas fournir une échelle de vitesses. Une matière qui
    tourne d'un angle POSÉ par couche le peut, et c'est la seule chose que cette tranche demande à
    l'étalon.

    ⚠ Les crêtes sont la même modulation que partout ailleurs : ce qui change d'un barreau à l'autre
    est la vitesse, et rien d'autre.
    """
    yy, xx = np.mgrid[0:int(cote), 0:int(cote)].astype(np.float64)
    out = []
    for k in range(int(couches)):
        a = 0.0 if int(sur) <= 0 else np.radians(90.0 * k / float(sur))
        s_ = np.cos(a) * yy + np.sin(a) * xx
        out.append(100.0 + 40.0 * np.cos(2.0 * np.pi * s_ / float(longueur_de_fibre_vox)))
    return np.stack(out).astype(np.float32)


def sur_la_fixture(montees, combien: int = DEPARTS_PAR_COUCHE,
                   sur=COUCHES_DUN_QUART_DE_TOUR, graine: int = GRAINE) -> dict:
    """Des matières dont la VITESSE de rotation en profondeur est POSÉE, et elle décroît d'une à
    l'autre.

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE QUI REND LE ROULEAU LISIBLE, ET IL PEUT ÉCHOUER. Une matière qui tourne
    d'un quart de tour sur quatre couches change vite ; sur soixante-quatre, lentement ; une matière
    qui ne tourne pas ne change pas du tout. La portée lue doit CROÎTRE dans cet ordre, et la
    dernière ne doit même pas se séparer de son mélange. Un instrument qui rendrait la même portée
    aux quatre mesurerait sa propre échelle.

    ⚠ Trois issues sont possibles et elles sont ORDONNÉES : une portée DANS l'échelle, une portée
    AU-DELÀ, et une matière qui ne se sépare jamais. Exiger quatre nombres croissants rendrait le
    contrôle indécidable dès qu'une portée sort de l'échelle — ce qu'une matière lente doit faire.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    plafond = le_plafond(vx, pas)
    lignes = []
    for n in list(sur) + [0]:
        bloc = une_pile_qui_tourne(COUCHES_DE_LA_CAMPAGNE, int(n))
        ang, coh = orientation_profile(bloc)
        lu = lechelle_sur_un_bloc(bloc, ang, coh, montees, combien, plafond,
                                  PLANCHER_DE_COHERENCE, graine)
        nom = (f"un quart de tour sur {n} couches" if n else "aucune rotation")
        if not lu.get("decidable"):
            lignes.append({"matiere": nom, "couches_dun_quart_de_tour": int(n),
                           "decidable": False, "raison": lu.get("raison")})
            continue
        portee = la_portee_en_profondeur(lu["barreaux"])
        lignes.append({"matiere": nom, "couches_dun_quart_de_tour": int(n),
                       "degres_par_couche": (round(90.0 / float(n), 4) if n else 0.0),
                       **lu, **portee})
    # ⚠⚠⚠ L'ORDRE EST L'ENONCE, PAS LA VALEUR, ET IL SE LIT SUR UNE ECHELLE BORNEE.
    def _rang(x) -> int:
        if not x.get("decidable"):
            return 2
        return 1 if x.get("au_dela_de_lechelle") else 0

    rangs = [_rang(x) for x in lignes]
    dedans = [x.get("portee_en_couches") for x in lignes
              if x.get("decidable") and not x.get("au_dela_de_lechelle")]
    return {"couches_dun_quart_de_tour": [int(n) for n in sur],
            "lignes": lignes, "matieres_lues": len([x for x in lignes if x.get("decidable")]),
            "portees_lues": [x.get("portee_en_couches") for x in lignes], "rangs": rangs,
            "la_portee_croit_avec_la_lenteur": bool(
                len(rangs) >= 2 and all(b >= a for a, b in zip(rangs, rangs[1:]))
                and rangs[0] == 0 and rangs[-1] == 2
                and all(b > a for a, b in zip(dedans, dedans[1:]))),
            "la_matiere_qui_ne_tourne_pas_ne_se_separe_jamais": bool(
                lignes and not lignes[-1].get("decidable")),
            "la_portee_la_plus_courte": (dedans[0] if dedans else None),
            "la_portee_la_plus_longue": (dedans[-1] if dedans else None)}


def un_segment(volume: dict, montees, combien: int, plafond_max: int,
               cote: int = COTE_DU_TREILLIS, delai: float = DELAI,
               graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    lignes, refus = [], {}
    for cy, cx in les_chunks(-(-rows // hy), -(-cols // hx), cote):
        raw = get(f"{url}/{chunk_key(meta, 0, cy, cx)}", delai)
        if raw is None:
            refus["absent"] = refus.get("absent", 0) + 1
            continue
        data = decode(raw, meta, profond * hy * hx)
        if data is None:
            refus["illisible"] = refus.get("illisible", 0) + 1
            continue
        bloc = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx)
        if int(bloc.max()) == 0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        ang, coh = orientation_profile(bloc)
        if int((coh > PLANCHER_DE_COHERENCE).sum()) < profond // 4:
            refus["trop peu texturé"] = refus.get("trop peu texturé", 0) + 1
            continue
        lu = lechelle_sur_un_bloc(bloc.astype(np.float32), ang, coh, montees, combien,
                                  plafond_max, PLANCHER_DE_COHERENCE, graine)
        if not lu.get("decidable"):
            refus[lu.get("raison", "indécidable")] = refus.get(lu.get("raison", "indécidable"),
                                                               0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)], **lu,
                       **la_portee_en_profondeur(lu["barreaux"])})
    portees = [x["portee_en_couches"] for x in lignes if x.get("portee_en_couches") is not None]
    # ⚠⚠ LA COURBE DU SEGMENT EST LA MEDIANE BARREAU PAR BARREAU, pas la courbe d'un chunk choisi :
    # un chunk qui rendrait une courbe atypique deviendrait sinon la mesure.
    courbe = []
    for i, m in enumerate(montees):
        v = [x["barreaux"][i]["pas_median"] for x in lignes
             if x["barreaux"][i]["pas_median"] is not None]
        f = [x["barreaux"][i]["pas_median_melange"] for x in lignes
             if x["barreaux"][i]["pas_median_melange"] is not None]
        courbe.append({"montee": int(m), "pas_median": _med(v), "pas_median_melange": _med(f),
                       "excedent": (round(_med(v) - _med(f), 3) if v and f else None)})
    return {"decidable": bool(lignes), "segment": volume["segment"], "chunks_lus": len(lignes),
            "refuses": refus, "courbe": courbe,
            "plafond_du_ruban_median": (int(statistics.median_low(
                [x["plafond_du_ruban"] for x in lignes])) if lignes else None),
            "portee_mediane_en_couches": (int(statistics.median_low(portees))
                                          if portees else None),
            "chunks_sans_portee": int(sum(1 for x in lignes
                                          if x.get("portee_en_couches") is None)),
            **la_portee_en_profondeur(courbe), "chunks": lignes}


def juger(segments: list[dict], etalon: dict, montees, voxel_um: float, pas_um: float) -> dict:
    """Jusqu'où une surface peut-elle dériver — EN MICROMÈTRES ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    courbe = []
    for i, m in enumerate(montees):
        v = [s["courbe"][i]["pas_median"] for s in lus
             if s["courbe"][i]["pas_median"] is not None]
        f = [s["courbe"][i]["pas_median_melange"] for s in lus
             if s["courbe"][i]["pas_median_melange"] is not None]
        courbe.append({"montee": int(m), "montee_um": round(float(m) * float(voxel_um), 3),
                       "pas_median": _med(v), "pas_median_melange": _med(f),
                       "excedent": (round(_med(v) - _med(f), 3) if v and f else None)})
    portee = la_portee_en_profondeur(courbe)
    p = portee.get("portee_en_couches")
    return {"decidable": True, "segments": len(lus),
            "chunks_lus": int(sum(s["chunks_lus"] for s in lus)),
            "courbe": courbe, **portee,
            "portee_um": (round(float(p) * float(voxel_um), 3) if p is not None else None),
            # ⚠⚠ UNE PORTEE HORS DE L'ECHELLE RESTE UNE BORNE INFERIEURE, ET ELLE SE PUBLIE COMME
            # TELLE : « au-dela du dernier barreau » n'est pas « inconnue », c'est « au moins
            # autant », et le lecteur a droit au nombre.
            "portee_minimale_um": (round(float(p) * float(voxel_um), 3) if p is not None
                                   else round(float(montees[-1]) * float(voxel_um), 3)),
            "le_pas_entre_deux_feuilles_um": float(pas_um),
            "elle_vaut_le_pas_entre_deux_feuilles_fois": (
                round(float(p) * float(voxel_um) / float(pas_um), 4) if p is not None
                else round(float(montees[-1]) * float(voxel_um) / float(pas_um), 4)),
            "plafond_du_ruban_median": (int(statistics.median_low(
                [s["plafond_du_ruban_median"] for s in lus
                 if s["plafond_du_ruban_median"] is not None]))
                if any(s["plafond_du_ruban_median"] is not None for s in lus) else None),
            "portee_mediane_des_chunks": (int(statistics.median_low(
                [s["portee_mediane_en_couches"] for s in lus
                 if s["portee_mediane_en_couches"] is not None]))
                if any(s["portee_mediane_en_couches"] is not None for s in lus) else None),
            "la_portee_la_plus_courte_de_letalon": etalon.get("la_portee_la_plus_courte"),
            "la_portee_la_plus_longue_de_letalon": etalon.get("la_portee_la_plus_longue"),
            "portees_de_letalon": etalon.get("portees_lues"),
            # ⚠⚠ TROIS ENONCES, ET LE PREMIER CONDITIONNE LES AUTRES. Un instrument qui rendrait la
            # meme portee a trois matieres dont l'espacement des frontieres DIFFERE mesurerait sa
            # propre echelle, et rien de ce qu'il rend du rouleau ne se lirait.
            "letalon_ordonne_les_portees": bool(
                etalon.get("la_portee_croit_avec_la_lenteur")
                and etalon.get("la_matiere_qui_ne_tourne_pas_ne_se_separe_jamais")),
            "la_portee_se_lit_sur_le_rouleau": bool(p is not None),
            # ⚠⚠⚠ ET DEPASSER L'ECHELLE ENTIERE EST FRANCHIR LE PAS, puisque le dernier barreau EST
            # le pas arrondi vers le haut. Une premiere version ne traitait pas cette branche et
            # rendait « ne franchit pas » a une matiere qui porte au-dela de TOUTE l'echelle — un
            # enonce incomplet, pas une mesure.
            "elle_franchit_un_pas_entre_deux_feuilles": bool(
                (p is not None and float(p) * float(voxel_um) >= float(pas_um))
                or (p is None and portee.get("au_dela_de_lechelle")
                    and float(montees[-1]) * float(voxel_um) >= float(pas_um)))}


def mesurer(segments_n: int = SEGMENTS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    montees = lechelle_des_montees(vx, pas)
    plafond = le_plafond(vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    etalon = sur_la_fixture(montees, combien)
    segs = [un_segment(v, montees, combien, plafond, cote) for v in volumes]
    return {"departs_par_couche": int(combien), "cote_du_treillis": int(cote),
            "plafond_de_pas": int(plafond), "voxel_um": vx, "pas_um": pas, "graine": int(GRAINE),
            "montees": [int(m) for m in montees],
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "letalon": etalon, "les_segments": segs,
            "le_verdict": juger(segs, etalon, montees, vx, pas)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("JUSQU'OÙ UNE SURFACE PEUT-ELLE DÉRIVER ?")
    print(f"  {r['departs_par_couche']} départs par couche · treillis "
          f"{r['cote_du_treillis']}×{r['cote_du_treillis']} · {v['chunks_lus']} chunks · échelle "
          f"{r['montees']} couches · voxel {r['voxel_um']} µm")
    print()
    print("  L'ÉTALON — des matières dont la VITESSE de rotation est POSÉE")
    for x in e["lignes"]:
        if not x.get("decidable"):
            print(f"     {x['matiere']:<32} — {x.get('raison')}")
            continue
        print(f"     {x['matiere']:<32} {x.get('degres_par_couche')} °/couche · "
              f"portée {x.get('portee_en_couches')} · au-delà de l'échelle "
              f"{x.get('au_dela_de_lechelle')} · excédent max {x.get('excedent_maximal')}")
    print()
    print("  LE ROULEAU")
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"     {s['segment']} — {s.get('raison', 'rien de lisible')}")
            continue
        print(f"     {s['segment']} · {s['chunks_lus']} chunks · portée "
              f"{s.get('portee_en_couches')} · médiane des chunks "
              f"{s['portee_mediane_en_couches']} · refusés {s['refuses']}")
    print()
    print("  LA COURBE — la vraie matière contre ses couches mélangées")
    for b in v["courbe"]:
        print(f"     montée {b['montee']:>3} couches ({b['montee_um']:>7} µm) · "
              f"{b['pas_median']} contre {b['pas_median_melange']} · excédent {b['excedent']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("segments", "chunks_lus", "plafond_du_ruban_median", "portee_en_couches",
                "portee_um", "portee_minimale_um", "au_dela_de_lechelle", "sommet_en_couches",
                "excedent_maximal", "excedent_a_la_portee",
                "portee_mediane_des_chunks", "le_pas_entre_deux_feuilles_um",
                "elle_vaut_le_pas_entre_deux_feuilles_fois", "portees_de_letalon",
                "la_portee_la_plus_courte_de_letalon", "la_portee_la_plus_longue_de_letalon",
                "letalon_ordonne_les_portees", "la_portee_se_lit_sur_le_rouleau",
                "elle_franchit_un_pas_entre_deux_feuilles"):
        print(f"     {cle:<46} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)

    # ⚠⚠ L'ECHELLE EST DERIVEE : elle va jusqu'au PAS ENTRE DEUX FEUILLES, la distance qu'un
    # transfert demande de franchir, et elle double parce que la reponse est un ordre de grandeur.
    ech = lechelle_des_montees(vx, pas)
    v("l'échelle part de zéro", ech[0] == 0, str(ech))
    # ⚠ Le dernier barreau est le PAS, ajouté a part : le doublement porte sur tous les autres.
    v("elle double jusqu'à l'avant-dernier barreau",
      all(b == 2 * a for a, b in zip(ech[1:-2], ech[2:-1])), str(ech))
    v("★ son dernier barreau FRANCHIT un pas entre deux feuilles",
      ech[-1] * vx >= pas, f"{ech[-1] * vx} contre {pas}")
    v("et le barreau d'avant ne le franchit pas", ech[-2] * vx < pas,
      f"{ech[-2] * vx} contre {pas}")
    # ⚠⚠ L'ECHELLE EST EN COUCHES MAIS SON PLAFOND EST EN MICROMETRES : a voxel deux fois plus fin
    # elle porte deux fois plus de couches pour couvrir LA MEME distance. Un plafond en couches
    # ferait dependre la question de la resolution au lieu de la matiere.
    fine = lechelle_des_montees(vx / 2.0, pas)
    v("une échelle à voxel deux fois plus fin couvre la MÊME distance",
      abs(fine[-1] * (vx / 2.0) - ech[-1] * vx) < vx, f"{fine[-1] * vx / 2.0} contre {ech[-1] * vx}")
    v("et elle y met environ deux fois plus de couches", fine[-1] >= 2 * ech[-1] - 2,
      f"{fine[-1]} contre {ech[-1]}")

    # ⭐⭐⭐⭐ LA FORME EN TABLEAU DU RUBAN REND EXACTEMENT CE QUE REND LA FORME SCALAIRE. Sans ce
    # controle, marcher des rubans partis de profondeurs differentes en un passage serait une
    # SECONDE definition de la marche, libre de diverger de celle de `187`.
    yy, xx = np.mgrid[0:64, 0:64].astype(np.float32)
    empile = np.stack([100.0 + 40.0 * np.cos(2.0 * np.pi * (yy + 3.0 * k) / 12.0)
                       for k in range(12)]).astype(np.float32)
    dep = les_departs(empile[2], DEPARTS_PAR_COUCHE)
    a_la_main = un_ruban(empile, dep, 2, 17.0, 4, 30)
    en_tableau = un_ruban(empile, dep, np.full(len(dep), 2.0), np.full(len(dep), 17.0), 4, 30)
    v("★★★★ la forme en tableau rend exactement la forme scalaire",
      a_la_main == en_tableau, f"{a_la_main[:5]} contre {en_tableau[:5]}")
    melanges = un_ruban(empile, dep + dep, np.array([2.0] * len(dep) + [5.0] * len(dep)),
                        np.array([17.0] * len(dep) + [17.0] * len(dep)), 4, 30)
    v("et deux profondeurs marchées ensemble rendent chacune ce qu'elle rend seule",
      melanges[:len(dep)] == a_la_main
      and melanges[len(dep):] == un_ruban(empile, dep, 5, 17.0, 4, 30),
      str(melanges[:3]))

    # ⚠⚠ A MONTEE NULLE LES DEUX SENS SONT LE MEME RUBAN : le compter deux fois donnerait au
    # barreau de reference un poids que les autres n'ont pas.
    coh = np.full(12, 0.9)
    ang = np.zeros(12)
    dpc = les_departs_par_couche(empile, coh, DEPARTS_PAR_COUCHE)
    b0 = un_barreau(empile, ang, coh, 0, dpc, 30)
    b4 = un_barreau(empile, ang, coh, 4, dpc, 30)
    v("le barreau zéro ne compte chaque ruban qu'une fois",
      b0["rubans"] == len(dpc) * DEPARTS_PAR_COUCHE, f"{b0['rubans']} pour {len(dpc)} couches")
    v("et un barreau non nul lit les deux sens", b4["rubans"] > b0["rubans"],
      f"{b4['rubans']} contre {b0['rubans']}")

    # ⚠⚠ LES DEPARTS SONT CALCULES UNE FOIS ET NE DEPENDENT PAS DE LA MONTEE.
    v("il y a un jeu de départs par couche texturée", len(dpc) == 12, str(len(dpc)))
    v("et chaque jeu a autant de départs que demandé",
      all(len(x) == DEPARTS_PAR_COUCHE for x in dpc.values()),
      str({k: len(x) for k, x in list(dpc.items())[:3]}))
    v("une couche sans texture ne rend aucun jeu",
      les_departs_par_couche(empile, [0.01] * 12, DEPARTS_PAR_COUCHE) == {})

    # ⭐⭐⭐⭐ LA PORTEE EST UN CROISEMENT, PAS UN SEUIL : le premier barreau ou l'avance de la vraie
    # matiere s'annule. Et une echelle ou elle ne s'annule jamais rend une BORNE, pas une portee.
    def _b(m, exc):
        return {"montee": int(m), "pas_median": 20.0, "pas_median_melange": 20.0 - exc,
                "excedent": float(exc)}

    # ⚠⚠ LE CROISEMENT SE CHERCHE APRES LE SOMMET : ici l'avance vaut zero au barreau UN puis monte,
    # et une recherche depuis le debut y lirait une portee d'une couche.
    p0 = la_portee_en_profondeur([_b(0, 0.0), _b(1, 0.0), _b(2, 8.0), _b(4, 3.0), _b(8, -1.0)])
    v("★★★★ un excédent nul AVANT le sommet n'arrête pas la recherche",
      p0["portee_en_couches"] == 8, str(p0))
    v("et le sommet est publié", p0["sommet_en_couches"] == 2, str(p0.get("sommet_en_couches")))
    p1 = la_portee_en_profondeur([_b(0, 0.0), _b(1, 5.0), _b(2, 3.0), _b(4, 0.0), _b(8, -1.0)])
    v("la portée est le premier barreau où l'avance s'annule", p1["portee_en_couches"] == 4,
      str(p1))
    v("et le barreau zéro n'est jamais la portée", not p1["au_dela_de_lechelle"])
    p2 = la_portee_en_profondeur([_b(0, 0.0), _b(1, 5.0), _b(2, 4.0), _b(4, 3.0)])
    v("une avance qui ne s'annule jamais rend une borne et non une portée",
      p2["au_dela_de_lechelle"] and p2["portee_en_couches"] is None, str(p2))
    v("et la borne dit à quel barreau l'échelle s'est arrêtée", p2["dernier_barreau"] == 4,
      str(p2["dernier_barreau"]))
    v("l'excédent maximal est publié dans les deux cas",
      p1["excedent_maximal"] == 5.0 and p2["excedent_maximal"] == 5.0)
    p3 = la_portee_en_profondeur([_b(0, 0.0), _b(1, -2.0)])
    v("★★★★ une matière que le mélange ne dégrade JAMAIS est refusée, pas lue à zéro",
      not p3.get("decidable") and "séparent jamais" in p3.get("raison", ""), str(p3))
    p4 = la_portee_en_profondeur([_b(0, 0.0), _b(1, 5.0), _b(2, -1.0)])
    v("une matière qui se sépare puis retombe rend sa portée au barreau suivant",
      p4["portee_en_couches"] == 2, str(p4))

    # ⭐⭐⭐⭐ LA MATIERE CONSTRUITE : une pile dont les couches SE RESSEMBLENT porte loin, une pile
    # dont chaque couche est independante ne porte rien. C'est le controle qui dit que l'echelle lit
    # la matiere et non sa propre mecanique.
    def _tournante(couches: int, sur: int) -> np.ndarray:
        """Une pile dont les fibres tournent d'un QUART DE TOUR sur `sur` couches."""
        return np.stack([
            100.0 + 40.0 * np.cos(2.0 * np.pi * (np.cos(np.radians(90.0 * k / float(sur))) * yy
                                                 + np.sin(np.radians(90.0 * k / float(sur))) * xx)
                                  / 12.0)
            for k in range(couches)]).astype(np.float32)

    # ⚠⚠ LE MEME TOUR TOTAL ETALE SUR PLUS OU MOINS DE COUCHES : le nombre de couches s'annule dans
    # la comparaison, donc ce qui reste est la VITESSE a laquelle la matiere change en profondeur.
    # C'est l'identite que `179` emploie pour departager deux escaliers.
    montees = [0, 1, 2, 4, 8, 16]
    portees = []
    for sur in (4, 32):
        bl = _tournante(48, sur)
        a2, c2 = orientation_profile(bl)
        lu = lechelle_sur_un_bloc(bl, a2, c2, montees, DEPARTS_PAR_COUCHE, 40)
        po = la_portee_en_profondeur(lu["barreaux"])
        portees.append(po)
        v(f"une pile qui tourne d'un quart de tour sur {sur} couches rend une portée",
          po.get("decidable"), str(po))
    v("★★★★ une matière qui tourne PLUS LENTEMENT porte PLUS LOIN",
      all(p.get("decidable") for p in portees)
      and (portees[1].get("au_dela_de_lechelle")
           or (portees[0].get("portee_en_couches") is not None
               and portees[1].get("portee_en_couches") is not None
               and portees[1]["portee_en_couches"] > portees[0]["portee_en_couches"])),
      f"{portees[0].get('portee_en_couches')} contre {portees[1].get('portee_en_couches')}")

    # ⚠⚠⚠ ET UNE PILE AUX COUCHES IDENTIQUES N'A PAS DE PORTEE A LIRE : le melange y est l'IDENTITE,
    # donc il n'enleve rien, et « l'avance s'annule au premier barreau » se lirait comme une portee
    # nulle alors que la matiere porte partout. C'est la sonde qui a fait naitre la troisieme issue.
    proche = np.stack([100.0 + 40.0 * np.cos(2.0 * np.pi * yy / 12.0)
                       for _ in range(24)]).astype(np.float32)
    a4, c4 = orientation_profile(proche)
    lu4 = lechelle_sur_un_bloc(proche, a4, c4, montees, DEPARTS_PAR_COUCHE, 40)
    po4 = la_portee_en_profondeur(lu4["barreaux"])
    v("★★★★ une pile aux couches identiques n'a PAS de portée à lire",
      not po4.get("decidable") and "séparent jamais" in po4.get("raison", ""), str(po4))

    # ⚠⚠ ET LE MELANGE NE DOIT RIEN CHANGER A MONTEE NULLE : un ruban qui ne quitte pas sa couche
    # lit la meme matiere dans les deux cas, donc l'excedent y vaut zero.
    a3, c3 = orientation_profile(proche)
    lu3 = lechelle_sur_un_bloc(proche, a3, c3, montees, DEPARTS_PAR_COUCHE, 40)
    v("à montée nulle, le mélange ne change rien", abs(lu3["barreaux"][0]["excedent"]) < 1e-9,
      str(lu3["barreaux"][0]))

    # ⚠⚠ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(courbe):
        return {"decidable": True, "segment": "x", "chunks_lus": 9, "refuses": {},
                "courbe": courbe, "plafond_du_ruban_median": 30,
                "portee_mediane_en_couches": 8, "chunks_sans_portee": 0, "chunks": []}

    mont = lechelle_des_montees(vx, pas)
    bonne = [_b(m, (0.0 if i == 0 else (6.0 - i if i < 6 else -1.0)))
             for i, m in enumerate(mont)]
    jamais = [_b(m, (0.0 if i == 0 else 6.0 - 0.5 * i)) for i, m in enumerate(mont)]
    tout_au_bout = [_b(m, (0.0 if i == 0 else (6.0 if i < len(mont) - 1 else -1.0)))
                    for i, m in enumerate(mont)]
    bon_etalon = {"la_portee_croit_avec_la_lenteur": True,
                  "la_matiere_qui_ne_tourne_pas_ne_se_separe_jamais": True,
                  "la_portee_la_plus_courte": 8, "la_portee_la_plus_longue": 32,
                  "portees_lues": [8, 16, 32, None]}
    r1 = juger([_seg(bonne)], bon_etalon, mont, vx, pas)
    v("un étalon qui ordonne ses portées rend le premier énoncé",
      r1["letalon_ordonne_les_portees"])
    v("la portée du rouleau est lue", r1["la_portee_se_lit_sur_le_rouleau"]
      and r1["portee_en_couches"] == mont[6], str(r1["portee_en_couches"]))
    v("et elle est publiée en micromètres",
      abs(r1["portee_um"] - mont[6] * vx) < 1e-9, str(r1["portee_um"]))
    v("elle ne franchit pas un pas entre deux feuilles",
      not r1["elle_franchit_un_pas_entre_deux_feuilles"],
      f"{r1['portee_um']} contre {pas}")
    # ⚠⚠⚠ ET L'ENONCE DOIT POUVOIR REUSSIR : le dernier barreau EST le pas entre deux feuilles,
    # donc une portee qui l'atteint le franchit. Sans ce barreau, l'echelle s'arreterait a 64
    # couches et l'enonce serait une verification qui ne peut pas reussir.
    r2 = juger([_seg(tout_au_bout)], bon_etalon, mont, vx, pas)
    v("★★★★ une portée au dernier barreau franchit un pas entre deux feuilles",
      r2["elle_franchit_un_pas_entre_deux_feuilles"],
      f"{r2['portee_um']} contre {pas}")
    v("et ce dernier barreau est bien le pas entre deux feuilles",
      abs(mont[-1] * vx - pas) < vx, f"{mont[-1] * vx} contre {pas}")
    r3 = juger([_seg(jamais)], bon_etalon, mont, vx, pas)
    v("une avance qui ne s'annule jamais retire le deuxième énoncé",
      not r3["la_portee_se_lit_sur_le_rouleau"] and r3["au_dela_de_lechelle"])
    # ⚠⚠⚠ MAIS ELLE FRANCHIT LE PAS : depasser l'echelle entiere, c'est porter plus loin que son
    # dernier barreau, et ce barreau EST le pas. La branche manquait a une premiere version.
    v("★★★★ mais une portée hors de l'échelle FRANCHIT un pas entre deux feuilles",
      r3["elle_franchit_un_pas_entre_deux_feuilles"], str(r3["portee_minimale_um"]))
    v("et la borne inférieure est publiée en micromètres",
      abs(r3["portee_minimale_um"] - mont[-1] * vx) < 1e-9, str(r3["portee_minimale_um"]))
    v("et une portée LUE sous le pas ne le franchit pas",
      not r1["elle_franchit_un_pas_entre_deux_feuilles"]
      and r1["portee_minimale_um"] == r1["portee_um"], str(r1["portee_minimale_um"]))
    for cle in ("la_portee_croit_avec_la_lenteur",
                "la_matiere_qui_ne_tourne_pas_ne_se_separe_jamais"):
        r4 = juger([_seg(bonne)], {**bon_etalon, cle: False}, mont, vx, pas)
        v(f"★ un étalon qui perd « {cle} » retire le premier énoncé",
          not r4["letalon_ordonne_les_portees"])
    vide = juger([{"decidable": False, "segment": "x"}], bon_etalon, mont, vx, pas)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "jusquou_une_surface_peut_elle_deriver.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return len(echecs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
