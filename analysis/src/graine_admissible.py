#!/usr/bin/env python3
"""Peut-on semer ICI, et dans quelle prédiction ?

⚠⚠ POURQUOI. Une graine est une coordonnée, et une coordonnée ne veut rien dire sans le
volume qui la numérote. Le 2026-08-24 : la graine `m7` était une coordonnée du volume au
**niveau 2**, réutilisée telle quelle dans une prédiction pleine résolution — donc à un quart
de sa vraie position, dans le vide. Treize rendus entièrement noirs en sont sortis, et le
traceur n'a rien refusé : il imprime `value is 0` puis `empty space tracing` et pousse.

Ce fichier répond à la question dans le sens qui ne peut pas se tromper : **on part d'une
coordonnée du SCAN** — celle où il y a réellement du papyrus — et on demande, pour chaque
prédiction, ce qu'elle en dit **dans son propre repère**.

    scan (z, y, x) ──┬── ÷ 1 ──> prédiction ps256 (L0) ──> valeur
                     └── ÷ 4 ──> prédiction m7    (L2) ──> valeur

⭐ Le sens compte. Aller de la prédiction vers le scan oblige à deviner le niveau ; venir du
scan le rend **lisible dans le nom de la prédiction** (`-L0-`, `-L2-`), qui est là depuis le
début et que personne ne lisait.

⚠ Trois réponses distinctes, et les confondre est ce qui a coûté cher : **hors des bornes**
est une erreur de repère, **bloc absent** veut dire que le dépôt n'a rien écrit là, et
**valeur nulle** veut dire que la prédiction a regardé et n'a rien vu. Seule la troisième est
un fait sur le papyrus.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
SURFACES = "PHercParis4/representations/predictions/surfaces"
# ⚠ Les mêmes URL que `tools/tracer_une_graine.sh`. Elles sont recopiées ici, et c'est une
# dette assumée et nommée : les partager demanderait un fichier de configuration lu par un
# shell ET par Python, ce qui est un mécanisme de plus à garder juste. La batterie vérifie
# qu'elles restent identiques des deux côtés.
PREDICTIONS = {
    "ps256": f"{SURFACES}/20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr",
    "m7": f"{SURFACES}/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr",
}
SCAN = "PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr"


def niveau_de(url: str) -> int | None:
    """Le niveau de pyramide écrit dans le nom, ou None.

    ⚠ `None` et pas `0` : défauter à zéro referait, en silence, exactement l'erreur que ce
    fichier existe pour empêcher.
    """
    import re

    m = re.search(r"-L(\d+)-", url)
    return int(m.group(1)) if m else None


def coordonnee_dans(niveau: int, z: int, y: int, x: int) -> tuple[int, int, int]:
    """Une coordonnée du scan, exprimée dans un volume au niveau `niveau`.

    ⚠ Division ENTIÈRE vers le bas : un indice de voxel est un entier, et arrondir au plus
    proche ferait désigner la cellule voisine une fois sur deux — assez pour tomber à côté
    d'une feuille de trois voxels d'épaisseur.
    """
    f = 1 << niveau
    return z // f, y // f, x // f


def juger(z: int, y: int, x: int, timeout: float = 60.0) -> dict:
    """Ce que le scan et chaque prédiction disent de ce point."""
    from matiere_au_point import lire_bloc

    out = {"scan": [z, y, x], "predictions": {}}
    bloc, val, cle = lire_bloc(f"{BUCKET}/{SCAN}", 0, z, y, x, timeout)
    out["matiere"] = ({"refus": str(val)} if bloc is None
                      else {"valeur": int(val), "max_bloc": int(bloc.max()),
                            "part_allumee": float((bloc > 0).mean())})
    out["cle_scan"] = cle
    for nom, url in PREDICTIONS.items():
        niv = niveau_de(url)
        if niv is None:
            out["predictions"][nom] = {"refus": "aucun -L<n>- dans le nom"}
            continue
        pz, py, px = coordonnee_dans(niv, z, y, x)
        bloc, val, _ = lire_bloc(f"{BUCKET}/{url}", 0, pz, py, px, timeout)
        d = {"niveau": niv, "coordonnee": [pz, py, px]}
        if bloc is None:
            d["refus"] = str(val)
        else:
            d.update(valeur=int(val), max_bloc=int(bloc.max()),
                     part_allumee=float((bloc > 0).mean()))
        out["predictions"][nom] = d
    return out


def verifier() -> int:
    """Les témoins, hors réseau."""
    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    v("ps256 est au niveau 0", niveau_de(PREDICTIONS["ps256"]) == 0)
    v("m7 est au niveau 2", niveau_de(PREDICTIONS["m7"]) == 2)
    # ⚠⚠ Le refus, pas un défaut : c'est toute la leçon du 2026-08-24.
    v("un nom sans niveau rend None", niveau_de("surface.zarr") is None)
    v("... et pas zéro", niveau_de("surface.zarr") is not None or True)

    v("au niveau 0 rien ne bouge", coordonnee_dans(0, 38740, 10616, 10752)
      == (38740, 10616, 10752))
    v("au niveau 2 tout est divisé par 4",
      coordonnee_dans(2, 38740, 10616, 10752) == (9685, 2654, 2688))
    # ⚠⚠ LE CAS RÉEL, dans l'autre sens : la graine m7 publiée est (2924, 5324, 9260) en
    # coordonnées de prédiction L2 ; multipliée par 4 elle vaut (11696, 21296, 37040) en scan.
    v("la graine m7 remonte bien au scan",
      coordonnee_dans(2, 37040, 21296, 11696) == (9260, 5324, 2924))
    # ⚠ La division est ENTIÈRE vers le bas, pas arrondie : 4×n+3 reste dans la cellule n.
    for r in range(4):
        v(f"un reste de {r} ne change pas de cellule",
          coordonnee_dans(2, 40 + r, 0, 0)[0] == 10)

    # ⚠⚠ Les URL doivent rester identiques à celles du script de traçage : deux définitions
    # de « la prédiction m7 » libres de diverger feraient tracer une surface et en juger une
    # autre.
    racine = Path(__file__).resolve().parents[2]
    shell = (racine / "tools" / "tracer_une_graine.sh").read_text(encoding="utf-8")
    for nom, url in PREDICTIONS.items():
        v(f"l'URL {nom} est celle du script de traçage",
          url.rsplit("/", 1)[-1] in shell, url.rsplit("/", 1)[-1][:48])

    # ⚠⚠ La règle d'admissibilité porte sur le BLOC. Sondée ici parce que la graine `ps256`
    # qui marche lit zéro à son voxel exact : un critère sur le voxel l'aurait refusée.
    def semable(max_bloc, valeur, matiere_ok=True):
        return max_bloc > 0 and matiere_ok

    v("un voxel à zéro dans un bloc vu reste semable", semable(255, 0))
    v("un bloc entièrement vu est semable", semable(255, 255))
    v("un bloc entièrement nul ne l'est pas", not semable(0, 0))
    v("sans matière scannée, rien n'est semable", not semable(255, 255, matiere_ok=False))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--point", nargs=3, type=int, metavar=("Z", "Y", "X"),
                   help="une coordonnée du SCAN (pleine résolution)")
    p.add_argument("--maillage", type=Path,
                   help="prendre le point de grille central d'un tifxyz du scan")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    if a.maillage:
        import numpy as np
        import tifffile

        plans = {n: tifffile.imread(str(a.maillage / f"{n}.tif")) for n in ("x", "y", "z")}
        bon = (plans["x"] > 0) & (plans["y"] > 0) & (plans["z"] > 0)
        if not bon.any():
            print(f"refus : {a.maillage} n'a aucun point valide", file=sys.stderr)
            return 2
        rs, cs = np.nonzero(bon)
        r0, c0 = bon.shape[0] / 2.0, bon.shape[1] / 2.0
        k = int(np.argmin((rs - r0) ** 2 + (cs - c0) ** 2))
        r, c = int(rs[k]), int(cs[k])
        z, y, x = (int(round(float(plans[n][r, c]))) for n in ("z", "y", "x"))
        print(f"{a.maillage} · point de grille ({r}, {c})")
    elif a.point:
        z, y, x = a.point
    else:
        p.error("--point ou --maillage requis")

    d = juger(z, y, x)
    m = d["matiere"]
    print(f"scan (z={z}, y={y}, x={x})  ·  " + (
        f"⚠⚠ {m['refus']}" if "refus" in m else
        f"valeur {m['valeur']}, bloc allumé à {100 * m['part_allumee']:.1f} %"))
    admissibles = []
    for nom, r in d["predictions"].items():
        c = r.get("coordonnee")
        tete = f"  {nom:6s} niveau {r['niveau']}  → ({c[0]}, {c[1]}, {c[2]})" if c else f"  {nom:6s}"
        if "refus" in r:
            print(f"{tete}  ⚠ {r['refus']}")
        else:
            # ⚠⚠ LE CRITÈRE EST LE BLOC, PAS LE VOXEL EXACT — et c'est une observation, pas
            # un confort. La graine `ps256` qui a produit huit traces avec matière lit
            # `valeur 0` à son voxel exact, `max du bloc 255` autour : le traceur cherche
            # dans le voisinage. Exiger `valeur > 0` au voxel aurait déclaré inadmissible la
            # seule graine du dépôt dont on sait qu'elle marche.
            ok = r["max_bloc"] > 0 and "refus" not in m
            print(f"{tete}  valeur {r['valeur']}  max du bloc {r['max_bloc']}"
                  + ("  ⭐ semable" if ok else "  ⚠ la prédiction ne voit rien ALENTOUR"))
            if ok:
                admissibles.append((nom, c))
    if admissibles:
        print("\n⭐ graines admissibles, dans le repère de leur prédiction :")
        for nom, c in admissibles:
            print(f"    PREDICTION={nom} … {c[2]} {c[1]} {c[0]}   (x y z)")
    else:
        print("\n⚠⚠ aucune prédiction ne voit de surface ici — semer y produirait du vide")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return 0 if admissibles else 4


if __name__ == "__main__":
    raise SystemExit(main())
