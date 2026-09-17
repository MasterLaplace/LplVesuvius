"""La cohérence creuse-t-elle à la frontière ? — séparer un empilement d'une rotation sans le tour.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `178` a réfuté la voie la moins chère par un ÉCHANGE : le plancher du
juge descend d'un cran par pli lu — 90° à 36 couches, 45° à 72, 22,5° à 108 — mais un EMPILEMENT y
devient une ROTATION au même cran. Un escalier de plis portant le même tour total est lu comme un
empilement 306 fois sur 400 à un pli, puis comme une rotation 212 fois à deux et 226 à trois. Les
deux moitiés sont la MÊME quantité, le tour accumulé, et c'est cette unicité qui rend l'échange
inévitable : tout ce que `174`–`178` lit passe par l'orientation MOYENNE par couche.

⭐⭐⭐⭐ IL EXISTE UN SECOND OBSERVABLE, PRODUIT PAR LE MÊME CHEMIN DEPUIS LE DÉBUT, ET RIEN NE L'A
EXPLOITÉ. `orientation_profile` rend `(angle, cohérence)` couche par couche, et toute la chaîne ne
se sert de la cohérence que comme d'un POIDS. Or à une frontière de pli deux feuilles de directions
différentes se recouvrent : une couche qui contient les deux voit son tenseur de structure
s'isotropiser, donc sa cohérence CREUSE. Une rotation régulière ne creuse nulle part, parce qu'une
couche n'y contient jamais qu'une direction.

⚠⚠⚠ ET LA PRÉMISSE EST FAUSSE SUR LA MATIÈRE QUE LE DÉPÔT LISAIT. Mesuré avant d'écrire une ligne
de lecteur : sur `VolumeFabriqueAFibres` telle qu'elle existait, la frontière est un RASOIR — le
tenseur de structure est calculé DANS le plan d'une couche, et aucune couche ne contient deux plis.
La cohérence y vaut 1,0000 partout, aux deux frontières comme ailleurs. Le creux n'existe donc
qu'avec une ÉPAISSEUR DE RECOUVREMENT, et cette épaisseur est devenue un paramètre de la fixture
(`transition_um`, nul par défaut) plutôt qu'une hypothèse tue.

⭐⭐⭐⭐ CE QUI SE MESURE ICI EST DONC D'ABORD UN SEUIL DE MATIÈRE, PAS UN VERDICT. Combien de
recouvrement faut-il pour qu'un creux tombe sur la frontière à TOUS les décalages ? La forme de la
question est celle de `173` : une lecture qui ne marche qu'à un décalage sur deux est une loterie,
parce que la phase de la fenêtre dans la feuille n'est pas connue sur données réelles.

⚠⚠⚠ ET LE CONTRÔLE APPARIÉ RESTE LA PERMUTATION. Un creux est un MINIMUM, donc minimiser trouve
toujours quelque chose, exactement comme maximiser. Mélanger les couches conserve le multiensemble
des cohérences — donc la liberté de chercher le meilleur creux sur toutes les positions et toutes
les largeurs — et ne détruit que la localisation. L'EXCÉDENT, creux réel moins creux médian des
mélanges, est la seule part du creux qui vient de la profondeur.

⚠⚠ CE QUE CE LECTEUR NE FAIT PAS, ET IL FAUT L'ÉCRIRE : il ne classe pas deux formes. Il répond
« il y a une frontière ici » ou « rien », et une rotation comme du bruit rendent tous deux « rien ».
C'est `177` qui sait dire qu'une matière TOURNE. Les deux lecteurs sont donc complémentaires, et ce
que cette tranche met à l'épreuve est leur LECTURE JOINTE à la largeur où `178` a mesuré l'échange.

⚠ `156` mesure trois pertes au bruit 16 : la cohérence est sensible au bruit, donc le domaine se
mesure sur l'échelle de bruit de `156`, jamais supposé.

Usage :
    uv run python src/nappe/la_coherence_creuse_t_elle_a_la_frontiere.py --verifier
    uv run python src/nappe/la_coherence_creuse_t_elle_a_la_frontiere.py \\
        --json docs/mesures/la_coherence_creuse_t_elle_a_la_frontiere.json
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
    COUCHES_DE_LA_CAMPAGNE, COUCHES_MINIMALES)
from la_croix_marche_t_elle_le_tour import BRUITS  # noqa: E402
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import (  # noqa: E402
    GRAINES_PAR_CELLULE, PERMUTATIONS, le_verdict)
from plus_de_profondeur_ou_plus_de_discernement import lechelle_des_largeurs  # noqa: E402
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20260919
DECALAGES = 12
CONTRASTE_DE_LA_FIXTURE = 0.5
PLIS_DE_LA_FIXTURE = 2


def les_largeurs_du_creux(minimum: int = COUCHES_MINIMALES) -> list[int]:
    """Les largeurs de creux balayées — DÉRIVÉES, et la première est exclue pour une raison.

    ⭐⭐⭐⭐ UN CREUX D'UNE SEULE COUCHE NE PEUT PORTER AUCUN EXCÉDENT, ET C'EST UN THÉORÈME, PAS UNE
    PRÉCAUTION. Le creux le plus profond d'une seule couche vaut un moins le minimum divisé par la
    moyenne du reste : il ne dépend que du MULTIENSEMBLE des cohérences, donc une permutation le
    laisse EXACTEMENT inchangé. C'est le NUL de cet estimateur, le pendant exact de l'ajustement
    constant de `177`, et une première version qui le laissait concourir n'a rien trouvé nulle part
    — le maximum tombait toujours sur lui et son excédent était nul par construction.

    ⭐⭐⭐⭐ CE QUI DISTINGUE UNE FRONTIÈRE D'UNE COUCHE FAIBLE EST DONC LA CONTIGUÏTÉ. Deux feuilles
    qui se recouvrent creusent une SUITE de couches ; une cohérence basse isolée est du bruit. Une
    moyenne sur trois couches consécutives dépend de l'ordre, donc le mélange la détruit, donc la
    permutation la price.

    ⚠⚠ ET LE DERNIER BARREAU SE DÉRIVE : `178` a dérivé qu'une frontière doit laisser
    `COUCHES_MINIMALES` couches derrière elle, parce que `174` refuse une tranche plus courte. Un
    creux large de `2·minimum − 1` mange déjà tout le segment minimal des deux côtés.

    ⚠ Les largeurs sont IMPAIRES : une frontière est une position, pas un intervalle.
    """
    return list(range(3, 2 * int(minimum), 2))


def le_creux_nul(coherences) -> dict | None:
    """Le creux d'UNE SEULE couche — exactement invariant par permutation.

    ⭐⭐⭐⭐ IL EST LE NUL, ET IL EST RENDU À CÔTÉ PLUTÔT QUE SUPPRIMÉ : sans lui, « la cohérence
    descend à 0,08 » ne dit pas si elle y descend sur une suite de couches ou sur une seule. Sa
    position bouge au mélange, sa PROFONDEUR non, et c'est cette profondeur qui est le nul.

    ⚠ Aucune contrainte de bord ne s'applique : une couche isolée ne prétend séparer personne, donc
    lui interdire les bords en ferait une statistique que la permutation ne conserve plus.
    """
    c = np.asarray([float(x) for x in coherences], dtype=float)
    n = int(len(c))
    if n < 2:
        return None
    k = int(np.argmin(c))
    dehors = float(c.sum() - c[k]) / float(n - 1)
    if dehors <= 0.0:
        return None
    return {"profondeur": round(1.0 - float(c[k]) / dehors, 4), "couche": int(k)}


def le_creux(coherences, largeur: int, largeur_de_fenetre: int | None = None,
             minimum: int = COUCHES_MINIMALES) -> dict | None:
    """Le creux le plus PROFOND de cette largeur : sa couche et ce qu'il enlève.

    ⭐⭐⭐⭐ LA PROFONDEUR EST UNE PART, DONC ELLE SE COMPARE SANS SEUIL : un moins le rapport de la
    cohérence moyenne DEDANS à la cohérence moyenne DEHORS. Elle vaut zéro sur une courbe plate,
    tend vers un quand la cohérence s'effondre, et elle est sans unité — donc la même quantité sur
    une fixture dont la cohérence vaut un et sur un rouleau où elle vaut moins.

    ⚠⚠⚠ C'EST UNE MINIMISATION DÉGUISÉE EN MAXIMISATION, ET ELLE TROUVE TOUJOURS QUELQUE CHOSE.
    Rien ici ne dit qu'un creux trouvé est une frontière ; c'est `contre_les_melanges` qui price la
    liberté de l'avoir cherché sur toutes les positions.

    ⚠ Le centre laisse `minimum` couches de chaque côté, par la règle de `178` : un creux collé au
    bord ne sépare rien. Les égalités se tranchent par la couche puis le départ les plus petits,
    pour que deux exécutions rendent le même creux.

    ⚠⚠ `largeur_de_fenetre` change ce que « DEHORS » veut dire, et rien d'autre : une fenêtre
    étroite compare le creux à ses voisines proches, la courbe entière le compare à tout. Toutes les
    fenêtres sont balayées, et le mélange subit le même balayage.
    """
    c = np.asarray([float(x) for x in coherences], dtype=float)
    n = int(len(c))
    L = n if largeur_de_fenetre is None else int(largeur_de_fenetre)
    if L > n or L < 2 * int(minimum) + 1:
        return None
    w, h = int(largeur), int(largeur) // 2
    ks = np.arange(int(minimum), L - int(minimum))
    if ks.size == 0:
        return None
    P = np.concatenate([[0.0], np.cumsum(c)])
    departs = np.arange(0, n - L + 1)
    a = np.clip(departs[:, None] + ks[None, :] - h, departs[:, None], departs[:, None] + L)
    b = np.clip(departs[:, None] + ks[None, :] + h + 1, departs[:, None], departs[:, None] + L)
    dedans, nd = P[b] - P[a], (b - a).astype(float)
    total = (P[departs + L] - P[departs])[:, None]
    dehors, no = total - dedans, float(L) - nd
    ok = (nd > 0.0) & (no > 0.0) & (dehors > 0.0)
    prof = np.where(ok, 1.0 - (dedans / np.maximum(nd, 1.0)) / (dehors / np.maximum(no, 1.0)),
                    -np.inf)
    meilleur = float(prof.max())
    if not np.isfinite(meilleur):
        return None
    di, ki = np.nonzero(prof == meilleur)
    couches_abs = departs[di] + ks[ki]
    # ⚠ Egalites tranchees par la couche la plus petite puis le depart le plus petit : deux
    # executions doivent rendre le meme creux, sinon un detail d'ordre deviendrait un resultat.
    j = int(np.lexsort((departs[di], couches_abs))[0])
    d, k = int(departs[di[j]]), int(ks[ki[j]])
    aa, bb = max(d, d + k - h), min(d + L, d + k + h + 1)
    return {"couches": n, "largeur": w,
            "largeur_de_fenetre": (None if largeur_de_fenetre is None else L),
            "profondeur": round(meilleur, 4), "couche": int(d + k), "depart": d,
            "coherence_dedans": round(float(c[aa:bb].mean()), 4),
            "coherence_dehors": round(float((total[di[j], 0] - (P[bb] - P[aa]))
                                            / max(1.0, float(L - (bb - aa)))), 4)}


def contre_les_melanges(coherences, largeur_de_fenetre: int | None = None,
                        permutations: int = PERMUTATIONS, graine: int = GRAINE,
                        largeurs=None, minimum: int = COUCHES_MINIMALES,
                        une_seule_largeur: int | None = None,
                        sans_payer_la_largeur: bool = False) -> dict:
    """Le creux contre ses mélanges, LA LIBERTÉ DE CHOISIR LA LARGEUR COMPRISE.

    ⭐⭐⭐⭐ MÉLANGER CONSERVE LE MULTIENSEMBLE DES COHÉRENCES, donc conserve exactement la liberté
    de chercher le creux le plus profond sur toutes les positions, et ne détruit que la
    CONTIGUÏTÉ. Ce que la différence mesure est donc la part du creux qui vient de la profondeur.

    ⚠⚠⚠ MAIS LA LARGEUR EST UNE SECONDE LIBERTÉ, ET UNE PREMIÈRE VERSION NE LA PAYAIT PAS. Elle
    prenait la meilleure des trois largeurs après que chacune eut battu ses propres mélanges : trois
    chances à un sur vingt au lieu d'une. Mesuré sur deux cents cohérences tirées au hasard, le taux
    de fausses frontières sortait à **0,1** pour une garantie de **0,05** — exactement le double,
    et pas un accident d'échantillonnage.

    ⭐⭐⭐⭐ LA RÉPARATION EST UNE STATISTIQUE DE FAMILLE, ET ELLE EST EXACTE. On ne compare plus
    largeur par largeur mais le MAXIMUM sur les largeurs de l'excédent, et le même maximum est
    calculé pour chaque mélange pris à son tour comme s'il était le réel — sa médiane de référence
    étant alors celle des AUTRES mélanges. La liberté de choisir la largeur est ainsi subie à
    l'identique par le réel et par chaque mélange, donc payée.

    ⚠⚠ `sans_payer_la_largeur` PORTE LA RÈGLE RÉFUTÉE comme contrôle nommé — chaque largeur contre
    ses propres mélanges, une seule suffit — parce qu'une réparation qu'aucune mesure n'exerce est
    une précaution dont personne ne sait ce qu'elle achète. `177` a payé ce piège : le taux des deux
    règles est mesuré côte à côte, et c'est l'écart qui est le résultat.

    ⚠ `une_seule_largeur` mesure la même chose par l'autre bout : une famille d'un seul membre n'a
    aucune liberté à payer, donc son taux doit retomber sur la garantie. Ni l'un ni l'autre n'est le
    chemin du verdict.
    """
    c = np.asarray([float(x) for x in coherences], dtype=float)
    largeurs = ([int(une_seule_largeur)] if une_seule_largeur is not None
                else (list(largeurs) if largeurs is not None else les_largeurs_du_creux(minimum)))
    melanges = [c[np.random.default_rng(int(graine) + t).permutation(len(c))]
                for t in range(int(permutations))]
    reels, tirees = {}, {}
    for w in largeurs:
        reel = le_creux(c, w, largeur_de_fenetre, minimum)
        if reel is None:
            continue
        lus = [le_creux(m, w, largeur_de_fenetre, minimum) for m in melanges]
        if any(x is None for x in lus):
            continue
        reels[w] = reel
        tirees[w] = [float(x["profondeur"]) for x in lus]
    if not reels:
        return {"decidable": False, "raison": "aucune largeur ne se prononce",
                "permutations": int(permutations), "par_largeur": []}

    def mediane(valeurs):
        return float(statistics.median(valeurs)) if valeurs else 0.0

    par_largeur = [{**reels[w],
                    "profondeur_mediane_des_melanges": round(mediane(tirees[w]), 4),
                    "profondeur_maximale_des_melanges": round(float(max(tirees[w])), 4),
                    "excedent": round(float(reels[w]["profondeur"]) - mediane(tirees[w]), 4)}
                   for w in sorted(reels)]
    statistique = max(float(reels[w]["profondeur"]) - mediane(tirees[w]) for w in reels)
    des_melanges = [max(tirees[w][j] - mediane(tirees[w][:j] + tirees[w][j + 1:]) for w in reels)
                    for j in range(int(permutations))]
    # ⚠ Egalites tranchees par la largeur la plus petite : deux executions doivent retenir la meme.
    retenue = max(par_largeur, key=lambda x: (x["excedent"], -x["largeur"]))
    paye = bool(all(statistique > x for x in des_melanges))
    sans_payer = bool(any(all(float(reels[w]["profondeur"]) > x for x in tirees[w])
                          for w in reels))
    return {"decidable": True, "par_largeur": par_largeur, "le_nul": le_creux_nul(c),
            "largeurs_lues": sorted(reels), "permutations": int(permutations),
            "statistique": round(float(statistique), 4),
            "statistique_maximale_des_melanges": round(float(max(des_melanges)), 4),
            "statistique_mediane_des_melanges": round(mediane(des_melanges), 4),
            "depasse_tous_les_melanges": bool(sans_payer if sans_payer_la_largeur else paye),
            "depasse_en_payant_la_largeur": paye,
            "depasse_sans_payer_la_largeur": sans_payer,
            "profondeur": retenue["profondeur"], "couche": retenue["couche"],
            "largeur": retenue["largeur"], "depart": retenue["depart"],
            "excedent": retenue["excedent"],
            "profondeur_mediane_des_melanges": retenue["profondeur_mediane_des_melanges"]}


def le_verdict_du_creux(courbe, largeur_de_fenetre: int | None = None,
                        permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """« Empilement » quand une largeur dépasse TOUS ses mélanges, « rien » sinon.

    ⚠⚠ IL N'Y A QUE DEUX RÉPONSES POSSIBLES, ET C'EST UNE LIMITE, PAS UNE ÉCONOMIE. Ce lecteur
    détecte une frontière ; il ne sait pas dire qu'une matière tourne. Une rotation et du bruit lui
    rendent tous deux « rien », et c'est `177` qui les sépare.
    """
    lu = contre_les_melanges([x[1] for x in courbe], largeur_de_fenetre, permutations, graine)
    trouve = bool(lu.get("decidable") and lu.get("depasse_tous_les_melanges"))
    return {**lu, "gagnant": ("empilement" if trouve else None),
            "frontiere_lue": (lu["couche"] if trouve else None)}


def le_verdict_joint(courbe, largeur_de_fenetre: int | None = None,
                     permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Les DEUX lecteurs ensemble : le creux dit s'il y a une frontière, le tour dit si ça tourne.

    ⭐⭐⭐⭐ C'EST LA SEULE COMPOSITION QUI RÉPOND À `R4-P31`. `178` a montré qu'aucune largeur ne
    donne les deux réponses avec le tour accumulé seul, parce que les deux moitiés sont la même
    quantité. Le creux ne passe pas par le tour, donc il n'est pas soumis à cet échange.

    ⚠⚠ LA RÈGLE EST ÉCRITE UNE FOIS ET ELLE NE PORTE AUCUN SEUIL : une frontière lue fait un
    empilement ; sinon, ce que `177` rend fait foi. Elle peut se tromper, et les trois matières
    construites plus le tableau de `178` sont là pour mesurer de combien.
    """
    creux = le_verdict_du_creux(courbe, largeur_de_fenetre, permutations, graine)
    tour = le_verdict(courbe, largeur_de_fenetre, permutations, graine)
    if creux["gagnant"] == "empilement":
        joint = "empilement"
    elif tour["gagnant"] == "derive":
        joint = "rotation"
    elif tour["gagnant"] == "marche":
        joint = "empilement"
    else:
        joint = None
    return {"le_creux": creux, "le_tour": tour, "gagnant": joint,
            "par_le_tour_seul": ("empilement" if tour["gagnant"] == "marche"
                                 else ("rotation" if tour["gagnant"] == "derive" else None)),
            "les_deux_lecteurs_saccordent": bool(
                (creux["gagnant"] == "empilement") == (tour["gagnant"] == "marche"))}


# ------------------------------------------------------------------ le chemin physique

def les_frontieres_de_la_fixture(couches: int, decalage_um: float, plis: int,
                                 voxel_um: float, pas_um: float,
                                 minimum: int = COUCHES_MINIMALES) -> list[int]:
    """Les couches où la fixture change de pli — la réponse CONNUE avant la mesure.

    ⚠ Elles sont dérivées du pas, du nombre de plis et du décalage, jamais lues dans la courbe :
    une frontière relue dans la mesure qu'on met à l'épreuve ne contrôle rien.

    ⚠⚠ Seules comptent celles que l'estimateur peut atteindre, par la règle de `178` : un creux
    centré à moins de `minimum` couches d'un bord ne sépare rien, donc une frontière posée là
    n'est pas trouvable et l'exiger serait demander l'impossible.
    """
    epaisseur = float(pas_um) / float(plis)
    fr = []
    j = int(np.floor(float(decalage_um) / epaisseur))
    while True:
        k = (j * epaisseur - float(decalage_um)) / float(voxel_um)
        j += 1
        if k >= float(couches):
            break
        if k < 0.0:
            continue
        i = int(round(k))
        if int(minimum) <= i < int(couches) - int(minimum):
            fr.append(i)
    return fr


def lechelle_des_recouvrements(voxel_um: float, pas_um: float, plis: int) -> list[float]:
    """Les épaisseurs de recouvrement balayées, en micromètres — DÉRIVÉES du voxel.

    ⚠⚠ LE RASOIR EST LE PREMIER BARREAU, et il est la matière que tout le dépôt a lue jusqu'ici :
    sans lui, le tableau ne dirait pas que la prémisse était fausse.

    ⚠ Ensuite on double depuis un QUART de voxel — donc de part et d'autre du pas
    d'échantillonnage, qui est la seule longueur que l'instrument impose — et on s'arrête avant
    l'épaisseur d'un pli, que la fixture refuse.
    """
    echelle, x = [0.0], float(voxel_um) / 4.0
    limite = float(pas_um) / float(plis)
    while x < limite:
        echelle.append(round(x, 4))
        x *= 2.0
    return echelle


def le_tour_porte(couches: int, voxel_um: float, pas_um: float) -> float:
    """Le tour total qu'une fenêtre traverse — et il NE DÉPEND PAS du nombre de plis.

    ⭐⭐⭐⭐ C'EST CE QUI REND LES DEUX MATIÈRES DE L'ÉCHANGE COMPARABLES, et c'est une identité, pas
    un réglage. Les angles des plis d'une feuille sont équirépartis sur 180°, donc `P` plis font
    `180/P` degrés par frontière et une frontière tous les `pas/P` micromètres. Une fenêtre de `d`
    micromètres en traverse `d·P/pas`, donc elle tourne de `d·180/pas` — le `P` s'annule.

    ⚠ La fonction ne prend donc PAS le nombre de plis en argument : si elle le prenait, on pourrait
    croire que le tour en dépend.
    """
    return float(couches) * float(voxel_um) * 180.0 / float(pas_um)


def les_plis_dune_rotation(voxel_um: float, pas_um: float) -> int:
    """Combien de plis rendent un escalier INDISCERNABLE d'une rotation, pour CET instrument.

    ⭐⭐⭐⭐ LA BORNE SE DÉRIVE DU PAS D'ÉCHANTILLONNAGE, ELLE N'EST PAS CHOISIE. Un escalier n'est
    lisible comme escalier que si une couche tient à l'intérieur d'un pli. Dès que l'épaisseur d'un
    pli tombe au niveau du voxel, aucune couche n'est plus strictement dedans : l'instrument ne peut
    plus voir de marche, et ce qu'il voit est une orientation qui avance d'un peu à chaque couche.
    C'est la définition opératoire d'une rotation, et elle ne doit rien à un seuil.
    """
    return int(np.ceil(float(pas_um) / float(voxel_um)))


def sur_la_fixture(transitions, plis: int = PLIS_DE_LA_FIXTURE, bruit: float = 0.0,
                   decalages: int = DECALAGES, permutations: int = PERMUTATIONS,
                   graine: int = GRAINE) -> dict:
    """Le creux lu sur la fixture, par le MÊME chemin que le rouleau.

    ⭐⭐⭐⭐ C'EST LA PRÉMISSE, ET ELLE SE MESURE AU LIEU DE S'AFFIRMER. La matière traverse
    `VolumeFabriqueAFibres` puis `orientation_profile` : la cohérence n'est pas construite, elle est
    ce qu'un tenseur de structure rend sur des fibres qui se recouvrent.

    ⚠⚠ ON COMPTE LES DÉCALAGES OÙ LE CREUX TOMBE SUR UNE FRONTIÈRE CONSTRUITE, pas une moyenne :
    `173` a mesuré qu'une lecture qui ne marche qu'à un décalage sur deux est une loterie, et la
    phase de la fenêtre dans la feuille n'est pas connue sur données réelles.

    ⚠ `plis=1` est le CONTRÔLE VIDE de toute cette famille : une feuille d'un seul pli n'a aucune
    frontière d'orientation, donc aucun creux à rendre. Un recouvrement y est un recouvrement entre
    deux plis de MÊME direction, ce qui ne creuse rien — et c'est mesuré, pas supposé.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    lignes = []
    for tr in transitions:
        justes, trouves, profondeurs, largeurs, ecarts = 0, 0, [], [], []
        for k in range(int(decalages)):
            dec = pas * k / float(decalages)
            courbe = courbe_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, dec, CONTRASTE_DE_LA_FIXTURE,
                                          int(plis), vx, pas, transition_um=float(tr),
                                          bruit=float(bruit))
            attendues = les_frontieres_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, dec, int(plis),
                                                     vx, pas)
            v = le_verdict_du_creux(courbe, None, permutations, graine)
            if v["gagnant"] is None:
                continue
            trouves += 1
            profondeurs.append(float(v["profondeur"]))
            largeurs.append(int(v["largeur"]))
            if attendues:
                ecart = min(abs(int(v["frontiere_lue"]) - x) for x in attendues)
                ecarts.append(int(ecart))
                justes += int(ecart <= int(v["largeur"]) // 2 + 1)
        lignes.append({"transition_um": round(float(tr), 4),
                       "transition_en_couches": round(float(tr) / vx, 3),
                       "plis": int(plis), "decalages": int(decalages),
                       "creux_trouves": int(trouves),
                       "sans_creux": int(decalages) - int(trouves),
                       "creux_sur_une_frontiere": int(justes),
                       "lue_a_tous_les_decalages": bool(justes == int(decalages)),
                       "profondeur_mediane": (round(float(statistics.median(profondeurs)), 4)
                                              if profondeurs else None),
                       "largeur_mediane": (int(statistics.median_low(largeurs))
                                           if largeurs else None),
                       "ecart_median_en_couches": (int(statistics.median_low(ecarts))
                                                   if ecarts else None)})
    lisibles = [x for x in lignes if x["lue_a_tous_les_decalages"]]
    plus_petite = min((x["transition_um"] for x in lisibles), default=None)
    retenue = next((x for x in lisibles if x["transition_um"] == plus_petite), None)
    compte = [x["creux_sur_une_frontiere"] for x in lignes]
    return {"plis": int(plis), "bruit": float(bruit), "lignes": lignes,
            "le_compte_monte_avec_le_recouvrement": bool(
                all(a <= b for a, b in zip(compte, compte[1:]))),
            "creux_trouves_en_tout": int(sum(x["creux_trouves"] for x in lignes)),
            "le_rasoir_ne_creuse_pas": bool(
                any(x["transition_um"] == 0.0 and x["creux_sur_une_frontiere"] == 0
                    for x in lignes)),
            "la_plus_petite_transition_lisible_um": plus_petite,
            "elle_vaut_le_voxel_fois": (round(plus_petite / vx, 3)
                                        if plus_petite is not None else None),
            "profondeur_a_cette_transition": (retenue["profondeur_mediane"] if retenue else None),
            "largeur_a_cette_transition": (retenue["largeur_mediane"] if retenue else None)}


def la_transition_juste_suffisante(transitions, decalages: int = DECALAGES,
                                   permutations: int = PERMUTATIONS,
                                   graine: int = GRAINE) -> dict:
    """La plus petite épaisseur de recouvrement lue à TOUS les décalages, affinée par bissection.

    ⭐⭐⭐⭐ UN BARREAU D'ÉCHELLE N'EST PAS UNE BORNE. Le balayage rend le plus petit barreau qui
    passe, et l'échelle double : dire que le recouvrement doit valoir ce barreau serait confondre la
    borne avec la résolution du balayage. On encadre donc entre le dernier barreau qui échoue et le
    premier qui passe, puis on bissecte.

    ⚠⚠ LA TOLÉRANCE EST DÉRIVÉE, PAS CHOISIE : on s'arrête quand l'encadrement passe sous le VOXEL.
    En dessous du pas d'échantillonnage, deux recouvrements ne sont pas distinguables par
    l'instrument, donc affiner davantage rendrait un chiffre que rien ne porte.

    ⚠ La bissection suppose que le compte MONTE avec le recouvrement, et cette monotonie est
    mesurée sur l'échelle entière plutôt que supposée : `sur_la_fixture` la publie.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx = float(C.VOXEL_FIN_UM)
    lisibles = [x["transition_um"] for x in transitions["lignes"] if x["lue_a_tous_les_decalages"]]
    if not lisibles:
        return {"encadree": False, "raison": "aucun barreau n'est lu à tous les décalages"}
    haut = float(min(lisibles))
    dessous = [x["transition_um"] for x in transitions["lignes"]
               if not x["lue_a_tous_les_decalages"] and x["transition_um"] < haut]
    bas = float(max(dessous)) if dessous else 0.0
    pas_lus = 0
    while haut - bas > vx:
        milieu = 0.5 * (bas + haut)
        r = sur_la_fixture([milieu], PLIS_DE_LA_FIXTURE, 0.0, decalages, permutations, graine)
        pas_lus += 1
        if r["lignes"][0]["lue_a_tous_les_decalages"]:
            haut = milieu
        else:
            bas = milieu
    # ⚠⚠ LA PROFONDEUR ET LA LARGEUR SE LISENT A LA BORNE, PAS AU BARREAU. Les rendre au plus petit
    # barreau de l'echelle alors que la borne est ailleurs publierait deux nombres qui ne parlent
    # pas de la meme matiere, sous des noms qui suggerent qu'ils le font.
    a_la_borne = sur_la_fixture([haut], PLIS_DE_LA_FIXTURE, 0.0, decalages, permutations,
                                graine)["lignes"][0]
    return {"encadree": True, "bas_um": round(bas, 3), "haut_um": round(haut, 3),
            "bissections": int(pas_lus), "tolerance_um": vx,
            "profondeur_a_la_borne": a_la_borne["profondeur_mediane"],
            "largeur_a_la_borne": a_la_borne["largeur_mediane"],
            "ecart_median_a_la_borne": a_la_borne["ecart_median_en_couches"],
            "la_monotonie_tient": transitions["le_compte_monte_avec_le_recouvrement"]}


def les_profils(recouvrements, decalage_um: float = 0.0, plis: int = PLIS_DE_LA_FIXTURE,
                permutations: int = PERMUTATIONS, graine: int = GRAINE) -> list:
    """Les courbes de cohérence elles-mêmes, pour qu'une figure MONTRE ce que les comptes disent.

    ⚠ Elles sont produites par la mesure et non par la figure : une figure qui recalculerait la
    matière dessinerait quelque chose d'autre que ce que le document publie, et rien ne le dirait.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    sorties = []
    for tr in recouvrements:
        courbe = courbe_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, float(decalage_um),
                                      CONTRASTE_DE_LA_FIXTURE, int(plis), vx, pas,
                                      transition_um=float(tr))
        v = le_verdict_du_creux(courbe, None, permutations, graine)
        sorties.append({"transition_um": round(float(tr), 3),
                        "transition_en_couches": round(float(tr) / vx, 3),
                        "decalage_um": round(float(decalage_um), 3),
                        "coherences": [round(float(x[1]), 4) for x in courbe],
                        "frontieres_construites": les_frontieres_de_la_fixture(
                            COUCHES_DE_LA_CAMPAGNE, float(decalage_um), int(plis), vx, pas),
                        "gagnant": v["gagnant"], "frontiere_lue": v["frontiere_lue"],
                        "profondeur": v.get("profondeur"), "largeur": v.get("largeur")})
    return sorties


def le_domaine_de_bruit(transition_um: float, bruits=BRUITS, decalages: int = DECALAGES,
                        permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Jusqu'à quel bruit le creux tombe-t-il encore sur la frontière construite ?

    ⚠ L'échelle de bruit est celle de `156`, IMPORTÉE et non réécrite : c'est là que trois pertes
    ont déjà été mesurées, donc c'est l'échelle sur laquelle cette question a déjà un précédent.
    """
    lignes = []
    for b in bruits:
        r = sur_la_fixture([float(transition_um)], PLIS_DE_LA_FIXTURE, float(b), decalages,
                           permutations, graine)
        lignes.append({"bruit": float(b), **r["lignes"][0]})
    tenus = [x["bruit"] for x in lignes if x["lue_a_tous_les_decalages"]]
    return {"transition_um": float(transition_um), "bruits": [float(x) for x in bruits],
            "lignes": lignes,
            "le_plus_grand_bruit_tenu": (max(tenus) if tenus else None),
            "tient_au_bruit_de_156": bool(lignes and lignes[-1]["lue_a_tous_les_decalages"])}


def les_tirages_du_taux(permutations: int = PERMUTATIONS) -> int:
    """Combien de cohérences tirées au hasard pour qu'un taux MESURÉ veuille dire quelque chose.

    ⚠⚠ DÉRIVÉ, PAS CHOISI. La garantie vaut `p = 1/(m+1)`. L'erreur type d'un taux mesuré sur `n`
    tirages vaut `√(p(1−p)/n)`, et on exige qu'elle tombe sous la MOITIÉ de la garantie : sinon un
    taux mesuré ne peut pas être distingué de zéro ni du double, et le publier serait publier du
    bruit. Cela donne `n ≥ 4(1−p)/p`, arrondi au multiple supérieur de `m+1` parce qu'un taux se lit
    au grain de la garantie.
    """
    p = 1.0 / float(int(permutations) + 1)
    bloc = int(permutations) + 1
    return int(np.ceil(np.ceil(4.0 * (1.0 - p) / p) / bloc) * bloc)


def le_taux_sur_du_bruit(graines: int | None = None, permutations: int = PERMUTATIONS,
                         graine: int = GRAINE, une_seule_largeur: int | None = None) -> dict:
    """Combien de fois une cohérence TIRÉE AU HASARD porte un creux qui dépasse ses mélanges."""
    """Combien de fois une cohérence TIRÉE AU HASARD porte un creux qui dépasse ses mélanges.

    ⭐⭐⭐⭐ CE TAUX EST LA GARANTIE DE LA PERMUTATION, MESURÉE AU LIEU D'ÊTRE INVOQUÉE. Sous
    échange, la probabilité qu'une valeur réelle dépasse strictement ses `m` mélanges vaut au plus
    `1/(m+1)`, soit un sur vingt ici. Une seule matière de bruit est donc une pièce à vingt faces :
    une première version l'a tirée une fois, a obtenu un faux positif, et le contrôle aurait été
    déclaré en échec pour la raison exactement inverse de la bonne.

    ⚠⚠ CE QUI SE MESURE EST DONC UN TAUX, et ce qui s'asserte est une COMPARAISON : le bruit doit
    rendre strictement moins de frontières qu'une matière qui en porte une. Un taux comparé à un
    nombre choisi serait un seuil.
    """
    graines = les_tirages_du_taux(permutations) if graines is None else int(graines)
    faux, sans = 0, 0
    for g in range(int(graines)):
        r = np.random.default_rng(int(graine) + 7919 * g)
        courbe = [[float(a), float(c)] for a, c in zip(
            r.uniform(0.0, 180.0, COUCHES_DE_LA_CAMPAGNE),
            r.uniform(0.0, 1.0, COUCHES_DE_LA_CAMPAGNE))]
        lu = contre_les_melanges([x[1] for x in courbe], None, permutations, graine,
                                 une_seule_largeur=une_seule_largeur)
        if not lu.get("decidable"):
            continue
        faux += int(bool(lu["depasse_en_payant_la_largeur"]))
        sans += int(bool(lu["depasse_sans_payer_la_largeur"]))
    return {"tirages": int(graines), "faux_positifs": int(faux),
            "faux_positifs_sans_payer_la_largeur": int(sans),
            "une_seule_largeur": une_seule_largeur,
            "taux_mesure": round(float(faux) / float(graines), 4),
            "taux_sans_payer_la_largeur": round(float(sans) / float(graines), 4),
            "ce_que_la_permutation_garantit": round(1.0 / float(int(permutations) + 1), 4),
            "payer_la_largeur_ramene_sous_la_garantie": bool(
                float(faux) / float(graines) <= 1.0 / float(int(permutations) + 1)
                < float(sans) / float(graines))}


def lechange(largeurs, plis_grossiers: int, plis_fins: int, recouvrement_grossier_um: float,
             bruits=BRUITS, decalages: int = DECALAGES, permutations: int = PERMUTATIONS,
             graine: int = GRAINE) -> list:
    """L'échange de `178`, remis à l'épreuve SUR LE CHEMIN PHYSIQUE, par les deux lecteurs.

    ⭐⭐⭐⭐ LES DEUX MATIÈRES SONT DE LA MÊME FAMILLE ET PORTENT LE MÊME TOUR TOTAL. Un escalier
    grossier — deux plis par feuille, une frontière tous les trente-six couches — et un escalier si
    fin que l'instrument ne peut plus y voir de marche. `le_tour_porte` démontre qu'ils tournent
    exactement autant, donc ce qui les sépare est la RÉPARTITION du tour et rien d'autre : c'est
    l'énoncé de `178`, cette fois sur une matière lue par `orientation_profile` et non construite.

    ⚠⚠⚠ ET C'EST CE QUI ÉVITE LA FIXTURE COMPLAISANTE. Une première version construisait un creux
    aux frontières de l'escalier et aucun sur la dérive : le lecteur les séparait alors par
    construction, et la mesure n'aurait rien dit. Ici personne ne pose de creux — la cohérence est
    ce que le tenseur de structure rend.

    ⚠⚠ LE RECOUVREMENT DU FIN EST LA MÊME FRACTION D'UN PLI que celui du grossier, jamais la même
    longueur : deux matières dont les plis n'ont pas la même épaisseur ne se comparent qu'à
    interpénétration relative égale.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    fraction = float(recouvrement_grossier_um) / (pas / float(plis_grossiers))
    recouvrement_fin = fraction * (pas / float(plis_fins))
    sorties = []
    for largeur in largeurs:
        fenetre = None if int(largeur) >= COUCHES_DE_LA_CAMPAGNE else int(largeur)
        for b in bruits:
            compte = {"empilement": {"tour": 0, "joint": 0, "creux": 0},
                      "rotation": {"tour": 0, "joint": 0, "creux": 0}}
            for k in range(int(decalages)):
                dec = pas * k / float(decalages)
                for attendu, plis, tr in (("empilement", int(plis_grossiers),
                                           float(recouvrement_grossier_um)),
                                          ("rotation", int(plis_fins), float(recouvrement_fin))):
                    courbe = courbe_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, dec,
                                                  CONTRASTE_DE_LA_FIXTURE, plis, vx, pas,
                                                  transition_um=tr, bruit=float(b))
                    v = le_verdict_joint(courbe, fenetre, permutations, graine)
                    compte[attendu]["tour"] += int(v["par_le_tour_seul"] == attendu)
                    compte[attendu]["joint"] += int(v["gagnant"] == attendu)
                    compte[attendu]["creux"] += int(v["le_creux"]["gagnant"] == "empilement")
            sorties.append({
                "largeur": int(largeur),
                "en_plis": int(round(float(largeur) * vx / (pas / float(plis_grossiers)))),
                "lit_toute_la_profondeur": bool(fenetre is None), "bruit": float(b),
                "lectures_par_matiere": int(decalages),
                "recouvrement_grossier_um": round(float(recouvrement_grossier_um), 3),
                "recouvrement_fin_um": round(recouvrement_fin, 4),
                "empilement_par_le_tour": compte["empilement"]["tour"],
                "empilement_par_les_deux": compte["empilement"]["joint"],
                "rotation_par_le_tour": compte["rotation"]["tour"],
                "rotation_par_les_deux": compte["rotation"]["joint"],
                "creux_lus_sur_lempilement": compte["empilement"]["creux"],
                "creux_lus_sur_la_rotation": compte["rotation"]["creux"],
                # ⚠⚠⚠ « LES DEUX » EST LA SEULE LIGNE QUI COMPTE, et elle est exigeante : la
                # largeur doit rendre l'empilement ET la rotation a TOUS les decalages. `178` a
                # mesure qu'aucune largeur ne le fait par le tour seul ; c'est cet enonce-la qui
                # est remis a l'epreuve, pas une majorite.
                "le_tour_seul_donne_les_deux": bool(
                    compte["empilement"]["tour"] == int(decalages)
                    and compte["rotation"]["tour"] == int(decalages)),
                "les_deux_lecteurs_donnent_les_deux": bool(
                    compte["empilement"]["joint"] == int(decalages)
                    and compte["rotation"]["joint"] == int(decalages))})
    return sorties


def juger(fixture: dict, encadrement: dict, vide: dict, domaine: dict, bruit: dict,
          echange: list, pli: int, voxel_um: float) -> dict:
    """Ce que le creux ajoute, ce qu'il COÛTE, et ce qu'il exige de la matière.

    ⚠⚠⚠ LES CELLULES SONT RENDUES DANS LES DEUX SENS, et ce n'est pas une précaution. La lecture
    jointe gagne des cases que le tour seul n'avait pas, et elle en PERD une : sur une matière
    exactement sans bruit, un escalier fin porte des micro-creux parfaitement contigus qu'aucun
    mélange ne reproduit, donc le creux y voit une frontière qui n'en est pas. Ne publier que les
    cases gagnées ferait lire un échange comme un gain, ce qui est exactement le reproche que `178`
    adresse à la voie précédente.
    """
    cellule = (lambda x: [int(x["largeur"]), float(x["bruit"])])
    par_le_tour_c = [cellule(x) for x in echange if x["le_tour_seul_donne_les_deux"]]
    donnent_c = [cellule(x) for x in echange if x["les_deux_lecteurs_donnent_les_deux"]]
    gagnees = [c for c in donnent_c if c not in par_le_tour_c]
    perdues = [c for c in par_le_tour_c if c not in donnent_c]
    bruitees = [x for x in echange if float(x["bruit"]) > 0.0]
    donnent = sorted({x["largeur"] for x in echange if x["les_deux_lecteurs_donnent_les_deux"]})
    par_le_tour = sorted({x["largeur"] for x in echange if x["le_tour_seul_donne_les_deux"]})
    juste = encadrement.get("haut_um")
    epaisseur = float(pli) * float(voxel_um)
    return {"decidable": bool(fixture["le_rasoir_ne_creuse_pas"] and encadrement.get("encadree")),
            "raison": (None if encadrement.get("encadree")
                       else "aucun recouvrement ne rend le creux lisible à tous les décalages"),
            "le_rasoir_ne_creuse_pas": fixture["le_rasoir_ne_creuse_pas"],
            "le_compte_monte_avec_le_recouvrement":
                fixture["le_compte_monte_avec_le_recouvrement"],
            "le_recouvrement_juste_suffisant_um": juste,
            "encadre_entre_um": ([encadrement.get("bas_um"), encadrement.get("haut_um")]
                                 if encadrement.get("encadree") else None),
            "il_vaut_le_pli_fois": (round(juste / epaisseur, 4) if juste else None),
            "il_vaut_le_voxel_fois": (round(juste / float(voxel_um), 3) if juste else None),
            "profondeur_du_creux_a_la_borne": encadrement.get("profondeur_a_la_borne"),
            "largeur_du_creux_a_la_borne": encadrement.get("largeur_a_la_borne"),
            "ecart_median_a_la_borne": encadrement.get("ecart_median_a_la_borne"),
            "le_pli_unique_ne_creuse_jamais": bool(vide["creux_trouves_en_tout"] == 0),
            "le_plus_grand_bruit_tenu": domaine["le_plus_grand_bruit_tenu"],
            "tient_au_bruit_de_156": domaine["tient_au_bruit_de_156"],
            "faux_positifs_sur_du_bruit": bruit["faux_positifs"],
            "taux_sur_du_bruit": bruit["taux_mesure"],
            "taux_sans_payer_la_largeur": bruit["taux_sans_payer_la_largeur"],
            "ce_que_la_permutation_garantit": bruit["ce_que_la_permutation_garantit"],
            "payer_la_largeur_ramene_sous_la_garantie":
                bruit["payer_la_largeur_ramene_sous_la_garantie"],
            "largeurs_ou_le_tour_seul_donne_les_deux": par_le_tour,
            "largeurs_ou_les_deux_lecteurs_donnent_les_deux": donnent,
            "cellules_ou_le_tour_seul_donne_les_deux": par_le_tour_c,
            "cellules_ou_les_deux_donnent_les_deux": donnent_c,
            "cellules_gagnees_par_le_creux": gagnees,
            "cellules_perdues_par_le_creux": perdues,
            "cellules_en_tout": len(echange),
            "sur_matiere_bruitee_le_tour_seul_ne_donne_jamais_les_deux": bool(
                not any(x["le_tour_seul_donne_les_deux"] for x in bruitees)),
            "sur_matiere_bruitee_les_deux_donnent_les_deux": [
                cellule(x) for x in bruitees if x["les_deux_lecteurs_donnent_les_deux"]],
            "faux_creux_sur_un_escalier_fin_sans_bruit": int(sum(
                x["creux_lus_sur_la_rotation"] for x in echange if float(x["bruit"]) == 0.0)),
            "faux_creux_sur_un_escalier_fin_bruite": int(sum(
                x["creux_lus_sur_la_rotation"] for x in bruitees)),
            "une_largeur_donne_les_deux": bool(donnent),
            "le_creux_ajoute_des_cellules": bool(gagnees),
            "le_creux_en_coute_aussi": bool(perdues)}


def mesurer(graines: int = GRAINES_PAR_CELLULE, permutations: int = PERMUTATIONS,
            decalages: int = DECALAGES) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    pli = int(round(pas / float(PLIS_DE_LA_FIXTURE) / vx))
    transitions = lechelle_des_recouvrements(vx, pas, PLIS_DE_LA_FIXTURE)
    fixture = sur_la_fixture(transitions, PLIS_DE_LA_FIXTURE, 0.0, decalages, permutations)
    if fixture["la_plus_petite_transition_lisible_um"] is None:
        return {"message": "aucun recouvrement ne rend le creux lisible à tous les décalages",
                "la_fixture": fixture}
    encadrement = la_transition_juste_suffisante(fixture, decalages, permutations)
    juste = float(encadrement["haut_um"])
    # ⚠ LE CONTROLE VIDE, AUX MEMES RECOUVREMENTS : une feuille d'un seul pli n'a aucune frontiere
    # d'orientation, donc un recouvrement y est un recouvrement entre deux plis de MEME direction.
    # Le rasoir est retire de l'echelle parce qu'il ne creuse deja pas a deux plis : le garder
    # ferait passer ce controle pour une raison qui n'est pas la sienne.
    vide = sur_la_fixture([x for x in transitions if x > 0.0], 1, 0.0, decalages, permutations)
    # ⚠ Les trois profils dessines sont le rasoir, le dernier recouvrement qui ECHOUE, et la borne :
    # sans le rasoir on ne voit pas que la premisse etait fausse, sans l'echec on ne voit pas que
    # la borne est une borne.
    echoue = max((x["transition_um"] for x in fixture["lignes"]
                  if not x["lue_a_tous_les_decalages"] and x["transition_um"] < juste),
                 default=0.0)
    profils = les_profils([0.0, echoue, juste], 0.0, PLIS_DE_LA_FIXTURE, permutations)
    domaine = le_domaine_de_bruit(juste, BRUITS, decalages, permutations)
    bruit = le_taux_sur_du_bruit(None, permutations)
    plis_fins = les_plis_dune_rotation(vx, pas)
    echange = lechange(lechelle_des_largeurs(pli), PLIS_DE_LA_FIXTURE, plis_fins, juste,
                       BRUITS, decalages, permutations)
    return {"voxel_um": vx, "pas_um": pas, "pli_en_couches": pli,
            "couches": int(COUCHES_DE_LA_CAMPAGNE),
            "couches_minimales": int(COUCHES_MINIMALES),
            "largeurs_du_creux": les_largeurs_du_creux(),
            "recouvrements_um": transitions, "bruits": [float(x) for x in BRUITS],
            "plis_grossiers": int(PLIS_DE_LA_FIXTURE), "plis_fins": int(plis_fins),
            "tour_porte_deg": round(le_tour_porte(COUCHES_DE_LA_CAMPAGNE, vx, pas), 3),
            "permutations": int(permutations), "graine": int(GRAINE),
            "tirages_de_bruit": int(les_tirages_du_taux(permutations)), "decalages": int(decalages),
            "la_fixture": fixture, "lencadrement": encadrement, "le_pli_unique": vide,
            "les_profils": profils,
            "le_domaine": domaine, "le_bruit": bruit, "lechange": echange,
            "le_verdict": juger(fixture, encadrement, vide, domaine, bruit, echange, pli, vx)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    fx, d, b, v = r["la_fixture"], r["le_domaine"], r["le_bruit"], r["le_verdict"]
    print("LA COHÉRENCE CREUSE-T-ELLE À LA FRONTIÈRE ?")
    print(f"  {r['couches']} couches · un pli {r['pli_en_couches']} · voxel {r['voxel_um']} µm · "
          f"{r['decalages']} décalages · {r['permutations']} permutations")
    print(f"  la fenêtre porte {r['tour_porte_deg']}° de tour, à {r['plis_grossiers']} plis comme "
          f"à {r['plis_fins']}")
    print()
    print("  LE CHEMIN PHYSIQUE · deux plis, recouvrement par recouvrement")
    print(f"   {'recouvrement':>13} {'couches':>8} {'sur frontière':>14} {'profondeur':>11} "
          f"{'largeur':>8}  {'1 pli':>6}")
    vides = {x["transition_um"]: x for x in r["le_pli_unique"]["lignes"]}
    for x in fx["lignes"]:
        marque = "★" if x["lue_a_tous_les_decalages"] else " "
        w = vides.get(x["transition_um"])
        print(f"   {x['transition_um']:>13.4f} {x['transition_en_couches']:>8.3f} "
              f"{x['creux_sur_une_frontiere']:>10}/{x['decalages']:<3} "
              f"{str(x['profondeur_mediane']):>11} {str(x['largeur_mediane']):>8}  "
              f"{(str(w['creux_trouves']) + '/' + str(w['decalages'])) if w else '—':>6} {marque}")
    print(f"     encadrement {v['encadre_entre_um']} µm en {r['lencadrement']['bissections']} "
          f"bissections · tolérance {r['lencadrement']['tolerance_um']} µm")
    print()
    print("  LE DOMAINE DE BRUIT · l'échelle de `156`")
    for x in d["lignes"]:
        print(f"   bruit {x['bruit']:>5.1f} · sur frontière {x['creux_sur_une_frontiere']}"
              f"/{x['decalages']} · profondeur {x['profondeur_mediane']} "
              f"{'★' if x['lue_a_tous_les_decalages'] else '✗'}")
    print(f"   du bruit pur : {b['faux_positifs']}/{b['tirages']} = {b['taux_mesure']} en payant "
          f"la largeur · {b['faux_positifs_sans_payer_la_largeur']}/{b['tirages']} = "
          f"{b['taux_sans_payer_la_largeur']} sans la payer · la permutation garantit au plus "
          f"{b['ce_que_la_permutation_garantit']}")
    print()
    print("  L'ÉCHANGE DE `178` · empilement / rotation, par le tour seul puis par les deux")
    for x in r["lechange"]:
        print(f"   {x['largeur']:>4} couches ({x['en_plis']} pli(s)) bruit {x['bruit']:>4.1f} · "
              f"tour seul {x['empilement_par_le_tour']:>3}/{x['rotation_par_le_tour']:<3} · "
              f"les deux {x['empilement_par_les_deux']:>3}/{x['rotation_par_les_deux']:<3} "
              f"sur {x['lectures_par_matiere']} · creux "
              f"{x['creux_lus_sur_lempilement']:>3}/{x['creux_lus_sur_la_rotation']:<3} "
              f"{'★' if x['les_deux_lecteurs_donnent_les_deux'] else '✗'}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("le_rasoir_ne_creuse_pas", "le_compte_monte_avec_le_recouvrement",
                "le_recouvrement_juste_suffisant_um", "encadre_entre_um", "il_vaut_le_pli_fois",
                "il_vaut_le_voxel_fois", "profondeur_du_creux_a_la_borne",
                "largeur_du_creux_a_la_borne", "ecart_median_a_la_borne",
                "le_pli_unique_ne_creuse_jamais",
                "le_plus_grand_bruit_tenu", "tient_au_bruit_de_156",
                "faux_positifs_sur_du_bruit", "taux_sur_du_bruit",
                "taux_sans_payer_la_largeur", "ce_que_la_permutation_garantit",
                "payer_la_largeur_ramene_sous_la_garantie",
                "cellules_ou_le_tour_seul_donne_les_deux",
                "cellules_ou_les_deux_donnent_les_deux",
                "cellules_gagnees_par_le_creux", "cellules_perdues_par_le_creux",
                "sur_matiere_bruitee_le_tour_seul_ne_donne_jamais_les_deux",
                "faux_creux_sur_un_escalier_fin_sans_bruit",
                "faux_creux_sur_un_escalier_fin_bruite",
                "une_largeur_donne_les_deux", "le_creux_ajoute_des_cellules",
                "le_creux_en_coute_aussi"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    n = int(COUCHES_DE_LA_CAMPAGNE)

    # ⭐⭐⭐⭐ LE NUL EST EXACTEMENT INVARIANT PAR PERMUTATION, et c'est le theoreme qui interdit a
    # un creux d'une seule couche de concourir : sa profondeur ne depend que du multiensemble.
    # ⚠⚠ LA TROISIEME MATIERE A SON MINIMUM AU BORD, ET C'EST ELLE QUI REND LE CONTROLE CAPABLE
    # D'ECHOUER. Sur les deux autres, contraindre la position du nul aux couches interieures ne
    # retire rien, donc la sonde passait au vert : la condition couverte n'ecartait aucune cellule.
    for nom, coh in (("une frontière", [0.9] * 40 + [0.1] * 5 + [0.9] * (n - 45)),
                     ("du bruit", list(np.random.default_rng(GRAINE).uniform(0.0, 1.0, n))),
                     ("un creux collé au bord", [0.1] * 3 + [0.9] * (n - 3))):
        base = le_creux_nul(coh)
        vus = set()
        for tour in range(19):
            r = np.random.default_rng(GRAINE + tour)
            vus.add(le_creux_nul(list(np.asarray(coh)[r.permutation(len(coh))]))["profondeur"])
        v(f"le nul est invariant par permutation sur {nom}", vus == {base["profondeur"]},
          f"{sorted(vus)[:3]} contre {base['profondeur']}")

    # ⚠⚠ ET C'EST POUR CA QUE L'ECHELLE COMMENCE A TROIS : une largeur de un rendrait la MEME
    # profondeur sur la courbe et sur chacun de ses melanges, donc un excedent nul par construction.
    coh = [0.9] * 40 + [0.1] * 5 + [0.9] * (n - 45)
    largeurs = les_largeurs_du_creux()
    v("l'échelle des largeurs exclut la couche isolée", 1 not in largeurs, str(largeurs))
    v("l'échelle des largeurs s'arrête au segment minimal",
      largeurs[-1] == 2 * COUCHES_MINIMALES - 1, str(largeurs))
    seul = le_creux(coh, 1)
    melanges = [le_creux(list(np.asarray(coh)[np.random.default_rng(GRAINE + t)
                                             .permutation(len(coh))]), 1) for t in range(19)]
    v("une largeur de un ne peut porter aucun excédent",
      {x["profondeur"] for x in melanges} == {seul["profondeur"]},
      f"{sorted({x['profondeur'] for x in melanges})[:3]} contre {seul['profondeur']}")

    # ⭐⭐⭐⭐ LA REPONSE EST CONNUE AVANT LA MESURE : le creux est pose a une couche CHOISIE, et
    # elle n'est ni le milieu de la fenetre ni la frontiere de `174`, pour qu'aucune recette ne
    # puisse avoir raison par coincidence.
    pose = 40
    lu = le_verdict_du_creux([[20.0, x] for x in coh], None, PERMUTATIONS, GRAINE)
    v("le creux construit est lu", lu["gagnant"] == "empilement", str(lu.get("statistique")))
    if lu["gagnant"] == "empilement":
        v("le creux tombe sur la couche posée",
          abs(int(lu["frontiere_lue"]) - (pose + 2)) <= int(lu["largeur"]) // 2 + 1,
          f"lu {lu['frontiere_lue']} pour un creusement de {pose} à {pose + 4}")

    # ⚠ UNE COHERENCE PLATE NE CREUSE NULLE PART, et la profondeur y vaut exactement zero : c'est
    # le cas ou le lecteur doit se taire par arithmetique et non par chance.
    plat = le_verdict_du_creux([[float(a), 0.9] for a in np.linspace(0.0, 90.0, n)],
                               None, PERMUTATIONS, GRAINE)
    v("une cohérence plate ne rend aucune frontière", plat["gagnant"] is None,
      str(plat.get("statistique")))

    # ⭐⭐⭐⭐ LES DEUX REGLES DE PERMUTATION SONT MESUREES COTE A COTE. Sans ce controle nomme, la
    # statistique de famille serait une precaution qu'aucune mesure n'exerce.
    taux = le_taux_sur_du_bruit(None, PERMUTATIONS, GRAINE)
    v("payer la largeur ramène le taux sous la garantie, pas la règle réfutée",
      taux["payer_la_largeur_ramene_sous_la_garantie"],
      f"{taux['taux_mesure']} contre {taux['taux_sans_payer_la_largeur']} pour une garantie de "
      f"{taux['ce_que_la_permutation_garantit']}")
    v("le nombre de tirages est dérivé de la garantie",
      les_tirages_du_taux(PERMUTATIONS) % (PERMUTATIONS + 1) == 0
      and np.sqrt(0.05 * 0.95 / les_tirages_du_taux(PERMUTATIONS)) <= 0.025,
      str(les_tirages_du_taux(PERMUTATIONS)))

    # ⭐⭐⭐⭐ LE CHEMIN PHYSIQUE, ET C'EST LA PREMISSE : un rasoir ne creuse pas, un recouvrement
    # suffisant creuse SUR la frontiere, et une feuille d'un seul pli ne creuse jamais.
    # ⚠⚠ LE RECOUVREMENT EPROUVE EST LE DERNIER BARREAU DE L'ECHELLE DERIVEE, jamais une valeur
    # tapee. Une premiere version ecrivait « seize voxels suffisent » : la sonde a echoue a un
    # decalage sur trois, et c'etait la REDACTION qui avait tort — la mesure encadre la borne a
    # dix-neuf voxels. Une batterie qui affirme un chiffre que la mesure n'a pas rendu est une
    # seconde reponse a la meme question.
    large_um = lechelle_des_recouvrements(vx, pas, PLIS_DE_LA_FIXTURE)[-1]
    for k in range(3):
        dec = pas * k / 3.0
        rasoir = le_verdict_du_creux(
            courbe_de_la_fixture(n, dec, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, vx, pas,
                                 transition_um=0.0), None, PERMUTATIONS, GRAINE)
        v(f"le rasoir ne creuse pas (décalage {round(dec, 1)} µm)", rasoir["gagnant"] is None,
          str(rasoir.get("statistique")))
        large = le_verdict_du_creux(
            courbe_de_la_fixture(n, dec, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, vx, pas,
                                 transition_um=large_um), None, PERMUTATIONS, GRAINE)
        attendues = les_frontieres_de_la_fixture(n, dec, PLIS_DE_LA_FIXTURE, vx, pas)
        v(f"le dernier barreau de l'échelle creuse (décalage {round(dec, 1)} µm)",
          large["gagnant"] == "empilement", str(large.get("statistique")))
        if large["gagnant"] == "empilement" and attendues:
            v(f"et le creux tombe sur une frontière construite (décalage {round(dec, 1)} µm)",
              min(abs(int(large["frontiere_lue"]) - x) for x in attendues)
              <= int(large["largeur"]) // 2 + 1,
              f"lu {large['frontiere_lue']} contre {attendues}")
        vide = le_verdict_du_creux(
            courbe_de_la_fixture(n, dec, CONTRASTE_DE_LA_FIXTURE, 1, vx, pas,
                                 transition_um=large_um), None, PERMUTATIONS, GRAINE)
        v(f"un seul pli ne creuse pas, au même recouvrement (décalage {round(dec, 1)} µm)",
          vide["gagnant"] is None, str(vide.get("statistique")))

    # ⭐⭐⭐⭐ LE RASOIR NE REND PAS « AUCUN CREUX », IL REND UNE COHERENCE CONSTANTE, et c'est
    # cette forme-la qu'il faut asserter. Une premiere version se contentait de « le lecteur se
    # tait » : forcer le melange des deux plis a recouvrement nul rendait des valeurs aberrantes
    # que le lecteur refusait aussi, donc la sonde passait au vert pour la raison inverse de la
    # bonne. Le grain de comparaison est celui que le module PUBLIE — quatre decimales — donc
    # aucun seuil n'entre.
    rasoir_c = [round(float(x[1]), 4) for x in courbe_de_la_fixture(
        n, 0.0, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, vx, pas, transition_um=0.0)]
    large_c = [round(float(x[1]), 4) for x in courbe_de_la_fixture(
        n, 0.0, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, vx, pas, transition_um=large_um)]
    v("le rasoir rend une cohérence constante", len(set(rasoir_c)) == 1,
      f"{len(set(rasoir_c))} valeurs distinctes, {sorted(set(rasoir_c))[:3]}")
    v("un recouvrement la fait varier", len(set(large_c)) > 1,
      f"{len(set(large_c))} valeurs distinctes")

    # ⚠⚠ LA MONOTONIE EST CE QUI AUTORISE LA BISSECTION, donc elle est mesuree et non supposee.
    echelle = lechelle_des_recouvrements(vx, pas, PLIS_DE_LA_FIXTURE)
    v("le rasoir est le premier barreau de l'échelle", echelle[0] == 0.0, str(echelle[:2]))
    v("l'échelle s'arrête avant l'épaisseur d'un pli",
      echelle[-1] < pas / PLIS_DE_LA_FIXTURE, f"{echelle[-1]} contre {pas / PLIS_DE_LA_FIXTURE}")

    # ⭐⭐ LES FRONTIERES ATTENDUES SONT VERIFIEES SUR LEUR FORME, pas seulement utilisees. Leur
    # espacement DOIT etre l'epaisseur d'un pli en couches, et la premiere doit etre la plus petite
    # que la regle de bord laisse passer : sans cela, une liste fausse d'un pli entier resterait
    # indetectable, puisque le creux lu tomberait quand meme sur l'un de ses elements.
    epaisseur_en_couches = pas / float(PLIS_DE_LA_FIXTURE) / vx
    for dec in (0.0, 43.25, 57.7):
        fr = les_frontieres_de_la_fixture(n, dec, PLIS_DE_LA_FIXTURE, vx, pas)
        ecarts = {round(b - a, 0) for a, b in zip(fr, fr[1:])}
        v(f"les frontières sont espacées d'un pli (décalage {round(dec, 2)} µm)",
          len(fr) >= 2 and ecarts == {round(epaisseur_en_couches, 0)},
          f"{fr} · écarts {sorted(ecarts)} contre {round(epaisseur_en_couches, 0)}")
        attendue = min((int(round((j * pas / PLIS_DE_LA_FIXTURE - dec) / vx))
                        for j in range(0, 12)
                        if COUCHES_MINIMALES
                        <= int(round((j * pas / PLIS_DE_LA_FIXTURE - dec) / vx))
                        < n - COUCHES_MINIMALES), default=None)
        v(f"et la première est la plus petite atteignable (décalage {round(dec, 2)} µm)",
          bool(fr) and fr[0] == attendue, f"{fr[:1]} contre {attendue}")

    # ⭐⭐⭐⭐ LE TOUR PORTE NE DEPEND PAS DU NOMBRE DE PLIS, et c'est ce qui rend les deux matieres
    # de l'echange comparables. La verification le RECALCULE depuis les frontieres et le pas
    # angulaire de chaque matiere, au lieu de relire la formule.
    plis_fins = les_plis_dune_rotation(vx, pas)
    tours = []
    for plis in (PLIS_DE_LA_FIXTURE, plis_fins):
        franchies = float(n) * vx / (pas / float(plis))
        tours.append(round(franchies * (180.0 / float(plis)), 6))
    v("les deux matières portent le même tour total", tours[0] == tours[1], str(tours))
    v("et c'est celui que `le_tour_porte` rend",
      abs(tours[0] - le_tour_porte(n, vx, pas)) < 1e-6,
      f"{tours[0]} contre {le_tour_porte(n, vx, pas)}")
    v("un pli de la matière fine tombe au niveau du voxel",
      pas / float(plis_fins) <= vx < pas / float(plis_fins - 1),
      f"{pas / float(plis_fins)} contre {vx}")

    # ⭐⭐⭐⭐ ET LE CONTROLE QUI DECIDE SI CETTE TRANCHE ACHETE QUELQUE CHOSE : les deux lecteurs
    # doivent RENDRE DES REPONSES DIFFERENTES sur la meme matiere. Si le creux disait toujours ce
    # que le tour dit, la lecture jointe ne serait qu'une seconde ecriture de `177`.
    fraction = large_um / (pas / float(PLIS_DE_LA_FIXTURE))
    fine = courbe_de_la_fixture(n, 0.0, CONTRASTE_DE_LA_FIXTURE, plis_fins, vx, pas,
                                transition_um=fraction * (pas / float(plis_fins)))
    grosse = courbe_de_la_fixture(n, 0.0, CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, vx, pas,
                                  transition_um=large_um)
    jf = le_verdict_joint(fine, None, PERMUTATIONS, GRAINE)
    jg = le_verdict_joint(grosse, None, PERMUTATIONS, GRAINE)
    v("l'escalier fin n'est pas lu comme un empilement par le creux",
      jf["le_creux"]["gagnant"] is None, str(jf["le_creux"].get("statistique")))
    v("l'escalier grossier l'est", jg["le_creux"]["gagnant"] == "empilement",
      str(jg["le_creux"].get("statistique")))
    v("les deux lecteurs ne rendent pas la même lecture sur les deux matières",
      not (jf["les_deux_lecteurs_saccordent"] and jg["les_deux_lecteurs_saccordent"]),
      f"fin {jf['le_creux']['gagnant']}/{jf['le_tour']['gagnant']} · "
      f"grossier {jg['le_creux']['gagnant']}/{jg['le_tour']['gagnant']}")

    # ⭐⭐⭐⭐ LE CHEMIN DU VERDICT EST EXERCE, ET PAS SEULEMENT LE CHAMP QUI PORTE LA REGLE. Une
    # premiere version lisait `depasse_en_payant_la_largeur` et `depasse_sans_payer_la_largeur`
    # cote a cote sans jamais verifier LEQUEL des deux le verdict suit : brancher le verdict sur la
    # regle refutee laissait la batterie verte. On cherche donc une cohérence ou les deux regles se
    # SEPARENT, et on asserte que le verdict suit la payee.
    separe = None
    for g in range(400):
        r = np.random.default_rng(GRAINE + 104729 * g)
        c = [[float(a), float(x)] for a, x in zip(r.uniform(0.0, 180.0, n),
                                                  r.uniform(0.0, 1.0, n))]
        lu = contre_les_melanges([x[1] for x in c], None, PERMUTATIONS, GRAINE)
        if lu.get("decidable") and lu["depasse_sans_payer_la_largeur"] != \
                lu["depasse_en_payant_la_largeur"]:
            separe = (c, lu)
            break
    v("il existe une cohérence où les deux règles se séparent", separe is not None)
    if separe is not None:
        c, lu = separe
        v("et le verdict suit la règle PAYÉE",
          (le_verdict_du_creux(c, None, PERMUTATIONS, GRAINE)["gagnant"] == "empilement")
          == bool(lu["depasse_en_payant_la_largeur"]),
          f"payée {lu['depasse_en_payant_la_largeur']} · réfutée "
          f"{lu['depasse_sans_payer_la_largeur']}")

    # ⭐⭐⭐⭐ ET LA REGLE JOINTE EST EXERCEE PAR UNE MATIERE OU ELLE CHANGE LA REPONSE. Sans cela,
    # la lecture jointe pouvait ignorer le creux sans qu'aucun controle ne bouge : les sondes ne
    # regardaient que ce que chaque lecteur dit SEPAREMENT.
    v("le creux change la lecture de l'escalier grossier",
      jg["gagnant"] == "empilement" and jg["par_le_tour_seul"] != "empilement",
      f"joint {jg['gagnant']} · tour seul {jg['par_le_tour_seul']}")

    nom = "la_coherence_creuse_t_elle_a_la_frontiere.py"
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
    p.add_argument("--decalages", type=int, default=DECALAGES)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graines, a.permutations, a.decalages)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
