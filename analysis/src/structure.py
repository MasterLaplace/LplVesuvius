#!/usr/bin/env python3
"""Y a-t-il de l'ECRITURE dans cette region, ou seulement du signal ?

Reprise de `htr/src/coherence.py`, qui avait echoue, avec le diagnostic de son
echec applique. Trois corrections, chacune correspondant a une cause identifiee :

1. **L'axe.** Sur ce segment les lignes de texte courent le long des LIGNES du
   tableau, pas des colonnes -- verifie sur la verite terrain tracee a la main
   (coefficient de variation de l'espacement : 0,46 sur le bon axe contre 1,20 sur
   l'autre). Un profil pris sur le mauvais axe traverse les lignes au lieu de les
   longer, donc il ne peut par construction montrer aucune periodicite. La version
   precedente prenait `mean(axis=1)`, c'est-a-dire l'autre.
2. **La taille.** Une autocorrelation a besoin de nombreuses periodes ; sur 20 x
   24 mm il y avait quatre lignes. Ici chaque region fait ~4 Mpx.
3. **Le temoin.** L'ancien temoin negatif venait d'un autre endroit avec un autre
   rendu. Ici les trois regions sortent du MEME segment, du MEME passage du modele,
   et ne different que par la question posee -- donc tout ecart mesure porte sur le
   contenu et non sur la chaine.

⚠ Ce fichier travaille sur le tableau de scores et jamais sur un PNG : la
binarisation d'une image deja quantifiee en 256 niveaux, reduite et reechantillonnee
mesurerait le rendu autant que le papyrus.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

LINE_AXIS = 0
"""Axe a moyenner pour obtenir un profil transverse aux lignes de texte.

Une ligne de texte est ici a colonne ~constante, donc moyenner sur les lignes
(`axis=0`) donne un profil indexe par colonne dont les pics SONT les lignes.
"""


def binarise(scores: np.ndarray, threshold: float) -> np.ndarray:
    """Seuil sur la frontiere de decision du modele, la MEME dans toutes les regions.

    ⚠ Une version anterieure normalisait par quantile, pour comparer les regions a
    quantite d'encre egale. C'etait le defaut : dans une region VIDE, forcer 8 % des
    pixels a compter comme encre fabrique de la structure a partir du bruit -- et le
    bruit etant plus uniforme que du texte, la region vide ressortait avec
    l'espacement de lignes le PLUS regulier des trois. La mesure repondait a
    l'envers, pour une raison entierement contenue dans sa normalisation.

    Le seuil est donc absolu, mais ce n'est pas un reglage : c'est le zero du logit,
    la decision du modele lui-meme, et toutes les regions sortent du meme passage.
    Ce que ce depot interdit ailleurs est un seuil absolu sur des grandeurs
    PHYSIQUES qui varient d'un endroit a l'autre -- ici la grandeur est la sortie
    d'un unique classifieur, qui a par construction la meme echelle partout.
    """
    covered = np.isfinite(scores)
    if covered.sum() < 10_000:
        raise ValueError("region trop petite ou non couverte")
    return covered & (scores >= threshold)


def line_rhythm(mask: np.ndarray, smooth: float, min_gap: int) -> dict:
    """Regularite de l'espacement entre lignes de texte.

    Mesure par POSITION DE PIC et non par autocorrelation : l'autocorrelation d'un
    profil binaire creux est dominee par son lobe central, et sur ces donnees son
    maximum tombe systematiquement sur la borne basse de la fenetre de recherche --
    c'est-a-dire qu'elle ne trouve aucune periode, ni sur un axe ni sur l'autre.
    Des positions de pics donnent directement les espacements, dont on rapporte le
    coefficient de variation : PLUS BAS veut dire plus regulier.
    """
    from scipy import ndimage, signal

    profile = ndimage.gaussian_filter1d(mask.mean(axis=LINE_AXIS).astype(np.float64), smooth)
    if profile.max() <= 0:
        return {"lines": 0, "spacing_px": float("nan"), "variation": float("nan")}
    peaks, _ = signal.find_peaks(profile, height=profile.max() * 0.25, distance=min_gap)
    if peaks.size < 4:
        return {"lines": int(peaks.size), "spacing_px": float("nan"), "variation": float("nan")}
    gaps = np.diff(peaks).astype(np.float64)
    return {
        "lines": int(peaks.size),
        "spacing_px": float(np.median(gaps)),
        "variation": float(gaps.std() / gaps.mean()),
    }


def stroke_width(mask: np.ndarray) -> dict:
    """Regularite de l'epaisseur de trait, par longueurs de plages.

    Le balayage est fait PERPENDICULAIREMENT aux lignes de texte, donc chaque plage
    traverse un trait plutot que de le longer. Longer un trait mesurerait la
    longueur de la lettre, qui varie legitimement d'une lettre a l'autre.
    """
    runs = []
    scan = mask if LINE_AXIS == 0 else mask.T
    for line in scan.T:
        if not line.any():
            continue
        padded = np.concatenate(([False], line, [False]))
        edges = np.flatnonzero(padded[1:] != padded[:-1])
        runs.append(edges[1::2] - edges[0::2])
    if not runs:
        return {"median_px": float("nan"), "variation": float("nan"), "count": 0}
    widths = np.concatenate(runs).astype(np.float64)
    widths = widths[widths >= 2]  # une plage d'un pixel est du bruit de seuil
    if widths.size < 200:
        return {"median_px": float("nan"), "variation": float("nan"), "count": int(widths.size)}
    return {
        "median_px": float(np.median(widths)),
        "variation": float(widths.std() / widths.mean()),
        "count": int(widths.size),
    }


def glyph_shape(mask: np.ndarray, min_area: int) -> dict:
    """Taille et compacite des composantes connexes -- le module de la main.

    Une ecriture a des caracteres de taille comparable et de forme compacte. Le
    bruit de detection donne soit des taches minuscules, soit de longues trainees
    qui suivent une fibre. La COMPACITE (aire sur aire de la boite englobante) est
    ce qui separe les deux : une lettre remplit mal sa boite mais pas au point d'une
    trainee, et une tache la remplit trop.
    """
    from scipy import ndimage

    labelled, count = ndimage.label(mask)
    if count < 20:
        return {"glyphs": int(count), "median_area": float("nan"),
                "area_variation": float("nan"), "median_fill": float("nan")}
    slices = ndimage.find_objects(labelled)
    areas, fills, heights = [], [], []
    for index, box in enumerate(slices, start=1):
        sub = labelled[box] == index
        area = int(sub.sum())
        if area < min_area:
            continue
        boxed = sub.shape[0] * sub.shape[1]
        areas.append(area)
        fills.append(area / boxed)
        heights.append(sub.shape[LINE_AXIS])
    if len(areas) < 20:
        return {"glyphs": len(areas), "median_area": float("nan"),
                "area_variation": float("nan"), "median_fill": float("nan")}
    areas = np.asarray(areas, dtype=np.float64)
    heights = np.asarray(heights, dtype=np.float64)
    return {
        "glyphs": int(areas.size),
        "median_area": float(np.median(areas)),
        "area_variation": float(areas.std() / areas.mean()),
        "median_fill": float(np.median(fills)),
        "median_height": float(np.median(heights)),
        "height_variation": float(heights.std() / heights.mean()),
    }


def describe(scores: np.ndarray, name: str, threshold: float,
             smooth: float, min_gap: int, min_area: int) -> dict:
    mask = binarise(scores, threshold)
    return {
        "region": name,
        "pixels": int(np.isfinite(scores).sum()),
        "ink_%": float(mask.sum() / max(np.isfinite(scores).sum(), 1) * 100.0),
        "rhythm": line_rhythm(mask, smooth, min_gap),
        "stroke": stroke_width(mask),
        "glyph": glyph_shape(mask, min_area),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Structure d'une carte d'encre : ecriture ou signal informe ?",
        epilog="Passer au moins un temoin positif ET un temoin negatif : les nombres "
               "ne sont interpretables que compares.",
    )
    parser.add_argument("prediction", type=Path)
    parser.add_argument(
        "--region", action="append", default=[], metavar="NOM:HAUT:HAUTEUR",
        help="region a decrire, repetable (ex: texte:3584:2048)",
    )
    parser.add_argument("--threshold", type=float, default=0.0,
                        help="seuil sur le logit, identique partout (defaut: 0.0, soit p=0,5)")
    parser.add_argument("--smooth", type=float, default=25.0)
    parser.add_argument("--min-gap", type=int, default=80,
                        help="ecart minimal entre deux lignes de texte, en px")
    parser.add_argument("--min-area", type=int, default=200,
                        help="aire minimale d'une composante pour compter comme glyphe")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if len(args.region) < 2:
        print("erreur : au moins deux regions, sinon les nombres ne veulent rien dire",
              file=sys.stderr)
        return 2

    scores = np.load(args.prediction)
    reports = []
    for spec in args.region:
        try:
            name, top, height = spec.split(":")
            top, height = int(top), int(height)
        except ValueError:
            print(f"erreur : region mal formee '{spec}' (attendu NOM:HAUT:HAUTEUR)",
                  file=sys.stderr)
            return 2
        try:
            reports.append(describe(scores[top : top + height], name, args.threshold,
                                    args.smooth, args.min_gap, args.min_area))
        except ValueError as error:
            print(f"erreur sur {name} : {error}", file=sys.stderr)
            return 3

    if args.as_json:
        json.dump(reports, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    header = (f"{'region':<16}{'encre%':>8}{'lignes':>8}{'espac.':>8}{'var.esp':>9}"
              f"{'trait':>8}{'var.tr':>8}{'glyphes':>9}{'aire':>8}{'var.aire':>10}{'remp.':>7}")
    print(header)
    print("-" * len(header))
    for r in reports:
        print(f"{r['region'][:16]:<16}{r['ink_%']:>8.2f}"
              f"{r['rhythm']['lines']:>8d}{r['rhythm']['spacing_px']:>8.0f}"
              f"{r['rhythm']['variation']:>9.3f}"
              f"{r['stroke']['median_px']:>8.1f}{r['stroke']['variation']:>8.3f}"
              f"{r['glyph']['glyphs']:>9d}{r['glyph']['median_area']:>8.0f}"
              f"{r['glyph']['area_variation']:>10.3f}{r['glyph']['median_fill']:>7.3f}")
    print()
    print("Lecture : de l'ECRITURE donne un espacement de lignes REGULIER (var. basse),")
    print("des traits d'epaisseur reguliere, et des glyphes de taille comparable.")
    print("Un ecart faible sur les trois signifie que la mesure ne discrimine pas --")
    print("et non que la region est vide.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
