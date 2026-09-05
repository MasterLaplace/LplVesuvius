#!/usr/bin/env python3
"""Combien de tours un dérouleur aveugle survit-il — la dérive, et ce qu'elle coûte.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « La feuille est perdue au tour 2 » se lit comme un échec ;
la courbe dit autre chose et c'est elle qui compte. Le dérouleur reste **deux à trois fois
meilleur que l'immobilité** sur douze tours : il déroule, mais il **glisse** d'environ une
demi-feuille par tour. Deux faits opposés dans un seul nombre, et seule la courbe les sépare.

⭐⭐ La ligne de la demi-épaisseur est tracée, parce que c'est elle qui définit « perdu » : au
dessus, le dérouleur ne peut plus dire sur quelle feuille il est. Elle vient de l'écart mesuré
entre spires, pas d'un choix.

⚠ Le compte de cellules est dessiné à côté de l'erreur : une normale demande quatre voisins, donc
la grille perd un anneau par tour. Une erreur qui baisserait pendant que la grille fond ne serait
pas un progrès.

Usage :
    uv run python src/figures/figure_derouler_par_le_pas_normal.py --verifier
    uv run python src/figures/figure_derouler_par_le_pas_normal.py \\
        --sortie docs/images/75_derouler_par_le_pas_normal.png
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
MESURE = RACINE / "docs" / "mesures" / "derouler_par_le_pas_normal.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
GRIS = (170, 170, 170)
VERT = (52, 122, 72)
CADRE = (200, 200, 200)


def derive_par_tour(m: dict) -> float:
    """La pente de l'erreur, en micromètres par tour — ajustée, pas devinée.

    ⚠ Moindres carrés sur toute la marche plutôt que « dernier moins premier sur le nombre de
    tours » : la marche est irrégulière — les spires publiées le sont — et deux points pris aux
    extrémités feraient dépendre la pente de deux tours particuliers.
    """
    xs = [e["tours"] for e in m["marche"]]
    ys = [e["erreur_um"] for e in m["marche"]]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den) if den else 0.0


def prose(m: dict) -> list[str]:
    d = derive_par_tour(m)
    fin = m["marche"][-1]
    return [
        f"deroulement AVEUGLE depuis la spire {m['depuis']} : un pas d'un ecart inter-feuilles "
        f"le long de la normale, la grille conservee, {m['bits_de_supervision']} bit de "
        "supervision (le sens, fixe au premier pas).",
        f"la feuille est perdue au tour {m['tours_avant_de_perdre_la_feuille']}, "
        f"c'est-a-dire des que l'erreur depasse la demi-epaisseur "
        f"({m['demi_epaisseur_um']:.0f} um) et qu'on ne sait plus sur laquelle on est.",
        f"mais il DEROULE : a {fin['tours']} tours il est a {fin['erreur_um']:.0f} um quand ne "
        f"pas bouger en met {fin['temoin_sur_place_um']:.0f} — deux a trois fois mieux, tout du "
        "long.",
        f"la derive vaut {d:.0f} um par tour, soit environ {d / m['ecart_lu_um'] * 100:.0f} % "
        "d'une feuille : c'est ce qu'un recalage sur la matiere doit tuer a chaque pas.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    mm = m["marche"]
    marge = 44
    gw, gh = 620, 270
    x0, y0 = marge + 48, 106
    lignes = couper(prose(m), 108)
    L = x0 + gw + marge + 40
    H = y0 + gh + 150 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Combien de tours un derouleur aveugle survit-il",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"erreur mediane a la spire de meme rang, {mm[0]['juges']} points juges par tour, "
             f"volume {m['volume']}", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             "ambre : le derouleur — gris : ne pas bouger — rouge : la demi-epaisseur, "
             "au dela de laquelle la feuille est perdue", fill=DISCRET, font=moyen)

    haut = max(max(e["temoin_sur_place_um"], e["erreur_um"]) for e in mm) * 1.1
    art.rectangle([x0, y0, x0 + gw, y0 + gh], outline=CADRE)
    for k in (0, 1, 2):
        val = haut * k / 2.0
        y = y0 + gh - val / haut * gh
        art.text((x0 - 44, y - 6), f"{val:.0f}µ", fill=DISCRET, font=petit)

    def pt(e, cle):
        x = x0 + (e["tours"] - mm[0]["tours"]) / max(1, len(mm) - 1) * gw
        return x, y0 + gh - e[cle] / haut * gh

    yd = y0 + gh - m["demi_epaisseur_um"] / haut * gh
    art.line([x0, yd, x0 + gw, yd], fill=ROUGE, width=2)
    etiq = f"demi-epaisseur : {m['demi_epaisseur_um']:.0f} um"
    art.rectangle([x0 + 4, yd - 16, x0 + 4 + 7 * len(etiq), yd - 3], fill=FOND)
    art.text((x0 + 4, yd - 15), etiq, fill=ROUGE, font=petit)

    for cle, coul in (("temoin_sur_place_um", GRIS), ("erreur_um", AMBRE)):
        pts = [pt(e, cle) for e in mm]
        for a_, b_ in zip(pts, pts[1:]):
            art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=3)
        for (x, y) in pts:
            art.ellipse([x - 3, y - 3, x + 3, y + 3], fill=coul)
    perdu = m["tours_avant_de_perdre_la_feuille"]
    if perdu:
        e = next(e for e in mm if e["tours"] == perdu)
        x, y = pt(e, "erreur_um")
        art.line([x, y0, x, y0 + gh], fill=ROUGE)
        art.text((x + 4, y0 + 4), f"perdue au tour {perdu}", fill=ROUGE, font=petit)
    for e in mm:
        x, _ = pt(e, "erreur_um")
        art.text((x - 4, y0 + gh + 5), f"{e['tours']}", fill=DISCRET, font=petit)
    art.text((x0, y0 + gh + 22), "tours de deroulement", fill=DISCRET, font=petit)

    # --- les cellules survivantes ---
    ys = y0 + gh + 48
    art.text((x0, ys), "cellules encore jugeables, tour par tour", fill=TEXTE, font=moyen)
    hmax = max(e["cellules"] for e in mm)
    for k, e in enumerate(mm):
        h = e["cellules"] / hmax * 40
        x = x0 + k * gw / len(mm)
        art.rectangle([x, ys + 62 - h, x + gw / len(mm) - 4, ys + 62], fill=VERT)
    art.text((x0, ys + 66), f"de {mm[0]['cellules']} a {mm[-1]['cellules']} — "
             "une normale demande quatre voisins, donc un anneau part par tour",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"tours": len(mm),
            "tours_sous_le_temoin": sum(1 for e in mm
                                        if e["erreur_um"] < e["temoin_sur_place_um"]),
            "derive_um_par_tour": round(derive_par_tour(m), 1), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ La pente est ajustée : sur une marche parfaitement linéaire elle doit rendre la pente,
    # et sur une marche plate zéro. Sans les deux, « la dérive vaut tant » serait un mot.
    droite = {"marche": [{"tours": k, "erreur_um": 10.0 * k} for k in range(1, 6)]}
    v("la dérive d'une marche linéaire est sa pente",
      abs(derive_par_tour(droite) - 10.0) < 1e-9, str(derive_par_tour(droite)))
    plate = {"marche": [{"tours": k, "erreur_um": 7.0} for k in range(1, 6)]}
    v("... et celle d'une marche plate est nulle", abs(derive_par_tour(plate)) < 1e-9)

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LES DEUX FAITS OPPOSÉS QUE LA FIGURE PORTE, et ils doivent être vrais tous les deux :
    # la feuille EST perdue tôt, ET le dérouleur bat l'immobilité tout du long. Ne garder que
    # l'un des deux serait raconter un échec ou une victoire au lieu de la mesure.
    v("la feuille est bien perdue, et tôt",
      m["tours_avant_de_perdre_la_feuille"] is not None
      and m["tours_avant_de_perdre_la_feuille"] <= 4,
      str(m["tours_avant_de_perdre_la_feuille"]))
    v("... et pourtant le dérouleur bat l'immobilité à CHAQUE tour",
      all(e["erreur_um"] < e["temoin_sur_place_um"] for e in m["marche"]),
      f"{sum(1 for e in m['marche'] if e['erreur_um'] < e['temoin_sur_place_um'])} sur "
      f"{len(m['marche'])}")
    v("le seuil de perte est la demi-épaisseur, pas un nombre écrit",
      abs(m["demi_epaisseur_um"] * 2 - m["ecart_lu_um"]) < 1e-6,
      f"{m['demi_epaisseur_um']} pour {m['ecart_lu_um']}")
    # ⚠ La grille fond : le dire empêche de lire une erreur basse comme un progrès.
    v("la grille fond au fil des tours",
      m["marche"][-1]["cellules"] < m["marche"][0]["cellules"],
      f"{m['marche'][0]['cellules']} puis {m['marche'][-1]['cellules']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les tours sont tracés", r["tours"] == len(m["marche"]), str(r["tours"]))
        v("... et le compte de tours sous le témoin est celui de la mesure",
          r["tours_sous_le_temoin"] == len(m["marche"]))
        v("la dérive publiée est positive, donc il y a bien dérive",
          r["derive_um_par_tour"] > 0, f"{r['derive_um_par_tour']} µm/tour")
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png").convert("L")
        gris = img.getextrema()
        v("l'image a du relief", gris[0] < 90 and gris[1] > 240, str(gris))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_derouler_par_le_pas_normal.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['tours']} tours, dérive "
          f"{r['derive_um_par_tour']} µm/tour)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
