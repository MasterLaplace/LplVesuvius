"""Un ajustement décrit une frontière.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la relation : la part atteinte vaut
un jusqu'à une frontière et décroche dès deux. En haut à droite, le contrôle — une fenêtre sans
frontière rend elle aussi un, et c'est la bascule qui les sépare. En bas à gauche, la fenêtre utile
et le recouvrement qui la répare. En bas à droite, la fenêtre de la campagne, qui en porte trois.

  uv run python src/figures/figure_un_ajustement_decrit_une_frontiere.py \\
      --json docs/mesures/un_ajustement_decrit_une_frontiere.json \\
      --sortie docs/images/175_un_ajustement_decrit_une_frontiere.png
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
CONTRE = (92, 108, 150)


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{n}f}".rstrip("0").rstrip(".").replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `un_ajustement_decrit_une_frontiere.py`.

    ⚠⚠ Refuse une mesure sans le RECOUVREMENT : le résultat a une moitié qui réfute et une qui
    répare, et une figure qui n'en montrerait qu'une ferait lire soit que rien ne marche, soit
    qu'il n'y avait pas de problème.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("la_relation", "sans_frontiere", "la_fenetre_utile", "le_recouvrement",
                "la_campagne", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["la_relation"].get("lignes"):
        raise ValueError(f"{chemin} : la relation est vide")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    rel, vi = d["la_relation"], d["sans_frontiere"]
    ut, rc, ca, v = d["la_fenetre_utile"], d["le_recouvrement"], d["la_campagne"], d["le_verdict"]

    ecrire(28, 20, "Un ajustement décrit UNE frontière — la fenêtre de la campagne en porte trois",
           gros, ENCRE)
    ecrire(28, 46, "Deux segments ne décrivent pas trois blocs : le décrochage n'est pas un défaut "
                   "de la recette, c'est sa définition", petit, GRIS)

    # ---- panneau 1 : la relation
    x0, y0, pw, ph = 56, 122, 620, 296
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la part atteinte, par nombre de frontières dans la fenêtre", moyen, ENCRE)
    ecrire(x0 + 120, y0 + 12, "cellules", petit, GRIS)
    ecrire(x0 + 200, y0 + 12, "part médiane", petit, ENCRE)
    ecrire(x0 + 310, y0 + 12, "minimale", petit, GRIS)
    x_barre, barre_max = x0 + 400, pw - 470
    for k, x in enumerate(rel["lignes"]):
        yy = y0 + 38 + k * 26
        ok = x["toutes_les_parts_valent_un"]
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {x['frontieres']}", 0, BON if ok else ALERTE)
        ecrire(x0 + 120, yy, f"{x['cellules']}", 0, GRIS)
        ecrire(x0 + 200, yy, _fr(x["part_mediane"]), 0, ENCRE)
        ecrire(x0 + 310, yy, _fr(x["part_minimale"]), 0, GRIS)
        w = (float(x["part_mediane"] or 0.0)) * barre_max
        art.rectangle([x_barre, yy + 1, x_barre + max(w, 1), yy + 13], fill=BON if ok else ALERTE)
        points.append((x_barre + w, yy + 7))
        barres.append((x_barre + w, x_barre + barre_max))
    ecrire(x0 + 14, y0 + 228,
           f"★  jusqu'à UNE frontière la part vaut un ({_fr(v['part_mediane_a_une_frontiere'])}), "
           f"et dès deux elle décroche ({_fr(v['part_mediane_a_deux_frontieres'])})", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 254,
           f"⚠⚠ la relation ne porte que sur les fenêtres dont TOUTES les frontières sont",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 270,
           f"atteignables : {rel['cellules_ecartees_car_une_frontiere_est_hors_datteinte']} "
           f"cellules écartées, car une frontière trop près d'un bord fait chuter la part", petit,
           GRIS)

    # ---- panneau 2 : le controle
    x0, y0, pw, ph = 712, 122, 592, 296
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle — une fenêtre SANS frontière rend elle aussi un", moyen,
           ENCRE)
    for k, (lib, val) in enumerate((("cellules sans frontière", vi["cellules"]),
                                    ("part atteinte médiane", _fr(vi["part_mediane"])),
                                    ("bascule médiane", f"{_fr(vi['bascule_mediane_deg'], 1)}°"),
                                    ("elles lisent une frontière",
                                     f"{vi['combien_lisent_une_frontiere']}/{vi['cellules']}"))):
        yy = y0 + 24 + k * 26
        ecrire(x0 + 14, yy, lib, 0, GRIS)
        ecrire(x0 + 300, yy, str(val), 0, ENCRE)
    marq = "★" if vi["aucune_ne_lit_de_frontiere"] else "✗"
    ecrire(x0 + 14, y0 + 140,
           f"{marq}  une part de un ne suffit donc PAS : ce qui sépare", moyen,
           BON if vi["aucune_ne_lit_de_frontiere"] else ALERTE)
    ecrire(x0 + 14, y0 + 164, "   « trouvée » de « rien à trouver » est la BASCULE.", moyen,
           BON if vi["aucune_ne_lit_de_frontiere"] else ALERTE)
    ecrire(x0 + 14, y0 + 202, "⚠⚠ sans ce contrôle, « part atteinte un » se lirait comme", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 218, "une réussite partout où la matière est homogène — et une", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 234, "fenêtre homogène est exactement ce qu'un pli est.", petit, GRIS)
    ecrire(x0 + 14, y0 + 262,
           f"★ quand il y a UNE frontière atteignable, la coupe tombe dessus "
           f"{v['cellules_sur_une_frontiere_unique']} fois sur "
           f"{v['cellules_sur_une_frontiere_unique']}.", petit,
           BON if v["la_coupe_tombe_toujours_sur_la_frontiere_unique"] else ALERTE)

    # ---- panneau 3 : la fenetre utile et le recouvrement
    x0, y0, pw, ph = 56, 470, 620, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "une fenêtre seule, et deux fenêtres décalées d'une demi-longueur", moyen,
           ENCRE)
    ecrire(x0 + 150, y0 + 10, "une seule", petit, ALERTE)
    ecrire(x0 + 300, y0 + 10, "deux, décalées", petit, BON)
    par_couches = {x["couches"]: x for x in rc["lignes"]}
    for k, x in enumerate(ut["lignes"]):
        if k % 2:
            continue
        yy = y0 + 34 + (k // 2) * 22
        r2 = par_couches.get(x["couches"], {})
        ecrire(x0 + 14, yy, f"{x['couches']} c ({_fr(x['en_plis'], 2)} pli)", 0, ENCRE)
        ecrire(x0 + 150, yy, f"{x['lisent_une_frontiere']}/{x['decalages']}", 0, ALERTE)
        ok = r2.get("elles_lisent_partout")
        ecrire(x0 + 300, yy, f"{'★' if ok else '✗'} {r2.get('decalages_lus')}/"
                             f"{r2.get('decalages')}", 0, BON if ok else ALERTE)
    ecrire(x0 + 14, y0 + 206,
           f"✗  AUCUNE longueur seule ne lit à tous les décalages : {v['longueurs_utiles']}",
           moyen, ALERTE)
    ecrire(x0 + 14, y0 + 228,
           f"★  deux fenêtres couvrent tout dès {v['la_plus_courte_qui_couvre']} couches", moyen,
           BON)
    ecrire(x0 + 14, y0 + 250,
           "⚠ la demi-longueur est DÉRIVÉE : elle met le bord de l'une au centre de l'autre.",
           petit, GRIS)

    # ---- panneau 4 : la campagne
    x0, y0, pw, ph = 712, 470, 592, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la fenêtre de la campagne", moyen, ENCRE)
    for k, (lib, val) in enumerate((("couches", str(ca["couches"])),
                                    ("épaisseur", f"{_fr(ca['epaisseur_um'], 1)} µm"),
                                    ("en feuilles", _fr(ca["en_feuilles"])),
                                    ("en PLIS", _fr(ca["en_plis"])),
                                    ("frontières portées",
                                     f"{ca['frontieres_minimum']} à {ca['frontieres_maximum']}"),
                                    ("part atteinte médiane", _fr(ca["part_mediane"])),
                                    ("décalages qui lisent",
                                     f"{ca['lisent_une_frontiere']}/{ca['decalages']}"))):
        yy = y0 + 20 + k * 24
        ecrire(x0 + 14, yy, lib, 0, GRIS)
        ecrire(x0 + 260, yy, val, 0, ALERTE if lib == "en PLIS" else ENCRE)
    ecrire(x0 + 14, y0 + 196,
           "✗  elle est trop LONGUE pour deux segments, pas trop courte", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 222,
           "⚠⚠ c'est l'inverse de l'explication nº 3 laissée ouverte par", petit, GRIS)
    ecrire(x0 + 14, y0 + 238,
           "`14` §3, qui la disait plus courte qu'une épaisseur de feuille.", petit, GRIS)

    # ---- bande
    y = 754
    art.rectangle([56, y, L - 56, y + 148], fill=BANDE)
    cadres.append((56, y, L - 56, y + 148))
    ecrire(74, y + 12,
           "✗  L'hypothèse inscrite dans la porte est RÉFUTÉE d'entrée : la cohérence vaut un "
           "partout sur cette fixture, le profil d'intensité n'y est pour rien.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"★★★★  La cause est structurelle et elle est dans le nom : deux segments décrivent UNE "
           f"frontière. La part atteinte vaut {_fr(v['part_mediane_a_une_frontiere'])} jusqu'à une, "
           f"et {_fr(v['part_mediane_a_deux_frontieres'])} dès deux.", moyen, ENCRE)
    ecrire(74, y + 64,
           f"★★★★  Et la fenêtre de la campagne en porte {ca['frontieres_minimum']} à "
           f"{ca['frontieres_maximum']} : elle fait {_fr(ca['en_plis'])} PLIS. Elle est trop "
           f"longue pour ce modèle, pas trop courte pour porter une bascule.", moyen, ENCRE)
    ecrire(74, y + 90,
           f"★  Le remède est mesuré, pas espéré : deux fenêtres décalées d'une demi-longueur "
           f"lisent tous les décalages dès {v['la_plus_courte_qui_couvre']} couches, là où aucune "
           f"fenêtre seule n'y arrive.", moyen, ENCRE)
    ecrire(74, y + 116,
           "⚠⚠  Et une part atteinte de un ne suffit pas : une fenêtre sans frontière en rend une "
           "aussi. C'est la bascule qui sépare « trouvée » de « rien à trouver ».", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres = dessiner(d, sortie)
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
    v("⭐⭐⭐⭐ aucune barre ne déborde de son graphe, donc aucune ne recouvre son nombre",
      not debordantes, f"{len(barres)} barres, {debordantes}"[:180])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    faux = copy.deepcopy(d)
    faux["la_relation"]["lignes"][1]["part_mediane"] = 0.717
    _c, p2, _cd, pt2, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ la part atteinte est lue, et sa barre suit",
      any("0,717" in t for _x, _y, t, _f in p2) and pt2 != points)
    faux2 = copy.deepcopy(d)
    faux2["la_campagne"]["en_plis"] = 9.191
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ la fenêtre de la campagne est lue EN PLIS des deux côtés de la figure",
      sum(1 for _x, _y, t, _f in p3 if "9,191" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p3 if '9,191' in t)} mentions")
    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["la_plus_courte_qui_couvre"] = 71
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ la plus courte longueur qui couvre est lue des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if " 71 " in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if ' 71 ' in t)} mentions")
    faux4 = copy.deepcopy(d)
    faux4["sans_frontiere"]["bascule_mediane_deg"] = 31.3
    _c, p5, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐ la bascule du contrôle est lue, pas supposée",
      any("31,3" in t for _x, _y, t, _f in p5) and not any("31,3" in t for t in tous))
    faux5 = copy.deepcopy(d)
    faux5["le_recouvrement"]["lignes"][-1]["elles_lisent_partout"] = False
    _c, p6, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐ le verdict par longueur du recouvrement est lu ligne par ligne",
      sum(1 for _x, _y, t, _f in p6 if t.startswith("✗ "))
      > sum(1 for t in tous if t.startswith("✗ ")))
    creux = copy.deepcopy(d)
    creux["le_recouvrement"] = {}
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure sans le recouvrement est REFUSÉE, jamais dessinée à moitié", lire_ok)

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
                   default=RACINE / "docs" / "mesures"
                   / "un_ajustement_decrit_une_frontiere.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "175_un_ajustement_decrit_une_frontiere.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
