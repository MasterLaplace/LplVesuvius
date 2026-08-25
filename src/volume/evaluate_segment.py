#!/usr/bin/env python3
"""Evaluation d'une carte d'encre contre un etiquetage PARTIEL.

Le probleme central, et pourquoi ce fichier ne se contente pas d'appeler
`roc_auc_score` : l'etiquetage de ce jeu ne couvre pas tout le segment. Un pixel
etiquete a zero peut vouloir dire deux choses incompatibles -- « l'annotateur a
regarde et il n'y a pas d'encre » ou « l'annotateur n'a pas regarde ». Les
confondre transforme chaque lettre correctement trouvee hors zone annotee en faux
positif, donc rabaisse la precision d'une quantite qui ne mesure QUE la couverture
de l'annotation.

Trois evaluations sont donc rapportees cote a cote, de la plus pessimiste a la plus
juste, et l'ecart entre elles EST le resultat :

1. **tout le segment**   -- borne inferieure franche, aucun choix a discuter ;
2. **lignes annotees**   -- le decoupage de `08`, grossier : l'annotation manquante
   est surtout faite de colonnes ;
3. **tuiles annotees**   -- possible seulement sur un segment entier : une tuile
   qui porte de l'encre etiquetee est une tuile ou quelqu'un a regarde, donc ses
   zeros sont de vrais negatifs.

⚠ Aucune de ces restrictions ne peut inventer du signal : elles retirent des
pixels, elles n'en ajoutent pas. Le controle qui le verifie est le meme calcul sur
une prediction MELANGEE, qui doit rendre 0,5 dans les trois cas -- sans lui, un
decoupage assez agressif finirait par flatter n'importe quoi.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

UNSEEN = np.nan
"""Valeur des pixels que le balayage n'a pas atteints : « pas regarde »."""


class EvaluationError(RuntimeError):
    """Leve quand une precondition d'alignement ou de forme n'est pas tenue."""


def load_pair(prediction_path: Path, labels_path: Path):
    """Charge prediction et etiquettes, et VERIFIE l'alignement au lieu de le supposer.

    Les etiquettes sont publiees remplies jusqu'a un multiple de 512, les couches
    non. Un recadrage silencieux serait exactement le genre de decalage qui produit
    un chiffre parfaitement faux : on exige donc que la zone retiree soit vide.
    """
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    prediction = np.load(prediction_path)
    labels_full = np.array(Image.open(labels_path))

    if labels_full.shape[0] < prediction.shape[0] or labels_full.shape[1] < prediction.shape[1]:
        raise EvaluationError(
            f"etiquettes {labels_full.shape} plus petites que la prediction {prediction.shape}"
        )

    labels = labels_full[: prediction.shape[0], : prediction.shape[1]] > 0
    trimmed = int((labels_full > 0).sum() - labels.sum())
    if trimmed != 0:
        raise EvaluationError(
            f"le recadrage jette {trimmed} pixels d'encre : l'alignement en (0,0) est faux"
        )
    return prediction, labels


def auc(scores: np.ndarray, truth: np.ndarray) -> float:
    """Aire sous la courbe ROC, par la statistique de Mann-Whitney sur les rangs.

    Ecrit ici plutot qu'importe : la formule par les rangs est exacte, traite les
    ex aequo par leur rang moyen, et ne demande pas de trier des dizaines de
    millions de couples. Le detour par scikit-learn n'apporterait rien qu'une
    dependance.
    """
    positives = int(truth.sum())
    negatives = truth.size - positives
    if positives == 0 or negatives == 0:
        return float("nan")
    order = np.argsort(scores, kind="stable")
    sorted_scores = scores[order]
    # Ex aequo : rang MOYEN, sinon l'AUC dependrait de l'ordre d'arrivee -- et la
    # sortie de ce modele en porte beaucoup (75 % des scores tiennent dans 0,3).
    # Vectorise : une boucle Python sur 45 M d'elements coutait deux minutes.
    boundary = np.empty(sorted_scores.size, dtype=bool)
    boundary[0] = True
    np.not_equal(sorted_scores[1:], sorted_scores[:-1], out=boundary[1:])
    group = np.cumsum(boundary) - 1
    starts = np.flatnonzero(boundary)
    ends = np.append(starts[1:], sorted_scores.size)
    # Rang moyen d'un groupe d'ex aequo occupant les positions [start, end).
    mean_rank = (starts + ends + 1) / 2.0
    ranks = np.empty(scores.size, dtype=np.float64)
    ranks[order] = mean_rank[group]
    rank_sum = ranks[truth].sum()
    return float((rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives))


def at_threshold(scores: np.ndarray, truth: np.ndarray, threshold: float) -> dict:
    """Precision, rappel et F1 a un seuil donne."""
    predicted = scores >= threshold
    true_positive = int((predicted & truth).sum())
    false_positive = int((predicted & ~truth).sum())
    false_negative = int((~predicted & truth).sum())
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    return {
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-9),
    }


def annotated_tiles(labels: np.ndarray, tile: int, minimum: int) -> np.ndarray:
    """Masque des tuiles ou quelqu'un a manifestement annote.

    Le critere est volontairement grossier -- une tuile qui porte au moins
    `minimum` pixels d'encre etiquetee -- parce qu'un critere fin serait un reglage
    choisi pour que le chiffre du jour passe. Ce qui compte est que le critere ne
    regarde QUE les etiquettes : il ne peut pas selectionner les tuiles ou la
    prediction se trouve etre bonne, ce qui serait circulaire et flatteur.
    """
    height, width = labels.shape
    mask = np.zeros(labels.shape, dtype=bool)
    for top in range(0, height, tile):
        for left in range(0, width, tile):
            block = labels[top : top + tile, left : left + tile]
            if block.sum() >= minimum:
                mask[top : top + tile, left : left + tile] = True
    return mask


def evaluate(scores: np.ndarray, truth: np.ndarray, name: str, threshold: float) -> dict:
    report = {
        "domaine": name,
        "pixels": int(scores.size),
        "encre_%": float(truth.mean() * 100.0),
        "auc": auc(scores, truth),
    }
    report.update(at_threshold(scores, truth, threshold))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluer une carte d'encre contre un etiquetage partiel.",
        epilog="Rapporte trois domaines et un controle melange ; l'ecart entre eux est le resultat.",
    )
    parser.add_argument("prediction", type=Path, help="carte .npy produite par infer_ink")
    parser.add_argument("labels", type=Path, help="PNG d'etiquetage")
    parser.add_argument("--tile", type=int, default=256, help="cote de tuile (defaut: 256)")
    parser.add_argument(
        "--tile-min", type=int, default=64,
        help="pixels d'encre minimum pour qu'une tuile compte comme annotee",
    )
    parser.add_argument("--threshold", type=float, default=0.0,
                        help="seuil de decision sur le LOGIT (defaut: 0.0, soit p=0,5)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        prediction, labels = load_pair(args.prediction, args.labels)
    except EvaluationError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    covered = np.isfinite(prediction)
    if not covered.any():
        print("erreur : aucun pixel couvert", file=sys.stderr)
        return 3

    # Le seuil par defaut est ZERO, la frontiere de decision du modele lui-meme :
    # la sortie est un logit non calibre, donc zero vaut p = 0,5. C'est le seul
    # point de fonctionnement qu'on ne choisit pas. ⚠ Une mediane serait pire :
    # essayee, elle predit par construction la moitie du segment comme encre et
    # rend une precision de 0,061 qui ne mesure que ce choix.
    threshold = args.threshold

    rows_annotated = labels.sum(axis=1) > 0
    tiles = annotated_tiles(labels, args.tile, args.tile_min)

    domains = {
        "tout le segment": covered,
        "lignes annotees": covered & rows_annotated[:, None],
        f"tuiles annotees ({args.tile}px)": covered & tiles,
    }

    reports = []
    for name, mask in domains.items():
        reports.append(evaluate(prediction[mask], labels[mask], name, threshold))

    # Controle : la meme chaine sur une prediction melangee doit rendre 0,5 partout.
    # Sans lui, rien ne garantit qu'un decoupage n'est pas en train de flatter.
    generator = np.random.default_rng(args.seed)
    shuffled = prediction.copy()
    values = shuffled[covered]
    generator.shuffle(values)
    shuffled[covered] = values
    for name, mask in domains.items():
        control = evaluate(shuffled[mask], labels[mask], f"CONTROLE melange / {name}", threshold)
        reports.append(control)

    summary = {
        "prediction": str(args.prediction),
        "forme": list(prediction.shape),
        "couverture_%": float(covered.mean() * 100.0),
        "seuil": threshold,
        "tuiles_annotees_%": float(tiles.mean() * 100.0),
        "domaines": reports,
    }

    if args.as_json:
        json.dump(summary, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"prediction  : {prediction.shape[0]} x {prediction.shape[1]}")
    print(f"couverture  : {summary['couverture_%']:.2f} %   seuil : {threshold:+.3f}")
    print(f"tuiles annotees : {summary['tuiles_annotees_%']:.1f} % de la surface")
    print()
    header = f"{'domaine':<34}{'pixels':>12}{'encre %':>9}{'AUC':>8}{'prec.':>8}{'rappel':>8}{'F1':>7}"
    print(header)
    print("-" * len(header))
    for r in reports:
        if r["domaine"].startswith("CONTROLE"):
            continue
        print(f"{r['domaine']:<34}{r['pixels']:>12d}{r['encre_%']:>9.2f}"
              f"{r['auc']:>8.3f}{r['precision']:>8.3f}{r['recall']:>8.3f}{r['f1']:>7.3f}")
    print()
    print("Controle -- meme chaine sur une prediction MELANGEE :")
    print("  L'AUC doit tomber a 0,500. La precision, elle, ne tombe PAS a zero :")
    print("  elle tombe au taux d'encre du domaine, parce que tirer au hasard dans")
    print("  une zone dense est mecaniquement plus precis. C'est la ligne de base a")
    print("  laquelle comparer la colonne precision ci-dessus.")
    print()
    print(f"  {'domaine':<32}{'AUC':>8}{'prec. hasard':>14}{'gain':>8}")
    for control, measured in zip(reports[len(domains):], reports[: len(domains)]):
        gain = measured["precision"] / max(control["precision"], 1e-9)
        print(f"  {control['domaine'].split(' / ', 1)[1]:<32}{control['auc']:>8.3f}"
              f"{control['precision']:>14.3f}{gain:>7.1f}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
