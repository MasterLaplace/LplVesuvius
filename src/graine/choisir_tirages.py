#!/usr/bin/env python3
"""Quels tirages valent le second axe ? -- parce qu'un rendu coute dix minutes.

⚠⚠ Pourquoi ce fichier existe. Produire le second axe (`31` §4 : selectionner sur un axe,
valider sur l'autre) demande `vc_flatten` + `vc_render_tifxyz` par tirage, soit ~10 min
mesurees. Les 72 tirages de `35` feraient 12 heures, et la plupart n'apprendraient rien :
sur huit rouleaux les six tirages s'accordent deja sur l'axe geometrique.

⭐ **La comparaison qui tranche est INTRA-rouleau.** Sur un rouleau qui bascule, on tient
le mauvais tirage ET des tirages propres, meme graine, memes parametres. Si le mauvais
selon l'axe 1 est aussi le pire selon l'axe 2, les deux axes s'accordent et la selection
marche. Sinon ils sont independants -- et c'est la malediction du vainqueur, rendue
concrete plutot qu'annoncee.

⚠ Des rouleaux TEMOINS sont inclus, ou aucun tirage ne bascule. Sans eux, une difference
d'axe 2 entre « le mauvais » et « les propres » ne se distinguerait pas de la dispersion
ordinaire d'un rouleau -- il faut savoir ce que l'axe 2 fait quand l'axe 1 ne dit rien.

Usage :
    uv run python src/graine/choisir_tirages.py [--propres 2] [--temoins 2]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def choisir(table: dict, propres: int, temoins: int, racine: Path) -> list[dict]:
    bascule = [l for l in table["lignes"] if l["verdict_bascule"]]
    stables = [l for l in table["lignes"] if l["verdict_bascule"] is False]
    # ⚠ Les temoins sont les rouleaux stables les PLUS DISPERSES en aire : ce sont eux qui
    # bornent ce que l'axe 2 fait quand l'axe 1 ne signale rien. Prendre les moins disperses
    # rendrait le temoin trop facile.
    stables.sort(key=lambda l: -l["etendue_relative"])

    cibles = []
    for l in bascule:
        crois = l["croisements"]
        mauvais = [i for i, c in enumerate(crois) if c > 0]
        bons = [i for i, c in enumerate(crois) if c == 0]
        for i in mauvais:
            cibles.append({"rouleau": l["rouleau"], "repetition": i + 1,
                           "role": "mauvais", "transverse": crois[i]})
        for i in bons[:propres]:
            cibles.append({"rouleau": l["rouleau"], "repetition": i + 1,
                           "role": "propre", "transverse": 0})
    for l in stables[:temoins]:
        for i in range(min(2, l["n"])):
            cibles.append({"rouleau": l["rouleau"], "repetition": i + 1,
                           "role": "témoin", "transverse": l["croisements"][i]})

    for c in cibles:
        c["chemin"] = str(racine / "data/tirages" / c["rouleau"] / f"r{c['repetition']}")
        c["existe"] = Path(c["chemin"]).is_dir()
    return cibles


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table", type=Path, default=RACINE / "docs/table_tirages.json")
    ap.add_argument("--propres", type=int, default=2,
                    help="tirages propres a rendre par rouleau qui bascule")
    ap.add_argument("--temoins", type=int, default=2,
                    help="rouleaux stables a inclure comme temoins")
    ap.add_argument("--chemins", action="store_true", help="n'imprimer que les chemins")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    if not a.table.is_file():
        print(f"absent : {a.table}", file=sys.stderr)
        return 1
    cibles = choisir(json.loads(a.table.read_text()), a.propres, a.temoins, RACINE)
    manquants = [c for c in cibles if not c["existe"]]

    if a.chemins:
        print(" ".join(c["chemin"] for c in cibles if c["existe"]))
        return 1 if manquants else 0

    print(f"{len(cibles)} tirages à rendre — "
          f"{sum(1 for c in cibles if c['role'] == 'mauvais')} mauvais, "
          f"{sum(1 for c in cibles if c['role'] == 'propre')} propres appariés, "
          f"{sum(1 for c in cibles if c['role'] == 'témoin')} témoins\n")
    for c in cibles:
        marque = "" if c["existe"] else "   ⚠ absent du disque"
        print(f"  {c['rouleau']:<12} r{c['repetition']:<2} {c['role']:<8} "
              f"{c['transverse']:>6} croisements{marque}")
    print(f"\n  coût estimé : {len(cibles)} × ~10 min ≈ "
          f"{len(cibles) * 10 / 60:.1f} h, contre {72 * 10 / 60:.0f} h pour les 72")
    if manquants:
        print(f"  ⚠ {len(manquants)} tirage(s) absent(s) du disque")

    if a.json:
        a.json.write_text(json.dumps({"cibles": cibles}, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
