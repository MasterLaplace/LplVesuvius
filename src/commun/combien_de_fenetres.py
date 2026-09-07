#!/usr/bin/env python3
"""Combien de fenetres faut-il pour que la carte des treize rouleaux DECIDE quelque chose ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA QUESTION QUI PRECEDE LA CAMPAGNE. `16` classe les
treize rouleaux du Grand Prize par leur part de fenetres indissociables et en tire une
designation. `33` mesure l'incertitude de ce classement et l'annule : **0 rouleau sur 13**
separe du temoin apres Holm, **0 paire sur 78** separee. Et `31` inscrit au calendrier
« mesurer la part comprimee rouleau par rouleau, a 50 fenetres minimum ».

⭐⭐ MAIS 50 EST LE CHIFFRE POUR SEPARER UN ROULEAU DU TEMOIN, et ce n'est PAS la decision dont
le prix a besoin. Le prix demande de choisir **sur lequel des treize** depenser six mois : il
faut donc separer les rouleaux **ENTRE EUX**, ce qui est une question strictement plus dure —
deux estimations incertaines au lieu d'une contre un quasi-zero — et personne n'a calcule ce
qu'elle coute.

⚠⚠ ET LE PRIX DU MULTIPLE EST LA VRAIE MORSURE. Comparer 78 paires au seuil de 5 % produit un
« significatif » par pur hasard ; `33` l'ecrit deja pour les treize. Corrige par Holm, le seuil
de la plus petite p-valeur tombe a 0,05/78, et l'effectif necessaire explose. Ce fichier chiffre
les deux, parce que publier le nominal seul ferait croire la campagne quatre fois moins chere
qu'elle n'est.

⚠ CE FICHIER NE MESURE RIEN SUR LES ROULEAUX. Il relit les parts deja publiees et repond a une
question de PUISSANCE : a quel effectif la question deviendrait decidable. Une campagne lancee
sans ce chiffre est une campagne dont on ne sait pas si elle peut conclure.

Usage :
    uv run python src/commun/combien_de_fenetres.py --verifier
    uv run python src/commun/combien_de_fenetres.py --json docs/mesures/combien_de_fenetres.json
"""

from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from incertitude_carte import charger  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
# ⚠ Le dossier des parts publiees, nomme ici plutot que passe : `incertitude_carte` le prend
# en argument de ligne de commande, donc il n'existe pas comme constante importable.
CARTE = RACINE / "docs" / "carte_separabilite"
# ⚠ Une ECHELLE et pas une recherche fine : ce fichier repond a « quel ordre de grandeur »,
# parce que c'est la forme de la reponse dont une decision de budget a besoin. Pretendre a
# l'effectif exact demanderait une precision que le modele binomial ne porte pas de toute facon.
ECHELLE = (25, 50, 100, 200, 400)
# ⚠⚠ L'ECHELLE S'ARRETE A 400 PARCE QUE LA TABLE DE REJET EST EN O(n²) APPELS DE FISHER, et
# qu'aller plus haut couterait des dizaines de minutes pour rendre le meme mot : « hors de
# portee ». Ce qui manquerait alors est la DISTANCE, et elle est fournie autrement — par une
# borne analytique dont on sait le sens de l'erreur.
CIBLE = 0.80
ALPHA = 0.05


@lru_cache(maxsize=32)
def table_de_rejet(n: int, alpha: float) -> tuple:
    """La matrice des (k1, k2) que Fisher rejetterait, calculee UNE fois par (n, alpha).

    ⚠⚠ C'EST CE QUI REND LE BALAYAGE FAISABLE. La p-valeur de Fisher ne depend que de
    (k1, k2, n) — jamais des proportions supposees — donc la table se calcule une fois et sert
    les 78 paires. Sans ce cache, chaque paire refarait (n+1)² tests exacts et le fichier
    mettrait des heures a rendre un chiffre d'ordre de grandeur.
    """
    from scipy.stats import fisher_exact  # noqa: PLC0415

    r = np.zeros((n + 1, n + 1), dtype=bool)
    for k1 in range(n + 1):
        for k2 in range(k1, n + 1):
            p = fisher_exact([[k1, n - k1], [k2, n - k2]], alternative="two-sided").pvalue
            r[k1, k2] = r[k2, k1] = p < alpha
    return tuple(map(tuple, r))


def puissance_a(p1: float, p2: float, n: int, alpha: float = ALPHA) -> float:
    """La puissance EXACTE de Fisher a n fenetres par rouleau, pour deux parts supposees.

    ⚠ Exacte et pas approchee : sur des parts de quelques pour-cent l'approximation normale
    surestime la puissance, donc elle promettrait une campagne moins chere que la vraie. C'est
    la meme reserve que `incertitude_carte.puissance_exacte` ecrit deja, et ce fichier la tient
    en reutilisant la meme definition — celle-ci ne differe que par le cache.
    """
    from scipy.stats import binom  # noqa: PLC0415

    r = np.array(table_de_rejet(int(n), float(alpha)))
    k = np.arange(n + 1)
    poids = np.outer(binom.pmf(k, n, p1), binom.pmf(k, n, p2))
    return float(poids[r].sum())


def fenetres_pour(p1: float, p2: float, alpha: float = ALPHA, cible: float = CIBLE,
                  echelle=ECHELLE) -> dict:
    """Le premier barreau de l'echelle qui atteint la puissance visee, ou None.

    ⚠⚠ RENDRE None PLUTOT QU'UN NOMBRE INVENTE. Une paire dont les parts sont trop proches
    peut demander un effectif que ce fichier ne balaie pas ; extrapoler donnerait un chiffre
    de budget faux dans le sens qui coute cher. « Au-dela de l'echelle » est une reponse.
    """
    for n in echelle:
        p = puissance_a(p1, p2, int(n), alpha)
        if p >= cible:
            return dict(fenetres=int(n), puissance=round(p, 3))
    return dict(fenetres=None, puissance=round(puissance_a(p1, p2, int(echelle[-1]), alpha), 3))


def fenetres_approchees(p1: float, p2: float, alpha: float = ALPHA,
                        cible: float = CIBLE) -> int:
    """Une BORNE BASSE sur l'effectif necessaire, par l'approximation normale.

    ⚠⚠⚠ POURQUOI UNE BORNE ET PAS UNE ESTIMATION, et le sens de l'erreur est ce qui la rend
    utilisable. `incertitude_carte` ecrit deja que sur des parts de quelques pour-cent
    l'approximation normale **surestime la puissance** ; a puissance visee fixee, elle
    **sous-estime** donc l'effectif. Le nombre rendu ici est ce qu'il faudrait AU MINIMUM, et
    le vrai cout est plus grand — c'est le sens d'erreur qu'on veut quand on chiffre un budget.

    ⚠ Elle existe parce que l'echelle exacte s'arrete a quelques centaines de fenetres : sans
    elle, une paire hors de portee ne rendrait que le mot « hors de portee », sans dire si elle
    est a deux fois ou a trois cents fois le budget actuel. Les deux appellent des decisions
    differentes.
    """
    from scipy.stats import norm  # noqa: PLC0415

    d = abs(float(p1) - float(p2))
    if d < 1e-12:
        return -1
    pm = (float(p1) + float(p2)) / 2.0
    za = float(norm.ppf(1.0 - alpha / 2.0))
    zb = float(norm.ppf(cible))
    num = za * (2.0 * pm * (1.0 - pm)) ** 0.5 + zb * (
        p1 * (1.0 - p1) + p2 * (1.0 - p2)) ** 0.5
    return int(round(num * num / (d * d)))


def mesurer(dossier: Path | None = None, echelle=ECHELLE, cible: float = CIBLE) -> dict:
    """Ce que separer les treize couterait, en fenetres par rouleau."""
    temoin, rouleaux = charger(CARTE if dossier is None else dossier)
    rouleaux = sorted(rouleaux, key=lambda x: x["part"])
    n_paires = len(rouleaux) * (len(rouleaux) - 1) // 2
    # ⚠⚠⚠ LE SEUIL CORRIGE EST CELUI DE LA PLUS PETITE p-VALEUR SOUS HOLM : alpha / m. C'est la
    # borne la plus dure, donc l'effectif qu'elle demande est celui qu'il faut prevoir. Publier
    # le nominal seul ferait croire la campagne bien moins chere qu'elle n'est.
    alpha_holm = ALPHA / n_paires

    paires = []
    for i, a in enumerate(rouleaux):
        for b in rouleaux[i + 1:]:
            nom = puissance_a(a["part"], b["part"], 50)
            paires.append(dict(
                a=a["rouleau"], b=b["rouleau"], part_a=round(a["part"], 4),
                part_b=round(b["part"], 4), ecart=round(abs(a["part"] - b["part"]), 4),
                nominal=fenetres_pour(a["part"], b["part"], ALPHA, cible, echelle),
                holm=fenetres_pour(a["part"], b["part"], alpha_holm, cible, echelle),
                borne_basse_holm=fenetres_approchees(a["part"], b["part"], alpha_holm, cible),
                puissance_a_50=round(nom, 3)))

    # ⚠ ET LA COMPARAISON AU TEMOIN, gardee parce que c'est le chiffre que `31` inscrit au
    # calendrier : elle est BEAUCOUP moins chere, et c'est justement le piege — repondre a la
    # question facile ne repond pas a celle qui decide du rouleau.
    au_temoin = [dict(rouleau=x["rouleau"], part=round(x["part"], 4),
                      nominal=fenetres_pour(x["part"], temoin["part"], ALPHA, cible, echelle),
                      holm=fenetres_pour(x["part"], temoin["part"],
                                         ALPHA / len(rouleaux), cible, echelle))
                 for x in rouleaux]

    def au_plus(cle: str, budget: int) -> int:
        return sum(1 for p in paires
                   if p[cle]["fenetres"] is not None and p[cle]["fenetres"] <= budget)

    # ⭐⭐⭐ LA PAIRE QUI DECIDE DU ROULEAU : les deux mieux classes. C'est elle qu'il faut
    # separer pour choisir ou depenser six mois, et c'est la plus chere de toutes parce que
    # leurs parts sont les plus proches.
    decisive = next(p for p in paires
                    if p["a"] == rouleaux[0]["rouleau"] and p["b"] == rouleaux[1]["rouleau"])
    return dict(
        rouleaux=len(rouleaux), paires=n_paires, cible=cible, alpha=ALPHA,
        alpha_holm=alpha_holm, echelle=list(echelle),
        temoin=dict(rouleau=temoin["rouleau"], part=round(temoin["part"], 4),
                    fenetres=temoin["n"]),
        fenetres_actuelles={x["rouleau"]: x["n"] for x in rouleaux},
        fenetres_actuelles_total=sum(x["n"] for x in rouleaux),
        paire_decisive=decisive, paires_detail=paires, au_temoin=au_temoin,
        # ⚠⚠ COMBIEN DE PAIRES UN BUDGET ACHETE, aux deux seuils. C'est la forme sous laquelle
        # une decision se prend : pas « quel effectif », mais « ce que cet effectif rend ».
        paires_separees_par_budget={
            str(n): dict(nominal=au_plus("nominal", n), holm=au_plus("holm", n))
            for n in echelle},
        # ⭐⭐⭐ LE VERDICT : la paire qui decide est-elle atteignable dans l'echelle balayee ?
        la_paire_decisive_est_atteignable=bool(decisive["holm"]["fenetres"] is not None),
        cout_total_fenetres=(decisive["holm"]["fenetres"] * len(rouleaux)
                             if decisive["holm"]["fenetres"] else None),
        # ⭐⭐⭐ ET LA DISTANCE, quand l'echelle exacte ne suffit pas : ce qu'il faudrait AU
        # MINIMUM pour la paire qui decide, et ce que ca fait pour les treize. Le rapport au
        # budget actuel est le nombre qui rend la decision evidente.
        borne_basse_decisive=decisive["borne_basse_holm"],
        borne_basse_totale=decisive["borne_basse_holm"] * len(rouleaux),
        facteur_sur_lexistant=round(
            decisive["borne_basse_holm"] * len(rouleaux)
            / max(sum(x["n"] for x in rouleaux), 1), 1))


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ LA TABLE DE REJET EST SYMETRIQUE ET NE REJETTE PAS LA DIAGONALE : deux comptes egaux
    # ne peuvent pas etre declares differents, quel que soit n. Si c'etait faux, toute la
    # puissance serait surestimee du poids de la diagonale, qui est le cas le plus probable.
    r = np.array(table_de_rejet(20, 0.05))
    v("la table de rejet est symétrique", bool((r == r.T).all()))
    v("... et elle ne rejette jamais deux comptes ÉGAUX",
      not bool(np.diagonal(r).any()))
    v("... elle rejette bien les extrêmes opposés", bool(r[0, 20]))
    # ⚠⚠⚠ LA PUISSANCE EST BORNEE ET MONOTONE : elle croît avec n, et deux parts IDENTIQUES ne
    # donnent jamais plus que le seuil — sinon le test se tromperait plus souvent qu'annoncé.
    v("la puissance croît avec l'effectif",
      puissance_a(0.05, 0.25, 25) < puissance_a(0.05, 0.25, 50)
      < puissance_a(0.05, 0.25, 100),
      f"{puissance_a(0.05, 0.25, 25):.3f} < {puissance_a(0.05, 0.25, 50):.3f} < "
      f"{puissance_a(0.05, 0.25, 100):.3f}")
    v("... deux parts identiques ne dépassent jamais le seuil de test",
      puissance_a(0.15, 0.15, 50, 0.05) <= 0.05,
      f"{puissance_a(0.15, 0.15, 50, 0.05):.4f}")
    v("... et un écart plus grand demande moins de fenêtres",
      puissance_a(0.05, 0.30, 50) > puissance_a(0.05, 0.10, 50))
    # ⚠⚠ UN SEUIL PLUS DUR DEMANDE PLUS DE FENETRES : c'est toute la raison de publier Holm à
    # côté du nominal, donc le contrôle porte dessus.
    v("un seuil corrigé demande plus de fenêtres qu'un seuil nominal",
      puissance_a(0.05, 0.25, 50, 0.05) > puissance_a(0.05, 0.25, 50, 0.05 / 78))
    # ⚠ « AU-DELA DE L'ECHELLE » EST UNE REPONSE, jamais un nombre extrapolé.
    v("une paire hors de portée rend None, pas un nombre inventé",
      fenetres_pour(0.10, 0.1001, echelle=(25, 50))["fenetres"] is None)
    v("... et elle publie quand même la puissance atteinte au dernier barreau",
      fenetres_pour(0.10, 0.1001, echelle=(25, 50))["puissance"] is not None)

    r2 = mesurer(echelle=(25, 50, 100))
    v("la mesure tourne de bout en bout sur les parts publiées",
      r2["rouleaux"] == 13 and r2["paires"] == 78,
      f"{r2['rouleaux']} rouleaux · {r2['paires']} paires")
    # ⚠⚠⚠ LA PAIRE DECISIVE EST CELLE DES DEUX MIEUX CLASSES, pas la plus facile : c'est elle
    # qui decide ou depenser six mois, et c'est la plus chere. Prendre la plus facile serait
    # repondre a une question que personne ne pose.
    parts = sorted(r2["fenetres_actuelles"], key=lambda k: r2["paires_detail"][0]["part_a"])
    v("... la paire décisive est celle des deux MIEUX classés",
      r2["paire_decisive"]["part_a"] <= r2["paire_decisive"]["part_b"]
      and all(r2["paire_decisive"]["part_a"] <= p["part_a"] for p in r2["paires_detail"]),
      f"{r2['paire_decisive']['a']} ({r2['paire_decisive']['part_a']}) contre "
      f"{r2['paire_decisive']['b']} ({r2['paire_decisive']['part_b']})")
    # ⚠⚠ UN BUDGET PLUS GRAND N'ACHETE JAMAIS MOINS DE PAIRES, et le nominal jamais moins que
    # Holm : deux monotonies qui, si elles cassaient, diraient que le compte ne compte pas ce
    # qu'il annonce.
    budgets = sorted(int(k) for k in r2["paires_separees_par_budget"])
    v("... un budget plus grand n'achète jamais moins de paires",
      all(r2["paires_separees_par_budget"][str(a)]["nominal"]
          <= r2["paires_separees_par_budget"][str(b)]["nominal"]
          for a, b in zip(budgets, budgets[1:])),
      str({k: v_["nominal"] for k, v_ in r2["paires_separees_par_budget"].items()}))
    v("... et le seuil corrigé n'achète jamais plus que le nominal",
      all(x["holm"] <= x["nominal"] for x in r2["paires_separees_par_budget"].values()),
      str({k: (v_["nominal"], v_["holm"])
           for k, v_ in r2["paires_separees_par_budget"].items()}))
    # ⚠⚠⚠ LA BORNE ANALYTIQUE EST BASSE, ET SON SENS D'ERREUR EST CE QUI LA REND UTILISABLE :
    # l'approximation normale surestime la puissance, donc elle sous-estime l'effectif. Le
    # contrôle l'épingle en la confrontant à l'échelle EXACTE là où celle-ci conclut.
    # ⚠ Les paires du corpus ne sont PAS résolues par l'échelle courte, donc les confronter
    # ici rendrait un contrôle satisfait par l'ensemble vide — la faute nº1 de ce dépôt. La
    # confrontation se fait sur des écarts assez larges pour que l'échelle exacte conclue.
    duos = [(0.05, 0.40), (0.05, 0.35), (0.10, 0.45)]
    exacts = [(fenetres_approchees(a, b), fenetres_pour(a, b, ALPHA, CIBLE, (25, 50, 100, 200)))
              for a, b in duos]
    exacts = [(bb, x["fenetres"]) for bb, x in exacts if x["fenetres"] is not None]
    v("la borne analytique ne dépasse jamais l'effectif exact quand celui-ci est connu",
      bool(exacts) and all(bb <= n for bb, n in exacts),
      f"{len(exacts)} paires résolues · {exacts}")
    v("... elle croît quand l'écart des parts diminue",
      fenetres_approchees(0.05, 0.25) < fenetres_approchees(0.05, 0.10)
      < fenetres_approchees(0.05, 0.06),
      f"{fenetres_approchees(0.05, 0.25)} < {fenetres_approchees(0.05, 0.10)} < "
      f"{fenetres_approchees(0.05, 0.06)}")
    v("... et un seuil corrigé en demande plus qu'un seuil nominal",
      fenetres_approchees(0.05, 0.10, 0.05 / 78) > fenetres_approchees(0.05, 0.10, 0.05))
    v("... deux parts identiques rendent -1, jamais une division par zéro",
      fenetres_approchees(0.1, 0.1) == -1)
    v("... le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(r2), str))
    souci = None
    try:
        afficher(r2)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("... et l'affichage tourne sur ce résultat", souci is None, str(souci))
    del parts

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible : ce qu'un budget achète, et ce que la décision coûte."""
    def dire(x: dict) -> str:
        return (f"{x['fenetres']}" if x["fenetres"] is not None
                else f"> {r['echelle'][-1]} (puissance {x['puissance']:.2f})")

    print(f"{r['rouleaux']} rouleaux · {r['paires']} paires · cible {r['cible']:.0%} de "
          f"puissance · seuil nominal {r['alpha']}, corrigé {r['alpha_holm']:.2e}")
    print(f"aujourd'hui : {r['fenetres_actuelles_total']} fenêtres au total, "
          f"{min(r['fenetres_actuelles'].values())} à {max(r['fenetres_actuelles'].values())} "
          "par rouleau")
    print()
    print("ce qu'un budget par rouleau achète, en paires séparées sur "
          f"{r['paires']} :")
    print(f"{'fenêtres':>10} {'nominal':>9} {'après Holm':>12}")
    for n, x in r["paires_separees_par_budget"].items():
        print(f"{n:>10} {x['nominal']:>9} {x['holm']:>12}")
    print()
    d = r["paire_decisive"]
    print(f"⭐ la paire qui DÉCIDE du rouleau — les deux mieux classés :")
    print(f"   {d['a']} ({d['part_a']:.1%}) contre {d['b']} ({d['part_b']:.1%}) · "
          f"écart {d['ecart']:.1%}")
    print(f"   nominal : {dire(d['nominal'])} fenêtres · après Holm : {dire(d['holm'])}")
    print(f"   puissance à 50 fenêtres, le chiffre du calendrier : {d['puissance_a_50']:.1%}")
    print(f"   ⭐ borne BASSE sur l'effectif nécessaire : {r['borne_basse_decisive']} fenêtres "
          f"par rouleau, soit {r['borne_basse_totale']} au total — "
          f"{r['facteur_sur_lexistant']}× le budget actuel")
    print()
    print("⚠ à comparer : séparer un rouleau du TÉMOIN, la question facile")
    for x in r["au_temoin"][:3]:
        print(f"   {x['rouleau']:>12} ({x['part']:.1%}) : nominal {dire(x['nominal'])} · "
              f"Holm {dire(x['holm'])}")
    print()
    if r["la_paire_decisive_est_atteignable"]:
        print(f"→ ⭐ la décision est atteignable : {d['holm']['fenetres']} fenêtres par "
              f"rouleau, soit {r['cout_total_fenetres']} au total")
    else:
        print(f"→ ⛔ LA PAIRE QUI DÉCIDE N'EST PAS ATTEIGNABLE dans l'échelle balayée "
              f"(jusqu'à {r['echelle'][-1]} fenêtres par rouleau) : au seuil corrigé, sa "
              f"puissance y plafonne à {d['holm']['puissance']:.1%}")
        print(f"   → il en faudrait AU MOINS {r['borne_basse_decisive']} par rouleau "
              f"({r['borne_basse_totale']} au total, {r['facteur_sur_lexistant']}× l'existant)")
        print("   → choisir le rouleau par sa part comprimée n'est donc PAS une procédure de "
              "décision disponible à ce prix")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--carte", type=Path, default=None)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(dossier=a.carte)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
