"""La feuille a-t-elle trois plis ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les espacements construits et
celui du rouleau. En haut à droite, les étalons : chacun relit le pas qu'il porte, ce qui dit que le
lecteur est juste. En bas à gauche, les segments. En bas à droite, l'ÉTALEMENT — et c'est lui qui
refuse l'hypothèse, parce que le rouleau y est six fois au-dessus de tout empilement régulier.

  uv run python src/figures/figure_la_feuille_a_t_elle_trois_plis.py \\
      --json docs/mesures/la_feuille_a_t_elle_trois_plis.json \\
      --sortie docs/images/182_la_feuille_a_t_elle_trois_plis.png
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
    """Le JSON de `la_feuille_a_t_elle_trois_plis.py`.

    ⚠⚠ Refuse une mesure dont les deux formes construites ne se séparent pas : c'est l'étalement qui
    tranche cette tranche, et si un mélange étalait moins qu'un empilement régulier, la comparaison
    du rouleau à l'un ou à l'autre ne voudrait rien dire.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "les_etalons", "le_melange", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("les_deux_formes_se_separent"):
        raise ValueError(f"{chemin} : les deux formes construites ne se séparent pas")
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

    v, m = d["le_verdict"], d["le_melange"]
    ecrire(28, 20, "La feuille a-t-elle trois plis ? — non : le rouleau n'est régulier à aucun "
                   "nombre de plis", gros, ENCRE)
    ecrire(28, 46, f"{d['creux_cherches_par_chunk']} creux cherchés par chunk · "
                   f"{v['chunks_lus']} chunks sur {v['segments']} segments · "
                   f"{d['permutations']} permutations · plis balayés {d['plis_balayes']} · bruit "
                   f"{_fr(d['bruit_apparie_de_180'], 0)} (`180`)", petit, GRIS)

    # ---- panneau 1 : les espacements sur une règle
    x0, y0, pw, ph = 56, 122, 620, 258
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les espacements qu'une feuille de P plis porte, et celui du rouleau",
           moyen, ENCRE)
    haut = max([e["espacement_construit"] for e in d["les_etalons"]]
               + [v["espacement_median_du_rouleau"] or 0.0]) * 1.2
    gx, gw = x0 + 130, 420
    for k, e in enumerate(d["les_etalons"]):
        yy = y0 + 22 + k * 28
        ecrire(x0 + 14, yy - 2, f"{e['plis']} plis", 0, BON)
        barre(gx, yy, gw, float(e["espacement_construit"]) / haut, 12, BON)
        ecrire(gx + gw * float(e["espacement_construit"]) / haut + 6, yy - 2,
               _fr(e["espacement_construit"], 3), 0, BON)
    yy = y0 + 22 + len(d["les_etalons"]) * 28
    ecrire(x0 + 14, yy - 2, "le rouleau", 0, ALERTE)
    barre(gx, yy, gw, float(v["espacement_median_du_rouleau"] or 0.0) / haut, 12, ALERTE)
    ecrire(gx + gw * float(v["espacement_median_du_rouleau"] or 0.0) / haut + 6, yy - 2,
           _fr(v["espacement_median_du_rouleau"], 1), 0, ALERTE)
    ecrire(x0 + 14, y0 + 158,
           f"★ L'espacement médian du rouleau vaut {_fr(v['espacement_median_du_rouleau'], 1)} "
           f"couches,", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 182,
           f"     et le pli le plus proche est {v['les_plis_qui_correspondent']} "
           f"({_fr(v['espacement_construit_a_ce_pli'], 3)}).", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 212,
           f"⚠ `181` en rendait {_fr(v['espacement_median_de_181'], 1)} avec un plafond de trois "
           "creux : un plafond trop bas", petit, GRIS)
    ecrire(x0 + 14, y0 + 228,
           "ne rend pas moins de creux, il rend des MULTIPLES du vrai pas.", petit, GRIS)

    # ---- panneau 2 : les étalons relisent leur pas
    x0, y0, pw, ph = 712, 122, 592, 258
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "chaque étalon relit le pas qu'il porte — le lecteur est juste", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 10, "plis", petit, GRIS)
    ecrire(x0 + 80, y0 + 10, "construit", petit, ENCRE)
    ecrire(x0 + 180, y0 + 10, "lu", petit, ENCRE)
    ecrire(x0 + 260, y0 + 10, "mesures", petit, GRIS)
    ecrire(x0 + 350, y0 + 10, "étalement relatif", petit, ALERTE)
    for k, e in enumerate(d["les_etalons"]):
        yy = y0 + 36 + k * 26
        marque = e["plis"] == v.get("les_plis_qui_correspondent")
        ecrire(x0 + 14, yy, f"{e['plis']}", 0, ENCRE)
        ecrire(x0 + 80, yy, _fr(e["espacement_construit"], 3), 0, GRIS)
        ecrire(x0 + 180, yy, _fr(e["mediane"], 1), 0, ENCRE)
        ecrire(x0 + 260, yy, str(e["mesures"]), 0, GRIS)
        ecrire(x0 + 350, yy, _fr(e["etalement_relatif"], 4), 0, BON)
        barre(x0 + 420, yy + 3, 140, float(e["etalement_relatif"] or 0.0) / 0.6, 10, BON)
        if marque:
            ecrire(x0 + 566, yy, "★", 0, ENCRE)
    yy = y0 + 36 + len(d["les_etalons"]) * 26
    ecrire(x0 + 14, yy, "mél.", 0, CONTRE)
    ecrire(x0 + 80, yy, "—", 0, GRIS)
    ecrire(x0 + 180, yy, _fr(m["mediane"], 1), 0, CONTRE)
    ecrire(x0 + 260, yy, str(m["mesures"]), 0, GRIS)
    ecrire(x0 + 350, yy, _fr(m["etalement_relatif"], 4), 0, CONTRE)
    barre(x0 + 420, yy + 3, 140, float(m["etalement_relatif"] or 0.0) / 0.6, 10, CONTRE)
    ecrire(x0 + 14, y0 + 158,
           f"★ Un mélange à {m['surnumeraires']} creux en trop étale "
           f"{_fr(m['etalement_relatif'], 4)},", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 182,
           f"     un empilement régulier {_fr(v['etalement_relatif_a_ce_pli'], 4)}. Les deux "
           "formes se séparent.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 212,
           "⚠ Le nombre de creux en trop est dérivé des ESPACEMENTS et non des comptes,", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 228,
           "qui sont plafonnés par le lecteur et rendaient un mélange sans mélange.", petit, GRIS)

    # ---- panneau 3 : les segments
    x0, y0, pw, ph = 56, 432, 620, 280
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments du rouleau", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 180, y0 + 10, "creux", petit, ENCRE)
    ecrire(x0 + 260, y0 + 10, "espacement", petit, ENCRE)
    ecrire(x0 + 380, y0 + 10, "étalement relatif", petit, ALERTE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 38 + k * 38
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"{s['chunks_lus']} chunks · {s['mesures']} mesures", 0, GRIS)
        ecrire(x0 + 180, yy, str(s["creux_retenus"]), 0, ENCRE)
        ecrire(x0 + 260, yy, _fr(s["mediane"], 1), 0, ENCRE)
        ecrire(x0 + 380, yy, _fr(s["etalement_relatif"], 4), 0, ALERTE)
        barre(x0 + 450, yy + 3, 140, float(s["etalement_relatif"] or 0.0) / 0.6, 10, ALERTE)
    ecrire(x0 + 14, y0 + 170,
           f"★ {v['creux_retenus']} creux retenus, {v['espacements_mesures']} espacements mesurés "
           f"sur {v['chunks_lus']} chunks.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 202,
           "⚠ Le plafond de creux est DÉRIVÉ du pas le plus fin de l'échelle : à quatre plis",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 218,
           "la matière porte une frontière toutes les dix-huit couches, et un lecteur", petit, GRIS)
    ecrire(x0 + 14, y0 + 234,
           "plafonné à trois en rendait cinquante-trois — il ne voyait que les trois plus", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 250, "profondes, qui ne sont pas voisines.", petit, GRIS)

    # ---- panneau 4 : l'étalement, et c'est lui qui refuse
    x0, y0, pw, ph = 712, 432, 592, 280
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalement — et c'est lui qui refuse l'hypothèse", moyen, ENCRE)
    lignes = ([(f"{e['plis']} plis, régulier", e["etalement_relatif"], BON)
               for e in d["les_etalons"]]
              + [("un mélange construit", m["etalement_relatif"], CONTRE),
                 ("le rouleau", v["etalement_relatif_du_rouleau"], ALERTE)])
    for k, (nom, val, coul) in enumerate(lignes):
        yy = y0 + 26 + k * 30
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 190, yy, _fr(val, 4), 0, coul)
        barre(x0 + 250, yy + 2, 300, float(val or 0.0) / 0.6, 12, coul)
    ecrire(x0 + 250, y0 + 182, "0", 0, GRIS)
    ecrire(x0 + 530, y0 + 182, "0,6", 0, GRIS)
    ecrire(x0 + 14, y0 + 208,
           f"✗ Le rouleau étale {_fr(v['etalement_relatif_du_rouleau'], 4)} : au-dessus de tout "
           "empilement régulier,", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 232,
           f"     et au-dessus du mélange construit ({_fr(m['etalement_relatif'], 4)}).", moyen,
           ALERTE)
    ecrire(x0 + 14, y0 + 258,
           "⚠ Un creux manqué fusionne deux espacements en un : ce lecteur ne l'exclut pas.",
           petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LE LECTEUR EST JUSTE : chaque étalon relit le pas qu'il porte — "
           + " · ".join(f"{e['plis']} plis {_fr(e['espacement_construit'], 3)} lu "
                        f"{_fr(e['mediane'], 1)}" for e in d["les_etalons"]) + ".", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     Et les deux formes construites se séparent : un empilement régulier étale "
           f"{_fr(v['etalement_relatif_a_ce_pli'], 4)}, un mélange "
           f"{_fr(m['etalement_relatif'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"✗  LA FEUILLE N'A PAS TROIS PLIS, ET PAS QUATRE NON PLUS : le rouleau étale "
           f"{_fr(v['etalement_relatif_du_rouleau'], 4)}, plusieurs fois au-dessus de TOUT "
           "empilement régulier.", moyen, ALERTE)
    ecrire(78, y + 106,
           f"     Son espacement médian ({_fr(v['espacement_median_du_rouleau'], 1)}) tombe près "
           f"de {v['les_plis_qui_correspondent']} plis, mais une médiane ne dit rien quand la "
           "distribution est aussi étalée.", moyen, ALERTE)
    ecrire(78, y + 138,
           f"✗  ET CE N'EST PAS NON PLUS LE MÉLANGE CONSTRUIT ({_fr(m['etalement_relatif'], 4)}) : "
           "les frontières du rouleau sont plus irrégulières qu'un empilement à deux plis plus "
           f"{m['surnumeraires']} fissures.", moyen, ALERTE)
    ecrire(78, y + 170,
           "⚠⚠ Ce que cette tranche établit est donc une NÉGATION : à cette échelle, la profondeur "
           "du rouleau n'est périodique à aucun pas. Ce qu'elle ne dit pas est ce qu'elle est.",
           petit, GRIS)
    ecrire(78, y + 192,
           "⚠ Et un creux manqué fusionne deux espacements en un, ce qui étale aussi : les étalons "
           "montrent que le lecteur ne le fait pas sur une matière régulière, pas qu'il ne le fait "
           "jamais.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(20.0, 1), _fr(0.5, 4)) == ("90", "20", "0,5"),
      f"{(_fr(90.0, 0), _fr(20.0, 1), _fr(0.5, 4))}")
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

    # ★★★★ L'ETALEMENT DU ROULEAU EST LU DES DEUX COTES : c'est le ✗ de la tranche.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["etalement_relatif_du_rouleau"] = 0.1234
    _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ l'étalement du rouleau est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p2 if "0,1234" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p2 if '0,1234' in t)} mentions")

    # ★★★★ CELUI DU MELANGE AUSSI : sans lui « le rouleau etale » n'a pas de borne haute.
    faux2 = copy.deepcopy(d)
    faux2["le_melange"]["etalement_relatif"] = 0.4321
    _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
    v("★★★★ l'étalement du mélange est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p3 if "0,4321" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p3 if '0,4321' in t)} mentions")

    # ★★★★ CHAQUE ETALON EST DESSINE AVEC SON PAS CONSTRUIT ET SON PAS LU : c'est ce qui dit que
    # le lecteur est juste, et l'ecrire en dur en ferait un dessin.
    faux3 = copy.deepcopy(d)
    faux3["les_etalons"][0]["mediane"] = 61.5
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("★★★★ le pas relu de chaque étalon est dessiné",
      sum(1 for _x, _y, t, _f in p4 if "61,5" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '61,5' in t)} mentions")

    # ★★★ LE NOMBRE DE CREUX SURNUMERAIRES EST LU.
    faux4 = copy.deepcopy(d)
    faux4["le_melange"]["surnumeraires"] = 9
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("★★★ le nombre de creux surnuméraires est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p5 if "9 " in t and "creux" in t) >= 1
      and sum(1 for _x, _y, t, _f in p5 if "9 fissures" in t) >= 1,
      str([t for _x, _y, t, _f in p5 if "9" in t][:2])[:150])

    # ★★★ L'ESPACEMENT DE `181` EST RELU : sans lui on ne voit pas que le plafond a change.
    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["espacement_median_de_181"] = 31.5
    _c, p6, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("★★★ l'espacement que `181` rendait est relu",
      any("31,5" in t for _x, _y, t, _f in p6) and not any("31,5" in x for x in tous))

    creux = copy.deepcopy(d)
    creux["le_verdict"]["les_deux_formes_se_separent"] = False
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("★★★★ une mesure dont les deux formes ne se séparent pas est REFUSÉE", lire_ok)

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
                   default=RACINE / "docs" / "mesures" / "la_feuille_a_t_elle_trois_plis.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "182_la_feuille_a_t_elle_trois_plis.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
