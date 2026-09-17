"""Un creux se retrouve-t-il à côté ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les deux bornes construites et le
rouleau entre elles. En haut à droite, les trois segments. En bas à gauche, la distribution des parts
appariées, paire par paire. En bas à droite, ce que ça vaut comme repère.

  uv run python src/figures/figure_un_creux_se_retrouve_t_il_a_cote.py \\
      --json docs/mesures/un_creux_se_retrouve_t_il_a_cote.json \\
      --sortie docs/images/183_un_creux_se_retrouve_t_il_a_cote.png
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
    """Le JSON de `un_creux_se_retrouve_t_il_a_cote.py`.

    ⚠⚠ Refuse une mesure dont les deux bornes construites ne se séparent pas : c'est entre elles que
    le rouleau se place, et une première version les avait ÉGALES — décaler d'une demi-feuille remet
    les frontières de pli aux mêmes couches.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "la_fixture", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("les_deux_bornes_se_separent"):
        raise ValueError(f"{chemin} : les deux bornes construites ne se séparent pas")
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

    v, fx = d["le_verdict"], d["la_fixture"]
    ecrire(28, 20, "Un creux se retrouve-t-il à côté ? — un peu, et très loin de ce qu'un repère "
                   "demande", gros, ENCRE)
    ecrire(28, 46, f"{d['creux_cherches_par_chunk']} creux cherchés · amas de 2×2 sur le treillis "
                   f"{d['cote_du_treillis']}×{d['cote_du_treillis']} · {v['amas_lus']} amas · "
                   f"{v['paires_adjacentes']} paires adjacentes · "
                   f"{d['tirages_de_non_voisins']} tirages de non-voisins", petit, GRIS)

    # ---- panneau 1 : les deux bornes et le rouleau entre elles
    x0, y0, pw, ph = 56, 122, 620, 266
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux bornes construites, et le rouleau entre elles", moyen, ENCRE)
    lignes = (("la même matière", fx["part_mediane_de_la_meme_matiere"], BON),
              ("le rouleau, chez le voisin", v["part_des_voisins"], ALERTE),
              ("le rouleau, chez un non-voisin", v["part_des_non_voisins"], CONTRE),
              ("deux matières différentes", fx["part_mediane_de_matieres_differentes"], GRIS))
    for k, (nom, val, coul) in enumerate(lignes):
        yy = y0 + 26 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 230, yy, _fr(val, 4), 0, coul)
        barre(x0 + 292, yy + 2, 300, float(val or 0.0), 12, coul)
    ecrire(x0 + 292, y0 + 170, "0", 0, GRIS)
    ecrire(x0 + 574, y0 + 170, "1", 0, GRIS)
    ecrire(x0 + 14, y0 + 196,
           f"★ Chez le voisin {_fr(v['part_des_voisins'], 4)}, chez un non-voisin "
           f"{_fr(v['part_des_non_voisins'], 4)}.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 224,
           f"✗ Mais {_fr(v['le_rouleau_vaut_la_meme_matiere_fois'], 4)} fois seulement ce que la "
           "même matière rend.", moyen, ALERTE)

    # ---- panneau 2 : les segments
    x0, y0, pw, ph = 712, 122, 592, 266
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 176, y0 + 10, "voisins", petit, ALERTE)
    ecrire(x0 + 300, y0 + 10, "non-voisins", petit, CONTRE)
    ecrire(x0 + 430, y0 + 10, "paires", petit, ENCRE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 38 + k * 44
        loin = s["les_non_voisins"]
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"{s['amas_lus']} amas · {s['chunks_lus']} chunks", 0, GRIS)
        ecrire(x0 + 176, yy, _fr(s["part_moyenne_des_voisins"], 4), 0, ALERTE)
        barre(x0 + 176, yy + 18, 100, float(s["part_moyenne_des_voisins"] or 0.0), 9, ALERTE)
        ecrire(x0 + 300, yy, _fr(loin.get("part_moyenne"), 4), 0, CONTRE)
        barre(x0 + 300, yy + 18, 100, float(loin.get("part_moyenne") or 0.0), 9, CONTRE)
        ecrire(x0 + 430, yy, f"{s['paires_qui_se_correspondent']}/{s['paires_adjacentes']}", 0,
               ENCRE)
        ecrire(x0 + 430, yy + 16, f"écart {_fr(s['ecart_median_des_voisins'], 1)}", 0, GRIS)
    ecrire(x0 + 14, y0 + 186,
           f"★ {v['paires_qui_se_correspondent']} paires sur {v['paires_adjacentes']} portent au "
           "moins un creux commun,", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 210,
           f"     et quand un creux se retrouve, il est à {_fr(v['ecart_median_des_voisins'], 1)} "
           "couche près.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 234,
           "⚠ Le non-voisin est tiré parmi les chunks des AUTRES amas : même loi de", petit, GRIS)
    ecrire(x0 + 14, y0 + 248,
           "profondeurs, même densité de creux, seul le voisinage change.", petit, GRIS)

    # ---- panneau 3 : la distribution des parts, paire par paire
    x0, y0, pw, ph = 56, 440, 620, 272
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "paire par paire — la plupart ne partagent aucun creux", moyen, ENCRE)
    parts = sorted(float(p["part"]) for s in lus for a in s["amas"] for p in a["paires"]
                   if p.get("part") is not None)
    hx, hy, hw, hh = x0 + 46, y0 + 26, 540, 132
    art.line([hx, hy + hh, hx + hw, hy + hh], fill=TRAIT, width=1)
    cases = 10
    compte = [0] * cases
    for p in parts:
        compte[min(cases - 1, int(p * cases))] += 1
    haut = max(1, max(compte))
    for i, n in enumerate(compte):
        bx = hx + hw * i / float(cases)
        bh = hh * float(n) / float(haut)
        if bh > 0:
            art.rectangle([bx + 2, hy + hh - bh, bx + hw / cases - 2, hy + hh], fill=ALERTE)
        # ⚠ LE SOMMET DE CHAQUE BARRE EST ENREGISTRE, PAS SEULEMENT SON PIED : une sonde qui
        # remplacait toutes les parts par un ne deplacait aucun point, donc le controle « la
        # figure vient des paires mesurees » ne pouvait pas echouer.
        points.append((bx + hw / cases - 2, hy + hh))
        points.append((bx + 2, hy + hh - bh))
        if n:
            ecrire(bx + 6, hy + hh - bh - 14, str(n), 0, GRIS)
    ecrire(hx - 8, hy + hh + 6, "0", 0, GRIS)
    ecrire(hx + hw - 8, hy + hh + 6, "1", 0, GRIS)
    ecrire(hx + hw / 2 - 60, hy + hh + 24, "part des creux appariés, par paire", 0, GRIS)
    ecrire(x0 + 14, y0 + 206,
           f"✗ {compte[0]} paires sur {len(parts)} ne partagent AUCUN creux.", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 236,
           "⚠ Un appariement est exclusif et la part se calcule sur le plus petit des", petit, GRIS)
    ecrire(x0 + 14, y0 + 252,
           "deux : sinon elle mesurerait une densité de creux et non une correspondance.", petit,
           GRIS)

    # ---- panneau 4 : ce que ça vaut comme repère
    x0, y0, pw, ph = 712, 440, 592, 272
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que ça vaut comme repère", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 20,
           "Un repère n'a pas besoin d'être périodique — `182` a montré qu'il ne l'est", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 36,
           "pas. Il a besoin d'être RETROUVABLE d'une spire à la suivante.", petit, ENCRE)
    for k, (nom, val, coul) in enumerate(
            (("il se retrouve un peu", v["part_des_voisins"], ALERTE),
             ("par hasard", v["part_des_non_voisins"], CONTRE),
             ("ce qu'il faudrait", fx["part_mediane_de_la_meme_matiere"], BON))):
        yy = y0 + 70 + k * 32
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 200, yy, _fr(val, 4), 0, coul)
        barre(x0 + 260, yy + 2, 300, float(val or 0.0), 12, coul)
    ecrire(x0 + 14, y0 + 178,
           f"✗ L'écart au hasard est réel mais mince : {_fr(v['part_des_voisins'], 4)} contre "
           f"{_fr(v['part_des_non_voisins'], 4)}.", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 206,
           "★ Et quand un creux se retrouve, il est très précis : une couche.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 236,
           "⚠ Un creux seul ne suffit donc pas à transférer une spire. Ce qui reste à", petit, GRIS)
    ecrire(x0 + 14, y0 + 252,
           "essayer est de les prendre ENSEMBLE plutôt qu'un par un.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LES DEUX BORNES SE SÉPARENT : la même matière lue deux fois rend "
           f"{_fr(fx['part_mediane_de_la_meme_matiere'], 4)}, deux matières différentes "
           f"{_fr(fx['part_mediane_de_matieres_differentes'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"★  UN CREUX SE RETROUVE À CÔTÉ PLUS SOUVENT QUE PAR HASARD : "
           f"{_fr(v['part_des_voisins'], 4)} chez le voisin contre "
           f"{_fr(v['part_des_non_voisins'], 4)} chez un non-voisin tiré parmi les autres amas.",
           moyen, ENCRE)
    ecrire(78, y + 74,
           f"     Et quand il se retrouve, il est à {_fr(v['ecart_median_des_voisins'], 1)} couche "
           "près : le signal est rare, mais il est précis.", moyen, ENCRE)
    ecrire(78, y + 106,
           f"✗  MAIS C'EST {_fr(v['le_rouleau_vaut_la_meme_matiere_fois'], 4)} FOIS SEULEMENT CE "
           f"QUE LA MÊME MATIÈRE REND, et {compte[0]} paires adjacentes sur {len(parts)} ne "
           "partagent AUCUN creux.", moyen, ALERTE)
    ecrire(78, y + 134,
           "     Un creux pris seul ne suffit donc pas à transférer une spire à la suivante : "
           "c'est le fait qui décide, et il est négatif.", moyen, ALERTE)
    ecrire(78, y + 166,
           "⚠⚠ Ce que la tranche ne dit pas : ce que valent les creux pris ENSEMBLE. Une suite de "
           "quatre creux peut être retrouvable là où aucun de ses membres ne l'est,", petit, GRIS)
    ecrire(78, y + 188,
           "et c'est une question de MOTIF et non de position. ⚠ Et deux chunks voisins partagent "
           "une frontière de 128 voxels : ce qui est mesuré ici est la correspondance à cette "
           "distance-là.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(1.0, 4), _fr(0.2222, 4)) == ("90", "1", "0,2222"),
      f"{(_fr(90.0, 0), _fr(1.0, 4), _fr(0.2222, 4))}")
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

    # ★★★★ LA PART DES VOISINS EST LUE DE TROIS COTES : c'est le ★ de la tranche.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["part_des_voisins"] = 0.4321
    _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la part chez le voisin est lue de PLUSIEURS côtés",
      sum(1 for _x, _y, t, _f in p2 if "0,4321" in t) >= 3,
      f"{sum(1 for _x, _y, t, _f in p2 if '0,4321' in t)} mentions")

    # ★★★★ CELLE DES NON-VOISINS AUSSI : sans elle « il se retrouve » n'a pas de nul.
    faux2 = copy.deepcopy(d)
    faux2["le_verdict"]["part_des_non_voisins"] = 0.1975
    _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
    v("★★★★ la part chez un non-voisin est lue de PLUSIEURS côtés",
      sum(1 for _x, _y, t, _f in p3 if "0,1975" in t) >= 3,
      f"{sum(1 for _x, _y, t, _f in p3 if '0,1975' in t)} mentions")

    # ★★★★ LES DEUX BORNES SONT DESSINEES : sans elles le rouleau n'a pas d'echelle.
    faux3 = copy.deepcopy(d)
    faux3["la_fixture"]["part_mediane_de_matieres_differentes"] = 0.3125
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("★★★★ la borne des matières différentes est lue des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "0,3125" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '0,3125' in t)} mentions")

    # ★★★★ L'HISTOGRAMME VIENT DES PAIRES MESUREES.
    faux4 = copy.deepcopy(d)
    for s in faux4["les_segments"]:
        if s.get("decidable"):
            for a in s["amas"]:
                for p in a["paires"]:
                    if p.get("part") is not None:
                        p["part"] = 1.0
    _c, _p, _cd, pt5, _b, _t = dessiner(faux4, sortie)
    v("★★★★ l'histogramme vient des paires mesurées", pt5 != points)

    # ★★★ LE COMPTE DE PAIRES QUI SE CORRESPONDENT EST LU.
    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["paires_qui_se_correspondent"] = 77
    _c, p6, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("★★★ le compte de paires qui se correspondent est lu",
      any("77 paires sur" in t for _x, _y, t, _f in p6)
      and not any("77 paires sur" in x for x in tous))

    creux = copy.deepcopy(d)
    creux["le_verdict"]["les_deux_bornes_se_separent"] = False
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("★★★★ une mesure dont les bornes ne se séparent pas est REFUSÉE", lire_ok)

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
                   default=RACINE / "docs" / "mesures" / "un_creux_se_retrouve_t_il_a_cote.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "183_un_creux_se_retrouve_t_il_a_cote.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
