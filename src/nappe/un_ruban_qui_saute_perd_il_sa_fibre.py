"""Un ruban qui saute perd-il sa fibre ? — le critère du prix pris comme TÉMOIN et non comme ancre.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL REDRESSE LA QUESTION QUE `R4-P35` POSAIT. `185` a mesuré la
longueur suivable et l'a comparée au pas entre deux feuilles ; `186` a fermé la voie de la
résolution. La porte demandait ensuite si la minorité qui franchit déjà **ancre** un transfert de
spire à spire. ⚠⚠⚠ Or une fibre ne traverse PAS une frontière de feuille : elle appartient à une
feuille et s'arrête avec elle. Elle ne peut donc pas être l'ancre du saut. Ce que le prix demande est
l'inverse, et sa phrase le dit : « follow horizontal papyrus fibers... **and not jumping between
sheets** ». La continuité d'une fibre est le **TÉMOIN** qu'on n'a PAS sauté.

⭐⭐⭐⭐ ET C'EST EXACTEMENT CE QUE L'HUMAIN FAIT AU TRANSFERT. Il regarde si la surface qu'il vient
de poser est encore sur la même feuille, et il corrige quand elle a sauté. Un témoin automatique de
ce saut-là est donc, mot pour mot, ce qui le remplace. `185` ne l'avait mesuré que par PROCURATION —
une longueur comparée à une distance ; ici le saut est **construit** et le témoin est mis à
l'épreuve dessus.

⭐⭐⭐⭐ LE RUBAN EST L'OBJET QUI MANQUAIT. Une surface de segmentation n'est pas une couche : elle
avance latéralement **et** dérive en profondeur. Un `ruban` est une marche de `185` dont la
profondeur **monte** d'un bout à l'autre. Il lit la matière comme une segmentation la lit.

⚠⚠⚠ ET LE CONTRÔLE QUI DÉCIDE EST LE RUBAN QUI DÉRIVE SANS TRAVERSER. Sans lui, un témoin qui
pénalise n'importe quel mouvement en profondeur passerait pour un détecteur de saut — et il serait
inutilisable, puisqu'une vraie feuille dérive. Les deux groupes ont donc **exactement la même
montée** ; seule leur profondeur de départ change, et c'est la MATIÈRE qui décide lequel traverse.

⚠⚠ L'ANGLE EST CELUI DE LA COUCHE DE DÉPART, TENU FIXE. C'est ce qu'un pipeline connaît : on est sur
une feuille, on lit sa direction de fibres, et on avance. Si le ruban passe sur une autre feuille
dont les fibres pointent ailleurs, la marche quitte la crête — et c'est précisément l'effet mesuré.

Usage :
    uv run python src/nappe/un_ruban_qui_saute_perd_il_sa_fibre.py --verifier
    uv run python src/nappe/un_ruban_qui_saute_perd_il_sa_fibre.py \\
        --json docs/mesures/un_ruban_qui_saute_perd_il_sa_fibre.json
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

from la_coupe_cherchee_trouve_t_elle_la_frontiere import COUCHES_DE_LA_CAMPAGNE  # noqa: E402
from de_quoi_une_frontiere_est_elle_faite import plusieurs_creux  # noqa: E402
from fiber_orientation import orientation_profile  # noqa: E402
from jusquou_suit_on_une_fibre import DEPARTS_PAR_COUCHE, les_departs, suivre  # noqa: E402
from la_coherence_creuse_t_elle_a_la_frontiere import (CONTRASTE_DE_LA_FIXTURE,  # noqa: E402
                                                       PLIS_DE_LA_FIXTURE,
                                                       les_frontieres_de_la_fixture)
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PLANCHER_DE_COHERENCE, SEGMENTS, les_chunks,
                                             les_volumes)
from langle_publie_est_il_celui_des_fibres import direction_des_fibres_deg  # noqa: E402
from quelle_fenetre_lit_une_bascule import bloc_de_la_fixture  # noqa: E402
from suit_on_plus_loin_quand_le_voxel_est_plus_fin import le_plafond  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20260927
DECALAGES_DE_LA_FIXTURE = 6
# ⚠⚠ LES DEUX RECOUVREMENTS DE L'ETALON SONT RELUS DE `179`, JAMAIS CHOISIS : le RASOIR, que `179`
# nomme comme le controle vide (une frontiere sans recouvrement, qui ne creuse pas la coherence), et
# **45,6** µm, la plus petite transition ou le creux tombe sur la frontiere a TOUS les decalages.
# Les deux bornent ce qu'une frontiere peut etre, donc l'ecart entre elles dit ce qu'un recouvrement
# coute au temoin.
RECOUVREMENTS_DE_LA_FIXTURE_UM = (0.0, 45.6)
RECOUVREMENT_DE_LA_FIXTURE_UM = 45.6


def un_ruban(bloc: np.ndarray, departs, couche_de_depart: int, angle_deg: float, montee: int,
             plafond: int, plancher: float | None = None) -> list[int]:
    """La marche de `185`, mais dont la PROFONDEUR monte d'un bout à l'autre du parcours.

    ⭐⭐⭐⭐ À MONTÉE NULLE C'EST EXACTEMENT LE SUIVEUR DE `185`, et la batterie le vérifie contre lui
    plutôt que de l'affirmer : un ruban est une généralisation, pas un second suiveur. Le pas vaut un
    voxel, le recentrage ±1 voxel perpendiculaire, et la mesure est la plus longue suite de pas
    restés au-dessus du plancher.

    ⚠⚠⚠ LE PLANCHER EST CELUI DE CHAQUE COUCHE, ET UNE PREMIÈRE VERSION PRENAIT CELUI DU BLOC —
    C'ÉTAIT UN DÉFAUT, ET UN INSTRUMENT L'A TRANCHÉ APRÈS DEUX HYPOTHÈSES FAUSSES. Une matière
    empilée porte un PROFIL DE DENSITÉ en profondeur — dans la fixture il vaut quarante d'amplitude
    contre vingt pour les fibres — donc un plancher pris sur tout le bloc fait tomber des couches
    entières sous lui et casse la suite pour une raison qui n'est PAS la fibre. Les longueurs
    déclinaient alors continûment avec la couche de départ, sans aucune marche à la frontière. Le
    plancher de chaque couche est celui de `185`, et il ne retire que ce qui ne doit pas être lu.

    ⚠ La profondeur est arrondie à la couche : un ruban lit la matière telle qu'elle est
    échantillonnée, pas une interpolation qu'aucun voxel ne porte.

    ⭐ `couche_de_depart` ET `angle_deg` ACCEPTENT UN TABLEAU, un par départ, et c'est ce qui permet
    de marcher des rubans partis de PROFONDEURS DIFFÉRENTES dans un seul passage. Un second suiveur
    écrit pour ça aurait été une seconde définition de la marche, libre de diverger ; ici c'est la
    même, et la batterie vérifie que la forme en tableau rend EXACTEMENT ce que rend la forme
    scalaire.
    """
    couches, h, w = bloc.shape
    planchers = (np.full(couches, float(plancher), dtype=float) if plancher is not None
                 else np.median(bloc.reshape(couches, -1), axis=1).astype(float))
    n = len(departs)
    if n == 0 or int(plafond) <= 0:
        return []
    ang = np.asarray(angle_deg, dtype=float)
    kd = np.asarray(couche_de_depart, dtype=float)
    if ang.ndim == 0:
        ang = np.full(n, float(ang))
    if kd.ndim == 0:
        kd = np.full(n, float(kd))
    th = np.radians(ang)
    ux, uy = np.cos(th), np.sin(th)
    px, py = -uy, ux
    idx = np.arange(n)
    y = np.array([float(d[0]) for d in departs])
    x = np.array([float(d[1]) for d in departs])
    vivant = np.ones(n, dtype=bool)
    suite = np.zeros(n, dtype=np.int64)
    meilleure = np.zeros(n, dtype=np.int64)
    ecarts = np.array([-1.0, 0.0, 1.0])
    for t in range(1, int(plafond) + 1):
        k = np.clip(np.rint(kd + float(montee) * t / float(plafond)).astype(np.int64),
                    0, couches - 1)
        ny, nx = y + uy, x + ux
        cy = np.rint(ny[None, :] + ecarts[:, None] * py[None, :]).astype(np.int64)
        cx = np.rint(nx[None, :] + ecarts[:, None] * px[None, :]).astype(np.int64)
        dedans = (cy >= 0) & (cy < h) & (cx >= 0) & (cx < w)
        val = np.where(dedans,
                       bloc[np.broadcast_to(k, (3, n)), np.clip(cy, 0, h - 1),
                            np.clip(cx, 0, w - 1)], -np.inf)
        meilleur = np.argmax(val, axis=0)
        v = val[meilleur, idx]
        vivant = vivant & np.isfinite(v)
        y = np.where(vivant, cy[meilleur, idx].astype(float), y)
        x = np.where(vivant, cx[meilleur, idx].astype(float), x)
        au_dessus = vivant & (v > planchers[k])
        suite = np.where(au_dessus, suite + 1, 0)
        meilleure = np.maximum(meilleure, suite)
    return [int(m) for m in meilleure]


def la_montee_du_ruban(frontieres) -> int:
    """De combien de couches un ruban monte : la MOITIÉ de l'espacement entre deux frontières.

    ⭐⭐⭐⭐ C'EST LA SEULE MONTÉE QUI PRODUIT LES DEUX GROUPES. Plus grande, tout ruban traverserait
    et le contrôle n'existerait pas ; plus petite, presque aucun ne traverserait. La moitié est aussi
    la borne que `184` a dérivée pour sa plage de décalage, et pour la même raison : au-delà, une
    frontière tomberait sur la suivante.

    ⚠ Elle se lit dans la MATIÈRE — l'espacement des frontières que cette matière-là porte — et
    jamais dans une constante tapée. Une matière qui n'en porte pas deux ne dit pas quoi que ce soit
    sur l'espacement, donc elle n'est pas décidable.
    """
    f = sorted({int(x) for x in frontieres})
    if len(f) < 2:
        return 0
    ecarts = [b - a for a, b in zip(f, f[1:])]
    return max(1, int(round(float(statistics.median(ecarts)) / 2.0)))


def traverse_t_il(couche_de_depart: int, montee: int, frontieres) -> bool:
    """Le ruban traverse-t-il une frontière, c'est-à-dire en contient-il une STRICTEMENT dedans ?

    ⚠ Strictement : un ruban qui s'arrête SUR une frontière ne l'a pas franchie, et compter son
    extrémité ferait traverser tout ruban qui l'effleure.
    """
    bas = min(int(couche_de_depart), int(couche_de_depart) + int(montee))
    haut = max(int(couche_de_depart), int(couche_de_depart) + int(montee))
    return any(bas < int(f) < haut for f in frontieres)


def les_profondeurs_de_depart(coherences, montee: int,
                              plancher: float = PLANCHER_DE_COHERENCE) -> list[int]:
    """Les couches de départ admissibles : TEXTURÉES, et qui laissent passer la montée entière.

    ⚠⚠ UN DÉPART SUR UNE COUCHE SANS TEXTURE MESURERAIT LE BRUIT, et c'est la règle du producteur
    que toute la chaîne suit depuis `176` : on ne lit que les couches dont la cohérence dépasse son
    plancher. ⚠ Et une montée tronquée par le bord du bloc ferait deux groupes de longueurs
    différentes, donc le ruban doit tenir entier.
    """
    n = len(coherences)
    m = int(montee)
    out = []
    for k in range(n):
        if float(coherences[k]) <= float(plancher):
            continue
        if 0 <= k + m < n and 0 <= k < n:
            out.append(int(k))
    return out


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def le_plafond_du_ruban(bloc: np.ndarray, angles, coherences, combien: int, plafond_max: int,
                        plancher_de_coherence: float, plancher: float | None = None) -> int:
    """Le plafond d'un ruban : la longueur qu'une fibre SURVIT sur cette matiere-la, lue a plat.

    ⚠⚠⚠ C'EST LE DEFAUT QUE LA PREMIERE VERSION A PAYE, ET IL RENDAIT LA MESURE AVEUGLE PAR
    CONSTRUCTION. Le plafond valait celui de `185` — de quoi franchir un pas entre deux feuilles,
    soit 146 pas — alors qu'une fibre n'en survit qu'une vingtaine. La montee s'etalait donc sur tout
    le parcours et la traversee arrivait LONGTEMPS APRES que la crete etait morte : les deux groupes
    rendaient la meme chose, et l'etalon a montre nu que le temoin ne voyait pas une frontiere POSEE.

    ⭐⭐⭐⭐ UNE FIBRE NE PEUT TEMOIGNER QUE D'UNE TRAVERSEE QUI ARRIVE DANS SA PROPRE LONGUEUR. Le
    plafond se lit donc dans la matiere : c'est la longueur que le ruban PLAT atteint ici, par le
    meme suiveur et les memes departs. Une valeur choisie en aurait fait un reglage ; celle-ci est
    une propriete de la matiere lue.

    ⚠ Elle vaut au moins un pas : un plafond nul ne ferait marcher personne.

    ⚠⚠ LE PLANCHER RESTE CELUI DE CHAQUE COUCHE : le plafond doit se lire avec exactement la règle
    qui servira ensuite, sinon il bornerait les rubans avec une autre lecture que la leur.
    """
    lus = []
    for k in les_profondeurs_de_depart(coherences, 0, plancher_de_coherence):
        ang = float(direction_des_fibres_deg(float(angles[k])))
        departs = les_departs(bloc[k], combien)
        if not departs:
            continue
        m = _med(un_ruban(bloc, departs, k, ang, 0, int(plafond_max), plancher))
        if m is not None:
            lus.append(m)
    return max(1, int(round(float(statistics.median(lus))))) if lus else 0


def la_pente_du_ruban(montee: int, plafond: int) -> float:
    """De combien de couches le ruban descend par pas lateral — la pente qu'il faut pour traverser.

    ⭐ ELLE EST PUBLIEE PARCE QU'ELLE EST LA LIMITE GEOMETRIQUE DE TOUTE LA TRANCHE : une fibre ne
    peut temoigner que d'une traversee qui arrive dans sa longueur, donc une surface qui derive plus
    LENTEMENT que cette pente ne sera jamais prise en faute par une fibre, quelle que soit la qualite
    du temoin.
    """
    return round(float(montee) / float(plafond), 4) if plafond else 0.0


def les_deux_groupes(bloc: np.ndarray, angles, coherences, frontieres, montee: int,
                     combien: int, plafond: int, plancher_de_coherence: float,
                     plancher: float | None = None) -> dict:
    """Les rubans qui traversent contre ceux qui dérivent autant sans traverser.

    ⭐⭐⭐⭐ LES DEUX GROUPES ONT LA MÊME MONTÉE ET LE MÊME PLAFOND : ce qui les sépare est la
    profondeur de départ, et c'est la MATIÈRE qui décide lequel traverse. Aucun réglage ne distingue
    un groupe de l'autre.

    ⚠⚠ LES DEUX SENS DE MONTÉE SONT LUS. Une segmentation dérive vers l'intérieur comme vers
    l'extérieur ; n'en lire qu'un ferait dépendre le résultat du sens où le bloc a été empilé.
    """
    traversent, restent, plats = [], [], []
    couches = bloc.shape[0]
    for signe in (1, -1):
        m = int(signe) * int(montee)
        for k in les_profondeurs_de_depart(coherences, m, plancher_de_coherence):
            # ⚠⚠ L'ANGLE EST CELUI DE LA COUCHE DE DEPART, tenu fixe le long du ruban : c'est ce
            # qu'un pipeline connait, et c'est ce qui rend le saut visible.
            ang = float(direction_des_fibres_deg(float(angles[k])))
            departs = les_departs(bloc[k], combien)
            if not departs:
                continue
            lu = un_ruban(bloc, departs, k, ang, m, plafond, plancher)
            if not lu:
                continue
            cible = traversent if traverse_t_il(k, m, frontieres) else restent
            cible.append(_med(lu))
            if signe == 1:
                plats.append(_med(un_ruban(bloc, departs, k, ang, 0, plafond, plancher)))
    traversent = [x for x in traversent if x is not None]
    restent = [x for x in restent if x is not None]
    plats = [x for x in plats if x is not None]
    return {"decidable": bool(traversent and restent),
            "rubans_qui_traversent": len(traversent), "rubans_qui_restent": len(restent),
            "couches": int(couches), "montee": int(montee),
            "pas_en_traversant": _med(traversent), "pas_en_restant": _med(restent),
            "pas_a_plat": _med(plats),
            "ce_que_le_saut_coute": (round(_med(restent) - _med(traversent), 3)
                                     if traversent and restent else None),
            # ⚠⚠ CE QUE LA DERIVE COUTE SE PUBLIE A COTE DE CE QUE LE SAUT COUTE, et les deux ne
            # disent pas la meme chose : deriver, c'est changer de couche ; sauter, c'est changer de
            # feuille. Un temoin qui ne separerait pas les deux serait un detecteur de mouvement.
            "ce_que_la_derive_coute": (round(_med(plats) - _med(restent), 3)
                                       if plats and restent else None),
            "il_en_reste_la_part": (round(_med(traversent) / _med(restent), 4)
                                    if traversent and restent and _med(restent) else None)}


def contre_le_melange_des_couches(bloc: np.ndarray, angles, coherences, frontieres, montee: int,
                                  combien: int, plafond: int, plancher_de_coherence: float,
                                  graine: int = GRAINE) -> dict:
    """Le MÊME calcul sur un bloc dont l'ORDRE DES COUCHES est mélangé — le nul de la tranche.

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE APPARIÉ, ET IL PRICE EXACTEMENT LA BONNE CHOSE. Mélanger l'ordre des
    couches garde chaque couche intacte — même texture, même direction de fibres, même histogramme —
    et détruit seulement le fait que deux couches voisines appartiennent à la même feuille. Les
    étiquettes « traverse » et « reste » viennent des frontières d'ORIGINE, donc après le mélange
    elles ne désignent plus rien : les deux groupes doivent s'égaler.

    ⚠⚠ SANS LUI, « UN RUBAN QUI TRAVERSE PERD SA FIBRE » SERAIT INDISCERNABLE DE « UN RUBAN QUI PART
    D'UNE COUCHE PROFONDE PERD SA FIBRE ». Le mélange conserve la loi des profondeurs de départ et
    supprime la contiguïté — c'est la seule chose qu'on met à l'épreuve.
    """
    r = np.random.default_rng(int(graine))
    ordre = r.permutation(bloc.shape[0])
    return les_deux_groupes(bloc[ordre], np.asarray(angles)[ordre], np.asarray(coherences)[ordre],
                            frontieres, montee, combien, plafond, plancher_de_coherence)


def sur_la_fixture(decalages: int = DECALAGES_DE_LA_FIXTURE, combien: int = DEPARTS_PAR_COUCHE,
                   plis: int = PLIS_DE_LA_FIXTURE,
                   recouvrements=RECOUVREMENTS_DE_LA_FIXTURE_UM,
                   graine: int = GRAINE) -> dict:
    """Une matière dont les frontières sont POSÉES — la réponse est connue avant la mesure.

    ⭐⭐⭐⭐ SANS CET ÉTALON, UN ÉCART SUR LE ROULEAU NE VEUT RIEN DIRE. Ici chaque feuille porte deux
    plis dont les fibres font quatre-vingt-dix degrés d'écart, et les couches où ça change sont
    calculées et non relues. Un ruban qui les traverse DOIT perdre sa crête ; un ruban qui dérive
    autant sans les traverser DOIT la garder.

    ⚠ Le recouvrement est celui que `179` a encadré, et les frontières viennent de la fonction qui
    les dérive du pas — deux nombres relus de leur mesure, jamais retapés.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    plafond = le_plafond(vx, pas)
    lignes = []
    for rec, i in [(r, i) for r in recouvrements for i in range(int(decalages))]:
        dec = pas * i / float(decalages)
        bloc = bloc_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, dec, CONTRASTE_DE_LA_FIXTURE, int(plis),
                                  vx, pas, transition_um=float(rec))
        frontieres = les_frontieres_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, dec, int(plis), vx, pas)
        montee = la_montee_du_ruban(frontieres)
        if not montee:
            continue
        ang, coh = orientation_profile(bloc)
        # ⚠⚠⚠ LE PLAFOND DU RUBAN SE LIT DANS LA MATIERE, il n'est pas celui de `185` : sinon la
        # traversee arrive apres la mort de la crete et le temoin est aveugle par construction.
        pl = le_plafond_du_ruban(bloc, ang, coh, combien, plafond, PLANCHER_DE_COHERENCE)
        if not pl:
            continue
        lu = les_deux_groupes(bloc, ang, coh, frontieres, montee, combien, pl,
                              PLANCHER_DE_COHERENCE)
        nul = contre_le_melange_des_couches(bloc, ang, coh, frontieres, montee, combien, pl,
                                            PLANCHER_DE_COHERENCE, graine)
        lignes.append({"recouvrement_um": round(float(rec), 3),
                       "decalage_um": round(float(dec), 3), "frontieres": len(frontieres),
                       "plafond_du_ruban": int(pl),
                       "pente_en_couches_par_pas": la_pente_du_ruban(montee, pl),
                       **lu, "le_nul": nul})
    lisibles = [x for x in lignes if x.get("decidable")]
    couts = [x["ce_que_le_saut_coute"] for x in lisibles
             if x["ce_que_le_saut_coute"] is not None]
    nuls = [x["le_nul"]["ce_que_le_saut_coute"] for x in lisibles
            if x["le_nul"].get("ce_que_le_saut_coute") is not None]
    par_recouvrement = []
    for rec in recouvrements:
        c = [x["ce_que_le_saut_coute"] for x in lisibles
             if abs(x["recouvrement_um"] - float(rec)) < 1e-9
             and x["ce_que_le_saut_coute"] is not None]
        n = [x["le_nul"]["ce_que_le_saut_coute"] for x in lisibles
             if abs(x["recouvrement_um"] - float(rec)) < 1e-9
             and x["le_nul"].get("ce_que_le_saut_coute") is not None]
        par_recouvrement.append({"recouvrement_um": round(float(rec), 3),
                                 "decalages_lisibles": len(c),
                                 "decalages_ou_le_saut_coute": int(sum(1 for y in c if y > 0)),
                                 "cout_median": _med(c), "nul_median": _med(n)})
    return {"decalages": int(decalages), "plis": int(plis),
            "recouvrements_um": [float(r) for r in recouvrements],
            "par_recouvrement": par_recouvrement,
            "plafond_de_pas": int(plafond),
            "lignes": lignes, "decalages_lisibles": len(lisibles),
            "decalages_ou_le_saut_coute": int(sum(1 for c in couts if c > 0)),
            "cout_median_du_saut": _med(couts), "cout_median_du_nul": _med(nuls),
            "montee_mediane": (int(statistics.median_low([x["montee"] for x in lisibles]))
                               if lisibles else None),
            "plafond_du_ruban_median": (int(statistics.median_low(
                [x["plafond_du_ruban"] for x in lisibles])) if lisibles else None),
            "pente_mediane": _med([x["pente_en_couches_par_pas"] for x in lisibles]),
            "pas_a_plat_median": _med([x["pas_a_plat"] for x in lisibles
                                       if x["pas_a_plat"] is not None]),
            "cout_median_de_la_derive": _med([x["ce_que_la_derive_coute"] for x in lisibles
                                              if x["ce_que_la_derive_coute"] is not None]),
            "le_saut_coute_a_tous_les_decalages": bool(
                lisibles and all(c > 0 for c in couts) and len(couts) == len(lisibles)),
            # ⚠ UN RECOUVREMENT ADOUCIT LE SAUT, et c'est mesure sur l'echelle et non affirme : une
            # frontiere qui se recouvre est un saut moins net, donc un temoin moins fort.
            "le_recouvrement_adoucit_le_saut": bool(
                len(par_recouvrement) >= 2
                and all(a["cout_median"] is not None and b["cout_median"] is not None
                        and b["cout_median"] < a["cout_median"]
                        for a, b in zip(par_recouvrement, par_recouvrement[1:])))}


def un_chunk(bloc: np.ndarray, angles, coherences, combien: int, plafond: int,
             graine: int = GRAINE) -> dict:
    """Un chunk du rouleau : ses frontières lues par `181`, puis les deux groupes de rubans."""
    lu = plusieurs_creux([float(c) for c in coherences])
    frontieres = sorted(int(x["couche"]) for x in (lu.get("creux") or [])
                        if x.get("depasse_tous_les_melanges"))
    montee = la_montee_du_ruban(frontieres)
    if not montee:
        return {"decidable": False, "raison": "moins de deux frontières retenues",
                "frontieres": frontieres}
    pl = le_plafond_du_ruban(bloc, angles, coherences, combien, plafond, PLANCHER_DE_COHERENCE)
    if not pl:
        return {"decidable": False, "raison": "aucune couche texturée", "frontieres": frontieres}
    groupes = les_deux_groupes(bloc, angles, coherences, frontieres, montee, combien, pl,
                               PLANCHER_DE_COHERENCE)
    nul = contre_le_melange_des_couches(bloc, angles, coherences, frontieres, montee, combien,
                                        pl, PLANCHER_DE_COHERENCE, graine)
    return {"frontieres": frontieres, "plafond_du_ruban": int(pl),
            "pente_en_couches_par_pas": la_pente_du_ruban(montee, pl), **groupes, "le_nul": nul}


def un_segment(volume: dict, combien: int, plafond: int, cote: int = COTE_DU_TREILLIS,
               delai: float = DELAI, graine: int = GRAINE) -> dict:
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
        lu = un_chunk(bloc.astype(np.float32), ang, coh, combien, plafond, graine)
        if not lu.get("decidable"):
            refus[lu.get("raison", "indécidable")] = refus.get(lu.get("raison", "indécidable"),
                                                               0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)], **lu})
    couts = [x["ce_que_le_saut_coute"] for x in lignes if x["ce_que_le_saut_coute"] is not None]
    nuls = [x["le_nul"]["ce_que_le_saut_coute"] for x in lignes
            if x["le_nul"].get("ce_que_le_saut_coute") is not None]
    return {"decidable": bool(lignes), "segment": volume["segment"], "chunks_lus": len(lignes),
            "refuses": refus,
            "pas_en_traversant": _med([x["pas_en_traversant"] for x in lignes
                                       if x["pas_en_traversant"] is not None]),
            "pas_en_restant": _med([x["pas_en_restant"] for x in lignes
                                    if x["pas_en_restant"] is not None]),
            "pas_a_plat": _med([x["pas_a_plat"] for x in lignes if x["pas_a_plat"] is not None]),
            "cout_median_du_saut": _med(couts),
            "cout_median_de_la_derive": _med([x["ce_que_la_derive_coute"] for x in lignes
                                              if x["ce_que_la_derive_coute"] is not None]),
            "cout_median_du_nul": _med(nuls),
            "chunks_ou_le_saut_coute": int(sum(1 for c in couts if c > 0)),
            "chunks_ou_le_nul_coute": int(sum(1 for c in nuls if c > 0)),
            "montee_mediane": (int(statistics.median_low([x["montee"] for x in lignes]))
                               if lignes else None),
            "plafond_du_ruban_median": (int(statistics.median_low(
                [x["plafond_du_ruban"] for x in lignes])) if lignes else None),
            "pente_mediane": _med([x["pente_en_couches_par_pas"] for x in lignes]),
            "chunks": lignes}


def juger(segments: list[dict], etalon: dict, voxel_um: float, pas_um: float) -> dict:
    """Le témoin du saut : coûte-t-il, et coûte-t-il PLUS que la dérive seule ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    trav = _med([s["pas_en_traversant"] for s in lus if s["pas_en_traversant"] is not None])
    reste = _med([s["pas_en_restant"] for s in lus if s["pas_en_restant"] is not None])
    plat = _med([s["pas_a_plat"] for s in lus if s["pas_a_plat"] is not None])
    cout = _med([s["cout_median_du_saut"] for s in lus if s["cout_median_du_saut"] is not None])
    derive = _med([s["cout_median_de_la_derive"] for s in lus
                   if s.get("cout_median_de_la_derive") is not None])
    nul = _med([s["cout_median_du_nul"] for s in lus if s["cout_median_du_nul"] is not None])
    chunks = int(sum(s["chunks_lus"] for s in lus))
    ou = int(sum(s["chunks_ou_le_saut_coute"] for s in lus))
    ou_nul = int(sum(s["chunks_ou_le_nul_coute"] for s in lus))
    return {"decidable": True, "segments": len(lus), "chunks_lus": chunks,
            "pas_en_traversant": trav, "pas_en_restant": reste, "pas_a_plat": plat,
            "en_traversant_um": (round(trav * float(voxel_um), 3)
                                 if trav is not None else None),
            "en_restant_um": (round(reste * float(voxel_um), 3)
                              if reste is not None else None),
            "ce_que_le_saut_coute": cout,
            "ce_que_le_saut_coute_um": (round(cout * float(voxel_um), 3)
                                        if cout is not None else None),
            "ce_que_le_nul_rend": nul,
            "ce_que_la_derive_coute": derive,
            "ce_que_la_derive_coute_um": (round(derive * float(voxel_um), 3)
                                          if derive is not None else None),
            "la_derive_de_letalon": etalon.get("cout_median_de_la_derive"),
            "pas_a_plat_de_letalon": etalon.get("pas_a_plat_median"),
            "il_en_reste_la_part": (round(trav / reste, 4)
                                    if trav is not None and reste else None),
            "chunks_ou_le_saut_coute": ou, "chunks_ou_le_nul_coute": ou_nul,
            "le_pas_entre_deux_feuilles_um": float(pas_um),
            "montee_mediane": (int(statistics.median_low(
                [s["montee_mediane"] for s in lus if s["montee_mediane"] is not None]))
                if any(s["montee_mediane"] is not None for s in lus) else None),
            "plafond_du_ruban_median": (int(statistics.median_low(
                [s["plafond_du_ruban_median"] for s in lus
                 if s["plafond_du_ruban_median"] is not None]))
                if any(s["plafond_du_ruban_median"] is not None for s in lus) else None),
            "pente_mediane": _med([s["pente_mediane"] for s in lus
                                   if s["pente_mediane"] is not None]),
            "la_pente_de_letalon": etalon.get("pente_mediane"),
            "plafond_du_ruban_de_letalon": etalon.get("plafond_du_ruban_median"),
            "le_cout_de_letalon": etalon.get("cout_median_du_saut"),
            "le_recouvrement_adoucit_le_saut": bool(etalon.get("le_recouvrement_adoucit_le_saut")),
            "le_cout_par_recouvrement": etalon.get("par_recouvrement"),
            "le_nul_de_letalon": etalon.get("cout_median_du_nul"),
            "decalages_ou_le_saut_coute_sur_letalon": etalon.get("decalages_ou_le_saut_coute"),
            "decalages_lisibles_de_letalon": etalon.get("decalages_lisibles"),
            # ⚠⚠ TROIS ENONCES, ET LE PREMIER CONDITIONNE LES AUTRES. Si le temoin ne voit pas un
            # saut CONSTRUIT, ce qu'il rend sur le rouleau ne se lit pas.
            "le_temoin_voit_un_saut_construit": bool(
                etalon.get("le_saut_coute_a_tous_les_decalages")),
            "le_saut_coute_sur_le_rouleau": bool(cout is not None and cout > 0.0),
            # ⚠⚠⚠ ET LE COUT DOIT DEPASSER CELUI DU NUL : sur un bloc dont l'ordre des couches est
            # melange, « traverser » ne designe plus rien, donc ce que le nul rend est ce que la
            # liberte de decouper deux groupes rapporte toute seule.
            "le_saut_coute_plus_que_le_hasard": bool(
                cout is not None and nul is not None and cout > nul),
            # ⚠⚠⚠ ET L'ENONCE QUI SEPARE LES DEUX EFFETS : sur une matiere ou changer de feuille
            # coute, le saut doit couter PLUS que la simple derive en profondeur. S'il coute moins,
            # le ruban lit un mouvement et non une frontiere.
            "le_saut_coute_plus_que_la_derive": bool(
                cout is not None and derive is not None and cout > derive)}


def mesurer(segments_n: int = SEGMENTS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    plafond = le_plafond(vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    etalon = sur_la_fixture(combien=combien)
    segs = [un_segment(v, combien, plafond, cote) for v in volumes]
    return {"departs_par_couche": int(combien), "cote_du_treillis": int(cote),
            "plafond_de_pas": int(plafond), "voxel_um": vx, "pas_um": pas, "graine": int(GRAINE),
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "recouvrements_de_la_fixture_um": [float(x)
                                               for x in RECOUVREMENTS_DE_LA_FIXTURE_UM],
            "letalon": etalon, "les_segments": segs,
            "le_verdict": juger(segs, etalon, vx, pas)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("UN RUBAN QUI SAUTE PERD-IL SA FIBRE ?")
    print(f"  {r['departs_par_couche']} départs par couche · treillis "
          f"{r['cote_du_treillis']}×{r['cote_du_treillis']} · plafond {r['plafond_de_pas']} pas · "
          f"voxel {r['voxel_um']} µm")
    print()
    print(f"  L'ÉTALON — frontières posées, recouvrements {e['recouvrements_um']} µm, montée "
          f"{e['montee_mediane']} couches, plafond {e['plafond_du_ruban_median']}")
    for x in e["par_recouvrement"]:
        print(f"     recouvrement {x['recouvrement_um']:>6} µm · coûte à "
              f"{x['decalages_ou_le_saut_coute']}/{x['decalages_lisibles']} décalages · médiane "
              f"{x['cout_median']} · nul {x['nul_median']}")
    for x in e["lignes"]:
        print(f"     r {x['recouvrement_um']:>5} · décalage {x['decalage_um']:>7} µm · "
              f"{x['frontieres']} frontières · "
              f"traversent {x['rubans_qui_traversent']} / restent {x['rubans_qui_restent']} · "
              f"en traversant {x['pas_en_traversant']} contre {x['pas_en_restant']} · coûte "
              f"{x['ce_que_le_saut_coute']} · nul {x['le_nul']['ce_que_le_saut_coute']}")
    print()
    print("  LE ROULEAU")
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"     {s['segment']} — {s.get('raison', 'rien de lisible')}")
            continue
        print(f"     {s['segment']} · {s['chunks_lus']} chunks · refusés {s['refuses']}")
        print(f"        en traversant {s['pas_en_traversant']} · en restant "
              f"{s['pas_en_restant']} · à plat {s['pas_a_plat']} · coûte "
              f"{s['cout_median_du_saut']} · nul {s['cout_median_du_nul']}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("segments", "chunks_lus", "montee_mediane", "plafond_du_ruban_median",
                "pente_mediane", "plafond_du_ruban_de_letalon", "la_pente_de_letalon",
                "pas_a_plat", "pas_a_plat_de_letalon", "ce_que_la_derive_coute",
                "ce_que_la_derive_coute_um", "la_derive_de_letalon", "pas_en_restant",
                "pas_en_traversant", "en_restant_um", "en_traversant_um",
                "ce_que_le_saut_coute", "ce_que_le_saut_coute_um", "ce_que_le_nul_rend",
                "il_en_reste_la_part", "chunks_ou_le_saut_coute", "chunks_ou_le_nul_coute",
                "le_cout_de_letalon", "le_nul_de_letalon",
                "decalages_ou_le_saut_coute_sur_letalon", "decalages_lisibles_de_letalon",
                "le_temoin_voit_un_saut_construit", "le_recouvrement_adoucit_le_saut",
                "le_saut_coute_sur_le_rouleau",
                "le_saut_coute_plus_que_le_hasard", "le_saut_coute_plus_que_la_derive"):
        print(f"     {cle:<44} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)

    # ⭐⭐⭐⭐ A MONTEE NULLE, LE RUBAN EST EXACTEMENT LE SUIVEUR DE `185`. C'est le controle de non
    # regression de toute la tranche : un ruban est une generalisation, pas un second suiveur, et
    # deux suiveurs libres de diverger rendraient deux longueurs sous un seul nom.
    yy, xx = np.mgrid[0:64, 0:64].astype(np.float32)
    bandes = np.stack([100.0 + 40.0 * np.cos(2.0 * np.pi * yy / 12.0)] * 8).astype(np.float32)
    dep = les_departs(bandes[3], DEPARTS_PAR_COUCHE)
    plancher_couche = float(np.median(bandes[3]))
    plat = un_ruban(bandes, dep, 3, 0.0, 0, 40, plancher_couche)
    ref = [int(suivre(bandes[3], d, 0.0, 40, plancher_couche)["pas"]) for d in dep]
    v("★ à montée nulle, le ruban rend EXACTEMENT ce que rend le suiveur de `185`",
      plat == ref, f"{plat[:5]} contre {ref[:5]}")

    # ⚠⚠ ET IL MARCHE BIEN LE LONG DES CRETES : sur des bandes horizontales, le long va loin et en
    # travers tombe a chaque creux.
    # ⚠ Le plafond depasse la largeur de l'image, donc un depart proche du bord droit meurt avant
    # de l'atteindre : c'est le MAXIMUM qui dit que la marche va jusqu'au bout, pas le minimum.
    v("le ruban va jusqu'au plafond le long des crêtes", max(plat) >= 40, str(max(plat)))
    travers = un_ruban(bandes, dep, 3, 90.0, 0, 40, plancher_couche)
    v("et il tombe en travers", max(travers) < 12, str(max(travers)))
    v("et le long dépasse le travers", _med(plat) > _med(travers),
      f"{_med(plat)} contre {_med(travers)}")

    # ⭐⭐⭐⭐ UN RUBAN QUI TRAVERSE UNE FRONTIERE CONSTRUITE PERD SA CRETE, ET UN RUBAN QUI DERIVE
    # AUTANT SANS TRAVERSER LA GARDE. Les couches 0 a 5 portent des crêtes horizontales, les couches
    # 6 a 11 des crêtes VERTICALES : la frontiere est a 6 et elle est posee, pas relue.
    verticales = np.stack([100.0 + 40.0 * np.cos(2.0 * np.pi * xx / 12.0)] * 6).astype(np.float32)
    horizontales = np.stack([100.0 + 40.0 * np.cos(2.0 * np.pi * yy / 12.0)] * 6).astype(np.float32)
    deux = np.concatenate([horizontales, verticales], axis=0)
    pl = float(np.median(deux))
    dep2 = les_departs(deux[3], DEPARTS_PAR_COUCHE)
    saute = un_ruban(deux, dep2, 3, 0.0, 5, 40, pl)       # 3 -> 8, traverse la couche 6
    dep3 = les_departs(deux[0], DEPARTS_PAR_COUCHE)
    derive = un_ruban(deux, dep3, 0, 0.0, 5, 40, pl)      # 0 -> 5, ne traverse pas
    v("★★★★ un ruban qui traverse une frontière construite perd sa crête",
      _med(saute) < _med(derive), f"{_med(saute)} contre {_med(derive)}")
    v("et celui qui dérive autant sans traverser la garde",
      _med(derive) >= 30, str(_med(derive)))
    v("traverse_t_il dit lequel des deux traverse",
      traverse_t_il(3, 5, [6]) and not traverse_t_il(0, 5, [6]))
    v("et une frontière au bout du ruban n'est pas traversée",
      not traverse_t_il(0, 6, [6]) and not traverse_t_il(6, 5, [6]))
    v("ni une frontière hors du ruban", not traverse_t_il(0, 3, [6]))
    v("un ruban qui descend traverse aussi", traverse_t_il(8, -5, [6]))

    # ⚠⚠ LA MONTEE EST LA MOITIE DE L'ESPACEMENT DES FRONTIERES, lue dans la matiere.
    v("la montée vaut la moitié de l'espacement", la_montee_du_ruban([10, 46, 82]) == 18,
      str(la_montee_du_ruban([10, 46, 82])))
    v("et elle suit un espacement plus serré", la_montee_du_ruban([10, 34, 58]) == 12,
      str(la_montee_du_ruban([10, 34, 58])))
    v("une matière qui ne porte pas deux frontières n'est pas décidable",
      la_montee_du_ruban([10]) == 0 and la_montee_du_ruban([]) == 0)
    v("★ et la montée produit bien les DEUX groupes sur cet espacement",
      any(traverse_t_il(k, 18, [10, 46, 82]) for k in range(10, 46))
      and any(not traverse_t_il(k, 18, [10, 46, 82]) for k in range(10, 46)))
    v("⚠ une montée d'un espacement ENTIER ferait traverser tout le monde",
      all(traverse_t_il(k, 36, [10, 46, 82]) for k in range(11, 46)))

    # ⚠⚠ LES DEPARTS SONT LES COUCHES TEXTUREES, et la montee doit tenir dans le bloc.
    coh = [0.05] * 4 + [0.9] * 10 + [0.05] * 4
    prof = les_profondeurs_de_depart(coh, 5, 0.15)
    v("seules les couches texturées sont des départs",
      all(coh[k] > 0.15 for k in prof), str(prof))
    v("et la montée tient entière dans le bloc",
      all(0 <= k + 5 < len(coh) for k in prof), str(prof))
    v("une montée descendante ne sort pas non plus par le bas",
      all(0 <= k - 5 for k in les_profondeurs_de_depart(coh, -5, 0.15)),
      str(les_profondeurs_de_depart(coh, -5, 0.15)))
    v("une matière sans couche texturée ne rend aucun départ",
      les_profondeurs_de_depart([0.01] * 20, 5, 0.15) == [])

    # ⭐⭐⭐⭐ LE NUL : MELANGER L'ORDRE DES COUCHES DOIT EFFACER L'ECART. Sans lui, « traverser coute »
    # serait indiscernable de « partir d'une couche profonde coute ».
    # ⚠⚠⚠ LES ANGLES VIENNENT DE `orientation_profile`, PAS D'UN TABLEAU FABRIQUE. Une premiere
    # version passait des zeros : `les_deux_groupes` convertit vers la DIRECTION DES FIBRES (`172`),
    # donc la marche partait en travers des cretes et les deux groupes s'inversaient. La sonde
    # exerce ainsi le chemin reel, conversion comprise, et pas seulement la fonction.
    ang2, coh2 = orientation_profile(deux)
    vrai = les_deux_groupes(deux, ang2, coh2, [6], 5, DEPARTS_PAR_COUCHE, 40, 0.15)
    faux = contre_le_melange_des_couches(deux, ang2, coh2, [6], 5, DEPARTS_PAR_COUCHE, 40, 0.15)
    v("★★★★ sur la matière construite, traverser coûte",
      vrai["decidable"] and vrai["ce_que_le_saut_coute"] > 0,
      str(vrai.get("ce_que_le_saut_coute")))
    v("★★★★ et le mélange des couches efface l'écart",
      (faux.get("ce_que_le_saut_coute") is None
       or faux["ce_que_le_saut_coute"] < vrai["ce_que_le_saut_coute"]),
      f"{faux.get('ce_que_le_saut_coute')} contre {vrai['ce_que_le_saut_coute']}")
    v("les deux groupes sont non vides", vrai["rubans_qui_traversent"] > 0
      and vrai["rubans_qui_restent"] > 0,
      f"{vrai['rubans_qui_traversent']} / {vrai['rubans_qui_restent']}")
    v("et les deux sens de montée sont lus",
      vrai["rubans_qui_traversent"] + vrai["rubans_qui_restent"] > 12,
      str(vrai["rubans_qui_traversent"] + vrai["rubans_qui_restent"]))

    # ⚠⚠⚠ LE SECOND DEFAUT PAYE, DEVENU UN CONTROLE NOMME. Une matiere empilee porte un PROFIL DE
    # DENSITE en profondeur ; un plancher pris sur tout le bloc fait alors tomber des couches
    # entieres sous lui et casse la suite pour une raison qui n'est PAS la fibre. Ici toutes les
    # couches portent EXACTEMENT les memes cretes et ne different que par leur niveau moyen : le
    # plancher de chaque couche doit rendre la meme longueur partout, celui du bloc non.
    niveaux = 100.0 + 60.0 * np.cos(2.0 * np.pi * np.arange(12) / 12.0)
    empile = np.stack([niveaux[k] + 20.0 * np.cos(2.0 * np.pi * yy / 12.0)
                       for k in range(12)]).astype(np.float32)
    dep4 = les_departs(empile[0], DEPARTS_PAR_COUCHE)
    par_couche = [_med(un_ruban(empile, dep4, k, 0.0, 0, 30)) for k in range(12)]
    par_bloc = [_med(un_ruban(empile, dep4, k, 0.0, 0, 30, float(np.median(empile))))
                for k in range(12)]
    v("★★★★ avec le plancher de chaque couche, toutes les couches rendent la même longueur",
      len(set(par_couche)) == 1 and par_couche[0] >= 30, str(par_couche))
    v("★★★★ et le plancher du BLOC fait dépendre la longueur du niveau de la couche",
      len(set(par_bloc)) > 1 and min(par_bloc) < max(par_couche),
      str(par_bloc))

    # ⚠⚠⚠ LE DEFAUT QUE CETTE TRANCHE A PAYE, DEVENU UN CONTROLE NOMME. Un ruban dont le plafond
    # depasse largement la longueur qu'une fibre survit est AVEUGLE PAR CONSTRUCTION : sa montee
    # s'etale sur tout le parcours, donc la traversee arrive longtemps apres la mort de la crete et
    # les deux groupes rendent la meme chose. La matiere ci-dessous porte des cretes INTERROMPUES,
    # donc une longueur de fibre finie, et la frontiere est posee a la couche 6.
    coupees = np.stack([
        (100.0 + 40.0 * np.cos(2.0 * np.pi * yy / 12.0)) * (np.mod(xx, 24.0) < 16.0)
        + 100.0 * (np.mod(xx, 24.0) >= 16.0)] * 6).astype(np.float32)
    debout = np.stack([
        (100.0 + 40.0 * np.cos(2.0 * np.pi * xx / 12.0)) * (np.mod(yy, 24.0) < 16.0)
        + 100.0 * (np.mod(yy, 24.0) >= 16.0)] * 6).astype(np.float32)
    finie = np.concatenate([coupees, debout], axis=0)
    angf, cohf = orientation_profile(finie)
    plat_f = le_plafond_du_ruban(finie, angf, cohf, DEPARTS_PAR_COUCHE, 200,
                                 PLANCHER_DE_COHERENCE)
    v("le plafond du ruban se lit dans la matière", 0 < plat_f < 200, str(plat_f))
    lu_juste = les_deux_groupes(finie, angf, cohf, [6], 5, DEPARTS_PAR_COUCHE, plat_f,
                                PLANCHER_DE_COHERENCE)
    lu_aveugle = les_deux_groupes(finie, angf, cohf, [6], 5, DEPARTS_PAR_COUCHE, 10 * plat_f,
                                  PLANCHER_DE_COHERENCE)
    v("★★★★ au plafond lu dans la matière, la traversée coûte",
      lu_juste["decidable"] and lu_juste["ce_que_le_saut_coute"] > 0,
      str(lu_juste.get("ce_que_le_saut_coute")))
    v("★★★★ et un plafond dix fois trop grand rend le témoin AVEUGLE",
      lu_aveugle["ce_que_le_saut_coute"] < lu_juste["ce_que_le_saut_coute"],
      f"{lu_aveugle.get('ce_que_le_saut_coute')} contre {lu_juste['ce_que_le_saut_coute']}")

    # ⚠ LA PENTE EST LA LIMITE GEOMETRIQUE DE LA TRANCHE : une surface qui derive plus lentement ne
    # sera jamais prise en faute par une fibre, quelle que soit la qualite du temoin.
    v("la pente est la montée par pas", abs(la_pente_du_ruban(18, 36) - 0.5) < 1e-9,
      str(la_pente_du_ruban(18, 36)))
    v("et un plafond nul ne rend aucune pente", la_pente_du_ruban(18, 0) == 0.0)

    # ⚠⚠ LE PLAFOND EST CELUI DE `186`, DERIVE EN MICROMETRES : il doit franchir un pas de feuille.
    v("le plafond franchit un pas entre deux feuilles", le_plafond(vx, pas) * vx > pas,
      f"{le_plafond(vx, pas) * vx} contre {pas}")

    # ⚠⚠ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(trav, reste, cout, nul, ou=3, ou_nul=0):
        return {"decidable": True, "segment": "x", "chunks_lus": 9, "refuses": {},
                "pas_en_traversant": float(trav), "pas_en_restant": float(reste),
                "pas_a_plat": float(reste) + 2.0, "cout_median_du_saut": float(cout),
                "cout_median_du_nul": float(nul), "chunks_ou_le_saut_coute": int(ou),
                "chunks_ou_le_nul_coute": int(ou_nul), "montee_mediane": 12,
                "plafond_du_ruban_median": 30, "pente_mediane": 0.4,
                "cout_median_de_la_derive": 4.0, "chunks": []}

    bon = {"cout_median_du_saut": 9.0, "cout_median_du_nul": 0.0,
           "decalages_ou_le_saut_coute": 6, "decalages_lisibles": 6,
           "le_saut_coute_a_tous_les_decalages": True}
    r1 = juger([_seg(20.0, 32.0, 12.0, 1.0)], bon, vx, pas)
    v("un étalon qui voit le saut rend le premier énoncé",
      r1["le_temoin_voit_un_saut_construit"])
    v("un coût positif dit que le saut coûte sur le rouleau",
      r1["le_saut_coute_sur_le_rouleau"], str(r1["ce_que_le_saut_coute"]))
    v("et il dépasse le nul", r1["le_saut_coute_plus_que_le_hasard"],
      f"{r1['ce_que_le_saut_coute']} contre {r1['ce_que_le_nul_rend']}")
    v("et le coût est publié en micromètres aussi",
      abs(r1["ce_que_le_saut_coute_um"] - 12.0 * vx) < 1e-9,
      str(r1["ce_que_le_saut_coute_um"]))
    # ⚠⚠⚠ DERIVER N'EST PAS SAUTER : un temoin dont le saut coute MOINS que la simple derive en
    # profondeur lit un mouvement et non une frontiere. L'enonce les separe.
    v("le saut coûte plus que la dérive quand c'est le cas",
      r1["le_saut_coute_plus_que_la_derive"],
      f"{r1['ce_que_le_saut_coute']} contre {r1['ce_que_la_derive_coute']}")
    r_derive = juger([_seg(20.0, 32.0, 2.0, 1.0)], bon, vx, pas)
    v("★★★★ et un saut qui coûte moins que la dérive ne la dépasse pas",
      not r_derive["le_saut_coute_plus_que_la_derive"],
      f"{r_derive['ce_que_le_saut_coute']} contre {r_derive['ce_que_la_derive_coute']}")
    v("et ce que la dérive coûte est publié en micromètres",
      abs(r1["ce_que_la_derive_coute_um"] - 4.0 * vx) < 1e-9,
      str(r1["ce_que_la_derive_coute_um"]))

    r2 = juger([_seg(32.0, 32.0, 0.0, 0.0)], bon, vx, pas)
    v("un coût nul retire le deuxième énoncé", not r2["le_saut_coute_sur_le_rouleau"])
    r3 = juger([_seg(20.0, 32.0, 12.0, 14.0)], bon, vx, pas)
    v("★★★★ un coût que le mélange égale ou dépasse retire le troisième",
      not r3["le_saut_coute_plus_que_le_hasard"],
      f"{r3['ce_que_le_saut_coute']} contre {r3['ce_que_le_nul_rend']}")
    r4 = juger([_seg(20.0, 32.0, 12.0, 1.0)],
               {**bon, "le_saut_coute_a_tous_les_decalages": False}, vx, pas)
    v("★ un étalon qui ne voit pas le saut retire le premier énoncé",
      not r4["le_temoin_voit_un_saut_construit"])
    vide = juger([{"decidable": False, "segment": "x"}], bon, vx, pas)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "un_ruban_qui_saute_perd_il_sa_fibre.py"
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
