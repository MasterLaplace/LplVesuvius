"""Jusqu'où une mâchoire peut être juste, et où elle y est déjà.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le résultat : le rapport de ce que
l'instrument rend à l'échelle de ce qu'il doit moyenner, segment contre croix. Sous la ligne, il bat
la variation qu'il couvre ; au-dessus, il reste quelque chose à prendre. En haut à droite, les deux
axes de la mâchoire à la demi-largeur de référence, et le zéro EXACT du second sur les matières
lisses. En bas à gauche, la variation contre la distance, avec la demi-largeur et la longueur d'onde
en repère. En bas à droite, l'étalement des appuis, qui ordonne les matières sans en donner le niveau.

  uv run python src/figures/figure_jusquou_une_machoire_peut_elle_etre_juste.py \\
      --json docs/mesures/jusquou_une_machoire_peut_elle_etre_juste.json \\
      --sortie docs/images/154_jusquou_une_machoire_peut_elle_etre_juste.png
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
COURBES = ((150, 152, 156), (120, 124, 130), (196, 160, 60), (176, 120, 60), (176, 60, 42))


def lire(chemin: Path) -> dict:
    """Le JSON de `jusquou_une_machoire_peut_elle_etre_juste.py`.

    ⚠⚠ Refuse une mesure dont le jugement est indécidable : sans la mesure de `153` il n'y a rien à
    comparer, et une figure qui dessinerait les deux moitiés restantes ressemblerait exactement à
    une figure complète.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    for cle in ("variation", "etalement"):
        if not d.get(cle, {}).get("decidable"):
            raise ValueError(f"{chemin} : « {cle} » est indécidable")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if "sur_la_matiere_du_rouleau" not in j:
        raise ValueError(f"{chemin} : la matière du rouleau est absente du jugement")
    if not j.get("etalement_a_la_largeur_de_reference"):
        raise ValueError(f"{chemin} : l'étalement à la largeur de référence est absent")
    return d


def _court(nom: str) -> str:
    return nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1340, 900
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    v, e, j = d["variation"], d["etalement"], d["juger"]
    dur = j["sur_la_matiere_du_rouleau"]

    ecrire(28, 20, "Jusqu'où une mâchoire peut être juste, et où elle y est déjà", gros, ENCRE)
    ecrire(28, 46, f"{v['poses_par_case']} poses par case · l'échelle est la variation de la VRAIE "
                   f"normale sur le patch, analytique et gratuite · erreurs LUES dans `153`",
           petit, GRIS)

    # ---- panneau 1 : LE RESULTAT, le rapport instrument sur echelle
    x0, y0, pw, ph = 60, 122, 600, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que l'instrument rend, divisé par l'échelle qu'il doit moyenner",
           moyen, ENCRE)
    lignes = [x for x in j["par_matiere"]
              if x["le_segment_au_dessus_de_son_echelle"] is not None]
    mx = max(max(x["le_segment_au_dessus_de_son_echelle"],
                 x["la_croix_au_dessus_de_son_echelle"] or 0.0) for x in lignes) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 200
    un = x_barre + barre_max / mx
    for k, x in enumerate(lignes):
        yy = y0 + 28 + k * 46
        for dec, cle, coul in ((0, "le_segment_au_dessus_de_son_echelle", GRIS),
                               (15, "la_croix_au_dessus_de_son_echelle", None)):
            val = x[cle]
            if val is None:
                continue
            w = (val / mx) * barre_max
            c = coul if coul is not None else (BON if val < 1.0 else ALERTE)
            art.rectangle([x_barre, yy + dec, x_barre + max(w, 1), yy + dec + 13], fill=c)
            points.append((x_barre + w, yy + dec + 6))
        ecrire(x_nom, yy + 6, _court(x["nom"]), petit, ENCRE)
        s_ = x["le_segment_au_dessus_de_son_echelle"]
        c_ = x["la_croix_au_dessus_de_son_echelle"]
        ecrire(x_barre + 6, yy - 12, f"segment {s_:.2f}×   croix {c_:.2f}×", petit,
               BON if c_ < 1.0 else ALERTE)
    art.line([un, y0 + 20, un, y0 + ph - 42], fill=ENCRE, width=1)
    ecrire(x0 + 12, y0 + ph - 30, "le trait vertical est UN : à gauche l'instrument bat la "
                                  "variation qu'il couvre, à droite il reste à prendre",
           petit, GRIS)

    # ---- panneau 2 : les deux axes a la demi-largeur
    x0, y0, pw, ph = 700, 122, 580, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, f"variation de la normale à {v['demi_largeur_de_reference_um']} µm, "
                        f"par axe", moyen, ENCRE)
    mv = max(max(x["variation_le_long_de_t_deg"],
                 x["variation_le_long_de_n_croix_t_deg"] or 0.0)
             for x in j["par_matiere"]) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 224
    for k, x in enumerate(j["par_matiere"]):
        yy = y0 + 28 + k * 46
        for dec, val, coul in ((0, x["variation_le_long_de_t_deg"], GRIS),
                               (15, x["variation_le_long_de_n_croix_t_deg"], ALERTE)):
            if val is None:
                continue
            w = (val / mv) * barre_max
            if w > 0.5:
                art.rectangle([x_barre, yy + dec, x_barre + w, yy + dec + 13], fill=coul)
                points.append((x_barre + w, yy + dec + 6))
            else:
                art.line([x_barre, yy + dec, x_barre, yy + dec + 13], fill=ENCRE, width=2)
        ecrire(x_nom, yy + 6, _court(x["nom"]), petit, ENCRE)
        ecrire(x_barre + 6, yy - 12,
               f"t {x['variation_le_long_de_t_deg']:.2f}°   "
               f"nxt {x['variation_le_long_de_n_croix_t_deg']:.2f}°", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 30, "gris : l'axe du segment · ambre : celui que la croix ajoute · "
                                  "un trait sans barre est un ZÉRO EXACT", petit, GRIS)

    # ---- panneau 3 : la variation contre la distance
    x0, y0, pw, ph = 60, 446, 600, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "variation de la normale le long de t, contre la distance", moyen, ENCRE)
    ds = v["distances_um"]
    n = max(len(ds) - 1, 1)
    vals = [x["le_long_de_t_deg"] for m in v["par_matiere"] for x in m["par_distance"]
            if x["le_long_de_t_deg"] is not None]
    dmax = max(vals) if vals else 1.0

    def px3(i):
        return x0 + 54 + i * (pw - 176) / n

    def py3(val):
        return y0 + ph - 52 - (val / max(dmax, 1e-9)) * (ph - 96)

    for k in range(3):
        vv = dmax * k / 2
        art.line([x0 + 46, py3(vv), x0 + pw - 116, py3(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 8, int(py3(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    art.rectangle([x0 + pw - 114, y0 + 6, x0 + pw - 6, y0 + 12 + 17 * len(v["par_matiere"])],
                  fill=FOND)
    for k, m in enumerate(v["par_matiere"]):
        coul = COURBES[k % len(COURBES)]
        xy = [(px3(i), py3(x["le_long_de_t_deg"])) for i, x in enumerate(m["par_distance"])
              if x["le_long_de_t_deg"] is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
            points.append((a_, b_))
        ecrire(x0 + pw - 110, y0 + 8 + k * 17, _court(m["nom"]), petit, coul)
    for i, val in enumerate(ds):
        if i % 2 == 0 or i == len(ds) - 1:
            ecrire(int(px3(i)) - 14, y0 + ph - 40, f"{val:g}", petit, ENCRE)
    for rang, (cible, nom, coul) in enumerate(
            ((v["demi_largeur_de_reference_um"], "demi-largeur", ALERTE),
             (v["longueur_donde_um"], "longueur d'onde", GRIS))):
        proche = min(range(len(ds)), key=lambda i: abs(ds[i] - cible))
        art.line([px3(proche), y0 + 14, px3(proche), y0 + ph - 46], fill=coul, width=2)
        # ⚠ L'etiquette du repere va EN BAS : ecrite en haut, celle de la longueur d'onde tombait
        # dans la legende, et `textes_qui_se_recouvrent` l'a dit. Elle est aussi calee A GAUCHE du
        # trait quand celui-ci est pres du bord droit, sinon elle sortirait du cadre.
        largeur_du_nom = 7 * len(nom)
        xa = px3(proche) - (largeur_du_nom + 6 if proche > n - 2 else -6)
        # ⚠⚠ Et les deux reperes sont ETAGES : cales chacun a son trait, ils se recouvraient
        # l'un l'autre des que les deux distances sont proches sur l'axe.
        ecrire(int(xa), y0 + ph - 74 + rang * 14, nom, petit, coul)
    ecrire(x0 + 12, y0 + ph - 22, "en µm", petit, GRIS)

    # ---- panneau 4 : l'etalement des appuis
    x0, y0, pw, ph = 700, 446, 580, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalement des appuis ordonne, et ne donne pas le niveau", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 14, f"{'matière':<20}{'D':>9}{'arctan':>9}{'erreur':>10}{'×':>7}",
           petit, GRIS)
    for k, x in enumerate(j["etalement_a_la_largeur_de_reference"]):
        yy = y0 + 42 + k * 34
        r_ = "—" if x["rapport"] is None else f"{x['rapport']:.2f}"
        coul = ENCRE if x["amplitude_um"] == 0.0 else ALERTE
        ecrire(x0 + 14, yy, f"{_court(x['nom']):<20}{x['etalement_um']:>7.2f}µm"
                            f"{x['inclinaison_impliquee_deg']:>8.2f}°"
                            f"{x['erreur_du_segment_deg']:>9.2f}°{r_:>7}", petit, coul)
    ecrire(x0 + 14, y0 + ph - 46,
           "une mâchoire dont les appuis trouvent leur interstice à D l'un de l'autre",
           petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 28,
           "penche d'au moins arctan(D/2w) : l'ordre est juste, le niveau est un facteur deux",
           petit, GRIS)

    # ---- la bande de conclusion, sur son propre cadre RESERVE
    by = 724
    art.rectangle([0, by, L, H], fill=BANDE)
    cadres.append((0, by, L, H))
    ecrire(28, by + 18, "La croix a fini le travail sur les froissements modérés, et pas sur la "
                        "matière du rouleau", moyen, ENCRE)
    ecrire(28, by + 46,
           f"Sur les froissements modérés la croix rend {dur['sur_les_froissements_moderes']} fois "
           f"l'échelle qu'elle doit moyenner, donc elle est SOUS un : aucun instrument de cette "
           f"taille ne peut faire mieux, la seule voie est de rétrécir.", petit, ENCRE)
    ecrire(28, by + 68,
           f"Sur la matière du rouleau elle est à {dur['croix_au_dessus_de_son_echelle']}× son "
           f"échelle : il reste un facteur trois à prendre À TAILLE ÉGALE, donc un défaut "
           f"d'instrument encore à trouver, et ce n'est ni sa taille ni sa dimension.",
           petit, ALERTE)
    ecrire(28, by + 90,
           "Le point bas des matières lisses est ce qui rend ce rapport lisible : un plan ajusté "
           "sur un patch symétrique bat la variation qu'il couvre, donc un rapport de un veut bien "
           "dire « à la limite ».", petit, ENCRE)
    ecrire(28, by + 112,
           "Et le second axe ne porte exactement rien là où la matière est lisse : la croix ne "
           "récupère que ce que le froissement y met.", petit, ENCRE)

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
    v("l'image est écrite et a la taille attendue", img.size == (1340, 900), f"{img.size}")
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

    # ---- ⚠⚠ LES SONDES DÉPLACENT DES CHAMPS QUE LA BANDE LIT VRAIMENT.
    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["sur_la_matiere_du_rouleau"]["croix_au_dessus_de_son_echelle"] = 8.88
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer le rapport de la croix change ce que la bande DIT",
      any("8.88" in t for _x, _y, t, _f in p2)
      and not any("8.88" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["sur_la_matiere_du_rouleau"]["sur_les_froissements_moderes"] = [7.77]
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et changer les froissements modérés aussi",
      any("7.77" in t for _x, _y, t, _f in p3))

    sans = copy.deepcopy(d)
    sans["juger"] = {"decidable": False, "raison": "la mesure de `153` n'est pas lue"}
    tmp = sortie.parent / "_sans_jugement.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans le jugement est REFUSÉE, jamais dessinée à moitié", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures"
                    / "jusquou_une_machoire_peut_elle_etre_juste.json")
    ap.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                    / "154_jusquou_une_machoire_peut_elle_etre_juste.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
