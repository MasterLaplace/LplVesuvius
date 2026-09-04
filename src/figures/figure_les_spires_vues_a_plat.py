#!/usr/bin/env python3
"""Les spires d'une tranche, dépliées en (angle, rayon) — l'angle de caméra qui montre la panne.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `77` §7 mesure que le prédicat d'identité sépare sur
`PHerc0139` et pas sur `PHerc0172`, et **quatre causes candidates ont été testées et rejetées**
(couverture angulaire, dérive de l'axe, spires par cellule, monotonie des rayons). À court
d'hypothèses, on regarde.

Le bon angle est celui dans lequel le champ **travaille** : pour une tranche de hauteur, le
rayon de chaque spire en fonction de l'angle. Le champ interpole verticalement dans ce plan —
il lit, à un angle donné, la suite des rayons et cherche entre lesquels tombe un point. Si
cette suite est propre, il sépare ; si elle est emmêlée, il ne peut pas.

⚠ **C'est un instrument de diagnostic, pas une gate.** Il ne folde rien et ne décide rien. Sa
seule règle est celle de tout visuel du dépôt : il porte la commande qui le régénère.

Usage :
    uv run python src/figures/figure_les_spires_vues_a_plat.py \\
        --sortie docs/article/figures/spires_a_plat.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), str(RACINE / "src" / "excision")]
from figure_commune import police  # noqa: E402

LARGEUR, HAUTEUR = 470, 330
MARGE_G, MARGE_D, MARGE_H, MARGE_B = 52, 14, 44, 40

ENCRE = (40, 40, 40)


def _teinte(i: int, n: int) -> tuple[int, int, int]:
    """
    @brief Une couleur par spire, du centre (froid) vers l'extérieur (chaud).

    ⚠ Un dégradé continu et non des couleurs distinctes : ce qu'on cherche à voir est si
    l'ORDRE des spires est respecté. Des couleurs arbitraires rendraient un croisement
    invisible, un dégradé le rend criant.
    """
    t = i / max(1, n - 1)
    return (int(30 + 200 * t), int(70 + 60 * abs(0.5 - t) * 2), int(220 - 190 * t))


def panneau(rouleau: str, tranche_cible: float = 0.5):
    """
    @brief Le rayon de chaque spire en fonction de l'angle, pour UNE tranche de hauteur.
    """
    from PIL import Image, ImageDraw

    import le_champ_denroulement as champ
    from le_sens_des_indices import SECTEURS, charger, _spires

    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    bords_z, _, centres = champ._grille(nuages)
    rayons = {k: champ._rayons(n, bords_z, _, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}
    indices = sorted(rayons)

    # ⚠ La tranche la mieux remplie autour de la position visee, pas la position elle-meme :
    # une tranche a moitie vide montrerait des trous qui sont ceux de l'echantillonnage, pas
    # ceux du rouleau.
    tranches = sorted({t for v in rayons.values() for (t, _) in v})
    vise = tranches[int(tranche_cible * (len(tranches) - 1))]
    remplissage = {t: sum(1 for v in rayons.values() for (tt, _) in v if tt == t)
                   for t in tranches[max(0, vise - 3):vise + 4]}
    tranche = max(remplissage, key=remplissage.get)

    f_titre, f_petit = police(13, 10)
    img = Image.new("RGB", (LARGEUR, HAUTEUR), "white")
    art = ImageDraw.Draw(img)
    art.text((8, 10), f"{rouleau} — une tranche, dépliée", fill=ENCRE, font=f_titre)

    courbes = {}
    for k in indices:
        pts = sorted((s, r) for (t, s), r in rayons[k].items() if t == tranche)
        if len(pts) >= 8:
            courbes[k] = pts
    if not courbes:
        art.text((MARGE_G, HAUTEUR // 2), "aucune spire dans cette tranche", fill=ENCRE)
        return img

    tous = [r for pts in courbes.values() for _, r in pts]
    rmin, rmax = min(tous), max(tous)
    art.text((8, 26), f"tranche {tranche} · {len(courbes)} spires · "
             f"rayon {rmin:.0f}–{rmax:.0f} vx", fill=(110, 110, 110), font=f_petit)

    px = lambda s: MARGE_G + (s - 1) * (LARGEUR - MARGE_G - MARGE_D) / max(1, SECTEURS - 1)  # noqa: E731
    py = lambda r: (HAUTEUR - MARGE_B
                    - (r - rmin) * (HAUTEUR - MARGE_H - MARGE_B) / max(1e-9, rmax - rmin))  # noqa: E731

    art.rectangle([MARGE_G, MARGE_H, LARGEUR - MARGE_D, HAUTEUR - MARGE_B],
                  outline=(215, 215, 215))
    for j, k in enumerate(sorted(courbes)):
        couleur = _teinte(j, len(courbes))
        art.line([(px(s), py(r)) for s, r in courbes[k]], fill=couleur, width=1)

    art.text((MARGE_G, HAUTEUR - 26), "angle  0°", fill=(120, 120, 120), font=f_petit)
    art.text((LARGEUR - MARGE_D - 34, HAUTEUR - 26), "360°", fill=(120, 120, 120), font=f_petit)
    art.text((6, MARGE_H - 2), "rayon", fill=(120, 120, 120), font=f_petit)
    # ⚠ Le haut est le GRAND rayon : `py` envoie `rmin` en bas. J'avais inverse les deux
    # etiquettes a la premiere version -- une figure mal legendee est pire qu'aucune figure,
    # parce qu'elle se lit avec confiance.
    art.text((MARGE_G + 4, MARGE_H + 4), "extérieur",
             fill=_teinte(len(courbes) - 1, len(courbes)), font=f_petit)
    art.text((MARGE_G + 4, HAUTEUR - MARGE_B - 14), "intérieur",
             fill=_teinte(0, len(courbes)), font=f_petit)
    return img


def main() -> int:
    from PIL import Image

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleaux", nargs="+", default=["PHerc0139", "PHerc0172"])
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/article/figures/spires_a_plat.png"))
    a = p.parse_args()

    panneaux = [panneau(r) for r in a.rouleaux]
    img = Image.new("RGB", (LARGEUR * len(panneaux) + 12 * (len(panneaux) - 1), HAUTEUR),
                    "white")
    for i, x in enumerate(panneaux):
        img.paste(x, (i * (LARGEUR + 12), 0))
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({img.width}×{img.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
