"""La présence de fibres : pourquoi elle ne départage pas, rayon par rayon, une feuille d'un interstice.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, L'AIRE SOUS LA COURBE des deux témoins pour chaque prédiction de
fibres et chaque côté, avec le rapport à la feuille du segment et sans : toutes tournent autour d'un demi. À droite, LA PART
DES TÉMOINS SANS AUCUNE FIBRE sur la feuille du segment : c'est ce qui rend le rapport instable, surtout pour la seconde
prédiction.

  uv run python src/figures/figure_les_fibres_voient_elles_ce_que_les_predictions_ratent.py \\
      --sortie docs/images/255_les_fibres_voient_elles_ce_que_les_predictions_ratent.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_fibres_voient_elles_ce_que_les_predictions_ratent.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (150, 185, 170)
L_, H_ = 1360, 600
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))
LES_FIBRES = (("fibres du 1er août", "fibres_0801"), ("fibres du 15 septembre", "fibres_0915"))


def _fr(x, n: int = 3) -> str:
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


def les_aires(d: dict) -> list[float]:
    return [x for _, f in LES_FIBRES for _, c in LES_COTES
            for x in (d["les_fibres"][f][c]["le_seuil"]["laire_sous_la_courbe"],
                      d["les_fibres"][f][c]["sans_rapport"]["le_seuil_sur_la_presence_brute"]["laire_sous_la_courbe"])]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : les aires restent-elles toutes près d'un demi ?"""
    a = les_aires(d)
    if max(abs(x - 0.5) for x in a) < 0.1:
        return (f"RAYON PAR RAYON, LA PRÉSENCE DE FIBRES NE SÉPARE PAS UNE FEUILLE D'UN INTERSTICE : AIRES DE "
                f"{_fr(min(a), 4)} À {_fr(max(a), 4)}")
    return "RAYON PAR RAYON, LA PRÉSENCE DE FIBRES SÉPARE UNE FEUILLE D'UN INTERSTICE"


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

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"{d['la_bande']} · présence de fibres au niveau 3 (19,2 µm) · témoins : là où m7 et ps256 s'accordent et "
                   f"sont justes, la chute (une feuille) contre la mi-chemin (un interstice)", petit, GRIS)

    # ── PANNEAU 1 · LES AIRES ────────────────────────────────────────────────────────────────
    panneau(50, 84, 760, 460, "L'AIRE SOUS LA COURBE DES DEUX TÉMOINS, RAYON PAR RAYON")
    bx0, bx1 = 330, 700
    X0, X1 = 0.3, 0.8
    y = 132
    barres = 0
    for nom_f, f in LES_FIBRES:
        ecrire(66, y, nom_f, 0, ENCRE)
        y += 22
        for nom_c, c in LES_COTES:
            x = d["les_fibres"][f][c]
            for nom_r, v_, coul in (("rapportée au segment", x["le_seuil"]["laire_sous_la_courbe"], BON),
                                    ("brute", x["sans_rapport"]["le_seuil_sur_la_presence_brute"]["laire_sous_la_courbe"], PALE)):
                w = (bx1 - bx0) * (v_ - X0) / (X1 - X0)
                art.rectangle([bx0, y + 2, bx0 + w, y + 14], fill=coul)
                points.append((bx0 + w, y + 14))
                ecrire(80, y, f"côté {nom_c}, {nom_r}", 0, GRIS)
                ecrire(bx1 + 8, y, _fr(v_, 4), 0, ENCRE)
                barres += 1
                y += 24
            y += 6
        y += 16
    xg = bx0 + (bx1 - bx0) * (0.5 - X0) / (X1 - X0)
    art.line([xg, 150, xg, y - 10], fill=ALERTE, width=1)
    ecrire(xg - 30, y - 6, "un demi : le hasard", 0, ALERTE)
    traces["barres"] = barres

    # ── PANNEAU 2 · LES TÉMOINS SANS FIBRE ───────────────────────────────────────────────────
    panneau(780, 84, 1310, 460, "LES TÉMOINS SANS AUCUNE FIBRE")
    y = 132
    for nom_f, f in LES_FIBRES:
        ecrire(796, y, nom_f, 0, ENCRE)
        y += 22
        for nom_c, c in LES_COTES:
            sr = d["les_fibres"][f][c]["sans_rapport"]
            ecrire(810, y, f"côté {nom_c} : sur la feuille du segment {_fr(sr['la_part_des_temoins_sans_fibre_sur_le_segment'])}, "
                           f"à la chute {_fr(sr['la_part_des_temoins_sans_fibre_a_la_chute'])}", 0, GRIS)
            y += 22
        y += 16
    m = d["les_fibres"]["fibres_0801"]
    ecrire(796, y + 10, "en moyenne, les témoins se séparent (fibres du 1er août) :", 0, ENCRE)
    for k, (nom_c, c) in enumerate(LES_COTES):
        e = m[c]["en_moyenne"]
        ecrire(810, y + 32 + k * 20, f"côté {nom_c} : feuille {_fr(e['le_temoin_feuille']['le_contraste'])}, interstice "
                                     f"{_fr(e['le_temoin_interstice']['le_contraste'])}", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 478, L_, H_], fill=BANDE)
    ecrire(50, 492, "LE VERDICT : la présence de fibres publiée ne remplace pas la troisième prédiction ; à 19,2 µm, un rayon n'y "
                    "sépare pas une feuille d'un interstice", petit, ENCRE)
    ecrire(50, 516, "★ en moyenne sur des milliers de rayons, elle voit les feuilles ; sur un seul, elle ne dit rien, et les ratés "
                    "communs ne s'y lisent pas.", moyen, ENCRE)
    ecrire(50, 542, "⚠ ce qui n'est PAS établi : seul le niveau 3 est publié ; la mesure sans rapport a été ajoutée après la "
                    "première.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_255.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LA PRÉSENCE DE FIBRES" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque aire a sa barre : deux fibres, deux côtés, deux lectures", traces["barres"] == 8)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les deux prédictions de fibres et ce qui n'est PAS établi",
      "1er août" in txt and "15 septembre" in txt and "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "images" / "255_les_fibres_voient_elles_ce_que_les_predictions_ratent.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
