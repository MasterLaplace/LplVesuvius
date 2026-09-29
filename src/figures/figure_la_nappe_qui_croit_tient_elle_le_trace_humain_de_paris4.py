"""La nappe qui croît de 305 sur PHercParis4 : la part des sommets du tracé humain qu'elle tient, par distance à sa graine, contre la nappe du vote de 321, et l'histogramme de ses écarts au tracé.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, graine par graine, trois barres : la part des sommets du segment en face de
la nappe qui croît qui sont à un quart de pas d'elle, près de la graine, à mi-distance et au bord du plan ; un trait noir marque, pour
le même anneau, la part de la nappe du vote de `321`. Si les barres dépassent les traits au bord, refuser le saut tient la feuille là
où le vote la perdait. À droite, l'histogramme des écarts de la nappe qui croît.

  uv run python src/figures/figure_la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.py \\
      --sortie docs/images/322_la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.png

⚠ Tout vient des mesures de `322` et de `321`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.json"
LA_MESURE_321 = RACINE / "docs" / "mesures" / "la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
LES_TEINTES = ((40, 84, 66), (96, 150, 124), (170, 206, 186))
PALE = (226, 236, 230)
L_, H_ = 1360, 660
LA_BANDE = 570
LE_MINIMUM_PAR_ANNEAU = 10
LES_LECTURES = {"tient jusqu'au bord": "tient", "ne tient pas": "ne tient pas", "n'atteint pas le bord": "n'y arrive pas"}


def lire(chemin: Path = LA_MESURE, chemin_321: Path = LA_MESURE_321) -> dict:
    d = json.loads(chemin.read_text())
    d["la_nappe_du_vote"] = {g["le_rang"]: g["la_nappe"]["par_anneau"] for g in json.loads(chemin_321.read_text())["les_graines"]}
    return d


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].split(" ; ")[0].upper()


def les_reperes_attendus(d: dict) -> list:
    return [(g["le_rang"], k, a["la_part_sur_la_feuille_du_trace"]) for g in d["les_graines"]
            for k, a in enumerate(d["la_nappe_du_vote"][g["le_rang"]]) if a["les_sommets_en_face"] >= LE_MINIMUM_PAR_ANNEAU]


def les_barres_attendues(d: dict) -> list:
    return [(g["le_rang"], k, a["la_part_sur_la_feuille_du_trace"]) for g in d["les_graines"]
            for k, a in enumerate(g["la_nappe"]["par_anneau"]) if a["les_sommets_en_face"] >= LE_MINIMUM_PAR_ANNEAU]


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "reperes": [], "histogrammes": [], "ecretes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "PHercParis4, m7 au niveau 2 (9,6 µm), la nappe qui croît de 305 depuis les graines de 321 ; un sommet est sur la "
                   "feuille du tracé s'il est à un quart de pas (18 voxels de 2,4 µm) de la nappe", petit, GRIS)

    x0, y0, x1, y1 = 50, 76, 660, 550
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des sommets en face sur la feuille du tracé ; trait noir : la nappe du vote", moyen, ENCRE)
    for k, (nom, col) in enumerate(zip(("0 à 2 sommets", "3 à 5", "6 à 8 (bord du plan)"), LES_TEINTES)):
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
        for k, a in enumerate(g["la_nappe"]["par_anneau"]):
            if a["les_sommets_en_face"] < LE_MINIMUM_PAR_ANNEAU:
                continue
            p = a["la_part_sur_la_feuille_du_trace"]
            if not 0.0 <= p <= 1.0:
                traces["ecretes"] += 1
            p = min(1.0, max(0.0, p))
            bx = xa + k * (lw - 14) / 3
            art.rectangle([bx, gy1 - p * (gy1 - gy0), bx + (lw - 14) / 3 - 3, gy1], fill=LES_TEINTES[k])
            traces["barres"].append((g["le_rang"], k, a["la_part_sur_la_feuille_du_trace"]))
        for k, a in enumerate(d["la_nappe_du_vote"][g["le_rang"]]):
            if a["les_sommets_en_face"] < LE_MINIMUM_PAR_ANNEAU:
                continue
            q = a["la_part_sur_la_feuille_du_trace"]
            if not 0.0 <= q <= 1.0:
                traces["ecretes"] += 1
            q = min(1.0, max(0.0, q))
            bx = xa + k * (lw - 14) / 3
            art.line([bx - 2, gy1 - q * (gy1 - gy0), bx + (lw - 14) / 3 - 1, gy1 - q * (gy1 - gy0)], fill=ENCRE, width=3)
            traces["reperes"].append((g["le_rang"], k, a["la_part_sur_la_feuille_du_trace"]))
        ecrire(int(xa), gy1 + 6, f"g{g['le_rang']}", 0, ENCRE)
        lec = LES_LECTURES[g["au_bord"]]
        ecrire(int(xa), gy1 + 22 + (r % 2) * 14, lec, 0, BON if lec == "tient" else GRIS)

    x0, y0, x1, y1 = 690, 76, 1310, 550
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "l'écart signé du tracé à la nappe qui croît, de −162 à +162 voxels", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 30, "vert pâle : à un quart de pas ; traits : zéro et un pas de chaque côté", 0, GRIS)
    colonnes, pw, ph = 4, 142, 190
    for r, g in enumerate(graines):
        px = x0 + 16 + (r % colonnes) * (pw + 10)
        py = y0 + 56 + (r // colonnes) * (ph + 16)
        h = g["la_nappe"]["lhistogramme"]
        n = len(h)
        bw = (pw - 4) / n
        art.rectangle([px + 2 + 8 * bw, py + 18, px + 2 + 10 * bw, py + ph - 4], fill=PALE)
        haut = max(h) if max(h) else 1
        for b, c in enumerate(h):
            art.rectangle([px + 2 + b * bw, py + ph - 4 - c / haut * (ph - 26), px + 2 + (b + 1) * bw - 1, py + ph - 4],
                          fill=BON)
        for e in (5, 9, 13):
            art.line([px + 2 + e * bw, py + 18, px + 2 + e * bw, py + ph - 4], fill=ALERTE if e != 9 else ENCRE)
        art.rectangle([px, py + 16, px + pw, py + ph - 2], outline=TRAIT)
        ecrire(px + 2, py, f"g{g['le_rang']} : {sum(h)} sommets", 0, ENCRE)
        traces["histogrammes"].append((g["le_rang"], sum(h)))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que la nappe qui croît vaille sur PHerc0358 ; ni pourquoi, sur la graine 4, "
                              "elle part sous le tracé.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE, mesure_321: Path = LA_MESURE_321) -> int:
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

    d = lire(mesure, mesure_321)
    tmp = sortie.parent / ".sonde_322.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "sur 2 des 8 x ; y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SUR 2 DES 8 X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une barre par graine et par anneau lu, à la part mesurée", traces["barres"] == les_barres_attendues(d))
    v("★★★ un trait par graine et par anneau lu de la nappe du vote, à la part mesurée par 321",
      traces["reperes"] == les_reperes_attendus(d))
    v("★★★★ les traits viennent de la mesure de 321, pas de celle de 322",
      d["la_nappe_du_vote"] == {g["le_rang"]: g["la_nappe"]["par_anneau"]
                                for g in json.loads(mesure_321.read_text())["les_graines"]})
    v("★★★ aucune barre ni aucun trait n'est écrêté", traces["ecretes"] == 0, str(traces["ecretes"]))
    v("★★★ un histogramme par graine, à son compte mesuré",
      traces["histogrammes"] == [(g["le_rang"], sum(g["la_nappe"]["lhistogramme"])) for g in d["les_graines"]])
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
                   / "322_la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--mesure-321", type=Path, default=LA_MESURE_321)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure, a.mesure_321)
    chemin, *_ = dessiner(lire(a.mesure, a.mesure_321), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
