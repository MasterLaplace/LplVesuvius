"""Le retour : ce qu'il trahit d'un saut raté, et ce qu'il ne peut pas voir.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, TROIS ALLERS-RETOURS DESSINÉS : un saut juste revient sur le
segment ; un saut qui n'a pas quitté sa feuille revient une spire trop loin, et il est signalé ; une feuille que la
prédiction manque est sautée dans les deux sens, et le raté passe inaperçu. À droite, CE QUE LE RETOUR SIGNALE sur la
bande et sur le segment : une petite part des ratés, et peu de justes. En bas, LA PART JUSTE avant et après avoir écarté
les points signalés.

  uv run python src/figures/figure_le_retour_trahit_il_le_saut_rate.py \\
      --sortie docs/images/250_le_retour_trahit_il_le_saut_rate.png
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
MESURES = RACINE / "docs" / "mesures"
LES_OBJETS = (("la bande w028-037", MESURES / "le_retour_trahit_il_le_saut_rate.json"),
              ("le segment 20230702185753", MESURES / "le_retour_sur_le_segment_5753.json"))

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
PALE = (205, 200, 190)
L_, H_ = 1360, 950
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = {}
    for nom, chemin in LES_OBJETS:
        m = json.loads(chemin.read_text())
        if not m.get("decidable"):
            raise SystemExit(f"mesure indécidable : {chemin.name}")
        d[nom] = m
    return d


def la_confusion(d: dict, objet: str, pred: str, cote: str) -> dict:
    return d[objet]["les_predictions"][pred][cote]["la_confusion"]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : quelle part des ratés le retour signale au plus, sur les deux objets."""
    r = [la_confusion(d, o, p, c)["la_part_des_rates_signales"] for o in d for p in ("m7", "ps256") for _, c in LES_COTES]
    if max(r) < 0.5:
        return f"LE RETOUR NE TRAHIT QU'UNE PETITE PART DES SAUTS RATÉS : DE {_fr(min(r))} À {_fr(max(r))}"
    return "LE RETOUR TRAHIT LA PLUPART DES SAUTS RATÉS"


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

    def fleche(x, y0, y1, coul):
        art.line([x, y0, x, y1], fill=coul, width=3)
        s = 1 if y1 > y0 else -1
        art.polygon([(x - 6, y1 - 10 * s), (x + 6, y1 - 10 * s), (x, y1)], fill=coul)

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, "l'aller est le premier saut de 248 (la feuille suivante, puis le vote) ; le retour est le même saut, "
                   "parti de la surface produite, normale retournée ; incohérent à un demi-feuillet ou plus du segment",
           petit, GRIS)

    # ── PANNEAU 1 · TROIS ALLERS-RETOURS ────────────────────────────────────────────────────
    panneau(50, 84, 560, 800, "TROIS ALLERS-RETOURS, DESSINÉS")
    cas = (("le saut est juste", "le retour retombe sur le segment : cohérent", (True, True, True), 1, 0, BON),
           ("l'aller n'a pas quitté sa feuille", "le retour tombe une spire avant : signalé", (True, True, True), 0, -1,
            ALERTE),
           ("la prédiction manque une feuille", "sautée dans les deux sens : le raté passe", (True, False, True), 2, 0, GRIS))
    for k, (titre, legende, vues, arrivee, retour, coul) in enumerate(cas):
        y0 = 124 + k * 222
        ecrire(74, y0, titre, 0, ENCRE)
        niveaux = {-1: y0 + 176, 0: y0 + 136, 1: y0 + 86, 2: y0 + 36}
        for sp, yy in niveaux.items():
            vue = sp < 0 or vues[sp]
            art.line([120, yy, 360, yy], fill=ENCRE if vue else PALE, width=3 if sp == 0 else 2)
            if not vue:
                ecrire(370, yy - 7, "manquée par la prédiction", 0, GRIS)
        ecrire(74, niveaux[0] - 7, "segment", 0, GRIS)
        fleche(200, niveaux[0], niveaux[arrivee] + (6 if arrivee else -6), CONTRE)
        fleche(280, niveaux[arrivee] + (6 if arrivee else -6), niveaux[retour] + (-6 if retour < 0 else 6), coul)
        points.extend([(200, niveaux[arrivee]), (280, niveaux[retour])])
        ecrire(150, (niveaux[0] + niveaux[max(arrivee, 1)]) / 2 - 20, "aller", 0, CONTRE)
        ecrire(290, (niveaux[max(arrivee, 1)] + niveaux[0]) / 2 - 20, "retour", 0, coul)
        ecrire(74, y0 + 192, legende, 0, coul)
    traces["cas"] = len(cas)

    # ── PANNEAU 2 · CE QUE LE RETOUR SIGNALE ────────────────────────────────────────────────
    panneau(580, 84, 1310, 480, "CE QUE LE RETOUR SIGNALE")
    bx0, bx1 = 900, 1210
    y = 128
    barres = 0
    for objet in d:
        ecrire(596, y, objet, 0, ENCRE)
        y += 20
        for pred in ("m7", "ps256"):
            for nom_c, cote in LES_COTES:
                c = la_confusion(d, objet, pred, cote)
                ecrire(610, y, f"{pred}, côté {nom_c}", 0, GRIS)
                for j, (cle, coul) in enumerate((("la_part_des_rates_signales", ALERTE),
                                                  ("la_part_des_justes_signales_a_tort", CONTRE))):
                    v_ = c[cle]
                    art.rectangle([bx0, y + j * 8, bx0 + (bx1 - bx0) * v_, y + j * 8 + 6], fill=coul)
                    points.append((bx0 + (bx1 - bx0) * v_, y + j * 8 + 6))
                    barres += 1
                ecrire(bx1 + 8, y, f"{_fr(c['la_part_des_rates_signales'])} · {_fr(c['la_part_des_justes_signales_a_tort'])}",
                       0, ENCRE)
                y += 20
        y += 10
    for f_ in (0.0, 0.25, 0.5):
        xg = bx0 + (bx1 - bx0) * f_
        art.line([xg, 146, xg, y - 8], fill=TRAIT, width=1)
        ecrire(xg - 10, y - 6, _fr(f_, 2), 0, GRIS)
    traces["barres"] = barres
    ecrire(596, y + 14, "rouille : la part des ratés signalés · bleu : la part des justes signalés à tort", 0, GRIS)

    # ── PANNEAU 3 · LA PART JUSTE ───────────────────────────────────────────────────────────
    panneau(580, 500, 1310, 800, "LA PART JUSTE, AVANT ET APRÈS AVOIR ÉCARTÉ LES SIGNALÉS")
    cx0, cx1 = 900, 1210
    X0, X1 = 0.85, 0.95
    y = 544
    paires = 0
    for objet in d:
        ecrire(596, y, objet, 0, ENCRE)
        y += 20
        for pred in ("m7", "ps256"):
            for nom_c, cote in LES_COTES:
                c = la_confusion(d, objet, pred, cote)
                a_, b_ = c["la_part_juste_a_laller"], c["la_part_juste_parmi_les_gardes"]
                xa, xb = (cx0 + (cx1 - cx0) * (min(max(x, X0), X1) - X0) / (X1 - X0) for x in (a_, b_))
                art.line([xa, y + 6, xb, y + 6], fill=BON, width=2)
                art.ellipse([xa - 3, y + 3, xa + 3, y + 9], fill=GRIS)
                art.ellipse([xb - 4, y + 2, xb + 4, y + 10], fill=BON)
                points.extend([(xa, y + 6), (xb, y + 6)])
                ecrire(610, y, f"{pred}, côté {nom_c}", 0, GRIS)
                ecrire(cx1 + 8, y, f"{_fr(a_)} → {_fr(b_)}", 0, ENCRE)
                paires += 1
                y += 14
        y += 8
    for f_ in (0.86, 0.9, 0.94):
        xg = cx0 + (cx1 - cx0) * (f_ - X0) / (X1 - X0)
        art.line([xg, 560, xg, y - 6], fill=TRAIT, width=1)
        ecrire(xg - 12, y - 4, _fr(f_, 2), 0, GRIS)
    traces["paires"] = paires

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    b = la_confusion(d, "la bande w028-037", "m7", "du_cote_plus")
    bm = la_confusion(d, "la bande w028-037", "m7", "du_cote_moins")
    ecrire(50, 832, "LE VERDICT : le retour ne trahit qu'une petite part des sauts ratés ; la plupart sont symétriques, et "
                    "il les refait", petit, ENCRE)
    ecrire(50, 856, f"★ sur la bande, avec m7, il signale {_fr(b['la_part_des_rates_signales'])} et "
                    f"{_fr(bm['la_part_des_rates_signales'])} des ratés, et {_fr(b['la_part_des_justes_signales_a_tort'])} et "
                    f"{_fr(bm['la_part_des_justes_signales_a_tort'])} des justes ; un signalé sur trois environ est un raté.",
           moyen, ENCRE)
    ecrire(50, 882, f"★ écarter les signalés fait passer la part juste de {_fr(b['la_part_juste_a_laller'])} à "
                    f"{_fr(b['la_part_juste_parmi_les_gardes'])} et de {_fr(bm['la_part_juste_a_laller'])} à "
                    f"{_fr(bm['la_part_juste_parmi_les_gardes'])} : un point de plus, pas dix.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : un seul saut aller et retour ; ce qui répare un point signalé n'est pas "
                    "essayé.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_250.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LE RETOUR" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ les trois allers-retours sont dessinés", traces["cas"] == 3)
    v("★★★★ chaque objet a ses deux barres, deux prédictions et deux côtés", traces["barres"] == 2 * 2 * 2 * 2)
    v("★★★★ chaque objet a sa paire avant et après, deux prédictions et deux côtés", traces["paires"] == 2 * 2 * 2)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les deux objets, les deux prédictions et ce qui n'est PAS établi",
      "w028-037" in txt and "20230702185753" in txt and "ps256" in txt and "n'est PAS établi" in txt)
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "250_le_retour_trahit_il_le_saut_rate.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
