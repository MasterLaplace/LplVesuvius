#!/usr/bin/env python3
"""Ou est la STRUCTURE : la sonde du milieu disait « un bloc », le profil radial dit
« l'ecart-type quintuple au bord ». On va voir au bord, a pleine resolution.

Centre du rouleau, lu au niveau 5 : (y=100, x=134), rayon max 123 vox de 253,1 um.
En voxels du niveau 0 : centre (3200, 4288), rayon max 3936.
"""
import subprocess, sys
import numpy as np

B = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
V = "PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr"
CH = 128
Z0 = 10496            # milieu de l'axe, en voxels du niveau 0
CY, CX = 3200, 4288   # centre du rouleau, en voxels du niveau 0

def chunk(level, z, y, x):
    import numcodecs
    r = subprocess.run(["curl", "-s", "--fail", "--max-time", "90",
                        f"{B}/{V}/{level}/{z}/{y}/{x}"], capture_output=True)
    if r.returncode != 0:
        return None
    return np.frombuffer(numcodecs.Blosc().decode(r.stdout), dtype=np.uint8).reshape(CH, CH, CH)

def composantes(solid, mini=64):
    idx = -np.ones(solid.shape, dtype=np.int32)
    flat = np.flatnonzero(solid.ravel())
    if flat.size == 0:
        return 0, 0
    idx.ravel()[flat] = np.arange(flat.size, dtype=np.int32)
    parent = np.arange(flat.size, dtype=np.int32)
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for ax in range(3):
        a = np.moveaxis(idx, ax, 0)
        lo, hi = a[:-1], a[1:]
        m = (lo >= 0) & (hi >= 0)
        for u, v in zip(lo[m], hi[m]):
            ra, rb = find(int(u)), find(int(v))
            if ra != rb: parent[max(ra, rb)] = min(ra, rb)
    rac = np.array([find(i) for i in range(flat.size)], dtype=np.int32)
    _, t = np.unique(rac, return_counts=True)
    return int((t >= mini).sum()), int(t.max())

def faces(solid):
    n = 0
    for ax in range(3):
        a = np.moveaxis(solid, ax, 0)
        n += int(np.count_nonzero(a[:-1] != a[1:]))
        n += int(np.count_nonzero(a[0])) + int(np.count_nonzero(a[-1]))
    return n

print("rayon parcouru en voxels du niveau 0, plein axe +x depuis le centre\n")
print(f"{'rayon':>6} {'chunk':>14} {'nonzero':>8} {'moy':>6} {'ecart':>6} "
      f"{'p05':>4} {'p50':>4} {'p95':>4} {'bimodal ?':>10}")
print("-" * 78)
retenu = None
for rvox in (0, 1000, 2000, 2600, 3000, 3300, 3600):
    y, x = CY, CX + rvox
    key = (Z0 // CH, y // CH, x // CH)
    a = chunk(0, *key)
    if a is None:
        print(f"{rvox:6d} {str(key):>14}  chunk absent"); continue
    nz = a[a > 0]
    if nz.size < 1000:
        print(f"{rvox:6d} {str(key):>14}  quasi vide ({nz.size} vox)"); continue
    p05, p50, p95 = np.percentile(nz, (5, 50, 95))
    # bimodalite grossiere : creux entre deux pics dans l'histogramme lisse
    h, _ = np.histogram(nz, bins=64, range=(1, 256))
    hs = np.convolve(h, np.ones(3) / 3, mode="same")
    pics = [i for i in range(1, 63) if hs[i] > hs[i-1] and hs[i] >= hs[i+1] and hs[i] > hs.max() * 0.08]
    print(f"{rvox:6d} {str(key):>14} {nz.size/a.size*100:7.1f}% {nz.mean():6.1f} {nz.std():6.1f} "
          f"{int(p05):4d} {int(p50):4d} {int(p95):4d} {len(pics):>6} pics")
    if rvox >= 2600 and retenu is None and nz.std() > 20:
        retenu = (rvox, key, a)

if retenu is None:
    print("\naucune region a fort ecart-type trouvee sur cet axe")
    sys.exit(0)

rvox, key, a = retenu
print(f"\n=== region retenue : rayon {rvox} vox, chunk {key} du niveau 0 ===")
for seuil in (100, 110, 120, 128, 136, 144):
    solid = a > seuil
    nc, big = composantes(solid)
    print(f"  seuil {seuil:3d} : matiere {solid.mean()*100:5.1f} %  faces {faces(solid):8d}  "
          f"composantes>=64 {nc:4d}  plus grosse {big/max(solid.sum(),1)*100:5.1f} %")

for name, sl in (("xy", a[CH // 2]), ("xz", a[:, CH // 2, :])):
    p = f"{sys.argv[1] if len(sys.argv) > 1 else '/tmp'}/exterieur_{name}.pgm"
    with open(p, "wb") as fh:
        fh.write(b"P5\n%d %d\n255\n" % (sl.shape[1], sl.shape[0]))
        fh.write(np.ascontiguousarray(sl).tobytes())
    print(f"  coupe {name} -> {p}")
