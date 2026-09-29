"""La spire suivante de la nappe qui croît sur PHercParis4 : la part des sommets du tour suivant du segment qui sont à un quart de pas d'elle, et, graine par graine, la distance d'un sommet du tracé à son vis-à-vis.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, graine par graine, trois barres : la part des sommets du tour suivant du
segment, en face de la surface, qui sont à un quart de pas d'elle, pour la nappe (grise), la spire plus (verte) et la spire moins
(bleue). Si l'une des deux spires monte haut quand la nappe reste basse, la chaîne tombe sur le tour suivant et la comparaison sépare
deux tours. À droite, la distance médiane d'un sommet du tracé à son vis-à-vis, contre le pas du rouleau.

  uv run python src/figures/figure_la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.py \\
      --sortie docs/images/323_la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.png

⚠ Tout vient de la mesure.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
GRIS_BARRE = (178, 180, 184)
L_, H_ = 1360, 600
LA_BANDE = 510
LE_PAS = 72.083
LES_SURFACES = (("la_nappe", "la nappe", GRIS_BARRE), ("la_spire_plus", "spire plus", BON), ("la_spire_moins", "spire moins", BLEU))
LES_LECTURES = {"tombe sur le tour suivant": "tombe", "ne tombe pas sur le tour suivant": "ne tombe pas", "non lue": "non lue"}
LA_DISTANCE_MAXIMALE = 120.0


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def les_barres_attendues(d: dict) -> list:
    return [(g["le_rang"], s, g[s]["la_part_a_un_quart_de_pas"]) for g in d["les_graines"] for s, _, _ in LES_SURFACES
            if g[s]["la_lecture"] != "non lue"]


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "distances": [], "ecretes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "PHercParis4 : la nappe qui croît de 322 et ses deux spires par le saut qui croît de 306 ; le tour suivant est "
                   "l'ensemble des vis-à-vis de 296 des sommets du tracé autour de la graine", petit, GRIS)

    x0, y0, x1, y1 = 50, 76, 900, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des sommets du tour suivant à un quart de pas de la surface (sous 50 en face : non lue)",
           moyen, ENCRE)
    for k, (_, nom, col) in enumerate(LES_SURFACES):
        lx = x0 + 12 + k * 150
        art.rectangle([lx, y0 + 34, lx + 12, y0 + 46], fill=col)
        ecrire(lx + 18, y0 + 33, nom, 0, GRIS)
    gy0, gy1 = y0 + 70, y1 - 50
    art.line([x0 + 10, gy0, x1 - 10, gy0], fill=TRAIT)
    art.line([x0 + 10, (gy0 + gy1) // 2, x1 - 10, (gy0 + gy1) // 2], fill=TRAIT)
    ecrire(x0 + 12, gy0 + 2, "100 %", 0, GRIS)
    ecrire(x0 + 12, (gy0 + gy1) // 2 + 2, "50 %", 0, GRIS)
    graines = d["les_graines"]
    lw = (x1 - x0 - 70) / max(1, len(graines))
    for r, g in enumerate(graines):
        xa = x0 + 60 + r * lw
        for k, (s, _, col) in enumerate(LES_SURFACES):
            bx = xa + k * (lw - 14) / 3
            if g[s]["la_lecture"] == "non lue":
                ecrire(int(bx + 4), gy1 - 16, "–", 0, GRIS)
                continue
            p = g[s]["la_part_a_un_quart_de_pas"]
            if not 0.0 <= p <= 1.0:
                traces["ecretes"] += 1
            p = min(1.0, max(0.0, p))
            art.rectangle([bx, gy1 - p * (gy1 - gy0), bx + (lw - 14) / 3 - 3, gy1], fill=col)
            traces["barres"].append((g["le_rang"], s, g[s]["la_part_a_un_quart_de_pas"]))
        ecrire(int(xa), gy1 + 6, f"g{g['le_rang']}", 0, ENCRE)
        lec = LES_LECTURES[g["la_lecture"]]
        ecrire(int(xa), gy1 + 22 + (r % 2) * 14, lec, 0, BON if lec == "tombe" else GRIS)

    x0, y0, x1, y1 = 930, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "du tracé à son vis-à-vis, en voxels de 2,4 µm", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 30, "distance médiane ; trait : le pas du rouleau, 72,08", 0, GRIS)
    bx0, bx1 = x0 + 50, x1 - 20
    by0 = y0 + 64
    hb = (y1 - 20 - by0) / max(1, len(graines))
    px = bx0 + LE_PAS / LA_DISTANCE_MAXIMALE * (bx1 - bx0)
    art.line([px, by0 - 6, px, y1 - 16], fill=ALERTE, width=2)
    for r, g in enumerate(graines):
        dist = g["la_distance_mediane_au_vis_a_vis_voxels"]
        yb = by0 + r * hb
        ecrire(x0 + 12, int(yb + hb / 2 - 7), f"g{g['le_rang']}", 0, ENCRE)
        if dist is None:
            continue
        if not 0.0 <= dist <= LA_DISTANCE_MAXIMALE:
            traces["ecretes"] += 1
        q = min(LA_DISTANCE_MAXIMALE, max(0.0, dist))
        art.rectangle([bx0, yb + 6, bx0 + q / LA_DISTANCE_MAXIMALE * (bx1 - bx0), yb + hb - 6], fill=GRIS_BARRE)
        traces["distances"].append((g["le_rang"], dist))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : ce que vaut la chaîne au-delà d'un saut, ni sur PHerc0358.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_323.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "sur 2 des 8 x"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SUR 2 DES 8 X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une barre par graine et par surface lue, à la part mesurée", traces["barres"] == les_barres_attendues(d))
    v("★★★ une distance par graine, à la médiane mesurée", traces["distances"] == [
        (g["le_rang"], g["la_distance_mediane_au_vis_a_vis_voxels"]) for g in d["les_graines"]
        if g["la_distance_mediane_au_vis_a_vis_voxels"] is not None])
    v("★★★ rien n'est écrêté", traces["ecretes"] == 0, str(traces["ecretes"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "323_la_spire_qui_croit_tombe_t_elle_sur_le_tour_suivant_du_segment.png")
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
