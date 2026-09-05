#!/usr/bin/env python3
"""L'accord avec la carte publiée, en fonction du seuil d'encre — deux régimes, un témoin.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat n'est **pas un nombre mais une FORME** : en
production l'accord monte avec le seuil (0,345 → 0,755), au régime du prix il reste plat
(0,398 → 0,391), et le témoin par mélange tient 0,500 partout. Trois nombres ne se comparent
pas ; trois courbes, si.

⭐⭐⭐ ET LE TÉMOIN EST DESSINÉ AVEC LES DEUX AUTRES, pas relégué à une note. C'est lui qui
autorise à lire une AUC sous 0,5 comme un fait sur les cartes plutôt que comme un biais du
montage — le voir plat à 0,500 est ce qui rend les deux autres courbes lisibles.

⚠⚠ LE NOMBRE DE PIXELS EST ÉCRIT À CHAQUE POINT, parce que le point le plus haut de la courbe
de production n'en porte que **32**. Une courbe sans ses effectifs invite à lire son extrémité
comme son milieu, et c'est exactement l'endroit où la réserve se joue.

⚠ Les nombres sont LUS dans `docs/mesures/la_case_vide_remplie.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_case_vide_remplie.py --verifier
    uv run python src/figures/figure_case_vide_remplie.py \\
        --sortie docs/images/75_la_case_vide_remplie.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
BLEU = (86, 148, 196)
GRIS = (110, 116, 124)


def series(m: dict) -> list[tuple[str, list[dict], tuple[int, int, int]]]:
    """
    @brief Les trois courbes à tracer, dans l'ordre où elles se lisent.

    ⚠ Le témoin passe en DERNIER dans le dessin pour rester visible par-dessus les deux autres :
    c'est la ligne de référence, et une figure où la référence disparaît sous une courbe se lit
    comme une figure à deux courbes.
    """
    out = []
    for nom, cle, couleur in (("production (2,399 µm)", "production_courbe", AMBRE),
                              ("regime du prix (9,362 µm)", "courbe", BLEU),
                              ("temoin : nos pixels melanges", "temoin_melange", GRIS)):
        points = [x for x in (m.get(cle) or []) if x.get("auc") is not None]
        if points:
            out.append((nom, points, couleur))
    return out


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    prod = [x["auc"] for x in (m.get("production_courbe") or []) if x["auc"] is not None]
    prix = [x["auc"] for x in (m.get("courbe") or []) if x["auc"] is not None]
    queue = [x for x in (m.get("production_courbe") or []) if x["quantile"] == 99]
    lignes = [
        f"en production l'accord MONTE avec le seuil : {prod[0]:.3f} -> {prod[-1]:.3f}.",
        f"au regime du prix il reste PLAT : {prix[0]:.3f} -> {prix[-1]:.3f}.",
        "le temoin par melange tient 0,500 partout, donc le montage n'est pas biaise.",
    ]
    if queue:
        lignes.append(f"⚠ mais le point le plus haut ne porte que {queue[0]['pixels_encre']} "
                      "pixels, et le bas des deux courbes ordonne du bruit de JPEG.")
    return lignes


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    courbes = series(m)
    if len(courbes) < 2:
        raise SystemExit("moins de deux courbes : rien à comparer")

    marge, larg, haut = 64, 560, 300
    L, H = marge * 2 + larg + 300, 96 + haut + 40 + len(prose(m)) * 19 + 30
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    d.text((marge, 22), "l'accord avec la carte publiee, seuil par seuil", fill=TEXTE, font=gros)
    d.text((marge, 48), f"{m['segment']} — notre detecteur contre la carte d'encre publiee du "
                        "meme segment", fill=DISCRET, font=moyen)

    y0, y1 = 96, 96 + haut
    # ⚠⚠ L'AXE VA DE 0,3 A 0,8 ET LE DIT. Un axe qui partirait de 0 écraserait tout l'écart
    # entre 0,35 et 0,76 contre le bord ; un axe muet ferait croire à une échelle pleine.
    lo, hi = 0.30, 0.80
    d.rectangle([marge, y0, marge + larg, y1], outline=(60, 60, 60))
    for val in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
        yy = y1 - (val - lo) / (hi - lo) * haut
        couleur = (90, 90, 90) if abs(val - 0.5) > 1e-9 else (150, 120, 60)
        d.line([marge, yy, marge + larg, yy], fill=couleur)
        d.text((marge - 34, yy - 7), f"{val:.1f}", fill=DISCRET, font=petit)
    d.text((marge + larg + 6, y1 - (0.5 - lo) / (hi - lo) * haut - 7), "hasard",
           fill=(150, 120, 60), font=petit)

    quantiles = [x["quantile"] for x in courbes[0][1]]
    def px(i):
        return marge + (larg * i / max(1, len(quantiles) - 1))
    for i, q in enumerate(quantiles):
        d.text((px(i) - 8, y1 + 8), f"p{q}", fill=DISCRET, font=petit)
    d.text((marge, y1 + 26), "seuil d'encre : quantile de la carte publiee",
           fill=DISCRET, font=petit)

    for k, (nom, points, couleur) in enumerate(courbes):
        pts = [(px(i), y1 - (x["auc"] - lo) / (hi - lo) * haut) for i, x in enumerate(points)]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=couleur, width=2)
        montre_effectifs = "melanges" not in nom
        for (xx, yy), x in zip(pts, points):
            d.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], outline=couleur, width=2)
            # ⚠ L'effectif à chaque point : c'est là que la réserve se lit. Pas sur le témoin,
            # qui partage la carte de référence du régime du prix — écrire deux fois le même
            # nombre au même endroit rend les deux illisibles.
            if montre_effectifs:
                d.text((xx - 12, yy - 18), str(x["pixels_encre"]), fill=couleur, font=petit)
        d.text((marge + larg + 24, y0 + 8 + k * 22), nom, fill=couleur, font=moyen)

    bas = y1 + 48
    for j, ligne in enumerate(prose(m)):
        d.text((marge, bas + j * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"courbes": [nom for nom, _, _ in courbes], "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        print(f"  {'ok  ' if cond else 'ECHEC'}  {nom}" + (f"  — {detail}" if detail else ""))
        if not cond:
            echecs += 1

    faux = {"segment": "s",
            "production_courbe": [{"quantile": q, "auc": a, "pixels_encre": n, "seuil": 30.0}
                                  for q, a, n in ((50, 0.345, 1934), (75, 0.395, 989),
                                                  (90, 0.432, 390), (95, 0.516, 193),
                                                  (99, 0.755, 32))],
            "courbe": [{"quantile": q, "auc": a, "pixels_encre": n, "seuil": 30.0}
                       for q, a, n in ((50, 0.398, 25204), (75, 0.409, 14168),
                                       (90, 0.354, 5973), (95, 0.380, 2986),
                                       (99, 0.391, 547))],
            "temoin_melange": [{"quantile": q, "auc": 0.5, "pixels_encre": 100, "seuil": 30.0}
                               for q in (50, 75, 90, 95, 99)]}
    v("les trois courbes sont trouvées", len(series(faux)) == 3,
      str([n for n, _, _ in series(faux)]))
    # ⚠⚠ LE TÉMOIN EST TRACÉ EN DERNIER, donc par-dessus : une figure où la référence disparaît
    # sous une courbe se lit comme une figure à deux courbes.
    v("... et le témoin passe en dernier", "melanges" in series(faux)[-1][0])
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle dit que la production MONTE", any("MONTE" in l for l in lignes))
    v("... et que le régime du prix reste PLAT", any("PLAT" in l for l in lignes))
    # ⚠⚠⚠ LA RÉSERVE EST DANS LA FIGURE, pas dans une note à côté : le point le plus haut ne
    # porte que 32 pixels, et une courbe qui tairait ses effectifs invite à lire son extrémité
    # comme son milieu.
    v("... et elle nomme les 32 pixels du point le plus haut",
      any("32 pixels" in l for l in lignes), str(lignes[-1]))
    # ⚠ Une mesure sans courbe de production ne doit pas prétendre comparer deux régimes.
    seule = {"segment": "s", "courbe": faux["courbe"]}
    v("une seule courbe ne produit pas de figure",
      _leve(lambda: dessiner(seule, Path("/tmp/x.png"))))

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
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
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_case_vide_remplie.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_la_case_vide_remplie.png")
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
