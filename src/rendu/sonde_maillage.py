#!/usr/bin/env python3
"""P0 — la sonde. Ce qu'un chunk de rouleau donne REELLEMENT a un mailleur.

Trois questions, dans l'ordre ou elles commandent la suite :
  1. combien de faces une isosurface emet vraiment (pas le pire cas theorique) ;
  2. les feuilles restent-elles des composantes SEPAREES quand on monte les niveaux ;
  3. a quoi ca ressemble (une coupe en PPM).
"""
import subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
# ⚠ Une seule definition de `faces` et `composantes` dans le depot, testee.
from topologie_du_volume import composantes, faces  # noqa: E402

B = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
V = "PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr"
CH = 128
SEUIL = {0: 128, 1: 130, 2: 132, 3: 134, 4: 135, 5: 136}   # mesure appariee
# chunks couvrant la meme region physique (ancre : chunk (10,3,4) du niveau 2)
ANCRE = {0: (40, 12, 16), 1: (20, 6, 8), 2: (10, 3, 4), 3: (5, 1, 2), 4: (2, 0, 1), 5: (1, 0, 0)}

def chunk(level, zyx):
    import numcodecs
    r = subprocess.run(["curl", "-s", "--fail", "--max-time", "90",
                        f"{B}/{V}/{level}/{zyx[0]}/{zyx[1]}/{zyx[2]}"], capture_output=True)
    if r.returncode != 0:
        return None
    return np.frombuffer(numcodecs.Blosc().decode(r.stdout), dtype=np.uint8).reshape(CH, CH, CH)

print(f"{'niv':>3} {'seuil':>5} {'cote':>4} {'matiere':>8} {'faces':>10} {'f/voxel':>8} "
      f"{'comp>=64':>9} {'plus grosse':>12}")
print("-" * 70)
for lv in range(6):
    a = chunk(lv, ANCRE[lv])
    if a is None:
        print(f"{lv:>3}  absent"); continue
    solid = a > SEUIL[lv]
    f = faces(solid)
    c = composantes(solid)
    print(f"{lv:>3} {SEUIL[lv]:>5} {CH:>4} {solid.mean()*100:7.1f}% {f:10d} "
          f"{f/solid.size:8.4f} {c['grandes']:9d} "
          f"{c['part_de_la_plus_grosse']*100:11.1f}%")

# la coupe, pour regarder
a = chunk(2, ANCRE[2])
if a is not None:
    sl = a[CH // 2]
    with open(f"{sys.argv[1] if len(sys.argv)>1 else '/tmp/coupe.ppm'}", "wb") as fh:
        fh.write(b"P5\n%d %d\n255\n" % (CH, CH))
        fh.write(sl.tobytes())
    print(f"\ncoupe niveau 2 ecrite ({CH}x{CH}, PGM 8 bits)")
