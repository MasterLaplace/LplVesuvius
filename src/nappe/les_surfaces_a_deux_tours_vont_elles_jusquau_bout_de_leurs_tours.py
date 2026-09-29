"""Les sommets posés d'une surface qui retrouve deux tours publiés voisins vont-ils jusqu'au bout de chacun de ses deux tours, là où ceux d'une surface qui n'en retrouve qu'un s'arrêtent avant ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE MOINDRE SOMMET POSÉ NE SOIT COMPTÉ AU BOUT DE SON TOUR. Ce qui était vu avant d'écrire : tout ce que
`296` à `338` publient, dont `R4-F524` (dix des douze surfaces à deux tours de la descente de la chaîne bornée ont leurs sommets posés à
moins de 1280 voxels, en médiane, du bout de leurs deux tours, mais vingt des trente-six surfaces à un tour aussi : la médiane ne sépare
rien, toute la région des graines étant près du bout des tours publiés).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P135`. Une surface qui traverse la couture entre deux tours est posée sur chacun jusqu'à son
bout : sur l'un jusqu'à sa dernière colonne, sur l'autre depuis sa première, et la feuille y est continue. Une surface qui s'arrête avant
la couture ne touche le bout d'aucun tour. Ce n'est pas la distance médiane qui le dit, c'est la présence de sommets posés au bout même.

## Ce qui est fait

- **La chaîne et les surfaces comptées** : celles de `338`, sans rien y changer ; la chaîne doit redonner `335`, sans quoi la tranche est
  indécidable.
- **Les sommets posés** : ceux de `338`, les sommets de chaque tour retrouvé qui ont la surface en face à au plus un quart de pas.
- **Au bout** : un sommet posé est au bout de son tour s'il est à au plus 60 voxels, trois colonnes, de la première ou de la dernière colonne
  posée de sa rangée. Un tour est touché jusqu'au bout par une surface si au moins 10 de ses sommets posés y sont.
- **La règle** : une surface à deux tours traverse la couture si elle touche ses deux tours jusqu'au bout ; une surface à un tour va jusqu'au
  bout si elle touche son tour jusqu'au bout.

## Les issues

L'issue de la tranche : **k2 des n2 surfaces à deux tours traversent la couture, et k1 des n1 surfaces à un tour vont jusqu'au bout** ; et,
déclaré avant : **les surfaces à deux tours traversent la couture** si k2 > n2/2 et k1 < n1/2 ; **elles ne la traversent pas** si
k2 < n2/2 ; **le bout ne les sépare pas des surfaces à un tour** sinon.

## Rapporté à côté, qui ne décide rien

Pour chaque surface à deux tours qui touche ses deux tours jusqu'au bout, le bout touché de chacun (première ou dernière colonne), et la
distance médiane de ses sommets posés au bout d'un tour aux sommets posés au bout de l'autre : si la feuille est continue à la couture, ils
sont à moins d'un quart de pas les uns des autres.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la couture des tours publiés est au bon endroit.

Usage :
    uv run python src/nappe/les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.py --verifier
    uv run python src/nappe/les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.py \\
        --json docs/mesures/les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.json
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
import les_surfaces_a_deux_tours_passent_elles_par_la_couture as m338  # noqa: E402

LE_SEUIL = 60.0                    # voxels de 2,4 µm : trois colonnes des tours publiés
LE_MINIMUM_AU_BOUT = 10


def au_bout(tour: dict, k: np.ndarray, seuil: float = LE_SEUIL) -> dict:
    """Parmi les sommets d'indices `k`, ceux qui sont à au plus `seuil` voxels de la première ou de la dernière colonne posée de leur rangée."""
    i, j = tour["i"][k], tour["j"][k]
    e = tour["lespacement"]
    premier = (j - tour["premiere"][i]) * e <= seuil
    dernier = (tour["derniere"][i] - j) * e <= seuil
    return {"au_premier": k[premier], "au_dernier": k[dernier & ~premier]}


def touche_le_bout(bouts: dict, minimum: int = LE_MINIMUM_AU_BOUT) -> bool:
    return len(bouts["au_premier"]) + len(bouts["au_dernier"]) >= minimum


def va_jusquau_bout(bouts_par_tour: dict) -> bool:
    """Une surface va jusqu'au bout si elle touche jusqu'au bout chacun des tours qu'elle retrouve."""
    return bool(bouts_par_tour) and all(touche_le_bout(b) for b in bouts_par_tour.values())


def le_bout_touche(bouts: dict) -> str:
    return "le premier" if len(bouts["au_premier"]) >= len(bouts["au_dernier"]) else "le dernier"


def la_continuite(a: np.ndarray, b: np.ndarray) -> float | None:
    """La distance médiane, en voxels, de chaque point de `a` au point de `b` le plus proche ; None si l'un est vide."""
    from scipy.spatial import cKDTree

    if not len(a) or not len(b):
        return None
    dist, _ = cKDTree(b).query(a)
    return round(float(np.median(dist)), 1)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_335"):
        return {"decidable": False, "lissue": "indécidable : la chaîne ne redonne pas celle de 335"}
    deux, un = d["les_surfaces_a_deux_tours"], d["les_surfaces_a_un_tour"]
    if not deux or not un:
        return {"decidable": False, "lissue": "indécidable : il manque des surfaces à comparer"}
    k2 = sum(1 for s in deux if s["jusquau_bout"])
    k1 = sum(1 for s in un if s["jusquau_bout"])
    tete = (f"{k2} des {len(deux)} surfaces à deux tours traversent la couture, et {k1} des {len(un)} surfaces à un tour vont jusqu'au "
            f"bout")
    if 2 * k2 < len(deux):
        suite = "elles ne la traversent pas"
    elif 2 * k2 > len(deux) and 2 * k1 < len(un):
        suite = "les surfaces à deux tours traversent la couture"
    else:
        suite = "le bout ne les sépare pas des surfaces à un tour"
    return {"decidable": True, "k2": k2, "n2": len(deux), "k1": k1, "n1": len(un), "lissue": f"{tete} ; {suite}"}


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
    d["redonne_335"] = m334.redonne_333(d, json.loads(m338.CE_QUE_335_A_PUBLIE.read_text()))
    tours = {}

    def le_tour(r):
        if r not in tours:
            p, ok, esp = lire_tifxyz(m329.le_dossier_du_tour(r, m330.LES_TOURS))
            n, nok = les_normales(p, ok)
            tours[r] = m338.indexer(p, ok, n, nok, esp)
        return tours[r]

    deux, un = [], []
    for s in m338.les_surfaces_comptees(d["les_graines"]["PHercParis4"]):
        surf = gardees.get((s["le_rang"], s["le_saut"]))
        e = dict(s, les_sommets_poses={}, au_bout={}, les_bouts_touches={})
        bouts = {}
        for r in s["les_tours_retrouves"]:
            k = m338.les_sommets_poses(le_tour(r), surf) if surf is not None else np.zeros(0, dtype=np.int64)
            bouts[r] = au_bout(le_tour(r), k)
            e["les_sommets_poses"][str(r)] = int(len(k))
            e["au_bout"][str(r)] = int(len(bouts[r]["au_premier"]) + len(bouts[r]["au_dernier"]))
            e["les_bouts_touches"][str(r)] = le_bout_touche(bouts[r])
        e["jusquau_bout"] = va_jusquau_bout(bouts)
        if len(s["les_tours_retrouves"]) >= 2:
            if e["jusquau_bout"]:
                a_, b_ = s["les_tours_retrouves"][:2]
                pa = le_tour(a_)["points"][np.concatenate([bouts[a_]["au_premier"], bouts[a_]["au_dernier"]])]
                pb = le_tour(b_)["points"][np.concatenate([bouts[b_]["au_premier"], bouts[b_]["au_dernier"]])]
                e["la_continuite_voxels"] = la_continuite(pa, pb)
            deux.append(e)
        else:
            un.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    d["les_surfaces_a_deux_tours"] = deux
    d["les_surfaces_a_un_tour"] = un
    d["les_constantes"].update(le_seuil_voxels=LE_SEUIL, le_minimum_au_bout=LE_MINIMUM_AU_BOUT)
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

    h, w, esp = 6, 40, 20.0
    jj, ii = np.meshgrid(np.arange(w, dtype=float), np.arange(h, dtype=float))
    p = np.stack([jj * esp, ii * esp, np.full((h, w), 100.0)], axis=-1)
    n = np.zeros((h, w, 3))
    n[..., 2] = 1.0
    okg = np.ones((h, w), dtype=bool)
    okg[3, 35:] = False
    tour = m338.indexer(p, okg, n, np.ones((h, w), dtype=bool), esp)
    tout = np.arange(len(tour["i"]))
    b = au_bout(tour, tout)
    v("★★★★★ au bout : à trois colonnes au plus de la première ou de la dernière colonne posée de sa rangée",
      len(b["au_premier"]) == 4 * h and len(b["au_dernier"]) == 4 * h
      and set(tour["j"][b["au_dernier"]][tour["i"][b["au_dernier"]] == 3]) == {31, 32, 33, 34}, f"{len(b['au_premier'])} {len(b['au_dernier'])}")
    milieu = np.flatnonzero((tour["j"] >= 10) & (tour["j"] <= 25))
    v("★★★★ des sommets au milieu du tour ne sont pas au bout", not any(len(x) for x in au_bout(tour, milieu).values()))
    v("★★★★ toucher le bout demande au moins 10 sommets au bout",
      touche_le_bout({"au_premier": np.arange(6), "au_dernier": np.arange(4)})
      and not touche_le_bout({"au_premier": np.arange(6), "au_dernier": np.arange(3)}))
    dix, trois = {"au_premier": np.arange(10), "au_dernier": np.arange(0)}, {"au_premier": np.arange(3), "au_dernier": np.arange(0)}
    v("★★★★★ une surface à deux tours ne va jusqu'au bout que si elle touche le bout des deux",
      va_jusquau_bout({0: dix, -1: dix}) and not va_jusquau_bout({0: dix, -1: trois}) and not va_jusquau_bout({}))
    v("★★★ le bout touché est celui qui a le plus de sommets", le_bout_touche({"au_premier": np.arange(2), "au_dernier": np.arange(5)})
      == "le dernier")
    a = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    v("★★★ la continuité : la distance médiane au plus proche", la_continuite(a, a + np.array([0.0, 0.0, 5.0])) == 5.0
      and la_continuite(a, np.zeros((0, 3))) is None)

    s_ = lambda x: {"jusquau_bout": x}  # noqa: E731
    base = {"les_pannes": [], "redonne_335": True}
    vd = le_verdict(dict(base, les_surfaces_a_deux_tours=[s_(True), s_(True), s_(False)],
                         les_surfaces_a_un_tour=[s_(False), s_(False), s_(True)]))
    v("★★★★★ deux sur trois à deux tours, une sur trois à un tour : elles traversent la couture",
      vd["lissue"].endswith("les surfaces à deux tours traversent la couture"), vd["lissue"])
    vd = le_verdict(dict(base, les_surfaces_a_deux_tours=[s_(True), s_(True), s_(False)],
                         les_surfaces_a_un_tour=[s_(True), s_(True), s_(False)]))
    v("★★★★★ si les surfaces à un tour vont aussi jusqu'au bout, le bout ne les sépare pas",
      vd["lissue"].endswith("le bout ne les sépare pas des surfaces à un tour"))
    vd = le_verdict(dict(base, les_surfaces_a_deux_tours=[s_(False), s_(False), s_(True)], les_surfaces_a_un_tour=[s_(False)]))
    v("★★★★ une sur trois à deux tours : elles ne la traversent pas", vd["lissue"].endswith("elles ne la traversent pas"))
    v("★★★★ une chaîne qui ne redonne pas 335 est indécidable",
      not le_verdict(dict(base, redonne_335=False, les_surfaces_a_deux_tours=[s_(True)], les_surfaces_a_un_tour=[s_(False)]))["decidable"])

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
