#!/usr/bin/env python3
"""La portee mesure-t-elle le MARCHEUR, ou le mur du corpus ?

⚠⚠⚠ CETTE FIGURE AUDITE LE RESULTAT CENTRAL DU DEPOT. Le panneau A montre le mur : un saut de
1000,6 µm entre les spires 10 et 11, la ou le pas nominal en demande 135,5 et ou la famille ne
sait decaler que de ±67,8. Le panneau B montre ce que ce mur fait a la mesure : l'oracle y est
colle sur les CINQ ancres, donc « la borne vaut 6 » n'est pas etabli, et deux ancres n'offrent
plus assez de dynamique pour separer quoi que ce soit.

⚠⚠ LA BARRE DU BRAS 7 EST TRONQUEE et le dit : a l'echelle des autres, elle sortirait du panneau
cinq fois. Une barre coupee sans le dire ferait lire une limite de dessin comme une mesure.

Usage :
    uv run python src/figures/figure_le_mur_du_corpus.py --verifier
    uv run python src/figures/figure_le_mur_du_corpus.py \\
        --sortie docs/images/82_le_mur_du_corpus.png
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
MESURE = RACINE / "docs" / "mesures" / "le_mur_du_corpus.json"
MARCHE = RACINE / "docs" / "mesures" / "la_portee_du_raccrochage.json"
BORNE = "oracle"

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
    mur = m["mur"]
    sans = m["ancres_sans_pouvoir_de_separer"]
    return [
        f"une portee est un nombre de spires traversees avant que l'erreur depasse la "
        f"demi-feuille ({m['demi_feuille_um']} µm). ce que ce depot n'avait pas croise : le "
        f"corpus lui-meme impose un plafond, et deux mesures publiees cote a cote — « la borne "
        f"(oracle) : 6 » et « ce que le corpus autorise : 6 » — sont le MEME 6.",
        f"⚠⚠⚠ PANNEAU A — LE MUR. le bras {mur['bras']} relie les spires {mur['de']} et "
        f"{mur['vers']}, voisines par leur NUMERO, et il demande {mur['ecart_um']} µm la ou le "
        f"pas nominal en demande 135.5 — soit {mur['ecart_au_pas_um']} µm d'ecart. or la famille "
        f"entiere ne sait decaler que de ±{m['glissement_maximal_um']} µm, une demi-feuille : le "
        f"bras est donc a {m['mur_en_glissements']}× ce qu'elle peut atteindre. ce n'est pas un "
        "echec de methode, c'est une impossibilite de construction — l'oracle compris.",
        f"⚠⚠⚠ PANNEAU B — CE QUE LE MUR FAIT A LA MESURE. une portee egale au plafond est une "
        f"observation CENSUREE A DROITE : elle dit « au moins », jamais « vaut ». l'oracle y est "
        f"colle sur {len(m['ancres_ou_la_borne_est_censuree'])}/{m['ancres']} ancres, donc « la "
        "borne vaut 6 » n'est PAS etabli — la vraie borne est inconnue et superieure ou egale a "
        "6. c'est le peche numero un de ce depot, une limite de grille publiee comme une limite "
        "materielle, present dans son resultat le plus cite.",
        f"⚠⚠ ET LES CINQ ANCRES NE SONT PAS CINQ REPLICATIONS. leurs plafonds valent exactement "
        f"{mur['de']} moins l'ancre — {', '.join(str(l['plafond']) for l in m['lignes'])} — donc "
        "elles meurent toutes au MEME saut. « le signe tient sur 5/5 ancres » compte cinq fois "
        "un seul defaut du corpus.",
        f"▲▲ et deux d'entre elles ne separent RIEN : aux ancres {' et '.join(map(str, sans))} "
        "les sept marcheurs aveugles rendent tous le meme nombre. une ancre dont le plafond vaut "
        "2 offre trois valeurs dont une censuree ; elle ne peut separer aucune paire de methodes, "
        "quelles qu'elles soient. les compter comme des confirmations, c'est compter du silence.",
        "★★ CE QUI TIENT, ET IL FAUT LE DIRE AUSSI : a l'ancre 4 le plafond vaut 6, quatre "
        "valeurs distinctes sortent, et le pas normal (4) comme sa version lissee (5) sont SOUS "
        "le plafond. cette comparaison-la mesure bien les marcheurs, et le gain d'un bras par le "
        "lissage n'est pas touche par cet audit. ce qui tombe est la BORNE, pas le resultat.",
        "⚠ ce que ca ouvre : la marge reelle entre le meilleur marcheur aveugle et la borne est "
        "INCONNUE, et non « un bras ». elle pourrait etre bien plus grande — ce qui serait une "
        "bonne nouvelle pour l'objectif — et la mesurer demande un corpus sans ce trou.",
    ]


def panneau_mur(art, x0, y0, pw, ph, m, mrch, petit) -> dict:
    """Chaque bras du corpus par ce qu'il demande, contre ce que la famille peut atteindre."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "ce que chaque bras du corpus demande, en µm",
             fill=DISCRET, font=petit)
    bras = mrch["bras_du_corpus"]
    pas = 135.5
    gliss = float(m["glissement_maximal_um"])
    gauche, droite = x0 + 74, x0 + pw - 176
    haut = y0 + 44
    hauteur = min(26, (ph - 76) / max(1, len(bras)))
    # ⚠⚠ L'ECHELLE S'ARRETE A LA FENETRE ATTEIGNABLE ELARGIE, pas au plus grand bras : sinon le
    # saut ecrase les sept autres barres contre zero et la figure ne montre plus rien de ce
    # qu'elle sert a montrer. La barre qui deborde est TRONQUEE et le dit.
    maxi = 260.0

    def px(v: float) -> float:
        return gauche + (droite - gauche) * min(v, maxi) / maxi

    # ⭐ La fenetre atteignable est PEINTE, parce que c'est elle qui rend le verdict lisible :
    # un bras hors de la bande est hors de portee de tout marcheur de la famille.
    art.rectangle([px(pas - gliss), haut - 8, px(pas + gliss), haut + hauteur * len(bras) + 2],
                  fill=PALE)
    art.line([px(pas), haut - 8, px(pas), haut + hauteur * len(bras) + 2], fill=VERT)
    art.text((px(pas) - 26, haut - 20), "pas nominal", fill=VERT, font=petit)
    art.text((px(pas + gliss) + 3, haut - 20), f"+{gliss:.0f}", fill=VERT, font=petit)
    tronquees = 0
    deborde = -1e9
    for i, b in enumerate(bras):
        y = haut + i * hauteur
        hors = not b["au_pas_nominal"]
        coul = ROUGE if hors else BLEU
        art.text((x0 + 8, y - 1), f"{b['de']}→{b['vers']}", fill=coul, font=petit)
        art.rectangle([gauche, y + 1, px(b["ecart_um"]), y + hauteur - 5], fill=coul)
        if b["ecart_um"] > maxi:
            tronquees += 1
            # ⚠ LE DEBORDEMENT EST MESURE CONTRE LE CADRE, pas ajuste a l'oeil : une etiquette
            # plus large que son panneau sort dans la gouttiere et touche le panneau voisin.
            etiquette = f"≫ {b['ecart_um']:.0f} µm — barre tronquée"
            deborde = max(deborde, px(maxi) + 3 + petit.getbbox(etiquette)[2] - (x0 + pw))
            art.text((px(maxi) + 3, y - 1), etiquette, fill=ROUGE, font=petit)
        else:
            art.text((px(b["ecart_um"]) + 4, y - 1), f"{b['ecart_um']:.0f}", fill=coul,
                     font=petit)
    art.line([gauche, haut + hauteur * len(bras) + 2, droite,
              haut + hauteur * len(bras) + 2], fill=TEXTE)
    art.text((x0 + 8, y0 + ph - 18),
             f"bande verte : ±{gliss:.0f} µm autour du pas — ce que la famille peut atteindre",
             fill=DISCRET, font=petit)
    return {"tronquees": tronquees, "maxi": maxi, "deborde": deborde}


def panneau_censure(art, x0, y0, pw, ph, m, petit) -> int:
    """Chaque ancre x chaque marcheur : la portee, et si elle est collee au plafond.

    ⚠⚠ UNE MATRICE ET NON DES BARRES. A cinq ancres et huit marcheurs, huit barres par ligne
    font des colonnes de six pixels dont aucune n'est lisible, et les etiquettes se recouvrent.
    Ce qui doit se lire ici n'est pas une hauteur, c'est **quelles cases touchent le plafond** :
    un nombre dans une case le dit, une barre minuscule non.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "portee de chaque marcheur · encadre rouge = collee au plafond, "
             "donc censuree", fill=DISCRET, font=petit)
    lignes = m["lignes"]
    noms = [n for n in lignes[0]["marcheurs"] if n != BORNE] + [BORNE]
    gauche = x0 + 58
    largeur = (pw - 74 - 58) / len(noms)
    haut = y0 + 62
    hauteur = min(30, (ph - 96) / max(1, len(lignes)))
    # ⚠ Les noms sont ecrits sur DEUX rangees en quinconce : a huit colonnes de cinquante
    # pixels, une seule rangee les fait se chevaucher, et un nom coupe ne nomme rien.
    for j, n in enumerate(noms):
        y = haut - 30 + (14 if j % 2 else 0)
        art.text((gauche + j * largeur + 2, y), n[:11], fill=DISCRET, font=petit)
    art.text((gauche + len(noms) * largeur + 8, haut - 23), "plafond", fill=ROUGE, font=petit)
    censurees = 0
    for i, l in enumerate(lignes):
        y = haut + i * hauteur
        sep = l["pouvoir_de_separer"]
        art.text((x0 + 8, y + 2), f"ancre {l['ancre']}", fill=TEXTE, font=petit)
        art.text((x0 + 8, y + 14), f"sépare {sep}",
                 fill=(DISCRET if sep > 1 else ROUGE), font=petit)
        for j, n in enumerate(noms):
            e = l["marcheurs"][n]
            x = gauche + j * largeur
            # ⭐ La couleur porte la MARGE au plafond, pas la portee : c'est la marge qui dit si
            # le nombre mesure le marcheur, et deux ancres de plafonds differents ne se
            # comparent pas par leur portee brute.
            if e["censuree"]:
                censurees += 1
                art.rectangle([x + 1, y, x + largeur - 3, y + hauteur - 6], fill=(246, 226, 222),
                              outline=ROUGE, width=2)
                art.text((x + 6, y + hauteur / 2 - 12), f"≥{e['portee']}", fill=ROUGE, font=petit)
            else:
                fond = PALE if e["marge"] >= 2 else (238, 238, 238)
                art.rectangle([x + 1, y, x + largeur - 3, y + hauteur - 6], fill=fond,
                              outline=GRIS)
                art.text((x + 8, y + hauteur / 2 - 12), str(e["portee"]),
                         fill=(VERT if e["marge"] >= 2 else TEXTE), font=petit)
        x = gauche + len(noms) * largeur
        art.rectangle([x + 5, y, x + 44, y + hauteur - 6], outline=ROUGE)
        art.text((x + 20, y + hauteur / 2 - 12), str(l["plafond"]), fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 30),
             "vert : au moins deux bras de marge · gris : un seul · « sépare » : valeurs",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "distinctes et non censurées, hors la borne — 1 veut dire qu'on ne sépare rien",
             fill=DISCRET, font=petit)
    return censurees


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    mrch = json.loads(MARCHE.read_text())
    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 296
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "La portee mesure-t-elle le MARCHEUR, ou le mur du corpus ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · le saut {m['mur']['de']}→{m['mur']['vers']} vaut "
             f"{m['mur_en_glissements']}× le decalage atteignable · la borne est censuree sur "
             f"{len(m['ancres_ou_la_borne_est_censuree'])}/{m['ancres']} ancres",
             fill=DISCRET, font=moyen)
    titres = ("A · le mur : ce que chaque bras demande",
              "B · ce qu'il fait a la mesure, ancre par ancre")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_mur(art, marge, 104, pw, ph, m, mrch, petit)
    censurees = panneau_censure(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "tronquees": a["tronquees"], "censurees": censurees,
            "deborde_mur": a["deborde"],
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

    if not (MESURE.is_file() and MARCHE.is_file()):
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, RACINE / "docs" / "images" / "82_le_mur_du_corpus.png")
    v("la figure est écrite", d["sortie"] and Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    # ⚠⚠ UNE BARRE TRONQUEE DOIT L'ETRE ET LE DIRE. Si l'échelle finissait par contenir le saut,
    # les sept autres barres seraient écrasées contre zéro et le panneau ne montrerait plus la
    # bande atteignable, qui est tout son sujet.
    v("la barre du mur est tronquée, et une seule l'est", d["tronquees"] == 1,
      str(d["tronquees"]))
    v("... et son étiquette tient dans le cadre du panneau", d["deborde_mur"] <= 0,
      f"déborde de {d['deborde_mur']:.0f} px")
    # ⭐⭐⭐ LE VERDICT DESSINE DOIT ETRE CELUI DE LA MESURE : autant de marques de censure que
    # d'observations censurées, sinon la figure adoucit ce qu'elle est là pour montrer.
    attendu = sum(len(l["censures"]) for l in m["lignes"])
    v("chaque observation censurée porte sa marque", d["censurees"] == attendu,
      f"{d['censurees']} marques pour {attendu} censures")
    v("la borne est censurée sur les cinq ancres", m["la_borne_est_censuree_partout"],
      str(m["ancres_ou_la_borne_est_censuree"]))
    v("un seul mur explique les cinq plafonds", m["le_meme_mur_explique_tout"])
    # ⚠ La figure doit aussi porter ce qui TIENT, sinon elle fait lire un audit comme une
    # rétractation générale.
    v("la prose dit aussi ce qui tient", any("CE QUI TIENT" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "82_le_mur_du_corpus.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
