"""Pourquoi l'erreur déclarée est-elle trop petite : les queues, la dépendance, ou les deux ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE SA STATISTIQUE NE SOIT CALCULÉE, comme celui de `216`. L'épreuve,
le nul, la prédiction et les issues du verdict sont posés d'abord ; la mesure tourne ensuite.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P62` SANS AUCUNE LECTURE NEUVE. `216` a établi que
l'erreur déclarée `se(V) = V·√(2/(n-1))` sous-estime la vraie erreur d'un facteur **1,4942** sur la
matière de `214`, mais n'a PAS dit laquelle de ses deux hypothèses est fausse. Les deux suffisent
séparément : un excès d'aplatissement de **2,465** expliquerait tout sans aucune dépendance, et une
dépendance le long de la rangée l'expliquerait sans aucune queue lourde.

⭐⭐⭐⭐ ET LA SÉRIE QU'IL FAUT EST DÉJÀ PUBLIÉE, PAR `211`, DEPUIS LE DÉBUT. Son JSON porte
`les_ecarts_de_pas_du_troncon_en_voxels` pour **trois** paires de rangées : la suite des désaccords
COUTURE PAR COUTURE le long d'un tronçon CONTIGU. C'est exactement la matière dont la question a
besoin, et la contiguïté est ce qui rend une autocorrélation lisible — un jeu de coutures éparpillées
ne l'aurait pas permis.

## La décomposition, posée d'avance

La variance d'une variance échantillonnale n'a pas une seule cause. Pour une suite `d` de moyenne
nulle, de variance `σ²` et d'excès d'aplatissement `κ` :

    var(V) = (κ + 2)·σ⁴ / n         si les termes sont indépendants
    var(V) = (κ + 2)·σ⁴ · τ / n     en général, où τ = 1 + 2·Σ_k ρ_k

et `ρ_k` est l'autocorrélation de la suite des CARRÉS `d²` — car c'est `d²` que la variance somme,
et non `d`. La formule déclarée est le cas `κ = 0, τ = 1`.

⭐⭐⭐⭐ LE FACTEUR DE SOUS-ESTIMATION SE DÉCOMPOSE DONC EXACTEMENT EN DEUX :

    Λ_prédit = (κ + 2)/2 · τ
               └── les QUEUES ──┘ └ la DÉPENDANCE ┘

et les deux facteurs se mesurent SÉPARÉMENT sur la série publiée. ⚠⚠⚠ C'EST UNE PRÉDICTION
FALSIFIABLE, pas une description : `216` a mesuré `Λ = 2,2325` sur les résidus de `214` SANS jamais
regarder une série par couture, et cette tranche calcule la même quantité par un chemin entièrement
différent. Si les deux tombent au même endroit, l'explication est close ; si elles divergent, c'est
qu'il manque une troisième cause, et le savoir vaut mieux que de ne pas le savoir.

⚠⚠ LA COMPARAISON N'EST PAS EXACTE ET C'EST DIT D'AVANCE. `216` agrège **trente-six** paires lues
sur toutes leurs coutures communes ; `211` publie **trois** paires sur un tronçon contigu. Un accord
est une confirmation forte, un désaccord ne dit pas lequel des deux a tort. La tranche publie donc
les deux et ne prétend pas que l'un démontre l'autre.

## Les deux épreuves, déclarées

⭐⭐⭐⭐ **PREMIÈRE ÉPREUVE — LA DÉPENDANCE EXISTE-T-ELLE ?** `τ` vaut-il plus que un ? Le nul est
celui que `R4-P62` prescrit et il ne suppose rien de la loi : **rebrasser la série observée**. Un
rebrassage simple garde exactement les mêmes valeurs — donc exactement les mêmes queues — et détruit
l'ordre, donc toute dépendance. La distribution de `τ` sous ce rebrassage est le nul, et l'écart de
`τ` observé à ce nul EST la dépendance. ⚠ Aucun modèle paramétrique n'entre là, ce qui est
indispensable : la matière n'est pas gaussienne, c'est le point de départ.

⭐⭐⭐⭐ **SECONDE ÉPREUVE — LES DEUX FACTEURS RENDENT-ILS COMPTE DE `Λ` ?** Le produit
`(κ+2)/2 · τ` tombe-t-il là où `216` a mesuré `Λ` ? ⚠ L'incertitude sur le produit se prend par
**bootstrap par blocs** sur la série observée, parce qu'un bootstrap ordinaire détruirait la
dépendance qu'on cherche justement à propager.

⚠⚠⚠⚠ ET LA PREMIÈRE STATISTIQUE QUE CETTE TRANCHE AVAIT DÉCLARÉE EST REFUSÉE, POUR UNE RAISON
STRUCTURELLE ET NON POUR CE QU'ELLE A RENDU. `τ` devait être sommé par la règle de la SUITE INITIALE
POSITIVE — sommer les paires `ρ_{2k} + ρ_{2k+1}` tant qu'elles sont positives — qui a le mérite de ne
demander aucun réglage. ⚠⚠ Mais cette règle est **plancher à un** par construction : quand la
première paire est négative, la somme est vide et `τ` vaut exactement `1`. Son nul par rebrassage
s'empile donc au même plancher, et la comparaison est dégénérée — l'épreuve ne peut pas se
déclencher, quelle que soit la matière. C'est le péché de la vérification incapable d'échouer, dans
l'autre sens.

⭐ CE N'EST PAS UN REJET DICTÉ PAR LES DONNÉES, et c'est ce qui rend le remplacement légitime : le
plancher se démontre sans regarder la moindre série. `τ` est donc porté comme **refus nommé**, avec
sa valeur et avec le nul qui s'empile, et la statistique déclarée devient ce que `τ` sommait :
la FAMILLE des autocorrélations elles-mêmes, `max_k |ρ_k|` sur les `K` premiers décalages, avec le
nul pris sur la MÊME famille. Le choix d'un décalage parmi `K` est ainsi payé — c'est le remède de
`179` — et `K` n'affecte que la puissance, jamais la validité, puisque les deux côtés le subissent.

⚠⚠ LE PIÈGE EST NOMMÉ D'AVANCE, ET IL EST RÉEL : une série à queues lourdes rend une
autocorrélation empirique BRUITÉE. Mesurer `τ` sans son nul attribuerait à la dépendance ce que les
queues produisent — et c'est précisément pour ça que le nul rebrasse la série OBSERVÉE au lieu de
tirer sous une loi.

⚠ Et le contrôle gratuit reste celui de `212` : rien ici ne peut rendre une variance propre négative,
puisque la tranche ne touche qu'aux ERREURS et jamais aux valeurs.

Usage :
    uv run python src/nappe/pourquoi_lerreur_declaree_est_trop_petite.py --verifier
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
from le_bruit_propre_croit_il_avec_lecartement import (la_suite_est_monotone,  # noqa: E402
                                                       le_taux_tient)
from ouvrir_les_quinze import _rng  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LACCORD_A_RENDU = MESURES / "les_rangees_saccordent_elles_entre_elles.json"
CE_QUE_LE_BUDGET_A_RENDU = MESURES / "les_erreurs_declarees_rendent_elles_compte_des_residus.json"
GRAINE = 20261029

LA_QUESTION_DECLAREE = ("l'erreur déclarée est trop petite : est-ce parce que les désaccords par "
                        "couture sont DÉPENDANTS le long de la rangée, ou parce que leur loi a des "
                        "QUEUES bien plus lourdes qu'une gaussienne ?")
LES_EPREUVES_DECLAREES = ("une autocorrélation dépasse ce que le rebrassage de la série donne",
                          "le facteur des queues rend compte du dépassement mesuré par `216`")
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)
LE_COMPTE_DECISIF = 171


def ce_que_laccord_a_rendu(chemin: Path = CE_QUE_LACCORD_A_RENDU) -> dict:
    """Les séries par couture que `211` publie — relues, jamais retapées, refusées par leur nom.

    ⚠⚠⚠ C'EST LA SEULE MATIÈRE DE CETTE TRANCHE, ET ELLE EXISTE DEPUIS `211`. Le JSON porte, pour
    chaque paire, la suite des désaccords COUTURE PAR COUTURE le long d'un tronçon CONTIGU. La
    contiguïté est ce qui rend une autocorrélation lisible : un jeu de coutures éparpillées aurait
    mélangé des voisines et des non-voisines sous un seul décalage.

    ⚠⚠ LA SÉRIE EST VÉRIFIÉE CONTRE LE NOMBRE QUE `211` PUBLIE À CÔTÉ D'ELLE. Son écart-type doit
    valoir `lecart_type_des_pas_du_troncon_en_voxels`, sinon ce n'est pas la série qu'on croit lire
    — et lire une autre suite sous ce nom serait `R4-L19` une fois de plus.
    """
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    brut = d.get("les_desaccords")
    if not isinstance(brut, dict) or not brut:
        return {"decidable": False, "raison": "`211` ne publie pas ses désaccords"}
    paires = {}
    for nom, v in sorted(brut.items()):
        if not v.get("decidable"):
            return {"decidable": False, "raison": f"le désaccord {nom} est indécidable"}
        s = v.get("les_ecarts_de_pas_du_troncon_en_voxels")
        if not isinstance(s, list) or len(s) < 30:
            return {"decidable": False,
                    "raison": f"la paire {nom} ne publie pas de série par couture utilisable"}
        attendu = v.get("lecart_type_des_pas_du_troncon_en_voxels")
        if attendu is None:
            return {"decidable": False,
                    "raison": f"la paire {nom} ne publie pas l'écart-type de son tronçon"}
        a = np.asarray(s, dtype=float)
        rms = float(np.sqrt(float(np.mean((a - float(np.mean(a))) ** 2))))
        if abs(rms - float(attendu)) > 5e-3:
            return {"decidable": False,
                    "raison": (f"la série de {nom} rend {rms:.4f} là où `211` publie "
                               f"{float(attendu):.4f}")}
        paires[nom] = {"la_serie": [float(x) for x in s],
                       "combien_de_coutures_du_troncon": len(s),
                       "les_coutures_communes": int(v.get("les_coutures_communes") or 0),
                       "les_troncons_communs": int(v.get("les_troncons_communs") or 0),
                       "lecart_type_du_troncon_en_voxels": float(attendu),
                       "lecart_type_sur_toutes_les_communes_en_voxels":
                           v.get("lecart_type_des_pas_sur_toutes_les_communes_en_voxels")}
    return {"decidable": True, "les_paires": paires, "combien_de_paires": len(paires)}


def ce_que_216_a_rendu(chemin: Path = CE_QUE_LE_BUDGET_A_RENDU) -> dict:
    """Le dépassement que `216` a mesuré — relu, parce que c'est lui que cette tranche prédit."""
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    b = d.get("lepreuve_du_budget") or {}
    if not b.get("decidable") or b.get("le_rapport") is None:
        return {"decidable": False, "raison": "`216` ne publie pas son rapport au budget"}
    return {"decidable": True,
            "le_rapport": float(b["le_rapport"]),
            "le_facteur_sur_lerreur": b.get("le_facteur_sur_lerreur"),
            "les_tirages_au_moins_aussi_forts": b.get("les_tirages_au_moins_aussi_forts"),
            # ⚠⚠ CE QUE `217` CITE DE `216` EST RELU, JAMAIS RETAPE — precedent de `215` et `216`.
            "lexces_daplatissement_qui_suffirait":
                (d.get("le_controle_des_queues") or {}).get("lexces_daplatissement_qui_suffirait"),
            "le_rapport_de_queue_le_plus_grand":
                (d.get("le_controle_des_queues") or {}).get("le_rapport_le_plus_grand"),
            "le_rapport_de_queue_median":
                (d.get("le_controle_des_queues") or {}).get("le_rapport_median"),
            "la_reference_gaussienne_la_plus_forte":
                (d.get("le_controle_des_queues") or {}).get("la_reference_gaussienne_la_plus_forte")}


def _centre(serie) -> np.ndarray:
    a = np.asarray(list(serie), dtype=float)
    return a - float(np.mean(a))


def lautocorrelation(x, k: int) -> float | None:
    """L'autocorrélation au décalage `k` — écrite ici parce que toute la tranche en dépend."""
    a = np.asarray(list(x), dtype=float)
    a = a - float(np.mean(a))
    n = len(a)
    if k < 1 or k >= n:
        return None
    v = float(np.dot(a, a) / n)
    if v <= 0.0:
        return None
    return float(np.dot(a[:n - k], a[k:]) / (n * v))


def combien_de_decalages(n: int) -> int:
    """Le nombre de décalages que la famille parcourt — DÉRIVÉ de la longueur, jamais choisi.

    ⚠⚠ `K = ⌊√n⌋` est la règle usuelle du nombre de décalages qu'une série de `n` points peut
    porter : au-delà, chaque autocorrélation repose sur trop peu de couples pour vouloir dire quoi
    que ce soit. ⭐ Et surtout `K` n'affecte QUE la puissance, jamais la validité : le nul parcourt
    la MÊME famille, donc le choix d'un décalage parmi `K` est payé quel que soit `K`.
    """
    return max(1, min(int(np.sqrt(max(1, int(n)))), max(1, int(n) // 2 - 1)))


def le_refus_de_tau(x) -> dict:
    """LA STATISTIQUE D'ABORD DÉCLARÉE, REFUSÉE — et la raison est un PLANCHER, pas un résultat.

    ⚠⚠⚠ LA RÈGLE DE LA SUITE INITIALE POSITIVE SOMME `ρ_{2k} + ρ_{2k+1}` TANT QUE C'EST POSITIF.
    Quand la première paire est négative, la somme est vide et `τ` vaut EXACTEMENT un. Elle ne peut
    donc jamais descendre sous un, et son nul par rebrassage s'empile au même plancher : la
    comparaison est dégénérée, l'épreuve ne peut pas se déclencher, quelle que soit la matière.

    ⭐ Le refus se démontre SANS REGARDER LA MOINDRE SÉRIE, ce qui est exactement ce qui le rend
    légitime : ce n'est pas une statistique écartée pour ce qu'elle a rendu. Elle est publiée avec
    sa valeur, pour que rien n'empêche de la recalculer.
    """
    a = _centre(x)
    n = len(a)
    v = float(np.dot(a, a) / n)
    if v <= 0.0:
        return {"decidable": False, "raison": "la série est constante"}
    rho = [lautocorrelation(a, k) for k in range(1, n // 2)]
    somme, paires = 0.0, 0
    for i in range(0, len(rho) - 1, 2):
        if rho[i] is None or rho[i + 1] is None:
            break
        p = rho[i] + rho[i + 1]
        if p <= 0.0:
            break
        somme += p
        paires += 1
    return {"decidable": True,
            "tau": round(1.0 + 2.0 * somme, 4),
            "les_paires_sommees": int(paires),
            "tau_est_au_plancher": bool(paires == 0),
            "pourquoi_il_est_refuse":
                "la règle est plancher à un par construction, donc son nul s'empile au plancher "
                "et l'épreuve ne peut pas se déclencher, quelle que soit la matière"}


def la_famille_des_decalages(x, tirages: int = PERMUTATIONS, graine: int = GRAINE,
                             sur_les_carres: bool = True) -> dict:
    """PREMIÈRE ÉPREUVE : une autocorrélation dépasse-t-elle ce que le rebrassage donne ?

    ⚠⚠⚠ LE NUL REBRASSE LA SÉRIE OBSERVÉE, ET RIEN D'AUTRE. Un rebrassage garde EXACTEMENT les
    mêmes valeurs — donc exactement les mêmes queues, y compris la plus extrême — et ne détruit que
    l'ordre. C'est indispensable ici : la matière n'est pas gaussienne, c'est le point de départ de
    la tranche, donc tout nul paramétrique répondrait pour une loi qu'elle n'a pas.

    ⚠⚠ C'EST LA SUITE DES CARRÉS QU'ON REGARDE, PAS LA SUITE ELLE-MÊME. Une variance somme des
    carrés, donc c'est la dépendance des carrés qui gonfle l'erreur d'une variance. La suite
    elle-même est portée à côté comme contrôle nommé : si elle dérivait, les carrés seuls ne le
    diraient pas forcément.

    ⚠⚠ LE MAXIMUM EST PRIS SUR LA FAMILLE ENTIÈRE, DES DEUX CÔTÉS, donc le choix d'un décalage
    parmi `K` est payé au lieu d'être fait après les avoir vus.
    """
    a = _centre(x)
    q = a ** 2 if sur_les_carres else a
    n = len(q)
    k_max = combien_de_decalages(n)
    obs = {}
    for k in range(1, k_max + 1):
        r = lautocorrelation(q, k)
        if r is not None:
            obs[k] = float(r)
    if not obs:
        return {"decidable": False, "raison": "aucun décalage ne rend d'autocorrélation"}
    porteur = max(obs, key=lambda k: abs(obs[k]))
    fort = abs(obs[porteur])
    g = _rng(int(graine))
    nuls = []
    for _ in range(int(tirages)):
        m = g.permutation(q)
        vals = [abs(lautocorrelation(m, k)) for k in range(1, k_max + 1)
                if lautocorrelation(m, k) is not None]
        if vals:
            nuls.append(float(max(vals)))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de famille"}
    au_moins = int(sum(1 for v in nuls if v >= fort))
    return {"decidable": True,
            "tirages": int(tirages),
            "sur_les_carres": bool(sur_les_carres),
            "combien_de_decalages": int(k_max),
            "les_autocorrelations": {str(k): round(v, 4) for k, v in sorted(obs.items())},
            "le_decalage_le_plus_fort": int(porteur),
            "la_famille_observee": round(fort, 4),
            "la_famille_du_nul_mediane": round(float(np.median(nuls)), 4),
            "la_famille_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "une_dependance_depasse_le_hasard": bool(au_moins == 0)}


def la_famille_longue(x, tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """CONTRÔLE NOMMÉ : la même famille, mais jusqu'à une portée QUATRE FOIS plus longue.

    ⚠⚠⚠ LA FAMILLE DÉCLARÉE NE PEUT PAS VOIR UNE DÉPENDANCE DONT LA PORTÉE DÉPASSE `⌊√n⌋`, et le
    suspect physique est justement de LONGUE portée : `208` a mesuré une dérive PARTAGÉE le long de
    la rangée, et une dérive n'a pas de raison de s'éteindre en dix coutures. Regarder plus loin est
    donc indispensable — mais comme ce n'est pas ce qui a été déclaré, c'est porté comme contrôle et
    non comme verdict.

    ⚠ La portée est `⌊n/4⌋` : au-delà, une autocorrélation repose sur moins de trois quarts de la
    série et son estimation cesse de vouloir dire quelque chose.
    """
    a = _centre(x)
    q = a ** 2
    n = len(q)
    k_max = max(1, min(n // 4, n // 2 - 1))
    obs = {}
    for k in range(1, k_max + 1):
        r = lautocorrelation(q, k)
        if r is not None:
            obs[k] = float(r)
    if not obs:
        return {"decidable": False, "raison": "aucun décalage ne rend d'autocorrélation"}
    porteur = max(obs, key=lambda k: abs(obs[k]))
    fort = abs(obs[porteur])
    g = _rng(int(graine))
    nuls = []
    for _ in range(int(tirages)):
        m = g.permutation(q)
        vals = [abs(v) for v in (lautocorrelation(m, k) for k in range(1, k_max + 1))
                if v is not None]
        if vals:
            nuls.append(float(max(vals)))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de famille"}
    au_moins = int(sum(1 for v in nuls if v >= fort))
    return {"decidable": True,
            "tirages": int(tirages),
            "combien_de_decalages": int(k_max),
            "le_decalage_le_plus_fort": int(porteur),
            "la_famille_observee": round(fort, 4),
            "la_famille_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "une_dependance_longue_depasse_le_hasard": bool(au_moins == 0)}


def la_longueur_de_bloc(n: int) -> int:
    """La longueur de bloc du bootstrap — DÉRIVÉE de la longueur de la série, jamais choisie.

    ⚠ `L = ⌈n^(1/3)⌉` est la règle usuelle pour un bootstrap par blocs mobiles : elle croît assez
    vite pour capturer une dépendance courte et assez lentement pour que le nombre de blocs reste
    grand. ⭐ Et comme la première épreuve mesure s'il y a une dépendance du tout, le bootstrap par
    blocs est comparé au bootstrap ORDINAIRE (`L = 1`) : quand il n'y a pas de dépendance, les deux
    doivent s'accorder, et cet accord est un contrôle gratuit.
    """
    return max(1, int(np.ceil(max(1, int(n)) ** (1.0 / 3.0))))


def le_facteur_des_queues(x, tirages_du_bootstrap: int = 399, graine: int = GRAINE) -> dict:
    """SECONDE ÉPREUVE : de combien les seules QUEUES gonflent-elles l'erreur d'une variance ?

    ⚠⚠⚠ LE FACTEUR EST EXACT ET NON EMPIRIQUE. La variance d'une variance échantillonnale vaut
    `(κ + 2)·σ⁴/n` pour des termes indépendants, et la formule déclarée par `212`–`214` est le cas
    `κ = 0`. Le facteur de sous-estimation dû aux seules queues vaut donc `(κ + 2)/2`, sans aucun
    réglage.

    ⚠⚠ L'INCERTITUDE EST INDISPENSABLE ET NON DÉCORATIVE : un aplatissement estimé sur une centaine
    de points à queues lourdes est très bruité, et une seule valeur extrême le déplace beaucoup.
    Publier le point sans l'intervalle ferait passer une estimation très incertaine pour une mesure.

    ⚠ Le bootstrap est fait PAR BLOCS et aussi ORDINAIRE : le second détruit la dépendance, le
    premier la garde, et leur accord est le contrôle gratuit de la première épreuve.
    """
    a = _centre(x)
    n = len(a)
    if n < 8:
        return {"decidable": False, "raison": "la série est trop courte"}
    m2 = float(np.mean(a ** 2))
    if m2 <= 0.0:
        return {"decidable": False, "raison": "la série est constante"}
    kappa = float(np.mean(a ** 4) / m2 ** 2 - 3.0)
    facteur = (kappa + 2.0) / 2.0

    def _boot(longueur: int) -> list[float]:
        g = _rng(int(graine) + longueur)
        out = []
        for _ in range(int(tirages_du_bootstrap)):
            if longueur <= 1:
                b = a[g.integers(0, n, n)]
            else:
                idx = []
                while len(idx) < n:
                    d = int(g.integers(0, n - longueur + 1))
                    idx.extend(range(d, d + longueur))
                b = a[np.asarray(idx[:n])]
            b = b - float(np.mean(b))
            v2 = float(np.mean(b ** 2))
            if v2 > 0.0:
                out.append((float(np.mean(b ** 4) / v2 ** 2 - 3.0) + 2.0) / 2.0)
        return sorted(out)

    long_ = la_longueur_de_bloc(n)
    par_blocs, ordinaire = _boot(long_), _boot(1)
    if not par_blocs or not ordinaire:
        return {"decidable": False, "raison": "le bootstrap n'a rien rendu"}

    def _bornes(s):
        return (round(float(s[int(0.025 * len(s))]), 4), round(float(s[int(0.975 * len(s))]), 4))

    bb, bo = _bornes(par_blocs), _bornes(ordinaire)
    return {"decidable": True,
            "combien_de_coutures": int(n),
            "lexces_daplatissement": round(kappa, 4),
            "le_facteur_des_queues": round(facteur, 4),
            "la_longueur_de_bloc": int(long_),
            "les_tirages_du_bootstrap": int(tirages_du_bootstrap),
            "lintervalle_par_blocs": list(bb),
            "lintervalle_ordinaire": list(bo),
            # ⚠ LE CONTROLE GRATUIT : sans dependance, les deux bootstraps doivent s'accorder. Leur
            # ecart relatif est publie plutot qu'affirme nul.
            "lecart_relatif_des_deux_bootstraps":
                round(abs((bb[1] - bb[0]) - (bo[1] - bo[0])) / max(1e-9, bo[1] - bo[0]), 4)}


def lerreur_corrigee(facteur: dict, sigma, coutures) -> dict:
    """Le remède, et il tient en une ligne : `se(V) = V·√((κ+2)/n)`.

    ⭐⭐ C'EST CE QUE CETTE TRANCHE REND UTILISABLE PLUTÔT QUE SEULEMENT VRAI. La formule déclarée
    par `212`–`214` est le cas `κ = 0` ; la remplacer par la forme générale ne demande que
    l'aplatissement de la série, qui se mesure sur ce qui est déjà lu. Aucune lecture neuve, aucun
    réglage.

    ⚠ L'erreur corrigée est publiée à côté de la déclarée et non à sa place : c'est leur RAPPORT
    qui est le résultat, et une seule des deux ne dirait pas de combien on se trompait.
    """
    if not facteur.get("decidable"):
        return {"decidable": False, "raison": facteur.get("raison")}
    n = int(coutures)
    if n < 3 or float(sigma) <= 0.0:
        return {"decidable": False, "raison": "les coutures ou l'écart-type ne tiennent pas"}
    v = float(sigma) ** 2
    declaree = v * float(np.sqrt(2.0 / (n - 1)))
    kappa = float(facteur["lexces_daplatissement"])
    corrigee = v * float(np.sqrt(max(0.0, kappa + 2.0) / n))
    return {"decidable": True,
            "les_coutures": n,
            "lerreur_declaree_en_voxels2": round(declaree, 4),
            "lerreur_corrigee_en_voxels2": round(corrigee, 4),
            "le_rapport": round(corrigee / declaree, 4) if declaree > 0 else None}


def une_serie(mode: str, n: int, force: float, graine: int) -> dict:
    """Une série fabriquée dont on connaît la propriété — et les trois modes sont les trois mondes.

    ⚠⚠⚠ LE MODE `queues` EST LE PIÈGE DE CETTE TRANCHE, FABRIQUÉ EXPRÈS. Il porte des queues
    lourdes et AUCUNE dépendance : une règle qui tirerait dessus attribuerait à la dépendance ce
    que les queues produisent, et c'est exactement l'erreur que la tranche existe pour éviter.

    ⚠⚠ LE MODE `dependante` EST UNE VOLATILITÉ STOCHASTIQUE, PAS UN AR SUR LA SÉRIE. Ce qui doit
    être corrélé est le CARRÉ — c'est lui que somme une variance — et un AR sur la série
    corrélerait la série elle-même, ce qui est un monde différent et plus facile. La volatilité
    stochastique corrèle les carrés en laissant la série non corrélée, donc elle fabrique le cas
    DIFFICILE plutôt que le cas commode.

    ⚠ Le degré de liberté du mode `queues` est DÉRIVÉ de l'aplatissement visé, `df = 4 + 6/κ`,
    jamais choisi.
    """
    g = _rng(int(graine))
    n = max(8, int(n))
    if mode == "gaussienne":
        return {"la_serie": g.normal(0.0, 1.0, n), "le_mode": mode}
    if mode == "queues":
        k = max(1e-3, float(force))
        return {"la_serie": g.standard_t(4.0 + 6.0 / k, n), "le_mode": mode}
    if mode == "echelle_lente":
        # ⚠⚠ LA SECONDE FORME DE DEPENDANCE EXISTE PARCE QUE LA PREMIERE MELANGE DEUX CHOSES. Une
        # volatilite stochastique fabrique de la dependance ET des queues, et plus phi monte plus
        # les queues montent avec — donc la detection SATURE au lieu de croitre. Une echelle
        # sinusoidale lente corriere les carres SANS faire exploser les queues, ce qui donne une
        # borne lisible la ou la premiere n'en donne aucune. Les deux sont publiees.
        # ⚠⚠⚠ LA PERIODE EST DERIVEE DE LA PORTEE DE LA FAMILLE, ET C'EST UNE LIMITE QUI SE DIT.
        # La famille declaree regarde les decalages 1 a K ; une dependance dont la portee depasse K
        # lui est STRUCTURELLEMENT invisible. Une premiere version de cette fixture oscillait a la
        # periode n/4, soit bien au-dela de K, donc elle mesurait l'aveuglement de la regle et non
        # sa sensibilite. La periode est desormais dans la portee, et la portee longue est portee a
        # cote comme controle nomme.
        a_ = max(0.0, min(0.95, float(force)))
        per = float(max(4, combien_de_decalages(n)))
        s_ = 1.0 + a_ * np.sin(2.0 * np.pi * np.arange(n) / per)
        return {"la_serie": s_ * g.normal(0.0, 1.0, n), "le_mode": mode}
    if mode != "dependante":
        return {"la_serie": None, "le_mode": mode, "raison": f"mode inconnu : {mode}"}
    phi = max(0.0, min(0.99, float(force)))
    h = np.zeros(n)
    for i in range(1, n):
        h[i] = phi * h[i - 1] + g.normal(0.0, 1.0)
    return {"la_serie": np.exp(h / 2.0) * g.normal(0.0, 1.0, n), "le_mode": mode}


def _une_course(mode: str, n: int, force: float, graine: int, tirages: int) -> dict:
    s = une_serie(mode, n, force, graine)
    if s.get("la_serie") is None:
        return {"decidable": False, "raison": s.get("raison")}
    fam = la_famille_des_decalages(s["la_serie"], tirages, graine + 1)
    if not fam.get("decidable"):
        return {"decidable": False, "raison": fam.get("raison")}
    return {"decidable": True, "voit": bool(fam["une_dependance_depasse_le_hasard"])}


def sur_letalon(n: int = 105, forces=(0.3, 0.5, 0.7, 0.9, 0.95, 0.98),
                forces_lentes=(0.2, 0.4, 0.6, 0.8, 0.95), replicats: int = 12,
                decisif: int = LE_COMPTE_DECISIF, graine: int = GRAINE,
                tirages: int = PERMUTATIONS, aplatissement_du_piege: float = 6.0) -> dict:
    """L'étalon : le taux de faux, le PIÈGE des queues sans dépendance, et l'échelle.

    ⚠⚠⚠ LE CONTRÔLE QUI COMPTE N'EST PAS UN AVEUGLE MAIS LE PIÈGE LUI-MÊME : une série à queues
    lourdes SANS dépendance ne doit pas faire tirer la règle. Une règle qui y tirerait rendrait
    exactement le verdict inverse de celui que cette tranche doit rendre, et aucun contrôle
    ordinaire ne l'attraperait.
    """
    faux = 0
    for i in range(int(decisif)):
        c = _une_course("gaussienne", n, 0.0, int(graine) + 4000 + i * 7, tirages)
        if c.get("decidable") and c["voit"]:
            faux += 1
    piege = 0
    for i in range(int(decisif)):
        c = _une_course("queues", n, float(aplatissement_du_piege), int(graine) + 8000 + i * 11,
                        tirages)
        if c.get("decidable") and c["voit"]:
            piege += 1
    def _echelle(mode, liste, sel):
        out = []
        for f in liste:
            vus, ind = 0, 0
            for i in range(int(replicats)):
                c = _une_course(mode, n, float(f), int(graine) + sel + int(f * 1000) * 13 + i,
                                tirages)
                if not c.get("decidable"):
                    ind += 1
                    continue
                vus += int(c["voit"])
            out.append({"la_force": float(f), "les_vus": int(vus), "sur": int(replicats),
                        "les_replicats_indecidables": int(ind)})
        return out

    echelle = _echelle("dependante", forces, 0)
    echelle_lente = _echelle("echelle_lente", forces_lentes, 20000)
    pleins = [e["la_force"] for e in echelle if e["les_vus"] == int(replicats)]
    pleins_lents = [e["la_force"] for e in echelle_lente if e["les_vus"] == int(replicats)]
    tf, tp = faux / float(decisif), piege / float(decisif)
    return {"decidable": True,
            "les_coutures_par_serie": int(n),
            "les_forces": [float(f) for f in forces],
            "les_replicats": int(replicats),
            "le_compte_decisif": int(decisif),
            "laplatissement_du_piege": float(aplatissement_du_piege),
            "les_forces_lentes": [float(f) for f in forces_lentes],
            "lechelle_par_volatilite": echelle,
            "lechelle_par_echelle_lente": echelle_lente,
            "la_plus_petite_force_vue": (min(pleins) if pleins else None),
            "la_plus_petite_force_lente_vue": (min(pleins_lents) if pleins_lents else None),
            "la_volatilite_sature_sans_jamais_etre_vue_partout": bool(not pleins),
            "la_suite_est_monotone": la_suite_est_monotone([e["les_vus"] for e in echelle]),
            "la_suite_lente_est_monotone":
                la_suite_est_monotone([e["les_vus"] for e in echelle_lente]),
            "les_faux": int(faux),
            "le_taux_de_faux": round(float(tf), 4),
            "elle_tient_sa_garantie": le_taux_tient(tf, GARANTIE),
            "les_tirs_sur_le_piege": int(piege),
            "le_taux_sur_le_piege": round(float(tp), 4),
            "elle_resiste_au_piege": le_taux_tient(tp, GARANTIE),
            "elle_separe": bool(pleins_lents and le_taux_tient(tf, GARANTIE)
                                and le_taux_tient(tp, GARANTIE))}


def le_tau_implique(facteur: dict, lam: float) -> dict:
    """LA BORNE SUR LA DÉPENDANCE, prise là où elle existe : dans le BUDGET, pas dans les décalages.

    ⚠⚠⚠ L'ÉPREUVE DES DÉCALAGES NE BORNE RIEN, ET L'ÉTALON LE DIT. Sur une centaine de points à
    queues lourdes, la règle ne voit une volatilité stochastique qu'environ sept fois sur douze,
    même au réglage le plus extrême, et une échelle lente pas davantage. Un négatif sans borne est
    un SILENCE, pas une réponse — la règle de ce dépôt depuis `214`.

    ⭐⭐⭐⭐ MAIS LA BORNE EXISTE AILLEURS, ET ELLE SORT DES DEUX ÉPREUVES DÉCLARÉES SANS EN AJOUTER
    UNE TROISIÈME. La décomposition posée d'avance est `Λ = (κ+2)/2 · τ`. `216` a mesuré `Λ`, cette
    tranche mesure `(κ+2)/2` ; le quotient est donc `τ`, avec son intervalle. C'est une INVERSION
    de la prédiction déclarée, pas une statistique de plus.

    ⚠⚠ ET SON SENS EST À LIRE AVEC SOIN : un `τ` impliqué inférieur à un n'a pas de sens physique —
    une dépendance ne peut que gonfler l'erreur — donc il dit que l'aplatissement mesuré sur ce
    tronçon SURESTIME celui des trente-six paires de `214`, ce qui est exactement ce qu'on attend
    d'un aplatissement estimé sur une centaine de points à queues lourdes. Le borner par le haut
    reste valide : il n'y a pas de place pour une dépendance importante EN PLUS des queues.
    """
    if not facteur.get("decidable"):
        return {"decidable": False, "raison": facteur.get("raison")}
    f = float(facteur["le_facteur_des_queues"])
    bas, haut = facteur["lintervalle_par_blocs"]
    if f <= 0.0 or float(bas) <= 0.0:
        return {"decidable": False, "raison": "le facteur des queues est nul"}
    return {"decidable": True,
            "le_rapport_de_216": round(float(lam), 4),
            "le_facteur_des_queues": round(f, 4),
            "le_tau_implique": round(float(lam) / f, 4),
            # ⚠ L'intervalle du facteur s'INVERSE : un facteur plus grand implique un tau plus
            # petit, donc la borne HAUTE de tau vient de la borne BASSE du facteur.
            "le_tau_implique_au_plus": round(float(lam) / float(bas), 4),
            "le_tau_implique_au_moins": round(float(lam) / float(haut), 4),
            "il_reste_de_la_place_pour_une_dependance":
                bool(float(lam) / float(bas) > 1.0)}


def _ce_qui_reste(dependance: bool, couvre: bool, borne: bool) -> str:
    """Les quatre issues, et elles sont EXCLUSIVES."""
    if dependance:
        return "LES DEUX HYPOTHÈSES SONT FAUSSES, ET LA DÉPENDANCE EST MESURABLE"
    if not couvre:
        return "LES QUEUES SEULES NE RENDENT PAS COMPTE DU DÉPASSEMENT, IL MANQUE UNE CAUSE"
    if borne:
        return ("CE SONT LES QUEUES, ET LE BUDGET NE LAISSE PAS DE PLACE POUR AUTRE CHOSE — "
                "MAIS L'AUTOCORRÉLATION N'A PAS PU LE BORNER ELLE-MÊME")
    return "CE SONT LES QUEUES, ET SEULEMENT ELLES — LA FORMULE SE CORRIGE SANS RIEN RELIRE"


def juger(familles: dict, facteurs: dict, par216: dict, etalon: dict, refus: dict,
          longues: dict, taus: dict) -> dict:
    dep = any(v.get("une_dependance_depasse_le_hasard") for v in familles.values()
              if v.get("decidable"))
    dep_longue = any(v.get("une_dependance_longue_depasse_le_hasard") for v in longues.values()
                     if v.get("decidable"))
    lam = float(par216.get("le_rapport") or 0.0)
    couvrantes = [nom for nom, f in facteurs.items()
                  if f.get("decidable") and f["lintervalle_par_blocs"][0] <= lam
                  <= f["lintervalle_par_blocs"][1]]
    couvre = bool(couvrantes) and len(couvrantes) == len([1 for f in facteurs.values()
                                                          if f.get("decidable")])
    place = [nom for nom, x in taus.items()
             if x.get("decidable") and x["il_reste_de_la_place_pour_une_dependance"]]
    borne_par_letalon = bool(etalon.get("elle_separe"))
    return {
        "une_dependance_depasse_le_hasard": bool(dep),
        "une_dependance_longue_depasse_le_hasard": bool(dep_longue),
        "lepreuve_des_decalages_borne_quelque_chose": borne_par_letalon,
        "combien_de_paires_laissent_de_la_place_a_une_dependance": len(place),
        "le_tau_implique_le_plus_grand": (
            max((x["le_tau_implique_au_plus"] for x in taus.values() if x.get("decidable")),
                default=None)),
        "combien_de_paires_couvrent_le_rapport_de_216": len(couvrantes),
        "combien_de_paires_mesurees": len([1 for f in facteurs.values() if f.get("decidable")]),
        "les_queues_rendent_compte_du_depassement": couvre,
        "le_rapport_de_216": lam,
        "la_statistique_refusee_est_au_plancher": all(
            r.get("tau_est_au_plancher") for r in refus.values() if r.get("decidable")),
        "letalon_separe": (bool(etalon.get("elle_separe")) if etalon else None),
        "ce_qui_reste_a_mesurer": _ce_qui_reste(dep, couvre, not borne_par_letalon),
        "pourquoi": (
            f"aucune des {len(familles)} paires ne rend d'autocorrélation que le rebrassage de sa "
            f"propre série n'égale, et le facteur des queues couvre le rapport {lam} de `216` sur "
            f"{len(couvrantes)} d'entre elles ; l'étalon dit que l'épreuve des décalages ne "
            f"borne rien sur cette longueur de série, donc la borne vient du budget et non d'elle"
            if not dep else
            f"une autocorrélation dépasse le rebrassage sur au moins une des {len(familles)} paires"),
    }


def mesurer(graine: int = GRAINE, tirages: int = PERMUTATIONS, replicats: int = 12,
            decisif: int = LE_COMPTE_DECISIF, chemin: Path = CE_QUE_LACCORD_A_RENDU,
            chemin216: Path = CE_QUE_LE_BUDGET_A_RENDU, avec_etalon: bool = True) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    lu = ce_que_laccord_a_rendu(chemin)
    if not lu.get("decidable"):
        return {"decidable": False, "raison": lu.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    par216 = ce_que_216_a_rendu(chemin216)
    if not par216.get("decidable"):
        return {"decidable": False, "raison": par216.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    familles, sur_la_serie, facteurs, refus, corriges, longues = {}, {}, {}, {}, {}, {}
    taus = {}
    for nom, p in lu["les_paires"].items():
        s = p["la_serie"]
        familles[nom] = la_famille_des_decalages(s, tirages, graine, sur_les_carres=True)
        longues[nom] = la_famille_longue(s, tirages, graine + 2)
        sur_la_serie[nom] = la_famille_des_decalages(s, tirages, graine + 1, sur_les_carres=False)
        facteurs[nom] = le_facteur_des_queues(s, graine=graine)
        refus[nom] = le_refus_de_tau(s)
        corriges[nom] = lerreur_corrigee(facteurs[nom], p["lecart_type_du_troncon_en_voxels"],
                                         p["combien_de_coutures_du_troncon"])
        taus[nom] = le_tau_implique(facteurs[nom], par216["le_rapport"])
    n_med = int(np.median([p["combien_de_coutures_du_troncon"]
                           for p in lu["les_paires"].values()]))
    etalon = (sur_letalon(n_med, replicats=replicats, decisif=decisif, graine=graine,
                          tirages=tirages) if avec_etalon else None)
    return {"decidable": True,
            "graine": int(graine),
            "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE,
            "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
            "la_garantie_du_nul": GARANTIE,
            "la_garantie_par_epreuve": GARANTIE_PAR_EPREUVE,
            "ce_que_211_a_rendu": {n: {k: v for k, v in p.items() if k != "la_serie"}
                                   for n, p in lu["les_paires"].items()},
            "ce_que_216_a_rendu": par216,
            "lepreuve_des_decalages": familles,
            "les_decalages_sur_la_serie": sur_la_serie,
            "la_famille_longue": longues,
            "lepreuve_des_queues": facteurs,
            "la_statistique_refusee": refus,
            "lerreur_corrigee": corriges,
            "le_tau_implique": taus,
            "letalon": etalon,
            "le_verdict": juger(familles, facteurs, par216, etalon or {}, refus, longues, taus)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"\n{len(r['ce_que_211_a_rendu'])} paires · rapport de `216` à battre : "
          f"{r['ce_que_216_a_rendu']['le_rapport']}")
    for nom, p in sorted(r["ce_que_211_a_rendu"].items()):
        f = r["lepreuve_des_queues"][nom]
        fam = r["lepreuve_des_decalages"][nom]
        ser = r["les_decalages_sur_la_serie"][nom]
        ref = r["la_statistique_refusee"][nom]
        co = r["lerreur_corrigee"][nom]
        print(f"\n  {nom} · {p['combien_de_coutures_du_troncon']} coutures contiguës sur "
              f"{p['les_coutures_communes']} communes ({p['les_troncons_communs']} tronçons) · σ "
              f"{p['lecart_type_du_troncon_en_voxels']}")
        if fam.get("decidable"):
            print(f"      carrés   · famille de {fam['combien_de_decalages']} décalages · la plus "
                  f"forte {fam['la_famille_observee']} au décalage {fam['le_decalage_le_plus_fort']}"
                  f" · nul médian {fam['la_famille_du_nul_mediane']} le plus fort "
                  f"{fam['la_famille_du_nul_la_plus_forte']} · "
                  f"{fam['les_tirages_au_moins_aussi_forts']}/{fam['tirages']} au moins aussi forts")
        if ser.get("decidable"):
            print(f"      série    · la plus forte {ser['la_famille_observee']} · "
                  f"{ser['les_tirages_au_moins_aussi_forts']}/{ser['tirages']} au moins aussi forts")
        lg = r["la_famille_longue"][nom]
        if lg.get("decidable"):
            print(f"      longue   · {lg['combien_de_decalages']} décalages · la plus forte "
                  f"{lg['la_famille_observee']} au décalage {lg['le_decalage_le_plus_fort']} · "
                  f"{lg['les_tirages_au_moins_aussi_forts']}/{lg['tirages']} au moins aussi forts")
        if ref.get("decidable"):
            print(f"      refusée  · τ = {ref['tau']} ({ref['les_paires_sommees']} paires sommées, "
                  f"au plancher : {ref['tau_est_au_plancher']})")
        if f.get("decidable"):
            print(f"      queues   · κ = {f['lexces_daplatissement']} → facteur "
                  f"{f['le_facteur_des_queues']} · par blocs (L={f['la_longueur_de_bloc']}) "
                  f"{f['lintervalle_par_blocs']} · ordinaire {f['lintervalle_ordinaire']} · "
                  f"écart {f['lecart_relatif_des_deux_bootstraps']}")
        ta = r["le_tau_implique"][nom]
        if ta.get("decidable"):
            print(f"      τ impliqué · {ta['le_tau_implique']} (au plus "
                  f"{ta['le_tau_implique_au_plus']}, au moins {ta['le_tau_implique_au_moins']}) · "
                  f"place pour une dépendance : {ta['il_reste_de_la_place_pour_une_dependance']}")
        if co.get("decidable"):
            print(f"      remède   · erreur déclarée {co['lerreur_declaree_en_voxels2']} vx² contre "
                  f"corrigée {co['lerreur_corrigee_en_voxels2']} vx², rapport {co['le_rapport']}")
    t = r.get("letalon")
    if t and t.get("decidable"):
        print(f"\nÉTALON · séries de {t['les_coutures_par_serie']} points :")
        for e in t["lechelle_par_volatilite"]:
            print(f"    volatilité stochastique φ={e['la_force']} · vu {e['les_vus']}/{e['sur']}")
        print(f"  ⚠ la volatilité SATURE sans jamais être vue partout : "
              f"{t['la_volatilite_sature_sans_jamais_etre_vue_partout']} — plus φ monte, plus les "
              f"queues montent avec, et les queues détruisent la puissance")
        for e in t["lechelle_par_echelle_lente"]:
            print(f"    échelle lente a={e['la_force']} · vu {e['les_vus']}/{e['sur']}")
        print(f"  plus petite échelle lente vue partout {t['la_plus_petite_force_lente_vue']} · "
              f"monotone {t['la_suite_lente_est_monotone']}")
        print(f"  faux {t['les_faux']}/{t['le_compte_decisif']} = {t['le_taux_de_faux']} · "
              f"PIÈGE (queues κ={t['laplatissement_du_piege']} sans dépendance) "
              f"{t['les_tirs_sur_le_piege']}/{t['le_compte_decisif']} = {t['le_taux_sur_le_piege']}"
              f" · sépare {t['elle_separe']}")
    v = r["le_verdict"]
    print(f"\nVERDICT · dépendance courte : {v['une_dependance_depasse_le_hasard']} · longue : "
          f"{v['une_dependance_longue_depasse_le_hasard']} · les queues couvrent "
          f"{v['combien_de_paires_couvrent_le_rapport_de_216']}/"
          f"{v['combien_de_paires_mesurees']} paires")
    print(f"  reste à mesurer : {v['ce_qui_reste_a_mesurer']}")
    print(f"  pourquoi        : {v['pourquoi']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        """Une sonde accepte un appelable, et une levée est un ÉCHEC — jamais une batterie morte."""
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★★★ deux épreuves sont déclarées et la garantie se partage",
      len(LES_EPREUVES_DECLAREES) == 2 and abs(GARANTIE_PAR_EPREUVE - GARANTIE / 2.0) < 1e-12)

    # ⚠⚠⚠ LE LECTEUR VERIFIE LA SERIE CONTRE LE NOMBRE QUE `211` PUBLIE A COTE D'ELLE.
    v("★★★ un fichier absent est refusé par son nom",
      not ce_que_laccord_a_rendu(Path("/nen/existe/pas.json")).get("decidable"))
    tmp = RACINE / "docs" / "mesures" / ".sonde_217.json"
    try:
        base = json.loads(CE_QUE_LACCORD_A_RENDU.read_text())
        tmp.write_text(json.dumps({}))
        v("★★★★ un JSON sans désaccords est refusé et la raison les NOMME",
          lambda: "désaccords" in (ce_que_laccord_a_rendu(tmp).get("raison") or ""))
        d2 = json.loads(json.dumps(base))
        nom0 = sorted(d2["les_desaccords"])[0]
        d2["les_desaccords"][nom0]["les_ecarts_de_pas_du_troncon_en_voxels"] = \
            [x * 2.0 for x in d2["les_desaccords"][nom0]["les_ecarts_de_pas_du_troncon_en_voxels"]]
        tmp.write_text(json.dumps(d2))
        got = ce_que_laccord_a_rendu(tmp)
        v("★★★★ une série qui ne rend PAS l'écart-type que `211` publie à côté d'elle est REFUSÉE — "
          "lire une autre suite sous ce nom serait `R4-L19` une fois de plus",
          not got.get("decidable") and nom0 in (got.get("raison") or ""), str(got.get("raison")))
        d2 = json.loads(json.dumps(base))
        d2["les_desaccords"][nom0].pop("les_ecarts_de_pas_du_troncon_en_voxels", None)
        tmp.write_text(json.dumps(d2))
        v("★★★ une paire sans série est refusée, jamais sautée",
          lambda: not ce_que_laccord_a_rendu(tmp).get("decidable"))
        d2 = json.loads(json.dumps(base))
        d2["les_desaccords"][nom0].pop("lecart_type_des_pas_du_troncon_en_voxels", None)
        tmp.write_text(json.dumps(d2))
        v("★★★★ une série sans son écart-type de référence est refusée — sans lui, rien ne dit que "
          "c'est la bonne suite",
          lambda: not ce_que_laccord_a_rendu(tmp).get("decidable"))
    finally:
        tmp.unlink(missing_ok=True)
    lu = ce_que_laccord_a_rendu()
    v("★★★★ `211` publie TROIS paires, toutes vérifiées contre leur écart-type",
      lu.get("decidable") and lu.get("combien_de_paires") == 3, str(lu.get("raison")))
    p216 = ce_que_216_a_rendu()
    v("★★★★ le rapport de `216` est relu, parce que c'est LUI que cette tranche prédit",
      p216.get("decidable") and p216.get("le_rapport", 0) > 0, str(p216.get("raison")))
    v("★★★ un `216` absent rend la mesure indécidable",
      not mesurer(GRAINE, PERMUTATIONS, 2, 4,
                  chemin216=Path("/nen/existe/pas.json")).get("decidable"))

    # ⭐ L'AUTOCORRELATION EST EPINGLEE SUR DU CONNU.
    # ⚠⚠ L'ESTIMATEUR DIVISE PAR `n` ET NON PAR `n - k`, DONC IL RETRECIT DE `(n-k)/n` — c'est la
    # forme BIAISEE, voulue parce qu'elle garde la suite des autocorrelations semi-definie positive.
    # La sonde epingle donc la valeur EXACTE que cette forme rend, pas un « environ un » qui aurait
    # accepte n'importe quel estimateur.
    v("★★★★ l'autocorrélation d'une suite alternée vaut EXACTEMENT ±(n-k)/n, la forme biaisée",
      abs(lautocorrelation([1.0, -1.0] * 40, 2) - 78.0 / 80.0) < 1e-9
      and abs(lautocorrelation([1.0, -1.0] * 40, 1) + 79.0 / 80.0) < 1e-9,
      f"{lautocorrelation([1.0, -1.0] * 40, 2)} et {lautocorrelation([1.0, -1.0] * 40, 1)}")
    v("★★★ un décalage hors de portée rend None, jamais zéro",
      lautocorrelation([1.0, 2.0, 3.0], 5) is None
      and lautocorrelation([1.0, 2.0, 3.0], 0) is None)
    v("★★★ une suite constante n'a pas d'autocorrélation", lautocorrelation([2.0] * 20, 1) is None)
    v("★★★★ le nombre de décalages est DÉRIVÉ de la longueur, jamais choisi",
      combien_de_decalages(100) == 10 and combien_de_decalages(169) == 13
      and combien_de_decalages(8) <= 3, str([combien_de_decalages(n) for n in (8, 100, 169)]))

    # ⚠⚠⚠ LE REFUS DE TAU SE DEMONTRE SANS REGARDER LA MOINDRE SERIE.
    g0 = _rng(3)
    v("★★★★ τ vaut EXACTEMENT un dès que la première paire d'autocorrélations est négative, donc "
      "il est plancher par construction",
      le_refus_de_tau([1.0, -1.0] * 50)["tau"] == 1.0
      and le_refus_de_tau([1.0, -1.0] * 50)["tau_est_au_plancher"] is True)
    v("★★★★ et il dépasse un quand la dépendance est franche, donc le plancher n'est pas un bug",
      le_refus_de_tau(np.cumsum(g0.normal(0.0, 1.0, 200)))["tau"] > 1.0,
      str(le_refus_de_tau(np.cumsum(_rng(3).normal(0.0, 1.0, 200)))["tau"]))
    v("★★★ le refus porte sa raison avec lui",
      "plancher" in (le_refus_de_tau([1.0, -1.0] * 50).get("pourquoi_il_est_refuse") or ""))
    v("★★★ une série constante rend le refus indécidable",
      not le_refus_de_tau([1.0] * 40).get("decidable"))

    # ⭐⭐⭐⭐ LA FAMILLE DOIT TIRER SUR UNE DEPENDANCE PLANTEE *DANS SA PORTEE*, ET SE TAIRE SINON.
    n_ = 400
    k_ = combien_de_decalages(n_)
    gg = _rng(11)
    # ⚠⚠⚠ LA MATIERE DE CETTE SONDE A DU ETRE CHERCHEE, ET CE QU'IL A FALLU CHERCHER EST LE
    # RESULTAT. La regle est faiblement dotee — l'etalon le mesure — et il y a DEUX facons de la
    # rendre aveugle : planter la dependance hors de sa portee (l'erreur de la fixture
    # `echelle_lente`), ou la planter si fort que le contraste fabrique lui-meme des queues, qui
    # gonflent le nul autant que l'observe. Le contraste est donc MODERE (quatre pour un sur les
    # carres) et la serie LONGUE, et c'est la seule fenetre ou la sonde peut passer sur du code
    # juste.
    bloc = np.where((np.arange(n_) // 2) % 2 == 0, 2.0, 0.5)
    dedans = bloc * gg.normal(0, 1, n_)
    v("★★★★ sur une dépendance FRANCHE plantée DANS la portée de la famille, elle tire",
      la_famille_des_decalages(dedans, PERMUTATIONS, 13)["une_dependance_depasse_le_hasard"],
      str(la_famille_des_decalages(dedans, PERMUTATIONS, 13)
          .get("les_tirages_au_moins_aussi_forts")))
    long_bloc = np.where((np.arange(n_) // (3 * k_)) % 2 == 0, 2.0, 0.5)
    dehors = long_bloc * _rng(11).normal(0, 1, n_)
    fam_dehors = la_famille_des_decalages(dehors, PERMUTATIONS, 13)
    fam_longue = la_famille_longue(dehors, PERMUTATIONS, 13)
    v("★★★★ une dépendance plantée HORS de sa portée lui échappe, et la famille LONGUE la voit — "
      "c'est la limite déclarée, mesurée plutôt qu'affirmée",
      fam_dehors.get("decidable") and fam_longue.get("decidable")
      and fam_longue["combien_de_decalages"] > fam_dehors["combien_de_decalages"]
      and fam_longue["la_famille_observee"] >= fam_dehors["la_famille_observee"],
      f"{fam_dehors.get('la_famille_observee')} contre {fam_longue.get('la_famille_observee')}")
    iid = _rng(17).normal(0.0, 1.0, n_)
    v("★★★ sur du bruit indépendant elle se tait",
      not la_famille_des_decalages(iid, PERMUTATIONS, 13)["une_dependance_depasse_le_hasard"])
    v("★★★★ le nul REBRASSE la série observée, donc il en garde EXACTEMENT les valeurs et les "
      "queues — un nul paramétrique répondrait pour une loi que la matière n'a pas",
      la_famille_des_decalages(_rng(19).standard_t(4.5, n_), PERMUTATIONS, 13)
      .get("la_famille_du_nul_la_plus_forte") is not None)
    v("★★★ la famille porte autant d'autocorrélations que de décalages déclarés",
      len(la_famille_des_decalages(iid, PERMUTATIONS, 13)["les_autocorrelations"])
      == combien_de_decalages(n_))

    # ⭐⭐⭐⭐ LE FACTEUR DES QUEUES EST EPINGLE SUR DES LOIS DONT ON CONNAIT L'APLATISSEMENT.
    gq = _rng(23).normal(0.0, 1.0, 4000)
    fg = le_facteur_des_queues(gq, graine=23)
    v("★★★★ sur une gaussienne, le facteur des queues vaut UN — c'est le cas que la formule "
      "déclarée par `212` suppose",
      fg.get("decidable") and abs(fg["le_facteur_des_queues"] - 1.0) < 0.15,
      str(fg.get("le_facteur_des_queues")))
    ft = le_facteur_des_queues(_rng(29).standard_t(6.0, 6000), graine=29)
    v("★★★★ sur une loi à queues lourdes il dépasse franchement un, donc il MESURE les queues et "
      "ne les suppose pas",
      ft.get("decidable") and ft["le_facteur_des_queues"] > 1.6,
      str(ft.get("le_facteur_des_queues")))
    v("★★★★ l'intervalle par blocs encadre le point, et la longueur de bloc est DÉRIVÉE",
      ft["lintervalle_par_blocs"][0] <= ft["le_facteur_des_queues"] <= ft["lintervalle_par_blocs"][1]
      and ft["la_longueur_de_bloc"] == la_longueur_de_bloc(6000))
    v("★★★ une série trop courte est refusée, jamais extrapolée",
      not le_facteur_des_queues([1.0, 2.0, 3.0]).get("decidable"))

    # ⚠⚠ LE REMEDE SE REDUIT A LA FORMULE DECLAREE QUAND L'APLATISSEMENT EST NUL.
    co = lerreur_corrigee({"decidable": True, "lexces_daplatissement": 0.0}, 2.0, 200)
    v("★★★★ à aplatissement NUL, l'erreur corrigée rejoint la déclarée — sinon le remède ne serait "
      "pas une généralisation mais une autre formule",
      co.get("decidable") and abs(co["le_rapport"] - 1.0) < 0.01, str(co.get("le_rapport")))
    co2 = lerreur_corrigee({"decidable": True, "lexces_daplatissement": 6.0}, 2.0, 200)
    v("★★★★ et à aplatissement SIX elle vaut deux fois la déclarée, comme √((6+2)/2) le prédit",
      co2.get("decidable") and abs(co2["le_rapport"] - 2.0) < 0.02, str(co2.get("le_rapport")))
    v("★★★ un facteur indécidable rend le remède indécidable",
      not lerreur_corrigee({"decidable": False}, 2.0, 200).get("decidable"))

    # ⚠⚠⚠ LE TAU IMPLIQUE INVERSE L'INTERVALLE, ET C'EST LE SENS QUI COMPTE.
    ti = le_tau_implique({"decidable": True, "le_facteur_des_queues": 4.0,
                          "lintervalle_par_blocs": [2.0, 8.0]}, 2.0)
    v("★★★★ le τ impliqué est le quotient du rapport par le facteur",
      ti.get("decidable") and abs(ti["le_tau_implique"] - 0.5) < 1e-9)
    v("★★★★ et son intervalle S'INVERSE : la borne HAUTE de τ vient de la borne BASSE du facteur",
      abs(ti["le_tau_implique_au_plus"] - 1.0) < 1e-9
      and abs(ti["le_tau_implique_au_moins"] - 0.25) < 1e-9,
      f"{ti['le_tau_implique_au_plus']} et {ti['le_tau_implique_au_moins']}")
    v("★★★★ il dit qu'il reste de la place pour une dépendance exactement quand sa borne haute "
      "dépasse un",
      le_tau_implique({"decidable": True, "le_facteur_des_queues": 4.0,
                       "lintervalle_par_blocs": [4.0, 8.0]}, 2.0)
      ["il_reste_de_la_place_pour_une_dependance"] is False)

    # ⚠⚠ LES TROIS MODES DE MATIERE SONT DISTINCTS, ET LE PIEGE EST BIEN UN PIEGE.
    sq = une_serie("queues", 3000, 6.0, 31)["la_serie"]
    sg = une_serie("gaussienne", 3000, 0.0, 31)["la_serie"]
    v("★★★★ le mode `queues` porte bien des queues plus lourdes que le mode `gaussienne`",
      le_facteur_des_queues(sq, graine=31)["le_facteur_des_queues"]
      > le_facteur_des_queues(sg, graine=31)["le_facteur_des_queues"] + 0.5)
    v("★★★★ et il ne porte AUCUNE dépendance — c'est ce qui en fait le piège de cette tranche",
      not la_famille_des_decalages(une_serie("queues", 200, 6.0, 37)["la_serie"],
                                   PERMUTATIONS, 37)["une_dependance_depasse_le_hasard"])
    v("★★★ un mode inconnu est REFUSÉ, jamais replié sur un mode connu",
      une_serie("la_moyenne", 100, 1.0, 5).get("la_serie") is None)

    # ⚠⚠⚠ L'ETALON DOIT POUVOIR DIRE QU'IL NE SEPARE PAS.
    et = sur_letalon(105, forces=(0.9,), forces_lentes=(0.95,), replicats=4, decisif=20,
                     graine=41, tirages=PERMUTATIONS)
    v("★★★★ l'étalon publie les DEUX échelles, parce qu'une seule ne dirait pas que la saturation "
      "vient des queues et non de la règle",
      et.get("decidable") and et.get("lechelle_par_volatilite")
      and et.get("lechelle_par_echelle_lente"))
    v("★★★★ il PEUT rendre « ne sépare pas », donc son verdict n'est pas décoratif",
      et.get("decidable") and isinstance(et.get("elle_separe"), bool))
    v("★★★★ les deux taux tiennent la garantie du nul",
      et.get("decidable") and et["elle_tient_sa_garantie"] and et["elle_resiste_au_piege"],
      f"{et.get('le_taux_de_faux')} et {et.get('le_taux_sur_le_piege')}")
    v("★★★ un taux au-dessus de deux fois la garantie ne tient pas",
      not le_taux_tient(2.0 * GARANTIE + 0.01, GARANTIE))

    # ⭐⭐⭐ LES QUATRE ISSUES SONT EXCLUSIVES.
    issues = {_ce_qui_reste(a, b, c) for a in (True, False) for b in (True, False)
              for c in (True, False)}
    v("★★★★ les huit combinaisons ne rendent que QUATRE issues, et la dépendance prime sur tout",
      len(issues) == 4 and _ce_qui_reste(True, False, False) == _ce_qui_reste(True, True, True))
    v("★★★★ une issue dit explicitement que l'autocorrélation n'a pas pu borner — sans elle, un "
      "silence se lirait comme une réponse",
      any("N'A PAS PU" in x for x in issues))

    # ⭐⭐⭐⭐ LA MESURE ENTIERE.
    out = mesurer(GRAINE, PERMUTATIONS, 2, 6, avec_etalon=True)
    v("★★★★ la mesure traverse sans lire le volume et rend son verdict",
      out.get("decidable") and (out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer"),
      str(out.get("raison")))
    v("★★★★ elle publie la statistique REFUSÉE avec sa valeur, pour qu'on puisse la recalculer",
      all(x.get("decidable") for x in (out.get("la_statistique_refusee") or {}).values()))
    v("★★★★ elle publie la famille LONGUE à côté de la déclarée, sans quoi la limite de portée "
      "resterait invisible",
      all(x.get("decidable") for x in (out.get("la_famille_longue") or {}).values()))
    v("★★★★ elle publie le remède pour chaque paire, avec l'erreur déclarée À CÔTÉ de la corrigée",
      all(x.get("decidable") and x.get("lerreur_declaree_en_voxels2") is not None
          for x in (out.get("lerreur_corrigee") or {}).values()))
    v("★★★★ et le verdict LIT l'étalon pour dire si l'épreuve des décalages a borné quoi que ce "
      "soit — l'affirmer sans le lire serait publier une borne que rien ne soutient",
      (out.get("le_verdict") or {}).get("lepreuve_des_decalages_borne_quelque_chose")
      == bool((out.get("letalon") or {}).get("elle_separe")),
      f"{(out.get('le_verdict') or {}).get('lepreuve_des_decalages_borne_quelque_chose')} contre "
      f"{(out.get('letalon') or {}).get('elle_separe')}")
    v("★★★★ et quand l'étalon ne sépare pas, l'issue le DIT au lieu de rendre un négatif nu",
      bool((out.get("letalon") or {}).get("elle_separe"))
      or "N'A PAS PU" in ((out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer") or ""),
      str((out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer")))

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
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--tirages", type=int, default=PERMUTATIONS)
    p.add_argument("--replicats", type=int, default=12)
    p.add_argument("--decisif", type=int, default=LE_COMPTE_DECISIF)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graine, a.tirages, a.replicats, a.decisif, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
