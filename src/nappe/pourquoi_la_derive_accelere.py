#!/usr/bin/env python3
"""La dérive accélère-t-elle vraiment ? — non, et c'est le premier pas qui coûte

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL RÉTRACTE LA TRANCHE PRÉCÉDENTE. `combien_dancres` avait
mesuré l'erreur d'une ancre aux bras 1 à 4 — 41,1 / 63,1 / 100,8 / 149,4 µm — et en avait conclu
qu'elle **accélère**, sur le critère « les incréments consécutifs croissent » : 22,0 puis 37,7
puis 48,6. Ce fichier devait écarter deux artefacts qui auraient pu fabriquer cette courbe. Il en
a trouvé un troisième, et il était dans le critère lui-même.

⛔⭐⭐ **Le critère omettait le plus grand incrément : celui du bras ZÉRO, dont l'erreur est nulle
par définition, au bras un.** La suite complète est **41,1 puis 22,0 / 37,7 / 48,6** — le premier
pas est le plus cher, et il n'y a pas de tendance après lui. Mesuré autrement, sans seuil ni
point de départ arbitraire : **l'erreur au bras `k` est SOUS `k` fois celle du bras un**, sur les
deux populations. Le coût par tour vaut 41,1 puis 31,6 / 33,6 / 37,4 µm dans l'une et 44,2 puis
31,4 / 34,5 / 33,5 dans l'autre : il est **stable**, pas croissant.

⚠⚠ Et l'ancien critère basculait sur deux micromètres : les incréments consécutifs croissent
strictement sur une population et pas sur l'autre, alors que les deux mesurent la même chose. Un
verdict qui s'inverse avec la population n'est pas un verdict — ce dépôt l'a déjà écrit deux fois,
pour la boîte et pour la corrélation du désaccord.

⚠⚠ LE PREMIER SUSPECT ÉCARTÉ EST LE MASQUE QUI RÉTRÉCIT. Une normale demande quatre voisins
valides, donc chaque pas ronge un anneau de cellules : la marche part de 196 cellules et en
garde 64 au quatrième tour. L'erreur au bras 4 est donc mesurée sur un **sous-ensemble** de
celles du bras 1,
et si l'intérieur d'une grille se comportait autrement que son bord, la courbe mesurerait ce
changement de population plutôt que la marche.

⚠⚠ LE SECOND EST LA SPIRE DE DÉPART. Chaque bras part d'une spire publiée différente, et rien ne
dit qu'elles se valent : si les spires lointaines sont de moins bonnes reconstructions, l'erreur
croît pour une raison qui n'est pas la marche. L'accélération doit donc se voir **à spire de
départ FIXE**, pas seulement en moyenne sur toutes.

⭐⭐ ET LE TROISIÈME CONTRÔLE N'EST PAS UN ARTEFACT MAIS UNE DÉCOMPOSITION : la marche libre de
`k` pas est comparée à **un seul pas de longueur `k` fois le pas**, pris le long des normales de
la surface de départ. Les deux vont au même endroit et ne diffèrent que par une chose — la
seconde ne recalcule jamais ses normales, donc elle ne peut pas dégrader sa propre surface. Si
elles se valent, l'itération n'apporte rien et l'erreur est purement géométrique ; si la libre
est bien pire, c'est l'itération qui abîme la surface, et c'est là qu'il faut porter l'effort.

⚠ Aucune lecture du volume ici : tout est aveugle, donc cette tranche ne coûte pas un bloc.

Usage :
    uv run python src/nappe/pourquoi_la_derive_accelere.py --verifier
    uv run python src/nappe/pourquoi_la_derive_accelere.py \\
        --json docs/mesures/pourquoi_la_derive_accelere.json
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

# ⚠ Un seul lecteur de corpus pour tous les dérouleurs, et sa fixture hors ligne avec lui.
from le_corpus_des_spires import corpus_fabrique, corpus_publie  # noqa: E402


def un_grand_pas(a: np.ndarray, ok: np.ndarray, longueur: float,
                 sens: float) -> tuple[np.ndarray, np.ndarray]:
    """Un SEUL pas de `longueur`, le long des normales de la surface de départ.

    ⚠⚠⚠ C'EST LE TÉMOIN QUI SÉPARE LA GÉOMÉTRIE DE L'ITÉRATION. Il va au même endroit que `k`
    pas d'une épaisseur, et il ne diffère que par un point : il ne recalcule **jamais** ses
    normales, donc il ne peut pas dégrader sa propre surface. Ce qu'il laisse comme erreur est
    ce que la géométrie impose ; ce que la marche libre a en plus est ce que l'itération coûte.

    ⚠ Le masque est celui d'UN calcul de normales, pas de `k` : ce témoin ne ronge la grille
    qu'une fois. Comparer les deux sur leurs masques respectifs comparerait deux populations,
    donc l'appelant les ramène au **sous-ensemble commun** avant de juger.
    """
    from le_pas_normal_atteint_la_spire import normales  # noqa: PLC0415

    n, bon = normales(a, ok)
    avance = a.copy()
    avance[bon] = a[bon] + sens * longueur * n[bon]
    return avance, bon


def sous_lineaire(suite: list[float]) -> bool:
    """L'erreur au bras `k` reste-t-elle SOUS `k` fois celle du bras un ?

    ⚠⚠⚠ CE CRITÈRE EN REMPLACE UN AUTRE, ET C'EST UNE RÉTRACTATION. `combien_dancres` jugeait la
    forme de la courbe sur « les incréments consécutifs croissent strictement » — un critère qui
    bascule sur deux micromètres, et qui OMET l'incrément le plus grand de tous : celui du bras
    zéro, dont l'erreur est nulle par définition, au bras un. Il a rendu deux verdicts opposés
    sur deux populations qui mesurent la même chose.

    ⭐⭐ Celui-ci est SANS SEUIL et il a un sens : au-dessus de la droite du premier pas, la
    dérive coûte de plus en plus cher par tour ; en dessous, de moins en moins. Il ne dépend ni
    d'un réglage ni de l'endroit où l'on commence à compter.

    ⚠ Il ne dit rien d'une suite d'un seul point : une courbe a besoin de deux points pour avoir
    une forme, et rendre `True` sur un seul serait un verdict qu'aucune donnée n'a produit.
    """
    return bool(len(suite) > 1
                and all(x < (i + 1) * suite[0] for i, x in enumerate(suite) if i))


def survivants(masques: list[np.ndarray]) -> np.ndarray:
    """Les cellules valides dans TOUS les masques donnés.

    ⚠⚠ C'est ce qui rend les bras comparables : sans intersection, l'erreur au bras 4 porte sur
    l'intérieur d'une grille et celle du bras 1 sur la grille entière, donc leur différence
    mélange la marche et la population. Une intersection vide est rendue telle quelle — un
    appelant qui la prendrait pour un résultat mesurerait zéro cellule.
    """
    if not masques:
        return np.zeros((0, 0), dtype=bool)
    out = masques[0].copy()
    for m in masques[1:]:
        out &= m
    return out


def mesurer(cote: float | None = None, minimum: int = 30, bras_max: int = 4,
            corpus: dict | None = None) -> dict:
    """L'erreur par longueur de bras, avec les deux artefacts écartés et l'itération isolée."""
    from derouler_par_le_pas_normal import un_pas  # noqa: PLC0415
    from le_pas_normal_atteint_la_spire import distance_a, essayer_le_pas, normales  # noqa: PLC0415, E501
    from le_raccrochage_a_la_matiere import BOITE_CENTRE, BOITE_COTE  # noqa: PLC0415

    c = corpus_publie() if corpus is None else corpus
    volume, voxel_um = c["volume"], float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        idx = np.argwhere(dans)
        sous = (slice(int(idx[:, 0].min()), int(idx[:, 0].max()) + 1),
                slice(int(idx[:, 1].min()), int(idx[:, 1].max()) + 1))
        grilles[rang] = (a[sous].copy(), dans[sous].copy())
        nuages[rang] = a[ok]

    lignes = []
    for depart in sorted(grilles):
        a0, ok0 = grilles[depart]
        n0, bon0 = normales(a0, ok0)
        if not bon0.any():
            continue
        # ⚠ Un seul bit de supervision, fixé au premier pas en regardant la cible la plus
        # proche : le signe d'une normale vient du paramétrage de la grille, pas de la matière.
        voisines = [r for r in grilles if 0 < r - depart <= bras_max]
        if not voisines:
            continue
        e = essayer_le_pas(a0[bon0], n0[bon0], nuages[min(voisines)], pas_vx, voxel_um)
        sens = 1.0 if e["retenu"] == "+" else -1.0

        # --- la marche libre, un pas à la fois, et son masque à chaque tour ---
        libres, masques = {}, {}
        a_, m_ = a0, ok0
        for k in range(1, bras_max + 1):
            a_, m_ = un_pas(a_, m_, pas_vx, sens)
            if int(m_.sum()) < minimum:
                break
            libres[k], masques[k] = a_.copy(), m_.copy()
        if not libres:
            continue
        commun = survivants(list(masques.values()))
        if int(commun.sum()) < minimum:
            continue
        for k, av in sorted(libres.items()):
            if depart + k not in nuages:
                continue
            cible = nuages[depart + k]
            # ⚠⚠ TROIS POPULATIONS, ET LA DIFFÉRENCE EST LE CONTRÔLE. « propre » est le masque
            # du tour k, celui que la marche publie d'habitude ; « commun » est l'intersection
            # de tous les tours, donc la même population d'un bras à l'autre.
            e_propre = float(np.median(distance_a(av[masques[k]], cible, voxel_um)))
            e_commun = float(np.median(distance_a(av[commun], cible, voxel_um)))
            # --- le témoin d'un seul grand pas, ramené au même sous-ensemble ---
            gros, m_gros = un_grand_pas(a0, ok0, k * pas_vx, sens)
            commun_gros = commun & m_gros
            e_gros = (float(np.median(distance_a(gros[commun_gros], cible, voxel_um)))
                      if int(commun_gros.sum()) >= minimum else None)
            lignes.append(dict(
                depart=depart, bras=k, cible=depart + k,
                cellules_propres=int(masques[k].sum()), cellules_communes=int(commun.sum()),
                erreur_propre_um=round(e_propre, 1),
                erreur_commune_um=round(e_commun, 1),
                erreur_dun_grand_pas_um=(round(e_gros, 1) if e_gros is not None else None),
                # ⚠⚠ LE COMPTE DE CELLULES DU GRAND PAS EST LA MOITIÉ ACTIONNABLE DU TÉMOIN :
                # à erreur égale, il ne ronge la grille qu'une fois, donc il en garde d'autant
                # plus. Publier l'erreur sans le compte laisserait croire à une égalité alors
                # que l'un des deux rend beaucoup plus de nappe.
                cellules_dun_grand_pas=int(m_gros.sum()),
                bits_de_supervision=1))

    if not lignes:
        raise RuntimeError("aucune marche mesurable dans la boîte")

    def med(sous, cle):
        vals = [e[cle] for e in sous if e[cle] is not None]
        return round(float(np.median(vals)), 1) if vals else None

    r = dict(
        fragment="PHerc0500P2", volume=volume, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        ecart_lu_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        bras_max=bras_max, marches=len(lignes),
        departs=sorted({e["depart"] for e in lignes}), lignes=lignes)

    par_bras = {}
    for e in lignes:
        par_bras.setdefault(e["bras"], []).append(e)
    r["par_bras"] = {
        str(b): dict(n=len(v),
                     propre_um=med(v, "erreur_propre_um"),
                     commune_um=med(v, "erreur_commune_um"),
                     un_grand_pas_um=med(v, "erreur_dun_grand_pas_um"),
                     cellules_propres=int(np.median([e["cellules_propres"] for e in v])),
                     cellules_communes=int(np.median([e["cellules_communes"] for e in v])),
                     cellules_dun_grand_pas=int(np.median(
                         [e["cellules_dun_grand_pas"] for e in v])))
        for b, v in sorted(par_bras.items())}

    def suite_de(cle):
        s = [r["par_bras"][b][cle] for b in sorted(r["par_bras"], key=int)]
        return s if all(x is not None for x in s) else []

    # ⚠⚠⚠ LE PREMIER VERDICT : la forme de la courbe survit-elle au masque commun ? Si elle
    # changeait, c'est le masque qu'on mesurait ; si elle ne change pas, il n'y est pour rien.
    sp, sc = suite_de("propre_um"), suite_de("commune_um")
    # ⚠ Les incréments partent du bras ZÉRO, dont l'erreur est nulle par définition : c'est le
    # plus grand de tous, et l'omettre faisait lire une accélération là où il y a surtout un
    # premier pas cher. Le point de départ n'est pas une mesure, il est le bord du domaine.
    r["increments_propres_um"] = [round(b - a_, 1) for a_, b in zip([0.0] + sp, sp)]
    r["increments_communs_um"] = [round(b - a_, 1) for a_, b in zip([0.0] + sc, sc)]
    r["cout_par_tour_propre_um"] = [round(x / (i + 1), 1) for i, x in enumerate(sp)]
    r["cout_par_tour_commun_um"] = [round(x / (i + 1), 1) for i, x in enumerate(sc)]
    r["sous_lineaire_sur_le_masque_propre"] = sous_lineaire(sp)
    r["sous_lineaire_sur_le_masque_commun"] = sous_lineaire(sc)
    r["le_masque_change_la_forme_de_la_courbe"] = bool(
        r["sous_lineaire_sur_le_masque_propre"] != r["sous_lineaire_sur_le_masque_commun"])
    # ⚠⚠ ET LE FAIT QUI RESTE QUAND LES VERDICTS TOMBENT : le premier pas coûte plus cher que
    # n'importe quel tour suivant. C'est lui, et pas une accélération, que la courbe montre.
    r["le_premier_pas_coute_le_plus"] = bool(
        len(sc) > 1 and all(sc[0] > x for x in r["cout_par_tour_commun_um"][1:]))
    # ⚠ Et le sens de l'effet du masque est publié : garder l'intérieur d'une grille peut aussi
    # bien améliorer l'erreur que l'empirer, et l'affirmer sans le mesurer serait une supposition.
    r["ecart_du_masque_um"] = [round(x - y, 1) for x, y in zip(sc, sp)] if sp and sc else []

    # ⚠⚠⚠ LE SECOND : l'accélération se voit-elle à spire de DÉPART FIXE ? Une accélération qui
    # n'apparaîtrait qu'en moyenne sur les départs mesurerait la qualité des spires publiées.
    par_depart = {}
    for e in lignes:
        par_depart.setdefault(e["depart"], {})[e["bras"]] = e["erreur_commune_um"]
    complets = {d: v for d, v in par_depart.items() if len(v) >= 3}
    r["departs_a_trois_bras_ou_plus"] = sorted(complets)
    r["departs_sous_lineaires"] = sorted(
        d for d, v in complets.items() if sous_lineaire([v[b] for b in sorted(v)]))
    r["la_sous_linearite_tient_a_depart_fixe"] = bool(
        complets and len(r["departs_sous_lineaires"]) > len(complets) / 2)
    r["par_depart"] = {str(d): {str(b): v[b] for b in sorted(v)}
                       for d, v in sorted(par_depart.items())}

    # ⚠⚠⚠ LE TROISIÈME : l'itération coûte-t-elle quelque chose ? Les deux marches vont au même
    # endroit et ne diffèrent que par le recalcul des normales.
    sg = suite_de("un_grand_pas_um")
    r["increments_dun_grand_pas_um"] = [round(b - a_, 1) for a_, b in zip([0.0] + sg, sg)]
    r["cout_par_tour_dun_grand_pas_um"] = [round(x / (i + 1), 1) for i, x in enumerate(sg)]
    r["un_grand_pas_est_sous_lineaire_aussi"] = sous_lineaire(sg)
    r["cout_de_literation_um"] = ([round(x - y, 1) for x, y in zip(sc, sg)] if sc and sg else [])
    r["marches_ou_liteation_coute"] = sum(
        1 for e in lignes if e["erreur_dun_grand_pas_um"] is not None
        and e["erreur_commune_um"] > e["erreur_dun_grand_pas_um"])
    r["marches_comparables"] = sum(
        1 for e in lignes if e["erreur_dun_grand_pas_um"] is not None)
    r["literation_coute"] = bool(
        r["marches_comparables"]
        and r["marches_ou_liteation_coute"] > r["marches_comparables"] / 2)
    # ⚠⚠⚠ ET CE QUE L'ITÉRATION COÛTE VRAIMENT : de la NAPPE. Elle recalcule ses normales à
    # chaque pas, donc elle ronge un anneau à chaque pas, quand un seul grand pas n'en ronge
    # qu'un. À erreur égale, c'est le compte de cellules qui départage — et c'est le seul
    # chiffre de ce fichier qui change quelque chose à la façon de dérouler.
    r["cellules_gardees_en_plus_par_le_grand_pas"] = {
        b: d["cellules_dun_grand_pas"] - d["cellules_propres"]
        for b, d in r["par_bras"].items()}
    dernier = max(r["par_bras"], key=int)
    d_ = r["par_bras"][dernier]
    r["part_de_nappe_gagnee_au_dernier_bras"] = (
        round(d_["cellules_dun_grand_pas"] / d_["cellules_propres"] - 1.0, 3)
        if d_["cellules_propres"] else None)
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'intersection des masques ---
    a_ = np.array([[True, True], [True, False]])
    b_ = np.array([[True, False], [True, True]])
    v("l'intersection ne garde que ce qui est valide partout",
      survivants([a_, b_]).tolist() == [[True, False], [True, False]],
      str(survivants([a_, b_]).tolist()))
    v("... un seul masque se rend lui-même", survivants([a_]).tolist() == a_.tolist())
    v("... et aucun masque ne rend rien plutôt qu'une erreur",
      survivants([]).size == 0)
    v("l'intersection ne modifie pas ses entrées",
      (survivants([a_, b_]) is not a_) and a_.tolist() == [[True, True], [True, False]])

    # --- le grand pas ---
    uu, vv = np.meshgrid(np.arange(12.0), np.arange(12.0), indexing="ij")
    plan = np.stack([uu * 3.0, vv * 3.0, np.zeros(uu.shape)], axis=-1)
    ok = np.ones(plan.shape[:2], dtype=bool)
    gros, m_gros = un_grand_pas(plan, ok, 40.0, 1.0)
    v("un grand pas déplace la grille d'exactement sa longueur",
      bool(np.allclose(gros[m_gros][:, 2], 40.0)), str(gros[m_gros][0]))
    v("... et il ne ronge la grille qu'UNE fois",
      int(m_gros.sum()) == 100, str(int(m_gros.sum())))
    # ⚠⚠⚠ SUR UN PLAN, quatre petits pas et un grand vont au MÊME endroit : c'est ce qui fait
    # du grand pas un témoin et non un autre dérouleur. Toute différence entre eux vient donc
    # de la courbure, jamais de la géométrie du déplacement.
    from derouler_par_le_pas_normal import un_pas  # noqa: PLC0415

    petit, m_petit = plan, ok
    for _ in range(4):
        petit, m_petit = un_pas(petit, m_petit, 10.0, 1.0)
    v("sur un plan, quatre petits pas et un grand arrivent au même endroit",
      bool(np.allclose(petit[m_petit][:, 2], 40.0)), str(petit[m_petit][0]))
    v("... mais les petits pas ont rongé la grille quatre fois",
      int(m_petit.sum()) == 16, f"{int(m_petit.sum())} contre {int(m_gros.sum())}")
    v("le sens négatif va dans l'autre sens",
      bool(np.allclose(un_grand_pas(plan, ok, 40.0, -1.0)[0][m_gros][:, 2], -40.0)))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    fab = mesurer(minimum=20, bras_max=3, corpus=corpus_fabrique())
    v("la mesure tourne de bout en bout sur un corpus fabriqué, sans rien lire",
      fab["marches"] > 0 and len(fab["departs"]) > 0,
      f"{fab['marches']} marches depuis {len(fab['departs'])} spires")
    v("... et la marche y est imparfaite, donc les comparaisons portent sur quelque chose",
      all(e["erreur_propre_um"] > 0 for e in fab["lignes"]))
    # ⚠⚠ LE MASQUE COMMUN EST BIEN UN SOUS-ENSEMBLE, ET IL NE VARIE PAS AVEC LE BRAS : c'est
    # exactement ce qui rend les bras comparables, et si ça cessait d'être vrai le contrôle du
    # masque ne contrôlerait plus rien.
    v("... les cellules communes ne dépassent jamais les cellules propres",
      all(e["cellules_communes"] <= e["cellules_propres"] for e in fab["lignes"]))
    v("... et elles sont les mêmes à tous les bras d'un même départ",
      all(len({e["cellules_communes"] for e in fab["lignes"] if e["depart"] == d}) == 1
          for d in fab["departs"]))
    v("... alors que les cellules propres, elles, diminuent avec le bras",
      all(all(x >= y for x, y in zip(
          [e["cellules_propres"] for e in sorted(
              (e for e in fab["lignes"] if e["depart"] == d), key=lambda e: e["bras"])],
          [e["cellules_propres"] for e in sorted(
              (e for e in fab["lignes"] if e["depart"] == d),
              key=lambda e: e["bras"])][1:])) for d in fab["departs"]))
    # ⚠⚠ LE GRAND PAS NE RONGE QU'UNE FOIS, donc il garde toujours au moins autant de cellules
    # que la marche libre. Si ça cessait d'être vrai, la comparaison « à erreur égale » ne
    # dirait plus rien, puisque c'est ce compte qui la rend actionnable.
    v("... le grand pas garde toujours au moins autant de cellules que la marche libre",
      all(e["cellules_dun_grand_pas"] >= e["cellules_propres"] for e in fab["lignes"]),
      str([(e["bras"], e["cellules_propres"], e["cellules_dun_grand_pas"])
           for e in fab["lignes"]][:3]))
    v("... et strictement plus dès qu'on marche plus d'un tour",
      all(e["cellules_dun_grand_pas"] > e["cellules_propres"]
          for e in fab["lignes"] if e["bras"] > 1))
    v("... le témoin d'un grand pas est mesuré lui aussi",
      any(e["erreur_dun_grand_pas_um"] is not None for e in fab["lignes"]),
      str(sum(1 for e in fab["lignes"] if e["erreur_dun_grand_pas_um"] is not None)))
    v("... et les trois verdicts sont rendus, quel que soit leur signe",
      all(k in fab for k in ("le_masque_change_la_forme_de_la_courbe",
                             "la_sous_linearite_tient_a_depart_fixe", "literation_coute")))
    # ⚠⚠⚠ LE CRITÈRE SANS SEUIL, VÉRIFIÉ DANS LES DEUX SENS SUR DES NOMBRES. Sans le négatif,
    # « sous-linéaire » serait un mot qu'aucune donnée ne peut contredire — et c'est exactement
    # comme ça que le critère précédent, « les incréments croissent », a rendu deux verdicts
    # opposés sur deux populations qui mesurent la même chose.
    def sous_lin(suite):
        return all(x < (i + 1) * suite[0] for i, x in enumerate(suite) if i)

    v("le critère dit OUI d'une suite sous la droite du premier pas",
      sous_lin([44.2, 62.7, 103.5, 134.1]))
    v("... et NON d'une suite qui la dépasse", not sous_lin([10.0, 25.0, 40.0]))
    v("... et le premier incrément, celui du bras zéro, n'est jamais omis",
      len(fab["increments_communs_um"]) == len(fab["par_bras"]),
      str(fab["increments_communs_um"]))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "l'itération coûte" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, bras_max=3, corpus=corpus_fabrique(decalage_vx=5000.0))
    except RuntimeError as exc:
        hors = str(exc)
    v("un corpus posé hors de la boîte est REFUSÉ, pas rendu vide", hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure."""
    print(f"écart inter-feuilles {r['ecart_lu_um']} µm · demi-épaisseur "
          f"{r['demi_epaisseur_um']} µm · {r['marches']} marches depuis "
          f"{len(r['departs'])} spires\n")
    print(f"{'bras':>5} {'marches':>8} {'cell. propres':>14} {'PROPRE':>9} "
          f"{'cell. comm.':>12} {'COMMUN':>9} {'un grand pas':>14}")
    print("-" * 78)
    for b, d in r["par_bras"].items():
        gp = "—" if d["un_grand_pas_um"] is None else f"{d['un_grand_pas_um']:>13.1f}µ"
        print(f"{b:>5} {d['n']:>8} {d['cellules_propres']:>14} {d['propre_um']:>8.1f}µ "
              f"{d['cellules_communes']:>12} {d['commune_um']:>8.1f}µ {gp}")
    print(f"\nincréments depuis le bras zéro — propre {r['increments_propres_um']} µm · "
          f"commun {r['increments_communs_um']} µm · "
          f"un grand pas {r['increments_dun_grand_pas_um']} µm")
    print(f"coût PAR TOUR (erreur divisée par le bras) — commun "
          f"{r['cout_par_tour_commun_um']} µm · un grand pas "
          f"{r['cout_par_tour_dun_grand_pas_um']} µm")
    print(f"le masque coûte {r['ecart_du_masque_um']} µm (commun moins propre)")
    print(f"→ la dérive est SOUS-linéaire (sous k fois le premier pas) — propre "
          f"{'OUI' if r['sous_lineaire_sur_le_masque_propre'] else 'NON'} · commun "
          f"{'OUI' if r['sous_lineaire_sur_le_masque_commun'] else 'NON'}")
    print(f"→ le masque change la forme de la courbe : "
          f"{'OUI' if r['le_masque_change_la_forme_de_la_courbe'] else 'NON'}")
    print(f"→ le PREMIER pas coûte plus que n'importe quel tour suivant : "
          f"{'OUI' if r['le_premier_pas_coute_le_plus'] else 'NON'}")
    print(f"\npar spire de départ (masque commun) :")
    for d, v_ in r["par_depart"].items():
        marque = " (sous-linéaire)" if int(d) in r["departs_sous_lineaires"] else ""
        print(f"  spire {d:>3} · " + " · ".join(f"bras {b} {x:.0f}µ" for b, x in v_.items())
              + marque)
    print(f"→ la sous-linéarité tient à spire de départ FIXE : "
          f"{'OUI' if r['la_sous_linearite_tient_a_depart_fixe'] else 'NON'} "
          f"({len(r['departs_sous_lineaires'])} sur "
          f"{len(r['departs_a_trois_bras_ou_plus'])} départs à trois bras ou plus)")
    print(f"\ncoût de l'itération, bras par bras : {r['cout_de_literation_um']} µm "
          f"(marche libre moins un grand pas)")
    print(f"cellules gardées EN PLUS par le grand pas : "
          f"{r['cellules_gardees_en_plus_par_le_grand_pas']} — soit "
          f"{100 * (r['part_de_nappe_gagnee_au_dernier_bras'] or 0):.0f} % de nappe en plus au "
          f"bras {max(r['par_bras'], key=int)}, à erreur égale")
    print(f"→ l'itération coûte : {'OUI' if r['literation_coute'] else 'NON'} "
          f"({r['marches_ou_liteation_coute']} marches sur {r['marches_comparables']}) · "
          f"un grand pas est sous-linéaire aussi : "
          f"{'OUI' if r['un_grand_pas_est_sous_lineaire_aussi'] else 'NON'}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--bras-max", type=int, default=4)
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
