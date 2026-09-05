#!/usr/bin/env python3
"""La rampe de la chaîne contre l'échelle du référent — deux objets de nature différente.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat d'`A5 bis` est un argument de **forme**, et une
forme se lit mal en pourcentages : « un biais explique au plus 0,5 % » demande de croire sur
parole qu'un biais est constant. Tracer les dix maillons et poser, autour du **premier**, la
bande de ce que le référent vaut, montre d'un coup que la rampe en sort tout de suite et n'y
revient jamais.

⭐⭐ **La bande est ancrée sur le PREMIER maillon, pas sur zéro**, et c'est tout l'argument :
un biais de référent déplace la courbe entière, donc il déplace l'origine — il ne peut pas
changer la **pente**. Une bande centrée sur zéro raconterait autre chose.

⚠ L'axe des abscisses est le **parcouru en micromètres** et non l'indice de maillon : les
maillons ne sont pas équidistants (96, 288, 480, 768…), et les espacer également transformerait
une rampe en autre chose.

⚠ Les nombres sont LUS dans `docs/mesures/la_derive_nest_pas_le_referent.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_la_derive_et_le_referent.py --verifier
    uv run python src/figures/figure_la_derive_et_le_referent.py \\
        --sortie docs/images/75_la_derive_et_le_referent.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BANDE = (214, 226, 214)
VERT = (52, 122, 72)
GRILLE = (226, 226, 226)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    return [
        f"la chaine part a {m['borne_du_biais_um']:.1f} um de la surface publiee et finit a "
        f"{m['ecart_final_um']:.1f} um : c'est une RAMPE.",
        f"un biais de referent decale toute la courbe, donc il explique au plus "
        f"{m['part_expliquable_par_un_biais'] * 100:.1f} % — il ne change pas la pente.",
        f"avec la dispersion retiree en quadrature ({m['referent_um']:.1f} um), le referent "
        f"entier en explique au plus {m['part_expliquable_par_le_referent'] * 100:.1f} %.",
        "un referent mal place produit un decalage ; la chaine produit une rampe. Ce ne sont "
        "pas les memes objets.",
    ]


def bande_du_referent(premier_ecart: float, referent_um: float) -> tuple[float, float]:
    """Les bornes de la bande, ANCRÉES sur le premier maillon.

    ⚠⚠ C'est tout l'argument, et c'est pourquoi une seule fonction la calcule : un biais de
    référent déplace la courbe entière, donc il déplace l'**origine** — il ne peut pas changer
    la pente. Une bande centrée sur zéro raconterait un autre argument, et le dessin et le
    compte doivent la lire **au même endroit**, sinon la figure pourrait la peindre ailleurs
    que là où elle est vérifiée.
    """
    return (max(premier_ecart - referent_um, 0.0), premier_ecart + referent_um)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    xs = m["parcouru_um"]
    ys = [abs(e) for e in m["ecart_um"]]
    if len(xs) < 2:
        raise SystemExit("au moins deux maillons sont requis")

    marge, larg, haut = 62, 880, 300
    lignes = prose(m)
    L = marge + larg + 130
    H = 96 + haut + 64 + len(lignes) * 19 + 24
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge - 36, 18), "La derive de la chaine contre l'echelle du referent",
             fill=TEXTE, font=gros)
    art.text((marge - 36, 42),
             f"{len(xs)} maillons — l'ecart est mesure le long des normales de la surface "
             "publiee", fill=DISCRET, font=moyen)

    y0 = 92
    xmax, ymax = max(xs), max(ys) * 1.12
    def px(x): return marge + x / xmax * larg
    def py(y): return y0 + haut - y / ymax * haut

    for k in range(0, int(ymax) + 1, 20):
        art.line([marge, py(k), marge + larg, py(k)], fill=GRILLE)
        art.text((marge - 34, py(k) - 7), f"{k:3d}", fill=DISCRET, font=petit)
    art.text((marge - 40, y0 - 18), "ecart |um|", fill=DISCRET, font=petit)

    # ⚠⚠ LA BANDE EST ANCRÉE SUR LE PREMIER MAILLON. Un biais déplace la courbe entière, donc
    # il déplace l'ORIGINE ; une bande centrée sur zéro raconterait un autre argument.
    b = m["referent_um"]
    bas_b, haut_b = bande_du_referent(ys[0], b)
    art.rectangle([marge, py(haut_b), marge + larg, py(bas_b)], fill=BANDE)
    art.text((marge + 8, py(haut_b) - 15),
             f"ce que le referent vaut : ±{b:.1f} um autour du PREMIER maillon",
             fill=VERT, font=petit)

    art.line([marge, y0 + haut, marge + larg, y0 + haut], fill=(150, 150, 150))
    for k in range(0, int(xmax) + 1, 1000):
        art.line([px(k), y0 + haut, px(k), y0 + haut + 5], fill=(150, 150, 150))
        art.text((px(k) - 10, y0 + haut + 8), f"{k // 1000}", fill=DISCRET, font=petit)
    art.text((marge + larg // 2 - 40, y0 + haut + 26), "parcouru (mm)", fill=DISCRET, font=petit)

    for (xa, ya), (xb, yb) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        art.line([px(xa), py(ya), px(xb), py(yb)], fill=AMBRE, width=3)
    for x, y in zip(xs, ys):
        art.ellipse([px(x) - 4, py(y) - 4, px(x) + 4, py(y) + 4], fill=AMBRE)
    art.text((px(xs[-1]) - 60, py(ys[-1]) - 24), f"{ys[-1]:.1f} um", fill=AMBRE, font=moyen)
    art.text((px(xs[0]) + 8, py(ys[0]) - 4), f"{ys[0]:.1f} um", fill=AMBRE, font=petit)

    bas = H - len(lignes) * 19 - 14
    for j, l in enumerate(lignes):
        art.text((marge - 36, bas + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠ Rendu et non affirmé : combien de maillons SORTENT de la bande du référent. Zéro
    # rendrait la figure muette, et il faut le savoir plutôt que le regarder.
    dehors = [not (bas_b <= y <= haut_b) for y in ys]
    hors = sum(dehors)
    # ⚠⚠ Ce qui compte n'est pas COMBIEN de maillons sortent — un compte se règle — mais que
    # la sortie soit DÉFINITIVE : une fois dehors, la rampe n'y revient jamais. Un bruit autour
    # du référent, lui, entrerait et sortirait.
    premier = next((i for i, d in enumerate(dehors) if d), None)
    return {"maillons": len(xs), "hors_de_la_bande": hors,
            "sortie_definitive": premier is not None and all(dehors[premier:]),
            "premier_hors": premier, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    faux = {"parcouru_um": [96.0, 288.0, 480.0, 768.0, 1152.0, 1920.0, 2880.0, 3840.0,
                            4800.0, 5760.0],
            "ecart_um": [-0.35, -1.49, -3.84, -12.24, -20.54, -28.06, -34.82, -44.93,
                         -56.78, -69.17],
            "ecart_final_um": 69.17, "referent_um": 19.5, "borne_du_biais_um": 0.35,
            "part_expliquable_par_un_biais": 0.005,
            "part_expliquable_par_le_referent": 0.045}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle donne le DEBUT et la fin de la rampe",
      any("0.3 um" in x and "69.2 um" in x for x in lignes), str(lignes[0]))
    # ⚠⚠ L'argument est que le biais ne change pas la PENTE. La figure doit le dire, sinon le
    # « 0,5 % » se lit comme un chiffre sorti d'un ajustement.
    v("... et elle dit qu'un biais ne change pas la pente",
      any("pente" in x for x in lignes), str(lignes[1]))
    v("... et que ce ne sont pas les mêmes objets",
      any("memes objets" in x for x in lignes), str(lignes[-1]))

    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    r = dessiner(faux, d / "x.png")
    # ⭐⭐ LE CONTRÔLE QUI COMPTE, et ce n'est PAS un compte. Ma première version assertait
    # « ≥ 7 maillons sur 10 » — un nombre que je n'avais pas calculé, et la géométrie en donne
    # 6 : le seuil choisi pour que le résultat du jour passe, pris dans l'autre sens. Ce qui
    # est structurel est que la sortie soit DÉFINITIVE — un bruit autour du référent entrerait
    # et ressortirait, une rampe non.
    v("la rampe sort de la bande du referent et n'y revient jamais",
      r["sortie_definitive"] and r["hors_de_la_bande"] >= 1,
      f"sortie au maillon {r['premier_hors']}, {r['hors_de_la_bande']} dehors sur "
      f"{r['maillons']}")
    # ⚠ Et le contrôle inverse : une série PLATE reste dedans, donc « sortir » n'est pas une
    # propriété du dessin.
    plat = {**faux, "ecart_um": [-0.35] * 10}
    v("... alors qu'une serie plate y reste entierement",
      dessiner(plat, d / "y.png")["hors_de_la_bande"] == 0)
    # ⚠⚠⚠ L'ANCRAGE DE LA BANDE, testé directement : une sonde qui la centrait sur zéro
    # passait, parce que le compte la relisait ailleurs que le dessin. Une seule fonction la
    # calcule désormais, et ce contrôle porte sur elle.
    v("la bande est ancree sur le PREMIER maillon, pas sur zero",
      bande_du_referent(0.35, 19.5) == (0.0, 19.85)
      and bande_du_referent(30.0, 19.5) == (10.5, 49.5),
      str(bande_du_referent(30.0, 19.5)))

    # ⚠ Et le contrôle qui distingue une RAMPE d'un bruit : une série qui sort puis rentre
    # n'est pas une sortie définitive. Sans lui, « sortie_definitive » serait satisfait par
    # n'importe quoi qui dépasse une fois.
    bruit = {**faux, "ecart_um": [-0.35, -40.0, -0.4, -41.0, -0.5, -42.0, -0.6, -43.0,
                                  -0.7, -44.0]}
    v("... et une serie qui sort PUIS RENTRE n'est pas une sortie definitive",
      not dessiner(bruit, d / "b.png")["sortie_definitive"])
    v("une serie d'un seul maillon est REFUSEE",
      _leve(lambda: dessiner({**faux, "parcouru_um": [96.0], "ecart_um": [-0.35]},
                             d / "z.png")))
    shutil.rmtree(d, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_derive_nest_pas_le_referent.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_la_derive_et_le_referent.png")
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
