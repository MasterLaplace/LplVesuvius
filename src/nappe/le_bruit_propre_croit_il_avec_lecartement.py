"""Le bruit propre d'une rangée croît-il avec l'écartement à sa voisine ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `212` QUI LE FORCE EN NOMMANT SA PROPRE CONDITION. `212` a
donné à la nappe son équation de conception et en a tiré que la HAUTEUR est gratuite : sous le
modèle de `208`, le pas d'une rangée se décompose en une dérive PARTAGÉE et un bruit PROPRE, et un
bruit propre ne connaît pas la distance — donc seules les deux rangées extrêmes d'une bande coûtent
quelque chose, et trois cent quatre-vingt-seize rangées coûtent autant que deux. ⚠⚠⚠ C'EST UNE
CONCLUSION TROP BELLE POSÉE SUR UNE PROPRIÉTÉ QUE PERSONNE N'A MESURÉE : toute la chaîne `208`–`212`
n'a jamais lu que des rangées VOISINES, écartées d'un cran, et un bruit qui croîtrait avec la
distance y serait rigoureusement invisible.

⚠⚠⚠ LA PRÉDICTION EST POSÉE AVANT LA MESURE, ET C'EST CE QUI REND LA TRANCHE FALSIFIABLE. Sous le
modèle, le désaccord par couture de deux rangées vaut la racine de la somme des carrés de leurs deux
bruits propres — donc il ne dépend QUE de l'identité des deux rangées, et pas du tout de leur
écartement sur le treillis. Il doit rester PLAT en fonction de la distance. S'il croît, le bruit
n'est pas propre : c'est un champ qui se décorrèle, la nappe a une largeur ET une hauteur tenables,
et le recto se découpe en dalles au lieu de se lire d'un bloc.

⭐⭐ ET LE TREILLIS OFFRE L'ÉCHELLE GRATUITEMENT, SANS QU'AUCUN ÉCARTEMENT NE SOIT CHOISI. La porte
nommait quatre, huit et seize rangées d'intervalle ; les lire DES DEUX CÔTÉS de la médiane n'est pas
un luxe mais le précédent de `208` — n'en lire qu'un côté serait un choix — et les paires que les
neuf rangées portent couvrent alors des écartements de un à trente-deux, tous DÉRIVÉS du jeu lu.

⚠⚠ LE PIÈGE EST CELUI DE `211`, EN PIRE, ET IL SE PUBLIE AU LIEU DE S'ENCAISSER. Deux rangées
éloignées partagent moins de trous, donc leur tronçon commun raccourcit et leur désaccord est estimé
sur moins de coutures. La LONGUEUR se publie donc à côté du désaccord, et la corrélation de la
longueur à l'écartement est portée comme CONTRÔLE NOMMÉ : si elle est forte, une tendance du
désaccord peut n'être qu'une tendance de la longueur.

⭐⭐⭐⭐ ET LE TRIANGLE DE `212` DEVIENT ENFIN RÉFUTABLE. À trois rangées il portait trois équations
pour trois inconnues : exactement déterminé, donc incapable de contredire quoi que ce soit hormis par
une variance négative. À neuf rangées il en porte trente-six pour neuf, et le modèle n'a plus nulle
part où se cacher — ses résidus d'ajustement sont nuls sous le modèle, aux erreurs d'échantillonnage
près, et l'écart se lit sans qu'aucun seuil ne soit choisi.

Usage :
    uv run python src/nappe/le_bruit_propre_croit_il_avec_lecartement.py --verifier
    uv run python src/nappe/le_bruit_propre_croit_il_avec_lecartement.py \\
        --json docs/mesures/le_bruit_propre_croit_il_avec_lecartement.json
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
from la_derive_saccumule_t_elle import la_ligne_declaree  # noqa: E402
from la_moyenne_des_rangees_traverse_t_elle import les_replicats_du_refus  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from les_rangees_saccordent_elles_entre_elles import le_desaccord_des_cumuls  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)
from une_rangee_voisine_lit_elle_le_meme_pas import les_pas_dune_rangee  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_VOISINE_A_RENDU = MESURES / "une_rangee_voisine_lit_elle_le_meme_pas.json"
CE_QUE_LACCORD_A_RENDU = MESURES / "les_rangees_saccordent_elles_entre_elles.json"
CE_QUE_LE_BUDGET_A_RENDU = MESURES / "le_budget_de_la_nappe.json"
GRAINE = 20261026
LES_RANGEES = 16
LES_ECARTEMENTS = (1, 4, 8, 16)
"""Les écartements que la porte nomme, lus DES DEUX CÔTÉS de la médiane.

⚠⚠ N'EN LIRE QU'UN CÔTÉ SERAIT UN CHOIX, et c'est le précédent de `208` : au-dessus et au-dessous
doivent se comporter pareil vis-à-vis de la médiane, et une asymétrie serait un fait et non un
bruit. Les écartements RÉELLEMENT couverts ne sont pas ceux-ci mais tous ceux que les paires de
rangées portent — ils se dérivent du jeu lu, ils ne se tapent pas."""

LA_QUESTION_DECLAREE = ("le désaccord par couture de deux rangées croît-il avec leur écartement sur "
                        "le treillis, ou ne dépend-il que de l'identité des deux rangées ?")
LES_EPREUVES_DECLAREES = ("le désaccord par couture croît-il avec l'écartement",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def ce_que_laccord_a_rendu(chemin: Path = CE_QUE_LACCORD_A_RENDU) -> dict:
    """Le désaccord par couture que `211` a publié à l'écartement UN — relu, jamais retapé.

    ⚠⚠⚠ C'EST LE NIVEAU QUE LA PRÉDICTION ANNONCE PLAT, donc il ne peut pas être une constante
    écrite ici : un nombre tapé deux fois est un nombre qui peut se contredire, et celui-ci porte
    tout l'énoncé de la tranche. Il vient du producteur qui l'a mesuré.
    """
    p = Path(chemin)
    if not p.exists():
        return {"decidable": False, "raison": f"{p.name} est absent — `211` n'a pas couru"}
    try:
        d = json.loads(p.read_text())
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "raison": f"{p.name} illisible : {type(e).__name__}"}
    paire = d.get("la_paire_declaree")
    valeurs = (d.get("ce_que_les_desaccords_valent") or {})
    cle = f"{paire[0]}-{paire[1]}" if paire and len(paire) == 2 else None
    v = valeurs.get(cle) or {}
    sigma = v.get("le_desaccord_par_couture_mesure_en_voxels")
    if sigma is None:
        return {"decidable": False,
                "raison": f"`211` ne publie pas le désaccord de sa paire déclarée {paire}"}
    return {"decidable": True, "la_paire_de_211": [int(paire[0]), int(paire[1])],
            "lecartement_de_211": abs(int(paire[0]) - int(paire[1])),
            "le_desaccord_par_couture_en_voxels": float(sigma),
            "les_coutures_de_211": v.get("les_coutures_communes")}


def ce_que_la_voisine_a_rendu(chemin: Path = CE_QUE_LA_VOISINE_A_RENDU) -> dict:
    """La décomposition de `208` — la dérive partagée et les bruits propres, relus."""
    p = Path(chemin)
    if not p.exists():
        return {"decidable": False, "raison": f"{p.name} est absent"}
    try:
        d = json.loads(p.read_text())
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "raison": f"{p.name} illisible : {type(e).__name__}"}
    # ⚠⚠⚠ `208` RANGE SA DECOMPOSITION SOUS `le_verdict`, PAS A LA RACINE. Premiere version : ce
    # lecteur lisait la racine, n'y trouvait rien, et rendait quand meme « decidable ». Une sonde
    # SATISFAITE PAR L'ABSENCE — le champ existait, valait None, et l'etalon retombait en silence
    # sur un nombre tape. Il lit desormais la ou `208` ecrit, et REFUSE quand la derive manque.
    v = d.get("le_verdict") or {}
    derive = v.get("la_derive_partagee_en_voxels")
    if derive is None:
        return {"decidable": False,
                "raison": f"{p.name} ne publie pas de dérive partagée sous `le_verdict`"}
    return {"decidable": True,
            "la_derive_partagee_en_voxels": derive,
            "le_bruit_de_la_mediane_en_voxels": v.get("le_bruit_de_la_mediane_en_voxels"),
            "le_bruit_de_la_voisine_en_voxels": v.get("le_bruit_de_la_voisine_en_voxels")}


def les_bruits_propres_mesures(chemin: Path = CE_QUE_LE_BUDGET_A_RENDU) -> dict:
    """Les bruits propres que le triangle de `212` a rendus — relus, jamais inventés.

    ⭐⭐⭐⭐ ILS SONT CE QUI REND L'ÉTALON FIDÈLE, ET LA SONDE L'A PROUVÉ EN LE CASSANT. Une fixture
    dont toutes les rangées portent le MÊME bruit propre donne une épreuve bien plus puissante
    qu'elle ne l'est sur la vraie matière : `212` mesure des variances propres de **2,3394** à
    **6,5374** voxels carrés, donc un désaccord qui varie d'une paire à l'autre SANS qu'aucune
    distance n'y soit pour rien. C'est exactement le bruit de fond contre lequel une tendance doit
    ressortir, et le poser au hasard reviendrait à choisir la difficulté de son propre examen.

    ⚠ Les rangées de `212` ne sont pas celles d'ici : ce qui est repris est le JEU des bruits
    propres, pas leur affectation. Les affecter par nom supposerait que la rangée 198 de `212` est
    la rangée 198 d'un étalon fabriqué, ce qui n'a aucun sens.
    """
    q = Path(chemin)
    if not q.exists():
        return {"decidable": False, "raison": f"{q.name} est absent — `212` n'a pas couru"}
    try:
        d = json.loads(q.read_text())
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "raison": f"{q.name} illisible : {type(e).__name__}"}
    tri = ((d.get("le_triangle") or {}).get("les_bruits_propres") or {})
    vals = [float(x["le_bruit_propre_en_voxels"]) for x in tri.values()
            if isinstance(x, dict) and x.get("le_bruit_propre_en_voxels") is not None]
    if len(vals) < 2:
        return {"decidable": False, "raison": "`212` ne publie pas deux bruits propres"}
    return {"decidable": True, "les_bruits_propres_en_voxels": [round(float(x), 4)
                                                                for x in sorted(vals)],
            "combien": len(vals),
            "le_plus_petit_en_voxels": round(float(min(vals)), 4),
            "le_plus_grand_en_voxels": round(float(max(vals)), 4)}


def les_rangees_ecartees(gy: int, ecartements=LES_ECARTEMENTS) -> dict:
    """La médiane et ses voisines aux écartements déclarés, des deux côtés — aucune n'est choisie.

    ⚠ La médiane vient de `la_ligne_declaree`, jamais retapée : c'est la même rangée que `208`,
    `210` et `211` ont lue, donc l'écartement UN de cette tranche RECOUPE celui de `211` au lieu de
    porter sur une autre matière.

    ⚠⚠ UN ÉCARTEMENT QUI SORT DU TREILLIS EST ÉCARTÉ ET COMPTÉ, jamais replié sur le bord. Le
    replier collerait deux écartements différents sur la même rangée, donc mettrait deux points de
    l'échelle au même endroit sous deux noms.
    """
    m = int(la_ligne_declaree(int(gy)))
    tenus, perdus = [], []
    for e in sorted(set(int(x) for x in ecartements)):
        if e <= 0:
            perdus.append({"lecartement": int(e), "raison": "un écartement nul n'est pas une paire"})
            continue
        cotes = [x for x in (m - e, m + e) if 0 <= x < int(gy)]
        if not cotes:
            perdus.append({"lecartement": int(e),
                           "raison": f"un treillis de {int(gy)} rangées ne porte pas ±{e}"})
            continue
        tenus.append({"lecartement": int(e), "les_cotes": [int(x) for x in cotes]})
    rangees = sorted({m} | {int(x) for t in tenus for x in t["les_cotes"]})
    if len(rangees) < 3:
        return {"decidable": False,
                "raison": f"un treillis de {int(gy)} rangées n'offre pas trois rangées écartées"}
    return {"decidable": True, "la_mediane": m,
            "les_ecartements_declares": [int(x) for x in ecartements],
            "les_ecartements_tenus": tenus, "les_ecartements_perdus": perdus,
            "les_rangees": [int(x) for x in rangees], "combien_de_rangees": len(rangees)}


def les_paires_du_treillis(rangees) -> dict:
    """Toutes les paires du jeu lu et leur écartement — DÉRIVÉS, jamais choisis.

    ⭐⭐ C'EST CE QUI DONNE L'ÉCHELLE GRATUITEMENT : neuf rangées posées à ±1, ±4, ±8 et ±16 de la
    médiane portent bien plus que ces quatre écartements — la paire des deux extrêmes en vaut
    trente-deux, celle de +4 et −4 en vaut huit. Choisir les paires reviendrait à choisir l'échelle
    sur laquelle on teste une tendance ; les prendre TOUTES ne laisse aucune liberté.
    """
    r = sorted(int(x) for x in rangees)
    if len(r) < 3:
        return {"decidable": False, "raison": "moins de trois rangées"}
    paires = []
    for i, a in enumerate(r):
        for b in r[i + 1:]:
            paires.append({"la_paire": [int(a), int(b)], "lecartement": int(abs(b - a))})
    ecarts = sorted({p["lecartement"] for p in paires})
    return {"decidable": True, "les_paires": paires, "combien_de_paires": len(paires),
            "les_ecartements_couverts": [int(x) for x in ecarts],
            "combien_decartements": len(ecarts),
            "lecartement_le_plus_petit": int(ecarts[0]),
            "lecartement_le_plus_grand": int(ecarts[-1])}


def _rangs(valeurs) -> np.ndarray:
    """Les rangs, ex aequo moyennés — écrit ici parce qu'une corrélation de rangs en dépend."""
    a = np.asarray(list(valeurs), dtype=float)
    ordre = np.argsort(a, kind="mergesort")
    rangs = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[ordre[j + 1]] == a[ordre[i]]:
            j += 1
        moyen = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            rangs[ordre[k]] = moyen
        i = j + 1
    return rangs


def la_correlation_de_rangs(x, y) -> float | None:
    """La corrélation de rangs entre deux listes — monotone, sans forme imposée.

    ⚠⚠ LA QUESTION EST « CROÎT-IL », PAS « CROÎT-IL LINÉAIREMENT ». Une corrélation ordinaire
    imposerait une droite, donc elle raterait une croissance qui sature — et un bruit qui se
    décorrèle SATURE par nature, puisque deux rangées assez loin l'une de l'autre n'ont plus rien
    à partager. Les rangs ne supposent que l'ordre.
    """
    a, b = np.asarray(list(x), dtype=float), np.asarray(list(y), dtype=float)
    if len(a) != len(b) or len(a) < 3:
        return None
    ra, rb = _rangs(a), _rangs(b)
    sa, sb = float(np.std(ra)), float(np.std(rb))
    if sa <= 0.0 or sb <= 0.0:
        return None
    return float(np.mean((ra - np.mean(ra)) * (rb - np.mean(rb))) / (sa * sb))


def le_taux_tient(taux, garantie: float = GARANTIE_PAR_EPREUVE) -> bool:
    """Un taux de faux tient-il la garantie ?

    ⚠⚠⚠ IL TIENT À DEUX FOIS LA GARANTIE, JAMAIS À ZÉRO. Chaque réplicat porte la garantie de
    l'épreuve, donc en exiger zéro c'est attendre du nul ce qu'il ne peut pas donner — `211` a
    refusé son propre étalon sur du code juste pour cette raison, et `178` l'avait payé avant lui.
    La marge de deux laisse trois erreurs d'échantillonnage au compte que `210` a dérivé.

    ⚠ La fonction est PURE et à part pour qu'elle se sonde sans courir un étalon : la règle et son
    site d'appel sont alors deux choses, et casser l'une rougit.
    """
    if taux is None:
        return False
    return bool(float(taux) <= float(garantie) * 2.0 + 1e-12)


def la_suite_est_monotone(valeurs) -> bool:
    """Une suite de comptes ne décroît-elle jamais ?

    ⚠⚠ UNE SENSIBILITÉ QUI RÉGRESSERAIT QUAND LA CROISSANCE AUGMENTE SERAIT UN DÉFAUT, PAS UN
    RÉSULTAT — et c'est pourquoi la monotonie se MESURE au lieu de s'affirmer. `178` a payé
    l'inverse : exiger un zéro que rien ne soutient.
    """
    v = [float(x) for x in valeurs]
    return bool(all(v[i] <= v[i + 1] for i in range(len(v) - 1)))


def contre_les_valeurs(paires: dict, rangees, tirages: int = PERMUTATIONS,
                       graine: int = GRAINE) -> dict:
    """LA RÈGLE RÉFUTÉE, portée comme contrôle nommé — et l'écart qu'elle coûte, mesuré.

    ⚠⚠⚠ ELLE A L'AIR JUSTE ET ELLE EST FAUSSE. Rebrasser les désaccords un à un contre des
    écartements figés semble poser la même question, et rend presque toujours le même verdict. Mais
    les désaccords ne sont pas trente-six nombres libres : ils partagent neuf rangées, donc chacune
    entre dans huit d'entre eux. Détruire cette structure rend un nul TROP ÉTROIT, donc une tendance
    déclarée là où il n'y en a pas — mesuré sur une matière à bruits propres alternés, elle tire
    cinq fois plus souvent que la bonne règle sans qu'aucune distance n'y soit pour rien.

    ⚠ Elle est calculée et PUBLIÉE à côté de l'épreuve, jamais suivie : c'est le précédent de `211`,
    qui porte le décalage sans recalage comme contrôle plutôt que de l'effacer.
    """
    if not paires.get("decidable"):
        return {"decidable": False, "raison": "les paires sont indécidables"}
    cles = sorted({(min(int(q["la_paire"][0]), int(q["la_paire"][1])),
                    max(int(q["la_paire"][0]), int(q["la_paire"][1]))):
                   float(q["le_desaccord_par_couture_en_voxels"])
                   for q in paires["les_paires"]
                   if q.get("le_desaccord_par_couture_en_voxels") is not None}.items())
    if len(cles) < 3:
        return {"decidable": False, "raison": "moins de trois paires portent un désaccord"}
    ecarts = [float(abs(a - b)) for (a, b), _s in cles]
    valeurs = [float(s) for _k, s in cles]
    obs = la_correlation_de_rangs(ecarts, valeurs)
    if obs is None:
        return {"decidable": False, "raison": "la tendance observée n'est pas calculable"}
    g = _rng(int(graine))
    nuls = []
    for _ in range(int(tirages)):
        t = la_correlation_de_rangs(ecarts, list(g.permutation(valeurs)))
        if t is not None:
            nuls.append(float(t))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de tendance"}
    au_moins = int(sum(1 for x in nuls if x >= obs))
    return {"decidable": True, "tirages": int(tirages),
            "la_tendance_observee": round(float(obs), 4),
            "la_tendance_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "ca_croit_selon_la_regle_refutee": bool(au_moins == 0)}


def contre_les_etiquettes(paires: dict, rangees, tirages: int = PERMUTATIONS,
                          graine: int = GRAINE) -> dict:
    """La tendance observée dépasse-t-elle celle de TOUS les rebrassages des étiquettes de rangée ?

    ⭐⭐⭐⭐ C'EST LE SEUL NUL QUI RÉPONDE À LA QUESTION, ET IL EST DICTÉ PAR LE MODÈLE LUI-MÊME.
    Sous le modèle de `208`, le désaccord d'une paire ne dépend que de l'IDENTITÉ de ses deux
    rangées — il vaut la racine de la somme des carrés de leurs bruits propres — et pas du tout de
    leur POSITION sur le treillis. Rebrasser l'affectation des identités aux positions laisse donc
    toute la structure du modèle intacte et ne détruit que le lien à la distance : c'est exactement
    l'hypothèse nulle, et non une approximation d'icelle.

    ⚠⚠⚠ PERMUTER LES DÉSACCORDS UN À UN SERAIT FAUX ET AURAIT L'AIR JUSTE. Les trente-six désaccords
    ne sont pas indépendants : ils partagent neuf rangées, donc chaque rangée entre dans huit
    d'entre eux. Un tirage qui les traiterait comme trente-six nombres libres casserait cette
    structure et rendrait un nul trop étroit — donc une tendance déclarée là où il n'y en a pas.
    Ici la structure voyage AVEC les rangées, parce que c'est l'affectation qui bouge.

    ⚠⚠⚠ ET LES REBRASSAGES QUI REFONT L'OBSERVÉ SONT ÉCARTÉS, PARCE QU'ILS NE SONT PAS UNE AUTRE
    HYPOTHÈSE. Une suite de positions a des SYMÉTRIES : la retourner bout pour bout laisse tous les
    écartements identiques, donc ce rebrassage-là reproduit exactement la tendance observée et la
    compte comme « au moins aussi forte ». Sur cinq rangées ils sont deux sur cent vingt, donc près
    d'un tirage sur quatre les touche — et l'épreuve REFUSE alors une croissance qu'elle voit
    parfaitement. Mesuré : la face positive de l'étalon tombait à trois sur six sur du code juste.
    Ce ne sont pas des nuls faibles, ce sont des ÉGALITÉS STRUCTURELLES, et leur compte est publié.

    ⚠ Le test est à UN SENS, déclaré d'avance : la question est si le désaccord CROÎT.
    """
    if not paires.get("decidable"):
        return {"decidable": False, "raison": "les paires sont indécidables"}
    r = sorted(int(x) for x in rangees)
    index = {v: i for i, v in enumerate(r)}
    mesure, lignes = {}, []
    for p in paires["les_paires"]:
        a, b = int(p["la_paire"][0]), int(p["la_paire"][1])
        s = p.get("le_desaccord_par_couture_en_voxels")
        if s is None:
            continue
        mesure[(min(a, b), max(a, b))] = float(s)
        lignes.append((a, b))
    if len(mesure) < 3:
        return {"decidable": False, "raison": "moins de trois paires portent un désaccord"}
    cles = sorted(mesure)
    valeurs = [float(mesure[k]) for k in cles]
    return _le_nul_des_etiquettes(cles, valeurs, r, tirages, graine)


def _le_nul_des_etiquettes(cles, valeurs, r, tirages: int, graine: int) -> dict:
    """
    @brief Le rebrassage des étiquettes de rangée, appliqué à N'IMPORTE QUEL vecteur par paire.

    ⚠⚠⚠ Ce moteur est extrait pour qu'il n'y en ait qu'UN. Deux règles le traversent — le désaccord
    brut que le verdict suit, et les résidus de l'ajustement additif que la tranche porte comme
    contrôle nommé — et elles ne diffèrent QUE par le vecteur qu'on leur donne. Deux
    implémentations du même nul finiraient par ne pas s'accorder sur le traitement des égalités
    structurelles, et la comparaison des deux taux de faux ne voudrait alors plus rien dire :
    c'est précisément cette comparaison qui est publiée.
    """
    index = {v: i for i, v in enumerate(r)}
    positions = np.asarray(r, dtype=float)

    def _ecarts(perm):
        return tuple(abs(float(positions[perm[index[a]]] - positions[perm[index[b]]]))
                     for a, b in cles)

    if len(cles) < 3:
        return {"decidable": False, "raison": "moins de trois paires portent une valeur"}
    identite = list(range(len(r)))
    observes = _ecarts(identite)
    # ⚠⚠ LA SYMETRIE SE CALCULE, ELLE NE SE DECOUVRE PAS PAR TIRAGE. Une suite de positions
    # symetrique autour de sa mediane — ce que le treillis rend TOUJOURS, puisque les ecartements
    # sont lus des deux cotes — est laissee identique par le retournement bout pour bout : ce
    # rebrassage-la refait tous les ecartements. Sur neuf rangees il vaut deux tirages sur neuf
    # factorielle, donc l'echantillonnage ne le rencontrerait presque jamais et on ne saurait pas
    # qu'il existe. Le publier le rend verifiable.
    retourne = list(range(len(r) - 1, -1, -1))
    symetrique = bool(_ecarts(retourne) == observes)
    obs = la_correlation_de_rangs(observes, valeurs)
    if obs is None:
        return {"decidable": False, "raison": "la tendance observée n'est pas calculable"}
    g = _rng(int(graine))
    nuls, rejets, essais = [], 0, 0
    while len(nuls) < int(tirages) and essais < int(tirages) * 50:
        essais += 1
        perm = list(g.permutation(len(r)))
        ec = _ecarts(perm)
        if ec == observes:
            rejets += 1
            continue
        t = la_correlation_de_rangs(ec, valeurs)
        if t is not None:
            nuls.append(float(t))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de tendance distincte"}
    au_moins = int(sum(1 for x in nuls if x >= obs))
    return {"decidable": True, "tirages": int(tirages),
            "combien_de_paires": len(cles),
            "la_tendance_observee": round(float(obs), 4),
            "la_tendance_du_nul_median": round(float(np.median(nuls)), 4),
            "la_tendance_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "les_rebrassages_qui_refont_lobserve": int(rejets),
            "la_suite_des_positions_a_une_symetrie": symetrique,
            "ca_croit_avec_lecartement": bool(au_moins == 0)}



def contre_les_residus(paires: dict, rangees, tirages: int = PERMUTATIONS,
                       graine: int = GRAINE) -> dict:
    """
    @brief LA RÈGLE PLUS PUISSANTE, REFUSÉE — portée comme contrôle nommé, avec son taux de faux.

    ⭐⭐⭐⭐ ELLE EST PLUS PUISSANTE, ET C'EST BIEN LÀ LE PIÈGE. Corréler l'écartement avec les
    RÉSIDUS de l'ajustement additif, plutôt qu'avec le désaccord brut, retire des données tout ce
    que les bruits propres des rangées expliquent — donc le bruit de fond contre lequel une
    croissance doit ressortir s'effondre, et la face positive de l'étalon monte. Une statistique
    qui voit mieux est exactement ce qu'on cherche, et c'est pour cela qu'il faut la mesurer au
    lieu de l'adopter.

    ⚠⚠⚠ ELLE NE TIENT PAS SA GARANTIE, ET LA RAISON EST STRUCTURELLE. Un résidu n'est pas une
    donnée : il est AJUSTÉ depuis les trente-six désaccords mêmes que le rebrassage redistribue.
    Le nul des étiquettes laisse intacte la structure du modèle — c'est ce qui le rend exact pour
    le désaccord brut — mais les résidus, eux, portent en plus la contrainte de l'ajustement, que
    la permutation ne redistribue pas. Le nul est alors trop étroit du côté qui compte.

    ⚠⚠ ELLE EST DONC CALCULÉE ET PUBLIÉE, JAMAIS SUIVIE. Le verdict de la tranche lit le désaccord
    brut ; celle-ci voyage à côté avec son taux de faux mesuré sur LES MÊMES réplicats et LES MÊMES
    graines que la règle gardée, sans quoi les deux taux ne se compareraient pas. C'est le
    précédent de `211`, appliqué à la statistique que la tranche a le plus regretté de refuser.
    """
    tri = le_triangle_surdetermine(paires, rangees)
    if not tri.get("decidable"):
        return {"decidable": False, "raison": tri.get("raison")}
    par_paire = tri.get("les_residus_par_paire_en_erreurs") or {}
    r = sorted(int(x) for x in rangees)
    cles, valeurs = [], []
    for nom, res in sorted(par_paire.items()):
        if res is None:
            continue
        a, b = (int(x) for x in nom.split("-"))
        cles.append((min(a, b), max(a, b)))
        # ⚠⚠⚠ LE RÉSIDU EST SIGNÉ, ET UNE SONDE A CORRIGÉ L'INVERSE. Une première version prenait
        # son AMPLEUR, au motif que l'ajustement rend autant de positifs que de négatifs. C'est
        # vrai en somme et faux en structure : une croissance avec la distance laisse des résidus
        # NÉGATIFS aux petits écartements et POSITIFS aux grands, donc la valeur absolue détruit
        # exactement le signal cherché. Mesuré — l'ampleur ne voyait rien, et tenait sa garantie
        # pour la seule raison qu'elle ne voyait rien.
        valeurs.append(float(res))
    # ⚠ AUCUN REFUS ICI : le moteur partagé en porte déjà un, et le dupliquer donnerait DEUX
    # endroits qui décident du même seuil. Une sonde l'a montré en ne pouvant pas casser celui-ci.
    ordre = sorted(range(len(cles)), key=lambda i: cles[i])
    rendu = _le_nul_des_etiquettes([cles[i] for i in ordre], [valeurs[i] for i in ordre],
                                   r, tirages, graine)
    if not rendu.get("decidable"):
        return rendu
    rendu["ce_quelle_correle"] = "l'écartement contre le résidu SIGNÉ de l'ajustement additif"
    rendu["ca_croit_selon_la_regle_plus_puissante"] = rendu.pop("ca_croit_avec_lecartement")
    return rendu


def le_triangle_surdetermine(paires: dict, rangees) -> dict:
    """Les bruits propres ajustés sur TOUTES les paires — le triangle de `212`, enfin réfutable.

    ⭐⭐⭐⭐ À TROIS RANGÉES LE TRIANGLE NE POUVAIT PAS CONTREDIRE LE MODÈLE. Trois paires, trois
    inconnues : le système est exactement déterminé, donc il rend toujours une solution et la seule
    chose qu'il puisse refuser est une variance négative. `212` l'a dit et l'a publié comme tel.
    À neuf rangées il porte trente-six équations pour neuf inconnues, et un système sur-déterminé
    n'a plus nulle part où se cacher : sous le modèle ses résidus sont nuls aux erreurs
    d'échantillonnage près, et un résidu qui les dépasse est une réfutation.

    ⚠⚠ L'ERREUR EST DÉRIVÉE, PAS CHOISIE : la variance d'une variance estimée sur `n` tirages vaut
    deux fois le carré de la variance divisé par `n - 1`, donc l'erreur d'une variance mesurée sur
    `n` coutures vaut cette variance fois la racine de deux sur `n - 1`. Aucun seuil n'entre là.

    ⚠ La variance NÉGATIVE reste refusée, comme chez `212` : elle réfute le modèle avant tout
    résidu, parce qu'aucune décomposition en somme de carrés ne peut la produire.
    """
    if not paires.get("decidable"):
        return {"decidable": False, "raison": "les paires sont indécidables"}
    r = sorted(int(x) for x in rangees)
    index = {v: i for i, v in enumerate(r)}
    lignes, cibles, erreurs, noms = [], [], [], []
    for p in paires["les_paires"]:
        a, b = int(p["la_paire"][0]), int(p["la_paire"][1])
        s = p.get("le_desaccord_par_couture_en_voxels")
        n = p.get("les_coutures_communes")
        if s is None or not n or int(n) < 3:
            continue
        v = float(s) ** 2
        ligne = [0.0] * len(r)
        ligne[index[a]] = 1.0
        ligne[index[b]] = 1.0
        lignes.append(ligne)
        cibles.append(v)
        erreurs.append(v * float(np.sqrt(2.0 / (int(n) - 1))))
        noms.append(f"{a}-{b}")
    if len(lignes) <= len(r):
        return {"decidable": False,
                "raison": f"{len(lignes)} équations pour {len(r)} inconnues — rien à sur-déterminer"}
    a_mat = np.asarray(lignes, dtype=float)
    y = np.asarray(cibles, dtype=float)
    sol, *_ = np.linalg.lstsq(a_mat, y, rcond=None)
    ajuste = a_mat @ sol
    residus = y - ajuste
    en_erreurs = [float(residus[i] / erreurs[i]) if erreurs[i] > 0 else None
                  for i in range(len(residus))]
    finis = [abs(x) for x in en_erreurs if x is not None]
    # ⚠⚠⚠ DEUX « PIRES » ET DEUX PAIRES, ET LES CONFONDRE A COÛTÉ UN NOM FAUX. Le plus grand
    # résidu BRUT (en voxels carrés) et le plus grand résidu EN ERREURS ne tombent pas sur la même
    # paire, puisque l'erreur d'échantillonnage varie d'une paire à l'autre avec sa longueur.
    # Première version : elle prenait l'argmax du résidu brut pour NOMMER la paire et publiait à
    # côté le max des résidus en erreurs — donc un nombre juste sous le nom d'une autre paire, ce
    # que `R4-L19` désigne comme pire qu'un nombre absent. Le verdict lit les ERREURS, donc c'est
    # la paire des erreurs qui compte ; l'autre est publiée sous son propre nom.
    pire_brut = max(range(len(residus)), key=lambda i: abs(residus[i]))
    pire_err = (max((i for i in range(len(residus)) if en_erreurs[i] is not None),
                    key=lambda i: abs(en_erreurs[i])) if finis else None)
    negatives = [r[i] for i in range(len(r)) if float(sol[i]) < 0.0]
    return {"decidable": True,
            "combien_dequations": int(len(lignes)),
            "combien_dinconnues": int(len(r)),
            "les_bruits_propres_en_voxels2": {str(r[i]): round(float(sol[i]), 4)
                                              for i in range(len(r))},
            "les_rangees_a_variance_negative": [int(x) for x in negatives],
            "le_modele_est_refute_par_une_variance_negative": bool(len(negatives) > 0),
            "le_pire_residu_en_voxels2": round(float(residus[pire_brut]), 4),
            "la_paire_du_pire_residu_en_voxels2": noms[pire_brut],
            "le_pire_residu_en_erreurs": (round(max(finis), 4) if finis else None),
            "la_paire_du_pire_residu_en_erreurs": (noms[pire_err] if pire_err is not None
                                                   else None),
            "le_residu_median_en_erreurs": (round(float(np.median(finis)), 4) if finis else None),
            # ⚠⚠ LES RESIDUS PAR PAIRE SONT PUBLIES POUR QU'UNE SEULE FONCTION LES PRODUISE. La
            # regle plus puissante que cette tranche porte comme controle nomme les LIT ici ; les
            # recalculer chez elle serait une SECONDE DEFINITION de l'ajustement additif, donc deux
            # chemins libres de diverger sur le rcond, sur l'ordre des equations ou sur l'erreur.
            # ⚠⚠ LES DEUX TABLES SONT PUBLIEES, et symetriquement : chaque « pire » doit pouvoir
            # se verifier contre LA SIENNE. Publier une seule table laissait l'autre affirmation
            # invérifiable, et c'est exactement par la que le nom faux avait survecu.
            "les_residus_par_paire_en_voxels2": {
                noms[i]: round(float(residus[i]), 4) for i in range(len(noms))},
            "les_residus_par_paire_en_erreurs": {
                noms[i]: (round(float(en_erreurs[i]), 4) if en_erreurs[i] is not None else None)
                for i in range(len(noms))},
            "le_modele_tient_aux_erreurs": (bool(max(finis) <= 3.0) if finis else None)}


def ce_que_la_longueur_fait(paires: dict) -> dict:
    """Le contrôle nommé : le nombre de coutures communes suit-il lui aussi l'écartement ?

    ⚠⚠⚠ C'EST LE PIÈGE DE LA TRANCHE, ET IL SE MESURE PLUTÔT QUE DE SE SUPPOSER ABSENT. Deux
    rangées éloignées partagent moins de trous, donc leur désaccord est estimé sur moins de
    coutures. Un écart-type estimé sur moins de tirages n'est pas BIAISÉ, seulement plus bruité —
    mais si la longueur suit l'écartement aussi nettement que le désaccord, alors une tendance
    déclarée peut n'être qu'une tendance de la longueur, et le dire coûte une ligne.
    """
    if not paires.get("decidable"):
        return {"decidable": False, "raison": "les paires sont indécidables"}
    ecarts, longueurs, troncons = [], [], []
    for p in paires["les_paires"]:
        n = p.get("les_coutures_communes")
        if n is None:
            continue
        ecarts.append(float(p["lecartement"]))
        longueurs.append(float(n))
        troncons.append(float(p.get("les_coutures_du_troncon") or 0))
    if len(ecarts) < 3:
        return {"decidable": False, "raison": "moins de trois paires portent une longueur"}
    return {"decidable": True,
            "la_tendance_de_la_longueur": (lambda v: None if v is None else round(v, 4))(
                la_correlation_de_rangs(ecarts, longueurs)),
            "la_tendance_du_troncon": (lambda v: None if v is None else round(v, 4))(
                la_correlation_de_rangs(ecarts, troncons)),
            "les_coutures_communes_les_plus_nombreuses": int(max(longueurs)),
            "les_coutures_communes_les_moins_nombreuses": int(min(longueurs)),
            "les_coutures_communes_medianes": int(np.median(longueurs))}


def les_desaccords_par_paire(pas_par_rangee: dict, colonnes, paires: dict) -> dict:
    """Le désaccord par couture de CHAQUE paire — le chemin unique, matière et étalon confondus.

    ⭐⭐⭐⭐ C'EST L'ÉTALON QUI IMPOSE QUE CETTE FONCTION EXISTE. Si la matière fabriquée passait par
    un raccourci pendant que le rouleau passe par `le_desaccord_des_cumuls` de `211`, l'étalon
    prouverait qu'un autre lecteur sépare — donc rien du tout. Les deux empruntent la même porte,
    et une faute dans le recalage des origines se paierait des DEUX côtés.

    ⚠ Le désaccord retenu est celui de TOUTES les coutures communes et non du seul tronçon
    contigu : c'est une dispersion de pas, elle n'a pas besoin de contiguïté — alors que le CUMUL,
    lui, en a besoin, et c'est pourquoi les deux nombres sont publiés côte à côte.
    """
    if not paires.get("decidable"):
        return {"decidable": False, "raison": "les paires sont indécidables"}
    out, perdues = [], []
    for p in paires["les_paires"]:
        a, b = int(p["la_paire"][0]), int(p["la_paire"][1])
        if a not in pas_par_rangee or b not in pas_par_rangee:
            perdues.append({"la_paire": [a, b], "raison": "une des deux rangées n'a pas été lue"})
            continue
        d = le_desaccord_des_cumuls(pas_par_rangee[a], pas_par_rangee[b], colonnes, a, b)
        if not d.get("decidable"):
            perdues.append({"la_paire": [a, b], "raison": d.get("raison")})
            continue
        n = int(d["les_coutures_communes"])
        sigma = float(d["lecart_type_des_pas_sur_toutes_les_communes_en_voxels"])
        out.append({
            "la_paire": [a, b], "lecartement": int(abs(b - a)),
            "les_coutures_communes": n,
            "les_coutures_du_troncon": int(d["les_coutures_du_troncon"]),
            "le_desaccord_par_couture_en_voxels": round(sigma, 4),
            "lerreur_dechantillonnage_en_voxels": round(
                float(sigma / np.sqrt(2.0 * n)), 4) if n > 0 else None,
            "le_desaccord_le_plus_grand_en_voxels": d.get("le_desaccord_le_plus_grand_en_voxels"),
            "lexcursion_du_desaccord_en_voxels": (
                d.get("lexcursion_du_desaccord") or {}).get("lexcursion_en_voxels")})
    if len(out) < 3:
        return {"decidable": False,
                "raison": f"seulement {len(out)} paires décidables — moins de trois"}
    return {"decidable": True, "les_paires": out, "combien_de_paires": len(out),
            "les_paires_perdues": perdues,
            "les_ecartements_couverts": sorted({int(p["lecartement"]) for p in out}),
            "lecartement_le_plus_grand": max(int(p["lecartement"]) for p in out)}


def des_rangees_ecartees_fabriquees(positions, coutures: int, derive: float, propre: float,
                                    croissance: float, graine: int,
                                    propres: dict | None = None) -> dict:
    """Des rangées posées SUR LE TREILLIS, dont le désaccord croît — ou non — avec l'écartement.

    ⭐⭐⭐⭐ LA CROISSANCE EST UNE MARCHE AU HASARD EN TRAVERS DES RANGÉES, ET C'EST LA SEULE FORME
    QUI DISE LA QUESTION. Un bruit qui « croît avec la distance » n'est pas un bruit plus fort ;
    c'est un champ dont deux lectures se ressemblent d'autant moins qu'elles sont loin. Posé ainsi,
    le carré du désaccord vaut deux fois le bruit propre PLUS l'écartement fois le carré de la
    croissance : exactement l'alternative, et un seul paramètre sépare les deux faces.

    ⚠⚠ LES DEUX FACES PARTAGENT TOUT LE RESTE — même dérive partagée, même bruit propre, même
    graine. Elles ne diffèrent que par la croissance, donc ce que l'étalon montre est bien l'effet
    de la croissance et non celui d'une matière plus agitée.

    ⚠ Les positions sont celles du treillis, jamais des indices de zéro à huit : c'est l'écartement
    RÉEL qui doit entrer dans la fixture, sinon la face positive testerait une autre échelle que
    celle que le rouleau porte.

    ⚠⚠⚠ `propres` EST NUL PAR DÉFAUT, ET SANS LUI L'ÉTALON EST TROP FACILE. Toutes les rangées
    portant le même bruit propre, le seul écart entre paires vient de la distance, donc l'épreuve
    la voit sans effort. `212` mesure que la vraie matière n'est pas comme ça — ses variances
    propres vont de **2,3394** à **6,5374** voxels carrés. Le paramètre est AJOUTÉ plutôt que le
    défaut corrigé en place, parce que les sondes de forme de cette tranche dérivent déjà du cas
    homogène.
    """
    p = sorted(int(x) for x in positions)
    if len(p) < 3:
        return {}
    r = _rng(int(graine))
    commune = r.normal(0.0, float(derive), size=int(coutures))
    champ = {p[0]: np.zeros(int(coutures), dtype=float)}
    for i in range(1, len(p)):
        saut = r.normal(0.0, float(croissance) * float(np.sqrt(p[i] - p[i - 1])),
                        size=int(coutures))
        champ[p[i]] = champ[p[i - 1]] + saut
    out = {}
    for pos in p:
        sigma_k = float((propres or {}).get(int(pos), propre))
        propre_k = r.normal(0.0, sigma_k, size=int(coutures))
        total = commune + champ[pos] + propre_k
        out[int(pos)] = {int(c): float(total[c]) for c in range(int(coutures))}
    return out


def la_croissance_derivee(sigma_211: float, ecartement_max: int,
                          facteur: float = 2.0) -> dict:
    """La croissance que la face positive pose — DÉRIVÉE des nombres publiés, jamais réglée.

    ⚠⚠⚠ UN PARAMÈTRE DE FIXTURE CHOISI POUR QUE L'ÉTALON PASSE EST UN SEUIL DÉGUISÉ. Celui-ci se
    dérive : le `facteur` est ce par quoi le CARRÉ du désaccord est multiplié d'un bout à l'autre
    de l'échelle des écartements. Deux, c'est le doublement ; trois, le triplement. Ce n'est pas un
    réglage mais un ÉNONCÉ sur la matière posée, et le bruit propre s'en déduit pour que
    l'écartement un retombe sur le nombre que `211` a mesuré.

    ⭐⭐ ET C'EST CE QUI PERMET DE PUBLIER UNE SENSIBILITÉ PLUTÔT QU'UN SIMPLE « ÇA SÉPARE ». En
    parcourant les facteurs, l'étalon dit LE PLUS PETIT que l'épreuve voit sur tous ses réplicats —
    donc un résultat négatif sur le rouleau cesse d'être un silence et devient une BORNE.
    """
    s = float(sigma_211)
    e = int(ecartement_max)
    f = float(facteur)
    if s <= 0.0 or e < 1 or f <= 1.0:
        return {"decidable": False,
                "raison": "le désaccord de `211`, l'échelle ou le facteur est absent"}
    return {"decidable": True,
            "le_desaccord_de_211_en_voxels": round(s, 4),
            "lecartement_le_plus_grand": e,
            "le_facteur_pose": round(f, 4),
            "la_croissance_posee_en_voxels": round(float(s * np.sqrt(f - 1.0) / np.sqrt(e)), 4),
            "le_bruit_propre_pose_en_voxels": round(float(s / np.sqrt(2.0)), 4),
            "ce_quelle_annonce_au_plus_grand_ecartement_en_voxels": round(
                float(s * np.sqrt(f)), 4)}


def les_bruits_propres_poses(positions, par_212: dict) -> dict | None:
    """Les bruits propres de `212` répartis sur les positions de l'étalon, en tournant.

    ⚠⚠ LA RÉPARTITION EST UNE ROTATION ET NON UNE AFFECTATION PAR NOM. Les rangées de `212` ne
    sont pas celles d'un étalon fabriqué, donc prétendre que la rangée 198 de là-bas est la
    rangée 198 d'ici serait un nom juste sur une chose fausse. Ce qui est repris est le JEU des
    valeurs — l'hétérogénéité mesurée — et rien d'autre.

    ⚠ Un producteur absent rend `None`, donc la fixture retombe sur son bruit uniforme, et
    l'étalon le DIT au lieu de fabriquer une hétérogénéité qu'il aurait inventée.
    """
    if not (par_212 or {}).get("decidable"):
        return None
    vals = [float(x) for x in par_212["les_bruits_propres_en_voxels"]]
    if not vals:
        return None
    return {int(pos): vals[i % len(vals)] for i, pos in enumerate(sorted(int(x)
                                                                        for x in positions))}


LES_FACTEURS = (2, 3, 4, 6, 9)
"""L'échelle des croissances que l'étalon parcourt, en facteurs sur le CARRÉ du désaccord.

⚠⚠ CE N'EST PAS UNE LISTE DE SEUILS MAIS UNE ÉCHELLE DE LECTURE. Chaque barreau est un énoncé —
« le carré du désaccord double / triple / quadruple d'un bout à l'autre des écartements » — et ce
que l'étalon publie est le PLUS PETIT que l'épreuve voit sur TOUS ses réplicats. Un barreau
d'échelle n'est pas une borne : ce qui est publié est le barreau atteint, et la monotonie du compte
le long de l'échelle est MESURÉE plutôt que supposée."""


def sur_letalon(positions, coutures: int = 240, sigma_211: float = 2.7138,
                derive: float = 1.5129, graine: int = GRAINE, replicats: int = 12,
                tirages: int = PERMUTATIONS, aveugle_croissance: float = 0.0,
                propres: dict | None = None, facteurs=LES_FACTEURS,
                refus_croissance: float = 0.0) -> dict:
    """Quelle décorrélation l'épreuve voit-elle, et se tait-elle quand il n'y en a pas ?

    ⭐⭐⭐⭐ LA FACE POSITIVE EST UNE ÉCHELLE, PAS UN OUI. La sonde a mesuré pourquoi : sur des
    rangées dont les bruits propres sont ceux que `212` a rendus, un doublement du carré du
    désaccord n'est vu que sur huit réplicats sur douze. Déclarer « l'étalon sépare » sur cette
    seule croissance aurait été un vœu ; parcourir l'échelle donne un nombre — le plus petit
    facteur vu partout — et ce nombre transforme un résultat négatif sur le rouleau en BORNE au
    lieu d'un silence.

    ⚠⚠ LES DEUX AUTRES FACES SONT DES TAUX SUR LE COMPTE DÉRIVÉ PAR `210`, jamais des zéros :
    chaque réplicat porte la garantie de l'épreuve, donc en attendre zéro c'est attendre du nul ce
    qu'il ne peut pas donner — la faute que `211` a payée et que `178` avait payée avant lui.

    ⚠⚠⚠ ET LE CONTRÔLE AVEUGLE DIT DE QUOI L'ÉPREUVE SÉPARE : une dérive PARTAGÉE, même dix fois
    plus forte, s'annule dans une différence de deux rangées et ne doit produire AUCUNE tendance.
    `aveugle_croissance` est nul par défaut et existe pour qu'il puisse TIRER — un contrôle qui ne
    pourrait jamais se déclencher ne prouverait rien.

    ⚠⚠⚠ `refus_croissance` EXISTE POUR LA MÊME RAISON, DU CÔTÉ DE LA FACE NÉGATIVE. Sur du code
    sain le taux de faux sort à zéro, donc la conjonction du verdict n'est exercée par RIEN de ce
    côté-là : retirer la lecture du taux laisserait l'étalon séparer quand même. Le passer non nul
    met une VRAIE croissance dans la face qui n'est pas censée en porter, donc le taux DOIT
    dépasser et le verdict DOIT cesser de séparer.

    ⚠⚠ UNE LIMITE, DITE PLUTÔT QUE MASQUÉE : la MONOTONIE de l'échelle est un conjoint du verdict
    que du code sain n'exerce jamais — aucune graine ni aucun compte de réplicats balayés ici ne
    rend une échelle qui régresse. Ce qui l'exerce est sa propre règle, sondée à part, et le bris
    qui débranche le facteur de la croissance : celui-là rend bien une échelle non monotone.
    """
    p_ = sorted(int(x) for x in positions)
    paires = les_paires_du_treillis(p_)
    if not paires.get("decidable"):
        return {"decidable": False, "raison": paires.get("raison")}
    emax = int(paires["lecartement_le_plus_grand"])
    colonnes = list(range(int(coutures) + 1))
    base = la_croissance_derivee(float(sigma_211), emax, 2.0)
    if not base.get("decidable"):
        return {"decidable": False, "raison": base.get("raison")}
    propre = float(base["le_bruit_propre_pose_en_voxels"])

    def _une_course(g: int, pousse: float, partage: float):
        """⚠⚠ LES DEUX RÈGLES LISENT LA MÊME FIXTURE ET LA MÊME GRAINE. Les mesurer sur deux
        courses distinctes rendrait deux taux de faux qui ne se comparent pas : l'écart entre eux
        serait alors celui des tirages autant que celui des règles, et c'est l'écart entre les
        règles que cette tranche publie."""
        rangees = des_rangees_ecartees_fabriquees(p_, int(coutures), partage, propre, pousse, g,
                                                  propres)
        if not rangees:
            return {"decidable": False, "raison": "la fixture n'a rendu aucune rangée"}
        mesures = les_desaccords_par_paire(rangees, colonnes, paires)
        if not mesures.get("decidable"):
            return {"decidable": False, "raison": mesures.get("raison")}
        return {"gardee": contre_les_etiquettes(mesures, p_, tirages, g + 7),
                "puissante": contre_les_residus(mesures, p_, tirages, g + 7)}

    def _vue(c) -> bool:
        return bool((c.get("gardee") or {}).get("ca_croit_avec_lecartement"))

    def _vue_puissante(c) -> bool:
        return bool((c.get("puissante") or {}).get("ca_croit_selon_la_regle_plus_puissante"))

    echelle, plus_petit = [], None
    for f in sorted(int(x) for x in facteurs):
        pose = la_croissance_derivee(float(sigma_211), emax, float(f))
        if not pose.get("decidable"):
            continue
        cr = float(pose["la_croissance_posee_en_voxels"])
        courses = [_une_course(int(graine) + 1000 * i, cr, float(derive))
                   for i in range(int(replicats))]
        vus = sum(int(_vue(c)) for c in courses)
        vus_puissante = sum(int(_vue_puissante(c)) for c in courses)
        echelle.append({"le_facteur": int(f), "la_croissance_en_voxels": round(cr, 4),
                        "ce_quelle_annonce_au_plus_grand_ecartement_en_voxels":
                            pose["ce_quelle_annonce_au_plus_grand_ecartement_en_voxels"],
                        "les_vus": int(vus),
                        "les_vus_de_la_regle_plus_puissante": int(vus_puissante),
                        "replicats": int(replicats)})
        if plus_petit is None and vus >= int(replicats):
            plus_petit = int(f)
    monotone = la_suite_est_monotone([b["les_vus"] for b in echelle])
    combien = les_replicats_du_refus(GARANTIE_PAR_EPREUVE)
    refus = int(combien["le_compte_decisif"])
    refusees = [_une_course(int(graine) + 500000 + 1000 * i, float(refus_croissance),
                            float(derive)) for i in range(refus)]
    faux = sum(int(_vue(c)) for c in refusees)
    faux_puissante = sum(int(_vue_puissante(c)) for c in refusees)
    aveugles = sum(int(_vue(_une_course(int(graine) + 900000 + 1000 * i,
                                        float(aveugle_croissance),
                                        float(derive) * 10.0)))
                   for i in range(refus))
    taux = float(faux) / float(refus)
    taux_puissante = float(faux_puissante) / float(refus)
    taux_aveugle = float(aveugles) / float(refus)
    aveugle_tient = le_taux_tient(taux_aveugle)
    return {"decidable": True,
            "les_positions_posees": [int(x) for x in p_],
            "les_coutures_par_replicat": int(coutures),
            "lecartement_le_plus_grand": emax,
            "le_bruit_propre_pose_en_voxels": round(propre, 4),
            "les_bruits_propres_par_rangee_en_voxels": (
                None if not propres else {str(k): round(float(x), 4)
                                          for k, x in sorted(propres.items())}),
            "la_derive_partagee_posee_en_voxels": float(derive),
            "la_croissance_posee_sur_la_face_negative_en_voxels": float(refus_croissance),
            "lechelle_de_sensibilite": echelle,
            "le_plus_petit_facteur_vu": plus_petit,
            "la_sensibilite_est_monotone": bool(monotone),
            "replicats": int(replicats),
            "les_replicats_du_refus": int(refus), "les_faux": int(faux),
            "le_plancher_de_202": combien["le_plancher_de_202"],
            "la_chance_de_rater_au_plancher": combien["la_chance_de_rater_au_plancher"],
            "le_taux_de_faux": round(taux, 4),
            "les_replicats_du_controle_aveugle": int(refus),
            "les_derives_partagees_vues": int(aveugles),
            "le_taux_du_controle_aveugle": round(taux_aveugle, 4),
            "une_derive_partagee_reste_invisible": aveugle_tient,
            # ⭐⭐⭐⭐ LA REGLE PLUS PUISSANTE, MESUREE SUR LES MEMES REPLICATS ET REFUSEE POUR CE
            # QU'ELLE RENDER ICI. Elle voit mieux — c'est ce que sa colonne de l'echelle montre —
            # et son taux de faux depasse la garantie. Publier les deux cote a cote est ce qui
            # empeche une tranche ulterieure de la redecouvrir et de l'adopter.
            "la_regle_plus_puissante": {
                "ce_quelle_correle":
                    "l'écartement contre le résidu SIGNÉ de l'ajustement additif",
                "les_vus_par_facteur": [
                    {"le_facteur": b["le_facteur"],
                     "les_vus": b["les_vus_de_la_regle_plus_puissante"],
                     "replicats": b["replicats"]} for b in echelle],
                "les_faux": int(faux_puissante),
                "les_replicats_du_refus": int(refus),
                "le_taux_de_faux": round(taux_puissante, 4),
                "elle_tient_sa_garantie": le_taux_tient(taux_puissante),
                "elle_voit_plus_que_la_gardee": bool(
                    sum(b["les_vus_de_la_regle_plus_puissante"] for b in echelle)
                    > sum(b["les_vus"] for b in echelle))},
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(plus_petit is not None and monotone
                                   and le_taux_tient(taux) and aveugle_tient)}



def _ce_qui_reste(croit, tient, negative) -> str:
    """
    @brief Ce que la porte laisse derrière elle, lu sur les TROIS réponses et non sur une seule.

    ⚠⚠⚠ Première version : ce champ ne branchait que sur `croit`, donc dès que la tendance était
    absente il répondait « RIEN DE CETTE PORTE » et justifiait par « seules les deux rangées
    extrêmes d'une bande coûtent quelque chose ». Or cette phrase EST l'énoncé du modèle additif :
    la tenir pendant que le triangle réfute ce modèle, c'est publier une conclusion que la mesure
    ne soutient pas. C'est la règle composée que rien n'exerçait, sous sa forme la plus discrète —
    le champ était juste sur le vrai rouleau le jour où la tendance et le résidu s'accordaient, et
    faux le jour où ils divergent, ce qui est exactement le jour qui compte.

    Les trois sorties, et elles sont exclusives :
    - la tendance existe          → la bande a une hauteur, elle reste à mesurer ;
    - aucune tendance, modèle sain → la hauteur est gratuite, la porte est close ;
    - aucune tendance, modèle cassé → quelque chose rompt l'additivité SANS être la distance, et
      c'est cela qui reste à nommer.
    """
    if croit is None or tient is None:
        return "INDÉCIDABLE"
    if croit:
        return "LA HAUTEUR TENABLE D'UNE BANDE"
    if tient and not negative:
        return "RIEN DE CETTE PORTE"
    return "CE QUI ROMPT L'ADDITIVITÉ SANS ÊTRE LA DISTANCE"


def _pourquoi_il_reste(croit, tient, negative) -> str:
    """La raison suit la sortie de `_ce_qui_reste`, jamais l'inverse."""
    if croit is None or tient is None:
        return "une des deux lectures n'a pas abouti"
    if croit:
        return ("le désaccord croît avec l'écartement, donc une bande a une hauteur au-delà de "
                "laquelle ses deux bords ne s'accordent plus")
    if tient and not negative:
        return ("le désaccord ne dépend pas de l'écartement et le modèle additif tient, donc "
                "seules les deux rangées extrêmes d'une bande coûtent quelque chose")
    return ("le désaccord ne dépend pas de l'écartement, mais le triangle sur-déterminé refuse "
            "un bruit propre par rangée : ce qui fait diverger deux rangées n'est ni leur "
            "distance ni leur seule identité")

def juger(mesures: dict, epreuve: dict, triangle: dict, longueur: dict,
          par_211: dict) -> dict:
    """Le bruit est-il PROPRE, ou est-ce un champ qui se décorrèle ?

    ⚠⚠ LA LONGUEUR DE L'ÉCHELLE SE PUBLIE AVANT SON VERDICT, comme `207`, `210` et `211` publient
    la longueur du tronçon avant la séparation. Une tendance cherchée sur trois écartements voisins
    n'est pas la même affirmation que la même tendance sur une échelle de un à trente-deux, et un
    verdict qui les rendrait identiques mentirait par omission.

    ⭐⭐ ET LES DEUX LECTURES SONT PUBLIÉES CÔTE À CÔTE PLUTÔT QUE FONDUES. L'épreuve répond « la
    tendance dépasse-t-elle le rebrassage » ; le triangle répond « le modèle additif tient-il sur
    trente-six équations ». Elles peuvent se contredire, et ce serait un fait : une tendance sans
    résidu dit que la croissance est trop douce pour rompre l'additivité, un résidu sans tendance
    dit que le modèle casse autrement que par la distance.
    """
    if not mesures.get("decidable"):
        return {"decidable": False, "raison": mesures.get("raison")}
    croit = epreuve.get("ca_croit_avec_lecartement")
    tient = triangle.get("le_modele_tient_aux_erreurs")
    negative = triangle.get("le_modele_est_refute_par_une_variance_negative")
    ecarts = mesures.get("les_ecartements_couverts") or []
    sigmas = [float(p["le_desaccord_par_couture_en_voxels"]) for p in mesures["les_paires"]]
    attendu = (par_211 or {}).get("le_desaccord_par_couture_en_voxels")
    le_plus_proche = min(mesures["les_paires"], key=lambda p: int(p["lecartement"]))
    le_plus_loin = max(mesures["les_paires"], key=lambda p: int(p["lecartement"]))
    return {"decidable": True,
            "combien_de_paires": int(mesures["combien_de_paires"]),
            "lechelle_des_ecartements": [int(min(ecarts)), int(max(ecarts))] if ecarts else None,
            "combien_decartements": len(ecarts),
            "le_desaccord_le_plus_petit_en_voxels": round(float(min(sigmas)), 4),
            "le_desaccord_le_plus_grand_en_voxels": round(float(max(sigmas)), 4),
            "le_desaccord_median_en_voxels": round(float(np.median(sigmas)), 4),
            "au_plus_petit_ecartement": {
                "la_paire": le_plus_proche["la_paire"],
                "lecartement": le_plus_proche["lecartement"],
                "le_desaccord_par_couture_en_voxels":
                    le_plus_proche["le_desaccord_par_couture_en_voxels"],
                "les_coutures_communes": le_plus_proche["les_coutures_communes"]},
            "au_plus_grand_ecartement": {
                "la_paire": le_plus_loin["la_paire"],
                "lecartement": le_plus_loin["lecartement"],
                "le_desaccord_par_couture_en_voxels":
                    le_plus_loin["le_desaccord_par_couture_en_voxels"],
                "les_coutures_communes": le_plus_loin["les_coutures_communes"]},
            "ce_que_211_a_mesure_a_lecartement_un_en_voxels": attendu,
            "la_tendance_observee": epreuve.get("la_tendance_observee"),
            "les_tirages_au_moins_aussi_forts": epreuve.get("les_tirages_au_moins_aussi_forts"),
            "le_bruit_croit_avec_lecartement": (None if croit is None else bool(croit)),
            "la_tendance_de_la_longueur": longueur.get("la_tendance_de_la_longueur"),
            "le_pire_residu_du_triangle_en_erreurs": triangle.get("le_pire_residu_en_erreurs"),
            "le_modele_additif_tient": (None if tient is None else bool(tient)),
            "le_modele_est_refute_par_une_variance_negative": (
                None if negative is None else bool(negative)),
            "la_hauteur_reste_gratuite": (None if (croit is None or tient is None)
                                          else bool((not croit) and tient and not negative)),
            "ce_qui_reste_a_mesurer": _ce_qui_reste(croit, tient, negative),
            "pourquoi_il_reste_a_mesurer": _pourquoi_il_reste(croit, tient, negative)}



def ce_quon_peut_poser(par_211: dict, par_208: dict) -> dict:
    """
    @brief Les deux nombres que l'étalon exige, relus chez leurs producteurs ou REFUSÉS.

    ⚠⚠⚠ Première version : `mesurer` posait l'étalon sur `... or 2.7138` et `... or 1.5129`, deux
    valeurs TAPÉES en repli. Elles se trouvaient être les bonnes, ce qui est la pire façon d'avoir
    raison : le jour où un producteur ne tourne pas, l'étalon se pose quand même, sur des nombres
    que plus personne ne peut rattacher à une mesure. Un nombre sans producteur est un nombre
    inventé, même quand il est juste.

    Le repli est donc remplacé par un REFUS NOMMÉ : sans `211` et sans `208`, il n'y a pas
    d'étalon, et la mesure le dit au lieu de le masquer.
    """
    sigma = (par_211 or {}).get("le_desaccord_par_couture_en_voxels") \
        if (par_211 or {}).get("decidable") else None
    derive = (par_208 or {}).get("la_derive_partagee_en_voxels") \
        if (par_208 or {}).get("decidable") else None
    manquants = [nom for nom, val in (("`211`", sigma), ("`208`", derive)) if val is None]
    if manquants:
        return {"decidable": False,
                "raison": "l'étalon ne peut pas être posé : " + " et ".join(manquants)
                          + " n'a pas rendu son nombre"}
    return {"decidable": True,
            "le_desaccord_de_211_en_voxels": float(sigma),
            "la_derive_partagee_de_208_en_voxels": float(derive)}

def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            combien: int = LES_RANGEES, ecartements=LES_ECARTEMENTS) -> dict:
    """Les rangées écartées lues, puis le désaccord de chaque paire contre son écartement."""
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
    echelle = les_rangees_ecartees(gy, ecartements)
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
    par_211 = ce_que_laccord_a_rendu()
    par_208 = ce_que_la_voisine_a_rendu()
    par_212 = les_bruits_propres_mesures()
    paires = les_paires_du_treillis(echelle["les_rangees"])
    mesures = les_desaccords_par_paire(pas_par_rangee, les_colonnes, paires)
    if not mesures.get("decidable"):
        return {"decidable": False, "raison": mesures.get("raison")}
    epreuve = contre_les_etiquettes(mesures, echelle["les_rangees"], PERMUTATIONS, graine)
    refutee = contre_les_valeurs(mesures, echelle["les_rangees"], PERMUTATIONS, graine)
    puissante = contre_les_residus(mesures, echelle["les_rangees"], PERMUTATIONS, graine)
    triangle = le_triangle_surdetermine(mesures, echelle["les_rangees"])
    longueur = ce_que_la_longueur_fait(mesures)
    posable = ce_quon_peut_poser(par_211, par_208)
    sigma_211 = posable.get("le_desaccord_de_211_en_voxels")
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "les_rangees_ecartees": echelle,
        "ce_que_208_a_rendu": par_208,
        "ce_que_211_a_rendu": par_211,
        "ce_que_212_a_rendu": par_212,
        "les_lignes": lignes,
        "les_pas_par_rangee": {str(k): len(x) for k, x in pas_par_rangee.items()},
        "les_paires_du_treillis": {k: x for k, x in paires.items() if k != "les_paires"},
        "les_desaccords_par_paire": mesures,
        "lepreuve": epreuve,
        "la_regle_refutee": refutee,
        "la_regle_plus_puissante": puissante,
        "le_triangle_surdetermine": triangle,
        "ce_que_la_longueur_fait": longueur,
        "le_verdict": juger(mesures, epreuve, triangle, longueur, par_211),
        "ce_quon_peut_poser": posable,
        "letalon": (sur_letalon(
            echelle["les_rangees"],
            max(3, int(np.median([int(p["les_coutures_communes"])
                                  for p in mesures["les_paires"]]))),
            float(sigma_211),
            float(posable["la_derive_partagee_de_208_en_voxels"]),
            graine, replicats,
            propres=les_bruits_propres_poses(echelle["les_rangees"], par_212))
            if posable.get("decidable")
            else {"decidable": False, "raison": posable.get("raison")}),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"indécidable — {r['raison']}")
        return
    e = r.get("les_rangees_ecartees") or {}
    print(f"médiane {e.get('la_mediane')} · {e.get('combien_de_rangees')} rangées · "
          f"écartements déclarés {e.get('les_ecartements_declares')}")
    for p_ in (e.get("les_ecartements_perdus") or []):
        print(f"  ⚠ écartement {p_['lecartement']} perdu — {p_['raison']}")
    m = r.get("les_desaccords_par_paire") or {}
    print(f"\n{m.get('combien_de_paires')} paires · écartements couverts "
          f"{m.get('les_ecartements_couverts')}")
    print(f"{'paire':>12} {'écart':>6} {'coutures':>9} {'désaccord':>10} {'erreur':>8}")
    for p_ in sorted(m.get("les_paires") or [], key=lambda x: (x["lecartement"], x["la_paire"])):
        print(f"{str(p_['la_paire']):>12} {p_['lecartement']:>6} "
              f"{p_['les_coutures_communes']:>9} "
              f"{p_['le_desaccord_par_couture_en_voxels']:>10.4f} "
              f"{(p_.get('lerreur_dechantillonnage_en_voxels') or 0.0):>8.4f}")
    ep = r.get("lepreuve") or {}
    print(f"\ntendance {ep.get('la_tendance_observee')} · nul médian "
          f"{ep.get('la_tendance_du_nul_median')} · nul le plus fort "
          f"{ep.get('la_tendance_du_nul_la_plus_forte')} · "
          f"{ep.get('les_tirages_au_moins_aussi_forts')}/{ep.get('tirages')} au moins aussi forts")
    t = r.get("le_triangle_surdetermine") or {}
    print(f"triangle : {t.get('combien_dequations')} équations pour "
          f"{t.get('combien_dinconnues')} inconnues · pire résidu "
          f"{t.get('le_pire_residu_en_erreurs')} erreurs sur {t.get('la_paire_du_pire_residu')}")
    lg = r.get("ce_que_la_longueur_fait") or {}
    print(f"contrôle de longueur : tendance {lg.get('la_tendance_de_la_longueur')}")
    v_ = r.get("le_verdict") or {}
    print(f"\nVERDICT · le bruit croît avec l'écartement : "
          f"{v_.get('le_bruit_croit_avec_lecartement')} · le modèle additif tient : "
          f"{v_.get('le_modele_additif_tient')} · la hauteur reste gratuite : "
          f"{v_.get('la_hauteur_reste_gratuite')}")
    print(f"  reste à mesurer : {v_.get('ce_qui_reste_a_mesurer')}")
    print(f"  pourquoi        : {v_.get('pourquoi_il_reste_a_mesurer')}")
    et = r.get("letalon") or {}
    print("\nétalon · échelle de sensibilité :")
    for b in (et.get("lechelle_de_sensibilite") or []):
        print(f"    facteur {b['le_facteur']:>2} · croissance {b['la_croissance_en_voxels']:.4f} "
              f"· vu {b['les_vus']}/{b['replicats']}")
    print(f"  plus petit facteur vu {et.get('le_plus_petit_facteur_vu')} · monotone "
          f"{et.get('la_sensibilite_est_monotone')} · faux "
          f"{et.get('les_faux')}/{et.get('les_replicats_du_refus')} = {et.get('le_taux_de_faux')} "
          f"· aveugle {et.get('les_derives_partagees_vues')}/"
          f"{et.get('les_replicats_du_controle_aveugle')} = "
          f"{et.get('le_taux_du_controle_aveugle')} · sépare {et.get('letalon_separe')}")


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

    # ⭐⭐⭐⭐ LES RANGEES SE POSENT DES DEUX COTES, ET LA MEDIANE EST CELLE DES TRANCHES D'AVANT.
    ec = les_rangees_ecartees(40)
    v("★★★★ la médiane est celle de `la_ligne_declaree`, donc la même que `208`, `210` et `211`",
      ec.get("decidable") and ec.get("la_mediane") == la_ligne_declaree(40), str(ec.get("la_mediane")))
    v("★★★★ chaque écartement tenu est lu DES DEUX CÔTÉS — n'en lire qu'un serait un choix",
      all(len(t["les_cotes"]) == 2 for t in (ec.get("les_ecartements_tenus") or [{"les_cotes": []}])),
      str(ec.get("les_ecartements_tenus")))
    v("★★★★ quatre écartements des deux côtés font NEUF rangées, pas cinq",
      ec.get("combien_de_rangees") == 9, str(ec.get("les_rangees")))
    v("★★★ la médiane est dans le jeu, une seule fois",
      (ec.get("les_rangees") or []).count(ec.get("la_mediane")) == 1)
    # ⚠⚠⚠ UN ECARTEMENT QUI SORT DU TREILLIS EST COMPTE, JAMAIS REPLIE : replier collerait deux
    # ecartements sur la meme rangee, donc mettrait deux points de l'echelle au meme endroit.
    petit = les_rangees_ecartees(8)
    v("★★★★ sur un treillis étroit, un écartement qui sort d'un seul bord n'est lu que d'UN côté "
      "et le reste est publié",
      petit.get("decidable") and any(len(t["les_cotes"]) == 1
                                     for t in (petit.get("les_ecartements_tenus") or [])),
      str(petit.get("les_ecartements_tenus")))
    v("★★★★ et aucune rangée n'est comptée deux fois sous deux écartements",
      len(petit.get("les_rangees") or []) == len(set(petit.get("les_rangees") or [])))
    v("★★★ un écartement qui ne tient pas du tout est PERDU et nommé",
      (les_rangees_ecartees(6).get("les_ecartements_perdus") or []) != [],
      str(les_rangees_ecartees(6).get("les_ecartements_perdus")))
    v("★★★ un treillis qui n'offre pas trois rangées est indécidable",
      not les_rangees_ecartees(2).get("decidable"))
    v("★★★ un écartement nul n'est pas une paire",
      any(p_["lecartement"] == 0 for p_ in (les_rangees_ecartees(40, (0, 4)).get("les_ecartements_perdus") or [])))

    # ⭐⭐⭐⭐ L'ECHELLE EST DERIVEE DU JEU LU, ET ELLE VA BIEN PLUS LOIN QUE LES ECARTEMENTS POSES.
    pa = les_paires_du_treillis(ec["les_rangees"])
    v("★★★★ toutes les paires sont prises, donc aucune échelle n'est choisie",
      pa.get("combien_de_paires") == 9 * 8 // 2, str(pa.get("combien_de_paires")))
    v("★★★★ l'échelle DÉRIVÉE va jusqu'au DOUBLE du plus grand écartement déclaré",
      pa.get("lecartement_le_plus_grand") == 2 * max(LES_ECARTEMENTS),
      str(pa.get("lecartement_le_plus_grand")))
    v("★★★★ et elle porte plus d'écartements que les quatre déclarés",
      (pa.get("combien_decartements") or 0) > len(LES_ECARTEMENTS),
      str(pa.get("les_ecartements_couverts")))
    v("★★★ l'écartement le plus petit vaut un",
      pa.get("lecartement_le_plus_petit") == 1)
    v("★★★ moins de trois rangées ne font pas d'échelle",
      not les_paires_du_treillis([3, 4]).get("decidable"))

    # ⭐⭐⭐ LA CORRELATION EST DE RANGS, DONC MONOTONE ET SANS FORME IMPOSEE.
    v("★★★ une suite croissante corrèle à un avec elle-même",
      abs(la_correlation_de_rangs([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-12)
    v("★★★ une suite décroissante corrèle à moins un",
      abs(la_correlation_de_rangs([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-12)
    # ⚠⚠ UNE CROISSANCE QUI SATURE DOIT ETRE VUE : c'est la forme qu'un champ qui se decorrele
    # prend REELLEMENT, et une correlation ordinaire la raterait d'autant plus qu'elle sature.
    v("★★★★ une croissance qui SATURE corrèle quand même à un — c'est pourquoi les rangs",
      abs(la_correlation_de_rangs([1, 2, 4, 8, 16], [1.0, 1.9, 2.6, 2.9, 3.0]) - 1.0) < 1e-12)
    # ⚠⚠ LES EX AEQUO CHANGENT LA REPONSE, ET LA SONDE LIT LE NOMBRE. Une suite constante rend
    # `None` que les rangs soient moyennes ou non, donc elle ne separait rien : il faut une suite
    # ou DEUX valeurs seulement sont egales, et la valeur exacte est calculee a la main.
    v("★★★★ les ex aequo sont MOYENNÉS, et ça change le nombre : deux valeurs égales sur quatre "
      "ne rendent plus un accord parfait",
      abs(la_correlation_de_rangs([1, 2, 3, 4], [10, 20, 20, 30]) - 0.9487) < 1e-4,
      str(round(la_correlation_de_rangs([1, 2, 3, 4], [10, 20, 20, 30]), 4)))
    v("★★★ et une suite constante ne corrèle à rien du tout",
      la_correlation_de_rangs([1, 2, 3], [5, 5, 5]) is None)
    v("★★★ moins de trois points ne rendent aucune corrélation",
      la_correlation_de_rangs([1, 2], [1, 2]) is None)
    v("★★★ deux listes de longueurs différentes ne rendent aucune corrélation",
      la_correlation_de_rangs([1, 2, 3], [1, 2]) is None)

    # ⭐⭐⭐⭐ LA CROISSANCE DE LA FIXTURE EST DERIVEE, JAMAIS REGLEE.
    cr = la_croissance_derivee(2.7138, 32)
    v("★★★★ la croissance posée est le désaccord de `211` divisé par la racine de l'échelle",
      cr["decidable"] and abs(cr["la_croissance_posee_en_voxels"]
                              - round(2.7138 / np.sqrt(32), 4)) < 1e-9,
      str(cr.get("la_croissance_posee_en_voxels")))
    v("★★★★ au plus grand écartement elle DOUBLE le carré du désaccord, donc annonce √2 fois "
      "le nombre de `211`",
      abs(cr["ce_quelle_annonce_au_plus_grand_ecartement_en_voxels"]
          - round(2.7138 * np.sqrt(2.0), 4)) < 1e-9,
      str(cr.get("ce_quelle_annonce_au_plus_grand_ecartement_en_voxels")))
    v("★★★ et le bruit propre posé fait retomber l'écartement un sur le nombre de `211`",
      abs(np.sqrt(2.0) * cr["le_bruit_propre_pose_en_voxels"] - 2.7138) < 1e-3,
      str(cr.get("le_bruit_propre_pose_en_voxels")))
    v("★★★ un désaccord absent ou une échelle vide ne dérivent aucune croissance",
      not la_croissance_derivee(0.0, 32)["decidable"]
      and not la_croissance_derivee(2.7138, 0)["decidable"])

    # ⭐⭐⭐⭐ LA FIXTURE POSE CE QU'ELLE ANNONCE, ET ÇA SE VÉRIFIE SANS SEUIL : le carré du
    # désaccord doit valoir deux fois le bruit propre PLUS l'écartement fois le carré de la
    # croissance. C'est une identité algébrique de la construction, pas une tendance à constater.
    positions = [0, 1, 4, 8, 16, 32]
    plates = des_rangees_ecartees_fabriquees(positions, 4000, 1.5, 2.0, 0.0, 7)
    poussees = des_rangees_ecartees_fabriquees(positions, 4000, 1.5, 2.0, 0.5, 7)

    def _sigma(rangees, a, b):
        return float(np.std([rangees[a][c] - rangees[b][c] for c in rangees[a]]))

    v("★★★★ sans croissance, le désaccord ne dépend PAS de l'écartement",
      abs(_sigma(plates, 0, 1) - _sigma(plates, 0, 32)) < 0.25,
      f"{_sigma(plates, 0, 1):.4f} à 1 contre {_sigma(plates, 0, 32):.4f} à 32")
    v("★★★★ avec croissance, il croît, et il vaut la racine de 2σ² + écartement × croissance²",
      abs(_sigma(poussees, 0, 32) - np.sqrt(2 * 2.0 ** 2 + 32 * 0.5 ** 2)) < 0.6,
      f"{_sigma(poussees, 0, 32):.4f} contre "
      f"{np.sqrt(2 * 2.0 ** 2 + 32 * 0.5 ** 2):.4f}")
    v("★★★★ et à l'écartement un les deux fixtures se confondent — elles ne diffèrent QUE par la "
      "croissance",
      abs(_sigma(plates, 0, 1) - _sigma(poussees, 0, 1)) < 0.35,
      f"{_sigma(plates, 0, 1):.4f} contre {_sigma(poussees, 0, 1):.4f}")
    v("★★★ la dérive PARTAGÉE s'annule dans la différence, donc elle ne touche pas le désaccord",
      abs(_sigma(des_rangees_ecartees_fabriquees(positions, 4000, 40.0, 2.0, 0.0, 7), 0, 1)
          - _sigma(plates, 0, 1)) < 0.25)
    v("★★★ moins de trois positions ne fabriquent rien",
      des_rangees_ecartees_fabriquees([0, 1], 100, 1.0, 1.0, 0.0, 7) == {})

    # ⭐⭐⭐⭐ LE CHEMIN DE MESURE EST LE MÊME POUR LA MATIÈRE ET POUR L'ÉTALON.
    paires_f = les_paires_du_treillis(positions)
    col_f = list(range(4001))
    mes_plates = les_desaccords_par_paire(plates, col_f, paires_f)
    mes_poussees = les_desaccords_par_paire(poussees, col_f, paires_f)
    v("★★★ le chemin rend une ligne par paire, avec sa longueur À CÔTÉ de son désaccord",
      mes_plates.get("decidable")
      and mes_plates.get("combien_de_paires") == paires_f.get("combien_de_paires")
      and all("les_coutures_communes" in p_ and "le_desaccord_par_couture_en_voxels" in p_
              for p_ in (mes_plates.get("les_paires") or [])))
    # ⚠⚠⚠ DEUX DISPERSIONS SONT PUBLIEES PAR `211` ET UNE SEULE EST LA BONNE. Celle du tronçon
    # contigu n'est pas celle de toutes les coutures communes des que les trous coupent la ligne,
    # et prendre l'une pour l'autre serait un nombre juste sous un mauvais nom. La sonde compare
    # au CHAMP NOMME du producteur, jamais a un calcul refait ici.
    _a = {c: float(c % 5) - 2.0 for c in range(40)}
    _b = {c: float((c * 3) % 7) - 3.0 for c in range(40) if c not in (11, 12, 13)}
    _d = le_desaccord_des_cumuls(_a, _b, list(range(41)), 1, 2)
    _m = les_desaccords_par_paire({1: _a, 2: _b}, list(range(41)),
                                  {"decidable": True, "les_paires": [
                                      {"la_paire": [1, 2], "lecartement": 1},
                                      {"la_paire": [1, 2], "lecartement": 1},
                                      {"la_paire": [1, 2], "lecartement": 1}]})
    v("★★★★ la fixture SÉPARE les deux dispersions que `211` publie — sinon la sonde suivante ne "
      "dirait rien",
      abs(float(_d["lecart_type_des_pas_sur_toutes_les_communes_en_voxels"])
          - float(_d["lecart_type_des_pas_du_troncon_en_voxels"])) > 0.05,
      f"{_d.get('lecart_type_des_pas_sur_toutes_les_communes_en_voxels')} contre "
      f"{_d.get('lecart_type_des_pas_du_troncon_en_voxels')}")
    v("★★★★ et le désaccord publié est celui de TOUTES les coutures communes, pas du tronçon",
      abs(float(_m["les_paires"][0]["le_desaccord_par_couture_en_voxels"])
          - float(_d["lecart_type_des_pas_sur_toutes_les_communes_en_voxels"])) < 1e-9,
      str(_m["les_paires"][0]["le_desaccord_par_couture_en_voxels"]))
    # ⚠⚠⚠ ET LE TRONCON EST L'INTERSECTION, JAMAIS L'UNION : une colonne qu'une seule rangee a lue
    # n'a pas de difference, donc accumuler par-dessus inventerait un ecart que personne n'a
    # mesure. La fixture met les trous des DEUX cotes pour que l'union differe de l'intersection.
    _u = {c: 1.0 for c in range(0, 10)}
    _w = {c: 0.0 for c in range(5, 15)}
    _mi = les_desaccords_par_paire({1: _u, 2: _w}, list(range(16)),
                                   {"decidable": True, "les_paires": [
                                       {"la_paire": [1, 2], "lecartement": 1}] * 3})
    v("★★★★ le tronçon est l'INTERSECTION des deux rangées, jamais leur union",
      _mi["les_paires"][0]["les_coutures_communes"] == 5,
      str(_mi["les_paires"][0]["les_coutures_communes"]))
    v("★★★ l'erreur d'échantillonnage est DÉRIVÉE, σ sur racine de deux n",
      abs(mes_plates["les_paires"][0]["lerreur_dechantillonnage_en_voxels"]
          - round(float(mes_plates["les_paires"][0]["le_desaccord_par_couture_en_voxels"]
                        / np.sqrt(2.0 * mes_plates["les_paires"][0]["les_coutures_communes"])), 4))
      < 1e-9)
    # ⚠⚠⚠ UNE PAIRE DONT UNE RANGEE MANQUE EST PERDUE ET COMPTEE, jamais absorbee en silence :
    # une echelle qui perdrait ses grands ecartements sans le dire testerait une autre question.
    amputee = {k: x for k, x in plates.items() if k != 32}
    mes_amputees = les_desaccords_par_paire(amputee, col_f, paires_f)
    v("★★★★ une paire dont une rangée n'a pas été lue est PERDUE et nommée, pas silencieuse",
      mes_amputees.get("decidable") and len(mes_amputees.get("les_paires_perdues") or []) == 5
      and (mes_amputees.get("lecartement_le_plus_grand") or 99) < 32,
      str(len(mes_amputees.get("les_paires_perdues") or [])))
    v("★★★ moins de trois paires décidables rendent le chemin indécidable",
      not les_desaccords_par_paire({0: plates[0], 1: plates[1]}, col_f, paires_f)["decidable"])
    v("★★★ des paires indécidables ne traversent pas le chemin",
      not les_desaccords_par_paire(plates, col_f, {"decidable": False})["decidable"])

    # ⭐⭐⭐⭐ L'EPREUVE TIRE SUR LA CROISSANCE ET SE TAIT SUR LE PLAT.
    ep_p = contre_les_etiquettes(mes_poussees, positions, PERMUTATIONS, 11)
    ep_0 = contre_les_etiquettes(mes_plates, positions, PERMUTATIONS, 11)
    v("★★★★ l'épreuve TIRE quand le désaccord croît avec l'écartement",
      ep_p.get("decidable") and ep_p.get("ca_croit_avec_lecartement"),
      f"{ep_p.get('la_tendance_observee')} contre {ep_p.get('la_tendance_du_nul_la_plus_forte')}")
    v("★★★★ et elle SE TAIT quand il n'en dépend pas",
      ep_0.get("decidable") and not ep_0.get("ca_croit_avec_lecartement"),
      f"{ep_0.get('la_tendance_observee')} contre {ep_0.get('la_tendance_du_nul_la_plus_forte')}")
    v("★★★ le nul le plus fort est publié à côté de l'observé, pas seulement le verdict",
      ep_p.get("la_tendance_du_nul_la_plus_forte") is not None
      and ep_p.get("les_tirages_au_moins_aussi_forts") is not None)
    # ⚠⚠⚠ LE REBRASSAGE PORTE SUR LES ETIQUETTES, DONC IL PRESERVE LE JEU DES DESACCORDS. Un bris
    # qui permuterait les trente-six desaccords un a un casserait la structure — chaque rangee
    # entre dans huit paires — et rendrait un nul trop etroit, donc une tendance declaree a tort.
    v("★★★★ chaque rangée entre dans exactement n−1 paires, et c'est cette structure que le "
      "rebrassage préserve",
      all(sum(1 for p_ in (mes_poussees.get("les_paires") or []) if r_ in p_["la_paire"])
          == len(positions) - 1 for r_ in positions))
    # ⚠⚠⚠ ET LES EGALITES STRUCTURELLES SONT COMPTEES : retourner la suite des positions bout
    # pour bout laisse TOUS les ecartements identiques, donc ce rebrassage refait l'observe au
    # lieu de le contredire. Les compter pour zero ferait refuser une croissance parfaitement
    # visible — mesure, la face positive de l'etalon tombait a trois sur six.
    sym = [0, 4, 7, 8, 9, 12, 16]
    mes_sym = les_desaccords_par_paire(
        des_rangees_ecartees_fabriquees(sym, 500, 1.5, 2.0, 0.5, 3), list(range(501)),
        les_paires_du_treillis(sym))
    v("★★★★ une suite SYMÉTRIQUE — celle que le treillis rend toujours — porte une symétrie, "
      "et elle est CALCULÉE et non découverte par tirage",
      contre_les_etiquettes(mes_sym, sym, PERMUTATIONS, 11)[
          "la_suite_des_positions_a_une_symetrie"] is True)
    v("★★★★ une suite qui n'est PAS symétrique n'en porte aucune",
      ep_p.get("la_suite_des_positions_a_une_symetrie") is False,
      str(positions))
    v("★★★ et le compte des rebrassages écartés est publié, même quand il vaut zéro",
      "les_rebrassages_qui_refont_lobserve" in ep_p)
    # ⚠⚠⚠ SUR NEUF RANGEES LE RETOURNEMENT VAUT DEUX TIRAGES SUR NEUF FACTORIELLE, donc
    # l'echantillonnage ne le rencontre presque jamais et la sonde ne verrait rien. Sur TROIS
    # positions il vaut un tirage sur trois, donc le mecanisme se mesure au lieu de se supposer.
    _p3 = [0, 1, 2]
    _e3 = contre_les_etiquettes(
        les_desaccords_par_paire(des_rangees_ecartees_fabriquees(_p3, 400, 1.5, 2.0, 0.6, 3),
                                 list(range(401)), les_paires_du_treillis(_p3)),
        _p3, PERMUTATIONS, 11)
    v("★★★★ sur trois positions symétriques, les rebrassages qui refont l'observé sont bel et "
      "bien ÉCARTÉS, et comptés",
      (_e3.get("les_rebrassages_qui_refont_lobserve") or 0) > 0
      and _e3.get("la_suite_des_positions_a_une_symetrie") is True,
      str(_e3.get("les_rebrassages_qui_refont_lobserve")))
    # ⚠⚠⚠ L'EPREUVE EST A UN SENS, DECLARE D'AVANCE, et ça se mesure : un desaccord qui DECROIT
    # nettement avec l'ecartement est une tendance tout aussi forte, et une epreuve a deux sens la
    # declarerait. La question posee est « croît-il », donc elle doit se taire.
    _dec = {"decidable": True, "les_paires": [
        {"la_paire": [a, b], "lecartement": abs(b - a), "les_coutures_communes": 200,
         "le_desaccord_par_couture_en_voxels": round(9.0 - 0.25 * abs(b - a), 4)}
        for i, a in enumerate([0, 1, 4, 8, 16, 32]) for b in [0, 1, 4, 8, 16, 32][i + 1:]]}
    _ed = contre_les_etiquettes(_dec, [0, 1, 4, 8, 16, 32], PERMUTATIONS, 11)
    v("★★★★ un désaccord qui DÉCROÎT avec l'écartement ne fait PAS tirer une épreuve à un sens",
      _ed.get("decidable") and _ed.get("ca_croit_avec_lecartement") is False
      and (_ed.get("la_tendance_observee") or 0.0) < -0.5,
      str(_ed.get("la_tendance_observee")))
    # ⚠⚠⚠ LA REGLE REFUTEE A L'AIR JUSTE ET ELLE EST FAUSSE, ET C'EST MESURE PLUTOT QU'ARGUMENTE.
    # La fixture porte des bruits propres ALTERNES le long du treillis et AUCUNE dependance a la
    # distance : rebrasser les etiquettes reproduit cette structure, rebrasser les valeurs la
    # detruit, donc la seconde declare une tendance la ou il n'y en a pas. ⚠ Les bruits sont
    # INVENTES ici, et c'est assume : le role de cette fixture est d'exercer la branche, pas de
    # modeler le rouleau — l'etalon, lui, prend ceux que `212` a mesures.
    _alt = [0, 1, 4, 8, 16, 32]
    _bruits = {0: 1.0, 1: 5.0, 4: 1.2, 8: 4.5, 16: 1.1, 32: 5.5}
    _pa = les_paires_du_treillis(_alt)
    _col = list(range(601))
    _et, _va = 0, 0
    for _i in range(20):
        _g = 900 + 17 * _i
        _m = les_desaccords_par_paire(
            des_rangees_ecartees_fabriquees(_alt, 600, 1.5, 1.0, 0.0, _g, _bruits), _col, _pa)
        _et += int(bool(contre_les_etiquettes(_m, _alt, PERMUTATIONS,
                                              _g + 7).get("ca_croit_avec_lecartement")))
        _va += int(bool(contre_les_valeurs(_m, _alt, PERMUTATIONS,
                                           _g + 7).get("ca_croit_selon_la_regle_refutee")))
    v("★★★★ sur des bruits propres ALTERNÉS et AUCUNE distance, la règle réfutée déclare une "
      "tendance bien plus souvent que la bonne",
      _va > _et * 2, f"valeurs {_va}/20 contre étiquettes {_et}/20")
    v("★★★★ et la bonne règle, elle, reste sous sa garantie sur cette même matière",
      _et <= int(20 * GARANTIE_PAR_EPREUVE * 2.0) + 1, f"{_et}/20")
    v("★★★ la règle réfutée est CALCULÉE et publiée, jamais suivie",
      contre_les_valeurs(mes_poussees, positions, PERMUTATIONS, 11).get("decidable") is True
      and "ca_croit_selon_la_regle_refutee" in contre_les_valeurs(mes_poussees, positions,
                                                                  PERMUTATIONS, 11))
    v("★★★ des paires indécidables ne rendent aucune règle réfutée",
      not contre_les_valeurs({"decidable": False}, positions, 3, 5).get("decidable"))

    # ⭐⭐⭐⭐ LA REGLE PLUS PUISSANTE, PORTEE COMME CONTROLE NOMME. Elle lit les residus que le
    # triangle publie — jamais un second ajustement — et le verdict ne la suit PAS.
    _pu_plate = contre_les_residus(mes_plates, positions, PERMUTATIONS, 11)
    _pu_poussee = contre_les_residus(mes_poussees, positions, PERMUTATIONS, 11)
    v("★★★★ la règle plus puissante lit une matière POUSSÉE et y voit la croissance",
      _pu_poussee.get("decidable")
      and _pu_poussee.get("ca_croit_selon_la_regle_plus_puissante") is True,
      f"tendance {_pu_poussee.get('la_tendance_observee')}")
    # ⚠⚠⚠ LE RESIDU EST SIGNE, ET C'EST CE CONTROLE QUI LE DIT. Une croissance avec la distance
    # laisse des residus NEGATIFS aux petits ecartements et POSITIFS aux grands : la tendance
    # observee doit donc etre franchement positive. Une version qui prendrait l'AMPLEUR du residu
    # rendrait une tendance proche de zero — mesure, elle ne voyait plus rien du tout.
    v("★★★★ et sa tendance est FRANCHEMENT positive, ce qui dit que le résidu est SIGNÉ",
      (_pu_poussee.get("la_tendance_observee") or 0.0) > 0.5,
      str(_pu_poussee.get("la_tendance_observee")))
    v("★★★★ sur une matière PLATE elle ne déclare rien",
      _pu_plate.get("decidable")
      and _pu_plate.get("ca_croit_selon_la_regle_plus_puissante") is False,
      f"tendance {_pu_plate.get('la_tendance_observee')}")
    v("★★★★ elle est CALCULÉE et publiée sous son propre nom, jamais sous celui du verdict",
      "ca_croit_selon_la_regle_plus_puissante" in _pu_poussee
      and "ca_croit_avec_lecartement" not in _pu_poussee)
    v("★★★ elle dit ce qu'elle corrèle, pour qu'on ne la confonde pas avec la règle gardée",
      "SIGNÉ" in (_pu_poussee.get("ce_quelle_correle") or ""),
      str(_pu_poussee.get("ce_quelle_correle")))
    v("★★★ un triangle indécidable ne rend aucune règle plus puissante",
      not contre_les_residus({"decidable": True, "les_paires": [
          {"la_paire": [0, 1], "lecartement": 1, "le_desaccord_par_couture_en_voxels": 1.0,
           "les_coutures_communes": 40}]}, [0, 1], 3, 5).get("decidable"))
    # ⚠⚠⚠ ET LE REFUS « MOINS DE TROIS RESIDUS » DOIT ETRE ATTEIGNABLE, sinon c'est une branche
    # que rien n'exerce. Le triangle exige deja plus d'equations que d'inconnues, donc un manque de
    # PAIRES ne l'atteint jamais : il ne se declenche que quand des residus sont INDECIDABLES, ce
    # qu'un desaccord nul produit — son erreur d'echantillonnage vaut alors zero, donc son residu
    # ne se divise pas. Quatre rangees, six paires, quatre desaccords nuls : il en reste deux.
    _muettes = {"decidable": True, "les_paires": [
        {"la_paire": [a, b], "lecartement": abs(a - b), "les_coutures_communes": 40,
         "le_desaccord_par_couture_en_voxels": (2.0 if (a, b) in ((0, 1), (0, 2)) else 0.0)}
        for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]}
    _tri_muet = le_triangle_surdetermine(_muettes, [0, 1, 2, 3])
    v("★★★★ le triangle reste décidable quand des désaccords sont nuls, et leurs résidus non",
      _tri_muet.get("decidable")
      and sum(1 for x in (_tri_muet.get("les_residus_par_paire_en_erreurs") or {}).values()
              if x is None) == 4,
      str(_tri_muet.get("les_residus_par_paire_en_erreurs")))
    # ⚠⚠ LA SONDE PORTE SUR LA RAISON ET PAS SUR LE SEUL REFUS, et c'est un bris qui l'a imposé.
    # La corrélation de rangs rend déjà None sur deux points, donc le refus est DOUBLEMENT couvert
    # et « refusé ou non » ne peut pas distinguer les deux chemins : retirer la garde de compte
    # laissait la sonde verte. Ce qui les sépare est ce que le refus DIT — « moins de trois »
    # nomme la cause, « la tendance n'est pas calculable » nomme le symptôme.
    _refus_muet = contre_les_residus(_muettes, [0, 1, 2, 3], 3, 5)
    v("★★★★ et la règle plus puissante REFUSE alors en NOMMANT le compte, pas le symptôme",
      not _refus_muet.get("decidable")
      and "moins de trois" in (_refus_muet.get("raison") or ""),
      str(_refus_muet.get("raison")))
    # ⚠⚠ ET LE TRIANGLE PUBLIE SES RESIDUS PAR PAIRE, sinon la regle ci-dessus devrait les
    # recalculer et il y aurait DEUX ajustements additifs libres de diverger.
    _tri_pub = le_triangle_surdetermine(mes_poussees, positions)
    # ⚠⚠⚠ CHAQUE « PIRE » PORTE SA PROPRE PAIRE, ET C'EST LA SONDE QUI MANQUAIT. Le module a
    # publie pendant toute une tranche un residu en ERREURS sous le nom de la paire du residu
    # BRUT : les deux argmax ne coincident pas, puisque l'erreur d'echantillonnage varie avec la
    # longueur de chaque paire. Toutes les gardes etaient vertes et tous les nombres justes — seul
    # le NOM etait faux, ce que `R4-L19` designe comme pire qu'un nombre absent.
    # ⚠⚠⚠ LA MATIERE EST CHOISIE POUR QUE LES DEUX ARGMAX DIFFERENT, et un premier jet ne l'avait
    # pas fait : sur une fixture trop uniforme le pire brut et le pire en erreurs tombent sur la
    # MEME paire, donc un code qui les confond passe au vert.
    # ⚠⚠ ET CE QUI LES SEPARE EST LE CONTRASTE DE VALEUR, PAS CELUI DE LONGUEUR — un bris l'a
    # montre en retirant le second sans rien deplacer. L'erreur d'echantillonnage vaut
    # v*sqrt(2/(n-1)) : elle croit avec la VALEUR de la paire autant qu'avec sa longueur, donc une
    # paire forte normalise son residu vers le bas et une paire faible vers le haut. La paire
    # courte reste dans la fixture pour exercer ce chemin-la, mais elle n'est pas ce qui separe.
    # ⚠ La separation est ASSERTEE en nom ET en valeur avant d'etre utilisee : une fixture qui
    # cesserait de separer rendrait toute cette famille de controles incapable d'echouer.
    # ⚠⚠⚠ CINQ RANGEES, ET PAS QUATRE, ET C'EST STRUCTUREL. A quatre rangees l'ajustement additif
    # rend des residus EGAUX par paires complementaires — 0-3 et 1-2 portent le meme nombre — donc
    # echanger la valeur de l'une pour celle de l'autre ne deplace RIEN et aucun controle ne peut
    # le voir. Une fixture a quatre rangees etait donc incapable d'echouer sur ce point precis, et
    # un bris l'a montre. A cinq, la degenerescence tombe.
    _contraste = {"decidable": True, "les_paires": [
        {"la_paire": [a, b], "lecartement": abs(a - b),
         "le_desaccord_par_couture_en_voxels": sg, "les_coutures_communes": nn}
        for (a, b), sg, nn in zip(
            ((0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)),
            (2.0, 2.0, 6.0, 2.0, 2.0, 2.0, 2.0, 1.0, 2.0, 2.0),
            (240, 240, 240, 240, 240, 240, 240, 20, 240, 240))]}
    _tri_c = le_triangle_surdetermine(_contraste, [0, 1, 2, 3, 4])
    v("★★★★ la matière de contrôle SÉPARE les deux pires, sinon rien ne pourrait les confondre",
      _tri_c.get("decidable")
      and _tri_c.get("la_paire_du_pire_residu_en_voxels2") is not None
      and _tri_c.get("la_paire_du_pire_residu_en_erreurs") is not None
      and _tri_c.get("la_paire_du_pire_residu_en_voxels2")
      != _tri_c.get("la_paire_du_pire_residu_en_erreurs"),
      f"brut {_tri_c.get('la_paire_du_pire_residu_en_voxels2')} · "
      f"erreurs {_tri_c.get('la_paire_du_pire_residu_en_erreurs')}")
    # ⚠⚠ ET ELLE LES SEPARE AUSSI EN VALEUR, sans quoi echanger les deux ne deplacerait aucun
    # nombre : c'est la degenerescence qui a rendu la fixture a quatre rangees inutile.
    _rb0 = _tri_c.get("les_residus_par_paire_en_voxels2") or {}
    v("★★★★ ... et elle les sépare EN VALEUR aussi, pas seulement en nom",
      _tri_c.get("la_paire_du_pire_residu_en_voxels2") in _rb0
      and _tri_c.get("la_paire_du_pire_residu_en_erreurs") in _rb0
      and abs(abs(float(_rb0[_tri_c.get("la_paire_du_pire_residu_en_voxels2")]))
              - abs(float(_rb0[_tri_c.get("la_paire_du_pire_residu_en_erreurs")]))) > 1e-6,
      f"{_rb0.get(_tri_c.get('la_paire_du_pire_residu_en_voxels2'))} contre "
      f"{_rb0.get(_tri_c.get('la_paire_du_pire_residu_en_erreurs'))}")
    _rp = _tri_c.get("les_residus_par_paire_en_erreurs") or {}
    v("★★★★ la paire nommée pour le pire résidu EN ERREURS porte bien cette valeur",
      _tri_c.get("la_paire_du_pire_residu_en_erreurs") in _rp
      and _tri_c.get("le_pire_residu_en_erreurs") is not None
      and abs(abs(float(_rp[_tri_c.get("la_paire_du_pire_residu_en_erreurs")]))
              - float(_tri_c.get("le_pire_residu_en_erreurs"))) < 1e-9,
      f"{_tri_c.get('la_paire_du_pire_residu_en_erreurs')} "
      f"= {_tri_c.get('le_pire_residu_en_erreurs')}")
    v("★★★★ et aucune autre paire ne porte un résidu en erreurs plus grand",
      _tri_c.get("le_pire_residu_en_erreurs") is not None
      and max(abs(float(x)) for x in _rp.values() if x is not None)
      <= float(_tri_c.get("le_pire_residu_en_erreurs")) + 1e-9)
    v("★★★★ la paire du pire résidu BRUT porte elle aussi SA valeur, et pas celle de l'autre",
      _tri_c.get("le_pire_residu_en_voxels2") is not None
      and _tri_c.get("le_pire_residu_en_erreurs") is not None
      and abs(abs(float(_tri_c.get("le_pire_residu_en_voxels2")))
          - max(abs(float(x)) for x in (
              le_triangle_surdetermine(_contraste, [0, 1, 2, 3, 4]).get(
                  "les_residus_par_paire_en_erreurs") or {}).values()
              if x is not None)) > 1e-6,
      f"brut {_tri_c.get('le_pire_residu_en_voxels2')} vx² · "
      f"erreurs {_tri_c.get('le_pire_residu_en_erreurs')}")
    _rb = _tri_c.get("les_residus_par_paire_en_voxels2") or {}
    v("★★★★ la paire nommée pour le pire résidu BRUT porte bien CETTE valeur, dans SA table",
      _tri_c.get("la_paire_du_pire_residu_en_voxels2") in _rb
      and _tri_c.get("le_pire_residu_en_voxels2") is not None
      and abs(float(_rb[_tri_c.get("la_paire_du_pire_residu_en_voxels2")])
              - float(_tri_c.get("le_pire_residu_en_voxels2"))) < 1e-9,
      f"{_tri_c.get('la_paire_du_pire_residu_en_voxels2')} "
      f"= {_tri_c.get('le_pire_residu_en_voxels2')}")
    v("★★★★ et aucune autre paire ne porte un résidu brut plus grand en valeur absolue",
      _tri_c.get("le_pire_residu_en_voxels2") is not None
      and max(abs(float(x)) for x in _rb.values())
      <= abs(float(_tri_c.get("le_pire_residu_en_voxels2"))) + 1e-9)
    v("★★★ le nom AMBIGU a disparu : chaque pire porte son unité dans sa clef",
      "la_paire_du_pire_residu_en_voxels2" in _tri_c
      and "la_paire_du_pire_residu" not in _tri_c,
      str(_tri_c.get("la_paire_du_pire_residu_en_voxels2")))
    v("★★★★ le triangle publie un résidu par paire, et c'est le seul producteur qui les rende",
      len(_tri_pub.get("les_residus_par_paire_en_erreurs") or {})
      == _tri_pub.get("combien_dequations"),
      f"{len(_tri_pub.get('les_residus_par_paire_en_erreurs') or {})} pour "
      f"{_tri_pub.get('combien_dequations')}")
    v("★★★ moins de trois paires ne rendent aucune épreuve",
      not contre_les_etiquettes({"decidable": True, "les_paires": [
          {"la_paire": [0, 1], "lecartement": 1, "le_desaccord_par_couture_en_voxels": 1.0}]},
          [0, 1], 3, 5)["decidable"])
    v("★★★ des paires indécidables ne rendent aucune épreuve",
      not contre_les_etiquettes({"decidable": False}, positions, 3, 5)["decidable"])

    # ⭐⭐⭐⭐ LE TRIANGLE EST SUR-DETERMINE, DONC IL PEUT ENFIN REFUTER.
    tr_0 = le_triangle_surdetermine(mes_plates, positions)
    tr_p = le_triangle_surdetermine(mes_poussees, positions)
    v("★★★★ à six rangées le triangle porte quinze équations pour six inconnues",
      tr_0.get("decidable") and tr_0.get("combien_dequations") == 15
      and tr_0.get("combien_dinconnues") == 6,
      f"{tr_0.get('combien_dequations')} pour {tr_0.get('combien_dinconnues')}")
    v("★★★★ sur une matière ADDITIVE ses résidus tiennent aux erreurs d'échantillonnage",
      tr_0.get("le_modele_tient_aux_erreurs") is True,
      str(tr_0.get("le_pire_residu_en_erreurs")))
    v("★★★★ sur une matière qui se DÉCORRÈLE il les dépasse — c'est la réfutation que `212` "
      "ne pouvait pas porter",
      tr_p.get("decidable") and tr_p.get("le_modele_tient_aux_erreurs") is False,
      str(tr_p.get("le_pire_residu_en_erreurs")))
    # ⚠⚠ ET IL RETROUVE LE BRUIT PROPRE POSE : sans ca, « les residus tiennent » serait satisfait
    # par un ajustement qui tient bien n'importe quoi de faux.
    propres = [float(x) for x in (tr_0.get("les_bruits_propres_en_voxels2") or {}).values()]
    v("★★★★ et il RETROUVE le bruit propre posé, donc il n'ajuste pas n'importe quoi",
      bool(propres) and all(abs(np.sqrt(max(x, 0.0)) - 2.0) < 0.2 for x in propres),
      str([round(float(np.sqrt(max(x, 0.0))), 3) for x in propres]))
    # ⚠⚠⚠ L'ERREUR EST DERIVEE DU NOMBRE DE COUTURES, ET ÇA SE MESURE : lire le MEME desaccord sur
    # moitie moins de coutures double presque la variance de l'estimation, donc le meme residu doit
    # valoir racine de deux fois MOINS d'erreurs. Une erreur fixee rendrait exactement le meme
    # nombre, et « le modele tient » serait vrai ou faux pour une raison qui n'est pas la mesure.
    _moitie = {"decidable": True, "les_paires": [
        dict(q, les_coutures_communes=max(3, int(q["les_coutures_communes"]) // 2))
        for q in mes_poussees["les_paires"]]}
    _tm = le_triangle_surdetermine(_moitie, positions)
    _r1 = tr_p.get("le_pire_residu_en_erreurs")
    _r2 = _tm.get("le_pire_residu_en_erreurs")
    v("★★★★ l'erreur du triangle est DÉRIVÉE des coutures : moitié moins de coutures, racine de "
      "deux fois moins d'erreurs pour le même résidu",
      _r1 and _r2 and abs(_r1 / _r2 - np.sqrt(2.0)) < 0.05,
      f"{_r1} contre {_r2} — rapport {round(_r1 / _r2, 4) if (_r1 and _r2) else None}")
    # ⚠⚠⚠ UNE VARIANCE NEGATIVE REFUTE LE MODELE AVANT TOUT RESIDU, parce qu'aucune decomposition
    # en somme de carres ne peut la produire. La fixture est impossible sous le modele et le DIT :
    # une rangee s'accorde avec TOUTES les autres pendant que les autres se disputent entre elles.
    _imp = {"decidable": True, "les_paires": [
        {"la_paire": [a, b], "lecartement": abs(b - a), "les_coutures_communes": 200,
         "le_desaccord_par_couture_en_voxels": (1.0 if a == 0 else 4.4721)}
        for i, a in enumerate([0, 1, 2, 3]) for b in [0, 1, 2, 3][i + 1:]]}
    _ti = le_triangle_surdetermine(_imp, [0, 1, 2, 3])
    v("★★★★ une rangée qui s'accorde avec TOUTES pendant que les autres se disputent rend une "
      "variance NÉGATIVE, et le modèle est réfuté",
      _ti.get("le_modele_est_refute_par_une_variance_negative") is True
      and _ti.get("les_rangees_a_variance_negative") == [0],
      str(_ti.get("les_bruits_propres_en_voxels2")))
    v("★★★ toutes les variances sont positives sur une matière saine",
      tr_0.get("le_modele_est_refute_par_une_variance_negative") is False)
    # ⚠⚠⚠ A TROIS RANGEES IL N'Y A RIEN A SUR-DETERMINER, ET LE REFUS EST EXPLICITE — c'est
    # exactement la limite que `212` avait et qu'il faut refuser de faire disparaitre en silence.
    tr3 = le_triangle_surdetermine(
        les_desaccords_par_paire({k: plates[k] for k in (0, 1, 4)}, col_f,
                                 les_paires_du_treillis([0, 1, 4])), [0, 1, 4])
    v("★★★★ à TROIS rangées il refuse : trois équations pour trois inconnues ne réfutent rien",
      not tr3.get("decidable"), str(tr3.get("raison")))

    # ⭐⭐⭐ LE CONTROLE DE LONGUEUR EST NOMME, PAS SUPPOSE ABSENT.
    lg = ce_que_la_longueur_fait(mes_plates)
    v("★★★★ sur une fixture sans trous, la longueur ne suit PAS l'écartement",
      lg.get("decidable") and lg.get("la_tendance_de_la_longueur") is None,
      str(lg.get("la_tendance_de_la_longueur")))
    v("★★★ et elle publie la longueur la plus courte à côté de la plus longue",
      lg.get("les_coutures_communes_les_moins_nombreuses") is not None
      and lg.get("les_coutures_communes_les_plus_nombreuses") is not None)
    v("★★★ des paires indécidables ne rendent aucun contrôle de longueur",
      not ce_que_la_longueur_fait({"decidable": False}).get("decidable"))

    # ⭐⭐⭐⭐ LE VERDICT PUBLIE LES DEUX LECTURES COTE A COTE, ET N'EN FOND AUCUNE.
    j0 = juger(mes_plates, ep_0, tr_0, lg, {"le_desaccord_par_couture_en_voxels": 2.7138})
    jp = juger(mes_poussees, ep_p, tr_p, ce_que_la_longueur_fait(mes_poussees),
               {"le_desaccord_par_couture_en_voxels": 2.7138})
    v("★★★★ sur une matière additive, la hauteur reste gratuite",
      j0.get("decidable") and j0.get("la_hauteur_reste_gratuite") is True,
      f"croît {j0.get('le_bruit_croit_avec_lecartement')} · tient "
      f"{j0.get('le_modele_additif_tient')}")
    v("★★★★ sur une matière qui se décorrèle, elle ne l'est PLUS",
      jp.get("decidable") and jp.get("la_hauteur_reste_gratuite") is False,
      f"croît {jp.get('le_bruit_croit_avec_lecartement')} · tient "
      f"{jp.get('le_modele_additif_tient')}")
    # ⚠⚠ LA GRATUITE EXIGE LES DEUX LECTURES : une tendance absente ne suffit pas si le triangle
    # casse, parce que le modele peut ceder autrement que par la distance.
    v("★★★★ une tendance absente ne suffit PAS si le triangle casse — les deux lectures comptent",
      juger(mes_plates, ep_0, dict(tr_0, le_modele_tient_aux_erreurs=False), lg,
            {}).get("la_hauteur_reste_gratuite") is False)
    v("★★★★ une variance NÉGATIVE refuse la gratuité même si tout le reste tient",
      juger(mes_plates, ep_0,
            dict(tr_0, le_modele_est_refute_par_une_variance_negative=True), lg,
            {}).get("la_hauteur_reste_gratuite") is False)
    # ⚠⚠⚠ ET « CE QUI RESTE A MESURER » LIT LES MEMES TROIS REPONSES QUE LA GRATUITE. Sans cela le
    # champ ne branchait que sur la tendance : il repondait « RIEN DE CETTE PORTE » en justifiant
    # par « seules les deux rangees extremes coutent quelque chose » — l'enonce MEME du modele
    # additif — pendant que le triangle refutait ce modele. La regle composee n'etait exercee par
    # rien, et c'est exactement la case que le vrai rouleau occupe.
    v("★★★★ les trois sorties de « ce qui reste » sont exclusives, et la règle se sonde seule",
      len({_ce_qui_reste(True, True, False),
           _ce_qui_reste(False, True, False),
           _ce_qui_reste(False, False, False)}) == 3
      and _ce_qui_reste(False, True, True) == _ce_qui_reste(False, False, False),
      _ce_qui_reste(False, False, False))
    j_casse = juger(mes_plates, ep_0, dict(tr_0, le_modele_tient_aux_erreurs=False), lg, {})
    v("★★★★ une tendance absente avec un triangle cassé NE ferme PAS la porte",
      j_casse.get("ce_qui_reste_a_mesurer") != j0.get("ce_qui_reste_a_mesurer")
      and "extrêmes" not in (j_casse.get("pourquoi_il_reste_a_mesurer") or ""),
      str(j_casse.get("ce_qui_reste_a_mesurer")))
    v("★★★★ ce qui reste à mesurer et POURQUOI sont deux champs, jamais une phrase",
      j0.get("ce_qui_reste_a_mesurer") not in (j0.get("pourquoi_il_reste_a_mesurer") or "")
      and jp.get("ce_qui_reste_a_mesurer") != j0.get("ce_qui_reste_a_mesurer")
      and len(j0.get("ce_qui_reste_a_mesurer") or "") < 60)
    v("★★★ le verdict publie l'échelle des écartements AVANT sa conclusion",
      j0.get("lechelle_des_ecartements") == [1, 32], str(j0.get("lechelle_des_ecartements")))
    v("★★★ il publie le désaccord au plus PETIT et au plus GRAND écartement, avec leurs longueurs",
      (j0.get("au_plus_petit_ecartement") or {}).get("lecartement") == 1
      and (j0.get("au_plus_grand_ecartement") or {}).get("lecartement") == 32
      and (j0.get("au_plus_petit_ecartement") or {}).get("les_coutures_communes") is not None)
    v("★★★ une épreuve sans verdict laisse la gratuité indécidée plutôt que de la trancher",
      juger(mes_plates, {"decidable": False}, tr_0, lg, {}).get("la_hauteur_reste_gratuite") is None)
    v("★★★ des mesures indécidables ne rendent aucun verdict",
      not juger({"decidable": False}, ep_0, tr_0, lg, {}).get("decidable"))

    # ⚠⚠⚠ LES DEUX NOMBRES DE L'ETALON SE RELISENT OU SE REFUSENT. Ils etaient TAPES en repli, et
    # ils se trouvaient justes — la pire facon d'avoir raison, parce qu'un producteur qui ne tourne
    # pas laisse alors l'etalon se poser sur des nombres que rien ne rattache a une mesure.
    v("★★★★ le lecteur de `208` lit sous `le_verdict`, là où `208` écrit vraiment",
      (ce_que_la_voisine_a_rendu(CE_QUE_LA_VOISINE_A_RENDU).get("la_derive_partagee_en_voxels")
       is not None)
      if CE_QUE_LA_VOISINE_A_RENDU.exists() else True,
      str(ce_que_la_voisine_a_rendu(CE_QUE_LA_VOISINE_A_RENDU).get(
          "la_derive_partagee_en_voxels")))
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _d:
        _vide = Path(_d) / "une_rangee_voisine_lit_elle_le_meme_pas.json"
        _vide.write_text(json.dumps({"le_verdict": {"le_bruit_de_la_mediane_en_voxels": 1.9}}))
        _lu = ce_que_la_voisine_a_rendu(_vide)
        v("★★★★ un `208` sans dérive partagée est REFUSÉ, jamais rendu décidable et vide",
          not _lu.get("decidable") and "dérive" in (_lu.get("raison") or ""),
          str(_lu.get("raison")))
    v("★★★★ sans `211`, aucun étalon n'est posable — et rien n'est tapé à sa place",
      not ce_quon_peut_poser({"decidable": False}, {
          "decidable": True, "la_derive_partagee_en_voxels": 1.5129}).get("decidable"))
    v("★★★★ sans `208` non plus",
      not ce_quon_peut_poser({"decidable": True,
                              "le_desaccord_par_couture_en_voxels": 2.7138},
                             {"decidable": False}).get("decidable"))
    v("★★★★ avec les deux, les nombres posés sont CEUX DES PRODUCTEURS, à la décimale",
      ce_quon_peut_poser({"decidable": True, "le_desaccord_par_couture_en_voxels": 2.7138},
                         {"decidable": True, "la_derive_partagee_en_voxels": 1.6758})
      == {"decidable": True, "le_desaccord_de_211_en_voxels": 2.7138,
          "la_derive_partagee_de_208_en_voxels": 1.6758})

    # ⭐⭐⭐⭐ L'ETALON TRAVERSE LE CHEMIN COMPLET, ET SA FACE POSITIVE EST UNE ECHELLE.
    # ⚠⚠⚠ LES BRUITS PROPRES SONT CEUX QUE `212` A MESURES, ET SANS EUX L'EXAMEN EST TRUQUE : avec
    # un bruit propre uniforme le seul ecart entre paires vient de la distance, donc l'epreuve la
    # voit sans effort. La sonde l'a mesure — le facteur deux passe de douze sur douze a huit sur
    # douze des que l'heterogeneite mesuree entre en jeu.
    hetero = les_bruits_propres_poses(sym, {"decidable": True,
                                            "les_bruits_propres_en_voxels": [1.5295, 2.2417,
                                                                             2.5568]})
    v("★★★★ les bruits propres de l'étalon sont ceux que `212` a MESURÉS, et ils sont hétérogènes",
      hetero is not None and len(set(hetero.values())) == 3, str(hetero))
    # ⚠⚠⚠ ET LA FIXTURE LES EMPLOIE REELLEMENT : sans cette sonde, `propres` pourrait etre ignore
    # et l'etalon redeviendrait trop facile sans que rien ne le dise.
    _pose = {0: 1.0, 4: 1.0, 7: 1.0, 8: 6.0, 9: 1.0, 12: 1.0, 16: 1.0}
    _r = des_rangees_ecartees_fabriquees(sym, 3000, 0.0, 1.0, 0.0, 5, _pose)
    _d8 = float(np.std([_r[8][c] for c in _r[8]]))
    _d0 = float(np.std([_r[0][c] for c in _r[0]]))
    v("★★★★ la fixture emploie RÉELLEMENT le bruit propre de chaque rangée, pas un bruit uniforme",
      abs(_d8 / _d0 - 6.0) < 0.5, f"{_d8:.3f} contre {_d0:.3f} — rapport {_d8 / _d0:.3f}")
    v("★★★ une rangée sans bruit posé retombe sur le bruit uniforme",
      abs(float(np.std([des_rangees_ecartees_fabriquees(sym, 3000, 0.0, 2.0, 0.0, 5,
                                                        {8: 6.0})[0][c]
                        for c in range(3000)])) - 2.0) < 0.15)
    v("★★★ un producteur absent laisse la fixture uniforme au lieu d'inventer une hétérogénéité",
      les_bruits_propres_poses(sym, {"decidable": False}) is None)
    et = sur_letalon(sym, 240, 2.7138, 1.5129, GRAINE, 6, propres=hetero)
    v("★★★★ l'étalon SÉPARE : une croissance assez forte est vue partout, et l'absence de "
      "croissance ne l'est nulle part",
      et.get("decidable") and et.get("letalon_separe"),
      f"plus petit facteur {et.get('le_plus_petit_facteur_vu')} · faux "
      f"{et.get('le_taux_de_faux')} · aveugle {et.get('le_taux_du_controle_aveugle')}")
    # ⭐⭐⭐⭐ ET C'EST LA SENSIBILITE QUI FAIT D'UN RESULTAT NEGATIF UNE BORNE PLUTOT QU'UN SILENCE.
    v("★★★★ la face positive est une ÉCHELLE et publie le PLUS PETIT facteur vu sur tous les "
      "réplicats",
      et.get("le_plus_petit_facteur_vu") in LES_FACTEURS
      and len(et.get("lechelle_de_sensibilite") or []) == len(LES_FACTEURS),
      str(et.get("le_plus_petit_facteur_vu")))
    v("★★★★ et le compte vu le long de l'échelle est MONOTONE — une sensibilité qui régresserait "
      "quand la croissance augmente serait un défaut, pas un résultat",
      et.get("la_sensibilite_est_monotone") is True,
      str([b["les_vus"] for b in (et.get("lechelle_de_sensibilite") or [])]))
    v("★★★ chaque barreau publie la croissance qu'il pose ET ce qu'elle annonce au plus grand "
      "écartement",
      all(b.get("la_croissance_en_voxels") is not None
          and b.get("ce_quelle_annonce_au_plus_grand_ecartement_en_voxels") is not None
          for b in (et.get("lechelle_de_sensibilite") or [{}])))
    # ⚠⚠⚠ LES DEUX REGLES SE SONDENT SANS COURIR UN ETALON, donc casser l'une rougit meme quand
    # la mesure du jour ne la fait pas jouer. Un taux EXACTEMENT egal a la garantie doit passer :
    # l'exiger a zero est la faute que `211` a payee sur du code juste.
    v("★★★★ un taux de faux ÉGAL à la garantie est toléré — l'exiger à zéro refuserait un étalon "
      "sain",
      le_taux_tient(GARANTIE_PAR_EPREUVE) is True and le_taux_tient(0.0) is True)
    v("★★★★ et un taux de trois fois la garantie est refusé",
      le_taux_tient(GARANTIE_PAR_EPREUVE * 3.0) is False
      and le_taux_tient(GARANTIE_PAR_EPREUVE * 2.0) is True)
    v("★★★ un taux absent ne tient pas", le_taux_tient(None) is False)
    v("★★★★ la monotonie est CALCULÉE : une suite qui régresse n'est pas monotone",
      la_suite_est_monotone([1, 2, 2, 3]) is True
      and la_suite_est_monotone([1, 3, 2, 3]) is False
      and la_suite_est_monotone([]) is True)
    v("★★★★ et le drapeau publié par l'étalon est celui que la règle rend sur SON échelle",
      et.get("la_sensibilite_est_monotone")
      == la_suite_est_monotone([b["les_vus"]
                                for b in (et.get("lechelle_de_sensibilite") or [])]))
    # ⚠⚠⚠ LE BARREAU NOMME DOIT ETRE VU SUR TOUS LES REPLICATS, et les deux champs publies doivent
    # s'accorder : sinon « le plus petit facteur vu » designerait un barreau que l'epreuve ne voit
    # qu'une fois sur douze, et la borne publiee serait une fiction.
    _nomme = [b for b in (et.get("lechelle_de_sensibilite") or [])
              if b["le_facteur"] == et.get("le_plus_petit_facteur_vu")]
    v("★★★★ le barreau NOMMÉ comme le plus petit vu l'est sur TOUS les réplicats",
      len(_nomme) == 1 and int(_nomme[0]["les_vus"]) >= int(_nomme[0]["replicats"]),
      str(_nomme))
    v("★★★★ et aucun barreau PLUS PETIT ne l'était",
      all(int(b["les_vus"]) < int(b["replicats"])
          for b in (et.get("lechelle_de_sensibilite") or [])
          if b["le_facteur"] < (et.get("le_plus_petit_facteur_vu") or 0)))
    v("★★★★ le compte du refus est celui que `210` a DÉRIVÉ de la garantie, jamais choisi",
      et.get("les_replicats_du_refus")
      == les_replicats_du_refus(GARANTIE_PAR_EPREUVE)["le_compte_decisif"],
      str(et.get("les_replicats_du_refus")))
    v("★★★★ le taux de faux tient la garantie sur le compte dérivé",
      et.get("le_taux_de_faux") is not None
      and et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('le_taux_de_faux')} contre {round(GARANTIE_PAR_EPREUVE * 2.0, 4)}")
    v("★★★★ une dérive PARTAGÉE, même dix fois plus forte, reste INVISIBLE",
      et.get("une_derive_partagee_reste_invisible") is True,
      str(et.get("le_taux_du_controle_aveugle")))
    # ⚠⚠⚠ ET LE CONTROLE AVEUGLE PEUT TIRER : un controle qui ne pourrait jamais se declencher ne
    # prouverait rien. En lui donnant une VRAIE croissance il DOIT la voir, et l'etalon DOIT
    # cesser de separer — c'est la sonde structurelle, pas une consequence.
    et_a = sur_letalon(sym, 240, 2.7138, 1.5129, GRAINE, 6,
                       aveugle_croissance=2.7138 * np.sqrt(8.0) / np.sqrt(16),
                       propres=hetero, facteurs=(9,))
    v("★★★★ mais il TIRE dès qu'on lui donne une vraie croissance — donc il peut échouer",
      et_a.get("decidable") and et_a.get("une_derive_partagee_reste_invisible") is False
      and et_a.get("letalon_separe") is False,
      str(et_a.get("le_taux_du_controle_aveugle")))
    # ⚠⚠⚠ ET LA FACE NEGATIVE PEUT TIRER, SINON LA CONJONCTION DU VERDICT N'EST EXERCEE PAR RIEN
    # DE CE COTE : sur du code sain le taux de faux sort a zero, donc retirer sa lecture laisserait
    # l'etalon separer quand meme. En mettant une VRAIE croissance dans la face qui n'est pas
    # censee en porter, le taux DOIT depasser et le verdict DOIT cesser de separer.
    et_f = sur_letalon(sym, 240, 2.7138, 1.5129, GRAINE, 6,
                       propres=hetero, facteurs=(9,),
                       refus_croissance=2.7138 * np.sqrt(8.0) / np.sqrt(16))
    v("★★★★ la face négative TIRE dès qu'on y met une vraie croissance — donc elle peut échouer",
      et_f.get("decidable") and et_f.get("le_taux_de_faux", 0.0) > GARANTIE_PAR_EPREUVE * 2.0
      and et_f.get("letalon_separe") is False,
      str(et_f.get("le_taux_de_faux")))
    v("★★★ et la croissance posée sur la face négative est publiée, pas cachée",
      et.get("la_croissance_posee_sur_la_face_negative_en_voxels") == 0.0
      and (et_f.get("la_croissance_posee_sur_la_face_negative_en_voxels") or 0.0) > 0.0)
    v("★★★ un jeu de positions trop court ne rend aucun étalon",
      not sur_letalon([0, 1], 100).get("decidable"))
    v("★★★ un facteur qui ne pose aucune croissance est écarté de l'échelle",
      not la_croissance_derivee(2.7138, 16, 1.0).get("decidable"))

    # ⭐⭐ CE QUE `211` A PUBLIE EST RELU, JAMAIS RETAPE.
    lu = ce_que_laccord_a_rendu()
    if lu.get("decidable"):
        v("★★★★ le niveau que la prédiction annonce plat vient de `211`, à l'écartement UN",
          lu.get("lecartement_de_211") == 1
          and (lu.get("le_desaccord_par_couture_en_voxels") or 0.0) > 0.0,
          f"{lu.get('le_desaccord_par_couture_en_voxels')} à l'écartement "
          f"{lu.get('lecartement_de_211')}")
    # ⚠⚠⚠ RELU VEUT DIRE RELU : une constante tapee ici aurait exactement le meme air tant que le
    # producteur porte le meme nombre. La sonde ecrit un producteur qui en porte un AUTRE.
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as _d:
        _faux = Path(_d) / "faux_211.json"
        _faux.write_text(json.dumps({"la_paire_declaree": [40, 41],
                                     "ce_que_les_desaccords_valent": {"40-41": {
                                         "le_desaccord_par_couture_mesure_en_voxels": 9.8765,
                                         "les_coutures_communes": 77}}}))
        _lu = ce_que_laccord_a_rendu(_faux)
        v("★★★★ le niveau annoncé plat est RELU chez `211`, jamais tapé ici",
          _lu.get("decidable")
          and abs((_lu.get("le_desaccord_par_couture_en_voxels") or 0.0) - 9.8765) < 1e-9
          and _lu.get("lecartement_de_211") == 1,
          str(_lu.get("le_desaccord_par_couture_en_voxels")))
        _vide = Path(_d) / "vide_211.json"
        _vide.write_text(json.dumps({"la_paire_declaree": [40, 41],
                                     "ce_que_les_desaccords_valent": {}}))
        v("★★★ un `211` qui ne publie pas sa paire déclarée est dit, pas comblé",
          not ce_que_laccord_a_rendu(_vide).get("decidable"))
    v("★★★ un producteur absent est dit, pas remplacé par une constante",
      not ce_que_laccord_a_rendu(Path("/absent/211.json")).get("decidable"))
    v("★★★ un producteur illisible est dit aussi",
      not ce_que_la_voisine_a_rendu(Path("/absent/208.json")).get("decidable"))

    # ⚠⚠⚠ ET LA MESURE COMPLETE TRAVERSE TOUT LE CHEMIN SUR UN FAUX DEPOT, parce qu'une chaine
    # dont chaque maillon est sonde separement peut encore etre mal cablee.
    meta = {"chunks": [109, 12, 12], "shape": [109, 480, 40]}
    _g = np.random.default_rng(31)
    _blocs = {cy: _g.normal(0.5, 0.2, size=(109, 12, 12)).astype(np.float32) for cy in range(40)}

    def _depot(cy, cx):
        """Un dépôt qui rend une matière DIFFÉRENTE par rangée — sinon le désaccord serait nul."""
        b = _blocs.get(int(cy))
        return ((b, None) if b is not None else (None, "absent du dépôt"))

    out = mesurer(0.0, GRAINE, 2, 4, _depot, meta, 4)
    v("★★★★ la mesure complète traverse les NEUF rangées écartées",
      len(out.get("les_pas_par_rangee") or {}) == 9, str(out.get("raison")))
    v("★★★★ elle publie une ligne par paire, et l'échelle va de un à trente-deux",
      (out.get("les_desaccords_par_paire") or {}).get("lecartement_le_plus_grand") == 32,
      str((out.get("les_desaccords_par_paire") or {}).get("les_ecartements_couverts")))
    v("★★★★ le triangle qu'elle publie est bien SUR-déterminé",
      (out.get("le_triangle_surdetermine") or {}).get("combien_dequations", 0)
      > (out.get("le_triangle_surdetermine") or {}).get("combien_dinconnues", 99),
      f"{(out.get('le_triangle_surdetermine') or {}).get('combien_dequations')} pour "
      f"{(out.get('le_triangle_surdetermine') or {}).get('combien_dinconnues')}")
    v("★★★ elle publie le contrôle de longueur à côté du verdict",
      (out.get("ce_que_la_longueur_fait") or {}).get("decidable") is True)
    v("★★★ elle publie la question déclarée et sa garantie",
      out.get("la_question_declaree") == LA_QUESTION_DECLAREE
      and out.get("la_garantie_par_epreuve") is not None)
    v("★★★ un volume qui ne répond pas est dit, pas deviné",
      not mesurer(0.0, GRAINE, 1, 4, _depot, {"chunks": [109, 12, 12], "shape": [109, 24, 40]},
                  4).get("decidable", True))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--delai", type=float, default=DELAI)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--replicats", type=int, default=12)
    p.add_argument("--colonnes", type=int, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.delai, a.graine, a.replicats, a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
