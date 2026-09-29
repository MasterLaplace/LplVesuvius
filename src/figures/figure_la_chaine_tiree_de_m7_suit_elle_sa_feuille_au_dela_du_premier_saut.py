"""La chaîne tirée de m7 sur PHerc0358 : le Z de chaque saut, de chaque côté des cinq nappes, et son pas.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté, jusqu'où la chaîne suit sa feuille, et que là où elle la suit
jusqu'au bout, chaque saut avance d'environ un pas du rouleau.

  uv run python src/figures/figure_la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.py \\
      --sortie docs/images/303_la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
L_, H_ = 1360, 860
Z_BAS, Z_HAUT = -4.0, 28.0


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    n = sum(1 for x in v["les_derniers"] if x >= v["H"]) if v["H"] else 0
    return (f"SUR PHerc0358, LA CHAÎNE TIRÉE DE m7 SUIT SA FEUILLE JUSQU'AU SAUT {v['H']} SUR {n} DES "
            f"{len(v['les_derniers'])} CÔTÉS")


def _y(z: float, base: float, haut: float) -> float:
    z = min(max(z, Z_BAS), Z_HAUT)
    return base - (z - Z_BAS) / (Z_HAUT - Z_BAS) * haut


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"z": [], "pas": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "chaque saut part de la surface du précédent, le long de sa normale, jusqu'à la feuille de m7 d'après ; le juge "
                   "de 301, Z ≥ 3 contre huit rampes, étalonné par taux", petit, GRIS)

    panneau(50, 74, 1310, 420, "Z DE CHAQUE SAUT (1 À 4), CÔTÉ PAR CÔTÉ ; ÉCRÊTÉ À 28")
    base, haut = 380, 270
    for z, nom, coul in ((0.0, "Z = 0", GRIS), (3.0, "Z = 3", ENCRE)):
        y = _y(z, base, haut)
        art.line([110, y, 1290, y], fill=coul)
        ecrire(60, int(y) - 7, nom, 0, coul)
    for i, c in enumerate(d["les_cotes"]):
        x0 = 130 + i * 116
        for k, s in enumerate(c["les_sauts"]):
            x = x0 + k * 22
            z = s["le_z"]
            if z is not None:
                y0_, y1_ = sorted((_y(0.0, base, haut), _y(z, base, haut)))
                coul = BON if s["la_piece"] == "suit sa feuille" else ALERTE
                art.rectangle([x, y0_, x + 16, y1_], fill=coul)
                points.append((x + 16, y0_))
            traces["z"].append((c["le_rang"], c["le_cote"], s["le_saut"], z))
        signe = "+" if c["le_cote"] == "plus" else "−"
        ecrire(x0, base + 8, f"g{c['le_rang']} {signe}", 0, ENCRE)
        ecrire(x0, base + 24, f"jusqu'au {c['le_dernier_saut_qui_suit']}", 0, GRIS)
    ecrire(700, 100, "■ suit sa feuille", 0, BON)
    ecrire(860, 100, "■ ne la suit pas", 0, ALERTE)

    panneau(50, 436, 1310, 740, "LE PAS MÉDIAN DES POINTS APPUYÉS, SAUT PAR SAUT, EN VOXELS (LE PAS DU ROULEAU : 20)")
    base, haut = 700, 220
    y20 = base - 20 / 40 * haut
    art.line([110, y20, 1290, y20], fill=ENCRE)
    ecrire(60, int(y20) - 7, "20", 0, ENCRE)
    art.line([110, base, 1290, base], fill=GRIS)
    for i, c in enumerate(d["les_cotes"]):
        x0 = 130 + i * 116
        for k, s in enumerate(c["les_sauts"]):
            x = x0 + k * 22
            p = s["le_pas_median_des_appuyes_voxels"]
            if p is not None:
                hh = min(p / 40.0, 1.0) * haut
                art.rectangle([x, base - hh, x + 16, base], fill=BLEU)
                points.append((x + 16, base - hh))
            traces["pas"].append((c["le_rang"], c["le_cote"], s["le_saut"], p))
        signe = "+" if c["le_cote"] == "plus" else "−"
        ecrire(x0, base + 8, f"g{c['le_rang']} {signe}", 0, ENCRE)

    art.rectangle([0, 756, L_, H_], fill=BANDE)
    ecrire(50, 768, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 790, "⚠ ce qui n'est PAS établi : sur quelle feuille tombe chaque saut ; qu'aucun ne saute deux feuilles là où m7 "
                    "en manque une ; que la nappe reste sur une seule feuille", moyen, ALERTE)
    ecrire(50, 812, "(302) ; ce que vaut une chaîne de 6 mm pour un rouleau entier.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


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
    tmp = sortie.parent / ".sonde_303.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "H": 2, "les_derniers": [2, 2, 3, 0, 1, 2], "lissue": "x"}
    v("★★★ le titre LIT la mesure", "JUSQU'AU SAUT 2 SUR 4 DES 6 CÔTÉS" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ une barre par saut et par côté, à son Z et à son pas mesurés",
      traces["z"] == [(c["le_rang"], c["le_cote"], s["le_saut"], s["le_z"]) for c in d["les_cotes"] for s in c["les_sauts"]]
      and traces["pas"] == [(c["le_rang"], c["le_cote"], s["le_saut"], s["le_pas_median_des_appuyes_voxels"])
                            for c in d["les_cotes"] for s in c["les_sauts"]])
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
                   / "303_la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut.png")
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
