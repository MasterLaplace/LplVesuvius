#!/usr/bin/env python3
"""Ce que coûte une carte d'encre, et ce que coûterait un rouleau.

⚠⚠ Pourquoi ce fichier existe. `src/volume/cout_passage_echelle.py` chiffre le coût de
**lire** un rouleau — des octets et des secondes de téléchargement. Personne n'avait chiffré
le coût d'en **rendre l'encre**, alors que c'est l'étape qui décide si l'approche tient à
treize rouleaux. Mesuré le 2026-08-27, après une journée où deux rendus se sont disputé la
machine et où l'auteur a demandé, à juste titre, si quelque chose tournait encore.

⭐ Le chiffre qui compte n'est pas la vitesse mais le **débit par fil-seconde** : c'est lui
qui se transporte d'une machine à l'autre, là où « 94 ms par fenêtre » ne vaut que pour le
nombre de cœurs du jour.

⚠⚠ Et la mesure a un second usage, moins attendu : elle chiffre la **contention**. Deux
rendus lancés ensemble sur vingt-deux cœurs ont demandé trente-deux fils, et le débit par
fil-seconde a été divisé par cinq. Deux rendus simultanés finissent plus tard que les mêmes
lancés l'un après l'autre, et ce fichier dit de combien.

Usage :
    uv run python src/encre/cout_du_rendu.py --json docs/mesures/cout_du_rendu.json
    uv run python src/encre/cout_du_rendu.py --verifier
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

OBSERVATIONS = [
    # (ce que c'est, fenêtres, secondes, fils, machine partagée ?)
    ("Scroll 1, 1024 px, machine libre", 2116, 199.7, 16, False),
    ("PHerc1447, 1024 px, machine libre", 2116, 198.1, 16, False),
    ("PHerc1447, surface entière, machine libre", 21128, 2079.5, 16, False),
    ("PHerc0172, 1024 px, machine partagée", 2116, 509.3, 16, True),
    ("témoin négatif, 1100 px pas 8, machine partagée", 1488, 2006.0, 6, True),
]
"""Les rendus chronométrés de la journée, chacun avec sa ligne de log pour origine.

⚠ Le dernier n'est PAS fini : ce sont ses fenêtres au moment de la lecture, ce que la
progression imprime désormais. Un débit se mesure sur une portion aussi bien que sur un tout,
et attendre la fin pour connaître le débit était précisément le problème.
"""

FENETRES_PAR_MM2 = 21128 / (2980 * 3240 * (8.64e-3) ** 2)
"""Fenêtres par millimètre carré de papyrus, au pas de balayage 21 et à 8,64 µm.

⚠ Le pas ET la taille de voxel entrent tous deux dedans : à pas égal, un scan deux fois plus
fin demande quatre fois plus de fenêtres pour la même surface de papyrus. Extrapoler sans
les nommer ferait un chiffre qui ne vaut que pour le rouleau où il a été pris.
"""


def debit(fenetres: int, secondes: float, fils: int) -> float:
    """Fenêtres par fil-seconde — la grandeur qui se transporte d'une machine à l'autre."""
    return fenetres / (secondes * fils) if secondes > 0 and fils > 0 else 0.0


def resume(observations=OBSERVATIONS) -> dict:
    """Le débit des machines libres, celui des machines partagées, et leur rapport."""
    libres = [o for o in observations if not o[4]]
    partagees = [o for o in observations if o[4]]

    def moyen(lot):
        if not lot:
            return None
        return sum(debit(f, s, t) for _, f, s, t, _ in lot) / len(lot)

    d_libre, d_partage = moyen(libres), moyen(partagees)
    return {
        "lignes": [{"quoi": q, "fenetres": f, "secondes": s, "fils": t, "partagee": p,
                    "debit_fenetres_par_fil_seconde": round(debit(f, s, t), 4)}
                   for q, f, s, t, p in observations],
        "debit_machine_libre": round(d_libre, 4) if d_libre else None,
        "debit_machine_partagee": round(d_partage, 4) if d_partage else None,
        "facteur_de_contention": (round(d_libre / d_partage, 2)
                                  if d_libre and d_partage else None),
        "fenetres_par_mm2": round(FENETRES_PAR_MM2, 3),
    }


def heures_pour(mm2: float, fils: int, partagee: bool, r=None) -> float:
    """Heures pour rendre `mm2` de papyrus, au débit mesuré."""
    r = r or resume()
    d = r["debit_machine_partagee"] if partagee else r["debit_machine_libre"]
    if not d or not fils:
        return float("inf")
    return mm2 * r["fenetres_par_mm2"] / (d * fils) / 3600.0


def verifier() -> int:
    """Auto-test HORS LIGNE."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    v("le débit est par fil-seconde, donc il divise par les deux",
      abs(debit(100, 10.0, 5) - 2.0) < 1e-9)
    v("un temps nul ne divise pas par zéro", debit(100, 0.0, 5) == 0.0)
    v("zéro fil non plus", debit(100, 10.0, 0) == 0.0)

    r = resume()
    v("une machine libre rend plus qu'une machine partagée",
      r["debit_machine_libre"] > r["debit_machine_partagee"])
    # ⚠⚠ Le facteur de contention est le résultat, pas une décoration : il dit que lancer
    # deux rendus ensemble coûte plus cher que les lancer l'un après l'autre.
    v("... et le facteur de contention le chiffre", r["facteur_de_contention"] > 2.0)

    # ⚠ Une extrapolation doit être linéaire en surface : doubler la surface double le coût.
    a = heures_pour(100.0, 16, False)
    b = heures_pour(200.0, 16, False)
    v("le coût est linéaire en surface de papyrus", abs(b - 2 * a) < 1e-9)
    v("... et inversement proportionnel au nombre de fils",
      abs(heures_pour(100.0, 32, False) - a / 2) < 1e-9)
    v("une machine partagée coûte plus d'heures",
      heures_pour(100.0, 16, True) > heures_pour(100.0, 16, False))

    # ⚠⚠ Le contrôle qui rattache le chiffre à une mesure réelle : la surface entière de
    # PHerc1447 doit retomber sur sa durée observée, à 10 % près.
    mm2 = 2980 * 3240 * (8.64e-3) ** 2
    attendu = heures_pour(mm2, 16, False)
    observe = 2079.5 / 3600.0
    v("la surface entière retombe sur sa durée mesurée",
      abs(attendu - observe) / observe < 0.10)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--fils", type=int, default=16)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    r = resume()
    for l in r["lignes"]:
        marque = "partagée" if l["partagee"] else "libre   "
        print(f"  {l['quoi']:48} {marque}  {l['debit_fenetres_par_fil_seconde']:.3f} f/fil·s")
    print(f"\n  débit machine libre    : {r['debit_machine_libre']:.3f} fenêtres par fil-seconde")
    print(f"  débit machine partagée : {r['debit_machine_partagee']:.3f}")
    print(f"  ⚠ facteur de contention : ×{r['facteur_de_contention']}")

    # ⚠ Les surfaces sont celles qu'on a réellement vues, pas des rouleaux entiers : un
    # rouleau entier n'a pas de surface tracée, c'est tout l'objet du prix.
    print("\n  à ce débit, sur une machine libre et 16 fils :")
    for quoi, mm2 in (("une surface publiée de PHerc1447 (719 mm²)",
                       2980 * 3240 * (8.64e-3) ** 2),
                      ("les quatre surfaces publiées de PHerc1447", 4 * 2980 * 3240 * (8.64e-3) ** 2),
                      ("un décimètre carré de papyrus", 10000.0)):
        print(f"    {quoi:48} {heures_pour(mm2, a.fils, False, r):6.2f} h")

    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
