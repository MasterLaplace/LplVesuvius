#!/usr/bin/env python3
"""Fabriquer une image de calibrage a DEUX panneaux, temoin inclus.

⚠ Pourquoi ce fichier existe : la premiere version du protocole demandait a un
humain d'envoyer trois images dans trois messages separes, dans un ordre precis, en
notant chaque reponse. Elle a echoue au premier essai -- les trois images sont
parties ensemble et le modele a rendu UNE reponse, ce qui rend impossible de savoir
s'il aurait refuse le temoin negatif.

La faute est dans la conception, pas dans l'execution : **un protocole dont la
validite depend d'un humain qui sequence correctement est un protocole qui echouera.**

Le remede est le meme que partout dans ce depot : rendre le controle impossible a
sauter. Ici le temoin negatif est mis DANS la meme image que le test, cote a cote.
Un seul envoi suffit, il n'y a plus d'ordre a respecter, et un modele qui decrit du
texte dans les deux panneaux s'est disqualifie lui-meme en une reponse.

Le cote qui porte le texte est tire au sort par une graine ecrite dans le nom du
fichier de reponse -- pas dans l'image -- pour qu'un modele ne puisse pas le deduire
et qu'un humain ne puisse pas se tromper en depouillant.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

SEPARATOR_PX = 24
"""Largeur de la barre entre panneaux. Assez large pour etre non ambigue."""

SEPARATOR_VALUE = 0
"""Barre NOIRE. Un separateur clair se confondrait avec le support ; un separateur
gris se confondrait avec le « pas regarde »."""


def load_panel(scores: np.ndarray, top: int, height: int, reduce: int,
               low: float, high: float) -> np.ndarray:
    """Un panneau, rendu exactement comme les images livrees ailleurs.

    ⚠ L'echelle de gris est calculee sur le SEGMENT ENTIER et non panneau par
    panneau : normaliser chaque panneau separement etirerait le contraste du
    panneau vierge jusqu'a ce que son bruit ressemble a de l'encre, ce qui
    fabriquerait le faux positif qu'on cherche justement a mesurer.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from render_segment import reduce_max, to_image

    covered = np.isfinite(scores)
    lo = float(np.quantile(scores[covered], low))
    hi = float(np.quantile(scores[covered], high))
    crop = scores[top : top + height]
    reduced = reduce_max(crop, reduce)
    normalised = np.clip((reduced - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    out = np.full(reduced.shape, 128, dtype=np.uint8)
    finite = np.isfinite(reduced)
    out[finite] = (255.0 * (1.0 - normalised[finite])).astype(np.uint8)
    return np.rot90(out, k=3)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Image de calibrage a deux panneaux, temoin negatif inclus.",
        epilog="Un seul envoi suffit : il n'y a plus d'ordre a respecter.",
    )
    parser.add_argument("prediction", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--text", required=True, metavar="HAUT:HAUTEUR",
                        help="region PORTANT du texte")
    parser.add_argument("--blank", required=True, metavar="HAUT:HAUTEUR",
                        help="region VIERGE, le temoin negatif")
    parser.add_argument("--reduce", type=int, default=2)
    parser.add_argument("--low", type=float, default=0.02)
    parser.add_argument("--high", type=float, default=0.995)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    from PIL import Image

    scores = np.load(args.prediction)
    panels = {}
    for name, spec in (("texte", args.text), ("vierge", args.blank)):
        top, height = (int(v) for v in spec.split(":"))
        panels[name] = load_panel(scores, top, height, args.reduce, args.low, args.high)

    if panels["texte"].shape[0] != panels["vierge"].shape[0]:
        print("erreur : les deux regions doivent avoir la meme hauteur apres rotation, "
              "sinon la difference de forme trahit le temoin", file=sys.stderr)
        return 2

    generator = np.random.default_rng(args.seed)
    text_left = bool(generator.integers(0, 2))
    left, right = (("texte", "vierge") if text_left else ("vierge", "texte"))

    bar = np.full((panels[left].shape[0], SEPARATOR_PX), SEPARATOR_VALUE, dtype=np.uint8)
    image = np.concatenate([panels[left], bar, panels[right]], axis=1)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(args.out)

    key = {
        "image": args.out.name,
        "gauche": left,
        "droite": right,
        "attendu": f"des lettres a {'gauche' if text_left else 'droite'}, "
                   f"AUCUNE LETTRE VISIBLE a {'droite' if text_left else 'gauche'}",
        "seed": args.seed,
    }
    key_path = args.out.with_suffix(".reponse.json")
    key_path.write_text(json.dumps(key, indent=2, ensure_ascii=False) + "\n")

    print(f"{args.out}  {image.shape[1]} x {image.shape[0]}")
    print(f"cle de reponse : {key_path}  (⚠ ne pas ouvrir avant de depouiller)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
