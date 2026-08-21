#!/usr/bin/env python3
"""Une chaine de spires DERIVE-t-elle, ou chaque tour est-il un tirage ?

⚠⚠ Pourquoi la question decide de la strategie, et pas seulement de la description.
`43` mesure trois chaines dont l'alpha OSCILLE : la chaine « in » donne +0,04, +0,69,
+0,99, +0,72, puis **+0,00**, puis +0,26. Un tour parfait apres deux mauvais. Deux lectures
s'opposent :

  DERIVE   : l'erreur s'accumule, chaque tour part d'une surface deja plus fausse. Alors la
             chaine a une longueur maximale et il n'y a rien a faire au-dela.
  LOTERIE  : chaque tour reussit ou echoue selon la geometrie LOCALE, presque
             independamment du precedent. Alors un mauvais tour ne condamne pas la suite :
             on peut juger chaque spire et REJOUER les mauvaises.

⭐ La seconde lecture est beaucoup plus utile, ce qui est exactement la raison de ne pas la
choisir sans mesure.

Le test : la correlation de rang **au decalage 1** entre alpha(tour N) et alpha(tour N+1),
contre un controle par permutation. Une derive donne une correlation positive ; une loterie
donne zero.

⚠⚠ ET LA PUISSANCE EST DERISOIRE, ce qui doit etre imprime AVANT le resultat. Avec sept
tours par chaine, on a six paires par chaine. Meme en cumulant les chaines, un test de
permutation sur une douzaine de paires ne detecte qu'un effet enorme. Le resultat honnete
sera le plus souvent « on ne peut pas trancher », et c'est une information : ca dit qu'il
faut plus de tours, pas que les tours sont independants.

⚠ Les chaines sont cumulees par PAIRES, pas concatenees bout a bout : coller la fin d'une
chaine au debut d'une autre fabriquerait une paire qui n'existe pas.

Usage :
    uv run python analysis/src/derive_ou_loterie.py --chaine docs/spire_spire --nom out \\
        --chaine docs/spire_dedans_spire --nom in --json docs/derive_ou_loterie.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def alphas(prefixe: str, n_max: int = 12) -> list[float]:
    """Les alpha d'une chaine, dans l'ordre des tours, en s'arretant au premier trou.

    ⚠ On s'ARRETE au premier verdict manquant au lieu de sauter par-dessus : sauter
    fabriquerait une paire (tour 2, tour 4) presentee comme consecutive.
    """
    out = []
    for i in range(n_max):
        f = Path(f"{prefixe}{i:02d}.json")
        if not f.is_file():
            break
        out.append(json.loads(f.read_text(encoding="utf-8"))["series"][0]["alpha"])
    return out


def rangs(xs: list[float]) -> list[float]:
    """Rangs moyens (les ex aequo partagent leur rang), pour un Spearman elementaire."""
    ordre = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(ordre):
        j = i
        while j + 1 < len(ordre) and xs[ordre[j + 1]] == xs[ordre[i]]:
            j += 1
        moyen = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[ordre[k]] = moyen
        i = j + 1
    return r


def spearman(xs: list[float], ys: list[float]) -> float:
    """Corrélation de rang. Rend 0,0 quand une des deux séries est constante."""
    if len(xs) < 3:
        return 0.0
    rx, ry = rangs(xs), rangs(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def paires_decalees(chaines: dict[str, list[float]]) -> tuple[list[float], list[float]]:
    """Toutes les paires (tour N, tour N+1), cumulées sur les chaînes SANS les recoller."""
    a, b = [], []
    for serie in chaines.values():
        for i in range(len(serie) - 1):
            a.append(serie[i])
            b.append(serie[i + 1])
    return a, b


def permutation(a: list[float], b: list[float], tirages: int = 20000) -> dict:
    """p bilatéral par permutation de b contre a, exact quand c'est faisable.

    ⚠ Exact si `len(b)! <= tirages` : sur une douzaine de paires ce n'est jamais le cas,
    donc on échantillonne — et on le DIT, plutôt que de laisser croire à un test exact.
    """
    import math
    import random

    obs = spearman(a, b)
    n = len(b)
    exact = math.factorial(n) <= tirages if n <= 10 else False
    plus_extremes = 0
    total = 0
    if exact:
        for perm in itertools.permutations(b):
            total += 1
            if abs(spearman(a, list(perm))) >= abs(obs) - 1e-12:
                plus_extremes += 1
    else:
        rng = random.Random(12345)     # graine fixe : le p doit être reproductible
        c = list(b)
        for _ in range(tirages):
            rng.shuffle(c)
            total += 1
            if abs(spearman(a, c)) >= abs(obs) - 1e-12:
                plus_extremes += 1
    return {"rho": obs, "p": plus_extremes / total, "exact": exact, "tirages": total}


def puissance(n: int, rho_cible: float = 0.7, tirages: int = 2000) -> float:
    """A quel taux ce test detecterait-il une derive de force `rho_cible` sur n paires ?

    ⚠ Imprimee AVANT le resultat : un « on ne peut pas trancher » ne veut rien dire si on
    ne sait pas ce que le test aurait pu voir.
    """
    import random
    rng = random.Random(777)
    detecte = 0
    for _ in range(tirages):
        a = [rng.gauss(0, 1) for _ in range(n)]
        b = [rho_cible * x + (1 - rho_cible ** 2) ** 0.5 * rng.gauss(0, 1) for x in a]
        if permutation(a, b, tirages=400)["p"] < 0.05:
            detecte += 1
    return detecte / tirages


def verifier() -> int:
    echecs = 0

    def ok(cond, quoi):
        nonlocal echecs
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de derive_ou_loterie")

    ok(abs(spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9, "une suite croissante : ρ = 1")
    ok(abs(spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-9, "renversée : ρ = −1")
    ok(spearman([1, 2, 3], [5, 5, 5]) == 0.0, "une série constante rend 0, pas NaN")
    ok(spearman([1], [1]) == 0.0, "une seule valeur ne prétend pas corréler")
    ok(abs(spearman([1, 2, 3, 4], [1, 3, 2, 4]) - 0.8) < 1e-9,
       "les rangs échangés au milieu donnent ρ = 0,8")

    # ⚠⚠ Les paires ne se recollent pas d'une chaîne à l'autre. Deux chaînes de 3 tours
    # donnent 2 + 2 = 4 paires, pas 5.
    # ⚠ Ma première version de ce témoin cherchait la paire (1, 10) — qui n'existe pas :
    # les paires sont (tour N, tour N+1) d'une MÊME chaîne. Le témoin a attrapé mon erreur
    # dans le témoin, ce qui est le bon sens de la découverte.
    a, b = paires_decalees({"x": [1.0, 2.0, 3.0], "y": [10.0, 20.0, 30.0]})
    paires = list(zip(a, b))
    ok(len(paires) == 4, f"deux chaînes de 3 tours font 4 paires et non 5 ({len(paires)})")
    ok((1.0, 2.0) in paires and (10.0, 20.0) in paires,
       "les paires consécutives de chaque chaîne y sont")
    ok((3.0, 10.0) not in paires,
       "la fin d'une chaîne n'est JAMAIS appariée au début de l'autre (la sonde du recollage)")

    # Une dérive parfaite doit être détectée, un bruit ne doit pas l'être.
    d = permutation([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6])
    ok(d["p"] < 0.01, f"une dérive parfaite ressort (p = {d['p']:.4f})")
    ok(d["exact"], "…et sur six paires le test est EXACT, pas échantillonné")
    import random
    rng = random.Random(3)
    bruit = [rng.random() for _ in range(6)]
    d2 = permutation([1, 2, 3, 4, 5, 6], bruit)
    ok(d2["p"] > 0.05, f"du bruit ne ressort pas (p = {d2['p']:.3f})")

    print(f"\n{'tous les témoins passent' if not echecs else f'{echecs} échec(s)'}")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chaine", action="append", default=[])
    ap.add_argument("--nom", action="append", default=[])
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.chaine:
        ap.error("donner au moins une --chaine, ou --verifier")

    chaines = {}
    for i, pre in enumerate(a.chaine):
        nom = a.nom[i] if i < len(a.nom) else f"chaîne {i + 1}"
        s = alphas(pre)
        if len(s) < 3:
            print(f"⚠ {nom} : {len(s)} tour(s), trop court — ignorée", file=sys.stderr)
            continue
        chaines[nom] = s
        print(f"  {nom:<10} {len(s)} tours : " + "  ".join(f"{v:+.3f}" for v in s))

    if not chaines:
        print("aucune chaîne utilisable", file=sys.stderr)
        return 3

    x, y = paires_decalees(chaines)
    print(f"\n  {len(x)} paires (tour N, tour N+1), cumulées sans recoller les chaînes")

    # ⚠ La puissance AVANT le résultat, exprès.
    pw = puissance(len(x))
    print(f"  puissance du test : il détecterait une dérive forte (ρ = 0,7) "
          f"dans **{pw * 100:.0f} %** des cas à cette taille")

    r = permutation(x, y)
    mode = "exact" if r["exact"] else f"{r['tirages']} tirages"
    print(f"\n  ρ au décalage 1 = {r['rho']:+.3f}   p = {r['p']:.3f}   ({mode})")

    # ⚠⚠ CORRECTION DE MA PREMIERE VERSION DE CE VERDICT. Elle concluait « LOTERIE » des que
    # la puissance a ρ = 0,7 depassait 50 %. C'est trop genereux : ne pas voir une derive
    # FORTE ne dit rien d'une derive MODEREE, et ρ observe valait justement 0,3. On calcule
    # donc aussi la puissance a l'effet OBSERVE, et le verdict ne peut exclure que ce que le
    # test aurait su voir.
    pw_obs = puissance(len(x), max(0.15, abs(r["rho"])))
    print(f"  puissance à l'effet OBSERVÉ (ρ = {abs(r['rho']):.2f}) : "
          f"**{pw_obs * 100:.0f} %**")
    if r["p"] < 0.05 and r["rho"] > 0:
        verdict = "DÉRIVE — le tour suivant hérite du précédent"
    elif pw_obs >= 0.8:
        verdict = "LOTERIE — chaque tour joue sa propre partie"
    elif pw >= 0.5:
        verdict = ("PAS DE DÉRIVE FORTE — une dérive de cette ampleur aurait été vue ; "
                   "une dérive modérée, non")
    else:
        verdict = ("INDÉCIDABLE — la taille de l'échantillon l'empêche, "
                   "pas l'absence d'effet")
    print(f"  → {verdict}")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "chaines": chaines, "paires": len(x), "rho_decalage1": r["rho"],
            "p": r["p"], "exact": r["exact"], "puissance_rho07": pw,
            "puissance_effet_observe": pw_obs,
            "verdict": verdict,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
