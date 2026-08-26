#!/usr/bin/env python3
"""La dérive de la chaîne est-elle une LOI, ou seulement une description ?

⚠⚠ **Ce que ce fichier décide, et pourquoi la réponse ne peut pas venir d'un ajustement.**
[`44`](docs/44_ou_la_chaine_se_trouve.md) mesure que la chaîne **glisse** hors de la
feuille connue — −69 µm à 5,76 mm, du même côté pour 73 % des points, avec une pente qui
décélère. `31` §5 en tire la marche suivante : « corriger la dérive ». Mais corriger
suppose de **prédire**, et prédire suppose une loi qui tienne **là où on n'a pas mesuré**.

Or ajuster une courbe sur dix points la décrit toujours bien. Ce qui décide, c'est un
test **hors échantillon** : ajuster sur les premiers maillons, prédire les derniers, et
comparer l'erreur à celle du **modèle nul** — ne rien corriger du tout.

> **Une correction ne vaut d'être appliquée que si elle bat « ne rien faire » sur des
> maillons qui n'ont pas servi à l'ajuster.**

⚠ Sans le modèle nul, n'importe quelle loi paraît bonne : la dérive est monotone, donc
même une droite grossière suit la tendance. Le nul est ce qui transforme « ça suit » en
« ça sert ».

⚠⚠ **Et la circularité qu'il faut éviter.** La dérive se mesure contre le maillage
**publié**, c'est-à-dire là où la vérité existe déjà. Corriger là n'a aucun intérêt — on y
a la vérité. L'intérêt est **au-delà**, et c'est précisément là qu'on ne peut pas vérifier.
Le test hors échantillon est le seul substitut honnête : il demande si la loi apprise en
territoire connu vaut encore un peu plus loin, ce qui est la question posée en la
retardant d'un cran.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def serie(chemin: Path) -> tuple[list[float], list[float]]:
    """Distance parcourue et écart signé, en µm, maillon par maillon."""
    d = json.loads(chemin.read_text())
    um = float(d.get("um_par_voxel", 1.0))
    s, e = [], []
    for m in d["maillons"]:
        if "parcouru_um" not in m or "ecart_signe_median_vox" not in m:
            continue
        s.append(float(m["parcouru_um"]))
        e.append(float(m["ecart_signe_median_vox"]) * um)
    return s, e


def _lois():
    """Les formes candidates, avec leur nombre de paramètres.

    ⚠ Chacune est ajustée **dans l'espace d'origine** (moindres carrés sur l'écart en µm),
    et non sur une variable transformée : ajuster une puissance sur des logarithmes
    minimise l'erreur des logarithmes, ce qui pondère les petits maillons bien plus que
    les grands et n'est pas ce qu'on veut prédire.
    """
    import numpy as np

    return {
        "droite par l'origine": (lambda s, a: a * s, [1e-3]),
        "droite affine": (lambda s, a, b: a * s + b, [1e-3, 0.0]),
        "puissance": (lambda s, a, p: a * np.power(np.maximum(s, 1e-9), p), [1e-3, 1.0]),
        "logarithme": (lambda s, a, b: a * np.log1p(np.maximum(s, 0.0) / max(b, 1e-9)),
                       [-10.0, 100.0]),
    }


def _hors_echantillon(s, e, coupe: int) -> tuple[float, dict]:
    """L'erreur du modèle nul et celle de chaque loi, hors échantillon."""
    import numpy as np
    from scipy.optimize import curve_fit

    s_fit, e_fit, s_test, e_test = s[:coupe], e[:coupe], s[coupe:], e[coupe:]
    nul = float(np.sqrt(np.mean(e_test ** 2)))
    out = {}
    for nom, (f, p0) in _lois().items():
        try:
            popt, _ = curve_fit(f, s_fit, e_fit, p0=p0, maxfev=20000)
            hors = float(np.sqrt(np.mean((f(s_test, *popt) - e_test) ** 2)))
            dedans = float(np.sqrt(np.mean((f(s_fit, *popt) - e_fit) ** 2)))
        except (RuntimeError, TypeError, ValueError):
            hors = dedans = float("nan")
            popt = []
        out[nom] = (list(map(float, popt)), dedans, hors)
    return nul, out


def juger(s, e, part_ajustement: float = 0.5, tirages: int = 2000,
          graine: int = 0) -> dict:
    """Ajuster sur le DÉBUT, prédire la FIN, et comparer à un TIRAGE, pas à un seuil.

    ⚠⚠ **Battre « ne rien faire » ne suffit pas, et c'est une sonde qui l'a montré** :
    sur du bruit pur, une droite affine ajustée sur la première moitié enlève encore
    **1,8 %** de l'erreur de la seconde. Un critère « strictement mieux que le nul » est
    donc satisfait par le hasard, et déclarerait extrapolable une dérive qui n'existe pas.

    ⚠ Et poser un seuil — « il faut enlever 20 % » — serait un nombre choisi pour que le
    cas du jour passe, ce que ce dépôt refuse partout ailleurs. Le contrôle est donc un
    **tirage** : les mêmes écarts, réattribués au hasard aux mêmes distances, refont
    l'ajustement et la prédiction. La part de l'erreur enlevée par la vraie série se lit
    alors contre ce que le hasard obtient — c'est un `p`, pas une limite arbitraire.
    """
    import numpy as np
    from scipy.optimize import curve_fit

    s = np.asarray(s, dtype=float)
    e = np.asarray(e, dtype=float)
    ordre = np.argsort(s)
    s, e = s[ordre], e[ordre]
    coupe = max(2, int(round(len(s) * part_ajustement)))
    if len(s) - coupe < 2:
        raise SystemExit(f"il faut au moins deux maillons de test ; {len(s)} points")

    # ⚠⚠ LE MODELE NUL : ne rien corriger. C'est lui qui transforme « la loi suit la
    # tendance » en « la loi sert a quelque chose » -- mais il ne suffit pas, cf. le
    # tirage ci-dessous.
    nul, brut = _hors_echantillon(s, e, coupe)

    rng = np.random.default_rng(graine)
    melanges = {nom: [] for nom in brut}
    for _ in range(tirages):
        permute = rng.permutation(e)
        n2, b2 = _hors_echantillon(s, permute, coupe)
        for nom, (_, _, hors2) in b2.items():
            if n2 > 0 and hors2 == hors2:
                melanges[nom].append(1.0 - hors2 / n2)

    resultats = {}
    for nom, (popt, dedans, hors) in brut.items():
        part = float(1.0 - hors / nul) if nul > 0 and hors == hors else float("nan")
        tir = melanges[nom]
        p = (float((sum(1 for x in tir if x >= part) + 1) / (len(tir) + 1))
             if tir and part == part else float("nan"))
        resultats[nom] = {
            "parametres": [float(v) for v in popt],
            "erreur_dans_l_ajustement_um": dedans,
            "erreur_hors_echantillon_um": hors,
            "part_de_l_erreur_enlevee": part,
            "p_permutation": p,
            "bat_le_hasard": bool(p == p and p < 0.05),
        }

    meilleure = min((r["erreur_hors_echantillon_um"], n) for n, r in resultats.items()
                    if r["erreur_hors_echantillon_um"] == r["erreur_hors_echantillon_um"])
    return {
        "maillons": int(len(s)),
        "ajustes_sur": int(coupe),
        "testes_sur": int(len(s) - coupe),
        "parcouru_ajustement_um": [float(s[0]), float(s[coupe - 1])],
        "parcouru_test_um": [float(s[coupe]), float(s[-1])],
        "modele_nul_um": nul,
        "tirages": int(tirages),
        "lois": resultats,
        "meilleure_loi": meilleure[1],
        "au_moins_une_bat_le_hasard": any(r["bat_le_hasard"] for r in resultats.values()),
    }


def verifier() -> int:
    """Chaque règle avec son cas négatif."""
    import numpy as np

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    s = list(np.linspace(100.0, 6000.0, 12))

    # Une derive PARFAITEMENT lineaire doit etre predite presque exactement, et battre
    # le nul largement.
    droite = juger(s, [-0.012 * x for x in s], tirages=400)
    v("une derive lineaire est extrapolable",
      droite["au_moins_une_bat_le_hasard"], str(droite["modele_nul_um"]))
    v("... et l'erreur hors echantillon est negligeable",
      droite["lois"]["droite par l'origine"]["erreur_hors_echantillon_um"] < 0.5,
      str(droite["lois"]["droite par l'origine"]["erreur_hors_echantillon_um"]))
    v("... donc elle enleve presque toute l'erreur",
      droite["lois"]["droite par l'origine"]["part_de_l_erreur_enlevee"] > 0.99)

    # ⚠⚠ LE CAS NEGATIF, sans lequel ce fichier ne peut pas rendre « non » : une derive
    # TIREE AU HASARD ne doit etre extrapolable par aucune loi. Sans lui, un juge qui
    # repondrait toujours « oui » passerait.
    rng = np.random.default_rng(0)
    bruit = list(rng.normal(0.0, 40.0, len(s)))
    hasard = juger(s, bruit, tirages=400)
    v("du bruit n'est extrapolable par AUCUNE loi",
      not hasard["au_moins_une_bat_le_hasard"], str(hasard["lois"]["droite affine"]))

    # Le decoupage est honnete : aucun point de test ne sert a l'ajustement.
    j = juger(s, [-0.012 * x for x in s], part_ajustement=0.5, tirages=40)
    v("le decoupage separe ajustement et test",
      j["ajustes_sur"] + j["testes_sur"] == j["maillons"] and j["testes_sur"] >= 2, str(j))
    v("... et le test est APRES l'ajustement",
      j["parcouru_test_um"][0] > j["parcouru_ajustement_um"][1],
      f"{j['parcouru_test_um']} apres {j['parcouru_ajustement_um']}")

    # ⚠ Une derive qui S'ARRETE apres l'ajustement ne doit PAS etre declaree extrapolable :
    # c'est le mode de panne qui compte, celui d'une loi apprise sur un regime disparu.
    casse = [-0.012 * x if x < 3000 else -36.0 for x in s]
    jc = juger(s, casse, tirages=400)
    v("une loi qui cesse de valoir n'est pas extrapolable",
      not jc["au_moins_une_bat_le_hasard"] or
      jc["lois"]["droite par l'origine"]["part_de_l_erreur_enlevee"] < 0.5,
      str(jc["lois"]["droite par l'origine"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="La derive est-elle extrapolable ? Ajuster sur le debut, predire la fin.",
        epilog="Une correction ne vaut que si elle bat « ne rien faire » hors echantillon.")
    parser.add_argument("mesure", type=Path, nargs="?",
                        help="le JSON de couverture_publiee.py")
    parser.add_argument("--part-ajustement", type=float, default=0.5)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--verifier", action="store_true")
    a = parser.parse_args()

    if a.verifier:
        return verifier()
    if a.mesure is None:
        parser.error("donner le JSON de couverture_publiee.py, ou --verifier")

    s, e = serie(a.mesure)
    if len(s) < 4:
        raise SystemExit(f"seulement {len(s)} maillons : trop peu pour un test hors echantillon")
    r = juger(s, e, a.part_ajustement)

    print(f"{r['maillons']} maillons — ajustes sur {r['ajustes_sur']} "
          f"({r['parcouru_ajustement_um'][0]:.0f} a {r['parcouru_ajustement_um'][1]:.0f} µm), "
          f"testes sur {r['testes_sur']} "
          f"({r['parcouru_test_um'][0]:.0f} a {r['parcouru_test_um'][1]:.0f} µm)")
    print(f"\n  modele NUL (ne rien corriger) : {r['modele_nul_um']:.1f} µm\n")
    print(f"  {'loi':<22} {'dans l ajust.':>14} {'HORS ech.':>12} {'erreur enlevee':>15} {'p':>8}")
    for nom, x in r["lois"].items():
        part = x["part_de_l_erreur_enlevee"]
        print(f"  {nom:<22} {x['erreur_dans_l_ajustement_um']:>13.1f}µ "
              f"{x['erreur_hors_echantillon_um']:>11.1f}µ "
              f"{100 * part:>14.1f}% {x['p_permutation']:>8.4f}"
              + ("  ⭐" if x["bat_le_hasard"] else "  ❌"))
    print(f"\n  {'⭐ la derive EST extrapolable' if r['au_moins_une_bat_le_hasard'] else '❌ AUCUNE loi ne bat le HASARD'}"
          f" — meilleure : {r['meilleure_loi']}")

    if a.out:
        a.out.write_text(json.dumps(r, indent=2) + "\n")
        print(f"\necrit : {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
