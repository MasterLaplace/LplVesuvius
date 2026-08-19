#!/usr/bin/env python3
"""Agréger la campagne appariée des deux critères de graine.

⚠⚠ **Conception appariée** : chaque rouleau est tracé deux fois, une graine par critère,
tout le reste identique. Un rouleau est donc son propre témoin, et la différence ne peut
pas être mise sur le dos de « celui-là est plus facile ». C'est aussi pourquoi la
statistique lue ici est un **test des signes sur les paires**, pas une comparaison de deux
moyennes : deux moyennes mélangeraient la difficulté des rouleaux à l'effet du critère.

⚠ **L'aire sature contre le budget de générations.** Deux traces qui vont au bout des 120
générations rendent la même aire à huit millièmes de pour-cent près, sur des rouleaux
différents — parce qu'une surface croît par un front et que son aire est alors fixée par le
nombre de pas. L'aire n'est donc lue ici que comme **proxy de « jusqu'où le traceur est
allé »**, et la grandeur qui décide reste **le nombre d'auto-intersections**, qui, lui, ne
dépend d'aucun budget.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CRITERES = ("planarite", "voisinage")


def lire(dossier: Path) -> list[dict]:
    lignes = []
    for p in sorted(dossier.glob("PHerc*.json")):
        if p.name.count(".") > 1:          # PHerc0358.planarite.json etc.
            continue
        d = json.loads(p.read_text())
        essais = {e["critere"]: e for e in d.get("essais", [])}
        if not all(c in essais for c in CRITERES):
            continue
        lignes.append({"rouleau": d["rouleau"], "voxel_um": d["voxel_um"],
                       **{c: essais[c] for c in CRITERES}})
    return lignes


def signes(lignes: list[dict], cle: str, sens: int) -> dict:
    """Test des signes sur les paires. `sens` = +1 si « plus grand est meilleur ».

    ⚠ Les ex æquo sont **écartés et comptés**, jamais attribués à l'un des deux camps :
    les compter pour le critère qu'on défend est exactement la façon dont un test des
    signes ment.
    """
    pour = contre = nul = 0
    for l in lignes:
        a, b = l["planarite"].get(cle), l["voisinage"].get(cle)
        if a is None or b is None:
            nul += 1
            continue
        d = (a - b) * sens
        if d > 0:
            pour += 1
        elif d < 0:
            contre += 1
        else:
            nul += 1
    n = pour + contre
    # p bilatéral exact du test des signes, sans scipy : somme binomiale à p = 1/2.
    from math import comb
    if n:
        k = min(pour, contre)
        p = min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / (2 ** n))
    else:
        p = 1.0
    return {"pour_planarite": pour, "pour_voisinage": contre, "ex_aequo": nul,
            "n_paires": n, "p_signes": p}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Table de la campagne appariee des criteres de graine.")
    parser.add_argument("dossier", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    lignes = lire(args.dossier)
    if not lignes:
        print(f"aucun rouleau complet dans {args.dossier}", file=sys.stderr)
        return 1

    print(f"{'rouleau':<12} {'planarite':>22}   {'voisinage':>22}")
    print(f"{'':<12} {'aire cm²':>10} {'croisements':>11}   "
          f"{'aire cm²':>10} {'croisements':>11}")
    for l in lignes:
        a, b = l["planarite"], l["voisinage"]
        print(f"{l['rouleau']:<12} {a.get('aire_cm2', 0) or 0:>10.2f} "
              f"{a.get('transverse', -1):>11}   "
              f"{b.get('aire_cm2', 0) or 0:>10.2f} {b.get('transverse', -1):>11}")

    aire = signes(lignes, "aire_cm2", +1)
    crois = signes(lignes, "transverse", -1)
    print(f"\naire       — planarite {aire['pour_planarite']} / voisinage "
          f"{aire['pour_voisinage']} / ex aequo {aire['ex_aequo']}  "
          f"(test des signes p = {aire['p_signes']:.4f})")
    print(f"croisements — planarite {crois['pour_planarite']} / voisinage "
          f"{crois['pour_voisinage']} / ex aequo {crois['ex_aequo']}  "
          f"(test des signes p = {crois['p_signes']:.4f})")

    tot_p = sum(l["planarite"].get("transverse") or 0 for l in lignes)
    tot_v = sum(l["voisinage"].get("transverse") or 0 for l in lignes)
    plafond = sum(1 for l in lignes if (l["planarite"].get("aire_cm2") or 0) > 19.8)
    print(f"\nauto-intersections cumulees : planarite {tot_p}   voisinage {tot_v}")
    print(f"traces qui atteignent le plafond de generations (aire > 19,8 cm²) : "
          f"{plafond} / {len(lignes)} en planarite")
    print("⚠ l'aire sature contre le budget de generations — voir l'en-tete de ce fichier")

    if args.out:
        args.out.write_text(json.dumps(
            {"rouleaux": len(lignes), "lignes": lignes, "signes_aire": aire,
             "signes_croisements": crois,
             "croisements_cumules": {"planarite": tot_p, "voisinage": tot_v}},
            indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
