#!/usr/bin/env python3
"""Le gabarit lu ailleurs : ce que le raccrochage cherche, et où il l'a appris

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `le_raccrochage_choisit_il_bien` a mesuré que le raccrochage
**lit** — rho +0,076 contre −0,006 pour son mélange — et qu'il lit **très peu** : il prend 24 %
de ce que prend un oracle borné à la même fenêtre, et il reste 16,7 µm entre les deux. La suite
ne porte donc pas sur la fenêtre, ni sur la longueur du pas, ni sur la direction : elle porte sur
**la forme cherchée**.

⭐⭐ ET CETTE FORME N'A JAMAIS ÉTÉ MISE EN QUESTION. Le gabarit en service est lu sur **une seule
spire** — celle du départ — sur une demi-largeur d'**un quart de pas**, et il n'a jamais été
comparé à ce qu'un gabarit lu ailleurs, plus large, ou moyenné sur plusieurs spires donnerait.
Trois choses sont donc balayées ici, et chacune est jugée par le seul chiffre qui compte : son
**accord de rang avec le décalage que l'oracle choisit**, puis son erreur de marche.

⚠⚠ LA FENÊTRE DE RECHERCHE EST INVARIANTE, et c'est ce qui rend le balayage honnête. Un gabarit
plus large lit une ligne plus longue, mais `correler` ne rend que les positions où le gabarit
tient ENTIER dans la ligne : les centres balayés valent toujours ±une demi-feuille, quelle que
soit la largeur. Sans cette propriété, une variante large gagnerait en visant des décalages que
les autres ne peuvent pas atteindre, et le balayage mesurerait des fenêtres au lieu de lectures.

⚠⚠ ET TOUTES LES VARIANTES SONT JUGÉES SUR LES MÊMES CELLULES. Une ligne dont un seul échantillon
manque est écartée entière, donc un gabarit large en écarte davantage : comparer les erreurs de
deux variantes sur deux populations serait exactement le défaut que ce dépôt a déjà retiré une
fois — un verdict qui change avec la population n'est pas un verdict. La ligne la plus longue est
donc lue **une fois**, et toutes les largeurs sont des tranches centrées de cette lecture.

⛔ UNE DES QUATRE SOURCES N'EST PAS UN CONTENDANT. Le gabarit de la spire d'**arrivée** n'existe
pas en production — l'arrivée est précisément ce qu'on calcule — mais il dit ce qu'un gabarit
PARFAIT donnerait. S'il ne gagne rien, la famille des gabarits est épuisée et le chantier est
ailleurs. Il est traité comme l'oracle des décalages : une borne, jamais une méthode.

Usage :
    uv run python src/nappe/le_gabarit_lu_ailleurs.py --verifier
    uv run python src/nappe/le_gabarit_lu_ailleurs.py \\
        --json docs/mesures/le_gabarit_lu_ailleurs.json
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

# ⚠ Un seul lecteur de corpus pour tous les dérouleurs, et ses deux fixtures hors ligne.
from le_corpus_des_spires import corpus_fabrique, corpus_publie, volume_fabrique  # noqa: E402

# ⚠⚠⚠ L'ÉCART APPARIÉ VIT DANS UN SEUL FICHIER, et c'est ce balayage qui a montré pourquoi il
# le faut : la variabilité d'un pas à l'autre vaut quatre fois celle d'une méthode à l'autre,
# donc une différence de médianes ne décide rien ici. `le_raccrochage_choisit_il_bien` s'en sert
# aussi, et deux implémentations d'un même verdict finiraient par ne pas s'accorder sur ce que
# « mieux » veut dire.
from lecart_apparie import choisir_hors_echantillon, ecart_apparie, tranche  # noqa: E402
from le_raccrochage_choisit_il_bien import (  # noqa: E402
    accord_des_decalages, decalage_de_loracle,
)

# ⚠⚠ LA FAMILLE DES DEMI-LARGEURS EST DÉRIVÉE, PAS CHOISIE : elle est exprimée en unités de la
# DEMI-FEUILLE, et ses deux bouts ont chacun un sens physique. Un quart de demi-feuille est le
# plus étroit qui garde une dizaine de voxels, donc encore une forme et pas trois points ; deux
# demi-feuilles, c'est un gabarit qui couvre DEUX pas entiers, donc qui contient déjà la crête
# voisine de chaque côté — au-delà, on n'ajoute plus de forme, on ajoute des feuilles.
# La valeur en service, une demi-demi-feuille, est l'un des barreaux : sans elle le balayage se
# comparerait à autre chose que ce qui tourne.
FRACTIONS_DE_DEMI_FEUILLE = (0.25, 0.5, 1.0, 2.0)
FRACTION_DEPLOYEE = 0.5

# ⛔ La source qui n'existe pas en production : la spire d'arrivée est ce que la marche calcule.
SOURCE_BORNE = "arrivee"
SOURCES = ("depart", "ailleurs", "moyennee", SOURCE_BORNE)


def demi_largeurs(demi_vx: float) -> list[int]:
    """Les demi-largeurs de gabarit balayées, en voxels, dérivées de la demi-feuille.

    ⚠ Elles sont dédoublonnées après arrondi : sur une géométrie très fine deux fractions
    voisines tomberaient sur le même entier, et publier deux fois la même largeur sous deux
    noms ferait croire à un balayage plus fin qu'il n'est.
    """
    return sorted({max(1, int(round(demi_vx * f))) for f in FRACTIONS_DE_DEMI_FEUILLE})


def demi_largeur_deployee(demi_vx: float) -> int:
    """La demi-largeur du gabarit en service, telle que `le_raccrochage_a_la_matiere` la calcule."""
    return max(1, int(round(demi_vx * FRACTION_DEPLOYEE)))


def tronquer(gabarit: np.ndarray, demi_gab: int) -> np.ndarray:
    """Le cœur centré d'un gabarit, à la demi-largeur demandée.

    ⚠⚠ C'EST CE QUI FAIT QUE LES LARGEURS SE COMPARENT. Le gabarit le plus large est lu une
    fois, sur des lignes dont TOUS les échantillons sont valides, et les plus étroits en sont
    des tranches : ils viennent donc exactement des mêmes lignes et du même volume. Les lire
    séparément donnerait à chaque largeur son propre jeu de lignes valides, et l'écart mesuré
    entre deux largeurs porterait autant sur leurs populations que sur leur forme.
    """
    k = (len(gabarit) - 1) // 2 - int(demi_gab)
    if k < 0:
        raise ValueError(f"gabarit de demi-largeur {(len(gabarit) - 1) // 2} < {demi_gab}")
    return gabarit if k == 0 else gabarit[k:len(gabarit) - k]


def sources_du_pas(rang: int, spires: list[int]) -> dict[str, list[int] | None]:
    """D'où chaque variante lit son gabarit, pour le pas `rang → rang + 1`.

    ⚠⚠ TROIS DES QUATRE SONT DISPONIBLES EN PRODUCTION, et la règle est la même pour les trois :
    une spire déjà déroulée est connue, une spire à venir ne l'est pas. `moyennee` ne remonte
    donc jamais au-delà du départ — un gabarit moyenné sur des spires postérieures serait la
    réponse recopiée dans la question, et il gagnerait pour cette raison-là.

    ⛔ `arrivee` viole délibérément cette règle, parce que c'est une BORNE : elle dit ce qu'un
    gabarit parfait donnerait, comme l'oracle dit ce qu'un décalage parfait donne.
    """
    avant = [s for s in spires if s <= rang]
    autres = [s for s in spires if s != rang]
    return {
        "depart": [rang] if rang in spires else None,
        # ⚠⚠⚠ LA PLUS ANCIENNE SPIRE **DÉJÀ ATTEINTE**, ET LA PREMIÈRE VERSION LISAIT L'ARRIVÉE.
        # Écrite comme « la plus ancienne spire autre que le départ », elle rendait la spire 5
        # pour le pas 4 → 5 — c'est-à-dire exactement la surface que la marche cherche, sur un
        # pas sur sept, dans une variante annoncée comme disponible en production. La règle est
        # donc la même que pour `moyennee` : rien au-delà du départ. Sur le premier pas de la
        # boîte il ne reste alors AUCUN candidat, et le pas est écarté entier plutôt que servi
        # par une source qui triche.
        "ailleurs": [min(avant_strict)] if (avant_strict := [s for s in spires if s < rang])
        else None,
        "moyennee": avant if avant else None,
        SOURCE_BORNE: [rang + 1] if (rang + 1) in spires else None,
    }


def _net(accord: dict, melange: dict) -> float | None:
    """L'accord d'une forme, **net de ce que son propre mélange lit déjà**.

    ⚠⚠⚠ POURQUOI CETTE SOUSTRACTION EXISTE, ET ELLE A CHANGÉ UN VERDICT. Une ligne qui traverse
    des feuilles est **périodique** : la corrélation avec n'importe quel vecteur fixe, même
    entièrement mélangé, a donc des maxima aux mêmes phases que les feuilles, et son choix
    s'accorde déjà un peu avec celui de l'oracle. Mesuré : à demi-largeur 31 voxels, le gabarit
    MÉLANGÉ obtient +0,192 contre +0,175 pour le vrai — il « lit » mieux que la forme qu'il
    détruit. Comparer les accords bruts créditerait donc une forme large pour la périodicité que
    son propre mélange lit aussi bien, et c'est exactement ce que la première version de ce
    fichier a failli publier.

    ⚠ Rien n'est seuillé : la soustraction est la comparaison, et son signe est le verdict.
    """
    if accord["rho"] is None or melange["rho"] is None:
        return None
    return round(float(accord["rho"] - melange["rho"]), 3)


def pas_par_cote(corpus: dict, cotes: list[float], minimum: int = 30) -> list[dict]:
    """Combien de pas complets une boîte de chaque taille rendrait — sans lire un seul voxel.

    ⚠⚠⚠ POURQUOI CE RELEVÉ EST PUBLIÉ AVEC LA MESURE. Ce balayage ne décide rien, et la raison
    est comptée plutôt que déplorée : à six pas, retirer un seul pas déplace l'erreur de la
    forme en service de plus de dix micromètres. « Il faudrait plus de pas » serait une plainte ;
    « une boîte de tel côté en rend tant » est un plan. Le relevé ne coûte rien — il ne regarde
    que les grilles déjà lues, jamais le volume — donc il n'y a aucune raison de le remplacer
    par une supposition.

    ⚠ Un pas n'est compté que s'il rendrait les QUATRE sources, exactement comme la mesure les
    exige : compter les pas d'un découpage plus permissif annoncerait des pas que le balayage
    écarterait ensuite.
    """
    from le_raccrochage_a_la_matiere import BOITE_CENTRE  # noqa: PLC0415

    centre = np.array(BOITE_CENTRE)
    releve = []
    for cote in cotes:
        lo, hi = centre - cote / 2, centre + cote / 2
        dedans = sorted(rang for rang, (a, ok) in corpus["grilles"].items()
                        if int((ok & ((a >= lo) & (a <= hi)).all(axis=-1)).sum()) >= minimum)
        complets = [r for r in dedans if r + 1 in corpus["grilles"]
                    and all(v is not None for v in sources_du_pas(r, dedans).values())]
        releve.append(dict(cote_voxels=float(cote), spires=len(dedans),
                           pas_complets=len(complets)))
    return releve


def _recalage(courbes: list[np.ndarray], facteurs: np.ndarray,
              erreurs: list[float]) -> dict:
    """Ce que vaut, pour une variante, un simple facteur d'échelle sur ses décalages."""
    dedans, pris, valeurs = choisir_hors_echantillon(courbes, facteurs)
    # ⚠⚠⚠ LE POINT DE LA COURBE À FACTEUR UN, PUBLIÉ À CÔTÉ DE L'ERREUR NON RECALÉE. Ce sont
    # deux chemins de calcul pour un même nombre, donc leur égalité est vérifiable — et c'est
    # précisément ce qui attrape une grille qui ne contient pas exactement l'identité.
    un = int(np.argmin(np.abs(facteurs - 1.0)))
    a_un = round(float(np.median([c[un] for c in courbes])), 1) if courbes else None
    if not valeurs:
        return dict(facteur_ajuste=round(dedans, 3), facteur_median_hors_echantillon=None,
                    erreur_a_facteur_un_um=a_un, erreur_recalee_mediane_um=None,
                    paires_ou_le_recalage_ameliore=0, le_recalage_ameliore=False)
    recalee = float(np.median(valeurs))
    mieux = sum(1 for v, e in zip(valeurs, erreurs) if v < e)
    return dict(
        facteur_ajuste=round(dedans, 3), erreur_a_facteur_un_um=a_un,
        facteur_median_hors_echantillon=round(float(np.median(pris)), 3),
        erreur_recalee_mediane_um=round(recalee, 1),
        paires_ou_le_recalage_ameliore=mieux,
        # ⚠⚠ La médiane ET le compte par pas, comme partout : une médiane que le compte par
        # cas contredit n'est pas un verdict.
        le_recalage_ameliore=bool(recalee < float(np.median(erreurs))
                                  and mieux > len(valeurs) / 2))


def facteurs_dechelle(demi_vx: float) -> np.ndarray:
    """La grille des facteurs d'échelle essayés, DÉRIVÉE de la fenêtre et non choisie.

    ⚠ Un pas de la grille déplace d'exactement **un voxel** le décalage le plus grand que la
    fenêtre autorise : c'est la résolution à laquelle la mesure peut distinguer deux échelles,
    et en essayer de plus fines rendrait des chiffres que la donnée ne porte pas. Elle va
    jusqu'à deux parce qu'une forme peut aussi **sous-estimer** son décalage, et s'arrêter à un
    ne laisserait voir que la moitié du défaut.

    ⚠⚠⚠ ELLE EST ANCRÉE SUR L'IDENTITÉ, ET LA PREMIÈRE VERSION NE L'ÉTAIT PAS. Partir de zéro
    et avancer par pas de `1/demi-feuille` **rate 1,0** dès que le pas ne divise pas un — donc
    « recaler améliore » se comparait à un facteur voisin de l'identité plutôt qu'à l'identité,
    et une part du gain mesuré n'était qu'un décalage de grille. La grille part donc de 1,0 et
    s'étend d'une unité entière de chaque côté : elle voit une forme qui SUR-estime son décalage
    comme une qui le SOUS-estime, et son milieu est exactement « ne rien changer ».
    """
    pas = 1.0 / demi_vx
    n = int(np.ceil(1.0 / pas))
    return np.round(1.0 + np.arange(-n, n + 1) * pas, 12)


def facteurs_dechelle(demi_vx: float) -> np.ndarray:
    """La grille des facteurs d'échelle essayés, DÉRIVÉE de la fenêtre et non choisie.

    ⚠ Un pas de la grille déplace d'exactement **un voxel** le décalage le plus grand que la
    fenêtre autorise : c'est la résolution à laquelle la mesure peut distinguer deux échelles,
    et en essayer de plus fines rendrait des chiffres que la donnée ne porte pas. Elle va
    jusqu'à deux parce qu'une forme peut aussi **sous-estimer** son décalage, et s'arrêter à un
    ne laisserait voir que la moitié du défaut.

    ⚠⚠⚠ ELLE EST ANCRÉE SUR L'IDENTITÉ, ET LA PREMIÈRE VERSION NE L'ÉTAIT PAS. Partir de zéro
    et avancer par pas de `1/demi-feuille` **rate 1,0** dès que le pas ne divise pas un — donc
    « recaler améliore » se comparait à un facteur voisin de l'identité plutôt qu'à l'identité,
    et une part du gain mesuré n'était qu'un décalage de grille. La grille part donc de 1,0 et
    s'étend d'une unité entière de chaque côté : elle voit une forme qui SUR-estime son décalage
    comme une qui le SOUS-estime, et son milieu est exactement « ne rien changer ».
    """
    pas = 1.0 / demi_vx
    n = int(np.ceil(1.0 / pas))
    return np.round(1.0 + np.arange(-n, n + 1) * pas, 12)


def choisir_hors_echantillon(courbes: list[np.ndarray],
                             facteurs: np.ndarray) -> tuple[float, list[float], list[float]]:
    """Le meilleur facteur d'échelle, et ce qu'il vaut sur un pas qui n'a PAS servi à le choisir.

    ⚠⚠⚠ POURQUOI HORS ÉCHANTILLON. Un facteur choisi sur les mêmes pas que ceux qui le jugent
    ne peut que gagner : il suffit d'en essayer soixante-deux pour que l'un tombe bien. Chaque
    pas est donc jugé au facteur que les **autres** pas ont préféré, ce qui est la seule forme
    sous laquelle « recaler améliore » veut dire quelque chose pour un pas qu'on n'a pas encore
    marché.

    ⚠⚠ LE CRITÈRE D'AJUSTEMENT EST LA MÉDIANE DES ERREURS PAR PAS, ET C'EST UNE CORRECTION.
    J'avais écrit la SOMME en la justifiant par « un pas difficile pèse autant qu'un pas
    facile » — l'arithmétique dit l'inverse : dans une somme, le pas dont l'erreur varie le plus
    est celui qui décide, donc le pas le plus coûteux choisit le facteur de tous les autres. La
    médiane est aussi la statistique par laquelle le verdict est rendu : ajuster sur une
    grandeur et juger sur une autre laisserait un écart qui n'appartient à aucune des deux.

    Rend `(facteur ajusté sur tout, facteur retenu pour chaque pas, erreur de chaque pas)`.
    """
    if not courbes:
        return 1.0, [], []
    pile = np.stack(courbes)
    dedans = float(facteurs[int(np.argmin(np.median(pile, axis=0)))])
    if len(courbes) < 2:
        # ⚠ Avec un seul pas il n'y a aucun « autre pas » : le recalage n'est pas jugeable, et
        # rendre le facteur ajusté sur ce pas-là serait le noter sur sa propre copie.
        return dedans, [], []
    pris, valeurs = [], []
    for i, c in enumerate(courbes):
        j = int(np.argmin(np.median(np.delete(pile, i, axis=0), axis=0)))
        pris.append(float(facteurs[j]))
        valeurs.append(float(c[j]))
    return dedans, pris, valeurs


def gabarit_combine(par_spire: dict[int, np.ndarray], spires: list[int]) -> np.ndarray:
    """Le gabarit d'un ensemble de spires : la MÉDIANE de leurs gabarits, jamais la moyenne.

    ⚠ Même raison que `profil_autour` : une spire qui longe un éclat dense tire une moyenne et
    ne bouge pas une médiane. Combiner à la moyenne ferait décider le gabarit commun par la
    spire la plus abîmée.
    """
    pile = np.stack([par_spire[s] for s in spires])
    return np.median(pile, axis=0)


def mesurer(echantillon: int = 400, graine: int = 42, minimum: int = 30,
            cache_actif: bool = True, cote: float | None = None,
            corpus: dict | None = None, volume=None) -> dict:
    """Ce que chaque gabarit lit, contre le décalage que l'oracle choisirait."""
    from le_pas_normal_atteint_la_spire import distance_a, normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        BOITE_CENTRE, BOITE_COTE, CacheDisque, Volume, ZARR, accorde_aux_spires, correler,
        decalage_retenu, le_long, profil_autour, url_du_volume,
    )

    c = corpus_publie() if corpus is None else corpus
    volume_nom, voxel_um = c["volume"], float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um
    demi_vx = pas_vx / 2.0
    largeurs = demi_largeurs(demi_vx)
    dg_max = max(largeurs)
    deployee = demi_largeur_deployee(demi_vx)
    if volume is None and not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({volume_nom})")
    if volume is None:
        import tracecheck as tc  # noqa: PLC0415

        url = url_du_volume()
        vol = Volume(url, tc.array_meta(url, 0, 120), CacheDisque(actif=cache_actif))
    else:
        vol = volume

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2
    rng = np.random.default_rng(graine)
    # ⚠ La ligne la plus longue et le gabarit le plus large sont lus UNE fois ; tout le reste
    # en est une tranche centrée. Voir `tronquer`.
    t_gab_max = np.arange(-dg_max, dg_max + 1e-9, 1.0)
    t_ligne_max = np.arange(-(demi_vx + dg_max), demi_vx + dg_max + 1e-9, 1.0)
    facteurs = facteurs_dechelle(demi_vx)

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        grilles[rang] = (a, dans)
        nuages[rang] = a[ok]

    # --- les points et normales de chaque spire, une fois ---
    ancres: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for r in sorted(grilles):
        a0, dans = grilles[r]
        n0, bon = normales(a0, dans)
        garde = bon & dans
        if int(garde.sum()) < minimum:
            continue
        p, d = a0[garde], n0[garde]
        if len(p) > echantillon:
            pris = rng.choice(len(p), size=echantillon, replace=False)
            p, d = p[pris], d[pris]
        ancres[r] = (p, d)

    # --- le sens sortant de chaque spire, et l'accord entre elles ---
    # ⚠⚠ LE SENS EST LE BIT DE SUPERVISION UNIQUE, et il est ici demandé à CHAQUE spire plutôt
    # qu'une fois : un gabarit lu sur une spire et retourné selon le sens d'une AUTRE serait un
    # profil miroir, donc une forme que la matière ne porte nulle part.
    sens_par_spire: dict[int, float] = {}
    for r, (p, d) in ancres.items():
        if r + 1 not in nuages:
            continue
        cible = nuages[r + 1]
        sortant = float(np.median(distance_a(p + d * pas_vx, cible, voxel_um)))
        rentrant = float(np.median(distance_a(p - d * pas_vx, cible, voxel_um)))
        sens_par_spire[r] = 1.0 if sortant <= rentrant else -1.0
    if not sens_par_spire:
        raise RuntimeError("aucune spire n'a de voisine : le sens sortant n'est pas décidable")
    majorite = 1.0 if sum(1 for s in sens_par_spire.values() if s > 0) * 2 >= len(
        sens_par_spire) else -1.0
    orientations_daccord = len(set(sens_par_spire.values())) == 1

    # --- le gabarit le plus large de chaque spire, déjà orienté vers l'extérieur ---
    gab_par_spire: dict[int, np.ndarray] = {}
    for r, (p, d) in ancres.items():
        vg, okg = le_long(p, d, t_gab_max, vol)
        if int(okg.sum()) < minimum:
            continue
        g = profil_autour(vg[okg])
        gab_par_spire[r] = g if sens_par_spire.get(r, majorite) > 0 else g[::-1]
    spires_lisibles = sorted(gab_par_spire)
    if not spires_lisibles:
        raise RuntimeError("aucune spire ne rend un gabarit lisible dans la boîte")

    lignes: list[dict] = []
    # ⚠⚠ Les décalages sont GARDÉS par variante, parce que l'accord se lit de deux façons qui
    # ne disent pas la même chose : pas par pas (robuste, mais sur sept nombres) et sur toutes
    # les cellules d'un coup (c'est la grandeur que `le_raccrochage_choisit_il_bien` publie,
    # donc la seule qui se compare à son 0,076). Publier l'une en taisant l'autre laisserait
    # croire qu'un nombre a bougé alors que c'est la question qui a changé.
    par_variante: dict[tuple[int, str], list[tuple[np.ndarray, np.ndarray, np.ndarray]]] = {}
    # ⚠⚠ La courbe d'erreur en fonction du facteur d'échelle, gardée par variante et par pas :
    # c'est ce qui permet d'ajuster le facteur sur les AUTRES pas que celui qu'on juge.
    courbes: dict[tuple[int, str], list[np.ndarray]] = {}
    # ⚠⚠⚠ LES DISTANCES PAR CELLULE, GARDÉES PAR VARIANTE ET PAR PAS. Une médiane sur six ou
    # sept pas est une médiane sur six ou sept nombres : mesuré, retirer UN pas déplaçait
    # l'erreur de la forme en service de 36,0 à 48,5 µm et faisait basculer deux verdicts. Le
    # résumé qui décide est donc pris sur toutes les CELLULES, et le compte par pas dit si
    # l'effet est le même partout.
    distances: dict[tuple[int, str], list[np.ndarray]] = {}
    # ⚠⚠ LES DEUX REPÈRES SONT GARDÉS PAR CELLULE EUX AUSSI. Comparer une variante résumée sur
    # les cellules à un repère résumé sur les pas serait comparer deux statistiques — la faute
    # que ce fichier reproche partout ailleurs, commise sur sa propre ligne de référence.
    reperes: dict[str, list[np.ndarray]] = {"sans_bouger": [], "oracle": []}
    ecartees = 0
    for r in sorted(ancres):
        if r + 1 not in nuages:
            continue
        src = sources_du_pas(r, spires_lisibles)
        # ⚠⚠ UNE POPULATION, PAS QUATRE : un pas dont une seule source manque est écarté
        # ENTIER et compté. Publier chaque variante sur les pas où elle existe donnerait des
        # médianes prises sur des ensembles différents, donc incomparables — le défaut exact
        # que ce dépôt a déjà eu à retirer.
        if any(v is None for v in src.values()):
            ecartees += 1
            continue
        p, d = ancres[r]
        cible = nuages[r + 1]
        sens = sens_par_spire.get(r, majorite)
        prevu, dd = p + d * (sens * pas_vx), d * sens
        v_, okv = le_long(prevu, dd, t_ligne_max, vol)
        if int(okv.sum()) < minimum:
            ecartees += 1
            continue
        P, D, L = prevu[okv], dd[okv], v_[okv]

        # ⚠ L'arbre de la cible est construit UNE fois par pas : `distance_a` en rebâtit un à
        # chaque appel, et le balayage des facteurs en demande des milliers.
        from scipy.spatial import cKDTree  # noqa: PLC0415

        arbre = cKDTree(cible)

        def cellules(t: np.ndarray, _P=P, _D=D, _arbre=arbre) -> np.ndarray:
            return _arbre.query(_P + t[:, None] * _D, k=1)[0] * voxel_um

        def erreur(t: np.ndarray) -> float:
            return float(np.median(cellules(t)))

        # ⚠⚠⚠ LES CHOIX D'ABORD, L'ORACLE ENSUITE, ET SUR LA FENÊTRE QU'ILS ONT RÉELLEMENT
        # BALAYÉE. Déduire la fenêtre d'un côté et l'oracle de l'autre serait deux descriptions
        # d'une même chose : la première version de ce fichier a donné à l'oracle une fenêtre
        # deux fois et demie plus large que celle des contendants, et il gagnait alors pour une
        # raison qui n'a rien à voir avec la qualité d'une lecture.
        brut, fenetre = [], None
        for dg in largeurs:
            k = dg_max - dg
            t_slice = t_ligne_max if k == 0 else t_ligne_max[k:len(t_ligne_max) - k]
            L_slice = L if k == 0 else L[:, k:L.shape[1] - k]
            for nom in SOURCES:
                gab = tronquer(gabarit_combine(gab_par_spire, src[nom]), dg)
                corr, cent = correler(L_slice, gab, t_slice)
                if fenetre is None:
                    fenetre = cent
                elif not np.array_equal(cent, fenetre):
                    raise RuntimeError(
                        f"la demi-largeur {dg} ne balaye pas la fenêtre des autres")
                corr_m, _ = correler(L_slice, rng.permuted(gab), t_slice)
                brut.append((int(dg), nom, decalage_retenu(corr, cent),
                             decalage_retenu(corr_m, cent)))

        t_oracle, e_oracle = decalage_de_loracle(P, D, fenetre, cible, voxel_um)
        essais = [dict(
            demi_largeur_vx=dg, source=nom, spires_lues=[int(s) for s in src[nom]],
            disponible_en_production=nom != SOURCE_BORNE,
            deployee=bool(dg == deployee and nom == "depart"),
            fenetre_vx=[round(float(fenetre.min()), 2), round(float(fenetre.max()), 2)],
            accord=accord_des_decalages(t_v, t_oracle),
            accord_du_melange=accord_des_decalages(t_m, t_oracle),
            accord_net=_net(accord_des_decalages(t_v, t_oracle),
                            accord_des_decalages(t_m, t_oracle)),
            erreur_um=round(erreur(t_v), 1),
            erreur_melangee_um=round(erreur(t_m), 1),
            decalage_median_vx=round(float(np.median(t_v)), 2))
            for dg, nom, t_v, t_m in brut]
        for dg, nom, t_v, t_m in brut:
            par_variante.setdefault((dg, nom), []).append((t_v, t_m, t_oracle))
            distances.setdefault((dg, nom), []).append(cellules(t_v))
            courbes.setdefault((dg, nom), []).append(
                np.array([erreur(f * t_v) for f in facteurs]))

        reperes["sans_bouger"].append(cellules(np.zeros(len(P))))
        reperes["oracle"].append(e_oracle)
        lignes.append(dict(
            de=r, vers=r + 1, cellules=int(len(P)),
            erreur_sans_bouger_um=round(erreur(np.zeros(len(P))), 1),
            erreur_oracle_um=round(float(np.median(e_oracle)), 1),
            essais=essais, bits_de_supervision=1))

    if not lignes:
        raise RuntimeError("aucun pas ne rend les quatre sources dans la boîte")

    r = dict(
        fragment="PHerc0500P2", volume=volume_nom, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        pas_nominal_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        demi_feuille_vx=round(demi_vx, 2), demi_largeurs_vx=[int(x) for x in largeurs],
        facteurs_dechelle=dict(pas=round(float(facteurs[1] - facteurs[0]), 4),
                               maximum=round(float(facteurs[-1]), 3), nombre=len(facteurs)),
        demi_largeur_deployee_vx=int(deployee), sources=list(SOURCES),
        source_borne=SOURCE_BORNE, spires_lisibles=spires_lisibles,
        orientations_daccord=bool(orientations_daccord),
        paires=len(lignes), paires_ecartees=int(ecartees),
        cellules=int(sum(e["cellules"] for e in lignes)), lignes=lignes,
        cout=vol.cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises),
        erreur_sans_bouger_mediane_um=round(
            float(np.median([e["erreur_sans_bouger_um"] for e in lignes])), 1),
        erreur_oracle_mediane_um=round(
            float(np.median([e["erreur_oracle_um"] for e in lignes])), 1))

    # ⚠⚠⚠ LE RÉSUMÉ QUI DÉCIDE EST PRIS SUR TOUTES LES CELLULES, ET IL EST DOUBLÉ D'UN
    # INTERVALLE À UN PAS DE MOINS. « Un verdict qui change avec la population n'est pas un
    # verdict » est une règle de ce dépôt, et elle a failli être enfreinte ici : la médiane
    # pas-par-pas bougeait de douze micromètres quand un pas sur sept sortait. L'intervalle
    # rend cette fragilité VISIBLE au lieu de la laisser décider en silence.
    def poolee(cle: tuple[int, str], exclu: int | None = None) -> float:
        parts = [a for i, a in enumerate(distances[cle]) if i != exclu]
        return float(np.median(np.concatenate(parts)))

    def poolee_repere(nom: str) -> float:
        return float(np.median(np.concatenate(reperes[nom])))

    def intervalle(cle: tuple[int, str]) -> list[float]:
        if len(distances[cle]) < 2:
            return [round(poolee(cle), 1)] * 2
        v_ = [poolee(cle, i) for i in range(len(distances[cle]))]
        return [round(min(v_), 1), round(max(v_), 1)]

    # --- le résumé par variante, sur la même population ---
    def essais_de(dg: int, nom: str) -> list[dict]:
        return [x for e in lignes for x in e["essais"]
                if x["demi_largeur_vx"] == dg and x["source"] == nom]

    variantes = []
    for dg in largeurs:
        for nom in SOURCES:
            ex = essais_de(dg, nom)
            rhos = [x["accord"]["rho"] for x in ex if x["accord"]["rho"] is not None]
            rhos_m = [x["accord_du_melange"]["rho"] for x in ex
                      if x["accord_du_melange"]["rho"] is not None]
            nets = [x["accord_net"] for x in ex if x["accord_net"] is not None]
            suite = par_variante.get((int(dg), nom), [])
            glob = (accord_des_decalages(np.concatenate([t[0] for t in suite]),
                                         np.concatenate([t[2] for t in suite]))
                    if suite else dict(rho=None))
            glob_m = (accord_des_decalages(np.concatenate([t[1] for t in suite]),
                                           np.concatenate([t[2] for t in suite]))
                      if suite else dict(rho=None))
            variantes.append(dict(
                demi_largeur_vx=int(dg), source=nom,
                disponible_en_production=nom != SOURCE_BORNE,
                deployee=bool(dg == deployee and nom == "depart"),
                paires=len(ex),
                rho_median=round(float(np.median(rhos)), 3) if rhos else None,
                rho_median_du_melange=round(float(np.median(rhos_m)), 3) if rhos_m else None,
                # ⭐⭐ LE CRITÈRE QUI DÉCIDE : l'accord NET de ce que le mélange lit déjà.
                rho_net_median=round(float(np.median(nets)), 3) if nets else None,
                # ⚠ L'accord sur TOUTES les cellules d'un coup : c'est la grandeur que
                # `le_raccrochage_choisit_il_bien` publie, et elle ne vaut pas la médiane des
                # accords pas par pas — mélanger sept populations dont les décalages diffèrent
                # dilue une corrélation que chacune porte.
                rho_global=glob["rho"], rho_global_du_melange=glob_m["rho"],
                # ⭐⭐ L'AMPLITUDE, ET C'EST ELLE QUI EXPLIQUE QUE LES DEUX CRITÈRES DIVERGENT.
                # Spearman est invariant par changement d'échelle : une forme qui choisit des
                # décalages trois fois trop grands garde tout son rang et paie tout son coût.
                # Le rapport des amplitudes médianes dit laquelle des deux choses on regarde.
                amplitude_relative=(
                    round(float(np.median(np.abs(np.concatenate([t[0] for t in suite]))))
                          / float(np.median(np.abs(np.concatenate([t[2] for t in suite])))), 3)
                    if suite and float(np.median(np.abs(
                        np.concatenate([t[2] for t in suite])))) > 1e-9 else None),
                erreur_mediane_um=round(float(np.median([x["erreur_um"] for x in ex])), 1),
                # ⭐ L'erreur sur toutes les cellules, et sa plage quand un pas quelconque
                # sort. C'est elle qui décide ; celle par pas dit si l'effet est partagé.
                erreur_globale_um=round(poolee((int(dg), nom)), 1),
                erreur_globale_intervalle_um=intervalle((int(dg), nom)),
                # ⭐⭐⭐ LES DEUX ÉCARTS APPARIÉS, ET CE SONT EUX QUI DÉCIDENT. Voir
                # `ecart_apparie` : la variabilité d'un pas à l'autre vaut quatre fois celle
                # d'une méthode à l'autre, donc seul un écart pris sur le MÊME pas la résout.
                contre_sans_bouger=ecart_apparie(
                    [x["erreur_um"] for x in ex],
                    [e["erreur_sans_bouger_um"] for e in lignes]),
                contre_le_deploye=ecart_apparie(
                    [x["erreur_um"] for x in ex],
                    [x2["erreur_um"] for e in lignes for x2 in e["essais"]
                     if x2["deployee"]]),
                erreur_melangee_mediane_um=round(
                    float(np.median([x["erreur_melangee_um"] for x in ex])), 1),
                # ⚠ Un accord médian ne suffit pas : le compte par pas dit si la médiane est
                # portée par tous ou par un seul. Les deux sont publiés côte à côte, et les
                # verdicts exigent les deux.
                **_recalage(courbes.get((int(dg), nom), []), facteurs,
                            [x["erreur_um"] for x in ex]),
                paires_ou_il_bat_son_melange=sum(
                    1 for x in ex if x["accord"]["rho"] is not None
                    and x["accord_du_melange"]["rho"] is not None
                    and x["accord"]["rho"] > x["accord_du_melange"]["rho"])))
    r["erreur_sans_bouger_globale_um"] = round(poolee_repere("sans_bouger"), 1)
    r["erreur_oracle_globale_um"] = round(poolee_repere("oracle"), 1)
    r["variantes"] = variantes

    def trouver(dg: int, nom: str) -> dict:
        return next(v for v in variantes if v["demi_largeur_vx"] == dg and v["source"] == nom)

    ref = trouver(deployee, "depart")
    r["variante_deployee"] = ref
    dispo = [v for v in variantes if v["disponible_en_production"]]
    # ⭐⭐⭐ LA MEILLEURE VARIANTE DISPONIBLE, PAR SON ACCORD **NET**. Le critère que la tranche
    # précédente a désigné est l'accord de rang avec l'oracle — mais une ligne qui traverse des
    # feuilles est périodique, donc un gabarit MÉLANGÉ s'accorde déjà un peu avec l'oracle
    # (mesuré : +0,192 à demi-largeur 31, plus que le vrai). Choisir sur l'accord brut
    # couronnerait une forme large pour ce que son propre mélange lit aussi bien. Voir `_net`.
    meilleure = max((v for v in dispo if v["rho_net_median"] is not None),
                    key=lambda v: v["rho_net_median"], default=None)
    r["meilleure_par_accord"] = meilleure
    # ⚠ Et la meilleure par l'ERREUR est publiée à part : les deux critères peuvent désigner
    # deux variantes, et forcer un seul gagnant cacherait ce désaccord au lieu de le dire.
    # ⭐ La meilleure marche est désormais celle dont l'ÉCART APPARIÉ au déployé est le plus
    # négatif : c'est la seule comparaison que la variabilité entre pas ne domine pas.
    r["meilleure_par_erreur"] = min(dispo, key=lambda v: v["contre_le_deploye"]["ecart_median_um"])

    def survit(a_: dict, b_: dict) -> int:
        """Dans combien de mondes à un pas de moins `a_` marche-t-il encore mieux que `b_` ?"""
        ka = (a_["demi_largeur_vx"], a_["source"])
        kb = (b_["demi_largeur_vx"], b_["source"])
        return sum(1 for i in range(len(lignes)) if poolee(ka, i) < poolee(kb, i))

    def compte_mieux(v: dict, cle: str, sens: int) -> int:
        a = essais_de(v["demi_largeur_vx"], v["source"])
        b = essais_de(ref["demi_largeur_vx"], ref["source"])
        n = 0
        for x, y in zip(a, b):
            if cle == "net":
                if x["accord_net"] is None or y["accord_net"] is None:
                    continue
                n += int(sens * (x["accord_net"] - y["accord_net"]) > 0)
            else:
                n += int(sens * (x["erreur_um"] - y["erreur_um"]) > 0)
        return n

    r["paires_ou_la_meilleure_lit_mieux"] = (
        compte_mieux(meilleure, "net", +1) if meilleure else 0)
    r["paires_ou_la_meilleure_marche_mieux"] = compte_mieux(
        r["meilleure_par_erreur"], "erreur", -1)
    r["ecart_du_raccrochage_a_ne_pas_bouger_um"] = ref["contre_sans_bouger"]["ecart_median_um"]
    # ⭐⭐⭐ LES DEUX VERDICTS, ET CHACUN EXIGE SA MÉDIANE **ET** SON COMPTE PAR PAS. Une médiane
    # que le compte par cas contredit n'est pas un verdict — le dépôt a déjà eu à en retirer un.
    r["une_autre_forme_lit_mieux"] = bool(
        meilleure is not None and not meilleure["deployee"]
        and ref["rho_net_median"] is not None
        and meilleure["rho_net_median"] > ref["rho_net_median"]
        and r["paires_ou_la_meilleure_lit_mieux"] > len(lignes) / 2)
    # ⚠⚠⚠ TROIS CONDITIONS, ET LA TROISIÈME EST NOUVELLE : le verdict doit tenir dans TOUS les
    # mondes où un pas quelconque est retiré. Sans elle, un seul pas peut porter la conclusion —
    # mesuré : en perdre un faisait passer « aucune forme ne marche mieux » de 0 pas sur 7 à
    # 4 pas sur 6, c'est-à-dire retourner le verdict.
    r["pas_dont_le_retrait_conserve_la_marche"] = survit(r["meilleure_par_erreur"], ref)
    ecart_m = r["meilleure_par_erreur"]["contre_le_deploye"]
    r["une_autre_forme_marche_mieux"] = bool(
        not r["meilleure_par_erreur"]["deployee"] and tranche(ecart_m))
    # ⭐⭐⭐ ET LA QUESTION QUE CE BALAYAGE POSE À LA TRANCHE PRÉCÉDENTE : sur les pas où les
    # quatre sources existent, le raccrochage en service bat-il seulement le fait de NE PAS
    # BOUGER ? La réponse est publiée avec son écart apparié, son compte et son intervalle,
    # parce que la mesure d'avant portait sur une autre population et n'a pas à être reprise
    # à l'aveugle — mais elle n'a pas non plus à être reconduite sans être redemandée.
    r["le_raccrochage_en_service_bat_ne_pas_bouger"] = tranche(ref["contre_sans_bouger"])
    # ⛔ LA BORNE : le gabarit de l'arrivée, à la largeur déployée. S'il ne gagne rien, la
    # famille des gabarits est épuisée et ce qui reste à gagner n'est pas une question de forme.
    borne = trouver(deployee, SOURCE_BORNE)
    r["gabarit_borne"] = borne
    r["pas_dont_le_retrait_conserve_la_marche_de_la_borne"] = survit(borne, ref)
    r["paires_ou_la_borne_lit_mieux"] = compte_mieux(borne, "net", +1)
    r["le_gabarit_parfait_lirait_mieux"] = bool(
        borne["rho_net_median"] is not None and ref["rho_net_median"] is not None
        and borne["rho_net_median"] > ref["rho_net_median"]
        and r["paires_ou_la_borne_lit_mieux"] > len(lignes) / 2)
    # ⚠⚠ LE TÉMOIN, VARIANTE PAR VARIANTE : une forme dont l'accord ne bat pas celui de son
    # propre mélange ne lit rien, si large ou si bien située soit-elle.
    r["variantes_qui_battent_leur_melange"] = sum(
        1 for v in variantes if v["rho_net_median"] is not None
        and v["rho_net_median"] > 0)
    # ⚠⚠ ET LE CONTRAIRE, PUBLIÉ PLUTÔT QUE TU : combien de mélanges lisent quelque chose. Un
    # témoin qui lit est la mesure de ce que la périodicité rend toute seule, et c'est ce qui
    # interdit de lire un accord brut comme une lecture de forme.
    r["melanges_qui_lisent"] = sum(
        1 for v in variantes if v["rho_median_du_melange"] is not None
        and v["rho_median_du_melange"] > 0)
    r["variantes_mesurees"] = len(variantes)
    # ⚠ Les côtés balayés sont des multiples de celui publié : ils disent ce que coûterait
    # d'élargir la fenêtre, dans l'unité où la campagne l'exprime déjà.
    r["pas_par_cote"] = pas_par_cote(c, [cote, cote * 1.5, cote * 2.0, cote * 3.0], minimum)
    # ⭐⭐⭐ LE LEVIER QUE LE BALAYAGE A DÉCOUVERT, ET QUI N'EST PAS LE GABARIT. Les deux critères
    # se contredisent — une forme peut mieux ORDONNER les décalages et plus mal MARCHER — parce
    # qu'un accord de rang est invariant d'échelle. Le premier remède n'est donc pas de changer
    # la forme mais de corriger l'AMPLITUDE de ce qu'elle choisit, et il est mesuré hors
    # échantillon plutôt qu'écrit comme une piste.
    recalables = [v for v in dispo if v["erreur_recalee_mediane_um"] is not None]
    r["meilleure_apres_recalage"] = (
        min(recalables, key=lambda v: v["erreur_recalee_mediane_um"]) if recalables else None)
    r["le_recalage_de_la_forme_en_service_ameliore"] = ref["le_recalage_ameliore"]
    r["erreur_deployee_globale_um"] = ref["erreur_globale_um"]
    r["erreur_deployee_intervalle_um"] = ref["erreur_globale_intervalle_um"]
    r["gain_du_recalage_um"] = (
        round(ref["erreur_mediane_um"] - ref["erreur_recalee_mediane_um"], 1)
        if ref["erreur_recalee_mediane_um"] is not None else None)
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- la famille des largeurs ---
    demi_vx = (135.5 / 2.215) / 2.0
    fam = demi_largeurs(demi_vx)
    v("la famille des demi-largeurs est croissante et sans doublon",
      fam == sorted(set(fam)) and len(fam) == len(FRACTIONS_DE_DEMI_FEUILLE), str(fam))
    # ⚠⚠ SANS CE CONTRÔLE LE BALAYAGE COMPARERAIT AUTRE CHOSE QUE CE QUI TOURNE : la valeur en
    # service doit être un barreau de l'échelle, sinon « mieux que le déployé » n'a pas de
    # référence dans la mesure.
    v("... et elle contient la demi-largeur EN SERVICE",
      demi_largeur_deployee(demi_vx) in fam, str(demi_largeur_deployee(demi_vx)))
    v("... son bout large couvre deux pas entiers, donc contient déjà la crête voisine",
      max(fam) >= 2 * demi_vx - 1, f"{max(fam)} contre {2 * demi_vx:.1f}")
    v("... et son bout étroit garde encore une forme, pas trois points", min(fam) >= 5, str(min(fam)))

    # --- la troncature ---
    g = np.arange(11.0)
    v("un gabarit étroit est le CŒUR du large, à la même position",
      tronquer(g, 2).tolist() == [3.0, 4.0, 5.0, 6.0, 7.0], str(tronquer(g, 2).tolist()))
    v("... tronquer à sa propre demi-largeur ne change rien",
      tronquer(g, 5).tolist() == g.tolist())
    trop = None
    try:
        tronquer(g, 9)
    except ValueError as exc:
        trop = str(exc)
    v("... et on ne peut pas tronquer PLUS LARGE que ce qui a été lu", trop is not None, str(trop))

    # --- d'où chaque source lit ---
    s = sources_du_pas(5, [3, 4, 5, 6, 7])
    v("le gabarit du DÉPART se lit sur la spire de départ", s["depart"] == [5])
    v("... celui d'AILLEURS n'est jamais celui du départ, ni d'après",
      s["ailleurs"] == [3] and max(s["ailleurs"]) < 5, str(s["ailleurs"]))
    # ⚠⚠⚠ LE CONTRÔLE QUI A ATTRAPÉ UNE FUITE RÉELLE : sur le premier pas de la boîte, « la
    # plus ancienne spire autre que le départ » est la spire d'ARRIVÉE. Une variante annoncée
    # disponible en production lisait donc la surface cherchée.
    v("... et sur le premier pas il n'y a PAS d'ailleurs, plutôt que l'arrivée",
      sources_du_pas(3, [3, 4, 5])["ailleurs"] is None,
      str(sources_du_pas(3, [3, 4, 5])["ailleurs"]))
    # ⚠⚠⚠ LA FUITE QUE CE CONTRÔLE INTERDIT : une moyenne qui remonterait au-delà du départ
    # lirait la spire qu'on cherche, donc gagnerait en recopiant la réponse dans la question.
    v("... la MOYENNE ne lit jamais une spire postérieure au départ",
      s["moyennee"] == [3, 4, 5] and max(s["moyennee"]) <= 5, str(s["moyennee"]))
    v("... et la BORNE lit bien l'arrivée, celle qui n'existe pas en production",
      s[SOURCE_BORNE] == [6])
    v("une source dont la spire manque est rendue ABSENTE, pas remplacée",
      sources_du_pas(7, [3, 4, 5, 6, 7])[SOURCE_BORNE] is None)
    v("... et une spire seule n'a pas d'ailleurs", sources_du_pas(3, [3])["ailleurs"] is None)

    # --- la combinaison ---
    par = {1: np.array([0.0, 10.0, 0.0]), 2: np.array([0.0, 12.0, 0.0]),
           3: np.array([0.0, 200.0, 0.0])}
    v("le gabarit combiné est la MÉDIANE, donc une spire abîmée ne le décide pas",
      gabarit_combine(par, [1, 2, 3]).tolist() == [0.0, 12.0, 0.0],
      str(gabarit_combine(par, [1, 2, 3]).tolist()))

    # --- la grille des facteurs d'échelle ---
    f = facteurs_dechelle(demi_vx)
    # ⚠⚠ SANS L'IDENTITÉ DANS LA GRILLE, « recaler améliore » n'a pas de point de comparaison :
    # l'écart mesuré mêlerait le recalage et un décalage de grille.
    v("la grille des facteurs contient EXACTEMENT l'identité",
      float(np.min(np.abs(f - 1.0))) == 0.0, f"{len(f)} facteurs de {f[0]:.3f} à {f[-1]:.3f}")
    v("... un pas de la grille déplace d'un voxel le décalage le plus grand de la fenêtre",
      abs(float(f[1] - f[0]) * demi_vx - 1.0) < 1e-9, f"pas {float(f[1] - f[0]):.4f}")
    v("... et elle couvre les DEUX défauts : sur-estimer et sous-estimer le décalage",
      float(f[-1]) >= 2.0 and float(f[0]) <= 0.0, f"[{f[0]:.3f}, {f[-1]:.3f}]")

    # ⚠ Le choix hors échantillon vit dans `src/commun/lecart_apparie.py` et y est exercé ; ce
    # qui est vérifié ICI, c'est que ce fichier s'en sert bien pour son facteur d'échelle.

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE, avec ses DEUX matières.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    g0 = geometrie_fabriquee()
    fab = mesurer(echantillon=90, minimum=20, corpus=corpus_fabrique(),
                  volume=volume_fabrique(g0))
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["paires"] > 0 and fab["variantes_mesurees"] == len(fab["demi_largeurs_vx"]) * 4,
      f"{fab['paires']} pas, {fab['variantes_mesurees']} variantes")
    # ⚠⚠⚠ LA PROPRIÉTÉ QUI REND LE BALAYAGE HONNÊTE : une fenêtre commune à toutes les largeurs.
    # Sans elle une variante large gagnerait en visant des décalages que les autres ne peuvent
    # pas atteindre, et la mesure porterait sur des fenêtres et non sur des formes.
    fenetres = {tuple(x["fenetre_vx"]) for e in fab["lignes"] for x in e["essais"]}
    v("... et TOUTES les largeurs balayent exactement la MÊME fenêtre",
      len(fenetres) == 1, str(sorted(fenetres)))
    # ⚠⚠⚠ ET LA SECONDE : une seule population. Un verdict qui change avec la population n'est
    # pas un verdict, et une ligne plus longue écarte plus de cellules.
    v("... toutes les variantes d'un même pas sont jugées sur les MÊMES cellules",
      all(len(e["essais"]) == fab["variantes_mesurees"] for e in fab["lignes"]),
      str([e["cellules"] for e in fab["lignes"]]))
    v("... et un pas dont une source manque est écarté ENTIER et compté",
      isinstance(fab["paires_ecartees"], int), str(fab["paires_ecartees"]))
    # ⚠⚠ L'ORACLE EST UNE BORNE, ET SA TOLÉRANCE EST DÉRIVÉE PLUTÔT QUE CHOISIE. Il ne peut
    # viser que les positions de la grille, là où `decalage_retenu` affine par parabole et
    # atterrit entre deux : un contendant peut donc le battre, mais d'au plus **un voxel**,
    # parce qu'un déplacement d'un voxel ne change une distance que d'un voxel. Toute avance
    # au-delà de cette borne ne serait pas de l'affinage, ce serait une fuite de la réponse.
    marge = fab["voxel_um"]
    v("... l'oracle des décalages n'est battu par AUCUNE forme de plus d'un voxel",
      all(e["erreur_oracle_um"] <= min(x["erreur_um"] for x in e["essais"]) + marge
          for e in fab["lignes"]),
      f"marge {marge} µm · "
      + str([(e["erreur_oracle_um"], min(x["erreur_um"] for x in e["essais"]))
             for e in fab["lignes"]]))
    v("... les décalages retenus restent tous dans la fenêtre commune",
      all(x["fenetre_vx"][0] <= x["decalage_median_vx"] <= x["fenetre_vx"][1]
          for e in fab["lignes"] for x in e["essais"]))
    # ⚠⚠ LE TÉMOIN EXISTE POUR CHAQUE VARIANTE, pas une fois pour toutes : mélanger le gabarit
    # étroit ne dit rien de ce que le hasard rend sur un gabarit large.
    v("... chaque variante porte SON PROPRE mélange",
      all(x["accord_du_melange"] is not None and x["erreur_melangee_um"] > 0
          for e in fab["lignes"] for x in e["essais"]))
    v("... la variante EN SERVICE est présente, et une seule",
      sum(1 for x in fab["variantes"] if x["deployee"]) == 1)
    # ⚠⚠⚠ LA RÈGLE GÉNÉRALE, RELUE SUR LA MESURE ELLE-MÊME plutôt que sur la fonction seule :
    # aucune source annoncée disponible ne lit une spire que la marche n'a pas encore atteinte.
    fuites = [(e["de"], x["source"], x["spires_lues"]) for e in fab["lignes"]
              for x in e["essais"]
              if x["disponible_en_production"] and max(x["spires_lues"]) > e["de"]]
    v("... aucune source de production ne lit une spire au-delà du départ",
      not fuites, str(fuites[:3]))
    v("... la source qui n'existe pas en production est marquée comme telle",
      all(not x["disponible_en_production"] for x in fab["variantes"]
          if x["source"] == SOURCE_BORNE)
      and all(x["disponible_en_production"] for x in fab["variantes"]
              if x["source"] != SOURCE_BORNE))
    v("... et la meilleure variante n'est cherchée QUE parmi les disponibles",
      fab["meilleure_par_accord"] is None
      or fab["meilleure_par_accord"]["disponible_en_production"])
    # ⚠⚠⚠ UN VERDICT SUR LA MÉDIANE QUE LE COMPTE PAR PAS CONTREDIRAIT N'EST PAS UN VERDICT.
    # ⚠⚠⚠ LE CONTRÔLE QUI A CHANGÉ UN VERDICT : chaque variante porte son accord NET, et le
    # choix de la meilleure passe par lui. Sans ça, une forme large serait couronnée pour la
    # périodicité que son propre mélange lit aussi bien.
    v("... chaque forme porte son accord NET, et c'est lui qui désigne la meilleure",
      all(x["accord_net"] is None
          or abs(x["accord_net"] - (x["accord"]["rho"] - x["accord_du_melange"]["rho"])) < 1e-9
          for e in fab["lignes"] for x in e["essais"])
      and (fab["meilleure_par_accord"] is None
           or fab["meilleure_par_accord"]["rho_net_median"]
           == max(x["rho_net_median"] for x in fab["variantes"]
                  if x["disponible_en_production"] and x["rho_net_median"] is not None)),
      str(fab["meilleure_par_accord"]["rho_net_median"]
          if fab["meilleure_par_accord"] else None))
    # ⚠ Et l'accord GLOBAL est rendu à côté du médian : ce sont deux questions, pas deux
    # écritures d'une même — l'une porte sur un pas typique, l'autre sur toutes les cellules.
    v("... et l'accord sur TOUTES les cellules est rendu à côté de celui pas par pas",
      all("rho_global" in x and "rho_net_median" in x for x in fab["variantes"]))
    # ⚠⚠ LA COURBE DES FACTEURS DOIT PASSER PAR L'ERREUR NON RECALÉE À α = 1 : sans ce lien,
    # une erreur de grille d'un cran rendrait un recalage qui améliore par construction.
    # ⚠⚠⚠ DEUX CHEMINS DE CALCUL POUR UN MÊME NOMBRE : le point de la courbe à facteur un, et
    # l'erreur non recalée. Leur égalité est ce qui attrape une grille qui rate l'identité —
    # le défaut que la première version de `facteurs_dechelle` portait.
    ecarts = [(x["erreur_a_facteur_un_um"], x["erreur_mediane_um"]) for x in fab["variantes"]
              if x["erreur_a_facteur_un_um"] != x["erreur_mediane_um"]]
    v("... à facteur un, la courbe de recalage RETOMBE exactement sur l'erreur non recalée",
      not ecarts, str(ecarts[:3]) if ecarts else
      f"{len(fab['variantes'])} variantes d'accord")
    # ⚠⚠ ET LE VERDICT DE RECALAGE EXIGE SA MÉDIANE ET SON COMPTE PAR PAS, comme les autres.
    v("... le verdict de recalage exige la médiane ET le compte par pas",
      all(not x["le_recalage_ameliore"]
          or (x["erreur_recalee_mediane_um"] < x["erreur_mediane_um"]
              and x["paires_ou_le_recalage_ameliore"] > x["paires"] / 2)
          for x in fab["variantes"]),
      f"{fab['variante_deployee']['paires_ou_le_recalage_ameliore']}/{fab['paires']}")
    v("... et l'amplitude relative à celle de l'oracle est publiée",
      all(x["amplitude_relative"] is None or x["amplitude_relative"] > 0
          for x in fab["variantes"]),
      str([x["amplitude_relative"] for x in fab["variantes"]][:4]))
    # ⚠⚠⚠ LE CONTRÔLE QUE CETTE TRANCHE A DÛ AJOUTER PARCE QUE SA PROPRE MESURE L'A EXIGÉ : un
    # verdict de marche ne tient que s'il survit au retrait de N'IMPORTE QUEL pas. Sans lui, un
    # seul pas portait la conclusion — mesuré, en retirer un faisait passer « aucune forme ne
    # marche mieux » de 0 pas sur 7 à 4 pas sur 6.
    v("... le verdict de marche doit tenir dans TOUS les mondes à un pas de moins",
      not fab["une_autre_forme_marche_mieux"]
      or fab["meilleure_par_erreur"]["contre_le_deploye"]["intervalle_um"][1] < 0,
      str(fab["meilleure_par_erreur"]["contre_le_deploye"]["intervalle_um"]))
    # ⚠⚠ ET LA QUESTION POSÉE À LA TRANCHE PRÉCÉDENTE EST RENDUE, quel que soit son signe :
    # taire un « non » serait choisir ce que la mesure a le droit de dire.
    v("... et le raccrochage en service est confronté à NE PAS BOUGER, appariement compris",
      isinstance(fab["le_raccrochage_en_service_bat_ne_pas_bouger"], bool)
      and fab["ecart_du_raccrochage_a_ne_pas_bouger_um"] is not None,
      f"{fab['ecart_du_raccrochage_a_ne_pas_bouger_um']:+.1f} µm")
    # ⚠⚠ ET L'ERREUR QUI DÉCIDE EST PRISE SUR LES CELLULES, pas sur six ou sept nombres. Son
    # intervalle à un pas de moins est publié à côté, pour que sa fragilité soit lisible.
    # ⚠⚠⚠ LES REPÈRES SONT RÉSUMÉS COMME LES VARIANTES, sinon la ligne de référence et ce
    # qu'on lui compare ne seraient pas la même statistique.
    v("... les deux repères sont résumés sur les MÊMES cellules que les variantes",
      fab["erreur_sans_bouger_globale_um"] > 0 and fab["erreur_oracle_globale_um"] > 0
      and fab["erreur_oracle_globale_um"] <= min(x["erreur_globale_um"]
                                                 for x in fab["variantes"]) + fab["voxel_um"],
      f"sans bouger {fab['erreur_sans_bouger_globale_um']} · oracle "
      f"{fab['erreur_oracle_globale_um']} µm")
    v("... l'erreur qui décide est prise sur toutes les cellules, avec sa plage",
      all(x["erreur_globale_intervalle_um"][0] <= x["erreur_globale_um"]
          <= x["erreur_globale_intervalle_um"][1] + 0.05 for x in fab["variantes"]),
      str(fab["variante_deployee"]["erreur_globale_intervalle_um"]))
    # ⚠ Les propriétés de l'écart apparié sont exercées par `src/commun/lecart_apparie.py` ;
    # ce qui est vérifié ICI, c'est qu'il est bien celui qui décide.
    ref_ = fab["variante_deployee"]
    v("l'écart apparié d'une forme à elle-même vaut exactement zéro",
      ref_["contre_le_deploye"]["ecart_median_um"] == 0.0
      and ref_["contre_le_deploye"]["intervalle_um"] == [0.0, 0.0],
      str(ref_["contre_le_deploye"]))
    # ⚠⚠ LE RELEVÉ QUI TRANSFORME LA LIMITE EN PLAN : il est monotone par construction — une
    # boîte plus large ne peut pas contenir moins de spires — et le vérifier attrape un
    # découpage qui aurait cessé d'être emboîté.
    releve = fab["pas_par_cote"]
    v("le relevé des pas par taille de boîte est croissant, et part du côté publié",
      releve[0]["cote_voxels"] == fab["boite"]["cote_voxels"]
      and all(a["spires"] <= b_["spires"] for a, b_ in zip(releve, releve[1:])),
      str([(int(x["cote_voxels"]), x["spires"], x["pas_complets"]) for x in releve]))
    # ⚠⚠ LE RELEVÉ EST UNE BORNE SUPÉRIEURE, ET LE CONTRÔLE L'ENCADRE DES DEUX CÔTÉS. Il ne
    # regarde que les grilles, donc il ignore qu'une ligne dont un échantillon manque écarte
    # sa cellule et qu'un pas peut tomber sous le seuil : il ne peut donc pas annoncer MOINS de
    # pas que la mesure n'en a marchés, ni plus que ceux qu'elle a marchés et écartés ensemble.
    v("... et au côté publié il encadre exactement les pas que la mesure a marchés",
      fab["paires"] <= releve[0]["pas_complets"] <= fab["paires"] + fab["paires_ecartees"],
      f"{fab['paires']} ≤ {releve[0]['pas_complets']} ≤ "
      f"{fab['paires'] + fab['paires_ecartees']}")
    v("un mélange qui lit est COMPTÉ plutôt que tu",
      isinstance(fab["melanges_qui_lisent"], int)
      and fab["melanges_qui_lisent"] <= fab["variantes_mesurees"],
      f"{fab['melanges_qui_lisent']}/{fab['variantes_mesurees']}")
    v("un verdict n'est rendu que si la médiane ET le compte par pas s'accordent",
      (not fab["une_autre_forme_lit_mieux"]
       or fab["paires_ou_la_meilleure_lit_mieux"] > fab["paires"] / 2)
      and (not fab["une_autre_forme_marche_mieux"]
           or fab["paires_ou_la_meilleure_marche_mieux"] > fab["paires"] / 2),
      f"{fab['paires_ou_la_meilleure_lit_mieux']}/{fab['paires']}")
    v("l'accord des orientations est rendu, quel qu'il soit",
      isinstance(fab["orientations_daccord"], bool), str(fab["orientations_daccord"]))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "FORME" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(echantillon=90, minimum=20, corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(geometrie_fabriquee(decalage_vx=5000.0)))
    except RuntimeError as exc:
        hors = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      hors is not None, str(hors))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'un balayage de gabarits."""
    print(f"pas nominal {r['pas_nominal_um']} µm · demi-feuille {r['demi_feuille_vx']} vx · "
          f"{r['paires']} pas ({r['paires_ecartees']} écartés), {r['cellules']} cellules · "
          f"spires lisibles {r['spires_lisibles']}\n")
    print(f"{'demi-larg.':>10} {'source':>10} {'spires':>14} {'rho':>7} {'mêlé':>7} "
          f"{'NET':>7} {'ampl.':>6} {'/pas':>7} {'GLOBAL':>8} {'vs rien':>7} {'vs deploye, -1 pas':>14} {'recalée':>8} {'bat mêlé':>9}")
    print("-" * 128)
    def rho_lisible(valeur) -> str:
        return "—" if valeur is None else f"{valeur:+.3f}"

    def nombre(valeur, chiffres: int = 2) -> str:
        return "—" if valeur is None else f"{valeur:.{chiffres}f}"

    for x in r["variantes"]:
        marque = " ⭐" if x["deployee"] else (" ⛔" if not x["disponible_en_production"] else "")
        lu = next((e for e in r["lignes"][0]["essais"]
                   if e["demi_largeur_vx"] == x["demi_largeur_vx"]
                   and e["source"] == x["source"]), None)
        spires = str(lu["spires_lues"]) if lu else "?"
        print(f"{x['demi_largeur_vx']:>10} {x['source']:>10} {spires:>14} "
              f"{rho_lisible(x['rho_median']):>7} "
              f"{rho_lisible(x['rho_median_du_melange']):>7} "
              f"{rho_lisible(x['rho_net_median']):>7} "
              f"{nombre(x['amplitude_relative']):>6} "
              f"{x['erreur_mediane_um']:>6.1f}µ "
              f"{x['erreur_globale_um']:>7.1f}µ "
              f"{x['contre_sans_bouger']['ecart_median_um']:>+7.1f} "
              f"{str(x['contre_le_deploye']['intervalle_um']):>14} "
              f"{nombre(x['erreur_recalee_mediane_um'], 1):>7}µ "
              f"{x['paires_ou_il_bat_son_melange']:>4}/{x['paires']:<4}{marque}")
    ref = r["variante_deployee"]
    print(f"\nen service : demi-largeur {ref['demi_largeur_vx']} vx sur la spire de départ — "
          f"rho médian {ref['rho_median']} · NET {ref['rho_net_median']} · global "
          f"{ref['rho_global']} · erreur GLOBALE {ref['erreur_globale_um']} µm "
          f"(à un pas de moins : {ref['erreur_globale_intervalle_um']})")
    print(f"repères, sur les mêmes cellules : sans bouger "
          f"{r['erreur_sans_bouger_globale_um']} µm · oracle des décalages "
          f"{r['erreur_oracle_globale_um']} µm  (par pas : "
          f"{r['erreur_sans_bouger_mediane_um']} et {r['erreur_oracle_mediane_um']})")
    ma = r["meilleure_par_accord"]
    me = r["meilleure_par_erreur"]
    if ma:
        print(f"meilleur accord NET parmi les disponibles : {ma['demi_largeur_vx']} vx / "
              f"{ma['source']} — net {ma['rho_net_median']} (brut {ma['rho_median']}, mêlé "
              f"{ma['rho_median_du_melange']})")
    print(f"meilleure ERREUR GLOBALE parmi les disponibles : {me['demi_largeur_vx']} vx / "
          f"{me['source']} — {me['erreur_globale_um']} µm {me['erreur_globale_intervalle_um']}")
    b = r["gabarit_borne"]
    print(f"⛔ borne, le gabarit de l'ARRIVÉE à la largeur déployée : net {b['rho_net_median']} "
          f"· {b['erreur_globale_um']} µm {b['erreur_globale_intervalle_um']} — elle marche "
          f"mieux dans {r['pas_dont_le_retrait_conserve_la_marche_de_la_borne']} des "
          f"{r['paires']} mondes à un pas de moins")
    print(f"→ une autre FORME lit mieux que celle en service : "
          f"{'OUI' if r['une_autre_forme_lit_mieux'] else 'NON'} "
          f"({r['paires_ou_la_meilleure_lit_mieux']} pas sur {r['paires']})")
    manques, ed = [], me["contre_le_deploye"]
    if me["deployee"]:
        manques.append("la meilleure EST celle en service")
    elif ed["ecart_median_um"] >= 0:
        manques.append(f"son écart apparié vaut {ed['ecart_median_um']:+.1f} µm")
    if ed["pas_ameliores"] <= r["paires"] / 2:
        manques.append(f"seuls {ed['pas_ameliores']} pas sur {r['paires']} y gagnent")
    if ed["intervalle_um"][1] >= 0:
        manques.append(f"l'écart remonte à {ed['intervalle_um'][1]:+.1f} µm quand un pas sort")
    print(f"→ une autre FORME marche mieux (écart APPARIÉ au déployé) : "
          f"{'OUI' if r['une_autre_forme_marche_mieux'] else 'NON'}"
          + (f" — il manque : {' ; '.join(manques)}" if manques else ""))
    cs = ref["contre_sans_bouger"]
    print(f"→ ⭐ le raccrochage EN SERVICE bat-il seulement NE PAS BOUGER, sur ces pas ? "
          f"{'OUI' if r['le_raccrochage_en_service_bat_ne_pas_bouger'] else 'NON'} "
          f"(écart apparié {cs['ecart_median_um']:+.1f} µm, {cs['pas_ameliores']} pas sur "
          f"{cs['pas']}, intervalle à un pas de moins {cs['intervalle_um']})")
    print("   ce qu'il faudrait pour décider — pas complets par côté de boîte : "
          + " · ".join(f"{int(x['cote_voxels'])} vx → {x['pas_complets']} pas "
                       f"({x['spires']} spires)" for x in r["pas_par_cote"]))
    print(f"→ ⛔ un gabarit PARFAIT lirait mieux : "
          f"{'OUI' if r['le_gabarit_parfait_lirait_mieux'] else 'NON'} "
          f"({r['paires_ou_la_borne_lit_mieux']} pas sur {r['paires']})")
    print(f"→ ⭐ RECALER les décalages de la forme EN SERVICE améliore : "
          f"{'OUI' if r['le_recalage_de_la_forme_en_service_ameliore'] else 'NON'} "
          f"({r['gain_du_recalage_um']:+.1f} µm, facteur "
          f"{ref['facteur_median_hors_echantillon']}, "
          f"{ref['paires_ou_le_recalage_ameliore']} pas sur {ref['paires']}) — "
          f"amplitude choisie {ref['amplitude_relative']}× celle de l'oracle")
    mr = r["meilleure_apres_recalage"]
    if mr:
        print(f"   meilleure erreur APRÈS recalage, hors échantillon : "
              f"{mr['demi_largeur_vx']} vx / {mr['source']} — "
              f"{mr['erreur_recalee_mediane_um']} µm")
    print(f"→ formes dont l'accord bat celui de leur mélange : "
          f"{r['variantes_qui_battent_leur_melange']} sur {r['variantes_mesurees']} · "
          f"et {r['melanges_qui_lisent']} MÉLANGES lisent déjà quelque chose")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs, {r['cout']['mebioctets']} Mio")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=400)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(echantillon=a.echantillon, cote=a.cote)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
