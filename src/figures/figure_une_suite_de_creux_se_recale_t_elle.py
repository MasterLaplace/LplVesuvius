"""Une suite de creux se recale-t-elle ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le recalage triple la
correspondance — et il la triple AUSSI chez le non-voisin. En haut à droite, l'étalon : le recalage
retrouve tous les décalages construits, donc il recale vraiment. En bas à gauche, les segments. En
bas à droite, le chiffre qui décide : aucune paire ne dépasse son propre tirage.

  uv run python src/figures/figure_une_suite_de_creux_se_recale_t_elle.py \\
      --json docs/mesures/une_suite_de_creux_se_recale_t_elle.json \\
      --sortie docs/images/184_une_suite_de_creux_se_recale_t_elle.png
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
    """Le JSON de `une_suite_de_creux_se_recale_t_elle.py`.

    ⚠⚠⚠ Refuse une mesure dont l'étalon ne retrouve pas ses décalages construits : si le recalage ne
    recale pas, tout ce que le rouleau rend est du bruit sous un nom qui promet autre chose. Une
    première version avait le signe attendu à l'envers et l'étalon rendait quatre sur seize.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "la_fixture", "le_verdict", "de_183"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("le_recalage_retrouve_un_decalage_construit"):
        raise ValueError(f"{chemin} : l'étalon ne retrouve pas ses décalages construits")
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
    ecrire(28, 20, "Une suite de creux se recale-t-elle ? — le gain est celui de la liberté de "
                   "décaler", gros, ENCRE)
    ecrire(28, 46, f"{d['creux_cherches_par_chunk']} creux · plage ±{d['plage_de_decalage']} "
                   f"couches · {v['amas_lus']} amas · {v['paires_adjacentes']} paires adjacentes · "
                   f"{d['permutations']} tirages par paire · recouvrement "
                   f"{_fr(d['recouvrement_um_de_179'], 1)} µm (`179`)", petit, GRIS)

    # ---- panneau 1 : le recalage triple, mais des deux côtés
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le recalage triple la correspondance — et des DEUX côtés", moyen, ENCRE)
    lignes = (("la même matière (étalon)", fx["part_mediane"], BON),
              ("les voisins, recalés", v["part_des_voisins_recales"], ALERTE),
              ("les non-voisins, recalés", v["part_des_non_voisins_recales"], CONTRE),
              ("les voisins, sans recalage (`183`)",
               v["part_des_voisins_sans_recalage_de_183"], GRIS))
    for k, (nom, val, coul) in enumerate(lignes):
        yy = y0 + 26 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 250, yy, _fr(val, 4), 0, coul)
        barre(x0 + 312, yy + 2, 280, float(val or 0.0), 12, coul)
    ecrire(x0 + 312, y0 + 170, "0", 0, GRIS)
    ecrire(x0 + 584, y0 + 170, "1", 0, GRIS)
    ecrire(x0 + 14, y0 + 196,
           f"★ Le recalage fait passer les voisins de "
           f"{_fr(v['part_des_voisins_sans_recalage_de_183'], 4)} à "
           f"{_fr(v['part_des_voisins_recales'], 4)},", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 224,
           f"✗ mais il porte les non-voisins à {_fr(v['part_des_non_voisins_recales'], 4)}.",
           moyen, ALERTE)

    # ---- panneau 2 : l'étalon
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — le recalage retrouve ce qu'on lui pose", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "décalage posé", petit, GRIS)
    ecrire(x0 + 170, y0 + 10, "retrouvé", petit, BON)
    ecrire(x0 + 300, y0 + 10, "correspondance", petit, ENCRE)
    for k, x in enumerate(fx["lignes"]):
        yy = y0 + 36 + k * 26
        ecrire(x0 + 14, yy, f"{x['decalage_pose']:+d} couches", 0, ENCRE)
        ecrire(x0 + 170, yy, f"{x['retrouve']}/{x['cellules']}", 0, BON)
        barre(x0 + 220, yy + 3, 60, float(x["retrouve"]) / max(1, int(x["cellules"])), 10, BON)
        ecrire(x0 + 300, yy, _fr(x["part_mediane"], 4), 0, ENCRE)
    ecrire(x0 + 14, y0 + 150,
           f"★ {v['decalages_retrouves_sur_la_fixture']}/{v['cellules_de_la_fixture']} décalages "
           f"retrouvés exactement, correspondance {_fr(v['part_de_la_fixture'], 4)}.", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 178,
           f"     Il recale donc vraiment. Sur le rouleau, décalage médian "
           f"{_fr(v['decalage_median'], 1)} couches.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 210,
           "⚠⚠ Le SIGNE attendu a été mesuré et non raisonné : ma première rédaction le", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 226,
           "prenait à l'envers et l'étalon rendait quatre sur seize.", petit, ALERTE)

    # ---- panneau 3 : les segments
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 180, y0 + 10, "voisins", petit, ALERTE)
    ecrire(x0 + 300, y0 + 10, "non-voisins", petit, CONTRE)
    ecrire(x0 + 430, y0 + 10, "dépassent", petit, ENCRE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 38 + k * 44
        loin = s["les_non_voisins"]
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"{s['amas_lus']} amas · décalage "
                                 f"{_fr(s['decalage_median'], 1)}", 0, GRIS)
        ecrire(x0 + 180, yy, _fr(s["part_moyenne_des_voisins"], 4), 0, ALERTE)
        barre(x0 + 180, yy + 18, 100, float(s["part_moyenne_des_voisins"] or 0.0), 9, ALERTE)
        ecrire(x0 + 300, yy, _fr(loin.get("part_moyenne"), 4), 0, CONTRE)
        barre(x0 + 300, yy + 18, 100, float(loin.get("part_moyenne") or 0.0), 9, CONTRE)
        ecrire(x0 + 430, yy, f"{s['paires_qui_depassent_le_hasard']}/{s['paires_adjacentes']}",
               0, ENCRE)
    ecrire(x0 + 14, y0 + 180,
           "⚠ Le non-voisin subit EXACTEMENT la même recherche de décalage, sur la même", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 196,
           "plage : sans cela, comparer un voisin recalé à un non-voisin non recalé", petit, GRIS)
    ecrire(x0 + 14, y0 + 212, "mesurerait la liberté de bouger et rien d'autre.", petit, GRIS)
    ecrire(x0 + 14, y0 + 236,
           "⚠⚠ La plage vaut un DEMI-PLI : au-delà, un décalage fait tomber une frontière",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 252, "sur la suivante et cesse d'être un décalage.", petit, GRIS)

    # ---- panneau 4 : le chiffre qui décide
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le chiffre qui décide", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 24,
           "Chaque paire est comparée à SES PROPRES creux tirés au hasard,", petit, ENCRE)
    ecrire(x0 + 14, y0 + 40,
           "en même nombre, recalés sur la même plage.", petit, ENCRE)
    gx, gy, gw, gh = x0 + 40, y0 + 70, 500, 52
    art.rectangle([gx, gy, gx + gw, gy + gh], outline=TRAIT, width=1)
    part = float(v["paires_qui_depassent_le_hasard"]) / max(1, int(v["paires_adjacentes"]))
    barre(gx + 1, gy + 1, gw - 2, part, gh - 2, ALERTE)
    ecrire(gx + 12, gy + 18,
           f"{v['paires_qui_depassent_le_hasard']} paires sur {v['paires_adjacentes']} "
           f"dépassent leur propre tirage", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 146,
           f"✗ {_fr(v['part_des_paires_qui_depassent'], 4)} — le contrôle apparié absorbe",
           moyen, ALERTE)
    ecrire(x0 + 14, y0 + 170, "entièrement le gain du recalage.", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 200,
           "⚠⚠⚠ Un creux UNIQUE se recale toujours : un seul point se met en face de", petit, GRIS)
    ecrire(x0 + 14, y0 + 216,
           "n'importe quel autre point de la plage, donc il ne peut jamais battre son", petit, GRIS)
    ecrire(x0 + 14, y0 + 232, "propre tirage. Le recalage ne crée pas d'information.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LE RECALAGE RECALE : il retrouve {v['decalages_retrouves_sur_la_fixture']}/"
           f"{v['cellules_de_la_fixture']} décalages construits, des deux signes et nul compris, "
           f"avec une correspondance de {_fr(v['part_de_la_fixture'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"★  ET IL TRIPLE LA CORRESPONDANCE DES VOISINS : "
           f"{_fr(v['part_des_voisins_sans_recalage_de_183'], 4)} sans lui (`183`), "
           f"{_fr(v['part_des_voisins_recales'], 4)} avec — soit "
           f"{_fr(v['ce_quil_ajoute_fois'], 4)} fois.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"✗  MAIS IL PORTE AUSSI LES NON-VOISINS À {_fr(v['part_des_non_voisins_recales'], 4)}, "
           f"et AUCUNE des {v['paires_adjacentes']} paires ne dépasse son propre tirage de creux "
           "au hasard.", moyen, ALERTE)
    ecrire(78, y + 106,
           "     Le gain vient donc de la LIBERTÉ DE DÉCALER et non d'une propriété de la matière. "
           "Le recalage ne crée pas d'information, il en consomme.", moyen, ALERTE)
    ecrire(78, y + 138,
           "⚠⚠⚠ Cette voie est donc close : ni un creux seul (`183`), ni une suite recalée ne "
           "transfèrent une spire à la suivante. Ce que la chaîne a gagné est ailleurs —", moyen,
           ENCRE)
    ecrire(78, y + 166,
           f"     le creux EXISTE, il est profond, il tombe où l'orientation change le plus, et il "
           f"tient au bruit. Ce qui manque est sa CONTINUITÉ latérale.", moyen, ENCRE)
    ecrire(78, y + 194,
           "⚠ Et ce qui n'a jamais été mesuré reste ce que `14` §8 nomme : la continuité LE LONG "
           "D'UNE LIGNE, en suivant un individu plutôt qu'en comparant des cases.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(1.0, 4), _fr(0.6667, 4)) == ("90", "1", "0,6667"),
      f"{(_fr(90.0, 0), _fr(1.0, 4), _fr(0.6667, 4))}")
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

    # ★★★★ LE CHIFFRE QUI DECIDE EST LU DE PLUSIEURS COTES.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["paires_qui_depassent_le_hasard"] = 41
    _c, p2, _cd, _pt, b2, _t = dessiner(faux, sortie)
    v("★★★★ le compte de paires qui dépassent est lu, barre comprise",
      sum(1 for _x, _y, t, _f in p2 if "41 paires sur" in t) >= 1
      and any("41" in t for _x, _y, t, _f in p2) and b2 != barres)

    # ★★★★ LES DEUX PARTS RECALEES SONT LUES DES DEUX COTES : sans la seconde, le triplement se
    # lirait comme un gain.
    for cle, val, nom in (("part_des_voisins_recales", 0.4321, "des voisins"),
                          ("part_des_non_voisins_recales", 0.1975, "des non-voisins")):
        faux2 = copy.deepcopy(d)
        faux2["le_verdict"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
        v(f"★★★★ la part recalée {nom} est lue des DEUX côtés",
          sum(1 for _x, _y, t, _f in p3 if _fr(val, 4) in t) >= 2,
          f"{sum(1 for _x, _y, t, _f in p3 if _fr(val, 4) in t)} mentions")

    # ★★★★ CE QUE `183` RENDAIT EST RELU : sans lui, le triplement n'a pas d'origine.
    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["part_des_voisins_sans_recalage_de_183"] = 0.3125
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("★★★★ ce que `183` rendait est relu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "0,3125" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '0,3125' in t)} mentions")

    # ★★★ CHAQUE LIGNE DE L'ETALON EST DESSINEE.
    faux4 = copy.deepcopy(d)
    faux4["la_fixture"]["lignes"][1]["retrouve"] = 1
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("★★★ chaque ligne de l'étalon est dessinée",
      any(t == "1/4" for _x, _y, t, _f in p5) and not any(x == "1/4" for x in tous))

    creux = copy.deepcopy(d)
    creux["le_verdict"]["le_recalage_retrouve_un_decalage_construit"] = False
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("★★★★ une mesure dont l'étalon ne recale pas est REFUSÉE", lire_ok)

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
                   / "une_suite_de_creux_se_recale_t_elle.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "184_une_suite_de_creux_se_recale_t_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
