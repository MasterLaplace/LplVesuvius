"""La profondeur tourne-t-elle, ou bascule-t-elle ? — le juge, et le domaine où il répond.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `176` mesure qu'il y a de l'ordre en profondeur sur le vrai rouleau —
vingt et un chunks sur vingt-deux dépassent TOUTES leurs permutations quand le hasard en donnerait
1,1 — et que cet ordre n'est PAS une bascule recto/verso : la bascule médiane vaut 6,862° là où la
même recette rend 90,0° sur une matière dont la bascule est construite. Ce que cet ordre EST restait
ouvert, et `174` dit pourquoi : une DÉRIVE n'est pas séparée d'une MARCHE par un verdict. Le témoin
vaut 0,0° sur une marche et 43,287° sur une dérive, mais il reste un nombre à lire. Sur le rouleau
la bascule vaut 6,862° pour un témoin de 5,54° : deux nombres du même ordre, et rien ne tranche.

⭐⭐⭐⭐ LE TROISIÈME ÉNONCÉ EST UN SECOND AJUSTEMENT, LU PAR LE MÊME ESTIMATEUR. Une marche a une
orientation constante de part et d'autre d'un point : c'est l'ajustement en DEUX SEGMENTS de `174`.
Une dérive tourne régulièrement : c'est un ajustement AFFINE, une rotation par couche. Les deux
rendent la même quantité — la résultante atteinte divisée par la somme des cohérences — donc leurs
valeurs se comparent sans qu'aucun seuil n'entre.

⚠⚠⚠ MAIS LEURS LIBERTÉS NE SONT PAS LES MÊMES, ET UNE PART BRUTE SERAIT DONC TRUQUÉE. Les deux
ajustements sont des EXTENSIONS d'un même nul, l'ajustement CONSTANT, et aucun des deux ne peut
faire moins que lui : couper ne perd jamais (l'inégalité triangulaire donne
`|Σa| + |Σb| ≥ |Σa + Σb|`) et l'affine contient la pente nulle. Comparer deux maximums pris sur deux
libertés différentes ne dirait donc que laquelle des deux est la plus large.

⭐⭐⭐⭐ C'EST LA PERMUTATION QUI PAIE LA LIBERTÉ, ET ELLE LE FAIT EXACTEMENT. Mélanger les couches
conserve chaque angle et chaque cohérence, donc conserve la liberté de chaque ajustement, et ne
détruit que l'ordre en profondeur. Et l'ajustement CONSTANT est exactement invariant par
permutation : une somme de vecteurs ne dépend pas de l'ordre des termes. Ce que l'EXCÉDENT — la part
réelle moins la part médiane des mélanges — mesure est donc la seule part de l'ajustement qui vient
de la profondeur, sa liberté déjà déduite. Le vainqueur est celui dont l'excédent est le plus grand,
et personne ne gagne si aucun ne dépasse tous ses mélanges.

⚠⚠⚠ ET LA FENÊTRE EST CHOISIE PAR LE NUL, PAS PAR UN CANDIDAT. Une première version laissait chaque
ajustement prendre sa meilleure fenêtre : la batterie a jugé « dérive » une marche construite, parce
que les deux retenaient une fenêtre HOMOGÈNE où tous deux atteignent un. C'est le défaut que `175` a
mesuré — une fenêtre sans frontière rend une part de un — réapparu un étage plus haut.

⚠⚠ LE PLANCHER `1/√n` NE PROTÈGE PAS L'AFFINE, ET C'EST DIT PLUTÔT QUE MASQUÉ. Il est appliqué aux
deux pour que l'estimateur soit le même, mais il vaut pour UNE direction, pas pour un maximum pris
sur autant de pentes qu'il y a de couches. Ce qui price cette maximisation est la permutation, qui
la subit à l'identique.

⭐⭐⭐⭐ ET LE RÉSULTAT DE CETTE TRANCHE EST UN DOMAINE, PAS UN VERDICT SUR LE ROULEAU. Le juge est
mesuré sur une échelle de tours dérivée — le quart de tour, ses moitiés, puis la bascule que `176` a
publiée — croisée avec des dispersions par couche dérivées du témoin du même verdict. Les deux
formes portent le MÊME tour total et ne diffèrent que par sa répartition, donc ce qui est mesuré est
la forme et non l'amplitude.

⚠⚠⚠ CETTE TRANCHE NE TOUCHE PAS LE VRAI ROULEAU, ET C'EST LE PRÉCÉDENT DE `174` : on ne pointe pas
sur la matière un instrument dont le contrôle vient de dire qu'il ne répond pas là. Un verdict rendu
hors du domaine mesuré n'est pas un verdict faible, c'est un nombre sans garantie sous un nom qui en
promet une.

⚠ ET CE QUE LE JUGE NE SÉPARE PAS, MÊME DANS SON DOMAINE : une rotation lente de la MATIÈRE et une
rotation lente de l'INSTRUMENT le long de la spire rendent la même courbe.

Usage :
    uv run python src/nappe/la_profondeur_tourne_t_elle_ou_bascule_t_elle.py --verifier
    uv run python src/nappe/la_profondeur_tourne_t_elle_ou_bascule_t_elle.py \\
        --json docs/mesures/la_profondeur_tourne_t_elle_ou_bascule_t_elle.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_coupe_cherchee_trouve_t_elle_la_frontiere import (  # noqa: E402
    COUCHES_DE_LA_CAMPAGNE, COUCHES_MINIMALES, FRONTIERE, PLANCHER_DE_COHERENCE,
    du_bruit,
    la_coupe_par_ajustement, la_direction_dune_tranche, une_derive, une_marche)
from la_recette_posee_sur_le_rouleau import les_fenetres  # noqa: E402
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LE_ROULEAU_A_RENDU = MESURES / "la_recette_posee_sur_le_rouleau.json"
LE_QUART_DE_TOUR = 90.0
GRAINES_PAR_CELLULE = 20
PERMUTATIONS = 19
GRAINE = 20260918
# ⭐⭐⭐⭐ LA DERIVE CONSTRUITE TOURNE D'UN QUART DE TOUR, EXACTEMENT COMME LA MARCHE CONSTRUITE DE
# `174`. Les deux matieres portent alors le MEME tour total et ne different que par sa FORME : d'un
# coup ou reparti. Une derive d'une autre etendue ferait du verdict une question d'amplitude, alors
# que l'amplitude est precisement ce que `176` a deja mesure.
# ⚠ Et ce quart de tour tombe au MILIEU d'un bin du balayage — 0,5 bin sur la campagne — donc la
# sonde qui verifie que l'affinage affine quelque chose peut echouer. La verification l'exige.
ETENDUE_DE_LA_DERIVE_DEG = 90.0


def _fort(courbe, plancher: float, minimum: int):
    """Les couches TEXTURÉES d'une courbe : leur indice, leur angle doublé, leur cohérence."""
    ang = np.asarray([x[0] for x in courbe], dtype=float)
    w = np.asarray([x[1] for x in courbe], dtype=float)
    fort = w > float(plancher)
    n = int(fort.sum())
    if n < int(minimum):
        return None
    return (np.arange(len(courbe), dtype=float)[fort], np.radians(2.0 * ang[fort]), w[fort])


def lajustement_constant(courbe, plancher: float = PLANCHER_DE_COHERENCE,
                         minimum: int = COUCHES_MINIMALES) -> dict | None:
    """Une seule direction pour toute la fenêtre — le NUL dont les deux autres sont des extensions.

    ⭐⭐⭐⭐ IL EST EXACTEMENT INVARIANT PAR PERMUTATION, et c'est ce qui rend l'excédent honnête :
    une somme de vecteurs ne dépend pas de l'ordre des termes. Tout ce qu'un ajustement gagne sur
    ses mélanges vient donc de la profondeur, et rien de sa liberté.

    ⚠ C'est `la_direction_dune_tranche` de `174` sur la fenêtre entière, sans un octet de plus :
    une seconde définition de « la direction d'une tranche » serait libre d'en diverger.
    """
    lu = la_direction_dune_tranche(courbe, 0, len(courbe), plancher, minimum)
    if lu is None:
        return None
    return {"quoi": "constant", "couches": int(lu["couches"]),
            "part_atteinte": round(float(lu["resultante"]), 3),
            "angle_deg": round(float(lu["angle_deg"]), 3)}


def lajustement_affine(courbe, plancher: float = PLANCHER_DE_COHERENCE,
                       minimum: int = COUCHES_MINIMALES) -> dict | None:
    """Une ROTATION PAR COUCHE : l'ajustement qu'une dérive atteint et qu'une marche n'atteint pas.

    ⭐⭐⭐⭐ LA PENTE EST UNE FRÉQUENCE, DONC SA RÉSOLUTION SE DÉRIVE. En angle doublé le modèle
    s'écrit `φ(k) = φ₀ + β·k`, et dé-tourner par `β` puis sommer est exactement une transformée
    évaluée en `β`. Deux pentes qui diffèrent de moins d'un tour réparti sur la fenêtre ne sont pas
    distinguables : ce sont les `m` bins `2π·j/m`. On les balaye tous, puis on affine autour du
    meilleur par une recherche ternaire jusqu'à ce que l'encadrement passe SOUS la précision que ce
    module publie — une tolérance dérivée de ce qui est écrit, pas choisie.

    ⚠⚠ LA PLAGE EST ALIASÉE ET ELLE N'EST PAS RESTREINTE. Sur des indices entiers, `β` et `β + 2π`
    rendent la même suite, donc la pente vit dans un demi-tour par couche en angle simple. Une pente
    rapide n'est plus une rotation lente mais une alternation, et la restreindre serait un seuil
    choisi : la pente est RENDUE, avec le nombre de couches qu'un demi-tour lui coûte, pour qu'un
    lecteur voie de quoi il s'agit.

    ⚠ Le plancher `1/√n` est celui de `174`, appliqué pour que les deux ajustements soient refusés
    par la MÊME règle. Il vaut pour une direction, pas pour un maximum pris sur `m` pentes : c'est
    la permutation qui paie cette maximisation, pas lui.
    """
    pret = _fort(courbe, plancher, minimum)
    if pret is None:
        return None
    k, phi, poids = pret
    n = int(len(k))
    total = float(poids.sum())
    m = int(len(courbe))

    def norme(beta: float) -> float:
        psi = phi - float(beta) * k
        return float(np.hypot(float((poids * np.cos(psi)).sum()),
                              float((poids * np.sin(psi)).sum())))

    pas = 2.0 * np.pi / float(m)
    bins = pas * np.arange(m, dtype=float)
    valeurs = [norme(b) for b in bins]
    j = int(np.argmax(valeurs))
    au_bin = float(valeurs[j])
    # ⚠ L'affinage encadre le meilleur bin par ses deux voisins : entre deux bins adjacents la
    # transformee n'a qu'un sommet, donc une recherche ternaire y converge.
    bas, haut = bins[j] - pas, bins[j] + pas
    tolerance = np.radians(1e-4)  # sous la precision publiee de la pente
    for _ in range(200):
        if haut - bas <= tolerance:
            break
        a = bas + (haut - bas) / 3.0
        b = haut - (haut - bas) / 3.0
        if norme(a) < norme(b):
            bas = a
        else:
            haut = b
    beta = 0.5 * (bas + haut)
    meilleure = norme(beta)
    if meilleure < au_bin:  # l'affinage ne doit jamais perdre
        beta, meilleure = float(bins[j]), au_bin
    resultante = meilleure / max(total, 1e-12)
    if resultante <= 1.0 / np.sqrt(n):
        return None
    psi = phi - beta * k
    intercepte = float(np.degrees(np.arctan2(float((poids * np.sin(psi)).sum()),
                                             float((poids * np.cos(psi)).sum()))) / 2.0) % 180.0
    # ⚠ La pente est repliee dans (-90, 90] degres par couche en angle simple : au-dela elle
    # designerait la meme suite par aliasing, et un nombre plus grand se lirait comme plus de
    # rotation alors que c'est la meme.
    rotation = float(np.degrees(beta) / 2.0)
    rotation = ((rotation + 90.0) % 180.0) - 90.0
    return {"quoi": "affine", "couches": n, "part_atteinte": round(float(resultante), 3),
            "angle_deg": round(intercepte, 3),
            "rotation_deg_par_couche": round(rotation, 4),
            "demi_tour_en_couches": (round(180.0 / abs(rotation), 1) if abs(rotation) > 1e-9
                                     else None),
            "part_au_meilleur_bin": round(float(au_bin / max(total, 1e-12)), 3),
            "pentes_balayees": m}


def lajustement_en_deux_segments(courbe, plancher: float = PLANCHER_DE_COHERENCE,
                                 minimum: int = COUCHES_MINIMALES) -> dict | None:
    """L'ajustement de `174`, ramené aux mêmes champs — une MARCHE à une frontière.

    ⚠ Il appelle `la_coupe_par_ajustement` sans la redéfinir : la recette réparée de `174` est
    publiée, et en réécrire l'arithmétique ici en ferait une seconde définition.
    """
    lu = la_coupe_par_ajustement(courbe)
    if lu is None:
        return None
    return {"quoi": "deux_segments", "couches": int(lu["couches"]),
            "part_atteinte": round(float(lu["part_atteinte"]), 3),
            "coupe": int(lu["coupe"]), "bascule_deg": lu["bascule_deg"],
            "temoin_deg": lu["temoin_deg"]}


LES_AJUSTEMENTS = {"constant": lajustement_constant,
                   "marche": lajustement_en_deux_segments,
                   "derive": lajustement_affine}


def la_fenetre_a_expliquer(courbe, largeur: int) -> int | None:
    """La fenêtre où le NUL explique le MOINS — celle qui a quelque chose à expliquer.

    ⭐⭐⭐⭐ C'EST LE NUL QUI CHOISIT LA FENÊTRE, ET AUCUN DES DEUX CANDIDATS. Une première version
    laissait chaque ajustement prendre sa meilleure fenêtre par la part atteinte, et la batterie a
    jugé « dérive » une marche construite : les deux ajustements retenaient une fenêtre HOMOGÈNE,
    où tous deux atteignent un, et le verdict se décidait alors sur les mélanges, c'est-à-dire sur
    la liberté de chacun et non sur la matière. C'est le défaut que `175` a mesuré — une fenêtre
    sans frontière rend une part de un — réapparu un étage plus haut.

    ⚠⚠ L'AJUSTEMENT CONSTANT EST AVEUGLE À LA FORME : il ne sait ni ce qu'est une marche ni ce
    qu'est une dérive, donc choisir par lui ne favorise ni l'un ni l'autre. Et la part qu'il atteint
    est basse exactement là où une seule direction ne suffit pas, ce qui est la définition d'une
    fenêtre à expliquer.

    ⚠ Une fenêtre où le nul est REFUSÉ vaut zéro : une seule direction n'y explique rien du tout,
    donc elle est la première à expliquer. Les égalités se tranchent par le départ le plus petit,
    pour que deux exécutions rendent la même fenêtre.
    """
    departs = les_fenetres(len(courbe), int(largeur))
    if not departs:
        return None
    def part_du_nul(d: int) -> float:
        lu = lajustement_constant(courbe[d:d + int(largeur)])
        return 0.0 if lu is None else float(lu["part_atteinte"])
    return int(min(departs, key=lambda d: (part_du_nul(d), d)))


def sur_la_fenetre(courbe, largeur: int, ajuster) -> dict | None:
    """L'ajustement lu sur la fenêtre que le nul a désignée — la même pour les deux candidats."""
    d = la_fenetre_a_expliquer(courbe, largeur)
    if d is None:
        return None
    lu = ajuster(courbe[d:d + int(largeur)])
    return None if lu is None else {**lu, "depart": int(d)}


def contre_les_melanges(courbe, ajuster, largeur: int | None = None,
                        permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Un ajustement, et le MÊME ajustement sur des couches mélangées — son excédent.

    ⭐⭐⭐⭐ L'EXCÉDENT EST LA QUANTITÉ QUI SE COMPARE. Mélanger conserve chaque angle et chaque
    cohérence, donc conserve la liberté de l'ajustement, et ne détruit que l'ordre en profondeur.
    La part réelle moins la part médiane des mélanges est donc ce que la profondeur explique, et
    rien d'autre — c'est ce qui rend comparables deux ajustements qui n'ont pas la même liberté.

    ⚠ La graine est fixe et dérivée du numéro de permutation : deux exécutions rendent le même
    compte. Un mélange que l'ajustement refuse compte comme DÉPASSÉ, le réel faisant mieux.
    """
    def lire(c):
        return ajuster(c) if largeur is None else sur_la_fenetre(c, largeur, ajuster)

    reel = lire(courbe)
    if reel is None:
        return {"decidable": False, "raison": "l'ajustement ne se prononce pas",
                "permutations": int(permutations)}
    parts, refuses = [], 0
    for t in range(int(permutations)):
        r = np.random.default_rng(int(graine) + t)
        m = lire([courbe[i] for i in r.permutation(len(courbe))])
        if m is None:
            refuses += 1
            continue
        parts.append(float(m["part_atteinte"]))
    mediane = float(statistics.median(parts)) if parts else 0.0
    return {"decidable": True, **reel,
            "permutations": int(permutations), "permutations_lues": len(parts),
            "permutations_refusees": int(refuses),
            "part_mediane_des_melanges": (round(mediane, 3) if parts else None),
            "part_maximale_des_melanges": (round(float(max(parts)), 3) if parts else None),
            "excedent": round(float(reel["part_atteinte"]) - mediane, 3),
            "depasse_tous_les_melanges": bool(
                all(float(reel["part_atteinte"]) > x for x in parts))}


def le_verdict(courbe, largeur: int | None = None, permutations: int = PERMUTATIONS,
               graine: int = GRAINE) -> dict:
    """Marche, dérive, ou ni l'une ni l'autre — décidé par les excédents, jamais par les parts.

    ⚠⚠ UN DÉPART NUL SE DIT AU LIEU D'ÊTRE TRANCHÉ. Deux excédents égaux à la précision publiée ne
    désignent personne, et laisser l'ordre des candidats décider ferait d'un détail d'écriture un
    résultat.

    ⚠ Le nul est rendu à côté : sans lui, « la marche atteint 0,99 » ne dit pas si la fenêtre a une
    frontière ou si elle est simplement homogène.
    """
    plat = (lajustement_constant(courbe) if largeur is None
            else sur_la_fenetre(courbe, largeur, lajustement_constant))
    marche = contre_les_melanges(courbe, lajustement_en_deux_segments, largeur,
                                 permutations, graine)
    derive = contre_les_melanges(courbe, lajustement_affine, largeur, permutations, graine)
    candidats = [(nom, d) for nom, d in (("marche", marche), ("derive", derive))
                 if d.get("decidable") and d["depasse_tous_les_melanges"]]

    def par(cle: str):
        # ⚠ UN DEPART NUL SE DIT AU LIEU D'ETRE TRANCHE : deux valeurs egales a la precision
        # publiee ne designent personne, et laisser l'ordre des candidats decider ferait d'un
        # detail d'ecriture un resultat.
        nul = (len(candidats) == 2
               and abs(candidats[0][1][cle] - candidats[1][1][cle]) < 1e-9)
        return (None if (not candidats or nul) else max(
            candidats, key=lambda t: t[1][cle])[0]), bool(nul)

    gagnant, nul = par("excedent")
    brut, nul_brut = par("part_atteinte")
    return {"decidable": bool(marche.get("decidable") or derive.get("decidable")),
            "part_constante": (plat["part_atteinte"] if plat else None),
            "la_marche": marche, "la_derive": derive,
            "candidats": [nom for nom, _ in candidats],
            "depart_nul": bool(nul), "gagnant": gagnant,
            # ⚠⚠⚠ LA REGLE BRUTE EST UN CONTROLE NOMME, PAS UNE SECONDE REPONSE. `174` mesure
            # cote a cote la recette refutee et la recette reparee, et c'est l'ECART entre elles
            # qui est le resultat ; ici l'ecart entre les deux regles dit ce que l'excedent
            # achete, au lieu de le faire croire.
            "gagnant_par_les_parts_brutes": brut, "depart_nul_par_les_parts_brutes": nul_brut,
            "les_deux_regles_saccordent": bool(brut == gagnant)}


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def sur_les_matieres_construites(largeur: int, permutations: int = PERMUTATIONS) -> dict:
    """Les trois contrôles, et chacun doit rendre une réponse DIFFÉRENTE.

    ⭐⭐⭐⭐ SANS LES TROIS, LE VERDICT NE PROUVE RIEN. Un juge qui dirait « marche » partout passe
    le contrôle de la marche ; un juge qui dirait « dérive » partout passe celui de la dérive ; un
    juge qui ne dirait jamais rien passe celui du bruit. Seuls les trois ensemble excluent les trois
    juges dégénérés, et aucun n'exige de seuil : la réponse de chaque matière est CONSTRUITE.
    """
    matieres = [("une marche", une_marche(COUCHES_DE_LA_CAMPAGNE), "marche"),
                ("une dérive", une_derive(COUCHES_DE_LA_CAMPAGNE, ETENDUE_DE_LA_DERIVE_DEG),
                 "derive"),
                ("du bruit", du_bruit(COUCHES_DE_LA_CAMPAGNE), None)]
    lignes = []
    for nom, courbe, attendu in matieres:
        v = le_verdict(courbe, largeur, permutations)
        lignes.append({"matiere": nom, "attendu": attendu, **v,
                       "le_verdict_est_celui_construit": bool(v["gagnant"] == attendu)})
    return {"cas": len(lignes),
            "tous_conformes": bool(all(x["le_verdict_est_celui_construit"] for x in lignes)),
            "lignes": lignes}


def sur_la_fixture(largeur: int, permutations: int = PERMUTATIONS) -> dict:
    """La fixture à deux plis, lue par le MÊME chemin que le rouleau — l'étalon de la marche.

    ⭐ C'est une matière dont la bascule est construite et dont la profondeur ne tourne pas : le
    verdict doit y être « marche » à tous les décalages. C'est le contrôle qui donne son échelle à
    ce que le rouleau rendra, mesuré par le même instrument.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = C.VOXEL_FIN_UM, C.PAS_UM
    lignes = []
    for k in range(12):
        dec = float(pas) * k / 12.0
        v = le_verdict(courbe_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, dec, 0.5, 2, vx, pas),
                       largeur, permutations)
        lignes.append({"decalage_um": round(dec, 3), **v})
    marches = [x for x in lignes if x["gagnant"] == "marche"]
    derives = [x for x in lignes if x["gagnant"] == "derive"]
    return {"cellules": len(lignes), "marches": len(marches), "derives": len(derives),
            "sans_verdict": int(sum(1 for x in lignes if x["gagnant"] is None)),
            "excedent_median_de_la_marche": _med([x["la_marche"]["excedent"] for x in lignes
                                                  if x["la_marche"].get("decidable")]),
            "excedent_median_de_la_derive": _med([x["la_derive"]["excedent"] for x in lignes
                                                  if x["la_derive"].get("decidable")]),
            "rotation_mediane_deg_par_couche": _med(
                [abs(x["la_derive"]["rotation_deg_par_couche"]) for x in lignes
                 if x["la_derive"].get("decidable")]),
            "lignes": lignes}


def ce_que_le_rouleau_a_rendu(chemin: Path = CE_QUE_LE_ROULEAU_A_RENDU) -> dict | None:
    """La bascule et le témoin que `176` a PUBLIÉS sur le vrai rouleau, relus de sa mesure.

    ⚠ Ils sont LUS et non recopiés : deux écritures d'un même nombre sont deux nombres qui peuvent
    se contredire, et celui-ci a un producteur.
    """
    if not chemin.exists():
        return None
    v = json.loads(chemin.read_text(encoding="utf-8")).get("le_verdict", {})
    if v.get("bascule_mediane_du_rouleau_deg") is None:
        return None
    return {"bascule_deg": float(v["bascule_mediane_du_rouleau_deg"]),
            "temoin_deg": float(v["temoin_median_du_rouleau_deg"])}


def lechelle_des_tours(bascule_deg: float) -> list[float]:
    """Les amplitudes de l'échelle : le quart de tour, ses moitiés, puis celle du rouleau.

    ⚠ ELLE EST DÉRIVÉE, PAS CHOISIE. On part du quart de tour — ce qu'une bascule recto/verso vaut
    et ce que la marche construite de `174` porte — et on halve tant qu'on reste AU-DESSUS de la
    bascule que `176` a mesurée sur le rouleau. La dernière barreau est cette bascule elle-même,
    donc l'échelle encadre exactement la question posée.
    """
    echelle, x = [], float(LE_QUART_DE_TOUR)
    while x > float(bascule_deg):
        echelle.append(round(x, 4))
        x /= 2.0
    return echelle + [round(float(bascule_deg), 4)]


def lechelle_des_dispersions(temoin_deg: float) -> list[float]:
    """Les dispersions de l'échelle : le témoin du rouleau, ses moitiés, puis zéro.

    ⚠ La dispersion par couche est posée à la valeur du TÉMOIN que `176` publie. Ce n'est pas une
    identité — un témoin est un écart entre deux demi-tranches, pas un écart-type — et ce que ce
    choix produit est MESURÉ et imprimé plutôt que supposé : la dernière ligne du tableau dit ce que
    le juge rend là où la matière est aussi dispersée que le rouleau.
    """
    return [0.0, round(float(temoin_deg) / 4.0, 4), round(float(temoin_deg) / 2.0, 4),
            round(float(temoin_deg), 4)]


def une_courbe_bruitee(forme: str, couches: int, amplitude: float, dispersion: float,
                       graine: int, frontiere: int = FRONTIERE) -> list:
    """Une marche ou une dérive du MÊME tour total, avec une dispersion par couche.

    ⚠ Les deux formes portent exactement le même tour : elles ne diffèrent que par sa répartition,
    d'un coup ou couche après couche. Sans cette égalité, le verdict mesurerait l'amplitude, que
    `176` a déjà mesurée, au lieu de la forme.
    """
    r = np.random.default_rng(int(graine))
    base = (np.concatenate([np.zeros(int(frontiere)),
                            np.full(int(couches) - int(frontiere), float(amplitude))])
            if forme == "marche" else np.linspace(0.0, float(amplitude), int(couches)))
    ecart = (r.normal(0.0, float(dispersion), int(couches)) if dispersion > 0.0
             else np.zeros(int(couches)))
    return [[float((a + b) % 180.0), 0.9] for a, b in zip(base, ecart)]


def le_domaine(largeur: int, bascule_deg: float, temoin_deg: float,
               graines: int = GRAINES_PAR_CELLULE, permutations: int = PERMUTATIONS,
               graine: int = GRAINE) -> dict:
    """Jusqu'à quel tour et jusqu'à quelle dispersion le juge rend-il la forme CONSTRUITE ?

    ⭐⭐⭐⭐ UN JUGE SANS DOMAINE N'EST PAS UN INSTRUMENT. Celui-ci sépare une marche d'une dérive au
    quart de tour ; savoir s'il les sépare encore au tour que le rouleau montre est la seule chose
    qui décide si on a le droit de le pointer dessus. Le domaine se mesure sur des matières dont la
    forme est construite, donc aucune cellule ne demande de seuil : on compte les verdicts justes.

    ⚠ Chaque cellule est tirée `graines` fois, sinon une cellule est une anecdote.
    """
    amplitudes = lechelle_des_tours(bascule_deg)
    dispersions = lechelle_des_dispersions(temoin_deg)
    cellules = []
    for amp in amplitudes:
        for disp in dispersions:
            justes, bruts, desaccords = {}, {}, 0
            for forme in ("marche", "derive"):
                n, b = 0, 0
                for g in range(int(graines)):
                    c = une_courbe_bruitee(forme, COUCHES_DE_LA_CAMPAGNE, amp, disp,
                                           int(graine) + 1000 * g)
                    lu = le_verdict(c, largeur, permutations)
                    n += int(lu["gagnant"] == forme)
                    b += int(lu["gagnant_par_les_parts_brutes"] == forme)
                    desaccords += int(not lu["les_deux_regles_saccordent"])
                justes[forme], bruts[forme] = int(n), int(b)
            cellules.append({"tour_deg": amp, "dispersion_deg": disp,
                             "marches_justes": justes["marche"],
                             "derives_justes": justes["derive"],
                             "marches_justes_par_les_parts_brutes": bruts["marche"],
                             "derives_justes_par_les_parts_brutes": bruts["derive"],
                             "desaccords_entre_les_deux_regles": int(desaccords),
                             "les_deux_formes_sont_rendues": bool(
                                 justes["marche"] == int(graines)
                                 and justes["derive"] == int(graines))})
    tenus = [c["tour_deg"] for c in cellules
             if c["tour_deg"] > 0 and all(x["les_deux_formes_sont_rendues"] for x in cellules
                                          if x["tour_deg"] == c["tour_deg"])]
    au_rouleau = [c for c in cellules
                  if c["tour_deg"] == round(float(bascule_deg), 4)
                  and c["dispersion_deg"] == round(float(temoin_deg), 4)]
    return {"graines_par_cellule": int(graines), "tours": amplitudes,
            "dispersions": dispersions, "cellules": cellules,
            "desaccords_entre_les_deux_regles": int(
                sum(c["desaccords_entre_les_deux_regles"] for c in cellules)),
            "justes_par_lexcedent": int(sum(c["marches_justes"] + c["derives_justes"]
                                            for c in cellules)),
            "justes_par_les_parts_brutes": int(
                sum(c["marches_justes_par_les_parts_brutes"]
                    + c["derives_justes_par_les_parts_brutes"] for c in cellules)),
            "le_plus_petit_tour_tenu_deg": (min(tenus) if tenus else None),
            "au_tour_du_rouleau": (au_rouleau[0] if au_rouleau else None)}


def juger(matieres: dict, fixture: dict, domaine: dict, rouleau: dict | None) -> dict:
    """Le juge existe, voici son domaine, et voici s'il couvre la question que `176` a laissée.

    ⚠⚠⚠ ET C'EST CE QUI INTERDIT DE LE POINTER SUR LA MATIÈRE. `174` a refusé de poser sur le
    rouleau une recette que son contrôle venait de réfuter ; le même refus vaut ici pour une
    amplitude, et pour la même raison : un verdict rendu hors du domaine mesuré n'est pas un
    verdict faible, c'est un nombre sans garantie sous un nom qui en promet une.
    """
    petit = domaine["le_plus_petit_tour_tenu_deg"]
    au_rouleau = domaine["au_tour_du_rouleau"]
    couvre = bool(au_rouleau and au_rouleau["les_deux_formes_sont_rendues"])
    return {"decidable": bool(matieres["tous_conformes"] and fixture["marches"]
                              == fixture["cellules"]),
            "raison": (None if matieres["tous_conformes"]
                       else "les matières construites ne sont pas jugées comme elles sont bâties"),
            "le_juge_separe_au_quart_de_tour": bool(
                any(c["les_deux_formes_sont_rendues"] for c in domaine["cellules"]
                    if c["tour_deg"] == LE_QUART_DE_TOUR)),
            "le_plus_petit_tour_tenu_deg": petit,
            "il_vaut_le_quart_de_tour_fois": (round(petit / LE_QUART_DE_TOUR, 3)
                                              if petit else None),
            "la_bascule_du_rouleau_deg": (rouleau["bascule_deg"] if rouleau else None),
            "le_temoin_du_rouleau_deg": (rouleau["temoin_deg"] if rouleau else None),
            "marches_justes_au_tour_du_rouleau": (au_rouleau["marches_justes"]
                                                  if au_rouleau else None),
            "derives_justes_au_tour_du_rouleau": (au_rouleau["derives_justes"]
                                                  if au_rouleau else None),
            "graines_par_cellule": domaine["graines_par_cellule"],
            "la_bascule_du_rouleau_vaut_le_plancher_fois": (
                round(float(rouleau["bascule_deg"]) / petit, 4)
                if (rouleau and petit) else None),
            # ⚠⚠⚠ LE SENS DE LA PANNE EST LA MOITIE QUI COMPTE. Un juge qui se trompe au hasard
            # laisse la question ouverte ; celui-ci se trompe DANS UN SENS — il lit une derive
            # comme une marche — donc la lecture « une marche de 6,862° » que `176` publie est
            # exactement ce qu'il rendrait sur une dérive.
            "le_juge_rate_du_cote_de_la_derive": bool(
                au_rouleau and au_rouleau["marches_justes"] > au_rouleau["derives_justes"]),
            "verdicts_justes_par_lexcedent": domaine["justes_par_lexcedent"],
            "verdicts_justes_par_les_parts_brutes": domaine["justes_par_les_parts_brutes"],
            "verdicts_ou_les_deux_regles_different": domaine["desaccords_entre_les_deux_regles"],
            "lexcedent_fait_mieux_que_la_part_brute": bool(
                domaine["justes_par_lexcedent"] > domaine["justes_par_les_parts_brutes"]),
            "le_domaine_couvre_le_rouleau": couvre,
            "on_peut_le_pointer_sur_le_rouleau": couvre}


def mesurer(graines: int = GRAINES_PAR_CELLULE,
            permutations: int = PERMUTATIONS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    # ⚠⚠ LA LARGEUR EST CELLE DE `176`, DERIVEE DU PAS ET DU VOXEL, jamais ecrite a la main : lire
    # la meme matiere par une autre fenetre repondrait a une autre question.
    largeur = int(round(C.PAS_UM / 2.0 / C.VOXEL_FIN_UM))
    rouleau = ce_que_le_rouleau_a_rendu()
    if rouleau is None:
        return {"message": "la mesure de `176` est absente : son verdict donne l'échelle"}
    matieres = sur_les_matieres_construites(largeur, permutations)
    fixture = sur_la_fixture(largeur, permutations)
    domaine = le_domaine(largeur, rouleau["bascule_deg"], rouleau["temoin_deg"],
                         graines, permutations)
    return {"largeur_en_couches": largeur, "pas_um": float(C.PAS_UM),
            "voxel_um": float(C.VOXEL_FIN_UM), "couches": int(COUCHES_DE_LA_CAMPAGNE),
            "frontiere": int(FRONTIERE), "le_quart_de_tour_deg": float(LE_QUART_DE_TOUR),
            "permutations": int(permutations), "graine": int(GRAINE),
            "etendue_de_la_derive_deg": float(ETENDUE_DE_LA_DERIVE_DEG),
            "le_rouleau": rouleau, "les_matieres": matieres, "la_fixture": fixture,
            "le_domaine": domaine,
            "le_verdict": juger(matieres, fixture, domaine, rouleau)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    m, fx, d, v = r["les_matieres"], r["la_fixture"], r["le_domaine"], r["le_verdict"]
    print("LA PROFONDEUR TOURNE-T-ELLE, OU BASCULE-T-ELLE ?")
    print(f"  fenêtre {r['largeur_en_couches']} couches (un pli) sur {r['couches']} · "
          f"{r['permutations']} permutations · {d['graines_par_cellule']} graines par cellule")
    print()
    print("  LES MATIÈRES CONSTRUITES · chacune doit rendre une réponse différente")
    for x in m["lignes"]:
        ma, de = x["la_marche"], x["la_derive"]
        print(f"   {x['matiere']:<12} nul {x['part_constante']} · marche "
              f"{ma.get('part_atteinte')}/{ma.get('part_mediane_des_melanges')} excédent "
              f"{ma.get('excedent')} · dérive {de.get('part_atteinte')}/"
              f"{de.get('part_mediane_des_melanges')} excédent {de.get('excedent')}")
        print(f"   {'':<12} → {x['gagnant']} (construit : {x['attendu']}) "
              f"{'★' if x['le_verdict_est_celui_construit'] else '✗'}")
    print()
    print(f"  L'ÉTALON · la fixture à deux plis, {fx['cellules']} décalages · marche "
          f"{fx['marches']} · dérive {fx['derives']} · sans verdict {fx['sans_verdict']}")
    print(f"     excédents {fx['excedent_median_de_la_marche']} contre "
          f"{fx['excedent_median_de_la_derive']} · rotation lue "
          f"{fx['rotation_mediane_deg_par_couche']}°/couche")
    print()
    print(f"  LE DOMAINE · tours en ligne, dispersions en colonne, justes sur "
          f"{d['graines_par_cellule']} (marche / dérive)")
    entete = "  ".join(f"{x:>11.3f}" for x in d["dispersions"])
    print(f"   {'tour °':>9}   {entete}")
    for tour in d["tours"]:
        cells = [c for c in d["cellules"] if c["tour_deg"] == tour]
        ligne = "  ".join(f"{c['marches_justes']:>4}/{c['derives_justes']:<6}" for c in cells)
        marque = "★" if all(c["les_deux_formes_sont_rendues"] for c in cells) else " "
        print(f"   {tour:>9.3f} {marque} {ligne}")
    print()
    print(f"  ★ LE VERDICT · la bascule du rouleau vaut {v['la_bascule_du_rouleau_deg']}° pour un "
          f"témoin de {v['le_temoin_du_rouleau_deg']}°")
    for cle in ("le_juge_separe_au_quart_de_tour", "le_plus_petit_tour_tenu_deg",
                "il_vaut_le_quart_de_tour_fois", "marches_justes_au_tour_du_rouleau",
                "derives_justes_au_tour_du_rouleau", "la_bascule_du_rouleau_vaut_le_plancher_fois",
                "le_juge_rate_du_cote_de_la_derive", "verdicts_justes_par_lexcedent",
                "verdicts_justes_par_les_parts_brutes",
                "verdicts_ou_les_deux_regles_different",
                "lexcedent_fait_mieux_que_la_part_brute", "le_domaine_couvre_le_rouleau",
                "on_peut_le_pointer_sur_le_rouleau"):
        print(f"     {cle:<40} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    largeur = int(round(C.PAS_UM / 2.0 / C.VOXEL_FIN_UM))
    marche = une_marche(COUCHES_DE_LA_CAMPAGNE)
    derive = une_derive(COUCHES_DE_LA_CAMPAGNE, ETENDUE_DE_LA_DERIVE_DEG)
    bruit = du_bruit(COUCHES_DE_LA_CAMPAGNE)

    # ⭐ L'INVARIANCE DU NUL EST CE QUI REND L'EXCEDENT HONNETE : si l'ajustement constant bougeait
    # au melange, l'excedent melangerait la profondeur et la liberte. Un refus compte comme une
    # reponse : il doit etre le meme sur la courbe et sur chacun de ses melanges.
    for nom, c in (("marche", marche), ("dérive", derive), ("bruit", bruit)):
        base = lajustement_constant(c)
        attendu = None if base is None else base["part_atteinte"]
        vus = set()
        for t in range(19):
            r = np.random.default_rng(GRAINE + t)
            m = lajustement_constant([c[i] for i in r.permutation(len(c))])
            vus.add(None if m is None else m["part_atteinte"])
        v(f"le nul est invariant par permutation sur {nom}", vus == {attendu},
          f"{sorted(str(x) for x in vus)[:3]} contre {attendu}")

    # ⚠ LES DEUX EXTENSIONS NE PEUVENT PAS FAIRE MOINS QUE LE NUL : couper donne |Σa|+|Σb| ≥ |Σa+Σb|
    # et l'affine contient la pente nulle. C'est ce qui interdit de comparer deux parts brutes.
    for nom, c in (("marche", marche), ("dérive", derive), ("bruit", bruit)):
        base = lajustement_constant(c)
        for quoi, lu in (("marche", lajustement_en_deux_segments(c)),
                         ("dérive", lajustement_affine(c))):
            if base is None or lu is None:
                continue
            v(f"l'ajustement {quoi} ne fait jamais moins que le nul sur {nom}",
              lu["part_atteinte"] >= base["part_atteinte"] - 1e-9,
              f"{lu['part_atteinte']} contre {base['part_atteinte']}")

    # ⭐⭐⭐⭐ L'AFFINE RETROUVE UNE ROTATION CONSTRUITE : la reponse est connue AVANT la mesure.
    attendue = ETENDUE_DE_LA_DERIVE_DEG / float(COUCHES_DE_LA_CAMPAGNE - 1)
    lu = lajustement_affine(derive)
    v("l'affine lit la dérive", lu is not None)
    if lu is not None:
        v("l'affine retrouve la rotation construite",
          abs(abs(lu["rotation_deg_par_couche"]) - attendue) <= 1e-4,
          f"{lu['rotation_deg_par_couche']} contre {round(attendue, 4)}")
        v("l'affine atteint tout sur une dérive franche", lu["part_atteinte"] >= 0.999,
          str(lu["part_atteinte"]))
        # ⚠ HYGIENE : si la rotation construite tombait SUR un bin, l'affinage n'aurait rien a
        # gagner et la verification suivante ne pourrait pas echouer.
        bins = (np.radians(2.0 * attendue) * COUCHES_DE_LA_CAMPAGNE) / (2.0 * np.pi)
        v("la rotation construite ne tombe pas sur un bin",
          abs(bins - round(bins)) > 0.25, f"{bins:.4f} bin")
        v("l'affinage gagne sur le meilleur bin",
          lu["part_atteinte"] > lu["part_au_meilleur_bin"],
          f"{lu['part_atteinte']} contre {lu['part_au_meilleur_bin']}")
        v("la pente est repliée dans un demi-tour par couche",
          abs(lu["rotation_deg_par_couche"]) <= 90.0)

    # ⭐⭐⭐⭐ LA FENETRE EST CHOISIE PAR LE NUL, ET LA REPONSE EST CONNUE AVANT LA MESURE : sur une
    # courbe homogene sauf une marche posee a une couche choisie, la fenetre retenue doit CONTENIR
    # cette couche. Une fenetre choisie par la part atteinte d'un candidat en retiendrait une
    # homogene, ou tous deux atteignent un et ou il n'y a rien a expliquer.
    posee = 54
    temoin = ([[20.0, 0.9]] * posee
              + [[110.0, 0.9]] * (COUCHES_DE_LA_CAMPAGNE - posee))
    d = la_fenetre_a_expliquer(temoin, largeur)
    v("la fenêtre retenue contient la frontière posée",
      d is not None and d < posee < d + largeur, f"départ {d} pour une frontière à {posee}")

    # ⭐⭐⭐⭐ LES TROIS MATIERES CONSTRUITES, ET CHACUNE DOIT RENDRE UNE REPONSE DIFFERENTE. Sans
    # les trois, un juge qui dirait toujours la meme chose passerait l'une d'elles.
    m = sur_les_matieres_construites(largeur, PERMUTATIONS)
    for x in m["lignes"]:
        v(f"{x['matiere']} est jugée {x['attendu']}", x["le_verdict_est_celui_construit"],
          f"rendu {x['gagnant']} · excédents marche {x['la_marche'].get('excedent')} · "
          f"dérive {x['la_derive'].get('excedent')}")
        v(f"le gagnant de {x['matiere']} sort des candidats",
          x["gagnant"] is None or x["gagnant"] in x["candidats"],
          f"{x['gagnant']} hors de {x['candidats']}")
    v("les trois réponses sont différentes",
      len({x["gagnant"] for x in m["lignes"]}) == 3,
      str([x["gagnant"] for x in m["lignes"]]))

    # ⭐ L'ETALON : une matiere dont la bascule est construite et dont la profondeur ne tourne pas.
    fx = sur_la_fixture(largeur, PERMUTATIONS)
    v("la fixture à deux plis est jugée marche partout", fx["marches"] == fx["cellules"],
      f"marche {fx['marches']} · dérive {fx['derives']} · sans verdict {fx['sans_verdict']} "
      f"sur {fx['cellules']}")
    v("l'étalon sépare les deux excédents",
      (fx["excedent_median_de_la_marche"] or 0) > (fx["excedent_median_de_la_derive"] or 0),
      f"{fx['excedent_median_de_la_marche']} contre {fx['excedent_median_de_la_derive']}")

    # ⭐⭐⭐⭐ LE DOMAINE, ET C'EST LUI QUI DECIDE SI ON A LE DROIT DE POINTER CE JUGE SUR LA
    # MATIERE. Il est repris ici a moins de graines : ce qui est asserte n'est pas un compte mais
    # une STRUCTURE — le quart de tour tient, le tour du rouleau ne tient pas, et la panne a un
    # sens.
    rouleau = ce_que_le_rouleau_a_rendu()
    v("la mesure de `176` donne l'échelle", rouleau is not None)
    if rouleau is not None:
        tours = lechelle_des_tours(rouleau["bascule_deg"])
        v("l'échelle part du quart de tour", tours[0] == LE_QUART_DE_TOUR, str(tours[0]))
        v("l'échelle descend jusqu'à la bascule du rouleau",
          tours[-1] == round(rouleau["bascule_deg"], 4), str(tours[-1]))
        # ⚠ HYGIENE : le dernier barreau halve doit ENCADRER la bascule, sinon l'echelle la
        # depasserait sans l'atteindre et le tableau ne repondrait pas a la question posee.
        v("l'échelle encadre la bascule du rouleau",
          len(tours) >= 3 and tours[-2] > rouleau["bascule_deg"] >= tours[-2] / 2.0,
          f"{tours[-2]} puis {tours[-2] / 2.0} autour de {rouleau['bascule_deg']}")
        # ⚠⚠ LES DEUX FORMES PORTENT LE MEME TOUR TOTAL : sans cette egalite le verdict mesurerait
        # l'amplitude, que `176` a deja mesuree, au lieu de la forme.
        for amp in (LE_QUART_DE_TOUR, rouleau["bascule_deg"]):
            tours_lus = []
            for forme in ("marche", "derive"):
                base = [x[0] for x in une_courbe_bruitee(forme, COUCHES_DE_LA_CAMPAGNE,
                                                         amp, 0.0, GRAINE)]
                tours_lus.append(round(max(base) - min(base), 6))
            v(f"les deux formes portent le même tour à {round(amp, 3)}°",
              tours_lus[0] == tours_lus[1] == round(amp, 6), str(tours_lus))

        d = le_domaine(largeur, rouleau["bascule_deg"], rouleau["temoin_deg"], 5, PERMUTATIONS)
        haut = [c for c in d["cellules"] if c["tour_deg"] == LE_QUART_DE_TOUR]
        v("au quart de tour les deux formes sont rendues à toutes les dispersions",
          all(c["les_deux_formes_sont_rendues"] for c in haut),
          str([(c["marches_justes"], c["derives_justes"]) for c in haut]))
        bas = d["au_tour_du_rouleau"]
        v("le tour du rouleau est lu", bas is not None)
        if bas is not None:
            v("au tour du rouleau les deux formes ne sont PAS rendues",
              not bas["les_deux_formes_sont_rendues"],
              f"{bas['marches_justes']}/{bas['derives_justes']} sur 5")
            # ⚠⚠⚠ LE SENS DE LA PANNE : un juge qui se trompe au hasard laisse la question
            # ouverte, celui-ci lit une derive comme une marche.
            v("la panne est du côté de la dérive",
              bas["marches_justes"] > bas["derives_justes"],
              f"marche {bas['marches_justes']} · dérive {bas['derives_justes']}")
        # ⚠⚠⚠ L'EXCEDENT DOIT ETRE EXERCE PAR QUELQUE CHOSE, SINON C'EST UNE PRECAUTION QUE
        # RIEN NE MESURE. La regle BRUTE — comparer les parts au lieu des excedents — est portee
        # comme controle nomme, et ce qui est asserte est qu'elle rend un AUTRE tableau : sans
        # desaccord, l'excedent ne s'achete rien et il faudrait le retirer.
        v("les deux règles ne rendent pas le même tableau",
          d["desaccords_entre_les_deux_regles"] > 0,
          f"{d['desaccords_entre_les_deux_regles']} désaccords")
        v("l'excédent ne fait pas moins bien que la part brute",
          d["justes_par_lexcedent"] >= d["justes_par_les_parts_brutes"],
          f"{d['justes_par_lexcedent']} contre {d['justes_par_les_parts_brutes']}")

    nom = "la_profondeur_tourne_t_elle_ou_bascule_t_elle.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e in echecs:
            print(f"   ✗ {e}")
        return 1
    print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--graines", type=int, default=GRAINES_PAR_CELLULE)
    p.add_argument("--permutations", type=int, default=PERMUTATIONS)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graines, a.permutations)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
