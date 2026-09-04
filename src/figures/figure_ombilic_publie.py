#!/usr/bin/env python3
"""L'axe ajusté contre l'axe publié — et la mesure qui n'en bouge pas.

Deux panneaux, et le second n'a de sens que grâce au premier :

- **à gauche, les deux axes**, vus de dessus, avec le biais entre eux. ⚠ L'échelle porte une
  barre d'un écart inter-feuilles (154 µm) : sans elle, « 3 mm » est un nombre, alors que ce
  qu'un lecteur doit voir est que **l'écart entre les deux axes vaut des dizaines de feuilles**.
- **à droite, ce que ça change** — rien. Deux paires de barres, sens et écart, sur les deux
  axes. ⚠ L'axe vertical part de zéro pour le sens : une barre tronquée exagérerait n'importe
  quelle différence, et c'est précisément l'ABSENCE de différence qui est le résultat.

⚠ Dessiné avec PIL, comme toutes les figures du dépôt (`figure_commune.py`).

Usage :
    uv run python src/figures/figure_ombilic_publie.py \\
        --json docs/mesures/lombilic_publie.json \\
        --sortie docs/article/figures/ombilic_publie.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), str(RACINE / "src" / "excision")]
from figure_commune import police  # noqa: E402

LARGEUR, HAUTEUR = 470, 320
MARGE = 54

AJUSTE = (31, 111, 67)
PUBLIE = (140, 58, 18)
GRIS = (150, 150, 150)
ENCRE = (40, 40, 40)


def panneau_axes(r: dict):
    """
    @brief Les deux axes vus de dessus, à l'échelle, avec une barre d'un écart inter-feuilles.
    """
    from PIL import Image, ImageDraw
    from le_champ_denroulement import _grille  # noqa: PLC0415
    from le_sens_des_indices import charger, _spires  # noqa: PLC0415
    from lombilic_publie import _centres_publies, charger_axe, voxel_de  # noqa: PLC0415

    c = r["comparaison"]
    charge = charger_axe(c["rouleau"])
    nuages = {k: v for k, v in ((k, charger(x)) for k, x in _spires(c["rouleau"]).items()) if v}
    points, meta = charge
    bords_z, _, ajustes = _grille(nuages)
    publies = _centres_publies(points, (voxel_de(meta) or 9.362) / c["voxel_um"], bords_z)

    a = np.array([ajustes[i] for i in sorted(ajustes)])
    b = np.array([publies[i] for i in sorted(ajustes) if i in publies])

    f_titre, f_petit = police(13, 10)
    img = Image.new("RGB", (LARGEUR, HAUTEUR), "white")
    art = ImageDraw.Draw(img)
    art.text((8, 10), "les deux axes, vus de dessus", fill=ENCRE, font=f_titre)
    art.text((8, 26), f"{c['rouleau']} — {c['points_de_controle']} points annotés à la main",
             fill=(110, 110, 110), font=f_petit)

    tous = np.vstack([a, b])
    lo, hi = tous.min(0) - 40, tous.max(0) + 40
    etendue = float(max(hi - lo))
    px = lambda x: MARGE + (x - lo[0]) * (LARGEUR - 2 * MARGE) / etendue  # noqa: E731
    py = lambda y: MARGE + (y - lo[1]) * (HAUTEUR - 2 * MARGE) / etendue  # noqa: E731

    for pts, couleur, nom in ((a, AJUSTE, "ajusté sur les spires"), (b, PUBLIE, "publié")):
        art.line([(px(p[0]), py(p[1])) for p in pts], fill=couleur, width=2)
        art.ellipse([px(pts[0][0]) - 3, py(pts[0][1]) - 3,
                     px(pts[0][0]) + 3, py(pts[0][1]) + 3], fill=couleur)
    # ⚠ Les traits d'appariement : sans eux on voit deux courbes, avec eux on voit un ECART.
    for p, q in zip(a, b):
        art.line([px(p[0]), py(p[1]), px(q[0]), py(q[1])], fill=(210, 210, 210))

    # la barre d'echelle : un ecart inter-feuilles, pour que « 3 mm » cesse d'etre un nombre
    feuille_vx = 154.1 / c["voxel_um"]
    x0, y0 = MARGE, HAUTEUR - 30
    art.line([x0, y0, x0 + (px(lo[0] + feuille_vx) - px(lo[0])), y0], fill=ENCRE, width=3)
    art.text((x0 + 6, y0 - 13), "1 feuille (154 µm)", fill=ENCRE, font=f_petit)
    art.text((LARGEUR - 200, 44),
             f"biais médian {c['biais_median_um'] / 1000:.2f} mm", fill=(90, 90, 90), font=f_petit)
    art.text((LARGEUR - 200, 58),
             f"= {c['biais_max_en_feuilles']:.0f} feuilles au pire", fill=(90, 90, 90), font=f_petit)
    art.text((MARGE, 44), "ajusté", fill=AJUSTE, font=f_petit)
    art.text((MARGE + 46, 44), "· publié", fill=PUBLIE, font=f_petit)
    return img


def panneau_effet(r: dict):
    """
    @brief Ce que ce biais change à la mesure appariée : rien.
    """
    from PIL import Image, ImageDraw

    c = r["comparaison"]
    f_titre, f_petit = police(13, 10)
    img = Image.new("RGB", (LARGEUR, HAUTEUR), "white")
    art = ImageDraw.Draw(img)
    art.text((8, 10), "ce que ce biais change à la mesure", fill=ENCRE, font=f_titre)
    art.text((8, 26), "rien — c'est ce pour quoi elle est appariée",
             fill=(110, 110, 110), font=f_petit)

    groupes = (
        ("sens (%)", 100.0,
         c["axe_ajuste"]["part_vers_l_exterieur"] * 100,
         c["axe_publie"]["part_vers_l_exterieur"] * 100, "{:.1f} %"),
        ("écart (µm)", 200.0,
         c["axe_ajuste"]["ecart_um"], c["axe_publie"]["ecart_um"], "{:.1f}"),
    )
    largeur_g = (LARGEUR - 2 * MARGE) / len(groupes)
    for i, (nom, plein, va, vp, fmt) in enumerate(groupes):
        base = MARGE + i * largeur_g
        haut, bas = MARGE + 24, HAUTEUR - 52
        art.text((base, HAUTEUR - 34), nom, fill=(90, 90, 90), font=f_petit)
        for j, (v, couleur, etiquette) in enumerate(((va, AJUSTE, "ajusté"),
                                                     (vp, PUBLIE, "publié"))):
            # ⚠ La barre part de ZERO : tronquer l'axe exagererait une difference, or c'est
            # l'ABSENCE de difference qui est le resultat.
            h = (bas - haut) * min(1.0, v / plein)
            x = base + 24 + j * 42
            art.rectangle([x, bas - h, x + 30, bas], fill=couleur)
            art.text((x - 2, bas - h - 14), fmt.format(v), fill=couleur, font=f_petit)
            art.text((x, bas + 4), etiquette, fill=(120, 120, 120), font=f_petit)
        art.line([base, bas, base + largeur_g - 20, bas], fill=(190, 190, 190))
    return img


def dessiner(r: dict, sortie: Path) -> None:
    from PIL import Image

    g, d = panneau_axes(r), panneau_effet(r)
    img = Image.new("RGB", (LARGEUR * 2 + 12, HAUTEUR), "white")
    img.paste(g, (0, 0))
    img.paste(d, (LARGEUR + 12, 0))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    print(f"écrit : {sortie}  ({img.width}×{img.height})")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path, default=Path("docs/mesures/lombilic_publie.json"))
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/article/figures/ombilic_publie.png"))
    a = p.parse_args()
    if not a.json.is_file():
        raise SystemExit(
            f"mesure absente : {a.json}\n"
            f"  la produire :  uv run python src/excision/lombilic_publie.py --json {a.json}")
    r = json.loads(a.json.read_text(encoding="utf-8"))
    if not r.get("comparaison"):
        raise SystemExit("la mesure ne porte pas de comparaison — spires absentes du cache")
    dessiner(r, a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
