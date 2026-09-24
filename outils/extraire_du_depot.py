"""Extraire du dépôt de recherche ce que le logiciel embarque pour un segment, et rien d'autre.

Le pipeline Grand Prize doit tourner sans l'arbre de recherche (dans l'image Docker, par exemple). Ce
qu'il lui faut de la recherche est PUBLIÉ dans `docs/mesures/` : la présence des chunks, les 112 bandes
lues, les sources qui contrôlent une lecture neuve, le contexte de la procédure, le budget et la
couverture à la main. Ce script les relit par les lecteurs mêmes de la chaîne et les écrit sous
`vesuve/donnees/segments/<segment>/`, de façon déterministe (clés triées, gzip sans date), pour qu'un
test puisse exiger que l'embarqué égale une extraction fraîche.

    uv run --extra tests python outils/extraire_du_depot.py [--recherche <racine>]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

LE_SEGMENT = "20230702185753"
ICI = Path(__file__).resolve().parents[1]
LA_SORTIE = ICI / "vesuve" / "donnees" / "segments" / LE_SEGMENT


def _preparer(recherche: Path) -> None:
    for famille in sorted((recherche / "src").iterdir()):
        if famille.is_dir() and str(famille) not in sys.path:
            sys.path.insert(0, str(famille))


def _ecrire(chemin: Path, x) -> None:
    brut = json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    if chemin.suffix == ".gz":
        brut = gzip.compress(brut, compresslevel=9, mtime=0)
    chemin.write_bytes(brut)


def _empreinte(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extraire(recherche: Path, sortie: Path) -> dict:
    _preparer(recherche)
    from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import ce_que_225_a_publie
    from la_couverture_sans_main import (LES_LECTURES_PUBLIEES, ce_que_243_a_publie, ce_que_245_a_publie,
                                         les_lectures_publiees)
    from le_segment_au_dela_du_rectangle_se_relie_t_il import ce_que_233_a_publie, les_sources_de_234
    from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu
    from ou_sarrete_le_segment import ce_que_232_a_publie
    from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu
    from deux_chemins_arrivent_ils_sur_la_meme_spire import ce_que_223_a_rendu
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS
    mesures = recherche / "docs" / "mesures"
    sortie.mkdir(parents=True, exist_ok=True)

    presence = json.loads((mesures / "ou_sarrete_le_segment.json").read_text())["la_presence"]
    _ecrire(sortie / "presence.json.gz", {"la_grille": presence["la_grille"], "les_rangees": presence["les_rangees"]})

    bandes = []
    for b in les_lectures_publiees()["les_bandes"]:
        bandes.append({k: b[k] for k in ("le_sens", "le_centre", "les_lignes", "de", "a", "le_long", "en_travers")}
                      | {"les_lectures": {l_: {"refuses": x.get("refuses") or {}}
                                          for l_, x in (b.get("les_lectures") or {}).items()}})
    _ecrire(sortie / "bandes_publiees.json.gz", {"les_bandes": bandes})

    p219, p223, p224 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu()
    sources = les_sources_de_234(p219, p223, p224, ce_que_232_a_publie(), ce_que_233_a_publie())
    _ecrire(sortie / "sources_de_controle.json.gz", {
        nom: {"domaine": {f: sorted([list(c) for c in s]) for f, s in S["domaine"].items()},
              "pas": {f: sorted([[r, c, p] for (r, c), p in s.items()]) for f, s in S["pas"].items()}}
        for nom, S in sorted(sources.items())})

    p225, p245, p243 = ce_que_225_a_publie(), ce_que_245_a_publie(), ce_que_243_a_publie()
    budget = json.loads((mesures / "le_budget_de_la_nappe.json").read_text())["les_budgets"]
    volume = next(l.split("\t")[1] for l in (mesures / "volumes_surface_PHercParis4.txt").read_text().splitlines()
                  if l.startswith(f"{LE_SEGMENT}\t") and "/2.4um-" in l)
    commit = subprocess.run(["git", "-C", str(recherche), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    sources_lues = sorted({*LES_LECTURES_PUBLIEES, mesures / "ou_sarrete_le_segment.json", mesures / "le_budget_de_la_nappe.json",
                           mesures / "une_aile_plus_etroite_tient_elle.json", mesures / "la_portee_voit_elle_sa_traversee.json"})
    contexte = {
        "le_segment": LE_SEGMENT, "lobjet": "PHercParis4", "le_volume": volume,
        "le_voxel_um": 2.4, "le_pas_um": 173.0, "le_demi_feuillet_voxels": int(DEMI_PAS_EN_VOXELS),
        "la_procedure": {"plus_long": int(max(p225["les_longueurs_essayees"])), "graine": int(p224["graine"]),
                         "tirages": int(p224["tirages"]), "demi": float(DEMI_PAS_EN_VOXELS),
                         "portee": int(p245["la_portee_qui_voit"])},
        "le_budget": {"traverser": {k: v["la_dispersion_en_voxels"] for k, v in budget["traverser"].items()},
                      "saccorder": {k: v["la_dispersion_en_voxels"] for k, v in budget["saccorder"].items()},
                      "les_coutures_dune_rangee": 284},
        "la_couverture_a_la_main": {"les_boucles": [[co, k] for co, k in p243["les_boucles"]],
                                    "la_couverture": p243["la_couverture"]},
        "la_provenance": {"le_commit_de_la_recherche": commit,
                          "les_fichiers": {str(p.relative_to(recherche)): _empreinte(p) for p in sources_lues}},
    }
    _ecrire(sortie / "contexte.json", contexte)
    return contexte


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--recherche", type=Path, default=ICI.parent)
    p.add_argument("--sortie", type=Path, default=LA_SORTIE)
    a = p.parse_args()
    c = extraire(a.recherche.resolve(), a.sortie)
    print(f"écrit : {a.sortie} ({len(c['la_provenance']['les_fichiers'])} fichiers de recherche relus)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
