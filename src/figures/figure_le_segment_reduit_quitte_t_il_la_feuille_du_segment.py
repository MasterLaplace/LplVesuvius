"""Sur le voisinage de (160, 160), ce que le segment réduit s'écarte du segment, contre ce que sa marche en lit.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux cartes du voisinage, à la même échelle de couleur : à gauche, l'écart du
segment réduit au segment, pure géométrie ; à droite, la marche du segment réduit moins son ancre (`272`). Les 13 chunks que la
décision corrige sont cernés. La carte de gauche est blanche partout, celle de droite ne l'est pas sous ces chunks. À droite de
la figure, chunk par chunk, les deux valeurs l'une à côté de l'autre.

  uv run python src/figures/figure_le_segment_reduit_quitte_t_il_la_feuille_du_segment.py \\
      --sortie docs/images/273_le_segment_reduit_quitte_t_il_la_feuille_du_segment.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)
from figure_laquelle_des_deux_marches_porte_lecart import VIDE, la_teinte  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
M = RACINE / "docs" / "mesures"
LA_MESURE = M / "le_segment_reduit_quitte_t_il_la_feuille_du_segment.json"
DE_272 = M / "laquelle_des_deux_marches_porte_lecart.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
L_, H_ = 1360, 620
LE_BLOC = 16


def _fr(x, n: int = 2) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def _carte(a: list) -> np.ndarray:
    return np.array([[np.nan if x is None else float(x) for x in r] for r in a])


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    d["_272"] = json.loads(DE_272.read_text())["les_voisinages"]["160_160"]
    return d


def les_deux_cartes(d: dict) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int]]]:
    """L'écart géométrique, la marche du segment réduit moins son ancre, et les chunks corrigés, sur le voisinage."""
    v = d["_272"]
    geo = _carte(d["les_voisinages"]["160_160"]["lecart_aux_chunks"])
    marche = _carte(v["la_marche_du_segment_reduit"]) - v["les_ancres_voxels"]["le_segment_reduit"]
    return geo, marche, [(int(i), int(j)) for i, j in v["les_chunks_decides"]]


def le_titre(d: dict) -> str:
    f = d["les_voisinages"]["160_160"]["les_chunks_corriges"]
    return (f"SOUS LES {f['les_chunks']} CHUNKS CORRIGÉS DE (160, 160), LE SEGMENT RÉDUIT EST À "
            f"{_fr(f['lecart_abs_median_voxels'])} VOXELS DU SEGMENT, ET SA MARCHE EN LIT "
            f"{_fr(d['_272']['juges_justes']['la_part_du_segment_reduit_mediane_voxels'])}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(15, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cernes": 0, "paires": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 50, "20230702185753 · le segment réduit : un point sur huit du segment, bilinéaire entre ses points gardés · "
                   "l'écart le long de la normale du segment, médiane par chunk", petit, GRIS)
    geo, marche, dec = les_deux_cartes(d)
    cel = 6
    panneau(50, 76, 700, 480, "LE VOISINAGE DE (160, 160), À LA MÊME ÉCHELLE")
    for m, (a, titre) in enumerate(((geo, "le segment réduit moins le segment"),
                                    (marche, "la marche du segment réduit, moins son ancre"))):
        x0, y0 = 70 + 320 * m, 136
        ecrire(x0, y0 - 22, titre, 0, ENCRE)
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                art.rectangle([x0 + j * cel, y0 + i * cel, x0 + (j + 1) * cel - 1, y0 + (i + 1) * cel - 1],
                              fill=la_teinte(a[i, j]))
        b0, b1 = LE_BLOC * cel, 2 * LE_BLOC * cel
        art.rectangle([x0 + b0 - 1, y0 + b0 - 1, x0 + b1, y0 + b1], outline=ENCRE)
        for i, j in dec:
            cx, cy = x0 + (LE_BLOC + j) * cel, y0 + (LE_BLOC + i) * cel
            art.rectangle([cx, cy, cx + cel - 1, cy + cel - 1], outline=ENCRE)
            traces["cernes"] += 1
    for s, (lib, v) in enumerate((("−80", -80.0), ("0", 0.0), ("+80", 80.0))):
        xs = 70 + 90 * s
        art.rectangle([xs, 440, xs + 24, 454], fill=la_teinte(v), outline=TRAIT)
        ecrire(xs + 30, 440, lib, 0, GRIS)
    art.rectangle([340, 440, 364, 454], fill=VIDE, outline=TRAIT)
    ecrire(370, 440, "rien à lire", 0, GRIS)

    # ── CHUNK PAR CHUNK ────────────────────────────────────────────────────────────────────────────────────────────
    panneau(720, 76, 1310, 480, "LES 13 CHUNKS CORRIGÉS, VOXELS")
    gx0, gx1 = 760, 1290
    GX = lambda x: gx0 + (gx1 - gx0) * (max(-30.0, min(90.0, x)) + 30.0) / 120.0  # noqa: E731
    for t in (-18, 0, 18, 36, 72):
        art.line([GX(t), 120, GX(t), 420], fill=TRAIT)
        ecrire(GX(t) - 8, 424, _fr(t), 0, GRIS)
    for k, (i, j) in enumerate(sorted(dec)):
        y = 132 + 22 * k
        g = geo[LE_BLOC + i, LE_BLOC + j]
        w = abs(marche[LE_BLOC + i, LE_BLOC + j])
        art.line([GX(g), y, GX(w), y], fill=TRAIT)
        art.ellipse([GX(g) - 4, y - 4, GX(g) + 4, y + 4], fill=ENCRE)
        art.ellipse([GX(w) - 4, y - 4, GX(w) + 4, y + 4], fill=ALERTE)
        traces["paires"] += 1
    ecrire(736, 448, "● le segment réduit moins le segment", 0, ENCRE)
    ecrire(1010, 448, "● la marche du segment réduit, en valeur absolue", 0, ALERTE)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    t_ = d["tous_les_chunks"]
    art.rectangle([0, 496, L_, H_], fill=BANDE)
    ecrire(50, 508, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 530, f"★ sur les {t_['les_chunks']} chunks des trois voisinages, le segment réduit n'est à un quart de pas ou "
                    f"plus du segment que dans {_fr(100 * t_['la_part_au_quart_de_pas_ou_plus'])} % d'entre eux.", moyen, ENCRE)
    ecrire(50, 556, "⚠ ce qui n'est PAS établi : pourquoi la marche lit mal ici ; si la spire produite coupe des plis ; que le "
                    "rendu interpole en bilinéaire.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_273.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    f = d["les_voisinages"]["160_160"]["les_chunks_corriges"]
    v("★★★ le titre LIT la mesure", f"EST À {_fr(f['lecart_abs_median_voxels'])} VOXELS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    geo, marche, dec = les_deux_cartes(d)
    v("★★★★ chaque chunk corrigé est cerné sur les deux cartes et a sa paire de points",
      traces["cernes"] == 2 * len(dec) and traces["paires"] == len(dec) == f["les_chunks"], str(traces))
    sous = np.array([geo[LE_BLOC + i, LE_BLOC + j] for i, j in dec])
    v("★★★★ la carte dessinée redonne la médiane publiée sous les chunks corrigés",
      abs(float(np.median(np.abs(sous))) - f["lecart_abs_median_voxels"]) < 0.01, f"{np.median(np.abs(sous))}")
    v("★★★ aucune paire n'est écrasée contre un bord de son échelle",
      all(-30 < geo[LE_BLOC + i, LE_BLOC + j] < 90 and abs(marche[LE_BLOC + i, LE_BLOC + j]) < 90 for i, j in dec))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "273_le_segment_reduit_quitte_t_il_la_feuille_du_segment.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
