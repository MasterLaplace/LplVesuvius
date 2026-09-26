"""Sur le segment `20230702185753`, une ancre prise au seul nord et au seul sud garde-t-elle le gain que l'ancre est-ouest perd ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE CALCUL. Ce qui était vu avant d'écrire : tout ce que `257` à `292` publient. Sous la marche de
`275`, l'ancre prise à l'est et à l'ouest seulement fait tomber le gain net sur les points de 122 à 23 (`292`). Cette ancre a
deux défauts à la fois : elle est prise sur moitié moins de chunks, et sur les blocs que la marche traverse dans le sens où elle
intègre ses pas.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Une ancre prise au nord et au sud a autant de chunks que l'ancre est-ouest,
dans l'autre direction. Si elle garde le gain, c'est la direction est-ouest qui gâte l'ancre, et la bande, qui n'a que l'est et
l'ouest, demande une autre ancre que la médiane de ses voisins ; si elle le perd aussi, c'est le nombre de chunks.

## Ce qui est fait, déclaré avant le calcul

- La marche est celle de `275`, sur le bloc et tous ses voisins candidats ; l'ancre est la médiane de la différence des marches
  sur les seuls blocs voisins au nord et au sud, le bloc retiré. Un bloc sans voisin au nord ni au sud n'est pas décidé.
- Le reste est la décision de `264`, comme dans `275` et `292`.

⚠ Le contrôle rend la mesure décidable : avec l'ancre de `275`, le même calcul redonne `275` bloc par bloc.

## Les issues, exclusives, sur les points réunis

- le test du signe de `290` passe sous 0,05 sur les points : l'ancre nord-sud garde le gain, et c'est la direction est-ouest qui
  gâte l'ancre ;
- il n'y passe pas : l'ancre nord-sud le perd aussi, et c'est le nombre de chunks.

⚠ Rapporté à côté : les blocs ; l'ancre est-ouest de `292`, sur les mêmes blocs décidés.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une ancre pour la bande ; la raison pour laquelle une direction serait pire que l'autre.

Usage :
    uv run python src/nappe/lancre_nord_sud_garde_t_elle_le_gain_du_segment.py --verifier
    uv run python src/nappe/lancre_nord_sud_garde_t_elle_le_gain_du_segment.py \\
        --json docs/mesures/lancre_nord_sud_garde_t_elle_le_gain_du_segment.json
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
from lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment import lancre_est_ouest  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import lancre_du_voisinage  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_275_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


def lancre_nord_sud(diff: np.ndarray, y0: int, x0: int, by: int, bx: int, cote: int = LE_BLOC) -> float | None:
    """La médiane de la différence sur les seuls blocs au nord et au sud du bloc, dans le carré de la marche."""
    d = np.full(diff.shape, np.nan)
    c0 = bx - x0
    d[:, c0:c0 + cote] = diff[:, c0:c0 + cote]
    return lancre_du_voisinage(d, y0, x0, by, bx, cote)


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : le calcul avec l'ancre de 275 ne redonne pas 275"}
    if r["avec_lancre_nord_sud"]["le_test"]["sur_les_points"]["sous_le_seuil"]:
        return {"lissue": "l'ancre nord-sud garde le gain du segment : c'est la direction est-ouest qui gâte l'ancre"}
    return {"lissue": "l'ancre nord-sud perd aussi le gain du segment : c'est le nombre de chunks"}


def mesurer() -> dict:
    debut = time.monotonic()
    tau0, err, glissade, candidats = le_segment()
    rendus = les_rendus_sur_le_disque(candidats)
    tables = les_tables(candidats, rendus)
    faire = lambda lancre: [un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade, lancre=lancre)[0]  # noqa: E731
                            for by, bx in sorted(candidats)]
    tous, ns, eo = faire(lancre_du_voisinage), faire(lancre_nord_sud), faire(lancre_est_ouest)
    publie = {(b["la_rangee"], b["la_colonne"]): b for b in json.loads(CE_QUE_275_A_PUBLIE.read_text())["les_blocs"]}
    differents = sorted(f"{b['la_rangee']}_{b['la_colonne']}" for b in tous
                        if b.get("decidable") != publie[(b["la_rangee"], b["la_colonne"])].get("decidable")
                        or (b.get("decidable") and any(b[k] != publie[(b["la_rangee"], b["la_colonne"])][k]
                                                        for k in LES_COMPTES)))
    decides = {(b["la_rangee"], b["la_colonne"]) for b in ns if b.get("decidable")}
    garde = lambda blocs: [b for b in blocs if (b["la_rangee"], b["la_colonne"]) in decides]  # noqa: E731
    r_ns, r_eo, r_tous = la_reunion(ns), la_reunion(garde(eo)), la_reunion(garde(tous))
    out = {"les_blocs_candidats": len(candidats), "les_blocs_qui_different_de_275": differents,
           "avec_lancre_nord_sud": {"les_reunis": r_ns, "le_test": le_test(r_ns),
                                    "les_non_decides": sum(1 for b in ns if not b.get("decidable"))},
           "avec_lancre_est_ouest_sur_les_memes_blocs": {"les_reunis": r_eo, "le_test": le_test(r_eo)},
           "avec_lancre_de_275_sur_les_memes_blocs": {"les_reunis": r_tous, "le_test": le_test(r_tous)}}
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
    diff[:c, c:2 * c] = 10.0        # le nord
    diff[2 * c:, c:2 * c] = 30.0    # le sud
    diff[c:2 * c, :c] = 90.0        # l'ouest
    diff[c:2 * c, 2 * c:] = 90.0    # l'est
    diff[c:2 * c, c:2 * c] = 500.0  # le bloc
    v("★★★★ l'ancre nord-sud est la médiane du nord et du sud seuls, sans l'est, l'ouest ni le bloc",
      lancre_nord_sud(diff, 0, 0, c, c, c) == 20.0, str(lancre_nord_sud(diff, 0, 0, c, c, c)))
    v("★★★ elle lit autant de chunks que l'ancre est-ouest", int(np.isfinite(np.where(
        np.isfinite(diff), 0.0, np.nan)[:, c:2 * c]).sum()) - c * c == 2 * c * c)
    seul = np.full((3 * c, 3 * c), np.nan)
    seul[c:2 * c, :c] = 1.0
    seul[c:2 * c, c:2 * c] = 5.0
    v("★★★ sans voisin au nord ni au sud, pas d'ancre", lancre_nord_sud(seul, 0, 0, c, c, c) is None)
    r_ = lambda s: {"decidable": True, "avec_lancre_nord_sud": {"le_test": {"sur_les_points": {"sous_le_seuil": s}}}}  # noqa: E731
    v("★★★★ les issues : la direction si le nord-sud garde le gain, sinon le nombre de chunks",
      "direction" in le_verdict(r_(True))["lissue"] and "nombre de chunks" in le_verdict(r_(False))["lissue"]
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
