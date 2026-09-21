"""Le creux change-t-il avec la PROFONDEUR lue — et lit-il vraiment une frontière ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P54` QUI LE NOMME. `205` a isolé une quantité que rien
n'avait encore nommée : l'erreur du creux porte une composante **commune à un chunk**, de **14,9372
voxels**, qu'aucun découpage du PLAN n'atteint. C'est elle, et elle seule, qui interdit au repère
absolu de servir — donc c'est elle qu'il faut expliquer.

⭐⭐⭐⭐ ET LA SUITE SE COUPE DANS L'AUTRE SENS, PAR SYMÉTRIE EXACTE. `205` a découpé le chunk dans
le plan ; celle-ci le découpe en PROFONDEUR. Le cube fait **109 couches**, soit **1,5121 pli**, donc
il contient une frontière ou deux selon la phase — et si l'erreur commune vient de ce que le creux
désigne UNE frontière parmi celles que la fenêtre contient, alors elle doit CHANGER quand la fenêtre
raccourcit.

⭐⭐⭐⭐ LA PRÉDICTION SE POSE AVANT LA MESURE, ET ELLE EST GÉOMÉTRIQUE. Les frontières de pli sont
un réseau de période **72,0833 voxels** dont la phase est essentiellement uniforme — `200` l'a
mesuré, l'écart-type de la couche du creux vaut **0,9253** fois celui d'un tirage uniforme. Une
fenêtre de longueur `L` plus courte qu'un pli contient donc exactement une frontière avec la
probabilité `L / P`, et rien d'autre n'entre là-dedans. À un DEMI-pli, cette part vaut un demi.

⚠⚠⚠ ET C'EST CE QUI REND L'ÉPREUVE CAPABLE DE RÉFUTER LE LECTEUR. Si le creux se lit AUSSI SOUVENT
dans une fenêtre d'un demi-pli que dans une fenêtre qui en contient une et demie, alors il trouve un
creux là où il ne peut y avoir aucune frontière, et toute la courbe qui suit ne veut rien dire.
L'épreuve est donc une GARDE sur la description, pas un résultat de plus.

⚠⚠ LE PIÈGE EST CELUI DE `200`, ÉCRIT D'AVANCE : raccourcir la fenêtre change AUSSI le nombre de
couches texturées, donc le filtre du producteur. Le compte de chunks retenus est publié À CÔTÉ de
l'erreur à chaque profondeur, sinon une erreur qui baisse pourrait n'être que l'effet d'avoir jeté
les chunks difficiles.

Usage :
    uv run python src/nappe/le_creux_change_t_il_avec_la_profondeur_lue.py --verifier
    uv run python src/nappe/le_creux_change_t_il_avec_la_profondeur_lue.py \\
        --json docs/mesures/le_creux_change_t_il_avec_la_profondeur_lue.json
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
                                        la_ligne_declaree)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_creux_borne_t_il_la_marche import (la_courbe_dun_bloc,  # noqa: E402
                                           le_repere_dun_chunk)
from moyenner_le_creux_reduit_il_son_bruit import (la_couche_de_ces_sous_colonnes,  # noqa: E402
                                                   le_bruit_du_creux_de_202,
                                                   le_pas_dune_couture,
                                                   les_grilles_a_essayer,
                                                   les_lectures_requises,
                                                   les_sous_colonnes)
from ou_le_maillage_quitte_t_il_son_feuillet import (la_queue_haute_exacte,  # noqa: E402
                                                     le_segment_declare,
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)
from regarder_dans_la_profondeur import la_loi_appariee, le_seuil_apparie  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LE_PLAN_A_RENDU = MESURES / "moyenner_le_creux_reduit_il_son_bruit.json"
GRAINE = 20261014

LA_QUESTION_DECLAREE = ("l'erreur que toutes les sous-colonnes d'un chunk partagent change-t-elle "
                        "avec la profondeur lue, comme le ferait une frontière choisie parmi "
                        "plusieurs ?")
LES_EPREUVES_DECLAREES = ("les deux profondeurs lisent-elles la MÊME frontière",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def ce_que_le_plan_a_rendu(chemin: Path = CE_QUE_LE_PLAN_A_RENDU) -> dict:
    """L'erreur commune à un chunk que `205` a isolée — relue, jamais recalculée.

    ⚠⚠⚠ C'EST LA QUANTITE QUE CETTE TRANCHE EXPLIQUE, donc elle vient de son producteur et de nulle
    part ailleurs. La recalculer ici en ferait une seconde definition, libre de deriver de celle que
    `205` publie.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `205` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("le_bruit_de_chunk_en_voxels") is None:
        return {"decidable": False, "raison": "`205` ne publie pas d'erreur commune à un chunk"}
    return {"decidable": True,
            "le_bruit_de_chunk_en_voxels": v.get("le_bruit_de_chunk_en_voxels"),
            "lalea_en_voxels": v.get("lalea_au_maximum_en_voxels"),
            "les_sous_colonnes": v.get("les_sous_colonnes_de_lepreuve")}


def ce_que_179_a_rendu(chemin: Path | None = None) -> dict:
    """La transition juste suffisante que `179` a encadrée — relue, jamais retapée.

    ⚠⚠ C'EST CE NOMBRE QUI REFUTE LA PREMISSE DE `R4-P54`, donc il vient de son producteur. `179`
    l'a obtenu par bissection avec une tolerance derivee du voxel, et le retaper ici en ferait une
    valeur que rien ne tient a jour.
    """
    p = Path(chemin) if chemin is not None else (
        MESURES / "la_coherence_creuse_t_elle_a_la_frontiere.json")
    if not p.is_file():
        return {"decidable": False, "raison": "la mesure de `179` est absente"}
    d = json.loads(p.read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("il_vaut_le_voxel_fois") is None:
        return {"decidable": False, "raison": "`179` ne publie pas de transition en voxels"}
    return {"decidable": True,
            "la_transition_en_voxels": v.get("il_vaut_le_voxel_fois"),
            "la_transition_en_um": v.get("le_recouvrement_juste_suffisant_um"),
            "elle_vaut_le_pli_fois": v.get("il_vaut_le_pli_fois")}


def les_profondeurs_a_lire(couches: int, demi: float = DEMI_PAS_EN_VOXELS,
                           periode: float = PAS_EN_VOXELS) -> dict:
    """L'échelle des profondeurs, et la part de fenêtres qu'une frontière peut atteindre.

    ⚠⚠ L'ECHELLE EST CELLE DU PLI, PAS UN DECOUPAGE CHOISI. Son pas est le DEMI-PLI, qui est une
    constante publiee de la chaine, et ses barreaux sont les multiples de ce demi-pli qui tiennent
    dans le cube. Une echelle en puissances de deux aurait le meme nombre de barreaux et aucune
    frontiere ne tomberait dessus.

    ⭐⭐⭐⭐ ET LA PART ATTENDUE EST GEOMETRIQUE, PAS REGLEE : des frontieres de periode `P` dont la
    phase est uniforme tombent dans une fenetre de longueur `L < P` avec la probabilite `L / P`
    exactement, et dans une fenetre plus longue avec la probabilite un. C'est la prediction que
    l'epreuve met a l'essai, et elle ne contient aucun nombre choisi.

    ⚠ Le cube entier est gardé comme dernier barreau même quand un multiple du demi-pli en est tout
    proche : deux profondeurs qui ne diffèrent que d'une couche doivent rendre la même chose, et
    c'est un contrôle gratuit.
    """
    c = int(couches)
    barreaux = [int(demi) * k for k in range(1, int(c // int(demi)) + 1)]
    # ⚠⚠ UN SEUL GARDE, ET C'EST CELUI QUI DERIVE DE L'ECHELLE. Une premiere version en avait deux —
    # « le cube est plus court qu'un demi-pli » puis « l'echelle est vide » — et le second couvrait
    # deja le premier : un bris pose sur le premier restait donc invisible. Un garde qu'aucun bris
    # ne peut rendre rouge n'est pas un garde, c'est du texte.
    if not barreaux:
        return {"decidable": False,
                "raison": f"un cube de {c} couches ne porte aucun multiple du demi-pli, donc il "
                          f"est plus court qu'un demi-pli"}
    if barreaux[-1] != c:
        barreaux.append(c)
    return {"decidable": True,
            "les_profondeurs": barreaux,
            "les_plis_par_profondeur": [round(float(x) / float(periode), 4) for x in barreaux],
            "la_part_attendue_par_profondeur": [round(min(1.0, float(x) / float(periode)), 4)
                                                for x in barreaux],
            "la_profondeur_la_plus_courte": int(barreaux[0]),
            "la_profondeur_de_reference": int(barreaux[-1]),
            "le_demi_pli_en_voxels": int(demi),
            "le_pas_dun_pli_en_voxels": round(float(periode), 4)}


def le_debut_dune_sous_tranche(couches: int, profondeur: int) -> int:
    """Où commence une sous-tranche — au MILIEU du cube, toujours.

    ⚠⚠⚠ LE CENTRAGE EST CE QUI EMPECHE DEUX EFFETS DE SE CONFONDRE. Une sous-tranche prise en haut
    du cube serait a la fois plus courte ET ailleurs, donc un changement d'erreur ne dirait pas
    lequel des deux l'a produit. Centrees, toutes les profondeurs lisent le meme milieu.
    """
    return max(0, (int(couches) - int(profondeur)) // 2)


def la_couche_dune_sous_colonne_a_cette_profondeur(bloc, tuile: dict, profondeur: int,
                                                   permutations: int = PERMUTATIONS,
                                                   graine: int = GRAINE) -> dict:
    """La couche du creux lue dans une sous-colonne ET une sous-tranche, RENDUE AU CUBE.

    ⚠⚠⚠ L'OFFSET DE LA SOUS-TRANCHE EST RAJOUTE, ET C'EST INDISPENSABLE. Le lecteur rend un indice
    dans la fenetre qu'on lui donne ; sans le decalage, une fenetre courte rendrait des couches dans
    SON repere et les pas d'une profondeur a l'autre cesseraient d'etre comparables. Un nombre juste
    sous un mauvais nom, et celui-la ne se verrait pas.

    ⚠ Le filtre du producteur est celui de `14` et de `176`, relu et non choisi, et il s'applique a
    la sous-tranche : un quart de SES couches doit depasser le plancher de coherence.
    """
    b = np.asarray(bloc)
    debut = le_debut_dune_sous_tranche(b.shape[0], profondeur)
    tranche = b[debut:debut + int(profondeur),
                int(tuile["y0"]):int(tuile["y1"]), int(tuile["x0"]):int(tuile["x1"])]
    if tranche.shape[0] < 2 or tranche.shape[1] < 3 or tranche.shape[2] < 3:
        return {"iy": int(tuile["iy"]), "ix": int(tuile["ix"]), "la_couche": None,
                "pourquoi": "sous-tranche plus petite que l'opérateur"}
    courbe, quoi = la_courbe_dun_bloc(tranche)
    if courbe is None:
        return {"iy": int(tuile["iy"]), "ix": int(tuile["ix"]), "la_couche": None,
                "pourquoi": quoi}
    lu = le_repere_dun_chunk(courbe, permutations, graine)
    couche = lu.get("la_couche")
    return {"iy": int(tuile["iy"]), "ix": int(tuile["ix"]),
            "le_debut_de_la_tranche": int(debut),
            "la_couche": (None if couche is None else int(couche) + int(debut)),
            "pourquoi": (None if lu.get("lisible") else "aucun creux au-dessus de ses mélanges")}


def la_fenetre_effective(profondeurs, transition, periode: float = PAS_EN_VOXELS) -> dict:
    """Ce qu'une fenêtre lit VRAIMENT, transition comprise — et pourquoi la géométrie ne tranche pas.

    ⚠⚠⚠ C'EST LA PREMISSE DE `R4-P54` REFUTEE PAR UN CHIFFRE DEJA PUBLIE. La porte annonçait qu'une
    sous-tranche de moins d'un pli DEVAIT ne rien rendre, en s'appuyant sur le contrôle vide de
    `179`. Mais `179` a aussi mesuré la largeur de la TRANSITION — le recouvrement juste suffisant —
    et une frontière située jusqu'à cette distance HORS de la fenêtre incline encore la cohérence
    DEDANS. La fenêtre effective vaut donc la fenêtre plus deux transitions, et à ces profondeurs
    elle couvre déjà tout l'intervalle entre frontières : une épreuve bâtie sur le compte de
    fenêtres lisibles n'aurait aucun pouvoir de discriminer, quel que soit le résultat.

    ⚠ La transition est RELUE de `179`, jamais tapée : c'est le nombre que sa bissection a rendu.
    """
    if transition is None:
        return {"decidable": False, "raison": "`179` ne publie pas de transition"}
    t_ = float(transition)
    lignes = []
    for d_ in profondeurs:
        effective = float(d_) + 2.0 * t_
        lignes.append({"la_profondeur": int(d_),
                       "la_fenetre_effective_en_voxels": round(effective, 4),
                       "elle_vaut_le_pas_fois": round(effective / float(periode), 4)})
    return {"decidable": True, "la_transition_de_179_en_voxels": round(t_, 4),
            "les_fenetres": lignes,
            "la_geometrie_peut_elle_discriminer": bool(
                any(x["elle_vaut_le_pas_fois"] < 1.0 for x in lignes))}


def les_deux_profondeurs_saccordent(couches_lues: dict, courte: int, longue: int,
                                    periode: float = PAS_EN_VOXELS,
                                    tirages: int = PERMUTATIONS, graine: int = GRAINE,
                                    garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """L'ÉPREUVE : les deux profondeurs marquent-elles la MÊME frontière ?

    ⭐⭐⭐⭐ LE NUL EST UNE PERMUTATION, ET C'EST CE QUI LE REND VALIDE ICI. Un nul uniforme aurait
    demandé de savoir à quelle période les frontières se répètent — or `179` mesure un intervalle de
    36 couches là où `200` replie par 72,0833, et cette tranche n'a pas de quoi trancher. Une
    permutation n'a besoin d'aucune période : elle apparie la lecture courte d'un chunk à la lecture
    longue d'un AUTRE, et le repli s'applique de la même façon des deux côtés.

    ⭐ LA STATISTIQUE EST LA MÉDIANE DE L'ÉCART REPLIÉ, et elle est du bon côté : deux profondeurs
    qui marquent la même frontière rendent un écart petit, donc l'observé doit être SOUS ses
    mélanges. Une médiane plutôt qu'une moyenne parce qu'un chunk calé un pli plus loin ne doit pas
    emporter le verdict à lui seul.

    ⚠⚠ ET C'EST UNE GARDE SUR LA DESCRIPTION, PAS UN RESULTAT DE PLUS : si les deux profondeurs ne
    lisent pas la même chose, comparer leurs erreurs n'a aucun sens.
    """
    a, b = [], []
    for c, par in couches_lues.items():
        x, y = par.get(int(courte)), par.get(int(longue))
        if x is None or y is None:
            continue
        a.append(float(x))
        b.append(float(y))
    if len(a) < 3:
        return {"decidable": False, "raison": "moins de trois chunks lisibles aux deux profondeurs"}
    import peut_on_deplier_la_phase as D  # noqa: PLC0415
    aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    observee = float(np.median(np.abs(np.asarray(D.le_repli(aa - bb, periode), dtype=float))))
    r = _rng(int(graine))
    melanges = []
    for _ in range(int(tirages)):
        melange = bb[r.permutation(len(bb))]
        melanges.append(float(np.median(np.abs(
            np.asarray(D.le_repli(aa - melange, periode), dtype=float)))))
    au_moins_aussi_bas = int(sum(1 for m in melanges if m <= observee))
    pv = (1.0 + au_moins_aussi_bas) / (1.0 + float(tirages))
    return {"decidable": True,
            "la_profondeur_courte": int(courte), "la_profondeur_longue": int(longue),
            "les_chunks_lus_aux_deux": len(a),
            "lecart_median_replie_en_voxels": round(observee, 4),
            "lecart_median_des_melanges_en_voxels": round(float(np.median(melanges)), 4),
            "les_melanges_au_moins_aussi_bas": au_moins_aussi_bas,
            "les_tirages": int(tirages),
            "la_valeur_p": round(float(pv), 7),
            "la_garantie_de_lepreuve": round(float(garantie), 7),
            "elles_lisent_la_meme_frontiere": bool(pv <= float(garantie) + 1e-12)}


def la_courbe_par_profondeur(lectures: dict, lisibles: dict, profondeurs, coutures,
                             cible, parts_attendues) -> dict:
    """L'aléa, la dispersion et l'erreur commune, profondeur par profondeur.

    ⚠⚠⚠ LE COMPTE DE CHUNKS LISIBLES EST PUBLIE A COTE DE L'ERREUR, TOUJOURS — le piege de `200`
    ecrit d'avance. Raccourcir la fenetre change le filtre du producteur, donc une erreur qui baisse
    pourrait n'etre que l'effet d'avoir jete les chunks difficiles.

    ⚠⚠ L'ERREUR COMMUNE EST CELLE DE `205`, CALCULEE DE LA MEME FACON : ce que la dispersion du pas
    laisse une fois le desaccord entre sous-colonnes retire, moins la derive que `202` attribue au
    creux. Elle se refute par ses propres nombres si la difference des carres est negative.
    """
    barreaux = []
    for d_, attendue in zip(profondeurs, parts_attendues):
        pas, des = [], []
        for p in coutures:
            lu = lectures.get((int(d_), p))
            if lu is None or not lu.get("decidable"):
                continue
            pas.append(float(lu["le_pas_en_voxels"]))
            des.append(float(lu["le_desaccord_en_voxels"]))
        lus = sum(1 for x in lisibles.values() if x.get(int(d_)))
        if len(pas) < 3:
            barreaux.append({"la_profondeur": int(d_), "les_chunks_lisibles": int(lus),
                             "la_part_attendue": round(float(attendue), 4),
                             "les_coutures": len(pas), "lalea_en_voxels": None,
                             "la_dispersion_du_pas_en_voxels": None,
                             "lerreur_commune_en_voxels": None, "le_signal_sur_bruit": None})
            continue
        alea = float(np.std(np.asarray(des, dtype=float))) / 2.0
        disp = float(np.std(np.asarray(pas, dtype=float)))
        reste = (disp * disp - alea * alea) if disp > alea else None
        commune = None
        if reste is not None and cible is not None:
            r2 = reste - float(cible) ** 2
            commune = (round(r2 ** 0.5, 4) if r2 > 0.0 else None)
        barreaux.append({
            "la_profondeur": int(d_), "les_chunks_lisibles": int(lus),
            "la_part_attendue": round(float(attendue), 4),
            "les_coutures": len(pas),
            "lalea_en_voxels": round(alea, 4),
            "la_dispersion_du_pas_en_voxels": round(disp, 4),
            "lerreur_commune_en_voxels": commune,
            "le_signal_sur_bruit": (None if commune is None or alea <= 0
                                    else round(float(commune) / alea, 4))})
    lisibles_ = [x for x in barreaux if x["lerreur_commune_en_voxels"] is not None]
    if not lisibles_:
        return {"decidable": False, "raison": "aucune profondeur ne rend d'erreur commune",
                "les_barreaux": barreaux}
    plus_courte, plus_longue = lisibles_[0], lisibles_[-1]
    return {"decidable": True, "les_barreaux": barreaux,
            "les_profondeurs_qui_rendent_une_erreur": [x["la_profondeur"] for x in lisibles_],
            "lerreur_a_la_plus_courte_en_voxels": plus_courte["lerreur_commune_en_voxels"],
            "lerreur_a_la_plus_longue_en_voxels": plus_longue["lerreur_commune_en_voxels"],
            "le_rapport_des_deux_erreurs": (
                round(float(plus_courte["lerreur_commune_en_voxels"])
                      / float(plus_longue["lerreur_commune_en_voxels"]), 4)
                if plus_longue["lerreur_commune_en_voxels"] else None)}


def juger(courbe: dict, epreuve: dict, echelle: dict, fenetre: dict, par_le_plan: dict,
          par_le_creux: dict) -> dict:
    """Les deux profondeurs lisent-elles la même frontière, et l'erreur commune bouge-t-elle ?

    ⚠⚠⚠ L'EPREUVE EST UNE GARDE, PAS UN RESULTAT DE PLUS, et c'est pour ca que le verdict la porte
    en premier : si les deux profondeurs ne marquent pas la meme frontiere, comparer leurs erreurs
    ne veut rien dire.

    ⚠⚠ ET LA COMPARAISON DES ERREURS D'UNE PROFONDEUR A L'AUTRE EST UNE DESCRIPTION, PAS UNE
    EPREUVE. Une seule epreuve est declaree, donc la garantie reste entiere ; departager deux
    erreurs derivees demanderait une seconde epreuve et un second nul, et cette tranche n'en declare
    pas.
    """
    if not epreuve.get("decidable"):
        return {"decidable": False, "raison": "l'épreuve manque"}
    bar = (courbe.get("les_barreaux") or [])
    return {"decidable": True,
            "la_profondeur_courte": epreuve["la_profondeur_courte"],
            "la_profondeur_longue": epreuve["la_profondeur_longue"],
            "les_chunks_lus_aux_deux": epreuve["les_chunks_lus_aux_deux"],
            "lecart_median_replie_en_voxels": epreuve["lecart_median_replie_en_voxels"],
            "lecart_median_des_melanges_en_voxels": epreuve[
                "lecart_median_des_melanges_en_voxels"],
            "la_valeur_p": epreuve["la_valeur_p"],
            "elles_lisent_la_meme_frontiere": bool(epreuve["elles_lisent_la_meme_frontiere"]),
            "les_profondeurs": echelle.get("les_profondeurs"),
            "les_plis_par_profondeur": echelle.get("les_plis_par_profondeur"),
            "la_transition_de_179_en_voxels": fenetre.get("la_transition_de_179_en_voxels"),
            "la_geometrie_peut_elle_discriminer": fenetre.get(
                "la_geometrie_peut_elle_discriminer"),
            "lerreur_a_la_plus_courte_en_voxels": courbe.get(
                "lerreur_a_la_plus_courte_en_voxels"),
            "lerreur_a_la_plus_longue_en_voxels": courbe.get(
                "lerreur_a_la_plus_longue_en_voxels"),
            "le_rapport_des_deux_erreurs": courbe.get("le_rapport_des_deux_erreurs"),
            "lerreur_que_205_a_isolee_en_voxels": par_le_plan.get("le_bruit_de_chunk_en_voxels"),
            "la_derive_visee_par_202_en_voxels": par_le_creux.get("la_derive_en_voxels"),
            "les_chunks_lisibles_par_profondeur": [
                {"la_profondeur": x["la_profondeur"],
                 "les_chunks_lisibles": x["les_chunks_lisibles"]} for x in bar]}


def une_courbe_a_cette_profondeur(profondeur: int, frontieres, debut: int, bruit: float,
                                  largeur: float, rng) -> list:
    """La courbe de cohérence d'une fenêtre : un creux là où une frontière y tombe, rien sinon.

    ⭐⭐⭐⭐ C'EST LE CONTROLE VIDE DE `179`, PORTE DANS LA FIXTURE : une fenetre qui ne contient
    aucune frontiere rend une courbe PLATE bruitee, et le lecteur doit s'y taire. Une fixture qui
    mettrait un creux partout ne mesurerait que la capacite du lecteur a trouver ce qu'on lui a
    donne.
    """
    z = np.arange(int(profondeur), dtype=float)
    coh = 0.6 + rng.normal(0.0, float(bruit), size=int(profondeur))
    for f in frontieres:
        local = float(f) - float(debut)
        if -float(largeur) <= local < float(profondeur) + float(largeur):
            coh = coh - 0.45 * np.exp(-0.5 * ((z - local) / (float(largeur) / 2.0)) ** 2)
    return [[0.0, float(max(0.0, x))] for x in coh]


def un_chunk_fabrique_en_profondeur(couches: int, profondeurs, phase: float,
                                    periode: float = PAS_EN_VOXELS, bruit: float = 0.05,
                                    largeur: float = 9.0, graine: int = GRAINE,
                                    permutations: int = PERMUTATIONS,
                                    phases_independantes: bool = False) -> dict:
    """Un chunk dont les frontières forment un RÉSEAU de période posée, lu à chaque profondeur.

    ⭐⭐⭐⭐ LA COUCHE EST LUE PAR LE VRAI LECTEUR ET RENDUE AU CUBE, jamais ecrite par la fixture.
    C'est ce qui fait de l'etalon un controle plutot qu'une petition de principe : deux profondeurs
    qui s'accordent doivent s'accorder parce que le lecteur a retrouve la meme frontiere, pas parce
    qu'on la lui a posee deux fois.

    ⚠⚠ `phases_independantes` CONSTRUIT LA FACE NEGATIVE : chaque profondeur recoit son propre
    reseau, donc sa lecture n'a rien a voir avec celle des autres. C'est exactement ce que le nul
    par permutation decrit, et le seul refus qui mesure quelque chose.
    """
    r = _rng(int(graine))
    lues = {}
    for d_ in profondeurs:
        ph = float(r.uniform(0.0, float(periode))) if phases_independantes else float(phase)
        k0 = int(np.floor(-ph / float(periode))) - 1
        k1 = int(np.ceil((float(couches) - ph) / float(periode))) + 1
        frontieres = [ph + float(periode) * k for k in range(k0, k1 + 1)]
        debut = le_debut_dune_sous_tranche(couches, int(d_))
        courbe = une_courbe_a_cette_profondeur(int(d_), frontieres, debut, bruit, largeur, r)
        lu = le_repere_dun_chunk(courbe, int(permutations), int(graine) + 13 * int(d_))
        couche = lu.get("la_couche")
        lues[int(d_)] = (None if couche is None else int(couche) + int(debut))
    return lues


def sur_letalon(profondeurs, echelle: dict, graine: int = GRAINE, chunks: int = 60,
                couches: int = 109, bruit: float = 0.05, replicats: int = 12,
                permutations: int = PERMUTATIONS,
                tirages_de_lepreuve: int = PERMUTATIONS) -> dict:
    """L'épreuve voit-elle deux profondeurs qui s'accordent, et se tait-elle quand elles ne le
    font pas ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202`.
    ⭐ LA FACE POSITIVE EST LA MATIERE HONNETE : un seul reseau de plis, lu a deux profondeurs, qui
    doit rendre la meme frontiere. LA FACE NEGATIVE donne a chaque profondeur son propre reseau,
    donc deux lectures sans rapport — c'est le refus difficile, et le seul qui mesure quelque chose.

    ⚠⚠⚠ LES DEUX COMPTES DE TIRAGES SONT SEPARES, ET C'EST UNE REPARATION. `permutations` est celui
    du LECTEUR de creux — il price la largeur du creux, dans `179` — et `tirages_de_lepreuve` est
    celui du NUL de cette tranche. Les confondre plafonne la valeur p de l'epreuve au premier des
    deux : une sonde qui abaissait le lecteur pour aller vite rendait l'epreuve incapable de
    descendre sous un huitieme, donc incapable de REUSSIR, et l'etalon accusait le code.
    """
    courte = int(echelle["la_profondeur_la_plus_courte"])
    ref = int(echelle["la_profondeur_de_reference"])
    # ⚠⚠⚠ UN ETALON DONT L'EPREUVE NE PEUT PAS ATTEINDRE LA GARANTIE NE MESURE RIEN, et il se
    # REFUSE plutot que de rendre une face positive vide qu'on lirait comme un instrument casse.
    # La plus petite valeur p qu'une permutation puisse rendre vaut un sur un plus le nombre de
    # tirages : si elle est deja au-dessus de la garantie, aucune matiere ne fera reussir l'epreuve.
    plus_petite_p = 1.0 / (1.0 + float(tirages_de_lepreuve))
    if plus_petite_p > float(GARANTIE_PAR_EPREUVE) + 1e-12:
        return {"decidable": False,
                "raison": f"{int(tirages_de_lepreuve)} tirages ne descendent pas sous "
                          f"{round(float(GARANTIE_PAR_EPREUVE), 4)} : la plus petite valeur p "
                          f"atteignable vaut {round(plus_petite_p, 4)}"}
    vus, ecarts = 0, []
    r = _rng(int(graine))
    for i in range(int(replicats)):
        lues = {}
        for c in range(int(chunks)):
            lues[c] = un_chunk_fabrique_en_profondeur(
                couches, profondeurs, float(r.uniform(0.0, PAS_EN_VOXELS)), bruit=bruit,
                graine=int(graine) + 1000 * i + 7 * c, permutations=permutations)
        ep = les_deux_profondeurs_saccordent(lues, courte, ref, PAS_EN_VOXELS,
                                             int(tirages_de_lepreuve), int(graine) + i)
        vus += int(bool(ep.get("elles_lisent_la_meme_frontiere")))
        if ep.get("decidable"):
            ecarts.append(float(ep["lecart_median_replie_en_voxels"]))
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux, ecarts_sans = 0, []
    for i in range(replicats_du_refus):
        lues = {}
        for c in range(int(chunks)):
            lues[c] = un_chunk_fabrique_en_profondeur(
                couches, profondeurs, 0.0, bruit=bruit,
                graine=int(graine) + 500000 + 1000 * i + 7 * c, permutations=permutations,
                phases_independantes=True)
        ep = les_deux_profondeurs_saccordent(lues, courte, ref, PAS_EN_VOXELS,
                                             int(tirages_de_lepreuve), int(graine) + 77 + i)
        faux += int(bool(ep.get("elles_lisent_la_meme_frontiere")))
        if ep.get("decidable"):
            ecarts_sans.append(float(ep["lecart_median_replie_en_voxels"]))
    return {"decidable": True,
            "la_profondeur_courte": courte, "la_profondeur_longue": ref,
            "les_chunks_par_replicat": int(chunks),
            "replicats": int(replicats), "les_vus": int(vus),
            "les_tirages_de_lepreuve": int(tirages_de_lepreuve),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "lecart_median_sur_la_face_positive_en_voxels": (
                round(float(np.median(ecarts)), 4) if ecarts else None),
            "les_replicats_du_refus": int(replicats_du_refus), "les_faux": int(faux),
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "lecart_median_sur_la_face_negative_en_voxels": (
                round(float(np.median(ecarts_sans)), 4) if ecarts_sans else None),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= replicats
                                   and faux / float(replicats_du_refus)
                                   <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)}


def la_ligne(volume: dict, profondeurs, grille: int, delai: float = DELAI,
             colonnes: int | None = None, permutations: int = PERMUTATIONS,
             graine: int = GRAINE, ouvrir=None, meta=None) -> dict:
    """Le creux de chaque sous-colonne, à chaque profondeur — la MÊME rangée que `199` à `205`.

    ⚠⚠⚠ TOUTES LES PROFONDEURS SORTENT DU MEME TELECHARGEMENT. Les lire en plusieurs passes en
    ferait plusieurs rangees, et la comparaison des barreaux entre eux cesserait d'en etre une.
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
    lues, lisibles, refus, reprises = {}, {}, {}, 0
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
        tuiles = les_sous_colonnes(b.shape[1], b.shape[2], int(grille))
        par_profondeur, lu_par_profondeur = {}, {}
        for d_ in profondeurs:
            lectures = [la_couche_dune_sous_colonne_a_cette_profondeur(
                b, t, int(d_), permutations,
                int(graine) + 31 * int(cx) + 101 * int(d_) + 7 * int(t["iy"]) + int(t["ix"]))
                for t in tuiles]
            r_ = la_couche_de_ces_sous_colonnes(lectures)
            par_profondeur[int(d_)] = r_
            lu_par_profondeur[int(d_)] = bool(r_.get("decidable"))
        lues[int(cx)] = par_profondeur
        lisibles[int(cx)] = lu_par_profondeur
    return {"decidable": bool(lues), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "le_cote_du_chunk_en_pixels": int(min(hy, hx)),
            "les_couches_du_cube": int(meta["chunks"][0]),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(lues),
            "la_grille_du_plan": int(grille), "les_sous_colonnes": int(grille) * int(grille),
            "les_profondeurs": [int(x) for x in profondeurs],
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "lues": lues, "lisibles": lisibles, "les_colonnes": voulues}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            chunks_de_letalon: int = 60) -> dict:
    """L'échelle des profondeurs, la courbe, l'épreuve d'accord et l'étalon."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    if meta is None:
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    couches, hy, hx = meta["chunks"]
    echelle = les_profondeurs_a_lire(int(couches))
    if not echelle.get("decidable"):
        return {"decidable": False, "raison": echelle.get("raison")}
    par_le_creux = le_bruit_du_creux_de_202()
    par_le_plan = ce_que_le_plan_a_rendu()
    par_179 = ce_que_179_a_rendu()
    fenetre = la_fenetre_effective(echelle["les_profondeurs"],
                                   par_179.get("la_transition_en_voxels"))
    prediction = les_lectures_requises(par_le_creux.get("le_bruit_du_creux_en_voxels"),
                                       par_le_creux.get("la_derive_en_voxels"))
    plan = les_grilles_a_essayer(int(min(hy, hx)), prediction.get("les_lectures_requises"))
    if not plan.get("decidable"):
        return {"decidable": False, "raison": plan.get("raison")}
    grille = plan["les_grilles"][-1]
    profondeurs = echelle["les_profondeurs"]
    lg = la_ligne(v, profondeurs, grille, delai, colonnes, PERMUTATIONS, graine, ouvrir, meta)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celles de `199` à `205`",
                "la_ligne": {k: x for k, x in lg.items()
                             if k not in ("lues", "lisibles", "les_colonnes")}}
    lues, lisibles = lg["lues"], lg["lisibles"]
    voisines = [(c, c + 1) for c in sorted(lues) if (c + 1) in lues]
    lectures = {}
    for d_ in profondeurs:
        for a, b in voisines:
            lectures[(int(d_), (a, b))] = le_pas_dune_couture(lues[a][int(d_)], lues[b][int(d_)])
    couches_lues = {c: {int(d_): (par[int(d_)].get("la_couche_en_voxels")
                                  if par[int(d_)].get("decidable") else None)
                        for d_ in profondeurs}
                    for c, par in lues.items()}
    courbe = la_courbe_par_profondeur(lectures, lisibles, profondeurs, voisines,
                                      par_le_creux.get("la_derive_en_voxels"),
                                      echelle["la_part_attendue_par_profondeur"])
    epreuve = les_deux_profondeurs_saccordent(
        couches_lues, echelle["la_profondeur_la_plus_courte"],
        echelle["la_profondeur_de_reference"], PAS_EN_VOXELS, PERMUTATIONS, graine)
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "lechelle_des_profondeurs": echelle,
        "la_fenetre_effective": fenetre,
        "la_grille_du_plan": int(grille),
        "ce_que_179_a_rendu": par_179,
        "ce_que_202_a_rendu": par_le_creux,
        "ce_que_205_a_rendu": par_le_plan,
        "la_ligne": {k: x for k, x in lg.items()
                     if k not in ("lues", "lisibles", "les_colonnes")},
        "les_coutures_voisines": len(voisines),
        "la_courbe": courbe,
        "lepreuve": epreuve,
        "le_verdict": juger(courbe, epreuve, echelle, fenetre, par_le_plan, par_le_creux),
        "letalon": sur_letalon(profondeurs, echelle, graine, chunks=chunks_de_letalon,
                               couches=int(couches), replicats=replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    lg = r.get("la_ligne") or {}
    ec = r.get("lechelle_des_profondeurs") or {}
    fe = r.get("la_fenetre_effective") or {}
    print(f"LE CREUX CHANGE-T-IL AVEC LA PROFONDEUR LUE   segment {lg.get('segment')} · "
          f"rangée {lg.get('la_rangee')} · {lg.get('colonnes_lues')} chunks lus sur "
          f"{lg.get('colonnes_demandees')} · cube {lg.get('les_couches_du_cube')} couches · "
          f"{lg.get('les_sous_colonnes')} sous-colonnes")
    print(f"  LES PROFONDEURS   {ec.get('les_profondeurs')} couches · plis "
          f"{ec.get('les_plis_par_profondeur')}")
    if fe.get("decidable"):
        print(f"  LA FENÊTRE VRAIE  transition de `179` {fe['la_transition_de_179_en_voxels']} "
              f"voxels · effectives "
              f"{[x['la_fenetre_effective_en_voxels'] for x in fe['les_fenetres']]} = "
              f"{[x['elle_vaut_le_pas_fois'] for x in fe['les_fenetres']]} pas · la géométrie "
              f"discrimine {fe['la_geometrie_peut_elle_discriminer']}")
    cb = r.get("la_courbe") or {}
    for nom, clef in (("CHUNKS LISIBLES", "les_chunks_lisibles"),
                      ("LES COUTURES", "les_coutures"),
                      ("L'ALÉA", "lalea_en_voxels"),
                      ("LA DISPERSION", "la_dispersion_du_pas_en_voxels"),
                      ("L'ERREUR COMMUNE", "lerreur_commune_en_voxels"),
                      ("SIGNAL / BRUIT", "le_signal_sur_bruit")):
        print(f"  {nom:<17} " + " · ".join(
            f"{x['la_profondeur']}→{x[clef]}" for x in (cb.get("les_barreaux") or [])))
    ep = r.get("lepreuve") or {}
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         écart médian replié "
              f"{ep['lecart_median_replie_en_voxels']} voxels contre "
              f"{ep['lecart_median_des_melanges_en_voxels']} au mélange · "
              f"{ep['les_melanges_au_moins_aussi_bas']}/{ep['les_tirages']} · P = "
              f"{ep['la_valeur_p']} · même frontière "
              f"{ep['elles_lisent_la_meme_frontiere']} sur {ep['les_chunks_lus_aux_deux']} chunks")
    ve = r.get("le_verdict") or {}
    if ve.get("decidable"):
        print(f"  LE VERDICT        erreur commune {ve['lerreur_a_la_plus_courte_en_voxels']} à la "
              f"plus courte contre {ve['lerreur_a_la_plus_longue_en_voxels']} à la plus longue · "
              f"rapport {ve['le_rapport_des_deux_erreurs']}")
        print(f"                    `205` en isolait {ve['lerreur_que_205_a_isolee_en_voxels']} "
              f"voxels, `202` vise {ve['la_derive_visee_par_202_en_voxels']}")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats (écart "
              f"{et['lecart_median_sur_la_face_positive_en_voxels']}) · {et['les_faux']} faux sur "
              f"{et['les_replicats_du_refus']} = {et['le_taux_de_faux']} pour "
              f"{et['la_garantie']} garantis (écart "
              f"{et['lecart_median_sur_la_face_negative_en_voxels']})")


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
    v("★★ la rangée est la MÊME que celle de `199` à `205`", la_ligne_declaree(396) == 198)

    # ⚠⚠ L'ECHELLE EST CELLE DU PLI, ET LA PART ATTENDUE EST GEOMETRIQUE.
    e = les_profondeurs_a_lire(109)
    v("★★★★ l'échelle avance par DEMI-PLIS et garde le cube entier en dernier",
      e["decidable"] and e["les_profondeurs"] == [36, 72, 108, 109],
      str(e.get("les_profondeurs")))
    v("★★★★ la part attendue est la longueur de la fenêtre divisée par le pli, plafonnée à un",
      e["la_part_attendue_par_profondeur"] == [round(36 / PAS_EN_VOXELS, 4),
                                               round(72 / PAS_EN_VOXELS, 4), 1.0, 1.0],
      str(e["la_part_attendue_par_profondeur"]))
    v("★★★ la plus courte vaut un demi-pli et la référence est le plus long barreau",
      e["la_profondeur_la_plus_courte"] == 36 and e["la_profondeur_de_reference"] == 109)
    v("★★★ les plis par profondeur viennent de la période, jamais d'un compte de couches",
      abs(e["les_plis_par_profondeur"][0] - round(36 / PAS_EN_VOXELS, 4)) < 1e-9)
    v("★★★ un cube qui tombe juste sur un multiple ne double pas son dernier barreau",
      les_profondeurs_a_lire(108)["les_profondeurs"] == [36, 72, 108])
    # ⚠⚠ LA SONDE ATTRAPE L'EXCEPTION ET LA COMPTE COMME UN ECHEC : « ca refuse » et « ca leve »
    # sont deux facons de ne pas rendre d'echelle, mais seule la premiere laisse la batterie aller
    # jusqu'a son verdict. Un bris pose sur ce garde faisait autrement tomber tout le fichier.
    try:
        refuse_court = not les_profondeurs_a_lire(20)["decidable"]
    except Exception as exc:  # noqa: BLE001
        refuse_court, detail_court = False, f"{type(exc).__name__}"
    else:
        detail_court = ""
    v("★★★★ un cube plus court qu'un demi-pli est REFUSÉ, jamais rogné ni levé",
      refuse_court, detail_court)

    v("★★★ une sous-tranche est CENTRÉE, donc toutes lisent le même milieu",
      le_debut_dune_sous_tranche(109, 36) == 36
      and le_debut_dune_sous_tranche(109, 108) == 0
      and le_debut_dune_sous_tranche(109, 109) == 0)

    # ⭐ LE VRAI LECTEUR, SUR LA VRAIE MATIERE DE `179`, ET L'OFFSET EST L'INVARIANT.
    import quelle_fenetre_lit_une_bascule as Q  # noqa: PLC0415
    from combien_dinterstices_traverses import PAS_UM, VOXEL_FIN_UM  # noqa: PLC0415
    from la_coherence_creuse_t_elle_a_la_frontiere import (  # noqa: PLC0415
        CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE)
    bloc = Q.bloc_de_la_fixture(109, 0.0, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE,
                                VOXEL_FIN_UM, PAS_UM, 64, transition_um=45.6)
    tuile = les_sous_colonnes(64, 64, 2)[0]
    # ⚠⚠⚠ L'INVARIANT EST QUE LA MEME FRONTIERE SE LISE A LA MEME COUCHE DU CUBE QUELLE QUE SOIT
    # LA FENETRE, et c'est tout ce sur quoi la tranche repose. Une sonde qui se contenterait de
    # « la couche tombe dans la fenetre OU elle est absente » serait satisfaite par l'ABSENCE : un
    # bris qui retire l'offset est alors reste vert.
    a72 = la_couche_dune_sous_colonne_a_cette_profondeur(bloc, tuile, 72, PERMUTATIONS, 7)
    a108 = la_couche_dune_sous_colonne_a_cette_profondeur(bloc, tuile, 108, PERMUTATIONS, 7)
    v("★★★★ une couche lue dans une sous-tranche est RENDUE AU CUBE, jamais à la fenêtre",
      a72["le_debut_de_la_tranche"] == 18 and a108["le_debut_de_la_tranche"] == 0
      and a72["la_couche"] is not None and a108["la_couche"] is not None
      and int(a72["la_couche"]) == int(a108["la_couche"]),
      f"{a72.get('la_couche')} à 72 contre {a108.get('la_couche')} à 108")
    v("★★★ une sous-tranche plus petite que l'opérateur est REFUSÉE, jamais devinée",
      la_couche_dune_sous_colonne_a_cette_profondeur(
          bloc, {"iy": 0, "ix": 0, "y0": 0, "y1": 2, "x0": 0, "x1": 2}, 36)["la_couche"] is None)
    plat = la_couche_dune_sous_colonne_a_cette_profondeur(
        np.zeros((109, 32, 32), dtype=np.float32),
        {"iy": 0, "ix": 0, "y0": 0, "y1": 32, "x0": 0, "x1": 32}, 36)
    v("★★★ une sous-tranche sans texture tombe sur le filtre DU PRODUCTEUR",
      plat["la_couche"] is None and plat["pourquoi"] == "trop peu texturé")

    # ⭐⭐⭐⭐ LE CONTROLE VIDE DE `179` EST DANS LA FIXTURE : PAS DE FRONTIERE, PAS DE CREUX.
    r = _rng(11)
    sans = une_courbe_a_cette_profondeur(36, [200.0], 36, 0.02, 9.0, r)
    avec = une_courbe_a_cette_profondeur(36, [50.0], 36, 0.02, 9.0, r)
    v("★★★★ une fenêtre sans frontière rend une courbe PLATE, une fenêtre avec creuse vraiment",
      min(x[1] for x in sans) > 0.5 and min(x[1] for x in avec) < 0.3,
      f"{round(min(x[1] for x in sans), 3)} contre {round(min(x[1] for x in avec), 3)}")

    # ⚠⚠⚠ LA PREMISSE DE `R4-P54` EST REFUTEE PAR UN CHIFFRE DEJA PUBLIE.
    fe = la_fenetre_effective([36, 72, 108, 109], 19.0)
    v("★★★★ la fenêtre effective vaut la fenêtre PLUS deux transitions",
      fe["decidable"]
      and abs(fe["les_fenetres"][0]["la_fenetre_effective_en_voxels"] - 74.0) < 1e-9,
      str(fe["les_fenetres"][0]))
    v("★★★★ à ces profondeurs la géométrie ne peut RIEN discriminer, et la fonction le dit",
      fe["la_geometrie_peut_elle_discriminer"] is False,
      str([x["elle_vaut_le_pas_fois"] for x in fe["les_fenetres"]]))
    v("★★★ une transition assez courte rendrait la géométrie discriminante à nouveau",
      la_fenetre_effective([36], 2.0)["la_geometrie_peut_elle_discriminer"] is True)
    v("★★★ une transition absente est dite, jamais remplacée par zéro",
      not la_fenetre_effective([36], None)["decidable"])
    v("★★★★ la transition vient de `179` et de nulle part ailleurs",
      ce_que_179_a_rendu().get("la_transition_en_voxels")
      == (json.loads((MESURES / "la_coherence_creuse_t_elle_a_la_frontiere.json")
                     .read_text(encoding="utf-8"))["le_verdict"]["il_vaut_le_voxel_fois"]))
    v("★★★ `179` absent est dit, jamais remplacé",
      not ce_que_179_a_rendu(Path("/pas/de/fichier.json"))["decidable"])

    # ⚠⚠⚠ L'EPREUVE : NUL PAR PERMUTATION, DONC AUCUNE PERIODE SUPPOSEE.
    accord = {c: {36: 50.0 + 0.3 * c, 109: 50.0 + 0.3 * c + 0.4} for c in range(40)}
    ep = les_deux_profondeurs_saccordent(accord, 36, 109, PAS_EN_VOXELS, PERMUTATIONS, 3)
    v("★★★★ deux profondeurs qui marquent la même frontière sont VUES",
      ep["decidable"] and ep["elles_lisent_la_meme_frontiere"]
      and ep["les_melanges_au_moins_aussi_bas"] == 0,
      str(ep.get("la_valeur_p")))
    sans = _rng(8)
    hasard = {c: {36: float(sans.uniform(0.0, 109.0)), 109: float(sans.uniform(0.0, 109.0))}
              for c in range(40)}
    ep2 = les_deux_profondeurs_saccordent(hasard, 36, 109, PAS_EN_VOXELS, PERMUTATIONS, 3)
    v("★★★★ deux lectures sans rapport ne sont PAS vues",
      not ep2["elles_lisent_la_meme_frontiere"], str(ep2.get("la_valeur_p")))
    v("★★★★ l'écart médian est REPLIÉ : un chunk calé un pli plus loin ne compte pas double",
      abs(les_deux_profondeurs_saccordent(
          {c: {36: 10.0, 109: 10.0 + PAS_EN_VOXELS} for c in range(5)},
          36, 109, PAS_EN_VOXELS, 3, 1)["lecart_median_replie_en_voxels"]) < 1e-9)
    v("★★★ moins de trois chunks lus aux deux profondeurs ne rendent AUCUN verdict",
      not les_deux_profondeurs_saccordent({0: {36: 1.0, 109: 2.0}}, 36, 109)["decidable"])
    v("★★★ un chunk illisible à une profondeur est SAUTÉ, jamais complété",
      les_deux_profondeurs_saccordent(
          {0: {36: 1.0, 109: 2.0}, 1: {36: None, 109: 3.0}, 2: {36: 4.0, 109: 5.0},
           3: {36: 6.0, 109: 7.0}}, 36, 109)["les_chunks_lus_aux_deux"] == 3)

    # ⚠⚠⚠ LA COURBE : LE COMPTE DE CHUNKS LISIBLES VOYAGE AVEC L'ERREUR.
    des = [1.0, -3.0, 2.0, -2.0, 4.0, -1.0]
    # ⚠⚠ LA DISPERSION DE LA FIXTURE EST AU-DESSUS DE LA DERIVE DE `202`, SINON LE MODELE
    # ADDITIF SE REFUTE PAR CONSTRUCTION et la sonde ne mesurerait que son propre refus.
    pss = [30.0, 45.0, 22.0, 50.0, 28.0, 40.0]
    lect = {(36, i): {"decidable": True, "le_pas_en_voxels": pss[i],
                      "le_desaccord_en_voxels": des[i]} for i in range(6)}
    lect.update({(109, i): {"decidable": True, "le_pas_en_voxels": pss[i] * 1.2,
                            "le_desaccord_en_voxels": des[i]} for i in range(6)})
    lis = {c: {36: bool(c % 2 == 0), 109: True} for c in range(10)}
    cb = la_courbe_par_profondeur(lect, lis, [36, 109], list(range(6)), 3.4585, [0.4994, 1.0])
    v("★★★★ le compte de chunks lisibles est publié À CÔTÉ de l'erreur — le piège de `200`",
      cb["decidable"] and cb["les_barreaux"][0]["les_chunks_lisibles"] == 5
      and cb["les_barreaux"][1]["les_chunks_lisibles"] == 10,
      str([x["les_chunks_lisibles"] for x in cb["les_barreaux"]]))
    v("★★★★ l'aléa vaut le DEMI écart-type du désaccord, exactement",
      abs(cb["les_barreaux"][0]["lalea_en_voxels"]
          - round(float(np.std(des)) / 2.0, 4)) < 1e-9)
    # ⚠⚠ LA SONDE LIT PAR `.get()` ET TESTE LA PRESENCE AVANT LA VALEUR : un bris qui retire la
    # clef doit rendre cette sonde ROUGE, jamais tuer la batterie avant son verdict.
    commune_lue = cb["les_barreaux"][0].get("lerreur_commune_en_voxels")
    v("★★★★ l'erreur commune retire la dérive de `202`, jamais rien d'autre",
      commune_lue is not None
      and abs(float(commune_lue)
              - round((float(np.std(pss)) ** 2 - (float(np.std(des)) / 2.0) ** 2
                       - 3.4585 ** 2) ** 0.5, 4)) < 1e-9,
      str(commune_lue))
    # ⚠⚠⚠ DEUX REFUS DIFFERENTS, ET LE SECOND EST CELUI QU'UN BRIS A TRAVERSE : une dispersion
    # SOUS l'alea ne rend deja rien, donc elle n'atteint jamais la soustraction de la derive. Il
    # faut une dispersion AU-DESSUS de l'alea mais SOUS la derive pour exercer cette branche-la.
    v("★★★ une dispersion sous l'aléa ne rend aucune erreur",
      la_courbe_par_profondeur(
          {(36, i): {"decidable": True, "le_pas_en_voxels": 3.0 + 0.01 * i,
                     "le_desaccord_en_voxels": des[i]} for i in range(6)},
          lis, [36], list(range(6)), 3.4585, [0.4994]
      )["les_barreaux"][0]["lerreur_commune_en_voxels"] is None)
    calmes = [0.2, -0.2, 0.1, -0.1, 0.3, -0.3]
    petits = [30.0, 33.0, 27.0, 34.0, 29.0, 32.0]
    v("★★★★ une dispersion SOUS la dérive de `202` réfute le modèle par ses propres nombres",
      la_courbe_par_profondeur(
          {(36, i): {"decidable": True, "le_pas_en_voxels": petits[i] / 10.0,
                     "le_desaccord_en_voxels": calmes[i]} for i in range(6)},
          lis, [36], list(range(6)), 3.4585, [0.4994]
      )["les_barreaux"][0]["lerreur_commune_en_voxels"] is None,
      f"dispersion {round(float(np.std([x / 10.0 for x in petits])), 4)} contre 3,4585")
    v("★★★ le rapport des deux erreurs va de la plus COURTE à la plus LONGUE",
      cb.get("le_rapport_des_deux_erreurs") is not None
      and abs(float(cb["le_rapport_des_deux_erreurs"])
          - round(float(cb["lerreur_a_la_plus_courte_en_voxels"])
                  / float(cb["lerreur_a_la_plus_longue_en_voxels"]), 4)) < 1e-9)

    jug = juger(cb, ep, e, fe, {"le_bruit_de_chunk_en_voxels": 14.9372},
                {"la_derive_en_voxels": 3.4585})
    v("★★★★ le verdict porte l'épreuve EN PREMIER : c'est une garde, pas un résultat de plus",
      jug["decidable"] and jug["elles_lisent_la_meme_frontiere"] is True
      and jug["lerreur_que_205_a_isolee_en_voxels"] == 14.9372)
    v("★★★★ il porte aussi la transition de `179`, qui dit pourquoi la géométrie ne tranche pas",
      jug["la_transition_de_179_en_voxels"] == 19.0
      and jug["la_geometrie_peut_elle_discriminer"] is False)
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger(cb, {"decidable": False}, e, fe, {}, {})["decidable"])

    v("★★★ `205` absent est dit, jamais remplacé",
      not ce_que_le_plan_a_rendu(Path("/pas/de/fichier.json"))["decidable"])
    v("★★★★ l'erreur que cette tranche explique vient de `205` et de nulle part ailleurs",
      ce_que_le_plan_a_rendu().get("le_bruit_de_chunk_en_voxels")
      == (json.loads(CE_QUE_LE_PLAN_A_RENDU.read_text(encoding="utf-8"))
          ["le_verdict"]["le_bruit_de_chunk_en_voxels"]))

    meta = {"chunks": [40, 12, 12], "shape": [40, 24, 40]}
    v("★★★ un volume qui ne répond pas est refusé, jamais deviné",
      not la_ligne({"cle": "x", "segment": "s"}, [36], 2, 0.0, None, PERMUTATIONS, GRAINE,
                   lambda cy, cx: (None, "absent du dépôt"), meta)["decidable"])
    lg = la_ligne({"cle": "x", "segment": "s"}, [36, 40], 2, 0.0, None, PERMUTATIONS, GRAINE,
                  lambda cy, cx: (bloc[:40, :12, :12], None), meta)
    v("★★★★ la ligne lit TOUTES les profondeurs du MÊME téléchargement",
      lg["decidable"] and lg["colonnes_lues"] == 4
      and all(set(x) == {36, 40} for x in lg["lues"].values())
      and all(set(x) == {36, 40} for x in lg["lisibles"].values()),
      f"{lg.get('colonnes_lues')} colonnes")
    v("★★ la profondeur du cube est relue de la méta, jamais supposée",
      lg["les_couches_du_cube"] == 40)

    et = sur_letalon([36, 109], e, GRAINE, chunks=30, couches=109, replicats=3, permutations=7)
    v("★★★★ l'étalon voit deux profondeurs qui lisent la même frontière",
      et["la_part_trouvee"] >= 0.99, str(et.get("la_part_trouvee")))
    v("★★★★ la face négative a DEUX fois le compte que la garantie exige — la leçon de `202`",
      et["les_replicats_du_refus"] == int(2.0 / GARANTIE_PAR_EPREUVE))
    v("★★★★ sur une matière honnête, le taux de faux tient la garantie",
      et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('les_faux')} faux sur {et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare ses deux faces, et il le DIT", et["letalon_separe"] is True)
    v("★★★★ les deux comptes de tirages sont SÉPARÉS : celui du lecteur et celui du nul",
      et["les_tirages_de_lepreuve"] == PERMUTATIONS,
      str(et.get("les_tirages_de_lepreuve")))
    v("★★★★ un étalon dont l'épreuve ne peut pas atteindre la garantie se REFUSE",
      not sur_letalon([36, 109], e, GRAINE, chunks=4, couches=109, replicats=1,
                      permutations=7, tirages_de_lepreuve=3)["decidable"])
    v("★★★★ l'écart médian est publié sur les DEUX faces, et la positive est la plus SERRÉE",
      et["lecart_median_sur_la_face_positive_en_voxels"] is not None
      and et["lecart_median_sur_la_face_negative_en_voxels"] is not None
      and et["lecart_median_sur_la_face_positive_en_voxels"]
      < et["lecart_median_sur_la_face_negative_en_voxels"],
      f"{et.get('lecart_median_sur_la_face_positive_en_voxels')} contre "
      f"{et.get('lecart_median_sur_la_face_negative_en_voxels')}")

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
