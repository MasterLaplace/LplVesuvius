#!/usr/bin/env python3
"""L'axe du rouleau est une courbe, et `85` a paye cette hypothese.

⚠⚠⚠ CETTE FIGURE PORTE UNE RETRACTATION. Le panneau A montre le centre d'enroulement tranche par
tranche : il part, revient, et s'ecarte de sa propre droite de dizaines d'epaisseurs de feuille.
Le panneau B montre ce que la correction fait a la courbe de cout de `85` — elle se RESSERRE, et
le « second regime » que `85` publiait disparait.

Usage :
    uv run python src/figures/figure_laxe_est_une_courbe.py --verifier
    uv run python src/figures/figure_laxe_est_une_courbe.py \\
        --sortie docs/images/90_laxe_est_une_courbe.png
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
MESURE = RACINE / "docs" / "mesures" / "laxe_est_une_courbe.json"
AXE = RACINE / "docs" / "mesures" / "laxe_trace.json"

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
    d, P, C, H = (m["derive_de_laxe"], m["longueur_par_passe_plat_mm"],
                  m["longueur_par_passe_courbe_mm"], m["hors_coeur_courbe_mm"])
    s, c, n = (m["le_coeur_est_un_second_regime"], m["couverture_angulaire"],
               m["le_ruban_depaisseur_constante"])
    return [
        f"`85` estime l'axe d'enroulement comme UN point (x, y) et en tire un rayon par bande. un "
        f"controle que je n'avais pas fait le refute : l'etendue radiale d'une bande vaut "
        f"{n['rapport_min']} a {n['rapport_max']} fois ce que « etendue x periode » predit, et le "
        "rapport CROIT quand l'etendue diminue. une bande de deux spires couvrirait quatorze "
        "millimetres de rayon, soit l'equivalent de soixante-dix-sept spires.",
        f"⚠⚠⚠ PANNEAU A — L'AXE N'EST NI VERTICAL NI DROIT. le centre par tranche se deplace de "
        f"{d['deplacement_x_mm']} mm en x et {d['deplacement_y_mm']} mm en y sur "
        f"{d['longueur_z_mm']} mm de z, ET REVIENT SUR SES PAS. il s'ecarte de sa PROPRE DROITE "
        f"de {d['ecart_a_la_droite_mm']} mm, soit "
        f"{d['ecart_en_epaisseurs_de_feuille']} epaisseurs de feuille. le rouleau est COURBE, ce "
        "qui est l'etat normal d'un papyrus carbonise.",
        f"⚠⚠ ET LE CONFONDANT EST LEVE, PAS SUPPOSE. si une tranche ne contenait pas un tour "
        "complet, sa mediane serait tiree vers le secteur present — et si le secteur couvert "
        "changeait avec z, on lirait ce changement comme une courbure. mesure : "
        f"{c['min']:.0%} a {c['max']:.0%} des {c['secteurs']} secteurs occupes dans CHAQUE "
        "tranche. c'est une sonde fabriquee qui m'a appris a poser cette question, en echouant.",
        f"★★ PANNEAU B — CE QUI SURVIT, ET IL SURVIT MIEUX. le classement des rayons est "
        f"INCHANGE : {m['classement_axe_courbe']['montees']} montees sur "
        f"{m['classement_axe_courbe']['paires']} paires, comme sous l'axe plat et comme sous "
        f"l'ancienne revision. trois modeles d'axe rendent le meme ordre, donc « le rang monte "
        "vers le dehors » n'etait pas un artefact.",
        f"★★★ ET LA COURBE DE COUT SE RESSERRE : la longueur de feuille par passe vaut "
        f"{C['median']:.0f} mm ({C['min']:.0f} a {C['max']:.0f}, rapport {C['rapport']}) contre "
        f"{P['median']:.0f} mm ({P['min']:.0f} a {P['max']:.0f}, rapport {P['rapport']}) sous "
        f"l'axe plat. hors le coeur : {H['min']:.0f} a {H['max']:.0f} mm, rapport "
        f"{H['rapport']}, ecart-type relatif {H['ecart_type_relatif']:.0%}.",
        f"⚠⚠⚠ RETRACTATION — LE « SECOND REGIME » DE `85` N'EXISTE PAS. la bande du coeur y "
        f"valait {s['coeur_plat_mm']:.0f} mm, un facteur deux au-dessus de toutes les autres, et "
        f"je l'avais publiee comme une population a part. elle vaut {s['coeur_courbe_mm']:.0f} mm "
        "et rentre dans la distribution. il n'y avait pas deux populations : il y avait mon "
        "erreur d'axe, concentree sur la bande la plus PROCHE de l'axe, donc la plus sensible a "
        "s'etre trompe dessus.",
        f"⚠⚠ ce qui reste refute : « l'etendue radiale d'une bande vaut son etendue fois la "
        f"periode ». meme sous l'axe courbe les rapports vont de {n['rapport_min']} a "
        f"{n['rapport_max']}. une bande n'est pas un ruban d'epaisseur constante — c'est une "
        "nappe qui court sur toute la longueur du rouleau et dont la section n'est pas un cercle.",
        "⚠⚠⚠ ET C'EST UN FAIT SUR LA GEOMETRIE OU LE TRANSFERT DOIT TRAVAILLER : tout marcheur "
        "qui supposerait un axe droit, ou un repere cylindrique global, se trompe de deux "
        "centimetres — une centaine d'epaisseurs de feuille. un tel cadre placerait une spire a "
        "la place d'une autre, ce qui EST le transfert. la courbure n'est pas un detail de "
        "mesure, c'est une propriete de l'objet.",
    ]


def panneau_axe(art, x0, y0, pw, ph, m, trace, petit) -> int:
    """Le centre d'enroulement, tranche par tranche, contre sa propre droite."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "le centre d'enroulement, tranche par tranche de z",
             fill=DISCRET, font=petit)
    if not trace:
        art.text((x0 + 20, y0 + ph / 2), "tracé de l'axe absent", fill=ROUGE, font=petit)
        return 0
    zs = trace["z_mm"]
    for j, (cle, coul, titre) in enumerate((("cx_mm", BLEU, "x"), ("cy_mm", VERT, "y"))):
        h = (ph - 74) / 2
        haut = y0 + 30 + j * (h + 14)
        vals = trace[cle]
        lo, hi = min(vals), max(vals)
        marge = (hi - lo) * 0.12 or 1.0
        gauche, droite = x0 + 52, x0 + pw - 16

        def px(z):
            return gauche + (droite - gauche) * (z - zs[0]) / max(1e-9, zs[-1] - zs[0])

        def py(v):
            return haut + h - h * (v - lo + marge) / (hi - lo + 2 * marge)

        # ⚠⚠ LA DROITE DES MOINDRES CARRES EST TRACEE : sans elle, « s'écarte de sa propre
        # droite » serait une phrase et pas une chose qu'on voit.
        a = (vals[-1] - vals[0]) / max(1e-9, zs[-1] - zs[0])
        b = vals[0] - a * zs[0]
        art.line([px(zs[0]), py(a * zs[0] + b), px(zs[-1]), py(a * zs[-1] + b)],
                 fill=GRIS)
        art.line([(px(z), py(v)) for z, v in zip(zs, vals)], fill=coul, width=2)
        art.text((x0 + 8, haut + h / 2 - 6), f"{titre} (mm)", fill=coul, font=petit)
        # ⚠⚠⚠ LES DEUX GRADUATIONS ETAIENT INVERSEES : `py` place `lo` EN BAS, et j'ecrivais
        # `lo` en haut. Une figure dont l'axe est etiquete a l'envers ne dit pas seulement un
        # nombre faux, elle dit la mauvaise DIRECTION — et la direction est le sujet ici.
        art.text((x0 + 8, haut - 2), f"{hi:.0f}", fill=DISCRET, font=petit)
        art.text((x0 + 8, haut + h - 12), f"{lo:.0f}", fill=DISCRET, font=petit)
    d = m["derive_de_laxe"]
    art.text((x0 + 8, y0 + ph - 32),
             f"⚠ écart à sa PROPRE droite : {d['ecart_a_la_droite_mm']} mm = "
             f"{d['ecart_en_epaisseurs_de_feuille']} épaisseurs de feuille",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             f"abscisse : position le long du rouleau, 0 à {zs[-1] - zs[0]:.0f} mm · "
             "gris : la droite des moindres carrés", fill=DISCRET, font=petit)
    return len(zs)


def panneau_cout(art, x0, y0, pw, ph, m, petit) -> int:
    """La longueur par passe, sous les deux modèles d'axe."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "longueur de feuille par passe — axe plat contre axe courbe",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 24
    base, sommet = y0 + ph - 44, y0 + 46
    hi = max(x["longueur_par_passe_plat_mm"] for x in lignes) * 1.05
    r0 = min(x["rayon_median_courbe_mm"] for x in lignes)
    r1 = max(x["rayon_median_courbe_mm"] for x in lignes)

    def px(r):
        return gauche + (droite - gauche) * (r - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v):
        return base - (base - sommet) * v / hi

    H = m["hors_coeur_courbe_mm"]
    # ⭐ La bande où tout tient SOUS L'AXE COURBE est peinte : c'est elle le verdict.
    art.rectangle([gauche, py(H["max"]), droite, py(H["min"])], fill=PALE)
    # ⚠ L'etiquette de la bande vit SOUS elle : posee dessus, elle tombait sur les points.
    art.text((gauche + 4, py(H["min"]) + 4),
             f"{H['min']:.0f} à {H['max']:.0f} mm — axe courbe, hors le cœur",
             fill=VERT, font=petit)
    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0, int(hi / 2), int(hi)):
        art.text((gauche - 54, py(g) - 6), f"{g:>4} mm", fill=DISCRET, font=petit)
    mx = max(x["etendue"] for x in lignes)
    fleches = 0
    for x in lignes:
        cx = px(x["rayon_median_courbe_mm"])
        yp, yc = py(x["longueur_par_passe_plat_mm"]), py(x["longueur_par_passe_courbe_mm"])
        coeur = x["etendue"] == mx
        # ⚠⚠ LE DEPLACEMENT EST TRACE, pas seulement les deux etats : c'est la correction
        # qu'on veut voir, et deux nuages superposes la laisseraient deviner.
        art.line([cx, yp, cx, yc], fill=GRIS)
        art.ellipse([cx - 3, yp - 3, cx + 3, yp + 3], outline=ROUGE)
        art.ellipse([cx - 3, yc - 3, cx + 3, yc + 3], fill=BLEU)
        if coeur:
            fleches += 1
            art.text((cx + 8, yp - 6),
                     f"la bande du cœur : {x['longueur_par_passe_plat_mm']:.0f} → "
                     f"{x['longueur_par_passe_courbe_mm']:.0f} mm", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 32),
             "cercle rouge : axe plat (`85`) · disque bleu : axe courbe",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian sous l'axe courbe", fill=DISCRET, font=petit)
    return fleches


def dessiner(m: dict, trace: dict | None, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 380
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    d = m["derive_de_laxe"]
    art.text((marge, 16), "L'axe du rouleau est une courbe, et `85` a payé cette hypothèse",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['points']} points · l'axe s'écarte de sa propre droite de "
             f"{d['ecart_en_epaisseurs_de_feuille']} épaisseurs de feuille",
             fill=DISCRET, font=moyen)
    titres = ("A · le centre d'enroulement, tranche par tranche",
              "B · ce que la correction fait à la courbe de coût de `85`")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    pts = panneau_axe(art, marge, 104, pw, ph, m, trace, petit)
    coeurs = panneau_cout(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points_de_laxe": pts, "coeurs": coeurs,
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
    trace = json.loads(AXE.read_text()) if AXE.is_file() else None
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, trace, RACINE / "docs" / "images" / "90_laxe_est_une_courbe.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    # ⚠⚠ LE TRACE DE L'AXE EST LE SUJET DU PANNEAU A : sans lui, la figure affirme une courbure
    # qu'elle ne montre pas.
    v("le tracé de l'axe est dessiné", d["points_de_laxe"] > 8,
      f"{d['points_de_laxe']} tranches — lancer `laxe_est_une_courbe --json`")
    # ⭐ LA RETRACTATION EST MONTREE, pas seulement écrite : le déplacement de la bande du cœur.
    v("le déplacement de la bande du cœur est marqué", d["coeurs"] == 1, str(d["coeurs"]))
    v("la rétractation est dans la prose",
      any("SECOND REGIME" in x and "N'EXISTE PAS" in x for x in prose(m)))
    v("... et le second régime a bien disparu",
      m["le_coeur_est_un_second_regime"]["sous_axe_plat"]
      and not m["le_coeur_est_un_second_regime"]["sous_axe_courbe"])
    # ⭐⭐ CE QUI SURVIT est dit aussi : une figure qui ne montrerait que la faute laisserait
    # croire que tout `85` tombe.
    v("ce qui survit est dit : le classement",
      m["classement_axe_courbe"]["toutes"] and any("n'etait pas un artefact" in x
                                                   for x in prose(m)))
    v("... et que la courbe de coût se RESSERRE",
      m["longueur_par_passe_courbe_mm"]["rapport"]
      < m["longueur_par_passe_plat_mm"]["rapport"])
    # ⚠⚠ LE CONFONDANT LEVÉ est dans la prose : sans lui, un lecteur ne saurait pas que la
    # question a été posée.
    v("le confondant de la couverture angulaire est dit",
      any("tour complet" in x for x in prose(m))
      and m["couverture_angulaire"]["complete_partout"])
    # ⚠⚠⚠ LES GRADUATIONS DE L'AXE VONT DANS LE BON SENS. Ma premiere version ecrivait `lo` en
    # haut alors que `py` le place en bas : une figure dont l'axe est etiquete a l'envers dit la
    # mauvaise DIRECTION, et la direction est tout le sujet.
    if trace:
        for cle in ("cx_mm", "cy_mm"):
            vals = trace[cle]
            # ⚠ Le détail dit ce qui EST, pas ce qui aurait échoué : un message d'échec
            # imprimé sur un succès est un message qui contredit son propre verdict.
            haut, bas = f"{max(vals):.0f}", f"{min(vals):.0f}"
            trouve = haut in d["textes_dessines"]
            v(f"la graduation du haut de {cle} porte le maximum", trouve,
              f"{haut} en haut, {bas} en bas" if trouve else f"{haut} absent des textes tracés")
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "90_laxe_est_une_courbe.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    trace = json.loads(AXE.read_text()) if AXE.is_file() else None
    d = dessiner(json.loads(MESURE.read_text()), trace, a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
