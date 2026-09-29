"""Les surfaces à deux tours que le compte des feuilles de 345 tient sur les graines 4 à 8 sont-elles posées là où leurs deux tours publiés se recouvrent, comme autour des graines 1 à 3 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL RECOUVREMENT NE SOIT LU SOUS UNE SURFACE D'UNE CHAÎNE. Ce qui était vu avant d'écrire : tout ce
que `296` à `345` publient, dont `R4-F527` (autour des graines 4 à 6, les tours voisins se recouvrent sur 2 à 15 % de leurs sommets, autour
des graines 7 et 8 sur 0 à 5 %), `R4-F529` (autour des graines 1 à 3, un tour publié est posé sur la feuille de son voisin) et `R4-F531`
(le compte tient trois des quatre sauts à deux tours des graines 4 à 8, et les 19 des graines 1 à 3). Les lectures publiées disent que
deux de ces trois surfaces retrouvent `5753_-2` et `5753_-6`, deux tours qui ne sont pas voisins, et la troisième `5753_-2` et `5753_-3`.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P142`. Une surface qui passe à la feuille suivante et retrouve deux tours publiés est soit
posée là où ces deux tours sont sur la même feuille, et c'est le référent qui la dit fausse à tort, soit à cheval sur deux feuilles, et
c'est elle qui a tort. Si les trois sauts que le compte tient sont du premier genre, le compte ne manque que des sauts faux par le
référent, et il vaut pour `#5`.

## Ce qui est fait

- **Les chaînes** : celles de `344`, rejouées par sa mesure ; elles doivent redonner ce que `344` publie, sans quoi la tranche est
  indécidable. Chaque surface qui retrouve au moins deux tours est gardée le temps d'une lecture.
- **Les surfaces** : celles des sauts que `344` dit faux parce qu'ils retrouvent deux tours ; leur tour attendu est le voisin, du côté du
  saut, du seul tour que retrouve la surface d'avant, et leur tour de trop l'autre.
- **Le recouvrement sous la surface** : parmi les sommets du tour de trop qui ont la surface en face à au plus un quart de pas nominal,
  ceux par qui la surface le retrouve, la part qui a le tour attendu en face à au plus un quart de pas, par la comparaison de `321`. Une
  surface est **posée où ses deux tours se recouvrent** si cette part est d'au moins la moitié, **à cheval sur deux feuilles** sinon ;
  non lue si moins de 50 de ces sommets ont le tour attendu en face. Avec plus d'un tour de trop, la plus petite part décide.
- **Le contrôle** : la mesure doit dire recouvrement sous au moins la moitié des surfaces à deux tours des graines 1 à 3, où `343` a
  établi qu'un tour publié est posé sur la feuille de son voisin, sans quoi la tranche est indécidable.
- **La règle** : sur les trois surfaces à deux tours que `345` tient aux graines 4 à 8, si les trois sont posées où leurs tours se
  recouvrent, **c'est le référent** ; si aucune, **c'est la surface** ; sinon, **l'un et l'autre**. Indécidable si l'une n'est pas lue.

## Rapporté à côté, qui ne décide rien

La part dans l'autre sens, celle des sommets du tour attendu qui ont le tour de trop en face ; les deux surfaces à deux tours que `345`
refuse aux graines 4 à 8 ; et chaque surface des graines 1 à 3.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : lequel des deux tours publiés est à la mauvaise place là où ils se recouvrent.

Usage :
    uv run python src/nappe/les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.py --verifier
    uv run python src/nappe/les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.py \\
        --json docs/mesures/les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.json
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
import jugee_strictement_jusquou_la_chaine_bornee_descend_elle as m340  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_345_A_PUBLIE = LES_MESURES / "les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.json"
LA_PART_COMMUNE = 0.5


def la_part_sur_lautre(tx: dict, ty: dict, pts: np.ndarray) -> dict:
    """Parmi les sommets de `tx` qui ont la surface `pts` en face à au plus un quart de pas, la part qui a `ty` en face à au plus un
    quart de pas."""
    ref, ref_n = m329.les_sommets_proches(tx, pts)
    t = m321.les_ecarts(ref, ref_n, pts)
    pose = np.isfinite(t) & (np.abs(t) <= m321.LE_QUART)
    c, cn = ref[pose], ref_n[pose]
    yp = m329.les_sommets_proches(ty, c)[0] if len(c) else np.zeros((0, 3))
    u = m321.les_ecarts(c, cn, yp)
    en_face = np.isfinite(u)
    k = int((np.abs(u[en_face]) <= m321.LE_QUART).sum())
    n = int(en_face.sum())
    return {"les_sommets_poses": int(pose.sum()), "en_face_de_lautre": n, "a_un_quart": k,
            "la_part": round(k / n, 4) if n >= m321.LE_MINIMUM else None}


def les_parts(pts: np.ndarray, tours: dict) -> dict:
    """Ce que les tours publiés disent de la surface : ceux qu'elle retrouve et, s'il y en a au moins deux, chaque part sur l'autre."""
    lect = m329.les_lectures(pts, tours)
    r = sorted((t for t, x in lect.items() if x["la_lecture"] == "retrouve"), reverse=True)
    out = {"les_retrouves": r}
    if len(r) >= 2:
        out["les_parts"] = {f"{x}|{y}": la_part_sur_lautre(tours[x], tours[y], pts) for x in r for y in r if x != y}
    return out


def la_surface(avant: dict, parts: dict | None, sens: int) -> dict | None:
    """Pour une surface qui retrouve le tour attendu et d'autres : le tour attendu, les tours de trop, la plus petite part de ceux-ci sur
    le tour attendu, et ce qu'elle dit ; None si la surface d'avant ne retrouve pas un seul tour."""
    r0 = m340.les_retrouves(avant)
    if len(r0) != 1 or parts is None or len(parts["les_retrouves"]) < 2:
        return None
    attendu = r0[0] + sens
    if attendu not in parts["les_retrouves"]:
        return None
    de_trop = [t for t in parts["les_retrouves"] if t != attendu]
    p = [parts["les_parts"][f"{t}|{attendu}"]["la_part"] for t in de_trop]
    q = [parts["les_parts"][f"{attendu}|{t}"]["la_part"] for t in de_trop]
    part = None if any(x is None for x in p) else min(p)
    lecture = "non lue" if part is None else ("posée où ses tours se recouvrent" if part >= LA_PART_COMMUNE else "à cheval sur deux feuilles")
    return {"le_tour_attendu": attendu, "les_tours_de_trop": de_trop, "la_part": part,
            "la_part_dans_lautre_sens": None if any(x is None for x in q) else min(q), "la_lecture": lecture}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_344"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 344"}
    ctl = [s["la_surface"]["la_lecture"] for s in d["les_surfaces"] if s["le_rang"] < 4]
    lus = [x for x in ctl if x != "non lue"]
    if not lus or 2 * sum(x == "posée où ses tours se recouvrent" for x in lus) < len(lus):
        return {"decidable": False, "lissue": "indécidable : la mesure ne voit pas le recouvrement autour des graines 1 à 3"}
    tenues = [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["tient_par_345"]]
    if not tenues or any(s["la_surface"]["la_lecture"] == "non lue" for s in tenues):
        return {"decidable": False, "lissue": "indécidable : une surface tenue par 345 n'est pas lue"}
    k = sum(s["la_surface"]["la_lecture"] == "posée où ses tours se recouvrent" for s in tenues)
    tete = (f"sur les graines 4 à 8, {k} des {len(tenues)} surfaces à deux tours que le compte tient sont posées où leurs tours publiés "
            f"se recouvrent, contre {sum(x == 'posée où ses tours se recouvrent' for x in lus)} des {len(lus)} autour des graines 1 à 3")
    suite = "c'est le référent" if k == len(tenues) else ("c'est la surface" if k == 0 else "l'un et l'autre")
    return {"decidable": True, "k": k, "n": len(tenues), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}

    def garder(dep, arr, lv):
        if arr is None or not arr["valide"].any():
            return None
        return les_parts(arr["la_nappe"][arr["valide"]] * m321.LE_FACTEUR, tours)

    d344 = m344.mesurer(en_plus=garder)
    publie344 = json.loads(m345.CE_QUE_344_A_PUBLIE.read_text())
    publie345 = json.loads(CE_QUE_345_A_PUBLIE.read_text())
    publiees = {n: json.loads((LES_MESURES / f).read_text()) for n, f in m340.LES_CHAINES.items()}
    nappes = {g["le_rang"]: {t: x["la_lecture"] for t, x in g["la_nappe"].items()} for g in publiees["sans relance"]["les_graines"]}
    surfaces, saccordent = [], True
    for n, ch in d344["les_chaines"].items():
        for g in ch["les_graines"]:
            for cote, x in g["les_cotes"].items():
                lect = m340.les_surfaces(n, publiees[n], nappes, g["le_rang"], cote)
                t345 = next(y for y in publie345["les_chaines"][n]["les_graines"] if y["le_rang"] == g["le_rang"])
                for s in x["les_sauts"]:
                    if s["en_plus"] is not None:
                        saccordent &= s["en_plus"]["les_retrouves"] == m340.les_retrouves(lect[s["le_saut"]])
                    if s["la_justesse"] != "faux : deux tours":
                        continue
                    s345 = t345["les_cotes"][cote]["les_sauts"][s["le_saut"] - 1]
                    surfaces.append({"la_chaine": n, "le_rang": g["le_rang"], "le_cote": cote, "le_saut": s["le_saut"],
                                     "tient_par_345": s345["tient"],
                                     "la_surface": la_surface(lect[s["le_saut"] - 1], s["en_plus"], m344.LE_SENS[cote]),
                                     "les_parts": s["en_plus"]["les_parts"]})
                    print(json.dumps({k: v for k, v in surfaces[-1].items() if k != "les_parts"}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_part_commune": LA_PART_COMMUNE,
                                                                    "le_quart_voxels": round(m321.LE_QUART, 3)},
         "les_pannes": d344["les_pannes"], "la_lecture_de_m7": d344["la_lecture_de_m7"],
         "redonne_344": bool(json.loads(json.dumps(m345.sans_le_compte(d344["les_chaines"]))) == publie344["les_chaines"]
                             and d344["le_verdict"] == publie344["le_verdict"] and d344["redonne_328"] and saccordent),
         "les_lectures_saccordent": bool(saccordent), "les_surfaces": surfaces}
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

    def tour(z, x0=0.0, x1=200.0, y0=0.0, y1=200.0):
        xs, ys = np.meshgrid(np.arange(x0, x1, 10.0), np.arange(y0, y1, 10.0))
        p = np.stack([xs.ravel(), ys.ravel(), np.full(xs.size, float(z))], axis=1)
        return {"points": p, "normales": np.tile([0.0, 0.0, 1.0], (len(p), 1))}

    def nuage(zs):
        return np.concatenate([tour(z, a, b)["points"] for z, a, b in zs])

    surf = nuage([(100.0, 0.0, 200.0)])
    p = la_part_sur_lautre(tour(100.0), tour(105.0), surf)
    v("★★★★ deux tours sur la même feuille, sous la surface : tous les sommets posés ont l'autre à un quart de pas",
      p["la_part"] == 1.0 and p["les_sommets_poses"] == 400, str(p))
    p = la_part_sur_lautre(tour(100.0), tour(160.0), surf)
    v("★★★★ l'autre tour à 60 voxels : aucun", p["la_part"] == 0.0, str(p))
    cheval = nuage([(100.0, 0.0, 100.0), (170.0, 100.0, 200.0)])
    p = la_part_sur_lautre(tour(170.0), tour(100.0), cheval)
    v("★★★★ une surface à cheval sur deux feuilles : là où elle est sur le tour de trop, le tour attendu n'y est pas",
      p["la_part"] == 0.0 and p["les_sommets_poses"] >= 200, str(p))
    p = la_part_sur_lautre(tour(100.0), tour(105.0, y0=230.0, y1=400.0), surf)
    v("★★★ trop peu de sommets en face de l'autre : non lue", p["la_part"] is None and p["en_face_de_lautre"] < 50, str(p))
    R, N = "retrouve", "ne retrouve pas"
    parts = {"les_retrouves": [-2, -3], "les_parts": {"-2|-3": {"la_part": 0.8}, "-3|-2": {"la_part": 0.3}}}
    s = la_surface({"-2": R, "-1": N}, parts, -1)
    v("★★★★ le tour attendu est le voisin de celui d'avant ; la part est celle du tour de trop sur lui",
      s["le_tour_attendu"] == -3 and s["les_tours_de_trop"] == [-2] and s["la_part"] == 0.8
      and s["la_part_dans_lautre_sens"] == 0.3 and s["la_lecture"] == "posée où ses tours se recouvrent", str(s))
    s = la_surface({"-2": R}, {"les_retrouves": [-2, -3], "les_parts": {"-2|-3": {"la_part": 0.49}, "-3|-2": {"la_part": 0.9}}}, -1)
    v("★★★ sous la moitié : à cheval", s["la_lecture"] == "à cheval sur deux feuilles")
    s = la_surface({"-2": R}, {"les_retrouves": [-2, -3], "les_parts": {"-2|-3": {"la_part": 0.5}, "-3|-2": {"la_part": 0.9}}}, -1)
    v("★★★ la moitié juste : posée où ses tours se recouvrent", s["la_lecture"] == "posée où ses tours se recouvrent")
    s = la_surface({"-3": R}, parts, 1)
    v("★★★★ côté plus, le tour attendu est w + 1, et le tour de trop celui d'avant",
      s is not None and s["le_tour_attendu"] == -2 and s["les_tours_de_trop"] == [-3] and s["la_part"] == 0.3, str(s))
    tx = {"points": np.concatenate([tour(130.0, 0.0, 100.0)["points"], tour(100.0, 100.0, 200.0)["points"]]),
          "normales": np.tile([0.0, 0.0, 1.0], (400, 1))}
    p = la_part_sur_lautre(tx, tour(125.0, 0.0, 100.0), surf)
    v("★★★★ seuls les sommets du tour de trop posés sur la surface comptent, pas ceux qui l'ont seulement en face",
      p["les_sommets_poses"] == 200 and p["la_part"] == 0.0, str(p))
    tri = {"les_retrouves": [0, -4, -5], "les_parts": {f"{a}|{b}": {"la_part": 0.9 if a == 0 else 0.2}
                                                       for a in (0, -4, -5) for b in (0, -4, -5) if a != b}}
    s = la_surface({"-4": R}, tri, -1)
    v("★★★ plusieurs tours de trop : la plus petite part décide", s["les_tours_de_trop"] == [0, -4] and s["la_part"] == 0.2
      and s["la_lecture"] == "à cheval sur deux feuilles", str(s))
    v("★★★ une surface d'avant à deux tours : pas de surface à lire",
      la_surface({"-1": R, "-2": R}, parts, -1) is None and la_surface({"-2": R}, {"les_retrouves": [-2]}, -1) is None)

    def s_(rang, tient_, lecture):
        return {"le_rang": rang, "tient_par_345": tient_, "la_surface": {"la_lecture": lecture}}
    P, C, NL = "posée où ses tours se recouvrent", "à cheval sur deux feuilles", "non lue"
    ctl = [s_(2, True, P)] * 3 + [s_(1, True, C)]
    base = lambda ss: {"les_pannes": [], "redonne_344": True, "les_surfaces": ctl + ss}  # noqa: E731
    v("★★★★ les trois tenues posées où leurs tours se recouvrent : le référent",
      le_verdict(base([s_(5, True, P)] * 3)).get("lissue", "").endswith("c'est le référent"))
    v("★★★★ aucune : la surface", le_verdict(base([s_(5, True, C)] * 3)).get("lissue", "").endswith("c'est la surface"))
    v("★★★★ deux sur trois : l'un et l'autre", le_verdict(base([s_(5, True, P)] * 2 + [s_(8, True, C)])).get("lissue", "")
      .endswith("l'un et l'autre"))
    v("★★★★ les surfaces refusées par 345 ne comptent pas",
      le_verdict(base([s_(5, True, P)] * 3 + [s_(7, False, C)])).get("lissue", "").endswith("c'est le référent"))
    v("★★★★ une tenue non lue : indécidable", not le_verdict(base([s_(5, True, P)] * 2 + [s_(8, True, NL)]))["decidable"])
    v("★★★★ le contrôle : si la mesure ne voit pas le recouvrement autour des graines 1 à 3, indécidable",
      not le_verdict({"les_pannes": [], "redonne_344": True, "les_surfaces": [s_(2, True, C)] * 3 + [s_(5, True, P)] * 3})["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 344 : indécidable",
      not le_verdict(dict(base([s_(5, True, P)] * 3), redonne_344=False))["decidable"])

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
