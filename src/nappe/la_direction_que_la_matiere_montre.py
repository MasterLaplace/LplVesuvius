#!/usr/bin/env python3
"""Quelle DIRECTION la matiere montre-t-elle ? — le compagnon de `99`, et l'arbitre de `100`.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST `100` QUI L'IMPOSE. `100` a mesure que la normale du maillage
humain est a **34,1°** du rayon la ou une spirale de ce pas en predit **0,09°**, et que deux
estimateurs sans hypothese commune s'accordent dessus. Il reste donc DEUX lectures possibles, et
elles ne se distinguent pas dans le maillage :

  (a) la matiere est reellement oblique au rayon, et le maillage la suit fidelement ;
  (b) la matiere est a peu pres radiale, et c'est le MAILLAGE qui est oblique a la matiere —
      c'est-a-dire que la surface tracee par les humains NE REPOSE PAS sur une feuille.

⭐⭐⭐ SEULE LA MATIERE PEUT TRANCHER, ET ELLE LE PEUT. Le volume fin donne l'orientation locale de
l'empilement sans aucun maillage : le **tenseur de structure** — la covariance des gradients
d'intensite dans un petit cube — a pour vecteur propre dominant la direction dans laquelle
l'image varie le PLUS, c'est-a-dire la normale de la feuille. Aucun oracle, aucune supervision,
aucun modele.

⭐⭐ ET LA CONSEQUENCE POUR LE GRAAL EST DIRECTE. `99` rend le PAS que la matiere montre ; ce
fichier rend la DIRECTION. Les deux ensemble sont exactement ce qu'un automate doit savoir pour
franchir une feuille sans humain : *avance de p(matiere) le long de n(matiere)*. Si la lecture (b)
est la bonne, cela dit en prime que le referent humain ne repose pas sur la matiere — ce qui
prolonge `97` d'un cran et pour une raison differente.

⭐⭐⭐ POURQUOI LE TENSEUR DE STRUCTURE ET PAS UN GRADIENT MOYEN. Un cube qui enjambe une feuille
entiere contient des gradients de signes OPPOSES sur ses deux flancs : leur moyenne s'annule et
rendrait une direction arbitraire. Le tenseur moyenne des produits exterieurs `g g^T`, ou le signe
disparait — c'est precisement ce qui le rend juste sur un empilement periodique, et c'est la
raison de le preferer.

⚠⚠ ET LE CAS DEGENERE EST DETECTE PLUTOT QUE REPONDU. Un cube d'intensite constante a un tenseur
NUL : sa direction dominante est arbitraire et parfaitement finie. C'est le meme piege que `98` a
paye avec son test de platitude — un profil exactement constant a une etendue nulle ET un bruit
nul. La **planarite** est donc mesuree a cote de la direction, et sa barre vient d'un modele nul
fabrique.

⚠⚠⚠ ET LA CONDITION QUI REND LA CONFRONTATION POSSIBLE EST VERIFIEE, PAS SUPPOSEE. L'angle du
maillage vit dans les voxels a 45,532 µm, la direction de la matiere dans ceux a 2,4 µm. Une
transformation qui cisaillerait ne conserverait PAS les angles, donc « 34° » ne voudrait rien dire
d'un volume a l'autre — et l'ecart serait silencieux, les deux nombres restant plausibles.
`defaut_de_similitude` le mesure : **0,30°** sur la transformation publiee.

Usage :
    uv run python src/nappe/la_direction_que_la_matiere_montre.py --verifier
    uv run python src/nappe/la_direction_que_la_matiere_montre.py \\
        --json docs/mesures/la_direction_que_la_matiere_montre.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"

# ⚠ La demi-largeur du cube, en voxels FINS. Elle est DERIVEE et non choisie : a 2,4 µm de voxel
# et 173 µm de pas, un demi-pas fait 36 voxels — un cube de demi-largeur 10 couvre donc 50 µm,
# soit un peu plus d'un demi-flanc de feuille. Assez pour resoudre la rampe d'intensite qui
# TRAVERSE la feuille, et assez peu pour que la direction reste LOCALE.
# ⭐⭐ Elle est DERIVEE du balayage de `limite_de_bruit` et non choisie : a demi = 10 la direction
# derive de 9,7° des sigma = 8, a demi = 20 de 1,7°, a demi = 36 de 0,6°. Vingt est le plus grand
# cube qui tienne dans le budget de lecture — 41³ = 68 921 voxels par cellule, soit 1681 rangees
# recollees — et il rend deja la direction a moins de deux degres au bruit le plus fort teste.
DEMI = 20
CELLULES_PAR_BANDE = 8
# ⚠ La barre de planarite vient du nul, pas d'un reglage. Le nombre de tirages est le seul
# parametre, et il ne change que la precision du p99.
TIRAGES_DU_NUL = 400


def bloc(centre_zyx: np.ndarray, demi: int = DEMI, pas: int = 1) -> np.ndarray:
    """Les points entiers d'un cube centre sur `centre_zyx`, en indices du volume fin.

    ⭐⭐⭐ `pas` SOUS-ECHANTILLONNE SANS RETRECIR LE CUBE, et c'est la difference qui compte : la
    PORTEE physique reste la meme — donc la structure vue reste la meme — mais le nombre de points
    lus tombe comme le cube du pas. Retrecir le cube changerait ce qu'on regarde ; l'echantillonner
    plus grossierement change seulement combien on paie pour le regarder. A `pas = 2`, un cube de
    98 µm coute HUIT fois moins.

    ⚠ Le gradient est alors pris sur des voxels espaces de `pas`, ce qui EQUIVAUT a une derivee a
    plus grande echelle. Le balayage de bruit de `limite_de_bruit` montre que c'est un AVANTAGE
    quand le bruit domine par voxel — mais ce n'est pas une raison de le supposer :
    `limite_de_sous_echantillonnage` le mesure contre une reponse connue.

    ⭐⭐ LE CUBE EST BATI DANS LE VOLUME FIN ET NON DANS LE MAILLAGE, et ce n'est pas un detail :
    le voxel fin est isotrope, donc un cube d'indices EST un cube de matiere. Le construire dans
    le maillage puis le transformer donnerait un parallelepipede legerement cisaille, et le
    tenseur de structure lirait ce cisaillement comme une orientation.

    ⚠ L'ordre des points est (z, y, x) avec x qui varie le plus vite : c'est ce qui laisse
    `voxel_distant` recoller une RANGEE entiere en une seule plage d'octets, une par (z, y) au
    lieu d'une par voxel.
    """
    pas = max(1, int(pas))
    d = np.arange(-demi, demi + 1, pas)
    n = len(d)
    zz, yy, xx = np.meshgrid(d, d, d, indexing="ij")
    c = np.rint(np.asarray(centre_zyx, dtype=np.float64)).astype(np.int64)
    p = np.stack([zz + c[0], yy + c[1], xx + c[2]], axis=-1)
    return p.reshape(n * n * n, 3)


def cote_du_bloc(demi: int = DEMI, pas: int = 1) -> int:
    """Combien de points par arete un cube de cette demi-largeur et de ce pas porte.

    ⚠ Elle existe pour que l'appelant n'ait PAS a recalculer la forme du cube pour le remodeler :
    deux formules pour une meme forme finiraient par ne pas s'accorder, et le tenseur lirait alors
    un cube transpose sans que rien ne leve.
    """
    return len(np.arange(-demi, demi + 1, max(1, int(pas))))


def tenseur_de_structure(cube: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La normale locale et les trois valeurs propres du tenseur, sur un cube (n, n, n).

    ⭐⭐⭐ LA NORMALE EST LE VECTEUR PROPRE DOMINANT, ET C'EST L'INVERSE DE L'ACP DES POINTS. Une
    ACP sur des POSITIONS cherche la direction de moindre etalement ; un tenseur de structure
    porte sur des GRADIENTS et cherche celle ou l'image varie le PLUS. Les deux rendent la
    normale d'une surface, par deux chemins opposes — confondre lequel prendre rendrait une
    direction TANGENTE, a 90° de la reponse, ce qui reste un vecteur unitaire parfaitement
    plausible.

    Rend la direction en (z, y, x) et les valeurs propres en ordre DECROISSANT.
    """
    c = np.asarray(cube, dtype=np.float64)
    g = np.gradient(c)
    # ⚠⚠⚠ LES PLANS DE BORD SONT JETES, ET C'EST UNE CORRECTION MESUREE PLUTOT QU'UNE PRUDENCE.
    # `np.gradient` prend des differences UNILATERALES sur les deux plans extremes de chaque axe,
    # dont la variance est QUATRE fois celle d'une difference centree. Le cube injecte donc une
    # anisotropie a son propre bord : ses plans extremes en z gonflent gz, ceux en y gonflent gy.
    # Mesure du defaut : sur du BRUIT PUR, deux moities d'un meme cube coupees selon z
    # s'accordaient a **10,4°** au lieu des ~60° que deux directions au hasard donnent en trois
    # dimensions — parce que la coupe cree un nouveau bord en z et biaise les DEUX moities vers z.
    # C'est « un estimateur qui mesure la grille » (`97`) sous un nouveau costume, et il aurait
    # rendu une garde qui parait stricte tout en laissant passer du bruit, et une direction de
    # matiere tiree vers z.
    if min(c.shape) >= 3:
        g = [x[1:-1, 1:-1, 1:-1] for x in g]
    gz, gy, gx = g[0].ravel(), g[1].ravel(), g[2].ravel()
    v = np.stack([gz, gy, gx], axis=-1)
    j = v.T @ v / max(len(v), 1)
    valeurs, vecteurs = np.linalg.eigh(j)
    ordre = np.argsort(valeurs)[::-1]
    return vecteurs[:, ordre[0]], valeurs[ordre]


def planarite(valeurs: np.ndarray) -> float:
    """Quelle part de la variation d'image tient dans UNE direction, entre 0 et 1.

    ⭐⭐ C'EST LE JUGE DE « LA MATIERE A-T-ELLE UNE ORIENTATION ICI », et il est necessaire :
    sans lui, un cube homogene rendrait une direction arbitraire, parfaitement unitaire, que rien
    ne distinguerait d'une mesure. C'est le meme role que le score d'accord dans `98`.

    ⚠ Un tenseur exactement nul — cube constant — rend **0** plutot qu'une division par zero :
    le cas degenere doit etre DETECTE, pas repondu. C'est le piege que `98` a paye avec un profil
    plat, dont l'etendue et le bruit sont nuls tous les deux.
    """
    s = float(np.sum(valeurs))
    if s <= 1e-12:
        return 0.0
    return float(valeurs[0] / s)


def accord_des_moities(cube: np.ndarray) -> tuple[float, np.ndarray]:
    """L'angle entre les directions lues sur DEUX MOITIES DISJOINTES du meme cube.

    ⭐⭐⭐ C'EST LA GARDE, ET ELLE A REMPLACE LA PLANARITE POUR UNE RAISON MESUREE. La planarite
    dit quelle part de la variation d'image tient dans une direction — or un bruit blanc
    contribue ISOTROPIQUEMENT aux trois valeurs propres, donc il ecrase le RAPPORT sans deplacer
    la DIRECTION, que la moyenne sur des milliers de voxels continue de retrouver. Mesure du
    balayage : a sigma = 15 pour 40 d'amplitude, un cube de 175 µm de cote rend la direction a
    **2,50°** pendant que sa planarite est **0,344**, c'est-a-dire AU niveau du bruit pur.

    ⛔⛔ FERMER SUR LA PLANARITE AURAIT DONC ETE UNE GARDE QUI SUPPRIME CE QU'ELLE DOIT LAISSER
    PASSER — le peche que `97` a paye avec son critere de bord. La planarite est gardee et
    PUBLIEE, mais comme une mesure de contraste, jamais comme un juge de direction.

    ⭐⭐ Deux moities disjointes donnent une garde SANS modele nul : si la direction est reelle,
    les deux moities s'accordent ; si c'est du bruit, elles ne s'accordent pas. C'est la
    discipline des « deux estimateurs sans hypothese commune » de `100`, ramenee a l'interieur
    d'un seul cube — et elle se calibre elle-meme, donc rien a regler.

    ⚠ La coupe est faite selon z, l'axe le plus LENT du cube : couper selon x separerait des
    voxels contigus en octets, donc deux moities qui partagent le meme bruit de lecture.

    Rend (l'angle entre les deux moities, la direction de l'ensemble).
    """
    c = np.asarray(cube, dtype=np.float64)
    n = c.shape[0]
    # ⚠ Chaque moitie perd deux plans par axe au gradient, donc il lui faut au moins cinq plans
    # pour garder un interieur : sous dix plans au total, la garde n'a rien a comparer et le dit.
    if n < 10:
        return float("nan"), tenseur_de_structure(c)[0]
    milieu = n // 2
    d1, _ = tenseur_de_structure(c[:milieu])
    d2, _ = tenseur_de_structure(c[milieu:])
    d, _ = tenseur_de_structure(c)
    return angle_entre(d1, d2), d


def nul_du_tenseur(tirages: int = TIRAGES_DU_NUL, demi: int = DEMI,
                   graine: int = 101, pas: int = 1) -> dict:
    """Ce que le tenseur rend sur du BRUIT PUR : la barre de planarite et le controle de direction.

    ⭐⭐⭐ LA BARRE NE VIENT PAS D'UN REGLAGE. Sur du bruit blanc, la variation d'image se repartit
    a peu pres egalement sur les trois axes, donc la planarite tourne autour d'un tiers — mais pas
    exactement, et sa QUEUE est ce qui compte : c'est elle qui dit quelle planarite un cube sans
    structure peut atteindre par chance. Le p99 est la barre.

    ⚠ Et la DIRECTION du nul est controlee aussi, pas seulement sa planarite : sur du bruit elle
    doit etre isotrope. Si elle privilegiait un axe — ce que `np.gradient` pourrait faire aux
    bords d'un cube — le fichier mesurerait une preference de l'estimateur et l'appellerait une
    propriete de la matiere.
    """
    r = np.random.default_rng(graine)
    # ⚠⚠ LA BARRE DEPEND DE LA FORME DU CUBE, PAS DE SA PORTEE. Un cube sous-echantillonne a
    # moins de points, donc son tenseur est plus bruite et son nul plus haut : reutiliser la barre
    # d'un cube plein comparerait deux choses differentes, et laisserait passer du bruit.
    n = cote_du_bloc(demi, pas)
    pl, dirs, acc = [], [], []
    for _ in range(tirages):
        cube = r.normal(100.0, 10.0, size=(n, n, n))
        d, val = tenseur_de_structure(cube)
        pl.append(planarite(val))
        dirs.append(d)
        acc.append(accord_des_moities(cube)[0])
    pl = np.asarray(pl)
    acc = np.asarray(acc)
    dirs = np.abs(np.asarray(dirs))
    return {
        "tirages": tirages, "demi": demi, "pas_echantillon": int(max(1, pas)),
        "cote_en_points": int(n),
        "planarite_mediane": round(float(np.median(pl)), 4),
        "planarite_p95": round(float(np.percentile(pl, 95)), 4),
        "planarite_p99": round(float(np.percentile(pl, 99)), 4),
        # ⭐⭐⭐ LA BARRE QUI SERT : ce que l'accord des deux moities atteint sur du BRUIT PUR.
        # Deux directions tirees au hasard en trois dimensions font 60° en moyenne, donc une
        # barre basse est franchie seulement par de la structure. Le p1 est la barre parce que
        # la quantite est un DESACCORD : on garde ce qui est EN DESSOUS.
        "accord_des_moities_median_deg": round(float(np.median(acc)), 2),
        "accord_des_moities_p1_deg": round(float(np.percentile(acc, 1)), 2),
        "accord_des_moities_p5_deg": round(float(np.percentile(acc, 5)), 2),
        # ⚠ L'isotropie du nul : les trois composantes moyennes doivent se ressembler.
        "composantes_moyennes": [round(float(x), 4) for x in dirs.mean(axis=0)],
        "anisotropie_du_nul": round(
            float(dirs.mean(axis=0).max() / max(dirs.mean(axis=0).min(), 1e-9)), 3),
    }


def limite_de_sous_echantillonnage(pas_voxels: float, demi: int = DEMI,
                                   amplitude: float = 40.0, bruit: float = 15.0,
                                   pas_echantillon=(1, 2, 3, 4, 5), tirages: int = 4,
                                   normale=(0.0, 0.5, 0.866)) -> dict:
    """Jusqu'ou peut-on echantillonner GROSSIEREMENT un cube sans perdre la direction ?

    ⭐⭐⭐ C'EST LA QUESTION QUI DECIDE SI LA MESURE DE PORTEE EST ABORDABLE. Un cube coute
    **15,4 s** de lecture reseau, donc `102` a mis SEPT HEURES pour six pas — et sa portee est
    censuree, donc la marche suivante demande d'aller plus loin. Le nombre de points tombe comme le
    CUBE du pas d'echantillonnage : a `pas = 2`, huit fois moins, donc deux secondes au lieu de
    quinze.

    ⚠⚠ MAIS CELA NE SE SUPPOSE PAS. Un gradient pris sur des voxels espaces est une derivee a plus
    grande echelle : cela peut aider — le bruit par voxel s'y moyenne — ou detruire la direction si
    le pas approche la demi-periode de l'empilement. Ici la periode fait 72 voxels, donc un pas de
    2 a 5 reste tres en deca ; le balayage le VERIFIE plutot que de l'argumenter.

    ⚠ La portee physique du cube ne change PAS : seule la finesse de l'echantillonnage change. Un
    cube retreci regarderait autre chose ; un cube sous-echantillonne regarde la meme chose moins
    cher.
    """
    out = {"demi": demi, "cote_um_du_cube": round((2 * demi + 1) * 2.4, 1),
           "bruit": bruit, "lignes": []}
    for pe in pas_echantillon:
        ang, acc, pl = [], [], []
        for g in range(tirages):
            cube = cube_dun_empilement(normale, pas_voxels, demi=demi, amplitude=amplitude,
                                       bruit=bruit, graine=g, pas_echantillon=pe)
            d, val = tenseur_de_structure(cube)
            ang.append(angle_entre(d, normale))
            pl.append(planarite(val))
            acc.append(accord_des_moities(cube)[0])
        cote = cote_du_bloc(demi, pe)
        # ⭐⭐⭐ CHAQUE PAS EST COMPARE A LA BARRE DE SA PROPRE FORME. Un cube plus grossier a
        # moins de points, donc un nul plus haut : le juger a la barre du cube plein le
        # declarerait bon pour la mauvaise raison.
        nul = nul_du_tenseur(tirages=120, demi=demi, pas=pe)
        barre = nul["accord_des_moities_p1_deg"]
        des = float(np.median(acc)) if np.isfinite(acc).all() else float("nan")
        out["lignes"].append({
            "pas_echantillon": pe, "cote_en_points": cote, "points": cote ** 3,
            "barre_de_sa_forme_deg": barre,
            # ⚠ La MARGE est ce qui decide, pas le desaccord seul : c'est de combien
            # l'empilement passe SOUS la barre de sa propre forme.
            "marge_sous_la_barre_deg": (round(barre - des, 2)
                                        if np.isfinite(des) else None),
            "la_garde_tient": bool(np.isfinite(des) and des < barre),
            # ⭐ Le gain est le rapport des NOMBRES DE POINTS, donc du temps de lecture : c'est la
            # quantite qui decide, pas le pas lui-meme.
            "gain_de_lecture": round((cote_du_bloc(demi, 1) ** 3) / max(cote ** 3, 1), 1),
            "angle_deg": round(float(np.median(ang)), 2),
            "desaccord_des_moities_deg": round(float(np.median(acc)), 2),
            "planarite": round(float(np.median(pl)), 3),
        })
    return out


def limite_de_bruit(pas_voxels: float, demis=(10, 20), amplitude: float = 40.0,
                    sigmas=(0.0, 1.0, 2.0, 4.0, 8.0, 15.0), tirages: int = 3,
                    normale=(0.0, 0.5, 0.866)) -> dict:
    """Jusqu'a quel bruit le tenseur rend-il encore la direction, et pour quelle taille de cube ?

    ⭐⭐⭐ C'EST LE BALAYAGE QUI A CORRIGE LA CONCEPTION DE CE FICHIER, et il faut le publier
    plutot que d'en garder la conclusion. Le gradient du SIGNAL par voxel vaut
    `A * 2*pi / T` = 3,49 pour 40 d'amplitude et un pas de 72 voxels ; celui du BRUIT vaut
    `sigma * sqrt(2)`, soit 21 a sigma = 15. Le bruit domine donc le signal d'un facteur SIX par
    voxel — et pourtant la direction reste juste, parce qu'un bruit isotrope s'annule dans la
    MOYENNE des produits exterieurs sans s'annuler dans leur RAPPORT.

    ⛔ Consequence, et c'est ce qui a failli fermer le fichier sur la mauvaise garde : la
    planarite retombe a 0,34 — le niveau du bruit pur — la ou la direction est encore a 2,5°.
    """
    out = {"pas_voxels": round(float(pas_voxels), 1),
           "gradient_du_signal_par_voxel": round(
               float(amplitude * 2 * np.pi / pas_voxels), 2),
           "cubes": {}}
    for demi in demis:
        lignes = []
        for sg in sigmas:
            ang, pl = [], []
            for g in range(tirages):
                cube = cube_dun_empilement(normale, pas_voxels, demi=demi,
                                           amplitude=amplitude, bruit=sg, graine=g)
                d, val = tenseur_de_structure(cube)
                ang.append(angle_entre(d, normale))
                pl.append(planarite(val))
            lignes.append({"sigma": sg,
                           "gradient_du_bruit_par_voxel": round(
                               float(sg * np.sqrt(2.0)), 2),
                           "angle_deg": round(float(np.median(ang)), 2),
                           "planarite": round(float(np.median(pl)), 3)})
        out["cubes"][str(demi)] = {"cote_voxels": 2 * demi + 1, "lignes": lignes}
    return out


def cube_dun_empilement(normale_zyx, pas_voxels: float, demi: int = DEMI,
                        amplitude: float = 40.0, bruit: float = 0.0,
                        graine: int = 7, pas_echantillon: int = 1) -> np.ndarray:
    """Un cube fabrique dont l'empilement a une normale CONNUE — la fixture porteuse.

    ⭐⭐⭐ ELLE EST DANS LE MODULE ET NON DANS LA BATTERIE parce que c'est elle qui porte
    l'argument : une direction mesuree sur des donnees reelles ne peut pas etre validee, on ne
    sait pas ou est la reponse. Ici on la connait, donc l'estimateur peut ECHOUER.
    """
    d = np.arange(-demi, demi + 1, max(1, int(pas_echantillon))).astype(np.float64)
    zz, yy, xx = np.meshgrid(d, d, d, indexing="ij")
    u = np.asarray(normale_zyx, dtype=np.float64)
    u = u / np.linalg.norm(u)
    proj = zz * u[0] + yy * u[1] + xx * u[2]
    cube = 100.0 + amplitude * np.cos(2 * np.pi * proj / pas_voxels)
    if bruit:
        cube = cube + np.random.default_rng(graine).normal(0.0, bruit, cube.shape)
    return cube


def angle_entre(u: np.ndarray, v: np.ndarray) -> float:
    """L'angle non oriente entre deux directions, en degres — une normale n'a pas de sens."""
    u = np.asarray(u, dtype=np.float64).ravel()
    v = np.asarray(v, dtype=np.float64).ravel()
    u = u / max(np.linalg.norm(u), 1e-12)
    v = v / max(np.linalg.norm(v), 1e-12)
    return float(np.degrees(np.arccos(min(1.0, abs(float(u @ v))))))


def angle_dun_centre_decale(rayon_mm: float, decalage_mm: float) -> float:
    """L'angle qu'un CENTRE MAL ESTIME ferait apparaitre entre le vrai rayon et le rayon calcule.

    ⭐⭐⭐ C'EST LA DERNIERE EXPLICATION ALTERNATIVE DE L'OBLIQUITE, ET ELLE SE REFUTE PAR SA
    SIGNATURE. La direction radiale est calculee depuis l'axe du rouleau ; si cet axe est decale
    de `d`, la direction calculee tourne de `arctan(d / r)` par rapport a la vraie. Un decalage de
    trois millimetres suffirait donc a fabriquer 35° a quatre millimetres de rayon — et `90` a
    mesure que l'axe DERIVE de 12,6 mm sur la hauteur du fragment, donc l'hypothese n'est pas
    farfelue.

    ⭐⭐ MAIS ELLE PREDIT UNE DECROISSANCE EN 1/r, ET C'EST CA QUI LA REND FALSIFIABLE. Un meme
    decalage ne peut pas produire le meme angle au coeur et au bord : ajuste sur le coeur il
    predit 7° au bord, ajuste sur le bord il predit 69° au coeur. Une obliquite a peu pres
    CONSTANTE sur un rayon qui varie d'un facteur six n'est donc pas un defaut d'axe.
    """
    return float(np.degrees(np.arctan2(abs(decalage_mm), max(rayon_mm, 1e-9))))


def refutation_du_centre_decale(lignes: list[dict]) -> dict:
    """Un axe decale explique-t-il mieux les angles mesures qu'une obliquite constante ?

    ⭐⭐⭐ LES DEUX MODELES SONT AJUSTES ET COMPARES, ET AUCUN N'EST PRIVILEGIE D'AVANCE. Le
    modele « axe decale » a un parametre libre (le decalage) exactement comme le modele
    « obliquite constante » (la valeur constante), donc leurs residus sont directement
    comparables — c'est ce qui rend la comparaison honnete plutot qu'un homme de paille.

    ⚠ Et les deux extremites sont rendues a part de l'ajustement, parce que c'est la que la
    signature en 1/r se voit : un residu global peut cacher un desaccord qui change de signe.
    """
    lues = [x for x in lignes
            if x.get("angle_matiere_rayon_deg") is not None and x.get("rayon_mm")]
    if len(lues) < 5:
        return {"message": "trop peu de bandes pour comparer les deux modeles"}
    r = np.array([x["rayon_mm"] for x in lues], dtype=np.float64)
    a = np.array([x["angle_matiere_rayon_deg"] for x in lues], dtype=np.float64)
    # ⚠ Le decalage est cherche par balayage plutot que par une formule : la fonction n'est pas
    # lineaire en d, et une linearisation autour d'un point choisi serait un reglage cache.
    ds = np.linspace(0.0, 40.0, 4001)
    residus = np.array([
        float(np.mean((a - np.degrees(np.arctan2(d, r))) ** 2)) for d in ds])
    k = int(np.argmin(residus))
    d_ajuste = float(ds[k])
    residu_axe = float(np.sqrt(residus[k]))
    residu_constante = float(np.sqrt(np.mean((a - np.median(a)) ** 2)))
    ordre = np.argsort(r)
    coeur, bord = int(ordre[0]), int(ordre[-1])
    return {
        "bandes": len(lues),
        "decalage_ajuste_mm": round(d_ajuste, 2),
        "residu_du_modele_daxe_deg": round(residu_axe, 2),
        "residu_du_modele_constant_deg": round(residu_constante, 2),
        # ⭐⭐⭐ LE VERDICT, CALCULE ET NON REDIGE.
        "un_axe_decale_explique_mieux": bool(residu_axe < residu_constante),
        "rayon_le_plus_petit_mm": round(float(r[coeur]), 1),
        "rayon_le_plus_grand_mm": round(float(r[bord]), 1),
        "angle_mesure_au_coeur_deg": round(float(a[coeur]), 1),
        "angle_mesure_au_bord_deg": round(float(a[bord]), 1),
        # ⚠ Les deux ajustements a une seule extremite, qui montrent l'incompatibilite : le
        # decalage qui explique le coeur predit un angle bien trop petit au bord, et l'inverse.
        "decalage_qui_explique_le_coeur_mm": round(
            float(r[coeur] * np.tan(np.deg2rad(a[coeur]))), 2),
        "angle_predit_au_bord_par_ce_decalage_deg": round(
            angle_dun_centre_decale(float(r[bord]),
                                    float(r[coeur] * np.tan(np.deg2rad(a[coeur])))), 1),
        "decalage_qui_explique_le_bord_mm": round(
            float(r[bord] * np.tan(np.deg2rad(a[bord]))), 2),
        "angle_predit_au_coeur_par_ce_decalage_deg": round(
            angle_dun_centre_decale(float(r[coeur]),
                                    float(r[bord] * np.tan(np.deg2rad(a[bord])))), 1),
    }


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def _mediane(v) -> float | None:
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)])
    return round(float(np.median(v)), 2) if len(v) else None


def accord_entre_pas(cellules: int = 24, demi: int = DEMI, pas=(1, 2, 3),
                     graine: int = 71, bandes_max: int | None = 2,
                     fils: int = 32) -> dict:
    """Sur les MEMES cellules du vrai volume, plusieurs finesses d'echantillonnage s'accordent-elles ?

    ⭐⭐⭐ C'EST LA GARDE QUI DECIDE SI L'ECONOMIE EST LEGITIME. `limite_de_sous_echantillonnage`
    montre sur un empilement FABRIQUE qu'un pas grossier est meilleur ET moins cher — mais cet
    empilement est parfaitement periodique et son bruit est blanc. Adopter le pas grossier sur
    cette seule base changerait EN SILENCE ce que `101` et `102` mesurent.

    ⚠⚠ LES CELLULES SONT LES MEMES, ET C'EST TOUTE LA FORCE DU CONTROLE : comparer deux
    populations differentes ferait dire au resultat ce qu'on veut, et ce depot l'a deja paye —
    `derouler_par_le_pas_normal` mesure son temoin sur les memes cellules, exactement pour ca.
    Chaque cellule est lue une fois PAR PAS, et la quantite rendue est l'angle au pas le plus fin.

    ⚠⚠⚠ ET LE COUT SE MESURE, IL NE SE MODELISE PAS. Le comptage de points predisait un gain de
    SEPT pour un pas de 2 ; la mesure en rend DEUX. Une lecture distante est dominee par le nombre
    de PLAGES d'octets et par un fixe par cube, pas par le nombre de points — un cube
    sous-echantillonne touche toujours une plage par rangee (z, y).
    """
    import time  # noqa: PLC0415

    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import appliquer, matrice  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    pas = tuple(int(x) for x in pas)
    reference = min(pas)
    bandes = R.bandes_du_fragment()[:bandes_max]
    # ⚠⚠ MEME LECON QUE `102` : une mesure qui lit le reseau pendant des dizaines de minutes doit
    # dire ou elle en est, sinon on decide de l'attendre ou de la tuer sans donnee.
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415

    depart = maintenant()
    faites = 0
    ecarts = {pe: [] for pe in pas}
    desaccords = {pe: [] for pe in pas}
    temps = {pe: 0.0 for pe in pas}
    lus = 0
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        centres = appliquer(m, a[ind[:, 0], ind[:, 1]])
        for k in range(len(centres)):
            reponses, t_local = {}, {}
            for pe in pas:
                pts = bloc(centres[k], demi, pe)
                if not vol.dans_le_volume(pts).all():
                    reponses = {}
                    break
                t0 = maintenant()
                brut = vol.lire(pts, fils=fils)
                t_local[pe] = maintenant() - t0
                if not np.isfinite(brut).all():
                    reponses = {}
                    break
                n = cote_du_bloc(demi, pe)
                cube = brut.reshape(n, n, n)
                reponses[pe] = (tenseur_de_structure(cube)[0], accord_des_moities(cube)[0])
            if len(reponses) != len(pas):
                continue
            lus += 1
            for pe in pas:
                temps[pe] += t_local[pe]
                ecarts[pe].append(angle_entre(reponses[pe][0], reponses[reference][0]))
                desaccords[pe].append(reponses[pe][1])
        faites += 1
        avancement(faites, len(bandes), "bandes", depart)
    if lus < 5:
        return {"message": f"trop peu de cellules lues à tous les pas ({lus})"}

    lignes = []
    for pe in pas:
        e = np.asarray(ecarts[pe])
        cote = cote_du_bloc(demi, pe)
        lignes.append({
            "pas_echantillon": pe, "cote_en_points": cote, "points": cote ** 3,
            # ⚠ Les RANGEES sont ce qui coute : `voxel_distant` recolle une plage par (z, y).
            "rangees_lues": cote ** 2,
            "ecart_median_au_plus_fin_deg": round(float(np.median(e)), 2),
            "ecart_p90_deg": round(float(np.percentile(e, 90)), 2),
            "part_au_dela_de_dix_degres": round(float(np.mean(e > 10.0)), 3),
            "desaccord_median_deg": round(float(np.nanmedian(desaccords[pe])), 2),
            "secondes_par_cube": round(temps[pe] / lus, 2),
            "gain_de_temps": round(temps[reference] / max(temps[pe], 1e-9), 2),
        })
    return {"cellules": lus, "demi": demi, "pas_reference": reference,
            "cote_um_du_cube": round((2 * demi + 1) * C.VOXEL_FIN_UM, 1),
            "lignes": lignes}


def mesurer(cellules: int = CELLULES_PAR_BANDE, demi: int = DEMI, graine: int = 101,
            bandes_max: int | None = None, fils: int = 32) -> dict:
    """Pour chaque bande : la direction de la matiere, contre le rayon et contre le maillage."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_normale_nest_pas_le_rayon as N  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import (appliquer, appliquer_direction,  # noqa: PLC0415
                                           defaut_de_similitude, matrice)
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    # ⚠⚠⚠ LA CONDITION QUI REND LA CONFRONTATION POSSIBLE, VERIFIEE AVANT DE MESURER : sans
    # conservation des angles, un angle du maillage et une direction du volume fin ne sont pas
    # comparables, et l'ecart serait silencieux.
    defaut = defaut_de_similitude(m)
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    co = ({(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
          if CONTINUITE.is_file() else {})
    nul = nul_du_tenseur(demi=demi)
    # ⭐⭐⭐ LA BARRE EST CELLE DE L'ACCORD DES MOITIES, PAS CELLE DE LA PLANARITE, et c'est la
    # correction que le balayage de bruit a imposee : un bruit isotrope ecrase le RAPPORT des
    # valeurs propres sans deplacer la DIRECTION. Fermer sur la planarite aurait ecarte des
    # cellules ou la direction est juste a deux degres.
    barre = nul["accord_des_moities_p1_deg"]
    n_cote = 2 * demi + 1

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    # ⚠ « le cache manque » et « on n'a demande qu'une bande » sont deux causes differentes du
    # meme symptome, et les confondre envoie telecharger un cache deja present.
    if len(nuages) < 2 and len(bandes) >= 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    if len(nuages) < 2:
        return {"message": f"l'axe demande au moins deux bandes ; {len(bandes)} demandée(s)"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = maintenant()
    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 10:
            continue
        p0 = a[ind[:, 0], ind[:, 1]]
        c0 = N.centre_interpole(p0[:, 2], bords, cx, cy)
        rad = N.direction_radiale(p0, c0)
        ng = N.normale_de_la_grille(a, ok, ind)
        bon = np.isfinite(ng).all(axis=1)
        if int(bon.sum()) < 10:
            continue
        ng = N.orienter_vers_lexterieur(ng[bon], rad[bon])
        # ⭐⭐ LES DEUX DIRECTIONS DU MAILLAGE SONT TRANSPORTEES VERS LE VOLUME FIN, et non
        # l'inverse : la direction de la matiere y est mesuree, donc c'est le seul espace ou les
        # trois vivent ensemble. Et une DIRECTION se transporte par la partie lineaire seule.
        rad_fin = appliquer_direction(m, rad[bon])
        ng_fin = appliquer_direction(m, ng)
        centres = appliquer(m, p0[bon])

        d_rad, d_mail, pls, accs, lus = [], [], [], [], 0
        for k in range(len(centres)):
            pts = bloc(centres[k], demi)
            if not vol.dans_le_volume(pts).all():
                continue
            brut = vol.lire(pts, fils=fils)
            if not np.isfinite(brut).all():
                continue
            cube = brut.reshape(n_cote, n_cote, n_cote)
            _, val = tenseur_de_structure(cube)
            desaccord, nm = accord_des_moities(cube)
            pls.append(planarite(val))
            accs.append(desaccord)
            # ⭐ « La matiere a une orientation ici » et « voici laquelle » sont DEUX faits :
            # une direction dont les deux moities du cube ne s'accordent pas ne doit pas entrer
            # dans la mediane. La barre est celle du bruit pur, donc rien n'est regle.
            if not np.isfinite(desaccord) or desaccord >= barre:
                continue
            lus += 1
            d_rad.append(angle_entre(nm, rad_fin[k]))
            d_mail.append(angle_entre(nm, ng_fin[k]))
        d = {
            "de": x["de"], "a": x["a"],
            "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
            # ⚠ La rupture de continuite vient de `92` et non d'ici : c'est la variable contre
            # laquelle toute la campagne mesure ses signaux, et la recalculer en ferait une
            # seconde definition.
            "continuite": co.get((x["de"], x["a"]), {}).get("rapport_interieur"),
            "cellules": int(len(centres)), "cubes_lus": len(pls), "cubes_orientes": lus,
            "part_orientee": round(lus / max(len(pls), 1), 3),
            "planarite_mediane": _mediane(pls),
            "desaccord_des_moities_median_deg": _mediane(accs),
            "angle_matiere_rayon_deg": _mediane(d_rad),
            "angle_matiere_maillage_deg": _mediane(d_mail),
        }
        lignes.append(d)
        avancement(len(lignes), len(bandes), "bandes", depart)

    out = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN,
           "voxel_fin_um": C.VOXEL_FIN_UM, "voxel_maillage_um": C.VOXEL_MAILLAGE_UM,
           "pas_nominal_um": C.PAS_UM, "demi_cube_voxels": demi,
           "cote_du_cube_um": round((2 * demi + 1) * C.VOXEL_FIN_UM, 1),
           "cellules_par_bande": cellules,
           "defaut_de_similitude_deg": round(defaut, 3),
           "les_angles_sont_transportables": bool(defaut < 1.0),
           "nul_du_tenseur": nul, "barre_daccord_des_moities_deg": barre,
           # ⛔⛔ LA PLANARITE EST GARDEE ET PUBLIEE, MAIS REFUTEE COMME JUGE DE DIRECTION : le
           # balayage montre qu'elle retombe au niveau du bruit pur la ou la direction est encore
           # juste a deux degres. La publier sans son refus inviterait a s'en servir.
           "limite_de_bruit_du_tenseur": limite_de_bruit(
               C.PAS_UM / C.VOXEL_FIN_UM, demis=(10, demi)),
           "bandes": len(lignes), "lignes": lignes}
    return agreger(out)


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des lignes par bande — meme partage que `100`."""
    lues = [x for x in r["lignes"] if x.get("angle_matiere_rayon_deg") is not None]
    if not lues:
        return r
    ar = [x["angle_matiere_rayon_deg"] for x in lues]
    am = [x["angle_matiere_maillage_deg"] for x in lues]
    ray = [x["rayon_mm"] for x in lues if x["rayon_mm"] is not None]
    arr = [x["angle_matiere_rayon_deg"] for x in lues if x["rayon_mm"] is not None]
    rup = [x["continuite"] for x in lues if x.get("continuite") is not None]
    amr = [x["angle_matiere_maillage_deg"] for x in lues
           if x.get("continuite") is not None]
    orr = [x["part_orientee"] for x in lues if x.get("continuite") is not None]
    r["un_axe_decale_est_il_lexplication"] = refutation_du_centre_decale(r["lignes"])
    r["resume"] = {
        "bandes_lues": len(lues),
        "angle_matiere_rayon_median_deg": round(float(np.median(ar)), 2),
        "angle_matiere_maillage_median_deg": round(float(np.median(am)), 2),
        "part_orientee_mediane": round(
            float(np.median([x["part_orientee"] for x in lues])), 3),
        # ⚠ `_mediane` saute les absents plutot que de supposer le champ present : une ligne
        # qui n'a pas pu mesurer sa planarite est legitime, et une image ecrite avant qu'un
        # champ n'existe doit rester reagregeable. Le contraire leve un KeyError au milieu
        # d'un recalcul, ce qui a ete rencontre pour de vrai sur ce fichier.
        "planarite_mediane": _mediane([x.get("planarite_mediane") for x in lues]),
        # ⭐⭐⭐ LE VERDICT, CALCULE ET NON REDIGE. Les deux lectures que `100` laissait ouvertes
        # se distinguent par un seul signe : la matiere est-elle plus proche du RAYON ou du
        # MAILLAGE ?
        "la_matiere_suit_le_maillage": bool(np.median(am) < np.median(ar)),
        "ecart_entre_les_deux_lectures_deg": round(
            float(np.median(ar)) - float(np.median(am)), 2),
        "angle_au_rayon_contre_rayon": correlation(arr, ray),
        # ⭐⭐⭐ LA QUESTION DU GRAAL, POSEE A LA MATIERE ET NON A UN MAILLAGE. « De combien
        # l'humain s'est-il ecarte de la matiere » est un signal dont le REFERENT est la
        # matiere, contrairement aux quatre candidats que `94` a `97` ont fermes — tous
        # calibres contre un maillage dont `97` a mesure qu'il n'a pas de valeur unique.
    }
    # ⚠⚠⚠ UNE CORRELATION SANS DONNEE EST ABSENTE, PAS NULLE. `correlation` rend 0,0 sur une
    # liste vide, ce qui est juste comme valeur de repli et FAUX comme resultat publie : « +0,000 »
    # se lit « rien ne correle » alors que cela veut dire « la continuite n'est pas jointe ». Le
    # depot a paye ce zero-la ailleurs, sous la forme d'un compteur que personne ne remplissait.
    if len(rup) >= 3:
        # ⭐⭐⭐ LE CONFONDANT EST RETIRE, ET IL EST NOMME : `part_orientee` monte avec le rayon
        # ET la rupture de continuite monte avec le rayon, donc « la matiere repond mieux la ou
        # le transfert casse » et « la matiere repond mieux au bord » sont la MEME observation
        # tant que le rayon n'est pas tenu constant — et une seule des deux est un resultat.
        # L'instrument vient de `95`, importe et non recopie : deux implementations d'une
        # correlation partielle finiraient par ne pas s'accorder sur ce qu'elles retirent.
        from la_surface_et_la_feuille_par_rayon import correlation_partielle  # noqa: PLC0415

        ray_c = [x["rayon_mm"] for x in lues if x.get("continuite") is not None]
        r["resume"].update({
            # ⭐⭐⭐ LA QUESTION DU GRAAL, POSEE A LA MATIERE ET NON A UN MAILLAGE. « De combien
            # l'humain s'est-il ecarte de la matiere » est un signal dont le REFERENT est la
            # matiere, contrairement aux quatre candidats que `94` a `97` ont fermes — tous
            # calibres contre un maillage dont `97` a mesure qu'il n'a pas de valeur unique.
            "ecart_a_la_matiere_contre_continuite": correlation(amr, rup),
            "part_orientee_contre_continuite": correlation(orr, rup),
            "bandes_avec_continuite": len(rup),
            "ecart_a_la_matiere_contre_continuite_a_rayon_tenu": correlation_partielle(
                amr, rup, ray_c),
            "part_orientee_contre_continuite_a_rayon_tenu": correlation_partielle(
                orr, rup, ray_c),
            "part_orientee_contre_rayon": correlation(orr, ray_c),
            "continuite_contre_rayon": correlation(rup, ray_c),
        })
    else:
        r["resume"]["continuite_jointe"] = False
    return r


def joindre_la_continuite(r: dict) -> dict:
    """Rattacher a chaque bande sa rupture de continuite, lue de `92` et jamais recalculee.

    ⭐⭐ ELLE SE JOINT PAR L'IDENTITE DE LA BANDE, donc elle n'exige aucune relecture du volume :
    c'est une mesure EXTERIEURE indexee par bande, pas une quantite derivee de celle-ci. La
    recalculer ici en ferait une seconde definition de la meme chose.
    """
    if not CONTINUITE.is_file():
        return r
    co = {(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
    for x in r.get("lignes", []):
        if x.get("continuite") is None:
            x["continuite"] = co.get((x["de"], x["a"]), {}).get("rapport_interieur")
    return r


def reagreger(chemin: Path) -> dict:
    """Recalculer les verdicts DERIVES depuis un resultat deja ecrit, sans retoucher au volume.

    ⚠⚠ CE N'EST PAS UNE NOUVELLE MESURE, ET LE FICHIER LE DIT — meme partage que `100` : les
    lignes par bande sont la mesure, les verdicts n'en sont qu'une lecture. Ajouter une quantite
    derivee ne doit pas couter une heure de lecture reseau.
    """
    return agreger(joindre_la_continuite(json.loads(chemin.read_text())))


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    from la_normale_nest_pas_le_rayon import nombre_ou_absent  # noqa: PLC0415

    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · cube de {r['cote_du_cube_um']} µm de côté "
          f"({2 * r['demi_cube_voxels'] + 1}³ voxels de {r['voxel_fin_um']} µm) · "
          f"{r['bandes']} bandes\n")
    n = r["nul_du_tenseur"]
    print(f"barre : les deux moitiés du cube doivent s'accorder à moins de "
          f"{r['barre_daccord_des_moities_deg']}° — c'est le p1 du BRUIT PUR, dont le désaccord "
          f"médian vaut {n['accord_des_moities_median_deg']}°")
    print(f"⛔ la planarité est publiée mais RÉFUTÉE comme juge : elle retombe à "
          f"{n['planarite_mediane']} (le nul) là où la direction est encore juste — "
          f"anisotropie du nul ×{n['anisotropie_du_nul']}")
    print(f"défaut de similitude de la transformation : {r['defaut_de_similitude_deg']}° — "
          f"les angles sont {'' if r['les_angles_sont_transportables'] else 'NON '}"
          f"transportables d'un volume à l'autre\n")
    print(f"{'bande':>10} {'rayon':>6} {'cubes':>6} {'orientés':>9} {'désacc.':>8} "
          f"{'planar.':>8} {'∠ rayon':>9} {'∠ maillage':>11}")
    for x in r["lignes"]:
        if x.get("angle_matiere_rayon_deg") is None:
            print(f"  w{x['de']:03d}-{x['a']:03d} {nombre_ou_absent(x['rayon_mm']):>6.1f} "
                  f"{x['cubes_lus']:>6d} {'MUETTE':>9}")
            continue
        print(f"  w{x['de']:03d}-{x['a']:03d} {nombre_ou_absent(x['rayon_mm']):>6.1f} "
              f"{x['cubes_lus']:>6d} {x['part_orientee']:>9.2f} "
              f"{nombre_ou_absent(x['desaccord_des_moities_median_deg']):>7.1f}° "
              f"{nombre_ou_absent(x['planarite_mediane']):>8.3f} "
              f"{x['angle_matiere_rayon_deg']:>8.1f}° "
              f"{x['angle_matiere_maillage_deg']:>10.1f}°")
    s = r.get("resume")
    if not s:
        print("\n⚠ aucune bande orientée : la matière n'a pas répondu")
        return 0
    print(f"\n{'':>26} {'∠ au rayon':>12} {'∠ au maillage':>15}")
    print(f"{'médiane sur les bandes':>26} "
          f"{s['angle_matiere_rayon_median_deg']:>11.1f}° "
          f"{s['angle_matiere_maillage_median_deg']:>14.1f}°")
    if s["la_matiere_suit_le_maillage"]:
        print(f"\n★★★ LA MATIÈRE SUIT LE MAILLAGE : sa normale est à "
              f"{s['angle_matiere_maillage_median_deg']:.1f}° de celle du maillage")
        print(f"   contre {s['angle_matiere_rayon_median_deg']:.1f}° du rayon. L'obliquité de "
              f"`100` est donc RÉELLE : la matière")
        print("   elle-même est oblique au rayon, et le maillage humain la suit fidèlement.")
    else:
        print(f"\n★★★ LA MATIÈRE NE SUIT PAS LE MAILLAGE : sa normale est à "
              f"{s['angle_matiere_rayon_median_deg']:.1f}° du rayon")
        print(f"   contre {s['angle_matiere_maillage_median_deg']:.1f}° du maillage. C'est donc "
              f"le MAILLAGE qui est oblique à la")
        print("   matière — la surface tracée par les humains ne repose pas sur une feuille.")
    ax = r.get("un_axe_decale_est_il_lexplication", {})
    if "decalage_ajuste_mm" in ax:
        print(f"\n⭐⭐⭐ ET UN AXE MAL ESTIMÉ N'EST PAS L'EXPLICATION, parce qu'il prédit une "
              f"décroissance en 1/r :")
        print(f"   le décalage qui explique le cœur ({ax['decalage_qui_explique_le_coeur_mm']} "
              f"mm à {ax['rayon_le_plus_petit_mm']} mm de rayon) prédit "
              f"{ax['angle_predit_au_bord_par_ce_decalage_deg']}° au bord,")
        print(f"   où l'on mesure {ax['angle_mesure_au_bord_deg']}° ; celui qui explique le bord "
              f"({ax['decalage_qui_explique_le_bord_mm']} mm) prédit "
              f"{ax['angle_predit_au_coeur_par_ce_decalage_deg']}° au cœur, où l'on mesure "
              f"{ax['angle_mesure_au_coeur_deg']}°.")
        print(f"   Résidu du modèle d'axe {ax['residu_du_modele_daxe_deg']}° contre "
              f"{ax['residu_du_modele_constant_deg']}° pour une obliquité CONSTANTE — "
              f"l'axe explique "
              f"{'MIEUX' if ax['un_axe_decale_explique_mieux'] else 'MOINS BIEN'}.")
    if s.get("continuite_jointe") is False:
        print("\n⚠ la continuité de `92` n'est pas jointe : les corrélations ne sont pas "
              "calculées plutôt que rendues nulles")
    if "ecart_a_la_matiere_contre_continuite" in s:
        print(f"\n⭐⭐ ET LE SIGNAL DONT LE RÉFÉRENT EST LA MATIÈRE : l'écart du maillage à la "
              f"matière corrèle")
        print(f"   à {s['ecart_a_la_matiere_contre_continuite']:+.3f} avec la rupture de "
              f"continuité, et la part de cellules où la matière")
        print(f"   répond à {s['part_orientee_contre_continuite']:+.3f}.")
        print(f"\n⚠⚠ MAIS LE RAYON EST UN CONFONDANT, ET IL EST RETIRÉ : la part orientée "
              f"corrèle à {s['part_orientee_contre_rayon']:+.3f} avec le")
        print(f"   rayon et la rupture à {s['continuite_contre_rayon']:+.3f}, donc les deux "
              f"montent ensemble vers le bord. À rayon TENU")
        print(f"   constant, la part orientée tombe à "
              f"{s['part_orientee_contre_continuite_a_rayon_tenu']:+.3f} et l'écart à la matière "
              f"à {s['ecart_a_la_matiere_contre_continuite_a_rayon_tenu']:+.3f}.")
    print(f"\n⚠ « la matière a une orientation ici » et « voici laquelle » sont DEUX faits : "
          f"{100 * s['part_orientee_mediane']:.0f} %")
    print(f"   des cubes ont leurs DEUX MOITIÉS d'accord sous "
          f"{r['barre_daccord_des_moities_deg']}°, planarité médiane {s['planarite_mediane']}.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415

    # --- le cube, et sa forme -------------------------------------------------------------
    b = bloc(np.array([100.0, 200.0, 300.0]), demi=2)
    v("le cube a (2d+1)³ points", b.shape == (125, 3), str(b.shape))
    v("... et il est centré sur le point demandé",
      list(b.mean(axis=0)) == [100.0, 200.0, 300.0], str(b.mean(axis=0)))
    # ⚠ x doit varier le plus vite, sinon `voxel_distant` ne peut pas recoller une rangee.
    v("... et x varie le plus vite, ce qui permet le recollement en rangées",
      b[1, 2] == b[0, 2] + 1 and b[1, 0] == b[0, 0])

    # === LA FIXTURE PORTEUSE : UNE NORMALE CONNUE DOIT ETRE RETROUVEE =====================
    pas_vx = C.PAS_UM / C.VOXEL_FIN_UM
    for nom, u in (("radiale en x", (0.0, 0.0, 1.0)),
                   ("en z", (1.0, 0.0, 0.0)),
                   ("oblique 34° dans le plan", (0.0, np.sin(np.deg2rad(34.0)),
                                                 np.cos(np.deg2rad(34.0)))),
                   ("oblique en z et dans le plan", (0.35, 0.45, 0.82))):
        cube = cube_dun_empilement(u, pas_vx)
        d, val = tenseur_de_structure(cube)
        lu = angle_entre(d, u)
        v(f"une normale {nom} est retrouvée", lu < 3.0, f"{lu:.2f}° d'écart")
        v(f"... et la planarité y est franche ({nom})", planarite(val) > 0.9,
          f"{planarite(val):.3f}")

    # ⭐⭐⭐ LE BALAYAGE DE BRUIT, ET C'EST LUI QUI A CORRIGE LA CONCEPTION DU FICHIER. Le bruit
    # par voxel domine le signal par voxel d'un facteur SIX a sigma = 15 — et la direction reste
    # juste, parce qu'un bruit isotrope s'annule dans la MOYENNE des produits exterieurs.
    lim = limite_de_bruit(pas_vx, demis=(10, DEMI))
    petit = lim["cubes"]["10"]["lignes"][-1]
    grand = lim["cubes"][str(DEMI)]["lignes"][-1]
    v("le gradient du BRUIT par voxel dépasse celui du SIGNAL au bruit le plus fort",
      petit["gradient_du_bruit_par_voxel"] > 3 * lim["gradient_du_signal_par_voxel"],
      f"{petit['gradient_du_bruit_par_voxel']} contre "
      f"{lim['gradient_du_signal_par_voxel']}")
    v("... et un cube plus GRAND rend malgré tout la direction",
      grand["angle_deg"] < petit["angle_deg"] / 2.0,
      f"{grand['angle_deg']}° à demi={DEMI} contre {petit['angle_deg']}° à demi=10")
    v("... alors que sa PLANARITÉ est retombée au niveau du bruit pur",
      grand["planarite"] < 0.4, f"{grand['planarite']}")
    # ⛔⛔ D'OU LE REFUS DE LA PLANARITE COMME JUGE : elle ecarterait une direction juste.
    cube = cube_dun_empilement((0.0, 0.5, 0.866), pas_vx, demi=DEMI, bruit=15.0)
    d, val = tenseur_de_structure(cube)
    lu = angle_entre(d, (0.0, 0.5, 0.866))
    des, _ = accord_des_moities(cube)
    # ⚠ La barre de comparaison est le HASARD et non un seuil choisi : deux directions tirees au
    # hasard en trois dimensions font ~60° d'ecart, donc « mieux que 20° » est un enonce sur le
    # signal et pas un reglage.
    v("un empilement noyé dans le bruit a une direction JUSTE et une planarité NULLE",
      lu < 20.0 and planarite(val) < 0.4,
      f"{lu:.2f}° d'écart (le hasard en donne ~60) pour une planarité de "
      f"{planarite(val):.3f}")
    # ⭐⭐⭐ ET LA GARDE QUI LE LAISSE PASSER : les deux moities s'accordent.
    v("... et ses deux MOITIÉS s'accordent, donc la bonne garde le laisse passer",
      des < 25.0, f"{des:.2f}° entre les deux moitiés, contre ~60 au hasard")

    # ⭐⭐⭐ LE CONTROLE QUI DISTINGUE LE TENSEUR D'UNE ACP : prendre le PLUS PETIT vecteur propre
    # rendrait une direction TANGENTE, a 90° de la reponse, et parfaitement unitaire.
    cube = cube_dun_empilement((0.0, 0.0, 1.0), pas_vx)
    _, val = tenseur_de_structure(cube)
    g = np.gradient(cube)
    j = np.stack([g[0].ravel(), g[1].ravel(), g[2].ravel()], -1)
    j = j.T @ j / j.shape[0]
    va, ve = np.linalg.eigh(j)
    petit = angle_entre(ve[:, int(np.argsort(va)[0])], (0.0, 0.0, 1.0))
    v("le PLUS PETIT vecteur propre est à 90° de la réponse, donc le choix compte",
      petit > 80.0, f"{petit:.1f}°")

    # === LE CAS DEGENERE, DETECTE PLUTOT QUE REPONDU ======================================
    plat = np.full((21, 21, 21), 100.0)
    d, val = tenseur_de_structure(plat)
    v("un cube CONSTANT rend une planarité nulle, pas une direction",
      planarite(val) == 0.0, f"{planarite(val)}")
    v("... et sa direction reste finie, donc seule la planarité peut l'écarter",
      bool(np.isfinite(d).all()))

    # === LE MODELE NUL, SA BARRE ET SON ISOTROPIE =========================================
    nul = nul_du_tenseur(tirages=60, demi=10)
    v("le bruit pur répartit la variation sur les trois axes",
      abs(nul["planarite_mediane"] - 1 / 3) < 0.12, str(nul["planarite_mediane"]))
    # ⚠⚠ L'ISOTROPIE DU NUL EST UN CONTROLE SUR L'ESTIMATEUR, pas sur la matiere : si
    # `np.gradient` privilegiait un axe, le fichier lirait cette preference comme un resultat.
    v("... et la direction du nul est isotrope, donc l'estimateur ne préfère aucun axe",
      nul["anisotropie_du_nul"] < 1.25, str(nul["composantes_moyennes"]))
    # ⭐⭐⭐ LA BARRE QUI SERT : sur du bruit pur, deux moities du meme cube ne s'accordent PAS.
    # Deux directions tirees au hasard en trois dimensions font 60° en moyenne.
    v("sur du bruit pur, les deux moitiés d'un cube ne s'accordent pas",
      nul["accord_des_moities_median_deg"] > 30.0,
      f"{nul['accord_des_moities_median_deg']}° de désaccord médian")
    v("... et sa barre, le p1, reste franchissable par de la structure",
      0.5 < nul["accord_des_moities_p1_deg"] < 30.0,
      f"{nul['accord_des_moities_p1_deg']}°")
    # ⭐ Et un empilement doit passer SOUS cette barre, sinon l'instrument ne trancherait rien.
    # ⚠⚠ ET LA TAILLE DU CUBE DECIDE : a demi = 10 le meme empilement bruite NE PASSE PAS
    # (40,1° contre une barre de 15,5), parce qu'une moitie de dix plans n'en garde que huit
    # apres le rejet des bords. C'est exactement pourquoi `DEMI` est derive du balayage plutot
    # que choisi, et le contraste entre les deux tailles est asserte plutot que raconte.
    nul_grand = nul_du_tenseur(tirages=40, demi=DEMI)
    petit_cube = cube_dun_empilement((0.0, 0.3, 0.954), pas_vx, demi=10, bruit=8.0)
    grand_cube = cube_dun_empilement((0.0, 0.3, 0.954), pas_vx, demi=DEMI, bruit=8.0)
    des_petit, _ = accord_des_moities(petit_cube)
    des_grand, _ = accord_des_moities(grand_cube)
    v(f"un empilement bruité passe sous la barre dans un cube de demi={DEMI}",
      des_grand < nul_grand["accord_des_moities_p1_deg"],
      f"{des_grand:.2f}° contre {nul_grand['accord_des_moities_p1_deg']}°")
    v("... et il ne passe PAS dans un cube deux fois plus petit, ce qui est pourquoi la "
      "taille est dérivée",
      des_petit > nul["accord_des_moities_p1_deg"],
      f"{des_petit:.2f}° contre {nul['accord_des_moities_p1_deg']}°")

    # === LE SOUS-ECHANTILLONNAGE : MEME PORTEE, MOINS DE POINTS ===========================
    # ⭐⭐ Retrecir un cube change CE QU'ON REGARDE ; l'echantillonner plus grossierement change
    # seulement COMBIEN ON PAIE pour le regarder. Le controle verifie que la portee est bien
    # conservee, sinon les deux seraient confondus.
    b1 = bloc(np.array([100.0, 200.0, 300.0]), demi=10, pas=1)
    b2 = bloc(np.array([100.0, 200.0, 300.0]), demi=10, pas=2)
    v("un pas de 2 garde la MÊME portée physique",
      int(b1[:, 2].max() - b1[:, 2].min()) == int(b2[:, 2].max() - b2[:, 2].min()) == 20,
      f"{int(b2[:, 2].max() - b2[:, 2].min())} voxels d'arête dans les deux cas")
    # ⚠ Le rapport est (2d+1)³ / cote³ et non 2³ : a demi = 10 il vaut 6,96, pas 8. Le controle
    # verifie la FORMULE plutot qu'un nombre rond que j'avais suppose et qui etait faux.
    attendu = cote_du_bloc(10, 1) ** 3 / cote_du_bloc(10, 2) ** 3
    v("... mais lit près de sept fois moins de points, et le rapport suit la formule",
      abs(len(b1) / len(b2) - attendu) < 1e-9 and 6.5 < attendu < 7.5,
      f"{len(b1)} contre {len(b2)}, soit ×{attendu:.2f}")
    v("... et `cote_du_bloc` décrit la forme réellement produite",
      cote_du_bloc(10, 2) ** 3 == len(b2), f"{cote_du_bloc(10, 2)}³ pour {len(b2)}")
    # ⚠⚠⚠ LA BARRE DEPEND DE LA FORME, ET SON SENS NE SE DEVINE PAS. J'avais asserte qu'un cube
    # grossier a un nul PLUS HAUT — la mesure dit l'inverse a demi = 10 (7,31° contre 15,19°), et
    # le balayage montre qu'elle n'est pas monotone du tout (8,91 / 11,21 / 7,54 / 6,00 pour les
    # pas 1 a 4 a demi = 20). Ce qui compte n'est donc pas son SENS mais qu'elle soit REFAITE
    # pour chaque forme : reutiliser celle d'une autre comparerait deux choses.
    nul_fin = nul_du_tenseur(tirages=40, demi=10, pas=1)
    nul_gros = nul_du_tenseur(tirages=40, demi=10, pas=2)
    v("la barre DIFFÈRE d'une forme de cube à l'autre, donc elle ne se réutilise pas",
      abs(nul_gros["accord_des_moities_p1_deg"]
          - nul_fin["accord_des_moities_p1_deg"]) > 1.0,
      f"{nul_gros['accord_des_moities_p1_deg']}° contre "
      f"{nul_fin['accord_des_moities_p1_deg']}°")
    v("... et chaque nul déclare la forme qu'il a mesurée",
      nul_gros["pas_echantillon"] == 2 and nul_gros["cote_en_points"] == cote_du_bloc(10, 2))
    # ⭐⭐⭐ ET LE BALAYAGE COMPARE CHAQUE PAS A LA BARRE DE SA PROPRE FORME, donc il peut dire
    # qu'un pas NE tient PAS — sinon il approuverait n'importe quelle economie.
    lim = limite_de_sous_echantillonnage(pas_vx, demi=10, pas_echantillon=(1, 2, 8),
                                         tirages=2)
    v("le balayage de sous-échantillonnage juge chaque pas contre SA barre",
      all("barre_de_sa_forme_deg" in x for x in lim["lignes"]))
    # ⚠ Un pas de 8 sur un cube de demi = 10 laisse 3 points d'arete : chaque moitie en garde
    # une, donc `accord_des_moities` ne peut RIEN comparer et rend NaN. Le refus vient de la
    # garde qui avoue ne pas savoir, et c'est le bon mode d'echec — pas d'un seuil franchi.
    dernier = lim["lignes"][-1]
    v("... et il refuse un pas si grossier que les deux moitiés n'ont plus rien à comparer",
      not dernier["la_garde_tient"]
      and not np.isfinite(dernier["desaccord_des_moities_deg"]),
      f"pas 8 : {dernier['cote_en_points']} points d'arête, désaccord "
      f"{dernier['desaccord_des_moities_deg']}")

    # === LA CONDITION DE TRANSPORT DES ANGLES ==============================================
    from transformations_de_volume import (appliquer_direction,  # noqa: PLC0415
                                           defaut_de_similitude, matrice)

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is not None:
        v("la transformation conserve les angles, donc la confrontation a un sens",
          defaut_de_similitude(m) < 1.0, f"{defaut_de_similitude(m):.2f}°")
        # ⭐⭐ ET LE TRANSPORT PRESERVE L'ANGLE ENTRE DEUX DIRECTIONS, mesure plutot que suppose.
        r = np.random.default_rng(5)
        u = r.normal(size=(40, 3))
        w = r.normal(size=(40, 3))
        u = u / np.linalg.norm(u, axis=1, keepdims=True)
        w = w / np.linalg.norm(w, axis=1, keepdims=True)
        av = [angle_entre(u[i], w[i]) for i in range(len(u))]
        uf, wf = appliquer_direction(m, u), appliquer_direction(m, w)
        ap = [angle_entre(uf[i], wf[i]) for i in range(len(u))]
        ecart = float(np.max(np.abs(np.array(av) - np.array(ap))))
        v("... et l'angle entre deux directions survit au changement de volume",
          ecart < 1.0, f"{ecart:.3f}° d'écart maximal sur 40 paires")

    # === L'AXE DECALE, ET LE VERDICT DOIT POUVOIR DIRE OUI ================================
    v("un centre décalé de 3 mm fabrique 36,9° à 4 mm de rayon",
      abs(angle_dun_centre_decale(4.0, 3.0) - 36.87) < 0.1,
      f"{angle_dun_centre_decale(4.0, 3.0):.2f}°")
    v("... et seulement 7,1° à 24 mm, ce qui EST la signature en 1/r",
      abs(angle_dun_centre_decale(24.0, 3.0) - 7.13) < 0.1,
      f"{angle_dun_centre_decale(24.0, 3.0):.2f}°")
    # ⭐⭐⭐ LE CONTROLE QUI EMPECHE UN VERDICT QUI REFUTE TOUJOURS. Sur un jeu fabrique dont les
    # angles SUIVENT arctan(d/r), la refutation doit dire que l'axe explique — sinon son « non »
    # sur les vraies donnees ne voudrait rien dire.
    rayons = np.linspace(4.0, 24.0, 12)
    suit = {"lignes": [{"de": i, "a": i, "rayon_mm": float(rr),
                        "angle_matiere_rayon_deg": angle_dun_centre_decale(float(rr), 5.0),
                        "angle_matiere_maillage_deg": 10.0, "part_orientee": 0.5,
                        "continuite": None}
                       for i, rr in enumerate(rayons)]}
    verdict = refutation_du_centre_decale(suit["lignes"])
    v("un jeu dont les angles SUIVENT arctan(d/r) fait dire OUI au verdict",
      verdict["un_axe_decale_explique_mieux"],
      f"décalage ajusté {verdict['decalage_ajuste_mm']} mm pour 5,0 injectés")
    v("... et le décalage retrouvé est celui qui a été injecté",
      abs(verdict["decalage_ajuste_mm"] - 5.0) < 0.2,
      f"{verdict['decalage_ajuste_mm']} mm")
    # ⛔ Et un jeu d'angles CONSTANTS doit faire dire non.
    plat = {"lignes": [{"de": i, "a": i, "rayon_mm": float(rr),
                        "angle_matiere_rayon_deg": 34.0,
                        "angle_matiere_maillage_deg": 10.0, "part_orientee": 0.5,
                        "continuite": None}
                       for i, rr in enumerate(rayons)]}
    v("... alors qu'un jeu d'angles CONSTANTS fait dire non",
      not refutation_du_centre_decale(plat["lignes"])["un_axe_decale_explique_mieux"])

    # === UNE CORRELATION SANS DONNEE EST ABSENTE, PAS NULLE ================================
    # ⚠⚠⚠ LE ZERO QUI SE LIT COMME UN RESULTAT. `correlation` rend 0,0 sur une liste vide, ce
    # qui est juste comme repli et faux comme resultat publie : « +0,000 » se lit « rien ne
    # correle » alors que cela veut dire « la continuite n'est pas jointe ». Le defaut a ete
    # rencontre pour de vrai sur ce fichier, la premiere reagregation l'ayant affiche.
    sans = agreger({"lignes": [dict(x, continuite=None) for x in plat["lignes"]]})
    v("sans continuité, la corrélation est DÉCLARÉE absente et non rendue nulle",
      sans["resume"].get("continuite_jointe") is False
      and "ecart_a_la_matiere_contre_continuite" not in sans["resume"])
    avec = agreger({"lignes": [dict(x, continuite=1.0 + 0.5 * i)
                               for i, x in enumerate(plat["lignes"])]})
    v("... et avec la continuité, elle est calculée",
      "ecart_a_la_matiere_contre_continuite" in avec["resume"]
      and avec["resume"]["bandes_avec_continuite"] == len(rayons))
    # ⭐⭐ ET LE CONFONDANT DU RAYON EST RETIRE, AVEC L'INSTRUMENT DE `95` PLUTOT QU'UN SECOND.
    v("... et le rayon est retiré comme confondant",
      "part_orientee_contre_continuite_a_rayon_tenu" in avec["resume"])

    # === LES DONNEES REELLES ==============================================================
    # ⚠ Au moins douze cellules : `normale_de_la_grille` en perd sur les bords de grille, et
    # la mesure saute une bande qui en garde moins de dix — un contrôle a quatre cellules
    # sautait donc TOUTES les bandes en rendant « 0 bande », ce qui ressemble a une panne.
    r = mesurer(cellules=14, demi=6, bandes_max=2)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint le volume fin", r["bandes"] >= 1, f"{r['bandes']} bandes")
    v("les angles sont déclarés transportables, avec leur défaut",
      r["les_angles_sont_transportables"], f"{r['defaut_de_similitude_deg']}°")
    v("la barre vient du nul, pas d'un réglage",
      r["barre_daccord_des_moities_deg"]
      == r["nul_du_tenseur"]["accord_des_moities_p1_deg"])
    # ⛔⛔ ET LA PLANARITE EST PUBLIEE AVEC SON REFUS, sinon la publier inviterait a s'en servir.
    v("la limite de bruit du tenseur est publiée",
      "limite_de_bruit_du_tenseur" in r
      and len(r["limite_de_bruit_du_tenseur"]["cubes"]) == 2)
    if "resume" in r:
        s = r["resume"]
        # ⭐⭐⭐ LE VERDICT DOIT ETRE PRESENT ET NOMME, quel qu'il soit : les deux reponses sont
        # utiles, et c'est la marque d'une bonne mesure.
        v("le verdict qui distingue les deux lectures de `100` est rendu",
          "la_matiere_suit_le_maillage" in s
          and "ecart_entre_les_deux_lectures_deg" in s)
        v("« orientée » et « voici la direction » restent deux faits distincts",
          0.0 <= s["part_orientee_mediane"] <= 1.0, str(s["part_orientee_mediane"]))
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--demi", type=int, default=DEMI)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = reagreger(a.json)
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, demi=a.demi, bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
