#!/usr/bin/env python3
"""Là où la matière cesse de se lire, est-ce la surface du rouleau ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** Chaque marche arrêtée
sur « plus rien à lire » est un point : en abscisse le rayon où elle s'est arrêtée, en ordonnée le
rayon de la surface extérieure du rouleau lu sur son propre rayon. Un point sur la diagonale est une
marche qui s'est arrêtée **parce qu'il n'y avait plus de rouleau devant elle** ; un point loin
au-dessous est un vide intérieur. Le panneau de droite montre, pour chaque arrêt, ce que le volume
contient sur les seize pas qui suivent : du remplissage jusqu'au bout, ou de la matière qui reprend.

  uv run python src/figures/figure_ou_la_matiere_cesse_de_se_lire.py \\
      --json docs/mesures/ou_la_matiere_cesse_de_se_lire.json \\
      --sortie docs/images/135_la_surface_du_rouleau.png
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
SORTI = (60, 110, 90)
VIDE = (176, 62, 62)
PLAFOND = (86, 104, 132)
AUTRE = (196, 140, 60)
REMPLISSAGE = (90, 92, 96)
MATIERE = (222, 214, 190)


def lire(chemin: Path) -> dict:
    """Le JSON de `ou_la_matiere_cesse_de_se_lire.py`.

    ⚠⚠ Refuse un JSON sans arrêt décidable : une diagonale sans point est une image juste au pixel
    près au sujet de rien.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d or not d.get("par_course"):
        raise ValueError(f"{chemin} : pas de course")
    n = sum(1 for c in d["par_course"] for x in c["arrets"] if x["verdict"].get("decidable"))
    if n == 0:
        raise ValueError(f"{chemin} : aucun arrêt décidable")
    return d


def _couleur(x: dict):
    v = x["verdict"]
    if x["fin"] == "plafond":
        return PLAFOND
    if v.get("sorti_du_rouleau"):
        return SORTI
    if v.get("dans_un_vide_interieur"):
        return VIDE
    return AUTRE


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    arrets = [(c, x) for c in d["par_course"] for x in c["arrets"]]
    L, H = 1180, 700
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    total = sum(c["resume"]["plus_rien_a_lire"] for c in d["par_course"])
    sortis = sum(c["resume"]["sortis_du_rouleau"] for c in d["par_course"])
    vides = sum(c["resume"]["dans_un_vide_interieur"] for c in d["par_course"])
    ecrire(28, 20, "Là où la matière cesse de se lire, est-ce la surface du rouleau ?", gros, ENCRE)
    ecrire(28, 46, f"{d.get('fragment')} · {len(d['par_course'])} courses · {total} arrêts « plus rien à lire » "
                   f"· {sortis} sortis du rouleau · {vides} dans un vide intérieur", petit, GRIS)

    # ── Gauche : rayon d'arrêt contre rayon de la surface ─────────────────────
    x0, y0, pw, ph = 60, 110, 520, 480
    ecrire(x0, y0 - 26, "rayon de la surface extérieure (mm) contre rayon de l'arrêt (mm)", moyen, ENCRE)
    decid = [(c, x) for c, x in arrets if x["verdict"].get("decidable")]
    rs = [x["rayon_arret_mm"] for _, x in decid] + [x["surface"]["rayon_exterieur_mm"] for _, x in decid]
    lo, hi = min(rs) - 1.0, max(rs) + 1.0
    # ⚠ MÊME échelle sur les deux axes et bornée par le PLUS PETIT côté : la première version
    # prenait la largeur, et la diagonale sortait du cadre par le haut (le panneau est plus large
    # que haut). Une diagonale qui déborde est une diagonale qu'on ne peut plus lire.
    ech = min(pw - 20, ph - 20) / max(1e-9, hi - lo)

    def px(v):
        return x0 + 10 + (v - lo) * ech

    def py(v):
        return y0 + ph - 10 - (v - lo) * ech

    pas_mm = float(d.get("pas_um", 173.0)) / 1000.0
    # la bande « à un pas de la diagonale » : un arrêt qui y tombe est à la surface
    art.polygon([(px(lo), py(lo + pas_mm)), (px(hi - pas_mm), py(hi)), (px(hi), py(hi)),
                 (px(hi), py(hi - pas_mm)), (px(lo + pas_mm), py(lo)), (px(lo), py(lo))], fill=BANDE)
    art.line([px(lo), py(lo), px(hi), py(hi)], fill=SORTI, width=1)
    for v in range(int(lo) + 1, int(hi) + 1, 2):
        ecrire(int(px(v)) - 6, y0 + ph + 4, f"{v}", petit, GRIS)
        ecrire(x0 - 30, int(py(v)) - 6, f"{v}", petit, GRIS)
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    points = []
    for c, x in decid:
        a, b = px(x["rayon_arret_mm"]), py(x["surface"]["rayon_exterieur_mm"])
        points.append((a, b))
        coul = _couleur(x)
        if x["fin"] == "plafond":
            art.rectangle([a - 4, b - 4, a + 4, b + 4], outline=coul, width=2)
        else:
            art.ellipse([a - 5, b - 5, a + 5, b + 5], fill=coul)
        if x["surface"].get("coupe_par_le_bord_du_champ"):
            art.line([a - 7, b - 7, a + 7, b + 7], fill=ENCRE, width=1)
    ecrire(x0, y0 + ph + 24, "bande : à un pas (173 µm) de la diagonale · carré : au plafond", petit, GRIS)
    ecrire(x0, y0 + ph + 40, "barre oblique : surface coupée par le bord du champ", petit, GRIS)
    # la légende sur deux colonnes : quatre lignes sortaient par le bas de la toile.
    yl = y0 + ph + 60
    for i, (coul, nom) in enumerate(((SORTI, "sorti du rouleau"), (VIDE, "vide intérieur, la matière reprend"),
                                     (AUTRE, "ni l'un ni l'autre"), (PLAFOND, "au plafond de pas"))):
        xl = x0 + (i % 2) * 260
        yy = yl + (i // 2) * 16
        art.ellipse([xl, yy + 3, xl + 8, yy + 11], fill=coul)
        ecrire(xl + 14, yy, nom, petit, ENCRE)

    # ── Droite : ce qu'il y a au-delà de chaque arrêt ─────────────────────────
    x1 = x0 + pw + 60
    pw2 = L - x1 - 30
    ecrire(x1, y0 - 26, "au-delà de l'arrêt, pas par pas : remplissage ou matière", moyen, ENCRE)
    lignes = [(c, x) for c, x in arrets if x["fin"] == "plus rien a lire"]
    hl = max(10, min(18, (ph - 10) // max(1, len(lignes))))
    n_pas = int(d.get("pas_au_dela", 16)) + 1
    lcase = (pw2 - 150) / n_pas
    for i, (c, x) in enumerate(lignes):
        y = y0 + i * hl
        ecrire(x1, y, f"r {x['rayon_arret_mm']:>5.2f} · λ {c['memoire_du_cap']}", petit, ENCRE)
        parts = x["au_dela"]["part_au_remplissage_par_pas"]
        for k, part in enumerate(parts):
            if part is None:
                continue
            g = int(REMPLISSAGE[0] * part + MATIERE[0] * (1 - part))
            coul = (g, int(REMPLISSAGE[1] * part + MATIERE[1] * (1 - part)),
                    int(REMPLISSAGE[2] * part + MATIERE[2] * (1 - part)))
            art.rectangle([x1 + 130 + k * lcase, y + 1, x1 + 130 + (k + 1) * lcase - 1, y + hl - 2],
                          fill=coul)
        art.ellipse([x1 + 118, y + hl // 2 - 3, x1 + 124, y + hl // 2 + 3], fill=_couleur(x))
    yb = y0 + len(lignes) * hl + 8
    ecrire(x1 + 130, yb, "pas 0 (l'arrêt) … 16 → sombre : remplissage, clair : matière", petit, GRIS)

    # ── Le verdict, sous la bande de droite ───────────────────────────────────
    yv = yb + 26
    for c in d["par_course"]:
        s = c["resume"]
        ecrire(x1, yv, f"{c['source']} (λ {c['memoire_du_cap']}) : {s['sortis_du_rouleau']}/{s['decidables']} "
                       f"sortis du rouleau, {s['dans_un_vide_interieur']} dans un vide", moyen, ENCRE)
        ecrire(x1, yv + 20, f"   {s['a_la_surface']} à la surface, {s['au_dela_de_la_surface']} au-delà · "
                            f"surface médiane {s['rayon_exterieur_median_mm']} mm · écart médian "
                            f"{s['ecart_a_la_surface_median_mm']} mm", petit, GRIS)
        yv += 44

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0 - 40, y0 - 30, x0 + pw + 10, H), (x1 - 4, y0 - 30, L - 4, H)], points


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

    def arret(r0, r_arret, r_ext, fin, reprend=None, borne=False):
        parts = [1.0] * 17 if reprend is None else [1.0] * reprend + [0.4] * (17 - reprend)
        sorti = fin == "plus rien a lire" and reprend is None and abs(r_arret - r_ext) <= 0.173
        return {"marche": 0, "rayon_mm": r0, "fin": fin, "pas": 40,
                "rayon_arret_mm": r_arret,
                "au_dela": {"part_au_remplissage_par_pas": parts,
                            "la_matiere_reprend_au_pas": reprend, "rien_sur_seize_pas": reprend is None},
                "surface": {"decidable": True, "rayon_exterieur_mm": r_ext,
                            "coupe_par_le_bord_du_champ": borne},
                "verdict": {"decidable": True, "ecart_a_la_surface_mm": round(r_arret - r_ext, 2),
                            "a_la_surface": sorti, "au_dela_de_la_surface": False,
                            "dans_un_vide_interieur": reprend is not None, "sorti_du_rouleau": sorti}}

    def course(nom, lam, arrets_):
        rien = [x for x in arrets_ if x["fin"] == "plus rien a lire"]
        return {"source": nom, "memoire_du_cap": lam, "marches": len(arrets_), "arrets": arrets_,
                "resume": {"plus_rien_a_lire": len(rien), "decidables": len(rien),
                           "sortis_du_rouleau": sum(1 for x in rien if x["verdict"]["sorti_du_rouleau"]),
                           "a_la_surface": sum(1 for x in rien if x["verdict"]["a_la_surface"]),
                           "au_dela_de_la_surface": 0,
                           "dans_un_vide_interieur": sum(1 for x in rien if x["verdict"]["dans_un_vide_interieur"]),
                           "rien_sur_seize_pas": sum(1 for x in rien if x["au_dela"]["rien_sur_seize_pas"]),
                           "ecart_a_la_surface_median_mm": 0.05, "rayon_exterieur_median_mm": 23.5,
                           "rayon_arret_median_mm": 23.4}}

    faux = {"fragment": "F", "pas_um": 173.0, "pas_au_dela": 16, "par_course": [
        course("a.json", 0.75, [arret(4.0, 12.0, 23.0, "plafond"),
                                arret(6.3, 18.7, 18.8, "plus rien a lire"),
                                arret(9.4, 17.0, 23.1, "plus rien a lire", reprend=2),
                                arret(10.5, 24.3, 24.3, "plus rien a lire"),
                                arret(13.3, 22.0, 22.1, "plus rien a lire", borne=True)]),
        course("b.json", 0.0, [arret(15.5, 23.9, 24.0, "plus rien a lire"),
                               arret(16.2, 21.9, 25.0, "plus rien a lire", reprend=5)])]}
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
        v("les arrêts sortis et les vides ont deux couleurs",
          pixels.count(SORTI) > 60 and pixels.count(VIDE) > 60)
        v("la bande à un pas de la diagonale est peinte", pixels.count(BANDE) > 300)
        v("le remplissage au-delà est peint", pixels.count(REMPLISSAGE) > 200)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        gx0, gy0, gx1, gy1 = cadres[0]
        v("tous les points tiennent dans leur cadre",
          [1 for x, y in points if not (gx0 <= x <= gx1 and gy0 <= y <= gy1)], [])
        v("le verdict de chaque course est écrit",
          sum(1 for _, _, t, _ in poses if "sortis du rouleau," in t), 2)
        # sondes
        for nom_, bris in (("sans course", lambda x: x.update(par_course=[])),
                           ("sans arrêt décidable", lambda x: [a["verdict"].update(decidable=False)
                                                               for c in x["par_course"] for a in c["arrets"]]),
                           ("porteur d'un message", lambda x: x.update(message="volume injoignable"))):
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
                   default=RACINE / "docs" / "mesures" / "ou_la_matiere_cesse_de_se_lire.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "135_la_surface_du_rouleau.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
