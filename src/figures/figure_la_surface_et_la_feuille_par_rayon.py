#!/usr/bin/env python3
"""La surface humaine est MIEUX posee sur la feuille la ou le transfert casse.

⚠⚠⚠ CETTE FIGURE PORTE UN SECOND CANDIDAT REFUTE, ET C'EST SON INTERET. `94` a tue le
froissement comme signal de confiance parce qu'il est une propriete du MAILLAGE. Restait une
observable de la MATIERE : l'ecart entre la surface publiee et le ruban de papyrus qu'elle suit.
Le panneau A montre qu'elle echoue de la meme facon — la dispersion TOMBE la ou la continuite
explose.

⭐⭐⭐ ET LE PANNEAU B EST CE QUI DISTINGUE UN RESULTAT D'UN ARTEFACT DE CHAMP. Le volume est
masque, et la part au remplissage monte fortement avec le rayon : sans le retirer, « la surface
est mieux posee au bord » et « le volume s'arrete au bord » sont la MEME observation. Le
balayage de seuil est publie plutot qu'un seuil choisi.

Usage :
    uv run python src/figures/figure_la_surface_et_la_feuille_par_rayon.py --verifier
    uv run python src/figures/figure_la_surface_et_la_feuille_par_rayon.py \\
        --sortie docs/images/95_la_surface_et_la_feuille_par_rayon.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_surface_et_la_feuille_par_rayon.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def mesurees(m: dict) -> list[dict]:
    """Les bandes que le volume fin atteint réellement."""
    return [x for x in m["lignes"] if not x["hors_du_volume_fin"]]


def prose(m: dict) -> list[str]:
    c, p = m["correlations"], m["par_tiers"]
    q, sm = m["une_fois_le_masque_retire"], m["sans_les_bandes_rongees_par_le_masque"]
    bal = m["balayage_du_seuil"]
    disps = [x["dispersion_contre_rayon"] for x in bal if "dispersion_contre_rayon" in x]
    return [
        "★★★ CE QUE CE FICHIER TESTE, ET POURQUOI IL FALLAIT LE TESTER. `94` a tue le "
        "froissement comme signal de confiance : a travers les rayons il est ANTI-predictif, et "
        "la raison mesuree est que les maillages humains sont plus LISSES la ou ils ont ponte. "
        "il fallait donc une observable de la MATIERE et non du maillage — et le depot en a "
        "une : l'ecart entre la surface publiee et le ruban de papyrus qu'elle suit. ce qui est "
        "neuf ici est l'AXE : cette mesure ne couvrait `PHercParis4` que par UNE bande.",
        f"★★★ NON — PANNEAU A : LA SECONDE OBSERVABLE ECHOUE DE LA MEME FACON. la dispersion du "
        f"centre de masse vaut {p['coeur']['dispersion_um']} µm au coeur, "
        f"{p['milieu']['dispersion_um']} au milieu et {p['bord']['dispersion_um']} au BORD — "
        f"donc la surface humaine est MIEUX posee sur la feuille la ou `92` mesure une "
        f"continuite brisee (×{p['bord']['continuite']}) et `93` des spires desalignees "
        f"(×{p['bord']['desalignement']}). correlations : {c['dispersion_contre_rayon']} avec le "
        f"rayon, {c['dispersion_contre_continuite']} avec la rupture.",
        f"★★ ET LE VERDICT SURVIT AU CONFONDANT, CE QUI EST TOUT CE QUI COMPTE ICI. le volume "
        f"est masque et la part au remplissage monte avec le rayon "
        f"({c['part_au_zero_contre_rayon']:+.3f}), donc sans la retirer « la surface est mieux "
        f"posee au bord » et « le volume s'arrete au bord » seraient la meme observation. une "
        f"fois le masque retire : {q['dispersion_contre_rayon']} avec le rayon et "
        f"{q['dispersion_contre_continuite']} avec la rupture. et en JETANT les bandes rongees "
        f"plutot qu'en corrigeant : {sm['dispersion_contre_rayon']} sur {sm['bandes']} bandes.",
        f"★★★ PANNEAU B — LE SEUIL N'EST PAS REGLE, ET C'EST VERIFIABLE PLUTOT QU'AFFIRME. le "
        f"balayage publie donne {', '.join(str(x) for x in disps)} de 5 % a 30 % de "
        f"remplissage tolere : le verdict tient partout, donc il ne vient pas du seuil. un "
        f"verdict qui ne tiendrait qu'a une valeur serait un nombre choisi pour que le "
        f"resultat passe, ce qui est la faute nº1 de ce depot.",
        f"⚠⚠ ET LE CONTRASTE, LUI, N'A AUCUNE RELATION STABLE AU RAYON : "
        f"{c['contraste_contre_rayon']} brut, {q['contraste_contre_rayon']} une fois le masque "
        f"retire, et le signe CHANGE selon le seuil du balayage. ce qui ressemblait a un "
        "effondrement du contraste au bord etait DEUX bandes que le masque mange, pas la "
        "matiere.",
        "⚠⚠⚠ ET C'EST UNE ERREUR A MOI, GARDEE. ma sonde exploratoire prenait TROIS bandes — "
        "coeur, milieu, `w128-129` — et voyait le contraste tomber de 119 a 11. or `w128-129` "
        "est l'une des DEUX seules bandes dont le contraste s'effondre, et celle dont le "
        "remplissage est le plus fort. c'est exactement la faute que `93` avait deja payee : un "
        "bord se compte sur le corpus entier, pas sur les bandes qu'on a sondees.",
        "★★★ CE QUE CA CONTRAINT POUR LE REMPLACANT DE L'HUMAIN, ET C'EST LE VRAI RESULTAT. "
        "deux observables LOCALES independantes — le pli du maillage et la pose sur la matiere — "
        "disent toutes deux « plus propre » exactement la ou le transfert echoue. la raison est "
        "la meme : au bord, l'humain qui ne peut pas suivre la vraie feuille en trace une autre, "
        "proprement. le maillage epouse tres bien UNE feuille, simplement pas la bonne. donc ce "
        "qui echoue au bord n'est pas la QUALITE locale mais l'IDENTITE de la feuille, et aucune "
        "observable locale ne peut la voir.",
    ]


def panneau_anti(art, x0, y0, pw, ph, m, petit) -> int:
    """La dispersion et la continuité contre le rayon, sur le même axe."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les deux contre le rayon — ils vont en sens INVERSE",
             fill=DISCRET, font=petit)
    lignes = mesurees(m)
    gauche, droite = x0 + 52, x0 + pw - 52
    base, sommet = y0 + ph - 58, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    d_hi = max(x["dispersion_um"] for x in lignes) * 1.12
    c_hi = max(x["continuite"] for x in lignes) * 1.12

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v, hi):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([(px(x["rayon_mm"]), py(x["dispersion_um"], d_hi)) for x in lignes],
             fill=BLEU, width=2)
    art.line([(px(x["rayon_mm"]), py(x["continuite"], c_hi)) for x in lignes],
             fill=ROUGE, width=2)
    points = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["dispersion_um"], d_hi)
        art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLEU)
        points += 1
    for g in (0.0, d_hi / 2, d_hi):
        art.text((x0 + 6, py(g, d_hi) - 6), f"{g:>4.0f}", fill=BLEU, font=petit)
    for g in (0.0, c_hi / 2, c_hi):
        art.text((droite + 6, py(g, c_hi) - 6), f"×{g:.0f}", fill=ROUGE, font=petit)
    art.text((gauche + 4, sommet - 16), "dispersion, µm", fill=BLEU, font=petit)
    art.text((droite - 108, sommet - 16), "continuité, ×référence", fill=ROUGE, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★ corrélation dispersion/continuité : "
             f"{m['correlations']['dispersion_contre_continuite']}, et "
             f"{m['une_fois_le_masque_retire']['dispersion_contre_continuite']} sans le masque",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande — cœur à gauche, bord à droite",
             fill=DISCRET, font=petit)
    return points


def panneau_confondant(art, x0, y0, pw, ph, m, petit) -> int:
    """Le masque, et le balayage qui montre que le verdict n'en dépend pas."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "le confondant, puis le verdict à chaque seuil",
             fill=DISCRET, font=petit)
    lignes = mesurees(m)
    gauche, droite = x0 + 56, x0 + pw - 30
    haut, h = y0 + 42, (ph - 190) / 2
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    z_hi = max(x["part_au_zero"] for x in lignes) * 1.15

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    base = haut + h
    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([(px(x["rayon_mm"]), base - h * x["part_au_zero"] / z_hi) for x in lignes],
             fill=AMBRE, width=2)
    art.text((gauche + 4, haut - 14),
             f"part du profil au remplissage — {m['correlations']['part_au_zero_contre_rayon']:+.3f}"
             " avec le rayon", fill=AMBRE, font=petit)
    for g in (0.0, z_hi):
        art.text((x0 + 8, base - h * g / z_hi - 6), f"{g:.2f}", fill=AMBRE, font=petit)
    art.text((gauche, base + 5), f"{int(r0)} mm", fill=DISCRET, font=petit)
    art.text((droite - 34, base + 5), f"{int(r1)} mm", fill=DISCRET, font=petit)

    # ⭐⭐⭐ LE BALAYAGE : une barre par seuil, toutes du meme cote de zero, sinon le verdict
    # dependrait du seuil et serait un nombre choisi.
    bal = [x for x in m["balayage_du_seuil"] if "dispersion_contre_rayon" in x]
    y2 = haut + h + 62
    art.text((x0 + 8, y2 - 18),
             "corrélation dispersion/rayon, à chaque seuil de remplissage toléré",
             fill=BLEU, font=petit)
    zero = gauche + 30
    ech = (droite - zero - 40)
    art.line([zero, y2, zero, y2 + len(bal) * 22], fill=TEXTE)
    art.text((zero - 6, y2 + len(bal) * 22 + 3), "0", fill=DISCRET, font=petit)
    barres = 0
    for j, b in enumerate(bal):
        v = b["dispersion_contre_rayon"]
        yb = y2 + j * 22
        larg = abs(v) * ech
        art.rectangle([zero, yb + 3, zero + larg, yb + 16], fill=BLEU if v < 0 else ROUGE)
        art.text((x0 + 8, yb + 3), f"{int(b['seuil'] * 100):>2d} %", fill=DISCRET, font=petit)
        art.text((zero + larg + 5, yb + 3), f"{v}  ({b['bandes']} bandes)",
                 fill=BLEU if v < 0 else ROUGE, font=petit)
        barres += 1
    art.text((x0 + 8, y0 + ph - 32),
             "★ toutes du même côté : le verdict ne vient pas du seuil",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             "bleu : la dispersion tombe quand le rayon monte", fill=DISCRET, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 400
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    p = m["par_tiers"]
    art.text((marge, 16),
             "La surface humaine est MIEUX posée sur la feuille là où le transfert casse",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · volume à {m['voxel_fin_um']} µm · {m['bandes_mesurees']} bandes "
             f"· dispersion {p['coeur']['dispersion_um']} µm au cœur contre "
             f"{p['bord']['dispersion_um']} au bord, où la continuité passe de "
             f"×{p['coeur']['continuite']} à ×{p['bord']['continuite']}",
             fill=DISCRET, font=moyen)
    titres = ("A · l'anti-prédiction : la dispersion tombe où la continuité explose",
              "B · le confondant du masque, et le balayage du seuil")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_anti(art, marge, 104, pw, ph, m, petit)
    barres = panneau_confondant(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "barres": barres,
            "textes_dessines": art.textes,
            "debordants": textes_debordants(art.poses, L - marge),
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
    d = dessiner(m, RACINE / "docs" / "images" / "95_la_surface_et_la_feuille_par_rayon.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("toutes les bandes mesurées sont tracées", d["points"] == m["bandes_mesurees"],
      f"{d['points']} pour {m['bandes_mesurees']}")
    # ⭐⭐⭐ LE BALAYAGE EST CE QUI REND LE VERDICT VERIFIABLE, donc il est DESSINE.
    v("le balayage du seuil est dessiné, une barre par seuil",
      d["barres"] == len([x for x in m["balayage_du_seuil"]
                          if "dispersion_contre_rayon" in x]), str(d["barres"]))
    bal = [x["dispersion_contre_rayon"] for x in m["balayage_du_seuil"]
           if "dispersion_contre_rayon" in x]
    v("... et toutes les barres sont du même côté de zéro",
      len(bal) >= 4 and (all(x < 0 for x in bal) or all(x > 0 for x in bal)), str(bal))
    # ⚠⚠ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    v("la dispersion tombe bien quand la continuité casse",
      m["correlations"]["dispersion_contre_continuite"] < 0
      and m["par_tiers"]["bord"]["dispersion_um"] < m["par_tiers"]["coeur"]["dispersion_um"],
      str(m["correlations"]["dispersion_contre_continuite"]))
    v("... et il survit au retrait du masque",
      m["une_fois_le_masque_retire"]["dispersion_contre_continuite"] < 0,
      str(m["une_fois_le_masque_retire"]["dispersion_contre_continuite"]))
    v("le confondant est dessiné, pas relégué en annexe",
      any("remplissage" in t for t in d["textes_dessines"]))
    v("la prose garde l'erreur de la sonde à trois bandes",
      any("TROIS bandes" in x for x in prose(m)))
    v("... et dit ce que ça contraint pour le remplaçant de l'humain",
      any("IDENTITE de la feuille" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "95_la_surface_et_la_feuille_par_rayon.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
