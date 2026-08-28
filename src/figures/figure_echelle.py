#!/usr/bin/env python3
"""La meme pile, la meme fenetre, le meme modele — seule l'echelle d'entree change.

⚠⚠ Pourquoi cette figure existe. Le resultat qu'elle porte ne se lit pas dans un tableau :
`sigma 0,017` contre `sigma 0,656` sont deux nombres, et « le modele etait muet parce qu'on
lui donnait du noir » est une IMAGE. La panne a tenu des semaines parce qu'une sortie
constante se lit comme « il n'y a pas d'encre ici » ; la mettre a cote de la sortie corrigee
est ce qui rend l'erreur evidente en une seconde.

⚠ Les deux panneaux partagent leur ETIREMENT, sinon la comparaison ment : etirer chacun sur
sa propre plage rendrait une constante aussi contrastee qu'une vraie carte, ce qui est
exactement l'inverse de ce qu'on montre. La barre d'echelle commune est le sujet de la
figure, pas sa decoration.

Usage :
    uv run python src/figures/figure_echelle.py \\
        --avant data/out/ink_PHerc1447_avant.npy --apres data/out/ink_PHerc1447_corrige.npy \\
        --sortie docs/images/60_echelle_uint8.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SENTINELLE = -9e9


def valides(a):
    import numpy as np

    m = np.isfinite(a) & (a > SENTINELLE)
    return a, m


def panneau(a, m, lo: float, hi: float):
    """Un panneau, etire sur la plage COMMUNE et non sur la sienne."""
    import numpy as np

    img = np.clip((a - lo) / (hi - lo), 0.0, 1.0)
    img[~m] = 0.0
    return (img * 255).astype(np.uint8)


def verifier() -> int:
    """Auto-test HORS LIGNE : ni donnee, ni fichier."""
    import numpy as np

    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    plate = np.full((8, 8), -1.1, dtype=np.float32)
    plate[0, 0] = -1.0
    vive = np.linspace(-1.8, 2.5, 64, dtype=np.float32).reshape(8, 8)
    _, mp = valides(plate)
    _, mv = valides(vive)
    lo, hi = -1.8, 2.5

    pp, pv = panneau(plate, mp, lo, hi), panneau(vive, mv, lo, hi)
    # ⚠⚠ LE controle qui donne son sens a la figure : sur une echelle COMMUNE, la carte
    # plate doit rester plate. C'est precisement ce qu'un etirement par panneau detruirait.
    v("sur l'échelle commune, une carte constante reste plate", int(pp.max() - pp.min()) <= 6)
    v("... et la carte vive occupe toute la plage", int(pv.max() - pv.min()) > 200)
    v("les deux panneaux ont la même taille", pp.shape == pv.shape)

    # Le contre-exemple, explicite : etire sur SA plage, la carte plate devient contrastee.
    seul = panneau(plate, mp, float(plate.min()), float(plate.max()))
    v("étirée sur sa propre plage, elle deviendrait trompeuse", int(seul.max() - seul.min()) > 200)

    # ⚠ Les pixels non couverts sont mis a zero, jamais etires : ils ne sont pas une valeur.
    troue = vive.copy()
    troue[0, :] = np.nan
    a, m = valides(troue)
    v("un pixel non couvert sort noir, pas étiré", int(panneau(a, m, lo, hi)[0, :].max()) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--avant", type=Path)
    ap.add_argument("--apres", type=Path)
    ap.add_argument("--titre-avant", default="normalisée par 65535 (la constante)")
    ap.add_argument("--titre-apres", default="normalisée par le plafond du type")
    ap.add_argument("--sortie", type=Path, default=RACINE / "docs/images/60_echelle_uint8.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.avant or not a.apres:
        ap.error("donner --avant et --apres, ou --verifier")

    import numpy as np
    from PIL import Image, ImageDraw

    cartes = []
    for p in (a.avant, a.apres):
        x = np.load(p)
        cartes.append(valides(x))
    # ⚠ La plage commune vient des DEUX cartes : prendre celle de la seule carte vive
    # ecraserait la plate vers le noir et suggererait qu'elle est vide, alors qu'elle est
    # CONSTANTE — deux defauts differents.
    tout = np.concatenate([c[0][c[1]].ravel() for c in cartes])
    lo, hi = float(np.percentile(tout, 1)), float(np.percentile(tout, 99))

    vues = [Image.fromarray(panneau(x, m, lo, hi), "L").convert("RGB") for x, m in cartes]
    largeur = min(v.width for v in vues)
    vues = [v.resize((largeur, int(v.height * largeur / v.width))) for v in vues]
    marge = 26
    h = max(v.height for v in vues)
    toile = Image.new("RGB", (largeur * 2 + 12, h + marge), (16, 16, 16))
    for i, v in enumerate(vues):
        toile.paste(v, (i * (largeur + 12), marge))
    d = ImageDraw.Draw(toile)
    for i, t in enumerate((a.titre_avant, a.titre_apres)):
        d.text((i * (largeur + 12) + 6, 7), t, fill=(235, 232, 224))
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(a.sortie)
    print(f"étendue commune : {lo:.3f} … {hi:.3f}")
    print(f"figure : {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
