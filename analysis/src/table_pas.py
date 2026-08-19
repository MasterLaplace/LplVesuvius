#!/usr/bin/env python3
"""Depouiller le balayage de `step_size` (tools/campagne_pas.sh).

⚠ Pourquoi la comparaison n'est pas triviale. Une surface croit par un FRONT, donc son
aire va comme (k x pas)^2 : a nombre de generations egal, un pas de 5 couvre seize fois
moins qu'un pas de 20. Comparer les comptes bruts ferait passer la LENTEUR pour de la
QUALITE -- un petit morceau a moins d'occasions de se replier sur lui-meme. La campagne
met donc le nombre de generations a l'echelle en 1/pas, et ce script verifie que les
aires obtenues sont effectivement comparables AVANT de comparer quoi que ce soit d'autre.

⚠ Un pas dont le run a ete tue ou n'a rien produit n'est PAS une mesure : il est rapporte
a part, jamais agrege. C'est le correctif du 2026-08-19 -- un run tue enregistrait
`aire=0, transverse=0`, soit exactement le resultat espere.

Usage :
    python3 analysis/src/table_pas.py [data/trace/PHerc0358/pas] [--json sortie.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def lire(dossier: Path) -> list[dict]:
    lots = []
    for d in sorted(dossier.glob("pas_*"), key=lambda p: int(p.name.split("_")[1])):
        f = d / "resume.json"
        if not f.is_file():
            lots.append({"pas": int(d.name.split("_")[1]), "statut": "en_cours"})
            continue
        r = json.loads(f.read_text())
        # ⚠ Les resumes ecrits avant le correctif n'ont pas de champ `statut`. On ne les
        # promeut PAS en "ok" par defaut : on dit qu'ils sont d'un format anterieur, et
        # on les traite comme mesures seulement s'ils portent une aire non nulle.
        if "statut" not in r:
            r["statut"] = "ok_format_anterieur" if r.get("aire_cm2") else "indetermine"
        lots.append(r)
    return lots


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?",
                    default=str(RACINE / "data/trace/PHerc0358/pas"))
    ap.add_argument("--json")
    a = ap.parse_args()

    lots = lire(Path(a.dossier))
    mesures = [l for l in lots if str(l.get("statut", "")).startswith("ok")]
    autres = [l for l in lots if l not in mesures]

    print(f"balayage de step_size — {len(mesures)} mesure(s), {len(autres)} non mesure(s)\n")
    print(f"  {'pas':>4}  {'gen':>5}  {'aire cm²':>9}  {'transverse':>10}  {'par cm²':>8}")
    for l in mesures:
        a_, c = l.get("aire_cm2"), l.get("transverse")
        print(f"  {l['pas']:>4}  {l.get('generations', 0):>5}  {a_:>9.3f}  {c:>10}  "
              f"{(c / a_ if a_ else float('nan')):>8.2f}")
    for l in autres:
        print(f"  {l['pas']:>4}  {'—':>5}  {'—':>9}  {'—':>10}  {'—':>8}   "
              f"⚠ {l.get('statut')}")

    if not mesures:
        print("\n⚠ aucune mesure exploitable")
        return 1

    aires = [l["aire_cm2"] for l in mesures]
    etendue = (max(aires) - min(aires)) / (sum(aires) / len(aires))
    zeros = [l["pas"] for l in mesures if l["transverse"] == 0]
    non_zeros = [(l["pas"], l["transverse"]) for l in mesures if l["transverse"]]

    print(f"\n  aires : {min(aires):.2f} à {max(aires):.2f} cm², "
          f"étendue relative {etendue:.1%}")
    # ⚠ Sans cette verification, toute la comparaison est nulle : c'est elle qui dit que
    # la mise a l'echelle des generations a fait son travail.
    if etendue > 0.15:
        print("  ⚠⚠ les aires ne sont PAS comparables — la mise à l'échelle a échoué,")
        print("     et un compte brut mesurerait la taille, pas la qualité")
    else:
        print("  ✅ aires comparables : le compte brut mesure bien la qualité")

    print(f"\n  pas à ZÉRO auto-intersection : {zeros}")
    if non_zeros:
        print(f"  pas non nuls : {non_zeros}")
        print("\n  ⚠ le résultat n'est PAS monotone : un seul pas s'écarte, encadré de")
        print("    pas plus petits ET plus grands qui rendent zéro. Un point isolé sur")
        print("    une graine et un rouleau ne fait pas une tendance — à répliquer avant")
        print("    d'en tirer quoi que ce soit.")
    else:
        print("\n  aucun pas ne produit d'auto-intersection sur cette graine")

    if a.json:
        Path(a.json).write_text(json.dumps(
            {"mesures": mesures, "non_mesures": autres,
             "etendue_relative_aires": etendue,
             "pas_a_zero": zeros, "pas_non_nuls": non_zeros},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
