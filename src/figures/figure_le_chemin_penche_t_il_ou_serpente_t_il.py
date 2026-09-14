#!/usr/bin/env python3
"""Le chemin du marcheur penche-t-il sur le rayon, ou serpente-t-il autour ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** À gauche, la
distribution de l'angle entre chaque pas et le rayon, pour les deux courses — et, sur le même axe,
ce que le MEME instrument lit sur des matières dont l'inclinaison est connue : une spirale à
0,394°, une pile plane, une pile froissée. L'écart entre ces repères et la masse du rouleau est
tout l'argument. À droite, marche par marche : le penchant contre le rayon de départ, la cohérence
en remplissage, et l'obliquité du maillage humain en regard.

  uv run python src/figures/figure_le_chemin_penche_t_il_ou_serpente_t_il.py \\
      --json docs/mesures/le_chemin_penche_t_il_ou_serpente_t_il.json \\
      --sortie docs/images/137_le_chemin_penche_sur_le_rayon.png
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
CAP = (60, 110, 90)
SANS = (176, 92, 42)
MAILLAGE = (150, 96, 176)
FIXTURE = (86, 104, 132)
BANDE = (236, 234, 228)
RETOUR = (176, 62, 62)

ANGLE_MAX = 90.0
LARGEUR_CASE = 3.0


def lire(chemin: Path) -> dict:
    """Le JSON de `le_chemin_penche_t_il_ou_serpente_t_il.py`.

    ⚠⚠ Refuse un JSON sans marche arrivée, et un JSON dont le contrôle de l'axe a ECHOUE : une
    décomposition cylindrique sur un repère où l'axe n'est pas z dessinerait une part « axiale »
    qui ne mesure pas ce que la légende annonce.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d or not d.get("par_course"):
        raise ValueError(f"{chemin} : pas de course")
    if not d.get("laxe", {}).get("laxe_du_rouleau_est_le_z_du_volume"):
        raise ValueError(f"{chemin} : l'axe du rouleau n'est pas le z du volume")
    if not any(c.get("marches") for c in d["par_course"]):
        raise ValueError(f"{chemin} : aucune marche arrivée")
    return d


def _histogramme(angles: list[float]) -> list[float]:
    """La part des pas par case de trois degrés, la dernière case portant tout ce qui dépasse 90°."""
    n = int(ANGLE_MAX / LARGEUR_CASE)
    cases = [0.0] * (n + 1)
    for a in angles:
        k = n if a >= ANGLE_MAX else int(a / LARGEUR_CASE)
        cases[k] += 1.0
    total = max(1.0, sum(cases))
    return [c / total for c in cases]


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1180, 760
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    courses = d["par_course"]
    avec = next((c for c in courses if c["memoire_du_cap"]), None)
    sans = next((c for c in courses if not c["memoire_du_cap"]), None)
    total = sum(c["marches_arrivees"] for c in courses)
    pas = sum(c["la_forme_du_penchant"].get("pas", 0) for c in courses
              if c["la_forme_du_penchant"].get("decidable"))
    ecrire(28, 20, "Le chemin penche sur le rayon, il ne serpente pas autour", gros, ENCRE)
    ecrire(28, 46, f"{total} marches arrivées ({d['laxe']['radiaux']} radiaux de `107` à "
                   f"{d['laxe']['angle_au_plan_perpendiculaire_a_z_median_deg']}° du plan "
                   f"perpendiculaire à z, donc l'axe du rouleau est le z du volume) · {pas} pas",
           petit, GRIS)

    # ── Gauche : la distribution de l'angle, et les repères de la fixture ─────
    x0, y0, pw, ph = 60, 150, 520, 380
    ecrire(x0, y0 - 26, "part des pas par angle au rayon (cases de 3°)", moyen, ENCRE)

    def px(a):
        return x0 + 10 + (min(a, ANGLE_MAX + LARGEUR_CASE) / (ANGLE_MAX + LARGEUR_CASE)) * (pw - 20)

    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    # ⚠ Les repères de la fixture occupent le haut du panneau : sans cette réserve leur étiquette
    # tombe sur celle de la première course, et deux textes superposés sont deux textes perdus.
    reserve = 56
    # ⚠ Seize pixels de bandeau AU-DESSUS de chaque histogramme : la première version écrivait
    # l'étiquette de la course DANS les barres, où elle devenait illisible sans qu'aucun contrôle
    # ne le voie — `textes_qui_se_recouvrent` compare des textes entre eux, pas un texte à un
    # aplat.
    bandeau = 16
    hauteur = (ph - 8 - reserve - 2 * (bandeau + 6)) // 2
    points: list[tuple[float, float]] = []
    for i, c in enumerate((avec, sans)):
        if c is None or not c["marches"]:
            continue
        base = y0 + reserve + bandeau + hauteur + i * (hauteur + bandeau + 6)
        coul = CAP if c["memoire_du_cap"] else SANS
        angles = [a for m in c["marches"] for a in m.get("angles_deg", [])]
        cases = _histogramme(angles)
        haut = max(cases) or 1.0
        for k, part in enumerate(cases):
            a0, a1 = px(k * LARGEUR_CASE), px((k + 1) * LARGEUR_CASE)
            hh = (part / haut) * (hauteur - 6)
            if hh <= 0:
                continue
            # ⚠ La dernière case est celle des pas qui REVIENNENT vers l'axe : elle a sa couleur,
            # sinon un retour se lit comme un grand penchant, ce qui n'est pas la même panne.
            art.rectangle([a0, base - hh, a1 - 1, base], fill=RETOUR if k == len(cases) - 1 else coul)
            points.append((a1 - 1, base - hh))
        art.line([x0 + 6, base, x0 + pw - 6, base], fill=TRAIT, width=1)
        f = c["la_forme_du_penchant"]
        ecrire(x0 + 12, base - hauteur - bandeau + 1,
               f"λ = {c['memoire_du_cap']} · médiane {f['angle_median_deg']}° · "
               f"cohérence {f['coherence_mediane']} · retours {f['pas_au_dela_de_90_deg']}",
               petit, coul)
    for a in range(0, int(ANGLE_MAX), 15):
        ecrire(int(px(a)) - 6, y0 + ph + 4, f"{a}", petit, GRIS)
    ecrire(int(px(ANGLE_MAX + LARGEUR_CASE)) - 34, y0 + ph + 4, "> 90°", petit, RETOUR)

    # ⚠ Les repères de la fixture sont dessinés SUR le même axe : c'est ce qui rend la distance
    # entre « une matière plane » et « le rouleau » visible plutôt qu'écrite.
    fx = d.get("la_fixture_tranche_t_elle") or {}
    reperes = []
    if fx.get("spirales"):
        s = fx["spirales"][0]
        lu = max((c["angle_median_deg"] for c in s["par_cap"] if c["angle_median_deg"] is not None),
                 default=None)
        if lu is not None:
            reperes.append((lu, f"spirale {s['rayon_mm']} mm (vraie {s['inclinaison_analytique_deg']}°)"))
    if fx.get("penchant_de_la_pile_froissee_deg") is not None:
        reperes.append((fx["penchant_de_la_pile_froissee_deg"], "pile froissée par feuille"))
    accord = (avec or sans or {}).get("le_penchant_saccorde_t_il_au_maillage", {})
    if accord.get("decidable"):
        reperes.append((accord["maillage_median_deg"], "normale du maillage humain"))
    yr = y0 + 4
    for i, (a, nom) in enumerate(sorted(reperes)):
        xa = px(a)
        coul = MAILLAGE if "maillage" in nom else FIXTURE
        art.line([xa, y0 + 2, xa, y0 + ph - 2], fill=coul, width=1)
        ecrire(min(int(xa) + 4, x0 + pw - 150), yr + i * 15, f"{a}° · {nom}", petit, coul)

    # ── Droite : marche par marche ────────────────────────────────────────────
    x1 = x0 + pw + 70
    pw2 = L - x1 - 40
    ecrire(x1, y0 - 26, "par marche : penchant médian contre rayon de départ", moyen, ENCRE)
    art.rectangle([x1, y0, x1 + pw2, y0 + ph], outline=TRAIT, width=1)
    marches = [(c, m) for c in courses for m in c["marches"]]
    rr = [m["rayon_mm"] for _, m in marches] or [0.0, 1.0]
    r_lo, r_hi = min(rr) - 0.8, max(rr) + 0.8
    a_hi = max([m["angle_median_deg"] for _, m in marches] + [40.0]) * 1.1

    def rx(r):
        return x1 + 12 + (r - r_lo) / max(1e-9, r_hi - r_lo) * (pw2 - 24)

    def ay(a):
        return y0 + ph - 14 - (a / a_hi) * (ph - 28)

    for a in range(0, int(a_hi) + 1, 15):
        art.line([x1 + 4, ay(a), x1 + pw2 - 4, ay(a)], fill=TRAIT, width=1)
        ecrire(x1 - 26, int(ay(a)) - 6, f"{a}°", petit, GRIS)
    for r in range(int(r_lo) + 1, int(r_hi) + 1, 2):
        ecrire(int(rx(r)) - 6, y0 + ph + 4, f"{r}", petit, GRIS)
    maillage_par_bande = {}
    for c in courses:
        mm = c.get("le_penchant_saccorde_t_il_au_maillage", {})
        if mm.get("decidable"):
            maillage_par_bande[c["source"]] = mm
    for c, m in marches:
        xx, yy = rx(m["rayon_mm"]), ay(m["angle_median_deg"])
        points.append((xx, yy))
        coul = CAP if c["memoire_du_cap"] else SANS
        # ⚠ Le remplissage porte la COHERENCE : un disque plein penche, un anneau serpente.
        if m["coherence_tangentielle"] >= 0.5:
            art.ellipse([xx - 5, yy - 5, xx + 5, yy + 5], fill=coul)
        else:
            art.ellipse([xx - 5, yy - 5, xx + 5, yy + 5], outline=coul, width=2)
        if m["pas_au_dela_de_90_deg"]:
            art.line([xx - 7, yy - 7, xx + 7, yy + 7], fill=RETOUR, width=1)
    mm = maillage_par_bande.get((avec or sans or {}).get("source"))
    if mm:
        lo, hi = mm["etendue_du_maillage_deg"]
        art.rectangle([rx(r_lo) + 2, ay(hi), rx(r_hi) - 2, ay(lo)], outline=MAILLAGE, width=1)
        ecrire(x1 + 14, int(ay(hi)) - 15,
               f"obliquité du maillage humain, {lo}° à {hi}°", petit, MAILLAGE)
    ecrire(x1, y0 + ph + 24, "rayon de départ (mm) · disque plein : cohérent (penche) · "
                             "anneau : incohérent (serpente)", petit, GRIS)
    ecrire(x1, y0 + ph + 40, "croix rouge : la marche compte des pas qui reviennent vers l'axe",
           petit, GRIS)

    # ── La bande de conclusion, sous les deux panneaux ────────────────────────
    yb = y0 + ph + 76
    art.rectangle([x0, yb, L - 40, H - 20], fill=BANDE, outline=TRAIT, width=1)
    lignes = []
    if fx:
        s = fx["spirales"][0] if fx.get("spirales") else None
        if s:
            lu = min(c["angle_median_deg"] for c in s["par_cap"]
                     if c["angle_median_deg"] is not None)
            lignes.append((f"★ Le même instrument lit {lu}° sur une spirale dont l'inclinaison "
                           f"analytique vaut {s['inclinaison_analytique_deg']}°, et "
                           f"{fx['piles'][0]['par_cap'][0]['angle_median_deg']}° sur une pile plane. "
                           f"Le penchant est donc dans la matière.", ENCRE))
    cc = d.get("le_cap_change_t_il_le_penchant")
    if cc and cc.get("decidable"):
        lignes.append((f"★ Le cap fait passer le penchant de {cc['angle_median_sans_cap_deg']}° à "
                       f"{cc['angle_median_avec_cap_deg']}°, la cohérence de "
                       f"{cc['coherence_sans_cap']} à {cc['coherence_avec_cap']}, et les retours "
                       f"vers l'axe de {cc['part_au_dela_de_90_sans_cap']} à "
                       f"{cc['part_au_dela_de_90_avec_cap']}.", ENCRE))
    if accord.get("decidable"):
        lignes.append((f"★ Contre le maillage tracé à la main : {accord['penchant_median_deg']}° "
                       f"contre {accord['maillage_median_deg']}°, indiscernable en niveau "
                       f"(p apparié {accord['p_apparie']}) — mais les rangs ne s'accordent pas "
                       f"(rho {accord['rho_de_spearman']:+}, p {accord['p_du_rang']}).", ENCRE))
    if fx.get("coherence_de_la_pile_froissee") is not None:
        lignes.append((f"✗ Ce que la mesure NE tranche PAS : sous un cap, une pile froissée rend "
                       f"une cohérence de {fx['coherence_de_la_pile_froissee']} — donc la cohérence "
                       f"ne sépare pas des feuilles inclinées de feuilles froissées.", RETOUR))
    for i, (texte, coul) in enumerate(lignes):
        ecrire(x0 + 14, yb + 12 + i * 22, texte, petit, coul)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    # ⚠ Trois cadres : un par panneau, plus un pour la bande de conclusion. `textes_hors_cadre`
    # range un texte sous le cadre qui contient son origine, donc sans le troisième la conclusion
    # serait rangée sous le panneau de gauche et jugée débordante.
    cadres = [(x0 - 40, y0 - 30, x0 + pw + 10, yb - 2),
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

    def marche(r0, ang, coh, retours=0, bande=(10, 20)):
        n = 20
        angles = [ang] * (n - retours) + [110.0] * retours
        return {"marche": 0, "bande": list(bande), "rayon_mm": r0, "pas": n,
                "angles_deg": angles, "angle_median_deg": ang,
                "angle_q1_deg": ang - 4, "angle_q3_deg": ang + 4,
                "pas_au_dela_de_90_deg": retours, "axial_median": 0.2,
                "glissement_axial_median_um": 57.8,
                "axial_absolu_median": 0.3, "azimutal_absolu_median": 0.2,
                "coherence_tangentielle": coh, "chemin_um": 3460.0,
                "rayon_depart_um": r0 * 1000.0, "etendue_cylindrique_um": 3000.0,
                "etendue_spherique_um": 3050.0}

    def forme(ms, coh):
        tous = [a for m in ms for a in m["angles_deg"]]
        return {"decidable": True, "marches": len(ms), "pas": len(tous),
                "angle_median_deg": 25.0, "angle_q1_deg": 16.0, "angle_q3_deg": 38.0,
                "angle_p90_deg": 48.0, "pas_au_dela_de_90_deg": sum(m["pas_au_dela_de_90_deg"] for m in ms),
                "part_des_pas_au_dela_de_90": 0.0, "coherence_mediane": coh, "coherence_min": 0.4,
                "etendue_cylindrique_mediane_um": 3000.0, "etendue_spherique_mediane_um": 3050.0,
                "le_rayon_spherique_surestime_letendue_de": 1.0098, "et_au_plus_de": 1.19,
                "axial_absolu_median": 0.33, "azimutal_absolu_median": 0.19,
                "glissement_axial_median_um": 57.8,
                "bandes_qui_glissent_vers_les_z_croissants": 2, "p_du_signe_axial": 1.0,
                "le_glissement_axial_a_un_sens_prefere": False,
                "le_chemin_penche": coh > 0.5, "le_chemin_serpente": coh <= 0.5}

    acc = {"decidable": True, "paires": 4, "penchant_median_deg": 28.05, "maillage_median_deg": 33.24,
           "etendue_du_maillage_deg": [29.62, 38.57], "etendue_du_penchant_deg": [9.22, 49.05],
           "ecart_median_deg": -4.44, "p_apparie": 0.14648, "rho_de_spearman": -0.6868,
           "p_du_rang": 0.00951, "le_niveau_est_indiscernable": True, "les_rangs_saccordent": False}
    a_ms = [marche(6.3, 28.0, 0.98, bande=(10, 20)), marche(10.5, 15.0, 0.47, bande=(21, 30)),
            marche(14.7, 29.0, 0.82, bande=(31, 40)), marche(18.6, 43.6, 0.89, bande=(41, 50))]
    s_ms = [marche(6.3, 26.6, 0.89), marche(10.5, 41.2, 0.68, retours=4),
            marche(16.2, 57.9, 0.18, retours=6), marche(18.6, 42.9, 0.72)]
    faux = {"sources": ["a.json", "b.json"], "voxel_um": 2.4, "bandes_du_maillage": 28,
            "laxe": {"decidable": True, "radiaux": 32,
                     "angle_au_plan_perpendiculaire_a_z_median_deg": 0.35, "angle_max_deg": 0.404,
                     "laxe_du_rouleau_est_le_z_du_volume": True},
            "par_course": [
                {"source": "a.json", "memoire_du_cap": 0.75, "marches_arrivees": len(a_ms),
                 "marches": a_ms, "la_forme_du_penchant": forme(a_ms, 0.925),
                 "le_penchant_saccorde_t_il_au_maillage": acc},
                {"source": "b.json", "memoire_du_cap": 0.0, "marches_arrivees": len(s_ms),
                 "marches": s_ms, "la_forme_du_penchant": forme(s_ms, 0.719),
                 "le_penchant_saccorde_t_il_au_maillage": {**acc, "p_apparie": 0.42578}}],
            "le_cap_change_t_il_le_penchant": {
                "decidable": True, "angle_median_avec_cap_deg": 25.48,
                "angle_median_sans_cap_deg": 36.35, "coherence_avec_cap": 0.925,
                "coherence_sans_cap": 0.719, "part_au_dela_de_90_avec_cap": 0.0,
                "part_au_dela_de_90_sans_cap": 0.1037, "le_cap_reduit_le_penchant": True,
                "le_cap_supprime_les_retours": True},
            "la_fixture_tranche_t_elle": {
                "pas_max": 40,
                "spirales": [{"rayon_mm": 4.0, "phase_du_depart": 0.0,
                              "inclinaison_analytique_deg": 0.394,
                              "par_cap": [{"memoire_du_cap": 0.0, "pas": 40, "angle_median_deg": 0.22,
                                           "coherence_tangentielle": 1.0}]}],
                "piles": [{"amplitude_um": 0.0, "longueur_donde_um": 393.6,
                           "par_cap": [{"memoire_du_cap": 0.0, "pas": 40, "angle_median_deg": 0.01,
                                        "coherence_tangentielle": 1.0}]},
                          {"amplitude_um": 47.469, "longueur_donde_um": 393.6,
                           "par_cap": [{"memoire_du_cap": 0.0, "pas": 40, "angle_median_deg": 13.32,
                                        "coherence_tangentielle": 0.647}]}],
                "la_spirale_reste_sous_un_degre": True, "la_spirale_suit_la_loi_du_rayon": True,
                "la_pile_plane_ne_penche_pas": True, "penchant_de_la_pile_froissee_deg": 13.32,
                "coherence_de_la_pile_froissee": 0.859,
                "la_coherence_separe_le_froisse_du_penche": False}}

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "c.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", len(lu["par_course"]), 2)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())
        v("les deux courses ont deux couleurs", pixels.count(CAP) > 200 and pixels.count(SANS) > 200)
        v("les pas qui reviennent vers l'axe sont peints à part", pixels.count(RETOUR) > 60)
        v("le repère du maillage humain est tracé", pixels.count(MAILLAGE) > 150)
        v("le repère de la fixture est tracé", pixels.count(FIXTURE) > 100)
        v("la bande de conclusion est peinte", pixels.count(BANDE) > 3000)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        for gx0, gy0, gx1, gy1 in cadres[:1]:
            v("tous les points tiennent dans leur cadre",
              [1 for x, y in points if not (gx0 <= x <= gx1 + 640 and gy0 <= y <= gy1)], [])
        v("les quatre lignes de conclusion sont écrites",
          sum(1 for _, _, t, _ in poses if t.startswith("★") or t.startswith("✗")), 4)
        # sondes
        for nom_, bris in (
                ("sans course", lambda x: x.update(par_course=[])),
                ("sans marche arrivée", lambda x: [c.update(marches=[]) for c in x["par_course"]]),
                ("dont l'axe n'est pas z",
                 lambda x: x["laxe"].update(laxe_du_rouleau_est_le_z_du_volume=False)),
                ("porteur d'un message", lambda x: x.update(message="mesure absente"))):
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
        # ⚠ Sonde de l'histogramme : la dernière case doit porter TOUT ce qui dépasse 90°, sinon
        # un retour vers l'axe disparaîtrait de l'image sans que rien ne le dise.
        h = _histogramme([10.0, 95.0, 179.0])
        v("l'histogramme range tout ce qui dépasse 90° dans la dernière case",
          abs(h[-1] - 2.0 / 3.0) < 1e-9)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_chemin_penche_t_il_ou_serpente_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "137_le_chemin_penche_sur_le_rayon.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
