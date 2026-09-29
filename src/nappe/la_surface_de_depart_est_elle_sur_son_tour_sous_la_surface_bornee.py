"""Là où les points de la surface bornée, graine 8, quatrième saut, posés sur 5753_-2 franchissent une feuille, la surface d'où part le saut est-elle posée sur 5753_-2 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL POINT DE LA SURFACE DE DÉPART NE SOIT RAPPORTÉ À UN TOUR PUBLIÉ SOUS UN SAUT. Ce qui était vu
avant d'écrire : tout ce que `296` à `347` publient, dont `R4-F529` (autour des graines 1 à 3, un tour publié est posé sur la feuille de
son voisin) et `R4-F533` (sous la surface bornée de la graine 8, quatrième saut, le tour de trop est `5753_-2`, celui d'où part le saut,
et 165 des 273 points posés dessus franchissent pourtant une feuille jusqu'à la surface de départ, que `340` dit retrouver `5753_-2` et
lui seul).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P144`. Un point posé sur le tour d'où part le saut devrait être sur la feuille de la surface
de départ. Si, là où le compte voit une feuille entre eux, la surface de départ n'est pas posée sur son tour, l'erreur du saut commence un
saut plus tôt, et c'est la surface de départ qu'il fallait refuser. Si elle y est posée, `5753_-2` y tient sur deux feuilles de `m7`, et
c'est le référent ou `m7` qui est en cause.

## Ce qui est fait

- **Les chaînes et le compte** : ceux de `347`, rejoués par sa mesure ; ils doivent redonner ce que `344` et `345` publient, sans quoi la
  tranche est indécidable.
- **Les pieds** : pour chaque point du compte, le point de la surface de départ que le compte prend pour elle, le plus proche, avec sa
  normale ; un pied sans normale n'est pas lu.
- **La pose d'un pied** : un pied est **lu** sur un tour publié si le sommet de ce tour le plus proche est en face de lui le long de sa
  normale, et **posé** sur ce tour s'il l'est à au plus un quart de pas nominal, par la comparaison de `321`.
- **La question** : sous la surface bornée, graine 8, côté moins, quatrième saut, parmi les points posés sur le tour de trop que le compte
  dit franchir exactement une feuille, les pieds lus sur `5753_-2`, le tour que retrouve la surface de départ ; la part d'entre eux qui
  y est posée.
- **Le contrôle** : sous la même surface, les points posés sur le tour attendu que le compte dit franchir exactement une feuille ; au
  moins la moitié de leurs pieds lus sur `5753_-2` doivent y être posés, sans quoi la mesure ne voit pas la surface de départ sur son
  tour et la tranche est indécidable.
- **La règle** : au moins 50 pieds lus de chaque côté, sinon indécidable. Si au moins les trois quarts des pieds de la question sont posés
  sur `5753_-2`, **oui, la surface de départ y est sur son tour** ; si au plus un quart, **non, elle n'y est pas** ; sinon, **en
  partie**.

## Les issues

L'issue de la tranche : **sous la surface bornée, p % des pieds lus des points qui franchissent une feuille depuis 5753_-2 sont posés sur
5753_-2**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les tours sur lesquels les pieds de la question sont posés ; l'écart le long de la normale entre ces points et leurs pieds ; et la même
lecture sous chaque autre surface à deux tours des quatre chaînes.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si l'erreur, quand la surface de départ n'est pas sur son tour, est dans cette surface ou dans le
tour publié ; et ce que vaut tout ceci sur PHerc0358.

Usage :
    uv run python src/nappe/la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.py --verifier
    uv run python src/nappe/la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.py \\
        --json docs/mesures/la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import jugee_strictement_jusquou_la_chaine_bornee_descend_elle as m340  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille as m347  # noqa: E402

LA_SURFACE = {"la_chaine": "bornée", "le_rang": 8, "le_cote": "moins", "le_saut": 4}
LA_PART_AU_MOINS = 0.75
LA_PART_AU_PLUS = 0.25
LA_PART_DU_CONTROLE = 0.5
LE_MINIMUM_DE_PIEDS = 50


def les_pieds(q: np.ndarray, depart: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pour chaque point, le point de la surface de départ le plus proche, celui que le compte prend pour elle, avec sa normale, et si
    cette normale est connue."""
    from scipy.spatial import cKDTree
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    v = depart["valide"]
    if not len(q) or not v.any():
        return np.zeros((len(q), 3)), np.zeros((len(q), 3)), np.zeros(len(q), dtype=bool)
    nn, nok = les_normales(depart["la_nappe"], v)
    pts, nrm, ok = depart["la_nappe"][v], nn[v], nok[v]
    _, idx = cKDTree(pts).query(q)
    return pts[idx], nrm[idx], ok[idx]


def les_poses_des_pieds(pieds: np.ndarray, normales: np.ndarray, ok: np.ndarray, tours: dict) -> tuple[list[list[int]], list[list[int]]]:
    """Pour chaque pied, les tours sur lesquels il est lu, et ceux sur lesquels il est posé ; rien pour un pied sans normale."""
    lus: list[list[int]] = [[] for _ in range(len(pieds))]
    poses: list[list[int]] = [[] for _ in range(len(pieds))]
    if not ok.any():
        return lus, poses
    ix = np.flatnonzero(ok)
    for t, tour in tours.items():
        u = m321.les_ecarts(pieds[ix], normales[ix], m329.les_sommets_proches(tour, pieds[ix])[0])
        for i, x in zip(ix, u):
            if np.isfinite(x):
                lus[i].append(t)
                if abs(x) <= m321.LE_QUART:
                    poses[i].append(t)
    return lus, poses


def le_groupe(sur: int, lus: list[list[int]], poses: list[list[int]], ecarts: list[float]) -> dict:
    """Des pieds d'un groupe de points : combien sont lus sur le tour `sur`, combien y sont posés, la part posée, et, rapportés à côté, les
    tours sur lesquels ils sont posés et l'écart médian, en pas, entre les points et leurs pieds."""
    lu = [i for i, w in enumerate(lus) if sur in w]
    pose = [i for i in lu if sur in poses[i]]
    ailleurs = Counter(str(t) for i, w in enumerate(poses) for t in w)
    e = [abs(x) for x in ecarts if np.isfinite(x)]
    return {"les_points": len(lus), "les_pieds_lus": len(lu), "les_pieds_poses": len(pose),
            "la_part_posee": round(len(pose) / len(lu), 4) if len(lu) >= LE_MINIMUM_DE_PIEDS else None,
            "les_tours_des_pieds": dict(sorted(ailleurs.items(), key=lambda kv: -int(kv[0]))),
            "sans_tour": sum(1 for w in poses if not w),
            "lecart_median_en_pas": round(statistics.median(e) / m321.LE_PAS_L2, 4) if e else None}


def la_lecture(avant: dict, en_plus: dict | None, sens: int) -> dict | None:
    """Sous une surface qui retrouve le tour attendu et d'autres, et dont la surface d'avant retrouve un seul tour, le tour de départ : les
    pieds des points posés sur un tour de trop qui franchissent une feuille, et ceux des points posés sur le tour attendu qui en franchissent
    une, lus sur le tour de départ."""
    r0 = m340.les_retrouves(avant)
    if len(r0) != 1 or en_plus is None or len(en_plus.get("les_retrouves", [])) < 2:
        return None
    depart, attendu = r0[0], r0[0] + sens
    if attendu not in en_plus["les_retrouves"]:
        return None
    de_trop = [t for t in en_plus["les_retrouves"] if t != attendu]
    pts = en_plus["les_pieds"]

    def groupe(garde):
        ix = [i for i, (c, w) in enumerate(zip(en_plus["les_comptes"], en_plus["les_poses"])) if c == 1 and garde(w)]
        return le_groupe(depart, [pts["lus"][i] for i in ix], [pts["poses"][i] for i in ix], [pts["ecarts"][i] for i in ix])
    return {"le_tour_de_depart": depart, "le_tour_attendu": attendu, "les_tours_de_trop": de_trop,
            "la_question": groupe(lambda w: any(t in w for t in de_trop)), "le_controle": groupe(lambda w: attendu in w)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_344") or not d.get("redonne_345"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 344 et 345"}
    s = next((x for x in d["les_surfaces"] if all(x[k] == v for k, v in LA_SURFACE.items())), None)
    if s is None or s["la_surface"] is None:
        return {"decidable": False, "lissue": "indécidable : la surface bornée n'est pas lue"}
    q, c = s["la_surface"]["la_question"], s["la_surface"]["le_controle"]
    if c["la_part_posee"] is None or c["la_part_posee"] < LA_PART_DU_CONTROLE:
        return {"decidable": False, "lissue": "indécidable : la mesure ne voit pas la surface de départ sur son tour"}
    if q["la_part_posee"] is None:
        return {"decidable": False, "lissue": f"indécidable : {q['les_pieds_lus']} pieds lus"}
    p = q["la_part_posee"]
    tete = (f"sous la surface bornée, {round(100 * p)} % des pieds lus des points qui franchissent une feuille depuis 5753_"
            f"{s['la_surface']['le_tour_de_depart']} sont posés sur 5753_{s['la_surface']['le_tour_de_depart']}")
    suite = ("oui, la surface de départ y est sur son tour" if p >= LA_PART_AU_MOINS
             else "non, elle n'y est pas" if p <= LA_PART_AU_PLUS else "en partie")
    return {"decidable": True, "la_part": p, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}

    def garder(dep, arr, lv):
        r = m345.les_comptes_point_par_point(dep, arr, lv, m321.LE_PAS_L2)
        out = {"les_feuilles": m345.le_resume(r)}
        if arr is None or not arr["valide"].any():
            return out
        lect = m329.les_lectures(arr["la_nappe"][arr["valide"]] * m321.LE_FACTEUR, tours)
        out["les_retrouves"] = sorted((t for t, x in lect.items() if x["la_lecture"] == "retrouve"), reverse=True)
        if len(out["les_retrouves"]) >= 2 and r is not None:
            out["les_comptes"] = r["les_comptes"]
            out["les_poses"] = m347.les_poses(r["les_points"] * m321.LE_FACTEUR, r["les_normales"],
                                              {t: tours[t] for t in out["les_retrouves"]})
            pieds, npieds, ok = les_pieds(r["les_points"], dep)
            lus, poses = les_poses_des_pieds(pieds * m321.LE_FACTEUR, npieds, ok, tours)
            out["les_pieds"] = {"lus": lus, "poses": poses, "ecarts": [float(x) for x in r["les_ecarts"]]}
        return out

    d344 = m344.mesurer(en_plus=garder)
    publie344 = json.loads(m345.CE_QUE_344_A_PUBLIE.read_text())
    surfaces, redonne345, saccordent = m347.les_surfaces_rejouees(d344, la_lecture)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_surface": LA_SURFACE, "la_part_au_moins": LA_PART_AU_MOINS, "la_part_au_plus": LA_PART_AU_PLUS,
                            "la_part_du_controle": LA_PART_DU_CONTROLE, "le_minimum_de_pieds": LE_MINIMUM_DE_PIEDS,
                            "le_quart_voxels": round(m321.LE_QUART, 3)},
         "les_pannes": d344["les_pannes"], "la_lecture_de_m7": d344["la_lecture_de_m7"],
         "redonne_344": bool(json.loads(json.dumps(m345.sans_le_compte(d344["les_chaines"]))) == publie344["les_chaines"]
                             and d344["le_verdict"] == publie344["le_verdict"] and d344["redonne_328"]),
         "redonne_345": redonne345, "les_lectures_saccordent": saccordent, "les_surfaces": surfaces}
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

    def tour(z, x0=0.0, x1=200.0):
        xs, ys = np.meshgrid(np.arange(x0, x1, 10.0), np.arange(0.0, 200.0, 10.0))
        p = np.stack([xs.ravel(), ys.ravel(), np.full(xs.size, float(z))], axis=1)
        return {"points": p, "normales": np.tile([0.0, 0.0, 1.0], (len(p), 1))}

    def nappe(z, dz=None):
        g = np.zeros((11, 11, 3))
        for a in range(11):
            for b in range(11):
                g[a, b] = (10.0 * b, 10.0 * a, z if dz is None or b < 6 else dz)
        return {"la_nappe": g, "valide": np.ones((11, 11), dtype=bool)}

    q = nappe(30.0)["la_nappe"].reshape(-1, 3)
    pieds, npieds, ok = les_pieds(q, nappe(10.0))
    v("★★★★ le pied d'un point est le point de départ le plus proche, avec sa normale",
      np.allclose(pieds[:, :2], q[:, :2]) and np.allclose(pieds[:, 2], 10.0) and ok[60] and abs(abs(npieds[60, 2]) - 1.0) < 1e-6,
      str(pieds[:2]))
    marche = nappe(10.0, 40.0)
    pieds, npieds, ok = les_pieds(q, marche)
    lus, poses = les_poses_des_pieds(pieds, npieds, ok, {-2: tour(10.0), -1: tour(40.0)})
    gauche = [i for i in range(len(q)) if q[i, 0] < 45.0 and ok[i]]
    droite = [i for i in range(len(q)) if q[i, 0] > 65.0 and ok[i]]
    v("★★★★ une surface de départ à cheval : chaque pied est posé sur le tour qu'il touche, et lu sur l'autre",
      gauche and droite and all(poses[i] == [-2] and lus[i] == [-2, -1] for i in gauche)
      and all(poses[i] == [-1] and lus[i] == [-2, -1] for i in droite), str([(lus[i], poses[i]) for i in gauche[:1] + droite[:1]]))
    lus, poses = les_poses_des_pieds(pieds, npieds, np.zeros(len(pieds), dtype=bool), {-2: tour(10.0)})
    v("★★★ un pied sans normale n'est pas lu", all(w == [] for w in lus) and all(w == [] for w in poses))
    p = les_poses_des_pieds(np.array([[50.0, 50.0, 10.0 + m321.LE_QUART + 1.0]]), np.array([[0.0, 0.0, 1.0]]), np.array([True]),
                            {-2: tour(10.0)})
    v("★★★ un pied à un peu plus d'un quart de pas du tour : lu, pas posé", p == ([[-2]], [[]]), str(p))
    p = les_poses_des_pieds(np.array([[50.0, 50.0, 10.0]]), np.array([[0.0, 0.0, 1.0]]), np.array([True]),
                            {-2: tour(10.0, 300.0, 400.0), -1: tour(10.0)})
    v("★★★★ un tour qui n'est pas en face du pied n'y est pas lu", p == ([[-1]], [[-1]]), str(p))

    g = le_groupe(-2, [[-2, -1]] * 60 + [[-1]] * 10, [[-2]] * 45 + [[-1]] * 15 + [[-1]] * 10, [18.02] * 70)
    v("★★★★ la part posée est prise sur les pieds lus sur le tour de départ, pas sur tous",
      g["les_pieds_lus"] == 60 and g["les_pieds_poses"] == 45 and g["la_part_posee"] == 0.75
      and g["les_tours_des_pieds"] == {"-1": 25, "-2": 45} and g["lecart_median_en_pas"] == 1.0, str(g))
    v("★★★ sous 50 pieds lus : pas de part", le_groupe(-2, [[-2]] * 49, [[-2]] * 49, [1.0] * 49)["la_part_posee"] is None)

    R, N = "retrouve", "ne retrouve pas"
    en_plus = {"les_retrouves": [-2, -3], "les_comptes": [1] * 60 + [0] * 5 + [1] * 60,
               "les_poses": [[-2]] * 65 + [[-3]] * 60,
               "les_pieds": {"lus": [[-2]] * 125, "poses": [[-1]] * 60 + [[-2]] * 65, "ecarts": [18.0] * 125}}
    s = la_lecture({"-2": R, "-1": N}, en_plus, -1)
    v("★★★★ la question : les points du tour de trop qui franchissent une feuille ; le contrôle : ceux du tour attendu",
      s is not None and s["le_tour_de_depart"] == -2 and s["le_tour_attendu"] == -3
      and s["la_question"]["les_points"] == 60 and s["la_question"]["la_part_posee"] == 0.0
      and s["le_controle"]["les_points"] == 60 and s["le_controle"]["la_part_posee"] == 1.0, str(s))
    s = la_lecture({"-3": R}, en_plus, 1)
    v("★★★ côté plus, le tour attendu est w + 1, et les pieds sont lus sur w", s is not None and s["le_tour_de_depart"] == -3
      and s["le_tour_attendu"] == -2 and s["la_question"]["les_points"] == 60, str(s))
    v("★★★ une surface d'avant à deux tours, ou sans le tour attendu : rien à lire",
      la_lecture({"-1": R, "-2": R}, en_plus, -1) is None and la_lecture({"-5": R}, en_plus, -1) is None)

    def d_(pq, pc, **kw):
        g_ = lambda p: {"la_part_posee": p, "les_pieds_lus": 60}  # noqa: E731
        return dict({"les_pannes": [], "redonne_344": True, "redonne_345": True, "les_surfaces": [
            {**LA_SURFACE, "le_saut": 5, "la_surface": {"le_tour_de_depart": -3, "la_question": g_(0.0), "le_controle": g_(0.9)}},
            {**LA_SURFACE, "le_rang": 7, "la_surface": {"le_tour_de_depart": -3, "la_question": g_(0.0), "le_controle": g_(0.9)}},
            {**LA_SURFACE, "la_surface": {"le_tour_de_depart": -2, "la_question": g_(pq), "le_controle": g_(pc)}}]}, **kw)
    v("★★★★ les trois quarts posés : oui", le_verdict(d_(0.75, 0.9)).get("lissue", "").endswith("oui, la surface de départ y est sur son tour")
      and "5753_-2" in le_verdict(d_(0.75, 0.9))["lissue"])
    v("★★★★ un quart : non", le_verdict(d_(0.25, 0.9)).get("lissue", "").endswith("non, elle n'y est pas"))
    v("★★★ entre les deux : en partie", le_verdict(d_(0.5, 0.9)).get("lissue", "").endswith("en partie"))
    v("★★★★ seule la surface bornée, graine 8, quatrième saut, décide", le_verdict(d_(0.9, 0.9)).get("la_part") == 0.9)
    v("★★★★ le contrôle sous la moitié : indécidable", not le_verdict(d_(0.9, 0.49))["decidable"]
      and le_verdict(d_(0.9, 0.5))["decidable"])
    v("★★★ trop peu de pieds lus : indécidable", not le_verdict(d_(None, 0.9))["decidable"]
      and not le_verdict(d_(0.9, None))["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 344 ou 345 : indécidable", not le_verdict(d_(0.9, 0.9, redonne_345=False))["decidable"]
      and not le_verdict(d_(0.9, 0.9, redonne_344=False))["decidable"])

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
