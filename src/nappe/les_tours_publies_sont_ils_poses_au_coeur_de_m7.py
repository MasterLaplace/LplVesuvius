"""Les tours publiés 5753_k de PHercParis4 sont-ils posés au cœur des plages de m7, comme une surface qui en serait tirée, ou à côté, comme le tracé humain ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SOMMET D'UN TOUR PUBLIÉ NE SOIT RAPPORTÉ À `m7`. Ce qui était vu avant d'écrire : tout ce que
`296` à `331` publient, dont `R4-F514` et `R4-F516` (la chaîne tirée de `m7` descend les tours `5753_k` un par saut, six d'affilée), et
la réserve que ces tranches portent : si les tours `5753_k` ont eux-mêmes été tirés d'une prédiction comme `m7`, l'accord n'est pas
indépendant. Et `R4-F490` : le tracé humain de PHercParis4 est posé de −16 à +12 voxels du niveau 2 du plus dense de sa feuille selon le
bloc, sur sa face plutôt qu'en son cœur.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST LA RÉSERVE DE `329` ET `330`. Une surface tirée de `m7` passe au centre de ses plages, à un
voxel près ; une surface tracée à la main ou sur le scan n'a pas de raison d'y être. Mesurer où passent les tours publiés dans les plages
de `m7`, et où y passe le tracé humain, dit si la validation de `330` est circulaire.

## Ce qui est fait

- **Les surfaces** : le segment réduit de `296` (le tracé humain de 2023), et les tours `5753_0` à `5753_-3`.
- **Les sommets** : ceux du segment dans les fenêtres de `321` autour des huit graines ; pour chaque tour, ses sommets dans les boîtes
  englobantes de ces fenêtres élargies de 100 voxels, au plus 3000 par tour, pris régulièrement.
- **La lecture** : le long de la normale de chaque sommet, `m7` au niveau 2 sur un pas de chaque côté (18 voxels) ; l'écart du sommet au
  centre de la plage la plus proche, en voxels du niveau 2, comme `300` lit ses plages.

## Les issues

Par surface : l'écart absolu médian au centre de la plage la plus proche, et la part des sommets à au plus un voxel. **Les tours publiés
sont posés au cœur de `m7`** si l'écart médian de chacun est d'au plus un voxel et d'au plus la moitié de celui du tracé humain ; **ils
n'y sont pas** si l'écart médian de l'un d'eux dépasse celui du tracé humain ; **entre les deux** sinon.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : comment les tours `5753_k` ont été faits ; un tour au cœur de `m7` peut avoir été tracé sur le scan,
là où `m7` est juste.

Usage :
    uv run python src/nappe/les_tours_publies_sont_ils_poses_au_coeur_de_m7.py --verifier
    uv run python src/nappe/les_tours_publies_sont_ils_poses_au_coeur_de_m7.py \\
        --json docs/mesures/les_tours_publies_sont_ils_poses_au_coeur_de_m7.json
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
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402

LE_MAXIMUM = 3000
LA_MARGE = 100.0


def les_ecarts_aux_plages(points_l0: np.ndarray, normales: np.ndarray, lire_valeurs, demi: float) -> np.ndarray:
    """Pour chaque sommet, l'écart signé, en voxels du niveau 2, au centre de la plage de `m7` la plus proche le long de sa normale, sur
    `demi` voxels de chaque côté ; NaN s'il n'en voit aucune."""
    if not len(points_l0):
        return np.zeros(0)
    p = points_l0 / m321.LE_FACTEUR
    t = np.arange(-np.floor(demi), np.floor(demi) + 1.0)
    idx = np.floor((p[:, None, :] + t[None, :, None] * normales[:, None, :])[..., ::-1]).astype(np.int64)
    centres = m300.les_plages(lire_valeurs(idx) > 0, t)
    out = np.full(len(p), np.nan)
    for k, c in enumerate(centres):
        if len(c):
            out[k] = c[int(np.argmin(np.abs(c)))]
    return out


def resumer(ecarts: np.ndarray) -> dict:
    vus = np.abs(ecarts[np.isfinite(ecarts)])
    return {"les_sommets": int(len(ecarts)), "la_part_qui_voit_une_plage": round(float(len(vus) / len(ecarts)), 4) if len(ecarts) else None,
            "lecart_median_voxels": round(float(np.median(vus)), 3) if len(vus) else None,
            "la_part_a_un_voxel": round(float((vus <= 1.0).mean()), 4) if len(vus) else None}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    h = d["les_surfaces"]["le_trace_humain"]["lecart_median_voxels"]
    tours = [v["lecart_median_voxels"] for k, v in d["les_surfaces"].items() if k != "le_trace_humain"]
    if h is None or any(x is None for x in tours):
        return {"decidable": False, "lissue": "indécidable : une surface ne voit aucune plage"}
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    tete = f"les tours publiés sont à {f_(min(tours))} à {f_(max(tours))} voxels du centre des plages de m7, le tracé humain à {f_(h)}"
    if max(tours) <= 1.0 and max(tours) <= h / 2:
        suite = "les tours publiés sont posés au cœur de m7"
    elif max(tours) > h:
        suite = "les tours publiés n'y sont pas"
    else:
        suite = "entre les deux"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    ok = sok & snok
    fen = np.zeros_like(ok)
    for i, j in m321.les_graines(seg, sok, snok):
        fen |= m321.la_fenetre(ok.shape, i, j)
    fen &= ok
    pts_h, n_h = seg[fen], sn[fen]
    lo, hi = pts_h.min(axis=0) - LA_MARGE, pts_h.max(axis=0) + LA_MARGE
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    surfaces = {"le_trace_humain": resumer(les_ecarts_aux_plages(pts_h, n_h, lv4, m321.LE_PAS_L2))}
    print("le_trace_humain", surfaces["le_trace_humain"], flush=True)
    for rang in sorted(m329.LES_TOURS, reverse=True):
        tour = m329.lire_un_tour(rang)
        m = ((tour["points"] >= lo) & (tour["points"] <= hi)).all(axis=1)
        pts, nn = tour["points"][m], tour["normales"][m]
        if len(pts) > LE_MAXIMUM:
            k = np.linspace(0, len(pts) - 1, LE_MAXIMUM).round().astype(int)
            pts, nn = pts[k], nn[k]
        surfaces[f"le_tour_{rang}"] = resumer(les_ecarts_aux_plages(pts, nn, lv4, m321.LE_PAS_L2))
        print(rang, surfaces[f"le_tour_{rang}"], flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_maximum": LE_MAXIMUM, "la_marge_voxels": LA_MARGE, "la_demi_portee_l2_voxels": round(m321.LE_PAS_L2, 3)},
         "les_pannes": list(stats4["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats4.items() if k != "pannes"},
         "les_surfaces": surfaces}
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

    pts = np.array([[400.0, 400.0, 400.0], [400.0, 440.0, 408.0], [800.0, 800.0, 800.0]])
    nn = np.tile([0.0, 0.0, 1.0], (3, 1))
    feuille = lambda idx: (idx[..., 0] >= 99) & (idx[..., 0] <= 101) & (idx[..., 2] < 150)  # noqa: E731
    e = les_ecarts_aux_plages(pts, nn, feuille, 18.0)
    v("★★★★ au centre de la plage : 0 ; à 2 voxels du niveau 2 au-dessus : −2 ; hors de m7 : NaN",
      e[0] == 0.0 and e[1] == -2.0 and np.isnan(e[2]), str(e))
    deux = lambda idx: ((idx[..., 0] == 100) | (idx[..., 0] == 110))  # noqa: E731
    e = les_ecarts_aux_plages(np.array([[400.0, 400.0, 432.0]]), nn[:1], deux, 18.0)
    v("★★★★ deux plages : la plus proche, pas la première", e[0] == 2.0, str(e))
    r = resumer(np.array([0.0, -2.0, np.nan, 1.0]))
    v("★★★ le résumé : écart absolu médian et part à un voxel sur les sommets qui voient une plage",
      r["lecart_median_voxels"] == 1.0 and r["la_part_a_un_voxel"] == round(2 / 3, 4) and r["la_part_qui_voit_une_plage"] == 0.75, str(r))
    s = lambda h, *t: {"les_pannes": [], "les_surfaces": dict({"le_trace_humain": {"lecart_median_voxels": h}},  # noqa: E731
                                                              **{f"le_tour_{k}": {"lecart_median_voxels": x} for k, x in enumerate(t)})}
    v("★★★★ des tours à 0,5 et 1 voxel, un tracé à 4 : au cœur", le_verdict(s(4.0, 0.5, 1.0))["lissue"].endswith("au cœur de m7"))
    v("★★★★ un tour à 1 voxel pour un tracé à 1,5 : entre les deux (plus de la moitié)",
      le_verdict(s(1.5, 1.0, 0.5))["lissue"].endswith("entre les deux"))
    v("★★★★ un tour plus loin que le tracé : ils n'y sont pas", le_verdict(s(2.0, 0.5, 3.0))["lissue"].endswith("n'y sont pas"))
    v("★★★ une surface sans plage : indécidable", not le_verdict(s(2.0, None))["decidable"])

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
