"""Sur PHercParis4 : les sauts jugés, rangés par la part de leurs points qui porte le compte majoritaire de m7, les sauts faux en orange.

⚠⚠ **Ce que cette figure doit rendre évident.** Un histogramme des sauts jugés par part majoritaire ; le seuil des deux tiers en trait, les
mélanges à sa gauche, les sauts nets à sa droite ; dans chaque barre, les sauts justes en bleu et les sauts faux en orange. Si les mélanges
sont rares, la figure le montre avant que le verdict ne le dise.

  uv run python src/figures/figure_les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.py \\
      --sortie docs/images/394_les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.png

⚠ Tout vient de la mesure de `394`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 560
LA_BANDE = 440
X0, X1 = 120, 1100
HAUT, BAS = 130, 360
LES_CASES = 20


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_bas(d: dict) -> float:
    """La part la plus basse de l'échelle : un demi si aucune part n'est en dessous, zéro sinon."""
    return 0.5 if all(s["la_part_majoritaire"] >= 0.5 for s in d["les_sauts"]) else 0.0


def en_x(p: float, bas: float) -> int:
    return round(X0 + (p - bas) / (1 - bas) * (X1 - X0))


def les_cases(d: dict) -> list[tuple[int, int]]:
    """Par case de part majoritaire, de la plus basse à la plus haute : les sauts justes et les sauts faux."""
    bas = le_bas(d)
    out = [[0, 0] for _ in range(LES_CASES)]
    for s in d["les_sauts"]:
        i = min(LES_CASES - 1, int((s["la_part_majoritaire"] - bas) / (1 - bas) * LES_CASES))
        out[i][0 if s["juste"] else 1] += 1
    return [tuple(c) for c in out]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    m, n = d["le_bilan"]["melanges"], d["le_bilan"]["nets"]
    faux = [s for s in d["les_sauts"] if not s["juste"]]
    detail = " ; ".join(f"graine {s['le_rang']}, {s['la_chaine']}, saut {s['le_saut']} : m7 compte {s['le_nombre_de_feuilles']}, "
                        f"les tours en disent {s['les_tours']}" for s in faux)
    deux = (f"rapporté à côté, qui ne décide rien : {m['faux']} des {m['juges']} mélanges et {n['faux']} des {n['juges']} sauts nets "
            f"sont faux{' ; ' + detail if detail else ''}")
    trois = "⚠ ce qui n'est PAS établi : ce que vaut la règle sur PHerc0358, où les mélanges sont nombreux."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 420)]
    traces = {"barres": [], "rectangles": [], "seuil": None}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"les sauts mélangés de m7 sur PHercParis4 : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "les sauts jugés par la part de leurs points qui porte le compte majoritaire ; justes en bleu, faux en orange",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([X0, BAS, X1, BAS], fill=GRIS)
    bas = le_bas(d)
    cases = les_cases(d)
    plus = max(j + f for j, f in cases) or 1
    pas = (X1 - X0) / LES_CASES
    for i, (j, f) in enumerate(cases):
        g, dr = round(X0 + i * pas) + 2, round(X0 + (i + 1) * pas) - 2
        sj = BAS - round(j / plus * (BAS - HAUT))
        sf = sj - round(f / plus * (BAS - HAUT))
        if j:
            art.rectangle([g, sj, dr, BAS], fill=BLEU)
            traces["rectangles"].append((g, dr, sj, BAS))
        if f:
            art.rectangle([g, sf, dr, sj], fill=ORANGE)
            traces["rectangles"].append((g, dr, sf, sj))
        traces["barres"].append((i, j, f, sj, sf))
        if j + f:
            ecrire(g + 8, sf - 18, str(j + f), petit, ENCRE)
    for k in range(0, 11):
        p = bas + k * (1 - bas) / 10
        x = en_x(p, bas)
        art.line([x, BAS, x, BAS + 5], fill=GRIS)
        if k % 2 == 0:
            ecrire(x - 12, BAS + 8, f"{p:.1f}".replace(".", ","), petit, GRIS)
    xs = en_x(2 / 3, bas)
    art.line([xs, HAUT - 30, xs, BAS], fill=ALERTE, width=2)
    traces["seuil"] = xs
    ecrire(xs - 92, HAUT - 46, "mélanges  |  nets", moyen, ALERTE)
    ecrire(X0, BAS + 30, "part des points mesurés qui porte le compte majoritaire de m7", moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_394.png"
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
    bas = le_bas(d)
    attendu = [[0, 0] for _ in range(LES_CASES)]
    for s in d["les_sauts"]:
        attendu[min(LES_CASES - 1, int((s["la_part_majoritaire"] - bas) / (1 - bas) * LES_CASES))][0 if s["juste"] else 1] += 1
    v("★★★★ chaque barre compte ses sauts justes et faux, recomptés", [(j, f) for _, j, f, _, _ in traces["barres"]]
      == [tuple(a) for a in attendu])
    v("★★★★ les barres somment aux sauts jugés", sum(j + f for _, j, f, _, _ in traces["barres"]) == len(d["les_sauts"]))
    v("★★★★ les faux somment aux sauts faux", sum(f for _, _, f, _, _ in traces["barres"]) == sum(not s["juste"] for s in d["les_sauts"]))
    v("★★★★ l'échelle ne coupe aucun saut", all(s["la_part_majoritaire"] >= bas for s in d["les_sauts"]))
    v("★★★★ le seuil est aux deux tiers", traces["seuil"] == round(X0 + (2 / 3 - bas) / (1 - bas) * (X1 - X0)))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    m, n = d["le_bilan"]["melanges"], d["le_bilan"]["nets"]
    v("★★★★ la bande rapporte les deux taux", f"{m['faux']} des {m['juges']} mélanges et {n['faux']} des {n['juges']} sauts nets"
      in la_bande(d)[1])
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
                   / "394_les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.png")
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
