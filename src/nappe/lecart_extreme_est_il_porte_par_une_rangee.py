"""L'écart de couture extrême est-il porté par UNE rangée, ou par la colonne ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE SA STATISTIQUE NE SOIT CALCULÉE SUR LA MATIÈRE. Les sondes de
conception n'ont tourné que sur des matières fabriquées ; la question, l'épreuve, le nul, l'étalon et
les issues sont posés d'abord.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P63`. `217` a mesuré que le pire écart PAR COUTURE vaut
cinq écarts-types quand un échantillon gaussien n'en donne pas quatre, et la porte demande d'où il
vient. L'hypothèse à mettre en procès est un SAUT : un recalage qui manque une couture dans UNE
rangée, c'est-à-dire le transfert que le graal doit corriger sans humain. Si c'est le cas, les
rangées voisines le désignent — deux s'accordent, une s'écarte — et un vote de voisines remplace
l'humain à cet endroit.

⭐⭐⭐⭐ AUCUNE LECTURE NEUVE. `211` publie, pour chacune de ses trois rangées, la colonne de chaque
couture et le cumul de ses pas : la différence de deux positions consécutives EST le pas de la
couture. Les trois rangées se recouvrent sur les colonnes que leur intersection rend, et c'est la
matière entière de la tranche.

## La porte se trompait deux fois, et c'est dit avant de mesurer

⚠⚠⚠⚠ « DU BRUIT INDÉPENDANT RÉPARTIT L'ANOMALIE » EST FAUX DÈS QUE LE BRUIT A DES QUEUES. Une queue
lourde propre à une rangée tombe, elle aussi, sur une seule rangée à la fois : elle est concentrée
exactement comme un saut. Ce que la forme d'une colonne peut séparer n'est donc PAS un saut d'une
queue, mais un écart porté par UNE rangée d'un écart porté par TOUTES — une colonne difficile pour
la matière entière, où chaque rangée se trompe à sa façon. ⭐ C'est aussi la seule distinction qui
compte pour le graal : un vote de voisines corrige la première et ne peut rien contre la seconde.
⚠ Saut et queue propre à une rangée restent confondus, et la tranche le dit au lieu de le taire.

⚠⚠⚠⚠ ET LE NUL QU'ELLE PRESCRIVAIT NE TIENT PAS. Rebrasser les colonnes indépendamment par rangée
suppose que les anomalies des trois rangées sont trois séries libres. Elles ne le sont pas : à chaque
colonne elles somment à zéro, parce que la part partagée n'est connue que par leur moyenne. Les
rebrasser séparément fabrique des triplets qui n'ont pas la loi observée, même sans rien de
localisé. ⭐ La règle est portée comme CONTRÔLE NOMMÉ et son taux de faux est MESURÉ sur l'étalon —
précédent de `211` et de `214`, qui gardent la règle réfutée à côté plutôt que de l'effacer.

## L'épreuve, déclarée

À chaque colonne commune, les trois pas `p_r(c)` sont centrés par rangée, puis par colonne : la part
partagée — la géométrie que les trois lisent — s'annule EXACTEMENT, et il reste un vecteur
d'anomalie dans le plan des sommes nulles. Il est BLANCHI par la covariance que les bruits propres
des trois rangées lui donnent, ces bruits étant tirés des variances des trois différences deux à
deux. Blanchi, un bruit gaussien — et tout mélange d'échelle PARTAGÉ par les trois rangées d'une
colonne — a une direction uniforme et indépendante de sa taille.

⭐⭐⭐⭐ UN ÉCART PORTÉ PAR UNE RANGÉE A UNE DIRECTION PRÉCISE : l'image de l'axe de cette rangée. La
proximité d'une colonne est donc le plus grand cosinus de sa direction avec l'un des trois axes.

⭐⭐⭐⭐ LA STATISTIQUE est la proximité MOYENNE des colonnes FORTES, et une colonne est forte quand son
énergie blanchie dépasse ce que le maximum de `n` tirages gaussiens atteint : le quantile
`1 - 1/n` d'un khi-deux à deux degrés, soit `2·ln n`. Le seuil est DÉRIVÉ de la longueur, jamais
choisi, et il ne regarde que ce que la porte interroge — les écarts qu'une gaussienne n'explique pas.

⭐⭐⭐⭐ LE NUL rebrasse les proximités entre les colonnes, et rien d'autre. Il garde l'énergie de
chaque colonne et la loi des directions, et ne détruit que le lien entre la TAILLE d'un écart et sa
FORME. C'est exactement l'hypothèse nulle : une direction indépendante de la taille, ce que le bruit
gaussien et la colonne difficile satisfont tous deux. L'épreuve voit quand aucun des
`PERMUTATIONS` tirages n'égale la proximité observée.

## L'étalon, et ce qu'il doit montrer AVANT que le verdict ne veuille dire quelque chose

⚠⚠⚠ LE PIÈGE EST LA COLONNE DIFFICILE : des queues de la force que `217` a mesurée, mais PARTAGÉES
par les trois rangées d'une colonne. Une règle qui y tirerait prendrait des queues pour un saut, et
c'est l'erreur que la tranche existe pour éviter. ⚠⚠ La queue PROPRE à une rangée, de même loi,
est portée comme contrôle nommé : elle est localisée, donc la règle peut y tirer, et c'est dit.

⭐⭐⭐ LES SAUTS DE L'ÉTALON ONT LA TAILLE DU PLUS PETIT EXTRÊME QUE `217` A MESURÉ, relu et jamais
retapé : c'est la question « la règle voit-elle les écarts qu'on a réellement ? ».

⭐⭐⭐⭐ ET L'ÉTALON PORTE UNE ÉCHELLE EN NOMBRE DE RANGÉES. La sonde de conception, sur matière
fabriquée seulement, a montré qu'avec trois rangées un saut isolé de cinq écarts-types se laisse
à peine distinguer : trois axes à soixante degrés couvrent le plan, et une direction quelconque
passe souvent pour une rangée fautive. ⚠⚠ Si le verdict est un silence, il faut savoir combien de
rangées rendraient la question décidable, et c'est le seul nombre qu'une lecture future peut
demander.

## Les issues, exclusives

- l'étalon ne tient pas son taux de faux ou tire sur le piège : aucun verdict ;
- l'épreuve voit : les écarts extrêmes sont portés par une rangée à la fois ;
- elle ne voit pas et l'étalon la dit puissante au nombre de colonnes fortes observé : ils sont
  partagés par la colonne ;
- elle ne voit pas et l'étalon la dit aveugle : trois rangées ne décident pas, et l'échelle dit
  combien il en faut.

⚠⚠ LE TÉLESCOPAGE N'EST JAMAIS UN RÉSULTAT ICI. `d(198,197) + d(197,199) = d(198,199)` sert à ce à
quoi il peut servir : VÉRIFIER que les séries de paires publiées sont bien la différence des pas de
rangées publiés. C'est une identité arithmétique, et c'est pourquoi elle vérifie la lecture au lieu
de conclure.

Usage :
    uv run python src/nappe/lecart_extreme_est_il_porte_par_une_rangee.py --verifier
    uv run python src/nappe/lecart_extreme_est_il_porte_par_une_rangee.py \\
        --json docs/mesures/lecart_extreme_est_il_porte_par_une_rangee.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import chi2

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_recette_posee_sur_le_rouleau import PERMUTATIONS  # noqa: E402
from le_bruit_propre_croit_il_avec_lecartement import (la_suite_est_monotone,  # noqa: E402
                                                       le_taux_tient)
from ouvrir_les_quinze import _rng  # noqa: E402
from pourquoi_lerreur_declaree_est_trop_petite import LE_COMPTE_DECISIF  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LACCORD_A_RENDU = MESURES / "les_rangees_saccordent_elles_entre_elles.json"
CE_QUE_217_A_RENDU = MESURES / "pourquoi_lerreur_declaree_est_trop_petite.json"
GRAINE = 20261030
LA_TOLERANCE_DU_TELESCOPAGE = 1e-6

LA_QUESTION_DECLAREE = ("un écart de couture extrême est-il porté par UNE rangée — deux voisines "
                        "s'accordent, une s'écarte — ou par la colonne, où toutes se trompent ?")
LEPREUVE_DECLAREE = ("les colonnes fortes pointent-elles vers l'axe d'une rangée plus que le "
                     "rebrassage des directions ne le fait ?")
GARANTIE = 1.0 / (PERMUTATIONS + 1)
LES_COMPTES_DE_SAUTS = (1, 2, 3, 5)
LES_NOMBRES_DE_RANGEES = (3, 5, 7, 9)


def ce_que_laccord_a_rendu(chemin: Path = CE_QUE_LACCORD_A_RENDU) -> dict:
    """Les pas par rangée que `211` publie — relus, et VÉRIFIÉS contre ses séries de paires.

    ⚠⚠⚠ LE PAS D'UNE COUTURE EST LA DIFFÉRENCE DE DEUX POSITIONS CONSÉCUTIVES DU CUMUL, parce que le
    cumul de `211` part de zéro et ajoute un pas par couture : `n` coutures, `n+1` positions. Un
    cumul qui n'aurait pas une position de plus que ses colonnes n'est pas celui qu'on croit lire.

    ⚠⚠⚠ ET LA LECTURE EST VÉRIFIÉE PAR LE TÉLESCOPAGE, À CE À QUOI IL PEUT SERVIR. `211` publie aussi,
    pour chaque paire, la suite de ses désaccords sur son plus long tronçon. Chacune doit être EXACTEMENT
    la différence des pas des deux rangées aux mêmes colonnes. Une paire qui ne la rend pas est
    refusée par son nom : lire une autre suite sous ce nom serait `R4-L19` une fois de plus.
    """
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    marches = d.get("les_marches_separees")
    if not isinstance(marches, dict) or len(marches) < 3:
        return {"decidable": False, "raison": "`211` ne publie pas trois marches séparées"}
    pas = {}
    for nom, m in sorted(marches.items()):
        if not m.get("decidable"):
            return {"decidable": False, "raison": f"la marche de la rangée {nom} est indécidable"}
        cols, cum = m.get("les_colonnes"), m.get("le_cumul_en_voxels")
        if not isinstance(cols, list) or not isinstance(cum, list) or len(cum) != len(cols) + 1:
            return {"decidable": False,
                    "raison": (f"la rangée {nom} ne publie pas un cumul d'une position de plus "
                               f"que ses coutures")}
        marches_ = np.diff(np.asarray(cum, dtype=float))
        pas[int(nom)] = {int(c): float(s) for c, s in zip(cols, marches_)}
    desaccords = d.get("les_desaccords")
    if not isinstance(desaccords, dict) or not desaccords:
        return {"decidable": False, "raison": "`211` ne publie pas ses désaccords"}
    series, pire = {}, 0.0
    for nom, v in sorted(desaccords.items()):
        paire, tr = v.get("la_paire"), v.get("le_plus_long_troncon")
        s = v.get("les_ecarts_de_pas_du_troncon_en_voxels")
        if (not isinstance(paire, list) or len(paire) != 2 or not isinstance(tr, list)
                or len(tr) < 2 or not isinstance(s, list)):
            return {"decidable": False, "raison": f"la paire {nom} ne publie pas son tronçon"}
        a, b = int(paire[0]), int(paire[1])
        cols = list(range(int(tr[0]), int(tr[1]) + 1))
        if len(cols) != len(s) or a not in pas or b not in pas:
            return {"decidable": False,
                    "raison": f"la paire {nom} ne correspond à aucune marche publiée"}
        if any(c not in pas[a] or c not in pas[b] for c in cols):
            return {"decidable": False,
                    "raison": f"la paire {nom} porte une colonne qu'une de ses rangées n'a pas"}
        attendu = np.asarray([pas[a][c] - pas[b][c] for c in cols])
        ecart = float(np.max(np.abs(np.asarray(s, dtype=float) - attendu)))
        if ecart > LA_TOLERANCE_DU_TELESCOPAGE:
            return {"decidable": False,
                    "raison": (f"la paire {nom} ne rend pas la différence des pas de ses deux "
                               f"rangées (écart {ecart:.4g} voxel)")}
        pire = max(pire, ecart)
        series[nom] = {"la_paire": [a, b], "les_colonnes": cols,
                       "la_serie": [float(x) for x in s]}
    rangees = sorted(pas)
    communes = sorted(set.intersection(*[set(pas[r]) for r in rangees]))
    if len(communes) < 30:
        return {"decidable": False,
                "raison": f"les rangées ne partagent que {len(communes)} colonnes"}
    return {"decidable": True,
            "les_rangees": rangees,
            "les_colonnes_communes": communes,
            "combien_de_colonnes": len(communes),
            "la_premiere_colonne": int(communes[0]),
            "la_derniere_colonne": int(communes[-1]),
            "les_pas": [[pas[r][c] for r in rangees] for c in communes],
            "les_series_des_paires": series,
            "les_paires_sont_la_difference_des_rangees": True,
            "lecart_au_telescopage_le_plus_grand": pire}


def ce_que_217_a_rendu(chemin: Path = CE_QUE_217_A_RENDU) -> dict:
    """Les extrêmes et les aplatissements que `217` publie — relus, parce que l'étalon les injecte."""
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    rendu, queues = d.get("ce_que_211_a_rendu"), d.get("lepreuve_des_queues")
    if not isinstance(rendu, dict) or not isinstance(queues, dict) or not rendu:
        return {"decidable": False, "raison": "`217` ne publie ni ses extrêmes ni ses queues"}
    par = {}
    for nom, p in sorted(rendu.items()):
        x = p.get("le_plus_grand_ecart_par_couture_en_voxels")
        e = p.get("le_plus_grand_ecart_en_ecarts_types")
        k = (queues.get(nom) or {}).get("lexces_daplatissement")
        if x is None or e is None or k is None:
            return {"decidable": False,
                    "raison": f"`217` ne publie pas l'extrême et l'aplatissement de {nom}"}
        par[nom] = {"le_plus_grand_ecart_en_voxels": float(x),
                    "le_plus_grand_ecart_en_ecarts_types": float(e),
                    "lexces_daplatissement": float(k)}
    return {"decidable": True, "par_paire": par,
            # ⚠⚠ LE PLUS PETIT EXTREME, parce que l'etalon demande si la regle voit les ecarts
            # REELLEMENT mesures : si elle voit le plus petit, elle voit les autres.
            "le_plus_petit_extreme_en_voxels":
                min(p["le_plus_grand_ecart_en_voxels"] for p in par.values()),
            # ⚠⚠ LE PLUS GRAND APLATISSEMENT, parce que c'est le piege le plus dur.
            "le_plus_grand_aplatissement": max(p["lexces_daplatissement"] for p in par.values())}


def la_base_du_plan(k: int) -> np.ndarray:
    """Une base orthonormée du plan des sommes nulles — `k` lignes, `k-1` colonnes."""
    m = np.eye(int(k)) - 1.0 / float(k)
    w, vec = np.linalg.eigh(m)
    return vec[:, w > 0.5]


def les_bruits_propres(pas) -> dict:
    """La variance propre de chaque rangée, tirée des variances des différences deux à deux.

    ⭐⭐⭐ LA PART PARTAGÉE N'ENTRE DANS AUCUNE DIFFÉRENCE, donc `var(p_i - p_j) = σ_i² + σ_j²` et le
    système se résout sans elle. Trois rangées le résolvent exactement ; plus de trois le
    sur-déterminent et les moindres carrés tranchent.

    ⚠⚠ UNE VARIANCE NÉGATIVE EST REFUSÉE, jamais écrêtée : `212` a posé que les bruits propres sont
    positifs, et une matière qui en rendrait un négatif ne suit pas le modèle qui les définit.
    """
    p = np.asarray(pas, dtype=float)
    if p.ndim != 2 or p.shape[1] < 3 or p.shape[0] < 3:
        return {"decidable": False, "raison": "il faut trois rangées et trois colonnes au moins"}
    k = p.shape[1]
    lignes, droite = [], []
    for i in range(k):
        for j in range(i + 1, k):
            e = np.zeros(k)
            e[i] = e[j] = 1.0
            lignes.append(e)
            droite.append(float(np.var(p[:, i] - p[:, j])))
    s2, *_ = np.linalg.lstsq(np.asarray(lignes), np.asarray(droite), rcond=None)
    if np.any(s2 <= 0.0):
        return {"decidable": False,
                "raison": f"une variance propre est négative ou nulle ({np.round(s2, 4).tolist()})"}
    return {"decidable": True, "les_variances": [float(x) for x in s2]}


def les_directions(pas, variances) -> dict:
    """L'anomalie de chaque colonne, blanchie : son énergie, sa proximité, la rangée qu'elle désigne.

    ⚠⚠⚠ LE CENTRAGE PAR COLONNE EST CE QUI ANNULE LA PART PARTAGÉE, et il l'annule EXACTEMENT : tout
    ce que les rangées lisent en commun à une colonne disparaît de la moyenne retranchée.

    ⚠⚠ LE BLANCHIMENT EST CE QUI REND LA DIRECTION UNIFORME SOUS LE NUL. Sans lui, une rangée plus
    bruitée que les autres étirerait le nuage vers son propre axe, et le bruit gaussien passerait
    pour des écarts localisés sur elle.
    """
    p = np.asarray(pas, dtype=float)
    n, k = p.shape
    p = p - p.mean(axis=0, keepdims=True)
    a = p - p.mean(axis=1, keepdims=True)
    u = la_base_du_plan(k)
    c = u.T @ np.diag(np.asarray(variances, dtype=float)) @ u
    w, vec = np.linalg.eigh(c)
    if np.any(w <= 0.0):
        return {"decidable": False, "raison": "la covariance des anomalies n'est pas définie"}
    blanc = vec @ np.diag(w ** -0.5) @ vec.T
    z = (a @ u) @ blanc.T
    axes = (blanc @ u.T).T
    axes = axes / np.linalg.norm(axes, axis=1, keepdims=True)
    r2 = np.sum(z ** 2, axis=1)
    if np.any(r2 <= 0.0):
        return {"decidable": False, "raison": "une colonne n'a aucune anomalie"}
    cos = np.abs((z / np.sqrt(r2)[:, None]) @ axes.T)
    return {"decidable": True, "les_anomalies": a, "les_energies": r2,
            "les_proximites": cos.max(axis=1), "les_fautives": cos.argmax(axis=1)}


def le_seuil_des_colonnes_fortes(n: int, k: int) -> float:
    """Le maximum de `n` tirages gaussiens : le quantile `1 - 1/n` d'un khi-deux à `k-1` degrés.

    ⭐ DÉRIVÉ de la longueur et du nombre de rangées, jamais choisi. Avec trois rangées il vaut
    exactement `2·ln n`, puisque le khi-deux à deux degrés est une exponentielle.
    """
    return float(chi2.isf(1.0 / float(n), int(k) - 1))


def _proximite_des_fortes(dirs: dict, seuil: float):
    fortes = dirs["les_energies"] > seuil
    return (float(np.mean(dirs["les_proximites"][fortes])) if np.any(fortes) else None,
            int(np.sum(fortes)))


def lepreuve(pas, tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """L'ÉPREUVE DÉCLARÉE : les colonnes fortes pointent-elles vers l'axe d'une rangée ?

    ⚠⚠⚠ LE NUL NE REBRASSE QUE LES PROXIMITÉS. Chaque colonne garde son énergie, la loi des
    directions est gardée, et seul le lien entre la taille d'un écart et sa forme est détruit —
    c'est l'hypothèse nulle elle-même, que le bruit gaussien et la colonne difficile satisfont.
    """
    p = np.asarray(pas, dtype=float)
    bp = les_bruits_propres(p)
    if not bp.get("decidable"):
        return {"decidable": False, "raison": bp.get("raison")}
    dirs = les_directions(p, bp["les_variances"])
    if not dirs.get("decidable"):
        return {"decidable": False, "raison": dirs.get("raison")}
    n, k = p.shape
    seuil = le_seuil_des_colonnes_fortes(n, k)
    obs, m = _proximite_des_fortes(dirs, seuil)
    base = {"decidable": True, "tirages": int(tirages), "combien_de_colonnes": int(n),
            "combien_de_rangees": int(k), "le_seuil_denergie": round(seuil, 4),
            "combien_de_colonnes_fortes": m,
            "lenergie_la_plus_forte": round(float(np.max(dirs["les_energies"])), 4)}
    if obs is None:
        return {**base, "la_proximite_observee": None, "les_tirages_au_moins_aussi_forts": None,
                "elle_voit": False,
                "pourquoi_elle_se_tait": "aucune colonne ne dépasse le maximum gaussien"}
    g = _rng(int(graine))
    prox = dirs["les_proximites"]
    nuls = [float(np.mean(g.permutation(prox)[:m])) for _ in range(int(tirages))]
    au_moins = int(sum(1 for x in nuls if x >= obs))
    return {**base,
            "la_proximite_observee": round(obs, 4),
            "la_proximite_du_nul_mediane": round(float(np.median(nuls)), 4),
            "la_proximite_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "elle_voit": bool(au_moins == 0)}


def la_regle_de_la_porte(pas, tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """CONTRÔLE NOMMÉ : la même statistique, sous le nul que `R4-P63` prescrivait.

    ⚠⚠⚠ ELLE REBRASSE LES ANOMALIES INDÉPENDAMMENT PAR RANGÉE, puis les recentre par colonne pour
    les ramener dans le plan des sommes nulles — la complétion la plus fidèle de ce que la porte
    écrivait. Elle est calculée et PUBLIÉE, jamais suivie : les anomalies de trois rangées somment à
    zéro à chaque colonne, donc les rebrasser séparément fabrique des triplets d'une autre loi.
    """
    p = np.asarray(pas, dtype=float)
    bp = les_bruits_propres(p)
    if not bp.get("decidable"):
        return {"decidable": False, "raison": bp.get("raison")}
    dirs = les_directions(p, bp["les_variances"])
    if not dirs.get("decidable"):
        return {"decidable": False, "raison": dirs.get("raison")}
    n, k = p.shape
    seuil = le_seuil_des_colonnes_fortes(n, k)
    obs, m = _proximite_des_fortes(dirs, seuil)
    if obs is None:
        return {"decidable": True, "tirages": int(tirages), "combien_de_colonnes_fortes": 0,
                "elle_voit": False}
    g = _rng(int(graine))
    a = dirs["les_anomalies"]
    nuls = []
    for _ in range(int(tirages)):
        b = np.stack([g.permutation(a[:, r]) for r in range(k)], axis=1)
        d = les_directions(b, bp["les_variances"])
        t = _proximite_des_fortes(d, seuil)[0] if d.get("decidable") else None
        nuls.append(-1.0 if t is None else float(t))
    au_moins = int(sum(1 for x in nuls if x >= obs))
    return {"decidable": True, "tirages": int(tirages), "combien_de_colonnes_fortes": m,
            "la_proximite_observee": round(obs, 4),
            "la_proximite_du_nul_mediane": round(float(np.median(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "elle_voit": bool(au_moins == 0)}


def le_detail_des_extremes(lu: dict, dirs: dict, seuil: float) -> dict:
    """Où tombe l'extrême de chaque paire, et ce que les trois rangées y font — une DESCRIPTION.

    ⚠⚠⚠ CE N'EST PAS UNE PREUVE, ET C'EST ÉCRIT DANS LE NOM DES CHAMPS. Une colonne où deux rangées
    s'accordent et une s'écarte se produit souvent par hasard avec trois rangées ; c'est l'épreuve et
    l'étalon qui disent si l'ensemble dépasse le hasard. Ce détail dit OÙ regarder, pas ce que c'est.

    ⚠⚠ L'ACCORD DES DEUX AUTRES SE MESURE EN ÉCARTS-TYPES DE LEUR PROPRE PAIRE, sur les colonnes
    communes : c'est le désaccord ordinaire de ces deux rangées qui dit si elles s'accordent là.
    """
    rangees = lu["les_rangees"]
    communes = lu["les_colonnes_communes"]
    index = {c: i for i, c in enumerate(communes)}
    p = np.asarray(lu["les_pas"], dtype=float)
    out = {}
    for nom, s in sorted(lu["les_series_des_paires"].items()):
        x = np.asarray(s["la_serie"], dtype=float)
        centre = x - float(np.mean(x))
        i = int(np.argmax(np.abs(centre)))
        col = int(s["les_colonnes"][i])
        if col not in index:
            manque = [r for r in rangees if r not in s["la_paire"]]
            out[nom] = {"la_colonne": col, "dans_le_recouvrement": False,
                        "raison": (f"la rangée {manque[0] if manque else '?'} n'est pas lue sur "
                                   f"cette colonne")}
            continue
        j = index[col]
        fautive = int(dirs["les_fautives"][j])
        autres = [q for q in range(len(rangees)) if q != fautive]
        dq = p[:, autres[0]] - p[:, autres[1]]
        dq = dq - float(np.mean(dq))
        rms = float(np.sqrt(np.mean(dq ** 2)))
        e = dirs["les_energies"]
        out[nom] = {"la_colonne": col, "dans_le_recouvrement": True,
                    "les_anomalies_en_voxels": {str(r): round(float(dirs["les_anomalies"][j, q]), 4)
                                                for q, r in enumerate(rangees)},
                    "la_rangee_que_la_direction_designe": int(rangees[fautive]),
                    "la_proximite": round(float(dirs["les_proximites"][j]), 4),
                    "lenergie": round(float(e[j]), 4),
                    "le_rang_de_lenergie": int(1 + np.sum(e > e[j])),
                    "cest_une_colonne_forte": bool(e[j] > seuil),
                    "les_deux_autres": [int(rangees[q]) for q in autres],
                    "le_desaccord_des_deux_autres_en_ecarts_types":
                        (round(float(dq[j]) / rms, 4) if rms > 0 else None)}
    return out


def une_matiere(mode: str, n: int, ecarts_types, graine: int, amplitude: float = 0.0,
                combien: int = 0, aplatissement: float = 6.0):
    """Une matière fabriquée de `n` colonnes, dont on connaît la propriété.

    ⚠⚠⚠ `colonne_difficile` EST LE PIÈGE : une échelle à queues lourdes PARTAGÉE par toutes les
    rangées d'une colonne. `queue_propre` a EXACTEMENT la même loi par rangée, mais chaque rangée tire
    son échelle — la seule différence entre les deux est QUI partage l'échelle. Leur degré de liberté
    est DÉRIVÉ de l'aplatissement visé, `df = 4 + 6/κ`, comme chez `217`.

    ⚠⚠ UNE PART PARTAGÉE DIX FOIS PLUS FORTE QUE TOUT BRUIT PROPRE est ajoutée à chaque mode, pour
    que son annulation se voie : si elle fuyait, elle dominerait tout.
    """
    g = _rng(int(graine))
    sig = np.asarray(ecarts_types, dtype=float)
    k, n = len(sig), int(n)
    partage = np.cumsum(g.normal(0.0, 10.0 * float(sig.max()), n))[:, None]
    o = g.normal(0.0, 1.0, (n, k)) * sig
    df = 4.0 + 6.0 / max(1e-3, float(aplatissement))
    norme = np.sqrt(df / (df - 2.0))
    if mode == "colonne_difficile":
        o = o * (np.sqrt(df / g.chisquare(df, n)) / norme)[:, None]
    elif mode == "queue_propre":
        o = o * (np.sqrt(df / g.chisquare(df, (n, k))) / norme)
    elif mode == "saut":
        for c in g.choice(n, int(combien), replace=False):
            r = int(g.integers(k))
            o[c, r] += float(g.choice([-1.0, 1.0])) * float(amplitude)
    elif mode != "gaussienne":
        return None
    return partage + o


def _voit(mode, n, sig, graine, tirages, regle=lepreuve, **kw) -> dict:
    m = une_matiere(mode, n, sig, graine, **kw)
    if m is None:
        return {"decidable": False}
    r = regle(m, tirages, graine + 1)
    if not r.get("decidable"):
        return {"decidable": False}
    return {"decidable": True, "voit": bool(r["elle_voit"]),
            "vide": r.get("combien_de_colonnes_fortes", 0) == 0}


def _taux(mode, n, sig, graine, tirages, fois, regle=lepreuve, **kw) -> dict:
    vus, vides, ind = 0, 0, 0
    for i in range(int(fois)):
        c = _voit(mode, n, sig, int(graine) + i * 7, tirages, regle, **kw)
        if not c["decidable"]:
            ind += 1
            continue
        vus += int(c["voit"])
        vides += int(c["vide"])
    return {"les_vus": vus, "sur": int(fois), "les_sans_colonne_forte": vides,
            "les_indecidables": ind, "le_taux": round(vus / float(fois), 4)}


def _etendre(sig, k: int) -> list:
    """Les bruits propres mesurés, répétés jusqu'à `k` rangées — la matière, pas un choix."""
    s = [float(x) for x in sig]
    return [s[i % len(s)] for i in range(int(k))]


def le_plus_petit_nombre_de_rangees_qui_voit(par_rangs, replicats: int):
    """Le plus petit nombre de rangées qui voit PARTOUT — et qui résiste au piège à ce nombre-là.

    ⚠⚠⚠ UNE PUISSANCE SANS TAUX DE FAUX NE DIT RIEN : un nombre de rangées qui verrait tout en
    tirant aussi sur le piège ne désignerait pas des sauts, il désignerait n'importe quelle queue.
    """
    pleins = [int(e["combien_de_rangees"]) for e in par_rangs
              if int(e["les_vus"]) == int(replicats) and e.get("elle_resiste_au_piege")]
    return min(pleins) if pleins else None


def letalon_est_valide(taux_de_faux, taux_sur_le_piege) -> bool:
    """L'étalon tient s'il tient sa garantie sur le bruit ET sur le piège — jamais l'un sans l'autre."""
    return bool(le_taux_tient(taux_de_faux, GARANTIE) and le_taux_tient(taux_sur_le_piege, GARANTIE))


def sur_letalon(n: int, ecarts_types, amplitude: float, aplatissement: float,
                colonnes_fortes: int, replicats: int = 12, decisif: int = LE_COMPTE_DECISIF,
                graine: int = GRAINE, tirages: int = PERMUTATIONS,
                comptes=LES_COMPTES_DE_SAUTS, rangs=LES_NOMBRES_DE_RANGEES) -> dict:
    """L'étalon : le taux de faux, le PIÈGE, la règle de la porte, et les deux échelles.

    ⚠⚠⚠ LE CONTRÔLE QUI COMPTE EST LE PIÈGE. Des queues partagées ne doivent pas faire tirer la
    règle ; si elles le faisaient, la tranche prendrait des queues pour des sauts.

    ⭐⭐⭐⭐ L'ÉCHELLE EN RANGÉES EST TIRÉE AU NOMBRE DE COLONNES FORTES QUE LA MATIÈRE MONTRE. C'est la
    question « combien de rangées rendraient CETTE matière décidable », et le piège y est repassé à
    chaque nombre de rangées : une puissance sans taux de faux ne dit rien.
    """
    sig = [float(x) for x in ecarts_types]
    faux = _taux("gaussienne", n, sig, graine + 1000, tirages, decisif)
    piege = _taux("colonne_difficile", n, sig, graine + 3000, tirages, decisif,
                  aplatissement=aplatissement)
    propre = _taux("queue_propre", n, sig, graine + 5000, tirages, decisif,
                   aplatissement=aplatissement)
    porte_faux = _taux("gaussienne", n, sig, graine + 1000, tirages, decisif,
                       regle=la_regle_de_la_porte)
    m_haut = max(int(x) for x in comptes)
    porte_sauts = _taux("saut", n, sig, graine + 7000, tirages, decisif,
                        regle=la_regle_de_la_porte, amplitude=amplitude, combien=m_haut)
    declaree_sauts = _taux("saut", n, sig, graine + 7000, tirages, decisif,
                           amplitude=amplitude, combien=m_haut)
    sauts = []
    for m in comptes:
        t = _taux("saut", n, sig, graine + 9000 + int(m) * 101, tirages, replicats,
                  amplitude=amplitude, combien=int(m))
        sauts.append({"combien_de_sauts": int(m), **t})
    m_eff = max(1, int(colonnes_fortes))
    par_rangs = []
    for k in rangs:
        sk = _etendre(sig, k)
        t = _taux("saut", n, sk, graine + 20000 + int(k) * 211, tirages, replicats,
                  amplitude=amplitude, combien=m_eff)
        pk = _taux("colonne_difficile", n, sk, graine + 40000 + int(k) * 223, tirages, decisif,
                   aplatissement=aplatissement)
        par_rangs.append({"combien_de_rangees": int(k), **t,
                          "le_taux_sur_le_piege": pk["le_taux"],
                          "elle_resiste_au_piege": le_taux_tient(pk["le_taux"], GARANTIE)})
    tient = le_taux_tient(faux["le_taux"], GARANTIE)
    resiste = le_taux_tient(piege["le_taux"], GARANTIE)
    return {"decidable": True,
            "les_colonnes_par_matiere": int(n),
            "les_bruits_propres_en_voxels": [round(float(x), 4) for x in sig],
            "lamplitude_des_sauts_en_voxels": round(float(amplitude), 4),
            "laplatissement_du_piege": round(float(aplatissement), 4),
            "le_compte_decisif": int(decisif),
            "les_replicats": int(replicats),
            "les_colonnes_fortes_de_la_matiere": int(colonnes_fortes),
            "les_sauts_de_lechelle_en_rangees": int(m_eff),
            "le_faux": faux,
            "elle_tient_sa_garantie": tient,
            "le_piege": piege,
            "elle_resiste_au_piege": resiste,
            "la_queue_propre": propre,
            "la_regle_de_la_porte_sur_du_bruit": porte_faux,
            "la_regle_de_la_porte_tient_sa_garantie": le_taux_tient(porte_faux["le_taux"],
                                                                    GARANTIE),
            "la_regle_de_la_porte_sur_des_sauts": porte_sauts,
            "la_regle_declaree_sur_les_memes_sauts": declaree_sauts,
            "les_sauts_du_face_a_face": int(m_haut),
            "lechelle_en_sauts": sauts,
            "lechelle_en_sauts_est_monotone": la_suite_est_monotone([e["les_vus"] for e in sauts]),
            "lechelle_en_rangees": par_rangs,
            "lechelle_en_rangees_est_monotone":
                la_suite_est_monotone([e["les_vus"] for e in par_rangs]),
            "le_plus_petit_nombre_de_rangees_qui_voit":
                le_plus_petit_nombre_de_rangees_qui_voit(par_rangs, replicats),
            "elle_est_valide": letalon_est_valide(faux["le_taux"], piege["le_taux"])}


def _ce_qui_reste(valide: bool, voit: bool, puissante: bool, k_min) -> str:
    """Les quatre issues, et elles sont EXCLUSIVES."""
    if not valide:
        return "L'ÉTALON NE TIENT PAS : LE VERDICT EST RETENU"
    if voit:
        return ("LOCALISÉ : LES ÉCARTS EXTRÊMES SONT PORTÉS PAR UNE RANGÉE À LA FOIS, ET UN VOTE DE "
                "VOISINES LES DÉSIGNE")
    if puissante:
        return ("PARTAGÉ : LES ÉCARTS EXTRÊMES TOMBENT SUR DES COLONNES DIFFICILES POUR TOUTES LES "
                "RANGÉES, ET UN VOTE N'Y PEUT RIEN")
    combien = (f"{k_min}" if k_min is not None else "PLUS QUE L'ÉCHELLE N'EN PORTE")
    return f"INDÉCIDABLE AVEC TROIS RANGÉES : IL EN FAUT {combien}"


def juger(epreuve: dict, etalon: dict, porte: dict) -> dict:
    valide = bool(etalon.get("elle_est_valide"))
    voit = bool(epreuve.get("elle_voit"))
    k3 = next((e for e in etalon.get("lechelle_en_rangees") or []
               if e["combien_de_rangees"] == 3), None)
    puissante = bool(k3 and k3["les_vus"] == int(etalon.get("les_replicats") or 0))
    k_min = etalon.get("le_plus_petit_nombre_de_rangees_qui_voit")
    return {"lepreuve_voit": voit,
            "combien_de_colonnes_fortes": epreuve.get("combien_de_colonnes_fortes"),
            "letalon_est_valide": valide,
            "trois_rangees_suffisent_au_nombre_observe": puissante,
            "le_plus_petit_nombre_de_rangees_qui_voit": k_min,
            "la_regle_de_la_porte_voit": bool(porte.get("elle_voit")),
            "la_regle_de_la_porte_tient_sa_garantie":
                bool(etalon.get("la_regle_de_la_porte_tient_sa_garantie")),
            "ce_qui_reste_a_mesurer": _ce_qui_reste(valide, voit, puissante, k_min)}


def mesurer(graine: int = GRAINE, tirages: int = PERMUTATIONS, replicats: int = 12,
            decisif: int = LE_COMPTE_DECISIF, chemin: Path = CE_QUE_LACCORD_A_RENDU,
            chemin217: Path = CE_QUE_217_A_RENDU, avec_etalon: bool = True) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    lu = ce_que_laccord_a_rendu(chemin)
    if not lu.get("decidable"):
        return {"decidable": False, "raison": lu.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    par217 = ce_que_217_a_rendu(chemin217)
    if not par217.get("decidable"):
        return {"decidable": False, "raison": par217.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    p = np.asarray(lu["les_pas"], dtype=float)
    bp = les_bruits_propres(p)
    if not bp.get("decidable"):
        return {"decidable": False, "raison": bp.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    dirs = les_directions(p, bp["les_variances"])
    if not dirs.get("decidable"):
        return {"decidable": False, "raison": dirs.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    n, k = p.shape
    seuil = le_seuil_des_colonnes_fortes(n, k)
    ep = lepreuve(p, tirages, graine)
    porte = la_regle_de_la_porte(p, tirages, graine)
    detail = le_detail_des_extremes(lu, dirs, seuil)
    sig = [float(np.sqrt(x)) for x in bp["les_variances"]]
    etalon = (sur_letalon(n, sig, par217["le_plus_petit_extreme_en_voxels"],
                          par217["le_plus_grand_aplatissement"],
                          int(ep.get("combien_de_colonnes_fortes") or 0), replicats, decisif,
                          graine, tirages) if avec_etalon else None)
    return {"decidable": True,
            "graine": int(graine),
            "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE,
            "lepreuve_declaree": LEPREUVE_DECLAREE,
            "la_garantie_du_nul": GARANTIE,
            "ce_que_211_a_rendu": {x: v for x, v in lu.items()
                                   if x not in ("les_pas", "les_series_des_paires",
                                                "les_colonnes_communes")},
            "ce_que_217_a_rendu": par217,
            "les_bruits_propres_en_voxels": {str(r): round(s, 4)
                                            for r, s in zip(lu["les_rangees"], sig)},
            "lepreuve": ep,
            # ⚠⚠ CHAQUE COLONNE EST PUBLIEE, pour que l'epreuve se refasse a la main et que la
            # figure trace le nuage entier au lieu d'un resume.
            "par_colonne": {"les_colonnes": [int(c) for c in lu["les_colonnes_communes"]],
                            "les_energies": [round(float(x), 4) for x in dirs["les_energies"]],
                            "les_proximites": [round(float(x), 4) for x in dirs["les_proximites"]],
                            "les_rangees_designees": [int(lu["les_rangees"][int(i)])
                                                      for i in dirs["les_fautives"]]},
            "la_regle_de_la_porte": porte,
            "le_detail_des_extremes": detail,
            "letalon": etalon,
            "le_verdict": juger(ep, etalon or {}, porte)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    lu = r["ce_que_211_a_rendu"]
    print(f"\n{len(lu['les_rangees'])} rangées {lu['les_rangees']} · {lu['combien_de_colonnes']} "
          f"colonnes communes ({lu['la_premiere_colonne']}–{lu['la_derniere_colonne']}) · paires = "
          f"différence des rangées : {lu['les_paires_sont_la_difference_des_rangees']}")
    print(f"  bruits propres : {r['les_bruits_propres_en_voxels']}")
    e = r["lepreuve"]
    print(f"\nÉPREUVE · seuil {e['le_seuil_denergie']} · {e['combien_de_colonnes_fortes']} "
          f"colonnes fortes · énergie la plus forte {e['lenergie_la_plus_forte']}")
    if e.get("la_proximite_observee") is not None:
        print(f"  proximité observée {e['la_proximite_observee']} · nul médian "
              f"{e['la_proximite_du_nul_mediane']} le plus fort "
              f"{e['la_proximite_du_nul_la_plus_forte']} · "
              f"{e['les_tirages_au_moins_aussi_forts']}/{e['tirages']} au moins aussi forts · "
              f"voit {e['elle_voit']}")
    po = r["la_regle_de_la_porte"]
    print(f"  règle de la porte (contrôle nommé) · voit {po.get('elle_voit')} · "
          f"{po.get('les_tirages_au_moins_aussi_forts')}/{po.get('tirages')}")
    print("\nEXTRÊMES DE `217` :")
    for nom, d in sorted(r["le_detail_des_extremes"].items()):
        if not d["dans_le_recouvrement"]:
            print(f"  {nom} · colonne {d['la_colonne']} · hors du recouvrement : {d['raison']}")
            continue
        print(f"  {nom} · colonne {d['la_colonne']} · anomalies {d['les_anomalies_en_voxels']} · "
              f"désigne {d['la_rangee_que_la_direction_designe']} (proximité {d['la_proximite']}) "
              f"· énergie {d['lenergie']} rang {d['le_rang_de_lenergie']} forte "
              f"{d['cest_une_colonne_forte']} · les deux autres "
              f"{d['le_desaccord_des_deux_autres_en_ecarts_types']} σ")
    t = r.get("letalon")
    if t and t.get("decidable"):
        print(f"\nÉTALON · sauts de {t['lamplitude_des_sauts_en_voxels']} vx · piège κ = "
              f"{t['laplatissement_du_piege']}")
        print(f"  faux {t['le_faux']['les_vus']}/{t['le_faux']['sur']} · piège "
              f"{t['le_piege']['les_vus']}/{t['le_piege']['sur']} · queue propre "
              f"{t['la_queue_propre']['les_vus']}/{t['la_queue_propre']['sur']} · valide "
              f"{t['elle_est_valide']}")
        print(f"  règle de la porte · sur du bruit {t['la_regle_de_la_porte_sur_du_bruit']['les_vus']}"
              f"/{t['le_compte_decisif']} · sur {t['les_sauts_du_face_a_face']} sauts "
              f"{t['la_regle_de_la_porte_sur_des_sauts']['les_vus']}/{t['le_compte_decisif']} "
              f"contre {t['la_regle_declaree_sur_les_memes_sauts']['les_vus']} pour la déclarée")
        for x in t["lechelle_en_sauts"]:
            print(f"    {x['combien_de_sauts']} saut(s) · vu {x['les_vus']}/{x['sur']}")
        for x in t["lechelle_en_rangees"]:
            print(f"    {x['combien_de_rangees']} rangées · {t['les_sauts_de_lechelle_en_rangees']} "
                  f"saut(s) · vu {x['les_vus']}/{x['sur']} · piège {x['le_taux_sur_le_piege']}")
        print(f"  plus petit nombre de rangées qui voit : "
              f"{t['le_plus_petit_nombre_de_rangees_qui_voit']}")
    v = r["le_verdict"]
    print(f"\nVERDICT · {v['ce_qui_reste_a_mesurer']}")


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

    v("★★★ une seule question et une seule épreuve sont déclarées",
      isinstance(LA_QUESTION_DECLAREE, str) and isinstance(LEPREUVE_DECLAREE, str)
      and abs(GARANTIE - 1.0 / (PERMUTATIONS + 1)) < 1e-12)
    v("★★★ le compte décisif est celui que `210` a dérivé, importé et non recopié",
      LE_COMPTE_DECISIF == 171, str(LE_COMPTE_DECISIF))

    # ⚠⚠⚠ LE LECTEUR : LA SERIE DE PAIRE DOIT ETRE LA DIFFERENCE DES PAS DE RANGEES.
    v("★★★ un fichier absent est refusé par son nom",
      not ce_que_laccord_a_rendu(Path("/nen/existe/pas.json")).get("decidable"))
    tmp = RACINE / "docs" / "mesures" / ".sonde_218.json"
    try:
        base = json.loads(CE_QUE_LACCORD_A_RENDU.read_text())
        tmp.write_text(json.dumps({}))
        v("★★★★ un JSON sans marches séparées est refusé et la raison les NOMME",
          lambda: "marches" in (ce_que_laccord_a_rendu(tmp).get("raison") or ""))
        d2 = json.loads(json.dumps(base))
        nom0 = sorted(d2["les_desaccords"])[0]
        s0 = d2["les_desaccords"][nom0]["les_ecarts_de_pas_du_troncon_en_voxels"]
        s0[len(s0) // 2] += 0.5
        tmp.write_text(json.dumps(d2))
        got = ce_que_laccord_a_rendu(tmp)
        v("★★★★ une paire qui ne rend PAS la différence des pas de ses rangées est REFUSÉE par son "
          "nom — le télescopage vérifie la lecture, il ne conclut rien",
          not got.get("decidable") and nom0 in (got.get("raison") or ""), str(got.get("raison")))
        d2 = json.loads(json.dumps(base))
        r0 = sorted(d2["les_marches_separees"])[0]
        d2["les_marches_separees"][r0]["le_cumul_en_voxels"].pop()
        tmp.write_text(json.dumps(d2))
        got = ce_que_laccord_a_rendu(tmp)
        v("★★★★ un cumul qui n'a pas une position de plus que ses coutures est refusé par sa rangée",
          not got.get("decidable") and r0 in (got.get("raison") or ""), str(got.get("raison")))
        d2 = json.loads(json.dumps(base))
        d2["les_marches_separees"][r0]["decidable"] = False
        tmp.write_text(json.dumps(d2))
        v("★★★ une marche indécidable est refusée, jamais sautée",
          lambda: not ce_que_laccord_a_rendu(tmp).get("decidable"))
        d2 = json.loads(json.dumps(base))
        d2["les_desaccords"][nom0]["le_plus_long_troncon"][1] -= 1
        tmp.write_text(json.dumps(d2))
        v("★★★ un tronçon qui ne couvre pas sa série est refusé",
          lambda: not ce_que_laccord_a_rendu(tmp).get("decidable"))
        tmp.write_text(json.dumps({"les_marches_separees": base["les_marches_separees"]}))
        v("★★★ des marches sans désaccords sont refusées : sans eux rien ne vérifie la lecture",
          lambda: "désaccords" in (ce_que_laccord_a_rendu(tmp).get("raison") or ""))
        tmp.write_text("{ pas du json")
        v("★★★ un JSON illisible est refusé par son nom",
          lambda: "illisible" in (ce_que_laccord_a_rendu(tmp).get("raison") or ""))
    finally:
        if tmp.exists():
            tmp.unlink()

    def _sur(fn, *args, **kw):
        """Un calcul qui lève rend un refus nommé : la batterie ne meurt pas avant son verdict."""
        try:
            return fn(*args, **kw)
        except Exception as exc:  # noqa: BLE001
            return {"decidable": False, "raison": f"LEVÉE {type(exc).__name__}: {exc}"}

    lu = _sur(ce_que_laccord_a_rendu)
    v("★★★★ la lecture réelle passe la vérification par le télescopage",
      lambda: lu.get("decidable") and lu["les_paires_sont_la_difference_des_rangees"]
      and lu["lecart_au_telescopage_le_plus_grand"] <= LA_TOLERANCE_DU_TELESCOPAGE,
      str(lu.get("raison")))
    v("★★★★ les colonnes communes sont l'INTERSECTION des trois marches, dérivée et non tapée",
      lambda: lu["les_colonnes_communes"] == sorted(
          set.intersection(*[set(int(c) for c in m["les_colonnes"])
                             for m in json.loads(CE_QUE_LACCORD_A_RENDU.read_text())
                             ["les_marches_separees"].values()])))
    v("★★★★ chaque ligne de pas porte une valeur par rangée, dans l'ordre des rangées",
      lambda: all(len(x) == len(lu["les_rangees"]) for x in lu["les_pas"])
      and lu["les_rangees"] == sorted(lu["les_rangees"]))
    v("★★★★ le pas d'une couture est la DIFFÉRENCE de deux positions du cumul, pas la position",
      lambda: abs(lu["les_pas"][0][0] - float(np.diff(np.asarray(
          json.loads(CE_QUE_LACCORD_A_RENDU.read_text())["les_marches_separees"]
          [str(lu["les_rangees"][0])]["le_cumul_en_voxels"], dtype=float))[
              json.loads(CE_QUE_LACCORD_A_RENDU.read_text())["les_marches_separees"]
              [str(lu["les_rangees"][0])]["les_colonnes"].index(lu["les_colonnes_communes"][0])]))
      < 1e-12)

    p217 = _sur(ce_que_217_a_rendu)
    v("★★★ `217` est relu : un extrême et un aplatissement par paire",
      lambda: p217.get("decidable") and len(p217["par_paire"]) == 3, str(p217.get("raison")))
    v("★★★★ l'étalon injecte le PLUS PETIT extrême et le PLUS GRAND aplatissement — jamais retapés",
      lambda: p217["le_plus_petit_extreme_en_voxels"]
      == min(x["le_plus_grand_ecart_en_voxels"] for x in p217["par_paire"].values())
      and p217["le_plus_grand_aplatissement"]
      == max(x["lexces_daplatissement"] for x in p217["par_paire"].values()))
    v("★★★ un `217` absent est refusé",
      lambda: not ce_que_217_a_rendu(Path("/nen/existe/pas.json")).get("decidable"))

    # ⭐⭐⭐ LA GEOMETRIE.
    v("★★★★ la base du plan est orthonormée et orthogonale au vecteur des uns",
      lambda: np.allclose(la_base_du_plan(3).T @ la_base_du_plan(3), np.eye(2))
      and np.allclose(np.ones(3) @ la_base_du_plan(3), 0.0))
    v("★★★ elle vaut pour neuf rangées aussi",
      lambda: la_base_du_plan(9).shape == (9, 8)
      and np.allclose(la_base_du_plan(9).T @ la_base_du_plan(9), np.eye(8)))
    v("★★★★ le seuil vaut EXACTEMENT 2·ln n avec trois rangées",
      lambda: abs(le_seuil_des_colonnes_fortes(105, 3) - 2.0 * np.log(105)) < 1e-9)
    v("★★★ et il croît avec le nombre de rangées, parce qu'un khi-deux plus large va plus loin",
      lambda: le_seuil_des_colonnes_fortes(105, 9) > le_seuil_des_colonnes_fortes(105, 3))

    g0 = _rng(3)
    sig0 = np.array([1.0, 1.5, 2.5])
    grand = g0.normal(0.0, 1.0, (40000, 3)) * sig0 + g0.normal(0.0, 5.0, (40000, 1))
    bp0 = _sur(les_bruits_propres, grand)
    v("★★★★ les bruits propres se retrouvent depuis les seules différences, part partagée comprise",
      lambda: bp0.get("decidable")
      and np.allclose(np.sqrt(bp0["les_variances"]), sig0, rtol=0.03), str(bp0))
    jumeaux = np.column_stack([grand[:300, 0], grand[:300, 0], grand[:300, 1] + 3.0])
    v("★★★★ une variance propre négative ou nulle est REFUSÉE, jamais écrêtée",
      lambda: not les_bruits_propres(jumeaux).get("decidable"))
    v("★★★ moins de trois rangées est refusé",
      lambda: not les_bruits_propres(grand[:, :2]).get("decidable"))
    dg = _sur(les_directions, grand, bp0.get("les_variances", [1.0, 1.0, 1.0]))
    v("★★★★ le blanchiment rend l'énergie moyenne égale au nombre de degrés (deux)",
      lambda: abs(float(np.mean(dg["les_energies"])) - 2.0) < 0.06,
      str(dg.get("raison") or ""))
    v("★★★ les anomalies somment à zéro à chaque colonne",
      lambda: np.allclose(dg["les_anomalies"].sum(axis=1), 0.0))
    pp = grand[:200]
    d1 = _sur(les_directions, pp, bp0.get("les_variances", [1.0, 1.0, 1.0]))
    d2_ = _sur(les_directions, pp + g0.normal(0.0, 50.0, (200, 1)),
               bp0.get("les_variances", [1.0, 1.0, 1.0]))
    v("★★★★ la part partagée s'annule EXACTEMENT : l'ajouter ne change ni énergie ni direction",
      lambda: np.allclose(d1["les_energies"], d2_["les_energies"], atol=1e-6)
      and np.allclose(d1["les_proximites"], d2_["les_proximites"], atol=1e-6))
    pur = g0.normal(0.0, 0.01, (50, 3))
    pur[17, 2] += 20.0
    dp = _sur(les_directions, pur, [1.0, 1.0, 1.0])
    v("★★★★ un saut pur dans une rangée pointe sur SON axe et désigne cette rangée",
      lambda: int(dp["les_fautives"][17]) == 2 and float(dp["les_proximites"][17]) > 0.999)
    # ⚠⚠ AVEC DES BRUITS PROPRES INEGAUX, L'AXE D'UNE RANGEE N'EST PLUS L'AXE BRUT : il faut le
    # blanchir comme l'anomalie, sinon un saut pur cesse de pointer sur sa propre rangee. ⚠ Les trois
    # variances sont TOUTES differentes : avec deux egales, l'axe de la troisieme est un axe propre
    # de la covariance et le blanchiment le laisse en place — une premiere version de cette sonde
    # passait pour cette raison, sans rien verifier.
    dpi = _sur(les_directions, pur, [1.0, 4.0, 9.0])
    v("★★★★ et il pointe encore sur son axe quand les bruits propres sont INÉGAUX — l'axe est "
      "blanchi comme l'anomalie",
      lambda: int(dpi["les_fautives"][17]) == 2 and float(dpi["les_proximites"][17]) > 0.999,
      str({k_: dpi.get(k_) for k_ in ("raison",)}))
    v("★★★ une proximité est un cosinus : entre zéro et un",
      lambda: float(dg["les_proximites"].min()) >= 0.0
      and float(dg["les_proximites"].max()) <= 1.0 + 1e-12)

    # ⭐⭐⭐⭐ L'EPREUVE PEUT DIRE OUI ET PEUT DIRE NON.
    fort = une_matiere("saut", 105, [2.0, 2.0, 2.6], 11, amplitude=30.0, combien=8)
    rf = _sur(lepreuve, fort, PERMUTATIONS, 12)
    v("★★★★ l'épreuve VOIT huit sauts francs", lambda: rf.get("elle_voit") is True, str(rf))
    v("★★★★ son nul VARIE d'un tirage à l'autre — un nul figé n'est pas un rebrassage",
      lambda: rf["la_proximite_du_nul_la_plus_forte"] > rf["la_proximite_du_nul_mediane"])
    calme = _rng(5).normal(0.0, 1.0, (105, 3))
    rc = _sur(lepreuve, calme, PERMUTATIONS, 6)
    v("★★★★ une matière sans saut ne voit rien, et DIT pourquoi quand elle se tait faute de colonne",
      lambda: rc.get("decidable") and (rc["elle_voit"] is False)
      and (rc["combien_de_colonnes_fortes"] > 0
           or "maximum" in rc.get("pourquoi_elle_se_tait", "")))
    v("★★★ l'épreuve est reproductible à graine égale",
      lambda: lepreuve(fort, PERMUTATIONS, 12) == lepreuve(fort, PERMUTATIONS, 12))
    rp = _sur(la_regle_de_la_porte, fort, PERMUTATIONS, 12)
    v("★★★★ la règle de la porte rebrasse les rangées SÉPARÉMENT : son nul n'est pas l'observé",
      lambda: rp.get("decidable") and rp["la_proximite_du_nul_mediane"] != rp["la_proximite_observee"],
      str(rp))

    # ⚠⚠ LE DETAIL DES EXTREMES, SUR UNE MATIERE CONSTRUITE.
    gx = _rng(9)
    pas_x = gx.normal(0.0, 1.0, (31, 3))
    pas_x[12, 0] -= 25.0
    communes_x = list(range(10, 41))
    serie_hors = [0.0] * 36
    serie_hors[0] = 40.0
    lu_x = {"les_rangees": [1, 2, 3], "les_colonnes_communes": communes_x,
            "les_pas": pas_x.tolist(),
            "les_series_des_paires": {
                "1-2": {"la_paire": [1, 2], "les_colonnes": communes_x,
                        "la_serie": (pas_x[:, 0] - pas_x[:, 1]).tolist()},
                "1-3": {"la_paire": [1, 3], "les_colonnes": list(range(5, 41)),
                        "la_serie": serie_hors}}}
    bx = les_bruits_propres(pas_x)
    dx = _sur(les_directions, pas_x, bx.get("les_variances", [1.0, 1.0, 1.0]))
    detx = _sur(le_detail_des_extremes, lu_x, dx, le_seuil_des_colonnes_fortes(31, 3))
    v("★★★★ un extrême NÉGATIF est trouvé : c'est le module qui compte, pas le signe",
      lambda: detx["1-2"]["la_colonne"] == 22 and detx["1-2"]["la_rangee_que_la_direction_designe"]
      == 1, str(detx))
    v("★★★★ un extrême hors du recouvrement est DIT, jamais décomposé avec une rangée absente",
      lambda: detx["1-3"]["dans_le_recouvrement"] is False and "2" in detx["1-3"]["raison"])
    lu_x10 = json.loads(json.dumps(lu_x))
    lu_x10["les_pas"] = (pas_x * 10.0).tolist()
    lu_x10["les_series_des_paires"]["1-2"]["la_serie"] = ((pas_x[:, 0] - pas_x[:, 1]) * 10.0).tolist()
    dx10 = _sur(les_directions, pas_x * 10.0, [x * 100.0 for x in bx.get("les_variances", [1.0])])
    detx10 = _sur(le_detail_des_extremes, lu_x10, dx10, le_seuil_des_colonnes_fortes(31, 3))
    v("★★★★ l'accord des deux autres se mesure en écarts-types de LEUR paire : dix fois plus de "
      "voxels ne change rien",
      lambda: abs(detx["1-2"]["le_desaccord_des_deux_autres_en_ecarts_types"]
                  - detx10["1-2"]["le_desaccord_des_deux_autres_en_ecarts_types"]) < 1e-3)

    # ⚠⚠ LES MATIERES FABRIQUEES SONT CE QU'ELLES DISENT.
    base_g = une_matiere("gaussienne", 105, [2.0, 2.0, 2.6], 21)
    sautee = une_matiere("saut", 105, [2.0, 2.0, 2.6], 21, amplitude=15.0, combien=3)
    v("★★★★ un mode inconnu est REFUSÉ, jamais replié sur un mode connu",
      lambda: une_matiere("la_moyenne", 10, [1.0, 1.0, 1.0], 1) is None)
    v("★★★★ le saut touche EXACTEMENT le nombre de colonnes demandé, une rangée chacune",
      lambda: int(np.sum(np.abs(sautee - base_g) > 1e-9)) == 3)
    cd = une_matiere("colonne_difficile", 60000, [1.0, 1.0, 1.0], 22, aplatissement=6.0)
    qp = une_matiere("queue_propre", 60000, [1.0, 1.0, 1.0], 22, aplatissement=6.0)

    # ⚠⚠ AVEC TROIS RANGEES AUCUNE PAIRE N'EST DISJOINTE D'UNE AUTRE — le telescopage encore —, donc
    # la difference entre les deux modes se lit sur la FORME des colonnes fortes, pas sur une
    # correlation de paires qui partagent forcement une rangee.
    def _ecart_de_forme(x):
        d_ = les_directions(x, les_bruits_propres(x)["les_variances"])
        e_, p_ = d_["les_energies"], d_["les_proximites"]
        haut = e_ >= np.quantile(e_, 0.99)
        return (float(np.mean(p_[haut]) - np.mean(p_)),
                float(np.std(p_[haut]) / np.sqrt(np.sum(haut))))

    # ⚠⚠ LES MARGES SONT QUATRE ERREURS-TYPES DE L'ESTIMATION ELLE-MEME, jamais un seuil regle :
    # une premiere version exigeait un ecart fixe de 0,015 et echouait a 0,0145, ce qui disait le
    # seuil et non la matiere.
    formes = _sur(lambda: (_ecart_de_forme(cd), _ecart_de_forme(qp)))
    v("★★★★ le PIÈGE partage l'échelle : ses colonnes fortes n'ont aucune forme privilégiée, alors "
      "que celles de la queue propre pointent vers un axe",
      lambda: abs(formes[0][0]) < 4.0 * formes[0][1]
      and formes[1][0] - formes[0][0] > 4.0 * float(np.hypot(formes[0][1], formes[1][1])),
      str(formes))
    v("★★★ les deux modes ont des queues : un aplatissement nettement au-dessus du gaussien",
      lambda: all(float(np.mean(((z_ - z_.mean()) / z_.std()) ** 4)) - 3.0 > 1.5
                  for z_ in (cd[:, 0] - cd[:, 1], qp[:, 0] - qp[:, 1])))
    v("★★★ les bruits propres mesurés se répètent jusqu'à neuf rangées, sans nombre choisi",
      lambda: _etendre([1.0, 2.0, 3.0], 7) == [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0])

    # ⚠⚠⚠ L'ETALON DOIT POUVOIR DIRE QU'IL NE TIENT PAS.
    et = _sur(sur_letalon, 105, [2.0, 1.95, 2.6], 15.0, 7.0, 1, replicats=3, decisif=12, graine=41,
              comptes=(1, 3), rangs=(3, 5))
    v("★★★★ l'étalon publie le piège, la queue propre, la porte, et les DEUX échelles",
      lambda: et.get("decidable") and et.get("le_piege") and et.get("la_queue_propre")
      and et.get("la_regle_de_la_porte_sur_du_bruit") and et.get("lechelle_en_sauts")
      and et.get("lechelle_en_rangees"))
    v("★★★★ il repasse le piège à CHAQUE nombre de rangées, sans quoi une puissance ne dit rien",
      lambda: all("le_taux_sur_le_piege" in e for e in et.get("lechelle_en_rangees") or []))
    v("★★★★ il PEUT rendre « non valide », donc son verdict n'est pas décoratif",
      lambda: isinstance(et.get("elle_est_valide"), bool))
    v("★★★ un taux au-dessus de deux fois la garantie ne tient pas",
      lambda: not le_taux_tient(2.0 * GARANTIE + 0.01, GARANTIE))
    v("★★★★ un étalon qui tire sur le PIÈGE n'est pas valide, même s'il tient sur le bruit",
      lambda: letalon_est_valide(0.0, 0.0) and not letalon_est_valide(0.0, 0.5)
      and not letalon_est_valide(0.5, 0.0))
    v("★★★★ un nombre de rangées qui voit tout en tirant sur le piège ne compte PAS",
      lambda: le_plus_petit_nombre_de_rangees_qui_voit(
          [{"combien_de_rangees": 5, "les_vus": 12, "elle_resiste_au_piege": False},
           {"combien_de_rangees": 7, "les_vus": 12, "elle_resiste_au_piege": True}], 12) == 7
      and le_plus_petit_nombre_de_rangees_qui_voit(
          [{"combien_de_rangees": 9, "les_vus": 11, "elle_resiste_au_piege": True}], 12) is None)
    faux_et = {"elle_est_valide": True, "les_replicats": 12,
               "lechelle_en_rangees": [{"combien_de_rangees": 3, "les_vus": 5},
                                       {"combien_de_rangees": 9, "les_vus": 12}],
               "le_plus_petit_nombre_de_rangees_qui_voit": 9}
    v("★★★★ la puissance du verdict est lue à TROIS rangées, pas au plus grand nombre de l'échelle",
      lambda: juger({"elle_voit": False}, faux_et, {})["trois_rangees_suffisent_au_nombre_observe"]
      is False and "IL EN FAUT 9" in juger({"elle_voit": False}, faux_et, {})
      ["ce_qui_reste_a_mesurer"])

    # ⭐⭐⭐ LES QUATRE ISSUES SONT EXCLUSIVES, ET LA VALIDITE PRIME.
    issues = {_ce_qui_reste(a, b, c, k) for a in (True, False) for b in (True, False)
              for c in (True, False) for k in (5, None)}
    v("★★★★ les combinaisons ne rendent que les issues posées, et un étalon invalide prime sur tout",
      _ce_qui_reste(False, True, True, 5) == _ce_qui_reste(False, False, False, None)
      and len({x.split(":")[0] for x in issues}) == 4)
    v("★★★★ le silence dit COMBIEN de rangées il faudrait, ou qu'aucune de l'échelle ne suffit",
      "IL EN FAUT 5" in _ce_qui_reste(True, False, False, 5)
      and "PLUS QUE" in _ce_qui_reste(True, False, False, None))

    # ⭐⭐⭐⭐ LA MESURE ENTIERE.
    out = _sur(mesurer, GRAINE, PERMUTATIONS, 2, 6, avec_etalon=True)
    v("★★★★ la mesure traverse sans lire le volume et rend son verdict",
      lambda: out.get("decidable") and (out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer"),
      str(out.get("raison")))
    v("★★★★ elle publie la règle de la porte à côté de l'épreuve, jamais à sa place",
      lambda: (out.get("la_regle_de_la_porte") or {}).get("decidable")
      and (out.get("lepreuve") or {}).get("decidable"))
    v("★★★★ elle situe l'extrême de chaque paire de `217`",
      lambda: len(out.get("le_detail_des_extremes") or {}) == 3)
    v("★★★★ elle publie chaque colonne, et les colonnes fortes du nuage sont celles que l'épreuve "
      "compte",
      lambda: sum(1 for e_ in out["par_colonne"]["les_energies"]
                  if e_ > out["lepreuve"]["le_seuil_denergie"])
      == out["lepreuve"]["combien_de_colonnes_fortes"]
      and len(out["par_colonne"]["les_colonnes"]) == out["lepreuve"]["combien_de_colonnes"])
    v("★★★★ l'étalon de la mesure injecte le plus petit extrême de `217`, relu",
      lambda: out["letalon"]["lamplitude_des_sauts_en_voxels"]
      == round(p217["le_plus_petit_extreme_en_voxels"], 4))
    v("★★★★ et son échelle en rangées est tirée au nombre de colonnes fortes que la matière montre",
      lambda: out["letalon"]["les_sauts_de_lechelle_en_rangees"]
      == max(1, int(out["lepreuve"]["combien_de_colonnes_fortes"])))
    v("★★★★ et le verdict LIT l'étalon : un étalon invalide retient le verdict",
      lambda: ((out.get("letalon") or {}).get("elle_est_valide")
               or "RETENU" in (out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer", "")))

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
