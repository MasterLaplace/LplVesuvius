"""Au septième saut, pourquoi aucune chaîne ne retrouve-t-elle 5753_-7 : la surface tombe-t-elle à côté de 5753_-7, ou 5753_-7 est-il décalé, loin d'un pas de 5753_-6 ou de la feuille que m7 voit ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE SEPTIÈME SURFACE NE SOIT RAPPORTÉE À `5753_-6` ET `5753_-7`. Ce qui était vu avant
d'écrire : tout ce que `296` à `335` publient, dont `R4-F521` (bornée à deux mailles de ses semis, la chaîne relancée depuis sa spire
descend `5753_0` à `5753_-6` sur les huit graines de PHercParis4 sans un saut faux, et s'arrête au septième saut sur un tour manqué, au bout
de ses huit sauts, ou sur une surface non lue) et `R4-F520` (au septième saut, `5753_-7` est lu en face des spires et ne les retrouve
pas). Sans relance, relancée libre ou bornée, aucune chaîne n'a jamais retrouvé `5753_-7`.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P132`. Deux causes donneraient la même lecture. La surface peut tomber à côté de
`5753_-7` : alors le septième saut se trompe, sans que la lecture puisse dire où il va. Ou `5753_-7` peut ne pas être à un pas de
`5753_-6`, ou ne pas passer sur une feuille de `m7` : alors aucune surface tirée de `m7` ne peut le retrouver, et c'est le référent qui
manque.

## Ce qui est fait

- **La chaîne** : celle de `335` sur PHercParis4, sans rien y changer ; elle doit redonner, côté par côté, la descente et ce qui l'arrête
  que `335` publie, sans quoi la tranche est indécidable. Chaque nappe relancée est gardée.
- **La septième surface** : pour chaque graine dont la descente, côté moins, atteint `5753_-6` et s'arrête sur une surface lue, la surface
  qui devait retrouver `5753_-7`.
- **Les mesures**, dans la boîte de cette surface élargie de 100 voxels comme `329` : l'écart médian de la surface à `5753_-6` et à
  `5753_-7` le long de leurs normales, par la comparaison de `321` ; l'écart médian de `5753_-7` à `5753_-6`, en pas ; et l'écart médian
  de `5753_-7` au centre de la plage de `m7` la plus proche, comme `332`.
- **La règle, pour chaque graine** : **`5753_-7` est décalé** si son écart à `5753_-6` sort de 0,75 à 1,25 pas, ou si son écart médian à
  `m7` dépasse un quart de pas du niveau 2 (4,5 voxels) ; sinon **la surface tombe à côté de `5753_-7`** si son écart médian à `5753_-7`
  dépasse un quart de pas ou si `5753_-7` n'a pas assez de sommets en face d'elle ; sinon **la surface est sur `5753_-7` en médiane sans
  le retrouver**.

## Les issues

L'issue de la tranche : **sur les n graines dont la chaîne a une septième surface, 5753_-7 est décalé a fois, la surface tombe à côté b
fois, elle est sur 5753_-7 en médiane c fois** ; et, déclaré avant, la cause est celle qui l'emporte strictement sur les deux autres ;
**la lecture ne tranche pas** sinon.

## Rapporté à côté, qui ne décide rien

Pour la même graine, l'écart de `5753_-6` à `5753_-5` et l'écart de `5753_-6` à `m7`, dans la même boîte : ce que valent les mêmes mesures un
tour plus haut, là où la chaîne retrouve le tour.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : comment `5753_-7` a été fait ; ni où irait un huitième saut.

Usage :
    uv run python src/nappe/pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.py --verifier
    uv run python src/nappe/pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.py \\
        --json docs/mesures/pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.json
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
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_tours_publies_sont_ils_poses_au_coeur_de_m7 as m332  # noqa: E402
import au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle as m334  # noqa: E402
import la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse as m335  # noqa: E402

CE_QUE_335_A_PUBLIE = RACINE / "docs" / "mesures" / "la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse.json"
LE_QUART_EN_PAS = 0.25
LA_BANDE_DU_PAS = (0.75, 1.25)
LE_QUART_L2 = m321.LE_PAS_L2 / 4.0
LES_CAUSES = ("5753_-7 est décalé", "la surface tombe à côté de 5753_-7", "la surface est sur 5753_-7 en médiane sans le retrouver")


def lecart_entre_deux_tours(a: dict, b: dict, pts: np.ndarray) -> dict:
    """L'écart médian, en pas, des sommets de `a` au tour `b` le long de leurs normales, les deux pris dans la boîte de `pts`."""
    ref, ref_n = m329.les_sommets_proches(a, pts)
    nuage, _ = m329.les_sommets_proches(b, pts)
    t = np.abs(m321.les_ecarts(ref, ref_n, nuage))
    t = t[np.isfinite(t)]
    return {"les_sommets_en_face": int(len(t)),
            "lecart_median_en_pas": round(float(np.median(t)) / m321.LE_PAS_L0, 3) if len(t) >= m321.LE_MINIMUM else None}


def la_place_sur_m7(tour: dict, pts: np.ndarray, lire_valeurs, maximum: int = m332.LE_MAXIMUM) -> dict:
    """Les sommets du tour dans la boîte de `pts`, au plus `maximum` pris régulièrement, et leur écart au centre de la plage de `m7` la
    plus proche, comme `332`."""
    p, n = m329.les_sommets_proches(tour, pts)
    if len(p) > maximum:
        k = np.linspace(0, len(p) - 1, maximum).round().astype(int)
        p, n = p[k], n[k]
    return m332.resumer(m332.les_ecarts_aux_plages(p, n, lire_valeurs, m321.LE_PAS_L2))


def la_cause(surface_7: dict, ecart_67: dict, m7_de_7: dict) -> str:
    """La cause, pour une graine, selon la règle déclarée."""
    if ecart_67["lecart_median_en_pas"] is None or m7_de_7["lecart_median_voxels"] is None:
        return "non mesurable"
    if (not LA_BANDE_DU_PAS[0] <= ecart_67["lecart_median_en_pas"] <= LA_BANDE_DU_PAS[1]
            or m7_de_7["lecart_median_voxels"] > LE_QUART_L2):
        return LES_CAUSES[0]
    if surface_7.get("la_lecture") == "non lue" or abs(surface_7["lecart_median_en_pas"]) > LE_QUART_EN_PAS:
        return LES_CAUSES[1]
    return LES_CAUSES[2]


def les_septiemes(graines: list[dict]) -> list[tuple[int, int]]:
    """Les graines dont la descente, côté moins, atteint `5753_-6` et s'arrête sur une surface qui devait retrouver `5753_-7` ; et le
    rang de cette surface dans la chaîne."""
    out = []
    for g in graines:
        c = g["les_cotes"]["moins"]
        if c["larret"] not in ("un tour manqué", "un saut faux"):
            continue
        ou = m334.le_saut_ou_elle_sarrete(c)
        if ou is not None and ou[1] == -7:
            out.append((g["le_rang"], ou[0]))
    return out


def redonne_335(d: dict, publie: dict) -> bool:
    return m334.redonne_333(d, publie)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_335"):
        return {"decidable": False, "lissue": "indécidable : la chaîne ne redonne pas celle de 335"}
    ss = [s for s in d["les_septiemes"] if s["la_cause"] in LES_CAUSES]
    if not ss:
        return {"decidable": False, "lissue": "indécidable : aucune septième surface mesurable"}
    a, b, c = (sum(1 for s in ss if s["la_cause"] == x) for x in LES_CAUSES)
    tete = (f"sur les {len(ss)} graines dont la chaîne a une septième surface, 5753_-7 est décalé {a} fois, la surface tombe à côté {b} "
            f"fois, elle est sur 5753_-7 en médiane {c} fois")
    comptes = {LES_CAUSES[0]: a, LES_CAUSES[1]: b, LES_CAUSES[2]: c}
    haut = max(comptes.values())
    gagnantes = [k for k, v in comptes.items() if v == haut]
    suite = {LES_CAUSES[0]: "c'est le référent qui manque", LES_CAUSES[1]: "c'est le septième saut qui tombe à côté",
             LES_CAUSES[2]: "la surface est au bon endroit mais trop dispersée"}[gagnantes[0]] if len(gagnantes) == 1 \
        else "la lecture ne tranche pas"
    return {"decidable": True, "n": len(ss), "a": a, "b": b, "c": c, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    gardees = {}

    def garder(rang, nom, h, k):
        rl = k["la_relance"]
        if rl is not None and rl["valide"].any():
            gardees[(rang, nom, h)] = rl["la_nappe"][rl["valide"]] * m321.LE_FACTEUR
        return {}

    d = m331.mesurer(relancer4=m335.la_relance_de_paris4, avec_la_spire=True, lire_la_spire=True, rouleaux=("PHercParis4",),
                     observer=garder)
    d.pop("les_cotes", None)
    d["la_question"] = __doc__.splitlines()[0]
    d["redonne_335"] = redonne_335(d, json.loads(CE_QUE_335_A_PUBLIE.read_text()))
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in (-5, -6, -7)}
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    ss = []
    for rang, h in les_septiemes(d["les_graines"]["PHercParis4"]):
        pts = gardees.get((rang, "moins", h))
        if pts is None:
            ss.append({"le_rang": rang, "le_saut": h, "la_cause": "non mesurable"})
            continue
        lect = m329.les_lectures(pts, {-6: tours[-6], -7: tours[-7]})
        e = {"le_rang": rang, "le_saut": h, "les_points": int(len(pts)),
             "la_surface_et_5753_-6": lect[-6], "la_surface_et_5753_-7": lect[-7],
             "5753_-7_et_5753_-6": lecart_entre_deux_tours(tours[-7], tours[-6], pts),
             "5753_-7_et_m7": la_place_sur_m7(tours[-7], pts, lv4),
             "5753_-6_et_5753_-5": lecart_entre_deux_tours(tours[-6], tours[-5], pts),
             "5753_-6_et_m7": la_place_sur_m7(tours[-6], pts, lv4)}
        e["la_cause"] = la_cause(e["la_surface_et_5753_-7"], e["5753_-7_et_5753_-6"], e["5753_-7_et_m7"])
        ss.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d["les_septiemes"] = ss
    d["les_pannes"] = list(d["les_pannes"]) + list(stats4["pannes"])
    d["la_lecture_de_m7_aux_tours"] = {k: v for k, v in stats4.items() if k != "pannes"}
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

    k = np.arange(-200.0, 201.0, 20.0)
    xy = np.stack(np.meshgrid(k, k, indexing="ij"), axis=-1).reshape(-1, 2)

    def plan(z):
        pts = np.concatenate([xy + 1000.0, np.full((len(xy), 1), z)], axis=1)
        return {"points": pts, "normales": np.tile([0.0, 0.0, 1.0], (len(pts), 1))}

    surf = plan(400.0)["points"]
    e = lecart_entre_deux_tours(plan(400.0 - m321.LE_PAS_L0), plan(400.0), surf)
    v("★★★★ deux tours à un pas l'un de l'autre sont à 1,0 pas", e["lecart_median_en_pas"] == 1.0 and e["les_sommets_en_face"] > 100,
      str(e))
    retourne = dict(plan(400.0 - m321.LE_PAS_L0))
    retourne["normales"] = -retourne["normales"]
    v("★★★★ l'écart entre deux tours ne dépend pas du sens de leurs normales",
      lecart_entre_deux_tours(retourne, plan(400.0), surf)["lecart_median_en_pas"] == 1.0)
    v("★★★ à un demi-pas, 0,5", lecart_entre_deux_tours(plan(400.0 - m321.LE_PAS_L0 / 2), plan(400.0), surf)["lecart_median_en_pas"]
      == 0.5)
    v("★★★ sans sommets en face, pas d'écart", lecart_entre_deux_tours(plan(400.0), {"points": np.zeros((0, 3)),
                                                                                    "normales": np.zeros((0, 3))},
                                                                         surf)["lecart_median_en_pas"] is None)
    feuille = lambda z2: (lambda idx: (np.abs(idx[..., 0] - z2) <= 1).astype(float))  # noqa: E731
    sur = la_place_sur_m7(plan(400.0), surf, feuille(100))
    v("★★★★ un tour posé sur une feuille de m7 en est à 0 voxel du niveau 2", sur["lecart_median_voxels"] == 0.0, str(sur))
    loin = la_place_sur_m7(plan(400.0), surf, feuille(106))
    v("★★★★ un tour posé à 6 voxels du niveau 2 d'une feuille en est à 6", loin["lecart_median_voxels"] == 6.0, str(loin))

    s_ = lambda med, lec="ne retrouve pas": {"lecart_median_en_pas": med, "la_lecture": lec}  # noqa: E731
    p_ = lambda x: {"lecart_median_en_pas": x}  # noqa: E731
    m_ = lambda x: {"lecart_median_voxels": x}  # noqa: E731
    v("★★★★ -7 à 1,4 pas de -6 : décalé, quoi que fasse la surface", la_cause(s_(0.1), p_(1.4), m_(1.0)) == LES_CAUSES[0])
    v("★★★★ -7 à 6 voxels de m7 : décalé", la_cause(s_(0.1), p_(1.0), m_(6.0)) == LES_CAUSES[0])
    v("★★★★ -7 à sa place, la surface à 0,4 pas de lui : elle tombe à côté", la_cause(s_(-0.4), p_(1.0), m_(1.0)) == LES_CAUSES[1])
    v("★★★ -7 non lu en face de la surface : elle tombe à côté", la_cause(s_(0.0, "non lue"), p_(1.0), m_(1.0)) == LES_CAUSES[1])
    v("★★★ -7 à sa place, la surface à 0,1 pas : sur -7 en médiane", la_cause(s_(0.1), p_(0.9), m_(1.0)) == LES_CAUSES[2])
    v("★★★ sans écart entre les tours, non mesurable", la_cause(s_(0.1), p_(None), m_(1.0)) == "non mesurable")

    t_ = lambda *r: {str(t): ("retrouve" if t in r else "ne retrouve pas") for t in range(0, -8, -1)}  # noqa: E731
    cote = {"le_tour_de_depart": 0, "la_descente": 6, "larret": "un tour manqué", "les_tours_de_la_nappe": t_(),
            "les_surfaces": [{"les_tours": t_(-i)} for i in range(0, 7)] + [{"les_tours": t_()}]}
    bout = dict(cote, larret="le bout de la chaîne")
    court = dict(cote, la_descente=3, les_surfaces=[{"les_tours": t_(-i)} for i in range(0, 4)] + [{"les_tours": t_()}] * 4)
    gs = [{"le_rang": 1, "les_cotes": {"moins": cote}}, {"le_rang": 2, "les_cotes": {"moins": bout}},
          {"le_rang": 3, "les_cotes": {"moins": court}}]
    v("★★★★★ la septième surface : celle qui suit la surface sur -6, et seulement quand la descente a atteint -6",
      les_septiemes(gs) == [(1, 8)], str(les_septiemes(gs)))

    c_ = lambda x: {"la_cause": x}  # noqa: E731
    base = {"les_pannes": [], "redonne_335": True}
    vd = le_verdict(dict(base, les_septiemes=[c_(LES_CAUSES[0]), c_(LES_CAUSES[0]), c_(LES_CAUSES[1])]))
    v("★★★★ deux sur trois décalés : c'est le référent qui manque", vd["lissue"].endswith("c'est le référent qui manque"), vd["lissue"])
    vd = le_verdict(dict(base, les_septiemes=[c_(LES_CAUSES[1]), c_(LES_CAUSES[1]), c_(LES_CAUSES[0]), c_("non mesurable")]))
    v("★★★★ deux sur trois à côté : c'est le septième saut, et le non mesurable ne compte pas",
      vd["lissue"].endswith("c'est le septième saut qui tombe à côté") and vd["n"] == 3)
    vd = le_verdict(dict(base, les_septiemes=[c_(LES_CAUSES[1]), c_(LES_CAUSES[0])]))
    v("★★★ à égalité, la lecture ne tranche pas", vd["lissue"].endswith("la lecture ne tranche pas"))
    v("★★★★ une chaîne qui ne redonne pas 335 est indécidable",
      not le_verdict(dict(base, redonne_335=False, les_septiemes=[c_(LES_CAUSES[0])]))["decidable"])
    v("★★★ sans septième surface mesurable, indécidable", not le_verdict(dict(base, les_septiemes=[c_("non mesurable")]))["decidable"])

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
