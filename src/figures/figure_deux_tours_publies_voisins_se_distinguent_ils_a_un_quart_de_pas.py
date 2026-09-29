"""Autour de chaque graine, l'écart médian entre tours publiés consécutifs, en pas nominaux, contre le demi-pas sous lequel une surface à mi-chemin serait à un quart de pas des deux ; et, dans la descente de la chaîne bornée, les surfaces comptées justes qui retrouvent aussi un autre tour.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, une barre par paire de tours voisins, groupées par graine, et la ligne du
demi-pas nominal : une barre sous la ligne serait une paire que la lecture pourrait confondre. Une barre rouge serait une paire confondue.
À droite, pour chaque graine, les surfaces que la descente compte justes et, en orange, celles qui retrouvent aussi un autre tour : si
l'écart ne confond rien et que des surfaces retrouvent pourtant deux tours, l'écart n'en est pas la cause.

  uv run python src/figures/figure_deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.py \\
      --sortie docs/images/337_deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.png

⚠ Tout vient de la mesure de `337`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
ROUGE = (170, 40, 40)
BON = (60, 110, 90)
CLAIR = (190, 192, 196)
L_, H_ = 1360, 580
LA_BANDE = 490
LE_MAX_PAS = 4.0
LE_MAX_SURFACES = 6


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    ds = d["les_descentes_de_336"]
    deux, comptees = sum(x["a_deux_tours"] for x in ds), sum(x["comptees"] for x in ds)
    paires = f"{v['m']} paire confondue" if v["m"] <= 1 else f"{v['m']} paires confondues"
    return f"{paires} sur {v['N']} ; pourtant {deux} des {comptees} surfaces comptées justes retrouvent deux tours".upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "ecretes": 0, "rectangles": [], "boites": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, largeur, h, maximum, col, cle):
        if h is None or not 0 <= h <= maximum:
            traces["ecretes"] += 1
        hh = min(maximum, max(0.0, h or 0.0))
        y = gy1 - hh / maximum * (gy1 - gy0)
        art.rectangle([x, y, x + largeur, gy1], fill=col)
        traces["barres"].append(cle + (h,))
        traces["rectangles"].append((len(cadres) - 1, x, x + largeur))
        traces["boites"].append((x, y, x + largeur, gy1))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "chaque tour lu contre le suivant autour des huit graines, dans un cube de 1280 voxels de demi-côté", petit, GRIS)

    x0, y0, x1, y1 = 50, 76, 900, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "l'écart médian d'un tour au suivant, en pas nominaux, de 0/-1 à -6/-7", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 28, "la ligne : un demi-pas nominal ; en dessous, une surface à mi-chemin serait à un quart de pas des deux", 0,
           ALERTE)
    gy0, gy1 = y0 + 60, y1 - 40
    for q in (1, 2, 3, 4):
        yq = gy1 - q / LE_MAX_PAS * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 12, int(yq) - 7, str(q), 0, GRIS)
    yq = gy1 - 0.5 / LE_MAX_PAS * (gy1 - gy0)
    art.line([x0 + 40, yq, x1 - 10, yq], fill=ALERTE, width=2)
    for n, g in enumerate(d["les_graines"]):
        xa = x0 + 45 + n * 100
        for m, p in enumerate(g["les_paires"]):
            if not p["mesuree"]:
                continue
            barre(xa + m * 12, 9, p["lecart_median_en_pas"], LE_MAX_PAS, ROUGE if p["confondus"] else CLAIR,
                  ("pas", g["le_rang"], tuple(p["les_tours"])))
        ecrire(int(xa + 30), gy1 + 8, f"g{g['le_rang']}", 0, ENCRE)

    x0, y0, x1, y1 = 930, 76, 1310, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les surfaces comptées justes (336)", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 28, "gris : toutes ; orange : qui retrouvent deux tours", 0, ALERTE)
    for q in (2, 4, 6):
        yq = gy1 - q / LE_MAX_SURFACES * (gy1 - gy0)
        art.line([x0 + 30, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 12, int(yq) - 7, str(q), 0, GRIS)
    for n, x in enumerate(d["les_descentes_de_336"]):
        xa = x0 + 40 + n * 42
        barre(xa, 16, x["comptees"], LE_MAX_SURFACES, CLAIR, ("comptées", x["le_rang"]))
        barre(xa + 18, 16, x["a_deux_tours"], LE_MAX_SURFACES, ALERTE, ("à deux tours", x["le_rang"]))
        ecrire(int(xa + 8), gy1 + 8, f"g{x['le_rang']}", 0, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : pourquoi des surfaces retrouvent deux tours voisins, si ce n'est pas leur écart.",
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
    tmp = sortie.parent / ".sonde_337.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update(m=5, N=9)
    for x in autre["les_descentes_de_336"]:
        x["a_deux_tours"], x["comptees"] = 0, 1
    v("★★★ le titre LIT la mesure", le_titre(autre) == f"5 PAIRES CONFONDUES SUR 9 ; POURTANT 0 DES {len(d['les_descentes_de_336'])} "
      "SURFACES COMPTÉES JUSTES RETROUVENT DEUX TOURS", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = ([("pas", g["le_rang"], tuple(p["les_tours"]), p["lecart_median_en_pas"]) for g in d["les_graines"]
                for p in g["les_paires"] if p["mesuree"]]
               + [c for x in d["les_descentes_de_336"] for c in (("comptées", x["le_rang"], x["comptees"]),
                                                                  ("à deux tours", x["le_rang"], x["a_deux_tours"]))])
    v("★★★ une barre par paire mesurée et deux par graine, aux valeurs mesurées", traces["barres"] == attendu)
    v("★★★ aucune barre n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2])]
    v("★★★★ aucune barre ne sort de son cadre", not dehors, str(dehors[:3]))
    sous = []
    for x, y, t, f in poses:
        a, b, c, e = f.getbbox(t)
        sous += [t for (u0, w0, u1, w1) in traces["boites"] if x + a < u1 and u0 < x + c and y + b < w1 and w0 < y + e]
    v("★★★★ aucun texte ne passe sous une barre", not sous, str(sous[:3]))
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
                   / "337_deux_tours_publies_voisins_se_distinguent_ils_a_un_quart_de_pas.png")
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
