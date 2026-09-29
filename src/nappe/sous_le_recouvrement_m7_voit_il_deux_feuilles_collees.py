"""Là où deux tours publiés voisins se recouvrent, autour des graines 1 à 3, la plage de m7 sous eux est-elle deux fois plus épaisse que là où ils sont séparés, deux feuilles collées, ou d'épaisseur simple, un tour posé sur la feuille de son voisin ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE PLAGE DE m7 NE SOIT LUE SOUS UN RECOUVREMENT. Ce qui était vu avant d'écrire : tout ce que
`296` à `341` publient, dont `R4-F527` (autour des graines 1 à 3, deux tours publiés voisins sont à un quart de pas nominal l'un de l'autre
sur 27 à 46 % des sommets du premier qui ont le second en face) et `R4-F518` (les tours publiés passent à un voxel médian du niveau 2 du
centre d'une plage de `m7`) ; `m7` est un masque seuillé à 0,2, et `326` y lisait une feuille comme une plage de 0,15 à 0,25 pas.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P138`. Deux feuilles écrasées l'une contre l'autre sont deux tours légitimes, et une surface
posée là peut les retrouver tous les deux sans erreur ; `m7` les verrait comme une plage plus épaisse qu'une feuille seule. Un tour publié
posé sur la feuille de son voisin est une erreur du référent ; `m7` n'y verrait qu'une feuille, d'épaisseur simple.

## Ce qui est fait

- **Les paires** : autour des graines 1 à 3, celles que `341` dit se recouvrir, dans les mêmes cubes de 1280 voxels.
- **Les deux groupes de sommets** : parmi les sommets du premier tour qui ont le second en face, les recouverts, à au plus un quart de pas
  nominal de lui, et les séparés, à plus d'un demi-pas et au plus un pas et demi ; au plus 600 de chaque, pris régulièrement.
- **La plage** : pour chaque sommet, `m7` au niveau 2 le long de sa normale, sur un pas de chaque côté ; la longueur de la plage qui
  contient le sommet, ou de la plus proche, comme `326`.
- **La règle** : pour chaque paire où les deux groupes ont au moins 50 sommets qui voient une plage, le rapport de la longueur médiane des
  recouverts à celle des séparés ; sur ces paires, la médiane de ce rapport dit **deux feuilles collées** si elle est d'au moins 1,5, **un
  tour posé sur la feuille de son voisin** si elle est d'au plus 1,2, **la plage ne tranche pas** sinon.

## Les issues

L'issue de la tranche : **sous les n paires qui se recouvrent, la plage de m7 là où les tours se recouvrent a en médiane r fois la
longueur de celle d'où ils sont séparés** ; puis l'une des trois lectures déclarées.

## Rapporté à côté, qui ne décide rien

Pour chaque paire, la part des sommets de chaque groupe qui voient une plage, et le nombre médian de plages à moins d'un demi-pas du sommet.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : lequel des deux tours est à la mauvaise place si c'en est un ; et si une probabilité de `m7`, plutôt
que son masque seuillé, séparerait deux feuilles collées.

Usage :
    uv run python src/nappe/sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.py --verifier
    uv run python src/nappe/sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.py \\
        --json docs/mesures/sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.json
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
import la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7 as m326  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas as m337  # noqa: E402

CE_QUE_341_A_PUBLIE = RACINE / "docs" / "mesures" / "les_tours_publies_voisins_se_recouvrent_ils.json"
LES_GRAINES_DU_PROBLEME = (1, 2, 3)
LE_MAXIMUM = 600
LE_MINIMUM = 50
LE_COLLE, LE_SIMPLE = 1.5, 1.2


def les_deux_groupes(ta: dict, tb: dict, centre: np.ndarray, maximum: int = LE_MAXIMUM) -> dict:
    """Les sommets du premier tour, et leurs normales, qui ont le second en face : recouverts à au plus un quart de pas nominal, séparés
    à plus d'un demi-pas et au plus un pas et demi ; au plus `maximum` de chaque, pris régulièrement."""
    a, an = m337.dans_la_boite(ta, centre)
    b, _ = m337.dans_la_boite(tb, centre, maximum=10 ** 9)
    t = np.abs(m321.les_ecarts(a, an, b)) if len(a) and len(b) else np.zeros(0)
    out = {}
    for nom, m in (("recouverts", t <= m321.LE_QUART), ("separes", (t > 2.0 * m321.LE_QUART) & (t <= 1.5 * m321.LE_PAS_L0))):
        k = np.flatnonzero(m)
        if len(k) > maximum:
            k = k[np.linspace(0, len(k) - 1, maximum).round().astype(int)]
        out[nom] = (a[k], an[k])
    return out


def les_plages(points_l0: np.ndarray, normales: np.ndarray, lire_valeurs) -> dict:
    """Pour chaque sommet, `m7` au niveau 2 le long de sa normale sur un pas de chaque côté : la longueur de la plage du sommet, ou de la
    plus proche, et le nombre de plages à moins d'un demi-pas."""
    if not len(points_l0):
        return {"les_longueurs": np.zeros(0), "les_nombres": np.zeros(0, dtype=int), "les_sommets": 0}
    demi = np.floor(m321.LE_PAS_L2)
    t = np.arange(-demi, demi + 1.0)
    p = points_l0 / m321.LE_FACTEUR
    idx = np.floor((p[:, None, :] + t[None, :, None] * normales[:, None, :])[..., ::-1]).astype(np.int64)
    vu = lire_valeurs(idx) > 0
    longueurs, nombres = [], []
    proche = np.abs(t) <= m321.LE_PAS_L2 / 2.0
    for rayon in vu:
        r = m326.la_plage_du_point(rayon, t)
        if r is None:
            continue
        longueurs.append(r[0])
        nombres.append(len(m300.les_plages(rayon[proche][None, :], t[proche])[0]))
    return {"les_longueurs": np.array(longueurs), "les_nombres": np.array(nombres, dtype=int), "les_sommets": int(len(points_l0))}


def le_rapport(recouverts: dict, separes: dict) -> float | None:
    if len(recouverts["les_longueurs"]) < LE_MINIMUM or len(separes["les_longueurs"]) < LE_MINIMUM:
        return None
    return round(float(np.median(recouverts["les_longueurs"]) / np.median(separes["les_longueurs"])), 3)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    rs = [p["le_rapport"] for p in d["les_paires"] if p["le_rapport"] is not None]
    if not rs:
        return {"decidable": False, "lissue": "indécidable : aucune paire mesurable"}
    r = round(float(np.median(rs)), 2)
    tete = (f"sous les {len(rs)} paires qui se recouvrent, la plage de m7 là où les tours se recouvrent a en médiane {r:g} fois la "
            f"longueur de celle d'où ils sont séparés").replace(".", ",")
    suite = ("deux feuilles collées" if r >= LE_COLLE else "un tour posé sur la feuille de son voisin" if r <= LE_SIMPLE
             else "la plage ne tranche pas")
    return {"decidable": True, "n": len(rs), "r": r, "lissue": f"{tete} ; {suite}"}


def resumer(g: dict) -> dict:
    lo = g["les_longueurs"]
    return {"les_sommets": g["les_sommets"], "qui_voient_une_plage": int(len(lo)),
            "la_longueur_mediane_l2": round(float(np.median(lo)), 2) if len(lo) else None,
            "le_nombre_median_de_plages": float(np.median(g["les_nombres"])) if len(lo) else None,
            "les_longueurs_comptees": {str(int(x)): int(c) for x, c in zip(*np.unique(lo, return_counts=True))}}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    d341 = json.loads(CE_QUE_341_A_PUBLIE.read_text())
    a_lire = {(g["le_rang"], tuple(p["les_tours"])) for g in d341["les_graines"] if g["le_rang"] in LES_GRAINES_DU_PROBLEME
              for p in g["les_paires"] if p["se_recouvrent"]}
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    paires = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        for ka, kb in m337.LES_PAIRES:
            if (rang, (ka, kb)) not in a_lire:
                continue
            gr = les_deux_groupes(tours[ka], tours[kb], seg[i, j])
            pl = {nom: les_plages(p, n, lv4) for nom, (p, n) in gr.items()}
            e = {"le_rang": rang, "les_tours": [ka, kb], "les_recouverts": resumer(pl["recouverts"]),
                 "les_separes": resumer(pl["separes"]), "le_rapport": le_rapport(pl["recouverts"], pl["separes"])}
            paires.append(e)
            print(json.dumps(e, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_maximum": LE_MAXIMUM, "le_minimum": LE_MINIMUM, "le_colle": LE_COLLE, "le_simple": LE_SIMPLE},
         "les_pannes": list(stats4["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats4.items() if k != "pannes"},
         "les_paires": paires}
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

    k = np.arange(-400.0, 401.0, 20.0)
    xy = np.stack(np.meshgrid(k, k, indexing="ij"), axis=-1).reshape(-1, 2)
    centre = np.array([1000.0, 1000.0, 400.0])

    def plan(z):
        z = np.broadcast_to(np.asarray(z, dtype=float), (len(xy),))
        return {"points": np.concatenate([xy + 1000.0, z[:, None]], axis=1), "normales": np.tile([0.0, 0.0, 1.0], (len(xy), 1))}

    a = plan(400.0)
    zs = np.where(xy[:, 0] < 0.0, 400.0 + 5.0, 400.0 + 0.9 * m321.LE_PAS_L0)
    gr = les_deux_groupes(a, plan(zs), centre)
    v("★★★★★ les recouverts sont les sommets à un quart de pas du second, les séparés ceux qui en sont à 0,9 pas",
      len(gr["recouverts"][0]) == LE_MAXIMUM and len(gr["separes"][0]) == LE_MAXIMUM and np.all(gr["recouverts"][0][:, 0] < 1060.0)
      and np.all(gr["separes"][0][:, 0] >= 1000.0), f"{len(gr['recouverts'][0])} {len(gr['separes'][0])}")
    zs = np.where(xy[:, 0] < 0.0, 400.0 + 0.4 * m321.LE_PAS_L0, 400.0 + 2.0 * m321.LE_PAS_L0)
    gr = les_deux_groupes(a, plan(zs), centre)
    v("★★★★ un sommet entre un quart et un demi-pas, ou au-delà d'un pas et demi, n'est dans aucun groupe",
      len(gr["recouverts"][0]) == 0 and len(gr["separes"][0]) == 0)

    def feuilles(epaisse_si):
        """Une feuille en z = 100 du niveau 2, de 3 voxels, et de 7 là où `epaisse_si(x)` ; x au niveau 2."""
        def lv(idx):
            z, x = idx[..., 0], idx[..., 2]
            demi = np.where(epaisse_si(x), 3, 1)
            return (np.abs(z - 100) <= demi).astype(float)
        return lv

    pts = np.stack([np.full(10, 1000.0), np.full(10, 1000.0), np.full(10, 400.0)], axis=1)
    nn = np.tile([0.0, 0.0, 1.0], (10, 1))
    fin = les_plages(pts, nn, feuilles(lambda x: x < 0))
    epais = les_plages(pts, nn, feuilles(lambda x: x >= 0))
    v("★★★★★ la plage d'une feuille de 3 voxels a 3 voxels, et 7 sous deux feuilles collées",
      np.all(fin["les_longueurs"] == 3.0) and np.all(epais["les_longueurs"] == 7.0), f"{fin['les_longueurs']} {epais['les_longueurs']}")
    v("★★★ une feuille seule : une plage à moins d'un demi-pas", np.all(fin["les_nombres"] == 1))
    vide = les_plages(pts, nn, lambda idx: np.zeros(idx.shape[:-1]))
    v("★★★ un sommet qui ne voit rien n'a pas de plage", len(vide["les_longueurs"]) == 0 and vide["les_sommets"] == 10)

    g_ = lambda lo, n=60: {"les_longueurs": np.full(n, lo), "les_nombres": np.ones(n, dtype=int)}  # noqa: E731
    v("★★★★ le rapport des longueurs médianes, et rien sous 50 sommets qui voient une plage",
      le_rapport(g_(7.0), g_(3.5)) == 2.0 and le_rapport(g_(7.0, 49), g_(3.5)) is None)

    p_ = lambda r: {"le_rapport": r}  # noqa: E731
    vd = le_verdict({"les_pannes": [], "les_paires": [p_(2.0), p_(1.6), p_(1.4), p_(None)]})
    v("★★★★ médiane 1,6 : deux feuilles collées ; une paire non mesurable ne compte pas",
      vd["lissue"].endswith("deux feuilles collées") and vd["n"] == 3, vd["lissue"])
    vd = le_verdict({"les_pannes": [], "les_paires": [p_(1.0), p_(1.1), p_(1.3)]})
    v("★★★★ médiane 1,1 : un tour posé sur la feuille de son voisin", vd["lissue"].endswith("un tour posé sur la feuille de son voisin"))
    vd = le_verdict({"les_pannes": [], "les_paires": [p_(1.3)]})
    v("★★★ entre les deux : la plage ne tranche pas", vd["lissue"].endswith("la plage ne tranche pas"))
    v("★★★ indécidable si une lecture échoue", not le_verdict({"les_pannes": ["x"], "les_paires": [p_(2.0)]})["decidable"])

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
