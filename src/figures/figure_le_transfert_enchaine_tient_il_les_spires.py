"""La chaîne de transferts : combien de spires elle tient d'affilée, et où elle décroche.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LA PART SUR LA BONNE SPIRE SAUT APRÈS SAUT, sur les
points de la bande `w028-037` qui ont une couche à chacun des quatre sauts : le pas fixe s'effondre dès le deuxième, la
chaîne décroît sans s'effondrer. En haut à droite, LA PART QUI TIENT LES QUATRE SAUTS D'AFFILÉE, avec les deux
prédictions. En bas, OÙ LA CHAÎNE DÉCROCHE le long de la bande, c'est-à-dire d'une spire à l'autre : un saut raté est
définitif, donc ses creux se creusent d'un saut au suivant au lieu de se déplacer.

  uv run python src/figures/figure_le_transfert_enchaine_tient_il_les_spires.py \\
      --sortie docs/images/248_le_transfert_enchaine_tient_il_les_spires.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "le_transfert_enchaine_tient_il_les_spires.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (150, 185, 170)
CONTRE = (92, 108, 150)
L_, H_ = 1360, 950
LA_PREDICTION = "m7"
LES_PROCEDURES = (("le pas fixe, sans lire", "le_temoin_sans_lecture", CONTRE, 2),
                  ("le compte sur un rayon", "le_compte_sur_un_rayon", GRIS, 2),
                  ("la chaîne, normale du segment", "la_chaine_le_long_de_la_normale_du_segment", PALE, 2),
                  ("la chaîne", "la_chaine", BON, 4))
LES_COTES = (("côté plus", "du_cote_plus"), ("côté moins", "du_cote_moins"))
LE_TAS = 40   # les colonnes de la maille regroupées en un point du profil
LE_MINIMUM = 50   # un tas de moins de mailles jugées n'est pas tracé : sa part ne dirait rien


def _fr(x, n: int = 3) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = json.loads(LA_MESURE.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_courbe(d: dict, cote: str, cle: str, prediction: str = LA_PREDICTION) -> list[float]:
    """La part sur la bonne spire à chaque saut, sur les points notés à chaque saut, lue et jamais recalculée."""
    return d["les_predictions"][prediction][cote]["sur_les_points_notes_a_chaque_saut"][cle]


def qui_tient(d: dict, cote: str, cle: str, prediction: str = LA_PREDICTION) -> float:
    return d["les_predictions"][prediction][cote]["qui_tient"][cle]["la_part_qui_tient_tous_les_sauts"]


def le_profil(lignes: list[str], tas: int = LE_TAS) -> tuple[list[float | None], dict]:
    """La part des mailles sur la bonne spire, colonne par colonne de la carte, par tas de `tas` colonnes."""
    larg = max(len(l_) for l_ in lignes)
    v = [0] * larg
    x = [0] * larg
    for l_ in lignes:
        for j, ch in enumerate(l_):
            if ch == "v":
                v[j] += 1
            elif ch == "x":
                x[j] += 1
    out = []
    for a in range(0, larg, tas):
        nv, nx = sum(v[a:a + tas]), sum(x[a:a + tas])
        out.append(nv / (nv + nx) if nv + nx >= LE_MINIMUM else None)
    return out, {"v": sum(v), "x": sum(x)}


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la chaîne contre le pas fixe, sur les quatre sauts d'affilée."""
    a = [qui_tient(d, c, "la_chaine") for _, c in LES_COTES]
    b = [qui_tient(d, c, "le_temoin_sans_lecture") for _, c in LES_COTES]
    if min(a) > max(b):
        return (f"LA CHAÎNE TIENT QUATRE SPIRES D'AFFILÉE SUR {_fr(a[0])} ET {_fr(a[1])} DES POINTS, "
                f"UN PAS FIXE SUR {_fr(b[0])} ET {_fr(b[1])}")
    return "LA CHAÎNE NE TIENT PAS MIEUX QU'UN PAS FIXE"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    pr = d["les_predictions"][LA_PREDICTION]
    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"{d['le_segment']}, rangées {_fr(d['les_rangees'][0], 2)} à {_fr(d['les_rangees'][1], 2)} · juge : la "
                   f"h-ième couche que la bande porte elle-même · prédiction {LA_PREDICTION} à 9,6 µm · "
                   f"{pr['du_cote_plus']['sur_les_points_notes_a_chaque_saut']['les_points']} et "
                   f"{pr['du_cote_moins']['sur_les_points_notes_a_chaque_saut']['les_points']} points notés à chaque saut",
           petit, GRIS)

    # ── PANNEAU 1 · SAUT APRÈS SAUT ──────────────────────────────────────────────────────────
    panneau(50, 84, 790, 560, "LA PART SUR LA BONNE SPIRE, SAUT APRÈS SAUT · les mêmes points à chaque saut")
    Y0, Y1 = 0.4, 1.0
    courbes = 0
    for c, (nom_c, cote) in enumerate(LES_COTES):
        gx0, gx1, gy0, gy1 = 96 + c * 350, 360 + c * 350, 150, 470
        ecrire(gx0, 124, nom_c, 0, ENCRE)
        art.line([gx0, gy1, gx1, gy1], fill=TRAIT, width=1)
        for f_ in (0.4, 0.6, 0.8, 1.0):
            yg = gy1 - (gy1 - gy0) * (f_ - Y0) / (Y1 - Y0)
            art.line([gx0, yg, gx1, yg], fill=TRAIT, width=1)
            ecrire(gx0 - 34, yg - 7, _fr(f_, 1), 0, GRIS)
        sauts = len(la_courbe(d, cote, "la_chaine"))
        for h in range(sauts):
            xs = gx0 + (gx1 - gx0) * h / (sauts - 1)
            ecrire(xs - 3, gy1 + 6, str(h + 1), 0, GRIS)
        for nom, cle, coul, ep in LES_PROCEDURES:
            ys = la_courbe(d, cote, cle)
            pts = [(gx0 + (gx1 - gx0) * h / (len(ys) - 1), gy1 - (gy1 - gy0) * (y - Y0) / (Y1 - Y0))
                   for h, y in enumerate(ys)]
            art.line(pts, fill=coul, width=ep)
            for p in pts:
                art.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=coul)
                points.append(p)
            courbes += 1
        ecrire(gx0, gy1 + 24, "saut", 0, GRIS)
    traces["courbes"] = courbes
    for k, (nom, cle, coul, _) in enumerate(LES_PROCEDURES):
        xl, yl = 74 + (k % 2) * 330, 510 + (k // 2) * 20
        art.rectangle([xl, yl + 3, xl + 14, yl + 11], fill=coul)
        ecrire(xl + 22, yl, nom, 0, ENCRE)

    # ── PANNEAU 2 · QUI TIENT LES QUATRE SAUTS ───────────────────────────────────────────────
    panneau(810, 84, 1310, 560, "QUI TIENT LES QUATRE SAUTS D'AFFILÉE")
    BX0, BX1 = 1036, 1206
    y = 128
    barres = 0
    for pred in ("m7", "ps256"):
        ecrire(826, y, f"prédiction {pred}", 0, ENCRE)
        y += 22
        for nom, cle, coul, _ in LES_PROCEDURES:
            ecrire(840, y + 2, nom, 0, GRIS)
            vals = [qui_tient(d, c, cle, pred) for _, c in LES_COTES]
            for c, v_ in enumerate(vals):
                yy = y + c * 9
                art.rectangle([BX0, yy, BX0 + (BX1 - BX0) * v_, yy + 7], fill=coul)
                points.append((BX0 + (BX1 - BX0) * v_, yy + 7))
                barres += 1
            ecrire(BX1 + 8, y + 2, f"{_fr(vals[0])} · {_fr(vals[1])}", 0, ENCRE)
            y += 26
        y += 18
    for f_ in (0.25, 0.5, 0.75, 1.0):
        xg = BX0 + (BX1 - BX0) * f_
        art.line([xg, 146, xg, y - 14], fill=TRAIT, width=1)
        ecrire(xg - 10, y - 10, _fr(f_, 2), 0, GRIS)
    traces["barres"] = barres
    ecrire(826, y + 14, "deux barres par procédure : côté plus, côté moins", 0, GRIS)
    pas = pr["du_cote_moins"]["qui_tient"]["la_chaine"]["parmi_ceux_qui_ont_tenu_le_saut_precedent"]
    ecrire(826, y + 36, "la chaîne, saut par saut, parmi ceux qui ont tenu le précédent (côté moins) :", 0, ENCRE)
    ecrire(826, y + 54, " · ".join(_fr(x) for x in pas), 0, ENCRE)

    # ── PANNEAU 3 · OÙ LA CHAÎNE DÉCROCHE ────────────────────────────────────────────────────
    panneau(50, 580, 1310, 800, "OÙ LA CHAÎNE DÉCROCHE LE LONG DE LA BANDE · côté moins, de la première colonne à la "
                                "dernière, donc de spire en spire")
    cartes = pr["du_cote_moins"]["les_cartes_de_la_chaine"]
    px0, px1, py0, py1 = 96, 1180, 620, 770
    art.line([px0, py1, px1, py1], fill=TRAIT, width=1)
    for f_ in (0.4, 0.7, 1.0):
        yg = py1 - (py1 - py0) * (f_ - Y0) / (Y1 - Y0)
        art.line([px0, yg, px1, yg], fill=TRAIT, width=1)
        ecrire(px0 - 34, yg - 7, _fr(f_, 1), 0, GRIS)
    comptes = []
    teintes = (PALE, (105, 150, 130), (80, 128, 108), BON)
    for h, lignes in enumerate(cartes):
        prof, n = le_profil(lignes)
        comptes.append(n)
        seg = []
        for k, y_ in enumerate(prof):
            if y_ is None:
                if len(seg) > 1:
                    art.line(seg, fill=teintes[h], width=1 + h)
                seg = []
                continue
            p = (px0 + (px1 - px0) * k / max(len(prof) - 1, 1),
                 py1 - (py1 - py0) * (max(y_, Y0) - Y0) / (Y1 - Y0))
            seg.append(p)
            points.append(p)
        if len(seg) > 1:
            art.line(seg, fill=teintes[h], width=1 + h)
        ecrire(px1 + 16, 626 + h * 20, f"saut {h + 1}", 0, teintes[h] if h else GRIS)
    traces["comptes"] = comptes
    ecrire(px0, py1 + 8, f"chaque point du profil : {LE_TAS} colonnes de la maille, s'il en porte au moins {LE_MINIMUM} jugées ; "
                         f"sous 0,4, le tracé est posé sur 0,4",
           0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ch = [la_courbe(d, c, "la_chaine") for _, c in LES_COTES]
    tm = [la_courbe(d, c, "le_temoin_sans_lecture") for _, c in LES_COTES]
    ecrire(50, 832, "LE VERDICT : enchaîner la feuille suivante et le vote tient la spire saut après saut, et le pas fixe "
                    "s'effondre dès le deuxième", petit, ENCRE)
    ecrire(50, 856, f"★ au quatrième saut, la chaîne est sur la bonne spire en {_fr(ch[0][-1])} et {_fr(ch[1][-1])} des "
                    f"points, le pas fixe en {_fr(tm[0][-1])} et {_fr(tm[1][-1])} ; recalculer la normale ne coûte rien.",
           moyen, ENCRE)
    r1 = pr["du_cote_moins"]["les_rates_de_la_chaine"][0]
    ecrire(50, 882, f"★ chaque saut perd encore une part de ceux qui ont tenu le précédent ; au premier, "
                    f"{_fr(r1['trop_pres_dont_la_ou_la_bande_saute_plus_dun_pas_et_demi'])} des chutes trop près tombent là "
                    f"où la bande saute plus d'un pas et demi.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : une seule bande, quatre sauts ; aucune spire n'est produite en maillage, et "
                    "un tour que la bande n'a pas tracé fausse son juge.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d = lire()
    tmp = sortie.parent / ".sonde_248.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LA CHAÎNE TIENT" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    # ⚠⚠⚠ LE PROFIL DOIT DIRE CE QUE LA MESURE DIT : ses mailles vertes, rapportées aux mailles jugées, rendent la
    # part que la mesure publie pour la chaîne, à chaque saut.
    rs = d["les_predictions"][LA_PREDICTION]["du_cote_moins"]["les_sauts"]
    for h, n in enumerate(traces["comptes"]):
        part = rs[h]["la_chaine"]["la_part_sur_la_bonne_spire"]
        v(f"★★★★ le profil du saut {h + 1} rend la part publiée", round(n["v"] / (n["v"] + n["x"]), 4) == part,
          f"{n} contre {part}")
    v("★★★★ chaque procédure a sa courbe, des deux côtés", traces["courbes"] == 2 * len(LES_PROCEDURES))
    v("★★★★ chaque procédure a ses deux barres, avec les deux prédictions", traces["barres"] == 2 * len(LES_PROCEDURES) * 2)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le juge, les deux prédictions et ce qui n'est PAS établi",
      "h-ième couche" in txt and "ps256" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "248_le_transfert_enchaine_tient_il_les_spires.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
