#!/usr/bin/env python3
"""Les écarts entre segments publiés : la bande des raccordables est VIDE.

⚠⚠ **Ce que cette figure établit, et que le tableau de `44` ne montre pas.** Le tableau
donne trois comptes — 0 / 2 / 45 — et un compte de zéro se lit comme « on n'a pas
trouvé », c'est-à-dire comme un résultat faible. La distribution, elle, montre autre
chose : il n'y a pas *un peu* moins de candidats que prévu, il y a un **trou d'un facteur
deux** entre le seuil de même-feuille et la paire la plus proche du rouleau.

⭐ Chaque point est une paire de segments publiés dont les boîtes se recouvrent, placée
sur son écart médian point-à-point. L'axe est **logarithmique** parce que la question
couvre deux ordres de grandeur : quelques µm pour deux patchs d'une même nappe, quelques
centaines pour deux nappes distinctes.

⚠ Les paires **hors de portée** sont dessinées à droite, dans leur propre colonne, et pas
omises : aucun de leurs points n'approche l'autre à moins de 432 µm, donc ce sont des
paires éloignées — les taire ferait un graphique dont les points ne totalisent pas les
paires. C'est la correction qui a fait passer la dernière bande de 49 à 45.

⚠ La ligne des 113 µm est l'espacement entre nappes voisines **mesuré sur ce rouleau**
(`44` §4), pas une valeur de catalogue : c'est elle qui explique pourquoi les deux seules
paires proches ne sont pas des candidates mais des voisines.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    cd experiments && uv run python ../analysis/src/figure_segments.py \\
        --entree ../docs/segments_PHerc1447.json \\
        --sortie ../docs/images/44_ecarts_segments.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from carte_segments import MEME_FEUILLE_UM, VOISINES_UM  # noqa: E402

LARGEUR, HAUTEUR = 1120, 440
X0, LARG = 130, 760          # origine et largeur de l'axe des écarts
Y0, HAUT = 110, 170          # haut du champ et sa hauteur
# ⚠ Les bornes couvrent la PLAGE MESUREE (79 a 7039 µm) et pas une plage choisie
# d'avance : la premiere version s'arretait a 1200 µm et ecretait 30 des 47 paires en une
# seule colonne, qui debordait du cadre par le haut. Un axe qui ecrete est un axe qui
# fabrique un amas la ou il n'y en a pas.
UM_MIN, UM_MAX = 20.0, 9000.0
X_HORS = X0 + LARG + 96      # colonne des paires hors de portée
ESPACEMENT_NAPPES_UM = 113.0  # mesuré au §4 de `44`

FOND, TRAIT, TEXTE = (255, 255, 255), (120, 120, 120), (25, 25, 25)
CANDIDAT, VOISINE, LOIN = (200, 40, 40), (215, 130, 20), (70, 110, 170)


def x_de(um: float) -> int:
    """Position d'un écart sur l'axe logarithmique, écrêtée aux bornes."""
    u = min(max(um, UM_MIN), UM_MAX)
    return X0 + int(math.log10(u / UM_MIN) / math.log10(UM_MAX / UM_MIN) * LARG)


def bandes(paires: list[dict]) -> dict[str, list]:
    """Range les paires dans les quatre catégories que la prose publie."""
    mes = sorted((p for p in paires if p.get("ecart_um") is not None),
                 key=lambda p: p["ecart_um"])
    return {
        "meme": [p for p in mes if p["ecart_um"] < MEME_FEUILLE_UM],
        "voisine": [p for p in mes if MEME_FEUILLE_UM <= p["ecart_um"] < VOISINES_UM],
        "loin": [p for p in mes if p["ecart_um"] >= VOISINES_UM],
        "hors": [p for p in paires if p.get("raison") == "hors_portee"],
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ Les sondes sont derivees des bornes PAR RATIO GEOMETRIQUE, donc elles tiennent
    # dans le domaine quelle que soit son etendue. Une version anterieure testait la decade
    # `MIN`, `MIN*10`, `MIN*100` -- correct sur un axe qui couvre plus de deux decades,
    # faux sinon : la troisieme sonde sortait du domaine et le temoin mesurait un ECRETAGE
    # en croyant mesurer une echelle. C'est la deuxieme fois que ce piege se paie.
    k = (UM_MAX / UM_MIN) ** 0.5
    d1, d2, d3 = UM_MIN, UM_MIN * k, UM_MAX
    v("l'axe est croissant", x_de(d1) < x_de(d2) < x_de(d3))
    v("... et logarithmique : un même rapport fait toujours la même largeur",
      abs((x_de(d2) - x_de(d1)) - (x_de(d3) - x_de(d2))) <= 1,
      f"{x_de(d2) - x_de(d1)} contre {x_de(d3) - x_de(d2)}")
    # ⚠ Un ecart hors bornes doit etre ECRETE, pas sortir du cadre : un point dessine a
    # x negatif disparait en silence et le graphique compte alors moins de paires que le
    # tableau, ce qui est exactement le defaut que cette figure existe pour corriger.
    v("un écart sous la borne reste dans le cadre", X0 <= x_de(0.01) <= X0 + LARG)
    v("... et un écart au-dessus aussi", X0 <= x_de(99999.0) <= X0 + LARG)
    v("la colonne « hors de portée » est hors de l'axe", X_HORS > X0 + LARG)

    faux = [{"ecart_um": 3.0}, {"ecart_um": 79.0}, {"ecart_um": 500.0},
            {"raison": "hors_portee"}, {"raison": "illisible"}]
    b = bandes(faux)
    v("chaque bande reçoit ce qui lui revient",
      (len(b["meme"]), len(b["voisine"]), len(b["loin"]), len(b["hors"])) == (1, 1, 1, 1),
      str({k: len(x) for k, x in b.items()}))
    # ⭐⭐ La sonde qui compte : les quatre bandes doivent TOTALISER les paires jugeables.
    # Sans elle, une categorie oubliee -- « hors_portee », precisement -- disparait du
    # graphique sans que rien ne le signale, et c'est arrive dans le tableau publie.
    jugeables = [p for p in faux if p.get("ecart_um") is not None
                 or p.get("raison") == "hors_portee"]
    v("... et leur somme est le nombre de paires jugeables",
      sum(len(x) for x in b.values()) == len(jugeables),
      f"{sum(len(x) for x in b.values())} contre {len(jugeables)}")
    v("une paire illisible n'est comptée nulle part",
      not any(any(p.get("raison") == "illisible" for p in x) for x in b.values()))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--entree", type=Path, default=racine / "docs/segments_PHerc1447.json")
    ap.add_argument("--sortie", type=Path,
                    default=racine / "docs/images/44_ecarts_segments.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer d'abord carte_segments.py --json",
              file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    b = bandes(d["paires"])
    n_seg = len(d["segments"])

    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    img = Image.new("RGB", (LARGEUR, HAUTEUR), FOND)
    g = ImageDraw.Draw(img)

    g.text((X0 - 24, 26), f"PHerc1447 — écart entre les {n_seg} segments publiés, "
                          f"paire par paire", font=f_t, fill=TEXTE)
    g.text((X0 - 24, 50), "un point = une paire dont les boîtes se recouvrent ; "
                          "écart médian point-à-point", font=f_p, fill=(90, 90, 90))

    # La bande des raccordables, peinte AVANT les points : c'est le vide qu'elle montre.
    g.rectangle([X0, Y0, x_de(MEME_FEUILLE_UM), Y0 + HAUT], fill=(252, 233, 233))
    g.text((X0 + 6, Y0 + 8), "raccordables", font=f_p, fill=CANDIDAT)
    g.text((X0 + 6, Y0 + 24), "(vide)", font=f_n, fill=CANDIDAT)

    for um in (100, 1000, 5000):
        x = x_de(um)
        g.line([x, Y0, x, Y0 + HAUT], fill=(228, 228, 228))
        g.text((x - 12, Y0 + HAUT + 8), f"{um}", font=f_p, fill=(110, 110, 110))
    g.text((X0 + LARG // 2 - 60, Y0 + HAUT + 30), "écart médian (µm, échelle log)",
           font=f_n, fill=TEXTE)

    # ⚠ Les trois etiquettes sont ETAGEES : a la meme hauteur elles se recouvraient et
    # « nappes voisines mesurees 113 µm » mangeait « 250 µm ».
    for i, (um, nom, coul) in enumerate((
            (MEME_FEUILLE_UM, f"seuil même feuille {MEME_FEUILLE_UM:.0f} µm", CANDIDAT),
            (ESPACEMENT_NAPPES_UM,
             f"nappes voisines mesurées {ESPACEMENT_NAPPES_UM:.0f} µm", VOISINE),
            (VOISINES_UM, f"{VOISINES_UM:.0f} µm", TRAIT))):
        x = x_de(um)
        for y in range(Y0, Y0 + HAUT, 8):
            g.line([x, y, x, y + 4], fill=coul)
        g.text((x + 5, Y0 - 40 + i * 14), nom, font=f_p, fill=coul)

    # Les points, empilés verticalement quand plusieurs paires tombent au même endroit.
    occupe: dict[int, int] = {}

    def poser(x: int, coul, r: int = 5):
        k = x // 8
        n = occupe.get(k, 0)
        occupe[k] = n + 1
        y = Y0 + HAUT - 26 - n * 15
        g.ellipse([x - r, y - r, x + r, y + r], fill=coul, outline=(255, 255, 255))
        return y

    for p in b["loin"]:
        poser(x_de(p["ecart_um"]), LOIN)
    # ⚠ 79 et 89 µm tombent a une dizaine de pixels l'un de l'autre : deux etiquettes se
    # chevauchaient et se lisaient « 7989 µm ». Une SEULE etiquette nomme le groupe, ce qui
    # est aussi la facon dont la prose l'ecrit.
    ys = [poser(x_de(p["ecart_um"]), VOISINE, 6) for p in b["voisine"]]
    if b["voisine"]:
        xs = [x_de(p["ecart_um"]) for p in b["voisine"]]
        libelle = " et ".join(f"{p['ecart_um']:.0f}" for p in b["voisine"]) + " µm"
        g.text((min(xs) - 18, min(ys) - 26), libelle, font=f_p, fill=VOISINE)
    for p in b["meme"]:
        poser(x_de(p["ecart_um"]), CANDIDAT, 6)

    for i, _ in enumerate(b["hors"]):
        y = Y0 + HAUT - 26 - i * 15
        g.ellipse([X_HORS - 5, y - 5, X_HORS + 5, y + 5], fill=(170, 180, 195),
                  outline=(255, 255, 255))
    g.text((X_HORS - 46, Y0 + HAUT + 8), "hors de portée", font=f_p, fill=(110, 110, 110))
    g.text((X_HORS - 46, Y0 + HAUT + 22), "(> 432 µm)", font=f_p, fill=(110, 110, 110))

    plus_proche = min((p["ecart_um"] for p in b["voisine"] + b["loin"] + b["meme"]),
                      default=0.0)
    lignes = [
        f"{len(b['meme'])} paire sous {MEME_FEUILLE_UM:.0f} µm — la bande des "
        f"raccordables est vide",
        f"{len(b['voisine'])} paires entre {MEME_FEUILLE_UM:.0f} et {VOISINES_UM:.0f} µm "
        f"— des nappes VOISINES, à ne surtout pas fusionner",
        f"{len(b['loin'])} mesurées et {len(b['hors'])} hors de portée au-delà",
        f"la paire la plus proche du rouleau est encore à {plus_proche:.0f} µm, "
        f"soit deux fois le seuil",
    ]
    for i, t in enumerate(lignes):
        y = Y0 + HAUT + 62 + i * 19
        coul = CANDIDAT if i in (0, 3) else TEXTE
        g.text((X0 - 24, y), ("⚠ " if i == 0 else "  ") + t, font=f_n, fill=coul)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{HAUTEUR})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
