"""Autour de chaque graine et pour chaque paire de tours publiés consécutifs, la part des sommets du premier qui sont à un quart de pas du second : là, les deux tours sont sur la même feuille.

⚠⚠ **Ce que cette figure doit rendre évident.** Une case par graine et par paire, la part écrite dedans, d'autant plus foncée qu'elle est
grande ; bordée d'orange si la paire se recouvre par la règle déclarée. Si les rangées des graines 1 à 3 sont foncées et les autres claires,
le recouvrement est propre à l'endroit où aucune chaîne ne descend strictement.

  uv run python src/figures/figure_les_tours_publies_voisins_se_recouvrent_ils.py \\
      --sortie docs/images/341_les_tours_publies_voisins_se_recouvrent_ils.png

⚠ Tout vient de la mesure de `341`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_tours_publies_voisins_se_recouvrent_ils.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
L_, H_ = 1360, 580
LA_BANDE = 490
LA_PART_MAX = 0.5


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"{v['a']} des {v['n1']} paires se recouvrent autour des graines 1 à 3, {v['b']} des {v['n2']} autour des graines 4 à 8").upper()


def la_teinte(part: float | None) -> tuple[int, int, int]:
    """Du blanc cassé au vert foncé, en proportion de la part, jusqu'à `LA_PART_MAX`."""
    if part is None:
        return (236, 234, 228)
    x = min(1.0, max(0.0, part / LA_PART_MAX))
    return tuple(int(round(a + (b - a) * x)) for a, b in zip((244, 243, 238), (40, 90, 70)))


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

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "dans chaque case : la part des sommets du premier tour, en face du second, à au plus un quart de pas de lui ; bord orange : "
                   "la paire se recouvre (au moins 5 % et 200 sommets)", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 1310, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    paires = d["les_graines"][0]["les_paires"]
    for m, p in enumerate(paires):
        ka, kb = p["les_tours"]
        ecrire(x0 + 110 + m * 165 + 30, y0 + 10, f"{ka} et {kb}".replace("-", "−"), 0, GRIS)
    for n, g in enumerate(d["les_graines"]):
        ya = y0 + 32 + n * 44
        ecrire(x0 + 14, ya + 11, f"graine {g['le_rang']}", 0, ALERTE if g["le_rang"] <= 3 else ENCRE)
        for m, p in enumerate(g["les_paires"]):
            xa = x0 + 110 + m * 165
            fonce = p["la_part"] is not None and p["la_part"] > LA_PART_MAX / 2
            art.rectangle([xa, ya, xa + 155, ya + 36], fill=la_teinte(p["la_part"]),
                          outline=ALERTE if p["se_recouvrent"] else None, width=3)
            texte = "non mesurée" if p["la_part"] is None else f"{p['la_part'] * 100:.1f} %".replace(".", ",")
            ecrire(xa + 10, ya + 11, texte, 0, (250, 249, 246) if fonce else ENCRE)
            traces["cases"].append((g["le_rang"], tuple(p["les_tours"]), p["la_part"], p["se_recouvrent"],
                                    xa + 155 < x1 and ya + 36 < y1))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : si ce sont deux feuilles collées, ou un tour publié posé sur la feuille de son "
                              "voisin.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_341.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update(a=2, n1=9, b=8, n2=9)
    v("★★★ le titre LIT la mesure", le_titre(autre) == "2 DES 9 PAIRES SE RECOUVRENT AUTOUR DES GRAINES 1 À 3, 8 DES 9 AUTOUR DES GRAINES "
      "4 À 8", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(g["le_rang"], tuple(p["les_tours"]), p["la_part"], p["se_recouvrent"]) for g in d["les_graines"] for p in g["les_paires"]]
    v("★★★ une case par graine et par paire, à la part mesurée", [c[:4] for c in traces["cases"]] == attendu)
    v("★★★★ aucune case ne sort du cadre", all(c[4] for c in traces["cases"]))
    v("★★★ la teinte croît avec la part et plafonne", la_teinte(0.0) == (244, 243, 238) and la_teinte(LA_PART_MAX) == (40, 90, 70)
      and la_teinte(0.9) == la_teinte(LA_PART_MAX) and sum(la_teinte(0.1)) > sum(la_teinte(0.3)))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "341_les_tours_publies_voisins_se_recouvrent_ils.png")
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
