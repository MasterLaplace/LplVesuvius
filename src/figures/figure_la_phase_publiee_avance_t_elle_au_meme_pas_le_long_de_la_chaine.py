"""Le cosinus de la phase d'enroulement publiée (lasagna), rang par rang le long de la chaîne de 303, et l'ajustement d'une sinusoïde.

⚠⚠ **Ce que cette figure doit rendre évident.** Graine par graine, le cosinus médian de `lasagna` sur chacune des neuf surfaces de
la pile, de la spire −4 à la spire +4 ; et, à côté, le R² médian de l'ajustement point par point contre celui du témoin permuté :
tant que les deux se valent, la sinusoïde n'est pas lue.

  uv run python src/figures/figure_la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.py \\
      --sortie docs/images/314_la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 560
LA_BANDE = 460


def _fr(x, n: int = 2) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"courbes": []}
    rangs = d["les_constantes"]["les_rangs"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "cosinus médian de lasagna sur chaque surface de la pile, de la spire −4 à la spire +4 (axe de −1 à 1) ; en bas, "
                   "R² médian de l'ajustement point par point, et celui du témoin permuté", petit, GRIS)
    for k, g in enumerate(d["les_graines"]):
        x0, y0 = 50 + k * 254, 72
        x1, y1 = x0 + 240, 446
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 8, y0 + 6, f"graine {g['le_rang']}", moyen, ENCRE)
        ecrire(x0 + 8, y0 + 26, g["la_lecture"], 0, GRIS)
        gx0, gx1, gy0, gy1 = x0 + 14, x1 - 14, y0 + 52, y0 + 260

        def xk(r):
            return gx0 + (r - rangs[0]) / (rangs[-1] - rangs[0]) * (gx1 - gx0)

        def yc(c):
            return gy1 - (c + 1.0) / 2.0 * (gy1 - gy0)

        art.line([gx0, yc(0.0), gx1, yc(0.0)], fill=TRAIT)
        art.line([xk(0), gy0, xk(0), gy1], fill=TRAIT)
        pts = [(xk(r), yc(c)) for r, c in zip(rangs, g["le_cosinus_median_par_rang"]) if c is not None]
        if len(pts) > 1:
            art.line(pts, fill=BON, width=2)
        for x, y in pts:
            art.ellipse([x - 3, y - 3, x + 3, y + 3], fill=BON)
        traces["courbes"].append((g["le_rang"], len(pts)))
        ecrire(int(xk(rangs[0])) - 6, gy1 + 4, "−4", 0, GRIS)
        ecrire(int(xk(0)) - 3, gy1 + 4, "0", 0, GRIS)
        ecrire(int(xk(rangs[-1])) - 6, gy1 + 4, "+4", 0, GRIS)
        ecrire(x0 + 8, y0 + 290, f"R² médian {_fr(g.get('le_r2_median'))}", 0, ENCRE)
        ecrire(x0 + 8, y0 + 308, f"témoin permuté {_fr(g.get('le_r2_median_du_temoin'))}", 0, ENCRE)
        ecrire(x0 + 8, y0 + 326, f"δ médian {_fr(g.get('le_delta_median_degres'), 1)}°, IQR {_fr(g.get('lecart_interquartile_degres'), 1)}°",
               0, GRIS)
        ecrire(x0 + 8, y0 + 344, f"{g['les_points']} points", 0, GRIS)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que lasagna ait raison ; un accord ou un désaccord entre deux prédictions ne dit "
                              "pas laquelle voit juste.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_314.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "la phase avance"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA PHASE AVANCE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une courbe par graine, un point par rang lu", traces["courbes"] == [
        (g["le_rang"], sum(1 for c in g["le_cosinus_median_par_rang"] if c is not None)) for g in d["les_graines"]])
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
                   / "314_la_phase_publiee_avance_t_elle_au_meme_pas_le_long_de_la_chaine.png")
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
