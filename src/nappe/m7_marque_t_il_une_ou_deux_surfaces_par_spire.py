"""Le long des rayons des plans de 301, m7 marque-t-il une surface par spire, ou deux, les deux couches ou les deux faces d'une même feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL ÉCART ENTRE SURFACES DE m7 NE SOIT COMPTÉ. Ce qui était vu avant d'écrire : tout ce
que `300` à `311` publient, dont `304` (les sauts de 12 à 13,5 voxels des nappes du vote relient deux plages de `m7` séparées par un
creux du scan) et `311` (le profil moyen du scan sur 6 mm ne garde pas la périodicité de l'empilement).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST UNE LECTURE DE `R4-P112` PAR `m7`. Le scan moyenné efface ce qui dépasse le premier voisin ;
`m7`, lui, est binaire, et le long d'un rayon ses plages se comptent sans moyenne. Si `m7` marque une surface par spire, ses plages
se suivent au pas du rouleau, 20 voxels ; s'il en marque deux par spire, elles viennent par paires, un écart court puis un écart
long dont la somme vaut le pas ; si l'empilement est écrasé, elles se suivent serrées.

## Ce qui est fait

- **Les rayons** : ceux des plans de `300` sur les huit graines de `301`, 65 × 65 rayons au pas de 10 voxels, le long de la normale
  de la graine, de −60 à +60 voxels, trois pas de chaque côté.
- **Les plages** : les centres des plages allumées de `m7` le long de chaque rayon, comme `300` les lit.
- **Les écarts** : entre centres consécutifs sur un même rayon. Un écart est **au pas** entre 15 et 25 voxels (0,75 à 1,25 pas),
  **court** sous 15, **long** au-delà de 25 ; un écart court **fait paire** avec l'écart qui le suit si leur somme est entre 17 et 23
  voxels (0,85 à 1,15 pas).
- **La lecture, par graine** : **une surface par spire** si au moins la moitié des écarts sont au pas ; **deux surfaces par spire**
  si au moins la moitié sont courts et qu'au moins la moitié des courts font paire ; **serrées** si au moins la moitié sont courts
  et que moins de la moitié font paire ; **mêlées** sinon ; **non lue** sous 100 écarts.

## L'issue

**Sur k des graines lues, m7 marque deux surfaces par spire**, avec, à côté, le compte des autres lectures.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que sont les deux surfaces d'une paire, faces ou couches ; ni si le scan les voit comme
`m7` les voit.

Usage :
    uv run python src/nappe/m7_marque_t_il_une_ou_deux_surfaces_par_spire.py --verifier
    uv run python src/nappe/m7_marque_t_il_une_ou_deux_surfaces_par_spire.py \\
        --json docs/mesures/m7_marque_t_il_une_ou_deux_surfaces_par_spire.json
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

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402

LA_PORTEE = 60
LE_MINIMUM_DECARTS = 100


def les_ecarts(centres: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Les écarts entre centres consécutifs de chaque rayon, et pour chacun l'écart qui le suit sur le même rayon (NaN s'il n'y en
    a pas)."""
    e, suivant = [], []
    for c in centres:
        d = np.diff(np.sort(c))
        e.extend(d.tolist())
        suivant.extend(list(d[1:]) + [np.nan] if len(d) else [])
    return np.asarray(e, dtype=float), np.asarray(suivant, dtype=float)


def la_lecture(e: np.ndarray, suivant: np.ndarray, pas: float = m300.LE_PAS_0358) -> dict:
    n = len(e)
    if n < LE_MINIMUM_DECARTS:
        return {"la_lecture": "non lue", "les_ecarts": n}
    au_pas = (e >= 0.75 * pas) & (e <= 1.25 * pas)
    court = e < 0.75 * pas
    somme = e + suivant
    paire = court & np.isfinite(suivant) & (somme >= 0.85 * pas) & (somme <= 1.15 * pas)
    part = lambda m: round(float(m.mean()), 4)  # noqa: E731
    parts = {"les_ecarts": n, "au_pas": part(au_pas), "courts": part(court), "longs": part(e > 1.25 * pas),
             "des_courts_font_paire": round(float(paire.sum() / court.sum()), 4) if court.any() else None,
             "lecart_median": round(float(np.median(e)), 2)}
    if parts["au_pas"] >= 0.5:
        lec = "une surface par spire"
    elif parts["courts"] >= 0.5:
        lec = "deux surfaces par spire" if parts["des_courts_font_paire"] >= 0.5 else "serrées"
    else:
        lec = "mêlées"
    return dict(parts, la_lecture=lec)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lues = [g for g in d["les_graines"] if g["la_lecture"] != "non lue"]
    if not lues:
        return {"decidable": False, "lissue": "indécidable : aucune graine lue"}
    compte = {k: sum(1 for g in lues if g["la_lecture"] == k)
              for k in ("une surface par spire", "deux surfaces par spire", "serrées", "mêlées")}
    return {"decidable": True, "k": compte["deux surfaces par spire"], "n": len(lues), "les_lectures": compte,
            "lissue": f"sur {compte['deux surfaces par spire']} des {len(lues)} graines lues, m7 marque deux surfaces par spire"}


def mesurer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs

    from zarr_depth import array_meta

    t0 = time.monotonic()
    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    graines = []
    t = np.arange(-float(LA_PORTEE), float(LA_PORTEE) + 1.0)
    for rang, g in enumerate(m301.les_graines_neuves(), 1):
        nz, ny, nx = g["normale_zyx"]
        grille, n = m300.le_plan((g["x"], g["y"], g["z"]), (nx, ny, nz))
        p = grille.reshape(-1, 3)
        idx = np.floor((p[:, None, :] + t[None, :, None] * n[None, None, :])[..., ::-1]).astype(np.int64)
        vu = lire_les_valeurs(idx, pred, lire_) > 0
        e, suivant = les_ecarts(m300.les_plages(vu, t))
        hist = np.histogram(e, bins=np.arange(0, 2 * LA_PORTEE + 5, 2.5))[0] if len(e) else np.zeros(0)
        graines.append(dict(la_lecture(e, suivant), le_rang=rang, la_graine=[g["x"], g["y"], g["z"]],
                            les_rayons_qui_voient=int(vu.any(axis=1).sum()), lhistogramme=[int(x) for x in hist]))
        print(json.dumps({k: v for k, v in graines[-1].items() if k != "lhistogramme"}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_portee_voxels": LA_PORTEE, "le_pas_voxels": m300.LE_PAS_0358,
                            "le_minimum_decarts": LE_MINIMUM_DECARTS, "la_classe_de_lhistogramme_voxels": 2.5},
         "les_pannes": list(stats["pannes"]), "les_graines": graines}
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

    e, s = les_ecarts([np.array([0.0, 12.0, 20.0]), np.array([5.0])])
    v("★★★ les écarts d'un rayon, et l'écart qui suit chacun", np.allclose(e, [12.0, 8.0])
      and s[0] == 8.0 and np.isnan(s[1]), f"{e} {s}")
    un = [np.arange(-60.0, 61.0, 20.0)] * 30
    v("★★★★ des plages au pas : une surface par spire", la_lecture(*les_ecarts(un))["la_lecture"] == "une surface par spire")
    deux = [np.array([-60, -47.5, -40, -27.5, -20, -7.5, 0, 12.5, 20, 32.5, 40, 52.5, 60.0])] * 20
    v("★★★★ des plages par paires, 12,5 puis 7,5 : deux surfaces par spire",
      la_lecture(*les_ecarts(deux))["la_lecture"] == "deux surfaces par spire", str(la_lecture(*les_ecarts(deux))))
    serre = [np.arange(-60.0, 61.0, 12.5)] * 20
    v("★★★★ des plages à 12,5 : serrées", la_lecture(*les_ecarts(serre))["la_lecture"] == "serrées")
    mele = [np.array([0.0, 30.0, 60.0, 70.0])] * 60
    v("★★★ des écarts longs et courts sans majorité : mêlées", la_lecture(*les_ecarts(mele))["la_lecture"] == "mêlées")
    tiers = [np.array([0.0, 20.0, 32.5, 40.0])] * 40
    v("★★★ un tiers d'écarts au pas ne fait pas une majorité : les paires l'emportent",
      la_lecture(*les_ecarts(tiers))["la_lecture"] == "deux surfaces par spire")
    v("★★★ sous 100 écarts : non lue", la_lecture(*les_ecarts([np.array([0.0, 20.0])] * 50))["la_lecture"] == "non lue")
    vd = le_verdict({"les_graines": [{"la_lecture": "deux surfaces par spire"}, {"la_lecture": "non lue"},
                                     {"la_lecture": "une surface par spire"}]})
    v("★★★ l'issue : k des graines lues", vd["k"] == 1 and vd["n"] == 2 and vd["lissue"].startswith("sur 1 des 2 graines"))
    v("★★★ indécidable sans graine lue, ou si une lecture échoue",
      not le_verdict({"les_graines": [{"la_lecture": "non lue"}]})["decidable"] and not le_verdict({"les_pannes": ["x"]})["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
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
