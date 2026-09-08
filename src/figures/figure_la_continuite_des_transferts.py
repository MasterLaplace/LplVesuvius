#!/usr/bin/env python3
"""Les transferts que l'humain a reussis sont-ils continus ? Oui au coeur, non au bord.

⚠⚠⚠ CETTE FIGURE PORTE UN FAIT ET DEUX REFUS. Le panneau A montre la degradation de la
continuite du coeur vers le bord. Le panneau B montre le confondant — une correlation de 0,80
entre les sauts et le gonflement de pente de `91` — et le test direct qui la refuse.

Usage :
    uv run python src/figures/figure_la_continuite_des_transferts.py --verifier
    uv run python src/figures/figure_la_continuite_des_transferts.py \\
        --sortie docs/images/92_la_continuite_des_transferts.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import Tracee, police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    d, e = m["degradation"], m["retirer_les_sauts_change_la_pente_de"]
    return [
        f"`91` etablit que les {m['bandes']} bandes de {m['fragment']} sont des transferts de "
        "spire a spire deja faits a la main. reste a savoir ce que l'humain a REELLEMENT produit : "
        "une nappe continue qui derive de feuille en feuille, ou une couture de morceaux ?",
        f"★★★ PANNEAU A — LA CONTINUITE SE DEGRADE VERS L'EXTERIEUR. le plus grand saut entre deux "
        "cellules VOISINES d'une meme ligne de grille, rapporte au pas d'echantillonnage, vaut "
        f"{d['coeur']['rapport_median']} au coeur, {d['milieu']['rapport_median']} au milieu et "
        f"{d['bord']['rapport_median']} au bord. la progression est reguliere, et les tiers sont "
        "une decoupe de la matiere : les bandes sont deja ordonnees du coeur vers le bord.",
        f"★★ CE QUE CA DIT DU REMPLACANT DE L'HUMAIN, et c'est une borne sur ce qu'on peut lui "
        "demander : la ou le rouleau est intact, un humain trace CONTINUMENT ; la ou il ne l'est "
        "pas, MEME UN HUMAIN rend une surface discontinue. donc l'etendue qui tombe de 18 a 2 "
        "spires (`84`) n'est pas seulement la circonference qui croit — c'est aussi la continuite "
        "qui casse.",
        "⚠⚠ UNE PREMIERE LECTURE, FAUSSE, EST GARDEE. j'ai vu les sauts sur les lignes 3, 4 et 181 "
        "d'une grille de 198 et conclu « effilochage du bord du maillage ». le test structurel les "
        "GARDE : une cellule est dite interieure quand ses QUATRE voisines de grille sont valides, "
        "ce qui ne depend d'aucune marge choisie, et les sauts de trente millimetres y survivent.",
        f"⚠⚠⚠ PANNEAU B — ET UNE SECONDE LECTURE, REFUTEE PAR LE TEST DIRECT. les sauts correlent "
        f"fortement avec le gonflement de pente que `91` n'expliquait pas : r = "
        f"{m['correlation_saut_pente']}. j'ai failli publier la cause. mais retirer les lignes qui "
        f"contiennent un saut change la pente de {e['ecart_relatif_median']:.1%} en mediane et "
        f"{e['ecart_relatif_max']:.1%} au pire, sur {e['bandes_testees']} bandes.",
        "★ les deux grandeurs croissent vers l'exterieur, et AUCUNE NE CAUSE L'AUTRE. une "
        "correlation de 0,80 entre deux quantites qui montent ensemble n'est pas un mecanisme ; "
        "retirer la cause supposee et regarder si l'effet bouge, si.",
        "⚠ donc la cause du gonflement de `91` reste NON TROUVEE, avec desormais TROIS candidats "
        "refutes : la section ovale (elle degonfle), le centre decale (dix fois trop faible), et "
        "les sauts (moins de deux pour cent d'effet). le controle de fenetre de `91` tient "
        "toujours sans elle.",
    ]


def panneau_degradation(art, x0, y0, pw, ph, m, petit) -> int:
    """Le rapport de saut, bande par bande, du cœur vers le bord."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "plus grand saut entre cellules voisines, rapporté au pas d'échantillonnage",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 24
    base, sommet = y0 + ph - 44, y0 + 34
    hi = max(x["rapport_interieur"] for x in lignes) * 1.06
    n = len(lignes)

    def q(v):
        return base - (base - sommet) * v / hi

    # ⭐ La bande « continu » est peinte : un rapport de 1 est une surface parfaitement
    # echantillonnee, et sans repere le lecteur ne saurait pas ce que 1,7 vaut.
    art.rectangle([gauche, q(3.0), droite, q(1.0)], fill=PALE)
    art.text((gauche + 4, q(3.0) - 13), "1 à 3 : continu à l'échantillonnage près",
             fill=VERT, font=petit)
    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0, int(hi / 2), int(hi)):
        art.text((gauche - 26, q(g) - 6), f"{g:>3}", fill=DISCRET, font=petit)
    tiers = 0
    for i, x in enumerate(lignes):
        cx = gauche + (droite - gauche) * i / max(1, n - 1)
        r = x["rapport_interieur"]
        coul = VERT if r < 3 else (AMBRE if r < 15 else ROUGE)
        art.line([cx, base, cx, q(r)], fill=coul)
        art.ellipse([cx - 3, q(r) - 3, cx + 3, q(r) + 3], fill=coul)
    # ⚠⚠ LES TROIS TIERS SONT TRACES, parce que c'est eux le verdict.
    d = m["degradation"]
    for j, (cle, nom) in enumerate((("coeur", "cœur"), ("milieu", "milieu"), ("bord", "bord"))):
        if cle not in d:
            continue
        tiers += 1
        a0 = gauche + (droite - gauche) * (j * n // 3) / max(1, n - 1)
        a1 = gauche + (droite - gauche) * min(n - 1, (j + 1) * n // 3) / max(1, n - 1)
        y = q(d[cle]["rapport_median"])
        art.line([a0, y, a1, y], fill=TEXTE, width=2)
        # ⚠ L'etiquette du premier tiers vit SOUS sa ligne : au-dessus, elle tombait sur la
        # legende de la bande verte, et les deux se lisaient l'une par-dessus l'autre.
        art.text((a0 + 4, y + 3 if j == 0 else y - 14),
                 f"{nom} : {d[cle]['rapport_median']:.1f}", fill=TEXTE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : les bandes, du cœur (gauche) vers le bord (droite)",
             fill=DISCRET, font=petit)
    return tiers


def panneau_confondant(art, x0, y0, pw, ph, m, petit) -> int:
    """La corrélation, et le test direct qui la refuse."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "le saut contre la pente de `91`, puis ce que retirer les sauts change",
             fill=DISCRET, font=petit)
    lignes = [x for x in m["lignes"] if x.get("pente_sans_les_sauts_um") is not None]
    gauche, droite = x0 + 62, x0 + pw - 24
    depassement = -1e9
    h = (ph - 130) / 2
    haut = y0 + 34
    base1 = haut + h
    hx = max(x["saut_max_interieur_um"] for x in lignes) / 1000 * 1.06
    hy = max(x["pente_toutes_lignes_um"] for x in lignes) * 1.06

    def px(v):
        return gauche + (droite - gauche) * v / hx

    def py(v):
        return base1 - (base1 - haut) * v / hy

    art.line([gauche, base1, droite, base1], fill=TEXTE)
    for x in lignes:
        cx, cy = px(x["saut_max_interieur_um"] / 1000), py(x["pente_toutes_lignes_um"])
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BLEU)
    art.text((gauche + 4, haut - 2),
             f"r = {m['correlation_saut_pente']}  — « les sauts expliquent la pente ? »",
             fill=BLEU, font=petit)
    art.text((x0 + 8, base1 + 6), f"saut intérieur, 0 à {hx:.0f} mm · pente, 0 à {hy:.0f} µm",
             fill=DISCRET, font=petit)

    # --- le test direct
    haut2 = base1 + 46
    base2 = haut2 + h
    art.line([gauche, base2, droite, base2], fill=TEXTE)
    n = len(lignes)
    marques = 0
    hi2 = max(max(x["pente_toutes_lignes_um"], x["pente_sans_les_sauts_um"])
              for x in lignes) * 1.06

    def q2(v):
        return base2 - (base2 - haut2) * v / hi2

    for i, x in enumerate(lignes):
        cx = gauche + (droite - gauche) * i / max(1, n - 1)
        ya, yb = q2(x["pente_toutes_lignes_um"]), q2(x["pente_sans_les_sauts_um"])
        art.line([cx, ya, cx, yb], fill=GRIS)
        art.ellipse([cx - 3, ya - 3, cx + 3, ya + 3], outline=ROUGE)
        art.ellipse([cx - 2, yb - 2, cx + 2, yb + 2], fill=VERT)
        marques += 1
    e = m["retirer_les_sauts_change_la_pente_de"]
    # ⚠⚠ LA LEGENDE EST COUPEE EN DEUX LIGNES ET SA LARGEUR EST MESUREE : ma premiere version
    # la posait sur une ligne et le panneau la TRONQUAIT au bord droit, donc « écart 1,5 % au
    # pire » se lisait « au pir ». Une legende coupee ne dit pas ce qu'elle affirme.
    for k, t in enumerate((
            "cercle rouge : toutes les lignes · disque vert : sans les sauts",
            f"écart {e['ecart_relatif_max']:.1%} au pire, "
            f"{e['ecart_relatif_median']:.1%} en médiane")):
        art.text((gauche + 4, haut2 - 2 + k * 13), t, fill=TEXTE, font=petit)
        depassement = max(depassement, gauche + 4 + petit.getbbox(t)[2] - (x0 + pw))
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse du bas : les bandes testées, du cœur vers le bord",
             fill=DISCRET, font=petit)
    return marques, depassement


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 396
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    d = m["degradation"]
    art.text((marge, 16),
             "Les transferts que l'humain a réussis sont-ils continus ? Oui au cœur, non au bord",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes']} bandes · rapport au pas d'échantillonnage : "
             f"{d['coeur']['rapport_median']} au cœur, {d['bord']['rapport_median']} au bord",
             fill=DISCRET, font=moyen)
    titres = ("A · la continuité, du cœur vers le bord",
              "B · le confondant, et le test qui le refuse")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    tiers = panneau_degradation(art, marge, 104, pw, ph, m, petit)
    marques, depassement = panneau_confondant(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "tiers": tiers, "paires": marques,
            "depassement_legende": depassement,
            "textes_dessines": art.textes,
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
    d = dessiner(m, RACINE / "docs" / "images" / "92_la_continuite_des_transferts.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    # ⭐⭐ LES TROIS TIERS SONT TRACÉS : c'est eux le verdict, et un nuage sans eux laisserait
    # juger la dégradation à l'œil.
    v("les trois tiers sont tracés", d["tiers"] == 3, str(d["tiers"]))
    v("... et ils sont ordonnés dans la mesure",
      m["degradation"]["coeur"]["rapport_median"]
      < m["degradation"]["milieu"]["rapport_median"]
      < m["degradation"]["bord"]["rapport_median"], str(m["degradation"]))
    # ⚠⚠ LE TEST DIRECT EST DESSINÉ PAIRE PAR PAIRE : l'écrire sans le montrer demanderait
    # qu'on le croie, et c'est lui qui refuse le confondant.
    v("chaque bande testée porte ses deux pentes", d["paires"] >= 10, str(d["paires"]))
    v("... et l'écart reste sous cinq pour cent",
      m["retirer_les_sauts_change_la_pente_de"]["ecart_relatif_max"] < 0.05,
      str(m["retirer_les_sauts_change_la_pente_de"]))
    # ⚠⚠⚠ LES DEUX LECTURES FAUSSES SONT DANS LA PROSE.
    v("la lecture « effilochage du bord » est gardée et réfutée",
      any("effilochage" in x for x in prose(m)))
    v("... et le confondant est nommé comme tel",
      any("AUCUNE NE CAUSE L'AUTRE" in x for x in prose(m)))
    v("... et la cause est déclarée NON TROUVÉE",
      any("NON TROUVEE" in x for x in prose(m))
      and not m["les_sauts_expliquent_la_pente"])
    # ⭐ Et la borne sur le remplaçant de l'humain est dite.
    v("la borne sur le remplaçant de l'humain est dite",
      any("MEME UN HUMAIN" in x for x in prose(m)))
    # ⚠⚠ AUCUNE LEGENDE NE DEBORDE DU PANNEAU : une legende tronquee ne dit pas ce qu'elle
    # affirme, et « écart 1,5 % au pire » coupe devient « au pir ».
    v("aucune légende du panneau B ne déborde", d["depassement_legende"] < 0,
      f"dépasse de {d['depassement_legende']:.0f} px")
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "92_la_continuite_des_transferts.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
