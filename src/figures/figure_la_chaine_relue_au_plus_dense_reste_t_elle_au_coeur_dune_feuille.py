"""Les spires des chaînes de m7, saut par saut : où est le plus dense du scan, et de combien chaque saut avance.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté et saut par saut, une case verte quand le plus dense du profil moyen
de la spire est à au plus un quart de pas d'elle, orange sinon, avec le décalage du plus dense et le pas du saut : on voit d'un coup
d'œil quels côtés restent au cœur d'une feuille jusqu'au bout, et où les autres en sortent.

  uv run python src/figures/figure_la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.py \\
      --sortie docs/images/310_la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
VERT = (214, 232, 221)
ORANGE = (244, 222, 205)
VIDE = (234, 232, 226)
L_, H_ = 1360, 700
LA_BANDE = 600


def _fr(x, n: int = 1) -> str:
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
    traces = {"cases": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def grille(x0, y0, x1, y1, titre, cotes):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 10, y0 + 8, titre, moyen, ENCRE)
        cx0, lw = x0 + 150, (x1 - x0 - 170) / 4
        for h in range(4):
            ecrire(int(cx0 + h * lw + 8), y0 + 32, f"saut {h + 1}", 0, GRIS)
        rh = min(44, (y1 - y0 - 60) / max(1, len(cotes)))
        for r, c in enumerate(cotes):
            y = y0 + 52 + r * rh
            ecrire(x0 + 10, int(y + rh / 2 - 7), f"graine {c['le_rang']}, {c['le_cote']}", 0, ENCRE)
            for h, s in enumerate(c["les_sauts"]):
                xa = cx0 + h * lw
                fond = VIDE if s["le_plus_dense"] is None else (VERT if s["au_coeur"] else ORANGE)
                art.rectangle([xa + 2, y + 2, xa + lw - 4, y + rh - 4], fill=fond)
                col = ENCRE if s["le_plus_dense"] is not None else GRIS
                ecrire(int(xa + 8), int(y + rh / 2 - 14), f"{_fr(s['le_plus_dense'], 0)} vx", 0, col)
                ecrire(int(xa + 8), int(y + rh / 2 + 1), f"pas {_fr(s['le_pas_median_voxels'])}", 0, col)
                traces["cases"].append((c["le_rang"], c["le_cote"], s["le_saut"], fond))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "case : décalage du plus dense du profil moyen de la spire, en voxels, et pas médian du saut ; vert : à au plus un "
                   "quart de pas (5 voxels), orange : au-delà, gris : sans matière jugée", petit, GRIS)
    grille(50, 72, 700, 586, "la chaîne de 303 : chaque saut est un vote", d["les_chaines"]["vote"])
    grille(740, 72, 1310, 586, "la chaîne de 306 : chaque saut croît", d["les_chaines"]["croissante"])

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que « au plus dense » veuille dire « sur une feuille », ni que les spires "
                              "soient consécutives, ni qu'elles restent sur une seule feuille.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_310.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "la chaîne tient"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA CHAÎNE TIENT", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(c["le_rang"], c["le_cote"], s["le_saut"],
                VIDE if s["le_plus_dense"] is None else (VERT if s["au_coeur"] else ORANGE))
               for nom in ("vote", "croissante") for c in d["les_chaines"][nom] for s in c["les_sauts"]]
    v("★★★ une case par saut, à la couleur de sa mesure", traces["cases"] == attendu)
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
                   / "310_la_chaine_relue_au_plus_dense_reste_t_elle_au_coeur_dune_feuille.png")
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
