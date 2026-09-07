#!/usr/bin/env python3
"""Le verdict de la marche tient-il depuis une autre ancre ?

⚠⚠⚠ POURQUOI CETTE FIGURE EXISTE. Un verdict tire d'UNE marche depuis UNE ancre est une
hypothese sur les autres. Ce depot a deja vu trois verdicts s'inverser en changeant la
population — passer de sept a six pas deplacait l'erreur du chemin deploye de 36,0 a 48,5 um —
et c'est cette decouverte qui a produit l'ecart apparie.

⚠⚠ ET ELLE PORTE UNE NUANCE QUE LE TITRE DE LA TRANCHE PRECEDENTE NE PORTAIT PAS : le GAIN
apparie tient partout, le BRAS gagne non. Les deux panneaux existent pour qu'on ne puisse pas
lire l'un pour l'autre.

Usage :
    uv run python src/figures/figure_la_portee_tient_elle_ailleurs.py --verifier
    uv run python src/figures/figure_la_portee_tient_elle_ailleurs.py \\
        --sortie docs/images/75_la_portee_tient_elle_ailleurs.png
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
MESURE = RACINE / "docs" / "mesures" / "la_portee_tient_elle_ailleurs.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
TURQUOISE = (26, 128, 128)
GRIS = (110, 110, 110)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
PALE = (236, 243, 242)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    neg, gag = m["ancres_ou_lecart_est_negatif"], m["ancres_ou_la_portee_gagne"]
    e = [x["ecart"]["ecart_median_um"] for x in m["lignes"] if x["ecart"]]
    return [
        f"la meme marche est refaite depuis {m['ancres']} ancres, la spire la plus basse de la "
        "boite puis chacune des suivantes. ⚠⚠ les ancres ne sont PAS comparables entre elles : "
        "une ancre plus haute a moins de bras devant elle et rencontre d'autres spires, donc "
        "rien n'est moyenne ici. ce qui s'agrege est le COMPTE des ancres ou le signe tient, "
        "qui est un fait sur la robustesse et non sur la matiere.",
        f"⚠⚠⚠ PANNEAU A : l'ecart apparie du marcheur lisse au pas normal seul est NEGATIF aux "
        f"{len(neg)} ancres sur {m['ancres']} — {', '.join(f'{x:+.1f}' for x in e)} um — et la "
        "majorite des bras est amelioree a chaque fois. le gain de la nappe lissee n'est donc "
        "pas une propriete de l'ancre ou il a ete trouve.",
        f"⚠⚠⚠ PANNEAU B : mais la PORTEE ne gagne un bras qu'a {len(gag)} ancre sur "
        f"{m['ancres']}. un gain de six micrometres est constant et fin ; un bras gagne demande "
        "que l'erreur passe SOUS le seuil de la demi-feuille, ce qui n'arrive que la ou elle en "
        "etait deja proche — a l'ancre 4 le pas normal seul lisait 72,2 um pour un seuil de "
        "67,75. publier le second a la place du premier ferait passer la chance d'une ancre "
        "pour une propriete de la methode.",
        f"⚠⚠ et la colonne du CORPUS tombe avec l'ancre ({', '.join(str(x['bras_au_pas_nominal']) for x in m['lignes'])}) : "
        "plus on part haut, moins il reste de bras que le corpus demande au pas nominal avant "
        "son trou. les portees courtes des ancres hautes ne sont donc pas un echec de methode, "
        "c'est la matiere qui s'arrete.",
    ]


def panneau_ecarts(art, x0, y0, pw, ph, m, petit, moyen) -> None:
    """L'ecart apparie a chaque ancre, avec son intervalle."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "negatif = le marcheur lisse fait mieux", fill=DISCRET, font=petit)
    gauche, droite = x0 + 54, x0 + pw - 26
    base, sommet = y0 + ph - 26, y0 + 40
    bornes = [b for x in m["lignes"] if x["ecart"] for b in x["ecart"]["intervalle_um"]]
    lo, hi = min(bornes + [0.0]) * 1.15, max(bornes + [0.0]) * 1.15 + 0.5

    def py(v: float) -> float:
        return base - (base - sommet) * (v - lo) / (hi - lo)

    art.rectangle([gauche - 10, sommet, droite + 10, py(0.0)], fill=PALE)
    art.line([gauche - 10, py(0.0), droite + 10, py(0.0)], fill=TEXTE)
    art.text((gauche - 48, py(0.0) - 6), "   0", fill=TEXTE, font=petit)
    for g in (-10, -5, 5):
        if lo < g < hi:
            art.text((gauche - 48, py(g) - 6), f"{g:>4}", fill=DISCRET, font=petit)
    n = len(m["lignes"])
    for i, x in enumerate(m["lignes"]):
        cx = gauche + (droite - gauche) * (i + 0.5) / n
        e = x["ecart"]
        if not e:
            continue
        b0, b1 = e["intervalle_um"]
        art.line([cx, py(b0), cx, py(b1)], fill=TURQUOISE, width=2)
        art.line([cx - 7, py(b0), cx + 7, py(b0)], fill=TURQUOISE)
        art.line([cx - 7, py(b1), cx + 7, py(b1)], fill=TURQUOISE)
        art.ellipse([cx - 5, py(e["ecart_median_um"]) - 5, cx + 5,
                     py(e["ecart_median_um"]) + 5], fill=TURQUOISE)
        art.text((cx - 22, base + 10), f"spire {x['ancre']}", fill=DISCRET, font=petit)
        art.text((cx - 12, py(b1) - 15), f"{e['pas_ameliores']}/{e['pas']}", fill=VERT,
                 font=petit)
    art.text((x0 + 8, y0 + 19), "um · sous la ligne, le lisse gagne · la fraction verte est "
             "le nombre de bras ameliores", fill=DISCRET, font=petit)


def panneau_portees(art, x0, y0, pw, ph, m, petit, moyen) -> None:
    """Les deux portees a chaque ancre, et le nombre de bras que le corpus autorise."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "barre claire : ce que le corpus autorise a cette ancre",
             fill=DISCRET, font=petit)
    gauche, droite = x0 + 44, x0 + pw - 26
    base, sommet = y0 + ph - 26, y0 + 40
    haut = max([x["bras_au_pas_nominal"] for x in m["lignes"]]
               + [x["portee_candidat"] for x in m["lignes"]]) + 1

    def py(v: float) -> float:
        return base - (base - sommet) * v / haut

    n = len(m["lignes"])
    larg = (droite - gauche) / n * 0.3
    for i, x in enumerate(m["lignes"]):
        cx = gauche + (droite - gauche) * (i + 0.5) / n
        art.rectangle([cx - larg * 1.6, py(x["bras_au_pas_nominal"]), cx + larg * 1.6, base],
                      fill=(232, 238, 240))
        art.rectangle([cx - larg * 1.05, py(x["portee_reference"]), cx - larg * 0.05, base],
                      fill=GRIS)
        art.rectangle([cx + larg * 0.05, py(x["portee_candidat"]), cx + larg * 1.05, base],
                      fill=TURQUOISE)
        if x["portee_candidat"] > x["portee_reference"]:
            art.ellipse([cx + larg * 0.25, py(x["portee_candidat"]) - 18,
                         cx + larg * 0.85, py(x["portee_candidat"]) - 6], outline=ROUGE, width=2)
        art.text((cx - 22, base + 10), f"spire {x['ancre']}", fill=DISCRET, font=petit)
    for g in range(1, haut):
        art.text((gauche - 38, py(g) - 6), f"{g:>3}", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19),
             "gris : pas normal seul · turquoise : + nappe lissee · cercle : un bras gagne",
             fill=DISCRET, font=petit)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 262
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Le verdict de la marche tient-il depuis une autre ancre ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['ancres']} ancres · candidat « {m['candidat']} » contre « {m['reference']} » · "
             f"le signe tient sur {m['ancres_ou_le_signe_tient']}/{m['ancres']}",
             fill=DISCRET, font=moyen)
    titres = ("A · l'ecart apparie, ancre par ancre",
              "B · la portee, et ce que le corpus autorise")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_ecarts(art, marge, 104, pw, ph, m, petit, moyen)
    panneau_portees(art, marge + pw + ecart, 104, pw, ph, m, petit, moyen)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"ancres": len(m["lignes"]), "titres": titres, "panneau": pw,
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
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠ CHAQUE ANCRE EST UNE MARCHE À PART : si deux lignes partaient de la même spire, le
    # balayage n'aurait pas balayé et le compte d'ancres serait un compte de répétitions.
    v("chaque ancre part d'une spire différente",
      len({x["ancre"] for x in m["lignes"]}) == len(m["lignes"]),
      str([x["ancre"] for x in m["lignes"]]))
    # ⚠⚠⚠ LA NUANCE QUE CETTE FIGURE EXISTE POUR PORTER : les deux verdicts sont distincts, et
    # celui de la portée est inclus dans celui de l'écart, jamais l'inverse.
    v("« l'écart est négatif » et « la portée gagne » sont deux comptes distincts",
      set(m["ancres_ou_la_portee_gagne"]) <= set(m["ancres_ou_lecart_est_negatif"]),
      f"portée {m['ancres_ou_la_portee_gagne']} ⊆ écart "
      f"{m['ancres_ou_lecart_est_negatif']}")
    # ⚠ AUCUNE PORTÉE NE PEUT DÉPASSER CE QUE LE CORPUS AUTORISE À CETTE ANCRE.
    v("... et aucune portée ne dépasse ce que le corpus demande au pas nominal",
      all(x["portee_candidat"] <= x["bras_au_pas_nominal"]
          and x["portee_reference"] <= x["bras_au_pas_nominal"] for x in m["lignes"]),
      str([(x["ancre"], x["portee_candidat"], x["bras_au_pas_nominal"]) for x in m["lignes"]]))
    v("chaque ancre publie son écart apparié avec son intervalle",
      all(x["ecart"] and x["ecart"]["intervalle_um"] for x in m["lignes"]),
      str([x["ecart"]["ecart_median_um"] for x in m["lignes"] if x["ecart"]]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les ancres sont dessinées", r["ancres"] == len(m["lignes"]), str(r["ancres"]))
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
                   default=RACINE / "docs" / "images" / "75_la_portee_tient_elle_ailleurs.png")
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
