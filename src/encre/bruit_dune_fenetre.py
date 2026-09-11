#!/usr/bin/env python3
"""La dispersion 0,52–0,75 entre fragments est-elle un EFFET, ou le bruit d'une fenêtre ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. [`63`](../../docs/archive/63_la_premiere_verite_terrain.md) laisse
une seule tâche vivante : « la dispersion est réelle, elle est plus grande que tout écart
qu'on chercherait à mesurer entre deux réglages, et elle n'est pas expliquée ». Mais avant
de chercher **ce qui** distingue trois fragments, il faut savoir s'il y a quelque chose à
distinguer — parce que chaque fragment n'a été mesuré que par **une fenêtre**, et qu'une
mesure unique n'a pas de barre d'erreur.

⭐⭐ Le partage que ce fichier tranche :

  - si la dispersion **entre** fragments est du même ordre que la dispersion **dans** un
    fragment, alors « le fragment » n'explique rien du tout, et la réponse à `63` n'est pas
    une cause mais une **borne** : une fenêtre n'est pas une mesure d'un objet ;
  - si elle est nettement plus grande, alors il reste une cause à trouver, et on sait
    combien elle doit peser pour être visible.

⚠⚠ ET LE PIÈGE QUI DÉCIDE DE TOUT : la barre d'erreur d'une AUC **ne se calcule pas** par
la formule de Hanley–McNeil ici. Cette formule suppose des tirages indépendants, et une
carte d'encre est massivement auto-corrélée — deux pixels voisins portent presque la même
valeur et presque toujours la même étiquette. Sur un million de pixels elle rendrait une
erreur-type de l'ordre du dix-millième, donc elle « prouverait » que la dispersion est
réelle **quelle que soit** la dispersion. Le rééchantillonnage se fait donc **par tuiles**,
qui est l'échelle à laquelle la structure spatiale existe, jamais par pixels.

⚠ Ce que ce fichier N'ÉTABLIT PAS : *quelle* cause, si cause il y a. Il mesure la taille de
l'aiguille contre celle de la botte de foin, et rien d'autre.

Usage :
    uv run python src/encre/bruit_dune_fenetre.py --verifier
    uv run python src/encre/bruit_dune_fenetre.py --json docs/mesures/bruit_dune_fenetre.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from volume.evaluate_segment import auc, load_pair  # noqa: E402

FRAGMENTS = ("frag1", "frag2", "frag3")
"""Écrits plutôt que découverts : un quatrième doit être ajouté ici, donc vu."""

TUILE = 256
"""Le côté d'une tuile, en pixels.

⚠⚠ La MÊME valeur pour tous les fragments, et c'est une condition de validité : une tuile
plus petite rend une AUC plus bruitée, donc mesurer un fragment à 128 et un autre à 256
mettrait une part de « combien la tuile est bruitée » dans le compartiment « entre
fragments ». La comparaison n'aurait plus de sens et rien ne le signalerait.

⭐ 256 est aussi la maille d'annotation de `evaluate_segment.annotated_tiles`, donc les
tuiles d'ici coïncident avec celles dont ce dépôt dit déjà « quelqu'un a annoté là ».
"""

MINIMUM_POSITIFS = 64
"""Combien de pixels d'encre une tuile doit porter pour que son AUC veuille dire quelque chose.

⚠⚠ Une tuile qui n'a QU'UNE classe rend une AUC indéfinie, et la compter comme 0,5 serait
la faute qui fabrique la conclusion : chaque fragment serait tiré vers le milieu, donc
l'écart entre fragments rétrécirait, donc « la dispersion n'est pas réelle » sortirait de
l'instrument et non des données. Ces tuiles sont **écartées et comptées**.

⚠ Le seuil est bas exprès (64 pixels sur 65 536, soit 0,1 %) : il écarte le dégénéré, pas
le rare. Monter ce seuil jetterait justement les tuiles pauvres en encre, qui sont l'objet
même de la question posée au § « AUC contre densité ».
"""


def tuiles(prediction: np.ndarray, verite: np.ndarray, cote: int = TUILE,
           minimum: int = MINIMUM_POSITIFS) -> list[dict]:
    """AUC et densité d'encre de chaque tuile utilisable d'une carte.

    ⚠ Les tuiles de bord incomplètes sont **écartées** : une tuile deux fois plus petite
    porte une AUC deux fois plus bruitée, et la mélanger aux autres mettrait du bruit
    d'estimation dans la dispersion qu'on cherche à mesurer.

    ⚠⚠ ET LES PIXELS NON COUVERTS SONT ÉCARTÉS, exactement comme `evaluate_segment` le
    fait pour son domaine « tout le segment ». Ce n'est pas un détail de propreté : un
    pixel que le rendu n'a pas atteint vaut `NaN`, et `argsort` range les `NaN` **en
    tête** — ils seraient donc classés comme les pixels les MIEUX notés du fragment. Payé
    ici : la première version rendait 0,731 pour `Frag1` là où le dépôt publie 0,746, soit
    deux réponses à « quelle est l'AUC de ce fragment » — le motif que ce dépôt appelle
    « deux réponses à une même question », attrapé parce que le nombre existait déjà.
    """
    out = []
    h, w = prediction.shape
    for y in range(0, h - cote + 1, cote):
        for x in range(0, w - cote + 1, cote):
            p = prediction[y:y + cote, x:x + cote].ravel()
            t = verite[y:y + cote, x:x + cote].ravel()
            couvert = np.isfinite(p)
            p, t = p[couvert], t[couvert]
            positifs = int(t.sum())
            negatifs = int(t.size - positifs)
            if positifs < minimum or negatifs < minimum:
                continue
            out.append({
                "y": y, "x": x,
                "pixels": int(t.size),
                "encre_%": 100.0 * positifs / t.size,
                "auc": auc(p, t),
            })
    return out


def destriage(prediction: np.ndarray, verite: np.ndarray, lot: list[dict],
              cote: int = TUILE) -> dict:
    """De combien le classement GLOBAL souffre-t-il d'un décalage par région ?

    ⚠⚠ POURQUOI CETTE FONCTION EXISTE. La mesure principale a sorti un fait qui n'était pas
    prévu : sur `Frag3`, l'AUC **groupée** vaut 0,575 pendant que la moyenne des AUC **par
    tuile** vaut 0,845. Les deux nombres portent sur le même modèle et les mêmes étiquettes.
    Un tel écart ne peut venir que d'une chose : dans chaque tuile le modèle **range bien**
    l'encre, mais d'une tuile à l'autre il travaille à des **niveaux différents**, si bien
    qu'un pixel vierge d'une tuile « haute » passe devant un pixel encré d'une tuile
    « basse ».

    ⭐ Le décalage se mesure en le retirant : dans chaque tuile, les scores sont remplacés
    par leur **rang** ramené à [0, 1], ce qui aligne les niveaux sans toucher à l'ordre
    interne. Ce qui reste de l'AUC est ce que le modèle sait faire une fois ce défaut ôté.

    ⚠ Le témoin est calculé sur **exactement les mêmes pixels** (l'union des tuiles
    utilisables), jamais sur « tout le segment » : sinon la comparaison mêlerait le
    changement de domaine au changement de scores, et l'écart mesuré ne voudrait plus rien
    dire.
    """
    if not lot:
        return {"exploitable": False}
    brut, aligne, verites = [], [], []
    for t in lot:
        y, x = t["y"], t["x"]
        p_ = prediction[y:y + cote, x:x + cote].ravel()
        v_ = verite[y:y + cote, x:x + cote].ravel()
        couvert = np.isfinite(p_)
        p_, v_ = p_[couvert], v_[couvert]
        ordre = np.argsort(p_, kind="stable")
        rangs = np.empty(p_.size, dtype=np.float64)
        rangs[ordre] = np.arange(p_.size, dtype=np.float64)
        brut.append(p_)
        aligne.append(rangs / max(p_.size - 1, 1))
        verites.append(v_)
    brut = np.concatenate(brut)
    aligne = np.concatenate(aligne)
    verites = np.concatenate(verites)
    a_brut, a_aligne = auc(brut, verites), auc(aligne, verites)
    return {
        "exploitable": True,
        "pixels": int(verites.size),
        "auc_brute": a_brut,
        "auc_alignee": a_aligne,
        "gain": a_aligne - a_brut,
    }


def decomposer(par_fragment: dict[str, list[float]]) -> dict:
    """Variance INTRA (tuile à tuile) contre variance INTER (fragment à fragment).

    ⭐ C'est une analyse de variance à un facteur, et le nombre qui répond à `63` est le
    **coefficient de corrélation intraclasse** : la part de la dispersion totale qu'on peut
    attribuer à « de quel fragment vient cette tuile ».

      ICC proche de 0 → savoir de quel fragment vient une tuile n'apprend rien
      ICC proche de 1 → les fragments diffèrent nettement, et la cause reste à trouver

    ⚠⚠ La formule est celle d'ICC(1) à groupes de tailles inégales, pas la variance naïve
    des moyennes : avec trois groupes de tailles différentes, la variance des moyennes
    surestime l'effet de groupe, puisqu'une moyenne calculée sur peu de tuiles est
    elle-même bruitée. Une version naïve rendrait donc « les fragments diffèrent » un peu
    plus souvent qu'il ne faut, et toujours dans le même sens.
    """
    groupes = [v for v in par_fragment.values() if len(v) >= 2]
    k = len(groupes)
    n_total = sum(len(v) for v in groupes)
    if k < 2 or n_total <= k:
        return {"exploitable": False, "groupes": k, "tuiles": n_total}

    moyenne_generale = sum(sum(v) for v in groupes) / n_total
    ss_inter = sum(len(v) * (sum(v) / len(v) - moyenne_generale) ** 2 for v in groupes)
    ss_intra = sum(sum((x - sum(v) / len(v)) ** 2 for x in v) for v in groupes)
    ms_inter = ss_inter / (k - 1)
    ms_intra = ss_intra / (n_total - k)
    # Taille de groupe « effective » de Snedecor, pour des groupes inegaux.
    n0 = (n_total - sum(len(v) ** 2 for v in groupes) / n_total) / (k - 1)
    var_inter = max((ms_inter - ms_intra) / n0, 0.0)
    icc = var_inter / (var_inter + ms_intra) if (var_inter + ms_intra) > 0 else 0.0
    return {
        "exploitable": True,
        "groupes": k,
        "tuiles": n_total,
        "ecart_type_intra": math.sqrt(ms_intra),
        "ecart_type_inter": math.sqrt(var_inter),
        "icc": icc,
        "f": ms_inter / ms_intra if ms_intra > 0 else float("inf"),
    }


def bootstrap_par_tuiles(tuiles_du_fragment: list[dict], tirages: int = 2000,
                         graine: int = 0) -> dict:
    """Intervalle de confiance de l'AUC d'une fenêtre, en rééchantillonnant les TUILES.

    ⚠⚠ C'est le cœur du fichier. Rééchantillonner des **pixels** rendrait un intervalle
    ridiculement étroit — ils ne sont pas indépendants — et l'instrument déclarerait alors
    toute dispersion significative. Rééchantillonner des **tuiles** respecte la structure
    spatiale à l'échelle où elle existe.

    ⚠ La statistique rééchantillonnée est la MOYENNE des AUC de tuiles, pas l'AUC groupée :
    une AUC groupée recalculée sur des tuiles tirées avec remise compterait plusieurs fois
    les mêmes pixels dans le même classement de rangs, ce qui n'a pas de sens.
    """
    valeurs = np.array([t["auc"] for t in tuiles_du_fragment], dtype=np.float64)
    if valeurs.size < 2:
        return {"exploitable": False, "tuiles": int(valeurs.size)}
    rng = np.random.default_rng(graine)
    idx = rng.integers(0, valeurs.size, size=(tirages, valeurs.size))
    moyennes = valeurs[idx].mean(axis=1)
    return {
        "exploitable": True,
        "tuiles": int(valeurs.size),
        "moyenne": float(valeurs.mean()),
        "ic_bas": float(np.percentile(moyennes, 2.5)),
        "ic_haut": float(np.percentile(moyennes, 97.5)),
        "erreur_type": float(moyennes.std(ddof=1)),
    }


def se_hanley_mcneil(a: float, positifs: int, negatifs: int) -> float:
    """L'erreur-type que la formule usuelle rendrait — écrite pour être RÉFUTÉE.

    ⚠⚠ Elle n'est pas utilisée pour conclure. Elle est calculée et rapportée à côté du
    bootstrap par tuiles pour montrer **de combien** l'hypothèse d'indépendance se trompe
    sur une carte d'encre. Sans ce vis-à-vis, quelqu'un la rappliquerait un jour en croyant
    bien faire, et sortirait un intervalle cent fois trop étroit qui aurait l'air rigoureux.
    """
    if positifs < 1 or negatifs < 1:
        return float("nan")
    q1 = a / (2.0 - a)
    q2 = 2.0 * a * a / (1.0 + a)
    var = (a * (1 - a) + (positifs - 1) * (q1 - a * a)
           + (negatifs - 1) * (q2 - a * a)) / (positifs * negatifs)
    return math.sqrt(max(var, 0.0))


def quantile_normale(p: float) -> float:
    """Le quantile de la loi normale centrée réduite, sans dépendance.

    ⚠ Écrit ici plutôt qu'importé de scipy : ce dépôt tient à ce que ses batteries tournent
    hors ligne et sans installation. L'approximation est celle d'Acklam ; elle est vérifiée
    contre trois valeurs connues dans la batterie, ce qui est le seul moyen honnête de
    publier une formule qu'on n'a pas dérivée soi-même.
    """
    if not 0.0 < p < 1.0:
        return float("nan")
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    bas, haut = 0.02425, 1.0 - 0.02425
    if p < bas:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    if p > haut:
        return -quantile_normale(1.0 - p)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
           (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)


def tuiles_pour_distinguer(ecart: float, sigma: float, alpha: float = 0.05,
                           puissance: float = 0.80) -> int:
    """Combien de tuiles PAR FRAGMENT pour qu'un écart d'AUC soit établi.

    ⭐ C'est ce qui transforme le résultat en règle : mesurer un fragment par **une**
    fenêtre est une décision qu'on peut désormais chiffrer au lieu de la regretter après.

    ⚠⚠ Ce n'est PAS `fenetres_par_region.fenetres_pour_discriminer`, et les confondre
    donnerait un nombre faux. Celle-là compare des **proportions** (combien de fenêtres sont
    périodiques) par un test exact de Fisher ; celle-ci compare des **moyennes** d'AUC dont
    on connaît l'écart-type. Deux questions, deux formules — et c'est exactement pourquoi
    la seconde n'a pas été réutilisée.

    ⚠ Le résultat est un MINORANT : la formule suppose des tuiles indépendantes, or deux
    tuiles voisines d'un même fragment se ressemblent. Le vrai nombre est plus grand.
    """
    if ecart <= 0 or sigma <= 0:
        return 0
    z = quantile_normale(1.0 - alpha / 2.0) + quantile_normale(puissance)
    return int(math.ceil(2.0 * (z * sigma / ecart) ** 2))


def correlation(xs: list[float], ys: list[float]) -> float:
    """Pearson, écrit ici pour ne pas dépendre de scipy dans un script hors ligne."""
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx > 0 and dy > 0 else float("nan")


def mesurer(racine: Path = RACINE, fragments=FRAGMENTS, tirages: int = 2000) -> dict:
    """Le rapport complet, sur les cartes déjà rendues — aucun rendu n'est relancé."""
    par_fragment: dict[str, dict] = {}
    for frag in fragments:
        carte = racine / "data" / "out" / f"ink_{frag}_54keV.npy"
        labels = racine / "data" / frag / "labels_fenetre.png"
        if not carte.is_file() or not labels.is_file():
            continue
        prediction, verite = load_pair(carte, labels)
        lot = tuiles(prediction, verite)
        # ⚠ Le MEME domaine que `evaluate_segment` « tout le segment », pour que ce
        # fichier ne publie pas une seconde AUC du meme fragment.
        couvert = np.isfinite(prediction)
        positifs = int(verite[couvert].sum())
        groupee = auc(prediction[couvert], verite[couvert])
        par_fragment[frag] = {
            "carte": str(carte.relative_to(racine)),
            "auc_groupee": groupee,
            "encre_%": 100.0 * positifs / int(couvert.sum()),
            "tuiles_utilisables": len(lot),
            "tuiles_ecartees": (prediction.shape[0] // TUILE) * (prediction.shape[1] // TUILE) - len(lot),
            "tuiles": lot,
            "bootstrap": bootstrap_par_tuiles(lot, tirages=tirages),
            "destriage": destriage(prediction, verite, lot),
            "se_hanley_mcneil": se_hanley_mcneil(groupee, positifs,
                                                 int(couvert.sum()) - positifs),
        }

    aucs = {f: [t["auc"] for t in d["tuiles"]] for f, d in par_fragment.items()}
    toutes = [t for d in par_fragment.values() for t in d["tuiles"]]
    groupees = [d["auc_groupee"] for d in par_fragment.values()]
    ecart_observe = (max(groupees) - min(groupees)) if len(groupees) >= 2 else 0.0
    var = decomposer(aucs)
    sigma_intra = var.get("ecart_type_intra", 0.0) if var.get("exploitable") else 0.0
    return {
        "tuile_px": TUILE,
        "minimum_positifs": MINIMUM_POSITIFS,
        "fragments": par_fragment,
        "variance": var,
        "correlation_auc_densite": correlation([t["encre_%"] for t in toutes],
                                               [t["auc"] for t in toutes]),
        "tuiles_totales": len(toutes),
        # ⚠⚠ Une tuile sous 0,5 n'est pas « du bruit autour du hasard » : c'est le modele
        # qui range l'encre SOUS le papyrus vierge, donc un signal reel a l'envers. Compte
        # a part parce que la moyenne le noie.
        "tuiles_sous_le_hasard": sum(1 for t in toutes if t["auc"] < 0.5),
        "auc_de_tuile_minimale": min((t["auc"] for t in toutes), default=float("nan")),
        "auc_de_tuile_maximale": max((t["auc"] for t in toutes), default=float("nan")),
        "tuiles_pour_distinguer": tuiles_pour_distinguer(ecart_observe, sigma_intra)
        if ecart_observe > 0 and sigma_intra > 0 else 0,
        "ecart_observe": ecart_observe,
        # ⚠⚠ Deux ecarts de reference, parce que le nombre qui sert n'est pas celui de
        # NOTRE ecart mais celui qu'une campagne FUTURE voudra etablir. Ecrits ici plutot
        # que recalcules dans un document : j'ai publie « 63 » une premiere fois, valeur
        # juste pour un ecart-type de 0,2 et fausse pour le notre, qui vaut 0,2243.
        "tuiles_pour_un_ecart_de_0_05": tuiles_pour_distinguer(0.05, sigma_intra),
        "tuiles_pour_un_ecart_de_0_10": tuiles_pour_distinguer(0.10, sigma_intra),
    }


def se_chevauchent(a: dict, b: dict) -> bool:
    """Deux intervalles de confiance se recouvrent-ils ?

    ⚠ C'est un test FAIBLE, et c'est voulu : deux intervalles qui se recouvrent ne prouvent
    pas l'égalité, ils prouvent seulement que la différence n'est pas établie. Dire l'un
    pour l'autre serait exactement la faute que ce dépôt appelle « une vérification
    satisfaite pour la mauvaise raison ».
    """
    if not (a.get("exploitable") and b.get("exploitable")):
        return False
    return a["ic_bas"] <= b["ic_haut"] and b["ic_bas"] <= a["ic_haut"]


def rapporter(m: dict) -> None:
    """La sortie lisible, avec le verdict écrit en toutes lettres."""
    print(f"tuiles de {m['tuile_px']} px, {m['tuiles_totales']} utilisables au total\n")
    print(f"{'fragment':10} {'AUC groupee':>12} {'moy. tuiles':>12} "
          f"{'IC 95 % (bootstrap par tuiles)':>32} {'tuiles':>7}")
    for frag, d in m["fragments"].items():
        b = d["bootstrap"]
        if not b.get("exploitable"):
            print(f"{frag:10} {d['auc_groupee']:12.3f} {'—':>12} "
                  f"{'pas assez de tuiles':>32} {b['tuiles']:7d}")
            continue
        ic = f"[{b['ic_bas']:.3f} ; {b['ic_haut']:.3f}]"
        print(f"{frag:10} {d['auc_groupee']:12.3f} {b['moyenne']:12.3f} {ic:>32} "
              f"{b['tuiles']:7d}")

    v = m["variance"]
    print()
    if v.get("exploitable"):
        print(f"  ecart-type INTRA fragment (tuile a tuile)  {v['ecart_type_intra']:.4f}")
        print(f"  ecart-type INTER fragments                 {v['ecart_type_inter']:.4f}")
        print(f"  part attribuable au fragment (ICC)         {v['icc']:.3f}")
    print(f"  correlation AUC de tuile / densite d'encre  {m['correlation_auc_densite']:+.3f}")
    print(f"  tuiles SOUS le hasard (AUC < 0,5)          "
          f"{m['tuiles_sous_le_hasard']} sur {m['tuiles_totales']}, "
          f"la plus basse a {m['auc_de_tuile_minimale']:.3f}")

    print()
    print("  ce que coute un decalage de niveau d'une tuile a l'autre "
          "(memes pixels, rangs alignes par tuile) :")
    for frag, d in m["fragments"].items():
        s_ = d.get("destriage", {})
        if s_.get("exploitable"):
            print(f"    {frag:8} {s_['auc_brute']:.3f} -> {s_['auc_alignee']:.3f}  "
                  f"({s_['gain']:+.3f} sur {s_['pixels']} px)")

    print()
    for frag, d in m["fragments"].items():
        b = d["bootstrap"]
        if b.get("exploitable"):
            print(f"  ⚠ {frag} : erreur-type par tuiles {b['erreur_type']:.4f}, "
                  f"par Hanley-McNeil {d['se_hanley_mcneil']:.5f} "
                  f"(soit {b['erreur_type'] / max(d['se_hanley_mcneil'], 1e-12):.0f}x plus etroite)")

    if m.get("tuiles_pour_distinguer"):
        print()
        print(f"  ⭐ pour etablir l'ecart observe de {m['ecart_observe']:.3f} d'AUC, il faudrait "
              f"{m['tuiles_pour_distinguer']} tuiles PAR fragment")
        print("     (minorant : la formule suppose des tuiles independantes, "
              "deux tuiles voisines ne le sont pas)")

    noms = list(m["fragments"])
    paires = [(a, b) for i, a in enumerate(noms) for b in noms[i + 1:]]
    chevauchent = [(a, b) for a, b in paires
                   if se_chevauchent(m["fragments"][a]["bootstrap"],
                                     m["fragments"][b]["bootstrap"])]
    print()
    print(f"  {len(chevauchent)} paire(s) sur {len(paires)} dont les intervalles se recouvrent"
          + (" : " + ", ".join(f"{a}/{b}" for a, b in chevauchent) if chevauchent else ""))


def verifier() -> int:
    """L'instrument est-il capable de rendre la mauvaise réponse ?"""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    rng = np.random.default_rng(7)

    # -- tuiles : une tuile d'une seule classe est ECARTEE, jamais comptee 0,5.
    pred = rng.random((512, 512)).astype(np.float32)
    ver = np.zeros((512, 512), dtype=bool)
    ver[:256, :256] = rng.random((256, 256)) < 0.3          # une seule tuile a deux classes
    lot = tuiles(pred, ver)
    v("une tuile sans encre est ecartee", len(lot) == 1, f"{len(lot)} tuiles")
    v("... et la tuile gardee est la bonne", lot and lot[0]["y"] == 0 and lot[0]["x"] == 0,
      str(lot[:1]))
    v("... et aucune AUC rendue n'est NaN", all(not math.isnan(t["auc"]) for t in lot))

    # ⚠⚠ LA SONDE QUI COMPTE : si les tuiles degenerees etaient comptees 0,5, le compte
    # monterait a 4 et trois valeurs identiques ecraseraient toute dispersion.
    v("... donc le compte ne peut pas etre gonfle par des tuiles vides", len(lot) != 4)

    # ⚠⚠ LE CONTROLE DU BUG REELLEMENT PAYE : un pixel non couvert vaut NaN, et `argsort`
    # le range EN TETE. Sans le masque de couverture, les NaN seraient les pixels les mieux
    # notes de la tuile, donc l'AUC monterait ou tomberait selon l'endroit ou le rendu a
    # eu des trous -- et rien n'aurait l'air faux.
    pred_nan = rng.random((256, 256)).astype(np.float64)
    ver_nan = rng.random((256, 256)) < 0.3
    sans_trou = tuiles(pred_nan, ver_nan)[0]["auc"]
    troue = pred_nan.copy()
    troue[ver_nan] = np.nan            # on troue exactement l'encre : le pire cas
    avec_trou = tuiles(troue, ver_nan)
    v("un pixel non couvert n'est pas classe comme le mieux note",
      not avec_trou or abs(avec_trou[0]["auc"] - 1.0) > 0.4,
      str(avec_trou[:1]))
    v("... et la tuile pleine reste mesurable", 0.4 < sans_trou < 0.6, f"{sans_trou:.3f}")

    # -- tuiles de bord : une carte non multiple de la tuile ne doit pas rendre de tuile courte.
    pred2 = rng.random((300, 300)).astype(np.float32)
    ver2 = rng.random((300, 300)) < 0.3
    v("une carte plus petite que deux tuiles n'en rend qu'une",
      len(tuiles(pred2, ver2)) == 1, str(len(tuiles(pred2, ver2))))

    # -- decomposer : deux groupes IDENTIQUES ne doivent rien attribuer au groupe.
    a = [0.60, 0.65, 0.70, 0.75]
    d_meme = decomposer({"x": a, "y": list(a)})
    v("deux groupes identiques donnent un ICC nul", d_meme["icc"] == 0.0, str(d_meme["icc"]))
    # -- et deux groupes bien separes doivent, eux, attribuer beaucoup.
    d_loin = decomposer({"x": [0.40, 0.41, 0.42, 0.43], "y": [0.80, 0.81, 0.82, 0.83]})
    v("deux groupes eloignes donnent un ICC eleve", d_loin["icc"] > 0.9, str(d_loin["icc"]))
    v("... et l'ICC est bien borne a 1", d_loin["icc"] <= 1.0, str(d_loin["icc"]))
    # ⚠ Le cas qui distingue l'ICC de la variance naive des moyennes : deux groupes tires
    # de la MEME loi tres dispersee. La variance des moyennes n'est pas nulle, l'ICC doit
    # rester bas parce que la dispersion intra explique deja tout.
    g = rng.normal(0.65, 0.12, 40)
    d_bruit = decomposer({"x": list(g[:20]), "y": list(g[20:])})
    v("deux moities d'un meme tirage donnent un ICC bas", d_bruit["icc"] < 0.2,
      str(d_bruit["icc"]))

    # -- destriage : un decalage FABRIQUE doit etre retrouve, et l'absence de decalage
    #    ne doit rien rendre. Les deux sens, sinon la fonction pourrait toujours dire oui.
    base = rng.random((512, 512))
    ver_d = rng.random((512, 512)) < 0.4
    base[ver_d] += 0.6                                   # l'encre note plus haut : signal reel
    lot_d = tuiles(base, ver_d)
    d_sans = destriage(base, ver_d, lot_d)
    v("sans decalage, aligner les rangs ne change presque rien",
      abs(d_sans["gain"]) < 0.02, f"{d_sans['gain']:+.4f}")
    biaise = base.copy()
    biaise[:256, :] += 3.0                               # une moitie travaille 3 crans plus haut
    d_avec = destriage(biaise, ver_d, tuiles(biaise, ver_d))
    v("un decalage par region abime l'AUC groupee", d_avec["auc_brute"] < d_sans["auc_brute"] - 0.05,
      f"{d_avec['auc_brute']:.3f} vs {d_sans['auc_brute']:.3f}")
    v("... et aligner les rangs par tuile le retire", d_avec["gain"] > 0.05,
      f"{d_avec['gain']:+.3f}")
    v("... jusqu'a retrouver l'AUC d'avant le decalage",
      abs(d_avec["auc_alignee"] - d_sans["auc_alignee"]) < 0.02,
      f"{d_avec['auc_alignee']:.3f} vs {d_sans['auc_alignee']:.3f}")
    v("un lot vide n'est pas exploitable", destriage(base, ver_d, [])["exploitable"] is False)

    # ⚠⚠⚠ LA SONDE QUI MANQUAIT, et sans elle le chiffre de tete de ce fichier n'etait
    # garde par rien : une premiere version calculait `var_inter = ms_inter / n0` sans
    # RETRANCHER le bruit intra, et la batterie passait au vert. Un ICC naif attribue au
    # groupe une part qui vaut 1/(1+n0) meme quand les groupes sont tires de la MEME loi.
    #
    # Le cas est algebrique, calcule a la main, donc il ne depend d'aucun tirage :
    #   x = [0, 2], y = [1, 3]  ->  MS_inter = 1, MS_intra = 2, n0 = 2
    #   correct : var_inter = max(1 - 2, 0) / 2 = 0        -> ICC = 0
    #   naif    : var_inter = 1 / 2 = 0,5                  -> ICC = 0,2
    d_borne = decomposer({"x": [0.0, 2.0], "y": [1.0, 3.0]})
    v("des groupes moins ecartes que leur propre bruit n'expliquent RIEN",
      d_borne["icc"] == 0.0, str(d_borne["icc"]))
    v("... et l'ecart-type inter est nul dans ce cas",
      d_borne["ecart_type_inter"] == 0.0, str(d_borne["ecart_type_inter"]))

    # Et la meme faute vue en moyenne sur des tirages nuls. Le seuil n'est pas choisi pour
    # que le tirage du jour passe : l'estimateur correct, ecrete a zero, vaut la MOITIE du
    # biais naif 1/(1+n0) (mesure : 0,0995 contre 0,2000 pour des groupes de 4). Le seuil
    # est le milieu des deux, donc les deux erreurs sont a egale distance.
    for taille in (4, 8):
        vals = []
        for _ in range(200):
            g = rng.normal(0.65, 0.15, 2 * taille)
            vals.append(decomposer({"x": list(g[:taille]), "y": list(g[taille:])})["icc"])
        moyen = sum(vals) / len(vals)
        v(f"sous l'hypothese nulle, l'ICC moyen reste sous le biais naif (groupes de {taille})",
          moyen < 0.75 / (1 + taille), f"{moyen:.4f} vs {0.75 / (1 + taille):.4f}")

    d_vide = decomposer({"x": [0.5]})
    v("un seul groupe n'est pas exploitable", d_vide["exploitable"] is False, str(d_vide))

    # -- bootstrap : l'intervalle doit ENCADRER la moyenne, et se resserrer avec n.
    petit = [{"auc": x} for x in rng.normal(0.7, 0.1, 8)]
    grand = [{"auc": x} for x in rng.normal(0.7, 0.1, 200)]
    bp, bg = bootstrap_par_tuiles(petit, 2000, 1), bootstrap_par_tuiles(grand, 2000, 1)
    v("l'intervalle encadre la moyenne",
      bp["ic_bas"] <= bp["moyenne"] <= bp["ic_haut"], str(bp))
    v("... et se resserre quand il y a plus de tuiles",
      (bg["ic_haut"] - bg["ic_bas"]) < (bp["ic_haut"] - bp["ic_bas"]),
      f"{bg['ic_haut'] - bg['ic_bas']:.4f} vs {bp['ic_haut'] - bp['ic_bas']:.4f}")
    v("... et il est reproductible a graine egale",
      bootstrap_par_tuiles(petit, 2000, 1) == bp)
    v("une tuile unique n'est pas exploitable",
      bootstrap_par_tuiles([{"auc": 0.7}], 500, 0)["exploitable"] is False)

    # -- Hanley-McNeil : le point du fichier est qu'elle est BEAUCOUP trop etroite ici.
    se_pix = se_hanley_mcneil(0.75, 300_000, 700_000)
    v("la formule usuelle rend une erreur-type minuscule sur un million de pixels",
      se_pix < 0.002, f"{se_pix:.5f}")
    v("... et elle grandit quand l'echantillon rapetisse",
      se_hanley_mcneil(0.75, 300, 700) > 10 * se_pix)
    v("... et elle est indefinie sans les deux classes",
      math.isnan(se_hanley_mcneil(0.75, 0, 700)))

    # -- se_chevauchent : dans les deux sens.
    x = {"exploitable": True, "ic_bas": 0.60, "ic_haut": 0.70}
    y = {"exploitable": True, "ic_bas": 0.65, "ic_haut": 0.80}
    z = {"exploitable": True, "ic_bas": 0.90, "ic_haut": 0.95}
    v("deux intervalles qui se touchent sont dits recouvrants", se_chevauchent(x, y))
    v("deux intervalles disjoints ne le sont pas", not se_chevauchent(x, z))
    v("... et la relation est symetrique",
      se_chevauchent(y, x) and not se_chevauchent(z, x))
    v("un intervalle inexploitable ne recouvre rien",
      not se_chevauchent({"exploitable": False}, y))

    # -- quantile normal : contre trois valeurs connues, sinon la formule est une croyance.
    v("le quantile normal retrouve 1,95996 a 95 %",
      abs(quantile_normale(0.975) - 1.959964) < 1e-4, f"{quantile_normale(0.975):.6f}")
    v("... 0,84162 pour une puissance de 80 %",
      abs(quantile_normale(0.80) - 0.841621) < 1e-4, f"{quantile_normale(0.80):.6f}")
    v("... 2,57583 a 99 %",
      abs(quantile_normale(0.995) - 2.575829) < 1e-4, f"{quantile_normale(0.995):.6f}")
    v("... et il est antisymetrique",
      abs(quantile_normale(0.2) + quantile_normale(0.8)) < 1e-6)
    v("... et refuse une probabilite hors bornes", math.isnan(quantile_normale(1.0)))

    # -- taille d'echantillon : le sens de variation, et le cas connu.
    v("un ecart deux fois plus petit coute quatre fois plus de tuiles",
      tuiles_pour_distinguer(0.05, 0.2) == 4 * tuiles_pour_distinguer(0.10, 0.2) or
      abs(tuiles_pour_distinguer(0.05, 0.2) - 4 * tuiles_pour_distinguer(0.10, 0.2)) <= 2,
      f"{tuiles_pour_distinguer(0.05, 0.2)} vs {tuiles_pour_distinguer(0.10, 0.2)}")
    v("... et un ecart nul n'est jamais etablissable",
      tuiles_pour_distinguer(0.0, 0.2) == 0)
    v("... et une dispersion nulle non plus", tuiles_pour_distinguer(0.1, 0.0) == 0)
    # Valeur de reference calculee a la main : 2 * ((1,959964 + 0,841621) * 0,2 / 0,1)^2
    # = 2 * (5,60324)^2 * ... soit 63 tuiles. Ecrire le nombre attendu ailleurs que dans
    # le code teste est ce qui rend le controle capable d'echouer.
    v("... et il vaut 63 pour sigma 0,2 et un ecart de 0,1",
      tuiles_pour_distinguer(0.1, 0.2) == 63, str(tuiles_pour_distinguer(0.1, 0.2)))

    # -- correlation : signe et cas degeneres.
    v("la correlation retrouve une pente positive",
      correlation([1, 2, 3, 4], [2, 4, 6, 8]) > 0.99)
    v("... et une pente negative", correlation([1, 2, 3, 4], [8, 6, 4, 2]) < -0.99)
    v("... et refuse un echantillon trop court",
      math.isnan(correlation([1, 2], [3, 4])))

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--tirages", type=int, default=2000)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    m = mesurer(tirages=a.tirages)
    if not m["fragments"]:
        print("aucune carte de fragment rendue — rien a mesurer", file=sys.stderr)
        return 2
    rapporter(m)
    if a.json:
        # ⚠ Les tuiles individuelles sont gardees : c'est le seul moyen de refaire la
        # decomposition autrement sans relancer une lecture d'un giga-octet de cartes.
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n→ {a.json.relative_to(RACINE) if a.json.is_absolute() else a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
