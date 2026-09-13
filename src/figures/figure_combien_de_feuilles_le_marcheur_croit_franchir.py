#!/usr/bin/env python3
"""Le marcheur compte juste, mais une feuille n'est pas un rayon.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** Le panneau de GAUCHE
est le contrôle : sur une pile dont la normale est connue, le compte du marcheur rapporté à
l'**épaisseur** traversée reste à un quelle que soit l'obliquité, alors que le même compte rapporté
au **chemin** s'effondre. L'instrument est donc juste. Le panneau de DROITE est le rouleau : chaque
traversée porte deux points — l'espacement que son compte implique le long du **chemin**, et le
long du **rayon** — contre la bande des deux instruments qui l'ont mesuré. Les premiers y tombent,
les seconds sont dessous. C'est la même mesure lue de deux façons, et une seule est une erreur.

  uv run python src/figures/figure_combien_de_feuilles_le_marcheur_croit_franchir.py \\
      --json docs/mesures/combien_de_feuilles_le_marcheur_croit_franchir.json \\
      --sortie docs/images/136_une_feuille_nest_pas_un_rayon.png
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
BANDE = (214, 232, 222)
EPAISSEUR = (60, 110, 90)
CHEMIN = (196, 140, 60)
RAYON = (86, 104, 132)
ALERTE = (176, 62, 62)


def lire(chemin: Path) -> dict:
    """Le JSON de `combien_de_feuilles_le_marcheur_croit_franchir.py`.

    ⚠⚠ Refuse un JSON sans la fixture ou sans traversée : le panneau de gauche est le contrôle qui
    autorise à lire celui de droite, et une figure qui le dessinerait vide ferait passer une
    mesure non contrôlée pour une mesure contrôlée.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("traversees"):
        raise ValueError(f"{chemin} ne porte aucune traversée")
    if not d.get("la_fixture_tranche_t_elle", {}).get("decidable"):
        raise ValueError(f"{chemin} ne porte pas le contrôle sur fixture")
    if not d.get("lecart_au_compte_geometrique", {}).get("decidable"):
        raise ValueError(f"{chemin} ne porte pas l'écart au compte géométrique")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    f = d["la_fixture_tranche_t_elle"]
    g = d["lecart_au_compte_geometrique"]
    tr = d["traversees"]
    L, H = 1180, 660
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(28, 20, "Le marcheur compte juste, mais une feuille n'est pas un rayon", gros, ENCRE)
    ecrire(28, 46, f"{len(tr)} traversées complètes · fixture à "
                   f"{len(f['lots'])} angles · fourchette des deux instruments "
                   f"{g['fourchette_des_instruments_um']} µm", petit, GRIS)

    # ── Gauche : la fixture ──────────────────────────────────────────────────
    x0, y0, pw, ph = 60, 120, 430, 380
    ecrire(x0, y0 - 26, "contrôle : le compte rapporté à l'épaisseur, et au chemin", moyen, ENCRE)
    lots = f["lots"]
    vals = [x["compte_sur_epaisseur"] for x in lots] + [x["compte_sur_chemin"] for x in lots]
    lo, hi = min(0.6, min(vals) - 0.05), max(1.1, max(vals) + 0.05)

    def py(v):
        return y0 + ph - 20 - (v - lo) / (hi - lo) * (ph - 40)

    art.line([x0, py(1.0), x0 + pw, py(1.0)], fill=TRAIT, width=1)
    ecrire(x0 + pw + 4, int(py(1.0)) - 6, "1,000", petit, GRIS)
    larg = pw / max(1, len(lots))
    for i, x in enumerate(lots):
        cx = x0 + (i + 0.5) * larg
        for v, coul, dx in ((x["compte_sur_epaisseur"], EPAISSEUR, -8),
                            (x["compte_sur_chemin"], CHEMIN, +8)):
            yy = py(v)
            points.append((cx + dx, yy))
            art.line([cx + dx, py(1.0), cx + dx, yy], fill=coul, width=3)
            art.ellipse([cx + dx - 4, yy - 4, cx + dx + 4, yy + 4], fill=coul)
        ecrire(int(cx) - 14, y0 + ph - 12, f"{x['angle_a_la_normale_deg']:.0f}°", petit,
               GRIS if x["angle_a_la_normale_deg"] == 0 else ENCRE)
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    ecrire(x0, y0 + ph + 8, "angle imposé entre la direction et la normale · 0° est le témoin",
           petit, GRIS)
    for i, (coul, nom) in enumerate(((EPAISSEUR, "compte / épaisseur traversée"),
                                     (CHEMIN, "compte / chemin parcouru"))):
        yy = y0 + ph + 28 + i * 16
        art.ellipse([x0, yy + 3, x0 + 8, yy + 11], fill=coul)
        ecrire(x0 + 14, yy, nom, petit, ENCRE)
    ecrire(x0, y0 + ph + 64, f"médianes sur les angles obliques : épaisseur "
                             f"{f['compte_sur_epaisseur_median']} · chemin "
                             f"{f['compte_sur_chemin_median']}", petit, EPAISSEUR)

    # ── Droite : le rouleau ──────────────────────────────────────────────────
    x1, pw2 = x0 + pw + 110, L - (x0 + pw + 110) - 90
    ecrire(x1, y0 - 26, "le rouleau : l'espacement que chaque traversée implique", moyen, ENCRE)
    bas, haut = g["fourchette_des_instruments_um"]
    imp_c = [x["chemin_um"] / x["feuilles_comptees"] for x in tr]
    imp_r = [x["etendue_radiale_um"] / x["feuilles_comptees"] for x in tr]
    elo = min(min(imp_r), bas) - 10.0
    ehi = max(max(imp_c), haut) + 10.0

    def px(v):
        return x1 + (v - elo) / (ehi - elo) * pw2

    art.rectangle([px(bas), y0, px(haut), y0 + ph], fill=BANDE)
    hl = (ph - 20) / max(1, len(tr))
    for i, x in enumerate(tr):
        yy = y0 + 10 + i * hl
        a, b = px(x["chemin_um"] / x["feuilles_comptees"]), px(x["etendue_radiale_um"] / x["feuilles_comptees"])
        points.extend([(a, yy), (b, yy)])
        art.line([b, yy, a, yy], fill=TRAIT, width=1)
        art.ellipse([b - 3, yy - 3, b + 3, yy + 3], fill=RAYON)
        art.ellipse([a - 3, yy - 3, a + 3, yy + 3], fill=CHEMIN)
    art.rectangle([x1, y0, x1 + pw2, y0 + ph], outline=TRAIT, width=1)
    for v in range(int(elo // 20 + 1) * 20, int(ehi) + 1, 40):
        if x1 <= px(v) <= x1 + pw2:
            ecrire(int(px(v)) - 10, y0 + ph + 8, f"{v}", petit, GRIS)
    ecrire(x1, y0 + ph + 28, f"bande verte : les deux instruments, {bas:.0f} et {haut:.0f} µm "
                             f"(`R4-F14`)", petit, EPAISSEUR)
    for i, (coul, nom) in enumerate(((CHEMIN, f"par le CHEMIN · médiane "
                                              f"{g['espacement_implique_par_le_chemin_um']} µm"),
                                     (RAYON, f"par le RAYON · médiane "
                                             f"{g['espacement_implique_par_le_rayon_um']} µm"))):
        yy = y0 + ph + 48 + i * 16
        art.ellipse([x1, yy + 3, x1 + 8, yy + 11], fill=coul)
        ecrire(x1 + 14, yy, nom, petit, ENCRE)

    # ⚠ La bande de conclusion court sous les DEUX panneaux, donc elle commence sous leur bord
    # bas : posée plus haut, la garde de cadre la range dans le panneau de gauche et la déclare
    # débordante — un faux positif sur un texte parfaitement placé.
    ecrire(28, H - 52, f"le compteur est juste, et l'écart entre les deux lectures vaut "
                       f"{g['espacement_implique_par_le_chemin_um'] / g['espacement_implique_par_le_rayon_um']:.3f}",
           moyen, ENCRE)
    ecrire(28, H - 28, "traduire un compte de feuilles en étendue radiale coûterait "
                       f"{d['lecart_au_compte_geometrique']['par_espacement'][0]['erreur_mediane_spires']:+} "
                       "spires par traversée", petit, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    # ⚠ Trois cadres : les deux panneaux, et la bande de conclusion qui court sous les deux. Sans
    # le troisième, la garde de cadre range la conclusion dans le panneau de gauche et la déclare
    # débordante — un faux positif qui ferait déplacer un texte parfaitement placé.
    return (sortie, poses,
            [(x0 - 40, y0 - 30, x0 + pw + 40, y0 + ph + 84),
             (x1 - 4, y0 - 30, L - 4, y0 + ph + 84), (20, H - 60, L - 20, H)], points)


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

    def trav(ete, ch, n):
        return {"course": "a.json", "memoire_du_cap": 0.75, "bande": [0, 1], "rayon_mm": 6.0,
                "pas_voyants": 40, "etendue_radiale_um": ete, "chemin_um": ch,
                "feuilles_comptees": n, "obliquite_du_chemin": round(ch / ete, 3),
                "retour_radial": 1.0, "pas_en_butee": 0, "fraction_par_pas": 1.0,
                "etendue_radiale_parcourue_um": ete}

    faux = {
        "traversees": [trav(12400.0, 13520.0, 81.2), trav(7570.0, 9390.0, 56.5),
                       trav(13810.0, 14740.0, 88.8), trav(5200.0, 5400.0, 24.0)],
        "lecart_au_compte_geometrique": {
            "decidable": True, "traversees": 4, "fourchette_des_instruments_um": [164.0, 182.4],
            "espacement_implique_par_le_rayon_um": 140.3,
            "espacement_implique_par_le_chemin_um": 166.4,
            "espacement_implique_par_le_rayon_min": 46.8,
            "espacement_implique_par_le_rayon_max": 217.0,
            "espacement_implique_par_le_chemin_min": 137.1,
            "espacement_implique_par_le_chemin_max": 225.1,
            "marches_dont_le_chemin_tombe_dans_la_fourchette": 2,
            "le_compte_radial_est_sous_la_fourchette": True,
            "le_compte_radial_est_au_dessus": False,
            "le_compte_du_chemin_est_dans_la_fourchette": True,
            "par_espacement": [{"espacement_um": 164.0, "erreur_mediane_spires": 8.4,
                                "erreur_min_spires": -7.7, "erreur_max_spires": 99.3,
                                "marches_qui_sur_comptent": 18},
                               {"espacement_um": 182.4, "erreur_mediane_spires": 13.0,
                                "erreur_min_spires": -4.5, "erreur_max_spires": 103.3,
                                "marches_qui_sur_comptent": 20}]},
        "la_fixture_tranche_t_elle": {
            "decidable": True, "angles_obliques": 3,
            "compte_sur_epaisseur_median": 1.018, "compte_sur_chemin_median": 0.831,
            "le_compte_suit_lepaisseur": True, "le_compte_suit_le_chemin": False,
            "lots": [{"angle_a_la_normale_deg": 0.0, "pas": 20, "chemin_um": 3693.5,
                      "epaisseur_um": 3693.5, "feuilles_comptees": 21.58,
                      "compte_sur_epaisseur": 1.011, "compte_sur_chemin": 1.011,
                      "pas_en_butee": 0},
                     {"angle_a_la_normale_deg": 20.0, "pas": 20, "chemin_um": 3727.6,
                      "epaisseur_um": 3502.8, "feuilles_comptees": 21.07,
                      "compte_sur_epaisseur": 1.041, "compte_sur_chemin": 0.978,
                      "pas_en_butee": 0},
                     {"angle_a_la_normale_deg": 35.0, "pas": 19, "chemin_um": 5804.3,
                      "epaisseur_um": 4754.6, "feuilles_comptees": 27.87,
                      "compte_sur_epaisseur": 1.014, "compte_sur_chemin": 0.831,
                      "pas_en_butee": 0},
                     {"angle_a_la_normale_deg": 50.0, "pas": 20, "chemin_um": 5440.9,
                      "epaisseur_um": 3497.3, "feuilles_comptees": 20.57,
                      "compte_sur_epaisseur": 1.018, "compte_sur_chemin": 0.654,
                      "pas_en_butee": 0}]}}
    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "c.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", len(lu["traversees"]), 4)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())
        v("les trois séries ont trois couleurs",
          pixels.count(EPAISSEUR) > 80 and pixels.count(CHEMIN) > 80 and pixels.count(RAYON) > 40)
        v("la bande des deux instruments est peinte", pixels.count(BANDE) > 500)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f_ in poses if f_ is not None and y + f_.getbbox(t)[3] > im.size[1]], [])
        # ⚠ Un point appartient à l'UN des deux panneaux, pas aux deux : tester contre le seul
        # cadre de gauche déclarait débordants les huit points du panneau de droite.
        def dedans(x, y):
            return any(a <= x <= c and b <= y <= d for a, b, c, d in cadres[:2])
        v("tous les points tiennent dans un panneau",
          [1 for x, y in points if not dedans(x, y)], [])
        # ⚠⚠ LES SONDES : un JSON sans le contrôle sur fixture est REFUSÉ, parce que le panneau de
        # gauche est ce qui autorise à lire celui de droite.
        for nom_, bris in (("sans traversée", lambda x: x.update(traversees=[])),
                           ("sans fixture", lambda x: x.update(
                               la_fixture_tranche_t_elle={"decidable": False})),
                           ("sans écart", lambda x: x.update(
                               lecart_au_compte_geometrique={"decidable": False}))):
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
    p.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures"
                   / "combien_de_feuilles_le_marcheur_croit_franchir.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "136_une_feuille_nest_pas_un_rayon.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
