"""Là où la chaîne bornée de 335 a une septième surface : l'écart de 5753_-7 et de 5753_-6 aux plages de m7, et l'écart de 5753_-7 à 5753_-6 comparé à celui de 5753_-6 à 5753_-5, graine par graine.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque graine, l'écart médian au centre de la plage de `m7` la plus proche,
de `5753_-6` (clair) et de `5753_-7` (foncé), avec le quart de pas du niveau 2 : si les barres foncées dépassent la ligne et pas les
claires, `5753_-7` n'est pas posé sur `m7` là où `5753_-6` l'est. À droite, l'écart d'un tour au précédent, en pas nominaux, avec la bande
déclarée de 0,75 à 1,25 pas : si les barres claires en sortent aussi, la bande ne sépare pas un bon tour d'un mauvais.

  uv run python src/figures/figure_pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.py \\
      --sortie docs/images/336_pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.png

⚠ Tout vient de la mesure de `336`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
CLAIR = (160, 196, 180)
FONCE = (60, 110, 90)
L_, H_ = 1360, 580
LA_BANDE = 490
LE_MAX_M7 = 8.0
LE_MAX_PAS = 3.5
LE_QUART_L2 = 18.02 / 4.0
LA_BANDE_DU_PAS = (0.75, 1.25)


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    ss = [s for s in d["les_septiemes"] if "5753_-7_et_m7" in s]
    loin = sum(1 for s in ss if s["5753_-7_et_m7"]["lecart_median_voxels"] > s["5753_-6_et_m7"]["lecart_median_voxels"])
    return (f"5753_-7 est plus loin de m7 que 5753_-6 sur {loin} des {len(ss)} graines ; {v['lissue'].split(' ; ')[-1]}").upper()


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

    def panneau(x0, x1, titre, cle_clair, cle_fonce, champ, maximum, lignes, legende, graduations, unite):
        y0, y1 = 76, 470
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 12, y0 + 8, titre, moyen, ENCRE)
        gy0, gy1 = y0 + 50, y1 - 60
        for q in graduations:
            yq = gy1 - q / maximum * (gy1 - gy0)
            art.line([x0 + 50, yq, x1 - 10, yq], fill=TRAIT)
            ecrire(x0 + 10, int(yq) - 7, f"{q:g}".replace(".", ","), 0, GRIS)
        for q in lignes:
            yq = gy1 - q / maximum * (gy1 - gy0)
            art.line([x0 + 50, yq, x1 - 10, yq], fill=ALERTE, width=2)
        ecrire(x0 + 12, y0 + 28, legende, 0, ALERTE)
        for n, s in enumerate(d["les_septiemes"]):
            if cle_clair not in s:
                continue
            xa = x0 + 80 + n * 100
            for dx, cle, col in ((0, cle_clair, CLAIR), (26, cle_fonce, FONCE)):
                h = s[cle][champ]
                if h is None or not 0 <= h <= maximum:
                    traces["ecretes"] += 1
                hh = min(maximum, max(0.0, h or 0.0))
                art.rectangle([xa + dx, gy1 - hh / maximum * (gy1 - gy0), xa + dx + 22, gy1], fill=col)
                traces["boites"].append((xa + dx, gy1 - hh / maximum * (gy1 - gy0), xa + dx + 22, gy1))
                traces["barres"].append((unite, s["le_rang"], cle, h))
                traces["rectangles"].append((len(cadres) - 1, xa + dx, xa + dx + 22))
            ecrire(int(xa + 12), gy1 + 6, f"g{s['le_rang']}", 0, ENCRE)

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "clair : 5753_-6 ; foncé : 5753_-7 ; dans la boîte de la septième surface de chaque graine", petit, GRIS)
    panneau(50, 660, "l'écart médian au centre de la plage de m7 (voxels du niveau 2)", "5753_-6_et_m7", "5753_-7_et_m7",
            "lecart_median_voxels", LE_MAX_M7, [LE_QUART_L2], "la ligne : un quart de pas du niveau 2, 4,5 voxels", (2, 4, 6, 8), "m7")
    panneau(690, 1310, "l'écart au tour précédent (pas nominaux) : -6/-5 clair, -7/-6 foncé", "5753_-6_et_5753_-5",
            "5753_-7_et_5753_-6", "lecart_median_en_pas", LE_MAX_PAS,
            list(LA_BANDE_DU_PAS), "les lignes : la bande déclarée, de 0,75 à 1,25 pas", (1, 2, 3), "pas")

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : lequel, de 5753_-7 ou de m7, est à la bonne place ; et -6/-5 sort aussi de la "
                              "bande déclarée.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_336.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; la lecture ne tranche pas"}
    for s in autre["les_septiemes"]:
        if "5753_-7_et_m7" in s:
            s["5753_-7_et_m7"]["lecart_median_voxels"] = 0.0
    n = sum(1 for s in d["les_septiemes"] if "5753_-7_et_m7" in s)
    v("★★★ le titre LIT la mesure", le_titre(autre) == f"5753_-7 EST PLUS LOIN DE M7 QUE 5753_-6 SUR 0 DES {n} GRAINES ; LA LECTURE NE "
      "TRANCHE PAS", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = ([("m7", s["le_rang"], c, s[c]["lecart_median_voxels"]) for s in d["les_septiemes"] if "5753_-6_et_m7" in s
                for c in ("5753_-6_et_m7", "5753_-7_et_m7")]
               + [("pas", s["le_rang"], c, s[c]["lecart_median_en_pas"]) for s in d["les_septiemes"] if "5753_-6_et_5753_-5" in s
                  for c in ("5753_-6_et_5753_-5", "5753_-7_et_5753_-6")])
    v("★★★ deux barres par graine et par panneau, aux écarts mesurés", traces["barres"] == attendu)
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
                   / "336_pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.png")
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
