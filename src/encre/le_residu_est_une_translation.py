#!/usr/bin/env python3
"""Le résidu entre les deux aplatissements est-il un CHAMP, ou une TRANSLATION ? — tranché sur l'encre.

⚠⚠ POURQUOI CE FICHIER EXISTE. Tout le lot C1 suppose que le désaccord entre les deux
aplatissements est un **champ** : `75` a mesuré un champ de bord sur 34 carreaux, refusé un
modèle lisse, refusé l'agrégation locale, puis trouvé 55 repères intérieurs appariés. Chaque
étape a été jugée sur **une seule fenêtre** — celle que `le_regime_du_prix` avait retenue parce
qu'elle est la plus encrée — où le champ de bord fait passer l'AUC de la carte publiée de 0,418
à 0,612.

⭐⭐⭐ **Une fenêtre n'est pas une mesure.** Ce fichier rejoue exactement la même validation sur
**toute l'empreinte**, fenêtre par fenêtre, et compare quatre prétendants sur les mêmes
fenêtres : le champ nul, le champ de bord, le champ des repères, et — le contrôle que personne
n'avait posé — la **constante** de chacun, c'est-à-dire son déplacement médian appliqué partout.

⚠⚠ Si une constante fait aussi bien qu'un champ, il n'y a pas de champ : il y a un **biais de
recalage**, et le champ n'était que ce biais plus du bruit. C'est le motif que ce dépôt connaît
déjà (`77` : un biais est CONSTANT, donc il s'annule dans les différences) pris dans l'autre
sens — ici le biais ne s'annule pas, il se retranche.

⚠ Trois contrôles obligatoires, chacun capable de faire tomber le résultat :
  - la **carte mélangée** : l'encre n'est plus à sa place, donc aucun décalage ne doit gagner.
    Une surface qui garderait un maximum mesurerait l'empreinte et non l'encre ;
  - le **maximum au bord** : `75` a déjà publié un optimum à (−104, −120) qui touchait la borne
    du balayage, donc ne désignait rien. La position du maximum dans la grille est rendue ;
  - les **positions mélangées** du champ des repères : mêmes déplacements, positions permutées.
    Un champ qui ne battrait pas ce témoin ne porterait aucune structure spatiale.

Usage :
    uv run python src/encre/le_residu_est_une_translation.py --verifier
    uv run python src/encre/le_residu_est_une_translation.py \\
        --json docs/mesures/le_residu_est_une_translation.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

RECALAGE = RACINE / "docs" / "mesures" / "le_recalage_des_etiquettes.json"
REPERES = RACINE / "docs" / "mesures" / "les_reperes_apparies.json"

CELLULE_UM = 2.215 * 8.0
"""La cellule de la carte publiée réduite, en micromètres.

⚠ Lue dans le nom du fichier publié — `2.215um` … `ds8` — et non choisie : une réduction ×8
d'une carte à 2,215 µm fait des cases de 17,72 µm. C'est ce qui permet de dire si un décalage de
vingt cases est une broutille ou la moitié d'une lettre (~600 µm, `48`)."""


def deplacements_des_reperes(paires: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Les positions (dans le repère de la carte publiée) et le déplacement de chaque repère.

    ⚠⚠⚠ LA CONVENTION DE SIGNE EST DÉRIVÉE, PAS CHOISIE, et se trompe silencieusement. Dans
    `champ_local`, un carreau de l'empreinte **publiée** pris en `(i, j)` est comparé au masque
    transporté pris en `(i + di, j + dj)` : le décalage indexe donc le masque, à partir d'une
    position de la carte. Un repère est le même énoncé sur un point : le trou vu en `cible` dans
    la carte est vu en `source` dans le masque transporté, donc `d = source − cible`, et la
    position à laquelle ce déplacement s'applique est **la cible**.

    ⚠ Prendre `cible − source` inverserait le champ. C'est mesurable et c'est mesuré
    (`--verifier`), parce qu'un champ inversé ne ressemble pas à une panne : il dégrade
    doucement, comme un champ juste appliqué à un objet bruité.
    """
    src = np.array([p["source"] for p in paires], dtype=float)
    cib = np.array([p["cible"] for p in paires], dtype=float)
    if src.size == 0:
        return np.zeros((0, 2)), np.zeros((0, 2))
    return cib, src - cib


def deplacements_des_carreaux(champ: dict) -> tuple[np.ndarray, np.ndarray]:
    """Les mêmes deux tableaux pour le champ de bord — position au CENTRE du carreau.

    ⚠ Au centre et non au coin : un carreau porte un décalage valable pour sa surface, et
    l'indexer par son coin le décalerait d'un demi-pas vers le haut à gauche, soit 64 cases.
    """
    car = champ.get("carreaux", [])
    pas = int(champ.get("pas", 0))
    if not car:
        return np.zeros((0, 2)), np.zeros((0, 2))
    pos = np.array([[c["i"] + pas / 2.0, c["j"] + pas / 2.0] for c in car], dtype=float)
    dep = np.array([[float(c["di"]), float(c["dj"])] for c in car], dtype=float)
    return pos, dep


def predire(positions: np.ndarray, deplacements: np.ndarray, i: float, j: float,
            rayon: float, omettre: int | None = None) -> tuple[float, float] | None:
    """Le déplacement prédit en un point, par distance inverse — ou `None` hors de portée.

    ⚠⚠ Le refus hors de portée est la moitié utile de cette fonction. Les repères sont
    **groupés d'un côté** du fragment (`75`), donc un champ qui répondrait partout
    extrapolerait, et un champ jugé là où rien ne le contraint mesure l'extrapolation, pas le
    champ.

    ⚠ Le poids est `1/(d+1)` et non `1/d` : à distance nulle le second diverge, ce qui rend la
    prédiction en un point de mesure dépendante de l'ordre du tableau.
    """
    if positions.size == 0:
        return None
    d = np.hypot(positions[:, 0] - i, positions[:, 1] - j)
    garde = d <= rayon
    if omettre is not None:
        garde = garde.copy()
        garde[omettre] = False
    if not garde.any():
        return None
    w = 1.0 / (d[garde] + 1.0)
    return (float((deplacements[garde, 0] * w).sum() / w.sum()),
            float((deplacements[garde, 1] * w).sum() / w.sum()))


def laisser_un_dehors(positions: np.ndarray, deplacements: np.ndarray, rayon: float,
                      tirages: int = 20, graine: int = 7) -> dict:
    """L'erreur de prédiction d'un point omis, contre le champ NUL et contre les positions mélangées.

    ⚠⚠ DEUX TÉMOINS, PARCE QU'ILS ÉCHOUENT DIFFÉREMMENT. Le champ nul dit si prédire vaut mieux
    que ne rien prédire ; les positions mélangées disent si c'est la **structure spatiale** qui
    prédit, ou seulement la distribution des déplacements. Un champ qui bat le premier sans
    battre le second est une constante déguisée.

    ⚠ Les trois erreurs sont calculées sur les **mêmes** points — ceux que le voisinage sait
    prédire — sinon on comparerait deux populations.
    """
    n = len(positions)
    err, nul = [], []
    for k in range(n):
        p = predire(positions, deplacements, positions[k, 0], positions[k, 1], rayon, omettre=k)
        if p is None:
            continue
        err.append(float(np.hypot(deplacements[k, 0] - p[0], deplacements[k, 1] - p[1])))
        nul.append(float(np.hypot(deplacements[k, 0], deplacements[k, 1])))
    rng = np.random.default_rng(graine)
    melanges = []
    for _ in range(tirages):
        pm = positions[rng.permutation(n)]
        e = []
        for k in range(n):
            p = predire(pm, deplacements, pm[k, 0], pm[k, 1], rayon, omettre=k)
            if p is None:
                continue
            e.append(float(np.hypot(deplacements[k, 0] - p[0], deplacements[k, 1] - p[1])))
        if e:
            melanges.append(float(np.median(e)))
    return dict(rayon=float(rayon), predits=len(err),
                erreur_mediane=float(np.median(err)) if err else None,
                erreur_du_champ_nul=float(np.median(nul)) if nul else None,
                temoin_positions_melangees_mediane=(float(np.median(melanges))
                                                    if melanges else None),
                temoin_positions_melangees_meilleur=(float(min(melanges))
                                                     if melanges else None),
                bat_le_champ_nul=bool(err and np.median(err) < np.median(nul)),
                bat_les_positions_melangees=bool(err and melanges
                                                 and np.median(err) < min(melanges)))


def fenetres(carte: np.ndarray, etiquettes: np.ndarray, cote: int, pas: int,
             minimum: int = 1000) -> list[tuple[int, int]]:
    """Les fenêtres où l'AUC a de quoi être calculée : assez d'encre ET assez de fond.

    ⚠ Les deux comptes, pas seulement l'encre : une fenêtre entièrement encrée n'a aucun négatif
    et son AUC n'est pas définie. Le minimum est appliqué aux deux populations.
    """
    dedans = np.isfinite(carte) & (carte > 0)
    out = []
    for i in range(0, carte.shape[0] - cote + 1, pas):
        for j in range(0, carte.shape[1] - cote + 1, pas):
            ok = dedans[i:i + cote, j:j + cote]
            reg = etiquettes[i:i + cote, j:j + cote]
            if (ok & (reg > 0.5)).sum() >= minimum and (ok & (reg <= 0.5)).sum() >= minimum:
                out.append((i, j))
    return out


def fenetres_deplacables(liste: list[tuple[int, int]], forme: tuple[int, int],
                         cote: int, portee: int) -> list[tuple[int, int]]:
    """Les fenêtres qui savent répondre pour TOUS les décalages du balayage.

    ⚠⚠⚠ SANS CE FILTRE, UNE SURFACE D'AUC COMPARE DES POPULATIONS DIFFÉRENTES. `aire` refuse un
    décalage qui sortirait du tableau, donc une fenêtre collée au bord haut répond à `+20` et
    pas à `−20` : la médiane prise à chaque point de grille porterait alors sur un jeu de
    fenêtres qui change avec le décalage, et le maximum irait là où les fenêtres restantes sont
    les plus faciles. C'est le même piège que `comparer` évite en n'acceptant que les fenêtres
    où tout le monde répond — ici il faut l'appliquer à la grille entière.
    """
    h, w = forme
    return [(i, j) for (i, j) in liste
            if i - portee >= 0 and j - portee >= 0
            and i + portee + cote <= h and j + portee + cote <= w]


def aire(carte: np.ndarray, etiquettes: np.ndarray, fenetre: tuple[int, int], cote: int,
         di: float, dj: float, minimum: int = 1000) -> float | None:
    """L'AUC de la carte publiée sur une fenêtre, les étiquettes décalées de `(di, dj)`."""
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415

    i, j = fenetre
    di, dj = int(round(di)), int(round(dj))
    if i + di < 0 or j + dj < 0:
        return None
    reg = etiquettes[i + di:i + di + cote, j + dj:j + dj + cote]
    ref = carte[i:i + cote, j:j + cote]
    if reg.shape != ref.shape:
        return None
    ok = np.isfinite(ref) & (ref > 0)
    a = ref[ok & (reg > 0.5)].ravel()
    b = ref[ok & (reg <= 0.5)].ravel()
    return aire_sous_la_courbe(a, b) if a.size >= minimum and b.size >= minimum else None


def accord_des_silhouettes(masque_recale: np.ndarray, support: np.ndarray,
                           portee: int, pas: int) -> dict:
    """Le même plan de décalages, jugé sur les SILHOUETTES au lieu de l'encre.

    ⚠⚠⚠ POURQUOI CE PLAN EXISTE, ET IL DÉCIDE DE LA CAUSE. Un décalage qui remonte l'accord de
    l'**encre** peut venir de deux endroits, et les deux demandent des remèdes opposés :
      - les deux **silhouettes** sont mal recalées, et l'encre en hérite. Le remède est le
        recalage, et le même décalage doit alors remonter le Dice des silhouettes ;
      - les silhouettes s'accordent et ce sont les **étiquettes d'encre** qui sont posées de
        travers **dans leur propre aplatissement**. Le recalage n'y peut rien, et le Dice doit
        rester maximal à zéro.

    ⚠ Le Dice est calculé sur l'intersection valide des deux fenêtres décalées, donc sur des
    surfaces comparables : décaler puis comparer des tableaux de tailles différentes ferait
    baisser le Dice avec la seule amputation.
    """
    h, w = support.shape
    grille, meilleur = [], None
    for di in range(-portee, portee + 1, pas):
        for dj in range(-portee, portee + 1, pas):
            i0, i1 = max(0, di), min(h, h + di)
            j0, j1 = max(0, dj), min(w, w + dj)
            a = masque_recale[i0:i1, j0:j1]
            b = support[i0 - di:i1 - di, j0 - dj:j1 - dj]
            s_ = a.sum() + b.sum()
            d = float(2.0 * (a & b).sum() / s_) if s_ else 0.0
            grille.append(dict(di=di, dj=dj, dice=round(d, 5)))
            if meilleur is None or d > meilleur["dice"]:
                meilleur = dict(di=di, dj=dj, dice=round(d, 5))
    zero = next(c["dice"] for c in grille if c["di"] == 0 and c["dj"] == 0)
    return dict(portee=portee, pas=pas, grille=grille, meilleur=meilleur,
                dice_sans_decalage=zero,
                maximum_au_bord=bool(abs(meilleur["di"]) >= portee
                                     or abs(meilleur["dj"]) >= portee))


def accord_global(carte: np.ndarray, etiquettes: np.ndarray,
                  candidats: dict[str, tuple[float, float]]) -> dict:
    """L'AUC de la carte publiée sur TOUTE l'empreinte, à quelques décalages nommés.

    ⚠⚠ POURQUOI CE CHIFFRE À CÔTÉ DES FENÊTRES. `75` publie **0,756** comme l'accord de la carte
    publiée avec les étiquettes, et ce nombre sert de référence à tout le lot. S'il monte de
    plusieurs centièmes en décalant les étiquettes d'un déplacement constant, alors ce n'est pas
    une propriété du détecteur qui était mesurée mais un **défaut de recalage des données
    publiées elles-mêmes** — et la référence doit être corrigée avant d'être comparée à quoi que
    ce soit.

    ⚠ Les deux populations sont prises sur la MÊME empreinte décalée, donc les comptes bougent
    d'un décalage à l'autre ; ils sont rendus pour qu'un écart de population ne passe pas pour un
    écart d'accord.
    """
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415

    h, w = carte.shape
    out = {}
    for nom, (di, dj) in candidats.items():
        di, dj = int(round(di)), int(round(dj))
        i0, i1 = max(0, di), min(h, h + di)
        j0, j1 = max(0, dj), min(w, w + dj)
        reg = etiquettes[i0:i1, j0:j1]
        ref = carte[i0 - di:i1 - di, j0 - dj:j1 - dj]
        ok = np.isfinite(ref) & (ref > 0)
        a = ref[ok & (reg > 0.5)].ravel()
        b = ref[ok & (reg <= 0.5)].ravel()
        out[nom] = dict(decalage=[di, dj],
                        auc=(round(aire_sous_la_courbe(a, b), 5)
                             if a.size >= 100 and b.size >= 100 else None),
                        pixels_encre=int(a.size), pixels_fond=int(b.size))
    return out


def melanger_la_carte(carte: np.ndarray, graine: int = 42) -> np.ndarray:
    """La même carte, ses valeurs permutées DANS l'empreinte.

    ⚠⚠ Dans l'empreinte : permuter le rectangle entier ferait entrer des zéros hors fragment
    parmi les valeurs, donc changerait la population comparée en plus de casser la place. Le
    témoin doit casser **une seule** chose.
    """
    rng = np.random.default_rng(graine)
    out = carte.copy()
    dedans = np.isfinite(carte) & (carte > 0)
    v = out[dedans]
    rng.shuffle(v)
    out[dedans] = v
    return out


def balayer_constantes(carte: np.ndarray, etiquettes: np.ndarray, liste: list[tuple[int, int]],
                       cote: int, portee: int, pas: int) -> dict:
    """L'AUC médiane sur les fenêtres, en fonction d'un décalage CONSTANT.

    ⚠⚠ La position du maximum dans la grille est rendue avec lui. `75` a publié un optimum à
    (−104, −120) **au bord** de son balayage : un maximum au bord ne désigne pas un déplacement,
    il dit que le balayage était trop court, et le lire comme un résultat est le piège que ce
    dépôt a déjà payé.
    """
    liste = fenetres_deplacables(liste, carte.shape, cote, portee)
    grille, meilleur = [], None
    for di in range(-portee, portee + 1, pas):
        for dj in range(-portee, portee + 1, pas):
            v = [x for x in (aire(carte, etiquettes, f, cote, di, dj) for f in liste)
                 if x is not None]
            if not v:
                continue
            m = float(np.median(v))
            grille.append(dict(di=di, dj=dj, auc=round(m, 5), fenetres=len(v)))
            if meilleur is None or m > meilleur["auc"]:
                meilleur = dict(di=di, dj=dj, auc=round(m, 5))
    if meilleur is None:
        return {}
    au_bord = abs(meilleur["di"]) >= portee or abs(meilleur["dj"]) >= portee
    return dict(portee=portee, pas=pas, grille=grille, meilleur=meilleur,
                maximum_au_bord=bool(au_bord))


def constantes_sur_toutes_les_fenetres(carte: np.ndarray, etiquettes: np.ndarray,
                                       liste: list[tuple[int, int]], cote: int, portee: int,
                                       candidats: dict[str, tuple[float, float]]) -> dict:
    """Quelques décalages constants jugés sur TOUTES les fenêtres déplaçables.

    ⚠⚠ POURQUOI SÉPARÉ DE `comparer`. Un champ **refuse** hors de portée de ses contraintes, donc
    la comparaison tête-à-tête n'a lieu que là où tout le monde répond — et les repères sont
    groupés d'un côté, ce qui réduit d'autant. Une constante, elle, répond partout : la juger sur
    l'empreinte entière est la seule façon de dire si elle vaut mieux que l'affine **du fragment**
    et non seulement du quart où les repères vivent.

    ⚠ Le compte de fenêtres améliorées est rendu avec la médiane : une médiane qui monte de deux
    millièmes en cassant la moitié des fenêtres n'est pas une amélioration.
    """
    liste = fenetres_deplacables(liste, carte.shape, cote, portee)
    base = {f: aire(carte, etiquettes, f, cote, 0, 0) for f in liste}
    retenues = [f for f in liste if base[f] is not None]
    out = {}
    for nom, (di, dj) in candidats.items():
        v, mieux = [], 0
        for f in retenues:
            a = aire(carte, etiquettes, f, cote, di, dj)
            if a is None:
                continue
            v.append(a)
            mieux += int(a > base[f])
        out[nom] = dict(decalage=[round(float(di), 2), round(float(dj), 2)],
                        auc_mediane=round(float(np.median(v)), 5) if v else None,
                        fenetres_ameliorees=mieux, fenetres=len(v))
    out["_fenetres"] = len(retenues)
    out["_auc_du_champ_nul"] = (round(float(np.median([base[f] for f in retenues])), 5)
                                if retenues else None)
    return out


def comparer(carte: np.ndarray, etiquettes: np.ndarray, liste: list[tuple[int, int]], cote: int,
             pretendants: dict[str, object]) -> dict:
    """Chaque prétendant jugé sur les MÊMES fenêtres, contre le champ nul.

    ⚠⚠ Une fenêtre n'entre au dossier que si **tous** les prétendants y répondent : comparer des
    médianes calculées sur des sous-ensembles différents comparerait des fragments différents, et
    c'est exactement ce qui laisserait un champ à courte portée paraître bon en n'étant jugé que
    là où il est bon.
    """
    noms = list(pretendants)
    lignes = []
    for f in liste:
        ci, cj = f[0] + cote // 2, f[1] + cote // 2
        vals = {}
        base = aire(carte, etiquettes, f, cote, 0, 0)
        if base is None:
            continue
        for nom in noms:
            p = pretendants[nom]
            d = p(ci, cj) if callable(p) else p
            vals[nom] = None if d is None else aire(carte, etiquettes, f, cote, d[0], d[1])
        if any(v is None for v in vals.values()):
            continue
        lignes.append(dict(fenetre=[f[0], f[1]], nul=round(base, 5),
                           **{n: round(vals[n], 5) for n in noms}))
    if not lignes:
        return {}
    nul = np.array([l["nul"] for l in lignes])
    mediane = float(np.median(nul))
    resume = {}
    for nom in noms:
        v = np.array([l[nom] for l in lignes])
        g = v - nul
        discordantes = nul < mediane
        resume[nom] = dict(
            auc_mediane=round(float(np.median(v)), 5),
            gain_median=round(float(np.median(g)), 5),
            fenetres_ameliorees=int((g > 0).sum()),
            gain_median_discordantes=round(float(np.median(g[discordantes])), 5),
            ameliorees_discordantes=int((g[discordantes] > 0).sum()))
    return dict(fenetres=len(lignes), auc_mediane_du_champ_nul=round(mediane, 5),
                mediane_de_partage=round(mediane, 5),
                discordantes=int((nul < mediane).sum()), resume=resume, lignes=lignes)


def optimum_par_fenetre(carte: np.ndarray, etiquettes: np.ndarray,
                        liste: list[tuple[int, int]], cote: int,
                        portee: int, pas: int) -> dict:
    """Le décalage que CHAQUE fenêtre préfère, et la dispersion de ces préférences.

    ⚠⚠⚠ C'EST LA QUESTION POSÉE À L'ENVERS, ET C'EST ELLE QUI TRANCHE. Comparer des champs dit
    lequel gagne ; demander à chaque fenêtre ce qu'elle veut dit s'il y a quelque chose à
    gagner. Si les optima se ressemblent tous, le résidu est une **translation** et aucun champ
    ne peut faire mieux qu'elle ; s'ils se dispersent, un champ existe et les nôtres sont
    seulement mauvais.

    ⚠ La dispersion rendue est une BORNE SUPÉRIEURE de la dispersion vraie : l'optimum d'une
    fenêtre est estimé avec du bruit, et ce bruit s'ajoute à l'étalement. Ce qui est donc
    interprétable est « le champ vrai varie d'AU PLUS tant », ce qui suffit pour le comparer à
    l'amplitude des champs candidats.

    ⚠ Le compte des optima **au bord** du balayage est rendu : une fenêtre dont l'optimum touche
    la borne n'a pas d'optimum, elle a une borne.
    """
    liste = fenetres_deplacables(liste, carte.shape, cote, portee)
    opt, au_bord = [], 0
    for f in liste:
        meilleur = None
        for di in range(-portee, portee + 1, pas):
            for dj in range(-portee, portee + 1, pas):
                v = aire(carte, etiquettes, f, cote, di, dj)
                if v is not None and (meilleur is None or v > meilleur[0]):
                    meilleur = (v, di, dj)
        if meilleur is None:
            continue
        if abs(meilleur[1]) >= portee or abs(meilleur[2]) >= portee:
            au_bord += 1
        opt.append(dict(fenetre=[f[0], f[1]], di=meilleur[1], dj=meilleur[2],
                        auc=round(meilleur[0], 5)))
    if not opt:
        return {}
    o = np.array([[e["di"], e["dj"]] for e in opt], dtype=float)
    return dict(portee=portee, pas=pas, fenetres=len(opt), optima=opt,
                di_median=float(np.median(o[:, 0])), dj_median=float(np.median(o[:, 1])),
                dispersion_di=round(float(o[:, 0].std()), 2),
                dispersion_dj=round(float(o[:, 1].std()), 2),
                dispersion_um=round(float(np.hypot(o[:, 0].std(), o[:, 1].std()) * CELLULE_UM), 1),
                translation_um=round(float(np.hypot(np.median(o[:, 0]),
                                                    np.median(o[:, 1]))) * CELLULE_UM, 1),
                optima_au_bord=au_bord)


def _charger() -> tuple[np.ndarray, np.ndarray, np.ndarray, str] | None:
    """La carte publiée, les étiquettes ET le masque, transportés par la MÊME affine.

    ⚠⚠ Les trois sortent d'ici et l'affine n'est calculée qu'une fois : deux appels à
    `affine_par_boites` sur les mêmes entrées ne peuvent pas se contredire aujourd'hui, mais
    deux sites qui dérivent la même transformation sont deux endroits où l'un peut changer sans
    l'autre — et le plan des silhouettes ne vaut que s'il est dans le repère du plan de l'encre.
    """
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415

    masque, etiquettes = rec._image("500P2_mask.png"), rec._image("500P2_inklabels.png")
    publiee = rec.carte_publiee_reduite()
    if masque is None or etiquettes is None or publiee is None:
        return None
    carte, nom = publiee
    empreinte = (carte > 0).astype(float)
    t = rec.affine_par_boites(masque, empreinte)
    # ⚠⚠ Le masque est rendu NON SEUILLÉ, et ce détail a fait échouer un recoupement : la mesure
    # antérieure réduit à 1024² **puis** seuille à 0,5 sur une échelle de 0 à 255, ce qui garde
    # un bloc dès qu'il porte un peu de matière. Seuiller d'abord donne une réduction par
    # MAJORITÉ, donc un autre nombre. Rendre le tableau brut laisse chaque appelant choisir le
    # sien, et laisse le contrôle refaire exactement celui qui est déjà publié.
    return (carte, rec.appliquer(etiquettes, t, empreinte.shape),
            rec.appliquer(masque, t, empreinte.shape), nom)


def mesurer(cote: int = 269, pas_fenetre: int = 134, rayon: float = 300.0,
            portee: int = 48, pas_balayage: int = 8, graine: int = 42) -> dict:
    """Le dossier complet : les champs, leurs constantes, le balayage, et les deux témoins."""
    charge = _charger()
    if charge is None:
        raise SystemExit("carte publiée ou masque absents")
    carte, eti, masque_recale, nom = charge

    champ = json.loads(RECALAGE.read_text()).get("champ_local", {})
    paires = json.loads(REPERES.read_text()).get("paires", [])
    pos_b, dep_b = deplacements_des_carreaux(champ)
    pos_r, dep_r = deplacements_des_reperes(paires)
    if pos_b.size == 0 or pos_r.size == 0:
        raise SystemExit("champ de bord ou repères absents")

    rng = np.random.default_rng(graine)
    dep_melange = dep_r[rng.permutation(len(dep_r))]
    cst_b = (float(np.median(dep_b[:, 0])), float(np.median(dep_b[:, 1])))
    cst_r = (float(np.median(dep_r[:, 0])), float(np.median(dep_r[:, 1])))

    liste = fenetres(carte, eti, cote, pas_fenetre)
    silhouettes = accord_des_silhouettes(masque_recale > 0.5, carte > 0, portee, pas_balayage)
    # ⚠⚠ LE RECOUPEMENT EST CALCULÉ ICI ET NON DANS LA BATTERIE, et c'est un choix de coût. Il
    # exige de transporter le masque entier (400 M pixels) puis de le réduire à 1024², donc
    # quelques minutes : payé une fois à la mesure, il devient un nombre que le contrôle compare
    # à celui déjà publié en un instant. Une batterie qui coûte cinq minutes est une batterie
    # qu'on cesse de lancer, et un contrôle qu'on ne lance pas n'en est plus un.
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415

    dice_publie = rec.dice(rec._reduire(masque_recale, rec.COTE_VALIDATION),
                           rec._reduire((carte > 0).astype(float), rec.COTE_VALIDATION))
    pretendants = {
        "champ_de_bord": lambda i, j: predire(pos_b, dep_b, i, j, rayon),
        "champ_des_reperes": lambda i, j: predire(pos_r, dep_r, i, j, rayon),
        "reperes_positions_melangees": lambda i, j: predire(pos_r, dep_melange, i, j, rayon),
        "constante_des_bords": cst_b,
        "constante_des_reperes": cst_r,
    }
    balayage = balayer_constantes(carte, eti, liste, cote, portee, pas_balayage)
    dossier = comparer(carte, eti, liste, cote, pretendants)
    # ⚠⚠ UNE TROISIÈME COMPARAISON, ET SA RAISON EST LE COMPTE DE FENÊTRES. Le tête-à-tête
    # ci-dessus n'a lieu que là où TOUS les prétendants répondent, or les repères sont groupés
    # d'un côté : la question « le champ de bord bat-il sa propre constante ? » mérite d'être
    # posée là où le champ de bord répond, c'est-à-dire sur bien plus de fenêtres.
    du_bord = comparer(carte, eti, liste, cote,
                       {"champ_de_bord": lambda i, j: predire(pos_b, dep_b, i, j, rayon),
                        "constante_des_bords": cst_b})
    global_ = accord_global(carte, eti,
                            {"champ_nul": (0.0, 0.0), "constante_des_bords": cst_b,
                             "constante_des_reperes": cst_r,
                             "optimum_des_fenetres": (float(balayage["meilleur"]["di"]),
                                                      float(balayage["meilleur"]["dj"]))}
                            ) if balayage else {}
    partout = constantes_sur_toutes_les_fenetres(
        carte, eti, liste, cote, portee,
        {"champ_nul": (0.0, 0.0), "constante_des_bords": cst_b,
         "constante_des_reperes": cst_r})
    temoin = balayer_constantes(melanger_la_carte(carte, graine), eti, liste, cote,
                                portee, pas_balayage * 3)
    return dict(carte_publiee=nom, cote=cote, pas_fenetre=pas_fenetre, rayon=rayon,
                cellule_um=CELLULE_UM,
                carreaux_du_bord=len(pos_b), reperes=len(pos_r),
                # ⚠⚠ L'AMPLITUDE DE CHAQUE CHAMP CANDIDAT est rendue à côté de la dispersion des
                # optima, parce que c'est la comparaison qui tranche : un champ qui déplace de
                # soixante cases là où les fenêtres ne divergent que de vingt ne corrige pas un
                # champ, il en invente un.
                norme_mediane_des_bords=round(float(np.median(np.hypot(dep_b[:, 0],
                                                                      dep_b[:, 1]))), 2),
                norme_mediane_des_reperes=round(float(np.median(np.hypot(dep_r[:, 0],
                                                                        dep_r[:, 1]))), 2),
                constante_des_bords=[round(cst_b[0], 2), round(cst_b[1], 2)],
                constante_des_reperes=[round(cst_r[0], 2), round(cst_r[1], 2)],
                laisser_un_dehors_reperes=laisser_un_dehors(pos_r, dep_r, rayon),
                laisser_un_dehors_bords=laisser_un_dehors(pos_b, dep_b, rayon),
                accord_des_silhouettes=silhouettes, accord_global=global_,
                dice_a_la_resolution_publiee=dice_publie,
                cote_de_validation=rec.COTE_VALIDATION,
                comparaison=dossier, comparaison_du_bord=du_bord,
                constantes_partout=partout, balayage=balayage, temoin_carte_melangee=temoin,
                optimum_par_fenetre=optimum_par_fenetre(carte, eti, liste, cote,
                                                        portee, pas_balayage))


def _fixture(cote: int = 600, decalage: tuple[int, int] = (0, 0),
             bande: int = 0, marge: int = 60, graine: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Une carte d'encre et ses étiquettes, décalées d'un déplacement CONNU.

    ⚠ Les étiquettes sont bâties **depuis** la carte, donc la seule chose qui les sépare est le
    déplacement : une fixture où les deux seraient tirées séparément mesurerait la chance.

    ⚠⚠ `bande` fabrique un vrai CHAMP et non un gradient doux : chaque bande de 200 lignes reçoit
    son propre décalage. Un gradient continu est écrasé par une fenêtre plus large que lui — ma
    première version variait avec la ligne, donc chaque fenêtre voyait le champ symétrique
    autour de son centre et préférait zéro, et le contrôle « un vrai champ disperse les optima »
    ne pouvait pas échouer.

    ⚠ La marge tient l'encre loin des bords : le décalage y ferait sortir des étiquettes du
    tableau, et une fenêtre à qui il manque ses étiquettes n'est pas une fenêtre mal recalée.
    """
    rng = np.random.default_rng(graine)
    encre = np.zeros((cote, cote), dtype=bool)
    for _ in range(cote * 2):
        i, j = rng.integers(marge, cote - marge, size=2)
        encre[i - 5:i + 5, j - 5:j + 5] = True
    carte = np.where(encre, 200.0, 60.0) + rng.normal(0, 6.0, size=(cote, cote))
    carte = np.clip(carte, 1.0, 255.0)
    eti = np.zeros_like(carte)
    ii, jj = np.nonzero(encre)
    di = decalage[0] + bande * (ii // 200)
    a, b = ii + di, jj + decalage[1]
    garde = (a >= 0) & (a < cote) & (b >= 0) & (b < cote)
    eti[a[garde], b[garde]] = 1.0
    return carte, eti


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- la convention de signe, dérivée puis vérifiée ---
    paires = [{"source": [110.0, 205.0], "cible": [100.0, 200.0]}]
    pos, dep = deplacements_des_reperes(paires)
    v("le déplacement d'un repère est source − cible",
      dep.shape == (1, 2) and dep[0, 0] == 10.0 and dep[0, 1] == 5.0, str(dep))
    v("... et il est porté par la CIBLE, dans le repère de la carte",
      pos[0, 0] == 100.0 and pos[0, 1] == 200.0, str(pos))
    v("aucune paire ne rend aucun déplacement", deplacements_des_reperes([])[0].shape == (0, 2))

    ch = {"pas": 128, "carreaux": [{"i": 0, "j": 256, "di": -5, "dj": 3}]}
    pb, db = deplacements_des_carreaux(ch)
    v("un carreau est porté par son CENTRE, pas son coin",
      pb[0, 0] == 64.0 and pb[0, 1] == 320.0, str(pb))
    v("... et son déplacement est recopié tel quel", db[0, 0] == -5.0 and db[0, 1] == 3.0)

    # --- la prédiction ---
    p = np.array([[0.0, 0.0], [100.0, 0.0]])
    d = np.array([[4.0, 2.0], [4.0, 2.0]])
    v("un champ constant est prédit exactement",
      predire(p, d, 50.0, 0.0, 200.0) == (4.0, 2.0))
    v("hors de portée, le champ REFUSE au lieu d'extrapoler",
      predire(p, d, 5000.0, 0.0, 200.0) is None)
    v("... et à distance nulle il ne diverge pas",
      predire(p, d, 0.0, 0.0, 200.0) == (4.0, 2.0))
    # ⚠⚠ Le contrôle discriminant : sur un champ LINÉAIRE, une implémentation qui rendrait la
    # moyenne globale passerait les trois contrôles précédents. Ici elle rendrait 0 partout.
    pl = np.array([[float(k) * 100.0, 0.0] for k in range(11)])
    dl = np.array([[float(k) * 100.0 - 500.0, 0.0] for k in range(11)])
    est = predire(pl, dl, 800.0, 0.0, 1e9)
    v("un champ linéaire est prédit près de sa valeur locale, pas de sa moyenne",
      est is not None and est[0] > 100.0, f"{est} contre 300 attendu, 0 pour une moyenne")

    # --- laisser-un-dehors, dans les deux sens ---
    n = 40
    ii = np.linspace(0.0, 1000.0, n)
    lisse = np.stack([ii, np.zeros(n)], axis=1)
    dl2 = np.stack([ii / 10.0 - 50.0, np.zeros(n)], axis=1)
    r = laisser_un_dehors(lisse, dl2, 400.0, tirages=8)
    v("un champ lisse bat le champ nul", r["bat_le_champ_nul"],
      f"{r['erreur_mediane']:.2f} contre {r['erreur_du_champ_nul']:.2f}")
    v("... et bat ses positions mélangées", r["bat_les_positions_melangees"],
      f"témoin {r['temoin_positions_melangees_meilleur']:.2f}")
    rng = np.random.default_rng(11)
    bruit = rng.normal(0.0, 50.0, size=(n, 2))
    rb = laisser_un_dehors(lisse, bruit, 400.0, tirages=8)
    v("un champ de bruit ne bat pas ses positions mélangées",
      not rb["bat_les_positions_melangees"],
      f"{rb['erreur_mediane']:.2f} contre {rb['temoin_positions_melangees_meilleur']:.2f}")

    # --- les fenêtres et l'AUC ---
    carte, eti = _fixture(decalage=(0, 0))
    liste = fenetres_deplacables(fenetres(carte, eti, 200, 100, minimum=200),
                                 carte.shape, 200, 48)
    v("des fenêtres sont retenues", len(liste) >= 4, str(len(liste)))
    v("... et aucune sans assez d'encre ni de fond",
      fenetres(carte, np.zeros_like(eti), 200, 100, minimum=200) == [])
    # ⚠⚠ Le filtre des fenêtres déplaçables est ce qui garde la surface comparable : une fenêtre
    # collée au bord répondrait à +48 et pas à −48, donc entrerait dans la médiane d'un point de
    # grille et pas de l'autre.
    v("une fenêtre collée au bord est écartée du balayage",
      (0, 0) not in fenetres_deplacables([(0, 0), (100, 100)], (600, 600), 200, 48)
      and (100, 100) in fenetres_deplacables([(0, 0), (100, 100)], (600, 600), 200, 48))
    a0 = aire(carte, eti, liste[0], 200, 0, 0, minimum=200)
    v("l'AUC d'un accord parfait est élevée", a0 is not None and a0 > 0.9, str(a0))
    a1 = aire(carte, eti, liste[0], 200, 40, 40, minimum=200)
    v("... et un décalage la fait tomber", a1 is not None and a1 < a0, f"{a1} contre {a0}")

    # --- le témoin de la carte mélangée ---
    mel = melanger_la_carte(carte)
    dedans = np.isfinite(carte) & (carte > 0)
    v("le mélange garde exactement les mêmes valeurs dans l'empreinte",
      np.array_equal(np.sort(carte[dedans]), np.sort(mel[dedans])))
    v("... et ne touche rien hors de l'empreinte",
      np.array_equal(carte[~dedans], mel[~dedans]))
    am = aire(mel, eti, liste[0], 200, 0, 0, minimum=200)
    v("... et il détruit l'accord", am is not None and abs(am - 0.5) < 0.05, str(am))

    # --- le balayage retrouve un décalage planté, et sait dire qu'il touche le bord ---
    # ⚠ Le décalage planté est un MULTIPLE du pas du balayage : à (12, −8) sur une grille de 8
    # l'optimum vrai n'est pas dans la grille, donc le contrôle jugerait l'arrondi et non la
    # recherche. Et le pas est de 8 plutôt que 4 parce que la batterie coûtait 110 s pour 4 874
    # AUC, dont les deux tiers dans ces balayages — mesuré au profileur, pas supposé.
    carte2, eti2 = _fixture(decalage=(16, -8))
    liste2 = fenetres_deplacables(fenetres(carte2, eti2, 200, 100, minimum=200),
                                  carte2.shape, 200, 48)
    b = balayer_constantes(carte2, eti2, liste2, 200, 24, 8)
    v("le balayage retrouve le décalage planté",
      b and b["meilleur"]["di"] == 16 and b["meilleur"]["dj"] == -8,
      str(b.get("meilleur")))
    v("... et le déclare loin du bord", b and not b["maximum_au_bord"])
    # ⚠⚠ Le contrôle inverse, sans lequel `maximum_au_bord` serait une constante à False : un
    # balayage trop court DOIT le dire, sinon on republie l'optimum (−104, −120) de `75`.
    b2 = balayer_constantes(carte2, eti2, liste2, 200, 8, 8)
    v("un balayage trop court se déclare au bord", b2 and b2["maximum_au_bord"],
      str(b2.get("meilleur")))

    # --- l'optimum par fenêtre distingue une translation d'un champ ---
    o1 = optimum_par_fenetre(carte2, eti2, liste2, 200, 24, 8)
    carte3, eti3 = _fixture(decalage=(0, 0), bande=12)
    liste3 = fenetres_deplacables(fenetres(carte3, eti3, 200, 100, minimum=200),
                                  carte3.shape, 200, 48)
    o3 = optimum_par_fenetre(carte3, eti3, liste3, 200, 24, 8)
    # ⚠⚠ L'ÉTENDUE, PAS L'ÉCART-TYPE, et l'attendu est DÉRIVÉ. Une translation doit donner le
    # MÊME optimum partout — étendue nulle — et un champ à bandes de 12 doit faire différer deux
    # fenêtres d'au moins une bande moins le pas du balayage. Comparer deux écarts-types par un
    # facteur choisi laisserait passer un champ dont les optima diffèrent d'un pas de rien.
    def etendue_di(o):
        d = [e["di"] for e in o["optima"]]
        return max(d) - min(d)

    v("une translation donne le MÊME optimum dans toutes les fenêtres",
      o1 and etendue_di(o1) == 0, f"étendue {etendue_di(o1) if o1 else None}")
    v("... et un champ à bandes de 12 les fait différer d'au moins une bande moins le pas",
      o3 and etendue_di(o3) >= 12 - 8, f"étendue {etendue_di(o3) if o3 else None}")

    # --- la comparaison n'accepte que les fenêtres où TOUT LE MONDE répond ---
    c = comparer(carte2, eti2, liste2, 200,
                 {"bon": (16, -8), "muet": lambda i, j: None})
    v("un prétendant muet vide la comparaison plutôt que de la fausser",
      c == {} or c["fenetres"] == 0, str(c.get("fenetres")))
    # --- l'accord global, et le contrôle qui empêche de lire un écart de population ---
    g = accord_global(carte2, eti2, {"nul": (0.0, 0.0), "bon": (16.0, -8.0)})
    v("l'accord global monte au décalage planté", g["bon"]["auc"] > g["nul"]["auc"],
      f"{g['bon']['auc']} contre {g['nul']['auc']}")
    # ⚠⚠ Sans ce contrôle, une AUC qui monte parce que le décalage a rogné l'empreinte jusqu'à ne
    # garder que les pixels faciles passerait pour un gain. Les deux populations doivent rester
    # du même ordre.
    v("... sans que la population d'encre s'effondre",
      g["bon"]["pixels_encre"] > 0.5 * g["nul"]["pixels_encre"],
      f"{g['bon']['pixels_encre']} contre {g['nul']['pixels_encre']}")

    # --- le plan des silhouettes, dans les deux sens ---
    sil = np.zeros((300, 300), dtype=bool)
    sil[80:220, 60:200] = True
    dec = np.zeros_like(sil)
    dec[80 + 16:220 + 16, 60 - 8:200 - 8] = True
    a1 = accord_des_silhouettes(dec, sil, 24, 4)
    v("le plan des silhouettes retrouve un décalage planté",
      a1["meilleur"]["di"] == 16 and a1["meilleur"]["dj"] == -8, str(a1["meilleur"]))
    v("... et son Dice y est meilleur que sans décalage",
      a1["meilleur"]["dice"] > a1["dice_sans_decalage"],
      f"{a1['meilleur']['dice']} contre {a1['dice_sans_decalage']}")
    # ⚠⚠ LE CAS QUI DÉCIDE DE LA CAUSE, et sans lui la fonction ne prouverait rien : deux
    # silhouettes DÉJÀ d'accord doivent avoir leur maximum à zéro. Si le plan de l'encre a son
    # maximum ailleurs, alors ce sont les étiquettes qui sont posées de travers, pas le recalage.
    a2 = accord_des_silhouettes(sil, sil, 24, 4)
    v("deux silhouettes déjà d'accord ont leur maximum à zéro",
      a2["meilleur"]["di"] == 0 and a2["meilleur"]["dj"] == 0 and a2["meilleur"]["dice"] > 0.99,
      str(a2["meilleur"]))

    # --- les constantes sur toutes les fenêtres ---
    pa = constantes_sur_toutes_les_fenetres(carte2, eti2, liste2, 200, 48,
                                            {"nul": (0.0, 0.0), "bonne": (16.0, -8.0),
                                             "fausse": (30.0, 30.0)})
    v("la bonne constante améliore presque toutes les fenêtres",
      pa["bonne"]["fenetres_ameliorees"] >= pa["_fenetres"] - 1,
      f"{pa['bonne']['fenetres_ameliorees']}/{pa['_fenetres']}")
    # ⚠⚠ MON ASSERTION ÉTAIT FAUSSE, PAS LE CODE : j'avais écrit « la fausse n'améliore aucune
    # fenêtre », et elle en améliore 7 sur 9. Sur une fixture dense, un mauvais décalage pose les
    # étiquettes AU HASARD, donc l'AUC vaut 0,5 — et le champ nul, décalé de 14 cases, vaut 0,496.
    # Comparer deux tirages de pile ou face par un compte de signes ne peut rien dire. Ce qui se
    # mesure, c'est que la bonne constante SORT du hasard et que la fausse y reste.
    v("... et la fausse reste au hasard là où la bonne en sort",
      abs(pa["fausse"]["auc_mediane"] - 0.5) < 0.05 and pa["bonne"]["auc_mediane"] > 0.95,
      f"{pa['fausse']['auc_mediane']} contre {pa['bonne']['auc_mediane']}")
    # ⚠⚠ LA PROPRIÉTÉ QUI REND CE TABLEAU COMPARABLE : une constante répond partout, donc toutes
    # les lignes portent le MÊME compte de fenêtres. Si un jour l'une en portait moins, ses
    # médianes cesseraient d'être comparables aux autres sans que rien ne le dise.
    v("toutes les constantes sont jugées sur le même compte de fenêtres",
      len({pa[n]["fenetres"] for n in ("nul", "bonne", "fausse")}) == 1,
      str([pa[n]["fenetres"] for n in ("nul", "bonne", "fausse")]))
    v("... et le champ nul ne s'améliore pas lui-même",
      pa["nul"]["fenetres_ameliorees"] == 0)

    c2 = comparer(carte2, eti2, liste2, 200, {"bon": (16, -8), "faux": (24, 24)})
    # ⚠⚠ MÊME PIÈGE QUE CI-DESSUS, ET IL M'A REPRIS : « le mauvais prétendant PERD » compare
    # deux tirages de pile ou face — un décalage absurde pose les étiquettes au hasard, donc son
    # gain oscille autour de zéro et son SIGNE ne veut rien dire. Ce qui se mesure est que le bon
    # sort du hasard et que le mauvais y reste.
    v("le bon prétendant sort du hasard, le mauvais y reste",
      c2["resume"]["bon"]["gain_median"] > 0.4
      and abs(c2["resume"]["faux"]["gain_median"]) < 0.05,
      f"{c2['resume']['bon']['gain_median']} / {c2['resume']['faux']['gain_median']}")

    # --- le recoupement avec la mesure ANTÉRIEURE, s'il y a de quoi ---
    # ⚠⚠⚠ POURQUOI CE CONTRÔLE VAUT PLUS QUE LES AUTRES : `le_recalage_des_etiquettes` publie
    # `dice_apres`, l'accord des deux silhouettes après l'affine. Le plan des silhouettes de ce
    # fichier recalcule cette même quantité, par un autre chemin, et doit retomber dessus à son
    # point zéro. S'il n'y retombe pas, l'un des deux modules ne parle pas du repère qu'il croit
    # — et tout ce qui suit serait mesuré dans un repère inconnu.
    if RECALAGE.is_file() and (RACINE / "docs" / "mesures"
                               / "le_residu_est_une_translation.json").is_file():
        ancien = json.loads(RECALAGE.read_text())
        neuf = json.loads((RACINE / "docs" / "mesures"
                           / "le_residu_est_une_translation.json").read_text())
        sil = neuf.get("accord_des_silhouettes", {})
        # ⚠⚠⚠ MON ASSERTION ÉTAIT FAUSSE, PAS LE CODE, et l'écart valait 0,0013. `dice_apres` est
        # mesuré sur une **réduction 1024²** (`COTE_VALIDATION`), le plan des silhouettes à
        # pleine résolution : deux mesures de la même chose à deux échelles n'ont aucune raison
        # de coïncider au millième, et exiger qu'elles le fassent aurait fait rejeter un module
        # correct. Le recoupement se fait donc **à la résolution de l'ancien**, où il doit
        # tomber au chiffre près — c'est ce qui prouve que les deux modules transportent le
        # masque par la MÊME affine, ce que le plan des silhouettes suppose pour valoir quelque
        # chose.
        refait = neuf.get("dice_a_la_resolution_publiee")
        if refait is not None and ancien.get("dice_apres") is not None:
            v("le masque transporté ici est CELUI de la mesure déjà publiée",
              abs(refait - ancien["dice_apres"]) < 1e-9,
              f"{refait} contre {ancien['dice_apres']}")
            v("... et le plan des silhouettes, à pleine résolution, en diffère un peu",
              bool(sil) and abs(sil["dice_sans_decalage"] - ancien["dice_apres"]) < 5e-3,
              f"{sil.get('dice_sans_decalage')} contre {ancien['dice_apres']} "
              f"(réduction {neuf.get('cote_de_validation')}²)")
        car = ancien.get("champ_local", {}).get("carreaux")
        if car and neuf.get("norme_mediane_des_bords") is not None:
            attendu = float(np.median([np.hypot(c["di"], c["dj"]) for c in car]))
            v("... et l'amplitude du champ de bord est bien celle de ses 34 carreaux",
              abs(neuf["norme_mediane_des_bords"] - attendu) < 0.01,
              f"{neuf['norme_mediane_des_bords']} contre {attendu:.2f}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cote", type=int, default=269, help="côté d'une fenêtre, en cases")
    p.add_argument("--pas-fenetre", type=int, default=134)
    p.add_argument("--rayon", type=float, default=300.0)
    p.add_argument("--portee", type=int, default=48)
    p.add_argument("--pas-balayage", type=int, default=8)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.cote, a.pas_fenetre, a.rayon, a.portee, a.pas_balayage)
    c = r["comparaison"]
    print(f"fenêtres jugées {c['fenetres']}   dont discordantes {c['discordantes']}")
    print(f"AUC du champ nul (médiane) {c['auc_mediane_du_champ_nul']:.4f}\n")
    print(f"{'prétendant':<30} {'AUC':>8} {'gain':>8} {'améliorées':>12} {'discordantes':>14}")
    print("-" * 76)
    for nom, e in c["resume"].items():
        print(f"{nom:<30} {e['auc_mediane']:>8.4f} {e['gain_median']:>+8.4f} "
              f"{e['fenetres_ameliorees']:>7}/{c['fenetres']:<4} "
              f"{e['ameliorees_discordantes']:>8}/{c['discordantes']:<4}")
    d = r["comparaison_du_bord"]
    print(f"\nle champ de bord contre sa constante, sur {d['fenetres']} fenetres "
          f"(AUC nulle {d['auc_mediane_du_champ_nul']:.4f}) :")
    for nom, e in d["resume"].items():
        print(f"  {nom:<24} {e['auc_mediane']:.4f}  {e['gain_median']:+.4f}  "
              f"{e['fenetres_ameliorees']}/{d['fenetres']}")
    pa = r["constantes_partout"]
    print(f"\nles constantes sur les {pa['_fenetres']} fenetres de l'empreinte "
          f"(AUC nulle {pa['_auc_du_champ_nul']:.4f}) :")
    for nom, e in pa.items():
        if nom.startswith("_"):
            continue
        print(f"  {nom:<24} {e['decalage']}  {e['auc_mediane']:.4f}  "
              f"{e['fenetres_ameliorees']}/{e['fenetres']}")
    b = r["balayage"]["meilleur"]
    print(f"\noptimum d'une CONSTANTE sur l'encre  ({b['di']}, {b['dj']})  AUC {b['auc']:.4f}"
          f"   au bord : {'oui' if r['balayage']['maximum_au_bord'] else 'non'}")
    print("\nsur TOUTE l'empreinte, l'accord de la carte publiee :")
    for nom, e in r["accord_global"].items():
        print(f"  {nom:<24} {e['decalage']}  AUC {e['auc']:.4f}")
    sl = r["accord_des_silhouettes"]
    print(f"le meme decalage sur les SILHOUETTES : optimum ({sl['meilleur']['di']}, "
          f"{sl['meilleur']['dj']})  Dice {sl['meilleur']['dice']:.4f} contre "
          f"{sl['dice_sans_decalage']:.4f} sans decalage")
    t = r["temoin_carte_melangee"]["meilleur"]
    print(f"témoin, carte mélangée               ({t['di']}, {t['dj']})  AUC {t['auc']:.4f}")
    o = r["optimum_par_fenetre"]
    print(f"\noptimum PAR FENÊTRE : médiane ({o['di_median']:.0f}, {o['dj_median']:.0f}) "
          f"= {o['translation_um']:.0f} µm   dispersion "
          f"({o['dispersion_di']}, {o['dispersion_dj']}) = {o['dispersion_um']:.0f} µm")
    ld = r["laisser_un_dehors_reperes"]
    print(f"repères, laisser-un-dehors : {ld['erreur_mediane']:.2f} contre "
          f"{ld['erreur_du_champ_nul']:.2f} au champ nul et "
          f"{ld['temoin_positions_melangees_meilleur']:.2f} au meilleur mélange")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
