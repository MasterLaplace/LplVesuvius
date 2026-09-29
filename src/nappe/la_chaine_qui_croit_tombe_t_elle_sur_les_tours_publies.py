"""Saut après saut, la chaîne qui croît de PHercParis4 tombe-t-elle sur les tours consécutifs que l'équipe publie, 5753_0, 5753_-1, 5753_-2 et 5753_-3 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL DE CES TOURS NE SOIT TÉLÉCHARGÉ. Ce qui était vu avant d'écrire : tout ce que `296` à `328`
publient, dont `R4-F506` (le premier saut qui croît tombe sur le tour suivant du segment, là où il repasse, sur 4 graines sur 8) et la
chaîne de `328` (sur PHercParis4, 2,5 sauts au pas en médiane, huit sur la graine 6 côté moins, sans référent au-delà du premier). Et la
liste du dépôt : PHercParis4 publie des tours nommés d'après le segment `20230702185753`, `5753_0` puis `5753_-1` à `5753_-7`, dont les
boîtes englobantes au pas de 2,4 µm recouvrent celle du segment réduit de `296`, et dont l'aire décroît de `5753_0` (916 565 191 voxels²)
à `5753_-2` (801 003 953) : des tours de plus en plus intérieurs. Aucune de leurs géométries n'a été lue.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P126` VU PAR SON RÉFÉRENT. Le segment de `296` ne repasse qu'une fois autour des graines ;
ces tours publiés donnent une réponse connue à chaque saut, jusqu'au troisième.

## Ce qui est fait

- **Les tours** : `5753_0`, `5753_-1`, `5753_-2` et `5753_-3`, dans le repère au pas de 2,4 µm du volume `20260411134726`, rangés dans
  `data/tours_publies_5753/`.
- **Les graines et la nappe** : les huit graines de `321` et la nappe qui croît de `322`, sans rien y changer.
- **La chaîne** : de chaque côté, trois sauts qui croissent de `306`, au pas de PHercParis4, chacun parti de la spire du précédent.
- **La comparaison** : celle de `321`, sur les sommets de chaque tour publié proches de la surface comparée (dans sa boîte englobante
  élargie de 100 voxels) : l'écart signé le long de la normale du tour, en face à au plus 40 voxels de côté. Une surface **retrouve** un
  tour par la règle de `321`.

## Les issues

Par graine : **le tour de la nappe** est le tour publié qu'elle retrouve, s'il y en a un seul. Par côté, **la chaîne descend les tours
jusqu'au saut h** si, pour chaque saut j de 1 à h, sa spire retrouve le tour de la nappe moins j. Par graine, h est le plus grand des
deux côtés. L'issue de la tranche : **sur k des huit graines, la chaîne qui croît tombe au premier saut sur le tour publié suivant, et
elle descend les tours jusqu'au saut h en médiane sur ces k graines.** Une graine dont la nappe ne retrouve aucun tour, ou plusieurs,
n'est pas lue.

## Rapporté à côté, qui ne décide rien

Pour chaque surface et chaque tour : les sommets en face, l'écart médian et la part à un quart de pas.

⚠ Ajouté après la première mesure, le 2026-09-29, sans toucher à la règle : **les passages d'un tour au suivant**. La première mesure a
rendu six nappes sur huit posées sur aucun des quatre tours publiés, et des chaînes qui, une fois sur l'un d'eux, tombent sur le suivant.
Un passage est compté chaque fois qu'une surface de la chaîne, nappe comprise, retrouve un seul tour w : il réussit si la surface
suivante retrouve le tour w − 1, il échoue sinon ; une surface suivante qui n'est pas lue ne compte pas.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que valent ces tours publiés comme vérité, eux-mêmes tracés par une méthode que ce dépôt n'a pas
jugée ; ni ce que vaut la chaîne au-delà du troisième saut.

Usage :
    uv run python src/nappe/la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.py --verifier
    uv run python src/nappe/la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.py --telecharger
    uv run python src/nappe/la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.py \\
        --json docs/mesures/la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.json
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
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402

LE_DOSSIER = RACINE / "data" / "tours_publies_5753"
LES_TOURS = {0: "20260602225659-5753_0", -1: "20260603005223-5753_-1", -2: "20260603024952-5753_-2",
             -3: "20260603042357-5753_-3"}
LE_MAILLAGE = "on-20260411134726-2.4um.tifxyz"
LES_SAUTS = 3
LA_MARGE = 100.0


def le_dossier_du_tour(rang: int, tours: dict = LES_TOURS) -> Path:
    return LE_DOSSIER / tours[rang]


def telecharger(tours: dict = LES_TOURS) -> dict:
    """Les tours, leur maillage au pas de 2,4 µm seulement, un fichier après l'autre ; un fichier déjà là n'est pas relu. `330` en
    demande quatre de plus."""
    import urllib.request

    from zarr_depth import BUCKET

    out = {}
    for rang, nom in tours.items():
        id_ = nom.split("-")[0]
        dossier = le_dossier_du_tour(rang, tours)
        dossier.mkdir(parents=True, exist_ok=True)
        for f in ("meta.json", "x.tif", "y.tif", "z.tif"):
            cible = dossier / f
            if cible.exists() and cible.stat().st_size > 0:
                continue
            url = f"{BUCKET}/PHercParis4/segments/{nom}/mesh/{id_}-{LE_MAILLAGE}/{f}"
            tmp = cible.with_suffix(cible.suffix + ".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(cible)
        out[nom] = sum((dossier / f).stat().st_size for f in ("meta.json", "x.tif", "y.tif", "z.tif"))
        print(nom, out[nom], flush=True)
    return out


def le_tour_de_la_nappe(lectures: dict) -> int | None:
    """Le tour publié que la nappe retrouve, s'il y en a un seul."""
    tours = [t for t, l_ in lectures.items() if l_ == "retrouve"]
    return tours[0] if len(tours) == 1 else None


def la_descente(tour_de_la_nappe: int | None, spires: list[dict]) -> int:
    """Le plus grand h tel que la spire j retrouve le tour de la nappe moins j, pour chaque j de 1 à h."""
    if tour_de_la_nappe is None:
        return 0
    h = 0
    for j, lectures in enumerate(spires, 1):
        if lectures.get(tour_de_la_nappe - j) != "retrouve":
            break
        h += 1
    return h


def les_passages(surfaces: list[dict]) -> dict:
    """Rapporté : de chaque surface qui retrouve un seul tour w à la suivante, si elle retrouve w − 1 ; les surfaces sont données dans
    l'ordre de la chaîne, nappe comprise, chacune comme {tour : lecture}."""
    reussis, echoues = 0, 0
    for avant, apres in zip(surfaces, surfaces[1:]):
        w = le_tour_de_la_nappe(avant)
        if w is None or (w - 1) not in apres:
            continue
        if apres[w - 1] == "retrouve":
            reussis += 1
        elif apres[w - 1] != "non lue":
            echoues += 1
    return {"reussis": reussis, "echoues": echoues}


def les_sommets_proches(tour: dict, pts: np.ndarray, marge: float = LA_MARGE) -> tuple[np.ndarray, np.ndarray]:
    """Les sommets du tour, avec leurs normales, dans la boîte englobante des points élargie de `marge`."""
    if not len(pts):
        return np.zeros((0, 3)), np.zeros((0, 3))
    lo, hi = pts.min(axis=0) - marge, pts.max(axis=0) + marge
    m = ((tour["points"] >= lo) & (tour["points"] <= hi)).all(axis=1)
    return tour["points"][m], tour["normales"][m]


def lire_un_tour(rang: int, tours: dict = LES_TOURS) -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    p, ok, esp = lire_tifxyz(le_dossier_du_tour(rang, tours))
    n, nok = les_normales(p, ok)
    m = ok & nok
    return {"points": p[m], "normales": n[m], "lespacement": esp, "les_sommets": int(m.sum())}


def les_lectures(surface_pts: np.ndarray, tours: dict) -> dict:
    """Pour chaque tour publié, ce que la comparaison de `321` dit de la surface."""
    out = {}
    for rang, tour in tours.items():
        ref, ref_n = les_sommets_proches(tour, surface_pts)
        t = m321.les_ecarts(ref, ref_n, surface_pts)
        out[rang] = m321.la_coincidence(t)
    return out


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    lues = [g for g in d["les_graines"] if g["le_tour_de_la_nappe"] is not None]
    if not lues:
        return {"decidable": False, "lissue": "indécidable : aucune nappe ne retrouve un seul tour publié"}
    tombent = [g for g in lues if g["la_descente"] >= 1]
    h = float(np.median([g["la_descente"] for g in tombent])) if tombent else 0.0
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    return {"decidable": True, "k": len(tombent), "lues": len(lues), "h": h,
            "lissue": f"sur {len(tombent)} des {len(lues)} graines lues, la chaîne qui croît tombe au premier saut sur le tour publié "
                      f"suivant, et elle descend les tours jusqu'au saut {f_(h)} en médiane sur ces graines"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    tours = {r: lire_un_tour(r) for r in LES_TOURS}
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        nappe_pts = r["la_nappe"][r["valide"]] * m321.LE_FACTEUR
        lect_nappe = les_lectures(nappe_pts, tours)
        tour0 = le_tour_de_la_nappe({t: x["la_lecture"] for t, x in lect_nappe.items()})
        e = {"le_rang": rang, "la_nappe": {str(t): x for t, x in lect_nappe.items()}, "le_tour_de_la_nappe": tour0, "les_cotes": {}}
        descentes = []
        for nom, cote in m306.LES_COTES:
            surf, ok = r["la_nappe"], r["valide"]
            spires = []
            with m321.le_rouleau_de_paris4():
                for _ in range(LES_SAUTS):
                    s = m306.le_saut_croissant(surf, ok, cote, lv4, tolerance=m322.LA_TOLERANCE_L2)
                    pts = s["la_spire"][s["valide"]] * m321.LE_FACTEUR
                    spires.append({"la_part_du_plan": round(float(s["valide"].mean()), 4),
                                   "les_tours": {str(t): x for t, x in les_lectures(pts, tours).items()}})
                    if not s["valide"].any():
                        break
                    surf, ok = s["la_spire"], s["valide"]
            lect = [{int(t): x["la_lecture"] for t, x in sp["les_tours"].items()} for sp in spires]
            h = la_descente(tour0, lect)
            nappe_l = {int(t): x["la_lecture"] for t, x in lect_nappe.items()}
            e["les_cotes"][nom] = {"les_spires": spires, "la_descente": h, "les_passages": les_passages([nappe_l] + lect)}
            descentes.append(h)
        e["la_descente"] = max(descentes)
        graines.append(e)
        print(json.dumps({"le_rang": rang, "le_tour_de_la_nappe": tour0, "la_descente": e["la_descente"],
                          "par_cote": {c: v["la_descente"] for c, v in e["les_cotes"].items()}}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_tours": {str(k): v for k, v in LES_TOURS.items()}, "le_maillage": LE_MAILLAGE,
                            "les_sauts": LES_SAUTS, "la_marge_voxels": LA_MARGE},
         "les_tours_lus": {str(k): {"les_sommets": v["les_sommets"], "lespacement": v["lespacement"]} for k, v in tours.items()},
         "les_pannes": list(stats4["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats4.items() if k != "pannes"},
         "les_graines": graines}
    d["les_passages"] = {k: sum(c["les_passages"][k] for g in graines for c in g["les_cotes"].values()) for k in ("reussis", "echoues")}
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

    v("★★★ le tour de la nappe : un seul retrouvé", le_tour_de_la_nappe({0: "retrouve", -1: "ne retrouve pas"}) == 0)
    v("★★★ deux tours retrouvés : aucun", le_tour_de_la_nappe({0: "retrouve", -1: "retrouve"}) is None)
    v("★★★ aucun : aucun", le_tour_de_la_nappe({0: "non lue", -1: "ne retrouve pas"}) is None)
    sp = [{-1: "retrouve"}, {-2: "retrouve"}, {-3: "ne retrouve pas"}]
    v("★★★★ la descente s'arrête au premier saut qui manque son tour", la_descente(0, sp) == 2)
    v("★★★★ un tour retrouvé après un tour manqué ne compte pas",
      la_descente(0, [{-1: "retrouve"}, {-2: "ne retrouve pas"}, {-3: "retrouve"}]) == 1)
    v("★★★★ une spire sur le tour de la nappe lui-même ne descend pas", la_descente(0, [{0: "retrouve", -1: "ne retrouve pas"}]) == 0)
    v("★★★ une nappe sur le tour -1 descend vers -2", la_descente(-1, [{-2: "retrouve"}]) == 1)
    v("★★★ sans tour de la nappe, pas de descente", la_descente(None, sp) == 0)
    k = np.arange(-10, 11) * 20.0
    plan = np.stack(np.meshgrid(k, k, indexing="ij"), -1).reshape(-1, 2)
    tour = {"points": np.concatenate([plan, np.full((len(plan), 1), 72.0)], axis=1),
            "normales": np.tile([0.0, 0.0, 1.0], (len(plan), 1))}
    lointain = {"points": tour["points"] + np.array([5000.0, 0.0, 0.0]), "normales": tour["normales"]}
    surf = np.concatenate([plan[::2], np.full((len(plan[::2]), 1), 70.0)], axis=1)
    lect = les_lectures(surf, {-1: tour, -2: lointain})
    v("★★★★ une surface à 2 voxels du tour le retrouve ; un tour lointain n'est pas lu", lect[-1]["la_lecture"] == "retrouve"
      and lect[-2]["la_lecture"] == "non lue", str({t: x["la_lecture"] for t, x in lect.items()}))
    ref, _ = les_sommets_proches(lointain, surf)
    v("★★★ seuls les sommets proches du tour sont comparés", len(ref) == 0)
    ps = les_passages([{0: "ne retrouve pas"}, {0: "retrouve", -1: "ne retrouve pas"}, {-1: "retrouve", 0: "ne retrouve pas"},
                       {-2: "ne retrouve pas", -1: "ne retrouve pas"}, {-3: "non lue"}])
    v("★★★★ les passages : 0 puis -1 réussit, -1 puis -2 manqué échoue, rien avant ni après ne compte", ps == {"reussis": 1,
      "echoues": 1}, str(ps))
    v("★★★ une surface suivante non lue sur le tour attendu ne compte pas",
      les_passages([{-2: "retrouve"}, {-3: "non lue"}]) == {"reussis": 0, "echoues": 0})
    v("★★★ une surface qui retrouve deux tours n'ouvre pas de passage",
      les_passages([{0: "retrouve", -1: "retrouve"}, {-1: "retrouve", -2: "retrouve"}]) == {"reussis": 0, "echoues": 0})
    g = lambda t, h: {"le_tour_de_la_nappe": t, "la_descente": h}  # noqa: E731
    vd = le_verdict({"les_pannes": [], "les_graines": [g(0, 3), g(0, 1), g(0, 0), g(None, 0)]})
    v("★★★ l'issue : k des graines lues, h médian sur celles qui tombent", vd["k"] == 2 and vd["lues"] == 3 and vd["h"] == 2.0, str(vd))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--telecharger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.telecharger:
        print(json.dumps(telecharger(), ensure_ascii=False))
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
