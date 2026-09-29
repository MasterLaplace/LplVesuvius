"""Le profil moyen du scan le long des rayons, de −1 à +41 voxels, là où m7 voit une feuille à un pas et là où il n'en voit aucune.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté, deux courbes : vert, les rayons où `m7` voit une feuille entre 5 et
30 voxels ; orange, ceux où il n'en voit aucune ; la bande claire est la zone de 12 à 28 voxels où la saillance cherche un maximum.
Ce qui se voit d'un coup : si la courbe verte elle-même a un maximum, et si l'orange en a un aussi.

  uv run python src/figures/figure_le_scan_montre_t_il_la_feuille_que_m7_manque.py \\
      --sortie docs/images/319_le_scan_montre_t_il_la_feuille_que_m7_manque.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "le_scan_montre_t_il_la_feuille_que_m7_manque.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (226, 236, 230)
L_, H_ = 1360, 700
LA_BANDE = 600


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
    u = d["les_constantes"]["les_u"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "profil moyen du scan le long du rayon, de −1 à +41 voxels (axe de −1,5 à 1,5) ; vert : m7 voit une feuille entre 5 "
                   "et 30 voxels ; orange : il n'en voit aucune ; bande : 12 à 28 voxels", petit, GRIS)
    for k, c in enumerate(d["les_cotes"]):
        col, lig = k % 5, k // 5
        x0, y0 = 50 + col * 254, 72 + lig * 262
        x1, y1 = x0 + 240, y0 + 248
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 8, y0 + 6, f"graine {c['le_rang']}, {c['le_cote']}", moyen, ENCRE)
        ecrire(x0 + 8, y0 + 24, c["la_lecture"][:40], 0, GRIS)
        gx0, gx1, gy0, gy1 = x0 + 12, x1 - 12, y0 + 46, y0 + 196

        def xu(v):
            return gx0 + (v - u[0]) / (u[-1] - u[0]) * (gx1 - gx0)

        def yv(v):
            return gy1 - (max(-1.5, min(1.5, v)) + 1.5) / 3.0 * (gy1 - gy0)

        art.rectangle([xu(12), gy0, xu(28), gy1], fill=PALE)
        art.line([gx0, yv(0.0), gx1, yv(0.0)], fill=TRAIT)
        for g, coul in (("m7_voit", BON), ("m7_ne_voit_rien", ALERTE)):
            p = c[g]["le_profil_moyen"]
            xy = [(xu(a), yv(b)) for a, b in zip(u, p)]
            if len(xy) > 1:
                art.line(xy, fill=coul, width=2)
            traces["courbes"].append((c["le_rang"], c["le_cote"], g, len(xy)))
        ecrire(x0 + 8, y0 + 204, f"saillance {_fr(c['m7_voit']['la_saillance'])} ({c['m7_voit']['les_rayons_lus']})", 0, BON)
        ecrire(x0 + 8, y0 + 222, f"saillance {_fr(c['m7_ne_voit_rien']['la_saillance'])} "
                                 f"({c['m7_ne_voit_rien']['les_rayons_lus']})", 0, ALERTE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que le scan montre ces feuilles ; là où la courbe verte n'a pas de maximum, le "
                              "rapport des saillances compare du bruit.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_319.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "le scan montre"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LE SCAN MONTRE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ deux courbes par côté, à la longueur mesurée", traces["courbes"] == [
        (c["le_rang"], c["le_cote"], g, len(c[g]["le_profil_moyen"])) for c in d["les_cotes"]
        for g in ("m7_voit", "m7_ne_voit_rien")])
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "319_le_scan_montre_t_il_la_feuille_que_m7_manque.png")
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
