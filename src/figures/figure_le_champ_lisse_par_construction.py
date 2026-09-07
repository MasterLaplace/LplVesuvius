#!/usr/bin/env python3
"""Être lisse ne suffit pas : la lissité du champ vrai était un indice, pas une recette.

⚠⚠ POURQUOI CETTE FIGURE EXISTE, ET CE QU'ELLE CORRIGE. Deux tranches avaient conclu que le champ
de décalages utile est « lisse localement et étendu globalement », et que c'était **exactement ce
qu'un ajustement de surface produit ». Cette mesure essaie cet ajustement — et le réfute.

⭐⭐⭐ Le panneau B porte le fait qui tranche : à rugosité **nulle** on trouve **deux choses** —
le champ de l'oracle, qui rend 20 µm, et des surfaces ajustées, qui en rendent 42 à 45. Être
lisse était donc une propriété **nécessaire** du bon champ, jamais une propriété **suffisante**,
et la confondre était une inférence sur une corrélation.

⚠ Le panneau A donne le classement : aucun champ lisse par construction ne bat le voisinage 3×3
en service, et le meilleur perd **de façon consistante**. Ce que la médiane garde et qu'une
surface écrase, c'est la variation **locale** — celle-là même qu'on prenait pour du bruit.

Usage :
    uv run python src/figures/figure_le_champ_lisse_par_construction.py --verifier
    uv run python src/figures/figure_le_champ_lisse_par_construction.py \\
        --sortie docs/images/75_le_champ_lisse_par_construction.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import echelle_appariee, police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402
from lecart_apparie import tranche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_champ_lisse_par_construction.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def court(e) -> str:
    if e is None or e["ecart_median_um"] is None:
        return "—"
    return (f"{e['ecart_median_um']:+.1f} um  {e['pas_ameliores']}/{e['pas']}  "
            f"{e['intervalle_um']}")


def prose(m: dict) -> list[str]:
    def par(nom: str) -> dict:
        return next(x for x in m["resume"] if x["ajustement"] == nom)

    dep, best = par("median_3"), m["meilleur_ajustement"]
    s3 = par("surface_3")
    return [
        f"{m['paires']} pas, {m['cellules']} cellules retenues sur "
        f"{m['cellules_lisibles']} lisibles. une mediane de voisinage est un ajustement LOCAL "
        f"par une CONSTANTE ; ce qui est essaye ici est un champ dont la lissite est une "
        f"propriete de sa FORME — une surface polynomiale de degre 0 a 3 sur toute la grille, "
        f"un plan ajuste localement, et la composition du voisinage en service avec une surface.",
        f"⚠⚠ AUCUN NE BAT LE VOISINAGE EN SERVICE. le 3x3 rend {dep['erreur_correlation_um']} um ; "
        f"le meilleur des champs construits ({best['ajustement']}) rend "
        f"{best['erreur_correlation_um']} um, soit {court(best['correlation_contre_deploye'])} "
        f"— un intervalle entierement POSITIF, donc il perd de facon consistante.",
        f"⚠⚠⚠ ET LE PANNEAU B DIT POURQUOI, ce qu'aucun classement ne montrerait. a rugosite "
        f"NULLE on trouve DEUX choses : le champ de l'ORACLE, qui rend "
        f"{m['erreur_oracle_mediane_um']} um, et les surfaces ajustees, qui en rendent "
        f"{s3['erreur_correlation_um']} a {par('surface_1')['erreur_correlation_um']}. etre "
        "lisse etait donc une propriete NECESSAIRE du bon champ, jamais une propriete "
        "SUFFISANTE — et deux tranches l'avaient prise pour une recette.",
        f"⚠⚠ le temoin le confirme etage par etage : les surfaces ameliorent enormement le "
        f"BRUIT ({par('brut')['erreur_melange_um']} um pour le champ brut, "
        f"{s3['erreur_melange_um']} une fois ajuste) et a peine la LECTURE. leur part HORS "
        f"LISSAGE est POSITIVE partout ({s3['part_hors_lissage_um']:+.1f} um au degre trois) : "
        "elles rendent moins sur la lecture que sur le hasard.",
        "⚠⚠⚠ ce que ca corrige : le champ vrai est plat, mais ce qui distingue une lecture d'un "
        "bruit est LOCAL et de haute frequence spatiale. la mediane 3x3 le garde, une surface "
        "globale l'ecrase avec le bruit. l'inference « le champ utile est lisse, donc ajustons "
        "une surface » etait un raisonnement sur une correlation, et la mesure le refute.",
        f"IL RESTE {round(dep['erreur_correlation_um'] - m['erreur_oracle_mediane_um'], 1)} um "
        f"entre le voisinage en service et l'oracle, et la cinquieme porte vient de se fermer : "
        "ni la forme, ni son lieu d'apprentissage, ni son amplitude, ni la largeur du lissage, "
        "ni un champ lisse par construction.",
    ]


def nuage(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, legende: str) -> list:
    """La rugosité contre l'erreur : deux champs également lisses, deux résultats opposés.

    ⚠⚠⚠ C'EST LE PANNEAU QUI TRANCHE, et il ne peut être qu'un nuage. Un classement montrerait
    que les surfaces perdent ; seul un nuage montre POURQUOI la lissité ne prédit rien — deux
    points de même abscisse, l'oracle et une surface, séparés de plus de vingt micromètres en
    ordonnée.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    pts = [(x["rugosite_vx"], x["erreur_correlation_um"], x["ajustement"],
            VERT if x["deploye"] else BLEU)
           for x in m["resume"] if x["rugosite_vx"] is not None]
    # ⚠⚠ L'ORACLE EST SUR LE MÊME NUAGE, et c'est indispensable : sans lui, on lirait « les
    # champs lisses perdent », alors que le fait est que le MEILLEUR champ possible est lui
    # aussi parfaitement lisse.
    pts.append((0.0, m["erreur_oracle_mediane_um"], "ORACLE", ROUGE))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    gauche, droite = x0 + 50, x0 + pw - 40
    bas, haut = y0 + ph - 44, y0 + 34
    xmax = max(xs) * 1.15 or 1.0
    ymin, ymax = min(ys) * 0.9, max(ys) * 1.05

    def px(val: float) -> float:
        return gauche + (droite - gauche) * val / xmax

    def py(val: float) -> float:
        return bas - (bas - haut) * (val - ymin) / (ymax - ymin)

    art.line([gauche, bas, droite, bas], fill=TEXTE)
    art.line([gauche, bas, gauche, haut], fill=TEXTE)
    for val in (0.0, xmax / 2, xmax):
        art.text((px(val) - 10, bas + 6), f"{val:.1f}", fill=DISCRET, font=petit)
    for val in (ymin, (ymin + ymax) / 2, ymax):
        art.text((x0 + 8, py(val) - 6), f"{val:.0f}", fill=DISCRET, font=petit)
    # ⚠⚠ LES ÉTIQUETTES SONT ÉCARTÉES VERTICALEMENT, parce que le fait à montrer les empile :
    # quatre surfaces ont exactement la même abscisse (rugosité nulle) et des ordonnées à deux
    # micromètres l'une de l'autre. Superposées, elles ne se lisent ni l'une ni l'autre, et
    # c'est précisément le groupe qui porte le résultat.
    ecart_mini, prise = 13.0, []
    for x_, y_, nom, coul in sorted(pts, key=lambda t: t[1]):
        cx, cy = px(x_), py(y_)
        art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=coul)
        ty = cy - 6
        while any(abs(ty - u) < ecart_mini for u in prise):
            ty -= ecart_mini
        prise.append(ty)
        if abs(ty - (cy - 6)) > 2:
            art.line([cx + 6, cy, cx + 10, ty + 6], fill=coul)
        art.text((cx + 12, ty), nom.replace("_", " "), fill=coul, font=petit)
    art.text((x0 + 10, y0 + ph - 18),
             "abscisse : rugosite (vx) · ordonnee : erreur de marche (um)",
             fill=DISCRET, font=petit)
    return [p[2].replace("_", " ") for p in pts]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart = 40, 440, 46
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    ph = 34 + 46 * len(m["resume"])
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Etre lisse ne suffit pas : c'etait un indice, pas une recette",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} pas · {m['cellules']} cellules · surfaces ajustees contre le "
             f"voisinage en service", fill=DISCRET, font=moyen)
    art.text((marge, 76), "A · ce que chaque champ construit coute, contre le 3x3 en service",
             fill=TEXTE, font=moyen)
    eta = echelle_appariee(
        art, marge, 96, pw, ph,
        [(x["ajustement"].replace("_", " "), x["correlation_contre_deploye"],
          VERT if tranche(x["correlation_contre_deploye"]) else BLEU, x["deploye"])
         for x in m["resume"]],
        petit, "negatif : mieux que le voisinage en service · positif : pire",
        FOND, TEXTE, DISCRET, CADRE)
    bx = marge + pw + ecart
    art.text((bx, 76), "B · la rugosite ne predit PAS l'erreur", fill=TEXTE, font=moyen)
    eta += nuage(art, bx, 96, pw, ph, m, petit,
                 "rouge : l'ORACLE · vert : le voisinage en service · bleu : les autres")
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"ajustements": len(m["resume"]), "etiquettes": eta,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "panneau": pw, "sortie": str(sortie)}


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
        return next(x for x in m["resume"] if x["ajustement"] == nom)

    # ⭐⭐⭐ LE RÉSULTAT : aucun champ lisse par construction ne bat le voisinage en service, et
    # le meilleur perd de façon CONSISTANTE — l'intervalle est entièrement positif.
    v("aucun champ lisse par construction ne bat le voisinage en service",
      not m["un_champ_construit_bat_le_deploye"],
      str(m["meilleur_ajustement"]["correlation_contre_deploye"]))
    v("... et le meilleur perd de façon consistante",
      m["meilleur_ajustement"]["correlation_contre_deploye"]["intervalle_um"][0] > 0,
      f"{m['meilleur_ajustement']['ajustement']} · "
      f"{m['meilleur_ajustement']['correlation_contre_deploye']['intervalle_um']}")
    # ⭐⭐⭐ ET LE FAIT QUE LE PANNEAU B PORTE : les surfaces font EXACTEMENT ce qu'on leur
    # demandait — elles sont parfaitement lisses — et elles marchent plus mal.
    v("les surfaces ajustées sont parfaitement lisses, et marchent pourtant plus mal",
      all(par(f"surface_{d}")["rugosite_vx"] == 0.0 for d in m["degres"])
      and all(par(f"surface_{d}")["erreur_correlation_um"]
              > par("median_3")["erreur_correlation_um"] for d in m["degres"]),
      str({f"surface_{d}": (par(f'surface_{d}')['rugosite_vx'],
                            par(f'surface_{d}')['erreur_correlation_um'])
           for d in m["degres"]}))
    # ⚠⚠⚠ LA CONFUSION QUE LA FIGURE CORRIGE : à rugosité nulle on trouve l'oracle ET les
    # surfaces, séparés de plus de vingt micromètres. La lissité ne prédit donc rien.
    v("... à rugosité nulle on trouve AUSSI l'oracle, vingt micromètres plus bas",
      par("surface_1")["erreur_correlation_um"] - m["erreur_oracle_mediane_um"] > 20.0,
      f"{par('surface_1')['erreur_correlation_um']} contre "
      f"{m['erreur_oracle_mediane_um']} µm")
    # ⚠⚠ ET LE TÉMOIN : les surfaces améliorent le bruit plus que la lecture.
    v("les surfaces rendent MOINS sur la lecture que sur le bruit",
      all(par(f"surface_{d}")["part_hors_lissage_um"] > 0 for d in m["degres"]),
      str([par(f"surface_{d}")["part_hors_lissage_um"] for d in m["degres"]]))
    v("... et le voisinage en service reste le meilleur des champs mesurés",
      par("median_3")["erreur_correlation_um"]
      == min(x["erreur_correlation_um"] for x in m["resume"]),
      str({x["ajustement"]: x["erreur_correlation_um"] for x in m["resume"]}))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les ajustements sont dessinés", r["ajustements"] == len(m["resume"]),
          str(r["ajustements"]))
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"][:3]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · ce que chaque champ construit coute, contre le 3x3 en service",
                      "B · la rugosite ne predit PAS l'erreur"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < r["panneau"],
              f"{pt_.getbbox(titre)[2]} px pour {r['panneau']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "75_le_champ_lisse_par_construction.png")
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
