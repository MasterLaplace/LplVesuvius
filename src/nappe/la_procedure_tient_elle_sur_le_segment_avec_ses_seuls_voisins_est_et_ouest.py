"""Sur le segment `20230702185753`, la procédure de `265` tient-elle encore avec ses seuls voisins à l'est et à l'ouest ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE CALCUL. Ce qui était vu avant d'écrire : tout ce que `257` à `290` publient. Sur le segment,
la procédure corrige le premier saut au-delà du hasard, bloc par bloc : 42 blocs montent et 11 descendent (`275`, `290`). Sur la
bande `w028-037`, rien ne s'en distingue (`290`). Or la tranche de la bande ne fait que 37 chunks de haut, et tous ses blocs
candidats sont sur une seule rangée de blocs (`281`) : chacun n'a de voisins qu'à l'est et à l'ouest. Sur le segment, 268 des
340 blocs en ont quatre.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. La décision d'un bloc lit la marche d'un seul tenant sur le bloc et ses
voisins, et son ancre est la médiane de leur différence sur les voisins seuls. Deux voisins au lieu de quatre, c'est une marche
plus courte et une ancre prise sur moitié moins de chunks. Si la procédure cesse de tenir sur le segment quand on ne lui laisse
que l'est et l'ouest, la forme de la tranche de la bande suffit à expliquer ce qui y manque ; sinon, non.

## Ce qui est fait, déclaré avant le calcul

- Aucune pile n'est rendue, aucune table de pas n'est refaite : ce sont celles de `275`.
- La décision de `275` est refaite sur les 340 blocs, avec tous leurs voisins candidats : elle doit redonner, bloc par bloc, les
  points corrigés, les ratés rendus justes et les justes rendus ratés publiés.
- Puis elle est refaite avec les seuls voisins candidats de la même rangée de blocs, à l'est et à l'ouest. Un bloc qui n'en a
  aucun n'est pas décidé.
- Le test est celui de `290` : le test du signe sur les blocs qui montent contre ceux qui descendent, au seuil de 0,05.

⚠ Le contrôle rend la mesure décidable : la décision refaite avec tous les voisins redonne `275` bloc par bloc.

## Les issues, exclusives, avec les seuls voisins est et ouest

- bloc par bloc, le test du signe passe sous 0,05 : la procédure tient sur le segment avec ses seuls voisins est et ouest, et la
  forme de la tranche de la bande n'explique pas ce qui y manque ;
- il n'y passe pas : elle n'y tient plus, et la forme de la tranche suffit à l'expliquer.

⚠ Rapporté à côté : les comptes réunis sur les points ; les blocs qui ne sont plus décidés ; les mêmes blocs avec tous leurs
voisins, pour comparer à nombre de blocs égal.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une tranche de la bande plus haute ; le deuxième saut du segment.

Usage :
    uv run python src/nappe/la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest.py --verifier
    uv run python src/nappe/la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest.py \\
        --json docs/mesures/la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest.json
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

from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (la_reunion, le_segment,  # noqa: E402
                                                                     les_rendus_sur_le_disque, les_tables, un_bloc)
from le_voisinage_dit_il_quel_niveau_est_le_bon import les_voisins  # noqa: E402
from les_gains_publies_se_distinguent_ils_du_hasard import LE_SEUIL, le_test_du_signe, trois_chiffres  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_275_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


def les_voisins_est_ouest(by: int, bx: int, candidats: set) -> list[tuple[int, int]]:
    """Les voisins candidats d'un bloc sur sa propre rangée de blocs, à l'ouest et à l'est."""
    return [v for v in les_voisins(by, bx, candidats) if v[0] == by]


def le_test(reunis: dict) -> dict:
    m, d = reunis["les_blocs_qui_montent"], reunis["les_blocs_qui_descendent"]
    rj, jr = reunis["les_rates_rendus_justes"], reunis["les_justes_rendus_rates"]
    pb, pp = trois_chiffres(le_test_du_signe(m, d)), trois_chiffres(le_test_du_signe(rj, jr))
    return {"sur_les_blocs": {"les_blocs_qui_montent": m, "les_blocs_qui_descendent": d, "la_probabilite": pb,
                              "sous_le_seuil": pb < LE_SEUIL},
            "sur_les_points": {"les_rates_rendus_justes": rj, "les_justes_rendus_rates": jr, "le_gain_net": rj - jr,
                               "la_probabilite": pp, "sous_le_seuil": pp < LE_SEUIL}}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la décision refaite avec tous les voisins ne redonne pas 275"}
    if r["avec_les_seuls_voisins_est_et_ouest"]["le_test"]["sur_les_blocs"]["sous_le_seuil"]:
        return {"lissue": "la procédure tient sur le segment avec ses seuls voisins est et ouest"}
    return {"lissue": "la procédure ne tient plus sur le segment avec ses seuls voisins est et ouest"}


def mesurer() -> dict:
    debut = time.monotonic()
    tau0, err, glissade, candidats = le_segment()
    rendus = les_rendus_sur_le_disque(candidats)
    tables = les_tables(candidats, rendus)
    tous = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade)[0] for by, bx in sorted(candidats)]
    eo = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade, les_voisins_de=les_voisins_est_ouest)[0]
          for by, bx in sorted(candidats)]
    publie = {(b["la_rangee"], b["la_colonne"]): b for b in json.loads(CE_QUE_275_A_PUBLIE.read_text())["les_blocs"]}
    differents = sorted(f"{b['la_rangee']}_{b['la_colonne']}" for b in tous
                        if b.get("decidable") != publie[(b["la_rangee"], b["la_colonne"])].get("decidable")
                        or (b.get("decidable") and any(b[k] != publie[(b["la_rangee"], b["la_colonne"])][k]
                                                        for k in LES_COMPTES)))
    decides_eo = {(b["la_rangee"], b["la_colonne"]) for b in eo if b.get("decidable")}
    memes = [b for b in tous if (b["la_rangee"], b["la_colonne"]) in decides_eo]
    r_tous, r_eo, r_memes = la_reunion(tous), la_reunion(eo), la_reunion(memes)
    out = {"les_blocs_candidats": len(candidats), "les_blocs_qui_different_de_275": differents,
           "avec_tous_les_voisins": {"les_reunis": r_tous, "le_test": le_test(r_tous)},
           "avec_les_seuls_voisins_est_et_ouest": {"les_reunis": r_eo, "le_test": le_test(r_eo),
                                                   "les_non_decides": sum(1 for b in eo if not b.get("decidable"))},
           "les_memes_blocs_avec_tous_les_voisins": {"les_reunis": r_memes, "le_test": le_test(r_memes)}}
    out["decidable"] = not differents
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

    c = {(16, 16), (0, 16), (32, 16), (16, 0), (16, 32), (16, 48)}
    v("★★★★ les voisins est et ouest sont ceux de la même rangée de blocs, et eux seuls",
      sorted(les_voisins_est_ouest(16, 16, c)) == [(16, 0), (16, 32)], str(les_voisins_est_ouest(16, 16, c)))
    v("★★★ un bloc sans voisin sur sa rangée n'en a aucun", les_voisins_est_ouest(0, 16, c) == [])
    r = le_test({"les_blocs_qui_montent": 42, "les_blocs_qui_descendent": 11, "les_rates_rendus_justes": 163,
                 "les_justes_rendus_rates": 41})
    v("★★★★ le test est celui de 290, bloc par bloc et sur les points",
      r["sur_les_blocs"]["la_probabilite"] == 2.25e-05 and r["sur_les_blocs"]["sous_le_seuil"]
      and r["sur_les_points"]["le_gain_net"] == 122, str(r))
    r_ = lambda s: {"decidable": True, "avec_les_seuls_voisins_est_et_ouest": {"le_test": {"sur_les_blocs": {  # noqa: E731
        "sous_le_seuil": s}}}}
    v("★★★★ les issues : tient si les blocs passent sous le seuil, sinon non, indécidable sans contrôle",
      "ne tient plus" not in le_verdict(r_(True))["lissue"] and "ne tient plus" in le_verdict(r_(False))["lissue"]
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
