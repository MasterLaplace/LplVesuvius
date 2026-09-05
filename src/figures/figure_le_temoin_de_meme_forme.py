#!/usr/bin/env python3
"""Le témoin qui garde la forme : la vraie place des repères n'a rien de particulier.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « L'appariement ne bat pas le témoin de même forme » est une
phrase qu'on croit ou non. La **règle** des vingt poses, avec la vraie posée dessus, se regarde :
si la vraie tombe au milieu du peloton, il n'y a pas de correspondance, et aucun commentaire ne
peut le faire dire autrement.

⭐⭐ **Et le nuage déplacé est dessiné à côté du vrai**, sur la même carte, pour montrer ce que le
témoin conserve : la géométrie interne. C'est ce qui le distingue du semis uniforme, qui cassait
la place ET le groupement, donc ne pouvait pas dire lequel des deux expliquait un bon score.

⚠ Les nombres et les positions sont LUS dans `docs/mesures/le_temoin_de_meme_forme.json`, y
compris les poses : les retirer au hasard ici dessinerait un témoin différent de celui qui a été
jugé.

Usage :
    uv run python src/figures/figure_le_temoin_de_meme_forme.py --verifier
    uv run python src/figures/figure_le_temoin_de_meme_forme.py \\
        --sortie docs/images/75_le_temoin_de_meme_forme.png
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
MESURE = RACINE / "docs" / "mesures" / "le_temoin_de_meme_forme.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
GRIS = (170, 170, 170)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    t = m["temoin_de_meme_forme"]
    return [
        f"le support publie est un MASQUE et non un seuil : {m['signature_de_masque']['part_de_zero'] * 100:.0f} % "
        f"de zeros, puis un vide de {m['signature_de_masque']['largeur_du_vide_apres_zero']} "
        f"niveaux avant la premiere valeur rendue.",
        f"les {m['reperes']} reperes s'apparient a ses {m['cibles']} vides a "
        f"{m['distance_vraie']:.0f} px, contre {m['temoin_uniforme']:.0f} pour un semis "
        f"uniforme — un rapport de x{m['rapport_a_l_uniforme']} qui semblait probant.",
        f"mais le MEME nuage pose ailleurs fait {t['meilleure']:.0f} px au mieux et "
        f"{t['mediane']:.0f} en mediane : la vraie place est la {m['rang_de_la_pose_vraie']}e "
        f"sur {m['poses_comparees'] + 1}, p = {m['p_de_permutation']}.",
        "le semis uniforme cassait la place ET le groupement ; celui-ci ne casse que la place, "
        "et il montre que le rapport x7,7 etait le groupement, pas une correspondance.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    h, w = m["forme_carte"]
    marge, cote = 40, 470
    ech = cote / max(h, w)
    lp, hp = int(w * ech), int(h * ech)
    xg = marge
    xd = xg + lp + 90
    y0 = 100
    lignes = couper(prose(m), 106)
    L = xd + 420 + marge
    H = y0 + hp + 74 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "La vraie place des reperes n'a rien de particulier",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['reperes']} reperes du masque contre {m['cibles']} vides du support publie, "
             f"a pleine resolution", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             "le temoin garde la GEOMETRIE du nuage et ne casse que sa place",
             fill=DISCRET, font=moyen)

    art.rectangle([xg, y0, xg + lp, y0 + hp], outline=CADRE)
    poses = m.get("poses_echantillon", [])
    for q in poses[:1]:
        for pi, pj in q:
            art.ellipse([xg + pj * ech - 1.4, y0 + pi * ech - 1.4,
                         xg + pj * ech + 1.4, y0 + pi * ech + 1.4], fill=GRIS)
    for pi, pj in m["reperes_xy"]:
        art.ellipse([xg + pj * ech - 1.4, y0 + pi * ech - 1.4,
                     xg + pj * ech + 1.4, y0 + pi * ech + 1.4], fill=AMBRE)
    for ci, cj in m["cibles_xy"]:
        art.ellipse([xg + cj * ech - 5, y0 + ci * ech - 5,
                     xg + cj * ech + 5, y0 + ci * ech + 5], outline=ROUGE, width=2)
    ly = y0 + hp + 10
    for k, (coul, nom, plein) in enumerate(
            ((AMBRE, f"{m['reperes']} reperes, a leur vraie place", True),
             (GRIS, "le meme nuage, une pose du temoin", True),
             (ROUGE, f"{m['cibles']} vides du support", False))):
        if plein:
            art.ellipse([xg, ly + k * 16 + 4, xg + 7, ly + k * 16 + 11], fill=coul)
        else:
            art.ellipse([xg, ly + k * 16 + 3, xg + 8, ly + k * 16 + 11], outline=coul, width=2)
        art.text((xg + 14, ly + k * 16), nom, fill=DISCRET, font=petit)

    # --- la règle des poses ---
    art.text((xd, y0 - 20), "distance mediane d'appariement, en px", fill=TEXTE, font=moyen)
    toutes = m["temoin_de_meme_forme"]["toutes"]
    bas = min(toutes + [m["distance_vraie"]])
    haut = max(toutes + [m["distance_vraie"]])
    marge_r = (haut - bas) * 0.08 or 1.0
    bas, haut = bas - marge_r, haut + marge_r
    rx, rw, ry = xd, 360, y0 + 90

    def place(val):
        return rx + (val - bas) / (haut - bas) * rw

    art.line([rx, ry, rx + rw, ry], fill=CADRE)
    for val in toutes:
        x = place(val)
        art.line([x, ry - 9, x, ry + 9], fill=GRIS, width=2)
    xv = place(m["distance_vraie"])
    art.line([xv, ry - 22, xv, ry + 22], fill=AMBRE, width=3)
    art.text((xv - 16, ry - 40), f"{m['distance_vraie']:.0f}", fill=AMBRE, font=moyen)
    art.text((xv - 30, ry + 26), "la VRAIE place", fill=AMBRE, font=petit)
    art.text((rx - 6, ry + 44), f"{bas:.0f}", fill=DISCRET, font=petit)
    art.text((rx + rw - 24, ry + 44), f"{haut:.0f}", fill=DISCRET, font=petit)
    art.text((rx, ry + 62), f"les {len(toutes)} poses du temoin, en gris",
             fill=DISCRET, font=petit)
    art.text((rx, ry + 78),
             f"rang de la vraie : {m['rang_de_la_pose_vraie']} sur "
             f"{m['poses_comparees'] + 1}   →   p = {m['p_de_permutation']}",
             fill=TEXTE, font=moyen)
    art.text((rx, ry + 100),
             f"le semis uniforme, lui, est a {m['temoin_uniforme']:.0f} px — hors de cette "
             f"regle,", fill=DISCRET, font=petit)
    art.text((rx, ry + 114), "et c'est exactement ce qui le rendait trop facile a battre",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠ Rendu et non affirmé : combien de poses du témoin battent la vraie place. C'est ce que la
    # figure existe pour montrer, donc c'est comptable.
    battent = sum(1 for t in toutes if t < m["distance_vraie"])
    return {"reperes": len(m["reperes_xy"]), "cibles": len(m["cibles_xy"]),
            "poses_dessinees": min(1, len(poses)), "poses_sur_la_regle": len(toutes),
            "poses_qui_battent_la_vraie": battent, "sortie": str(sortie)}


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
    # ⚠⚠⚠ LE RANG DESSINÉ DOIT ÊTRE LE RANG MESURÉ. La règle place la vraie parmi les poses ;
    # si le dossier annonçait un autre rang que celui que les poses donnent, la figure citerait
    # un nombre que son propre dessin contredit.
    battent = sum(1 for t in m["temoin_de_meme_forme"]["toutes"] if t < m["distance_vraie"])
    v("le rang publié est celui que les poses donnent",
      m["rang_de_la_pose_vraie"] == battent + 1,
      f"{m['rang_de_la_pose_vraie']} contre {battent + 1}")
    v("... et la valeur p en découle",
      abs(m["p_de_permutation"] - m["rang_de_la_pose_vraie"]
          / (m["poses_comparees"] + 1)) < 1e-4)
    # ⚠⚠ Et le contrôle qui empêche la figure de raconter une victoire : le témoin uniforme doit
    # être HORS de la règle des poses, sinon « il était trop facile à battre » serait faux.
    v("le témoin uniforme est bien hors de la règle, donc trop facile",
      m["temoin_uniforme"] > max(m["temoin_de_meme_forme"]["toutes"]),
      f"{m['temoin_uniforme']} contre un pire de {m['temoin_de_meme_forme']['pire']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les trois semis sont dessinés",
          r["reperes"] == m["reperes"] and r["cibles"] == m["cibles"]
          and r["poses_dessinees"] == 1,
          f"{r['reperes']} repères, {r['cibles']} cibles, {r['poses_dessinees']} pose")
        v("toutes les poses sont sur la règle",
          r["poses_sur_la_regle"] == m["poses_comparees"], str(r["poses_sur_la_regle"]))
        v("... et des poses battent bien la vraie place, comme la prose le dit",
          r["poses_qui_battent_la_vraie"] >= 1,
          f"{r['poses_qui_battent_la_vraie']} sur {r['poses_sur_la_regle']}")
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
                   default=RACINE / "docs" / "images" / "75_le_temoin_de_meme_forme.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['poses_qui_battent_la_vraie']} poses battent la vraie)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
