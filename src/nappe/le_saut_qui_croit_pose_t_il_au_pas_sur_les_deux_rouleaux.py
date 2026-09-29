"""Le saut qui croît de 306 pose-t-il sa spire au pas aussi souvent sur PHerc0358, sans tracé, que sur PHercParis4, où elle tombe sur le tour que la main humaine a tracé ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT QUI CROÎT NE SOIT TIRÉ DEPUIS LES HUIT GRAINES DE `301` SUR PHerc0358. Ce qui était vu
avant d'écrire : tout ce que `296` à `323` publient, dont `R4-F506` (sur PHercParis4, la spire qui croît tombe sur le tour suivant du
segment sur 4 graines sur 8) et ce que `306` publie sur PHerc0358 pour ses deux seuls départs, les graines 3 et 6 : au premier saut, la
graine 3 pose 9,63 % du plan côté plus à un pas médian de 57 voxels et 0,09 % côté moins, la graine 6 pose 19,31 % côté plus à 45
voxels et 79,24 % côté moins à 18. Les six autres graines n'ont jamais eu de saut qui croît ; et le premier saut des huit graines de
PHercParis4 n'a été compté que par sa part posée, pas par son pas.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P122`. Le même saut tombe sur le tracé humain de PHercParis4 et ne tenait pas sur
PHerc0358. Soit il y pose aussi souvent au pas et la différence est dans le juge de `306`, soit il pose moins, ou pas au pas, et elle
est dans `m7` ou le rouleau.

## Ce qui est fait

- **Les graines** : sur PHerc0358, les huit de `301` avec leur normale ; sur PHercParis4, les huit de `321`.
- **La nappe** : celle de `305`, à la tolérance et au pas de chaque rouleau (5 voxels et 20 sur PHerc0358, 4,51 et 18,02 voxels du
  niveau 2 sur PHercParis4). Sur PHerc0358, elle doit redonner le nombre de points que `305` publie pour chaque graine.
- **Le saut** : le premier saut qui croît de `306`, de chaque côté, sans en changer une règle, au pas de chaque rouleau.
- **Ce qui est compté** : la part du plan que le saut pose, et le pas médian de ses points posés, en pas du rouleau.

## Les issues

Un côté **pose au pas** si son premier saut pose au moins 10 % du plan et que son pas médian est entre un demi-pas et un pas et demi (le
tour suivant de PHercParis4 est à 0,79 à 1,46 pas du tracé, `R4-F506`). L'issue de la tranche : **le saut qui croît pose au pas sur k
des 16 côtés de PHerc0358 et sur m des 16 de PHercParis4** ; et, déclaré avant : **le saut se comporte sur PHerc0358 comme sur
PHercParis4** si k vaut au moins la moitié de m, et m au moins 4 ; **il y pose moins au pas** sinon. Indécidable si une lecture échoue ou
si une nappe de PHerc0358 ne redonne pas celle de `305`.

## Rapporté à côté, qui ne décide rien

La part du plan posée par la nappe ; et, sur PHerc0358, pour les graines 3 et 6, que le premier saut redonne la part posée que `306`
publie.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille tombe une spire posée au pas de PHerc0358, qu'aucun tracé ne dit.

Usage :
    uv run python src/nappe/le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux.py --verifier
    uv run python src/nappe/le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux.py \\
        --json docs/mesures/le_saut_qui_croit_pose_t_il_au_pas_sur_les_deux_rouleaux.json
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
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402

LA_PART_MINIMALE = 0.10
LE_PAS_BAS, LE_PAS_HAUT = 0.5, 1.5
CE_QUE_305_A_PUBLIE = RACINE / "docs" / "mesures" / "une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.json"
CE_QUE_306_A_PUBLIE = RACINE / "docs" / "mesures" / "la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.json"


def le_saut(pas_: np.ndarray, pose: np.ndarray, pas_du_rouleau: float) -> dict:
    """La part du plan posée par un saut, son pas médian en pas du rouleau, et s'il pose au pas."""
    part = float(pose.mean()) if pose.size else 0.0
    a = np.abs(pas_[pose & np.isfinite(pas_)])
    med = float(np.median(a)) / pas_du_rouleau if len(a) else None
    au_pas = part >= LA_PART_MINIMALE and med is not None and LE_PAS_BAS <= med <= LE_PAS_HAUT
    return {"la_part_du_plan": round(part, 4), "le_pas_median_en_pas": None if med is None else round(med, 3),
            "pose_au_pas": bool(au_pas)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_nappes_de_0358_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe de PHerc0358 ne redonne pas celle de 305"}
    k = sum(1 for c in d["les_cotes"]["PHerc0358"] if c["le_saut"]["pose_au_pas"])
    m = sum(1 for c in d["les_cotes"]["PHercParis4"] if c["le_saut"]["pose_au_pas"])
    n0, n4 = len(d["les_cotes"]["PHerc0358"]), len(d["les_cotes"]["PHercParis4"])
    tete = f"le saut qui croît pose au pas sur {k} des {n0} côtés de PHerc0358 et sur {m} des {n4} de PHercParis4"
    if m < 4:
        return {"decidable": False, "k": k, "m": m, "lissue": f"indécidable : {tete}, trop peu sur PHercParis4"}
    pareil = 2 * k >= m
    return {"decidable": True, "k": k, "m": m, "pareil": pareil,
            "lissue": tete + (" ; il se comporte sur PHerc0358 comme sur PHercParis4" if pareil
                              else " ; il y pose moins au pas sur PHerc0358")}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    pannes, cotes, nappes = [], {"PHerc0358": [], "PHercParis4": []}, {"PHerc0358": [], "PHercParis4": []}
    lecture = {}

    publie = {g["le_rang"]: g["les_points_poses"] for g in json.loads(CE_QUE_305_A_PUBLIE.read_text())["les_graines"]}
    pred = array_meta(f"{BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    d301 = {tuple(g["la_graine"]): g["le_rang"] for g in json.loads(m305.CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    se_redonnent = True
    for g in m301.les_graines_neuves():
        cle = (g["x"], g["y"], g["z"])
        rang = d301[cle]
        nz, ny, nx = g["normale_zyx"]
        r = m305.la_nappe_croissante(cle, (nx, ny, nz), lv)
        poses = int(r["valide"].sum())
        se_redonnent &= poses == publie.get(rang)
        nappes["PHerc0358"].append({"le_rang": rang, "les_points_poses": poses, "la_part_du_plan": round(float(r["valide"].mean()), 4),
                                    "redonne_305": poses == publie.get(rang)})
        for nom, cote in m306.LES_COTES:
            s = m306.le_saut_croissant(r["la_nappe"], r["valide"], cote, lv)
            e = {"le_rang": rang, "le_cote": nom, "le_saut": le_saut(s["le_pas"], s["valide"], m300.LE_PAS_0358)}
            cotes["PHerc0358"].append(e)
            print("PHerc0358", json.dumps(e, ensure_ascii=False), flush=True)
    pannes += list(stats["pannes"])
    lecture["PHerc0358"] = {k: v for k, v in stats.items() if k != "pannes"}

    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        nappes["PHercParis4"].append({"le_rang": rang, "les_points_poses": int(r["valide"].sum()),
                                      "la_part_du_plan": round(float(r["valide"].mean()), 4)})
        with m321.le_rouleau_de_paris4():
            for nom, cote in m306.LES_COTES:
                s = m306.le_saut_croissant(r["la_nappe"], r["valide"], cote, lv4, tolerance=m322.LA_TOLERANCE_L2)
                e = {"le_rang": rang, "le_cote": nom, "le_saut": le_saut(s["le_pas"], s["valide"], m321.LE_PAS_L2)}
                cotes["PHercParis4"].append(e)
                print("PHercParis4", json.dumps(e, ensure_ascii=False), flush=True)
    pannes += list(stats4["pannes"])
    lecture["PHercParis4"] = {k: v for k, v in stats4.items() if k != "pannes"}

    d306 = {(c["le_rang"], c["le_cote"]): c["les_sauts"][0]["la_part_du_plan"]
            for c in json.loads(CE_QUE_306_A_PUBLIE.read_text())["les_cotes"]}
    redonne_306 = {f"{r}_{c}": {"306": v, "ici": next(x["le_saut"]["la_part_du_plan"] for x in cotes["PHerc0358"]
                                                       if x["le_rang"] == r and x["le_cote"] == c)}
                   for (r, c), v in d306.items()}
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part_minimale": LA_PART_MINIMALE, "le_pas_bas": LE_PAS_BAS, "le_pas_haut": LE_PAS_HAUT},
         "les_pannes": pannes, "la_lecture_de_m7": lecture, "les_nappes_de_0358_se_redonnent": bool(se_redonnent),
         "les_nappes": nappes, "les_cotes": cotes, "le_premier_saut_de_306": redonne_306}
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

    pose = np.zeros((10, 10), dtype=bool)
    pose[:2, :] = True
    pas_ = np.full((10, 10), 21.0)
    s = le_saut(pas_, pose, 20.0)
    v("★★★★ un saut qui pose 20 % du plan à 21 voxels pour un pas de 20 pose au pas", s["pose_au_pas"]
      and s["la_part_du_plan"] == 0.2 and s["le_pas_median_en_pas"] == 1.05, str(s))
    v("★★★★ à 57 voxels pour un pas de 20, il ne pose pas au pas", not le_saut(np.full((10, 10), 57.0), pose, 20.0)["pose_au_pas"])
    v("★★★ à un demi-pas juste, il pose au pas ; en deçà, non", le_saut(np.full((10, 10), 10.0), pose, 20.0)["pose_au_pas"]
      and not le_saut(np.full((10, 10), 9.9), pose, 20.0)["pose_au_pas"])
    v("★★★ le pas se lit sans son signe", le_saut(np.full((10, 10), -21.0), pose, 20.0)["pose_au_pas"])
    peu = np.zeros((10, 10), dtype=bool)
    peu[0, :9] = True
    v("★★★★ sous 10 % du plan, il ne pose pas au pas", not le_saut(pas_, peu, 20.0)["pose_au_pas"])
    v("★★★ un saut vide n'a pas de pas", le_saut(pas_, np.zeros((10, 10), dtype=bool), 20.0)["le_pas_median_en_pas"] is None)
    cote = lambda b: {"le_saut": {"pose_au_pas": b}}  # noqa: E731
    base = {"les_pannes": [], "les_nappes_de_0358_se_redonnent": True}
    vd = le_verdict(dict(base, les_cotes={"PHerc0358": [cote(True), cote(True)] + [cote(False)] * 14,
                                          "PHercParis4": [cote(True)] * 4 + [cote(False)] * 12}))
    v("★★★★ k = 2, m = 4 : il se comporte pareil", vd["decidable"] and vd["pareil"], str(vd))
    vd = le_verdict(dict(base, les_cotes={"PHerc0358": [cote(True)] + [cote(False)] * 15,
                                          "PHercParis4": [cote(True)] * 4 + [cote(False)] * 12}))
    v("★★★★ k = 1, m = 4 : il pose moins au pas sur PHerc0358", vd["decidable"] and not vd["pareil"], str(vd))
    vd = le_verdict(dict(base, les_cotes={"PHerc0358": [cote(True)] * 3, "PHercParis4": [cote(True)] * 3}))
    v("★★★ trop peu au pas sur PHercParis4 : indécidable", not vd["decidable"])
    v("★★★ une nappe de PHerc0358 qui ne redonne pas 305 : indécidable",
      not le_verdict(dict(base, les_nappes_de_0358_se_redonnent=False, les_cotes={}))["decidable"])

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
