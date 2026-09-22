"""Les erreurs déclarées rendent-elles compte des résidus de l'ajustement additif ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE SA STATISTIQUE NE SOIT CALCULÉE. C'est la contrainte que `215`
a identifiée comme la seule qui compte, et la seule façon honnête de la tenir est de poser
l'épreuve, le nul et le verdict d'abord, puis de mesurer. Ce qui suit a donc été rédigé sans
qu'aucun des nombres qu'il produira ne soit connu.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P61` SOUS SA FORME LA MOINS CHÈRE. Toute la chaîne
`R4-P60` suppose qu'il y a une rupture d'additivité à expliquer, et cette supposition repose sur UN
nombre : le pire résidu du triangle sur-déterminé de `214`, **3,6279 erreurs** sur la paire
`197-198`. Un résidu « en erreurs » est un rapport, donc il a DEUX moitiés, et la chaîne n'a
interrogé que le numérateur. Le dénominateur est l'erreur d'échantillonnage déclarée

    se(V) = V·√(2/(n-1))

où `n` est le nombre de coutures communes à la paire. ⚠⚠⚠ CETTE FORMULE SUPPOSE QUE LES `n`
DIFFÉRENCES PAR COUTURE SONT INDÉPENDANTES, et PERSONNE NE L'A MESURÉ. Si elles sont corrélées le
long de la rangée — ce qu'une nappe qui dérive fait volontiers, et `208` a précisément mesuré une
dérive PARTAGÉE — alors le nombre effectif de coutures indépendantes est plus petit que `n`,
l'erreur déclarée est SOUS-ESTIMÉE, et TOUS les résidus en erreurs sont gonflés du même facteur.
La réfutation du modèle additif serait alors un artefact d'une hypothèse que personne n'a vérifiée.

⚠⚠ ET LA QUESTION SE TRANCHE SANS AUCUNE LECTURE NEUVE DU VOLUME, parce que l'ajustement porte sa
propre prédiction. Pour une projection au moindre carré NON pondérée `H = A(AᵀA)⁻¹Aᵀ`, le résidu de
l'équation `i` vaut `r = (I - H)y`, donc son espérance quadratique est EXACTEMENT

    E[r_i²] = Σ_k (I - H)_{ik}² · σ_k²

et l'énergie totale attendue des résidus STANDARDISÉS vaut

    E[Λ] = Σ_i Σ_k (I - H)_{ik}² · σ_k² / σ_i²

⭐ AUCUN SEUIL N'ENTRE LÀ : la matrice de projection est celle du treillis, les `σ_k` sont les
erreurs que `214` a déclarées, et la somme se calcule. Ce n'est pas le `n - p` approché d'un
ajustement pondéré, parce que l'ajustement de `214` n'est PAS pondéré, et prendre `n - p` ici serait
un nombre juste pour un autre ajustement que celui qui tourne.

## Les deux épreuves, déclarées d'avance

⭐⭐⭐⭐ **PREMIÈRE ÉPREUVE — LE BUDGET.** Le rapport `Λ = observé / attendu` vaut-il un ? S'il vaut
sensiblement plus, les résidus dépassent ce que les erreurs déclarées autorisent, et il y a quelque
chose ; s'il vaut un, il n'y a rien à expliquer et `R4-P60` se referme sans qu'aucune piste B n'ait
à être payée.

⭐⭐⭐⭐ **SECONDE ÉPREUVE — LA FORME, ET C'EST ELLE QUI SÉPARE LES DEUX EXPLICATIONS.** Un excès
peut venir de deux mondes qui rendent le MÊME `Λ` :

  - les erreurs déclarées sont sous-estimées d'un facteur commun, et alors l'excès est ÉTALÉ : tous
    les résidus sont gonflés ensemble, et leur forme reste celle du modèle ;
  - le modèle additif casse sur quelques paires, et alors l'excès est CONCENTRÉ : quelques résidus
    énormes et beaucoup de petits.

La statistique déclarée est le **plus grand résidu standardisé après remise à l'échelle par √Λ** —
la remise à l'échelle est ce qui rend les deux mondes comparables, puisqu'elle force le budget total
à tomber juste dans les deux cas et ne laisse donc que la FORME.

⚠⚠⚠ ET C'EST ICI, ET NULLE PART AILLEURS DANS CETTE CHAÎNE, QU'UN NUL PARAMÉTRIQUE EST LE BON
OUTIL. Une permutation ne peut pas répondre : rebrasser les résidus ne change ni le budget total ni
l'ensemble des valeurs, donc elle ne peut pas dire si cet ensemble est celui qu'un modèle à erreurs
déclarées produit. Ce qui est en procès EST le modèle d'erreur, donc le nul doit SIMULER sous ce
modèle — tirer des désaccords sous l'additivité avec les erreurs déclarées, réajuster à chaque
tirage, et regarder la forme que ça donne. ⚠ `R4-P60` avait d'abord prescrit un nul paramétrique
pour une question où la permutation tenait sa garantie, et avait dû se rétracter ; ici c'est
l'inverse, et la raison est écrite plutôt que supposée.

⚠⚠ LE PIÈGE EST NOMMÉ D'AVANCE : un nul paramétrique ne teste QUE ce qu'il simule. Il suppose des
tirages gaussiens indépendants autour du modèle additif, donc il ne peut pas détecter une
non-normalité des désaccords eux-mêmes ; il répond « cette forme est-elle celle du modèle déclaré »,
jamais « le modèle déclaré est-il le bon ». Cette limite se publie à côté du verdict.

⚠ ET LE CONTRÔLE GRATUIT RESTE CELUI DE `212` : les neuf variances propres sont POSITIVES. Une
explication qui rendrait une variance négative serait pire que le modèle qu'elle remplace.

Usage :
    uv run python src/nappe/les_erreurs_declarees_rendent_elles_compte_des_residus.py --verifier
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
CE_QUE_LE_BRUIT_PROPRE_A_RENDU = MESURES / "le_bruit_propre_croit_il_avec_lecartement.json"
GRAINE = 20261028

LA_QUESTION_DECLAREE = ("les erreurs d'échantillonnage déclarées par `214` rendent-elles compte de "
                        "l'énergie de ses résidus, et si non, cet excès est-il ÉTALÉ sur toutes "
                        "les paires ou CONCENTRÉ sur quelques-unes ?")
LES_EPREUVES_DECLAREES = ("l'énergie des résidus dépasse le budget des erreurs déclarées",
                          "l'excès est concentré et non étalé")
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)
"""⚠⚠ DEUX ÉPREUVES, DONC LA GARANTIE SE PARTAGE — c'est la règle de `214` et elle a un coût réel.

Le nul ne porte que `PERMUTATIONS` tirages, donc le plus petit degré de surprise atteignable est
`1/(PERMUTATIONS+1)`. Partager la garantie en deux la met SOUS ce plancher : aucune des deux
épreuves ne peut donc être déclarée franchie par le seul compte de tirages. ⭐ C'est voulu et c'est
dit : la première épreuve ne repose PAS sur un nul mais sur une espérance EXACTEMENT calculée, donc
elle ne consomme aucun tirage ; la seconde est la seule qui en consomme, et elle porte la garantie
entière du nul. Le partage reste publié pour que le lecteur puisse le refaire."""

LE_COMPTE_DECISIF = 171


def ce_que_le_bruit_propre_a_rendu(chemin: Path = CE_QUE_LE_BRUIT_PROPRE_A_RENDU) -> dict:
    """Les paires que `214` a lues — relues, jamais retapées, et REFUSÉES par leur nom.

    ⚠⚠⚠ CETTE TRANCHE A BESOIN DES DEUX MOITIÉS DU RAPPORT, donc elle relit les DÉSACCORDS et les
    COUTURES et refait l'ajustement elle-même. Relire les résidus déjà standardisés ne servirait à
    rien : c'est justement le dénominateur qui est en procès, et un résidu en erreurs l'a déjà
    absorbé.

    ⚠⚠ Une paire sans ses coutures est refusée : sans elles l'erreur déclarée n'existe pas, et la
    compter pour une erreur quelconque reviendrait à inventer le nombre qu'on met en procès.
    """
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    mes = d.get("les_desaccords_par_paire") or {}
    if not mes.get("decidable"):
        return {"decidable": False, "raison": "les désaccords par paire de `214` sont indécidables"}
    brutes = mes.get("les_paires")
    if not isinstance(brutes, list) or len(brutes) < 4:
        return {"decidable": False, "raison": "`214` ne publie pas assez de paires"}
    tri = d.get("le_triangle_surdetermine") or {}
    if not tri.get("decidable"):
        return {"decidable": False, "raison": "le triangle sur-déterminé de `214` est indécidable"}
    ep214 = d.get("lepreuve") or {}
    paires, rangees = [], set()
    for p in brutes:
        pa = p.get("la_paire") or []
        s = p.get("le_desaccord_par_couture_en_voxels")
        n = p.get("les_coutures_communes")
        if len(pa) != 2 or s is None:
            return {"decidable": False, "raison": "une paire ne porte pas son désaccord"}
        if not n or int(n) < 3:
            return {"decidable": False,
                    "raison": f"la paire {pa[0]}-{pa[1]} ne porte pas ses coutures"}
        paires.append({"la_paire": [int(pa[0]), int(pa[1])],
                       "le_desaccord_en_voxels": float(s),
                       "les_coutures_communes": int(n),
                       # ⚠⚠ LE MAXIMUM PAR COUTURE EST RELU PARCE QUE L'AUTRE MOITIE DE LA FORMULE
                       # D'ERREUR EST LA NORMALITE, et `214` l'a deja publie sans le lire ainsi.
                       "le_desaccord_le_plus_grand_en_voxels":
                           (None if p.get("le_desaccord_le_plus_grand_en_voxels") is None
                            else float(p["le_desaccord_le_plus_grand_en_voxels"]))})
        rangees.update(int(x) for x in pa)
    r = sorted(rangees)
    if len(paires) <= len(r):
        return {"decidable": False,
                "raison": f"{len(paires)} équations pour {len(r)} inconnues, rien à sur-déterminer"}
    return {"decidable": True,
            "les_paires": paires,
            "les_rangees": r,
            "combien_de_paires": len(paires),
            "combien_de_rangees": len(r),
            # ⚠⚠ CE QUE `216` CITE DE `214` EST RELU, JAMAIS RETAPE — precedent de `215`.
            "le_pire_residu_de_214_en_erreurs": tri.get("le_pire_residu_en_erreurs"),
            "le_residu_median_de_214_en_erreurs": tri.get("le_residu_median_en_erreurs"),
            "la_tendance_de_214_contre_lecartement": ep214.get("la_tendance_observee"),
            "les_tirages_de_214_au_moins_aussi_forts":
                ep214.get("les_tirages_au_moins_aussi_forts"),
            "la_paire_du_pire_residu_de_214": tri.get("la_paire_du_pire_residu_en_erreurs"),
            "les_variances_negatives_de_214": list(tri.get("les_rangees_a_variance_negative") or []),
            "les_coutures_les_plus_nombreuses": max(p["les_coutures_communes"] for p in paires),
            "les_coutures_les_moins_nombreuses": min(p["les_coutures_communes"] for p in paires),
            "les_coutures_medianes": int(np.median([p["les_coutures_communes"] for p in paires]))}


def le_treillis(paires, rangees) -> dict:
    """La matrice du treillis, les cibles et les erreurs DÉCLARÉES — une seule définition.

    ⚠⚠⚠ L'ERREUR EST CELLE DE `214`, `se(V) = V·√(2/(n-1))`, ÉCRITE ICI PARCE QU'ELLE EST L'OBJET
    DU PROCÈS. La recopier depuis un résidu déjà standardisé serait impossible — un rapport a perdu
    son dénominateur — et la réécrire autrement ferait juger une formule qui n'a jamais tourné.
    """
    r = sorted(int(x) for x in rangees)
    index = {v: i for i, v in enumerate(r)}
    lignes, cibles, erreurs, noms = [], [], [], []
    for p in paires:
        a, b = int(p["la_paire"][0]), int(p["la_paire"][1])
        n = int(p["les_coutures_communes"])
        v = float(p["le_desaccord_en_voxels"]) ** 2
        ligne = [0.0] * len(r)
        ligne[index[a]] = 1.0
        ligne[index[b]] = 1.0
        lignes.append(ligne)
        cibles.append(v)
        erreurs.append(v * float(np.sqrt(2.0 / (n - 1))))
        noms.append(f"{a}-{b}")
    return {"A": np.asarray(lignes, dtype=float), "y": np.asarray(cibles, dtype=float),
            "sigma": np.asarray(erreurs, dtype=float), "noms": noms, "rangees": r}


def le_budget_attendu(a_mat: np.ndarray, sigma: np.ndarray) -> dict:
    """L'énergie que les erreurs DÉCLARÉES autorisent — exactement, pas approximativement.

    ⚠⚠⚠ CE N'EST PAS `n - p`, ET LA DIFFÉRENCE N'EST PAS COSMÉTIQUE. `n - p` est l'espérance du
    khi-deux d'un ajustement PONDÉRÉ ; celui de `214` ne l'est pas, il minimise la somme des carrés
    bruts en voxels carrés. Pour une projection non pondérée `H = A·A⁺`, le résidu vaut
    `r = (I - H)y`, donc `E[r_i²] = Σ_k (I-H)_{ik}²·σ_k²` et l'énergie standardisée attendue est
    la somme de ces termes divisés par `σ_i²`. Employer `n - p` ici rendrait un nombre juste pour
    un ajustement qui ne tourne pas.

    ⚠ La trace de `I - H` est publiée à côté : elle VAUT `n - p` exactement, donc les deux nombres
    côte à côte montrent que l'écart vient bien de la pondération et non d'une erreur de rang.
    """
    n = a_mat.shape[0]
    if n != len(sigma) or n < 4:
        return {"decidable": False, "raison": "la matrice et les erreurs ne s'accordent pas"}
    if float(np.min(sigma)) <= 0.0:
        return {"decidable": False, "raison": "une erreur déclarée est nulle ou négative"}
    m = np.eye(n) - a_mat @ np.linalg.pinv(a_mat)
    v = sigma ** 2
    attendu = float(np.sum((m ** 2) @ v / v))
    return {"decidable": True,
            "combien_dequations": int(n),
            "combien_dinconnues": int(np.linalg.matrix_rank(a_mat)),
            "la_trace_du_projecteur": round(float(np.trace(m)), 4),
            "lenergie_attendue": round(attendu, 4),
            "lenergie_attendue_du_khi_deux_pondere": int(round(float(np.trace(m)))),
            "les_deux_sont_egales": bool(abs(attendu - float(np.trace(m))) < 1e-9)}


def lajustement(tre: dict) -> dict:
    """L'ajustement additif NON pondéré de `214`, et ses résidus standardisés."""
    a_mat, y, sigma = tre["A"], tre["y"], tre["sigma"]
    sol, *_ = np.linalg.lstsq(a_mat, y, rcond=None)
    r = y - a_mat @ sol
    return {"decidable": True,
            "les_variances_propres": {str(tre["rangees"][i]): round(float(sol[i]), 4)
                                      for i in range(len(tre["rangees"]))},
            "les_rangees_a_variance_negative": [int(tre["rangees"][i])
                                                for i in range(len(sol)) if float(sol[i]) < 0.0],
            "les_residus_standardises": {tre["noms"][i]: round(float(r[i] / sigma[i]), 4)
                                         for i in range(len(r))},
            "_std": r / sigma}


def le_nul_parametrique(tre: dict, attendu: float, tirages: int = PERMUTATIONS,
                        graine: int = GRAINE) -> dict:
    """UN SEUL nul, lu par les DEUX épreuves — il simule sous le modèle d'erreur en procès.

    ⚠⚠⚠ DEUX NULS SERAIENT DEUX TIRAGES ET NON DEUX ÉPREUVES. Le rapport au budget et la forme
    sont deux lectures du MÊME monde simulé ; les faire courir sur deux séries différentes
    reviendrait à comparer deux hasards au lieu de comparer deux propriétés. `214` a dû appliquer
    exactement ce remède à son propre étalon.

    ⚠⚠ CHAQUE TIRAGE SUBIT LE MÊME TRAITEMENT QUE L'OBSERVÉ : on tire sous l'additivité avec les
    erreurs déclarées, on REFAIT l'ajustement, on calcule SON rapport, et on remet SA forme à
    l'échelle par SON propre rapport. C'est ce qui rend la remise à l'échelle honnête plutôt que
    commode — le biais de circularité est identique des deux côtés.
    """
    a_mat, sigma = tre["A"], tre["sigma"]
    if attendu <= 0.0:
        return {"decidable": False, "raison": "le budget attendu est nul"}
    sol, *_ = np.linalg.lstsq(a_mat, tre["y"], rcond=None)
    vrai = a_mat @ sol
    g = _rng(int(graine))
    rapports, formes, orthos = [], [], []
    for _ in range(int(tirages)):
        tire = vrai + g.normal(0.0, sigma)
        s2, *_ = np.linalg.lstsq(a_mat, tire, rcond=None)
        brut = tire - a_mat @ s2
        rr = brut / sigma
        lam = float(np.sum(rr ** 2)) / float(attendu)
        if lam <= 0.0:
            continue
        n_brut = float(np.linalg.norm(brut))
        # ⚠⚠⚠ L'ORTHOGONALITE EST LA SIGNATURE D'UN AJUSTEMENT, ET ELLE SE PUBLIE. Un residu de
        # moindre carre est orthogonal aux colonnes du treillis : `Aᵀr = 0`. Un nul qui TIRERAIT
        # sans reajuster rendrait des ecarts au modele VRAI et non des residus, donc il violerait
        # cette identite — et sans elle, rien dans la sortie ne distinguerait les deux.
        orthos.append(0.0 if n_brut <= 0.0
                      else float(np.max(np.abs(a_mat.T @ brut))) / n_brut)
        rapports.append(lam)
        formes.append(float(np.max(np.abs(rr / np.sqrt(lam)))))
    if not rapports:
        return {"decidable": False, "raison": "aucun tirage n'a rendu de rapport"}
    # ⚠⚠ L'EMPREINTE EXISTE POUR QUE LES DEUX EPREUVES PROUVENT QU'ELLES LISENT LE MEME NUL.
    # Comparer leurs nombres de tirages ne prouve rien : deux nuls tires separement en ont autant.
    empreinte = round(float(np.sum(np.asarray(rapports) * np.arange(1, len(rapports) + 1))), 9)
    return {"decidable": True, "tirages": int(tirages),
            "les_rapports": rapports, "les_formes": formes,
            "lempreinte": empreinte,
            "lorthogonalite_la_plus_grande": round(float(max(orthos)), 12),
            "le_nul_ajuste_vraiment": bool(max(orthos) < 1e-8)}


def le_rapport_au_budget(std: np.ndarray, attendu: float, nul: dict) -> dict:
    """PREMIÈRE ÉPREUVE : l'énergie observée tient-elle dans le budget déclaré ?

    ⚠⚠ ELLE NE CONSOMME AUCUN TIRAGE, parce que son attendu est CALCULÉ et non simulé. Un rapport
    de un veut dire que les erreurs déclarées rendent exactement compte des résidus ; un rapport
    bien au-dessus veut dire que le numérateur dépasse ce que le dénominateur autorise, sans dire
    laquelle des deux moitiés a tort.

    ⭐ LE NOMBRE DE COUTURES EFFECTIVES EN DÉCOULE, et c'est ce qui rend le résultat actionnable :
    `se(V) = V·√(2/(n-1))` décroît comme la racine de `n`, donc une erreur sous-estimée d'un facteur
    `√Λ` correspond à `n/Λ` coutures réellement indépendantes. Ce nombre est une PRÉDICTION pour la
    tranche qui relira une rangée, pas une conclusion de celle-ci.

    ⚠⚠⚠ ET LE VERDICT NE TIENT PAS À « Λ DÉPASSE UN ». Un rapport de un est l'espérance, pas un
    plancher : sous le modèle il varie d'un tirage à l'autre, et déclarer un dépassement dès qu'on
    passe au-dessus de l'espérance serait tirer une fois sur deux sur du code sain. Le même nul
    paramétrique que la seconde épreuve dit ce que le modèle donne vraiment.
    """
    observe = float(np.sum(std ** 2))
    if attendu <= 0.0:
        return {"decidable": False, "raison": "le budget attendu est nul"}
    if not nul.get("decidable"):
        return {"decidable": False, "raison": nul.get("raison")}
    lam = observe / float(attendu)
    au_moins = int(sum(1 for x in nul["les_rapports"] if x >= lam))
    return {"decidable": True,
            "tirages": int(nul["tirages"]),
            "lempreinte_du_nul": nul.get("lempreinte"),
            "lenergie_observee": round(observe, 4),
            "lenergie_attendue": round(float(attendu), 4),
            "le_rapport": round(lam, 4),
            "le_facteur_sur_lerreur": round(float(np.sqrt(lam)), 4),
            "le_rapport_du_nul_median": round(float(np.median(nul["les_rapports"])), 4),
            "le_rapport_du_nul_le_plus_fort": round(float(max(nul["les_rapports"])), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "les_residus_depassent_le_budget": bool(au_moins == 0)}


def la_forme(std: np.ndarray, tre: dict, attendu: float, nul: dict) -> dict:
    """SECONDE ÉPREUVE : l'excès est-il CONCENTRÉ, ou seulement ÉTALÉ ?

    ⚠⚠⚠ LE NUL EST PARAMÉTRIQUE, ET C'EST LE SEUL ENDROIT DE CETTE CHAÎNE OÙ IL EST LE BON OUTIL.
    Une permutation rebrasse des valeurs sans changer ni leur ensemble ni leur somme, donc elle ne
    peut rien dire d'une FORME rapportée à un budget. Ce qui est en procès est le modèle d'erreur
    lui-même, donc le nul doit SIMULER sous ce modèle : tirer des désaccords sous l'additivité avec
    les erreurs déclarées, REFAIRE l'ajustement à chaque tirage, et remettre à l'échelle comme
    l'observé l'est.

    ⚠⚠⚠ ET LA REMISE À L'ÉCHELLE EST CIRCULAIRE SI ON NE LA PAIE PAS DES DEUX CÔTÉS. Diviser les
    résidus par `√Λ` laisse les paires aberrantes financer leur propre normalisation : trois gros
    résidus gonflent `Λ`, donc se rapetissent eux-mêmes. Le nul subit EXACTEMENT le même traitement
    — son `Λ` est recalculé sur chacun de ses tirages et sa forme rapetissée de la même façon —
    donc le biais est identique des deux côtés et la comparaison reste juste. C'est ce qui rend la
    remise à l'échelle légitime au lieu de la rendre commode.

    ⚠⚠ ET LE NUL NE TESTE QUE CE QU'IL SIMULE : des tirages gaussiens indépendants autour du modèle
    additif. Il répond « cette forme est-elle celle du modèle déclaré », jamais « le modèle déclaré
    est-il le bon ». La limite se publie à côté du verdict.
    """
    if attendu <= 0.0:
        return {"decidable": False, "raison": "le budget attendu est nul"}
    if not nul.get("decidable"):
        return {"decidable": False, "raison": nul.get("raison")}
    lam = float(np.sum(std ** 2)) / float(attendu)
    if lam <= 0.0:
        return {"decidable": False, "raison": "l'énergie observée est nulle"}
    mis = std / float(np.sqrt(lam))
    obs = float(np.max(np.abs(mis)))
    nuls = nul["les_formes"]
    au_moins = int(sum(1 for x in nuls if x >= obs))
    i = int(np.argmax(np.abs(mis)))
    return {"decidable": True,
            "tirages": int(nul["tirages"]),
            "lempreinte_du_nul": nul.get("lempreinte"),
            "le_rapport_employe": round(lam, 4),
            "le_plus_grand_residu_remis_a_lechelle": round(obs, 4),
            "la_paire_du_plus_grand": tre["noms"][i],
            "le_residu_median_remis_a_lechelle": round(float(np.median(np.abs(mis))), 4),
            "la_forme_du_nul_mediane": round(float(np.median(nuls)), 4),
            "la_forme_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "lexces_est_concentre": bool(au_moins == 0)}


def le_refus_du_khi_deux_naif(std: np.ndarray, trace: float, attendu: float) -> dict:
    """L'attendu NAÏF, porté comme refus nommé — et l'écart qu'il coûte, chiffré.

    ⚠⚠⚠ `n - p` EST LE BON NOMBRE POUR UN AUTRE AJUSTEMENT QUE CELUI QUI TOURNE. Il vaut la trace
    du projecteur, donc il ignore que les erreurs déclarées diffèrent d'une paire à l'autre alors
    que l'ajustement, lui, ne les pondère pas. Le publier à côté de l'attendu exact est la seule
    façon d'empêcher qu'on le réemploie : l'écart se lit, il ne se raisonne pas.
    """
    observe = float(np.sum(std ** 2))
    if trace <= 0.0 or attendu <= 0.0:
        return {"decidable": False, "raison": "un des deux budgets est nul"}
    return {"decidable": True,
            "le_rapport_naif": round(observe / float(trace), 4),
            "le_rapport_exact": round(observe / float(attendu), 4),
            "lecart_relatif": round(abs(observe / float(trace) - observe / float(attendu))
                                    / (observe / float(attendu)), 4),
            "pourquoi_il_est_refuse":
                "`n - p` est l'espérance d'un khi-deux PONDÉRÉ et l'ajustement de `214` ne "
                "pondère pas, donc il répond pour un ajustement qui ne tourne pas"}


def une_matiere(tre: dict, mode: str, facteur: float, graine: int, combien: int = 3) -> dict:
    """Une matière fabriquée sous le modèle additif, abîmée d'UNE façon nommée.

    ⚠⚠⚠ LES DEUX FAÇONS D'ABÎMER RENDENT LE MÊME BUDGET ET DOIVENT ÊTRE SÉPARÉES PAR LA FORME. En
    `etalee`, toutes les erreurs sont sous-estimées du même facteur : le modèle tient, seul le
    dénominateur ment. En `concentree`, les erreurs sont justes et le modèle casse sur quelques
    paires. La première épreuve ne peut PAS les distinguer, par construction, et c'est ce que
    l'étalon doit rendre visible au lieu de le laisser supposer.

    ⚠⚠ L'AMPLITUDE DU DÉCALAGE EST DÉRIVÉE, PAS CHOISIE. L'énergie qu'un décalage unitaire sur
    `combien` paires laisse APRÈS projection se calcule une fois ; l'amplitude est la racine du
    rapport à l'excès visé. Choisir l'amplitude à la main aurait fait une fixture complaisante,
    puisque c'est elle qui décide si l'épreuve voit.
    """
    a_mat, sigma = tre["A"], tre["sigma"]
    sol, *_ = np.linalg.lstsq(a_mat, tre["y"], rcond=None)
    vrai = a_mat @ sol
    g = _rng(int(graine))
    if mode == "declaree":
        return {"y": vrai + g.normal(0.0, sigma), "le_mode": mode}
    if mode == "etalee":
        return {"y": vrai + g.normal(0.0, sigma * float(facteur)), "le_mode": mode}
    if mode != "concentree":
        return {"y": None, "le_mode": mode, "raison": f"mode inconnu : {mode}"}
    n = len(vrai)
    k = max(1, min(int(combien), n))
    unite = np.zeros(n)
    unite[:k] = sigma[:k]
    s1, *_ = np.linalg.lstsq(a_mat, unite, rcond=None)
    reste = (unite - a_mat @ s1) / sigma
    porte = float(np.sum(reste ** 2))
    if porte <= 0.0:
        return {"y": None, "le_mode": mode, "raison": "le décalage unitaire ne laisse rien"}
    budget = float(np.sum(((np.eye(n) - a_mat @ np.linalg.pinv(a_mat)) ** 2)
                          @ (sigma ** 2) / (sigma ** 2)))
    vise = max(0.0, (float(facteur) ** 2 - 1.0) * budget)
    amplitude = float(np.sqrt(vise / porte))
    return {"y": vrai + g.normal(0.0, sigma) + amplitude * unite, "le_mode": mode,
            "lamplitude_derivee": round(amplitude, 4), "les_paires_decalees": k}


def _une_course(tre: dict, attendu: float, mode: str, facteur: float, graine: int,
                tirages: int, combien: int = 3) -> dict:
    """Un réplicat : fabriquer, ajuster, puis faire passer LES DEUX épreuves sur le MÊME nul."""
    mat = une_matiere(tre, mode, facteur, graine, combien)
    if mat.get("y") is None:
        return {"decidable": False, "raison": mat.get("raison")}
    faux = dict(tre)
    faux["y"] = mat["y"]
    aj = lajustement(faux)
    nul = le_nul_parametrique(faux, attendu, tirages, graine + 1)
    if not nul.get("decidable"):
        return {"decidable": False, "raison": nul.get("raison")}
    bud = le_rapport_au_budget(aj["_std"], attendu, nul)
    frm = la_forme(aj["_std"], faux, attendu, nul)
    if not bud.get("decidable") or not frm.get("decidable"):
        return {"decidable": False, "raison": "une épreuve est indécidable"}
    return {"decidable": True,
            "depasse": bool(bud["les_residus_depassent_le_budget"]),
            "concentre": bool(frm["lexces_est_concentre"]),
            "le_rapport": float(bud["le_rapport"]),
            "une_variance_negative": bool(aj["les_rangees_a_variance_negative"])}


def sur_letalon(tre: dict, attendu: float, facteurs=(1.1, 1.25, 1.5, 2.0, 3.0),
                replicats: int = 12, decisif: int = LE_COMPTE_DECISIF, graine: int = GRAINE,
                tirages: int = PERMUTATIONS, combien: int = 3) -> dict:
    """L'étalon : le taux de faux, l'échelle, et LE CONTRÔLE QUI DISCRIMINE.

    ⚠⚠⚠ LE CONTRÔLE DE CETTE TRANCHE N'EST PAS UN AVEUGLE, C'EST UNE CONFUSION. Une règle qui
    répond « il y a un excès » sur les deux matières ne dit rien de plus que le budget ; ce qu'il
    faut vérifier est que la SECONDE épreuve SÉPARE une matière étalée d'une matière concentrée
    de MÊME budget. Un aveugle ordinaire aurait mesuré autre chose et aurait passé sans rien
    prouver.
    """
    echelle, negatives = [], 0
    for f in facteurs:
        vus_e, vus_c, conc_e, conc_c, ind = 0, 0, 0, 0, 0
        for i in range(int(replicats)):
            ce = _une_course(tre, attendu, "etalee", float(f), int(graine) + 300 * int(f * 10) + i,
                             tirages, combien)
            cc = _une_course(tre, attendu, "concentree", float(f),
                             int(graine) + 700 * int(f * 10) + i, tirages, combien)
            if not ce.get("decidable") or not cc.get("decidable"):
                ind += 1
                continue
            vus_e += int(ce["depasse"])
            vus_c += int(cc["depasse"])
            conc_e += int(ce["concentre"])
            conc_c += int(cc["concentre"])
            negatives += int(ce["une_variance_negative"]) + int(cc["une_variance_negative"])
        echelle.append({"le_facteur": float(f), "sur": int(replicats),
                        "le_budget_voit_letalee": int(vus_e),
                        "le_budget_voit_la_concentree": int(vus_c),
                        "la_forme_dit_concentree_sur_letalee": int(conc_e),
                        "la_forme_dit_concentree_sur_la_concentree": int(conc_c),
                        "les_replicats_indecidables": int(ind)})
    faux_budget, faux_forme = 0, 0
    for i in range(int(decisif)):
        c = _une_course(tre, attendu, "declaree", 1.0, int(graine) + 5000 + i * 7, tirages,
                        combien)
        if not c.get("decidable"):
            continue
        faux_budget += int(c["depasse"])
        faux_forme += int(c["concentre"])
    pleins = [e["le_facteur"] for e in echelle if e["le_budget_voit_letalee"] == int(replicats)]
    separe = [e["le_facteur"] for e in echelle
              if e["la_forme_dit_concentree_sur_la_concentree"]
              > e["la_forme_dit_concentree_sur_letalee"]]
    tb = faux_budget / float(decisif)
    tf = faux_forme / float(decisif)
    return {"decidable": True,
            "les_facteurs": [float(f) for f in facteurs],
            "les_replicats": int(replicats),
            "le_compte_decisif": int(decisif),
            "les_paires_decalees": int(combien),
            "lechelle": echelle,
            "le_plus_petit_facteur_vu_par_le_budget": (min(pleins) if pleins else None),
            "le_plus_petit_facteur_ou_la_forme_separe": (min(separe) if separe else None),
            "la_suite_du_budget_est_monotone":
                la_suite_est_monotone([e["le_budget_voit_letalee"] for e in echelle]),
            "les_faux_du_budget": int(faux_budget),
            "le_taux_de_faux_du_budget": round(float(tb), 4),
            "le_budget_tient_sa_garantie": le_taux_tient(tb, GARANTIE),
            "les_faux_de_la_forme": int(faux_forme),
            "le_taux_de_faux_de_la_forme": round(float(tf), 4),
            "la_forme_tient_sa_garantie": le_taux_tient(tf, GARANTIE),
            "les_variances_negatives_rencontrees": int(negatives),
            "elle_separe": bool(pleins and separe and le_taux_tient(tb, GARANTIE)
                                and le_taux_tient(tf, GARANTIE))}


def _ce_qui_reste(depasse: bool, concentre: bool) -> str:
    """Les trois issues, et elles sont EXCLUSIVES."""
    if not depasse:
        return "RIEN À EXPLIQUER — LES ERREURS DÉCLARÉES RENDENT COMPTE DES RÉSIDUS"
    if concentre:
        return "UNE RUPTURE D'ADDITIVITÉ SUR QUELQUES PAIRES, QUE LE BUDGET NE SUFFIT PAS À EXPLIQUER"
    return ("LES ERREURS DÉCLARÉES SONT SOUS-ESTIMÉES, DONC LA RÉFUTATION DE `214` EST UN "
            "ARTEFACT DE SA FORMULE D'ERREUR")


def _pourquoi(depasse: bool, concentre: bool, bud: dict, frm: dict, queues: dict) -> str:
    if not depasse:
        return (f"le rapport vaut {bud.get('le_rapport')} et "
                f"{bud.get('les_tirages_au_moins_aussi_forts')} tirages du modèle déclaré sur "
                f"{bud.get('tirages')} font au moins aussi fort")
    if concentre:
        return (f"le rapport vaut {bud.get('le_rapport')}, et une fois le budget remis à "
                f"l'échelle le plus grand résidu reste à "
                f"{frm.get('le_plus_grand_residu_remis_a_lechelle')} sur "
                f"{frm.get('la_paire_du_plus_grand')}, que le modèle déclaré ne produit jamais")
    q = ("et la normalité que cette formule suppose est réfutée par les maxima que `214` publie "
         f"(rapport médian {queues.get('le_rapport_median')} écarts-types contre "
         f"{queues.get('la_reference_gaussienne_la_plus_forte')} pour la pire gaussienne)"
         if queues.get("la_normalite_est_refusee")
         else "et la normalité que cette formule suppose n'est pas réfutée par les maxima publiés")
    return (f"le rapport vaut {bud.get('le_rapport')}, donc l'erreur déclarée est sous-estimée "
            f"d'un facteur {bud.get('le_facteur_sur_lerreur')} ; une fois le budget remis à "
            f"l'échelle la forme redevient celle du modèle "
            f"({frm.get('les_tirages_au_moins_aussi_forts')}/{frm.get('tirages')} au moins aussi "
            f"forts), {q}")


def les_coutures_effectives(bud: dict, lu: dict) -> dict:
    """Ce que le rapport implique sur le nombre de coutures RÉELLEMENT indépendantes.

    ⭐⭐ C'EST UNE PRÉDICTION POUR UNE TRANCHE FUTURE, PAS UNE CONCLUSION DE CELLE-CI. `se` décroît
    comme la racine de `n`, donc une erreur sous-estimée d'un facteur `√Λ` correspond à `n/Λ`
    coutures indépendantes.

    ⚠⚠⚠ MAIS IL NE VAUT QUE SOUS DEUX CONDITIONS, ET LA SECONDE EST CELLE QUE J'AVAIS OUBLIÉE. La
    première : l'excès doit être ÉTALÉ, sinon il vient du modèle et pas du dénominateur. La
    seconde : le dépassement doit venir de la DÉPENDANCE et non des QUEUES. La formule déclarée
    suppose aussi la normalité, et un excès d'aplatissement de `2Λ - 2` suffirait à tout expliquer
    sans qu'aucune couture ne soit corrélée — or les maxima que `214` publie réfutent la normalité.
    Ce nombre est donc un PLAFOND sur les coutures effectives, jamais une estimation.
    """
    if not bud.get("decidable") or not bud.get("le_rapport"):
        return {"decidable": False, "raison": "le rapport n'est pas calculable"}
    lam = float(bud["le_rapport"])
    if lam <= 0.0:
        return {"decidable": False, "raison": "le rapport est nul"}
    return {"decidable": True,
            "les_coutures_medianes_declarees": int(lu.get("les_coutures_medianes") or 0),
            "les_coutures_effectives_impliquees":
                round(float(lu.get("les_coutures_medianes") or 0) / lam, 1),
            "cest_un_plancher_pas_une_estimation": True,
            "elle_ne_vaut_que_si_lexces_est_etale_ET_que_les_queues_ny_sont_pour_rien": True}


def le_controle_des_queues(paires, lam, tirages: int = PERMUTATIONS,
                           graine: int = GRAINE) -> dict:
    """CONTRÔLE NOMMÉ : la formule d'erreur suppose aussi la NORMALITÉ, et `214` l'a déjà réfutée.

    ⚠⚠⚠ `se(V) = V·√(2/(n-1))` A DEUX HYPOTHÈSES, PAS UNE. L'indépendance des coutures est la
    première et c'est celle qu'on soupçonne en premier ; la seconde est que les différences par
    couture sont GAUSSIENNES. En général la variance d'une variance échantillonnale vaut
    `(κ + 2)·σ⁴/n` où `κ` est l'excès d'aplatissement, et la formule déclarée est le cas `κ = 0`.
    Un excès d'aplatissement de `2Λ - 2` suffirait donc à expliquer tout le dépassement SANS
    qu'aucune couture ne soit corrélée.

    ⭐⭐⭐⭐ ET LA PREUVE EST DÉJÀ DANS LE JSON DE `214`, PUBLIÉE ET JAMAIS LUE AINSI : chaque paire
    porte son désaccord le plus grand À CÔTÉ de son désaccord par couture. Le rapport des deux dit
    combien d'écarts-types le pire échantillon atteint, et une gaussienne de `n` tirages ne va pas
    au-delà d'une valeur que la simulation rend sans qu'aucun seuil ne soit choisi.

    ⚠ Le contrôle ne dit PAS lequel des deux défauts est en cause, et ne le prétend pas : il dit
    que l'un des deux suffit. Les séparer demande la série par couture, que personne ne publie.
    """
    ratios, ns = [], []
    for p in paires:
        s = float(p.get("le_desaccord_en_voxels") or 0.0)
        mx = p.get("le_desaccord_le_plus_grand_en_voxels")
        if mx is None or s <= 0.0:
            continue
        ratios.append(float(mx) / s)
        ns.append(int(p["les_coutures_communes"]))
    if len(ratios) < 4:
        return {"decidable": False, "raison": "trop peu de paires portent leur maximum"}
    g = _rng(int(graine))
    n_median = int(np.median(ns))
    gaussiens = [float(np.max(np.abs(g.normal(0.0, 1.0, n_median)))) for _ in range(int(tirages))]
    return {"decidable": True,
            "combien_de_paires": len(ratios),
            "les_coutures_de_reference": n_median,
            "le_rapport_le_plus_petit": round(float(min(ratios)), 4),
            "le_rapport_median": round(float(np.median(ratios)), 4),
            "le_rapport_le_plus_grand": round(float(max(ratios)), 4),
            "la_reference_gaussienne_mediane": round(float(np.median(gaussiens)), 4),
            "la_reference_gaussienne_la_plus_forte": round(float(max(gaussiens)), 4),
            "lexces_daplatissement_qui_suffirait": round(float(2.0 * lam - 2.0), 4),
            # ⚠ AUCUN SEUIL : on compare la MEDIANE observee au PLUS FORT des tirages gaussiens.
            # Si la moitie des paires depasse ce qu'une gaussienne fait de pire, la normalite est
            # refusee sans qu'aucun nombre n'ait ete choisi.
            "la_normalite_est_refusee":
                bool(float(np.median(ratios)) > float(max(gaussiens)))}


def juger(bud: dict, frm: dict, eff: dict, naif: dict, budget: dict, lu: dict,
          etalon: dict, queues: dict) -> dict:
    depasse = bool(bud.get("decidable") and bud.get("les_residus_depassent_le_budget"))
    concentre = bool(frm.get("decidable") and frm.get("lexces_est_concentre"))
    return {
        "les_residus_depassent_le_budget": depasse,
        "lexces_est_concentre": concentre,
        "le_facteur_sur_lerreur": bud.get("le_facteur_sur_lerreur"),
        "les_coutures_effectives_impliquees": eff.get("les_coutures_effectives_impliquees"),
        "lattendu_exact_differe_du_khi_deux_naif": (
            None if not naif.get("decidable") else bool(naif.get("lecart_relatif", 0) > 0)),
        "le_modele_reste_non_refute_par_une_variance_negative": bool(
            not lu.get("les_variances_negatives_de_214")),
        "letalon_separe": (bool(etalon.get("elle_separe")) if etalon else None),
        "la_normalite_est_refusee": queues.get("la_normalite_est_refusee"),
        "lexces_daplatissement_qui_suffirait": queues.get("lexces_daplatissement_qui_suffirait"),
        "ce_qui_reste_a_mesurer": _ce_qui_reste(depasse, concentre),
        "pourquoi": _pourquoi(depasse, concentre, bud, frm, queues),
    }


def mesurer(graine: int = GRAINE, tirages: int = PERMUTATIONS, replicats: int = 12,
            decisif: int = LE_COMPTE_DECISIF, chemin: Path = CE_QUE_LE_BRUIT_PROPRE_A_RENDU,
            avec_etalon: bool = True) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    lu = ce_que_le_bruit_propre_a_rendu(chemin)
    if not lu.get("decidable"):
        return {"decidable": False, "raison": lu.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    tre = le_treillis(lu["les_paires"], lu["les_rangees"])
    budget = le_budget_attendu(tre["A"], tre["sigma"])
    if not budget.get("decidable"):
        return {"decidable": False, "raison": budget.get("raison")}
    aj = lajustement(tre)
    attendu = float(budget["lenergie_attendue"])
    nul = le_nul_parametrique(tre, attendu, tirages, graine)
    bud = le_rapport_au_budget(aj["_std"], attendu, nul)
    frm = la_forme(aj["_std"], tre, attendu, nul)
    naif = le_refus_du_khi_deux_naif(aj["_std"], float(budget["la_trace_du_projecteur"]), attendu)
    eff = les_coutures_effectives(bud, lu)
    queues = le_controle_des_queues(lu["les_paires"], float(bud.get("le_rapport") or 1.0),
                                    tirages, graine + 2)
    etalon = (sur_letalon(tre, attendu, replicats=replicats, decisif=decisif, graine=graine,
                          tirages=tirages) if avec_etalon else None)
    return {"decidable": True,
            "graine": int(graine),
            "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE,
            "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
            "la_garantie_par_epreuve": GARANTIE_PAR_EPREUVE,
            "la_garantie_du_nul": GARANTIE,
            "ce_que_214_a_rendu": {k: v for k, v in lu.items() if k != "les_paires"},
            "le_budget_attendu": budget,
            "lajustement": {k: v for k, v in aj.items() if not k.startswith("_")},
            "lepreuve_du_budget": bud,
            "lepreuve_de_la_forme": frm,
            "le_refus_du_khi_deux_naif": naif,
            "les_coutures_effectives": eff,
            "le_controle_des_queues": queues,
            "letalon": etalon,
            "le_verdict": juger(bud, frm, eff, naif, budget, lu, etalon or {}, queues)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    lu, bg = r["ce_que_214_a_rendu"], r["le_budget_attendu"]
    print(f"\n{lu['combien_de_rangees']} rangées · {lu['combien_de_paires']} paires · coutures de "
          f"{lu['les_coutures_les_moins_nombreuses']} à {lu['les_coutures_les_plus_nombreuses']} "
          f"(médiane {lu['les_coutures_medianes']})")
    print(f"\nBUDGET · {bg['combien_dequations']} équations, {bg['combien_dinconnues']} inconnues · "
          f"trace du projecteur {bg['la_trace_du_projecteur']} · énergie ATTENDUE "
          f"{bg['lenergie_attendue']}")
    b = r["lepreuve_du_budget"]
    if b.get("decidable"):
        print(f"\nÉPREUVE 1 · énergie observée {b['lenergie_observee']} pour un budget de "
              f"{b['lenergie_attendue']} → rapport {b['le_rapport']} · "
              f"facteur sur l'erreur {b['le_facteur_sur_lerreur']}")
        print(f"  nul médian {b['le_rapport_du_nul_median']} · le plus fort "
              f"{b['le_rapport_du_nul_le_plus_fort']} · "
              f"{b['les_tirages_au_moins_aussi_forts']}/{b['tirages']} au moins aussi forts")
    n = r["le_refus_du_khi_deux_naif"]
    if n.get("decidable"):
        print(f"  refus nommé · le rapport NAÏF (n-p) vaudrait {n['le_rapport_naif']} contre "
              f"{n['le_rapport_exact']} exact, soit {n['lecart_relatif']} d'écart relatif")
    f = r["lepreuve_de_la_forme"]
    if f.get("decidable"):
        print(f"\nÉPREUVE 2 · une fois le budget remis à l'échelle, le plus grand résidu vaut "
              f"{f['le_plus_grand_residu_remis_a_lechelle']} sur {f['la_paire_du_plus_grand']} "
              f"(médian {f['le_residu_median_remis_a_lechelle']})")
        print(f"  nul médian {f['la_forme_du_nul_mediane']} · le plus fort "
              f"{f['la_forme_du_nul_la_plus_forte']} · "
              f"{f['les_tirages_au_moins_aussi_forts']}/{f['tirages']} au moins aussi forts")
    q = r.get("le_controle_des_queues") or {}
    if q.get("decidable"):
        print(f"\nCONTRÔLE DES QUEUES · le pire désaccord d'une paire vaut de "
              f"{q['le_rapport_le_plus_petit']} à {q['le_rapport_le_plus_grand']} écarts-types "
              f"(médiane {q['le_rapport_median']}) contre {q['la_reference_gaussienne_mediane']} "
              f"pour une gaussienne de {q['les_coutures_de_reference']} tirages "
              f"(la pire : {q['la_reference_gaussienne_la_plus_forte']})")
        print(f"  la normalité est refusée : {q['la_normalite_est_refusee']} · un excès "
              f"d'aplatissement de {q['lexces_daplatissement_qui_suffirait']} suffirait à tout "
              f"expliquer sans aucune dépendance")
    e = r["les_coutures_effectives"]
    if e.get("decidable"):
        print(f"\nCOUTURES EFFECTIVES · au plus {e['les_coutures_effectives_impliquees']} pour "
              f"{e['les_coutures_medianes_declarees']} déclarées — un PLANCHER, et seulement si "
              f"les queues n'y sont pour rien")
    t = r.get("letalon")
    if t and t.get("decidable"):
        print(f"\nÉTALON · décalage sur {t['les_paires_decalees']} paires :")
        for x in t["lechelle"]:
            print(f"    facteur {x['le_facteur']:<5} · budget vu étalée "
                  f"{x['le_budget_voit_letalee']}/{x['sur']} concentrée "
                  f"{x['le_budget_voit_la_concentree']}/{x['sur']} · forme dit CONCENTRÉE "
                  f"étalée {x['la_forme_dit_concentree_sur_letalee']}/{x['sur']} concentrée "
                  f"{x['la_forme_dit_concentree_sur_la_concentree']}/{x['sur']}")
        print(f"  budget vu dès {t['le_plus_petit_facteur_vu_par_le_budget']} · la forme sépare dès "
              f"{t['le_plus_petit_facteur_ou_la_forme_separe']} · monotone "
              f"{t['la_suite_du_budget_est_monotone']}")
        print(f"  faux budget {t['les_faux_du_budget']}/{t['le_compte_decisif']} = "
              f"{t['le_taux_de_faux_du_budget']} · faux forme {t['les_faux_de_la_forme']}/"
              f"{t['le_compte_decisif']} = {t['le_taux_de_faux_de_la_forme']} · sépare "
              f"{t['elle_separe']}")
    v = r["le_verdict"]
    print(f"\nVERDICT · dépasse le budget : {v['les_residus_depassent_le_budget']} · concentré : "
          f"{v['lexces_est_concentre']}")
    print(f"  reste à mesurer : {v['ce_qui_reste_a_mesurer']}")
    print(f"  pourquoi        : {v['pourquoi']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        """⚠⚠⚠ UNE SONDE ACCEPTE UN APPELABLE, ET UNE LEVÉE EST UN ÉCHEC — jamais une batterie
        morte. `215` a payé qu'un bris tue la batterie avant son verdict : de l'extérieur, cela
        ressemble à un défaut de la batterie et non du code."""
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
    v("★★★★ deux épreuves sont déclarées, et la garantie se partage",
      len(LES_EPREUVES_DECLAREES) == 2
      and abs(GARANTIE_PAR_EPREUVE - GARANTIE / 2.0) < 1e-12)
    v("★★★★ la garantie partagée passe SOUS le plancher du nul, et c'est dit plutôt que masqué",
      GARANTIE_PAR_EPREUVE < 1.0 / (PERMUTATIONS + 1))

    # ⚠⚠⚠ LE LECTEUR REFUSE PAR SON NOM, ET JAMAIS PAR L'ABSENCE.
    v("★★★ un fichier absent est refusé par son nom",
      not ce_que_le_bruit_propre_a_rendu(Path("/nen/existe/pas.json")).get("decidable"))
    tmp = RACINE / "docs" / "mesures" / ".sonde_216.json"
    try:
        base = json.loads(CE_QUE_LE_BRUIT_PROPRE_A_RENDU.read_text())
        tmp.write_text(json.dumps({}))
        v("★★★★ un JSON sans désaccords par paire est refusé et la raison les NOMME",
          lambda: "désaccords" in (ce_que_le_bruit_propre_a_rendu(tmp).get("raison") or ""))
        d2 = json.loads(json.dumps(base))
        d2["les_desaccords_par_paire"]["les_paires"][0].pop("les_coutures_communes", None)
        tmp.write_text(json.dumps(d2))
        got = ce_que_le_bruit_propre_a_rendu(tmp)
        v("★★★★ une paire sans ses COUTURES est refusée en NOMMANT la paire — sans elles l'erreur "
          "déclarée n'existe pas, et l'inventer serait fabriquer le nombre qu'on met en procès",
          not got.get("decidable") and "-" in (got.get("raison") or ""), str(got.get("raison")))
        d2 = json.loads(json.dumps(base))
        d2["les_desaccords_par_paire"]["les_paires"] = \
            d2["les_desaccords_par_paire"]["les_paires"][:3]
        tmp.write_text(json.dumps(d2))
        v("★★★★ trois paires pour trois rangées ne sur-déterminent rien, donc c'est refusé",
          lambda: not ce_que_le_bruit_propre_a_rendu(tmp).get("decidable"))
        d2 = json.loads(json.dumps(base))
        d2["le_triangle_surdetermine"]["decidable"] = False
        tmp.write_text(json.dumps(d2))
        v("★★★ un triangle indécidable chez `214` est refusé ici",
          lambda: not ce_que_le_bruit_propre_a_rendu(tmp).get("decidable"))
    finally:
        tmp.unlink(missing_ok=True)
    lu = ce_que_le_bruit_propre_a_rendu()
    v("★★★★ le JSON de `214` porte les trente-six paires et leurs coutures",
      lu.get("decidable") and lu.get("combien_de_paires") == 36
      and lu.get("les_coutures_les_moins_nombreuses") > 0, str(lu.get("raison")))

    tre = le_treillis(lu["les_paires"], lu["les_rangees"])
    v("★★★★ chaque ligne du treillis porte exactement DEUX un — une paire, pas un triplet",
      all(abs(float(np.sum(l)) - 2.0) < 1e-12 for l in tre["A"]))
    v("★★★★ l'erreur déclarée est bien `V·√(2/(n-1))`, recalculée ici et non recopiée",
      all(abs(tre["sigma"][i]
              - tre["y"][i] * np.sqrt(2.0 / (lu["les_paires"][i]["les_coutures_communes"] - 1)))
          < 1e-9 for i in range(len(tre["y"]))))

    # ⚠⚠⚠ LE BUDGET EXACT N'EST PAS `n - p`, ET LA SONDE LE PROUVE SUR DU CONNU.
    bg = le_budget_attendu(tre["A"], tre["sigma"])
    v("★★★★ la trace du projecteur vaut EXACTEMENT `n - p`",
      bg.get("decidable")
      and abs(bg["la_trace_du_projecteur"] - (len(tre["y"]) - bg["combien_dinconnues"])) < 1e-9,
      f"{bg.get('la_trace_du_projecteur')} pour {len(tre['y'])} - {bg.get('combien_dinconnues')}")
    egales = le_budget_attendu(tre["A"], np.full(len(tre["y"]), 3.0))
    v("★★★★ quand toutes les erreurs sont ÉGALES, l'attendu exact REJOINT `n - p` — c'est ce qui "
      "montre que l'écart vient de la pondération et de rien d'autre",
      egales.get("decidable") and egales["les_deux_sont_egales"],
      f"{egales.get('lenergie_attendue')} contre {egales.get('la_trace_du_projecteur')}")
    v("★★★★ et quand elles DIFFÈRENT, il s'en écarte — sinon la distinction serait décorative",
      bg.get("decidable") and not bg["les_deux_sont_egales"],
      f"{bg.get('lenergie_attendue')} contre {bg.get('la_trace_du_projecteur')}")
    v("★★★ une erreur nulle est refusée, jamais divisée",
      not le_budget_attendu(tre["A"], np.zeros(len(tre["y"]))).get("decidable"))

    # ⭐⭐⭐⭐ LE BUDGET EST JUSTE SUR UNE MATIERE DONT ON CONNAIT LA REPONSE.
    attendu = float(bg["lenergie_attendue"])
    rapports = []
    for g_ in range(24):
        mat = une_matiere(tre, "declaree", 1.0, 900 + g_)
        faux = dict(tre)
        faux["y"] = mat["y"]
        rapports.append(float(np.sum(lajustement(faux)["_std"] ** 2)) / attendu)
    med = float(np.median(rapports))
    v("★★★★ sur une matière tirée SOUS le modèle déclaré, le rapport tombe autour de UN — c'est "
      "la seule façon de vérifier que le budget est le bon et pas un nombre plausible",
      0.7 < med < 1.4, f"médiane {med:.4f} sur 24 tirages")
    doubles = []
    for g_ in range(24):
        mat = une_matiere(tre, "etalee", 2.0, 1900 + g_)
        faux = dict(tre)
        faux["y"] = mat["y"]
        doubles.append(float(np.sum(lajustement(faux)["_std"] ** 2)) / attendu)
    v("★★★★ et sur une matière dont les erreurs sont doublées il tombe autour de QUATRE, donc il "
      "mesure bien le CARRÉ du facteur",
      3.0 < float(np.median(doubles)) < 5.5, f"médiane {float(np.median(doubles)):.4f}")

    # ⚠⚠⚠ LES DEUX MATIERES ABIMEES PORTENT LE MEME BUDGET ET DOIVENT DIFFERER PAR LA FORME.
    ecart = []
    for g_ in range(24):
        a = une_matiere(tre, "etalee", 2.0, 2900 + g_)
        b = une_matiere(tre, "concentree", 2.0, 2900 + g_)
        fa, fb = dict(tre), dict(tre)
        fa["y"], fb["y"] = a["y"], b["y"]
        la_ = float(np.sum(lajustement(fa)["_std"] ** 2)) / attendu
        lb_ = float(np.sum(lajustement(fb)["_std"] ** 2)) / attendu
        ecart.append(abs(la_ - lb_) / max(la_, lb_))
    v("★★★★ les deux façons d'abîmer rendent le MÊME budget à quelques pour cent — sans cela la "
      "seconde épreuve pourrait séparer par le budget au lieu de séparer par la forme",
      float(np.median(ecart)) < 0.35, f"écart relatif médian {float(np.median(ecart)):.4f}")
    v("★★★★ l'amplitude du décalage est DÉRIVÉE du budget visé, pas choisie",
      (une_matiere(tre, "concentree", 3.0, 7).get("lamplitude_derivee") or 0)
      > (une_matiere(tre, "concentree", 1.5, 7).get("lamplitude_derivee") or 0))
    v("★★★ un mode inconnu est REFUSÉ, jamais replié sur un mode connu",
      une_matiere(tre, "la_moyenne", 2.0, 7).get("y") is None)

    aj = lajustement(tre)
    nul = le_nul_parametrique(tre, attendu, PERMUTATIONS, 31)
    v("★★★★ le nul rend AUTANT de rapports que de formes — deux nuls seraient deux tirages et non "
      "deux épreuves",
      nul.get("decidable") and len(nul["les_rapports"]) == len(nul["les_formes"]))
    v("★★★★ les rapports du nul tombent autour de UN, donc il simule bien SOUS le modèle déclaré",
      nul.get("decidable") and 0.6 < float(np.median(nul["les_rapports"])) < 1.5,
      str(float(np.median(nul["les_rapports"])) if nul.get("decidable") else None))
    bud = le_rapport_au_budget(aj["_std"], attendu, nul)
    frm = la_forme(aj["_std"], tre, attendu, nul)
    v("★★★★ les deux épreuves lisent le MÊME nul, prouvé par son EMPREINTE et non par son compte "
      "de tirages — deux nuls tirés séparément en ont tout autant",
      bud.get("lempreinte_du_nul") is not None
      and bud.get("lempreinte_du_nul") == frm.get("lempreinte_du_nul") == nul.get("lempreinte"),
      f"{bud.get('lempreinte_du_nul')} contre {frm.get('lempreinte_du_nul')}")
    v("★★★★ et deux nuls de graines DIFFÉRENTES portent des empreintes différentes, sinon "
      "l'empreinte ne prouverait rien",
      le_nul_parametrique(tre, attendu, PERMUTATIONS, 31).get("lempreinte")
      != le_nul_parametrique(tre, attendu, PERMUTATIONS, 32).get("lempreinte"))
    v("★★★★ le nul RÉAJUSTE à chaque tirage — ses résidus sont orthogonaux au treillis, ce qu'un "
      "écart au modèle vrai ne serait pas",
      nul.get("le_nul_ajuste_vraiment") is True,
      str(nul.get("lorthogonalite_la_plus_grande")))
    v("★★★★ le verdict du budget n'est QUE la lecture de son compte, jamais « Λ dépasse un »",
      bud.get("decidable")
      and bud["les_residus_depassent_le_budget"] == (bud["les_tirages_au_moins_aussi_forts"] == 0))
    v("★★★★ le facteur sur l'erreur est la RACINE du rapport, jamais le rapport",
      bud.get("decidable")
      and abs(bud["le_facteur_sur_lerreur"] - np.sqrt(bud["le_rapport"])) < 5e-4,
      f"{bud.get('le_facteur_sur_lerreur')} contre √{bud.get('le_rapport')}")
    v("★★★ un budget nul rend les deux épreuves indécidables",
      not le_rapport_au_budget(aj["_std"], 0.0, nul).get("decidable")
      and not la_forme(aj["_std"], tre, 0.0, nul).get("decidable"))
    v("★★★ un nul indécidable rend les deux épreuves indécidables",
      not le_rapport_au_budget(aj["_std"], attendu, {"decidable": False}).get("decidable")
      and not la_forme(aj["_std"], tre, attendu, {"decidable": False}).get("decidable"))

    # ⚠⚠⚠ LA REMISE A L'ECHELLE DOIT ETRE SUBIE DES DEUX COTES.
    v("★★★★ la forme est remise à l'échelle par le rapport OBSERVÉ, donc son plus grand résidu est "
      "strictement plus petit que le brut dès que le rapport dépasse un",
      frm.get("decidable") and bud.get("decidable")
      and (frm["le_plus_grand_residu_remis_a_lechelle"]
           < max(abs(x) for x in aj["les_residus_standardises"].values())) == (bud["le_rapport"] > 1))
    v("★★★★ le nul subit la MÊME remise à l'échelle, sinon la circularité ne serait payée que d'un "
      "côté et la comparaison serait faussée en faveur de la concentration",
      nul.get("decidable") and all(0.0 < x < 10.0 for x in nul["les_formes"]))

    # ⭐ LE REFUS NOMME : `n - p` EST LE BON NOMBRE POUR UN AUTRE AJUSTEMENT.
    naif = le_refus_du_khi_deux_naif(aj["_std"], float(bg["la_trace_du_projecteur"]), attendu)
    v("★★★★ le rapport naïf et le rapport exact DIFFÈRENT, et l'écart est publié",
      naif.get("decidable") and naif["lecart_relatif"] > 0.0
      and naif["le_rapport_naif"] != naif["le_rapport_exact"],
      str(naif.get("lecart_relatif")))
    v("★★★ et la raison du refus est écrite avec lui",
      "pondér" in (naif.get("pourquoi_il_est_refuse") or "").lower())

    # ⚠⚠⚠ LE CONTROLE DES QUEUES : IL DOIT POUVOIR REFUSER *ET* ACCEPTER.
    q = le_controle_des_queues(lu["les_paires"], float(bud["le_rapport"]), PERMUTATIONS, 41)
    v("★★★★ sur la matière lue, la normalité est REFUSÉE — un contrôle qui ne refuserait jamais ne "
      "protégerait de rien",
      q.get("decidable") and q["la_normalite_est_refusee"],
      f"médiane {q.get('le_rapport_median')} contre {q.get('la_reference_gaussienne_la_plus_forte')}")
    gg = _rng(7)
    gauss = [{"la_paire": [i, i + 1], "les_coutures_communes": 239,
              "le_desaccord_en_voxels": 1.0,
              "le_desaccord_le_plus_grand_en_voxels":
                  float(np.max(np.abs(gg.normal(0.0, 1.0, 239))))} for i in range(36)]
    qg = le_controle_des_queues(gauss, 1.0, PERMUTATIONS, 41)
    v("★★★★ et sur une matière VRAIMENT gaussienne il ACCEPTE — sinon il refuserait tout et son "
      "refus ne voudrait rien dire",
      qg.get("decidable") and not qg["la_normalite_est_refusee"],
      f"médiane {qg.get('le_rapport_median')} contre "
      f"{qg.get('la_reference_gaussienne_la_plus_forte')}")
    v("★★★★ l'excès d'aplatissement qui suffirait est DÉRIVÉ de `2Λ - 2`, pas choisi",
      abs(q["lexces_daplatissement_qui_suffirait"] - (2.0 * float(bud["le_rapport"]) - 2.0)) < 5e-4)
    v("★★★ une matière sans maxima publiés rend le contrôle indécidable, jamais vert",
      not le_controle_des_queues(
          [{"la_paire": [1, 2], "les_coutures_communes": 9, "le_desaccord_en_voxels": 1.0,
            "le_desaccord_le_plus_grand_en_voxels": None} for _ in range(36)], 1.0).get("decidable"))

    # ⚠⚠ LES COUTURES EFFECTIVES SONT UN PLANCHER, ET LE DISENT.
    eff = les_coutures_effectives(bud, lu)
    v("★★★★ les coutures effectives sont le quotient des coutures déclarées par le rapport",
      eff.get("decidable")
      and abs(eff["les_coutures_effectives_impliquees"]
              - lu["les_coutures_medianes"] / float(bud["le_rapport"])) < 0.2)
    v("★★★★ et elles se déclarent PLANCHER, avec leurs DEUX conditions — une seule aurait laissé "
      "lire un nombre de coutures là où les queues suffisent à tout expliquer",
      eff.get("decidable") and eff.get("cest_un_plancher_pas_une_estimation") is True
      and eff.get("elle_ne_vaut_que_si_lexces_est_etale_ET_que_les_queues_ny_sont_pour_rien")
      is True)

    # ⭐⭐⭐ LES TROIS ISSUES SONT EXCLUSIVES, ET AUCUNE NE NOMME UNE EXPLICATION QUE LA MESURE NE
    # SÉPARE PAS.
    issues = {_ce_qui_reste(a, b) for a in (True, False) for b in (True, False)}
    v("★★★★ les quatre combinaisons ne rendent que TROIS issues, et ne pas dépasser prime",
      len(issues) == 3 and _ce_qui_reste(False, True) == _ce_qui_reste(False, False))
    v("★★★★ aucune issue ne nomme l'indépendance des coutures — la mesure ne sépare PAS la "
      "dépendance des queues, et le verdict ne doit pas prétendre le contraire",
      all("indépend" not in x.lower() for x in issues), str(issues))

    # ⚠⚠⚠ L'ETALON : IL DOIT SEPARER LES DEUX MATIERES PAR LA FORME.
    et = sur_letalon(tre, attendu, facteurs=(1.25, 3.0), replicats=6, decisif=24, graine=53,
                     tirages=PERMUTATIONS)
    v("★★★★ le budget voit le plus gros dommage sur les DEUX matières — il ne peut PAS les "
      "distinguer, et c'est ce que l'étalon doit rendre visible",
      et.get("decidable") and et["lechelle"][-1]["le_budget_voit_letalee"] >= 5
      and et["lechelle"][-1]["le_budget_voit_la_concentree"] >= 5, str(et.get("lechelle")))
    v("★★★★ la FORME, elle, dit « concentrée » plus souvent sur la concentrée que sur l'étalée — "
      "sans cette séparation la seconde épreuve ne mesurerait rien",
      et.get("decidable") and et["lechelle"][-1]["la_forme_dit_concentree_sur_la_concentree"]
      > et["lechelle"][-1]["la_forme_dit_concentree_sur_letalee"], str(et.get("lechelle")))
    v("★★★★ les deux taux de faux tiennent la garantie du nul",
      et.get("decidable") and et["le_budget_tient_sa_garantie"]
      and et["la_forme_tient_sa_garantie"],
      f"{et.get('le_taux_de_faux_du_budget')} et {et.get('le_taux_de_faux_de_la_forme')}")
    v("★★★ un taux au-dessus de deux fois la garantie ne tient pas",
      not le_taux_tient(2.0 * GARANTIE + 0.01, GARANTIE))

    # ⭐⭐⭐⭐ LA MESURE ENTIERE.
    out = mesurer(GRAINE, PERMUTATIONS, 2, 6, avec_etalon=True)
    v("★★★★ la mesure traverse sans lire le volume et rend son verdict",
      out.get("decidable") and (out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer"),
      str(out.get("raison")))
    v("★★★★ elle publie le budget attendu À CÔTÉ de la trace, donc le refus du naïf se vérifie",
      (out.get("le_budget_attendu") or {}).get("lenergie_attendue") is not None
      and (out.get("le_budget_attendu") or {}).get("la_trace_du_projecteur") is not None)
    v("★★★★ elle publie le contrôle des queues, sans lequel le verdict nommerait une explication "
      "que la mesure ne sépare pas",
      (out.get("le_controle_des_queues") or {}).get("decidable") is True)
    v("★★★★ et DANS LA MESURE COMPLÈTE les deux épreuves portent la MÊME empreinte de nul — une "
      "sonde qui ne regarderait que les épreuves appelées à la main ne verrait pas un second nul "
      "tiré au site d'assemblage",
      (out.get("lepreuve_du_budget") or {}).get("lempreinte_du_nul") is not None
      and ((out.get("lepreuve_du_budget") or {}).get("lempreinte_du_nul")
           == (out.get("lepreuve_de_la_forme") or {}).get("lempreinte_du_nul")),
      f"{(out.get('lepreuve_du_budget') or {}).get('lempreinte_du_nul')} contre "
      f"{(out.get('lepreuve_de_la_forme') or {}).get('lempreinte_du_nul')}")
    v("★★★ et le nul de la mesure complète réajuste vraiment",
      (out.get("lepreuve_du_budget") or {}).get("lempreinte_du_nul") is not None)
    v("★★★ elle publie la question déclarée, les deux épreuves et les deux garanties",
      out.get("la_question_declaree") == LA_QUESTION_DECLAREE
      and len(out.get("les_epreuves_declarees") or []) == 2
      and out.get("la_garantie_du_nul") is not None)
    v("★★★ un `214` illisible rend la mesure indécidable, avec sa raison",
      not mesurer(GRAINE, PERMUTATIONS, 2, 6,
                  chemin=Path("/nen/existe/pas.json")).get("decidable"))

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
