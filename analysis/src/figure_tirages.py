#!/usr/bin/env python3
"""Douze rouleaux, six tirages chacun, parametres strictement identiques.

⚠⚠ **Ce que cette figure etablit.** Chaque ligne est un rouleau ; chaque point est une
execution de `vc_grow_seg_from_seed` avec **la meme graine et les memes parametres**. Si le
traceur etait deterministe, chaque ligne serait un point unique.

Aucune ne l'est. ⭐ Et sur quatre lignes un point est **rouge** : le meme appel qui rend une
trace propre cinq fois rend une trace auto-intersectee la sixieme.

⚠ L'axe est en **aire relative a la mediane du rouleau**, pas en cm². Les douze rouleaux
n'ont pas la meme taille de trace (9,4 a 20,0 cm²) : un axe absolu ecraserait les petits et
la dispersion des grands deviendrait invisible. Ce qui est compare ici est la **dispersion**,
pas l'etendue.

⚠ La couleur ne dit PAS « mauvaise trace » : elle dit « auto-intersections non nulles », ce
qui est une condition necessaire de defaut, jamais suffisante (`28` §4 mesure qu'aucun test
geometrique ne voit un saut d'une seule spire dans le cas serre).

⚠ Trace avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python analysis/src/figure_tirages.py
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

LARGEUR, MARGE_H, LIGNE = 1080, 108, 30

# ⚠ La table de traduction de cette figure. Les cles matchent le texte SOURCE.
ANGLAIS = {
    "Le même appel, six fois — sur douze rouleaux":
        "The same call, six times — across thirteen scrolls",
    "Même graine, mêmes paramètres. Si le traceur était déterministe, chaque ":
        "Same seed, same parameters. If the tracer were deterministic, every ",
    "ligne serait un point unique. ": "row would be a single point. ",
    " rouleaux sur ": " scrolls out of ",
    " ne le sont pas.": " are not.",
    "● trace propre": "● clean trace",
    "● auto-intersections non nulles": "● non-zero self-intersections",
    "médiane": "median",
    " croisements": " crossings",
    " tirages · ": " runs · ",
    " mauvais ": " bad ",
    "IC 95 %": "95 % CI",
    " rouleaux où le VERDICT bascule": " scrolls where the VERDICT flips",
    "L'axe est relatif à la médiane de chaque rouleau : les traces vont de 9,4 à ":
        "The axis is relative to each scroll's median: traces span 9.4 to ",
    "20,0 cm², un axe absolu écraserait les petites.":
        "20.0 cm², and an absolute axis would crush the small ones.",
    "Rouge = auto-intersections non nulles. C'est une condition nécessaire de ":
        "Red = non-zero self-intersections. It is a necessary condition for a ",
    "défaut, jamais suffisante.": "defect, never a sufficient one.",
}
X0, LARG = 250, 620
ETENDUE = 0.22          # ±22 % autour de la mediane : au-dela aucun tirage ne sort


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/table_tirages.json")
    ap.add_argument("--sortie", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/images/35_tirages.png")
    ap.add_argument("--anglais", action="store_true",
                    help="écrire la figure en anglais (pour l'article)")
    a = ap.parse_args()
    anglais = a.anglais

    from PIL import Image, ImageDraw, ImageFont
    from langue import Traduisant

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer d'abord table_tirages.py --json", file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    lignes = sorted(d["lignes"], key=lambda l: -l["etendue_relative"])

    hauteur = MARGE_H + len(lignes) * LIGNE + 112
    im = Image.new("RGB", (LARGEUR, hauteur), (255, 255, 255))
    # ⭐ Envelopper l'objet de dessin suffit a traduire la figure entiere.
    art = Traduisant(ImageDraw.Draw(im), ANGLAIS if anglais else None)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    art.text((14, 20), "Le même appel, six fois — sur douze rouleaux",
             fill=(20, 20, 20), font=f_t)
    art.text((14, 42),
             f"Même graine, mêmes paramètres. Si le traceur était déterministe, chaque "
             f"ligne serait un point unique. {d['rouleaux'] - len(d['rouleaux_reproductibles'])}"
             f"/{d['rouleaux']} ne le sont pas.",
             fill=(110, 110, 110), font=f_n)
    art.text((X0, MARGE_H - 26), "● trace propre", fill=(90, 110, 170), font=f_p)
    art.text((X0 + 120, MARGE_H - 26), "● auto-intersections non nulles",
             fill=(200, 40, 40), font=f_p)

    bas = MARGE_H + len(lignes) * LIGNE
    milieu = X0 + LARG // 2
    art.line([milieu, MARGE_H - 12, milieu, bas + 4], fill=(220, 220, 220))
    for t in (-0.2, -0.1, 0.0, 0.1, 0.2):
        x = milieu + int(t / ETENDUE * (LARG // 2))
        art.line([x, bas + 6, x, bas + 12], fill=(180, 180, 180))
        art.text((x - 12, bas + 15), f"{t:+.0%}" if t else "médiane",
                 fill=(120, 120, 120), font=f_p)

    for i, l in enumerate(lignes):
        y = MARGE_H + i * LIGNE
        art.text((14, y + 6), l["rouleau"], fill=(40, 40, 40), font=f_n)
        art.text((104, y + 7), f"±{l['etendue_relative']:.0%}",
                 fill=(130, 130, 130), font=f_p)
        med = l["aire_mediane"]
        # ⚠⚠ Pas de repli si `aires` manque. Reconstruire une plage depuis min/max/mediane
        # donnerait une liste qui ne correspond PAS aux croisements position par position,
        # donc un point rouge sur le mauvais tirage -- une figure fausse et plausible.
        aires = l.get("aires")
        crois = l["croisements"]
        if aires is None or len(aires) != len(crois):
            print(f"REFUS : {l['rouleau']} n'a pas ses aires par tirage — relancer "
                  f"table_tirages.py --json", file=sys.stderr)
            return 2
        art.line([X0, y + 14, X0 + LARG, y + 14], fill=(242, 242, 242))
        for j, aire in enumerate(aires):
            rel = (aire - med) / med if med else 0.0
            x = milieu + int(max(-ETENDUE, min(ETENDUE, rel)) / ETENDUE * (LARG // 2))
            mauvais = j < len(crois) and crois[j] > 0
            c = (200, 40, 40) if mauvais else (90, 110, 170)
            r = 5 if mauvais else 3
            art.ellipse([x - r, y + 14 - r, x + r, y + 14 + r], fill=c)
        pires = [c for c in crois if c > 0]
        if pires:
            art.text((X0 + LARG + 16, y + 7), f"⚠ {max(pires)} croisements",
                     fill=(200, 40, 40), font=f_p)

    art.text((14, bas + 42),
             f"{d['tirages_total']} tirages · {d['mauvais']} mauvais "
             f"({d['taux_mauvais']:.1%}, IC 95 % {d['ic95_bas']:.1%}–{d['ic95_haut']:.1%}) · "
             f"{len(d['rouleaux_bascule'])} rouleaux où le VERDICT bascule",
             fill=(70, 70, 70), font=f_n)
    art.text((14, bas + 62),
             "L'axe est relatif à la médiane de chaque rouleau : les traces vont de 9,4 à "
             "20,0 cm², un axe absolu écraserait les petites.",
             fill=(120, 120, 120), font=f_p)
    art.text((14, bas + 80),
             "Rouge = auto-intersections non nulles. C'est une condition nécessaire de "
             "défaut, jamais suffisante.",
             fill=(150, 90, 20), font=f_p)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    # ⚠⚠ Une figure a moitie traduite a l'air traduite. On REFUSE de l'ecrire.
    if anglais and art.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for _t in art.intraduits():
            print(f"    « {_t} »", file=sys.stderr)
        return 1
    im.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}x{hauteur}, {len(lignes)} rouleaux)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
