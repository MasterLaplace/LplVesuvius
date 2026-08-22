#!/usr/bin/env python3
"""Quel volume va avec quelle prediction de surface — par IDENTITE, pas par position.

⚠⚠ **Ce fichier existe parce que `tools/campagne_graines.sh` appariait par POSITION** :
`lister .../surfaces/ | head -1` et `lister .../volumes/ | head -1`. Tant qu'un rouleau
n'a qu'un scan, les deux listes ont un element et le resultat est juste. Des qu'il en a
deux — c'est le cas de `PHerc1203`, scanne a 9,362 µm et a 2,403 µm — la premiere surface
et le premier volume ne sont le meme scan **que si les deux listes se trouvent triees
pareil**. Rien ne le garantit.

⚠ Et la panne serait SILENCIEUSE, du genre le plus couteux : le script lit la taille de
voxel dans le nom du volume, donc il tracerait la surface d'un scan avec la resolution
d'un autre. `vc_grow_seg_from_seed` ne s'en apercevrait pas — il rendrait une surface dont
l'aire, les coordonnees et la geometrie sont toutes fausses d'un facteur constant, sans un
seul message. C'est exactement le piege que l'en-tete de `campagne_graines.sh` nomme
(« emprunter le chiffre d'un rouleau voisin ») applique a deux scans d'un MEME rouleau.

⭐ Le remede est dans les noms : une prediction s'appelle `<scan>-surface-...zarr` et son
volume `<scan>-<voxel>um-...zarr`. Le prefixe est l'identite du scan. On apparie dessus.

Usage :
    uv run python analysis/src/apparier_volumes.py PHerc1203
    uv run python analysis/src/apparier_volumes.py --tous --json docs/appariement.json
    python3 analysis/src/apparier_volumes.py --verifier
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
# Les rouleaux du prix, dans l'ordre ou `tools/carte_separabilite.sh` les liste.
ROULEAUX = ("PHerc0125", "PHerc0139", "PHerc0191", "PHerc0211", "PHerc0257", "PHerc0268",
            "PHerc0358", "PHerc0800", "PHerc0813", "PHerc0826", "PHerc1203", "PHerc1218",
            "PHerc1447", "PHerc1545")

SCAN = re.compile(r"^(\d{14})-")
VOXEL = re.compile(r"-(\d+\.\d+)um-")


def scan_de(nom: str) -> str | None:
    """L'identite du scan : l'horodatage de tete du nom de dossier."""
    m = SCAN.match(nom)
    return m.group(1) if m else None


def voxel_de(nom: str) -> float | None:
    """La taille de voxel, LUE dans le nom du volume et jamais supposee."""
    m = VOXEL.search(nom)
    return float(m.group(1)) if m else None


def apparier(surfaces: list[str], volumes: list[str]) -> dict:
    """Apparie par identite de scan, et dit si la position aurait donne la meme reponse.

    ⚠ Rend AUSSI le verdict de l'appariement par position, parce que c'est ce que fait le
    script de campagne aujourd'hui : sans la comparaison, corriger le script serait un
    changement dont personne ne saurait s'il repare quelque chose.
    """
    par_scan = {}
    for v in volumes:
        s = scan_de(v)
        if s:
            par_scan.setdefault(s, []).append(v)

    paires, orphelines = [], []
    for surf in surfaces:
        s = scan_de(surf)
        cands = par_scan.get(s or "", [])
        if not cands:
            orphelines.append(surf)
            continue
        # ⚠ Plusieurs volumes d'un meme scan : on prend le premier dans l'ordre du
        # depot, mais on le DIT, parce que le choix n'est alors plus determine par
        # l'identite seule.
        paires.append({"surface": surf, "volume": cands[0], "scan": s,
                       "voxel_um": voxel_de(cands[0]),
                       "volumes_du_scan": len(cands)})

    position = None
    if surfaces and volumes:
        s0, v0 = surfaces[0], volumes[0]
        position = {"surface": s0, "volume": v0,
                    "meme_scan": scan_de(s0) is not None and scan_de(s0) == scan_de(v0),
                    "voxel_um": voxel_de(v0)}
    return {"paires": paires, "orphelines": orphelines, "par_position": position,
            "scans": len(par_scan)}


def choisir(paires: list[dict], voxel_cible: float | None,
            tolerance: float = 1.0) -> tuple[dict | None, str]:
    """La paire a tracer, et POURQUOI celle-la.

    ⚠⚠ Un rouleau a plusieurs scans est un rouleau ou « quel scan ? » est une DECISION,
    et l'ordre d'un listage S3 n'en est pas une. `PHerc1203` est scanne a 9,362 µm et a
    2,403 µm, soit un facteur nettement superieur a 3 : les deux sont valides, et le choix
    change tout ce qui suit. La campagne des graines est une comparaison APPARIEE sur
    douze rouleaux tous a 8,64 ou 9,362 µm, donc le scan a prendre est celui de la
    COHORTE — sinon le treizieme rouleau n'est pas comparable aux douze autres, et le
    dessein apparie de la campagne est perdu sans qu'aucun message ne le dise.

    ⚠ Rend une raison plutot qu'un simple resultat : un appelant qui trace doit pouvoir
    l'ecrire dans son journal, et un choix dont le motif n'est pas transporte redevient
    un choix par defaut au premier refactor.
    """
    if not paires:
        return None, "aucune paire"
    if len(paires) == 1:
        return paires[0], "scan unique"
    if voxel_cible is None:
        return None, (f"{len(paires)} scans et aucune resolution demandee — refus, "
                      f"le choix appartient a l'appelant")
    proches = [p for p in paires
               if p["voxel_um"] is not None
               and abs(p["voxel_um"] - voxel_cible) <= tolerance]
    if not proches:
        dispo = ", ".join(f"{p['voxel_um']} µm" for p in paires)
        return None, f"aucun scan a {voxel_cible} µm ± {tolerance} — disponibles : {dispo}"
    if len(proches) > 1:
        return None, (f"{len(proches)} scans a {voxel_cible} µm ± {tolerance} — "
                      f"ambigu, refus plutot qu'un tirage au sort")
    return proches[0], f"choisi pour sa resolution, {proches[0]['voxel_um']} µm"


def lister(prefixe: str, delai: int = 60) -> list[str]:
    r = subprocess.run(["curl", "-s", "--max-time", str(delai),
                        f"{BASE}/?list-type=2&prefix={prefixe}&delimiter=/"],
                       capture_output=True, text=True)
    out = []
    for bloc in r.stdout.split("<"):
        if bloc.startswith("Prefix>"):
            p = bloc[len("Prefix>"):]
            if p != prefixe and p.endswith("/"):
                out.append(p[len(prefixe):-1])
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("l'identite d'un scan est son horodatage de tete",
      scan_de("20250820131727-surface-x.zarr") == "20250820131727")
    v("un nom sans horodatage n'a pas d'identite", scan_de("surface-x.zarr") is None)
    v("la taille de voxel est lue dans le nom",
      voxel_de("20250820131727-9.362um-1.2m-113keV-masked.zarr") == 9.362)
    v("... et absente quand le nom ne la porte pas",
      voxel_de("20250820131727-surface-m7-L0-th0.2.zarr") is None)

    # ⭐ Un seul scan : position et identite disent la meme chose, et c'est pourquoi le
    # defaut a survecu -- douze rouleaux sur treize sont dans ce cas.
    un = apparier(["20250820131727-surface-a.zarr"],
                  ["20250820131727-9.362um-x.zarr"])
    v("un rouleau a scan unique s'apparie", len(un["paires"]) == 1)
    v("... et la position aurait donne la meme reponse", un["par_position"]["meme_scan"])
    v("... avec le bon voxel", un["paires"][0]["voxel_um"] == 9.362)

    # ⚠⚠ LA SONDE : deux scans dont les listes ne sont PAS triees pareil. C'est le cas
    # que l'appariement par position rate, et le seul qui justifie ce fichier.
    croise = apparier(
        ["20260319130212-surface-L2.zarr", "20250820131727-surface-L0.zarr"],
        ["20250820131727-9.362um-x.zarr", "20260319130212-2.403um-y.zarr"])
    v("deux scans croises s'apparient quand meme par identite",
      len(croise["paires"]) == 2 and croise["orphelines"] == [])
    v("... chacun avec SON voxel",
      {p["scan"]: p["voxel_um"] for p in croise["paires"]}
      == {"20260319130212": 2.403, "20250820131727": 9.362},
      str({p["scan"]: p["voxel_um"] for p in croise["paires"]}))
    v("... et la position, elle, se trompe — c'est ce que ce fichier existe pour dire",
      croise["par_position"]["meme_scan"] is False)
    # ⚠ Le controle du controle : si la sonde ci-dessus passait aussi quand les listes
    # s'accordent, elle ne discriminerait rien.
    droit = apparier(
        ["20250820131727-surface-L0.zarr", "20260319130212-surface-L2.zarr"],
        ["20250820131727-9.362um-x.zarr", "20260319130212-2.403um-y.zarr"])
    v("... alors qu'elle a raison quand les listes s'accordent",
      droit["par_position"]["meme_scan"] is True)

    # ⭐ Le choix, et surtout ses REFUS : un rouleau a deux scans n'a pas de reponse par
    # defaut, et en inventer une est precisement ce qui rendrait le treizieme rouleau
    # incomparable aux douze autres sans qu'aucun message ne le dise.
    deux = croise["paires"]
    pick, pourquoi = choisir(deux, 9.362)
    v("un scan est choisi par sa RESOLUTION quand il y en a plusieurs",
      pick is not None and pick["voxel_um"] == 9.362, pourquoi)
    pick, pourquoi = choisir(deux, None)
    v("... et sans resolution demandee, le choix est REFUSE, pas tire au sort",
      pick is None and "refus" in pourquoi, pourquoi)
    pick, pourquoi = choisir(deux, 5.0)
    v("... une resolution absente est refusée en NOMMANT ce qui existe",
      pick is None and "9.362 µm" in pourquoi and "2.403 µm" in pourquoi, pourquoi)
    pick, pourquoi = choisir(un["paires"], None)
    v("un scan unique ne demande aucune resolution",
      pick is not None and pourquoi == "scan unique", pourquoi)
    pick, pourquoi = choisir([], 9.362)
    v("aucune paire ne rend aucun choix", pick is None)
    # ⚠ Deux scans a la MEME resolution : la resolution ne discrimine plus, donc le
    # choix redeviendrait un tirage. Refus.
    ambigu = apparier(["20250101000000-surface-a.zarr", "20250202000000-surface-b.zarr"],
                      ["20250101000000-9.362um-x.zarr", "20250202000000-9.362um-y.zarr"])
    pick, pourquoi = choisir(ambigu["paires"], 9.362)
    v("deux scans a la meme resolution sont AMBIGUS, donc refuses",
      pick is None and "ambigu" in pourquoi, pourquoi)

    seule = apparier(["20991231235959-surface-z.zarr"], ["20250820131727-9.362um-x.zarr"])
    v("une surface sans volume est declaree orpheline, pas appariee au hasard",
      seule["paires"] == [] and len(seule["orphelines"]) == 1)
    v("un rouleau vide ne rend aucune paire ni aucune position",
      apparier([], []) == {"paires": [], "orphelines": [], "par_position": None,
                           "scans": 0})

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rouleaux", nargs="*")
    ap.add_argument("--tous", action="store_true", help="les 14 rouleaux du prix")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--pour-campagne", action="store_true",
                    help="imprimer « <surface> <volume> <voxel> » pour LE scan à tracer, "
                         "et sortir 1 si le choix n'est pas déterminé")
    # ⚠ Optionnelle EXPRES : un rouleau a scan unique n'a pas de choix a faire, donc
    # exiger une resolution obligerait l'appelant a en inventer une pour douze rouleaux
    # sur quatorze — et une valeur inventee finit par etre celle qui decide.
    ap.add_argument("--voxel-um", type=float,
                    help="résolution du scan à prendre, quand le rouleau en a plusieurs")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    if a.pour_campagne:
        if len(a.rouleaux) != 1:
            ap.error("--pour-campagne prend exactement un rouleau")
        r = a.rouleaux[0]
        d = apparier([s for s in lister(f"{r}/representations/predictions/surfaces/")
                      if s.endswith(".zarr")],
                     [v for v in lister(f"{r}/volumes/") if v.endswith(".zarr")])
        pick, pourquoi = choisir(d["paires"], a.voxel_um)
        if pick is None:
            print(f"{r} : {pourquoi}", file=sys.stderr)
            return 1
        print(f"{r}/representations/predictions/surfaces/{pick['surface']} "
              f"{r}/volumes/{pick['volume']} {pick['voxel_um']}")
        print(f"  # {pourquoi}", file=sys.stderr)
        return 0

    cibles = list(ROULEAUX) if a.tous else a.rouleaux
    if not cibles:
        ap.error("nommer au moins un rouleau, ou --tous")

    tout, desaccords = {}, []
    for r in cibles:
        surfaces = [s for s in lister(f"{r}/representations/predictions/surfaces/")
                    if s.endswith(".zarr")]
        volumes = [v for v in lister(f"{r}/volumes/") if v.endswith(".zarr")]
        d = apparier(surfaces, volumes)
        tout[r] = d
        pos = d["par_position"]
        marque = ""
        if d["scans"] > 1:
            marque = "  ⚠ plusieurs scans"
        if pos and not pos["meme_scan"]:
            marque = "  ⚠⚠ LA POSITION SE TROMPE"
            desaccords.append(r)
        print(f"  {r}  {len(surfaces)} surface(s), {len(volumes)} volume(s), "
              f"{d['scans']} scan(s){marque}")
        for p in d["paires"]:
            print(f"      {p['voxel_um']} µm  {p['surface'][:52]}")
        for o in d["orphelines"]:
            print(f"      ⚠ sans volume : {o[:60]}")

    print(f"\n  {len(desaccords)} rouleau(x) où l'appariement PAR POSITION donne le "
          f"mauvais volume" + (f" : {', '.join(desaccords)}" if desaccords else ""))
    plusieurs = [r for r, d in tout.items() if d["scans"] > 1]
    print(f"  {len(plusieurs)} rouleau(x) à plusieurs scans" +
          (f" : {', '.join(plusieurs)}" if plusieurs else "") +
          " — les seuls où la question se pose")

    if a.json:
        a.json.write_text(json.dumps(tout, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
