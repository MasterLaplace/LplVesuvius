"""Combien de rangées faut-il pour lire le pas — et la racine de k tient-elle ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P52` QUI LE NOMME. `203` a établi qu'à AUCUNE largeur de
bande l'estimateur différentiel ne lit plus de signal que de bruit : le désaccord de deux rangées
d'un même chunk dépasse la dispersion du pas lui-même, de **0,2362** contre **0,2203** à deux
colonnes jusqu'à **13,6967** contre **10,4107** à soixante-quatre. Ce n'est donc plus un problème de
réglage mais de FORME de mesure.

⭐⭐⭐⭐ ET `203` A LAISSÉ DEUX LECTURES OUVERTES, QUE CETTE TRANCHE SÉPARE. Ou bien ce désaccord est
le BRUIT de l'estimateur — et alors moyenner plusieurs rangées doit le diviser par la racine de leur
nombre — ou bien c'est la VARIATION RÉELLE de la surface à l'intérieur d'un chunk — et alors
moyenner n'y fera rien, parce que les erreurs des rangées ne sont pas indépendantes. Les deux
hypothèses prédisent des courbes différentes, et la mesure tranche.

⭐⭐⭐⭐ LA PRÉDICTION EST POSÉE AVANT LA MESURE, ET C'EST LA PREMIÈRE FOIS DE LA CHAÎNE. Si les
erreurs sont indépendantes, l'aléa d'une moyenne de `k` rangées vaut celui d'une rangée divisé par
la racine de `k`, exactement. Le rapport de l'observé au prédit est donc publié à chaque `k` : proche
de un, les rangées sont indépendantes et le bruit est celui de l'instrument ; bien plus grand, elles
ne le sont pas et ce qu'on mesurait était la surface elle-même.

⚠⚠⚠ ET LE PIÈGE DE `203` EST ÉCRIT D'AVANCE : un critère qui ne regarde pas la DYNAMIQUE récompense
un instrument mort. La dispersion du pas lu est publiée À CÔTÉ de l'aléa à chaque `k`, toujours.

Usage :
    uv run python src/nappe/combien_de_rangees_faut_il_pour_lire_le_pas.py --verifier
    uv run python src/nappe/combien_de_rangees_faut_il_pour_lire_le_pas.py \\
        --json docs/mesures/combien_de_rangees_faut_il_pour_lire_le_pas.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_derive_saccumule_t_elle import (LA_PAUSE_ENTRE_ESSAIS,  # noqa: E402
                                        combien_de_chunks_avant, la_largeur_du_bord,
                                        la_ligne_declaree, un_pas)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_creux_borne_t_il_la_marche import la_courbe_dun_bloc  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from peut_on_deplier_la_phase import ce_que_la_marche_a_rendu  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS, une_section)
from regarder_dans_la_profondeur import la_loi_appariee, le_seuil_apparie  # noqa: E402
from une_bande_plus_large_lit_elle_mieux import ce_que_lappariement_a_rendu  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261012
LES_RANGEES = 16

LA_QUESTION_DECLAREE = ("moyenner plusieurs rangées divise-t-il l'aléa par la racine de leur "
                        "nombre, ou le désaccord était-il la surface elle-même ?")
LES_EPREUVES_DECLAREES = ("moyenner seize rangées réduit-il le désaccord, couture par couture, "
                          "par rapport à deux",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def les_rangees_a_lire(cote: int, combien: int = LES_RANGEES) -> list[int]:
    """Les rangées de coupe, réparties UNIFORMÉMENT sur la hauteur du chunk.

    ⚠ Elles sont derivees et centrees : la `i`-eme tombe au milieu de la `i`-eme tranche d'egale
    hauteur, donc aucune ne touche un bord et aucune n'est privilegiee. Les prendre contigues
    ferait `k` lectures de la MEME matiere, et leur moyenne ne reduirait aucun bruit.
    """
    n = max(1, int(combien))
    return [int(cote) * (2 * i + 1) // (2 * n) for i in range(n)]


def les_sous_ensembles(combien: int = LES_RANGEES) -> list[int]:
    """Les comptes de rangées essayés : les puissances de deux qu'une coupe en deux admet.

    ⚠⚠ LE PLANCHER EST DEUX, parce qu'une seule rangee ne se coupe pas en deux moities et ne rend
    donc aucun alea. Le plafond est le nombre de rangees lues.
    """
    out, k = [], 2
    while k <= int(combien):
        out.append(int(k))
        k *= 2
    return out


def un_sous_ensemble(rangees, k: int) -> list[int]:
    """Les `k` rangées retenues — un prélèvement RÉGULIER, donc étalé sur toute la hauteur.

    ⭐ LES SOUS-ENSEMBLES SONT EMBOITES : celui de deux est inclus dans celui de quatre, et ainsi de
    suite. C'est ce qui rend la comparaison entre comptes APPARIEE couture par couture — deux
    prelevements independants melangeraient le gain du nombre avec celui de l'endroit.
    """
    n, k = len(rangees), int(k)
    if k < 1 or k > n:
        return []
    pas = n // k
    return [rangees[i * pas] for i in range(k)]


def le_pas_dune_rangee(droit, gauche, plage: int = DEMI_PAS_EN_VOXELS) -> dict:
    """Le pas lu sur UNE rangée — `un_pas` de `199`, sur les profils de bord déjà moyennés.

    ⭐ LE PROFIL EST MOYENNE UNE FOIS A LA LECTURE, PAS A CHAQUE APPEL : `un_pas` moyenne les
    colonnes de la bande qu'on lui donne, donc lui passer le profil deja moyenne comme une colonne
    unique rend EXACTEMENT le meme nombre, et la rangee entiere tient alors dans quelques kilooctets
    au lieu de quelques mega. Une sonde le verifie plutot que de le supposer.
    """
    g = np.asarray(droit, dtype=float).reshape(-1, 1)
    d = np.asarray(gauche, dtype=float).reshape(-1, 1)
    return un_pas(g, d, 1, plage)


def le_pas_de_k_rangees(profils_droits: dict, profils_gauches: dict, rangees,
                        plage: int = DEMI_PAS_EN_VOXELS) -> dict:
    """Le pas d'une couture, MOYENNÉ sur les rangées données, et ses deux demi-moyennes.

    ⭐⭐⭐⭐ LA MOYENNE EST CELLE DES ESTIMATIONS, PAS DES PROFILS, et c'est ce qui rend la prediction
    exacte : la variance d'une moyenne de `k` mesures independantes vaut celle d'une mesure divisee
    par `k`, donc son ecart-type est divise par la racine de `k`. Moyenner les PROFILS avant de
    correler melangerait les matieres et ne suivrait aucune loi simple.

    ⚠⚠ LES DEUX DEMI-MOYENNES SONT PRISES EN ALTERNANCE, une rangee sur deux : deux moities
    contigues verraient deux bandes differentes du chunk, et leur desaccord porterait la variation
    de la surface entre ces bandes plutot que l'alea de la lecture.
    """
    lus = []
    for r in rangees:
        if r not in profils_droits or r not in profils_gauches:
            continue
        x = le_pas_dune_rangee(profils_droits[r], profils_gauches[r], plage)
        if x.get("decidable"):
            lus.append((int(r), float(x["le_pas_en_voxels"])))
    if len(lus) < 2:
        return {"decidable": False, "raison": "moins de deux rangées lisibles"}
    a = [v for i, (_r, v) in enumerate(lus) if i % 2 == 0]
    b = [v for i, (_r, v) in enumerate(lus) if i % 2 == 1]
    if not a or not b:
        return {"decidable": False, "raison": "une des deux demi-moyennes est vide"}
    return {"decidable": True, "les_rangees": len(lus),
            "le_pas_en_voxels": round(float(np.mean([v for _r, v in lus])), 4),
            "la_demi_moyenne_paire_en_voxels": round(float(np.mean(a)), 4),
            "la_demi_moyenne_impaire_en_voxels": round(float(np.mean(b)), 4),
            "le_desaccord_en_voxels": round(float(np.mean(a)) - float(np.mean(b)), 4)}


def lalea_predit(alea_de_reference: float, k_de_reference: int, k: int) -> float:
    """L'aléa qu'une moyenne de `k` rangées aurait si leurs erreurs étaient INDÉPENDANTES.

    ⭐⭐⭐⭐ C'EST LA PREDICTION, ET ELLE EST POSEE AVANT LA MESURE. Elle n'a aucun reglage : l'ecart-
    type d'une moyenne de mesures independantes decroit comme la racine de leur nombre, donc le
    rapport de l'alea a `k` a celui a `k` de reference vaut la racine du rapport inverse des deux
    comptes. Comparer l'observe a ce nombre-la est ce qui separe un bruit d'instrument d'une
    variation de la matiere.
    """
    return float(alea_de_reference) * (float(k_de_reference) / float(k)) ** 0.5


def la_couture_porte_un_pas(lectures: dict, k: int, coutures,
                            garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """Y a-t-il un pas au-delà du bruit ? L'ÉPREUVE, exacte, avec un nul de un demi DÉRIVÉ.

    ⭐⭐⭐⭐ LE NUL N'EST PAS POSE, IL SE DEMONTRE. Chaque couture rend deux demi-moyennes `A` et `B`
    de meme taille. Le pas publie est leur moyenne, donc `2p = A + B`, et le desaccord est
    `d = A - B`. S'il n'y a AUCUN pas a lire, `A` et `B` sont deux tirages independants de meme loi
    symetrique, donc `A + B` et `A - B` sont IDENTIQUEMENT distribues : la probabilite que l'un
    depasse l'autre en module vaut exactement un demi. Aucun reglage, aucune hypothese gaussienne.

    ⭐ ET S'IL Y A UN PAS `T`, alors `A + B = 2T + (e1 + e2)` grandit avec lui pendant que
    `A - B = e1 - e2` ne bouge pas : l'epreuve a de la puissance exactement contre ce qu'elle
    cherche.

    ⚠⚠ LA LOI EN RACINE DE `k` SUR L'ALEA N'EST PAS L'EPREUVE, ET C'EST DELIBERE : l'ecart-type
    d'une moyenne de mesures independantes decroit comme la racine de leur nombre par construction,
    donc le verifier serait une verification incapable d'echouer. Elle est publiee comme DESCRIPTION,
    et c'est son ECART a la prediction qui renseigne.
    """
    informatives, justes, vues = 0, 0, 0
    for p in coutures:
        lu = lectures.get((int(k), p))
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
    return {"decidable": bool(informatives > 0), "les_rangees": int(k),
            "les_coutures_vues": int(vues), "les_coutures_informatives": int(informatives),
            "les_coutures_qui_portent_un_pas": int(justes),
            "le_seuil_apparie": le_seuil_apparie(informatives, garantie).get("le_seuil"),
            "la_valeur_p": round(float(pv), 7),
            "la_garantie_de_lepreuve": round(float(garantie), 7),
            "la_couture_porte_un_pas": bool(pv <= float(garantie) + 1e-12)}


def la_courbe(lectures: dict, comptes, coutures) -> dict:
    """L'aléa, la dispersion et la dérive, compte de rangées par compte de rangées.

    ⭐⭐⭐⭐ L'ALEA D'UNE MOYENNE DE `k` RANGEES VAUT LE DEMI ECART-TYPE DU DESACCORD, exactement :
    chaque demi-moyenne porte `k/2` rangees, donc son erreur vaut `s/racine(k/2)` ; leur difference
    vaut `2s/racine(k)` et la moyenne entiere `s/racine(k)`. La division par deux est donc une
    identite, pas un reglage.

    ⚠⚠⚠ LA DISPERSION DU PAS EST PUBLIEE A COTE DE L'ALEA, TOUJOURS. `203` a paye qu'un critere qui
    ne la regarde pas recompense un instrument mort : une lecture qui rend toujours le meme pas a un
    alea minuscule et ne mesure rien.
    """
    barreaux, ref = [], None
    for k in comptes:
        pas, des = [], []
        for p in coutures:
            lu = lectures.get((int(k), p))
            if lu is None or not lu.get("decidable"):
                continue
            pas.append(float(lu["le_pas_en_voxels"]))
            des.append(float(lu["le_desaccord_en_voxels"]))
        if len(pas) < 3:
            continue
        alea = float(np.std(np.asarray(des, dtype=float))) / 2.0
        disp = float(np.std(np.asarray(pas, dtype=float)))
        if ref is None:
            ref = (int(k), alea)
        predit = lalea_predit(ref[1], ref[0], int(k))
        derive = (disp * disp - alea * alea) ** 0.5 if disp > alea else None
        barreaux.append({
            "les_rangees": int(k), "les_coutures": len(pas),
            "lalea_en_voxels": round(alea, 4),
            "lalea_predit_en_voxels": round(predit, 4),
            "le_rapport_observe_sur_predit": (round(alea / predit, 4) if predit > 0 else None),
            "la_dispersion_du_pas_en_voxels": round(disp, 4),
            "la_derive_en_voxels": (None if derive is None else round(derive, 4)),
            "le_signal_sur_bruit": (None if derive is None or alea <= 0
                                    else round(derive / alea, 4))})
    if not barreaux:
        return {"decidable": False, "raison": "aucun compte de rangées lisible"}
    # ⚠⚠ UN BARREAU SANS ALEA NE PEUT PAS ETRE COMPARE : sur une matiere ou toutes les rangees
    # lisent le meme pas, le desaccord est nul partout et le signal sur bruit n'existe pas. L'ecarter
    # ici garde a la batterie un VERDICT — un bris pose sur la fixture la faisait tomber en panne.
    lisibles = [x for x in barreaux if x["la_derive_en_voxels"] is not None
                and x["le_signal_sur_bruit"] is not None]
    meilleur = (max(lisibles, key=lambda x: x["le_signal_sur_bruit"]) if lisibles else None)
    return {"decidable": True, "les_barreaux": barreaux,
            "le_compte_de_reference": ref[0],
            "les_comptes_qui_rendent_une_derive": [x["les_rangees"] for x in lisibles],
            "le_meilleur_compte": (None if meilleur is None else meilleur["les_rangees"]),
            "sa_derive_en_voxels": (None if meilleur is None else meilleur["la_derive_en_voxels"]),
            "son_alea_en_voxels": (None if meilleur is None else meilleur["lalea_en_voxels"]),
            "son_signal_sur_bruit": (None if meilleur is None else meilleur["le_signal_sur_bruit"])}


def la_portee(derive, alea, reference: dict) -> dict:
    """Après combien de chunks un demi-pli est perdu — la SECONDE LECTURE, refusée si le bruit gagne.

    ⚠⚠⚠ LE REFUS EST DERIVE ET IL A ETE PAYE : `203` a projete une derive plus petite que son propre
    alea et a rendu dix-neuf metres sur un rouleau large de cent vingt et un millimetres. Une derive
    qui ne depasse pas le bruit qui la mesure ne se projette pas.

    ⚠ La fonction de projection est celle de `199`, importee et jamais reecrite.
    """
    if derive is None or float(derive) <= 0.0:
        return {"decidable": False, "raison": "aucune dérive à projeter"}
    if alea is not None and float(derive) <= float(alea):
        return {"decidable": False,
                "raison": f"la dérive ({round(float(derive), 4)} voxel) ne dépasse pas l'aléa qui "
                          f"la mesure ({round(float(alea), 4)}) : rien à projeter"}
    par_la_derive = combien_de_chunks_avant(float(derive), float(DEMI_PAS_EN_VOXELS))
    ref = reference.get("le_pas_quadratique_en_voxels")
    par_le_pas = (combien_de_chunks_avant(float(ref), float(DEMI_PAS_EN_VOXELS))
                  if ref else {"decidable": False, "raison": "le pas de `199` est absent"})
    return {"decidable": bool(par_la_derive.get("decidable")),
            "la_derive_en_voxels": round(float(derive), 4),
            "par_la_derive": par_la_derive,
            "le_pas_quadratique_de_199_en_voxels": ref,
            "par_le_pas_de_199": par_le_pas,
            "le_rapport_des_portees": (
                round(float(par_la_derive["les_chunks"]) / float(par_le_pas["les_chunks"]), 4)
                if par_la_derive.get("decidable") and par_le_pas.get("decidable")
                and par_le_pas["les_chunks"] else None)}


def une_couture_fabriquee(couches: int, rangees, pas_vrai: float, bruit_par_rangee: float,
                          graine: int) -> tuple[dict, dict]:
    """Une couture dont le pas est POSÉ et dont chaque rangée le lit avec sa propre erreur.

    ⭐ LE PAS EST LU PAR LE VRAI ESTIMATEUR, PAS ECRIT : la fixture decale le profil de droite d'un
    nombre de voxels et laisse `un_pas` le retrouver. Une fixture qui poserait directement le pas de
    chaque rangee testerait l'arithmetique de la moyenne et rien d'autre.

    ⚠ Le bruit est un decalage propre a chaque rangee : c'est la forme exacte que la prediction
    suppose — des erreurs independantes d'une rangee a l'autre — donc la face qui l'emploie mesure
    si l'instrument sait la lire, et la face sans pas mesure s'il sait se taire.
    """
    r = _rng(int(graine))
    marge = int(DEMI_PAS_EN_VOXELS) * 2 + 4
    fond = r.normal(0.0, 1.0, size=int(couches) + 2 * marge)
    droits, gauches = {}, {}
    for row in rangees:
        j = int(round(float(pas_vrai) + r.normal(0.0, float(bruit_par_rangee))))
        j = max(-marge, min(marge, j))
        droits[int(row)] = fond[marge:marge + int(couches)]
        gauches[int(row)] = fond[marge - j:marge - j + int(couches)]
    return droits, gauches


def une_rangee_fabriquee(coutures: int, couches: int, rangees, derive: float,
                         bruit_par_rangee: float, graine: int) -> dict:
    """Une suite de coutures dont les pas vrais sont tirés — la matière de l'étalon."""
    r = _rng(int(graine))
    vrais = r.normal(0.0, float(derive), size=int(coutures))
    lectures = {}
    for i, t in enumerate(vrais):
        d_, g_ = une_couture_fabriquee(couches, rangees, float(t), bruit_par_rangee,
                                       int(graine) + 17 * i + 1)
        for k in les_sous_ensembles(len(rangees)):
            lectures[(k, i)] = le_pas_de_k_rangees(d_, g_, un_sous_ensemble(rangees, k))
    return {"lectures": lectures, "les_pas_vrais": vrais,
            "les_coutures": list(range(int(coutures)))}


def sur_letalon(rangees, graine: int = GRAINE, coutures: int = 60, couches: int = 109,
                derive: float = 3.5, bruit_par_rangee: float = 6.0,
                replicats: int = 12) -> dict:
    """L'épreuve trouve-t-elle un pas posé, et se tait-elle quand il n'y en a aucun ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202` : avec
    `n` replicats le plus petit taux non nul vaut `1/n`, donc il en faut au moins `1/garantie` pour
    qu'un seul faux n'excede pas deja la garantie, et le double pour que deux ne l'excedent pas.

    ⭐ LA FACE NEGATIVE POSE UN PAS VRAI NUL ET GARDE LE MEME BRUIT : c'est le refus difficile, et le
    seul qui mesure quelque chose. Une face negative sans bruit du tout serait triviale a refuser.
    """
    k_max = max(les_sous_ensembles(len(rangees)))
    vus = 0
    derives = []
    for i in range(int(replicats)):
        f = une_rangee_fabriquee(coutures, couches, rangees, derive, bruit_par_rangee,
                                 int(graine) + 1000 * i)
        ep = la_couture_porte_un_pas(f["lectures"], k_max, f["les_coutures"])
        vus += int(bool(ep.get("la_couture_porte_un_pas")))
        cb = la_courbe(f["lectures"], les_sous_ensembles(len(rangees)), f["les_coutures"])
        if cb.get("decidable") and cb.get("sa_derive_en_voxels"):
            derives.append(float(cb["sa_derive_en_voxels"]))
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux = 0
    for i in range(replicats_du_refus):
        f = une_rangee_fabriquee(coutures, couches, rangees, 0.0, bruit_par_rangee,
                                 int(graine) + 500000 + 1000 * i)
        ep = la_couture_porte_un_pas(f["lectures"], k_max, f["les_coutures"])
        faux += int(bool(ep.get("la_couture_porte_un_pas")))
    return {"decidable": True, "le_pas_pose_en_voxels": float(derive),
            "le_bruit_par_rangee_en_voxels": float(bruit_par_rangee),
            "les_coutures_par_replicat": int(coutures), "les_rangees_maximales": int(k_max),
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


def la_ligne(volume: dict, delai: float = DELAI, colonnes: int | None = None,
             ouvrir=None, meta=None, combien: int = LES_RANGEES) -> dict:
    """Les profils de bord de chaque chunk, sur `combien` rangées — la MÊME rangée que `199`–`203`.

    ⭐ SEULS LES PROFILS DE BORD SONT GARDES : `un_pas` ne regarde que les `w` colonnes du bord, et
    il les moyenne. Garder le profil deja moyenne au lieu du chunk entier divise la memoire par
    plus de mille sans changer un seul nombre — une sonde le verifie plutot que de le supposer.
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
    w = int(la_largeur_du_bord())
    droits, gauches, refus, reprises = {}, {}, {}, 0
    rangees = None
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
        if rangees is None:
            rangees = les_rangees_a_lire(b.shape[1], combien)
        dr, ga = {}, {}
        for r_ in rangees:
            sec = une_section(b, r_)
            ww = max(1, min(w, sec.shape[1]))
            dr[int(r_)] = np.asarray(sec[:, -ww:].mean(axis=1), dtype=float)
            ga[int(r_)] = np.asarray(sec[:, :ww].mean(axis=1), dtype=float)
        droits[int(cx)], gauches[int(cx)] = dr, ga
    return {"decidable": bool(droits), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "le_cote_du_chunk": int(hx), "la_largeur_du_bord": w,
            "les_rangees_lues": (rangees or []),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(droits),
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "droits": droits, "gauches": gauches, "les_colonnes": voulues}


def juger(courbe: dict, epreuve: dict, croise: dict, portee: dict, k_max: int) -> dict:
    """Y a-t-il un pas au-delà du bruit, et à quel prix en rangées ?

    ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE, qui porte sur un compte de rangees POSE
    D'AVANCE — le plus grand lu. Aucune selection n'entre donc dans le verdict, et aucun prix de
    chercher n'est a payer : la courbe entiere est une description.
    """
    if not courbe.get("decidable") or not epreuve.get("decidable"):
        return {"decidable": False, "raison": "la courbe ou l'épreuve manque"}
    au_max = next((x for x in courbe["les_barreaux"] if x["les_rangees"] == int(k_max)), None)
    au_min = courbe["les_barreaux"][0] if courbe["les_barreaux"] else None
    return {"decidable": True,
            "les_rangees_de_lepreuve": int(k_max),
            "la_couture_porte_un_pas": bool(epreuve["la_couture_porte_un_pas"]),
            "la_valeur_p": epreuve["la_valeur_p"],
            "lalea_au_depart_en_voxels": (None if au_min is None
                                          else au_min["lalea_en_voxels"]),
            "lalea_au_maximum_en_voxels": (None if au_max is None
                                           else au_max["lalea_en_voxels"]),
            "le_rapport_observe_sur_predit_au_maximum": (
                None if au_max is None else au_max["le_rapport_observe_sur_predit"]),
            "la_dispersion_au_maximum_en_voxels": (
                None if au_max is None else au_max["la_dispersion_du_pas_en_voxels"]),
            "la_derive_au_maximum_en_voxels": (None if au_max is None
                                               else au_max["la_derive_en_voxels"]),
            "le_signal_sur_bruit_au_maximum": (None if au_max is None
                                               else au_max["le_signal_sur_bruit"]),
            "la_derive_par_le_creux_en_voxels": croise.get("la_derive_en_voxels"),
            "le_rapport_des_deux_derives": (
                round(float(au_max["la_derive_en_voxels"])
                      / float(croise["la_derive_en_voxels"]), 4)
                if au_max and au_max.get("la_derive_en_voxels")
                and croise.get("la_derive_en_voxels") else None),
            "la_portee_en_chunks": ((portee.get("par_la_derive") or {}).get("les_chunks")),
            "la_portee_en_mm": ((portee.get("par_la_derive") or {}).get("la_largeur_en_mm"))}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            combien: int = LES_RANGEES) -> dict:
    """La courbe par compte de rangées, l'épreuve au compte maximal, et la portée."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    lg = la_ligne(v, delai, colonnes, ouvrir, meta, combien)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celles de `199` à `203`",
                "la_ligne": {k: x for k, x in lg.items()
                             if k not in ("droits", "gauches", "les_colonnes")}}
    droits, gauches = lg["droits"], lg["gauches"]
    voisines = [(c, c + 1) for c in sorted(droits) if (c + 1) in droits]
    rangees = lg["les_rangees_lues"]
    comptes = les_sous_ensembles(len(rangees))
    lectures = {}
    for k in comptes:
        sous = un_sous_ensemble(rangees, k)
        for p in voisines:
            lectures[(k, p)] = le_pas_de_k_rangees(droits[p[0]], gauches[p[1]], sous)
    k_max = max(comptes)
    courbe = la_courbe(lectures, comptes, voisines)
    epreuve = la_couture_porte_un_pas(lectures, k_max, voisines)
    croise = ce_que_lappariement_a_rendu()
    m199 = ce_que_la_marche_a_rendu()
    au_max = next((x for x in courbe.get("les_barreaux") or []
                   if x["les_rangees"] == k_max), None)
    portee = la_portee(None if au_max is None else au_max.get("la_derive_en_voxels"),
                       None if au_max is None else au_max.get("lalea_en_voxels"), m199)
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "les_comptes_essayes": comptes,
        "la_ligne": {k: x for k, x in lg.items()
                     if k not in ("droits", "gauches", "les_colonnes")},
        "les_coutures_voisines": len(voisines),
        "ce_que_199_a_rendu": m199,
        "ce_que_202_a_rendu": croise,
        "la_courbe": courbe,
        "lepreuve": epreuve,
        "la_portee": portee,
        "le_verdict": juger(courbe, epreuve, croise, portee, k_max),
        "letalon": sur_letalon(rangees, graine, replicats=replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"COMBIEN DE RANGÉES FAUT-IL   indécidable : {r.get('raison')}")
        return
    lg, cb, ep = r["la_ligne"], r["la_courbe"], r["lepreuve"]
    po, ve, e = r["la_portee"], r["le_verdict"], r["letalon"]
    print(f"COMBIEN DE RANGÉES FAUT-IL   segment {lg['segment']} · rangée {lg['la_rangee']} · "
          f"{lg['colonnes_lues']} chunks lus sur {lg['colonnes_demandees']} · "
          f"{len(lg['les_rangees_lues'])} rangées · bord {lg['la_largeur_du_bord']} colonnes · "
          f"{r['les_coutures_voisines']} coutures")
    if cb.get("decidable"):
        print("  L'ALÉA            " + " · ".join(
            f"{x['les_rangees']}→{x['lalea_en_voxels']}" for x in cb["les_barreaux"]))
        print("  PRÉDIT (√k)       " + " · ".join(
            f"{x['les_rangees']}→{x['lalea_predit_en_voxels']}" for x in cb["les_barreaux"]))
        print("  OBSERVÉ / PRÉDIT  " + " · ".join(
            f"{x['les_rangees']}→{x['le_rapport_observe_sur_predit']}"
            for x in cb["les_barreaux"]))
        print("  LA DISPERSION     " + " · ".join(
            f"{x['les_rangees']}→{x['la_dispersion_du_pas_en_voxels']}"
            for x in cb["les_barreaux"]))
        print("  LA DÉRIVE         " + " · ".join(
            f"{x['les_rangees']}→{x['la_derive_en_voxels']}" for x in cb["les_barreaux"]))
        print("  SIGNAL / BRUIT    " + " · ".join(
            f"{x['les_rangees']}→{x['le_signal_sur_bruit']}" for x in cb["les_barreaux"]))
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         {ep['les_coutures_qui_portent_un_pas']} coutures portent un "
              f"pas sur {ep['les_coutures_informatives']} informatives (seuil "
              f"{ep['le_seuil_apparie']}) · P = {ep['la_valeur_p']} · porte "
              f"{ep['la_couture_porte_un_pas']}")
    if ve.get("decidable"):
        print(f"  LE VERDICT        dérive {ve['la_derive_au_maximum_en_voxels']} vx contre "
              f"{ve['la_derive_par_le_creux_en_voxels']} par le creux (`202`) · rapport "
              f"{ve['le_rapport_des_deux_derives']} · signal sur bruit "
              f"{ve['le_signal_sur_bruit_au_maximum']}")
    if po.get("decidable"):
        print(f"  LA PORTÉE         un demi-pli en {po['par_la_derive']['les_chunks']} chunks = "
              f"{po['par_la_derive']['la_largeur_en_mm']} mm · `199` en donnait "
              f"{po['par_le_pas_de_199']['les_chunks']}")
    else:
        print(f"  LA PORTÉE         refusée : {po.get('raison')}")
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · trouve {e['la_part_trouvee']} des "
          f"{e['replicats']} réplicats · dérive retrouvée "
          f"{e['la_derive_retrouvee_en_voxels']} pour {e['le_pas_pose_en_voxels']} posée · "
          f"{e['les_faux']} faux sur {e['les_replicats_du_refus']} = {e['le_taux_de_faux']} pour "
          f"{e['la_garantie']} garantis")


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
    v("★★ la rangée est la MÊME que celle de `199` à `203`", la_ligne_declaree(396) == 198)

    # ⚠⚠ LES RANGEES ET LES COMPTES SONT DERIVES DU CHUNK, PAS TAPES.
    rg = les_rangees_a_lire(128)
    v("★★★★ les rangées sont réparties uniformément et aucune ne touche un bord",
      len(rg) == 16 and rg[0] == 4 and rg[-1] == 124
      and len(set(np.diff(rg))) == 1, str(rg[:4]))
    v("★★★ un chunk plus petit en rend autant, mais plus serrées",
      les_rangees_a_lire(64) == [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62],
      str(les_rangees_a_lire(64)[:3]))
    v("★★★★ les comptes sont les puissances de deux à partir de DEUX — une seule rangée ne se "
      "coupe pas en deux", les_sous_ensembles(16) == [2, 4, 8, 16],
      str(les_sous_ensembles(16)))
    v("★★★★ les sous-ensembles sont EMBOÎTÉS et étalés sur toute la hauteur",
      set(un_sous_ensemble(rg, 2)) <= set(un_sous_ensemble(rg, 4))
      <= set(un_sous_ensemble(rg, 8)) <= set(un_sous_ensemble(rg, 16))
      and un_sous_ensemble(rg, 2) == [4, 68], str(un_sous_ensemble(rg, 4)))
    v("★★ un compte plus grand que le nombre de rangées ne rend rien",
      un_sous_ensemble(rg, 32) == [])

    # ⭐⭐⭐⭐ LE PROFIL MOYENNE D'AVANCE REND EXACTEMENT LE MEME PAS QUE LA BANDE ENTIERE.
    f0 = _rng(3).normal(0.0, 1.0, size=200)
    sg = np.tile(f0[60:60 + 109][:, None], (1, 64))
    sd_ = np.tile(f0[55:55 + 109][:, None], (1, 64))
    v("★★★★ le profil moyenné d'avance rend le MÊME pas que la bande entière",
      un_pas(sg, sd_, 16)["le_pas_en_voxels"]
      == le_pas_dune_rangee(sg[:, -16:].mean(axis=1), sd_[:, :16].mean(axis=1))
      ["le_pas_en_voxels"],
      f"{un_pas(sg, sd_, 16)['le_pas_en_voxels']} contre "
      f"{le_pas_dune_rangee(sg[:, -16:].mean(axis=1), sd_[:, :16].mean(axis=1))['le_pas_en_voxels']}")

    # ⚠⚠ LES DEUX DEMI-MOYENNES ALTERNENT, ET LE DESACCORD EST LEUR DIFFERENCE.
    dr = {r_: f0[60:60 + 109] for r_ in rg}
    ga = {r_: f0[60 - (2 if i % 2 == 0 else 8):60 - (2 if i % 2 == 0 else 8) + 109]
          for i, r_ in enumerate(rg)}
    lu = le_pas_de_k_rangees(dr, ga, rg)
    v("★★★★ les deux demi-moyennes ALTERNENT une rangée sur deux",
      lu["decidable"] and abs(lu["la_demi_moyenne_paire_en_voxels"] - 2.0) < 1e-9
      and abs(lu["la_demi_moyenne_impaire_en_voxels"] - 8.0) < 1e-9, str(lu))
    v("★★★ le pas publié est la moyenne des rangées",
      abs(lu["le_pas_en_voxels"] - 5.0) < 1e-9, str(lu["le_pas_en_voxels"]))
    v("★★★ et le désaccord est la différence des deux moitiés",
      abs(lu["le_desaccord_en_voxels"] + 6.0) < 1e-9, str(lu["le_desaccord_en_voxels"]))
    v("★★ moins de deux rangées lisibles est indécidable",
      not le_pas_de_k_rangees(dr, ga, [rg[0]]).get("decidable"))

    # ⭐⭐⭐⭐ LE NUL DE L'EPREUVE VAUT UN DEMI, ET IL SE VERIFIE PLUTOT QUE DE SE POSTULER.
    g1 = _rng(21)
    n_ = 40000
    A = g1.normal(0.0, 3.0, size=n_)
    B = g1.normal(0.0, 3.0, size=n_)
    part = float(np.mean(np.abs(A + B) > np.abs(A - B)))
    v("★★★★ sous AUCUN pas, la somme dépasse la différence exactement une fois sur deux",
      abs(part - 0.5) < 0.01, str(round(part, 4)))
    C = A + 6.0
    D = B + 6.0
    part2 = float(np.mean(np.abs(C + D) > np.abs(C - D)))
    v("★★★★ et avec un pas posé, elle la dépasse bien plus souvent",
      part2 > 0.8, str(round(part2, 4)))

    # ⭐⭐⭐⭐ L'EPREUVE SE DECLENCHE SUR UN PAS POSE ET SE TAIT SANS LUI.
    fab = une_rangee_fabriquee(60, 109, rg, 3.5, 6.0, 31)
    ep = la_couture_porte_un_pas(fab["lectures"], 16, fab["les_coutures"])
    v("★★★★ l'épreuve trouve un pas posé à trois voxels et demi",
      ep["decidable"] and ep["la_couture_porte_un_pas"], f"P = {ep['la_valeur_p']}")
    plat = une_rangee_fabriquee(60, 109, rg, 0.0, 6.0, 31)
    v("★★★★ et elle se tait quand le pas posé est nul",
      not la_couture_porte_un_pas(plat["lectures"], 16,
                                  plat["les_coutures"])["la_couture_porte_un_pas"])
    v("★★★ une couture où la somme égale la différence ne désigne personne",
      la_couture_porte_un_pas(
          {(4, 0): {"decidable": True, "le_pas_en_voxels": 1.0,
                    "le_desaccord_en_voxels": 2.0}}, 4, [0])["les_coutures_informatives"] == 0)

    # ⭐ LA PREDICTION EN RACINE DE k EST EXACTE, ET ELLE N'EST PAS L'EPREUVE.
    v("★★★★ l'aléa prédit décroît comme la racine du nombre de rangées",
      abs(lalea_predit(4.0, 2, 8) - 2.0) < 1e-12
      and abs(lalea_predit(4.0, 2, 32) - 1.0) < 1e-12, str(lalea_predit(4.0, 2, 8)))
    v("★★★ et il vaut la référence quand le compte ne bouge pas",
      abs(lalea_predit(4.0, 2, 2) - 4.0) < 1e-12)

    # ⚠⚠⚠ LA COURBE PUBLIE LA DISPERSION A COTE DE L'ALEA, ET L'ALEA EST LE DEMI ECART-TYPE.
    lect = {}
    g2 = _rng(5)
    for k in (2, 4, 8, 16):
        for i in range(200):
            lect[(k, i)] = {"decidable": True,
                            "le_pas_en_voxels": float(g2.normal(0.0, 5.0)),
                            "le_desaccord_en_voxels": float(g2.normal(0.0, 8.0))}
    cb = la_courbe(lect, [2, 4, 8, 16], list(range(200)))
    v("★★★★ l'aléa est le DEMI écart-type du désaccord",
      cb["decidable"] and abs(cb["les_barreaux"][0]["lalea_en_voxels"] - 4.0) < 0.5,
      str(cb["les_barreaux"][0]["lalea_en_voxels"]))
    # ⚠⚠⚠ LA SONDE LIT LA VALEUR, PAS SEULEMENT LA PRESENCE DE LA CLEF : un bris qui rendait une
    # dispersion CONSTANTE est reste vert tant qu'on ne verifiait que sa presence.
    v("★★★★ chaque barreau porte la DISPERSION du pas, et elle vient des données",
      all("la_dispersion_du_pas_en_voxels" in x for x in cb["les_barreaux"])
      and abs(cb["les_barreaux"][0]["la_dispersion_du_pas_en_voxels"] - 5.0) < 0.6,
      str(cb["les_barreaux"][0]["la_dispersion_du_pas_en_voxels"]))
    v("★★★★ et deux matières de dispersions différentes ne rendent pas le même nombre",
      la_courbe({(2, i): {"decidable": True, "le_pas_en_voxels": 20.0 * (1 if i % 2 else -1),
                          "le_desaccord_en_voxels": 1.0 * (1 if i % 2 else -1)}
                 for i in range(50)}, [2], list(range(50)))
      ["les_barreaux"][0]["la_dispersion_du_pas_en_voxels"]
      != cb["les_barreaux"][0]["la_dispersion_du_pas_en_voxels"])
    v("★★★★ une dispersion plus petite que l'aléa ne laisse AUCUNE dérive à extraire",
      la_courbe({(2, i): {"decidable": True, "le_pas_en_voxels": 0.1 * (i % 3),
                          "le_desaccord_en_voxels": 10.0 * (1 if i % 2 else -1)}
                 for i in range(50)}, [2], list(range(50)))
      ["les_barreaux"][0]["la_derive_en_voxels"] is None)
    v("★★★ et une dispersion plus grande en rend une",
      la_courbe({(2, i): {"decidable": True, "le_pas_en_voxels": 10.0 * (1 if i % 2 else -1),
                          "le_desaccord_en_voxels": 0.2 * (1 if i % 2 else -1)}
                 for i in range(50)}, [2], list(range(50)))
      ["les_barreaux"][0]["la_derive_en_voxels"] is not None)

    # ⚠⚠⚠ LA PORTEE REFUSE UNE DERIVE PLUS PETITE QUE SON ALEA — LE DEFAUT DE `203`.
    v("★★★★ une dérive plus petite que l'aléa qui la mesure est REFUSÉE",
      not la_portee(0.14, 0.24, {"le_pas_quadratique_en_voxels": 4.941}).get("decidable"))
    po = la_portee(3.4585, 1.2, {"le_pas_quadratique_en_voxels": 4.941})
    v("★★★★ et une dérive qui le dépasse se projette, par la fonction de `199`",
      po["decidable"] and po["par_la_derive"]["les_chunks"]
      == combien_de_chunks_avant(3.4585, float(DEMI_PAS_EN_VOXELS))["les_chunks"])
    v("★★★★ la portée du PAS de `199` est publiée À CÔTÉ, jamais écrasée",
      abs(po["par_le_pas_de_199"]["les_chunks"] - 53.09) < 0.5)
    v("★★ une dérive nulle ne se projette pas",
      not la_portee(0.0, 0.1, {"le_pas_quadratique_en_voxels": 4.941}).get("decidable"))

    # ⭐⭐⭐⭐ L'ETALON SEPARE SES DEUX FACES, ET LA NEGATIVE A ASSEZ DE REPLICATS.
    e = sur_letalon(rg, 11, coutures=40, replicats=4)
    v("★★★★ l'étalon trouve le pas posé sur tous ses réplicats",
      e["la_part_trouvee"] >= 1.0, str(e["la_part_trouvee"]))
    # ⚠⚠ LA SONDE LIT PAR `get` ET VERIFIE LA PRESENCE : sans cela, un bris pose sur la fixture
    # faisait tomber la batterie AVANT son verdict, donc le defaut se lisait comme une erreur
    # d'execution et non comme une sonde rouge.
    v("★★★★ et il retrouve la dérive posée",
      e.get("la_derive_retrouvee_en_voxels") is not None
      and abs(float(e["la_derive_retrouvee_en_voxels"])
              - float(e["le_pas_pose_en_voxels"])) < 0.6,
      f"{e.get('la_derive_retrouvee_en_voxels')} pour {e['le_pas_pose_en_voxels']}")
    v("★★★★ la face négative a ASSEZ de réplicats pour qu'un seul faux ne dépasse pas la garantie",
      e["les_replicats_du_refus"] >= int(1.0 / GARANTIE_PAR_EPREUVE)
      and 1.0 / float(e["les_replicats_du_refus"]) <= GARANTIE_PAR_EPREUVE,
      f"{e['les_replicats_du_refus']} réplicats")
    v("★★★★ et son taux de faux reste dans la garantie", e["letalon_separe"],
      f"{e['les_faux']} faux sur {e['les_replicats_du_refus']}")

    # ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE.
    faux_courbe = {"decidable": True, "les_barreaux": [
        {"les_rangees": 2, "lalea_en_voxels": 4.0, "lalea_predit_en_voxels": 4.0,
         "le_rapport_observe_sur_predit": 1.0, "la_dispersion_du_pas_en_voxels": 5.0,
         "la_derive_en_voxels": 3.0, "le_signal_sur_bruit": 0.75},
        {"les_rangees": 16, "lalea_en_voxels": 1.4, "lalea_predit_en_voxels": 1.4,
         "le_rapport_observe_sur_predit": 1.0, "la_dispersion_du_pas_en_voxels": 5.0,
         "la_derive_en_voxels": 4.8, "le_signal_sur_bruit": 3.4}]}
    jg = juger(faux_courbe, {"decidable": True, "la_couture_porte_un_pas": False,
                             "la_valeur_p": 0.4}, {"la_derive_en_voxels": 3.4585}, {}, 16)
    v("★★★★ un signal sur bruit flatteur ne suffit pas si l'épreuve ne se déclenche pas",
      not jg["la_couture_porte_un_pas"])
    jg2 = juger(faux_courbe, {"decidable": True, "la_couture_porte_un_pas": True,
                              "la_valeur_p": 0.0}, {"la_derive_en_voxels": 3.4585}, {}, 16)
    v("★★★★ et le verdict lit la dérive AU COMPTE DE L'ÉPREUVE, pas au premier barreau venu",
      abs(float(jg2["la_derive_au_maximum_en_voxels"]) - 4.8) < 1e-9,
      str(jg2["la_derive_au_maximum_en_voxels"]))
    v("★★★ le rapport au creux de `202` est dérivé des deux producteurs",
      abs(float(jg2["le_rapport_des_deux_derives"]) - round(4.8 / 3.4585, 4)) < 1e-9,
      str(jg2["le_rapport_des_deux_derives"]))
    v("★★ un verdict sans épreuve est indécidable",
      not juger(faux_courbe, {"decidable": False}, {}, {}, 16)["decidable"])

    meta = {"chunks": [109, 8, 8], "shape": [109, 24, 40]}
    v("★★★ un volume qui ne répond pas est refusé, jamais deviné",
      not la_ligne({"cle": "x", "segment": "s"}, 0.0, None,
                   lambda cy, cx: (None, "absent du dépôt"), meta)["decidable"])

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
