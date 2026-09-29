"""Les cinq nappes de m7 qui suivent leur feuille sur PHerc0358 : leurs pièces, leurs boucles, et la taille de leurs sauts.

⚠⚠ **Ce que cette figure doit rendre évident.** Que chaque nappe et ses deux spires tiennent presque toujours d'une seule pièce ;
mais que, sur trois d'entre elles, un carré de voisins sur dix ne ferme pas sa boucle, et que les sauts qui font ces boucles valent
à peu près un demi-pas, pas un pas.

  uv run python src/figures/figure_les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.py \\
      --sortie docs/images/302_les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
VIOLET = (120, 84, 150)
L_, H_ = 1360, 820
LES_SURFACES = (("nappe", "nappe", BON), ("plus", "spire +", BLEU), ("moins", "spire −", VIOLET))


def _fr(x, n: int = 2) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"PAR LA RÈGLE, {v['k']} DES {v['n']} NAPPES TIENNENT D'UNE SEULE PIÈCE AVEC LEURS SPIRES ; "
            "MAIS LEURS BOUCLES NE FERMENT PAS TOUTES")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"pieces": [], "boucles": [], "sauts": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "pièce : points voisins dont les décalages diffèrent d'au plus un demi-pas (10 voxels) · boucle : les quatre "
                   "sauts d'un carré de voisins, arrondis au pas, doivent faire zéro", petit, GRIS)
    nappes = d["le_verdict"] and d["les_nappes"]

    def barres(y0, titre, cle, echelle, unite, fmt):
        panneau(50, y0, 1310, y0 + 210, titre)
        base, haut = y0 + 170, 120
        for i, n in enumerate(nappes):
            x0 = 120 + i * 240
            for k, (s, nom, coul) in enumerate(LES_SURFACES):
                val = cle(n["les_surfaces"][s])
                x = x0 + k * 56
                if val is not None:
                    hh = min(val / echelle, 1.0) * haut
                    art.rectangle([x, base - hh, x + 40, base], fill=coul)
                    points.append((x + 40, base - hh))
                    ecrire(x, int(base - hh) - 15, fmt(val), 0, ENCRE)
                yield (n["le_rang"], s, val)
            ecrire(x0, base + 6, f"graine {n['le_rang']}", 0, ENCRE)
        art.line([100, base, 1290, base], fill=GRIS)
        for k, (_, nom, coul) in enumerate(LES_SURFACES):
            ecrire(900 + k * 120, y0 + 12, f"■ {nom}", 0, coul)
        ecrire(700, y0 + 12, unite, 0, GRIS)

    traces["pieces"] = list(barres(74, "LA PLUS GRANDE PIÈCE, EN PART DES POINTS", lambda x: x["la_plus_grande"], 1.0,
                                   "échelle : 1", lambda v: _fr(v, 3)))
    traces["boucles"] = list(barres(300, "LES CARRÉS QUI NE FERMENT PAS LEUR BOUCLE, EN PART DES CARRÉS",
                                    lambda x: x["les_boucles"]["la_part"], 0.2, "échelle : 0,2", lambda v: _fr(v, 3)))
    traces["sauts"] = list(barres(526, "LA MÉDIANE DES SAUTS DE PLUS D'UN DEMI-PAS, EN VOXELS (LE PAS : 20)",
                                  lambda x: x["les_boucles"]["leur_mediane_voxels"], 20.0, "échelle : 20",
                                  lambda v: _fr(v, 1)))

    art.rectangle([0, 750, L_, H_], fill=BANDE)
    ecrire(50, 760, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 780, "⚠ ce qui n'est PAS établi : qu'une nappe reste sur une seule feuille ; la règle des pièces ne voit pas une "
                    "coupure ouverte, et les boucles, ajoutées après, ne ferment pas partout", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_302.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "k": 2, "n": 5, "lissue": "x"}
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("PAR LA RÈGLE, 2 DES 5 NAPPES"), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    ns = d["les_nappes"]
    v("★★★★ les pièces, les boucles et les sauts sont ceux de la mesure",
      traces["pieces"] == [(n["le_rang"], s, n["les_surfaces"][s]["la_plus_grande"]) for n in ns for s, _, _ in LES_SURFACES]
      and traces["boucles"] == [(n["le_rang"], s, n["les_surfaces"][s]["les_boucles"]["la_part"]) for n in ns
                                for s, _, _ in LES_SURFACES]
      and traces["sauts"] == [(n["le_rang"], s, n["les_surfaces"][s]["les_boucles"]["leur_mediane_voxels"]) for n in ns
                              for s, _, _ in LES_SURFACES])
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
                   / "302_les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille.png")
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
