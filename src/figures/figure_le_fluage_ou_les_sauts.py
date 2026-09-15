"""La dérive est-elle un fluage ou des sauts ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle : sur la spirale nue
aucun pas ne saute, donc la décomposition ne mesure pas son propre bruit. En haut à droite, ce que le
repliement cache — la dérive repliée contre l'exacte, matière par matière. En bas à gauche, la part
des pas qui franchissent une feuille. En bas à droite, les marches : combien n'ont AUCUN saut, et sur
combien les sauts l'emportent sur le fluage.

  uv run python src/figures/figure_le_fluage_ou_les_sauts.py \\
      --json docs/mesures/le_fluage_ou_les_sauts.json \\
      --sortie docs/images/160_le_fluage_ou_les_sauts.png
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


def lire(chemin: Path) -> dict:
    """Le JSON de `le_fluage_ou_les_sauts.py`.

    ⚠⚠ Refuse une mesure sans le contrôle de la spirale nue : c'est lui qui autorise à lire le
    reste, et une figure dessinée sans lui ressemble exactement à une figure qui l'aurait.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucune matière jugée")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_tient") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    return d


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

    j = d["juger"]
    mat = j["par_matiere"]
    c = j["le_controle_de_la_spirale_nue"]

    ecrire(28, 20, "La dérive est-elle un fluage ou des sauts ? La question de `158`, "
                   "posable depuis `159`", gros, ENCRE)
    ecrire(28, 46, "un pas dont la phase EXACTE franchit plus d'une DEMI-feuille a changé de "
                   "feuille — même énoncé que le demi-pas de la contrainte et la demi-épaisseur "
                   "du rejet, et sans aucun seuil", petit, GRIS)

    # ---- panneau 1 : le controle
    x0, y0, pw, ph = 56, 122, 620, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle : là où l'instrument est exact, rien ne saute", moyen, ENCRE)
    marque = "★" if c["il_tient"] else "✗"
    ecrire(x0 + 14, y0 + 24, f"{marque}  {c['nom']}", moyen, BON if c["il_tient"] else ALERTE)
    ecrire(x0 + 14, y0 + 56, f"pas qui sautent : {c['pas_qui_sautent']}", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 82,
           f"marches sans aucun saut : {c['marches_sans_aucun_saut']} sur {c['decidables']}",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + ph - 96,
           "`159` y mesure zéro pas replié à tort, donc la décomposition", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 80,
           "doit y rendre zéro saut. Une décomposition qui en trouverait", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 64,
           "là mesurerait son propre bruit, et tout le reste du tableau", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 48, "ne voudrait rien dire.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 24,
           f"la matière qui saute le plus : « {_court(j['la_matiere_qui_saute_le_plus'])} »",
           petit, ALERTE)

    # ---- panneau 2 : repliee contre exacte
    x0, y0, pw, ph = 712, 122, 592, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que le repliement cache — dérive médiane, en feuilles", moyen, ENCRE)
    vmax = max(m["derive_exacte_mediane"] for m in mat) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 132
    barre_max = pw - 300
    for k, m in enumerate(mat):
        yy = y0 + 24 + k * 42
        ecrire(x_nom, yy + 8, _court(m["nom"]), petit, ENCRE)
        for dec, val, coul in ((0, m["derive_repliee_mediane"], TEMOIN),
                               (14, m["derive_exacte_mediane"], ALERTE)):
            w = (val / vmax) * barre_max
            art.rectangle([x_barre, yy + dec, x_barre + max(w, 1), yy + dec + 11], fill=coul)
            points.append((x_barre + w, yy + dec + 5))
        ecrire(x_barre + barre_max + 10, yy + 8,
               f"{m['derive_repliee_mediane']:g} → {m['derive_exacte_mediane']:g}", petit,
               ALERTE if m["derive_exacte_mediane"] > m["derive_repliee_mediane"] else GRIS)
    ecrire(x0 + 12, y0 + ph - 32, "gris : la dérive REPLIÉE · ambre : l'EXACTE", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 16,
           "les deux coïncident là où rien ne saute, et divergent là où ça saute", petit, ENCRE)

    # ---- panneau 3 : la part des pas qui sautent
    x0, y0, pw, ph = 56, 428, 620, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la part des pas qui franchissent une feuille", moyen, ENCRE)
    parts = [(m["pas_qui_sautent"] / m["pas_marches"] if m["pas_marches"] else 0.0) for m in mat]
    pmax = max(parts) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 132
    barre_max = pw - 300
    for k, (m, p) in enumerate(zip(mat, parts)):
        yy = y0 + 28 + k * 36
        w = (p / pmax) * barre_max
        coul = BON if m["pas_qui_sautent"] == 0 else ALERTE
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
        points.append((x_barre + w, yy + 7))
        ecrire(x_nom, yy + 2, _court(m["nom"]), petit, ENCRE)
        ecrire(x_barre + barre_max + 10, yy + 2,
               f"{m['pas_qui_sautent']}/{m['pas_marches']}", petit, coul)
    ecrire(x0 + 12, y0 + ph - 32,
           "vert : aucun pas ne saute · ambre : au moins un", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 16,
           "le compte croît avec la difficulté, et il est NUL sur la spirale nue", petit, ENCRE)

    # ---- panneau 4 : les marches
    x0, y0, pw, ph = 712, 428, 592, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les marches : combien ne sautent jamais", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 132
    barre_max = pw - 300
    for k, m in enumerate(mat):
        yy = y0 + 28 + k * 36
        dec = max(m["decidables"], 1)
        w = (m["marches_sans_aucun_saut"] / dec) * barre_max
        coul = BON if m["marches_sans_aucun_saut"] == m["decidables"] else ALERTE
        art.rectangle([x_barre, yy, x_barre + barre_max, yy + 14], fill=TRAIT)
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
        points.append((x_barre + w, yy + 7))
        ecrire(x_nom, yy + 2, _court(m["nom"]), petit, ENCRE)
        ecrire(x_barre + barre_max + 10, yy + 2,
               f"{m['marches_sans_aucun_saut']}/{m['decidables']}", petit, coul)
    ecrire(x0 + 12, y0 + ph - 48,
           "la barre pleine : les marches SANS AUCUN saut", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 32,
           f"sur la grille entière : {j['marches_sans_aucun_saut']} marches sur "
           f"{j['decidables']} ne sautent jamais,", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 16,
           f"et les sauts l'emportent sur le fluage dans {j['marches_ou_les_sauts_lemportent']}.",
           petit, ALERTE)

    # ---- bande de conclusion
    y = 700
    art.rectangle([56, y, L - 56, y + 122], fill=BANDE)
    cadres.append((56, y, L - 56, y + 122))
    dure = next(m for m in mat if m["nom"] == j["la_matiere_qui_saute_le_plus"])
    ecrire(74, y + 12,
           f"★★★★  Ni l'un ni l'autre partout : la spirale NUE ne saute pas d'un seul pas sur "
           f"{mat[0]['pas_marches']}, et la matière du rouleau en saute "
           f"{dure['pas_qui_sautent']}.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★  {j['marches_sans_aucun_saut']} marches sur {j['decidables']} ne sautent JAMAIS, "
           f"et les sauts l'emportent sur {j['marches_ou_les_sauts_lemportent']}. Le saut est le "
           f"régime des matières dures, pas la règle.", moyen, BON)
    ecrire(74, y + 64,
           f"⚠  Et le repliement cache la dérive exactement là : "
           f"{dure['derive_repliee_mediane']:g} au lieu de "
           f"{dure['derive_exacte_mediane']:g} feuilles sur la matière du rouleau.",
           moyen, ALERTE)
    ecrire(74, y + 90,
           "⚠⚠  Donc « corriger le transfert de spire à spire » n'est pas une correction ponctuelle "
           "sur ces matières : c'est le pas lui-même qui change de feuille.", moyen, ENCRE)

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
    faux["juger"]["le_controle_de_la_spirale_nue"]["pas_qui_sautent"] = 8888
    faux["juger"]["le_controle_de_la_spirale_nue"]["il_tient"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ un contrôle qui TOMBE change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    for m in faux2["juger"]["par_matiere"]:
        m["derive_exacte_mediane"] = 77.77
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et la dérive exacte est LUE, pas supposée",
      any("77.77" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    faux3["juger"]["marches_ou_les_sauts_lemportent"] = 333
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐ ... et le compte des marches où les sauts l'emportent aussi",
      any("333" in t for _x, _y, t, _f in p4))

    sans = copy.deepcopy(d)
    del sans["juger"]["le_controle_de_la_spirale_nue"]
    tmp = sortie.parent / "_sans_controle_160.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans le contrôle de la spirale nue est REFUSÉE", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures" / "le_fluage_ou_les_sauts.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "160_le_fluage_ou_les_sauts.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
