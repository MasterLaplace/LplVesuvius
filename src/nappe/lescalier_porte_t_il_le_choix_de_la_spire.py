"""Porter un choix de spire de chunk en chunk, plutôt qu'un niveau : l'escalier des marches corrige-t-il la spire produite ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE L'ESCALIER NE SOIT CONSTRUIT SUR UN SEUL BLOC. Ce qui était vu avant d'écrire : tout ce
que `257` à `266` publient, dont la portée de la marche, seize chunks, et son écart entre chunks qui se touchent, 18,2497
voxels, la moitié d'un demi-feuillet.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `266` montre que la marche ne porte pas un niveau au-delà d'un bloc : sa
dérive s'accumule. Mais d'un chunk à celui qui le touche, elle ne perd que 18 voxels, là où une spire glissée en fait 69. Ce
qui se porte bien de proche en proche n'est donc pas un niveau, c'est un choix entier : ce chunk est-il sur la même spire que
son voisin, ou à une spire de lui. Une dérive lente passe dans le niveau sans changer le choix ; un glissement franc change le
choix sans toucher au niveau. C'est le dépliage d'une phase.

## L'escalier

Sur la différence des marches `D` d'une marche d'un seul tenant, chaque chunk reçoit un entier `k` et un niveau
`ℓ = D − 69,458 · k`, 69,458 voxels étant ce que la marche retrouve d'un pas plein (`261`). Le premier chunk est celui dont les
voisins s'écartent le moins de lui, `k = 0`. De proche en proche, par les quatre voisins, un chunk non encore placé reçoit
l'entier qui rend son niveau le plus proche de celui du chunk placé qui le touche ; l'arête la plus douce passe toujours la
première. ⚠ Une marche de l'escalier plus petite que quatre chunks reliés prend l'entier le plus fréquent de ce qui
l'entoure : un point de la maille est à 1,25 chunk du suivant, donc une spire glissée, même d'un seul point, couvre au moins
deux chunks sur deux ; un chunk seul qui saute est du bruit. La spire de référence est l'entier le plus fréquent de la marche,
et la correction ramène chaque point de la maille de la différence d'entiers, en pas pleins, 72,0833 voxels. Aucun réglage.

⚠ La règle des quatre chunks est ajoutée avant la première mesure, après qu'un contrôle sur du bruit a fait des marches d'un
seul chunk.

## Sur quoi, et une seule passe

Les deux voisinages de `265`, marchés d'un seul tenant, et les dix blocs de `264`, marchés chacun seul. Le juge note la carte du
transfert.

## Les issues, exclusives, sur les deux voisinages

Sur chacun, la part sur la bonne spire du bloc de `262` au centre, et celle de ses voisins réunis.

- elle monte au centre des deux voisinages, et ne baisse pas chez leurs voisins : l'escalier porte le choix de la spire ;
- elle monte au centre des deux, mais baisse chez les voisins de l'un au moins : il corrige le centre et abîme autour ;
- sinon : l'escalier ne corrige pas les deux blocs.

⚠ Rapporté à côté, hors de l'issue : les sept blocs réguliers notés, marchés chacun seul, réunis.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : un glissement qui s'étale sur plusieurs chunks, que l'escalier prend pour de la dérive ;
une boucle ; d'autres voisinages.

Usage :
    uv run python src/nappe/lescalier_porte_t_il_le_choix_de_la_spire.py --verifier
    uv run python src/nappe/lescalier_porte_t_il_le_choix_de_la_spire.py \\
        --json docs/mesures/lescalier_porte_t_il_le_choix_de_la_spire.json
"""
from __future__ import annotations

import argparse
import heapq
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_correction_tient_elle_sur_des_blocs_reguliers import la_part_reunie  # noqa: E402
from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points, la_part_juste  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LES_JUGES, lerreur_jugee)
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille  # noqa: E402
from que_montrent_ces_deux_vues import PAS_EN_VOXELS  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_264_A_PUBLIE = LES_MESURES / "la_marche_sait_elle_ou_ne_pas_corriger.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"
LES_QUATRE = ((0, 1), (1, 0), (0, -1), (-1, 0))
LA_PLUS_PETITE_MARCHE = 4


def le_premier(diff: np.ndarray) -> tuple[int, int] | None:
    """Le chunk dont les voisins s'écartent le moins de lui, en médiane ; égalités par la rangée puis la colonne."""
    best = None
    n, m = diff.shape
    for i in range(n):
        for j in range(m):
            if not np.isfinite(diff[i, j]):
                continue
            e = [abs(diff[i + a, j + b] - diff[i, j]) for a, b in LES_QUATRE
                 if 0 <= i + a < n and 0 <= j + b < m and np.isfinite(diff[i + a, j + b])]
            if not e:
                continue
            c = (float(np.median(e)), i, j)
            if best is None or c < best:
                best = c
    return None if best is None else (best[1], best[2])


def lescalier(diff: np.ndarray, glissade: float) -> tuple[np.ndarray, np.ndarray]:
    """Les entiers et les niveaux, de proche en proche depuis le premier chunk, l'arête la plus douce d'abord.

    Rend `k` (NaN là où `diff` manque ou n'est pas relié) et le niveau `D − glissade · k`.
    """
    n, m = diff.shape
    k = np.full((n, m), np.nan)
    niveau = np.full((n, m), np.nan)
    depart = le_premier(diff)
    if depart is None:
        return k, niveau
    tas = []

    def pousser(i, j):
        for a, b in LES_QUATRE:
            y, x = i + a, j + b
            if 0 <= y < n and 0 <= x < m and np.isfinite(diff[y, x]) and np.isnan(k[y, x]):
                kk = int(np.round((diff[y, x] - niveau[i, j]) / glissade))
                saut = abs(diff[y, x] - glissade * kk - niveau[i, j])
                heapq.heappush(tas, (saut, y, x, kk))
    i, j = depart
    k[i, j], niveau[i, j] = 0.0, diff[i, j]
    pousser(i, j)
    while tas:
        _, y, x, kk = heapq.heappop(tas)
        if not np.isnan(k[y, x]):
            continue
        k[y, x] = kk
        niveau[y, x] = diff[y, x] - glissade * kk
        pousser(y, x)
    return k, niveau


def les_marches_trop_petites(k: np.ndarray, taille: int = LA_PLUS_PETITE_MARCHE) -> np.ndarray:
    """Chaque marche de moins de `taille` chunks reliés prend l'entier le plus fréquent de ses voisins hors d'elle ; les plus
    petites d'abord, jusqu'à ce qu'aucune ne change."""
    from scipy.ndimage import label

    k = k.copy()
    for _ in range(k.size):
        petites = []
        for val in np.unique(k[np.isfinite(k)]):
            lab, n = label(k == val)
            for c in range(1, n + 1):
                m = lab == c
                if m.sum() < taille:
                    petites.append((int(m.sum()), float(val), int(np.argmax(m)), m))
        change = False
        for _, _, _, m in sorted(petites, key=lambda t: t[:3]):
            bord = np.zeros_like(m)
            bord[1:] |= m[:-1]
            bord[:-1] |= m[1:]
            bord[:, 1:] |= m[:, :-1]
            bord[:, :-1] |= m[:, 1:]
            bord &= ~m & np.isfinite(k)
            if not bord.any():
                continue
            ref = la_reference(k[bord])
            if ref is not None and ref != k[m][0]:
                k[m] = ref
                change = True
                break
        if not change:
            break
    return k


def la_reference(k: np.ndarray) -> int | None:
    """L'entier le plus fréquent ; égalités par le plus proche de zéro, puis le plus petit."""
    v = k[np.isfinite(k)].astype(int)
    if not v.size:
        return None
    vals, n = np.unique(v, return_counts=True)
    return int(sorted(zip(-n, np.abs(vals), vals))[0][2])


def corriger_par_lescalier(tau: np.ndarray, k: np.ndarray, ref: int, y0: int, x0: int,
                           pas: float = PAS_EN_VOXELS) -> tuple[np.ndarray, np.ndarray]:
    """Chaque point de la maille ramené de la différence d'entiers à la référence, en pas pleins, portée aux points."""
    kp, dedans = la_carte_aux_points(k - ref, y0, x0, tau.shape)
    with np.errstate(invalid="ignore"):
        d = np.where(dedans & np.isfinite(kp), np.round(kp), 0.0)
    return tau - pas * d, dedans & (d != 0)


def le_bilan(tau0, tau1, verite, err, masque) -> dict:
    note = masque & np.isfinite(err)
    with np.errstate(invalid="ignore"):
        rate = np.abs(err) >= DEMI_PAS_EN_VOXELS
        e1 = tau1 - verite
        return {"avant": la_part_juste(tau0, verite, masque), "apres": la_part_juste(tau1, verite, masque),
                "les_rates_rendus_justes": int((note & rate & (np.abs(e1) < DEMI_PAS_EN_VOXELS)).sum()),
                "les_justes_rendus_rates": int((note & ~rate & (np.abs(e1) >= DEMI_PAS_EN_VOXELS)).sum())}


def une_marche(diff: np.ndarray, y0: int, x0: int, blocs: list[tuple[int, int]], tau0, err, glissade) -> dict:
    verite = tau0 - err
    brut, _ = lescalier(diff, glissade)
    k = les_marches_trop_petites(brut)
    ref = la_reference(k)
    out = {"la_reference": ref, "les_marches": {},
           "les_chunks_repris_par_la_regle_des_quatre": int((np.isfinite(brut) & (brut != k)).sum())}
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
    out = {"la_glissade_voxels": glissade, "le_pas_voxels": round(PAS_EN_VOXELS, 4), "les_voisinages": {}, "les_blocs": {}}
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
        return {"lissue": "elle monte au centre des deux voisinages sans baisser chez leurs voisins : l'escalier porte le "
                          "choix de la spire", "monte": monte, "tient": tient}
    if all(monte.values()):
        return {"lissue": "elle monte au centre des deux, et baisse chez des voisins : il corrige le centre et abîme autour",
                "monte": monte, "tient": tient}
    return {"lissue": "l'escalier ne corrige pas les deux blocs", "monte": monte, "tient": tient}


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
    x = np.arange(24)[None, :] * np.ones((24, 1))
    derive = 3.0 * x
    k, niv = lescalier(derive, g)
    v("★★★★ une dérive lente, trois voxels par chunk, soixante-neuf sur la marche, reste sur une seule spire",
      lambda: np.nanmax(k) == np.nanmin(k), str(np.unique(k)))
    franc = derive.copy()
    franc[:, 12:] += g
    k2, _ = lescalier(franc, g)
    v("★★★★ un glissement franc, en travers de cette dérive, change l'entier d'un et d'un seul",
      lambda: (k2[:, 12:] - k2[:, :12].mean()).min() == 1.0 and (k2[:, 12:] - k2[:, :12].mean()).max() == 1.0
      and len(np.unique(k2[:, :12])) == 1)
    rng = np.random.default_rng(11)
    bruit = rng.normal(0.0, 12.0, (20, 20))
    k3, _ = lescalier(bruit, g)
    k3b = les_marches_trop_petites(k3)
    v("★★★★ un bruit de douze voxels ne fait pas d'escalier, une fois les marches d'un chunk reprises",
      lambda: len(np.unique(k3b)) == 1 and len(np.unique(k3)) > 1, str(np.unique(k3b)))
    k2b = les_marches_trop_petites(k2)
    v("★★★★ et la règle des quatre ne touche pas à un vrai glissement", lambda: np.array_equal(k2b, k2))
    trou = franc.copy()
    trou[5, 5] = np.nan
    k4, _ = lescalier(trou, g)
    v("★★★ un chunk manquant reste sans entier, le reste est placé",
      lambda: np.isnan(k4[5, 5]) and np.isfinite(k4).sum() == 24 * 24 - 1)
    v("★★★ la référence est l'entier le plus fréquent", lambda: la_reference(np.array([[0.0, 1.0, 1.0], [np.nan, 1.0, 0.0]]))
      == 1 and la_reference(np.array([[2.0, -1.0]])) == -1)
    tau = np.full((40, 40), 72.0)
    kk = np.zeros((16, 16))
    kk[:, 8:] = 1.0
    t1, bouge = corriger_par_lescalier(tau, kk, 0, 16, 16)
    v("★★★★ la correction ramène d'un pas plein les points de la partie glissée, et d'aucun ailleurs",
      lambda: np.allclose(t1[bouge], 72.0 - PAS_EN_VOXELS) and bouge.sum() > 0 and np.allclose(t1[~bouge], 72.0))

    def verdict(c1, c2, n1, n2):
        f = lambda a, b: {"le_centre": {"avant": {"la_part_sur_la_bonne_spire": 0.5},  # noqa: E731
                                        "apres": {"la_part_sur_la_bonne_spire": a}},
                          "les_voisins_reunis": {"avant": 0.9, "apres": b}}
        return le_verdict({"decidable": True, "les_voisinages": {"x": f(c1, n1), "y": f(c2, n2)}})["lissue"]
    v("★★★★ les issues : porte le choix, abîme autour, ne corrige pas",
      lambda: "porte le choix" in verdict(0.6, 0.7, 0.9, 0.95) and "abîme autour" in verdict(0.6, 0.7, 0.89, 0.95)
      and "ne corrige pas" in verdict(0.5, 0.7, 0.9, 0.9))

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
                                                                       "le_centre", "les_voisins_reunis")}
                                         for n, v_ in r["les_voisinages"].items()},
                      "les_reguliers_reunis": r["les_reguliers_reunis"], "le_verdict": r["le_verdict"]},
                     indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
