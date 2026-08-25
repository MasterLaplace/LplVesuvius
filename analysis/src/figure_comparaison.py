#!/usr/bin/env python3
"""Le classement des treize, avant et apres un echantillonnage trois fois plus dense.

⚠⚠ **Ce que cette figure etablit.** Un tableau de rho de Spearman dit qu'un ordre ne se
reproduit pas ; un graphe de pentes le MONTRE. Chaque rouleau est un segment entre sa place
dans la campagne creuse (15-35 fenetres) et sa place dans la campagne dense (57-115). Si le
classement portait de l'information, les segments seraient a peu pres paralleles.

Ils se croisent tous. ⭐ Et les deux segments epais sont ceux qui decidaient : `PHerc0358`,
que `16` designait comme le premier a attaquer, descend du 1er au 6e rang ; `PHerc0800`,
classe 11e sur 13, remonte au 1er.

⚠ L'axe est la PART, pas le rang : deux rouleaux tres proches en part ont des rangs tres
differents, et un axe de rang ferait passer un ecart de 0,2 point pour un ecart reel. Les
rangs sont ecrits a cote des noms, ils ne structurent pas le dessin.

⚠ Le temoin est trace, et c'est lui qui porte le resultat le plus net : son « 0 % », que
`16` presentait comme une propriete qu'aucun des treize ne partage, devient 4 %.

⚠ Trace avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python analysis/src/figure_comparaison.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, HAUT, BAS = 940, 118, 560
XG, XD = 330, 610


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/comparaison_cartes.json")
    ap.add_argument("--temoin-creux", type=Path,
                    default=Path(__file__).resolve().parents[2]
                    / "docs/carte_separabilite/_TEMOIN_PHerc0139.json")
    ap.add_argument("--sortie", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/images/33_comparaison.png")
    a = ap.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer comparer_cartes.py --json", file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    lignes = d["lignes"]
    tc = json.loads(a.temoin_creux.read_text())["part_sous_1"] if a.temoin_creux.is_file() else None
    td = d["temoin"]["part"]

    pic = max(max(l["creux_part"], l["dense_part"]) for l in lignes) * 1.06
    def y(part: float) -> int:
        return HAUT + int(part / pic * (BAS - HAUT))

    im = Image.new("RGB", (LARGEUR, 660), (255, 255, 255))
    art = ImageDraw.Draw(im)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    art.text((14, 20), "Le même classement, échantillonné trois fois plus dense",
             fill=(20, 20, 20), font=f_t)
    art.text((14, 42),
             f"rho de Spearman = {d['rho']:+.3f} · {d['rangs_changes']}/{len(lignes)} rouleaux "
             f"changent de rang. Si l'ordre portait de l'information, les segments seraient "
             f"parallèles.",
             fill=(150, 90, 20), font=f_n)
    art.text((XG - 76, HAUT - 34), "15 – 35 fenêtres", fill=(110, 110, 110), font=f_n)
    art.text((XD + 12, HAUT - 34), "57 – 115 fenêtres", fill=(110, 110, 110), font=f_n)
    art.line([XG, HAUT - 12, XG, BAS + 12], fill=(215, 215, 215))
    art.line([XD, HAUT - 12, XD, BAS + 12], fill=(215, 215, 215))

    rangs_c = {l["rouleau"]: i + 1 for i, l in
               enumerate(sorted(lignes, key=lambda l: l["creux_part"]))}
    rangs_d = {l["rouleau"]: i + 1 for i, l in
               enumerate(sorted(lignes, key=lambda l: l["dense_part"]))}
    decideurs = {"PHerc0358", "PHerc0800"}

    if tc is not None:
        art.line([XG, y(tc), XD, y(td)], fill=(90, 165, 110), width=3)
        art.text((XG - 210, y(tc) - 7), f"TÉMOIN PHerc0139   {tc:.0%}",
                 fill=(60, 130, 80), font=f_n)
        art.text((XD + 12, y(td) - 7), f"{td:.0%}  ⚠ son « 0 % » n'existe plus",
                 fill=(60, 130, 80), font=f_n)

    # ⚠ Les segments se posent aux VRAIES ordonnees ; seules les ETIQUETTES sont ecartees
    # quand elles se recouvrent. Deplacer les points ferait mentir la figure sur les parts ;
    # laisser les etiquettes se superposer la rend illisible la ou trois rouleaux sont a
    # 0,2 point l'un de l'autre -- ce qui est justement le fait a montrer.
    def ecarter(paires: list[tuple[str, float]], hauteur_ligne: int = 15) -> dict[str, int]:
        ordonne = sorted(paires, key=lambda t: t[1])
        place: dict[str, int] = {}
        dernier = -10**6
        for nom, yy in ordonne:
            pose = max(int(yy), dernier + hauteur_ligne)
            place[nom] = pose
            dernier = pose
        return place

    yg = ecarter([(l["rouleau"], y(l["creux_part"]) - 7) for l in lignes])
    yd = ecarter([(l["rouleau"], y(l["dense_part"]) - 7) for l in lignes])

    for l in lignes:
        nom = l["rouleau"]
        gros = nom in decideurs
        c = (185, 85, 35) if gros else (168, 178, 195)
        art.line([XG, y(l["creux_part"]), XD, y(l["dense_part"])],
                 fill=c, width=3 if gros else 1)
        art.ellipse([XG - 3, y(l["creux_part"]) - 3, XG + 3, y(l["creux_part"]) + 3], fill=c)
        art.ellipse([XD - 3, y(l["dense_part"]) - 3, XD + 3, y(l["dense_part"]) + 3], fill=c)
        # Un trait fin relie l'etiquette ecartee a son point, sinon un decalage de 15 px
        # ferait lire la mauvaise valeur.
        for x_txt, x_pt, y_txt, y_pt in ((XG - 14, XG, yg[nom], y(l["creux_part"])),
                                         (XD + 8, XD, yd[nom], y(l["dense_part"]))):
            if abs(y_txt + 7 - y_pt) > 3:
                art.line([x_txt, y_txt + 7, x_pt, y_pt], fill=(228, 228, 228))
        art.text((XG - 200, yg[nom]),
                 f"{nom}  {rangs_c[nom]:>2}ᵉ  {l['creux_part']:>5.1%}",
                 fill=(40, 40, 40) if gros else (130, 130, 130), font=f_p)
        art.text((XD + 12, yd[nom]),
                 f"{l['dense_part']:>5.1%}  {rangs_d[nom]:>2}ᵉ  {nom}",
                 fill=(40, 40, 40) if gros else (130, 130, 130), font=f_p)

    # ⚠ Les rangs de la legende sont DERIVES des donnees, jamais ecrits a la main : la
    # premiere version en avait un faux (« 11e » pour un rouleau que l'artefact classe 10e),
    # et une legende fausse sur une figure juste est le pire des deux mondes.
    n_tot = len(lignes)
    art.text((14, BAS + 44),
             f"En orange : les deux rouleaux qui décidaient. PHerc0358 était désigné « le "
             f"premier à attaquer » ; il passe {rangs_d['PHerc0358']}ᵉ.",
             fill=(185, 85, 35), font=f_n)
    art.text((14, BAS + 64),
             f"PHerc0800, classé {rangs_c['PHerc0800']}ᵉ sur {n_tot}, devient le meilleur du "
             f"lot. Un ordre réel ne change pas de sujet quand on triple l'échantillonnage.",
             fill=(70, 70, 70), font=f_n)
    art.text((14, BAS + 84),
             f"⚠ 12 des 13 estimations denses tombent dans l'intervalle creux : le sondage "
             f"creux était BRUITÉ, pas biaisé.",
             fill=(120, 120, 120), font=f_p)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}x660, {len(lignes)} rouleaux)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
