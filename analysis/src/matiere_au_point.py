#!/usr/bin/env python3
"""Y a-t-il de la matière à CETTE coordonnée, dans CE volume, à CE niveau ?

⚠⚠ POURQUOI. Une trace commence par une graine, qui est une coordonnée. Une coordonnée ne
veut rien dire sans le volume qui la numérote, et le 2026-08-24 treize rendus ont été produits
entièrement noirs parce que des coordonnées de **niveau 2** ont été lues au **niveau 0** —
c'est-à-dire au quart de leur vraie position, dans le vide. Rien n'avait posé la question la
plus simple qui soit : *y a-t-il quelque chose là où je regarde ?*

Un seul bloc zarr (128³) suffit à répondre, donc la question coûte une requête et pas un
rendu. ⭐ C'est le contrôle à faire **avant** de payer un tracé, pas après.

⚠ L'ordre des axes est `(z, y, x)` et il est **vérifié contre la forme du tableau** plutôt
que supposé : le volume de `PHercParis4` à 2,4 µm fait `[75784, 32693, 32693]`, donc seul le
premier axe peut porter un z de 73 919. Un ordre supposé lirait un autre endroit du rouleau
et rendrait « pas de matière » avec le même aplomb.

Le lecteur de blocs est celui de `tracecheck/` — importé, jamais recopié. Deux lecteurs de
zarr finiraient par ne pas s'accorder sur le séparateur de clé ou sur le codec, et le mode
d'échec des deux est de rendre « bloc vide » au lieu d'une erreur.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tracecheck"))

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"


def lire_bloc(zarr_url: str, niveau: int, z: int, y: int, x: int, timeout: float = 30.0,
              meta: dict | None = None, cache: dict | None = None):
    """Le bloc zarr contenant `(z, y, x)`, et la valeur exacte du point.

    Rend `(bloc, valeur, cle)` ou `(None, raison, cle)`.

    ⚠⚠ `meta` et `cache` existent pour le BALAYAGE, et pas par élégance. Un bloc fait 128³
    octets, soit 2 Mio, et deux points de grille voisins tombent presque toujours dans le
    même : sans cache, sonder vingt-cinq points d'une nappe télécharge cinquante mégaoctets
    pour lire vingt-cinq octets. Et sans `meta`, chaque sondage redemande le `.zarray`, donc
    paie un aller-retour de plus par point. Mesuré : le premier balayage tournait encore au
    bout de plusieurs minutes.
    """
    import numpy as np
    import tracecheck as tc

    if meta is None:
        meta = tc.array_meta(zarr_url, niveau, timeout)
    forme = meta["shape"]
    tailles = meta["chunks"]
    if len(forme) != 3:
        return None, f"tableau à {len(forme)} axes, attendu 3", ""
    # ⚠⚠ Les bornes AVANT la requête : une coordonnée hors du volume rendrait « bloc
    # manquant », qui se lit comme « rien ici » alors que la vraie réponse est « tu regardes
    # en dehors du scan ». Ce sont deux faits différents et c'est justement leur confusion
    # qui a coûté treize rendus.
    for axe, (v, n) in enumerate(zip((z, y, x), forme)):
        if not (0 <= v < n):
            return None, (f"HORS DU VOLUME : l'axe {axe} vaut {v}, le volume en a {n}"), ""
    cz, cy, cx = z // tailles[0], y // tailles[1], x // tailles[2]
    cle = tc.chunk_key(meta, niveau, cy, cx, cz)
    if cache is not None and cle in cache:
        bloc = cache[cle]
        if bloc is None:
            return None, "bloc absent du dépôt", cle
    else:
        brut = tc.get(f"{zarr_url}/{cle}", timeout)
        if brut is None:
            if cache is not None:
                cache[cle] = None
            return None, "bloc absent du dépôt", cle
        n = tailles[0] * tailles[1] * tailles[2]
        donnees = tc.decode(brut, meta, n)
        if donnees is None:
            return None, "bloc illisible", cle
        bloc = np.frombuffer(donnees, dtype=np.dtype(meta["dtype"])).reshape(tailles)
        if cache is not None:
            cache[cle] = bloc
    valeur = int(bloc[z % tailles[0], y % tailles[1], x % tailles[2]])
    return bloc, valeur, cle


def balayer(maillage: Path, zarr_url: str, niveau: int, combien: int = 25,
            timeout: float = 30.0) -> dict:
    """Combien des points de CE maillage tombent dans de la matière ?

    ⚠⚠ Un seul point ne tranche pas. Une nappe incurvée peut avoir son centre hors du scan
    et ses bords dedans, et un maillage parfaitement posé peut avoir un trou là où on sonde.
    Ce qui répond, c'est la RÉPARTITION : combien de points sur combien, et de quel genre
    est le refus.

    ⚠ Les trois refus sont comptés séparément parce qu'ils disent trois choses différentes :
    **hors du volume** est une erreur de repère, **bloc absent** veut dire que le dépôt n'a
    rien écrit là (donc hors du masque du scan), et **bloc vide** veut dire que le bloc
    existe et ne contient que du noir. Les confondre est exactement ce qui a coûté treize
    rendus.
    """
    import numpy as np
    import tifffile

    plans = {n: tifffile.imread(str(maillage / f"{n}.tif")) for n in ("x", "y", "z")}
    bon = (plans["x"] > 0) & (plans["y"] > 0) & (plans["z"] > 0)
    rs, cs = np.nonzero(bon)
    if len(rs) == 0:
        return {"maillage": str(maillage), "refus": "aucun point valide"}
    import tracecheck as tc

    meta = tc.array_meta(zarr_url, niveau, timeout)
    cache: dict = {}
    pas = max(1, len(rs) // max(1, combien))
    comptes = {"matiere": 0, "bloc_vide": 0, "bloc_absent": 0, "hors_volume": 0,
               "illisible": 0}
    exemples = []
    # ⚠⚠ Les points QUI MARCHENT sont enregistrés aussi, et pas seulement les refus. Un
    # instrument qui ne rapporte que ses échecs dit qu'il y a un problème et pas OÙ regarder
    # — or sur une nappe qui déborde du scan, savoir quelle partie est dedans est
    # exactement ce dont on a besoin pour découper un morceau lisible.
    trouves = []
    for k in range(0, len(rs), pas):
        r, c = int(rs[k]), int(cs[k])
        x, y, z = (int(round(float(plans[n][r, c]))) for n in ("x", "y", "z"))
        bloc, val, _ = lire_bloc(zarr_url, niveau, z, y, x, timeout, meta, cache)
        if bloc is None:
            cle = ("hors_volume" if "HORS DU VOLUME" in str(val)
                   else "illisible" if "illisible" in str(val) else "bloc_absent")
            comptes[cle] += 1
            if len(exemples) < 3:
                exemples.append({"grille": [r, c], "zyx": [z, y, x], "refus": str(val)})
        elif int(bloc.max()) == 0:
            comptes["bloc_vide"] += 1
        else:
            comptes["matiere"] += 1
            trouves.append({"grille": [r, c], "zyx": [z, y, x], "max_bloc": int(bloc.max())})
    total = sum(comptes.values())
    return {"maillage": str(maillage), "niveau": niveau, "sondes": total,
            "blocs_distincts": len(cache), "comptes": comptes, "exemples": exemples,
            "avec_matiere": trouves,
            "part_matiere": comptes["matiere"] / total if total else None}


def verifier() -> int:
    """Les témoins, hors ligne : la géométrie de blocs et les refus.

    ⚠ Ce qui est vérifié ici est **l'arithmétique**, pas le réseau. Une batterie qui
    dépendrait du dépôt serait rouge chaque fois que la connexion tombe, donc elle finirait
    par être ignorée — et c'est là qu'elle cesse d'être une batterie.
    """
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {detail}" if detail else ""))

    import tracecheck as tc

    meta = {"shape": [75784, 32693, 32693], "chunks": [128, 128, 128],
            "dtype": "|u1", "dimension_separator": "/"}
    v("la clé de bloc suit l'ordre z/y/x",
      tc.chunk_key(meta, 0, 90, 109, 229) == "0/229/90/109",
      tc.chunk_key(meta, 0, 90, 109, 229))
    # ⚠ Le séparateur est celui que le tableau DÉCLARE, jamais '/' en dur.
    v("un séparateur '.' est respecté",
      tc.chunk_key({**meta, "dimension_separator": "."}, 0, 1, 2, 3) == "0/3.1.2")

    # ⚠⚠ La PROPRIÉTÉ plutôt qu'une paire de nombres tapés à la main. Ma première version
    # écrivait le reste de tête et se trompait — troisième attendu faux de la journée. Un
    # attendu tapé est une seconde implémentation, et elle peut être la fausse des deux ;
    # « index de bloc fois taille plus reste redonne la coordonnée » ne se tape pas.
    for coord in (29438, 11637, 0, 127, 128, 75783):
        v(f"le découpage en blocs est exact pour {coord}",
          (coord // 128) * 128 + (coord % 128) == coord)
        v(f"... et le reste de {coord} est dans le bloc", 0 <= coord % 128 < 128)

    # ⚠⚠ Le cas qui a coûté : une coordonnée de niveau 2 lue au niveau 0 tombe au quart de
    # sa vraie position. Le contrôle est arithmétique et n'a besoin d'aucun réseau.
    z2, y2, x2 = 9260, 5324, 2924
    v("une coordonnée de niveau 2 lue telle quelle est au quart",
      (z2 * 4, y2 * 4, x2 * 4) == (37040, 21296, 11696))
    v("... et 37040 est bien dans la bande où vit le rouleau",
      29438 <= 37040 <= 73919)
    v("... alors que 9260 n'y est pas", not (29438 <= z2 <= 73919))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--volume", default="PHercParis4/volumes/"
                                       "20260411134726-2.400um-0.2m-78keV-masked.zarr")
    p.add_argument("--niveau", type=int, default=0)
    p.add_argument("--point", nargs=3, type=float, metavar=("Z", "Y", "X"))
    p.add_argument("--maillage", type=Path,
                   help="lire le CENTRE de la bbox d'un tifxyz au lieu d'un point")
    p.add_argument("--balayer", action="store_true",
                   help="sonder ~25 points repartis sur le maillage au lieu d'un seul")
    p.add_argument("--combien", type=int, default=25)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.balayer:
        if not a.maillage:
            p.error("--balayer exige --maillage")
        r = balayer(a.maillage, f"{BUCKET}/{a.volume}", a.niveau, a.combien)
        if r.get("refus"):
            print(f"⚠ {r['refus']}", file=sys.stderr)
            return 2
        c = r["comptes"]
        print(f"{a.maillage} au niveau {a.niveau} — {r['sondes']} points sondés")
        print(f"  matière {c['matiere']}   bloc vide {c['bloc_vide']}   "
              f"bloc absent {c['bloc_absent']}   hors du volume {c['hors_volume']}")
        for e in r["exemples"]:
            print(f"    refus  grille {e['grille']} → z,y,x {e['zyx']} : {e['refus']}")
        for e in r.get("avec_matiere", [])[:5]:
            print(f"    ⭐ matière grille {e['grille']} → z,y,x {e['zyx']} "
                  f"(max du bloc {e['max_bloc']})")
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(r, indent=2), encoding="utf-8")
        return 0

    if a.maillage:
        # ⚠⚠ LE POINT EST LU SUR LA SURFACE, PAS AU CENTRE DE SA BOÎTE. Ma première version
        # prenait le centre de la bbox, et c'est faux dès que la feuille est courbe : le
        # centre de la boîte d'une nappe incurvée est dans l'AIR à l'intérieur de la courbe,
        # donc le sondage rendait « bloc absent » sur des maillages parfaitement posés. Le
        # symptôme est le même que celui d'un maillage dans le mauvais repère, ce qui est
        # exactement le diagnostic qu'on essayait de porter.
        import tifffile

        import numpy as np

        plans = {n: tifffile.imread(str(a.maillage / f"{n}.tif")) for n in ("x", "y", "z")}
        bon = (plans["x"] > 0) & (plans["y"] > 0) & (plans["z"] > 0)
        if not bon.any():
            print(f"refus : {a.maillage} n'a aucun point valide", file=sys.stderr)
            return 2
        # ⚠ Le point valide le plus proche du centre de la GRILLE : un maillage troué n'a pas
        # forcément un point en son milieu exact.
        rs, cs = np.nonzero(bon)
        r0, c0 = bon.shape[0] / 2.0, bon.shape[1] / 2.0
        k = int(np.argmin((rs - r0) ** 2 + (cs - c0) ** 2))
        r, c = int(rs[k]), int(cs[k])
        cx, cy, cz = (float(plans[n][r, c]) for n in ("x", "y", "z"))
        point = (cz, cy, cx)
        print(f"{a.maillage} · point de grille ({r}, {c}) : z={cz:.0f} y={cy:.0f} x={cx:.0f}")
    elif a.point:
        point = tuple(a.point)
    else:
        p.error("--point ou --maillage requis")

    z, y, x = (int(round(v)) for v in point)
    url = f"{BUCKET}/{a.volume}"
    bloc, valeur, cle = lire_bloc(url, a.niveau, z, y, x)
    if bloc is None:
        print(f"⚠⚠ ({z}, {y}, {x}) au niveau {a.niveau} : {valeur}", file=sys.stderr)
        rendu = {"point": [z, y, x], "niveau": a.niveau, "refus": valeur, "cle": cle}
        code = 3
    else:
        part = float((bloc > 0).mean())
        print(f"bloc {cle}  ·  valeur au point {valeur}  ·  max du bloc {int(bloc.max())}"
              f"  ·  {100 * part:.1f} % du bloc allumé")
        if bloc.max() == 0:
            print("⚠⚠ le bloc entier est VIDE — il n'y a rien à cette coordonnée, "
                  "et un rendu qui part d'ici sera noir")
        rendu = {"point": [z, y, x], "niveau": a.niveau, "cle": cle,
                 "valeur": valeur, "max_bloc": int(bloc.max()), "part_allumee": part}
        code = 0
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(rendu, indent=2), encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
