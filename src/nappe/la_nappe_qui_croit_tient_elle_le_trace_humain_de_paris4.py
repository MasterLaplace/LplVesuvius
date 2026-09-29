"""La nappe qui croît de 305, tirée sur PHercParis4 depuis les graines de 321, tient-elle la feuille du tracé humain jusqu'au bord de son plan ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE NAPPE CROISSANTE NE SOIT TIRÉE SUR PHercParis4. Ce qui était vu avant d'écrire : tout ce
que `296` à `321` publient, dont `R4-F502` et `R4-F503` : depuis les huit graines de `321`, la nappe du vote de `300` part de la
feuille du tracé humain (40 à 100 % des sommets en face à un quart de pas près de la graine) et la quitte en s'en éloignant (9 à 67 %
au bord du plan), et sur quatre graines elle passe à la feuille voisine.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P119`. `305` a été écrite pour qu'une nappe ne puisse pas passer à la feuille voisine en
un pas de grille : chaque point prend la feuille de `m7` la plus proche de la médiane de ses voisins déjà posés, à au plus un quart de
pas, ou attend. Elle n'a été jugée que sans référent, par un juge aveugle à la position (`R4-F488`). Contre le tracé humain, on saura si
refuser le saut suffit à tenir une feuille courbe.

## Ce qui est fait

- **Les graines** : les huit de `321`, dans leur ordre.
- **La nappe** : celle de `305`, sans en changer une règle, au pas de PHercParis4 : une tolérance d'un quart de pas (4,51 voxels du
  niveau 2) et une demi-portée d'un pas et demi (27,03 voxels).
- **La comparaison** : celle de `321`, sans rien y changer, sur les points posés : les sommets du segment dans l'emprise du plan, leur
  écart signé à la nappe le long de leur normale, en face à au plus 40 voxels de côté.

## Les issues

Par graine, **la nappe retrouve le tracé**, **ne le retrouve pas** ou **non lue**, par la règle de `321`. Et, pour `R4-P119`, par
l'anneau du bord (les sommets à 6 à 8 sommets de la graine) : **elle tient le tracé jusqu'au bord** si au moins 10 sommets de cet
anneau lui font face et qu'au moins la moitié sont à un quart de pas ; **elle ne le tient pas** si 10 lui font face et moins de la
moitié sont à un quart de pas ; **elle n'atteint pas le bord** sous 10 sommets en face. L'issue de la tranche : **sur k des huit
graines, la nappe qui croît tient la feuille du tracé humain jusqu'au bord de son plan.**

## Rapporté à côté, qui ne décide rien

La part du plan posée ; par anneau, la part des sommets en face sur la feuille du tracé et la part à un pas ; l'histogramme des écarts.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut une nappe croissante sur PHerc0358, ni au-delà du plan de 2560 voxels de 2,4 µm.

Usage :
    uv run python src/nappe/la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.py --verifier
    uv run python src/nappe/la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.py \\
        --json docs/mesures/la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.json
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
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402

LA_TOLERANCE_L2 = m321.LE_PAS_L2 / 4.0    # 4,51 voxels du niveau 2
LA_DEMI_PORTEE_L2 = 1.5 * m321.LE_PAS_L2  # 27,03
LE_MINIMUM_AU_BORD = 10


def au_bord(anneaux: list[dict]) -> str:
    """Ce que dit l'anneau du bord : la nappe y tient-elle le tracé, ne le tient-elle pas, ou n'y arrive-t-elle pas ?"""
    b = anneaux[-1]
    if b["les_sommets_en_face"] < LE_MINIMUM_AU_BORD:
        return "n'atteint pas le bord"
    return "tient jusqu'au bord" if b["la_part_sur_la_feuille_du_trace"] >= 0.5 else "ne tient pas"


def la_nappe_de_paris4(graine_l2, normale, lire_valeurs) -> dict:
    """La nappe qui croît de `305`, au pas de PHercParis4 : sa tolérance, sa demi-portée et celles du plan de `300`."""
    with m321.le_rouleau_de_paris4():
        return m305.la_nappe_croissante(tuple(graine_l2), tuple(normale), lire_valeurs, tolerance=LA_TOLERANCE_L2,
                                        demi_portee=LA_DEMI_PORTEE_L2)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    gs = d["les_graines"]
    if not gs:
        return {"decidable": False, "lissue": "indécidable : aucune graine"}
    k = sum(1 for g in gs if g["au_bord"] == "tient jusqu'au bord")
    lues = [g for g in gs if g["la_nappe"]["la_lecture"] != "non lue"]
    r = sum(1 for g in lues if g["la_nappe"]["la_lecture"] == "retrouve")
    return {"decidable": True, "k": k, "n": len(gs), "retrouve": r, "lues": len(lues),
            "lissue": f"sur {k} des {len(gs)} graines, la nappe qui croît tient la feuille du tracé humain jusqu'au bord de son plan ; "
                      f"elle le retrouve sur {r} des {len(lues)} graines lues"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    seg, sok, esp = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv = lambda idx: m300.lire_m7(idx, (pred, lire_))  # noqa: E731
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        g0 = seg[i, j] / m321.LE_FACTEUR
        f = sok & snok & m321.la_fenetre(sok.shape, i, j)
        ref, ref_n = seg[f], sn[f]
        ii, jj = np.nonzero(f)
        anneau = np.maximum(np.abs(ii - i), np.abs(jj - j))
        plan, _ = m300.le_plan(tuple(g0), tuple(sn[i, j]))
        t_plan = m321.les_ecarts(ref, ref_n, plan.reshape(-1, 3) * m321.LE_FACTEUR)
        r = la_nappe_de_paris4(g0, sn[i, j], lv)
        pts = r["la_nappe"][r["valide"]] * m321.LE_FACTEUR
        t = m321.les_ecarts(ref, ref_n, pts)
        anneaux = m321.par_anneau(t, anneau, t_plan)
        e = {"le_rang": rang, "le_sommet": [i, j], "la_part_posee": round(float(r["valide"].mean()), 4),
             "les_sommets_de_la_fenetre": int(f.sum()),
             "la_nappe": dict(m321.la_coincidence(t), par_anneau=anneaux, lhistogramme=m321.lhistogramme(t)),
             "au_bord": au_bord(anneaux)}
        graines.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_tolerance_l2_voxels": round(LA_TOLERANCE_L2, 3), "la_demi_portee_l2_voxels":
                            round(LA_DEMI_PORTEE_L2, 3), "le_minimum_au_bord": LE_MINIMUM_AU_BORD,
                            "le_quart_de_pas_l0_voxels": round(m321.LE_QUART, 3), "lespacement_du_segment": esp},
         "les_pannes": list(stats["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats.items() if k != "pannes"},
         "les_graines": graines}
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

    v("★★★ la tolérance et la demi-portée de PHercParis4 : 4,51 et 27,03 voxels du niveau 2",
      round(LA_TOLERANCE_L2, 2) == 4.51 and round(LA_DEMI_PORTEE_L2, 2) == 27.03)
    bord = lambda n, p: [{}, {}, {"les_sommets_en_face": n, "la_part_sur_la_feuille_du_trace": p}]  # noqa: E731
    v("★★★★ au bord : la moitié à un quart de pas tient", au_bord(bord(12, 0.5)) == "tient jusqu'au bord")
    v("★★★★ au bord : moins de la moitié ne tient pas", au_bord(bord(12, 0.49)) == "ne tient pas")
    v("★★★★ au bord : sous 10 sommets en face, la nappe n'y arrive pas", au_bord(bord(9, 1.0)) == "n'atteint pas le bord")

    centres = [np.array([0.0]) for _ in range(9 * 9)]
    for a in range(9):
        for b in range(9):
            centres[a * 9 + b] = np.array([0.8 * b, 0.8 * b + 18.0])
    dec, pose = m305.croitre(centres, (9, 9), (4, 4), tolerance=LA_TOLERANCE_L2, demi_portee=LA_DEMI_PORTEE_L2)
    v("★★★★ la croissance suit une feuille qui monte de 0,8 voxel par point sans passer à la voisine, 18 voxels au-dessus",
      pose.all() and np.allclose(dec, np.tile(0.8 * np.arange(9), (9, 1))), str(dec[0]))
    for a in range(9):
        for b in range(9):
            centres[a * 9 + b] = np.array([5.0 * b - 20.0])
    dec, pose = m305.croitre(centres, (9, 9), (4, 4), tolerance=LA_TOLERANCE_L2, demi_portee=LA_DEMI_PORTEE_L2)
    v("★★★ une pente de 5 voxels par point, au-delà d'un quart de pas, arrête la croissance à la colonne de la graine",
      pose[:, 4].all() and not pose[:, 3].any() and not pose[:, 5].any())
    def la_pente_de_475(idx):
        return idx[..., 0] == 100 + np.round(4.75 * np.abs(idx[..., 2] - 100) / 10.0)

    r = la_nappe_de_paris4((100.0, 100.0, 100.0), (0.0, 0.0, 1.0), la_pente_de_475)
    v("★★★★ la nappe de PHercParis4 refuse un pas de 5 voxels que la tolérance de PHerc0358 aurait pris",
      int(r["valide"].sum()) == 65, str(int(r["valide"].sum())))
    r = m305.la_nappe_croissante((100.0, 100.0, 100.0), (0.0, 0.0, 1.0), la_pente_de_475)
    v("★★ le témoin : la tolérance de PHerc0358 prend ce pas", int(r["valide"].sum()) > 65, str(int(r["valide"].sum())))

    d = {"les_pannes": [], "les_graines": [{"au_bord": "tient jusqu'au bord", "la_nappe": {"la_lecture": "retrouve"}},
                                           {"au_bord": "n'atteint pas le bord", "la_nappe": {"la_lecture": "non lue"}},
                                           {"au_bord": "ne tient pas", "la_nappe": {"la_lecture": "ne retrouve pas"}}]}
    vd = le_verdict(d)
    v("★★★ l'issue : k des huit graines tiennent jusqu'au bord ; et les retrouvées parmi les lues",
      vd["k"] == 1 and vd["n"] == 3 and vd["retrouve"] == 1 and vd["lues"] == 2, str(vd))
    v("★★★ une panne de lecture rend la tranche indécidable",
      not le_verdict({"les_pannes": ["x"], "les_graines": d["les_graines"]})["decidable"])

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
