#!/usr/bin/env python3
"""Le budget de pas n'achète plus de portée : le net culmine, puis recule.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** La portée d'une marche
n'est pas ce qu'elle parcourt, c'est la distance à laquelle elle EMMÈNE. Les deux se confondent tant
que la marche va droit, et se séparent dès qu'elle tourne. Un tableau de deux colonnes laisse le
lecteur faire la soustraction ; une courbe la fait voir.

  ⭐⭐⭐⭐ **Un seul panneau, deux courses, les mêmes axes.** En abscisse le chemin parcouru, en
  ordonnée le déplacement net. La **diagonale** est la marche parfaite : tout ce qu'elle parcourt,
  elle l'emmène. Les marches de vingt pas tiennent la diagonale et s'arrêtent là. Les trois marches
  de cent douze pas la quittent, culminent, puis **redescendent** pendant que l'abscisse continue.

  ⭐⭐ Chaque marche longue porte deux marques : un cercle à son **maximum** de net, un carré à son
  dernier pas. Quand le carré est plus bas que le cercle, le dernier tiers du budget a été négatif.

⚠ Les deux axes partagent la **même échelle**, sinon la diagonale ne serait plus à 45° et
« quitter la diagonale » ne voudrait plus rien dire.

⚠ Trois marches atteignent le plafond. La figure montre qu'une marche peut reculer, pas à quelle
fréquence.

  uv run python src/figures/figure_jusquou_le_net_progresse.py \\
      --json docs/mesures/le_marcheur_derive_sur_la_re_course.json \\
      --court docs/mesures/le_marcheur_derive_t_il.json \\
      --sortie docs/images/130_le_budget_nachete_plus_de_portee.png
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
COURT = (86, 104, 132)
LONG = (196, 140, 60)
ALERTE = (176, 62, 62)
PARFAIT = (60, 110, 90)


def lire(long_p: Path, court_p: Path) -> dict:
    """Les deux courses, et le refus de dessiner ce qui n'a pas été mesuré.

    ⚠⚠ Une figure qui dessine un JSON indécidable invente la forme qu'elle montre. Les deux
    courses doivent porter un `jusquou_le_net_progresse_t_il` décidable, sinon rien n'est dessiné.
    """
    d = json.loads(Path(long_p).read_text(encoding="utf-8"))
    c = json.loads(Path(court_p).read_text(encoding="utf-8"))
    for nom, x in (("longue", d), ("courte", c)):
        j = x.get("jusquou_le_net_progresse_t_il", {})
        if not j.get("decidable"):
            raise ValueError(f"la course {nom} n'a pas de progression décidable : "
                             f"{j.get('pourquoi', 'absente')}")
        if not x.get("la_trajectoire_est_elle_celle_de_la_course", {}).get(
                "la_trajectoire_est_celle_de_la_course"):
            raise ValueError(f"la course {nom} ne se reconstruit pas : rien à dessiner")
        for m in j["par_marche"]:
            if len(m.get("chemin_um", [])) != len(m.get("net_um", [])):
                raise ValueError(f"la course {nom} a un chemin et un net de longueurs "
                                 f"différentes : ils ne décrivent pas la même marche")
    return {"longue": d, "courte": c}


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    jl = d["longue"]["jusquou_le_net_progresse_t_il"]
    jc = d["courte"]["jusquou_le_net_progresse_t_il"]
    L, H = 1080, 640
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(28, 20, "Le budget de pas n'achète plus de portée", gros, ENCRE)
    ecrire(28, 46, f"le chemin parcouru contre le déplacement net · "
                   f"{jc['marches']} marches à {jc['plafond']} pas et {jl['marches']} à "
                   f"{jl['plafond']}", petit, GRIS)

    x0, y0 = 92, 92
    pw, ph = L - x0 - 300, H - y0 - 118
    # ⚠⚠ LES DEUX AXES PARTAGENT LA MÊME ÉCHELLE, et c'est la condition pour que la diagonale
    # veuille dire quelque chose : étirer l'ordonnée ferait passer une marche parfaite pour une
    # marche qui s'envole, et une marche qui recule pour une marche qui plafonne.
    tout = [v for j in (jl, jc) for m in j["par_marche"]
            for v in (m["chemin_um"] + m["net_um"])]
    haut = max(tout)
    ech = min(pw, ph) / max(1e-9, haut)
    ox, oy = x0, y0 + ph

    def pt(chemin, net):
        return (ox + chemin * ech, oy - net * ech)

    art.line([ox, oy, ox + pw, oy], fill=TRAIT, width=1)
    art.line([ox, oy, ox, y0], fill=TRAIT, width=1)
    # La diagonale : tout ce qui est parcouru est emmené.
    diag = min(pw, ph)
    art.line([ox, oy, ox + diag, oy - diag], fill=PARFAIT, width=1)
    ecrire(ox + diag - 150, oy - diag - 4, "la marche parfaite", petit, PARFAIT)

    points = []
    for m in jc["par_marche"]:
        pts = [pt(c_, n_) for c_, n_ in zip(m["chemin_um"], m["net_um"])]
        points.extend(pts)
        art.line(pts, fill=COURT, width=1)
    for m in jl["par_marche"]:
        pts = [pt(c_, n_) for c_, n_ in zip(m["chemin_um"], m["net_um"])]
        points.extend(pts)
        art.line(pts, fill=LONG, width=2)
        k = m["net_um"].index(max(m["net_um"]))
        cx, cy = pts[k]
        # ⭐⭐ Le cercle est le maximum, le carré la fin. Quand le carré est SOUS le cercle, le
        # dernier tiers du budget a été négatif — et il est peint en alerte pour qu'on le voie.
        art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=LONG, width=2)
        fx, fy = pts[-1]
        recule = m["net_au_plafond_um"] < m["net_maximum_um"] - 1.0
        art.rectangle([fx - 4, fy - 4, fx + 4, fy + 4],
                      fill=ALERTE if recule else LONG)

    ecrire(28, y0 - 26, "déplacement net (µm)", petit, GRIS)
    ecrire(ox, oy + 10, "chemin parcouru (µm)", petit, GRIS)
    for part in (0.25, 0.5, 0.75, 1.0):
        v_ = haut * part
        art.line([ox + v_ * ech, oy, ox + v_ * ech, oy + 4], fill=TRAIT, width=1)
        ecrire(int(ox + v_ * ech) - 18, oy + 24, f"{int(v_)}", petit, GRIS)
        art.line([ox - 4, oy - v_ * ech, ox, oy - v_ * ech], fill=TRAIT, width=1)
        ecrire(28, int(oy - v_ * ech) - 6, f"{int(v_)}", petit, GRIS)

    # ── La colonne de lecture ────────────────────────────────────────────────
    tx = ox + pw + 34
    ecrire(tx, y0, f"à {jc['plafond']} pas", moyen, COURT)
    ecrire(tx, y0 + 22, f"{jc['marches_dont_le_net_culmine_avant_le_plafond']}/{jc['marches']} "
                        f"culminent avant", petit, ENCRE)
    ecrire(tx, y0 + 40, "le budget achète de la portée", petit, PARFAIT)
    ecrire(tx, y0 + 84, f"à {jl['plafond']} pas", moyen, LONG)
    ecrire(tx, y0 + 106, f"{jl['marches_dont_le_net_culmine_avant_le_plafond']}/{jl['marches']} "
                         f"culminent avant", petit, ENCRE)
    ecrire(tx, y0 + 124, "il n'en achète plus", petit, ALERTE)
    ecrire(tx, y0 + 168, "net médian", moyen, ENCRE)
    ecrire(tx, y0 + 190, f"maximum {jl['net_maximum_median_um']} µm", petit, ENCRE)
    ecrire(tx, y0 + 208, f"au pas {jl['k_du_maximum_median']}", petit, GRIS)
    ecrire(tx, y0 + 226, f"au plafond {jl['net_au_plafond_median_um']} µm", petit, ALERTE)
    ecrire(tx, y0 + 270, "○ maximum du net", petit, GRIS)
    ecrire(tx, y0 + 288, "■ dernier pas", petit, GRIS)

    ecrire(28, H - 72, "une marche qui tourne parcourt sans emmener : la portée est l'ordonnée, "
                       "jamais l'abscisse", moyen, ENCRE)
    ecrire(28, H - 46, f"population tenue constante : seules les marches qui atteignent "
                       f"{jl['plafond']} pas sont tracées, sur "
                       f"{jl['marches_de_la_course']} de la course", petit, GRIS)
    ecrire(28, H - 26, "trois marches au plafond : la figure montre qu'une marche peut reculer, "
                       "pas à quelle fréquence", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph)], points


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

    def course(marches, nets, plafond, culminent):
        return {
            "la_trajectoire_est_elle_celle_de_la_course": {
                "la_trajectoire_est_celle_de_la_course": True},
            "jusquou_le_net_progresse_t_il": {
                "decidable": True, "plafond": plafond, "marches": marches,
                "marches_de_la_course": marches + 2,
                "k_du_maximum_median": plafond // 2,
                "net_maximum_median_um": max(nets[0]),
                "net_au_plafond_median_um": nets[0][-1],
                "marches_dont_le_net_culmine_avant_le_plafond": culminent,
                "le_budget_achete_de_la_portee": culminent == 0,
                "par_marche": [
                    {"rayon_mm": 4.0 + i,
                     "chemin_um": [200.0 * (k + 1) for k in range(len(n))],
                     "net_um": list(n),
                     "net_maximum_um": max(n), "net_au_plafond_um": n[-1],
                     "k_du_maximum_median": 1}
                    for i, n in enumerate(nets)]}}

    # ⚠⚠ LES DEUX COURSES NE DOIVENT PAS SE SUPERPOSER DANS LA FIXTURE, sinon la plus large
    # efface l'autre et le controle « la course courte est tracee » echoue pour une raison qui
    # n'est pas celle qu'il verifie. Ma premiere version les faisait partir du meme point avec le
    # meme net, donc une seule ligne etait visible.
    monte = [[180.0 * (k + 1) - 10.0 * i for k in range(6)] for i in range(3)]
    recule = [[200.0 * (k + 1) for k in range(8)] + [1400.0, 900.0, 400.0] for _ in range(3)]
    faux = {"longue": course(3, recule, 11, 3), "courte": course(3, monte, 6, 0)}

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        jl, jc = r / "l.json", r / "c.json"
        jl.write_text(json.dumps(faux["longue"]), encoding="utf-8")
        jc.write_text(json.dumps(faux["courte"]), encoding="utf-8")
        lu = lire(jl, jc)
        v("les deux courses sont lues", len(lu), 2)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1080)
        # ⚠⚠ LE COMPTAGE EST BORNE AU CADRE, ET C'EST CE QUI REND LA SONDE HONNETE. La colonne
        # de lecture ecrit « il n'en achete plus » en ALERTE, donc compter sur toute la toile
        # trouverait des centaines de pixels d'alerte meme sur une course ou rien ne recule : le
        # controle passerait pour la mauvaise raison, puis son inverse echouerait.
        def dans_le_cadre(image, cadre):
            gx0_, gy0_, gx1_, gy1_ = (int(round(v_)) for v_ in cadre)
            return list(image.crop((gx0_, gy0_, gx1_, gy1_)).convert("RGB").getdata())

        px = dans_le_cadre(im, cadres[0])
        v("la course courte est tracée", px.count(COURT) > 100)
        v("la course longue est tracée", px.count(LONG) > 100)
        v("la diagonale de la marche parfaite est tracée", px.count(PARFAIT) > 100)
        # ⭐⭐⭐⭐ LA SONDE QUI COMPTE : une marche qui RECULE doit se distinguer à l'écran, sinon
        # la figure dessine la même chose pour les deux courses et ne montre rien.
        v("une marche qui recule est marquée en alerte", px.count(ALERTE) > 20)
        sans = {"longue": course(3, monte, 6, 0), "courte": course(3, monte, 6, 0)}
        jl.write_text(json.dumps(sans["longue"]), encoding="utf-8")
        _, _, cadres2, _ = dessiner(lire(jl, jc), r / "g.png")
        px2 = dans_le_cadre(Image.open(r / "g.png"), cadres2[0])
        v("... et une course sans recul n'en porte aucune", px2.count(ALERTE) < 20)

        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        # ⚠⚠ LA garde qu'aucune garde de TEXTE ne peut rendre : les courbes doivent tenir dans
        # leur cadre. Une marche dont le net dépasserait l'emprise serait dessinée hors de la
        # toile, en silence.
        gx0, gy0, gx1, gy1 = cadres[0]
        v("toutes les courbes tiennent dans leur cadre",
          [1 for x, y in points if not (gx0 - 1 <= x <= gx1 + 1 and gy0 - 1 <= y <= gy1 + 1)], [])

        for nom, bris in (
                ("indécidable", lambda x: x["jusquou_le_net_progresse_t_il"].update(
                    decidable=False, pourquoi="pas assez de marches")),
                ("irréconciliable", lambda x: x[
                    "la_trajectoire_est_elle_celle_de_la_course"].update(
                        la_trajectoire_est_celle_de_la_course=False)),
                ("chemin et net de longueurs différentes",
                 lambda x: x["jusquou_le_net_progresse_t_il"]["par_marche"][0].update(
                     chemin_um=[1.0, 2.0]))):
            casse = json.loads(json.dumps(faux["longue"]))
            bris(casse)
            jl.write_text(json.dumps(casse), encoding="utf-8")
            try:
                lire(jl, jc)
                v(f"sonde : une course {nom} est refusée", False)
            except ValueError:
                v(f"sonde : une course {nom} est refusée", True)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "le_marcheur_derive_sur_la_re_course.json")
    p.add_argument("--court", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_marcheur_derive_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "130_le_budget_nachete_plus_de_portee.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json, a.court), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
