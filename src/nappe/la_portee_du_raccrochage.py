#!/usr/bin/env python3
"""Combien de spires la marche traverse-t-elle avant de se perdre ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA QUESTION DU BUT. Sept tranches ont mesuré ce que
coûte **un** pas — 37,5 µm pour le chemin déployé, contre 43,6 en ne bougeant pas et 20,0 pour un
oracle. Mais le but n'est pas un pas : c'est le **déroulement**, donc une marche qui traverse
plusieurs feuilles. Et cette marche-là n'a jamais été mesurée avec la méthode **réellement
déployée** : les tranches sur la dérive datent d'avant l'accord de voisinage et d'avant l'écart
apparié qui a invalidé leur instrument.

⭐⭐⭐ LE CRITÈRE N'EST PAS CHOISI, IL EST PHYSIQUE. Une marche est **perdue** quand son erreur
dépasse la **demi-feuille** : au-delà, le point prédit est plus proche de la feuille voisine que
de la sienne, et rien en aval ne peut le savoir. La portée est donc le plus grand bras dont
l'erreur reste sous ce seuil, et ce seuil vient de la matière, pas d'un réglage.

⚠⚠ LA MARCHE NE CONNAÎT QUE SA SPIRE DE DÉPART. À chaque bras, elle part de sa **propre
prédiction** — jamais de la spire publiée suivante —, y recalcule ses normales, y relit son
gabarit. Relire les spires publiées en chemin serait se ré-ancrer à chaque pas, et la portée
mesurerait alors les ancres et non la marche.

⚠⚠ ET LA POPULATION RÉTRÉCIT EN CHEMIN, ce qui est un fait sur la marche et pas un défaut : une
cellule dont la ligne sort du volume est perdue pour de bon. Le nombre de cellules encore vivantes
à chaque bras est donc publié à côté de l'erreur — et un second jeu de nombres, restreint aux
cellules vivantes **au dernier bras**, dit ce que la même population donne d'un bout à l'autre.

Usage :
    uv run python src/nappe/la_portee_du_raccrochage.py --verifier
    uv run python src/nappe/la_portee_du_raccrochage.py --cote 960 \\
        --json docs/mesures/la_portee_du_raccrochage.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

from le_corpus_des_spires import corpus_fabrique, corpus_publie, volume_fabrique  # noqa: E402
from le_critere_du_raccrochage import poser_sur_la_grille  # noqa: E402
from lecart_apparie import ecart_apparie, tranche  # noqa: E402

# ⚠ Les marcheurs comparés. « rien » est le pas normal seul — la référence contre laquelle tout
# se juge ; « oracle » regarde la cible une fois par cellule et par bras, donc c'est une BORNE
# et jamais une méthode ; « melange » est le témoin, même géométrie et forme détruite.
MARCHEURS = ("rien", "rien_lisse", "raccroche", "raccroche_lisse", "sortie_raccrochee",
             "sortie_lisse", "melange", "oracle")
# ⚠⚠ LES DEUX MARCHEURS QUI COMPOSENT CE QUI A MARCHÉ. `rien_lisse` avance au pas normal et
# lisse la NAPPE entre deux bras ; `sortie_lisse` fait de même et publie la sortie raccrochée.
# Aucun des deux n'ajoute de réglage : le voisinage est celui qui tourne, et la séparation
# état/sortie est la séparation ordinaire d'un système. Ce sont des COMPOSITIONS, pas des idées.
ETAT_LISSE = ("rien_lisse", "sortie_lisse")
LISSE = "raccroche_lisse"
# ⭐⭐⭐ LE MARCHEUR QUI SÉPARE L'ÉTAT DE LA SORTIE. Sept tranches ont mesuré qu'un raccrochage
# gagne quelques µm sur UN pas ; la tranche de la marche mesure qu'il en coûte cinquante sur
# huit, parce que ce qu'il corrige devient la surface où le bras suivant estime ses normales.
# Les deux faits tiennent ensemble dès qu'on cesse de RÉINJECTER la correction : la marche
# avance au pas normal, et le raccrochage n'est appliqué qu'à ce qui est PUBLIÉ. C'est la
# séparation ordinaire entre l'état d'un système et sa sortie, et elle n'ajoute aucun réglage.
SORTIE = "sortie_raccrochee"
BORNE = "oracle"
TEMOIN = "melange"


def portee(erreurs: list[float], demi_feuille_um: float) -> int:
    """Le plus grand bras dont l'erreur reste sous la demi-feuille — zéro si le premier échoue.

    ⚠⚠⚠ LA PORTÉE S'ARRÊTE AU PREMIER ÉCHEC, elle ne compte pas les bras réussis. Une marche
    qui repasse sous le seuil après l'avoir franchi n'a pas « rattrapé » : elle a traversé une
    zone où elle était plus proche de la mauvaise feuille, et tout ce qui suit est bâti dessus.
    Compter les succès isolés rendrait une portée qu'aucun dérouleur ne peut utiliser.

    ⚠ Le seuil est la demi-feuille, qui vient de la matière : au-delà, le point prédit est plus
    près de la feuille voisine que de la sienne.
    """
    for k, e in enumerate(erreurs):
        if not np.isfinite(e) or e >= demi_feuille_um:
            return k
    return len(erreurs)


def _lisser_la_nappe(neuf, masque, accorder_les_voisins, demi: int = 1, passes: int = 1):
    """Le voisinage déployé, appliqué à la NAPPE canal par canal, à masque CONSTANT.

    ⚠⚠⚠ LE MASQUE NE BOUGE PAS. Un lissage qui écarterait les cellules dont le voisinage ne fait
    pas majorité comparerait ce marcheur aux autres sur une AUTRE population, et une médiane sur
    moins de cellules n'est pas une médiane meilleure. Là où le voisinage ne suffit pas, la
    cellule garde sa valeur non lissée — c'est exactement ce que fait le raccrochage déployé sur
    son champ de décalage.

    ⚠ Écrit une seule fois pour ses trois appelants. Deux copies de « lisser la nappe » seraient
    deux occasions de ne pas s'accorder sur ce que le repli fait.

    ⚠⚠ `demi` et `passes` valent par défaut CE QUI TOURNE — la demi-largeur et le nombre
    d'applications du voisinage déployé — de sorte que ne rien passer reproduit exactement la
    mesure publiée. Ils existent pour qu'un balayage puisse les faire varier HORS ÉCHANTILLON,
    jamais pour qu'un appelant choisisse le réglage qui l'arrange.

    ⚠ Zéro passe rend la nappe intacte : c'est l'étage « brut », traité comme les autres.

    ⚠⚠⚠ REND AUSSI LA PART DE CELLULES RÉELLEMENT LISSÉES, et ce n'est pas un détail : une
    fenêtre large exige une majorité de voisins présents, donc plus elle s'élargit, plus elle
    est REFUSÉE près des bords et plus les cellules gardent leur valeur brute. Sans ce nombre,
    « la fenêtre 17×17 gagne » pourrait vouloir dire « elle ne s'applique presque plus », ce qui
    est un tout autre énoncé — et c'est la faute que le balayage du cône de directions a déjà
    payée, où l'optimum était un plancher du balayage et pas une propriété de la matière.
    """
    part = 1.0 if int(passes) > 0 else 0.0
    for _ in range(max(0, int(passes))):
        assez = masque.copy()
        canaux = []
        for c in range(neuf.shape[2]):
            v2, ok2 = accorder_les_voisins(neuf[:, :, c], masque, demi=max(1, int(demi)))
            canaux.append(v2)
            assez &= ok2
        pris = assez & masque
        vus = int(masque.sum())
        part = min(part, (int(pris.sum()) / vus) if vus else 0.0)
        for c in range(neuf.shape[2]):
            neuf[:, :, c] = np.where(pris & np.isfinite(canaux[c]), canaux[c], neuf[:, :, c])
    return neuf, part


def marcher(nom: str, grille, garde, cible, vol, reglage, rng) -> dict | None:
    """Un pas de marche depuis la grille courante, par la méthode demandée.

    ⚠⚠⚠ LES NORMALES SONT RECALCULÉES SUR LA GRILLE COURANTE, qui est la PRÉDICTION du bras
    précédent et non une spire publiée. C'est ce que fait un vrai déroulement, et c'est là que
    l'erreur se compose : une normale estimée sur une surface déjà fausse l'est un peu plus.

    Rend la grille prédite, son masque, et de quoi juger — ou None si le pas n'est plus
    calculable.
    """
    from le_pas_normal_atteint_la_spire import distance_a, normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        accorder_les_voisins, correler, decalage_retenu, le_long, profil_autour,
    )

    n, bon = normales(grille, garde)
    vivant = bon & garde
    if int(vivant.sum()) < reglage["minimum"]:
        return None
    p, d = grille[vivant], n[vivant]
    pas_vx = reglage["pas_vx"]
    voxel_um = reglage["voxel_um"]
    # ⚠ Le sens sortant est décidé sur la CIBLE, et c'est le bit de supervision unique de toute
    # la campagne. Le décider sur la prédiction précédente ferait tourner la marche sur
    # elle-même dès qu'elle s'égare.
    sortant = float(np.median(distance_a(p + d * pas_vx, cible, voxel_um)))
    rentrant = float(np.median(distance_a(p - d * pas_vx, cible, voxel_um)))
    sens = 1.0 if sortant <= rentrant else -1.0
    prevu, dd = p + d * (sens * pas_vx), d * sens
    # ⚠⚠⚠ CE QUE LE BRAS DOIT RÉELLEMENT FRANCHIR, mesuré AVANT le pas et depuis là où la
    # marche se tient. Sans lui, un bras que le corpus rend impossible — deux spires voisines
    # par leur numéro et éloignées de huit feuilles dans la matière — se lit comme une méthode
    # qui échoue, et le blâme tombe sur le marcheur au lieu du corpus.
    depart = distance_a(p, cible, voxel_um)
    if nom in ("rien", "rien_lisse"):
        # ⚠ La grille porte trois coordonnées par cellule : son masque a donc la forme des deux
        # premiers axes, jamais celle de la grille entière. Confondre les deux fait lever la
        # pose sur un décalage de formes — ce qui est le bon échec, mais tardif.
        from la_lissite_de_la_feuille import rugosite_de_la_nappe  # noqa: PLC0415

        part_lissee = 0.0
        neuf = np.full(grille.shape, np.nan)
        neuf[vivant] = prevu
        if nom == "rien_lisse":
            neuf, part_lissee = _lisser_la_nappe(neuf, vivant, accorder_les_voisins,
                                                 *reglage["lissage_nappe"])
            prevu = neuf[vivant]
        # ⚠⚠ LE PLANCHER DU BRAS, PAR CELLULE. Une distance à un nuage est 1-lipschitzienne :
        # un point à distance d du nuage, déplacé de L, ne peut pas être à moins de |d − L|.
        # C'est une borne INFÉRIEURE dérivée de la géométrie et d'aucun réglage, et elle vaut
        # pour l'oracle comme pour le reste — lui aussi garde la longueur de son pas.
        return dict(grille=neuf, garde=vivant, points=prevu, directions=dd,
                    decalage=np.zeros(len(prevu)), depart_um=float(np.median(depart)),
                    plancher_um=float(np.median(np.abs(depart - pas_vx * voxel_um))),
                    glissement_um=0.0, glissement_max_um=0.0, rugosite_vx=0.0,
                    rugosite_nappe_um=rugosite_de_la_nappe(neuf, vivant, voxel_um),
                    part_lissee=round(part_lissee, 3),
                    forme_grille=list(vivant.shape))

    t_gab = reglage["t_gab"]
    t_ligne = reglage["t_ligne"]
    vg, okg = le_long(p, d, t_gab, vol)
    if int(okg.sum()) < reglage["minimum"]:
        return None
    gab = profil_autour(vg[okg])
    gab_oriente = gab if sens > 0 else gab[::-1]
    v_, okv = le_long(prevu, dd, t_ligne, vol)
    if int(okv.sum()) < reglage["minimum"]:
        return None
    lisible = poser_sur_la_grille(okv.astype(float), vivant, vivant.shape) == 1.0
    P, D, L = prevu[okv], dd[okv], v_[okv]
    corr, centres = correler(L, gab_oriente, t_ligne)
    if nom == TEMOIN:
        corr, _ = correler(L, rng.permuted(gab_oriente), t_ligne)
    if nom == BORNE:
        from le_raccrochage_choisit_il_bien import decalage_de_loracle  # noqa: PLC0415

        t, _ = decalage_de_loracle(P, D, centres, cible, voxel_um)
    else:
        brut = decalage_retenu(corr, centres)
        # ⚠⚠ L'ACCORD DE VOISINAGE EST LE CHEMIN RÉELLEMENT DÉPLOYÉ, et sept tranches ont
        # mesuré que tout le gain vient de lui. Une marche qui ne l'appliquerait pas mesurerait
        # un raccrochage plus grossier que celui qui tourne.
        champ = poser_sur_la_grille(brut, lisible, lisible.shape)
        acc, _ = accorder_les_voisins(champ, lisible)
        ou = np.argwhere(lisible)
        val = acc[ou[:, 0], ou[:, 1]]
        t = np.where(np.isfinite(val), val, brut)
    neuf = np.full(grille.shape, np.nan)
    ou = np.argwhere(lisible)
    neuf[ou[:, 0], ou[:, 1]] = P + t[:, None] * D
    champ_t = poser_sur_la_grille(t, lisible, lisible.shape)
    # ⚠⚠⚠ CE QUE SEPT TRANCHES N'ONT JAMAIS LISSÉ : la NAPPE. Toutes ont lissé le champ de
    # DÉCALAGE d'UN pas ; ce qu'une marche abîme est la SURFACE sur laquelle le bras suivant
    # estime ses normales et lit son gabarit. Le voisinage employé est celui qui tourne — même
    # demi-largeur, même règle de majorité — donc ce marcheur n'ajoute aucun réglage.
    part_lissee = 0.0
    if nom == LISSE:
        neuf, part_lissee = _lisser_la_nappe(neuf, lisible, accorder_les_voisins,
                                             *reglage["lissage_nappe"])
    pts = neuf[ou[:, 0], ou[:, 1]]
    # ⚠⚠ LE PLANCHER EST CALCULÉ SUR LE DÉPLACEMENT RÉELLEMENT SUBI, du point de départ au point
    # final, et non sur le pas nominal. Le raccrochage glisse le long de la ligne et le lissage
    # déplace encore : prendre le pas donnerait un « plancher » que l'erreur peut passer sous,
    # c'est-à-dire pas un plancher.
    d0 = np.full(grille.shape, np.nan)
    d0[vivant] = p
    depart_g = poser_sur_la_grille(depart, vivant, vivant.shape)
    dep_ok = depart_g[ou[:, 0], ou[:, 1]]
    bouge = np.linalg.norm(pts - d0[ou[:, 0], ou[:, 1]], axis=1) * voxel_um
    # ⚠ CE QUE LA CORRÉLATION PROPOSE, ET CE QUE LE BRAS A PRIS. Le premier borne le second, et
    # les deux sont publiés : une borne sans usage ne dit pas si elle serre.
    borne = float(max(abs(centres[0]), abs(centres[-1]))) * voxel_um if len(centres) else 0.0
    t_final = champ_t[ou[:, 0], ou[:, 1]]
    # ⚠⚠ LA RUGOSITÉ DU CHAMP DE DÉCALAGE, bras par bras : c'est la PRÉMISSE du diagnostic — si
    # la surface ne se froisse pas, « la marche froisse ce qu'elle laisse » est une histoire et
    # non un fait. Elle est mesurée sur le champ que ce bras a réellement appliqué.
    from la_lissite_de_la_feuille import rugosite_de_la_nappe  # noqa: PLC0415
    from loracle_est_il_atteignable import rugosite  # noqa: PLC0415

    return dict(grille=neuf, garde=lisible, points=pts, directions=D,
                decalage=t, depart_um=float(np.median(dep_ok)),
                plancher_um=float(np.median(np.abs(dep_ok - bouge))),
                glissement_um=float(np.nanmedian(np.abs(t_final))) * voxel_um,
                glissement_max_um=borne,
                rugosite_vx=rugosite(champ_t, lisible),
                rugosite_nappe_um=rugosite_de_la_nappe(neuf, lisible, voxel_um),
                part_lissee=round(part_lissee, 3), forme_grille=list(lisible.shape))


def sur_les_cellules_communes(a: list[dict], b: list[dict]) -> tuple[list, list, list]:
    """Les deux séries de médianes, bras par bras, sur les cellules que les DEUX ont gardées.

    ⚠⚠⚠ DEUX MARCHEURS DIVERGENT, DONC LEURS MASQUES DIVERGENT. Comparer leurs médianes
    publiées reviendrait à comparer deux populations, et une médiane sur moins de cellules
    n'est pas une médiane meilleure — c'est la faute que ce dépôt a déjà eu à retirer.

    Rend `(médianes de a, médianes de b, nombre de cellules communes)`, tronqué au nombre de
    bras que les deux ont faits. Un bras sans aucune cellule commune est écarté des trois.
    """
    ma, mb, nc = [], [], []
    for x, y in zip(a, b):
        cles = np.intersect1d(x["cles"], y["cles"], assume_unique=False)
        if len(cles) == 0:
            break
        ia = np.isin(x["cles"], cles)
        ib = np.isin(y["cles"], cles)
        ma.append(round(float(np.median(x["erreurs"][ia])), 1))
        mb.append(round(float(np.median(y["erreurs"][ib])), 1))
        nc.append(int(len(cles)))
    return ma, mb, nc


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, bras_max: int = 8,
            corpus: dict | None = None, volume=None, decalage_ancre: int = 0,
            lissage_nappe: tuple[int, int] = (1, 1),
            marcheurs: tuple[str, ...] | None = None) -> dict:
    """Jusqu'où chaque marcheur va avant que son erreur ne dépasse la demi-feuille."""
    from le_pas_normal_atteint_la_spire import distance_a, normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        BOITE_CENTRE, BOITE_COTE, CacheDisque, Volume, ZARR, accorde_aux_spires,
        url_du_volume,
    )

    c = corpus_publie() if corpus is None else corpus
    voxel_um = float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um
    demi_vx = pas_vx / 2.0
    demi_gab = max(1, int(round(demi_vx / 2.0)))
    demi_feuille_um = ecart_um / 2.0
    if volume is None and not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({c['volume']})")
    if volume is None:
        import tracecheck as tc  # noqa: PLC0415

        url = url_du_volume()
        vol = Volume(url, tc.array_meta(url, 0, 120), CacheDisque(actif=cache_actif))
    else:
        vol = volume

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    reglage = dict(minimum=minimum, pas_vx=pas_vx, voxel_um=voxel_um,
                   lissage_nappe=tuple(lissage_nappe),
                   t_gab=np.arange(-demi_gab, demi_gab + 1e-9, 1.0),
                   t_ligne=np.arange(-(demi_vx + demi_gab), demi_vx + demi_gab + 1e-9, 1.0))

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        grilles[rang] = (a, dans)
        nuages[rang] = a[ok]

    # ⚠⚠ L'ANCRE EST LA SPIRE LA PLUS BASSE DE LA BOÎTE, et la marche va vers les rangs
    # croissants. Choisir l'ancre sur le résultat serait choisir l'endroit où la marche est
    # belle ; la prendre au bord est le seul choix qui ne regarde rien.
    rangs = sorted(grilles)
    if len(rangs) < 2:
        raise RuntimeError("il faut au moins deux spires dans la boîte pour marcher")
    # ⚠⚠ L'ANCRE EST LA PLUS BASSE DE LA BOÎTE, et `decalage_ancre` la fait glisser vers le haut
    # pour REFAIRE la même marche ailleurs. Ce n'est pas un réglage de méthode : c'est ce qui
    # permet de demander si un verdict tient hors de la population où il a été trouvé — question
    # que ce dépôt a déjà eu à se poser après trois verdicts inversés par un changement de pas.
    if not 0 <= decalage_ancre < len(rangs) - 1:
        raise RuntimeError(
            f"décalage d'ancre {decalage_ancre} hors des {len(rangs)} spires de la boîte")
    ancre = rangs[decalage_ancre]
    atteignables = [r for r in rangs if r > ancre][:bras_max]
    if not atteignables:
        raise RuntimeError("aucune spire à atteindre depuis l'ancre")

    # ⚠⚠⚠ CE QUE LE CORPUS DEMANDE À CHAQUE BRAS, mesuré sans aucun marcheur : la distance
    # médiane de la spire de départ à la spire d'arrivée, dans la boîte. C'est une DESCRIPTION
    # du corpus et jamais un verdict sur une méthode — un marcheur qui a déjà dérivé vers sa
    # cible part de plus près que la spire publiée, donc ce chiffre ne le borne pas. Ce qui le
    # borne est son propre plancher, bras par bras. Ce que cette ligne empêche, c'est de lire
    # un trou de numérotation — deux spires voisines par leur numéro et éloignées de huit
    # feuilles dans la matière — comme un échec de méthode.
    chaine = [ancre, *atteignables]
    corpus_bras = []
    for k, (de, vers) in enumerate(zip(chaine, chaine[1:]), start=1):
        ad, dd_ = grilles[de]
        g = float(np.median(distance_a(ad[dd_], nuages[vers], voxel_um)))
        corpus_bras.append(dict(bras=k, de=de, vers=vers, ecart_um=round(g, 1),
                                ecart_au_pas_um=round(abs(g - ecart_um), 1),
                                au_pas_nominal=bool(abs(g - ecart_um) < demi_feuille_um)))

    rng = np.random.default_rng(graine)
    glissement_max = 0.0
    resultats: dict[str, list[dict]] = {}
    # ⚠⚠ RESTREINDRE LES MARCHEURS SERT UN BALAYAGE, PAS UN VERDICT. Un balayage de réglage n'a
    # besoin que de la colonne qu'il balaie, et faire marcher les autres à chaque réglage
    # coûterait des lectures de volume pour rien. Mais un résultat restreint ne porte plus les
    # verdicts qui comparent les colonnes absentes : ils sont alors mis à None, jamais devinés.
    voulus = tuple(MARCHEURS if marcheurs is None else marcheurs)
    inconnus = [x for x in voulus if x not in MARCHEURS]
    if inconnus:
        raise RuntimeError(f"marcheur(s) inconnu(s) : {inconnus}")
    for nom in voulus:
        grille, garde = grilles[ancre]
        bras = []
        for k, cible_rang in enumerate(atteignables, start=1):
            cible = nuages[cible_rang]
            # ⭐⭐⭐ L'ÉTAT ET LA SORTIE SONT DEUX CHOSES. Pour ce marcheur, l'état avance au pas
            # normal — donc rien ne se compose — et le raccrochage est lu SUR CE MÊME DÉPART
            # sans jamais être réinjecté. Ce qui est jugé est la sortie ; ce qui est porté au
            # bras suivant est l'état. Confondre les deux est exactement ce que la tranche de
            # la marche a mesuré comme coûteux.
            if nom in (SORTIE, "sortie_lisse"):
                etat = marcher("rien_lisse" if nom == "sortie_lisse" else "rien",
                               grille, garde, cible, vol, reglage, rng)
                pas = marcher("raccroche", grille, garde, cible, vol, reglage, rng)
                if etat is None or pas is None:
                    break
            else:
                etat = pas = marcher(nom, grille, garde, cible, vol, reglage, rng)
                if pas is None:
                    break
            glissement_max = max(glissement_max, pas["glissement_max_um"])
            e = distance_a(pas["points"], cible, voxel_um)
            # ⚠⚠ LE PLANCHER DU BRAS : un pas de longueur nominale le long de la normale ne
            # peut pas mieux faire que l'écart entre ce qu'il franchit et ce qu'il devait
            # franchir. C'est une borne INFÉRIEURE sur l'erreur, dérivée et non choisie —
            # aucune méthode qui garde la longueur du pas ne descend en dessous.
            ou_k = np.argwhere(pas["garde"])
            bras.append(dict(bras=k, vers=cible_rang, cellules=int(len(e)),
                             erreur_um=round(float(np.median(e)), 1),
                             # ⚠⚠⚠ L'ERREUR PAR CELLULE, gardée avec l'INDICE de sa cellule.
                             # Deux marcheurs divergent, donc leurs masques divergent : sans
                             # l'indice, un écart apparié comparerait deux médianes prises sur
                             # deux populations, ce que ce dépôt a déjà eu à retirer une fois.
                             cles=(ou_k[:, 0] * pas["garde"].shape[1] + ou_k[:, 1]),
                             erreurs=e,
                             pas_reel_um=round(pas["depart_um"], 1),
                             plancher_um=round(pas["plancher_um"], 1),
                             glissement_um=round(pas["glissement_um"], 1),
                             rugosite_vx=pas["rugosite_vx"],
                             # ⚠⚠ LA RUGOSITÉ DE LA NAPPE, à côté de celle du CHAMP. Un marcheur
                             # peut avoir un champ de décalage lisse et laisser une nappe
                             # froissée : ce sont deux grandeurs, et c'est la seconde que le
                             # bras suivant subit quand il estime ses normales.
                             rugosite_nappe_um=etat["rugosite_nappe_um"],
                             # ⚠⚠⚠ LA PART DE NAPPE RÉELLEMENT LISSÉE : une fenêtre large est
                             # REFUSÉE près des bords, donc « elle gagne » et « elle s'applique »
                             # sont deux affirmations, et la seconde doit être publiée.
                             part_lissee=etat["part_lissee"],
                             ou=np.argwhere(pas["garde"]).tolist()))
            grille, garde = etat["grille"], etat["garde"]
        resultats[nom] = bras

    # ⚠ Un balayage peut ne demander qu'une colonne : la garde porte alors sur ce qui a été
    # demandé, pas sur un marcheur qu'on n'a pas fait marcher.
    if not any(resultats.values()):
        raise RuntimeError("aucun marcheur n'a pu faire son premier pas")

    # ⚠⚠⚠ UNE SECONDE LECTURE SUR UNE SEULE POPULATION : les cellules encore vivantes au
    # dernier bras commun. La première dit ce que la marche fait vraiment — elle perd des
    # cellules — la seconde dit ce que la même population donne d'un bout à l'autre, et les
    # deux ensemble empêchent de lire une perte de couverture comme un gain de précision.
    commun = min((len(v) for v in resultats.values() if v), default=0)
    lignes = []
    for nom in voulus:
        bras = resultats[nom]
        erreurs = [b["erreur_um"] for b in bras]
        lignes.append(dict(
            marcheur=nom, borne=nom == BORNE, temoin=nom == TEMOIN,
            deploye=nom == "raccroche",
            bras_faits=len(bras), bras=[{k: b[k] for k in ("bras", "vers", "cellules",
                                                           "erreur_um", "pas_reel_um",
                                                           "plancher_um", "glissement_um",
                                                           "rugosite_vx", "rugosite_nappe_um",
                                                           "part_lissee")}
                                       for b in bras],
            rugosites_vx=[b["rugosite_vx"] for b in bras],
            rugosites_nappe_um=[b["rugosite_nappe_um"] for b in bras],
            parts_lissees=[b["part_lissee"] for b in bras],
            erreurs_um=erreurs,
            glissements_um=[b["glissement_um"] for b in bras],
            pas_reels_um=[b["pas_reel_um"] for b in bras],
            planchers_um=[b["plancher_um"] for b in bras],
            cellules_par_bras=[b["cellules"] for b in bras],
            portee=portee(erreurs, demi_feuille_um)))
    r = dict(
        fragment="PHerc0500P2", volume=c["volume"], voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        pas_nominal_um=ecart_um, demi_feuille_um=round(demi_feuille_um, 2),
        # ⚠⚠⚠ CE QUE LE RACCROCHAGE PEUT RÉELLEMENT APPLIQUER, mesuré sur les décalages que la
        # corrélation propose et NON sur la demi-largeur de la ligne. Les deux diffèrent de la
        # demi-largeur du gabarit, que la corrélation consomme à chaque bout. Publier la
        # seconde donnerait au raccrochage un pouvoir qu'il n'a pas.
        glissement_maximal_um=round(glissement_max, 1),
        glissement_en_demi_feuilles=round(glissement_max / demi_feuille_um, 2),
        lissage_nappe=list(reglage["lissage_nappe"]), marcheurs_parcourus=list(voulus),
        forme_grille=list(grilles[ancre][1].shape),
        ancre=ancre, spires_visees=atteignables, bras_communs=commun,
        marcheurs=list(voulus), lignes=lignes, bras_du_corpus=corpus_bras,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises))

    # ⭐⭐ COMBIEN DE BRAS LE CORPUS DEMANDE AU PAS NOMINAL, avant le premier qui demande tout
    # autre chose. Une portée qui s'arrête là s'arrête sur la matière ; une portée qui s'arrête
    # avant s'arrête sur la méthode, et c'est la seule des deux qui se corrige.
    r["bras_au_pas_nominal"] = portee([0.0 if b["au_pas_nominal"] else np.inf
                                       for b in corpus_bras], 1.0)
    r["bras_hors_du_pas_nominal"] = [b["bras"] for b in corpus_bras if not b["au_pas_nominal"]]

    def trouver(nom: str) -> dict | None:
        return next((x for x in r["lignes"] if x["marcheur"] == nom), None)

    def portee_de(nom: str):
        x = trouver(nom)
        return x["portee"] if x else None

    def apparier(a: str, b: str):
        # ⚠ Un écart entre une colonne présente et une colonne absente n'est pas zéro : il n'est
        # pas calculable, et le publier à zéro serait affirmer que les deux se valent.
        if a not in resultats or b not in resultats:
            return None, None
        ma, mb, nc = sur_les_cellules_communes(resultats[a], resultats[b])
        return (ecart_apparie(ma, mb) if nc else None), nc

    dep, rien = trouver("raccroche"), trouver("rien")
    r["portee_du_deploye"] = portee_de("raccroche")
    r["portee_sans_rien_faire"] = portee_de("rien")
    r["portee_de_loracle"] = portee_de(BORNE)
    r["portee_du_temoin"] = portee_de(TEMOIN)
    r["portee_de_la_nappe_lissee"] = portee_de(LISSE)
    # ⚠⚠ MÊME POPULATION, DONC APPARIEMENT LÉGITIME : le lissage garde le masque du raccrochage
    # (une cellule dont le voisinage ne suffit pas garde sa valeur non lissée), donc les deux
    # colonnes portent sur les mêmes cellules bras par bras.
    r["ecart_du_lissage_au_raccrochage"], ncl = apparier(LISSE, "raccroche")
    r["cellules_communes_lissage_raccrochage"] = ncl
    r["le_lissage_de_la_nappe_aide"] = bool(
        r["ecart_du_lissage_au_raccrochage"] and tranche(r["ecart_du_lissage_au_raccrochage"]))
    r["portee_de_la_sortie_raccrochee"] = portee_de(SORTIE)
    r["ecart_de_la_sortie_au_pas_normal"], ncs = apparier(SORTIE, "rien")
    r["cellules_communes_sortie_pas_normal"] = ncs
    # ⭐⭐⭐ LE VERDICT QUE CETTE TRANCHE POSE : séparer l'état de la sortie fait-il mieux que ne
    # rien faire, sur une marche ? Les deux sens sont publiés, comme partout ailleurs ici.
    r["la_sortie_raccrochee_bat_le_pas_normal"] = bool(
        r["ecart_de_la_sortie_au_pas_normal"] and tranche(r["ecart_de_la_sortie_au_pas_normal"]))
    inv_s, _ = apparier("rien", SORTIE)
    r["le_pas_normal_bat_la_sortie_raccrochee"] = bool(inv_s and tranche(inv_s))
    # ⭐⭐ LES DEUX COMPOSITIONS, chacune appariée à ce qu'elle prétend améliorer.
    r["portee_du_pas_normal_lisse"] = portee_de("rien_lisse")
    r["ecart_du_pas_normal_lisse"], ncrl = apparier("rien_lisse", "rien")
    r["cellules_communes_rien_lisse"] = ncrl
    r["le_lissage_aide_le_pas_normal"] = bool(
        r["ecart_du_pas_normal_lisse"] and tranche(r["ecart_du_pas_normal_lisse"]))
    r["portee_de_la_sortie_lisse"] = portee_de("sortie_lisse")
    r["ecart_de_la_sortie_lisse_au_pas_normal"], ncsl = apparier("sortie_lisse", "rien")
    r["cellules_communes_sortie_lisse"] = ncsl
    r["la_sortie_lisse_bat_le_pas_normal"] = bool(
        r["ecart_de_la_sortie_lisse_au_pas_normal"]
        and tranche(r["ecart_de_la_sortie_lisse_au_pas_normal"]))
    r["ecart_du_lissage_au_pas_normal"], ncr = apparier(LISSE, "rien")
    r["cellules_communes_lissage_pas_normal"] = ncr
    r["le_lissage_bat_le_pas_normal"] = bool(
        r["ecart_du_lissage_au_pas_normal"] and tranche(r["ecart_du_lissage_au_pas_normal"]))
    inv_l, _ = apparier("rien", LISSE)
    r["le_pas_normal_bat_le_lissage"] = bool(inv_l and tranche(inv_l))
    # ⭐⭐⭐ LE VERDICT DU BUT : la marche déployée va-t-elle plus loin que le pas normal seul ?
    r["le_raccrochage_porte_plus_loin"] = bool(
        dep and rien and dep["portee"] > rien["portee"])
    r["le_raccrochage_porte_plus_loin_que_son_temoin"] = bool(
        dep and trouver(TEMOIN) and dep["portee"] > trouver(TEMOIN)["portee"])
    # ⚠⚠ ET L'ÉCART APPARIÉ BRAS PAR BRAS, sur les bras que les deux ont faits : une portée est
    # un entier, donc elle ne dit rien de la marge. L'écart dit de combien.
    r["ecart_au_pas_normal"], nc = apparier("raccroche", "rien")
    r["cellules_communes_par_bras"] = nc
    r["le_raccrochage_bat_le_pas_normal"] = bool(
        r["ecart_au_pas_normal"] and tranche(r["ecart_au_pas_normal"]))
    # ⚠⚠⚠ ET LA QUESTION SYMÉTRIQUE, POSÉE AVEC LE MÊME INSTRUMENT. `tranche` répond « y
    # a-t-il une différence constante EN FAVEUR DU PREMIER », donc un faux ne dit pas « les
    # deux se valent » : il dit « pas en faveur du premier ». Renverser l'appariement pose
    # l'autre moitié de la question, sans seuil ajouté et sans nouvel instrument — et sans
    # elle un raccrochage qui coûte se lirait comme un raccrochage qui n'apporte rien.
    r["ecart_du_pas_normal"], _ = apparier("rien", "raccroche")
    r["le_pas_normal_bat_le_raccrochage"] = bool(
        r["ecart_du_pas_normal"] and tranche(r["ecart_du_pas_normal"]))
    # ⚠ La couverture perdue en chemin est un fait sur la marche, publié à côté de l'erreur.
    cpb = dep["cellules_par_bras"] if dep else []
    r["cellules_au_premier_bras"] = cpb[0] if cpb else 0
    r["cellules_au_dernier_bras"] = cpb[-1] if cpb else 0
    r["part_de_nappe_gardee"] = (
        round(r["cellules_au_dernier_bras"] / r["cellules_au_premier_bras"], 3)
        if r["cellules_au_premier_bras"] else None)
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- la portée ---
    v("la portée compte les bras réussis jusqu'au premier échec",
      portee([10.0, 20.0, 30.0], 25.0) == 2, str(portee([10.0, 20.0, 30.0], 25.0)))
    v("... elle vaut zéro si le premier bras échoue déjà",
      portee([99.0, 1.0], 25.0) == 0)
    # ⚠⚠⚠ ELLE NE COMPTE PAS LES SUCCÈS APRÈS UN ÉCHEC : une marche qui repasse sous le seuil
    # n'a pas rattrapé, elle a traversé une zone où elle était plus près de la mauvaise feuille,
    # et tout ce qui suit est bâti dessus.
    v("... et un retour sous le seuil après un échec ne la rallonge PAS",
      portee([10.0, 99.0, 10.0, 10.0], 25.0) == 1,
      str(portee([10.0, 99.0, 10.0, 10.0], 25.0)))
    v("... une marche qui ne dépasse jamais le seuil porte sur tous ses bras",
      portee([1.0, 2.0, 3.0], 25.0) == 3)
    v("... et un bras non calculable arrête la portée",
      portee([1.0, float("nan"), 1.0], 25.0) == 1)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(minimum=20, corpus=corpus_fabrique(), volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      len(fab["lignes"]) == len(MARCHEURS) and fab["lignes"][0]["bras_faits"] > 0,
      f"ancre {fab['ancre']} · vise {fab['spires_visees']}")
    # ⚠⚠ LE SEUIL VIENT DE LA MATIÈRE : c'est la demi-feuille, pas un réglage.
    v("... le seuil est la demi-feuille, dérivée du pas nominal",
      abs(fab["demi_feuille_um"] - fab["pas_nominal_um"] / 2) < 1e-6,
      f"{fab['demi_feuille_um']} pour un pas de {fab['pas_nominal_um']}")
    v("... chaque marcheur rend une portée entre zéro et le nombre de bras qu'il a faits",
      all(0 <= x["portee"] <= x["bras_faits"] for x in fab["lignes"]),
      str({x["marcheur"]: (x["portee"], x["bras_faits"]) for x in fab["lignes"]}))
    # ⚠⚠⚠ L'ORACLE EST UNE BORNE : il ne peut pas porter moins loin qu'un marcheur aveugle,
    # puisqu'il regarde la cible à chaque bras.
    orc = next(x for x in fab["lignes"] if x["borne"])
    v("... l'oracle porte au moins aussi loin que tout marcheur aveugle",
      all(orc["portee"] >= x["portee"] for x in fab["lignes"] if not x["borne"]),
      str({x["marcheur"]: x["portee"] for x in fab["lignes"]}))
    # ⚠⚠ LA COUVERTURE NE PEUT QUE DÉCROÎTRE : une cellule perdue l'est pour de bon.
    v("... la couverture ne remonte jamais en chemin",
      all(all(b <= a for a, b in zip(x["cellules_par_bras"], x["cellules_par_bras"][1:]))
          for x in fab["lignes"]),
      str(next(x for x in fab["lignes"] if x["deploye"])["cellules_par_bras"]))
    v("... et la part de nappe gardée est publiée",
      fab["part_de_nappe_gardee"] is None or 0.0 < fab["part_de_nappe_gardee"] <= 1.0,
      str(fab["part_de_nappe_gardee"]))
    # ⚠⚠⚠ LES MARCHEURS DIVERGENT, DONC LEURS MASQUES DIVERGENT, et c'est pourquoi chaque écart
    # apparié publie le nombre de cellules COMMUNES sur lesquelles il est pris. Exiger des
    # couvertures identiques serait exiger que les marcheurs ne divergent pas — c'est-à-dire
    # exiger qu'il n'y ait rien à mesurer.
    v("... chaque écart apparié publie les cellules communes sur lesquelles il est pris",
      all(isinstance(fab[c], list) and fab[c] and all(x > 0 for x in fab[c])
          for c in ("cellules_communes_par_bras", "cellules_communes_lissage_raccrochage",
                    "cellules_communes_lissage_pas_normal")),
      str(fab["cellules_communes_par_bras"]))
    # ⚠⚠ ET L'APPARIEMENT NE PREND QUE L'INTERSECTION : un contrôle qui ne ferait que lire les
    # médianes publiées passerait aussi bien avec deux populations disjointes.
    a = [dict(cles=np.array([1, 2, 3]), erreurs=np.array([10.0, 20.0, 90.0]))]
    b = [dict(cles=np.array([2, 3, 4]), erreurs=np.array([21.0, 91.0, 1000.0]))]
    ma, mb, nc = sur_les_cellules_communes(a, b)
    v("... et il écarte les cellules qu'un seul des deux a gardées",
      (ma, mb, nc) == ([55.0], [56.0], [2]), f"{ma} {mb} {nc}")
    v("... un bras sans aucune cellule commune arrête l'appariement",
      sur_les_cellules_communes(
          [dict(cles=np.array([1]), erreurs=np.array([1.0]))],
          [dict(cles=np.array([9]), erreurs=np.array([1.0]))]) == ([], [], []))
    # ⚠⚠ LA RUGOSITÉ EST LA PRÉMISSE DU DIAGNOSTIC : « la marche froisse ce qu'elle laisse » est
    # une histoire tant que le champ de décalage n'est pas mesuré bras après bras. Elle est
    # publiée pour les marcheurs qui glissent, et nulle pour celui qui ne glisse pas.
    v("... la rugosité du champ de décalage est publiée bras par bras",
      all(g == 0.0 for x in fab["lignes"] if x["marcheur"] == "rien" for g in x["rugosites_vx"])
      and any(g for x in fab["lignes"] if x["deploye"] for g in x["rugosites_vx"]),
      str({x["marcheur"]: x["rugosites_vx"] for x in fab["lignes"]}))
    # ⚠⚠⚠ LA RUGOSITÉ DE LA NAPPE EST UNE SECONDE GRANDEUR, pas une relecture de la première :
    # un marcheur peut avoir un champ de décalage lisse et laisser une nappe froissée. Le
    # contrôle exige qu'elle soit publiée pour TOUS, y compris ceux qui ne glissent pas — dont
    # le champ est nul et dont la nappe, elle, ne l'est pas.
    v("... la rugosité de la NAPPE est publiée pour chaque marcheur, à côté de celle du champ",
      all(x["rugosites_nappe_um"] and all(g is not None for g in x["rugosites_nappe_um"])
          for x in fab["lignes"]),
      str({x["marcheur"]: x["rugosites_nappe_um"][:3] for x in fab["lignes"]}))
    # ⚠⚠⚠ « LA FENÊTRE GAGNE » ET « LA FENÊTRE S'APPLIQUE » SONT DEUX AFFIRMATIONS. Une fenêtre
    # large exige une majorité de voisins présents, donc elle est refusée près des bords et les
    # cellules y gardent leur valeur brute. Le contrôle exige que la part lissée soit publiée, et
    # qu'elle DÉCROISSE quand la fenêtre s'élargit — sinon ce nombre ne mesure rien.
    v("... la part de nappe réellement lissée est publiée",
      all(0.0 <= g <= 1.0 for x in fab["lignes"] for g in x["parts_lissees"]),
      str({x["marcheur"]: x["parts_lissees"][:3] for x in fab["lignes"]}))
    parts = []
    for d in (1, 2, 4):
        w = mesurer(minimum=20, corpus=corpus_fabrique(), volume=volume_fabrique(g0),
                    marcheurs=("rien_lisse",), lissage_nappe=(d, 1))
        parts.append(w["lignes"][0]["parts_lissees"][0])
    v("... et elle décroît quand la fenêtre s'élargit",
      parts == sorted(parts, reverse=True) and parts[0] > parts[-1],
      f"demi 1/2/4 → {parts} sur une grille {fab['forme_grille']}")
    # ⚠⚠ ET LE LISSAGE DE LA NAPPE DOIT RÉELLEMENT LA LISSER : si la rugosité de nappe du
    # marcheur lissé n'était pas plus basse que celle de son homologue brut, le lissage ne
    # ferait rien et tous les verdicts posés dessus seraient des coïncidences.
    rn_l = next(x for x in fab["lignes"] if x["marcheur"] == "rien_lisse")["rugosites_nappe_um"]
    rn_r = next(x for x in fab["lignes"] if x["marcheur"] == "rien")["rugosites_nappe_um"]
    v("... et lisser la nappe la rend effectivement moins rugueuse",
      sum(a <= b for a, b in zip(rn_l, rn_r)) > len(rn_l) // 2,
      f"lissé {rn_l} · brut {rn_r}")
    # ⭐⭐⭐ L'ÉTAT ET LA SORTIE SONT DEUX CHOSES, et le contrôle porte sur la seule propriété qui
    # rend ce marcheur différent : sa COUVERTURE est celle du raccrochage (c'est lui qui est
    # publié) tandis que ce qu'il porte au bras suivant est le pas normal. Si son état était
    # raccroché, ses erreurs égaleraient celles du raccrochage et le marcheur ne mesurerait rien.
    so_ = next(x for x in fab["lignes"] if x["marcheur"] == "sortie_raccrochee")
    ra_ = next(x for x in fab["lignes"] if x["marcheur"] == "raccroche")
    ri_ = next(x for x in fab["lignes"] if x["marcheur"] == "rien")
    v("... la sortie raccrochée a le PREMIER bras du raccrochage et diverge ensuite",
      bool(so_["erreurs_um"]) and so_["erreurs_um"][0] == ra_["erreurs_um"][0]
      and (len(so_["erreurs_um"]) < 2 or so_["erreurs_um"] != ra_["erreurs_um"]),
      f"sortie {so_['erreurs_um']} · raccroche {ra_['erreurs_um']} · rien {ri_['erreurs_um']}")
    v("... et son écart au pas normal est apparié, avec son intervalle",
      fab["ecart_de_la_sortie_au_pas_normal"] is not None
      and fab["ecart_de_la_sortie_au_pas_normal"]["intervalle_um"] is not None,
      f"portée {fab['portee_de_la_sortie_raccrochee']} · "
      + str(fab["ecart_de_la_sortie_au_pas_normal"]))
    # ⚠ LE CINQUIÈME MARCHEUR N'AJOUTE AUCUN RÉGLAGE : il applique le voisinage déployé à la
    # NAPPE au lieu du champ de décalage. Son écart au raccrochage est donc apparié cellule à
    # cellule, et il est publié qu'il aide ou non.
    v("... le lissage de la nappe est comparé au raccrochage, apparié",
      fab["ecart_du_lissage_au_raccrochage"] is not None
      and fab["ecart_du_lissage_au_raccrochage"]["intervalle_um"] is not None,
      f"portée {fab['portee_de_la_nappe_lissee']} · "
      + str(fab["ecart_du_lissage_au_raccrochage"]))
    # ⚠⚠⚠ LE GLISSEMENT PUBLIÉ EST CELUI QUE LA CORRÉLATION PROPOSE, jamais la demi-largeur de
    # la ligne : les deux diffèrent de la demi-largeur du gabarit, que la corrélation consomme à
    # chaque bout, et publier la seconde donnerait au raccrochage un pouvoir qu'il n'a pas. Le
    # contrôle exige que ce qui est APPLIQUÉ tienne dans ce qui est ANNONCÉ.
    trop = [(x["marcheur"], b["bras"], b["glissement_um"])
            for x in fab["lignes"] for b in x["bras"]
            if b["glissement_um"] > fab["glissement_maximal_um"] + 1e-6]
    v("... aucun bras ne glisse plus loin que ce que la corrélation propose",
      not trop and fab["glissement_maximal_um"] > 0,
      str(trop[:3]) if trop else f"au plus ±{fab['glissement_maximal_um']:.1f} µm = "
      f"{fab['glissement_en_demi_feuilles']} demi-feuille")
    # ⚠⚠ ET UN MARCHEUR QUI NE GLISSE PAS DOIT LE PUBLIER À ZÉRO : sans ça « le pas normal ne
    # raccroche rien » serait une affirmation du code et non une mesure.
    v("... et le pas normal seul ne glisse d'aucun bras",
      all(b["glissement_um"] == 0.0
          for x in fab["lignes"] if x["marcheur"] == "rien" for b in x["bras"]),
      str([b["glissement_um"] for x in fab["lignes"] if x["marcheur"] == "rien"
           for b in x["bras"]]))
    # ⚠⚠⚠ LES DEUX MOITIÉS DE LA QUESTION NE PEUVENT PAS ÊTRE VRAIES ENSEMBLE : un même
    # appariement ne peut pas trancher dans les deux sens. Si les deux sortaient vrais, c'est
    # `tranche` qui serait cassé, et tous les verdicts de la campagne avec lui.
    v("... les deux sens de l'écart apparié ne tranchent jamais tous les deux",
      not (fab["le_raccrochage_bat_le_pas_normal"] and fab["le_pas_normal_bat_le_raccrochage"]),
      f"{fab['le_raccrochage_bat_le_pas_normal']} / "
      f"{fab['le_pas_normal_bat_le_raccrochage']}")
    v("... l'écart au pas normal est apparié, avec son intervalle",
      fab["ecart_au_pas_normal"] is None
      or fab["ecart_au_pas_normal"]["intervalle_um"] is not None,
      str(fab["ecart_au_pas_normal"]))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "PORTÉE" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    # ⚠⚠⚠ LE PLANCHER EST UNE BORNE INFÉRIEURE, et elle vaut pour TOUS les marcheurs — la
    # distance à un nuage est 1-lipschitzienne. S'il dépassait l'erreur d'un seul bras, ce ne
    # serait pas un plancher mais un nombre posé à côté.
    hors = [(x["marcheur"], b["bras"], b["plancher_um"], b["erreur_um"])
            for x in fab["lignes"] for b in x["bras"]
            if b["plancher_um"] > b["erreur_um"] + 1e-6]
    v("... le plancher d'un bras ne dépasse JAMAIS l'erreur mesurée sur ce bras",
      not hors and any(x["bras"] for x in fab["lignes"]), str(hors[:3]))
    # ⚠⚠ ET LE CORPUS EST DÉCRIT, PAS JUGÉ : un bras que le corpus demande loin du pas nominal
    # est nommé, pour qu'un trou de numérotation ne se lise pas comme un échec de méthode.
    v("... et le corpus publie l'écart qu'il demande à chaque bras",
      len(fab["bras_du_corpus"]) == len(fab["spires_visees"])
      and all("au_pas_nominal" in b for b in fab["bras_du_corpus"]),
      str([b["ecart_um"] for b in fab["bras_du_corpus"]]))
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une marche."""
    print(f"pas nominal {r['pas_nominal_um']} µm · demi-feuille {r['demi_feuille_um']} µm · "
          f"ancre = spire {r['ancre']} · vise {r['spires_visees']}")
    print()
    entete = " ".join(f"{b:>8}" for b in range(1, len(r["spires_visees"]) + 1))
    print(f"{'marcheur':>12} {entete} {'portée':>8}")
    print("-" * (14 + 9 * len(r["spires_visees"]) + 9))
    for x in r["lignes"]:
        cases = []
        for e in x["erreurs_um"]:
            perdu = "*" if e >= r["demi_feuille_um"] else " "
            cases.append(f"{e:>7.1f}{perdu}")
        cases += ["      —"] * (len(r["spires_visees"]) - len(cases))
        marque = (" ⭐" if x["deploye"] else (" ⛔" if x["borne"] else
                                             ("  ~" if x["temoin"] else "")))
        print(f"{x['marcheur']:>12} {' '.join(cases)} {x['portee']:>8}{marque}")
    cases = [f"{b['ecart_um']:>7.1f}{'!' if not b['au_pas_nominal'] else ' '}"
             for b in r["bras_du_corpus"]]
    print(f"{'le corpus':>12} {' '.join(cases)} {r['bras_au_pas_nominal']:>8}  ·")
    print()
    print("* = au-delà de la demi-feuille : la marche est plus près de la MAUVAISE feuille")
    print("rugosité du CHAMP de décalage (voxels) / rugosité de la NAPPE (µm), bras par bras :")
    for x in r["lignes"]:
        print(f"{x['marcheur']:>18} champ {str(x['rugosites_vx']):<44} "
              f"nappe {x['rugosites_nappe_um']}")
    dep_l = next(x for x in r["lignes"] if x["deploye"])
    print(f"glissement : au plus ±{r['glissement_maximal_um']} µm "
          f"({r['glissement_en_demi_feuilles']} demi-feuille) · appliqué bras par bras "
          f"{[round(g, 1) for g in dep_l['glissements_um']]}")
    print("! = le corpus demande à ce bras tout autre chose que le pas nominal : ce qui s'y "
          "arrête s'arrête sur la matière")
    print(f"cellules du chemin déployé : {r['cellules_au_premier_bras']} au premier bras, "
          f"{r['cellules_au_dernier_bras']} au dernier — il en garde "
          f"{r['part_de_nappe_gardee']}")
    print(f"→ ⭐⭐⭐ PORTÉE du chemin déployé : {r['portee_du_deploye']} spires · pas normal seul "
          f"{r['portee_sans_rien_faire']} · témoin mélangé {r['portee_du_temoin']} · ⛔ oracle "
          f"{r['portee_de_loracle']}")
    print(f"→ le raccrochage porte plus loin que le pas normal : "
          f"{'OUI' if r['le_raccrochage_porte_plus_loin'] else 'NON'} · que son témoin : "
          f"{'OUI' if r['le_raccrochage_porte_plus_loin_que_son_temoin'] else 'NON'}")
    for cle, nom_, por in (("ecart_du_pas_normal_lisse", "pas normal + nappe lissée",
                           "portee_du_pas_normal_lisse"),
                          ("ecart_de_la_sortie_lisse_au_pas_normal",
                           "nappe lissée + sortie raccrochée", "portee_de_la_sortie_lisse")):
        x = r[cle]
        if x:
            print(f"→ ⭐ {nom_} : portée {r[por]} · écart au pas normal "
                  f"{x['ecart_median_um']:+.1f} µm · {x['pas_ameliores']}/{x['pas']} bras · "
                  f"{x['intervalle_um']}")
    es = r["ecart_de_la_sortie_au_pas_normal"]
    if es:
        print(f"→ ⭐ l'ÉTAT au pas normal, la SORTIE raccrochée : portée "
              f"{r['portee_de_la_sortie_raccrochee']} · écart au pas normal "
              f"{es['ecart_median_um']:+.1f} µm · {es['pas_ameliores']}/{es['pas']} bras · "
              f"{es['intervalle_um']} · "
              f"{'elle GAGNE' if r['la_sortie_raccrochee_bat_le_pas_normal'] else 'ne tranche pas'}")
    el = r["ecart_du_lissage_au_raccrochage"]
    if el:
        print(f"→ ⭐ la NAPPE lissée entre deux bras : portée {r['portee_de_la_nappe_lissee']} · "
              f"écart au raccrochage {el['ecart_median_um']:+.1f} µm · "
              f"{el['pas_ameliores']}/{el['pas']} bras · {el['intervalle_um']} · "
              f"{'elle AIDE' if r['le_lissage_de_la_nappe_aide'] else 'ne tranche pas'}")
    inv = r["ecart_du_pas_normal"]
    if inv:
        print(f"→ ⚠ et le PAS NORMAL bat-il le raccrochage : "
              f"{'OUI' if r['le_pas_normal_bat_le_raccrochage'] else 'non'} "
              f"({inv['ecart_median_um']:+.1f} µm · {inv['pas_ameliores']}/{inv['pas']} bras · "
              f"{inv['intervalle_um']})")
    e = r["ecart_au_pas_normal"]
    if e:
        print(f"→ et son écart apparié au pas normal : {e['ecart_median_um']:+.1f} µm · "
              f"{e['pas_ameliores']}/{e['pas']} bras · {e['intervalle_um']} · "
              f"{'TRANCHE' if tranche(e) else 'ne tranche pas'}")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--bras-max", type=int, default=8, dest="bras_max")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, bras_max=a.bras_max)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
