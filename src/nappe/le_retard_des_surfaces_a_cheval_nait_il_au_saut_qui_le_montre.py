"""Sous les surfaces justes à cheval des graines 4 à 8, les points restés sur le tour de départ sont-ils au-dessus d'une surface de départ déjà restée en arrière, ou le retard naît-il à ce saut ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PIED D'UN POINT RESTÉ NE SOIT RAPPORTÉ À UN TOUR PUBLIÉ, HORS DE LA SURFACE DE `348`. Ce qui
était vu avant d'écrire : tout ce que `296` à `349` publient, dont `R4-F534` (sous la surface bornée de la graine 8, quatrième saut, les
points posés sur le tour de départ ont leur pied sur le tour d'avant : 152 sur 152) et `R4-F535` (60 des 104 sauts justes des graines 4 à
8 donnent une surface à cheval, tous dans les chaînes relancées ; des 8963 points restés, 4306 franchissent une feuille pour le compte de
`345`, 2275 aucune).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P146`. Un point resté dont le pied est sur le tour de départ n'a pas quitté la feuille de la
surface de départ : le retard naît à ce saut. Un point resté dont le pied est sur le tour d'avant est au-dessus d'une surface de départ
déjà en arrière : le retard vient de plus haut, et il se propage de saut en saut. Dans le second cas, un critère sans référent doit juger
une surface au moment où la chaîne la relance, et non saut par saut.

## Ce qui est fait

- **Les chaînes et le compte** : ceux de `349`, rejoués par la mesure de `347` ; ils doivent redonner ce que `344` et `345` publient, sans
  quoi la tranche est indécidable.
- **Les surfaces** : celles que `349` dit à cheval par des points restés, parmi les sauts justes des graines 4 à 8 (au moins 50 points
  posés sur le tour de départ et pas sur le tour attendu).
- **Les pieds** : pour chaque point resté, le point de la surface de départ que le compte prend pour elle, par `348`, et les tours publiés
  sur lesquels il est posé, à au plus un quart de pas.
- **La lecture sous une surface** : parmi les pieds des points restés posés sur le tour de départ ou sur le tour d'avant (le voisin du tour
  de départ du côté opposé au saut), la part posée sur le tour d'avant et pas sur le tour de départ. Au moins les trois quarts, le retard
  est **hérité** ; au plus un quart, il est **né ici** ; sinon, **mêlé**. Non lue sous 50 tels pieds.
- **Le contrôle** : sous chaque surface lue, les pieds des points posés sur le tour attendu ; sous au moins les trois quarts des surfaces
  lues, au moins la moitié de ces pieds doivent être posés sur le tour de départ, sans quoi la mesure ne voit pas la surface de départ sur
  son tour et la tranche est indécidable.
- **La règle** : indécidable si moins de la moitié des surfaces sont lues. Si au moins les trois quarts des surfaces lues sont héritées,
  **le retard vient de plus haut** ; si au moins les trois quarts sont nées ici, **il naît au saut qui le montre** ; sinon, **l'un et
  l'autre**.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, le retard est hérité sous h des n surfaces à cheval lues, et né ici sous i**, puis ce que
dit la règle.

## Rapporté à côté, qui ne décide rien

Pour chaque chaîne et chaque graine, le premier saut juste qui donne une surface à cheval ; les mêmes lectures sous les surfaces à cheval
des graines 1 à 3.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où, avant la surface de départ, le retard est né quand il est hérité ; et ce que vaut tout ceci sur
PHerc0358.

Usage :
    uv run python src/nappe/le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.py --verifier
    uv run python src/nappe/le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.py \\
        --json docs/mesures/le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

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
import la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee as m348  # noqa: E402

LE_MINIMUM = 50
LA_PART_HERITEE = 0.75
LA_PART_NEE_ICI = 0.25
LA_PART_DU_CONTROLE = 0.5
LA_PART_DES_SURFACES = 0.75
HERITE, NE_ICI, MELE, NON_LU = "hérité", "né ici", "mêlé", "non lu"


def la_lecture(avant: dict, en_plus: dict | None, sens: int) -> dict | None:
    """Sous la surface d'un saut dont la surface d'avant retrouve un seul tour : les points restés, leurs pieds sur le tour de départ et sur
    le tour d'avant, ce que dit la part héritée ; et, pour le contrôle, les pieds des points posés sur le tour attendu."""
    r0 = m340.les_retrouves(avant)
    if len(r0) != 1 or en_plus is None or "les_pieds" not in en_plus:
        return None
    w0 = r0[0]
    wa, wv = w0 + sens, w0 - sens
    poses, pieds = en_plus["les_poses"], en_plus["les_pieds"]["poses"]
    restes = [i for i, w in enumerate(poses) if w0 in w and wa not in w]
    sur_depart = sum(1 for i in restes if w0 in pieds[i])
    sur_avant = sum(1 for i in restes if wv in pieds[i] and w0 not in pieds[i])
    lus = sur_depart + sur_avant
    part = round(sur_avant / lus, 4) if lus >= LE_MINIMUM else None
    lecture = NON_LU if part is None else HERITE if part >= LA_PART_HERITEE else NE_ICI if part <= LA_PART_NEE_ICI else MELE
    ctl = [i for i, w in enumerate(poses) if wa in w]
    ctl_lus = sum(1 for i in ctl if pieds[i])
    ctl_sur = sum(1 for i in ctl if w0 in pieds[i])
    return {"le_tour_de_depart": w0, "le_tour_attendu": wa, "le_tour_davant": wv, "les_restes": len(restes),
            "pieds_sur_le_tour_de_depart": sur_depart, "pieds_sur_le_tour_davant": sur_avant, "la_part_heritee": part,
            "la_lecture": lecture, "le_controle": {"les_points": len(ctl), "pieds_poses": ctl_lus, "sur_le_tour_de_depart": ctl_sur,
                                                     "la_part": round(ctl_sur / ctl_lus, 4) if ctl_lus >= LE_MINIMUM else None}}


def a_cheval_par_les_restes(a: dict | None) -> bool:
    return a is not None and a["les_restes"] >= LE_MINIMUM


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_344") or not d.get("redonne_345"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 344 et 345"}
    cheval = [s["la_surface"] for s in d["les_surfaces"]
              if s["le_rang"] >= 4 and s["la_justesse"] == "juste" and a_cheval_par_les_restes(s["la_surface"])]
    lues = [a for a in cheval if a["la_lecture"] != NON_LU]
    if not cheval or 2 * len(lues) < len(cheval):
        return {"decidable": False, "lissue": f"indécidable : {len(lues)} des {len(cheval)} surfaces à cheval sont lues"}
    bien = sum(1 for a in lues if a["le_controle"]["la_part"] is not None and a["le_controle"]["la_part"] >= LA_PART_DU_CONTROLE)
    if bien < LA_PART_DES_SURFACES * len(lues):
        return {"decidable": False, "lissue": "indécidable : la mesure ne voit pas la surface de départ sur son tour"}
    h = sum(1 for a in lues if a["la_lecture"] == HERITE)
    i = sum(1 for a in lues if a["la_lecture"] == NE_ICI)
    tete = f"sur les graines 4 à 8, le retard est hérité sous {h} des {len(lues)} surfaces à cheval lues, et né ici sous {i}"
    suite = ("le retard vient de plus haut" if h >= LA_PART_DES_SURFACES * len(lues)
             else "il naît au saut qui le montre" if i >= LA_PART_DES_SURFACES * len(lues) else "l'un et l'autre")
    return {"decidable": True, "h": h, "i": i, "n": len(lues), "N": len(cheval), "lissue": f"{tete} ; {suite}"}


def les_premiers(surfaces: list[dict]) -> list[dict]:
    """Rapporté à côté : pour chaque chaîne, graine et côté, le premier saut juste qui donne une surface à cheval par des points restés."""
    vus: dict = {}
    for s in surfaces:
        if s["la_justesse"] == "juste" and a_cheval_par_les_restes(s["la_surface"]):
            k = (s["la_chaine"], s["le_rang"], s["le_cote"])
            vus[k] = min(vus.get(k, s["le_saut"]), s["le_saut"])
    return [{"la_chaine": c, "le_rang": r, "le_cote": co, "le_premier_saut": x} for (c, r, co), x in sorted(vus.items())]


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
        if r is not None:
            out["les_poses"] = m347.les_poses(r["les_points"] * m321.LE_FACTEUR, r["les_normales"], tours)
            pieds, npieds, ok = m348.les_pieds(r["les_points"], dep)
            lus, poses = m348.les_poses_des_pieds(pieds * m321.LE_FACTEUR, npieds, ok, tours)
            out["les_pieds"] = {"poses": poses}
        return out

    d344 = m344.mesurer(en_plus=garder)
    publie344 = json.loads(m345.CE_QUE_344_A_PUBLIE.read_text())
    surfaces, redonne345, saccordent = m347.les_surfaces_rejouees(d344, la_lecture, quels=("juste",))
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_minimum": LE_MINIMUM, "la_part_heritee": LA_PART_HERITEE, "la_part_nee_ici": LA_PART_NEE_ICI,
                            "la_part_du_controle": LA_PART_DU_CONTROLE, "la_part_des_surfaces": LA_PART_DES_SURFACES,
                            "le_quart_voxels": round(m321.LE_QUART, 3)},
         "les_pannes": d344["les_pannes"], "la_lecture_de_m7": d344["la_lecture_de_m7"],
         "redonne_344": bool(json.loads(json.dumps(m345.sans_le_compte(d344["les_chaines"]))) == publie344["les_chaines"]
                             and d344["le_verdict"] == publie344["le_verdict"] and d344["redonne_328"]),
         "redonne_345": redonne345, "les_lectures_saccordent": saccordent, "les_surfaces": surfaces,
         "les_premiers": les_premiers(surfaces)}
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

    R, N = "retrouve", "ne retrouve pas"
    en_plus = {"les_poses": [[-3]] * 100 + [[-2]] * 80 + [[-2, -3]] * 20 + [[-1]] * 10,
               "les_pieds": {"poses": [[-2]] * 100 + [[-1]] * 60 + [[-2]] * 20 + [[-2]] * 20 + [[-1]] * 10}}
    a = la_lecture({"-2": R, "-1": N}, en_plus, -1)
    v("★★★★ côté moins : départ w, attendu w - 1, avant w + 1 ; 60 pieds sur l'avant contre 20 sur le départ : hérité",
      a is not None and (a["le_tour_de_depart"], a["le_tour_attendu"], a["le_tour_davant"]) == (-2, -3, -1)
      and a["les_restes"] == 80 and a["pieds_sur_le_tour_davant"] == 60 and a["pieds_sur_le_tour_de_depart"] == 20
      and a["la_part_heritee"] == 0.75 and a["la_lecture"] == HERITE, str(a))
    v("★★★★ le contrôle : les pieds des points du tour attendu, sur le tour de départ",
      a["le_controle"] == {"les_points": 120, "pieds_poses": 120, "sur_le_tour_de_depart": 120, "la_part": 1.0}, str(a["le_controle"]))
    ici = dict(en_plus, les_pieds={"poses": [[-2]] * 100 + [[-1]] * 20 + [[-2]] * 60 + [[-2]] * 20 + [[-1]] * 10})
    v("★★★★ 20 pieds sur l'avant contre 60 sur le départ : né ici", la_lecture({"-2": R}, ici, -1)["la_lecture"] == NE_ICI)
    mele = dict(en_plus, les_pieds={"poses": [[-2]] * 100 + [[-1]] * 40 + [[-2]] * 40 + [[-2]] * 20 + [[-1]] * 10})
    v("★★★ moitié-moitié : mêlé", la_lecture({"-2": R}, mele, -1)["la_lecture"] == MELE)
    deux = dict(en_plus, les_pieds={"poses": [[-2]] * 100 + [[-1, -2]] * 60 + [[-2]] * 20 + [[-2]] * 20 + [[-1]] * 10})
    v("★★★★ un pied posé sur le départ ET sur l'avant compte pour le départ",
      la_lecture({"-2": R}, deux, -1)["pieds_sur_le_tour_davant"] == 0)
    peu = dict(en_plus, les_pieds={"poses": [[-2]] * 100 + [[-1]] * 30 + [[]] * 50 + [[-2]] * 20 + [[-1]] * 10})
    v("★★★ moins de 50 pieds posés sur l'un des deux : non lu", la_lecture({"-2": R}, peu, -1)["la_lecture"] == NON_LU)
    v("★★★ un point posé sur le départ ET l'attendu n'est pas resté", la_lecture({"-2": R}, en_plus, -1)["les_restes"] == 80)
    a = la_lecture({"-3": R}, en_plus, 1)
    v("★★★ côté plus : attendu w + 1, avant w - 1", (a["le_tour_attendu"], a["le_tour_davant"]) == (-2, -4), str(a))
    v("★★★ une surface d'avant à deux tours, ou sans pieds : rien à lire",
      la_lecture({"-1": R, "-2": R}, en_plus, -1) is None and la_lecture({"-2": R}, {"les_poses": []}, -1) is None)

    def s_(rang, lecture, restes=80, ctl=0.9, j="juste"):
        return {"le_rang": rang, "la_justesse": j, "la_surface": {"les_restes": restes, "la_lecture": lecture, "le_controle": {"la_part": ctl}}}
    base = lambda ss: {"les_pannes": [], "redonne_344": True, "redonne_345": True, "les_surfaces": ss}  # noqa: E731
    v("★★★★ les trois quarts héritées : le retard vient de plus haut",
      le_verdict(base([s_(5, HERITE)] * 3 + [s_(5, NE_ICI)])).get("lissue", "").endswith("vient de plus haut"))
    v("★★★★ les trois quarts nées ici : il naît au saut qui le montre",
      le_verdict(base([s_(5, NE_ICI)] * 3 + [s_(5, MELE)])).get("lissue", "").endswith("au saut qui le montre"))
    v("★★★★ sinon : l'un et l'autre", le_verdict(base([s_(5, NE_ICI)] * 2 + [s_(5, HERITE)] * 2)).get("lissue", "").endswith("l'un et l'autre")
      and le_verdict(base([s_(5, HERITE)] * 5 + [s_(5, NE_ICI)] * 3)).get("lissue", "").endswith("l'un et l'autre"))
    loin = dict(en_plus, les_pieds={"poses": [[-4]] * 100 + [[-1]] * 60 + [[-2]] * 20 + [[-4]] * 20 + [[-1]] * 10})
    v("★★★★ au contrôle, un pied posé ailleurs que sur le tour de départ ne compte pas",
      la_lecture({"-2": R}, loin, -1)["le_controle"]["la_part"] == 0.0, str(la_lecture({"-2": R}, loin, -1)["le_controle"]))
    v("★★★★ seules les surfaces justes à cheval des graines 4 à 8 comptent",
      le_verdict(base([s_(5, HERITE)] * 3 + [s_(2, NE_ICI)] * 3 + [s_(5, NE_ICI, restes=49)] * 3 + [s_(5, NE_ICI, j="faux : deux tours")] * 3))
      .get("n") == 3)
    v("★★★★ moins de la moitié lues : indécidable", not le_verdict(base([s_(5, HERITE)] + [s_(5, NON_LU)] * 2))["decidable"]
      and le_verdict(base([s_(5, HERITE)] * 2 + [s_(5, NON_LU)] * 2))["decidable"])
    v("★★★★ le contrôle sous la moitié sur plus d'un quart des surfaces : indécidable",
      not le_verdict(base([s_(5, HERITE, ctl=0.49)] * 2 + [s_(5, HERITE)] * 2))["decidable"]
      and le_verdict(base([s_(5, HERITE, ctl=0.5)] + [s_(5, HERITE)] * 3))["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 344 ou 345 : indécidable",
      not le_verdict(dict(base([s_(5, HERITE)] * 3), redonne_345=False))["decidable"]
      and not le_verdict(dict(base([s_(5, HERITE)] * 3), redonne_344=False))["decidable"])
    p = les_premiers([{"la_chaine": "bornée", "le_rang": 8, "le_cote": "moins", "le_saut": k, "la_justesse": j,
                       "la_surface": {"les_restes": r}} for k, j, r in ((2, "juste", 10), (3, "juste", 60), (5, "juste", 90),
                                                                        (1, "faux : deux tours", 90))])
    v("★★★ le premier saut juste à cheval d'une chaîne", p == [{"la_chaine": "bornée", "le_rang": 8, "le_cote": "moins",
                                                                "le_premier_saut": 3}], str(p))

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
