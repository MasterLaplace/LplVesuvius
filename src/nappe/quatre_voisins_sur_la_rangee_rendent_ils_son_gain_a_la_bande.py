"""Quatre voisins sur la même rangée, deux de chaque côté, rendent-ils à la bande `w028-037` le gain que la procédure y perd ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE CALCUL. Ce qui était vu avant d'écrire : tout ce que `257` à `293` publient. Sur la bande,
la procédure n'améliore pas le premier saut (`281`), et rien ne s'en distingue du hasard (`290`). Chacun de ses blocs n'a de
voisins qu'à l'est et à l'ouest. Sur le segment `20230702185753`, une ancre prise sur deux voisins seulement double les
corrections et perd l'essentiel du gain, quelle que soit sa direction (`292`, `293`). Mais la bande, qui n'a qu'une rangée de
blocs, en a beaucoup sur cette rangée : ses 84 blocs candidats se suivent.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Une ancre prise sur quatre voisins a autant de chunks que celle de `275`. Sur
la bande, ces quatre voisins ne peuvent être que sur la rangée : deux à l'est, deux à l'ouest. La marche s'étend alors sur cinq
blocs d'une rangée, et l'ancre est la médiane de sa différence sur les quatre voisins. Rien n'est rendu de neuf : les piles et les
tables de pas de la rangée existent (`281`).

## Ce qui est fait, déclaré avant le calcul

- Les voisins d'un bloc sont les blocs candidats de sa rangée, à l'est puis à l'ouest, jusqu'à deux de chaque côté, en s'arrêtant
  au premier qui manque : une marche ne se relie pas à travers un trou.
- La marche s'étend sur deux blocs de chaque côté du bloc ; l'ancre est la médiane de la différence des marches sur la rangée du
  bloc, le bloc retiré. Le reste est la décision de `264`, comme dans `275`.
- Le même calcul est fait sur le segment, pour savoir ce que cette façon rend là où la procédure marche, et sur la bande.
- Le test est celui de `290`, sur les points et sur les blocs, au seuil de 0,05.

⚠ Les contrôles rendent la mesure décidable : avec un seul bloc de chaque côté et les voisins de `275`, le calcul redonne `275`
sur le segment et `281` sur la bande, bloc par bloc.

## Les issues, exclusives, sur la bande

- le gain net sur les points est positif, et le test du signe passe sous 0,05 sur les points et sur les blocs : quatre voisins sur
  la rangée rendent à la bande un gain qui se distingue du hasard ;
- sinon : ils ne le lui rendent pas.

⚠ Rapporté à côté : le même calcul sur le segment, contre `275` ; les blocs qui ne sont plus décidés.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : le deuxième saut ; plus de deux voisins de chaque côté.

Usage :
    uv run python src/nappe/quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.py --verifier
    uv run python src/nappe/quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.py \\
        --json docs/mesures/quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.json
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

from la_procedure_sans_juge_tient_elle_sur_la_bande import (LES_COUCHES_DE_LA_BANDE,  # noqa: E402
                                                            LES_SURFACES_DE_LA_BANDE, LE_PREMIER_SAUT)
from la_procedure_sans_juge_tient_elle_sur_la_bande import lire_le_plan as le_plan_de_281  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (LES_SURFACES, la_reunion,  # noqa: E402
                                                                     le_segment, les_rendus_sur_le_disque,
                                                                     les_tables, un_bloc)
from la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest import le_test  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import LE_BLOC  # noqa: E402
from lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment import lancre_est_ouest  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_275_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"
CE_QUE_281_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_la_bande.json"
LA_PORTEE = 2
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


def les_voisins_de_la_rangee(portee: int):
    """Les voisins candidats d'un bloc sur sa rangée, jusqu'à `portee` de chaque côté, arrêtés au premier qui manque."""
    def voisins(by: int, bx: int, candidats: set) -> list[tuple[int, int]]:
        out = []
        for sens in (-1, 1):
            for k in range(1, portee + 1):
                v = (by, bx + sens * k * LE_BLOC)
                if v not in candidats:
                    break
                out.append(v)
        return out
    return voisins


def les_blocs_differents(blocs: list[dict], publie: dict) -> list[str]:
    return sorted(f"{b['la_rangee']}_{b['la_colonne']}" for b in blocs
                  if b.get("decidable") != publie[(b["la_rangee"], b["la_colonne"])].get("decidable")
                  or (b.get("decidable") and any(b[k] != publie[(b["la_rangee"], b["la_colonne"])][k] for k in LES_COMPTES)))


def une_surface(tau0, err, glissade, candidats, surfaces, publie: dict) -> dict:
    rendus = les_rendus_sur_le_disque(candidats, surfaces)
    tables = les_tables(candidats, rendus, surfaces)
    tous = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade, surfaces)[0] for by, bx in sorted(candidats)]
    rangee = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade, surfaces,
                      les_voisins_de=les_voisins_de_la_rangee(LA_PORTEE), lancre=lancre_est_ouest, portee=LA_PORTEE)[0]
              for by, bx in sorted(candidats)]
    r = la_reunion(rangee)
    return {"les_blocs_qui_different_de_la_publiee": les_blocs_differents(tous, publie),
            "avec_quatre_voisins_sur_la_rangee": {"les_reunis": r, "le_test": le_test(r),
                                                  "les_non_decides": sum(1 for b in rangee if not b.get("decidable")),
                                                  "les_voisins": {str(k): sum(1 for b in rangee if b.get("les_voisins") == k)
                                                                  for k in range(1, 2 * LA_PORTEE + 1)}}}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : avec un bloc de chaque côté, le calcul ne redonne pas 275 ou 281"}
    t = r["la_bande"]["avec_quatre_voisins_sur_la_rangee"]["le_test"]
    if t["sur_les_points"]["le_gain_net"] > 0 and t["sur_les_points"]["sous_le_seuil"] and t["sur_les_blocs"]["sous_le_seuil"]:
        return {"lissue": "quatre voisins sur la rangée rendent à la bande un gain qui se distingue du hasard"}
    return {"lissue": "quatre voisins sur la rangée ne rendent pas à la bande un gain qui se distingue du hasard"}


def mesurer() -> dict:
    debut = time.monotonic()
    tau0, err, glissade, candidats = le_segment()
    p275 = {(b["la_rangee"], b["la_colonne"]): b for b in json.loads(CE_QUE_275_A_PUBLIE.read_text())["les_blocs"]}
    d281 = json.loads(CE_QUE_281_A_PUBLIE.read_text())
    p281 = {(b["la_rangee"], b["la_colonne"]): b for b in d281["les_blocs"]}
    out = {"le_segment": une_surface(tau0, err, glissade, candidats, LES_SURFACES, p275)}
    tb = np.load(LE_PREMIER_SAUT)
    eb = tb - np.load(LES_COUCHES_DE_LA_BANDE)[..., 0]
    out["la_bande"] = une_surface(tb, eb, float(d281["la_glissade_voxels"]), le_plan_de_281()["candidats"],
                                  LES_SURFACES_DE_LA_BANDE, p281)
    out["decidable"] = not (out["le_segment"]["les_blocs_qui_different_de_la_publiee"]
                            or out["la_bande"]["les_blocs_qui_different_de_la_publiee"])
    out["le_verdict"] = le_verdict(out)
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


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

    c = {(16, x) for x in (0, 16, 32, 64, 80)} | {(0, 32), (32, 32)}
    vo = les_voisins_de_la_rangee(2)
    v("★★★★ les voisins sont sur la rangée, deux de chaque côté au plus, arrêtés au premier qui manque",
      sorted(vo(16, 32, c)) == [(16, 0), (16, 16)] and sorted(vo(16, 64, c)) == [(16, 80)], str(vo(16, 32, c)))
    v("★★★ les blocs au nord et au sud n'en sont pas", (0, 32) not in vo(16, 32, c) and (32, 32) not in vo(16, 32, c))
    v("★★ avec une portée d'un bloc, ce sont les voisins est et ouest", sorted(les_voisins_de_la_rangee(1)(16, 16, c)) ==
      [(16, 0), (16, 32)])
    t_ = lambda g, pp, pb: {"decidable": True, "la_bande": {"avec_quatre_voisins_sur_la_rangee": {"le_test": {  # noqa: E731
        "sur_les_points": {"le_gain_net": g, "sous_le_seuil": pp}, "sur_les_blocs": {"sous_le_seuil": pb}}}}}
    v("★★★★ les issues : un gain positif et les deux tests sous le seuil, sinon non, indécidable sans contrôle",
      "ne rendent pas" not in le_verdict(t_(5, True, True))["lissue"]
      and all("ne rendent pas" in le_verdict(t_(*x))["lissue"] for x in ((-5, True, True), (5, False, True), (5, True, False)))
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
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
    r = mesurer()
    texte = json.dumps(r, ensure_ascii=False, indent=1)
    print(texte)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
