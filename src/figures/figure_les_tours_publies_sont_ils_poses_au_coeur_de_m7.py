"""Où passent le tracé humain et les tours publiés 5753_0 à 5753_-3 dans les plages de m7 : l'écart médian au centre de la plage la plus proche, et la part des sommets à un voxel du niveau 2.

⚠⚠ **Ce que cette figure doit rendre évident.** Une barre par surface, la part de ses sommets à au plus un voxel du centre d'une plage de
`m7` ; le nombre au-dessus, l'écart médian. Si les tours publiés montent bien plus haut que le tracé humain, ils ont été posés sur `m7` ;
s'ils sont à la même hauteur, `m7` ne les distingue pas d'un tracé à la main.

  uv run python src/figures/figure_les_tours_publies_sont_ils_poses_au_coeur_de_m7.py \\
      --sortie docs/images/332_les_tours_publies_sont_ils_poses_au_coeur_de_m7.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "les_tours_publies_sont_ils_poses_au_coeur_de_m7.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 520
LA_BANDE = 430
LES_NOMS = {"le_trace_humain": "le tracé humain (2023)", "le_tour_0": "5753_0", "le_tour_-1": "5753_-1", "le_tour_-2": "5753_-2",
            "le_tour_-3": "5753_-3"}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    s = d["les_surfaces"]
    tours = [x["la_part_a_un_voxel"] for k, x in s.items() if k != "le_trace_humain"]
    f_ = lambda x: f"{x * 100:.0f}".replace(".", ",")  # noqa: E731
    return (f"à un voxel du centre des plages de m7 : {f_(min(tours))} à {f_(max(tours))} % des sommets des tours publiés, "
            f"{f_(s['le_trace_humain']['la_part_a_un_voxel'])} % du tracé humain").upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "le long de la normale de chaque sommet, l'écart au centre de la plage de m7 la plus proche, en voxels du niveau 2 ; "
                   "barre : la part des sommets à un voxel ; nombre : l'écart médian", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 1310, 410
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    gy0, gy1 = y0 + 40, y1 - 50
    for q in (0.25, 0.5, 0.75, 1.0):
        yq = gy1 - q * (gy1 - gy0)
        art.line([x0 + 60, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, f"{int(q * 100)} %", 0, GRIS)
    for n, (k, x) in enumerate(d["les_surfaces"].items()):
        xa = x0 + 120 + n * 230
        p = x["la_part_a_un_voxel"] or 0.0
        art.rectangle([xa, gy1 - p * (gy1 - gy0), xa + 120, gy1], fill=ALERTE if k == "le_trace_humain" else BON)
        ecrire(int(xa), int(gy1 - p * (gy1 - gy0)) - 20, f"écart médian {x['lecart_median_voxels']:g}".replace(".", ","), 0, ENCRE)
        ecrire(int(xa), gy1 + 8, LES_NOMS.get(k, k), 0, ENCRE)
        ecrire(int(xa), gy1 + 24, f"{x['les_sommets']} sommets", 0, GRIS)
        traces["barres"].append((k, x["la_part_a_un_voxel"]))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : comment les tours 5753_k ont été faits.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_332.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["les_surfaces"]["le_trace_humain"]["la_part_a_un_voxel"] = 0.1
    v("★★★ le titre LIT la mesure", "10 % DU TRACÉ HUMAIN" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une barre par surface, à sa part mesurée", traces["barres"] == [(k, x["la_part_a_un_voxel"])
                                                                         for k, x in d["les_surfaces"].items()])
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
                   / "332_les_tours_publies_sont_ils_poses_au_coeur_de_m7.png")
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
