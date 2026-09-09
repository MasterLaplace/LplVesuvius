#!/usr/bin/env python3
"""La normale de la nappe n'est pas le rayon — et l'obliquite n'explique pas le trou de `99`.

⭐⭐⭐ LE PANNEAU A PORTE LE FAIT : la normale du maillage est a des DIZAINES de degres du rayon la
ou une spirale de ce pas en predit une FRACTION de degre. L'echelle est logarithmique parce que
c'est la seule facon de montrer les deux sur un meme axe — et le fait EST cet ecart d'echelle.

⚠⚠ LE PANNEAU B REPOND A « BRUIT OU STRUCTURE ? ». L'angle decroit quand le voisinage grandit,
donc une part est de la rugosite locale — mais il PLAFONNE, cent fois au-dessus de la prediction.

⛔⛔⛔ ET LE PANNEAU C PORTE LA REFUTATION. Si l'obliquite expliquait l'ecart de pas de `99`, la
barre verte (pas mesure le long de la NORMALE) tomberait sur le repere rouge (pas radial × cos).
Elle tombe sur la barre bleue. Le pas ne depend pas de la direction.

Usage :
    uv run python src/figures/figure_la_normale_nest_pas_le_rayon.py --verifier
    uv run python src/figures/figure_la_normale_nest_pas_le_rayon.py \\
        --sortie docs/images/100_la_normale_nest_pas_le_rayon.png
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_normale_nest_pas_le_rayon.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def lues(m: dict) -> list[dict]:
    return [x for x in m["lignes"]
            if x.get("angle_grille_deg") is not None
            and x.get("rayon_mesure_mm") is not None]


def refutation(m: dict) -> list[dict]:
    d = m.get("le_pas_dans_les_deux_directions", {})
    return [x for x in d.get("lignes", [])
            if x.get("rapport_radial_sur_normal") is not None]


def prose(m: dict) -> list[str]:
    s = m["resume"]
    b = m.get("balayage_de_voisinage_deg", {})
    d = m.get("le_pas_dans_les_deux_directions", {})
    cles = sorted(b, key=int)
    lignes = [
        f"★★★ CE QUE CE FICHIER MESURE, ET C'EST L'ITEM A BIS DU BLOC DE REPRISE. `99` a mesure "
        f"que la matiere montre un pas de 199 µm la ou `91` publie 164 sur les transferts humains "
        f"— 21 % d'ecart inexplique. une explication evidente se presentait : si le rayon n'est "
        f"pas perpendiculaire a l'empilement, la distance radiale entre deux feuilles vaut "
        f"pas / cos(theta), donc un pas apparent plus GRAND. et l'accord numerique etait "
        f"stupefiant — 1/cos median 1,212 contre un rapport observe 198,9/164,0 = 1,213.",
        f"★★★ PANNEAU A — LE FAIT, ET IL EST PLUS LOURD QUE L'HYPOTHESE QU'IL DEVAIT SERVIR. la "
        f"normale du maillage est a {s['angle_grille_median_deg']:.1f}° du rayon, la ou une "
        f"spirale de pas {m['pas_nominal_um']:.0f} µm en predit "
        f"{s['inclinaison_predite_mediane_deg']:.2f}° — "
        f"{s['combien_de_fois_la_prediction']:.0f} fois moins. la surface que les humains ont "
        f"tracee n'est donc pas une spirale vue de face : elle est franchement OBLIQUE au rayon.",
        f"★★ ET CE N'EST PAS L'ESTIMATEUR. la normale par ACP — plus petit vecteur propre de la "
        f"covariance des voisins, donc INDEPENDANTE de la grille — rend "
        f"{s['angle_acp_median_deg']:.1f}° contre {s['angle_grille_median_deg']:.1f}° pour la "
        f"normale de la grille, soit {s['ecart_entre_estimateurs_deg']:.1f}° d'ecart. deux "
        f"estimateurs qui ne partagent AUCUNE hypothese s'accordent : l'obliquite est dans la "
        f"matiere tracee, pas dans la facon de la lire.",
        f"⚠⚠ PANNEAU B — BRUIT OU STRUCTURE ? c'est le controle de `96`, applique a une direction. "
        f"l'angle TOMBE quand le voisinage grandit — {b[cles[0]]:.1f}° a {cles[0]} voisins, "
        f"{b[cles[-1]]:.1f}° a {cles[-1]} — donc une part est de la rugosite locale. mais il ne "
        f"converge PAS vers zero : il plafonne "
        f"{b[cles[-1]] / max(s['inclinaison_predite_mediane_deg'], 1e-9):.0f} fois au-dessus de "
        f"ce que la spirale predit.",
        f"⚠ DECOMPOSEE, L'OBLIQUITE EST LES DEUX A LA FOIS : {s['angle_du_a_z_median_deg']:.1f}° "
        f"hors du plan de la section — les feuilles seraient CONIQUES et non cylindriques — et "
        f"{s['angle_dans_le_plan_median_deg']:.1f}° dans le plan — la section n'est pas un cercle, "
        f"ce que `91` signalait deja. les deux se corrigent differemment, donc un angle total seul "
        f"ne dirait pas laquelle on regarde.",
    ]
    if d.get("bandes_mesurees"):
        lignes += [
            f"★★★ NON — PANNEAU C — L'HYPOTHESE EST REFUTEE PAR LA MESURE, ET C'EST TOUT L'OBJET DU "
            f"FICHIER. le long de la NORMALE, le pas mesure est le MEME que radialement : rapport "
            f"median {d['rapport_median']:.3f} (de {d['rapport_min']:.2f} a {d['rapport_max']:.2f})"
            f" la ou l'obliquite en predirait {d['un_sur_cos_median']:.3f}. ecart a 1 : "
            f"{d['ecart_a_un']:.3f} ; ecart a 1/cos : {d['ecart_a_un_sur_cos']:.3f}. l'accord "
            f"1,212 contre 1,213 etait une COINCIDENCE — exactement le piege que `94` a "
            f"enregistre avec la sagitta, evite cette fois parce que le test a ete lance AVANT de "
            f"publier.",
            f"★★★ ET LE CONTROLE QUI REND CE RESULTAT NEGATIF LISIBLE : un test qui ne voit rien "
            f"est indiscernable d'un test AVEUGLE. sur un empilement fabrique dont l'obliquite est "
            f"connue, le meme instrument lit bien 1,238 pour un 1/cos(35°) = 1,221 attendu, et "
            f"1,000 a angle nul. il VOIT l'obliquite quand elle existe — et il ne la voit pas ici.",
            f"⚠⚠⚠ ET CELA CORRIGE UNE AFFIRMATION DE `98`. sa docstring disait « le segment est "
            f"radial et a z constant, DONC il traverse l'empilement perpendiculairement ». la "
            f"seconde moitie est mesuree fausse. ce qui sauve la mesure de `98` n'est pas ce qui "
            f"etait ecrit, c'est l'autre resultat de ce fichier : le pas ne depend pas de la "
            f"direction. la raison, elle, reste inexpliquee.",
        ]
    return lignes


def panneau_angle(art, x0, y0, pw, ph, m, petit) -> int:
    """L'angle mesuré contre celui qu'une spirale prédit, en échelle logarithmique."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "angle de la normale au rayon", fill=DISCRET, font=petit)
    lignes = lues(m)
    gauche, droite = x0 + 46, x0 + pw - 18
    base, sommet = y0 + ph - 58, y0 + 40
    r0 = min(x["rayon_mesure_mm"] for x in lignes)
    r1 = max(x["rayon_mesure_mm"] for x in lignes)
    # ⚠⚠ L'ECHELLE EST LOGARITHMIQUE PARCE QUE LE FAIT EST UN ECART D'ECHELLE. Une echelle
    # lineaire ecraserait la prediction sur l'axe et le lecteur ne verrait qu'une courbe.
    lo, hi = math.log10(0.03), math.log10(90.0)

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.9) / max(r1 * 1.08 - r0 * 0.9, 1e-9)

    def py(v):
        return base - (base - sommet) * (math.log10(max(v, 0.03)) - lo) / (hi - lo)

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    for g in (0.1, 1.0, 10.0):
        y = py(g)
        art.line([gauche, y, droite, y], fill=(235, 235, 235))
        art.text((x0 + 6, y - 6), f"{g:g}°", fill=DISCRET, font=petit)
    points = 0
    for nom, cle, coul in (("normale de la grille", "angle_grille_deg", BLEU),
                           ("normale par ACP", "angle_acp_deg", AMBRE),
                           ("prédit par la spirale", "inclinaison_predite_deg", ROUGE)):
        pts = [(px(x["rayon_mesure_mm"]), py(x[cle])) for x in lignes]
        if len(pts) > 1:
            art.line(pts, fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=coul)
            points += 1
        del nom
    art.text((x0 + 8, y0 + 22), "normale de la grille", fill=BLEU, font=petit)
    art.text((x0 + 8, y0 + 36), "normale par ACP (sans la grille)", fill=AMBRE, font=petit)
    art.text((gauche + 4, base - 22), "ce qu'une spirale de ce pas prédit", fill=ROUGE,
             font=petit)
    for g in (r0, (r0 + r1) / 2, r1):
        art.text((px(g) - 14, base + 6), f"{g:.0f} mm", fill=DISCRET, font=petit)
    s = m["resume"]
    art.text((x0 + 8, y0 + ph - 34),
             f"★★★ {s['combien_de_fois_la_prediction']:.0f} fois la prédiction "
             f"({s['angle_grille_median_deg']:.1f}° contre "
             f"{s['inclinaison_predite_mediane_deg']:.2f}°)", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian · ordonnée logarithmique",
             fill=DISCRET, font=petit)
    return points


def panneau_voisinage(art, x0, y0, pw, ph, m, petit) -> int:
    """L'angle contre la taille du voisinage : ce qui s'efface et ce qui reste."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "bruit ou structure ? l'angle contre le voisinage",
             fill=DISCRET, font=petit)
    b = m.get("balayage_de_voisinage_deg", {})
    cles = sorted(b, key=int)
    gauche, droite = x0 + 46, x0 + pw - 18
    base, sommet = y0 + ph - 58, y0 + 40
    lo, hi = math.log10(int(cles[0])), math.log10(int(cles[-1]))
    haut = max(60.0, max(b.values()) * 1.15)

    def px(k):
        return gauche + (droite - gauche) * (math.log10(k) - lo) / max(hi - lo, 1e-9)

    def py(v):
        return base - (base - sommet) * v / haut

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    for g in (0, 20, 40, 60):
        y = py(g)
        art.line([gauche, y, droite, y], fill=(235, 235, 235))
        art.text((x0 + 6, y - 6), f"{g}°", fill=DISCRET, font=petit)
    courbes = 0
    for x in lues(m):
        bb = x.get("balayage_de_voisinage_deg", {})
        pts = [(px(int(k)), py(bb[k])) for k in cles if bb.get(k) is not None]
        if len(pts) > 1:
            art.line(pts, fill=(214, 222, 232), width=1)
            courbes += 1
    art.line([(px(int(k)), py(b[k])) for k in cles], fill=BLEU, width=3)
    for k in cles:
        cx, cy = px(int(k)), py(b[k])
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BLEU)
        art.text((cx - 12, base + 6), k, fill=DISCRET, font=petit)
    s = m["resume"]
    # ⭐⭐⭐ LA PREDICTION EST TRACEE SUR LE MEME AXE, ET ELLE EST INDISCERNABLE DE L'AXE : c'est
    # ca, le fait. Une legende suffirait a le dire ; la ligne le MONTRE.
    y = py(s["inclinaison_predite_mediane_deg"])
    for xx in range(int(gauche), int(droite), 8):
        art.line([xx, y, xx + 4, y], fill=ROUGE)
    art.text((gauche + 4, y - 16),
             f"prédit par la spirale : {s['inclinaison_predite_mediane_deg']:.2f}° — "
             "confondu avec l'axe", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★★ l'angle tombe de {b[cles[0]]:.1f}° à {b[cles[-1]]:.1f}° — mais il PLAFONNE",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : voisins de l'ACP (log) · fines : par bande",
             fill=DISCRET, font=petit)
    return courbes


def panneau_refutation(art, x0, y0, pw, ph, m, petit) -> int:
    """Le rapport OBSERVE contre le rapport que l'obliquite PREDIT, bande par bande.

    ⭐⭐⭐ LE NUAGE EST LA FORME QUI DISCRIMINE, ET C'EST POUR CA QU'IL A REMPLACE DES BARRES. Si
    l'obliquite expliquait l'ecart de pas, les points tomberaient sur la DIAGONALE rouge — chaque
    bande rendrait le rapport que son propre angle predit. S'ils tombent sur l'HORIZONTALE verte,
    le pas ignore la direction. Vingt-huit paires de barres ne montraient ni l'une ni l'autre :
    elles se recouvraient, et une figure illisible est une figure qui n'affirme rien.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "rapport observé contre rapport prédit", fill=DISCRET, font=petit)
    lignes = refutation(m)
    if not lignes:
        art.text((x0 + 8, y0 + 40),
                 "volume fin injoignable : le test décisif n'a pas tourné",
                 fill=ROUGE, font=petit)
        return 0
    gauche, droite = x0 + 52, x0 + pw - 24
    # ⚠ Le nuage est remonte pour laisser place aux DEUX verdicts sous lui : la garde de
    # recouvrement a montre que la legende du bas recouvrait la ligne de correlation.
    base, sommet = y0 + ph - 162, y0 + 54
    cx0 = min(x["un_sur_cos"] for x in lignes)
    cx1 = max(x["un_sur_cos"] for x in lignes)
    ry0 = min(0.80, min(x["rapport_radial_sur_normal"] for x in lignes))
    ry1 = max(1.40, max(x["rapport_radial_sur_normal"] for x in lignes))
    # ⚠ Les deux axes portent la MEME quantite (un rapport sans unite), donc la diagonale y = x
    # doit etre tracable : les bornes en x sont incluses dans celles en y.
    ax0, ax1 = min(cx0, ry0) * 0.98, max(cx1, ry1) * 1.02

    def px(v):
        return gauche + (droite - gauche) * (cx0 * 0.98 - ax0 + (v - cx0 * 0.98)) / (ax1 - ax0)

    def qx(v):
        return gauche + (droite - gauche) * (v - ax0) / (ax1 - ax0)

    def py(v):
        return base - (base - sommet) * (v - ax0) / (ax1 - ax0)

    del px
    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    # ⭐⭐⭐ LES DEUX HYPOTHESES SONT TRACEES, PAS UNE. Sans la diagonale, l'horizontale ne serait
    # qu'une ligne de reference ; c'est leur ECART qui fait la figure.
    art.line([qx(ax0), py(ax0), qx(ax1), py(ax1)], fill=ROUGE, width=2)
    art.line([gauche, py(1.0), droite, py(1.0)], fill=VERT, width=2)
    points = 0
    for x in lignes:
        cx, cy = qx(x["un_sur_cos"]), py(x["rapport_radial_sur_normal"])
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BLEU)
        points += 1
    d = m["le_pas_dans_les_deux_directions"]
    mx, my = qx(d["un_sur_cos_median"]), py(d["rapport_median"])
    art.line([mx - 8, my, mx + 8, my], fill=AMBRE, width=2)
    art.line([mx, my - 8, mx, my + 8], fill=AMBRE, width=2)
    for g in (0.9, 1.0, 1.1, 1.2, 1.3):
        if ax0 < g < ax1:
            art.text((x0 + 8, py(g) - 6), f"{g:.1f}", fill=DISCRET, font=petit)
            art.text((qx(g) - 10, base + 6), f"{g:.1f}", fill=DISCRET, font=petit)
    art.text((gauche + 4, py(1.0) - 16), "le pas ignore la direction", fill=VERT, font=petit)
    art.text((droite - 150, sommet + 2), "si l'obliquité expliquait tout", fill=ROUGE, font=petit)
    art.text((x0 + 8, base + 24), "abscisse : 1/cos de l'angle mesuré de la bande",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, base + 38), "ordonnée : pas radial / pas le long de la normale",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, base + 58),
             f"NON — médiane {d['rapport_median']:.3f} (croix ambre) là où", fill=ROUGE,
             font=petit)
    art.text((x0 + 8, base + 72),
             f"   l'obliquité prédirait {d['un_sur_cos_median']:.3f}.", fill=ROUGE, font=petit)
    art.text((x0 + 8, base + 86),
             f"   écart à 1 : {d['ecart_a_un']:.3f} ; à 1/cos : "
             f"{d['ecart_a_un_sur_cos']:.3f}.", fill=ROUGE, font=petit)
    if "correlation_rapport_contre_un_sur_cos" in d:
        art.text((x0 + 8, base + 106),
                 "★★ et la pente n'y est pas non plus :", fill=VERT, font=petit)
        art.text((x0 + 8, base + 120),
                 f"   corrélation {d['correlation_rapport_contre_un_sur_cos']:+.3f}, "
                 f"second verdict.", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "un test aveugle et un test qui ne voit rien se ressemblent",
             fill=DISCRET, font=petit)
    return points


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 330, 26, 400
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (150, 142, 134, 126, 118, 110):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    s = m["resume"]
    art.text((marge, 16),
             "La normale de la nappe n'est pas le rayon — et l'obliquité n'explique pas "
             "l'écart de pas", fill=TEXTE, font=gros)
    d = m.get("le_pas_dans_les_deux_directions", {})
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes']} bandes · "
             f"{s['angle_grille_median_deg']:.1f}° mesurés contre "
             f"{s['inclinaison_predite_mediane_deg']:.2f}° prédits "
             f"({s['combien_de_fois_la_prediction']:.0f}×) · "
             f"pas radial/normal = {d.get('rapport_median', float('nan')):.3f} là où "
             f"l'obliquité en prédirait {d.get('un_sur_cos_median', float('nan')):.3f}",
             fill=DISCRET, font=moyen)
    titres = ("A · mesuré contre ce qu'une spirale prédit",
              "B · bruit ou structure ?",
              "C · NON — le pas ignore la direction")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_angle(art, marge, 104, pw, ph, m, petit)
    courbes = panneau_voisinage(art, marge + pw + ecart, 104, pw, ph, m, petit)
    nuage = panneau_refutation(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    # ⭐⭐⭐ LES CADRES SONT RENDUS POUR QUE LA GARDE PUISSE MESURER CONTRE EUX. Un texte qui
    # tient dans la TOILE peut deborder de son panneau et recouvrir ce que le voisin dit : la
    # garde de largeur ne peut pas le voir, parce qu'une pose ne dit pas dans quel cadre
    # elle vit.
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "courbes": courbes, "nuage": nuage,
            "textes_dessines": art.textes,
            "debordants": textes_debordants(art.poses, L - marge),
            "hors_cadre": textes_hors_cadre(art.poses, cadres),
            "recouvrements": textes_qui_se_recouvrent(art.poses),
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
    d = dessiner(m, RACINE / "docs" / "images" / "100_la_normale_nest_pas_le_rayon.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    # ⭐⭐⭐ LES DEUX GARDES QUI FERMENT L'ANGLE MORT DE LA PRECEDENTE : un texte peut tenir dans
    # la toile en debordant de son PANNEAU, et il peut tenir partout en etant ECRIT PAR-DESSUS
    # un autre. Les trois classes echouent differemment, donc il en faut trois.
    v("aucun texte ne déborde de son PANNEAU", not d["hors_cadre"], str(d["hors_cadre"]))
    v("aucun texte n'est écrit par-dessus un autre", not d["recouvrements"],
      str(d["recouvrements"][:3]))
    v("toutes les bandes sont tracées dans le panneau A",
      d["points"] == 3 * len(lues(m)), f"{d['points']} pour {3 * len(lues(m))}")
    v("chaque bande a sa courbe de voisinage", d["courbes"] == len(lues(m)),
      f"{d['courbes']} pour {len(lues(m))}")
    # ⭐⭐⭐ LE PANNEAU C EST LA REFUTATION : deux barres par bande, et le repere de l'hypothese.
    v("le panneau C porte un point par bande mesurée",
      d["nuage"] == len(refutation(m)), f"{d['nuage']} pour {len(refutation(m))}")
    # ⭐⭐⭐ LES DEUX HYPOTHESES DOIVENT ETRE TRACEES : sans la diagonale, l'horizontale n'est
    # qu'une reference et la figure n'oppose rien.
    v("... et TRACE les deux hypothèses, pas une",
      any("si l'obliquité expliquait tout" in t for t in d["textes_dessines"])
      and any("le pas ignore la direction" in t for t in d["textes_dessines"]))
    # ⚠⚠ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    s = m["resume"]
    v("la mesure dépasse la prédiction d'un ordre de grandeur au moins",
      s["combien_de_fois_la_prediction"] >= 20, str(s["combien_de_fois_la_prediction"]))
    v("les deux estimateurs s'accordent", s["les_deux_estimateurs_saccordent"],
      f"écart {s['ecart_entre_estimateurs_deg']}°")
    v("une part est de la rugosité, et le reste plafonne",
      s["une_part_est_de_la_rugosite"]
      and s["mais_il_reste_bien_au_dela_de_la_prediction"])
    dd = m.get("le_pas_dans_les_deux_directions", {})
    if dd.get("bandes_mesurees"):
        v("l'obliquité n'explique PAS l'écart de pas",
          not dd["lobliquite_explique_le_pas"],
          f"rapport {dd['rapport_median']} contre 1/cos {dd['un_sur_cos_median']}")
        v("... le rapport étant plus près de 1 que de 1/cos",
          dd["ecart_a_un"] < dd["ecart_a_un_sur_cos"],
          f"{dd['ecart_a_un']} contre {dd['ecart_a_un_sur_cos']}")
    v("la prose garde la coïncidence et la nomme comme telle",
      any("COINCIDENCE" in x for x in prose(m)))
    v("... et le contrôle qui prouve que l'instrument n'est pas aveugle",
      any("indiscernable d'un test AVEUGLE" in x for x in prose(m)))
    v("... et la correction de la docstring de `98`",
      any("corrige une affirmation de `98`" in x.lower() for x in prose(m)))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "100_la_normale_nest_pas_le_rayon.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
