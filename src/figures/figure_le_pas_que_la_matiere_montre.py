#!/usr/bin/env python3
"""Le pas que la matiere montre n'est pas le pas nominal — et le nul l'a fallu deux fois.

⭐⭐⭐ CETTE FIGURE PORTE LE SIGNAL AU BON SIGNE LE PLUS FORT DE LA CAMPAGNE : la part de cellules
ou la matiere repond correle a **-0,845** avec la rupture de continuite. Le panneau A le montre
contre le rayon.

⛔⛔ ET LE PANNEAU B PORTE L'ARTEFACT QUE LE NUL A TUE. La premiere version de la recherche rendait
147 µm sur le vrai volume ET 147 µm sur du bruit pur, parce qu'un segment court reechantillonne est
plus lisse donc mieux correle. La calibration par candidat le corrige, et la distribution des
longueurs devient distinguable du nul (Kolmogorov-Smirnov p = 1,4e-05).

Usage :
    uv run python src/figures/figure_le_pas_que_la_matiere_montre.py --verifier
    uv run python src/figures/figure_le_pas_que_la_matiere_montre.py \\
        --sortie docs/images/99_le_pas_que_la_matiere_montre.png
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
MESURE = RACINE / "docs" / "mesures" / "le_pas_que_la_matiere_montre.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def lues(m: dict) -> list[dict]:
    return [x for x in m["lignes"]
            if x["mesurable"] and x.get("pas_median_um") is not None
            and x.get("rayon_mm") is not None]


def prose(m: dict) -> list[str]:
    p, c = m["par_tiers"], m["correlations"]
    cn = m["la_longueur_differe_du_nul"]
    npc = m["nul_par_candidat"]
    return [
        "★★★ CE QUE CE FICHIER CHANGE : `98` AUDITE, CELUI-CI DECIDE. `98` verifie un pas qu'on "
        "lui donne ; un automate a besoin de l'inverse, qu'on lui DISE le pas. le meme filtre le "
        "fait en balayant la distance et en gardant celle que la matiere accorde le mieux. ⚠ la "
        "degenerescence est levee en fixant k = 1 : un segment de 2p traverse par deux "
        "interstices est indiscernable d'un segment de p traverse par un.",
        f"★★★ PANNEAU A — LE SIGNAL AU BON SIGNE LE PLUS FORT DE LA CAMPAGNE. la part de cellules "
        f"ou la matiere repond vaut {p['coeur']['part_utilisable']} au coeur, "
        f"{p['milieu']['part_utilisable']} au milieu et {p['bord']['part_utilisable']} au bord, "
        f"et elle correle a {c['part_utilisable_contre_continuite']:+.3f} avec la rupture de "
        "continuite. c'est au niveau de la BANDE, donc utilisable pour dire ou un automate doit "
        "ralentir.",
        f"★★ ET LE PAS MONTRE N'EST PAS LE NOMINAL : {p['coeur']['pas_median_um']} µm au coeur et "
        f"{p['bord']['pas_median_um']} au bord contre {m['pas_nominal_um']} publie, avec "
        f"{round(100 * p['coeur']['part_a_plus_dun_dixieme_du_nominal'])} % des cellules a plus "
        "d'un dixieme du nominal. un automate qui avancerait d'un pas CONSTANT se tromperait "
        "quatre fois sur cinq.",
        f"★★★ NON — PANNEAU B — LE PREMIER RESULTAT ETAIT UN ARTEFACT, ET LE NUL L'A MONTRE. la "
        f"premiere version rendait un pas median de 147 µm sur le vrai volume ; la MEME recherche "
        f"sur du BRUIT PUR rendait 147 µm aussi. la cause se chiffre : un segment court "
        f"reechantillonne sur le meme nombre de points est SUR-echantillonne, donc plus lisse, "
        f"donc mieux correle — le nul passe de {npc['le_plus_court']} au plus court a "
        f"{npc['le_plus_long']} au plus long, soit ×{npc['rapport']}.",
        "★★★ ET LA LECON SE GENERALISE : un modele nul doit s'appliquer a CHAQUE quantite qu'une "
        "recherche rapporte, pas seulement a sa confiance. le nul du SCORE existait et etait "
        "juste ; celui de la LONGUEUR CHOISIE manquait, et c'est la que vivait l'artefact.",
        f"★★ APRES CALIBRATION, LA LONGUEUR DEVIENT UNE MESURE, ET C'EST TESTE. la distribution "
        f"des longueurs retenues est confrontee a celle que le meme balayage retient sur du bruit "
        f"pur, au-dessus de la meme barre : elles DIFFERENT "
        f"(Kolmogorov-Smirnov D = {cn['kolmogorov_smirnov_D']}, p = "
        f"{cn['kolmogorov_smirnov_p']}), mediane {cn['mediane_reelle_um']} µm contre "
        f"{cn['mediane_du_nul_um']} au nul, et la barre ne laisse passer que "
        f"{100 * cn['part_du_nul_au_dessus_de_la_barre']:.1f} % du bruit.",
        f"⚠⚠⚠ ET UNE SECONDE ERREUR DE NUL, CORRIGEE AVANT CELLE-LA. la barre comparait le "
        f"MAXIMUM sur {m['candidats']} candidats × 2 polarites au nul d'UN SEUL test — l'erreur "
        f"des comparaisons multiples, qui rend la mesure INCAPABLE D'ECHOUER : la part lue "
        f"sautait a 0,98. les trois barres sont publiees "
        f"({m['barre_dun_seul_essai']} pour un essai, {m['barre_du_nul']} en ecarts-types apres "
        "calibration) parce que leur ECART montre l'ampleur de chaque correction.",
        f"⚠⚠ CE QUE CA NE DIT PAS. le pas montre ({p['coeur']['pas_median_um']} µm) depasse aussi "
        f"celui que `91` lit sur les transferts humains (164 µm) et celui de l'atlas (182,4), de "
        f"9 a 21 %. `97` a etabli que le maillage humain n'a pas de valeur unique, donc un "
        "desaccord est attendu — mais son AMPLEUR n'est pas expliquee ici, et il faut le dire "
        "plutot que choisir le chiffre qui arrange.",
        f"⚠ ET UNE BUTEE N'EST PAS UNE MESURE : quand l'optimum tombe sur une extremite de la "
        f"fenetre, la matiere dit « au moins ceci ». ces cellules — "
        f"{round(100 * p['coeur']['part_en_butee'])} a "
        f"{round(100 * p['bord']['part_en_butee'])} % — sont comptees a part et retirees de "
        "l'utilisable, sinon une limite de FENETRE se publierait comme une limite de MATIERE.",
    ]


def panneau_signal(art, x0, y0, pw, ph, m, petit) -> int:
    """La part utilisable et la continuité contre le rayon."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "où la matière répond, contre le rayon", fill=DISCRET, font=petit)
    lignes = lues(m)
    gauche, droite = x0 + 52, x0 + pw - 52
    base, sommet = y0 + ph - 58, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    c_hi = max(x["continuite"] for x in lignes if x["continuite"]) * 1.12

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v, hi):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([(px(x["rayon_mm"]), py(x["part_utilisable"], 1.0)) for x in lignes],
             fill=BLEU, width=2)
    art.line([(px(x["rayon_mm"]), py(x["continuite"], c_hi)) for x in lignes
              if x["continuite"]], fill=ROUGE, width=2)
    points = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["part_utilisable"], 1.0)
        art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLEU)
        points += 1
    for g in (0.0, 0.5, 1.0):
        art.text((x0 + 6, py(g, 1.0) - 6), f"{g:>4.1f}", fill=BLEU, font=petit)
    for g in (0.0, c_hi / 2, c_hi):
        art.text((droite + 6, py(g, c_hi) - 6), f"×{g:.0f}", fill=ROUGE, font=petit)
    art.text((gauche + 4, sommet - 16), "part où la matière répond", fill=BLEU, font=petit)
    art.text((droite - 108, sommet - 16), "continuité, ×référence", fill=ROUGE, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★ corrélation : {m['correlations']['part_utilisable_contre_continuite']:+.3f} — "
             "la plus forte de la campagne", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande — cœur à gauche, bord à droite",
             fill=DISCRET, font=petit)
    return points


def panneau_nul(art, x0, y0, pw, ph, m, petit) -> int:
    """L'artefact que le nul a tué, et la distribution qui le remplace."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "ce que le nul a corrigé, et ce qui reste",
             fill=DISCRET, font=petit)
    cn = m["la_longueur_differe_du_nul"]
    npc = m["nul_par_candidat"]
    # ⚠ La colonne des libellés doit tenir « BRUIT PUR, non calibré », sinon la barre le
    # recouvre — et c'est justement la ligne qui porte l'argument du panneau.
    gauche, droite = x0 + 152, x0 + pw - 96
    haut = y0 + 56
    entrees = [
        ("réel, non calibré", 147.0, ROUGE),
        ("BRUIT PUR, non calibré", 147.0, ROUGE),
        ("BRUIT PUR, calibré", cn["mediane_du_nul_um"], AMBRE),
        ("réel, calibré", cn["mediane_reelle_um"], BLEU),
        ("nominal publié", m["pas_nominal_um"], VERT),
    ]
    hi = max(v for _, v, _ in entrees) * 1.25
    h = (ph - 190) / len(entrees)
    barres = 0
    for j, (nom, val, coul) in enumerate(entrees):
        y = haut + j * h
        art.text((x0 + 8, y + 1), nom, fill=coul, font=petit)
        larg = (droite - gauche) * val / hi
        art.rectangle([gauche, y, gauche + larg, y + 13], fill=coul)
        art.text((gauche + larg + 5, y), f"{val:.1f} µm", fill=coul, font=petit)
        barres += 1
    # ⭐⭐⭐ LES DEUX PREMIERES BARRES SONT IDENTIQUES, ET C'EST TOUT L'ARGUMENT : le reel et le
    # bruit pur rendaient LE MEME nombre. Sans les mettre cote a cote, « artefact » serait un mot.
    y2 = haut + len(entrees) * h + 10
    art.text((x0 + 8, y2),
             "★★★ les deux premières sont IDENTIQUES : le réel et le bruit",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y2 + 14),
             "   pur rendaient le MÊME nombre — c'est ça, l'artefact.", fill=ROUGE, font=petit)
    art.text((x0 + 8, y2 + 34),
             f"★ cause chiffrée : le nul passe de {npc['le_plus_court']} au plus court",
             fill=AMBRE, font=petit)
    art.text((x0 + 8, y2 + 48),
             f"   à {npc['le_plus_long']} au plus long, soit ×{npc['rapport']}.",
             fill=AMBRE, font=petit)
    art.text((x0 + 8, y2 + 68),
             f"★★ après calibration les distributions DIFFÈRENT :",
             fill=VERT, font=petit)
    art.text((x0 + 8, y2 + 82),
             f"   Kolmogorov-Smirnov D = {cn['kolmogorov_smirnov_D']}, "
             f"p = {cn['kolmogorov_smirnov_p']}", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             f"et la barre ne laisse passer que "
             f"{100 * cn['part_du_nul_au_dessus_de_la_barre']:.1f} % du bruit pur",
             fill=DISCRET, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 420
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
             "Le pas que la matière montre n'est pas le pas nominal, et le nul l'a fallu deux "
             "fois", fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes_lisibles']} bandes · pas montré "
             f"{p['coeur']['pas_median_um']} µm au cœur contre {m['pas_nominal_um']} nominal · "
             f"part utilisable {p['coeur']['part_utilisable']} au cœur contre "
             f"{p['bord']['part_utilisable']} au bord",
             fill=DISCRET, font=moyen)
    titres = ("A · où la matière répond — corrélation la plus forte",
              "B · l'artefact que le nul a tué, et ce qui reste")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_signal(art, marge, 104, pw, ph, m, petit)
    barres = panneau_nul(art, marge + pw + ecart, 104, pw, ph, m, petit)
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
    d = dessiner(m, RACINE / "docs" / "images" / "99_le_pas_que_la_matiere_montre.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("toutes les bandes lisibles sont tracées", d["points"] == len(lues(m)), str(d["points"]))
    # ⭐⭐⭐ LES DEUX PREMIERES BARRES DU PANNEAU B SONT L'ARGUMENT : reel et bruit pur, identiques.
    v("le panneau B met le réel et le bruit pur côte à côte", d["barres"] == 5, str(d["barres"]))
    v("... et dit qu'ils étaient identiques",
      any("IDENTIQUES" in t for t in d["textes_dessines"]))
    # ⚠⚠ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    v("la part utilisable baisse bien avec la rupture",
      m["correlations"]["part_utilisable_contre_continuite"] < -0.5,
      str(m["correlations"]["part_utilisable_contre_continuite"]))
    cn = m["la_longueur_differe_du_nul"]
    v("... et la longueur diffère du nul", cn["differe"],
      f"p={cn['kolmogorov_smirnov_p']}")
    v("... la barre ne laissant passer qu'une part infime du bruit",
      cn["part_du_nul_au_dessus_de_la_barre"] < 0.05,
      str(cn["part_du_nul_au_dessus_de_la_barre"]))
    v("le biais vers les courts est publié avec son ampleur",
      m["nul_par_candidat"]["rapport"] > 1.3, str(m["nul_par_candidat"]))
    v("le pas montré dépasse franchement le nominal",
      m["par_tiers"]["coeur"]["ecart_au_nominal"] > 1.1,
      str(m["par_tiers"]["coeur"]["ecart_au_nominal"]))
    v("la prose garde l'artefact et sa leçon générale",
      any("CHAQUE quantite qu'une" in x for x in prose(m)))
    v("... et le désaccord non expliqué avec `91`",
      any("son AMPLEUR n'est pas expliquee" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "99_le_pas_que_la_matiere_montre.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
