"""Entre chaque surface de la chaîne de 303 et sa spire suivante, la part des rayons qui traversent zéro, une ou plusieurs plages de m7.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté et saut par saut, une barre partagée : vert, aucune plage entre les
deux surfaces, la chaîne passe à la surface suivante ; orange, une ; brun, plusieurs.

  uv run python src/figures/figure_la_chaine_saute_t_elle_des_surfaces_de_m7.py \\
      --sortie docs/images/313_la_chaine_saute_t_elle_des_surfaces_de_m7.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_saute_t_elle_des_surfaces_de_m7.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
ORANGE = (222, 160, 110)
BRUN = (140, 80, 50)
L_, H_ = 1360, 640
LA_BANDE = 540


def _fr(x, n: int = 0) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",")


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
    traces = {"barres": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "part des rayons appuyés sur m7 qui traversent, entre la surface et sa spire suivante : aucune plage (vert), une "
                   "(orange), plusieurs (brun)", petit, GRIS)
    x0, y0, x1, y1 = 50, 72, 1310, 526
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    cx0, lw = x0 + 160, (x1 - x0 - 180) / 4
    for h in range(4):
        ecrire(int(cx0 + h * lw + 8), y0 + 10, f"saut {h + 1}", 0, GRIS)
    rh = (y1 - y0 - 40) / max(1, len(d["les_cotes"]))
    for r, c in enumerate(d["les_cotes"]):
        y = y0 + 30 + r * rh
        ecrire(x0 + 10, int(y + rh / 2 - 7), f"graine {c['le_rang']}, {c['le_cote']}", 0, ENCRE)
        for h, s in enumerate(c["les_sauts"]):
            xa, xb = cx0 + h * lw + 4, cx0 + (h + 1) * lw - 8
            if s["aucune"] is None:
                continue
            w = xb - xa
            p0, p1, p2 = s["aucune"], s["une"], s["plus"]
            art.rectangle([xa, y + 6, xa + p0 * w, y + rh - 6], fill=BON)
            art.rectangle([xa + p0 * w, y + 6, xa + (p0 + p1) * w, y + rh - 6], fill=ORANGE)
            art.rectangle([xa + (p0 + p1) * w, y + 6, xb, y + rh - 6], fill=BRUN)
            ecrire(int(xa + 6), int(y + rh / 2 - 7), f"{_fr(100 * p0)} %", 0, FOND)
            traces["barres"].append((c["le_rang"], c["le_cote"], h + 1, p0))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que deux surfaces consécutives de m7 soient deux spires consécutives du "
                              "rouleau.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_313.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "la chaîne passe"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA CHAÎNE PASSE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une barre par saut lu, à la part mesurée", traces["barres"] == [
        (c["le_rang"], c["le_cote"], h + 1, s["aucune"]) for c in d["les_cotes"] for h, s in enumerate(c["les_sauts"])
        if s["aucune"] is not None])
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "313_la_chaine_saute_t_elle_des_surfaces_de_m7.png")
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
