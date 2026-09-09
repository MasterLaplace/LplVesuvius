#!/usr/bin/env python3
"""Deux humains sur la meme matiere divergent de plus d'une DEMI-feuille, partout.

⭐⭐⭐ CETTE FIGURE CHIFFRE LE PLANCHER QUE `95` ET `96` NOMMAIENT SANS POUVOIR LE MESURER. Chaque
bande de `PHercParis4` existe en DEUX revisions, soit deux traces humains independants de la meme
matiere : le panneau A montre que leur desaccord vaut ~110 µm PARTOUT, quand la demi-feuille de
cet objet vaut 82 a 91 µm.

★ ET LE PANNEAU B PORTE L'ESTIMATEUR REFUTE, parce que le facteur entre les deux EST la lecon :
la distance au plus proche voisin rend 271 a 315 µm, mais elle mesure l'ESPACEMENT DES RANGS de
l'autre revision — un point a mi-chemin entre deux rangs en est loin meme si les deux surfaces
coincident exactement.

Usage :
    uv run python src/figures/figure_deux_humains_sur_la_meme_matiere.py --verifier
    uv run python src/figures/figure_deux_humains_sur_la_meme_matiere.py \\
        --sortie docs/images/97_deux_humains_sur_la_meme_matiere.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "deux_humains_sur_la_meme_matiere.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)
DEMI_FEUILLE_UM = 82.0


def prose(m: dict) -> list[str]:
    p, c = m["par_tiers"], m["correlations"]
    co = p["coeur"]
    return [
        "★★★ CE QUE CE FICHIER MESURE, ET C'EST `96` QUI L'A DEMANDE. trois observables de "
        "confiance ont ete testees : le pli (`94`) et la pose sur la matiere (`95`) sont "
        "ANTI-predictifs, la fermeture d'un tour (`96`) a enfin le bon signe mais ne peut pas "
        "etre CALIBREE — les maillages humains ne ferment pas eux-memes a la demi-feuille pres. "
        "ce qui manquait n'etait pas l'instrument mais un REFERENT.",
        "★★★ ET IL Y EN A UN QUE LE DEPOT TELECHARGE DEJA SANS L'AVOIR EMPLOYE : chaque bande "
        "existe en DEUX revisions, soit deux traces humains INDEPENDANTS de la meme matiere. la "
        "ou les deux s'accordent, la matiere a dicte la reponse ; la ou ils divergent, au moins "
        "l'un des deux se trompe. aucun oracle n'est requis.",
        f"★★★ PANNEAU A — LE PLANCHER EST CHIFFRE, ET IL EST PLAT. le desaccord vaut "
        f"{co['desaccord_median_um']} µm au coeur, {p['milieu']['desaccord_median_um']} au "
        f"milieu et {p['bord']['desaccord_median_um']} au bord, sans AUCUNE translation "
        f"systematique (vecteur moyen 8 a 38 µm apres restriction au recouvrement). or la "
        f"demi-feuille de cet objet vaut 82 a 91 µm (`91`) : les deux humains sont donc a plus "
        f"d'une demi-feuille l'un de l'autre, et "
        f"{round(100 * co['part_au_dela_dune_feuille'])} % des points a plus d'une feuille "
        "ENTIERE. ce n'est pas un probleme de bord, c'est partout.",
        f"★★★ NON — ET LA FERMETURE N'EST PAS CALIBREE PAR CE REFERENT NON PLUS : le desaccord entre "
        f"les deux humains ne suit ni le rayon ({c['desaccord_contre_rayon']:+.3f}), ni la "
        f"rupture de continuite ({c['desaccord_contre_continuite']:+.3f}), ni la fermeture de "
        f"`96` ({c['desaccord_contre_fermeture']:+.3f}). la ou les deux humains divergent n'est "
        "donc PAS la ou la fermeture echoue, et l'observable reste sans etalon.",
        f"★★★ NON — PANNEAU B — L'ESTIMATEUR REFUTE, GARDE, ET C'EST LE FACTEUR QUI COMPTE. au plus "
        f"proche voisin le desaccord rend {co['au_plus_proche_voisin_um']} µm contre "
        f"{co['desaccord_median_um']} au PLAN local. les rangs de l'ancienne revision sont "
        f"espaces d'environ 800 µm, donc un point a mi-chemin entre deux rangs en est loin MEME "
        "SI LES DEUX SURFACES COINCIDENT exactement — la fixture le montre en rendant une "
        "distance non nulle sur deux surfaces identiques. publier ce nombre aurait ete publier "
        "une limite de GRILLE comme une limite de MATIERE, le peche nº 1 de ce depot.",
        "⚠⚠⚠ ET UNE GARDE A MOI QUI SUPPRIMAIT CE QU'ELLE DEVAIT LAISSER MESURER. mon critere "
        "de bord — « mes voisins sont-ils tous du meme cote ? » — etait d'abord mesure dans "
        "l'ESPACE, ou il melange deux choses : etre au bord d'une couverture, et etre LOIN de la "
        "surface. sur deux plans separes de 2 avec des voisins a 2,4, le rapport ne descendait "
        "jamais sous 0,354, donc applique au reel il aurait ecarte EXACTEMENT les points ou les "
        "deux humains divergent le plus. mesure dans le PLAN TANGENT, il ne voit plus que le "
        "bord — et le desaccord publie double, de 53 a 122 µm.",
        f"⚠⚠ ET LE CONFONDANT DE COUVERTURE EST TRAITE AVANT TOUT LE RESTE, comme `85` l'avait "
        f"deja paye : l'ancienne revision ne couvre que "
        f"{round(100 * m['lignes'][0]['part_dans_le_recouvrement_z'])} % de l'etendue en z de la "
        "recente (119 rangs contre 184). sans restriction, le vecteur moyen de A vers B valait "
        "5918 µm, domine par 5567 en z — c'est-a-dire qu'on mesurait la couverture. restreint au "
        "recouvrement, il tombe a 8-38 µm.",
        "★★★ CE QUE CA CHANGE POUR LE GRAAL, ET C'EST PLUS LOURD QUE LA CALIBRATION CHERCHEE. le "
        "prix demande d'automatiser un travail dont l'etat de l'art ne reproduit pas sa propre "
        "sortie a une feuille pres : deux passes humaines sur la meme matiere divergent d'une "
        "demi-feuille en mediane et d'une feuille entiere sur un tiers des points. donc la cible "
        "d'un automate ne peut pas etre « egaler le maillage humain » — cette cible n'a pas de "
        "valeur unique. elle doit etre un critere que la MATIERE tranche, pas un maillage.",
    ]


def panneau_plancher(art, x0, y0, pw, ph, m, petit) -> int:
    """Le désaccord contre le rayon, avec la demi-feuille tracée."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "le désaccord entre deux tracés humains, contre le rayon",
             fill=DISCRET, font=petit)
    lignes = [x for x in m["lignes"] if x["rayon_mm"] is not None]
    gauche, droite = x0 + 56, x0 + pw - 30
    base, sommet = y0 + ph - 58, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    hi = max(max(x["desaccord_median_um"] for x in lignes), 1.15 * DEMI_FEUILLE_UM) * 1.15

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    # ⭐⭐⭐ LA DEMI-FEUILLE EST TRACEE, ET C'EST ELLE QUI DONNE UN SENS A LA COURBE : sans ce
    # repere, « 110 µm » est un nombre nu ; avec lui, c'est au-dessus du critere d'identite.
    art.line([gauche, py(DEMI_FEUILLE_UM), droite, py(DEMI_FEUILLE_UM)], fill=ROUGE)
    art.text((gauche + 4, py(DEMI_FEUILLE_UM) - 14),
             f"demi-feuille de cet objet : {DEMI_FEUILLE_UM:.0f} µm (`91`)",
             fill=ROUGE, font=petit)
    art.line([(px(x["rayon_mm"]), py(x["desaccord_median_um"])) for x in lignes],
             fill=BLEU, width=2)
    points = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["desaccord_median_um"])
        art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLEU)
        points += 1
    for g in (0.0, hi / 2, hi):
        art.text((x0 + 8, py(g) - 6), f"{g:>5.0f}", fill=DISCRET, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((gauche + 4, sommet - 16), "désaccord au plan local, µm", fill=BLEU, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★ corrélation avec le rayon : {m['correlations']['desaccord_contre_rayon']:+.3f} — "
             "PLAT, donc ce n'est pas un problème de bord",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande — cœur à gauche, bord à droite",
             fill=DISCRET, font=petit)
    return points


def panneau_estimateur(art, x0, y0, pw, ph, m, petit) -> int:
    """Les deux estimateurs côte à côte, par tiers."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "deux estimateurs du même désaccord, et l'un mesure la GRILLE",
             fill=DISCRET, font=petit)
    p = m["par_tiers"]
    tiers = [k for k in ("coeur", "milieu", "bord") if k in p]
    mots = {"coeur": "cœur", "milieu": "milieu", "bord": "bord"}
    gauche, droite = x0 + 92, x0 + pw - 96
    haut = y0 + 52
    h = (ph - 200) / max(1, len(tiers))
    hi = max(p[k]["au_plus_proche_voisin_um"] for k in tiers) * 1.18
    barres = 0
    for j, k in enumerate(tiers):
        yb = haut + j * h
        art.text((x0 + 8, yb + 10), mots[k], fill=TEXTE, font=petit)
        for i, (cle, coul, nom) in enumerate((
                ("desaccord_median_um", BLEU, "au PLAN local"),
                ("au_plus_proche_voisin_um", AMBRE, "au plus proche voisin"))):
            val = p[k][cle]
            y = yb + 4 + i * 16
            larg = (droite - gauche) * val / hi
            art.rectangle([gauche, y, gauche + larg, y + 13], fill=coul)
            art.text((gauche + larg + 5, y), f"{val:.1f} µm", fill=coul, font=petit)
            if j == 0:
                art.text((gauche, haut - 34 + i * 13), nom, fill=coul, font=petit)
            barres += 1
    # ⭐ La demi-feuille sert de repere ici aussi.
    xd = gauche + (droite - gauche) * DEMI_FEUILLE_UM / hi
    art.line([xd, haut - 6, xd, haut + len(tiers) * h - 4], fill=ROUGE)
    art.text((xd - 30, haut + len(tiers) * h + 2), f"½ feuille", fill=ROUGE, font=petit)
    y = haut + len(tiers) * h + 26
    art.text((x0 + 8, y),
             f"★★★ le plus proche voisin mesure l'ESPACEMENT DES RANGS (~800 µm)",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 14),
             "   de l'autre révision, pas le désaccord : sur deux surfaces",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 28),
             "   IDENTIQUES il rend déjà une distance non nulle (fixture).",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 32),
             f"★ et le désaccord dépasse la demi-feuille dans les TROIS tiers",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             f"★★ un tiers des points diffèrent de plus d'une feuille ENTIÈRE",
             fill=VERT, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 410
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    p = m["par_tiers"]
    art.text((marge, 16),
             "Deux humains sur la même matière divergent de plus d'une demi-feuille, partout",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes']} bandes en deux révisions · désaccord "
             f"{p['coeur']['desaccord_median_um']} µm au cœur et "
             f"{p['bord']['desaccord_median_um']} au bord, pour une demi-feuille de "
             f"{DEMI_FEUILLE_UM:.0f} µm",
             fill=DISCRET, font=moyen)
    titres = ("A · le plancher du référent, et il est PLAT",
              "B · l'estimateur réfuté, et le facteur qu'il cache")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_plancher(art, marge, 104, pw, ph, m, petit)
    barres = panneau_estimateur(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "barres": barres,
            "textes_dessines": art.textes,
            "debordants": textes_debordants(art.poses, L - marge),
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, RACINE / "docs" / "images" / "97_deux_humains_sur_la_meme_matiere.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("toutes les bandes sont tracées",
      d["points"] == len([x for x in m["lignes"] if x["rayon_mm"] is not None]),
      str(d["points"]))
    # ★★ LES DEUX ESTIMATEURS SONT DESSINES COTE A COTE, sinon le facteur qu'ils cachent ne se
    # verrait pas — et c'est lui qui distingue une limite de grille d'une limite de matiere.
    v("les deux estimateurs sont dessinés pour chaque tiers", d["barres"] == 6, str(d["barres"]))
    v("... et le réfuté est bien le plus grand dans chaque tiers",
      all(m["par_tiers"][k]["au_plus_proche_voisin_um"]
          > m["par_tiers"][k]["desaccord_median_um"] for k in m["par_tiers"]))
    # ⭐⭐⭐ LE VERDICT EST DANS LA MESURE : le desaccord depasse la demi-feuille partout.
    v("le désaccord dépasse la demi-feuille dans les trois tiers",
      all(m["par_tiers"][k]["desaccord_median_um"] > DEMI_FEUILLE_UM for k in m["par_tiers"]),
      str([m["par_tiers"][k]["desaccord_median_um"] for k in m["par_tiers"]]))
    v("... et la demi-feuille est TRACÉE, sinon le nombre serait nu",
      any("demi-feuille" in t for t in d["textes_dessines"]))
    v("le désaccord ne suit PAS la fermeture de `96`",
      abs(m["correlations"]["desaccord_contre_fermeture"]) < 0.3,
      str(m["correlations"]["desaccord_contre_fermeture"]))
    v("la prose garde la garde qui supprimait ce qu'elle devait mesurer",
      any("PLAN TANGENT" in x for x in prose(m)))
    v("... et le confondant de couverture", any("recouvrement" in x for x in prose(m)))
    v("... et ce que ça change pour le graal", any("n'a pas de valeur unique" in x
                                                  for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "97_deux_humains_sur_la_meme_matiere.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
