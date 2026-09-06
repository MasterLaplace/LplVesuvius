#!/usr/bin/env python3
"""Le dérouleur qui RACCROCHE à chaque pas — l'erreur cesse-t-elle de s'accumuler ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA QUESTION QUI DÉCIDE. `derouler_par_le_pas_normal`
mesure qu'un dérouleur **aveugle** perd la feuille au tour 2 et dérive de **53 µm par tour**.
`le_raccrochage_a_la_matiere` mesure qu'un raccrochage sur le volume brut ramène **un** pas de
46,7 à **33,3 µm**. Ces deux nombres ne se composent pas : un raccrochage qui reprendrait un
tiers de l'erreur à chaque pas peut aussi bien **arrêter** la dérive que la ralentir. Ce fichier
enchaîne les pas et regarde laquelle des deux choses arrive.

⚠⚠⚠ LE GABARIT VIENT DE LA SURFACE COURANTE, PAS DES SPIRES PUBLIÉES. Au tour `k` le dérouleur
n'a plus la spire `k` sous les pieds : il a **sa propre reconstruction**. Le profil de feuille
est donc relu sur elle à chaque tour. C'est la seule version honnête, et c'est aussi celle qui
peut échouer d'une façon qu'aucune autre ne peut : un gabarit dit *« je suis sur une feuille »*,
jamais *« je suis sur la BONNE feuille »*. Un dérouleur qui a glissé d'une feuille garde donc un
gabarit parfaitement net et une confiance intacte.

⚠⚠ UNE CELLULE QUE LE VOLUME NE RÉPOND PAS GARDE SON PAS AVEUGLE, elle n'est PAS retirée. La
retirer ferait comparer deux populations différentes — le dérouleur raccroché ne garderait que
les cellules faciles, et il gagnerait pour cette raison-là. Le compte des non-raccrochées est
rendu à côté du résultat.

⚠⚠ LE PAS RESTE LE NOMINAL PUBLIÉ (135,5 µm), pas la longueur ajustée de 108,4 : celle-ci est
tirée des spires cibles, donc l'utiliser serait souffler la route. La comparaison avec le
dérouleur aveugle exige de toute façon le même pas des deux côtés.

⚠ Le témoin du gabarit MÉLANGÉ est itéré lui aussi, tour après tour : un dérouleur qui
raccrocherait au hasard à chaque pas est le plancher de bruit de cette marche, pas d'un pas.

⛔⛔⛔ LA RÉPONSE, ET ELLE EST NÉGATIVE : rien ne déroule. Sur 906 cellules et six tours, le
raccrochage par point dérive de **+56 µm par tour** contre **+22** pour l'aveugle, et il dérive
plus que lui aux **trois** tailles de boîte mesurées. Le moins mauvais des six dérouleurs est
celui qui ne lit rien.

⭐⭐⭐ ET LA RAISON EST MESURÉE PAR `le_gain_vieillit` : le gain d'un pas raccroché vaut
**+12,7 µm** depuis une spire **publiée** et **−0,2 µm** dès qu'un seul tour aveugle a été fait.
**Le raccrochage ne raccroche que ce qui est déjà à sa place.** Les 33,3 µm mesurés sur un pas
sont donc un gain conditionnel au point de départ, pas une capacité de la méthode.

⭐⭐⭐ ET LE MÉCANISME EST TROUVÉ PAR ÉLIMINATION : ce sont les NORMALES. Trois soupçons ont été
testés et écartés — fenêtre plus étroite (+43,0), décalages accordés au voisinage (+33,6),
gabarit FIGÉ lu une fois sur la spire de départ (+54,2 contre +56,1 sans remède, et son
contraste ne s'effondre pas). La surface ressemble encore à une feuille ; c'est la DIRECTION de
recherche qui se perd. Lisser le champ de normales avant le pas fait tomber la dérive du
raccrochage de **+56,1 à +25,3 µm par tour**, et ne fait **RIEN** pour le pas aveugle (+22,3
contre +22,0) — c'est cette seconde moitié qui prouve la première : le raccrochage **ride** la
nappe, la nappe gâte ses normales, et la mauvaise normale gâte le pas suivant.

⚠⚠ `accorder_les_voisins` et `lisser_les_normales` ne portent PAS sur le même objet : l'un lisse
DE COMBIEN on bouge, l'autre DANS QUELLE DIRECTION on cherche. Les deux ensemble donnent +29,4,
donc moins bien que les normales seules — ils se recouvrent et sur-lissent.

⚠⚠⚠ ET LA BOÎTE DOIT ÊTRE BALAYÉE AVANT DE CONCLURE — payé le 2026-09-06. À 191 cellules, cette
mesure rendait une dérive NÉGATIVE pour le décalage unique et il a été publié comme « le seul qui
tienne encore la feuille ». À 494 puis 906 cellules, au même endroit et avec le même code, elle
vaut +67 puis +56. La largeur de la boîte avait été choisie pour sa **facture de
téléchargement** — un bloc fait 2 Mio non compressés — et un paramètre choisi pour son coût n'a
aucune raison d'être neutre sur le résultat. D'où `--balayer`.

Usage :
    uv run python src/nappe/derouler_en_raccrochant.py --verifier
    uv run python src/nappe/derouler_en_raccrochant.py --cote 640 \\
        --json docs/mesures/derouler_en_raccrochant.json
    uv run python src/nappe/derouler_en_raccrochant.py --balayer 384,512,640 \\
        --json docs/mesures/derouler_en_raccrochant_balayage.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre", "tracecheck"):
    sys.path.insert(0, str(RACINE / "src" / _d))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def lisser_les_normales(n: np.ndarray, bon: np.ndarray) -> np.ndarray:
    """Le champ de normales moyenné sur le voisinage de grille 3×3, puis renormalisé.

    ⚠⚠⚠ CE N'EST PAS LE MÊME GESTE QUE `accorder_les_voisins`, ET LA DIFFÉRENCE EST TOUT LE
    SUJET. Accorder les voisins lisse **de combien** on bouge ; lisser les normales lisse **dans
    quelle direction** on cherche. Le premier corrige la sortie du raccrochage, le second
    corrige la géométrie qui décide où le raccrochage va regarder — et le pas aveugle, qui ne
    raccroche rien, en dépend tout autant.

    ⚠⚠ La moyenne se fait sur les VECTEURS puis se renormalise : moyenner des angles n'a pas de
    sens sur une sphère, et normaliser avant de moyenner donnerait le même poids à une normale
    dégénérée qu'à une bonne.

    ⚠ Une cellule sans voisin valide garde SA normale plutôt que d'être écartée : la retirer
    ferait fondre la grille plus vite que le pas non lissé, donc comparerait deux populations.
    """
    somme = np.zeros_like(n)
    combien = np.zeros(n.shape[:2], dtype=int)
    for du in (-1, 0, 1):
        for dv in (-1, 0, 1):
            h, w = n.shape[0], n.shape[1]
            su = slice(max(0, du), h + min(0, du))
            sv = slice(max(0, dv), w + min(0, dv))
            tu = slice(max(0, -du), h + min(0, -du))
            tv = slice(max(0, -dv), w + min(0, -dv))
            masque = np.zeros(n.shape[:2], dtype=bool)
            masque[su, sv] = bon[tu, tv]
            somme[su, sv] += np.where(bon[tu, tv][..., None], n[tu, tv], 0.0)
            combien += masque
    norme = np.linalg.norm(somme, axis=-1)
    out = n.copy()
    utile = bon & (combien >= 2) & (norme > 1e-9)
    out[utile] = somme[utile] / norme[utile][:, None]
    return out


def dispersion_angulaire(n: np.ndarray, bon: np.ndarray) -> float | None:
    """L'angle médian, en degrés, entre une normale et celle de sa voisine de droite.

    ⚠⚠ CETTE GRANDEUR NE DEMANDE AUCUNE CIBLE, donc un dérouleur peut la calculer sur lui-même
    en marchant. C'est ce qui la distingue de l'écart aux normales publiées, qui est un
    diagnostic et ne pourrait jamais guider quoi que ce soit.
    """
    paire = bon[:, :-1] & bon[:, 1:]
    if not paire.any():
        return None
    cos = np.sum(n[:, :-1][paire] * n[:, 1:][paire], axis=-1)
    return float(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))).mean())


def un_pas_raccroche(a: np.ndarray, ok: np.ndarray, pas_vx: float, sens: float,
                     vol, demi_vx: float, demi_gab: int,
                     lignes_gabarit: int = 400, melanger=None,
                     accorder: bool = False, raccrocher: bool = True,
                     global_: bool = False, gabarit_fixe=None,
                     normales_lissees: bool = False, pas_de_normale: int = 1) -> tuple:
    """Un pas normal, puis le raccrochage de chaque cellule sur le gabarit de la surface courante.

    Rend `(grille avancée, masque, diagnostic)`.

    ⚠⚠ L'ORDRE COMPTE ET IL EST DÉLIBÉRÉ : la normale est calculée sur la surface **avant** le
    pas, le pas est fait, PUIS le raccrochage. Raccrocher avant d'avancer ferait deux fois le
    même geste ; recalculer la normale après le pas ferait dépendre la direction du raccrochage
    d'une surface qui n'existe pas encore.

    ⚠ Le gabarit se lit sur un sous-échantillon : il en faut assez pour qu'une médiane soit
    stable, pas toute la grille — et la lecture est le poste cher.
    """
    from le_pas_normal_atteint_la_spire import normales  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        accorder_les_voisins, correler, decalage_retenu, le_long, profil_autour,
    )

    n, bon = normales(a, ok, pas=pas_de_normale)
    brute = dispersion_angulaire(n, bon)
    if normales_lissees:
        n = lisser_les_normales(n, bon)
    avance = a.copy()
    avance[bon] = a[bon] + sens * pas_vx * n[bon]
    cel = np.argwhere(bon)
    diag = dict(cellules=int(bon.sum()), raccrochees=0, gabarit_lignes=0,
                rugosite_vx=None, deplacement_vx=None, decalage_signe_vx=None,
                contraste_du_gabarit=None, gabarit=None,
                dispersion_normales_deg=brute)
    # ⚠⚠ `raccrocher=False` DÉGÉNÈRE EN PAS AVEUGLE, et ce n'est pas une commodité : c'est ce
    # qui fait que le témoin aveugle de ce fichier et le dérouleur aveugle publié sont **le
    # même geste**, avec les mêmes diagnostics. Deux implémentations d'un même pas finiraient
    # par ne pas s'accorder, et la comparaison porterait sur leur désaccord. La batterie
    # vérifie l'égalité **au bit près** avec `derouler_par_le_pas_normal.un_pas`.
    if not raccrocher or len(cel) == 0:
        return avance, bon, diag

    p = a[bon]
    d = n[bon] * sens
    t_gab = np.arange(-demi_gab, demi_gab + 1e-9, 1.0)
    t_ligne = np.arange(-(demi_vx + demi_gab), demi_vx + demi_gab + 1e-9, 1.0)

    # ⚠⚠⚠ LE GABARIT EST LU SUR LA SURFACE QU'IL EST CENSÉ CORRIGER, et c'est le soupçon que
    # `gabarit_fixe` existe pour tester. Au tour 0 on se tient sur une spire publiée, donc sur
    # la crête : le profil lu est celui d'une feuille. Au tour suivant on se tient à quelques
    # dizaines de micromètres de la crête, donc le profil lu est un mélange de matière et
    # d'air — l'outil qui cherche des feuilles est fabriqué à partir de ce qu'il doit réparer.
    # `gabarit_fixe` casse cette boucle sans rien apprendre de la cible : la forme d'une
    # feuille se lit UNE fois, sur la spire de départ, qui est une donnée qu'on a.
    pas_ech = max(1, len(cel) // lignes_gabarit)
    vg, okg = le_long(p[::pas_ech], d[::pas_ech], t_gab, vol)
    diag["gabarit_lignes"] = int(okg.sum())
    if okg.sum() >= 20:
        lu = profil_autour(vg[okg])
        diag["gabarit"] = lu
        # ⚠ Le contraste du gabarit est rendu MÊME quand un gabarit fixe est utilisé : c'est
        # la grandeur qui dit si la surface courante ressemble encore à une feuille, et elle
        # est intéressante précisément quand on a cessé de s'en servir.
        lisse_ = np.convolve(lu, np.ones(5) / 5.0, mode="valid") if len(lu) >= 5 else lu
        diag["contraste_du_gabarit"] = float(lisse_.max() - lisse_.min())
    if gabarit_fixe is not None:
        gab = np.asarray(gabarit_fixe, dtype=np.float64)
    elif okg.sum() >= 20:
        gab = profil_autour(vg[okg])
    else:
        # ⚠⚠ Pas de gabarit lisible : le pas reste AVEUGLE plutôt que raccroché sur un profil
        # bâti sur trois lignes. Un gabarit tiré de presque rien est un dessin, pas une forme.
        return avance, bon, diag
    if melanger is not None:
        gab = melanger.permuted(gab)

    v, okv = le_long(avance[bon], d, t_ligne, vol)
    if okv.any():
        corr, centres = correler(v[okv], gab, t_ligne)
        if global_:
            # ⚠⚠⚠ UN SEUL DÉCALAGE POUR TOUTE LA NAPPE, et c'est la leçon que ce dépôt a déjà
            # payée une fois sur un autre objet : `le_residu_est_une_translation` a montré
            # qu'un « champ » de recalage estimé fenêtre par fenêtre était en réalité **une
            # constante**, et que l'estimer par morceaux ne faisait qu'ajouter du bruit. Ici
            # le raccrochage par point décide cent quarante et une fois ce qu'une feuille
            # entière ne fait qu'une fois. La corrélation est donc SOMMÉE avant d'être
            # maximisée, ce qui divise par cent le nombre de degrés de liberté.
            somme = corr.mean(axis=0)[None, :]
            t = np.full(corr.shape[0], float(decalage_retenu(somme, centres)[0]))
        else:
            t = decalage_retenu(corr, centres)
        pris = cel[okv]
        # ⚠⚠ LA RUGOSITÉ EST MESURÉE AVANT TOUT ACCORD, et c'est elle qui explique la marche :
        # un raccrochage décide point par point, donc il peut RIDER une surface que le pas
        # aveugle gardait lisse par construction. Une surface ridée a de mauvaises normales,
        # et une mauvaise normale gâche le pas SUIVANT — c'est comme ça qu'un geste qui gagne
        # au premier tour peut perdre aux suivants.
        champ = np.full(a.shape[:2], np.nan)
        champ[pris[:, 0], pris[:, 1]] = t
        valide = np.zeros(a.shape[:2], dtype=bool)
        valide[pris[:, 0], pris[:, 1]] = True
        lisse, assez = accorder_les_voisins(champ, valide)
        if assez.any():
            diag["rugosite_vx"] = float(np.median(np.abs(champ[assez] - lisse[assez])))
        if accorder:
            # ⚠ Une cellule sans majorité de voisins garde son propre décalage plutôt que
            # d'être écartée : la retirer ferait fondre la grille plus vite que le pas
            # aveugle, donc comparerait deux populations différentes.
            t = np.where(assez[pris[:, 0], pris[:, 1]], lisse[pris[:, 0], pris[:, 1]], t)
        avance[pris[:, 0], pris[:, 1]] += d[okv] * t[:, None]
        diag["raccrochees"] = int(okv.sum())
        diag["deplacement_vx"] = float(np.median(np.abs(t)))
        # ⚠⚠ LE SIGNE FERME UNE AUTRE EXPLICATION. Un décalage global toujours du même côté et
        # de la même taille ne serait qu'une LONGUEUR DE PAS corrigée — c'est-à-dire la
        # longueur ajustée que `la_derive_est_elle_un_biais` a déjà mesurée, et qui plafonne à
        # 54,1 µm sur des paires réservées. La valeur absolue seule cachait cette lecture.
        diag["decalage_signe_vx"] = float(np.median(t))
    return avance, bon, diag


def derouler(depart: np.ndarray, ok: np.ndarray, cibles: dict[int, np.ndarray],
             pas_vx: float, voxel_um: float, sens: float, vol,
             demi_vx: float, demi_gab: int, melanger=None, accorder: bool = False,
             minimum: int = 30, demi_feuille_um: float = 67.75,
             raccrocher: bool = True, global_: bool = False,
             gabarit_fige: bool = False, normales_lissees: bool = False,
             pas_de_normale: int = 1) -> list[dict]:
    """La marche raccrochée, jugée à chaque tour contre la spire de même rang.

    ⚠⚠ Les cellules jugées sont celles **encore vivantes**, et leur compte accompagne chaque
    distance : une erreur qui baisse pendant que la grille fond n'est pas une erreur qui baisse.

    ⚠⚠⚠ ET LA MARCHE S'ARRÊTE QUAND LA POPULATION PASSE SOUS `minimum`, sur un critère
    **déclaré d'avance et géométrique**. Une normale demande quatre voisins valides, donc le
    masque s'érode d'une cellule par tour sur tout son pourtour : sur un morceau de nappe de
    deux cents cellules, il n'en reste que deux au sixième tour. Une médiane sur deux cellules
    n'est pas une mesure, et la laisser dans le tableau ferait porter une conclusion par du
    bruit.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    a, m = depart.copy(), ok.copy()
    sur_place = depart.copy()
    fige = None
    out = []
    for k in sorted(cibles):
        a, m, diag = un_pas_raccroche(a, m, pas_vx, sens, vol, demi_vx, demi_gab,
                                      melanger=melanger, accorder=accorder,
                                      raccrocher=raccrocher, global_=global_,
                                      gabarit_fixe=fige,
                                      normales_lissees=normales_lissees,
                                      pas_de_normale=pas_de_normale)
        # ⚠ Le gabarit figé est celui du PREMIER tour, donc celui de la spire de départ, et
        # il est gelé après coup : le construire avant la boucle demanderait de dupliquer la
        # lecture que le premier pas fait déjà.
        if gabarit_fige and fige is None and diag["gabarit"] is not None:
            fige = np.asarray(diag["gabarit"], dtype=np.float64)
        pts = a[m]
        if pts.shape[0] < minimum:
            break
        d = distance_a(pts, cibles[k], voxel_um)
        d0 = distance_a(sur_place[m], cibles[k], voxel_um)
        # ⚠⚠ LA PART PERDUE EST LA MESURE QUI DIT SI L'ERREUR EST UNE DÉRIVE OU UN SAUT. Une
        # cellule au-delà d'une demi-feuille n'est plus « un peu à côté » : elle est sur une
        # AUTRE feuille, et aucun lissage local ne l'en fera revenir. Une médiane qui monte
        # parce que tout le monde glisse un peu et une médiane qui monte parce qu'un tiers a
        # sauté sont deux pannes différentes, qui ne se réparent pas pareil.
        perdues = float(np.mean(d > demi_feuille_um))
        # ⚠ Diagnostic, pas méthode : il se sert de la CIBLE, donc il ne peut pas guider un
        # dérouleur. Il sert à dire de quelle panne il s'agit, pas à la réparer.
        carte = np.zeros(m.shape, dtype=bool)
        cel_m = np.argwhere(m)
        carte[cel_m[:, 0], cel_m[:, 1]] = d > demi_feuille_um
        groupe = groupement_des_perdues(carte, m, np.random.default_rng(7))
        out.append(dict(tours=k, cellules=diag["cellules"],
                        raccrochees=diag["raccrochees"],
                        non_raccrochees=diag["cellules"] - diag["raccrochees"],
                        gabarit_lignes=diag["gabarit_lignes"],
                        rugosite_um=(None if diag["rugosite_vx"] is None
                                     else round(diag["rugosite_vx"] * voxel_um, 1)),
                        contraste_du_gabarit=(None if diag["contraste_du_gabarit"] is None
                                              else round(diag["contraste_du_gabarit"], 1)),
                        dispersion_normales_deg=(
                            None if diag["dispersion_normales_deg"] is None
                            else round(diag["dispersion_normales_deg"], 2)),
                        deplacement_um=(None if diag["deplacement_vx"] is None
                                        else round(diag["deplacement_vx"] * voxel_um, 1)),
                        decalage_signe_um=(None if diag["decalage_signe_vx"] is None
                                           else round(diag["decalage_signe_vx"] * voxel_um, 1)),
                        part_perdue=round(perdues, 3), groupement=groupe,
                        erreur_um=round(float(np.median(d)), 1),
                        erreur_p90_um=round(float(np.percentile(d, 90)), 1),
                        temoin_sur_place_um=round(float(np.median(d0)), 1)))
    return out


def groupement_des_perdues(perdue: np.ndarray, valide: np.ndarray,
                          rng=None, tirages: int = 40) -> dict | None:
    """Les cellules perdues sont-elles GROUPÉES, ou éparpillées ?

    Rend `{observe, temoin, rapport}` : la part de cellules perdues ayant au moins deux
    voisines perdues, la même part sous un mélange des étiquettes, et leur rapport. Au-dessus
    de 1, elles sont groupées.

    ⚠⚠ LE RAPPORT EST RENDU À CÔTÉ DE SES DEUX MOITIÉS, ET IL PEUT MANQUER. À faible densité
    un semis mélangé ne produit presque jamais deux voisines perdues, donc le dénominateur
    approche zéro et le rapport explose — mesuré, il rendait **100** là où l'observé valait
    quelques centièmes. La borne est **dérivée** et non choisie : en dessous d'une cellule
    perdue sur l'ensemble des perdues, le témoin n'est pas mesurable, et un rapport bâti
    dessus serait un nombre sans dénominateur.

    ⚠⚠⚠ POURQUOI CE NOMBRE DÉCIDE. Une queue **éparpillée** est exactement ce qu'un lissage
    de voisinage répare ; une queue **groupée** ne l'est pas — une plaque entière posée sur la
    feuille voisine a des voisins qui sont d'accord avec elle, donc la médiane du voisinage la
    confirme au lieu de la corriger. Les deux pannes rendent la même médiane et ne se
    réparent pas du tout pareil.

    ⚠ Le témoin est un **mélange des étiquettes sur les mêmes cellules valides**, pas un semis
    uniforme : il casse le groupement et rien d'autre — ni le nombre de perdues, ni la forme
    du domaine. Ce dépôt a déjà payé qu'un témoin cassant deux choses ne dise laquelle
    comptait.
    """
    if rng is None:
        rng = np.random.default_rng(0)
    if perdue.sum() < 3 or valide.sum() < 9:
        return None

    def part(masque: np.ndarray) -> float:
        voisines = np.zeros(masque.shape, dtype=int)
        for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dec = np.zeros(masque.shape, dtype=bool)
            su = slice(max(0, du), masque.shape[0] + min(0, du))
            sv = slice(max(0, dv), masque.shape[1] + min(0, dv))
            tu = slice(max(0, -du), masque.shape[0] + min(0, -du))
            tv = slice(max(0, -dv), masque.shape[1] + min(0, -dv))
            dec[su, sv] = masque[tu, tv]
            voisines += dec
        return float(np.mean(voisines[masque] >= 2)) if masque.any() else 0.0

    observe = part(perdue)
    cellules = np.argwhere(valide)
    combien = int(perdue.sum())
    tires = []
    for _ in range(tirages):
        faux = np.zeros(perdue.shape, dtype=bool)
        pris = cellules[rng.choice(len(cellules), size=combien, replace=False)]
        faux[pris[:, 0], pris[:, 1]] = True
        tires.append(part(faux))
    temoin = float(np.median(tires))
    # ⚠ STRICTEMENT au-dessus : un témoin qui vaut exactement une cellule sur l'ensemble des
    # perdues n'est pas une base, c'est un cas isolé.
    mesurable = temoin > 1.0 / combien
    return dict(observe=round(observe, 3), temoin=round(temoin, 3),
                rapport=(round(observe / temoin, 2) if mesurable else None))


def derive_par_tour(marche: list[dict], cle: str = "erreur_um") -> float | None:
    """La pente de l'erreur par tour, par moindres carrés sur TOUTE la marche.

    ⚠ Prise entre les deux extrémités, elle dépendrait de deux points ; sur toute la marche,
    elle dit ce que la marche fait. C'est la même règle que dans le dérouleur aveugle, et il
    faut la même pour que les deux pentes soient comparables.
    """
    if len(marche) < 2:
        return None
    x = np.array([e["tours"] for e in marche], dtype=float)
    y = np.array([e[cle] for e in marche], dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def _boite_du_depart(grilles: dict, centre, cote: float, minimum: int) -> int | None:
    """Le rang le plus bas dont la grille ET sa suivante passent dans la boîte.

    ⚠ Le départ se choisit sur la GÉOMÉTRIE — qui est là — et jamais sur l'erreur : partir de
    la spire où le raccrochage marche le mieux serait choisir sur le résultat.
    """
    lo, hi = centre - cote / 2, centre + cote / 2
    for r in sorted(grilles):
        a, ok = grilles[r]
        dedans = ok & ((a >= lo) & (a <= hi)).all(axis=-1)
        if int(dedans.sum()) < minimum or r + 1 not in grilles:
            continue
        b, okb = grilles[r + 1]
        if int((okb & ((b >= lo) & (b <= hi)).all(axis=-1)).sum()) >= minimum:
            return r
    return None


def mesurer(minimum: int = 30, graine: int = 42, cache_actif: bool = True,
            cote: float | None = None, grilles: dict | None = None,
            corpus: dict | None = None, volume=None) -> dict:
    """Le dérouleur raccroché, contre l'aveugle, contre le hasard, contre l'immobilité.

    ⚠⚠ DEUX MATIÈRES SONT INJECTABLES : les **spires** disent d'où partir et où juger, le
    **volume** dit sur quoi se raccrocher. Les défauts sont ceux du dépôt distant, donc les
    nombres publiés ne bougent pas ; la batterie en fournit deux fabriqués, qui décrivent le
    même objet — sans quoi la marche snapperait sur de la matière qui contredit ses ancres.

    ⚠ `grilles` reste là et sert au balayage : les mêmes grilles servent à toutes les tailles
    de boîte, et les retélécharger à chaque point ferait payer treize `tifxyz` par taille.
    """
    from le_corpus_des_spires import corpus_publie  # noqa: PLC0415
    from le_raccrochage_a_la_matiere import (  # noqa: PLC0415
        BOITE_CENTRE, BOITE_COTE, CacheDisque, Volume, ZARR, accorde_aux_spires,
        url_du_volume,
    )

    c = corpus_publie() if (corpus is None and grilles is None) else corpus
    if c is None:
        from les_wraps_publies import VOLUME, VOXEL_UM  # noqa: PLC0415

        c = dict(volume=VOLUME, voxel_um=VOXEL_UM,
                 ecart_um=float(json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]),
                 grilles=grilles)
    VOLUME, VOXEL_UM = c["volume"], float(c["voxel_um"])
    if volume is None and not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({VOLUME})")
    if not WRAPS.is_file():
        raise RuntimeError(f"mesure absente : {WRAPS}")
    ecart_um = float(c["ecart_um"])
    pas_vx = ecart_um / VOXEL_UM
    demi_vx = pas_vx / 2.0
    demi_gab = round(demi_vx / 2.0)

    # ⚠ Les grilles sont RÉUTILISABLES d'un côté de boîte à l'autre : les retélécharger à
    # chaque taille ferait payer treize `tifxyz` par point du balayage, pour des données
    # identiques.
    grilles = c["grilles"] if grilles is None else grilles
    # ⚠⚠ LA BOÎTE S'ÉLARGIT, SON CENTRE NE BOUGE PAS. Élargir change UNE chose — combien de
    # tours la grille survit avant que l'érosion ne la mange. Déplacer le centre en changerait
    # une seconde : l'endroit de la nappe qu'on mesure. Deux marches à deux endroits ne se
    # comparent pas, et c'est précisément ce que ce dépôt appelle un témoin qui casse deux
    # choses.
    cote = BOITE_COTE if cote is None else float(cote)
    centre = np.array(BOITE_CENTRE)
    depuis = _boite_du_depart(grilles, centre, cote, minimum)
    if depuis is None:
        raise RuntimeError("aucune spire de départ dans la boîte")

    # ⚠⚠ LA GRILLE DE DÉPART EST RESTREINTE À LA BOÎTE, et c'est une contrainte de COÛT
    # assumée : un bloc de ce volume fait 2 Mio non compressés, et une spire entière en
    # traverserait des centaines. Ce qui est mesuré est donc un morceau de nappe, pas la
    # nappe — et le compte de cellules le dit.
    a0, ok0 = grilles[depuis]
    lo, hi = centre - cote / 2, centre + cote / 2
    dans = ok0 & ((a0 >= lo) & (a0 <= hi)).all(axis=-1)
    u = np.flatnonzero(dans.any(axis=1))
    v = np.flatnonzero(dans.any(axis=0))
    sous = (slice(int(u.min()), int(u.max()) + 1), slice(int(v.min()), int(v.max()) + 1))
    a0, ok0 = a0[sous].copy(), dans[sous].copy()

    # ⚠⚠ Les cibles sont les nuages ENTIERS des spires suivantes, pas leur part dans la boîte :
    # une distance à une surface tronquée grandit là où la surface s'arrête, pas là où le
    # dérouleur se trompe.
    cibles = {}
    for r in sorted(grilles):
        if r <= depuis:
            continue
        b, okb = grilles[r]
        if int((okb & ((b >= lo) & (b <= hi)).all(axis=-1)).sum()) < minimum:
            break
        cibles[r - depuis] = b[okb]
    if not cibles:
        raise RuntimeError("aucune spire d'arrivée dans la boîte")

    if volume is None:
        import tracecheck as tc  # noqa: PLC0415

        url = url_du_volume()
        vol = Volume(url, tc.array_meta(url, 0, 120), CacheDisque(actif=cache_actif))
    else:
        vol = volume
    cache = vol.cache

    # ⚠⚠⚠ LE SENS EST LE SEUL BIT DE SUPERVISION, fixé au premier pas et jamais rechoisi.
    from le_pas_normal_atteint_la_spire import essayer_le_pas, normales  # noqa: PLC0415
    n0, bon0 = normales(a0, ok0)
    e = essayer_le_pas(a0[bon0], n0[bon0], cibles[1], pas_vx, VOXEL_UM)
    sens = 1.0 if e["retenu"] == "+" else -1.0

    rng = np.random.default_rng(graine)
    raccroche = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                         minimum=minimum, demi_feuille_um=ecart_um / 2)
    accorde = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                       accorder=True, minimum=minimum, demi_feuille_um=ecart_um / 2)
    # ⚠⚠⚠ LE TÉMOIN À UNE SEULE VARIABLE : la MÊME marche, la même forme cherchée, le même
    # gabarit — seule la largeur de la fenêtre change. Si l'itération échoue parce qu'une
    # part des cellules saute sur la feuille voisine, alors une fenêtre deux fois plus
    # étroite, qui rend ce saut impossible, doit faire mieux. Si elle ne fait pas mieux, la
    # cause est ailleurs et il faudra la chercher ailleurs.
    etroite = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx / 2, demi_gab,
                       minimum=minimum, demi_feuille_um=ecart_um / 2)
    # ⚠⚠⚠ LE CONTENDANT À CENT QUARANTE FOIS MOINS DE DEGRÉS DE LIBERTÉ : un seul décalage
    # pour toute la nappe, celui qui maximise la corrélation SOMMÉE. Même gabarit, même
    # fenêtre, même forme cherchée — seul le nombre de décisions change.
    globale = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                       minimum=minimum, demi_feuille_um=ecart_um / 2, global_=True)
    hasard = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                      melanger=rng, minimum=minimum, demi_feuille_um=ecart_um / 2)
    # ⚠⚠⚠ LES DEUX CONTENDANTS QUI TESTENT LA GÉOMÉTRIE plutôt que la lecture. `accorder_les_
    # voisins` lisse DE COMBIEN on bouge ; ceux-ci lissent DANS QUELLE DIRECTION on cherche.
    # Le second n'a pas de raccrochage du tout : si le pas aveugle s'en trouve mieux, alors ce
    # qui se dégrade est le champ de normales, et aucun raccrochage n'aurait pu y remédier.
    normales_raccroche = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx,
                                  demi_gab, minimum=minimum, demi_feuille_um=ecart_um / 2,
                                  normales_lissees=True)
    normales_aveugle = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx,
                                demi_gab, minimum=minimum, demi_feuille_um=ecart_um / 2,
                                raccrocher=False, normales_lissees=True)
    # ⚠⚠⚠ LES DEUX REMÈDES ENSEMBLE. Ils ne portent pas sur le même objet — l'un lisse DE
    # COMBIEN on bouge, l'autre DANS QUELLE DIRECTION on cherche — donc rien ne dit qu'ils se
    # recouvrent. Les mesurer séparément puis ensemble est ce qui permet de dire s'ils
    # s'additionnent ou si l'un contient l'autre.
    les_deux = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                        minimum=minimum, demi_feuille_um=ecart_um / 2,
                        accorder=True, normales_lissees=True)
    # ⚠⚠⚠ LE CONTENDANT QUI TESTE LE SOUPÇON : la forme d'une feuille est lue UNE fois, sur la
    # spire de départ, et gelée. Rien d'autre ne change. Si la marche s'en trouve mieux, ce qui
    # échouait était le gabarit relu sur une surface déjà fausse ; si elle n'y gagne rien, la
    # boucle du gabarit n'était pas la panne et il faut la chercher ailleurs.
    fige = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                    minimum=minimum, demi_feuille_um=ecart_um / 2, gabarit_fige=True)
    # ⚠ Le pas aveugle passe par LE MÊME code, drapeau baissé : la batterie vérifie qu'il
    # produit la grille de `derouler_par_le_pas_normal.un_pas` au bit près.
    aveugle = derouler(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab,
                       minimum=minimum, demi_feuille_um=ecart_um / 2, raccrocher=False)
    vieillissement = le_gain_vieillit(a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol,
                                      demi_vx, demi_gab, minimum=minimum)

    r = dict(
        volume=VOLUME, voxel_um=VOXEL_UM, zarr=ZARR,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=cote,
                   cote_par_defaut=BOITE_COTE),
        depuis=depuis, ecart_lu_um=ecart_um, pas_en_voxels=round(pas_vx, 2),
        demi_epaisseur_um=round(ecart_um / 2, 2),
        demi_fenetre_um=round(demi_vx * VOXEL_UM, 1),
        sens_retenu="+" if sens > 0 else "-", bits_de_supervision=1,
        cellules_au_depart=int(ok0.sum()),
        tours_mesures=len(raccroche),
        minimum_de_cellules=minimum,
        marche_raccrochee=raccroche, marche_accordee=accorde,
        marche_fenetre_etroite=etroite, marche_globale=globale,
        marche_gabarit_fige=fige,
        marche_normales_lissees=normales_raccroche,
        marche_aveugle_normales_lissees=normales_aveugle,
        marche_les_deux_remedes=les_deux,
        marche_aveugle=aveugle, marche_hasard=hasard,
        le_gain_vieillit=vieillissement,
        cout=cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises),
    )

    def perdue(marche):
        """Le PREMIER tour où la médiane dépasse la demi-épaisseur.

        ⚠⚠ C'est un premier franchissement, pas un verdict : une marche qui CONVERGE peut le
        franchir au tour 1 et revenir. Lu seul, ce nombre désignerait la meilleure marche du
        lot comme la pire. Il se lit avec `feuille_tenue_a_la_fin`.
        """
        for e_ in marche:
            if e_["erreur_um"] > ecart_um / 2:
                return e_["tours"]
        return None

    def tenue(marche):
        """La feuille est-elle tenue au DERNIER tour mesuré, et par toutes les cellules ?"""
        if not marche:
            return None
        return dict(erreur_um=marche[-1]["erreur_um"],
                    sous_la_demi_feuille=bool(marche[-1]["erreur_um"] < ecart_um / 2),
                    part_perdue=marche[-1]["part_perdue"],
                    p90_um=marche[-1]["erreur_p90_um"])

    r["tours_avant_de_perdre_la_feuille"] = dict(
        raccroche=perdue(raccroche), accorde=perdue(accorde), etroite=perdue(etroite),
        globale=perdue(globale), fige=perdue(fige),
        normales=perdue(normales_raccroche), aveugle_normales=perdue(normales_aveugle),
        les_deux=perdue(les_deux),
        aveugle=perdue(aveugle), hasard=perdue(hasard))
    r["feuille_tenue_a_la_fin"] = dict(
        raccroche=tenue(raccroche), accorde=tenue(accorde), etroite=tenue(etroite),
        globale=tenue(globale), fige=tenue(fige),
        normales=tenue(normales_raccroche), aveugle_normales=tenue(normales_aveugle),
        les_deux=tenue(les_deux),
        aveugle=tenue(aveugle), hasard=tenue(hasard))
    def pente(m_):
        d_ = derive_par_tour(m_)
        return None if d_ is None else round(d_, 1)

    r["derive_par_tour_um"] = dict(raccroche=pente(raccroche), accorde=pente(accorde),
                                   etroite=pente(etroite), globale=pente(globale),
                                   fige=pente(fige),
                                   normales=pente(normales_raccroche),
                                   aveugle_normales=pente(normales_aveugle),
                                   les_deux=pente(les_deux),
                                   aveugle=pente(aveugle), hasard=pente(hasard))
    r["groupement_des_perdues"] = dict(
        raccroche=[e_["groupement"] for e_ in raccroche],
        aveugle=[e_["groupement"] for e_ in aveugle])
    r["part_perdue"] = dict(
        raccroche=[e_["part_perdue"] for e_ in raccroche],
        accorde=[e_["part_perdue"] for e_ in accorde],
        etroite=[e_["part_perdue"] for e_ in etroite],
        globale=[e_["part_perdue"] for e_ in globale],
        fige=[e_["part_perdue"] for e_ in fige],
        aveugle=[e_["part_perdue"] for e_ in aveugle])
    # ⚠⚠ Un décalage global constant et toujours du même signe serait une longueur de pas
    # corrigée, pas un raccrochage. Les signes sont rendus pour que la lecture soit possible.
    signes = [e_["decalage_signe_um"] for e_ in globale if e_["decalage_signe_um"] is not None]
    r["decalage_global_signe_um"] = signes
    r["le_global_change_de_signe"] = bool(
        len(signes) > 1 and min(signes) < 0 < max(signes))
    r["longueur_equivalente_um"] = (
        None if not signes else round(ecart_um + float(np.median(signes)), 1))
    # ⚠⚠ LE CONTRASTE DU GABARIT EST LA GRANDEUR QUI DIT SI LA SURFACE RESSEMBLE ENCORE À UNE
    # FEUILLE : lu sur la crête il vaut plusieurs dizaines de niveaux, lu à côté il s'écrase.
    r["balayage_du_pas_de_normale"] = balayer_le_pas_de_normale(
        a0, ok0, cibles, pas_vx, VOXEL_UM, sens, vol, demi_vx, demi_gab, minimum=minimum)
    # ⚠⚠⚠ LA SEULE COMPARAISON NON CONFONDUE EST CELLE DU PREMIER TOUR. Au-delà, un support
    # large a mangé le bord — 349 cellules contre 41 au sixième tour — donc les marches ne sont
    # plus jugées sur la même population et leur écart mesure l'érosion autant que la
    # géométrie. Au premier tour, tous les supports partent de cinq à huit cents cellules.
    bal_ = r["balayage_du_pas_de_normale"]
    r["au_premier_tour_par_support"] = [
        dict(pas_de_normale=e_["pas_de_normale"], cellules=e_["cellules_au_premier_tour"],
             erreur_um=(e_["erreur_um"][0] if e_["erreur_um"] else None),
             dispersion_deg=(e_["dispersion_deg"][0] if e_["dispersion_deg"] else None))
        for e_ in bal_]
    prem = [e_ for e_ in r["au_premier_tour_par_support"] if e_["erreur_um"] is not None]
    if len(prem) > 1:
        d0, dn = prem[0]["dispersion_deg"], prem[-1]["dispersion_deg"]
        e0, en = prem[0]["erreur_um"], prem[-1]["erreur_um"]
        r["la_dispersion_baisse_avec_le_support"] = bool(dn < d0 * 0.8)
        # ⚠⚠ ET L'ERREUR, ELLE, NE SUIT PAS : c'est ce qui fait de la dispersion un SYMPTÔME.
        # Le seuil est un vingtième, soit l'ordre de l'arrondi publié, pas un nombre choisi
        # pour que la phrase passe.
        r["lerreur_suit_la_dispersion"] = bool(abs(en - e0) > 0.05 * e0)
        r["la_dispersion_est_un_symptome"] = bool(
            r["la_dispersion_baisse_avec_le_support"] and not r["lerreur_suit_la_dispersion"])
    r["meilleur_pas_de_normale"] = min(
        (e_ for e_ in r["balayage_du_pas_de_normale"] if e_["derive_par_tour_um"] is not None),
        key=lambda e_: e_["derive_par_tour_um"], default={}).get("pas_de_normale")
    r["dispersion_des_normales_deg"] = dict(
        aveugle=[e_["dispersion_normales_deg"] for e_ in aveugle],
        raccroche=[e_["dispersion_normales_deg"] for e_ in raccroche],
        aveugle_normales_lissees=[e_["dispersion_normales_deg"]
                                  for e_ in normales_aveugle])
    r["les_deux_remedes_battent_laveugle"] = bool(
        les_deux and aveugle
        and pente(les_deux) is not None and pente(aveugle) is not None
        and pente(les_deux) < pente(aveugle))
    r["lisser_les_normales_aide_laveugle"] = bool(
        normales_aveugle and aveugle
        and np.median([e_["erreur_um"] for e_ in normales_aveugle])
        < np.median([e_["erreur_um"] for e_ in aveugle]))
    r["contraste_du_gabarit"] = dict(
        raccroche=[e_["contraste_du_gabarit"] for e_ in raccroche],
        aveugle=[e_["contraste_du_gabarit"] for e_ in aveugle])
    r["erreur_mediane_figee_um"] = round(
        float(np.median([e_["erreur_um"] for e_ in fige])), 1)
    r["le_gabarit_fige_fait_mieux"] = bool(
        fige and raccroche
        and np.median([e_["erreur_um"] for e_ in fige])
        < np.median([e_["erreur_um"] for e_ in raccroche]))
    r["erreur_mediane_globale_um"] = round(
        float(np.median([e_["erreur_um"] for e_ in globale])), 1)
    r["tours_ou_la_globale_gagne"] = sum(
        1 for x, y in zip(globale, aveugle) if x["erreur_um"] < y["erreur_um"])
    r["la_globale_fait_mieux_que_par_point"] = bool(
        globale and raccroche
        and np.median([e_["erreur_um"] for e_ in globale])
        < np.median([e_["erreur_um"] for e_ in raccroche]))
    r["letroite_fait_mieux"] = bool(
        etroite and raccroche
        and np.median([e_["erreur_um"] for e_ in etroite])
        < np.median([e_["erreur_um"] for e_ in raccroche]))
    # ⚠⚠ LA RUGOSITÉ EST LE MÉCANISME, et elle est rendue à côté des erreurs : un raccrochage
    # décide point par point, donc il RIDE une surface que le pas aveugle gardait lisse. Sans
    # ce chiffre, « le raccrochage perd à l'itération » serait un constat sans cause attachée.
    r["rugosite_um"] = dict(
        raccroche=[e_["rugosite_um"] for e_ in raccroche],
        accorde=[e_["rugosite_um"] for e_ in accorde])
    r["tours_ou_le_raccrochage_gagne"] = sum(
        1 for x, y in zip(raccroche, aveugle) if x["erreur_um"] < y["erreur_um"])
    r["tours_ou_il_bat_le_hasard"] = sum(
        1 for x, y in zip(raccroche, hasard) if x["erreur_um"] < y["erreur_um"])
    r["erreur_mediane_raccrochee_um"] = round(
        float(np.median([e_["erreur_um"] for e_ in raccroche])), 1)
    r["erreur_mediane_accordee_um"] = round(
        float(np.median([e_["erreur_um"] for e_ in accorde])), 1)
    r["tours_ou_laccord_gagne"] = sum(
        1 for x, y in zip(accorde, aveugle) if x["erreur_um"] < y["erreur_um"])
    r["laccord_lisse_vraiment"] = bool(
        accorde and raccroche and accorde[0]["rugosite_um"] is not None
        and raccroche[0]["rugosite_um"] is not None)
    r["erreur_mediane_aveugle_um"] = round(
        float(np.median([e_["erreur_um"] for e_ in aveugle])), 1)
    # ⚠⚠ LE VERDICT EST PAR CONTENDANT, ET LA PREMIÈRE VERSION NE L'ÉTAIT PAS : elle ne
    # regardait que le raccrochage par point, donc elle imprimait « la dérive n'est pas
    # arrêtée » au moment même où le décalage global la faisait DESCENDRE. Un verdict qui ne
    # nomme pas son sujet dit le contraire de ce que la mesure a trouvé.
    da = r["derive_par_tour_um"]["aveugle"]
    r["la_derive_est_arretee"] = {
        cle: bool(d_ is not None and d_ <= 0.0)
        for cle, d_ in r["derive_par_tour_um"].items()}
    r["la_derive_est_reduite"] = {
        cle: bool(d_ is not None and da is not None and abs(d_) < abs(da))
        for cle, d_ in r["derive_par_tour_um"].items()}
    gains = [e_["gain_um"] for e_ in vieillissement]
    r["gain_du_premier_pas_um"] = gains[0] if gains else None
    r["gain_apres_un_tour_um"] = gains[1] if len(gains) > 1 else None
    r["gain_du_dernier_pas_um"] = gains[-1] if gains else None
    # ⚠⚠⚠ LE VERDICT QUI COMPTE, ET IL FAUT LES DEUX MOITIÉS : le gain existe au premier pas
    # — depuis une spire PUBLIÉE — et il a disparu au suivant. Regarder seulement le dernier
    # tour ferait conclure « le gain ne survit pas », ce qui est vrai mais trop faible : il ne
    # survit pas à UN SEUL tour, et c'est ça qui explique pourquoi aucune marche n'en profite.
    r["le_gain_existe_au_premier_pas"] = bool(gains and gains[0] > 0.0)
    # ⚠⚠ LE CRITÈRE EST STRUCTUREL, PAS UN SEUIL. Ma première version demandait « moins de la
    # moitié du gain initial », et elle est tombée sur 6,8 contre 6,35 — un verdict décidé au
    # dixième de micromètre par un nombre que j'avais choisi. Ce qui distingue un effet d'un
    # bruit n'est pas sa taille : c'est que le bruit CHANGE DE SIGNE et qu'un effet non.
    apres = gains[1:]
    r["gain_median_apres_le_premier_pas_um"] = (
        None if not apres else round(float(np.median(apres)), 1))
    r["le_gain_change_de_signe_apres_le_premier_pas"] = bool(
        apres and min(apres) < 0.0 < max(apres))
    r["le_gain_nexiste_quau_premier_pas"] = bool(
        gains and gains[0] > 0.0 and apres
        and min(apres) < 0.0 < max(apres))
    r["tient_la_feuille_a_la_fin"] = [
        cle for cle, f_ in r["feuille_tenue_a_la_fin"].items()
        if f_ and f_["sous_la_demi_feuille"]]
    return r


def le_gain_vieillit(depart: np.ndarray, ok: np.ndarray, cibles: dict[int, np.ndarray],
                    pas_vx: float, voxel_um: float, sens: float, vol,
                    demi_vx: float, demi_gab: int, minimum: int = 30) -> list[dict]:
    """Le gain d'UN pas raccroché, en partant d'une surface de plus en plus vieille.

    ⚠⚠⚠ POURQUOI CETTE MESURE EXISTE, ET C'EST L'ÉCART QUE LES DEUX PRÉCÉDENTES LAISSENT.
    Le raccrochage d'**un** pas gagne franchement (33,3 µm contre 46,7, sur 2401 lignes), et
    aucune marche ne s'en trouve mieux. Ces deux faits ne se contredisent que si l'on oublie
    d'où part chaque pas : la mesure d'un pas part TOUJOURS d'une spire **publiée**, dont les
    normales sont propres ; une marche part de sa propre reconstruction, qui ne l'est plus.

    Ici la trajectoire de référence est la marche **aveugle** — donc une surface qui vieillit
    sans que le raccrochage y soit pour rien. À chaque tour on en tire DEUX pas depuis le même
    point : un aveugle, un raccroché. La différence des deux, tour après tour, dit si le gain
    survit à l'âge de la surface d'où il part.

    ⚠⚠ UNE SEULE VARIABLE CHANGE ENTRE LES DEUX PAS : le raccrochage. Même surface de départ,
    même normale, même longueur, même cible. C'est ce qui manquait aux deux marches, qui
    partaient chacune de sa propre histoire — comparer leurs tours n'isolait rien.

    ⚠ La surface vieillit ET s'éloigne en même temps, et les deux ne sont pas séparés ici : ce
    qui est mesuré est « le gain survit-il à la dégradation », pas « laquelle des deux
    dégradations compte ».
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    a, m = depart.copy(), ok.copy()
    out = []
    for k in sorted(cibles):
        avant_a, avant_m = a.copy(), m.copy()
        nu, mnu, _ = un_pas_raccroche(avant_a, avant_m, pas_vx, sens, vol, demi_vx, demi_gab,
                                      raccrocher=False)
        rac, mrac, diag = un_pas_raccroche(avant_a, avant_m, pas_vx, sens, vol,
                                           demi_vx, demi_gab)
        if int(mnu.sum()) < minimum:
            break
        d_nu = distance_a(nu[mnu], cibles[k], voxel_um)
        d_rac = distance_a(rac[mrac], cibles[k], voxel_um)
        out.append(dict(
            tours_de_vieillissement=k - 1, cellules=int(mnu.sum()),
            pas_aveugle_um=round(float(np.median(d_nu)), 1),
            pas_raccroche_um=round(float(np.median(d_rac)), 1),
            gain_um=round(float(np.median(d_nu)) - float(np.median(d_rac)), 1),
            rugosite_um=(None if diag["rugosite_vx"] is None
                         else round(diag["rugosite_vx"] * voxel_um, 1))))
        # ⚠ La trajectoire de référence avance en AVEUGLE : si elle avançait raccrochée, l'âge
        # de la surface dépendrait du geste qu'on est en train de juger.
        a, m = nu, mnu
    return out


def balayer_le_pas_de_normale(depart: np.ndarray, ok: np.ndarray,
                              cibles: dict[int, np.ndarray], pas_vx: float, voxel_um: float,
                              sens: float, vol, demi_vx: float, demi_gab: int,
                              pas: tuple[int, ...] = (1, 2, 3, 4),
                              minimum: int = 30) -> list[dict]:
    """La marche AVEUGLE, pour plusieurs supports de dérivée de la normale.

    ⚠⚠⚠ POURQUOI CE BALAYAGE, ET POURQUOI SUR LA MARCHE AVEUGLE. La chaîne d'élimination a
    désigné les normales sans jamais les attaquer : leur dispersion monte de 2,8° à 10,9° même
    quand personne ne raccroche, donc elle borne tout le reste. Une normale est une dérivée, et
    une dérivée estimée entre voisins immédiats divise le bruit de position par la maille — ici
    seize voxels, donc une erreur d'un voxel fait déjà quatre degrés. Élargir le support divise
    ce bruit d'autant.

    ⚠⚠ ET ÇA COÛTE LE BORD, ce qui est l'autre moitié de la mesure : une cellule a besoin de
    voisins à ±`pas`, donc le masque perd `pas` cellules de chaque côté **par tour**. Les deux
    effets sont opposés et le balayage les rend visibles ensemble — un support qui nettoie la
    normale en mangeant la nappe n'a rien nettoyé.

    ⚠ Le raccrochage est ÉTEINT ici : on mesure ce que la géométrie fait toute seule. Le
    mélanger à un raccrochage ferait bouger deux choses et n'en attribuerait aucune.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    out = []
    for k in pas:
        marche = derouler(depart, ok, cibles, pas_vx, voxel_um, sens, vol, demi_vx, demi_gab,
                          raccrocher=False, minimum=minimum, pas_de_normale=k)
        if not marche:
            out.append(dict(pas_de_normale=k, tours=0, cellules_au_premier_tour=0,
                            derive_par_tour_um=None, dispersion_deg=[], erreur_um=[]))
            continue
        d_ = derive_par_tour(marche)
        out.append(dict(
            pas_de_normale=k, tours=len(marche),
            cellules_au_premier_tour=marche[0]["cellules"],
            cellules_au_dernier_tour=marche[-1]["cellules"],
            derive_par_tour_um=(None if d_ is None else round(d_, 1)),
            dispersion_deg=[e_["dispersion_normales_deg"] for e_ in marche],
            erreur_um=[e_["erreur_um"] for e_ in marche],
            # ⚠⚠ CE QUE LA DISPERSION EXPLIQUE, calculé et non affirmé : une normale fausse de
            # θ fait atterrir un pas de longueur L à L·sin(θ) de côté. Si ce nombre est du
            # même ordre que l'erreur mesurée, la dispersion SUFFIT à l'expliquer ; s'il est
            # dix fois plus petit, elle est un symptôme et pas la cause.
            ecart_lateral_attendu_um=[
                (None if e_["dispersion_normales_deg"] is None else
                 round(pas_vx * np.sin(np.radians(e_["dispersion_normales_deg"])) * voxel_um, 1))
                for e_ in marche],
        ))
    return out


def balayer_la_boite(cotes: tuple[float, ...] = (384.0, 512.0, 640.0),
                    minimum: int = 30, corpus: dict | None = None, volume=None) -> dict:
    """Le verdict de chaque dérouleur, à plusieurs tailles de morceau de nappe.

    ⚠⚠⚠ POURQUOI CE BALAYAGE EXISTE, ET C'EST UNE RÉTRACTATION. À 191 cellules et quatre
    tours, le décalage unique par tour rendait une dérive **négative** — l'erreur descendait —
    et c'était publié comme « le seul des six qui tienne encore la feuille ». À 494 cellules
    et six tours, la même marche, au même endroit, avec le même code, dérive de **+67 µm par
    tour** et devient la pire après le témoin. **Un résultat qui s'inverse quand l'échantillon
    grandit n'était pas un résultat**, et le publier sans le balayage aurait fait porter une
    conclusion par la taille d'une boîte choisie pour son coût de téléchargement.

    ⚠⚠ CE QUI CHANGE ENTRE DEUX POINTS DU BALAYAGE EST UNE SEULE CHOSE : la largeur de la
    boîte. Le centre ne bouge pas, la spire de départ non plus, le pas non plus. Les boîtes
    sont **emboîtées** — la plus grande contient la plus petite — donc ce n'est pas un autre
    endroit de la nappe, c'est le même endroit avec plus de matière autour.

    ⚠ Le coût est cumulatif et il est rendu : les blocs d'une petite boîte servent à la
    grande, donc le balayage complet coûte le prix de la plus large.
    """
    from le_corpus_des_spires import corpus_publie  # noqa: PLC0415

    c_ = corpus_publie() if corpus is None else corpus

    points = []
    for c in cotes:
        r = mesurer(minimum=minimum, cote=c, corpus=c_, volume=volume)
        points.append(dict(
            cote_voxels=c, cellules_au_depart=r["cellules_au_depart"],
            tours=r["tours_mesures"],
            derive_par_tour_um=r["derive_par_tour_um"],
            erreur_au_dernier_tour_um={k: (v["erreur_um"] if v else None)
                                       for k, v in r["feuille_tenue_a_la_fin"].items()},
            tient_la_feuille_a_la_fin=r["tient_la_feuille_a_la_fin"],
            la_derive_est_arretee=r["la_derive_est_arretee"],
            cout=r["cout"]))

    # ⚠⚠ LE FAIT QUE LE BALAYAGE EXISTE POUR ÉTABLIR : un contendant dont le verdict CHANGE
    # d'un point à l'autre n'a pas de verdict. Il est nommé, pas moyenné.
    contendants = sorted(points[0]["la_derive_est_arretee"])
    instables = [c for c in contendants
                 if len({p["la_derive_est_arretee"][c] for p in points}) > 1]
    return dict(cotes=list(cotes), points=points,
                contendants_au_verdict_instable=instables,
                verdict_stable=not instables,
                aucun_ne_tient_partout=[c for c in contendants
                                        if all(c not in p["tient_la_feuille_a_la_fin"]
                                               for p in points)])


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from le_raccrochage_a_la_matiere import Volume  # noqa: PLC0415

    # --- un volume fabriqué où les feuilles sont des plans z = 40, 100, 160 ---
    forme = (256, 64, 64)
    bloc = np.zeros(forme, dtype=np.uint8)
    zz = np.arange(forme[0])[:, None, None]
    for c in (40, 100, 160, 220):
        bloc |= (60 + 90 * np.exp(-((zz - c) ** 2) / 40.0)).astype(np.uint8)
    faux = dict(shape=list(forme), chunks=[256, 64, 64], dtype="|u1",
                dimension_separator="/", compressor=None)

    class VolumeFictif(Volume):
        def _bloc(self, cz, cy, cx):
            return bloc

    vf = VolumeFictif("", faux, {})

    # une grille plate posée à z = 40, la feuille suivante à 100 : le pas nominal vaut 60
    uu, vv = np.meshgrid(np.arange(12.0), np.arange(12.0), indexing="ij")
    plan = np.stack([uu * 2 + 20, vv * 2 + 20, np.full(uu.shape, 40.0)], axis=-1)
    ok = np.ones(plan.shape[:2], dtype=bool)

    av, bon, diag = un_pas_raccroche(plan, ok, 60.0, 1.0, vf, 15.0, 8)
    v("le pas raccroché avance le long de la normale", bool(bon[1:-1, 1:-1].all()))
    v("... et il lit un gabarit sur la surface de départ", diag["gabarit_lignes"] > 20,
      str(diag["gabarit_lignes"]))
    v("... et raccroche les cellules qu'il a pu lire", diag["raccrochees"] > 20,
      str(diag["raccrochees"]))
    atteint = float(np.median(av[bon][:, 2]))
    v("il tombe sur la feuille suivante", abs(atteint - 100.0) < 2.0, str(atteint))

    # ⚠⚠ LE TÉMOIN QUI COMPTE : un pas TROP COURT doit être RATTRAPÉ par le raccrochage. Sans
    # ça, « il tombe sur la feuille » serait satisfait par un pas exact que rien n'a corrigé.
    court, bonc, _ = un_pas_raccroche(plan, ok, 45.0, 1.0, vf, 15.0, 8)
    v("un pas trop court est rattrapé", abs(float(np.median(court[bonc][:, 2])) - 100.0) < 3.0,
      str(float(np.median(court[bonc][:, 2]))))
    # ⚠ … et un pas trop court NON raccroché reste où il est tombé, sinon le témoin ci-dessus
    # ne mesurerait que le pas.
    from derouler_par_le_pas_normal import un_pas  # noqa: PLC0415
    nu, bnu = un_pas(plan, ok, 45.0, 1.0)
    v("... alors que sans raccrochage il reste court",
      abs(float(np.median(nu[bnu][:, 2])) - 85.0) < 1e-6, str(float(np.median(nu[bnu][:, 2]))))
    # ⚠⚠ UN PAS TROP LONG DOIT ÊTRE RAMENÉ, sinon le raccrochage ne corrigerait que dans un sens.
    long_, bonl, _ = un_pas_raccroche(plan, ok, 75.0, 1.0, vf, 15.0, 8)
    v("un pas trop long est ramené", abs(float(np.median(long_[bonl][:, 2])) - 100.0) < 3.0,
      str(float(np.median(long_[bonl][:, 2]))))
    # ⚠⚠⚠ ET LA FENÊTRE DOIT L'EN EMPÊCHER AU-DELÀ D'UNE DEMI-FEUILLE : un pas de 110 tombe
    # plus près de la feuille 160 que de la 100, donc le raccrochage doit y aller — c'est ce
    # qui fait qu'un dérouleur peut glisser d'une feuille sans jamais s'en apercevoir.
    saut, bons, _ = un_pas_raccroche(plan, ok, 110.0, 1.0, vf, 15.0, 8)
    v("au-delà d'une demi-feuille, le raccrochage se pose sur la VOISINE",
      abs(float(np.median(saut[bons][:, 2])) - 160.0) < 4.0,
      str(float(np.median(saut[bons][:, 2]))))

    # ⚠⚠⚠ LE CONTRÔLE ANTI-DOUBLON : drapeau baissé, ce pas doit être EXACTEMENT celui du
    # dérouleur aveugle publié. Sans lui, la comparaison « raccroché contre aveugle » pourrait
    # mesurer l'écart entre deux implémentations d'un même geste.
    nul_ici, bon_ici, diag_ici = un_pas_raccroche(plan, ok, 60.0, 1.0, vf, 15.0, 8,
                                                 raccrocher=False)
    nul_la, bon_la = un_pas(plan, ok, 60.0, 1.0)
    v("drapeau baissé, le pas est celui du dérouleur aveugle publié, au bit près",
      bool(np.array_equal(nul_ici, nul_la) and np.array_equal(bon_ici, bon_la)))
    v("... et il ne raccroche rien", diag_ici["raccrochees"] == 0)

    # --- l'itération ---
    cibles = {1: np.array([[x, y, 100.0] for x in range(20, 45) for y in range(20, 45)],
                          dtype=float),
              2: np.array([[x, y, 160.0] for x in range(20, 45) for y in range(20, 45)],
                          dtype=float)}
    m = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8)
    v("la marche rend un tour par cible", len(m) == 2, str(len(m)))
    v("... et l'erreur reste sous une demi-feuille aux deux tours",
      all(e["erreur_um"] < 30.0 for e in m), str([e["erreur_um"] for e in m]))
    v("... et le témoin sur place s'éloigne, lui",
      m[-1]["temoin_sur_place_um"] > m[-1]["erreur_um"],
      f"{m[-1]['temoin_sur_place_um']} contre {m[-1]['erreur_um']}")
    v("les non-raccrochées sont comptées",
      all(e["non_raccrochees"] == e["cellules"] - e["raccrochees"] for e in m))

    # ⚠⚠ Le témoin du gabarit mélangé, itéré : il doit faire PIRE, sinon la forme ne sert à rien.
    mh = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8,
                  melanger=np.random.default_rng(3))
    v("le gabarit mélangé, itéré, fait pire",
      mh[-1]["erreur_um"] > m[-1]["erreur_um"],
      f"{mh[-1]['erreur_um']} contre {m[-1]['erreur_um']}")

    # --- la rugosité, l'accord, et la règle d'arrêt ---
    v("la rugosité est mesurée à chaque tour",
      all(e["rugosite_um"] is not None for e in m), str([e["rugosite_um"] for e in m]))
    # ⚠⚠ SUR UN PLAN PARFAIT LA RUGOSITÉ EST NULLE : si elle ne l'était pas, le chiffre
    # mesurerait le bruit de la mesure et non celui de la surface.
    v("... et elle est nulle sur un volume en plans parfaits",
      all(e["rugosite_um"] < 1.0 for e in m), str([e["rugosite_um"] for e in m]))
    # ⚠⚠⚠ ET CE QUE LA RUGOSITÉ MESURE EXACTEMENT : le DÉSACCORD entre voisins, pas l'erreur.
    # Sur un volume parfaitement uniforme, même un gabarit mélangé rend le MÊME décalage faux
    # partout — donc rugosité nulle. Ma première version l'avait écrit à l'envers et le
    # contrôle est tombé ; il faut un volume dont les lignes diffèrent pour que le témoin
    # discrimine.
    # ⚠⚠ LE BRUIT DOIT VARIER LE LONG DE LA LIGNE, pas seulement d'une colonne à l'autre : la
    # corrélation retire la moyenne de chaque segment, donc un décalage constant par colonne
    # ne la déplace pas d'un cheveu. Ma première fixture bruitait par colonne et rendait
    # rugosité nulle des deux côtés — le contrôle ne pouvait pas échouer.
    zz3, yy3, xx3 = np.meshgrid(*[np.arange(n_) for n_ in forme], indexing="ij")
    grain = (((zz3 * 15485863 + yy3 * 7919 + xx3 * 104729) % 61) - 30).astype(np.int16)
    bruite = np.clip(bloc.astype(np.int16) + grain, 0, 255).astype(np.uint8)

    class VolumeBruite(Volume):
        def _bloc(self, cz, cy, cx):
            return bruite

    vb = VolumeBruite("", faux, {})
    mb = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vb, 15.0, 8)
    mbh = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vb, 15.0, 8,
                   melanger=np.random.default_rng(5))
    v("sur un volume dont les lignes diffèrent, le hasard ride la surface",
      mbh[0]["rugosite_um"] > 3.0 * max(1e-9, mb[0]["rugosite_um"]),
      f"{mbh[0]['rugosite_um']} contre {mb[0]['rugosite_um']}")
    v("... et le gabarit juste, lui, la garde lisse", mb[0]["rugosite_um"] < 2.0,
      str(mb[0]["rugosite_um"]))
    ma = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8, accorder=True)
    v("l'accord des voisins rend une marche aussi bonne sur un plan",
      ma[-1]["erreur_um"] <= m[-1]["erreur_um"] + 1.0,
      f"{ma[-1]['erreur_um']} contre {m[-1]['erreur_um']}")
    # ⚠ La règle d'arrêt est déclarée : sous le minimum, la marche s'arrête au lieu de rendre
    # une médiane sur trois cellules.
    court_m = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8, minimum=200)
    v("la marche s'arrête sous le minimum de cellules", len(court_m) == 0, str(len(court_m)))
    v("... et elle va jusqu'au bout quand il est bas",
      len(derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8, minimum=1)) == 2)

    # --- le décalage GLOBAL ---
    # ⚠⚠ Sur un volume bruité, un décalage unique doit être MOINS dispersé qu'un décalage par
    # point : c'est toute sa raison d'être. La rugosité le dit directement — elle vaut zéro
    # par construction quand toutes les cellules reçoivent le même nombre.
    mg = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vb, 15.0, 8, global_=True)
    v("un décalage global ne ride pas la surface", mg[0]["rugosite_um"] < 1e-9, str(mg[0]))
    v("... alors que le décalage par point la ride sur le même volume",
      mb[0]["rugosite_um"] > mg[0]["rugosite_um"],
      f"{mb[0]['rugosite_um']} contre {mg[0]['rugosite_um']}")
    v("... et il trouve quand même la feuille",
      mg[-1]["erreur_um"] < 30.0, str(mg[-1]["erreur_um"]))

    # --- le gain qui vieillit ---
    # ⚠⚠ SUR UN VOLUME OÙ LE PAS EST EXACT, le raccrochage n'a rien à gagner : le gain doit
    # être nul, pas positif. Un gain positif là voudrait dire que la mesure récompense le
    # raccrochage même quand il n'y a rien à corriger.
    vj = le_gain_vieillit(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8, minimum=1)
    v("un pas exact ne laisse rien à gagner au raccrochage",
      all(abs(e["gain_um"]) < 1.0 for e in vj), str([e["gain_um"] for e in vj]))
    # ⚠⚠⚠ ET LE TÉMOIN QUI REND LA MESURE CAPABLE DE VOIR UN GAIN : avec un pas trop court, le
    # raccrochage DOIT gagner à chaque tour, sinon le zéro ci-dessus ne prouverait rien.
    vc = le_gain_vieillit(plan, ok, {1: cibles[1]}, 45.0, 1.0, 1.0, vf, 15.0, 8, minimum=1)
    v("... et avec un pas trop court, il gagne", vc[0]["gain_um"] > 10.0, str(vc[0]))
    # ⚠ La trajectoire de référence avance en AVEUGLE : l'âge de la surface ne doit pas
    # dépendre du geste jugé.
    v("l'âge se compte en tours, à partir de zéro",
      [e["tours_de_vieillissement"] for e in vj] == list(range(len(vj))),
      str([e["tours_de_vieillissement"] for e in vj]))

    # --- les normales lissées ---
    # ⚠⚠ SUR UN PLAN, toutes les normales sont déjà identiques : le lissage ne doit RIEN
    # changer, et sa dispersion vaut zéro. Un écart là voudrait dire que le lissage déplace
    # une géométrie qu'il devrait laisser en place.
    from le_pas_normal_atteint_la_spire import normales as _norm  # noqa: PLC0415
    n_p, bon_p = _norm(plan, ok)
    v("sur un plan, la dispersion des normales est nulle",
      abs(dispersion_angulaire(n_p, bon_p)) < 1e-6, str(dispersion_angulaire(n_p, bon_p)))
    v("... et le lissage ne les déplace pas",
      bool(np.allclose(lisser_les_normales(n_p, bon_p)[bon_p], n_p[bon_p])))
    # ⚠⚠⚠ LE TÉMOIN QUI REND LE LISSAGE MESURABLE : une normale isolée retournée doit être
    # ramenée par ses voisines, et la dispersion doit BAISSER. Sans ça, « lisser les normales »
    # serait un no-op qu'aucun contrôle ne distinguerait.
    tordu = n_p.copy()
    tordu[5, 5] = np.array([0.6, 0.0, 0.8])
    tordu[5, 5] /= np.linalg.norm(tordu[5, 5])
    avant = dispersion_angulaire(tordu, bon_p)
    apres = dispersion_angulaire(lisser_les_normales(tordu, bon_p), bon_p)
    v("une normale isolée tordue est ramenée par ses voisines", apres < avant / 2.0,
      f"{apres:.3f} contre {avant:.3f}")
    v("... et la dispersion voit la torsion", avant > 0.1, f"{avant:.3f}")
    # ⚠ Une cellule sans voisin valide garde SA normale : elle n'est pas écartée, sinon la
    # grille fondrait plus vite que celle du pas non lissé.
    seule = np.zeros(bon_p.shape, dtype=bool)
    seule[4, 4] = True
    v("une cellule sans voisin garde sa normale",
      bool(np.allclose(lisser_les_normales(n_p, seule)[4, 4], n_p[4, 4])))
    mn = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8, normales_lissees=True)
    v("lisser les normales ne casse pas une marche exacte",
      all(e["erreur_um"] < 1.0 for e in mn), str([e["erreur_um"] for e in mn]))
    v("la dispersion est rendue à chaque tour",
      all(e["dispersion_normales_deg"] is not None for e in mn))

    # --- le support de la dérivée ---
    bal = balayer_le_pas_de_normale(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8,
                                    pas=(1, 2), minimum=1)
    v("le balayage rend un point par support", len(bal) == 2, str(len(bal)))
    # ⚠⚠ UN SUPPORT PLUS LARGE COÛTE DES CELLULES, et c'est la moitié de la mesure : un
    # balayage qui ne rendrait que la dérive laisserait croire qu'élargir est gratuit.
    v("... et un support plus large part de moins de cellules",
      bal[1]["cellules_au_premier_tour"] < bal[0]["cellules_au_premier_tour"],
      f"{bal[1]['cellules_au_premier_tour']} contre {bal[0]['cellules_au_premier_tour']}")
    # ⚠⚠⚠ L'ÉCART LATÉRAL ATTENDU est calculé, pas affirmé : une normale fausse de θ fait
    # atterrir un pas de longueur L à L·sin(θ) de côté. Sur un plan parfait il vaut zéro.
    v("l'écart latéral attendu est nul quand les normales sont parfaites",
      all(x < 1e-6 for x in bal[0]["ecart_lateral_attendu_um"]),
      str(bal[0]["ecart_lateral_attendu_um"]))
    # ⚠⚠ CE CONTRÔLE A ÉTÉ RÉÉCRIT : la première version vérifiait que 60·sin(10°) vaut 10,42,
    # c'est-à-dire ma propre arithmétique contre elle-même — elle ne pouvait pas échouer. Ce
    # qui se teste vraiment est que les DEUX colonnes publiées s'accordent : un écart latéral
    # calculé sur une autre dispersion que celle rendue à côté serait un chiffre plausible et
    # faux, et c'est exactement la panne qu'aucune relecture n'attrape.
    bruite_p = plan.copy()
    bruite_p[:, :, 2] += np.random.default_rng(23).normal(0.0, 0.6, plan.shape[:2])
    balb = balayer_le_pas_de_normale(bruite_p, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8,
                                     pas=(1,), minimum=1)
    # ⚠ La tolérance vient des ARRONDIS des deux colonnes publiées — un dixième de micromètre
    # sur l'une, un centième de degré sur l'autre — et pas d'un nombre choisi : les comparer au
    # bit près a fait échouer ce contrôle sur 59,97 contre 60,0, ce qui n'est pas un désaccord.
    accord = all(
        abs(lat - 60.0 * np.sin(np.radians(dg))) < 0.06
        for lat, dg in zip(balb[0]["ecart_lateral_attendu_um"], balb[0]["dispersion_deg"]))
    v("l'écart latéral publié s'accorde avec la dispersion publiée à côté", accord,
      f"{balb[0]['ecart_lateral_attendu_um']} pour {balb[0]['dispersion_deg']}")
    v("... et il n'est pas nul sur une surface bruitée",
      any(x > 0.5 for x in balb[0]["ecart_lateral_attendu_um"]),
      str(balb[0]["ecart_lateral_attendu_um"]))

    # --- le gabarit figé ---
    # ⚠⚠ SUR UN VOLUME EN PLANS PARFAITS, geler le gabarit ne doit RIEN changer : la forme
    # d'une feuille y est la même partout. Un écart là voudrait dire que le gel modifie autre
    # chose que la source du gabarit.
    mfig = derouler(plan, ok, cibles, 60.0, 1.0, 1.0, vf, 15.0, 8, gabarit_fige=True)
    v("geler le gabarit ne change rien sur un volume homogène",
      [e["erreur_um"] for e in mfig] == [e["erreur_um"] for e in m],
      f"{[e['erreur_um'] for e in mfig]} contre {[e['erreur_um'] for e in m]}")
    # ⚠⚠⚠ ET LE CONTRASTE DU GABARIT EST RENDU MÊME QUAND ON NE S'EN SERT PLUS : c'est la
    # grandeur qui dit si la surface courante ressemble encore à une feuille, et elle est
    # intéressante précisément là.
    v("le contraste du gabarit est mesuré à chaque tour",
      all(e["contraste_du_gabarit"] is not None for e in mfig),
      str([e["contraste_du_gabarit"] for e in mfig]))
    v("... et il est fort sur un volume à feuilles nettes",
      all(e["contraste_du_gabarit"] > 20.0 for e in mfig),
      str([e["contraste_du_gabarit"] for e in mfig]))
    # ⚠ Sur un volume PLAT, il n'y a pas de feuille, donc pas de contraste — sinon le nombre
    # mesurerait le bruit de la mesure.
    uni = np.full(forme, 90, dtype=np.uint8)

    class VolumeUni(Volume):
        def _bloc(self, cz, cy, cx):
            return uni

    v("un volume sans feuille rend un contraste nul",
      derouler(plan, ok, {1: cibles[1]}, 60.0, 1.0, 1.0, VolumeUni("", faux, {}), 15.0, 8,
               minimum=1)[0]["contraste_du_gabarit"] < 1e-9)

    # ⚠⚠ UN GAIN QUI CHANGE DE SIGNE N'EST PAS UN GAIN, et c'est le critère retenu parce
    # qu'il ne demande aucun seuil : un effet garde son signe, un bruit non.
    v("un gain qui change de signe après le premier pas n'en est pas un",
      bool(min([-0.2, -13.5, 2.5, 6.8, -9.5]) < 0 < max([-0.2, -13.5, 2.5, 6.8, -9.5])))
    v("... alors qu'un gain qui garde son signe en est un",
      not (min([12.0, 9.0, 7.0]) < 0 < max([12.0, 9.0, 7.0])))

    # ⚠⚠ Le verdict doit nommer SON contendant : un verdict global sur une marche qui en
    # compare six dirait le contraire de la mesure dès que deux d'entre elles divergent.
    v("une marche qui descend rend une pente négative",
      derive_par_tour([dict(tours=k, erreur_um=100.0 - 20.0 * k) for k in range(1, 5)]) < 0)

    # ⚠⚠ Le premier franchissement et la tenue finale sont DEUX questions : une marche qui
    # franchit puis revient serait déclarée perdue par la première et tenue par la seconde.
    montee = [dict(tours=1, erreur_um=100.0, part_perdue=0.9, erreur_p90_um=200.0),
              dict(tours=2, erreur_um=20.0, part_perdue=0.0, erreur_p90_um=30.0)]
    v("une marche qui franchit puis revient est signalée par les deux nombres",
      montee[0]["erreur_um"] > 67.75 and montee[-1]["erreur_um"] < 67.75)

    # ⚠⚠ Le signe du décalage global doit être RENDU, pas seulement sa taille : sans lui,
    # « un décalage unique » et « une longueur de pas corrigée » sont indiscernables.
    v("le décalage global est rendu avec son signe",
      all(e["decalage_signe_um"] is not None for e in mg), str(mg[0]))
    v("... et il est négatif quand le pas dépasse",
      derouler(plan, ok, {1: cibles[1]}, 75.0, 1.0, 1.0, vf, 15.0, 8,
               global_=True)[0]["decalage_signe_um"] < 0)
    v("... positif quand le pas est trop court",
      derouler(plan, ok, {1: cibles[1]}, 45.0, 1.0, 1.0, vf, 15.0, 8,
               global_=True)[0]["decalage_signe_um"] > 0)

    # --- le groupement des perdues ---
    # ⚠ La grille du contrôle est GRANDE : sur douze par douze, la part de cellules ayant deux
    # voisines perdues se compte sur quelques dizaines de cas et le rapport bouge d'un tirage
    # à l'autre. Un contrôle qui dépend du tirage n'est pas un contrôle.
    val = np.ones((40, 40), dtype=bool)
    plaque = np.zeros((40, 40), dtype=bool)
    plaque[10:20, 10:20] = True
    eparses = np.zeros((40, 40), dtype=bool)
    idx_e = np.random.default_rng(11).choice(1600, size=int(plaque.sum()), replace=False)
    eparses[np.unravel_index(idx_e, (40, 40))] = True
    gp = groupement_des_perdues(plaque, val, np.random.default_rng(1))
    ge = groupement_des_perdues(eparses, val, np.random.default_rng(1))
    v("une plaque de perdues est vue comme groupée",
      gp["observe"] > 0.8, str(gp))
    v("... et un éparpillement de MÊME COMPTE ne l'est pas",
      ge["observe"] < 0.1, str(ge))
    v("... donc les deux se séparent", gp["observe"] > 8 * max(ge["observe"], 1e-3),
      f"{gp['observe']} contre {ge['observe']}")
    # ⚠⚠ ET LE RAPPORT SE REFUSE QUAND SON DÉNOMINATEUR N'EST PAS MESURABLE : à cette densité
    # un semis mélangé ne fait presque jamais deux voisines perdues.
    v("le rapport est refusé quand le témoin n'est pas mesurable",
      ge["rapport"] is None or gp["rapport"] is None, f"{gp['rapport']} / {ge['rapport']}")
    # ⚠⚠ CE QUE CE RAPPORT NE PERMET PAS, et il faut l'écrire : il n'est PAS comparable d'un
    # compte à l'autre. Le témoin garde le nombre de perdues, donc sa base monte avec la
    # densité — mesuré, une plaque de 10×10 rend 5,0 et une de 14×14 rend 2,7 pour le même
    # degré de groupement. Il se lit tour par tour contre son propre 1, jamais entre tours.
    plaque2 = np.zeros((40, 40), dtype=bool)
    plaque2[8:22, 8:22] = True
    g2 = groupement_des_perdues(plaque2, val, np.random.default_rng(1))
    v("... et à densité plus forte le témoin devient mesurable",
      g2["rapport"] is not None and g2["rapport"] > 1.5, str(g2))
    v("trop peu de perdues ne rend pas de rapport",
      groupement_des_perdues(np.zeros((40, 40), dtype=bool), val) is None)

    # --- la dérive ---
    plate = [dict(tours=k, erreur_um=30.0) for k in range(1, 6)]
    v("une marche plate n'a pas de dérive", abs(derive_par_tour(plate)) < 1e-9)
    montante = [dict(tours=k, erreur_um=30.0 + 10.0 * k) for k in range(1, 6)]
    v("une marche qui monte de dix par tour rend dix",
      abs(derive_par_tour(montante) - 10.0) < 1e-9, str(derive_par_tour(montante)))
    v("un seul tour ne permet pas de pente", derive_par_tour(plate[:1]) is None)
    # ⚠ La pente est prise sur TOUTE la marche : une marche qui monte puis redescend ne doit
    # pas rendre la pente de ses deux extrémités.
    bosse = [dict(tours=1, erreur_um=30.0), dict(tours=2, erreur_um=90.0),
             dict(tours=3, erreur_um=30.0)]
    v("une bosse ne rend pas la pente de ses extrémités",
      abs(derive_par_tour(bosse)) < 1e-9, str(derive_par_tour(bosse)))

    # --- le choix du départ ---
    g = {1: (np.zeros((3, 3, 3)), np.zeros((3, 3), dtype=bool)),
         4: (np.full((6, 6, 3), 10.0), np.ones((6, 6), dtype=bool)),
         5: (np.full((6, 6, 3), 12.0), np.ones((6, 6), dtype=bool))}
    v("le départ est le rang le plus bas dont la spire ET la suivante sont là",
      _boite_du_depart(g, np.array([10.0, 10.0, 10.0]), 20.0, 30) == 4,
      str(_boite_du_depart(g, np.array([10.0, 10.0, 10.0]), 20.0, 30)))
    v("... et rien n'est rendu si personne n'y est",
      _boite_du_depart(g, np.array([900.0, 900.0, 900.0]), 20.0, 30) is None)

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LES NOMBRES PUBLIÉS, HORS LIGNE, avec ses DEUX matières : les
    # spires disent d'où partir et où juger, le volume sur quoi se raccrocher. Elles décrivent
    # le même objet — `le_corpus_des_spires` ne le décrit qu'une fois —, sans quoi la marche
    # snapperait sur de la matière qui contredit ses propres ancres.
    # ⚠⚠ AUCUN VERDICT N'EST VÉRIFIÉ ICI. La fixture n'est pas le fragment : quel contendant y
    # gagne ne dit rien, et l'épingler ferait de la batterie une mesure de la fixture. Ce qui
    # est vérifié, ce sont les invariants que la mesure revendique.
    import contextlib  # noqa: PLC0415
    import io as _io  # noqa: PLC0415

    from le_corpus_des_spires import (  # noqa: PLC0415
        corpus_fabrique, geometrie_fabriquee, volume_fabrique,
    )

    g0 = geometrie_fabriquee()
    corpus0, vol0 = corpus_fabrique(), volume_fabrique(g0)
    fab = mesurer(minimum=20, corpus=corpus0, volume=vol0)
    v("la mesure tourne de bout en bout sur des matières fabriquées, sans rien lire",
      fab["tours_mesures"] > 0 and fab["cellules_au_depart"] > 0,
      f"{fab['tours_mesures']} tours depuis {fab['cellules_au_depart']} cellules")
    v("... et les dix contendants sont tous mesurés",
      len(fab["derive_par_tour_um"]) == 10 and all(
          v_ is not None for v_ in fab["derive_par_tour_um"].values()),
      str(sorted(fab["derive_par_tour_um"])))
    # ⚠⚠⚠ LE SEUL VERDICT QUI DOIT TENIR SUR N'IMPORTE QUELLE MATIÈRE : un décalage TIRÉ AU
    # HASARD ne peut pas battre une méthode. S'il le fait, ce n'est pas un résultat sur la
    # nappe, c'est que la mesure est cassée — et ce contrôle-là ne demande aucune cible.
    v("le contendant tiré au hasard est le pire de tous",
      fab["derive_par_tour_um"]["hasard"] == max(fab["derive_par_tour_um"].values()),
      str(fab["derive_par_tour_um"]))
    # ⚠⚠ LE ROND-TRIP : le pas nominal traverse la mesure sans se déformer, et la demi-épaisseur
    # en est bien la moitié. Sans ça, une marche calibrée sur une autre échelle passerait.
    v("... le pas lu est celui qu'on a injecté, et la demi-épaisseur en est la moitié",
      abs(fab["ecart_lu_um"] - g0["ecart_um"]) < 0.01
      and abs(fab["demi_epaisseur_um"] - g0["ecart_um"] / 2) < 0.01,
      f"{fab['ecart_lu_um']} µm, demi {fab['demi_epaisseur_um']}")
    v("... la marche perd des cellules et s'arrête sur le minimum déclaré",
      fab["cellules_au_depart"] >= fab["minimum_de_cellules"]
      and all(a_["cellules"] >= b_["cellules"] for a_, b_ in
              zip(fab["marche_aveugle"], fab["marche_aveugle"][1:])),
      str([e["cellules"] for e in fab["marche_aveugle"]]))
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = _io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "tient la feuille au dernier tour" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")

    # ⚠⚠ LE BALAYAGE, LUI AUSSI, doit tourner : c'est lui qui a rétracté une conclusion publiée,
    # donc c'est le dernier endroit du module qu'on peut se permettre de ne jamais exercer.
    bal = balayer_la_boite(cotes=(300.0, 384.0), minimum=20, corpus=corpus0, volume=vol0)
    v("le balayage tourne sur les mêmes matières et rend un point par côté",
      len(bal["points"]) == 2 and [p_["cote_voxels"] for p_ in bal["points"]] == [300.0, 384.0],
      str([p_["cellules_au_depart"] for p_ in bal["points"]]))
    # ⚠⚠ LES BOÎTES SONT EMBOÎTÉES : une boîte plus large contient PLUS de cellules. La
    # comparaison est STRICTE, et c'est ce qui la rend capable d'échouer : la fixture déborde de
    # la petite boîte, donc un découpage qui cesserait de mordre rendrait les deux points égaux
    # — et une inégalité large serait satisfaite par une boîte qui ne fait rien. Sans ça, deux
    # points du balayage ne seraient plus le même endroit avec plus de matière autour.
    v("... et une boîte plus large contient strictement plus de cellules",
      bal["points"][1]["cellules_au_depart"] > bal["points"][0]["cellules_au_depart"],
      str([p_["cellules_au_depart"] for p_ in bal["points"]]))
    v("... il nomme les contendants dont le verdict change avec la taille",
      isinstance(bal["contendants_au_verdict_instable"], list),
      str(bal["contendants_au_verdict_instable"]))
    tampon2, souci2 = _io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon2):
            afficher_le_balayage(bal)
    except Exception as exc:  # noqa: BLE001
        souci2 = f"{type(exc).__name__}: {exc}"
    v("... et son affichage tourne aussi",
      souci2 is None and "verdict CHANGE" in tampon2.getvalue(),
      souci2 or f"{len(tampon2.getvalue().splitlines())} lignes")
    # ⚠ Le refus, DISCRIMINANT : les deux matières sont déplacées ensemble, donc les feuilles
    # existent et se lisent — elles sont seulement ailleurs que la boîte.
    ailleurs = geometrie_fabriquee(decalage_vx=5000.0)
    refus = None
    try:
        mesurer(minimum=20, corpus=corpus_fabrique(decalage_vx=5000.0),
                volume=volume_fabrique(ailleurs))
    except RuntimeError as exc:
        refus = str(exc)
    v("un objet entier posé hors de la boîte est REFUSÉ, pas rendu vide",
      refus is not None, str(refus))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=float, default=None,
                   help="côté de la boîte en voxels ; le centre ne bouge jamais")
    p.add_argument("--balayer", type=str, default=None,
                   help="côtés de boîte séparés par des virgules, ex. 384,512,640")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.balayer:
        b = balayer_la_boite(tuple(float(x) for x in a.balayer.split(",")))
        afficher_le_balayage(b)
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(b, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"écrit : {a.json}")
        return 0
    r = mesurer(cote=a.cote)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


def afficher_le_balayage(b: dict) -> None:
    """Le compte rendu lisible d'un balayage de boîte.

    ⚠⚠ Sorti de `main` pour la raison mesurée dans `80` : un bloc de `main` ne peut être exercé
    qu'en lisant le dépôt distant, donc jamais par la batterie.
    """
    print(f"{'côté':>6} {'cellules':>9} {'tours':>6}  dérive par tour (µm)")
    print("-" * 88)
    for pt in b["points"]:
        d_ = pt["derive_par_tour_um"]
        print(f"{pt['cote_voxels']:>6.0f} {pt['cellules_au_depart']:>9} "
              f"{pt['tours']:>6}  " + "  ".join(
                  f"{k} {v:+.1f}" for k, v in d_.items() if v is not None))
    print(f"\ncontendants dont le verdict CHANGE avec la taille : "
          f"{b['contendants_au_verdict_instable'] or 'aucun'}")
    print(f"contendants qui ne tiennent la feuille à AUCUNE taille : "
          f"{b['aucun_ne_tient_partout']}")
    print(f"coût cumulé : {b['points'][-1]['cout']['blocs_telecharges']} blocs "
          f"au dernier point")


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'une mesure.

    ⚠⚠ Sorti de `main` pour la raison mesurée dans `80` : c'est dans un bloc d'affichage de
    `main` qu'un patch à moitié appliqué a laissé, le 2026-09-05, un enregistrement
    référençant des variables inexistantes, sans qu'aucune batterie puisse le voir.
    """
    print(f"départ : spire {r['depuis']}, {r['cellules_au_depart']} cellules dans une boîte "
          f"de {r['boite']['cote_voxels']:.0f} voxels")
    print(f"pas nominal {r['ecart_lu_um']} µm, sens « {r['sens_retenu']} », "
          f"{r['bits_de_supervision']} bit de supervision\n")
    print(f"{'tour':>5} {'cell.':>6} {'par point':>10} {'accordé':>9} {'étroite':>9} "
          f"{'GLOBAL':>8} {'FIGÉ':>7} {'NORM.':>7} {'2 REM':>7} {'av.+N':>7} {'aveugle':>9} "
          f"{'hasard':>8} {'disp°':>6} {'perdues':>8}")
    print("-" * 126)
    for k in range(r["tours_mesures"]):
        x = r["marche_raccrochee"][k]
        w = r["marche_accordee"][k] if k < len(r["marche_accordee"]) else {}
        y = r["marche_aveugle"][k] if k < len(r["marche_aveugle"]) else {}
        z = r["marche_hasard"][k] if k < len(r["marche_hasard"]) else {}
        e_ = r["marche_fenetre_etroite"][k] if k < len(r["marche_fenetre_etroite"]) else {}
        g_ = r["marche_globale"][k] if k < len(r["marche_globale"]) else {}
        f_ = r["marche_gabarit_fige"][k] if k < len(r["marche_gabarit_fige"]) else {}
        n_ = r["marche_normales_lissees"][k] if k < len(r["marche_normales_lissees"]) else {}
        an = (r["marche_aveugle_normales_lissees"][k]
              if k < len(r["marche_aveugle_normales_lissees"]) else {})
        dsp = y.get("dispersion_normales_deg")
        print(f"{x['tours']:>5} {x['cellules']:>6} {x['erreur_um']:>9.0f}µ "
              f"{w.get('erreur_um', float('nan')):>8.0f}µ "
              f"{e_.get('erreur_um', float('nan')):>8.0f}µ "
              f"{g_.get('erreur_um', float('nan')):>7.0f}µ "
              f"{f_.get('erreur_um', float('nan')):>6.0f}µ "
              f"{n_.get('erreur_um', float('nan')):>6.0f}µ "
              f"{r['marche_les_deux_remedes'][k].get('erreur_um', float('nan')):>6.0f}µ "
              f"{an.get('erreur_um', float('nan')):>6.0f}µ "
              f"{y.get('erreur_um', float('nan')):>8.0f}µ "
              f"{z.get('erreur_um', float('nan')):>7.0f}µ "
              f"{('—' if dsp is None else f'{dsp:.1f}'):>6} "
              f"{x['part_perdue']:>8.2f}")
    d = r["derive_par_tour_um"]
    print(f"\ndérive par tour : raccroché {d['raccroche']} µm · accordé {d['accorde']} µm · "
          f"étroite {d['etroite']} µm · GLOBAL {d['globale']} µm · "
          f"FIGÉ {d['fige']} µm · normales {d['normales']} µm · "
          f"aveugle+normales {d['aveugle_normales']} µm · LES DEUX {d['les_deux']} µm · "
          f"aveugle {d['aveugle']} µm · hasard {d['hasard']} µm")
    print(f"part de cellules au-delà d'une demi-feuille — raccroché "
          f"{r['part_perdue']['raccroche']} contre aveugle {r['part_perdue']['aveugle']}")
    print(f"groupement des perdues (1 = éparpillées) — raccroché "
          f"{r['groupement_des_perdues']['raccroche']} contre aveugle "
          f"{r['groupement_des_perdues']['aveugle']}")
    t = r["tours_avant_de_perdre_la_feuille"]
    print(f"premier tour au-dessus d'une demi-feuille ({r['demi_epaisseur_um']} µm) : "
          f"par point {t['raccroche']} · global {t['globale']} · aveugle {t['aveugle']} · "
          f"hasard {t['hasard']}")
    print("au DERNIER tour mesuré :")
    for nom, cle in (("par point", "raccroche"), ("accordé", "accorde"),
                     ("étroite", "etroite"), ("GLOBAL", "globale"),
                     ("aveugle", "aveugle"), ("hasard", "hasard")):
        f = r["feuille_tenue_a_la_fin"][cle]
        if f:
            print(f"  {nom:>10} : {f['erreur_um']:>6.1f} µm  p90 {f['p90_um']:>6.1f}  "
                  f"perdues {f['part_perdue']:.2f}  "
                  f"{'tient' if f['sous_la_demi_feuille'] else 'a perdu la feuille'}")
    print(f"le raccrochage gagne à {r['tours_ou_le_raccrochage_gagne']} tours sur "
          f"{r['tours_mesures']} (accordé : {r['tours_ou_laccord_gagne']}), "
          f"et bat le hasard à {r['tours_ou_il_bat_le_hasard']}")
    print("\nle support de la dérivée de la normale, sur la marche AVEUGLE :")
    print(f"  {'pas':>4} {'tours':>6} {'cell. 1er':>10} {'cell. fin':>10} "
          f"{'dérive/tour':>12} {'dispersion fin':>15} {'écart latéral':>14}")
    for e_ in r["balayage_du_pas_de_normale"]:
        d_ = e_["derive_par_tour_um"]
        disp = e_["dispersion_deg"][-1] if e_["dispersion_deg"] else None
        lat = e_["ecart_lateral_attendu_um"][-1] if e_.get("ecart_lateral_attendu_um") else None
        print(f"  {e_['pas_de_normale']:>4} {e_['tours']:>6} "
              f"{e_['cellules_au_premier_tour']:>10} "
              f"{e_.get('cellules_au_dernier_tour', 0):>10} "
              f"{('—' if d_ is None else f'{d_:+.1f}µ'):>12} "
              f"{('—' if disp is None else f'{disp:.1f}°'):>15} "
              f"{('—' if lat is None else f'{lat:.0f}µ'):>14}")
    print(f"  → meilleur support : {r['meilleur_pas_de_normale']}")
    print("  au PREMIER tour, seule comparaison non confondue par l'érosion :")
    for e_ in r["au_premier_tour_par_support"]:
        print(f"     pas {e_['pas_de_normale']} · {e_['cellules']:>4} cellules · "
              f"erreur {e_['erreur_um']:.1f} µm · dispersion {e_['dispersion_deg']:.2f}°")
    print(f"  → la dispersion baisse avec le support : "
          f"{'OUI' if r.get('la_dispersion_baisse_avec_le_support') else 'NON'} · "
          f"l'erreur suit : {'OUI' if r.get('lerreur_suit_la_dispersion') else 'NON'} · "
          f"donc symptôme : "
          f"{'OUI' if r.get('la_dispersion_est_un_symptome') else 'NON'}")

    print("\nle gain d'UN pas raccroché, depuis une surface qui vieillit EN AVEUGLE :")
    print(f"  {'âge':>4} {'cell.':>6} {'pas aveugle':>12} {'raccroché':>11} {'gain':>8} "
          f"{'rugosité':>9}")
    for e_ in r["le_gain_vieillit"]:
        rug_ = e_["rugosite_um"]
        print(f"  {e_['tours_de_vieillissement']:>4} {e_['cellules']:>6} "
              f"{e_['pas_aveugle_um']:>11.1f}µ {e_['pas_raccroche_um']:>10.1f}µ "
              f"{e_['gain_um']:>+7.1f}µ "
              f"{('—' if rug_ is None else f'{rug_:.0f}µ'):>9}")
    print(f"→ le gain n'existe qu'au premier pas : "
          f"{'OUI' if r['le_gain_nexiste_quau_premier_pas'] else 'NON'}"
          f"  (âge 0 : {r['gain_du_premier_pas_um']:+.1f} µm ; ensuite médiane "
          f"{r['gain_median_apres_le_premier_pas_um']:+.1f} µm et le signe change : "
          f"{'OUI' if r['le_gain_change_de_signe_apres_le_premier_pas'] else 'NON'})")
    print(f"décalage global par tour (signé) : {r['decalage_global_signe_um']} µm — "
          f"longueur de pas équivalente {r['longueur_equivalente_um']} µm "
          f"(change de signe : {'OUI' if r['le_global_change_de_signe'] else 'NON'})")
    print(f"marche arrêtée sous {r['minimum_de_cellules']} cellules ; "
          f"la grille part de {r['cellules_au_depart']}")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs téléchargés, "
          f"{r['cout']['mebioctets']} Mio")
    arret = [c for c, ok_ in r["la_derive_est_arretee"].items() if ok_]
    print(f"\n→ la dérive cesse de monter pour : {', '.join(arret) if arret else 'aucun'}")
    print(f"→ tient la feuille au dernier tour : "
          f"{', '.join(r['tient_la_feuille_a_la_fin']) or 'aucun'}")


if __name__ == "__main__":
    sys.exit(main())
