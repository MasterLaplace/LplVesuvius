#!/usr/bin/env python3
"""Le classement des treize rouleaux du prix est-il RESOLU par ses propres donnees ?

⚠⚠ Pourquoi cette verification existe. `16` classe les treize rouleaux du Grand Prize sur
la **queue** de leur separabilite -- la part de fenetres ou feuille et interstice ne se
separent pas -- et designe `PHerc0358` (4 %) comme le premier a attaquer. Le temoin,
`PHerc0139`, est a 0 %.

Ce que `16` ne dit pas : ces parts sont des proportions sur **15 a 35 fenetres**. Une part
de 4 % est alors 1 fenetre sur 28, et une part de 24 % est 5 sur 21. Un classement lu sur
des comptes aussi petits peut n'etre que du bruit d'echantillonnage -- et c'est exactement
la forme d'erreur que ce depot a deja payee ailleurs.

Ce script ne remesure rien : il relit les artefacts versionnes et repond a trois questions
que le document laisse ouvertes.

  1. Quel est l'intervalle de confiance exact de chaque part ?
  2. Un rouleau est-il **distinguable du temoin** ? (Fisher exact, correction de Holm sur
     les treize comparaisons -- sans elle, treize essais rendent un « significatif »
     attendu par pur hasard.)
  3. Le **classement** est-il resolu ? Sur les 78 paires possibles, combien sont
     reellement separees ?

⚠ Le test est unilateral -- on demande « ce rouleau a-t-il PLUS de fenetres
indissociables que le temoin », pas « differe-t-il ». La question du document a un sens,
et un test bilateral depenserait de la puissance a exclure une direction qu'on ne
soupconne pas.

⚠ La part est une fraction de **fenetres sondees**, pas de surface de recto. Elle ne se
compare donc PAS directement au « less than 10 % » que le prix tolere pour les patches
sautes : ce sont deux grandeurs differentes, et les confondre serait la faute que ce
depot traque. Le script imprime la confrontation, en disant qu'elle est indicative.

Usage :
    uv run python analysis/src/incertitude_carte.py [--json docs/incertitude_carte.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
TOLERANCE_PRIX = 0.10


def clopper_pearson(succes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    """Intervalle exact d'une proportion binomiale.

    ⚠ Exact et non normal : sur 1 succes en 28 essais l'approximation normale rend une
    borne basse negative, c'est-a-dire hors du domaine de la grandeur qu'elle encadre.
    """
    from scipy.stats import beta
    bas = 0.0 if succes == 0 else float(beta.ppf(alpha / 2, succes, total - succes + 1))
    haut = 1.0 if succes == total else float(beta.ppf(1 - alpha / 2, succes + 1, total - succes))
    return bas, haut


def holm(pvaleurs: list[float]) -> list[float]:
    """Correction de Holm-Bonferroni : moins conservatrice que Bonferroni, meme garantie."""
    n = len(pvaleurs)
    ordre = sorted(range(n), key=lambda i: pvaleurs[i])
    ajustees = [0.0] * n
    courant = 0.0
    for rang, i in enumerate(ordre):
        courant = max(courant, min(1.0, (n - rang) * pvaleurs[i]))
        ajustees[i] = courant
    return ajustees


def charger(dossier: Path) -> tuple[dict, list[dict]]:
    temoin, rouleaux = None, []
    for f in sorted(dossier.glob("*.json")):
        d = json.loads(f.read_text())
        nom = f.stem
        # Le compte est RECONSTRUIT depuis la part et le nombre de fenetres : l'artefact
        # n'enregistre pas le compte brut. L'arrondi est exact tant que n < 1/eps.
        n = int(d["chunks"])
        k = round(d["part_sous_1"] * n)
        ligne = {"rouleau": nom.replace("_TEMOIN_", ""), "n": n, "k": k,
                 "part": d["part_sous_1"], "d_prime_median": d["d_prime_median"],
                 "d_prime_min": d["d_prime_min"], "temoin": nom.startswith("_TEMOIN_")}
        if ligne["temoin"]:
            temoin = ligne
        else:
            rouleaux.append(ligne)
    return temoin, rouleaux


def puissance_exacte(p1: float, p2: float, n: int, alpha: float = 0.05) -> float:
    """Puissance EXACTE de Fisher a n fenetres par rouleau, par enumeration.

    ⚠ Pas l'approximation normale : sur des parts de quelques pour-cent avec n < 50 elle
    surestime la puissance, donc elle promettrait une campagne moins chere que la vraie.
    On enumere les (n+1)² tables possibles, chacune ponderee par sa probabilite
    binomiale, et on somme celles que le test rejetterait.
    """
    import numpy as np
    from scipy.stats import binom, fisher_exact

    k = np.arange(n + 1)
    poids = np.outer(binom.pmf(k, n, p1), binom.pmf(k, n, p2))
    puissance = 0.0
    for k1 in k:
        for k2 in k:
            w = poids[k1, k2]
            if w < 1e-9:
                continue
            if fisher_exact([[int(k1), n - int(k1)], [int(k2), n - int(k2)]],
                            alternative="two-sided").pvalue < alpha:
                puissance += w
    return float(puissance)


def verifier() -> int:
    """Temoin hors ligne de l'appareil statistique de ce fichier.

    ⚠ Il ne verifie PAS le resultat -- un temoin qui rejouerait la mesure ne pourrait que
    confirmer ce que le code fait. Il verifie les proprietes que les fonctions doivent
    avoir et qu'une erreur d'implementation casserait :

      - Clopper-Pearson sur des cas dont la forme fermee est connue ;
      - Holm sur un exemple ou l'ordre des ajustements est calculable a la main ;
      - ⭐ et la propriete qui rend le tableau de puissance lisible : **sous l'hypothese
        nulle, la puissance doit tomber au niveau du test**. Une fonction de puissance qui
        rendrait 80 % quand les deux parts sont EGALES produirait un tableau entierement
        plausible et entierement faux.
    """
    from scipy.stats import fisher_exact

    echecs, controles = 0, 0

    def verifie(nom: str, condition: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not condition:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # Clopper-Pearson : k = 0 a une forme fermee, 1 - (alpha/2)^(1/n).
    bas, haut = clopper_pearson(0, 24)
    attendu = 1 - 0.025 ** (1 / 24)
    verifie("CP(0,24) borne basse nulle", bas == 0.0, f"{bas}")
    verifie("CP(0,24) borne haute = 1-(a/2)^(1/n)", abs(haut - attendu) < 1e-12,
            f"{haut} vs {attendu}")
    bas, haut = clopper_pearson(24, 24)
    verifie("CP(n,n) borne haute = 1", haut == 1.0, f"{haut}")
    verifie("CP(n,n) borne basse = (a/2)^(1/n)",
            abs(bas - 0.025 ** (1 / 24)) < 1e-12, f"{bas}")
    bas, haut = clopper_pearson(1, 28)
    verifie("CP(1,28) encadre la part observee", bas < 1 / 28 < haut, f"{bas}–{haut}")
    verifie("CP se resserre quand n monte",
            (clopper_pearson(5, 100)[1] - clopper_pearson(5, 100)[0])
            < (clopper_pearson(1, 20)[1] - clopper_pearson(1, 20)[0]))

    # Holm : m*p1, puis (m-1)*p2 borne par le precedent, et monotone.
    aj = holm([0.01, 0.02, 0.04])
    verifie("Holm premier = m*p", abs(aj[0] - 0.03) < 1e-12, f"{aj}")
    verifie("Holm deuxieme = max(prec, (m-1)*p)", abs(aj[1] - 0.04) < 1e-12, f"{aj}")
    verifie("Holm monotone", aj[0] <= aj[1] <= aj[2], f"{aj}")
    verifie("Holm plafonne a 1", max(holm([0.5, 0.6, 0.9])) <= 1.0)
    verifie("Holm sur un seul essai ne corrige rien", holm([0.03]) == [0.03])

    # Fisher : une table dont le p exact est calculable a la main.
    p_fisher = float(fisher_exact([[0, 24], [0, 24]], alternative="greater").pvalue)
    verifie("Fisher sur deux colonnes identiques rend 1", abs(p_fisher - 1.0) < 1e-12,
            f"{p_fisher}")

    # ⭐ La sonde qui compte : sous H0 la puissance vaut le niveau, pas davantage.
    sous_nulle = puissance_exacte(0.15, 0.15, 30)
    verifie("puissance sous H0 <= alpha (Fisher est conservateur)",
            sous_nulle <= 0.05, f"{sous_nulle:.4f}")
    verifie("puissance croit avec n",
            puissance_exacte(0.04, 0.24, 25) < puissance_exacte(0.04, 0.24, 60))
    verifie("puissance croit avec l'ecart",
            puissance_exacte(0.10, 0.14, 40) < puissance_exacte(0.04, 0.30, 40))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?", default=str(RACINE / "docs/carte_separabilite"))
    ap.add_argument("--json")
    ap.add_argument("--puissance", type=int, nargs="*", default=[25, 50, 100, 200],
                    help="effectifs a evaluer pour la puissance (fenetres par rouleau)")
    ap.add_argument("--verifier", action="store_true",
                    help="temoin hors ligne de l'appareil statistique, sans artefact")
    a = ap.parse_args()

    if a.verifier:
        return verifier()

    from scipy.stats import fisher_exact

    temoin, rouleaux = charger(Path(a.dossier))
    if temoin is None or not rouleaux:
        print(f"artefacts introuvables sous {a.dossier}")
        return 1

    ic_temoin = clopper_pearson(temoin["k"], temoin["n"])
    temoin["ic95"] = ic_temoin
    print(f"témoin {temoin['rouleau']} : {temoin['k']}/{temoin['n']} fenêtres "
          f"indissociables ({temoin['part']:.1%}), "
          f"IC 95 % {ic_temoin[0]:.1%} – {ic_temoin[1]:.1%}")
    print("  ⚠ Le zéro du témoin n'est pas un zéro : sur 24 fenêtres il est compatible")
    print(f"     avec un taux réel allant jusqu'à {ic_temoin[1]:.1%}.\n")

    # Fisher unilateral contre le temoin, puis Holm sur les treize.
    bruts = []
    for r in rouleaux:
        table = [[r["k"], r["n"] - r["k"]], [temoin["k"], temoin["n"] - temoin["k"]]]
        bruts.append(float(fisher_exact(table, alternative="greater").pvalue))
    ajustes = holm(bruts)
    for r, p, q in zip(rouleaux, bruts, ajustes):
        r["p_vs_temoin"], r["p_holm"] = p, q
        r["ic95"] = clopper_pearson(r["k"], r["n"])

    rouleaux.sort(key=lambda r: (r["part"], -r["n"]))
    entete = (f"  {'rouleau':<12} {'k/n':>7} {'part':>7} {'IC 95 %':>16} "
              f"{'p vs témoin':>12} {'p Holm':>8}")
    print(entete)
    print("  " + "-" * (len(entete) - 2))
    for r in rouleaux:
        marque = " ⭐" if r["p_holm"] < 0.05 else ""
        print(f"  {r['rouleau']:<12} {r['k']:>3}/{r['n']:<3} {r['part']:>6.1%} "
              f"{r['ic95'][0]:>6.1%} – {r['ic95'][1]:<6.1%} "
              f"{r['p_vs_temoin']:>12.3f} {r['p_holm']:>8.3f}{marque}")

    distincts = [r["rouleau"] for r in rouleaux if r["p_holm"] < 0.05]
    nominaux = [r["rouleau"] for r in rouleaux if r["p_vs_temoin"] < 0.05]

    # Le classement : combien des paires sont reellement separees ?
    paires, separees, brutes_p = 0, 0, []
    for i, ri in enumerate(rouleaux):
        for rj in rouleaux[i + 1:]:
            paires += 1
            brutes_p.append(float(fisher_exact(
                [[rj["k"], rj["n"] - rj["k"]], [ri["k"], ri["n"] - ri["k"]]],
                alternative="two-sided").pvalue))
    for q in holm(brutes_p):
        if q < 0.05:
            separees += 1

    print(f"\n  distinguables du témoin après Holm : {len(distincts)}/{len(rouleaux)}"
          + (f"  ({', '.join(distincts)})" if distincts else ""))
    print(f"  ... au seuil nominal, sans correction : {len(nominaux)}/{len(rouleaux)}"
          + (f"  ({', '.join(nominaux)})" if nominaux else ""))
    print(f"  paires de rouleaux réellement séparées : {separees}/{paires}")

    # La designation de `16` : PHerc0358 est-il separe de ses concurrents immediats ?
    meilleur = rouleaux[0]
    print(f"\n  le mieux classé est {meilleur['rouleau']} ({meilleur['k']}/{meilleur['n']}, "
          f"IC {meilleur['ic95'][0]:.1%} – {meilleur['ic95'][1]:.1%})")
    if meilleur["ic95"][1] > TOLERANCE_PRIX:
        print(f"  ⚠ son intervalle contient {TOLERANCE_PRIX:.0%} : les données ne permettent")
        print("     pas d'affirmer qu'il est sous la marge, ni qu'il la dépasse.")
    au_dessus = [r["rouleau"] for r in rouleaux if r["ic95"][0] > TOLERANCE_PRIX]
    en_dessous = [r["rouleau"] for r in rouleaux if r["ic95"][1] < TOLERANCE_PRIX]
    print(f"  rouleaux dont l'IC exclut d'être sous {TOLERANCE_PRIX:.0%} : "
          f"{len(au_dessus)}" + (f"  ({', '.join(au_dessus)})" if au_dessus else ""))
    print(f"  rouleaux dont l'IC exclut d'être au-dessus : "
          f"{len(en_dessous)}" + (f"  ({', '.join(en_dessous)})" if en_dessous else ""))
    print("  ⚠ comparaison INDICATIVE : la part est une fraction de fenêtres sondées,")
    print("     la marge du prix une fraction de surface de recto. Deux grandeurs.")

    # Ce qui SURVIT : les treize pris ensemble. C'est une revendication plus faible que
    # le classement, et c'est la seule que ces effectifs portent.
    k_total = sum(r["k"] for r in rouleaux)
    n_total = sum(r["n"] for r in rouleaux)
    p_groupe = float(fisher_exact([[k_total, n_total - k_total],
                                   [temoin["k"], temoin["n"] - temoin["k"]]],
                                  alternative="greater").pvalue)
    memedirection = sum(1 for r in rouleaux if r["part"] > temoin["part"])
    print(f"\n  les treize PRIS ENSEMBLE : {k_total}/{n_total} = {k_total/n_total:.1%} "
          f"contre {temoin['k']}/{temoin['n']} — p = {p_groupe:.4f}")
    print(f"  rouleaux dont la queue dépasse celle du témoin : {memedirection}/{len(rouleaux)}")
    print("  ⚠ Le p groupé traite les fenêtres comme échangeables entre rouleaux, ce")
    print("     qu'elles ne sont pas : elles sont groupées par rouleau. C'est donc une")
    print("     borne BASSE du vrai p, à lire comme un ordre de grandeur.")

    if separees == 0:
        print(f"\n  ⚠⚠ AUCUNE des {paires} paires n'est séparée : sur ces effectifs, la carte")
        print("     ordonne les treize sans que les données puissent soutenir un ordre.")
        print("     Ce qui reste vrai est le contraste au témoin, là où il survit à Holm.")

    # ⭐ Ce qui RESOUDRAIT la question. Un resultat negatif qui ne dit pas ce qu'il
    # faudrait pour trancher laisse la mesure en l'etat ; celui-ci chiffre la campagne.
    extremes = (rouleaux[0], rouleaux[-1])
    p1, p2 = extremes[0]["part"], extremes[1]["part"]
    print(f"\n  ce qu'il faudrait pour séparer les deux extrêmes "
          f"({extremes[0]['rouleau']} {p1:.1%} contre {extremes[1]['rouleau']} {p2:.1%}) :")
    echelle, atteint = [], None
    for n in a.puissance:
        pw = puissance_exacte(p1, p2, n)
        echelle.append({"n": n, "puissance": pw})
        etat = "✅" if pw >= 0.80 else "  "
        print(f"    {etat} {n:>4} fenêtres par rouleau → puissance {pw:.0%}")
        if atteint is None and pw >= 0.80:
            atteint = n
    if atteint:
        print(f"  ⭐ {atteint} fenêtres par rouleau suffiraient, contre "
              f"{min(r['n'] for r in rouleaux)}–{max(r['n'] for r in rouleaux)} aujourd'hui.")
        print("     La campagne existante est reprenable : c'est un échantillonnage plus")
        print("     dense, pas un instrument neuf.")
    else:
        print(f"  ⚠ même {max(a.puissance)} fenêtres ne suffiraient pas : l'écart entre ces")
        print("     deux rouleaux est trop petit pour être établi par ce sondage.")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "temoin": temoin, "tolerance_prix": TOLERANCE_PRIX,
            "distinguables_holm": distincts, "significatifs_nominal": nominaux,
            "paires": paires, "paires_separees": separees,
            "groupe_k": k_total, "groupe_n": n_total, "groupe_p": p_groupe,
            "meme_direction": memedirection,
            "puissance": echelle, "n_pour_80pc": atteint,
            "ic_exclut_sous_marge": au_dessus, "ic_exclut_au_dessus": en_dessous,
            "lignes": rouleaux,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
