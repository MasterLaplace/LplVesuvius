#!/usr/bin/env python3
"""Un cap change-t-il la course ? — deux courses aux MEMES departs, appariees bande par bande.

⭐⭐⭐⭐ POURQUOI CE FICHIER EXISTE. `132` a construit `memoire_du_cap` et mesure par relecture
qu'il devrait marcher ; il a dit aussi que seule une course qui l'emploie peut le juger, parce que
changer la direction change ce que le marcheur lit au pas suivant. Cette course existe
(`la_course_a_cap.json`) et son temoin aussi (`la_re_course_large.json`, λ = 0) : memes departs,
meme plafond, meme arret sur vide. Ce qui manque est l'instrument qui les met COTE A COTE.

⚠⚠⚠ APPARIE PAR BANDE, JAMAIS PAR MEDIANE. Les deux courses n'ont pas les memes longueurs de
marche, et `131` a deja paye que deux medianes sur des lots de longueurs differentes ne se
comparent pas. Ici chaque bande a UNE marche dans chaque course, partie du MEME point : la
difference est donc un effet du cap et de rien d'autre, et le test est celui des differences
appariees.

⚠⚠ CE QUE « PLUS DROIT » NE DIT PAS. Une rectitude qui monte peut vouloir dire que le marcheur
traverse mieux, ou qu'il s'arrete avant d'avoir eu le temps de tourner : la rectitude est lue
AVEC la longueur de la marche et le motif de son arret, et le verdict porte les trois.

⚠ Zero lecture distante : tout vient des deux JSON de course.

Usage :
    uv run python src/nappe/un_cap_change_t_il_la_course.py --verifier
    uv run python src/nappe/un_cap_change_t_il_la_course.py \\
        --sans-cap docs/mesures/la_re_course_large.json \\
        --avec-cap docs/mesures/la_course_a_cap.json \\
        --json docs/mesures/un_cap_change_t_il_la_course.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))

from ce_qui_porte_le_taux import est_aveugle  # noqa: E402
from le_marcheur_derive_t_il import _rectitude, _wilcoxon  # noqa: E402

SANS_CAP = RACINE / "docs" / "mesures" / "la_re_course_large.json"
AVEC_CAP = RACINE / "docs" / "mesures" / "la_course_a_cap.json"


def _motif(cel: dict) -> str:
    if cel.get("sortie"):
        return "sortie du volume"
    if cel.get("plus_rien_a_lire"):
        return "plus rien a lire"
    if cel.get("au_plafond"):
        return "plafond"
    return "arret"


def _marche(cel: dict) -> dict | None:
    """Une marche coupee a son premier pas aveugle, comme `le_marcheur_derive_t_il` le fait.

    ⚠ La coupure est la meme que celle de `119` : `116` a mesure que la cecite est absorbante,
    donc ce qui suit le premier pas aveugle est la trajectoire d'un marcheur qui ne lit rien.
    """
    etapes = [e for e in cel.get("etapes", []) if "confirme" in e]
    n = next((i for i, e in enumerate(etapes) if est_aveugle(e)), len(etapes))
    voyants = etapes[:n]
    if not voyants:
        return None
    d = [e["direction"] for e in voyants]
    a = [float(e["avance_um"]) for e in voyants]
    return {"pas_voyants": len(voyants), "rectitude": round(_rectitude(d, a), 4),
            "chemin_um": round(float(sum(a)), 1),
            "confirmes": sum(1 for e in voyants if e.get("confirme")),
            "pas_confirmes_consecutifs": int(cel.get("pas_confirmes") or 0),
            "fin": _motif(cel)}


def apparier(sans: dict, avec: dict) -> dict:
    """Les bandes presentes dans les DEUX courses, et ce que chaque marche y a fait.

    ⚠ Une bande presente d'un seul cote est comptee, jamais appariee a une autre : apparier deux
    departs differents ferait porter au cap une difference qui est celle du lieu.
    """
    def par_bande(course):
        out = {}
        for ligne in course.get("lignes", []):
            cle = (int(ligne["de"]), int(ligne["a"]))
            det = ligne.get("detail", [])
            if det:
                out[cle] = (ligne.get("rayon_mm"), det[0])
        return out

    a, b = par_bande(sans), par_bande(avec)
    communes = sorted(set(a) & set(b))
    paires, ignorees = [], sorted((set(a) ^ set(b)))
    for cle in communes:
        ma, mb = _marche(a[cle][1]), _marche(b[cle][1])
        if ma is None or mb is None:
            ignorees.append(cle)
            continue
        paires.append({"bande": list(cle), "rayon_mm": a[cle][0], "sans_cap": ma, "avec_cap": mb})
    return {"paires": paires, "bandes_non_appariees": [list(k) for k in ignorees]}


def juger(paires: list[dict]) -> dict:
    """Le verdict apparie : le cap redresse-t-il, et mene-t-il plus loin ?

    ⚠⚠ Deux questions, deux tests, et elles peuvent repondre en sens contraire : un marcheur
    plus droit qui s'arrete plus tot n'a pas gagne de portee. Le verdict porte les deux, et le
    lecteur n'a pas a choisir lequel croire.

    ⚠ Un Wilcoxon a moins de sept paires ne peut pas descendre sous 0,05 (plancher 2/2^n) : le
    test se declare alors indecidable plutot que de rendre un p qui ressemble a un « non ».
    """
    n = len(paires)
    if n < 7:
        return {"decidable": False, "pourquoi": f"{n} paire(s), il en faut au moins sept "
                                                 "pour qu'un Wilcoxon puisse trancher"}
    rs = np.array([p["sans_cap"]["rectitude"] for p in paires])
    ra = np.array([p["avec_cap"]["rectitude"] for p in paires])
    ls = np.array([p["sans_cap"]["pas_voyants"] for p in paires], dtype=float)
    la = np.array([p["avec_cap"]["pas_voyants"] for p in paires], dtype=float)
    p_rect = _wilcoxon(ra, rs)
    p_long = _wilcoxon(la, ls)
    plus_droites = int(np.sum(ra > rs))
    plus_longues = int(np.sum(la > ls))
    return {
        "decidable": True, "paires": n,
        "rectitude_mediane_sans_cap": round(float(np.median(rs)), 4),
        "rectitude_mediane_avec_cap": round(float(np.median(ra)), 4),
        "marches_plus_droites_avec_cap": plus_droites,
        "p_rectitude": None if p_rect is None else round(p_rect, 5),
        "pas_voyants_median_sans_cap": float(np.median(ls)),
        "pas_voyants_median_avec_cap": float(np.median(la)),
        "marches_plus_longues_avec_cap": plus_longues,
        "p_longueur": None if p_long is None else round(p_long, 5),
        "au_plafond_sans_cap": sum(1 for p in paires if p["sans_cap"]["fin"] == "plafond"),
        "au_plafond_avec_cap": sum(1 for p in paires if p["avec_cap"]["fin"] == "plafond"),
        "plus_rien_a_lire_sans_cap": sum(1 for p in paires
                                         if p["sans_cap"]["fin"] == "plus rien a lire"),
        "plus_rien_a_lire_avec_cap": sum(1 for p in paires
                                         if p["avec_cap"]["fin"] == "plus rien a lire"),
        "taux_sans_cap": round(sum(p["sans_cap"]["confirmes"] for p in paires)
                               / max(1, int(ls.sum())), 4),
        "taux_avec_cap": round(sum(p["avec_cap"]["confirmes"] for p in paires)
                               / max(1, int(la.sum())), 4),
        # ⭐⭐⭐⭐ Les deux verdicts, separes exprès.
        "le_cap_redresse_la_marche": bool(p_rect is not None and p_rect < 0.05
                                          and plus_droites > n / 2),
        "le_cap_mene_plus_loin": bool(p_long is not None and p_long < 0.05
                                      and plus_longues > n / 2),
        "le_cap_raccourcit_la_marche": bool(p_long is not None and p_long < 0.05
                                            and plus_longues < n / 2)}


def le_cout(sans: dict, avec: dict) -> dict:
    """Le cout d'un pas dans chaque course, tel que chacune le PUBLIE — et le rapport.

    ⚠ Le rapport est celui des deux nombres publies. Si l'un porte du sommeil de machine (la
    course de `131` a precede l'horloge monotone), c'est au document de le dire : ce module ne
    peut pas le savoir depuis les fichiers.
    """
    s = (sans.get("resume") or {}).get("secondes_par_pas")
    a = (avec.get("resume") or {}).get("secondes_par_pas")
    if s is None or a is None or a <= 0:
        return {"decidable": False, "pourquoi": "une des deux courses ne publie pas son cout"}
    return {"decidable": True, "secondes_par_pas_sans_cap": s, "secondes_par_pas_avec_cap": a,
            "rapport": round(float(s) / float(a), 1)}


def mesurer(sans_p: Path = SANS_CAP, avec_p: Path = AVEC_CAP) -> dict:
    sans = json.loads(sans_p.read_text(encoding="utf-8"))
    avec = json.loads(avec_p.read_text(encoding="utf-8"))
    for nom, c in (("sans cap", sans), ("avec cap", avec)):
        if c.get("course_incomplete"):
            raise ValueError(f"la course {nom} est incomplete")
    if float(sans.get("memoire_du_cap") or 0.0) != 0.0:
        raise ValueError("la course `sans cap` porte une memoire non nulle")
    if float(avec.get("memoire_du_cap") or 0.0) <= 0.0:
        raise ValueError("la course `avec cap` n'a pas de memoire du cap")
    for champ in ("pas_max", "arret_sur_vide", "selecteur", "demi_cube_voxels", "fenetre_locale"):
        if sans.get(champ) != avec.get(champ):
            raise ValueError(f"les deux courses different sur `{champ}` : "
                             f"{sans.get(champ)!r} contre {avec.get(champ)!r}")
    ap = apparier(sans, avec)
    return {"sans_cap": sans_p.name, "avec_cap": avec_p.name,
            "memoire_du_cap": avec.get("memoire_du_cap"), "pas_max": avec.get("pas_max"),
            **ap, "verdict": juger(ap["paires"]), "cout": le_cout(sans, avec)}


def afficher(r: dict) -> None:
    v = r["verdict"]
    print(f"{r['sans_cap']} (λ = 0) contre {r['avec_cap']} (λ = {r['memoire_du_cap']}) · "
          f"{len(r['paires'])} paires · {len(r['bandes_non_appariees'])} bande(s) non appariée(s)")
    for p in r["paires"]:
        s, a = p["sans_cap"], p["avec_cap"]
        print(f"   r {p['rayon_mm']:>5} mm · sans {s['pas_voyants']:>3} pas, rect {s['rectitude']:.3f}"
              f", {s['fin']:<16} · avec {a['pas_voyants']:>3} pas, rect {a['rectitude']:.3f}, {a['fin']}")
    if not v.get("decidable"):
        print(f"⚠ {v['pourquoi']}")
        return
    print(f"\n★★★ LE CAP REDRESSE-T-IL LA MARCHE ? {'OUI' if v['le_cap_redresse_la_marche'] else 'NON'}")
    print(f"   rectitude médiane {v['rectitude_mediane_sans_cap']} → {v['rectitude_mediane_avec_cap']} · "
          f"{v['marches_plus_droites_avec_cap']}/{v['paires']} plus droites · p {v['p_rectitude']}")
    print(f"★★★ MÈNE-T-IL PLUS LOIN ? {'OUI' if v['le_cap_mene_plus_loin'] else 'NON'}"
          f"{' — IL RACCOURCIT' if v['le_cap_raccourcit_la_marche'] else ''}")
    print(f"   pas voyants médians {v['pas_voyants_median_sans_cap']} → {v['pas_voyants_median_avec_cap']} · "
          f"{v['marches_plus_longues_avec_cap']}/{v['paires']} plus longues · p {v['p_longueur']}")
    print(f"   au plafond {v['au_plafond_sans_cap']} → {v['au_plafond_avec_cap']} · plus rien à lire "
          f"{v['plus_rien_a_lire_sans_cap']} → {v['plus_rien_a_lire_avec_cap']} · taux "
          f"{v['taux_sans_cap']} → {v['taux_avec_cap']}")
    c = r["cout"]
    if c.get("decidable"):
        print(f"   coût d'un pas : {c['secondes_par_pas_sans_cap']} s → {c['secondes_par_pas_avec_cap']} s "
              f"(rapport {c['rapport']})")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def course(virage_deg, pas, memoire, bandes=12, plafond=20, secondes=None):
        lignes = []
        for i in range(bandes):
            th = np.radians(virage_deg)
            e = []
            d = np.array([0.0, 0.0, 1.0])
            for k in range(1, pas + 1):
                c, s = np.cos(th * k), np.sin(th * k)
                d = np.array([0.0, s, c])
                e.append({"pas": k, "confirme": k % 4 != 0, "oriente": True, "rien_lu": False,
                          "desaccord_des_moities_deg": 3.0, "planarite": 0.5,
                          "direction": [float(x) for x in d], "avance_um": 173.0,
                          "parcouru_um": 173.0 * k})
            lignes.append({"de": 10 * i, "a": 10 * i + 9, "rayon_mm": 4.0 + i,
                           "detail": [{"etapes": e, "pas_parcourus": pas,
                                       "pas_confirmes": 3, "sortie": False,
                                       "plus_rien_a_lire": pas < plafond,
                                       "au_plafond": pas >= plafond, "longueur_um": 173.0 * pas}]})
        out = {"pas_max": plafond, "arret_sur_vide": True, "selecteur": "deux_roles",
               "demi_cube_voxels": 20, "fenetre_locale": False, "memoire_du_cap": memoire,
               "lignes": lignes, "resume": {}}
        if secondes is not None:
            out["resume"]["secondes_par_pas"] = secondes
        return out

    sans = course(8.0, 20, 0.0, secondes=100.0)
    avec = course(1.0, 20, 0.75, secondes=4.0)
    ap = apparier(sans, avec)
    v("douze bandes communes font douze paires", len(ap["paires"]) == 12
      and ap["bandes_non_appariees"] == [])
    j = juger(ap["paires"])
    v("un cap qui redresse est vu", j["decidable"] and j["le_cap_redresse_la_marche"],
      f"{j.get('marches_plus_droites_avec_cap')}/12, p {j.get('p_rectitude')}")
    v("... sans prétendre qu'il mène plus loin quand les longueurs sont égales",
      not j["le_cap_mene_plus_loin"] and not j["le_cap_raccourcit_la_marche"]
      and j["p_longueur"] is None)
    c = le_cout(sans, avec)
    v("le coût rend le rapport des deux nombres publiés", c["decidable"] and c["rapport"] == 25.0)
    # ⚠⚠ LA SONDE : inverser les deux courses doit inverser le verdict, sinon le test ne lit pas
    # le sens de la difference.
    j2 = juger(apparier(avec, sans)["paires"])
    v("sonde : les courses inversées ne donnent PAS un cap qui redresse",
      not j2["le_cap_redresse_la_marche"] and j2["marches_plus_droites_avec_cap"] == 0)
    court = course(1.0, 9, 0.75)
    j3 = juger(apparier(sans, court)["paires"])
    v("un cap qui s'arrête plus tôt est dit RACCOURCIR, pas mener plus loin",
      j3["le_cap_raccourcit_la_marche"] and not j3["le_cap_mene_plus_loin"],
      f"p {j3['p_longueur']}")
    v("... et le motif d'arrêt suit", j3["plus_rien_a_lire_avec_cap"] == 12
      and j3["au_plafond_sans_cap"] == 12)
    v("six paires sont indécidables plutôt qu'un « non »",
      not juger(apparier(course(8.0, 20, 0.0, bandes=6), course(1.0, 20, 0.75, bandes=6))["paires"])["decidable"])
    autre = course(1.0, 20, 0.75, bandes=8)
    autre["lignes"][0]["de"], autre["lignes"][0]["a"] = 999, 1000
    ap2 = apparier(sans, autre)
    v("une bande présente d'un seul côté est comptée, jamais appariée",
      len(ap2["paires"]) == 7 and len(ap2["bandes_non_appariees"]) == 6,
      f"{len(ap2['paires'])} paires, {len(ap2['bandes_non_appariees'])} non appariées")
    v("une course sans coût publié rend le coût indécidable",
      not le_cout(course(8.0, 20, 0.0), avec)["decidable"])

    if SANS_CAP.is_file() and AVEC_CAP.is_file():
        r = mesurer()
        v("sur les données réelles, les seize bandes sont appariées", len(r["paires"]) == 16,
          f"{len(r['paires'])}")
        v("... et le verdict est rendu", r["verdict"].get("decidable") is True)
        v("... et le coût aussi", r["cout"].get("decidable") is True,
          f"rapport {r['cout'].get('rapport')}")
        # ⚠ L'affichage tourne sur le vrai résultat : c'est le chemin qui imprime le nombre publié,
        # et une batterie qui ne l'atteint pas ne peut pas échouer là où ça compte.
        import io, contextlib  # noqa: PLC0415
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            afficher(r)
        v("... et l'affichage tourne dessus", "LE CAP REDRESSE-T-IL" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sans-cap", type=Path, default=SANS_CAP)
    p.add_argument("--avec-cap", type=Path, default=AVEC_CAP)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.sans_cap, a.avec_cap)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
