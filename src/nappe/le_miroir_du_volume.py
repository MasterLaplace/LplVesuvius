"""Le miroir local du volume brut : les seuls chunks qu'un rendu lit, téléchargés une fois.

⚠⚠ POURQUOI CE FICHIER EXISTE. `vc_render_tifxyz` lit le volume brut de PHercParis4 sur S3, chunk par chunk, sans cache
disque (le dossier passé à `-v` reste vide, `50` l'avait vu). Le 2026-09-25, un bloc de 16 × 16 chunks rendu à distance
tirait environ 6 Go du réseau pour les 891 chunks de 2 Mo qu'il lit réellement, et la liaison plafonnait vers 30 Mo/s
quel que soit le nombre de rendus parallèles, 4 ou 8. Le même bloc rendu depuis un miroir local de ces 891 chunks sort en
24 s, identique voxel pour voxel au rendu à distance.

Les chunks qu'un rendu lit se déduisent de sa surface : chaque point du cadre, porté le long de sa normale sur les couches
rendues, avec une marge. ⚠ Un chunk manquant dans le miroir se lit comme du vide, sans erreur : la marge est donc large, et le
miroir n'est tenu pour juste que là où un rendu depuis lui égale un rendu à distance.

Usage :
    uv run python src/nappe/le_miroir_du_volume.py --verifier
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_spire_produite_se_lit_elle_dans_le_treillis import (LE_DOSSIER,  # noqa: E402
                                                            LE_VOLUME_BRUT)

LE_MIROIR = LE_DOSSIER / "le_miroir"
LE_CHUNK_DU_VOLUME = 128
LES_METAS = (".zgroup", ".zattrs", "0/.zarray", "0/.zattrs")
LA_DEMI_EPAISSEUR = 54   # les 109 couches du rendu, de part et d'autre de la surface
LA_MARGE = 32            # voxels, dans chaque direction, autour de chaque point porté


def les_chunks_dun_cadre(points: np.ndarray, grille: float, cadre: dict, demi: int = LA_DEMI_EPAISSEUR,
                         marge: int = LA_MARGE, pas: int = 16, pas_des_couches: int = 6) -> set[tuple[int, int, int]]:
    """Les chunks `(z, y, x)` du volume que le rendu du cadre lit : les points de la surface, bilinéaires entre ceux de la
    grille, tous les `pas` pixels, portés le long de la normale de `-demi` à `demi`, chacun avec une marge de `marge`
    voxels sur chaque axe.

    `points` est la grille tifxyz `(h, w, 3)` en `(x, y, z)`, `grille` son espacement en pixels du rendu.
    """
    s = 1.0 / float(grille)
    u = np.arange(cadre["x"], cadre["x"] + cadre["largeur"] + 1, pas) * s
    v = np.arange(cadre["y"], cadre["y"] + cadre["hauteur"] + 1, pas) * s
    V, U = np.meshgrid(v, u, indexing="ij")
    i0 = np.clip(np.floor(V).astype(int), 0, points.shape[0] - 2)
    j0 = np.clip(np.floor(U).astype(int), 0, points.shape[1] - 2)
    fv, fu = (V - i0)[..., None], (U - j0)[..., None]

    def bil(a):
        return ((1 - fv) * (1 - fu) * a[i0, j0] + (1 - fv) * fu * a[i0, j0 + 1]
                + fv * (1 - fu) * a[i0 + 1, j0] + fv * fu * a[i0 + 1, j0 + 1])

    p = bil(points)
    n = np.cross(bil(np.gradient(points, axis=1)), bil(np.gradient(points, axis=0)))
    with np.errstate(invalid="ignore", divide="ignore"):
        n = n / np.linalg.norm(n, axis=-1, keepdims=True)
    bon = np.isfinite(p).all(axis=-1) & np.isfinite(n).all(axis=-1) & (p > -1.0).all(axis=-1)
    p, n = p[bon], n[bon]
    out: set[tuple[int, int, int]] = set()
    decalages = np.array([[dx, dy, dz] for dx in (-marge, marge) for dy in (-marge, marge) for dz in (-marge, marge)])
    for k in list(range(-demi, demi + 1, pas_des_couches)) + [demi]:
        q = p + k * n
        for d in decalages:
            c = np.floor((q + d) / LE_CHUNK_DU_VOLUME).astype(int)
            out.update(map(tuple, c[:, ::-1].tolist()))
    return {c for c in out if min(c) >= 0}


def le_fichier(c: tuple[int, int, int], miroir: Path = LE_MIROIR) -> Path:
    return miroir / "0" / str(c[0]) / str(c[1]) / str(c[2])


def telecharger(url: str) -> bytes | None:
    """Les octets d'un objet, ou None s'il n'existe pas : un chunk absent de S3 est un chunk vide, au sens de zarr."""
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            return None
        raise


def preparer(miroir: Path = LE_MIROIR, source: str = LE_VOLUME_BRUT, lire=telecharger) -> None:
    """Les métadonnées du volume, recopiées telles quelles : c'est ce qui fait du dossier un volume que le rendu ouvre."""
    for f in LES_METAS:
        p = miroir / f
        if not p.is_file():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(lire(f"{source}/{f}"))


def remplir(chunks: set, miroir: Path = LE_MIROIR, source: str = LE_VOLUME_BRUT, ouvriers: int = 32,
            lire=telecharger) -> dict:
    """Les chunks qui manquent au miroir, téléchargés ; un chunk déjà là n'est pas refait.

    ⚠ L'écriture passe par un fichier temporaire renommé : un téléchargement coupé ne laisse jamais un chunk tronqué, qui se
    lirait comme un chunk complet.
    """
    preparer(miroir, source, lire)
    manquants = sorted(c for c in chunks if not le_fichier(c, miroir).is_file()
                       and not le_fichier(c, miroir).with_suffix(".vide").is_file())
    debut = time.monotonic()

    def un(c):
        data = lire(f"{source}/0/{c[0]}/{c[1]}/{c[2]}")
        f = le_fichier(c, miroir)
        f.parent.mkdir(parents=True, exist_ok=True)
        if data is None:
            f.with_suffix(".vide").write_text("absent de la source\n")
            return 0
        tmp = f.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(f)
        return len(data)

    with ThreadPoolExecutor(max_workers=int(ouvriers)) as pool:
        tailles = list(pool.map(un, manquants))
    s = time.monotonic() - debut
    return {"les_chunks": len(chunks), "telecharges": len(manquants), "absents_de_la_source": tailles.count(0),
            "les_octets": int(sum(tailles)), "les_secondes": round(s, 1),
            "le_debit_mo_s": round(sum(tailles) / 1e6 / s, 1) if s > 0 and manquants else None}


def vider(garder: set, miroir: Path = LE_MIROIR) -> int:
    """Les chunks du miroir que plus rien ne demande, retirés. Rend combien."""
    racine = miroir / "0"
    if not racine.is_dir():
        return 0
    n = 0
    for f in racine.glob("*/*/*"):
        if f.suffix in (".tmp",) or f.name.startswith("."):
            continue
        c = (int(f.parent.parent.name), int(f.parent.name), int(f.name.split(".")[0]))
        if c not in garder:
            f.unlink()
            n += 1
    return n


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────────

def verifier() -> int:
    import tempfile

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # Un plan à z = 500, grille de 10 × 10 points espacés de 160 pixels, x et y en voxels égaux aux pixels.
    jj, ii = np.meshgrid(np.arange(10), np.arange(10))
    plan = np.stack([jj * 160.0, ii * 160.0, np.full(jj.shape, 500.0)], axis=-1)
    cadre = {"x": 256, "y": 256, "largeur": 512, "hauteur": 512}
    lu = les_chunks_dun_cadre(plan, 160.0, cadre)
    zs = {c[0] for c in lu}
    attendu_z = set(range((500 - 54 - 32) // 128, (500 + 54 + 32) // 128 + 1))
    attendu_xy = set(range((256 - 32) // 128, (768 + 32) // 128 + 1))
    v("★★★★ sur un plan, les chunks sont le cadre et l'épaisseur rendue, marge comprise, ni plus ni moins",
      zs == attendu_z and {c[2] for c in lu} == attendu_xy and {c[1] for c in lu} == attendu_xy
      and len(lu) == len(attendu_z) * len(attendu_xy) ** 2, str((sorted(zs), sorted({c[2] for c in lu}))))
    v("★★★ sans marge, le cadre seul : la marge est bien ce qui l'élargit",
      {c[2] for c in les_chunks_dun_cadre(plan, 160.0, cadre, marge=0)} == set(range(256 // 128, 768 // 128 + 1)))
    haut = plan.copy()
    haut[..., 2] = 460.0
    v("★★★ sans marge, toute l'épaisseur rendue compte, la dernière couche comprise",
      {c[0] for c in les_chunks_dun_cadre(haut, 160.0, cadre, marge=0)} == {(460 - 54) // 128, (460 + 54) // 128})
    penche = plan.copy()
    penche[..., 2] = 500.0 + penche[..., 0] * 0.5
    v("★★★ une surface penchée monte dans les chunks qu'elle traverse",
      max(c[0] for c in les_chunks_dun_cadre(penche, 160.0, cadre)) > max(zs))

    with tempfile.TemporaryDirectory() as t:
        m = Path(t) / "m"
        appels = []

        def faux(url):
            appels.append(url)
            if url.endswith("/0/9/9/9"):
                return None
            return b"x" * 7 if "/0/" in url and not url.endswith(("zarray", "zattrs")) else b"{}"

        r1 = remplir({(1, 2, 3), (9, 9, 9)}, miroir=m, source="S", lire=faux)
        n1 = len(appels)
        r2 = remplir({(1, 2, 3), (9, 9, 9)}, miroir=m, source="S", lire=faux)
        v("★★★★ un chunk déjà là n'est pas retéléchargé, un chunk absent de la source non plus",
          r1["telecharges"] == 2 and r2["telecharges"] == 0 and len(appels) == n1 and r1["absents_de_la_source"] == 1)
        v("★★★ le chunk est écrit entier, sans fichier temporaire laissé", le_fichier((1, 2, 3), m).read_bytes() == b"x" * 7
          and not list(m.rglob("*.tmp")))
        v("★★★ les métadonnées du volume sont recopiées", all((m / f).is_file() for f in LES_METAS))
        remplir({(4, 4, 4)}, miroir=m, source="S", lire=faux)
        n = vider({(4, 4, 4)}, miroir=m)
        v("★★★★ vider ne retire que ce qui n'est plus demandé",
          n == 2 and le_fichier((4, 4, 4), m).is_file() and not le_fichier((1, 2, 3), m).is_file()
          and not le_fichier((9, 9, 9), m).with_suffix(".vide").is_file(), str(n))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
