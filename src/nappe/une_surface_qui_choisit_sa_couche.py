"""Une surface qui choisit sa couche reste-t-elle sur sa feuille ? — et ce que le choix coûte.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P38` QUI LE NOMME. `189` rend la première borne sur le PAS
d'un déroulage : ce que l'ordre en profondeur du rouleau porte est la CONTIGUÏTÉ — un chemin porte
**4,5625** fois plus loin qu'un saut direct — donc une surface qui se pose en profondeur doit y
avancer par pas contigus. La question du graal devient alors concrète : une surface posée pas à pas,
qui à chaque pas choisit la couche voisine où la lecture de la fibre se transfère le MIEUX,
dérive-t-elle vers la feuille ou s'en écarte-t-elle ?

⭐⭐⭐⭐ ET CE QUI SE MESURE N'EST PAS LA LONGUEUR, C'EST LA PROFONDEUR OÙ LA MARCHE ATTERRIT. `186` a
établi qu'optimiser trouve de la longueur sur N'IMPORTE QUELLE image — son optimum exact suit
**127,2** µm de bruit pur. Une marche qui choisit le plus brillant de ses voisines suivra donc plus
loin qu'une marche à plat, et ce gain ne prouve rien. Ce qui prouve quelque chose est l'endroit où
elle se trouve à la fin : une marche tenue par la matière reste dans sa feuille, une marche qui
achète sa longueur va où la brillance l'appelle.

⚠⚠⚠ ET LE PIÈGE EST CELUI DE `184`, ÉCRIT D'AVANCE PAR LA PORTE : une marche qui CHOISIT sa couche
se donne une liberté, et cette liberté doit être payée. Elle l'est ici par une marche qui choisit AU
HASARD parmi les MÊMES voisines, avec la MÊME poursuite latérale et le MÊME nombre de pas — donc un
déplacement en profondeur identique pas pour pas, et le critère pour seule différence. Sans ce nul,
« la marche reste » ne serait qu'un énoncé sur le pas qu'on lui a donné.

⚠⚠⚠ ET LE PAS EST FORCÉ : la couche change d'EXACTEMENT une couche à chaque pas latéral, jamais
zéro. Autoriser l'immobilité confondrait deux choses — « la marche est tenue » et « la marche ne
bouge pas » — parce que le glouton choisirait de rester et le hasard bougerait deux fois sur trois,
donc leurs excursions différeraient par la mobilité et non par le critère. Forcée, la marche et son
nul parcourent exactement la même longueur en profondeur.

⚠⚠⚠ ET LA VALEUR COMPARÉE EST CELLE AU-DESSUS DU PLANCHER DE SA PROPRE COUCHE, C'EST LE DÉFAUT QUE
`187` A PAYÉ. Une matière empilée porte un PROFIL DE DENSITÉ en profondeur, d'amplitude double de
celle des fibres : comparer les brillances brutes ferait choisir à la marche la couche la plus DENSE
et non celle où la fibre continue, donc l'instrument lirait la densité. La règle brute est portée
comme CONTRÔLE NOMMÉ et l'écart est mesuré.

⚠⚠ ET LES ÉGALITÉS SE TRANCHENT AU HASARD. Un départage déterministe est une préférence cachée pour
un sens de la profondeur : sur une matière dont les couches se ressemblent, `argmax` prendrait
toujours la première candidate et toute marche descendrait tout droit — la mesure lirait le départage
et non la matière.

⚠ Les deux pièges de `187` tiennent : le plafond se lit dans la MATIÈRE, le plancher dans CHAQUE
COUCHE. Et l'angle reste celui de la couche de DÉPART : c'est ce qu'un pipeline connaît, et le relire
à chaque changement de couche serait une seconde liberté non payée.

Usage :
    uv run python src/nappe/une_surface_qui_choisit_sa_couche.py --verifier
    uv run python src/nappe/une_surface_qui_choisit_sa_couche.py \\
        --json docs/mesures/une_surface_qui_choisit_sa_couche.json
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

from de_quoi_une_frontiere_est_elle_faite import plusieurs_creux  # noqa: E402
from fiber_orientation import orientation_profile  # noqa: E402
from jusquou_suit_on_une_fibre import DEPARTS_PAR_COUCHE  # noqa: E402
from jusquou_une_surface_peut_elle_deriver import (les_departs_par_couche,  # noqa: E402
                                                   une_pile_qui_tourne)
from langle_publie_est_il_celui_des_fibres import direction_des_fibres_deg  # noqa: E402
from la_coherence_creuse_t_elle_a_la_frontiere import (CONTRASTE_DE_LA_FIXTURE,  # noqa: E402
                                                       PLIS_DE_LA_FIXTURE,
                                                       les_frontieres_de_la_fixture)
from la_coupe_cherchee_trouve_t_elle_la_frontiere import COUCHES_DE_LA_CAMPAGNE  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PERMUTATIONS, PLANCHER_DE_COHERENCE, SEGMENTS,
                                             les_chunks, les_volumes)
from quelle_fenetre_lit_une_bascule import bloc_de_la_fixture  # noqa: E402
from suit_on_plus_loin_quand_le_voxel_est_plus_fin import le_plafond  # noqa: E402
from un_ruban_qui_saute_perd_il_sa_fibre import (RECOUVREMENTS_DE_LA_FIXTURE_UM,  # noqa: E402
                                                 le_plafond_du_ruban)
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LEMPILEMENT_A_RENDU = MESURES / "lempilement_se_repete_t_il.json"
CE_QUE_LA_RECETTE_A_RENDU = MESURES / "la_recette_posee_sur_le_rouleau.json"
GRAINE = 20260930

# ⚠⚠⚠ LE PAS EST FORCÉ ET IL VAUT UNE COUCHE : c'est le plus contigu que l'échantillonnage permette,
# donc aucune échelle n'est choisie, et zéro est absent parce qu'une surface qui se pose AVANCE.
ECARTS_DU_PAS = (-1, 1)
# ⚠ Une seule direction, tournée si lentement qu'aucune frontière n'existe — le pendant NÉGATIF de
# l'étalon. Le tour total est un quart sur huit hauteurs de bloc, donc les couches diffèrent assez
# pour qu'aucune égalité ne domine et trop peu pour qu'une frontière se lise.
COUCHES_SANS_FRONTIERE = 8
# ⚠⚠⚠ LE NOMBRE DE REPLICATS EST DERIVE DE LA GARANTIE QU'IL MESURE : un nul de dix-neuf tirages
# garantit un taux de faux d'un sur vingt, donc il faut au moins deux fois vingt replicats pour que
# ce taux-la soit resolu mieux que lui-meme. Moins ne trancherait rien ; plus couterait sans rien
# ajouter.
REPLICATS_DU_TAUX = 2 * (PERMUTATIONS + 1)
FRONTIERES_DE_LETALON = (36, 72)


def la_borne_du_pas_publiee(chemin: Path = CE_QUE_LEMPILEMENT_A_RENDU) -> dict:
    """La portée du transfert que `189` a publiée — la borne sur le pas, relue et jamais retapée.

    ⭐ C'EST ELLE QUI AUTORISE CETTE MARCHE. `189` mesure que deux couches distantes de plus de
    **16** couches sont aussi étrangères que deux tirées au hasard ; un pas d'une couche est donc
    seize fois sous la borne, et la marche a le droit d'exister.
    """
    if not chemin.is_file():
        return {}
    d = json.loads(chemin.read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    return {"en_couches": v.get("la_portee_du_transfert_en_couches"),
            "en_um": v.get("la_portee_du_transfert_um")}


def les_bascules_publiees(chemin: Path = CE_QUE_LA_RECETTE_A_RENDU) -> dict:
    """Ce que `176` a publié de l'écart de direction — celui du rouleau et celui de la fixture.

    ⭐⭐⭐⭐ C'EST CE QUI REND L'ÉCHELLE DÉRIVÉE ET NON CHOISIE. `176` a mesuré que d'un côté à
    l'autre d'une coupe le rouleau change de direction de **6,862** degrés quand la fixture en
    change de **90** — un rapport de **0,076**. L'échelle va donc de l'un à l'autre, et son DERNIER
    barreau est la valeur du rouleau : c'est la distance dont la question dépend, et une échelle qui
    ne sait pas l'exprimer ne pourrait jamais y répondre (la leçon de `188`).
    """
    if not chemin.is_file():
        return {}
    d = json.loads(chemin.read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    return {"du_rouleau_deg": v.get("bascule_mediane_du_rouleau_deg"),
            "de_la_fixture_deg": v.get("bascule_mediane_de_la_fixture_deg"),
            "le_temoin_du_rouleau_deg": v.get("temoin_median_du_rouleau_deg")}


def lechelle_des_ecarts_de_direction(fixture_deg: float, rouleau_deg: float,
                                     temoin_deg: float) -> list[float]:
    """L'échelle des écarts de direction — DÉRIVÉE de bout en bout, et zéro est son dernier barreau.

    ⭐⭐⭐⭐ SES QUATRE BORNES SONT DES NOMBRES PUBLIÉS, JAMAIS DES CHOIX. Le haut est l'écart de la
    fixture (**90** degrés, `176`). L'écart du ROULEAU est un barreau, parce que c'est la distance
    dont la question dépend — un halvage qui s'arrêterait avant ferait une vérification qui ne peut
    pas RÉUSSIR, le défaut que `188` a payé. Le halvage descend jusque SOUS le témoin du rouleau,
    c'est-à-dire sous le bruit propre de l'estimateur de direction : un écart plus petit que son
    témoin est un écart qu'aucun estimateur ne voit.

    ⚠⚠⚠ ET ZÉRO EST LE DERNIER BARREAU, PARCE QUE SANS LUI L'ÉCHELLE NE PEUT RIEN DIRE. Une échelle
    dont tous les barreaux « tiennent » ressemble exactement à une échelle qui ne mesure rien. Zéro
    est la matière où il n'y a AUCUN changement de direction à lire, donc celle où le critère DOIT
    lâcher ; c'est ce barreau-là qui rend les autres lisibles.

    ⚠ Le halvage parce que ce qu'on cherche est un ORDRE DE GRANDEUR : à partir de quel écart le
    critère cesse de tenir. Une échelle linéaire dépenserait ses barreaux là où rien ne bouge.
    """
    out, a = [], float(fixture_deg)
    while a > float(temoin_deg):
        out.append(round(a, 4))
        a /= 2.0
    out.append(round(a, 4))
    out.append(round(float(rouleau_deg), 4))
    out.append(0.0)
    return sorted(set(out), reverse=True)


def une_pile_a_deux_directions(couches: int, frontieres, ecart_deg: float, cote: int = 48,
                              longueur_de_fibre_vox: float = 12.0) -> np.ndarray:
    """Une pile dont la direction des fibres BASCULE d'un écart POSÉ à chaque frontière.

    ⭐⭐⭐⭐ ELLE ISOLE LA SEULE VARIABLE QUI COMPTE ICI. La fixture de `179` porte un écart de
    quatre-vingt-dix degrés et rien ne permet de le changer : c'est sa construction. Cette pile-là
    pose l'écart, donc l'échelle mesure à quel changement de direction le critère cesse de tenir —
    et rien d'autre ne bouge d'un barreau à l'autre.

    ⚠ Les couches d'un même pli sont IDENTIQUES : c'est voulu. Le critère n'a alors rien à préférer
    à l'intérieur d'un pli — les égalités s'y tranchent au hasard — donc tout ce qu'il peut lire est
    la frontière, et c'est ce que l'échelle met à l'épreuve.
    """
    yy, xx = np.mgrid[0:int(cote), 0:int(cote)].astype(np.float64)
    seuils = sorted(int(f) for f in frontieres)
    out = []
    for k in range(int(couches)):
        a = np.radians(float(ecart_deg) * (sum(1 for f in seuils if k >= f) % 2))
        s_ = np.cos(a) * yy + np.sin(a) * xx
        out.append(100.0 + 40.0 * np.cos(2.0 * np.pi * s_ / float(longueur_de_fibre_vox)))
    return np.stack(out).astype(np.float32)


def les_plis_par_couche(couches: int, frontieres) -> np.ndarray:
    """À quel pli appartient chaque couche — l'index qui dit si une marche a CHANGÉ de feuille.

    ⚠ Une frontière POSÉE, jamais relue dans la mesure qu'on met à l'épreuve : c'est la seule chose
    qui rend l'étalon capable de contredire l'instrument.
    """
    out = np.zeros(int(couches), dtype=np.int64)
    for f in sorted(int(x) for x in frontieres):
        if 0 <= f < int(couches):
            out[f:] += 1
    return out


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def une_marche_qui_choisit(bloc: np.ndarray, departs, couche_de_depart, angle_deg,
                           plafond: int, choix: str = "glouton", ecarts=ECARTS_DU_PAS,
                           plancher: float | None = None, plis_par_couche=None,
                           brut: bool = False, graine: int = GRAINE) -> dict:
    """La marche de `185`, mais dont la COUCHE est choisie à chaque pas latéral.

    ⭐⭐⭐⭐ C'EST LE GESTE DU PIPELINE, ET C'EST LA PREMIÈRE FOIS QUE LA CHAÎNE L'ÉCRIT. `188`
    marchait un ruban dont la profondeur monte à un rythme IMPOSÉ ; ici la surface décide, à chaque
    pas, dans laquelle des couches voisines elle se pose. La poursuite latérale est celle de `185`,
    inchangée : un pas d'un voxel le long de la fibre, recentrage à ±1 voxel perpendiculaire.

    ⚠⚠⚠ `choix="glouton"` prend la couche où la valeur au-dessus du plancher est la plus forte ;
    `choix="hasard"` en prend une AU HASARD parmi les mêmes, avec la même poursuite latérale — c'est
    le nul qui price la liberté, et il parcourt exactement la même longueur en profondeur ;
    `choix="fixe"` ne change pas de couche et redonne le suiveur à plat de `185`.

    ⚠⚠ `brut=True` compare les brillances BRUTES : c'est la règle que `187` a réfutée, portée comme
    contrôle nommé pour que l'écart se mesure au lieu de s'affirmer.

    ⚠ L'excursion est le plus grand écart à la couche de départ atteint en route, et non l'écart
    final : une marche qui s'éloigne puis revient a bel et bien quitté sa place, et une marche qui
    meurt tôt n'a pas d'écart final du tout.
    """
    couches, h, w = bloc.shape
    planchers = (np.full(couches, float(plancher), dtype=float) if plancher is not None
                 else np.median(bloc.reshape(couches, -1), axis=1).astype(float))
    n = len(departs)
    if n == 0 or int(plafond) <= 0:
        return {"marches": 0, "choix": str(choix), "longueur_mediane": None,
                "excursion_mediane": None, "excursion_maximale": None,
                "pas_vivants_median": None, "franchissements": None, "part_qui_franchit": None}
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
    k = np.clip(np.rint(kd).astype(np.int64), 0, couches - 1)
    depart = k.copy()
    dk = np.asarray((0,) if choix == "fixe" else ecarts, dtype=np.int64)
    nd = len(dk)
    lateraux = np.array([-1.0, 0.0, 1.0])
    r = np.random.default_rng(int(graine))
    vivant = np.ones(n, dtype=bool)
    suite = np.zeros(n, dtype=np.int64)
    meilleure = np.zeros(n, dtype=np.int64)
    excursion = np.zeros(n, dtype=np.int64)
    vivants = np.zeros(n, dtype=np.int64)
    franchi = np.zeros(n, dtype=bool)
    plis = None if plis_par_couche is None else np.asarray(plis_par_couche, dtype=np.int64)
    for _ in range(1, int(plafond) + 1):
        ny, nx = y + uy, x + ux
        cy = np.rint(ny[None, :] + lateraux[:, None] * py[None, :]).astype(np.int64)
        cx = np.rint(nx[None, :] + lateraux[:, None] * px[None, :]).astype(np.int64)
        dedans = (cy >= 0) & (cy < h) & (cx >= 0) & (cx < w)
        kc = k[None, :] + dk[:, None]
        admis = (kc >= 0) & (kc < couches)
        kk = np.clip(kc, 0, couches - 1)
        valeur = bloc[kk[:, None, :], np.clip(cy, 0, h - 1)[None, :, :],
                      np.clip(cx, 0, w - 1)[None, :, :]].astype(float)
        ok = dedans[None, :, :] & admis[:, None, :]
        # ⚠⚠⚠ LA VALEUR COMPAREE EST CELLE AU-DESSUS DU PLANCHER DE SA PROPRE COUCHE (`187`).
        compare = np.where(ok, valeur if brut else valeur - planchers[kk][:, None, :], -np.inf)
        valeur = np.where(ok, valeur, -np.inf)
        if choix == "hasard":
            score = np.where(np.isfinite(compare).any(axis=1), r.random((nd, n)), -np.inf)
        else:
            score = compare.max(axis=1)
        # ⚠⚠ LES EGALITES SE TRANCHENT AU HASARD : un departage deterministe ferait descendre toute
        # marche tout droit sur une matiere dont les couches se ressemblent.
        i_d = np.lexsort((r.random((nd, n)), score), axis=0)[-1]
        vcomp = compare[i_d, :, idx]
        i_o = np.lexsort((r.random((n, 3)), vcomp), axis=1)[:, -1]
        v = valeur[i_d, i_o, idx]
        vivant = vivant & np.isfinite(v)
        vivants = vivants + vivant.astype(np.int64)
        k = np.where(vivant, np.clip(k + dk[i_d], 0, couches - 1), k)
        y = np.where(vivant, cy[i_o, idx].astype(float), y)
        x = np.where(vivant, cx[i_o, idx].astype(float), x)
        excursion = np.maximum(excursion, np.abs(k - depart))
        if plis is not None:
            franchi = franchi | (vivant & (plis[k] != plis[depart]))
        au_dessus = vivant & (v > planchers[k])
        suite = np.where(au_dessus, suite + 1, 0)
        meilleure = np.maximum(meilleure, suite)
    return {"marches": int(n), "choix": str(choix), "brut": bool(brut),
            "longueur_mediane": _med([int(m) for m in meilleure]),
            "excursion_mediane": _med([int(e) for e in excursion]),
            "excursion_maximale": int(excursion.max()),
            "pas_vivants_median": _med([int(p_) for p_ in vivants]),
            "franchissements": (int(franchi.sum()) if plis is not None else None),
            "part_qui_franchit": (round(float(franchi.mean()), 4) if plis is not None else None)}


def les_marches_du_bloc(bloc: np.ndarray, angles, coherences, combien: int, plafond: int,
                        plis_par_couche=None,
                        plancher_de_coherence: float = PLANCHER_DE_COHERENCE,
                        tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Les quatre marches sur le MÊME jeu de départs — celle qui choisit, son nul, la plate, la brute.

    ⚠⚠⚠ LE MÊME JEU DE DÉPARTS AUX QUATRE, ET C'EST CE QUI REND LA COMPARAISON APPARIÉE. Laisser
    chaque marche prendre ses propres départs ferait varier l'échantillon avec le critère, et l'écart
    mêlerait alors ce que le critère apporte et ce que les départs ont changé.

    ⚠⚠ ET LES PAS VIVANTS SONT PUBLIÉS : une marche qui franchit moins parce qu'elle MEURT plus tôt
    n'aurait pas tenu sa feuille, elle aurait manqué d'occasions de la quitter. Sans ce compte, les
    deux pannes seraient le même nombre.
    """
    dep = les_departs_par_couche(bloc, coherences, combien, plancher_de_coherence)
    if not dep:
        return {"decidable": False, "raison": "aucune couche texturée"}
    departs, kk, aa = [], [], []
    for k in sorted(dep):
        a = float(direction_des_fibres_deg(float(angles[k])))
        for p in dep[k]:
            departs.append(p)
            kk.append(float(k))
            aa.append(a)
    kk, aa = np.asarray(kk), np.asarray(aa)
    out = {}
    for nom, choix, brut in (("celle_qui_choisit", "glouton", False),
                             ("a_plat", "fixe", False),
                             ("la_regle_brute", "glouton", True)):
        out[nom] = une_marche_qui_choisit(bloc, departs, kk, aa, plafond, choix,
                                          plis_par_couche=plis_par_couche, brut=brut,
                                          graine=graine)
    # ⚠⚠⚠ LE NUL EST UNE FAMILLE DE DIX-NEUF TIRAGES, ET C'EST UNE REPARATION QU'UNE MESURE A
    # IMPOSEE. La premiere version comparait le glouton a UN seul tirage au hasard, donc « il
    # franchit moins » etait satisfait par un frisson : sur une matiere SANS aucun changement de
    # direction — celle ou il n'y a rien a lire — la regle passait au vert pour QUATRE
    # DIX-MILLIEMES d'ecart. C'est le defaut que la seconde reparation de `189` a paye, sous un
    # autre costume. Le glouton doit desormais franchir moins que les DIX-NEUF, ce qui est la
    # statistique de famille de `176` et de `179` et lui donne le meme taux de faux garanti : un
    # sur vingt.
    nuls = [une_marche_qui_choisit(bloc, departs, kk, aa, plafond, "hasard",
                                   plis_par_couche=plis_par_couche,
                                   graine=int(graine) + 1 + t) for t in range(int(tirages))]
    parts = [x["part_qui_franchit"] for x in nuls if x["part_qui_franchit"] is not None]
    out["le_hasard"] = {**nuls[0], "tirages": int(tirages),
                        "part_qui_franchit": _med(parts),
                        "la_plus_basse_des_parts": (round(min(parts), 4) if parts else None),
                        "pas_vivants_median": _med([x["pas_vivants_median"] for x in nuls
                                                    if x["pas_vivants_median"] is not None])}
    g, h_, p, b = (out["celle_qui_choisit"], out["le_hasard"], out["a_plat"],
                   out["la_regle_brute"])
    gp, hp, bp = g["part_qui_franchit"], h_["part_qui_franchit"], b["part_qui_franchit"]
    basse = h_["la_plus_basse_des_parts"]
    return {"decidable": True, "marches": g["marches"], "tirages_du_nul": int(tirages), **out,
            "ce_que_le_choix_retient": (round(float(hp) - float(gp), 4)
                                        if gp is not None and hp is not None else None),
            "la_plus_basse_des_parts_du_hasard": basse,
            # ⭐⭐⭐⭐ L'ENONCE DE LA TRANCHE, ET IL EST PAYE PAR UNE FAMILLE : une marche qui choisit
            # sa couche quitte sa feuille moins souvent que les DIX-NEUF marches qui la choisissent
            # au hasard parmi les memes voisines.
            "le_choix_retient_la_marche": bool(
                gp is not None and basse is not None and float(gp) < float(basse)
                and g["pas_vivants_median"] is not None
                and h_["pas_vivants_median"] is not None
                and float(g["pas_vivants_median"]) >= float(h_["pas_vivants_median"])),
            "ce_que_la_regle_brute_coute": (round(float(bp) - float(gp), 4)
                                            if gp is not None and bp is not None else None),
            "la_regle_brute_franchit_plus": bool(gp is not None and bp is not None
                                                 and float(bp) > float(gp)),
            # ⚠⚠ LA GARDE QUI SEPARE DEUX PANNES : une marche qui franchit moins parce qu'elle
            # MEURT plus tot n'a pas tenu sa feuille. Les deux comptes de pas vivants doivent se
            # tenir, et l'ecart est publie plutot qu'affirme.
            "pas_vivants_de_celle_qui_choisit": g["pas_vivants_median"],
            "pas_vivants_du_hasard": h_["pas_vivants_median"],
            "les_deux_marches_vivent_autant": bool(
                g["pas_vivants_median"] is not None and h_["pas_vivants_median"] is not None
                and float(g["pas_vivants_median"]) >= float(h_["pas_vivants_median"])),
            "ce_que_le_choix_coute_en_longueur": (
                round(float(g["longueur_mediane"]) - float(p["longueur_mediane"]), 3)
                if g["longueur_mediane"] is not None and p["longueur_mediane"] is not None
                else None)}


def sur_la_fixture(combien: int = DEPARTS_PAR_COUCHE, plis: int = PLIS_DE_LA_FIXTURE,
                   recouvrements=RECOUVREMENTS_DE_LA_FIXTURE_UM,
                   graine: int = GRAINE) -> dict:
    """Trois matières dont la réponse est CONNUE, et le contrôle peut échouer des deux côtés.

    ⭐⭐⭐⭐ LES DEUX PREMIÈRES PORTENT DE VRAIES FRONTIÈRES — des plis dont les fibres font
    quatre-vingt-dix degrés d'écart, aux couches que la fonction dérive du pas — et une marche qui
    suit la fibre DOIT les quitter moins souvent que le hasard. La troisième porte des frontières
    FICTIVES : une seule direction sur tout le bloc, et les mêmes couches déclarées frontières. Rien
    n'y sépare deux plis, donc le choix ne DOIT rien retenir. Un instrument qui « retiendrait » aussi
    sur celle-là lirait sa propre marche et non la matière.

    ⚠⚠ C'EST UN CONTRÔLE SUR LA FORME ET NON SUR LA CONSÉQUENCE : ce qui manque à la troisième
    matière est le CHANGEMENT DE DIRECTION, pas la frontière déclarée. Les deux ont exactement les
    mêmes couches-frontières, le même étiquetage des plis et le même nul.

    ⚠ La troisième tourne d'un quart de tour sur huit hauteurs de bloc : assez pour que ses couches
    diffèrent — sinon toute candidate serait à égalité et la marche lirait le départage — et trop peu
    pour qu'une frontière s'y lise.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    plafond = le_plafond(vx, pas)
    frontieres = les_frontieres_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, 0.0, int(plis), vx, pas)
    plis_par_couche = les_plis_par_couche(COUCHES_DE_LA_CAMPAGNE, frontieres)
    matieres = [(f"deux plis à 90°, recouvrement {rec} µm",
                 bloc_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, 0.0, CONTRASTE_DE_LA_FIXTURE,
                                    int(plis), vx, pas, transition_um=float(rec)),
                 "le choix retient") for rec in recouvrements]
    matieres.append(("une seule direction, frontières fictives",
                     une_pile_qui_tourne(COUCHES_DE_LA_CAMPAGNE,
                                         COUCHES_DE_LA_CAMPAGNE * COUCHES_SANS_FRONTIERE),
                     "le choix ne retient rien"))
    lignes = []
    for nom, bloc, attendu in matieres:
        ang, coh = orientation_profile(bloc)
        pl = le_plafond_du_ruban(bloc, ang, coh, combien, plafond, PLANCHER_DE_COHERENCE)
        if not pl:
            lignes.append({"matiere": nom, "attendu": attendu, "decidable": False,
                           "raison": "aucune couche texturée"})
            continue
        lu = les_marches_du_bloc(bloc, ang, coh, combien, pl, plis_par_couche,
                                 PLANCHER_DE_COHERENCE, graine=graine)
        lignes.append({"matiere": nom, "attendu": attendu, "plafond_du_ruban": int(pl),
                       "frontieres": [int(f) for f in frontieres], **lu})
    vraies = [x for x in lignes if x.get("attendu") == "le choix retient" and x.get("decidable")]
    fictives = [x for x in lignes
                if x.get("attendu") == "le choix ne retient rien" and x.get("decidable")]
    return {"frontieres": [int(f) for f in frontieres],
            "recouvrements_um": [float(r) for r in recouvrements], "lignes": lignes,
            "le_choix_retient_sur_de_vraies_frontieres": bool(
                vraies and all(x["le_choix_retient_la_marche"] for x in vraies)),
            "le_choix_ne_retient_rien_sur_des_frontieres_fictives": bool(
                fictives and not any(x["le_choix_retient_la_marche"] for x in fictives)),
            # ⚠⚠ LES DEUX ENSEMBLE : un instrument qui retiendrait partout, ou nulle part, passerait
            # la moitie du controle en ne discriminant rien.
            "letalon_separe_les_deux": bool(
                vraies and fictives and all(x["le_choix_retient_la_marche"] for x in vraies)
                and not any(x["le_choix_retient_la_marche"] for x in fictives)),
            "la_regle_brute_franchit_plus_sur_letalon": bool(
                vraies and all(x["la_regle_brute_franchit_plus"] for x in vraies))}


def sur_lechelle_des_directions(ecarts, rouleau_deg: float | None = None,
                                combien: int = DEPARTS_PAR_COUCHE,
                                frontieres=(36, 72), graine: int = GRAINE) -> dict:
    """De quel changement de direction le critère a-t-il BESOIN pour tenir une surface ?

    ⭐⭐⭐⭐ C'EST LA MESURE QUI EXPLIQUE, ET SON DERNIER BARREAU EST L'ÉCART DU ROULEAU. Si le
    critère tient à quatre-vingt-dix degrés et lâche en descendant, alors ce qu'il lit est le
    CHANGEMENT DE DIRECTION, et l'échelle dit à partir de quel écart il ne le lit plus. L'écart du
    rouleau étant un barreau, la réponse sur le rouleau et la réponse sur la matière construite se
    comparent au même endroit.

    ⚠⚠ Une seule chose varie d'un barreau à l'autre : l'écart. Même pile, mêmes frontières, mêmes
    départs, même nul — sinon l'ordre de la courbe mêlerait l'écart et ce que la matière a changé.

    ⚠ Les frontières sont celles de la fixture, à la couche près : ce qui se mesure est l'écart, pas
    où il tombe.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    plafond_max = le_plafond(float(C.VOXEL_FIN_UM), float(C.PAS_UM))
    plc = les_plis_par_couche(COUCHES_DE_LA_CAMPAGNE, frontieres)
    lignes = []
    for e in ecarts:
        bloc = une_pile_a_deux_directions(COUCHES_DE_LA_CAMPAGNE, frontieres, float(e))
        ang, coh = orientation_profile(bloc)
        pl = le_plafond_du_ruban(bloc, ang, coh, combien, plafond_max,
                                 PLANCHER_DE_COHERENCE)
        if not pl:
            lignes.append({"ecart_deg": float(e), "decidable": False,
                           "raison": "aucune couche texturée"})
            continue
        lu = les_marches_du_bloc(bloc, ang, coh, combien, pl, plc, PLANCHER_DE_COHERENCE,
                                 graine=graine)
        lignes.append({"ecart_deg": float(e), "plafond_du_ruban": int(pl),
                       "part_qui_franchit": lu["celle_qui_choisit"]["part_qui_franchit"],
                       "part_qui_franchit_au_hasard": lu["le_hasard"]["part_qui_franchit"],
                       "la_plus_basse_des_parts_du_hasard":
                           lu["la_plus_basse_des_parts_du_hasard"],
                       "ce_que_le_choix_retient": lu["ce_que_le_choix_retient"],
                       "le_choix_retient_la_marche": lu["le_choix_retient_la_marche"],
                       "les_deux_marches_vivent_autant": lu["les_deux_marches_vivent_autant"]})
    lisibles = [x for x in lignes if x.get("plafond_du_ruban")]
    tiennent = [x for x in lisibles if x["le_choix_retient_la_marche"]]
    lachent = [x for x in lisibles if not x["le_choix_retient_la_marche"]]
    return {"ecarts_deg": [float(e) for e in ecarts], "lignes": lignes,
            "le_plus_grand_ecart_tient": bool(lisibles and lisibles[0]["le_choix_retient_la_marche"]),
            "lecart_du_rouleau_est_un_barreau_deg": (
                float(rouleau_deg) if rouleau_deg is not None else None),
            "le_critere_tient_jusqua_deg": (min(float(x["ecart_deg"]) for x in tiennent)
                                            if tiennent else None),
            "le_critere_lache_a_partir_de_deg": (max(float(x["ecart_deg"]) for x in lachent)
                                                 if lachent else None),
            # ⭐⭐⭐⭐ L'ENONCE : a l'ecart du rouleau, le critere tient-il sur une matiere
            # CONSTRUITE ? Si non, l'echelle explique la reponse du rouleau ; si oui, l'explication
            # est ailleurs et la tranche doit le dire.
            "le_critere_tient_a_lecart_du_rouleau": bool(
                rouleau_deg is not None
                and any(abs(float(x["ecart_deg"]) - float(rouleau_deg)) < 1e-6
                        and x["le_choix_retient_la_marche"] for x in lisibles)),
            # ⚠⚠⚠ ET LE BARREAU ZERO DOIT LACHER : c'est la matiere ou il n'y a RIEN a lire, donc
            # celle qui rend les autres barreaux lisibles.
            "le_barreau_zero_lache": bool(
                lisibles and abs(float(lisibles[-1]["ecart_deg"])) < 1e-9
                and not lisibles[-1]["le_choix_retient_la_marche"]),
            # ⚠⚠ ET L'ECHELLE DOIT DISCRIMINER : un critere qui tiendrait a TOUS les barreaux, ou a
            # AUCUN, ne dirait rien de l'ecart.
            "lechelle_discrimine": bool(tiennent and lachent)}


def le_taux_de_faux_mesure(combien: int = DEPARTS_PAR_COUCHE,
                           replicats: int = REPLICATS_DU_TAUX, tirages: int = PERMUTATIONS,
                           frontieres=FRONTIERES_DE_LETALON, graine: int = GRAINE) -> dict:
    """Le taux de faux de la règle, MESURÉ sur une matière où il n'y a RIEN à tenir.

    ⭐⭐⭐⭐ PARCE QU'UN SUR VINGT EST UNE GARANTIE, PAS UNE MESURE, ET QUE LA GARANTIE NE S'APPLIQUE
    PAS ICI TELLE QUELLE. Une permutation rend des tirages ÉCHANGEABLES avec l'observé — c'est ce
    qui donne à `176` et à `179` leur un sur vingt. Ici l'observé vient d'une RÈGLE différente de
    celle des tirages, donc rien ne garantit qu'il soit échangeable avec eux : une règle de même
    moyenne mais de variance plus faible serait la plus basse plus souvent qu'un sur vingt. Le taux
    se mesure donc au lieu de se supposer, sur la matière où le critère n'a rien à lire — celle à
    écart de direction NUL, le dernier barreau de l'échelle.

    ⚠ Chaque replicat tire une graine neuve : ce qui varie est le départage des égalités et les
    dix-neuf tirages du nul, c'est-à-dire tout ce qui est aléatoire dans la règle.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    bloc = une_pile_a_deux_directions(COUCHES_DE_LA_CAMPAGNE, frontieres, 0.0)
    ang, coh = orientation_profile(bloc)
    pl = le_plafond_du_ruban(bloc, ang, coh, combien,
                             le_plafond(float(C.VOXEL_FIN_UM), float(C.PAS_UM)),
                             PLANCHER_DE_COHERENCE)
    if not pl:
        return {"decidable": False, "raison": "aucune couche texturée"}
    plc = les_plis_par_couche(COUCHES_DE_LA_CAMPAGNE, frontieres)
    retiennent = 0
    for t in range(int(replicats)):
        lu = les_marches_du_bloc(bloc, ang, coh, combien, pl, plc,
                                 tirages=int(tirages), graine=int(graine) + 1000 * (t + 1))
        retiennent += int(bool(lu.get("le_choix_retient_la_marche")))
    return {"decidable": True, "replicats": int(replicats), "tirages": int(tirages),
            "retiennent": int(retiennent),
            "le_taux_de_faux_mesure": round(retiennent / float(replicats), 4),
            "le_taux_garanti_par_les_tirages": round(1.0 / float(tirages + 1), 4)}


def un_chunk(bloc: np.ndarray, angles, coherences, combien: int, plafond_max: int,
             graine: int = GRAINE) -> dict:
    """Un chunk du rouleau : ses frontières LUES par `181`, puis les quatre marches.

    ⚠⚠ LES FRONTIÈRES DU ROULEAU NE SONT PAS POSÉES, ELLES SONT LUES — par le lecteur de creux que
    `180` a validé sur ce même rouleau, avec la statistique de famille de `179`. C'est ce qui rend
    la mesure sur le rouleau comparable à celle sur l'étalon : la même question, le même comptage,
    et seule la provenance des frontières change.
    """
    lu = plusieurs_creux([float(c) for c in coherences])
    frontieres = sorted(int(x["couche"]) for x in (lu.get("creux") or [])
                        if x.get("depasse_tous_les_melanges"))
    if len(frontieres) < 2:
        return {"decidable": False, "raison": "moins de deux frontières retenues",
                "frontieres": frontieres}
    pl = le_plafond_du_ruban(bloc, angles, coherences, combien, plafond_max,
                             PLANCHER_DE_COHERENCE)
    if not pl:
        return {"decidable": False, "raison": "aucune couche texturée",
                "frontieres": frontieres}
    plis = les_plis_par_couche(bloc.shape[0], frontieres)
    marches = les_marches_du_bloc(bloc, angles, coherences, combien, pl, plis,
                                  PLANCHER_DE_COHERENCE, graine=graine)
    if not marches.get("decidable"):
        return {"decidable": False, "raison": marches.get("raison"), "frontieres": frontieres}
    return {"frontieres": frontieres, "plafond_du_ruban": int(pl), **marches}


def un_segment(volume: dict, combien: int, plafond_max: int, cote: int = COTE_DU_TREILLIS,
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
        lu = un_chunk(bloc.astype(np.float32), ang, coh, combien, plafond_max, graine)
        if not lu.get("decidable", True) or "celle_qui_choisit" not in lu:
            r_ = lu.get("raison", "indécidable")
            refus[r_] = refus.get(r_, 0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)], **lu})
    return {"decidable": bool(lignes), "segment": volume["segment"], "chunks_lus": len(lignes),
            "refuses": refus,
            "part_qui_franchit_en_choisissant": _med(
                [x["celle_qui_choisit"]["part_qui_franchit"] for x in lignes]),
            "part_qui_franchit_au_hasard": _med(
                [x["le_hasard"]["part_qui_franchit"] for x in lignes]),
            "part_qui_franchit_a_la_regle_brute": _med(
                [x["la_regle_brute"]["part_qui_franchit"] for x in lignes]),
            "la_plus_basse_des_parts_du_hasard": _med(
                [x["la_plus_basse_des_parts_du_hasard"] for x in lignes
                 if x["la_plus_basse_des_parts_du_hasard"] is not None]),
            "chunks_ou_le_choix_retient": int(sum(1 for x in lignes
                                                  if x["le_choix_retient_la_marche"])),
            "excursion_en_choisissant": _med(
                [x["celle_qui_choisit"]["excursion_mediane"] for x in lignes]),
            "excursion_au_hasard": _med([x["le_hasard"]["excursion_mediane"] for x in lignes]),
            "longueur_en_choisissant": _med(
                [x["celle_qui_choisit"]["longueur_mediane"] for x in lignes]),
            "longueur_a_plat": _med([x["a_plat"]["longueur_mediane"] for x in lignes]),
            "chunks": lignes}


def juger(segments: list[dict], etalon: dict, echelle: dict, taux_de_faux: dict,
          voxel_um: float, pas_um: float, borne: dict, bascules: dict) -> dict:
    """Une surface qui choisit sa couche reste-t-elle sur sa feuille, et de combien s'en écarte-t-elle ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    chunks = [c for s in lus for c in s["chunks"]]
    g = _med([c["celle_qui_choisit"]["part_qui_franchit"] for c in chunks])
    h_ = _med([c["le_hasard"]["part_qui_franchit"] for c in chunks])
    basse = _med([c["la_plus_basse_des_parts_du_hasard"] for c in chunks
                  if c["la_plus_basse_des_parts_du_hasard"] is not None])
    tirages = int(chunks[0].get("tirages_du_nul") or PERMUTATIONS)
    # ⭐⭐⭐⭐ L'ATTENDU PAR HASARD EST CALCULE AVEC LE TAUX MESURE, JAMAIS AVEC LA GARANTIE.
    taux = taux_de_faux.get("le_taux_de_faux_mesure")
    attendus = (round(len(chunks) * float(taux), 4) if taux is not None
                else round(len(chunks) / float(tirages + 1), 4))
    b = _med([c["la_regle_brute"]["part_qui_franchit"] for c in chunks])
    exc = _med([c["celle_qui_choisit"]["excursion_mediane"] for c in chunks])
    exc_h = _med([c["le_hasard"]["excursion_mediane"] for c in chunks])
    lg = _med([c["celle_qui_choisit"]["longueur_mediane"] for c in chunks])
    lp = _med([c["a_plat"]["longueur_mediane"] for c in chunks])
    pv_g = _med([c["celle_qui_choisit"]["pas_vivants_median"] for c in chunks])
    pv_h = _med([c["le_hasard"]["pas_vivants_median"] for c in chunks])
    retiennent = int(sum(1 for c in chunks if c["le_choix_retient_la_marche"]))
    return {"decidable": True, "segments": len(lus), "chunks_lus": len(chunks),
            "frontieres_medianes": _med([len(c["frontieres"]) for c in chunks]),
            "la_part_qui_franchit_en_choisissant": g,
            "la_part_qui_franchit_au_hasard": h_,
            "la_plus_basse_des_parts_du_hasard": basse,
            "les_tirages_du_nul": tirages,
            "le_taux_de_faux_mesure": taux,
            "le_taux_garanti_par_les_tirages": taux_de_faux.get("le_taux_garanti_par_les_tirages"),
            "les_replicats_du_taux": taux_de_faux.get("replicats"),
            "les_chunks_attendus_par_hasard": attendus,
            "la_part_qui_franchit_a_la_regle_brute": b,
            "ce_que_le_choix_retient": (round(float(h_) - float(g), 4)
                                        if g is not None and h_ is not None else None),
            "le_choix_retient_fois": (round(float(h_) / float(g), 4)
                                      if g not in (None, 0.0) and h_ is not None else None),
            "chunks_ou_le_choix_retient": retiennent,
            "part_des_chunks_ou_le_choix_retient": (round(retiennent / len(chunks), 4)
                                                    if chunks else None),
            "lexcursion_en_couches": exc,
            "lexcursion_um": (round(float(exc) * float(voxel_um), 3)
                              if exc is not None else None),
            "lexcursion_au_hasard_en_couches": exc_h,
            "la_longueur_en_choisissant": lg, "la_longueur_a_plat": lp,
            "ce_que_le_choix_coute_en_longueur": (round(float(lg) - float(lp), 3)
                                                  if lg is not None and lp is not None else None),
            "les_pas_vivants_en_choisissant": pv_g, "les_pas_vivants_au_hasard": pv_h,
            # ⚠⚠ LA GARDE : franchir moins en mourant plus tot n'est pas tenir sa feuille.
            "les_deux_marches_vivent_autant": bool(
                pv_g is not None and pv_h is not None and float(pv_g) >= float(pv_h)),
            # ⭐⭐⭐⭐ LA STATISTIQUE EST LE COMPTE DE CHUNKS, CONTRE L'ATTENDU PAR HASARD, et c'est
            # exactement celle de `176` et de `180` : chaque chunk est juge par sa PROPRE famille de
            # dix-neuf tirages, donc son taux de faux garanti est un sur vingt, et le compte observe
            # se compare a ce qu'un chunk sur vingt donnerait. Une mediane de parts ne pourrait pas
            # le faire : elle est satisfaite par un frisson, ce que le barreau zero de l'echelle a
            # montre nu.
            "le_choix_retient_la_marche": bool(
                float(retiennent) > float(attendus)
                and pv_g is not None and pv_h is not None and float(pv_g) >= float(pv_h)),
            "la_regle_brute_franchit_plus": bool(g is not None and b is not None
                                                 and float(b) > float(g)),
            "ce_que_la_regle_brute_coute": (round(float(b) - float(g), 4)
                                            if g is not None and b is not None else None),
            # ⚠⚠⚠ LA SECONDE LECTURE, ET ELLE EST PUBLIEE MEME QUAND ELLE CONTREDIT LA PREMIERE.
            # Le compte de chunks dit si une minorite retient au-dela du hasard ; la mediane dit ce
            # que la marche fait EN GENERAL. Les deux peuvent diverger — c'est ce qu'un effet
            # concentre sur quelques chunks produit — et taire celle qui derange serait publier un
            # nombre juste sous un mauvais nom.
            "la_mediane_va_dans_le_meme_sens": bool(
                g is not None and h_ is not None and float(g) < float(h_)),
            "le_pas_de_la_marche_um": round(float(voxel_um), 3),
            "la_borne_du_pas_relue_de_189_couches": borne.get("en_couches"),
            "la_borne_du_pas_relue_de_189_um": borne.get("en_um"),
            "le_pas_est_sous_la_borne_fois": (
                round(float(borne["en_um"]) / float(voxel_um), 4)
                if borne.get("en_um") else None),
            "le_pas_entre_deux_feuilles_um": float(pas_um),
            "letalon_separe_les_deux": bool(etalon.get("letalon_separe_les_deux")),
            "le_choix_retient_sur_de_vraies_frontieres": bool(
                etalon.get("le_choix_retient_sur_de_vraies_frontieres")),
            "le_choix_ne_retient_rien_sur_des_frontieres_fictives": bool(
                etalon.get("le_choix_ne_retient_rien_sur_des_frontieres_fictives")),
            "la_regle_brute_franchit_plus_sur_letalon": bool(
                etalon.get("la_regle_brute_franchit_plus_sur_letalon")),
            "la_bascule_du_rouleau_deg": bascules.get("du_rouleau_deg"),
            "la_bascule_de_la_fixture_deg": bascules.get("de_la_fixture_deg"),
            "lechelle_discrimine": bool(echelle.get("lechelle_discrimine")),
            "le_critere_tient_jusqua_deg": echelle.get("le_critere_tient_jusqua_deg"),
            "le_critere_lache_a_partir_de_deg": echelle.get("le_critere_lache_a_partir_de_deg"),
            "le_critere_tient_a_lecart_du_rouleau": bool(
                echelle.get("le_critere_tient_a_lecart_du_rouleau")),
            "le_barreau_zero_lache": bool(echelle.get("le_barreau_zero_lache")),
            "le_temoin_du_rouleau_deg": bascules.get("le_temoin_du_rouleau_deg")}


def mesurer(segments_n: int = SEGMENTS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    borne = la_borne_du_pas_publiee()
    if not borne.get("en_um"):
        return {"message": "la borne du pas de `189` n'est pas lisible ; relancer `189` d'abord"}
    plafond = le_plafond(vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    bascules = les_bascules_publiees()
    if not bascules.get("du_rouleau_deg") or not bascules.get("de_la_fixture_deg"):
        return {"message": "les bascules de `176` ne sont pas lisibles ; relancer `176` d'abord"}
    if not bascules.get("le_temoin_du_rouleau_deg"):
        return {"message": "le témoin de `176` n'est pas lisible ; relancer `176` d'abord"}
    ecarts = lechelle_des_ecarts_de_direction(bascules["de_la_fixture_deg"],
                                              bascules["du_rouleau_deg"],
                                              bascules["le_temoin_du_rouleau_deg"])
    etalon = sur_la_fixture(combien)
    echelle = sur_lechelle_des_directions(ecarts, bascules["du_rouleau_deg"], combien)
    taux = le_taux_de_faux_mesure(combien)
    segs = [un_segment(v, combien, plafond, cote) for v in volumes]
    return {"departs_par_couche": int(combien), "cote_du_treillis": int(cote),
            "plafond_de_pas": int(plafond), "voxel_um": vx, "pas_um": pas, "graine": int(GRAINE),
            "ecarts_du_pas": [int(e) for e in ECARTS_DU_PAS],
            "la_borne_du_pas_relue_de_189": borne,
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "les_bascules_relues_de_176": bascules, "ecarts_deg": ecarts,
            "letalon": etalon, "lechelle_des_directions": echelle,
            "le_taux_de_faux": taux, "les_segments": segs,
            "le_verdict": juger(segs, etalon, echelle, taux, vx, pas, borne, bascules)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("UNE SURFACE QUI CHOISIT SA COUCHE RESTE-T-ELLE SUR SA FEUILLE ?")
    print(f"  pas forcé de {r['ecarts_du_pas']} couche · borne de `189` "
          f"{r['la_borne_du_pas_relue_de_189'].get('en_um')} µm · {v['chunks_lus']} chunks")
    print()
    print("  L'ÉTALON — de vraies frontières, puis des frontières FICTIVES")
    for x in e["lignes"]:
        if not x.get("decidable"):
            print(f"     {x['matiere']:<40} — {x.get('raison')}")
            continue
        print(f"     {x['matiere']:<40} attendu « {x['attendu']} » · franchit "
              f"{x['celle_qui_choisit']['part_qui_franchit']} contre "
              f"{x['le_hasard']['part_qui_franchit']} au hasard et "
              f"{x['la_regle_brute']['part_qui_franchit']} à la règle brute · retient "
              f"{x['le_choix_retient_la_marche']}")
    print()
    print("  L'ÉCHELLE DES ÉCARTS DE DIRECTION — de celui de la fixture à celui du rouleau, puis zéro")
    for x in r["lechelle_des_directions"]["lignes"]:
        if not x.get("plafond_du_ruban"):
            print(f"     {x['ecart_deg']:>8}° — {x.get('raison')}")
            continue
        marque = ("  ←— l'écart du rouleau"
                  if abs(float(x["ecart_deg"])
                         - float(r["les_bascules_relues_de_176"]["du_rouleau_deg"])) < 1e-6
                  else ("  ←— rien à lire" if float(x["ecart_deg"]) == 0.0 else ""))
        print(f"     {x['ecart_deg']:>8}° · franchit {x['part_qui_franchit']} contre "
              f"{x['part_qui_franchit_au_hasard']} (la plus basse des "
              f"{r['le_verdict']['les_tirages_du_nul']} : "
              f"{x['la_plus_basse_des_parts_du_hasard']}) · retient "
              f"{x['le_choix_retient_la_marche']}{marque}")
    print()
    print("  LE ROULEAU, SEGMENT PAR SEGMENT")
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"     segment {s['segment']} — {s.get('raison', s.get('refuses'))}")
            continue
        print(f"     segment {s['segment']} · {s['chunks_lus']} chunks · franchit "
              f"{s['part_qui_franchit_en_choisissant']} contre "
              f"{s['part_qui_franchit_au_hasard']} · retient dans "
              f"{s['chunks_ou_le_choix_retient']}/{s['chunks_lus']} chunks")
    print()
    print("  ★ LE VERDICT")
    for cle in ("segments", "chunks_lus", "frontieres_medianes", "les_tirages_du_nul",
                "la_part_qui_franchit_en_choisissant", "la_part_qui_franchit_au_hasard",
                "la_plus_basse_des_parts_du_hasard",
                "ce_que_le_choix_retient", "le_choix_retient_fois",
                "la_mediane_va_dans_le_meme_sens",
                "les_replicats_du_taux", "le_taux_de_faux_mesure",
                "le_taux_garanti_par_les_tirages",
                "chunks_ou_le_choix_retient", "les_chunks_attendus_par_hasard",
                "part_des_chunks_ou_le_choix_retient",
                "lexcursion_en_couches", "lexcursion_um", "lexcursion_au_hasard_en_couches",
                "la_longueur_en_choisissant", "la_longueur_a_plat",
                "ce_que_le_choix_coute_en_longueur", "les_pas_vivants_en_choisissant",
                "les_pas_vivants_au_hasard", "les_deux_marches_vivent_autant",
                "la_part_qui_franchit_a_la_regle_brute", "ce_que_la_regle_brute_coute",
                "la_regle_brute_franchit_plus", "le_pas_de_la_marche_um",
                "la_borne_du_pas_relue_de_189_um", "le_pas_est_sous_la_borne_fois",
                "letalon_separe_les_deux", "le_choix_retient_sur_de_vraies_frontieres",
                "le_choix_ne_retient_rien_sur_des_frontieres_fictives",
                "la_regle_brute_franchit_plus_sur_letalon",
                "la_bascule_du_rouleau_deg", "le_temoin_du_rouleau_deg",
                "lechelle_discrimine", "le_critere_tient_jusqua_deg",
                "le_critere_lache_a_partir_de_deg", "le_critere_tient_a_lecart_du_rouleau",
                "le_barreau_zero_lache", "le_choix_retient_la_marche"):
        print(f"     {cle:<52} {v.get(cle)}")


def _une_pile_a_creux(couches: int, cote: int = 32, longueur: float = 12.0,
                      brillante: int | None = None) -> np.ndarray:
    """Une pile de crêtes identiques, dont une couche peut être UNIFORMÉMENT brillante.

    ⚠⚠ ELLE EXISTE POUR LA SONDE DE `187` : la couche brillante ne porte AUCUNE crête, donc sa
    valeur au-dessus de son propre plancher est nulle partout. Une règle qui compare les brillances
    brutes y va ; une règle qui compare au-dessus du plancher de chaque couche n'y va pas.
    """
    yy, xx = np.mgrid[0:int(cote), 0:int(cote)].astype(np.float64)
    out = []
    for k in range(int(couches)):
        if brillante is not None and k == int(brillante):
            out.append(np.full((int(cote), int(cote)), 200.0))
            continue
        out.append(100.0 + 40.0 * np.cos(2.0 * np.pi * yy / float(longueur)) + 0.0 * xx)
    return np.stack(out).astype(np.float32)


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from jusquou_suit_on_une_fibre import les_departs  # noqa: PLC0415
    from un_ruban_qui_saute_perd_il_sa_fibre import un_ruban  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)

    # ⚠⚠ LA BORNE DU PAS EST RELUE DE `189` ET NON TAPEE : c'est elle qui autorise cette marche.
    borne = la_borne_du_pas_publiee()
    v("la borne du pas de `189` est relue", bool(borne.get("en_um")), str(borne))
    v("et elle est absente quand la mesure l'est",
      la_borne_du_pas_publiee(Path("/n/existe/pas.json")) == {})
    if borne.get("en_um"):
        v("★ le pas d'une couche est SOUS la borne", float(borne["en_um"]) > vx,
          f"{borne['en_um']} µm contre {vx} µm")

    # ⚠⚠⚠ LE PAS EST FORCE : zero est absent de l'echelle, sinon le glouton choisirait de rester et
    # l'excursion mesurerait la mobilite au lieu du critere.
    v("★ le pas est forcé — zéro n'est pas un écart admissible", 0 not in ECARTS_DU_PAS,
      str(ECARTS_DU_PAS))
    v("et il vaut une seule couche", set(abs(e) for e in ECARTS_DU_PAS) == {1},
      str(ECARTS_DU_PAS))

    plis = les_plis_par_couche(10, [3, 7])
    v("les plis sont indexés par leurs frontières", list(plis) == [0, 0, 0, 1, 1, 1, 1, 2, 2, 2],
      str(list(plis)))
    v("une frontière hors du bloc est ignorée",
      list(les_plis_par_couche(4, [2, 99])) == [0, 0, 1, 1], str(list(les_plis_par_couche(4, [2, 99]))))
    v("sans frontière tout le bloc est un seul pli",
      set(les_plis_par_couche(6, [])) == {0})

    # ⭐⭐ LA MARCHE A PLAT EST EXACTEMENT LE SUIVEUR DE `185`, et c'est verifie contre lui plutot
    # qu'affirme : cette marche est une GENERALISATION, pas un second suiveur.
    pile = une_pile_qui_tourne(30, 0)
    dep = les_departs(pile[10], 16)
    plat = une_marche_qui_choisit(pile, dep, 10, 0.0, 12, "fixe")
    ruban = _med(un_ruban(pile, dep, 10, 0.0, 0, 12))
    v("★★ à écart nul la marche redonne le suiveur de `185`",
      plat["longueur_mediane"] == ruban, f"{plat['longueur_mediane']} contre {ruban}")
    v("et son excursion est exactement nulle", plat["excursion_maximale"] == 0,
      str(plat["excursion_maximale"]))

    # ⭐⭐⭐ LES EGALITES SE TRANCHENT AU HASARD, ET LA SONDE LE VERIFIE SUR UNE MATIERE OU TOUT EST A
    # EGALITE. Un departage deterministe ferait descendre toute marche tout droit : l'excursion
    # vaudrait alors le plafond entier au lieu d'une diffusion.
    identique = _une_pile_a_creux(41)
    dep_i = les_departs(identique[20], 16)
    egal = une_marche_qui_choisit(identique, dep_i, 20, 0.0, 20, "glouton")
    v("★★★ sur une matière où tout est à égalité, la marche ne descend PAS tout droit",
      egal["excursion_maximale"] is not None and egal["excursion_maximale"] < 20,
      f"excursion max {egal['excursion_maximale']} pour un plafond de 20")
    v("et son excursion reste celle d'une diffusion",
      egal["excursion_mediane"] is not None and egal["excursion_mediane"] <= 8.0,
      str(egal["excursion_mediane"]))

    # ⭐⭐⭐⭐ LA SONDE DE `187` : une couche UNIFORMEMENT brillante et sans crete. La regle qui compare
    # au-dessus du plancher de chaque couche n'y va pas ; la regle brute y va. Sans cette regle
    # l'instrument lirait le PROFIL DE DENSITE et non la fibre.
    dense = _une_pile_a_creux(11, brillante=6)
    dep_d = les_departs(dense[4], 16)
    pl_d = les_plis_par_couche(11, [6])
    normal = une_marche_qui_choisit(dense, dep_d, 4, 0.0, 8, "glouton", plis_par_couche=pl_d)
    brute = une_marche_qui_choisit(dense, dep_d, 4, 0.0, 8, "glouton", plis_par_couche=pl_d,
                                   brut=True)
    v("★★★★ la valeur comparée est celle au-dessus du plancher de sa couche",
      normal["part_qui_franchit"] is not None and normal["part_qui_franchit"] < 0.25,
      f"{normal['part_qui_franchit']} franchit vers la couche brillante")
    v("★★★★ et la règle BRUTE se laisse attirer par la couche dense",
      brute["part_qui_franchit"] is not None and brute["part_qui_franchit"] > 0.75,
      f"{brute['part_qui_franchit']} contre {normal['part_qui_franchit']}")

    # ⚠⚠ L'ECHELLE DES ECARTS DE DIRECTION EST DERIVEE DE BOUT EN BOUT, ET SES BORNES SONT DES
    # NOMBRES PUBLIES PAR `176`.
    bas = les_bascules_publiees()
    v("les bascules de `176` sont relues",
      bool(bas.get("du_rouleau_deg") and bas.get("de_la_fixture_deg")
           and bas.get("le_temoin_du_rouleau_deg")), str(bas))
    v("et elles sont absentes quand la mesure l'est",
      les_bascules_publiees(Path("/n/existe/pas.json")) == {})
    if bas.get("du_rouleau_deg"):
        ech = lechelle_des_ecarts_de_direction(bas["de_la_fixture_deg"], bas["du_rouleau_deg"],
                                               bas["le_temoin_du_rouleau_deg"])
        v("★ l'échelle part de l'écart de la FIXTURE", ech[0] == bas["de_la_fixture_deg"],
          str(ech))
        v("★★★ et l'écart du ROULEAU est un barreau", bas["du_rouleau_deg"] in ech, str(ech))
        v("★★★★ et zéro est son dernier barreau", ech[-1] == 0.0, str(ech))
        v("elle descend sous le témoin de l'estimateur",
          any(0.0 < x < bas["le_temoin_du_rouleau_deg"] for x in ech), str(ech))
        v("elle décroît", all(a_ > b_ for a_, b_ in zip(ech, ech[1:])), str(ech))

    # ⭐⭐⭐⭐ LA MATIERE A DEUX DIRECTIONS POSE SON ECART, ET C'EST CE QUI REND L'ECHELLE POSSIBLE.
    deux = une_pile_a_deux_directions(60, (30,), 90.0)
    a0, _c0 = orientation_profile(deux)
    ecart_lu = abs(float(a0[10]) - float(a0[50]))
    v("★★ la pile à deux directions porte bien l'écart POSÉ",
      abs(min(ecart_lu, 180.0 - ecart_lu) - 90.0) < 6.0, f"{round(ecart_lu, 2)}°")
    plat_ = une_pile_a_deux_directions(60, (30,), 0.0)
    a1, _c1 = orientation_profile(plat_)
    v("et à écart nul elle n'en porte aucun",
      abs(float(a1[10]) - float(a1[50])) < 1e-6, str(abs(float(a1[10]) - float(a1[50]))))

    # ⚠⚠ LE NUL A LES MEMES DEPARTS ET VIT AUTANT : sans cette garde, « franchit moins » et « meurt
    # plus tot » seraient le meme nombre.
    fix = bloc_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, 0.0, CONTRASTE_DE_LA_FIXTURE,
                             PLIS_DE_LA_FIXTURE, vx, pas, transition_um=0.0)
    ang_f, coh_f = orientation_profile(fix)
    fr_f = les_frontieres_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, 0.0, PLIS_DE_LA_FIXTURE, vx, pas)
    v("les frontières de la fixture sont deux", len(fr_f) == 2, str(fr_f))
    plc = les_plis_par_couche(COUCHES_DE_LA_CAMPAGNE, fr_f)
    pl_f = le_plafond_du_ruban(fix, ang_f, coh_f, DEPARTS_PAR_COUCHE, le_plafond(vx, pas),
                               PLANCHER_DE_COHERENCE)
    lu = les_marches_du_bloc(fix, ang_f, coh_f, DEPARTS_PAR_COUCHE, pl_f, plc)
    v("les quatre marches partent du même jeu",
      len({lu[c]["marches"] for c in ("celle_qui_choisit", "le_hasard", "a_plat",
                                      "la_regle_brute")}) == 1,
      str({c: lu[c]["marches"] for c in ("celle_qui_choisit", "le_hasard")}))
    v("★★ et les deux marches appariées vivent autant", lu["les_deux_marches_vivent_autant"],
      f"{lu['pas_vivants_de_celle_qui_choisit']} contre {lu['pas_vivants_du_hasard']}")
    v("★★★ sur une frontière POSÉE, le choix retient la marche",
      lu["le_choix_retient_la_marche"],
      f"{lu['celle_qui_choisit']['part_qui_franchit']} contre "
      f"{lu['le_hasard']['part_qui_franchit']}")
    v("et la marche à plat ne franchit rien du tout",
      lu["a_plat"]["part_qui_franchit"] == 0.0, str(lu["a_plat"]["part_qui_franchit"]))

    # ⭐⭐⭐⭐ LA FACE NEGATIVE DE L'ETALON : les MEMES frontieres declarees sur une matiere qui ne
    # change pas de direction. Le choix ne doit RIEN retenir, sinon l'instrument lit sa marche.
    sans = une_pile_qui_tourne(COUCHES_DE_LA_CAMPAGNE,
                               COUCHES_DE_LA_CAMPAGNE * COUCHES_SANS_FRONTIERE)
    ang_s, coh_s = orientation_profile(sans)
    pl_s = le_plafond_du_ruban(sans, ang_s, coh_s, DEPARTS_PAR_COUCHE, le_plafond(vx, pas),
                               PLANCHER_DE_COHERENCE)
    lu_s = les_marches_du_bloc(sans, ang_s, coh_s, DEPARTS_PAR_COUCHE, pl_s, plc)
    v("★★★★ sur des frontières FICTIVES, le choix ne retient rien",
      not lu_s["le_choix_retient_la_marche"],
      f"{lu_s['celle_qui_choisit']['part_qui_franchit']} contre "
      f"{lu_s['le_hasard']['part_qui_franchit']}")
    v("et cette matière n'a bien aucun changement de direction lisible",
      float(np.std([float(a) for a in ang_s])) < 12.0,
      str(round(float(np.std([float(a) for a in ang_s])), 3)))

    # ⚠⚠⚠ ET SUR DU BRUIT PUR LE CHOIX NE DOIT RIEN RETENIR NON PLUS — c'est la lecon de `186` :
    # optimiser trouve de la longueur sur n'importe quelle image, donc une mesure qui sortirait
    # POSITIVE sur du bruit mesurerait la liberte qu'on s'est donnee.
    # ⚠⚠ ET LA SONDE PORTE SUR TOUT LE BLOC ET NON SUR UNE COUCHE : une premiere version ne
    # marchait que seize departs depuis une seule profondeur, et tranchait donc sur DEUX
    # franchissements d'ecart — elle rapportait du bruit et non une propriete.
    r_ = np.random.default_rng(7)
    bruit = r_.normal(120.0, 20.0, (COUCHES_DE_LA_CAMPAGNE, 48, 48)).astype(np.float32)
    lu_b = les_marches_du_bloc(bruit, np.zeros(COUCHES_DE_LA_CAMPAGNE),
                               np.full(COUCHES_DE_LA_CAMPAGNE, 0.9), DEPARTS_PAR_COUCHE,
                               pl_f, plc)
    v("★★★ sur du bruit pur le choix ne retient rien", not lu_b["le_choix_retient_la_marche"],
      f"{lu_b['celle_qui_choisit']['part_qui_franchit']} contre "
      f"{lu_b['le_hasard']['part_qui_franchit']} sur {lu_b['marches']} marches")

    # ⭐⭐⭐⭐ ET LA REGLE REFUTEE EST PORTEE COMME CONTROLE NOMME : un nul a UN SEUL tirage est
    # satisfait par un frisson. Sur une matiere SANS aucun changement de direction — celle ou il n'y
    # a rien a tenir — un tirage unique passe au vert, la famille de dix-neuf non.
    zero = une_pile_a_deux_directions(COUCHES_DE_LA_CAMPAGNE, (36, 72), 0.0)
    ang_z, coh_z = orientation_profile(zero)
    pl_z = le_plafond_du_ruban(zero, ang_z, coh_z, DEPARTS_PAR_COUCHE, le_plafond(vx, pas),
                               PLANCHER_DE_COHERENCE)
    un_seul = les_marches_du_bloc(zero, ang_z, coh_z, DEPARTS_PAR_COUCHE, pl_z, plc, tirages=1)
    famille = les_marches_du_bloc(zero, ang_z, coh_z, DEPARTS_PAR_COUCHE, pl_z, plc)
    v("★★★★ un nul à UN SEUL tirage est satisfait par un frisson",
      un_seul["le_choix_retient_la_marche"],
      f"{un_seul['celle_qui_choisit']['part_qui_franchit']} contre "
      f"{un_seul['le_hasard']['part_qui_franchit']}")
    v("★★★★ et la famille de dix-neuf ne l'est PAS",
      not famille["le_choix_retient_la_marche"],
      f"{famille['celle_qui_choisit']['part_qui_franchit']} contre la plus basse "
      f"{famille['la_plus_basse_des_parts_du_hasard']}")
    v("la famille compte bien dix-neuf tirages", famille["tirages_du_nul"] == PERMUTATIONS,
      str(famille["tirages_du_nul"]))

    # ⭐⭐⭐⭐ ET LE TAUX DE FAUX SE MESURE AU LIEU DE SE SUPPOSER. Un sur vingt est la GARANTIE
    # d'une permutation, dont les tirages sont echangeables avec l'observe ; ici l'observe vient
    # d'une REGLE differente, donc rien ne garantit l'echangeabilite et le taux doit se lire sur la
    # matiere ou le critere n'a rien a tenir.
    v("★ le nombre de replicats est DÉRIVÉ de la garantie qu'il mesure",
      REPLICATS_DU_TAUX == 2 * (PERMUTATIONS + 1), str(REPLICATS_DU_TAUX))
    taux = le_taux_de_faux_mesure(DEPARTS_PAR_COUCHE, replicats=4)
    v("★★★ le taux de faux est mesuré, et la garantie est publiée à côté",
      taux.get("decidable") and 0.0 <= float(taux["le_taux_de_faux_mesure"]) <= 1.0
      and abs(float(taux["le_taux_garanti_par_les_tirages"]) - 1.0 / (PERMUTATIONS + 1)) < 1e-9,
      str(taux))

    # ⚠ UN CHUNK SANS DEUX FRONTIERES LUES EST REFUSE, jamais compte comme « ne franchit pas ».
    refus = un_chunk(bruit, np.zeros(COUCHES_DE_LA_CAMPAGNE),
                     np.full(COUCHES_DE_LA_CAMPAGNE, 0.9), 16, 18)
    v("un bloc sans deux frontières lues est refusé", refus.get("decidable") is False,
      str(refus.get("raison")))

    v("la marche refuse un plafond nul",
      une_marche_qui_choisit(pile, dep, 10, 0.0, 0)["longueur_mediane"] is None)
    v("et un jeu de départs vide",
      une_marche_qui_choisit(pile, [], 10, 0.0, 12)["marches"] == 0)

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "une_surface_qui_choisit_sa_couche.py"
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
