"""Jusqu'où suit-on une fibre ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le suiveur suit : sur des crêtes
construites il va dix fois plus loin le long qu'en travers. En haut à droite, le rouleau et ses deux
contrôles. En bas à gauche, les segments. En bas à droite, la seule comparaison qui compte pour le
graal — la longueur atteinte contre le pas entre deux feuilles.

  uv run python src/figures/figure_jusquou_suit_on_une_fibre.py \\
      --json docs/mesures/jusquou_suit_on_une_fibre.json \\
      --sortie docs/images/185_jusquou_suit_on_une_fibre.png
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
    « 9 ». Défaut payé par `177`.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `jusquou_suit_on_une_fibre.py`.

    ⚠⚠ Refuse une mesure dont l'étalon ne montre pas que le suiveur suit : une longueur mesurée par
    un suiveur qui ne suit pas est un nombre sous un nom qui promet autre chose, et une première
    version du suiveur allait aussi loin en travers que le long.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "letalon", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("le_suiveur_suit"):
        raise ValueError(f"{chemin} : l'étalon ne montre pas que le suiveur suit")
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

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    v, e = d["le_verdict"], d["letalon"]
    ecrire(28, 20, "Jusqu'où suit-on une fibre ? — un demi-pas de feuille, et le critère du prix "
                   "en demande un", gros, ENCRE)
    ecrire(28, 46, f"{d['departs_par_couche']} départs par couche · "
                   f"{d['couches_par_chunk']} couches par chunk · {v['chunks_lus']} chunks · "
                   f"{v['couches_lues']} couches · plafond {d['plafond_de_pas']} pas · voxel "
                   f"{_fr(d['voxel_um'], 1)} µm", petit, GRIS)

    # ---- panneau 1 : l'étalon
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — le suiveur suit", moyen, ENCRE)
    haut = max(float(e["le_long"] or 1.0), float(v["le_long_en_pas"] or 1.0)) * 1.15
    for k, (nom, val, coul) in enumerate((("le long des crêtes", e["le_long"], BON),
                                          ("en travers", e["en_travers"], CONTRE),
                                          ("sur l'image mélangée", e["melangee"], GRIS))):
        yy = y0 + 28 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 210, yy, _fr(val, 1), 0, coul)
        barre(x0 + 260, yy + 2, 320, float(val or 0.0) / haut, 12, coul)
    ecrire(x0 + 14, y0 + 150, "par angle de crête construite :", petit, GRIS)
    for k, ligne in enumerate(e["lignes"]):
        yy = y0 + 172 + k * 18
        ecrire(x0 + 24, yy, f"{_fr(ligne['angle_des_cretes_deg'], 0)}° · le long "
                            f"{_fr(ligne['le_long']['pas_median'], 1)} · en travers "
                            f"{_fr(ligne['en_travers']['pas_median'], 1)} · mélangée "
                            f"{_fr(ligne['melangee']['pas_median'], 1)}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 234,
           "⚠⚠⚠ Une première version allait aussi loin en travers que le long : son critère", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 250,
           "d'arrêt était vacant dans cette direction-là. L'étalon l'a montré nu.", petit, ALERTE)

    # ---- panneau 2 : le rouleau
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le rouleau, et ses deux contrôles", moyen, ENCRE)
    for k, (nom, val, coul) in enumerate(
            (("le long des fibres", v["le_long_en_pas"], ALERTE),
             ("en travers", v["en_travers_en_pas"], CONTRE),
             ("sur l'image mélangée", v["melangee_en_pas"], GRIS))):
        yy = y0 + 28 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 200, yy, f"{_fr(val, 2)} pas", 0, coul)
        barre(x0 + 270, yy + 2, 290, float(val or 0.0) / haut, 12, coul)
    ecrire(x0 + 14, y0 + 148,
           f"★ Le rouleau porte des crêtes suivables : {_fr(v['le_long_en_pas'], 2)} pas le long",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 172,
           f"     contre {_fr(v['en_travers_en_pas'], 2)} en travers et "
           f"{_fr(v['melangee_en_pas'], 2)} sur du mélange.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 204,
           "⚠⚠ On suit un INDIVIDU, pas une fréquence : une autocorrélation rendrait la", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 220,
           "même chose sur deux morceaux qui ne sont pas la même fibre — objection de", petit, GRIS)
    ecrire(x0 + 14, y0 + 236, "`128`, et c'est elle qui décide de la forme de la mesure.", petit,
           GRIS)

    # ---- panneau 3 : les segments
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 180, y0 + 10, "le long", petit, ALERTE)
    ecrire(x0 + 290, y0 + 10, "en travers", petit, CONTRE)
    ecrire(x0 + 400, y0 + 10, "mélangée", petit, GRIS)
    ecrire(x0 + 500, y0 + 10, "au max", petit, ENCRE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 38 + k * 40
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"{s['chunks_lus']} chunks · {s['couches_lues']} couches", 0,
               GRIS)
        ecrire(x0 + 180, yy, _fr(s["le_long"], 2), 0, ALERTE)
        barre(x0 + 180, yy + 18, 90, float(s["le_long"] or 0.0) / haut, 9, ALERTE)
        ecrire(x0 + 290, yy, _fr(s["en_travers"], 2), 0, CONTRE)
        barre(x0 + 290, yy + 18, 90, float(s["en_travers"] or 0.0) / haut, 9, CONTRE)
        ecrire(x0 + 400, yy, _fr(s["melangee"], 2), 0, GRIS)
        ecrire(x0 + 500, yy, _fr(s["le_long_maximal"], 1), 0, ENCRE)
    ecrire(x0 + 14, y0 + 172,
           "⚠ Les départs sont les maximums de cases régulières : le choix est fait par", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 188,
           "la MATIÈRE et la répartition par la grille, jamais par nous.", petit, GRIS)
    ecrire(x0 + 14, y0 + 212,
           "⚠⚠ Le plancher de la marche est la MÉDIANE de l'image elle-même, donc il", petit, GRIS)
    ecrire(x0 + 14, y0 + 228,
           "vient de la matière lue et non d'un seuil choisi. Et le plafond de pas est", petit, GRIS)
    ecrire(x0 + 14, y0 + 244,
           "dérivé : il doit permettre de FRANCHIR une feuille, sinon le verdict serait", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 260, "le nôtre et non celui de la matière.", petit, GRIS)

    # ---- panneau 4 : la comparaison qui compte
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la seule comparaison qui compte pour le graal", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 20,
           "Le prix demande de suivre les fibres SANS SAUTER DE FEUILLE. La longueur", petit, ENCRE)
    ecrire(x0 + 14, y0 + 36,
           "suivable doit donc franchir la distance entre deux feuilles.", petit, ENCRE)
    hautum = max(float(v["le_pas_entre_deux_feuilles_um"]),
                 float(v["le_long_en_um"] or 0.0)) * 1.15
    for k, (nom, val, coul) in enumerate(
            (("ce qu'on suit", v["le_long_en_um"], ALERTE),
             ("le pas entre deux feuilles", v["le_pas_entre_deux_feuilles_um"], BON))):
        yy = y0 + 70 + k * 36
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 214, yy, f"{_fr(val, 1)} µm", 0, coul)
        barre(x0 + 290, yy + 2, 270, float(val or 0.0) / hautum, 14, coul)
    ecrire(x0 + 14, y0 + 158,
           f"✗ {_fr(v['il_vaut_le_pas_entre_deux_feuilles_fois'], 4)} fois — un peu moins",
           moyen, ALERTE)
    ecrire(x0 + 14, y0 + 182, "de la moitié.", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 212,
           f"⚠ La plus longue crête suivie atteint pourtant "
           f"{_fr(max((s['le_long_maximal'] or 0) for s in lus), 1)} pas :", petit, GRIS)
    ecrire(x0 + 14, y0 + 228,
           "certaines fibres franchissent une feuille, la médiane non.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           "★  LE CRITÈRE DU PRIX EST ENFIN MESURÉ. `14` §8 le nomme depuis le début — la "
           "continuité LE LONG D'UNE LIGNE — et rien ne l'avait mesuré.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"★  LE SUIVEUR SUIT : sur des crêtes construites, {_fr(e['le_long'], 1)} pas le long "
           f"contre {_fr(e['en_travers'], 1)} en travers et {_fr(e['melangee'], 1)} sur du "
           "mélange, à trois angles.", moyen, ENCRE)
    ecrire(78, y + 74,
           f"★  ET LE ROULEAU PORTE DES CRÊTES SUIVABLES : {_fr(v['le_long_en_pas'], 2)} pas le "
           f"long contre {_fr(v['en_travers_en_pas'], 2)} en travers et "
           f"{_fr(v['melangee_en_pas'], 2)} sur du mélange.", moyen, ENCRE)
    ecrire(78, y + 106,
           f"✗  MAIS ÇA FAIT {_fr(v['le_long_en_um'], 1)} µm POUR UN PAS DE FEUILLE DE "
           f"{_fr(v['le_pas_entre_deux_feuilles_um'], 0)} µm, soit "
           f"{_fr(v['il_vaut_le_pas_entre_deux_feuilles_fois'], 4)} fois : on ne franchit pas une "
           "feuille.", moyen, ALERTE)
    ecrire(78, y + 134,
           "     Suivre une fibre ne suffit donc pas, aujourd'hui, à garantir qu'on ne saute pas "
           "de feuille — c'est le critère même du prix, et il n'est pas atteint.", moyen, ALERTE)
    ecrire(78, y + 166,
           "⚠⚠ Ce que la mesure ne dit pas : ce qu'une matière mieux résolue donnerait. Le voxel "
           "vaut 2,4 µm et une fibre en fait quatre à huit ; à 1,129 µm elle en ferait une", petit,
           GRIS)
    ecrire(78, y + 188,
           "quinzaine. ⚠ Et la marche est GLOUTONNE — elle prend le plus brillant des trois "
           "voisins à chaque pas — donc elle ne cherche pas le meilleur chemin, seulement un "
           "chemin.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(173.0, 0), _fr(0.4855, 4)) == ("90", "173", "0,4855"),
      f"{(_fr(90.0, 0), _fr(173.0, 0), _fr(0.4855, 4))}")
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
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ★★★★ LA LONGUEUR SUIVIE EST LUE DE PLUSIEURS COTES.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_long_en_pas"] = 61.75
    _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la longueur suivie est lue de PLUSIEURS côtés",
      sum(1 for _x, _y, t, _f in p2 if "61,75" in t) >= 3,
      f"{sum(1 for _x, _y, t, _f in p2 if '61,75' in t)} mentions")

    # ★★★★ LES DEUX CONTROLES SONT LUS : sans eux, « le rouleau porte des cretes » est une phrase.
    for cle, val, nom in (("en_travers_en_pas", 41.25, "en travers"),
                          ("melangee_en_pas", 9.125, "sur du mélange")):
        faux2 = copy.deepcopy(d)
        faux2["le_verdict"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
        v(f"★★★★ le contrôle {nom} est lu des DEUX côtés",
          sum(1 for _x, _y, t, _f in p3 if _fr(val, 2) in t) >= 2,
          f"{sum(1 for _x, _y, t, _f in p3 if _fr(val, 2) in t)} mentions")

    # ★★★★ LA COMPARAISON AU PAS DE FEUILLE EST LUE DES DEUX COTES : c'est le ✗ de la tranche.
    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["il_vaut_le_pas_entre_deux_feuilles_fois"] = 0.9137
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("★★★★ le rapport au pas entre deux feuilles est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "0,9137" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '0,9137' in t)} mentions")

    # ★★★ CHAQUE ANGLE DE L'ETALON EST DESSINE.
    faux4 = copy.deepcopy(d)
    faux4["letalon"]["lignes"][1]["le_long"]["pas_median"] = 51.5
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("★★★ chaque angle de l'étalon est dessiné",
      any("51,5" in t for _x, _y, t, _f in p5) and not any("51,5" in x for x in tous))

    creux = copy.deepcopy(d)
    creux["le_verdict"]["le_suiveur_suit"] = False
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("★★★★ une mesure dont le suiveur ne suit pas est REFUSÉE", lire_ok)

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
                   default=RACINE / "docs" / "mesures" / "jusquou_suit_on_une_fibre.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "185_jusquou_suit_on_une_fibre.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
