"""Les surfaces de la descente qui retrouvent deux tours publiés voisins passent-elles là où un tour publié finit et le suivant commence ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE SURFACE À DEUX TOURS NE SOIT RAPPORTÉE AU BOUT D'UN TOUR. Ce qui était vu avant d'écrire :
tout ce que `296` à `337` publient, dont `R4-F523` (la lecture sépare toujours deux tours voisins par leur écart, et pourtant 12 des 48
surfaces que la descente de la chaîne bornée compte justes retrouvent deux tours, sur les graines 1, 2, 3 et 8). Et la forme des tours
publiés, lue avant d'écrire : chacun est une grille dont les rangées vont en hauteur, sur toute la hauteur du rouleau, et dont les colonnes
font le tour, à 20 voxels de 2,4 µm l'une de l'autre ; un tour publié finit à sa première et à sa dernière colonne.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P134`. Une feuille enroulée est une seule surface ; la découper en tours met une couture là où
un tour finit et le suivant commence, et de part et d'autre de la couture la feuille porte deux noms. Une surface qui suit la feuille à
travers la couture est sur un tour d'un côté et sur l'autre de l'autre côté : la lecture la donne aux deux, sans qu'elle se soit trompée.

## Ce qui est fait

- **La chaîne** : celle de `335` sur PHercParis4, sans rien y changer ; elle doit redonner `335` côté par côté, sans quoi la tranche est
  indécidable. Chaque nappe relancée est gardée.
- **Les surfaces à deux tours** : côté moins, les surfaces que la descente de `330` compte justes et qui retrouvent deux tours ; et, pour
  comparer, celles qui n'en retrouvent qu'un.
- **Les sommets posés** : pour chaque tour qu'une surface retrouve, ses sommets dans la boîte de la surface élargie de 100 voxels, qui ont
  la surface en face à au plus un quart de pas, comme la lecture de `321` les compte.
- **Le bout du tour** : pour chacun de ces sommets, sa distance, le long de sa rangée, à la première ou à la dernière colonne posée de son
  tour, la plus proche, en voxels de 2,4 µm.
- **La règle** : une surface à deux tours passe par la couture si, pour ses deux tours, la distance médiane de ses sommets posés au bout de
  leur tour est d'au plus 1280 voxels, la demi-largeur du plan des nappes.

## Les issues

L'issue de la tranche : **sur les n surfaces à deux tours, k passent par la couture** ; et, déclaré avant : **elles passent par la couture**
si k > n/2 ; **elles n'y passent pas** si k < n/2 ; **la lecture ne tranche pas** sinon.

## Rapporté à côté, qui ne décide rien

La distance médiane au bout de leur tour des sommets posés des surfaces qui ne retrouvent qu'un tour.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la couture des tours publiés est au bon endroit ; ni ce que vaudrait une descente qui lit la
feuille sans ses tours.

Usage :
    uv run python src/nappe/les_surfaces_a_deux_tours_passent_elles_par_la_couture.py --verifier
    uv run python src/nappe/les_surfaces_a_deux_tours_passent_elles_par_la_couture.py \\
        --json docs/mesures/les_surfaces_a_deux_tours_passent_elles_par_la_couture.json
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
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle as m334  # noqa: E402
import la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse as m335  # noqa: E402

CE_QUE_335_A_PUBLIE = RACINE / "docs" / "mesures" / "la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse.json"
LA_COUTURE = 1280.0                # voxels de 2,4 µm : la demi-largeur du plan des nappes


def les_bouts(ok: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pour chaque rangée, la première et la dernière colonne posées ; -1 pour une rangée vide."""
    a = np.where(ok.any(axis=1), ok.argmax(axis=1), -1)
    b = np.where(ok.any(axis=1), ok.shape[1] - 1 - ok[:, ::-1].argmax(axis=1), -1)
    return a, b


def indexer(p: np.ndarray, ok: np.ndarray, n: np.ndarray, nok: np.ndarray, espacement: float) -> dict:
    """Un tour : ses sommets posés à normale connue, leur rangée et leur colonne, et les bouts de chaque rangée."""
    m = ok & nok
    ii, jj = np.nonzero(m)
    a, b = les_bouts(ok)
    return {"points": p[m], "normales": n[m], "i": ii, "j": jj, "premiere": a, "derniere": b, "lespacement": float(espacement)}


def la_distance_au_bout(tour: dict, k: np.ndarray) -> np.ndarray:
    """Pour les sommets d'indices `k`, la distance le long de leur rangée à la colonne posée la plus proche d'un bout, en voxels."""
    i, j = tour["i"][k], tour["j"][k]
    return np.minimum(j - tour["premiere"][i], tour["derniere"][i] - j) * tour["lespacement"]


def les_sommets_poses(tour: dict, surface: np.ndarray, marge: float = m329.LA_MARGE) -> np.ndarray:
    """Les indices des sommets du tour dans la boîte de la surface élargie de `marge`, qui ont la surface en face à au plus un quart de
    pas."""
    if not len(surface):
        return np.zeros(0, dtype=np.int64)
    lo, hi = surface.min(axis=0) - marge, surface.max(axis=0) + marge
    k = np.flatnonzero(((tour["points"] >= lo) & (tour["points"] <= hi)).all(axis=1))
    t = m321.les_ecarts(tour["points"][k], tour["normales"][k], surface)
    return k[np.isfinite(t) & (np.abs(t) <= m321.LE_QUART)]


def les_surfaces_comptees(graines: list[dict]) -> list[dict]:
    """Côté moins, les surfaces que la descente de `330` compte justes, avec le rang du saut et les tours qu'elles retrouvent."""
    out = []
    for g in graines:
        c = g["les_cotes"]["moins"]
        surfaces = [{int(t): x for t, x in c["les_tours_de_la_nappe"].items()}]
        surfaces += [{int(t): x for t, x in s["les_tours"].items()} if "les_tours" in s else {} for s in c["les_surfaces"]]
        k0 = next((k for k, s in enumerate(surfaces) if m329.le_tour_de_la_nappe(s) is not None), None)
        if k0 is None:
            continue
        for h in range(k0 + 1, k0 + 1 + c["la_descente"]):
            r = sorted((t for t, x in surfaces[h].items() if x == "retrouve"), reverse=True)
            out.append({"le_rang": g["le_rang"], "le_saut": h, "les_tours_retrouves": r})
    return out


def passe_par_la_couture(distances: dict) -> bool | None:
    """Une surface à deux tours passe par la couture si la distance médiane au bout est d'au plus `LA_COUTURE` pour ses deux tours ;
    None si l'un des deux n'a aucun sommet posé."""
    if len(distances) != 2 or any(x is None for x in distances.values()):
        return None
    return all(x <= LA_COUTURE for x in distances.values())


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_335"):
        return {"decidable": False, "lissue": "indécidable : la chaîne ne redonne pas celle de 335"}
    ss = [s for s in d["les_surfaces_a_deux_tours"] if s["passe_par_la_couture"] is not None]
    if not ss:
        return {"decidable": False, "lissue": "indécidable : aucune surface à deux tours mesurable"}
    k = sum(1 for s in ss if s["passe_par_la_couture"])
    tete = f"sur les {len(ss)} surfaces à deux tours, {k} passent par la couture"
    suite = ("elles passent par la couture" if 2 * k > len(ss) else "elles n'y passent pas" if 2 * k < len(ss)
             else "la lecture ne tranche pas")
    return {"decidable": True, "n": len(ss), "k": k, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    t0 = time.monotonic()
    gardees = {}

    def garder(rang, nom, h, k):
        rl = k["la_relance"]
        if nom == "moins" and rl is not None and rl["valide"].any():
            gardees[(rang, h)] = rl["la_nappe"][rl["valide"]] * m321.LE_FACTEUR
        return {}

    d = m331.mesurer(relancer4=m335.la_relance_de_paris4, avec_la_spire=True, lire_la_spire=True, rouleaux=("PHercParis4",),
                     observer=garder)
    d.pop("les_cotes", None)
    d["la_question"] = __doc__.splitlines()[0]
    d["redonne_335"] = m334.redonne_333(d, json.loads(CE_QUE_335_A_PUBLIE.read_text()))
    comptees = les_surfaces_comptees(d["les_graines"]["PHercParis4"])
    tours = {}

    def le_tour(r):
        if r not in tours:
            p, ok, esp = lire_tifxyz(m329.le_dossier_du_tour(r, m330.LES_TOURS))
            n, nok = les_normales(p, ok)
            tours[r] = indexer(p, ok, n, nok, esp)
        return tours[r]

    deux, un = [], []
    for s in comptees:
        surf = gardees.get((s["le_rang"], s["le_saut"]))
        e = dict(s, les_points=0 if surf is None else int(len(surf)), les_distances_au_bout={}, les_sommets_poses={})
        for r in s["les_tours_retrouves"]:
            k = les_sommets_poses(le_tour(r), surf) if surf is not None else np.zeros(0, dtype=np.int64)
            e["les_sommets_poses"][str(r)] = int(len(k))
            e["les_distances_au_bout"][str(r)] = round(float(np.median(la_distance_au_bout(le_tour(r), k))), 1) if len(k) else None
        if len(s["les_tours_retrouves"]) >= 2:
            e["passe_par_la_couture"] = passe_par_la_couture(e["les_distances_au_bout"])
            deux.append(e)
        else:
            un.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d["les_surfaces_a_deux_tours"] = deux
    d["les_surfaces_a_un_tour"] = un
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

    ok = np.zeros((3, 10), dtype=bool)
    ok[0, 2:8] = True
    ok[1, :] = True
    a, b = les_bouts(ok)
    v("★★★★ les bouts d'une rangée : sa première et sa dernière colonne posées ; -1 pour une rangée vide",
      list(a) == [2, 0, -1] and list(b) == [7, 9, -1], f"{a} {b}")

    h, w, esp = 4, 40, 20.0
    jj, ii = np.meshgrid(np.arange(w, dtype=float), np.arange(h, dtype=float))
    p = np.stack([jj * esp, ii * esp, np.full((h, w), 100.0)], axis=-1)
    n = np.zeros((h, w, 3))
    n[..., 2] = 1.0
    okg = np.ones((h, w), dtype=bool)
    okg[2, 30:] = False
    tour = indexer(p, okg, n, np.ones((h, w), dtype=bool), esp)
    k = np.flatnonzero((tour["i"] == 2) & (tour["j"] == 27))
    v("★★★★★ la distance au bout se compte sur la rangée du sommet, jusqu'à sa colonne posée la plus proche",
      la_distance_au_bout(tour, k)[0] == 2 * esp and la_distance_au_bout(tour, np.flatnonzero((tour["i"] == 1) & (tour["j"] == 3)))[0]
      == 3 * esp)
    surface = np.stack([np.arange(100.0, 300.0, 10.0), np.full(20, 30.0), np.full(20, 110.0)], axis=1)
    ks = les_sommets_poses(tour, surface)
    v("★★★★ les sommets posés : ceux qui ont la surface en face à un quart de pas", len(ks) > 0
      and np.all(np.abs(tour["points"][ks][:, 2] - 100.0) == 0.0), str(len(ks)))
    v("★★★★ une surface à plus d'un quart de pas ne pose aucun sommet",
      len(les_sommets_poses(tour, surface + np.array([0.0, 0.0, 30.0]))) == 0)

    v("★★★★ les deux tours près de leur bout : la surface passe par la couture",
      passe_par_la_couture({"-2": 300.0, "-3": 900.0}) is True)
    v("★★★★ un seul des deux près de son bout : elle n'y passe pas", passe_par_la_couture({"-2": 300.0, "-3": 4000.0}) is False)
    v("★★★ un tour sans sommet posé : non mesurable", passe_par_la_couture({"-2": 300.0, "-3": None}) is None)

    t_ = lambda *r: {str(x): ("retrouve" if x in r else "ne retrouve pas") for x in range(0, -8, -1)}  # noqa: E731
    cote = {"la_descente": 3, "les_tours_de_la_nappe": t_(),
            "les_surfaces": [{"les_tours": t_(0)}, {"les_tours": t_(-1)}, {"les_tours": t_(-2)}, {"les_tours": t_(-3, -4)},
                             {"les_tours": t_(-3, -4)}]}
    cs = les_surfaces_comptees([{"le_rang": 4, "les_cotes": {"moins": cote}}])
    v("★★★★★ les surfaces comptées : de la suivante du départ au dernier saut juste, avec leurs tours",
      [(c["le_saut"], c["les_tours_retrouves"]) for c in cs] == [(2, [-1]), (3, [-2]), (4, [-3, -4])], str(cs))

    c_ = lambda x: {"passe_par_la_couture": x}  # noqa: E731
    base = {"les_pannes": [], "redonne_335": True}
    vd = le_verdict(dict(base, les_surfaces_a_deux_tours=[c_(True), c_(True), c_(False), c_(None)]))
    v("★★★★ deux sur trois : elles passent par la couture ; le non mesurable ne compte pas",
      vd["lissue"].endswith("elles passent par la couture") and vd["n"] == 3)
    vd = le_verdict(dict(base, les_surfaces_a_deux_tours=[c_(False), c_(False), c_(True)]))
    v("★★★★ une sur trois : elles n'y passent pas", vd["lissue"].endswith("elles n'y passent pas"))
    vd = le_verdict(dict(base, les_surfaces_a_deux_tours=[c_(False), c_(True)]))
    v("★★★ une sur deux : la lecture ne tranche pas", vd["lissue"].endswith("la lecture ne tranche pas"))
    v("★★★★ une chaîne qui ne redonne pas 335 est indécidable",
      not le_verdict(dict(base, redonne_335=False, les_surfaces_a_deux_tours=[c_(True)]))["decidable"])

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
