"""À quelle distance, en pas du rouleau, chaque point de la nappe qui croît voit-il la feuille de m7 après la sienne, sur PHerc0358 et sur PHercParis4, et le départ du saut prend-il la distance typique ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA DISTANCE À LA FEUILLE SUIVANTE NE SOIT LUE POINT PAR POINT. Ce qui était vu avant d'écrire :
tout ce que `296` à `324` publient, dont `R4-F508` (le premier saut qui croît pose au pas sur 14 côtés sur 16 de PHercParis4 et sur 5
de PHerc0358, où six côtés posent à 1,7 à 2,85 pas et cinq ne posent rien) et `R4-F493` (sur PHerc0358, les plages de `m7` se suivent
à 10 à 17,5 voxels le long des rayons des plans de `301`).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P123`. Le saut qui croît part d'un seul point, le plus proche du centre qui voit une
feuille après la sienne, et toute la spire croît autour de la distance que ce point a vue. Si, sur PHerc0358, les points de la nappe
voient la feuille suivante à un pas et que le départ en voit une plus loin, c'est le départ qui fait poser loin ; s'ils la voient
eux-mêmes loin, ou ne la voient pas, c'est `m7`.

## Ce qui est fait

- **Les graines, la nappe et le saut** : ceux de `324`, sans rien y changer.
- **La distance à la feuille suivante** : pour chaque point posé de la nappe, de chaque côté, la première feuille de `m7` après la
  sienne sur trois pas, exactement celle que le saut de `306` lit (la règle de `300`), en pas du rouleau.
- **Le départ** : le point d'où le saut croît, et la distance qu'il a vue.

## Les issues

Par côté, **la feuille suivante est vue à un pas** si au moins la moitié des points de la nappe en voient une et que la distance médiane
est entre un demi-pas et un pas et demi ; **plus près** sous un demi-pas ; **plus loin** au-delà d'un pas et demi ; **rarement vue** si
moins de la moitié des points en voient une. Et **le départ s'écarte** si la distance qu'il a vue est à plus d'un quart de pas de la
médiane de son côté. L'issue de la tranche : **sur PHerc0358, la feuille suivante est vue à un pas sur k des 16 côtés, et le départ
s'écarte sur a ; sur PHercParis4, sur m et sur b.**

## Rapporté à côté, qui ne décide rien

L'histogramme des distances par côté, par quart de pas de 0 à 3 pas ; la part des points qui voient une feuille suivante.

⚠ Ajouté après la première mesure, le 2026-09-29, sans toucher à la règle : pour chaque nappe, la part de ses points posés au décalage le
plus fréquent (au demi-voxel). La première mesure a rendu trois graines de PHerc0358 dont aucun point ne voit de feuille suivante, et
la carte que `305` publie met presque tous les points de deux d'entre elles au même décalage.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une plage de `m7` à moins d'un pas est une autre spire ou une autre face de la même.

Usage :
    uv run python src/nappe/a_quelle_distance_m7_montre_t_il_la_feuille_suivante.py --verifier
    uv run python src/nappe/a_quelle_distance_m7_montre_t_il_la_feuille_suivante.py \\
        --json docs/mesures/a_quelle_distance_m7_montre_t_il_la_feuille_suivante.json
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

LE_PAS_BAS, LE_PAS_HAUT = 0.5, 1.5
LA_PART_QUI_VOIT = 0.5
LES_BORNES = np.arange(0.0, 3.01, 0.25)


def le_cote(suivantes: np.ndarray, nappe_valide: np.ndarray, depart, pas_du_rouleau: float) -> dict:
    """Ce que les points posés de la nappe voient de la feuille suivante, en pas du rouleau, et ce que le départ du saut a vu."""
    s = suivantes[nappe_valide]
    vus = np.abs(s[np.isfinite(s)]) / pas_du_rouleau
    part = float(len(vus) / len(s)) if len(s) else 0.0
    med = float(np.median(vus)) if len(vus) else None
    dep = None
    if depart is not None and np.isfinite(suivantes[depart[0], depart[1]]):
        dep = float(abs(suivantes[depart[0], depart[1]])) / pas_du_rouleau
    if part < LA_PART_QUI_VOIT or med is None:
        lecture = "rarement vue"
    elif med < LE_PAS_BAS:
        lecture = "plus près"
    elif med > LE_PAS_HAUT:
        lecture = "plus loin"
    else:
        lecture = "à un pas"
    ecart = dep is not None and med is not None and abs(dep - med) > 0.25
    h, _ = np.histogram(np.minimum(vus, 3.0), bins=LES_BORNES)
    return {"la_part_qui_voit": round(part, 4), "la_distance_mediane_en_pas": None if med is None else round(med, 3),
            "le_depart_en_pas": None if dep is None else round(dep, 3), "la_lecture": lecture, "le_depart_secarte": bool(ecart),
            "lhistogramme": [int(x) for x in h]}


def la_platitude(decalage: np.ndarray, valide: np.ndarray) -> dict:
    """Rapporté : le décalage le plus fréquent des points posés, au demi-voxel, et la part des points posés qui l'ont."""
    v = np.round(decalage[valide & np.isfinite(decalage)] * 2.0) / 2.0
    if not len(v):
        return {"le_decalage_le_plus_frequent": None, "la_part_a_ce_decalage": None}
    vals, n = np.unique(v, return_counts=True)
    return {"le_decalage_le_plus_frequent": float(vals[int(np.argmax(n))]), "la_part_a_ce_decalage": round(float(n.max() / len(v)), 4)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("les_nappes_de_0358_se_redonnent"):
        return {"decidable": False, "lissue": "indécidable : une nappe de PHerc0358 ne redonne pas celle de 305"}
    c0, c4 = d["les_cotes"]["PHerc0358"], d["les_cotes"]["PHercParis4"]
    k = sum(1 for c in c0 if c["la_lecture"] == "à un pas")
    a = sum(1 for c in c0 if c["le_depart_secarte"])
    m = sum(1 for c in c4 if c["la_lecture"] == "à un pas")
    b = sum(1 for c in c4 if c["le_depart_secarte"])
    return {"decidable": True, "k": k, "a": a, "m": m, "b": b,
            "lissue": f"sur PHerc0358, la feuille suivante est vue à un pas sur {k} des {len(c0)} côtés, et le départ s'écarte sur "
                      f"{a} ; sur PHercParis4, sur {m} des {len(c4)} et sur {b}"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    cotes = {"PHerc0358": [], "PHercParis4": []}
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
        nappes["PHerc0358"].append(dict({"le_rang": rang, "la_part_du_plan": round(float(r["valide"].mean()), 4)},
                                        **la_platitude(r["le_decalage"], r["valide"])))
        for nom, cote in m306.LES_COTES:
            s = m306.le_saut_croissant(r["la_nappe"], r["valide"], cote, lv)
            e = dict({"le_rang": rang, "le_cote": nom}, **le_cote(s["les_suivantes"], r["valide"], s["le_depart"], m300.LE_PAS_0358))
            cotes["PHerc0358"].append(e)
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
        nappes["PHercParis4"].append(dict({"le_rang": rang, "la_part_du_plan": round(float(r["valide"].mean()), 4)},
                                          **la_platitude(r["le_decalage"], r["valide"])))
        with m321.le_rouleau_de_paris4():
            for nom, cote in m306.LES_COTES:
                s = m306.le_saut_croissant(r["la_nappe"], r["valide"], cote, lv4, tolerance=m322.LA_TOLERANCE_L2)
                e = dict({"le_rang": rang, "le_cote": nom},
                         **le_cote(s["les_suivantes"], r["valide"], s["le_depart"], m321.LE_PAS_L2))
                cotes["PHercParis4"].append(e)
                print("PHercParis4", json.dumps(e, ensure_ascii=False), flush=True)
    pannes += list(stats4["pannes"])
    lecture["PHercParis4"] = {k: v for k, v in stats4.items() if k != "pannes"}
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas_bas": LE_PAS_BAS, "le_pas_haut": LE_PAS_HAUT, "la_part_qui_voit": LA_PART_QUI_VOIT,
                            "les_bornes_en_pas": [float(x) for x in LES_BORNES]},
         "les_pannes": pannes, "la_lecture_de_m7": lecture, "les_nappes_de_0358_se_redonnent": bool(se_redonnent),
         "les_nappes": nappes, "les_cotes": cotes}
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

    val = np.ones((4, 5), dtype=bool)
    s = np.full((4, 5), 20.0)
    c = le_cote(s, val, [0, 0], 20.0)
    v("★★★★ tous à 20 voxels pour un pas de 20 : à un pas, départ dans la médiane", c["la_lecture"] == "à un pas"
      and c["la_distance_mediane_en_pas"] == 1.0 and not c["le_depart_secarte"], str(c))
    s2 = s.copy()
    s2[0, 0] = 57.0
    c = le_cote(s2, val, [0, 0], 20.0)
    v("★★★★ un départ qui a vu 57 voxels quand la nappe voit 20 s'écarte", c["le_depart_secarte"] and c["le_depart_en_pas"] == 2.85)
    s4 = s.copy()
    s4[0, 0] = 28.0
    v("★★★ un départ à 0,4 pas de la médiane s'écarte déjà ; à 0,2 pas, non", le_cote(s4, val, [0, 0], 20.0)["le_depart_secarte"]
      and not le_cote(np.where(s4 == 28.0, 24.0, s4), val, [0, 0], 20.0)["le_depart_secarte"])
    v("★★★ le signe ne compte pas", le_cote(-s, val, [0, 0], 20.0)["la_lecture"] == "à un pas")
    v("★★★★ à 8 voxels : plus près", le_cote(np.full((4, 5), 8.0), val, None, 20.0)["la_lecture"] == "plus près")
    v("★★★★ à 40 voxels : plus loin", le_cote(np.full((4, 5), 40.0), val, None, 20.0)["la_lecture"] == "plus loin")
    s3 = s.copy()
    s3[:3, :] = np.nan
    v("★★★★ si moins de la moitié des points voient une feuille : rarement vue",
      le_cote(s3, val, [3, 0], 20.0)["la_lecture"] == "rarement vue")
    moitie = s.copy()
    moitie[:2, :] = np.nan
    v("★★★ la moitié juste qui voit suffit", le_cote(moitie, val, [3, 0], 20.0)["la_lecture"] == "à un pas")
    hors = np.zeros_like(val)
    hors[0, :2] = True
    v("★★★ seuls les points posés de la nappe comptent", le_cote(s2, hors, None, 20.0)["la_distance_mediane_en_pas"] == 1.925)
    v("★★★ au-delà de 3 pas, l'histogramme range au dernier quart", le_cote(np.full((4, 5), 90.0), val, None, 20.0)["lhistogramme"][-1]
      == 20)
    dec = np.full((4, 5), 3.0)
    dec[0, 0] = 1.2
    pl = la_platitude(dec, val)
    v("★★★ la platitude : 19 points sur 20 au même décalage", pl["le_decalage_le_plus_frequent"] == 3.0
      and pl["la_part_a_ce_decalage"] == 0.95, str(pl))
    v("★★ une nappe vide n'a pas de platitude", la_platitude(dec, np.zeros_like(val))["la_part_a_ce_decalage"] is None)
    cote = lambda l_, e_: {"la_lecture": l_, "le_depart_secarte": e_}  # noqa: E731
    vd = le_verdict({"les_pannes": [], "les_nappes_de_0358_se_redonnent": True,
                     "les_cotes": {"PHerc0358": [cote("à un pas", True), cote("plus loin", False)],
                                   "PHercParis4": [cote("à un pas", False)] * 3}})
    v("★★★ l'issue compte les deux rouleaux", (vd["k"], vd["a"], vd["m"], vd["b"]) == (1, 1, 3, 0), str(vd))

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
