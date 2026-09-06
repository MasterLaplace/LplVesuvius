#!/usr/bin/env python3
"""L'oracle est une borne — mais en reste-t-il quelque chose à prendre ?

⚠⚠⚠ POURQUOI CE FICHIER VIENT AVANT LA PROCHAINE IDÉE DE LECTURE. Quatre portes se sont fermées
sur la lecture — la forme cherchée, l'endroit où on l'apprend, l'amplitude de ce qu'elle choisit,
la lissité qu'on lui applique — et l'écart au chemin déployé vaut toujours ~16 µm. Avant de
dépenser une cinquième tranche à « lire mieux », il faut demander si cet écart est **prenable**.

⭐⭐⭐ LA QUESTION EST SUR L'ORACLE, PAS SUR LA MÉTHODE. L'oracle choisit, par cellule, le décalage
qui minimise vraiment la distance à la spire d'arrivée — mais il choisit **le long de la normale**
et **dans une fenêtre**, sur une **grille d'un voxel**. Ses 20 µm résiduels se décomposent donc :

- ce que la **grille d'un voxel** coûte — un affinage le rendrait ;
- ce que la **fenêtre** coûte — une fenêtre plus large le rendrait ;
- ⭐ ce que **le rayon** coûte : la distance à laquelle la normale passe de la feuille visée.
  **Aucun décalage le long de la normale ne peut descendre sous celle-là.** Ce n'est plus une
  affaire de lecture, c'est une affaire de direction.

⚠⚠ ET UNE SECONDE QUESTION, QUI DÉCIDE SI UNE MÉTHODE POURRAIT SEULEMENT L'APPROCHER : le champ
de décalages de l'oracle est-il **lisse** sur la feuille ? Une méthode qui lit le volume et lisse
son résultat ne peut atteindre qu'un champ lisse. Si celui de l'oracle est rugueux, une part de
son avance n'est pas de l'information sur la feuille mais du bruit du nuage de référence —
c'est-à-dire une avance que rien ne peut prendre.

⚠ La comparaison de rugosité porte un témoin : le champ **mélangé**, qui est du bruit pur. Un
champ dont la rugosité vaut celle du mélange ne porte aucune structure spatiale.

Usage :
    uv run python src/nappe/loracle_est_il_atteignable.py --verifier
    uv run python src/nappe/loracle_est_il_atteignable.py --cote 960 \\
        --json docs/mesures/loracle_est_il_atteignable.json
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
from le_critere_du_raccrochage import (  # noqa: E402
    decalages_du_critere, parcourir_les_pas, poser_sur_la_grille,
)
from lecart_apparie import ecart_apparie, tranche  # noqa: E402

# ⚠⚠ Le pas fin est un QUART de voxel, et c'est dérivé : `decalage_retenu` affine par parabole
# et ne peut déplacer un décalage que d'un pas de grille, donc un quart de voxel est déjà quatre
# fois plus fin que ce qu'une méthode peut viser. Descendre en dessous rendrait des chiffres que
# la mesure ne porte pas.
PAS_FIN = 0.25
# ⚠ Le rayon est balayé sur une feuille et demie de part et d'autre : au-delà, le minimum trouvé
# est celui d'une AUTRE feuille, donc ce n'est plus la distance du rayon à la feuille visée mais
# la distance du rayon au rouleau. Une borne sur la mauvaise chose.
RAYON_EN_FEUILLES = 1.5


def meilleur_le_long(P: np.ndarray, D: np.ndarray, decalages: np.ndarray, arbre,
                     voxel_um: float) -> tuple[np.ndarray, np.ndarray]:
    """Le décalage qui minimise la distance, sur la grille de décalages donnée.

    ⚠ La table est construite décalage par décalage plutôt qu'en un bloc : à mille décalages et
    des milliers de cellules, la matrice complète tiendrait des gigaoctets pour un argmin qui se
    calcule au fil de l'eau.
    """
    best_t = np.full(len(P), np.nan)
    best_e = np.full(len(P), np.inf)
    for t in decalages:
        e = arbre.query(P + t * D, k=1)[0] * voxel_um
        mieux = e < best_e
        best_e[mieux] = e[mieux]
        best_t[mieux] = t
    return best_t, best_e


def rugosite(champ: np.ndarray, valide: np.ndarray) -> float | None:
    """De combien un décalage s'écarte de la médiane de son voisinage de grille, en médiane.

    ⚠⚠ C'EST LA GRANDEUR QUI DIT SI UNE MÉTHODE POURRAIT SEULEMENT APPROCHER CE CHAMP. Une
    méthode qui lit le volume puis lisse ne peut produire qu'un champ lisse ; un champ dont
    chaque cellule s'écarte fortement de ses voisines n'est donc pas atteignable par cette
    voie, quelle que soit la qualité de la lecture.

    ⚠ Elle se lit toujours contre un témoin : un champ de bruit a une rugosité, et c'est elle
    l'échelle. Rendre ce nombre seul le laisserait interpréter comme « beaucoup » ou « peu »
    selon l'humeur.
    """
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    lisse, assez = accorder_les_voisins(champ, valide)
    garde = assez & valide & np.isfinite(champ) & np.isfinite(lisse)
    if int(garde.sum()) < 3:
        return None
    return round(float(np.median(np.abs(champ[garde] - lisse[garde]))), 2)


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, fenetre_grille: int | None = None,
            corpus: dict | None = None, volume=None) -> dict:
    """Ce que valent la grille, la fenêtre et le rayon dans les 20 µm de l'oracle."""
    from le_raccrochage_a_la_matiere import accorder_les_voisins  # noqa: PLC0415

    pas = parcourir_les_pas(graine, minimum, cache_actif, cote, fenetre_grille, corpus, volume)
    reglage = next(pas)
    voxel_um = reglage["voxel_um"]
    demi_vx = reglage["pas_vx"] / 2.0
    lignes: list[dict] = []
    for ctx in pas:
        centres = ctx["centres"]
        pris = ctx["garde_dans_lisible"]
        P, D = ctx["P"], ctx["D"]
        arbre = ctx["arbre"]
        # --- les trois grilles de décalages, emboîtées ---
        fine = np.arange(centres.min(), centres.max() + 1e-9, PAS_FIN)
        large = np.arange(-RAYON_EN_FEUILLES * reglage["pas_vx"],
                          RAYON_EN_FEUILLES * reglage["pas_vx"] + 1e-9, PAS_FIN)
        t_grille, e_grille = meilleur_le_long(P, D, centres, arbre, voxel_um)
        _, e_fine = meilleur_le_long(P, D, fine, arbre, voxel_um)
        _, e_rayon = meilleur_le_long(P, D, large, arbre, voxel_um)
        # --- le raccrochage déployé, pour situer ce qui reste ---
        brut = decalages_du_critere("correlation", ctx["corr"], ctx["corr_melange"],
                                    centres, ctx["L"], ctx["t_fenetre"])
        melange = decalages_du_critere("melange", ctx["corr"], ctx["corr_melange"],
                                       centres, ctx["L"], ctx["t_fenetre"])
        grille_racc = poser_sur_la_grille(brut, ctx["lisible"], ctx["lisible"].shape)
        acc, _ = accorder_les_voisins(grille_racc, ctx["lisible"])
        plat = acc[ctx["ou_lisible"][:, 0], ctx["ou_lisible"][:, 1]]
        deploye = np.where(np.isnan(plat), brut, plat)
        # ⭐⭐ ET L'ORACLE LISSÉ : si le lisser ne coûte presque rien, son champ est lisse, donc
        # une méthode qui lit puis lisse pourrait en principe l'approcher.
        grille_o = poser_sur_la_grille(t_grille, ctx["lisible"], ctx["lisible"].shape)
        acc_o, _ = accorder_les_voisins(grille_o, ctx["lisible"])
        plat_o = acc_o[ctx["ou_lisible"][:, 0], ctx["ou_lisible"][:, 1]]
        oracle_lisse = np.where(np.isnan(plat_o), t_grille, plat_o)

        def med(v):
            return round(float(np.median(v[pris])), 1)

        entree = dict(
            de=ctx["de"], vers=ctx["vers"], cellules=int(ctx["assez"].sum()),
            cellules_lisibles=int(ctx["lisible"].sum()),
            decalages_essayes=dict(fenetre=len(centres), fine=len(fine), rayon=len(large)),
            erreur_ne_rien_faire_um=med(ctx["erreur"](np.zeros(len(P)), pris)[1]
                                        if False else
                                        arbre.query(P, k=1)[0] * voxel_um),
            erreur_deploye_um=ctx["erreur"](deploye, pris)[0],
            erreur_oracle_um=med(e_grille),
            erreur_oracle_fine_um=med(e_fine),
            erreur_rayon_um=med(e_rayon),
            erreur_oracle_lisse_um=ctx["erreur"](oracle_lisse, pris)[0],
            rugosite_oracle_vx=rugosite(grille_o, ctx["lisible"]),
            rugosite_raccrochage_vx=rugosite(grille_racc, ctx["lisible"]),
            rugosite_melange_vx=rugosite(
                poser_sur_la_grille(melange, ctx["lisible"], ctx["lisible"].shape),
                ctx["lisible"]),
            bits_de_supervision=1)
        entree["erreur_deploye_um"] = round(entree["erreur_deploye_um"], 1)
        entree["erreur_oracle_lisse_um"] = round(entree["erreur_oracle_lisse_um"], 1)
        lignes.append(entree)

    if not lignes:
        raise RuntimeError("aucun pas ne rend un voisinage de grille dans la boîte")

    vol = reglage["vol"]
    r = dict(
        fragment="PHerc0500P2", volume=reglage["volume"], voxel_um=voxel_um,
        boite=reglage["boite"], pas_nominal_um=reglage["ecart_um"],
        demi_epaisseur_um=round(reglage["ecart_um"] / 2, 2),
        pas_fin_vx=PAS_FIN, rayon_en_feuilles=RAYON_EN_FEUILLES,
        demi_fenetre_vx=round(demi_vx, 2),
        paires=len(lignes), paires_ecartees=int(reglage["ecartees"]),
        cellules=int(sum(e["cellules"] for e in lignes)), lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises))

    def par_pas(cle: str) -> list[float]:
        return [e[cle] for e in lignes]

    for cle in ("ne_rien_faire", "deploye", "oracle", "oracle_fine", "rayon", "oracle_lisse"):
        r[f"erreur_{cle}_mediane_um"] = round(
            float(np.median(par_pas(f"erreur_{cle}_um"))), 1)
    # ⭐⭐⭐ LA DÉCOMPOSITION, ET CHAQUE TERME EST UN ÉCART APPARIÉ. La dispersion entre pas vaut
    # quatre fois celle entre méthodes sur cette matière : une différence de médianes s'y ferait
    # décider par le tirage des pas.
    r["ce_que_coute_la_grille"] = ecart_apparie(
        par_pas("erreur_oracle_fine_um"), par_pas("erreur_oracle_um"))
    r["ce_que_coute_la_fenetre"] = ecart_apparie(
        par_pas("erreur_rayon_um"), par_pas("erreur_oracle_fine_um"))
    # ⭐ CE QUE LE RAYON LAISSE : la distance à laquelle la normale passe de la feuille visée.
    # Aucun décalage le long de cette normale ne descend sous ce nombre.
    r["ce_qui_reste_au_deploye"] = ecart_apparie(
        par_pas("erreur_rayon_um"), par_pas("erreur_deploye_um"))
    r["la_grille_coute_quelque_chose"] = tranche(r["ce_que_coute_la_grille"])
    r["la_fenetre_coute_quelque_chose"] = tranche(r["ce_que_coute_la_fenetre"])
    # ⚠⚠⚠ LA PART IRRÉDUCTIBLE LE LONG DE LA NORMALE, en fraction de ce qui sépare le chemin
    # déployé du fait de ne rien faire. Elle dit combien de l'écart restant n'est PAS une
    # affaire de lecture.
    reste = r["erreur_deploye_mediane_um"] - r["erreur_rayon_mediane_um"]
    r["ecart_du_deploye_au_rayon_um"] = round(reste, 1)
    r["part_du_rayon_dans_lerreur_deployee"] = (
        round(r["erreur_rayon_mediane_um"] / r["erreur_deploye_mediane_um"], 3)
        if r["erreur_deploye_mediane_um"] > 0 else None)
    # ⭐⭐ ET LA SECONDE QUESTION : le champ de l'oracle est-il LISSE, donc approchable par une
    # méthode qui lit puis lisse ?
    r["lisser_loracle_coute"] = ecart_apparie(
        par_pas("erreur_oracle_lisse_um"), par_pas("erreur_oracle_um"))
    # ⚠⚠⚠ PAS DE BOOLÉEN « LE CHAMP EST LISSE » ICI, ET C'EST UNE CORRECTION. Ma première
    # version le tirait de `tranche(oracle − oracle lissé)` : le lissage coûte 0,2 µm de façon
    # parfaitement consistante, donc le verdict répondait NON — pendant que la rugosité mesurée
    # du même champ valait ZÉRO. `tranche` répond « y a-t-il une différence consistante », pas
    # « est-elle grande » : deux nombres publiés côte à côte se contredisaient. Ce qui se compare
    # sans seuil, c'est la rugosité du champ de l'oracle À CELLE du raccrochage et du bruit.
    for cle in ("oracle", "raccrochage", "melange"):
        vals = [e[f"rugosite_{cle}_vx"] for e in lignes if e[f"rugosite_{cle}_vx"] is not None]
        r[f"rugosite_{cle}_mediane_vx"] = (round(float(np.median(vals)), 2) if vals else None)
    # ⚠ La rugosité se lit contre celle du MÉLANGE, qui est du bruit pur : c'est elle l'échelle.
    # ⭐⭐⭐ LA COMPARAISON QUI DÉCIDE, ET ELLE N'A PAS DE SEUIL : le champ que devrait produire
    # une méthode parfaite est-il plus lisse ou plus rugueux que celui qu'elle produit ? Si le
    # vrai champ est lisse et que le nôtre approche la rugosité du bruit, ce qui manque n'est
    # pas une meilleure forme mais un champ lisse PAR CONSTRUCTION.
    r["loracle_est_plus_lisse_que_le_raccrochage"] = bool(
        r["rugosite_oracle_mediane_vx"] is not None
        and r["rugosite_raccrochage_mediane_vx"] is not None
        and r["rugosite_oracle_mediane_vx"] < r["rugosite_raccrochage_mediane_vx"])
    r["part_de_bruit_dans_le_raccrochage"] = (
        round(r["rugosite_raccrochage_mediane_vx"] / r["rugosite_melange_mediane_vx"], 3)
        if r["rugosite_melange_mediane_vx"] else None)
    r["loracle_est_plus_lisse_que_le_bruit"] = bool(
        r["rugosite_oracle_mediane_vx"] is not None
        and r["rugosite_melange_mediane_vx"] is not None
        and r["rugosite_oracle_mediane_vx"] < r["rugosite_melange_mediane_vx"])
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from scipy.spatial import cKDTree  # noqa: PLC0415

    # --- le balayage le long d'un rayon ---
    P = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    D = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    cible = np.array([[0.0, 0.0, 3.0], [10.0, 5.0, -2.0]])
    arbre = cKDTree(cible)
    t, e = meilleur_le_long(P, D, np.arange(-5.0, 5.1, 1.0), arbre, 1.0)
    v("le balayage trouve le décalage qui annule vraiment la distance",
      t[0] == 3.0 and abs(e[0]) < 1e-9, f"{t.tolist()} · {e.round(2).tolist()}")
    # ⚠⚠⚠ LE FAIT QUE TOUTE CETTE TRANCHE EXISTE POUR MESURER : une cible que le rayon ne
    # traverse pas laisse une distance IRRÉDUCTIBLE, quel que soit le décalage. Ici la seconde
    # cible est à cinq unités de côté du rayon, et aucun décalage ne descend sous cinq.
    v("... et une cible hors du rayon laisse une distance qu'AUCUN décalage ne prend",
      abs(e[1] - 5.0) < 1e-9, str(round(float(e[1]), 3)))
    # ⚠ Une grille plus fine ne peut jamais faire PIRE : c'est un minimum sur un sur-ensemble.
    _, e_fin = meilleur_le_long(P, D, np.arange(-5.0, 5.01, 0.25), arbre, 1.0)
    v("... une grille plus fine ne fait jamais pire", bool(np.all(e_fin <= e + 1e-12)))

    # --- la rugosité ---
    lisse = np.tile(np.arange(7.0), (7, 1))
    ok = np.ones((7, 7), dtype=bool)
    rugueux = lisse.copy()
    rugueux[::2, ::2] += 9.0
    # ⚠⚠ LA RUGOSITÉ SE LIT PAR SON ORDRE, PAS PAR UN SEUIL. Ma première version exigeait
    # « plus de 1,0 » sur un damier ; la mesure a rendu exactement 1,0, et le seuil aurait été
    # un nombre choisi pour que le cas du jour passe. Ce qui est vrai et vérifiable, c'est
    # l'ORDRE : une rampe est plus lisse qu'un damier, qui est plus lisse que du bruit.
    bruit = np.random.default_rng(3).normal(0.0, 9.0, (7, 7))
    trois = (rugosite(lisse, ok), rugosite(rugueux, ok), rugosite(bruit, ok))
    v("la rugosité ordonne une rampe, un damier et du bruit, dans cet ordre",
      trois[0] < trois[1] < trois[2], str(trois))
    v("... et une rampe parfaitement lisse en a une nulle", trois[0] == 0.0, str(trois[0]))
    v("... un champ trop petit ne rend pas de rugosité",
      rugosite(np.zeros((2, 2)), np.ones((2, 2), dtype=bool)) is None)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(minimum=20, corpus=corpus_fabrique(), volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and fab["cellules"] > 0,
      f"{fab['paires']} pas, {fab['cellules']} cellules")
    # ⚠⚠⚠ LES TROIS BORNES SONT EMBOÎTÉES PAR CONSTRUCTION, et le vérifier attrape une grille
    # mal construite : la fine contient celle d'un voxel, et le rayon contient la fine.
    ordre = [(e["de"], e["erreur_oracle_um"], e["erreur_oracle_fine_um"], e["erreur_rayon_um"])
             for e in fab["lignes"]
             if not (e["erreur_rayon_um"] <= e["erreur_oracle_fine_um"] + 0.05
                     <= e["erreur_oracle_um"] + 0.1)]
    v("... les trois bornes sont EMBOÎTÉES : rayon ≤ fine ≤ grille d'un voxel",
      not ordre, str(ordre[:3]))
    v("... et la fenêtre fine est bien plus fine, le rayon bien plus large",
      all(e["decalages_essayes"]["fine"] > e["decalages_essayes"]["fenetre"]
          and e["decalages_essayes"]["rayon"] > e["decalages_essayes"]["fine"]
          for e in fab["lignes"]),
      str(fab["lignes"][0]["decalages_essayes"]))
    # ⚠ Le déployé ne peut pas battre le rayon : il choisit dans une fenêtre plus étroite, sur
    # une grille plus grossière, et sans regarder la cible.
    v("... et le chemin déployé ne descend jamais sous le rayon",
      all(e["erreur_deploye_um"] >= e["erreur_rayon_um"] - fab["voxel_um"]
          for e in fab["lignes"]),
      str([(e["erreur_deploye_um"], e["erreur_rayon_um"]) for e in fab["lignes"]][:3]))
    v("... les trois rugosités sont rendues, celle du témoin comprise",
      all(fab[f"rugosite_{c}_mediane_vx"] is not None
          for c in ("oracle", "raccrochage", "melange")),
      f"oracle {fab['rugosite_oracle_mediane_vx']} · raccrochage "
      f"{fab['rugosite_raccrochage_mediane_vx']} · mélange "
      f"{fab['rugosite_melange_mediane_vx']}")
    # ⚠⚠ LA DÉCOMPOSITION PASSE PAR L'ÉCART APPARIÉ, comme tout le reste de la famille.
    # ⚠⚠⚠ LE CONTRÔLE QUI EXISTE PARCE QUE DEUX NOMBRES PUBLIÉS SE CONTREDISAIENT. Un champ
    # dont la rugosité mesurée est nulle ne peut pas être annoncé « non lisse » ; `tranche`
    # répond « y a-t-il une différence consistante », jamais « est-elle grande ».
    v("... la rugosité et le coût du lissage ne se contredisent pas",
      fab["rugosite_oracle_mediane_vx"] is None
      or fab["rugosite_raccrochage_mediane_vx"] is None
      or (fab["loracle_est_plus_lisse_que_le_raccrochage"]
          == (fab["rugosite_oracle_mediane_vx"]
              < fab["rugosite_raccrochage_mediane_vx"])),
      f"oracle {fab['rugosite_oracle_mediane_vx']} · raccrochage "
      f"{fab['rugosite_raccrochage_mediane_vx']}")
    v("... et aucun verdict n'est tiré d'un `tranche` sur une différence minuscule",
      "le_champ_de_loracle_est_lisse" not in fab)
    v("... et chaque terme de la décomposition porte son intervalle",
      all(fab[c]["intervalle_um"] is not None for c in
          ("ce_que_coute_la_grille", "ce_que_coute_la_fenetre", "ce_qui_reste_au_deploye",
           "lisser_loracle_coute")))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "RAYON" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une décomposition de la borne."""
    print(f"pas nominal {r['pas_nominal_um']} µm · {r['paires']} pas · {r['cellules']} "
          f"cellules · pas fin {r['pas_fin_vx']} vx · rayon ±{r['rayon_en_feuilles']} feuille\n")
    for nom, cle in (("ne rien faire", "ne_rien_faire"),
                     ("chemin DÉPLOYÉ", "deploye"),
                     ("oracle, grille d'un voxel", "oracle"),
                     ("oracle, grille fine", "oracle_fine"),
                     ("⭐ le RAYON, tout décalage confondu", "rayon")):
        print(f"{nom:>34} {r[f'erreur_{cle}_mediane_um']:>7.1f} µm")

    def court(e) -> str:
        return (f"{e['ecart_median_um']:+6.1f} µm · {e['pas_ameliores']}/{e['pas']} · "
                f"{str(e['intervalle_um']):>14} · {'TRANCHE' if tranche(e) else '—'}")

    print(f"\nce que coûte la GRILLE d'un voxel : {court(r['ce_que_coute_la_grille'])}")
    print(f"ce que coûte la FENÊTRE           : {court(r['ce_que_coute_la_fenetre'])}")
    print(f"ce qui reste au chemin déployé    : {court(r['ce_qui_reste_au_deploye'])}")
    print(f"\n→ ⭐⭐⭐ la part IRRÉDUCTIBLE le long de la normale vaut "
          f"{r['erreur_rayon_mediane_um']} µm, soit "
          f"{r['part_du_rayon_dans_lerreur_deployee']} de l'erreur du chemin déployé — ce qui "
          f"reste à prendre par la LECTURE est l'écart apparié ci-dessus, "
          f"{-r['ce_qui_reste_au_deploye']['ecart_median_um']:.1f} µm "
          f"(la simple différence des médianes en dirait "
          f"{r['ecart_du_deploye_au_rayon_um']}, et ce n'est pas la même quantité)")
    print(f"→ la grille d'un voxel coûte-t-elle quelque chose ? "
          f"{'OUI' if r['la_grille_coute_quelque_chose'] else 'NON'} · la fenêtre ? "
          f"{'OUI' if r['la_fenetre_coute_quelque_chose'] else 'NON'}")
    print(f"→ ⭐⭐ rugosités : oracle {r['rugosite_oracle_mediane_vx']} vx · raccrochage "
          f"{r['rugosite_raccrochage_mediane_vx']} · témoin mélangé "
          f"{r['rugosite_melange_mediane_vx']} — le raccrochage est à "
          f"{r['part_de_bruit_dans_le_raccrochage']} de la rugosité du BRUIT, là où le vrai "
          f"champ est parfaitement lisse")
    print(f"→ le champ de l'oracle est plus lisse que celui du raccrochage : "
          f"{'OUI' if r['loracle_est_plus_lisse_que_le_raccrochage'] else 'NON'} · plus lisse "
          f"que le bruit : {'OUI' if r['loracle_est_plus_lisse_que_le_bruit'] else 'NON'} "
          f"· le lisser coûte {court(r['lisser_loracle_coute'])}")
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
