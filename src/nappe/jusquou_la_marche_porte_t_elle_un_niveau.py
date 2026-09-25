"""Jusqu'où la marche porte-t-elle un niveau ? L'écart de la marche à l'erreur jugée, entre deux chunks, selon leur distance.

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE CET ÉCART NE SOIT CALCULÉ. Ce qui était vu avant d'écrire : tout ce que `257` à `265`
publient, dont, vu après coup en `265`, des voisins que le juge voit à 8,0224 voxels près et que la marche met à 62,185
voxels les uns des autres.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `265` prend le niveau d'un bloc chez ses voisins, et bute sur la dérive de
la marche. Tenir sur une boucle, c'est porter un niveau loin : il faut savoir à quelle distance la marche cesse de le porter
à un demi-feuillet près.

## Ce qui se mesure

La différence des marches `D`, en chaque chunk, contient ce que la spire produite a vraiment glissé et l'erreur de la
marche. La première, le juge la donne : son erreur `E` au centre du chunk, et la marche en retrouve **0,9636** (`261`,
`R4-F441`). Le reste, `r = D − 0,9636 · E`, est ce que la marche ajoute. Si elle portait un niveau parfaitement, `r` serait
le même partout ; son écart entre deux chunks est ce qu'elle perd en allant de l'un à l'autre. ⚠ Seuls comptent les chunks que
le juge tient pour justes, `|E|` sous un demi-feuillet : là où la spire a glissé, ce que la marche en retrouve n'est
calibré que sur une rampe.

Pour chaque paire de chunks d'une même marche, la distance entre leurs centres, en chunks, et `r₁ − r₂` ; par classe de
distance, `σ(d)`, la racine de la moyenne de `(r₁ − r₂)²`. Deux familles de marches : celles des dix blocs, bloc par bloc
(`264`), et celles des deux voisinages, d'un seul tenant (`265`).

## Les classes, déclarées

`[1, 2)`, `[2, 4)`, `[4, 8)`, `[8, 16)`, `[16, 32)`, `[32, 64)` chunks.

## La portée, et les issues

La portée est le bas de la première classe, sur les voisinages, où `σ(d)` atteint le demi-feuillet, 36 voxels.

- aucune classe ne l'atteint : la marche porte un niveau au-delà de ce que la mesure couvre ;
- la portée est d'au moins seize chunks : elle le porte au-delà d'un bloc ;
- sinon : elle ne le porte pas au-delà d'un bloc.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : l'erreur du juge lui-même, qui entre dans `r` ; une boucle ; d'autres voisinages.

Usage :
    uv run python src/nappe/jusquou_la_marche_porte_t_elle_un_niveau.py --verifier
    uv run python src/nappe/jusquou_la_marche_porte_t_elle_un_niveau.py \\
        --json docs/mesures/jusquou_la_marche_porte_t_elle_un_niveau.json
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

from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LES_JUGES, lerreur_aux_chunks, lerreur_jugee)
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_264_A_PUBLIE = LES_MESURES / "la_marche_sait_elle_ou_ne_pas_corriger.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"
LES_CLASSES = (1, 2, 4, 8, 16, 32, 64)


def le_reste(diff: np.ndarray, erreur: np.ndarray, pente: float, seuil: float = DEMI_PAS_EN_VOXELS) -> np.ndarray:
    """Ce que la marche ajoute à ce que la spire a glissé, là où le juge tient le chunk pour juste ; NaN ailleurs."""
    with np.errstate(invalid="ignore"):
        ok = np.isfinite(diff) & np.isfinite(erreur) & (np.abs(erreur) < seuil)
    return np.where(ok, diff - pente * erreur, np.nan)


def les_ecarts_par_distance(reste: np.ndarray, classes=LES_CLASSES) -> list[dict]:
    """Pour chaque classe de distance entre centres de chunks, le nombre de paires et σ, la racine de la moyenne de
    (r₁ − r₂)²."""
    ii, jj = np.nonzero(np.isfinite(reste))
    v = reste[ii, jj]
    out = [{"de": a, "a": b, "les_paires": 0, "_s2": 0.0} for a, b in zip(classes[:-1], classes[1:])]
    for k in range(len(v) - 1):
        d = np.hypot(ii[k + 1:] - ii[k], jj[k + 1:] - jj[k])
        e2 = (v[k + 1:] - v[k]) ** 2
        for c in out:
            m = (d >= c["de"]) & (d < c["a"])
            c["les_paires"] += int(m.sum())
            c["_s2"] += float(e2[m].sum())
    return out


def reunir(listes: list[list[dict]]) -> list[dict]:
    """Les classes de plusieurs marches réunies : les paires s'ajoutent, σ est celle de toutes les paires."""
    out = []
    for k in range(len(listes[0])):
        n = sum(x[k]["les_paires"] for x in listes)
        s2 = sum(x[k]["_s2"] for x in listes)
        out.append({"de": listes[0][k]["de"], "a": listes[0][k]["a"], "les_paires": n,
                    "sigma_voxels": round(float(np.sqrt(s2 / n)), 4) if n else None})
    return out


def la_portee(classes: list[dict], seuil: float = DEMI_PAS_EN_VOXELS) -> int | None:
    """Le bas de la première classe où σ atteint le seuil ; None si aucune."""
    for c in classes:
        if c["sigma_voxels"] is not None and c["sigma_voxels"] >= seuil:
            return c["de"]
    return None


def la_pente_en_log(classes: list[dict]) -> float | None:
    """La pente de log σ contre log du milieu géométrique de la classe : un demi pour une marche au hasard."""
    xs = [(np.log(np.sqrt(c["de"] * c["a"])), np.log(c["sigma_voxels"])) for c in classes
          if c["sigma_voxels"] is not None and c["les_paires"] >= 10]
    if len(xs) < 2:
        return None
    x, y = np.array(xs).T
    return round(float(np.polyfit(x, y, 1)[0]), 4)


def mesurer(cache: Path = LE_CACHE) -> dict:
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    d264 = json.loads(CE_QUE_264_A_PUBLIE.read_text())
    d265 = json.loads(CE_QUE_265_A_PUBLIE.read_text())
    pente = float(d261["le_signe"]["la_pente"])
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    out = {"la_pente": pente, "les_classes": list(LES_CLASSES), "les_blocs": {}, "les_voisinages": {}}
    listes_b, listes_v = [], []
    for nom, b in d264["les_blocs"].items():
        e = lerreur_aux_chunks(err, b["la_rangee"], b["la_colonne"], LE_BLOC)
        r = le_reste(la_grille(b["la_difference"]), e, pente)
        cl = les_ecarts_par_distance(r)
        listes_b.append(cl)
        out["les_blocs"][nom] = {"les_chunks": int(np.isfinite(r).sum())}
    for nom, b in d265["les_blocs"].items():
        y0, x0 = b["la_rangee"] - LE_BLOC, b["la_colonne"] - LE_BLOC
        e = lerreur_aux_chunks(err, y0, x0, 3 * LE_BLOC)
        r = le_reste(la_grille(b["la_difference"]), e, pente)
        cl = les_ecarts_par_distance(r)
        listes_v.append(cl)
        out["les_voisinages"][nom] = {"les_chunks": int(np.isfinite(r).sum()), "les_classes": reunir([cl]),
                                      "le_reste": [[None if not np.isfinite(x) else round(float(x), 2) for x in rr]
                                                   for rr in r]}
    out["bloc_par_bloc"] = reunir(listes_b)
    out["dun_seul_tenant"] = reunir(listes_v)
    out["la_portee_en_chunks"] = la_portee(out["dun_seul_tenant"])
    out["la_pente_en_log"] = {"bloc_par_bloc": la_pente_en_log(out["bloc_par_bloc"]),
                              "dun_seul_tenant": la_pente_en_log(out["dun_seul_tenant"])}
    out["decidable"] = all(c["les_paires"] > 0 for c in out["dun_seul_tenant"][:4])
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    p = r["la_portee_en_chunks"]
    if p is None:
        return {"lissue": "aucune classe ne l'atteint : la marche porte un niveau au-delà de ce que la mesure couvre"}
    if p >= LE_BLOC:
        return {"lissue": f"la portée est de {p} chunks : elle porte un niveau au-delà d'un bloc"}
    return {"lissue": f"la portée est de {p} chunks : elle ne porte pas un niveau au-delà d'un bloc"}


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

    d = np.full((4, 4), 10.0)
    e = np.zeros((4, 4))
    e[2:, :] = 20.0
    e[0, 0] = 50.0
    e[1, 1] = np.nan
    r = le_reste(d + 0.5 * e, e, 0.5)
    v("★★★★ le reste retire ce que la marche retrouve de l'erreur jugée, et seulement là où le juge tient le chunk pour juste",
      lambda: np.allclose(r[np.isfinite(r)], 10.0) and np.isnan(r[0, 0]) and np.isnan(r[1, 1]) and np.isfinite(r).sum() == 14)
    plat = les_ecarts_par_distance(np.full((8, 8), 3.0))
    v("★★★★ un reste partout égal ne perd rien à aucune distance",
      lambda: all(c["_s2"] == 0.0 for c in plat) and plat[0]["les_paires"] > 0)
    pas = np.zeros((1, 3))
    pas[0, 2] = 6.0
    cl = reunir([les_ecarts_par_distance(pas)])
    v("★★★★ σ par classe : deux paires à la distance 1, une à la distance 2",
      lambda: cl[0]["les_paires"] == 2 and cl[1]["les_paires"] == 1 and cl[0]["sigma_voxels"] == round(np.sqrt(18.0), 4)
      and cl[1]["sigma_voxels"] == 6.0, str(cl[:2]))
    rng = np.random.default_rng(5)
    brown = np.cumsum(rng.normal(0, 4.0, 4000)).reshape(1, -1)[:, :60]
    cb = reunir([les_ecarts_par_distance(brown)])
    v("★★★ sur une marche au hasard, σ croît avec la distance", lambda: cb[4]["sigma_voxels"] > cb[1]["sigma_voxels"], str(cb))
    v("★★★ la portée : le bas de la première classe à 36 voxels, ou rien",
      lambda: la_portee([{"de": 1, "sigma_voxels": 10.0}, {"de": 2, "sigma_voxels": 40.0}]) == 2
      and la_portee([{"de": 1, "sigma_voxels": 10.0}]) is None)
    v("★★★ la pente en log est un demi pour σ en racine de la distance",
      lambda: la_pente_en_log([{"de": a, "a": 2 * a, "les_paires": 50, "sigma_voxels": float(np.sqrt(a * np.sqrt(2)))}
                               for a in (1, 2, 4, 8)]) == 0.5)
    v("★★★★ les issues : au-delà de la mesure, au-delà d'un bloc, pas au-delà",
      lambda: "au-delà de ce que" in le_verdict({"decidable": True, "la_portee_en_chunks": None})["lissue"]
      and "au-delà d'un bloc" in le_verdict({"decidable": True, "la_portee_en_chunks": 16})["lissue"]
      and "ne porte pas" in le_verdict({"decidable": True, "la_portee_en_chunks": 8})["lissue"])

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
    print(texte[:4000])
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
