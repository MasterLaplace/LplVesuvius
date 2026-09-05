#!/usr/bin/env python3
"""Le raccrochage gagne un pas et perd la marche — sauf s'il décide UNE fois pour toute la nappe.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le tableau des six marches est illisible en chiffres : cinq
d'entre elles montent et une descend, et c'est **laquelle descend** qui est le résultat. Tracées
ensemble contre la demi-épaisseur d'une feuille, elles disent d'un coup d'œil ce que quatre
lignes de nombres cachent — le raccrochage par point est le MEILLEUR au premier tour et le
PIRE au quatrième.

⭐⭐ Le panneau de la rugosité porte le mécanisme, et il est le même que celui que ce dépôt a
déjà payé sur l'encre : un « champ » estimé point par point n'était qu'une **constante** noyée
dans son propre bruit. Ici la constante est un décalage par tour, la rugosité du champ par
point monte de 5 à 25 µm, et celle du décalage global vaut zéro par construction.

⚠ Les six marches sont dessinées, y compris celles qui échouent, et la marche au hasard avec.
Une figure qui n'aurait montré que la gagnante serait un argument, pas une mesure.

Usage :
    uv run python src/figures/figure_derouler_en_raccrochant.py --verifier
    uv run python src/figures/figure_derouler_en_raccrochant.py \\
        --sortie docs/images/75_derouler_en_raccrochant.png
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
MESURE = RACINE / "docs" / "mesures" / "derouler_en_raccrochant.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
VERT = (60, 128, 84)
VIOLET = (118, 78, 140)
CADRE = (200, 200, 200)

# ⚠ L'ordre et les couleurs sont déclarés UNE fois : trois panneaux les partagent, et deux
# légendes qui divergeraient feraient lire une courbe sous le mauvais nom.
MARCHES = [
    ("marche_globale", "GLOBAL — un décalage par tour", AMBRE, 4),
    ("marche_aveugle", "aveugle — aucun raccrochage", BLEU, 2),
    ("marche_raccrochee", "par point", VERT, 2),
    ("marche_accordee", "par point, accordé aux voisins", VIOLET, 2),
    ("marche_fenetre_etroite", "par point, fenêtre deux fois plus étroite", DISCRET, 2),
    ("marche_hasard", "gabarit mélangé (témoin)", ROUGE, 2),
]


def prose(m: dict) -> list[str]:
    g = m["marche_globale"][-1]
    pp = m["marche_raccrochee"][-1]
    d = m["derive_par_tour_um"]
    return [
        f"depuis la spire {m['depuis']}, {m['cellules_au_depart']} cellules dans la boite, "
        f"pas nominal {m['ecart_lu_um']} um, un seul bit de supervision (le sens).",
        f"le raccrochage PAR POINT est le meilleur au tour 1 ({m['marche_raccrochee'][0]['erreur_um']:.0f} um "
        f"contre {m['marche_aveugle'][0]['erreur_um']:.0f} pour l'aveugle) et le pire au tour "
        f"{pp['tours'] if 'tours' in pp else len(m['marche_raccrochee'])} : "
        f"{pp['erreur_um']:.0f} um, {100 * pp['part_perdue']:.0f} % des cellules au-dela d'une demi-feuille.",
        f"ni l'accord des voisins ni une fenetre deux fois plus etroite ne le rattrapent : "
        f"derives {d['accorde']} et {d['etroite']} um par tour contre {d['raccroche']}.",
        f"UN SEUL decalage par tour, lui, converge : derive {d['globale']} um par tour, "
        f"{g['erreur_um']:.0f} um au dernier tour, p90 {g['erreur_p90_um']:.0f}, et "
        f"{100 * g['part_perdue']:.0f} % de cellules perdues.",
        f"le mecanisme est la rugosite : le champ par point ride la nappe de "
        f"{m['rugosite_um']['raccroche'][0]:.0f} a {m['rugosite_um']['raccroche'][-1]:.0f} um, "
        "un decalage unique ne la ride pas du tout.",
        f"et ce n'est PAS une longueur de pas corrigee : les decalages signes valent "
        f"{m['decalage_global_signe_um']} um, donc ils CHANGENT DE SIGNE. leur mediane "
        f"correspond a un pas de {m['longueur_equivalente_um']} um, a six micrometres de la "
        "longueur ajustee sur les cibles (108,4) que ce depot avait mesuree autrement.",
    ]


def _cadre(art, x0, y0, w, h):
    art.rectangle([x0, y0, x0 + w, y0 + h], outline=CADRE)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    marge = 40
    pw, ph = 400, 220
    ecart = 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 106 + ph + 56 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18),
             "Le raccrochage gagne un pas et perd la marche — sauf s'il decide UNE fois",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"depart spire {m['depuis']}, {m['cellules_au_depart']} cellules, "
             f"{m['tours_mesures']} tours, pas nominal {m['ecart_lu_um']} um",
             fill=DISCRET, font=moyen)

    tours = [e["tours"] for e in m["marche_raccrochee"]]
    demi = m["demi_epaisseur_um"]

    def axe_x(x0, k):
        return x0 + (k - tours[0]) / max(1, tours[-1] - tours[0]) * pw

    # ---------- A : les six marches ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · l'erreur a chaque tour, contre la demi-epaisseur d'une feuille",
             fill=TEXTE, font=moyen)
    _cadre(art, ax, ay, pw, ph)
    top = max(e["erreur_um"] for cle, _, _, _ in MARCHES for e in m[cle]) * 1.05
    yd = ay + ph - demi / top * ph
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    # ⚠ Le libellé va à DROITE : à gauche il tombait sur la courbe globale, et une légende
    # posée sur la courbe qu'elle commente est une légende qu'on lit de travers.
    art.text((ax + pw - 96, yd - 14), f"demi-feuille {demi:.0f}µ", fill=TEXTE, font=petit)
    # ⚠ Les extrêmes de l'axe sont écrits : une courbe sans échelle est un dessin.
    art.text((ax + 4, ay + 2), f"{top:.0f}µ", fill=DISCRET, font=petit)
    art.text((ax + 4, ay + ph - 14), "0µ", fill=DISCRET, font=petit)
    # ⚠ Le mot « tour » va SOUS les graduations, au milieu : à gauche il tombait sur le « 1 »,
    # à droite sur le dernier tour. Un axe dont le nom recouvre une graduation fait lire un
    # numéro de tour de travers.
    art.text((ax + pw / 2 - 12, ay + ph + 17), "tour", fill=DISCRET, font=petit)
    art.text((ax + pw - 150, ay + 2), "couleurs : voir le panneau D", fill=DISCRET, font=petit)
    for cle, _, coul, ep in MARCHES:
        pts = [(axe_x(ax, e["tours"]), ay + ph - e["erreur_um"] / top * ph) for e in m[cle]]
        for a_, b_ in zip(pts, pts[1:]):
            art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=ep)
        for x_, y_ in pts:
            art.ellipse([x_ - ep, y_ - ep, x_ + ep, y_ + ep], fill=coul)
    for k in tours:
        art.text((axe_x(ax, k) - 4, ay + ph + 3), str(k), fill=DISCRET, font=petit)

    # ---------- B : la legende, et la part perdue ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · part des cellules au-dela d'une demi-feuille",
             fill=TEXTE, font=moyen)
    _cadre(art, bx, by, pw, ph)
    for cle, nom, coul, ep in MARCHES:
        if cle not in ("marche_globale", "marche_aveugle", "marche_raccrochee"):
            continue
        pts = [(axe_x(bx, e["tours"]), by + ph - e["part_perdue"] * ph) for e in m[cle]]
        for a_, b_ in zip(pts, pts[1:]):
            art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=ep)
        for x_, y_ in pts:
            art.ellipse([x_ - ep, y_ - ep, x_ + ep, y_ + ep], fill=coul)
    for part, lab in ((0.0, "0 %"), (0.5, "50 %"), (1.0, "100 %")):
        y_ = by + ph - part * ph
        art.text((bx + pw - 34, y_ - 6), lab, fill=DISCRET, font=petit)
    for k in tours:
        art.text((axe_x(bx, k) - 4, by + ph + 3), str(k), fill=DISCRET, font=petit)

    # ---------- C : la rugosite ----------
    cx, cy = marge, 96 + ph + 106
    art.text((cx, cy - 20),
             "C · le mecanisme : de combien le raccrochage RIDE la nappe (um)",
             fill=TEXTE, font=moyen)
    _cadre(art, cx, cy, pw, ph)
    rug = [x for x in m["rugosite_um"]["raccroche"] if x is not None]
    haut = max(max(rug), 1.0) * 1.2
    larg = pw / (len(rug) * 2 + 1)
    for k, val in enumerate(rug):
        x_ = cx + larg * (2 * k + 1)
        h_ = val / haut * (ph - 30)
        art.rectangle([x_ - larg * 0.44, cy + ph - h_, x_ - 2, cy + ph], fill=VERT)
        art.rectangle([x_ + 2, cy + ph - 2, x_ + larg * 0.44, cy + ph], fill=AMBRE)
        art.text((x_ - 20, cy + ph - h_ - 15), f"{val:.0f}µ", fill=VERT, font=petit)
        art.text((x_ - 4, cy + ph + 3), str(tours[k]), fill=DISCRET, font=petit)
    art.text((cx + 8, cy + 8), "vert : un decalage par cellule", fill=VERT, font=petit)
    art.text((cx + 8, cy + 24), "ambre : un decalage par tour — zero par construction",
             fill=AMBRE, font=petit)

    # ---------- D : au dernier tour ----------
    dx, dy = marge + pw + ecart, 96 + ph + 106
    art.text((dx, dy - 20), "D · au dernier tour mesure : erreur, p90, et qui tient encore",
             fill=TEXTE, font=moyen)
    fin = m["feuille_tenue_a_la_fin"]
    cles = {"marche_globale": "globale", "marche_aveugle": "aveugle",
            "marche_raccrochee": "raccroche", "marche_accordee": "accorde",
            "marche_fenetre_etroite": "etroite", "marche_hasard": "hasard"}
    plus = max(fin[c]["p90_um"] for c in cles.values() if fin[c]) * 1.05
    haut2, lab = 22, 226
    for k, (cle, nom, coul, _) in enumerate(MARCHES):
        f = fin[cles[cle]]
        y_ = dy + k * (haut2 + 8)
        art.text((dx, y_ + 4), nom, fill=coul, font=petit)
        w_ = f["erreur_um"] / plus * (pw - lab)
        w9 = f["p90_um"] / plus * (pw - lab)
        art.rectangle([dx + lab, y_ + 2, dx + lab + w9, y_ + haut2 - 4],
                      outline=coul)
        art.rectangle([dx + lab, y_ + 2, dx + lab + w_, y_ + haut2 - 4], fill=coul)
        # ⚠ L'étiquette se pose après la barre p90 OU après le trait de la demi-feuille,
        # selon lequel est le plus à droite : sinon celle de la marche qui GAGNE — la plus
        # courte — s'écrit par-dessus le trait qu'elle est justement la seule à ne pas franchir.
        bord = max(dx + lab + w9, dx + lab + demi / plus * (pw - lab)) + 6
        art.text((bord, y_ + 4),
                 f"{f['erreur_um']:.0f}µ" + ("  tient" if f["sous_la_demi_feuille"] else ""),
                 fill=TEXTE if f["sous_la_demi_feuille"] else DISCRET, font=petit)
    yd2 = dx + lab + demi / plus * (pw - lab)
    art.line([yd2, dy - 4, yd2, dy + len(MARCHES) * (haut2 + 8)], fill=TEXTE, width=2)
    art.text((dx, dy + len(MARCHES) * (haut2 + 8) + 4),
             f"trait vertical : la demi-feuille, {demi:.0f}µ ; plein = mediane, contour = p90",
             fill=TEXTE, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"marches": len(MARCHES), "tours": len(tours),
            "tient": [c for c in cles.values() if fin[c] and fin[c]["sous_la_demi_feuille"]],
            "sortie": str(sortie)}


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
    # ⚠⚠⚠ LES TROIS FAITS QUE LA FIGURE PORTE. Le raccrochage par point gagne au premier tour,
    # il perd au dernier, et un décalage unique par tour est le seul qui descende. Sans les
    # trois, le dessin ne dit rien de plus qu'un tableau.
    v("le raccrochage par point gagne au premier tour",
      m["marche_raccrochee"][0]["erreur_um"] < m["marche_aveugle"][0]["erreur_um"],
      f"{m['marche_raccrochee'][0]['erreur_um']} contre {m['marche_aveugle'][0]['erreur_um']}")
    v("... et perd au dernier",
      m["marche_raccrochee"][-1]["erreur_um"] > m["marche_aveugle"][-1]["erreur_um"],
      f"{m['marche_raccrochee'][-1]['erreur_um']} contre {m['marche_aveugle'][-1]['erreur_um']}")
    v("le décalage global est le seul dont la dérive descende",
      [c for c, ok_ in m["la_derive_est_arretee"].items() if ok_] == ["globale"],
      str([c for c, ok_ in m["la_derive_est_arretee"].items() if ok_]))
    v("... et le seul qui tienne la feuille au dernier tour",
      m["tient_la_feuille_a_la_fin"] == ["globale"], str(m["tient_la_feuille_a_la_fin"]))
    # ⚠ Le mécanisme doit être visible : la rugosité du champ par point MONTE.
    rug = [x for x in m["rugosite_um"]["raccroche"] if x is not None]
    v("la rugosité du champ par point monte au fil des tours", rug[-1] > rug[0], str(rug))
    # ⚠⚠ Et le témoin qui rend la marche capable d'échouer : le gabarit mélangé doit être pire
    # que tout le reste au dernier tour.
    fins = {c: m["feuille_tenue_a_la_fin"][c]["erreur_um"]
            for c in m["feuille_tenue_a_la_fin"] if m["feuille_tenue_a_la_fin"][c]}
    v("le gabarit mélangé est le pire au dernier tour",
      max(fins, key=fins.get) == "hasard", str(fins))
    # ⚠⚠ LE FAIT QUI FERME L'AUTRE LECTURE : un décalage global toujours du même signe ne
    # serait qu'une longueur de pas corrigée, et ce dépôt a déjà mesuré ce que celle-là vaut
    # (54,1 µm sur des paires réservées). Il change de signe, donc il corrige tour par tour.
    v("le décalage global change de signe", m["le_global_change_de_signe"],
      str(m["decalage_global_signe_um"]))
    v("... et sa longueur équivalente tombe près de celle ajustée sur les cibles",
      abs(m["longueur_equivalente_um"] - 108.4) < 15.0, str(m["longueur_equivalente_um"]))
    v("toutes les marches ont le même nombre de tours",
      len({len(m[c]) for c, _, _, _ in MARCHES}) == 1,
      str({c: len(m[c]) for c, _, _, _ in MARCHES}))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les six marches sont dessinées", r["marches"] == 6)
        v("... et seule la globale est marquée comme tenant", r["tient"] == ["globale"],
          str(r["tient"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height * 0.9,
          f"{img.width}x{img.height}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_derouler_en_raccrochant.png")
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
