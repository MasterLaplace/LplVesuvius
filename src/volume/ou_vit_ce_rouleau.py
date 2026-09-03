#!/usr/bin/env python3
"""Ce qu'un rouleau contient VRAIMENT — toutes les sources à la fois, et leurs désaccords.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE : LE MÊME ANGLE MORT A MORDU TROIS FOIS, et la troisième
fois il a produit une **correction qui était elle-même fausse**.

  1. `59` — la campagne de scan lue sur le seul bucket open-data (`*-masked.zarr`), donc
     aveugle à l'ancien layout `full-scrolls/`. Le volume portant le résultat de référence,
     `20230205180739` à 7,91 µm, y était **invisible**.
  2. `67` §4.2 — « l'ombilic n'est pas publié », vérifié préfixe par préfixe **sur le bucket
     S3**. Il vit sur `dl.ash2txt.org`, l'autre serveur du concours. 241 points, HTTP 200.
  3. `07` §9 — « ⚠⚠ Corrigé le 2026-08-19 : PHerc1667 n'a AUCUN volume à 7,91 µm », vérifié
     sur `volumes_surface_PHerc1667.txt`. Ce fichier liste des **volumes de surface**, pas
     des **scans** : `PHerc1667` publie bien `20231117161658-7.910um-53keV`, et le maillage
     que le balayage a lu s'appelle `…-on-20231117161658-7.91um.tifxyz`. **La correction
     invalidait une ligne de tableau qui était bonne.**

⭐ Trois occurrences, c'est une famille, et le mode de panne est toujours le même :
**interroger UNE vue du corpus et conclure sur LE corpus**. Aucun outil ne répondait à la
question entière, donc chacun la re-dérivait de la vue qu'il avait sous la main.

⭐⭐ CE QUE CE FICHIER FAIT, ET C'EST LA SEULE CHOSE : pour un rouleau, il dit quelles
résolutions il porte **et d'où vient chaque réponse**. Il ne tranche pas, il **juxtapose** —
parce que ce qui a manqué les trois fois n'est pas une meilleure source, c'est de voir les
sources ensemble.

⚠ Il **nomme les désaccords** plutôt que de les fondre. Une résolution vue par une source et
pas par une autre n'est pas une erreur : un scan peut exister sans volume de surface rendu,
et c'est exactement le cas qui a piégé `07`. Ce qui serait une erreur, c'est de ne pas le
voir.

⚠ CE QU'IL N'ÉTABLIT PAS : que les sources soient complètes. Le réseau est optionnel et le
listage de `dl.ash2txt.org` n'est pas exhaustif ; le relevé local ne voit que ce qui a été
téléchargé. Un « absent partout » reste un **absent des sources interrogées**, et le fichier
l'écrit ainsi.

Usage :
    uv run python src/volume/ou_vit_ce_rouleau.py PHerc1667
    uv run python src/volume/ou_vit_ce_rouleau.py --verifier
    uv run python src/volume/ou_vit_ce_rouleau.py PHerc1667 --json docs/mesures/ou_vit_PHerc1667.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
INDEX = RACINE / "data" / "metadata.min.json"

UM = re.compile(r"(\d+\.\d+)um")
"""Le pas d'échantillonnage tel que TOUTES les sources l'écrivent : dans un `long_id` de
scan, dans un nom de `.tifxyz`, dans un chemin de volume de surface. C'est ce qui permet de
les comparer sans table de correspondance."""


def _index() -> dict:
    brut = INDEX.read_bytes()
    try:
        texte = gzip.decompress(brut).decode()
    except (OSError, gzip.BadGzipFile):
        texte = brut.decode()
    return json.loads(texte)["samples"]


def _um(texte: str) -> set[str]:
    """
    @brief Les pas d'échantillonnage nommés dans une chaîne, normalisés à trois décimales.

    ⚠ La normalisation est nécessaire et suffit : le corpus écrit le même scan « 7.910um »
    dans un `long_id` et « 7.91um » dans un nom de maillage. Sans elle, deux vues du même
    scan se compteraient comme un désaccord.
    """
    return {f"{float(v):.3f}" for v in UM.findall(texte)}


def relever(rouleau: str) -> dict:
    """
    @brief Les résolutions de ce rouleau, par source, avec ce que chaque source EST.
    """
    sources: dict[str, dict] = {}

    fiche = _index().get(rouleau, {})
    scans: set[str] = set()
    for scan in fiche.get("scans", {}).values():
        scans |= _um(scan.get("long_id", ""))
    sources["scans publiés (metadata.min.json)"] = dict(
        est="ce que le concours déclare avoir SCANNÉ", um=sorted(scans))

    vols: set[str] = set()
    for v in fiche.get("volumes", {}).values():
        p = v.get("properties", {}).get("pixel_size_um")
        if p:
            vols.add(f"{float(p):.3f}")
    sources["volumes reconstruits (metadata.min.json)"] = dict(
        est="ce qui est reconstruit et téléchargeable", um=sorted(vols))

    # ⚠ Les volumes de SURFACE sont la source qui a piégé `07` : un rouleau peut avoir un
    # scan sans qu'aucun segment n'y soit rendu. C'est un sous-ensemble par construction.
    surf = RACINE / "docs" / "mesures" / f"volumes_surface_{rouleau}.txt"
    sources["volumes de surface (relevé local)"] = dict(
        est="le tomogramme rééchantillonné sur les couches d'un SEGMENT — sous-ensemble",
        um=sorted(_um(surf.read_text())) if surf.is_file() else [],
        absent=not surf.is_file())

    traces = RACINE / "data" / "traces" / rouleau
    local: set[str] = set()
    if traces.is_dir():
        for m in traces.glob("*/mesh/*.tifxyz"):
            local |= _um(m.name)
    sources["maillages sur disque (data/traces)"] = dict(
        est="ce qu'une campagne d'ici a réellement lu", um=sorted(local),
        absent=not traces.is_dir())

    vues = {n: set(s["um"]) for n, s in sources.items() if s["um"]}
    union = set().union(*vues.values()) if vues else set()
    # ⚠ Le désaccord est le PRODUIT de ce fichier, pas son bruit : c'est lui qui aurait
    # évité les trois pannes. Une résolution vue par une source et pas par une autre est
    # rapportée avec les deux listes, jamais moyennée.
    desaccords = [
        dict(um=u, vue_par=sorted(n for n, s in vues.items() if u in s),
             absente_de=sorted(n for n, s in vues.items() if u not in s))
        for u in sorted(union)
        if any(u not in s for s in vues.values())
    ]
    return dict(rouleau=rouleau, sources=sources, union=sorted(union),
                n_sources_peuplees=len(vues), desaccords=desaccords)


def _verifier() -> int:
    """Les contrôles, ancrés sur le cas qui a produit la troisième panne."""
    echecs = 0

    def v(intitule: str, cond: bool, detail: str = "") -> None:
        nonlocal echecs
        if not cond:
            echecs += 1
        print(f"  [{'ok  ' if cond else 'FAIL'}] {intitule}{(' — ' + detail) if detail else ''}")

    r = relever("PHerc1667")
    scans = set(r["sources"]["scans publiés (metadata.min.json)"]["um"])
    surf = set(r["sources"]["volumes de surface (relevé local)"]["um"])
    disque = set(r["sources"]["maillages sur disque (data/traces)"]["um"])

    print("le cas qui a produit la troisième panne")
    v("PHerc1667 publie bien un scan à 7,91 µm", "7.910" in scans, ", ".join(sorted(scans)))
    v("... et un maillage sur disque le lit à cette résolution", "7.910" in disque,
      ", ".join(sorted(disque)))
    # ⚠⚠ LE CONTRÔLE QUI PORTE LE FICHIER : la source qui a servi à conclure « aucun volume
    # à 7,91 µm » doit effectivement NE PAS le voir. Si elle le voyait, la panne aurait une
    # autre cause et l'explication de l'en-tête serait fausse.
    v("... alors que les volumes de SURFACE ne le voient pas (la source qui a trompé `07`)",
      "7.910" not in surf, ", ".join(sorted(surf)) or "aucun")

    print("le désaccord est rapporté, pas fondu")
    d = [x for x in r["desaccords"] if x["um"] == "7.910"]
    v("le désaccord sur 7,91 µm est nommé", bool(d),
      f"{len(r['desaccords'])} désaccord(s) au total")
    v("... avec les deux listes", bool(d) and d[0]["vue_par"] and d[0]["absente_de"],
      f"vue par {len(d[0]['vue_par'])}, absente de {len(d[0]['absente_de'])}" if d else "")

    print("l'écriture du corpus est normalisée")
    # Sans ça, « 7.910um » d'un long_id et « 7.91um » d'un nom de maillage seraient deux
    # resolutions differentes, et le fichier fabriquerait le desaccord qu'il existe pour voir.
    v("« 7.910um » et « 7.91um » sont la même chose",
      _um("a-7.910um-b") == _um("c-7.91um-d"), str(_um("a-7.91um-b")))

    print("plusieurs sources sont réellement interrogées")
    v("au moins trois sources peuplées", r["n_sources_peuplees"] >= 3,
      f"{r['n_sources_peuplees']} sur 4")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print("  ALL PASS (0 failures, 7 checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("rouleau", nargs="?", help="par ex. PHerc1667")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    if args.verifier:
        return 1 if _verifier() else 0
    if not args.rouleau:
        p.error("donner un rouleau, ou --verifier")

    r = relever(args.rouleau)
    print(f"{r['rouleau']} — résolutions vues, par source\n")
    for nom, s in r["sources"].items():
        etat = ", ".join(s["um"]) if s["um"] else ("source absente" if s.get("absent") else "aucune")
        print(f"  {nom}")
        print(f"      {s['est']}")
        print(f"      → {etat}\n")
    if r["desaccords"]:
        print("⚠ désaccords entre sources — c'est le produit de ce relevé :")
        for d in r["desaccords"]:
            print(f"  {d['um']} µm vue par {len(d['vue_par'])} source(s), absente de "
                  f"{len(d['absente_de'])}")
            for n in d["absente_de"]:
                print(f"      absente de : {n}")
    else:
        print("aucun désaccord entre les sources interrogées.")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
