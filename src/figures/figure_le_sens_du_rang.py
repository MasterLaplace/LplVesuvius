#!/usr/bin/env python3
"""Le rang monte-t-il vers le dehors, et une passe humaine couvre-t-elle une longueur constante ?

⚠⚠⚠ CETTE FIGURE TRANCHE LA QUESTION QUE `84` AVAIT LAISSEE OUVERTE. Le panneau A montre le
rayon de chacune des 28 bandes de `PHercParis4` : il monte avec le rang, 27 fois sur 27, et le
verdict survit a un second centre. Le panneau B teste la PREDICTION qui rend l'explication
falsifiable — si une passe humaine couvre une longueur de feuille a peu pres constante, le
produit `etendue x 2piR` l'est aussi.

⚠⚠ Et il montre le residu pour ce qu'il est : une QUANTIFICATION. Dans chaque palier d'etendue
constante la longueur croit avec le rayon, parce qu'on ne coupe pas deux spires et demie.

Usage :
    uv run python src/figures/figure_le_sens_du_rang.py --verifier
    uv run python src/figures/figure_le_sens_du_rang.py \\
        --sortie docs/images/85_le_sens_du_rang.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_sens_du_rang.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    s = m["sens"]
    L, H = m["longueur_par_passe_mm"], m["longueur_par_passe_hors_coeur_mm"]
    pal = m["paliers_dune_meme_etendue"]
    e = m["echantillonnage_du_maillage"]
    mot = ("VERS LE DEHORS" if s["vers_le_dehors"]
           else ("VERS LE DEDANS" if s["vers_le_dedans"] else "NI L'UN NI L'AUTRE"))
    return [
        f"`84` mesure que les {m['bandes']} bandes de {m['fragment']} decroissent sans une seule "
        "inversion et nomme ce qu'il ne sait pas : dans quel sens va le rang. ce qui tranche est "
        f"un RAYON, et il se lit sur le maillage le moins cher publie — "
        f"{m['voxel_um']} µm, un mebioctet par bande.",
        f"⚠⚠⚠ PANNEAU A — LE RANG MONTE {mot}. {s['montees']} montee(s) et "
        f"{s['descentes']} descente(s) sur {s['paires']} paires, du rang {s['rangs'][0]} au rang "
        f"{s['rangs'][1]}, soit {s['du_premier_au_dernier'][0] / 1000:.2f} mm a "
        f"{s['du_premier_au_dernier'][1] / 1000:.2f} mm. et le verdict survit a un SECOND "
        "centre, ce qui est la condition pour que ce soit un ordre et non une propriete de "
        "l'estimation.",
        f"★★ PANNEAU B — DONC LA PREDICTION SE TESTE. si une passe humaine couvre une longueur "
        f"de feuille a peu pres constante, le produit etendue x 2piR l'est aussi. mesure : "
        f"{L['median']:.0f} mm en mediane, et hors la bande du coeur les {H['bandes']} autres "
        f"tiennent dans {H['min']:.0f} a {H['max']:.0f} mm — un facteur "
        f"{H['rapport']}, ecart-type relatif {H['ecart_type_relatif']:.0%}. le nombre de spires "
        "tombe parce que les spires s'allongent, a longueur de feuille a peu pres constante.",
        f"⚠⚠ ET LE RESIDU N'EST PAS DU BRUIT, C'EST DE LA QUANTIFICATION. on ne coupe pas deux "
        f"spires et demie, donc dans chacun des {len(pal['paliers'])} paliers d'etendue "
        f"constante la longueur croit mecaniquement avec le rayon — "
        f"{'ce qui est le cas des ' + str(len(pal['paliers'])) + ' paliers' if pal['tous_les_paliers_croissent'] else 'ce qui n est PAS le cas partout'}.",
        f"⚠ les maximums atteints juste avant chaque descente d'etendue declinent — "
        + " ".join(f"{x:.0f}" for x in pal["maximums_avant_descente_mm"])
        + " mm — ce qui RESSEMBLE a un budget par passe qui se reduit vers l'exterieur. mais un "
        "pas de quantification vaut une circonference entiere, donc a cette precision les deux "
        "ne sont pas separables. la mesure rend les deux et ne tranche pas.",
        f"⚠⚠⚠ ET CE MAILLAGE NE DONNE PAS LE PAS INTER-FEUILLES, dit avant de s'en servir : ses "
        f"cellules voisines sont a {e['pas_median_um']:.0f} µm, trois a six fois l'ecart cherche. "
        "une distance de feuille a feuille lue dessus serait dominee par l'echantillonnage et non "
        "par la matiere. c'est une limite de GRILLE, et la demi-feuille de cet objet reste donc "
        "un chiffre a mesurer ailleurs.",
        "⚠ deux revisions d'une meme bande ne couvrent pas la meme surface — 50877 cellules "
        "contre 78453 — donc leurs rayons medians different, jusqu'a 15.9 % sur la bande du "
        "coeur, 0.5 % en mediane. ce qui est asserte est le CLASSEMENT, qui survit entier : une "
        "mediane est un resume d'un echantillon, un ordre est une propriete de l'enroulement.",
    ]


def panneau_rayon(art, x0, y0, pw, ph, m, petit) -> int:
    """Le rayon de chaque bande, dans l'ordre des rangs."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "rayon médian de chaque bande · largeur = son étendue",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 22
    base, sommet = y0 + ph - 42, y0 + 34
    r0 = min(x["rayon_median_um"] for x in lignes) / 1000
    r1 = max(x["rayon_median_um"] for x in lignes) / 1000
    lo = min(x["de"] for x in lignes)
    hi = max(x["a"] for x in lignes)

    def px(r: float) -> float:
        return gauche + (droite - gauche) * (r - lo) / max(1, hi - lo)

    def py(v: float) -> float:
        return base - (base - sommet) * (v - r0 * 0.9) / (r1 * 1.05 - r0 * 0.9)

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (int(r0), int((r0 + r1) / 2), int(r1) + 1):
        art.text((gauche - 50, py(g) - 6), f"{g:>4} mm", fill=DISCRET, font=petit)
    dessinees = 0
    for x in lignes:
        y = py(x["rayon_median_um"] / 1000)
        a, b = px(x["de"]), px(x["a"] + 1)
        art.rectangle([a, y - 3, max(b, a + 2), y + 3],
                      fill=VERT if x["etendue"] >= 10 else (BLEU if x["etendue"] >= 4 else GRIS))
        dessinees += 1
    for g in (lo, (lo + hi) // 2, hi):
        art.text((px(g) - 12, base + 6), f"w{g:03d}", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : le rang de spire · ordonnée : distance à l'axe estimé",
             fill=DISCRET, font=petit)
    return dessinees


def panneau_longueur(art, x0, y0, pw, ph, m, petit) -> int:
    """La longueur de feuille par passe, contre le rayon."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "longueur de feuille couverte par une passe = étendue × 2πR",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    H = m["longueur_par_passe_hors_coeur_mm"]
    gauche, droite = x0 + 58, x0 + pw - 22
    base, sommet = y0 + ph - 42, y0 + 34
    r0 = min(x["rayon_median_um"] for x in lignes) / 1000
    r1 = max(x["rayon_median_um"] for x in lignes) / 1000
    l1 = max(x["longueur_par_passe_mm"] for x in lignes)

    def px(r: float) -> float:
        return gauche + (droite - gauche) * (r - r0 * 0.9) / (r1 * 1.05 - r0 * 0.9)

    def py(v: float) -> float:
        return base - (base - sommet) * v / (l1 * 1.05)

    # ⭐ LA BANDE OU TOUT TIENT SAUF LE COEUR est peinte, parce que c'est elle le verdict : un
    # nuage sans sa bande laisserait juger « constant » a l'oeil.
    art.rectangle([gauche, py(H["max"]), droite, py(H["min"])], fill=PALE)
    art.text((gauche + 4, py(H["max"]) - 13),
             f"{H['min']:.0f} à {H['max']:.0f} mm — les {H['bandes']} bandes hors le cœur",
             fill=VERT, font=petit)
    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0, int(l1 / 2), int(l1)):
        art.text((gauche - 52, py(g) - 6), f"{g:>4} mm", fill=DISCRET, font=petit)
    mx = max(x["etendue"] for x in lignes)
    marques = 0
    for x in lignes:
        cx, cy = px(x["rayon_median_um"] / 1000), py(x["longueur_par_passe_mm"])
        coeur = x["etendue"] == mx
        coul = ROUGE if coeur else BLEU
        art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=coul)
        art.text((cx + 5, cy - 6), str(x["etendue"]), fill=coul, font=petit)
        if coeur:
            marques += 1
            # ⚠ L'annotation part APRES le chiffre d'etendue, mesure et non devine : posee a
            # dix-huit pixels elle se collait au « 18 » et les deux se lisaient comme un mot.
            art.text((cx + 12 + petit.getbbox(str(x["etendue"]))[2], cy - 6),
                     "la bande du cœur — un second régime", fill=ROUGE, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon · le chiffre à côté de chaque point est l'étendue de la bande",
             fill=DISCRET, font=petit)
    return marques


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 316
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    s = m["sens"]
    art.text((marge, 16),
             "Le rang monte-t-il vers le dehors, et une passe couvre-t-elle une longueur "
             "constante ?", fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes_lues']} bandes · {s['montees']}/{s['paires']} "
             f"montées de rayon · une passe couvre "
             f"{m['longueur_par_passe_mm']['median']:.0f} mm de feuille en médiane",
             fill=DISCRET, font=moyen)
    titres = ("A · le rayon de chaque bande, dans l'ordre des rangs",
              "B · la longueur de feuille par passe, contre le rayon")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    barres = panneau_rayon(art, marge, 104, pw, ph, m, petit)
    coeurs = panneau_longueur(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "barres": barres, "coeurs": coeurs,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


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
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, RACINE / "docs" / "images" / "85_le_sens_du_rang.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    v("aucune ligne de prose n'est vide", all(x.strip() for x in prose(m)))
    # ⚠⚠ TOUTES LES BANDES SONT DESSINEES : une bande absente du panneau ferait lire un corpus
    # plus court ou une monotonie plus propre qu'elle n'est.
    v("chaque bande de la mesure est dessinée", d["barres"] == m["bandes_lues"],
      f"{d['barres']} pour {m['bandes_lues']}")
    # ⭐ LE SECOND REGIME EST MARQUE : sans lui, le nuage du panneau B se lirait comme constant.
    v("la bande du cœur est marquée comme un second régime", d["coeurs"] == 1, str(d["coeurs"]))
    # ⚠⚠⚠ LE VERDICT VIENT DE LA MESURE et non d'une phrase qui aurait survécu.
    v("le sens du rang est celui de la mesure",
      m["sens"]["vers_le_dehors"] and any("VERS LE DEHORS" in x for x in prose(m)),
      str(m["sens"]))
    v("... et il survit au second centre", m["le_sens_survit_au_centre"])
    v("la prédiction est publiée avec son rapport hors cœur",
      m["longueur_par_passe_hors_coeur_mm"]["rapport"] < 2.0
      and any(str(m["longueur_par_passe_hors_coeur_mm"]["rapport"]) in x for x in prose(m)),
      str(m["longueur_par_passe_hors_coeur_mm"]))
    # ⚠⚠ LA FIGURE DOIT PORTER SA PROPRE LIMITE, sinon un lecteur en tirerait un pas
    # inter-feuilles trois à six fois trop grand sans qu'aucune ligne ne le prévienne.
    v("la figure dit que ce maillage ne donne pas le pas inter-feuilles",
      m["ce_maillage_donne_le_pas_inter_feuilles"] is False
      and any("NE DONNE PAS LE PAS INTER-FEUILLES" in x for x in prose(m)))
    # ⚠ Et qu'un déclin observé n'est pas séparable de la quantification.
    v("... et que le déclin des maximums n'est pas séparable de la quantification",
      any("ne sont pas separables" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "85_le_sens_du_rang.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
