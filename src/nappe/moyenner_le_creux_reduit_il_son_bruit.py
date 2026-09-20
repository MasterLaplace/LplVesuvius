"""Moyenner le creux sur les sous-colonnes d'un chunk réduit-il son bruit — et assez ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P53` QUI LE NOMME. `204` a établi que moyenner seize
rangées met le signal devant le bruit pour le MAILLAGE : l'aléa tombe de **4,2369** à **1,029** et
la dérive vraie vaut **2,233** voxels. La même question se pose au CREUX, et elle ne s'était jamais
posée : `200` lit sa couche sur UN cube, sans moyenner quoi que ce soit, et `202` a mesuré que son
bruit vaut **18,0421** voxels pour une dérive commune de **3,4585**.

⭐⭐⭐⭐ ET LE GAIN SE PRÉDIT AVANT D'ÊTRE MESURÉ, exactement comme `204` l'a fait. Si les lectures
d'un même chunk sont indépendantes, l'écart-type de leur moyenne décroît comme la racine de leur
nombre ; ramener le bruit du creux sous sa dérive demande donc le CARRÉ de leur rapport, et ce
nombre-là se calcule à partir des chiffres que `202` a publiés, avant qu'un seul chunk ne soit lu.
C'est ce qui rend cette tranche falsifiable : elle sait d'avance combien de lectures il lui faut.

⚠⚠⚠ ET LA PRÉDICTION A UN ADVERSAIRE, QUI EST DANS LA MATIÈRE MÊME : découper un chunk en
sous-colonnes ne donne pas des lectures gratuites. Chaque sous-colonne est plus petite, donc son
tenseur de structure repose sur moins de pixels, donc sa courbe de cohérence est plus bruitée. Les
deux effets vont en sens contraire, et c'est leur somme que la courbe mesure. Une tranche qui
n'annoncerait que la racine de `k` promettrait un gain que la géométrie peut reprendre.

⚠⚠ LE PIÈGE DE `203` EST ÉCRIT D'AVANCE, UNE FOIS DE PLUS : la DISPERSION de ce qui est lu est
publiée à côté de l'aléa à chaque compte. Un découpage assez fin pour que le lecteur rende n'importe
quoi a un aléa qui peut paraître petit, et il ne mesure rien.

⚠⚠ ET UN REPLI EST OBLIGATOIRE, PARCE QUE `200` L'A MESURÉ : la couche du creux est définie MODULO
UN PLI. Deux sous-colonnes d'un même chunk peuvent se caler sur deux frontières séparées d'un pli,
et leur moyenne brute tomberait alors entre les deux, là où il n'y a rien. La moyenne est donc prise
autour de la MÉDIANE des sous-colonnes, chaque lecture repliée dans la demi-période, et le compte
des lectures effectivement repliées est publié.

Usage :
    uv run python src/nappe/moyenner_le_creux_reduit_il_son_bruit.py --verifier
    uv run python src/nappe/moyenner_le_creux_reduit_il_son_bruit.py \\
        --json docs/mesures/moyenner_le_creux_reduit_il_son_bruit.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from combien_de_rangees_faut_il_pour_lire_le_pas import (la_portee,  # noqa: E402
                                                         lalea_predit)
from la_derive_saccumule_t_elle import (LA_PAUSE_ENTRE_ESSAIS,  # noqa: E402
                                        la_ligne_declaree)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_creux_borne_t_il_la_marche import (la_courbe_dun_bloc,  # noqa: E402
                                           le_repere_dun_chunk)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from peut_on_deplier_la_phase import ce_que_la_marche_a_rendu, le_repli  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)
from regarder_dans_la_profondeur import la_loi_appariee, le_seuil_apparie  # noqa: E402
from une_bande_plus_large_lit_elle_mieux import ce_que_lappariement_a_rendu  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LES_RANGEES_ONT_RENDU = MESURES / "combien_de_rangees_faut_il_pour_lire_le_pas.json"
GRAINE = 20261013

LA_QUESTION_DECLAREE = ("moyenner les sous-colonnes d'un chunk réduit-il le bruit du creux, et "
                        "assez pour le faire passer sous la dérive que `202` a mesurée ?")
LES_EPREUVES_DECLAREES = ("moyenner toutes les sous-colonnes offertes laisse-t-il un pas au-delà "
                          "du bruit, couture par couture",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)

# ⚠⚠ LE PLANCHER EST CELUI DE L'OPÉRATEUR, PAS UN CHOIX : `orientation_profile` dérive par
# DIFFÉRENCE CENTRÉE sur les deux axes du plan, donc il lui faut au moins trois pixels par axe pour
# rendre un seul échantillon de gradient. Une sous-colonne plus étroite ne rend aucune courbe, et le
# lecteur ne peut pas y trouver un creux qu'il n'a pas les moyens de voir.
LE_PLANCHER_DE_LOPERATEUR = 3


def ce_que_les_rangees_ont_rendu(chemin: Path = CE_QUE_LES_RANGEES_ONT_RENDU) -> dict:
    """La dérive que `204` a mesurée sur seize rangées — relue, jamais recalculée.

    ⚠⚠⚠ C'EST LA SECONDE BORNE DU CONTROLE CROISE, ET ELLE EST GRATUITE. `202` donne la derive par
    le CREUX, `204` la donne par les RANGEES du maillage, et les deux lectures n'ont rien en commun.
    Une derive du creux qui s'accorderait avec l'une et pas avec l'autre serait un fait a expliquer.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `204` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable"):
        return {"decidable": False, "raison": "le verdict de `204` est indécidable"}
    return {"decidable": True,
            "la_derive_en_voxels": v.get("la_derive_au_maximum_en_voxels"),
            "lalea_en_voxels": v.get("lalea_au_maximum_en_voxels"),
            "les_rangees": v.get("les_rangees_de_lepreuve")}


def le_bruit_du_creux_de_202(chemin: Path | None = None) -> dict:
    """Le bruit PROPRE du creux et la dérive commune, tels que `202` les a décomposés.

    ⚠ La lecture passe par `ce_que_lappariement_a_rendu`, qui est le seul lecteur de ce fichier :
    un second lecteur du même JSON finirait par ne plus s'accorder avec le premier.
    """
    d = (ce_que_lappariement_a_rendu() if chemin is None
         else ce_que_lappariement_a_rendu(Path(chemin)))
    if not d.get("decidable"):
        return d
    if d.get("le_bruit_du_creux_en_voxels") is None:
        return {"decidable": False, "raison": "`202` ne publie pas le bruit du creux"}
    return d


def les_lectures_requises(bruit, derive) -> dict:
    """Combien de lectures INDÉPENDANTES il faudrait pour passer le bruit sous la dérive.

    ⭐⭐⭐⭐ C'EST LA PREDICTION, ET ELLE EST POSEE AVANT QU'UN SEUL CHUNK NE SOIT LU. L'ecart-type
    d'une moyenne de `k` mesures independantes vaut celui d'une mesure divise par la racine de `k`,
    donc passer un bruit `b` sous une derive `t` demande `k > (b/t)^2`. Aucun reglage n'entre
    la-dedans : les deux nombres viennent de `202`, et l'exposant vient de la loi.

    ⚠⚠⚠ LE COMPTE SE PREND PAR EXCES, JAMAIS AU PLUS PROCHE. Le rapport des variances est un
    plancher STRICT : a `k` egal au rapport arrondi vers le bas, le bruit vaut encore la derive. Une
    porte ecrite en prose a dit « vingt-sept » la ou la loi demande le premier entier STRICTEMENT
    au-dessus du rapport ; c'est la raison pour laquelle ce compte se calcule ici et ne se tape pas.
    """
    if bruit is None or derive is None or float(derive) <= 0.0 or float(bruit) <= 0.0:
        return {"decidable": False, "raison": "le bruit ou la dérive de `202` manque"}
    rapport = float(bruit) / float(derive)
    exact = rapport * rapport
    requises = int(math.floor(exact)) + 1
    return {"decidable": True,
            "le_bruit_du_creux_en_voxels": round(float(bruit), 4),
            "la_derive_commune_en_voxels": round(float(derive), 4),
            "le_rapport_du_bruit_a_la_derive": round(rapport, 4),
            "le_rapport_des_variances": round(exact, 4),
            "les_lectures_requises": int(requises)}


def les_grilles_a_essayer(cote: int, requises: int | None,
                          plancher: int = LE_PLANCHER_DE_LOPERATEUR) -> dict:
    """Les découpages d'un chunk à essayer, et ce que sa géométrie offre au plus.

    ⚠⚠ LES DEUX BOUTS DE L'ECHELLE SONT DERIVES, AUCUN N'EST CHOISI. Le bas commence a DEUX
    sous-colonnes par axe parce qu'une lecture unique ne porte aucun desaccord — elle ne peut donc
    rendre aucun alea, exactement la raison pour laquelle `204` partait de deux rangees. Le haut
    s'arrete au premier decoupage qui atteint le compte requis : aller plus loin ne repondrait a
    aucune question, s'arreter avant laisserait la question ouverte.

    ⚠⚠⚠ ET « CE QU'UN CHUNK OFFRE » EST UNE QUESTION DE GEOMETRIE, PAS D'INDEPENDANCE. Le plus grand
    compte publie ici est celui que le plancher de l'operateur autorise ; savoir si ces lectures-la
    sont independantes est precisement ce que la mesure tranche, et non ce qu'elle suppose.
    """
    c = int(cote)
    offertes = []
    g = 2
    while c // g >= int(plancher):
        offertes.append(g)
        g *= 2
    if not offertes:
        return {"decidable": False,
                "raison": f"un chunk de {c} pixels de côté ne porte aucune sous-colonne "
                          f"d'au moins {int(plancher)} pixels"}
    grilles = list(offertes)
    if requises is not None:
        atteintes = [x for x in offertes if x * x >= int(requises)]
        if atteintes:
            grilles = [x for x in offertes if x <= atteintes[0]]
    plus_grand = offertes[-1] * offertes[-1]
    return {"decidable": True,
            "les_grilles": grilles,
            "les_comptes": [x * x for x in grilles],
            "les_cotes_des_sous_colonnes": [c // x for x in grilles],
            "le_plancher_de_loperateur": int(plancher),
            "le_plus_grand_compte_que_la_geometrie_offre": int(plus_grand),
            "les_lectures_requises": (None if requises is None else int(requises)),
            "la_voie_est_ouverte_avant_la_mesure": (
                None if requises is None else bool(plus_grand >= int(requises)))}


def les_sous_colonnes(hauteur: int, largeur: int, grille: int) -> list[dict]:
    """Le pavage d'un chunk en `grille` × `grille` sous-colonnes, bornes entières.

    ⚠ Les bornes sont posées par produit entier plutôt que par pas constant : un côté qui n'est pas
    multiple de la grille laisserait sinon une bande non couverte, donc une partie du chunk que
    personne ne lit et que rien ne signale.
    """
    g = int(grille)
    tuiles = []
    for iy in range(g):
        for ix in range(g):
            tuiles.append({"iy": iy, "ix": ix,
                           "y0": (iy * int(hauteur)) // g, "y1": ((iy + 1) * int(hauteur)) // g,
                           "x0": (ix * int(largeur)) // g, "x1": ((ix + 1) * int(largeur)) // g})
    return tuiles


def la_couche_dune_sous_colonne(bloc, tuile: dict, permutations: int = PERMUTATIONS,
                                graine: int = GRAINE) -> dict:
    """La couche du creux lue dans UNE sous-colonne, par le lecteur de `179` et `200`.

    ⭐ C'EST LE VRAI LECTEUR, JAMAIS UN RACCOURCI : la sous-colonne passe par le meme filtre de
    texture que le producteur applique, puis par la meme statistique de famille. Une lecture qui
    sauterait le filtre ferait entrer des sous-colonnes que le producteur n'aurait jamais lues.
    """
    b = np.asarray(bloc)[:, int(tuile["y0"]):int(tuile["y1"]),
                         int(tuile["x0"]):int(tuile["x1"])]
    if b.shape[1] < LE_PLANCHER_DE_LOPERATEUR or b.shape[2] < LE_PLANCHER_DE_LOPERATEUR:
        return {"iy": int(tuile["iy"]), "ix": int(tuile["ix"]), "la_couche": None,
                "pourquoi": "sous-colonne plus étroite que l'opérateur"}
    courbe, quoi = la_courbe_dun_bloc(b)
    if courbe is None:
        return {"iy": int(tuile["iy"]), "ix": int(tuile["ix"]), "la_couche": None,
                "pourquoi": quoi}
    lu = le_repere_dun_chunk(courbe, permutations, graine)
    return {"iy": int(tuile["iy"]), "ix": int(tuile["ix"]),
            "la_couche": lu.get("la_couche"),
            "pourquoi": (None if lu.get("lisible") else "aucun creux au-dessus de ses mélanges")}


def la_couche_de_ces_sous_colonnes(lues, periode: float = PAS_EN_VOXELS) -> dict:
    """La couche moyenne d'un chunk et le désaccord de ses deux demi-moyennes.

    ⭐⭐⭐⭐ LES DEUX MOITIES SONT PRISES EN DAMIER, et c'est le pendant exact de l'alternance des
    rangees de `204` : deux moities contigues verraient deux bandes differentes du chunk, donc leur
    desaccord porterait l'inclinaison de la frontiere plutot que l'alea de la lecture. Un damier met
    de part et d'autre des sous-colonnes voisines deux a deux, donc toute inclinaison lineaire
    traverse les deux moities de la meme facon.

    ⚠⚠⚠ LES DEUX MOITIES SONT RAMENEES AU MEME COMPTE, ET C'EST LE NUL QUI L'EXIGE. Le nul de un
    demi tient parce que `A` et `B` sont deux tirages de MEME loi ; deux moyennes de comptes
    differents n'ont pas la meme dispersion, donc leur difference cesse d'etre symetrique vis-a-vis
    de leur somme. Les sous-colonnes en trop sont ecartees dans l'ordre des indices et comptees.

    ⚠⚠ LE REPLI VIENT DE `200`, PAS D'UN REGLAGE : la couche du creux est definie modulo un pli, donc
    deux sous-colonnes peuvent se caler sur deux frontieres separees d'une periode. La mediane sert
    d'ancre parce qu'elle ne bouge pas quand une minorite de lectures saute d'un pli.
    """
    ok = [x for x in lues if x.get("la_couche") is not None]
    if len(ok) < 2:
        return {"decidable": False, "raison": "moins de deux sous-colonnes lisibles"}
    brutes = np.asarray([float(x["la_couche"]) for x in ok], dtype=float)
    ancre = float(np.median(brutes))
    repliees = ancre + np.asarray(le_repli(brutes - ancre, periode), dtype=float)
    sautees = int(sum(1 for a, b in zip(brutes, repliees) if abs(float(a) - float(b)) > 1e-9))
    pairs = [float(v) for x, v in zip(ok, repliees) if (x["iy"] + x["ix"]) % 2 == 0]
    impairs = [float(v) for x, v in zip(ok, repliees) if (x["iy"] + x["ix"]) % 2 == 1]
    if not pairs or not impairs:
        return {"decidable": False, "raison": "une des deux moitiés du damier est vide"}
    n = min(len(pairs), len(impairs))
    ecartees = len(pairs) + len(impairs) - 2 * n
    a, b = float(np.mean(pairs[:n])), float(np.mean(impairs[:n]))
    return {"decidable": True,
            "les_sous_colonnes_lues": int(len(ok)),
            "les_sous_colonnes_par_moitie": int(n),
            "les_sous_colonnes_ecartees": int(ecartees),
            "les_sous_colonnes_repliees_dun_pli": int(sautees),
            "la_demi_paire_en_voxels": round(a, 4),
            "la_demi_impaire_en_voxels": round(b, 4),
            "la_couche_en_voxels": round((a + b) / 2.0, 4),
            "le_desaccord_en_voxels": round(a - b, 4),
            "la_dispersion_des_sous_colonnes_en_voxels": round(
                float(np.std(repliees[:2 * n] if ecartees else repliees)), 4)}


def le_pas_dune_couture(gauche: dict, droite: dict, periode: float = PAS_EN_VOXELS) -> dict:
    """Le pas du creux d'un chunk au suivant, REPLIÉ, et le désaccord qui va avec.

    ⭐⭐⭐⭐ LE REPLI SE RETRANCHE AUX DEUX DEMI-PAS, JAMAIS AU SEUL PAS PUBLIE, et c'est ce qui garde
    le nul exact. Replier la somme sans replier ses deux moities romprait l'identite `2p = A + B`
    dont le nul de un demi est tire ; retirer le MEME nombre entier de plis aux deux demi-pas laisse
    leur DIFFERENCE inchangee, donc le desaccord ne bouge pas d'un voxel.
    """
    if not gauche.get("decidable") or not droite.get("decidable"):
        return {"decidable": False, "raison": "un des deux chunks ne rend pas de couche"}
    brut = float(droite["la_couche_en_voxels"]) - float(gauche["la_couche_en_voxels"])
    plis = float(np.floor(brut / float(periode) + 0.5))
    demi_a = (float(droite["la_demi_paire_en_voxels"])
              - float(gauche["la_demi_paire_en_voxels"]) - plis * float(periode))
    demi_b = (float(droite["la_demi_impaire_en_voxels"])
              - float(gauche["la_demi_impaire_en_voxels"]) - plis * float(periode))
    return {"decidable": True,
            "le_pas_brut_en_voxels": round(brut, 4),
            "les_plis_retires": int(plis),
            "le_pas_en_voxels": round((demi_a + demi_b) / 2.0, 4),
            "le_desaccord_en_voxels": round(demi_a - demi_b, 4),
            "les_sous_colonnes": int(min(int(gauche["les_sous_colonnes_lues"]),
                                         int(droite["les_sous_colonnes_lues"]))),
            # ⚠⚠⚠ CE QUE LES DEUX CHUNKS ONT LU VOYAGE AVEC LEUR PAS, ET C'EST UNE REPARATION.
            # La premiere version ne le portait pas : la courbe annoncait « dispersion dans le
            # chunk » et « plis sautes » et rendait `None` et zero a tous les barreaux — deux
            # nombres justes sous un mauvais nom, le pire des deux mondes. La sonde ne l'avait pas
            # vu parce qu'elle nourrissait la courbe avec des coutures ecrites a la main qui
            # portaient DEJA ces clefs : une fixture complaisante, la famille que ce depot a deja
            # payee six fois.
            "la_dispersion_des_sous_colonnes_en_voxels": round(
                (float(gauche["la_dispersion_des_sous_colonnes_en_voxels"])
                 + float(droite["la_dispersion_des_sous_colonnes_en_voxels"])) / 2.0, 4),
            "les_sous_colonnes_repliees_dun_pli": int(
                int(gauche["les_sous_colonnes_repliees_dun_pli"])
                + int(droite["les_sous_colonnes_repliees_dun_pli"]))}


def la_couture_porte_un_pas(lectures: dict, compte: int, coutures,
                            garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """L'ÉPREUVE : reste-t-il un pas au-delà du bruit ? Nul de un demi DÉRIVÉ, comme `204`.

    ⭐⭐⭐⭐ LE NUL SE DEMONTRE ET NE SE POSE PAS. Chaque couture rend deux demi-pas `A` et `B` de
    meme compte ; le pas publie est leur moyenne, donc `2p = A + B`, et le desaccord est `d = A - B`.
    Sans aucun pas a lire, `A` et `B` sont deux tirages independants de meme loi symetrique, donc
    `A + B` et `A - B` sont identiquement distribues et la probabilite que l'un depasse l'autre en
    module vaut exactement un demi. Avec un pas `T`, la somme grandit avec lui pendant que la
    difference ne bouge pas : la puissance est dirigee vers ce que l'epreuve cherche.
    """
    informatives, justes, vues = 0, 0, 0
    for p in coutures:
        lu = lectures.get((int(compte), p))
        if lu is None or not lu.get("decidable"):
            continue
        vues += 1
        somme = abs(2.0 * float(lu["le_pas_en_voxels"]))
        difference = abs(float(lu["le_desaccord_en_voxels"]))
        if abs(somme - difference) < 1e-9:
            continue
        informatives += 1
        justes += int(somme > difference)
    pv = la_loi_appariee(informatives, justes)
    return {"decidable": bool(informatives > 0), "les_sous_colonnes": int(compte),
            "les_coutures_vues": int(vues), "les_coutures_informatives": int(informatives),
            "les_coutures_qui_portent_un_pas": int(justes),
            "le_seuil_apparie": le_seuil_apparie(informatives, garantie).get("le_seuil"),
            "la_valeur_p": round(float(pv), 7),
            "la_garantie_de_lepreuve": round(float(garantie), 7),
            "la_couture_porte_un_pas": bool(pv <= float(garantie) + 1e-12)}


def la_courbe(lectures: dict, comptes, coutures, bruit_a_une_lecture=None) -> dict:
    """L'aléa, la dispersion et la dérive, découpage par découpage.

    ⭐⭐⭐⭐ L'ALEA D'UNE MOYENNE DE `k` SOUS-COLONNES VAUT LE DEMI ECART-TYPE DU DESACCORD, et c'est
    une identite : chaque demi-moyenne porte `k/2` lectures, donc son erreur vaut `s/racine(k/2)` ;
    leur difference vaut `2s/racine(k)` et la moyenne entiere `s/racine(k)`.

    ⚠⚠⚠ LA DISPERSION DU PAS EST PUBLIEE A COTE DE L'ALEA, TOUJOURS — la dette de `203`. Un
    decoupage assez fin pour que le lecteur rende toujours la meme couche aurait un alea minuscule
    et ne mesurerait rien du tout.

    ⚠⚠ LE BRUIT D'UNE SEULE LECTURE VIENT DE `202` ET N'EST PAS RECALCULE ICI : cette tranche ne lit
    jamais un chunk entier d'un bloc, donc elle n'a pas ce barreau-la. Le comparer au premier barreau
    mesure ce que le decoupage COUTE avant que la moyenne ne le rende.
    """
    barreaux, ref = [], None
    for k in comptes:
        pas, des, disp_sc, repliees = [], [], [], 0
        for p in coutures:
            lu = lectures.get((int(k), p))
            if lu is None or not lu.get("decidable"):
                continue
            pas.append(float(lu["le_pas_en_voxels"]))
            des.append(float(lu["le_desaccord_en_voxels"]))
            if lu.get("la_dispersion_des_sous_colonnes_en_voxels") is not None:
                disp_sc.append(float(lu["la_dispersion_des_sous_colonnes_en_voxels"]))
            repliees += int(lu.get("les_sous_colonnes_repliees_dun_pli") or 0)
        if len(pas) < 3:
            continue
        alea = float(np.std(np.asarray(des, dtype=float))) / 2.0
        disp = float(np.std(np.asarray(pas, dtype=float)))
        if ref is None:
            ref = (int(k), alea)
        predit = lalea_predit(ref[1], ref[0], int(k))
        derive = (disp * disp - alea * alea) ** 0.5 if disp > alea else None
        barreaux.append({
            "les_sous_colonnes": int(k), "les_coutures": len(pas),
            "lalea_en_voxels": round(alea, 4),
            "lalea_predit_en_voxels": round(predit, 4),
            "le_rapport_observe_sur_predit": (round(alea / predit, 4) if predit > 0 else None),
            "la_dispersion_du_pas_en_voxels": round(disp, 4),
            "la_dispersion_dans_le_chunk_en_voxels": (round(float(np.mean(disp_sc)), 4)
                                                      if disp_sc else None),
            "les_sous_colonnes_repliees_dun_pli": int(repliees),
            "la_derive_en_voxels": (None if derive is None else round(derive, 4)),
            "le_signal_sur_bruit": (None if derive is None or alea <= 0
                                    else round(derive / alea, 4))})
    if not barreaux:
        return {"decidable": False, "raison": "aucun découpage lisible"}
    lisibles = [x for x in barreaux if x["la_derive_en_voxels"] is not None
                and x["le_signal_sur_bruit"] is not None]
    meilleur = (max(lisibles, key=lambda x: x["le_signal_sur_bruit"]) if lisibles else None)
    cout = None
    if bruit_a_une_lecture is not None and float(bruit_a_une_lecture) > 0:
        cout = round(barreaux[0]["lalea_en_voxels"]
                     / (float(bruit_a_une_lecture) / (float(barreaux[0]["les_sous_colonnes"]) ** 0.5)),
                     4)
    return {"decidable": True, "les_barreaux": barreaux,
            "le_compte_de_reference": ref[0],
            "le_bruit_dune_seule_lecture_en_voxels": (None if bruit_a_une_lecture is None
                                                      else round(float(bruit_a_une_lecture), 4)),
            "ce_que_le_decoupage_coute_au_premier_barreau": cout,
            "les_comptes_qui_rendent_une_derive": [x["les_sous_colonnes"] for x in lisibles],
            "le_meilleur_compte": (None if meilleur is None else meilleur["les_sous_colonnes"]),
            "sa_derive_en_voxels": (None if meilleur is None else meilleur["la_derive_en_voxels"]),
            "son_alea_en_voxels": (None if meilleur is None else meilleur["lalea_en_voxels"]),
            "son_signal_sur_bruit": (None if meilleur is None
                                     else meilleur["le_signal_sur_bruit"])}


def un_chunk_fabrique(couches: int, grilles, couche_vraie: float,
                      bruit_par_sous_colonne: float, graine: int, largeur: int = 9,
                      permutations: int = PERMUTATIONS) -> dict:
    """Les courbes de cohérence de toutes les sous-colonnes d'un chunk, autour d'une couche POSÉE.

    ⭐⭐⭐⭐ LA COUCHE EST LUE PAR LE VRAI LECTEUR, JAMAIS ECRITE PAR LA FIXTURE. Chaque sous-colonne
    recoit une courbe dont le creux est decale de son propre bruit, et c'est `le_repere_dun_chunk`
    qui doit le retrouver. Une fixture qui poserait la couche de chaque sous-colonne n'exercerait
    que l'arithmetique de la moyenne — la famille de fixtures complaisantes que ce depot a deja
    payee six fois.

    ⚠⚠ LE BRUIT NE DEPEND PAS DU DECOUPAGE, ET C'EST DELIBERE. Sur le vrai rouleau une sous-colonne
    plus petite est plus bruitee, et c'est justement ce que la mesure doit trancher ; le faire entrer
    dans l'etalon y encoderait la conclusion. L'etalon mesure l'EPREUVE, pas la matiere.
    """
    r = _rng(int(graine))
    z = np.arange(int(couches), dtype=float)
    par_grille = {}
    for g in grilles:
        lues = []
        for tuile in les_sous_colonnes(int(g), int(g), int(g)):
            c = float(couche_vraie) + float(r.normal(0.0, float(bruit_par_sous_colonne)))
            creux = np.exp(-0.5 * ((z - c) / (float(largeur) / 2.0)) ** 2)
            coh = 0.6 - 0.45 * creux + r.normal(0.0, 0.05, size=int(couches))
            courbe = [[0.0, float(max(0.0, x))] for x in coh]
            lu = le_repere_dun_chunk(courbe, int(permutations),
                                     int(graine) + 101 * int(g) + 7 * int(tuile["iy"])
                                     + int(tuile["ix"]))
            lues.append({"iy": int(tuile["iy"]), "ix": int(tuile["ix"]),
                         "la_couche": lu.get("la_couche")})
        par_grille[int(g)] = lues
    return par_grille


def une_rangee_fabriquee(chunks: int, couches: int, grilles, couche0: float, derive: float,
                         bruit_par_sous_colonne: float, graine: int,
                         permutations: int = PERMUTATIONS) -> dict:
    """Une suite de chunks dont la couche vraie dérive — la matière de l'étalon."""
    r = _rng(int(graine))
    marche = np.concatenate(([0.0], np.cumsum(r.normal(0.0, float(derive),
                                                       size=int(chunks) - 1))))
    lectures, couches_par_chunk = {}, {}
    for i in range(int(chunks)):
        par_grille = un_chunk_fabrique(couches, grilles, float(couche0) + float(marche[i]),
                                       bruit_par_sous_colonne, int(graine) + 977 * i + 3,
                                       permutations=permutations)
        couches_par_chunk[i] = {g: la_couche_de_ces_sous_colonnes(v)
                                for g, v in par_grille.items()}
    coutures = [(i, i + 1) for i in range(int(chunks) - 1)]
    for g in grilles:
        for a, b in coutures:
            lectures[(int(g) * int(g), (a, b))] = le_pas_dune_couture(
                couches_par_chunk[a][int(g)], couches_par_chunk[b][int(g)])
    return {"lectures": lectures, "les_coutures": coutures, "la_marche": marche}


def sur_letalon(grilles, graine: int = GRAINE, chunks: int = 60, couches: int = 109,
                derive: float = 3.5, bruit_par_sous_colonne: float = 6.0,
                replicats: int = 12, permutations: int = PERMUTATIONS) -> dict:
    """L'épreuve trouve-t-elle un pas posé, et se tait-elle quand il n'y en a aucun ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202` : avec
    `n` replicats le plus petit taux non nul vaut `1/n`, donc il en faut au moins `1/garantie` pour
    qu'un seul faux n'excede pas deja la garantie, et le double pour que deux ne l'excedent pas.

    ⭐ LA FACE NEGATIVE POSE UNE DERIVE NULLE ET GARDE LE MEME BRUIT : c'est le refus difficile, et
    le seul qui mesure quelque chose.

    ⚠⚠ LA TAILLE DE L'ETALON EST CELLE DE `204`, LA TRANCHE QUE CELLE-CI PROLONGE, et elle n'est pas
    negociable a la baisse : le seuil du test apparie croit avec le nombre de coutures, donc un
    etalon plus court n'echoue pas parce que l'instrument est mauvais mais parce qu'il n'a pas la
    puissance de montrer qu'il est bon. Une premiere version a un tiers de cette taille a rate sa
    face positive pour cette seule raison, et la raccourcir jusqu'a ce qu'elle passe aurait ete un
    reglage choisi.
    """
    comptes = [int(g) * int(g) for g in grilles]
    k_max = max(comptes)
    vus, derives = 0, []
    for i in range(int(replicats)):
        f = une_rangee_fabriquee(chunks, couches, grilles, couches / 2.0, derive,
                                 bruit_par_sous_colonne, int(graine) + 1000 * i,
                                 permutations=permutations)
        ep = la_couture_porte_un_pas(f["lectures"], k_max, f["les_coutures"])
        vus += int(bool(ep.get("la_couture_porte_un_pas")))
        cb = la_courbe(f["lectures"], comptes, f["les_coutures"])
        if cb.get("decidable") and cb.get("sa_derive_en_voxels"):
            derives.append(float(cb["sa_derive_en_voxels"]))
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux = 0
    for i in range(replicats_du_refus):
        f = une_rangee_fabriquee(chunks, couches, grilles, couches / 2.0, 0.0,
                                 bruit_par_sous_colonne, int(graine) + 500000 + 1000 * i,
                                 permutations=permutations)
        ep = la_couture_porte_un_pas(f["lectures"], k_max, f["les_coutures"])
        faux += int(bool(ep.get("la_couture_porte_un_pas")))
    return {"decidable": True, "la_derive_posee_en_voxels": float(derive),
            "le_bruit_par_sous_colonne_en_voxels": float(bruit_par_sous_colonne),
            "les_chunks_par_replicat": int(chunks),
            "les_sous_colonnes_maximales": int(k_max),
            "replicats": int(replicats), "les_vus": int(vus),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "la_derive_retrouvee_en_voxels": (round(float(np.median(derives)), 4)
                                              if derives else None),
            "les_replicats_du_refus": int(replicats_du_refus), "les_faux": int(faux),
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= replicats
                                   and faux / float(replicats_du_refus)
                                   <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)}


def la_ligne(volume: dict, grilles, delai: float = DELAI, colonnes: int | None = None,
             permutations: int = PERMUTATIONS, graine: int = GRAINE,
             ouvrir=None, meta=None) -> dict:
    """Le creux de chaque SOUS-COLONNE de chaque chunk d'une rangée — la MÊME que `199` à `204`.

    ⚠⚠⚠ TOUS LES DECOUPAGES SORTENT DU MEME TELECHARGEMENT. Les lire en plusieurs passes en ferait
    plusieurs rangees, et rien ne garantirait qu'elles portent sur les memes chunks — le fil du
    reseau tombe, et la comparaison des barreaux entre eux cesserait d'en etre une.
    """
    url = f"{BUCKET}/{volume['cle']}"
    if meta is None:
        try:
            meta = array_meta(url, 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    ligne = la_ligne_declaree(gy)
    voulues = list(range(gx if colonnes is None else min(int(colonnes), gx)))
    prendre = ouvrir or (lambda cy, cx: un_chunk(url, meta, cy, cx, delai, None,
                                                 pause=LA_PAUSE_ENTRE_ESSAIS))
    lues, refus, reprises = {}, {}, 0
    for cx in voulues:
        bloc, pourquoi = prendre(int(ligne), int(cx))
        if bloc is not None and pourquoi and str(pourquoi).startswith("repris"):
            reprises += int(str(pourquoi).split()[-1])
            pourquoi = None
        if bloc is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        b = np.asarray(bloc)
        if float(b.max()) <= 0.0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        courbe, quoi = la_courbe_dun_bloc(b)
        if courbe is None:
            refus[quoi] = refus.get(quoi, 0) + 1
            continue
        par_grille = {}
        for g in grilles:
            lectures = [la_couche_dune_sous_colonne(
                b, t, permutations, int(graine) + 31 * int(cx) + 101 * int(g)
                + 7 * int(t["iy"]) + int(t["ix"]))
                for t in les_sous_colonnes(b.shape[1], b.shape[2], int(g))]
            par_grille[int(g)] = la_couche_de_ces_sous_colonnes(lectures)
        lues[int(cx)] = par_grille
    return {"decidable": bool(lues), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "le_cote_du_chunk_en_pixels": int(min(hy, hx)),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(lues),
            "les_grilles": [int(g) for g in grilles],
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "lues": lues, "les_colonnes": voulues}


def juger(courbe: dict, epreuve: dict, prediction: dict, echelle: dict,
          par_le_creux: dict, par_les_rangees: dict, portee: dict, k_max: int) -> dict:
    """Le bruit du creux est-il passé sous sa dérive, et au prix de combien de lectures ?

    ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE ET A UNE COMPARAISON DE DEUX NOMBRES POSES
    D'AVANCE : l'alea mesure au plus grand decoupage, et la derive que `202` a publiee. Aucune
    selection n'entre dedans — la courbe entiere est une description.
    """
    if not courbe.get("decidable") or not epreuve.get("decidable"):
        return {"decidable": False, "raison": "la courbe ou l'épreuve manque"}
    au_max = next((x for x in courbe["les_barreaux"] if x["les_sous_colonnes"] == int(k_max)),
                  None)
    au_min = courbe["les_barreaux"][0] if courbe["les_barreaux"] else None
    cible = par_le_creux.get("la_derive_en_voxels")
    alea_max = None if au_max is None else au_max["lalea_en_voxels"]
    passe = (None if alea_max is None or cible is None
             else bool(float(alea_max) < float(cible)))
    derive_max = None if au_max is None else au_max.get("la_derive_en_voxels")
    bruit_de_chunk = None
    if derive_max is not None and cible is not None:
        reste_carre = float(derive_max) ** 2 - float(cible) ** 2
        bruit_de_chunk = (round(reste_carre ** 0.5, 4) if reste_carre > 0.0 else None)
    bruit_total = (None if bruit_de_chunk is None or alea_max is None
                   else round((float(alea_max) ** 2 + float(bruit_de_chunk) ** 2) ** 0.5, 4))
    b202 = par_le_creux.get("le_bruit_du_creux_en_voxels")
    reste = (None if bruit_total is None or not b202
             else round(float(bruit_total) / float(b202), 4))
    return {"decidable": True,
            "les_sous_colonnes_de_lepreuve": int(k_max),
            "la_couture_porte_un_pas": bool(epreuve["la_couture_porte_un_pas"]),
            "la_valeur_p": epreuve["la_valeur_p"],
            "les_lectures_requises": prediction.get("les_lectures_requises"),
            "le_plus_grand_compte_que_la_geometrie_offre": echelle.get(
                "le_plus_grand_compte_que_la_geometrie_offre"),
            "la_voie_etait_ouverte_avant_la_mesure": echelle.get(
                "la_voie_est_ouverte_avant_la_mesure"),
            "lalea_au_depart_en_voxels": (None if au_min is None
                                          else au_min["lalea_en_voxels"]),
            "lalea_au_maximum_en_voxels": alea_max,
            "le_rapport_observe_sur_predit_au_maximum": (
                None if au_max is None else au_max["le_rapport_observe_sur_predit"]),
            "la_dispersion_au_maximum_en_voxels": (
                None if au_max is None else au_max["la_dispersion_du_pas_en_voxels"]),
            "la_derive_au_maximum_en_voxels": (None if au_max is None
                                               else au_max["la_derive_en_voxels"]),
            "le_signal_sur_bruit_au_maximum": (None if au_max is None
                                               else au_max["le_signal_sur_bruit"]),
            "la_derive_visee_par_202_en_voxels": cible,
            "le_bruit_est_il_passe_sous_la_derive": passe,
            "le_rapport_de_lalea_a_la_derive": (
                None if alea_max is None or not cible else round(float(alea_max)
                                                                 / float(cible), 4)),
            # ⭐⭐⭐⭐ CE QUE LE MOYENNAGE NE RETIRE PAS, ET C'EST LE MODELE ADDITIF DE `202` LU
            # A L'ENVERS. Ce que la courbe extrait est la dispersion du pas DEBARRASSEE du
            # desaccord entre sous-colonnes ; or `202` a mesure que la part de ce pas qui est
            # PARTAGEE avec le maillage vaut la derive visee. Ce qui reste est donc une erreur
            # COMMUNE a toutes les sous-colonnes d'un chunk, qu'aucun decoupage ne peut atteindre.
            # ⚠ Le modele se refute par ses propres nombres si la difference est negative.
            "le_bruit_de_chunk_en_voxels": bruit_de_chunk,
            "le_bruit_total_au_maximum_en_voxels": bruit_total,
            "le_bruit_de_202_en_voxels": par_le_creux.get("le_bruit_du_creux_en_voxels"),
            "ce_qui_reste_du_bruit_de_202": reste,
            "la_derive_par_les_rangees_de_204_en_voxels": par_les_rangees.get(
                "la_derive_en_voxels"),
            "le_rapport_des_deux_derives": (
                round(float(au_max["la_derive_en_voxels"])
                      / float(par_les_rangees["la_derive_en_voxels"]), 4)
                if au_max and au_max.get("la_derive_en_voxels")
                and par_les_rangees.get("la_derive_en_voxels") else None),
            "la_portee_en_chunks": ((portee.get("par_la_derive") or {}).get("les_chunks")),
            "la_portee_en_mm": ((portee.get("par_la_derive") or {}).get("la_largeur_en_mm"))}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            chunks_de_letalon: int = 60) -> dict:
    """La prédiction posée, puis la courbe par découpage, l'épreuve au plus grand, et la portée."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    par_le_creux = le_bruit_du_creux_de_202()
    prediction = les_lectures_requises(par_le_creux.get("le_bruit_du_creux_en_voxels"),
                                       par_le_creux.get("la_derive_en_voxels"))
    if meta is None:
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    echelle = les_grilles_a_essayer(int(min(hy, hx)), prediction.get("les_lectures_requises"))
    if not echelle.get("decidable"):
        return {"decidable": False, "raison": echelle.get("raison")}
    grilles = echelle["les_grilles"]
    lg = la_ligne(v, grilles, delai, colonnes, PERMUTATIONS, graine, ouvrir, meta)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celles de `199` à `204`",
                "la_ligne": {k: x for k, x in lg.items()
                             if k not in ("lues", "les_colonnes")}}
    lues = lg["lues"]
    voisines = [(c, c + 1) for c in sorted(lues) if (c + 1) in lues]
    comptes = echelle["les_comptes"]
    lectures = {}
    for g in grilles:
        for a, b in voisines:
            lectures[(int(g) * int(g), (a, b))] = le_pas_dune_couture(lues[a][int(g)],
                                                                      lues[b][int(g)])
    k_max = max(comptes)
    courbe = la_courbe(lectures, comptes, voisines,
                       par_le_creux.get("le_bruit_du_creux_en_voxels"))
    epreuve = la_couture_porte_un_pas(lectures, k_max, voisines)
    par_les_rangees = ce_que_les_rangees_ont_rendu()
    m199 = ce_que_la_marche_a_rendu()
    au_max = next((x for x in courbe.get("les_barreaux") or []
                   if x["les_sous_colonnes"] == k_max), None)
    portee = la_portee(None if au_max is None else au_max.get("la_derive_en_voxels"),
                       None if au_max is None else au_max.get("lalea_en_voxels"), m199)
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "ce_que_202_a_rendu": par_le_creux,
        "la_prediction": prediction,
        "lechelle_des_decoupages": echelle,
        "la_ligne": {k: x for k, x in lg.items() if k not in ("lues", "les_colonnes")},
        "les_coutures_voisines": len(voisines),
        "ce_que_199_a_rendu": m199,
        "ce_que_204_a_rendu": par_les_rangees,
        "la_courbe": courbe,
        "lepreuve": epreuve,
        "la_portee": portee,
        "le_verdict": juger(courbe, epreuve, prediction, echelle, par_le_creux,
                            par_les_rangees, portee, k_max),
        "letalon": sur_letalon(grilles, graine, chunks=chunks_de_letalon,
                               replicats=replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    lg = r.get("la_ligne") or {}
    print(f"MOYENNER LE CREUX RÉDUIT-IL SON BRUIT   segment {lg.get('segment')} · "
          f"rangée {lg.get('la_rangee')} · {lg.get('colonnes_lues')} chunks lus sur "
          f"{lg.get('colonnes_demandees')} · côté {lg.get('le_cote_du_chunk_en_pixels')} px")
    p = r.get("la_prediction") or {}
    if p.get("decidable"):
        print(f"  LA PRÉDICTION     bruit {p['le_bruit_du_creux_en_voxels']} pour une dérive "
              f"{p['la_derive_commune_en_voxels']} · rapport "
              f"{p['le_rapport_du_bruit_a_la_derive']} · il faut "
              f"{p['les_lectures_requises']} lectures indépendantes")
    e = r.get("lechelle_des_decoupages") or {}
    if e.get("decidable"):
        print(f"  LES DÉCOUPAGES    {e['les_comptes']} sous-colonnes · côtés "
              f"{e['les_cotes_des_sous_colonnes']} px · la géométrie en offre "
              f"{e['le_plus_grand_compte_que_la_geometrie_offre']} · voie ouverte "
              f"{e['la_voie_est_ouverte_avant_la_mesure']}")
    cb = r.get("la_courbe") or {}
    if cb.get("decidable"):
        for nom, clef in (("L'ALÉA", "lalea_en_voxels"),
                          ("PRÉDIT (√k)", "lalea_predit_en_voxels"),
                          ("OBSERVÉ / PRÉDIT", "le_rapport_observe_sur_predit"),
                          ("LA DISPERSION", "la_dispersion_du_pas_en_voxels"),
                          ("DANS LE CHUNK", "la_dispersion_dans_le_chunk_en_voxels"),
                          ("LA DÉRIVE", "la_derive_en_voxels"),
                          ("SIGNAL / BRUIT", "le_signal_sur_bruit")):
            print(f"  {nom:<17} " + " · ".join(
                f"{x['les_sous_colonnes']}→{x[clef]}" for x in cb["les_barreaux"]))
        print(f"  LES PLIS SAUTÉS   " + " · ".join(
            f"{x['les_sous_colonnes']}→{x['les_sous_colonnes_repliees_dun_pli']}"
            for x in cb["les_barreaux"]))
        if cb.get("ce_que_le_decoupage_coute_au_premier_barreau") is not None:
            print(f"  LE PRIX DU DÉCOUPAGE  au premier barreau, l'aléa vaut "
                  f"{cb['ce_que_le_decoupage_coute_au_premier_barreau']} fois ce que la racine "
                  f"de k promettait depuis `202`")
    ep = r.get("lepreuve") or {}
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         {ep['les_coutures_qui_portent_un_pas']} coutures portent un "
              f"pas sur {ep['les_coutures_informatives']} informatives (seuil "
              f"{ep['le_seuil_apparie']}) · P = {ep['la_valeur_p']} · porte "
              f"{ep['la_couture_porte_un_pas']}")
    v = r.get("le_verdict") or {}
    if v.get("decidable"):
        print(f"  LE VERDICT        aléa {v['lalea_au_maximum_en_voxels']} à "
              f"{v['les_sous_colonnes_de_lepreuve']} sous-colonnes contre une dérive "
              f"{v['la_derive_visee_par_202_en_voxels']} · rapport "
              f"{v['le_rapport_de_lalea_a_la_derive']} · passé sous "
              f"{v['le_bruit_est_il_passe_sous_la_derive']}")
        print(f"                    dérive lue {v['la_derive_au_maximum_en_voxels']} contre "
              f"{v['la_derive_par_les_rangees_de_204_en_voxels']} par les rangées (`204`) · "
              f"rapport {v['le_rapport_des_deux_derives']}")
        print(f"  CE QUI RESTE      bruit de chunk {v['le_bruit_de_chunk_en_voxels']} · bruit "
              f"total {v['le_bruit_total_au_maximum_en_voxels']} contre "
              f"{v['le_bruit_de_202_en_voxels']} chez `202` · il en reste "
              f"{v['ce_qui_reste_du_bruit_de_202']}")
    po = r.get("la_portee") or {}
    if po.get("decidable"):
        d = po.get("par_la_derive") or {}
        print(f"  LA PORTÉE         un demi-pli en {d.get('les_chunks')} chunks = "
              f"{d.get('la_largeur_en_mm')} mm")
    elif po.get("raison"):
        print(f"  LA PORTÉE         refusée : {po['raison']}")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats · dérive retrouvée "
              f"{et['la_derive_retrouvee_en_voxels']} pour {et['la_derive_posee_en_voxels']} "
              f"posée · {et['les_faux']} faux sur {et['les_replicats_du_refus']} = "
              f"{et['le_taux_de_faux']} pour {et['la_garantie']} garantis")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★★ une seule épreuve est déclarée, donc la garantie reste entière",
      len(LES_EPREUVES_DECLAREES) == 1
      and abs(GARANTIE_PAR_EPREUVE - 1.0 / (PERMUTATIONS + 1)) < 1e-12)
    v("★★ la rangée est la MÊME que celle de `199` à `204`", la_ligne_declaree(396) == 198)

    # ⚠⚠⚠ LA PREDICTION EST UN CALCUL, PAS UN NOMBRE TAPE, ET SON ARRONDI EST PAR EXCES.
    p = les_lectures_requises(18.0421, 3.4585)
    v("★★★★ le compte requis est le carré du rapport, PRIS PAR EXCÈS",
      p["decidable"] and p["les_lectures_requises"] == 28
      and abs(p["le_rapport_des_variances"] - 27.2143) < 5e-4,
      f"{p.get('les_lectures_requises')} pour {p.get('le_rapport_des_variances')}")
    v("★★★ un rapport ENTIER exige encore une lecture de plus, jamais autant",
      les_lectures_requises(6.0, 3.0)["les_lectures_requises"] == 5)
    v("★★ un rapport inférieur à un demande déjà une lecture",
      les_lectures_requises(1.0, 4.0)["les_lectures_requises"] == 1)
    v("★★★ une dérive absente ne donne AUCUN compte, jamais un défaut",
      not les_lectures_requises(18.0, None)["decidable"]
      and not les_lectures_requises(None, 3.0)["decidable"]
      and not les_lectures_requises(18.0, 0.0)["decidable"])

    # ⚠⚠ L'ECHELLE DES DECOUPAGES EST DERIVEE DU CHUNK ET DU COMPTE REQUIS.
    e = les_grilles_a_essayer(128, 28)
    v("★★★ l'échelle part de DEUX sous-colonnes par axe, jamais d'une seule",
      e["decidable"] and e["les_grilles"][0] == 2 and e["les_comptes"][0] == 4)
    v("★★★★ elle s'arrête au premier découpage qui atteint le compte requis",
      e["les_comptes"] == [4, 16, 64] and e["les_cotes_des_sous_colonnes"] == [64, 32, 16],
      str(e["les_comptes"]))
    v("★★★ ce que la géométrie offre est publié À PART du compte requis",
      e["le_plus_grand_compte_que_la_geometrie_offre"] == 1024
      and e["la_voie_est_ouverte_avant_la_mesure"] is True)
    v("★★★ un compte requis hors de portée ferme la voie AVANT la mesure",
      les_grilles_a_essayer(128, 4096)["la_voie_est_ouverte_avant_la_mesure"] is False)
    v("★★★★ le plancher est celui de l'OPÉRATEUR : un chunk de cinq pixels n'offre rien",
      not les_grilles_a_essayer(5, 4)["decidable"])
    v("★★ le plancher se relit dans la sortie", e["le_plancher_de_loperateur"] == 3)

    # ⚠⚠ LE PAVAGE COUVRE LE CHUNK ENTIER, SANS TROU NI RECOUVREMENT.
    t = les_sous_colonnes(128, 128, 4)
    v("★★ le pavage rend exactement grille × grille sous-colonnes", len(t) == 16)
    couvert = np.zeros((128, 128), dtype=int)
    for x in t:
        couvert[x["y0"]:x["y1"], x["x0"]:x["x1"]] += 1
    v("★★★★ chaque pixel du chunk est lu UNE fois et une seule",
      int(couvert.min()) == 1 and int(couvert.max()) == 1)
    t7 = les_sous_colonnes(130, 130, 4)
    couvert7 = np.zeros((130, 130), dtype=int)
    for x in t7:
        couvert7[x["y0"]:x["y1"], x["x0"]:x["x1"]] += 1
    v("★★★ un côté non multiple de la grille ne laisse aucune bande dehors",
      int(couvert7.min()) == 1 and int(couvert7.max()) == 1)

    # ⭐ LE VRAI LECTEUR, SUR LA VRAIE MATIERE DE `179`.
    import quelle_fenetre_lit_une_bascule as Q  # noqa: PLC0415
    from combien_dinterstices_traverses import PAS_UM, VOXEL_FIN_UM  # noqa: PLC0415
    from la_coherence_creuse_t_elle_a_la_frontiere import (  # noqa: PLC0415
        CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE)
    bloc = Q.bloc_de_la_fixture(109, 0.0, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE,
                                VOXEL_FIN_UM, PAS_UM, 64, transition_um=45.6)
    lues64 = [la_couche_dune_sous_colonne(bloc, x, PERMUTATIONS, 7)
              for x in les_sous_colonnes(64, 64, 2)]
    v("★★★★ le creux se lit dans une sous-colonne de la matière à fibres",
      sum(1 for x in lues64 if x["la_couche"] is not None) >= 3,
      str([x["la_couche"] for x in lues64]))
    etroite = la_couche_dune_sous_colonne(bloc, {"iy": 0, "ix": 0, "y0": 0, "y1": 2,
                                                 "x0": 0, "x1": 2})
    v("★★★ une sous-colonne plus étroite que l'opérateur est REFUSÉE, jamais devinée",
      etroite["la_couche"] is None
      and "opérateur" in str(etroite["pourquoi"]))
    plat = la_couche_dune_sous_colonne(np.zeros((109, 32, 32), dtype=np.float32),
                                       {"iy": 0, "ix": 0, "y0": 0, "y1": 32,
                                        "x0": 0, "x1": 32})
    v("★★★ une sous-colonne sans texture tombe sur le filtre DU PRODUCTEUR",
      plat["la_couche"] is None and plat["pourquoi"] == "trop peu texturé")

    # ⚠⚠⚠ LE DAMIER, LE REPLI ET L'EGALITE DES DEUX MOITIES.
    quatre = [{"iy": 0, "ix": 0, "la_couche": 50.0}, {"iy": 0, "ix": 1, "la_couche": 52.0},
              {"iy": 1, "ix": 0, "la_couche": 48.0}, {"iy": 1, "ix": 1, "la_couche": 54.0}]
    c4 = la_couche_de_ces_sous_colonnes(quatre)
    v("★★★★ les deux moitiés sont prises en DAMIER, pas en bandes contiguës",
      c4["decidable"] and abs(c4["la_demi_paire_en_voxels"] - 52.0) < 1e-9
      and abs(c4["la_demi_impaire_en_voxels"] - 50.0) < 1e-9,
      f"{c4.get('la_demi_paire_en_voxels')} / {c4.get('la_demi_impaire_en_voxels')}")
    v("★★★ la couche publiée EST la demi-somme, donc `2p = A + B` est exact",
      abs(c4["la_couche_en_voxels"] - 51.0) < 1e-9
      and abs(c4["le_desaccord_en_voxels"] - 2.0) < 1e-9)
    saute = [dict(x) for x in quatre]
    saute[3]["la_couche"] = 54.0 + PAS_EN_VOXELS
    cs = la_couche_de_ces_sous_colonnes(saute)
    v("★★★★ une sous-colonne calée un pli plus loin est REPLIÉE, et comptée",
      cs["les_sous_colonnes_repliees_dun_pli"] == 1
      and abs(cs["la_couche_en_voxels"] - c4["la_couche_en_voxels"]) < 1e-9,
      f"{cs.get('les_sous_colonnes_repliees_dun_pli')} · {cs.get('la_couche_en_voxels')}")
    trois = quatre[:3]
    c3 = la_couche_de_ces_sous_colonnes(trois)
    v("★★★★ les deux moitiés sont ramenées au MÊME compte, et l'écart est dit",
      c3["decidable"] and c3["les_sous_colonnes_par_moitie"] == 1
      and c3["les_sous_colonnes_ecartees"] == 1)
    v("★★★ la dispersion DANS le chunk est publiée à côté de la couche — la dette de `203`",
      c4.get("la_dispersion_des_sous_colonnes_en_voxels") is not None
      and abs(c4["la_dispersion_des_sous_colonnes_en_voxels"]
              - round(float(np.std([50.0, 52.0, 48.0, 54.0])), 4)) < 1e-9)
    v("★★★ moins de deux sous-colonnes lisibles ne rendent AUCUNE couche",
      not la_couche_de_ces_sous_colonnes([quatre[0]])["decidable"])
    vide = la_couche_de_ces_sous_colonnes([{"iy": 0, "ix": 0, "la_couche": 1.0},
                                           {"iy": 1, "ix": 1, "la_couche": 2.0}])
    v("★★★ une moitié vide du damier est refusée, jamais complétée",
      not vide["decidable"] and "moitiés" in str(vide.get("raison")))

    # ⭐⭐⭐⭐ LE REPLI SE RETRANCHE AUX DEUX DEMI-PAS : LE DESACCORD NE BOUGE PAS.
    g0 = la_couche_de_ces_sous_colonnes(quatre)
    loin = [{"iy": x["iy"], "ix": x["ix"],
             "la_couche": x["la_couche"] + PAS_EN_VOXELS + 3.0} for x in quatre]
    d0 = la_couche_de_ces_sous_colonnes(loin)
    pas = le_pas_dune_couture(g0, d0)
    v("★★★★ le pas est REPLIÉ d'un pli entier, et le pli retiré est dit",
      pas["decidable"] and pas["les_plis_retires"] == 1
      and abs(pas["le_pas_en_voxels"] - 3.0) < 1e-3,
      f"{pas.get('les_plis_retires')} · {pas.get('le_pas_en_voxels')}")
    v("★★★★ le désaccord SURVIT au repli, au voxel près",
      abs(pas["le_desaccord_en_voxels"]) < 1e-9,
      str(pas.get("le_desaccord_en_voxels")))
    v("★★★ un chunk qui ne rend aucune couche ne rend aucun pas",
      not le_pas_dune_couture(g0, {"decidable": False})["decidable"])

    # ⚠⚠⚠ L'EPREUVE : LE NUL DE UN DEMI SE DEMONTRE, ET LA PUISSANCE EST DIRIGEE.
    r = _rng(4242)
    coutures = list(range(400))
    nul = {}
    for i in coutures:
        e1, e2 = float(r.normal()), float(r.normal())
        nul[(64, i)] = {"decidable": True, "le_pas_en_voxels": (e1 + e2) / 2.0,
                        "le_desaccord_en_voxels": e1 - e2}
    en_nul = la_couture_porte_un_pas(nul, 64, coutures)
    v("★★★★ sans aucun pas, l'épreuve se TAIT — le nul de un demi tient",
      not en_nul["la_couture_porte_un_pas"]
      and abs(en_nul["les_coutures_qui_portent_un_pas"]
              / en_nul["les_coutures_informatives"] - 0.5) < 0.08,
      f"{en_nul['les_coutures_qui_portent_un_pas']}/{en_nul['les_coutures_informatives']}")
    avec = {}
    for i in coutures:
        e1, e2 = float(r.normal()), float(r.normal())
        avec[(64, i)] = {"decidable": True, "le_pas_en_voxels": 3.0 + (e1 + e2) / 2.0,
                         "le_desaccord_en_voxels": e1 - e2}
    en_pas = la_couture_porte_un_pas(avec, 64, coutures)
    v("★★★★ avec un pas posé, l'épreuve le TROUVE",
      en_pas["la_couture_porte_un_pas"] and en_pas["la_valeur_p"] <= GARANTIE_PAR_EPREUVE,
      str(en_pas.get("la_valeur_p")))
    v("★★★ une couture dont la somme ÉGALE la différence n'est pas informative",
      la_couture_porte_un_pas({(4, 0): {"decidable": True, "le_pas_en_voxels": 0.5,
                                        "le_desaccord_en_voxels": 1.0}},
                              4, [0])["les_coutures_informatives"] == 0)
    v("★★ l'épreuve nomme le COMPTE DE SOUS-COLONNES, jamais un compte de rangées",
      "les_sous_colonnes" in en_pas and "les_rangees" not in en_pas)

    # ⚠⚠⚠ LA COURBE : L'ALEA EST UNE IDENTITE, LA DISPERSION EST PUBLIEE A COTE.
    des = [1.0, -3.0, 2.0, -2.0, 4.0, -1.0]
    pss = [5.0, 6.0, 4.0, 7.0, 5.5, 6.5]
    lect = {(4, i): {"decidable": True, "le_pas_en_voxels": pss[i],
                     "le_desaccord_en_voxels": des[i],
                     "la_dispersion_des_sous_colonnes_en_voxels": 9.0,
                     "les_sous_colonnes_repliees_dun_pli": 1}
            for i in range(6)}
    # ⚠⚠⚠ ET LA CHAINE ENTIERE EST EXERCEE, PAS SEULEMENT SON DERNIER MAILLON. Les coutures
    # ci-dessus sont ecrites a la main, donc elles portent les clefs par construction : c'est
    # exactement la fixture complaisante qui a laissé passer un `le_pas_dune_couture` qui ne
    # transmettait RIEN de ce que ses deux chunks avaient lu. Celle-ci part des sous-colonnes.
    gA = la_couche_de_ces_sous_colonnes(quatre)
    plus_disperse = [{"iy": x["iy"], "ix": x["ix"],
                      "la_couche": 60.0 + 4.0 * ((x["iy"] + x["ix"]) % 2)} for x in quatre]
    plus_disperse[2]["la_couche"] = 60.0 + PAS_EN_VOXELS
    gB = la_couche_de_ces_sous_colonnes(plus_disperse)
    chaine = le_pas_dune_couture(gA, gB)
    # ⚠⚠ LA SONDE LIT PAR `.get()` ET TESTE LA PRESENCE AVANT LA VALEUR : un bris qui retire la
    # clef doit rendre cette sonde ROUGE, jamais tuer la batterie avant son verdict.
    portee_lue = chaine.get("la_dispersion_des_sous_colonnes_en_voxels")
    v("★★★★ le pas d'une couture PORTE la dispersion que ses deux chunks ont lue",
      portee_lue is not None
      and abs(float(portee_lue)
              - round((float(gA["la_dispersion_des_sous_colonnes_en_voxels"])
                       + float(gB["la_dispersion_des_sous_colonnes_en_voxels"])) / 2.0, 4)) < 1e-9
      and gA["la_dispersion_des_sous_colonnes_en_voxels"]
      != gB["la_dispersion_des_sous_colonnes_en_voxels"],
      str(portee_lue))
    v("★★★★ il porte aussi le COMPTE des sous-colonnes repliées, somme des deux chunks",
      chaine["les_sous_colonnes_repliees_dun_pli"]
      == gA["les_sous_colonnes_repliees_dun_pli"] + gB["les_sous_colonnes_repliees_dun_pli"]
      and chaine["les_sous_colonnes_repliees_dun_pli"] == 1,
      str(chaine.get("les_sous_colonnes_repliees_dun_pli")))
    bout_en_bout = la_courbe({(4, i): le_pas_dune_couture(gA, gB) for i in range(6)},
                             [4], list(range(6)))
    v("★★★★ la courbe lit ces deux nombres SUR LA COUTURE, pas sur une fixture écrite à la main",
      bout_en_bout["les_barreaux"][0]["la_dispersion_dans_le_chunk_en_voxels"] is not None
      and bout_en_bout["les_barreaux"][0]["les_sous_colonnes_repliees_dun_pli"] == 6,
      str(bout_en_bout["les_barreaux"][0].get("la_dispersion_dans_le_chunk_en_voxels")))
    cb = la_courbe(lect, [4], list(range(6)))
    v("★★★★ l'aléa vaut le DEMI écart-type du désaccord, exactement",
      cb["decidable"]
      and abs(cb["les_barreaux"][0]["lalea_en_voxels"]
              - round(float(np.std(des)) / 2.0, 4)) < 1e-9,
      str(cb["les_barreaux"][0]["lalea_en_voxels"]))
    # ⚠⚠ LA SONDE LIT PAR `.get()` ET TESTE LA PRESENCE AVANT LA VALEUR : un bris qui retire la
    # clef doit rendre cette sonde ROUGE, pas tuer la batterie avant son verdict.
    disp_lue = cb["les_barreaux"][0].get("la_dispersion_du_pas_en_voxels")
    v("★★★★ la DISPERSION du pas est publiée à côté de l'aléa — le piège de `203`",
      disp_lue is not None and abs(float(disp_lue) - round(float(np.std(pss)), 4)) < 1e-9,
      str(disp_lue))
    v("★★★ la dispersion DANS le chunk et les plis sautés voyagent avec le barreau",
      cb["les_barreaux"][0]["la_dispersion_dans_le_chunk_en_voxels"] == 9.0
      and cb["les_barreaux"][0]["les_sous_colonnes_repliees_dun_pli"] == 6)
    v("★★★★ une dispersion SOUS l'aléa ne rend AUCUNE dérive, jamais une racine négative",
      la_courbe({(4, i): {"decidable": True, "le_pas_en_voxels": 5.0 + 0.001 * i,
                          "le_desaccord_en_voxels": des[i]}
                 for i in range(6)}, [4], list(range(6))
                )["les_barreaux"][0]["la_derive_en_voxels"] is None)
    deux = dict(lect)
    deux.update({(16, i): {"decidable": True, "le_pas_en_voxels": pss[i],
                           "le_desaccord_en_voxels": des[i] / 2.0}
                 for i in range(6)})
    cb2 = la_courbe(deux, [4, 16], list(range(6)))
    v("★★★★ le prédit suit la racine de k depuis le PREMIER barreau, et l'écart est publié",
      abs(cb2["les_barreaux"][1]["lalea_predit_en_voxels"]
          - round(cb2["les_barreaux"][0]["lalea_en_voxels"] * 0.5, 4)) < 1e-4
      and abs(cb2["les_barreaux"][1]["le_rapport_observe_sur_predit"] - 1.0) < 1e-3,
      str(cb2["les_barreaux"][1]))
    v("★★★ le prix du découpage se lit contre le bruit d'UNE lecture de `202`",
      la_courbe(lect, [4], list(range(6)), 18.0421
                )["ce_que_le_decoupage_coute_au_premier_barreau"] is not None)
    v("★★★ moins de trois coutures ne rendent aucun barreau",
      not la_courbe({(4, 0): lect[(4, 0)]}, [4], [0])["decidable"])

    # ⚠⚠ LE VERDICT COMPARE DEUX NOMBRES POSES D'AVANCE, ET LA PORTEE EST CELLE DE `204`.
    jug = juger(cb2, en_pas, p, e,
                {"la_derive_en_voxels": 3.4585, "le_bruit_du_creux_en_voxels": 18.0421},
                {"la_derive_en_voxels": 2.233}, {"decidable": False}, 16)
    v("★★★★ le verdict compare l'aléa au plus grand découpage à la dérive de `202`",
      jug["decidable"] and jug["la_derive_visee_par_202_en_voxels"] == 3.4585
      and jug["le_bruit_est_il_passe_sous_la_derive"] is (
          float(cb2["les_barreaux"][1]["lalea_en_voxels"]) < 3.4585))
    # ⚠ LA CIBLE DE CETTE SONDE EST SOUS LA DERIVE DE LA FIXTURE, SINON LE MODELE ADDITIF EST
    # REFUTE PAR CONSTRUCTION ET LA SONDE NE MESURERAIT QUE SON PROPRE REFUS.
    jug2 = juger(cb2, en_pas, p, e,
                 {"la_derive_en_voxels": 0.25, "le_bruit_du_creux_en_voxels": 18.0421},
                 {"la_derive_en_voxels": 2.233}, {"decidable": False}, 16)
    v("★★★★ le verdict nomme le bruit de CHUNK que le moyennage ne peut pas retirer",
      jug2["le_bruit_de_chunk_en_voxels"] is not None
      and abs(float(jug2["le_bruit_de_chunk_en_voxels"])
              - round((float(cb2["les_barreaux"][1]["la_derive_en_voxels"]) ** 2
                       - 0.25 ** 2) ** 0.5, 4)) < 1e-9,
      str(jug2.get("le_bruit_de_chunk_en_voxels")))
    v("★★★★ un résidu SOUS la dérive de `202` réfute le modèle par ses propres nombres",
      jug["le_bruit_de_chunk_en_voxels"] is None
      and juger(cb2, en_pas, p, e, {"la_derive_en_voxels": 999.0},
                {"la_derive_en_voxels": 2.233}, {"decidable": False},
                16)["le_bruit_de_chunk_en_voxels"] is None,
      str(jug.get("le_bruit_de_chunk_en_voxels")))
    v("★★★★ ce qui reste du bruit de `202` est publié, pas laissé à lire entre les lignes",
      jug2["ce_qui_reste_du_bruit_de_202"] is not None
      and abs(float(jug2["ce_qui_reste_du_bruit_de_202"])
              - round(float(jug2["le_bruit_total_au_maximum_en_voxels"]) / 18.0421, 4)) < 1e-9,
      str(jug2.get("ce_qui_reste_du_bruit_de_202")))
    v("★★★ le contrôle croisé porte les DEUX bornes, le creux et les rangées",
      jug["la_derive_par_les_rangees_de_204_en_voxels"] == 2.233
      and jug["les_lectures_requises"] == 28)
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger(cb2, {"decidable": False}, p, e, {}, {}, {}, 16)["decidable"])
    v("★★★★ une dérive qui ne dépasse pas son aléa ne se projette pas — le refus de `203`",
      not la_portee(0.5, 1.0, {"le_pas_quadratique_en_voxels": 4.941})["decidable"])
    v("★★★ une dérive au-dessus de son aléa se projette, elle",
      la_portee(5.0, 1.0, {"le_pas_quadratique_en_voxels": 4.941})["decidable"])

    # ⚠⚠ LES DEUX LECTEURS DE TRANCHES ANTERIEURES REFUSENT PLUTOT QUE DE DEVINER.
    v("★★★ `204` absent est dit, jamais remplacé",
      not ce_que_les_rangees_ont_rendu(Path("/pas/de/fichier.json"))["decidable"])
    v("★★★ `202` absent est dit, jamais remplacé",
      not le_bruit_du_creux_de_202(Path("/pas/de/fichier.json"))["decidable"])
    v("★★★★ `202` est lu par le lecteur de `203`, pas par un second",
      le_bruit_du_creux_de_202().get("le_bruit_du_creux_en_voxels")
      == (ce_que_lappariement_a_rendu() or {}).get("le_bruit_du_creux_en_voxels"))

    # ⚠⚠⚠ LA LIGNE : UN VOLUME MUET EST REFUSE, LE RESEAU TOMBE EST REFUSE.
    meta = {"chunks": [109, 12, 12], "shape": [109, 24, 40]}
    v("★★★ un volume qui ne répond pas est refusé, jamais deviné",
      not la_ligne({"cle": "x", "segment": "s"}, [2], 0.0, None, PERMUTATIONS, GRAINE,
                   lambda cy, cx: (None, "absent du dépôt"), meta)["decidable"])
    lg = la_ligne({"cle": "x", "segment": "s"}, [2], 0.0, None, PERMUTATIONS, GRAINE,
                  lambda cy, cx: (bloc[:, :12, :12], None), meta)
    v("★★★★ la ligne lit TOUS les découpages du MÊME téléchargement",
      lg["decidable"] and lg["colonnes_lues"] == 4 and lg["les_grilles"] == [2]
      and all(2 in x for x in lg["lues"].values()),
      f"{lg.get('colonnes_lues')} colonnes")
    v("★★ le côté du chunk est relu de la méta, jamais supposé",
      lg["le_cote_du_chunk_en_pixels"] == 12)

    # ⭐ L'ETALON, EN PETIT : IL DOIT SEPARER SES DEUX FACES.
    # ⚠⚠ LE REGIME DE LA SONDE EST POSE PAR LA PREDICTION, PAS REGLE JUSQU'A CE QU'ELLE PASSE :
    # avec quatre sous-colonnes et un bruit de deux voxels, l'alea predit vaut UN voxel, donc une
    # derive de huit est huit fois au-dessus de lui. L'etalon doit la trouver ; s'il ne la trouve
    # pas, c'est la machinerie qui est en cause et non le reglage.
    et = sur_letalon([2], GRAINE, chunks=8, couches=109, derive=8.0,
                     bruit_par_sous_colonne=2.0, replicats=3, permutations=7)
    v("★★★★ l'étalon trouve la dérive qu'il a posée",
      et["la_part_trouvee"] >= 0.99, str(et.get("la_part_trouvee")))
    v("★★★★ la face négative a DEUX fois le compte que la garantie exige — la leçon de `202`",
      et["les_replicats_du_refus"] == int(2.0 / GARANTIE_PAR_EPREUVE))
    v("★★★★ sur une matière SANS dérive, le taux de faux tient la garantie",
      et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('les_faux')} faux sur {et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare ses deux faces, et il le DIT", et["letalon_separe"] is True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--colonnes", type=int, default=None)
    ap.add_argument("--graine", type=int, default=GRAINE)
    ap.add_argument("--replicats", type=int, default=12)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(DELAI, a.graine, a.replicats, a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
