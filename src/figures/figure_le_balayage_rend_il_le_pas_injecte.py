#!/usr/bin/env python3
"""Le balayage rend-il le pas injecte ? — le selecteur de production choisit un cran trop haut.

★★★ LE PANNEAU A EST L'ALLER-RETOUR, ET IL SE LIT D'UN COUP D'OEIL : la diagonale est la verite,
le selecteur BRUT la suit, et le CALIBRE est au-dessus a chaque periode et a chaque bruit.

★★★ LE PANNEAU B PORTE LE MECANISME : le nul decroit avec la longueur du candidat, donc un
candidat plus long dont l'accord BRUT est moins bon obtient un score CALIBRE meilleur. Ce n'est pas
du bruit, c'est de l'arithmetique.

★★★ LE PANNEAU C EST LE CONTROLE APPARIE SUR LE VRAI VOLUME : les memes lectures, trois
selecteurs. Comparer trois populations differentes ferait dire au resultat ce qu'on veut.

Usage :
    uv run python src/figures/figure_le_balayage_rend_il_le_pas_injecte.py --verifier
    uv run python src/figures/figure_le_balayage_rend_il_le_pas_injecte.py \\
        --sortie docs/images/105_le_balayage_rend_il_le_pas_injecte.png
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
MESURE = RACINE / "docs" / "mesures" / "le_balayage_rend_il_le_pas_injecte.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    b = m["biais_fabrique"]
    s = m["resume"]
    c = m.get("ce_que_ca_change_pour_99", {})
    mec = m["mecanisme"]
    p = s.get("pas_median_par_selecteur_um", {})
    lignes = [
        f"★★★ LE SÉLECTEUR QUE `99` UTILISE NE REND PAS LA PÉRIODE QU'ON LUI INJECTE. Sur des "
        f"profils FABRIQUÉS dont la réponse est exacte, le sélecteur BRUT retrouve la période au "
        f"cran près (biais médian {b['brut']['biais_relatif_median']:+.4f}) là où le sélecteur "
        f"CALIBRÉ, celui que la mesure appelle, lit "
        f"{b['calibre']['biais_relatif_median']:+.1%} trop haut, jusqu'à "
        f"{b['calibre']['biais_relatif_max']:+.1%}.",
        f"★★★ ET LA BATTERIE DE `99` NE POUVAIT PAS LE VOIR : elle a bien un contrôle "
        f"aller-retour, mais il relit par `pas_montre`, le sélecteur BRUT, alors que `mesurer` "
        f"appelle `pas_montre_calibre`. C'est une forme neuve d'une faute que ce dépôt recense "
        f"déjà : une vérification qui n'emprunte pas le chemin de la production.",
        f"★★ LE MÉCANISME EST MESURÉ, PAS SUPPOSÉ. Le nul par candidat décroît avec la longueur "
        f"(µ de {mec['mu_le_plus_court']} au plus court à {mec['mu_le_plus_long']} au plus long, "
        f"σ de {mec['sd_le_plus_court']} à {mec['sd_le_plus_long']}), et la calibration divise "
        f"par cet écart-type décroissant. Sur {mec['periode_injectee_um']:.0f} µm injectés, le "
        f"calibré retient {mec['choix_calibre_um']} µm avec un accord brut de "
        f"{mec['accord_brut_du_choix_calibre']} contre {mec['accord_brut_du_choix_brut']} pour le "
        f"choix brut : il préfère un candidat qui colle MOINS bien.",
        f"★★★ LE REMÈDE EST LE PATRON QUE CE DÉPÔT APPLIQUE DÉJÀ UN ÉTAGE PLUS HAUT — deux rôles, "
        f"deux statistiques. Le score CALIBRÉ décide si la matière a répondu, le score BRUT "
        f"choisit lequel des candidats admis colle le mieux, exactement comme `102` sépare `99` "
        f"qui DÉCIDE de l'avance et `98` qui VÉRIFIE ce qu'elle a traversé. Biais médian "
        f"{b['deux_roles']['biais_relatif_median']:+.4f}.",
        f"⚠⚠ ET LA CALIBRATION N'EST PAS JETÉE, ce que la mesure impose : sans garde, le sélecteur "
        f"brut se rue sur les candidats courts et rend une valeur sous le nominal sur du BRUIT "
        f"PUR — la panne d'origine de `99`, qui lisait 147 µm sur le vrai volume comme sur du "
        f"bruit. Elle reste la GARDE ; seul le CHOIX parmi les candidats admis change.",
    ]
    if p.get("brut") is not None:
        lignes.append(
            f"★★★ ET LE CONTRÔLE APPARIÉ SUR LE VRAI VOLUME LE CONFIRME : sur les MÊMES lectures "
            f"de {s['bandes_lues']} bandes, le calibré lit {p['calibre']} µm là où le brut lit "
            f"{p['brut']} µm, soit {s['ecart_relatif']:+.1%}. Trois populations différentes "
            f"auraient fait dire au résultat ce qu'on veut ; une seule lecture par cellule ne le "
            f"permet pas.")
    w = m.get("consequence_pour_le_marcheur")
    if w:
        lignes.append(
            f"★★★ ET LA CONSÉQUENCE POUR LE MARCHEUR DE `102` EST DIRECTE, PARCE QU'IL AVANCE DE "
            f"CE QUE CE SÉLECTEUR REND. Son pas vaut {w['pas_du_marcheur_um']} µm là où le pas "
            f"vrai indiqué est {w['pas_vrai_indique_um']} : il franchit "
            f"{w['feuilles_franchies_par_pas']} feuille à chaque pas, donc cent vingt pas en "
            f"franchissent {w['spires_apres_120_pas']:.0f} — {w['spires_en_trop_sur_120']:.0f} "
            f"spires de trop. ⚠⚠ Et ce dépassement tombe DANS la bande d'acceptation que `104` a "
            f"mesurée ({w['bande_dacceptation_de_104'][0]} à "
            f"{w['bande_dacceptation_de_104'][1]}) : chaque pas est donc CONFIRMÉ et rien ne le "
            f"signale. C'est le cas « biais » que `104` opposait au cas « taux d'échec », mesuré "
            f"cette fois au lieu d'être hypothétique.")
    if c.get("periode_vraie_indiquee_um"):
        lignes.append(
            f"⚠ CE QUE ÇA CHANGE POUR L'ÉCART OUVERT DEPUIS `99` : injecter "
            f"{c['periode_vraie_indiquee_um']} µm fait rendre au sélecteur de production "
            f"exactement les {c['publie_par_99_um']} µm publiés, donc l'écart aux transferts "
            f"humains ({c['pas_des_transferts_humains_um']} µm) passe de "
            f"{c['ecart_publie_en_pourcent']} % à {c['ecart_indique_en_pourcent']} % : "
            f"{c['part_de_lecart_imputable_a_linstrument']:.0%} de l'écart est imputable à "
            f"l'INSTRUMENT, et les trois quarts restants ne sont toujours pas expliqués. "
            f"⚠⚠ Indication et non mesure : la carte d'étalonnage est établie sur un profil "
            f"sinusoïdal parfait.")
    return lignes


def panneau_aller_retour(art, x0, y0, pw, ph, m, petit) -> int:
    """La diagonale est la vérité ; le calibré est au-dessus partout."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "période injectée → période lue (µm)", fill=DISCRET, font=petit)
    lignes = [x for x in m["aller_retour"]["lignes"] if x["bruit"] == 15.0]
    g, d = x0 + 46, x0 + pw - 22
    haut, bas = y0 + 40, y0 + ph - 96
    lo, hi = 130.0, 290.0
    def X(v): return g + (d - g) * (v - lo) / (hi - lo)
    def Y(v): return bas - (bas - haut) * (v - lo) / (hi - lo)
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    art.line([X(lo), Y(lo), X(hi), Y(hi)], fill=DISCRET)
    # ⚠ L'etiquette est posee SOUS la diagonale : au-dessus elle tombait sur un point trace.
    art.text((X(232.0) + 6, Y(214.0)), "vérité", fill=DISCRET, font=petit)
    poses = 0
    for x in lignes:
        v = x["periode_injectee_um"]
        if not lo <= v <= hi:
            continue
        for nom, coul, ray in (("calibre", ROUGE, 4), ("brut", VERT, 3)):
            lu = x[nom]["lu_median_um"]
            if not lo <= lu <= hi:
                continue
            art.ellipse([X(v) - ray, Y(lu) - ray, X(v) + ray, Y(lu) + ray], fill=coul)
            poses += 1
    for v in (150, 200, 250):
        art.text((X(v) - 10, bas + 4), f"{v}", fill=DISCRET, font=petit)
        art.text((x0 + 8, Y(v) - 6), f"{v}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 22), "vert : sélecteur BRUT", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 36), "rouge : sélecteur CALIBRÉ (production)", fill=ROUGE, font=petit)
    b = m["biais_fabrique"]
    art.text((x0 + 8, bas + 56), f"★ biais médian brut "
             f"{b['brut']['biais_relatif_median']:+.4f},", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 70), f"   calibré "
             f"{b['calibre']['biais_relatif_median']:+.4f}, deux rôles "
             f"{b['deux_roles']['biais_relatif_median']:+.4f}.", fill=ROUGE, font=petit)
    return poses


def panneau_mecanisme(art, x0, y0, pw, ph, m, petit) -> int:
    """Le nul décroît avec la longueur : le calibré préfère un accord brut moins bon."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "pourquoi le calibré dérive vers le long",
             fill=DISCRET, font=petit)
    mec = m["mecanisme"]
    # ⭐⭐⭐ LE PANNEAU EST ZOOME SUR LA REGION DU CROISEMENT. L'ecart entre les deux argmax vaut
    # UN cran de balayage ; trace sur toute la fenetre il serait invisible, et une figure qui
    # illustre un mecanisme sans le montrer ne sert a rien.
    centre = 0.5 * (mec["choix_brut_um"] + mec["choix_calibre_um"])
    n = [x for x in mec["nul_par_candidat"] if abs(x["longueur_um"] - centre) <= 46.0]
    g, d = x0 + 46, x0 + pw - 24
    haut, bas = y0 + 44, y0 + ph - 116
    lo = min(x["longueur_um"] for x in n)
    hi = max(x["longueur_um"] for x in n)
    def X(v): return g + (d - g) * (v - lo) / max(hi - lo, 1e-9)
    art.line([g, bas, d, bas], fill=CADRE)
    poses = 0
    for cle, coul in (("accord_brut", VERT), ("score_calibre", ROUGE)):
        vals = [x[cle] for x in n]
        mx, mn = max(vals), min(vals)
        etendue = max(mx - mn, 1e-9)
        pts = [(X(x["longueur_um"]), bas - (bas - haut) * (x[cle] - mn) / etendue) for x in n]
        for i in range(len(pts) - 1):
            art.line([pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]], fill=coul)
        for px, py in pts:
            art.ellipse([px - 2, py - 2, px + 2, py + 2], fill=coul)
            poses += 1
    # ⚠ Les deux argmax sont MARQUES : c'est leur ecart d'un cran qui est le sujet du panneau.
    for val, coul in ((mec["choix_brut_um"], VERT), (mec["choix_calibre_um"], ROUGE)):
        art.line([X(val), haut - 8, X(val), bas + 4], fill=coul)
        art.text((X(val) - 16, haut - 24), f"{val:.0f}", fill=coul, font=petit)
    for v in (int(lo) + 5, int(centre), int(hi) - 5):

        art.text((X(v) - 12, bas + 4), f"{v}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 22), "chacune à sa propre échelle, zoom sur le croisement",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 36), "vert : accord BRUT   rouge : score CALIBRÉ",
             fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 50), f"µ du nul : {mec['mu_le_plus_court']} → "
             f"{mec['mu_le_plus_long']} (court → long)", fill=BLEU, font=petit)
    art.text((x0 + 8, bas + 70), f"★ sur {mec['periode_injectee_um']:.0f} µm injectés :",
             fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 84), f"   brut → {mec['choix_brut_um']} µm "
             f"(accord {mec['accord_brut_du_choix_brut']})", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 98), f"   calibré → {mec['choix_calibre_um']} µm "
             f"(accord {mec['accord_brut_du_choix_calibre']})", fill=ROUGE, font=petit)
    return poses


def panneau_apparie(art, x0, y0, pw, ph, m, petit) -> int:
    """Les mêmes lectures du vrai volume, lues par deux sélecteurs."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "vrai volume, mêmes lectures, deux sélecteurs",
             fill=DISCRET, font=petit)
    lignes = [x for x in m.get("lignes", [])
              if x.get("brut", {}).get("pas_median_um") is not None
              and x.get("calibre", {}).get("pas_median_um") is not None]
    if not lignes:
        art.text((x0 + 8, y0 + 40), "aucune bande appariée", fill=DISCRET, font=petit)
        return 0
    g, d = x0 + 46, x0 + pw - 22
    haut, bas = y0 + 40, y0 + ph - 116
    vals = [x[n]["pas_median_um"] for x in lignes for n in ("brut", "calibre")]
    lo, hi = min(vals) - 10, max(vals) + 10
    def X(v): return g + (d - g) * (v - lo) / (hi - lo)
    def Y(v): return bas - (bas - haut) * (v - lo) / (hi - lo)
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    # ⭐ La diagonale EST le fait : si les deux selecteurs lisaient pareil, tout serait dessus.
    art.line([X(lo), Y(lo), X(hi), Y(hi)], fill=DISCRET)
    art.text((X(lo + 0.72 * (hi - lo)) + 4, Y(lo + 0.86 * (hi - lo))),
             "égalité", fill=DISCRET, font=petit)
    poses = 0
    for x in lignes:
        art.ellipse([X(x["brut"]["pas_median_um"]) - 3, Y(x["calibre"]["pas_median_um"]) - 3,
                     X(x["brut"]["pas_median_um"]) + 3, Y(x["calibre"]["pas_median_um"]) + 3],
                    fill=ROUGE)
        poses += 1
    art.text((x0 + 8, bas + 22), "abscisse : lu par le BRUT", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 36), "ordonnée : lu par le CALIBRÉ", fill=ROUGE, font=petit)
    s = m["resume"]
    p = s["pas_median_par_selecteur_um"]
    art.text((x0 + 8, bas + 56), f"★ {len(lignes)} bandes, toutes au-dessus", fill=TEXTE,
             font=petit)
    art.text((x0 + 8, bas + 70), f"   de la diagonale d'égalité.", fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 90), f"★ médianes : brut {p['brut']},", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 104), f"   calibré {p['calibre']} "
             f"({s['ecart_relatif']:+.1%})", fill=ROUGE, font=petit)
    return poses


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
    b = m["biais_fabrique"]
    s = m["resume"]
    art.text((marge, 16),
             "Le balayage rend-il le pas injecté ? — le sélecteur de production choisit un cran "
             "trop haut", fill=TEXTE, font=gros)
    p = s.get("pas_median_par_selecteur_um", {})
    art.text((marge, 40),
             f"biais médian du sélecteur brut {b['brut']['biais_relatif_median']:+.4f}, du "
             f"calibré {b['calibre']['biais_relatif_median']:+.4f}"
             + (f" · sur le vrai volume {p['brut']} contre {p['calibre']} µm "
                f"({s['ecart_relatif']:+.1%}), {s['bandes_lues']} bandes appariées"
                if p.get("brut") is not None else ""),
             fill=DISCRET, font=moyen)
    titres = ("A · NON — le calibré lit au-dessus de la vérité",
              "B · ★ le mécanisme : le nul décroît",
              "C · ★ le contrôle apparié, vrai volume")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_aller_retour(art, marge, 104, pw, ph, m, petit)
    mm = panneau_mecanisme(art, marge + pw + ecart, 104, pw, ph, m, petit)
    ap = panneau_apparie(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "aller_retour": a, "mecanisme": mm, "apparie": ap,
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
                 / "105_le_balayage_rend_il_le_pas_injecte.png")
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
    # ⭐⭐⭐ LE PANNEAU A DOIT TRACER LES DEUX SELECTEURS, pas un : c'est leur ECART qui EST le
    # resultat, et une seule courbe se lirait comme une mesure ordinaire.
    dedans = [x for x in m["aller_retour"]["lignes"]
              if x["bruit"] == 15.0 and 130.0 <= x["periode_injectee_um"] <= 290.0]
    v("le panneau A trace le brut ET le calibré", d["aller_retour"] >= 2 * len(dedans) - 2,
      f"{d['aller_retour']} points pour {len(dedans)} périodes")
    # ⚠ Le panneau B est ZOOME : le compte attendu porte sur les candidats de la fenetre, pas
    # sur toute la grille, sinon la garde exigerait des points que la figure ne doit pas tracer.
    centre = 0.5 * (m["mecanisme"]["choix_brut_um"] + m["mecanisme"]["choix_calibre_um"])
    zoom = [x for x in m["mecanisme"]["nul_par_candidat"]
            if abs(x["longueur_um"] - centre) <= 46.0]
    v("le panneau B trace les deux scores sur la fenêtre du croisement",
      d["mecanisme"] == 2 * len(zoom), f"{d['mecanisme']} pour {2 * len(zoom)}")
    n = len([x for x in m["lignes"] if x["brut"]["pas_median_um"] is not None])
    v("le panneau C trace un point par bande appariée", d["apparie"] == n,
      f"{d['apparie']} pour {n}")
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    # === LES VERDICTS SONT DANS LA MESURE, PAS SEULEMENT DANS LA PROSE ======================
    s = m["resume"]
    v("le verdict est rendu, quel qu'il soit",
      "le_calibre_est_biaise_haut" in s and "les_deux_roles_corrigent_le_biais" in s)
    # ⭐⭐⭐ LE CONTROLE QUI AUTORISE A PUBLIER : la longueur du remede doit differer du nul.
    v("la longueur du remède est confrontée au nul, et en diffère",
      s.get("la_longueur_du_remede_differe_du_nul") is True,
      f"médiane du nul {s.get('mediane_du_nul_pour_le_remede_um')} µm")
    v("... et les trois sélecteurs sont confrontés au MÊME nul",
      set(m["la_longueur_differe_du_nul"]) == {"brut", "calibre", "deux_roles"})
    # ⚠⚠ LA CONSEQUENCE POUR LE MARCHEUR VOYAGE AVEC LA BANDE DE `104`, jamais seule : sans elle
    # « 1,18 feuille par pas » se lirait comme un ecart qu'une verification attraperait.
    w = m.get("consequence_pour_le_marcheur", {})
    v("la conséquence pour le marcheur porte la bande d'acceptation de `104`",
      "bande_dacceptation_de_104" in w and "le_depassement_est_confirme_par_le_critere" in w)
    txt = " ".join(prose(m))
    v("la prose porte l'écart mesuré entre les deux sélecteurs",
      f"{s['ecart_relatif']:+.1%}".replace("%", "") in txt.replace("%", ""),
      f"{s['ecart_relatif']:+.1%}")
    v("... et le nombre de spires en trop sur cent vingt",
      f"{w['spires_en_trop_sur_120']:.0f}" in txt if w else False)
    v("... et le fait que la batterie de `99` exerce un autre chemin",
      "pas_montre" in txt and "pas_montre_calibre" in txt)
    v("... et que la calibration reste la GARDE", "GARDE" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "105_le_balayage_rend_il_le_pas_injecte.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
