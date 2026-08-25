#!/usr/bin/env python3
"""Lire une RÉGION d'un zarr posé sur le disque — la moitié lecture de `fetch_zarr_boite.py`.

⚠⚠ POURQUOI CE FICHIER EXISTE. `src/outils/fetch_zarr_boite.py` écrit une boîte de chunks en
gardant la forme et les coordonnées du tableau d'origine, et **rien dans ce dépôt ne savait la
relire**. Un écrivain sans lecteur, c'est un artefact qu'on regénère sans jamais s'en servir ;
le dépôt a déjà payé cette forme-là ailleurs.

⭐ Ce que la boîte garantit et qui rend ce lecteur simple : hors de la boîte, un chunk est
**absent**, et un chunk absent vaut la valeur de remplissage. Donc « je lis une région plus
grande que ce que j'ai téléchargé » rend du vide et **jamais une erreur** — c'est le
comportement voulu, mais il faut le savoir avant de conclure qu'une région est vide dans le
rouleau. `chunks_absents` le compte, pour que la différence soit lisible.

⚠⚠ LE NIVEAU EST UN ARGUMENT ET N'A PAS DE DÉFAUT. Une coordonnée de niveau 2 lue au niveau 0
désigne un point quatre fois plus proche de l'origine — dans le vide. C'est ce qui a produit
treize rendus entièrement noirs (`54`), et le remède n'est pas de mieux se souvenir : c'est que
le niveau soit nommé à chaque appel.

⚠ L'ordre des axes est `(z, y, x)`, **vérifié contre la forme déclarée** plutôt que supposé.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]


def meta_locale(racine: Path, niveau: int) -> dict:
    """Le `.zarray` du niveau demandé, avec ses champs indispensables vérifiés."""
    f = racine / str(niveau) / ".zarray"
    if not f.is_file():
        raise FileNotFoundError(f"{f} — ce niveau n'est pas dans la boîte")
    m = json.loads(f.read_text(encoding="utf-8"))
    for cle in ("shape", "chunks", "dtype"):
        if cle not in m:
            raise ValueError(f"{f} ne déclare pas « {cle} »")
    if len(m["shape"]) != 3 or len(m["chunks"]) != 3:
        raise ValueError(f"{f} : ce lecteur ne lit que des tableaux à trois axes")
    return m


def lire_region(racine: Path, niveau: int, bas, haut):
    """Le sous-tableau `[z0:z1, y0:y1, x0:x1]` du niveau demandé, en `(z, y, x)`.

    ⚠⚠ Les bornes sont **écrêtées au tableau**, pas refusées : une nappe qui déborde du scan
    est un fait courant ici, et refuser rendrait ce lecteur inutilisable sur le cas normal. Ce
    qui serait faux, c'est de le taire — d'où `hors_volume` dans le rapport.
    """
    import numpy as np
    import zarr_depth as zd

    m = meta_locale(racine, niveau)
    forme = tuple(int(v) for v in m["shape"])
    cformes = tuple(int(v) for v in m["chunks"])
    b = [max(0, int(bas[i])) for i in range(3)]
    h = [min(forme[i], int(haut[i])) for i in range(3)]
    hors = any(int(bas[i]) < 0 or int(haut[i]) > forme[i] for i in range(3))
    if any(h[i] <= b[i] for i in range(3)):
        raise ValueError(f"région vide après écrêtage : {list(bas)} → {list(haut)} "
                         f"dans un tableau {forme}")

    dt = np.dtype(m["dtype"])
    out = np.zeros([h[i] - b[i] for i in range(3)], dtype=dt)
    absents = presents = 0
    sep = m.get("dimension_separator", ".")
    attendu = cformes[0] * cformes[1] * cformes[2] * dt.itemsize
    plages = [range(b[i] // cformes[i], (h[i] - 1) // cformes[i] + 1) for i in range(3)]
    for cz in plages[0]:
        for cy in plages[1]:
            for cx in plages[2]:
                f = racine / str(niveau) / sep.join((str(cz), str(cy), str(cx)))
                if not f.is_file():
                    absents += 1
                    continue
                brut = zd.decode(f.read_bytes(), m, attendu)
                if brut is None:
                    absents += 1
                    continue
                presents += 1
                bloc = np.frombuffer(brut, dtype=dt).reshape(cformes)
                deb = [cz * cformes[0], cy * cformes[1], cx * cformes[2]]
                # L'intersection du chunk et de la région demandée, dans les deux repères.
                d = [max(b[i], deb[i]) for i in range(3)]
                fin = [min(h[i], deb[i] + cformes[i]) for i in range(3)]
                out[d[0] - b[0]:fin[0] - b[0], d[1] - b[1]:fin[1] - b[1],
                    d[2] - b[2]:fin[2] - b[2]] = \
                    bloc[d[0] - deb[0]:fin[0] - deb[0], d[1] - deb[1]:fin[1] - deb[1],
                         d[2] - deb[2]:fin[2] - deb[2]]
    return out, {"origine": b, "forme_lue": list(out.shape), "forme_tableau": list(forme),
                 "chunks_presents": presents, "chunks_absents": absents,
                 "hors_volume": bool(hors), "niveau": niveau}


def verifier() -> int:
    """Les témoins, sur une boîte fabriquée dont on connaît chaque voxel."""
    import shutil
    import tempfile

    import numpy as np

    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    racine = Path(tempfile.mkdtemp(prefix="region_temoins_"))
    n, c = 8, 4                    # tableau 8³, chunks 4³ → 2×2×2 chunks
    d = racine / "0"
    d.mkdir(parents=True)
    (d / ".zarray").write_text(json.dumps(
        {"shape": [n, n, n], "chunks": [c, c, c], "dtype": "|u1", "compressor": None,
         "fill_value": 0, "dimension_separator": "/"}), encoding="utf-8")
    # Chaque voxel porte une valeur qui NOMME sa position : un décalage d'index se voit.
    plein = np.zeros((n, n, n), dtype=np.uint8)
    for z in range(n):
        for y in range(n):
            for x in range(n):
                plein[z, y, x] = (z * 16 + y * 4 + x) % 251 + 1
    # ⚠ Un chunk est délibérément ABSENT — c'est le cas courant d'une boîte partielle, et le
    # lecteur doit rendre du vide sans se plaindre, en le comptant.
    for cz in range(2):
        for cy in range(2):
            for cx in range(2):
                if (cz, cy, cx) == (1, 1, 1):
                    continue
                bloc = plein[cz * c:(cz + 1) * c, cy * c:(cy + 1) * c, cx * c:(cx + 1) * c]
                (d / f"{cz}/{cy}").mkdir(parents=True, exist_ok=True)
                (d / f"{cz}/{cy}/{cx}").write_bytes(bloc.tobytes())

    a, r = lire_region(racine, 0, (0, 0, 0), (n, n, n))
    v("la région a la forme demandée", a.shape == (n, n, n), str(a.shape))
    v("sept chunks sont présents", r["chunks_presents"] == 7, str(r["chunks_presents"]))
    v("... et un est compté absent", r["chunks_absents"] == 1)
    # ⚠⚠ LE CONTRÔLE QUI PORTE LE LECTEUR : la valeur relue est celle de CE voxel, donc un
    # décalage d'axe ou de chunk se voit. Une comparaison de formes ne l'aurait pas vu.
    v("chaque voxel présent revient à sa place",
      bool((a[:4, :4, :4] == plein[:4, :4, :4]).all()))
    v("... y compris dans un chunk non nul en z", bool((a[4:, :4, :4] == plein[4:, :4, :4]).all()))
    v("le chunk absent est du vide, pas une erreur", int(a[4:, 4:, 4:].max()) == 0)

    # Une sous-région à cheval sur quatre chunks.
    a2, r2 = lire_region(racine, 0, (2, 2, 2), (6, 6, 6))
    v("une sous-région a la forme demandée", a2.shape == (4, 4, 4), str(a2.shape))
    # ⚠⚠ Mon premier contrôle comparait TOUTE la sous-région au tableau et échouait — à
    # raison : elle chevauche le chunk (1,1,1) volontairement absent, dont le lecteur rend du
    # vide. C'était le TEST qui avait tort. Comparer la part couverte, et asserter à part que
    # la part manquante est vide, dit d'ailleurs plus que l'égalité globale.
    v("... et ses valeurs couvertes sont celles du tableau",
      bool((a2[:2, :2, :2] == plein[2:4, 2:4, 2:4]).all()))
    v("... la part du chunk absent est vide", int(a2[2:, 2:, 2:].max()) == 0)
    v("... et une part couverte hors de ce coin l'est aussi",
      bool((a2[2:, :2, :2] == plein[4:6, 2:4, 2:4]).all()))
    v("... son origine est rapportée", r2["origine"] == [2, 2, 2])

    # ⚠ Les bornes sont ÉCRÊTÉES, pas refusées — une nappe qui déborde du scan est courant.
    a3, r3 = lire_region(racine, 0, (-4, 0, 0), (n + 4, 4, 4))
    v("une région qui déborde est écrêtée", a3.shape == (n, 4, 4), str(a3.shape))
    v("... et le débordement est DIT", r3["hors_volume"] is True)
    v("une région entièrement dedans ne le dit pas", r["hors_volume"] is False)

    try:
        lire_region(racine, 0, (n + 1, 0, 0), (n + 2, 4, 4))
        v("une région entièrement hors du tableau est refusée", False)
    except ValueError:
        v("une région entièrement hors du tableau est refusée", True)
    try:
        lire_region(racine, 2, (0, 0, 0), (4, 4, 4))
        v("un niveau absent est refusé", False)
    except FileNotFoundError:
        v("un niveau absent est refusé", True)

    # ⚠ Le séparateur est celui que le tableau DÉCLARE. Le coder en dur ne lève pas : ça
    # rend des chunks « absents », donc une région pleine passerait pour du vide.
    d2 = racine / "1"
    d2.mkdir()
    (d2 / ".zarray").write_text(json.dumps(
        {"shape": [c, c, c], "chunks": [c, c, c], "dtype": "|u1", "compressor": None,
         "fill_value": 0, "dimension_separator": "."}), encoding="utf-8")
    (d2 / "0.0.0").write_bytes(plein[:c, :c, :c].tobytes())
    a4, r4 = lire_region(racine, 1, (0, 0, 0), (c, c, c))
    v("le séparateur déclaré « . » est respecté", r4["chunks_presents"] == 1)
    v("... et les valeurs sont là", bool((a4 == plein[:c, :c, :c]).all()))

    # Un `.zarray` incomplet est refusé plutôt que défauté.
    (racine / "3").mkdir()
    (racine / "3" / ".zarray").write_text(json.dumps({"shape": [4, 4, 4]}), encoding="utf-8")
    try:
        meta_locale(racine, 3)
        v("un .zarray sans chunks est refusé", False)
    except ValueError:
        v("un .zarray sans chunks est refusé", True)

    shutil.rmtree(racine, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("racine", nargs="?", type=Path, help="le dossier .zarr local")
    p.add_argument("--niveau", type=int, help="OBLIGATOIRE — sans défaut, exprès")
    p.add_argument("--boite", type=int, nargs=6, metavar=("Z0", "Z1", "Y0", "Y1", "X0", "X1"))
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.racine or a.niveau is None or not a.boite:
        p.error("racine, --niveau et --boite sont requis")
    bloc, r = lire_region(a.racine, a.niveau, a.boite[0::2], a.boite[1::2])
    nz = int((bloc > 0).sum())
    print(f"{a.racine.name} niveau {a.niveau}  ·  forme {r['forme_lue']}  ·  "
          f"origine {r['origine']}")
    print(f"  chunks   {r['chunks_presents']} présents, {r['chunks_absents']} absents"
          + ("  ⚠ la région déborde du tableau" if r["hors_volume"] else ""))
    print(f"  matière  {nz} voxels non nuls sur {bloc.size} "
          f"({100.0 * nz / bloc.size:.2f} %)  ·  max {int(bloc.max())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
