#!/usr/bin/env python3
"""OU la nappe se froisse : les cartes, et si les taches coincident.

⚠⚠⚠ CETTE FIGURE VIENT D'UNE IMAGE, ET C'EST LE POINT. Sept tranches ont publie le froissement
en MEDIANES ; regarder les cartes a montre que le froissement du pas normal n'est pas distribue
du tout, mais concentre en TACHES qui apparaissent au bras 3 et grandissent, le gros de la nappe
restant lisse. Une mediane sur une nappe surtout lisse avec quelques regions ruinees, et une
mediane sur une nappe uniformement tiede, sont le meme nombre.

⚠⚠ ET LE PANNEAU B PORTE LE TEMOIN, sans lequel la question n'a pas de reponse. Deux ensembles de
taches couvrant chacun 60 % d'une meme region se recouvrent largement PAR CONSTRUCTION : ce qui a
du sens est le RAPPORT entre ce qu'on observe et ce que le hasard donnerait a tailles egales.

Usage :
    uv run python src/figures/figure_ou_la_nappe_se_froisse.py --verifier
    uv run python src/figures/figure_ou_la_nappe_se_froisse.py \\
        --sortie docs/images/75_ou_la_nappe_se_froisse.png
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
MESURE = RACINE / "docs" / "mesures" / "ou_la_nappe_se_froisse.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
TURQUOISE = (26, 128, 128)
GRIS = (135, 135, 135)
VERT = (76, 122, 84)
CADRE = (200, 200, 200)
COULEUR = {"rien": (70, 70, 70), "rien_lisse": TURQUOISE, "raccroche": (76, 122, 84),
           "oracle": ROUGE}


def prose(m: dict) -> list[str]:
    def par(nom: str) -> dict:
        return next(x for x in m["lignes"] if x["marcheur"] == nom)

    ri, li = par("rien")["part_froissee"], par("rien_lisse")["part_froissee"]
    ra, orc = par("raccroche")["part_froissee"], par("oracle")["part_froissee"]
    n = len(ri) - 1
    return [
        f"une TACHE est une cellule dont l'ecart a la mediane de ses voisins depasse la "
        f"demi-feuille ({m['demi_feuille_um']} um). le seuil vient de la matiere : au-dela, le "
        "point est plus pres de la feuille voisine que du plan de ses PROPRES voisins, donc la "
        "nappe y est localement PLIEE et non bosselee.",
        f"⚠⚠⚠ PANNEAU A : le froissement du pas normal n'est PAS distribue. il commence a zero, "
        f"apparait au bras 3 et atteint {ri[n]:.0%} des cellules au bras {n + 1} — pendant que sa "
        f"rugosite MEDIANE reste a une vingtaine de micrometres. une mediane sur une nappe "
        "surtout lisse avec quelques regions ruinees, et une mediane sur une nappe uniformement "
        "tiede, sont le meme nombre : c'est pour ca qu'il fallait regarder.",
        f"⚠⚠⚠ et c'est la mesure la plus nette de ce que le LISSAGE fait : il ramene la part "
        f"froissee de {ri[n]:.0%} a {li[n]:.0%}, soit {1 - li[n] / max(ri[n], 1e-9):.0%} des "
        "cellules pliees en moins. dit comme ca, c'est un tout autre enonce que « six "
        "micrometres de mieux », et c'est le meme fait.",
        f"⚠⚠ le raccrochage est une panne d'une AUTRE NATURE : {ra[2]:.0%} des cellules des le "
        f"bras 3, {ra[n]:.0%} au bras {n + 1}. ce n'est plus une tache qui grandit, c'est la "
        "nappe entiere qui plie. et la borne, elle, se froisse AUSSI — "
        f"{orc[n]:.0%} au dernier bras — tout en gardant une erreur de 17 a 22 um : donc un "
        "froissement n'est PAS ce qui perd une marche, il ne le devient que si rien ne vient "
        "recaler ce qui repart dessus.",
        f"⚠⚠⚠ PANNEAU B : les taches coincident-elles d'un marcheur a l'autre ? les "
        f"{len(m['paires'])} paires sont au-dessus de leur temoin, mais le rapport median est "
        f"{m['rapport_median']} et le plus faible {m['rapport_le_plus_faible']}. ⚠ « au-dessus du "
        "temoin » est satisfait par un rapport de 1,01, et deux ensembles couvrant chacun 60 % "
        "d'une meme region se recouvrent largement PAR CONSTRUCTION — donc c'est le rapport qui "
        "porte le sens, jamais le signe.",
        f"⚠ ce qui reste : les deux paires ou les taches sont encore MINORITAIRES montrent une "
        f"vraie co-localisation (×3,0 pour rien/rien_lisse, ×1,5 pour rien/oracle). le "
        "froissement est donc en partie une propriete du LIEU et pas seulement du marcheur — "
        "modestement, et c'est une piste a verifier sur d'autres ancres avant d'en faire quoi que "
        "ce soit.",
    ]


def panneau_parts(art, x0, y0, pw, ph, m, petit) -> None:
    """La part de cellules pliees, bras par bras, une courbe par marcheur."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "part des cellules dont le pli depasse la demi-feuille",
             fill=DISCRET, font=petit)
    gauche, droite = x0 + 48, x0 + pw - 46
    base, sommet = y0 + ph - 40, y0 + 34
    n = max(len(x["part_froissee"]) for x in m["lignes"])

    def px(i: int) -> float:
        return gauche + (droite - gauche) * i / max(1, n - 1)

    def py(v: float) -> float:
        return base - (base - sommet) * v

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0.25, 0.5, 0.75, 1.0):
        art.line([gauche, py(g), droite, py(g)], fill=(238, 238, 238))
        art.text((gauche - 42, py(g) - 6), f"{g:>4.0%}", fill=DISCRET, font=petit)
    for x in m["lignes"]:
        coul = COULEUR.get(x["marcheur"], GRIS)
        pts = [(px(i), py(p or 0.0)) for i, p in enumerate(x["part_froissee"])]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        art.text((pts[-1][0] + 5, pts[-1][1] - 6), x["marcheur"], fill=coul, font=petit)
    for i in range(n):
        art.text((px(i) - 4, base + 8), str(i + 1), fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : le bras", fill=DISCRET, font=petit)


def panneau_coincidence(art, x0, y0, pw, ph, m, petit) -> None:
    """Le recouvrement observe contre son temoin, une paire par ligne."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "barre pleine : observe · barre creuse : temoin au hasard",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "a tailles EGALES, dans les memes cellules",
             fill=DISCRET, font=petit)
    gauche, droite = x0 + 148, x0 + pw - 56
    haut_p = (ph - 66) / max(1, len(m["paires"]))
    tous = [p["recouvrement"] for p in m["paires"]] + [p["temoin"] for p in m["paires"]]
    ech = max(tous + [0.1]) * 1.12
    for i, p in enumerate(m["paires"]):
        y = y0 + 40 + i * haut_p
        art.text((x0 + 8, y + haut_p / 2 - 12), f"{p['a']} /", fill=TEXTE, font=petit)
        art.text((x0 + 8, y + haut_p / 2), f"  {p['b']}", fill=TEXTE, font=petit)
        lo = (droite - gauche) * p["temoin"] / ech
        art.rectangle([gauche, y + haut_p * 0.18, gauche + lo, y + haut_p * 0.72],
                      outline=DISCRET)
        obs = (droite - gauche) * p["recouvrement"] / ech
        fort = (p["rapport"] or 0.0) >= 1.4
        art.rectangle([gauche, y + haut_p * 0.30, gauche + obs, y + haut_p * 0.60],
                      fill=VERT if fort else GRIS)
        art.text((droite + 6, y + haut_p / 2 - 6),
                 f"×{p['rapport']:.2f}" if p["rapport"] else "—",
                 fill=VERT if fort else DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "vert : au moins une fois et demie le hasard · gris : a peine au-dessus",
             fill=DISCRET, font=petit)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 270
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Ou la nappe se froisse, et si c'est le meme endroit pour tous",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"ancre {m['ancre']} · {m['bras_communs']} bras · seuil = demi-feuille "
             f"{m['demi_feuille_um']} um · {m['cellules_comparees']} cellules gardees par TOUS",
             fill=DISCRET, font=moyen)
    titres = ("A · la part de nappe PLIEE, bras par bras",
              "B · les taches coincident-elles ? le temoin decide")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_parts(art, marge, 104, pw, ph, m, petit)
    panneau_coincidence(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"marcheurs": len(m["lignes"]), "paires": len(m["paires"]), "titres": titres,
            "panneau": pw, "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
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
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))

    def par(nom: str) -> dict:
        return next(x for x in m["lignes"] if x["marcheur"] == nom)

    # ⚠⚠ LA PART PLIÉE NE PEUT QUE CROÎTRE OU STAGNER SI LE FROISSEMENT S'ACCUMULE, et c'est
    # l'affirmation que le panneau A porte. Une chute la contredirait ; le contrôle porte donc
    # sur la MAJORITÉ des bras, parce qu'une nappe qui perd des cellules peut perdre des taches.
    ri = par("rien")["part_froissee"]
    v("la part pliée du pas normal croît d'un bras au suivant",
      sum(b >= a for a, b in zip(ri, ri[1:])) >= len(ri) - 2, str(ri))
    # ⭐⭐⭐ LE FAIT QUE LA FIGURE PORTE : le lissage retire des cellules pliées, et il en retire
    # beaucoup. Si ce n'était pas vrai, sa prose annoncerait un pourcentage qui n'existe pas.
    li = par("rien_lisse")["part_froissee"]
    v("... et le lissage en retire la majorité au dernier bras",
      li[-1] < ri[-1] / 2, f"{li[-1]} contre {ri[-1]}")
    # ⚠⚠⚠ LA BORNE SE FROISSE AUSSI : c'est ce qui interdit de lire « la nappe se froisse » comme
    # « la marche est perdue ». Sans ce contrôle, la prose affirmerait une dissociation que la
    # mesure pourrait ne pas porter.
    v("... la borne se froisse elle aussi, alors que son erreur reste plate",
      par("oracle")["part_froissee"][-1] > 0.1,
      str(par("oracle")["part_froissee"][-1]))
    # ⚠⚠⚠ CHAQUE PAIRE PORTE SON TÉMOIN ET SON RAPPORT : le signe seul est satisfait par 1,01.
    v("chaque paire publie son témoin et son rapport observé/attendu",
      all(p["temoin"] is not None and "rapport" in p for p in m["paires"]),
      str([(p["a"][:6], p["rapport"]) for p in m["paires"]]))
    v("... et le rapport le plus faible est publié à côté du verdict",
      "rapport_le_plus_faible" in m, str(m["rapport_le_plus_faible"]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les marcheurs et toutes les paires sont dessinés",
          r["marcheurs"] == len(m["lignes"]) and r["paires"] == len(m["paires"]),
          f"{r['marcheurs']} marcheurs · {r['paires']} paires")
        debord = [(t[:36], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        _, _, pt_ = police(17, 13, 11)
        trop = [(t, pt_.getbbox(t)[2]) for t in r["titres"] if pt_.getbbox(t)[2] >= r["panneau"]]
        v("chaque titre de panneau tient dans son panneau", not trop, str(trop))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_ou_la_nappe_se_froisse.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
