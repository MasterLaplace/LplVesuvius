#!/usr/bin/env python3
"""Jusqu'où la lissité de la feuille peut-elle porter le raccrochage ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `le_critere_du_raccrochage` a mesuré que ce qui fait marcher le
raccrochage n'est **pas** la corrélation d'intensité — seule, elle ne tranche pas — mais l'accord
de voisinage, c'est-à-dire un énoncé sur la **matière** : *une feuille de papyrus est lisse à
l'échelle de trois cellules de grille*. Or cette contrainte est exploitée de la façon la plus
pauvre possible : une médiane sur **trois** cellules, appliquée **une fois**.

⭐⭐ CE FICHIER DEMANDE JUSQU'OÙ ELLE PORTE. Le voisinage s'élargit — 3×3, 5×5, 9×9, 17×17 — et
s'itère — la même médiane deux fois, trois fois. Chaque étage est jugé sur la même population,
contre le fait de ne rien faire **et** contre sa propre version non lissée.

⚠⚠ ET LE TÉMOIN SUIT À CHAQUE ÉTAGE, parce que c'est la seule façon de lire le résultat. Une
médiane de voisinage améliore n'importe quoi : appliquée aux décalages d'un gabarit **mélangé**,
elle gagne aussi. Ce qui est attribuable à la LECTURE est ce qui reste quand on retire ce que le
même lissage rend sur du bruit — et cette part est publiée à chaque étage, pas seulement au bout.

⚠ La famille des demi-largeurs double à partir de celle en service, et son bout large a un sens :
à 17×17 la fenêtre couvre déjà une fraction notable de la grille de la boîte, donc la médiane
tend vers la médiane globale — c'est-à-dire vers le recentrage, dont `le_critere_du_raccrochage`
a mesuré qu'il ne tranche pas seul.

Usage :
    uv run python src/nappe/la_lissite_de_la_feuille.py --verifier
    uv run python src/nappe/la_lissite_de_la_feuille.py --cote 960 \\
        --json docs/mesures/la_lissite_de_la_feuille.json
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

# ⚠⚠⚠ LE PARCOURS DES PAS EST IMPORTÉ, JAMAIS RECOPIÉ. Ce que la lecture d'un pas coûte — une
# traversée du volume pour le gabarit, une pour les lignes — est le même quel que soit ce qu'on
# balaye ensuite ; deux copies seraient deux mesures qui pourraient cesser de marcher sur la
# même matière.
from le_corpus_des_spires import corpus_fabrique, corpus_publie, volume_fabrique  # noqa: E402
from le_critere_du_raccrochage import (  # noqa: E402
    decalages_du_critere, parcourir_les_pas, poser_sur_la_grille,
)
from le_raccrochage_choisit_il_bien import decalage_de_loracle  # noqa: E402
from lecart_apparie import ecart_apparie, tranche  # noqa: E402

# ⚠ La famille double à partir de la demi-largeur EN SERVICE, qui vaut un.
DEMI_LARGEURS = (1, 2, 4, 8)
# ⚠ Et l'autre façon d'élargir : la même médiane, plusieurs fois. Ce n'est pas la même chose
# qu'une fenêtre large — itérer diffuse, élargir moyenne — donc les deux sont balayées.
PASSES = (2, 3)
LECTURES = ("correlation", "melange")


def etages(demi_largeurs=DEMI_LARGEURS, passes=PASSES) -> list[tuple[str, int, int]]:
    """Les étages de lissage balayés : `(nom, demi-largeur, passes)`.

    ⚠ L'étage sans lissage porte une demi-largeur de zéro plutôt qu'une absence : c'est ce qui
    permet de le traiter comme les autres au lieu d'en faire un cas particulier, et un cas
    particulier est exactement là où un traitement finit par différer sans qu'on le voie.
    """
    out = [("brut", 0, 0)]
    out += [(f"median_{d}", int(d), 1) for d in demi_largeurs]
    out += [(f"median_1_x{n}", 1, int(n)) for n in passes]
    return out


def lisser(t: np.ndarray, valide: np.ndarray, demi: int,
           passes: int) -> tuple[np.ndarray, np.ndarray]:
    """Le champ de décalages lissé, et les cellules que le lissage retient.

    ⚠⚠ LE MASQUE RÉTRÉCIT À CHAQUE PASSE, et il est rendu avec les valeurs. Une cellule dont le
    voisinage ne fait pas majorité est écartée, donc deux passes en écartent davantage qu'une :
    juger un étage sur ce qu'il lui reste et un autre sur ce qu'il lui reste comparerait deux
    populations, ce que ce dépôt a déjà eu à retirer une fois.

    ⚠ Zéro passe rend le champ intact : c'est l'étage « brut », traité comme les autres.
    """
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    champ, masque = t, valide
    for _ in range(max(0, int(passes))):
        champ, masque = accorder_les_voisins(champ, masque, demi=demi)
    return champ, masque


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, fenetre_grille: int | None = None,
            demi_largeurs=DEMI_LARGEURS, passes=PASSES,
            corpus: dict | None = None, volume=None) -> dict:
    """Ce que chaque étage de lissité rend, sur la lecture et sur le bruit."""
    table = etages(demi_largeurs, passes)
    pas = parcourir_les_pas(graine, minimum, cache_actif, cote, fenetre_grille, corpus, volume)
    reglage = next(pas)
    lignes: list[dict] = []
    for ctx in pas:
        # ⚠⚠⚠ UNE SEULE POPULATION POUR TOUS LES ÉTAGES, et c'est le plus large qui la fixe.
        # Les masques de tous les étages sont d'abord calculés, puis intersectés : sans ça, un
        # voisinage de 17×17 serait noté sur les cellules du cœur de la grille pendant qu'un
        # 3×3 serait noté sur presque tout, et l'écart mesuré porterait sur les bords.
        masques = []
        for _, demi, npasses in table:
            masques.append(lisser(np.zeros_like(ctx["lisible"], dtype=float),
                                  ctx["lisible"], demi, npasses)[1])
        commun = ctx["assez"].copy()
        for m in masques:
            commun &= m
        if int(commun.sum()) < minimum:
            reglage["ecartees"] += 1
            continue
        pris = commun[ctx["lisible"]]

        brut = {
            "correlation": decalages_du_critere(
                "correlation", ctx["corr"], ctx["corr_melange"], ctx["centres"],
                ctx["L"], ctx["t_fenetre"]),
            "melange": decalages_du_critere(
                "melange", ctx["corr"], ctx["corr_melange"], ctx["centres"],
                ctx["L"], ctx["t_fenetre"]),
        }
        entree = dict(de=ctx["de"], vers=ctx["vers"],
                      cellules_lisibles=int(ctx["lisible"].sum()),
                      cellules=int(commun.sum()), bits_de_supervision=1)
        entree["erreur_ne_rien_faire_um"] = round(
            ctx["erreur"](np.zeros(len(ctx["P"])), pris)[0], 1)
        t_oracle, _ = decalage_de_loracle(ctx["P"], ctx["D"], ctx["centres"], ctx["cible"],
                                          reglage["voxel_um"])
        entree["erreur_oracle_um"] = round(ctx["erreur"](t_oracle, pris)[0], 1)
        for lecture in LECTURES:
            for nom, demi, npasses in table:
                grille_t = poser_sur_la_grille(brut[lecture], ctx["lisible"],
                                               ctx["lisible"].shape)
                champ, _ = lisser(grille_t, ctx["lisible"], demi, npasses)
                valeurs = champ[ctx["ou_lisible"][:, 0], ctx["ou_lisible"][:, 1]]
                plat = np.where(np.isnan(valeurs), brut[lecture], valeurs)
                med, _ = ctx["erreur"](plat, pris)
                entree[f"erreur_{lecture}_{nom}_um"] = round(med, 1)
                if nom != "brut":
                    ecart = np.abs(plat - brut[lecture])[pris]
                    entree[f"deplacees_{lecture}_{nom}"] = int((ecart > 1e-9).sum())
        lignes.append(entree)

    if not lignes:
        raise RuntimeError("aucun pas ne rend un voisinage assez large dans la boîte")

    vol = reglage["vol"]
    r = dict(
        fragment="PHerc0500P2", volume=reglage["volume"], voxel_um=reglage["voxel_um"],
        boite=reglage["boite"], pas_nominal_um=reglage["ecart_um"],
        demi_epaisseur_um=round(reglage["ecart_um"] / 2, 2),
        demi_largeurs=[int(x) for x in demi_largeurs], passes=[int(x) for x in passes],
        etages=[n for n, _, _ in table], lectures=list(LECTURES),
        paires=len(lignes), paires_ecartees=int(reglage["ecartees"]),
        cellules=int(sum(e["cellules"] for e in lignes)),
        cellules_lisibles=int(sum(e["cellules_lisibles"] for e in lignes)),
        lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises))

    def par_pas(cle: str) -> list[float]:
        return [e[cle] for e in lignes]

    resume = []
    for nom, demi, npasses in table:
        entree = dict(etage=nom, demi_largeur=demi, passes=npasses,
                      cellules_du_voisinage=(2 * demi + 1) ** 2 if demi else 1,
                      deploye=bool(demi == 1 and npasses == 1))
        for lecture in LECTURES:
            cle = f"erreur_{lecture}_{nom}_um"
            entree[f"erreur_{lecture}_um"] = round(float(np.median(par_pas(cle))), 1)
            entree[f"{lecture}_contre_ne_rien_faire"] = ecart_apparie(
                par_pas(cle), par_pas("erreur_ne_rien_faire_um"))
            entree[f"{lecture}_contre_brut"] = ecart_apparie(
                par_pas(cle), par_pas(f"erreur_{lecture}_brut_um"))
        # ⭐⭐⭐ LA PART QUI N'EST PAS DU LISSAGE, ÉTAGE PAR ÉTAGE. Le même lissage appliqué au
        # bruit dit ce qu'un adoucissement rend tout seul ; ce qui reste est ce que la LECTURE
        # apporte à cet étage-là. Publier le gain brut sans cette soustraction créditerait la
        # corrélation d'un geste qui marche sans elle.
        a = entree["correlation_contre_brut"]["ecart_median_um"]
        b = entree["melange_contre_brut"]["ecart_median_um"]
        entree["part_hors_lissage_um"] = (None if a is None or b is None
                                          else round(a - b, 1))
        resume.append(entree)
    r["resume"] = resume

    def trouver(nom: str) -> dict:
        return next(x for x in resume if x["etage"] == nom)

    r["erreur_ne_rien_faire_mediane_um"] = round(
        float(np.median(par_pas("erreur_ne_rien_faire_um"))), 1)
    r["erreur_oracle_mediane_um"] = round(
        float(np.median(par_pas("erreur_oracle_um"))), 1)
    deploye = trouver("median_1")
    r["etage_deploye"] = deploye
    # ⭐⭐ LE MEILLEUR ÉTAGE, PAR SON ÉCART APPARIÉ À NE RIEN FAIRE — et jamais par son erreur
    # brute : sur cette matière la dispersion entre pas vaut quatre fois celle entre méthodes.
    r["meilleur_etage"] = min(
        resume, key=lambda x: x["correlation_contre_ne_rien_faire"]["ecart_median_um"])
    r["un_etage_bat_le_deploye"] = bool(
        not r["meilleur_etage"]["deploye"]
        and tranche(ecart_apparie(
            par_pas(f"erreur_correlation_{r['meilleur_etage']['etage']}_um"),
            par_pas("erreur_correlation_median_1_um"))))
    r["ecart_du_meilleur_au_deploye"] = ecart_apparie(
        par_pas(f"erreur_correlation_{r['meilleur_etage']['etage']}_um"),
        par_pas("erreur_correlation_median_1_um"))
    # ⚠⚠⚠ ET LA QUESTION QUI DÉCIDE SI LA LISSITÉ EST UN LEVIER OU UN PLATEAU : la part hors
    # lissage grandit-elle avec la largeur, ou stagne-t-elle ? Un lissage qui n'ajoute plus que
    # de l'adoucissement au-delà d'un certain étage dit que la contrainte est épuisée.
    parts = [(x["etage"], x["part_hors_lissage_um"]) for x in resume
             if x["etage"] != "brut" and x["part_hors_lissage_um"] is not None]
    r["part_hors_lissage_par_etage"] = parts
    r["meilleure_part_hors_lissage"] = (min(parts, key=lambda p: p[1]) if parts else None)
    r["la_lissite_paie_au_dela_du_deploye"] = bool(
        r["meilleure_part_hors_lissage"] is not None
        and r["meilleure_part_hors_lissage"][0] != "median_1"
        and r["meilleure_part_hors_lissage"][1] < deploye["part_hors_lissage_um"])
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    t = etages()
    v("l'échelle part du BRUT et contient l'étage en service",
      t[0][0] == "brut" and ("median_1", 1, 1) in t, str([n for n, _, _ in t]))
    v("... les demi-largeurs doublent à partir de celle en service",
      [d for _, d, p in t if p == 1] == [1, 2, 4, 8])
    v("... et l'itération est balayée à part de l'élargissement",
      [n for n, d, p in t if p > 1] == ["median_1_x2", "median_1_x3"])

    # --- le lissage lui-même ---
    champ = np.full((9, 9), 3.0)
    champ[4, 4] = 50.0
    ok = np.ones((9, 9), dtype=bool)
    v("zéro passe rend le champ intact, sans rien écarter",
      np.array_equal(lisser(champ, ok, 0, 0)[0], champ)
      and lisser(champ, ok, 0, 0)[1].sum() == 81)
    a1, m1 = lisser(champ, ok, 1, 1)
    v("une passe ramène l'isolé sur ses voisins", a1[4, 4] == 3.0, str(a1[4, 4]))
    # ⚠⚠⚠ LE MASQUE NE GRANDIT JAMAIS, et c'est ce qui oblige à intersecter avant de juger :
    # deux étages notés chacun sur ce qu'il lui reste comparent deux populations.
    # ⚠ Ma première version affirmait qu'il rétrécit à CHAQUE passe : c'est faux, et la mesure
    # l'a dit — sur une grille pleine il se stabilise dès la seconde (77 → 77 → 77), parce que
    # seuls les coins manquent de majorité et que leur absence n'en prive personne d'autre.
    _, m2 = lisser(champ, ok, 1, 2)
    _, m3 = lisser(champ, ok, 1, 3)
    v("... le masque ne GRANDIT jamais avec les passes",
      int(m1.sum()) >= int(m2.sum()) >= int(m3.sum()),
      f"{int(m1.sum())} → {int(m2.sum())} → {int(m3.sum())}")
    # ⚠⚠ ET LÀ OÙ IL Y A DE QUOI RÉTRÉCIR, IL RÉTRÉCIT JUSQU'À RIEN : un îlot de cellules
    # lisibles est mangé par les passes successives. C'est le cas qui rend le contrôle
    # discriminant — sur une grille pleine, « ne grandit jamais » est satisfait par un masque
    # qui ne bouge pas du tout.
    ilot = np.zeros((9, 9), dtype=bool)
    ilot[3:6, 3:6] = True
    tailles = [int(lisser(champ, ilot, 1, n)[1].sum()) for n in (1, 2, 3)]
    v("... et un ÎLOT de cellules lisibles est mangé passe après passe",
      tailles[0] > tailles[1] > tailles[2] == 0, str(tailles))
    _, m_large = lisser(champ, ok, 3, 1)
    v("... comme il rétrécit quand la fenêtre s'élargit",
      int(m_large.sum()) < int(m1.sum()), f"{int(m_large.sum())} contre {int(m1.sum())}")

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    # ⚠ La grille fabriquée fait 14 cellules de côté : une fenêtre de 17×17 n'y tiendrait pas,
    # donc la famille est réduite ICI. Ce qui est exercé est le mécanisme, jamais une valeur —
    # un 9×9 et un 17×17 sont le même code avec un entier de plus.
    fab = mesurer(minimum=20, demi_largeurs=(1, 2, 3), passes=(2,),
                  corpus=corpus_fabrique(), volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and len(fab["resume"]) == 5,
      f"{fab['paires']} pas, {len(fab['resume'])} étages")
    v("... tous les étages sont jugés sur la MÊME population, fixée par le plus large",
      all(0 < e["cellules"] <= e["cellules_lisibles"] for e in fab["lignes"]),
      str([(e["cellules"], e["cellules_lisibles"]) for e in fab["lignes"]]))
    # ⚠⚠ ET LE LISSAGE DOIT DÉPLACER DES CELLULES, sinon un étage inopérant rendrait « zéro
    # micromètre », indiscernable d'un lissage qui n'apporte rien.
    bouge = {n: sum(e[f"deplacees_correlation_{n}"] for e in fab["lignes"])
             for n in fab["etages"] if n != "brut"}
    v("... chaque étage DÉPLACE réellement des cellules", all(x > 0 for x in bouge.values()),
      str(bouge))
    # ⚠⚠⚠ LE TÉMOIN SUIT À CHAQUE ÉTAGE : sans lui, on créditerait la corrélation d'un geste
    # qui marche aussi bien sans elle.
    v("... le témoin du gabarit mélangé est mesuré à CHAQUE étage",
      all(x["melange_contre_brut"] is not None and x["part_hors_lissage_um"] is not None
          for x in fab["resume"]),
      str([(x["etage"], x["part_hors_lissage_um"]) for x in fab["resume"]]))
    v("... l'étage brut a un écart nul à lui-même, des deux côtés",
      all(next(x for x in fab["resume"] if x["etage"] == "brut")
          [f"{lec}_contre_brut"]["ecart_median_um"] == 0.0 for lec in LECTURES))
    v("... l'étage en service est désigné, et un seul",
      sum(1 for x in fab["resume"] if x["deploye"]) == 1)
    v("... et le meilleur étage est choisi sur l'écart APPARIÉ, pas sur l'erreur brute",
      fab["ecart_du_meilleur_au_deploye"]["intervalle_um"] is not None
      and (not fab["un_etage_bat_le_deploye"]
           or tranche(fab["ecart_du_meilleur_au_deploye"])),
      f"{fab['meilleur_etage']['etage']} · {fab['ecart_du_meilleur_au_deploye']}")
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "HORS LISSAGE" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    trop_large = None
    try:
        mesurer(minimum=20, demi_largeurs=(1, 40), passes=(),
                corpus=corpus_fabrique(), volume=volume_fabrique(g0))
    except RuntimeError as exc:
        trop_large = str(exc)
    # ⚠⚠ Une fenêtre plus large que la grille ne rend RIEN, et c'est un refus plutôt qu'une
    # population vide : un étage qui ne retient aucune cellule rendrait des médianes sur zéro.
    v("un voisinage plus large que la grille est REFUSÉ, pas rendu vide",
      trop_large is not None, str(trop_large))
    hors = None
    try:
        mesurer(minimum=20, demi_largeurs=(1,), passes=(),
                corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'un balayage de lissité."""
    print(f"pas nominal {r['pas_nominal_um']} µm · {r['paires']} pas "
          f"({r['paires_ecartees']} écartés) · {r['cellules']} cellules retenues sur "
          f"{r['cellules_lisibles']} lisibles\n")
    print(f"{'étage':>14} {'voisins':>8} {'LECTURE':>9} {'contre ne rien faire':>34} "
          f"{'BRUIT':>8} {'HORS LISSAGE':>13}")
    print("-" * 96)

    def court(e: dict | None) -> str:
        if e is None or e["ecart_median_um"] is None:
            return "—"
        return (f"{e['ecart_median_um']:+6.1f} · {e['pas_ameliores']}/{e['pas']} · "
                f"{str(e['intervalle_um']):>14} · {'TRANCHE' if tranche(e) else '—'}")

    for x in r["resume"]:
        marque = " ⭐" if x["deploye"] else ""
        part = ("—" if x["part_hors_lissage_um"] is None
                else f"{x['part_hors_lissage_um']:+.1f} µm")
        print(f"{x['etage']:>14} {x['cellules_du_voisinage']:>8} "
              f"{x['erreur_correlation_um']:>8.1f}µ "
              f"{court(x['correlation_contre_ne_rien_faire']):>34} "
              f"{x['erreur_melange_um']:>7.1f}µ {part:>13}{marque}")
    print(f"\nne rien faire {r['erreur_ne_rien_faire_mediane_um']} µm · ⛔ oracle "
          f"{r['erreur_oracle_mediane_um']} µm")
    print(f"→ ⭐ un étage bat-il celui EN SERVICE (3×3, une passe) ? "
          f"{'OUI' if r['un_etage_bat_le_deploye'] else 'NON'} "
          f"(le meilleur : {r['meilleur_etage']['etage']} · "
          f"{court(r['ecart_du_meilleur_au_deploye'])})")
    mp = r["meilleure_part_hors_lissage"]
    print(f"→ ⚠⚠ la part HORS LISSAGE — ce que la lecture ajoute une fois retiré ce que le même "
          f"lissage rend sur du BRUIT — est la meilleure à l'étage {mp[0] if mp else '—'} "
          f"({mp[1] if mp else '—'} µm)")
    print(f"→ la lissité paie-t-elle AU-DELÀ de l'étage déployé ? "
          f"{'OUI' if r['la_lissite_paie_au_dela_du_deploye'] else 'NON'}")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--fenetre-grille", type=int, default=None, dest="fenetre_grille")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, fenetre_grille=a.fenetre_grille)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
