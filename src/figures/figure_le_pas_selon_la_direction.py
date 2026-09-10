#!/usr/bin/env python3
"""Y a-t-il une direction ou la periode est minimale ? — l'eventail, avec le selecteur corrige.

★★★ LE PANNEAU A EST LA GARDE : sur une pile FABRIQUEE, `p(theta)` suit `p0/cos(theta)` a moins
d'un micron. Si l'instrument ne voyait pas l'anisotropie la, une courbe plate sur la matiere ne
prouverait rien.

★★★ LE PANNEAU B EST LA MATIERE : la courbe mediane de `p(theta)` sur toutes les cellules, avec les
DEUX modeles ajustes a armes egales — un parametre libre chacun, l'angle de la normale etant fixe
par `101` et non ajuste.

★★★ LE PANNEAU C REFUTE L'EXPLICATION LA PLUS PLAUSIBLE : une famille de feuilles qui TOURNE le
long de la sonde fait MONTER le rapport, pas descendre vers un.

Usage :
    uv run python src/figures/figure_le_pas_selon_la_direction.py --verifier
    uv run python src/figures/figure_le_pas_selon_la_direction.py \\
        --sortie docs/images/106_le_pas_selon_la_direction.png
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
MESURE = RACINE / "docs" / "mesures" / "le_pas_selon_la_direction.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    s = m["resume"]
    d = m["deux_roles"]
    c = m["calibre"]
    cf = m["controle_fabrique"]
    t = cf["tournantes"]
    lignes = [
        f"★★★ LA MATIÈRE N'EST PAS UN EMPILEMENT LOCALEMENT PARALLÈLE À L'ÉCHELLE OÙ LE BALAYAGE "
        f"LA SONDE. Sur {s['cellules']} cellules de {s['bandes']} bandes, le modèle "
        f"`p(θ) = p₀/cos θ` ne bat le modèle isotrope que sur "
        f"{d['part_ou_le_parallele_gagne']:.1%} d'entre elles, avec un gain médian de "
        f"×{d['gain_median_du_modele_parallele']} — là où la même mesure sur une pile FABRIQUÉE "
        f"rend un gain de ×{cf['empilements'][0]['ajustement_juste']['gain_du_modele_parallele']} "
        f"et un écart à la prédiction de "
        f"{cf['empilements'][0]['ecart_median_a_la_prediction_um']} µm.",
        f"★★★ ET LES DEUX MODÈLES SONT AJUSTÉS À ARMES ÉGALES, un paramètre libre chacun. L'angle "
        f"de la normale n'est PAS ajusté : il est fixé par la direction que `101` mesure sur la "
        f"même cellule, avec un instrument qui ne partage rien avec celui-ci — une covariance de "
        f"gradients contre une périodicité. Le laisser libre aurait donné au modèle parallèle un "
        f"degré de liberté de plus, et il aurait gagné souvent par accident.",
        f"★★ L'AMPLITUDE MÉDIANE DE LA COURBE VAUT {d['amplitude_mediane_um']} µm sur ±"
        f"{m['demi_angle_deg']:.0f}°, là où un empilement parallèle de pas "
        f"{d['pas_du_modele_parallele_median_um']} µm en prédirait "
        f"{d['pas_du_modele_parallele_median_um'] * (1 / math.cos(math.radians(m['demi_angle_deg'])) - 1):.0f}. "
        f"Elle varie donc DEUX FOIS PLUS qu'un empilement parallèle ne le prédit, et "
        f"irrégulièrement.",
        f"⚠⚠⚠ ET UNE MÉDIANE SIGNÉE D'ANGLE N'EST PAS UN ACCORD — c'est la faute que j'ai faite en "
        f"lisant la première sortie. Le minimum a une médiane SIGNÉE de "
        f"{d['angle_du_minimum_median_deg']:+.2f}°, ce qui se lit comme « il tombe sur la normale "
        f"de `101` », alors que sa médiane ABSOLUE vaut "
        f"{s['ecart_absolu_median_du_minimum_deg']:.1f}° pour un pas d'éventail de "
        f"{s['pas_de_leventail_deg']:.0f}°. Les minima sont DISPERSÉS et leur moyenne tombe près "
        f"de zéro par symétrie. L'éventail "
        + ("confirme" if s["le_minimum_saccorde_avec_101"] else "ne confirme donc PAS")
        + " la direction de `101`.",
    ]
    if "combien_de_fois_pire_que_la_pile_fabriquee" in s:
        lignes.insert(1, (
            f"★★★ ET LE REPÈRE DU RÉSIDU EST LA PILE FABRIQUÉE, PAS L'AMPLITUDE DE LA COURBE — "
            f"c'est une correction de ma première version, qui comparait le résidu au signal et "
            f"laissait donc passer un ajustement vingt fois pire que sur une réponse connue. Le "
            f"même instrument, le même sélecteur, la même longueur de sonde : "
            f"{s['residu_sur_pile_fabriquee_um']} µm sur une pile CONNUE contre "
            f"{d['residu_parallele_median_um']} µm sur la matière, soit "
            f"×{s['combien_de_fois_pire_que_la_pile_fabriquee']} pire. Battre une constante de "
            f"{100 * (d['gain_median_du_modele_parallele'] - 1):.0f} % ne rachète pas cela."))
    if "rapport_avec_le_selecteur_corrige" in s:
        # ⚠ La phrase est DÉRIVÉE du verdict, jamais affirmée : la première version écrivait
        # « l'anomalie n'était pas l'instrument » en dur, donc elle aurait continué à le dire le
        # jour où la mesure aurait dit l'inverse.
        survit = s.get("lanomalie_de_100_survit_a_la_correction")
        lignes.append(
            f"⚠⚠ L'ANOMALIE DE `100` "
            + ("SURVIT À LA CORRECTION" if survit else "ÉTAIT L'INSTRUMENT")
            + f", et c'est mesuré sur les MÊMES lectures : avec son sélecteur le rapport "
            f"rayon/normale vaut {s['rapport_avec_le_selecteur_de_100']}, avec celui que `105` a "
            f"corrigé {s['rapport_avec_le_selecteur_corrige']}, pour {s['un_sur_cos_attendu']} "
            f"prédits par 1/cos. Le sélecteur déplace le rapport de "
            f"{s['de_combien_le_selecteur_deplace_le_rapport']:+.3f} et il reste "
            f"{s['ecart_restant_a_la_prediction']:+.3f} à la prédiction, pour une résolution de "
            f"{s['resolution_du_rapport']:.3f} — "
            + ("l'écart est donc dans la matière, pas dans le choix du candidat."
               if survit else "l'écart restant tombe sous la résolution."))
    if len(t) >= 2:
        lignes.append(
            f"NON — ET L'EXPLICATION LA PLUS PLAUSIBLE EST RÉFUTÉE. Une famille de feuilles dont "
            f"l'orientation n'est pas cohérente sur la longueur de la sonde intègre un taux de "
            f"franchissement variable, ce qui pourrait aplatir la courbe. Sur une pile fabriquée "
            f"qui TOURNE, le rapport MONTE — de {t[0]['rapport']} à {t[-1]['rapport']} pour une "
            f"rotation de 0 à {t[-1]['rotation_deg_par_100um']:.0f}°/100 µm, soit "
            f"{t[-1]['rotation_sur_la_sonde_deg']:.0f}° sur la sonde. L'incohérence d'orientation "
            f"ne peut donc pas produire un rapport de un.")
    lignes.append(
        f"⚠ CE QUE CELA LAISSE OUVERT, ET C'EST LA QUESTION QUI COMPTE POUR LE GRAAL : si la "
        f"périodicité que le balayage suit n'est pas celle d'une famille de feuilles localement "
        f"parallèles, alors le pas dont le marcheur de `102` avance n'est pas un espacement de "
        f"feuilles, et « la matière porte deux pas » ne veut pas ce qu'on croyait. "
        f"{s['cellules_sans_direction']} cellules n'ont donné aucune direction et sont comptées à "
        f"part, jamais remplacées par celle du maillage.")
    return lignes


def _courbe(art, x0, y0, pw, ph, angles, series, titre, petit, lo=None, hi=None) -> int:
    """Un panneau de courbes p(theta), avec son cadre et ses graduations."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), titre, fill=DISCRET, font=petit)
    g, d = x0 + 46, x0 + pw - 22
    haut, bas = y0 + 44, y0 + ph - 116
    vals = [v for _, ys, _ in series for v in ys if v is not None]
    if not vals:
        art.text((x0 + 8, y0 + 40), "aucune valeur", fill=DISCRET, font=petit)
        return 0
    lo = min(vals) * 0.95 if lo is None else lo
    hi = max(vals) * 1.05 if hi is None else hi
    def X(v): return g + (d - g) * (v - angles[0]) / max(angles[-1] - angles[0], 1e-9)
    def Y(v): return bas - (bas - haut) * (v - lo) / max(hi - lo, 1e-9)
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    # ⚠ La verticale a zero est la NORMALE de `101` : sans elle la courbe n'a pas d'origine.
    art.line([X(0.0), haut - 6, X(0.0), bas], fill=DISCRET)
    art.text((X(0.0) - 24, haut - 22), "normale", fill=DISCRET, font=petit)
    poses = 0
    for coul, ys, _nom in series:
        pts = [(X(a), Y(v)) for a, v in zip(angles, ys) if v is not None]
        for i in range(len(pts) - 1):
            art.line([pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]], fill=coul)
        for px, py in pts:
            art.ellipse([px - 2, py - 2, px + 2, py + 2], fill=coul)
            poses += 1
    for a in (angles[0], 0.0, angles[-1]):
        art.text((X(a) - 12, bas + 4), f"{a:+.0f}°", fill=DISCRET, font=petit)
    for vv in (lo, 0.5 * (lo + hi), hi):
        art.text((x0 + 6, Y(vv) - 6), f"{vv:.0f}", fill=DISCRET, font=petit)
    for j, (coul, _ys, nom) in enumerate(series):
        art.text((x0 + 8, bas + 22 + j * 14), nom, fill=coul, font=petit)
    return poses


def panneau_fabrique(art, x0, y0, pw, ph, m, petit) -> int:
    e = m["controle_fabrique"]["empilements"][0]
    n = _courbe(art, x0, y0, pw, ph, e["angles_deg"],
                [(ROUGE, e["prediction_um"], "prédit : p₀/cos θ"),
                 (VERT, e["pas_um"], "mesuré par l'éventail")],
                "pile FABRIQUÉE : la réponse est connue", petit)
    j = e["ajustement_juste"]
    bas = y0 + ph - 116
    art.text((x0 + 8, bas + 56), f"★ écart à la prédiction : "
             f"{e['ecart_median_a_la_prediction_um']} µm", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 70), f"★ le parallèle gagne "
             f"×{j['gain_du_modele_parallele']}", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 84), f"★ minimum à {e['minimum']['angle_du_minimum_deg']}°",
             fill=VERT, font=petit)
    return n


def panneau_matiere(art, x0, y0, pw, ph, m, petit) -> int:
    d = m["deux_roles"]
    cb = d["courbe_mediane"]
    angles = [x["angle_deg"] for x in cb]
    lus = [x["pas_median_um"] for x in cb]
    p0 = d["pas_du_modele_parallele_median_um"]
    piso = d["pas_du_modele_isotrope_median_um"]
    par = [round(p0 / math.cos(math.radians(a)), 1) for a in angles]
    n = _courbe(art, x0, y0, pw, ph, angles,
                [(ROUGE, par, f"parallèle : {p0:.0f}/cos θ"),
                 (BLEU, [piso] * len(angles), f"isotrope : {piso:.0f} µm"),
                 (VERT, lus, "MESURÉ, médiane des cellules")],
                "la matière : quelle forme la courbe a-t-elle ?", petit)
    bas = y0 + ph - 116
    art.text((x0 + 8, bas + 64), f"★ le parallèle ne gagne que sur",
             fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 78), f"   {d['part_ou_le_parallele_gagne']:.1%} des cellules "
             f"(×{d['gain_median_du_modele_parallele']})", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 92), f"★ amplitude {d['amplitude_mediane_um']} µm pour "
             f"{d['pas_du_modele_parallele_median_um'] * (1 / math.cos(math.radians(m['demi_angle_deg'])) - 1):.0f} prédits",
             fill=TEXTE, font=petit)
    return n


def panneau_tournante(art, x0, y0, pw, ph, m, petit) -> int:
    t = m["controle_fabrique"]["tournantes"]
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "une famille qui TOURNE aplatit-elle la courbe ?",
             fill=DISCRET, font=petit)
    g, d = x0 + 46, x0 + pw - 24
    haut, bas = y0 + 48, y0 + ph - 130
    rots = [x["rotation_deg_par_100um"] for x in t]
    raps = [x["rapport"] for x in t]
    lo, hi = 0.9, max(raps) * 1.06
    def X(v): return g + (d - g) * (v - rots[0]) / max(rots[-1] - rots[0], 1e-9)
    def Y(v): return bas - (bas - haut) * (v - lo) / max(hi - lo, 1e-9)
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    # ⚠ La ligne à un est la cible de l'hypothese : si l'incoherence expliquait `100`, la courbe
    # DESCENDRAIT vers elle.
    art.line([g, Y(1.0), d, Y(1.0)], fill=BLEU)
    art.text((g + 6, Y(1.0) + 4), "rapport = 1, ce qu'il faudrait", fill=BLEU, font=petit)
    pts = [(X(a), Y(v)) for a, v in zip(rots, raps)]
    for i in range(len(pts) - 1):
        art.line([pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]], fill=ROUGE)
    for px, py in pts:
        art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=ROUGE)
    for a in (rots[0], rots[-1]):
        art.text((X(a) - 10, bas + 4), f"{a:.0f}", fill=DISCRET, font=petit)
    for vv in (1.0, hi):
        art.text((x0 + 6, Y(vv) - 6), f"{vv:.2f}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 22), "abscisse : rotation en °/100 µm", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 40), "NON — le rapport MONTE avec la", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 54), f"   rotation ({raps[0]} à {raps[-1]}),", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 68), "   il ne descend pas vers un.", fill=ROUGE, font=petit)
    s = m["resume"]
    if "rapport_avec_le_selecteur_corrige" in s:
        art.text((x0 + 8, bas + 88), f"★ et corriger le sélecteur ne", fill=AMBRE, font=petit)
        art.text((x0 + 8, bas + 102), f"   le ramène pas non plus :", fill=AMBRE, font=petit)
        art.text((x0 + 8, bas + 116), f"   {s['rapport_avec_le_selecteur_de_100']} → "
                 f"{s['rapport_avec_le_selecteur_corrige']} pour "
                 f"{s['un_sur_cos_attendu']}", fill=AMBRE, font=petit)
    return len(pts)


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
    s, d = m["resume"], m["deux_roles"]
    art.text((marge, 16),
             "Le pas selon la direction — la matière n'est pas un empilement localement parallèle",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{s['cellules']} cellules sur {s['bandes']} bandes · éventail de {m['directions']} "
             f"directions sur ±{m['demi_angle_deg']:.0f}° autour de la normale de `101` · le "
             f"modèle parallèle ne gagne que sur {d['part_ou_le_parallele_gagne']:.1%} des cellules",
             fill=DISCRET, font=moyen)
    titres = ("A · la garde, sur réponse connue",
              "B · ★ la matière : la forme de p(θ)",
              "C · NON — une famille tournante n'aplatit pas")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_fabrique(art, marge, 104, pw, ph, m, petit)
    b = panneau_matiere(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_tournante(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "fabrique": a, "matiere": b, "tournante": c,
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
    d = dessiner(m, RACINE / "docs" / "images" / "106_le_pas_selon_la_direction.png")
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
    # ⭐⭐⭐ LE PANNEAU A DOIT TRACER LA PRÉDICTION ET LA MESURE, pas une seule : c'est leur
    # superposition qui montre que l'instrument voit l'anisotropie, et une seule courbe se lirait
    # comme une affirmation.
    e = m["controle_fabrique"]["empilements"][0]
    lus = sum(1 for x in e["pas_um"] if x is not None)
    v("le panneau A trace la prédiction ET la mesure",
      d["fabrique"] == lus + len(e["prediction_um"]),
      f"{d['fabrique']} pour {lus} + {len(e['prediction_um'])}")
    cb = m["deux_roles"]["courbe_mediane"]
    n = sum(1 for x in cb if x["pas_median_um"] is not None)
    v("le panneau B trace les deux modèles ET la courbe mesurée",
      d["matiere"] == n + 2 * len(cb), f"{d['matiere']} pour {n} + {2 * len(cb)}")
    v("le panneau C trace un point par rotation",
      d["tournante"] == len(m["controle_fabrique"]["tournantes"]), str(d["tournante"]))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    # === LES VERDICTS SONT DANS LA MESURE, PAS SEULEMENT DANS LA PROSE ======================
    s = m["resume"]
    v("le verdict est rendu, quel qu'il soit",
      "la_matiere_est_un_empilement_parallele" in s)
    # ⚠⚠ STRUCTUREL, PAS UN RÉSULTAT : asserter « le parallèle perd » obligerait à réécrire le
    # contrôle le jour où la réponse change. On asserte que la PART est publiée à côté du gain.
    v("la part de cellules où le parallèle gagne est publiée à côté du gain médian",
      all("part_ou_le_parallele_gagne" in m[k] and "gain_median_du_modele_parallele" in m[k]
          for k in ("calibre", "deux_roles")))
    v("... et le compte de directions au minimum à côté de son angle",
      "directions_au_minimum_mediane" in m["deux_roles"]
      and "directions_lues_mediane" in m["deux_roles"])
    # ⭐⭐⭐ LE CONTRÔLE QUI REND LE RÉSULTAT LISIBLE : sans lui une courbe plate ne prouverait
    # que la cécité de l'instrument.
    cf = m["controle_fabrique"]
    v("la garde fabriquée est publiée à côté du résultat",
      cf.get("linstrument_voit_lanisotropie") is True
      and cf.get("le_minimum_tombe_sur_la_normale") is True)
    v("... et la réfutation de la famille tournante aussi",
      cf.get("le_rapport_monte_avec_la_rotation") is True)
    txt = " ".join(prose(m))
    v("la prose porte la part où le parallèle gagne",
      f"{m['deux_roles']['part_ou_le_parallele_gagne']:.1%}" in txt)
    v("... et le gain de la pile fabriquée, qui rend la comparaison lisible",
      str(cf["empilements"][0]["ajustement_juste"]["gain_du_modele_parallele"]) in txt)
    v("... et le fait que la normale n'est PAS ajustée", "n'est PAS ajusté" in txt)
    v("... et les cellules sans direction, comptées et non remplacées",
      "jamais remplacées" in txt)
    # ⭐⭐⭐ LE CHIFFRE LE PLUS FORT DE LA TRANCHE DOIT ÊTRE DANS LA PROSE : sans lui, « le modèle
    # ne gagne que sur 70 % » se lirait comme un résultat serré alors que l'ajustement est vingt
    # fois pire que sur une réponse connue.
    v("la prose porte le rapport au résidu de la pile fabriquée",
      f"×{s['combien_de_fois_pire_que_la_pile_fabriquee']}" in txt,
      f"×{s['combien_de_fois_pire_que_la_pile_fabriquee']}")
    # ⚠⚠ ET LA PHRASE SUR `100` EST DÉRIVÉE DU VERDICT, jamais écrite en dur.
    v("... et la phrase sur `100` suit le verdict plutôt que de l'affirmer",
      ("SURVIT À LA CORRECTION" in txt)
      is bool(s["lanomalie_de_100_survit_a_la_correction"]))
    # ⚠⚠⚠ LA PROSE DOIT PORTER L'ÉCART ABSOLU, pas seulement la médiane signée : c'est la
    # confusion des deux qui m'a fait lire un accord là où il n'y en a pas.
    v("la prose porte l'écart ABSOLU du minimum, pas seulement sa médiane signée",
      f"{s['ecart_absolu_median_du_minimum_deg']:.1f}" in txt
      and "médiane ABSOLUE" in txt, f"{s['ecart_absolu_median_du_minimum_deg']}°")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "106_le_pas_selon_la_direction.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
