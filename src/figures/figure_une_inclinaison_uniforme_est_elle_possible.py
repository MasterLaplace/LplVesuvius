#!/usr/bin/env python3
"""Une inclinaison uniforme est-elle possible, et un froissement suffit-il ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** À gauche, combien de
feuilles une inclinaison **uniforme** ferait croiser en un tour, contre l'unique feuille qu'un
rouleau croise : la courbe passe par 1 à un dixième de degré et par plusieurs centaines aux
trente-quatre degrés mesurés. À droite, ce qu'un marcheur paie sur une spirale **froissée** dont
l'amplitude est connue : le trait horizontal est le 1,186 du rouleau, et la zone teintée celle où
l'amplitude replie les feuilles les unes sur les autres. Le point qui compte est que la courbe
n'atteint le trait qu'une fois entrée dans la zone.

  uv run python src/figures/figure_une_inclinaison_uniforme_est_elle_possible.py \\
      --json docs/mesures/une_inclinaison_uniforme_est_elle_possible.json \\
      --sortie docs/images/139_une_inclinaison_uniforme_est_impossible.png
"""
from __future__ import annotations

import argparse
import json
import math
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
MESURE = (60, 110, 90)
PREDIT = (86, 104, 132)
ROULEAU = (176, 92, 42)
INTERDIT = (240, 222, 218)
REPERE = (150, 96, 176)


def lire(chemin: Path) -> dict:
    """Le JSON de `une_inclinaison_uniforme_est_elle_possible.py`.

    ⚠⚠ Refuse un JSON dont la fixture n'a rendu aucun rapport : la moitié droite de l'image est
    l'argument, et une courbe sans point est une figure juste au pixel près au sujet de rien.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    if not d.get("linclinaison_uniforme_est_elle_possible", {}).get("decidable"):
        raise ValueError(f"{chemin} : la moitié géométrique n'est pas décidable")
    lots = [x for x in d.get("sur_la_spirale_froissee", {}).get("lots", [])
            if "rapport_mesure_median" in x]
    if len(lots) < 2:
        raise ValueError(f"{chemin} : {len(lots)} amplitude(s) mesurée(s), il en faut deux")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1180, 720
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    u = d["linclinaison_uniforme_est_elle_possible"]
    j = d.get("juger", {})
    ecrire(28, 20, "Une inclinaison uniforme est impossible, et un froissement ne suffit pas",
           gros, ENCRE)
    ecrire(28, 46, f"inclinaison mesurée sur le maillage : {u['inclinaison_mesuree_deg']}° · "
                   f"espacements {' et '.join(str(e) for e in d['espacements_um'])} µm · "
                   f"rayons {', '.join(str(r) for r in d['rayons_mm'])} mm", petit, GRIS)

    # ── Gauche : combien de feuilles une inclinaison uniforme fait croiser ────
    x0, y0, pw, ph = 60, 150, 500, 360
    ecrire(x0, y0 - 26, "feuilles croisées par tour, selon l'inclinaison uniforme", moyen, ENCRE)
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    # ⚠ Echelle LOGARITHMIQUE en ordonnee : de une feuille a quatre cents, une echelle lineaire
    # ecraserait tout le bas de la courbe, c'est-a-dire l'endroit ou un rouleau vit.
    lo, hi = 0.05, 1000.0

    def ly(v):
        v = min(max(float(v), lo), hi)
        return y0 + ph - 26 - (math.log10(v / lo) / math.log10(hi / lo)) * (ph - 46)

    ax_lo, ax_hi = 0.02, 60.0

    def lx(a):
        a = min(max(float(a), ax_lo), ax_hi)
        return x0 + 34 + (math.log10(a / ax_lo) / math.log10(ax_hi / ax_lo)) * (pw - 48)

    for e in (0.1, 1.0, 10.0, 100.0, 1000.0):
        art.line([x0 + 6, ly(e), x0 + pw - 6, ly(e)], fill=TRAIT, width=1)
        ecrire(x0 + 6, int(ly(e)) - 12, f"{e:g}", petit, GRIS)
    for a in (0.1, 1.0, 10.0):
        ecrire(int(lx(a)) - 6, y0 + ph - 18, f"{a:g}°", petit, GRIS)
    # une courbe par rayon, a l'espacement le plus bas de la paire
    esp = min(d["espacements_um"])
    for r_mm in d["rayons_mm"]:
        precedent = None
        for k in range(140):
            a = ax_lo * (ax_hi / ax_lo) ** (k / 139.0)
            n = 2.0 * math.pi * r_mm * 1000.0 * math.sin(math.radians(a)) / esp
            q = (lx(a), ly(n))
            if precedent is not None:
                art.line([precedent[0], precedent[1], q[0], q[1]], fill=PREDIT, width=1)
            precedent = q
        points.append(precedent)
        ecrire(int(lx(ax_hi)) - 60, int(ly(2.0 * math.pi * r_mm * 1000.0
                                           * math.sin(math.radians(ax_hi)) / esp)) - 12,
               f"{r_mm} mm", petit, PREDIT)
    # ⚠ La ligne « UNE feuille par tour » est ce qu'un rouleau EST, pas un seuil choisi.
    art.line([x0 + 6, ly(1.0), x0 + pw - 6, ly(1.0)], fill=ROULEAU, width=2)
    ecrire(x0 + 12, int(ly(1.0)) + 4, "un rouleau croise UNE feuille par tour", petit, ROULEAU)
    xm = lx(u["inclinaison_mesuree_deg"])
    art.line([xm, y0 + 6, xm, y0 + ph - 22], fill=REPERE, width=1)
    ecrire(int(xm) - 132, y0 + 8, f"{u['inclinaison_mesuree_deg']}° mesurés →", petit, REPERE)
    xa = lx(u["inclinaison_autorisee_max_deg"])
    art.line([xa, y0 + 6, xa, y0 + ph - 22], fill=MESURE, width=1)
    ecrire(int(xa) + 4, y0 + 24, f"← {u['inclinaison_autorisee_min_deg']} à "
                                 f"{u['inclinaison_autorisee_max_deg']}° autorisés", petit, MESURE)
    ecrire(x0, y0 + ph + 8, "inclinaison uniforme (échelles logarithmiques)", petit, GRIS)

    # ── Droite : ce qu'un marcheur paie sur une spirale froissée ─────────────
    x1 = x0 + pw + 80
    pw2 = L - x1 - 40
    ecrire(x1, y0 - 26, "ce qu'un marcheur paie, selon l'amplitude du froissement", moyen, ENCRE)
    lots = [x for x in d["sur_la_spirale_froissee"]["lots"] if "rapport_mesure_median" in x]
    a_max = max(x["amplitude_um"] for x in lots) or 1.0
    r_max = max([x["rapport_predit_median"] for x in lots] + [1.3]) * 1.06

    def ax_(a):
        return x1 + 40 + (float(a) / a_max) * (pw2 - 56)

    def ay_(v):
        return y0 + ph - 26 - ((float(v) - 1.0) / max(r_max - 1.0, 1e-9)) * (ph - 46)

    # ⚠ La zone TEINTEE est celle ou la phase recule : la matiere n'y est plus une pile, donc un
    # rapport qu'on n'atteint que dedans n'est pas une explication.
    replient = [x for x in lots if x["les_feuilles_se_croisent"]]
    if replient:
        a0 = min(x["amplitude_um"] for x in replient)
        art.rectangle([ax_(a0), y0 + 2, x1 + pw2 - 2, y0 + ph - 24], fill=INTERDIT)
        ecrire(int(ax_(a0)) + 8, y0 + 44, "au-delà, les feuilles se croisent", petit, ROULEAU)
    art.rectangle([x1, y0, x1 + pw2, y0 + ph], outline=TRAIT, width=1)
    for v_ in [1.0 + 0.2 * k for k in range(0, int((r_max - 1.0) / 0.2) + 1)]:
        art.line([x1 + 6, ay_(v_), x1 + pw2 - 6, ay_(v_)], fill=TRAIT, width=1)
        ecrire(x1 + 6, int(ay_(v_)) - 12, f"{v_:.1f}", petit, GRIS)
    for coul, cle, nom in ((MESURE, "rapport_mesure_median", "mesuré"),
                           (PREDIT, "rapport_predit_median", "prédit par les normales")):
        precedent = None
        for x in sorted(lots, key=lambda z: z["amplitude_um"]):
            q = (ax_(x["amplitude_um"]), ay_(x[cle]))
            if precedent is not None:
                art.line([precedent[0], precedent[1], q[0], q[1]], fill=coul, width=2)
            art.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=coul)
            points.append(q)
            precedent = q
    rr = j.get("rapport_du_rouleau")
    if rr is not None:
        art.line([x1 + 6, ay_(rr), x1 + pw2 - 6, ay_(rr)], fill=ROULEAU, width=2)
        # ⚠ L'etiquette va a DROITE : posee a gauche elle tombe sur les graduations de l'axe, et
        # deux textes superposes sont deux textes perdus.
        ecrire(x1 + pw2 - 152, int(ay_(rr)) - 14, f"le rouleau coûte {rr}", petit, ROULEAU)
    for x in sorted(lots, key=lambda z: z["amplitude_um"]):
        ecrire(int(ax_(x["amplitude_um"])) - 12, y0 + ph - 18,
               f"{x['amplitude_um']:.0f}", petit, GRIS)
    ecrire(x1, y0 + ph + 8, "amplitude du froissement (µm) · espacement des feuilles "
                            f"{d['sur_la_spirale_froissee']['espacement_de_la_fixture_um']:.0f} µm",
           petit, GRIS)
    # ⚠ La legende va EN HAUT A GAUCHE du panneau : posee en bas elle croisait la ligne du
    # rouleau et la zone teintee, donc elle se lisait sur trois aplats a la fois.
    yl = y0 + 8
    for coul, nom in ((MESURE, "mesuré : chemin / étendue radiale"),
                      (PREDIT, "prédit : 1/⟨cos⟩ sur les normales rencontrées")):
        art.rectangle([x1 + 46, yl + 3, x1 + 58, yl + 9], fill=coul)
        ecrire(x1 + 64, yl, nom, petit, coul)
        yl += 16

    # ── La bande de conclusion ───────────────────────────────────────────────
    yb = y0 + ph + 30
    art.rectangle([x0, yb, L - 40, H - 20], fill=BANDE, outline=TRAIT, width=1)
    lignes = []
    if j.get("decidable"):
        lignes.append((f"★ Un rouleau croise UNE feuille par tour, donc il n'autorise qu'une "
                       f"inclinaison uniforme de {u['inclinaison_autorisee_min_deg']} à "
                       f"{u['inclinaison_autorisee_max_deg']}° — {u['combien_de_fois_trop_grande']} "
                       f"fois moins que les {u['inclinaison_mesuree_deg']}° mesurés localement.",
                       ENCRE))
        lignes.append((f"★ À cette inclinaison, un froissement fait payer "
                       f"{j['rapport_a_linclinaison_mesuree']} au marcheur, quand le rouleau lui "
                       f"coûte {j['rapport_du_rouleau']}.", ENCRE))
        if j.get("amplitude_qui_atteint_le_rouleau_um") is not None:
            lignes.append((f"✗ Il faut {j['amplitude_qui_atteint_le_rouleau_um']:.0f} µm "
                           f"d'amplitude ({j['amplitude_sur_espacement']} fois l'espacement) pour "
                           f"atteindre le rouleau, et là la phase recule sur "
                           f"{j['part_du_rayon_ou_la_phase_recule']:.0%} du rayon : les feuilles "
                           f"se croisent, ce n'est plus une pile.", ROULEAU))
        if j.get("part_de_lobliquite_que_le_cap_recupere") is not None:
            lignes.append((f"★ Et le cap récupère "
                           f"{j['part_de_lobliquite_que_le_cap_recupere']:.0%} de l'obliquité que "
                           f"le champ de normales imposerait : le marcheur paie bien moins que ce "
                           f"qu'il rencontre.", ENCRE))
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

    def lot(amp, mes, pre, croisent, incl, imed):
        return {"amplitude_um": amp, "amplitude_sur_espacement": round(amp / 173.0, 2),
                "inclinaison_max_deg": incl, "inclinaison_mediane_deg": imed,
                "rapport_mesure_median": mes, "rapport_predit_median": pre,
                "les_feuilles_se_croisent": croisent,
                "part_du_rayon_ou_la_phase_recule": 0.29 if croisent else 0.0,
                "et_au_plus": 0.33 if croisent else 0.0, "marches": [{}]}

    u = {"decidable": True, "inclinaison_mesuree_deg": 34.06,
         "lignes": [{"rayon_mm": 4.07, "espacement_um": 164.0,
                     "feuilles_par_tour_a_linclinaison_mesuree": 87.33,
                     "inclinaison_autorisee_deg": 0.3674},
                    {"rayon_mm": 18.62, "espacement_um": 182.4,
                     "feuilles_par_tour_a_linclinaison_mesuree": 359.23,
                     "inclinaison_autorisee_deg": 0.0893}],
         "inclinaison_autorisee_min_deg": 0.0803, "inclinaison_autorisee_max_deg": 0.4087,
         "feuilles_par_tour_min": 78.52, "feuilles_par_tour_max": 399.53,
         "combien_de_fois_trop_grande": 83.3, "une_inclinaison_uniforme_est_impossible": True}
    lots = [lot(0.0, 1.0, 1.0, False, 0.0, 0.12), lot(42.4, 1.0078, 1.0256, False, 34.09, 11.09),
            lot(100.0, 1.0228, 1.1412, False, 57.94, 22.48),
            lot(200.0, 1.1013, 1.445, True, 72.61, 38.98),
            lot(400.0, 1.8577, 2.1967, True, 81.1, 60.47)]
    faux = {"inclinaison_mesuree_deg": 34.06, "espacements_um": [164.0, 182.4],
            "rayons_mm": [4.07, 10.51, 18.62],
            "linclinaison_uniforme_est_elle_possible": u,
            "sur_la_spirale_froissee": {"rayon_mm": 10.0, "longueur_donde_um": 393.6,
                                        "espacement_de_la_fixture_um": 173.0, "pas_max": 40,
                                        "departs": 8, "lots": lots},
            "juger": {"decidable": True, "rapport_du_rouleau": 1.186,
                      "une_inclinaison_uniforme_est_impossible": True,
                      "inclinaison_autorisee_max_deg": 0.4087,
                      "feuilles_par_tour_a_linclinaison_mesuree": 399.53,
                      "amplitude_a_linclinaison_mesuree_um": 42.4,
                      "inclinaison_max_de_ce_lot_deg": 34.09,
                      "rapport_a_linclinaison_mesuree": 1.0078,
                      "rapport_predit_a_linclinaison_mesuree": 1.0256,
                      "amplitude_qui_atteint_le_rouleau_um": 400.0,
                      "amplitude_sur_espacement": 2.31,
                      "part_du_rayon_ou_la_phase_recule": 0.292,
                      "a_cette_amplitude_les_feuilles_se_croisent": True,
                      "rapport_le_plus_haut_sans_croiser": 1.0228,
                      "a_lamplitude_sans_croiser_um": 100.0,
                      "le_froissement_explique_le_rouleau": False,
                      "part_de_lobliquite_que_le_cap_recupere": 0.734}}

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "c.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", lu["inclinaison_mesuree_deg"], 34.06)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())
        v("les deux courbes de droite ont deux couleurs",
          pixels.count(MESURE) > 200 and pixels.count(PREDIT) > 200)
        v("la zone où les feuilles se croisent est teintée", pixels.count(INTERDIT) > 2000)
        v("le repère de l'inclinaison mesurée est tracé", pixels.count(REPERE) > 150)
        v("la ligne du rouleau est tracée", pixels.count(ROULEAU) > 300)
        v("la bande de conclusion est peinte", pixels.count(BANDE) > 3000)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        gx0, gy0, _, gy1 = cadres[0]
        v("tous les points tiennent dans un cadre",
          [1 for x, y in points if not (gx0 <= x <= cadres[1][2] and gy0 <= y <= gy1)], [])
        v("les quatre lignes de conclusion sont écrites",
          sum(1 for _, _, t, _ in poses if t.startswith("★") or t.startswith("✗")), 4)
        for nom_, bris in (
                ("porteur d'un message", lambda x: x.update(message="fixture injoignable")),
                ("sans moitié géométrique",
                 lambda x: x["linclinaison_uniforme_est_elle_possible"].update(decidable=False)),
                ("sans amplitude mesurée",
                 lambda x: x["sur_la_spirale_froissee"].update(lots=[]))):
            c = json.loads(json.dumps(faux))
            bris(c)
            j.write_text(json.dumps(c), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON {nom_} est refusé", False)
            except ValueError:
                v(f"sonde : un JSON {nom_} est refusé", True)
        # ⚠ Sonde : si AUCUNE amplitude ne replie les feuilles, la zone teintee ne doit pas exister.
        c = json.loads(json.dumps(faux))
        for x in c["sur_la_spirale_froissee"]["lots"]:
            x["les_feuilles_se_croisent"] = False
        j.write_text(json.dumps(c), encoding="utf-8")
        p2, _, _, _ = dessiner(lire(j), r / "h.png")
        im2 = Image.open(p2).convert("RGB")
        px2 = list(im2.get_flattened_data()) if hasattr(im2, "get_flattened_data") \
            else list(im2.getdata())
        v("⚠ sonde : sans repliement, la zone teintée n'est pas peinte", px2.count(INTERDIT), 0)
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
                   / "une_inclinaison_uniforme_est_elle_possible.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "139_une_inclinaison_uniforme_est_impossible.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
