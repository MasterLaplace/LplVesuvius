"""Là où la nappe qui croît de PHerc0358 est plate, est-elle posée dans un bloc de m7 plutôt que sur une feuille ? L'épaisseur de la plage de m7 sous chaque nappe, sur PHerc0358 et sur PHercParis4.

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA LONGUEUR D'UNE PLAGE DE m7 NE SOIT LUE SOUS UNE NAPPE. Ce qui était vu avant d'écrire : tout ce
que `296` à `325` publient, dont `R4-F510` : les nappes qui croissent des graines 1, 2 et 5 de PHerc0358 ont 90,58, 68,41 et 99,07 %
de leurs points au même décalage de leur plan (−10, 0 et 13 voxels), et aucun de leurs points ne voit de feuille après la sienne.
La nappe de la graine 1 est posée à −10 voxels d'un plan cherché sur ±30 : une plage de `m7` qui irait de −30 à +10 y aurait son centre.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P124`. Une feuille de `m7` est une plage mince le long de la normale ; si, sous une nappe
plate, la plage remplit la portée, la nappe est posée au milieu d'un bloc, pas sur une feuille, et un rouleau sans tracé peut le voir
seul : c'est un critère de départ.

## Ce qui est fait

- **Les graines et la nappe** : celles de `325`, sans rien y changer ; les nappes de PHerc0358 redonnent `305`.
- **La plage de la nappe** : pour chaque point posé, le long de la normale recalculée de la nappe, `m7` sur trois pas de chaque côté ;
  la plage est la suite de voxels où `m7` voit une feuille qui contient le voxel du point, ou, s'il n'en voit pas, la plus proche. Sa
  longueur est comptée en pas du rouleau ; elle **remplit la portée** si elle touche les deux bouts du rayon.

## Les issues

Par nappe, **elle est posée dans un bloc** si la longueur médiane de sa plage atteint un pas ; **sur une feuille** si elle ne dépasse pas
un demi-pas ; **mêlée** entre les deux ; **non lue** si moins de la moitié de ses points ont une plage. L'issue de la tranche : **sur
PHerc0358, k des huit nappes sont posées dans un bloc, et sur PHercParis4, m.**

## Rapporté à côté, qui ne décide rien

La part des points dont la plage remplit la portée ; et, pour chaque nappe, sa platitude de `325`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que le scan montre dans un bloc de `m7`, ni pourquoi `m7` y est plein.

Usage :
    uv run python src/nappe/la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.py --verifier
    uv run python src/nappe/la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.py \\
        --json docs/mesures/la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.json
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

import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import a_quelle_distance_m7_montre_t_il_la_feuille_suivante as m325  # noqa: E402

LA_PORTEE_EN_PAS = 3.0
LE_BLOC, LA_FEUILLE = 1.0, 0.5
LA_PART_LUE = 0.5
LE_MAXIMUM_DE_POINTS = 1200


def la_plage_du_point(vu: np.ndarray, t: np.ndarray) -> tuple[float, bool] | None:
    """La longueur, en voxels, de la plage vue qui contient t = 0, ou de la plus proche ; et si elle touche les deux bouts du rayon."""
    if not vu.any():
        return None
    bords = np.flatnonzero(np.diff(np.concatenate([[0], vu.astype(np.int8), [0]])))
    plages = list(zip(bords[::2], bords[1::2]))
    zero = int(np.argmin(np.abs(t)))
    dedans = [(a, b) for a, b in plages if a <= zero < b]
    if dedans:
        a, b = dedans[0]
    else:
        a, b = min(plages, key=lambda p: min(abs(p[0] - zero), abs(p[1] - 1 - zero)))
    return float(b - a), bool(a == 0 and b == len(vu))


def la_nappe(longueurs: list, remplies: list, n_points: int, pas_du_rouleau: float) -> dict:
    """Ce que les plages sous une nappe disent d'elle : longueur médiane en pas, part qui remplit la portée, et la lecture."""
    part = len(longueurs) / n_points if n_points else 0.0
    med = float(np.median(longueurs)) / pas_du_rouleau if longueurs else None
    if part < LA_PART_LUE or med is None:
        lecture = "non lue"
    elif med >= LE_BLOC:
        lecture = "dans un bloc"
    elif med <= LA_FEUILLE:
        lecture = "sur une feuille"
    else:
        lecture = "mêlée"
    return {"la_part_des_points_avec_une_plage": round(part, 4), "la_longueur_mediane_en_pas": None if med is None else round(med, 3),
            "la_part_qui_remplit_la_portee": round(float(np.mean(remplies)), 4) if remplies else None, "la_lecture": lecture}


def lire_les_plages(nappe: dict, lire_valeurs, pas_du_rouleau: float) -> dict:
    """Les plages de `m7` sous les points posés d'une nappe, le long de sa normale recalculée, sur trois pas de chaque côté ; au plus
    `LE_MAXIMUM_DE_POINTS` points, pris régulièrement dans l'ordre de la grille."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    nn, nok = les_normales(nappe["la_nappe"], nappe["valide"])
    m = nappe["valide"] & nok
    q, nq = nappe["la_nappe"][m], nn[m]
    if not len(q):
        return la_nappe([], [], 0, pas_du_rouleau)
    if len(q) > LE_MAXIMUM_DE_POINTS:
        k = np.linspace(0, len(q) - 1, LE_MAXIMUM_DE_POINTS).round().astype(int)
        q, nq = q[k], nq[k]
    demi = np.floor(LA_PORTEE_EN_PAS * pas_du_rouleau)
    t = np.arange(-demi, demi + 1.0)
    idx = np.floor((q[:, None, :] + t[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
    vu = lire_valeurs(idx) > 0
    longueurs, remplies = [], []
    for rayon in vu:
        r = la_plage_du_point(rayon, t)
        if r is not None:
            longueurs.append(r[0])
            remplies.append(r[1])
    return la_nappe(longueurs, remplies, len(q), pas_du_rouleau)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_nappes_de_0358_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe de PHerc0358 ne redonne pas celle de 305"}
    k = sum(1 for n in d["les_nappes"]["PHerc0358"] if n["la_lecture"] == "dans un bloc")
    m = sum(1 for n in d["les_nappes"]["PHercParis4"] if n["la_lecture"] == "dans un bloc")
    return {"decidable": True, "k": k, "m": m,
            "lissue": f"sur PHerc0358, {k} des {len(d['les_nappes']['PHerc0358'])} nappes sont posées dans un bloc de m7, et sur "
                      f"PHercParis4, {m} des {len(d['les_nappes']['PHercParis4'])}"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    nappes = {"PHerc0358": [], "PHercParis4": []}
    lecture = {}
    publie = {g["le_rang"]: g["les_points_poses"]
              for g in json.loads(m305.RACINE.joinpath("docs", "mesures",
                                                       "une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.json")
                                  .read_text())["les_graines"]}
    pred = array_meta(f"{BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    d301 = {tuple(g["la_graine"]): g["le_rang"]
            for g in json.loads(m305.CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    se_redonnent = True
    for g in m301.les_graines_neuves():
        cle = (g["x"], g["y"], g["z"])
        rang = d301[cle]
        nz, ny, nx = g["normale_zyx"]
        r = m305.la_nappe_croissante(cle, (nx, ny, nz), lv)
        se_redonnent &= int(r["valide"].sum()) == publie.get(rang)
        e = dict({"le_rang": rang}, **lire_les_plages(r, lv, m300.LE_PAS_0358), **m325.la_platitude(r["le_decalage"], r["valide"]))
        nappes["PHerc0358"].append(e)
        print("PHerc0358", json.dumps(e, ensure_ascii=False), flush=True)
    pannes = list(stats["pannes"])
    lecture["PHerc0358"] = {k: v for k, v in stats.items() if k != "pannes"}

    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        e = dict({"le_rang": rang}, **lire_les_plages(r, lv4, m321.LE_PAS_L2), **m325.la_platitude(r["le_decalage"], r["valide"]))
        nappes["PHercParis4"].append(e)
        print("PHercParis4", json.dumps(e, ensure_ascii=False), flush=True)
    pannes += list(stats4["pannes"])
    lecture["PHercParis4"] = {k: v for k, v in stats4.items() if k != "pannes"}
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_portee_en_pas": LA_PORTEE_EN_PAS, "le_bloc_en_pas": LE_BLOC, "la_feuille_en_pas": LA_FEUILLE,
                            "la_part_lue": LA_PART_LUE, "le_maximum_de_points": LE_MAXIMUM_DE_POINTS},
         "les_pannes": pannes, "la_lecture_de_m7": lecture, "les_nappes_de_0358_se_redonnent": bool(se_redonnent),
         "les_nappes": nappes}
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

    t = np.arange(-60.0, 61.0)
    vu = np.abs(t) <= 3
    v("★★★★ une feuille de 7 voxels autour du point", la_plage_du_point(vu, t) == (7.0, False))
    v("★★★★ une plage qui remplit le rayon le remplit", la_plage_du_point(np.ones_like(vu), t) == (121.0, True))
    v("★★★ une plage qui ne touche qu'un bout ne remplit pas", la_plage_du_point(t <= 10, t) == (71.0, False))
    decale = (t >= 8) & (t <= 12)
    v("★★★★ sans plage au point, la plus proche, pas la première",
      la_plage_du_point((t <= -40) | decale | (t >= 40), t) == (5.0, False))
    v("★★★ un rayon sans plage n'en a pas", la_plage_du_point(np.zeros_like(vu), t) is None)
    v("★★★★ médiane de 25 voxels pour un pas de 20 : dans un bloc", la_nappe([25.0] * 10, [False] * 10, 10, 20.0)["la_lecture"]
      == "dans un bloc")
    v("★★★★ médiane de 10 voxels pour un pas de 20 : sur une feuille, bornes comprises",
      la_nappe([10.0] * 10, [False] * 10, 10, 20.0)["la_lecture"] == "sur une feuille"
      and la_nappe([20.0] * 10, [False] * 10, 10, 20.0)["la_lecture"] == "dans un bloc")
    v("★★★ entre un demi-pas et un pas : mêlée", la_nappe([15.0] * 10, [False] * 10, 10, 20.0)["la_lecture"] == "mêlée")
    v("★★★ moins de la moitié des points avec une plage : non lue", la_nappe([25.0] * 4, [True] * 4, 10, 20.0)["la_lecture"] == "non lue")
    v("★★★ la part qui remplit la portée", la_nappe([121.0, 7.0], [True, False], 2, 20.0)["la_part_qui_remplit_la_portee"] == 0.5)
    vide = {"la_nappe": np.zeros((5, 5, 3)), "valide": np.zeros((5, 5), dtype=bool)}
    v("★★★ une nappe sans point n'est pas lue, et rien n'est lu du dépôt",
      lire_les_plages(vide, lambda idx: 1 / 0, 20.0)["la_lecture"] == "non lue")
    vd = le_verdict({"les_pannes": [], "les_nappes_de_0358_se_redonnent": True,
                     "les_nappes": {"PHerc0358": [{"la_lecture": "dans un bloc"}, {"la_lecture": "mêlée"}],
                                    "PHercParis4": [{"la_lecture": "sur une feuille"}]}})
    v("★★★ l'issue : k et m", vd["k"] == 1 and vd["m"] == 0, str(vd))

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
