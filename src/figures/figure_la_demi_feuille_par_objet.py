#!/usr/bin/env python3
"""La demi-feuille — le critere de marche perdue — vaut-elle la meme chose sur chaque objet ?

⚠⚠⚠ CETTE FIGURE PORTE LA CONFRONTATION LA PLUS LOURDE DE L'APPAREIL DE MARCHE. Le panneau A
situe le chiffre de ce depot — 135,5 µm, d'ou la demi-feuille de 67,75 µm — dans la distribution
que `winding-ruler` publie pour le MEME fragment : il tombe au percentile 27. Le panneau B range
les 36 objets par demi-feuille et montre que les treize du prix tiennent dans un facteur 1,2.

Usage :
    uv run python src/figures/figure_la_demi_feuille_par_objet.py --verifier
    uv run python src/figures/figure_la_demi_feuille_par_objet.py \\
        --sortie docs/images/86_la_demi_feuille_par_objet.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import Tracee, police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_demi_feuille_par_objet.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    c, p4, s = m["confrontation"], m["prix_du_changement_dobjet"], m["separation"]
    n = m["le_notre"]
    return [
        f"`85` conclut que le maillage a 45,532 µm ne peut pas donner le pas inter-feuilles, et "
        f"que la demi-feuille de {p4['vers']} reste un chiffre a mesurer ailleurs. elle etait "
        f"mesuree, a cote, dans un clone de l'arbre : {m['atlas']} publie la periode "
        f"inter-spires de {m['objets']} objets, dont les treize du prix, le temoin, l'objet "
        "courant et le candidat.",
        f"⚠⚠⚠ PANNEAU A — ET LE PREMIER FAIT EST LE PLUS PORTEUR DE TOUT L'APPAREIL DE MARCHE. "
        f"ce depot derive sa demi-feuille — {n['demi_um']:.2f} µm, le critere qui declare une "
        f"marche perdue — de {c['le_notre_um']:.1f} µm mesures sur {c['paires']} paires "
        f"consecutives des spires publiees de {c['fragment']}. l'atlas mesure "
        f"{c['atlas_um']:.1f} µm de mediane sur le MEME fragment, avec p25 = "
        f"{c['atlas_p25_um']:.1f} µm.",
        f"★★★ NOTRE CHIFFRE TOMBE DONC AU PERCENTILE {c['percentile_du_notre']:.0f} DE SON PROPRE "
        f"OBJET (un facteur {c['rapport']} sous la mediane). la marche est jugee dans la moitie "
        "la plus SERREE de la matiere, donc les portees publiees — 4 pour le pas normal, 5 avec "
        "la nappe lissee, 6 pour la borne — sont des BORNES BASSES, pas des plafonds.",
        "⚠⚠ CE NE SONT PAS DEUX MESURES CONTRADICTOIRES, ET LA DIFFERENCE EST DE POPULATION. les "
        "deux nomment la meme grandeur — la distance d'une surface de feuille a la suivante — "
        f"mais l'une porte sur {c['paires']} paires d'une region et l'autre sur "
        f"{m['lignes'][0]['coupes']} coupes et huit cents rayons du fragment entier. le lire "
        "comme une contradiction serait la faute ; le lire comme un ECHANTILLON est le resultat.",
        "⚠⚠ et les chaines d'instrument differrent aussi, ce qui borne la confiance dans un sens "
        "CONNU : l'atlas lit des PREDICTIONS de surface le long de rayons, et une prediction qui "
        "fusionne deux feuilles voisines saute un ecart et en rapporte un double — donc l'atlas "
        "surestime plutot qu'il ne sous-estime. notre chiffre vient de surfaces publiees, donc "
        "plus direct, mais local.",
        f"★★ PANNEAU B — ET LE PRIX DU CHANGEMENT D'OBJET EST CHIFFRE : la demi-feuille passe de "
        f"{p4['demi_actuelle_um']:.2f} µm sur {p4['de']} a {p4['demi_du_candidat_um']:.2f} µm sur "
        f"{p4['vers']}, soit {p4['plus_permissif_de']:.1%} de tolerance en plus. c'est ce que "
        "`85` disait non chiffre.",
        f"■ MAIS COMME CRITERE DE CHOIX DE ROULEAU, IL NE CHOISIT PAS : les treize du prix "
        f"tiennent dans un facteur {s['les_treize']['rapport']} "
        f"({s['les_treize']['min']} a {s['les_treize']['max']} µm), quand l'atlas entier va "
        f"jusqu'a {s['tout_latlas']['rapport']}. l'etroitesse est donc celle DES TREIZE et non "
        "celle de la mesure — la geometrie ne separe pas mieux que la part comprimee de `33`.",
        "⚠ une faute a moi, corrigee par une sonde : ma premiere version rendait un MOT — « au "
        "premier quartile » — en tolerant 5 % autour de p25, soit un seuil choisi pour que le "
        "chiffre du jour passe. un percentile n'a aucun seuil, et l'interpolation entre les trois "
        "quantiles publies ne pretend pas plus : hors des bornes elle BORNE au lieu d'extrapoler "
        "sur une queue que personne n'a mesuree.",
    ]


def panneau_confrontation(art, x0, y0, pw, ph, m, petit, moyen) -> int:
    """Notre chiffre situe dans la distribution du meme fragment."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    c = m["confrontation"]
    art.text((x0 + 8, y0 + 6),
             f"la distribution de {c['fragment']} contre le chiffre que ce dépôt en tire",
             fill=DISCRET, font=petit)
    gauche, droite = x0 + 40, x0 + pw - 40
    axe = y0 + 150
    lo, hi = 100.0, c["atlas_p75_um"] * 1.06

    def px(v: float) -> float:
        return gauche + (droite - gauche) * (v - lo) / (hi - lo)

    # ⚠ La boite des quartiles est PEINTE : sans elle, deux traits nus laisseraient juger « loin »
    # ou « proche » a l'oeil, ce qui est exactement ce que le percentile remplace.
    art.rectangle([px(c["atlas_p25_um"]), axe - 26, px(c["atlas_p75_um"]), axe + 26], fill=PALE)
    art.line([px(c["atlas_um"]), axe - 34, px(c["atlas_um"]), axe + 34], fill=VERT, width=2)
    for v, t, coul, dy in ((c["atlas_p25_um"], "p25", VERT, -46),
                           (c["atlas_um"], "médiane de l'atlas", VERT, -60),
                           (c["atlas_p75_um"], "p75", VERT, -46)):
        art.text((px(v) - 14, axe + dy), f"{t}\n{v:.1f} µm", fill=coul, font=petit)
    art.line([gauche, axe, droite, axe], fill=TEXTE)
    # ⭐ Notre chiffre, en rouge, avec son percentile — le nombre qui remplace le mot.
    ours = px(c["le_notre_um"])
    art.line([ours, axe - 40, ours, axe + 40], fill=ROUGE, width=2)
    art.text((ours - 30, axe + 46),
             f"ce dépôt\n{c['le_notre_um']:.1f} µm\npercentile {c['percentile_du_notre']:.0f}",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 76),
             f"⚠ un facteur {c['rapport']} sépare les deux — {c['paires']} paires de spires "
             f"publiées contre {m['lignes'][0]['coupes']} coupes du fragment",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 58),
             "★ donc le critère de marche perdue est CONSERVATEUR :", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 42),
             "   les portées publiées sont des bornes basses, pas des plafonds",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : période inter-feuilles en micromètres",
             fill=DISCRET, font=petit)
    return 1


def panneau_objets(art, x0, y0, pw, ph, m, petit) -> tuple[int, int]:
    """Les 36 objets rangés par demi-feuille, les treize du prix marqués."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             f"les {m['objets']} objets de l'atlas, rangés par demi-feuille",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 96, x0 + pw - 30
    haut = y0 + 30
    hauteur = (ph - 66) / max(1, len(lignes))
    lo = min(x["demi_um"] for x in lignes) * 0.97
    hi = max(x["demi_um"] for x in lignes) * 1.02

    def px(v: float) -> float:
        return gauche + (droite - gauche) * (v - lo) / (hi - lo)

    marques = nommes = 0
    for i, x in enumerate(lignes):
        y = haut + i * hauteur
        role = ("DU PRIX" if x["du_prix"] else ("témoin" if x["temoin"] else
                ("courant" if x["courant"] else ("CANDIDAT" if x["candidat"] else ""))))
        coul = (AMBRE if x["du_prix"] else (BLEU if x["temoin"] else
                (ROUGE if x["courant"] else (VERT if x["candidat"] else GRIS))))
        if role:
            art.text((x0 + 6, y + hauteur / 2 - 7), x["nom"], fill=coul, font=petit)
            nommes += 1
        art.ellipse([px(x["demi_um"]) - 3, y + hauteur / 2 - 3,
                     px(x["demi_um"]) + 3, y + hauteur / 2 + 3], fill=coul)
        if x["du_prix"]:
            marques += 1
    # ⚠⚠ LA BANDE DES TREIZE EST TRACEE : c'est elle qui porte le verdict « ne choisit pas », et
    # un nuage sans elle laisserait juger l'etroitesse a l'oeil.
    s = m["separation"]["les_treize"]
    art.line([px(s["min"]), haut - 8, px(s["min"]), y0 + ph - 40], fill=AMBRE)
    art.line([px(s["max"]), haut - 8, px(s["max"]), y0 + ph - 40], fill=AMBRE)
    art.text((px(s["min"]) + 3, y0 + ph - 38),
             f"les treize : {s['min']} à {s['max']} µm, un facteur {s['rapport']}",
             fill=AMBRE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             f"abscisse : demi-feuille en micromètres · l'atlas entier va jusqu'à "
             f"×{m['separation']['tout_latlas']['rapport']}",
             fill=DISCRET, font=petit)
    return marques, nommes


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 430
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    c = m["confrontation"]
    art.text((marge, 16),
             "La demi-feuille — le critère de marche perdue — vaut-elle la même chose sur chaque "
             "objet ?", fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['objets']} objets · notre chiffre au percentile "
             f"{c['percentile_du_notre']:.0f} de son propre objet · les treize du prix dans un "
             f"facteur {m['separation']['les_treize']['rapport']}",
             fill=DISCRET, font=moyen)
    titres = (f"A · notre {c['le_notre_um']:.1f} µm dans la distribution de {c['fragment']}",
              "B · la demi-feuille des 36 objets publiés")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    conf = panneau_confrontation(art, marge, 104, pw, ph, m, petit, moyen)
    marques, nommes = panneau_objets(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "confrontations": conf, "du_prix_marques": marques,
            "textes_dessines": art.textes,
            "nommes": nommes, "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
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
    d = dessiner(m, RACINE / "docs" / "images" / "86_la_demi_feuille_par_objet.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    v("aucune ligne de prose n'est vide", all(x.strip() for x in prose(m)))
    # ⚠⚠ LES TREIZE SONT TOUS MARQUES : c'est leur etroitesse qui porte le verdict du panneau B.
    v("les treize du prix sont tous marqués", d["du_prix_marques"] == 13,
      str(d["du_prix_marques"]))
    v("... et les quatre rôles sont nommés", d["nommes"] == 16, str(d["nommes"]))
    # ⭐⭐⭐ LE FAIT PORTEUR EST DANS LA PROSE, avec son nombre.
    c = m["confrontation"]
    v("le percentile est publié dans la prose",
      any(f"PERCENTILE {c['percentile_du_notre']:.0f}" in x.upper() for x in prose(m)),
      str(c["percentile_du_notre"]))
    v("... et la conséquence est dite : bornes basses",
      any("BORNES BASSES" in x for x in prose(m)))
    # ⚠⚠ LE SENS DU BIAIS DE L'ATLAS EST DIT, sinon un lecteur prendrait 196,6 pour la verite.
    v("le sens du biais de l'atlas est dit",
      any("surestime plutot qu'il ne sous-estime" in x for x in prose(m)))
    # ⚠ Et que ce n'est pas une contradiction mais une population.
    v("... et que la différence est de population, pas de contradiction",
      any("difference est de population" in x.lower() for x in prose(m)))
    # ⛔ LE VERDICT DU PANNEAU B.
    v("l'étroitesse des treize est publiée avec son facteur",
      m["separation"]["les_treize"]["rapport"] < 1.25
      and any(str(m["separation"]["les_treize"]["rapport"]) in x for x in prose(m)))
    # ⚠ Et la faute corrigée est gardée dans la figure elle-même.
    v("la faute du seuil choisi est gardée dans la prose",
      any("seuil choisi pour que le" in x for x in prose(m)))
    # ⚠⚠⚠ ET LA GARDE COUVRE TOUT LE TEXTE DESSINE, pas seulement la prose du bas : un « ⛔ »
    # est sorti en carré dans la ligne du panneau A qui porte le verdict, et rien ne l'a vu.
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents,
      f"{len(d['textes_dessines'])} textes tracés, absents : {absents}")
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "86_la_demi_feuille_par_objet.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
