#!/usr/bin/env python3
"""Poser deux fois converge vers le plan moyen de la mâchoire, pas vers la feuille.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le verdict en une courbe : sous
zéro le second temps redresse, au-dessus il dégrade, et les deux matières qui portent les DEUX
causes sont les seules au-dessus. En haut à droite, la case décisive — l'erreur à la vraie normale
sur la matière du rouleau, au premier puis au second temps, avec l'angle que `148` mesure en repère.
En bas à gauche, le partage par cause, qui est l'énoncé du fichier. En bas à droite, le prix : des
poses perdues et deux fois les lectures, pour une normale plus fausse.

  uv run python src/figures/figure_la_pose_en_deux_temps.py \\
      --json docs/mesures/la_pose_en_deux_temps.json \\
      --sortie docs/images/152_la_pose_en_deux_temps.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
COURBES = ((150, 152, 156), (120, 124, 130), (196, 160, 60), (176, 120, 60), (176, 60, 42))


def lire(chemin: Path) -> dict:
    """Le JSON de `la_pose_en_deux_temps.py`.

    ⚠⚠ Refuse une mesure dont le verdict décisif est indécidable : les quatre panneaux en
    dépendent, et une figure dessinée sur un verdict absent ressemble exactement à une figure
    dessinée sur un verdict présent.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    if not j.get("a_langle_du_cap", {}).get("decidable"):
        raise ValueError(f"{chemin} : l'angle que `148` mesure est absent, la case décisive aussi")
    if len(j.get("par_cause", [])) < 2:
        raise ValueError(f"{chemin} : le partage par cause demande ses deux groupes")
    if not d.get("redresse", {}).get("decidable"):
        raise ValueError(f"{chemin} : aucune pose mesurée")
    return d


def _court(nom: str) -> str:
    return nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1340, 900
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    red, j = d["redresse"], d["juger"]
    dec = j["a_langle_du_cap"]
    causes = {c["cause"]: c for c in j["par_cause"]}

    ecrire(28, 20, "Poser deux fois converge vers le plan moyen, pas vers la feuille", gros, ENCRE)
    ecrire(28, 46, f"{red['poses_par_case']} poses par case, départs recalés sur une feuille, "
                   f"largeur de référence · écart APPARIÉ sur le même départ, jamais une "
                   f"différence de médianes", petit, GRIS)

    # ---- panneau 1 : l'ecart apparie par inclinaison, une courbe par matiere
    x0, y0, pw, ph = 60, 122, 600, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "écart apparié du second temps, en degrés — sous zéro il redresse",
           moyen, ENCRE)
    incs = red["inclinaisons_deg"]
    n = max(len(incs) - 1, 1)
    # ⚠ L'ECHELLE VIENT DE CE QUI EST DESSINE, jamais d'une borne posee : une matiere qui
    # dégraderait dix fois plus sortirait du cadre sans que rien ne le dise.
    vals = sorted((abs(x["ecart_apparie_deg"]) for m in red["par_matiere"]
                   for x in m["par_inclinaison"] if x["ecart_apparie_deg"] is not None))
    # ⚠⚠ UNE SEULE VALEUR EXTREME APLATIT TOUT LE RESTE SUR LA LIGNE DE ZERO, et le panneau
    # existe justement pour montrer de quel COTE de zero chaque matiere tombe. L'echelle se prend
    # donc sur l'avant-derniere valeur, et tout point qui sort est dessine SUR le bord avec sa
    # valeur ECRITE a cote — borner en cachant serait pire que ne rien montrer.
    hi = max(vals[-2] if len(vals) > 1 else vals[-1], 1e-6)

    def px1(i):
        return x0 + 62 + i * (pw - 196) / n

    def py1(v):
        return y0 + ph / 2 - 10 - (v / hi) * (ph / 2 - 52)

    for v in (-hi, 0.0, hi):
        art.line([x0 + 54, py1(v), x0 + pw - 128, py1(v)],
                 fill=ENCRE if v == 0.0 else TRAIT, width=1)
        ecrire(x0 + 8, int(py1(v)) - 7, f"{v:+.2f}", petit, GRIS)
    art.rectangle([x0 + pw - 126, y0 + 6, x0 + pw - 6, y0 + 12 + 17 * len(red["par_matiere"])],
                  fill=FOND)
    for k, m in enumerate(red["par_matiere"]):
        coul = COURBES[k % len(COURBES)]
        brut = [(i, x["ecart_apparie_deg"]) for i, x in enumerate(m["par_inclinaison"])
                if x["ecart_apparie_deg"] is not None]
        haut_, bas_ = py1(hi), py1(-hi)
        xy = [(px1(i), min(max(py1(val), haut_), bas_)) for i, val in brut]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for (a_, b_), (_i, val) in zip(xy, brut):
            art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
            points.append((a_, b_))
            if abs(val) > hi:
                ecrire(int(a_) - 46, int(b_) - 16, f"{val:+.2f}° ↓", petit, coul)
        ecrire(x0 + pw - 122, y0 + 8 + k * 17, _court(m["nom"]), petit, coul)
    for i, val in enumerate(incs):
        ecrire(int(px1(i)) - 10, y0 + ph - 42, f"{val:.0f}°", petit, ENCRE)
    bas, haut = float(incs[0]), float(incs[-1])
    rx = px1(0) + ((dec["inclinaison_du_cap_deg"] - bas) / max(haut - bas, 1e-9)) * \
        (px1(n) - px1(0))
    art.line([rx, y0 + 14, rx, y0 + ph - 48], fill=ALERTE, width=2)
    ecrire(x0 + 10, y0 + ph - 24, f"repère ambre : {dec['inclinaison_du_cap_deg']}°, "
                                  f"l'angle que `148` mesure sur la matière du rouleau",
           petit, ALERTE)

    # ---- panneau 2 : la case decisive, erreur au premier puis au second temps
    x0, y0, pw, ph = 700, 122, 580, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, f"écart à la vraie normale sur {_court(dec['matiere'])}, en degrés",
           moyen, ENCRE)
    mat = next(m for m in red["par_matiere"] if m["amplitude_um"] == 100.0)
    e1 = [x["erreur_un_temps_deg"] for x in mat["par_inclinaison"]]
    e2 = [x["erreur_deux_temps_deg"] for x in mat["par_inclinaison"]]
    tous = [v for v in e1 + e2 if v is not None]
    emax = max(tous) if tous else 1.0

    def px2(i):
        return x0 + 62 + i * (pw - 180) / n

    def py2(v):
        return y0 + ph - 54 - (v / max(emax, 1e-9)) * (ph - 100)

    for k in range(3):
        vv = emax * k / 2
        art.line([x0 + 54, py2(vv), x0 + pw - 112, py2(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 8, int(py2(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    art.rectangle([x0 + pw - 110, y0 + 6, x0 + pw - 6, y0 + 46], fill=FOND)
    for nom, serie, coul in (("un temps", e1, BON), ("deux temps", e2, ALERTE)):
        xy = [(px2(i), py2(v)) for i, v in enumerate(serie) if v is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
            points.append((a_, b_))
        ecrire(x0 + pw - 106, y0 + 8 + (0 if coul is BON else 18), nom, petit, coul)
    for i, val in enumerate(incs):
        ecrire(int(px2(i)) - 10, y0 + ph - 42, f"{val:.0f}°", petit, ENCRE)
    rx = px2(0) + ((dec["inclinaison_du_cap_deg"] - bas) / max(haut - bas, 1e-9)) * \
        (px2(n) - px2(0))
    art.line([rx, y0 + 14, rx, y0 + ph - 48], fill=ALERTE, width=2)
    ecrire(x0 + 10, y0 + ph - 24, "l'ambre passe AU-DESSUS du vert : deux temps est plus faux "
                                  "qu'un", petit, GRIS)

    # ---- panneau 3 : le partage par cause
    x0, y0, pw, ph = 60, 446, 600, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le partage par CAUSE — écart apparié médian, inclinaisons non nulles",
           moyen, ENCRE)
    mx = max(abs(c["ecart_apparie_median_deg"]) for c in j["par_cause"]) or 1e-6
    zero = x0 + pw / 2
    # ⚠ L'axe ne traverse QUE la bande des barres : trace de haut en bas il barrait une legende,
    # et `textes_qui_se_recouvrent` ne l'aurait jamais vu — il compare TEXTE a TEXTE.
    for k, c in enumerate(j["par_cause"]):
        yy = y0 + 62 + k * 84
        art.line([zero, yy - 6, zero, yy + 32], fill=ENCRE, width=1)
        w = (c["ecart_apparie_median_deg"] / mx) * (pw / 2 - 92)
        coul = BON if c["ecart_apparie_median_deg"] < 0 else ALERTE
        art.rectangle([min(zero, zero + w), yy, max(zero, zero + w), yy + 26], fill=coul)
        points.append((zero + w, yy + 13))
        ecrire(x0 + 14, yy - 22, c["cause"], petit, ENCRE)
        ecrire(x0 + 14, yy + 32, f"{c['ecart_apparie_median_deg']:+.3f}°  ·  "
                                 f"{c['cases_qui_redressent']} redressent, "
                                 f"{c['cases_qui_degradent']} dégradent sur {c['cases']}"
                                 f"{'  ·  unanime' if c['unanime'] else ''}", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 26, "à gauche du trait la pose se redresse, à droite elle se fausse",
           petit, GRIS)

    # ---- panneau 4 : le prix
    x0, y0, pw, ph = 700, 446, 580, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que le second temps COÛTE, à l'angle du cap", moyen, ENCRE)
    lignes = [
        ("poses réussies", f"{dec['part_un_temps_pour_mille']} ‰",
         f"{dec['part_deux_temps_pour_mille']} ‰",
         f"{dec['perdues_au_second_temps']} perdues"),
        ("lectures par pose", f"{dec['lectures_un_temps']}", f"{dec['lectures_deux_temps']}",
         "exactement deux fois"),
        ("écart à la normale", f"{dec['erreur_un_temps_deg']}°", f"{dec['erreur_deux_temps_deg']}°",
         f"apparié {dec['ecart_apparie_deg']:+}°"),
        ("troisième temps", "—", f"{dec['le_troisieme_temps_ajoute_deg']:+}°",
         "le point fixe est atteint"),
    ]
    ecrire(x0 + 16, y0 + 16, f"{'':<20}{'un temps':>12}{'deux temps':>14}", petit, GRIS)
    for k, (nom, a_, b_, note) in enumerate(lignes):
        yy = y0 + 46 + k * 46
        ecrire(x0 + 16, yy, f"{nom:<20}{a_:>12}{b_:>14}", petit, ENCRE)
        ecrire(x0 + 16, yy + 16, note, petit, GRIS)
    ecrire(x0 + 16, y0 + ph - 26,
           f"{dec['redressees']} redressées contre {dec['degradees']} dégradées "
           f"sur {dec['appariees']} appariées", petit, ALERTE)

    # ---- la bande de conclusion, sur son propre cadre RESERVE
    by = 724
    art.rectangle([0, by, L, H], fill=BANDE)
    cadres.append((0, by, L, H))
    ecrire(28, by + 18, "La troisième source est réfutée, et pour le prix d'une pose seule",
           moyen, ENCRE)
    verdict = ("il ne redresse PAS" if not dec["il_redresse"] else "il redresse")
    ecrire(28, by + 46,
           f"À {dec['inclinaison_du_cap_deg']}° sur {_court(dec['matiere'])}, le second temps "
           f"{verdict} : écart apparié {dec['ecart_apparie_deg']:+}°, "
           f"{dec['redressees']} redressées contre {dec['degradees']} dégradées, "
           f"{dec['perdues_au_second_temps']} poses perdues et {dec['lectures_deux_temps']} "
           f"lectures au lieu de {dec['lectures_un_temps']}.", petit, ENCRE)
    ecrire(28, by + 68,
           f"Le troisième temps n'ajoute que {dec['le_troisieme_temps_ajoute_deg']:+}° : la pose "
           f"atteint son point fixe dès le second. Ce point fixe est le PLAN MOYEN de la mâchoire, "
           f"et sur une matière qui porte les deux causes il n'est pas la feuille.", petit, ENCRE)
    ecrire(28, by + 90,
           f"Partage : {causes['une cause au plus']['ecart_apparie_median_deg']:+}° quand une "
           f"cause au plus est présente ({causes['une cause au plus']['cases_qui_degradent']} case "
           f"dégrade sur {causes['une cause au plus']['cases']}), "
           f"{causes['écrasée ET froissée']['ecart_apparie_median_deg']:+}° quand les deux le "
           f"sont ({causes['écrasée ET froissée']['cases_qui_degradent']} sur "
           f"{causes['écrasée ET froissée']['cases']}).", petit, ENCRE)
    ecrire(28, by + 112,
           "Poser deux fois ne rend donc pas une direction plus droite : cela rend deux fois la "
           "direction que la mâchoire aurait choisie toute seule.", petit, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1340, 900), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({g for _x, _y, txt, _f in poses for g in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    # ---- ⭐⭐ LE RE-RENDU EST BIT-IDENTIQUE : une figure qui bouge d'un run a l'autre ne peut
    # pas etre comparee a elle-meme, et `fraicheur_des_figures` la declarerait perimee sans raison.
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ---- ⚠⚠ LA SONDE QUI MORD : elle deplace un champ que la BANDE LIT VRAIMENT. Une sonde qui
    # toucherait un champ que plus rien n'affiche ne prouverait rien du tout.
    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["a_langle_du_cap"]["ecart_apparie_deg"] = -9.999
    faux["juger"]["a_langle_du_cap"]["il_redresse"] = True
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer le verdict change ce que la bande DIT",
      any("-9.999" in t for _x, _y, t, _f in p2)
      and not any("-9.999" in t for _x, _y, t, _f in poses),
      "la bande lit l'écart apparié, donc elle le suit")
    faux2 = copy.deepcopy(d)
    faux2["juger"]["par_cause"][1]["cases_qui_degradent"] = 7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et changer le partage change ce que la bande DIT",
      any("7777" in t for _x, _y, t, _f in p3))

    # ---- ⚠ le lecteur REFUSE une mesure sans son verdict decisif
    sans = copy.deepcopy(d)
    sans["juger"]["a_langle_du_cap"] = {"decidable": False, "raison": "absent"}
    tmp = sortie.parent / "_sans_verdict.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans la case décisive est REFUSÉE, jamais dessinée à moitié", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures" / "la_pose_en_deux_temps.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "152_la_pose_en_deux_temps.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
