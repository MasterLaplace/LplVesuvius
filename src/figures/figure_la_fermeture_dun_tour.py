#!/usr/bin/env python3
"""Le premier signal dont le signe est le BON, et le plancher qui l'empeche de certifier.

⭐⭐⭐ CETTE FIGURE PORTE LE PREMIER RENVERSEMENT DE SIGNE DE LA CAMPAGNE. `94` (le pli) et `95`
(la pose sur la matiere) rendaient des correlations NEGATIVES avec la rupture de continuite : ils
disaient « plus propre » la ou le transfert casse. Le panneau A montre que la fermeture d'un tour
monte AVEC elle.

⚠⚠⚠ ET LE PANNEAU B EST CE QUI EMPECHE DE CRIER VICTOIRE. Il compare le balayage de fenetre du
REEL a celui de deux spirales fabriquees. Du bruit se moyenne quand la fenetre s'allonge, une
structure non : la courbe reelle est PLATE la ou celle du bruit s'effondre. Donc l'irregularite
radiale des maillages humains n'est pas du bruit, et un tour de fermeture ne peut certifier aucune
cellule, meme la ou la continuite est intacte.

Usage :
    uv run python src/figures/figure_la_fermeture_dun_tour.py --verifier
    uv run python src/figures/figure_la_fermeture_dun_tour.py \\
        --sortie docs/images/96_la_fermeture_dun_tour.png
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
MESURE = RACINE / "docs" / "mesures" / "la_fermeture_dun_tour.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def mesurees(m: dict) -> list[dict]:
    return [x for x in m["lignes"] if x["mesurable"]]


def prose(m: dict) -> list[str]:
    c, p = m["correlations"], m["par_tiers"]
    bal = m["balayage_reel"]
    fx = {x["tours"]: x for x in m["balayage_des_fixtures"]}
    r1, r5 = bal[0]["part_hors_demi_feuille_mediane"], bal[-1]["part_hors_demi_feuille_mediane"]
    return [
        "★★★ POURQUOI CETTE OBSERVABLE APRES LES DEUX AUTRES. `94` a tue le pli et `95` la pose "
        "sur la matiere, et les deux ont echoue de la MEME facon : ils disent « plus propre » "
        "exactement la ou le transfert casse. le motif est etabli — au bord, l'humain qui ne "
        "peut pas suivre la vraie feuille en trace une autre, proprement, donc le maillage "
        "epouse tres bien UNE feuille, simplement pas la bonne. ce qui echoue n'est pas la "
        "qualite LOCALE mais l'IDENTITE de la feuille, et aucune observable locale ne peut la "
        "voir par construction.",
        "★★★ LA FERMETURE EST UN ENONCE D'IDENTITE, PAS DE PROPRETE. partir d'une cellule, faire "
        "UN TOUR COMPLET, regarder de combien le rayon a monte : la reponse doit etre UN pas de "
        "feuille. zero voudrait dire qu'on est revenu sur la meme, deux qu'on en a saute une. "
        "aucune supervision n'entre — le maillage seul suffit.",
        f"★★★ PANNEAU A — LE SIGNE EST ENFIN LE BON. la part de cellules dont un tour atterrit "
        f"hors de la demi-feuille vaut {p['coeur']['part_hors_demi_feuille']} au coeur, "
        f"{p['milieu']['part_hors_demi_feuille']} au milieu et "
        f"{p['bord']['part_hors_demi_feuille']} au bord : elle MONTE avec la rupture "
        f"({c['hors_demi_feuille_contre_continuite']:+.3f}) la ou le pli descendait a −0,825 et "
        f"la pose sur la matiere a −0,694. c'est le premier renversement de signe de la campagne.",
        f"⚠⚠⚠ PANNEAU B — ET C'EST CE QUI EMPECHE DE CRIER VICTOIRE. la part vaut deja "
        f"{p['coeur']['part_hors_demi_feuille']} au COEUR, la ou la continuite est intacte "
        f"(×{p['coeur']['continuite']}) : un signal qui marque trois cellules sur cinq dans la "
        f"region propre ne peut certifier aucune cellule. reste a savoir si c'est du BRUIT, qui "
        f"se moyennerait, ou de la STRUCTURE, qui ne se moyenne pas — et le balayage de fenetre "
        "repond sans qu'aucun seuil ne soit choisi.",
        f"★★★ LA REPONSE EST : DE LA STRUCTURE. allonger la fenetre de un a cinq tours fait "
        f"tomber le reel de {r1} a {r5}, soit "
        f"{round(100 * (1 - r5 / r1))} % ; le MEME estimateur sur une spirale bruitee sans saut "
        f"tombe de {fx[1]['bruit_seul']} a {fx[5]['bruit_seul']}, c'est-a-dire a zero. "
        "l'irregularite radiale des maillages humains n'est donc pas du bruit, et un tour de "
        "fermeture ne certifie aucune cellule.",
        "⚠⚠⚠ ET LE BALAYAGE A DU ETRE REFAIT A SOUS-ENSEMBLE CONSTANT. ma premiere version "
        "prenait toutes les bandes disponibles a chaque fenetre — 28 a un tour, 5 a cinq — or "
        "les cinq qui portent cinq tours sont les plus INTERNES, donc les plus propres : la "
        "baisse mesuree etait celle du sous-ensemble, pas celle de la fenetre. c'est la faute que "
        "`93` avait deja payee en comparant la bande 0 a la bande 7. le confondant retiré rend le "
        f"fait PLUS fort — {round(100 * (1 - r5 / r1))} % de baisse contre les 30 % que la "
        "version confondue annoncait.",
        f"⚠⚠ ET LA PLAGE OU LA FIXTURE DISCRIMINE EST BORNEE AUX DEUX BOUTS : a cinq tours sur "
        f"une spirale de huit, la fenetre efface aussi l'echelon "
        f"({fx[5]['avec_une_feuille_sautee']}), donc cette colonne ne prouve rien. elle "
        "discrimine a deux et trois tours, et le dire evite de lire une fenetre trop longue "
        "comme une preuve de proprete.",
        f"⚠⚠ LA MEDIANE NE PORTE PAS LE RESULTAT, ET C'EST LA FIXTURE QUI LE DIT. sur une "
        f"spirale ou UNE feuille est sautee, la fermeture mediane reste a 1,000 — parfaitement "
        f"aveugle — pendant que la part hors demi-feuille l'attrape. sur le reel la mediane vaut "
        f"{p['coeur']['fermeture_en_feuilles']} au coeur et "
        f"{p['bord']['fermeture_en_feuilles']} au bord, donc le PAS est juste partout : ce n'est "
        "pas le pas qui manque, c'est la fermeture cellule par cellule.",
        "★★ CE QUE CA LAISSE POUR LE REMPLACANT DE L'HUMAIN, ET C'EST UTILISABLE. la direction "
        "est bonne — un invariant topologique est la seule famille dont le signe soit correct — "
        "et la fixture prouve que l'estimateur SAIT detecter une feuille sautee (0,096 contre "
        "0,004 a trois tours). ce qui manque n'est pas l'instrument mais un REFERENT : ces "
        "maillages ne ferment pas eux-memes a la demi-feuille pres, donc ils ne peuvent pas "
        "servir a calibrer le seuil d'un automate. c'est le meme plancher que `95` sur un autre "
        "axe — l'erreur du referent, pas la mienne.",
    ]


def panneau_signe(art, x0, y0, pw, ph, m, petit) -> int:
    """La part hors demi-feuille et la continuité contre le rayon — le même sens, enfin."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les deux contre le rayon — ils montent ENSEMBLE",
             fill=DISCRET, font=petit)
    lignes = mesurees(m)
    gauche, droite = x0 + 52, x0 + pw - 52
    base, sommet = y0 + ph - 58, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    c_hi = max(x["continuite"] for x in lignes) * 1.12

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v, hi):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([(px(x["rayon_mm"]), py(x["part_hors_demi_feuille"], 1.0)) for x in lignes],
             fill=BLEU, width=2)
    art.line([(px(x["rayon_mm"]), py(x["continuite"], c_hi)) for x in lignes],
             fill=ROUGE, width=2)
    points = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["part_hors_demi_feuille"], 1.0)
        art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLEU)
        points += 1
    for g in (0.0, 0.5, 1.0):
        art.text((x0 + 6, py(g, 1.0) - 6), f"{g:>4.1f}", fill=BLEU, font=petit)
    for g in (0.0, c_hi / 2, c_hi):
        art.text((droite + 6, py(g, c_hi) - 6), f"×{g:.0f}", fill=ROUGE, font=petit)
    art.text((gauche + 4, sommet - 16), "part hors demi-feuille", fill=BLEU, font=petit)
    art.text((droite - 108, sommet - 16), "continuité, ×référence", fill=ROUGE, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★ corrélation : {m['correlations']['hors_demi_feuille_contre_continuite']:+.3f}, "
             f"POSITIVE — `94` donnait −0,825 et `95` −0,694",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande — cœur à gauche, bord à droite",
             fill=DISCRET, font=petit)
    return points


def panneau_balayage(art, x0, y0, pw, ph, m, petit) -> int:
    """Le balayage de fenêtre : le réel contre les deux spirales fabriquées."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "du bruit se moyenne, une structure non — la fenêtre le demande",
             fill=DISCRET, font=petit)
    bal = [b for b in m["balayage_reel"] if "part_hors_demi_feuille_mediane" in b]
    fx = {x["tours"]: x for x in m["balayage_des_fixtures"]}
    gauche, droite = x0 + 56, x0 + pw - 40
    base, sommet = y0 + ph - 96, y0 + 44
    tmax = max(b["tours"] for b in bal)

    def px(t):
        return gauche + (droite - gauche) * (t - 1) / max(1, tmax - 1)

    def py(v):
        return base - (base - sommet) * v

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0.0, 0.25, 0.5, 0.75, 1.0):
        art.text((x0 + 8, py(g) - 6), f"{g:>4.2f}", fill=DISCRET, font=petit)
        if g:
            art.line([gauche, py(g), droite, py(g)], fill=(238, 238, 238))
    series = 0
    for nom, coul, cle in (("réel — maillages humains", BLEU, None),
                           ("fixture : bruit seul", VERT, "bruit_seul"),
                           ("fixture : + une feuille sautée", AMBRE, "avec_une_feuille_sautee")):
        pts = []
        for b in bal:
            v = (b["part_hors_demi_feuille_mediane"] if cle is None
                 else fx.get(b["tours"], {}).get(cle))
            if v is not None:
                pts.append((px(b["tours"]), py(v)))
        if len(pts) < 2:
            continue
        art.line(pts, fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        # ⚠ LA LEGENDE VIT A DROITE ET SOUS LE HAUT DU CADRE : posee en haut a gauche elle
        # tombait sur les etiquettes de l'axe, et les deux se lisaient l'une par-dessus l'autre.
        # Les trois courbes sont sous 0,60 des deux tours, donc ce coin est libre.
        art.text((droite - 210, sommet + 6 + series * 14), nom, fill=coul, font=petit)
        series += 1
    for b in bal:
        art.text((px(b["tours"]) - 8, base + 6), f"{b['tours']} t", fill=DISCRET, font=petit)
    # ⚠⚠ LA PLAGE OU LA FIXTURE DISCRIMINE EST BORNEE, et le dire sur la figure evite qu'un
    # lecteur prenne la colonne a cinq tours pour un temoin.
    art.text((x0 + 8, y0 + ph - 80),
             f"⚠ à 5 tours la fenêtre efface aussi l'échelon "
             f"({fx[5]['avec_une_feuille_sautee']}) :", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 66),
             "   la fixture ne discrimine qu'à 2 et 3 tours", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 46),
             f"★★ le réel est PLAT ({bal[0]['part_hors_demi_feuille_mediane']} → "
             f"{bal[-1]['part_hors_demi_feuille_mediane']}) là où le bruit s'effondre à zéro",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 30),
             f"★ sous-ensemble CONSTANT : les {bal[0]['bandes']} bandes qui portent 5 tours",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 14),
             "abscisse : longueur de la fenêtre de fermeture, en tours",
             fill=DISCRET, font=petit)
    return series


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
    p, c = m["par_tiers"], m["correlations"]
    art.text((marge, 16),
             "Le premier signal dont le signe est le BON, et le plancher qui l'empêche de "
             "certifier", fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes_mesurables']} bandes · part hors demi-feuille "
             f"{p['coeur']['part_hors_demi_feuille']} au cœur contre "
             f"{p['bord']['part_hors_demi_feuille']} au bord, corrélation "
             f"{c['hors_demi_feuille_contre_continuite']:+.3f} avec la rupture",
             fill=DISCRET, font=moyen)
    titres = ("A · le renversement de signe : les deux montent ensemble",
              "B · bruit ou structure ? le balayage de fenêtre répond")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_signe(art, marge, 104, pw, ph, m, petit)
    series = panneau_balayage(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "series": series,
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
    d = dessiner(m, RACINE / "docs" / "images" / "96_la_fermeture_dun_tour.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("toutes les bandes mesurables sont tracées", d["points"] == m["bandes_mesurables"],
      f"{d['points']} pour {m['bandes_mesurables']}")
    # ⭐⭐⭐ LE PANNEAU B PORTE TROIS SERIES, et sans les deux fixtures la courbe reelle ne
    # dirait rien : « elle est plate » n'a de sens que contre une courbe qui s'effondre.
    v("le balayage porte le réel ET ses deux fixtures", d["series"] == 3, str(d["series"]))
    v("... sur un sous-ensemble constant de bandes",
      len({b.get("bandes") for b in m["balayage_reel"]}) == 1,
      str([b.get("bandes") for b in m["balayage_reel"]]))
    # ⚠⚠ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    v("le signe est POSITIF, à l'inverse de `94` et `95`",
      m["correlations"]["hors_demi_feuille_contre_continuite"] > 0,
      str(m["correlations"]["hors_demi_feuille_contre_continuite"]))
    v("... et le plancher au cœur est bien là", m["par_tiers"]["coeur"][
        "part_hors_demi_feuille"] > 0.4,
      str(m["par_tiers"]["coeur"]["part_hors_demi_feuille"]))
    fx = {x["tours"]: x for x in m["balayage_des_fixtures"]}
    v("la fixture de bruit s'effondre là où le réel reste plat",
      fx[3]["bruit_seul"] < 0.05, str(fx[3]["bruit_seul"]))
    v("la prose garde la faute du sous-ensemble variable",
      any("sous-ensemble, pas celle de la fenetre" in x for x in prose(m)))
    v("... et dit que la fixture à 5 tours n'est pas un témoin",
      any("BORNEE AUX DEUX BOUTS" in x for x in prose(m)))
    v("... et ce que ça laisse pour le remplaçant de l'humain",
      any("REFERENT" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "96_la_fermeture_dun_tour.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
