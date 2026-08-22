#!/usr/bin/env python3
"""Le 2×2 croisé : la prédiction change-t-elle quelque chose, ou est-ce l'endroit ?

⚠⚠ **Pourquoi ce fichier refuse plus souvent qu'il ne conclut.** `PHercParis4` publie deux
prédictions de surface du même volume, et il faut choisir laquelle tracer
([`48`](../docs/48_ou_monter_lexperience.md)). Tracer chacune à *sa* meilleure graine
confondrait « quelle prédiction » avec « quel endroit » — les deux graines tombent à des
kilovoxels l'une de l'autre. D'où le 2×2 : les deux graines dans les deux prédictions.

⚠⚠ Et un troisième facteur s'y ajoute, que ce dépôt connaît depuis
[`30`](../docs/30_le_traceur_est_un_tirage.md) : **le traceur est un tirage**. Mesuré le
2026-08-22, la même graine dans la même prédiction a rendu α = +0,89 puis **+1,12**. Un
écart entre deux cellules plus petit que ça ne dit rien du tout.

⭐ Le seuil n'est donc pas choisi : c'est la **résolution que `test_convergence` déclare pour
son propre α**, importée et jamais recopiée. Un écart sous cette barre est rapporté comme
non concluant, avec le nombre qu'il aurait fallu.

Usage :
    python3 analysis/src/comparer_predictions.py --docs docs --json docs/paris4_2x2.json
    python3 analysis/src/comparer_predictions.py --verifier
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PREFIXE = "prediction_paris4_"


def charger(dossier: Path) -> list[dict]:
    """Les cellules du 2×2, lues depuis les verdicts que la campagne a écrits.

    ⚠ Le nom de fichier porte la cellule (`<prediction>_sur_graine_<graine>[_r<n>]`), et
    c'est la campagne qui l'écrit — donc lire le nom ici et le composer là-bas sont deux
    endroits qui doivent s'accorder. Un désaccord se voit tout de suite : la cellule
    manque du tableau, elle ne s'y trompe pas de case.
    """
    out = []
    for p in sorted(dossier.glob(f"{PREFIXE}*.json")):
        m = re.match(rf"{PREFIXE}(.+?)_sur_graine_(.+?)(?:_r(\d+))?$", p.stem)
        if not m:
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        out.append({"prediction": m.group(1), "graine": m.group(2),
                    "tirage": int(m.group(3) or 1), "fichier": p.name,
                    "verdict": d.get("verdict"), "alpha": d.get("alpha"),
                    "raison": d.get("raison"), "au_bord": d.get("au_bord"),
                    "serie": d.get("serie")})
    return out


def mediane(xs):
    v = sorted(xs)
    n = len(v)
    if not n:
        return None
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def croiser(cellules: list[dict], resolution: float) -> dict:
    """Le tableau 2×2 et ce qu'il autorise à dire.

    ⚠⚠ Une cellule **indécidable** n'est pas une cellule à α nul. La faire entrer dans une
    moyenne convertirait « je n'ai rien mesuré » en une valeur, ce qui est exactement le
    défaut que [`49`](../docs/49_alpha_ne_separe_pas_deux_pannes.md) vient de corriger dans
    l'instrument d'en dessous. Elles sont comptées à part.
    """
    cases: dict[tuple[str, str], list[dict]] = {}
    for c in cellules:
        cases.setdefault((c["prediction"], c["graine"]), []).append(c)

    tableau = []
    for (pred, gr), xs in sorted(cases.items()):
        alphas = [x["alpha"] for x in xs if x.get("alpha") is not None]
        indecidables = [x for x in xs if x.get("verdict") == "indecidable"]
        tableau.append({
            "prediction": pred, "graine": gr, "tirages": len(xs),
            "indecidables": len(indecidables),
            "alphas": alphas,
            "alpha_median": mediane(alphas),
            # ⚠ L'etendue INTRA-cellule est la seule mesure directe du bruit de tirage
            # disponible ici. A un seul tirage elle n'existe pas, et il faut le dire plutot
            # que d'ecrire zero -- zero se lirait comme « aucun bruit ».
            "etendue": (max(alphas) - min(alphas)) if len(alphas) >= 2 else None})

    d = {"cases": tableau, "resolution_alpha": resolution}

    # ⭐ Les deux questions que le 2×2 pose, et elles sont differentes.
    def ecart_par(cle_fixe: str, cle_varie: str) -> dict | None:
        """À valeur fixée du premier facteur, de combien le second déplace-t-il α ?"""
        ecarts = []
        for v in sorted({t[cle_fixe] for t in tableau}):
            m = [t["alpha_median"] for t in tableau
                 if t[cle_fixe] == v and t["alpha_median"] is not None]
            if len(m) >= 2:
                ecarts.append(max(m) - min(m))
        if not ecarts:
            return None
        return {"ecarts": ecarts, "max": max(ecarts), "median": mediane(ecarts)}

    d["effet_prediction"] = ecart_par("graine", "prediction")
    d["effet_endroit"] = ecart_par("prediction", "graine")

    # ⚠⚠ LE SIGNAL QUE LA COMPARAISON D'α NE PEUT PAS VOIR. Une cellule indecidable n'a pas
    # d'α, donc elle disparait des ecarts ci-dessus -- et c'est justement la ou le signal
    # etait le plus fort : mesure du 2026-08-22, les DEUX predictions rendent un profil plat
    # a la graine de `m7` et un α mesurable a celle de `ps256`. L'indecidabilite suit
    # l'ENDROIT, et c'est categorique, pas une petite difference d'α.
    #
    # ⭐ Un facteur « explique » l'indecidabilite quand elle est ENTIEREMENT concentree sur
    # un de ses niveaux : toutes les cellules indecidables d'un cote, aucune de l'autre. Un
    # partage partiel n'est pas concluant, et le dire ainsi evite d'avoir a inventer un
    # seuil sur un compte de quatre.
    def concentration(cle: str) -> dict | None:
        niveaux = sorted({t[cle] for t in tableau})
        if len(niveaux) < 2:
            return None
        par = {v: (sum(t["indecidables"] for t in tableau if t[cle] == v),
                   sum(t["tirages"] for t in tableau if t[cle] == v))
               for v in niveaux}
        total = sum(x for x, _ in par.values())
        touches = [v for v, (x, _) in par.items() if x]
        # ⚠ Zero indecidable partout n'est pas une concentration : il n'y a rien a
        # concentrer, et l'appeler « concluant » serait conclure sur une absence.
        entiere = bool(total) and len(touches) == 1 and \
            all(par[touches[0]][0] == par[touches[0]][1] for _ in (0,))
        return {"par_niveau": {v: {"indecidables": x, "tirages": n}
                               for v, (x, n) in par.items()},
                "total": total, "niveaux_touches": touches,
                "concentree": entiere}

    d["indecidabilite_par_prediction"] = concentration("prediction")
    d["indecidabilite_par_endroit"] = concentration("graine")

    # ⚠⚠ Le bruit retenu est le PLUS GRAND des deux : l'etendue intra-cellule mesuree si
    # elle existe, et la resolution que l'instrument declare. Prendre le plus petit
    # laisserait conclure sur un ecart que l'instrument ne resout pas.
    etendues = [t["etendue"] for t in tableau if t["etendue"] is not None]
    d["bruit_mesure"] = max(etendues) if etendues else None
    d["bruit_retenu"] = max([resolution] + etendues) if etendues else resolution

    verdicts = []
    for nom, e in (("prédiction", d["effet_prediction"]), ("endroit", d["effet_endroit"])):
        if e is None:
            verdicts.append({"facteur": nom, "concluant": False,
                             "raison": "pas deux valeurs à comparer"})
        elif e["max"] < d["bruit_retenu"]:
            verdicts.append({"facteur": nom, "concluant": False, "ecart_max": e["max"],
                             "raison": (f"écart maximal {e['max']:.2f} sous le bruit "
                                        f"{d['bruit_retenu']:.2f} — il faudrait au moins "
                                        f"ça pour distinguer")})
        else:
            verdicts.append({"facteur": nom, "concluant": True, "ecart_max": e["max"],
                             "raison": (f"écart maximal {e['max']:.2f} au-dessus du bruit "
                                        f"{d['bruit_retenu']:.2f}")})
    for nom, cle in (("prédiction", "indecidabilite_par_prediction"),
                     ("endroit", "indecidabilite_par_endroit")):
        c = d.get(cle)
        if c and c["concentree"]:
            verdicts.append({
                "facteur": nom, "concluant": True, "categorique": True,
                "raison": (f"toutes les {c['total']} cellule(s) indécidables sont du côté "
                           f"« {c['niveaux_touches'][0]} », aucune de l'autre — "
                           f"l'indécidabilité suit ce facteur")})
    d["verdicts"] = verdicts
    return d


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    def cel(pred, gr, a, tirage=1, verdict="suit la fenêtre"):
        return {"prediction": pred, "graine": gr, "tirage": tirage,
                "alpha": a, "verdict": verdict}

    # ⚠⚠ Quatre cellules qui ne different que par le BRUIT : rien ne doit etre conclu.
    plat = [cel("A", "a", 1.00), cel("B", "a", 1.05),
            cel("A", "b", 0.98), cel("B", "b", 1.02)]
    r = croiser(plat, 0.2)
    v("des écarts sous le bruit ne concluent pas",
      all(not x["concluant"] for x in r["verdicts"]))
    v("... en disant ce qu'il aurait fallu",
      "il faudrait au moins" in r["verdicts"][0]["raison"])

    # ⚠ Et le controle : un effet FRANC de prediction doit etre vu, sinon l'instrument ne
    # discrimine rien et son refus ne vaut rien non plus.
    net = [cel("A", "a", 0.10), cel("B", "a", 1.10),
           cel("A", "b", 0.05), cel("B", "b", 1.05)]
    r2 = croiser(net, 0.2)
    pred = next(x for x in r2["verdicts"] if x["facteur"] == "prédiction")
    lieu = next(x for x in r2["verdicts"] if x["facteur"] == "endroit")
    v("un effet franc de prédiction est vu", pred["concluant"] is True,
      str(pred))
    v("... et l'endroit reste non concluant", lieu["concluant"] is False)
    # ⚠ Le symetrique : un effet d'ENDROIT doit etre attribue a l'endroit et pas a la
    # prediction. Sans ce controle, un instrument qui dirait toujours « prediction »
    # passerait le test precedent.
    lieu_net = [cel("A", "a", 0.10), cel("B", "a", 0.05),
                cel("A", "b", 1.10), cel("B", "b", 1.05)]
    r3 = croiser(lieu_net, 0.2)
    v("un effet franc d'endroit est attribué à l'endroit",
      next(x for x in r3["verdicts"] if x["facteur"] == "endroit")["concluant"] is True)
    v("... et pas à la prédiction",
      next(x for x in r3["verdicts"] if x["facteur"] == "prédiction")["concluant"] is False)

    # ⚠⚠ Le bruit MESURE l'emporte sur la resolution quand il est plus grand : sinon on
    # conclurait sur un ecart que les tirages eux-memes reproduisent.
    bruyant = [cel("A", "a", 0.10, 1), cel("A", "a", 1.10, 2),
               cel("B", "a", 0.60), cel("A", "b", 0.60), cel("B", "b", 0.60)]
    r4 = croiser(bruyant, 0.2)
    v("l'étendue intra-cellule mesurée est retenue comme bruit",
      abs(r4["bruit_retenu"] - 1.0) < 1e-9, str(r4["bruit_retenu"]))
    v("... et elle est rapportée", abs(r4["bruit_mesure"] - 1.0) < 1e-9)
    # ⚠ A un seul tirage, l'etendue n'existe pas -- et ce n'est pas zero.
    v("une cellule à un seul tirage n'a pas d'étendue",
      croiser(plat, 0.2)["cases"][0]["etendue"] is None)
    v("... et le bruit retombe sur la résolution déclarée",
      croiser(plat, 0.2)["bruit_retenu"] == 0.2)

    # ⚠⚠ LA CONCENTRATION DE L'INDECIDABILITE, que la comparaison d'α ne peut pas voir.
    def ind(pred, gr):
        return {"prediction": pred, "graine": gr, "tirage": 1, "alpha": None,
                "verdict": "indecidable"}
    suit_endroit = [cel("A", "a", 1.10), cel("B", "a", 0.95), ind("A", "b"), ind("B", "b")]
    rc = croiser(suit_endroit, 0.2)
    ve = [x for x in rc["verdicts"] if x["facteur"] == "endroit" and x.get("categorique")]
    v("une indécidabilité concentrée sur un endroit est vue", len(ve) == 1, str(rc["verdicts"]))
    v("... et n'est PAS attribuée à la prédiction",
      not [x for x in rc["verdicts"]
           if x["facteur"] == "prédiction" and x.get("categorique")])
    # ⚠ Le symetrique, sinon l'instrument pourrait toujours repondre « endroit ».
    suit_pred = [cel("A", "a", 1.10), ind("B", "a"), cel("A", "b", 0.95), ind("B", "b")]
    vp = [x for x in croiser(suit_pred, 0.2)["verdicts"]
          if x["facteur"] == "prédiction" and x.get("categorique")]
    v("une indécidabilité concentrée sur une prédiction est vue", len(vp) == 1)
    # ⚠⚠ Un partage PARTIEL n'est pas une concentration -- sinon n'importe quelle
    # repartition inegale passerait pour un effet.
    partage = [ind("A", "a"), cel("B", "a", 1.0), ind("A", "b"), cel("B", "b", 1.0),
               ind("B", "b")]
    v("un partage partiel n'est pas concluant",
      not [x for x in croiser(partage, 0.2)["verdicts"] if x.get("categorique")])
    # ⚠ Et zero indecidable partout n'est pas une concentration : rien a concentrer.
    v("aucune indécidabilité ⇒ aucun verdict catégorique",
      not [x for x in croiser(plat, 0.2)["verdicts"] if x.get("categorique")])

    # ⚠⚠ Une cellule INDECIDABLE n'est pas une cellule a alpha nul.
    mixte = [{"prediction": "A", "graine": "a", "tirage": 1, "alpha": None,
              "verdict": "indecidable"}, cel("B", "a", 1.00)]
    rm = croiser(mixte, 0.2)
    ca = next(t for t in rm["cases"] if t["prediction"] == "A")
    v("une cellule indécidable est comptée à part", ca["indecidables"] == 1)
    v("... et n'entre pas dans la médiane", ca["alpha_median"] is None)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", type=Path, default=Path("docs"))
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from test_convergence import BRUIT_ALPHA as RESOLUTION
    except ImportError:                                   # pragma: no cover
        RESOLUTION = 0.2

    cellules = charger(a.docs)
    if not cellules:
        print(f"aucune cellule sous {a.docs} — lancer tools/tracer_prediction_paris4.sh",
              file=sys.stderr)
        return 1
    d = croiser(cellules, RESOLUTION)

    print(f"\n  {len(cellules)} cellule(s), résolution déclarée de α : {RESOLUTION}")
    print(f"\n  {'prédiction':<10} {'graine de':<10} {'tirages':>8} {'α médian':>9} "
          f"{'étendue':>8}  verdicts")
    print("  " + "-" * 62)
    for t in d["cases"]:
        am = "—" if t["alpha_median"] is None else f"{t['alpha_median']:+.2f}"
        et = "—" if t["etendue"] is None else f"{t['etendue']:.2f}"
        ind = f"  ⚠ {t['indecidables']} indécidable(s)" if t["indecidables"] else ""
        print(f"  {t['prediction']:<10} {t['graine']:<10} {t['tirages']:>8} {am:>9} "
              f"{et:>8}{ind}")

    if d["bruit_mesure"] is not None:
        print(f"\n  bruit de tirage MESURÉ : {d['bruit_mesure']:.2f}")
    print(f"  bruit retenu : {d['bruit_retenu']:.2f}")
    for x in d["verdicts"]:
        marque = "⭐" if x["concluant"] else "⚠⚠"
        cat = " (catégorique)" if x.get("categorique") else ""
        print(f"  {marque} effet {x['facteur']}{cat} : {x['raison']}")
    if not any(x["concluant"] for x in d["verdicts"]):
        print("\n  ⚠⚠ Aucun des deux facteurs ne ressort du bruit. Ce n'est pas « les deux")
        print("      prédictions se valent » — c'est « cette expérience ne peut pas les")
        print("      départager ». Répéter chaque cellule est ce qui changerait ça.")

    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
