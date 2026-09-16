"""La recette posée sur le rouleau.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les trois segments et ce que la
recette y lit. En haut à droite, l'étalon — la même recette sur une matière dont la bascule est
construite. En bas à gauche, le contrôle par permutation : il y a bien de l'ordre en profondeur. En
bas à droite, l'amplitude DESSINÉE : six degrés contre un quart de tour.

  uv run python src/figures/figure_la_recette_posee_sur_le_rouleau.py \\
      --json docs/mesures/la_recette_posee_sur_le_rouleau.json \\
      --sortie docs/images/176_la_recette_posee_sur_le_rouleau.png
"""
from __future__ import annotations

import argparse
import json
import math
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
CONTRE = (92, 108, 150)


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{n}f}".rstrip("0").rstrip(".").replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_recette_posee_sur_le_rouleau.py`.

    ⚠⚠ Refuse une mesure sans l'ÉTALON : la bascule du rouleau n'a pas d'échelle sans celle que la
    même recette rend sur une matière dont la bascule est construite, et une figure qui n'en
    montrerait qu'une ferait lire six degrés comme un résultat.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "la_fixture", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["la_fixture"].get("bascule_mediane_deg"):
        raise ValueError(f"{chemin} : l'étalon n'a pas de bascule")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : {d['le_verdict'].get('raison', 'verdict indécidable')}")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    traits: list[tuple[float, float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def brin(cx, cy, angle_deg, longueur, coul, largeur=3):
        th = math.radians(angle_deg)
        dx, dy = math.cos(th) * longueur / 2.0, math.sin(th) * longueur / 2.0
        art.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=coul, width=largeur)
        points.append((cx + dx, cy + dy))
        points.append((cx - dx, cy - dy))
        traits.append((cx - abs(dx), cy, cx + abs(dx)))

    fx, v = d["la_fixture"], d["le_verdict"]

    ecrire(28, 20, "La recette posée sur le rouleau — il y a de l'ordre, et ce n'est pas une "
                   "bascule", gros, ENCRE)
    ecrire(28, 46, f"Fenêtres d'un pli ({d['largeur_en_couches']} couches) décalées d'une "
                   f"demi-largeur, {d['permutations']} permutations des couches par chunk",
           petit, GRIS)

    # ---- panneau 1 : les trois segments
    x0, y0, pw, ph = 56, 122, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les segments — treillis régulier, chunks du producteur", moyen, ENCRE)
    ecrire(x0 + 200, y0 + 12, "chunks", petit, GRIS)
    ecrire(x0 + 270, y0 + 12, "part", petit, ENCRE)
    ecrire(x0 + 340, y0 + 12, "mélanges", petit, GRIS)
    ecrire(x0 + 420, y0 + 12, "bascule", petit, ALERTE)
    ecrire(x0 + 500, y0 + 12, "lisent", petit, ENCRE)
    for k, s in enumerate(d["les_segments"]):
        yy = y0 + 38 + k * 26
        if not s.get("decidable"):
            ecrire(x0 + 14, yy, f"✗ {s['segment']}", 0, ALERTE)
            ecrire(x0 + 200, yy, str(s.get("raison"))[:34], 0, GRIS)
            continue
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 200, yy, f"{s['chunks_lus']}/{s['chunks_du_treillis']}", 0, GRIS)
        ecrire(x0 + 270, yy, _fr(s["part_mediane"]), 0, ENCRE)
        ecrire(x0 + 340, yy, _fr(s["part_mediane_des_permutations"]), 0, GRIS)
        ecrire(x0 + 420, yy, f"{_fr(s['bascule_mediane_deg'], 2)}°", 0, ALERTE)
        ecrire(x0 + 500, yy, f"{s['lisent_quelque_chose']}/{s['chunks_lus']}", 0, ENCRE)
    refus = d["les_segments"][0].get("refuses") or {}
    ecrire(x0 + 14, y0 + 134,
           f"⚠ les chunks refusés le sont par le filtre du producteur : {refus}", petit, GRIS)
    ecrire(x0 + 14, y0 + 158,
           "⚠⚠ un treillis régulier tombe souvent hors de la matière — un segment est une", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 174,
           "bande dans un volume rectangulaire. Les choisir ferait mesurer le choix.", petit, GRIS)
    ecrire(x0 + 14, y0 + 202,
           f"★  {v['chunks_lus']} chunks lus sur {v['segments']} segments", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 228,
           f"     part médiane {_fr(v['part_mediane_du_rouleau'])} contre "
           f"{_fr(v['part_mediane_des_permutations'])} au mélange", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 252,
           f"     témoin médian {_fr(v['temoin_median_du_rouleau_deg'], 2)}°", moyen, GRIS)

    # ---- panneau 2 : l'etalon
    x0, y0, pw, ph = 712, 122, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — la MÊME recette sur une bascule CONSTRUITE", moyen, ENCRE)
    for k, (lib, val) in enumerate((("cellules lisibles", f"{fx['lisibles']}/{fx['cellules']}"),
                                    ("part atteinte", _fr(fx["part_mediane"])),
                                    ("bascule", f"{_fr(fx['bascule_mediane_deg'], 2)}°"),
                                    ("témoin", f"{_fr(fx['temoin_median_deg'], 2)}°"),
                                    ("elles lisent",
                                     f"{fx['lisent_quelque_chose']}/{fx['lisibles']}"))):
        yy = y0 + 22 + k * 26
        ecrire(x0 + 14, yy, lib, 0, GRIS)
        ecrire(x0 + 260, yy, val, 0, ALERTE if lib == "bascule" else ENCRE)
    ecrire(x0 + 14, y0 + 166,
           "★  la recette PEUT répondre : sur une matière à deux plis", moyen, BON)
    ecrire(x0 + 14, y0 + 190,
           f"   elle rend un quart de tour à {fx['lisent_quelque_chose']} décalages sur "
           f"{fx['lisibles']}.", moyen, BON)
    ecrire(x0 + 14, y0 + 224,
           "⚠⚠ sans cet étalon, six degrés se liraient comme un résultat.", petit, GRIS)
    ecrire(x0 + 14, y0 + 244,
           "C'est lui qui donne une échelle, et il est mesuré par le même chemin.", petit, GRIS)

    # ---- panneau 3 : le controle par permutation
    x0, y0, pw, ph = 56, 450, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle — mélanger les couches détruit l'ordre en profondeur",
           moyen, ENCRE)
    x_barre, barre_max = x0 + 250, pw - 330
    for k, (lib, val, coul) in enumerate((
            ("dépassent toutes leurs permutations", v["depassent_toutes_les_permutations"], BON),
            ("dépassent leur témoin", v["depassent_le_temoin"], CONTRE),
            ("lisent quelque chose", v["lisent_quelque_chose"], BON),
            ("attendus PAR HASARD", v["chunks_attendus_par_hasard"], ALERTE))):
        yy = y0 + 26 + k * 32
        ecrire(x0 + 14, yy, lib, 0, GRIS)
        w = (float(val) / max(1.0, float(v["chunks_lus"]))) * barre_max
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
        points.append((x_barre + w, yy + 7))
        barres.append((x_barre + w, x_barre + barre_max))
        ecrire(x_barre + barre_max + 8, yy - 1, f"{_fr(val, 2)}", 0, coul)
    marq = "★" if v["il_y_a_de_lordre_en_profondeur"] else "✗"
    ecrire(x0 + 14, y0 + 168,
           f"{marq}  il y a de l'ordre en profondeur : {v['lisent_quelque_chose']} contre "
           f"{_fr(v['chunks_attendus_par_hasard'], 2)}", moyen,
           BON if v["il_y_a_de_lordre_en_profondeur"] else ALERTE)
    ecrire(x0 + 14, y0 + 200,
           f"⚠ avec {v['permutations']} permutations, un chunk les dépasse toutes par hasard une",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 216,
           f"fois sur {v['permutations'] + 1} — le compte attendu est publié à côté de l'observé.",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 238,
           "⚠⚠ la comparaison porte sur la PART ATTEINTE, jamais sur l'écart.", petit, GRIS)

    # ---- panneau 4 : l'amplitude, DESSINEE
    x0, y0, pw, ph = 712, 450, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'amplitude — six degrés contre un quart de tour", moyen, ENCRE)
    for k, (lib, ang, coul) in enumerate((
            ("le rouleau", v["bascule_mediane_du_rouleau_deg"], ALERTE),
            ("l'étalon", v["bascule_mediane_de_la_fixture_deg"], BON))):
        cy = y0 + 54 + k * 78
        ecrire(x0 + 14, cy - 8, lib, moyen, coul)
        art.line([x0 + 200, cy, x0 + 300, cy], fill=GRIS, width=2)
        traits.append((x0 + 200, cy, x0 + 300))
        brin(x0 + 350, cy, float(ang), 96, coul)
        ecrire(x0 + 430, cy - 8, f"{_fr(ang, 2)}°", moyen, coul)
    marq = "✗" if not v["son_amplitude_est_celle_dune_bascule"] else "★"
    ecrire(x0 + 14, y0 + 190,
           f"{marq}  le rouleau vaut ×{_fr(v['le_rouleau_vaut_la_fixture_fois'])} de l'étalon",
           moyen, ALERTE if not v["son_amplitude_est_celle_dune_bascule"] else BON)
    ecrire(x0 + 14, y0 + 218,
           "⚠⚠ une DÉRIVE n'est pas séparée d'une marche par un verdict — un ordre de", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 234,
           "six degrés à côté d'un témoin de cinq peut être une rotation lente.", petit, GRIS)

    # ---- bande
    y = 728
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(74, y + 14,
           f"★★★★  IL Y A DE L'ORDRE EN PROFONDEUR : {v['depassent_toutes_les_permutations']} "
           f"chunks sur {v['chunks_lus']} dépassent TOUTES leurs permutations, quand le hasard en "
           f"donnerait {_fr(v['chunks_attendus_par_hasard'], 2)}.", moyen, ENCRE)
    ecrire(74, y + 44,
           f"✗  MAIS CE N'EST PAS UNE BASCULE : {_fr(v['bascule_mediane_du_rouleau_deg'], 2)}° "
           f"contre {_fr(v['bascule_mediane_de_la_fixture_deg'], 2)}° sur une matière dont la "
           f"bascule est construite, soit "
           f"×{_fr(v['le_rouleau_vaut_la_fixture_fois'])}.", moyen, ALERTE)
    ecrire(74, y + 74,
           f"★  Et la recette PEUT répondre : elle rend le quart de tour à "
           f"{fx['lisent_quelque_chose']}/{fx['lisibles']} décalages sur l'étalon. Ce qui manque au "
           f"rouleau n'est donc pas l'instrument.", moyen, ENCRE)
    ecrire(74, y + 104,
           f"⚠⚠  Le témoin médian du rouleau vaut {_fr(v['temoin_median_du_rouleau_deg'], 2)}° pour "
           f"une bascule de {_fr(v['bascule_mediane_du_rouleau_deg'], 2)}° : l'ordre lu est à peine "
           f"au-dessus de ce qu'une part se contredit à elle-même.", moyen, ALERTE)
    ecrire(74, y + 134,
           "⚠⚠  Et la limite héritée tient : une DÉRIVE n'est pas séparée d'une marche par un "
           "verdict. Un ordre de six degrés peut être une rotation lente de l'orientation.",
           moyen, ALERTE)
    ecrire(74, y + 164,
           "★  Le contrôle est apparié au sens le plus fort : la même donnée, le même estimateur, "
           "seul l'ordre en profondeur détruit — et la comparaison porte sur", moyen, ENCRE)
    ecrire(74, y + 190,
           "     la PART ATTEINTE, jamais sur l'écart, parce que l'écart survit au mélange.",
           moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres, traits


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("⭐⭐⭐⭐ aucune barre ne déborde de son graphe", not debordantes,
      f"{len(barres)} barres, {debordantes}"[:180])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    def _boite(x, y, texte, f):
        b = f.getbbox(texte)
        return (x + b[0], y + b[1], x + b[2], y + b[3])

    traverses = [(t, round(x1), round(x2)) for x1, ty, x2 in traits
                 for (px, py, t, f) in poses
                 if (lambda b: b[0] < x2 and b[2] > x1 and b[1] <= ty <= b[3])(
                     _boite(px, py, t, f))]
    v("⭐⭐⭐⭐ aucun trait ne traverse un texte", not traverses,
      f"{len(traits)} traits, {traverses}"[:180])

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ⭐⭐⭐⭐ LES DEUX BASCULES SONT DESSINEES DEPUIS LA MESURE : c'est leur ECART qui porte
    # l'argument, et un angle ecrit en dur le supprimerait de l'image.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["bascule_mediane_du_rouleau_deg"] = 71.7
    _c, p2, _cd, pt2, _b, _t = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ la bascule du rouleau est lue, et son brin se déplace",
      any("71,7" in t for _x, _y, t, _f in p2) and pt2 != points)
    faux2 = copy.deepcopy(d)
    faux2["le_verdict"]["bascule_mediane_de_la_fixture_deg"] = 51.5
    _c, p3, _cd, pt3, _b, _t = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ ... et celle de l'étalon aussi, sinon il n'y aurait pas d'échelle",
      any("51,5" in t for _x, _y, t, _f in p3) and pt3 != points)
    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["chunks_attendus_par_hasard"] = 9.19
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le compte attendu par hasard est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "9,19" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '9,19' in t)} mentions")
    faux4 = copy.deepcopy(d)
    faux4["le_verdict"]["son_amplitude_est_celle_dune_bascule"] = True
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("⭐⭐⭐ le verdict d'amplitude est LU, pas écrit en dur",
      sum(1 for _x, _y, t, _f in p5 if t.startswith("★  le rouleau vaut")) == 1
      and not any(t.startswith("★  le rouleau vaut") for t in tous))
    faux5 = copy.deepcopy(d)
    faux5["la_fixture"]["lisent_quelque_chose"] = 3
    _c, p6, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("⭐⭐⭐ ce que l'étalon lit est compté des DEUX côtés",
      sum(1 for _x, _y, t, _f in p6 if "3/12" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p6 if '3/12' in t)} mentions")
    creux = copy.deepcopy(d)
    creux["la_fixture"] = {}
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure sans l'étalon est REFUSÉE, jamais dessinée à moitié", lire_ok)

    dessiner(d, sortie)
    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {faits} checks)")
    else:
        print(f"ALL PASS (0 failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_recette_posee_sur_le_rouleau.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "176_la_recette_posee_sur_le_rouleau.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
