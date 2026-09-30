"""Sur PHerc0358, côté par côté : les sauts tenus à la suite depuis la nappe de départ, par la chaîne mixte et par la chaîne qui regrandit d'une maille.

⚠⚠ **Ce que cette figure doit rendre évident.** Une paire de barres par côté, la chaîne mixte en bleu, la chaîne d'une maille en vert ;
sous chaque paire, le côté ; au-dessus de chaque barre, sa suite.

  uv run python src/figures/figure_la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.py \\
      --sortie docs/images/366_la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.png

⚠ Tout vient des mesures de `366` et de `356`.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.json"
LA_MIXTE = RACINE / "docs" / "mesures" / "une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
VERT = (96, 140, 110)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 150, 390
LE_MAXIMUM = 8
LARGEUR = 50


def lire(chemin: Path = LA_MESURE, mixte: Path = LA_MIXTE) -> dict:
    return {"une_maille": json.loads(chemin.read_text()), "la_mixte": json.loads(mixte.read_text())}


def les_suites(d: dict, cle: str) -> dict[tuple[int, str], int]:
    return {(c["le_rang"], c["le_cote"]): c["la_suite"] for c in d[cle]["les_cotes"]}


def les_tenus(d: dict, cle: str) -> list[dict]:
    return [s for c in d[cle]["les_cotes"] for s in c["les_sauts"] if s["tenu"]]


def le_titre(d: dict) -> str:
    v = d["une_maille"]["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return (f"{v['u']:g} sauts à la suite en médiane, contre {v['m']:g} pour la chaîne mixte : {v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['une_maille']['le_verdict']['lissue']}"
    u, m = les_tenus(d, "une_maille"), les_tenus(d, "la_mixte")
    deux = (f"rapporté à côté, qui ne décide rien : elle tient {len(u)} sauts sur 40, contre {len(m)}, et ses surfaces tenues ont "
            f"{statistics.median(s['les_points'] for s in u):g} mailles en médiane, contre "
            f"{statistics.median(s['les_points'] for s in m):g}").replace(".", ",")
    trois = "⚠ ce qui n'est PAS établi : si ces surfaces sont sur leur feuille ; sur PHerc0358, aucun tour ne le dit."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "sur PHerc0358, rouleau sans tracé : les sauts tenus à la suite depuis la nappe de départ, par le critère de 352",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    for i, (nom, couleur) in enumerate((("chaîne mixte", BLEU), ("chaîne d'une maille", VERT))):
        lx = x0 + 12 + i * 200
        art.rectangle([lx, y0 + 12, lx + 12, y0 + 24], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, y0 + 12, y0 + 24))
        ecrire(lx + 18, y0 + 10, nom, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    m, u = les_suites(d, "la_mixte"), les_suites(d, "une_maille")
    cotes = list(u)
    for j, cote in enumerate(cotes):
        centre = x0 + 120 + j * 190
        for i, (cle, suites, couleur) in enumerate((("la_mixte", m, BLEU), ("une_maille", u, VERT))):
            n = suites.get(cote, 0)
            gauche = centre - LARGEUR - 4 if i == 0 else centre + 4
            sommet = BAS - round(min(n, LE_MAXIMUM) / LE_MAXIMUM * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((cote, cle, n, sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            ecrire(gauche + 20, sommet - 18, str(n), petit, ENCRE)
        ecrire(centre - 60, BAS + 8, f"graine {cote[0]}, {cote[1]}", moyen, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 54, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_366.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["une_maille"]["le_verdict"].update({"u": 5, "m": 3, "lissue": "x ; elle tient plus de sauts à la suite"})
    v("★★★ le titre LIT la mesure", le_titre(autre) == ("5 SAUTS À LA SUITE EN MÉDIANE, CONTRE 3 POUR LA CHAÎNE MIXTE : ELLE TIENT PLUS DE "
                                                        "SAUTS À LA SUITE"), le_titre(autre))
    autre["une_maille"]["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [((c["le_rang"], c["le_cote"]), cle, n) for c in d["une_maille"]["les_cotes"]
               for cle, n in (("la_mixte", les_suites(d, "la_mixte")[(c["le_rang"], c["le_cote"])]), ("une_maille", c["la_suite"]))]
    v("★★★★ une paire de barres par côté, la mixte puis la chaîne d'une maille, à leur suite",
      [(c, k, n) for c, k, n, _, _ in traces["barres"]] == attendu, str(traces["barres"]))
    v("★★★★ les mêmes côtés dans les deux mesures", set(les_suites(d, "la_mixte")) == set(les_suites(d, "une_maille")))
    v("★★★★ la mixte en bleu, la chaîne d'une maille en vert",
      all(f == {"la_mixte": BLEU, "une_maille": VERT}[k] for _, k, _, _, f in traces["barres"]))
    v("★★★★ la hauteur de chaque barre est sa suite", all(BAS - s == round(min(n, LE_MAXIMUM) / LE_MAXIMUM * (BAS - HAUT))
                                                          for _, _, n, s, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    u, m = les_tenus(d, "une_maille"), les_tenus(d, "la_mixte")
    v("★★★★ la bande rapporte les sauts tenus des deux chaînes, recomptés", f"elle tient {len(u)} sauts sur 40, contre {len(m)}"
      in la_bande(d)[1] and sum(len(c["les_sauts"]) for c in d["une_maille"]["les_cotes"]) == 40)
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['une_maille']['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for _, _, t, _ in poses))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "366_la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.png")
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
