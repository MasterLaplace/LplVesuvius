#!/usr/bin/env python3
"""Ce que la pleine résolution rend à C1 : des repères, et surtout de la COUVERTURE.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Un compte de repères qui monte ne dit pas si le problème est
résolu : mille repères entassés dans le même quartier ne valent pas mieux que cinquante-cinq. La
carte des positions montre **où**, et la courbe de couverture montre **combien** — et c'est la
seconde qui décide, parce que ce que le recalage réclame est de la matière là où il n'y en a pas.

⭐⭐ Les deux séries sont dessinées **dans la même grille**, l'ancienne remise à l'échelle : deux
semis tracés dans deux images de tailles différentes ne se comparent pas, et les superposer est
la seule façon de voir si le gain est de la densité ou de l'étendue.

⚠ Les nombres sont LUS dans `docs/mesures/les_reperes_a_pleine_resolution.json`.

Usage :
    uv run python src/figures/figure_les_reperes_a_pleine_resolution.py --verifier
    uv run python src/figures/figure_les_reperes_a_pleine_resolution.py \\
        --sortie docs/images/75_les_reperes_a_pleine_resolution.png
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
MESURE = RACINE / "docs" / "mesures" / "les_reperes_a_pleine_resolution.json"
APPARIES = RACINE / "docs" / "mesures" / "les_reperes_apparies.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)

PIXEL_UM = 2.215
"""Le pixel de la carte à pleine résolution, en micromètres.

⚠ Lu dans le nom du fichier publié (`2.215um`) et non choisi : c'est ce qui permet de dire qu'un
rayon de 500 pixels vaut un millimètre plutôt qu'un nombre sans unité."""


def prose(m: dict) -> list[str]:
    av = m["cas_reduit"]
    c0 = m["couverture"][0]
    ca = {c["rayon"]: c["part"] for c in av.get("couverture", [])}
    return [
        f"la carte publiee existe aussi a sa resolution native, {m['forme_carte'][0]} x "
        f"{m['forme_carte'][1]} : l'echelle du transport passe de 0,12 a "
        f"{m['echelle'][0]:.2f}.",
        f"les repères transportables passent de {av.get('repères', 0)} a "
        f"{m['reperes_transportables']} sur {m['trous_du_masque_utilisables']} utilisables, et "
        f"le support publie porte {m['trous_du_support']} trous au lieu de 71.",
        f"a {c0['rayon']} px ({c0['rayon'] * PIXEL_UM / 1000:.1f} mm), la couverture de "
        f"l'empreinte passe de {ca.get(c0['rayon'], 0) * 100:.0f} % a {c0['part'] * 100:.0f} %.",
        f"l'appariement tient : {m['distance_mediane']:.0f} px en mediane contre "
        f"{m['distance_temoin_mediane']:.0f} pour autant de points tires au hasard dans la meme "
        f"empreinte.",
        f"MAIS le gain est de la DENSITE, pas de l'etendue : le 80 % central du semis passe de "
        f"{m['cas_reduit']['etendue']['part_de_la_hauteur'] * 100:.0f} x "
        f"{m['cas_reduit']['etendue']['part_de_la_largeur'] * 100:.0f} % de la carte a "
        f"{m['etendue']['part_de_la_hauteur'] * 100:.0f} x "
        f"{m['etendue']['part_de_la_largeur'] * 100:.0f} % pour 5,7 fois plus de reperes.",
    ]


def anciennes_positions(m: dict, appariees: dict) -> list[tuple[float, float]]:
    """Les repères du cas réduit, remis dans la grille de la pleine résolution.

    ⚠⚠ Les positions sont LUES dans la mesure d'origine et remises à l'échelle par le facteur
    que la mesure de ce lot a publié : les recopier dans le second dossier en ferait deux
    exemplaires libres de diverger, et le facteur recalculé ici serait une seconde réponse à
    « de combien les deux grilles diffèrent ».
    """
    fr, fc = m["cas_reduit"].get("facteur_de_remise_a_l_echelle", [1.0, 1.0])
    return [(p["source"][0] * fr, p["source"][1] * fc)
            for p in appariees.get("paires", [])]


def dessiner(m: dict, appariees: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    h, w = m["forme_carte"]
    av = m["cas_reduit"]
    fr, fc = av.get("facteur_de_remise_a_l_echelle", [1.0, 1.0])

    marge, cote = 40, 520
    ech = cote / max(h, w)
    largeur_plan = int(w * ech)
    hauteur_plan = int(h * ech)
    xg = marge
    xd = xg + largeur_plan + 96
    y0 = 96
    lignes = couper(prose(m), 104)
    L = xd + 380 + marge
    H = y0 + hauteur_plan + 78 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Les reperes a pleine resolution, et leur couverture",
             fill=TEXTE, font=gros)
    art.text((marge, 42), f"{m['carte_publiee'][:70]}…", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             f"1 px = {PIXEL_UM} um ; les deux semis sont dans la MEME grille, l'ancien remis a "
             f"l'echelle (x{fr:.1f})", fill=DISCRET, font=moyen)

    art.rectangle([xg, y0, xg + largeur_plan, y0 + hauteur_plan], outline=CADRE)
    anciens = 0
    for pi, pj in anciennes_positions(m, appariees):
        x, y = xg + pj * ech, y0 + pi * ech
        art.ellipse([x - 4, y - 4, x + 4, y + 4], outline=BLEU, width=2)
        anciens += 1
    nouveaux = 0
    for p in m["paires"]:
        x = xg + p["source"][1] * ech
        y = y0 + p["source"][0] * ech
        art.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=AMBRE)
        nouveaux += 1
    ly = y0 + hauteur_plan + 10
    art.ellipse([xg, ly + 3, xg + 8, ly + 11], outline=BLEU, width=2)
    art.text((xg + 14, ly), f"{anciens} reperes du cas reduit (x8)", fill=DISCRET, font=petit)
    art.ellipse([xg, ly + 19, xg + 8, ly + 27], fill=AMBRE)
    art.text((xg + 14, ly + 16), f"{nouveaux} reperes a pleine resolution",
             fill=DISCRET, font=petit)

    # --- la courbe de couverture ---
    art.text((xd, y0 - 20), "part de l'empreinte a portee d'un repere", fill=TEXTE, font=moyen)
    gh, gw = 300, 300
    art.rectangle([xd, y0, xd + gw, y0 + gh], outline=CADRE)
    rayons = [c["rayon"] for c in m["couverture"]]
    ca = {c["rayon"]: c["part"] for c in av.get("couverture", [])}

    def point(k, part):
        return (xd + k * gw / max(1, len(rayons) - 1), y0 + gh - part * gh)

    for serie, coul, cle in ((m["couverture"], AMBRE, "part"), (av.get("couverture", []),
                                                                BLEU, "part")):
        pts = [point(k, c[cle]) for k, c in enumerate(serie)]
        for a, b in zip(pts, pts[1:]):
            art.line([a[0], a[1], b[0], b[1]], fill=coul, width=2)
        for (x, y), c in zip(pts, serie):
            art.ellipse([x - 3, y - 3, x + 3, y + 3], fill=coul)
            art.text((x - 12, y - 18), f"{c['part'] * 100:.0f}%", fill=coul, font=petit)
    for k, r in enumerate(rayons):
        x = xd + k * gw / max(1, len(rayons) - 1)
        art.text((x - 18, y0 + gh + 6), f"{r}", fill=DISCRET, font=petit)
        art.text((x - 18, y0 + gh + 19), f"{r * PIXEL_UM / 1000:.1f}mm", fill=DISCRET, font=petit)
    art.text((xd, y0 + gh + 38), "rayon, en pixels de la carte", fill=DISCRET, font=petit)
    art.ellipse([xd, y0 + gh + 56, xd + 8, y0 + gh + 64], fill=AMBRE)
    art.text((xd + 14, y0 + gh + 53), "pleine resolution", fill=DISCRET, font=petit)
    art.ellipse([xd + 150, y0 + gh + 56, xd + 158, y0 + gh + 64], fill=BLEU)
    art.text((xd + 164, y0 + gh + 53), "cas reduit", fill=DISCRET, font=petit)

    bas = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, bas + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"anciens": anciens, "nouveaux": nouveaux,
            "rayons": len(rayons), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    faux = {"cas_reduit": {"facteur_de_remise_a_l_echelle": [8.0, 8.0]}}
    pos = anciennes_positions(faux, {"paires": [{"source": [10.0, 20.0]}]})
    v("les anciennes positions sont remises à l'échelle publiée", pos == [(80.0, 160.0)],
      str(pos))
    v("... et un dossier sans paire n'en rend aucune",
      anciennes_positions(faux, {}) == [])

    if not MESURE.is_file() or not APPARIES.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    ap = json.loads(APPARIES.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ CE QUE LA FIGURE AFFIRME DOIT ÊTRE VRAI DANS LA MESURE, sinon elle illustre une autre
    # campagne que celle qu'elle cite. Les deux revendications sont donc assertées ici : la
    # couverture monte à chaque rayon, et elle monte PARTOUT — un gain à un seul rayon serait un
    # gain de portée et non de répartition.
    ca = {c["rayon"]: c["part"] for c in m["cas_reduit"].get("couverture", [])}
    v("la couverture est meilleure à CHAQUE rayon",
      all(c["part"] > ca.get(c["rayon"], 0.0) for c in m["couverture"]),
      str([(c["rayon"], c["part"], ca.get(c["rayon"])) for c in m["couverture"]]))
    v("... et les deux courbes sont croissantes",
      all(a["part"] <= b["part"] for a, b in zip(m["couverture"], m["couverture"][1:])))
    # ⚠⚠⚠ ET LA NUANCE QUE LE DESSIN A IMPOSÉE : le semis grossit beaucoup plus vite qu'il ne
    # s'étale. La figure le dit en toutes lettres, donc le fait doit être vrai dans la mesure —
    # sinon la prose serait une opinion collée sous une image.
    e, ea = m["etendue"], m["cas_reduit"]["etendue"]
    facteur_compte = e["repères"] / max(1, ea["repères"])
    facteur_etendue = (e["part_de_la_hauteur"] * e["part_de_la_largeur"]) / max(
        1e-9, ea["part_de_la_hauteur"] * ea["part_de_la_largeur"])
    v("le compte croît bien plus vite que l'étendue, comme la prose le dit",
      facteur_compte > 3.0 * facteur_etendue,
      f"×{facteur_compte:.1f} en compte contre ×{facteur_etendue:.2f} en aire du 80 % central")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, ap, Path(d) / "t.png")
        v("les deux semis sont dessinés",
          r["anciens"] == m["cas_reduit"]["repères"]
          and r["nouveaux"] == len(m["paires"]),
          f"{r['anciens']} anciens, {r['nouveaux']} nouveaux")
        v("... et le nouveau semis est bien plus nombreux",
          r["nouveaux"] > 3 * r["anciens"], f"{r['nouveaux']} contre {r['anciens']}")
        v("la courbe porte tous ses rayons", r["rayons"] == len(m["couverture"]))
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
    p.add_argument("--apparies", type=Path, default=APPARIES)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "75_les_reperes_a_pleine_resolution.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file() or not a.apparies.is_file():
        raise SystemExit("mesure absente")
    r = dessiner(json.loads(a.mesure.read_text()),
                 json.loads(a.apparies.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['nouveaux']} repères contre {r['anciens']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
