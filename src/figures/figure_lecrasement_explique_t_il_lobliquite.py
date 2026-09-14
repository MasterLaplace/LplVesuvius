#!/usr/bin/env python3
"""L'écrasement du rouleau explique-t-il l'obliquité du chemin ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** À gauche, chaque
matière fabriquée est un point : en abscisse le penchant du chemin sur le rayon, en ordonnée le
rapport du chemin à l'étendue radiale. La croix est le rouleau. Une matière qui l'explique doit
tomber **sur** la croix, pas seulement du bon côté. À droite, la cohérence de chaque matière contre
celle du rouleau : c'est elle qui sépare les deux causes — un écrasement en donne trop, un
froissement pas assez, et seule leur composition tombe juste.

  uv run python src/figures/figure_lecrasement_explique_t_il_lobliquite.py \\
      --json docs/mesures/lecrasement_explique_t_il_lobliquite.json \\
      --sortie docs/images/140_lecrasement_et_le_froissement.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ECRASE = (86, 104, 132)
FROISSE = (176, 92, 42)
LES_DEUX = (60, 110, 90)
ROULEAU = (150, 96, 176)
RIEN = (170, 172, 176)


def famille(x: dict):
    """De quelle cause ce lot relève — c'est ce que la couleur dit."""
    if x["ecrasement"] > 0.0 and x["amplitude_um"] > 0.0:
        return LES_DEUX, "les deux"
    if x["ecrasement"] > 0.0:
        return ECRASE, "écrasement seul"
    if x["amplitude_um"] > 0.0:
        return FROISSE, "froissement seul"
    return RIEN, "ni l'un ni l'autre"


def lire(chemin: Path) -> dict:
    """Le JSON de `lecrasement_explique_t_il_lobliquite.py`.

    ⚠⚠ Refuse un JSON où les TROIS familles ne sont pas représentées : l'image est une comparaison,
    et une comparaison à laquelle il manque un terme est une figure qui affirme sans montrer.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    lots = [x for x in d.get("sur_la_spirale", {}).get("lots", []) if "rapport_median" in x]
    familles = {famille(x)[1] for x in lots}
    manquantes = {"écrasement seul", "froissement seul", "les deux"} - familles
    if manquantes:
        raise ValueError(f"{chemin} : famille(s) absente(s) : {sorted(manquantes)}")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1180, 700
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    e = d["lecrasement_que_la_surface_impose"]
    j = d.get("juger", {})
    lots = [x for x in d["sur_la_spirale"]["lots"] if "rapport_median" in x]
    ecrire(28, 20, "L'écrasement donne la cohérence, le froissement donne le reste", gros, ENCRE)
    ecrire(28, 46, f"écrasement dérivé de la surface de `135` : {e['surface_min_mm']} à "
                   f"{e['surface_max_mm']} mm, rapport des axes {e['rapport_des_axes']}, "
                   f"e = {e['ecrasement']} · {len(lots)} matières · "
                   f"{d['sur_la_spirale']['departs']} départs, {d['sur_la_spirale']['pas_max']} pas",
           petit, GRIS)

    # ── Gauche : penchant contre rapport, et la croix du rouleau ──────────────
    x0, y0, pw, ph = 60, 150, 500, 360
    ecrire(x0, y0 - 26, "rapport chemin / étendue, contre penchant du chemin", moyen, ENCRE)
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    p_hi = max([x["penchant_median"] for x in lots] + [d["penchant_du_rouleau_deg"]]) * 1.15
    r_hi = max([x["rapport_median"] for x in lots] + [d["rapport_du_rouleau"]])
    r_hi = 1.0 + (r_hi - 1.0) * 1.18

    def px(v):
        return x0 + 40 + (float(v) / p_hi) * (pw - 58)

    def py(v):
        return y0 + ph - 30 - ((float(v) - 1.0) / max(r_hi - 1.0, 1e-9)) * (ph - 50)

    for k in range(0, int(p_hi) + 1, 5):
        ecrire(int(px(k)) - 6, y0 + ph - 22, f"{k}", petit, GRIS)
    for v_ in [1.0 + 0.05 * k for k in range(0, int((r_hi - 1.0) / 0.05) + 1)]:
        art.line([x0 + 6, py(v_), x0 + pw - 6, py(v_)], fill=TRAIT, width=1)
        ecrire(x0 + 6, int(py(v_)) - 12, f"{v_:.2f}", petit, GRIS)
    # ⚠ La croix du rouleau est dessinee AVANT les points : un point qui tombe dessus doit se voir
    # par-dessus, pas disparaitre dessous.
    cx_, cy_ = px(d["penchant_du_rouleau_deg"]), py(d["rapport_du_rouleau"])
    art.line([cx_ - 11, cy_, cx_ + 11, cy_], fill=ROULEAU, width=2)
    art.line([cx_, cy_ - 11, cx_, cy_ + 11], fill=ROULEAU, width=2)
    ecrire(int(cx_) - 118, int(cy_) - 6, "le rouleau →", petit, ROULEAU)
    for x in lots:
        coul, _ = famille(x)
        a, b = px(x["penchant_median"]), py(x["rapport_median"])
        points.append((a, b))
        art.ellipse([a - 5, b - 5, a + 5, b + 5], fill=coul)
    yl = y0 + 8
    for coul, nom in ((RIEN, "ni l'un ni l'autre"), (ECRASE, "écrasement seul"),
                      (FROISSE, "froissement seul"), (LES_DEUX, "les deux")):
        art.ellipse([x0 + 46, yl + 3, x0 + 56, yl + 13], fill=coul)
        ecrire(x0 + 62, yl, nom, petit, coul)
        yl += 16
    ecrire(x0, y0 + ph + 8, "penchant médian du chemin sur le rayon (degrés)", petit, GRIS)

    # ── Droite : la cohérence, qui sépare les deux causes ────────────────────
    x1 = x0 + pw + 80
    pw2 = L - x1 - 40
    ecrire(x1, y0 - 26, "la cohérence du penchant, matière par matière", moyen, ENCRE)
    art.rectangle([x1, y0, x1 + pw2, y0 + ph], outline=TRAIT, width=1)
    haut = 22
    ordre = sorted(lots, key=lambda z: (z["ecrasement"], z["amplitude_um"]))
    base = y0 + 34

    def cx2(v):
        return x1 + 128 + float(v) * (pw2 - 148)

    art.line([cx2(d["coherence_du_rouleau"]), y0 + 6, cx2(d["coherence_du_rouleau"]),
              y0 + ph - 30], fill=ROULEAU, width=2)
    ecrire(int(cx2(d["coherence_du_rouleau"])) - 96, y0 + 8,
           f"le rouleau {d['coherence_du_rouleau']} →", petit, ROULEAU)
    for i, x in enumerate(ordre):
        coul, _ = famille(x)
        y = base + i * haut
        ecrire(x1 + 10, y + 3, f"e {x['ecrasement']:.3f} · A {x['amplitude_um']:.0f}", petit, ENCRE)
        art.rectangle([cx2(0.0), y + 2, cx2(x["coherence_median"]), y + haut - 8], fill=coul)
        points.append((cx2(x["coherence_median"]), y + 2))
    for v_ in (0.0, 0.25, 0.5, 0.75, 1.0):
        ecrire(int(cx2(v_)) - 8, base + len(ordre) * haut + 6, f"{v_:g}", petit, GRIS)
    ecrire(x1, y0 + ph + 8, "cohérence tangentielle : 1 = le chemin penche toujours du même côté",
           petit, GRIS)

    # ── La bande de conclusion ───────────────────────────────────────────────
    yb = y0 + ph + 30
    art.rectangle([x0, yb, L - 40, H - 20], fill=BANDE, outline=TRAIT, width=1)
    lignes = []
    if j.get("decidable"):
        lignes.append((f"★ La matière la plus proche des TROIS grandeurs est l'écrasement MESURÉ "
                       f"({j['le_plus_proche_ecrasement']}) plus un froissement de "
                       f"{j['le_plus_proche_amplitude_um']:.0f} µm : {j['le_plus_proche_rapport']} · "
                       f"{j['le_plus_proche_penchant']}° · {j['le_plus_proche_coherence']}, à "
                       f"{j['le_plus_proche_distance']:.1%} de la pire des trois.", ENCRE))
        if "les_deux_font_mieux_que_chacune_seule" in j:
            lignes.append((f"★ Les deux causes ensemble font mieux que chacune seule : écrasement "
                           f"seul {j['meilleure_distance_ecrasement_seul']}, froissement seul "
                           f"{j['meilleure_distance_froissement_seul']}, les deux "
                           f"{j['meilleure_distance_les_deux']}.", ENCRE))
        if "coherence_ecrasement_seul" in j:
            lignes.append((f"★ Et c'est la COHÉRENCE qui les sépare : un écrasement seul en donne "
                           f"{j['coherence_ecrasement_seul']}, un froissement seul "
                           f"{j['coherence_froissement_seul']}, le rouleau "
                           f"{j['coherence_du_rouleau']}. Ni l'une ni l'autre ne l'atteint.",
                           ENCRE))
    for i, (texte, coul) in enumerate(lignes):
        ecrire(x0 + 14, yb + 12 + i * 22, texte, petit, coul)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    cadres = [(x0 - 30, y0 - 30, x0 + pw + 10, yb - 2),
              (x1 - 30, y0 - 30, L - 20, yb - 2),
              (x0, yb, L - 40, H)]
    return sortie, poses, cadres, points


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et des sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    def lot(ec, amp, rap, pen, coh):
        return {"ecrasement": ec, "amplitude_um": amp, "rapport_des_axes": 1.0,
                "inclinaison_max_du_froissement_deg": 0.0, "marches": [{}],
                "les_feuilles_se_croisent": False, "part_du_rayon_ou_la_phase_recule": 0.0,
                "et_au_plus": 0.0, "rapport_median": rap, "penchant_median": pen,
                "coherence_median": coh, "penchant_p90_median": pen + 8.0,
                "rapport_predit_median": rap + 0.01,
                "inclinaison_de_la_normale_median": pen}

    lots = [lot(0.0, 0.0, 1.0, 0.12, 1.0), lot(0.2782, 0.0, 1.0646, 20.0, 0.999),
            lot(0.5564, 0.0, 1.1278, 27.3, 0.999), lot(0.0, 42.4, 1.0046, 3.85, 0.393),
            lot(0.0, 100.0, 1.036, 12.46, 0.624), lot(0.2782, 42.4, 1.0713, 20.39, 0.986),
            lot(0.2782, 100.0, 1.1212, 24.48, 0.942), lot(0.5564, 100.0, 1.1479, 28.22, 0.985)]
    faux = {"lecrasement_que_la_surface_impose": {
                "decidable": True, "surface_min_mm": 16.8, "surface_max_mm": 29.75,
                "rapport_des_axes": 1.771, "ecrasement": 0.2782},
            "rapport_du_rouleau": 1.186, "penchant_du_rouleau_deg": 25.48,
            "coherence_du_rouleau": 0.925,
            "sur_la_spirale": {"rayon_mm": 10.0, "longueur_donde_um": 393.6, "pas_max": 40,
                               "departs": 10, "lots": lots},
            "juger": {"decidable": True, "rapport_du_rouleau": 1.186,
                      "penchant_du_rouleau_deg": 25.48, "coherence_du_rouleau": 0.925,
                      "ecrasement_mesure": 0.2782, "rapport_des_axes_mesure": 1.771,
                      "par_lot": [], "le_plus_proche_ecrasement": 0.2782,
                      "le_plus_proche_amplitude_um": 100.0, "le_plus_proche_rapport": 1.1212,
                      "le_plus_proche_penchant": 24.48, "le_plus_proche_coherence": 0.942,
                      "le_plus_proche_distance": 0.0546,
                      "meilleure_distance_ecrasement_seul": 0.08,
                      "meilleure_distance_froissement_seul": 0.5112,
                      "meilleure_distance_les_deux": 0.0546,
                      "les_deux_font_mieux_que_chacune_seule": True,
                      "coherence_ecrasement_seul": 0.999,
                      "coherence_froissement_seul": 0.3925}}

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "c.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", lu["rapport_du_rouleau"], 1.186)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())
        v("les trois familles ont trois couleurs",
          pixels.count(ECRASE) > 200 and pixels.count(FROISSE) > 200
          and pixels.count(LES_DEUX) > 200)
        v("le repère du rouleau est tracé", pixels.count(ROULEAU) > 150)
        v("la bande de conclusion est peinte", pixels.count(BANDE) > 3000)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        gx0, gy0, _, gy1 = cadres[0]
        v("tous les points tiennent dans un cadre",
          [1 for x, y in points if not (gx0 <= x <= cadres[1][2] and gy0 <= y <= gy1)], [])
        v("les trois lignes de conclusion sont écrites",
          sum(1 for _, _, t, _ in poses if t.startswith("★")), 3)
        for nom_, bris in (
                ("porteur d'un message", lambda x: x.update(message="fixture injoignable")),
                ("sans la famille « les deux »",
                 lambda x: x["sur_la_spirale"].update(
                     lots=[z for z in x["sur_la_spirale"]["lots"]
                           if not (z["ecrasement"] > 0 and z["amplitude_um"] > 0)])),
                ("sans froissement seul",
                 lambda x: x["sur_la_spirale"].update(
                     lots=[z for z in x["sur_la_spirale"]["lots"]
                           if not (z["ecrasement"] == 0 and z["amplitude_um"] > 0)]))):
            c = json.loads(json.dumps(faux))
            bris(c)
            j.write_text(json.dumps(c), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON {nom_} est refusé", False)
            except ValueError:
                v(f"sonde : un JSON {nom_} est refusé", True)
        j.write_text(json.dumps(faux), encoding="utf-8")
        dessiner(lire(j), r / "g.png")
        v("deux rendus du même JSON sont identiques au bit",
          (r / "f.png").read_bytes() == (r / "g.png").read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "lecrasement_explique_t_il_lobliquite.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "140_lecrasement_et_le_froissement.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
