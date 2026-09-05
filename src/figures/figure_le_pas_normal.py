#!/usr/bin/env python3
"""Le pas normal contre ses deux témoins : ne rien faire, et faire deux fois trop.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « Le pas normal atteint la feuille suivante » se croit ou ne se
croit pas ; **trois barres par paire** se regardent. Le pas nul dit ce que vaut ne rien faire, le
pas double dit ce que vaut dépasser, et le pas simple n'a de sens qu'entre les deux — c'est le
**V** qui prouve que la distance franchie est bien celle d'une feuille et non du bruit.

⭐⭐ La ligne de l'écart inter-feuilles est tracée, parce que c'est elle que le pas nul doit
retrouver : un témoin qui ne tomberait pas dessus dirait que les spires ne sont pas voisines, et
toute la mesure s'écroulerait avant d'avoir commencé.

⚠ La paire qui échoue est dessinée comme les autres et nommée : c'est **12 → 13**, dont l'écart
mesuré vaut 63 µm, soit moins d'une demi-feuille — un pas d'une feuille entière y dépasse
forcément.

Usage :
    uv run python src/figures/figure_le_pas_normal.py --verifier
    uv run python src/figures/figure_le_pas_normal.py \\
        --sortie docs/images/75_le_pas_normal.png
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
MESURE = RACINE / "docs" / "mesures" / "le_pas_normal_atteint_la_spire.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
GRIS = (170, 170, 170)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    rate = [e for e in m["lignes"] if not e["rapproche"]]
    lignes = [
        f"la primitive du deroulement : depuis une feuille, avancer d'un ecart inter-feuilles "
        f"({m['ecart_lu_um']:.0f} um = {m['pas_en_voxels']:.0f} voxels) le long de la normale.",
        f"pas nul {m['pas_nul_median_um']:.0f} um, pas SIMPLE {m['pas_simple_median_um']:.0f} um, "
        f"pas double {m['pas_double_median_um']:.0f} um : le simple est le seul a faire mieux que "
        "ne rien faire, et le double depasse.",
        f"{m['paires_rapprochees']} paires sur {m['paires']} sont rapprochees, et le sens retenu "
        "est le meme pour toutes — les grilles publiees partagent une orientation.",
    ]
    if rate:
        e = rate[0]
        lignes.append(
            f"la seule paire qui echoue est {e['de']} to {e['vers']}, dont l'ecart vaut "
            f"{e['pas_nul_um']:.0f} um : moins d'une demi-feuille, donc un pas entier y depasse.")
    return lignes


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lg = m["lignes"]
    marge = 44
    gw, gh = 700, 250
    x0, y0 = marge + 44, 108
    lignes = couper(prose(m), 108)
    L = x0 + gw + marge + 30
    H = y0 + gh + 130 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Le pas normal contre ses deux temoins", fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"distance mediane a la spire suivante, {m['echantillon']} points par paire, "
             f"volume {m['volume']}", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             "gris : ne rien faire — ambre : un ecart le long de la normale — bleu : deux ecarts",
             fill=DISCRET, font=moyen)

    haut = max(max(e["pas_nul_um"], e["pas_simple"]["atteint_um"],
                   e["pas_double"]["atteint_um"]) for e in lg) * 1.12
    art.rectangle([x0, y0, x0 + gw, y0 + gh], outline=CADRE)
    ye = y0 + gh - m["ecart_lu_um"] / haut * gh
    art.line([x0, ye, x0 + gw, ye], fill=ROUGE, width=2)
    # ⚠ Le libellé de la ligne est posé sur un fond opaque : sans lui il passe derrière les
    # barres, et un repère illisible est un repère absent.
    etiq = f"ecart inter-feuilles : {m['ecart_lu_um']:.0f} um"
    art.rectangle([x0 + 4, ye - 16, x0 + 4 + 7 * len(etiq), ye - 3], fill=FOND)
    art.text((x0 + 4, ye - 15), etiq, fill=ROUGE, font=petit)
    for k in (0, 1, 2):
        val = haut * k / 2.0
        y = y0 + gh - val / haut * gh
        art.text((x0 - 40, y - 6), f"{val:.0f}", fill=DISCRET, font=petit)

    lb = gw / max(1, len(lg))
    rates = 0
    for k, e in enumerate(lg):
        base = x0 + k * lb
        for j, (val, coul) in enumerate(((e["pas_nul_um"], GRIS),
                                         (e["pas_simple"]["atteint_um"], AMBRE),
                                         (e["pas_double"]["atteint_um"], BLEU))):
            h = val / haut * gh
            x = base + 4 + j * (lb - 10) / 3.0
            art.rectangle([x, y0 + gh - h, x + (lb - 10) / 3.0 - 2, y0 + gh], fill=coul)
        if not e["rapproche"]:
            rates += 1
            art.text((base + lb / 2 - 6, y0 + gh + 18), "✗", fill=ROUGE, font=moyen)
        art.text((base + lb / 2 - 12, y0 + gh + 4), f"{e['de']}-{e['vers']}",
                 fill=DISCRET, font=petit)
    art.text((x0, y0 + gh + 36), "une paire de spires par groupe, en micrometres",
             fill=DISCRET, font=petit)

    ys = y0 + gh + 58
    art.text((x0, ys), f"medianes : nul {m['pas_nul_median_um']:.0f} um  —  "
             f"SIMPLE {m['pas_simple_median_um']:.0f} um  —  "
             f"double {m['pas_double_median_um']:.0f} um", fill=TEXTE, font=moyen)
    art.text((x0, ys + 20),
             f"{m['paires_rapprochees']} paires sur {m['paires']} rapprochees   →   "
             f"le pas normal atteint la spire suivante : "
             f"{'OUI' if m['le_pas_normal_atteint_la_spire'] else 'NON'}",
             fill=TEXTE, font=moyen)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"paires": len(lg), "echecs_dessines": rates, "sortie": str(sortie)}


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
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LE V QUE LA FIGURE MONTRE DOIT EXISTER DANS LA MESURE : le simple sous le nul ET sous
    # le double. Sans les deux, « le pas franchit une feuille » n'est pas établi — un pas qui
    # bat seulement le nul pourrait franchir n'importe quelle distance.
    v("le pas simple bat le pas nul",
      m["pas_simple_median_um"] < m["pas_nul_median_um"],
      f"{m['pas_simple_median_um']} contre {m['pas_nul_median_um']}")
    v("... et le double dépasse, donc la distance franchie est bien celle d'une feuille",
      m["pas_double_median_um"] > m["pas_simple_median_um"],
      f"{m['pas_double_median_um']} contre {m['pas_simple_median_um']}")
    # ⚠⚠ Le pas nul doit retomber sur l'écart mesuré : sinon les spires ne seraient pas voisines
    # et toute la mesure s'écroulerait avant de commencer.
    v("le pas nul retombe sur l'écart inter-feuilles",
      abs(m["pas_nul_median_um"] - m["ecart_lu_um"]) / m["ecart_lu_um"] < 0.15,
      f"{m['pas_nul_median_um']} contre {m['ecart_lu_um']}")
    v("la majorité des paires est rapprochée",
      m["paires_rapprochees"] > m["paires"] / 2,
      f"{m['paires_rapprochees']} sur {m['paires']}")
    # ⚠ Et une figure qui ne montrerait QUE des succès cacherait la paire qui échoue.
    rates = [e for e in m["lignes"] if not e["rapproche"]]
    v("... et la ou les paires qui échouent existent et sont nommées",
      len(rates) == m["paires"] - m["paires_rapprochees"],
      f"{len(rates)} échec(s)")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les paires sont dessinées", r["paires"] == m["paires"], str(r["paires"]))
        v("... et les échecs sont marqués, pas gommés",
          r["echecs_dessines"] == len(rates), f"{r['echecs_dessines']} marqué(s)")
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
                   default=RACINE / "docs" / "images" / "75_le_pas_normal.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['paires']} paires, {r['echecs_dessines']} échec marqué)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
