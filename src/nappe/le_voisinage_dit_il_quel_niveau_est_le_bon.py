"""Les blocs voisins, marchés avec lui, disent-ils quel niveau d'un bloc à moitié glissé est la bonne spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL BLOC VOISIN NE SOIT RENDU. Ce qui était vu avant d'écrire : tout ce que `257` à
`264` publient, dont les deux bosses que `264` voit après coup sur le bloc de `257`, à 70,9434 voxels l'une de l'autre, et
l'ancre médiane entre les deux.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. La décision de `264` sait où ne pas corriger, mais sur un bloc à moitié
glissé elle ne corrige rien : la marche est de moyenne nulle dans le bloc, un bloc à moitié glissé a deux niveaux, et rien
dans le bloc ne dit lequel est le bon. Un humain regarde à côté. Ici aussi : les quatre blocs voisins sont rendus, et la
marche est faite d'un seul tenant sur le bloc et ses voisins, coutures entre blocs comprises ; le niveau que portent les
voisins devient l'ancre du bloc.

## Le voisinage, et l'ancre

Pour chacun des deux blocs de `262` : ses voisins au nord, au sud, à l'ouest et à l'est, sur le pas du bloc, gardés s'ils
sont candidats de la règle de `257`. Le segment réduit et la spire produite rendus sur chacun comme en `257`. La marche de
fenêtre en fenêtre de `260`, sur tous ces chunks à la fois, pour les deux surfaces ; leur différence. ⚠ L'ancre du
voisinage est la médiane de cette différence sur les seuls blocs voisins ; le bloc lui-même n'y entre pas.

## La correction, celle de `264`

Les écarts du bloc à l'ancre du voisinage, le mélange de `264` ajusté au bloc (bruit en zéro, spires glissées à
`± 69,458` voxels), un point corrigé s'il est plus probablement glissé que juste, ramené de son écart. Une passe ; le juge
note la carte du transfert. Pour isoler l'ancre, la même décision est faite aussi avec l'ancre du bloc, sur la même marche.

## Les issues, exclusives, sur la décision avec l'ancre du voisinage, la part de chaque bloc contre sa part avant

- plus haute sur les deux blocs : le voisinage dit quel niveau est le bon ;
- plus haute sur un seul : il le dit sur un bloc seulement ;
- sinon : le voisinage ne dit pas quel niveau est le bon.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : des blocs réguliers, un voisinage lui-même glissé, une boucle, le segment entier.

⚠ AJOUTÉ APRÈS LA PREMIÈRE MESURE, HORS DU VERDICT : `les_derivees`, relues sur les blocs mesurés ; dont, vu après coup
en regardant la carte, le niveau de chaque voisin dans la marche contre l'erreur médiane que le juge y voit.

Usage :
    uv run python src/nappe/le_voisinage_dit_il_quel_niveau_est_le_bon.py --verifier
    uv run python src/nappe/le_voisinage_dit_il_quel_niveau_est_le_bon.py \\
        --json docs/mesures/le_voisinage_dit_il_quel_niveau_est_le_bon.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_marche_corrige_t_elle_la_spire_produite import corriger, la_carte_aux_points, la_part_juste  # noqa: E402
from la_marche_sait_elle_ou_ne_pas_corriger import (corriger_decide, la_decision, le_bilan,  # noqa: E402
                                                    le_melange, les_deux_bosses)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LE_COTE_DU_CHUNK, LE_DOSSIER, LES_JUGES, le_cadre,
                                                            la_marche_du_bloc, les_blocs_candidats, lerreur_jugee,
                                                            lire_la_pile, rendre)
from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, LE_SEGMENT, lire_tifxyz, telecharger  # noqa: E402
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import les_pas_de_fenetre  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_262_A_PUBLIE = LES_MESURES / "la_correction_repetee_converge_t_elle.json"
LES_SURFACES = ("le_segment_reduit", "la_spire_produite")


def les_voisins(by: int, bx: int, candidats: set[tuple[int, int]], cote: int = LE_BLOC) -> list[tuple[int, int]]:
    """Les blocs au nord, au sud, à l'ouest et à l'est, sur le pas du bloc, s'ils sont candidats."""
    return [v for v in ((by - cote, bx), (by + cote, bx), (by, bx - cote), (by, bx + cote)) if v in candidats]


def servir_plusieurs(piles: dict[tuple[int, int], np.ndarray], cote: int = LE_BLOC, chunk: int = LE_COTE_DU_CHUNK):
    """Un lecteur de chunks sur plusieurs piles rendues, chacune d'un bloc aligné sur le pas du bloc : `(bloc, raison)`."""
    def ouvrir(cy: int, cx: int):
        cle = (int(cy) // cote * cote, int(cx) // cote * cote)
        p = piles.get(cle)
        if p is None:
            return None, "hors du rendu"
        y, x = int(cy) - cle[0], int(cx) - cle[1]
        return p[:, y * chunk:(y + 1) * chunk, x * chunk:(x + 1) * chunk], None
    return ouvrir


def la_marche_du_voisinage(piles: dict, y0: int, x0: int, cote: int) -> dict:
    """La marche de fenêtre en fenêtre sur tous les chunks des piles à la fois, dans le carré de côté `cote` en (y0, x0)."""
    lu = les_pas_de_fenetre(servir_plusieurs(piles), y0, x0, cote)
    m = la_marche_du_bloc(lu["h"], lu["v"], y0, x0, cote)
    return {**m, "les_chunks_lus": lu["les_chunks_lus"]}


def lancre_du_voisinage(diff: np.ndarray, y0: int, x0: int, by: int, bx: int, cote: int = LE_BLOC) -> float | None:
    """La médiane de la différence sur le voisinage, le bloc lui-même retiré."""
    d = diff.copy()
    d[by - y0:by - y0 + cote, bx - x0:bx - x0 + cote] = np.nan
    return float(np.nanmedian(d)) if np.isfinite(d).any() else None


def les_quatre(tau0, err, verite, by, bx, diff_bloc, ancre, glissade) -> dict:
    """La décision de `264` et la règle fixe de `261`, avec une ancre donnée, sur un bloc."""
    ecart, dedans = la_carte_aux_points(diff_bloc - ancre, by, bx, tau0.shape)
    ecart = np.where(dedans, ecart, np.nan)
    m = le_melange(diff_bloc - ancre, glissade)
    dec = la_decision(ecart, m)
    t_fixe, fixe = corriger(tau0, ecart)
    return {"lancre_voxels": round(ancre, 4), "le_melange": {k: v for k, v in m.items() if not k.startswith("_")},
            "la_decision": le_bilan(tau0, corriger_decide(tau0, ecart, dec), verite, err, dedans, dec),
            "la_regle_fixe": le_bilan(tau0, t_fixe, verite, err, dedans, fixe)}


def un_voisinage(nom, by, bx, candidats, tau0, err, glissade) -> dict:
    debut = time.monotonic()
    verite = tau0 - err
    blocs = [(by, bx)] + les_voisins(by, bx, candidats)
    r = {"la_rangee": by, "la_colonne": bx, "les_voisins": [list(v) for v in blocs[1:]], "les_rendus": {}}
    for s in LES_SURFACES:
        for (vy, vx) in blocs:
            rendu = rendre(LE_DOSSIER / s / "maillage", LE_DOSSIER / s / f"bloc_{vy}_{vx}", le_cadre(vy, vx, LE_BLOC))
            r["les_rendus"][f"{s}_{vy}_{vx}"] = rendu
            if not rendu["rendue"]:
                return {**r, "decidable": False, "la_raison": f"{s} ne se rend pas sur ({vy}, {vx})"}
    y0, x0, cote = by - LE_BLOC, bx - LE_BLOC, 3 * LE_BLOC
    prof = {}
    for s in LES_SURFACES:
        piles = {v: lire_la_pile(LE_DOSSIER / s / f"bloc_{v[0]}_{v[1]}") for v in blocs}
        m = la_marche_du_voisinage(piles, y0, x0, cote)
        del piles
        prof[s] = m.pop("la_profondeur")
        r[f"la_marche_{s}"] = m
    diff = prof["la_spire_produite"] - prof["le_segment_reduit"]
    diff_bloc = diff[LE_BLOC:2 * LE_BLOC, LE_BLOC:2 * LE_BLOC]
    ext = lancre_du_voisinage(diff, y0, x0, by, bx)
    _, dedans = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), by, bx, tau0.shape)
    r["avant"] = la_part_juste(tau0, verite, dedans)
    if ext is None:
        return {**r, "decidable": False, "la_raison": "aucun voisin ne se relie au bloc"}
    r["lancre_du_voisinage"] = les_quatre(tau0, err, verite, by, bx, diff_bloc, ext, glissade)
    r["lancre_du_bloc"] = les_quatre(tau0, err, verite, by, bx, diff_bloc, float(np.nanmedian(diff_bloc)), glissade)
    r["les_deux_bosses_du_bloc"] = les_deux_bosses(diff_bloc - ext)
    r["les_voisins_juges"] = {}
    for (vy, vx) in blocs[1:]:
        _, dv = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), vy, vx, tau0.shape)
        r["les_voisins_juges"][f"{vy}_{vx}"] = la_part_juste(tau0, verite, dv)
    r["la_difference"] = [[None if not np.isfinite(v) else round(float(v), 2) for v in rr] for rr in diff]
    r["les_secondes"] = round(time.monotonic() - debut, 1)
    r["decidable"] = True
    print(f"{nom} : {r['avant']['la_part_sur_la_bonne_spire']} -> "
          f"{r['lancre_du_voisinage']['la_decision']['apres']['la_part_sur_la_bonne_spire']}, {r['les_secondes']} s",
          flush=True)
    return r


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    d262 = json.loads(CE_QUE_262_A_PUBLIE.read_text())
    glissade = float(d261["le_signe"]["lecart_retrouve_voxels"])
    gy, gx = d257["le_treillis"]
    _, valide, _ = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    candidats = set(les_blocs_candidats(tau0, valide, gy, gx))
    noms = list(d262["les_blocs"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        res = list(pool.map(lambda n: un_voisinage(n, d262["les_blocs"][n]["la_rangee"], d262["les_blocs"][n]["la_colonne"],
                                                   candidats, tau0, err, glissade), noms))
    out = {"la_glissade_voxels": glissade, "les_blocs": dict(zip(noms, res))}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(b.get("decidable") for b in res)
    return out


def les_derivees(r: dict, err: np.ndarray | None = None) -> dict:
    """Ce que les blocs disent ensemble, relu sur leurs résultats : l'écart entre les deux ancres, et les sommes ; vu après
    coup, le niveau de chaque voisin dans la marche et, si `err` est donnée, l'erreur médiane que le juge y voit."""
    out = {"lecart_des_ancres_voxels": {}, "les_deux_blocs": {}}
    ok = {n: b for n, b in r["les_blocs"].items() if b.get("decidable")}
    out["vu_apres_coup"] = {"le_niveau_de_chaque_voisin_voxels": {}, "lerreur_mediane_jugee_de_chaque_voisin_voxels": {}}
    for n, b in ok.items():
        out["lecart_des_ancres_voxels"][n] = round(b["lancre_du_voisinage"]["lancre_voxels"]
                                                   - b["lancre_du_bloc"]["lancre_voxels"], 4)
        diff = np.array([[np.nan if x is None else x for x in rr] for rr in b["la_difference"]], dtype=float)
        y0, x0 = b["la_rangee"] - LE_BLOC, b["la_colonne"] - LE_BLOC
        out["vu_apres_coup"]["le_niveau_de_chaque_voisin_voxels"][n] = {
            f"{vy}_{vx}": round(float(np.nanmedian(diff[vy - y0:vy - y0 + LE_BLOC, vx - x0:vx - x0 + LE_BLOC]))
                                - b["lancre_du_voisinage"]["lancre_voxels"], 4) for vy, vx in b["les_voisins"]}
        if err is not None:
            je = {}
            for vy, vx in [(b["la_rangee"], b["la_colonne"])] + [tuple(q) for q in b["les_voisins"]]:
                _, dv = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), vy, vx, err.shape)
                e = err[dv & np.isfinite(err)]
                je[f"{vy}_{vx}"] = round(float(np.median(e)), 4) if e.size else None
            out["vu_apres_coup"]["lerreur_mediane_jugee_de_chaque_voisin_voxels"][n] = je
    et = lambda d: round(max(d.values()) - min(d.values()), 4) if d else None  # noqa: E731
    out["vu_apres_coup"]["letendue_des_niveaux_des_voisins_voxels"] = {
        n: et(d) for n, d in out["vu_apres_coup"]["le_niveau_de_chaque_voisin_voxels"].items()}
    out["vu_apres_coup"]["letendue_des_erreurs_jugees_des_voisins_voxels"] = {
        n: et({k: x for k, x in d.items() if k != f"{ok[n]['la_rangee']}_{ok[n]['la_colonne']}" and x is not None})
        for n, d in out["vu_apres_coup"]["lerreur_mediane_jugee_de_chaque_voisin_voxels"].items()}
    for ancre in ("lancre_du_voisinage", "lancre_du_bloc"):
        for regle in ("la_decision", "la_regle_fixe"):
            out["les_deux_blocs"][f"{ancre}_{regle}"] = {
                k: sum(b[ancre][regle][k] for b in ok.values())
                for k in ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")}
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    monte = {n: b["lancre_du_voisinage"]["la_decision"]["apres"]["la_part_sur_la_bonne_spire"]
             > b["avant"]["la_part_sur_la_bonne_spire"] for n, b in r["les_blocs"].items()}
    k = sum(monte.values())
    if k == len(monte):
        return {"lissue": "plus haute sur les deux blocs : le voisinage dit quel niveau est le bon", "monte": monte}
    if k == 1:
        return {"lissue": "plus haute sur un seul : il le dit sur un bloc seulement", "monte": monte}
    return {"lissue": "le voisinage ne dit pas quel niveau est le bon", "monte": monte}


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

    cand = {(0, 176), (32, 176), (16, 160)}
    v("★★★ les voisins sont les quatre côtés, gardés s'ils sont candidats",
      lambda: les_voisins(16, 176, cand) == [(0, 176), (32, 176), (16, 160)])
    c = LE_COTE_DU_CHUNK
    p1 = np.zeros((2, 16 * c, 16 * c), dtype=np.uint8)
    p2 = np.ones((2, 16 * c, 16 * c), dtype=np.uint8)
    p2[:, 4 * c:5 * c, 5 * c:6 * c] = 7
    ouvrir = servir_plusieurs({(16, 176): p1, (16, 192): p2})
    v("★★★★ le lecteur de plusieurs piles sert chaque chunk de sa pile, à sa place",
      lambda: ouvrir(16, 176)[0].max() == 0 and ouvrir(20, 197)[0].min() == 7 and ouvrir(16, 192)[0].max() == 1)
    v("★★★ et rien hors des piles", lambda: ouvrir(0, 176)[0] is None and ouvrir(16, 208)[0] is None)
    diff = np.full((48, 48), np.nan)
    diff[16:32, 16:32] = 5.0 + 69.458
    diff[16:32, 0:8] = 5.0
    v("★★★★ l'ancre du voisinage ignore le bloc, même quand le bloc glissé pèse plus que le voisinage",
      lambda: lancre_du_voisinage(diff, 0, 160, 16, 176) == 5.0 and np.nanmedian(diff) > 5.0)
    trou = np.full((48, 48), np.nan)
    trou[16:32, 16:32] = 1.0
    v("★★★ un bloc qu'aucun voisin ne relie n'a pas d'ancre", lambda: lancre_du_voisinage(trou, 0, 160, 16, 176) is None)
    rng = np.random.default_rng(3)
    bloc = rng.normal(0.0, 8.0, (16, 16))
    bloc[:, 6:] += 69.458
    tau_b = np.full((40, 40), 72.0)
    err_b = np.zeros((40, 40))
    _, db = la_carte_aux_points(np.zeros((16, 16)), 16, 16, tau_b.shape)
    for i, j in zip(*np.nonzero(db)):
        x = j * 160 / 128 - 16 - 0.5
        if x >= 5.5:
            tau_b[i, j] += 69.458
            err_b[i, j] = 69.458
    ext = les_quatre(tau_b, err_b, tau_b - err_b, 16, 16, bloc, 0.0, 69.458)
    blo = les_quatre(tau_b, err_b, tau_b - err_b, 16, 16, bloc, float(np.median(bloc)), 69.458)
    v("★★★★ avec l'ancre du dehors, la décision ramène la partie glissée d'un bloc glissé en majorité",
      lambda: ext["la_decision"]["apres"]["la_part_sur_la_bonne_spire"] > 0.9, str(ext["la_decision"]))
    v("★★★★ avec l'ancre du bloc, elle prend la majorité glissée pour la bonne spire",
      lambda: blo["la_decision"]["apres"]["la_part_sur_la_bonne_spire"] < 0.5, str(blo["la_decision"]))

    faux = {"a": {"decidable": True,
                  "lancre_du_voisinage": {"lancre_voxels": 1.5, **{g: {"les_points_corriges": 2, "les_rates_rendus_justes": 2,
                                                                        "les_justes_rendus_rates": 0}
                                                                    for g in ("la_decision", "la_regle_fixe")}},
                  "lancre_du_bloc": {"lancre_voxels": -2.0, **{g: {"les_points_corriges": 1, "les_rates_rendus_justes": 0,
                                                                    "les_justes_rendus_rates": 1}
                                                                for g in ("la_decision", "la_regle_fixe")}}}}
    faux["a"].update({"la_rangee": 16, "la_colonne": 16, "les_voisins": [[0, 16]],
                      "la_difference": [[1.5 + (10.0 if r < 16 else 0.0)] * 48 for r in range(48)]})
    der = les_derivees({"les_blocs": {**faux, "b": faux["a"], "c": {"decidable": False}}})
    v("★★★ les dérivées : l'écart des ancres, et les sommes sur les blocs décidables",
      lambda: der["lecart_des_ancres_voxels"] == {"a": 3.5, "b": 3.5}
      and der["les_deux_blocs"]["lancre_du_voisinage_la_decision"]["les_rates_rendus_justes"] == 4)
    v("★★★ vu après coup : le niveau d'un voisin est sa médiane moins l'ancre du voisinage",
      lambda: der["vu_apres_coup"]["le_niveau_de_chaque_voisin_voxels"]["a"] == {"0_16": 10.0}
      and der["vu_apres_coup"]["letendue_des_niveaux_des_voisins_voxels"]["a"] == 0.0)

    def verdict(a, b):
        return le_verdict({"decidable": True, "les_blocs": {
            "x": {"avant": {"la_part_sur_la_bonne_spire": 0.5},
                  "lancre_du_voisinage": {"la_decision": {"apres": {"la_part_sur_la_bonne_spire": a}}}},
            "y": {"avant": {"la_part_sur_la_bonne_spire": 0.6},
                  "lancre_du_voisinage": {"la_decision": {"apres": {"la_part_sur_la_bonne_spire": b}}}}}})["lissue"]
    v("★★★★ les issues : les deux, un seul, aucun",
      lambda: "dit quel niveau" in verdict(0.6, 0.7) and "un bloc seulement" in verdict(0.6, 0.6)
      and "ne dit pas" in verdict(0.5, 0.6))

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--deriver", action="store_true",
                   help="relire les blocs déjà mesurés dans --json et en refaire les dérivées et le verdict, sans rien rendre")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = json.loads(a.json.read_text()) if a.deriver else mesurer()
    if r.get("decidable"):
        tau0 = np.load(LE_CACHE / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
        err = lerreur_jugee(tau0, [np.load(LE_CACHE / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
        r["les_derivees"] = les_derivees(r, err)
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps({n: {k: b.get(k) for k in ("avant", "lancre_du_voisinage", "lancre_du_bloc")}
                      for n, b in r["les_blocs"].items()}, indent=1, ensure_ascii=False)[:4000])
    print(json.dumps(r["le_verdict"], ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
