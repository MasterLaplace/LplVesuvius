"""La correction sans juge de `261`, répétée, continue-t-elle de ramener la spire produite sur la bonne spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SECONDE PASSE NE SOIT FAITE NI JUGÉE. Ce qui était vu avant d'écrire : tout ce que
`261` publie, dont la différence des marches relue après la première passe, qui sépare encore 0,4056 et 0,3808 des paires
que le juge sépare encore.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Une procédure qui remplace l'humain doit savoir quand s'arrêter. Si une
passe corrige, la suivante corrige-t-elle encore, ou se met-elle à défaire ce que la première avait fait ?

## La règle, la même que `261`, répétée

À chaque passe : la marche de fenêtre en fenêtre de la spire de la passe, moins celle du segment ; l'ancre à sa médiane ; les
points de la maille à un demi-feuillet ou plus de l'ancre ramenés de leur écart ; la spire rendue et relue. La première passe
est celle de `261`, refaite à l'identique, et contrôlée contre ce qu'il publie. ⚠ Arrêt déclaré : quand plus aucun point n'est
signalé, ou après **4** passes.

## Ce qui se mesure, le juge ne servant qu'à juger

À chaque passe et sur chaque bloc : les points signalés, la part des points notés sur la bonne spire, et l'écart type de la
différence des marches.

## Les issues, exclusives, sur la part après la dernière passe comparée à celle après la première

- plus haute sur les deux blocs : répéter corrige encore ;
- plus basse sur un bloc au moins : répéter défait ;
- sinon : une passe suffit.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un autre côté, `ps256`, ni ce qu'une ancre fausse ferait en se répétant.

Usage :
    uv run python src/nappe/la_correction_repetee_converge_t_elle.py --verifier
    uv run python src/nappe/la_correction_repetee_converge_t_elle.py \\
        --json docs/mesures/la_correction_repetee_converge_t_elle.json
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

from la_marche_corrige_t_elle_la_spire_produite import (CE_QUE_260_A_PUBLIE, corriger,  # noqa: E402
                                                        la_carte_aux_points, la_part_juste)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LA_PREDICTION, LE_BLOC,  # noqa: E402
                                                            LE_COTE, LE_DOSSIER, LES_JUGES, ecrire_tifxyz,
                                                            le_cadre, le_maillage_produit, lerreur_jugee,
                                                            lire_la_pile, rendre)
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille, la_marche  # noqa: E402

CE_QUE_261_A_PUBLIE = RACINE / "docs" / "mesures" / "la_marche_corrige_t_elle_la_spire_produite.json"
LES_PASSES = 4


def une_passe(tau: np.ndarray, diff: np.ndarray, by: int, bx: int) -> tuple[np.ndarray, np.ndarray, float]:
    """Une passe de la règle : l'ancre à la médiane, l'écart porté aux points du bloc, les signalés ramenés."""
    ancre = float(np.nanmedian(diff))
    ecart, dedans = la_carte_aux_points(diff - ancre, by, bx, tau.shape)
    t, signale = corriger(tau, np.where(dedans, ecart, np.nan))
    return t, signale & dedans, ancre


def la_suite(parts: list[float | None]) -> str:
    """L'issue déclarée, pour un bloc : la part après la dernière passe contre celle après la première."""
    p = [x for x in parts if x is not None]
    if len(p) < 2:
        return "une passe"
    if p[-1] > p[0]:
        return "plus haute"
    if p[-1] < p[0]:
        return "plus basse"
    return "égale"


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d260 = json.loads(CE_QUE_260_A_PUBLIE.read_text())
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    dd = telecharger(LE_SEGMENT, cache)
    ref, valide, esp = lire_tifxyz(dd)
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    verite = tau0 - err
    out = {"les_passes_au_plus": LES_PASSES, "les_blocs": {}}
    for nom, b in d260["les_blocs"].items():
        by, bx = b["la_rangee"], b["la_colonne"]
        _, dedans = la_carte_aux_points(np.zeros((LE_BLOC, LE_BLOC)), by, bx, tau0.shape)
        segment = la_marche(lire_la_pile(LE_DOSSIER / "le_segment_reduit" / f"bloc_{by}_{bx}"), by, bx)["la_profondeur"]
        tau, diff = tau0, la_grille(b["les_cartes"]["la_difference"])
        passes = []
        for k in range(1, LES_PASSES + 1):
            tau_k, signale, ancre = une_passe(tau, diff, by, bx)
            juste = la_part_juste(tau_k, verite, dedans)
            p = {"la_passe": k, "lancre_voxels": round(ancre, 4), "les_points_signales": int(signale.sum()),
                 "lecart_type_de_la_difference_lue_voxels": round(float(np.nanstd(diff)), 4),
                 "la_part_sur_la_bonne_spire_apres": juste["la_part_sur_la_bonne_spire"]}
            if k == 1:
                p["la_part_de_261"] = d261["les_blocs"][nom]["apres"]["la_part_sur_la_bonne_spire"]
                p["la_part_avant"] = la_part_juste(tau0, verite, dedans)["la_part_sur_la_bonne_spire"]
            passes.append(p)
            if signale.sum() == 0:
                break
            tau = tau_k
            # ⚠ La première passe est celle de `261` : sa pile est déjà rendue, et elle n'est ni réécrite ni refaite.
            dossier = LE_DOSSIER / f"{'la_spire_corrigee' if k == 1 else f'la_spire_corrigee_passe{k}'}_{by}_{bx}"
            tif = dossier / "maillage"
            if not (dossier / f"bloc_{by}_{bx}").is_dir():
                pc, vc = le_maillage_produit(ref, valide, tau)
                tif = ecrire_tifxyz(tif, pc, vc, 1.0 / (esp * LA_MAILLE), f"la_spire_corrigee_passe{k}")
            rendu = rendre(tif, dossier / f"bloc_{by}_{bx}", le_cadre(by, bx, LE_BLOC))
            p["le_rendu"] = rendu
            if not rendu["rendue"]:
                break
            diff = la_marche(lire_la_pile(dossier / f"bloc_{by}_{bx}"), by, bx)["la_profondeur"] - segment
        out["les_blocs"][nom] = {"la_rangee": by, "la_colonne": bx, "les_passes": passes,
                                 "la_suite": la_suite([q["la_part_sur_la_bonne_spire_apres"] for q in passes])}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = True
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    suites = {n: b["la_suite"] for n, b in r["les_blocs"].items()}
    if all(s == "plus haute" for s in suites.values()):
        return {"lissue": "plus haute sur les deux blocs : répéter corrige encore", "les_suites": suites}
    if any(s == "plus basse" for s in suites.values()):
        return {"lissue": "plus basse sur un bloc au moins : répéter défait", "les_suites": suites}
    return {"lissue": "une passe suffit", "les_suites": suites}


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

    tau = np.full((40, 40), 72.0)
    diff = np.zeros((16, 16))
    diff[8:, 8:] = 60.0
    t1, s1, a1 = une_passe(tau, diff, 16, 16)
    v("★★★★ une passe ramène de leur écart à la médiane les points du bloc qui s'en écartent d'un demi-feuillet",
      lambda: a1 == 0.0 and s1.sum() > 0 and np.allclose(t1[s1], 12.0) and np.allclose(t1[~s1], 72.0), str(s1.sum()))
    v("★★★ rien hors du bloc ne bouge",
      lambda: np.array_equal(t1[:12], tau[:12]) and np.array_equal(t1[:, :12], tau[:, :12]))
    t2, s2, _ = une_passe(tau, np.full((16, 16), 5.0), 16, 16)
    v("★★★ une différence plate ne signale rien", lambda: s2.sum() == 0 and np.array_equal(t2, tau))
    v("★★★★ l'issue compare la dernière passe à la première",
      lambda: la_suite([0.6, 0.65, 0.7]) == "plus haute" and la_suite([0.6, 0.7, 0.55]) == "plus basse"
      and la_suite([0.6, 0.6]) == "égale" and la_suite([0.6]) == "une passe")
    v("★★★★ le verdict : une baisse sur un bloc l'emporte sur une hausse sur l'autre",
      lambda: "défait" in le_verdict({"decidable": True, "les_blocs": {"a": {"la_suite": "plus haute"},
                                                                         "b": {"la_suite": "plus basse"}}})["lissue"])
    v("★★★ deux hausses : répéter corrige encore",
      lambda: "corrige encore" in le_verdict({"decidable": True, "les_blocs": {"a": {"la_suite": "plus haute"},
                                                                                "b": {"la_suite": "plus haute"}}})["lissue"])

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
    print(texte[:3000])
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
