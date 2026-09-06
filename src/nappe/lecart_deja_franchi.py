#!/usr/bin/env python3
"""L'écart déjà franchi prédit-il celui à franchir ? — le premier gain qu'un dérouleur peut prendre

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `le_cout_dun_seul_pas` a montré qu'un tiers du coût d'un pas
vient d'une longueur prise sur la mauvaise population : le pas nominal vaut 135,5 µm, médiane sur
**toutes** les spires du fragment, quand l'écart local dans la boîte mesurée vaut **104,1**. Ce
tiers n'est pas un réglage à trouver, c'est un nombre à **mesurer** — mais un dérouleur ne peut
pas mesurer l'écart qu'il n'a pas encore franchi.

⭐⭐⭐ IL PEUT MESURER CELUI QU'IL VIENT DE FRANCHIR. Un dérouleur qui part d'une paire d'ancres
`r − 1` et `r` connaît, **en chaque point**, la distance qui sépare ces deux surfaces là. La
question est donc : cette distance-là prédit-elle la suivante ? Si oui, le tiers du coût est
récupérable **sans jamais regarder la cible**, et ce serait le premier gain de toute la campagne
qu'un vrai dérouleur puisse encaisser.

⚠⚠ LE TÉMOIN QUI DÉCIDE EST LE PRÉDICTEUR MÉLANGÉ. Une longueur par point tirée dans la BONNE
distribution mais attribuée au MAUVAIS point a la même moyenne et la même dispersion, et elle
gagnerait donc autant qu'un simple recentrage du pas. Ce qui distingue « la prédiction porte de
l'information locale » de « le pas nominal était juste mal centré » est de battre ce mélange.

⚠ Aucune lecture du volume : tout se mesure entre spires publiées. Cette tranche ne coûte pas un
bloc.

Usage :
    uv run python src/nappe/lecart_deja_franchi.py --verifier
    uv run python src/nappe/lecart_deja_franchi.py --json docs/mesures/lecart_deja_franchi.json
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


def erreur_par_point(points: np.ndarray, directions: np.ndarray, longueurs: np.ndarray,
                     cible: np.ndarray, voxel_um: float) -> np.ndarray:
    """L'erreur de chaque point avancé de SA longueur, en micromètres.

    ⚠ Les longueurs sont un vecteur, pas un scalaire : c'est ce qui distingue un pas prédit
    point par point d'un pas commun, et les deux se mesurent avec la même fonction pour que leur
    différence ne puisse pas venir de deux façons de mesurer.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    return distance_a(points + longueurs[:, None] * directions, cible, voxel_um)


def mesurer(cote: float | None = None, minimum: int = 30, points_max: int = 1500,
            graine: int = 42, corpus: dict | None = None) -> dict:
    """L'écart déjà franchi, comme longueur de pas, contre le nominal et contre son mélange."""
    from le_pas_normal_atteint_la_spire import distance_a, essayer_le_pas, normales  # noqa: PLC0415, E501
    from le_raccrochage_a_la_matiere import BOITE_CENTRE, BOITE_COTE  # noqa: PLC0415

    c = corpus_publie() if corpus is None else corpus
    volume, voxel_um = c["volume"], float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    rng = np.random.default_rng(graine)

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        grilles[rang] = (a, dans)
        nuages[rang] = a[ok]

    lignes, tous_avant, tous_apres = [], [], []
    for r in sorted(grilles):
        # ⚠⚠ IL FAUT LES TROIS : la spire d'avant pour le prédicteur, celle du départ pour
        # marcher, celle d'après pour juger. Une paire sans prédécesseur n'a rien à prédire
        # depuis, et l'inclure ferait un corpus où la moitié des lignes n'a pas de prédiction.
        if r - 1 not in nuages or r + 1 not in nuages:
            continue
        a0, dans = grilles[r]
        n0, bon = normales(a0, dans)
        garde = bon & dans
        if int(garde.sum()) < minimum:
            continue
        p, d = a0[garde], n0[garde]
        if len(p) > points_max:
            pris = rng.choice(len(p), size=points_max, replace=False)
            p, d = p[pris], d[pris]
        avant_nuage, cible = nuages[r - 1], nuages[r + 1]
        # ⚠ Le sens est fixé une fois, en regardant la cible : c'est le bit de supervision que
        # toute cette campagne compte, et il n'en faut pas un de plus ici.
        sens = 1.0 if essayer_le_pas(p, d, cible, pas_vx, voxel_um)["retenu"] == "+" else -1.0
        d = sens * d

        # ⚠⚠ LE PRÉDICTEUR EST DISPONIBLE, ET C'EST TOUT SON INTÉRÊT : la distance de chaque
        # point à la spire PRÉCÉDENTE se calcule avec les deux ancres que le dérouleur a déjà.
        # Rien de la cible n'y entre.
        d_avant = distance_a(p, avant_nuage, voxel_um) / voxel_um
        d_apres = distance_a(p, cible, voxel_um) / voxel_um
        tous_avant.append(d_avant * voxel_um)
        tous_apres.append(d_apres * voxel_um)

        e_nominal = erreur_par_point(p, d, np.full(len(p), pas_vx), cible, voxel_um)
        e_predite = erreur_par_point(p, d, d_avant, cible, voxel_um)
        # ⚠⚠⚠ LE TÉMOIN : les MÊMES longueurs, attribuées aux MAUVAIS points. Même moyenne, même
        # dispersion, aucune information locale. Sans lui, « la prédiction aide » serait
        # satisfait par un simple recentrage du pas.
        e_melange = erreur_par_point(p, d, rng.permutation(d_avant), cible, voxel_um)
        # ⚠⚠⚠ ET LE TROISIÈME CONTENDANT, CELUI QUI MANQUAIT : la MÉDIANE de l'écart franchi,
        # prise comme une longueur unique. Elle est disponible exactement comme la prédiction
        # par point, elle n'a aucune information locale, et elle n'a pas non plus le bruit du
        # mélange. C'est le « recentrage » pur — et sans lui on ne peut pas distinguer « prédire
        # point par point aide » de « le pas était juste mal centré ».
        e_recentree = erreur_par_point(
            p, d, np.full(len(p), float(np.median(d_avant))), cible, voxel_um)
        # ⚠ Et l'oracle : la vraie distance à la cible, qui demande la réponse. C'est une borne,
        # pas un contendant.
        e_oracle = erreur_par_point(p, d, d_apres, cible, voxel_um)
        lignes.append(dict(
            depuis=r, avant=r - 1, cible=r + 1, cellules=int(len(p)),
            ecart_avant_median_um=round(float(np.median(d_avant)) * voxel_um, 1),
            ecart_apres_median_um=round(float(np.median(d_apres)) * voxel_um, 1),
            erreur_nominale_um=round(float(np.median(e_nominal)), 1),
            erreur_predite_um=round(float(np.median(e_predite)), 1),
            erreur_melangee_um=round(float(np.median(e_melange)), 1),
            erreur_recentree_um=round(float(np.median(e_recentree)), 1),
            erreur_oracle_um=round(float(np.median(e_oracle)), 1),
            bits_de_supervision=1))

    if not lignes:
        raise RuntimeError("aucun triplet de spires consécutives dans la boîte")

    def med(cle):
        return round(float(np.median([e[cle] for e in lignes])), 1)

    avant = np.concatenate(tous_avant)
    apres = np.concatenate(tous_apres)
    r = dict(
        fragment="PHerc0500P2", volume=volume, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        pas_nominal_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        triplets=len(lignes), cellules=int(len(avant)), lignes=lignes,
        erreur_nominale_mediane_um=med("erreur_nominale_um"),
        erreur_predite_mediane_um=med("erreur_predite_um"),
        erreur_melangee_mediane_um=med("erreur_melangee_um"),
        erreur_recentree_mediane_um=med("erreur_recentree_um"),
        erreur_oracle_mediane_um=med("erreur_oracle_um"),
        ecart_avant_median_um=round(float(np.median(avant)), 1),
        ecart_apres_median_um=round(float(np.median(apres)), 1))
    # ⚠⚠⚠ LA CORRÉLATION EST DE RANG, PAS DE PEARSON : on demande si l'ordre se conserve — les
    # points où l'écart franchi est grand sont-ils ceux où le suivant l'est —, pas si les deux
    # sont proportionnels. Et elle porte sur des MILLIERS de cellules, pas sur douze paires : un
    # verdict sur douze n'en serait pas un.
    from scipy.stats import spearmanr  # noqa: PLC0415

    rho, pval = spearmanr(avant, apres)
    r["ecart_avant_contre_apres"] = dict(rho=round(float(rho), 3), p=float(f"{pval:.3g}"),
                                         n=int(len(avant)))
    r["lecart_franchi_predit_le_suivant"] = bool(rho > 0 and pval < 0.05)
    # ⚠⚠⚠ UN COEFFICIENT NE SE VOIT PAS ; UNE COURBE, SI. La médiane de l'écart SUIVANT, prise
    # par décile de l'écart FRANCHI, montre directement s'il y a une relation : plate, il n'y en
    # a pas. Publier `rho` seul laisserait croire qu'un nombre proche de zéro et un nombre
    # franchement négatif se lisent pareil.
    # ⚠ Les déciles sont ceux de l'écart franchi, donc chaque tranche a le même nombre de
    # cellules : des tranches de largeur égale mettraient presque tout dans une seule.
    bornes = np.percentile(avant, np.arange(0, 101, 10))
    tranches = []
    for i in range(10):
        dans_t = (avant >= bornes[i]) & (avant <= bornes[i + 1] if i == 9
                                         else avant < bornes[i + 1])
        if int(dans_t.sum()) == 0:
            continue
        tranches.append(dict(decile=i + 1, n=int(dans_t.sum()),
                             avant_median_um=round(float(np.median(avant[dans_t])), 1),
                             apres_median_um=round(float(np.median(apres[dans_t])), 1)))
    r["apres_par_decile_de_avant"] = tranches
    # ⚠⚠ ET L'ÉTENDUE DE LA COURBE, qui est ce qui dit si la relation vaut quelque chose : si le
    # suivant ne bouge que de quelques micromètres quand le franchi en parcourt cent, alors
    # même une corrélation significative ne porte rien d'utilisable.
    r["etendue_de_lecart_franchi_um"] = round(
        tranches[-1]["avant_median_um"] - tranches[0]["avant_median_um"], 1) if tranches else None
    r["etendue_de_lecart_suivant_um"] = round(
        max(t["apres_median_um"] for t in tranches)
        - min(t["apres_median_um"] for t in tranches), 1) if tranches else None
    # ⚠⚠ LES DEUX COMPARAISONS QUI DÉCIDENT, ET IL EN FAUT DEUX. Battre le nominal ne suffit pas
    # — un pas simplement mieux centré y suffirait ; battre le MÉLANGE est ce qui montre que
    # l'information est locale.
    # ⚠⚠⚠ UN VERDICT SUR LA MÉDIANE QUE LE COMPTE PAR CAS CONTREDIT N'EST PAS UN VERDICT, et
    # c'est une correction : la première version rendait « la prédiction bat le nominal : OUI »
    # sur un écart de 0,5 µm alors qu'elle ne gagnait que sur deux triplets sur cinq. Les deux
    # sont exigés ensemble.
    for nom, cle in (("le_nominal", "erreur_nominale_um"),
                     ("son_melange", "erreur_melangee_um"),
                     ("le_recentrage", "erreur_recentree_um")):
        gagnes = sum(1 for e in lignes if e["erreur_predite_um"] < e[cle])
        r[f"triplets_ou_la_prediction_bat_{nom}"] = gagnes
        r[f"la_prediction_bat_{nom}"] = bool(
            r["erreur_predite_mediane_um"] < r[cle.replace("_um", "_mediane_um")]
            and gagnes > len(lignes) / 2)
    r["triplets_ou_le_recentrage_bat_le_nominal"] = sum(
        1 for e in lignes if e["erreur_recentree_um"] < e["erreur_nominale_um"])
    r["le_recentrage_bat_le_nominal"] = bool(
        r["erreur_recentree_mediane_um"] < r["erreur_nominale_mediane_um"]
        and r["triplets_ou_le_recentrage_bat_le_nominal"] > len(lignes) / 2)
    r["gain_sur_le_nominal_um"] = round(
        r["erreur_nominale_mediane_um"] - r["erreur_predite_mediane_um"], 1)
    r["gain_du_recentrage_um"] = round(
        r["erreur_nominale_mediane_um"] - r["erreur_recentree_mediane_um"], 1)
    r["gain_du_melange_seul_um"] = round(
        r["erreur_nominale_mediane_um"] - r["erreur_melangee_mediane_um"], 1)
    # ⚠⚠ AUCUNE PART N'EST PUBLIÉE QUAND SON DÉNOMINATEUR EST NÉGLIGEABLE, et c'est une seconde
    # correction : la première version rendait « la part vraiment locale est 9,6 » — un rapport
    # supérieur à un, qui n'a aucun sens comme part, parce qu'il divisait par un gain de 0,5 µm.
    # Un rapport dont le dénominateur est plus petit que la résolution de la mesure ne dit rien.
    marge_um = 1.0
    r["part_du_gain_de_loracle_prise"] = (
        round(r["gain_sur_le_nominal_um"]
              / (r["erreur_nominale_mediane_um"] - r["erreur_oracle_mediane_um"]), 3)
        if r["erreur_nominale_mediane_um"] - r["erreur_oracle_mediane_um"] > marge_um else None)
    r["gain_trop_petit_pour_une_part"] = bool(abs(r["gain_sur_le_nominal_um"]) <= marge_um)
    r["sous_la_demi_feuille"] = {
        cle: bool(r[cle] < ecart_um / 2) for cle in
        ("erreur_nominale_mediane_um", "erreur_predite_mediane_um", "erreur_oracle_mediane_um")}
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'erreur par point ---
    p = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    d = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    cible = np.array([[0.0, 0.0, 5.0], [10.0, 0.0, 9.0]])
    v("chaque point avance de SA longueur, pas d'une commune",
      bool(np.allclose(erreur_par_point(p, d, np.array([5.0, 9.0]), cible, 1.0), [0.0, 0.0])),
      str(erreur_par_point(p, d, np.array([5.0, 9.0]), cible, 1.0).tolist()))
    v("... et une longueur commune ne peut satisfaire qu'un point à la fois",
      float(np.median(erreur_par_point(p, d, np.array([5.0, 5.0]), cible, 1.0))) > 0)
    # ⚠⚠ LE TÉMOIN EST EXACTEMENT LES MÊMES LONGUEURS, PERMUTÉES : même moyenne, même
    # dispersion. Le vérifier sur des nombres, sinon « mélangé » pourrait vouloir dire autre
    # chose — par exemple un tirage dans une loi, qui n'aurait pas la même dispersion.
    lg = np.array([3.0, 7.0, 11.0])
    perm = np.random.default_rng(1).permutation(lg)
    v("le mélange garde exactement les mêmes longueurs",
      sorted(perm.tolist()) == sorted(lg.tolist()), str(perm.tolist()))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    fab = mesurer(minimum=20, points_max=200, corpus=corpus_fabrique())
    v("la mesure tourne de bout en bout sur un corpus fabriqué, sans rien lire",
      fab["triplets"] > 0 and fab["cellules"] > 0,
      f"{fab['triplets']} triplets, {fab['cellules']} cellules")
    v("... chaque triplet a bien une spire avant, une de départ et une cible",
      all(e["avant"] == e["depuis"] - 1 and e["cible"] == e["depuis"] + 1
          for e in fab["lignes"]))
    v("... et la marche y est imparfaite, donc les comparaisons portent sur quelque chose",
      all(e["erreur_nominale_um"] > 0 for e in fab["lignes"]))
    # ⚠⚠⚠ L'ORACLE EST UNE BORNE, DONC IL NE PEUT PAS ÊTRE BATTU par un contendant qui ne
    # regarde pas la cible. Si la prédiction le battait, c'est qu'elle en saurait plus que la
    # réponse — signe que quelque chose fuit.
    v("... l'oracle n'est battu par aucun contendant aveugle",
      all(e["erreur_oracle_um"] <= min(e["erreur_predite_um"], e["erreur_melangee_um"]) + 0.05
          for e in fab["lignes"]),
      str([(e["erreur_oracle_um"], e["erreur_predite_um"]) for e in fab["lignes"]][:3]))
    # ⚠⚠ LES DÉCILES COUVRENT TOUTES LES CELLULES : une tranche perdue ferait une courbe qui
    # ne décrit qu'une partie du corpus tout en ayant l'air complète.
    v("... les déciles couvrent toutes les cellules, sans en perdre",
      sum(t["n"] for t in fab["apres_par_decile_de_avant"]) == fab["cellules"],
      f"{sum(t['n'] for t in fab['apres_par_decile_de_avant'])} sur {fab['cellules']}")
    v("... et l'écart franchi croît bien d'un décile au suivant, sinon ce ne sont pas des déciles",
      all(a["avant_median_um"] <= b["avant_median_um"] for a, b in
          zip(fab["apres_par_decile_de_avant"], fab["apres_par_decile_de_avant"][1:])))
    v("... la corrélation porte sur les cellules, pas sur les triplets",
      fab["ecart_avant_contre_apres"]["n"] == fab["cellules"],
      f"{fab['ecart_avant_contre_apres']['n']} cellules")
    v("... et les trois comparaisons sont rendues, quel que soit leur signe",
      all(k in fab for k in ("la_prediction_bat_le_nominal", "la_prediction_bat_son_melange",
                             "le_recentrage_bat_le_nominal")))
    # ⚠⚠⚠ UN VERDICT SUR LA MÉDIANE QUE LE COMPTE PAR CAS CONTREDIT N'EST PAS UN VERDICT : la
    # première version rendait OUI sur 0,5 µm d'écart alors que la prédiction ne gagnait que sur
    # deux triplets sur cinq. Les deux conditions sont désormais exigées ensemble.
    v("... un verdict exige la médiane ET le compte par cas",
      all(not fab[f"la_prediction_bat_{n}"]
          or fab[f"triplets_ou_la_prediction_bat_{n}"] > fab["triplets"] / 2
          for n in ("le_nominal", "son_melange", "le_recentrage")))
    # ⚠⚠ ET AUCUNE PART N'EST PUBLIÉE QUAND SON DÉNOMINATEUR EST NÉGLIGEABLE : la première
    # version rendait « la part vraiment locale est 9,6 », un rapport supérieur à un qui n'a
    # aucun sens comme part, parce qu'il divisait par un gain de 0,5 µm.
    v("... et une part n'est publiée que si son dénominateur veut dire quelque chose",
      fab["gain_trop_petit_pour_une_part"] == (abs(fab["gain_sur_le_nominal_um"]) <= 1.0),
      f"gain {fab['gain_sur_le_nominal_um']} µm")
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "bat son MÉLANGE" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, points_max=200, corpus=corpus_fabrique(decalage_vx=5000.0))
    except RuntimeError as exc:
        hors = str(exc)
    v("un corpus posé hors de la boîte est REFUSÉ, pas rendu vide", hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure."""
    print(f"pas nominal {r['pas_nominal_um']} µm · demi-épaisseur {r['demi_epaisseur_um']} µm · "
          f"{r['triplets']} triplets de spires consécutives, {r['cellules']} cellules\n")
    print(f"{'avant':>6} {'de':>4} {'vers':>5} {'cell.':>7} {'écart avant':>12} "
          f"{'écart après':>12} {'NOMINAL':>9} {'PRÉDIT':>9} {'recentré':>10} {'mélangé':>9} "
          f"{'oracle':>8}")
    print("-" * 108)
    for e in r["lignes"]:
        print(f"{e['avant']:>6} {e['depuis']:>4} {e['cible']:>5} {e['cellules']:>7} "
              f"{e['ecart_avant_median_um']:>11.1f}µ {e['ecart_apres_median_um']:>11.1f}µ "
              f"{e['erreur_nominale_um']:>8.1f}µ {e['erreur_predite_um']:>8.1f}µ "
              f"{e['erreur_recentree_um']:>9.1f}µ {e['erreur_melangee_um']:>8.1f}µ "
              f"{e['erreur_oracle_um']:>7.1f}µ")
    print(f"\nmédianes : nominal {r['erreur_nominale_mediane_um']} µm · PRÉDIT "
          f"{r['erreur_predite_mediane_um']} · recentré {r['erreur_recentree_mediane_um']} · "
          f"mélangé {r['erreur_melangee_mediane_um']} · oracle "
          f"{r['erreur_oracle_mediane_um']} µm")
    d_ = r["ecart_avant_contre_apres"]
    print(f"l'écart franchi prédit-il le suivant ? rho {d_['rho']} (p {d_['p']}, n {d_['n']} "
          f"cellules) → {'OUI' if r['lecart_franchi_predit_le_suivant'] else 'NON'}")
    print("\nl'écart SUIVANT, par décile de l'écart FRANCHI — une courbe plate ne porte rien :")
    print("  franchi " + " ".join(f"{t['avant_median_um']:>6.0f}"
                                  for t in r["apres_par_decile_de_avant"]))
    print("  suivant " + " ".join(f"{t['apres_median_um']:>6.0f}"
                                  for t in r["apres_par_decile_de_avant"]))
    print(f"  → le franchi parcourt {r['etendue_de_lecart_franchi_um']} µm pendant que le "
          f"suivant en parcourt {r['etendue_de_lecart_suivant_um']}")
    print(f"\ngains sur le nominal : prédit {r['gain_sur_le_nominal_um']} µm · recentré "
          f"{r['gain_du_recentrage_um']} · mélangé {r['gain_du_melange_seul_um']} µm")
    if r["gain_trop_petit_pour_une_part"]:
        print("⚠ le gain de la prédiction est plus petit que la marge de la mesure : aucune "
              "part n'en est publiée, un rapport à dénominateur négligeable ne dit rien")
    else:
        print(f"elle prend {r['part_du_gain_de_loracle_prise']} de ce que l'oracle prendrait")
    print(f"→ la prédiction bat le nominal : "
          f"{'OUI' if r['la_prediction_bat_le_nominal'] else 'NON'} "
          f"({r['triplets_ou_la_prediction_bat_le_nominal']} triplets sur {r['triplets']})")
    print(f"→ et elle bat son MÉLANGE — donc l'information serait locale : "
          f"{'OUI' if r['la_prediction_bat_son_melange'] else 'NON'} "
          f"({r['triplets_ou_la_prediction_bat_son_melange']} triplets sur {r['triplets']})")
    print(f"→ le RECENTRAGE seul — la médiane de l'écart franchi, sans information par point — "
          f"bat le nominal : {'OUI' if r['le_recentrage_bat_le_nominal'] else 'NON'} "
          f"({r['triplets_ou_le_recentrage_bat_le_nominal']} triplets sur {r['triplets']})")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--points", type=int, default=1500)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, points_max=a.points)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
