#!/usr/bin/env python3
"""Le premier critere dont le seuil vient de la MATIERE, et il est faible la ou il compte.

⭐⭐⭐ CETTE FIGURE PORTE UN SEUIL QUE NI UN MAILLAGE NI UN REGLAGE N'ONT FIXE. `97` a mesure que
deux traces humains independants divergent de plus d'une demi-feuille, donc qu'aucun signal
calibre contre un maillage ne peut l'etre. Le panneau A montre la part de transferts que la
MATIERE confirme, contre la barre d'un modele NUL fabrique.

⚠⚠ ET LE PANNEAU B PORTE CE QUI EMPECHE DE CRIER VICTOIRE : l'accord tombe a 0,353 au bord pour
une barre de 0,331, et la matiere n'y repond que 54 % du temps. La ou le transfert casse, elle est
presque muette.

Usage :
    uv run python src/figures/figure_combien_dinterstices_traverses.py --verifier
    uv run python src/figures/figure_combien_dinterstices_traverses.py \\
        --sortie docs/images/98_combien_dinterstices_traverses.png
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
MESURE = RACINE / "docs" / "mesures" / "combien_dinterstices_traverses.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def lues(m: dict) -> list[dict]:
    return [x for x in m["lignes"]
            if x["mesurable"] and x.get("part_un_interstice") is not None
            and x.get("rayon_mm") is not None]


def prose(m: dict) -> list[str]:
    p, c = m["par_tiers"], m["correlations"]
    nul = m["accord_du_bruit_pur"]
    return [
        "★★★ POURQUOI IL FALLAIT SORTIR DES MAILLAGES. `94` et `95` sont ANTI-predictifs, `96` a "
        "le bon signe mais aucun etalon, et `97` a mesure pourquoi : deux traces humains "
        "INDEPENDANTS de la meme matiere divergent de plus d'une DEMI-feuille partout. aucun "
        "signal calibre contre un maillage humain ne peut donc l'etre, parce que le maillage "
        "humain n'a pas de valeur unique.",
        "★★★ LE CRITERE QUE LA MATIERE TRANCHE S'ENONCE EN UNE PHRASE. une feuille est un ruban "
        "BRILLANT et l'espace entre deux feuilles est SOMBRE, donc entre une cellule et le point "
        "situe un pas de feuille plus loin le profil doit valoir brillant-sombre-brillant : "
        "exactement UN interstice. zero voudrait dire qu'on est revenu sur la meme feuille, deux "
        "qu'on en a saute une. aucun maillage, aucun oracle, aucune supervision.",
        f"⚠⚠⚠ LA QUESTION DE L'AUTEUR — « il faut etre adaptatif par rapport au rouleau teste ? » "
        f"— ET POURQUOI LA REPONSE N'EST PAS D'ADAPTER LE SEUIL. la mesure la rend plus forte : "
        f"dans UNE SEULE bande du bord, l'etendue du profil varie d'un facteur 146, et de 2,4 au "
        f"milieu. un seuil absolu est donc sans espoir et une constante par ROULEAU serait deja "
        f"un parametre ajuste. mais la bonne reponse est de choisir une quantite qui n'en a pas "
        f"besoin : une CORRELATION NORMALISEE est invariante en amplitude ET en decalage, donc "
        "il n'y a rien a adapter.",
        f"★★★ ET LE SEUIL VIENT D'UN MODELE NUL FABRIQUE, PAS DES DONNEES. un accord qu'un bruit "
        f"blanc atteint deja ne dit rien : le p99 du nul est la barre, et il vaut "
        f"{m['barre_du_nul']} — calculable sans regarder le rouleau. et le nul est INDEPENDANT "
        f"de sigma (medianes "
        + ", ".join(str(v["median"]) for v in nul.values()) +
        " pour sigma = 2, 10, 40), ce qui est le controle de l'invariance d'echelle : si le nul "
        "dependait du bruit, le filtre aurait un parametre cache.",
        f"★★★ PANNEAU A — LE SIGNE EST CORRECT. la part de transferts que la matiere confirme "
        f"vaut {p['coeur']['part_un_interstice']} au coeur, "
        f"{p['milieu']['part_un_interstice']} au milieu et {p['bord']['part_un_interstice']} au "
        f"bord, et elle BAISSE avec la rupture de continuite "
        f"({c['un_interstice_contre_continuite']:+.3f}). c'est le second signal apres `96` a "
        "avoir le bon signe, et le PREMIER dont le seuil soit materiel.",
        f"⚠⚠ PANNEAU B — ET C'EST CE QUI EMPECHE DE CRIER VICTOIRE. au bord l'accord median vaut "
        f"{p['bord']['accord_median']} pour une barre de {m['barre_du_nul']}, et la matiere ne "
        f"repond que {round(100 * p['bord']['part_lue'])} % du temps contre "
        f"{round(100 * p['coeur']['part_lue'])} % au coeur. la ou le transfert casse, elle est "
        "presque MUETTE — ce qui est coherent avec `94` : au bord le maillage humain a ENJAMBE ce "
        "qu'il ne pouvait pas suivre, donc il n'y a pas toujours de matiere a interroger.",
        f"★★ UN SECOND VERDICT QUE LA MEME LECTURE DONNE GRATUITEMENT. le gabarit existe en deux "
        f"polarites, et la cellule part SUR une feuille "
        f"{round(100 * p['coeur']['part_partant_sur_la_feuille'])} % du temps au coeur — soit "
        f"une fois sur deux. ⚠⚠⚠ ce nombre a DEUX lectures opposees qu'il fallait separer : le "
        f"maillage est-il vraiment dans un interstice une fois sur deux, ou les deux gabarits "
        f"sont-ils a egalite et le choix un TIRAGE ? seule la MARGE les distingue — elle vaut "
        f"{p['coeur']['marge_de_polarite_mediane']}, comparable a l'accord lui-meme, et "
        f"{round(100 * p['coeur']['part_polarite_tranchee'])} % des profils lus l'ont franche. "
        "l'instrument tranche donc, et ce qu'il tranche est que LA MOITIE des cellules du "
        "maillage humain partent d'un interstice.",
        "★★★ NON — ET LE COMPTEUR DE MINIMA EST REFUTE, GARDE, PARCE QUE SON ECHEC SE GENERALISE. a la "
        "proeminence qui rejette le bruit pur (×6) un interstice reel n'est vu que 6 % du temps, "
        "et a ×3 le bruit passe a 98,8 %. lisser fait monter la detection a 0,95 sans rien "
        "changer aux faux positifs, et la raison est structurelle : une proeminence exprimee en "
        "unites du bruit PROPRE au profil est invariante d'echelle, donc lisser abaisse le bruit "
        "ET le seuil ensemble. la discrimination ne peut pas venir de la PROFONDEUR, elle vient "
        "de la FORME.",
        "⚠⚠⚠ ET TROIS DEFAUTS PAYES ICI, TOUS GARDES. les gabarits etaient de signe INVERSE, ce "
        "qui appariait 40 % des profils reels a un gabarit dont la lecture correcte est « la "
        "cellule est dans un interstice » — deux etats sous une seule etiquette, trouve en lisant "
        "les comptes. mon test de platitude ne pouvait pas voir le cas degenere, un profil "
        "EXACTEMENT constant ayant une etendue nulle ET un bruit nul, donc `0 < 0` faux. et "
        "l'estimateur de bruit prenait une difference PREMIERE, qui lit aussi la pente du signal "
        "qu'on cherche a compter.",
    ]


def panneau_signe(art, x0, y0, pw, ph, m, petit) -> int:
    """La part à un interstice et la continuité contre le rayon."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "ce que la matière confirme, contre le rayon", fill=DISCRET, font=petit)
    lignes = lues(m)
    gauche, droite = x0 + 52, x0 + pw - 52
    base, sommet = y0 + ph - 58, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    c_hi = max(x["continuite"] for x in lignes if x["continuite"]) * 1.12

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v, hi):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([(px(x["rayon_mm"]), py(x["part_un_interstice"], 1.0)) for x in lignes],
             fill=BLEU, width=2)
    art.line([(px(x["rayon_mm"]), py(x["continuite"], c_hi)) for x in lignes
              if x["continuite"]], fill=ROUGE, width=2)
    points = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["part_un_interstice"], 1.0)
        art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLEU)
        points += 1
    # ⭐ La moitie est tracee : c'est le repere qui dit ce que « confirme » vaut face a « ne
    # confirme pas », et sans lui 0,52 serait un nombre nu.
    art.line([gauche, py(0.5, 1.0), droite, py(0.5, 1.0)], fill=GRIS)
    art.text((gauche + 4, py(0.5, 1.0) - 13), "une fois sur deux", fill=DISCRET, font=petit)
    for g in (0.0, 0.5, 1.0):
        art.text((x0 + 6, py(g, 1.0) - 6), f"{g:>4.1f}", fill=BLEU, font=petit)
    for g in (0.0, c_hi / 2, c_hi):
        art.text((droite + 6, py(g, c_hi) - 6), f"×{g:.0f}", fill=ROUGE, font=petit)
    art.text((gauche + 4, sommet - 16), "part à UN interstice", fill=BLEU, font=petit)
    art.text((droite - 108, sommet - 16), "continuité, ×référence", fill=ROUGE, font=petit)
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 34),
             f"★ corrélation : {m['correlations']['un_interstice_contre_continuite']:+.3f} — "
             "elle BAISSE là où la continuité casse",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande — cœur à gauche, bord à droite",
             fill=DISCRET, font=petit)
    return points


def panneau_barre(art, x0, y0, pw, ph, m, petit) -> int:
    """L'accord contre la barre du nul, et la part où la matière répond."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "l'accord contre la barre du modèle NUL, et la part lue", fill=DISCRET, font=petit)
    p = m["par_tiers"]
    tiers = [k for k in ("coeur", "milieu", "bord") if k in p]
    mots = {"coeur": "cœur", "milieu": "milieu", "bord": "bord"}
    gauche, droite = x0 + 92, x0 + pw - 86
    haut = y0 + 56
    h = (ph - 210) / max(1, len(tiers))
    hi = max(max(p[k]["accord_median"] for k in tiers), m["barre_du_nul"]) * 1.35
    barres = 0
    for j, k in enumerate(tiers):
        yb = haut + j * h
        art.text((x0 + 8, yb + 10), mots[k], fill=TEXTE, font=petit)
        for i, (cle, coul, nom) in enumerate((
                ("accord_median", BLEU, "accord médian"),
                ("part_lue", VERT, "part où la matière répond"))):
            val = p[k][cle]
            y = yb + 4 + i * 16
            larg = (droite - gauche) * (val / hi if cle == "accord_median" else val)
            art.rectangle([gauche, y, gauche + larg, y + 13], fill=coul)
            art.text((gauche + larg + 5, y), f"{val:.3f}", fill=coul, font=petit)
            if j == 0:
                art.text((gauche, haut - 38 + i * 13), nom, fill=coul, font=petit)
            barres += 1
    # ⭐⭐⭐ LA BARRE DU NUL EST TRACEE : sans elle, 0,353 est un nombre nu ; avec elle, on voit
    # que le bord frole ce qu'un bruit blanc atteint deja.
    xb = gauche + (droite - gauche) * m["barre_du_nul"] / hi
    art.line([xb, haut - 8, xb, haut + len(tiers) * h - 4], fill=ROUGE, width=2)
    art.text((xb - 40, haut + len(tiers) * h + 2),
             f"barre du nul {m['barre_du_nul']}", fill=ROUGE, font=petit)
    y = haut + len(tiers) * h + 24
    art.text((x0 + 8, y),
             "⚠ au bord l'accord FRÔLE la barre : là où le transfert",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 14),
             "   casse, la matière est presque muette.", fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 34),
             f"★ et la marge de polarité vaut {p[tiers[0]]['marge_de_polarite_mediane']}, donc",
             fill=VERT, font=petit)
    art.text((x0 + 8, y + 48),
             f"   {round(100 * p[tiers[0]]['part_polarite_tranchee'])} % des profils tranchent : "
             "la moitié des cellules", fill=VERT, font=petit)
    art.text((x0 + 8, y + 62),
             "   humaines partent d'un interstice, pas d'un tirage.", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             "la part lue est une fraction, l'accord une corrélation", fill=DISCRET, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 420
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
             "Le premier critère dont le seuil vient de la MATIÈRE, et il est faible là où il "
             "compte", fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · volume à {m['voxel_fin_um']} µm · {m['bandes_lisibles']} bandes "
             f"· part à un interstice {p['coeur']['part_un_interstice']} au cœur contre "
             f"{p['bord']['part_un_interstice']} au bord · barre du nul {m['barre_du_nul']}",
             fill=DISCRET, font=moyen)
    titres = ("A · le signe est correct : elle baisse où ça casse",
              "B · mais l'accord frôle la barre du nul au bord")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_signe(art, marge, 104, pw, ph, m, petit)
    barres = panneau_barre(art, marge + pw + ecart, 104, pw, ph, m, petit)
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
    d = dessiner(m, RACINE / "docs" / "images" / "98_combien_dinterstices_traverses.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("toutes les bandes lues sont tracées", d["points"] == len(lues(m)), str(d["points"]))
    v("les deux quantités sont dessinées pour chaque tiers", d["barres"] == 6, str(d["barres"]))
    # ⭐⭐⭐ LA BARRE DU NUL EST DESSINEE, sinon l'accord serait un nombre nu.
    v("la barre du nul est tracée", any("barre du nul" in t for t in d["textes_dessines"]))
    # ⚠⚠ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    v("le signe est correct : la part à un interstice baisse avec la rupture",
      m["correlations"]["un_interstice_contre_continuite"] < 0,
      str(m["correlations"]["un_interstice_contre_continuite"]))
    v("... et l'accord du bord frôle bien la barre du nul",
      m["par_tiers"]["bord"]["accord_median"] < 1.15 * m["barre_du_nul"],
      f"{m['par_tiers']['bord']['accord_median']} pour {m['barre_du_nul']}")
    v("... alors que celui du cœur la dépasse franchement",
      m["par_tiers"]["coeur"]["accord_median"] > 1.3 * m["barre_du_nul"],
      f"{m['par_tiers']['coeur']['accord_median']} pour {m['barre_du_nul']}")
    # ⚠⚠⚠ LA MARGE EST CE QUI DISTINGUE UN VERDICT D'UN TIRAGE, donc elle est assertee.
    v("la polarité est TRANCHÉE et non tirée au sort",
      all(m["par_tiers"][k]["part_polarite_tranchee"] > 0.6 for k in m["par_tiers"]),
      str([m["par_tiers"][k]["part_polarite_tranchee"] for k in m["par_tiers"]]))
    v("le nul est indépendant de l'écart-type",
      max(x["median"] for x in m["accord_du_bruit_pur"].values())
      - min(x["median"] for x in m["accord_du_bruit_pur"].values()) < 0.02)
    v("la prose garde la question de l'auteur sur l'adaptativité",
      any("adaptatif par rapport au rouleau" in x for x in prose(m)))
    v("... et le compteur de minima réfuté", any("REFUTE" in x for x in prose(m)))
    v("... et les trois défauts payés", any("signe INVERSE" in x for x in prose(m)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "98_combien_dinterstices_traverses.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
