"""Sur le segment `20230702185753`, est-ce l'ancre prise à l'est et à l'ouest qui fait perdre son gain à la procédure ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE CALCUL. Ce qui était vu avant d'écrire : tout ce que `257` à `291` publient. Avec ses seuls
voisins est et ouest, la procédure du segment corrige 1047 points au lieu de 495, et son gain net sur les points tombe de 122 à 5
(`291`). Deux choses changent alors ensemble : la marche, qui ne s'étend plus que sur une rangée de trois blocs, et l'ancre, prise
sur les deux voisins seulement.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Sur la bande, les blocs n'ont que l'est et l'ouest : si c'est l'ancre qui fait
perdre le gain, une ancre prise plus loin sur la même rangée peut s'y substituer sans rien rendre de neuf ; si c'est la marche,
il faut une tranche plus haute. On ne peut pas prendre une ancre au nord et au sud sans que la marche y passe ; on peut en
revanche garder la marche de `275`, sur les quatre voisins, et ne prendre l'ancre qu'à l'est et à l'ouest.

## Ce qui est fait, déclaré avant le calcul

- Les tables de pas et les piles sont celles de `275`, sans rien rendre.
- Pour chaque bloc : la marche de `275`, sur le bloc et tous ses voisins candidats ; l'ancre, la médiane de la différence des
  marches sur les seuls blocs voisins à l'est et à l'ouest, le bloc lui-même retiré. Un bloc sans voisin à l'est ni à l'ouest
  n'est pas décidé.
- Le reste est la décision de `264`, comme dans `275`.

⚠ Le contrôle rend la mesure décidable : avec l'ancre de `275`, le même calcul redonne `275` bloc par bloc.

## Les issues, exclusives, sur les points réunis

- le test du signe de `290` passe sous 0,05 sur les points : avec la marche de `275`, l'ancre est-ouest garde le gain, et c'est
  la marche qui le fait perdre dans `291` ;
- il n'y passe pas : l'ancre est-ouest suffit à faire perdre le gain.

⚠ Le test porte ici sur les points, et non sur les blocs : `291` a montré que le sens dans lequel les blocs bougent tient avec
les seuls voisins est et ouest, et que c'est le gain sur les points qui s'effondre. Les blocs sont rapportés à côté.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une ancre plus lointaine sur la même rangée ; la bande.

Usage :
    uv run python src/nappe/lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment.py --verifier
    uv run python src/nappe/lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment.py \\
        --json docs/mesures/lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment.json
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

from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (la_reunion, le_segment,  # noqa: E402
                                                                     les_rendus_sur_le_disque, les_tables, un_bloc)
from la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest import le_test  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import LE_BLOC  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import lancre_du_voisinage  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_275_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"
CE_QUE_291_A_PUBLIE = LES_MESURES / "la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest.json"
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


def lancre_est_ouest(diff: np.ndarray, y0: int, x0: int, by: int, bx: int, cote: int = LE_BLOC) -> float | None:
    """La médiane de la différence sur les seuls blocs à l'est et à l'ouest du bloc, dans le carré de la marche."""
    d = np.full(diff.shape, np.nan)
    r0 = by - y0
    d[r0:r0 + cote] = diff[r0:r0 + cote]
    return lancre_du_voisinage(d, y0, x0, by, bx, cote)


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : le calcul avec l'ancre de 275 ne redonne pas 275"}
    if r["avec_lancre_est_ouest"]["le_test"]["sur_les_points"]["sous_le_seuil"]:
        return {"lissue": "avec la marche de 275, l'ancre est-ouest garde le gain du segment"}
    return {"lissue": "l'ancre est-ouest suffit à faire perdre son gain à la procédure du segment"}


def mesurer() -> dict:
    debut = time.monotonic()
    tau0, err, glissade, candidats = le_segment()
    rendus = les_rendus_sur_le_disque(candidats)
    tables = les_tables(candidats, rendus)
    tous = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade)[0] for by, bx in sorted(candidats)]
    eo = [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade, lancre=lancre_est_ouest)[0]
          for by, bx in sorted(candidats)]
    publie = {(b["la_rangee"], b["la_colonne"]): b for b in json.loads(CE_QUE_275_A_PUBLIE.read_text())["les_blocs"]}
    differents = sorted(f"{b['la_rangee']}_{b['la_colonne']}" for b in tous
                        if b.get("decidable") != publie[(b["la_rangee"], b["la_colonne"])].get("decidable")
                        or (b.get("decidable") and any(b[k] != publie[(b["la_rangee"], b["la_colonne"])][k]
                                                        for k in LES_COMPTES)))
    r_tous, r_eo = la_reunion(tous), la_reunion(eo)
    d291 = json.loads(CE_QUE_291_A_PUBLIE.read_text())["avec_les_seuls_voisins_est_et_ouest"]
    out = {"les_blocs_candidats": len(candidats), "les_blocs_qui_different_de_275": differents,
           "avec_lancre_de_275": {"les_reunis": r_tous, "le_test": le_test(r_tous)},
           "avec_lancre_est_ouest": {"les_reunis": r_eo, "le_test": le_test(r_eo),
                                     "les_non_decides": sum(1 for b in eo if not b.get("decidable"))},
           "la_marche_et_lancre_est_ouest_de_291": {"les_reunis": d291["les_reunis"], "le_test": d291["le_test"]}}
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

    c = 2
    diff = np.zeros((3 * c, 3 * c))
    diff[:c] = 90.0           # le nord
    diff[2 * c:] = 90.0       # le sud
    diff[c:2 * c, :c] = 10.0  # l'ouest
    diff[c:2 * c, 2 * c:] = 30.0  # l'est
    diff[c:2 * c, c:2 * c] = 500.0  # le bloc
    v("★★★★ l'ancre est-ouest est la médiane de l'ouest et de l'est seuls, sans le nord, le sud ni le bloc",
      lancre_est_ouest(diff, 0, 0, c, c, c) == 20.0, str(lancre_est_ouest(diff, 0, 0, c, c, c)))
    v("★★★ l'ancre de 275 lit aussi le nord et le sud", lancre_du_voisinage(diff, 0, 0, c, c, c) == 90.0)
    seul = np.full((3 * c, 3 * c), np.nan)
    seul[:c] = 1.0
    seul[c:2 * c, c:2 * c] = 5.0
    v("★★★ sans voisin à l'est ni à l'ouest, pas d'ancre", lancre_est_ouest(seul, 0, 0, c, c, c) is None)
    r_ = lambda s: {"decidable": True, "avec_lancre_est_ouest": {"le_test": {"sur_les_points": {"sous_le_seuil": s}}}}  # noqa: E731
    v("★★★★ les issues : l'ancre garde le gain si les points passent sous le seuil, sinon elle suffit à le perdre",
      "garde le gain" in le_verdict(r_(True))["lissue"] and "suffit" in le_verdict(r_(False))["lissue"]
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
