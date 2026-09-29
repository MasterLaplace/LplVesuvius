"""Pour chaque surface que la descente de la chaîne bornée compte juste, la distance médiane de ses sommets posés au bout de leur tour publié : orange pour les surfaces qui retrouvent deux tours, gris pour celles qui n'en retrouvent qu'un, graine par graine.

⚠⚠ **Ce que cette figure doit rendre évident.** Une marque par tour de chaque surface, à la distance médiane de ses sommets posés au bout de
ce tour, et la ligne de 1280 voxels sous laquelle la règle dit qu'une surface passe par la couture. Si les marques orange sont sous la
ligne et les grises au-dessus, la couture sépare les surfaces à deux tours des autres ; si les grises y sont aussi, la ligne ne sépare rien.

  uv run python src/figures/figure_les_surfaces_a_deux_tours_passent_elles_par_la_couture.py \\
      --sortie docs/images/338_les_surfaces_a_deux_tours_passent_elles_par_la_couture.png

⚠ Tout vient de la mesure de `338`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_surfaces_a_deux_tours_passent_elles_par_la_couture.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
MARQUE_GRISE = (170, 172, 176)
L_, H_ = 1360, 580
LA_BANDE = 490
LE_MAX = 3000.0
LA_COUTURE = 1280.0


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    un = d["les_surfaces_a_un_tour"]
    sous = sum(1 for s in un if all(x is not None and x <= LA_COUTURE for x in s["les_distances_au_bout"].values()))
    return (f"{v['k']} des {v['n']} surfaces à deux tours sous la ligne, mais aussi {sous} des {len(un)} surfaces à un tour").upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"marques": [], "ecretees": 0, "boites": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "orange : une surface qui retrouve deux tours, une marque par tour ; gris : une surface qui n'en retrouve qu'un", petit,
           GRIS)
    x0, y0, x1, y1 = 50, 76, 1310, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la distance médiane des sommets posés au bout de leur tour, en voxels de 2,4 µm, saut par saut", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 28, "la ligne : 1280 voxels, la demi-largeur du plan des nappes", 0, ALERTE)
    gy0, gy1 = y0 + 60, y1 - 40
    for q in (1000, 2000, 3000):
        yq = gy1 - q / LE_MAX * (gy1 - gy0)
        art.line([x0 + 50, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, str(q), 0, GRIS)
    yq = gy1 - LA_COUTURE / LE_MAX * (gy1 - gy0)
    art.line([x0 + 50, yq, x1 - 10, yq], fill=ALERTE, width=2)
    rangs = sorted({s["le_rang"] for s in d["les_surfaces_a_un_tour"] + d["les_surfaces_a_deux_tours"]})
    for n, r in enumerate(rangs):
        xa = x0 + 80 + n * 150
        ecrire(int(xa + 40), gy1 + 8, f"g{r}", 0, ENCRE)
        for genre, surfaces, col in (("un", d["les_surfaces_a_un_tour"], MARQUE_GRISE),
                                     ("deux", d["les_surfaces_a_deux_tours"], ALERTE)):
            for s in surfaces:
                if s["le_rang"] != r:
                    continue
                for m, (t, x) in enumerate(sorted(s["les_distances_au_bout"].items())):
                    if x is None:
                        continue
                    if not 0 <= x <= LE_MAX:
                        traces["ecretees"] += 1
                    cx = xa + s["le_saut"] * 12 + m * 5
                    cy = gy1 - min(LE_MAX, x) / LE_MAX * (gy1 - gy0)
                    art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=col)
                    traces["marques"].append((genre, r, s["le_saut"], t, x))
                    traces["boites"].append((cx - 4, cy - 4, cx + 4, cy + 4))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : qu'une surface à deux tours traverse la couture ; la ligne passe aussi sous "
                              "des surfaces à un tour.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_338.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    for s in autre["les_surfaces_a_un_tour"]:
        s["les_distances_au_bout"] = {k: 9999.0 for k in s["les_distances_au_bout"]}
    v("★★★ le titre LIT la mesure", " MAIS AUSSI 0 DES " in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = sorted((g, s["le_rang"], s["le_saut"], t, x) for g, ss in (("un", d["les_surfaces_a_un_tour"]),
                                                                          ("deux", d["les_surfaces_a_deux_tours"]))
                     for s in ss for t, x in s["les_distances_au_bout"].items() if x is not None)
    v("★★★ une marque par tour de chaque surface comptée, à sa distance mesurée", sorted(traces["marques"]) == attendu)
    v("★★★ aucune marque n'est écrêtée", traces["ecretees"] == 0, str(traces["ecretees"]))
    x0, y0, x1, y1 = cadres[0]
    v("★★★★ aucune marque ne sort du cadre", all(x0 < a and c < x1 and y0 < b and e < y1 for a, b, c, e in traces["boites"]))
    sous = []
    for x, y, t, f in poses:
        a, b, c, e = f.getbbox(t)
        sous += [t for (u0, w0, u1, w1) in traces["boites"] if x + a < u1 and u0 < x + c and y + b < w1 and w0 < y + e]
    v("★★★★ aucun texte ne passe sous une marque", not sous, str(sous[:3]))
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
                   / "338_les_surfaces_a_deux_tours_passent_elles_par_la_couture.png")
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
