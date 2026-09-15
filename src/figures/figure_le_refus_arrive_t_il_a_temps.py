"""Le refus arrive-t-il à temps ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle : sur la spirale nue
rien ne saute et aucune règle ne coupe. En haut à droite, le fait — bras par bras, où le PREMIER
refus tombe, en cinq cas exhaustifs. En bas à gauche, la même chose matière par matière, avec
l'étoile là où la victoire JOINTE tient. En bas à droite, le PRIX : les marches propres coupées pour
rien, et ce qu'elles perdent.

  uv run python src/figures/figure_le_refus_arrive_t_il_a_temps.py \\
      --json docs/mesures/le_refus_arrive_t_il_a_temps.json \\
      --sortie docs/images/163_le_refus_arrive_t_il_a_temps.png
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
ENONCES = ("absolu", "relatif", "etalement")
# ⚠ L'ordre des cas est celui du RECIT : ce qui est sauve, ce qui est livre faux, ce qui passe
# inapercu, ce qui est perdu pour rien, ce qui n'est pas touche.
CAS = (("a_temps", BON), ("trop_tard", ALERTE), ("jamais", (120, 40, 40)),
       ("arretee_pour_rien", CONTRE), ("intacte", TRAIT))


def lire(chemin: Path) -> dict:
    """Le JSON de `le_refus_arrive_t_il_a_temps.py`.

    ⚠⚠ Refuse une mesure sans le contrôle de la spirale nue, et sans le verdict par matière.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_vide") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    if "matieres_ou_elle_tient" not in j:
        raise ValueError(f"{chemin} : le verdict par matière est absent")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def _empile(art, points, t, x, y, largeur, hauteur):
    """Une barre empilée des cinq cas — les proportions, jamais un compte déguisé."""
    total = sum(int(t[c]) for c, _ in CAS) or 1
    gauche = float(x)
    for cas, coul in CAS:
        w = int(t[cas]) / total * largeur
        if int(t[cas]):
            art.rectangle([gauche, y, gauche + max(w, 1), y + hauteur], fill=coul)
        points.append((gauche + w, y + hauteur / 2))
        gauche += w


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
    tient = j["matieres_ou_elle_tient"]

    ecrire(28, 20, "Le refus arrive-t-il à temps ? Le prix que `162` laissait à payer", gros, ENCRE)
    ecrire(28, 46, "un refus ne peut qu'ARRÊTER une marche, et il ne se déclenche QU'UNE FOIS : "
                   "la seule question qui décide est où son PREMIER refus tombe", petit, GRIS)

    # ---- panneau 1 : le controle
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle : rien à arrêter, et rien d'arrêté", moyen, ENCRE)
    marque = "★" if c["il_est_vide"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{marque}  {c['nom']}", moyen, BON if c["il_est_vide"] else ALERTE)
    ecrire(x0 + 14, y0 + 54,
           f"{c['marches_qui_sautent']} marche qui saute sur {c['decidables']}", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 82, "et aucune règle n'y coupe une marche :", petit, ENCRE)
    for k, regle in enumerate(ENONCES):
        n = c["marches_coupees"].get(regle)
        ecrire(x0 + 30, y0 + 102 + k * 18,
               f"{regle} : {'—' if n is None else n} marche coupée",
               petit, BON if n == 0 else ALERTE)
    ecrire(x0 + 14, y0 + ph - 78,
           "⚠ `162` jugeait ces règles sur une précision calculée sur la", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 62,
           "marche ENTIÈRE. Or un arrêt ne se déclenche qu'une fois : les", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 46,
           "refus suivants n'arrivent jamais, la marche étant déjà finie.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 22,
           "un taux peut être calculé sur un axe que la règle ne parcourt pas", petit, ALERTE)

    # ---- panneau 2 : ou le PREMIER refus tombe, bras par bras
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "où le PREMIER refus tombe, bras par bras", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 96
    barre_max = pw - 206
    for k, g in enumerate(bras):
        base = y0 + 24 + k * 88
        ecrire(x_nom, base - 16,
               f"{_court(g['nom'])} — {g['marches_qui_sautent']} sautent sur {g['decidables']}",
               petit, ENCRE)
        for i, regle in enumerate(ENONCES):
            t = g.get(regle)
            yy = base + i * 20
            ecrire(x_nom, yy - 1, regle, 0, GRIS)
            if t is None:
                continue
            _empile(art, points, t, x_barre, yy, barre_max, 13)
            ecrire(x_barre + barre_max + 8, yy - 1,
                   f"{t['a_temps']}/{t['a_temps'] + t['trop_tard'] + t['jamais']}", 0,
                   BON if t["jamais"] == 0 else ALERTE)
    ecrire(x0 + 12, y0 + ph - 54,
           "vert : arrêtée À TEMPS · ambre : trop tard · rouge : JAMAIS dite", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 36,
           "bleu : marche propre coupée POUR RIEN · pâle : intacte", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 18,
           "à droite, les marches qui sautent et que la règle a sauvées", petit, ENCRE)

    # ---- panneau 3 : matiere par matiere
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "matière par matière — ★ là où la victoire JOINTE tient", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 220
    pas_bloc = max((ph - 72) // max(len(mat), 1), 36)
    pas_ligne = pas_bloc // 3
    for k, g in enumerate(mat):
        base = y0 + 20 + k * pas_bloc
        ecrire(x_nom, base + pas_ligne, _court(g["nom"]), petit, ENCRE)
        for i, regle in enumerate(ENONCES):
            t = g.get(regle)
            yy = base + i * pas_ligne
            if t is None:
                continue
            gagne = g["nom"] in tient.get(regle, ())
            ecrire(x_barre - 14, yy - 1, "★" if gagne else " ", 0, BON)
            _empile(art, points, t, x_barre, yy, barre_max, pas_ligne - 3)
            ec = t.get("ecart_median")
            ecrire(x_barre + barre_max + 8, yy - 1,
                   "—" if ec is None else f"{ec:+d}", 0, BON if gagne else GRIS)
    ecrire(x0 + 12, y0 + ph - 36,
           "trois barres par matière : absolu, relatif, étalement", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 18,
           "à droite l'écart médian au saut : négatif, la règle arrive AVANT", petit, ENCRE)

    # ---- panneau 4 : le PRIX
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le PRIX — les marches propres coupées pour rien", moyen, ENCRE)
    # ⚠ LA BARRE CEDE LA PLACE AU LIBELLE, pas l'inverse : le libelle porte la PART, qui est le
    # chiffre que ce panneau existe pour dire.
    x_nom, x_barre = x0 + 12, x0 + 120
    barre_max = pw - 330
    pas_bloc2 = max((ph - 72) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        t = g.get("etalement")
        yy = y0 + 26 + k * pas_bloc2
        ecrire(x_nom, yy, _court(g["nom"]), petit, ENCRE)
        if t is None:
            continue
        propres = int(t["arretee_pour_rien"]) + int(t["intacte"])
        w = (int(t["arretee_pour_rien"]) / max(propres, 1)) * barre_max
        art.rectangle([x_barre, yy, x_barre + barre_max, yy + 13], fill=TRAIT)
        if int(t["arretee_pour_rien"]):
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 13], fill=CONTRE)
        points.append((x_barre + w, yy + 6))
        pe = t.get("pas_perdus_median")
        # ⚠⚠ LA PART EST ECRITE A COTE DE LA FRACTION : la fraction seule invite a comparer des
        # NUMERATEURS d'une matiere a l'autre, ce que ce document a paye.
        part = t.get("part_coupee")
        ecrire(x_barre + barre_max + 8, yy,
               f"{t['arretee_pour_rien']}/{propres}"
               + ("" if part is None else f" = {part:g}")
               + ("" if pe is None else f"  -{pe} pas"),
               0, CONTRE if int(t["arretee_pour_rien"]) else BON)
    ecrire(x0 + 12, y0 + ph - 54,
           "la barre ET le nombre : la PART des marches propres coupées, jamais leur compte",
           petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 36,
           "c'est la seule perte SÈCHE : ces marches allaient bien", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 18,
           "et c'est elle, pas les arrêts tardifs, qui fait tomber la victoire", petit, ALERTE)

    # ---- bande de conclusion
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince = bras[0]
    et = pince.get("etalement", {})
    ab = pince.get("absolu", {})
    ecrire(74, y + 12,
           f"★★★★  Sur la pince, l'étalement arrête {et.get('a_temps')} marches sur "
           f"{et.get('a_temps', 0) + et.get('trop_tard', 0) + et.get('jamais', 0)} qui sautent, "
           f"et AUCUNE ne saute en silence.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★  Le déplacement, lui, en laisse {ab.get('jamais')} sauter sans rien dire, et "
           f"quand il parle il arrive {ab.get('ecart_median')} pas trop tard.", moyen, ALERTE)
    ecrire(74, y + 64,
           f"★★★★  Et la victoire JOINTE est GAGNÉE sur une vraie matière : "
           f"{', '.join(_court(n) for n in tient.get('etalement', ()))} — "
           f"arrêtée à temps partout, aucune marche propre perdue.", moyen, BON)
    ecrire(74, y + 90,
           f"✗  Ailleurs c'est le PRIX qui la fait tomber : {et.get('part_coupee')} des marches "
           f"propres de la pince coupées pour rien, pas un arrêt tardif de plus.", moyen, ALERTE)
    ecrire(74, y + 110,
           "⚠⚠  Donc la question n'est plus « la pose le dit-elle » mais « combien de marches "
           "saines accepte-t-on de perdre pour n'en livrer aucune fausse ».", moyen, ENCRE)

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
    faux["juger"]["le_controle_de_la_spirale_nue"]["marches_coupees"]["etalement"] = 8888
    faux["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐⭐ un contrôle qui TOMBE change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_bras"]:
        if g.get("absolu"):
            g["absolu"]["jamais"] = 7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ ... et le compte des pannes SILENCIEUSES est LU, pas supposé",
      any("7777" in t for _x, _y, t, _f in p3),
      "c'est le fait qui sépare l'étalement du déplacement")
    # ⚠⚠⚠ L'ETOILE DE LA VICTOIRE EST LUE DU JUGEMENT, jamais recalculee par la figure : deux
    # calculs d'un meme verdict sont deux occasions de ne pas s'accorder.
    faux3 = copy.deepcopy(d)
    faux3["juger"]["matieres_ou_elle_tient"] = {r: [] for r in ENONCES}
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ l'étoile de la victoire est LUE du jugement, jamais recalculée par la figure",
      sum("★" in t for _x, _y, t, _f in p4) < sum("★" in t for _x, _y, t, _f in poses),
      f"{sum('★' in t for _x, _y, t, _f in p4)} étoiles contre "
      f"{sum('★' in t for _x, _y, t, _f in poses)}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_163.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle de la spirale nue est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_controle_de_la_spirale_nue")))
    v("⚠⚠ une mesure sans le verdict par matière est REFUSÉE",
      refuse(lambda x: x["juger"].pop("matieres_ou_elle_tient")))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures" / "le_refus_arrive_t_il_a_temps.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "163_le_refus_arrive_t_il_a_temps.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
