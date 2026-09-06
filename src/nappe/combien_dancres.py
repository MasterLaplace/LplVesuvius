#!/usr/bin/env python3
"""Combien d'ancres faut-il ? — et la troisième paie-t-elle encore ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `derouler_des_deux_bords` a établi une chose et une seule :
deux ancres valent bien mieux qu'une — l'erreur passe de 58,3 à 43,1 µm, et à 35,9 pondérée par
les bras. Et il a dit ce qu'il n'était pas : *« ce n'est pas une méthode, c'est une BORNE — elle
dit ce qu'on gagnerait si l'on avait deux ancres au lieu d'une, donc si l'effort doit aller vers
une meilleure propagation ou vers PLUS D'ANCRES »*. Cinq soupçons sur la mécanique du pas ont été
testés et écartés ; la seule piste qui ait rendu quelque chose est le **nombre d'ancres**. Ce
fichier va jusqu'au bout de cette piste : la troisième paie-t-elle, et où s'arrête le gain ?

⭐⭐ L'ESTIMATEUR N'A AUCUN PARAMÈTRE LIBRE, ET IL SE RAMÈNE AU CAS DÉJÀ VALIDÉ. Si l'erreur d'une
branche croît linéairement avec la longueur de son bras, alors la prédiction de l'ancre `i` vaut
$p_i \\simeq p + \\beta s_i$ où $s_i$ est son bras SIGNÉ. L'estimateur qui annule $\\beta$ est la
droite des moindres carrés en $s$, évaluée en $s = 0$. À deux ancres de signes opposés, elle rend
**exactement** la pondération par les bras déjà mesurée — ce n'est pas une ressemblance, c'est une
identité algébrique, et elle est vérifiée ici plutôt qu'affirmée.

⚠⚠⚠ CE FICHIER A PUBLIÉ « LA DÉRIVE ACCÉLÈRE », ET `pourquoi_la_derive_accelere` L'A RETIRÉ.
Le critère employé — « les incréments consécutifs croissent » — **omettait le plus grand
incrément de tous** : celui du bras zéro, dont l'erreur est nulle par définition, au bras un. La
suite complète est **41,1 puis 22,0 / 37,7 / 48,6** µm : le premier pas est le plus cher, et il
n'y a pas de tendance après lui. Le critère basculait en outre sur deux micromètres, et rendait
deux verdicts opposés sur deux populations qui mesurent la même chose.

⭐⭐ CE QUI EST VRAI ET REPRODUIT SUR LES DEUX POPULATIONS : l'erreur au bras `k` reste **SOUS**
`k` fois celle du bras un, et le coût par tour est **stable** — 41,1 puis 31,6 / 33,6 / 37,4 µm
ici. La dérive est donc à peu près **linéaire** avec un premier pas plus cher, ce qui est
exactement la prémisse dont l'estimateur a besoin, et ce qui explique que la parabole ne trouve
rien à annuler.

⚠⚠ LES POIDS NE DÉPENDENT QUE DES BRAS, JAMAIS DES DONNÉES. L'ordonnée à l'origine d'une droite
des moindres carrés est une combinaison linéaire des $p_i$ dont les coefficients ne contiennent
que les $s_i$. Aucun bit de la cible n'entre donc dans la combinaison : un dérouleur qui aurait
ses ancres pourrait l'appliquer sans jamais regarder où il doit arriver.

⚠⚠ CE QUE ÇA MESURE ET CE QUE ÇA NE MESURE PAS. Une ancre COÛTE — c'est une spire qu'il a fallu
tracer. Le résultat utile n'est donc pas « plus d'ancres, c'est mieux » mais la courbe : à partir
de combien la suivante ne paie plus. Et comme les sous-ensembles d'ancres sont énumérés par leurs
**bras signés**, la question « où poser la troisième » se lit dedans.

⚠ Aucune lecture du volume ici : le pas aveugle est le meilleur dérouleur mesuré et il ne lit
rien, donc cette tranche ne coûte pas un bloc.

Usage :
    uv run python src/nappe/combien_dancres.py --verifier
    uv run python src/nappe/combien_dancres.py --json docs/mesures/combien_dancres.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import itertools
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

# ⚠ Un seul lecteur de corpus pour tous les dérouleurs, et sa fixture hors ligne avec lui.
from le_corpus_des_spires import corpus_fabrique, corpus_publie  # noqa: E402
# ⚠ Le critère de forme vit chez la tranche qui l'a établi, et il n'est pas recopié : deux
# implémentations d'une même règle finiraient par rendre deux verdicts.
from pourquoi_la_derive_accelere import sous_lineaire  # noqa: E402


def poids_de_lajustement(bras: np.ndarray, degre: int = 1) -> np.ndarray:
    """Les poids qui annulent une erreur polynomiale en bras : l'ajustement évalué en 0.

    ⚠⚠⚠ ILS NE DÉPENDENT QUE DES BRAS. L'ordonnée à l'origine d'une régression de `p` sur `s`
    s'écrit $\\sum_i w_i p_i$ avec
    $w_i = 1/n - \\bar{s}(s_i - \\bar{s}) / \\sum_j (s_j - \\bar{s})^2$ : aucune valeur mesurée
    n'y entre. C'est ce qui autorise un dérouleur à s'en servir sans regarder sa cible —
    sinon ce ne serait pas un estimateur mais une correction.

    ⚠⚠ À DEUX ANCRES DE SIGNES OPPOSÉS, ELLE REND LA PONDÉRATION PAR LES BRAS déjà mesurée :
    pour $s = (-a, +b)$ on obtient $w = (b, a) / (a + b)$, donc la branche au bras COURT pèse le
    plus. La généralisation ne remplace pas le résultat précédent, elle le contient.

    ⚠ Si tous les bras sont ÉGAUX il n'y a pas de pente à estimer — la moyenne simple est
    rendue, et c'est la seule réponse honnête : rien dans les données ne dit de quel côté
    corriger. Idem pour une ancre seule, dont le poids vaut un.
    """
    s = np.asarray(bras, dtype=np.float64)
    n = len(s)
    if n == 0:
        return s
    # ⚠⚠ UN DEGRÉ NON IDENTIFIABLE EST REFUSÉ, PAS AJUSTÉ DE FORCE. Il faut au moins `degre + 1`
    # bras DISTINCTS pour qu'une courbe de ce degré soit déterminée ; avec moins, la pseudo-
    # inverse rendrait quand même des poids, tirés d'un système sous-déterminé, et l'estimateur
    # aurait l'air de marcher en n'ayant rien identifié.
    if degre >= len(set(s.tolist())):
        return np.full(n, 1.0 / n)
    if degre == 1:
        centre = s - s.mean()
        denom = float(centre @ centre)
        if denom <= 0.0:
            return np.full(n, 1.0 / n)
        return 1.0 / n - s.mean() * centre / denom
    # ⚠ Le degré 1 garde sa forme fermée : elle est exacte, elle se lit, et c'est elle que
    # l'identité avec la pondération par les bras porte. La forme générale n'est utilisée que
    # là où on en a besoin, pour ne pas remplacer un résultat vérifié par une pseudo-inverse.
    vandermonde = np.stack([s ** k for k in range(degre + 1)], axis=1)
    return np.linalg.pinv(vandermonde)[0]


def combiner_plusieurs(nuages: list[np.ndarray], poids: np.ndarray) -> np.ndarray:
    """Les nuages combinés point à point, tous ramenés sur la grille du PREMIER.

    ⚠⚠ LES ANCRES N'ONT PAS LA MÊME GRILLE — elles viennent de spires publiées différentes, donc
    de paramétrages différents. Les moyenner cellule à cellule apparierait des points qui n'ont
    rien à voir ; l'appariement se fait donc dans l'ESPACE, par plus proche voisin, ce qui est la
    seule correspondance que deux surfaces reconstruites partagent.

    ⚠ Le nuage de référence est le PREMIER de la liste, et l'appelant le choisit : le résultat a
    sa taille et sa densité. Prétendre qu'il existe une combinaison canonique de nuages de
    tailles différentes cacherait ce choix.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if not nuages or any(n.size == 0 for n in nuages):
        return np.zeros((0, 3))
    ref = nuages[0]
    out = poids[0] * ref
    for w, autre in zip(poids[1:], nuages[1:]):
        out = out + w * autre[cKDTree(autre).query(ref, k=1)[1]]
    return out


def jeux_dancres(rangs: list[int], cible: int, portee: int,
                 kmax: int) -> list[tuple[int, ...]]:
    """Tous les sous-ensembles d'ancres à portée de la cible, de une à `kmax`.

    ⚠⚠ ÉNUMÉRÉS PLUTÔT QUE CHOISIS PAR UNE POLITIQUE. « Prendre les k plus proches » est une
    politique, et elle tranche d'avance la question qu'on pose — où poser la troisième. En
    énumérant, chaque jeu est identifié par ses **bras signés**, donc la question se lit dans le
    résultat au lieu d'être décidée par le code.

    ⚠ La cible elle-même n'est jamais une ancre : elle est ce qu'on reconstruit.
    """
    voisins = [r for r in sorted(rangs) if r != cible and abs(r - cible) <= portee]
    return [c for k in range(1, kmax + 1) for c in itertools.combinations(voisins, k)]


def signature(bras: tuple[int, ...]) -> str:
    """Le nom d'un jeu d'ancres : ses bras signés, triés, séparés par des virgules."""
    return ",".join(f"{b:+d}" for b in sorted(bras))


def mesurer(cote: float | None = None, minimum: int = 30, portee: int = 3, kmax: int = 4,
            corpus: dict | None = None) -> dict:
    """Reconstruire chaque spire depuis tous les jeux d'ancres à portée, et juger par leur taille.

    ⚠⚠ La marche de chaque ancre vers sa cible est calculée UNE FOIS, puis partagée par tous les
    jeux qui la contiennent : recalculer ferait payer le nombre de sous-ensembles au lieu du
    nombre de paires, pour un résultat identique.
    """
    from derouler_des_deux_bords import ecart_signe, marcher  # noqa: PLC0415
    from le_pas_normal_atteint_la_spire import distance_a, essayer_le_pas, normales  # noqa: PLC0415, E501
    from le_raccrochage_a_la_matiere import BOITE_CENTRE, BOITE_COTE  # noqa: PLC0415

    c = corpus_publie() if corpus is None else corpus
    volume, voxel_um = c["volume"], float(c["voxel_um"])
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / voxel_um

    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - cote / 2, centre + cote / 2

    grilles, nuages = {}, {}
    for rang, (a, ok) in sorted(c["grilles"].items()):
        dans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dans.sum()) < minimum:
            continue
        idx = np.argwhere(dans)
        sous = (slice(int(idx[:, 0].min()), int(idx[:, 0].max()) + 1),
                slice(int(idx[:, 1].min()), int(idx[:, 1].max()) + 1))
        grilles[rang] = (a[sous].copy(), dans[sous].copy())
        nuages[rang] = a[ok]

    rangs = sorted(grilles)
    lignes = []
    for m in rangs:
        cible = nuages[m]
        # --- une marche par ancre, partagée par tous les jeux qui la contiennent ---
        marches, directions = {}, {}
        for r in rangs:
            if r == m or abs(r - m) > portee:
                continue
            a0, ok0 = grilles[r]
            n0, bon0 = normales(a0, ok0)
            if not bon0.any():
                continue
            # ⚠⚠ UN BIT DE SUPERVISION PAR ANCRE, DÉCLARÉ : le signe de la normale vient du
            # paramétrage de la grille et non de la matière, donc il est fixé au premier pas en
            # regardant la cible, une seule fois. Un jeu de k ancres en dépense donc k, et
            # c'est le prix qu'il faut compter contre son gain.
            e = essayer_le_pas(a0[bon0], n0[bon0], cible, pas_vx, voxel_um)
            sens = 1.0 if e["retenu"] == "+" else -1.0
            av, okv = marcher(a0, ok0, abs(m - r), pas_vx, sens)
            if int(okv.sum()) < minimum:
                continue
            marches[r] = av[okv]
            directions[r] = sens * n0[bon0].mean(axis=0)
        if len(marches) < 2:
            continue
        # ⚠ L'axe de projection est celui de l'ancre la plus BASSE présente : les ancres des deux
        # côtés marchent en sens contraires, donc les projeter chacune sur la sienne rendrait des
        # écarts tous positifs et cacherait l'opposition qu'on cherche à mesurer.
        axe = directions[min(marches)]
        for jeu in jeux_dancres(sorted(marches), m, portee, kmax):
            bras = tuple(r - m for r in jeu)
            w = poids_de_lajustement(np.array(bras, dtype=np.float64))
            nuage = [marches[r] for r in jeu]
            ajuste = combiner_plusieurs(nuage, w)
            # ⚠⚠⚠ LA COURBURE, MESURÉE PLUTÔT QUE SUPPOSÉE. La dérive n'étant pas linéaire, la
            # droite en annule la pente et laisse le terme suivant. Un ajustement de degré DEUX
            # l'annulerait aussi — et il faut trois ancres pour l'identifier, ce qui redonnerait
            # un rôle à la troisième : non plus moyenner, mais mesurer la courbure. C'est la
            # seule lecture du résultat qui ouvre quelque chose, donc elle est testée ici.
            w2 = poids_de_lajustement(np.array(bras, dtype=np.float64), degre=2)
            courbe = (combiner_plusieurs(nuage, w2) if len(jeu) >= 3 else None)
            # ⚠⚠ LE TÉMOIN EST LA MOYENNE SIMPLE : mêmes nuages, même appariement, même
            # machinerie — seuls les POIDS changent. Sans lui, « l'ajustement aide » serait
            # satisfait par le seul fait de combiner plusieurs nuages.
            plate = combiner_plusieurs(nuage, np.full(len(jeu), 1.0 / len(jeu)))
            e_aj = float(np.median(distance_a(ajuste, cible, voxel_um)))
            e_pl = float(np.median(distance_a(plate, cible, voxel_um)))
            seules = [float(np.median(distance_a(marches[r], cible, voxel_um))) for r in jeu]
            lignes.append(dict(
                cible=m, ancres=list(jeu), bras=list(bras), signature=signature(bras),
                k=len(jeu), encadre=bool(min(bras) < 0 < max(bras)),
                somme_des_bras=int(sum(abs(b) for b in bras)),
                erreur_ajustee_um=round(e_aj, 1),
                erreur_courbe_um=(round(float(np.median(
                    distance_a(courbe, cible, voxel_um))), 1) if courbe is not None else None),
                erreur_moyenne_plate_um=round(e_pl, 1),
                erreur_de_la_meilleure_ancre_um=round(min(seules), 1),
                erreur_de_la_plus_proche_um=round(
                    seules[int(np.argmin([abs(b) for b in bras]))], 1),
                ecart_signe_um=round(ecart_signe(ajuste, cible, axe, voxel_um), 1),
                bits_de_supervision=len(jeu),
                poids=[round(float(x), 3) for x in w]))

    if not lignes:
        raise RuntimeError("aucun jeu d'ancres mesurable dans la boîte")

    def med(sous, cle):
        return round(float(np.median([e[cle] for e in sous])), 1) if sous else None

    r = dict(
        fragment="PHerc0500P2", volume=volume, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        ecart_lu_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        portee=portee, kmax=kmax, jeux=len(lignes), cibles=len(set(e["cible"] for e in lignes)),
        lignes=lignes)

    # ⚠⚠⚠ LA COURBE QUI DÉCIDE : l'erreur par NOMBRE d'ancres. Une ancre coûte une spire tracée,
    # donc ce qu'on veut savoir n'est pas « plus, c'est mieux » mais à partir de combien la
    # suivante ne paie plus.
    par_k = {}
    for e in lignes:
        par_k.setdefault(e["k"], []).append(e)
    r["par_nombre_dancres"] = {
        str(k): dict(n=len(v), ajustee_um=med(v, "erreur_ajustee_um"),
                     courbe_um=(med([e for e in v if e["erreur_courbe_um"] is not None],
                                    "erreur_courbe_um") if k >= 3 else None),
                     moyenne_plate_um=med(v, "erreur_moyenne_plate_um"),
                     meilleure_ancre_um=med(v, "erreur_de_la_meilleure_ancre_um"),
                     plus_proche_um=med(v, "erreur_de_la_plus_proche_um"),
                     encadres=sum(1 for e in v if e["encadre"]))
        for k, v in sorted(par_k.items())}
    # ⚠⚠ LES JEUX QUI ENCADRENT ET CEUX QUI N'ENCADRENT PAS SONT SÉPARÉS, parce qu'ils ne font
    # pas la même chose : un jeu tout d'un côté EXTRAPOLE, et une extrapolation qui se trompe de
    # pente s'éloigne au lieu de s'approcher. Les mélanger ferait dire à la courbe une moyenne
    # de deux régimes.
    r["par_nombre_dancres_encadrants"] = {
        str(k): dict(n=sum(1 for e in v if e["encadre"]),
                     ajustee_um=med([e for e in v if e["encadre"]], "erreur_ajustee_um"),
                     moyenne_plate_um=med([e for e in v if e["encadre"]],
                                          "erreur_moyenne_plate_um"))
        for k, v in sorted(par_k.items())}
    r["par_nombre_dancres_dun_seul_cote"] = {
        str(k): dict(n=sum(1 for e in v if not e["encadre"]),
                     ajustee_um=med([e for e in v if not e["encadre"]], "erreur_ajustee_um"),
                     moyenne_plate_um=med([e for e in v if not e["encadre"]],
                                          "erreur_moyenne_plate_um"))
        for k, v in sorted(par_k.items())}
    # ⚠⚠ ET LE JEU LUI-MÊME, par sa signature de bras : c'est là que se lit « où poser la
    # troisième ». Un jeu est nommé par ses bras signés, donc (-1,+1,+2) et (-2,-1,+1) sont deux
    # réponses différentes à la même question et ne sont pas moyennés ensemble.
    par_sig = {}
    for e in lignes:
        par_sig.setdefault(e["signature"], []).append(e)
    r["par_jeu_dancres"] = {
        sig: dict(k=v[0]["k"], n=len(v), encadre=v[0]["encadre"],
                  somme_des_bras=v[0]["somme_des_bras"],
                  ajustee_um=med(v, "erreur_ajustee_um"),
                  meilleure_ancre_um=med(v, "erreur_de_la_meilleure_ancre_um"))
        for sig, v in sorted(par_sig.items(), key=lambda kv: (kv[1][0]["k"], kv[0]))}

    # ⚠⚠⚠ LA PRÉMISSE DE L'ESTIMATEUR, VÉRIFIÉE SUR LE CORPUS PLUTÔT QU'ASSUMÉE. L'ajustement
    # n'annule une erreur que si elle croît LINÉAIREMENT avec le bras. Les jeux d'une seule
    # ancre le disent directement : leur erreur, rangée par longueur de bras, doit monter — et
    # monter par pas à peu près constants. Si elle ne montait pas, l'estimateur corrigerait une
    # pente qui n'existe pas.
    par_bras = {}
    for e in lignes:
        if e["k"] == 1:
            par_bras.setdefault(abs(e["bras"][0]), []).append(e)
    r["erreur_dune_ancre_par_bras_um"] = {
        str(b): dict(n=len(v), erreur_um=med(v, "erreur_ajustee_um"))
        for b, v in sorted(par_bras.items())}
    suite = [d["erreur_um"] for d in r["erreur_dune_ancre_par_bras_um"].values()]
    r["lerreur_dune_ancre_croit_avec_son_bras"] = bool(
        len(suite) > 1 and all(x is not None for x in suite)
        and all(b > a_ for a_, b in zip(suite, suite[1:])))
    # ⚠ Les incréments partent du bras ZÉRO, dont l'erreur est nulle par définition : c'est le
    # plus grand de tous, et l'omettre faisait lire une accélération là où il y a surtout un
    # premier pas cher.
    r["increments_par_tour_um"] = ([round(b - a_, 1) for a_, b in zip([0.0] + suite, suite)]
                                   if all(x is not None for x in suite) else [])
    # ⚠⚠⚠ LE CRITÈRE EST CELUI DE `pourquoi_la_derive_accelere`, ET IL EN REMPLACE UN AUTRE,
    # RETIRÉ. Le précédent — « les incréments consécutifs croissent » — omettait l'incrément du
    # bras zéro, le plus grand de tous, et basculait sur deux micromètres. Celui-ci est sans
    # seuil : l'erreur au bras `k` reste-t-elle sous `k` fois celle du bras un ?
    r["cout_par_tour_um"] = [round(x / (i + 1), 1) for i, x in enumerate(suite)
                             ] if all(x is not None for x in suite) else []
    r["la_derive_dune_ancre_est_sous_lineaire"] = sous_lineaire(suite)
    r["le_premier_pas_coute_le_plus"] = bool(
        r["cout_par_tour_um"] and all(r["cout_par_tour_um"][0] > x
                                      for x in r["cout_par_tour_um"][1:]))

    ks = sorted(par_k)
    aj = {k: r["par_nombre_dancres"][str(k)]["ajustee_um"] for k in ks}
    # ⚠⚠⚠ LA COURBE QUI DÉCIDE EST CELLE DES JEUX QUI ENCADRENT, PAS L'AGRÉGÉE, et c'est une
    # correction d'un chiffre que j'avais d'abord publié sur la population mélangée. La part de
    # jeux encadrants CHANGE avec `k` — 30 sur 58 à deux ancres, 45 sur 53 à trois, 28 sur 28 à
    # quatre —, donc la courbe agrégée mélange deux régimes et son affaissement mesure d'abord
    # ce changement de composition. Les deux sont publiées, la seconde est celle qui tranche.
    enc = {k: r["par_nombre_dancres_encadrants"][str(k)]["ajustee_um"] for k in ks}
    r["lerreur_baisse_de_une_a_deux"] = bool(
        len(ks) > 1 and aj[ks[1]] is not None and aj[ks[0]] is not None
        and aj[ks[1]] < aj[ks[0]])
    r["lerreur_baisse_encore_de_deux_a_trois"] = bool(
        len(ks) > 2 and aj[ks[2]] is not None and aj[ks[1]] is not None
        and aj[ks[2]] < aj[ks[1]])

    def sature(courbe):
        return next((k for k, kp in zip(ks[1:], ks)
                     if courbe.get(k) is None or courbe.get(kp) is None
                     or courbe[k] >= courbe[kp]), None)

    r["ancres_avant_que_le_gain_cesse"] = sature(aj)
    r["ancres_avant_que_le_gain_cesse_en_encadrant"] = sature(enc)
    r["gain_de_la_deuxieme_ancre"] = (
        round(aj[ks[0]] - aj[ks[1]], 1) if len(ks) > 1 and None not in (aj[ks[0]], aj[ks[1]])
        else None)
    r["gain_de_la_troisieme_ancre"] = (
        round(aj[ks[1]] - aj[ks[2]], 1) if len(ks) > 2 and None not in (aj[ks[1]], aj[ks[2]])
        else None)
    r["gain_de_la_troisieme_ancre_en_encadrant"] = (
        round(enc[ks[1]] - enc[ks[2]], 1)
        if len(ks) > 2 and None not in (enc.get(ks[1]), enc.get(ks[2])) else None)
    r["gain_de_la_quatrieme_ancre_en_encadrant"] = (
        round(enc[ks[2]] - enc[ks[3]], 1)
        if len(ks) > 3 and None not in (enc.get(ks[2]), enc.get(ks[3])) else None)
    # ⚠⚠ L'AJUSTEMENT DOIT BATTRE LA MOYENNE PLATE, jeu par jeu et pas seulement en médiane :
    # battre une médiane est facile et ne dit pas que l'estimateur est meilleur là où il compte.
    r["jeux_ou_lajustement_bat_la_moyenne_plate"] = sum(
        1 for e in lignes if e["erreur_ajustee_um"] < e["erreur_moyenne_plate_um"])
    r["lajustement_bat_la_moyenne_plate"] = bool(
        r["jeux_ou_lajustement_bat_la_moyenne_plate"] > len(lignes) / 2)
    # ⚠⚠ LE COMPTE PAR JEU EST SÉPARÉ LUI AUSSI. En médiane l'ajustement gagne partout, mais
    # jeu par jeu il ne gagne qu'un peu plus d'une fois sur deux : il gagne GROS quand il gagne
    # et perd PETIT quand il perd. Un seul compte agrégé laisserait croire à un ex æquo.
    for nom, sous in (("encadrants", [e for e in lignes if e["encadre"]]),
                      ("dun_seul_cote", [e for e in lignes if not e["encadre"]])):
        r[f"jeux_{nom}_ou_lajustement_bat_la_moyenne_plate"] = sum(
            1 for e in sous if e["erreur_ajustee_um"] < e["erreur_moyenne_plate_um"])
        r[f"jeux_{nom}"] = len(sous)
    # ⚠⚠ ET IL DOIT BATTRE « LA MEILLEURE ANCRE SEULE », qui demande la réponse pour être
    # choisie : battre la plus proche ne suffirait pas, on la connaît sans regarder la cible.
    r["jeux_ou_lajustement_bat_la_meilleure_ancre"] = sum(
        1 for e in lignes if e["erreur_ajustee_um"] < e["erreur_de_la_meilleure_ancre_um"])
    r["jeux_ou_lajustement_bat_la_plus_proche"] = sum(
        1 for e in lignes if e["erreur_ajustee_um"] < e["erreur_de_la_plus_proche_um"])
    # ⚠⚠⚠ LE CHIFFRE QUI DÉCIDE DE L'EFFORT : jusqu'où peut-on ESPACER deux ancres et tenir
    # encore la feuille ? Les encadrements symétriques répondent seuls, parce qu'à bras égaux le
    # poids vaut un demi et rien ne dépend du réglage : ce qui reste est la distance.
    sym = {}
    for e in lignes:
        if e["k"] == 2 and e["encadre"] and e["bras"][0] == -e["bras"][1]:
            sym.setdefault(abs(e["bras"][0]), []).append(e)
    r["encadrements_symetriques_par_bras"] = {
        str(b): dict(n=len(v), ajustee_um=med(v, "erreur_ajustee_um"),
                     tient_la_feuille=bool(med(v, "erreur_ajustee_um") < ecart_um / 2))
        for b, v in sorted(sym.items())}
    # ⚠⚠ ET LE PLUS GRAND BRAS QUI TIENT ENCORE, avec son compte de cas ATTACHÉ. Sans le compte,
    # « il tient jusqu'à trois » se lirait comme un résultat alors qu'un seul cas ne tranche
    # rien — ce dépôt a déjà vu un verdict s'inverser quand l'échantillon a grandi.
    # ⚠⚠ LE RÉSIDU DE L'ENCADREMENT SUIT LA MÊME FORME : sous la droite de son premier pas, et
    # à coût par tour à peu près stable. L'encadrement divise ce coût par deux — 30,0 puis 17,0
    # / 14,9 / 16,0 µm par tour contre 41,1 puis 31,6 / 33,6 / 37,4 pour une ancre seule — ce
    # qui est exactement ce qu'annuler une pente linéaire doit donner.
    suite_sym = [d["ajustee_um"] for d in r["encadrements_symetriques_par_bras"].values()]
    r["increments_de_lencadrement_symetrique_um"] = (
        [round(b - a_, 1) for a_, b in zip([0.0] + suite_sym, suite_sym)]
        if all(x is not None for x in suite_sym) else [])
    r["cout_par_tour_de_lencadrement_um"] = (
        [round(x / (i + 1), 1) for i, x in enumerate(suite_sym)]
        if all(x is not None for x in suite_sym) else [])
    r["le_residu_de_lencadrement_est_sous_lineaire"] = sous_lineaire(suite_sym)
    tenus = [(int(b), d) for b, d in r["encadrements_symetriques_par_bras"].items()
             if d["tient_la_feuille"]]
    r["plus_grand_bras_symetrique_qui_tient"] = max(tenus)[0] if tenus else None
    r["cas_a_ce_bras"] = max(tenus)[1]["n"] if tenus else 0
    # ⚠⚠⚠ LE DEGRÉ DEUX PAIE-T-IL ? C'est la seule piste que le résultat précédent laissait
    # ouverte : si la troisième ancre ne sert pas à moyenner, sert-elle à identifier la
    # courbure ? La comparaison se fait sur les MÊMES jeux — ceux d'au moins trois ancres —,
    # sinon on comparerait deux populations.
    trois = [e for e in lignes if e["erreur_courbe_um"] is not None and e["encadre"]]
    r["jeux_a_trois_ancres_ou_plus_qui_encadrent"] = len(trois)
    r["erreur_courbe_mediane_um"] = med(trois, "erreur_courbe_um")
    r["erreur_droite_sur_les_memes_jeux_um"] = med(trois, "erreur_ajustee_um")
    r["la_courbure_paie"] = bool(
        r["erreur_courbe_mediane_um"] is not None
        and r["erreur_courbe_mediane_um"] < r["erreur_droite_sur_les_memes_jeux_um"])
    r["jeux_ou_la_courbure_bat_la_droite"] = sum(
        1 for e in trois if e["erreur_courbe_um"] < e["erreur_ajustee_um"])
    r["sous_la_demi_feuille"] = {
        k: bool(v["ajustee_um"] is not None and v["ajustee_um"] < ecart_um / 2)
        for k, v in r["par_nombre_dancres"].items()}
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- les poids : l'identité qui relie cette tranche à la précédente ---
    from derouler_des_deux_bords import poids_par_les_bras  # noqa: PLC0415

    v("une ancre seule pèse un", np.allclose(poids_de_lajustement(np.array([-2.0])), [1.0]),
      str(poids_de_lajustement(np.array([-2.0]))))
    v("les poids somment toujours à un",
      all(abs(poids_de_lajustement(np.array(s, dtype=float)).sum() - 1.0) < 1e-12
          for s in ([-1, 1], [-2, 1], [-3, -1, 2], [-1, 1, 2, 3])))
    # ⚠⚠⚠ L'IDENTITÉ QUI COMPTE : à deux ancres, la droite des moindres carrés en zéro EST la
    # pondération par les bras déjà mesurée. Ce n'est pas une ressemblance de forme, c'est une
    # égalité algébrique — et si elle tombait, la généralisation ne contiendrait plus le
    # résultat qu'elle prétend étendre.
    for a_, b_ in ((1, 1), (1, 2), (1, 3), (2, 3), (3, 1), (4, 1)):
        w = poids_de_lajustement(np.array([-float(a_), float(b_)]))
        attendu = poids_par_les_bras(a_, b_)
        v(f"à deux ancres ({-a_:+d},{b_:+d}) l'ajustement rend la pondération par les bras",
          abs(w[0] - attendu) < 1e-12, f"{w[0]:.6f} contre {attendu:.6f}")
    # ⚠ Et le sens : la branche au bras COURT pèse le plus. Une pondération inversée aurait la
    # même somme et le même nombre de poids.
    w = poids_de_lajustement(np.array([-1.0, 3.0]))
    v("... et le bras court pèse plus que le bras long", w[0] > w[1], str(w))
    v("à bras égaux et opposés, le milieu exact",
      np.allclose(poids_de_lajustement(np.array([-2.0, 2.0])), [0.5, 0.5]))
    # ⚠⚠ LE CAS DÉGÉNÉRÉ, dit plutôt que caché : avec tous les bras ÉGAUX il n'y a pas de pente
    # à estimer, donc la moyenne simple. Rendre autre chose serait inventer une correction dont
    # rien ne dit le sens.
    v("des bras tous égaux rendent la moyenne simple",
      np.allclose(poids_de_lajustement(np.array([2.0, 2.0, 2.0])), [1 / 3, 1 / 3, 1 / 3]))
    # ⚠⚠⚠ LA PROPRIÉTÉ QUE L'ESTIMATEUR REVENDIQUE : si l'erreur est exactement linéaire en
    # bras, l'ajustement la fait disparaître. Vérifié sur des nombres, pas argumenté.
    for s in ([-1.0, 2.0], [-2.0, -1.0, 3.0], [-3.0, -1.0, 1.0, 2.0]):
        s_ = np.array(s)
        p = 7.0 + 1.3 * s_
        v(f"une erreur linéaire en bras est annulée ({len(s)} ancres)",
          abs(float(poids_de_lajustement(s_) @ p) - 7.0) < 1e-9,
          f"{float(poids_de_lajustement(s_) @ p):.9f}")
    # ⚠⚠ ET LE NÉGATIF : un jeu tout d'un même côté EXTRAPOLE, donc au moins un poids est
    # négatif. C'est ce qui rend l'extrapolation dangereuse, et le fait est publié plutôt que
    # lissé — un poids négatif amplifie l'écart au lieu de l'amortir.
    v("un jeu d'un seul côté extrapole, donc porte un poids négatif",
      poids_de_lajustement(np.array([-3.0, -1.0])).min() < 0,
      str(poids_de_lajustement(np.array([-3.0, -1.0]))))
    v("... alors qu'un jeu qui encadre n'en porte aucun",
      poids_de_lajustement(np.array([-1.0, 2.0])).min() > 0,
      str(poids_de_lajustement(np.array([-1.0, 2.0]))))

    # ⚠⚠⚠ LE DEGRÉ DEUX, ET SA CONDITION D'IDENTIFIABILITÉ. Une parabole annule aussi la
    # courbure — mais il faut TROIS bras distincts pour la déterminer. Avec moins, une
    # pseudo-inverse rend quand même des poids, tirés d'un système sous-déterminé, et
    # l'estimateur aurait l'air de marcher en n'ayant rien identifié.
    for s_ in ([-2.0, -1.0, 3.0], [-3.0, -1.0, 1.0, 2.0]):
        arr = np.array(s_)
        p2 = 7.0 + 1.3 * arr - 0.4 * arr ** 2
        v(f"une erreur QUADRATIQUE en bras est annulée au degré deux ({len(s_)} ancres)",
          abs(float(poids_de_lajustement(arr, degre=2) @ p2) - 7.0) < 1e-8,
          f"{float(poids_de_lajustement(arr, degre=2) @ p2):.9f}")
    v("... et la droite, elle, ne l'annule PAS",
      abs(float(poids_de_lajustement(np.array([-2.0, -1.0, 3.0])) @ (
          7.0 + 1.3 * np.array([-2.0, -1.0, 3.0])
          - 0.4 * np.array([-2.0, -1.0, 3.0]) ** 2)) - 7.0) > 0.5)
    v("un degré deux sur deux ancres seulement est REFUSÉ, pas ajusté de force",
      np.allclose(poids_de_lajustement(np.array([-1.0, 2.0]), degre=2), [0.5, 0.5]),
      str(poids_de_lajustement(np.array([-1.0, 2.0]), degre=2)))
    v("... et des bras répétés ne comptent pas comme des bras distincts",
      np.allclose(poids_de_lajustement(np.array([-1.0, -1.0, 2.0]), degre=2),
                  [1 / 3, 1 / 3, 1 / 3]))
    v("le degré deux somme lui aussi à un",
      abs(poids_de_lajustement(np.array([-2.0, -1.0, 3.0]), degre=2).sum() - 1.0) < 1e-12)

    # --- l'énumération des jeux ---
    v("un jeu ne contient jamais la cible",
      all(5 not in j for j in jeux_dancres([3, 4, 5, 6, 7], 5, 2, 3)))
    v("... et rien au-delà de la portée",
      all(all(abs(r - 5) <= 2 for r in j) for j in jeux_dancres([1, 3, 4, 5, 6, 9], 5, 2, 3)))
    v("le compte des jeux est celui des combinaisons",
      len(jeux_dancres([3, 4, 6, 7], 5, 2, 2)) == 4 + 6,
      str(len(jeux_dancres([3, 4, 6, 7], 5, 2, 2))))
    v("une signature nomme les bras signés, triés",
      signature((2, -1, -3)) == "-3,-1,+2", signature((2, -1, -3)))

    # --- la combinaison de plusieurs nuages ---
    un = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    deux = np.array([[0.0, 2.0, 0.0], [1.0, 2.0, 0.0]])
    mid = combiner_plusieurs([un, deux], np.array([0.5, 0.5]))
    v("deux nuages à parts égales rendent leur milieu",
      np.allclose(mid[:, 1], 1.0), str(mid[:, 1]))
    v("... et un poids de un sur le premier le rend inchangé",
      np.allclose(combiner_plusieurs([un, deux], np.array([1.0, 0.0])), un))
    v("le résultat a la taille du nuage de référence",
      combiner_plusieurs([un, deux, deux], np.array([0.5, 0.25, 0.25])).shape == un.shape)
    v("un nuage vide ne rend rien plutôt qu'une erreur",
      combiner_plusieurs([un, np.zeros((0, 3))], np.array([0.5, 0.5])).shape[0] == 0)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE. Sans ça, le seul chemin non testé
    # du module serait celui qui produit son résultat — le défaut mesuré dans `80`.
    # ⚠⚠ LA PRÉMISSE VÉRIFIÉE SUR DES NOMBRES : l'erreur d'une ancre doit croître avec son bras,
    # sinon l'estimateur corrige une pente qui n'existe pas. Le contrôle porte sur la fixture
    # ici et sur le corpus dans la mesure publiée : les deux exercent le même chemin.
    fab = mesurer(minimum=30, portee=2, kmax=3, corpus=corpus_fabrique())
    v("la mesure tourne de bout en bout sur un corpus fabriqué, sans rien lire",
      fab["jeux"] > 0 and fab["cibles"] > 0,
      f"{fab['jeux']} jeux sur {fab['cibles']} cibles")
    v("... et la marche y est imparfaite, donc les comparaisons portent sur quelque chose",
      all(e["erreur_ajustee_um"] > 0 for e in fab["lignes"]),
      str(fab["par_nombre_dancres"]["1"]["ajustee_um"]))
    v("... chaque jeu déclare autant de bits de supervision que d'ancres",
      all(e["bits_de_supervision"] == e["k"] == len(e["ancres"]) for e in fab["lignes"]))
    v("... et un jeu d'une seule ancre rend exactement cette ancre",
      all(abs(e["erreur_ajustee_um"] - e["erreur_de_la_plus_proche_um"]) < 0.05
          for e in fab["lignes"] if e["k"] == 1),
      str([e["erreur_ajustee_um"] for e in fab["lignes"] if e["k"] == 1][:4]))
    v("... les jeux qui encadrent et ceux d'un seul côté sont comptés à part",
      all(fab["par_nombre_dancres_encadrants"][k]["n"]
          + fab["par_nombre_dancres_dun_seul_cote"][k]["n"]
          == fab["par_nombre_dancres"][k]["n"] for k in fab["par_nombre_dancres"]))
    v("... et les jeux d'une ancre n'encadrent jamais",
      fab["par_nombre_dancres_encadrants"]["1"]["n"] == 0)
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "la suivante ne paie plus" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    hors = None
    try:
        mesurer(minimum=30, portee=2, kmax=3, corpus=corpus_fabrique(decalage_vx=5000.0))
    except RuntimeError as exc:
        hors = str(exc)
    v("un corpus posé hors de la boîte est REFUSÉ, pas rendu vide", hors is not None, str(hors))

    v("... l'erreur d'une ancre croît avec la longueur de son bras",
      fab["lerreur_dune_ancre_croit_avec_son_bras"],
      str(fab["erreur_dune_ancre_par_bras_um"]))
    # ⚠⚠⚠ ET LA CORRECTION QUE LA MESURE M'A IMPOSÉE : la part de jeux ENCADRANTS change avec le
    # nombre d'ancres, donc la courbe agrégée mélange deux régimes et son affaissement mesure
    # d'abord ce changement de composition. Les deux saturations sont publiées, et ce contrôle
    # exige qu'elles soient calculées séparément — les confondre est le défaut qui a été corrigé.
    v("... la saturation est calculée sur les encadrants ET sur la population mélangée",
      "ancres_avant_que_le_gain_cesse_en_encadrant" in fab
      and "ancres_avant_que_le_gain_cesse" in fab)
    v("... et la part d'encadrants change bien avec le nombre d'ancres, donc les deux diffèrent",
      len({fab["par_nombre_dancres_encadrants"][k]["n"] / fab["par_nombre_dancres"][k]["n"]
           for k in fab["par_nombre_dancres"]}) > 1,
      str({k: fab["par_nombre_dancres_encadrants"][k]["n"] for k in fab["par_nombre_dancres"]}))

    # ⚠⚠ LA SUR-LINÉARITÉ EST UN FAIT DU CORPUS, PAS DE LA FIXTURE : la fixture a des feuilles
    # trop régulières pour la porter, donc ce contrôle vérifie que le CALCUL est fait et rendu,
    # et le fait lui-même est vérifié par la figure sur la mesure publiée. Prétendre le
    # contraire ferait dire à une fixture ce que seul le corpus peut dire.
    v("... les jeux d'au moins trois ancres portent une estimation de la courbure",
      all((e["erreur_courbe_um"] is not None) == (e["k"] >= 3) for e in fab["lignes"]),
      str(sum(1 for e in fab["lignes"] if e["erreur_courbe_um"] is not None)))
    v("... et la courbure est comparée à la droite sur LES MÊMES jeux",
      fab["erreur_courbe_mediane_um"] is None
      or fab["jeux_a_trois_ancres_ou_plus_qui_encadrent"] > 0,
      f"{fab['jeux_a_trois_ancres_ou_plus_qui_encadrent']} jeux")
    v("la forme de la courbe est calculée et rendue, quel que soit son signe",
      isinstance(fab["la_derive_dune_ancre_est_sous_lineaire"], bool)
      and isinstance(fab["le_residu_de_lencadrement_est_sous_lineaire"], bool),
      f"dérive {fab['cout_par_tour_um']} · encadrement "
      f"{fab['cout_par_tour_de_lencadrement_um']}")
    # ⚠⚠⚠ LE CRITÈRE VIENT DE `pourquoi_la_derive_accelere`, IL N'EST PAS RECOPIÉ : deux
    # implémentations d'une même règle finiraient par rendre deux verdicts, ce qui est
    # exactement ce que le critère précédent a fait sur deux populations.
    v("le critère dit OUI d'une suite sous la droite du premier pas, NON d'une qui la dépasse",
      sous_lineaire([41.1, 63.1, 100.8, 149.4]) and not sous_lineaire([10.0, 25.0, 40.0]))
    # ⚠ Et l'incrément du bras zéro n'est jamais omis : c'est lui qui a fait lire une
    # accélération là où il y a surtout un premier pas cher.
    v("... et le premier incrément, celui du bras zéro, est compté",
      len(fab["increments_par_tour_um"]) == len(fab["erreur_dune_ancre_par_bras_um"]),
      str(fab["increments_par_tour_um"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure.

    ⚠⚠ Sorti de `main` pour la raison mesurée dans `80` : un bloc de `main` ne peut être exercé
    qu'en lisant le dépôt distant, donc jamais par la batterie.
    """
    print(f"écart inter-feuilles {r['ecart_lu_um']} µm · demi-épaisseur "
          f"{r['demi_epaisseur_um']} µm · {r['jeux']} jeux d'ancres sur {r['cibles']} cibles "
          f"(portée {r['portee']}, jusqu'à {r['kmax']} ancres)\n")
    print(f"{'ancres':>7} {'jeux':>6} {'AJUSTÉ':>9} {'moy. plate':>11} {'meilleure':>10} "
          f"{'plus proche':>12} {'encadrants':>11}")
    print("-" * 72)
    for k, d in r["par_nombre_dancres"].items():
        print(f"{k:>7} {d['n']:>6} {d['ajustee_um']:>8.1f}µ {d['moyenne_plate_um']:>10.1f}µ "
              f"{d['meilleure_ancre_um']:>9.1f}µ {d['plus_proche_um']:>11.1f}µ "
              f"{d['encadres']:>11}")
    print("\nen ne gardant que les jeux qui ENCADRENT (les autres extrapolent) :")
    for k, d in r["par_nombre_dancres_encadrants"].items():
        if d["n"]:
            print(f"{k:>7} {d['n']:>6} {d['ajustee_um']:>8.1f}µ {d['moyenne_plate_um']:>10.1f}µ")
    print("\nd'un seul côté :")
    for k, d in r["par_nombre_dancres_dun_seul_cote"].items():
        if d["n"]:
            print(f"{k:>7} {d['n']:>6} {d['ajustee_um']:>8.1f}µ {d['moyenne_plate_um']:>10.1f}µ")
    print("\npar jeu de bras (où poser la suivante) :")
    for sig, d in r["par_jeu_dancres"].items():
        marque = "" if d["encadre"] else "  (extrapole)"
        print(f"  {sig:>14} · {d['n']:>2} cas · ajusté {d['ajustee_um']:>6.1f} µm · "
              f"meilleure ancre {d['meilleure_ancre_um']:>6.1f} µm{marque}")
    print(f"\nle degré DEUX, sur les {r['jeux_a_trois_ancres_ou_plus_qui_encadrent']} jeux "
          f"d'au moins trois ancres qui encadrent : {r['erreur_courbe_mediane_um']} µm contre "
          f"{r['erreur_droite_sur_les_memes_jeux_um']} pour la droite, et il gagne sur "
          f"{r['jeux_ou_la_courbure_bat_la_droite']} jeux")
    print(f"→ la courbure paie : {'OUI' if r['la_courbure_paie'] else 'NON'}")
    print(f"\nl'ajustement bat la moyenne plate sur "
          f"{r['jeux_ou_lajustement_bat_la_moyenne_plate']} jeux sur {r['jeux']} : "
          f"{'OUI' if r['lajustement_bat_la_moyenne_plate'] else 'NON'}")
    print(f"il bat « la meilleure ancre seule » (qui demande la réponse) sur "
          f"{r['jeux_ou_lajustement_bat_la_meilleure_ancre']} jeux, et « la plus proche » "
          f"(qui ne la demande pas) sur {r['jeux_ou_lajustement_bat_la_plus_proche']}")
    print("\nl'erreur d'UNE ancre, par longueur de bras — la prémisse de l'estimateur :")
    for b, d in r["erreur_dune_ancre_par_bras_um"].items():
        print(f"  bras {b} · {d['n']:>2} cas · {d['erreur_um']:>6.1f} µm")
    print(f"  → elle croît avec le bras : "
          f"{'OUI' if r['lerreur_dune_ancre_croit_avec_son_bras'] else 'NON'} · "
          f"incréments depuis le bras zéro {r['increments_par_tour_um']} µm · "
          f"coût par tour {r['cout_par_tour_um']} µm")
    print(f"  → SOUS-linéaire (sous k fois le premier pas) : "
          f"{'OUI' if r['la_derive_dune_ancre_est_sous_lineaire'] else 'NON'} · "
          f"le premier pas coûte le plus : "
          f"{'OUI' if r['le_premier_pas_coute_le_plus'] else 'NON'}")
    print(f"\ngain de la deuxième ancre : {r['gain_de_la_deuxieme_ancre']} µm · "
          f"de la troisième : {r['gain_de_la_troisieme_ancre']} µm")
    print(f"en ne gardant que les jeux qui ENCADRENT — la seule population comparable, "
          f"la part d'encadrants changeant avec le nombre d'ancres :")
    print(f"  troisième ancre {r['gain_de_la_troisieme_ancre_en_encadrant']} µm · "
          f"quatrième {r['gain_de_la_quatrieme_ancre_en_encadrant']} µm")
    print(f"→ à partir de {r['ancres_avant_que_le_gain_cesse_en_encadrant']} ancres qui "
          f"encadrent, la suivante ne paie plus "
          f"(sur la population mélangée : {r['ancres_avant_que_le_gain_cesse']})")
    print("\njusqu'où espacer deux ancres — les encadrements SYMÉTRIQUES, où le poids vaut un "
          "demi et où seule la distance parle :")
    for b, d in r["encadrements_symetriques_par_bras"].items():
        print(f"  bras ±{b} · {d['n']:>2} cas · {d['ajustee_um']:>6.1f} µm · "
              f"{'tient la feuille' if d['tient_la_feuille'] else 'a PERDU la feuille'}")
    print(f"  incréments de l'encadrement : {r['increments_de_lencadrement_symetrique_um']} µm · "
          f"coût par tour {r['cout_par_tour_de_lencadrement_um']} µm · SOUS-linéaire : "
          f"{'OUI' if r['le_residu_de_lencadrement_est_sous_lineaire'] else 'NON'}")
    print(f"→ deux ancres à ±{r['plus_grand_bras_symetrique_qui_tient']} tours tiennent encore "
          f"la feuille, sur {r['cas_a_ce_bras']} cas")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--portee", type=int, default=3)
    p.add_argument("--kmax", type=int, default=4)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote, portee=a.portee, kmax=a.kmax)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
