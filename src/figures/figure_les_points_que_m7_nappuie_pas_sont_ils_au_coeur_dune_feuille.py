"""Le plus dense du profil moyen, lu à part sur les points que m7 appuie et sur les autres, saut par saut, aux pas donnés de 16, 20 et 24.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté, au pas donné de 20, le décalage du plus dense saut par saut : vert
pour les points appuyés sur `m7`, orange pour les autres ; la bande claire est le quart de pas. Les uns collent à zéro, les autres
partent aux bords de la fenêtre. En dessous, la même lecture résumée aux pas de 16 et de 24.

  uv run python src/figures/figure_les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.py \\
      --sortie docs/images/317_les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.png

⚠ Tout vient de la mesure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (226, 236, 230)
L_, H_ = 1360, 600
LA_BANDE = 500
LA_PORTEE = 21


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def le_resume(lus: list, g: str) -> str:
    xs = [x[g]["le_plus_dense"] for x in lus[8:16] if x[g]["le_plus_dense"] is not None]
    am = [x[g]["lamplitude"] for x in lus[8:16] if x[g]["lamplitude"] is not None]
    if not xs:
        return "—"
    return f"{int(round(float(np.median(xs))))} vx, ampl. {_fr(float(np.median(am)), 2)}".replace("-", "−")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": []}
    q = d["les_constantes"]["le_quart_de_pas_voxels"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "au pas donné de 20 : décalage du plus dense, saut par saut, de −21 à +21 voxels ; vert : points appuyés sur m7, "
                   "orange : les autres ; bande : le quart de pas", petit, GRIS)
    for k, c in enumerate(d["les_cotes"]):
        x0, y0 = 50 + k * 318, 72
        x1, y1 = x0 + 300, 486
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 8, y0 + 6, f"graine {c['le_rang']}, {c['le_cote']}", moyen, ENCRE)
        ecrire(x0 + 8, y0 + 26, c["la_lecture"], 0, GRIS)
        gx0, gx1, gy0, gy1 = x0 + 14, x1 - 14, y0 + 50, y0 + 290
        lus = c["les_pas"]["20"]
        n = len(lus)

        def xh(h):
            return gx0 + (h - 1) / max(1, n - 1) * (gx1 - gx0)

        def yd(v):
            return gy0 + (LA_PORTEE - v) / (2 * LA_PORTEE) * (gy1 - gy0)

        art.rectangle([gx0, yd(q), gx1, yd(-q)], fill=PALE)
        art.line([gx0, yd(0), gx1, yd(0)], fill=TRAIT)
        for g, col in (("non_appuyes", ALERTE), ("appuyes", BON)):
            for x in lus:
                u = x[g]["le_plus_dense"]
                if u is not None:
                    px, py = xh(x["le_saut"]), yd(u)
                    art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=col)
                    traces["points"].append((c["le_rang"], c["le_cote"], g, x["le_saut"], u))
        for m, pas in enumerate(("16", "20", "24")):
            ecrire(x0 + 8, y0 + 300 + 34 * m, f"pas {pas} : appuyés {le_resume(c['les_pas'][pas], 'appuyes')}", 0, BON)
            ecrire(x0 + 8, y0 + 316 + 34 * m, f"         autres {le_resume(c['les_pas'][pas], 'non_appuyes')}", 0, ALERTE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : où sont les feuilles entre les points que m7 appuie ; et le seuil d'amplitude, "
                              "0,5, que même les points appuyés ne passent pas.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_317.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "les points parlent"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LES POINTS PARLENT", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ un point par saut et par groupe, au plus dense mesuré", traces["points"] == [
        (c["le_rang"], c["le_cote"], g, x["le_saut"], x[g]["le_plus_dense"]) for c in d["les_cotes"]
        for g in ("non_appuyes", "appuyes") for x in c["les_pas"]["20"] if x[g]["le_plus_dense"] is not None])
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
                   / "317_les_points_que_m7_nappuie_pas_sont_ils_au_coeur_dune_feuille.png")
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
