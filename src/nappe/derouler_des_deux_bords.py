#!/usr/bin/env python3
"""Deux ancres valent-elles mieux qu'une ? — encadrer une spire par les deux côtés.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Cinq soupçons ont été testés et écartés sur la mécanique du pas —
la fenêtre, les décalages, le gabarit, les normales, la longueur — et tous portaient sur **la même
marche** : une qui part d'une seule spire et n'a que sa propre reconstruction pour se juger. Ce
fichier change la structure du problème plutôt qu'un réglage : la spire `m` est reconstruite depuis
`m − j` **et** depuis `m + j`, donc par les deux côtés.

⭐⭐ ET LÀ, POUR LA PREMIÈRE FOIS, DEUX RECONSTRUCTIONS SE RENCONTRENT. Des spires concentriques ne
se croisent jamais, donc « plusieurs départs » ne veut rien dire tant qu'on marche tous dans le même
sens ; encadrer, si. Leur **désaccord** est alors une mesure de confiance qui ne demande **aucune
cible** — c'est la seule de tout le chantier, et elle se valide en la confrontant à l'erreur vraie.

⚠⚠ CE QUE ÇA MESURE ET CE QUE ÇA NE MESURE PAS. Un vrai dérouleur n'a qu'une ancre : encadrer
suppose de connaître les deux bouts. Ce n'est donc pas une méthode, c'est une **borne** — elle dit
ce qu'on gagnerait si l'on avait deux ancres au lieu d'une, donc si l'effort doit aller vers une
meilleure propagation ou vers **plus d'ancres**. Le corpus en publie treize.

⚠⚠ LA COMBINAISON DOIT BATTRE LES DEUX BRANCHES, pas la plus mauvaise. Battre la plus mauvaise est
gratuit : « prendre la meilleure des deux » y suffirait, et savoir laquelle est la meilleure demande
la réponse. C'est le verdict rendu.

⚠ Les triplets sont **symétriques** (`m − j`, `m`, `m + j`) : deux branches qui marchent un nombre
de tours différent ne se comparent pas, et leur combinaison mesurerait surtout laquelle a le moins
marché.

⚠ Aucune lecture du volume ici : le pas aveugle est le meilleur dérouleur mesuré, et il ne lit rien.
Cette tranche ne coûte donc pas un bloc.

⚠⚠ LA MATIÈRE EST INJECTABLE, ET C'EST CE QUI REND LA MESURE TESTABLE. `mesurer` prend un `corpus`
dont le défaut est le dépôt distant — donc le nombre publié ne bouge pas — et la batterie lui en
donne un fabriqué. Sans ce paramètre, le seul chemin non testé du module était celui qui produit
le nombre publié, ce qui a laissé passer un patch à moitié appliqué le 2026-09-05. Voir `80`.

Usage :
    uv run python src/nappe/derouler_des_deux_bords.py --verifier
    uv run python src/nappe/derouler_des_deux_bords.py \\
        --json docs/mesures/derouler_des_deux_bords.json
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
# ⚠ La lecture du corpus et sa fixture vivent dans UN seul fichier, partagé par tous les
# dérouleurs : cinq copies de la même boucle finiraient par ne pas lire la même matière, et
# l'écart entre deux dérouleurs mesurerait leur désaccord de lecture.
from le_corpus_des_spires import corpus_fabrique, corpus_publie  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def marcher(a: np.ndarray, ok: np.ndarray, tours: int, pas_vx: float,
            sens: float) -> tuple[np.ndarray, np.ndarray]:
    """La grille avancée de `tours` pas aveugles le long de ses propres normales.

    ⚠ C'est exactement le pas du dérouleur publié — `un_pas` y est importé, pas recopié : deux
    implémentations d'un même geste finiraient par ne pas s'accorder, et la comparaison des deux
    branches porterait sur leur désaccord d'implémentation.
    """
    from derouler_par_le_pas_normal import un_pas  # noqa: PLC0415

    for _ in range(tours):
        a, ok = un_pas(a, ok, pas_vx, sens)
        if not ok.any():
            break
    return a, ok


def poids_par_les_bras(bras_gauche: int, bras_droit: int) -> float:
    """Le poids de la branche GAUCHE, dérivé des deux longueurs de bras.

    ⚠⚠⚠ IL N'Y A PAS DE PARAMÈTRE LIBRE ICI, ET C'EST LE POINT. Le désaccord entre branches est
    **symétrique** — c'est le même nombre pour les deux — donc il ne peut pas dire laquelle
    croire. Ce qui les distingue sans regarder la réponse est la **longueur de leur bras**, et la
    mesure a établi que l'erreur croît avec elle. Si elle croît linéairement, l'estimateur qui
    annule les deux erreurs de signes opposés est l'interpolation linéaire entre les deux ancres :
    la branche au bras COURT pèse `bras_long / (somme)`. Aucun réglage, aucune constante.

    ⚠⚠ ET ELLE DÉGÉNÈRE EN MOYENNE À PARTS ÉGALES QUAND LES BRAS SONT ÉGAUX. C'est ce qui rend le
    remède sûr : il ne peut toucher QUE les encadrements asymétriques, c'est-à-dire exactement
    ceux que la mesure a identifiés comme cassés. Un remède qui déplacerait aussi les cas sains
    demanderait de vérifier qu'il ne les abîme pas ; celui-ci ne le peut pas.
    """
    total = bras_gauche + bras_droit
    return 0.5 if total <= 0 else bras_droit / total


def combiner(gauche: np.ndarray, droite: np.ndarray, poids: float = 0.5) -> np.ndarray:
    """Le nuage entre les deux branches, `poids` étant celui de `gauche`.

    ⚠ `poids = 0.5` rend le milieu, qui est le cas déjà mesuré : le défaut préserve donc la
    mesure publiée, et seul un appelant qui demande autre chose la déplace.

    ⚠⚠ LES DEUX BRANCHES N'ONT PAS LA MÊME GRILLE — elles viennent de deux spires publiées, donc
    de deux paramétrages. Les moyenner cellule à cellule apparierait des points qui n'ont rien à
    voir. L'appariement se fait donc dans l'ESPACE, par plus proche voisin, ce qui est la seule
    correspondance que deux surfaces reconstruites partagent.

    ⚠ Le résultat a la taille de `gauche` : la combinaison est **orientée**, et l'appelant qui
    veut la symétrie doit la demander dans les deux sens. Prétendre le contraire cacherait que
    deux nuages de tailles différentes ne se moyennent pas en un nuage canonique.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if gauche.size == 0 or droite.size == 0:
        return gauche
    proche = droite[cKDTree(droite).query(gauche, k=1)[1]]
    return poids * gauche + (1.0 - poids) * proche


def desaccord(gauche: np.ndarray, droite: np.ndarray, voxel_um: float) -> np.ndarray:
    """La distance de chaque point d'une branche à l'autre branche, en micromètres.

    ⚠⚠⚠ C'EST LA SEULE MESURE DE CONFIANCE DU CHANTIER QUI NE DEMANDE PAS LA RÉPONSE. Tout le
    reste — erreur, part perdue, groupement — se calcule contre une spire publiée. Celle-ci se
    calcule entre deux reconstructions, donc un dérouleur pourrait s'en servir en marchant. Reste
    à savoir si elle prédit quelque chose, ce que cette mesure confronte.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    return distance_a(gauche, droite, voxel_um)


def ecart_signe(branche: np.ndarray, cible: np.ndarray, direction: np.ndarray,
                voxel_um: float) -> float:
    """De combien la branche DÉPASSE sa cible, le long de sa direction de marche, en µm.

    ⚠⚠⚠ POURQUOI LE SIGNE, ET PAS SEULEMENT LA DISTANCE. Une distance est toujours positive,
    donc deux branches qui se trompent en sens contraires ont exactement le même profil d'erreur
    qu'une qui se trompe deux fois dans le même sens. Le signe sépare les deux, et c'est lui qui
    dit si l'encadrement gagne parce qu'il **annule un biais** ou parce que moyenner deux choses
    bruitées aide toujours un peu. Ce sont deux mécanismes différents et ils ne promettent pas
    la même chose ailleurs.

    ⚠ La projection se fait sur la direction de marche de la branche, pas sur la normale de la
    cible : ce qu'on veut savoir est si elle est allée trop loin, et « trop loin » se compte le
    long du chemin parcouru.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if branche.size == 0 or cible.size == 0:
        return 0.0
    proche = cible[cKDTree(cible).query(branche, k=1)[1]]
    u = direction / max(1e-12, float(np.linalg.norm(direction)))
    return float(np.median((branche - proche) @ u)) * voxel_um


def triplets(rangs: list[int], j: int) -> list[tuple[int, int, int]]:
    """Les triplets SYMÉTRIQUES `(m − j, m, m + j)` dont les trois spires sont disponibles."""
    presents = set(rangs)
    return [(m - j, m, m + j) for m in sorted(presents)
            if (m - j) in presents and (m + j) in presents]


def encadrements(rangs: list[int], portee: int) -> list[tuple[int, int, int]]:
    """TOUS les encadrements `(a, m, b)` avec `a < m < b`, chaque bras au plus long de `portee`.

    ⚠⚠⚠ POURQUOI LES ASYMÉTRIQUES COMPTENT. Les triplets symétriques répondent « l'encadrement
    vaut-il mieux qu'une branche », à difficulté égale des deux côtés. Ils ne répondent PAS à la
    question qui décide de l'effort : **des ancres coûtent, donc où les poser**. Un bras court et
    un bras long est le cas réel — on a rarement deux ancres à égale distance — et savoir si ça
    vaut deux bras moyens dit s'il faut espacer régulièrement ou grouper.

    ⚠ La portée est bornée des deux côtés séparément : un bras de dix contre un bras d'un ne
    mesurerait plus un encadrement mais une branche avec un garde-fou lointain.
    """
    presents = sorted(set(rangs))
    return [(a, m, b) for m in presents
            for a in presents if 0 < m - a <= portee
            for b in presents if 0 < b - m <= portee]




def mesurer(cote: float | None = None, minimum: int = 30, portee: int = 4,
            corpus: dict | None = None) -> dict:
    """Encadrer chaque spire par toutes les paires d'ancres à portée, et juger les trois nuages.

    ⚠ `portee` borne CHAQUE bras séparément. Les encadrements symétriques sont un sous-ensemble
    des encadrements mesurés, pas une mesure à part : les séparer ferait deux populations qu'on
    finirait par comparer sans le dire.

    ⚠⚠ `corpus` par défaut est celui du dépôt distant : le nombre publié ne change donc pas
    d'une virgule. Un appelant qui en fournit un autre — la batterie hors ligne — exerce le même
    code sur une autre matière, ce qui est exactement la propriété qui manquait.
    """
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

    lignes = []
    for bas, milieu, haut in encadrements(sorted(grilles), portee):
        cible = nuages[milieu]
        branches, directions = {}, {}
        for depart, cle, tours in ((bas, "montante", milieu - bas),
                                   (haut, "descendante", haut - milieu)):
            a0, ok0 = grilles[depart]
            n0, bon0 = normales(a0, ok0)
            if not bon0.any():
                break
            # ⚠⚠ UN BIT DE SUPERVISION PAR BRANCHE, DÉCLARÉ : le signe de la normale vient du
            # paramétrage de la grille, pas de la matière, donc il est fixé au premier pas en
            # regardant la cible — et une seule fois. Les branches en ont donc deux à elles
            # deux, contre un pour une marche simple, et c'est le prix de l'encadrement.
            e = essayer_le_pas(a0[bon0], n0[bon0], cible, pas_vx, voxel_um)
            sens = 1.0 if e["retenu"] == "+" else -1.0
            # ⚠ Chaque branche marche le nombre de tours de SON bras : avec des encadrements
            # asymétriques, les deux n'en font plus autant, et prendre un compte commun
            # ferait marcher l'une trop loin.
            av, okv = marcher(a0, ok0, tours, pas_vx, sens)
            if int(okv.sum()) < minimum:
                break
            branches[cle] = av[okv]
            # ⚠ La direction de marche de la branche est la normale MOYENNE de sa
            # surface de départ, orientée par le sens retenu : c'est la seule direction que
            # les deux branches partagent au signe près, donc la seule sur laquelle leurs
            # écarts se comparent.
            directions[cle] = sens * n0[bon0].mean(axis=0)
        if len(branches) != 2:
            continue
        g_, d_ = branches["montante"], branches["descendante"]
        # ⚠ La direction de marche retenue pour la projection est celle de la branche
        # MONTANTE : les deux branches vont en sens contraires, donc les projeter chacune
        # sur la sienne rendrait deux nombres positifs et cacherait justement l'opposition
        # qu'on cherche à mesurer.
        axe = directions["montante"]
        s_g = ecart_signe(g_, cible, axe, voxel_um)
        s_d = ecart_signe(d_, cible, axe, voxel_um)
        mid_g = combiner(g_, d_)
        mid_d = combiner(d_, g_)
        # ⚠⚠ LE POIDS EST DÉRIVÉ DES BRAS, appliqué dans le bon sens : la branche au bras COURT
        # pèse le plus. L'inverser est le témoin — sans lui, « la pondération aide » serait
        # satisfait par n'importe quel déplacement du milieu.
        w = poids_par_les_bras(milieu - bas, haut - milieu)
        pond_g = combiner(g_, d_, w)
        pond_d = combiner(d_, g_, 1.0 - w)
        pond_inv_g = combiner(g_, d_, 1.0 - w)
        pond_inv_d = combiner(d_, g_, w)
        e_g = float(np.median(distance_a(g_, cible, voxel_um)))
        e_d = float(np.median(distance_a(d_, cible, voxel_um)))
        e_m = float(np.median(np.concatenate([
            distance_a(mid_g, cible, voxel_um), distance_a(mid_d, cible, voxel_um)])))
        e_p = float(np.median(np.concatenate([
            distance_a(pond_g, cible, voxel_um), distance_a(pond_d, cible, voxel_um)])))
        e_pi = float(np.median(np.concatenate([
            distance_a(pond_inv_g, cible, voxel_um),
            distance_a(pond_inv_d, cible, voxel_um)])))
        des = float(np.median(desaccord(g_, d_, voxel_um)))
        lignes.append(dict(
            bras_bas=milieu - bas, bras_haut=haut - milieu,
            saut=max(milieu - bas, haut - milieu),
            symetrique=bool(milieu - bas == haut - milieu),
            depuis_bas=bas, cible=milieu, depuis_haut=haut,
            points_montante=int(len(g_)), points_descendante=int(len(d_)),
            erreur_montante_um=round(e_g, 1), erreur_descendante_um=round(e_d, 1),
            erreur_encadree_um=round(e_m, 1),
            erreur_ponderee_um=round(e_p, 1),
            temoin_poids_inverse_um=round(e_pi, 1),
            poids_de_la_montante=round(w, 3),
            erreur_de_la_meilleure_um=round(min(e_g, e_d), 1),
            desaccord_um=round(des, 1),
            ecart_signe_montante_um=round(s_g, 1),
            ecart_signe_descendante_um=round(s_d, 1),
            signes_opposes=bool(s_g * s_d < 0),
            bits_de_supervision=2))

    if not lignes:
        raise RuntimeError("aucun triplet mesurable dans la boîte")

    def med(cle):
        return round(float(np.median([e[cle] for e in lignes])), 1)

    r = dict(
        fragment="PHerc0500P2", volume=volume, voxel_um=voxel_um,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote),
        ecart_lu_um=ecart_um, demi_epaisseur_um=round(ecart_um / 2, 2),
        portee=portee, triplets=len(lignes), lignes=lignes,
        triplets_symetriques=sum(1 for e in lignes if e["symetrique"]),
        erreur_montante_mediane_um=med("erreur_montante_um"),
        erreur_descendante_mediane_um=med("erreur_descendante_um"),
        erreur_encadree_mediane_um=med("erreur_encadree_um"),
        erreur_de_la_meilleure_mediane_um=med("erreur_de_la_meilleure_um"),
        desaccord_median_um=med("desaccord_um"),
    )
    # ⚠⚠⚠ LE VERDICT EST QUE L'ENCADREMENT BATTE LES DEUX BRANCHES, TRIPLET PAR TRIPLET. Battre
    # leur médiane serait plus facile et ne voudrait rien dire : « prendre la meilleure des deux »
    # y suffirait, et savoir laquelle est la meilleure demande la réponse.
    # ⚠⚠ CE QUE LES ENCADREMENTS ASYMÉTRIQUES DÉCIDENT : à budget d'ancres égal, faut-il les
    # espacer régulièrement ou peut-on en poser une près et une loin ? Le regroupement se fait
    # sur la PAIRE de bras, pas sur leur somme : (1, 3) et (2, 2) coûtent la même chose et ne
    # promettent pas la même chose.
    par_bras = {}
    for e in lignes:
        cle = f"{min(e['bras_bas'], e['bras_haut'])}+{max(e['bras_bas'], e['bras_haut'])}"
        par_bras.setdefault(cle, []).append(e)
    r["par_paire_de_bras"] = {
        cle: dict(n=len(v),
                  encadree_um=round(float(np.median([x["erreur_encadree_um"] for x in v])), 1),
                  meilleure_branche_um=round(
                      float(np.median([x["erreur_de_la_meilleure_um"] for x in v])), 1),
                  symetrique=("+" in cle and cle.split("+")[0] == cle.split("+")[1]))
        for cle, v in sorted(par_bras.items())}
    # ⚠⚠⚠ LA COMPARAISON QUI DÉCIDE : à SOMME DE BRAS égale — donc à même écartement d'ancres —
    # le symétrique fait-il mieux que l'asymétrique ? C'est la question « où poser la seconde
    # ancre », et elle se pose à budget constant, sinon on compare deux dépenses.
    memes_sommes = {}
    for cle, d_ in r["par_paire_de_bras"].items():
        a_, b_ = (int(x) for x in cle.split("+"))
        memes_sommes.setdefault(a_ + b_, []).append((a_ == b_, d_["encadree_um"]))
    r["a_somme_egale"] = {
        str(k): dict(symetrique=next((x[1] for x in v if x[0]), None),
                     asymetrique=(None if not [x for x in v if not x[0]] else
                                  round(float(np.median([x[1] for x in v if not x[0]])), 1)))
        for k, v in sorted(memes_sommes.items()) if len(v) > 1}
    # ⚠⚠⚠ ET LA LIMITE, qui est le vrai conseil pratique : un bras BEAUCOUP plus long que
    # l'autre casse l'encadrement. La branche lointaine a tellement dérivé que la moyenne tire
    # la bonne avec elle — l'encadrement devient alors PIRE que sa meilleure branche, ce qui est
    # exactement le cas où il ne faut pas s'en servir.
    r["paires_ou_lencadrement_nuit"] = [
        cle for cle, d_ in r["par_paire_de_bras"].items()
        if d_["encadree_um"] > d_["meilleure_branche_um"]]
    # ⚠⚠ ET LE CHIFFRE QUI SERAIT TROMPEUR N'EST PAS PUBLIÉ. Le déséquilibre minimal parmi les
    # paires qui nuisent vaut deux — mais `1+3` a exactement ce déséquilibre et ne nuit pas.
    # Écrire « nuit dès un déséquilibre de deux » serait un seuil qui se lit comme une règle et
    # qui est faux. Ce que les deux paires fautives partagent est leur BRAS LONG, et il vaut la
    # portée mesurée : on ne peut donc pas dire, avec ce corpus, si c'est la longueur absolue ou
    # le déséquilibre qui casse. Les deux faits sont rendus, la conclusion non.
    r["bras_longs_des_paires_qui_nuisent"] = sorted(
        {int(c.split("+")[1]) for c in r["paires_ou_lencadrement_nuit"]})
    r["desequilibres_des_paires_qui_nuisent"] = sorted(
        {int(c.split("+")[1]) - int(c.split("+")[0]) for c in r["paires_ou_lencadrement_nuit"]})
    r["meme_desequilibre_sans_nuire"] = sorted(
        cle for cle, d_ in r["par_paire_de_bras"].items()
        if cle not in r["paires_ou_lencadrement_nuit"]
        and (int(cle.split("+")[1]) - int(cle.split("+")[0]))
        in r["desequilibres_des_paires_qui_nuisent"])
    r["la_symetrie_aide"] = bool(any(
        d_["symetrique"] is not None and d_["asymetrique"] is not None
        and d_["symetrique"] < d_["asymetrique"] for d_ in r["a_somme_egale"].values()))
    # ⚠⚠⚠ LE MÉCANISME : les deux branches se trompent-elles en sens CONTRAIRES ? Si oui,
    # l'encadrement annule un biais, et c'est une propriété de la marche qu'on peut espérer
    # ailleurs. Si non, il ne fait que moyenner du bruit, ce qui gagne √2 au mieux et ne promet
    # rien. Les deux mécanismes rendent la même médiane et ne disent pas la même chose.
    r["triplets_aux_signes_opposes"] = sum(1 for e in lignes if e["signes_opposes"])
    r["lencadrement_annule_un_biais"] = bool(
        r["triplets_aux_signes_opposes"] > 0.75 * len(lignes))
    r["ecart_signe_montant_median_um"] = med("ecart_signe_montante_um")
    r["ecart_signe_descendant_median_um"] = med("ecart_signe_descendante_um")
    r["triplets_ou_lencadrement_bat_les_deux"] = sum(
        1 for e in lignes
        if e["erreur_encadree_um"] < min(e["erreur_montante_um"], e["erreur_descendante_um"]))
    # ⚠⚠ LE RAPPORT EST PUBLIÉ ICI, PAS CALCULÉ PAR LA FIGURE. Un nombre qui apparaît dans une
    # légende sans exister dans la mesure est un nombre que personne ne peut retrouver — et le
    # contrôle de traçabilité de la prose l'a attrapé.
    r["erreur_ponderee_mediane_um"] = med("erreur_ponderee_um")
    r["temoin_poids_inverse_median_um"] = med("temoin_poids_inverse_um")
    # ⚠⚠⚠ LA PONDÉRATION NE PEUT TOUCHER QUE LES ASYMÉTRIQUES, par construction : à bras égaux
    # le poids vaut un demi et rend le milieu. Le vérifier ici plutôt que l'affirmer, parce que
    # c'est ce qui rend le remède sûr — il ne peut pas abîmer les cas qui marchaient.
    r["symetriques_inchanges_par_la_ponderation"] = all(
        e["erreur_ponderee_um"] == e["erreur_encadree_um"]
        for e in lignes if e["symetrique"])
    # ⚠⚠ ET LA VRAIE QUESTION : répare-t-elle les paires que la mesure a dites CASSÉES ? Une
    # pondération qui améliorerait la médiane globale sans réparer celles-là aurait déplacé des
    # cas déjà sains, ce qui ne vaut rien.
    r["paires_reparees_par_la_ponderation"] = [
        cle for cle in r["paires_ou_lencadrement_nuit"]
        if float(np.median([e["erreur_ponderee_um"] for e in lignes
                            if f"{min(e['bras_bas'], e['bras_haut'])}+"
                            f"{max(e['bras_bas'], e['bras_haut'])}" == cle]))
        < r["par_paire_de_bras"][cle]["meilleure_branche_um"]]
    r["la_ponderation_repare_les_paires_cassees"] = bool(
        r["paires_ou_lencadrement_nuit"]
        and len(r["paires_reparees_par_la_ponderation"])
        == len(r["paires_ou_lencadrement_nuit"]))
    r["la_ponderation_bat_le_milieu"] = bool(
        r["erreur_ponderee_mediane_um"] < r["erreur_encadree_mediane_um"])
    r["la_ponderation_bat_son_temoin"] = bool(
        r["erreur_ponderee_mediane_um"] < r["temoin_poids_inverse_median_um"])
    r["gain_sur_la_meilleure_branche"] = round(
        r["erreur_de_la_meilleure_mediane_um"] / r["erreur_encadree_mediane_um"], 2)
    r["gain_sur_la_branche_montante"] = round(
        r["erreur_montante_mediane_um"] / r["erreur_encadree_mediane_um"], 2)
    r["lencadrement_bat_les_deux"] = bool(
        r["erreur_encadree_mediane_um"] < r["erreur_de_la_meilleure_mediane_um"])
    # ⚠⚠ ET LE DÉSACCORD DOIT PRÉDIRE L'ERREUR pour valoir comme signal de confiance : sans cela
    # c'est un nombre qu'on peut calculer et dont on ne peut rien faire. La corrélation de rang
    # est préférée à celle de Pearson — on demande un ORDRE, pas une droite.
    if len(lignes) > 2:
        from scipy.stats import spearmanr  # noqa: PLC0415

        rho, pval = spearmanr([e["desaccord_um"] for e in lignes],
                              [e["erreur_encadree_um"] for e in lignes])
        r["desaccord_contre_erreur"] = dict(rho=round(float(rho), 3), p=round(float(pval), 4),
                                            n=len(lignes))
        r["le_desaccord_predit_lerreur"] = bool(rho > 0 and pval < 0.05)
    r["sous_la_demi_feuille"] = {
        cle: bool(r[cle] < ecart_um / 2) for cle in
        ("erreur_montante_mediane_um", "erreur_descendante_mediane_um",
         "erreur_encadree_mediane_um")}
    return r


def cles_lues_par(chemin: Path) -> set[str]:
    """Les clés que ce fichier lit par indice littéral — `x["…"]` — dans son arbre syntaxique.

    ⚠⚠ LUES DANS L'ARBRE, PAS PAR EXPRESSION RÉGULIÈRE. Une chaîne citée dans un commentaire ou
    une f-string n'est pas une lecture, et la compter ferait rougir le contrôle sur du texte —
    donc rendrait la traçabilité de la prose incompatible avec celle du code.

    ⚠ La liste n'est écrite nulle part, elle est DÉRIVÉE du fichier qui lit. Une liste recopiée
    à la main serait juste le jour où on l'écrit et se tairait à la première clé ajoutée, ce qui
    est exactement la panne que ce contrôle existe pour attraper.
    """
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    return {n.slice.value for n in ast.walk(arbre)
            if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
            and isinstance(n.slice.value, str)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- les triplets ---
    v("un triplet est symétrique et ses trois spires sont là",
      triplets([4, 5, 6, 7], 1) == [(4, 5, 6), (5, 6, 7)], str(triplets([4, 5, 6, 7], 1)))
    v("... et un trou en retire ceux qui le traversent",
      triplets([4, 5, 7, 8], 1) == [], str(triplets([4, 5, 7, 8], 1)))
    v("un saut plus grand donne d'autres triplets",
      triplets([4, 5, 6, 7, 8], 2) == [(4, 6, 8)], str(triplets([4, 5, 6, 7, 8], 2)))

    # --- les encadrements, symétriques et non ---
    enc = encadrements([4, 5, 6, 7], 2)
    v("tout encadrement a une ancre de chaque côté",
      all(a < m < b for a, m, b in enc) and len(enc) == 4, str(enc))
    v("... et les symétriques en sont un sous-ensemble",
      set(triplets([4, 5, 6, 7], 1)) <= set(enc), str(triplets([4, 5, 6, 7], 1)))
    # ⚠ Les asymétriques existent dès que la portée dépasse un, et ce sont justement eux qu'un
    # balayage limité aux symétriques n'aurait jamais vus. ⚠ Ma première version les disait
    # « majoritaires » : sur quatre spires et une portée de deux ils sont deux sur quatre, donc
    # l'attendu était faux, pas le code.
    v("... et les asymétriques existent",
      sum(1 for a, m, b in enc if m - a != b - m) >= 2, str(enc))
    # ⚠⚠ LA PORTÉE BORNE CHAQUE BRAS SÉPARÉMENT : un bras de dix contre un bras d'un ne
    # mesurerait plus un encadrement mais une branche avec un garde-fou lointain.
    v("la portée borne chaque bras, pas leur somme",
      all(m - a <= 1 and b - m <= 1 for a, m, b in encadrements([1, 2, 3, 4, 5], 1)),
      str(encadrements([1, 2, 3, 4, 5], 1)))
    v("une portée nulle ne rend aucun encadrement", encadrements([1, 2, 3], 0) == [])

    # --- la marche, sur un plan dont on connaît la cible ---
    uu, vv = np.meshgrid(np.arange(14.0), np.arange(14.0), indexing="ij")
    plan = np.stack([uu * 3 + 100, vv * 3 + 100, np.full(uu.shape, 50.0)], axis=-1)
    ok = np.ones(plan.shape[:2], dtype=bool)
    av, okv = marcher(plan, ok, 2, 10.0, 1.0)
    v("deux pas de dix avancent de vingt", abs(float(np.median(av[okv][:, 2])) - 70.0) < 1e-9,
      str(float(np.median(av[okv][:, 2]))))
    # ⚠ Le masque fond d'une cellule par tour : le compte est rendu, pas caché.
    v("... et la grille perd une cellule de bord par tour",
      int(okv.sum()) == 10 * 10, str(int(okv.sum())))

    # --- la combinaison ---
    g = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    d = np.array([[0.0, 0.0, 10.0], [1.0, 0.0, 10.0]])
    v("la combinaison tombe à mi-chemin",
      bool(np.allclose(combiner(g, d)[:, 2], 5.0)), str(combiner(g, d)))
    v("... et combiner un nuage avec lui-même ne le déplace pas",
      bool(np.allclose(combiner(g, g), g)))
    # ⚠⚠ L'APPARIEMENT EST SPATIAL, PAS PAR INDICE : deux grilles différentes n'ont pas les mêmes
    # cellules, et un appariement par indice moyennerait des points sans rapport.
    d_melange = d[::-1].copy()
    v("l'appariement se fait par plus proche voisin, pas par indice",
      bool(np.allclose(combiner(g, d_melange), combiner(g, d))))
    v("un nuage vide laisse l'autre en place", bool(np.allclose(combiner(g, np.zeros((0, 3))), g)))
    # ⚠ La combinaison est ORIENTÉE : deux nuages de tailles différentes n'ont pas de milieu
    # canonique, et prétendre le contraire cacherait l'asymétrie.
    v("la combinaison a la taille de son premier argument",
      combiner(g, np.vstack([d, d]))
      .shape[0] == 2 and combiner(np.vstack([g, g]), d).shape[0] == 4)

    # --- le poids dérivé des bras ---
    v("à bras égaux le poids vaut un demi", poids_par_les_bras(3, 3) == 0.5)
    # ⚠⚠ LA BRANCHE AU BRAS COURT PÈSE LE PLUS : l'inverse serait une pondération qui fait
    # confiance à celle qui a le plus dérivé, et le témoin de la mesure l'exerce.
    v("... et la branche au bras COURT pèse le plus", poids_par_les_bras(1, 4) > 0.5,
      str(poids_par_les_bras(1, 4)))
    v("... proportionnellement à l'autre bras", abs(poids_par_les_bras(1, 4) - 0.8) < 1e-9,
      str(poids_par_les_bras(1, 4)))
    v("des bras nuls ne rendent pas une division par zéro", poids_par_les_bras(0, 0) == 0.5)
    # ⚠⚠⚠ ET LA COMBINAISON PONDÉRÉE DOIT TOMBER SUR LA CIBLE quand l'erreur croît linéairement
    # avec le bras — c'est l'hypothèse dont le poids est tiré, donc elle se vérifie plutôt que
    # de se supposer. Une branche à un bras dérive de d, celle à quatre bras de 4d de l'autre
    # côté : l'interpolation linéaire les annule exactement.
    cib = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    court = cib + np.array([0.0, 0.0, -10.0])
    long_ = cib + np.array([0.0, 0.0, 40.0])
    from le_pas_normal_atteint_la_spire import distance_a as _d  # noqa: PLC0415
    w_ = poids_par_les_bras(1, 4)
    v("la pondération annule une dérive linéaire en la longueur du bras",
      float(np.median(_d(combiner(court, long_, w_), cib, 1.0))) < 1e-6,
      str(float(np.median(_d(combiner(court, long_, w_), cib, 1.0)))))
    v("... alors que la moyenne à parts égales ne l'annule pas",
      float(np.median(_d(combiner(court, long_), cib, 1.0))) > 10.0,
      str(float(np.median(_d(combiner(court, long_), cib, 1.0)))))
    v("... et le poids INVERSÉ fait bien pire",
      float(np.median(_d(combiner(court, long_, 1.0 - w_), cib, 1.0)))
      > float(np.median(_d(combiner(court, long_), cib, 1.0))))

    # --- le désaccord ---
    ds = desaccord(g, d, 2.0)
    v("le désaccord vaut la distance entre les deux branches",
      bool(np.allclose(ds, 20.0)), str(ds))
    v("... et il est nul entre une branche et elle-même",
      bool(np.allclose(desaccord(g, g, 2.0), 0.0)))
    # ⚠⚠⚠ LE TÉMOIN QUI COMPTE : une combinaison ne doit PAS être meilleure par construction.
    # Deux branches du MÊME côté de la cible ont un milieu qui reste du même côté, donc pas
    # meilleur que la plus proche — sans ce contrôle, « l'encadrement gagne » serait une
    # propriété de la moyenne et pas de l'encadrement.
    cible = np.array([[0.0, 0.0, 100.0], [1.0, 0.0, 100.0]])
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415
    meme_cote_a = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    meme_cote_b = np.array([[0.0, 0.0, 20.0], [1.0, 0.0, 20.0]])
    mid = combiner(meme_cote_a, meme_cote_b)
    v("deux branches du même côté : leur milieu ne bat pas la plus proche",
      float(np.median(distance_a(mid, cible, 1.0)))
      >= float(np.median(distance_a(meme_cote_b, cible, 1.0))),
      f"{float(np.median(distance_a(mid, cible, 1.0)))} contre "
      f"{float(np.median(distance_a(meme_cote_b, cible, 1.0)))}")
    # ⚠ … alors que deux branches qui l'ENCADRENT doivent, elles, faire mieux que les deux.
    enc_a = np.array([[0.0, 0.0, 60.0], [1.0, 0.0, 60.0]])
    enc_b = np.array([[0.0, 0.0, 150.0], [1.0, 0.0, 150.0]])
    mid2 = combiner(enc_a, enc_b)
    v("... et deux branches qui encadrent font mieux que les deux",
      float(np.median(distance_a(mid2, cible, 1.0)))
      < min(float(np.median(distance_a(enc_a, cible, 1.0))),
            float(np.median(distance_a(enc_b, cible, 1.0)))),
      str(float(np.median(distance_a(mid2, cible, 1.0)))))

    # --- l'écart SIGNÉ ---
    axe = np.array([0.0, 0.0, 1.0])
    v("une branche qui dépasse rend un écart positif",
      ecart_signe(enc_b, cible, axe, 1.0) > 0, str(ecart_signe(enc_b, cible, axe, 1.0)))
    v("... et une branche qui n'est pas allée assez loin, un écart négatif",
      ecart_signe(enc_a, cible, axe, 1.0) < 0, str(ecart_signe(enc_a, cible, axe, 1.0)))
    # ⚠⚠⚠ C'EST CE SIGNE QUI SÉPARE LES DEUX MÉCANISMES : deux branches du MÊME côté rendent le
    # même signe, donc leur moyenne ne peut pas annuler de biais — et c'est exactement le cas
    # où le contrôle plus haut montre que l'encadrement ne gagne pas.
    v("deux branches du même côté rendent le même signe",
      ecart_signe(meme_cote_a, cible, axe, 1.0)
      * ecart_signe(meme_cote_b, cible, axe, 1.0) > 0)
    v("... et deux branches qui encadrent, des signes opposés",
      ecart_signe(enc_a, cible, axe, 1.0) * ecart_signe(enc_b, cible, axe, 1.0) < 0)
    v("l'écart signé est nul contre soi-même",
      abs(ecart_signe(cible, cible, axe, 1.0)) < 1e-9)
    v("... et une cible vide ne rend pas d'écart",
      ecart_signe(enc_a, np.zeros((0, 3)), axe, 1.0) == 0.0)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE. Tout ce qui précède teste des
    # briques ; ce qui suit fait tourner `mesurer` en entier sur une matière fabriquée. Une
    # batterie verte sur un module dont le seul chemin non testé est celui qui produit le nombre
    # publié est une batterie qui ne peut pas échouer là où ça compte — et c'est exactement ce
    # qui a laissé passer, le 2026-09-05, un enregistrement référençant des variables absentes.
    #
    # ⚠⚠ AUCUNE VALEUR N'EST VÉRIFIÉE ICI. La fixture n'est pas le fragment : ses micromètres ne
    # veulent rien dire, et une batterie qui les épinglerait mesurerait la fixture. Ce qui est
    # vérifié, ce sont les invariants que la mesure revendique et les clés qu'elle promet.
    fab = mesurer(minimum=30, portee=3, corpus=corpus_fabrique())
    v("la mesure tourne de bout en bout sur un corpus fabriqué, sans rien lire",
      fab["triplets"] > 0, f"{fab['triplets']} triplets")
    # ⚠⚠ LA GARDE ANTI-DÉGÉNÉRÉ, et c'est la plus importante du bloc : des spires parfaitement
    # décalées sont atteintes EXACTEMENT par un pas normal, donc toutes les erreurs vaudraient
    # zéro et chaque comparaison ci-dessous serait satisfaite par des zéros.
    # ⚠ Ce que la sonde dit exactement, plutôt que ce qu'on aimerait : aplatir la fixture fait
    # aujourd'hui LEVER `mesurer` avant cette ligne — le gain se divise par une médiane nulle —
    # donc la batterie rougit sans arriver jusqu'ici. Les deux issues sont rouges, aucune n'est
    # silencieuse, et cette ligne reste celle qui NOMME l'exigence.
    v("... et la marche y est imparfaite, donc les comparaisons portent sur quelque chose",
      all(e["erreur_montante_um"] > 0 and e["erreur_descendante_um"] > 0 for e in fab["lignes"]),
      f"erreur montante médiane {fab['erreur_montante_mediane_um']} µm")
    v("... chaque bras est dans la portée demandée",
      all(1 <= e["bras_bas"] <= 3 and 1 <= e["bras_haut"] <= 3 for e in fab["lignes"]))
    v("... la meilleure branche est la plus petite des deux, ligne par ligne",
      all(e["erreur_de_la_meilleure_um"]
          == min(e["erreur_montante_um"], e["erreur_descendante_um"]) for e in fab["lignes"]))
    v("... un encadrement est symétrique exactement quand ses deux bras sont égaux",
      all(e["symetrique"] == (e["bras_bas"] == e["bras_haut"]) for e in fab["lignes"]))
    v("... et le poids vaut un demi sur ceux-là, et sur eux seuls",
      all((e["poids_de_la_montante"] == 0.5) == e["symetrique"] for e in fab["lignes"]))
    v("... donc la pondération ne peut pas déplacer un cas symétrique",
      fab["symetriques_inchanges_par_la_ponderation"])
    v("... les encadrements asymétriques sont mesurés eux aussi",
      any(not e["symetrique"] for e in fab["lignes"]),
      str(sorted(fab["par_paire_de_bras"])))
    v("... et la comparaison à somme de bras égale a de quoi comparer",
      bool(fab["a_somme_egale"]), str(sorted(fab["a_somme_egale"])))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    # ⚠ L'exception est RATTRAPÉE pour être rendue en contrôle rouge nommé, pas laissée
    # remonter : une trace d'appels dit qu'il s'est passé quelque chose, une ligne rouge dit
    # quoi. La sonde qui renomme une clé lue par l'affichage tombe sur celle-ci.
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "l'encadrement bat les DEUX branches" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")
    # ⚠⚠ LA TRAÇABILITÉ DANS L'AUTRE SENS : la figure ne doit lire aucune clé que la mesure ne
    # publie pas. Une légende qui affiche un nombre absent du JSON est un nombre que personne ne
    # peut retrouver, et ce dépôt l'a déjà payé une fois.
    formes = set(fab) | set(fab["lignes"][0]) | set(fab["desaccord_contre_erreur"]) \
        | set(next(iter(fab["par_paire_de_bras"].values()))) \
        | set(next(iter(fab["a_somme_egale"].values())))
    manquantes = sorted(cles_lues_par(RACINE / "src" / "figures"
                                      / "figure_derouler_des_deux_bords.py") - formes)
    v("la figure ne lit aucune clé que la mesure ne publie pas",
      not manquantes, str(manquantes))
    # ⚠⚠ ET LES DEUX REFUS, parce qu'un chemin heureux qui marche ne dit pas qu'un seuil est
    # respecté : une spire dont il ne reste presque rien doit être écartée, et un corpus posé
    # hors de la boîte ne doit rendre aucun triplet.
    creux = mesurer(minimum=30, portee=3, corpus=corpus_fabrique(creuse=3))
    rangs_vus = {e[c] for e in creux["lignes"] for c in ("depuis_bas", "cible", "depuis_haut")}
    v("une spire dont il ne reste que trois cellules est écartée",
      3 not in rangs_vus and creux["triplets"] > 0, str(sorted(rangs_vus)))
    hors = None
    try:
        mesurer(minimum=30, portee=3, corpus=corpus_fabrique(decalage_vx=5000.0))
    except RuntimeError as exc:
        hors = str(exc)
    v("un corpus posé hors de la boîte est REFUSÉ, pas rendu vide", hors is not None, str(hors))
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cote=a.cote)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure.

    ⚠⚠⚠ POURQUOI L'AFFICHAGE EST UNE FONCTION ET PLUS UN BLOC DE `main`. Un bloc de `main` ne
    peut être exercé qu'en lisant le dépôt distant, donc jamais par la batterie — et c'est là
    qu'un patch à moitié appliqué a laissé, le 2026-09-05, un enregistrement qui référençait des
    variables inexistantes. Sorti de `main`, il tourne sur n'importe quel corpus, et une clé
    absente ou renommée lève **hors ligne**.

    ⚠ Il ne calcule rien. Un nombre qui apparaîtrait ici sans exister dans la mesure serait un
    nombre que personne ne peut retrouver depuis le JSON publié — le contrôle de traçabilité de
    la prose a déjà attrapé ce défaut une fois.
    """
    print(f"écart inter-feuilles {r['ecart_lu_um']} µm · demi-épaisseur "
          f"{r['demi_epaisseur_um']} µm · {r['triplets']} triplets\n")
    print(f"{'saut':>5} {'triplet':>12} {'montante':>10} {'descend.':>10} {'ENCADRÉE':>10} "
          f"{'désaccord':>11}")
    print("-" * 64)
    for e in r["lignes"]:
        trio = f"{e['depuis_bas']}→{e['cible']}←{e['depuis_haut']}"
        print(f"{e['saut']:>5} {trio:>12} "
              f"{e['erreur_montante_um']:>9.0f}µ {e['erreur_descendante_um']:>9.0f}µ "
              f"{e['erreur_encadree_um']:>9.0f}µ {e['desaccord_um']:>10.0f}µ")
    print(f"\nmédianes : montante {r['erreur_montante_mediane_um']} µm · descendante "
          f"{r['erreur_descendante_mediane_um']} µm · encadrée "
          f"{r['erreur_encadree_mediane_um']} µm")
    print(f"la meilleure des deux branches : {r['erreur_de_la_meilleure_mediane_um']} µm "
          "(elle demande de savoir laquelle)")
    print(f"désaccord entre branches : {r['desaccord_median_um']} µm")
    print(f"écart SIGNÉ le long de la marche montante : montante "
          f"{r['ecart_signe_montant_median_um']:+.1f} µm · descendante "
          f"{r['ecart_signe_descendant_median_um']:+.1f} µm → signes opposés sur "
          f"{r['triplets_aux_signes_opposes']} triplets sur {r['triplets']}, donc "
          f"{'un BIAIS annulé' if r['lencadrement_annule_un_biais'] else 'du bruit moyenné'}")
    if "desaccord_contre_erreur" in r:
        d = r["desaccord_contre_erreur"]
        print(f"le désaccord prédit-il l'erreur ? rho {d['rho']} (p {d['p']}, n {d['n']}) → "
              f"{'OUI' if r['le_desaccord_predit_lerreur'] else 'NON'}")
    print("\npar paire de bras (bras court + bras long) :")
    for cle, d_ in r["par_paire_de_bras"].items():
        marque = " symétrique" if d_["symetrique"] else ""
        nuit = "  ⚠ NUIT" if cle in r["paires_ou_lencadrement_nuit"] else ""
        print(f"  {cle:>5} · {d_['n']:>2} cas · encadrée {d_['encadree_um']:>6.1f} µm · "
              f"meilleure branche {d_['meilleure_branche_um']:>6.1f} µm{marque}{nuit}")
    print("à somme de bras égale, la symétrie aide : "
          f"{'OUI' if r['la_symetrie_aide'] else 'NON'} — {r['a_somme_egale']}")
    print(f"l'encadrement NUIT sur {r['paires_ou_lencadrement_nuit']} — bras longs "
          f"{r['bras_longs_des_paires_qui_nuisent']}, déséquilibres "
          f"{r['desequilibres_des_paires_qui_nuisent']} ; mais "
          f"{r['meme_desequilibre_sans_nuire']} ont le même déséquilibre et ne nuisent pas, "
          "donc ce corpus ne dit pas si c'est la longueur ou le déséquilibre")
    print(f"\npondérée par les bras : {r['erreur_ponderee_mediane_um']} µm contre "
          f"{r['erreur_encadree_mediane_um']} à parts égales · témoin poids INVERSÉ "
          f"{r['temoin_poids_inverse_median_um']} µm")
    print(f"  symétriques inchangés (par construction) : "
          f"{'OUI' if r['symetriques_inchanges_par_la_ponderation'] else 'NON'} · "
          f"paires cassées réparées : {r['paires_reparees_par_la_ponderation']} sur "
          f"{r['paires_ou_lencadrement_nuit']}")
    print(f"\n→ l'encadrement bat les DEUX branches : "
          f"{'OUI' if r['lencadrement_bat_les_deux'] else 'NON'} "
          f"({r['triplets_ou_lencadrement_bat_les_deux']} triplets sur {r['triplets']})")


if __name__ == "__main__":
    sys.exit(main())
