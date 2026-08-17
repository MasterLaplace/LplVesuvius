#!/usr/bin/env python3
"""Score de coherence d'une carte d'encre : y a-t-il de l'ECRITURE, ou des taches ?

Pourquoi pas un modele de langue, et pas un HTR non plus.

Un modele de langue devant du grec degrade **produit du grec plausible** : sa sortie
est indistinguable d'une hallucination. Et un HTR generaliste a ete mesure ici comme
inutilisable -- le seul modele grec de Kraken est entraine sur du texte IMPRIME, et
sur nos cartes (resolution effective au 1/16) il rend 6 caracteres de bruit contre
2 sur du papyrus vierge : un signal du niveau du bruit.

Ce qui distingue de l'ecriture de taches est STRUCTUREL, pas linguistique :

1. les lignes de texte sont REGULIEREMENT espacees -- une periodicite verticale ;
2. l'epaisseur du trait est CONSTANTE -- un scribe garde son calame ;
3. la hauteur des caracteres est CONSTANTE -- une main garde son module.

Aucune de ces trois grandeurs ne demande de savoir lire, donc aucune ne peut
inventer un sens. Et chacune est comparable a un temoin negatif, ce qui est la seule
facon de rendre un score interpretable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def ink_mask(image: np.ndarray, quantile: float) -> np.ndarray:
    """Binarise par quantile, et non par seuil absolu.

    Un seuil absolu melangerait « il y a peu d'encre » et « le rendu est pale »,
    or les deux images comparees n'ont aucune raison de partager leur echelle.
    """
    valid = image < 255  # 255 = zone non analysee dans nos rendus
    if valid.sum() == 0:
        raise ValueError("aucun pixel analysable")
    threshold = np.quantile(image[valid], quantile)
    return (image <= threshold) & valid


def line_periodicity(mask: np.ndarray) -> dict:
    """Force de la periodicite verticale : les lignes de texte sont regulieres.

    Autocorrelation du profil de densite par ligne. Un texte donne un pic net a
    l'interligne ; des taches dispersees donnent une decroissance sans pic.
    """
    profile = mask.mean(axis=1).astype(np.float64)
    profile -= profile.mean()
    if profile.std() == 0:
        return {"strength": 0.0, "spacing_px": 0}
    correlation = np.correlate(profile, profile, mode="full")[len(profile) - 1 :]
    correlation /= correlation[0]
    # On cherche le premier pic APRES la decroissance centrale : un interligne
    # plausible fait au moins quelques dizaines de pixels a cette echelle.
    low = max(8, len(profile) // 100)
    high = len(profile) // 2
    window = correlation[low:high]
    if window.size == 0:
        return {"strength": 0.0, "spacing_px": 0}
    peak = int(np.argmax(window))
    return {"strength": float(window[peak]), "spacing_px": int(peak + low)}


def stroke_consistency(mask: np.ndarray) -> dict:
    """Regularite de l'epaisseur de trait, mesuree par longueurs de plages.

    Un scribe garde son calame, donc les largeurs de trait se concentrent autour
    d'une valeur. Des taches de tailles quelconques donnent une distribution large.
    On rapporte le coefficient de variation : PLUS BAS veut dire plus regulier.
    """
    runs = []
    for row in mask:
        if not row.any():
            continue
        padded = np.concatenate(([False], row, [False]))
        edges = np.flatnonzero(padded[1:] != padded[:-1])
        widths = edges[1::2] - edges[0::2]
        runs.extend(widths.tolist())
    if len(runs) < 50:
        return {"median_px": 0.0, "variation": float("nan"), "count": len(runs)}
    runs = np.asarray(runs, dtype=np.float64)
    return {
        "median_px": float(np.median(runs)),
        "variation": float(runs.std() / max(runs.mean(), 1e-9)),
        "count": int(runs.size),
    }


def component_regularity(mask: np.ndarray) -> dict:
    """Regularite de la taille des composantes connexes -- le module de la main.

    Une ecriture a des caracteres de hauteur comparable. Des taches issues du bruit
    n'ont aucune raison de partager une taille.
    """
    from scipy import ndimage

    labelled, count = ndimage.label(mask)
    if count < 5:
        return {"count": int(count), "height_variation": float("nan")}
    objects = ndimage.find_objects(labelled)
    heights = np.array([sl[0].stop - sl[0].start for sl in objects], dtype=np.float64)
    # Les composantes minuscules sont du bruit de seuil, pas des caracteres.
    heights = heights[heights >= 4]
    if heights.size < 5:
        return {"count": int(heights.size), "height_variation": float("nan")}
    return {
        "count": int(heights.size),
        "median_height_px": float(np.median(heights)),
        "height_variation": float(heights.std() / max(heights.mean(), 1e-9)),
    }


def score(path: Path, quantile: float) -> dict:
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    image = np.array(Image.open(path).convert("L"))
    mask = ink_mask(image, quantile)
    report = {
        "image": path.name,
        "ink_fraction": float(mask.mean()),
        "lines": line_periodicity(mask),
        "stroke": stroke_consistency(mask),
        "components": component_regularity(mask),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Coherence structurelle d'une carte d'encre (ecriture vs taches).",
        epilog=(
            "Un score n'a de sens que COMPARE : passer le temoin negatif en second "
            "argument. Sans lui, les nombres ne sont pas interpretables."
        ),
    )
    parser.add_argument("images", type=Path, nargs="+", help="images a scorer")
    parser.add_argument(
        "--quantile", type=float, default=0.10,
        help="fraction de pixels les plus sombres comptes comme encre (defaut: 0.10)",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    reports = []
    for path in args.images:
        try:
            reports.append(score(path, args.quantile))
        except Exception as error:  # noqa: BLE001 - on rapporte, on ne masque pas
            print(f"erreur sur {path} : {type(error).__name__}: {error}", file=sys.stderr)
            return 2

    if args.as_json:
        json.dump(reports, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    header = f"{'image':<24}{'periodicite':>12}{'interligne':>11}{'trait':>8}{'var.trait':>10}{'car.':>7}{'var.haut':>9}"
    print(header)
    print("-" * len(header))
    for r in reports:
        print(
            f"{r['image'][:24]:<24}"
            f"{r['lines']['strength']:>12.3f}"
            f"{r['lines']['spacing_px']:>11d}"
            f"{r['stroke']['median_px']:>8.1f}"
            f"{r['stroke']['variation']:>10.3f}"
            f"{r['components'].get('count', 0):>7d}"
            f"{r['components'].get('height_variation', float('nan')):>9.3f}"
        )
    if len(reports) >= 2:
        print()
        print("Lecture : la periodicite doit etre PLUS HAUTE sur du texte, et les")
        print("variations de trait et de hauteur PLUS BASSES. Un ecart faible sur les")
        print("trois signifie que la mesure ne discrimine pas -- et non que l'image est vide.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
