"""Sur PHerc0358 : la séparation des deux comptes de m7 dans chaque saut mélangé, comparée à celle des sauts nets, et les deux mélanges extrêmes vus à plat.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, un point par saut sur une échelle de séparation : les mélanges en haut, les sauts
nets en bas, les seuils de 0,2 et 0,5 en trait ; à droite, le mélange le plus entremêlé et le plus séparé, chaque point compté posé à sa
case de la surface d'arrivée et coloré par son compte. Si les deux comptes d'un mélange forment deux plages, la carte le montre.

  uv run python src/figures/figure_les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.py \\
      --sortie docs/images/396_les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.png

⚠ Tout vient de la mesure de `396`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
CLAIR = (196, 199, 204)
VERT = (92, 140, 96)
LES_COULEURS = {0: CLAIR, 1: BLEU, 2: ORANGE, 3: ALERTE}
L_, H_ = 1200, 660
LA_BANDE = 540
X0, X1 = 110, 540
LES_RANGEES = (("les_melanges", "sauts mélangés", 250), ("les_nets", "sauts nets, compte minoritaire", 420))
LES_CASES = 40
RAYON, MONTEE = 4, 8
LES_CARTES = (("le_plus_entremele", "le plus entremêlé", 610), ("le_plus_separe", "le plus séparé", 890))
CARTE_HAUT, CARTE_COTE = 150, 250


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_couleur(compte: int) -> tuple[int, int, int]:
    return LES_COULEURS.get(compte, VERT)


def le_bas(d: dict) -> float:
    toutes = [x["la_separation"] for cle, _, _ in LES_RANGEES for x in d[cle] if x["juge"]]
    return min(0.0, min(toutes, default=0.0))


def en_x(s: float, bas: float) -> int:
    return round(X0 + (s - bas) / (1 - bas) * (X1 - X0))


def la_case(s: float, bas: float) -> int:
    return min(LES_CASES - 1, int((s - bas) / (1 - bas) * LES_CASES))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    n = sorted(x["la_separation"] for x in d["les_nets"] if x["juge"])
    p = f"{n[len(n) // 2]:.2f}".replace(".", ",") if n else "?"
    deux = (f"rapporté à côté, qui ne décide rien : les {len(n)} sauts nets jugés ont une séparation médiane de {p} ; leurs comptes "
            f"minoritaires forment aussi des plages")
    trois = "⚠ ce qui n'est PAS établi : laquelle des deux plages est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 570, 520), (590, 70, 1150, 520)]
    traces = {"points": [], "cases": [], "seuils": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"les points des sauts mélangés de m7 : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "à gauche, la séparation de chaque saut ; à droite, les points comptés à leur case, colorés par leur compte", petit, GRIS)
    for x0, y0, x1, y1 in cadres:
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    bas = le_bas(d)
    for s, nom in ((0.2, "0,2"), (0.5, "0,5")):
        x = en_x(s, bas)
        art.line([x, 110, x, 470], fill=ALERTE)
        traces["seuils"].append((s, x))
        ecrire(x - 10, 92, nom, petit, ALERTE)
    for k in range(0, 11, 2):
        s = bas + k * (1 - bas) / 10
        ecrire(en_x(s, bas) - 10, 480, f"{s:.1f}".replace(".", ","), petit, GRIS)
    ecrire(X0, 498, "séparation des deux comptes les plus portés", petit, ENCRE)
    for cle, nom, base in LES_RANGEES:
        art.line([X0, base + RAYON + 2, X1, base + RAYON + 2], fill=GRIS)
        ecrire(X0, base + 12, nom, petit, ENCRE)
        piles: dict[int, int] = {}
        for m in sorted((x for x in d[cle] if x["juge"]), key=lambda x: x["la_separation"]):
            i = la_case(m["la_separation"], bas)
            h = piles.get(i, 0)
            piles[i] = h + 1
            x = round(X0 + (i + 0.5) * (X1 - X0) / LES_CASES)
            y = base - h * MONTEE
            art.ellipse([x - RAYON, y - RAYON, x + RAYON, y + RAYON], fill=BLEU if cle == "les_melanges" else GRIS)
            traces["points"].append((cle, m["la_separation"], i, y))
    for cle, nom, gauche in LES_CARTES:
        e = d.get(cle)
        if not e:
            continue
        cs = e["les_cases"]
        i0, j0 = min(a for a, _, _ in cs), min(b for _, b, _ in cs)
        n = max(max(a for a, _, _ in cs) - i0, max(b for _, b, _ in cs) - j0) + 1
        t = max(1, CARTE_COTE // n)
        for a, b, c in cs:
            x, y = gauche + (b - j0) * t, CARTE_HAUT + (a - i0) * t
            art.rectangle([x, y, x + t - 1, y + t - 1], fill=la_couleur(c))
            traces["cases"].append((cle, a, b, c, x, y, t))
        ecrire(gauche, CARTE_HAUT - 50, nom, moyen, ENCRE)
        sep = f"{e['la_separation']:.2f}".replace(".", ",")
        ecrire(gauche, CARTE_HAUT - 30, f"graine {e['le_rang']}, {e['le_cote']}, {e['la_chaine']}, saut {e['le_saut']} : {sep}", petit, GRIS)
    x = 610
    for c, nom in ((0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4 et plus")):
        art.rectangle([x, 440, x + 12, 452], fill=la_couleur(c))
        ecrire(x + 18, 440, nom, petit, ENCRE)
        x += 90
    ecrire(610, 466, "feuilles de m7 franchies par le point", petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_396.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "NON, Y", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    for cle, _, _ in LES_RANGEES:
        v(f"★★★★ un point par saut jugé dans la rangée {cle}", sorted(s for c, s, _, _ in traces["points"] if c == cle)
          == sorted(x["la_separation"] for x in d[cle] if x["juge"]))
    bas = le_bas(d)
    v("★★★★ chaque point est dans la case de sa séparation, recalculée",
      all(i == min(LES_CASES - 1, int((s - bas) / (1 - bas) * LES_CASES)) for _, s, i, _ in traces["points"]))
    v("★★★★ les seuils sont à 0,2 et 0,5", [(s, x) for s, x in traces["seuils"]]
      == [(s, round(X0 + (s - bas) / (1 - bas) * (X1 - X0))) for s in (0.2, 0.5)])
    for cle, _, _ in LES_CARTES:
        if d.get(cle):
            v(f"★★★★ la carte {cle} pose chaque point compté, à la couleur de son compte",
              [(a, b, c) for k, a, b, c, *_ in traces["cases"] if k == cle] == [tuple(x) for x in d[cle]["les_cases"]]
              and all(la_couleur(c) == LES_COULEURS.get(c, VERT) for k, _, _, c, *_ in traces["cases"] if k == cle))
    v("★★★★ les deux cartes sont le plus entremêlé et le plus séparé des mélanges jugés",
      d["le_plus_entremele"]["la_separation"] == min(x["la_separation"] for x in d["les_melanges"] if x["juge"])
      and d["le_plus_separe"]["la_separation"] == max(x["la_separation"] for x in d["les_melanges"] if x["juge"]))
    dehors = [c for c in traces["cases"] if not (590 < c[4] and c[4] + c[6] < 1150 and 70 < c[5] and c[5] + c[6] < 430)]
    v("★★★★ les cartes restent dans leur cadre, au-dessus de la légende", not dehors, str(dehors[:3]))
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
                   / "396_les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.png")
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
