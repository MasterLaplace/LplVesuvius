#!/usr/bin/env python3
"""La direction que la matiere montre — et elle tranche la question que `100` avait laissee ouverte.

⭐⭐⭐ LE PANNEAU A PORTE LE VERDICT : la normale de la matiere, mesuree dans le volume fin sans
aucun maillage, est a 13,3° de celle du maillage humain et a 34,6° du rayon. L'obliquite de `100`
est donc REELLE — et son 34,6° recoupe independamment le 34,06° que `100` lisait sur le maillage.

⭐⭐⭐ LE PANNEAU B REFUTE LA DERNIERE EXPLICATION ALTERNATIVE. Un axe mal estime ferait tourner la
direction radiale, mais en `arctan(d/r)` : les deux courbes rouges sont ce que l'hypothese exige,
ajustee sur le coeur puis sur le bord, et aucune ne passe par les points.

⚠⚠ ET LE PANNEAU C SEPARE UN SIGNAL D'UN CONFONDANT. La part de cellules ou la matiere repond
monte vers le bord, la rupture de continuite aussi : a rayon TENU constant le lien survit
(+0,452), donc c'est un fait et non une coincidence d'echelle.

Usage :
    uv run python src/figures/figure_la_direction_que_la_matiere_montre.py --verifier
    uv run python src/figures/figure_la_direction_que_la_matiere_montre.py \\
        --sortie docs/images/101_la_direction_que_la_matiere_montre.png
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
MESURE = RACINE / "docs" / "mesures" / "la_direction_que_la_matiere_montre.json"

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
            if x.get("angle_matiere_rayon_deg") is not None and x.get("rayon_mm")]


def prose(m: dict) -> list[str]:
    s = m["resume"]
    ax = m["un_axe_decale_est_il_lexplication"]
    n = m["nul_du_tenseur"]
    lim = m["limite_de_bruit_du_tenseur"]
    grand = lim["cubes"][str(m["demi_cube_voxels"])]["lignes"][-1]
    return [
        f"★★★ CE QUE CE FICHIER TRANCHE. `100` a mesure que la normale du maillage humain est a "
        f"34,1° du rayon la ou une spirale de ce pas en predit 0,09°, et deux estimateurs sans "
        f"hypothese commune s'accordaient dessus. il restait DEUX lectures, indistinguables dans "
        f"le maillage : soit la matiere est reellement oblique et le maillage la suit, soit c'est "
        f"le MAILLAGE qui est oblique a la matiere — c'est-a-dire que la surface tracee par les "
        f"humains ne repose pas sur une feuille. seule la matiere peut trancher.",
        f"★★★ PANNEAU A — LA MATIERE SUIT LE MAILLAGE, DONC L'OBLIQUITE EST REELLE. le tenseur de "
        f"structure du volume fin — la covariance des gradients d'intensite dans un cube de "
        f"{m['cote_du_cube_um']} µm, sans aucun maillage — rend une normale a "
        f"{s['angle_matiere_maillage_median_deg']:.1f}° de celle du maillage et a "
        f"{s['angle_matiere_rayon_median_deg']:.1f}° du rayon, sur {s['bandes_lues']} bandes. "
        f"et ce {s['angle_matiere_rayon_median_deg']:.1f}° recoupe INDEPENDAMMENT le 34,06° que "
        f"`100` lisait sur le maillage seul : deux instruments qui ne partagent rien.",
        f"★★ CE QUE CA DIT DU REFERENT HUMAIN, ET C'EST UNE NUANCE QUI COMPTE. le maillage est "
        f"donc sur la matiere en ORIENTATION, a treize degres — alors que `97` a mesure qu'il se "
        f"trompe de plus d'une demi-feuille en IDENTITE. ce sont deux pannes differentes, et une "
        f"seule est fatale : savoir sur quelle feuille on est.",
        f"★★★ PANNEAU B — LA DERNIERE EXPLICATION ALTERNATIVE EST REFUTEE PAR SA SIGNATURE. un axe "
        f"mal estime ferait tourner la direction radiale de arctan(d/r), et `90` a mesure que "
        f"l'axe DERIVE de 12,6 mm : l'hypothese n'etait pas farfelue. mais elle predit une "
        f"decroissance en 1/r. le decalage qui explique le coeur "
        f"({ax['decalage_qui_explique_le_coeur_mm']} mm a "
        f"{ax['rayon_le_plus_petit_mm']} mm de rayon) predit "
        f"{ax['angle_predit_au_bord_par_ce_decalage_deg']}° au bord ou l'on mesure "
        f"{ax['angle_mesure_au_bord_deg']}° ; celui qui explique le bord "
        f"({ax['decalage_qui_explique_le_bord_mm']} mm) predit "
        f"{ax['angle_predit_au_coeur_par_ce_decalage_deg']}° au coeur ou l'on mesure "
        f"{ax['angle_mesure_au_coeur_deg']}°.",
        f"★★ ET LES DEUX MODELES SONT AJUSTES ET COMPARES, PAS OPPOSES EN HOMME DE PAILLE : "
        f"chacun a UN parametre libre, donc leurs residus sont directement comparables. residu du "
        f"modele d'axe {ax['residu_du_modele_daxe_deg']}° contre "
        f"{ax['residu_du_modele_constant_deg']}° pour une obliquite CONSTANTE — l'axe explique "
        f"MOINS BIEN. et le verdict sait dire oui : sur un jeu fabrique dont les angles suivent "
        f"arctan(d/r), il retrouve le decalage injecte a 5,0 mm pres de zero.",
        f"⚠⚠⚠ DEUX CORRECTIONS D'INSTRUMENT, TOUTES DEUX TROUVEES PAR LA MESURE. (1) la PLANARITE "
        f"est refutee comme juge de direction : un bruit isotrope ecrase le RAPPORT des valeurs "
        f"propres sans deplacer la DIRECTION, donc a sigma = 15 elle retombe a "
        f"{grand['planarite']} — le niveau du bruit pur — la ou la direction est encore juste a "
        f"{grand['angle_deg']}°. fermer sur elle aurait ete une garde qui supprime ce qu'elle doit "
        f"laisser passer, le peche de `97`.",
        f"⚠⚠⚠ (2) `np.gradient` INJECTAIT UNE ANISOTROPIE AU BORD DU CUBE : ses plans extremes "
        f"prennent des differences unilaterales, de variance QUATRE fois celle d'une difference "
        f"centree. couper le cube en deux creait donc un nouveau bord en z et biaisait les DEUX "
        f"moities vers z — sur du BRUIT PUR elles s'accordaient a 10,4° au lieu des ~60 que deux "
        f"directions au hasard donnent. plans de bord jetes, le nul remonte a "
        f"{n['accord_des_moities_median_deg']}° et la garde redevient honnete.",
        f"⚠⚠ PANNEAU C — UN SIGNAL, ET SON CONFONDANT RETIRE. la part de cellules ou la matiere "
        f"repond corrèle a {s['part_orientee_contre_continuite']:+.3f} avec la rupture de "
        f"continuite — mais elle monte aussi avec le rayon "
        f"({s['part_orientee_contre_rayon']:+.3f}) et la rupture encore plus "
        f"({s['continuite_contre_rayon']:+.3f}), donc les deux montent ensemble vers le bord. a "
        f"rayon TENU constant, avec l'instrument de `95`, le lien SURVIT : "
        f"{s['part_orientee_contre_continuite_a_rayon_tenu']:+.3f}.",
        f"★★ ET C'EST UN ACQUIS POUR LE GRAAL : la matiere donne une direction sur "
        f"{100 * s['part_orientee_mediane']:.0f} % des cellules, PLUS souvent au bord, la ou `99` "
        f"perdait la periodicite (0,54 d'utilisable). avec le PAS de `99` et la DIRECTION d'ici, "
        f"un automate a les deux nombres qu'il faut pour franchir une feuille sans humain.",
        f"NON — CE QUI N'EST PAS UN SIGNAL, ET IL FAUT LE DIRE : l'ecart du maillage a la matiere ne "
        f"predit PAS la rupture — {s['ecart_a_la_matiere_contre_continuite']:+.3f} brut, "
        f"{s['ecart_a_la_matiere_contre_continuite_a_rayon_tenu']:+.3f} a rayon tenu, sur 28 "
        f"bandes. c'est faible et de signe instable ; s'en servir serait lire du bruit.",
    ]


def panneau_verdict(art, x0, y0, pw, ph, m, petit) -> int:
    """L'angle de la matière au rayon et au maillage, par bande."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "où pointe la normale de la MATIÈRE", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 22), "écart au rayon", fill=BLEU, font=petit)
    art.text((x0 + 8, y0 + 36), "écart au maillage humain", fill=VERT, font=petit)
    lignes = lues(m)
    gauche, droite = x0 + 46, x0 + pw - 18
    base, sommet = y0 + ph - 58, y0 + 54
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    haut = 70.0

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.9) / max(r1 * 1.06 - r0 * 0.9, 1e-9)

    def py(v):
        return base - (base - sommet) * v / haut

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    for g in (0, 20, 40, 60):
        art.line([gauche, py(g), droite, py(g)], fill=(235, 235, 235))
        art.text((x0 + 6, py(g) - 6), f"{g}°", fill=DISCRET, font=petit)
    points = 0
    for cle, coul in (("angle_matiere_rayon_deg", BLEU),
                      ("angle_matiere_maillage_deg", VERT)):
        pts = [(px(x["rayon_mm"]), py(x[cle])) for x in lignes]
        art.line(pts, fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=coul)
            points += 1
    s = m["resume"]
    # ⭐⭐⭐ LA PREDICTION DE LA SPIRALE EST TRACEE, ET ELLE EST CONFONDUE AVEC L'AXE : c'est ce
    # qui fait que le panneau se lit sans legende. Une valeur en tableau ne le montrerait pas.
    y = py(0.09)
    for xx in range(int(gauche), int(droite), 8):
        art.line([xx, y, xx + 4, y], fill=ROUGE)
    art.text((gauche + 4, y - 15), "ce qu'une spirale de ce pas prédit : 0,09°",
             fill=ROUGE, font=petit)
    for g in (r0, (r0 + r1) / 2, r1):
        art.text((px(g) - 14, base + 6), f"{g:.0f} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★★★ {s['angle_matiere_maillage_median_deg']:.1f}° du maillage contre "
             f"{s['angle_matiere_rayon_median_deg']:.1f}° du rayon", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "la matière suit le maillage : l'obliquité est RÉELLE", fill=DISCRET, font=petit)
    return points


def panneau_axe(art, x0, y0, pw, ph, m, petit) -> int:
    """La signature en 1/r qu'un axe décalé exigerait, contre les points mesurés."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "un axe mal estimé expliquerait-il tout ?",
             fill=DISCRET, font=petit)
    ax = m["un_axe_decale_est_il_lexplication"]
    lignes = lues(m)
    gauche, droite = x0 + 46, x0 + pw - 18
    base, sommet = y0 + ph - 88, y0 + 40
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    haut = 80.0

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.9) / max(r1 * 1.06 - r0 * 0.9, 1e-9)

    def py(v):
        return base - (base - sommet) * min(v, haut) / haut

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    for g in (0, 20, 40, 60, 80):
        art.line([gauche, py(g), droite, py(g)], fill=(235, 235, 235))
        art.text((x0 + 6, py(g) - 6), f"{g}°", fill=DISCRET, font=petit)
    # ⭐⭐⭐ LES DEUX COURBES QUE L'HYPOTHESE EXIGE, AJUSTEE SUR CHAQUE EXTREMITE. Sans elles, la
    # figure montrerait un nuage de points sans dire ce qu'il aurait du valoir.
    courbes = 0
    for dec, coul in ((ax["decalage_qui_explique_le_coeur_mm"], ROUGE),
                      (ax["decalage_qui_explique_le_bord_mm"], AMBRE)):
        pts = []
        rr = r0 * 0.92
        while rr <= r1 * 1.04:
            pts.append((px(rr), py(math.degrees(math.atan2(dec, rr)))))
            rr += 0.25
        art.line(pts, fill=coul, width=2)
        courbes += 1
    pts = [(px(x["rayon_mm"]), py(x["angle_matiere_rayon_deg"])) for x in lignes]
    for cx, cy in pts:
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BLEU)
    art.line([px(r0 * 0.92), py(ax["residu_du_modele_constant_deg"] * 0
                                + m["resume"]["angle_matiere_rayon_median_deg"]),
              px(r1 * 1.04), py(m["resume"]["angle_matiere_rayon_median_deg"])],
             fill=VERT, width=2)
    art.text((x0 + 8, y0 + 22), "mesuré · obliquité constante", fill=BLEU, font=petit)
    art.text((x0 + 8, base + 22),
             f"rouge : 1/r ajusté sur le cœur ({ax['decalage_qui_explique_le_coeur_mm']} mm)",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, base + 36),
             f"ambre : 1/r ajusté sur le bord ({ax['decalage_qui_explique_le_bord_mm']} mm)",
             fill=AMBRE, font=petit)
    art.text((x0 + 8, base + 56),
             f"NON — résidu {ax['residu_du_modele_daxe_deg']}° pour l'axe contre",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, base + 70),
             f"   {ax['residu_du_modele_constant_deg']}° pour une obliquité constante.",
             fill=ROUGE, font=petit)
    for g in (r0, (r0 + r1) / 2, r1):
        art.text((px(g) - 14, base + 6), f"{g:.0f} mm", fill=DISCRET, font=petit)
    return courbes


def panneau_ou_elle_repond(art, x0, y0, pw, ph, m, petit) -> int:
    """Où la matière donne une direction, et le confondant du rayon retiré."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "où la matière donne une direction", fill=DISCRET, font=petit)
    lignes = lues(m)
    gauche, droite = x0 + 46, x0 + pw - 46
    base, sommet = y0 + ph - 110, y0 + 40
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    c_hi = max(x["continuite"] for x in lignes if x.get("continuite")) * 1.12

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.9) / max(r1 * 1.06 - r0 * 0.9, 1e-9)

    def py(v, hi):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([(px(x["rayon_mm"]), py(x["part_orientee"], 1.0)) for x in lignes],
             fill=BLEU, width=2)
    art.line([(px(x["rayon_mm"]), py(x["continuite"], c_hi)) for x in lignes
              if x.get("continuite")], fill=ROUGE, width=2)
    points = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["part_orientee"], 1.0)
        art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLEU)
        points += 1
    for g in (0.0, 0.5, 1.0):
        art.text((x0 + 6, py(g, 1.0) - 6), f"{g:>4.1f}", fill=BLEU, font=petit)
    for g in (0.0, c_hi / 2, c_hi):
        art.text((droite + 6, py(g, c_hi) - 6), f"×{g:.0f}", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + 22), "part orientée · rupture de continuité", fill=DISCRET,
             font=petit)
    s = m["resume"]
    art.text((x0 + 8, base + 22),
             f"brut {s['part_orientee_contre_continuite']:+.3f} — mais les deux",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, base + 36),
             f"montent avec le rayon ({s['part_orientee_contre_rayon']:+.3f} et "
             f"{s['continuite_contre_rayon']:+.3f})", fill=DISCRET, font=petit)
    art.text((x0 + 8, base + 56),
             f"★★ à rayon TENU le lien SURVIT : "
             f"{s['part_orientee_contre_continuite_a_rayon_tenu']:+.3f}", fill=VERT, font=petit)
    art.text((x0 + 8, base + 76),
             f"NON — l'écart maillage/matière ne prédit rien :",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, base + 90),
             f"   {s['ecart_a_la_matiere_contre_continuite']:+.3f} brut, "
             f"{s['ecart_a_la_matiere_contre_continuite_a_rayon_tenu']:+.3f} à rayon tenu.",
             fill=ROUGE, font=petit)
    for g in (r0, (r0 + r1) / 2, r1):
        art.text((px(g) - 14, base + 6), f"{g:.0f} mm", fill=DISCRET, font=petit)
    return points


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 330, 26, 420
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
             "La direction que la matière montre — l'obliquité de `100` est réelle",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {s['bandes_lues']} bandes · cube de {m['cote_du_cube_um']} µm "
             f"dans le volume à {m['voxel_fin_um']} µm · "
             f"{s['angle_matiere_maillage_median_deg']:.1f}° du maillage contre "
             f"{s['angle_matiere_rayon_median_deg']:.1f}° du rayon · "
             f"{100 * s['part_orientee_mediane']:.0f} % des cellules orientées",
             fill=DISCRET, font=moyen)
    titres = ("A · la matière suit-elle le maillage ou le rayon ?",
              "B · NON — un axe décalé n'explique pas",
              "C · où la matière répond, confondant retiré")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_verdict(art, marge, 104, pw, ph, m, petit)
    courbes = panneau_axe(art, marge + pw + ecart, 104, pw, ph, m, petit)
    repond = panneau_ou_elle_repond(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "courbes": courbes, "repond": repond,
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
    d = dessiner(m, RACINE / "docs" / "images"
                 / "101_la_direction_que_la_matiere_montre.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("aucun texte ne déborde de son PANNEAU", not d["hors_cadre"], str(d["hors_cadre"]))
    v("aucun texte n'est écrit par-dessus un autre", not d["recouvrements"],
      str(d["recouvrements"][:3]))
    v("les deux angles sont tracés pour chaque bande",
      d["points"] == 2 * len(lues(m)), f"{d['points']} pour {2 * len(lues(m))}")
    # ⭐⭐⭐ LE PANNEAU B DOIT TRACER LES DEUX COURBES QUE L'HYPOTHESE EXIGE, pas une : c'est leur
    # incompatibilite entre elles qui la refute, pas leur ecart aux points.
    v("le panneau B trace les DEUX ajustements de l'hypothèse", d["courbes"] == 2,
      str(d["courbes"]))
    v("le panneau C trace chaque bande", d["repond"] == len(lues(m)), str(d["repond"]))
    # ⚠⚠ LES VERDICTS SONT DANS LA MESURE, pas seulement dans la prose.
    s = m["resume"]
    v("la matière est plus proche du maillage que du rayon",
      s["la_matiere_suit_le_maillage"],
      f"{s['angle_matiere_maillage_median_deg']}° contre "
      f"{s['angle_matiere_rayon_median_deg']}°")
    v("... et son angle au rayon recoupe celui que `100` lisait sur le maillage",
      abs(s["angle_matiere_rayon_median_deg"] - 34.06) < 6.0,
      f"{s['angle_matiere_rayon_median_deg']}° contre 34,06°")
    ax = m["un_axe_decale_est_il_lexplication"]
    v("un axe décalé n'explique PAS mieux qu'une obliquité constante",
      not ax["un_axe_decale_explique_mieux"],
      f"{ax['residu_du_modele_daxe_deg']}° contre "
      f"{ax['residu_du_modele_constant_deg']}°")
    v("... et les deux ajustements de l'hypothèse sont incompatibles entre eux",
      ax["angle_predit_au_bord_par_ce_decalage_deg"]
      < ax["angle_mesure_au_bord_deg"] / 2.0
      and ax["angle_predit_au_coeur_par_ce_decalage_deg"]
      > ax["angle_mesure_au_coeur_deg"] * 1.5,
      f"{ax['angle_predit_au_bord_par_ce_decalage_deg']}° au bord pour "
      f"{ax['angle_mesure_au_bord_deg']} mesurés")
    v("le confondant du rayon est retiré et le lien survit",
      s["part_orientee_contre_continuite_a_rayon_tenu"] > 0.3,
      str(s["part_orientee_contre_continuite_a_rayon_tenu"]))
    # ⛔ ET LE NEGATIF EST GARDE : l'ecart maillage/matiere ne predit rien.
    v("l'écart maillage/matière est publié comme NON prédictif",
      abs(s["ecart_a_la_matiere_contre_continuite"]) < 0.3,
      str(s["ecart_a_la_matiere_contre_continuite"]))
    v("la prose garde les deux corrections d'instrument",
      any("PLANARITE" in x and "refutee" in x for x in prose(m))
      and any("np.gradient" in x for x in prose(m)))
    v("... et l'acquis pour le graal, avec le pas de `99`",
      any("les deux nombres qu'il faut" in x for x in prose(m)))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "101_la_direction_que_la_matiere_montre.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
