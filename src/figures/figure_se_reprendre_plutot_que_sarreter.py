"""Se reprendre plutôt que s'arrêter.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle : sur la spirale nue
les trois marcheurs livrent EXACTEMENT la même chose. En haut à droite, les trois livrables du bras
livré, matière par matière. En bas à gauche, le croisement bras × matière, parce qu'un verdict par
matière met les deux bras en commun. En bas à droite, ce que la reprise récupère et ce qu'elle perd.

  uv run python src/figures/figure_se_reprendre_plutot_que_sarreter.py \\
      --json docs/mesures/se_reprendre_plutot_que_sarreter.json \\
      --sortie docs/images/165_se_reprendre_plutot_que_sarreter.png
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
CONTRE = (92, 108, 150)
MARCHEURS = (("sourd", TEMOIN), ("sarrete", CONTRE), ("se_reprend", BON))
LISIBLE = {"sourd": "sourd", "sarrete": "s'arrête", "se_reprend": "se reprend"}


def lire(chemin: Path) -> dict:
    """Le JSON de `se_reprendre_plutot_que_sarreter.py`.

    ⚠⚠ Refuse une mesure sans le contrôle, et sans le CROISEMENT bras × matière : sans lui le
    tableau par matière se lirait seul, et il met les deux bras en commun.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_identique") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    if not j.get("matieres_ou_la_reprise_lemporte_par_bras"):
        raise ValueError(f"{chemin} : le croisement bras × matière est absent")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    j = d["juger"]
    bras, mat = j["par_bras"], j["par_matiere"]
    c = j["le_controle_de_la_spirale_nue"]
    croise = j["matieres_ou_la_reprise_lemporte_par_bras"]

    ecrire(28, 20, "Se reprendre plutôt que s'arrêter — ce que `164` laissait ouvert", gros, ENCRE)
    ecrire(28, 46, "une pose qui se contredit peut ARRÊTER la marche, ou la faire halver son "
                   "avance et RÉESSAYER : l'idiome que le dépôt emploie depuis `142`", petit, GRIS)

    # ---- panneau 1 : le controle
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle : une IDENTITÉ, pas une absence", moyen, ENCRE)
    marque = "★" if c["il_est_identique"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{marque}  {c['nom']}", moyen, BON if c["il_est_identique"] else ALERTE)
    ecrire(x0 + 14, y0 + 54,
           f"{c['departs_identiques']} départs sur {c['apparies']} où les TROIS marcheurs",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 72, "livrent exactement le même nombre de pas", petit, ENCRE)
    ecrire(x0 + 14, y0 + 96, f"{c['reprises']} reprise déclenchée", petit, ENCRE)
    ecrire(x0 + 14, y0 + ph - 96,
           "c'est plus dur qu'un compte d'arrêts à zéro : un seul pas de", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 80,
           "différence le fait tomber. Là où rien ne se contredit, la", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 64,
           "reprise ne doit rien changer — sinon elle mesurerait son", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 48, "propre bruit.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 22,
           "la boucle s'épuise seule : sous le voxel, plus d'avance exprimable", petit, ALERTE)

    # ---- panneau 2 : les trois livrables du bras livre
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois livrables, bras par bras — pas UTILISABLES", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 108
    barre_max = pw - 216
    vmax = max(g[m]["utilisable"] for g in bras for m, _ in MARCHEURS) or 1
    for k, g in enumerate(bras):
        base = y0 + 28 + k * 86
        ecrire(x_nom, base - 18, _court(g["nom"]), petit, ENCRE)
        for i, (m, coul) in enumerate(MARCHEURS):
            yy = base + i * 20
            t = g[m]
            w = (t["utilisable"] / vmax) * barre_max
            ecrire(x_nom, yy - 1, LISIBLE[m], 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 13], fill=coul)
            points.append((x_barre + w, yy + 6))
            ecrire(x_barre + barre_max + 8, yy - 1,
                   f"{t['utilisable']} · {t['contaminees']}", 0, coul)
    ecrire(x0 + 12, y0 + ph - 38,
           "à droite : pas utilisables · livraisons contaminées", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "la reprise bat les DEUX autres sur le bras livré", petit, ENCRE)

    # ---- panneau 3 : le croisement bras x matiere
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le croisement bras × matière — ★ là où la reprise l'emporte", moyen, ENCRE)
    pas_bloc = max((ph - 84) // max(len(bras), 1), 40)
    for k, g in enumerate(bras):
        base = y0 + 20 + k * pas_bloc
        ecrire(x0 + 12, base, _court(g["nom"]), petit, ENCRE)
        gagnees = croise.get(g["nom"], [])
        for i, m in enumerate(mat):
            yy = base + 20 + i * 18
            gagne = m["nom"] in gagnees
            ecrire(x0 + 30, yy, f"{'★' if gagne else '·'}  {_court(m['nom'])}", 0,
                   BON if gagne else GRIS)
    ecrire(x0 + 12, y0 + ph - 56,
           "un verdict par MATIÈRE met les deux bras en commun, et la pince", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "ne perd AUCUN départ pendant que deux matières en affichent douze", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "et quinze, tous venus de l'autre bras — c'est la leçon de `161`", petit, ALERTE)

    # ---- panneau 4 : recupere contre perd
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce qu'elle récupère, et ce qu'elle perd", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 250
    nmax = max(max(g["reprise_recupere"], g["reprise_perd"]) for g in mat) or 1
    pas_bloc2 = max((ph - 84) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        base = y0 + 22 + k * pas_bloc2
        ecrire(x_nom, base + 6, _court(g["nom"]), petit, ENCRE)
        for i, (cle, coul) in enumerate((("reprise_recupere", BON),
                                         ("reprise_perd", ALERTE))):
            yy = base + i * 15
            n = int(g[cle])
            w = (n / nmax) * barre_max
            if n:
                art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 12], fill=coul)
            points.append((x_barre + w, yy + 6))
        ecrire(x_barre + barre_max + 8, base + 6,
               f"{g['reprise_recupere']} / {g['reprise_perd']}", 0,
               BON if g["reprise_perd"] == 0 else ALERTE)
    ecrire(x0 + 12, y0 + ph - 56,
           "vert : départs récupérés · ambre : départs perdus", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "la reprise continue là où l'arrêt s'arrêtait, donc elle PEUT sauter", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 20,
           "plus loin : une perte est une trajectoire contaminée contre une sûre", petit, ALERTE)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince = bras[0]
    ecrire(74, y + 12,
           f"★★★★  Sur le bras livré, la reprise bat les DEUX autres : "
           f"{pince['se_reprend']['utilisable']} pas utilisables contre "
           f"{pince['sourd']['utilisable']} au marcheur sourd et "
           f"{pince['sarrete']['utilisable']} à celui qui s'arrête.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★★  Et elle ne perd RIEN : {pince['reprise_recupere']} départs récupérés, "
           f"{pince['reprise_perd']} perdu. Les livraisons contaminées tombent de "
           f"{pince['sourd']['contaminees']} à {pince['se_reprend']['contaminees']}.", moyen, BON)
    ecrire(74, y + 64,
           "★★★  Donc s'arrêter n'était pas la bonne réponse : la pose qui se contredit dit "
           "« pas par là », pas « plus jamais ».", moyen, BON)
    ecrire(74, y + 90,
           f"✗  L'autre bras, lui, perd {bras[1]['reprise_perd']} départs : il se reprend "
           f"{bras[1]['reprises']} fois et se contamine quand même.", moyen, ALERTE)
    ecrire(74, y + 110,
           "⚠⚠  Quand la contradiction vient d'un pas allé trop loin, raccourcir la répare ; "
           "quand elle vient de la matière, aucune longueur ne la répare.", moyen, ENCRE)

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
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["le_controle_de_la_spirale_nue"]["departs_identiques"] = 8888
    faux["juger"]["le_controle_de_la_spirale_nue"]["il_est_identique"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐⭐ un contrôle qui TOMBE change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_bras"]:
        g["reprise_perd"] = 7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ ... et le compte des départs PERDUS est LU, pas supposé",
      any("7777" in t for _x, _y, t, _f in p3),
      "c'est le seul axe sur lequel la reprise peut échouer")
    # ⚠⚠⚠ LE CROISEMENT EST LU DU JUGEMENT, jamais recalcule par la figure : deux calculs d'un
    # meme verdict sont deux occasions de ne pas s'accorder.
    faux3 = copy.deepcopy(d)
    faux3["juger"]["matieres_ou_la_reprise_lemporte_par_bras"] = {
        k: [] for k in d["juger"]["matieres_ou_la_reprise_lemporte_par_bras"]}
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le croisement bras × matière est LU du jugement, jamais recalculé",
      sum("★" in t for _x, _y, t, _f in p4) < sum("★" in t for _x, _y, t, _f in poses),
      f"{sum('★' in t for _x, _y, t, _f in p4)} étoiles contre "
      f"{sum('★' in t for _x, _y, t, _f in poses)}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_165.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_controle_de_la_spirale_nue")))
    v("⚠⚠ une mesure sans le CROISEMENT bras × matière est REFUSÉE",
      refuse(lambda x: x["juger"].pop("matieres_ou_la_reprise_lemporte_par_bras")))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "se_reprendre_plutot_que_sarreter.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "165_se_reprendre_plutot_que_sarreter.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
