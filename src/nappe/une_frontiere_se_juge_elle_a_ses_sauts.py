"""Une frontière de l'escalier se juge-t-elle à ses sauts ? Une vraie saute d'une glissade tout du long, une fausse non.

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE FRONTIÈRE NE SOIT JUGÉE. Ce qui était vu avant d'écrire : tout ce que `257` à
`267` publient, dont la frontière fausse de `267` sur le voisinage de `259` : 516 chunks mis à une spire, des deux côtés que
le juge tient pour justes.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. L'escalier de `267` place chaque chunk par une seule arête, celle qui l'a
relié. Qu'une seule arête franchisse un demi-glissement par la dérive, et toute la région qu'elle ouvre passe à une spire. Or
une frontière a bien plus d'une arête : tous les chunks qui la bordent se touchent deux à deux par-dessus. Sur une vraie
frontière, la différence des marches saute d'une glissade sur chacune ; sur une fausse, elle ne saute que là où la dérive a
franchi le demi-glissement, et presque nulle part ailleurs.

## Le jugement des frontières

L'escalier de `267`, sa règle des quatre chunks comprise. Deux marches voisines de l'escalier ont une frontière : toutes les
paires de chunks qui se touchent par-dessus. L'entier que la frontière dit est l'arrondi de la médiane de leurs sauts, divisée
par la glissade, 69,458 voxels. S'il n'est pas l'écart d'entiers des deux marches, la frontière est fausse : la plus petite
des deux marches est décalée de ce qu'il faut pour qu'elle le devienne. La plus fausse d'abord, puis tout est relu, jusqu'à ce
qu'aucune frontière ne soit fausse. La référence et la correction sont celles de `267`. Aucun réglage.

## Sur quoi, et les issues

Les mêmes que `267`, pour les comparer : les deux voisinages de `265`, et les dix blocs marchés seuls, une passe.

- elle monte au centre des deux voisinages, et ne baisse pas chez leurs voisins : la frontière se juge à ses sauts ;
- elle monte au centre des deux, mais baisse chez les voisins de l'un au moins : elle corrige le centre et abîme autour ;
- sinon : juger les frontières ne suffit pas à corriger les deux blocs.

⚠ Rapporté à côté, hors de l'issue : les sept blocs réguliers notés, réunis.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une frontière dont la dérive fausse toutes les arêtes à la fois ; une boucle.

Usage :
    uv run python src/nappe/une_frontiere_se_juge_elle_a_ses_sauts.py --verifier
    uv run python src/nappe/une_frontiere_se_juge_elle_a_ses_sauts.py \\
        --json docs/mesures/une_frontiere_se_juge_elle_a_ses_sauts.json
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

from la_correction_tient_elle_sur_des_blocs_reguliers import la_part_reunie  # noqa: E402
from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LES_JUGES, lerreur_jugee)
from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, LE_SEGMENT  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille  # noqa: E402
from lescalier_porte_t_il_le_choix_de_la_spire import (corriger_par_lescalier, la_reference, le_bilan,  # noqa: E402
                                                       les_marches_trop_petites, lescalier)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_264_A_PUBLIE = LES_MESURES / "la_marche_sait_elle_ou_ne_pas_corriger.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"


def les_marches(k: np.ndarray) -> np.ndarray:
    """Chaque marche de l'escalier, des chunks reliés de même entier, numérotée ; 0 hors de l'escalier."""
    from scipy.ndimage import label

    lab = np.zeros(k.shape, dtype=int)
    n = 0
    for val in np.unique(k[np.isfinite(k)]):
        l_, m = label(k == val)
        lab[l_ > 0] = l_[l_ > 0] + n
        n += m
    return lab


def les_frontieres(diff: np.ndarray, k: np.ndarray, glissade: float) -> list[dict]:
    """Chaque frontière entre deux marches : ses sauts, orientés de la marche `a` vers la marche `b`, l'entier qu'ils disent
    et l'écart d'entiers des deux marches."""
    lab = les_marches(k)
    sauts: dict[tuple[int, int], list[float]] = {}
    n, m = diff.shape
    for i in range(n):
        for j in range(m):
            for y, x in ((i + 1, j), (i, j + 1)):
                if y >= n or x >= m or lab[i, j] == 0 or lab[y, x] == 0 or lab[i, j] == lab[y, x]:
                    continue
                a, b = sorted((int(lab[i, j]), int(lab[y, x])))
                s = diff[y, x] - diff[i, j] if lab[i, j] == a else diff[i, j] - diff[y, x]
                sauts.setdefault((a, b), []).append(float(s))
    out = []
    taille = np.bincount(lab.ravel())
    for (a, b), s in sorted(sauts.items()):
        ka, kb = int(k[lab == a][0]), int(k[lab == b][0])
        med = float(np.median(s))
        dit = int(np.round(med / glissade))
        out.append({"a": a, "b": b, "les_aretes": len(s), "le_saut_median_voxels": round(med, 4), "lentier_dit": dit,
                    "lecart_dentiers": kb - ka, "fausse": dit != kb - ka,
                    "lecart_au_dit": abs(med / glissade - (kb - ka)), "les_tailles": (int(taille[a]), int(taille[b]))})
    return out


def juger_les_frontieres(diff: np.ndarray, k: np.ndarray, glissade: float) -> tuple[np.ndarray, list[dict]]:
    """Tant qu'une frontière est fausse : la plus fausse d'abord, sa plus petite marche décalée pour qu'elle dise vrai."""
    k = k.copy()
    journal = []
    for _ in range(int(np.isfinite(k).sum()) + 1):
        fausses = [f for f in les_frontieres(diff, k, glissade) if f["fausse"]]
        if not fausses:
            break
        f = sorted(fausses, key=lambda f: (-f["lecart_au_dit"], min(f["les_tailles"]), f["a"], f["b"]))[0]
        lab = les_marches(k)
        corr = f["lentier_dit"] - f["lecart_dentiers"]
        if f["les_tailles"][1] <= f["les_tailles"][0]:
            k[lab == f["b"]] += corr
            deplace = f["les_tailles"][1]
        else:
            k[lab == f["a"]] -= corr
            deplace = f["les_tailles"][0]
        journal.append({"le_saut_median_voxels": f["le_saut_median_voxels"], "les_aretes": f["les_aretes"],
                        "lecart_dentiers": f["lecart_dentiers"], "lentier_dit": f["lentier_dit"],
                        "les_chunks_decales": deplace})
    return k, journal


def une_marche(diff, y0, x0, blocs, tau0, err, glissade) -> dict:
    verite = tau0 - err
    brut, _ = lescalier(diff, glissade)
    k267 = les_marches_trop_petites(brut)
    k, journal = juger_les_frontieres(diff, k267, glissade)
    ref = la_reference(k)
    out = {"la_reference": ref, "les_frontieres_fausses_corrigees": len(journal), "le_journal": journal,
           "reste_fausse": any(f["fausse"] for f in les_frontieres(diff, k, glissade))}
    if ref is None:
        return {**out, "decidable": False}
    vals, n = np.unique(k[np.isfinite(k)].astype(int) - ref, return_counts=True)
    out["les_marches"] = {str(int(a)): int(b) for a, b in zip(vals, n)}
    tau1, bouge = corriger_par_lescalier(tau0, k, ref, y0, x0)
    out["les_points_deplaces"] = int(bouge.sum())
    out["les_blocs"] = {}
    for by, bx in blocs:
        _, d = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), by, bx, tau0.shape)
        out["les_blocs"][f"{by}_{bx}"] = le_bilan(tau0, tau1, verite, err, d)
    out["lescalier"] = [[None if not np.isfinite(x) else int(x) - ref for x in rr] for rr in k]
    out["decidable"] = True
    return out


def mesurer(cache: Path = LE_CACHE) -> dict:
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    d264 = json.loads(CE_QUE_264_A_PUBLIE.read_text())
    d265 = json.loads(CE_QUE_265_A_PUBLIE.read_text())
    glissade = float(d261["le_signe"]["lecart_retrouve_voxels"])
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    out = {"la_glissade_voxels": glissade, "les_voisinages": {}, "les_blocs": {}}
    for nom, b in d265["les_blocs"].items():
        by, bx = b["la_rangee"], b["la_colonne"]
        blocs = [(by, bx)] + [tuple(v) for v in b["les_voisins"]]
        r = une_marche(la_grille(b["la_difference"]), by - LE_BLOC, bx - LE_BLOC, blocs, tau0, err, glissade)
        if r["decidable"]:
            voisins = {n: x for n, x in r["les_blocs"].items() if n != f"{by}_{bx}"}
            r["le_centre"] = r["les_blocs"][f"{by}_{bx}"]
            r["les_voisins_reunis"] = {"avant": la_part_reunie(voisins, "avant"),
                                       "apres": la_part_reunie(voisins, "apres"),
                                       "les_rates_rendus_justes": sum(x["les_rates_rendus_justes"] for x in voisins.values()),
                                       "les_justes_rendus_rates": sum(x["les_justes_rendus_rates"] for x in voisins.values())}
        out["les_voisinages"][nom] = r
    for nom, b in d264["les_blocs"].items():
        by, bx = b["la_rangee"], b["la_colonne"]
        r = une_marche(la_grille(b["la_difference"]), by, bx, [(by, bx)], tau0, err, glissade)
        if r["decidable"]:
            r["le_bloc"] = r["les_blocs"][f"{by}_{bx}"]
        out["les_blocs"][nom] = r
    reg = {n: r["le_bloc"] for n, r in out["les_blocs"].items()
           if n not in ("le_bloc_de_257", "le_bloc_de_259") and r.get("decidable")
           and r["le_bloc"]["avant"]["la_part_sur_la_bonne_spire"] is not None}
    out["les_reguliers_reunis"] = {"les_blocs": len(reg), "avant": la_part_reunie(reg, "avant"),
                                   "apres": la_part_reunie(reg, "apres"),
                                   "les_rates_rendus_justes": sum(x["les_rates_rendus_justes"] for x in reg.values()),
                                   "les_justes_rendus_rates": sum(x["les_justes_rendus_rates"] for x in reg.values())}
    out["decidable"] = all(r.get("decidable") for r in out["les_voisinages"].values())
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    v = r["les_voisinages"]
    monte = {n: x["le_centre"]["apres"]["la_part_sur_la_bonne_spire"] > x["le_centre"]["avant"]["la_part_sur_la_bonne_spire"]
             for n, x in v.items()}
    tient = {n: x["les_voisins_reunis"]["apres"] >= x["les_voisins_reunis"]["avant"] for n, x in v.items()}
    if all(monte.values()) and all(tient.values()):
        return {"lissue": "elle monte au centre des deux voisinages sans baisser chez leurs voisins : la frontière se juge "
                          "à ses sauts", "monte": monte, "tient": tient}
    if all(monte.values()):
        return {"lissue": "elle monte au centre des deux, et baisse chez des voisins : elle corrige le centre et abîme "
                          "autour", "monte": monte, "tient": tient}
    return {"lissue": "juger les frontières ne suffit pas à corriger les deux blocs", "monte": monte, "tient": tient}


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

    g = 69.458
    franc = np.zeros((20, 20))
    franc[:, 10:] += g
    kf = np.zeros((20, 20))
    kf[:, 10:] = 1.0
    ff = les_frontieres(franc, kf, g)
    v("★★★★ une vraie frontière saute d'une glissade sur chacune de ses arêtes et dit vrai",
      lambda: len(ff) == 1 and ff[0]["les_aretes"] == 20 and not ff[0]["fausse"] and ff[0]["lentier_dit"] == 1, str(ff))
    plat = np.zeros((20, 20))
    plat[3:5, 12:] = 40.0
    kfaux = np.zeros((20, 20))
    kfaux[:, 12:] = 1.0
    fx = les_frontieres(plat, kfaux, g)
    v("★★★★ une fausse frontière, où la marche ne saute presque nulle part, dit un écart de zéro et est fausse",
      lambda: len(fx) == 1 and fx[0]["fausse"] and fx[0]["lentier_dit"] == 0, str(fx))
    kj, jr = juger_les_frontieres(plat, kfaux, g)
    v("★★★★ jugée, la fausse frontière disparaît, et c'est la plus petite marche qui bouge",
      lambda: len(np.unique(kj)) == 1 and jr[0]["les_chunks_decales"] == 160 and kj[0, 0] == 0.0, str(jr))
    kv, jv = juger_les_frontieres(franc, kf, g)
    v("★★★★ une vraie frontière n'est pas touchée", lambda: np.array_equal(kv, kf) and jv == [])
    trois = np.zeros((10, 30))
    trois[:, 10:] += g
    k3 = np.zeros((10, 30))
    k3[:, 10:20] = 1.0
    k3[:, 20:] = 2.0
    kj3, _ = juger_les_frontieres(trois, k3, g)
    v("★★★ trois marches, une vraie frontière et une fausse : seule la fausse est défaite",
      lambda: (kj3[:, 10:] == 1).all() and (kj3[:, :10] == 0).all(), str(np.unique(kj3)))
    lab = les_marches(np.array([[0.0, 0.0, 1.0], [np.nan, 1.0, 1.0]]))
    v("★★★ les marches sont des chunks reliés de même entier", lambda: len(np.unique(lab[lab > 0])) == 2 and lab[1, 0] == 0)

    def verdict(c1, c2, n1, n2):
        f = lambda a, b: {"le_centre": {"avant": {"la_part_sur_la_bonne_spire": 0.5},  # noqa: E731
                                        "apres": {"la_part_sur_la_bonne_spire": a}},
                          "les_voisins_reunis": {"avant": 0.9, "apres": b}}
        return le_verdict({"decidable": True, "les_voisinages": {"x": f(c1, n1), "y": f(c2, n2)}})["lissue"]
    v("★★★★ les issues", lambda: "se juge à ses sauts" in verdict(0.6, 0.7, 0.9, 0.95)
      and "abîme autour" in verdict(0.6, 0.7, 0.89, 0.95) and "ne suffit pas" in verdict(0.5, 0.7, 0.9, 0.9))

    for x_ in echecs:
        print(f"  ÉCHEC {x_}")
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
    print(json.dumps({"les_voisinages": {n: {k_: v_.get(k_) for k_ in ("la_reference", "les_marches", "les_points_deplaces",
                                                                       "les_frontieres_fausses_corrigees", "reste_fausse",
                                                                       "le_centre", "les_voisins_reunis")}
                                         for n, v_ in r["les_voisinages"].items()},
                      "les_reguliers_reunis": r["les_reguliers_reunis"], "le_verdict": r["le_verdict"]},
                     indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
