"""La descente de la chaîne sans relance et de la chaîne bornée, comptée comme 330 la compte et comptée strictement, graine par graine ; et la médiane des quatre chaînes, comptée des deux façons.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque graine, quatre barres : la chaîne sans relance puis la chaîne bornée,
chacune comptée comme `330` la compte (claire) et strictement (foncée). À droite, la médiane de chaque chaîne des deux façons. Si les barres
foncées tombent là où les claires tenaient, la descente comptait juste des surfaces à deux tours.

  uv run python src/figures/figure_jugee_strictement_jusquou_la_chaine_bornee_descend_elle.py \\
      --sortie docs/images/340_jugee_strictement_jusquou_la_chaine_bornee_descend_elle.png

⚠ Tout vient de la mesure de `340`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "jugee_strictement_jusquou_la_chaine_bornee_descend_elle.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
LES_TEINTES = {"sans relance": ((200, 202, 206), (120, 124, 130)), "relancée depuis un point": ((222, 196, 170), (176, 120, 70)),
               "relancée depuis la spire": ((190, 205, 225), (70, 100, 150)), "bornée": ((160, 196, 180), (60, 110, 90))}
L_, H_ = 1360, 580
LA_BANDE = 490
LE_MAX = 7


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_mediane_souple(c: dict) -> float:
    return float(np.median([g["la_descente_souple"] for g in c["les_graines"] if g["le_tour_touche"]]))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    b = d["les_chaines"]["bornée"]
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    return (f"comptée strictement, la chaîne bornée passe de {f_(la_mediane_souple(b))} à {f_(b['la_mediane_stricte'])} tours en "
            f"médiane, la chaîne sans relance de {f_(la_mediane_souple(d['les_chaines']['sans relance']))} à "
            f"{f_(d['les_chaines']['sans relance']['la_mediane_stricte'])}").upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "ecretes": 0, "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, h, col, cle):
        if not 0 <= h <= LE_MAX:
            traces["ecretes"] += 1
        hh = min(LE_MAX, max(0.0, h))
        art.rectangle([x, gy1 - hh / LE_MAX * (gy1 - gy0), x + 16, gy1], fill=col)
        traces["barres"].append(cle + (h,))
        traces["rectangles"].append((len(cadres) - 1, x, x + 16))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "clair : compté comme 330, une surface à deux tours juste ; foncé : strictement, seul le tour attendu est juste", petit,
           GRIS)
    x0, y0, x1, y1 = 50, 76, 830, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les tours publiés descendus, graine par graine : sans relance (gris), bornée (vert)", moyen, ENCRE)
    gy0, gy1 = y0 + 50, y1 - 40
    for q in (2, 4, 6):
        yq = gy1 - q / LE_MAX * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 14, int(yq) - 7, str(q), 0, GRIS)
    for n, (gs, gb) in enumerate(zip(d["les_chaines"]["sans relance"]["les_graines"], d["les_chaines"]["bornée"]["les_graines"])):
        xa = x0 + 50 + n * 92
        for m, (nom, g) in enumerate((("sans relance", gs), ("bornée", gb))):
            clair, fonce = LES_TEINTES[nom]
            barre(xa + m * 38, g["la_descente_souple"], clair, (nom, g["le_rang"], "souple"))
            barre(xa + m * 38 + 18, g["la_descente_stricte"], fonce, (nom, g["le_rang"], "stricte"))
        ecrire(int(xa + 26), gy1 + 8, f"g{gs['le_rang']}", 0, ENCRE)

    x0, y0, x1, y1 = 860, 76, 1310, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la médiane des huit graines", moyen, ENCRE)
    for q in (2, 4, 6):
        yq = gy1 - q / LE_MAX * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 14, int(yq) - 7, str(q), 0, GRIS)
    noms = {"sans relance": "sans", "relancée depuis un point": "point", "relancée depuis la spire": "spire", "bornée": "bornée"}
    for n, (nom, c) in enumerate(d["les_chaines"].items()):
        xa = x0 + 60 + n * 100
        clair, fonce = LES_TEINTES[nom]
        barre(xa, la_mediane_souple(c), clair, (nom, "médiane", "souple"))
        barre(xa + 18, c["la_mediane_stricte"], fonce, (nom, "médiane", "stricte"))
        ecrire(int(xa), gy1 + 8, noms[nom], 0, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : où sont posées les surfaces qui retrouvent deux tours, sur les graines 1 à 3.",
           moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_340.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["les_chaines"]["bornée"]["la_mediane_stricte"] = 1.5
    v("★★★ le titre LIT la mesure", " À 1,5 TOURS EN MÉDIANE" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = ([(n, g["le_rang"], k, g[f"la_descente_{k}"]) for gs, gb in zip(d["les_chaines"]["sans relance"]["les_graines"],
                                                                             d["les_chaines"]["bornée"]["les_graines"])
                for n, g in (("sans relance", gs), ("bornée", gb)) for k in ("souple", "stricte")]
               + [(n, "médiane", k, x) for n, c in d["les_chaines"].items()
                  for k, x in (("souple", float(np.median([g["la_descente_souple"] for g in c["les_graines"] if g["le_tour_touche"]]))),
                               ("stricte", c["la_mediane_stricte"]))])
    v("★★★ les barres aux descentes mesurées", traces["barres"] == attendu)
    v("★★★ aucune barre n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2])]
    v("★★★★ aucune barre ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "340_jugee_strictement_jusquou_la_chaine_bornee_descend_elle.png")
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
