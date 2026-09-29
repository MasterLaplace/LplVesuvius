"""L'épaisseur de la plage de m7 sous chaque nappe qui croît, en pas du rouleau, sur PHerc0358 et sur PHercParis4, contre la platitude de la nappe.

⚠⚠ **Ce que cette figure doit rendre évident.** Une barre par nappe, sur une échelle logarithmique de 0,1 à 10 pas : la longueur médiane
de la plage de `m7` qui porte ses points, le long de sa normale. Au-dessus du trait d'un pas, la nappe est dans un bloc ; sous le trait
d'un demi-pas, sur une feuille. Sous chaque barre, la part des points de la nappe au même décalage : si les barres hautes sont celles des
nappes plates, la platitude dit le bloc.

  uv run python src/figures/figure_la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.py \\
      --sortie docs/images/326_la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.png

⚠ Tout vient de la mesure.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 600
LA_BANDE = 510
LES_ROULEAUX = (("PHerc0358", ALERTE), ("PHercParis4", BON))
LE_BAS, LE_HAUT = 0.1, 10.0


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def les_barres_attendues(d: dict) -> list:
    return [(r, n["le_rang"], n["la_longueur_mediane_en_pas"]) for r, _ in LES_ROULEAUX for n in d["les_nappes"][r]
            if n["la_longueur_mediane_en_pas"] is not None]


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "ecretes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "la longueur médiane de la plage de m7 qui porte les points de chaque nappe qui croît, le long de sa normale, en pas du "
                   "rouleau (échelle logarithmique) ; sous chaque barre, la part de la nappe au même décalage", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    gy0, gy1 = y0 + 30, y1 - 70
    Y = lambda q: gy1 - (math.log10(q) - math.log10(LE_BAS)) / (math.log10(LE_HAUT) - math.log10(LE_BAS)) * (gy1 - gy0)  # noqa: E731
    for q, lab, col in ((0.1, "0,1 pas", GRIS), (0.5, "un demi-pas", GRIS), (1.0, "un pas", ALERTE), (10.0, "10 pas", GRIS)):
        art.line([x0 + 90, Y(q), x1 - 10, Y(q)], fill=col if q in (0.5, 1.0) else TRAIT, width=2 if q == 1.0 else 1)
        ecrire(x0 + 8, int(Y(q)) - 7, lab, 0, col)
    ecrire(x1 - 230, int(Y(1.0)) - 20, "au-dessus : dans un bloc", 0, ALERTE)
    bw, gap = 58, 14
    xa = x0 + 110
    for r, col in LES_ROULEAUX:
        ecrire(int(xa), y0 + 8, r, moyen, ENCRE)
        for n in d["les_nappes"][r]:
            q = n["la_longueur_mediane_en_pas"]
            if q is not None:
                if not LE_BAS <= q <= LE_HAUT:
                    traces["ecretes"] += 1
                qq = min(LE_HAUT, max(LE_BAS, q))
                art.rectangle([xa, Y(qq), xa + bw - 8, gy1], fill=col)
                traces["barres"].append((r, n["le_rang"], q))
            ecrire(int(xa), gy1 + 6, f"g{n['le_rang']}", 0, ENCRE)
            pl = n["la_part_a_ce_decalage"]
            ecrire(int(xa), gy1 + 24, "—" if pl is None else f"{pl:.2f}".replace(".", ","), 0,
                   ALERTE if (pl or 0) > 0.5 else GRIS)
            xa += bw
        xa += gap + 20

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : ce que le scan montre dans un bloc de m7, ni pourquoi m7 y est plein.", moyen,
           ALERTE)

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
    tmp = sortie.parent / ".sonde_326.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x 2"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "X 2", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une barre par nappe, à sa longueur mesurée", traces["barres"] == les_barres_attendues(d))
    v("★★★ aucune barre n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★ la platitude de chaque nappe est écrite", all(f"{n['la_part_a_ce_decalage']:.2f}".replace(".", ",") in txt
                                                          for r, _ in LES_ROULEAUX for n in d["les_nappes"][r]))
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
                   / "326_la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7.png")
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
