#!/usr/bin/env python3
"""Deux juges, quatre rouleaux — et ils ne classent pas pareil.

⚠⚠ **Ce que cette figure etablit.** Sur chaque rouleau qui bascule on tient le tirage que
l'axe geometrique CONDAMNE et des tirages qu'il declare propres, meme graine, memes
parametres. Si les deux axes s'accordaient, le point rouge serait a droite -- le pire selon
la profondeur aussi.

Il ne l'est jamais. Sur deux des quatre rouleaux il est meme le plus a GAUCHE, c'est-a-dire
le meilleur.

⚠ L'axe horizontal est `au_bord_intensite`, PAS l'ecart a la trace. L'ecart est censure :
il bute sur `(couches / 2) × voxel` pour la majorite des tirages, donc ses ex-aequo sont des
ex-aequo par CENSURE et non par mesure. `au_bord` ne l'est pas, et c'est sur elle que la
conclusion repose.

⚠ Un rouleau par ligne, et l'echelle est COMMUNE : ces valeurs sont des fractions de
fenetres, donc directement comparables. Une echelle par ligne suggererait qu'un rouleau a
plus de dynamique qu'un autre, ce qui serait un artefact de mise en page.

⚠ Trace avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_deux_axes.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, MARGE_H, LIGNE = 1020, 118, 46
X0, LARG = 250, 560


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--etroite", type=Path, default=racine / "docs/second_axe_21.json")
    ap.add_argument("--large", type=Path, default=racine / "docs/second_axe_41.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/37_deux_axes.png")
    a = ap.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    for f in (a.etroite, a.large):
        if not f.is_file():
            print(f"absent : {f} — lancer table_second_axe.py --json", file=sys.stderr)
            return 1
    jeux = [("41 couches", json.loads(a.large.read_text())),
            ("21 couches", json.loads(a.etroite.read_text()))]

    # Les rouleaux testables : ceux qui ont un mauvais tirage ET des propres.
    def par_rouleau(d):
        out = {}
        for l in d["lignes"]:
            out.setdefault(l["rouleau"], []).append(l)
        return {r: v for r, v in out.items()
                if any(x["transverse"] for x in v) and any(not x["transverse"] for x in v)}

    rouleaux = sorted(par_rouleau(jeux[0][1]))
    hauteur = MARGE_H + len(rouleaux) * len(jeux) * LIGNE + 118
    im = Image.new("RGB", (LARGEUR, hauteur), (255, 255, 255))
    art = ImageDraw.Draw(im)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    art.text((14, 20), "Le tirage que la géométrie condamne, jugé par la profondeur",
             fill=(20, 20, 20), font=f_t)
    # ⚠ Le compte d'accords est DERIVE des donnees, jamais ecrit a la main : la premiere
    # version annoncait « il ne l'est sur aucun des quatre » alors que la figure montre le
    # contraire sur une ligne. Une legende fausse sur une figure juste est le pire des deux
    # mondes -- et c'est la figure qui l'a fait voir, pas la relecture.
    accords = total = 0
    for _, dd in jeux:
        prr = par_rouleau(dd)
        for _, lots in prr.items():
            total += 1
            pm = max(l["au_bord"] for l in lots if l["transverse"])
            pp = max(l["au_bord"] for l in lots if not l["transverse"])
            accords += 1 if pm > pp else 0
    art.text((14, 42),
             f"S'ils s'accordaient, le point rouge serait le plus à droite — le pire selon "
             f"les deux. Il l'est {accords} fois sur {total}.",
             fill=(150, 90, 20), font=f_n)
    art.text((X0, MARGE_H - 34), "● condamné par l'axe géométrique",
             fill=(200, 40, 40), font=f_p)
    art.text((X0 + 220, MARGE_H - 34), "○ déclaré propre", fill=(90, 110, 170), font=f_p)
    art.text((X0 + 360, MARGE_H - 34), "→ pire selon la profondeur",
             fill=(130, 130, 130), font=f_p)

    y = MARGE_H
    for nom_jeu, d in jeux:
        pr = par_rouleau(d)
        art.text((14, y - 4), nom_jeu, fill=(90, 90, 90), font=f_n)
        for r in rouleaux:
            lots = pr.get(r, [])
            art.text((14, y + 16), f"  {r}", fill=(40, 40, 40), font=f_p)
            art.line([X0, y + 22, X0 + LARG, y + 22], fill=(238, 238, 238))
            for l in lots:
                x = X0 + int(min(1.0, l["au_bord"]) * LARG)
                if l["transverse"]:
                    art.ellipse([x - 6, y + 16, x + 6, y + 28], fill=(200, 40, 40))
                else:
                    art.ellipse([x - 5, y + 17, x + 5, y + 27], outline=(90, 110, 170), width=2)
            y += LIGNE
        y += 6

    bas = y
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = X0 + int(t * LARG)
        art.line([x, bas, x, bas + 6], fill=(180, 180, 180))
        art.text((x - 12, bas + 9), f"{t:.0%}", fill=(120, 120, 120), font=f_p)
    art.text((X0 + LARG // 2 - 90, bas + 28),
             "part des fenêtres dont le pic est au bord de la pile — plus à droite = pire",
             fill=(120, 120, 120), font=f_p)
    art.text((14, bas + 52),
             f"{accords} accord sur {total} comparaisons (deux tailles de fenêtre × "
             f"{len(rouleaux)} rouleaux), là où le hasard seul en donnerait ~{total // 2}.",
             fill=(70, 70, 70), font=f_n)
    art.text((14, bas + 72),
             "⚠ L'écart à la trace n'est pas tracé : il est censuré par la fenêtre rendue. "
             "Cette statistique-ci ne l'est pas.",
             fill=(150, 90, 20), font=f_p)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}x{hauteur}, {len(rouleaux)} rouleaux × {len(jeux)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
