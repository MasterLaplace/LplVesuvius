"""Peut-on DÉPLIER la phase — l'absolu modulo un pli, plus le différentiel qui dérive ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P49` QUI LE NOMME. `199` rend un incrément RELATIF qui ne
saute jamais — pas quadratique **4,941 voxels**, **0 pas** saturés sur **254** — mais qui dérive
comme la racine du nombre de pas. `200` rend un repère ABSOLU, lisible dans **245** chunks sur
**251**, mais défini **modulo un pli** : il dit qu'il y a une frontière, jamais LAQUELLE. Les deux
moitiés manquantes sont exactement complémentaires, et c'est le problème classique du DÉPLIAGE DE
PHASE.

⭐⭐⭐⭐ ET LE THÉORÈME QUI LE RÉSOUT EST CELUI D'ITOH, DONT LA CONDITION EST DÉJÀ MESURÉE. Si le
déplacement vrai entre deux échantillons reste sous la DEMI-PÉRIODE, alors replier chaque écart
observé dans $[-P/2, P/2[$ et les accumuler reconstruit la trace absolue EXACTEMENT. `199` a
publié ce qu'il fallait pour le savoir : son pas maximal et son pas quadratique se comparent aux
**36** voxels de la demi-période. Le différentiel n'entre donc pas terme à terme — il CERTIFIE que
le dépliage par continuité est licite. C'est un usage plus fort, et il ne demande aucun alignement.

⚠⚠⚠ CE QUI OBLIGE À CETTE FORME EST UN DÉFAUT RÉEL DE LA PUBLICATION DE `199`, ET IL EST NOMMÉ ICI
PLUTÔT QUE CONTOURNÉ : le tronçon porte **257** chunks, donc **256** intervalles, et seulement
**254** pas décidables. Le cumul est indexé par numéro de pas et non par colonne, donc deux pas
manquants à des positions inconnues décalent la correspondance. Joindre les deux traces colonne à
colonne demanderait de DEVINER où, et un déplacement deviné vaut jusqu'à deux fois le plus grand pas
lu — davantage que la demi-période. Le compte est publgié (`les_pas_sans_colonne`), et la tranche
mesure ce qu'elle peut mesurer sans deviner.

⚠⚠⚠ LE PIÈGE EST ÉCRIT D'AVANCE, ET IL EST HÉRITÉ : un pas de plus d'une demi-période ALIASE au lieu
de saturer (`199` : posé **41** voxels, lu **-31**). Le dépliage hérite de cet angle mort. Les pas
dépliés qui sortent de l'enveloppe du différentiel, et ceux qui frôlent la limite d'alias, sont
comptés et publiés AVANT tout verdict — c'est la seule chose qui distingue un dépliage qui marche
d'un dépliage qui a l'air de marcher.

⚠⚠ UNE SEULE ÉPREUVE EST DÉCLARÉE, et c'est ce qui garde la garantie entière : la phase se suit-elle
d'un chunk au suivant, c'est-à-dire les écarts repliés sont-ils plus serrés que sous TOUT mélange des
mêmes phases. La comparaison des excursions qui suit est une comparaison de nombres déjà publiés,
pas une seconde épreuve.

⚠ ET LA TRANCHE NE TÉLÉCHARGE RIEN : les deux traces existent, sur la MÊME rangée du MÊME segment.

Usage :
    uv run python src/nappe/peut_on_deplier_la_phase.py --verifier
    uv run python src/nappe/peut_on_deplier_la_phase.py \\
        --json docs/mesures/peut_on_deplier_la_phase.json
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

from la_recette_posee_sur_le_rouleau import PERMUTATIONS  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import le_taux_tient_la_garantie  # noqa: E402
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_MARCHE_A_RENDU = MESURES / "la_derive_saccumule_t_elle.json"
CE_QUE_LE_CREUX_A_RENDU = MESURES / "le_creux_borne_t_il_la_marche.json"
GRAINE = 20261009

LA_QUESTION_DECLAREE = ("le creux, déplié par continuité, rend-il l'ordinal que ni l'absolu ni "
                        "le différentiel ne portent ?")
LES_EPREUVES_DECLAREES = ("la phase se suit-elle d'un chunk au suivant",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def le_repli(x, periode: float = PAS_EN_VOXELS):
    """Replie un écart dans la demi-période, en $[-P/2, P/2[$ — l'opération centrale du dépliage.

    ⚠⚠ LE REPLI EST EXPLICITEMENT A GAUCHE, ET NON CONFIE A `round` : l'arrondi de numpy est
    banquier, donc il envoie `P/2` sur zero et `3P/2` sur deux, et l'intervalle cesse d'etre le meme
    des deux cotes. Un plancher de `x/P + 1/2` rend un intervalle demi-ouvert, identique partout.
    """
    a = np.asarray(x, dtype=float)
    p = float(periode)
    return a - p * np.floor(a / p + 0.5)


def la_phase(couches, periode: float = PAS_EN_VOXELS):
    """La couche du creux, ramenée modulo un pli — ce que le repère porte RÉELLEMENT.

    ⭐⭐⭐⭐ C'EST LA LECTURE QUE `200` N'A PAS FAITE. Le cube porte **1,51** pli, donc deux frontieres
    peuvent y tomber et le lecteur en designe UNE : la couche brute melange les deux repliques, et
    c'est pourquoi sa dispersion ressemble a un tirage au hasard. La phase les ramene l'une sur
    l'autre.
    """
    a = np.asarray(couches, dtype=float)
    p = float(periode)
    return a - p * np.floor(a / p)


def les_ecarts_replies(phases, periode: float = PAS_EN_VOXELS):
    """L'écart replié d'une phase à la suivante — le pas que le dépliage accumule."""
    return le_repli(np.diff(np.asarray(phases, dtype=float)), periode)


def la_statistique(phases, periode: float = PAS_EN_VOXELS) -> float:
    """Le pas quadratique des écarts repliés — LA statistique de l'unique épreuve déclarée.

    ⭐ ELLE EST L'ENONCE DIRECT DE LA CONDITION D'ITOH : un repere qui suit la meme frontiere d'un
    chunk au suivant rend des ecarts repliés petits ; un repere qui designe une frontiere au hasard
    rend des ecarts etales sur toute la demi-periode.
    """
    e = les_ecarts_replies(phases, periode)
    if e.size == 0:
        return 0.0
    return float(np.sqrt(float(np.mean(e * e))))


def le_depliage(phases, periode: float = PAS_EN_VOXELS) -> dict:
    """Déplie la phase par continuité — la trace absolue que ni `199` ni `200` ne portent.

    ⭐⭐⭐⭐ C'EST LE GESTE QUE LA PORTE DEMANDE, et il tient en une ligne : chaque pas est l'ecart
    replié, et la trace est leur somme. Ce qui en sort n'est plus « une frontiere modulo un pli »
    mais UNE frontiere designee, donc un ORDINAL.

    ⚠⚠⚠ ET SON ANGLE MORT EST STRUCTUREL : un pas vrai de plus d'une demi-periode revient replié du
    mauvais cote, et la trace perd un pli SANS RIEN SIGNALER. Les deux comptes publies ici disent a
    quel point on en est pres ; ils ne le detectent pas, parce que rien dans la phase seule ne le
    peut.
    """
    p = np.asarray(phases, dtype=float)
    if p.size < 2:
        return {"decidable": False, "raison": "moins de deux phases"}
    pas = les_ecarts_replies(p, periode)
    trace = np.concatenate(([0.0], np.cumsum(pas)))
    return {"decidable": True, "les_pas": int(pas.size),
            "la_trace_en_voxels": [round(float(x), 4) for x in trace],
            "les_pas_en_voxels": [round(float(x), 4) for x in pas],
            "le_deplacement_net_en_voxels": round(float(trace[-1]), 4),
            "le_deplacement_net_en_plis": round(float(trace[-1]) / float(periode), 6),
            "lexcursion_en_voxels": round(float(np.max(trace) - np.min(trace)), 4),
            "lexcursion_en_plis": round(float(np.max(trace) - np.min(trace))
                                        / float(periode), 6),
            "le_pas_quadratique_en_voxels": round(float(np.sqrt(float(np.mean(pas * pas)))), 4)}


def langle_mort(pas_deplies, enveloppe: float, pas_quadratique: float,
                demi_periode: float = float(DEMI_PAS_EN_VOXELS)) -> dict:
    """Combien de pas dépliés le différentiel ne cautionne pas — PUBLIÉ AVANT TOUT VERDICT.

    ⚠⚠⚠ LES DEUX SEUILS SONT DES NOMBRES DU PRODUCTEUR, PAS DES CHOIX. L'enveloppe est le plus grand
    pas que `199` ait jamais lu : un pas déplié plus grand que cela n'a ete cautionne par aucune
    mesure differentielle. Et la marge d'alias se compare au pas QUADRATIQUE de `199` : un pas
    déplié dont il reste moins que cela avant la demi-periode bascule de replique sur une seule
    erreur typique.
    """
    a = np.abs(np.asarray(pas_deplies, dtype=float))
    if a.size == 0:
        return {"decidable": False, "raison": "aucun pas déplié"}
    marge = float(demi_periode) - a
    return {"decidable": True, "les_pas": int(a.size),
            "lenveloppe_du_differentiel_en_voxels": round(float(enveloppe), 4),
            "les_pas_hors_enveloppe": int(np.sum(a > float(enveloppe))),
            "la_part_hors_enveloppe": round(float(np.mean(a > float(enveloppe))), 6),
            "la_marge_dalias_exigee_en_voxels": round(float(pas_quadratique), 4),
            "les_pas_au_bord_de_lalias": int(np.sum(marge < float(pas_quadratique))),
            "la_part_au_bord_de_lalias": round(float(np.mean(marge < float(pas_quadratique))), 6),
            "la_marge_mediane_en_voxels": round(float(np.median(marge)), 4)}


def contre_le_melange(phases, tirages: int = PERMUTATIONS, graine: int = GRAINE,
                      periode: float = PAS_EN_VOXELS,
                      garantie: float = GARANTIE_PAR_EPREUVE) -> dict:
    """La phase se suit-elle, ou un mélange des mêmes phases fait-il aussi bien ? L'ÉPREUVE.

    ⭐⭐⭐⭐ LE MELANGE EST LE NUL EXACT, ET IL N'EST PAS VIDE. Il garde la loi marginale des phases —
    donc tout ce que le cube impose : sa profondeur, ses deux repliques, la forme du lecteur — et ne
    detruit que l'ORDRE. Or le pas quadratique des ecarts replies depend de l'ordre, contrairement au
    deplacement net de `199`, qu'une permutation laissait inchange. Le nul mord.

    ⚠⚠ ET LA MARGINALE, ELLE, EST INVARIANTE PAR MELANGE : aucune dispersion de phase ne se teste
    ainsi, et c'est pourquoi elle est publiee comme une DESCRIPTION et jamais comme une epreuve.
    """
    p = np.asarray(phases, dtype=float)
    if p.size < 3:
        return {"decidable": False, "raison": "moins de trois phases"}
    obs = la_statistique(p, periode)
    r = _rng(int(graine))
    nuls = [la_statistique(r.permutation(p), periode) for _ in range(int(tirages))]
    aussi_serres = int(sum(1 for x in nuls if x <= obs + 1e-12))
    pv = float(aussi_serres + 1) / float(int(tirages) + 1)
    return {"decidable": True, "tirages": int(tirages),
            "le_pas_quadratique_observe_en_voxels": round(obs, 4),
            "le_pas_quadratique_median_du_nul_en_voxels": round(float(np.median(nuls)), 4),
            "le_pas_quadratique_minimal_du_nul_en_voxels": round(float(np.min(nuls)), 4),
            "les_melanges_au_moins_aussi_serres": aussi_serres,
            # ⭐⭐⭐⭐ LE RAPPORT AU NUL DIT CE QUE LE VERDICT NE DIT PAS : une epreuve peut se
            # declencher au plancher exact des tirages tout en ne s'ecartant du nul que de quelques
            # pour cent. Publier le rapport EMPECHE de lire « oui » comme « fortement ».
            "le_rapport_au_nul": round(obs / float(np.median(nuls)), 4),
            "la_valeur_p": round(pv, 7),
            "la_garantie_de_lepreuve": round(float(garantie), 7),
            "la_phase_se_suit": bool(pv <= float(garantie) + 1e-12)}


def ce_que_le_creux_a_rendu(chemin: Path = CE_QUE_LE_CREUX_A_RENDU) -> dict:
    """Ce que `200` a publié sur cette rangée — relu, jamais recalculé.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ETALON NE SEPARE PAS : un repere aveugle rendrait une suite de
    couches qui se deplierait tout aussi bien, et le dépliage d'un bruit est un bruit deplié.

    ⚠ LES TROUS SONT DERIVES DES COLONNES, JAMAIS LUS DANS UNE CLEF : c'est la seule facon de savoir
    sur combien de coutures chaque ecart replié accumule.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `200` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    t = d.get("la_trace_absolue") or {}
    if not t.get("decidable"):
        return {"decidable": False, "raison": "la trace absolue de `200` est indécidable"}
    if not (d.get("letalon") or {}).get("letalon_separe"):
        return {"decidable": False, "raison": "l'étalon de `200` ne sépare pas"}
    cols = [int(c) for c in t.get("les_colonnes") or []]
    couches = [int(k) for k in t.get("la_trace_en_couches") or []]
    if len(cols) != len(couches) or len(cols) < 3:
        return {"decidable": False, "raison": "colonnes et couches ne s'apparient pas"}
    trous = np.diff(np.asarray(cols, dtype=int))
    return {"decidable": True, "les_reperes": len(cols),
            "la_rangee": (d.get("la_ligne") or {}).get("la_rangee"),
            "les_couches_du_cube": t.get("les_couches_du_cube"),
            "lexcursion_en_plis": t.get("lexcursion_en_plis"),
            "les_sauts_de_plus_dun_demi_pli": t.get("les_sauts_de_plus_dun_demi_pli"),
            "les_colonnes": cols, "la_trace_en_couches": couches,
            "les_coutures_par_ecart": [int(x) for x in trous],
            "la_plus_longue_couture": int(trous.max()),
            "les_ecarts_sur_une_seule_couture": int(np.sum(trous == 1))}


def ce_que_la_marche_a_rendu(chemin: Path = CE_QUE_LA_MARCHE_A_RENDU) -> dict:
    """Ce que `199` a publié sur la MÊME rangée — et le défaut d'alignement, compté et nommé.

    ⚠⚠⚠ `les_pas_sans_colonne` EST LE DEFAUT, ET IL EST PUBLIE PLUTOT QUE CONTOURNE : un tronçon de
    `n` chunks porte `n-1` intervalles, et `199` n'en a rendu que `pas`. La difference est le nombre
    de pas dont la colonne est inconnue, donc le nombre de decalages possibles entre le cumul publie
    et les colonnes. Tant qu'il n'est pas nul, joindre les deux traces terme a terme serait deviner.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `199` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    m = d.get("la_marche") or {}
    if not m.get("decidable"):
        return {"decidable": False, "raison": "la marche de `199` est indécidable"}
    # ⚠⚠⚠ `199` HISSE SES PAS A LA RACINE DU DOCUMENT, PAS DANS `la_marche` : ses `mesurer` les en
    # retire explicitement pour ne pas alourdir le bloc. Mes premieres sondes ne lisaient que
    # `la_marche` — et elles passaient, parce que leur FIXTURE les y mettait. C'est la mesure reelle
    # qui l'a dit, en rendant « `199` ne publie aucun pas ». Les deux emplacements sont lus, et les
    # deux sont exerces.
    bruts = d.get("les_pas_en_voxels") or m.get("les_pas_en_voxels") or []
    pas = np.abs(np.asarray(bruts, dtype=float))
    if pas.size == 0:
        return {"decidable": False, "raison": "`199` ne publie aucun pas"}
    manquants = sum(max(0, int(t.get("chunks", 0)) - 1 - int(t.get("pas", 0)))
                    for t in m.get("les_troncons") or [])
    demi = float(DEMI_PAS_EN_VOXELS)
    q = float(m.get("le_pas_quadratique_en_voxels") or 0.0)
    return {"decidable": True, "les_pas": int(m.get("les_pas") or pas.size),
            "la_rangee": (d.get("la_ligne") or {}).get("la_rangee"),
            "le_pas_quadratique_en_voxels": m.get("le_pas_quadratique_en_voxels"),
            "le_pas_maximal_en_voxels": round(float(pas.max()), 4),
            "la_marge_du_pas_maximal_en_voxels": round(demi - float(pas.max()), 4),
            "les_pas_au_bord_de_lalias": int(np.sum(pas > demi - q)),
            "les_pas_qui_saturent": m.get("les_pas_qui_saturent"),
            "lexcursion_en_plis": m.get("lexcursion_maximale_en_plis"),
            "les_pas_sans_colonne": int(manquants),
            "le_cumul_est_indexable_par_colonne": bool(manquants == 0)}


def la_condition_ditoh(marche: dict, creux: dict,
                       demi_periode: float = float(DEMI_PAS_EN_VOXELS)) -> dict:
    """Le différentiel certifie-t-il que le dépliage est licite ? PUBLIÉ AVANT LE VERDICT.

    ⭐⭐⭐⭐ C'EST LE ROLE QUE `199` TIENT ICI, ET IL EST PLUS FORT QUE D'ETRE ADDITIONNE TERME A
    TERME : le dépliage par continuite est exact tant que le deplacement VRAI entre deux echantillons
    reste sous la demi-periode. `199` a mesure ce deplacement. La certification se lit donc dans ses
    nombres publies, sans qu'aucun alignement colonne a colonne soit necessaire.

    ⚠⚠ ET ELLE NE VAUT PAS PARTOUT : `200` saute des colonnes, et un ecart qui enjambe `g` coutures
    accumule `g` pas. Le PIRE CAS s'obtient en empilant `g` fois le plus grand pas lu, le cas TYPIQUE
    en multipliant le pas quadratique par la racine de `g`. Les deux sont publies, parce qu'ils ne
    disent pas la meme chose et que ne publier que le second flatterait le resultat.
    """
    if not marche.get("decidable") or not creux.get("decidable"):
        return {"decidable": False, "raison": "une des deux lectures manque"}
    mx = float(marche["le_pas_maximal_en_voxels"])
    q = float(marche["le_pas_quadratique_en_voxels"])
    g = np.asarray(creux["les_coutures_par_ecart"], dtype=float)
    pire = g * mx
    typique = q * np.sqrt(g)
    return {"decidable": True,
            "la_demi_periode_en_voxels": float(demi_periode),
            "le_pas_maximal_de_199_en_voxels": round(mx, 4),
            "le_pas_quadratique_de_199_en_voxels": round(q, 4),
            "aucun_pas_lu_ne_depasse_la_demi_periode": bool(mx < float(demi_periode)),
            # ⚠⚠⚠ ET CE VRAI-LA NE CERTIFIE RIEN : un pas lu NE PEUT PAS depasser la demi-periode,
            # parce que la recherche de `199` s'y arrete et qu'un pas plus grand ALIASE au lieu de
            # saturer — `199` l'a mesure, pose 41 et lu -31. La condition d'Itoh porte sur le pas
            # VRAI, qu'aucune mesure differentielle de cette forme ne peut voir. Le dire est la
            # difference entre une certification et une tautologie.
            "la_condition_est_refutable_par_cette_mesure": False,
            "la_marge_du_pas_maximal_en_voxels": marche.get(
                "la_marge_du_pas_maximal_en_voxels"),
            "les_pas_de_199_au_bord_de_lalias": marche.get("les_pas_au_bord_de_lalias"),
            "les_ecarts": int(g.size),
            "les_ecarts_certifies_au_pire": int(np.sum(pire < float(demi_periode))),
            "les_ecarts_certifies_au_typique": int(np.sum(typique < float(demi_periode))),
            "le_pire_cas_maximal_en_voxels": round(float(pire.max()), 4),
            "le_cas_typique_maximal_en_voxels": round(float(typique.max()), 4)}


def la_marginale(phases, couches: int, periode: float = PAS_EN_VOXELS,
                 tirages: int = 4096, graine: int = GRAINE) -> dict:
    """La dispersion de la phase, et celle qu'un tirage au hasard DANS LE CUBE rendrait.

    ⚠⚠⚠ LE NUL N'EST PAS UNE PHASE UNIFORME, ET C'EST LE PIEGE DE CETTE LECTURE : le cube porte
    **1,51** pli, donc une couche tiree uniformement dans le cube puis ramenee modulo un pli charge
    DEUX FOIS la premiere demi-periode. Comparer a une phase uniforme ferait passer cette asymetrie
    pour de l'information. Le nul est donc la loi uniforme du cube REDUITE, tiree explicitement.

    ⚠⚠ ET CETTE QUANTITE NE SE TESTE PAS PAR MELANGE : elle est invariante par permutation. Elle est
    publiee comme description, jamais comme epreuve.
    """
    p = np.asarray(phases, dtype=float)
    if p.size < 2 or int(couches) <= 0:
        return {"decidable": False, "raison": "phase ou profondeur absente"}
    r = _rng(int(graine) + 1)
    nul = la_phase(r.uniform(0.0, float(couches), size=int(tirages)), periode)
    return {"decidable": True, "les_phases": int(p.size),
            "la_phase_mediane_en_voxels": round(float(np.median(p)), 4),
            "lecart_type_en_voxels": round(float(np.std(p)), 4),
            "lecart_type_du_nul_en_voxels": round(float(np.std(nul)), 4),
            "le_rapport_au_nul": round(float(np.std(p)) / float(np.std(nul)), 4)}


def juger(depliage: dict, accord: dict, creux: dict, marche: dict,
          periode: float = PAS_EN_VOXELS) -> dict:
    """Le dépliage rend-il l'ordinal, et borne-t-il la marche ?

    ⚠⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE. La comparaison des excursions qui l'accompagne
    met en regard trois nombres DEJA PUBLIES — `199`, `200` et celui-ci — et n'est pas une seconde
    epreuve : en faire une diviserait la garantie sans rien mesurer de neuf.

    ⚠⚠ ET L'ORDRE COMPTE : si la phase ne se suit pas, l'excursion du dépliage n'a aucun sens a
    comparer, parce qu'elle est celle d'une marche au hasard de pas uniformes sur la demi-periode.
    """
    if not depliage.get("decidable") or not accord.get("decidable"):
        return {"decidable": False, "raison": "le dépliage ou l'épreuve manque"}
    suit = bool(accord["la_phase_se_suit"])
    a = float(depliage["lexcursion_en_plis"])
    b = creux.get("lexcursion_en_plis")
    c = marche.get("lexcursion_en_plis")
    obs = accord.get("le_pas_quadratique_observe_en_voxels")
    q199 = marche.get("le_pas_quadratique_en_voxels")
    return {"decidable": True, "la_phase_se_suit": suit,
            # ⭐⭐⭐⭐ LA COMPARAISON QUI DONNE SON SENS AU « OUI » : un creux qui SUIVRAIT une
            # frontiere rendrait le pas que `199` mesure sur la meme rangee. Le rapport des deux dit
            # de combien le lecteur reel s'en ecarte, et c'est un nombre PRODUIT, pas ecrit en prose.
            "le_pas_replie_observe_en_voxels": obs,
            "le_pas_que_199_rendrait_en_voxels": q199,
            "le_rapport_a_ce_que_199_rendrait": (round(float(obs) / float(q199), 4)
                                                 if obs and q199 else None),
            "lexcursion_depliee_en_plis": round(a, 6),
            "lexcursion_absolue_en_plis": b,
            "lexcursion_differentielle_en_plis": c,
            "le_rapport_a_labsolue": (round(a / float(b), 4) if b else None),
            "le_rapport_au_differentiel": (round(a / float(c), 4) if c else None),
            "le_depliage_rend_un_ordinal": bool(
                suit and b is not None and c is not None
                and a < float(b) and a < float(c))}


def une_trace_repliee(pas_quadratique: float, echantillons: int, bruit: float,
                      graine: int, periode: float = PAS_EN_VOXELS):
    """Une trace absolue POSÉE, sa version repliée, et le bruit de lecture — la fixture de l'étalon.

    ⚠⚠ LA TRACE EST UNE MARCHE AU HASARD ET NON UNE DROITE : une derive constante se deplie meme
    quand elle depasse la demi-periode, parce que l'erreur est la meme a chaque pas et se lit comme
    une autre pente. C'est une matiere COMPLAISANTE, et l'etalon ne separerait plus rien.
    """
    r = _rng(int(graine))
    pas = r.normal(0.0, float(pas_quadratique), size=int(echantillons) - 1)
    vraie = np.concatenate(([0.0], np.cumsum(pas)))
    lue = la_phase(vraie + r.normal(0.0, float(bruit), size=vraie.size), periode)
    return vraie, lue


def les_plis_perdus(vraie, lue, periode: float = PAS_EN_VOXELS):
    """Combien de plis le dépliage a perdus à chaque échantillon — SANS AUCUN SEUIL.

    ⭐⭐⭐⭐ CE QUI SE VERIFIE EST UN ORDINAL, DONC IL SE COMPTE PLUTOT QU'IL NE SE TOLERE. L'ecart
    entre la trace depliee et la trace posee vaut la difference des bruits de lecture — qui se
    telescope et reste bornee — plus un MULTIPLE ENTIER de la periode. Diviser par la periode et
    arrondir rend donc le nombre de plis perdus, exactement, et aucune tolerance n'est a choisir.

    ⚠⚠ LA PREMIERE VERSION COMPARAIT A UNE DEMI-PERIODE, ET UN BRIS POSE EXPRES — juger a QUATRE plis
    pres — EST RESTE VERT : aucune sonde n'epinglait la valeur, parce que toutes les matieres
    d'epreuve perdaient bien plus que quatre plis ou aucun. Compter supprime la question.
    """
    d = le_depliage(lue, periode)
    if not d.get("decidable"):
        return None
    t = np.asarray(d["la_trace_en_voxels"], dtype=float)
    v = np.asarray(vraie, dtype=float) - float(vraie[0])
    return np.round((t - v) / float(periode))


def lordinal_est_retrouve(vraie, lue, periode: float = PAS_EN_VOXELS) -> bool:
    """Le dépliage a-t-il gardé le compte des plis ? Aucun pli perdu, nulle part."""
    plis = les_plis_perdus(vraie, lue, periode)
    return bool(plis is not None and np.all(plis == 0.0))


def la_part_depliee(pas_quadratique: float, bruit: float, replicats: int, echantillons: int,
                    graine: int, periode: float = PAS_EN_VOXELS) -> dict:
    """La part des réplicats où le dépliage garde le compte des plis, à ce pas-là."""
    vus = 0
    for k in range(int(replicats)):
        vraie, lue = une_trace_repliee(pas_quadratique, echantillons, bruit,
                                       int(graine) + k, periode)
        vus += int(lordinal_est_retrouve(vraie, lue, periode))
    return {"vus": int(vus), "replicats": int(replicats),
            "la_part": float(vus) / float(replicats)}


def sur_letalon(marche: dict, creux: dict, tirages: int = PERMUTATIONS, graine: int = GRAINE,
                replicats: int = 20, echantillons: int = 60,
                periode: float = PAS_EN_VOXELS) -> dict:
    """Le dépliage tient-il, jusqu'où, et l'épreuve se tait-elle sur une phase sans ordre ?

    ⭐⭐⭐⭐ L'ECHELLE EST DERIVEE DES NOMBRES DU PRODUCTEUR, AUCUNE VALEUR N'EST TAPEE : le pas
    quadratique de `199`, ses doubles et quadruples, puis la demi-periode et la periode. Le dernier
    barreau est la ou la condition d'Itoh casse, et l'etalon DOIT y echouer — un etalon qui reussit
    partout ne separe rien.

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS. La face positive est le dépliage d'une trace posee ; la face
    negative est l'EPREUVE DECLAREE lancee sur des phases tirees independamment dans le cube, ou elle
    ne doit se declencher qu'a la garantie. Juger la negative sur un tirage unique tombe du mauvais
    cote une fois sur vingt par construction.
    """
    if not marche.get("decidable") or not creux.get("decidable"):
        return {"decidable": False, "raison": "une des deux lectures manque"}
    q = float(marche["le_pas_quadratique_en_voxels"])
    demi = float(periode) / 2.0
    bruit = q
    echelle = [q, 2.0 * q, 4.0 * q, demi, float(periode)]
    courbe, tient, casse = [], None, None
    for s in echelle:
        x = la_part_depliee(s, bruit, replicats, echantillons, graine, periode)
        courbe.append({"le_pas_pose_en_voxels": round(float(s), 4),
                       "part_des_replicats": float(x["la_part"])})
        if x["la_part"] >= 1.0:
            tient = round(float(s), 4)
        elif casse is None:
            casse = round(float(s), 4)
    couches = int(creux.get("les_couches_du_cube") or 0)
    n = int(creux.get("les_reperes") or 0)
    r = _rng(int(graine) + 7)
    faux = 0
    for k in range(int(replicats)):
        sans_ordre = la_phase(r.uniform(0.0, float(couches), size=n), periode)
        faux += int(contre_le_melange(sans_ordre, tirages, int(graine) + 100 + k,
                                      periode)["la_phase_se_suit"])
    tenue = le_taux_tient_la_garantie(faux, replicats, GARANTIE_PAR_EPREUVE)
    return {"decidable": True, "la_courbe": courbe, "le_pas_qui_tient": tient,
            "le_pas_qui_casse": casse, "le_bruit_de_lecture_en_voxels": round(bruit, 4),
            "les_echantillons": int(echantillons), "replicats": int(replicats),
            "les_faux": int(faux), "le_taux_de_faux": round(float(faux) / float(replicats), 4),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "la_probabilite_den_avoir_autant": round(
                float(tenue["la_probabilite_den_avoir_autant"]), 6),
            "letalon_separe": bool(tient is not None and casse is not None
                                   and bool(tenue["il_tient"]))}


def mesurer(tirages: int = PERMUTATIONS, graine: int = GRAINE, replicats: int = 20,
            chemin_marche: Path = CE_QUE_LA_MARCHE_A_RENDU,
            chemin_creux: Path = CE_QUE_LE_CREUX_A_RENDU) -> dict:
    """Le dépliage de la phase, sur les deux traces déjà publiées — aucun téléchargement."""
    creux = ce_que_le_creux_a_rendu(chemin_creux)
    marche = ce_que_la_marche_a_rendu(chemin_marche)
    if not creux.get("decidable"):
        return {"decidable": False, "raison": creux.get("raison"), "ce_que_200_a_rendu": creux}
    if not marche.get("decidable"):
        return {"decidable": False, "raison": marche.get("raison"), "ce_que_199_a_rendu": marche}
    if creux.get("la_rangee") != marche.get("la_rangee"):
        return {"decidable": False,
                "raison": f"deux rangées différentes : {creux.get('la_rangee')} et "
                          f"{marche.get('la_rangee')}"}
    phases = la_phase(creux["la_trace_en_couches"], PAS_EN_VOXELS)
    dep = le_depliage(phases, PAS_EN_VOXELS)
    accord = contre_le_melange(phases, tirages, graine, PAS_EN_VOXELS)
    return {
        "graine": int(graine), "tirages": int(tirages),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "ce_que_200_a_rendu": {k: v for k, v in creux.items()
                               if k not in ("la_trace_en_couches", "les_colonnes",
                                            "les_coutures_par_ecart")},
        "ce_que_199_a_rendu": marche,
        "la_condition_ditoh": la_condition_ditoh(marche, creux),
        "la_marginale": la_marginale(phases, int(creux.get("les_couches_du_cube") or 0),
                                     PAS_EN_VOXELS, 4096, graine),
        "les_colonnes": creux["les_colonnes"],
        "la_phase_en_voxels": [round(float(x), 4) for x in phases],
        "le_depliage": dep,
        "langle_mort": langle_mort(dep.get("les_pas_en_voxels") or [],
                                   float(marche["le_pas_maximal_en_voxels"]),
                                   float(marche["le_pas_quadratique_en_voxels"])),
        "laccord": accord,
        "le_verdict": juger(dep, accord, creux, marche),
        "letalon": sur_letalon(marche, creux, tirages, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"PEUT-ON DÉPLIER LA PHASE   indécidable : {r.get('raison')}")
        return
    c2, c1 = r["ce_que_200_a_rendu"], r["ce_que_199_a_rendu"]
    it, mg, dep = r["la_condition_ditoh"], r["la_marginale"], r["le_depliage"]
    am, ac, ve, e = r["langle_mort"], r["laccord"], r["le_verdict"], r["letalon"]
    print(f"PEUT-ON DÉPLIER LA PHASE   rangée {c2['la_rangee']} · {c2['les_reperes']} repères de "
          f"`200` · {c1['les_pas']} pas de `199`")
    print(f"  L'ALIGNEMENT      {c1['les_pas_sans_colonne']} pas de `199` sans colonne · cumul "
          f"indexable {c1['le_cumul_est_indexable_par_colonne']}")
    print(f"  LA CONDITION      pas max {it['le_pas_maximal_de_199_en_voxels']} vx pour une "
          f"demi-période de {it['la_demi_periode_en_voxels']} · marge "
          f"{it['la_marge_du_pas_maximal_en_voxels']} vx · "
          f"{it['les_pas_de_199_au_bord_de_lalias']} pas au bord de l'alias · réfutable "
          f"{it['la_condition_est_refutable_par_cette_mesure']}")
    print(f"                    {it['les_ecarts_certifies_au_pire']} écarts certifiés au pire et "
          f"{it['les_ecarts_certifies_au_typique']} au typique, sur {it['les_ecarts']}")
    print(f"  LA MARGINALE      écart-type {mg['lecart_type_en_voxels']} vx contre "
          f"{mg['lecart_type_du_nul_en_voxels']} si tirée dans le cube · rapport "
          f"{mg['le_rapport_au_nul']}")
    print(f"  L'ANGLE MORT      {am['les_pas_hors_enveloppe']} pas hors enveloppe "
          f"({am['lenveloppe_du_differentiel_en_voxels']} vx) · "
          f"{am['les_pas_au_bord_de_lalias']} au bord de l'alias · marge médiane "
          f"{am['la_marge_mediane_en_voxels']} vx")
    print(f"  L'ÉPREUVE         pas quadratique replié {ac['le_pas_quadratique_observe_en_voxels']}"
          f" vx contre {ac['le_pas_quadratique_median_du_nul_en_voxels']} au mélange "
          f"(rapport {ac['le_rapport_au_nul']}) · "
          f"{ac['les_melanges_au_moins_aussi_serres']}/{ac['tirages']} · P = {ac['la_valeur_p']} "
          f"· suit {ac['la_phase_se_suit']}")
    print(f"                    contre {ve['le_pas_que_199_rendrait_en_voxels']} vx si le creux "
          f"suivait une frontière, soit {ve['le_rapport_a_ce_que_199_rendrait']} fois")
    print(f"  LE DÉPLIAGE       excursion {dep['lexcursion_en_plis']} pli · net "
          f"{dep['le_deplacement_net_en_plis']} pli · pas quadratique "
          f"{dep['le_pas_quadratique_en_voxels']} vx")
    print(f"  LE VERDICT        dépliée {ve['lexcursion_depliee_en_plis']} contre absolue "
          f"{ve['lexcursion_absolue_en_plis']} et différentielle "
          f"{ve['lexcursion_differentielle_en_plis']} · ordinal "
          f"{ve['le_depliage_rend_un_ordinal']}")
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · tient jusqu'à "
          f"{e['le_pas_qui_tient']} vx · casse à {e['le_pas_qui_casse']} vx · taux de faux "
          f"{e['le_taux_de_faux']} pour {e['la_garantie']} garantis")
    print("                    courbe " + " · ".join(
        f"{x['le_pas_pose_en_voxels']:g}→{x['part_des_replicats']:g}" for x in e["la_courbe"]))


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
      and abs(GARANTIE_PAR_EPREUVE - 1.0 / (PERMUTATIONS + 1)) < 1e-12,
      f"{len(LES_EPREUVES_DECLAREES)} épreuves, garantie {GARANTIE_PAR_EPREUVE}")
    v("★★ la période est RELUE du producteur, jamais tapée",
      abs(PAS_EN_VOXELS - 173.0 / 2.4) < 1e-9, str(PAS_EN_VOXELS))

    # ⚠⚠ LE REPLI EST L'OPERATION CENTRALE : son intervalle est verifie AUX DEUX BORDS.
    p = float(PAS_EN_VOXELS)
    v("★★★ le repli laisse un petit écart intact", abs(float(le_repli(3.0, p)) - 3.0) < 1e-9)
    v("★★★ un écart d'un pli exact se replie à zéro", abs(float(le_repli(p, p))) < 1e-9)
    v("★★★ un écart de trois plis aussi", abs(float(le_repli(3.0 * p, p))) < 1e-9)
    v("★★★★ le repli est demi-ouvert À GAUCHE, aux deux bords",
      abs(float(le_repli(p / 2.0, p)) + p / 2.0) < 1e-9
      and abs(float(le_repli(-p / 2.0, p)) + p / 2.0) < 1e-9,
      f"{float(le_repli(p / 2.0, p)):.4f} et {float(le_repli(-p / 2.0, p)):.4f}")
    r_ = le_repli(np.array([-5.0 * p - 7.0, 5.0 * p + 7.0]), p)
    v("★★★ et il ramène dans la demi-période quel que soit le nombre de plis",
      abs(float(r_[0]) + 7.0) < 1e-9 and abs(float(r_[1]) - 7.0) < 1e-9, str(r_))

    # ⚠⚠⚠ LA PHASE RAMENE LES DEUX REPLIQUES L'UNE SUR L'AUTRE — C'EST TOUT L'OBJET DE `200`→`201`.
    v("★★★★ deux couches séparées d'un pli exact rendent la MÊME phase",
      abs(float(la_phase(np.array([10.0]), p)[0])
          - float(la_phase(np.array([10.0 + p]), p)[0])) < 1e-9)
    v("★★★ la phase reste dans le pli", bool(np.all(
        (la_phase(np.arange(0.0, 109.0), p) >= 0.0)
        & (la_phase(np.arange(0.0, 109.0), p) < p))))
    v("★★★★ et une couche au-delà d'un pli N'EST PAS sa propre phase",
      abs(float(la_phase(np.array([100.0]), p)[0]) - 100.0) > 1.0,
      str(round(float(la_phase(np.array([100.0]), p)[0]), 3)))

    # ⭐⭐⭐⭐ LE DEPLIAGE RECONSTRUIT UNE TRACE POSEE — ET IL ECHOUE LA OU ITOH LE DIT.
    vraie = np.cumsum(np.concatenate(([0.0], np.full(40, 5.0))))
    d = le_depliage(la_phase(vraie, p), p)
    v("★★★★ une dérive de cinq voxels par pas se déplie EXACTEMENT sur quarante pas",
      d["decidable"] and max(abs(a - b) for a, b in
                             zip(d["la_trace_en_voxels"], vraie)) < 1e-6,
      str(d.get("la_trace_en_voxels", [])[-1]))
    v("★★★ et la trace dépliée porte un point de plus que ses pas",
      len(d["la_trace_en_voxels"]) == d["les_pas"] + 1)
    grosse = np.cumsum(np.concatenate(([0.0], np.full(6, p / 2.0 + 5.0))))
    dg = le_depliage(la_phase(grosse, p), p)
    lu = np.asarray(dg["les_pas_en_voxels"], dtype=float)
    v("★★★★ UN PAS AU-DELÀ DE LA DEMI-PÉRIODE ALIASE : il revient du signe opposé",
      bool(np.all(lu < 0.0)), str(lu[:3]))
    # ⚠⚠ LA COMPARAISON SE FAIT SUR LA VALEUR ARRONDIE COMME ELLE EST PUBLIEE : comparer l'attendu
    # non arrondi au pas publie a QUATRE decimales faisait echouer cette sonde de trois centiemes de
    # millieme, ce qui n'est pas un defaut du dépliage mais du test. Piege deja paye ailleurs.
    v("★★★★ et l'alias vaut exactement le pas vrai MOINS un pli, jamais une saturation",
      abs(float(lu[0]) - round((p / 2.0 + 5.0) - p, 4)) < 1e-9, str(float(lu[0])))
    v("★★★★ donc l'ordinal est PERDU au-delà de la demi-période",
      not lordinal_est_retrouve(grosse, la_phase(grosse, p), p))
    # ⚠⚠⚠ LA MATIERE QUI DISCRIMINE : UN SEUL pli perdu, et rien d'autre. Une trace qui en perd six
    # est rejetee par n'importe quelle tolerance, donc elle ne dit rien du critere ; celle-ci est
    # rejetee par le compte exact et acceptee par toute tolerance plus large qu'un pli.
    dun_seul = np.cumsum(np.array([0.0, 3.0, 3.0, p / 2.0 + 2.0, 3.0, 3.0]))
    perdus = les_plis_perdus(dun_seul, la_phase(dun_seul, p), p)
    v("★★★★ une trace qui ne perd QU'UN pli le dit, et l'ordinal est refusé",
      perdus is not None and float(np.max(np.abs(perdus))) == 1.0
      and not lordinal_est_retrouve(dun_seul, la_phase(dun_seul, p), p),
      str(None if perdus is None else list(perdus)))
    v("★★★★ et le pli n'est perdu qu'À PARTIR du pas qui alias, pas avant",
      perdus is not None and list(perdus[:3]) == [0.0, 0.0, 0.0]
      and list(perdus[3:]) == [-1.0, -1.0, -1.0],
      str(None if perdus is None else list(perdus)))
    v("★★★ une trace posée sans bruit ne perd aucun pli",
      float(np.max(np.abs(les_plis_perdus(vraie, la_phase(vraie, p), p)))) == 0.0)
    v("★★★★ et il est retrouvé en deçà",
      lordinal_est_retrouve(vraie, la_phase(vraie, p), p))
    v("★★ un dépliage de moins de deux phases est indécidable",
      not le_depliage(np.array([3.0]), p).get("decidable"))

    # ⚠⚠⚠ LE NUL PAR MELANGE MORD ICI, CONTRAIREMENT AU DEPLACEMENT NET DE `199`.
    suivie = la_phase(np.cumsum(np.concatenate(([0.0], np.full(80, 3.0)))), p)
    melangee = _rng(5).permutation(suivie)
    v("★★★★ mélanger les MÊMES phases change la statistique, donc le nul n'est pas vide",
      abs(la_statistique(suivie, p) - la_statistique(melangee, p)) > 1.0,
      f"{la_statistique(suivie, p):.3f} contre {la_statistique(melangee, p):.3f}")
    v("★★★★ et une phase qui se suit rend un pas replié BIEN plus serré qu'un mélange",
      la_statistique(suivie, p) < la_statistique(melangee, p) / 3.0)
    # ⚠⚠⚠ LA STATISTIQUE S'APPELLE « QUADRATIQUE » ET ELLE DOIT L'ETRE : un bris qui la remplacait
    # par une moyenne absolue est reste VERT, parce que les deux separent aussi bien. Le nombre
    # publie aurait alors ete juste sous un mauvais nom, ce qui est pire qu'un nombre absent.
    v("★★★★ la statistique est QUADRATIQUE, et non une moyenne absolue",
      abs(la_statistique(np.array([0.0, 3.0, 7.0]), p) - (12.5 ** 0.5)) < 1e-9,
      f"{la_statistique(np.array([0.0, 3.0, 7.0]), p):.6f} au lieu de {12.5 ** 0.5:.6f}")
    # ⚠⚠⚠ UN « OUI » AU PLANCHER DES TIRAGES N'EST PAS UN « OUI » FORT, ET LE RAPPORT LE DIT.
    v("★★★★ le rapport au nul est publié, et il vaut moins de un quand la phase se suit",
      0.0 < contre_le_melange(suivie, 19, 3, p)["le_rapport_au_nul"] < 0.5,
      str(contre_le_melange(suivie, 19, 3, p)["le_rapport_au_nul"]))
    a_suivie = contre_le_melange(suivie, 19, 3, p)
    v("★★★★ l'épreuve se déclenche sur une phase qui se suit",
      a_suivie["la_phase_se_suit"] and a_suivie["les_melanges_au_moins_aussi_serres"] == 0,
      f"P = {a_suivie['la_valeur_p']}")
    sans = la_phase(_rng(6).uniform(0.0, 109.0, size=80), p)
    v("★★★★ et elle se tait sur une phase tirée au hasard dans le cube",
      not contre_le_melange(sans, 19, 3, p)["la_phase_se_suit"])
    v("★★★ et le rapport au nul approche un quand la phase ne se suit pas",
      contre_le_melange(sans, 19, 3, p)["le_rapport_au_nul"] > 0.8,
      str(contre_le_melange(sans, 19, 3, p)["le_rapport_au_nul"]))
    v("★★★ la marginale, elle, est INVARIANTE par mélange — donc elle ne se teste pas ainsi",
      abs(la_marginale(suivie, 109, p, 512, 3)["lecart_type_en_voxels"]
          - la_marginale(melangee, 109, p, 512, 3)["lecart_type_en_voxels"]) < 1e-9)
    v("★★★ et son nul charge deux fois la première demi-période, donc il n'est PAS uniforme",
      la_marginale(sans, 109, p, 8192, 3)["lecart_type_du_nul_en_voxels"] < p / (12.0 ** 0.5),
      f"{la_marginale(sans, 109, p, 8192, 3)['lecart_type_du_nul_en_voxels']} contre "
      f"{round(p / (12.0 ** 0.5), 4)}")

    # ⚠⚠⚠ L'ANGLE MORT SE COMPTE SUR DES SEUILS DU PRODUCTEUR, ET IL COMPTE VRAIMENT.
    am = langle_mort([1.0, 2.0, 40.0, -35.5], enveloppe=35.0, pas_quadratique=5.0,
                     demi_periode=36.0)
    v("★★★★ un pas plus grand que tout ce que `199` a lu est compté hors enveloppe",
      am["les_pas_hors_enveloppe"] == 2, str(am["les_pas_hors_enveloppe"]))
    v("★★★★ et un pas dont il reste moins qu'un pas quadratique avant l'alias est compté au bord",
      am["les_pas_au_bord_de_lalias"] == 2, str(am["les_pas_au_bord_de_lalias"]))
    v("★★★ la marge médiane est celle des pas, pas une constante",
      abs(am["la_marge_mediane_en_voxels"] - 17.25) < 1e-6,
      str(am["la_marge_mediane_en_voxels"]))
    v("★★ un angle mort sans pas est indécidable", not langle_mort([], 1.0, 1.0)["decidable"])

    # ⚠⚠⚠ LES DEUX LECTURES SONT RELUES, ET LEURS REFUS SONT REELS.
    v("★★★ `200` absent est refusé, jamais deviné",
      not ce_que_le_creux_a_rendu(RACINE / "docs" / "mesures" / "absent.json")["decidable"])
    v("★★★ `199` absent est refusé, jamais deviné",
      not ce_que_la_marche_a_rendu(RACINE / "docs" / "mesures" / "absent.json")["decidable"])
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "c.json"
        base = {"la_ligne": {"la_rangee": 198},
                "la_trace_absolue": {"decidable": True, "les_couches_du_cube": 109,
                                     "les_colonnes": [1, 2, 3, 7, 8],
                                     "la_trace_en_couches": [4, 5, 6, 7, 8]},
                "letalon": {"letalon_separe": True}}
        f.write_text(json.dumps(base), encoding="utf-8")
        lu2 = ce_que_le_creux_a_rendu(f)
        v("★★★★ les coutures sont DÉRIVÉES des colonnes, pas lues dans une clef",
          lu2["les_coutures_par_ecart"] == [1, 1, 4, 1]
          and lu2["la_plus_longue_couture"] == 4
          and lu2["les_ecarts_sur_une_seule_couture"] == 3,
          str(lu2.get("les_coutures_par_ecart")))
        base["letalon"]["letalon_separe"] = False
        f.write_text(json.dumps(base), encoding="utf-8")
        v("★★★★ et une mesure dont l'étalon NE SÉPARE PAS est refusée",
          not ce_que_le_creux_a_rendu(f)["decidable"])
        base["letalon"]["letalon_separe"] = True
        base["la_trace_absolue"]["la_trace_en_couches"] = [4, 5]
        f.write_text(json.dumps(base), encoding="utf-8")
        v("★★★ des colonnes et des couches qui ne s'apparient pas sont refusées",
          not ce_que_le_creux_a_rendu(f)["decidable"])

        g = Path(tmp) / "m.json"
        marche = {"la_ligne": {"la_rangee": 198},
                  "la_marche": {"decidable": True, "les_pas": 3,
                                "les_pas_en_voxels": [1, -9, 4],
                                "le_pas_quadratique_en_voxels": 5.0,
                                "les_pas_qui_saturent": 0,
                                "lexcursion_maximale_en_plis": 1.3,
                                "les_troncons": [{"chunks": 6, "pas": 3}]}}
        g.write_text(json.dumps(marche), encoding="utf-8")
        lu1 = ce_que_la_marche_a_rendu(g)
        v("★★★★ le pas MAXIMAL est dérivé des pas publiés, pas lu dans une clef",
          abs(lu1["le_pas_maximal_en_voxels"] - 9.0) < 1e-9,
          str(lu1["le_pas_maximal_en_voxels"]))
        # ⚠⚠⚠ LA DISPOSITION DU PRODUCTEUR EST EXERCEE TELLE QU'ELLE EST : `199` hisse ses pas a la
        # RACINE. Une fixture qui ne les met que dans `la_marche` teste la fixture.
        racine = {"la_ligne": {"la_rangee": 198},
                  "les_pas_en_voxels": [1, -9, 4],
                  "la_marche": {k: x for k, x in marche["la_marche"].items()
                                if k != "les_pas_en_voxels"}}
        g.write_text(json.dumps(racine), encoding="utf-8")
        v("★★★★ et il se lit AUSSI quand `199` les hisse à la racine, comme il le fait vraiment",
          abs(ce_que_la_marche_a_rendu(g)["le_pas_maximal_en_voxels"] - 9.0) < 1e-9,
          str(ce_que_la_marche_a_rendu(g).get("le_pas_maximal_en_voxels")))
        g.write_text(json.dumps(marche), encoding="utf-8")
        v("★★★★ et les pas SANS COLONNE sont comptés : six chunks portent cinq intervalles",
          lu1["les_pas_sans_colonne"] == 2
          and not lu1["le_cumul_est_indexable_par_colonne"],
          str(lu1["les_pas_sans_colonne"]))
        marche["la_marche"]["les_troncons"] = [{"chunks": 4, "pas": 3}]
        g.write_text(json.dumps(marche), encoding="utf-8")
        v("★★★★ un tronçon complet rend un cumul indexable par colonne",
          ce_que_la_marche_a_rendu(g)["le_cumul_est_indexable_par_colonne"])

        # ⚠⚠ LA CONDITION D'ITOH DISTINGUE LE PIRE CAS DU CAS TYPIQUE, ET LES DEUX COMPTENT.
        it = la_condition_ditoh(ce_que_la_marche_a_rendu(g), lu2, demi_periode=36.0)
        v("★★★★ aucun pas lu ne dépasse la demi-période, et c'est tout ce qui se lit",
          it["aucun_pas_lu_ne_depasse_la_demi_periode"])
        v("★★★★ mais la condition d'Itoh n'est PAS réfutable par cette mesure, et le dit",
          it["la_condition_est_refutable_par_cette_mesure"] is False)
        v("★★★★ la marge du pas maximal est dérivée, et un pas au bord de l'alias est compté",
          abs(float(it["la_marge_du_pas_maximal_en_voxels"]) - 27.0) < 1e-9
          and int(it["les_pas_de_199_au_bord_de_lalias"]) == 0,
          f"marge {it['la_marge_du_pas_maximal_en_voxels']} · bord "
          f"{it['les_pas_de_199_au_bord_de_lalias']}")
        marche_bord = {"la_ligne": {"la_rangee": 198},
                       "la_marche": {"decidable": True, "les_pas": 3,
                                     "les_pas_en_voxels": [1, -35, 4],
                                     "le_pas_quadratique_en_voxels": 5.0,
                                     "les_troncons": [{"chunks": 4, "pas": 3}]}}
        g.write_text(json.dumps(marche_bord), encoding="utf-8")
        lu_bord = ce_que_la_marche_a_rendu(g)
        v("★★★★ un pas à un voxel de la limite est compté au bord de l'alias",
          lu_bord["les_pas_au_bord_de_lalias"] == 1
          and abs(lu_bord["la_marge_du_pas_maximal_en_voxels"] - 1.0) < 1e-9,
          f"{lu_bord['les_pas_au_bord_de_lalias']} · marge "
          f"{lu_bord['la_marge_du_pas_maximal_en_voxels']}")
        g.write_text(json.dumps(marche), encoding="utf-8")
        v("★★★★ un écart qui enjambe quatre coutures n'est PAS certifié au pire cas",
          it["les_ecarts_certifies_au_pire"] == 3 and it["les_ecarts"] == 4,
          f"{it['les_ecarts_certifies_au_pire']} sur {it['les_ecarts']}")
        v("★★★★ mais il l'est au cas typique, et publier le seul typique flatterait le résultat",
          it["les_ecarts_certifies_au_typique"] == 4,
          str(it["les_ecarts_certifies_au_typique"]))

    # ⭐⭐⭐⭐ L'ETALON SEPARE, ET IL CASSE LA OU LE THEOREME DIT QU'IL DOIT CASSER.
    fx_m = {"decidable": True, "le_pas_quadratique_en_voxels": 5.0,
            "le_pas_maximal_en_voxels": 35.0}
    fx_c = {"decidable": True, "les_couches_du_cube": 109, "les_reperes": 40}
    et = sur_letalon(fx_m, fx_c, 19, 21, replicats=12, echantillons=40)
    v("★★★★ l'étalon tient au pas quadratique de `199` et CASSE à la période",
      et["decidable"] and et["le_pas_qui_tient"] is not None
      and et["le_pas_qui_casse"] is not None
      and float(et["le_pas_qui_casse"]) > float(et["le_pas_qui_tient"]),
      f"tient {et.get('le_pas_qui_tient')} casse {et.get('le_pas_qui_casse')}")
    v("★★★★ sa courbe décroît quand le pas posé grandit",
      all(a["part_des_replicats"] >= b["part_des_replicats"] - 1e-12
          for a, b in zip(et["la_courbe"], et["la_courbe"][1:])),
      str([x["part_des_replicats"] for x in et["la_courbe"]]))
    v("★★★★ son échelle est DÉRIVÉE du pas quadratique de `199`, aucune valeur n'est tapée",
      abs(et["la_courbe"][0]["le_pas_pose_en_voxels"] - 5.0) < 1e-9
      and abs(et["la_courbe"][1]["le_pas_pose_en_voxels"] - 10.0) < 1e-9
      and abs(et["la_courbe"][-1]["le_pas_pose_en_voxels"] - PAS_EN_VOXELS) < 1e-3,
      str([x["le_pas_pose_en_voxels"] for x in et["la_courbe"]]))
    v("★★★★ et son taux de faux est COMPATIBLE avec la garantie, jamais simplement inférieur",
      et["letalon_separe"] and et["les_faux"] <= 2,
      f"{et['les_faux']} faux, P = {et['la_probabilite_den_avoir_autant']}")

    # ⚠⚠ LA FIXTURE DE L'ETALON EST UNE MARCHE AU HASARD, ET UNE DERIVE CONSTANTE EST COMPLAISANTE.
    droite = np.cumsum(np.concatenate(([0.0], np.full(30, p / 2.0 + 6.0))))
    v("★★★★ une dérive CONSTANTE au-delà de la demi-période se déplie quand même, mais FAUX",
      not lordinal_est_retrouve(droite, la_phase(droite, p), p)
      and abs(float(np.std(np.asarray(le_depliage(la_phase(droite, p), p)
                                      ["les_pas_en_voxels"], dtype=float)))) < 1e-6,
      "les pas aliasés sont tous identiques, donc la trace fausse est parfaitement lisse")

    # ⚠⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE.
    faux_dep = {"decidable": True, "lexcursion_en_plis": 0.1}
    v("★★★★ un dépliage étroit dont la phase NE SE SUIT PAS ne rend aucun ordinal",
      not juger(faux_dep, {"decidable": True, "la_phase_se_suit": False},
                {"lexcursion_en_plis": 1.4}, {"lexcursion_en_plis": 1.3})
      ["le_depliage_rend_un_ordinal"])
    v("★★★★ et une phase qui se suit ne suffit pas si l'excursion ne borne pas",
      not juger({"decidable": True, "lexcursion_en_plis": 9.0},
                {"decidable": True, "la_phase_se_suit": True},
                {"lexcursion_en_plis": 1.4}, {"lexcursion_en_plis": 1.3})
      ["le_depliage_rend_un_ordinal"])
    j_ = juger({"decidable": True, "lexcursion_en_plis": 0.1},
               {"decidable": True, "la_phase_se_suit": True,
                "le_pas_quadratique_observe_en_voxels": 20.0},
               {"lexcursion_en_plis": 1.4},
               {"lexcursion_en_plis": 1.3, "le_pas_quadratique_en_voxels": 5.0})
    v("★★★★ le rapport à ce que `199` rendrait est DÉRIVÉ des deux producteurs",
      abs(float(j_["le_rapport_a_ce_que_199_rendrait"]) - 4.0) < 1e-9,
      str(j_["le_rapport_a_ce_que_199_rendrait"]))
    v("★★★ et il manque plutôt que de valoir zéro quand un des deux manque",
      juger({"decidable": True, "lexcursion_en_plis": 0.1},
            {"decidable": True, "la_phase_se_suit": True},
            {"lexcursion_en_plis": 1.4}, {"lexcursion_en_plis": 1.3})
      ["le_rapport_a_ce_que_199_rendrait"] is None)
    v("★★★★ les deux ensemble rendent l'ordinal",
      juger(faux_dep, {"decidable": True, "la_phase_se_suit": True},
            {"lexcursion_en_plis": 1.4}, {"lexcursion_en_plis": 1.3})
      ["le_depliage_rend_un_ordinal"])

    # ⚠⚠ DEUX RANGEES DIFFERENTES NE SE JOIGNENT PAS.
    with tempfile.TemporaryDirectory() as tmp:
        fc, fm = Path(tmp) / "c.json", Path(tmp) / "m.json"
        fc.write_text(json.dumps({"la_ligne": {"la_rangee": 198},
                                  "la_trace_absolue": {
                                      "decidable": True, "les_couches_du_cube": 109,
                                      "les_colonnes": [1, 2, 3, 4],
                                      "la_trace_en_couches": [4, 5, 6, 7]},
                                  "letalon": {"letalon_separe": True}}), encoding="utf-8")
        fm.write_text(json.dumps({"la_ligne": {"la_rangee": 12},
                                  "la_marche": {"decidable": True, "les_pas": 3,
                                                "les_pas_en_voxels": [1, -2, 3],
                                                "le_pas_quadratique_en_voxels": 5.0,
                                                "les_troncons": [{"chunks": 4, "pas": 3}]}}),
                     encoding="utf-8")
        v("★★★★ deux rangées différentes sont refusées, jamais jointes",
          not mesurer(19, 3, 4, fm, fc).get("decidable"))

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
    ap.add_argument("--tirages", type=int, default=PERMUTATIONS)
    ap.add_argument("--graine", type=int, default=GRAINE)
    ap.add_argument("--replicats", type=int, default=20)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.tirages, a.graine, a.replicats)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
