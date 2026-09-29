"""Autour des graines 1 à 3, les tours publiés voisins se recouvrent-ils par endroits, deux tours posés sur la même feuille, et pas autour des autres graines ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE MOINDRE RECOUVREMENT ENTRE TOURS PUBLIÉS NE SOIT MESURÉ. Ce qui était vu avant d'écrire : tout ce
que `296` à `340` publient, dont `R4-F526` (jugées strictement, aucune chaîne ne descend un seul tour sur les graines 2 et 3, au plus trois
sur la graine 1, quelle que soit la relance), `R4-F523` (autour des huit graines, l'écart médian d'un tour publié au suivant va de 0,53 à 0,93
pas nominal, et une surface à mi-chemin n'est retrouvée des deux par aucune paire) et `R4-F525` (les surfaces à deux tours ne traversent
pas la couture).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P137`. Un écart médian de 0,6 pas n'interdit pas que deux tours voisins soient confondus sur une
partie de leur surface : si un tour publié passe, par endroits, sur la feuille de son voisin, une surface posée sur cette feuille retrouve
les deux, et aucune chaîne ne peut descendre strictement là.

## Ce qui est fait

- **Les boîtes et les paires** : celles de `337`, sans rien y changer : un cube de 1280 voxels de demi-côté autour de chacune des huit
  graines, et chaque paire de tours consécutifs de `5753_0` et `5753_-1` à `5753_-6` et `5753_-7`, au plus 20 000 sommets du premier.
- **Le recouvrement** : la part des sommets du premier tour qui ont le second en face, par la comparaison de `321`, à au plus un quart du pas
  nominal (18,02 voxels) : là, les deux tours sont sur la même feuille à la tolérance de la lecture.
- **La règle** : deux tours voisins se recouvrent autour d'une graine si au moins 5 % des sommets du premier qui ont le second en face, et
  au moins 200 sommets, sont à un quart de pas de lui.

## Les issues

L'issue de la tranche : **autour des graines 1 à 3, a des n1 paires mesurées se recouvrent ; autour des graines 4 à 8, b des n2** ; et,
déclaré avant : **les tours se recouvrent autour des graines 1 à 3 et pas ailleurs** si a > n1/2 et b < n2/2 ; **ils ne se recouvrent pas
autour des graines 1 à 3** si a < n1/2 ; **le recouvrement ne distingue pas les graines 1 à 3** sinon.

## Rapporté à côté, qui ne décide rien

La part à un quart de pas de chaque paire autour de chaque graine.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : lequel des deux tours est à la mauvaise place là où ils se recouvrent ; ni si les surfaces à deux tours
de la descente y sont posées.

Usage :
    uv run python src/nappe/les_tours_publies_voisins_se_recouvrent_ils.py --verifier
    uv run python src/nappe/les_tours_publies_voisins_se_recouvrent_ils.py \\
        --json docs/mesures/les_tours_publies_voisins_se_recouvrent_ils.json
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

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas as m337  # noqa: E402

LA_PART = 0.05
LE_MINIMUM = 200
LES_GRAINES_DU_PROBLEME = (1, 2, 3)


def le_recouvrement(ta: dict, tb: dict, centre: np.ndarray) -> dict:
    """La part des sommets de `ta` dans la boîte qui ont `tb` en face à au plus un quart du pas nominal."""
    a, an = m337.dans_la_boite(ta, centre)
    b, _ = m337.dans_la_boite(tb, centre, maximum=10 ** 9)
    if not len(a) or not len(b):
        return {"les_sommets_en_face": 0, "a_un_quart": 0, "la_part": None}
    t = m321.les_ecarts(a, an, b)
    t = np.abs(t[np.isfinite(t)])
    k = int((t <= m321.LE_QUART).sum())
    return {"les_sommets_en_face": int(len(t)), "a_un_quart": k,
            "la_part": round(k / len(t), 4) if len(t) >= m321.LE_MINIMUM else None}


def se_recouvrent(r: dict) -> bool | None:
    if r["la_part"] is None:
        return None
    return r["la_part"] >= LA_PART and r["a_un_quart"] >= LE_MINIMUM


def le_verdict(d: dict) -> dict:
    un = [p["se_recouvrent"] for g in d["les_graines"] if g["le_rang"] in LES_GRAINES_DU_PROBLEME for p in g["les_paires"]
          if p["se_recouvrent"] is not None]
    autres = [p["se_recouvrent"] for g in d["les_graines"] if g["le_rang"] not in LES_GRAINES_DU_PROBLEME for p in g["les_paires"]
              if p["se_recouvrent"] is not None]
    if not un or not autres:
        return {"decidable": False, "lissue": "indécidable : il manque des paires mesurées"}
    a, b = sum(un), sum(autres)
    tete = (f"autour des graines 1 à 3, {a} des {len(un)} paires mesurées se recouvrent ; autour des graines 4 à 8, {b} des "
            f"{len(autres)}")
    if 2 * a < len(un):
        suite = "ils ne se recouvrent pas autour des graines 1 à 3"
    elif 2 * a > len(un) and 2 * b < len(autres):
        suite = "les tours se recouvrent autour des graines 1 à 3 et pas ailleurs"
    else:
        suite = "le recouvrement ne distingue pas les graines 1 à 3"
    return {"decidable": True, "a": a, "n1": len(un), "b": b, "n2": len(autres), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    t0 = time.monotonic()
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        ps = []
        for ka, kb in m337.LES_PAIRES:
            r = le_recouvrement(tours[ka], tours[kb], seg[i, j])
            ps.append(dict(r, les_tours=[ka, kb], se_recouvrent=se_recouvrent(r)))
        graines.append({"le_rang": rang, "les_paires": ps})
        print(rang, [(p["les_tours"], p["la_part"], p["se_recouvrent"]) for p in ps], flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part": LA_PART, "le_minimum": LE_MINIMUM, "le_quart_voxels": round(m321.LE_QUART, 3),
                            "la_demi_boite_voxels": m337.LA_DEMI_BOITE},
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

    k = np.arange(-400.0, 401.0, 20.0)
    xy = np.stack(np.meshgrid(k, k, indexing="ij"), axis=-1).reshape(-1, 2)
    centre = np.array([1000.0, 1000.0, 400.0])

    def plan(z):
        z = np.broadcast_to(np.asarray(z, dtype=float), (len(xy),))
        pts = np.concatenate([xy + 1000.0, z[:, None]], axis=1)
        return {"points": pts, "normales": np.tile([0.0, 0.0, 1.0], (len(pts), 1))}

    a = plan(400.0)
    loin = plan(400.0 + 0.7 * m321.LE_PAS_L0)
    r = le_recouvrement(a, loin, centre)
    v("★★★★ deux tours à 0,7 pas l'un de l'autre ne se recouvrent nulle part", r["la_part"] == 0.0 and se_recouvrent(r) is False, str(r))
    r = le_recouvrement(a, plan(400.0 - 0.7 * m321.LE_PAS_L0), centre)
    v("★★★★ un second tour 0,7 pas en dessous ne recouvre pas le premier non plus", r["la_part"] == 0.0, str(r))
    r = le_recouvrement(a, plan(400.0 + 25.0), centre)
    v("★★★★ à 25 voxels, au-delà d'un quart de pas mais en deçà d'un demi-pas, ils ne se recouvrent pas", r["la_part"] == 0.0, str(r))
    zs = np.where(xy[:, 0] < -200.0, 400.0 + 5.0, 400.0 + 0.7 * m321.LE_PAS_L0)
    r = le_recouvrement(a, plan(zs), centre)
    v("★★★★★ là où le second passe à 5 voxels du premier, il le recouvre : la part est celle de cette région",
      se_recouvrent(r) is True and 0.15 < r["la_part"] < 0.35 and r["a_un_quart"] >= LE_MINIMUM, str(r))
    zs = np.where((xy[:, 0] < -380.0) & (xy[:, 1] < -380.0), 400.0 + 5.0, 400.0 + 0.7 * m321.LE_PAS_L0)
    r = le_recouvrement(a, plan(zs), centre)
    v("★★★★ un recouvrement de quelques sommets seulement ne compte pas", se_recouvrent(r) is False and r["a_un_quart"] > 0, str(r))
    v("★★★ sans sommets en face, pas de part", le_recouvrement(a, {"points": np.zeros((0, 3)), "normales": np.zeros((0, 3))},
                                                             centre)["la_part"] is None)
    v("★★★ la règle : 5 % et 200 sommets", se_recouvrent({"la_part": 0.05, "a_un_quart": 200}) is True
      and se_recouvrent({"la_part": 0.049, "a_un_quart": 900}) is False and se_recouvrent({"la_part": 0.5, "a_un_quart": 199}) is False)

    p_ = lambda x: {"se_recouvrent": x}  # noqa: E731
    g_ = lambda r, *xs: {"le_rang": r, "les_paires": [p_(x) for x in xs]}  # noqa: E731
    vd = le_verdict({"les_graines": [g_(1, True, True, False), g_(4, False, False, True), g_(5, False, None)]})
    v("★★★★★ plus de la moitié autour des graines 1 à 3, moins ailleurs : ils se recouvrent là et pas ailleurs ; le non mesuré ne compte pas",
      vd["lissue"].endswith("les tours se recouvrent autour des graines 1 à 3 et pas ailleurs") and vd["n2"] == 4, vd["lissue"])
    vd = le_verdict({"les_graines": [g_(2, True, False, False), g_(6, False)]})
    v("★★★★ moins de la moitié autour des graines 1 à 3 : ils ne s'y recouvrent pas",
      vd["lissue"].endswith("ils ne se recouvrent pas autour des graines 1 à 3"))
    vd = le_verdict({"les_graines": [g_(3, True, True), g_(7, True, True, False)]})
    v("★★★★ si ailleurs aussi : le recouvrement ne distingue pas les graines 1 à 3",
      vd["lissue"].endswith("le recouvrement ne distingue pas les graines 1 à 3"))
    v("★★★ sans paire mesurée d'un côté, indécidable", not le_verdict({"les_graines": [g_(1, True)]})["decidable"])

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
