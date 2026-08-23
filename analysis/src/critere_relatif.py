#!/usr/bin/env python3
"""Quelles grandeurs d'un profil décrivent la SURFACE, et lesquelles décrivent la FENÊTRE ?

⚠⚠ **La question laissée ouverte par `47`.** Un seuil absolu posé sur une grandeur de profil
compare des réglages dès que la grandeur dépend de la fenêtre d'observation : 13 traces sur
16 butaient sur le plafond du rendu, et leur « écart » n'était que le bord de leur fenêtre.
Le document concluait qu'il faut un critère **relatif**, lu à deux profondeurs comme α, et
notait que la définition manquait — pas la matière, puisque 92 séries portent deux
profondeurs non censurées.

⭐ La définition, la voici, et ce n'est pas un critère de plus : c'est **le test que tout
critère candidat doit passer**. Pour une grandeur `C` mesurée à deux profondeurs de fenêtre
`n₀` et `n₁` :

    β = log(C₁ / C₀) / log(n₁ / n₀)

`β ≈ 0` : la grandeur ne bouge pas quand la fenêtre change, donc elle décrit la surface, donc
un seuil absolu posé dessus veut dire quelque chose. `β ≈ 1` : elle suit la fenêtre, donc un
seuil absolu compare des réglages. C'est la même construction qu'α, appliquée à autre chose
qu'à l'écart au pic — et α n'en est que le cas particulier `C = écart médian`.

⚠⚠ **Deux refus, sans lesquels β mentirait.**

1. **Une grandeur nulle d'un côté** n'a pas de rapport : `log(0)` n'existe pas, et remplacer
   par une petite valeur inventerait un β. On refuse.
2. **Une grandeur SATURÉE à sa borne** rend β = 0 pour une raison qui n'a rien à voir avec la
   surface. Une part au bord qui vaut 1,0 aux deux profondeurs ne dit pas « stable », elle dit
   « je bute des deux côtés » — c'est exactement la censure que ce dépôt traque partout
   ailleurs, et la lire comme une stabilité serait le pire contresens possible.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# ⚠ Importé, jamais recopié : la résolution de β est celle d'α, puisque c'est la même
# construction. Deux valeurs finiraient par ne pas s'accorder.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from test_convergence import BRUIT_ALPHA
except Exception:                                   # pragma: no cover - repli hors dépôt
    BRUIT_ALPHA = 0.2

# ⚠⚠ Les bornes des grandeurs BORNÉES, déclarées. Une part vaut au plus 1 ; le savoir est ce
# qui permet de distinguer « stable » de « saturée », et le deviner depuis les données
# reviendrait à décider qu'une grandeur est à sa borne parce qu'elle y est deux fois.
BORNEES = {"au_bord": 1.0, "au_bord_intensite": 1.0, "au_bord_relief": 1.0,
           "part_plates": 1.0, "tiers_central": 1.0, "tiers_central_intensite": 1.0,
           "tiers_central_relief": 1.0, "pic_intensite_median": 1.0}

# ⚠ Les grandeurs dont le test a un sens : elles décrivent le profil. `windows`,
# `couche_tracee`, `voxel_um`, `folder` décrivent la MESURE, pas la surface — les passer au
# test rendrait un β parfaitement calculable et parfaitement vide.
IGNOREES = {"folder", "layer_step", "layers", "peaks", "voxel_um", "couche_tracee",
            "windows", "avec_matiere", "fenetres_avec_relief", "amplitude_min"}

MARGE_SATURATION = 0.02


def beta(c0: float, c1: float, n0: int, n1: int) -> float | None:
    """L'exposant : de combien la grandeur suit la fenêtre.

    ⚠ Rend `None` plutôt qu'un nombre quand le rapport n'existe pas. Un instrument qui
    substitue une valeur par défaut à une impossibilité produit un chiffre que personne ne
    peut distinguer d'une mesure.
    """
    # ⚠⚠ Les NaN passent AVANT les bornes : `nan <= 0` vaut False, donc un NaN traversait
    # les gardes et ressortait en β, puis contaminait la médiane du lot entier -- « β médian
    # = +nan » sur deux grandeurs, ce qui est exactement le genre de valeur qu on lit sans
    # la voir. Un profil peut porter un NaN quand une fenêtre n a rien trouvé.
    if any(isinstance(x, float) and math.isnan(x) for x in (c0, c1)):
        return None
    if c0 <= 0 or c1 <= 0 or n0 <= 0 or n1 <= 0 or n0 == n1:
        return None
    b = math.log(c1 / c0) / math.log(n1 / n0)
    return None if math.isnan(b) or math.isinf(b) else b


def juger(nom: str, c0: float, c1: float, n0: int, n1: int) -> dict:
    d = {"grandeur": nom, "n0": n0, "n1": n1, "c0": c0, "c1": c1}
    borne = BORNEES.get(nom)
    # ⚠⚠ La saturation se teste AVANT β : une grandeur collée à sa borne des deux côtés
    # rendrait β = 0, c'est-à-dire « propriété de la surface », alors qu'elle dit seulement
    # qu'elle ne peut pas monter plus haut.
    if borne is not None and c0 >= borne - MARGE_SATURATION \
            and c1 >= borne - MARGE_SATURATION:
        d["verdict"] = "saturée"
        d["raison"] = (f"collée à sa borne ({borne}) aux deux profondeurs : β vaudrait 0 "
                       f"pour une raison qui ne dit rien de la surface")
        return d
    b = beta(c0, c1, n0, n1)
    if b is None:
        d["verdict"] = "indéfini"
        d["raison"] = "nulle d'un côté au moins : le rapport n'existe pas"
        return d
    d["beta"] = b
    if abs(b) <= BRUIT_ALPHA:
        d["verdict"] = "propriété de la surface"
    elif abs(b - 1.0) <= BRUIT_ALPHA:
        d["verdict"] = "suit la fenêtre"
    else:
        d["verdict"] = "intermédiaire"
    return d


def lire_serie(dossier: Path) -> list[tuple[int, dict]]:
    """Les profils d'une série, appariés à leur profondeur de fenêtre.

    ⚠ La profondeur vient du CONTENU (`layers`), pas du nom de fichier : le nom est une
    convention d'écriture, le contenu est ce qui a été mesuré.
    """
    out = []
    for f in sorted(dossier.glob("profil*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        p = d[0] if isinstance(d, list) and d else d
        if not isinstance(p, dict) or not isinstance(p.get("layers"), list):
            continue
        out.append((len(p["layers"]), p))
    return sorted(out)


def confronter(series: list[list[tuple[int, dict]]]) -> dict:
    par_grandeur: dict[str, list[dict]] = {}
    utilisables = 0
    for s in series:
        if len(s) < 2:
            continue
        utilisables += 1
        (n0, p0), (n1, p1) = s[0], s[-1]
        for nom, v0 in p0.items():
            if nom in IGNOREES or not isinstance(v0, (int, float)):
                continue
            v1 = p1.get(nom)
            if not isinstance(v1, (int, float)):
                continue
            par_grandeur.setdefault(nom, []).append(
                juger(nom, float(v0), float(v1), n0, n1))

    resume = []
    for nom, lot in sorted(par_grandeur.items()):
        betas = [x["beta"] for x in lot if "beta" in x]
        sat = sum(1 for x in lot if x["verdict"] == "saturée")
        ind = sum(1 for x in lot if x["verdict"] == "indéfini")
        surf = sum(1 for x in lot if x["verdict"] == "propriété de la surface")
        fen = sum(1 for x in lot if x["verdict"] == "suit la fenêtre")
        e = {"grandeur": nom, "series": len(lot), "mesurables": len(betas),
             "saturees": sat, "indefinies": ind,
             "propriete_de_surface": surf, "suit_la_fenetre": fen}
        if betas:
            b = sorted(betas)
            e["beta_median"] = b[len(b) // 2] if len(b) % 2 else \
                (b[len(b) // 2 - 1] + b[len(b) // 2]) / 2
            e["beta_min"], e["beta_max"] = b[0], b[-1]
            # ⭐ Le verdict porte sur la MAJORITÉ des séries, pas sur la médiane seule :
            # une grandeur qui décrit la surface sur la moitié des traces et la fenêtre sur
            # l'autre n'est pas un critère, c'est un tirage.
            if surf > len(betas) * 0.7:
                e["verdict"] = "lisible en absolu"
            elif fen > len(betas) * 0.7:
                e["verdict"] = "un seuil absolu compare des réglages"
            else:
                e["verdict"] = "ne tranche pas"
        else:
            e["verdict"] = "aucune mesure"
        resume.append(e)
    return {"series_lues": len(series), "series_utilisables": utilisables,
            "resolution_beta": BRUIT_ALPHA, "grandeurs": resume}


def rapporter(d: dict) -> None:
    print(f"\n  {d['series_utilisables']} série(s) à deux profondeurs, "
          f"sur {d['series_lues']} lue(s)   ·   résolution de β : {d['resolution_beta']}")
    print(f"\n  {'grandeur':26s} {'β médian':>9s} {'surface':>8s} {'fenêtre':>8s} "
          f"{'saturée':>8s}  verdict")
    print("  " + "-" * 92)
    for e in d["grandeurs"]:
        b = f"{e['beta_median']:+.2f}" if "beta_median" in e else "—"
        print(f"  {e['grandeur']:26s} {b:>9s} {e['propriete_de_surface']:>8d} "
              f"{e['suit_la_fenetre']:>8d} {e['saturees']:>8d}  {e['verdict']}")
    lisibles = [e["grandeur"] for e in d["grandeurs"] if e.get("verdict") == "lisible en absolu"]
    print(f"\n  ⭐ lisibles en absolu : {', '.join(lisibles) if lisibles else 'aucune'}")


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    # ⭐ Le cas d'école : une grandeur qui ne bouge pas quand la fenêtre triple.
    r = juger("ecart_trace_um_median", 34.56, 34.56, 31, 81)
    v("une grandeur stable décrit la surface", r["verdict"] == "propriété de la surface")
    v("... et son β vaut zéro", abs(r["beta"]) < 1e-9)

    # ⭐ Et celui qui condamne : une grandeur qui suit la fenêtre exactement.
    r = juger("ecart_trace_um_median", 40.0, 40.0 * (160 / 40), 40, 160)
    v("une grandeur qui suit la fenêtre est nommée", r["verdict"] == "suit la fenêtre")
    v("... et son β vaut un", abs(r["beta"] - 1.0) < 1e-9)

    # ⚠⚠ Le refus qui porte le fichier : une part collée à sa borne des DEUX côtés rendrait
    # β = 0, donc « propriété de la surface », alors qu'elle est censurée.
    r = juger("au_bord", 1.0, 1.0, 41, 161)
    v("une grandeur saturée est refusée, pas lue comme stable", r["verdict"] == "saturée")
    v("... et la raison le dit", "borne" in r["raison"])
    v("... et aucun β n'est rendu", "beta" not in r)
    # ⚠ Le contrôle : la MÊME grandeur, non saturée, doit être jugée normalement. Sans lui,
    # le refus s'appliquerait à tout et ne distinguerait rien.
    r = juger("au_bord", 0.35, 0.15, 31, 81)
    v("la même grandeur non saturée est jugée", r["verdict"] != "saturée")
    v("... et son β est négatif", r["beta"] < 0, f"{r.get('beta')}")

    # ⚠ Une grandeur nulle d'un côté n'a pas de rapport : on refuse plutôt que d'inventer.
    r = juger("amplitude_mediane", 0.0, 0.1, 31, 81)
    v("une grandeur nulle d'un côté est indéfinie", r["verdict"] == "indéfini")
    v("... et rien n'est substitué", "beta" not in r)
    v("deux fenêtres identiques ne donnent pas de β", beta(1.0, 2.0, 40, 40) is None)
    # ⚠⚠ Le NaN, qui traversait les gardes : `nan <= 0` vaut False. Il ressortait en β et
    # contaminait la médiane du lot -- « β médian = +nan », lu sans être vu.
    v("un NaN en entrée ne produit pas de β", beta(float("nan"), 2.0, 31, 81) is None)
    v("... des deux côtés", beta(2.0, float("nan"), 31, 81) is None)
    v("... et le verdict le dit indéfini",
      juger("x", float("nan"), 2.0, 31, 81)["verdict"] == "indéfini")

    # ⚠⚠ Le verdict porte sur la MAJORITÉ : une grandeur qui décrit la surface une fois sur
    # deux n'est pas un critère, c'est un tirage — et le dire est le point de l'instrument.
    def serie(ecart0, ecart1, n0=31, n1=81):
        return [(n0, {"layers": [0] * n0, "ecart_trace_um_median": ecart0}),
                (n1, {"layers": [0] * n1, "ecart_trace_um_median": ecart1})]

    stables = [serie(34.0, 34.0) for _ in range(8)]
    d = confronter(stables)
    e = next(x for x in d["grandeurs"] if x["grandeur"] == "ecart_trace_um_median")
    v("huit séries stables rendent la grandeur lisible", e["verdict"] == "lisible en absolu")
    v("... et les huit sont comptées", e["propriete_de_surface"] == 8)

    melange = [serie(34.0, 34.0) for _ in range(5)] + [serie(34.0, 88.8) for _ in range(5)]
    e = next(x for x in confronter(melange)["grandeurs"]
             if x["grandeur"] == "ecart_trace_um_median")
    v("un mélange moitié-moitié ne tranche pas", e["verdict"] == "ne tranche pas",
      e["verdict"])

    suiveuses = [serie(40.0, 160.0, 40, 160) for _ in range(8)]
    e = next(x for x in confronter(suiveuses)["grandeurs"]
             if x["grandeur"] == "ecart_trace_um_median")
    v("huit séries suiveuses condamnent le seuil absolu",
      e["verdict"] == "un seuil absolu compare des réglages")

    v("une série à une seule profondeur est ignorée",
      confronter([[(31, {"layers": [0] * 31, "x": 1.0})]])["series_utilisables"] == 0)
    v("aucune série, aucun verdict", confronter([])["series_utilisables"] == 0)
    v("la résolution est importée d'α", BRUIT_ALPHA == 0.2)
    # ⚠ Les grandeurs qui décrivent la MESURE et non la surface sont écartées : leur β est
    # parfaitement calculable et parfaitement vide.
    v("les grandeurs de mesure sont ignorées",
      "windows" in IGNOREES and "voxel_um" in IGNOREES)

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--racine", type=Path, default=Path("data"))
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    dossiers = sorted({f.parent for f in a.racine.rglob("profil*.json")})
    series = [lire_serie(d) for d in dossiers]
    series = [s for s in series if s]
    if not series:
        print(f"aucun profil sous {a.racine}", file=sys.stderr)
        return 2
    d = confronter(series)
    rapporter(d)
    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
