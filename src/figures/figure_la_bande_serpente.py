#!/usr/bin/env python3
"""La coupe profondeur × largeur d'une spire publiée — la bande de matière, et où elle passe.

⚠⚠⚠ POURQUOI CETTE FIGURE. `77` §10 mesure qu'une spire publiée s'écarte de la feuille qu'elle
suit de ~30 µm (σ) et jusqu'à ~100 µm crête à crête. Ce sont des nombres ; la coupe est ce qui
les rend évidents, et c'est elle qui a trouvé le fait. Une pile de 33 couches vue **de côté**
montre la bande de matière **serpenter** au lieu de rester au milieu.

Deux traits sur l'image, et ils portent tout :
- **la ligne médiane** de la dalle, là où la surface publiée prétend être ;
- **la bande suivie**, centre de masse après lissage dans le plan.

⚠ L'écart entre les deux EST le résultat. Sans les deux traits, un lecteur voit une texture ;
avec, il voit une surface qui rate sa cible.

⚠ Le lissage 9 × 9 est celui de la mesure, pas un choix esthétique : sans lui la bande suivie
saute (0,49 feuille de dispersion contre 0,21).

Usage :
    uv run python src/figures/figure_la_bande_serpente.py \\
        --sortie docs/article/figures/bande_serpente.png
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), str(RACINE / "src" / "excision")]
from figure_commune import police  # noqa: E402

ETIREMENT = 9
"""De combien la profondeur est étirée verticalement. ⚠ Une dalle de 33 couches sur 1024 pixels
de large est illisible à l'échelle : sans étirement, l'ondulation qu'on veut montrer fait trois
pixels de haut. L'étirement est **écrit sur la figure**, parce qu'une image dont les deux axes
n'ont pas la même échelle et qui ne le dit pas se lit comme une pente réelle."""


def panneau(nom: str, ligne: int):
    """
    @brief Une coupe profondeur × largeur, avec la médiane de la dalle et la bande suivie.
    """
    from PIL import Image, ImageDraw

    # ⚠⚠⚠ ON REUTILISE LA FONCTION DE LA MESURE, on ne la reecrit pas -- et ce fichier existe
    # tel quel parce que je l'avais d'abord reecrite. Ma version calculait le seuil de fond sur
    # TOUTE la dalle, remplissage compris ; sur `w078`, 41 % de zeros mettent le percentile 20
    # a 0,0 et la bande suivie s'aplatit : sigma 0,55 couche au lieu de 3,72. La figure
    # montrait alors une surface parfaitement placee sur un rouleau ou elle ne l'est pas.
    # C'est le piege nº 27 (« un volume de surface est majoritairement du remplissage »),
    # evite dans la mesure et repaye dans la figure.
    from la_surface_et_la_feuille import _charger, _suivre  # noqa: PLC0415

    pile = _charger(nom)
    if pile is None:
        raise SystemExit(f"couches absentes pour {nom}")
    n, _, W = pile.shape
    centre, valide, _ = _suivre(pile)

    coupe = pile[:, ligne, :]
    normalisee = (coupe - coupe.min()) / max(1e-9, coupe.max() - coupe.min())
    img = Image.fromarray((normalisee * 255).astype(np.uint8))
    img = img.resize((W, n * ETIREMENT), Image.NEAREST).convert("RGB")
    art = ImageDraw.Draw(img)

    f_titre, f_petit = police(13, 10)
    # ⚠ La mediane de la dalle AVANT la bande : c'est la reference, et la tracer apres la
    # ferait passer pour une annotation de la bande.
    y_med = (n / 2) * ETIREMENT
    for x in range(0, W, 14):
        art.line([x, y_med, x + 7, y_med], fill=(90, 160, 255), width=2)
    # ⚠ Tracee UNIQUEMENT la ou il y a de la matiere : relier deux morceaux a travers le
    # remplissage dessinerait un trait droit qui se lit comme une bande plate.
    trait = [(x, centre[ligne, x] * ETIREMENT) for x in range(W) if valide[ligne, x]]
    for a_, b_ in zip(trait, trait[1:]):
        if b_[0] - a_[0] == 1:
            art.line([a_, b_], fill=(255, 120, 40), width=2)

    art.rectangle([0, 0, W, 34], fill=(255, 255, 255))
    art.text((8, 4), f"{nom} — coupe profondeur × largeur, ligne {ligne}",
             fill=(40, 40, 40), font=f_titre)
    art.text((8, 20), f"profondeur étirée ×{ETIREMENT} · {n} couches à 7,91 µm",
             fill=(110, 110, 110), font=f_petit)
    art.text((W - 300, 4), "— milieu de la dalle (la surface publiée)",
             fill=(60, 130, 230), font=f_petit)
    art.text((W - 300, 18), "— la bande de matière, suivie",
             fill=(215, 90, 20), font=f_petit)
    return img


def _ligne_mediane(nom: str) -> int:
    """
    @brief La ligne dont la dispersion de la bande est la plus proche de la médiane.

    ⚠ Choisie et non fixée : la ligne 512 est en dessous de la médiane sur les deux spires
    (2,96 contre 3,32 et 2,16 contre 2,57 couches), donc elle montre le fait plus petit qu'il
    n'est. Une figure doit montrer le cas typique, pas le cas commode.
    """
    from la_surface_et_la_feuille import _charger, _suivre  # noqa: PLC0415

    pile = _charger(nom)
    centre, valide, _ = _suivre(pile)
    lignes = [(y, float(centre[y][valide[y]].std()))
              for y in range(0, pile.shape[1], 16) if valide[y].sum() > 100]
    cible = float(np.median([d for _, d in lignes]))
    return min(lignes, key=lambda t: abs(t[1] - cible))[0]


def main() -> int:
    from PIL import Image

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--spires", nargs="+", default=["PHerc0172_w062", "PHerc0172_w078"])
    # ⚠ La ligne la plus REPRESENTATIVE, pas une ligne fixe : sur les deux spires, la 512
    # est en dessous de la mediane de dispersion, donc elle sous-vend le fait.
    p.add_argument("--ligne", type=int, default=None,
                   help="par défaut, la ligne dont la dispersion est la plus proche de la médiane")
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/article/figures/bande_serpente.png"))
    a = p.parse_args()

    panneaux = [panneau(n, a.ligne if a.ligne is not None else _ligne_mediane(n))
                for n in a.spires]
    largeur = max(x.width for x in panneaux)
    hauteur = sum(x.height for x in panneaux) + 10 * (len(panneaux) - 1)
    img = Image.new("RGB", (largeur, hauteur), "white")
    y = 0
    for x in panneaux:
        img.paste(x, (0, y))
        y += x.height + 10
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({img.width}×{img.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
