#!/usr/bin/env python3
"""P0 — la sonde. Ce qu'un chunk de rouleau donne REELLEMENT a un mailleur.

Trois questions, dans l'ordre ou elles commandent la suite :
  1. combien de faces une isosurface emet vraiment (pas le pire cas theorique) ;
  2. les feuilles restent-elles des composantes SEPAREES quand on monte les niveaux ;
  3. a quoi ca ressemble (une coupe en PPM).
"""
import subprocess, sys
import numpy as np

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

def faces(solid):
    """Faces emises : une par paire (plein, vide) adjacente. C'est exactement ce que
    forEachVoxelFace compte, et c'est SANS les faces interieures."""
    n = 0
    for ax in range(3):
        a = np.moveaxis(solid, ax, 0)
        n += int(np.count_nonzero(a[:-1] != a[1:]))          # interfaces internes
        n += int(np.count_nonzero(a[0])) + int(np.count_nonzero(a[-1]))  # bords du chunk
    return n

def composantes(solid, mini=64):
    """Nombre de composantes connexes de MATIERE (6-connexite), au-dessus de `mini` voxels.
    Union-find sur les voisins -x/-y/-z : une seule passe, pas de recursion."""
    idx = -np.ones(solid.shape, dtype=np.int32)
    flat = np.flatnonzero(solid.ravel())
    idx.ravel()[flat] = np.arange(flat.size, dtype=np.int32)
    parent = np.arange(flat.size, dtype=np.int32)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for ax in range(3):
        a = np.moveaxis(idx, ax, 0)
        lo, hi = a[:-1], a[1:]
        m = (lo >= 0) & (hi >= 0)
        for u, v in zip(lo[m], hi[m]):
            union(int(u), int(v))
    racines = np.array([find(i) for i in range(flat.size)], dtype=np.int32)
    _, tailles = np.unique(racines, return_counts=True)
    return int((tailles >= mini).sum()), int(tailles.max()) if tailles.size else 0, int(tailles.size)

print(f"{'niv':>3} {'seuil':>5} {'cote':>4} {'matiere':>8} {'faces':>10} {'f/voxel':>8} "
      f"{'comp>=64':>9} {'plus grosse':>12}")
print("-" * 70)
for lv in range(6):
    a = chunk(lv, ANCRE[lv])
    if a is None:
        print(f"{lv:>3}  absent"); continue
    solid = a > SEUIL[lv]
    f = faces(solid)
    nc, big, tot = composantes(solid)
    print(f"{lv:>3} {SEUIL[lv]:>5} {CH:>4} {solid.mean()*100:7.1f}% {f:10d} "
          f"{f/solid.size:8.4f} {nc:9d} {big/max(solid.sum(),1)*100:11.1f}%")

# la coupe, pour regarder
a = chunk(2, ANCRE[2])
if a is not None:
    sl = a[CH // 2]
    with open(f"{sys.argv[1] if len(sys.argv)>1 else '/tmp/coupe.ppm'}", "wb") as fh:
        fh.write(b"P5\n%d %d\n255\n" % (CH, CH))
        fh.write(sl.tobytes())
    print(f"\ncoupe niveau 2 ecrite ({CH}x{CH}, PGM 8 bits)")
