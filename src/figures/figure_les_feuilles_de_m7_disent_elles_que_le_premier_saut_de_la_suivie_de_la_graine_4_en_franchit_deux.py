"""Sur la graine 4, côté plus, de PHerc0358 : combien de feuilles de m7 les points du premier saut de chaque chaîne franchissent, et combien en séparent les nappes de départ.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour le premier saut de la suivie, de la compagne et de la tierce, les points
mesurés qui franchissent zéro, une et deux feuilles, avec le genre que `369` donne au saut et son écart en pas. À droite, les points de la
nappe de la compagne et de celle de la tierce, comptés contre la nappe de la suivie.

  uv run python src/figures/figure_les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.py \\
      --sortie docs/images/383_les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.png

⚠ Tout vient de la mesure de `383`.
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
LA_MESURE = (RACINE / "docs" / "mesures"
             / "les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1300, 580
LA_BANDE = 450
HAUT, BAS = 140, 340
LARGEUR = 30
LES_FEUILLES = (("0", CLAIR), ("1", BLEU), ("2", ORANGE))
LES_CHAINES = ("suivie", "compagne", "tierce")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_barres(d: dict) -> list[tuple[str, str, dict]]:
    """Les groupes de barres, dans l'ordre : le premier saut de chaque chaîne, puis les nappes de la compagne et de la tierce."""
    return ([("saut", x, d["les_sauts"][x][0]) for x in LES_CHAINES]
            + [("nappe", x, d["les_nappes"][x]) for x in ("compagne", "tierce")])


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    f = d["les_sauts"]["suivie"][0]["le_nombre_de_feuilles"]
    return (f"le premier saut de la suivie franchit {f} feuille{'s' if f > 1 else ''} de m7 : "
            f"{v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    tous = [s for x in LES_CHAINES for s in d["les_sauts"][x] if s["le_nombre_de_feuilles"] is not None]
    deux = (f"rapporté à côté, qui ne décide rien : des {len(tous)} sauts des trois chaînes dont le nombre est dit, "
            f"{sum(s['le_nombre_de_feuilles'] == 1 for s in tous)} franchissent une feuille ; 369 en compte "
            f"{sum(s['le_genre'] == 'double' for x in LES_CHAINES for s in d['les_sauts'][x])} doubles")
    trois = "⚠ ce qui n'est PAS établi : si m7 manque une feuille entre deux surfaces, un saut qui en franchit deux y compte pour une."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 790, 430), (830, 70, 1250, 430)]
    traces = {"barres": [], "rectangles": [], "dessous": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "les points mesurés qui franchissent zéro (gris), une (bleu) et deux (orange) feuilles de m7", petit, GRIS)
    for (x0, y0, x1, y1), titre in zip(cadres, ("le premier saut de chaque chaîne", "les nappes, contre celle de la suivie")):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS, width=1)
        ecrire(x0 + 16, y0 + 12, titre, moyen, ENCRE)
    groupes = les_barres(d)
    plus = max((g["les_comptes"].get(k, 0) for _, _, g in groupes for k, _ in LES_FEUILLES), default=0) or 1
    for i, (genre, x, g) in enumerate(groupes):
        gauche = (cadres[0][0] + 50 + i * 240) if genre == "saut" else (cadres[1][0] + 50 + (i - 3) * 190)
        for j, (k, couleur) in enumerate(LES_FEUILLES):
            n = g["les_comptes"].get(k, 0)
            gg = gauche + j * (LARGEUR + 6)
            sommet = BAS - round(n / plus * (BAS - HAUT))
            if n:
                art.rectangle([gg, sommet, gg + LARGEUR, BAS], fill=couleur)
                traces["rectangles"].append((gg, gg + LARGEUR, sommet, BAS))
            traces["barres"].append((genre, x, k, n, sommet, couleur))
            ecrire(gg + 4, sommet - 18, str(n), petit, ENCRE)
        ecrire(gauche, BAS + 10, f"la {x}", moyen, ENCRE)
        if genre == "saut":
            sous = f"369 : {g['le_genre']}, {g['lecart_median'] / 20.0:.2f} pas".replace(".", ",")
        else:
            sous = f"{g['les_mesures']} points mesurés"
        ecrire(gauche, BAS + 32, sous, petit, GRIS)
        traces["dessous"].append((genre, x, sous))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_383.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["les_sauts"]["suivie"][0]["le_nombre_de_feuilles"] = 2
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LE PREMIER SAUT DE LA SUIVIE FRANCHIT 2 FEUILLES DE M7 : OUI", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = ([("saut", x, k, d["les_sauts"][x][0]["les_comptes"].get(k, 0)) for x in ("suivie", "compagne", "tierce") for k in ("0", "1", "2")]
               + [("nappe", x, k, d["les_nappes"][x]["les_comptes"].get(k, 0)) for x in ("compagne", "tierce") for k in ("0", "1", "2")])
    v("★★★★ trois barres par groupe, zéro, une et deux feuilles, les premiers sauts puis les nappes", [b[:4] for b in traces["barres"]] == attendu,
      str(traces["barres"][:3]))
    v("★★★★ zéro en gris clair, une en bleu, deux en orange",
      all(f == {"0": CLAIR, "1": BLEU, "2": ORANGE}[k] for _, _, k, _, _, f in traces["barres"]))
    plus = max(n for _, _, _, n, _, _ in traces["barres"])
    v("★★★★ la hauteur de chaque barre est son nombre de points, rapporté à la plus haute",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for _, _, _, n, s, _ in traces["barres"]))
    sous = ([("saut", x, f"369 : {d['les_sauts'][x][0]['le_genre']}, {d['les_sauts'][x][0]['lecart_median'] / 20.0:.2f} pas".replace(".", ","))
             for x in ("suivie", "compagne", "tierce")]
            + [("nappe", x, f"{d['les_nappes'][x]['les_mesures']} points mesurés") for x in ("compagne", "tierce")])
    v("★★★★ sous chaque saut, le genre de 369 et l'écart en pas ; sous chaque nappe, les points mesurés", traces["dessous"] == sous,
      str(traces["dessous"]))
    dehors = [r for r in traces["rectangles"] if not any(x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1 for x0, y0, x1, y1 in cadres)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ chaque groupe de saut est dans le cadre de gauche, chaque groupe de nappe dans celui de droite",
      all((cadres[0][0] < r[0] < cadres[0][2]) == (b[0] == "saut") for b, r in zip([b for b in traces["barres"] if b[3]], traces["rectangles"])))
    tous = [s for x in ("suivie", "compagne", "tierce") for s in d["les_sauts"][x] if s["le_nombre_de_feuilles"] is not None]
    v("★★★★ la bande compte les sauts dits et ceux qui franchissent une feuille",
      f"des {len(tous)} sauts des trois chaînes dont le nombre est dit, {sum(s['le_nombre_de_feuilles'] == 1 for s in tous)} franchissent"
      in la_bande(d)[1])
    deux = json.loads(json.dumps(d))
    deux["les_sauts"]["tierce"][1]["le_nombre_de_feuilles"] = 2
    v("★★★★ un saut de deux feuilles n'est pas compté parmi ceux qui en franchissent une",
      f", {len(tous) - 1} franchissent une feuille" in la_bande(deux)[1], la_bande(deux)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
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
                   / "383_les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.png")
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
