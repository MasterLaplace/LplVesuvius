"""Sous les chunks que la décision corrige sur (160, 160), le segment réduit quitte-t-il la feuille du segment ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL ÉCART ENTRE LES DEUX MAILLAGES NE SOIT CALCULÉ. Ce qui était vu avant d'écrire : tout
ce que `257` à `272` publient. Sur `(160, 160)`, sous les 13 chunks que la décision corrige, la marche du segment réduit porte
46,3791 des 66,766 voxels de l'écart (`272`) ; sous les ratés corrigés juste des blocs de `257` et `259`, elle ne bouge que de
−9,5808 à 5,1406.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `272` laisse deux lectures : la marche du segment réduit lit mal sous ces
chunks, ou le segment réduit y quitte la feuille que le segment tracé suit. Le segment réduit garde un point sur huit du segment
(`257`) ; entre deux points gardés, 160 voxels de surface, il passe en ligne droite, et une ligne droite coupe un pli. Cette
question est de géométrie pure : elle se tranche sans le rendu, sans la marche et sans le juge.

⚠ `259` a montré que la couche la plus claire d'un chunk n'est pas un repère de la feuille que le segment suit : ce n'est donc
pas elle qu'on lit ici, mais les deux maillages eux-mêmes.

## La mesure

En chaque point du segment tracé, le segment réduit interpolé en bilinéaire entre ses quatre points gardés, et l'écart des deux
le long de la normale du segment. ⚠ Bilinéaire, c'est ce que cette tranche suppose du rendu entre deux points de la grille ; elle
ne le vérifie pas. Chunk par chunk, la médiane de cet écart. Sur les trois voisinages de `272`.

## Les issues, exclusives, sur les 13 chunks que la décision corrige sur `(160, 160)`

- la médiane de l'écart absolu atteint le quart d'un pas, 18 voxels : le segment réduit quitte la feuille du segment ;
- elle ne l'atteint pas : le segment réduit reste sur la feuille du segment, et c'est la marche qui lit mal.

⚠ Rapporté à côté : le même écart sous les ratés corrigés juste des blocs de `257` et `259`, et sur tous les chunks des trois
voisinages ; et, sur chaque voisinage, la corrélation de l'écart avec la marche du segment réduit de `272`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la spire produite, faite des mêmes points gardés, coupe les mêmes plis.

Usage :
    uv run python src/nappe/le_segment_reduit_quitte_t_il_la_feuille_du_segment.py --verifier
    uv run python src/nappe/le_segment_reduit_quitte_t_il_la_feuille_du_segment.py \\
        --json docs/mesures/le_segment_reduit_quitte_t_il_la_feuille_du_segment.json
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

from la_spire_produite_se_lit_elle_dans_le_treillis import LA_MAILLE, LE_BLOC, LE_COTE_DU_CHUNK  # noqa: E402
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                les_normales, lire_tifxyz, telecharger)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_272_A_PUBLIE = LES_MESURES / "laquelle_des_deux_marches_porte_lecart.json"
LE_QUART_DE_PAS = DEMI_PAS_EN_VOXELS / 2.0


def lecart_des_maillages(ref: np.ndarray, valide: np.ndarray, maille: int = LA_MAILLE) -> np.ndarray:
    """En chaque point du segment, le segment réduit (un point sur `maille`, bilinéaire entre ses quatre points gardés) moins
    le segment, le long de la normale du segment ; NaN là où un coin, le point ou sa normale manque."""
    n, ok = les_normales(ref, valide)
    r, v = ref[::maille, ::maille], valide[::maille, ::maille]
    h, w = ref.shape[:2]
    i = np.arange(h)[:, None].repeat(w, axis=1)
    j = np.arange(w)[None, :].repeat(h, axis=0)
    i0 = np.minimum(i // maille, r.shape[0] - 2)
    j0 = np.minimum(j // maille, r.shape[1] - 2)
    fy = (i / maille - i0)[..., None]
    fx = (j / maille - j0)[..., None]
    coins = v[i0, j0] & v[i0 + 1, j0] & v[i0, j0 + 1] & v[i0 + 1, j0 + 1]
    q = ((1 - fy) * ((1 - fx) * r[i0, j0] + fx * r[i0, j0 + 1]) + fy * ((1 - fx) * r[i0 + 1, j0] + fx * r[i0 + 1, j0 + 1]))
    d = ((q - ref) * n).sum(axis=-1)
    bon = coins & ok & valide & (fy[..., 0] <= 1.0) & (fx[..., 0] <= 1.0)
    return np.where(bon, d, np.nan)


def aux_chunks(ecart: np.ndarray, y0: int, x0: int, cote: int, espacement: float,
               chunk: int = LE_COTE_DU_CHUNK) -> np.ndarray:
    """La médiane de l'écart sur les points du segment qui tombent dans chaque chunk du carré (y0, x0, cote)."""
    out = np.full((cote, cote), np.nan)
    pas = chunk / espacement
    for a in range(cote):
        i_ = np.arange(int(np.ceil((y0 + a) * pas)), int(np.ceil((y0 + a + 1) * pas)))
        i_ = i_[(i_ >= 0) & (i_ < ecart.shape[0])]
        for b in range(cote):
            j_ = np.arange(int(np.ceil((x0 + b) * pas)), int(np.ceil((x0 + b + 1) * pas)))
            j_ = j_[(j_ >= 0) & (j_ < ecart.shape[1])]
            if len(i_) == 0 or len(j_) == 0:
                continue
            e = ecart[np.ix_(i_, j_)]
            if np.isfinite(e).any():
                out[a, b] = float(np.nanmedian(e))
    return out


def la_famille(valeurs: np.ndarray) -> dict:
    x = valeurs[np.isfinite(valeurs)]
    if len(x) == 0:
        return {"les_chunks": 0}
    return {"les_chunks": int(len(x)), "lecart_abs_median_voxels": round(float(np.median(np.abs(x))), 4),
            "lecart_median_voxels": round(float(np.median(x)), 4),
            "la_part_au_quart_de_pas_ou_plus": round(float((np.abs(x) >= LE_QUART_DE_PAS).mean()), 4)}


def la_correlation(a: np.ndarray, b: np.ndarray) -> float | None:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return None
    return round(float(np.corrcoef(a[ok], b[ok])[0, 1]), 4)


def la_carte(publiee: list) -> np.ndarray:
    return np.array([[np.nan if x is None else float(x) for x in r] for r in publiee])


def mesurer(cache: Path = LE_CACHE) -> dict:
    ref, valide, espacement = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    ecart = lecart_des_maillages(ref, valide)
    d272 = json.loads(CE_QUE_272_A_PUBLIE.read_text())["les_voisinages"]
    out = {"lespacement_voxels": espacement, "les_voisinages": {}}
    temoin, tous = [], []
    for nom, v in d272.items():
        by, bx = v["la_rangee"], v["la_colonne"]
        carte = aux_chunks(ecart, by - LE_BLOC, bx - LE_BLOC, 3 * LE_BLOC, espacement)
        red = la_carte(v["la_marche_du_segment_reduit"]) - v["les_ancres_voxels"]["le_segment_reduit"]
        err = la_carte(v["lerreur_aux_chunks"])
        dec = [(int(i), int(j)) for i, j in v["les_chunks_decides"]]
        sous = np.array([carte[LE_BLOC + i, LE_BLOC + j] for i, j in dec])
        with np.errstate(invalid="ignore"):
            rates = np.array([carte[LE_BLOC + i, LE_BLOC + j] for i, j in dec if abs(err[i, j]) >= DEMI_PAS_EN_VOXELS])
        out["les_voisinages"][nom] = {
            "les_chunks_corriges": la_famille(sous), "les_chunks_corriges_juges_rates": la_famille(rates),
            "tous_les_chunks": la_famille(carte.ravel()),
            "la_correlation_avec_la_marche_du_segment_reduit": la_correlation(carte, red),
            "lecart_aux_chunks": [[None if not np.isfinite(x) else round(float(x), 2) for x in r] for r in carte]}
        tous.append(carte.ravel())
        if nom != "160_160":
            temoin.append(rates)
    out["le_temoin"] = la_famille(np.concatenate(temoin))
    out["tous_les_chunks"] = la_famille(np.concatenate(tous))
    out["decidable"] = out["les_voisinages"]["160_160"]["les_chunks_corriges"]["les_chunks"] > 0
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : aucun chunk corrigé de (160, 160) où les deux maillages existent"}
    f = r["les_voisinages"]["160_160"]["les_chunks_corriges"]
    if f["lecart_abs_median_voxels"] >= LE_QUART_DE_PAS:
        return {"lissue": "le segment réduit quitte la feuille du segment"}
    return {"lissue": "le segment réduit reste sur la feuille du segment : c'est la marche qui lit mal"}


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

    # Un plan : le segment réduit, interpolé, est le segment lui-même.
    h, w = 41, 49
    ii, jj = np.mgrid[0:h, 0:w].astype(float)
    plan = np.stack([20.0 * jj, 20.0 * ii, 3.0 * jj + 500.0], axis=-1)
    val = np.ones((h, w), dtype=bool)
    e_plan = lecart_des_maillages(plan, val)
    v("★★★★ sur un plan, le segment réduit ne s'écarte pas du segment",
      lambda: np.nanmax(np.abs(e_plan)) < 1e-9 and np.isfinite(e_plan).sum() > 0.8 * h * w)
    # Un cylindre parabolique : entre deux points gardés, le segment réduit est la corde, et à un quart de la corde elle
    # passe à 0,001 × (160² × 1/4 − 40²) = 4,8 voxels au-dessus de la surface, soit 4,78 le long de la normale.
    cyl = plan.copy()
    cyl[..., 2] = 0.001 * (20.0 * jj) ** 2
    e_c = lecart_des_maillages(cyl, val)
    pente = 2 * 0.001 * 40.0
    v("★★★★ entre deux points gardés, le segment réduit est la corde, interpolée et non recopiée d'un coin",
      lambda: abs(abs(e_c[10, 2]) - 4.8 / np.sqrt(1 + pente ** 2)) < 0.05, f"{e_c[10, 2]}")
    # Une bosse entre deux points gardés : la corde passe dessous, d'autant de voxels que la bosse est haute.
    bosse = plan.copy()
    haut = 40.0 * np.exp(-(((ii - 12.0) ** 2) + ((jj - 20.0) ** 2)) / 2.0)
    bosse[..., 2] += haut
    e_b = lecart_des_maillages(bosse, val)
    v("★★★★ sur une bosse qui tient entre deux points gardés, le segment réduit passe dessous de toute sa hauteur",
      lambda: abs(abs(e_b[12, 20]) - 40.0) < 2.0 and abs(e_b[16, 16]) < 1e-6,
      f"{e_b[12, 20]} au sommet, {e_b[16, 16]} sur un point gardé")
    # Le passage aux chunks : l'espacement de 20 voxels met 6,4 points par chunk de 128.
    grille = np.arange(64.0 * 64.0).reshape(64, 64)
    c = aux_chunks(grille, 1, 2, 3, 20.0)
    attendu = float(np.median(grille[np.ix_(np.arange(7, 13), np.arange(13, 20))]))
    v("★★★★ la médiane d'un chunk est prise sur les points qui tombent dans ce chunk, et seulement eux",
      lambda: c[0, 0] == attendu and c.shape == (3, 3), f"{c[0, 0]} contre {attendu}")
    f = la_famille(np.array([-20.0, 5.0, 30.0, np.nan]))
    v("★★★ la famille compte l'écart absolu et la part au quart de pas, sans les chunks vides",
      lambda: f["les_chunks"] == 3 and f["lecart_abs_median_voxels"] == 20.0 and f["la_part_au_quart_de_pas_ou_plus"] == 0.6667)
    v("★★★★ les issues : quitte au quart de pas, reste en dessous, indécidable sans chunk",
      lambda: "quitte" in le_verdict({"decidable": True, "les_voisinages": {"160_160": {"les_chunks_corriges": {
          "lecart_abs_median_voxels": 18.0}}}})["lissue"]
      and "reste" in le_verdict({"decidable": True, "les_voisinages": {"160_160": {"les_chunks_corriges": {
          "lecart_abs_median_voxels": 17.9}}}})["lissue"]
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
    print(json.dumps({k: r.get(k) for k in ("le_temoin", "tous_les_chunks", "le_verdict")} | {
        n: {k: x[k] for k in ("les_chunks_corriges", "les_chunks_corriges_juges_rates",
                              "la_correlation_avec_la_marche_du_segment_reduit")}
        for n, x in r["les_voisinages"].items()}, indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
