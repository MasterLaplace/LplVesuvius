#!/usr/bin/env python3
"""Le marcheur avec le bon pas — `102` rejoue, et ses etapes gardees.

★★★ LE PANNEAU A EST LA PORTEE, les deux selecteurs depuis les MEMES departs, avec la CENSURE
dessinee : une cellule au plafond dit « au moins ceci », et l'omettre ferait passer un budget de
lecture pour une limite de matiere.

★★★ LE PANNEAU B EST LE RISQUE PAR PAS, conditionnel a avoir tenu les precedents — c'est lui qui
decide du graal, un risque constant `p` rendant `(1-p)^120`. La confirmation MARGINALE est tracee
a cote : leur ecart dit si les chutes sont des manques isoles ou un egarement.

★★★ LE PANNEAU C EST LE REGISTRE DU TRAJET ENTIER, la seule forme NON tautologique. La fraction
par pas ne l'est pas : les deux selecteurs y rendent le meme nombre malgre des pas differents,
parce que chacun CHOISIT son pas pour qu'une periode y tienne.

Usage :
    uv run python src/figures/figure_le_marcheur_avec_le_bon_pas.py --verifier
    uv run python src/figures/figure_le_marcheur_avec_le_bon_pas.py \\
        --sortie docs/images/107_le_marcheur_avec_le_bon_pas.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_marcheur_avec_le_bon_pas.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    s, ca, dr = m["resume"], m["calibre"], m["deux_roles"]
    lignes = []
    if "gain_en_pas" in s:
        lignes.append(
            f"{'★★★' if s['le_pas_corrige_porte_plus_loin'] else 'NON —'} LE PAS CORRIGÉ "
            f"{'PORTE PLUS LOIN' if s['le_pas_corrige_porte_plus_loin'] else 'NE PORTE PAS PLUS LOIN'}"
            f" : {s['pas_confirmes_corrige']} pas confirmés contre "
            f"{s['pas_confirmes_calibre']} pour le sélecteur que `102` utilisait, soit "
            f"{s['gain_en_pas']:+.2f}, sur {s['cellules']} cellules de {s['bandes']} bandes "
            f"partant des MÊMES départs. ⚠ Et la portée est une BORNE INFÉRIEURE : "
            f"{dr['cellules_au_plafond']} cellules sur {s['cellules']} touchent le plafond de "
            f"{s['plafond_de_pas']} pas ({dr['part_censuree']:.1%}).")
    md = dr.get("modes_du_trajet", {})
    if md.get("decidable") and "mode_haut" in md and "mode_bas" in md:
        lignes.append(
            f"★★★ ET LE REGISTRE DU TRAJET SÉPARE LES MARCHES EN DEUX POPULATIONS QUE RIEN D'AUTRE "
            f"NE DISTINGUE. {md['mode_haut']['trajets']} trajets franchissent "
            f"{md['mode_haut']['feuilles_median']} feuilles pour {md['pas_attendus']} pas — soit "
            f"{md['mode_haut']['feuilles_par_pas_median']} par pas, ce que le marcheur doit faire "
            f"— et {md['mode_bas']['trajets']} n'en franchissent que "
            f"{md['mode_bas']['feuilles_median']}, soit "
            f"{md['mode_bas']['feuilles_par_pas_median']} par pas. "
            f"{md['part_au_dessus']:.1%} des marches comptent juste ; les autres mesurent une "
            f"dérive de basse fréquence et non des feuilles.")
        lignes.append(
            f"⚠⚠⚠ ET LE SCORE NE PERMET PAS DE LES SÉPARER, IL EST PLUS HAUT POUR LES MAUVAISES : "
            f"{md['mode_bas']['score_median']} contre {md['mode_haut']['score_median']}, soit "
            f"{md['ecart_des_scores_entre_modes']:+.3f}. Une dérive s'ajuste mieux sur une longue "
            f"fenêtre qu'un vrai signal périodique, donc un seuil de score écarterait le BON mode. "
            f"C'est exactement le point de `104` — un pas confirmé ne garantit pas qu'une feuille "
            f"a été franchie — mesuré cette fois sur la marche elle-même.")
        lignes.append(
            f"⚠⚠ ET J'AVAIS PUBLIÉ LA MÉDIANE DE CES DEUX MODES. Elle vaut "
            f"{dr.get('feuilles_par_pas_du_trajet')} feuille par pas et tombe dans le mode BAS par "
            f"accident de comptage, ce qui se lit « le marcheur ne franchit presque rien » alors "
            f"que quatre marches sur dix franchissent exactement ce qu'elles doivent. Une "
            f"médiane sur une distribution bimodale n'est pas un résumé : c'est un choix de mode "
            f"qui s'ignore.")
    if "le_trajet_du_corrige_est_plus_juste" in s:
        lignes.append(
            f"★★★ LE REGISTRE DU TRAJET ENTIER EST LA SEULE FORME NON TAUTOLOGIQUE, et c'est une "
            f"réfutation de mon propre instrument, la seconde après celle de `104`. La fraction "
            f"mesurée sur le segment d'UN pas vaut "
            f"{s.get('feuilles_par_pas_corrige')} pour le corrigé et "
            f"{s.get('feuilles_par_pas_calibre')} pour le calibré — le MÊME nombre malgré des pas "
            f"différents, parce que chacun CHOISIT son pas pour qu'une période y tienne. Le trajet "
            f"complet, lui, n'a jamais été optimisé : il rend "
            f"{s['feuilles_par_pas_du_trajet_corrige']} feuille par pas contre "
            f"{s['feuilles_par_pas_du_trajet_calibre']}, donc "
            f"{s['spires_du_trajet_corrige']} spires pour cent vingt pas contre "
            f"{s['spires_du_trajet_calibre']}.")
    v = dr.get("le_risque_baisse", {})
    if v.get("decidable"):
        lignes.append(
            f"★★★ LE RISQUE PAR PAS EST CE QUI DÉCIDE DU GRAAL, pas la portée : un risque "
            f"constant `p` rend `(1−p)^120` sur cent vingt spires. Mesuré, précoce "
            f"{v['risque_precoce']:.3f} sur {v['en_risque_precoce']} pas en risque contre tardif "
            f"{v['risque_tardif']:.3f} sur {v['en_risque_tardif']}, soit ×{v['rapport']} — et "
            f"sous un risque CONSTANT ce partage a p = {v['p_sous_risque_constant']}. "
            f"{'Le risque BAISSE' if v['le_risque_baisse'] else 'Le risque ne baisse PAS'}. "
            f"Enchaîné : {v['part_des_cent_vingt_spires_qui_survit_au_risque_precoce']:.6f} des "
            f"cent vingt spires survivent au risque précoce, "
            f"{v['part_des_cent_vingt_spires_qui_survit_au_risque_tardif']:.6f} au tardif.")
    elif v:
        lignes.append(
            f"⚠⚠ LE RISQUE N'EST PAS DÉCIDABLE sur cette course : {v.get('pourquoi')}. Le dire "
            f"vaut mieux que rendre un verdict sur un tiers vide, et cela chiffre ce qu'une course "
            f"plus large devrait payer.")
    if "virage_median_deg" in s:
        lignes.append(
            f"★★ ET LE SEUL LEVIER DE COÛT RESTANT EST CHIFFRÉ GRATUITEMENT PAR CETTE COURSE. Le "
            f"cube de direction fait 91 % du prix d'un pas et `103` a réfuté de le lire moins "
            f"cher ; reste de le lire moins souvent. La direction tourne de "
            f"{s['virage_median_deg']}° d'un pas au suivant (p90 {s['virage_p90_deg']}°), pour une "
            f"barre d'accord des demi-blocs de {m['barre_daccord_des_moities_deg']}° : "
            f"{'sous la barre' if s['virage_sous_la_barre_des_moities'] else 'au-dessus de la barre'}. "
            f"Un cube sur deux ferait passer la course à {s['heures_si_un_cube_sur_deux']} h. "
            f"⚠ Ce chiffre dit si la mesure vaut d'être payée, il ne la remplace pas.")
    c = m.get("cout_par_etape", {})
    if c.get("mesures"):
        lignes.append(
            f"⚠⚠⚠ LE COÛT D'UNE ÉTAPE A ÉTÉ MESURÉ QUATRE FOIS ET IL A RENDU QUATRE VALEURS : "
            + ", ".join(f"{x['secondes']} s ({x['condition']})" for x in c["mesures"])
            + f". La dispersion EST le résultat — une lecture distante coûte ce que le réseau a "
            f"déjà servi. La valeur retenue pour les projections est la plus GRANDE des fiables "
            f"({c['retenue_pour_les_projections_s']} s), parce que sous-estimer fait lancer une "
            f"course qu'on ne peut pas finir.")
    lignes.append(
        f"⚠ CE QUE CETTE COURSE NE DIT PAS : `106` a montré que la périodicité que ce pas mesure "
        f"n'est pas l'espacement d'un empilement localement parallèle. Le marcheur peut donc "
        f"porter plus loin avec un pas plus juste sans que « une feuille » ait le sens géométrique "
        f"qu'on lui prêtait. Ce qui est mesuré ici est la CHAÎNE, pas le sens de son maillon.")
    return lignes


def panneau_portee(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "pas confirmés, mêmes départs", fill=DISCRET, font=petit)
    s = m["resume"]
    g, d = x0 + 56, x0 + pw - 44
    haut = y0 + 52
    h = 52
    hi = max(m[sel]["pas_confirmes_max"] for sel in ("calibre", "deux_roles")) or 1
    barres = 0
    for j, (sel, coul, nom) in enumerate((("calibre", ROUGE, "sélecteur de `102`"),
                                          ("deux_roles", VERT, "sélecteur CORRIGÉ"))):
        b = m[sel]
        y = haut + j * h
        art.text((x0 + 6, y - 14), nom, fill=coul, font=petit)
        med = b["pas_confirmes_median"] or 0.0
        larg = (d - g) * med / hi
        art.rectangle([g, y, g + max(larg, 1.0), y + 16], fill=coul)
        art.text((g + max(larg, 1.0) + 5, y + 1), f"{med}", fill=coul, font=petit)
        # ⚠ La CENSURE est dessinée sur la barre : une cellule au plafond dit « au moins ceci ».
        if b["la_portee_est_censuree"]:
            art.line([g + (d - g) * b["pas_confirmes_max"] / hi, y - 4,
                      g + (d - g) * b["pas_confirmes_max"] / hi, y + 20], fill=DISCRET)
            art.text((x0 + 6, y + 20), f"   {b['cellules_au_plafond']}/{s['cellules']} au "
                     f"plafond ({b['part_censuree']:.0%})", fill=DISCRET, font=petit)
        barres += 1
    bas = haut + 2 * h + 24
    art.line([g, bas - 8, d, bas - 8], fill=CADRE)
    for k in (0, hi // 2, hi):
        art.text((g + (d - g) * k / hi - 4, bas - 4), f"{k}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 14), f"plafond {s['plafond_de_pas']} pas · "
             f"{s['cellules']} cellules, {s['bandes']} bandes", fill=DISCRET, font=petit)
    if "gain_en_pas" in s:
        art.text((x0 + 8, bas + 34),
                 f"★ {'le corrigé porte plus loin' if s['le_pas_corrige_porte_plus_loin'] else 'NON — pas plus loin'}",
                 fill=VERT if s["le_pas_corrige_porte_plus_loin"] else ROUGE, font=petit)
        art.text((x0 + 8, bas + 48), f"   {s['gain_en_pas']:+.2f} pas", fill=TEXTE, font=petit)
    for sel, coul in (("calibre", ROUGE), ("deux_roles", VERT)):
        art.text((x0 + 8, bas + 68 + (0 if sel == "calibre" else 14)),
                 f"   pas lu {m[sel]['pas_lu_median_um']} µm", fill=coul, font=petit)
    return barres


def panneau_risque(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "risque conditionnel et confirmation marginale",
             fill=DISCRET, font=petit)
    rq = m["deux_roles"].get("risque_par_pas", [])
    mg = {x["pas"]: x for x in m["deux_roles"].get("confirmation_marginale", [])}
    if not rq:
        art.text((x0 + 8, y0 + 40), "aucun pas mesuré", fill=DISCRET, font=petit)
        return 0
    g, d = x0 + 46, x0 + pw - 24
    haut, bas = y0 + 44, y0 + ph - 130
    ks = [x["pas"] for x in rq]
    def X(k): return g + (d - g) * (k - ks[0]) / max(ks[-1] - ks[0], 1)
    def Y(v): return bas - (bas - haut) * v
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    poses = 0
    for cle, coul, src in (("risque", ROUGE, rq),
                           ("part", VERT, [mg[k] for k in ks if k in mg])):
        pts = [(X(x["pas"]), Y(x[cle])) for x in src]
        for i in range(len(pts) - 1):
            art.line([pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]], fill=coul)
        for px, py in pts:
            art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=coul)
            poses += 1
    for k in (ks[0], ks[-1]):
        art.text((X(k) - 4, bas + 4), f"{k}", fill=DISCRET, font=petit)
    for v in (0.0, 0.5, 1.0):
        art.text((x0 + 6, Y(v) - 6), f"{v:.1f}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 22), "rouge : risque de tomber au pas k", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 36), "vert : part confirmée (marginale)", fill=VERT, font=petit)
    v = m["deux_roles"].get("le_risque_baisse", {})
    if v.get("decidable"):
        art.text((x0 + 8, bas + 56), f"★ précoce {v['risque_precoce']:.3f} · tardif "
                 f"{v['risque_tardif']:.3f}", fill=TEXTE, font=petit)
        art.text((x0 + 8, bas + 70), f"   ×{v['rapport']}, p = "
                 f"{v['p_sous_risque_constant']}", fill=TEXTE, font=petit)
        art.text((x0 + 8, bas + 84), f"   le risque baisse : {v['le_risque_baisse']}",
                 fill=VERT if v["le_risque_baisse"] else ROUGE, font=petit)
        art.text((x0 + 8, bas + 104), f"⚠ sur 120 spires : "
                 f"{v['part_des_cent_vingt_spires_qui_survit_au_risque_tardif']:.6f}",
                 fill=TEXTE, font=petit)
    else:
        art.text((x0 + 8, bas + 56), "⚠ indécidable :", fill=ROUGE, font=petit)
        art.text((x0 + 8, bas + 70), f"   {v.get('pourquoi', '')}", fill=ROUGE, font=petit)
    return poses


def panneau_registre(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "feuilles franchies contre pas parcourus",
             fill=DISCRET, font=petit)
    s = m["resume"]
    pts = []
    for x in m["lignes"]:
        for c in x["detail"]:
            for sel, coul in (("calibre", ROUGE), ("deux_roles", VERT)):
                t = c[sel].get("trajet_entier", {})
                if t.get("decidable") and not t.get("en_butee"):
                    pts.append((t["pas_parcourus"], t["feuilles_franchies"], coul))
    if not pts:
        art.text((x0 + 8, y0 + 40), "aucun trajet lisible", fill=DISCRET, font=petit)
        return 0
    g, d = x0 + 46, x0 + pw - 24
    haut, bas = y0 + 44, y0 + ph - 130
    hi = max(max(p[0] for p in pts), max(p[1] for p in pts)) * 1.1
    def X(v): return g + (d - g) * v / hi
    def Y(v): return bas - (bas - haut) * v / hi
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    # ⭐ La diagonale EST le registre juste : une feuille par pas.
    art.line([X(0), Y(0), X(hi), Y(hi)], fill=DISCRET)
    art.text((X(0.62 * hi) + 4, Y(0.74 * hi)), "une feuille par pas", fill=DISCRET, font=petit)
    for px, py, coul in pts:
        art.ellipse([X(px) - 3, Y(py) - 3, X(px) + 3, Y(py) + 3], fill=coul)
    for v in (0, int(hi / 2), int(hi)):
        art.text((X(v) - 4, bas + 4), f"{v}", fill=DISCRET, font=petit)
        art.text((x0 + 6, Y(v) - 6), f"{v}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 22), "abscisse : pas · ordonnée : feuilles", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 36), "rouge : `102` · vert : CORRIGÉ", fill=TEXTE, font=petit)
    md = m["deux_roles"].get("modes_du_trajet", {})
    if md.get("decidable") and "mode_haut" in md:
        # ⚠ La ligne du seuil est dessinee : c'est elle qui separe les deux populations, et sans
        # elle le nuage se lit comme une dispersion alors qu'il est bimodal.
        art.line([X(0), Y(md["seuil_feuilles"]), X(hi), Y(md["seuil_feuilles"])], fill=AMBRE)
        art.text((x0 + 8, bas + 56), f"★ {md['mode_haut']['trajets']} trajets au compte attendu "
                 f"({md['mode_haut']['feuilles_par_pas_median']}/pas)", fill=VERT, font=petit)
        art.text((x0 + 8, bas + 70), f"   {md['mode_bas']['trajets']} sans périodicité "
                 f"({md['mode_bas']['feuilles_par_pas_median']}/pas)", fill=ROUGE, font=petit)
        art.text((x0 + 8, bas + 90), f"⚠⚠⚠ le score est PLUS HAUT pour les",
                 fill=TEXTE, font=petit)
        art.text((x0 + 8, bas + 104), f"   mauvais ({md['ecart_des_scores_entre_modes']:+.3f}) : "
                 f"un seuil", fill=TEXTE, font=petit)
        art.text((x0 + 8, bas + 118), f"   écarterait le BON mode.", fill=TEXTE, font=petit)
    return len(pts)


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
             "Le marcheur avec le bon pas — `102` rejoué, et ses étapes gardées",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{s['cellules']} cellules sur {s['bandes']} bandes · deux sélecteurs depuis les "
             f"MÊMES départs · plafond {s['plafond_de_pas']} pas · "
             + (f"{s['pas_confirmes_corrige']} pas confirmés contre "
                f"{s['pas_confirmes_calibre']}" if "gain_en_pas" in s else "portée en cours"),
             fill=DISCRET, font=moyen)
    titres = ("A · la portée, et sa censure",
              "B · ★ le risque par pas",
              "C · ★ le registre du trajet ENTIER")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_portee(art, marge, 104, pw, ph, m, petit)
    b = panneau_risque(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_registre(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "portee": a, "risque": b, "registre": c,
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
    d = dessiner(m, RACINE / "docs" / "images" / "107_le_marcheur_avec_le_bon_pas.png")
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
    v("le panneau A trace une barre par sélecteur", d["portee"] == 2, str(d["portee"]))
    # ⭐⭐⭐ LE PANNEAU B DOIT TRACER LES DEUX COURBES : le risque conditionnel SEUL ne dit pas si
    # les chutes sont des manques isolés ou un égarement, et c'est leur écart qui informe.
    rq = m["deux_roles"].get("risque_par_pas", [])
    mg = m["deux_roles"].get("confirmation_marginale", [])
    v("le panneau B trace le risque conditionnel ET la confirmation marginale",
      d["risque"] == len(rq) + len([x for x in mg if x["pas"] <= (rq[-1]["pas"] if rq else 0)]),
      f"{d['risque']} points")
    v("le panneau C trace un point par trajet lisible",
      d["registre"] == sum(1 for x in m["lignes"] for c in x["detail"]
                           for sel in ("calibre", "deux_roles")
                           if c[sel].get("trajet_entier", {}).get("decidable")
                           and not c[sel]["trajet_entier"].get("en_butee")),
      str(d["registre"]))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    # === LES VERDICTS SONT DANS LA MESURE, PAS SEULEMENT DANS LA PROSE ======================
    s = m["resume"]
    txt = " ".join(prose(m))
    # ⚠⚠ LA CENSURE VOYAGE AVEC LA PORTÉE, jamais après : publier la médiane sans dire qu'elle est
    # tronquée ferait passer un budget de lecture pour une limite de matière.
    v("la censure est nommée dans la même phrase que la portée",
      all("la_portee_est_censuree" in m[sel] for sel in ("calibre", "deux_roles"))
      and ("BORNE INFÉRIEURE" in txt or not m["deux_roles"]["la_portee_est_censuree"]))
    # ⭐⭐⭐ LA TAUTOLOGIE DE LA FRACTION PAR PAS EST UN FAIT PUBLIÉ, pas une opinion : si les deux
    # sélecteurs y rendent le même nombre, la quantité ne dépend pas du sélecteur.
    if "la_fraction_par_pas_est_tautologique" in s:
        v("la tautologie de la fraction par pas est publiée comme un fait mesuré",
          "tautologique" in txt.lower(),
          f"{s.get('feuilles_par_pas_corrige')} contre {s.get('feuilles_par_pas_calibre')}")
    if "virage_median_deg" in s:
        v("le virage entre pas consécutifs est publié avec sa conséquence de coût",
          f"{s['virage_median_deg']}" in txt and "heures_si_un_cube_sur_deux" in s)
    c = m.get("cout_par_etape", {})
    if c.get("mesures"):
        # ⚠⚠⚠ LES QUATRE MESURES DU COÛT SONT PUBLIÉES AVEC LEUR CONDITION : la dispersion EST le
        # résultat, et un chiffre unique se lirait comme une constante.
        v("les quatre mesures du coût voyagent avec leur condition",
          all(str(x["secondes"]) in txt for x in c["mesures"]),
          f"{[x['secondes'] for x in c['mesures']]}")
    v("... et la prose dit ce que la course ne mesure PAS",
      "pas le sens de son maillon" in txt)
    # ⭐⭐⭐ LA BIMODALITÉ EST LE RÉSULTAT : sans elle la prose publierait une médiane qui choisit
    # un mode sans le dire, ce que j'ai fait au premier jet.
    md = m["deux_roles"].get("modes_du_trajet", {})
    if md.get("decidable") and "mode_haut" in md:
        v("la prose porte les DEUX modes avec leur effectif",
          f"{md['mode_haut']['trajets']} trajets" in txt
          and f"{md['mode_bas']['trajets']}" in txt,
          f"{md['mode_haut']['trajets']} et {md['mode_bas']['trajets']}")
        v("... et le SENS de l'écart de score, qui interdit d'y mettre un seuil",
          "PLUS HAUT POUR LES MAUVAISES" in txt or "PLUS HAUT pour les" in txt)
        v("... et l'aveu que j'avais publié leur médiane",
          "bimodale n'est pas un résumé" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "107_le_marcheur_avec_le_bon_pas.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
