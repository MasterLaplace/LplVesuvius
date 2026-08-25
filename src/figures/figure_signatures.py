#!/usr/bin/env python3
"""Quatre traces, quatre signatures — et l'amplitude de profondeur à côté de chacune.

⚠⚠ **Ce que cette figure établit** : le règlement de First Letters demande de vérifier
*« can you visually follow horizontal papyrus fibers across the page »*. C'est un critère
de l'œil. L'**amplitude du profil de profondeur** en est la forme mesurable, et cette
figure ancre les deux bouts de l'échelle sur des images.

- Une surface **parallèle** aux feuilles a une normale qui **traverse** l'empilement :
  son profil de profondeur oscille fortement, et sa face montre des **fibres parallèles**.
- Une surface qui **coupe** l'empilement a une normale qui reste dans une même matière :
  profil plat, et sa face montre des **stratifications concentriques** — le rouleau vu en
  tranche.

⚠ **L'amplitude n'est pas un score de qualité**, et la figure le montre : un troisième cas
d'échec — une trace posée dans le **vide** — rend une amplitude intermédiaire pour une
raison qui n'a rien à voir. C'est une condition **nécessaire**, pas suffisante.

⚠ Les quatre vignettes couvrent la **même surface physique** ; sans quoi on comparerait des
fibres à des fibres vues de plus loin. Chaque volume a sa propre taille de voxel.

⚠ La fenêtre est choisie sur la **couverture**, pas au centre : un segment étroit a son
centroïde dans le vide, et la première version de cette figure a rendu une vignette
entièrement noire pour la trace officielle.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


def fenetre_dense(plan: np.ndarray, cote: int) -> tuple[int, int]:
    """Le coin de la fenêtre `cote`² la mieux couverte, par sommes cumulées."""
    m = (plan > 0).astype(np.float32)
    if m.shape[0] <= cote or m.shape[1] <= cote:
        return 0, 0
    c = np.cumsum(np.cumsum(m, axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    aires = (c[cote:, cote:] - c[:-cote, cote:] - c[cote:, :-cote] + c[:-cote, :-cote])
    # ⚠ Un pas d'echantillonnage : evaluer chaque pixel coute une seconde pour rien.
    pas = max(1, cote // 8)
    reduit = aires[::pas, ::pas]
    iy, ix = np.unravel_index(int(np.argmax(reduit)), reduit.shape)
    return int(iy * pas), int(ix * pas)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quatre signatures de trace, a echelle physique commune.")
    parser.add_argument("sortie", type=Path)
    parser.add_argument("--cas", action="append", nargs=5, required=True,
                        metavar=("TIF", "TITRE", "AMPLITUDE", "VERDICT", "VOXEL_UM"))
    parser.add_argument("--mm", type=float, default=7.0,
                        help="cote physique de chaque vignette")
    parser.add_argument("--px", type=int, default=420)
    parser.add_argument("--legende", default="")
    args = parser.parse_args()

    import tifffile
    from PIL import Image, ImageDraw, ImageFont

    vignettes = []
    for tif, titre, amplitude, verdict, voxel in args.cas:
        um = float(voxel)
        cote = max(64, int(round(args.mm * 1000.0 / um)))
        plan = tifffile.imread(tif).astype(np.float32)
        y0, x0 = fenetre_dense(plan, cote)
        sub = plan[y0:y0 + cote, x0:x0 + cote]
        m = sub > 0
        if not m.any():
            raise RuntimeError(f"{tif} : aucune matiere dans la fenetre choisie")
        bas, haut = np.percentile(sub[m], (2.0, 98.0))
        img = np.clip((sub - bas) / max(haut - bas, 1e-9), 0.0, 1.0)
        img[~m] = 0.0
        vue = Image.fromarray((img * 255).astype(np.uint8), mode="L").convert("RGB")
        vignettes.append({"img": vue.resize((args.px, args.px), Image.LANCZOS),
                          "titre": titre, "amplitude": amplitude, "verdict": verdict,
                          "um": um, "couverture": float(m.mean())})

    marge, ecart, entete, pied = 24, 18, 66, 78
    largeur = marge * 2 + args.px * len(vignettes) + ecart * (len(vignettes) - 1)
    hauteur = entete + args.px + pied
    toile = Image.new("RGB", (largeur, hauteur), (255, 255, 255))
    art = ImageDraw.Draw(toile)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = ImageFont.load_default()

    art.text((marge, 14), "Amplitude du profil de profondeur, et ce que la face montre",
             fill=(20, 20, 20), font=f_t)
    art.text((marge, 34),
             f"Chaque vignette couvre {args.mm:g} × {args.mm:g} mm de surface reelle.",
             fill=(110, 110, 110), font=f_n)

    for i, v in enumerate(vignettes):
        x = marge + i * (args.px + ecart)
        toile.paste(v["img"], (x, entete))
        art.rectangle([x - 1, entete - 1, x + args.px, entete + args.px],
                      outline=(190, 190, 190))
        y = entete + args.px + 8
        art.text((x, y), v["titre"], fill=(30, 30, 30), font=f_n)
        art.text((x, y + 15), f"amplitude {v['amplitude']}", fill=(150, 90, 20), font=f_t)
        art.text((x, y + 33), v["verdict"], fill=(90, 90, 90), font=f_n)

    if args.legende:
        art.text((marge, hauteur - 16), args.legende, fill=(70, 70, 70), font=f_n)

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(args.sortie)
    print(f"ecrit : {args.sortie} ({largeur}x{hauteur})")
    for v in vignettes:
        print(f"  {v['titre']:34} couverture de la fenetre {v['couverture'] * 100:5.1f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
