#!/usr/bin/env python3
"""La longueur locale du pas ne se lit pas : ce qui revient est un tirage dans la fenêtre.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le nombre qui trompe est la médiane : **136,5 µm lus contre
135,5 publiés**, un accord à sept millièmes, et il ne prouve rien du tout — la médiane d'un
tirage uniforme dans une fenêtre qui s'ouvre à une demi-longueur et se ferme à une et demie vaut
exactement la longueur nominale. Dessiner les trois distributions côte à côte avec **les bornes
de la fenêtre** montre d'un coup ce qu'un tableau de trois nombres cache.

⭐⭐ Le second panneau porte le verdict, et son étalon est **calculé** : deux tirages indépendants
dans une fenêtre de largeur W s'écartent, en médiane, de W(1 − 1/√2). L'écart mesuré entre la
lecture et son témoin en vaut 95 %.

Usage :
    uv run python src/figures/figure_la_longueur_locale_du_pas.py --verifier
    uv run python src/figures/figure_la_longueur_locale_du_pas.py \\
        --sortie docs/images/75_la_longueur_locale_du_pas.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_longueur_locale_du_pas.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    a = m["accord"]
    return [
        f"la crete suivante le long de la normale EST la feuille voisine, et elle se lit sans la "
        f"cible : {m['longueurs_lues']['n']} lignes sur {m['spires']} spires.",
        f"la mediane lue vaut {m['longueurs_lues']['mediane']} um contre "
        f"{m['longueurs_publiees']['mediane']} publiee, soit {abs(a['mediane']):.3f} d'ecart — et "
        "ce nombre ne prouve RIEN : la mediane d'un tirage uniforme dans [0,5 L ; 1,5 L] vaut "
        "exactement L.",
        f"la queue, elle, est TRONQUEE : la fenetre se ferme a {m['borne_haute_um']} um quand le "
        f"neuvieme decile publie est a {m['longueurs_publiees']['p90']}. exclure la deuxieme "
        "voisine et atteindre le neuvieme decile sont deux exigences incompatibles sur ce corpus.",
        f"et le verdict est cellule par cellule : la lecture et son temoin s'ecartent de "
        f"{m['part_de_la_fenetre_qui_separe_du_temoin']} de la fenetre quand deux tirages "
        f"INDEPENDANTS s'en ecarteraient de {m['ecart_attendu_si_tirages_independants']}. "
        "ce qui revient est un tirage dans la fenetre, pas une longueur.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    marge, pw, ph, ecart = 40, 400, 230, 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18),
             "La longueur locale ne se lit pas : ce qui revient est un tirage dans la fenetre",
             fill=TEXTE, font=gros)
    art.text((marge, 42), f"volume brut, {m['spires']} spires, "
             f"{m['longueurs_lues']['n']} lignes, pas nominal {m['pas_nominal_um']} um",
             fill=DISCRET, font=moyen)

    # ---------- A : les trois distributions, dans la fenetre ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · les trois distributions, et les bornes de la recherche",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    hautmax = max(m["longueurs_publiees"]["p90"], m["borne_haute_um"]) * 1.12

    def xv(u):
        return ax + u / hautmax * pw

    for u, coul, lab in ((m["fenetre_um"][0], AMBRE, "la fenetre s'ouvre"),
                         (m["borne_haute_um"], AMBRE, "et se ferme")):
        art.line([xv(u), ay, xv(u), ay + ph], fill=AMBRE, width=2)
    art.text((xv(m["fenetre_um"][0]) + 4, ay + 6), "fenetre", fill=AMBRE, font=petit)
    art.text((xv(m["borne_haute_um"]) - 60, ay + 6), f"{m['borne_haute_um']:.0f}µ",
             fill=AMBRE, font=petit)

    series = [("lues dans le volume", m["longueurs_lues"], BLEU),
              ("publiees (spires)", m["longueurs_publiees"], TEXTE),
              ("temoin melange", m["temoin_melange"], ROUGE)]
    for k, (nom, d, coul) in enumerate(series):
        y = ay + 46 + k * 58
        art.line([xv(d["p10"]), y, xv(d["p90"]), y], fill=coul, width=4)
        for u in (d["p10"], d["p90"]):
            art.line([xv(u), y - 7, xv(u), y + 7], fill=coul, width=3)
        art.ellipse([xv(d["mediane"]) - 6, y - 6, xv(d["mediane"]) + 6, y + 6], fill=coul)
        art.text((ax + 8, y - 26), nom, fill=coul, font=petit)
        art.text((xv(d["p90"]) + 6, y - 6), f"{d['p90']:.0f}µ", fill=coul, font=petit)
    art.text((ax + 8, ay + ph - 30),
             "trait : du 1er au 9e decile · point : la mediane", fill=DISCRET, font=petit)
    art.text((ax + 8, ay + ph + 3), "0", fill=DISCRET, font=petit)
    art.text((ax + pw - 40, ay + ph + 3), f"{hautmax:.0f}µ", fill=DISCRET, font=petit)

    # ---------- B : l'ecart au temoin contre l'etalon calcule ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · l'ecart au temoin, cellule par cellule",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    ref = m["ecart_attendu_si_tirages_independants"]
    mes = m["part_de_la_fenetre_qui_separe_du_temoin"]
    plus = ref * 1.5
    for k, (nom, val, coul) in enumerate((
            ("deux tirages INDEPENDANTS dans la fenetre", ref, DISCRET),
            ("mesure : la lecture contre son temoin", mes, ROUGE),
            ("ce qu'une vraie lecture rendrait (~0)", 0.0, BLEU))):
        y = by + 46 + k * 56
        w = val / plus * (pw - 80)
        art.rectangle([bx + 30, y, bx + 30 + w, y + 26], fill=coul)
        art.text((bx + 30, y - 16), nom, fill=coul, font=petit)
        art.text((bx + 36 + w, y + 6), f"{val:.3f}", fill=TEXTE, font=petit)
    art.text((bx + 8, by + ph - 46),
             "en part de la largeur de la fenetre "
             f"({m['largeur_de_la_fenetre_um']:.0f} um)", fill=DISCRET, font=petit)
    art.text((bx + 8, by + ph - 28),
             f"la mesure atteint {100 * mes / ref:.0f} % de l'etalon d'independance",
             fill=ROUGE, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"series": len(series), "p90_hors_fenetre":
            bool(m["longueurs_publiees"]["p90"] > m["borne_haute_um"]), "sortie": str(sortie)}


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
    # ⚠⚠⚠ LES TROIS FAITS QUE LA FIGURE PORTE, et il faut les trois : la médiane s'accorde, la
    # queue est tronquée par la fenêtre, et cellule par cellule la lecture est indiscernable
    # d'un tirage. Le premier seul serait une bonne nouvelle et il est faux.
    v("la médiane lue s'accorde avec la médiane publiée", abs(m["accord"]["mediane"]) < 0.05,
      str(m["accord"]["mediane"]))
    v("... et la queue haute, non", abs(m["accord"]["p90"]) > 0.5, str(m["accord"]["p90"]))
    v("... parce que la fenêtre la tronque", m["la_fenetre_tronque_la_queue_publiee"],
      f"{m['borne_haute_um']} contre {m['longueurs_publiees']['p90']}")
    v("cellule par cellule, la lecture est indiscernable de son témoin",
      m["indiscernable_du_temoin"],
      f"{m['part_de_la_fenetre_qui_separe_du_temoin']} contre "
      f"{m['ecart_attendu_si_tirages_independants']}")
    # ⚠⚠ ET LA COMPARAISON DES DÉCILES NE TRANCHE PAS : c'est le piège que la figure existe pour
    # montrer, donc il doit être vérifié et pas seulement raconté.
    v("... alors que les déciles, eux, ne séparent rien",
      not m["les_distributions_se_separent"],
      f"{m['accord']} contre {m['accord_du_temoin']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les trois distributions sont dessinées", r["series"] == 3)
        v("... et le neuvième décile publié tombe hors de la fenêtre dessinée",
          r["p90_hors_fenetre"])
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
                   default=RACINE / "docs" / "images" / "75_la_longueur_locale_du_pas.png")
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
