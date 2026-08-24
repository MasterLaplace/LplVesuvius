#!/usr/bin/env python3
"""Ce que vaut le relief SUR UN CORPUS, lu par l'instrument qui l'a lu.

⚠⚠ **Ce fichier existe parce qu'un seuil a été transporté deux fois le même jour, et deux
fois à tort.** Le relief dépend de la profondeur de la fenêtre (exposant mesuré **+1,01**)
ET de son étendue dans le plan (exposant **−0,83**). Un nombre lu dans une géométrie ne veut
donc rien dire dans une autre, et une table de calibration qui ne déclare pas sa géométrie
ne calibre rien.

⭐ Le remède est celui que le README public conseille désormais à ses lecteurs : ne comparer
un candidat qu'à la distribution mesurée **là où on le lit**. Ce fichier produit cette
distribution à partir d'un balayage `tracecheck --all --csv`.

⚠ La géométrie est **lue dans le fichier** quand il la porte, et **déclarée à la main**
sinon — les balayages antérieurs au 2026-08-24 ne l'écrivaient pas. La sortie dit laquelle
des deux, parce qu'un nombre fourni de mémoire vaut moins qu'un nombre relu.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
import sys
from pathlib import Path


def lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("segment")]


def nombres(lignes: list[dict], colonne: str) -> list[float]:
    out = []
    for r in lignes:
        v = r.get(colonne)
        if v in (None, ""):
            continue
        try:
            out.append(float(v))
        except ValueError:
            continue
    return sorted(out)


def geometrie(lignes: list[dict], couches: int | None,
              fenetre_px: int | None) -> dict:
    """La géométrie de lecture, relue si le fichier la porte, déclarée sinon.

    ⚠⚠ **Un désaccord entre les lignes est un refus, pas une moyenne.** Deux balayages
    concaténés à des profondeurs différentes produiraient une distribution qui n'appartient
    à aucun instrument — exactement la faute que ce fichier existe pour rendre impossible.
    """
    lues = {"layers": {r["layers"] for r in lignes if r.get("layers")},
            "window_px": {r["window_px"] for r in lignes if r.get("window_px")}}
    out: dict = {"declaree": False}
    for cle, fourni in (("layers", couches), ("window_px", fenetre_px)):
        vues = {v for v in lues[cle] if v not in ("", "0")}
        if len(vues) > 1:
            raise ValueError(f"{cle} n'est pas unique dans ce fichier : {sorted(vues)} — "
                             f"deux instruments concaténés ne calibrent rien")
        if vues:
            out[cle] = int(next(iter(vues)))
        elif fourni is not None:
            out[cle] = int(fourni)
            out["declaree"] = True
        else:
            raise ValueError(f"{cle} absent du fichier : le déclarer avec --{cle}, "
                             f"sinon la distribution n'appartient à aucun instrument")
    return out


def par_geometrie(lignes: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Les lignes groupées par géométrie de lecture.

    ⚠⚠ **Un corpus publié n'est PAS homogène, mesuré et non supposé.** Sur les 81 segments
    de `Scroll1`, quatre-vingts sont lus sur 109 couches et **un** sur 6. Une distribution
    unique aurait mélangé une lecture sur six couches à quatre-vingts lectures sur cent neuf
    — et le relief dépend de la profondeur (exposant +1,01), donc ce mélange n'aurait décrit
    aucun instrument. C'est le refus de `geometrie` qui l'a trouvé, au premier usage réel.

    ⭐ Grouper vaut mieux que refuser OU que moyenner : chaque groupe est une calibration
    valide, et le groupe d'un seul segment se voit tout de suite comme tel.
    """
    out: dict[tuple[str, str], list[dict]] = {}
    for r in lignes:
        cle = (r.get("layers") or "?", r.get("window_px") or "?")
        out.setdefault(cle, []).append(r)
    return out


def distribution(valeurs: list[float]) -> dict | None:
    if not valeurs:
        return None
    n = len(valeurs)
    return {"n": n, "min": valeurs[0], "max": valeurs[-1],
            "mediane": st.median(valeurs),
            "q1": valeurs[n // 4], "q3": valeurs[(3 * n) // 4]}


def resumer(lignes: list[dict], geo: dict, plancher: float = 0.02) -> dict:
    rel = nombres(lignes, "relief")
    bord = nombres(lignes, "edge_pinned")
    out = {"segments": len(lignes), "geometrie": geo, "plancher": plancher,
           "relief": distribution(rel), "edge_pinned": distribution(bord)}
    if rel:
        # ⚠ Le rapport au plancher est ce que le README dit de lire, donc c est lui qu on
        # publie -- pas la valeur brute, qui n a de sens que dans cette geometrie.
        out["relief_sur_plancher"] = distribution([x / plancher for x in rel])
        out["sous_le_plancher"] = sum(1 for x in rel if x < plancher)
    if bord:
        # ⚠⚠ Le compte a 90 % est rapporte parce que c est le seuil auquel `edge_pinned` a
        # ete declare fautif ailleurs. S il ne l atteint JAMAIS sur ce corpus, les deux
        # signaux ne s y departagent pas -- et le dire vaut mieux que de reciter l autre
        # mesure.
        out["au_bord_90"] = sum(1 for x in bord if x >= 0.90)
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    lignes = [{"segment": "a", "relief": "0.80", "edge_pinned": "0.05",
               "layers": "65", "window_px": "128"},
              {"segment": "b", "relief": "0.52", "edge_pinned": "0.15",
               "layers": "65", "window_px": "128"},
              {"segment": "c", "relief": "0.93", "edge_pinned": "0.00",
               "layers": "65", "window_px": "128"}]
    geo = geometrie(lignes, None, None)
    v("la geometrie est RELUE quand le fichier la porte",
      geo["layers"] == 65 and geo["window_px"] == 128 and not geo["declaree"], str(geo))

    sans = [{k: val for k, val in r.items() if k not in ("layers", "window_px")}
            for r in lignes]
    geo2 = geometrie(sans, 65, 128)
    v("... et DECLAREE quand il ne la porte pas", geo2["declaree"] and geo2["layers"] == 65)
    # ⚠⚠ Sans declaration ni colonne, on REFUSE : une distribution qui n appartient a aucun
    # instrument ne calibre rien.
    try:
        geometrie(sans, None, None)
        v("un fichier sans geometrie ni declaration est refuse", False)
    except ValueError:
        v("un fichier sans geometrie ni declaration est refuse", True)
    # ⚠⚠ Deux instruments concatenes : refus, jamais une moyenne.
    melange = lignes + [{"segment": "d", "relief": "0.10", "edge_pinned": "0.5",
                         "layers": "65", "window_px": "1024"}]
    try:
        geometrie(melange, None, None)
        v("deux geometries dans un meme fichier sont refusees", False)
    except ValueError as e:
        v("deux geometries dans un meme fichier sont refusees",
          "calibrent rien" in str(e))

    # ⚠⚠ Le groupage : mesure du 2026-08-24 sur `Scroll1`, 80 segments a 109 couches et UN
    # a 6. Une distribution unique aurait melange les deux.
    g = par_geometrie(melange)
    v("les geometries sont groupees et non fondues", len(g) == 2, str(list(g)))
    v("... et le groupe d un seul segment se voit",
      sorted(len(v) for v in g.values()) == [1, 3], str([len(v) for v in g.values()]))

    r = resumer(lignes, geo)
    v("la distribution du relief est resumee",
      r["relief"]["n"] == 3 and abs(r["relief"]["mediane"] - 0.80) < 1e-9, str(r["relief"]))
    v("le rapport au plancher est publie, pas seulement la valeur brute",
      abs(r["relief_sur_plancher"]["mediane"] - 40.0) < 1e-9,
      str(r["relief_sur_plancher"]))
    v("aucun segment sous le plancher ici", r["sous_le_plancher"] == 0)
    # ⚠ Le compte a 90 % doit etre rapporte MEME quand il vaut zero : c est ce zero qui dit
    # que les deux signaux ne se departagent pas sur ce corpus.
    v("le compte a 90 % est rapporte meme nul", r["au_bord_90"] == 0)
    v("un corpus vide ne rend pas de distribution", distribution([]) is None)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path, nargs="?", help="sortie de `tracecheck --all --csv`")
    ap.add_argument("--layers", type=int, help="profondeur lue, si le fichier ne la porte pas")
    ap.add_argument("--window-px", type=int, help="étendue dans le plan, idem")
    ap.add_argument("--plancher", type=float, default=0.02)
    ap.add_argument("--par-geometrie", action="store_true",
                    help="une calibration par géométrie plutôt qu'un refus")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.csv or not a.csv.is_file():
        ap.error("donner un CSV de balayage, ou --verifier")

    lignes = lire(a.csv)
    if not lignes:
        print(f"aucune ligne dans {a.csv}", file=sys.stderr)
        return 2
    if a.par_geometrie:
        groupes = par_geometrie(lignes)
        tout = {"corpus": len(lignes), "geometries": len(groupes), "groupes": []}
        print(f"\n  {len(lignes)} segments répartis en {len(groupes)} géométrie(s) de "
              f"lecture")
        for (couches, fenetre), sous in sorted(groupes.items(),
                                               key=lambda kv: -len(kv[1])):
            g = {"layers": int(couches), "window_px": int(fenetre), "declaree": False}
            rr = resumer(sous, g, a.plancher)
            tout["groupes"].append(rr)
            d = rr.get("relief")
            marque = "  ⚠ un seul segment" if len(sous) == 1 else ""
            print(f"    {fenetre} px × {couches} couches : {len(sous)} segment(s){marque}")
            if d:
                print(f"        relief min {d['min']:.3f}  médiane {d['mediane']:.3f}  "
                      f"max {d['max']:.3f}   sous le plancher : {rr['sous_le_plancher']}")
        print("\n  ⚠⚠ chaque groupe est une calibration ; les mélanger n'en serait pas une")
        if a.json:
            a.json.write_text(json.dumps(tout, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
            print(f"\n  écrit : {a.json}")
        return 0

    try:
        geo = geometrie(lignes, a.layers, a.window_px)
    except ValueError as e:
        print(f"refus : {e}", file=sys.stderr)
        return 3
    r = resumer(lignes, geo, a.plancher)

    src = "déclarée à la main" if geo["declaree"] else "relue dans le fichier"
    print(f"\n  {r['segments']} segments · fenêtre {geo['window_px']} px × "
          f"{geo['layers']} couches ({src})")
    for cle, nom in (("relief", "relief"), ("edge_pinned", "edge_pinned")):
        d = r.get(cle)
        if d:
            print(f"    {nom:12s} min {d['min']:.3f}  q1 {d['q1']:.3f}  "
                  f"médiane {d['mediane']:.3f}  q3 {d['q3']:.3f}  max {d['max']:.3f}")
    if r.get("relief_sur_plancher"):
        d = r["relief_sur_plancher"]
        print(f"    en multiples du plancher de {r['plancher']:g} : "
              f"×{d['min']:.1f} à ×{d['max']:.1f}, médiane ×{d['mediane']:.1f}")
        print(f"    segments sous le plancher : {r['sous_le_plancher']}")
    if r.get("au_bord_90") is not None:
        print(f"    segments à edge_pinned ≥ 90 % : {r['au_bord_90']}")
        if r["au_bord_90"] == 0:
            print("    ⚠ jamais atteint ici : sur ce corpus les deux signaux ne se "
                  "départagent pas")
    print("\n  ⚠⚠ cette distribution vaut pour CETTE géométrie et pour aucune autre")

    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
