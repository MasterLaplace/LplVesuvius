#!/usr/bin/env python3
"""Existe-t-il une boite ou la portee cesse d'etre censuree par le corpus ?

⚠⚠⚠ LA REPONSE EST PRESQUE NON, ET C'EST CE QUE CETTE FIGURE MONTRE. `le_mur_du_corpus` a
etabli que toutes les portees publiees sont censurees par un plafond de six. La question
suivante est gratuite : en deplacant la boite sur le meme fragment, ce plafond se desserre-t-il ?
Sur plus de mille placements, le meilleur monte a huit — et le prix en demande trente et un.

⚠⚠ LE PANNEAU A porte la DISTRIBUTION et pas le maximum : un maximum sans sa distribution ne dit
pas si le fragment est bon quelque part ou mauvais partout. LE PANNEAU B montre ou chaque boite
meurt, et la reponse n'est pas la meme des deux cotes — le corpus echoue dans les DEUX sens,
parfois trop loin, parfois trop pres.

Usage :
    uv run python src/figures/figure_ou_poser_la_boite.py --verifier
    uv run python src/figures/figure_ou_poser_la_boite.py \\
        --sortie docs/images/83_ou_poser_la_boite.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "ou_poser_la_boite.json"
SPIRES_DU_PRIX = 31

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    act, mei = m["boite_actuelle"], m["meilleure_boite"]
    hors = m["bras_trop_loin"] + m["bras_trop_pres"]
    # ⚠ La pire paire est LUE dans la mesure, jamais nommee ici : un couple retape cesserait
    # d'etre le pire le jour ou la boite ou le treillis bougent.
    # ⚠⚠ SEULES LES PAIRES DE RANGS VOISINS COMPTENT ICI. `5→7` n'existe que dans les boites ou
    # la spire 6 est trop pauvre : son etendue decrit une population de boites, pas l'ecart entre
    # deux feuilles voisines. Les melanger a d'abord fait publier « aucune paire ne varie de
    # moins d'un facteur dix », que la batterie a dementi.
    voisines = [x for x in m["ecarts_par_paire"] if x["boites"] > 1 and x["consecutif"]]
    pire = voisines[0] if voisines else None
    pas = " puis ".join(str(int(q)) for q in m["pas_essayes"])
    lignes = [
        f"le plafond du corpus est le nombre de bras qu'un marcheur PARFAIT parcourrait avant "
        f"que les spires publiees lui demandent un saut qu'aucun membre de la famille ne sait "
        f"faire — le decalage atteignable vaut une demi-feuille, {m['demi_feuille_um']:.1f} µm. "
        "au-dela, toute portee mesuree est censuree. ce balayage ne fait tourner AUCUN marcheur : "
        "il ne regarde que ce que les spires se demandent les unes aux autres.",
        f"⚠⚠⚠ PANNEAU A — LE FRAGMENT EST MAUVAIS PARTOUT, PAS BON AILLEURS. sur "
        f"{m['boites_essayees']} placements de boite de {m['cote']:.0f} voxels, "
        f"{m['plafonds'].get('0', 0)} n'offrent meme pas un bras, la boite actuelle atteint "
        f"{act['plafond']}, et seules {m['boites_meilleures']} font mieux. le meilleur plafond du "
        f"fragment entier vaut {m['plafond_maximal']}. le prix en demande {SPIRES_DU_PRIX}.",
        f"★★ CE QUE CA ACHETE QUAND MEME : {m['gain_de_plafond']:+d} bras sans changer d'objet, "
        f"en posant la boite en {' '.join(f'{x:.0f}' for x in mei['centre'])} au lieu de "
        f"{' '.join(f'{x:.0f}' for x in act['centre'])}. ce n'est pas une marche meilleure, c'est "
        "une MESURE capable de juger deux bras plus loin — et un marcheur peut parfaitement "
        "echouer au deuxieme bras d'une chaine qui en offre huit, ce qu'un plafond a six "
        "interdisait d'observer.",
        f"⚠⚠ PANNEAU B — LE CORPUS ECHOUE DANS LES DEUX SENS. sur les {m['bras_au_total']} bras "
        f"de tous les placements, {hors} sont hors du pas nominal, soit "
        f"{hors / max(1, m['bras_au_total']):.0%} : {m['bras_trop_loin']} demandent TROP LOIN — "
        f"un trou de numerotation — et {m['bras_trop_pres']} TROP PRES, ce qui est une paire de "
        "spires que la boite ne separe pas. les confondre sous un seul mot perdrait ce qui "
        "distingue une lacune d'un doublon.",
        f"⚠⚠⚠ ET LE MAXIMUM DEPEND DU TREILLIS, donc il est publie comme un MINORANT : au pas "
        + " · ".join(f"{k} le meilleur sort a {v['plafond_maximal']}"
                     for k, v in m["par_pas"].items())
        + f". un treillis plus grossier ne peut que RATER un bon placement, jamais en inventer "
        f"un — le sens de l'erreur est donc connu. balaye ici aux pas {pas}.",
        "⚠ la boite se choisit sur le CORPUS et jamais sur le resultat. choisir celle ou la "
        "marche est belle serait choisir l'endroit ou le verdict arrange, ce que ce depot refuse "
        "partout ailleurs ; choisir celle ou le corpus est mesurable est le contraire — c'est "
        "retirer une limite d'instrument, pas fabriquer un resultat.",
        (f"⚠⚠⚠ ET LA MEME PAIRE DE SPIRES NE DEMANDE PAS LA MEME CHOSE PARTOUT. sur les "
         f"{len(voisines)} paires de rangs VOISINS vues dans plusieurs boites, l'ecart median "
         f"varie d'un facteur {min(x['rapport'] for x in voisines):.1f} a "
         f"{max(x['rapport'] for x in voisines):.1f}, et "
         f"{sum(1 for x in voisines if x['rapport'] >= 10)} d'entre elles de plus de dix. la "
         f"pire est {pire['de']}→{pire['vers']} : de {pire['ecart_min_um']:.1f} a "
         f"{pire['ecart_max_um']:.1f} µm sur {pire['boites']} placements, ×{pire['rapport']}. "
         "« les spires publiees sont des feuilles voisines » est donc vrai LOCALEMENT et faux "
         "comme enonce sur le fragment : a vingt micrometres deux spires sont la meme feuille, "
         "a douze cents elles sont a neuf feuilles l'une de l'autre.") if pire else "",
        f"⚠ ce que ca ne dit pas : que ce fragment puisse porter les {SPIRES_DU_PRIX} spires du "
        f"prix. il ne peut pas, et aucun placement n'y change rien — c'est le corpus, et non la "
        "boite, qui est la limite.",
    ]
    # ⚠ Une ligne vide serait DESSINEE vide : la ligne de la pire paire n'existe que si la mesure
    # a vu une paire dans plus d'une boite, et son absence ne doit pas laisser un trou.
    return [x for x in lignes if x]


def panneau_distribution(art, x0, y0, pw, ph, m, petit) -> int:
    """Combien de placements atteignent chaque plafond."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "placements de boîte par plafond atteint", fill=DISCRET,
             font=petit)
    plafonds = {int(k): v for k, v in m["plafonds"].items()}
    haut = max(plafonds) if plafonds else 0
    cles = list(range(0, haut + 1))
    gauche, droite = x0 + 62, x0 + pw - 26
    base, sommet = y0 + ph - 42, y0 + 40
    maxi = max(plafonds.values()) if plafonds else 1

    def px(k: int) -> float:
        return gauche + (droite - gauche) * k / max(1, len(cles))

    def py(v: float) -> float:
        return base - (base - sommet) * v / maxi

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0, maxi // 2, maxi):
        art.text((gauche - 52, py(g) - 6), f"{g:>5}", fill=DISCRET, font=petit)
    lg = (droite - gauche) / max(1, len(cles))
    dessinees = 0
    act = m["boite_actuelle"]["plafond"]
    for k in cles:
        n = plafonds.get(k, 0)
        x = px(k)
        coul = ROUGE if k == act else (VERT if k > act else BLEU)
        if n:
            art.rectangle([x + 2, py(n), x + lg - 3, base], fill=coul)
            art.text((x + 3, py(n) - 13), str(n), fill=coul, font=petit)
            dessinees += 1
        art.text((x + lg / 2 - 3, base + 6), str(k), fill=DISCRET, font=petit)
    art.text((px(act) + 2, sommet - 16), "la boîte actuelle", fill=ROUGE, font=petit)
    # ⚠⚠ LES 31 DU PRIX SONT HORS DE L'AXE, ET IL FAUT LE DIRE : une figure dont l'axe s'arrête
    # au maximum observé laisse croire que l'objectif est dans le cadre.
    # ⚠ La note vit dans l'EN-TETE et non dans le graphe : posée près de l'axe, elle tombait
    # exactement sur les trois barres qui portent le verdict (6, 7 et 8).
    note = f"les {SPIRES_DU_PRIX} du prix sont hors de cet axe"
    art.text((x0 + pw - 12 - petit.getbbox(note)[2], y0 + 6), note, fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : plafond du corpus, en bras",
             fill=DISCRET, font=petit)
    return dessinees


def panneau_bras(art, x0, y0, pw, ph, m, petit) -> int:
    """Où chaque boîte meurt : le trop loin et le trop près."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "ce que chaque bras demande, boîte actuelle puis meilleure",
             fill=DISCRET, font=petit)
    ecart = m["ecart_um"]
    demi = m["demi_feuille_um"]
    gauche, droite = x0 + 84, x0 + pw - 132
    maxi = 260.0
    lignes = [("actuelle", m["boite_actuelle"]), ("meilleure", m["meilleure_boite"])]
    total = sum(len(b["bras"]) for _, b in lignes) + len(lignes)
    hauteur = min(18, (ph - 88) / max(1, total))
    y = y0 + 44

    def px(v: float) -> float:
        return gauche + (droite - gauche) * min(v, maxi) / maxi

    art.rectangle([px(ecart - demi), y - 10, px(ecart + demi), y + hauteur * total + 2],
                  fill=PALE)
    art.line([px(ecart), y - 10, px(ecart), y + hauteur * total + 2], fill=VERT)
    art.text((px(ecart) - 26, y - 22), "pas nominal", fill=VERT, font=petit)
    marquees = 0
    for nom, b in lignes:
        art.text((x0 + 8, y - 1), f"{nom} ({b['plafond']})", fill=TEXTE, font=petit)
        y += hauteur
        for a in b["bras"]:
            hors = not a["au_pas_nominal"]
            coul = ROUGE if hors else BLEU
            art.text((x0 + 8, y - 1), f"  {a['de']}→{a['vers']}", fill=coul, font=petit)
            art.rectangle([gauche, y + 1, px(a["ecart_um"]), y + hauteur - 4], fill=coul)
            if a["ecart_um"] > maxi:
                marquees += 1
                art.text((px(maxi) + 3, y - 1), f"≫ {a['ecart_um']:.0f} — tronquée",
                         fill=ROUGE, font=petit)
            elif hors:
                sens = "trop loin" if a["ecart_um"] > ecart else "trop près"
                art.text((px(a["ecart_um"]) + 4, y - 1),
                         f"{a['ecart_um']:.0f} — {sens}", fill=ROUGE, font=petit)
            else:
                art.text((px(a["ecart_um"]) + 4, y - 1), f"{a['ecart_um']:.0f}", fill=coul,
                         font=petit)
            y += hauteur
    art.text((x0 + 8, y0 + ph - 18),
             f"bande verte : ±{demi:.0f} µm autour du pas — ce que la famille peut atteindre",
             fill=DISCRET, font=petit)
    return marquees


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 396
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Existe-t-il une boite ou la portee cesse d'etre censuree ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['boites_essayees']} placements · plafond actuel "
             f"{m['boite_actuelle']['plafond']} · meilleur du fragment "
             f"{m['plafond_maximal']} (MINORANT) · le prix en demande {SPIRES_DU_PRIX}",
             fill=DISCRET, font=moyen)
    titres = ("A · combien de placements atteignent quel plafond",
              "B · ou chaque boite meurt, et dans quel sens")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    barres = panneau_distribution(art, marge, 104, pw, ph, m, petit)
    marquees = panneau_bras(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "barres": barres, "tronquees": marquees,
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
    d = dessiner(m, RACINE / "docs" / "images" / "83_ou_poser_la_boite.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    # ⚠⚠ LA DISTRIBUTION DOIT ETRE DESSINEE EN ENTIER : un plafond present dans la mesure et
    # absent du panneau ferait lire un fragment meilleur qu'il n'est.
    v("chaque plafond non vide de la mesure a sa barre",
      d["barres"] == sum(1 for n in m["plafonds"].values() if n),
      f"{d['barres']} barres pour {len(m['plafonds'])} plafonds")
    # ⭐ Le verdict de la figure vient de la mesure, jamais d'une phrase qui aurait survécu.
    v("le maximum du fragment est déclaré comme un minorant",
      m["le_plafond_maximal_est_un_minorant"] is True
      and any("MINORANT" in x for x in prose(m)))
    v("... et le maximum reste très loin des 31 du prix",
      m["plafond_maximal"] < SPIRES_DU_PRIX,
      f"{m['plafond_maximal']} contre {SPIRES_DU_PRIX}")
    # ⚠⚠ LES DEUX SENS D'ECHEC SONT NOMMES : une lacune et un doublon ne se soignent pas pareil.
    v("les deux sens d'échec sont présents dans la mesure",
      m["bras_trop_loin"] > 0 and m["bras_trop_pres"] > 0,
      f"{m['bras_trop_loin']} trop loin, {m['bras_trop_pres']} trop près")
    v("... et la prose les distingue",
      any("TROP LOIN" in x and "TROP PRES" in x for x in prose(m)))
    # ⚠ La figure doit dire ce qui est ACHETE, sinon elle se lit comme un pur refus.
    v("la prose dit aussi ce que le déplacement achète",
      any("CE QUE CA ACHETE" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)
    # ⚠⚠ LA PIRE PAIRE EST LUE DANS LA MESURE, jamais nommée dans la prose : un couple retapé
    # cesserait d'être le pire le jour où la boîte ou le treillis bougent, et la figure
    # affirmerait un record qui n'en est plus un.
    vois = [x for x in m["ecarts_par_paire"] if x["boites"] > 1 and x["consecutif"]]
    v("la pire paire de rangs voisins vient de la mesure et la prose la porte",
      bool(vois) and any(f"×{vois[0]['rapport']}" in x for x in prose(m)),
      str(vois[0]) if vois else "aucune paire voisine vue plusieurs fois")
    # ⚠⚠⚠ CE CONTROLE A DEMENTI MA PROPRE PROSE. J'avais publie « aucune paire ne varie de moins
    # d'un facteur dix » : faux — `2→3` varie de ×2,6 — et le compte melangeait en plus les
    # paires a saut de rang. Ce qui est asserte est ce que la mesure dit : toutes varient, la
    # majorite de plus de dix, et le minimum est publie plutot qu'arrondi vers le haut.
    v("... et toutes les paires voisines varient d'au moins un facteur deux",
      all(x["rapport"] >= 2 for x in vois),
      str([(x["de"], x["vers"], x["rapport"]) for x in vois if x["rapport"] < 2]))
    v("... la majorité de plus de dix",
      sum(1 for x in vois if x["rapport"] >= 10) > len(vois) / 2,
      f"{sum(1 for x in vois if x['rapport'] >= 10)} sur {len(vois)}")
    # ⚠ Les paires à saut de rang sont EXCLUES du compte, et ce n'est pas cosmétique : elles ne
    # décrivent pas l'écart entre deux feuilles voisines.
    v("... et les paires à saut de rang sont exclues",
      all(x["consecutif"] for x in vois)
      and any(not x["consecutif"] for x in m["ecarts_par_paire"]))
    # ⚠ Une ligne vide serait dessinée vide.
    v("aucune ligne de prose n'est vide", all(x.strip() for x in prose(m)))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "83_ou_poser_la_boite.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
