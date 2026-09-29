"""Le profil moyen long du scan, sur deux pas de part et d'autre des nappes de m7 de PHerc0358, et ses maxima.

⚠⚠ **Ce que cette figure doit rendre évident.** Nappe par nappe, le profil moyen de −42 à +42 voxels le long de la normale, avec
ses maxima marqués et les pas du rouleau en repères : combien de maxima survivent à la moyenne, et à quel écart l'un de l'autre.

  uv run python src/figures/figure_les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.py \\
      --sortie docs/images/311_les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 720
LA_BANDE = 620


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].split(" : ")[0].upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"courbes": [], "maxima": []}
    pas = d["les_constantes"]["PHerc0358"]["le_pas_voxels"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "profil moyen du scan brut le long de la normale, chaque profil normé, de −42 à +42 voxels ; traits verticaux : 0 et "
                   "±1, ±2 pas du rouleau (20 voxels) ; points : les maxima retenus", petit, GRIS)
    nappes = d["phercs0358"]
    for k, n in enumerate(nappes):
        col, lig = k % 4, k // 4
        x0, y0 = 50 + col * 318, 72 + lig * 270
        x1, y1 = x0 + 300, y0 + 256
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 8, y0 + 6, n["la_surface"].replace("_", " "), moyen, ENCRE)
        ecrire(x0 + 8, y0 + 26, f"maxima {n['les_maxima']}, {n['la_forme']}", 0, GRIS)
        p = n["le_profil_moyen"]
        gx0, gx1, gy0, gy1 = x0 + 12, x1 - 12, y0 + 50, y1 - 16
        T = len(p) // 2 if p else 42

        def xu(u):
            return gx0 + (u + T) / (2 * T) * (gx1 - gx0)

        def yv(v):
            return gy1 - (max(-1.5, min(2.5, v)) + 1.5) / 4.0 * (gy1 - gy0)

        for u in (-2 * pas, -pas, 0.0, pas, 2 * pas):
            art.line([xu(u), gy0, xu(u), gy1], fill=TRAIT)
        if len(p) > 1:
            xy = [(xu(i - T), yv(v)) for i, v in enumerate(p)]
            art.line(xy, fill=BON, width=2)
        traces["courbes"].append((n["la_surface"], len(p)))
        for m in n["les_maxima"]:
            y = yv(p[m + T])
            art.ellipse([xu(m) - 4, y - 4, xu(m) + 4, y + 4], fill=ALERTE)
            traces["maxima"].append((n["la_surface"], m))

    f = d["paris4_les_formes"]
    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']} ; PHercParis4, 24 blocs : {f['au pas']} au pas, "
                              f"{f['par paires']} par paires, {f['serrés']} serrés, {f['indécidable']} indécidables", petit, ENCRE)
    ecrire(50, LA_BANDE + 34, "⚠ ce qui n'est PAS établi : ce que sont les deux maxima d'une paire, ni qu'un profil moyen sur 6 mm garde "
                              "la périodicité de l'empilement.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_311.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "les maxima parlent : oui"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LES MAXIMA PARLENT", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une courbe par nappe, à la longueur mesurée",
      traces["courbes"] == [(n["la_surface"], len(n["le_profil_moyen"])) for n in d["phercs0358"]])
    v("★★★ un point par maximum mesuré", traces["maxima"] == [(n["la_surface"], m) for n in d["phercs0358"]
                                                             for m in n["les_maxima"]])
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
                   / "311_les_maxima_du_scan_sont_ils_au_pas_ou_par_paires.png")
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
