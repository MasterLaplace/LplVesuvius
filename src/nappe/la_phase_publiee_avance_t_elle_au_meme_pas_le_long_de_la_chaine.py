"""Le long de la chaîne de 303, la phase d'enroulement publiée (lasagna) avance-t-elle du même pas à chaque saut ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE VALEUR DE `lasagna` NE SOIT LUE SUR PHerc0358. Ce qui était vu avant d'écrire : tout ce
que `300` à `313` publient, dont `R4-F494` (la chaîne passe d'une surface de `m7` à la suivante) ; et, sur d'autres rouleaux,
`saut_de_spire.py` : le canal `cos` du groupe `lasagna` est le cosinus d'une phase d'enroulement lisse, dont la période vaut 3 à 7
pas inter-feuilles.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P103`. Tout ce qui établit la chaîne vient de `m7` et du scan. `lasagna` est une
autre prédiction publiée, qui ne dit pas où sont les feuilles mais à quelle phase d'enroulement est chaque voxel. Si les neuf
surfaces d'une pile de la chaîne sont neuf spires consécutives, la phase avance du même angle à chaque saut, et le cosinus lu sur
la pile suit une sinusoïde ; si un saut reste sur sa spire, en saute une, ou passe à une couche d'une même feuille, la sinusoïde se
casse.

## Ce qui est fait

- **La chaîne** : celle de `303`, retirée de `m7` à l'identique ; pour chaque graine, la pile de neuf surfaces, les quatre spires
  côté moins, la nappe, les quatre côté plus, dans l'ordre.
- **La phase** : le canal `cos` de `lasagna` de PHerc0358, au niveau 1 (voxels de 18,7 µm, le plus fin publié), lu au voxel qui
  contient chaque point ; la valeur brute de 1 à 255 ramenée à [−1, 1] ; zéro, la valeur de fond, compte comme absente.
- **L'ajustement** : en chaque point de la grille où les neuf surfaces sont valides et lues, le cosinus des neuf rangs k = −4 à +4
  ajusté par m + a·cos(kδ) + b·sin(kδ), δ balayé de 1 à 180 degrés (le terme constant rend l'ajustement indifférent à l'encodage
  du cosinus) ; on garde le δ du plus petit résidu, et la part de la variance
  expliquée, R².
- **Le témoin** : la même pile, ses neuf rangs permutés au hasard (graine fixe), ajustée de même.

## L'issue

Par graine, **la phase avance du même pas** si le R² médian des points dépasse 0,8, que celui du témoin permuté reste sous 0,5, et
que l'écart interquartile des δ retenus tient sous 20 degrés ; **elle ne l'avance pas** si le R² médian reste sous 0,5 ; **mêlé**
sinon ; **non lue** sous 100 points. L'issue de la tranche : **sur k des graines lues, la phase publiée avance du même pas le long
de la chaîne**, avec le δ médian, qui donne la période de `lasagna` en spires, 360/δ.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que `lasagna` ait raison ; une phase régulière le long de la chaîne dit que deux prédictions
publiées s'accordent, pas que l'une ou l'autre voit juste.

Usage :
    uv run python src/nappe/la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.py --verifier
    uv run python src/nappe/la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.py \\
        --json docs/mesures/la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402
import la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut as m303  # noqa: E402

LA_LASAGNA = "PHerc0358/representations/predictions/lasagna/20250821151737-lasagna-20260419180421/PHerc0358_cos.ome.zarr"
LE_NIVEAU = 1
LE_FACTEUR = 2.0
LE_CACHE = RACINE / "data" / "lasagna_0358"
LES_ANGLES = np.deg2rad(np.arange(1.0, 181.0))
LES_RANGS = np.arange(-4, 5)
LE_HASARD = 20260929
LE_MINIMUM = 100


def le_cosinus(brut: np.ndarray) -> np.ndarray:
    """La valeur brute ramenée à [−1, 1] ; zéro, la valeur de fond, devient NaN."""
    v = brut.astype(float)
    return np.where(v > 0, (v - 1.0) / 127.0 - 1.0, np.nan)


def ajuster(c: np.ndarray, rangs: np.ndarray = LES_RANGS, angles: np.ndarray = LES_ANGLES) -> tuple[np.ndarray, np.ndarray]:
    """Pour chaque ligne de c (n, len(rangs)), le δ du plus petit résidu de m + a·cos(kδ) + b·sin(kδ), et le R² correspondant ;
    le terme constant rend l'ajustement indifférent à l'encodage affine du cosinus."""
    n = len(c)
    meilleur = np.full(n, np.inf)
    delta = np.full(n, np.nan)
    tot = ((c - c.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
    for d in angles:
        X = np.stack([np.ones(len(rangs)), np.cos(rangs * d), np.sin(rangs * d)], axis=1)
        P = X @ np.linalg.pinv(X)
        r = ((c - c @ P.T) ** 2).sum(axis=1)
        mieux = r < meilleur
        meilleur[mieux], delta[mieux] = r[mieux], d
    with np.errstate(invalid="ignore", divide="ignore"):
        r2 = np.where(tot > 1e-9, 1.0 - meilleur / tot, np.nan)
    return np.rad2deg(delta), r2


def la_lecture(delta: np.ndarray, r2: np.ndarray, r2_temoin: np.ndarray) -> dict:
    ok = np.isfinite(r2)
    n = int(ok.sum())
    if n < LE_MINIMUM:
        return {"les_points": n, "la_lecture": "non lue"}
    m, mt = float(np.median(r2[ok])), float(np.nanmedian(r2_temoin))
    q = np.percentile(delta[ok], [25, 75])
    e = {"les_points": n, "le_r2_median": round(m, 4), "le_r2_median_du_temoin": round(mt, 4),
         "le_delta_median_degres": round(float(np.median(delta[ok])), 1),
         "lecart_interquartile_degres": round(float(q[1] - q[0]), 1),
         "la_periode_en_spires": round(360.0 / float(np.median(delta[ok])), 2)}
    if m > 0.8 and mt < 0.5 and e["lecart_interquartile_degres"] < 20.0:
        lec = "la phase avance du même pas"
    elif m < 0.5:
        lec = "elle ne l'avance pas"
    else:
        lec = "mêlé"
    return dict(e, la_lecture=lec)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lues = [g for g in d["les_graines"] if g["la_lecture"] != "non lue"]
    if not lues:
        return {"decidable": False, "lissue": "indécidable : aucune graine lue"}
    k = sum(1 for g in lues if g["la_lecture"] == "la phase avance du même pas")
    return {"decidable": True, "k": k, "n": len(lues),
            "lissue": f"sur {k} des {len(lues)} graines lues, la phase publiée avance du même pas le long de la chaîne"}


def mesurer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs

    from zarr_depth import BUCKET, array_meta
    import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298
    import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299

    t0 = time.monotonic()
    pred = array_meta(f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    las = array_meta(f"{BUCKET}/{LA_LASAGNA}", LE_NIVEAU, 120.0)
    lire_l, stats_l = lecteur_du_depot(las, LE_CACHE, "cos_L1", LA_LASAGNA, LE_NIVEAU)
    r302, identiques = m302.retirer()
    hasard = np.random.default_rng(LE_HASARD)
    graines = []
    for rang, r in r302["les_nappes"].items():
        piles = {0: (r["la_nappe"], r["valide"])}
        for nom, cote in m303.LES_COTES:
            for h, s in enumerate(m303.enchainer(r["la_nappe"], r["valide"], cote, lv), 1):
                piles[int(cote) * h] = (s["la_spire"], s["valide"])
        forme = r["valide"].shape
        valide = np.ones(forme, dtype=bool)
        cos = np.full(forme + (len(LES_RANGS),), np.nan)
        for j, k in enumerate(LES_RANGS):
            pts, ok = piles[int(k)]
            idx = np.floor(pts[..., ::-1] / LE_FACTEUR).astype(np.int64)
            cos[..., j] = le_cosinus(lire_les_valeurs(idx, las, lire_l).reshape(forme))
            valide &= ok
        c = cos[valide & np.isfinite(cos).all(axis=-1)]
        delta, r2 = ajuster(c) if len(c) else (np.zeros(0), np.zeros(0))
        perm = np.array([hasard.permutation(len(LES_RANGS)) for _ in range(len(c))], dtype=int) if len(c) else np.zeros((0, 9), int)
        ct = np.take_along_axis(c, perm, axis=1) if len(c) else c
        _, r2t = ajuster(ct) if len(c) else (np.zeros(0), np.zeros(0))
        e = dict(la_lecture(delta, r2, r2t), le_rang=rang,
                 les_points_de_la_grille_valides=int(valide.sum()),
                 les_points_sans_lasagna=int((valide & ~np.isfinite(cos).all(axis=-1)).sum()),
                 le_cosinus_median_par_rang=[round(float(np.nanmedian(cos[..., j][valide])), 4) if valide.any() else None
                                             for j in range(len(LES_RANGS))],
                 lhistogramme_des_delta=[int(x) for x in np.histogram(delta[np.isfinite(r2)], bins=np.arange(0, 190, 10))[0]])
        graines.append(e)
        print(json.dumps({k: v for k, v in e.items() if k != "lhistogramme_des_delta"}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_lasagna": LA_LASAGNA, "le_niveau": LE_NIVEAU, "le_facteur": LE_FACTEUR,
                            "les_rangs": [int(x) for x in LES_RANGS], "le_hasard": LE_HASARD, "le_minimum": LE_MINIMUM},
         "les_nappes_se_redonnent": identiques,
         "les_pannes": list(stats["pannes"]) + list(stats_l["pannes"]) + list(r302["les_pannes"]),
         "la_lecture_de_lasagna": {k: v for k, v in stats_l.items() if k != "pannes"}, "les_graines": graines}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


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

    v("★★★ le cosinus : 1 donne −1, 255 donne 1, zéro est absent",
      np.allclose(le_cosinus(np.array([1, 128, 255]))[:3], [-1.0, 0.0, 1.0]) and np.isnan(le_cosinus(np.array([0]))[0]))
    k = LES_RANGS
    reg = np.array([np.cos(0.7 + k * np.deg2rad(60.0)), np.cos(2.0 + k * np.deg2rad(90.0)), np.cos(1.1 + k * np.deg2rad(120.0))])
    d, r2 = ajuster(reg)
    v("★★★★ une pile qui avance du même angle : son δ retrouvé, et R² à 1", np.allclose(d, [60.0, 90.0, 120.0])
      and np.allclose(r2, 1.0),
      f"{d} {r2}")
    cassee = np.cos(0.7 + np.where(k < 1, k, k + 2) * np.deg2rad(60.0))[None]
    v("★★★★ une pile où un saut en vaut trois n'a plus un R² de 1", ajuster(cassee)[1][0] < 0.99, str(ajuster(cassee)[1]))
    rng = np.random.default_rng(1)
    bruit = rng.uniform(-1, 1, size=(400, len(k)))
    v("★★★ du bruit : R² médian bas", float(np.median(ajuster(bruit)[1])) < 0.8)
    plat = np.full((3, len(k)), 0.3)
    v("★★★ une pile constante n'a pas de R²", np.isnan(ajuster(plat)[1]).all())
    v("★★★★ un encodage affine du cosinus ne change ni δ ni R²",
      np.allclose(ajuster(3.0 * reg + 7.0)[0], d) and np.allclose(ajuster(3.0 * reg + 7.0)[1], r2))
    n = 300
    dd = np.full(n, 60.0)
    lec = la_lecture(dd, np.full(n, 0.95), np.full(n, 0.3))
    v("★★★★ la lecture : R² haut, témoin bas, δ serrés", lec["la_lecture"] == "la phase avance du même pas"
      and lec["la_periode_en_spires"] == 6.0)
    v("★★★★ la lecture : un témoin aussi bon que la pile ne la valide pas",
      la_lecture(dd, np.full(n, 0.95), np.full(n, 0.9))["la_lecture"] == "mêlé")
    v("★★★ la lecture : des δ dispersés ne la valident pas",
      la_lecture(np.linspace(10, 170, n), np.full(n, 0.95), np.full(n, 0.3))["la_lecture"] == "mêlé")
    v("★★★ la lecture : R² bas", la_lecture(dd, np.full(n, 0.3), np.full(n, 0.3))["la_lecture"] == "elle ne l'avance pas")
    v("★★★ la lecture : sous 100 points, non lue", la_lecture(dd[:50], np.full(50, 0.95), np.full(50, 0.3))["la_lecture"]
      == "non lue")
    vd = le_verdict({"les_graines": [{"la_lecture": "la phase avance du même pas"}, {"la_lecture": "non lue"},
                                     {"la_lecture": "mêlé"}]})
    v("★★★ l'issue : k des graines lues", vd["k"] == 1 and vd["n"] == 2)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
