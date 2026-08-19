#!/usr/bin/env python3
"""Depouiller les repetitions de trace a parametres identiques.

⚠ Pourquoi cette mesure existe. `24` a condamne une trace sur 240 auto-intersections. En
rejouant LA MEME graine avec LES MEMES parametres, on obtient zero. Le maillage archive,
lui, remesure bien 240 aujourd'hui : la mesure est fidele, c'est la TRACE qui change d'un
tirage a l'autre.

⚠⚠ Une seule execution n'est donc PAS une mesure de qualite de trace -- ni chez nous, ni
dans la litterature, ou les tableaux d'ablation donnent une ligne par configuration sans
barre d'erreur ni repetition (`27` §2).

Ce script rend la distribution : combien de tirages, combien propres, quelle etendue
d'aire, et l'ecart au maillage de reference s'il est fourni.

Usage :
    python3 analysis/src/table_thread_limit.py [data/trace/PHerc0358/thread_limit] \\
        [--reference artefacts/PHerc0358/mesh.tifxyz/meta.json] [--json sortie.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?",
                    default=str(RACINE / "data/trace/PHerc0358/thread_limit"))
    ap.add_argument("--reference", default=str(RACINE / "artefacts/PHerc0358/mesh.tifxyz/meta.json"))
    ap.add_argument("--reference-croisements", type=int, default=240)
    ap.add_argument("--json")
    a = ap.parse_args()

    lots = []
    for f in sorted(Path(a.dossier).glob("*/resume.json")):
        r = json.loads(f.read_text())
        if r.get("statut") == "ok":
            lots.append(r)
    if not lots:
        print("aucun tirage exploitable")
        return 1

    ref_aire = None
    p = Path(a.reference)
    if p.is_file():
        ref_aire = json.loads(p.read_text()).get("area_cm2")

    print(f"{len(lots)} tirages à paramètres identiques\n")
    print(f"  {'thread_limit':>12} {'essai':>6} {'gen':>5} {'aire cm²':>10} {'croisements':>12}")
    for r in sorted(lots, key=lambda x: (x["thread_limit"], x["repetition"])):
        print(f"  {r['thread_limit']:>12} {r['repetition']:>6} {r['generations']:>5} "
              f"{r['aire_cm2']:>10.6f} {r['transverse']:>12}")

    aires = [r["aire_cm2"] for r in lots]
    propres = [r for r in lots if r["transverse"] == 0]
    print(f"\n  propres (0 croisement) : {len(propres)}/{len(lots)}")
    print(f"  aire : {min(aires):.4f} à {max(aires):.4f} cm², "
          f"médiane {statistics.median(aires):.4f}, "
          f"étendue relative {(max(aires)-min(aires))/statistics.mean(aires):.1%}")

    if ref_aire is not None:
        # ⚠ Le controle qui rend le resultat lisible : trouver le tirage dont l'AIRE est la
        # plus proche du maillage de reference. S'il est propre alors que la reference ne
        # l'est pas, la difference n'est ni dans les parametres ni dans l'etendue.
        proche = min(lots, key=lambda r: abs(r["aire_cm2"] - ref_aire))
        ecart = abs(proche["aire_cm2"] - ref_aire) / ref_aire
        print(f"\n  référence : {ref_aire:.6f} cm², {a.reference_croisements} croisements")
        print(f"  tirage le plus proche en aire : {proche['aire_cm2']:.6f} cm² "
              f"({ecart:.2%} d'écart), {proche['transverse']} croisement(s)")
        if proche["transverse"] == 0 and a.reference_croisements > 0:
            print("\n  ⚠⚠ Deux maillages de MÊME aire à un centième de pour cent près,")
            print("     mêmes paramètres, même graine — et deux verdicts opposés.")
            print("     La différence n'est donc ni dans les paramètres, ni dans l'étendue.")

    if a.json:
        Path(a.json).write_text(json.dumps(
            {"tirages": lots, "propres": len(propres), "total": len(lots),
             "aire_min": min(aires), "aire_max": max(aires),
             "reference_aire": ref_aire,
             "reference_croisements": a.reference_croisements},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
