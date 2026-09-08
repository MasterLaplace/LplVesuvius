#!/usr/bin/env python3
"""Le froissement designe-t-il ou le transfert echoue ? Non — il designe l'inverse.

⚠⚠⚠ CETTE FIGURE PORTE UN CANDIDAT REFUTE, ET C'EST SON INTERET. `93` dit OU le pas geometrique
echoue ; il manque un signal qui le dise a un marcheur SANS SUPERVISION. Le pli etait le candidat
evident, et le depot l'avait deja mesure predictif PAR CELLULE (`75` : 8 bras sur 8 chez le
raccrochage, un bras sauve). Le panneau A montre qu'a travers les RAYONS il est ANTI-predictif :
il s'effondre exactement la ou le transfert casse.

★★★ ET LE PANNEAU B EST CE QUI TRANSFORME UNE CORRELATION EN CAUSE. Sans lui, « le froissement
tombe vers l'exterieur » est un fait sans mecanisme, et la premiere explication credible gagne —
c'est exactement comme ca que j'ai publie la sagitta avant de la retracter. Un cylindre parfait
rend zero, un cylindre a axe courbe aussi : le champ est aveugle a la courbure lisse et repond au
BRUIT, presque sans dependre du rayon.

Usage :
    uv run python src/figures/figure_le_froissement_mesure_la_rugosite.py --verifier
    uv run python src/figures/figure_le_froissement_mesure_la_rugosite.py \\
        --sortie docs/images/94_le_froissement_mesure_la_rugosite.png
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
MESURE = RACINE / "docs" / "mesures" / "le_froissement_mesure_la_rugosite.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    c, p, f = m["correlations"], m["par_tiers"], m["ce_que_le_champ_voit"]
    cas, k = f["cas"], m["laccord_avec_la_sagitta_est_une_coincidence"]
    chute = round(m["lignes"][0]["froissement_brut_um"]
                  / m["lignes"][-1]["froissement_brut_um"], 1)
    return [
        "il manque au marcheur un signal qui lui dise, SANS SUPERVISION, qu'il est dans la zone "
        "ou le pas geometrique ne suffit plus. le pli etait le candidat evident, et le depot "
        "l'avait deja mesure predictif PAR CELLULE : `75` lui fait gagner 8 bras sur 8 chez le "
        "raccrochage et SAUVER un bras en jetant les dix pour cent les plus plies, la ou le "
        "temoin au hasard n'en sauve aucun. ce fichier le teste la ou la carte d'echec existe : "
        "les 28 bandes humaines de PHercParis4, du coeur au bord.",
        f"★★★ NON — PANNEAU A — LA REPONSE EST NON, ET C'EST PIRE QUE NEUTRE. le froissement vaut "
        f"{p['coeur']['froissement_brut_um']} µm au coeur, {p['milieu']['froissement_brut_um']} au "
        f"milieu et {p['bord']['froissement_brut_um']} au bord, quand la continuite y passe de "
        f"×{p['coeur']['continuite']} a ×{p['bord']['continuite']}. correlations : "
        f"{c['brut_contre_rayon']} avec le rayon, {c['brut_contre_continuite']} avec la rupture. "
        "un marcheur qui s'en servirait signalerait le COEUR, ou tout est propre, et se TAIRAIT "
        "au bord.",
        f"★★★ PANNEAU B — CE QUE LE CHAMP MESURE, ETABLI PAR FIXTURE ET NON PAR CORRELATION. "
        f"le champ prend la MEDIANE d'un voisinage 3×3, et une mediane rend la valeur centrale "
        f"sur un voisinage symetrique : il est donc EXACTEMENT aveugle a la courbure lisse. un "
        f"cylindre parfait rend {cas['cylindre_parfait']['R5']:.2f} µm, un cylindre a AXE COURBE "
        f"— comme `90` en mesure un sur le vrai rouleau — {cas['axe_courbe']['R5']:.2f} aussi. "
        f"seul du bruit le reveille, et presque sans dependre du rayon "
        f"(×{cas['bruit_5um']['rapport_R5_sur_R20']} entre R=5 et R=20 mm).",
        f"★★ DONC LE VERDICT DEVIENT PLUS FORT, PAS PLUS FAIBLE. le reel tombe d'un facteur "
        f"×{chute} entre {m['lignes'][0]['rayon_mm']} et {m['lignes'][-1]['rayon_mm']} mm la ou "
        f"la rugosite seule n'en donnerait que ×{cas['bruit_5um']['rapport_R5_sur_R20']} : les "
        "maillages humains sont cinq fois plus LISSES au bord. or un maillage lisse qui porte des "
        "sauts de trente millimetres (`92`) et des spires desalignees (`93`) est un maillage qui "
        "a ENJAMBE ce qu'il ne pouvait pas suivre. la douceur au bord n'est pas de la qualite, "
        "c'est la signature d'un pontage — et un signal de confiance bati dessus classerait "
        "l'abandon comme une reussite.",
        f"⚠⚠⚠ ET UNE CAUSE QUE J'AI PUBLIEE PUIS RETRACTEE AVANT DE LA COMMITTER. j'avais "
        f"explique la chute en 1/R par la SAGITTA d'un cercle, s²/(8R), et l'accord numerique "
        f"etait frappant : {k['rapport_median']} en mediane sur vingt-huit bandes "
        f"({k['min']} a {k['max']}). la fixture la refute d'un coup — la sagitta predit "
        f"{f['sagitta_predite_a_R5_um']} µm a R = 5 mm la ou le champ rend zero. une correlation "
        "sur vingt-huit points ne vaut pas une fixture dont on connait la reponse. elle est "
        "gardee ici, refutee, parce qu'un accord de cet ordre reapparaitra a qui refera la "
        "mesure.",
        f"⚠⚠ AVERTISSEMENT DE NIVEAU, QUI NE RETRACTE PAS `75`. ce fichier compare des BANDES "
        f"entre elles ; `75` compare des CELLULES a l'interieur d'une meme marche, a rayon "
        f"presque constant. les deux peuvent etre vrais. normaliser par la sagitta retire le "
        f"rayon ({c['brut_contre_rayon']} → {c['normalise_contre_rayon']}) mais PAS le signe "
        f"({c['normalise_contre_continuite']}).",
        "★ CE QUE CA CONTRAINT POUR LE REMPLACANT DE L'HUMAIN : une marche de 31 spires change le "
        "rayon d'un facteur six, donc tout signal de confiance qu'elle emploie doit etre VERIFIE "
        "A TRAVERS LES RAYONS, ou il classera par rayon en croyant classer par difficulte.",
    ]


def panneau_anti(art, x0, y0, pw, ph, m, petit) -> int:
    """Le froissement et la continuité contre le rayon, sur le même axe."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les deux contre le rayon — ils vont en sens INVERSE",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 52, x0 + pw - 52
    base, sommet = y0 + ph - 58, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    fr_hi = max(x["froissement_brut_um"] for x in lignes) * 1.10
    co_hi = max(x["continuite"] for x in lignes) * 1.10

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v, hi):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    # ★★ LES DEUX COURBES PARTAGENT L'ABSCISSE ET PAS L'ORDONNEE : c'est le seul moyen de voir
    # qu'elles vont en sens inverse. Chaque echelle est donc annoncee dans sa propre couleur.
    art.line([(px(x["rayon_mm"]), py(x["froissement_brut_um"], fr_hi)) for x in lignes],
             fill=BLEU, width=2)
    art.line([(px(x["rayon_mm"]), py(x["continuite"], co_hi)) for x in lignes],
             fill=ROUGE, width=2)
    points = 0
    for x in lignes:
        cx = px(x["rayon_mm"])
        art.ellipse([cx - 2, py(x["froissement_brut_um"], fr_hi) - 2,
                     cx + 2, py(x["froissement_brut_um"], fr_hi) + 2], fill=BLEU)
        points += 1
    for g in (0.0, fr_hi / 2, fr_hi):
        art.text((x0 + 6, py(g, fr_hi) - 6), f"{g:>4.0f}", fill=BLEU, font=petit)
    for g in (0.0, co_hi / 2, co_hi):
        art.text((droite + 6, py(g, co_hi) - 6), f"×{g:.0f}", fill=ROUGE, font=petit)
    art.text((gauche + 4, sommet - 16), "froissement, µm", fill=BLEU, font=petit)
    art.text((droite - 96, sommet - 16), "continuité, ×référence", fill=ROUGE, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★ corrélation froissement/continuité : "
             f"{m['correlations']['brut_contre_continuite']}",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande — cœur à gauche, bord à droite",
             fill=DISCRET, font=petit)
    return points


def panneau_fixture(art, x0, y0, pw, ph, m, petit) -> int:
    """Ce que le champ rend sur des cylindres dont on connaît la réponse."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "cylindres fabriqués — la réponse est connue d'avance",
             fill=DISCRET, font=petit)
    f = m["ce_que_le_champ_voit"]
    cas = f["cas"]
    ordre = (("cylindre parfait", "cylindre_parfait"), ("+ axe courbe (`90`)", "axe_courbe"),
             ("+ bruit 5 µm", "bruit_5um"), ("+ bruit 20 µm", "bruit_20um"))
    gauche, droite = x0 + 132, x0 + pw - 78
    haut = y0 + 44
    h = (ph - 150) / len(ordre)
    hi = max(max(cas[c]["R5"], cas[c]["R20"]) for _, c in ordre) * 1.18
    # ⚠⚠ LA SAGITTA EST TRACEE COMME UN REPERE, PAS COMME UNE COURBE : c'est ce qu'une cause
    # refutee PREDISAIT, et sans elle « refutee » serait une affirmation plutot qu'un ecart visible.
    xs = gauche + (droite - gauche) * f["sagitta_predite_a_R5_um"] / hi
    art.line([xs, haut - 10, xs, haut + len(ordre) * h - 4], fill=AMBRE)
    art.text((xs - 52, haut - 24), f"sagitta prédite à R=5 : {f['sagitta_predite_a_R5_um']} µm",
             fill=AMBRE, font=petit)
    barres = 0
    for j, (nom, cle) in enumerate(ordre):
        yb = haut + j * h
        art.text((x0 + 8, yb + 6), nom, fill=TEXTE, font=petit)
        for i, (r, coul) in enumerate((("R5", BLEU), ("R20", GRIS))):
            v = cas[cle][r]
            y = yb + 4 + i * 13
            larg = (droite - gauche) * v / hi
            if larg < 1:
                # ★★★ ZERO SE DESSINE COMME UN ZERO ECRIT, pas comme une barre invisible : une
                # barre de largeur nulle est indistinguable d'une serie qu'on aurait oublie de
                # tracer, et c'est justement CE zero qui refute la sagitta.
                art.text((gauche + 2, y - 3), f"0,00 — {r} : le champ ne voit RIEN",
                         fill=VERT, font=petit)
            else:
                art.rectangle([gauche, y, gauche + larg, y + 10], fill=coul)
                art.text((gauche + larg + 4, y - 2), f"{v:.2f} µm ({r})", fill=coul, font=petit)
            barres += 1
    y = haut + len(ordre) * h + 12
    art.text((x0 + 8, y), f"★ le bruit répond ×{cas['bruit_5um']['rapport_R5_sur_R20']} entre "
             "R=5 et R=20 mm :", fill=VERT, font=petit)
    art.text((x0 + 8, y + 14), "   le champ ne dépend presque PAS du rayon",
             fill=VERT, font=petit)
    chute = round(m["lignes"][0]["froissement_brut_um"]
                  / m["lignes"][-1]["froissement_brut_um"], 1)
    art.text((x0 + 8, y + 32), f"★★ or le réel tombe de ×{chute} du cœur au bord —",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 46), "   donc la matière maillée est plus LISSE, pas mieux sondée",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "bleu : R = 5 mm · gris : R = 20 mm · ambre : ce que la cause réfutée prédisait",
             fill=DISCRET, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 392
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
             "Le froissement désigne-t-il où le transfert échoue ? Non — il désigne l'inverse",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes']} bandes · {p['coeur']['froissement_brut_um']} µm au "
             f"cœur contre {p['bord']['froissement_brut_um']} au bord, où la continuité passe de "
             f"×{p['coeur']['continuite']} à ×{p['bord']['continuite']}",
             fill=DISCRET, font=moyen)
    titres = ("A · l'anti-prédiction : les deux vont en sens inverse",
              "B · ce que le champ VOIT, sur des cylindres connus")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_anti(art, marge, 104, pw, ph, m, petit)
    barres = panneau_fixture(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "barres": barres,
            "textes_dessines": art.textes,
            # ⚠⚠⚠ LE BORD DROIT DE LA TOILE MOINS LA MARGE EST AUSSI CELUI DU PANNEAU DE
            # DROITE : c'est donc la meme borne pour la prose et pour le texte des panneaux.
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
    d = dessiner(m, RACINE / "docs" / "images" / "94_le_froissement_mesure_la_rugosite.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    # ⚠⚠⚠ ET AUCUN TEXTE DESSINE NE SORT DE LA TOILE. Ma première version de ce panneau
    # écrivait une ligne de verdict qui sortait du cadre et se faisait COUPER à mi-mot — un
    # garde de largeur qui ne lisait que la prose du bas ne pouvait pas la voir, exactement
    # comme le garde de glyphes ne lisait que la prose avant `93`.
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"],
      str(d["debordants"]))
    v("les 28 bandes sont tracées", d["points"] == m["bandes"], str(d["points"]))
    # ★★★ LE PANNEAU B EST CE QUI TRANSFORME LA CORRELATION EN CAUSE : quatre cas, deux rayons.
    v("la fixture porte ses quatre cas aux deux rayons", d["barres"] == 8, str(d["barres"]))
    f = m["ce_que_le_champ_voit"]
    v("... et un cylindre parfait y rend EXACTEMENT zéro",
      f["cas"]["cylindre_parfait"]["R5"] == 0.0 and f["cas"]["cylindre_parfait"]["R20"] == 0.0,
      str(f["cas"]["cylindre_parfait"]))
    v("... et un axe courbe aussi, donc `90` n'explique pas la chute",
      f["cas"]["axe_courbe"]["R5"] == 0.0, str(f["cas"]["axe_courbe"]))
    # ⚠⚠ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    v("le froissement est bien anti-prédictif dans la mesure",
      m["correlations"]["brut_contre_continuite"] < 0
      and m["par_tiers"]["bord"]["froissement_brut_um"]
      < m["par_tiers"]["coeur"]["froissement_brut_um"],
      str(m["correlations"]["brut_contre_continuite"]))
    v("... et normaliser ne corrige PAS le signe", not m["normaliser_corrige_le_signe"])
    # ⚠⚠⚠ LA CAUSE REFUTEE EST DANS LA FIGURE, avec sa réfutation.
    v("la prose garde la sagitta comme une cause RÉFUTÉE",
      any("SAGITTA" in x and "refute" in x for x in prose(m)))
    v("... et le repère de la sagitta est dessiné", any("sagitta prédite" in t
                                                       for t in d["textes_dessines"]))
    v("l'avertissement de niveau ne rétracte pas `75`",
      any("NE RETRACTE PAS `75`" in x for x in prose(m)))
    v("la prose dit ce que ça contraint pour le remplaçant de l'humain",
      any("A TRAVERS LES RAYONS" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "94_le_froissement_mesure_la_rugosite.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
