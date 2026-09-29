"""À quelle distance les points de la nappe qui croît voient la feuille de m7 après la sienne, côté par côté, sur PHerc0358 et sur PHercParis4, avec la distance que le départ du saut a vue.

⚠⚠ **Ce que cette figure doit rendre évident.** Chaque ligne est un côté ; ses douze cases, de 0 à 3 pas par quart de pas, sont d'autant
plus sombres que plus de points de la nappe y voient la feuille suivante. Le trait noir est la médiane, le trait orange ce que le départ
du saut a vu. Une ligne vide est un côté dont aucun point ne voit de feuille suivante ; à droite, la part des points qui en voient une,
et la part des points de la nappe au même décalage : une nappe plate est une nappe posée au même endroit partout.

  uv run python src/figures/figure_a_quelle_distance_m7_montre_t_il_la_feuille_suivante.py \\
      --sortie docs/images/325_a_quelle_distance_m7_montre_t_il_la_feuille_suivante.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "a_quelle_distance_m7_montre_t_il_la_feuille_suivante.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (226, 236, 230)
L_, H_ = 1360, 700
LA_BANDE = 610
LES_ROULEAUX = ("PHerc0358", "PHercParis4")
LE_PAS_MAX = 3.0


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].split(" ; ")[0].upper()


def _fr(x) -> str:
    return "—" if x is None else f"{x:.2f}".replace(".", ",")


def les_lignes_attendues(d: dict) -> list:
    return [(r, c["le_rang"], c["le_cote"], sum(c["lhistogramme"]), c["la_distance_mediane_en_pas"], c["le_depart_en_pas"])
            for r in LES_ROULEAUX for c in d["les_cotes"][r]]


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"lignes": [], "ecretes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par côté, la distance à la première feuille de m7 après celle de la nappe qui croît, de 0 à 3 pas ; trait noir : "
                   "la médiane ; trait orange : ce que le départ du saut a vu", petit, GRIS)
    plates = {r: {n["le_rang"]: n["la_part_a_ce_decalage"] for n in d["les_nappes"][r]} for r in LES_ROULEAUX}
    for k, r in enumerate(LES_ROULEAUX):
        x0, y0 = 50 + k * 640, 76
        x1, y1 = x0 + 620, 592
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 12, y0 + 8, r, moyen, ENCRE)
        ecrire(x0 + 440, y0 + 10, "voit     plate", 0, GRIS)
        cx0, cw, rh = x0 + 80, 28, 29
        cy0 = y0 + 50
        for b in range(0, 13, 2):
            ecrire(int(cx0 + b * cw) - 6, cy0 - 16, f"{b / 4:g}".replace(".", ","), 0, GRIS)
        for ligne, c in enumerate(d["les_cotes"][r]):
            yy = cy0 + ligne * rh
            ecrire(x0 + 12, yy + 7, f"g{c['le_rang']} {c['le_cote']}", 0, ENCRE)
            h = c["lhistogramme"]
            haut = max(h) if max(h) else 1
            for b, n in enumerate(h):
                t = n / haut
                col = tuple(int(FOND[i] + t * (BON[i] - FOND[i])) for i in range(3))
                art.rectangle([cx0 + b * cw, yy, cx0 + (b + 1) * cw - 1, yy + rh - 3], fill=col, outline=TRAIT)
            for q, col in ((c["la_distance_mediane_en_pas"], ENCRE), (c["le_depart_en_pas"], ALERTE)):
                if q is None:
                    continue
                if not 0.0 <= q <= LE_PAS_MAX:
                    traces["ecretes"] += 1
                xq = cx0 + min(LE_PAS_MAX, max(0.0, q)) / 0.25 * cw
                art.line([xq, yy - 1, xq, yy + rh - 2], fill=col, width=3)
            ecrire(x0 + 440, yy + 7, _fr(c["la_part_qui_voit"]), 0, ENCRE)
            ecrire(x0 + 490, yy + 7, _fr(plates[r].get(c["le_rang"])), 0, ALERTE if (plates[r].get(c["le_rang"]) or 0) > 0.5
                   else GRIS)
            traces["lignes"].append((r, c["le_rang"], c["le_cote"], sum(h), c["la_distance_mediane_en_pas"], c["le_depart_en_pas"]))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : si une plage de m7 à moins d'un pas est une autre spire ; ni ce qu'est m7 là où "
                              "la nappe est plate.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_325.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x 2 ; y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "X 2", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une ligne par côté, à ses comptes et marques mesurés", traces["lignes"] == les_lignes_attendues(d))
    v("★★★ aucune marque n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★ la platitude de chaque nappe est écrite", all(_fr(n["la_part_a_ce_decalage"]) in txt for r in LES_ROULEAUX
                                                          for n in d["les_nappes"][r]))
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
                   / "325_a_quelle_distance_m7_montre_t_il_la_feuille_suivante.png")
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
