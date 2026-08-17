#!/usr/bin/env python3
"""Localiser les fusions de feuilles en SUIVANT les spires, pas en les recomptant.

⚠ **Pourquoi ce fichier existe : le comptage a echoue.** Une premiere tentative
comptait les murs franchis rayon par rayon et signalait un deficit comme une fusion.
Elle a rendu **475 sites, presque tous pres du centre** — c'est-a-dire une carte de la
faiblesse du detecteur, pas des fusions. La cause est structurelle et n'est pas un
reglage : *compter des pics independamment a chaque angle jette le fait qu'une feuille
est une COURBE CONTINUE.* Un pic manque a un angle est du bruit ; un pic manquant sur
trente angles consecutifs est un evenement.

Le depliage polaire (`radial.py deplier`) rend le suivi possible. Dans la coupe
cartesienne une spire est un arc dont la courbure change avec le rayon ; depliee,
c'est une ligne quasi horizontale, et « suivre une feuille » redevient du chainage de
proche en proche.

**Ce que le suivi mesure, et que le comptage ne pouvait pas :**

- une **fusion** est une piste qui s'eteint la ou sa voisine continue ;
- une **rupture** est une piste qui s'eteint sans voisine pour la reprendre ;
- et les deux sont distinguees par la PERSISTANCE, qui est exactement ce que le
  comptage par angle ne pouvait pas voir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

VOXEL_UM = 7.91


def ridges(column: np.ndarray, prominence: float, min_gap: int, smooth: int) -> np.ndarray:
    """Rayons des murs franchis dans une colonne angulaire."""
    from scipy.signal import find_peaks

    kernel = np.ones(max(3, smooth)) / max(3, smooth)
    smoothed = np.convolve(column.astype(np.float32), kernel, mode="same")
    peaks, _ = find_peaks(smoothed, prominence=prominence, distance=min_gap)
    return peaks


def track(polar: np.ndarray, prominence: float, min_gap: int, smooth: int,
          tolerance: float, gap_tolerance: int) -> list[dict]:
    """Chainer les murs d'une colonne a la suivante en pistes continues.

    Chainage glouton du plus proche : a chaque colonne, chaque piste vivante cherche
    le mur le plus proche en rayon, dans une tolerance. Une piste qui n'en trouve pas
    n'est pas tuee tout de suite -- elle a droit a `gap_tolerance` colonnes de
    silence, parce qu'un detecteur rate legitimement un mur de temps en temps et
    qu'une piste coupee a chaque rate ne serait plus une piste.

    ⚠⚠ **La piste est cherchee la ou elle VA, pas la ou elle etait.** Une premiere
    version appariait au dernier rayon connu ; mesuree, elle fragmentait chaque
    feuille en ~80 morceaux (longueur mediane 111 colonnes sur 18 850) et rendait
    12 249 « fusions » sur une coupe qui compte 158 feuilles. Elargir la tolerance
    reparait le symptome — 139 pistes traversantes a tolerance 40 — mais 40 voxels
    valent plus de DEUX espacements entre feuilles (~18 voxels), donc une piste
    pouvait voler sa voisine : on echangeait une fragmentation visible contre des
    sauts de spire invisibles.

    Le correctif est de suivre la PENTE : une feuille derive doucement, donc on
    extrapole son rayon depuis son deplacement recent et on apparie autour de la
    position PREDITE. La tolerance borne alors l'ecart au mouvement lisse et non le
    mouvement lui-meme, ce qui permet de la garder **sous la moitie d'un espacement**
    — et un saut de spire devient impossible par construction plutot qu'improbable.
    """
    tracks: list[dict] = []
    live: list[int] = []
    for column_index in range(polar.shape[1]):
        found = ridges(polar[:, column_index], prominence, min_gap, smooth)
        taken = set()
        still: list[int] = []
        for tid in live:
            t = tracks[tid]
            if found.size:
                # Position predite : le rayon connu plus la derive recente, comptee
                # aussi pour les colonnes ou la piste etait muette.
                predicted = t["radius"] + t["slope"] * (1 + t["missed"])
                distances = np.abs(found - predicted)
                picked = None
                for k in np.argsort(distances):
                    if distances[k] > tolerance:
                        break          # les suivants sont plus loin encore
                    if k not in taken:
                        picked = int(k)
                        break
                if picked is not None:
                    taken.add(picked)
                    new_radius = float(found[picked])
                    step = max(1, 1 + t["missed"])
                    observed = (new_radius - t["radius"]) / step
                    # Pente lissee : une seule colonne bruitee ne doit pas lancer la
                    # piste dans une direction qu'elle ne suivra pas.
                    t["slope"] = 0.7 * t["slope"] + 0.3 * observed
                    t["radius"] = new_radius
                    t["end"] = column_index
                    t["points"] += 1
                    t["missed"] = 0
                    still.append(tid)
                    continue
            t["missed"] += 1
            if t["missed"] <= gap_tolerance:
                still.append(tid)
        live = still
        for k, r in enumerate(found):
            if k in taken:
                continue
            tracks.append({"start": column_index, "end": column_index, "radius": float(r),
                           "start_radius": float(r), "points": 1, "missed": 0,
                           "slope": 0.0})
            live.append(len(tracks) - 1)
    return tracks


def classify(tracks: list[dict], polar_shape: tuple, min_points: int,
             neighbour_voxels: float) -> dict:
    """Separer les fins de piste en fusions, ruptures, et bords de l'image.

    ⚠ Une piste qui s'arrete au dernier angle n'est pas un evenement : c'est la fin de
    l'image. Les compter serait ajouter une fusion par spire, ce qui donnerait un
    chiffre impressionnant et faux.
    """
    height, width = polar_shape
    kept = [t for t in tracks if t["points"] >= min_points]
    events = []
    for t in kept:
        if t["end"] >= width - 2:
            continue  # bord de l'image, pas un evenement
        # Une voisine vivante au meme endroit et au meme moment = fusion ; personne
        # = rupture. C'est la distinction que le comptage ne pouvait pas faire.
        companions = [
            o for o in kept
            if o is not t
            and o["start"] <= t["end"] <= o["end"]
            and abs(o["radius"] - t["radius"]) <= neighbour_voxels
        ]
        events.append({
            "angle_column": t["end"],
            "radius": t["radius"],
            "length_columns": t["points"],
            "kind": "fusion" if companions else "rupture",
        })
    return {
        "tracks_total": len(tracks),
        "tracks_kept": len(kept),
        "events": events,
        "fusions": sum(1 for e in events if e["kind"] == "fusion"),
        "ruptures": sum(1 for e in events if e["kind"] == "rupture"),
    }


def synthetic(sheets: int, height: int, width: int, merge_at: int | None) -> np.ndarray:
    """Une image polaire FABRIQUEE : N lignes paralleles, avec ou sans fusion.

    C'est le controle qui peut echouer. Sur N lignes paralleles intactes, le suivi
    doit trouver N pistes et ZERO fusion ; en soudant deux lignes a mi-parcours, il
    doit en trouver exactement une. Sans ce temoin, un tracker qui signale des
    fusions partout aurait l'air de marcher sur du vrai papyrus, ou personne ne sait
    combien il y en a.
    """
    image = np.zeros((height, width), dtype=np.uint8)
    spacing = height // (sheets + 1)
    rows = [(i + 1) * spacing for i in range(sheets)]
    for index, base in enumerate(rows):
        for column in range(width):
            row = base
            if merge_at is not None and index == 1 and column >= merge_at:
                # la piste 1 rejoint la piste 0 progressivement, puis se confond
                pull = min(1.0, (column - merge_at) / max(width * 0.1, 1))
                row = int(round(base + pull * (rows[0] - base)))
            if 0 <= row < height:
                image[max(row - 1, 0):row + 2, column] = 200
    return image


def cmd_control(args) -> int:
    ok = 0
    total = 0
    for label, merge in (("intact", None), ("une fusion", 900)):
        image = synthetic(args.sheets, 600, 1800, merge)
        tracks = track(image, args.prominence, args.min_gap, args.smooth,
                       args.tolerance, args.gap_tolerance)
        report = classify(tracks, image.shape, args.min_points, args.neighbour)
        expected = 0 if merge is None else 1
        total += 2
        got_tracks = report["tracks_kept"]
        ok += (got_tracks == args.sheets) + (report["fusions"] == expected)
        print(f"  {label:12} pistes {got_tracks} (attendu {args.sheets})   "
              f"fusions {report['fusions']} (attendu {expected})   "
              f"ruptures {report['ruptures']}")
    print()
    print(f"{'ALL PASS' if ok == total else 'ECHEC'} ({total - ok} failures, {total} checks)")
    return 0 if ok == total else 1


def cmd_run(args) -> int:
    polar = np.load(args.polar)
    print(f"polaire {polar.shape}  (rayon x angle)")
    tracks = track(polar, args.prominence, args.min_gap, args.smooth,
                   args.tolerance, args.gap_tolerance)
    report = classify(tracks, polar.shape, args.min_points, args.neighbour)
    events = report["events"]
    print(f"pistes suivies      : {report['tracks_total']}  "
          f"(retenues >= {args.min_points} colonnes : {report['tracks_kept']})")
    print(f"fusions localisees  : {report['fusions']}")
    print(f"ruptures localisees : {report['ruptures']}")
    if events:
        lengths = np.array([e["length_columns"] for e in events])
        radii = np.array([e["radius"] for e in events]) * VOXEL_UM / 1000.0
        print()
        print(f"longueur des pistes qui s'arretent : mediane {np.median(lengths):.0f} colonnes")
        print(f"rayon des evenements : {radii.min():.1f} a {radii.max():.1f} mm "
              f"(median {np.median(radii):.1f})")
        # ⚠ La repartition en rayon est LE controle : la tentative par comptage
        # rendait des sites presque tous pres du centre, signature du bruit de
        # detecteur et non des fusions.
        inner = int((radii < np.median(radii)).sum())
        print(f"repartition : {inner} en deca du rayon median, {len(radii) - inner} au-dela")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.json}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fusions de feuilles par SUIVI des spires depliees.",
        epilog="Lancer 'controle' avant 'chercher' : un tracker non teste voit des fusions partout.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("controle", cmd_control), ("chercher", cmd_run)):
        p = sub.add_parser(name)
        if name == "chercher":
            p.add_argument("polar", type=Path)
            p.add_argument("--json")
        else:
            p.add_argument("--sheets", type=int, default=12)
        p.add_argument("--prominence", type=float, default=8.0)
        p.add_argument("--min-gap", type=int, default=10)
        p.add_argument("--smooth", type=int, default=5)
        p.add_argument("--tolerance", type=float, default=8.0,
                       help="ecart TOLERE A LA POSITION PREDITE, en voxels. ⚠ Doit rester "
                            "sous la moitie de l'espacement entre feuilles (~18 voxels), "
                            "sinon une piste peut voler sa voisine")
        p.add_argument("--gap-tolerance", type=int, default=8,
                       help="colonnes de silence tolerees avant de tuer une piste")
        p.add_argument("--min-points", type=int, default=50,
                       help="longueur minimale d'une piste pour compter")
        p.add_argument("--neighbour", type=float, default=25.0,
                       help="distance radiale ou une piste voisine absorbe la fin, en voxels")
        p.set_defaults(func=func)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
