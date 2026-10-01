"""Sur PHerc0358 : pour chaque genre que 369 donne aux sauts, combien franchissent zéro, une, deux feuilles de m7 et plus ; et, côté par côté, les surfaces que l'accord valide aux comptes de 369 et aux comptes de m7.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, par genre de `369` (nul, simple, double), quatre barres : les sauts dont `m7`
dit qu'ils franchissent zéro (gris), une (bleu), deux (orange) feuilles, et plus (brun). À droite, par côté où l'accord valide une surface
d'une façon ou de l'autre, les validées aux comptes de `369` (gris) et de `m7` (bleu), et dessous le plus grand compte validé de chacun.

  uv run python src/figures/figure_les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.py \\
      --sortie docs/images/384_les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.png

⚠ Tout vient de la mesure de `384`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
BRUN = (130, 82, 50)
L_, H_ = 1300, 600
LA_BANDE = 470
HAUT, BAS = 150, 350
LARGEUR = 26
LES_GENRES = ("nul", "simple", "double")
LES_FEUILLES = (("zero", CLAIR), ("une", BLEU), ("deux", ORANGE), ("plus", BRUN))
LES_COMPTES = (("avec_369", CLAIR), ("avec_m7", BLEU))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_cotes_valides(d: dict) -> list[dict]:
    """Les côtés où l'accord valide au moins une surface, aux comptes de `369` ou de `m7`, dans l'ordre de la mesure."""
    return [c for c in d["les_cotes"] if c["avec_369"]["validees"] or c["avec_m7"]["validees"]]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    dd = d["les_genres"]["double"]
    return (f"{dd['une']} des {dd['dits']} sauts que 369 compte doubles ne franchissent qu'une feuille de m7 : "
            f"{v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    cs = les_cotes_valides(d)
    a, b = (sum(c[k]["validees"] for c in cs) for k in ("avec_369", "avec_m7"))
    s = d["les_genres"]["simple"]
    deux = (f"rapporté à côté, qui ne décide rien : l'accord valide {a} surfaces aux comptes de 369, {b} aux comptes de m7 ; contrôle : "
            f"{s['une']} des {s['dits']} sauts simples dits franchissent une feuille")
    trois = "⚠ ce qui n'est PAS établi : si une surface validée aux comptes de m7 est sur la bonne feuille."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 560, 450), (600, 70, 1250, 450)]
    traces = {"genres": [], "cotes": [], "rectangles": [], "dessous": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    def barre(g, n, plus, couleur):
        sommet = BAS - round(n / plus * (BAS - HAUT))
        if n:
            art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
            traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
        ecrire(g + 3, sommet - 18, str(n), petit, ENCRE)
        return sommet

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "à gauche, les sauts par genre de 369 et par feuilles de m7 franchies : zéro (gris), une (bleu), deux (orange), plus "
                   "(brun) ; à droite, les validées", petit, GRIS)
    for (x0, y0, x1, y1), titre in zip(cadres, ("les sauts, par genre de 369", "les surfaces validées, aux comptes de 369 et de m7")):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS, width=1)
        ecrire(x0 + 16, y0 + 12, titre, moyen, ENCRE)
    g_ = d["les_genres"]
    plus = max(g_[g][k] for g in LES_GENRES for k, _ in LES_FEUILLES) or 1
    for i, g in enumerate(LES_GENRES):
        gauche = cadres[0][0] + 40 + i * 160
        for j, (k, couleur) in enumerate(LES_FEUILLES):
            s = barre(gauche + j * (LARGEUR + 4), g_[g][k], plus, couleur)
            traces["genres"].append((g, k, g_[g][k], s, couleur))
        ecrire(gauche, BAS + 10, g, moyen, ENCRE)
        ecrire(gauche, BAS + 32, f"{g_[g]['dits']} dits sur {g_[g]['les_sauts']}", petit, GRIS)
    cs = les_cotes_valides(d)
    plus2 = max((c[k]["validees"] for c in cs for k, _ in LES_COMPTES), default=0) or 1
    for i, c in enumerate(cs):
        gauche = cadres[1][0] + 40 + i * 100
        for j, (k, couleur) in enumerate(LES_COMPTES):
            s = barre(gauche + j * (LARGEUR + 4), c[k]["validees"], plus2, couleur)
            traces["cotes"].append((c["le_rang"], c["le_cote"], k, c[k]["validees"], s, couleur))
        ecrire(gauche, BAS + 10, f"{c['le_rang']} {c['le_cote']}", moyen, ENCRE)
        f_ = lambda x: "—" if x is None else str(x)  # noqa: E731
        sous = f"→ {f_(c['avec_369']['le_plus_loin'])} | {f_(c['avec_m7']['le_plus_loin'])}"
        ecrire(gauche, BAS + 32, sous, petit, GRIS)
        traces["dessous"].append((c["le_rang"], c["le_cote"], sous))

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
    tmp = sortie.parent / ".sonde_384.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["les_genres"]["double"].update({"une": 2, "dits": 9})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "2 DES 9 SAUTS QUE 369 COMPTE DOUBLES NE FRANCHISSENT QU'UNE FEUILLE DE M7 : EN PARTIE",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    ag = [(g, k, d["les_genres"][g][k]) for g in ("nul", "simple", "double") for k in ("zero", "une", "deux", "plus")]
    v("★★★★ quatre barres par genre, nul, simple, double, lues dans la mesure", [t[:3] for t in traces["genres"]] == ag,
      str(traces["genres"][:4]))
    v("★★★★ zéro en gris, une en bleu, deux en orange, plus en brun",
      all(f == {"zero": CLAIR, "une": BLEU, "deux": ORANGE, "plus": BRUN}[k] for _, k, _, _, f in traces["genres"]))
    p1 = max(n for _, _, n, _, _ in traces["genres"])
    v("★★★★ la hauteur d'une barre de genre est son nombre, rapporté à la plus haute",
      all(BAS - s == round(n / p1 * (BAS - HAUT)) for _, _, n, s, _ in traces["genres"]))
    v("★★★★ les barres d'un genre somment à ses sauts dits",
      all(sum(n for g_, _, n, _, _ in traces["genres"] if g_ == g) == d["les_genres"][g]["dits"] for g in ("nul", "simple", "double")))
    cs = [c for c in d["les_cotes"] if c["avec_369"]["validees"] or c["avec_m7"]["validees"]]
    ac = [(c["le_rang"], c["le_cote"], k, c[k]["validees"]) for c in cs for k in ("avec_369", "avec_m7")]
    v("★★★★ deux barres par côté validé, aux comptes de 369 puis de m7", [t[:4] for t in traces["cotes"]] == ac, str(traces["cotes"][:2]))
    v("★★★★ aux comptes de 369 en gris, de m7 en bleu", all(f == {"avec_369": CLAIR, "avec_m7": BLEU}[k] for _, _, k, _, _, f in traces["cotes"]))
    p2 = max(n for *_, n, _, _ in traces["cotes"])
    v("★★★★ la hauteur d'une barre de côté est son nombre de validées, rapporté à la plus haute",
      all(BAS - s == round(n / p2 * (BAS - HAUT)) for *_, n, s, _ in traces["cotes"]))
    f_ = lambda x: "—" if x is None else str(x)  # noqa: E731
    v("★★★★ sous chaque côté, le plus grand compte validé de 369 puis de m7",
      traces["dessous"] == [(c["le_rang"], c["le_cote"], f"→ {f_(c['avec_369']['le_plus_loin'])} | {f_(c['avec_m7']['le_plus_loin'])}")
                            for c in cs])
    dehors = [r for r in traces["rectangles"] if not any(x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1 for x0, y0, x1, y1 in cadres)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    a, b = (sum(c[k]["validees"] for c in cs) for k in ("avec_369", "avec_m7"))
    v("★★★★ la bande rapporte les validées des deux comptes et le contrôle",
      f"l'accord valide {a} surfaces aux comptes de 369, {b} aux comptes de m7" in la_bande(d)[1]
      and f"{d['les_genres']['simple']['une']} des {d['les_genres']['simple']['dits']} sauts simples dits" in la_bande(d)[1])
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
                   / "384_les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.png")
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
