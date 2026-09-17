"""Le rouleau creuse-t-il ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les trois cohérences au même
niveau : le rouleau, une matière SANS frontière, une matière AVEC. En haut à droite, les trois
segments. En bas à gauche, les deux étalons et le bruit apparié. En bas à droite, ce que le creux
sépare — et c'est là que le ✗ se lit : un tiers de quart de tour.

  uv run python src/figures/figure_le_rouleau_creuse_t_il.py \\
      --json docs/mesures/le_rouleau_creuse_t_il.json \\
      --sortie docs/images/180_le_rouleau_creuse_t_il.png
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
    """Un nombre en français, sans zéros inutiles.

    ⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE : sans ce garde, `_fr(90, 0)` rend
    « 9 », le zéro des dizaines rogné comme s'il était décimal. Défaut payé par `177`, vu en
    REGARDANT l'image et par aucune garde.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_rouleau_creuse_t_il.py`.

    ⚠⚠ Refuse une mesure sans ses DEUX étalons ou sans ses profils. Dessiner ce que le rouleau rend
    sans la matière SANS frontière ferait lire « il creuse » comme un résultat, alors que sur une
    cohérence autocorrélée c'est l'étalon vide qui décide si battre ses mélanges veut dire quelque
    chose.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "les_etalons", "les_profils", "le_verdict", "la_fixture_de_179"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not any(int(e["plis"]) == 1 for e in d["les_etalons"]):
        raise ValueError(f"{chemin} : l'étalon sans frontière est absent")
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

    def segment(x1, y1, x2, y2, coul, largeur=2):
        art.line([x1, y1, x2, y2], fill=coul, width=largeur)
        points.append((x1, y1))
        points.append((x2, y2))
        traits.append((min(x1, x2), (y1 + y2) / 2.0, max(x1, x2)))

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    v = d["le_verdict"]
    ecrire(28, 20, "Le rouleau creuse-t-il ? — oui, partout, et plus creux qu'une frontière "
                   "construite", gros, ENCRE)
    ecrire(28, 46, f"{v['chunks_lus']} chunks sur {v['segments']} segments · treillis "
                   f"{d['cote_du_treillis']}×{d['cote_du_treillis']} · {d['permutations']} "
                   f"permutations · recouvrement de l'étalon "
                   f"{_fr(d['la_fixture_de_179']['recouvrement_um'], 1)} µm (`179`) · attendu par "
                   f"hasard {_fr(v['chunks_attendus_par_hasard'], 2)}", petit, GRIS)

    # ---- panneau 1 : les trois cohérences, au même niveau
    x0, y0, pw, ph = 56, 122, 620, 292
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les cohérences, au même niveau et au même recouvrement", moyen, ENCRE)
    gx, gy, gw, gh = x0 + 52, y0 + 20, 526, 128
    art.line([gx, gy, gx, gy + gh], fill=TRAIT, width=1)
    art.line([gx, gy + gh, gx + gw, gy + gh], fill=TRAIT, width=1)
    choisis = ([p for p in d["les_profils"] if p["quoi"] == "le rouleau"][:1]
               + [p for p in d["les_profils"] if p["quoi"] == "un seul pli"]
               + [p for p in d["les_profils"] if p["quoi"] == "deux plis"])
    couleurs = (ALERTE, CONTRE, BON)
    # ⚠⚠ L'AXE EST CALE SUR LES DONNEES, PAS SUR UN. Les trois coherences vivent sous un sixieme,
    # donc un axe de zero a un les ecrase toutes sur la meme ligne et le panneau cesse de montrer
    # ce qu'il annonce — le creux devient invisible. Vu en REGARDANT l'image, par aucune garde.
    haut = max([float(x) for p in choisis[:3] for x in p["coherences"]] or [1.0])
    haut = max(haut, 1e-6)
    for k, prof in enumerate(choisis[:3]):
        coul = couleurs[k]
        c = list(prof["coherences"])
        prec = None
        for i, val in enumerate(c):
            xi = gx + gw * float(i) / float(max(1, len(c) - 1))
            yi = gy + gh - gh * max(0.0, min(1.0, float(val) / haut))
            if prec is not None:
                segment(prec[0], prec[1], xi, yi, coul, 2)
            prec = (xi, yi)
        if prof.get("couche") is not None:
            xf = gx + gw * float(prof["couche"]) / float(max(1, len(c) - 1))
            art.line([xf, gy + gh, xf, gy + gh + 7], fill=coul, width=2)
            points.append((xf, gy + gh + 7))
    ecrire(gx - 34, gy - 6, _fr(haut, 2), 0, GRIS)
    ecrire(gx - 22, gy + gh - 8, "0", 0, GRIS)
    ecrire(gx, gy + gh + 26, "couche · ▲ creux lu", 0, GRIS)
    yy = y0 + 194
    for k, prof in enumerate(choisis[:3]):
        coul = couleurs[k]
        etat = (f"★ creux couche {prof['couche']}, profondeur {_fr(prof['profondeur'], 4)}"
                if prof["gagnant"] == "empilement" else "✗ aucun creux")
        nom = (f"{prof['quoi']} · {prof.get('segment', '')}".strip(" ·")
               if prof["quoi"] == "le rouleau"
               else f"{prof['quoi']} · bruit {_fr(prof.get('bruit'), 0)}")
        ecrire(x0 + 14, yy, f"— {nom}", 0, coul)
        ecrire(x0 + 250, yy, etat, 0, coul)
        yy += 18
    ecrire(x0 + 14, y0 + 248,
           "★ Une matière SANS frontière, au même niveau de cohérence, ne creuse pas :", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 264,
           "c'est elle qui rend la permutation suffisante ici, et non la permutation seule.", petit,
           GRIS)

    # ---- panneau 2 : les trois segments
    x0, y0, pw, ph = 712, 122, 592, 292
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments du rouleau", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 160, y0 + 10, "creusent", petit, ENCRE)
    ecrire(x0 + 330, y0 + 10, "profondeur", petit, GRIS)
    ecrire(x0 + 440, y0 + 10, "écart", petit, ALERTE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 36 + k * 44
        ecrire(x0 + 14, yy, f"{s['segment']}", 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"cohérence {_fr(s['coherence_mediane'], 4)}", 0, GRIS)
        ecrire(x0 + 160, yy, f"{s['chunks_qui_creusent']}/{s['chunks_lus']}", 0, BON)
        barre(x0 + 214, yy + 3, 100,
              float(s["chunks_qui_creusent"]) / max(1, int(s["chunks_lus"])), 10, BON)
        ecrire(x0 + 160, yy + 16, f"deux côtés dirigés {s['les_deux_cotes_sont_diriges']}", 0, GRIS)
        ecrire(x0 + 330, yy, _fr(s["profondeur_mediane"], 4), 0, ENCRE)
        ecrire(x0 + 330, yy + 16, f"largeur {s['largeur_mediane']}", 0, GRIS)
        ecrire(x0 + 440, yy, f"{_fr(s['ecart_median_deg'], 4)}°", 0, ALERTE)
    ecrire(x0 + 14, y0 + 190,
           f"★  les {v['chunks_lus']} chunks creusent, contre "
           f"{_fr(v['chunks_attendus_par_hasard'], 2)} attendus par hasard", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 216,
           f"     profondeur {_fr(v['profondeur_mediane_du_rouleau'], 4)} contre "
           f"{_fr(v['profondeur_de_letalon_avec_frontiere'], 4)} sur l'étalon à frontière", moyen,
           BON)
    ecrire(x0 + 14, y0 + 244,
           f"⚠ Aucun creux n'a ses DEUX côtés muets : ce ne sont pas des interstices vides,", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 260,
           f"il y a de la matière dirigée de part et d'autre dans "
           f"{v['creux_dont_les_deux_cotes_sont_diriges']} cas sur {v['chunks_qui_creusent']}.",
           petit, GRIS)

    # ---- panneau 3 : les deux étalons
    x0, y0, pw, ph = 56, 466, 620, 246
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux étalons, et le bruit apparié au rouleau", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "plis", petit, GRIS)
    ecrire(x0 + 70, y0 + 10, "bruit", petit, GRIS)
    ecrire(x0 + 140, y0 + 10, "cohérence", petit, ENCRE)
    ecrire(x0 + 240, y0 + 10, "creusent", petit, BON)
    ecrire(x0 + 390, y0 + 10, "profondeur", petit, GRIS)
    ecrire(x0 + 496, y0 + 10, "écart", petit, ALERTE)
    for k, e in enumerate(d["les_etalons"]):
        yy = y0 + 34 + k * 20
        apparie = e["bruit"] == v.get("le_bruit_apparie")
        coul = ENCRE if apparie else GRIS
        ecrire(x0 + 14, yy, f"{e['plis']}", 0, coul)
        ecrire(x0 + 70, yy, _fr(e["bruit"], 0), 0, coul)
        ecrire(x0 + 140, yy, _fr(e["coherence_mediane"], 4), 0, coul)
        ecrire(x0 + 240, yy, f"{e['chunks_qui_creusent']}/{e['cellules']}", 0,
               BON if e["chunks_qui_creusent"] else GRIS)
        barre(x0 + 292, yy + 3, 88,
              float(e["chunks_qui_creusent"]) / max(1, int(e["cellules"])), 9,
              BON if e["chunks_qui_creusent"] else GRIS)
        ecrire(x0 + 390, yy, _fr(e["profondeur_mediane"], 4), 0, coul)
        ecrire(x0 + 496, yy, _fr(e["ecart_median_deg"], 4), 0, ALERTE if apparie else GRIS)
        if apparie:
            ecrire(x0 + 560, yy, "★", 0, ENCRE)
    ecrire(x0 + 14, y0 + 172,
           f"★ Le bruit apparié est {_fr(v['le_bruit_apparie'], 0)} : la cohérence de l'étalon "
           f"vaut {_fr(v['coherence_mediane_de_letalon_sans_frontiere'], 4)}", petit, ENCRE)
    ecrire(x0 + 14, y0 + 188,
           f"contre {_fr(v['coherence_mediane_du_rouleau'], 4)} pour le rouleau. "
           "L'appariement est DÉRIVÉ, pas choisi.", petit, GRIS)
    ecrire(x0 + 14, y0 + 210,
           f"⚠ À ce bruit, un fond sans frontière creuse "
           f"{v['creusent_sur_letalon_sans_frontiere']}/{v['cellules_de_letalon']} "
           f"et une frontière {v['creusent_sur_letalon_avec_frontiere']}"
           f"/{v['cellules_de_letalon']}.", petit, GRIS)

    # ---- panneau 4 : ce que le creux sépare
    x0, y0, pw, ph = 712, 466, 592, 246
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que le creux sépare — et c'est là que ça bloque", moyen, ENCRE)
    lignes = (("l'étalon à frontière construite", v["ecart_de_letalon_avec_frontiere_deg"], BON),
              ("le rouleau, aux creux", v["ecart_median_aux_creux_deg"], ALERTE),
              ("le rouleau en moyenne (`176`)", v["la_bascule_mediane_de_176_deg"], CONTRE))
    for k, (nom, val, coul) in enumerate(lignes):
        yy = y0 + 24 + k * 30
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 230, yy, f"{_fr(val, 4)}°", 0, coul)
        barre(x0 + 292, yy + 2, 250, float(val or 0.0) / 90.0, 12, coul)
    ecrire(x0 + 292, y0 + 116, "0°", 0, GRIS)
    ecrire(x0 + 528, y0 + 116, "90°", 0, GRIS)
    ecrire(x0 + 14, y0 + 140,
           f"✗  l'écart aux creux vaut {_fr(v['lecart_aux_creux_vaut_letalon_fois'], 4)} fois "
           f"celui d'une frontière de pli", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 166,
           f"★  mais {_fr(v['lecart_aux_creux_vaut_la_bascule_de_176_fois'], 4)} fois la bascule "
           f"moyenne que `176` a publiée", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 196,
           "⚠ Le creux trouve donc bien l'endroit où l'orientation change le plus,", petit, GRIS)
    ecrire(x0 + 14, y0 + 212,
           "et cet endroit ne porte toujours pas un quart de tour.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LE ROULEAU CREUSE, ET PARTOUT : {v['chunks_qui_creusent']} chunks sur "
           f"{v['chunks_lus']}, contre {_fr(v['chunks_attendus_par_hasard'], 2)} attendus par "
           "hasard. La condition de matière que `179` posait est tenue.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     Profondeur {_fr(v['profondeur_mediane_du_rouleau'], 4)}, au-dessus de l'étalon à "
           f"frontière construite ({_fr(v['profondeur_de_letalon_avec_frontiere'], 4)}) et de la "
           f"borne de `179` ({_fr(v['profondeur_a_la_borne_de_179'], 4)}).", moyen, ENCRE)
    ecrire(78, y + 78,
           f"     Et une matière SANS frontière, au même niveau de cohérence, creuse "
           f"{v['creusent_sur_letalon_sans_frontiere']}/{v['cellules_de_letalon']} : "
           "battre ses mélanges veut donc dire quelque chose ici.", moyen, ENCRE)
    ecrire(78, y + 110,
           f"✗  MAIS CE QUE LE CREUX SÉPARE N'EST PAS UN QUART DE TOUR : "
           f"{_fr(v['ecart_median_aux_creux_deg'], 4)}° contre "
           f"{_fr(v['ecart_de_letalon_avec_frontiere_deg'], 4)}° sur l'étalon, soit "
           f"{_fr(v['lecart_aux_creux_vaut_letalon_fois'], 4)} fois.", moyen, ALERTE)
    ecrire(78, y + 138,
           f"     C'est pourtant {_fr(v['lecart_aux_creux_vaut_la_bascule_de_176_fois'], 4)} fois "
           f"la bascule médiane de {_fr(v['la_bascule_mediane_de_176_deg'], 4)}° que `176` "
           "publie : le creux désigne bien l'endroit où l'orientation change le plus.", moyen,
           ENCRE)
    ecrire(78, y + 170,
           f"⚠⚠⚠ Et aucun des {v['chunks_qui_creusent']} creux n'a ses deux côtés muets, donc ce ne "
           "sont pas des interstices vides — mais rien ici ne dit si un creux est une frontière de "
           "pli,", petit, GRIS)
    ecrire(78, y + 192,
           "un interstice partiellement rempli, ou une fissure. ⚠ Et la largeur lue sature le "
           "dernier barreau du balayage, pour le rouleau comme pour l'étalon : elle ne mesure "
           "donc pas la largeur du creux.", petit, GRIS)

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
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(90.0, 0), _fr(16.0, 0), _fr(27.363, 3)) == ("90", "16", "27,363"),
      f"{(_fr(90.0, 0), _fr(16.0, 0), _fr(27.363, 3))}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:200])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:200])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("★★★★ aucune barre ne déborde de son graphe", not debordantes,
      f"{len(barres)} barres, {debordantes}"[:200])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    def _boite(x, y, texte, f):
        b = f.getbbox(texte)
        return (x + b[0], y + b[1], x + b[2], y + b[3])

    traverses = [(t, round(x1), round(x2)) for x1, ty, x2 in traits
                 for (px, py, t, f) in poses
                 if (lambda bb: bb[0] < x2 and bb[2] > x1 and bb[1] <= ty <= bb[3])(
                     _boite(px, py, t, f))]
    v("★★★★ aucun trait ne traverse un texte", not traverses,
      f"{len(traits)} traits, {traverses}"[:200])

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ★★★★ LA COHERENCE DESSINEE VIENT DE LA MESURE, et celle du ROULEAU en particulier.
    faux = copy.deepcopy(d)
    for p in faux["les_profils"]:
        if p["quoi"] == "le rouleau":
            p["coherences"] = [0.5] * len(p["coherences"])
            break
    _c, _p, _cd, pt2, _b, _t = dessiner(faux, sortie)
    v("★★★★ la cohérence du rouleau dessinée est celle de la mesure", pt2 != points)

    # ★★★★ L'ETALON SANS FRONTIERE EST DESSINE : sans lui le panneau 1 ne montre qu'une moitie.
    faux1 = copy.deepcopy(d)
    for p in faux1["les_profils"]:
        if p["quoi"] == "un seul pli":
            p["coherences"] = [0.9] * len(p["coherences"])
            break
    _c, _p, _cd, pt3, _b, _t = dessiner(faux1, sortie)
    v("★★★★ l'étalon sans frontière est dessiné lui aussi", pt3 != points)

    # ★★★ L'AXE EST CALE SUR LES DONNEES : un axe fixe ecrase trois coherences qui vivent sous un
    # sixieme, et le creux devient invisible. Ce qui est asserte est que le HAUT de l'axe bouge.
    fauxa = copy.deepcopy(d)
    fauxa["les_profils"][0]["coherences"] = [0.61] * len(fauxa["les_profils"][0]["coherences"])
    _c, pa, _cd, _pt, _b, _t = dessiner(fauxa, sortie)
    v("★★★ l'axe des cohérences est calé sur les données",
      any(t == "0,61" for _x, _y, t, _f in pa) and not any(x == "0,61" for x in tous),
      str([t for _x, _y, t, _f in pa if "," in t][:3]))

    # ★★★★ L'ECART AUX CREUX EST LU DES DEUX COTES : c'est le ✗ de la tranche.
    faux2 = copy.deepcopy(d)
    faux2["le_verdict"]["ecart_median_aux_creux_deg"] = 41.375
    _c, p4, _cd, _pt, _b, _t = dessiner(faux2, sortie)
    v("★★★★ l'écart aux creux est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "41,375" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '41,375' in t)} mentions")

    # ★★★★ ET SON RAPPORT A L'ETALON AUSSI : « vingt-sept degres » ne dit rien sans lui.
    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["lecart_aux_creux_vaut_letalon_fois"] = 0.9137
    _c, p5, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("★★★★ le rapport de l'écart à l'étalon est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p5 if "0,9137" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p5 if '0,9137' in t)} mentions")

    # ★★★ LE COMPTE DE L'ETALON SANS FRONTIERE EST LU, barre comprise : c'est lui qui rend la
    # permutation suffisante, et l'ecrire en dur en ferait un dessin.
    faux4 = copy.deepcopy(d)
    for e in faux4["les_etalons"]:
        if int(e["plis"]) == 1 and e["bruit"] == d["le_verdict"]["le_bruit_apparie"]:
            e["chunks_qui_creusent"] = 9
    faux4["le_verdict"]["creusent_sur_letalon_sans_frontiere"] = 9
    _c, p6, _cd, _pt, b6, _t = dessiner(faux4, sortie)
    v("★★★ ce que creuse un fond sans frontière est lu, barre comprise",
      any("9/12" in t for _x, _y, t, _f in p6) and b6 != barres
      and not any("9/12" in x for x in tous))

    # ★★★ LE BRUIT APPARIE DESIGNE UNE LIGNE : sans lui, le tableau des etalons n'a pas de ligne
    # comparable au rouleau.
    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["le_bruit_apparie"] = 8.0
    _c, p7, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("★★★ le bruit apparié est lu et il déplace l'étoile",
      [t for _x, _y, t, _f in p7] != tous)

    creux = copy.deepcopy(d)
    creux["les_etalons"] = [e for e in creux["les_etalons"] if int(e["plis"]) != 1]
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure sans son étalon SANS frontière est REFUSÉE", lire_ok)

    dessiner(d, sortie)
    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {faits} checks)")
    else:
        print(f"ALL PASS (0 failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_rouleau_creuse_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "180_le_rouleau_creuse_t_il.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
