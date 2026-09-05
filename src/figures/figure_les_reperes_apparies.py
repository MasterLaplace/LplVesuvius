#!/usr/bin/env python3
"""Les repères intérieurs et leur vis-à-vis — le champ résiduel que les bords ne donnaient pas.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « Médiane 40 cellules contre 320 au hasard » dit qu'un
appariement existe, pas **où** il porte. Or ce que C1 cherche est précisément un champ : des
flèches réparties sur le fragment, avec leur échelle écrite, montrent d'un coup que les repères
sont **intérieurs** et non confinés à une frontière — la propriété que les 34 carreaux de bord
n'avaient pas.

⭐⭐ **Le témoin est dessiné à côté, pas raconté** : le même nombre de points tirés au hasard
dans la même empreinte, avec leur distance médiane. Sans lui, un semis de flèches courtes se
lit comme un accord, alors que sur une empreinte trouée n'importe quel point tombe parfois près
d'un trou.

⚠ Les flèches sont **à l'échelle** et l'échelle est écrite. Un champ de déplacement dessiné à
une échelle muette se lit comme on veut.

⚠ Les nombres sont LUS dans `docs/mesures/les_reperes_apparies.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_les_reperes_apparies.py --verifier
    uv run python src/figures/figure_les_reperes_apparies.py \\
        --sortie docs/images/75_les_reperes_apparies.png
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
VERT = (52, 122, 72)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    return [
        f"{m['reperes_transportables']} reperes interieurs du masque contre "
        f"{m['trous_du_support']} trous du support publie.",
        f"ils s'apparient a {m['distance_mediane']:.0f} cellules en mediane, contre "
        f"{m['distance_temoin_mediane']:.0f} pour autant de points tires au hasard.",
        "donc le support de la carte d'encre porte bien les trous du fragment : c'est un "
        "masque de fait.",
        "et les fleches sont le champ residuel que les bords seuls ne donnaient pas — dans "
        "l'AIRE du fragment, mais GROUPEES d'un cote plutot qu'etalees.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    paires = m.get("paires") or []
    if len(paires) < 3:
        raise SystemExit(f"moins de trois paires : {len(paires)}")
    h, w = m["forme_carte"]

    marge, cote = 34, 520
    ech = cote / max(h, w)
    L = marge * 2 + int(w * ech) + 400
    lignes = prose(m)
    H = 92 + int(h * ech) + 40 + len(lignes) * 19 + 24
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Les reperes interieurs et leur vis-a-vis", fill=TEXTE, font=gros)
    art.text((marge, 42), f"{m['carte'][:64]}…  ({h}×{w})", fill=DISCRET, font=moyen)

    y0 = 84
    art.rectangle([marge, y0, marge + int(w * ech), y0 + int(h * ech)], outline=CADRE)

    # ⚠⚠ L'ÉCHELLE DES FLÈCHES EST CHOISIE POUR QUE LA PLUS LONGUE TIENNE, et elle est écrite
    # en dessous. Sans ça une flèche est un ornement.
    dists = sorted(p["distance"] for p in paires)
    p90 = dists[int(0.9 * (len(dists) - 1))] or 1.0
    # ⚠⚠ L'échelle se prend sur le NEUVIÈME DÉCILE et non sur le maximum : un appariement raté
    # à quelques centaines de cellules — un repère accroché à un trou lointain — écraserait
    # toutes les autres flèches à l'invisible. Le maximum n'est pas le champ, c'est son échec.
    facteur = 55.0 / p90
    for p in paires:
        si, sj = p["source"]
        ci, cj = p["cible"]
        x, y = marge + sj * ech, y0 + si * ech
        dx, dy = (cj - sj) * facteur * ech, (ci - si) * facteur * ech
        couleur = ROUGE if p["distance"] > p90 else AMBRE
        art.ellipse([x - 2, y - 2, x + 2, y + 2], fill=couleur)
        art.line([x, y, x + dx, y + dy], fill=couleur, width=2)

    art.text((marge, y0 + int(h * ech) + 8),
             f"echelle : une fleche de {p90:.0f} cellules (9e decile) est dessinee x"
             f"{facteur:.1f} ; en rouge, au-dela — le plus mauvais vaut {dists[-1]:.0f}",
             fill=DISCRET, font=petit)

    # --- le témoin, à côté et non raconté ---
    bx = marge + int(w * ech) + 44
    art.text((bx, y0 - 22), "l'appariement contre le hasard", fill=TEXTE, font=moyen)
    lo, hi = 0.0, max(m["distance_temoin_mediane"], m["distance_mediane"]) * 1.15
    bh = 210
    for k, (nom, val, couleur) in enumerate(
            (("reperes", m["distance_mediane"], VERT),
             ("hasard, meme compte", m["distance_temoin_mediane"], DISCRET))):
        x = bx + k * 150
        haut = (val - lo) / (hi - lo) * bh
        art.rectangle([x, y0 + bh - haut, x + 92, y0 + bh], fill=couleur)
        art.text((x, y0 + bh + 8), nom, fill=DISCRET, font=petit)
        art.text((x, y0 + bh - haut - 18), f"{val:.0f}", fill=couleur, font=moyen)
    art.text((bx, y0 + bh + 34), "cellules, distance mediane au trou le plus proche",
             fill=DISCRET, font=petit)

    bas = H - len(lignes) * 19 - 14
    for j, l in enumerate(lignes):
        art.text((marge, bas + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠ Rendu et non affirmé : combien de flèches sont réellement dessinées à l'INTÉRIEUR de
    # l'empreinte plutôt que sur son pourtour. C'est la propriété que la figure existe pour
    # montrer, donc elle doit être comptable.
    marge_bord = 0.12
    interieur = sum(1 for p in paires
                    if marge_bord * h < p["source"][0] < (1 - marge_bord) * h
                    and marge_bord * w < p["source"][1] < (1 - marge_bord) * w)
    return {"paires": len(paires), "a_l_interieur": interieur, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    faux = {"carte": "x.jpg", "forme_carte": [3305, 1883],
            "reperes_transportables": 55, "trous_du_support": 71,
            "distance_mediane": 40.28, "distance_temoin_mediane": 319.58,
            "paires": [{"source": [500.0 + 60 * k, 400.0 + 20 * k],
                        "cible": [510.0 + 60 * k, 405.0 + 20 * k],
                        "distance": 11.2 + k, "aire": 500} for k in range(12)]}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle donne l'appariement ET le hasard",
      any("40 cellules" in x and "320" in x for x in lignes), str(lignes[1]))
    # ⚠⚠ La conclusion qui compte n'est pas « ça s'apparie » mais « le support EST un masque » :
    # c'est ce qui rend la voie praticable sans rien demander à personne.
    v("... et elle dit que le support est un masque de fait",
      any("masque de fait" in x for x in lignes), str(lignes[2]))
    # ⚠⚠⚠ La figure a attrapé ma propre sur-affirmation : j'avais écrit « répartis à
    # l'INTÉRIEUR » et le dessin montre des repères GROUPÉS d'un côté. La prose dit
    # maintenant les deux — dans l'aire du fragment, mais groupés — et le contrôle exige
    # les deux mots, sinon la moitié gênante peut disparaître sans que rien ne le voie.
    v("... et qu'ils sont dans l'AIRE mais GROUPES, les deux",
      any("AIRE" in x for x in lignes) and any("GROUPEES" in x for x in lignes),
      str(lignes[-1]))

    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    r = dessiner(faux, d / "x.png")
    # ⭐⭐ LE CONTRÔLE QUI COMPTE : les repères doivent être dessinés À L'INTÉRIEUR. C'est la
    # propriété qui les distingue des 34 carreaux de bord, donc elle doit être comptable.
    v("les reperes sont dessines a l'interieur, pas sur le pourtour",
      r["a_l_interieur"] >= 10, f"{r['a_l_interieur']} sur {r['paires']}")
    # ⚠ Et le contrôle inverse : des repères posés sur le pourtour ne comptent PAS comme
    # intérieurs, sinon la mesure serait satisfaite par n'importe quel semis.
    bord = {**faux, "paires": [{"source": [10.0 + 2 * k, 5.0], "cible": [12.0 + 2 * k, 7.0],
                               "distance": 2.8, "aire": 500} for k in range(12)]}
    v("... alors qu'un semis sur le pourtour ne compte pas comme interieur",
      dessiner(bord, d / "y.png")["a_l_interieur"] == 0)
    v("moins de trois paires est REFUSE",
      _leve(lambda: dessiner({**faux, "paires": faux["paires"][:2]}, d / "z.png")))
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
                   default=RACINE / "docs" / "mesures" / "les_reperes_apparies.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_les_reperes_apparies.png")
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
