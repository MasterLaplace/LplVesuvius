"""Deux prédictions : ce que leur désaccord trahit d'un saut raté, et ce qu'elles ratent ensemble.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, CE QUE CONTIENNENT L'ACCORD ET LE DÉSACCORD de `m7` et `ps256` :
là où elles s'accordent, presque tout est juste, mais une part fixe est ratée par les deux ; là où elles divergent,
aucune des deux n'a raison plus souvent que l'autre. À droite, LES TROIS DÉTECTEURS sur un même plan, la part des ratés
signalés contre la part des justes signalés à tort, et ce que devient la part juste une fois les signalés écartés.

  uv run python src/figures/figure_deux_predictions_trahissent_elles_le_saut_rate.py \\
      --sortie docs/images/251_deux_predictions_trahissent_elles_le_saut_rate.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"
LES_OBJETS = (("la bande w028-037", MESURES / "deux_predictions_trahissent_elles_le_saut_rate.json"),
              ("le segment 20230702185753", MESURES / "deux_predictions_sur_le_segment_5753.json"))

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
OCRE = (196, 160, 90)
L_, H_ = 1360, 950
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))
LES_PARTS = (("les deux justes", "les_deux", BON), ("seule m7 juste", "seul_le_premier", CONTRE),
             ("seule ps256 juste", "seul_le_second", OCRE), ("aucune", "aucun", ALERTE))
LES_DETECTEURS = (("le retour", "le_retour", CONTRE), ("le désaccord", "le_desaccord", OCRE),
                  ("les deux réunis", "la_reunion", ALERTE))


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = {}
    for nom, chemin in LES_OBJETS:
        m = json.loads(chemin.read_text())
        if not m.get("decidable"):
            raise SystemExit(f"mesure indécidable : {chemin.name}")
        d[nom] = m
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : le désaccord signale-t-il plus de ratés de m7 que le retour, partout ?"""
    plus = all(d[o][c]["les_detecteurs"]["m7"]["le_desaccord"]["la_part_des_rates_signales"]
               > d[o][c]["les_detecteurs"]["m7"]["le_retour"]["la_part_des_rates_signales"] for o in d for _, c in LES_COTES)
    aucun = [d[o][c]["la_ou_elles_saccordent"]["aucun"] for o in d for _, c in LES_COTES]
    if plus:
        return (f"LE DÉSACCORD DE DEUX PRÉDICTIONS TRAHIT PLUS DE RATÉS QUE LE RETOUR, MAIS ELLES EN RATENT "
                f"{_fr(min(aucun), 4)} À {_fr(max(aucun), 4)} ENSEMBLE")
    return "LE DÉSACCORD DE DEUX PRÉDICTIONS NE TRAHIT PAS PLUS DE RATÉS QUE LE RETOUR"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, "les deux premiers sauts sont ceux de 247, avec m7 et avec ps256 ; en désaccord à un demi-feuillet ou "
                   "plus l'un de l'autre ; juge : la couche que l'objet porte lui-même", petit, GRIS)

    # ── PANNEAU 1 · L'ACCORD ET LE DÉSACCORD ────────────────────────────────────────────────
    panneau(50, 84, 660, 800, "CE QUE CONTIENNENT L'ACCORD ET LE DÉSACCORD")
    bx0, bx1 = 250, 640
    y = 130
    piles = 0
    for objet in d:
        ecrire(66, y, objet, 0, ENCRE)
        y += 22
        for etat, cle_e in (("accord", "la_ou_elles_saccordent"), ("désaccord", "la_ou_elles_divergent")):
            for nom_c, cote in LES_COTES:
                q = d[objet][cote][cle_e]
                ecrire(80, y + 2, f"{etat}, côté {nom_c} ({q['combien']})", 0, GRIS)
                x = bx0
                for _, cle, coul in LES_PARTS:
                    w = (bx1 - bx0) * q[cle]
                    art.rectangle([x, y, x + w, y + 14], fill=coul)
                    x += w
                points.append((x, y + 14))
                piles += 1
                y += 22
            y += 6
        y += 16
    traces["piles"] = piles
    for k, (nom, _, coul) in enumerate(LES_PARTS):
        xl = 66 + (k % 2) * 290
        yl = y + (k // 2) * 20
        art.rectangle([xl, yl + 3, xl + 14, yl + 11], fill=coul)
        ecrire(xl + 22, yl, nom, 0, ENCRE)
    b = d["la bande w028-037"]
    ecrire(66, y + 52, f"là où elles s'accordent sur la bande, les deux ratent ensemble "
                       f"{_fr(b['du_cote_plus']['la_ou_elles_saccordent']['aucun'], 4)} et "
                       f"{_fr(b['du_cote_moins']['la_ou_elles_saccordent']['aucun'], 4)} des points", 0, ALERTE)

    # ── PANNEAU 2 · LES DÉTECTEURS ──────────────────────────────────────────────────────────
    panneau(680, 84, 1310, 480, "LES TROIS DÉTECTEURS, POUR m7")
    gx0, gx1, gy0, gy1 = 760, 1170, 130, 420
    X1, Y1 = 0.1, 0.5
    for f_ in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        yg = gy1 - (gy1 - gy0) * f_ / Y1
        art.line([gx0, yg, gx1, yg], fill=TRAIT, width=1)
        ecrire(gx0 - 32, yg - 7, _fr(f_, 1), 0, GRIS)
    for f_ in (0.0, 0.05, 0.1):
        xg = gx0 + (gx1 - gx0) * f_ / X1
        art.line([xg, gy0, xg, gy1], fill=TRAIT, width=1)
        ecrire(xg - 12, gy1 + 6, _fr(f_, 2), 0, GRIS)
    ecrire(gx0, gy1 + 24, "la part des justes signalés à tort", 0, GRIS)
    ecrire(gx0, gy0 - 20 + 6, "la part des ratés signalés", 0, GRIS)
    marques = 0
    for k_o, objet in enumerate(d):
        for _, cote in LES_COTES:
            for nom, cle, coul in LES_DETECTEURS:
                c = d[objet][cote]["les_detecteurs"]["m7"][cle]
                x = gx0 + (gx1 - gx0) * min(c["la_part_des_justes_signales_a_tort"], X1) / X1
                yy = gy1 - (gy1 - gy0) * min(c["la_part_des_rates_signales"], Y1) / Y1
                if k_o == 0:
                    art.ellipse([x - 5, yy - 5, x + 5, yy + 5], fill=coul)
                else:
                    art.rectangle([x - 4, yy - 4, x + 4, yy + 4], outline=coul, width=2)
                points.append((x, yy))
                marques += 1
    traces["marques"] = marques
    for k, (nom, _, coul) in enumerate(LES_DETECTEURS):
        art.ellipse([1192, 150 + k * 22, 1202, 160 + k * 22], fill=coul)
        ecrire(1208, 147 + k * 22, nom, 0, ENCRE)
    ecrire(1192, 226, "rond : la bande", 0, GRIS)
    ecrire(1192, 244, "carré : le segment", 0, GRIS)

    # ── PANNEAU 3 · LA PART JUSTE ───────────────────────────────────────────────────────────
    panneau(680, 500, 1310, 800, "LA PART JUSTE DE m7, AVANT ET APRÈS AVOIR ÉCARTÉ LES SIGNALÉS")
    cx0, cx1 = 900, 1210
    C0, C1 = 0.9, 0.95
    y = 544
    paires = 0
    for objet in d:
        ecrire(696, y, objet, 0, ENCRE)
        y += 20
        for nom_c, cote in LES_COTES:
            for nom, cle, coul in LES_DETECTEURS:
                c = d[objet][cote]["les_detecteurs"]["m7"][cle]
                a_, b_ = c["la_part_juste_a_laller"], c["la_part_juste_parmi_les_gardes"]
                xa, xb = (cx0 + (cx1 - cx0) * (min(max(x, C0), C1) - C0) / (C1 - C0) for x in (a_, b_))
                art.line([xa, y + 5, xb, y + 5], fill=coul, width=2)
                art.ellipse([xb - 3, y + 2, xb + 3, y + 8], fill=coul)
                points.extend([(xa, y + 5), (xb, y + 5)])
                ecrire(710, y - 1, f"côté {nom_c}, {nom}", 0, GRIS)
                ecrire(cx1 + 8, y - 1, f"{_fr(a_)} → {_fr(b_)}", 0, ENCRE)
                paires += 1
                y += 12
            y += 4
        y += 8
    for f_ in (0.9, 0.92, 0.94):
        xg = cx0 + (cx1 - cx0) * (f_ - C0) / (C1 - C0)
        art.line([xg, 560, xg, y - 6], fill=TRAIT, width=1)
        ecrire(xg - 12, y - 4, _fr(f_, 2), 0, GRIS)
    traces["paires"] = paires

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    bp, bm = b["du_cote_plus"]["les_detecteurs"]["m7"], b["du_cote_moins"]["les_detecteurs"]["m7"]
    ecrire(50, 832, "LE VERDICT : une seconde prédiction voit plus de ratés que le retour, mais là où les deux s'accordent, "
                    "une part fixe est ratée par les deux", petit, ENCRE)
    ecrire(50, 856, f"★ sur la bande, le désaccord signale {_fr(bp['le_desaccord']['la_part_des_rates_signales'])} et "
                    f"{_fr(bm['le_desaccord']['la_part_des_rates_signales'])} des ratés de m7, le retour "
                    f"{_fr(bp['le_retour']['la_part_des_rates_signales'])} et "
                    f"{_fr(bm['le_retour']['la_part_des_rates_signales'])} ; réunis, "
                    f"{_fr(bp['la_reunion']['la_part_des_rates_signales'])} et "
                    f"{_fr(bm['la_reunion']['la_part_des_rates_signales'])}.", moyen, ENCRE)
    ecrire(50, 882, f"★ écarter ce que les deux signalent fait passer la part juste de {_fr(bp['la_reunion']['la_part_juste_a_laller'])} "
                    f"à {_fr(bp['la_reunion']['la_part_juste_parmi_les_gardes'])} et de "
                    f"{_fr(bm['la_reunion']['la_part_juste_a_laller'])} à {_fr(bm['la_reunion']['la_part_juste_parmi_les_gardes'])}, "
                    f"en gardant {_fr(bp['la_reunion']['la_part_gardee'])} et {_fr(bm['la_reunion']['la_part_gardee'])} des points.",
           moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : un seul saut ; les points signalés sont écartés, pas réparés ; les deux "
                    "prédictions sont lues sur le même scan.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d = lire()
    tmp = sortie.parent / ".sonde_251.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LE DÉSACCORD DE DEUX PRÉDICTIONS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    # ⚠⚠ LES PILES FONT UN : chaque accord et chaque désaccord est partagé en quatre parts qui se complètent.
    somme = [sum(d[o][c][e][k] for _, k, _ in LES_PARTS) for o in d for _, c in LES_COTES
             for e in ("la_ou_elles_saccordent", "la_ou_elles_divergent")]
    v("★★★★ les quatre parts de chaque pile font un, à l'arrondi près", all(abs(s - 1.0) < 0.002 for s in somme), str(somme))
    v("★★★★ chaque pile est dessinée : deux objets, deux états, deux côtés", traces["piles"] == 8)
    v("★★★★ chaque détecteur a sa marque : deux objets, deux côtés", traces["marques"] == 12)
    v("★★★ chaque détecteur a sa paire avant et après", traces["paires"] == 12)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les deux objets, les deux prédictions et ce qui n'est PAS établi",
      "w028-037" in txt and "20230702185753" in txt and "ps256" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "251_deux_predictions_trahissent_elles_le_saut_rate.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
