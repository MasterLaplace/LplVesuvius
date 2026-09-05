#!/usr/bin/env python3
"""Dans quel volume publié ce maillage vit-il ? — la boîte le dit, et une seule répond.

⚠⚠ POURQUOI CE FICHIER EXISTE. `src/nappe/couverture_publiee.py` pose `UM_PAR_VOXEL = 2.4` en
le justifiant par *« la convention de `chainer_tangentiel.sh` »* et par une cohérence
**interne** — jamais contre le volume déclaré d'un rouleau. `77` §10 et `75` A5 bis en ont
conclu que *« tous les micromètres du tableau de couverture de `44` reposent sur une constante
que rien ne relie à un volume »*, et ont laissé la correction **transportable en feuilles**
plutôt que calculable en micromètres.

⭐⭐⭐ **Or la boîte englobante du maillage désigne son volume, et elle en désigne UN SEUL.**
Un `tifxyz` porte ses coins en voxels du niveau 0 ; un volume publié porte la forme de sa
grille. Un volume trop petit pour contenir la boîte **ne peut pas** être celui du maillage —
ce n'est pas une plausibilité, c'est une impossibilité.

⚠⚠⚠ **Et la prémisse de `77` §10 est fausse** : `PHercParis4` ne publie pas « deux volumes à
7,91 µm », il en publie **cinq**, deux à 45,532 µm, **deux à 2,400** et un à 1,129 — et **aucun
à 7,91**. Le 7,91 µm est la résolution de `PHerc0172`, empruntée. C'est le piège nº 6 du dépôt,
commis dans le document qui l'énonce.

⚠ Ce que ce fichier NE fait pas : lire la taille de voxel autrement que dans le **nom** du
volume. `76` a établi qu'un nom de **volume de surface d'un segment** porte la résolution
*avant* sous-échantillonnage et ment donc ; ici il s'agit des **volumes du rouleau**, une autre
famille, dont le nom est ce que tout le dépôt utilise déjà (`volumes_surface_*.txt`,
`campagne_champ.sh`). Le `.zattrs` publié ne porte que les rapports de pyramide, pas de micron.

Usage :
    uv run python src/nappe/le_volume_du_maillage.py --verifier
    uv run python src/nappe/le_volume_du_maillage.py \\
        data/temoin_rendu/morceaux/morceau_00 --rouleau PHercParis4 \\
        --json docs/mesures/le_volume_du_maillage.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"

VOXEL_DANS_LE_NOM = re.compile(r"-(\d+\.\d+)um-")


def boite_du_maillage(dossier: Path) -> dict:
    """Les deux coins du maillage, en voxels du NIVEAU 0, lus dans son `meta.json`.

    ⚠ Lus et non recalculés depuis les `.tif` : la `bbox` est ce que l'écrivain du maillage a
    déclaré, donc c'est elle qui dit dans quel repère il se croit. Recalculer donnerait le même
    nombre et répondrait à une autre question.
    """
    meta = json.loads((dossier / "meta.json").read_text())
    if "bbox" not in meta:
        raise SystemExit(f"{dossier}/meta.json ne déclare pas de bbox")
    (x0, y0, z0), (x1, y1, z1) = meta["bbox"]
    return {"x": [x0, x1], "y": [y0, y1], "z": [z0, z1], "uuid": meta.get("uuid")}


def voxel_du_nom(nom: str) -> float | None:
    """La taille de voxel qu'un nom de volume de ROULEAU déclare, ou None."""
    m = VOXEL_DANS_LE_NOM.search(nom)
    return float(m.group(1)) if m else None


def volumes_publies(rouleau: str, timeout: float = 90.0) -> list[str]:
    """Les `.zarr` que le bucket publie sous `<rouleau>/volumes/`."""
    r = subprocess.run(
        ["curl", "-s", "--max-time", str(int(timeout)),
         f"{BUCKET}/?list-type=2&prefix={rouleau}/volumes/&delimiter=/"],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"listage impossible pour {rouleau}")
    return sorted(p[:-1] for ligne in r.stdout.replace("<", "\n").splitlines()
                  if ligne.startswith("Prefix>")
                  for p in [ligne[len("Prefix>"):]] if p.endswith(".zarr/"))


def forme(cle: str, timeout: float = 60.0) -> list[int] | None:
    """La forme du niveau 0 d'un volume publié, ou None si le bucket ne la donne pas."""
    r = subprocess.run(["curl", "-s", "--fail", "--max-time", str(int(timeout)),
                        f"{BUCKET}/{cle}/0/.zarray"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout).get("shape")


def contient(shape: list[int], boite: dict) -> bool:
    """
    @brief La grille peut-elle tenir cette boîte ?

    ⚠ Une forme zarr est `[z, y, x]` et la boîte d'un `tifxyz` est en `x, y, z` — les inverser
    donnerait un verdict qui a l'air d'en être un. Les coins négatifs sont refusés : un
    maillage qui sortirait de la grille par le bas n'y vit pas non plus.
    """
    if not shape or len(shape) != 3:
        return False
    nz, ny, nx = shape
    return (boite["x"][0] >= 0 and boite["y"][0] >= 0 and boite["z"][0] >= 0
            and boite["x"][1] <= nx and boite["y"][1] <= ny and boite["z"][1] <= nz)


def designer(boite: dict, volumes: dict[str, list[int] | None]) -> dict:
    """Le volume qui contient la boîte — et un REFUS s'il n'y en a pas exactement un.

    ⚠⚠ Refuser à zéro **et** à deux est ce qui rend la désignation utilisable : à deux, on
    « nommerait » un volume par l'ordre du listage, ce qui n'est pas une propriété des données.
    """
    contenants = [c for c, s in volumes.items() if s and contient(s, boite)]
    return {"contenants": sorted(contenants),
            "designe": contenants[0] if len(contenants) == 1 else None,
            "voxel_um": voxel_du_nom(contenants[0]) if len(contenants) == 1 else None,
            "candidats": len(volumes), "reconstructible": len(contenants) == 1}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    b = {"x": [10, 100], "y": [20, 200], "z": [30, 300], "uuid": "t"}
    v("une grille assez grande contient la boîte", contient([400, 300, 200], b))
    # ⚠⚠ L'ORDRE DES AXES : une forme zarr est [z, y, x] et une bbox tifxyz est x, y, z.
    # Les confondre rendrait un verdict qui a l'air d'en être un.
    v("... et l'ordre des axes compte : [x, y, z] ne passe PAS",
      not contient([200, 300, 400], b), "z=300 > 200")
    v("une grille trop courte en z ne la contient pas", not contient([299, 300, 200], b))
    v("... ni trop étroite en x", not contient([400, 300, 99], b))
    v("un coin négatif est refusé",
      not contient([400, 300, 200], {**b, "z": [-1, 300]}))
    v("une forme absente n'est pas une contenance", not contient(None, b))
    v("... ni une forme à deux axes", not contient([400, 300], b))

    v("le voxel se lit dans un nom de volume de rouleau",
      voxel_du_nom("PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr") == 2.4)
    v("... et un nom sans micron rend None", voxel_du_nom("x/volumes/sans_resolution.zarr") is None)

    # --- la désignation, et ses deux refus ---
    un = designer(b, {"a.zarr": [400, 300, 200], "b.zarr": [10, 10, 10]})
    v("un seul contenant désigne le volume", un["designe"] == "a.zarr" and un["reconstructible"])
    # ⚠⚠ À DEUX, on « nommerait » un volume par l'ordre du listage — pas une propriété des
    # données. Le refus est ce qui empêche une désignation d'être un tirage.
    deux = designer(b, {"a.zarr": [400, 300, 200], "c.zarr": [500, 400, 300]})
    v("... deux contenants REFUSENT de désigner",
      deux["designe"] is None and not deux["reconstructible"], str(deux["contenants"]))
    zero = designer(b, {"b.zarr": [10, 10, 10]})
    v("... et zéro aussi", zero["designe"] is None and not zero["reconstructible"])

    # --- la boîte lue dans un vrai meta ---
    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "m").mkdir()
    (d / "m" / "meta.json").write_text(
        json.dumps({"bbox": [[1.5, 2.5, 3.5], [4.5, 5.5, 6.5]], "uuid": "m"}), encoding="utf-8")
    bb = boite_du_maillage(d / "m")
    v("la boîte est lue dans le meta, x/y/z dans cet ordre",
      bb["x"] == [1.5, 4.5] and bb["z"] == [3.5, 6.5], str(bb))
    (d / "m" / "meta.json").write_text(json.dumps({"uuid": "m"}), encoding="utf-8")
    v("un meta sans bbox est REFUSÉ, pas défauté à zéro",
      _leve(lambda: boite_du_maillage(d / "m")))
    shutil.rmtree(d, ignore_errors=True)

    # --- contre le VRAI maillage de `44`, si le bucket répond ---
    source = RACINE / "data" / "temoin_rendu" / "morceaux" / "morceau_00"
    if not (source / "meta.json").is_file():
        print("  ⚠ maillage absent : la partie « vrai arbre » n'a pas tourné")
    else:
        boite = boite_du_maillage(source)
        try:
            cles = volumes_publies("PHercParis4")
        except SystemExit:
            cles = []
        if not cles:
            print("  ⚠ bucket injoignable : la partie réseau n'a pas tourné")
        else:
            vols = {c: forme(c) for c in cles}
            r = designer(boite, vols)
            # ⚠⚠⚠ La prémisse de `77` §10 : « les deux volumes publiés sont à 7,91 µm ».
            # Il y en a CINQ, et aucun à 7,91.
            voxels = sorted({voxel_du_nom(c) for c in cles if voxel_du_nom(c)})
            v(f"`PHercParis4` publie plus de deux volumes ({len(cles)})", len(cles) > 2,
              ", ".join(f"{x:g}" for x in voxels))
            v("... et aucun n'est à 7,910 µm", 7.91 not in voxels, str(voxels))
            v("un seul volume publié peut contenir le maillage de `44`",
              r["reconstructible"], str(r["contenants"]))
            v("... et il est à 2,400 µm, la constante que `couverture_publiee` posait",
              r["voxel_um"] == 2.4, str(r["voxel_um"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("maillage", type=Path, nargs="?",
                   default=RACINE / "data" / "temoin_rendu" / "morceaux" / "morceau_00")
    p.add_argument("--rouleau", default="PHercParis4")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    boite = boite_du_maillage(a.maillage)
    cles = volumes_publies(a.rouleau)
    vols = {c: forme(c) for c in cles}
    r = designer(boite, vols)
    print(f"maillage {a.maillage.name} — boîte x {boite['x'][0]:.0f}–{boite['x'][1]:.0f}  "
          f"y {boite['y'][0]:.0f}–{boite['y'][1]:.0f}  z {boite['z'][0]:.0f}–{boite['z'][1]:.0f}\n")
    print(f"{'volume publié':58s} {'forme (z,y,x)':>26s}  contient ?")
    print("-" * 100)
    for c in cles:
        s = vols[c]
        print(f"{c.split('/')[-1]:58s} {str(s):>26s}  "
              f"{'OUI' if s and contient(s, boite) else 'non'}")
    print(f"\n{len(r['contenants'])} volume(s) contenant(s) — "
          + (f"désigné : {r['designe'].split('/')[-1]} ({r['voxel_um']:g} µm)"
             if r["designe"] else "REFUS : la provenance n'est pas reconstructible"))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(
            {"maillage": str(a.maillage.relative_to(RACINE)), "rouleau": a.rouleau,
             "boite": boite, "volumes": {c: vols[c] for c in cles}, **r},
            indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
