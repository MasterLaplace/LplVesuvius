#!/usr/bin/env python3
"""Ce qu'un maillage plus grossier VOIT d'une surface qui se croise.

⚠⚠ **Ce que cette figure etablit.** La geometrie est identique sur les quatre lignes :
c'est le maillage condamne de `24`, dont on ne change que la DESCRIPTION -- une ligne et
une colonne sur k. Un compte de croisements qui tombe est donc une perte du detecteur,
jamais une amelioration de la surface.

Deux barres par palier, et c'est leur ECART qui porte le resultat :

  - la barre pleine, au reglage par defaut (`--maxedge 60`) ;
  - la barre creuse, filtre desactive (`--maxedge 0`).

Aux deux derniers paliers la premiere tombe a zero pendant que la seconde vaut encore 72
et 49. La difference n'est pas une nuance de reglage : c'est un verdict « propre » rendu
sur zero paire testee.

⚠ Le compte de paires testees est ecrit a cote de chaque barre, en petit. Sans lui, un
zero se lit comme un resultat ; avec lui, il se lit comme une absence de mesure -- et
c'est tout le sujet.

⚠ Trace avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_sensibilite.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, MARGE_H, LIGNE = 1060, 104, 62
X0, LARG = 250, 560


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/mesures/sensibilite_maillage.json")
    ap.add_argument("--sortie", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/images/34_sensibilite.png")
    a = ap.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer d'abord src/outils/sensibilite_maillage.sh",
              file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    lignes = sorted(d["lignes"], key=lambda l: l["facteur"])
    # ⚠⚠ UNE MESURE VIDE N'EST PAS UNE PANNE DE CETTE FIGURE, et le dire vaut mieux qu'un
    # `ValueError: max() iterable argument is empty`. Le cas est arrive : un commit de rangement
    # a ecrase `sensibilite_maillage.json` par un `"lignes": []` le 2026-08-26, et le garde de
    # fraicheur des figures a range celle-ci parmi les « impossible » -- avec six autres qui, en
    # verite, exigent seulement des arguments. Un traceback ne distingue pas les deux cas.
    if not lignes:
        print(f"mesure vide : {a.entree} ne porte aucune ligne.\n"
              "  la refaire : ./src/outils/sensibilite_maillage.sh\n"
              "  ⚠ le maillage source `artefacts/PHerc0358/mesh.tifxyz` n'existe plus, donc la\n"
              "    seule copie de cette mesure est dans l'historique git.", file=sys.stderr)
        return 1
    pic = max(max(l["defaut"]["transverse"], l["brut"]["transverse"]) for l in lignes) or 1

    hauteur = MARGE_H + len(lignes) * LIGNE + 104
    im = Image.new("RGB", (LARGEUR, hauteur), (255, 255, 255))
    art = ImageDraw.Draw(im)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    art.text((14, 20), "La même surface, décrite de plus en plus grossièrement",
             fill=(20, 20, 20), font=f_t)
    art.text((14, 42),
             "Géométrie identique sur les quatre lignes — seule la densité du maillage "
             "change. Toute baisse est une perte du détecteur.",
             fill=(110, 110, 110), font=f_n)
    art.text((X0, MARGE_H - 26), "■ réglage par défaut (--maxedge 60)",
             fill=(190, 90, 40), font=f_p)
    art.text((X0 + 250, MARGE_H - 26), "□ filtre désactivé (--maxedge 0)",
             fill=(90, 110, 170), font=f_p)

    for i, l in enumerate(lignes):
        y = MARGE_H + i * LIGNE
        art.text((14, y + 6), f"k = {l['facteur']}", fill=(40, 40, 40), font=f_n)
        art.text((14, y + 24), f"pas ≈ {int(l['pas_equivalent'])} vx",
                 fill=(130, 130, 130), font=f_p)

        wb = int(l["brut"]["transverse"] / pic * LARG)
        art.rectangle([X0, y + 20, X0 + max(wb, 1), y + 36], outline=(90, 110, 170))
        art.text((X0 + max(wb, 1) + 8, y + 22), str(l["brut"]["transverse"]),
                 fill=(90, 110, 170), font=f_p)

        wd = int(l["defaut"]["transverse"] / pic * LARG)
        art.rectangle([X0, y + 2, X0 + max(wd, 1), y + 18], fill=(190, 90, 40))
        art.text((X0 + max(wd, 1) + 8, y + 4), str(l["defaut"]["transverse"]),
                 fill=(190, 90, 40), font=f_p)

        # ⚠ Le compte de paires est ce qui separe « aucun croisement » de « rien mesure ».
        paires = l["defaut"]["paires"]
        if paires == 0:
            art.text((X0 + 70, y + 4),
                     f"⚠ ZÉRO PAIRE TESTÉE — « propre » ne mesure rien "
                     f"({l['defaut']['jetes']} quads jetés)",
                     fill=(200, 40, 40), font=f_p)
        else:
            art.text((X0 + LARG + 70, y + 12), f"{paires:,} paires testées".replace(",", " "),
                     fill=(150, 150, 150), font=f_p)

    bas = MARGE_H + len(lignes) * LIGNE
    art.text((14, bas + 18),
             "Barre pleine : réglage par défaut. Barre creuse : filtre désactivé. "
             "L'écart entre les deux EST l'effet du filtre.",
             fill=(70, 70, 70), font=f_n)
    art.text((14, bas + 38),
             "Le maillage seul fait tomber 240 → 123 → 72 → 49. Le filtre transforme les "
             "deux derniers en zéros muets.",
             fill=(150, 90, 20), font=f_n)
    art.text((14, bas + 58),
             f"Source : {Path(d['maillage']).name}, tracé à step_size {d['step_size']:.0f} — "
             f"une surface dont on SAIT qu'elle se croise.",
             fill=(120, 120, 120), font=f_p)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}x{hauteur}, {len(lignes)} paliers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
