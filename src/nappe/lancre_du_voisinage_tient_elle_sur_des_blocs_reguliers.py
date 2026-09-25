"""L'ancre prise chez les voisins, avec la décision de 264, défait-elle les blocs pris à pas réguliers ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL VOISIN D'UN BLOC RÉGULIER NE SOIT RENDU. Ce qui était vu avant d'écrire : tout ce que
`257` à `269` publient, dont `265` sur les deux blocs choisis, 35 ratés rendus justes pour 1 juste rendu raté, et `264` sur les
blocs réguliers avec l'ancre du bloc, 4 ratés rendus justes et aucun juste abîmé.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. De tout ce qui a été essayé, une procédure corrige les deux blocs choisis
sans rien abîmer autour : la décision de `264`, avec l'ancre prise chez les voisins de `265`. La leçon de `263` est qu'une
procédure qui corrige là où on l'a regardée travailler peut défaire là où on ne l'a pas regardée. Elle n'a jamais été
essayée sur les blocs réguliers : l'ancre y bouge, et avec elle ce que le mélange appelle glissé.

## La procédure, celle de `265`, sans rien y changer

Pour chacun des blocs de `263` que le juge note, ses voisins au nord, au sud, à l'ouest et à l'est, gardés s'ils sont candidats
de `257`, rendus ; la marche d'un seul tenant sur le bloc et eux ; l'ancre, la médiane sur les voisins seuls ; la décision de
`264` ; une passe. `(80, 32)`, où le juge ne note rien, n'est pas rendu : rien ne s'y jugerait.

## Les issues, exclusives, sur la part réunie des blocs réguliers notés

- elle ne baisse pas : la procédure ne défait pas les blocs réguliers ;
- elle baisse : la procédure défait les blocs réguliers.

⚠ Rapporté à côté : chaque bloc, les ratés rendus justes et les justes rendus ratés, et la même décision avec l'ancre du bloc,
sur la même marche.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, d'autres blocs, une seconde passe.

Usage :
    uv run python src/nappe/lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.py --verifier
    uv run python src/nappe/lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.py \\
        --json docs/mesures/lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_correction_tient_elle_sur_des_blocs_reguliers import la_part_reunie  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LE_DOSSIER, LES_JUGES, le_cadre, les_blocs_candidats,
                                                            lerreur_jugee, rendre)
from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, LE_SEGMENT, lire_tifxyz, telecharger  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import LES_SURFACES, les_voisins, un_voisinage  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_263_A_PUBLIE = LES_MESURES / "la_correction_tient_elle_sur_des_blocs_reguliers.json"


def les_rendus_a_faire(blocs: list[tuple[int, int]], candidats: set) -> list[tuple[str, int, int]]:
    """Chaque surface de chaque bloc et de ses voisins, une seule fois, dans l'ordre."""
    tous = sorted({v for b in blocs for v in [b] + les_voisins(b[0], b[1], candidats)})
    return [(s, vy, vx) for s in LES_SURFACES for vy, vx in tous]


def les_reunions(blocs: dict) -> dict:
    """La part réunie avant et après, pour chaque ancre, et ce qui a été rendu juste ou raté."""
    ok = {n: b for n, b in blocs.items() if b.get("decidable") and b["avant"]["la_part_sur_la_bonne_spire"] is not None}
    out = {"les_blocs": len(ok), "avant": la_part_reunie({n: {"avant": b["avant"]} for n, b in ok.items()}, "avant")}
    for ancre in ("lancre_du_voisinage", "lancre_du_bloc"):
        dec = {n: b[ancre]["la_decision"] for n, b in ok.items()}
        out[ancre] = {"apres": la_part_reunie(dec, "apres"),
                      "les_points_corriges": sum(x["les_points_corriges"] for x in dec.values()),
                      "les_rates_rendus_justes": sum(x["les_rates_rendus_justes"] for x in dec.values()),
                      "les_justes_rendus_rates": sum(x["les_justes_rendus_rates"] for x in dec.values())}
    return out


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    d261 = json.loads(CE_QUE_261_A_PUBLIE.read_text())
    d263 = json.loads(CE_QUE_263_A_PUBLIE.read_text())
    glissade = float(d261["le_signe"]["lecart_retrouve_voxels"])
    gy, gx = d257["le_treillis"]
    _, valide, _ = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    candidats = set(les_blocs_candidats(tau0, valide, gy, gx))
    notes = [(n, b["la_rangee"], b["la_colonne"]) for n, b in d263["les_blocs"].items()
             if b["avant"]["la_part_sur_la_bonne_spire"] is not None]
    a_faire = les_rendus_a_faire([(by, bx) for _, by, bx in notes], candidats)
    with ThreadPoolExecutor(max_workers=2) as pool:
        rendus = list(pool.map(lambda t: rendre(LE_DOSSIER / t[0] / "maillage", LE_DOSSIER / t[0] / f"bloc_{t[1]}_{t[2]}",
                                                le_cadre(t[1], t[2], LE_BLOC)), a_faire))
    out = {"la_glissade_voxels": glissade, "les_rendus": len(a_faire),
           "les_rendus_refaits": sum(1 for x in rendus if not x.get("reprise")),
           "les_rendus_rates": [list(t) for t, x in zip(a_faire, rendus) if not x["rendue"]], "les_blocs": {}}
    for n, by, bx in notes:
        r = un_voisinage(n, by, bx, candidats, tau0, err, glissade)
        out["les_blocs"][n] = r
    out["les_reunis"] = les_reunions(out["les_blocs"])
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(b.get("decidable") for b in out["les_blocs"].values())
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable"}
    g = r["les_reunis"]
    if g["lancre_du_voisinage"]["apres"] >= g["avant"]:
        return {"lissue": "elle ne baisse pas : la procédure ne défait pas les blocs réguliers"}
    return {"lissue": "elle baisse : la procédure défait les blocs réguliers"}


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

    cand = {(16, 16), (0, 16), (32, 16), (16, 0), (16, 32), (32, 32), (48, 32)}
    faire = les_rendus_a_faire([(16, 16), (32, 32)], cand)
    v("★★★★ chaque surface de chaque bloc et de ses voisins n'est rendue qu'une fois",
      lambda: len(faire) == len(set(faire)) and ("le_segment_reduit", 32, 16) in faire
      and sum(1 for f in faire if f[1:] == (32, 16)) == 2 and len(faire) == 2 * 7, str(faire))

    def bloc(av, ap, rj, jr, ok=True):
        dec = {"apres": {"les_points_notes": 100, "la_part_sur_la_bonne_spire": ap}, "les_points_corriges": rj + jr,
               "les_rates_rendus_justes": rj, "les_justes_rendus_rates": jr}
        return {"decidable": ok, "avant": {"les_points_notes": 100, "la_part_sur_la_bonne_spire": av},
                "lancre_du_voisinage": {"la_decision": dec}, "lancre_du_bloc": {"la_decision": dec}}
    g = les_reunions({"a": bloc(0.9, 0.92, 2, 0), "b": bloc(0.8, 0.8, 0, 0), "c": bloc(0.5, 0.1, 0, 0, ok=False)})
    v("★★★★ la réunion pèse les blocs par leurs points et laisse de côté un bloc indécidable",
      lambda: g["les_blocs"] == 2 and g["avant"] == 0.85 and g["lancre_du_voisinage"]["apres"] == 0.86
      and g["lancre_du_voisinage"]["les_rates_rendus_justes"] == 2, str(g))
    v("★★★★ les issues : ne défait pas, défait",
      lambda: "ne défait pas" in le_verdict({"decidable": True, "les_reunis": g})["lissue"]
      and "défait les blocs" in le_verdict({"decidable": True, "les_reunis": les_reunions(
          {"a": bloc(0.9, 0.85, 0, 5)})})["lissue"]
      and "ne défait pas" not in le_verdict({"decidable": True, "les_reunis": les_reunions(
          {"a": bloc(0.9, 0.85, 0, 5)})})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps({"les_reunis": r.get("les_reunis"), "le_verdict": r["le_verdict"]}, indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
