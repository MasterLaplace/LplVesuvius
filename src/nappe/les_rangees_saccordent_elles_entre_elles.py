"""Les rangées traversées INDÉPENDAMMENT s'accordent-elles entre elles ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `210` QUI LE FORCE. `210` a fait traverser UNE rangée : le pas
moyenné sur les rangées **198**, **197** et **199** franchit ses coutures sans quitter le feuillet,
et à l'échelle de la rangée entière il annonce moins que le demi-feuillet là où une rangée seule
annonce davantage. C'est tout ce qu'il a fait. Le recto en porte **396**, et trois cent quatre-vingt
seize rangées traversées indépendamment ne font pas une surface : rien dans la chaîne n'a mesuré ce
qui se passe ENTRE elles.

⚠⚠⚠ LA PRÉDICTION EST POSÉE AVANT LA MESURE, ET ELLE EST ALARMANTE — C'EST CE QUI REND LA TRANCHE
FALSIFIABLE. `208` a séparé le pas en une part que deux rangées voisines PARTAGENT et une part
PROPRE à chacune. Dans la DIFFÉRENCE de deux cumuls, la part partagée s'annule terme à terme : il
ne reste que les deux bruits propres. Le désaccord est donc une marche au hasard dont le pas vaut la
racine de la somme des carrés des deux bruits propres, et il croît en racine du nombre de coutures.
À l'échelle d'une rangée entière, ce nombre dépasse le demi-feuillet — donc deux rangées voisines
traversées chacune pour elle-même finiraient sur deux feuillets DIFFÉRENTS.

⚠⚠⚠ ET LE RECOUPEMENT ANNONCÉ N'EN EST PAS UN, IL FAUT LE DIRE PLUTÔT QUE L'ENCAISSER. `208`
publie l'écart-type du désaccord des PAS, et la porte proposait de le comparer à la racine de deux
fois le bruit propre. Les deux nombres ne sont pas indépendants : `208` a DÉRIVÉ ses bruits propres
de cet écart-type même, donc la racine de la somme de leurs carrés le redonne par construction.
Ce qui reste, et qui vaut, est un vrai recoupement de MATIÈRE : le désaccord des pas relu ici sur une
seconde course du dépôt doit retomber sur le nombre que `208` a publié. Ce qui est NEUF est le
désaccord des CUMULS, que personne n'a mesuré, et sa croissance.

⚠⚠ LE PIÈGE EST CELUI DE `210`, UN CRAN PLUS HAUT, ET IL A DEUX FACES. Les rangées n'ont pas les
mêmes trous, donc leurs tronçons ne commencent ni ne finissent aux mêmes colonnes. Le désaccord ne
se lit que là où les DEUX cumuls existent, et il faut les RECALER sur une origine commune avant de
les soustraire. ⚠ Mais la faute ne se voit pas partout : l'EXCURSION d'une différence est insensible
à un décalage constant, alors que la SÉPARATION — jusqu'où les deux marches s'éloignent l'une de
l'autre — ne l'est pas. Or c'est la séparation qui décide si deux rangées finissent sur le même
feuillet. La règle réfutée est donc portée comme CONTRÔLE NOMMÉ, et son écart est mesuré.

Usage :
    uv run python src/nappe/les_rangees_saccordent_elles_entre_elles.py --verifier
    uv run python src/nappe/les_rangees_saccordent_elles_entre_elles.py \\
        --json docs/mesures/les_rangees_saccordent_elles_entre_elles.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import la_ligne  # noqa: E402
from la_derive_saccumule_t_elle import (contre_les_signes,  # noqa: E402
                                        les_troncons)
from la_moyenne_des_rangees_traverse_t_elle import (  # noqa: E402
    des_rangees_fabriquees, les_replicats_du_refus)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_cumul_recale_traverse_t_il_la_rangee import (le_cumul,  # noqa: E402
                                                     lexcursion,
                                                     lexcursion_predite)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)
from une_rangee_voisine_lit_elle_le_meme_pas import (les_coutures_communes,  # noqa: E402
                                                     les_pas_dune_rangee,
                                                     les_rangees_du_treillis)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_VOISINE_A_RENDU = MESURES / "une_rangee_voisine_lit_elle_le_meme_pas.json"
CE_QUE_LA_MOYENNE_A_RENDU = MESURES / "la_moyenne_des_rangees_traverse_t_elle.json"
GRAINE = 20261019
LES_RANGEES = 16

LA_QUESTION_DECLAREE = ("deux rangées voisines traversées chacune pour elle-même restent-elles sur "
                        "le même feuillet, ou leur désaccord dépasse-t-il le demi-feuillet ?")
LES_EPREUVES_DECLAREES = ("le désaccord des deux cumuls s'accumule-t-il, ou se compense-t-il",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def ce_que_la_voisine_a_rendu(chemin: Path = CE_QUE_LA_VOISINE_A_RENDU) -> dict:
    """La décomposition de `208` ET son désaccord des PAS — relus, jamais refaits.

    ⚠⚠⚠ LES DEUX BRUITS PROPRES SONT LUS SEPAREMENT, ET PAS UN SEUL PRIS DEUX FOIS. La porte posait
    la prediction comme « racine de deux fois le bruit propre », ce qui suppose que les deux rangees
    en portent autant l'une que l'autre — `208` mesure qu'elles n'en portent pas tout a fait autant.
    La prediction honnete est la racine de la SOMME DES CARRES des deux, et l'ecart entre les deux
    ecritures est publie plutot que gomme.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `208` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("le_bruit_de_la_mediane_en_voxels") is None:
        return {"decidable": False, "raison": "`208` ne publie pas de bruit propre"}
    return {"decidable": True,
            "la_rangee_mediane": v.get("la_rangee_mediane"),
            "la_voisine_de_lepreuve": v.get("la_voisine_de_lepreuve"),
            "la_derive_partagee_en_voxels": v.get("la_derive_partagee_en_voxels"),
            "le_bruit_de_la_mediane_en_voxels": v.get("le_bruit_de_la_mediane_en_voxels"),
            "le_bruit_de_la_voisine_en_voxels": v.get("le_bruit_de_la_voisine_en_voxels"),
            "le_desaccord_des_pas_en_voxels": v.get("lecart_type_observe_en_voxels"),
            "les_coutures_communes_a_deux": v.get("les_coutures_communes")}


def ce_que_la_moyenne_a_rendu(chemin: Path = CE_QUE_LA_MOYENNE_A_RENDU) -> dict:
    """Ce que `210` a mesuré sur la moyenne des trois rangées — la marche à laquelle on compare.

    ⚠⚠ C'EST LA MOITIE MANQUANTE DE LA COMPARAISON : `210` a mesure jusqu'ou UNE surface faite de
    trois rangees s'eloigne de son depart, cette tranche mesure de combien DEUX rangees s'eloignent
    l'une de l'autre. Les deux se lisent en voxels et se comparent au meme demi-feuillet, donc les
    publier cote a cote est la seule facon de dire laquelle des deux pannes arrive la premiere.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `210` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("lexcursion_moyennee_en_voxels") is None:
        return {"decidable": False, "raison": "`210` ne publie pas d'excursion moyennée"}
    a_toutes = d.get("les_predictions_a_toutes_les_coutures") or {}
    return {"decidable": True,
            "lexcursion_moyennee_en_voxels": v.get("lexcursion_moyennee_en_voxels"),
            "les_coutures_du_troncon": v.get("les_coutures_du_troncon"),
            "les_coutures_communes_en_tout": v.get("les_coutures_communes_en_tout"),
            "la_dispersion_du_pas_moyenne_en_voxels": v.get(
                "la_dispersion_du_pas_moyenne_en_voxels"),
            "ce_que_la_moyenne_annonce_a_la_rangee_en_voxels": (
                (a_toutes.get("la_moyenne_mesuree") or {}).get("lecart_attendu_en_voxels"))}


def le_desaccord_predit(propre_une, propre_autre) -> dict:
    """Ce que le désaccord de deux cumuls DOIT valoir par couture — posé avant la mesure.

    ⭐⭐⭐⭐ LA PART PARTAGEE S'ANNULE, ET C'EST TOUT LE RAISONNEMENT. Si le pas d'une rangee est une
    derive que les deux voient plus un bruit qui n'appartient qu'a elle, alors la difference des
    deux pas ne contient PLUS la derive : elle ne contient que les deux bruits propres. Moyenner
    aide a traverser et n'aide en RIEN a s'accorder — ce sont deux quantites differentes, et c'est
    pour cela qu'une tranche ne peut pas repondre aux deux.

    ⚠⚠ ET LA RACINE DE DEUX N'EST QU'UNE APPROXIMATION, celle qu'on ecrit quand on suppose les deux
    bruits egaux. Les deux ecritures sont rendues et leur ecart est publie : un nombre juste sous
    un mauvais nom est pire qu'un nombre absent, et « racine de deux fois le bruit » en serait un.
    """
    if propre_une is None or propre_autre is None:
        return {"decidable": False, "raison": "un des deux bruits propres manque"}
    a, b = float(propre_une), float(propre_autre)
    exact = float(np.sqrt(a * a + b * b))
    approche = float(np.sqrt(2.0) * a)
    return {"decidable": True,
            "le_bruit_propre_de_lune_en_voxels": round(a, 4),
            "le_bruit_propre_de_lautre_en_voxels": round(b, 4),
            "le_desaccord_par_couture_en_voxels": round(exact, 4),
            "ce_que_racine_de_deux_donnerait_en_voxels": round(approche, 4),
            "lecart_entre_les_deux_ecritures_en_voxels": round(abs(exact - approche), 4)}


def les_marches_separees(pas_par_rangee: dict, colonnes) -> dict:
    """Chaque rangée traversée POUR ELLE-MÊME, sur SON PROPRE tronçon.

    ⭐⭐⭐⭐ C'EST LA CONSTRUCTION QUE LA PORTE EXIGEAIT, ET ELLE DIT DEJA QUELQUE CHOSE AVANT TOUTE
    SOUSTRACTION : les trois rangees n'ont pas les memes trous, donc leurs plus longs troncons ne
    couvrent pas la meme portion du rouleau. Trois marches qui ne franchissent pas les memes
    colonnes ne sont pas trois lectures d'un meme objet, et c'est pourquoi leur desaccord se lit
    ailleurs que sur leurs troncons propres.

    ⚠ Le troncon est celui de `199`, importe : un trou coupe la marche, il ne se recolle pas.
    """
    out = {}
    for r, pas in pas_par_rangee.items():
        troncons = les_troncons(set(int(c) for c in pas), list(colonnes))
        if not troncons:
            out[str(int(r))] = {"decidable": False,
                                "raison": "aucune suite de deux colonnes contiguës"}
            continue
        lp = max(troncons, key=len)
        vals = [float(pas[int(c)]) for c in lp]
        cum = le_cumul(vals)
        out[str(int(r))] = {
            "decidable": True, "la_rangee": int(r),
            "les_troncons": len(troncons),
            "le_plus_long_troncon": [int(lp[0]), int(lp[-1]), len(lp)],
            "les_coutures": len(lp),
            "les_colonnes": [int(c) for c in lp],
            "le_cumul_en_voxels": [round(float(x), 4) for x in cum],
            "lexcursion": lexcursion(cum)}
    return out


def le_desaccord_des_cumuls(pas_une: dict, pas_autre: dict, colonnes,
                            nom_une: int, nom_autre: int) -> dict:
    """Les deux marches RECALÉES sur une origine commune, et leur écart colonne par colonne.

    ⭐⭐⭐⭐ LE RECALAGE EST DANS LA CONSTRUCTION, PAS DANS UNE CORRECTION APRES COUP. Le desaccord
    est le CUMUL DES DIFFERENCES DE PAS sur le tronçon commun, donc il part de zero a la premiere
    couture commune par definition meme. Soustraire deux cumuls bâtis chacun sur son propre tronçon
    aurait mesure un decalage d'origine — c'est-a-dire la distance parcourue par chacun AVANT de se
    rencontrer — et non une divergence.

    ⚠⚠⚠ ET LE TRONCON EST CELUI DES COUTURES COMMUNES AUX DEUX, jamais l'union ni le tronçon d'une
    seule : une colonne que l'une des deux n'a pas lue n'a pas de difference, donc accumuler
    par-dessus inventerait un ecart que personne n'a mesure.
    """
    communes = les_coutures_communes(pas_une, pas_autre)
    if len(communes) < 2:
        return {"decidable": False, "raison": "moins de deux coutures communes aux deux rangées"}
    troncons = les_troncons(set(int(c) for c in communes), list(colonnes))
    if not troncons:
        return {"decidable": False, "raison": "aucune suite de deux coutures communes contiguës"}
    lp = max(troncons, key=len)
    ecarts = [float(pas_une[int(c)]) - float(pas_autre[int(c)]) for c in lp]
    tous = [float(pas_une[int(c)]) - float(pas_autre[int(c)]) for c in communes]
    d = le_cumul(ecarts)
    return {"decidable": True,
            "la_paire": [int(nom_une), int(nom_autre)],
            "les_coutures_communes": len(communes),
            "les_troncons_communs": len(troncons),
            "le_plus_long_troncon": [int(lp[0]), int(lp[-1]), len(lp)],
            "les_coutures_du_troncon": len(lp),
            "les_colonnes_du_troncon": [int(c) for c in lp],
            "les_ecarts_de_pas_du_troncon_en_voxels": [round(float(x), 4) for x in ecarts],
            "le_desaccord_cumule_en_voxels": [round(float(x), 4) for x in d],
            "lecart_type_des_pas_sur_toutes_les_communes_en_voxels": round(
                float(np.std(tous)), 4),
            "lecart_type_des_pas_du_troncon_en_voxels": round(float(np.std(ecarts)), 4),
            "lexcursion_du_desaccord": lexcursion(d),
            "le_desaccord_final_en_voxels": round(float(abs(d[-1])), 4),
            "le_desaccord_le_plus_grand_en_voxels": round(float(np.abs(d).max()), 4)}


def le_decalage_si_on_ne_recale_pas(marche_une: dict, marche_autre: dict) -> dict:
    """La règle RÉFUTÉE, portée comme contrôle nommé — et l'écart qu'elle coûte, mesuré.

    ⚠⚠⚠ LA FAUTE NE SE VOIT PAS PARTOUT, ET C'EST CE QUI LA REND DANGEREUSE. Soustraire deux cumuls
    bâtis chacun sur son propre tronçon ajoute une CONSTANTE : la distance que chacun a parcourue
    avant la premiere colonne partagee. Une constante ne change pas l'EXCURSION d'une difference —
    donc une tranche qui n'aurait publie que l'excursion aurait rendu le bon nombre par accident, et
    n'aurait rien appris. Elle change en revanche la SEPARATION, c'est-a-dire jusqu'ou les deux
    marches s'eloignent l'une de l'autre, et c'est la separation qui decide du feuillet.

    ⚠ La comparaison se fait sur les colonnes que les DEUX tronçons propres portent, et sur rien
    d'autre : ailleurs, l'une des deux marches n'existe pas.
    """
    if not marche_une.get("decidable") or not marche_autre.get("decidable"):
        return {"decidable": False, "raison": "une des deux marches propres est indécidable"}
    ca = [int(c) for c in marche_une["les_colonnes"]]
    cb = [int(c) for c in marche_autre["les_colonnes"]]
    ua = [float(x) for x in marche_une["le_cumul_en_voxels"]]
    ub = [float(x) for x in marche_autre["le_cumul_en_voxels"]]
    partagees = sorted(set(ca) & set(cb))
    if not partagees:
        return {"decidable": False,
                "raison": "les deux tronçons propres ne partagent aucune colonne"}
    brut = [ua[ca.index(c)] - ub[cb.index(c)] for c in partagees]
    decalage = float(brut[0])
    recale = [x - decalage for x in brut]
    etendue_brute = float(max(brut) - min(brut))
    etendue_recalee = float(max(recale) - min(recale))
    return {"decidable": True,
            "les_colonnes_partagees_par_les_deux_troncons": len(partagees),
            "la_premiere_colonne_partagee": int(partagees[0]),
            "le_decalage_dorigine_en_voxels": round(abs(decalage), 4),
            "la_separation_sans_recalage_en_voxels": round(
                float(max(abs(x) for x in brut)), 4),
            "la_separation_avec_recalage_en_voxels": round(
                float(max(abs(x) for x in recale)), 4),
            "lexcursion_sans_recalage_en_voxels": round(etendue_brute, 4),
            "lexcursion_avec_recalage_en_voxels": round(etendue_recalee, 4),
            "lexcursion_est_insensible_au_decalage": bool(
                abs(etendue_brute - etendue_recalee) < 1e-9),
            "la_separation_y_est_sensible": bool(
                abs(float(max(abs(x) for x in brut))
                    - float(max(abs(x) for x in recale))) > 1e-9)}


def ce_que_le_desaccord_vaut(desaccord: dict, predit: dict, par_208: dict,
                             demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Le désaccord mesuré contre sa prédiction, et ce qu'il annonce à l'échelle de la rangée.

    ⭐⭐⭐⭐ LA CROISSANCE EN RACINE DU NOMBRE DE COUTURES EST LA SEULE CHOSE NEUVE ICI, et elle se
    mesure sans aucune liberte : `contre_les_signes` rend deja la marche au hasard de ces memes
    pas — la racine de la somme de leurs carres — donc le rapport du deplacement observe a cette
    marche est le test du modele, et aucune longueur n'a ete choisie pour l'obtenir.

    ⚠⚠ L'ERREUR D'ECHANTILLONNAGE EST DERIVEE ET NON CHOISIE : l'ecart-type d'un ecart-type estime
    sur `n` tirages vaut lui-meme divise par la racine de deux fois `n`. Sans elle, un ecart de deux
    pour cent au nombre de `208` se lirait comme un desaccord de mesure alors qu'il vaut une demi
    erreur.
    """
    if not desaccord.get("decidable"):
        return {"decidable": False, "raison": "le désaccord est indécidable"}
    n_tout = int(desaccord["les_coutures_communes"])
    sigma = float(desaccord["lecart_type_des_pas_sur_toutes_les_communes_en_voxels"])
    erreur = sigma / float(np.sqrt(2.0 * n_tout)) if n_tout > 0 else None
    par_208_val = (par_208 or {}).get("le_desaccord_des_pas_en_voxels")
    ecart_208 = (((sigma - float(par_208_val)) / erreur)
                 if (par_208_val and erreur and erreur > 0.0) else None)
    attendu = (predit or {}).get("le_desaccord_par_couture_en_voxels")
    ecart_predit = (((sigma - float(attendu)) / erreur)
                    if (attendu and erreur and erreur > 0.0) else None)
    exc = desaccord.get("lexcursion_du_desaccord") or {}
    n_tr = int(desaccord["les_coutures_du_troncon"])
    return {"decidable": True,
            "la_paire": desaccord.get("la_paire"),
            "les_coutures_communes": n_tout,
            "les_coutures_du_troncon": n_tr,
            "le_desaccord_par_couture_mesure_en_voxels": round(sigma, 4),
            "lerreur_dechantillonnage_en_voxels": (None if erreur is None
                                                   else round(float(erreur), 4)),
            "ce_que_208_a_mesure_en_voxels": par_208_val,
            "lecart_a_208_en_erreurs": (None if ecart_208 is None
                                        else round(float(ecart_208), 4)),
            "il_recoupe_208": (None if ecart_208 is None
                               else bool(abs(float(ecart_208)) <= 3.0)),
            "le_desaccord_par_couture_predit_en_voxels": attendu,
            "lecart_a_la_prediction_en_erreurs": (None if ecart_predit is None
                                                  else round(float(ecart_predit), 4)),
            "il_saccorde_a_la_prediction": (None if ecart_predit is None
                                            else bool(abs(float(ecart_predit)) <= 3.0)),
            "lexcursion_du_desaccord_sur_le_troncon_en_voxels": exc.get("lexcursion_en_voxels"),
            "la_separation_la_plus_grande_sur_le_troncon_en_voxels": desaccord.get(
                "le_desaccord_le_plus_grand_en_voxels"),
            "le_desaccord_final_sur_le_troncon_en_voxels": desaccord.get(
                "le_desaccord_final_en_voxels"),
            "ce_quune_marche_au_hasard_donnerait_sur_le_troncon": lexcursion_predite(
                sigma, n_tr),
            "ce_quelle_annonce_a_toutes_les_communes": lexcursion_predite(sigma, n_tout),
            "le_demi_pli_en_voxels": int(demi),
            "le_troncon_reste_sous_le_demi_pli": bool(
                float(desaccord["le_desaccord_le_plus_grand_en_voxels"]) < float(demi)),
            "la_rangee_entiere_reste_sous_le_demi_pli": bool(
                float(lexcursion_predite(sigma, n_tout)["lecart_attendu_en_voxels"])
                < float(demi))}


def sur_letalon(coutures: int = 240, derive: float = 1.5129, propre: float = 1.9387,
                biais: float | None = None, graine: int = GRAINE, replicats: int = 12,
                tirages: int = PERMUTATIONS, lecteur=None,
                aveugle_propre: float = 0.0) -> dict:
    """L'épreuve voit-elle un biais PROPRE à une rangée, et se tait-elle sinon ?

    ⭐⭐⭐⭐ LE BIAIS EST DANS LA PART PROPRE, ET C'EST L'EXACT INVERSE DE `210`. Là-bas, un biais que
    seule une rangee aurait porte se serait divise par trois en moyennant, donc la fixture devait le
    mettre dans la part PARTAGEE. Ici, un biais partage s'annule dans la difference et l'epreuve ne
    peut pas le voir : c'est dans la part propre qu'il doit vivre. Les deux tranches emploient la
    meme fixture avec le biais a deux endroits differents, et chacune ne voit que le sien — ce qui
    est un controle structurel gratuit et non une commodite.

    ⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE. Le compte du refus est
    celui que `210` a DERIVE de la garantie : le plancher de `202` fait EXISTER la face negative
    sans la faire DECIDER, parce qu'une epreuve au niveau exact y depasse l'acceptation dans une
    fraction non negligeable des courses.

    ⚠⚠ LE BIAIS N'EST PAS CHOISI ICI : c'est celui que l'etalon de `199` a pose, relu chez son
    producteur. En choisir un autre ferait dire a « l'etalon separe » deux choses selon la tranche.
    """
    if biais is None:
        from peut_on_deplier_la_phase import \
            ce_que_la_marche_a_rendu  # noqa: PLC0415
        lu = (lecteur or ce_que_la_marche_a_rendu)()
        biais = (lu or {}).get("le_biais_de_letalon_en_voxels")
    if biais is None:
        return {"decidable": False, "raison": "`199` ne publie pas le biais de son étalon"}

    def _une_course(g: int, propre_pose: float, partage: float):
        rangees = des_rangees_fabriquees(coutures, 2, derive, propre, partage, g,
                                         biais_propre=propre_pose)
        communes = les_coutures_communes(rangees[0], rangees[1])
        ecarts = [rangees[0][c] - rangees[1][c] for c in communes]
        return contre_les_signes(ecarts, tirages, g + 7), ecarts

    vus, nets, dispersions = 0, [], []
    for i in range(int(replicats)):
        ep, ec = _une_course(int(graine) + 1000 * i, float(biais), 0.0)
        vus += int(bool(ep.get("ca_saccumule")))
        if ep.get("decidable"):
            nets.append(float(ep["le_deplacement_net_en_voxels"]))
        dispersions.append(float(np.std(ec)))
    combien = les_replicats_du_refus(GARANTIE_PAR_EPREUVE)
    refus = int(combien["le_compte_decisif"])
    faux, sans = 0, []
    for i in range(refus):
        ep, _ = _une_course(int(graine) + 500000 + 1000 * i, 0.0, 0.0)
        faux += int(bool(ep.get("ca_saccumule")))
        if ep.get("decidable"):
            sans.append(float(ep["le_deplacement_net_en_voxels"]))
    # ⭐⭐⭐⭐ LE CONTROLE STRUCTUREL : un biais PARTAGE par les deux rangees doit rester INVISIBLE.
    # Sans lui, un etalon qui separe ne dirait pas de quoi il separe — une epreuve qui reagirait
    # a n'importe quel biais aurait exactement la meme face positive.
    # ⚠⚠⚠ `aveugle_propre` EST NUL PAR DEFAUT, ET IL EXISTE POUR QUE LE CONTROLE PUISSE TIRER.
    # Un controle qui ne peut jamais se declencher ne prouve rien — c'est le piege numero un de
    # cette chaine sous un autre costume. Le passer non nul deplace le biais du controle dans la
    # part PROPRE, donc le controle DOIT le voir, et le verdict DOIT cesser de separer.
    # ⚠⚠⚠ ET IL SE JUGE AU MEME TAUX QUE L'AUTRE FACE NEGATIVE, JAMAIS SUR UN ZERO. Une premiere
    # version exigeait qu'AUCUN de douze replicats ne tire — or chacun porte la garantie de
    # l'epreuve, donc en attendre zero c'est attendre du nul ce qu'il ne peut pas donner. La vraie
    # mesure a rendu un tirage sur douze et a REFUSE son propre etalon, sur du code juste. C'est
    # le piege de `178` repaye ici. Ce qui se mesure est qu'un biais PARTAGE ne fait rien de plus
    # qu'une absence de biais : le meme taux, sur le meme compte derive.
    aveugles = 0
    for i in range(refus):
        ep, _ = _une_course(int(graine) + 900000 + 1000 * i, float(aveugle_propre), float(biais))
        aveugles += int(bool(ep.get("ca_saccumule")))
    taux = float(faux) / float(refus)
    taux_aveugle = float(aveugles) / float(refus)
    aveugle_tient = bool(taux_aveugle <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)
    return {"decidable": True,
            "les_coutures_par_replicat": int(coutures),
            "la_derive_partagee_posee_en_voxels": float(derive),
            "le_bruit_propre_pose_en_voxels": float(propre),
            "le_biais_propre_pose_en_voxels": float(biais),
            "replicats": int(replicats), "les_vus": int(vus),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "la_dispersion_mediane_du_desaccord_en_voxels": (
                round(float(np.median(dispersions)), 4) if dispersions else None),
            "le_net_median_sur_la_face_positive_en_voxels": (
                round(float(np.median(nets)), 4) if nets else None),
            "les_replicats_du_refus": int(refus), "les_faux": int(faux),
            "le_plancher_de_202": combien["le_plancher_de_202"],
            "la_chance_de_rater_au_plancher": combien["la_chance_de_rater_au_plancher"],
            "le_taux_de_faux": round(taux, 4),
            "le_net_median_sur_la_face_negative_en_voxels": (
                round(float(np.median(sans)), 4) if sans else None),
            "les_replicats_du_controle_aveugle": int(refus),
            "les_biais_partages_vus": int(aveugles),
            "le_taux_du_controle_aveugle": round(taux_aveugle, 4),
            "un_biais_partage_reste_invisible": aveugle_tient,
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= int(replicats)
                                   and taux <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12
                                   and aveugle_tient)}


def juger(valeurs: dict, desaccord: dict, decalage: dict, epreuve: dict,
          par_210: dict, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Deux rangées voisines finissent-elles sur le même feuillet ?

    ⚠⚠ LA LONGUEUR EST PUBLIEE AVANT LA SEPARATION, exactement comme chez `207` et `210` : un
    desaccord lu sur un tronçon plus court n'est pas un meilleur accord, et un verdict qui donnerait
    la separation seule laisserait croire le contraire.

    ⚠ Tout se lit par `.get()` et la presence est testee avant la valeur : une batterie qui meurt
    avant son verdict ne dit rien.
    """
    if not valeurs.get("decidable") or not epreuve.get("decidable"):
        return {"decidable": False, "raison": "le désaccord ou l'épreuve manque"}
    a_la_rangee = valeurs.get("ce_quelle_annonce_a_toutes_les_communes") or {}
    au_hasard = valeurs.get("ce_quune_marche_au_hasard_donnerait_sur_le_troncon") or {}
    sep = valeurs.get("la_separation_la_plus_grande_sur_le_troncon_en_voxels")
    annonce = a_la_rangee.get("lecart_attendu_en_voxels")
    moy = (par_210 or {}).get("ce_que_la_moyenne_annonce_a_la_rangee_en_voxels")
    return {"decidable": True,
            "la_paire": valeurs.get("la_paire"),
            "les_coutures_du_troncon": valeurs.get("les_coutures_du_troncon"),
            "les_coutures_communes": valeurs.get("les_coutures_communes"),
            "le_desaccord_par_couture_en_voxels": valeurs.get(
                "le_desaccord_par_couture_mesure_en_voxels"),
            "lerreur_dechantillonnage_en_voxels": valeurs.get(
                "lerreur_dechantillonnage_en_voxels"),
            "ce_que_208_a_mesure_en_voxels": valeurs.get("ce_que_208_a_mesure_en_voxels"),
            "lecart_a_208_en_erreurs": valeurs.get("lecart_a_208_en_erreurs"),
            "il_recoupe_208": valeurs.get("il_recoupe_208"),
            "le_desaccord_par_couture_predit_en_voxels": valeurs.get(
                "le_desaccord_par_couture_predit_en_voxels"),
            "lecart_a_la_prediction_en_erreurs": valeurs.get("lecart_a_la_prediction_en_erreurs"),
            "il_saccorde_a_la_prediction": valeurs.get("il_saccorde_a_la_prediction"),
            "la_separation_la_plus_grande_en_voxels": sep,
            "la_separation_en_demi_plis": (round(float(sep) / float(demi), 4)
                                           if sep is not None else None),
            "le_desaccord_final_en_voxels": valeurs.get(
                "le_desaccord_final_sur_le_troncon_en_voxels"),
            "lexcursion_du_desaccord_en_voxels": valeurs.get(
                "lexcursion_du_desaccord_sur_le_troncon_en_voxels"),
            "ce_quune_marche_au_hasard_donnerait_en_voxels": au_hasard.get(
                "lecart_attendu_en_voxels"),
            "le_rapport_a_la_marche_au_hasard": (
                round(float(valeurs["lexcursion_du_desaccord_sur_le_troncon_en_voxels"])
                      / float(au_hasard["lecart_attendu_en_voxels"]), 4)
                if au_hasard.get("lecart_attendu_en_voxels") else None),
            "le_troncon_reste_sous_le_demi_pli": valeurs.get("le_troncon_reste_sous_le_demi_pli"),
            "ce_que_le_desaccord_annonce_a_la_rangee_en_voxels": annonce,
            "ce_que_la_moyenne_de_210_annonce_a_la_rangee_en_voxels": moy,
            "le_desaccord_depasse_ce_que_la_traversee_coute": (
                bool(float(annonce) > float(moy)) if (annonce and moy) else None),
            "le_demi_pli_en_voxels": int(demi),
            "la_rangee_entiere_reste_sous_le_demi_pli": valeurs.get(
                "la_rangee_entiere_reste_sous_le_demi_pli"),
            "deux_rangees_finissent_sur_des_feuillets_differents": (
                None if annonce is None else bool(float(annonce) >= float(demi))),
            "le_decalage_dorigine_en_voxels": (decalage or {}).get(
                "le_decalage_dorigine_en_voxels"),
            "lexcursion_est_insensible_au_decalage": (decalage or {}).get(
                "lexcursion_est_insensible_au_decalage"),
            "la_separation_y_est_sensible": (decalage or {}).get("la_separation_y_est_sensible"),
            "ca_saccumule": bool(epreuve.get("ca_saccumule")),
            "les_tirages_au_moins_aussi_loin": epreuve.get("les_tirages_au_moins_aussi_loin"),
            "combien_de_marches_au_hasard": epreuve.get("combien_de_marches_au_hasard"),
            "le_troncon_de_210": (par_210 or {}).get("les_coutures_du_troncon"),
            "lexcursion_moyennee_de_210_en_voxels": (par_210 or {}).get(
                "lexcursion_moyennee_en_voxels")}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            combien: int = LES_RANGEES) -> dict:
    """Les trois rangées lues, traversées séparément, puis leurs désaccords deux à deux."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    if meta is None:
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    echelle = les_rangees_du_treillis(gy)
    if not echelle.get("decidable"):
        return {"decidable": False, "raison": echelle.get("raison")}
    lignes, pas_par_rangee = {}, {}
    for r_ in echelle["les_rangees"]:
        lg = la_ligne(v, delai, colonnes, ouvrir, meta, combien, int(r_))
        if not lg.get("decidable"):
            return {"decidable": False,
                    "raison": f"la rangée {r_} est vide : {lg.get('raison')}"}
        pannes = les_pannes_de_reseau(lg.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": f"{pannes} chunks perdus par le réseau sur la rangée {r_} — une "
                              f"rangée dont le fil est tombé n'est pas comparable"}
        lignes[int(r_)] = {k: x for k, x in lg.items()
                           if k not in ("droits", "gauches", "les_colonnes")}
        pas_par_rangee[int(r_)] = les_pas_dune_rangee(lg["droits"], lg["gauches"],
                                                      lg["les_rangees_lues"])
    les_colonnes = list(range(gx if colonnes is None else min(int(colonnes), gx)))
    par_208 = ce_que_la_voisine_a_rendu()
    par_210 = ce_que_la_moyenne_a_rendu()
    predit = le_desaccord_predit(par_208.get("le_bruit_de_la_mediane_en_voxels"),
                                 par_208.get("le_bruit_de_la_voisine_en_voxels"))
    separees = les_marches_separees(pas_par_rangee, les_colonnes)
    mediane = int(echelle["la_mediane"])
    # ⚠⚠ LA PAIRE DE L'EPREUVE EST CELLE QUE `208` A DECLAREE, ET LES AUTRES SONT DES CONTROLES.
    # Declarer les trois paires diviserait la garantie par trois sans rien ajouter a la question ;
    # les publier comme description ne coute rien et dit si une voisine se comporte autrement.
    # ⚠⚠⚠ LA VOISINE DECLAREE VIENT DE `208`, MAIS SEULEMENT SI ELLE A ETE LUE. Une premiere
    # version la prenait telle quelle et mourait sur une cle absente des que le treillis n'etait
    # pas celui du rouleau — une batterie qui meurt avant son verdict ne dit rien, et c'est la
    # sonde du chemin complet qui l'a livre, pas une relecture.
    voisine = par_208.get("la_voisine_de_lepreuve")
    if voisine is None or int(voisine) not in pas_par_rangee:
        voisine = echelle["les_voisines"][0]
    declaree = (mediane, int(voisine))
    toutes = []
    for i, a in enumerate(echelle["les_rangees"]):
        for b in echelle["les_rangees"][i + 1:]:
            toutes.append((int(a), int(b)))
    paires, valeurs, decalages = {}, {}, {}
    for a, b in toutes:
        cle = f"{a}-{b}"
        d = le_desaccord_des_cumuls(pas_par_rangee[a], pas_par_rangee[b], les_colonnes, a, b)
        paires[cle] = {k: x for k, x in d.items()
                       if k not in ("les_colonnes_du_troncon",)}
        valeurs[cle] = ce_que_le_desaccord_vaut(d, predit, par_208)
        decalages[cle] = le_decalage_si_on_ne_recale_pas(separees.get(str(a)) or {},
                                                         separees.get(str(b)) or {})
    # ⚠⚠⚠ LA CLEF DE LA PAIRE DECLAREE EST CELLE SOUS LAQUELLE ELLE A ETE RANGEE, ET RIEN
    # D'AUTRE. Une premiere version la rebatissait en `min`-`max` — donc « 197-198 » quand la
    # paire est rangee « 198-197 » — et retombait sur la bonne paire par le seul ordre du
    # dictionnaire. Un nombre juste pour la mauvaise raison : le jour ou la mediane cesse d'etre
    # la premiere rangee lue, le verdict porte sur une AUTRE paire sous le nom de celle-ci.
    cle_declaree = f"{declaree[0]}-{declaree[1]}"
    if cle_declaree not in paires:
        return {"decidable": False,
                "raison": f"la paire déclarée {declaree} n'a pas été mesurée"}
    d_declaree = le_desaccord_des_cumuls(pas_par_rangee[declaree[0]],
                                         pas_par_rangee[declaree[1]], les_colonnes,
                                         declaree[0], declaree[1])
    epreuve = contre_les_signes(
        d_declaree.get("les_ecarts_de_pas_du_troncon_en_voxels") or [], PERMUTATIONS, graine)
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "les_rangees_du_treillis": echelle,
        "la_paire_declaree": [int(declaree[0]), int(declaree[1])],
        "ce_que_208_a_rendu": par_208,
        "ce_que_210_a_rendu": par_210,
        "le_desaccord_predit": predit,
        "les_lignes": lignes,
        "les_pas_par_rangee": {str(k): len(x) for k, x in pas_par_rangee.items()},
        "les_marches_separees": separees,
        "les_desaccords": paires,
        "ce_que_les_desaccords_valent": valeurs,
        "les_decalages_dorigine": decalages,
        "lepreuve": epreuve,
        "le_verdict": juger(valeurs.get(cle_declaree) or {}, d_declaree,
                            decalages.get(cle_declaree) or {}, epreuve, par_210),
        "letalon": sur_letalon(
            max(3, int(d_declaree.get("les_coutures_communes") or 240)),
            par_208.get("la_derive_partagee_en_voxels") or 1.5129,
            par_208.get("le_bruit_de_la_mediane_en_voxels") or 1.9387,
            None, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    ec = r.get("les_rangees_du_treillis") or {}
    lignes = r.get("les_lignes") or {}
    une = lignes.get(ec.get("la_mediane")) or next(iter(lignes.values()), {})
    print(f"LES RANGÉES S'ACCORDENT-ELLES   segment {une.get('segment')} · rangées "
          f"{ec.get('les_rangees')} · {une.get('colonnes_demandees')} colonnes demandées · "
          f"{len(une.get('les_rangees_lues') or [])} rangées de coupe")
    print("  LES PAS PAR RANGÉE " + " · ".join(
        f"{k}→{x}" for k, x in (r.get("les_pas_par_rangee") or {}).items()))
    for cle, m in (r.get("les_marches_separees") or {}).items():
        if m.get("decidable"):
            e = m.get("lexcursion") or {}
            print(f"  LA MARCHE {cle:<9}{m['les_troncons']} tronçons · le plus long "
                  f"{m['le_plus_long_troncon']} · excursion "
                  f"{e.get('lexcursion_en_voxels')} voxels")
    p = r.get("le_desaccord_predit") or {}
    if p.get("decidable"):
        print(f"  LA PRÉDICTION     désaccord par couture "
              f"{p['le_desaccord_par_couture_en_voxels']} voxels · racine de deux fois le bruit "
              f"en donnerait {p['ce_que_racine_de_deux_donnerait_en_voxels']} "
              f"(écart {p['lecart_entre_les_deux_ecritures_en_voxels']})")
    for cle, x in (r.get("ce_que_les_desaccords_valent") or {}).items():
        if not x.get("decidable"):
            continue
        a_la_rangee = x.get("ce_quelle_annonce_a_toutes_les_communes") or {}
        print(f"  LE DÉSACCORD {cle:<10}{x['le_desaccord_par_couture_mesure_en_voxels']} ± "
              f"{x['lerreur_dechantillonnage_en_voxels']} par couture sur "
              f"{x['les_coutures_communes']} communes · `208` en donnait "
              f"{x['ce_que_208_a_mesure_en_voxels']} (écart {x['lecart_a_208_en_erreurs']} erreur)")
        print(f"                    tronçon {x['les_coutures_du_troncon']} coutures · séparation "
              f"{x['la_separation_la_plus_grande_sur_le_troncon_en_voxels']} · final "
              f"{x['le_desaccord_final_sur_le_troncon_en_voxels']} · sous le demi-pli "
              f"{x['le_troncon_reste_sous_le_demi_pli']}")
        print(f"                    à {a_la_rangee.get('les_coutures')} coutures il annonce "
              f"{a_la_rangee.get('lecart_attendu_en_voxels')} voxels · sous le demi-pli "
              f"{x['la_rangee_entiere_reste_sous_le_demi_pli']}")
    for cle, x in (r.get("les_decalages_dorigine") or {}).items():
        if x.get("decidable"):
            print(f"  SANS RECALAGE {cle:<10}décalage d'origine "
                  f"{x['le_decalage_dorigine_en_voxels']} voxels · séparation "
                  f"{x['la_separation_sans_recalage_en_voxels']} contre "
                  f"{x['la_separation_avec_recalage_en_voxels']} recalée · l'excursion est "
                  f"insensible {x['lexcursion_est_insensible_au_decalage']}")
    ep = r.get("lepreuve") or {}
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         déplacement net {ep['le_deplacement_net_en_voxels']} contre "
              f"{ep['le_deplacement_du_nul_median_en_voxels']} au nul · "
              f"{ep['les_tirages_au_moins_aussi_loin']}/{ep['tirages']} · "
              f"{ep['combien_de_marches_au_hasard']} marche au hasard · ça s'accumule "
              f"{ep['ca_saccumule']}")
    ve = r.get("le_verdict") or {}
    if ve.get("decidable"):
        print(f"  LE VERDICT        paire {ve['la_paire']} · {ve['les_coutures_du_troncon']} "
              f"coutures · séparation {ve['la_separation_la_plus_grande_en_voxels']} voxels = "
              f"{ve['la_separation_en_demi_plis']} demi-pli · excursion "
              f"{ve['lexcursion_du_desaccord_en_voxels']} pour "
              f"{ve['ce_quune_marche_au_hasard_donnerait_en_voxels']} au hasard "
              f"(rapport {ve['le_rapport_a_la_marche_au_hasard']})")
        print(f"                    à la rangée le désaccord annonce "
              f"{ve['ce_que_le_desaccord_annonce_a_la_rangee_en_voxels']} contre "
              f"{ve['ce_que_la_moyenne_de_210_annonce_a_la_rangee_en_voxels']} pour la traversée "
              f"de `210` · deux feuillets différents "
              f"{ve['deux_rangees_finissent_sur_des_feuillets_differents']}")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats (net "
              f"{et['le_net_median_sur_la_face_positive_en_voxels']}) · {et['les_faux']} faux "
              f"sur {et['les_replicats_du_refus']} = {et['le_taux_de_faux']} pour "
              f"{et['la_garantie']} garantis · un biais partagé reste invisible "
              f"{et['un_biais_partage_reste_invisible']}")


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

    # ⭐⭐⭐⭐ LA PREDICTION EST LA RACINE DE LA SOMME DES CARRES DES DEUX BRUITS PROPRES, et la
    # sonde est batie pour que l'ecriture « racine de deux fois le bruit » DONNE AUTRE CHOSE :
    # les deux bruits poses sont differents, donc un bris qui prendrait le premier deux fois
    # sortirait un nombre distinct. Avec deux bruits egaux, les deux lectures coincident et la
    # sonde serait satisfaite par les deux.
    pr = le_desaccord_predit(1.9387, 1.899)
    exact = float(np.sqrt(1.9387 ** 2 + 1.899 ** 2))
    v("★★★★ le désaccord prédit est la racine de la SOMME DES CARRÉS des deux bruits propres",
      pr["decidable"] and abs(pr["le_desaccord_par_couture_en_voxels"] - round(exact, 4)) < 1e-9,
      f"{pr.get('le_desaccord_par_couture_en_voxels')} contre {round(exact, 4)}")
    v("★★★★ et l'écriture « racine de deux fois le bruit » en donne un AUTRE, publié à côté",
      abs(pr["ce_que_racine_de_deux_donnerait_en_voxels"]
          - pr["le_desaccord_par_couture_en_voxels"]) > 1e-9
      and pr["lecart_entre_les_deux_ecritures_en_voxels"] > 0.0,
      f"{pr.get('ce_que_racine_de_deux_donnerait_en_voxels')}")
    v("★★★ avec deux bruits ÉGAUX les deux écritures se confondent, et l'écart tombe à zéro",
      abs(le_desaccord_predit(2.0, 2.0)["lecart_entre_les_deux_ecritures_en_voxels"]) < 1e-9)
    v("★★★ un bruit propre nul d'un côté laisse l'autre seul",
      abs(le_desaccord_predit(3.0, 0.0)["le_desaccord_par_couture_en_voxels"] - 3.0) < 1e-9)
    v("★★★ un bruit propre absent ne rend AUCUNE prédiction",
      not le_desaccord_predit(None, 1.9)["decidable"]
      and not le_desaccord_predit(1.9, None)["decidable"])

    # ⚠⚠⚠ LE RECALAGE EST STRUCTUREL, ET LA FIXTURE LE REND VERIFIABLE SANS AUCUN SEUIL : deux
    # rangees aux pas IDENTIQUES mais aux TROUS DIFFERENTS doivent rendre un desaccord
    # EXACTEMENT NUL. Un bris qui soustrairait les deux cumuls propres rendrait autre chose, et
    # une sonde qui se contenterait de « le desaccord est petit » aurait ete satisfaite par les
    # deux. C'est la forme, pas la consequence.
    memes = {c: float(c % 7) - 3.0 for c in range(0, 20)}
    trouee = {c: memes[c] for c in memes if c not in (0, 1, 2)}
    # ⚠⚠ LES DEUX SONDES SONT GARDEES, PARCE QU'UN BRIS QUI PREND L'UNION LES FAIT MOURIR SUR UNE
    # CLEF ABSENTE AU LIEU DE LES FAIRE ROUGIR. Une batterie qui meurt avant son verdict ne dit
    # rien : l'exception est comptee comme un controle EN ECHEC, et nommee.
    try:
        d0 = le_desaccord_des_cumuls(memes, trouee, list(range(24)), 198, 197)
        nul = (d0["decidable"] and d0["le_desaccord_le_plus_grand_en_voxels"] == 0.0
               and d0["le_desaccord_final_en_voxels"] == 0.0)
        borne = (d0["le_plus_long_troncon"][0] == 3 and d0["les_coutures_du_troncon"] == 17)
        detail = f"{d0.get('le_desaccord_le_plus_grand_en_voxels')} · {d0.get('le_plus_long_troncon')}"
    except Exception as e:  # noqa: BLE001
        d0, nul, borne = {"decidable": False}, False, False
        detail = f"la batterie est MORTE : {type(e).__name__}"
    v("★★★★ deux rangées aux MÊMES pas mais aux trous DIFFÉRENTS ne se désaccordent en RIEN",
      nul, detail)
    v("★★★★ et le tronçon commun est celui de la rangée la plus TROUÉE, jamais de l'autre",
      borne, detail)
    sep0 = les_marches_separees({198: memes, 197: trouee}, list(range(24)))
    dec0 = le_decalage_si_on_ne_recale_pas(sep0["198"], sep0["197"])
    # ⚠⚠⚠ ET C'EST ICI QUE LA REGLE REFUTEE SE MESURE : les deux marches propres partent de
    # colonnes differentes, donc leur difference brute porte une constante que personne n'a
    # marchee. Sur cette fixture elle vaut exactement ce que la rangee complete a accumule sur
    # ses trois premieres coutures.
    attendu_decalage = abs(memes[0] + memes[1] + memes[2])
    v("★★★★ sans recalage, deux marches IDENTIQUES paraissent séparées d'un décalage d'origine",
      dec0["decidable"] and abs(dec0["le_decalage_dorigine_en_voxels"]
                                - round(attendu_decalage, 4)) < 1e-9,
      f"{dec0.get('le_decalage_dorigine_en_voxels')} pour {round(attendu_decalage, 4)}")
    v("★★★★ l'EXCURSION est insensible au décalage, et la SÉPARATION y est sensible",
      dec0["lexcursion_est_insensible_au_decalage"] and dec0["la_separation_y_est_sensible"],
      f"{dec0.get('lexcursion_sans_recalage_en_voxels')} / "
      f"{dec0.get('lexcursion_avec_recalage_en_voxels')}")
    v("★★★ deux tronçons propres sans colonne partagée ne rendent AUCUN décalage",
      not le_decalage_si_on_ne_recale_pas(
          {"decidable": True, "les_colonnes": [0, 1], "le_cumul_en_voxels": [0.0, 1.0, 2.0]},
          {"decidable": True, "les_colonnes": [8, 9], "le_cumul_en_voxels": [0.0, 1.0, 2.0]}
      )["decidable"])
    v("★★★ une marche propre indécidable ne rend AUCUN décalage",
      not le_decalage_si_on_ne_recale_pas({"decidable": False}, sep0["197"])["decidable"])

    # ⭐⭐⭐⭐ LE DESACCORD EST LE CUMUL DES DIFFERENCES, DONC IL PART DE ZERO PAR CONSTRUCTION.
    une = {c: 1.0 for c in range(10)}
    autre = {c: 0.0 for c in range(10)}
    d1 = le_desaccord_des_cumuls(une, autre, list(range(12)), 198, 197)
    v("★★★★ le désaccord cumulé part de zéro à la première couture commune",
      abs(d1["le_desaccord_cumule_en_voxels"][0]) < 1e-12)
    v("★★★★ un écart CONSTANT d'un voxel par couture donne une séparation égale au compte",
      abs(d1["le_desaccord_final_en_voxels"] - 10.0) < 1e-9,
      str(d1.get("le_desaccord_final_en_voxels")))
    v("★★★ le signe de la paire est celui de l'ordre demandé",
      abs(le_desaccord_des_cumuls(autre, une, list(range(12)), 197, 198)[
          "le_desaccord_cumule_en_voxels"][-1] + 10.0) < 1e-9)
    # ⚠⚠⚠ LES DEUX REFUS SONT GARDES : un bris qui prend l'union rend ces deux appels MORTELS
    # plutot que refuses — deux rangees qui ne partagent rien en auraient soudain tout. Une
    # exception est comptee comme un controle EN ECHEC, et nommee, sinon la batterie meurt avant
    # son verdict et le bris passe pour une panne de la sonde.
    for nom_, une_, autre_, cols_ in (
            ("moins de deux coutures communes", {0: 1.0}, {0: 2.0}, 4),
            ("aucune couture commune", {0: 1.0, 1: 2.0}, {5: 1.0, 6: 2.0}, 9)):
        try:
            refus = not le_desaccord_des_cumuls(une_, autre_, list(range(cols_)), 1,
                                                2)["decidable"]
            pourquoi = ""
        except Exception as e:  # noqa: BLE001
            refus, pourquoi = False, f"la batterie est MORTE : {type(e).__name__}"
        v(f"★★★ {nom_} ne rendent AUCUN désaccord", refus, pourquoi)
    # ⚠⚠ UN TROU COUPE LE DESACCORD COMME IL COUPE UNE MARCHE : deux coutures communes separees
    # par une colonne que l'une des deux n'a pas lue ne sont pas voisines.
    gauche = {0: 1.0, 1: 1.0, 5: 1.0, 6: 1.0, 7: 1.0}
    droite = {0: 0.0, 1: 0.0, 5: 0.0, 6: 0.0, 7: 0.0}
    d2 = le_desaccord_des_cumuls(gauche, droite, list(range(9)), 1, 2)
    v("★★★★ un trou coupe le désaccord en tronçons, et le plus long est pris",
      d2["les_troncons_communs"] == 2 and d2["les_coutures_du_troncon"] == 3,
      f"{d2.get('les_troncons_communs')} / {d2.get('les_coutures_du_troncon')}")
    v("★★★ l'écart-type sur TOUTES les communes est publié à côté de celui du tronçon",
      d2["lecart_type_des_pas_sur_toutes_les_communes_en_voxels"] is not None
      and d2["lecart_type_des_pas_du_troncon_en_voxels"] is not None)

    # ⚠⚠⚠ LES TROIS MARCHES SONT SEPAREES, ET CHACUNE SUR SON PROPRE TRONCON : la fixture donne
    # a chaque rangee un trou a un endroit different, donc un bris qui prendrait le troncon
    # COMMUN aux trois rendrait la meme longueur pour les trois — ce que la sonde refuse.
    trois = {}
    for r_, trou in ((198, 4), (197, 9), (199, 14)):
        trois[r_] = {c: 1.0 for c in range(20) if c != trou}
    sp = les_marches_separees(trois, list(range(20)))
    longueurs = sorted(m["les_coutures"] for m in sp.values())
    # ⚠⚠ LES TROIS LONGUEURS SONT CALCULEES A LA MAIN ET NON RELUES SUR LA SORTIE : un trou a la
    # colonne 4 laisse quinze coutures a droite, un trou a la colonne 9 en laisse dix, un trou a la
    # colonne 14 en laisse quatorze a gauche. Ma premiere ecriture s'etait trompee, et c'est la
    # sonde qui l'a dit — ce qui est exactement ce qu'un attendu ecrit deux fois sert a faire.
    v("★★★★ chaque rangée est traversée sur SON tronçon, et les trois diffèrent",
      longueurs == [10, 14, 15], str(longueurs))
    v("★★★★ chaque rangée porte DEUX tronçons ici, et c'est le plus long qui marche",
      all(m["les_troncons"] == 2 for m in sp.values()))
    v("★★★ une rangée dont aucune colonne n'est contiguë ne rend AUCUNE marche",
      not (les_marches_separees({5: {0: 1.0, 3: 1.0}}, list(range(6)))["5"])["decidable"])
    v("★★★ chaque marche publie son excursion et ses colonnes",
      all(m["lexcursion"]["decidable"] and len(m["les_colonnes"]) == m["les_coutures"]
          for m in sp.values()))

    # ⭐⭐⭐⭐ LA MESURE RETOMBE SUR SA PREDICTION SUR UNE MATIERE BATIE EXACTEMENT AINSI, et
    # l'encadrement est STRUCTUREL : un bris qui oublierait de soustraire la part partagee
    # sortirait BIEN AU-DESSUS, un bris qui soustrairait deux fois sortirait en dessous.
    # ⚠⚠⚠ LA TOLERANCE EST DERIVEE, JAMAIS CHOISIE : l'ecart-type d'un ecart-type estime sur `n`
    # tirages vaut lui-meme divise par la racine de deux fois `n`.
    fab = des_rangees_fabriquees(4000, 2, 1.5129, 1.9387, 0.0, 4242)
    df = le_desaccord_des_cumuls(fab[0], fab[1], list(range(4000)), 0, 1)
    pf = le_desaccord_predit(1.9387, 1.9387)
    faux_208 = {"le_desaccord_des_pas_en_voxels": pf["le_desaccord_par_couture_en_voxels"]}
    qf = ce_que_le_desaccord_vaut(df, pf, faux_208)
    mes = float(qf["le_desaccord_par_couture_mesure_en_voxels"])
    err = float(qf["lerreur_dechantillonnage_en_voxels"])
    v("★★★★ le désaccord mesuré s'accorde à sa prédiction à trois erreurs près",
      qf["decidable"] and abs(mes - float(pf["le_desaccord_par_couture_en_voxels"]))
      < 3.0 * err, f"{mes} contre {pf['le_desaccord_par_couture_en_voxels']} ± {round(err, 4)}")
    v("★★★★ et il est très AU-DESSUS de ce qu'UNE rangée porte — la part partagée ne s'y trouve "
      "plus, mais les deux bruits propres si",
      mes > float(np.sqrt(1.5129 ** 2 + 1.9387 ** 2)),
      f"{mes} contre {round(float(np.sqrt(1.5129 ** 2 + 1.9387 ** 2)), 4)}")
    v("★★★★ et très SOUS ce que deux rangées SANS part partagée donneraient",
      mes < float(np.sqrt(2.0)) * float(np.sqrt(1.5129 ** 2 + 1.9387 ** 2)) - 3.0 * err)
    # ⚠⚠ LA SONDE PORTE SUR UNE IDENTITE ENTRE DEUX NOMBRES PUBLIES, jamais sur une seconde
    # ecriture de la formule : recopier le calcul du producteur en ferait une SECONDE
    # DEFINITION, libre de deriver avec lui. La tolerance vient de l'arrondi publie.
    arrondi = 5e-5
    v("★★★★ l'erreur d'échantillonnage porte bien le facteur DEUX du compte de coutures",
      abs(err * float(np.sqrt(2.0 * qf["les_coutures_communes"])) - mes)
      < arrondi * float(np.sqrt(2.0 * qf["les_coutures_communes"])) + arrondi,
      f"{err} × racine de 2×{qf['les_coutures_communes']} pour {mes}")
    v("★★★★ l'écart à `208` est compté EN ERREURS, pas en voxels",
      abs(float(qf["lecart_a_208_en_erreurs"]) * err
          - (mes - float(qf["ce_que_208_a_mesure_en_voxels"])))
      < arrondi * (2.0 + abs(float(qf["lecart_a_208_en_erreurs"]))))
    v("★★★ et le recoupement à trois erreurs près est publié comme tel",
      qf["il_recoupe_208"] is bool(abs(float(qf["lecart_a_208_en_erreurs"])) <= 3.0))
    v("★★★ un désaccord indécidable ne rend AUCUNE valeur",
      not ce_que_le_desaccord_vaut({"decidable": False}, pf, faux_208)["decidable"])
    # ⚠⚠⚠ ET LA COMPARAISON AU DEMI-PLI EST UNE COMPARAISON, PAS UN SEUIL CHOISI : un desaccord
    # par couture assez grand DOIT faire basculer le verdict de la rangee entiere. Une sonde qui
    # n'aurait lu que le cas mesure n'aurait exerce qu'une des deux branches.
    petit = ce_que_le_desaccord_vaut(
        le_desaccord_des_cumuls({c: 0.001 for c in range(40)}, {c: 0.0 for c in range(40)},
                                list(range(40)), 1, 2), pf, faux_208)
    v("★★★★ un désaccord minuscule laisse la rangée entière SOUS le demi-pli",
      petit["la_rangee_entiere_reste_sous_le_demi_pli"] is True)
    v("★★★★ et le désaccord mesuré sur la matière fabriquée la fait passer AU-DESSUS",
      qf["la_rangee_entiere_reste_sous_le_demi_pli"] is False,
      str((qf.get("ce_quelle_annonce_a_toutes_les_communes") or {}).get(
          "lecart_attendu_en_voxels")))

    # ⭐⭐⭐⭐ L'ETALON, ET SON CONTROLE STRUCTUREL : un biais PROPRE se voit, un biais PARTAGE
    # reste invisible. C'est l'inverse exact de `210`, et c'est ce qui dit de quoi l'epreuve
    # separe. Une premiere version n'avait que la face positive et la face negative — elle
    # aurait ete satisfaite par une epreuve qui reagit a n'importe quel biais.
    et = sur_letalon(240, 1.5129, 1.9387, 2.0, 4242, 6, 19)
    v("★★★★ l'étalon trouve le biais PROPRE dans tous ses réplicats",
      et["decidable"] and et["les_vus"] == et["replicats"],
      f"{et.get('les_vus')}/{et.get('replicats')}")
    # ⚠⚠⚠ LA SONDE PORTE SUR UN TAUX ET NON SUR UN ZERO, et c'est la mesure qui l'a imposee :
    # exiger zero de douze replicats d'un nul qui tire a une chance sur vingt a fait refuser un
    # etalon parfaitement sain. Ce qui se verifie est que le biais PARTAGE ne fait pas mieux que
    # l'absence de biais, au meme compte et sous la meme garantie.
    v("★★★★ et un biais PARTAGÉ par les deux rangées reste INVISIBLE — il s'annule",
      et["un_biais_partage_reste_invisible"]
      and et["le_taux_du_controle_aveugle"] <= 2.0 * GARANTIE_PAR_EPREUVE + 1e-12,
      f"{et.get('les_biais_partages_vus')}/{et.get('les_replicats_du_controle_aveugle')}")
    v("★★★★ la face négative refuse, au compte DÉRIVÉ de la garantie et non au plancher de `202`",
      et["le_taux_de_faux"] <= 2.0 * GARANTIE_PAR_EPREUVE + 1e-12
      and et["les_replicats_du_refus"] > et["le_plancher_de_202"],
      f"{et.get('les_faux')}/{et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare, et le dit",
      et["letalon_separe"] is True)
    v("★★★ le biais posé est celui qu'on lui donne, et il est publié",
      abs(et["le_biais_propre_pose_en_voxels"] - 2.0) < 1e-12)
    # ⚠⚠⚠ ET LA REGLE COMPOSEE EST EXERCEE, PARCE QUE LIRE CE QUE CHAQUE FACE DIT SEPAREMENT NE
    # L'EXERCE PAS : un bris qui retirait le controle aveugle du verdict restait vert, puisque
    # sur du code juste les trois conditions sont vraies ensemble. Ici le controle aveugle est
    # rendu VOYANT par un parametre, les deux autres faces ne bougent pas, et le verdict DOIT
    # cesser de separer. Un controle qui ne peut pas tirer ne prouve rien non plus.
    voyant = sur_letalon(240, 1.5129, 1.9387, 2.0, 4242, 6, 19, aveugle_propre=2.0)
    v("★★★★ le contrôle aveugle PEUT tirer : rendu voyant, il voit tous ses réplicats",
      voyant["les_biais_partages_vus"] == voyant["les_replicats_du_controle_aveugle"],
      f"{voyant.get('les_biais_partages_vus')}/"
      f"{voyant.get('les_replicats_du_controle_aveugle')}")
    v("★★★★ et le contrôle aveugle porte le MÊME compte que l'autre face négative",
      et["les_replicats_du_controle_aveugle"] == et["les_replicats_du_refus"],
      f"{et.get('les_replicats_du_controle_aveugle')} contre {et.get('les_replicats_du_refus')}")
    v("★★★★ et alors l'étalon CESSE de séparer, alors que ses deux autres faces n'ont pas bougé",
      voyant["letalon_separe"] is False
      and voyant["les_vus"] == et["les_vus"] and voyant["les_faux"] == et["les_faux"],
      f"{voyant.get('letalon_separe')} · {voyant.get('les_vus')} · {voyant.get('les_faux')}")
    # ⚠⚠⚠ LE DEFAUT PAR DEFAUT EST EXERCE PAR UN APPEL QUI NE LE PASSE PAS : passer `None` en
    # cinquieme position aurait exerce le lecteur et non le defaut, et c'est le defaut de `208`
    # que `210` a paye un cran plus bas.
    v("★★★★ sans `199`, l'étalon REFUSE plutôt que de choisir un biais",
      not sur_letalon(24, 1.5129, 1.9387, lecteur=lambda: {"decidable": False},
                      replicats=1, tirages=3)["decidable"])
    # ⚠⚠ LE COMPTE DU REFUS VIENT DE `210`, IMPORTE : le reecrire ici en ferait une seconde
    # definition d'une regle de calibration dont deux tranches dependent.
    v("★★★ le compte décisif est celui que `210` dérive, et il dépasse le plancher de `202`",
      les_replicats_du_refus(GARANTIE_PAR_EPREUVE)["le_compte_decisif"]
      > les_replicats_du_refus(GARANTIE_PAR_EPREUVE)["le_plancher_de_202"])

    # ⚠⚠ LE VERDICT SE LIT PAR `.get()` ET NE MEURT PAS : une batterie qui meurt avant son
    # verdict ne dit rien, et c'est une panne que cette chaine a payee.
    try:
        jv = juger(qf, df, dec0, contre_les_signes([1.0, 2.0, 3.0], 5, 1), {})
        ok_j = jv.get("decidable") is True
    except Exception as e:  # noqa: BLE001
        ok_j = False
        jv = {"raison": f"{type(e).__name__}"}
    v("★★★★ le verdict se rend même quand `210` n'a rien publié", ok_j, str(jv.get("raison")))
    v("★★★ un désaccord indécidable ne rend AUCUN verdict",
      not juger({"decidable": False}, df, dec0,
                contre_les_signes([1.0, 2.0], 5, 1), {})["decidable"])
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger(qf, df, dec0, {"decidable": False}, {})["decidable"])
    # ⚠⚠⚠ ET UN DICTIONNAIRE SANS LA CLEF `decidable` DU TOUT, parce que c'est CE cas que le
    # `.get()` existe pour tenir : un bris qui l'ecrit en indexation directe passe tous les
    # appels dont le dictionnaire porte la clef, et ne meurt que sur celui qui ne la porte pas.
    for absent, ou in (({}, "le désaccord"), (qf, "l'épreuve")):
        try:
            rendu = (juger(absent, df, dec0, contre_les_signes([1.0, 2.0], 5, 1), {})
                     if ou == "le désaccord" else juger(qf, df, dec0, {}, {}))
            ok_a = rendu.get("decidable") is False
            pourquoi = str(rendu.get("raison"))
        except Exception as e:  # noqa: BLE001
            ok_a, pourquoi = False, f"la batterie est MORTE : {type(e).__name__}"
        v(f"★★★★ {ou} sans clef `decidable` est refusé, et le verdict ne MEURT pas",
          ok_a, pourquoi)
    v("★★★ le verdict publie la longueur du tronçon À CÔTÉ de la séparation",
      jv.get("les_coutures_du_troncon") is not None
      and jv.get("la_separation_la_plus_grande_en_voxels") is not None)

    # ⚠⚠⚠ LES LECTEURS REFUSENT PLUTOT QUE DE DEVINER.
    v("★★★ `208` absent est refusé, pas remplacé",
      not ce_que_la_voisine_a_rendu(Path("/absent/208.json"))["decidable"])
    v("★★★ `210` absent est refusé, pas remplacé",
      not ce_que_la_moyenne_a_rendu(Path("/absent/210.json"))["decidable"])
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.json"
        p.write_text(json.dumps({"le_verdict": {"decidable": True}}), encoding="utf-8")
        v("★★★ un `208` sans bruit propre est refusé",
          not ce_que_la_voisine_a_rendu(p)["decidable"])
        v("★★★ un `210` sans excursion est refusée",
          not ce_que_la_moyenne_a_rendu(p)["decidable"])
        p.write_text(json.dumps({"le_verdict": {
            "decidable": True, "le_bruit_de_la_mediane_en_voxels": 1.9387,
            "le_bruit_de_la_voisine_en_voxels": 1.899,
            "lecart_type_observe_en_voxels": 2.7138}}), encoding="utf-8")
        lu = ce_que_la_voisine_a_rendu(p)
        v("★★★★ le désaccord des PAS de `208` est relu, et c'est LUI le recoupement",
          lu["decidable"] and lu["le_desaccord_des_pas_en_voxels"] == 2.7138)
        # ⚠⚠⚠ ET LE FAIT QUI DOIT ETRE DIT PLUTOT QU'ENCAISSE : la prediction derivee des deux
        # bruits propres de `208` REDONNE son desaccord des pas, parce que `208` a derive ces
        # bruits de ce desaccord meme. Ce n'est donc PAS un recoupement independant, et la sonde
        # le constate au lieu de laisser croire le contraire.
        pd_ = le_desaccord_predit(lu["le_bruit_de_la_mediane_en_voxels"],
                                  lu["le_bruit_de_la_voisine_en_voxels"])
        v("★★★★ la prédiction dérivée de `208` REDONNE son désaccord des pas — identité, pas "
          "recoupement",
          abs(pd_["le_desaccord_par_couture_en_voxels"]
              - lu["le_desaccord_des_pas_en_voxels"]) < 1e-3,
          f"{pd_['le_desaccord_par_couture_en_voxels']} contre "
          f"{lu['le_desaccord_des_pas_en_voxels']}")

    # ⚠⚠⚠ ET LA MESURE COMPLETE TRAVERSE TOUT LE CHEMIN SUR UN FAUX DEPOT, parce qu'une chaine
    # dont chaque maillon est sonde separement peut encore etre mal cablee.
    meta = {"chunks": [109, 12, 12], "shape": [109, 36, 40]}
    bloc = np.random.default_rng(31).normal(0.5, 0.2, size=(109, 12, 12)).astype(np.float32)

    def _depot(cy, cx):
        """Un dépôt qui REFUSE une rangée hors du treillis — comme le vrai le ferait."""
        return ((bloc, None) if 0 <= int(cy) < 3 else (None, "absent du dépôt"))

    out = mesurer(0.0, GRAINE, 1, 4, _depot, meta, 4)
    v("★★★★ la mesure complète traverse les trois rangées du treillis",
      len(out.get("les_pas_par_rangee") or {}) == 3, str(out.get("raison")))
    v("★★★★ elle publie les TROIS marches séparées, une par rangée",
      len(out.get("les_marches_separees") or {}) == 3,
      str(list((out.get("les_marches_separees") or {}))))
    v("★★★★ elle publie les TROIS paires de désaccord, pas seulement celle de l'épreuve",
      len(out.get("les_desaccords") or {}) == 3,
      str(list((out.get("les_desaccords") or {}))))
    # ⚠⚠⚠ ET LE VERDICT PORTE SUR LA PAIRE DECLAREE, PAS SUR CELLE QUI SE TROUVE ETRE PREMIERE.
    # La sonde compare le verdict au desaccord RANGE sous la clef de cette paire : un bris qui
    # rebatit la clef autrement retombe sur une autre paire, et le nom publie cesse de designer
    # ce qui a ete mesure.
    pd_declaree = out.get("la_paire_declaree") or []
    vd = out.get("le_verdict") or {}
    v("★★★ la paire déclarée est celle que `208` a déclarée, ou la première voisine",
      len(pd_declaree) == 2)
    v("★★★★ le verdict porte sur la paire DÉCLARÉE, et sa clef est celle sous laquelle elle est "
      "rangée",
      vd.get("la_paire") == pd_declaree
      and f"{pd_declaree[0]}-{pd_declaree[1]}" in (out.get("les_desaccords") or {}),
      f"{vd.get('la_paire')} contre {pd_declaree}")
    v("★★★ elle publie un décalage d'origine par paire",
      len(out.get("les_decalages_dorigine") or {}) == 3)
    v("★★★ elle publie la question déclarée et sa garantie",
      out.get("la_question_declaree") == LA_QUESTION_DECLAREE
      and out.get("la_garantie_par_epreuve") is not None)

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
