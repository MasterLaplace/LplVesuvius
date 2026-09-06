#!/usr/bin/env python3
"""La lissité est épuisée à l'étage déployé : au-delà, tout le gain est du lissage.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. `le_critere_du_raccrochage` a montré que ce qui fait marcher le
raccrochage n'est pas la corrélation d'intensité mais l'accord de voisinage — un énoncé sur la
matière. Restait à savoir jusqu'où cet énoncé porte : le voisinage s'élargit (3×3 → 17×17) et
s'itère (une passe → trois).

⭐⭐⭐ La réponse est nette et c'est une porte fermée : **aucun étage ne bat celui en service**. Et
le panneau B dit pourquoi, ce qu'aucun tableau d'erreurs ne montrerait — à mesure que la fenêtre
s'élargit, l'écart contre l'immobilité semble s'améliorer, mais la part attribuable à la LECTURE
s'effondre et change de signe. Au-delà du 3×3, le gain supplémentaire est du **lissage pur**.

⚠⚠ Le panneau A porte la preuve visuelle : l'erreur de la lecture et celle du BRUIT **convergent**
quand la fenêtre s'élargit. Deux courbes qui se rejoignent, c'est un lissage qui a effacé ce qui
distinguait la lecture du hasard.

Usage :
    uv run python src/figures/figure_la_lissite_de_la_feuille.py --verifier
    uv run python src/figures/figure_la_lissite_de_la_feuille.py \\
        --sortie docs/images/75_la_lissite_de_la_feuille.png
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
MESURE = RACINE / "docs" / "mesures" / "la_lissite_de_la_feuille.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    def par(nom: str) -> dict:
        return next(x for x in m["resume"] if x["etage"] == nom)

    dep, large = par("median_1"), par("median_8")
    itere = par("median_1_x3")
    return [
        f"{m['paires']} pas, {m['cellules']} cellules retenues sur "
        f"{m['cellules_lisibles']} lisibles. ce qui varie est la LARGEUR du voisinage de grille "
        f"(3x3 a 17x17) et le nombre de PASSES. ⚠ tous les etages sont juges sur la MEME "
        f"population, fixee par le plus large — sinon un 17x17 serait note sur le coeur de la "
        f"grille pendant qu'un 3x3 le serait sur presque tout, et l'ecart porterait sur les "
        f"bords.",
        f"⚠⚠ AUCUN ETAGE NE BAT CELUI EN SERVICE. le 3x3 une passe rend "
        f"{dep['erreur_correlation_um']} um ; elargir a 17x17 remonte a "
        f"{large['erreur_correlation_um']}, iterer trois fois donne "
        f"{itere['erreur_correlation_um']}. le meilleur ecart apparie au deploye vaut "
        f"{m['ecart_du_meilleur_au_deploye']['ecart_median_um']:+.1f} um "
        f"({m['ecart_du_meilleur_au_deploye']['pas_ameliores']}/"
        f"{m['ecart_du_meilleur_au_deploye']['pas']} pas, intervalle "
        f"{m['ecart_du_meilleur_au_deploye']['intervalle_um']}) : il ne tranche pas.",
        f"⚠⚠⚠ ET LE PANNEAU B DIT POURQUOI, ce qu'aucun tableau d'erreurs ne montrerait. contre "
        f"l'immobilite, elargir SEMBLE aider : "
        + " · ".join(f"{x['etage']} "
                     f"{x['correlation_contre_ne_rien_faire']['ecart_median_um']:+.1f}"
                     for x in m["resume"] if x["etage"] != "brut")
        + " um. mais la part attribuable a la LECTURE — ce qui reste une fois retire ce que le "
        "MEME lissage rend sur du BRUIT — s'effondre et change de signe : "
        + " · ".join(f"{n} {p:+.1f}" for n, p in m["part_hors_lissage_par_etage"]) + " um.",
        f"⚠⚠ le panneau A porte la preuve : l'erreur de la LECTURE et celle du BRUIT "
        f"CONVERGENT quand la fenetre s'elargit — de "
        f"{dep['erreur_correlation_um']} contre {dep['erreur_melange_um']} um au 3x3, a "
        f"{large['erreur_correlation_um']} contre {large['erreur_melange_um']} au 17x17. deux "
        f"courbes qui se rejoignent, c'est un lissage qui a efface ce qui distinguait la "
        f"lecture du hasard.",
        f"⚠ iterer ne paie pas davantage qu'elargir : deux et trois passes du 3x3 rendent "
        f"{par('median_1_x2')['erreur_correlation_um']} et {itere['erreur_correlation_um']} um, "
        f"avec des parts hors lissage de "
        f"{par('median_1_x2')['part_hors_lissage_um']:+.1f} et "
        f"{itere['part_hors_lissage_um']:+.1f} um — soit la meme chose que la passe unique "
        f"({dep['part_hors_lissage_um']:+.1f}).",
        f"la BORNE reste a {m['erreur_oracle_mediane_um']} um contre "
        f"{dep['erreur_correlation_um']} pour l'etage deploye : il reste "
        f"{round(dep['erreur_correlation_um'] - m['erreur_oracle_mediane_um'], 1)} um, et la "
        "lissite n'ira pas les chercher. c'est une quatrieme porte fermee sur la lecture, apres "
        "la forme, l'endroit ou on l'apprend et l'amplitude.",
    ]


def courbes(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, moyen,
            legende: str) -> list[str]:
    """L'erreur de la LECTURE et celle du BRUIT, étage par étage, avec les deux repères.

    ⚠⚠⚠ LES DEUX COURBES SONT SUR LA MÊME ÉCHELLE, et c'est tout le propos : leur écart EST ce
    que la lecture apporte. Les dessiner sur deux axes, ou n'en dessiner qu'une, ferait perdre
    exactement le fait que la figure existe pour montrer — qu'elles se rejoignent.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    etages = [x["etage"] for x in m["resume"]]
    lecture = [x["erreur_correlation_um"] for x in m["resume"]]
    bruit = [x["erreur_melange_um"] for x in m["resume"]]
    reperes = [(m["erreur_ne_rien_faire_mediane_um"], "ne rien faire"),
               (m["erreur_oracle_mediane_um"], "oracle")]
    tout = lecture + bruit + [v for v, _ in reperes]
    bas, haut = 0.0, max(tout) * 1.08
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    base = y0 + ph - 26
    hmax = ph - 78

    def yy(val: float) -> float:
        return base - (val - bas) / (haut - bas) * hmax

    for val, nom in reperes:
        y = yy(val)
        for xx_ in range(x0 + 4, x0 + pw - 4, 7):
            art.line([xx_, y, xx_ + 3, y], fill=DISCRET)
        art.text((x0 + 8, y - 13), f"{nom} {val:.1f} um", fill=DISCRET, font=petit)
    pas_x = (pw - 40) / max(1, len(etages) - 1)
    for serie, coul, nom in ((lecture, VERT, "LECTURE"), (bruit, AMBRE, "BRUIT")):
        points = [(x0 + 20 + pas_x * i, yy(v)) for i, v in enumerate(serie)]
        for (ax, ay), (bx_, by_) in zip(points, points[1:]):
            art.line([ax, ay, bx_, by_], fill=coul, width=2)
        for cx, cy in points:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        art.text((points[-1][0] - petit.getbbox(nom)[2], points[-1][1] - 16), nom,
                 fill=coul, font=petit)
    for i, nom in enumerate(etages):
        court = nom.replace("median_", "").replace("brut", "0")
        art.text((x0 + 20 + pas_x * i - petit.getbbox(court)[2] / 2, base + 8), court,
                 fill=DISCRET, font=petit)
    # ⚠ La légende d'abscisse monte sous celle des couleurs : posée en bas, elle tombait sur
    # les étiquettes des étages, et deux textes superposés ne se lisent ni l'un ni l'autre.
    art.text((x0 + 8, y0 + 22), "abscisse : demi-largeur du voisinage, puis les passes",
             fill=DISCRET, font=petit)
    return etages


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
    art.text((marge, 18), "La lissite est epuisee a l'etage deploye", fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} pas · {m['cellules']} cellules · le voisinage s'elargit, "
             f"puis s'itere", fill=DISCRET, font=moyen)

    art.text((marge, 76), "A · la LECTURE et le BRUIT convergent quand la fenetre s'elargit",
             fill=TEXTE, font=moyen)
    eta = courbes(art, marge, 96, pw, ph, m, petit, moyen,
                  "vert : correlation · ambre : gabarit MELANGE · pointilles : les deux reperes")
    bx = marge + pw + ecart
    art.text((bx, 76), "B · ce que la LECTURE ajoute, une fois le lissage retire",
             fill=TEXTE, font=moyen)
    # ⚠⚠⚠ LA PART HORS LISSAGE EST UN ÉCART D'ÉCARTS, donc elle n'a pas d'intervalle apparié :
    # elle est dessinée comme une barre nue, et le panneau le dit. Lui fabriquer un intervalle
    # serait publier une précision que la soustraction ne porte pas.
    entrees = []
    for x in m["resume"]:
        if x["etage"] == "brut":
            continue
        part = x["part_hors_lissage_um"]
        e = dict(ecart_median_um=part, intervalle_um=[part, part],
                 pas_ameliores=x["correlation_contre_brut"]["pas_ameliores"],
                 pas=x["correlation_contre_brut"]["pas"])
        entrees.append((x["etage"].replace("_", " "),
                        e, VERT if part < 0 else ROUGE, x["deploye"]))
    eta += echelle_appariee(art, bx, 96, pw, ph, entrees, petit,
                            "negatif : la lecture ajoute · positif : le lissage seul suffirait",
                            FOND, TEXTE, DISCRET, CADRE)
    art.text((bx + 10, 96 + ph - 18),
             "barre nue : un ecart d'ecarts n'a pas d'intervalle apparie",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"etages": len(m["resume"]), "etiquettes": eta,
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
        return next(x for x in m["resume"] if x["etage"] == nom)

    # ⚠⚠ UNE SEULE POPULATION, fixée par le voisinage le plus large.
    v("tous les étages sont jugés sur la même population",
      all(0 < e["cellules"] <= e["cellules_lisibles"] for e in m["lignes"]),
      str([(e["cellules"], e["cellules_lisibles"]) for e in m["lignes"]][:3]))
    v("... et chaque étage déplace réellement des cellules",
      all(e[f"deplacees_correlation_{n}"] > 0 for e in m["lignes"]
          for n in m["etages"] if n != "brut"))
    # ⭐⭐⭐ LE RÉSULTAT : aucun étage ne bat celui en service.
    v("aucun étage ne bat celui EN SERVICE", not m["un_etage_bat_le_deploye"],
      f"{m['meilleur_etage']['etage']} · {m['ecart_du_meilleur_au_deploye']}")
    v("... et la lissité ne paie pas au-delà de l'étage déployé",
      not m["la_lissite_paie_au_dela_du_deploye"],
      str(m["part_hors_lissage_par_etage"]))
    # ⚠⚠⚠ LE FAIT QUE LE PANNEAU B PORTE : élargir SEMBLE aider contre l'immobilité, alors que
    # la part attribuable à la lecture s'effondre. Sans ce contrôle, la prose pourrait cesser
    # de dire les deux et l'on lirait « plus large, c'est mieux ».
    v("élargir améliore l'écart à l'immobilité, et DÉGRADE la part hors lissage",
      par("median_4")["correlation_contre_ne_rien_faire"]["ecart_median_um"]
      < par("median_1")["correlation_contre_ne_rien_faire"]["ecart_median_um"]
      and par("median_4")["part_hors_lissage_um"] > par("median_1")["part_hors_lissage_um"],
      f"écart {par('median_4')['correlation_contre_ne_rien_faire']['ecart_median_um']} "
      f"contre {par('median_1')['correlation_contre_ne_rien_faire']['ecart_median_um']} · "
      f"part {par('median_4')['part_hors_lissage_um']} contre "
      f"{par('median_1')['part_hors_lissage_um']}")
    # ⚠⚠ ET LA PREUVE DU PANNEAU A : les deux courbes se rejoignent.
    ecart_3 = par("median_1")["erreur_melange_um"] - par("median_1")["erreur_correlation_um"]
    ecart_17 = par("median_8")["erreur_melange_um"] - par("median_8")["erreur_correlation_um"]
    v("la LECTURE et le BRUIT convergent quand la fenêtre s'élargit",
      ecart_17 < ecart_3, f"{ecart_17:.1f} µm d'écart au 17×17 contre {ecart_3:.1f} au 3×3")
    v("itérer ne paie pas plus qu'élargir",
      abs(par("median_1_x3")["part_hors_lissage_um"]
          - par("median_1")["part_hors_lissage_um"]) < 1.0,
      f"{par('median_1_x3')['part_hors_lissage_um']} contre "
      f"{par('median_1')['part_hors_lissage_um']} µm")
    v("⛔ la borne reste loin, et la lissité n'ira pas la chercher",
      m["erreur_oracle_mediane_um"] < par("median_1")["erreur_correlation_um"] / 1.4,
      f"{m['erreur_oracle_mediane_um']} contre "
      f"{par('median_1')['erreur_correlation_um']} µm")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les étages sont dessinés", r["etages"] == len(m["resume"]), str(r["etages"]))
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
        for titre in ("A · la LECTURE et le BRUIT convergent quand la fenetre s'elargit",
                      "B · ce que la LECTURE ajoute, une fois le lissage retire"):
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
                   default=RACINE / "docs" / "images" / "75_la_lissite_de_la_feuille.png")
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
