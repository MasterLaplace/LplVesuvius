"""De quoi une frontière du rouleau est-elle faite ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les deux espacements que la
matière peut porter et celui que le rouleau rend. En haut à droite, les deux étalons — s'ils ne se
séparaient pas, rien du reste ne voudrait dire quelque chose. En bas à gauche, les trois segments. En
bas à droite, la distribution des espacements mesurés.

  uv run python src/figures/figure_de_quoi_une_frontiere_est_elle_faite.py \\
      --json docs/mesures/de_quoi_une_frontiere_est_elle_faite.json \\
      --sortie docs/images/181_de_quoi_une_frontiere_est_elle_faite.png
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
    « 9 », le zéro des dizaines rogné comme s'il était décimal. Défaut payé par `177`.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `de_quoi_une_frontiere_est_elle_faite.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT LES DEUX ÉTALONS NE SE SÉPARENT PAS. C'est le contrôle qui décide si
    la lecture du rouleau veut dire quelque chose, et une première version de la mesure l'a EU à
    faux : dessiner un verdict par-dessus un contrôle en échec ferait lire une lecture nulle comme
    un résultat.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "les_etalons", "le_verdict", "les_deux_espacements"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("les_deux_etalons_se_separent"):
        raise ValueError(f"{chemin} : les deux étalons ne se séparent pas")
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
    pli, feuille = int(v["un_pli_en_couches"]), int(v["une_feuille_en_couches"])
    ecrire(28, 20, "De quoi une frontière du rouleau est-elle faite ? — espacée comme un pli, mais "
                   "plus serrée", gros, ENCRE)
    ecrire(28, 46, f"{d['creux_par_chunk']} creux par chunk · {v['chunks_lus']} chunks sur "
                   f"{v['segments']} segments · {d['permutations']} permutations · recouvrement "
                   f"{_fr(d['recouvrement_um_de_179'], 1)} µm (`179`) · bruit "
                   f"{_fr(d['bruit_apparie_de_180'], 0)} (`180`)", petit, GRIS)

    # ---- panneau 1 : les trois espacements sur une règle
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux espacements que la matière peut porter, et celui du rouleau",
           moyen, ENCRE)
    gx, gy, gw = x0 + 40, y0 + 42, 520
    haut = float(feuille) * 1.25
    art.line([gx, gy + 96, gx + gw, gy + 96], fill=TRAIT, width=1)
    for nom, val, coul, dy in (("une feuille", feuille, CONTRE, 0),
                               ("un pli", pli, BON, 30),
                               ("le rouleau", v["espacement_median_du_rouleau"], ALERTE, 60)):
        yy = gy + dy
        ecrire(x0 + 14, yy - 14, nom, 0, coul)
        barre(gx + 100, yy - 2, gw - 120, float(val or 0.0) / haut, 12, coul)
        ecrire(gx + 100 + (gw - 120) * float(val or 0.0) / haut + 6, yy - 4,
               f"{_fr(val, 1)} couches", 0, coul)
    ecrire(gx + 100, gy + 100, "0", 0, GRIS)
    ecrire(gx + 100 + (gw - 120) * float(feuille) / haut - 10, gy + 100, str(feuille), 0, GRIS)
    ecrire(x0 + 14, y0 + 178,
           f"★ {v['chunks_qui_designent_un_pli']} chunks sur {v['chunks_lus']} rangent leur "
           f"espacement du côté du PLI,", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 202,
           f"     {v['chunks_qui_designent_une_feuille']} du côté de la feuille.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 228,
           f"⚠ Mais {_fr(v['espacement_median_du_rouleau'], 1)} est plus COURT que {pli} : le "
           "rouleau porte plus de frontières qu'un pli n'en prédit.", petit, ALERTE)

    # ---- panneau 2 : les deux étalons
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux étalons — sans leur séparation, rien ne veut dire quelque chose",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "frontières", petit, GRIS)
    ecrire(x0 + 150, y0 + 10, "espacement", petit, ENCRE)
    ecrire(x0 + 262, y0 + 10, "deux creux+", petit, GRIS)
    ecrire(x0 + 380, y0 + 10, "désignent pli / feuille", petit, ENCRE)
    for k, e in enumerate(d["les_etalons"]):
        yy = y0 + 40 + k * 32
        quoi = "aux feuilles" if e["feuilles_independantes"] else "aux plis"
        coul = CONTRE if e["feuilles_independantes"] else BON
        ecrire(x0 + 14, yy, quoi, 0, coul)
        ecrire(x0 + 150, yy, f"{_fr(e['espacement_median'], 1)}", 0, ENCRE)
        ecrire(x0 + 262, yy, f"{e['cellules_a_deux_creux_ou_plus']}/{e['cellules']}", 0, GRIS)
        ecrire(x0 + 380, yy, f"{e['designent_un_pli']} / {e['designent_une_feuille']}", 0, coul)
        barre(x0 + 440, yy + 3, 120,
              float(max(e["designent_un_pli"], e["designent_une_feuille"]))
              / max(1, int(e["cellules"])), 10, coul)
    ecrire(x0 + 14, y0 + 120,
           "★ Les deux se séparent : l'étalon aux plis se range du côté du pli,", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 144, "celui aux feuilles du côté de la feuille.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 174,
           "⚠⚠⚠ Une première version ne les séparait PAS : la bande d'exclusion valait la",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 190,
           "largeur du creux, donc deux creux à quatre couches passaient tous les deux et", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 206,
           "l'étalon aux feuilles rendait quatre au lieu de soixante-douze.", petit, ALERTE)
    ecrire(x0 + 14, y0 + 228,
           f"⚠ Et une fenêtre de la campagne ne porte deux frontières de feuille que "
           f"{d['les_etalons'][1]['cellules_a_deux_creux_ou_plus']} fois sur "
           f"{d['les_etalons'][1]['cellules']}.", petit, GRIS)

    # ---- panneau 3 : les trois segments
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments du rouleau", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 170, y0 + 10, "creux", petit, ENCRE)
    ecrire(x0 + 250, y0 + 10, "espacement", petit, ENCRE)
    ecrire(x0 + 370, y0 + 10, "pli / feuille", petit, BON)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 38 + k * 44
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"{s['chunks_lus']}/{s['chunks_du_treillis']} chunks", 0, GRIS)
        ecrire(x0 + 170, yy, f"{s['creux_retenus']}", 0, ENCRE)
        ecrire(x0 + 170, yy + 16, f"2+ : {s['chunks_a_deux_creux_ou_plus']}", 0, GRIS)
        ecrire(x0 + 250, yy, f"{_fr(s['espacement_median'], 1)}", 0, ENCRE)
        ecrire(x0 + 370, yy, f"{s['designent_un_pli']} / {s['designent_une_feuille']}", 0, BON)
        barre(x0 + 440, yy + 3, 140,
              float(s["designent_un_pli"]) / max(1, int(s["chunks_lus"])), 10, BON)
    ecrire(x0 + 14, y0 + 180,
           f"★ {v['creux_retenus']} creux retenus, {v['chunks_a_deux_creux_ou_plus']} chunks sur "
           f"{v['chunks_lus']} en portent au moins deux —", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 204,
           f"     donc {v['espacements_mesures']} espacements mesurés.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 232,
           "⚠ Chaque rang est comparé au creux DE MÊME RANG des mélanges : le second creux", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 248,
           "est moins profond par construction, et le comparer au premier des mélanges le", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 260, "déclarerait toujours perdant.", petit, GRIS)

    # ---- panneau 4 : la distribution des espacements
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "tous les espacements mesurés sur le rouleau", moyen, ENCRE)
    espaces = sorted(e for s in lus for e in s["espacements"])
    hx, hy, hw, hh = x0 + 40, y0 + 30, 512, 130
    art.line([hx, hy + hh, hx + hw, hy + hh], fill=TRAIT, width=1)
    borne = max([feuille] + espaces) if espaces else feuille
    cases = 12
    pas = max(1.0, float(borne) / float(cases))
    compte = [0] * cases
    for e in espaces:
        compte[min(cases - 1, int(float(e) / pas))] += 1
    haut2 = max(1, max(compte))
    for i, n in enumerate(compte):
        bx = hx + hw * i / float(cases)
        bh = hh * float(n) / float(haut2)
        if bh > 0:
            art.rectangle([bx + 2, hy + hh - bh, bx + hw / cases - 2, hy + hh], fill=ALERTE)
        points.append((bx + hw / cases - 2, hy + hh))
    for val, coul, nom in ((pli, BON, "pli"), (feuille, CONTRE, "feuille")):
        xv = hx + hw * float(val) / float(borne)
        art.line([xv, hy, xv, hy + hh], fill=coul, width=2)
        points.append((xv, hy))
        ecrire(xv - 10, hy - 18, nom, 0, coul)
    ecrire(hx - 10, hy + hh + 6, "0", 0, GRIS)
    ecrire(hx + hw - 20, hy + hh + 6, str(int(borne)), 0, GRIS)
    ecrire(hx + hw / 2 - 30, hy + hh + 24, "couches entre deux creux", 0, GRIS)
    ecrire(x0 + 14, y0 + 204,
           f"✗ La médiane vaut {_fr(v['espacement_median_du_rouleau'], 1)} couches, entre les deux "
           f"repères et plus près du pli.", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 234,
           "⚠ Un espacement plus court qu'un pli veut dire des frontières qu'un", petit, GRIS)
    ecrire(x0 + 14, y0 + 250,
           "empilement régulier de plis ne prédit pas : rien ici ne dit lesquelles.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LES DEUX ÉTALONS SE SÉPARENT : aux plis {_fr(d['les_etalons'][0]['espacement_median'], 1)} "
           f"couches et {d['les_etalons'][0]['designent_un_pli']}/{d['les_etalons'][0]['cellules']} "
           f"du côté du pli ; aux feuilles "
           f"{_fr(d['les_etalons'][1]['espacement_median'], 1)} couches.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     Sans cette séparation la lecture du rouleau ne dirait rien, et une première "
           "version de cette mesure l'avait à faux.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"★  LE ROULEAU SE RANGE DU CÔTÉ DU PLI : {v['chunks_qui_designent_un_pli']} chunks sur "
           f"{v['chunks_lus']} contre {v['chunks_qui_designent_une_feuille']} du côté de la "
           "feuille. Ses frontières ne sont donc pas les interstices entre feuilles.", moyen, ENCRE)
    ecrire(78, y + 110,
           f"✗  MAIS L'ESPACEMENT MÉDIAN VAUT {_fr(v['espacement_median_du_rouleau'], 1)} COUCHES, "
           f"PLUS COURT QU'UN PLI ({pli}) : le rouleau porte plus de frontières qu'un empilement "
           "régulier n'en prédit.", moyen, ALERTE)
    ecrire(78, y + 138,
           "     Rien ici ne dit lesquelles. Une frontière de pli, une fissure et une "
           "sous-structure de la feuille creusent toutes, et ce lecteur ne les distingue pas.",
           moyen, ALERTE)
    ecrire(78, y + 170,
           f"⚠⚠ Et la fenêtre de la campagne est courte pour cette question : elle ne porte deux "
           f"frontières de FEUILLE que "
           f"{d['les_etalons'][1]['cellules_a_deux_creux_ou_plus']}/"
           f"{d['les_etalons'][1]['cellules']} fois, donc l'étalon qui les représente est le moins "
           "bien mesuré des deux.", petit, GRIS)
    ecrire(78, y + 192,
           "⚠ La bande d'exclusion se dérive de `178` et de `174` — deux frontières doivent laisser "
           "un segment entre elles — et une bande trop étroite comptait deux fois le même creux.",
           petit, GRIS)

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
      (_fr(90.0, 0), _fr(72.0, 1), _fr(23.5, 1)) == ("90", "72", "23,5"),
      f"{(_fr(90.0, 0), _fr(72.0, 1), _fr(23.5, 1))}")
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

    # ★★★★ L'ESPACEMENT DU ROULEAU EST LU DES DEUX COTES : c'est le ✗ de la tranche.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["espacement_median_du_rouleau"] = 41.5
    _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ l'espacement médian du rouleau est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p2 if "41,5" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p2 if '41,5' in t)} mentions")

    # ★★★★ LES DEUX REPERES SONT LUS, ET ILS PLACENT LES TRAITS DE L'HISTOGRAMME.
    faux2 = copy.deepcopy(d)
    faux2["le_verdict"]["un_pli_en_couches"] = 20
    _c, _p, _cd, pt3, _b, _t = dessiner(faux2, sortie)
    v("★★★★ le repère du pli est lu et il déplace son trait", pt3 != points)

    # ★★★★ LES ESPACEMENTS MESURES SONT DESSINES : un histogramme ecrit en dur serait un dessin.
    faux3 = copy.deepcopy(d)
    for s in faux3["les_segments"]:
        if s.get("decidable"):
            s["espacements"] = [70] * len(s["espacements"])
    _c, _p, _cd, pt4, _b, _t = dessiner(faux3, sortie)
    v("★★★★ l'histogramme vient des espacements mesurés", pt4 != points)

    # ★★★ LES DEUX ETALONS SONT LUS CHACUN : sans eux la bande affirme une separation.
    faux4 = copy.deepcopy(d)
    faux4["les_etalons"][1]["espacement_median"] = 61.5
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("★★★ l'espacement de l'étalon aux feuilles est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p5 if "61,5" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p5 if '61,5' in t)} mentions")

    # ★★★ LE COMPTE DES CHUNKS QUI DESIGNENT UN PLI EST LU, barre comprise.
    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["chunks_qui_designent_un_pli"] = 13
    _c, p6, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("★★★ le compte des chunks qui désignent un pli est lu",
      sum(1 for _x, _y, t, _f in p6 if "13 chunks sur" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p6 if '13 chunks sur' in t)} mentions")

    # ★★★★ UNE MESURE DONT LES ETALONS NE SE SEPARENT PAS EST REFUSEE.
    creux = copy.deepcopy(d)
    creux["le_verdict"]["les_deux_etalons_se_separent"] = False
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("★★★★ une mesure dont les étalons ne se séparent pas est REFUSÉE", lire_ok)
    del tous

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
                   default=RACINE / "docs" / "mesures"
                   / "de_quoi_une_frontiere_est_elle_faite.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "181_de_quoi_une_frontiere_est_elle_faite.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
