#!/usr/bin/env python3
"""Le marcheur ne dérive pas : ses virages se compensent.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** `117` a montré que le
taux de confirmation ne baisse pas avec la profondeur. Ça ne dit rien de la trajectoire : une
marche peut confirmer ses vingt pas en tournant lentement pour longer la feuille au lieu de la
traverser.

  ⭐⭐⭐ Le panneau de GAUCHE dessine les dix-neuf trajectoires reconstruites, chacune aplatie dans
  **son plan le plus défavorable** — celui où son écart à la droite est maximal — et tournée pour
  que son déplacement net parte vers la droite. Elles ondulent et elles avancent ; aucune ne
  s'enroule.

  ⭐⭐⭐⭐ Le panneau de DROITE est le témoin, et c'est lui qui distingue « ne pas empirer » de
  « corriger ». Chaque marche est comparée à un tirage qui garde **exactement** son virage à
  chaque pas mais en tire la direction au hasard. Dix-sept traits sur dix-neuf montent : la marche
  réelle est plus droite que le hasard de mêmes virages.

⚠ Vingt pas font environ quatre millimètres, un sixième de l'étendue radiale des départs. La figure
ne dit rien des cent et quelques transferts qu'un rouleau entier demande.

  uv run python src/figures/figure_le_marcheur_derive_t_il.py \\
      --json docs/mesures/le_marcheur_derive_t_il.json \\
      --sortie docs/images/119_le_marcheur_ne_derive_pas.png
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
MARCHE = (86, 104, 132)
REEL = (60, 110, 90)
SIMULE = (196, 140, 60)
ALERTE = (176, 62, 62)


def lire(chemin: Path) -> dict:
    """Le JSON de `le_marcheur_derive_t_il.py`.

    ⚠⚠ Refuse un JSON dont la trajectoire ne s'est pas reconstruite : dessiner un chemin qui n'est
    pas celui de la course produirait une image juste au pixel près au sujet d'une autre marche.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    g = d.get("la_trajectoire_est_elle_celle_de_la_course", {})
    if not g.get("la_trajectoire_est_celle_de_la_course"):
        raise ValueError(f"{chemin} : la trajectoire n'est pas celle de la course")
    if not d.get("traces"):
        raise ValueError(f"{chemin} ne porte aucune trace")
    if not d.get("temoin_les_virages_se_compensent", {}).get("decidable"):
        raise ValueError(f"{chemin} ne porte pas le témoin")
    for t in d["traces"]:
        if len(t.get("xy_um", [])) < 2:
            raise ValueError(f"{chemin} : une trace n'a pas deux points")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres."""
    traces = d["traces"]
    w = d["temoin_les_virages_se_compensent"]
    deg = d["la_marche_se_degrade_t_elle"]
    L, H = 1180, 560
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(28, 20, "Le marcheur ne dérive pas : ses virages se compensent", gros, ENCRE)
    ecrire(28, 46, f"{len(traces)} marches d'au moins {min(t['pas'] for t in traces)} pas "
                   f"voyants · {d['pas_voyants']} pas · source {d['source']}", petit, GRIS)

    # ── Panneau gauche : les trajectoires ────────────────────────────────────
    x0, y0 = 40, 112
    pw, ph = 660, 300
    ecrire(x0, y0 - 26, "les trajectoires, aplaties dans leur plan le plus défavorable",
           moyen, ENCRE)
    # ⚠⚠ L'emprise est celle des VRAIS minimums et maximums, pas des valeurs absolues : une marche
    # qui recule passe en x négatif, et cadrer sur `max(abs(x))` la dessine hors de la toile. Ma
    # première version le faisait, et le dessin sortait par la gauche sans qu'aucune garde de
    # texte ne puisse le voir — d'où le contrôle sur les POINTS, plus bas.
    xs = [x for t in traces for x, _ in t["xy_um"]]
    ys = [y for t in traces for _, y in t["xy_um"]]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    # ⚠⚠ Les deux axes partagent la MÊME échelle. Étirer l'axe des écarts rendrait une ondulation
    # de 5 % aussi visible qu'un demi-tour, ce qui est exactement le mensonge qu'une figure de
    # rectitude peut faire.
    ech = min((pw - 24) / max(1e-9, xmax - xmin), (ph - 24) / max(1e-9, ymax - ymin))
    ox = x0 + 12 - xmin * ech
    oy = y0 + 12 + ymax * ech
    art.line([x0, oy, x0 + pw, oy], fill=TRAIT, width=1)
    points = []
    for t in traces:
        pts = [(ox + x * ech, oy - y * ech) for x, y in t["xy_um"]]
        points.extend(pts)
        art.line(pts, fill=MARCHE, width=1)
        art.ellipse([pts[-1][0] - 2, pts[-1][1] - 2, pts[-1][0] + 2, pts[-1][1] + 2], fill=MARCHE)
    ecrire(x0, y0 + ph + 8, f"{int(xmax - xmin)} µm de bout en bout · même échelle sur les deux "
                            f"axes", petit, GRIS)
    ecrire(x0, y0 + ph + 28, f"rectitude {deg['rectitude_premiere_moitie']} sur la 1re moitié "
                             f"contre {deg['rectitude_seconde_moitie']} sur la 2e "
                             f"(p {deg['p_appariee']})", petit, ENCRE)
    ecrire(x0, y0 + ph + 48, "donc rien ne s'accumule sur vingt pas", petit, REEL)

    # ── Panneau droit : le témoin apparié ────────────────────────────────────
    x1, y1 = x0 + pw + 90, y0
    pw2, ph2 = L - x1 - 40, 300
    ecrire(x1, y1 - 26, "témoin : mêmes virages, direction tirée au hasard", moyen, ENCRE)
    paires = sorted(zip(w["reels"], w["simules"]), key=lambda p: p[1])
    bas = min(min(w["reels"]), min(w["simules"]))
    haut = max(max(w["reels"]), max(w["simules"]))
    span = max(1e-9, haut - bas)
    base = y1 + ph2 - 40
    larg = max(6, int(pw2 / max(1, len(paires))) - 4)
    for i, (r_, s_) in enumerate(paires):
        x = x1 + i * (larg + 4) + larg // 2
        yr = base - (r_ - bas) / span * (ph2 - 70)
        ys = base - (s_ - bas) / span * (ph2 - 70)
        art.line([x, ys, x, yr], fill=REEL if r_ > s_ else ALERTE, width=2)
        art.ellipse([x - 3, ys - 3, x + 3, ys + 3], fill=SIMULE)
        art.ellipse([x - 3, yr - 3, x + 3, yr + 3], fill=REEL if r_ > s_ else ALERTE)
    art.line([x1, base, x1 + pw2, base], fill=TRAIT, width=1)
    ecrire(x1, base + 8, f"rectitude, {bas:.2f} → {haut:.2f}", petit, GRIS)
    ecrire(x1, base + 32, f"réel {w['rectitude_reelle']} contre simulé "
                          f"{w['rectitude_simulee']}", petit, ENCRE)
    ecrire(x1, base + 52, f"{w['marches_ou_le_reel_est_plus_droit']}/{w['marches']} marches, "
                          f"p {w['p_appariee']}", petit, REEL)

    s = d["le_virage_a_t_il_un_sens"]
    ecrire(28, H - 52, f"et le virage n'a pas de sens privilégié : rotation cumulée autour de "
                       f"l'axe {s['rotation_cumulee_mediane_deg']:+}° médian "
                       f"(p {s['p_contre_zero']}), donc pas de spirale", moyen, ENCRE)
    ecrire(28, H - 26, "vingt pas font environ quatre millimètres, un sixième de l'étendue "
                       "radiale des départs", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph), (x1, y1, x1 + pw2, y1 + ph2)], points


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et quatre sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    def trace(i):
        return {"rayon_mm": 4.0 + i, "pas": 20, "rectitude": 0.9,
                "xy_um": [[200.0 * k, 60.0 * ((k + i) % 3 - 1)] for k in range(21)]}

    faux = {
        "source": "m.json", "marches": 24, "pas_voyants": 382,
        "la_trajectoire_est_elle_celle_de_la_course": {
            "decidable": True, "ecart_max_um": 0.5, "tolerance_um": 1.0,
            "la_trajectoire_est_celle_de_la_course": True},
        "la_marche_se_degrade_t_elle": {
            "decidable": True, "marches": 19, "rectitude_premiere_moitie": 0.944,
            "rectitude_seconde_moitie": 0.942, "p_appariee": 0.8906,
            "la_marche_se_degrade": False},
        "le_virage_a_t_il_un_sens": {
            "decidable": True, "rotation_cumulee_mediane_deg": 13.2,
            "p_contre_zero": 0.1564, "le_virage_a_un_sens": False},
        "temoin_les_virages_se_compensent": {
            "decidable": True, "marches": 19, "tirages": 400,
            "rectitude_reelle": 0.928, "rectitude_simulee": 0.811,
            "marches_ou_le_reel_est_plus_droit": 17, "p_appariee": 0.00141,
            "les_virages_se_compensent": True,
            "reels": [0.80 + 0.01 * k for k in range(19)],
            "simules": [0.78 + 0.008 * k for k in range(19)]},
        "traces": [trace(i) for i in range(19)],
    }
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        j = r / "m.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", len(lu["traces"]), 19)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.getdata())
        v("les trajectoires sont tracées", pixels.count(MARCHE) > 500)
        v("le réel et le simulé ont deux couleurs", pixels.count(REEL) > 100
          and pixels.count(SIMULE) > 100)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        # ⚠⚠ LA garde qu'aucune garde de TEXTE ne peut rendre : les trajectoires elles-mêmes
        # doivent tenir dans leur cadre. Une marche qui recule passe en x négatif, et la première
        # version de cette figure la dessinait hors de la toile, en silence.
        gx0, gy0, gx1, gy1 = cadres[0]
        v("toutes les trajectoires tiennent dans leur cadre",
          [1 for x, y in points if not (gx0 <= x <= gx1 and gy0 <= y <= gy1)], [])

        # ⚠⚠ LA sonde qui compte : une trajectoire qui ne s'est pas reconstruite est REFUSÉE.
        casse = json.loads(json.dumps(faux))
        casse["la_trajectoire_est_elle_celle_de_la_course"][
            "la_trajectoire_est_celle_de_la_course"] = False
        j.write_text(json.dumps(casse), encoding="utf-8")
        try:
            lire(j)
            v("sonde : une trajectoire irréconciliable est refusée", False)
        except ValueError:
            v("sonde : une trajectoire irréconciliable est refusée", True)

        for nom, bris in (("sans trace", lambda x: x.update(traces=[])),
                          ("sans témoin", lambda x: x.update(
                              temoin_les_virages_se_compensent={"decidable": False})),
                          ("trace à un point", lambda x: x["traces"][0].update(
                              xy_um=[[0.0, 0.0]]))):
            c = json.loads(json.dumps(faux))
            bris(c)
            j.write_text(json.dumps(c), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON {nom} est refusé", False)
            except ValueError:
                v(f"sonde : un JSON {nom} est refusé", True)

        # ⚠ Une marche qui perd contre le tirage doit se distinguer à l'écran.
        perd = json.loads(json.dumps(faux))
        perd["temoin_les_virages_se_compensent"]["reels"] = [0.70] * 19
        j.write_text(json.dumps(perd), encoding="utf-8")
        dessiner(lire(j), r / "g.png")[0]
        px2 = list(Image.open(r / "g.png").convert("RGB").getdata())
        v("une marche qui perd est peinte en alerte", px2.count(ALERTE) > 100)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_marcheur_derive_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "119_le_marcheur_ne_derive_pas.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
