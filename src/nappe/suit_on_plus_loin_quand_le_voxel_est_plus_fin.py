"""Suit-on plus loin quand le voxel est plus fin ? — la réponse de `R4-P34`, EN MICROMÈTRES.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `185` a mesuré pour la première fois le critère que le prix emploie —
« follow horizontal papyrus fibers... and not jumping between sheets » — et la réponse fut un demi-pas
: **84,0** µm suivis pour un pas entre deux feuilles de **173** µm. Le suiveur suit, le rouleau porte
des crêtes suivables : ce qui manque n'est ni l'instrument ni la matière, c'est la LONGUEUR. La porte
`R4-P34` demande donc si une matière mieux résolue la rend suivable plus loin, et les volumes à
**1,129** µm existent.

⚠⚠⚠ ET LA COMPARAISON NE PEUT SE FAIRE QU'EN MICROMÈTRES. Un voxel deux fois plus fin double
mécaniquement le nombre de pas sans rien ajouter : publier des pas ferait lire un changement d'unité
comme un gain. Tout ce que cette tranche publie du rouleau est en micromètres, et le nombre de pas
n'apparaît qu'à côté, comme l'unité brute de l'instrument.

⚠⚠⚠ ET LA FENÊTRE DOIT ÊTRE LA MÊME. Un chunk fait 128 voxels de côté aux deux résolutions, donc
**307,2** µm à 2,4 µm et **144,5** µm à 1,129 — MOINS qu'un pas entre deux feuilles. Lire un chunk fin
brut bornerait la longueur par la fenêtre et non par la matière, et le verdict serait le nôtre. La
fenêtre fine est donc une MOSAÏQUE de chunks voisins, rognée au côté qui rend le MÊME champ physique
que la fenêtre grossière. Les deux résolutions lisent alors le même carré de papyrus, au même nombre
de départs, donc à la même densité physique de départs.

⚠⚠ ET LES SEGMENTS DOIVENT ÊTRE LES MÊMES. L'inventaire ne recense pas les deux résolutions pour tous
les segments ; prendre les premiers de chaque liste ferait comparer deux morceaux de rouleau
différents. On ne garde que les segments qui portent LES DEUX.

⭐⭐⭐⭐ LE CONTRÔLE QUI DÉCIDE EST UNE INVARIANCE, ET IL EST CONSTRUIT. Sur des crêtes dont la
LONGUEUR PHYSIQUE est posée, un suiveur qui mesure la MATIÈRE doit rendre la même longueur en
micromètres aux deux résolutions ; un suiveur qui mesure sa propre résolution rendrait le double.
Tant que cette invariance n'est pas constatée, aucun chiffre du rouleau n'est interprétable — c'est
le précédent de `181`, où rien n'a été publié pendant que le contrôle était rouge.

⭐ ET LA SECONDE LIMITE DE `185` EST LEVÉE ICI : sa marche est GLOUTONNE, elle prend le plus brillant
des trois voisins à chaque pas, donc elle ne cherche pas le meilleur chemin. `suivre_au_mieux` rend
l'OPTIMUM exact sur le même jeu de mouvements, par programmation dynamique, et sans aucune largeur à
choisir. ⚠⚠ Mais optimiser trouve toujours quelque chose : ce que l'exactitude achète se mesure comme
l'EXCÉDENT sur ce qu'elle achète sur la MÊME image mélangée.

⚠ Le suiveur glouton de `185` est IMPORTÉ et non réécrit : changer l'instrument et la résolution dans
la même tranche mélangerait les deux effets, et les nombres de `185` ne seraient plus comparables.

Usage :
    uv run python src/nappe/suit_on_plus_loin_quand_le_voxel_est_plus_fin.py --verifier
    uv run python src/nappe/suit_on_plus_loin_quand_le_voxel_est_plus_fin.py \\
        --json docs/mesures/suit_on_plus_loin_quand_le_voxel_est_plus_fin.json
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from fiber_orientation import orientation_profile  # noqa: E402
from jusquou_suit_on_une_fibre import (COUCHES_PAR_CHUNK, DEPARTS_PAR_COUCHE,  # noqa: E402
                                       les_departs, suivre)
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PLANCHER_DE_COHERENCE, VOLUMES, les_chunks)
from langle_publie_est_il_celui_des_fibres import direction_des_fibres_deg  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20260926
SEGMENTS = 3
ANGLES_DE_LETALON = (0.0, 30.0, 90.0)
# ⚠ LA PÉRIODE DE L'ÉTALON N'EST PAS CHOISIE ICI : c'est celle de l'étalon de `185`, douze voxels à
# 2,4 µm, reprise en micromètres pour que les deux résolutions décrivent la MÊME matière construite.
PERIODE_DE_LETALON_UM = 12.0 * 2.4


def les_deux_resolutions(chemin: Path = VOLUMES) -> list[tuple[str, float]]:
    """Les deux résolutions les plus fines que l'inventaire recense, la plus fine d'abord.

    ⚠⚠ ELLES SONT LUES DANS LE FICHIER, PAS TAPÉES. Écrire « 1.129um- » à la main ferait d'un fait
    sur le dépôt une constante de ce fichier, et le jour où l'inventaire change la mesure porterait
    sur autre chose que ce qu'elle annonce.
    """
    if not chemin.is_file():
        return []
    vues: dict[float, str] = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        champs = ligne.split("\t")
        if len(champs) < 2:
            continue
        for m in re.finditer(r"/([0-9]+(?:\.[0-9]+)?)um-", champs[1]):
            vues.setdefault(float(m.group(1)), f"{m.group(1)}um-")
    return [(vues[v], v) for v in sorted(vues)[:2]]


def les_segments_communs(chemin: Path = VOLUMES, marques: tuple[str, ...] = (),
                         combien: int = SEGMENTS) -> list[dict]:
    """Les premiers segments qui portent TOUTES les marques demandées, dans l'ordre du fichier.

    ⚠⚠ SANS CETTE INTERSECTION LA COMPARAISON PORTERAIT SUR DEUX MORCEAUX DE ROULEAU DIFFÉRENTS :
    l'inventaire ne recense la résolution fine que pour une partie des segments, donc prendre les
    trois premiers de chaque liste ferait lire des papyrus différents et attribuer leur écart à la
    résolution. ⚠ L'ordre reste celui du dépôt : choisir parmi eux ferait mesurer le choix.
    """
    if not chemin.is_file() or not marques:
        return []
    par_segment: dict[str, dict[str, str]] = {}
    ordre: list[str] = []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        champs = ligne.split("\t")
        if len(champs) < 2:
            continue
        seg, cle = champs[0], champs[1]
        if seg not in par_segment:
            par_segment[seg] = {}
            ordre.append(seg)
        for marque in marques:
            if marque in cle:
                par_segment[seg].setdefault(marque, cle)
    out = []
    for seg in ordre:
        if all(m in par_segment[seg] for m in marques):
            out.append({"segment": seg, "cles": dict(par_segment[seg])})
        if len(out) >= int(combien):
            break
    return out


def le_champ_commun_um(voxel_grossier_um: float, cote_chunk: int) -> float:
    """Le côté physique que les deux résolutions liront : celui d'UN chunk à la résolution grossière.

    ⚠ C'est la fenêtre que `185` a lue, donc le nombre qu'on compare reste comparable au sien.
    """
    return float(cote_chunk) * float(voxel_grossier_um)


def le_cote_en_voxels(champ_um: float, voxel_um: float) -> int:
    return max(1, int(round(float(champ_um) / float(voxel_um))))


def les_chunks_par_cote(cote_voxels: int, cote_chunk: int) -> int:
    return max(1, -(-int(cote_voxels) // int(cote_chunk)))


def le_plafond(voxel_um: float, pas_um: float) -> int:
    """Le nombre de pas autorisé : de quoi FRANCHIR deux fois le pas entre deux feuilles.

    ⚠⚠ IL EST DÉRIVÉ EN MICROMÈTRES, donc il vaut deux fois plus de pas à résolution deux fois plus
    fine et couvre la MÊME distance. Un plafond en pas, identique aux deux résolutions, bornerait la
    fine à la moitié de la distance et rendrait l'absence de gain par construction.
    """
    return int(np.ceil(float(pas_um) / float(voxel_um))) * 2


def suivre_au_mieux(image: np.ndarray, departs, angle_deg: float, plafond: int,
                    plancher: float | None = None) -> list[int]:
    """L'OPTIMUM exact sur le même jeu de mouvements que la marche gloutonne de `185`.

    ⭐⭐⭐⭐ ET C'EST UN OPTIMUM, PAS UNE APPROXIMATION. Le chemin est décrit par son DÉCALAGE
    PERPENDICULAIRE `o` au fil des pas : à chaque pas on avance d'un voxel le long de la direction et
    le décalage change d'au plus un. La plus longue suite de pas au-dessus du plancher se calcule
    alors exactement, parce qu'une suite qui finit en `(t, o)` prolonge une suite qui finit en
    `(t-1, o-1..o+1)` : `R[t][o] = 1 + max(R[t-1][o-1..o+1])` si le voxel dépasse le plancher, zéro
    sinon. Aucune largeur de faisceau à choisir, aucun seuil.

    ⚠⚠ ET L'EXACTITUDE SE PAIE. Optimiser sur tous les chemins trouve une suite plus longue sur
    N'IMPORTE QUELLE image, y compris mélangée — c'est la leçon de `179` sur une liberté de choix. Ce
    que l'exactitude achète est donc l'EXCÉDENT sur ce qu'elle achète sur la même image mélangée, et
    l'appelant lit les deux.

    ⚠ Le plancher est celui de `185` : la MÉDIANE de l'image, donc il vient de la matière lue.
    ⚠ Un décalage qui sort de l'image casse la suite au lieu de l'arrêter : on ne suit pas une fibre
    hors de l'image, mais un chemin qui y revient reste un chemin.
    """
    h, w = image.shape
    if plancher is None:
        plancher = float(np.median(image))
    th = np.radians(float(angle_deg))
    uy, ux = float(np.sin(th)), float(np.cos(th))
    py, px = ux, -uy
    # ⚠ LA BANDE EST DÉRIVÉE : un décalage change d'au plus un par pas, donc il est borné par le
    # nombre de pas ; et un décalage plus grand que l'image ne décrit aucun voxel lisible.
    demi = int(min(int(plafond), max(h, w)))
    o = np.arange(-demi, demi + 1, dtype=np.float64)
    n = len(departs)
    if n == 0 or int(plafond) <= 0:
        return []
    dy = np.array([float(d[0]) for d in departs], dtype=np.float64)[:, None]
    dx = np.array([float(d[1]) for d in departs], dtype=np.float64)[:, None]
    R = np.full((n, len(o)), -1, dtype=np.int32)
    R[:, demi] = 0
    meilleure = np.zeros(n, dtype=np.int32)
    for t in range(1, int(plafond) + 1):
        gauche = np.full_like(R, -1)
        gauche[:, :-1] = R[:, 1:]
        droite = np.full_like(R, -1)
        droite[:, 1:] = R[:, :-1]
        avant = np.maximum(np.maximum(gauche, R), droite)
        yy = np.rint(dy + t * uy + o[None, :] * py).astype(np.int64)
        xx = np.rint(dx + t * ux + o[None, :] * px).astype(np.int64)
        dedans = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w)
        val = image[np.clip(yy, 0, h - 1), np.clip(xx, 0, w - 1)]
        vivant = dedans & (val > float(plancher))
        R = np.where(avant < 0, -1, np.where(vivant, np.maximum(avant, 0) + 1, 0)).astype(np.int32)
        meilleure = np.maximum(meilleure, R.max(axis=1))
    return [int(v) for v in meilleure]


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def _lecture(pas: list[int], voxel_um: float, pas_um: float) -> dict:
    """Une lecture, PUBLIÉE EN MICROMÈTRES — le nombre de pas ne vaut que dans son unité."""
    if not pas:
        return {"departs": 0}
    ums = [p * float(voxel_um) for p in pas]
    franchissent = sum(1 for u in ums if u >= float(pas_um))
    return {"departs": len(pas), "pas_median": _med(pas),
            "um_median": round(float(statistics.median(ums)), 3),
            "um_maximal": round(float(max(ums)), 3),
            "part_qui_franchit_une_feuille": round(franchissent / len(pas), 4)}


def une_couche(image: np.ndarray, angle_des_fibres_deg: float, combien: int, plafond: int,
               voxel_um: float, pas_um: float, graine: int = GRAINE) -> dict:
    """Les trois lectures de `185` — le long, en travers, mélangée — par les DEUX suiveurs.

    ⚠⚠ LES MÊMES DÉPARTS SERVENT AUX SIX LECTURES : c'est ce qui fait que l'écart entre deux d'entre
    elles vient de la direction, de la matière ou de la règle, jamais d'un tirage.
    """
    departs = les_departs(image, combien)
    r = np.random.default_rng(int(graine))
    melangee = image.flatten()[r.permutation(image.size)].reshape(image.shape)
    out: dict = {}
    for nom, img, ang in (("le_long", image, angle_des_fibres_deg),
                          ("en_travers", image, angle_des_fibres_deg + 90.0),
                          ("melangee", melangee, angle_des_fibres_deg)):
        glouton = [int(suivre(img, d, ang, plafond)["pas"]) for d in departs]
        au_mieux = suivre_au_mieux(img, departs, ang, plafond)
        out[nom] = {"glouton": _lecture(glouton, voxel_um, pas_um),
                    "au_mieux": _lecture(au_mieux, voxel_um, pas_um)}
    return out


def _agrege(lignes, quoi: str, regle: str, cle: str = "um_median"):
    vals = [x[quoi][regle].get(cle) for x in lignes if x[quoi][regle].get(cle) is not None]
    return _med(vals)


def le_cadre_de_la_mosaique(cy: int, cx: int, par_cote: int, gy: int, gx: int):
    """Le coin de la mosaïque : centrée sur le site, RAMENÉE dans la grille plutôt qu'amputée.

    ⚠⚠ UNE MOSAÏQUE AMPUTÉE N'EST PLUS LE MÊME CHAMP. Au bord de la grille un site n'a pas de voisin
    de ce côté ; rogner la fenêtre y ferait lire un carré de papyrus plus petit et une longueur bornée
    par le bord serait rapportée comme une longueur de la matière. On glisse donc la mosaïque à
    l'intérieur. ⚠ Une grille trop petite pour la mosaïque est REFUSÉE, jamais réduite.
    """
    if int(par_cote) > int(gy) or int(par_cote) > int(gx):
        return None
    demi = int(par_cote) // 2
    oy = min(max(int(cy) - demi, 0), int(gy) - int(par_cote))
    ox = min(max(int(cx) - demi, 0), int(gx) - int(par_cote))
    return int(oy), int(ox)


def rogner_au_centre(bloc: np.ndarray, cote: int) -> np.ndarray | None:
    """Le rognage central au côté voulu — un rognage décalé lirait un autre carré que le site visé."""
    c = int(cote)
    if c > bloc.shape[1] or c > bloc.shape[2]:
        return None
    y0 = (bloc.shape[1] - c) // 2
    x0 = (bloc.shape[2] - c) // 2
    return bloc[:, y0:y0 + c, x0:x0 + c]


def une_mosaique(url: str, meta: dict, cy: int, cx: int, par_cote: int, cote_voulu: int,
                 gy: int, gx: int, delai: float) -> tuple[np.ndarray | None, str]:
    """Le champ commun, assemblé de `par_cote`² chunks voisins puis rogné au côté voulu.

    ⚠⚠ LE CÔTÉ VIENT DU CHAMP PHYSIQUE, pas d'un arrondi commode : c'est ce qui fait que les deux
    résolutions lisent le même carré de papyrus.

    ⚠⚠⚠ ET CHAQUE CHUNK DE LA MOSAÏQUE DOIT PORTER DE LA MATIÈRE, parce que c'est EXACTEMENT la
    règle que la résolution grossière applique à son chunk unique. Sans elle la comparaison serait
    truquée dans un sens : une fenêtre fine faite de neuf chunks a neuf fois plus d'occasions d'en
    contenir un vide, un vide dessine une plage noire au milieu du champ, et une crête qui s'y
    termine rend une longueur courte — on lirait alors le DÉCOUPAGE du dépôt comme une propriété de
    la matière fine.
    """
    profond, hy, hx = meta["chunks"]
    cadre = le_cadre_de_la_mosaique(cy, cx, par_cote, gy, gx)
    if cadre is None:
        return None, "hors grille"
    oy, ox = cadre
    bloc = np.zeros((profond, par_cote * hy, par_cote * hx), dtype=np.dtype(meta["dtype"]))
    for i in range(par_cote):
        for j in range(par_cote):
            raw = get(f"{url}/{chunk_key(meta, 0, oy + i, ox + j)}", delai)
            if raw is None:
                return None, "absent"
            data = decode(raw, meta, profond * hy * hx)
            if data is None:
                return None, "illisible"
            morceau = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx)
            if int(morceau.max()) == 0:
                return None, "vide"
            bloc[:, i * hy:(i + 1) * hy, j * hx:(j + 1) * hx] = morceau
    rogne = rogner_au_centre(bloc, cote_voulu)
    if rogne is None:
        return None, "champ trop grand"
    return rogne, ""


def un_chunk(bloc: np.ndarray, angles, coherences, combien: int, plafond: int, voxel_um: float,
             pas_um: float, couches: int = COUCHES_PAR_CHUNK,
             plancher: float = PLANCHER_DE_COHERENCE, graine: int = GRAINE) -> dict:
    """Les couches les plus texturées du champ, lues par les deux suiveurs — la règle de `185`."""
    fortes = [k for k in range(len(coherences)) if float(coherences[k]) > float(plancher)]
    fortes = sorted(fortes, key=lambda k: -float(coherences[k]))[:int(couches)]
    lignes = []
    for k in sorted(fortes):
        # ⚠⚠⚠ L'ANGLE PUBLIÉ EST LA PERPENDICULAIRE AUX FIBRES (`172`) : suivre l'angle brut
        # inverserait exactement les deux lectures que cette tranche compare.
        ang = float(direction_des_fibres_deg(float(angles[k])))
        lignes.append({"couche": int(k), "coherence": round(float(coherences[k]), 4),
                       "angle_des_fibres_deg": round(ang, 3),
                       **une_couche(bloc[k], ang, combien, plafond, voxel_um, pas_um, graine)})
    return {"couches_lues": len(lignes), "lignes": lignes}


def un_segment(segment: str, cle: str, voxel_um: float, champ_um: float, combien: int,
               cote_chunk_attendu: int | None = None, cote: int = COTE_DU_TREILLIS,
               delai: float = DELAI, pas_um: float = 173.0, graine: int = GRAINE) -> dict:
    """Un segment à UNE résolution, sur le champ commun."""
    url = f"{BUCKET}/{cle}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": segment, "voxel_um": float(voxel_um),
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    cote_voulu = le_cote_en_voxels(champ_um, voxel_um)
    par_cote = les_chunks_par_cote(cote_voulu, hy)
    plafond = le_plafond(voxel_um, pas_um)
    lignes, refus = [], {}
    for cy, cx in les_chunks(gy, gx, cote):
        # ⚠ ON SONDE LE CHUNK CENTRAL D'ABORD : une mosaïque entière tirée sur un site mort
        # coûterait huit lectures pour rien, et le dépôt n'en rend qu'une sur trois.
        raw = get(f"{url}/{chunk_key(meta, 0, cy, cx)}", delai)
        if raw is None:
            refus["absent"] = refus.get("absent", 0) + 1
            continue
        bloc, pourquoi = une_mosaique(url, meta, cy, cx, par_cote, cote_voulu, gy, gx, delai)
        if bloc is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        if int(bloc.max()) == 0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        ang, coh = orientation_profile(bloc)
        if int((coh > PLANCHER_DE_COHERENCE).sum()) < profond // 4:
            refus["trop peu texturé"] = refus.get("trop peu texturé", 0) + 1
            continue
        lu = un_chunk(bloc.astype(np.float32), ang, coh, combien, plafond, voxel_um, pas_um,
                      COUCHES_PAR_CHUNK, PLANCHER_DE_COHERENCE, graine)
        if lu["couches_lues"]:
            # ⚠⚠ LA PART DE VIDE EST PUBLIÉE : une fenêtre trouée rend des longueurs courtes pour
            # une raison qui n'est pas la matière, et les deux résolutions doivent pouvoir être
            # comparées là-dessus aussi.
            lignes.append({"chunk": [int(cy), int(cx)],
                           "part_vide": round(float((bloc == 0).mean()), 4), **lu})
    toutes = [x for c in lignes for x in c["lignes"]]
    out = {"decidable": bool(toutes), "segment": segment, "voxel_um": float(voxel_um),
           "champ_um": round(float(champ_um), 3), "cote_en_voxels": int(cote_voulu),
           "chunks_par_cote": int(par_cote), "chunk_du_depot": [int(profond), int(hy), int(hx)],
           "plafond_de_pas": int(plafond), "chunks_lus": len(lignes), "refuses": refus,
           "couches_lues": len(toutes)}
    for quoi in ("le_long", "en_travers", "melangee"):
        for regle in ("glouton", "au_mieux"):
            out[f"{quoi}_{regle}_um"] = _agrege(toutes, quoi, regle)
    out["le_long_glouton_um_maximal"] = _agrege(toutes, "le_long", "glouton", "um_maximal")
    out["le_long_au_mieux_um_maximal"] = _agrege(toutes, "le_long", "au_mieux", "um_maximal")
    out["part_qui_franchit_glouton"] = _agrege(toutes, "le_long", "glouton",
                                               "part_qui_franchit_une_feuille")
    out["part_qui_franchit_au_mieux"] = _agrege(toutes, "le_long", "au_mieux",
                                                "part_qui_franchit_une_feuille")
    out["part_vide"] = _med([c["part_vide"] for c in lignes]) if lignes else None
    out["chunks"] = lignes
    if cote_chunk_attendu is not None and int(hy) != int(cote_chunk_attendu):
        out["chunk_inattendu"] = True
    return out


def les_longueurs_de_crete_um(pas_um: float) -> tuple[float, ...]:
    """L'échelle des longueurs construites : quart, moitié, et un pas entre deux feuilles.

    ⚠⚠ ELLE EST DÉRIVÉE DU PAS PUBLIÉ, parce que c'est la distance dont dépend le verdict : une
    échelle qui ne l'encadrerait pas ne dirait rien de « franchit-on une feuille ».
    """
    return (float(pas_um) / 4.0, float(pas_um) / 2.0, float(pas_um))


def sur_une_image_construite(voxel_um: float, champ_um: float, combien: int, pas_um: float,
                             periode_um: float = PERIODE_DE_LETALON_UM,
                             graine: int = GRAINE) -> dict:
    """Des crêtes dont la LONGUEUR PHYSIQUE est posée — la réponse est connue avant la mesure.

    ⭐⭐⭐⭐ C'EST L'INVARIANCE QUI DÉCIDE DE TOUT LE RESTE. Un suiveur qui mesure la matière rend la
    même longueur en micromètres aux deux résolutions ; un suiveur qui mesure sa propre résolution en
    rend le double à voxel deux fois plus fin. Sans ce contrôle, un gain sur le rouleau serait
    indiscernable d'un changement d'unité.

    ⚠⚠ ET LES CRÊTES DOIVENT S'INTERROMPRE. Des crêtes qui traversent l'image entière feraient
    saturer les deux résolutions sur le bord du champ, donc l'invariance serait vraie par
    construction — une vérification incapable d'échouer. Elles sont coupées tous les `longueur_um`,
    par une coupure large d'une PÉRIODE, donc visible aux deux résolutions.

    ⚠ La coupure vaut exactement la valeur de fond, que la médiane de l'image rejoint : la suite s'y
    casse sans qu'aucun seuil n'ait été posé.
    """
    cote = le_cote_en_voxels(champ_um, voxel_um)
    plafond = le_plafond(voxel_um, pas_um)
    yy, xx = np.mgrid[0:cote, 0:cote].astype(np.float64)
    yy_um, xx_um = yy * float(voxel_um), xx * float(voxel_um)
    barreaux = []
    for longueur_um in les_longueurs_de_crete_um(pas_um):
        motif = float(longueur_um) + float(periode_um)
        lignes = []
        for angle in ANGLES_DE_LETALON:
            th = np.radians(angle)
            s = -np.sin(th) * xx_um + np.cos(th) * yy_um
            t = np.cos(th) * xx_um + np.sin(th) * yy_um
            porte = (np.mod(t, motif) < float(longueur_um)).astype(np.float64)
            img = (100.0 + 40.0 * np.cos(2.0 * np.pi * s / float(periode_um)) * porte)
            lignes.append({"angle_des_cretes_deg": float(angle),
                           **une_couche(img.astype(np.float32), angle, combien, plafond,
                                        voxel_um, pas_um, graine)})
        barreaux.append({"longueur_construite_um": round(float(longueur_um), 3),
                         "lignes": lignes,
                         "le_long_glouton_um": _agrege(lignes, "le_long", "glouton"),
                         "le_long_au_mieux_um": _agrege(lignes, "le_long", "au_mieux"),
                         "en_travers_glouton_um": _agrege(lignes, "en_travers", "glouton"),
                         "melangee_glouton_um": _agrege(lignes, "melangee", "glouton"),
                         "melangee_au_mieux_um": _agrege(lignes, "melangee", "au_mieux")})
    return {"voxel_um": float(voxel_um), "champ_um": round(float(champ_um), 3),
            "cote_en_voxels": int(cote), "plafond_de_pas": int(plafond),
            "periode_um": round(float(periode_um), 3), "barreaux": barreaux}


def _croissante(vals) -> bool:
    lus = [v for v in vals if v is not None]
    return len(lus) == len(vals) and all(b > a for a, b in zip(lus, lus[1:]))


def linvariance(etalons: dict, pas_um: float) -> dict:
    """Le suiveur mesure-t-il la matière ou sa propre résolution ?

    ⚠⚠ LA TOLÉRANCE N'EST PAS CHOISIE, ELLE EST STRUCTURELLE : l'écart entre les deux résolutions
    doit être PLUS PETIT que l'écart entre deux barreaux consécutifs de l'échelle construite. Le
    suiveur distingue alors mieux deux longueurs qu'il ne distingue deux résolutions, et c'est
    exactement ce qu'on lui demande.
    """
    echelle = les_longueurs_de_crete_um(pas_um)
    marche = min(b - a for a, b in zip(echelle, echelle[1:]))
    voxels = sorted(etalons)
    if len(voxels) != 2:
        return {"decidable": False, "raison": "il faut deux résolutions"}
    fin, gros = voxels[0], voxels[1]
    ecarts, suit = [], True
    # ⚠⚠ L'ÉCART DE CHAQUE BARREAU EST PRODUIT ICI, PAS AILLEURS. Un document ou une figure qui
    # soustrairait lui-même deux valeurs publierait un nombre sans producteur, et deux soustractions
    # écrites à deux endroits sont deux occasions de ne pas s'accorder.
    par_barreau: dict[str, list] = {}
    for regle in ("glouton", "au_mieux"):
        a = [b[f"le_long_{regle}_um"] for b in etalons[fin]["barreaux"]]
        b_ = [b[f"le_long_{regle}_um"] for b in etalons[gros]["barreaux"]]
        if not _croissante(a) or not _croissante(b_):
            suit = False
        ligne = []
        for x, y in zip(a, b_):
            if x is None or y is None:
                suit = False
                ligne.append(None)
            else:
                ecarts.append(abs(float(x) - float(y)))
                ligne.append(round(abs(float(x) - float(y)), 3))
        par_barreau[regle] = ligne
    return {"decidable": True, "voxel_fin_um": float(fin), "voxel_grossier_um": float(gros),
            "echelle_construite_um": [round(float(v), 3) for v in echelle],
            "marche_de_lechelle_um": round(float(marche), 3),
            "ecarts_par_barreau_glouton_um": par_barreau.get("glouton", []),
            "ecarts_par_barreau_au_mieux_um": par_barreau.get("au_mieux", []),
            "ecart_maximal_entre_resolutions_um": (round(max(ecarts), 3) if ecarts else None),
            "la_longueur_construite_est_suivie": bool(suit),
            "le_suiveur_mesure_la_matiere": bool(
                suit and ecarts and max(ecarts) < float(marche))}


def juger(par_resolution: dict, etalons: dict, pas_um: float) -> dict:
    """Suit-on plus loin quand le voxel est plus fin — EN MICROMÈTRES ?"""
    inv = linvariance(etalons, pas_um)
    voxels = sorted(par_resolution)
    if len(voxels) != 2:
        return {"decidable": False, "raison": "il faut deux résolutions", "linvariance": inv}
    fin, gros = voxels[0], voxels[1]
    out: dict = {"linvariance": inv, "voxel_fin_um": float(fin), "voxel_grossier_um": float(gros),
                 "le_pas_entre_deux_feuilles_um": float(pas_um)}
    lisibles = 0
    for etiquette, vx in (("fin", fin), ("grossier", gros)):
        lus = [s for s in par_resolution[vx] if s.get("decidable")]
        lisibles += bool(lus)
        out[f"segments_{etiquette}"] = len(lus)
        out[f"chunks_{etiquette}"] = int(sum(s["chunks_lus"] for s in lus))
        for quoi in ("le_long", "en_travers", "melangee"):
            for regle in ("glouton", "au_mieux"):
                out[f"{quoi}_{regle}_um_{etiquette}"] = _med(
                    [s[f"{quoi}_{regle}_um"] for s in lus if s[f"{quoi}_{regle}_um"] is not None])
        for regle in ("glouton", "au_mieux"):
            out[f"part_qui_franchit_{regle}_{etiquette}"] = _med(
                [s[f"part_qui_franchit_{regle}"] for s in lus
                 if s[f"part_qui_franchit_{regle}"] is not None])
            out[f"le_long_{regle}_um_maximal_{etiquette}"] = _med(
                [s[f"le_long_{regle}_um_maximal"] for s in lus
                 if s[f"le_long_{regle}_um_maximal"] is not None])
        out[f"part_vide_{etiquette}"] = _med(
            [s.get("part_vide") for s in lus if s.get("part_vide") is not None])
    if lisibles != 2:
        out["decidable"] = False
        out["raison"] = "une des deux résolutions n'a rien rendu"
        return out
    out["decidable"] = True
    # ⚠⚠ TOUT CE QUI SUIT EST EN MICROMÈTRES. Un rapport de pas vaudrait le rapport des voxels sans
    # que rien de la matière n'ait changé.
    for regle in ("glouton", "au_mieux"):
        a = out[f"le_long_{regle}_um_fin"]
        b = out[f"le_long_{regle}_um_grossier"]
        out[f"le_gain_{regle}_um"] = (round(float(a) - float(b), 3)
                                      if a is not None and b is not None else None)
        out[f"le_gain_{regle}_fois"] = (round(float(a) / float(b), 4)
                                        if a and b else None)
        # ⚠ L'EXCÉDENT SUR LE MÉLANGE EST CE QUE LA RÈGLE ACHÈTE VRAIMENT : optimiser allonge la
        # suite sur n'importe quelle image, donc la longueur brute ne dit pas si c'est la matière.
        for etiquette in ("fin", "grossier"):
            x = out[f"le_long_{regle}_um_{etiquette}"]
            y = out[f"melangee_{regle}_um_{etiquette}"]
            out[f"lexcedent_sur_le_melange_{regle}_um_{etiquette}"] = (
                round(float(x) - float(y), 3) if x is not None and y is not None else None)
    ex_g = out["lexcedent_sur_le_melange_glouton_um_fin"]
    ex_m = out["lexcedent_sur_le_melange_au_mieux_um_fin"]
    out["ce_que_lexactitude_achete_um"] = (round(float(ex_m) - float(ex_g), 3)
                                           if ex_g is not None and ex_m is not None else None)
    # ⭐⭐⭐⭐ LA COMPARAISON QUI DÉCIDE EST APPARIÉE PAR SEGMENT. Deux médianes de résolutions
    # différentes mêlent l'écart entre résolutions et l'écart entre morceaux de rouleau, et les
    # segments ne rendent pas la même longueur. Apparier retire cette seconde variation, et le compte
    # des segments où la longueur croît dit ce qu'une médiane de trois nombres ne peut pas dire.
    lus_fin = {s["segment"]: s for s in par_resolution[fin] if s.get("decidable")}
    lus_gros = {s["segment"]: s for s in par_resolution[gros] if s.get("decidable")}
    apparies = []
    for nom in sorted(set(lus_fin) & set(lus_gros)):
        a, b = lus_fin[nom]["le_long_glouton_um"], lus_gros[nom]["le_long_glouton_um"]
        if a is None or b is None:
            continue
        apparies.append({"segment": nom, "um_fin": float(a), "um_grossier": float(b),
                         "gain_um": round(float(a) - float(b), 3),
                         "gain_fois": (round(float(a) / float(b), 4) if b else None)})
    out["les_segments_apparies"] = apparies
    out["segments_apparies"] = len(apparies)
    out["le_gain_apparie_um"] = _med([x["gain_um"] for x in apparies])
    out["segments_ou_la_longueur_croit"] = sum(1 for x in apparies if x["gain_um"] > 0.0)
    fois = [x["gain_fois"] for x in apparies if x["gain_fois"] is not None]
    out["le_meilleur_gain_apparie_fois"] = (round(max(fois), 4) if fois else None)
    out["le_voxel_est_plus_fin_fois"] = round(float(gros) / float(fin), 4)
    # ⚠⚠ CINQ ÉNONCÉS, ET LE PREMIER CONDITIONNE LES AUTRES. Si le suiveur ne mesure pas la
    # matière sur de la matière construite, aucun chiffre du rouleau n'est interprétable.
    mesure = bool(inv.get("le_suiveur_mesure_la_matiere"))
    gain = out["le_gain_apparie_um"]
    out["la_longueur_croit_avec_la_resolution"] = bool(
        mesure and gain is not None and float(gain) > 0.0)
    # ⚠⚠⚠ « SUIVRE LA RÉSOLUTION » EST L'ÉNONCÉ QUI RÉPOND À LA PORTE, et il est plus exigeant que
    # « croître » : si c'est la finesse du voxel qui bornait la longueur, alors le MEILLEUR segment
    # doit s'allonger d'autant que le voxel s'affine. Un gain plus petit que ce facteur dit que ce
    # qui borne est ailleurs.
    meilleur = out["le_meilleur_gain_apparie_fois"]
    out["la_longueur_suit_la_resolution"] = bool(
        mesure and meilleur is not None
        and float(meilleur) >= float(out["le_voxel_est_plus_fin_fois"]))
    out["la_longueur_est_bornee_par_la_matiere"] = bool(
        mesure and meilleur is not None and not out["la_longueur_suit_la_resolution"])
    # ⚠⚠ ET IL FAUT QUE L'INSTRUMENT LISE ENCORE DES CRÊTES SUR LA MATIÈRE FINE. Sans cet énoncé,
    # « la longueur n'a pas grandi » serait indiscernable de « le suiveur a échoué sur ce volume ».
    lg = out["le_long_glouton_um_fin"]
    tr = out["en_travers_glouton_um_fin"]
    me = out["melangee_glouton_um_fin"]
    out["le_rouleau_porte_des_cretes_suivables_au_voxel_fin"] = bool(
        lg is not None and tr is not None and me is not None
        and float(lg) > float(tr) and float(lg) > float(me))
    out["on_franchit_une_feuille_au_voxel_fin"] = bool(
        out["le_long_glouton_um_fin"] is not None
        and float(out["le_long_glouton_um_fin"]) >= float(pas_um))
    out["lexactitude_achete_quelque_chose"] = bool(
        out["ce_que_lexactitude_achete_um"] is not None
        and float(out["ce_que_lexactitude_achete_um"]) > 0.0)
    return out


def mesurer(segments_n: int = SEGMENTS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    pas_um = float(C.PAS_UM)
    res = les_deux_resolutions()
    if len(res) != 2:
        return {"message": "l'inventaire ne recense pas deux résolutions"}
    (marque_fine, vx_fin), (marque_grosse, vx_gros) = res[0], res[1]
    communs = les_segments_communs(marques=(marque_fine, marque_grosse), combien=segments_n)
    if not communs:
        return {"message": "aucun segment ne porte les deux résolutions"}
    champ_um = le_champ_commun_um(vx_gros, 128)
    par_resolution: dict[float, list] = {}
    for marque, vx in ((marque_fine, vx_fin), (marque_grosse, vx_gros)):
        par_resolution[vx] = [
            un_segment(s["segment"], s["cles"][marque], vx, champ_um, combien,
                       cote=cote, pas_um=pas_um) for s in communs]
    etalons = {vx: sur_une_image_construite(vx, champ_um, combien, pas_um)
               for vx in (vx_fin, vx_gros)}
    return {"resolutions": [{"marque": m, "voxel_um": v} for m, v in res],
            "segments": [s["segment"] for s in communs],
            "champ_commun_um": round(float(champ_um), 3),
            "departs_par_couche": int(combien), "couches_par_chunk": int(COUCHES_PAR_CHUNK),
            "cote_du_treillis": int(cote), "graine": int(GRAINE),
            "periode_de_letalon_um": round(float(PERIODE_DE_LETALON_UM), 3),
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "les_segments": {str(v): par_resolution[v] for v in par_resolution},
            "les_etalons": {str(v): etalons[v] for v in etalons},
            "le_verdict": juger(par_resolution, etalons, pas_um)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v = r["le_verdict"]
    inv = v["linvariance"]
    print("SUIT-ON PLUS LOIN QUAND LE VOXEL EST PLUS FIN ?")
    print(f"  champ commun {r['champ_commun_um']} µm · {r['departs_par_couche']} départs par couche "
          f"· treillis {r['cote_du_treillis']}×{r['cote_du_treillis']}")
    print(f"  segments : {', '.join(r['segments'])}")
    print()
    print("  L'INVARIANCE (crêtes construites, longueur posée)")
    print(f"     échelle construite {inv.get('echelle_construite_um')} µm · marche "
          f"{inv.get('marche_de_lechelle_um')} µm")
    print(f"     écart maximal entre les deux résolutions {inv.get('ecart_maximal_entre_resolutions_um')} µm")
    print(f"     la longueur construite est suivie        {inv.get('la_longueur_construite_est_suivie')}")
    print(f"     ★ le suiveur mesure la matière            {inv.get('le_suiveur_mesure_la_matiere')}")
    print()
    for cle in sorted(r["les_segments"]):
        print(f"  VOXEL {cle} µm")
        for s in r["les_segments"][cle]:
            if not s.get("decidable"):
                print(f"     {s['segment']} — {s.get('raison', 'rien de lisible')} "
                      f"{s.get('refuses', '')}")
                continue
            print(f"     {s['segment']} · {s['chunks_lus']} champs · {s['couches_lues']} couches · "
                  f"côté {s['cote_en_voxels']} vx ({s['chunks_par_cote']}×{s['chunks_par_cote']} "
                  f"chunks) · refusés {s['refuses']}")
            print(f"        le long {s['le_long_glouton_um']} µm · en travers "
                  f"{s['en_travers_glouton_um']} · mélangée {s['melangee_glouton_um']} "
                  f"· au mieux {s['le_long_au_mieux_um']}")
        print()
    print("  LES SEGMENTS APPARIÉS")
    for x in v.get("les_segments_apparies", []):
        print(f"     {x['segment']} · {x['um_grossier']} µm → {x['um_fin']} µm · "
              f"{x['gain_um']:+} µm ({x['gain_fois']} fois)")
    print()
    print("  ★ LE VERDICT — TOUT EN MICROMÈTRES")
    for cle in ("segments_fin", "segments_grossier", "chunks_fin", "chunks_grossier",
                "part_vide_fin", "part_vide_grossier",
                "le_long_glouton_um_grossier", "le_long_glouton_um_fin",
                "en_travers_glouton_um_fin", "melangee_glouton_um_fin",
                "segments_apparies", "segments_ou_la_longueur_croit",
                "le_gain_apparie_um", "le_meilleur_gain_apparie_fois",
                "le_voxel_est_plus_fin_fois",
                "lexcedent_sur_le_melange_glouton_um_grossier",
                "lexcedent_sur_le_melange_glouton_um_fin",
                "lexcedent_sur_le_melange_au_mieux_um_fin",
                "ce_que_lexactitude_achete_um",
                "le_long_glouton_um_maximal_fin", "part_qui_franchit_glouton_fin",
                "part_qui_franchit_glouton_grossier",
                "le_pas_entre_deux_feuilles_um",
                "le_rouleau_porte_des_cretes_suivables_au_voxel_fin",
                "la_longueur_croit_avec_la_resolution",
                "la_longueur_suit_la_resolution",
                "la_longueur_est_bornee_par_la_matiere",
                "on_franchit_une_feuille_au_voxel_fin",
                "lexactitude_achete_quelque_chose"):
        print(f"     {cle:<52} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    pas_um = float(C.PAS_UM)

    # ⚠⚠ LES DEUX RÉSOLUTIONS SONT LUES DANS L'INVENTAIRE : une marque tapée ferait d'un fait sur le
    # dépôt une constante de ce fichier.
    res = les_deux_resolutions()
    v("l'inventaire rend deux résolutions", len(res) == 2, str(res))
    if len(res) == 2:
        v("et la plus fine vient en premier", res[0][1] < res[1][1], str(res))
        v("et la grossière est celle de la campagne", abs(res[1][1] - float(C.VOXEL_FIN_UM)) < 1e-9,
          str(res[1]))

    # ⚠⚠ LES SEGMENTS SONT L'INTERSECTION : sans elle on comparerait deux morceaux de rouleau
    # différents et on attribuerait leur écart à la résolution.
    if len(res) == 2:
        communs = les_segments_communs(marques=(res[0][0], res[1][0]), combien=SEGMENTS)
        v("des segments portent les deux résolutions", len(communs) > 0, str(len(communs)))
        v("et chacun porte bien les deux clés",
          all(len(s["cles"]) == 2 for s in communs), str([len(s["cles"]) for s in communs]))
        seuls_fins = les_segments_communs(marques=(res[0][0],), combien=99)
        v("et ils sont MOINS nombreux que ceux de la seule résolution fine",
          len(les_segments_communs(marques=(res[0][0], res[1][0]), combien=99))
          <= len(seuls_fins), f"{len(seuls_fins)} portant la fine")

    # ⭐⭐⭐⭐ LA FENÊTRE FINE DOIT RENDRE LE MÊME CHAMP PHYSIQUE. Un chunk fin brut fait 144,5 µm de
    # côté, MOINS qu'un pas entre deux feuilles : le lire nu bornerait la longueur par la fenêtre.
    champ = le_champ_commun_um(2.4, 128)
    v("le champ commun est celui d'un chunk grossier", abs(champ - 307.2) < 1e-9, str(champ))
    v("un chunk fin seul ne couvre PAS un pas entre deux feuilles", 128 * 1.129 < pas_um,
      f"{128 * 1.129} µm contre {pas_um}")
    v("mais le champ commun le couvre", champ > pas_um, f"{champ} µm contre {pas_um}")
    cote_fin = le_cote_en_voxels(champ, 1.129)
    v("le côté fin rend le même champ à un voxel près",
      abs(cote_fin * 1.129 - champ) <= 1.129, f"{cote_fin} vx = {cote_fin * 1.129} µm")
    v("et il faut plus d'un chunk pour l'atteindre", les_chunks_par_cote(cote_fin, 128) > 1,
      str(les_chunks_par_cote(cote_fin, 128)))
    v("là où un seul suffit à la résolution grossière",
      les_chunks_par_cote(le_cote_en_voxels(champ, 2.4), 128) == 1)

    # ⚠⚠ LA MOSAÏQUE EST CENTRÉE SUR LE SITE ET RAMENÉE DANS LA GRILLE, jamais amputée : une fenêtre
    # rognée au bord ferait lire un carré de papyrus plus petit et rapporterait une longueur bornée
    # par le bord comme une longueur de la matière.
    v("la mosaïque est centrée sur le site", le_cadre_de_la_mosaique(10, 10, 3, 50, 50) == (9, 9),
      str(le_cadre_de_la_mosaique(10, 10, 3, 50, 50)))
    v("au bord bas elle est ramenée dedans", le_cadre_de_la_mosaique(0, 0, 3, 50, 50) == (0, 0),
      str(le_cadre_de_la_mosaique(0, 0, 3, 50, 50)))
    v("au bord haut aussi", le_cadre_de_la_mosaique(49, 49, 3, 50, 50) == (47, 47),
      str(le_cadre_de_la_mosaique(49, 49, 3, 50, 50)))
    v("et elle tient toujours entièrement dans la grille",
      all(le_cadre_de_la_mosaique(a, b, 3, 7, 7)[0] + 3 <= 7
          and le_cadre_de_la_mosaique(a, b, 3, 7, 7)[1] + 3 <= 7
          for a in range(7) for b in range(7)))
    v("une grille trop petite est refusée, pas réduite",
      le_cadre_de_la_mosaique(0, 0, 3, 2, 9) is None)

    # ⚠⚠⚠ ET LA MOSAÏQUE REFUSE UN CHUNK VIDE, exactement comme la résolution grossière refuse son
    # chunk unique. Une fenêtre fine faite de neuf chunks a neuf fois plus d'occasions d'en contenir
    # un vide, et une crête qui se termine sur la plage noire rendrait une longueur courte : on
    # lirait le DÉCOUPAGE du dépôt comme une propriété de la matière fine. ⚠ La règle est éprouvée
    # AU SITE D'APPEL — c'est la réparation de `185`, dont une sonde passait au vert parce qu'elle
    # n'exerçait que la fonction et jamais l'endroit qui s'en sert.
    faux_meta = {"chunks": [2, 4, 4], "dtype": "|u1"}
    mondial = globals()
    vrais = (mondial["get"], mondial["decode"], mondial["chunk_key"])
    plein = np.full(2 * 4 * 4, 7, dtype=np.uint8).tobytes()
    creux = np.zeros(2 * 4 * 4, dtype=np.uint8).tobytes()
    try:
        mondial["chunk_key"] = lambda m, z, a, b: f"{a}.{b}"
        mondial["get"] = lambda u, d: u.rsplit("/", 1)[-1].encode()
        mondial["decode"] = lambda raw, m, n: (creux if raw == b"1.1" else plein)
        bloc_v, pourquoi_v = une_mosaique("u", faux_meta, 1, 1, 3, 4, 9, 9, 1.0)
        mondial["decode"] = lambda raw, m, n: plein
        bloc_p, pourquoi_p = une_mosaique("u", faux_meta, 1, 1, 3, 4, 9, 9, 1.0)
    finally:
        mondial["get"], mondial["decode"], mondial["chunk_key"] = vrais
    v("une mosaïque dont un chunk est vide est REFUSÉE",
      bloc_v is None and pourquoi_v == "vide", f"{pourquoi_v}")
    v("et une mosaïque dont tous les chunks portent de la matière est acceptée",
      bloc_p is not None and bloc_p.shape == (2, 4, 4), str(None if bloc_p is None else bloc_p.shape))

    # ⚠⚠ ET LE ROGNAGE EST CENTRÉ : un rognage décalé lirait un autre carré que le site visé.
    marque = np.zeros((2, 9, 9), dtype=np.float32)
    marque[:, 4, 4] = 1.0
    rogne = rogner_au_centre(marque, 3)
    v("le rognage garde le centre au centre", rogne is not None and rogne[0, 1, 1] == 1.0,
      str(None if rogne is None else rogne[0]))
    v("et il rend le côté demandé", rogne is not None and rogne.shape[1:] == (3, 3),
      str(None if rogne is None else rogne.shape))
    v("un côté plus grand que le bloc est refusé", rogner_au_centre(marque, 11) is None)

    # ⚠⚠ LE PLAFOND EST DÉRIVÉ EN MICROMÈTRES : un plafond en pas identique aux deux résolutions
    # bornerait la fine à la moitié de la distance et rendrait l'absence de gain par construction.
    v("le plafond couvre la même distance aux deux résolutions",
      abs(le_plafond(1.129, pas_um) * 1.129 - le_plafond(2.4, pas_um) * 2.4) < 2.0 * 2.4,
      f"{le_plafond(1.129, pas_um) * 1.129} contre {le_plafond(2.4, pas_um) * 2.4} µm")
    v("et il franchit une feuille", le_plafond(2.4, pas_um) * 2.4 > pas_um)

    # ⭐⭐⭐⭐ LE SUIVEUR EXACT EST UN OPTIMUM, ET IL DOIT BATTRE LE GLOUTON LÀ OÙ LE GLOUTON EST
    # PIÉGÉ. L'image porte une crête longue qui commence MOINS brillante qu'une amorce voisine sans
    # suite : le glouton prend l'amorce et s'arrête, l'exact prend la crête. Un contrôle qui se
    # contenterait de « l'exact n'est jamais plus court » passerait avec un exact qui recopie le
    # glouton.
    piege = np.full((60, 60), 10.0, dtype=np.float32)
    piege[30, :] = 100.0                      # la vraie crête, droite et longue
    for k in range(1, 21):                    # un leurre plus brillant, qui S'ÉCARTE puis meurt
        piege[30 - k, k] = 200.0
    glouton = int(suivre(piege, (30, 0), 0.0, 50)["pas"])
    exact = suivre_au_mieux(piege, [(30, 0)], 0.0, 50)[0]
    v("le glouton se fait piéger par le leurre plus brillant", glouton <= 21, str(glouton))
    v("et l'exact suit la crête entière", exact > glouton + 20, f"{exact} contre {glouton}")

    # ⚠⚠ ET L'EXACT NE PEUT PAS DÉPASSER LE PLAFOND, sinon la longueur serait celle de l'image.
    v("l'exact ne dépasse pas le plafond", suivre_au_mieux(piege, [(30, 0)], 0.0, 7)[0] <= 7,
      str(suivre_au_mieux(piege, [(30, 0)], 0.0, 7)[0]))

    # ⚠⚠ LE PLANCHER VIENT DE L'IMAGE : une image uniforme n'a aucun voxel au-dessus de sa médiane,
    # donc l'exact y rend zéro — comme le glouton de `185`.
    plat = np.full((40, 40), 100.0, dtype=np.float32)
    v("une image uniforme ne rend aucune suite, même à l'optimum",
      suivre_au_mieux(plat, [(20, 20)], 0.0, 30)[0] == 0,
      str(suivre_au_mieux(plat, [(20, 20)], 0.0, 30)[0]))

    # ⚠ ET IL REND UNE VALEUR PAR DÉPART, dans le même ordre.
    lu = suivre_au_mieux(piege, [(30, 0), (5, 0), (30, 0)], 0.0, 50)
    v("l'exact rend une longueur par départ", len(lu) == 3, str(len(lu)))
    v("et deux fois le même départ rend deux fois la même longueur", lu[0] == lu[2], str(lu))
    v("tandis qu'un départ hors crête rend moins", lu[1] < lu[0], str(lu))

    # ⭐⭐⭐⭐ L'INVARIANCE, SUR DES CRÊTES DONT LA LONGUEUR PHYSIQUE EST POSÉE. C'est le contrôle qui
    # rend le rouleau interprétable, et il est CONSTRUIT pour pouvoir échouer : les crêtes sont
    # coupées, donc aucune des deux résolutions ne sature sur le bord du champ.
    e_gros = sur_une_image_construite(2.4, champ, DEPARTS_PAR_COUCHE, pas_um)
    e_fin = sur_une_image_construite(1.129, champ, DEPARTS_PAR_COUCHE, pas_um)
    inv = linvariance({2.4: e_gros, 1.129: e_fin}, pas_um)
    v("la longueur construite est suivie aux deux résolutions",
      inv["la_longueur_construite_est_suivie"],
      str([b["le_long_glouton_um"] for b in e_fin["barreaux"]]))
    v("★ et le suiveur mesure la matière, pas sa résolution",
      inv["le_suiveur_mesure_la_matiere"],
      f"écart {inv['ecart_maximal_entre_resolutions_um']} µm contre une marche de "
      f"{inv['marche_de_lechelle_um']}")
    # ⚠⚠ L'ÉCART DE CHAQUE BARREAU EST PRODUIT PAR LA MESURE : un document qui soustrairait
    # lui-même deux valeurs publiées écrirait un nombre sans producteur.
    v("il y a un écart publié par barreau de l'échelle",
      len(inv["ecarts_par_barreau_glouton_um"]) == len(inv["echelle_construite_um"]),
      str(inv["ecarts_par_barreau_glouton_um"]))
    v("et le plus grand d'entre eux ne dépasse pas l'écart maximal publié",
      max(inv["ecarts_par_barreau_glouton_um"])
      <= inv["ecart_maximal_entre_resolutions_um"] + 1e-9,
      f"{max(inv['ecarts_par_barreau_glouton_um'])} contre "
      f"{inv['ecart_maximal_entre_resolutions_um']}")
    v("et chacun est bien la distance entre les deux lectures du barreau",
      all(abs(float(e) - abs(float(a["le_long_glouton_um"]) - float(b["le_long_glouton_um"]))) < 1e-9
          for e, a, b in zip(inv["ecarts_par_barreau_glouton_um"], e_fin["barreaux"],
                             e_gros["barreaux"])),
      str(inv["ecarts_par_barreau_glouton_um"]))
    v("aucune des deux résolutions ne sature sur le champ",
      all(b["le_long_glouton_um"] < e_gros["champ_um"] for b in e_gros["barreaux"])
      and all(b["le_long_glouton_um"] < e_fin["champ_um"] for b in e_fin["barreaux"]),
      str([b["le_long_glouton_um"] for b in e_gros["barreaux"]]))
    v("et le mélange ne suit rien de la longueur construite",
      not _croissante([b["melangee_glouton_um"] for b in e_gros["barreaux"]])
      or max(b["melangee_glouton_um"] for b in e_gros["barreaux"])
      < min(b["le_long_glouton_um"] for b in e_gros["barreaux"]),
      str([b["melangee_glouton_um"] for b in e_gros["barreaux"]]))

    # ⚠⚠ ET L'INVARIANCE DOIT POUVOIR ÊTRE REFUSÉE : un étalon dont la longueur rendue DOUBLE avec la
    # résolution — exactement ce que rendrait un suiveur qui compterait des pas — doit la retirer.
    faux = {2.4: {"barreaux": [dict(b) for b in e_gros["barreaux"]]},
            1.129: {"barreaux": [dict(b) for b in e_gros["barreaux"]]}}
    for b in faux[1.129]["barreaux"]:
        b["le_long_glouton_um"] = float(b["le_long_glouton_um"]) * 2.0
        b["le_long_au_mieux_um"] = float(b["le_long_au_mieux_um"]) * 2.0
    v("un suiveur qui doublerait avec la résolution perd l'invariance",
      not linvariance(faux, pas_um)["le_suiveur_mesure_la_matiere"])

    # ⚠⚠ ET UNE ÉCHELLE QUI N'EST PAS SUIVIE LA RETIRE AUSSI, sinon « suivre la longueur construite »
    # serait un énoncé que rien n'exerce.
    plate = {2.4: {"barreaux": [dict(b) for b in e_gros["barreaux"]]},
             1.129: {"barreaux": [dict(b) for b in e_gros["barreaux"]]}}
    for d in plate.values():
        for b in d["barreaux"]:
            b["le_long_glouton_um"] = 50.0
            b["le_long_au_mieux_um"] = 50.0
    v("une échelle rendue plate perd l'invariance",
      not linvariance(plate, pas_um)["le_suiveur_mesure_la_matiere"])

    # ⚠⚠ LES ÉNONCÉS DU VERDICT TOMBENT CHACUN SUR L'ENTRÉE QUI LE VISE.
    def _seg(lg, tr, me, lgm, part, nom="x"):
        return {"decidable": True, "segment": nom, "chunks_lus": 9, "couches_lues": 54,
                "le_long_glouton_um": float(lg), "en_travers_glouton_um": float(tr),
                "melangee_glouton_um": float(me), "le_long_au_mieux_um": float(lgm),
                "en_travers_au_mieux_um": float(tr), "melangee_au_mieux_um": float(me),
                "part_qui_franchit_glouton": float(part), "part_qui_franchit_au_mieux": float(part),
                "le_long_glouton_um_maximal": float(lg) * 3.0, "part_vide": 0.0,
                "le_long_au_mieux_um_maximal": float(lgm) * 3.0}

    bons = {2.4: e_gros, 1.129: e_fin}
    r1 = juger({1.129: [_seg(120.0, 30.0, 20.0, 150.0, 0.2)],
                2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("un gain apparié positif dit que la longueur croît avec la résolution",
      r1["la_longueur_croit_avec_la_resolution"], str(r1["le_gain_apparie_um"]))
    v("et le gain est publié en micromètres", abs(r1["le_gain_apparie_um"] - 36.0) < 1e-9,
      str(r1["le_gain_apparie_um"]))
    # ⚠⚠⚠ CROÎTRE N'EST PAS SUIVRE LA RÉSOLUTION, et c'est l'énoncé qui répond à la porte : un gain
    # de 1,43 fois pendant que le voxel devient 2,13 fois plus fin dit que ce qui borne est ailleurs.
    v("mais un gain plus petit que la finesse du voxel ne suit PAS la résolution",
      not r1["la_longueur_suit_la_resolution"],
      f"{r1['le_meilleur_gain_apparie_fois']} contre {r1['le_voxel_est_plus_fin_fois']}")
    v("donc la longueur reste bornée par la matière", r1["la_longueur_est_bornee_par_la_matiere"])
    v("et elle ne franchit pas encore une feuille",
      not r1["on_franchit_une_feuille_au_voxel_fin"], str(r1["le_long_glouton_um_fin"]))
    r2 = juger({1.129: [_seg(200.0, 30.0, 20.0, 220.0, 0.6)],
                2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("un gain au moins égal à la finesse du voxel SUIT la résolution",
      r2["la_longueur_suit_la_resolution"],
      f"{r2['le_meilleur_gain_apparie_fois']} contre {r2['le_voxel_est_plus_fin_fois']}")
    v("et les deux énoncés ne sont alors pas rendus ensemble",
      not r2["la_longueur_est_bornee_par_la_matiere"])
    v("une longueur qui dépasse le pas franchit une feuille",
      r2["on_franchit_une_feuille_au_voxel_fin"], str(r2["le_long_glouton_um_fin"]))
    r3 = juger({1.129: [_seg(70.0, 30.0, 20.0, 100.0, 0.1)],
                2.4: [_seg(89.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("une longueur qui recule ne croît pas",
      not r3["la_longueur_croit_avec_la_resolution"], str(r3["le_gain_apparie_um"]))
    v("et elle est bornée par la matière", r3["la_longueur_est_bornee_par_la_matiere"])

    # ⭐⭐⭐⭐ L'APPARIEMENT EST PAR SEGMENT : deux médianes de résolutions différentes mêleraient
    # l'écart entre résolutions et l'écart entre morceaux de rouleau. Ici un segment monte et l'autre
    # descend, et le COMPTE le dit là où une médiane ne le pourrait pas.
    r4 = juger({1.129: [_seg(60.0, 30.0, 20.0, 100.0, 0.1, "a"),
                        _seg(120.0, 30.0, 20.0, 100.0, 0.1, "b")],
                2.4: [_seg(90.0, 30.0, 20.0, 100.0, 0.1, "a"),
                      _seg(90.0, 30.0, 20.0, 100.0, 0.1, "b")]}, bons, pas_um)
    v("l'appariement rend une ligne par segment commun", r4["segments_apparies"] == 2,
      str(r4["segments_apparies"]))
    v("et il compte les segments où la longueur croît",
      r4["segments_ou_la_longueur_croit"] == 1, str(r4["segments_ou_la_longueur_croit"]))
    v("et le meilleur gain est celui du meilleur segment, pas celui des médianes",
      abs(r4["le_meilleur_gain_apparie_fois"] - round(120.0 / 90.0, 4)) < 1e-9,
      str(r4["le_meilleur_gain_apparie_fois"]))
    v("un segment que l'autre résolution n'a pas lu n'est pas apparié",
      juger({1.129: [_seg(60.0, 30.0, 20.0, 100.0, 0.1, "a")],
             2.4: [_seg(90.0, 30.0, 20.0, 100.0, 0.1, "b")]},
            bons, pas_um)["segments_apparies"] == 0)

    # ⚠⚠ ET L'INSTRUMENT DOIT LIRE ENCORE DES CRÊTES SUR LA MATIÈRE FINE : sans cet énoncé, « la
    # longueur n'a pas grandi » serait indiscernable de « le suiveur a échoué sur ce volume ».
    v("le rouleau porte des crêtes suivables au voxel fin quand il dépasse ses deux contrôles",
      r1["le_rouleau_porte_des_cretes_suivables_au_voxel_fin"])
    r5 = juger({1.129: [_seg(25.0, 30.0, 20.0, 100.0, 0.1)],
                2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("et il ne les porte plus quand le travers le dépasse",
      not r5["le_rouleau_porte_des_cretes_suivables_au_voxel_fin"])
    r6 = juger({1.129: [_seg(25.0, 20.0, 30.0, 100.0, 0.1)],
                2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("ni quand le mélange le dépasse",
      not r6["le_rouleau_porte_des_cretes_suivables_au_voxel_fin"])

    # ⚠⚠⚠ ET LE VERDICT SE TAIT QUAND L'INVARIANCE EST ROUGE : un gain mesuré par un suiveur qui
    # compte sa propre résolution n'est pas un gain, et le précédent de `181` interdit de publier
    # pendant qu'un contrôle est rouge.
    r7 = juger({1.129: [_seg(120.0, 30.0, 20.0, 150.0, 0.2)],
                2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, {2.4: faux[2.4], 1.129: faux[1.129]},
               pas_um)
    v("★ invariance rouge, aucun des deux énoncés de résolution n'est rendu",
      not r7["la_longueur_croit_avec_la_resolution"]
      and not r7["la_longueur_est_bornee_par_la_matiere"],
      str(r7["linvariance"]["le_suiveur_mesure_la_matiere"]))
    v("mais le gain reste publié, avec son contrôle rouge à côté",
      r7["le_gain_apparie_um"] == r1["le_gain_apparie_um"], str(r7["le_gain_apparie_um"]))

    # ⚠⚠ CE QUE L'EXACTITUDE ACHÈTE EST UN EXCÉDENT SUR LE MÉLANGE, pas une longueur brute : une
    # règle qui allonge autant la matière que le mélange n'a rien acheté.
    r8 = juger({1.129: [_seg(120.0, 30.0, 20.0, 150.0, 0.2)],
                2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("l'exactitude achète quand son excédent dépasse celui du glouton",
      r8["lexactitude_achete_quelque_chose"], str(r8["ce_que_lexactitude_achete_um"]))
    gonfle = _seg(120.0, 30.0, 20.0, 150.0, 0.2)
    gonfle["melangee_au_mieux_um"] = 50.0
    r9 = juger({1.129: [gonfle], 2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("une règle qui allonge aussi le mélange n'achète rien",
      not r9["lexactitude_achete_quelque_chose"], str(r9["ce_que_lexactitude_achete_um"]))

    vide = juger({1.129: [{"decidable": False, "segment": "x"}],
                  2.4: [_seg(84.0, 30.0, 20.0, 100.0, 0.1)]}, bons, pas_um)
    v("une résolution sans rien de lisible rend un verdict indécidable", not vide["decidable"])

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ÉCHECS, PAS UN LITTÉRAL. Un `return 0` écrit après le verdict
    # jette ce que la batterie vient de compter, et une batterie dont la sortie ne peut pas valoir
    # autre chose que zéro est une vérification incapable d'échouer.
    nom = "suit_on_plus_loin_quand_le_voxel_est_plus_fin.py"
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
