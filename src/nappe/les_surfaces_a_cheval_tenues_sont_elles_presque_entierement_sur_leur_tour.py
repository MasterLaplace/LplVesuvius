"""Les surfaces à cheval que le compte de 345 et le seuil de 50 points à zéro tiennent sur les graines 4 à 8 sont-elles presque entièrement sur le tour attendu, et plus que celles qu'ils refusent ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA PART DES POINTS SUR LE TOUR ATTENDU NE SOIT LUE, SURFACE PAR SURFACE, SELON QUE LE CRITÈRE LES
TIENT OU NON. Ce qui était vu avant d'écrire : tout ce que `296` à `352` publient, dont `R4-F535` (sous les 60 surfaces justes à cheval,
la part des points posés hors du tour attendu, restés ou au-delà, va de 5 à 45 %, 17 % en médiane) et `R4-F538` (le compte et le seuil
ensemble tiennent 23 des 60 sauts justes à cheval ; ce qu'ils tiennent est sain à 62 %). Ce qui n'était pas vu : cette part pour les
surfaces tenues et pour les surfaces refusées séparément.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P149`. Un saut est à cheval dès 50 points hors du tour attendu, soit 5 % de ses points. Si
les surfaces à cheval que le critère tient le sont à peine, ce qu'il tient est plus sain que ses 62 % ne le disent, et c'est la part de la
surface sur son tour, et non un oui ou un non, qui dira ce que vaut une première surface pour `#5`.

## Ce qui est fait

- **Aucune mesure neuve** : `345` et `349` rapprochés saut par saut, par les fonctions de `352`.
- **La part sur le tour attendu** d'une surface : parmi ses points du compte de `345` posés sur un tour publié, la part posée sur le tour
  attendu, telle que `349` la publie.
- **Les groupes** : les surfaces justes à cheval des graines 4 à 8 que le critère de `352` tient, et celles qu'il refuse.
- **La règle** : au moins 5 surfaces de chaque côté, sinon indécidable. Si la médiane des tenues est d'au moins 90 % et plus haute que
  celle des refusées, **oui, elles sont presque entièrement sur le tour attendu, et plus que les refusées** ; si elle est d'au moins 90 %
  sans être plus haute, **presque entièrement, mais pas plus que les refusées** ; sinon, **non**.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, les surfaces à cheval que le critère tient sont sur le tour attendu à p % en médiane,
celles qu'il refuse à q %**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La même part pour les sauts sains tenus et refusés, et pour les sauts faux ; et, sur tout ce que le critère tient, la part de tous les
points posés qui le sont sur le tour attendu.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où, sur la surface, sont les points hors du tour attendu ; et ce que vaut tout ceci sur PHerc0358.

Usage :
    uv run python src/nappe/les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.py --verifier
    uv run python src/nappe/les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.py \\
        --json docs/mesures/les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))

import le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains as m352  # noqa: E402

LA_PART_PRESQUE_ENTIERE = 0.9
LE_MINIMUM = 5


def la_part(a: dict) -> float | None:
    """La part des points posés d'une surface qui le sont sur le tour attendu ; None sans point posé."""
    return round(a["sur_le_tour_attendu"] / a["les_points_poses"], 4) if a["les_points_poses"] else None


def les_parts(d349: dict, sauts: dict, graines=(4, 5, 6, 7, 8)) -> dict:
    """Pour chaque groupe de `352` et selon que le critère le tient ou non, les parts sur le tour attendu, surface par surface ; et les
    points posés et sur le tour attendu, sommés sur tout ce que le critère tient."""
    groupes = m352.les_groupes(d349, graines)
    par_cle = {(s["la_chaine"], s["le_rang"], s["le_cote"], s["le_saut"]): s["la_surface"] for s in d349["les_surfaces"]}
    out, poses, sur = {}, 0, 0
    for g, cles in groupes.items():
        for tenu in (True, False):
            xs = [k for k in cles if m352.tient(sauts[k]) is tenu]
            out[f"{g}_{'tenus' if tenu else 'refuses'}"] = [p for p in (la_part(par_cle[k]) for k in xs) if p is not None]
            if tenu:
                poses += sum(par_cle[k]["les_points_poses"] for k in xs)
                sur += sum(par_cle[k]["sur_le_tour_attendu"] for k in xs)
    out["tout_ce_qui_est_tenu"] = {"les_points_poses": poses, "sur_le_tour_attendu": sur,
                                   "la_part": round(sur / poses, 4) if poses else None}
    return out


def le_verdict(d: dict) -> dict:
    if not d["le_controle"]:
        return {"decidable": False, "lissue": "indécidable : les sauts de 349 ne se retrouvent pas dans 345"}
    t, r = d["les_parts"]["les_a_cheval_tenus"], d["les_parts"]["les_a_cheval_refuses"]
    if len(t) < LE_MINIMUM or len(r) < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {len(t)} surfaces à cheval tenues et {len(r)} refusées"}
    mt, mr = statistics.median(t), statistics.median(r)
    tete = (f"sur les graines 4 à 8, les surfaces à cheval que le critère tient sont sur le tour attendu à {round(100 * mt)} % en médiane, "
            f"celles qu'il refuse à {round(100 * mr)} %")
    if mt >= LA_PART_PRESQUE_ENTIERE and mt > mr:
        suite = "oui, elles sont presque entièrement sur le tour attendu, et plus que les refusées"
    elif mt >= LA_PART_PRESQUE_ENTIERE:
        suite = "presque entièrement, mais pas plus que les refusées"
    else:
        suite = "non"
    return {"decidable": True, "la_mediane_des_tenues": round(mt, 4), "la_mediane_des_refusees": round(mr, 4), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d345, d349 = (json.loads(p.read_text()) for p in (m352.CE_QUE_345_A_PUBLIE, m352.CE_QUE_349_A_PUBLIE))
    sauts = m352.les_sauts_345(d345)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part_presque_entiere": LA_PART_PRESQUE_ENTIERE, "le_minimum": LE_MINIMUM, "le_seuil": m352.LE_SEUIL},
         "le_controle": m352.le_controle(d349, sauts)}
    if d["le_controle"]:
        d["les_parts"] = les_parts(d349, sauts)
    d["le_verdict"] = le_verdict(d)
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

    v("★★★★ la part sur le tour attendu est prise sur les points posés, pas sur tous",
      la_part({"sur_le_tour_attendu": 90, "les_points_poses": 100, "les_points": 400}) == 0.9
      and la_part({"sur_le_tour_attendu": 0, "les_points_poses": 0}) is None)

    def surf(n, j, cheval, sur, poses=100):
        return {"la_chaine": "bornée", "le_rang": 8, "le_cote": "moins", "le_saut": n, "la_justesse": j,
                "la_surface": {"a_cheval": cheval, "sur_le_tour_attendu": sur, "les_points_poses": poses}}
    d349 = {"les_surfaces": [surf(1, "juste", True, 95), surf(2, "juste", True, 70), surf(3, "juste", False, 99),
                             surf(4, "faux : deux tours", True, 50)]}
    k = lambda n: ("bornée", 8, "moins", n)  # noqa: E731
    sauts = {k(1): {"tient_345": True, "les_zeros": 10}, k(2): {"tient_345": True, "les_zeros": 80},
             k(3): {"tient_345": True, "les_zeros": 0}, k(4): {"tient_345": False, "les_zeros": 0}}
    p = les_parts(d349, sauts)
    v("★★★★ les surfaces à cheval tenues et refusées par le critère de 352, chacune à sa part",
      p["les_a_cheval_tenus"] == [0.95] and p["les_a_cheval_refuses"] == [0.7] and p["les_sains_tenus"] == [0.99]
      and p["les_faux_refuses"] == [0.5], str(p))
    v("★★★★ sur tout ce qui est tenu, les points posés et sur le tour attendu sont sommés",
      p["tout_ce_qui_est_tenu"] == {"les_points_poses": 200, "sur_le_tour_attendu": 194, "la_part": 0.97}, str(p["tout_ce_qui_est_tenu"]))

    def d_(t, r, ctl=True):
        return {"le_controle": ctl, "les_parts": {"les_a_cheval_tenus": t, "les_a_cheval_refuses": r}}
    v("★★★★ médiane des tenues à 90 % et plus haute : oui", le_verdict(d_([0.9] * 5, [0.8] * 5))["lissue"].endswith("plus que les refusées"))
    v("★★★★ à 90 % mais pas plus haute : pas plus que les refusées",
      le_verdict(d_([0.92] * 5, [0.92] * 5))["lissue"].endswith("pas plus que les refusées")
      and le_verdict(d_([0.9] * 5, [0.95] * 5))["lissue"].endswith("pas plus que les refusées"))
    v("★★★★ sous 90 % : non", le_verdict(d_([0.89] * 5, [0.5] * 5))["lissue"].endswith("; non"))
    v("★★★ la médiane, pas la moyenne", le_verdict(d_([0.1, 0.95, 0.95, 0.95, 0.95], [0.5] * 5))["lissue"].endswith("plus que les refusées"))
    v("★★★ moins de 5 d'un côté : indécidable", not le_verdict(d_([0.95] * 4, [0.5] * 5))["decidable"]
      and not le_verdict(d_([0.95] * 5, [0.5] * 4))["decidable"])
    v("★★★ le contrôle tombé : indécidable", not le_verdict(d_([0.95] * 5, [0.5] * 5, ctl=False))["decidable"])

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
