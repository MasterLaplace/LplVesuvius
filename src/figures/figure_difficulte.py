#!/usr/bin/env python3
"""La carte de difficulté des 13 rouleaux du prix, en image.

⚠⚠ **`docs/16` n'avait que des tableaux**, alors que son résultat est précisément une
**forme** : la médiane de qualité de scan ne sépare rien, et c'est la **queue** qui sépare.
Une colonne de nombres le dit ; un graphique le montre, et la page `Prizes` insiste
partout sur la preuve visuelle.

Deux grandeurs par rouleau, côte à côte, parce que la première est là pour **échouer** :

- `d_prime_median` — la séparabilité typique. ⚠ **Elle n'ordonne rien d'utile** : six des
  treize font aussi bien ou mieux que le témoin, un rouleau qu'on a su lire.
- `part_sous_1` — la part de fenêtres où feuille et interstice ne se séparent pas. Le
  témoin est à **0 %**, les treize entre 4 et 24 %.

⚠ Le **témoin est apparié** : `PHerc0139`, tracé et son titre retrouvé, au protocole exact
des treize. Sans lui, une part de 10 % ne voudrait rien dire — c'est lui qui fixe le zéro.

⚠ Tracé à la main avec PIL, sans matplotlib (absent de cet environnement, et l'ajouter pour
deux barres ferait dépendre une figure d'une pile graphique entière).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARGE_G, MARGE_H, LIGNE, LARGEUR = 168, 82, 26, 1215


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rendre la carte de difficulte des rouleaux du prix.")
    parser.add_argument("dossier", type=Path, help="repertoire des JSON de separabilite")
    parser.add_argument("sortie", type=Path)
    parser.add_argument("--temoin", default="PHerc0139",
                        help="rouleau TRACE servant de zero. ⚠ Sans temoin apparie, une "
                             "part de 10 %% ne veut rien dire")
    args = parser.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    lignes = []
    for f in sorted(args.dossier.glob("*.json")):
        d = json.loads(f.read_text())
        lignes.append({"nom": f.stem, "median": d["d_prime_median"],
                       "part": d["part_sous_1"], "voxel_um": d["voxel_um"]})
    if not lignes:
        print(f"aucun JSON dans {args.dossier}", file=sys.stderr)
        return 1

    temoin = next((l for l in lignes if args.temoin in l["nom"]), None)
    prix = [l for l in lignes if l is not temoin]
    prix.sort(key=lambda l: l["part"])
    ordre = ([temoin] if temoin else []) + prix

    hauteur = MARGE_H + len(ordre) * LIGNE + 92
    im = Image.new("RGB", (LARGEUR, hauteur), (255, 255, 255))
    art = ImageDraw.Draw(im)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except OSError:
        f_t = f_n = ImageFont.load_default()

    art.text((MARGE_G - 90, 20), "Les 13 rouleaux du Grand Prize, et le témoin qui fixe le zéro",
             fill=(20, 20, 20), font=f_t)

    x_med, l_med = MARGE_G, 300
    x_part, l_part = MARGE_G + l_med + 120, 300
    art.text((x_med, MARGE_H - 22), "séparabilité MÉDIANE (d′) — ne sépare rien",
             fill=(110, 110, 110), font=f_n)
    art.text((x_part + 6, MARGE_H - 22), "part de fenêtres INDISSOCIABLES — sépare",
             fill=(150, 90, 20), font=f_n)

    med_max = max(l["median"] for l in ordre) * 1.05
    part_max = max(l["part"] for l in ordre) * 1.05 or 1.0

    for i, l in enumerate(ordre):
        y = MARGE_H + i * LIGNE
        est_temoin = l is temoin
        coul = (40, 110, 60) if est_temoin else (190, 90, 40)
        # ⚠ Le nom vient du STEM du fichier ; celui du temoin porte un prefixe qui le
        # ferait deborder de la marge et donc tronquer en silence.
        court = l["nom"].replace("_TEMOIN_", "")
        nom = f"{court}  ✓ tracé et lu" if est_temoin else court
        art.text((14, y + 5), nom, fill=coul if est_temoin else (40, 40, 40), font=f_n)
        # ⚠ Les deux barres partagent leur hauteur mais PAS leur echelle : ce sont deux
        # grandeurs sans rapport, et une echelle commune suggererait une comparaison.
        w = int(l["median"] / med_max * l_med)
        art.rectangle([x_med, y + 6, x_med + w, y + 18], fill=(175, 178, 185))
        art.text((x_med + l_med + 10, y + 5), f"{l['median']:.2f}",
                 fill=(90, 90, 90), font=f_n)
        w2 = int(l["part"] / part_max * l_part)
        art.rectangle([x_part, y + 6, x_part + max(w2, 1), y + 18], fill=coul)
        art.text((x_part + l_part + 10, y + 5), f"{l['part'] * 100:.0f} %",
                 fill=coul, font=f_n)

    bas = MARGE_H + len(ordre) * LIGNE + 14
    art.line([x_part, MARGE_H - 4, x_part, bas], fill=(215, 215, 215))
    art.text((14, bas + 6),
             "Le témoin PHerc0139 est TRACÉ et son titre retrouvé, au protocole exact des treize.",
             fill=(70, 70, 70), font=f_n)
    art.text((14, bas + 26),
             "À gauche : six des treize font aussi bien ou mieux que lui — la médiane n'ordonne rien.",
             fill=(70, 70, 70), font=f_n)
    art.text((14, bas + 46),
             "À droite : le témoin est à 0 %, les treize entre 4 et 24 %. La difficulté est LOCALE.",
             fill=(150, 90, 20), font=f_n)

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(args.sortie)
    print(f"ecrit : {args.sortie}  ({LARGEUR}x{hauteur}, {len(ordre)} rouleaux)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
