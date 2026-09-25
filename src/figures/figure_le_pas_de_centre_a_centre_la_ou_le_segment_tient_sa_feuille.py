"""Le pas de centre à centre sur un second bloc : ce que la pile montre, et ce que le pas retrouve d'une même rampe.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LA PILE COUPÉE EN TRAVERS sur le second bloc : la publiée, le
segment réduit à la maille, la spire produite ; les feuilles y ondulent sur moins d'un chunk. En bas à gauche, CE QUE
CHAQUE PAS RETROUVE D'UNE MÊME RAMPE NUMÉRIQUE, sur le bloc de `257` et sur celui-ci : de centre à centre, de 1,25 à 0,06.
En bas à droite, où est la feuille selon `m7` et selon la couche la plus claire.

  uv run python src/figures/figure_le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.py \\
      --sortie docs/images/259_le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.json"
CELLE_DE_258 = RACINE / "docs" / "mesures" / "le_pas_de_centre_a_centre_voit_il_la_rampe.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 900
LES_COUPES = (("la publiée", "la_publiee"), ("le segment réduit à la maille", "le_segment_reduit"),
              ("la spire produite", "la_spire_produite"))


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
    d["_258"] = json.loads(CELLE_DE_258.read_text())
    return d


def les_rampes(d: dict) -> list[tuple[str, str, float]]:
    a, n, p = d["_258"]["la_rampe_numerique"], d["la_rampe_numerique"], d["la_pile_publiee"]["la_rampe_numerique"]
    return [("le bloc de 257, segment réduit", "de centre à centre", a["de_centre_a_centre"]["la_pente"]),
            ("le bloc de 257, segment réduit", "à la couture", a["a_la_couture"]["la_pente"]),
            ("ce bloc, segment réduit", "de centre à centre", n["de_centre_a_centre"]["la_pente"]),
            ("ce bloc, segment réduit", "à la couture", n["a_la_couture"]["la_pente"]),
            ("ce bloc, pile publiée", "de centre à centre", p["de_centre_a_centre"]["la_pente"]),
            ("ce bloc, pile publiée", "à la couture", p["a_la_couture"]["la_pente"])]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : le pas de centre à centre transporte-t-il d'un bloc à l'autre ?"""
    r = [x[2] for x in les_rampes(d) if x[1] == "de centre à centre"]
    if min(r) < 0.5 <= max(r):
        return (f"D'UNE MÊME RAMPE, LE PAS DE CENTRE À CENTRE RETROUVE DE {_fr(min(r), 4)} À {_fr(max(r), 4)} SELON LE BLOC : "
                f"IL NE TRANSPORTE PAS")
    return f"D'UNE MÊME RAMPE, LE PAS DE CENTRE À CENTRE RETROUVE DE {_fr(min(r), 4)} À {_fr(max(r), 4)} SELON LE BLOC"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"coupes": 0, "barres": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    b = d["le_bloc"]
    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"20230702185753 · le bloc de la règle : rangée {b['la_rangee']}, colonne {b['la_colonne']}, où m7 voit le "
                   f"segment en {_fr(b['la_part_ou_m7_voit_le_segment'], 4)} des points ; {b['les_rates']} ratés jugés sur "
                   f"{b['les_points_notes']} · rampe numérique de 24 voxels", petit, GRIS)

    # ── PANNEAU 1 · LES COUPES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 1310, 470, f"LA PILE COUPÉE EN TRAVERS, À LA RANGÉE {d['les_coupes']['la_rangee_du_bloc']} DU BLOC "
                               f"(LE MILIEU, EN OCRE, EST LA SURFACE)")
    y = 112
    for nom, cle in LES_COUPES:
        coupe = d["les_coupes"].get(cle)
        ecrire(66, y + 44, nom, 0, ENCRE)
        if coupe:
            h, w = len(coupe), len(coupe[0])
            im = Image.new("L", (w, h))
            im.putdata([int(v) for r in coupe for v in r])
            im = im.resize((w * 4, h), Image.NEAREST)
            img.paste(im.convert("RGB"), (250, y))
            art.line([246, y + h // 2, 254 + w * 4, y + h // 2], fill=ALERTE, width=1)
            points.append((254 + w * 4, y + h))
            traces["coupes"] += 1
        y += 120

    # ── PANNEAU 2 · LES RAMPES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 486, 860, 780, "CE QUE CHAQUE PAS RETROUVE D'UNE MÊME RAMPE : UN, TOUT ; ZÉRO, RIEN")
    bx0, bx1, P = 440, 780, 1.4
    y = 522
    for k, (qui, pas, pente) in enumerate(les_rampes(d)):
        if k % 2 == 0:
            ecrire(66, y, qui, 0, ENCRE)
        ecrire(300, y, pas, 0, GRIS)
        w = (bx1 - bx0) * max(0.0, min(P, pente)) / P
        art.rectangle([bx0, y + 2, bx0 + w, y + 14], fill=BON if pas.startswith("de centre") else ALERTE)
        points.append((bx0 + w, y + 14))
        ecrire(bx0 + w + 8, y, _fr(pente, 4), 0, ENCRE)
        traces["barres"] += 1
        y += 22 if k % 2 == 0 else 40
    for val, lib in ((0.5, "un demi"), (1.0, "tout")):
        x = bx0 + (bx1 - bx0) * val / P
        art.line([x, 516, x, y - 24], fill=GRIS, width=1)
        ecrire(x - 18, y - 20, lib, 0, GRIS)

    # ── PANNEAU 3 · OÙ EST LA FEUILLE ──────────────────────────────────────────────────────────────────────────────
    panneau(880, 486, 1310, 780, "OÙ EST LA FEUILLE, SUR CE BLOC")
    f_r, f_p = d["la_feuille_dans_la_pile_du_segment"], d["la_pile_publiee"]["la_feuille_dans_la_pile"]
    lignes = (("m7 voit le segment à 12 voxels près", b["la_part_ou_m7_voit_le_segment"]),
              ("pile publiée : couche claire à ¼ de pas", f_p["la_part_a_moins_dun_quart_de_pas"]),
              ("segment réduit : couche claire à ¼ de pas", f_r["la_part_a_moins_dun_quart_de_pas"]))
    y = 526
    for nom, val in lignes:
        ecrire(896, y, nom, 0, ENCRE)
        art.rectangle([896, y + 20, 896 + 300 * float(val), y + 32], fill=BON if nom.startswith("m7") else ALERTE)
        points.append((896 + 300 * float(val), y + 32))
        traces["barres"] += 1
        ecrire(1204, y + 18, _fr(val, 4), 0, ENCRE)
        y += 60
    ecrire(896, 712, "les deux mesures ne s'accordent pas : la couche", 0, GRIS)
    ecrire(896, 730, "la plus claire d'un chunk n'est pas, ici, un repère", 0, GRIS)
    ecrire(896, 748, "de la feuille que le segment suit", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 796, L_, H_], fill=BANDE)
    ecrire(50, 810, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 834, "★ d'un bloc à l'autre, le pas de centre à centre ne retrouve pas la même rampe : ce n'est pas un "
                    "instrument.", moyen, ENCRE)
    ecrire(50, 860, "⚠ ce qui n'est PAS établi : la pile publiée a été ajoutée après la première mesure ; deux blocs "
                    "seulement ; un côté ; m7.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_259.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    r = [x[2] for x in les_rampes(d) if x[1] == "de centre à centre"]
    v("★★★ le titre LIT la mesure", _fr(min(r), 4) in le_titre(d) and _fr(max(r), 4) in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ les trois piles ont leur coupe", traces["coupes"] == 3)
    v("★★★★ six pentes et trois parts ont leur barre", traces["barres"] == 9, str(traces["barres"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le bloc de 257 pour comparer, et ce qui n'est PAS établi",
      "le bloc de 257" in txt and "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "images" / "259_le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
