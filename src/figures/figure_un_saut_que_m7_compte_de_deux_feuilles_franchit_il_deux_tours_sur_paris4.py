"""Sur PHercParis4 : les sauts jugés des chaînes de 385 et des chaînes rognées, rangés par feuilles de m7 et par tours publiés franchis.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux tableaux, `385` à gauche et les chaînes rognées à droite ; une rangée par nombre de
feuilles que `m7` dit, une colonne par nombre de tours que le saut franchit ; chaque case porte son nombre de sauts, plus foncée qu'elle en
a. La diagonale, où `m7` dit autant de feuilles que de tours, est cerclée. Si les sauts de deux feuilles franchissent deux tours, la case
« 2 feuilles, 2 tours » porte tout ce que la rangée de deux feuilles contient.

  uv run python src/figures/figure_un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.py \
      --sortie docs/images/403_un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.png

⚠ Tout vient de la mesure de `403`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 640
LA_BANDE = 520
LES_VALEURS = (0, 1, 2, 3)
CASE = 66
HAUT = 150
LES_PANNEAUX = (("385", "chaînes de 385", 170, BLEU), ("rognees", "chaînes rognées", 720, ORANGE))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_classe(v) -> int | None:
    """Le rang d'une valeur dans le tableau : 0, 1, 2, ou « 3 et plus »."""
    if v is None:
        return None
    return min(int(v), LES_VALEURS[-1])


def les_cases(tableau: dict[str, int]) -> dict[tuple[int, int], int]:
    """Les sauts d'une famille par (feuilles, tours), les valeurs de trois et plus réunies, les tours négatifs mis à part."""
    out: dict[tuple[int, int], int] = {}
    for k, n in tableau.items():
        f, t = (None if x == "None" else int(x) for x in k.split("|"))
        if f is None or t is None or t < 0:
            continue
        cle = (la_classe(f), la_classe(t))
        out[cle] = out.get(cle, 0) + n
    return out


def les_ecartes(tableau: dict[str, int]) -> int:
    """Les sauts jugés qu'un tableau ne montre pas : sans compte de `m7`, ou qui reculent."""
    return sum(n for k, n in tableau.items() if "None" in k.split("|") or int(k.split("|")[1]) < 0)


def les_non_juges(d: dict, famille: str) -> int:
    """Les sauts d'une famille que `m7` compte de plusieurs feuilles et qu'aucun tour ne juge."""
    return sum(1 for c in d["les_cotes"] for x in c[famille].values() for s in x["les_sauts"]
               if s["dit"] is None and (s["le_nombre_de_feuilles"] or 0) >= 2)


def le_titre(d: dict) -> str:
    p = d["les_sauts_de_plusieurs_feuilles"]
    justes = sum(x["dit"] == "juste" for x in p)
    return (f"sauts jugés de plusieurs feuilles : {len(p)}, dont {justes} sur autant de tours ; "
            f"{d['le_verdict']['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = ("rapporté à côté, qui ne décide rien : les sauts jugés d'une feuille, nuls ou de trois et plus, dans les cases de leur rangée ; "
            f"écartés (sans compte ou qui reculent) : {les_ecartes(d['les_tableaux']['385'])} et {les_ecartes(d['les_tableaux']['rognees'])}")
    trois = "⚠ ce qui n'est PAS établi : ce que vaut un saut de plusieurs feuilles sur PHerc0358, qui n'a pas de tours publiés."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 500)]
    traces = {"cases": [], "rectangles": [], "non_juges": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "chaque case : le nombre de sauts jugés ; une rangée par feuilles de m7, une colonne par tours publiés franchis ; "
           "cerclée, la diagonale", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    for famille, nom, g, couleur in LES_PANNEAUX:
        cases = les_cases(d["les_tableaux"][famille])
        plus = max(cases.values(), default=1) or 1
        ecrire(g, HAUT - 64, nom, moyen, ENCRE)
        ecrire(g + 70, HAUT - 40, "tours publiés franchis", petit, GRIS)
        for j, t in enumerate(LES_VALEURS):
            ecrire(g + j * CASE + 28, HAUT - 20, f"{t}+" if t == LES_VALEURS[-1] else str(t), petit, GRIS)
        for i, f in enumerate(LES_VALEURS):
            y = HAUT + i * CASE
            ecrire(g - 92, y + 26, f"{f}+ feuilles" if f == LES_VALEURS[-1] else f"{f} feuille{'s' if f > 1 else ''}", petit, GRIS)
            for j, t in enumerate(LES_VALEURS):
                x = g + j * CASE
                n = cases.get((f, t), 0)
                fond = tuple(round(FOND[k] + (couleur[k] - FOND[k]) * (0.15 + 0.85 * n / plus)) for k in range(3)) if n else FOND
                art.rectangle([x, y, x + CASE - 4, y + CASE - 4], fill=fond, outline=ENCRE if f == t else TRAIT, width=3 if f == t else 1)
                traces["rectangles"].append((x, x + CASE - 4, y, y + CASE - 4))
                traces["cases"].append((famille, f, t, n, f == t))
                if n:
                    ecrire(x + 22, y + 24, str(n), moyen, FOND if n / plus > 0.5 else ENCRE)
        k = les_non_juges(d, famille)
        traces["non_juges"].append((famille, k))
        ecrire(g - 92, HAUT + len(LES_VALEURS) * CASE + 14,
               f"de plusieurs feuilles mais non jugés, faute de tour retrouvé aux deux bouts : {k}", petit, couleur)

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
    tmp = sortie.parent / ".sonde_403.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui"}
    autre["les_sauts_de_plusieurs_feuilles"] = [{"dit": "juste"}] * 6 + [{"dit": "de_trop"}]
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SAUTS JUGÉS DE PLUSIEURS FEUILLES : 7, DONT 6 SUR AUTANT DE TOURS ; OUI",
      le_titre(autre))
    v("★★★★ les cases réunissent trois et plus, et mettent à part ce qui recule ou n'a pas de compte",
      les_cases({"2|2": 3, "3|4": 1, "4|3": 2, "1|-1": 5, "None|1": 7}) == {(2, 2): 3, (3, 3): 3}
      and les_ecartes({"2|2": 3, "1|-1": 5, "None|1": 7}) == 12)
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    for famille, _, _, _ in LES_PANNEAUX:
        montres = sum(c[3] for c in traces["cases"] if c[0] == famille)
        v(f"★★★★ les cases de {famille} et ses écartés somment à ses sauts jugés",
          montres + les_ecartes(d["les_tableaux"][famille]) == sum(d["les_tableaux"][famille].values()))
        deux = sum(n for k, n in d["les_tableaux"][famille].items() if k.split("|")[0] == "2" and k.split("|")[1] != "None"
                   and int(k.split("|")[1]) >= 0)
        v(f"★★★★ la rangée de deux feuilles de {famille} porte ses sauts de deux feuilles",
          sum(c[3] for c in traces["cases"] if c[0] == famille and c[1] == 2) == deux)
    v("★★★★ les non jugés de plusieurs feuilles sont ceux de la mesure",
      [k for _, k in traces["non_juges"]] == [sum(1 for c in d["les_cotes"] for x in c[f].values() for s in x["les_sauts"]
                                                  if s["dit"] is None and s["le_nombre_de_feuilles"] is not None
                                                  and s["le_nombre_de_feuilles"] >= 2) for f, _, _, _ in LES_PANNEAUX])
    v("★★★★ la diagonale est celle où les feuilles égalent les tours", all(c[4] == (c[1] == c[2]) for c in traces["cases"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ aucune case ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "403_un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.png")
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
