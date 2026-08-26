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
    from scipy.optimize import linear_sum_assignment

    tracks: list[dict] = []
    live: list[int] = []
    for column_index in range(polar.shape[1]):
        found = ridges(polar[:, column_index], prominence, min_gap, smooth)
        taken: set[int] = set()
        still: list[int] = []

        if live and found.size:
            # ⚠⚠ APPARIEMENT GLOBAL, et non glouton au plus proche. Le glouton sert
            # les pistes dans l'ordre d'arrivee : deux pistes qui convoitent le meme
            # mur, la premiere le prend et la seconde repart de zero, meme quand un
            # echange aurait satisfait les deux. C'est le mode d'echec classique en
            # champ dense, et c'est ce qui fragmentait chaque feuille en ~80 morceaux.
            # Ici on minimise le cout TOTAL de la colonne, donc l'echange se fait tout
            # seul et aucune piste n'est sacrifiee a l'ordre d'iteration.
            predicted = np.array([tracks[t]["radius"] + tracks[t]["slope"] * (1 + tracks[t]["missed"])
                                  for t in live])
            cost = np.abs(predicted[:, None] - found[None, :])
            # Au-dela de la tolerance, l'appariement est INTERDIT et non simplement
            # cher : un cout fini laisserait l'optimum global sauter une spire pour
            # gagner ailleurs, ce qui est exactement l'erreur qu'on veut rendre
            # impossible.
            forbidden = cost > tolerance
            cost = np.where(forbidden, 1e6, cost)
            rows, cols = linear_sum_assignment(cost)
            for r, c in zip(rows, cols):
                if forbidden[r, c]:
                    continue
                tid = live[r]
                t = tracks[tid]
                taken.add(int(c))
                new_radius = float(found[c])
                step = max(1, 1 + t["missed"])
                observed = (new_radius - t["radius"]) / step
                t["slope"] = 0.7 * t["slope"] + 0.3 * observed
                t["radius"] = new_radius
                t["end"] = column_index
                t["points"] += 1
                t["missed"] = 0
                still.append(tid)
            matched = {live[r] for r, c in zip(rows, cols) if not forbidden[r, c]}
        else:
            matched = set()

        for tid in live:
            if tid in matched:
                continue
            t = tracks[tid]
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


# ---------------------------------------------------------------------------
# La methode vers laquelle les trois refutations convergent : ne rien suivre.
# ---------------------------------------------------------------------------

def gap_map(polar: np.ndarray, prominence: float, min_gap: int, smooth: int,
            band: int = 400) -> tuple:
    """Ecart entre murs voisins, colonne par colonne, NORMALISE localement.

    ⚠ Pourquoi cette mesure remplace le suivi. Trois hypotheses sur la fragmentation
    du tracker ont ete posees et **les trois refutees** (affectation globale : pire ;
    pistes en sursis : innocentes ; detecteur : 92 % des murs retrouves a moins de
    2 voxels). La cause reelle mesuree : 125 murs sur 126 sont apparies a chaque
    colonne, donc la couverture est quasi parfaite et c'est l'IDENTITE des pistes qui
    churne. Les « fusions » comptees comme des morts de piste etaient des changements
    d'etiquette.

    La signature physique, elle, ne demande aucune identite : **deux feuilles soudees
    laissent un ecart double**. Un ecart est local, il se mesure dans une colonne
    unique, et il ne depend d'aucun appariement entre colonnes.

    ⚠ **Normalise par l'espacement LOCAL et jamais par un seuil absolu.** L'espacement
    entre feuilles varie d'un facteur trois selon l'endroit (mesure : 158 um pres du
    coeur, 203 um vers l'exterieur), donc un seuil en micrometres attraperait le coeur
    et raterait le bord. La bande de normalisation est un voisinage en RAYON, pas la
    colonne entiere, pour la meme raison.
    """
    heights, widths = polar.shape
    ratios, radii, columns = [], [], []
    for column in range(widths):
        found = ridges(polar[:, column], prominence, min_gap, smooth)
        if found.size < 4:
            continue
        gaps = np.diff(found).astype(np.float64)
        middles = (found[:-1] + found[1:]) / 2.0
        for gap, middle in zip(gaps, middles):
            near = np.abs(middles - middle) <= band
            local = np.median(gaps[near])
            if local <= 0:
                continue
            ratios.append(gap / local)
            radii.append(middle)
            columns.append(column)
    return (np.asarray(ratios), np.asarray(radii), np.asarray(columns))


def persistent_sites(ratios: np.ndarray, radii: np.ndarray, columns: np.ndarray,
                     doubling: float, persistence: int, radial_window: float,
                     angular_window: int = 300) -> list[dict]:
    """Regrouper les ecarts doubles en SITES : contigus en rayon ET en angle.

    ⚠⚠ **Une premiere version ne groupait que par le rayon**, et rendait des « sites »
    couvrant les colonnes 0 a 18 849, c'est-a-dire la circonference entiere. Ce n'etait
    pas un endroit, c'etait un *rayon ou l'ecart double souvent* — deux choses
    differentes, et seule la seconde se va verifier au microscope.

    Une soudure occupe une **longueur d'arc**, donc un site doit etre borne dans les
    deux directions. Le regroupement est un chainage : une marque rejoint un site si
    elle est proche en rayon **et** a moins de `angular_window` colonnes de la derniere
    marque du site. Une trouee angulaire plus large ouvre un site distinct — deux
    soudures au meme rayon a deux endroits du rouleau sont deux evenements.

    ⚠ La persistance separe une soudure d'un rate de detecteur : un ecart double sur
    une colonne est du bruit, sur trois cents colonnes c'est un evenement. C'est
    exactement ce qui manquait a la tentative par comptage.
    """
    flagged = ratios >= doubling
    if not flagged.any():
        return []
    r_flag = radii[flagged]
    c_flag = columns[flagged]
    order = np.lexsort((c_flag, r_flag))
    r_flag, c_flag = r_flag[order], c_flag[order]

    sites: list[dict] = []
    current_r: list[float] = []
    current_c: list[int] = []

    def close(marks_r: list[float], marks_c: list[int]) -> None:
        if len(marks_c) >= persistence:
            sites.append({
                "radius": float(np.median(marks_r)),
                "column_first": int(min(marks_c)),
                "column_last": int(max(marks_c)),
                "arc_columns": int(max(marks_c) - min(marks_c) + 1),
                "marks": len(marks_c),
            })

    for radius, column in zip(r_flag, c_flag):
        if current_r and (abs(radius - current_r[-1]) > radial_window
                          or column - current_c[-1] > angular_window):
            close(current_r, current_c)
            current_r, current_c = [], []
        current_r.append(float(radius))
        current_c.append(int(column))
    close(current_r, current_c)
    return sites


def doubling_density(ratios, radii, columns, doubling: float,
                     radial_cell: float, angular_cell: int,
                     min_radius: float = 300.0, voxel_um: float = VOXEL_UM) -> tuple:
    """Densite de marquage par cellule (rayon x angle) -- sans chainage ni persistance.

    ⚠⚠ **Pourquoi ceci remplace le chainage.** Chainer des marques exigeait deux
    parametres qui se battaient : la persistance demandait 200 marques par groupe et
    la fenetre angulaire en plafonnait les groupes a 164, donc zero site. Les regler
    l'un contre l'autre jusqu'a voir apparaitre des sites serait choisir un nombre
    pour que le reglage du jour passe.

    La cause mesuree est que le marquage est **intermittent** : ecart median de 6
    colonnes entre deux marques voisines, mais q90 a 891. Un flag binaire trop bruite
    ne se chaine pas. Une DENSITE, elle, absorbe l'intermittence par construction --
    ce qu'on demande n'est plus « ces marques se touchent-elles » mais « cette region
    double-t-elle ses ecarts bien plus souvent qu'ailleurs ».

    ⚠ Et le seuil reste RELATIF : une cellule est anormale par rapport a la densite de
    fond du meme relevé, jamais par rapport a un nombre choisi d'avance.
    """
    # ⚠⚠ LE COEUR EST EXCLU, et ce n'est pas un reglage. Au rayon r, deux colonnes
    # voisines de l'image depliee echantillonnent des points distants de
    # 2*pi*r/colonnes voxels : a r = 100 cela fait 0,03 voxel, donc une trentaine de
    # colonnes lisent LE MEME PIXEL. Les ecarts y sont degeneres par construction du
    # depliage, pas bruites -- et sans cette coupe la mesure redecouvre exactement le
    # mode d'echec de la tentative par comptage (475 sites, tous pres du centre).
    # Le seuil est celui ou une colonne avance d'au moins un dixieme de voxel.
    usable = radii >= min_radius
    ratios, radii, columns = ratios[usable], radii[usable], columns[usable]
    flagged = ratios >= doubling
    r_bin = (radii / radial_cell).astype(np.int64)
    c_bin = (columns / angular_cell).astype(np.int64)
    key = r_bin * (c_bin.max() + 1) + c_bin
    total = np.bincount(key)
    hits = np.bincount(key, weights=flagged.astype(np.float64))
    enough = total >= 20          # une cellule vide ne rapporte pas un taux
    rate = np.full(total.shape, np.nan)
    rate[enough] = hits[enough] / total[enough]
    return rate, total, (c_bin.max() + 1), radial_cell, angular_cell, voxel_um


def cmd_density(args) -> int:
    polar = np.load(args.polar)
    ratios, radii, columns = gap_map(polar, args.prominence, args.min_gap,
                                     args.smooth, args.band)
    rate, total, width, rcell, acell, voxel = doubling_density(
        ratios, radii, columns, args.doubling, args.radial_cell, args.angular_cell,
        args.min_radius)
    print(f"⚠ coeur exclu sous r = {args.min_radius:.0f} voxels "
          f"({args.min_radius * VOXEL_UM / 1000:.1f} mm) : depliage degenere")
    valid = np.isfinite(rate)
    background = float(np.nanmedian(rate))
    spread = float(np.nanpercentile(rate[valid], 90) - background)
    print(f"polaire {polar.shape}  |  {ratios.size} ecarts, "
          f"{int(valid.sum())} cellules de {rcell:.0f} vx x {acell} colonnes")
    print(f"taux de doublement : fond {background * 100:.1f} %  "
          f"q90 {np.nanpercentile(rate[valid], 90) * 100:.1f} %  "
          f"q99 {np.nanpercentile(rate[valid], 99) * 100:.1f} %  "
          f"max {np.nanmax(rate) * 100:.1f} %")
    # ⚠ Le seuil est exprime en ECARTS AU FOND, mesures sur ce releve, et non en
    # pourcentage absolu : le fond depend du detecteur et du rouleau.
    threshold = background + args.excess * spread
    anomalous = valid & (rate > threshold)
    print(f"seuil : fond + {args.excess:.1f} x (q90 - fond) = {threshold * 100:.1f} %")
    print()
    print(f"cellules ANORMALES : {int(anomalous.sum())} sur {int(valid.sum())} "
          f"({anomalous.sum() / max(valid.sum(), 1) * 100:.2f} %)")
    if anomalous.any():
        idx = np.flatnonzero(anomalous)
        rr = (idx // width) * rcell * voxel / 1000.0
        cc = (idx % width) * acell
        inner = int((rr < np.median(rr)).sum())
        print(f"  rayon : {rr.min():.1f} a {rr.max():.1f} mm (median {np.median(rr):.1f})")
        print(f"  repartition : {inner} en deca du rayon median, {len(rr) - inner} au-dela")
        top = idx[np.argsort(-rate[idx])][:8]
        for k in top:
            print(f"    r={(k // width) * rcell * voxel / 1000:5.1f} mm  "
                  f"colonne ~{(k % width) * acell:6d}  "
                  f"taux {rate[k] * 100:5.1f} %  ({int(total[k])} ecarts)")
        if args.json:
            Path(args.json).write_text(json.dumps({
                "background_rate": background, "threshold": threshold,
                "cells": [{"radius_mm": float((int(k) // width) * rcell * voxel / 1000),
                           "column": int((int(k) % width) * acell),
                           "rate": float(rate[k]), "gaps": int(total[k])} for k in idx],
            }, indent=2) + "\n")
            print(f"\necrit : {args.json}")
    return 0


def cmd_gaps(args) -> int:
    polar = np.load(args.polar)
    ratios, radii, columns = gap_map(polar, args.prominence, args.min_gap,
                                     args.smooth, args.band)
    print(f"polaire {polar.shape}  |  {ratios.size} ecarts mesures")
    print(f"ecart / espacement local : median {np.median(ratios):.2f}  "
          f"q90 {np.percentile(ratios, 90):.2f}  q99 {np.percentile(ratios, 99):.2f}")
    print(f"fraction >= {args.doubling:.1f} (ecart double) : "
          f"{(ratios >= args.doubling).mean() * 100:.2f} %")
    sites = persistent_sites(ratios, radii, columns, args.doubling,
                             args.persistence, args.radial_window, args.angular_window)
    print()
    print(f"sites PERSISTANTS (>= {args.persistence} colonnes) : {len(sites)}")
    if sites:
        r = np.array([s["radius"] for s in sites]) * VOXEL_UM / 1000.0
        print(f"  rayon : {r.min():.1f} a {r.max():.1f} mm (median {np.median(r):.1f})")
        inner = int((r < np.median(r)).sum())
        print(f"  repartition : {inner} en deca du rayon median, {len(r) - inner} au-dela")
        for s in sorted(sites, key=lambda x: -x["marks"])[:8]:
            arc_mm = s['arc_columns'] / 18850.0 * 2 * np.pi * s['radius'] * VOXEL_UM / 1000
            print(f"    r={s['radius'] * VOXEL_UM / 1000:5.1f} mm  "
                  f"colonnes {s['column_first']}-{s['column_last']}  "
                  f"arc {arc_mm:5.1f} mm  ({s['marks']} marques)")
    if args.json:
        Path(args.json).write_text(json.dumps({"sites": sites}, indent=2) + "\n")
        print(f"\necrit : {args.json}")
    return 0


def cmd_gap_control(args) -> int:
    """Le temoin : sur des lignes fabriquees, un ecart double doit apparaitre la ou
    l'on a soude, et nulle part ailleurs."""
    checks = passed = 0
    for label, merge, expected in (("intact", None, 0), ("une fusion", 900, 1)):
        image = synthetic(args.sheets, 600, 1800, merge)
        ratios, radii, columns = gap_map(image, args.prominence, args.min_gap,
                                         args.smooth, args.band)
        sites = persistent_sites(ratios, radii, columns, args.doubling,
                                 args.persistence, args.radial_window, args.angular_window)
        checks += 1
        passed += (len(sites) == expected)
        print(f"  {label:12} sites {len(sites)} (attendu {expected})   "
              f"ecart median {np.median(ratios):.2f}")
    print()
    print(f"{'ALL PASS' if passed == checks else 'ECHEC'} "
          f"({checks - passed} failures, {checks} checks)")
    return 0 if passed == checks else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fusions de feuilles par SUIVI des spires depliees.",
        epilog="Lancer 'controle' avant 'chercher' : un tracker non teste voit des fusions partout.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("controle", cmd_control), ("chercher", cmd_run),
                       ("ecarts", cmd_gaps), ("ecarts-controle", cmd_gap_control),
                       ("densite", cmd_density)):
        p = sub.add_parser(name)
        if name in ("chercher", "ecarts", "densite"):
            p.add_argument("polar", type=Path)
            p.add_argument("--json")
        else:
            p.add_argument("--sheets", type=int, default=12)
        p.add_argument("--band", type=float, default=400.0,
                       help="voisinage RADIAL de normalisation, en voxels")
        p.add_argument("--doubling", type=float, default=1.7,
                       help="rapport ecart/espacement local a partir duquel on marque. "
                            "1,7 et non 2,0 : une soudure ecrase les deux feuilles l'une "
                            "contre l'autre, donc l'ecart resultant est un peu sous le double")
        p.add_argument("--persistence", type=int, default=200,
                       help="colonnes marquees minimum pour qu'un site compte")
        p.add_argument("--radial-window", type=float, default=30.0,
                       help="tolerance radiale pour regrouper des marques en un site")
        p.add_argument("--min-radius", type=float, default=300.0,
                       help="rayon sous lequel le depliage est degenere et la mesure "
                            "sans objet (defaut: 300 vx = 2,4 mm)")
        p.add_argument("--radial-cell", type=float, default=60.0,
                       help="hauteur d'une cellule de densite, en voxels (~3 feuilles)")
        p.add_argument("--angular-cell", type=int, default=500,
                       help="largeur d'une cellule de densite, en colonnes")
        p.add_argument("--excess", type=float, default=3.0,
                       help="combien de (q90 - fond) au-dessus du fond pour etre anormal")
        p.add_argument("--angular-window", type=int, default=300,
                       help="trouee angulaire au-dela de laquelle un site en devient deux")
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
