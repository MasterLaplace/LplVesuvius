"""Le déroulage de la phase suppose ce qu'on voudrait lui demander.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la borne : le repliement ne PEUT
pas rendre un pas au-delà d'une demi-feuille, quand le déroulage exact en rend de vingt. En haut à
droite, l'arbitre — un chemin échantillonné jusqu'à ce qu'aucun sous-pas ne soit replié. En bas à
gauche, la portée : zéro sur la spirale nue, presque tout sur la matière du rouleau. En bas à droite,
ce que la correction déplace aux comptes déjà publiés — et ce qu'elle ne déplace pas.

  uv run python src/figures/figure_le_deroulage_suppose_ce_quon_lui_demande.py \\
      --json docs/mesures/le_deroulage_suppose_ce_quon_lui_demande.json \\
      --sortie docs/images/159_le_deroulage_suppose_ce_quon_lui_demande.png
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
TEMOIN = (150, 152, 156)
LA_DEMI_FEUILLE = 0.5


def lire(chemin: Path) -> dict:
    """Le JSON de `le_deroulage_suppose_ce_quon_lui_demande.py`.

    ⚠⚠ Refuse une mesure sans arbitre : les trois autres panneaux se lisent contre lui, et une
    figure qui montrerait la portée d'un défaut sans dire qui a tranché ressemble exactement à une
    figure qui le dirait.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not d.get("arbitre", {}).get("decidable"):
        raise ValueError(f"{chemin} : l'arbitre n'a rien tranché")
    if not j.get("par_regle"):
        raise ValueError(f"{chemin} : aucune règle jugée")
    return d


def _bref(nom: str) -> str:
    return (nom.replace("la pince de ", "").replace("la pince avec rejet", "pince + rejet")
            .replace("une mâchoire avec rejet", "seule + rejet"))


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr"))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1360, 940
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    j, a = d["juger"], d["arbitre"]
    reg = j["par_regle"]
    non_tranches = int(a["litiges"]) - int(a["pour_lexact"]) - int(a["pour_le_replie"])

    ecrire(28, 20, "Le déroulage de la phase suppose ce qu'on voudrait lui demander", gros, ENCRE)
    ecrire(28, 46, f"`d - round(d)` choisit l'entier qui rend chaque pas le plus PETIT, donc il "
                   f"borne TOUT pas à une demi-feuille — et « un pas dépasse-t-il une "
                   f"demi-feuille ? » reçoit non par construction", petit, GRIS)

    # ---- panneau 1 : la borne
    x0, y0, pw, ph = 56, 122, 620, 296
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le plus grand pas, replié contre exact", moyen, ENCRE)
    vmax = max(x["plus_grand_pas_en_feuilles"] for x in reg) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 150
    barre_max = pw - 290
    for k, x in enumerate(reg):
        yy = y0 + 34 + k * 62
        ecrire(x_nom, yy + 10, _bref(x["regle"]), petit, ENCRE)
        wd = (LA_DEMI_FEUILLE / vmax) * barre_max
        art.rectangle([x_barre, yy, x_barre + max(wd, 1), yy + 14], fill=TEMOIN)
        points.append((x_barre + wd, yy + 7))
        we = (x["plus_grand_pas_en_feuilles"] / vmax) * barre_max
        art.rectangle([x_barre, yy + 18, x_barre + max(we, 1), yy + 32], fill=ALERTE)
        points.append((x_barre + we, yy + 25))
        ecrire(x_barre + barre_max + 10, yy + 1, "0,5 au plus", petit, TEMOIN)
        ecrire(x_barre + barre_max + 10, yy + 19,
               f"{x['plus_grand_pas_en_feuilles']:g}", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 46,
           "gris : tout ce que le repliement PEUT rendre · ambre : le pas réellement franchi",
           petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 30,
           "la borne du gris n'est pas une mesure, c'est une propriété de l'opération", petit,
           ENCRE)
    ecrire(x0 + 12, y0 + ph - 14,
           "l'entier se LIT sur l'angle elliptique de la fixture, seule coupure de la phase",
           petit, ENCRE)

    # ---- panneau 2 : l'arbitre
    x0, y0, pw, ph = 712, 122, 592, 296
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'arbitre : un chemin qui ne choisit aucun entier", moyen, ENCRE)
    tot = int(a["litiges"]) or 1
    x_barre, barre_max = x0 + 150, pw - 300
    for k, (nom, val, coul) in enumerate((("pour l'exact", int(a["pour_lexact"]), BON),
                                          ("pour le replié", int(a["pour_le_replie"]), ALERTE),
                                          ("non tranchés", non_tranches, GRIS))):
        yy = y0 + 40 + k * 46
        w = (val / tot) * barre_max
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 18], fill=coul)
        points.append((x_barre + w, yy + 9))
        ecrire(x0 + 12, yy + 3, nom, petit, ENCRE)
        ecrire(x_barre + barre_max + 10, yy + 3, f"{val}", petit, coul)
    ecrire(x0 + 12, y0 + 16, f"{a['litiges']} pas litigieux, sur {len(a['cas'])} marches",
           petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 78,
           "il double l'échantillonnage jusqu'à ce qu'AUCUN sous-pas ne soit replié :", petit,
           ENCRE)
    ecrire(x0 + 12, y0 + ph - 62,
           "une somme dont aucun terme n'a été choisi ne suppose rien.", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 40,
           "⚠ « deux échantillonnages s'accordent » serait FAUX : deux trop grossiers", petit,
           ALERTE)
    ecrire(x0 + 12, y0 + ph - 24,
           "replient le même sous-pas et s'accordent sur un nombre faux.", petit, ALERTE)

    # ---- panneau 3 : la portee
    x0, y0, pw, ph = 56, 474, 620, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "où le déroulage se trompe — toutes règles confondues", moyen, ENCRE)
    par = {}
    for c in d["portee"]["cases"]:
        e = par.setdefault(c["nom"], [0, 0, 0])
        e[0] += c["marches_touchees"]
        e[1] += c["decidables"]
        e[2] += c["pas_replies_a_tort"]
    noms = list(par)
    x_nom, x_barre = x0 + 12, x0 + 160
    barre_max = pw - 320
    for k, nom in enumerate(noms):
        t, dec, ps = par[nom]
        yy = y0 + 28 + k * 42
        w = (t / max(dec, 1)) * barre_max
        coul = BON if t == 0 else ALERTE
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 15], fill=coul)
        points.append((x_barre + w, yy + 7))
        ecrire(x_nom, yy + 2, _court(nom), petit, ENCRE)
        ecrire(x_barre + barre_max + 10, yy + 2, f"{t}/{dec}  ·  {ps} pas", petit, coul)
    ecrire(x0 + 12, y0 + ph - 46,
           "la barre : la part des marches dont au moins un pas est replié à tort", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 30,
           f"la seule matière qu'aucune marche touchée n'atteint : {j['matieres_intactes']}",
           petit, BON)
    ecrire(x0 + 12, y0 + ph - 14,
           "et les deux qui portent les DEUX causes sont touchées dès le bruit nul", petit,
           ALERTE)

    # ---- panneau 4 : ce que la correction deplace
    x0, y0, pw, ph = 712, 474, 592, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que la correction déplace aux comptes publiés", moyen, ENCRE)
    rmax = max(max(x["reussites_repliees"], x["reussites_exactes"]) for x in reg) or 1
    x_nom, x_barre = x0 + 12, x0 + 130
    barre_max = pw - 270
    for k, x in enumerate(reg):
        yy = y0 + 30 + k * 66
        ecrire(x_nom, yy + 12, _bref(x["regle"]), petit, ENCRE)
        for dec, val, coul in ((0, x["reussites_repliees"], TEMOIN),
                               (18, x["reussites_exactes"],
                                BON if x["la_correction_deplace"] == 0 else ALERTE)):
            w = (val / rmax) * barre_max
            art.rectangle([x_barre, yy + dec, x_barre + max(w, 1), yy + dec + 15], fill=coul)
            points.append((x_barre + w, yy + dec + 7))
        ecrire(x_barre + barre_max + 10, yy + 1, f"{x['reussites_repliees']} replié", petit,
               TEMOIN)
        ecrire(x_barre + barre_max + 10, yy + 19,
               f"{x['reussites_exactes']} exact  {x['la_correction_deplace']:+d}", petit,
               BON if x["la_correction_deplace"] == 0 else ALERTE)
    ecrire(x0 + 12, y0 + ph - 46,
           f"la barre de `144` ne bouge PAS, malgré {reg[0]['marches_touchees']} marches touchées "
           f"et {reg[0]['pas_replies_a_tort']} pas", petit, BON)
    ecrire(x0 + 12, y0 + ph - 30,
           "un pas replié à tort décale d'une feuille ENTIÈRE : il fait sortir de la bande",
           petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 14,
           "« même feuille » bien plus facilement qu'il n'y fait entrer.", petit, ENCRE)

    # ---- bande de conclusion
    y = 782
    art.rectangle([56, y, L - 56, y + 122], fill=BANDE)
    cadres.append((56, y, L - 56, y + 122))
    ecrire(74, y + 12,
           f"★★★★  Le chemin tranche : {a['pour_lexact']} pas litigieux sur {a['litiges']} pour le "
           f"déroulage EXACT, {a['pour_le_replie']} pour le replié, {non_tranches} non tranchés.",
           moyen, BON)
    ecrire(74, y + 38,
           f"★★★★  La barre de `144` tient : {reg[0]['reussites_repliees']} contre "
           f"{reg[0]['reussites_exactes']}, alors que {reg[0]['marches_touchees']} de ses "
           f"{reg[0]['decidables']} marches sont touchées.", moyen, ENCRE)
    ecrire(74, y + 64,
           f"✗  Mais les gains du rejet fondent — {reg[1]['reussites_repliees']} → "
           f"{reg[1]['reussites_exactes']} — et une mâchoire seule passe DERRIÈRE la pince : "
           f"{reg[2]['reussites_repliees']} → {reg[2]['reussites_exactes']}.", moyen, ALERTE)
    ecrire(74, y + 90,
           "⚠  L'instrument est exact là où la matière est simple et faux là où elle est dure, "
           "c'est-à-dire là où vivent toutes les questions ouvertes.", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 940), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["arbitre"]["pour_le_replie"] = 4444
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer ce que l'arbitre donne au replié change ce que la bande DIT",
      any("4444" in t for _x, _y, t, _f in p2)
      and not any("4444" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["par_regle"][0]["reussites_exactes"] = 6666
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et la barre de `144` est LUE, pas supposée",
      any("6666" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    for c in faux3["portee"]["cases"]:
        c["marches_touchees"] = 0
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐ ... et la portée aussi", any("0/" in t for _x, _y, t, _f in p4))

    sans = copy.deepcopy(d)
    sans["arbitre"]["decidable"] = False
    tmp = sortie.parent / "_sans_arbitre_159.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans arbitre est REFUSÉE, jamais dessinée à moitié", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "le_deroulage_suppose_ce_quon_lui_demande.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "159_le_deroulage_suppose_ce_quon_lui_demande.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
