"""L'angle publié est-il celui des fibres ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le quart de tour DESSINÉ : les
crêtes choisies et la direction que la formule rend, côte à côte. En haut à droite, la fixture à
deux plis — l'angle absolu se répare par la conversion, l'écart entre les plis ne bouge pas. En bas
à gauche, la portée : combien d'angles absolus sont publiés et combien d'écarts bougent. En bas à
droite, l'invariance mesurée sur un balayage dense.

  uv run python src/figures/figure_langle_publie_est_il_celui_des_fibres.py \\
      --json docs/mesures/langle_publie_est_il_celui_des_fibres.json \\
      --sortie docs/images/172_langle_publie_est_il_celui_des_fibres.png
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
    """Le JSON de `langle_publie_est_il_celui_des_fibres.py`.

    ⚠⚠ Refuse une mesure dont la PORTÉE manque : le résultat de cette tranche a deux moitiés — le
    nom est faux, et aucun écart publié ne bouge — et une figure qui ne montrerait que la première
    ferait lire qu'il faut refaire les campagnes.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("le_motif", "la_fixture", "la_portee", "linvariance", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["le_motif"].get("lignes"):
        raise ValueError(f"{chemin} : le motif n'a aucune direction mesurée")
    if len(d["la_fixture"].get("par_pli") or []) != 2:
        raise ValueError(f"{chemin} : la fixture n'a pas ses deux plis")
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

    def brin(cx, cy, angle_deg, longueur, coul, largeur=2):
        """Un segment orienté, dessiné dans le repère de l'image du module.

        ⚠ L'angle se compte depuis l'axe 2 du bloc vers l'axe 1, donc vers le BAS à l'écran : la
        figure emploie la même convention que le module, sinon elle dessinerait sa propre.
        """
        th = math.radians(angle_deg)
        dx, dy = math.cos(th) * longueur / 2.0, math.sin(th) * longueur / 2.0
        art.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=coul, width=largeur)
        points.append((cx + dx, cy + dy))
        points.append((cx - dx, cy - dy))

    m, f, p = d["le_motif"], d["la_fixture"], d["la_portee"]
    inv, v = d["linvariance"], d["le_verdict"]

    ecrire(28, 20, "L'angle publié est-il celui des fibres ? — non, c'est leur perpendiculaire",
           gros, ENCRE)
    ecrire(28, 46, "Le nombre est juste et son nom est faux : la forme close donne le plus GRAND "
                   "vecteur propre, donc la direction du gradient", petit, GRIS)

    # ---- panneau 1 : le quart de tour, DESSINE
    x0, y0, pw, ph = 56, 122, 620, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "un motif dont les crêtes sont CHOISIES, et ce que la formule rend",
           moyen, ENCRE)
    ecrire(x0 + 150, y0 + 14, "les crêtes", petit, CONTRE)
    ecrire(x0 + 300, y0 + 14, "ce qui est rendu", petit, ALERTE)
    ecrire(x0 + 450, y0 + 14, "après conversion", petit, BON)
    for k, x in enumerate(m["lignes"]):
        cy = y0 + 66 + k * 52
        ecrire(x0 + 14, cy - 7, f"{_fr(x['cretes_deg'], 1)}°", 0, ENCRE)
        brin(x0 + 190, cy, x["cretes_deg"], 42, CONTRE)
        brin(x0 + 340, cy, x["angle_rendu_deg"], 42, ALERTE)
        brin(x0 + 490, cy, x["les_fibres_lues_deg"], 42, BON)
        ecrire(x0 + 530, cy - 7, f"écart {_fr(x['ecart_aux_cretes_deg'], 1)}°", 0, GRIS)
    marq = "★" if m["toutes_a_un_quart_de_tour"] else "✗"
    ecrire(x0 + 14, y0 + 236,
           f"{marq}  toutes à un quart de tour exact, et aucune sur ses crêtes", moyen,
           BON if m["toutes_a_un_quart_de_tour"] else ALERTE)
    ecrire(x0 + 14, y0 + 256,
           "⚠ ces quatre directions ne sont PAS discrétisées par la grille ;", petit, GRIS)
    ecrire(x0 + 14, y0 + 270,
           "les obliques le sont, donc le verdict ne les emploie pas.", petit, GRIS)

    # ---- panneau 2 : la fixture a deux plis
    x0, y0, pw, ph = 712, 122, 592, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la fixture à deux plis — la réponse est connue d'avance", moyen, ENCRE)
    ecrire(x0 + 200, y0 + 12, "écart brut", petit, ALERTE)
    ecrire(x0 + 330, y0 + 12, "après conversion", petit, BON)
    x_barre, barre_max = x0 + 200, 110
    vm = max(x["ecart_a_lattendu_deg"] for x in f["par_pli"]) or 1.0
    for k, x in enumerate(f["par_pli"]):
        yy = y0 + 40 + k * 30
        ecrire(x0 + 14, yy - 1,
               f"pli {x['pli']} · attendu {_fr(x['angle_attendu_deg'], 1)}°", 0, GRIS)
        w = (x["ecart_a_lattendu_deg"] / vm) * barre_max
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=ALERTE)
        points.append((x_barre + w, yy + 7))
        barres.append((x_barre + w, x_barre + barre_max))
        ecrire(x0 + 330, yy - 1,
               f"{_fr(x['ecart_a_lattendu_deg'], 2)}°  →  "
               f"{_fr(x['ecart_des_fibres_a_lattendu_deg'], 2)}°", 0, BON)
    ecrire(x0 + 14, y0 + 118, "l'ÉCART entre les deux plis, lui", moyen, ENCRE)
    for k, (lib, val) in enumerate((("avant conversion", f["ecart_entre_les_plis_deg"]),
                                    ("après conversion",
                                     f["ecart_entre_les_plis_apres_conversion_deg"]))):
        yy = y0 + 146 + k * 26
        ecrire(x0 + 14, yy, lib, 0, GRIS)
        ecrire(x0 + 200, yy, f"{_fr(val, 1)}°", 0, ENCRE)
    marq2 = "★" if f["lecart_ne_bouge_pas"] else "✗"
    ecrire(x0 + 14, y0 + 206, f"{marq2}  il ne bouge pas", moyen,
           BON if f["lecart_ne_bouge_pas"] else ALERTE)
    ecrire(x0 + 14, y0 + ph - 46,
           "★ les deux moitiés du résultat d'un coup : l'angle absolu est faux", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 30,
           "d'un quart de tour, et l'écart entre les plis est juste quand même.", petit, GRIS)

    # ---- panneau 3 : la portee
    x0, y0, pw, ph = 56, 474, 620, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la portée — ce qui est atteint, et ce qui ne l'est pas", moyen, ENCRE)
    ecrire(x0 + 290, y0 + 12, "segments", petit, GRIS)
    ecrire(x0 + 390, y0 + 12, "courbes", petit, GRIS)
    ecrire(x0 + 480, y0 + 12, "angles absolus", petit, ALERTE)
    for k, x in enumerate(p["fichiers"]):
        yy = y0 + 38 + k * 22
        ecrire(x0 + 14, yy, x["fichier"], 0, ENCRE)
        if not x["present"]:
            ecrire(x0 + 290, yy, "absent", 0, GRIS)
            continue
        ecrire(x0 + 290, yy, str(x["segments"]), 0, GRIS)
        ecrire(x0 + 390, yy, str(x["courbes"]), 0, GRIS)
        ecrire(x0 + 480, yy, str(x["angles_absolus"]), 0, ALERTE)
    ecrire(x0 + 14, y0 + 120,
           f"✗  {p['angles_absolus_publies']} angles absolus publiés sous le nom d'une "
           f"orientation de fibres", moyen, ALERTE)
    marq3 = "★" if p["la_bascule_ne_bouge_jamais"] else "✗"
    ecrire(x0 + 14, y0 + 148,
           f"{marq3}  et {p['bascules_inchangees']} bascules sur {p['bascules_relues']} sont "
           f"IDENTIQUES après le quart de tour", moyen,
           BON if p["la_bascule_ne_bouge_jamais"] else ALERTE)
    ecrire(x0 + 14, y0 + 184, "⚠⚠ la bascule est relue par la recette DU PRODUCTEUR — même",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 200, "plancher de cohérence, mêmes moitiés, même moyenne en angle",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 216, "double. Une variante comparerait deux définitions au lieu de",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 232, "deux lectures d'une seule.", petit, GRIS)

    # ---- panneau 4 : l'invariance
    x0, y0, pw, ph = 712, 474, 592, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'invariance — pourquoi aucun écart publié ne bouge", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 18, f"sur {inv['paires']} paires d'angles tirées :", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 48, "pire écart après le quart de tour", 0, GRIS)
    ecrire(x0 + 330, y0 + 48, _fr(inv["pire_ecart_apres_le_quart_de_tour"], 1), 0, ENCRE)
    marq4 = "★" if inv["lecart_est_invariant"] else "✗"
    ecrire(x0 + 14, y0 + 74, f"{marq4}  un écart est INVARIANT", moyen,
           BON if inv["lecart_est_invariant"] else ALERTE)
    ecrire(x0 + 14, y0 + 108, "la moyenne en angle double, elle, SUIT :", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 136, "avant", 0, GRIS)
    ecrire(x0 + 150, y0 + 136, f"{_fr(inv['moyenne_avant_deg'], 3)}°", 0, ENCRE)
    ecrire(x0 + 300, y0 + 136, "après", 0, GRIS)
    ecrire(x0 + 400, y0 + 136, f"{_fr(inv['moyenne_apres_deg'], 3)}°", 0, ENCRE)
    marq5 = "★" if inv["la_moyenne_tourne_du_meme_quart"] else "✗"
    ecrire(x0 + 14, y0 + 162, f"{marq5}  elle tourne du même quart, donc elle est ÉQUIVARIANTE",
           moyen, BON if inv["la_moyenne_tourne_du_meme_quart"] else ALERTE)
    ecrire(x0 + 14, y0 + 200, "⚠⚠ IL FAUT LES DEUX. Sans l'invariance, toutes les dispersions",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 216, "publiées bougeraient ; sans l'équivariance, les angles moyens",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 232, "se mélangeraient. C'est mesuré, jamais argumenté.", petit, GRIS)

    # ---- bande
    y = 768
    art.rectangle([56, y, L - 56, y + 134], fill=BANDE)
    cadres.append((56, y, L - 56, y + 134))
    ecrire(74, y + 12,
           f"✗  La forme close `½·atan2(2·Jxy, Jxx − Jyy)` donne le plus GRAND vecteur propre, "
           f"donc la direction du gradient : la PERPENDICULAIRE aux fibres.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"★★★★  Mesuré sur un motif qui ne doit rien à la fixture : quatre directions "
           f"choisies, quatre écarts de {_fr(m['ecart_median_deg'], 1)}° exactement.", moyen,
           ENCRE)
    ecrire(74, y + 64,
           f"★★★★  Et AUCUN écart publié ne bouge : {p['bascules_inchangees']} bascules sur "
           f"{p['bascules_relues']} sont identiques, et sur {inv['paires']} paires tirées le pire "
           f"écart vaut {_fr(inv['pire_ecart_apres_le_quart_de_tour'], 1)}.", moyen, ENCRE)
    ecrire(74, y + 90,
           f"✗  Ce qui est atteint est le nom, et il se compte : "
           f"{v['angles_absolus_a_relire']} angles absolus publiés décrivent la perpendiculaire "
           f"de ce qu'ils nomment.", moyen, ALERTE)
    ecrire(74, y + 114,
           "★  La valeur rendue n'est PAS corrigée : la tourner réparerait un nom en déplaçant "
           "des nombres déjà publiés.", moyen, ENCRE)

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

    # ⭐⭐⭐⭐ LES TROIS BRINS SONT DESSINES DEPUIS LA MESURE, PAS DEPUIS UN ANGLE ECRIT EN DUR.
    # Si l'angle rendu etait dessine a la place des cretes, le quart de tour disparaitrait de
    # l'image alors qu'il reste dans le texte — et c'est l'image qui porte l'argument.
    faux = copy.deepcopy(d)
    for x in faux["le_motif"]["lignes"]:
        x["angle_rendu_deg"] = x["cretes_deg"]
    _c, _p, _cd, pt1, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ les brins sont tracés depuis la mesure : changer l'angle rendu déplace le dessin",
      pt1 != points, f"{len(points)} points de référence")
    faux2 = copy.deepcopy(d)
    faux2["le_motif"]["ecart_median_deg"] = 71.7
    _c, p2, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐ l'écart médian de la bande est lu, pas supposé",
      any("71,7" in t for _x, _y, t, _f in p2) and not any("71,7" in t for t in tous))
    faux3 = copy.deepcopy(d)
    faux3["la_portee"]["angles_absolus_publies"] = 31313
    _c, p3, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le compte des angles absolus est lu, et c'est LUI qui chiffre le défaut",
      any("31313" in t for _x, _y, t, _f in p3))
    faux4 = copy.deepcopy(d)
    faux4["la_portee"]["bascules_inchangees"] = 51
    _c, p4, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ ... et le compte des bascules INCHANGÉES aussi, sinon la seconde moitié manquerait",
      any(" 51 " in t for _x, _y, t, _f in p4))
    faux5 = copy.deepcopy(d)
    faux5["la_fixture"]["lecart_ne_bouge_pas"] = False
    _c, p5, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐ le verdict de la fixture est LU, pas écrit en dur",
      any("✗  il ne bouge pas" in t for _x, _y, t, _f in p5)
      and not any("✗  il ne bouge pas" in t for t in tous))
    # ⚠ Une mesure incomplete est REFUSEE, jamais dessinee a moitie.
    creux = copy.deepcopy(d)
    creux["la_portee"] = {}
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure sans la portée est REFUSÉE, jamais dessinée à moitié", lire_ok)

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
                   / "langle_publie_est_il_celui_des_fibres.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "172_langle_publie_est_il_celui_des_fibres.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
