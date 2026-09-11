#!/usr/bin/env python3
"""La fenêtre locale s'emballe sur la vraie matière — la boucle est circulaire.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST LA RE-COURSE QUI L'A TROUVÉ EN UNE BANDE. `122` a écrit la
fenêtre qui suit l'espacement local et l'a démontrée sur une pile fabriquée : la butée passait de 3
à 0. Lancée sur le vrai volume avec un plafond de 112 pas, la même fenêtre voit son échelle partir
de **1,000** et atteindre **32,664** — des pas de **7 644 µm**, soit quarante-quatre feuilles.

⭐⭐⭐⭐ **LA CAUSE EST STRUCTURELLE, PAS UN RÉGLAGE.** L'espacement suivi vaut `avance / feuilles
franchies`, or `avance` est choisi **dans la fenêtre déjà mise à l'échelle**. La boucle n'a donc
aucune force de rappel vers la vérité : elle a un point fixe à **n'importe quelle** échelle où la
fraction franchie vaut un, et la fraction vaut un facilement à toute échelle puisque le gabarit est
rééchantillonné sur le candidat. Le système dérive le long d'un continuum de points fixes.

⚠⚠ **ET LA DÉMONSTRATION DE `122` NE POUVAIT PAS LE VOIR.** Une pile fabriquée n'a **qu'un seul**
pas vrai, donc le profil ne s'accorde qu'à cet endroit et la boucle est ramenée à chaque pas. Sur la
vraie matière le profil s'accorde sur une plage, et rien ne ramène. Une fixture qui ne peut pas
produire l'ambiguïté ne peut pas produire la panne.

⚠⚠⚠ **ET C'EST UNE MAUVAISE LECTURE DE `118`, À MA CHARGE.** Il concluait qu'il faut une fenêtre
centrée sur l'espacement **MESURÉ à l'endroit du pas**. J'ai implémenté « déduit du pas précédent »,
ce qui est circulaire. Les deux phrases se ressemblent et ne disent pas la même chose.

⚠ Aucune lecture distante : tout se calcule sur la bande que la re-course a écrite avant d'être
arrêtée.

  uv run python src/nappe/la_fenetre_locale_semballe.py --verifier
  uv run python src/nappe/la_fenetre_locale_semballe.py \
      --json docs/mesures/la_fenetre_locale_semballe.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
BANDE = RACINE / "docs" / "mesures" / "la_fenetre_locale_sur_la_vraie_matiere.json"
DE_113 = RACINE / "docs" / "mesures" / "jusquou_va_t_il_si_on_le_laisse.json"


def etapes(course: dict) -> list[dict]:
    """Les pas de la course, aplatis."""
    return [e for l in course.get("lignes", []) for c in l.get("detail", [])
            for e in c.get("etapes", []) if "confirme" in e]


def lechelle_semballe_t_elle(course: dict) -> dict:
    """L'échelle de la fenêtre reste-t-elle près de un, ou part-elle ?

    ⭐⭐⭐⭐ C'EST LE CONSTAT. Une fenêtre qui suit l'espacement doit osciller autour de la vérité,
    pas s'en éloigner. Le rapport entre l'échelle maximale et la minimale dit d'un coup si elle a
    dérivé : à un facteur cinq cents, elle n'oscille plus, elle part.

    ⚠ La course doit déclarer `fenetre_locale` : mesurer l'emballement d'une fenêtre qui n'a jamais
    été recentrée rendrait 1,0 partout et se lirait comme « tout va bien ».
    """
    if not course.get("fenetre_locale"):
        return {"decidable": False, "pourquoi": "la course n'a pas de fenêtre locale"}
    es = etapes(course)
    ech = [e.get("echelle_de_la_fenetre") for e in es if e.get("echelle_de_la_fenetre")]
    if len(ech) < 10:
        return {"decidable": False, "pourquoi": f"{len(ech)} pas avec une échelle"}
    pas_um = [e["pas_um"] for e in es]
    return {
        "decidable": True, "pas": len(es),
        "echelle_au_depart": round(float(ech[0]), 4),
        "echelle_max": round(float(max(ech)), 4),
        "echelle_min": round(float(min(ech)), 4),
        "echelle_finale": round(float(ech[-1]), 4),
        "amplitude": round(float(max(ech) / max(min(ech), 1e-9)), 1),
        "pas_um_max": round(float(max(pas_um)), 1),
        "pas_um_en_feuilles": round(float(max(pas_um)) / float(course["pas_nominal_um"]), 1),
        # ⚠ Sortir de la fenêtre publiée [0,5 ; 2,0] n'est pas en soi une panne — c'est le but.
        # S'en éloigner d'un facteur dix en est une.
        "sort_de_la_fenetre_publiee": bool(max(ech) > 2.0 or min(ech) < 0.5),
        "lechelle_semballe": bool(max(ech) / max(min(ech), 1e-9) > 10.0)}


def la_fenetre_locale_a_t_elle_aide(course: dict, reference: dict | None = None) -> dict:
    """Elle devait retirer la butée. L'a-t-elle fait sur la vraie matière ?

    ⭐⭐⭐ LE TEST QUI TRANCHE, et il compare ce qui est comparable : la part des pas en butée, chez
    la course à fenêtre locale et chez `113`, qui a la fenêtre fixe.

    ⚠⚠ Les deux courses n'ont ni le même plafond ni les mêmes bandes, donc seule la **part** est
    comparable, jamais le compte. Comparer 24 butées à 63 dirait surtout que l'une a fait plus de
    pas que l'autre.
    """
    es = etapes(course)
    if not es:
        return {"decidable": False, "pourquoi": "aucun pas"}
    butee = sum(1 for e in es if e.get("en_butee"))
    confirme = sum(1 for e in es if e.get("confirme"))
    out = {"decidable": True, "pas": len(es), "en_butee": butee,
           "part_en_butee": round(butee / len(es), 4),
           "confirmes": confirme, "taux": round(confirme / len(es), 4)}
    if reference:
        ref = etapes(reference)
        voyants = [e for e in ref
                   if not (e.get("desaccord_des_moities_deg") == 0.0
                           and e.get("planarite") == 0.0)]
        if voyants:
            b = sum(1 for e in voyants if e.get("en_butee"))
            out["reference_pas_voyants"] = len(voyants)
            out["reference_part_en_butee"] = round(b / len(voyants), 4)
            out["reference_taux"] = round(
                sum(1 for e in voyants if e.get("confirme")) / len(voyants), 4)
            # ⭐⭐⭐ Le verdict : elle devait faire BAISSER la part en butée.
            out["la_fenetre_locale_a_aide"] = bool(
                out["part_en_butee"] < out["reference_part_en_butee"])
    return out


def la_boucle_est_elle_circulaire(course: dict) -> dict:
    """L'espacement suivi est-il déterminé par la fenêtre qu'il détermine ?

    ⭐⭐⭐⭐ C'EST LE DIAGNOSTIC, ET IL EST ARITHMÉTIQUE. L'espacement déduit vaut `avance / f`, et
    `avance` est borné par la fenêtre, donc par l'échelle. Si l'échelle d'un pas prédit
    l'espacement qu'il déduit, la boucle se nourrit d'elle-même — ce n'est plus une mesure de la
    matière, c'est une mesure de la fenêtre.

    ⚠ Le lien est **garanti** par la construction, et c'est précisément ce qu'on veut montrer : la
    valeur du rho n'est donc pas un résultat, c'est la démonstration que la quantité suivie n'est
    pas indépendante de ce qu'elle règle. Le nommer évite de le lire comme une corrélation
    intéressante.
    """
    from scipy import stats  # noqa: PLC0415

    es = etapes(course)
    couples = [(e["echelle_de_la_fenetre"], e["pas_um"] / e["feuilles_franchies"])
               for e in es
               if e.get("echelle_de_la_fenetre") and e.get("feuilles_franchies")
               and not e.get("fraction_en_butee")]
    if len(couples) < 20:
        return {"decidable": False, "pourquoi": f"{len(couples)} pas déductibles"}
    ech = [a for a, _ in couples]
    esp = [b for _, b in couples]
    rho, p = stats.spearmanr(ech, esp)
    return {"decidable": True, "pas_deductibles": len(couples),
            "rho_echelle_espacement": round(float(rho), 4), "p": float(p),
            "garanti_par_construction": True,
            "la_boucle_se_nourrit_delle_meme": bool(rho > 0.6 and p < 0.05)}


def mesurer(bande: Path = BANDE, reference: Path | None = DE_113) -> dict:
    """Tout, depuis la bande que la re-course a écrite — aucune lecture distante."""
    course = json.loads(bande.read_text(encoding="utf-8"))
    ref = json.loads(reference.read_text(encoding="utf-8")) if reference and \
        reference.is_file() else None
    return {"source": bande.name, "plafond": course.get("pas_max"),
            "secondes": course.get("secondes"),
            "arret": (etapes(course) and course["lignes"][0]["detail"][0]["etapes"][-1]
                      .get("fin")) or None,
            "lechelle_semballe_t_elle": lechelle_semballe_t_elle(course),
            "la_fenetre_locale_a_t_elle_aide": la_fenetre_locale_a_t_elle_aide(course, ref),
            "la_boucle_est_elle_circulaire": la_boucle_est_elle_circulaire(course)}


def afficher(r: dict) -> None:
    print(f"source {r['source']} · plafond {r['plafond']} · arrêt « {r['arret']} »")
    e = r["lechelle_semballe_t_elle"]
    if e.get("decidable"):
        print(f"\n  échelle de la fenêtre : {e['echelle_au_depart']} au départ, "
              f"{e['echelle_min']} à {e['echelle_max']} (amplitude ×{e['amplitude']})")
        print(f"  pas le plus long : {e['pas_um_max']} µm, soit {e['pas_um_en_feuilles']} feuilles")
        print(f"  ⭐ l'échelle s'emballe : {e['lechelle_semballe']}")
    a = r["la_fenetre_locale_a_t_elle_aide"]
    if a.get("decidable"):
        print(f"\n  {a['pas']} pas · {a['en_butee']} en butée ({a['part_en_butee']}) · "
              f"taux {a['taux']}")
        if "reference_part_en_butee" in a:
            print(f"  contre `113` à fenêtre fixe : {a['reference_part_en_butee']} en butée, "
                  f"taux {a['reference_taux']} sur {a['reference_pas_voyants']} pas voyants")
            print(f"  ⭐ la fenêtre locale a aidé : {a['la_fenetre_locale_a_aide']}")
    b = r["la_boucle_est_elle_circulaire"]
    if b.get("decidable"):
        print(f"\n  échelle contre espacement déduit : rho {b['rho_echelle_espacement']:+.4f} "
              f"(p {b['p']:.2e}) sur {b['pas_deductibles']} pas")
        print(f"  ⭐ la boucle se nourrit d'elle-même : {b['la_boucle_se_nourrit_delle_meme']}")


def verifier() -> int:
    """La batterie, hors ligne, sur des courses FABRIQUÉES."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    def etape(ech, pas_um, f=1.0, butee=False, conf=True, fb=False):
        return {"pas": 1, "echelle_de_la_fenetre": ech, "pas_um": pas_um,
                "feuilles_franchies": f, "fraction_en_butee": fb, "en_butee": butee,
                "confirme": conf, "desaccord_des_moities_deg": 11.0, "planarite": 0.4}

    def course(es, locale=True):
        return {"pas_nominal_um": 173.0, "pas_max": 112, "fenetre_locale": locale,
                "lignes": [{"rayon_mm": 4.0, "detail": [{"etapes": es}]}]}

    # ⭐⭐⭐⭐ L'EMBALLEMENT SE VOIT, ET UNE FENETRE SAGE N'EST PAS ACCUSEE.
    emballe = course([etape(1.4 ** k, 173.0 * 1.4 ** k) for k in range(24)])
    e = lechelle_semballe_t_elle(emballe)
    v("une echelle qui part est vue", e["lechelle_semballe"], f"amplitude ×{e['amplitude']}")
    v("... et elle sort de la fenetre publiee", e["sort_de_la_fenetre_publiee"])
    sage = course([etape(1.0 + 0.04 * ((-1) ** k), 173.0) for k in range(24)])
    s = lechelle_semballe_t_elle(sage)
    v("sonde : une echelle qui oscille n'est PAS accusee", not s["lechelle_semballe"],
      f"amplitude ×{s['amplitude']}")
    v("... et elle ne sort pas de la fenetre publiee", not s["sort_de_la_fenetre_publiee"])
    v("une course sans fenetre locale est indecidable",
      not lechelle_semballe_t_elle(course([etape(1.0, 173.0)] * 24, locale=False))["decidable"])

    # ⭐⭐⭐ LA COMPARAISON DES PARTS, jamais des comptes.
    ref = {"lignes": [{"detail": [{"etapes":
           [etape(1.0, 173.0, butee=(k < 10), conf=(k >= 10)) for k in range(100)]}]}]}
    a = la_fenetre_locale_a_t_elle_aide(
        course([etape(1.0, 173.0, butee=(k < 4), conf=(k >= 4)) for k in range(20)]), ref)
    v("la part en butee est comparee, pas le compte",
      a["part_en_butee"] == 0.2 and a["reference_part_en_butee"] == 0.1,
      f"{a['part_en_butee']} contre {a['reference_part_en_butee']}")
    v("... et une part PLUS HAUTE dit que la fenetre n'a pas aide",
      not a["la_fenetre_locale_a_aide"])
    a2 = la_fenetre_locale_a_t_elle_aide(
        course([etape(1.0, 173.0, butee=(k < 1), conf=(k >= 1)) for k in range(20)]), ref)
    v("sonde : une part plus basse dit qu'elle a aide", a2["la_fenetre_locale_a_aide"],
      f"{a2['part_en_butee']} contre {a2['reference_part_en_butee']}")

    # ⭐⭐⭐⭐ LA CIRCULARITE.
    b = la_boucle_est_elle_circulaire(emballe)
    v("la boucle circulaire est vue", b["la_boucle_se_nourrit_delle_meme"],
      f"rho {b['rho_echelle_espacement']}")
    v("... et elle se declare garantie par construction", b["garanti_par_construction"])
    # ⚠⚠ LA SONDE : si l'avance ne suivait PAS la fenetre, la boucle serait rompue et le test doit
    # le dire. Sans elle, il repondrait « circulaire » a n'importe quelle course.
    rompue = course([etape(1.0 + 0.05 * k, 173.0 * (1.0 + 0.05 * (23 - k))) for k in range(24)])
    v("sonde : une avance qui NE suit pas la fenetre rompt la boucle",
      not la_boucle_est_elle_circulaire(rompue)["la_boucle_se_nourrit_delle_meme"],
      f"rho {la_boucle_est_elle_circulaire(rompue)['rho_echelle_espacement']}")
    v("moins de vingt pas deductibles rend indecidable",
      not la_boucle_est_elle_circulaire(course([etape(1.0, 173.0)] * 5))["decidable"])

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "b.json"
        p.write_text(json.dumps(emballe), encoding="utf-8")
        r = mesurer(p, reference=None)
        v("la mesure rend ses trois sections",
          all(k in r for k in ("lechelle_semballe_t_elle", "la_fenetre_locale_a_t_elle_aide",
                               "la_boucle_est_elle_circulaire")))
        afficher(r)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bande", type=Path, default=BANDE)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.bande)
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
