#!/usr/bin/env python3
"""La campagne appariée des critères de graine, un rouleau par ligne.

⚠⚠ **Ce que la figure montre et que le tableau cache.** Le tableau publie « planéité 11,
voisinage 2, p = 0,0225 » — trois nombres qui se lisent comme un verdict net. La figure
montre deux choses qu'aucun de ces nombres ne porte :

1. ⚠ **Les deux « défaites » se jouent à 0,01 et 0,09 cm²** — `PHerc0800` 16,88 contre
   16,89, `PHerc0268` 16,90 contre 16,99. Ce sont des égalités que le test des signes
   compte comme des pertes. C'est le sens CONSERVATEUR de l'erreur, et il faut pouvoir le
   voir : un lecteur qui croirait à deux échecs francs lirait mal ce qui est mesuré.
2. ⚠⚠ **Cinq traces de planéité sur treize butent sur le PLAFOND de générations**
   (19,82–19,84 cm²). Sur celles-là, « la planéité va plus loin » veut dire « la planéité
   va jusqu'au budget » — la distance réellement atteignable n'est pas mesurée, elle est
   tronquée. Une barre qui s'arrête toutes au même endroit est un plafond, pas un résultat.

⭐ Chaque ligne est une paire APPARIÉE : même rouleau, même volume, mêmes paramètres, seule
la graine change. C'est ce qui autorise à lire l'écart comme un effet du critère et non de
la difficulté du rouleau.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    cd inference && uv run python ../analysis/src/figure_graines.py \\
        --entree ../docs/table_graines.json --sortie ../docs/images/25_campagne_graines.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, MARGE_H = 1120, 84
X0, LARG = 190, 720          # origine et largeur de l'axe des aires
LIGNE = 26                   # hauteur d'une ligne de rouleau
AIRE_MAX = 21.0              # borne de l'axe : le plafond mesuré est a 19,84

FOND, TEXTE, TRAIT = (255, 255, 255), (25, 25, 25), (150, 150, 150)
PLANARITE, VOISINAGE = (40, 110, 60), (185, 95, 25)
SERRE, PLAFOND = (200, 40, 40), (120, 120, 180)

# ⚠ Un ecart sous ce seuil n'est pas une victoire, c'est une egalite que le test des
# signes tranche quand meme. Nomme ici parce que la figure ET la prose le citent.
ECART_SERRE_CM2 = 0.2
# ⚠ Le plafond n'est pas une constante du monde : c'est le budget de generations de CETTE
# campagne, lu comme « toutes les traces qui s'arretent a la meme aire ». On le DERIVE.
TOLERANCE_PLAFOND_CM2 = 0.05


def plafond_de(aires: list[float]) -> float | None:
    """L'aire à laquelle plusieurs traces s'arrêtent ensemble, ou rien.

    ⚠ Dérivé, jamais écrit en dur : le plafond est une propriété du budget de
    générations, donc il bouge si la campagne est rejouée avec un autre budget. Une
    constante ici deviendrait fausse en silence, et la figure annoncerait un plafond là
    où il n'y en a plus.
    """
    if not aires:
        return None
    haut = max(aires)
    groupe = [a for a in aires if haut - a <= TOLERANCE_PLAFOND_CM2]
    return haut if len(groupe) >= 3 else None


def x_de(aire: float) -> int:
    return X0 + int(min(max(aire, 0.0), AIRE_MAX) / AIRE_MAX * LARG)


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("l'axe est croissant et ancré à zéro", x_de(0) == X0 and x_de(10) < x_de(20))
    v("une aire au-delà de la borne reste dans le cadre", X0 <= x_de(999) <= X0 + LARG)
    v("... et une aire négative aussi", X0 <= x_de(-5) <= X0 + LARG)

    # ⭐ Le plafond est DERIVE : trois traces ou plus qui s'arretent ensemble en font un.
    v("trois aires groupées au sommet font un plafond",
      plafond_de([19.82, 19.83, 19.82, 11.4, 3.0]) == 19.83)
    # ⚠⚠ La sonde qui compte : deux traces au sommet ne suffisent PAS. Sans ce refus,
    # n'importe quelle campagne aurait un « plafond » — celui de son maximum — et la
    # figure annoncerait une troncature partout, y compris la ou il n'y en a aucune.
    v("... mais deux, non — sinon tout maximum serait un plafond",
      plafond_de([19.82, 19.83, 11.4, 3.0]) is None)
    v("des aires étalées n'ont pas de plafond",
      plafond_de([1.0, 5.0, 9.0, 14.0, 19.0]) is None)
    v("une campagne vide n'a pas de plafond", plafond_de([]) is None)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--entree", type=Path, default=racine / "docs/table_graines.json")
    ap.add_argument("--sortie", type=Path,
                    default=racine / "docs/images/25_campagne_graines.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer d'abord table_graines.py --out",
              file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    lignes = sorted(d["lignes"], key=lambda l: -l["planarite"]["aire_cm2"])
    plafond = plafond_de([l["planarite"]["aire_cm2"] for l in lignes])
    signes = d["signes_aire"]

    hauteur = MARGE_H + len(lignes) * LIGNE + 150
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = ImageDraw.Draw(img)
    g.text((40, 26), f"Campagne appariée des critères de graine — "
                     f"{d['rouleaux']} rouleaux du prix", font=f_t, fill=TEXTE)
    g.text((40, 50), "même rouleau, même volume, mêmes paramètres ; seule la graine change",
           font=f_p, fill=(90, 90, 90))

    y0 = MARGE_H + 12
    if plafond is not None:
        xp = x_de(plafond)
        for y in range(y0 - 6, y0 + len(lignes) * LIGNE, 7):
            g.line([xp, y, xp, y + 3], fill=PLAFOND)
        g.text((xp - 76, y0 - 24), f"plafond de générations {plafond:.2f} cm²",
               font=f_p, fill=PLAFOND)

    for aire in (0, 5, 10, 15, 20):
        x = x_de(aire)
        g.line([x, y0 - 4, x, y0 + len(lignes) * LIGNE - 8], fill=(235, 235, 235))
        g.text((x - 6, y0 + len(lignes) * LIGNE), f"{aire}", font=f_p, fill=(110, 110, 110))
    g.text((X0 + LARG // 2 - 40, y0 + len(lignes) * LIGNE + 20), "aire atteinte (cm²)",
           font=f_n, fill=TEXTE)

    serres = 0
    for i, l in enumerate(lignes):
        y = y0 + i * LIGNE
        pa, vo = l["planarite"]["aire_cm2"], l["voisinage"]["aire_cm2"]
        xp, xv = x_de(pa), x_de(vo)
        ecart = abs(pa - vo)
        serre = ecart < ECART_SERRE_CM2
        serres += serre
        g.text((40, y - 7), l["rouleau"], font=f_n, fill=TEXTE)
        g.line([min(xp, xv), y, max(xp, xv), y],
               fill=SERRE if serre else TRAIT, width=3 if serre else 2)
        # ⚠ Quand les deux aires sont a moins d'un pixel, un disque cache l'autre et la
        # ligne se lit comme un rouleau a un seul critere -- exactement le contraire de ce
        # que la paire montre. On les DECALE verticalement : ils restent lisibles comme
        # deux mesures, et le decalage dit lui-meme qu'elles coincident.
        dy = 5 if abs(xp - xv) < 6 else 0
        g.ellipse([xv - 5, y - 5 + dy, xv + 5, y + 5 + dy],
                  fill=VOISINAGE, outline=(255, 255, 255))
        g.ellipse([xp - 5, y - 5 - dy, xp + 5, y + 5 - dy],
                  fill=PLANARITE, outline=(255, 255, 255))
        if serre:
            # ⚠ Trois decimales sous le centieme : « ecart 0,00 » sur une difference de
            # 0,001 cm² se lit comme une egalite exacte, ce qu'elle n'est pas.
            n = 3 if ecart < 0.01 else 2
            g.text((max(xp, xv) + 14, y - 7),
                   f"écart {ecart:.{n}f} cm²".replace(".", ","), font=f_p, fill=SERRE)

    yb = y0 + len(lignes) * LIGNE + 50
    g.ellipse([44, yb + 1, 54, yb + 11], fill=PLANARITE, outline=(255, 255, 255))
    g.text((62, yb), "planéité", font=f_n, fill=PLANARITE)
    g.ellipse([164, yb + 1, 174, yb + 11], fill=VOISINAGE, outline=(255, 255, 255))
    g.text((182, yb), "voisinage", font=f_n, fill=VOISINAGE)

    au_plafond = (sum(1 for l in lignes
                      if plafond is not None
                      and plafond - l["planarite"]["aire_cm2"] <= TOLERANCE_PLAFOND_CM2)
                  if plafond is not None else 0)
    for i, t in enumerate((
            f"planéité {signes['pour_planarite']}, voisinage "
            f"{signes['pour_voisinage']}, test des signes p = "
            f"{signes['p_signes']:.4f}".replace(".", ","),
            f"⚠ {serres} des {signes['pour_voisinage']} « défaites » se jouent à moins de "
            f"{ECART_SERRE_CM2:.1f} cm² — des égalités comptées comme des pertes"
            .replace("0.1", "0,1").replace("0.2", "0,2"),
            f"⚠⚠ {au_plafond} traces de planéité sur {len(lignes)} butent sur le plafond : "
            f"leur distance atteignable n'est pas mesurée, elle est tronquée")):
        g.text((40, yb + 28 + i * 20), t, font=f_n,
               fill=TEXTE if i == 0 else SERRE if i else TEXTE)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})  "
          f"{serres} paire(s) serrée(s), {au_plafond} au plafond")
    return 0


if __name__ == "__main__":
    sys.exit(main())
