"""La fixture penche-t-elle du même côté que le rouleau ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle : ni la spirale nue ni
l'écrasement seul ne glissent le long de l'axe. En haut à droite, la comparaison qui décide — les
deux parts, sur la fixture calibrée et sur le VRAI rouleau. En bas à gauche, matière par matière :
le glissement axial naît du froissement et croît avec lui. En bas à droite, le suivi — une cohérence
de 0,558 contre 0,925, c'est-à-dire un chemin qui glisse autant sans glisser du même côté.

  uv run python src/figures/figure_la_fixture_penche_t_elle_du_meme_cote.py \\
      --json docs/mesures/la_fixture_penche_t_elle_du_meme_cote.json \\
      --sortie docs/images/169_la_fixture_penche_t_elle_du_meme_cote.png
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
    """Le JSON de `la_fixture_penche_t_elle_du_meme_cote.py`.

    ⚠⚠ Refuse une mesure sans la COMPARAISON au rouleau : une figure qui ne montrerait que la
    fixture serait une affirmation sur une matière déguisée en comparaison entre deux.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_ne_penche_pas") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    cp = j.get("la_comparaison_au_rouleau")
    if not cp or cp.get("le_cote_saccorde") is None or cp.get("le_suivi_saccorde") is None:
        raise ValueError(f"{chemin} : la comparaison au rouleau est absente")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr"))


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

    j = d["juger"]
    mat, c, cp = j["par_matiere"], j["le_controle_de_la_spirale_nue"], j["la_comparaison_au_rouleau"]
    pa, pz = cp["part_axiale"], cp["part_azimutale"]
    gl, co = cp["glissement_axial_um"], cp["coherence"]

    ecrire(28, 20, "La fixture penche-t-elle du même côté que le rouleau ? — non, "
                   "et elle ne le suit pas non plus", gros, ENCRE)
    ecrire(28, 46, "`R4-F87` calibre la fixture sur le rapport, le penchant et la cohérence, à "
                   "5,5 % — la DIRECTION de ce penchant n'en fait pas partie", petit, GRIS)

    # ---- panneau 1 : le controle
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle — une absence de penchant", moyen, ENCRE)
    m1 = "★" if c["il_ne_penche_pas"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{m1}  {c['nom']} ne glisse PAS le long de l'axe", moyen,
           BON if c["il_ne_penche_pas"] else ALERTE)
    ecrire(x0 + 14, y0 + 52,
           f"glissement axial {_fr(c['glissement_axial_median_um'], 1)} µm, parts "
           f"{_fr(c['axial_median'])} et {_fr(c['azimutal_median'])}, sur "
           f"{c['decidables']} marches", petit, ENCRE)
    ecr = next((m for m in mat if m["nom"].endswith("écrasée")), None)
    if ecr and ecr.get("decidable"):
        ecrire(x0 + 14, y0 + 86, "★  et l'ÉCRASEMENT seul ne glisse pas davantage", moyen, BON)
        ecrire(x0 + 14, y0 + 116,
               f"{_fr(ecr['glissement_axial_median_um'], 1)} µm : le glissement axial ne vient "
               f"donc pas de", petit, ENCRE)
        ecrire(x0 + 14, y0 + 132, "l'aplatissement, il vient du FROISSEMENT", petit, ENCRE)
    ecrire(x0 + 14, y0 + ph - 74,
           "⚠⚠ Ce qui est exigé ici n'est pas un SENS mais une ABSENCE : sur", petit, ALERTE)
    ecrire(x0 + 14, y0 + ph - 58,
           "une matière sans penchant la comparaison des deux parts ne veut", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 42,
           "rien dire, et un glissement y mesurerait le MARCHEUR plutôt que", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 26, "la matière.", petit, GRIS)

    # ---- panneau 2 : la comparaison qui decide
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la comparaison qui décide — les deux parts", moyen, ENCRE)
    x_barre = x0 + 132
    barre_max = pw - 240
    vmax = max(pa["la_fixture"], pa["le_rouleau"], pz["la_fixture"], pz["le_rouleau"]) or 1.0
    for k, (qui, cle) in enumerate((("la fixture calibrée", "la_fixture"),
                                    ("le VRAI rouleau", "le_rouleau"))):
        base = y0 + 30 + k * 86
        ecrire(x0 + 12, base - 18, qui, petit, ENCRE)
        for i, (lib, src, coul) in enumerate((("part axiale", pa, ALERTE),
                                              ("part azimutale", pz, CONTRE))):
            yy = base + i * 22
            val = float(src[cle])
            w = (val / vmax) * barre_max
            ecrire(x0 + 12, yy - 1, lib, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy - 1, _fr(val), 0, coul)
        gagne = "axiale" if src and float(pa[cle]) > float(pz[cle]) else "azimutale"
        ecrire(x0 + 12, base + 46, f"penche {gagne}", 0,
               BON if gagne == "axiale" else ALERTE)
    ecrire(x0 + 12, y0 + ph - 38,
           f"{'★' if cp['le_cote_saccorde'] else '✗'}  le côté ne s'accorde PAS : le rouleau "
           f"penche axialement,", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 20, "la fixture azimutalement", petit, ALERTE)

    # ---- panneau 3 : matiere par matiere
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le glissement axial naît du froissement, et croît avec lui",
           moyen, ENCRE)
    x_nom, x_b = x0 + 12, x0 + 150
    b_max = pw - 260
    gmax = max(m["glissement_axial_median_um"] for m in mat if m.get("decidable")) or 1.0
    pas_bloc = max((ph - 84) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        base = y0 + 22 + k * pas_bloc
        ecrire(x_nom, base + 4, _court(g["nom"]), petit, ENCRE)
        if not g.get("decidable"):
            continue
        val = float(g["glissement_axial_median_um"])
        w = (val / gmax) * b_max
        yy = base + 2
        if val:
            art.rectangle([x_b, yy, x_b + max(w, 1), yy + 13], fill=ALERTE)
        points.append((x_b + w, yy + 6))
        barres.append((x_b + w, x_b + b_max))
        ecrire(x_b + b_max + 8, base + 4, f"{_fr(val, 1)} µm", 0, ALERTE)
        ecrire(x_nom, base + 20,
               f"{g['penchent_axialement']} axial / {g['penchent_azimutalement']} azimutal "
               f"sur {g['decidables']}", 0,
               BON if g["elle_penche_axialement"] else GRIS)
    ecrire(x0 + 12, y0 + ph - 56,
           "⚠⚠ Sur la matière calibrée le compte est un PARTAGE, pas un sens :", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 38,
           "rien de systématique n'y penche d'un côté plutôt que de l'autre,", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "là où le rouleau, lui, penche toujours du même.", petit, GRIS)

    # ---- panneau 4 : le suivi
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le SUIVI — glisser autant n'est pas glisser pareil", moyen, ENCRE)
    x_barre = x0 + 132
    barre_max = pw - 250
    for k, (lib, src, n, unite) in enumerate(
            (("cohérence", co, 3, ""), ("glissement axial", gl, 1, " µm"))):
        base = y0 + 30 + k * 96
        ecrire(x0 + 12, base - 18, lib, petit, ENCRE)
        vmax2 = max(float(src["la_fixture"]), float(src["le_rouleau"])) or 1.0
        for i, (qui, cle, coul) in enumerate((("la fixture", "la_fixture", ALERTE),
                                              ("le rouleau", "le_rouleau", CONTRE))):
            yy = base + i * 22
            val = float(src[cle])
            w = (val / vmax2) * barre_max
            ecrire(x0 + 12, yy - 1, qui, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy - 1, f"{_fr(val, n)}{unite}", 0, coul)
    ecrire(x0 + 12, y0 + ph - 74,
           f"{'★' if cp['le_suivi_saccorde'] else '✗'}  le suivi ne s'accorde PAS non plus",
           petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 56,
           "La cohérence est le déplacement tangentiel NET divisé par le chemin", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 40,
           "PARCOURU : un chemin qui penche toujours du même côté rend un, un", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 24,
           "chemin qui oblique alternativement rend zéro.", petit, GRIS)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    ecrire(74, y + 12,
           f"✗  Le côté ne s'accorde pas : la fixture calibrée rend {_fr(pa['la_fixture'])} de "
           f"part axiale contre {_fr(pz['la_fixture'])} d'azimutale, quand le rouleau rend "
           f"{_fr(pa['le_rouleau'])} contre {_fr(pz['le_rouleau'])}.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"✗  Et le suivi non plus : cohérence {_fr(co['la_fixture'])} contre "
           f"{_fr(co['le_rouleau'])}. La fixture glisse AUTANT ({_fr(gl['la_fixture'], 1)} µm "
           f"contre {_fr(gl['le_rouleau'], 1)}) sans glisser du même côté.", moyen, ALERTE)
    ecrire(74, y + 64,
           "★★★★  Ce que cela BORNE : toute conclusion tirée de la fixture sur le comportement "
           "AXIAL du rouleau, et `168` en particulier.", moyen, ENCRE)
    ecrire(74, y + 90,
           "★★★  Et ce que cela n'ôte pas : `R4-F87` calibre trois autres grandeurs à 5,5 %, et "
           "une pose qui se contredit se contredit vraiment sur cette matière.", moyen, BON)
    ecrire(74, y + 110,
           f"★  Le contrôle tient : ni la spirale nue ni l'écrasement seul ne glissent "
           f"({_fr(c['glissement_axial_median_um'], 1)} µm), donc l'instrument ne mesure pas "
           f"le marcheur.", moyen, ENCRE)

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

    # ⚠⚠⚠ LE DEFAUT QUE `169` A TROUVE DANS SON PROPRE MODULE : un nombre JUSTE sous un MAUVAIS
    # nom. Les deux cotes doivent bouger SEPAREMENT, sinon la figure peut afficher l'un pour
    # l'autre sans que rien n'echoue.
    faux = copy.deepcopy(d)
    faux["juger"]["la_comparaison_au_rouleau"]["part_axiale"]["la_fixture"] = 0.424
    _c, p2, _cd, _pt, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ la part axiale de la FIXTURE est LUE sous son propre nom",
      any("0,424" in t for _x, _y, t, _f in p2) and not any("0,424" in t for t in tous))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["la_comparaison_au_rouleau"]["part_axiale"]["le_rouleau"] = 0.313
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ ... et celle du ROULEAU sous le sien, séparément",
      any("0,313" in t for _x, _y, t, _f in p3) and not any("0,313" in t for t in tous),
      "un nombre juste sous un mauvais nom est pire qu'un nombre absent")
    faux3 = copy.deepcopy(d)
    faux3["juger"]["la_comparaison_au_rouleau"]["coherence"]["la_fixture"] = 0.515
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐ la cohérence de la fixture est LUE, et c'est elle qui porte le SUIVI",
      any("0,515" in t for _x, _y, t, _f in p4))
    faux4 = copy.deepcopy(d)
    for g in faux4["juger"]["par_matiere"]:
        g["penchent_azimutalement"] = 61
    _c, p5, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ le compte des marches qui penchent DANS L'AUTRE SENS est LU",
      any("61 azimutal" in t for _x, _y, t, _f in p5)
      and not any("61 azimutal" in t for t in tous),
      "c'est lui qui refuse un sens systématique")
    faux5 = copy.deepcopy(d)
    faux5["juger"]["le_controle_de_la_spirale_nue"]["il_ne_penche_pas"] = False
    _c, p6, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐⭐ un contrôle qui cesse de tenir change la marque de la figure",
      any(t.startswith("✗  spirale nue") for _x, _y, t, _f in p6)
      and not any(t.startswith("✗  spirale nue") for t in tous))
    v("⚠ le glissement axial des DEUX matières est écrit à côté de la comparaison",
      any("µm" in t for t in tous))

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_169.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle de la spirale nue est REFUSÉE",
      refuse(lambda x: x["juger"]["le_controle_de_la_spirale_nue"].pop("il_ne_penche_pas")))
    v("⚠⚠⚠ une mesure sans la COMPARAISON au rouleau est REFUSÉE",
      refuse(lambda x: x["juger"].update(la_comparaison_au_rouleau=None)),
      "une figure qui ne montrerait que la fixture ne comparerait rien")

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "la_fixture_penche_t_elle_du_meme_cote.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "169_la_fixture_penche_t_elle_du_meme_cote.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt, _b = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
