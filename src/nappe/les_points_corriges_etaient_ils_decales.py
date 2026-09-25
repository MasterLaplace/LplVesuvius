"""Les points que la décision corrige, le juge les voyait-il déjà décalés ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL ÉCART NE SOIT LU POINT PAR POINT. Ce qui était vu avant d'écrire : les comptes que
`265` et `270` publient, bloc par bloc, et rien en dessous. Sur les neuf voisinages, l'ancre des voisins avec la décision de
`264` rend 37 ratés justes et 7 justes ratés, dont 6 sur `(160, 160)` ; les deux bosses de ce bloc sont à 7,4151 et 47,114
voxels de l'ancre.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `270` laisse ouverte une question : sur `(160, 160)`, qui a raison, de la
marche qui y voit une glissade ou du juge qui n'en voit pas. Un point corrigé l'est de l'écart que la marche lit sous lui, pas
d'un pas plein. Deux lectures donnent le même compte : le juge voyait ces points décalés vers la spire voisine sans qu'ils le
soient d'un demi-feuillet, et la correction pousse trop loin un décalage que les deux voient ; ou le juge ne voyait rien, et la
marche voit ce qu'il ne voit pas. `269` a montré que les ratés se font en pente : la première lecture est possible.

## La mesure

Sur chaque voisinage, la décision recalculée depuis la différence que `265` et `270` publient, et elle doit redonner leurs
comptes, sans quoi rien n'est lu. Pour chaque point noté que la décision corrige : l'erreur jugée avant, `e`, l'écart que la
marche lit sous lui, `c`, et l'erreur après, `e − c`. Le décalage jugé du côté où la marche corrige : `e`, du signe de `c`.

## Les issues, exclusives, sur les justes rendus ratés réunis

- la médiane de leur décalage jugé atteint le quart d'un pas, 18 voxels, la moitié de ce qui sépare un juste d'un raté : le juge
  les voyait décalés du côté où la marche corrige ;
- elle ne l'atteint pas : le juge ne les voyait pas décalés.

⚠ Rapporté à côté : les ratés rendus justes, leur décalage jugé et ce que la marche en lit ; le témoin, les justes que la
décision ne corrige pas, sur les mêmes blocs.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : qui a raison. Le juge est ce qu'on compare ; cette tranche dit seulement s'il voyait
quelque chose là où la marche corrige.

Usage :
    uv run python src/nappe/les_points_corriges_etaient_ils_decales.py --verifier
    uv run python src/nappe/les_points_corriges_etaient_ils_decales.py \\
        --json docs/mesures/les_points_corriges_etaient_ils_decales.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points  # noqa: E402
from la_marche_sait_elle_ou_ne_pas_corriger import (corriger_decide, la_decision, le_bilan,  # noqa: E402
                                                    le_melange)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LES_JUGES, lerreur_jugee)
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import lancre_du_voisinage  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"
CE_QUE_270_A_PUBLIE = LES_MESURES / "lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.json"
LE_QUART_DE_PAS = DEMI_PAS_EN_VOXELS / 2.0
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


def la_difference(publiee: list) -> np.ndarray:
    return np.array([[np.nan if v is None else float(v) for v in rr] for rr in publiee])


def la_classe(e: float, c: float, demi: float = DEMI_PAS_EN_VOXELS) -> str:
    """Ce que la correction fait d'un point noté : d'une erreur `e`, elle retire l'écart `c` lu sous lui."""
    avant, apres = abs(e) < demi, abs(e - c) < demi
    return {(False, True): "rendu_juste", (True, False): "rendu_rate",
            (True, True): "reste_juste", (False, False): "reste_rate"}[(avant, apres)]


def les_points(tau0: np.ndarray, err: np.ndarray, diff: np.ndarray, by: int, bx: int, glissade: float) -> dict:
    """La décision de `265` sur un voisinage, recalculée, et chaque point noté qu'elle corrige."""
    y0, x0 = by - LE_BLOC, bx - LE_BLOC
    ancre = lancre_du_voisinage(diff, y0, x0, by, bx)
    diff_bloc = diff[LE_BLOC:2 * LE_BLOC, LE_BLOC:2 * LE_BLOC]
    ecart, dedans = la_carte_aux_points(diff_bloc - ancre, by, bx, tau0.shape)
    ecart = np.where(dedans, ecart, np.nan)
    dec = la_decision(ecart, le_melange(diff_bloc - ancre, glissade))
    bilan = le_bilan(tau0, corriger_decide(tau0, ecart, dec), tau0 - err, err, dedans, dec)
    note = dedans & np.isfinite(err)
    pts = [{"e": round(float(err[i, j]), 2), "c": round(float(ecart[i, j]), 2),
            "la_classe": la_classe(float(err[i, j]), float(ecart[i, j]))}
           for i, j in zip(*np.nonzero(note & dec))]
    with np.errstate(invalid="ignore"):
        temoin = note & ~dec & (np.abs(err) < DEMI_PAS_EN_VOXELS)
    return {"lancre_voxels": round(float(ancre), 4), "le_bilan": {k: bilan[k] for k in LES_COMPTES},
            "les_points": pts, "le_temoin_abs_e": [round(float(abs(err[i, j])), 2) for i, j in zip(*np.nonzero(temoin))]}


def le_decalage_juge(p: dict) -> float:
    """L'erreur jugée, comptée du côté où la marche corrige."""
    return p["e"] * (1.0 if p["c"] >= 0 else -1.0)


def la_famille(points: list[dict]) -> dict:
    if not points:
        return {"les_points": 0}
    s = np.array([le_decalage_juge(p) for p in points])
    c = np.array([abs(p["c"]) for p in points])
    return {"les_points": len(points), "le_decalage_juge_median_voxels": round(float(np.median(s)), 4),
            "lecart_lu_median_voxels": round(float(np.median(c)), 4)}


def les_reunions(voisinages: dict) -> dict:
    tous = [p for v in voisinages.values() for p in v["les_points"]]
    out = {k: la_famille([p for p in tous if p["la_classe"] == k])
           for k in ("rendu_rate", "rendu_juste", "reste_juste", "reste_rate")}
    t = [x for v in voisinages.values() for x in v["le_temoin_abs_e"]]
    out["le_temoin"] = {"les_points": len(t), "le_decalage_juge_abs_median_voxels": round(float(np.median(t)), 4)}
    return out


def mesurer(cache: Path = LE_CACHE) -> dict:
    glissade = float(json.loads(CE_QUE_261_A_PUBLIE.read_text())["le_signe"]["lecart_retrouve_voxels"])
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    out = {"la_glissade_voxels": glissade, "les_voisinages": {}}
    for source in (CE_QUE_265_A_PUBLIE, CE_QUE_270_A_PUBLIE):
        for nom, b in json.loads(source.read_text())["les_blocs"].items():
            r = les_points(tau0, err, la_difference(b["la_difference"]), b["la_rangee"], b["la_colonne"], glissade)
            publie = {k: b["lancre_du_voisinage"]["la_decision"][k] for k in LES_COMPTES}
            r["reproduit"] = r["le_bilan"] == publie
            r["publie"] = publie
            out["les_voisinages"][nom] = r
    out["decidable"] = all(v["reproduit"] for v in out["les_voisinages"].values())
    if out["decidable"]:
        out["les_reunis"] = les_reunions(out["les_voisinages"])
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la décision recalculée ne redonne pas les comptes publiés"}
    f = r["les_reunis"]["rendu_rate"]
    if f["les_points"] == 0:
        return {"lissue": "indécidable : aucun juste rendu raté"}
    if f["le_decalage_juge_median_voxels"] >= LE_QUART_DE_PAS:
        return {"lissue": "le juge les voyait décalés du côté où la marche corrige"}
    return {"lissue": "le juge ne les voyait pas décalés"}


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★★★ la classe suit l'erreur avant et après : un juste poussé d'un écart trop grand devient raté",
      lambda: la_classe(5.0, 47.0) == "rendu_rate" and la_classe(70.0, 66.0) == "rendu_juste"
      and la_classe(34.0, 69.0) == "reste_juste" and la_classe(-70.0, 20.0) == "reste_rate")
    v("★★★★ le décalage jugé se compte du côté où la marche corrige",
      lambda: le_decalage_juge({"e": 20.0, "c": 47.0}) == 20.0 and le_decalage_juge({"e": 20.0, "c": -47.0}) == -20.0
      and le_decalage_juge({"e": -20.0, "c": -47.0}) == 20.0)

    # Un voisinage entier, fabriqué : une bosse d'une glissade sur un coin du bloc central ; sous elle, des ratés à 70 et
    # des justes à 5 ; ailleurs, des justes.
    rng = np.random.default_rng(3)
    diff = rng.normal(0.0, 3.0, (3 * LE_BLOC, 3 * LE_BLOC))
    diff[LE_BLOC:LE_BLOC + 6, LE_BLOC:LE_BLOC + 6] += 69.458
    tau0 = np.zeros((40, 40))
    err = np.zeros((40, 40))
    carte, dedans = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), LE_BLOC, LE_BLOC, tau0.shape)
    bosse, _ = la_carte_aux_points(np.pad(np.ones((6, 6)), ((0, 10), (0, 10))), LE_BLOC, LE_BLOC, tau0.shape)
    sous = dedans & (bosse > 0.99)
    err[dedans & (bosse > 0) & ~sous] = np.nan   # le bord de la bosse, à mi-hauteur, n'est pas noté
    ii, jj = np.nonzero(sous)
    err[ii[::2], jj[::2]] = 70.0
    err[ii[1::2], jj[1::2]] = 5.0
    r = les_points(tau0, err, diff, LE_BLOC, LE_BLOC, 69.458)
    cls = [p["la_classe"] for p in r["les_points"]]
    v("★★★★ sur un voisinage fabriqué, la décision corrige la bosse : ses ratés rendus justes, ses justes rendus ratés",
      lambda: cls.count("rendu_juste") == len(ii[::2]) and cls.count("rendu_rate") == len(ii[1::2])
      and r["le_bilan"]["les_rates_rendus_justes"] == len(ii[::2]), f"{len(ii)} sous la bosse, {cls}")
    g = les_reunions({"a": r})
    hors = int((dedans & (bosse == 0)).sum())
    v("★★★★ la réunion rend le décalage jugé des justes rendus ratés, et le témoin est tout juste noté hors de la bosse",
      lambda: g["rendu_rate"]["le_decalage_juge_median_voxels"] == 5.0 and g["le_temoin"]["les_points"] == hors
      and len(r["les_points"]) == len(ii) and hors > 0, f"{g} ; {hors} hors de la bosse")
    v("★★★★ les issues : décalés au quart d'un pas, pas décalés en dessous, indécidable si non reproduit",
      lambda: "voyait décalés" in le_verdict({"decidable": True, "les_reunis": {"rendu_rate": {
          "les_points": 3, "le_decalage_juge_median_voxels": 18.0}}})["lissue"]
      and "ne les voyait pas" in le_verdict({"decidable": True, "les_reunis": {"rendu_rate": {
          "les_points": 3, "le_decalage_juge_median_voxels": 17.9}}})["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps({"les_reunis": r.get("les_reunis"), "le_verdict": r["le_verdict"],
                      "reproduits": {n: x["reproduit"] for n, x in r["les_voisinages"].items()}}, indent=1,
                     ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
