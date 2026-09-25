"""La correction sans juge, répétée jusqu'à l'arrêt, tient-elle sur des blocs pris à pas réguliers ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL BLOC NOUVEAU NE SOIT RENDU NI CORRIGÉ. Ce qui était vu avant d'écrire : tout ce
que `257` à `262` publient, dont le nombre de blocs que la règle de `257` admet, **340**.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `262` corrige et s'arrête seul sur deux blocs : celui de `257`, choisi pour
avoir le plus de ratés, et celui de `259`, choisi parce que `m7` y voit le segment. Deux blocs choisis ne disent pas ce que
la procédure fait sur un bloc quelconque. Ici les blocs ne sont pas choisis : ils sont pris à pas réguliers.

## La règle des blocs, déclarée avant le premier rendu

Les blocs candidats de `257` (au pas du bloc, dans l'empreinte, la spire produite partout définie), dans l'ordre de la
rangée puis de la colonne ; les deux blocs déjà étudiés retirés ; **8** pris à pas réguliers, l'indice `⌊(k + ½) · M / 8⌋`
pour `k` de 0 à 7, `M` le nombre qui reste. ⚠ Contrôle : la règle de `257`, refaite sur les mêmes candidats, rend son bloc.

## La procédure, celle de `262`, sans rien y changer

Pour chaque bloc : le segment réduit et la spire produite rendus comme en `257`, la marche de fenêtre en fenêtre de `260` sur
les deux, leur différence ; puis la passe de `261`, répétée comme en `262` jusqu'à ce que plus rien ne soit signalé, ou
après **4** passes. Le signe est celui que `261` a fixé sur la rampe rendue. Le juge ne sert qu'à juger.

## Ce qui se mesure

Sur chaque bloc : les points notés, la part sur la bonne spire avant et après chaque passe, les points signalés, l'écart
type de la différence relue, les ratés rendus justes et les justes rendus ratés, et si la procédure s'est arrêtée seule.
Sur l'ensemble : la part sur la bonne spire de tous les points notés réunis, avant et après.

## Les issues, exclusives, sur la part après la dernière passe contre la part avant toute correction

Seuls comptent les blocs où le juge note au moins un point ; un bloc où la part ne bouge pas ne compte ni pour ni contre.

- plus haute sur chaque bloc : la correction tient partout ;
- plus haute sur plus de blocs qu'elle n'est plus basse, et plus basse sur un au moins : elle tient en majorité, et défait
  ailleurs ;
- sinon : elle ne tient pas.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un autre côté, `ps256`, le segment entier.

Usage :
    uv run python src/nappe/la_correction_tient_elle_sur_des_blocs_reguliers.py --verifier
    uv run python src/nappe/la_correction_tient_elle_sur_des_blocs_reguliers.py \\
        --json docs/mesures/la_correction_tient_elle_sur_des_blocs_reguliers.json
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

from la_correction_repetee_converge_t_elle import LES_PASSES, une_passe  # noqa: E402
from la_marche_corrige_t_elle_la_spire_produite import (la_carte_aux_points, la_part_juste,  # noqa: E402
                                                        le_signalement)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LA_PREDICTION, LE_BLOC,  # noqa: E402
                                                            LE_COTE, LE_DOSSIER, LES_JUGES, ecrire_tifxyz,
                                                            le_bloc, le_cadre, le_maillage_produit,
                                                            les_blocs_candidats, lerreur_jugee, lire_la_pile,
                                                            rendre)
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_marche  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
CE_QUE_262_A_PUBLIE = LES_MESURES / "la_correction_repetee_converge_t_elle.json"
LE_NOMBRE_DE_BLOCS = 8
LES_OUVRIERS = 2


def les_blocs_de_la_regle(candidats: list[tuple[int, int]], exclus: set[tuple[int, int]],
                          combien: int = LE_NOMBRE_DE_BLOCS) -> list[tuple[int, int]]:
    """Les candidats dans l'ordre de la rangée puis de la colonne, les exclus retirés, `combien` pris à pas réguliers."""
    reste = sorted(c for c in candidats if c not in exclus)
    m = len(reste)
    if m <= combien:
        return reste
    return [reste[int(np.floor((k + 0.5) * m / combien))] for k in range(combien)]


def la_boucle(tau0: np.ndarray, diff0: np.ndarray, by: int, bx: int, relire, juger,
              passes: int = LES_PASSES) -> tuple[list[dict], np.ndarray]:
    """Les passes de `262` sur un bloc : `relire(tau, k)` rend la différence relue de la spire de la passe `k`, ou None si
    elle ne se rend pas ; `juger(tau)` rend la part sur la bonne spire. Rend les passes et la dernière carte du transfert."""
    tau, diff, out = tau0, diff0, []
    for k in range(1, passes + 1):
        tau_k, signale, ancre = une_passe(tau, diff, by, bx)
        out.append({"la_passe": k, "lancre_voxels": round(ancre, 4), "les_points_signales": int(signale.sum()),
                    "lecart_type_de_la_difference_lue_voxels": round(float(np.nanstd(diff)), 4),
                    "la_part_sur_la_bonne_spire_apres": juger(tau_k)})
        if signale.sum() == 0:
            break
        tau = tau_k
        if k == passes:
            break
        diff = relire(tau, k)
        if diff is None:
            out[-1]["la_relecture"] = "la spire de la passe ne se rend pas"
            break
    return out, tau


def la_suite(avant: float | None, apres: float | None) -> str | None:
    """Ce qu'un bloc dit : la part après la dernière passe contre la part avant toute correction."""
    if avant is None or apres is None:
        return None
    return "plus haute" if apres > avant else "plus basse" if apres < avant else "égale"


def la_part_reunie(blocs: dict, cle: str) -> float | None:
    """La part sur la bonne spire de tous les points notés des blocs, réunis."""
    n = sum(b[cle]["les_points_notes"] for b in blocs.values() if b.get(cle))
    j = sum(b[cle]["les_points_notes"] * b[cle]["la_part_sur_la_bonne_spire"] for b in blocs.values()
            if b.get(cle) and b[cle]["la_part_sur_la_bonne_spire"] is not None)
    return round(j / n, 4) if n else None


def les_reunis(blocs: dict) -> dict:
    """Ce que les blocs disent ensemble : la part réunie avant et après, ce qui a été rendu juste ou raté, et ce que la
    première passe a signalé parmi les ratés et parmi les justes notés."""
    ok = {n: b for n, b in blocs.items() if b.get("decidable")}
    sig = [b["le_signalement_de_la_premiere_passe"] for b in ok.values()]
    compte = lambda s, n, p: int(round(s[n] * s[p])) if s[p] is not None else 0  # noqa: E731
    rates, justes = sum(s["les_rates"] for s in sig), sum(s["les_justes"] for s in sig)
    rs = sum(compte(s, "les_rates", "la_part_des_rates_signales") for s in sig)
    js = sum(compte(s, "les_justes", "la_part_des_justes_signales") for s in sig)
    return {"les_blocs_decidables": len(ok), "avant": la_part_reunie(ok, "avant"), "apres": la_part_reunie(ok, "apres"),
            "les_points_notes": sum(b["avant"]["les_points_notes"] for b in ok.values()),
            "les_rates_rendus_justes": sum(b["les_rates_rendus_justes"] for b in ok.values()),
            "les_justes_rendus_rates": sum(b["les_justes_rendus_rates"] for b in ok.values()),
            "les_blocs_qui_sarretent_seuls": sum(1 for b in ok.values() if b["sarrete_seule"]),
            "les_gains": {n: round(b["apres"]["la_part_sur_la_bonne_spire"] - b["avant"]["la_part_sur_la_bonne_spire"], 4)
                          for n, b in ok.items() if b["avant"]["la_part_sur_la_bonne_spire"] is not None},
            "la_premiere_passe": {"les_rates": rates, "les_rates_signales": rs, "les_justes": justes,
                                  "les_justes_signales": js,
                                  "la_part_des_rates_signales": round(rs / rates, 4) if rates else None,
                                  "la_part_des_justes_signales": round(js / justes, 4) if justes else None}}


def un_bloc(by: int, bx: int, ref, valide, esp, tau0, err) -> dict:
    debut = time.monotonic()
    verite = tau0 - err
    _, dedans = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), by, bx, tau0.shape)
    cadre = le_cadre(by, bx, LE_BLOC)
    r = {"la_rangee": by, "la_colonne": bx, "les_rendus": {}}
    piles = {}
    for n in ("le_segment_reduit", "la_spire_produite"):
        sortie = LE_DOSSIER / n / f"bloc_{by}_{bx}"
        r["les_rendus"][n] = rendre(LE_DOSSIER / n / "maillage", sortie, cadre)
        if not r["les_rendus"][n]["rendue"]:
            return {**r, "decidable": False, "la_raison": f"{n} ne se rend pas"}
        piles[n] = la_marche(lire_la_pile(sortie), by, bx)["la_profondeur"]
    segment = piles["le_segment_reduit"]

    def relire(tau, k):
        dossier = LE_DOSSIER / f"{'la_spire_corrigee' if k == 1 else f'la_spire_corrigee_passe{k}'}_{by}_{bx}"
        pc, vc = le_maillage_produit(ref, valide, tau)
        tif = ecrire_tifxyz(dossier / "maillage", pc, vc, 1.0 / (esp * LA_MAILLE), f"la_spire_corrigee_passe{k}")
        rendu = rendre(tif, dossier / f"bloc_{by}_{bx}", cadre)
        r["les_rendus"][f"la_passe_{k}"] = rendu
        if not rendu["rendue"]:
            return None
        return la_marche(lire_la_pile(dossier / f"bloc_{by}_{bx}"), by, bx)["la_profondeur"] - segment

    def juger(tau):
        return la_part_juste(tau, verite, dedans)["la_part_sur_la_bonne_spire"]

    diff0 = piles["la_spire_produite"] - segment
    ancre = float(np.nanmedian(diff0))
    ecart, _ = la_carte_aux_points(diff0 - ancre, by, bx, tau0.shape)
    note = dedans & np.isfinite(err)
    with np.errstate(invalid="ignore"):
        rate = np.abs(err) >= DEMI_PAS_EN_VOXELS
        signale1 = dedans & np.isfinite(ecart) & (np.abs(ecart) >= DEMI_PAS_EN_VOXELS)
    passes, tau_f = la_boucle(tau0, diff0, by, bx, relire, juger)
    with np.errstate(invalid="ignore"):
        e_f = tau_f - verite
        r["les_rates_rendus_justes"] = int((note & rate & (np.abs(e_f) < DEMI_PAS_EN_VOXELS)).sum())
        r["les_justes_rendus_rates"] = int((note & ~rate & (np.abs(e_f) >= DEMI_PAS_EN_VOXELS)).sum())
    r.update({"les_points_du_bloc": int(dedans.sum()), "le_signalement_de_la_premiere_passe":
              le_signalement(signale1, rate, note), "avant": la_part_juste(tau0, verite, dedans),
              "apres": la_part_juste(tau_f, verite, dedans), "les_passes": passes,
              "sarrete_seule": passes[-1]["les_points_signales"] == 0,
              "les_chunks_relies": int(np.isfinite(diff0).sum())})
    r["la_suite"] = la_suite(r["avant"]["la_part_sur_la_bonne_spire"], r["apres"]["la_part_sur_la_bonne_spire"])
    r["les_secondes"] = round(time.monotonic() - debut, 1)
    r["decidable"] = True
    print(f"bloc ({by}, {bx}) : {r['avant']['la_part_sur_la_bonne_spire']} -> {r['apres']['la_part_sur_la_bonne_spire']}"
          f" sur {r['avant']['les_points_notes']} points, {len(passes)} passes, {r['les_secondes']} s", flush=True)
    return r


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    d262 = json.loads(CE_QUE_262_A_PUBLIE.read_text())
    gy, gx = d257["le_treillis"]
    ref, valide, esp = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    candidats = les_blocs_candidats(tau0, valide, gy, gx)
    b257 = le_bloc(tau0, err, valide, gy, gx)
    exclus = {(b["la_rangee"], b["la_colonne"]) for b in d262["les_blocs"].values()}
    out = {"les_blocs_candidats": len(candidats),
           "le_controle": {"le_bloc_de_la_regle_de_257": [b257.get("la_rangee"), b257.get("la_colonne")],
                           "le_bloc_publie": [d257["le_bloc"]["la_rangee"], d257["le_bloc"]["la_colonne"]]},
           "les_exclus": sorted([list(e) for e in exclus]), "les_passes_au_plus": LES_PASSES}
    if out["le_controle"]["le_bloc_de_la_regle_de_257"] != out["le_controle"]["le_bloc_publie"]:
        return {**out, "decidable": False, "la_raison": "la règle de 257 refaite ne rend pas son bloc"}
    choisis = les_blocs_de_la_regle(candidats, exclus)
    out["les_blocs_choisis"] = [list(c) for c in choisis]
    with ThreadPoolExecutor(max_workers=LES_OUVRIERS) as pool:
        res = list(pool.map(lambda c: un_bloc(c[0], c[1], ref, valide, esp, tau0, err), choisis))
    out["les_blocs"] = {f"{by}_{bx}": r for (by, bx), r in zip(choisis, res)}
    out["reunis"] = les_reunis(out["les_blocs"])
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = out["reunis"]["les_blocs_decidables"] == len(choisis)
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    suites = {n: b["la_suite"] for n, b in r["les_blocs"].items() if b.get("la_suite") is not None}
    haut = sum(s == "plus haute" for s in suites.values())
    bas = sum(s == "plus basse" for s in suites.values())
    comptes = {"plus haute": haut, "plus basse": bas, "égale": len(suites) - haut - bas}
    if suites and haut == len(suites):
        return {"lissue": "plus haute sur chaque bloc : la correction tient partout", "les_comptes": comptes}
    if haut > bas and bas >= 1:
        return {"lissue": "plus haute sur plus de blocs qu'elle n'est plus basse : elle tient en majorité, et défait "
                          "ailleurs", "les_comptes": comptes}
    return {"lissue": "elle ne tient pas", "les_comptes": comptes}


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

    cands = [(r, c) for r in range(0, 160, 16) for c in range(0, 64, 16)]
    pris = les_blocs_de_la_regle(cands[::-1], {(0, 0), (16, 16)})
    v("★★★★ la règle prend huit blocs distincts, à pas réguliers, dans l'ordre, sans les exclus",
      lambda: len(pris) == 8 and len(set(pris)) == 8 and pris == sorted(pris)
      and not {(0, 0), (16, 16)} & set(pris), str(pris))
    reste = sorted(c for c in cands if c not in {(0, 0), (16, 16)})
    v("★★★ le pas est régulier : le k-ième est à l'indice ⌊(k + ½) · M / 8⌋",
      lambda: pris == [reste[int((k + 0.5) * len(reste) / 8)] for k in range(8)])
    v("★★★ moins de candidats que de blocs : tous sont pris", lambda: les_blocs_de_la_regle(cands[:5], set()) == cands[:5])

    tau = np.full((40, 40), 72.0)
    diff = np.zeros((16, 16))
    diff[8:, 8:] = 60.0
    lus = []

    def relire_plat(t, k):
        lus.append(k)
        return np.zeros((16, 16))
    passes, tf = la_boucle(tau, diff, 16, 16, relire_plat, lambda t: 0.5)
    v("★★★★ la boucle s'arrête dès qu'une passe ne signale rien", lambda: len(passes) == 2 and lus == [1]
      and passes[0]["les_points_signales"] > 0 and passes[1]["les_points_signales"] == 0, str(len(passes)))
    v("★★★ la dernière carte est celle de la passe qui a corrigé", lambda: np.allclose(tf[tf != 72.0], 12.0))

    def relire_toujours(t, k):
        d = np.zeros((16, 16))
        d[8:, 8:] = 60.0
        return d
    passes4, _ = la_boucle(tau, diff, 16, 16, relire_toujours, lambda t: 0.5)
    v("★★★★ la boucle s'arrête après quatre passes même si la marche signale encore",
      lambda: len(passes4) == LES_PASSES and passes4[-1]["les_points_signales"] > 0)
    passesn, _ = la_boucle(tau, diff, 16, 16, lambda t, k: None, lambda t: 0.5)
    v("★★★ une spire qui ne se rend pas arrête la boucle et le dit",
      lambda: len(passesn) == 1 and "la_relecture" in passesn[0])

    v("★★★ la suite d'un bloc : plus haute, plus basse, égale, ou rien sans juge",
      lambda: la_suite(0.5, 0.6) == "plus haute" and la_suite(0.6, 0.5) == "plus basse"
      and la_suite(0.5, 0.5) == "égale" and la_suite(None, 0.5) is None)
    blocs = {"a": {"avant": {"les_points_notes": 100, "la_part_sur_la_bonne_spire": 0.5}},
             "b": {"avant": {"les_points_notes": 300, "la_part_sur_la_bonne_spire": 0.9}}}
    v("★★★★ la part réunie pèse chaque bloc par ses points notés", lambda: la_part_reunie(blocs, "avant") == 0.8)

    sig = lambda r, pr, j, pj: {"les_rates": r, "la_part_des_rates_signales": pr, "les_justes": j,  # noqa: E731
                                "la_part_des_justes_signales": pj}
    b1 = {"decidable": True, "avant": {"les_points_notes": 10, "la_part_sur_la_bonne_spire": 0.5},
          "apres": {"les_points_notes": 10, "la_part_sur_la_bonne_spire": 0.7}, "les_rates_rendus_justes": 2,
          "les_justes_rendus_rates": 0, "sarrete_seule": True, "le_signalement_de_la_premiere_passe": sig(5, 0.6, 5, 0.2)}
    b2 = {**b1, "sarrete_seule": False, "le_signalement_de_la_premiere_passe": sig(0, None, 10, 0.1)}
    rr = les_reunis({"a": b1, "b": b2, "c": {"decidable": False}})
    v("★★★★ la réunion compte les signalés de la première passe, et laisse de côté un bloc indécidable",
      lambda: rr["les_blocs_decidables"] == 2 and rr["la_premiere_passe"]["les_rates_signales"] == 3
      and rr["la_premiere_passe"]["les_justes_signales"] == 2 and rr["la_premiere_passe"]["la_part_des_justes_signales"]
      == round(2 / 15, 4) and rr["les_blocs_qui_sarretent_seuls"] == 1, str(rr))
    v("★★★ le gain d'un bloc est sa part après moins sa part avant", lambda: rr["les_gains"] == {"a": 0.2, "b": 0.2})

    def verdict(*s):
        return le_verdict({"decidable": True, "les_blocs": {str(i): {"la_suite": x} for i, x in enumerate(s)}})["lissue"]
    v("★★★★ les issues : partout, en majorité, ne tient pas",
      lambda: "partout" in verdict("plus haute", "plus haute")
      and "en majorité" in verdict("plus haute", "plus haute", "plus basse")
      and "ne tient pas" in verdict("plus haute", "plus basse")
      and "ne tient pas" in verdict("égale", "égale"))
    v("★★★ un bloc égal ne compte ni pour ni contre, un bloc sans juge non plus",
      lambda: "partout" in verdict("plus haute", None) and "en majorité" in verdict("plus haute", "plus haute", "égale",
                                                                                    "plus basse"))

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--reunir", action="store_true",
                   help="relire les blocs déjà mesurés dans --json et en refaire la réunion et le verdict, sans rien rendre")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reunir:
        r = json.loads(a.json.read_text())
        r["reunis"] = les_reunis(r["les_blocs"])
    else:
        r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte[:3000])
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
