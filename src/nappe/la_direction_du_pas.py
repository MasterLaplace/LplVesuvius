#!/usr/bin/env python3
"""La direction du pas : le plancher de 18 µm est-il mou ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL EST RENDU NÉCESSAIRE PAR UNE MESURE. `loracle_est_il_atteignable`
a montré que **48,5 %** de ce que coûte un pas est un **plancher** : la distance à laquelle la
normale passe de la feuille visée, qu'aucun décalage le long de cette normale ne prend. Seule une
autre **direction** la prendrait. Or le seul chiffre que la campagne ait sur la direction — « la
rotation ne vaut que 3 % » de `le_cout_dun_seul_pas` — a été rendu par l'instrument **non
apparié** que la rétraction du registre a invalidé, et sur une autre population.

⭐⭐ CE FICHIER LE REFAIT, AVEC LES INSTRUMENTS DE LA FAMILLE : même population que le plancher,
écart **apparié** avec son intervalle, et la distinction qui a déjà servi deux fois — une rotation
**d'ensemble**, qui est un biais qu'on peut corriger en production, contre une rotation **par
cellule**, qui est une borne parce qu'elle regarde la cible.

⚠⚠ ET LE CÔNE N'EST PAS CHOISI, IL EST BALAYÉ. Fixer un demi-angle ferait publier « la rotation
vaut tant » pour un nombre qu'on aurait posé soi-même ; la mesure rend donc une **courbe** — ce
que tel demi-angle achète — et le pas angulaire est dérivé : c'est la rotation qui déplace le
point d'arrivée d'**un voxel**, exactement comme la grille des décalages.

⚠ La rotation d'ensemble est ajustée **hors échantillon**, chaque pas jugé à l'angle que les
**autres** pas ont préféré : trois cents rotations essayées sur les pas qui les jugent
garantissent qu'une tombe bien.

Usage :
    uv run python src/nappe/la_direction_du_pas.py --verifier
    uv run python src/nappe/la_direction_du_pas.py --cote 960 \\
        --json docs/mesures/la_direction_du_pas.json
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
from le_cout_dun_seul_pas import rotations_essayees, tourner  # noqa: E402
from le_critere_du_raccrochage import parcourir_les_pas, poser_sur_la_grille  # noqa: E402
from lecart_apparie import (  # noqa: E402
    choisir_hors_echantillon, ecart_apparie, tranche,
)
from loracle_est_il_atteignable import meilleur_le_long, rugosite  # noqa: E402

# ⚠ Les demi-angles balayés sont des multiples du pas angulaire, qui double : le cône le plus
# étroit est un pas, le plus large en vaut huit. Ce sont des SOUS-ENSEMBLES emboîtés d'une même
# grille, donc les comparer ne compare jamais deux grilles.
MULTIPLES_DU_CONE = (1, 2, 4, 8)


def pas_angulaire_deg(pas_vx: float) -> float:
    """La rotation qui déplace le point d'arrivée d'exactement un voxel, en degrés.

    ⚠⚠ C'EST LA MÊME DÉRIVATION QUE LA GRILLE DES DÉCALAGES, et pas une analogie : un voxel est
    la résolution à laquelle la matière est échantillonnée, donc c'est la plus petite rotation
    dont l'effet soit distinguable. En essayer de plus fines rendrait des chiffres que la donnée
    ne porte pas ; en essayer de plus grosses sauterait par-dessus l'optimum.
    """
    if pas_vx <= 1.0:
        raise ValueError(f"un pas de {pas_vx} voxels ne permet aucune rotation mesurable")
    return float(np.degrees(np.arcsin(1.0 / pas_vx)))


def cones_emboites(pas_deg: float, multiples=MULTIPLES_DU_CONE) -> list[float]:
    """Les demi-angles balayés, en degrés — des multiples du pas angulaire."""
    return [round(pas_deg * m, 4) for m in multiples]


def dans_le_cone(angles: np.ndarray, demi_angle_deg: float) -> np.ndarray:
    """Quelles rotations de la grille tiennent dans ce demi-angle.

    ⚠ Le cône est ROND, pas carré : `rotations_essayees` rend le produit de deux axes, donc ses
    coins sont à √2 fois le demi-angle. Les garder ferait qu'un « cône de 4° » contiendrait des
    rotations de 5,6°, et la courbe publiée porterait sur autre chose que son abscisse.
    """
    return np.hypot(angles[:, 0], angles[:, 1]) <= demi_angle_deg + 1e-9


def mesurer(graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, fenetre_grille: int | None = None,
            multiples=MULTIPLES_DU_CONE, corpus: dict | None = None, volume=None) -> dict:
    """Ce qu'une rotation achète, d'ensemble puis par cellule, en fonction du cône."""
    pas = parcourir_les_pas(graine, minimum, cache_actif, cote, fenetre_grille, corpus, volume)
    reglage = next(pas)
    voxel_um = reglage["voxel_um"]
    pas_deg = pas_angulaire_deg(reglage["pas_vx"])
    demi_angles = cones_emboites(pas_deg, multiples)
    angles = rotations_essayees(max(demi_angles), pas_deg)
    masques = {d: dans_le_cone(angles, d) for d in demi_angles}
    # ⚠⚠ Le zéro doit être dans la grille : sans lui, « tourner améliore » se comparerait à la
    # rotation la plus proche de zéro plutôt qu'à l'absence de rotation.
    i_zero = int(np.argmin(np.hypot(angles[:, 0], angles[:, 1])))
    if not np.allclose(angles[i_zero], 0.0):
        raise RuntimeError("la grille de rotations ne contient pas l'absence de rotation")

    lignes: list[dict] = []
    courbes: list[np.ndarray] = []
    for ctx in pas:
        pris = ctx["garde_dans_lisible"]
        P, D0, arbre = ctx["P"], ctx["D"], ctx["arbre"]
        centres = ctx["centres"]
        # ⚠ La table complète (rotations × cellules) tiendrait en mémoire, mais seules deux
        # réductions en sortent : le minimum PAR CELLULE dans chaque cône, et la médiane PAR
        # ROTATION. Elles s'accumulent au fil de l'eau.
        meilleur_par_cone = {d: np.full(len(P), np.inf) for d in demi_angles}
        medianes = np.empty(len(angles))
        argmin_cone = np.zeros(len(P), dtype=int)
        large = max(demi_angles)
        for k, (a, b) in enumerate(angles):
            D = tourner(D0, float(a), float(b))
            _, e = meilleur_le_long(P, D, centres, arbre, voxel_um)
            medianes[k] = float(np.median(e[pris]))
            for d in demi_angles:
                if masques[d][k]:
                    mieux = e < meilleur_par_cone[d]
                    meilleur_par_cone[d][mieux] = e[mieux]
                    if d == large:
                        argmin_cone[mieux] = k
        courbes.append(medianes)
        entree = dict(de=ctx["de"], vers=ctx["vers"], cellules=int(ctx["assez"].sum()),
                      cellules_lisibles=int(ctx["lisible"].sum()),
                      rotations=int(len(angles)), bits_de_supervision=1)
        entree["erreur_sans_rotation_um"] = round(float(medianes[i_zero]), 1)
        for d in demi_angles:
            entree[f"erreur_oracle_{d}_um"] = round(
                float(np.median(meilleur_par_cone[d][pris])), 1)
            entree[f"erreur_meilleure_globale_{d}_um"] = round(
                float(np.min(medianes[masques[d]])), 1)
        # ⭐⭐ LA RUGOSITÉ DU CHAMP DE ROTATIONS : une correction de direction par cellule n'est
        # exploitable que si elle varie doucement d'une cellule à l'autre. Si elle saute d'un
        # cône entier entre voisines, ce n'est pas une correction, c'est du bruit.
        # ⚠⚠⚠ ET SON ÉTENDUE À CÔTÉ DE SA RUGOSITÉ, parce que les deux ensemble disent une
        # chose qu'aucune ne dit seule. Un champ de rugosité nulle peut être CONSTANT — et
        # alors une rotation d'ensemble le capture entièrement — ou LENTEMENT VARIABLE, et
        # alors elle n'en capture rien. Publier la seule rugosité laisserait supposer la
        # première lecture, qui est la plus naturelle et pas forcément la vraie.
        for axe, colonne in (("alpha", 0), ("beta", 1)):
            valeurs = angles[argmin_cone, colonne]
            champ = poser_sur_la_grille(valeurs, ctx["lisible"], ctx["lisible"].shape)
            entree[f"rugosite_{axe}_deg"] = rugosite(champ, ctx["lisible"])
            q1, q3 = np.percentile(valeurs[pris], [25, 75])
            entree[f"etendue_{axe}_deg"] = round(float(q3 - q1), 2)
        # ⚠⚠⚠ COMBIEN DE CELLULES CHOISISSENT LE BORD DU CÔNE. C'est ce qui décide si le
        # « gain de l'oracle de direction » est une BORNE ou seulement un plancher de balayage :
        # un optimum qui sature au bord dit que le cône est trop petit, donc que la mesure ne
        # sait pas ce que la direction vaut — et publier son chiffre comme une borne serait
        # présenter la limite de la grille comme une limite de la matière.
        porte = np.hypot(angles[argmin_cone, 0], angles[argmin_cone, 1])
        entree["part_au_bord_du_cone"] = round(
            float(np.mean(porte[pris] >= large - pas_deg / 2.0)), 3)
        # ⚠⚠⚠ VERS OÙ LE CÔNE TIRE, ET C'EST LE DIAGNOSTIC QUI FERME LA QUESTION. Le point le
        # plus proche du nuage est ce que toute rotation non bornée finirait par viser ; savoir
        # **à quel angle** il se trouve dit si un cône plus large rattraperait un optimum ou
        # s'il ne ferait que converger vers « vise ce qui est le plus près ».
        # ⚠ Ce point n'est PAS la bonne correspondance : deux surfaces se correspondent par
        # leur paramétrage, jamais par leur proximité. Et la distance rendue ici est celle du
        # point d'ARRIVÉE au nuage — c'est-à-dire l'erreur de ne pas bouger, pas ce qu'une
        # direction libre obtiendrait, qui serait zéro pour une longueur libre.
        d_proche, i_proche = arbre.query(P, k=1)
        vers = ctx["cible"][i_proche] - P
        vers = vers / np.maximum(np.linalg.norm(vers, axis=1, keepdims=True), 1e-9)
        cos = np.clip(np.einsum("ij,ij->i", vers, D0), -1.0, 1.0)
        entree["angle_au_plus_proche_deg"] = round(
            float(np.median(np.degrees(np.arccos(np.abs(cos)))[pris])), 1)
        entree["distance_au_plus_proche_um"] = round(
            float(np.median(d_proche[pris] * voxel_um)), 1)
        lignes.append(entree)

    if not lignes:
        raise RuntimeError("aucun pas ne rend un voisinage de grille dans la boîte")

    vol = reglage["vol"]
    r = dict(
        fragment="PHerc0500P2", volume=reglage["volume"], voxel_um=voxel_um,
        boite=reglage["boite"], pas_nominal_um=reglage["ecart_um"],
        pas_angulaire_deg=round(pas_deg, 4), demi_angles_deg=demi_angles,
        rotations_essayees=int(len(angles)),
        paires=len(lignes), paires_ecartees=int(reglage["ecartees"]),
        cellules=int(sum(e["cellules"] for e in lignes)), lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises))

    def par_pas(cle: str) -> list[float]:
        return [e[cle] for e in lignes]

    r["erreur_sans_rotation_mediane_um"] = round(
        float(np.median(par_pas("erreur_sans_rotation_um"))), 1)
    resume = []
    for d in demi_angles:
        # ⭐ LA ROTATION D'ENSEMBLE, AJUSTÉE HORS ÉCHANTILLON : chaque pas est jugé à l'angle que
        # les AUTRES pas ont préféré. Sans ça, essayer trois cents rotations sur les pas qui les
        # jugent garantit qu'une tombe bien.
        restreintes = [c[masques[d]] for c in courbes]
        # ⚠⚠ CE QUI EST CHOISI EST UN INDICE, CE QUI EST PUBLIÉ EST UN ANGLE. Rendre l'indice
        # sous un nom qui dit « angles » ferait publier un nombre sans unité que rien ne
        # rattache à la grille — et il se lirait comme des degrés.
        angles_du_cone = angles[masques[d]]
        indices = np.arange(len(angles_du_cone), dtype=float)
        _, pris_i, couts = choisir_hors_echantillon(restreintes, indices)
        globale = ecart_apparie(couts, par_pas("erreur_sans_rotation_um")) if couts else None
        resume.append(dict(
            demi_angle_deg=d, rotations_dans_le_cone=int(masques[d].sum()),
            # ⛔ L'oracle de direction regarde la cible une fois par cellule : c'est une borne,
            # et le lire comme une méthode serait lire la réponse comme un remède.
            erreur_oracle_mediane_um=round(
                float(np.median(par_pas(f"erreur_oracle_{d}_um"))), 1),
            oracle_contre_sans_rotation=ecart_apparie(
                par_pas(f"erreur_oracle_{d}_um"), par_pas("erreur_sans_rotation_um")),
            erreur_globale_hors_echantillon_um=(round(float(np.median(couts)), 1)
                                                if couts else None),
            globale_contre_sans_rotation=globale,
            angles_retenus_deg=[[round(float(angles_du_cone[int(i)][0]), 2),
                                 round(float(angles_du_cone[int(i)][1]), 2)]
                                for i in pris_i]))
    r["resume"] = resume

    def trouver(d: float) -> dict:
        return next(x for x in resume if x["demi_angle_deg"] == d)

    large = trouver(max(demi_angles))
    r["cone_le_plus_large"] = large
    # ⭐⭐⭐ LES DEUX VERDICTS, ET ILS NE DISENT PAS LA MÊME CHOSE. Une rotation d'ensemble est un
    # remède disponible en production ; l'oracle de direction est une borne sur ce que TOUTE
    # correction de direction dans ce cône pourrait rendre.
    r["une_rotation_densemble_ameliore"] = bool(
        large["globale_contre_sans_rotation"] is not None
        and tranche(large["globale_contre_sans_rotation"]))
    r["le_plancher_est_mou"] = tranche(large["oracle_contre_sans_rotation"])
    r["gain_de_loracle_de_direction_um"] = large["oracle_contre_sans_rotation"]["ecart_median_um"]
    for axe in ("alpha", "beta"):
        vals = [e[f"rugosite_{axe}_deg"] for e in lignes if e[f"rugosite_{axe}_deg"] is not None]
        r[f"rugosite_{axe}_mediane_deg"] = round(float(np.median(vals)), 2) if vals else None
        r[f"etendue_{axe}_mediane_deg"] = round(
            float(np.median([e[f"etendue_{axe}_deg"] for e in lignes])), 2)
    # ⭐⭐ CE QUE LES DEUX ENSEMBLE TRANCHENT : un champ lisse ET étendu varie lentement à travers
    # la feuille, donc une rotation d'ensemble — une seule pour tout le pas — ne peut pas le
    # suivre. C'est la lecture qui explique qu'un oracle de direction prenne quelque chose là où
    # un biais global ne prend rien, et elle est mesurée plutôt que supposée.
    r["le_champ_de_rotation_varie_a_travers_la_feuille"] = bool(
        r["rugosite_alpha_mediane_deg"] is not None
        and max(r["etendue_alpha_mediane_deg"], r["etendue_beta_mediane_deg"])
        > max(r["rugosite_alpha_mediane_deg"], r["rugosite_beta_mediane_deg"]))
    # ⚠⚠ ET LA PART QUE LA ROTATION D'ENSEMBLE PREND DE CE QUE L'ORACLE PREND. Un `tranche` sur
    # un dixième de micromètre répond « oui » sans rien vouloir dire de grand : ce rapport est
    # ce qui empêche de le lire comme un remède.
    gain_g = (large["globale_contre_sans_rotation"]["ecart_median_um"]
              if large["globale_contre_sans_rotation"] else None)
    gain_o = large["oracle_contre_sans_rotation"]["ecart_median_um"]
    r["part_au_bord_du_cone"] = round(
        float(np.median([e["part_au_bord_du_cone"] for e in lignes])), 3)
    # ⚠⚠⚠ ET LE VERDICT QUI EN DÉPEND : tant qu'une part notable des cellules choisit le bord,
    # ce que l'oracle de direction prend est un PLANCHER, pas une borne. Le dire est la seule
    # façon d'empêcher que 2,9 µm se lise comme « voilà ce que la direction vaut ».
    r["loracle_de_direction_est_une_borne"] = bool(r["part_au_bord_du_cone"] < 0.5)
    r["angle_au_plus_proche_median_deg"] = round(
        float(np.median(par_pas("angle_au_plus_proche_deg"))), 1)
    r["distance_au_plus_proche_mediane_um"] = round(
        float(np.median(par_pas("distance_au_plus_proche_um"))), 1)
    # ⚠⚠⚠ ET LE VERDICT QUI FERME LA QUESTION PLUTÔT QUE DE LA LAISSER OUVERTE SUR UN CÔNE PLUS
    # LARGE : si le point le plus proche se trouve bien au-delà du cône, l'élargir ne rendrait
    # pas une borne — il ferait converger l'optimum vers la direction qui vise ce point, et ce
    # point n'est pas la bonne correspondance entre deux surfaces. L'oracle de direction par
    # cellule est alors DÉGÉNÉRÉ, et aucun cône ne le sauve.
    r["loracle_de_direction_degenere"] = bool(
        r["angle_au_plus_proche_median_deg"] > max(demi_angles))
    r["part_de_loracle_prise_par_une_rotation_densemble"] = (
        round(gain_g / gain_o, 3) if gain_g is not None and gain_o < -0.05 else None)
    # ⚠⚠ ET LA RUGOSITÉ SE LIT CONTRE LE PAS ANGULAIRE : un champ qui saute de plusieurs pas
    # entre cellules voisines n'est pas une correction, c'est du bruit — et il ne serait donc
    # pas atteignable par une méthode qui lit puis lisse.
    r["le_champ_de_rotation_est_plus_lisse_quun_pas"] = bool(
        r["rugosite_alpha_mediane_deg"] is not None
        and max(r["rugosite_alpha_mediane_deg"], r["rugosite_beta_mediane_deg"]) < pas_deg)
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- le pas angulaire, dérivé ---
    pas_vx = (135.5 / 2.215)
    d = pas_angulaire_deg(pas_vx)
    # ⚠⚠ LA DÉRIVATION EST VÉRIFIÉE PAR SON EFFET, pas par sa formule : tourner de ce pas doit
    # déplacer le point d'arrivée d'exactement un voxel.
    v("le pas angulaire déplace le point d'arrivée d'un voxel exactement",
      abs(pas_vx * np.sin(np.radians(d)) - 1.0) < 1e-9, f"{d:.4f}°")
    trop = None
    try:
        pas_angulaire_deg(0.5)
    except ValueError as exc:
        trop = str(exc)
    v("... et un pas trop court pour porter une rotation est REFUSÉ", trop is not None, str(trop))
    v("les cônes emboîtés doublent à partir du pas angulaire",
      cones_emboites(2.0) == [2.0, 4.0, 8.0, 16.0], str(cones_emboites(2.0)))

    # --- le cône est rond, pas carré ---
    angles = rotations_essayees(4.0, 1.0)
    dedans = dans_le_cone(angles, 4.0)
    coins = angles[np.hypot(angles[:, 0], angles[:, 1]) > 4.0 + 1e-9]
    v("la grille de rotations a des coins hors du cône", len(coins) > 0, f"{len(coins)} coins")
    # ⚠⚠⚠ SANS CE FILTRE, un « cône de 4° » contiendrait des rotations de 5,6° et la courbe
    # publiée porterait sur autre chose que son abscisse.
    v("... et le cône les écarte, donc son demi-angle veut dire ce qu'il dit",
      bool(np.all(np.hypot(angles[dedans, 0], angles[dedans, 1]) <= 4.0 + 1e-9))
      and int(dedans.sum()) < len(angles),
      f"{int(dedans.sum())} sur {len(angles)}")
    v("... et les cônes sont EMBOÎTÉS, donc comparables",
      bool(np.all(dans_le_cone(angles, 2.0) <= dedans)))
    v("... l'absence de rotation est toujours dedans",
      bool(dans_le_cone(np.array([[0.0, 0.0]]), 0.5)[0]))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(minimum=20, multiples=(1, 2), corpus=corpus_fabrique(),
                  volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and len(fab["resume"]) == 2,
      f"{fab['paires']} pas, {fab['rotations_essayees']} rotations")
    # ⚠⚠ L'ORACLE DE DIRECTION EST UNE BORNE : ajouter une liberté ne peut pas faire pire, et un
    # cône plus large ne peut pas faire pire qu'un cône plus étroit.
    ordre = [(e["de"], [e[f"erreur_oracle_{d}_um"] for d in fab["demi_angles_deg"]],
              e["erreur_sans_rotation_um"]) for e in fab["lignes"]
             if not (e[f"erreur_oracle_{fab['demi_angles_deg'][-1]}_um"]
                     <= e[f"erreur_oracle_{fab['demi_angles_deg'][0]}_um"] + 0.05
                     <= e["erreur_sans_rotation_um"] + 0.1)]
    v("... l'oracle de direction ne fait jamais pire, et un cône large jamais pire qu'un étroit",
      not ordre, str(ordre[:2]))
    # ⚠⚠ ET LA ROTATION D'ENSEMBLE EST AJUSTÉE HORS ÉCHANTILLON, donc elle PEUT faire pire que
    # l'absence de rotation — c'est même ce qui rend son verdict falsifiable.
    v("... la rotation d'ensemble est jugée hors échantillon, avec son intervalle",
      all(x["globale_contre_sans_rotation"] is None
          or x["globale_contre_sans_rotation"]["intervalle_um"] is not None
          for x in fab["resume"]),
      str(fab["resume"][-1]["globale_contre_sans_rotation"]))
    # ⚠⚠ CE QUI EST PUBLIÉ SOUS UN NOM D'ANGLE DOIT ÊTRE UN ANGLE, et tenir dans le cône :
    # la première version rendait l'indice de grille, un nombre sans unité qui se lit comme des
    # degrés et qui, sur un cône de deux pas, valait « 8 ».
    v("... et les angles retenus sont des DEGRÉS, qui tiennent dans leur cône",
      all(np.hypot(a_, b_) <= x["demi_angle_deg"] + 1e-6
          for x in fab["resume"] for a_, b_ in x["angles_retenus_deg"]),
      str(fab["resume"][-1]["angles_retenus_deg"][:3]))
    # ⚠⚠⚠ LA RUGOSITÉ ET L'ÉTENDUE SONT PUBLIÉES ENSEMBLE, parce qu'aucune ne dit seule ce que
    # les deux disent : un champ de rugosité nulle peut être constant — capturé entièrement par
    # une rotation d'ensemble — ou lentement variable, et alors elle n'en capture rien.
    v("... la rugosité ET l'étendue du champ de rotations sont rendues, sur les deux axes",
      all(fab[f"{q}_{axe}_mediane_deg"] is not None
          for q in ("rugosite", "etendue") for axe in ("alpha", "beta")),
      f"rugosité {fab['rugosite_alpha_mediane_deg']}° · étendue "
      f"{fab['etendue_alpha_mediane_deg']}°")
    # ⚠⚠⚠ LE CONTRÔLE QUI EMPÊCHE DE PUBLIER UNE LIMITE DE GRILLE COMME UNE LIMITE DE MATIÈRE.
    # ⚠⚠⚠ ET LE DIAGNOSTIC QUI DIT SI UN CÔNE PLUS LARGE SAUVERAIT QUELQUE CHOSE : l'angle
    # auquel se trouve le point le plus proche. C'est l'optimum d'une direction non bornée, et
    # ce n'est PAS la bonne correspondance entre deux surfaces.
    v("... l'angle et la distance au point le plus proche sont publiés",
      fab["angle_au_plus_proche_median_deg"] >= 0.0
      and fab["distance_au_plus_proche_mediane_um"] > 0.0,
      f"{fab['angle_au_plus_proche_median_deg']}° · "
      f"{fab['distance_au_plus_proche_mediane_um']} µm")
    v("... et le verdict de dégénérescence en découle, sans seuil posé à la main",
      fab["loracle_de_direction_degenere"]
      == (fab["angle_au_plus_proche_median_deg"] > max(fab["demi_angles_deg"])),
      str(fab["loracle_de_direction_degenere"]))
    v("... la part de cellules qui choisissent le BORD du cône est publiée, et le verdict en dépend",
      0.0 <= fab["part_au_bord_du_cone"] <= 1.0
      and fab["loracle_de_direction_est_une_borne"] == (fab["part_au_bord_du_cone"] < 0.5),
      str(fab["part_au_bord_du_cone"]))
    v("... et la part que la rotation d'ensemble prend de l'oracle est publiée",
      "part_de_loracle_prise_par_une_rotation_densemble" in fab,
      str(fab["part_de_loracle_prise_par_une_rotation_densemble"]))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "PLANCHER" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=20, multiples=(1,), corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'un balayage de directions."""
    print(f"pas nominal {r['pas_nominal_um']} µm · {r['paires']} pas · {r['cellules']} "
          f"cellules · pas angulaire {r['pas_angulaire_deg']}° · "
          f"{r['rotations_essayees']} rotations\n")
    print(f"{'demi-angle':>11} {'rotations':>10} {'ORACLE':>8} "
          f"{'oracle contre sans rotation':>38} {'globale':>9} "
          f"{'globale contre sans rotation':>38}")
    print("-" * 120)

    def court(e) -> str:
        if e is None or e["ecart_median_um"] is None:
            return "—"
        return (f"{e['ecart_median_um']:+6.1f} · {e['pas_ameliores']}/{e['pas']} · "
                f"{str(e['intervalle_um']):>14} · {'TRANCHE' if tranche(e) else '—'}")

    for x in r["resume"]:
        g = x["erreur_globale_hors_echantillon_um"]
        print(f"{x['demi_angle_deg']:>10.2f}° {x['rotations_dans_le_cone']:>10} "
              f"{x['erreur_oracle_mediane_um']:>7.1f}µ "
              f"{court(x['oracle_contre_sans_rotation']):>38} "
              f"{('—' if g is None else f'{g:.1f}'):>8}µ "
              f"{court(x['globale_contre_sans_rotation']):>38}")
    print(f"\nsans rotation {r['erreur_sans_rotation_mediane_um']} µm")
    print(f"→ ⚠⚠ {r['part_au_bord_du_cone']} des cellules choisissent le BORD du cône — ce que "
          f"l'oracle de direction prend est donc "
          f"{'une BORNE' if r['loracle_de_direction_est_une_borne'] else 'un PLANCHER, pas une borne'}")
    print(f"→ ⚠⚠⚠ or le point le plus proche du nuage se trouve à "
          f"{r['angle_au_plus_proche_median_deg']}° de la normale (à "
          f"{r['distance_au_plus_proche_mediane_um']} µm du point d'arrivée, soit l'erreur de "
          f"ne pas bouger) — donc élargir le cône ne rattraperait pas un optimum, il "
          f"convergerait vers « viser ce qui est le plus près », qui n'est pas la bonne "
          f"correspondance : l'oracle de direction par cellule est "
          f"{'DÉGÉNÉRÉ' if r['loracle_de_direction_degenere'] else 'rattrapable en élargissant'}")
    print(f"→ ⭐⭐⭐ le PLANCHER est-il mou ? "
          f"{'OUI' if r['le_plancher_est_mou'] else 'NON'} — l'oracle de direction du plus large "
          f"cône ({r['cone_le_plus_large']['demi_angle_deg']:.2f}°) prend "
          f"{-r['gain_de_loracle_de_direction_um']:.1f} µm")
    print(f"→ ⭐ une rotation d'ENSEMBLE, ajustée hors échantillon, améliore-t-elle ? "
          f"{'OUI' if r['une_rotation_densemble_ameliore'] else 'NON'}")
    print(f"→ ⚠ le champ de rotations : rugosité {r['rugosite_alpha_mediane_deg']}° / "
          f"{r['rugosite_beta_mediane_deg']}° contre un pas de {r['pas_angulaire_deg']}° "
          f"(plus lisse qu'un pas : "
          f"{'OUI' if r['le_champ_de_rotation_est_plus_lisse_quun_pas'] else 'NON'}), "
          f"étendue {r['etendue_alpha_mediane_deg']}° / {r['etendue_beta_mediane_deg']}°")
    print(f"→ ⭐⭐ il varie donc LENTEMENT à travers la feuille (lisse mais étendu) : "
          f"{'OUI' if r['le_champ_de_rotation_varie_a_travers_la_feuille'] else 'NON'} — "
          f"c'est pourquoi un biais global n'en prend que "
          f"{r['part_de_loracle_prise_par_une_rotation_densemble']}")
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
