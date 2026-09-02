#!/usr/bin/env python3
"""Le rouleau ENTIER au niveau 5 (253 um) : 36 chunks, ~37 Mo. On regarde avant de mailler.

⚠ La sonde precedente portait sur UNE region, au milieu, et y a trouve 78 % de matiere en UNE
seule composante. Conclure « le rouleau est un bloc » depuis un chunk serait exactement l'erreur
que ce depot recense : mesurer un coin et parler du tout.
"""
import concurrent.futures as cf, subprocess, sys
import numpy as np

B = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
V = "PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr"
CH, LV = 128, 5
SHAPE = (656, 209, 284)
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/rouleau_n5.npy"

def one(key):
    import numcodecs
    z, y, x = key
    r = subprocess.run(["curl", "-s", "--fail", "--max-time", "90",
                        f"{B}/{V}/{LV}/{z}/{y}/{x}"], capture_output=True)
    if r.returncode != 0:
        return key, None
    return key, np.frombuffer(numcodecs.Blosc().decode(r.stdout), dtype=np.uint8).reshape(CH, CH, CH)

grid = [(z, y, x)
        for z in range((SHAPE[0] + CH - 1) // CH)
        for y in range((SHAPE[1] + CH - 1) // CH)
        for x in range((SHAPE[2] + CH - 1) // CH)]
vol = np.zeros(SHAPE, dtype=np.uint8)
absents = 0
with cf.ThreadPoolExecutor(16) as ex:
    for (z, y, x), a in ex.map(one, grid):
        if a is None:
            absents += 1
            continue
        z0, y0, x0 = z * CH, y * CH, x * CH
        zs, ys, xs = (min(CH, SHAPE[i] - o) for i, o in enumerate((z0, y0, x0)))
        vol[z0:z0 + zs, y0:y0 + ys, x0:x0 + xs] = a[:zs, :ys, :xs]
np.save(OUT, vol)
print(f"{len(grid)} chunks, {absents} absents -> {OUT}  ({vol.nbytes/1e6:.1f} Mo)")

nz = vol[vol > 0]
print(f"\nvide (0)        : {(vol == 0).mean()*100:5.1f} %   <- le masque, hors du rouleau")
print(f"non nul         : {nz.size/1e6:.1f} M voxels, moyenne {nz.mean():.1f}, ecart-type {nz.std():.1f}")
print("\nhistogramme des voxels NON NULS (16 paniers) :")
h, edges = np.histogram(nz, bins=16, range=(1, 256))
for i, c in enumerate(h):
    bar = "#" * int(60 * c / h.max())
    print(f"  {int(edges[i]):3d}-{int(edges[i+1]):3d} {c/nz.size*100:5.1f}% {bar}")

print("\nune coupe transverse au milieu de l'axe (z), en PGM :")
mid = vol[SHAPE[0] // 2]
with open(OUT.replace(".npy", "_coupe.pgm"), "wb") as fh:
    fh.write(b"P5\n%d %d\n255\n" % (mid.shape[1], mid.shape[0]))
    fh.write(np.ascontiguousarray(mid).tobytes())
print(f"  {OUT.replace('.npy', '_coupe.pgm')}  ({mid.shape[1]}x{mid.shape[0]})")

print("\nprofil radial : on cherche ou le rouleau est SERRE et ou il est LACHE")
cz = mid  # (y, x)
yy, xx = np.nonzero(cz > 0)
cy, cx = yy.mean(), xx.mean()
r = np.hypot(yy - cy, xx - cx)
print(f"  centre approx ({cy:.0f}, {cx:.0f}), rayon max {r.max():.0f} voxels "
      f"= {r.max()*253.1/1000:.1f} mm")
for lo in range(0, int(r.max()), 10):
    m = (r >= lo) & (r < lo + 10)
    if m.sum() < 20:
        continue
    v = cz[yy[m], xx[m]]
    print(f"  r {lo:3d}-{lo+10:3d} vox : {m.sum():6d} pts, moyenne {v.mean():6.1f}, "
          f"ecart-type {v.std():5.1f}")
