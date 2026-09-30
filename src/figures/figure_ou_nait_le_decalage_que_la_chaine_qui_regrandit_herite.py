"""Sur PHercParis4, sur les côtés jugés par `363` : les points hors de leur tour, surface par surface, nappe de départ comprise, sous la chaîne mixte et sous la chaîne qui regrandit.

⚠⚠ **Ce que cette figure doit rendre évident.** Un cadre par côté jugé ; dans chacun, une paire de barres par surface, la nappe de départ
d'abord, la chaîne mixte en bleu, la chaîne qui regrandit en orange, et un trait au seuil de 50 points.

  uv run python src/figures/figure_ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.py \\
      --sortie docs/images/363_ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.png

⚠ Tout vient de la mesure de `363`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 590
LA_BANDE = 470
LES_CHAINES = (("la_chaine_mixte", "chaîne mixte", BLEU), ("la_chaine_qui_regrandit", "chaîne qui regrandit", ORANGE))
LE_SEUIL = 50
LE_PLAFOND = 1000


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_cotes(d: dict) -> list[tuple[int, str]]:
    return [(x["le_rang"], x["le_cote"]) for x in d["les_bilans"]["la_chaine_qui_regrandit"]["le_detail"]]


def la_suite(d: dict, chaine: str, cote: tuple[int, str]) -> list[int]:
    return next(x["hors_de_son_tour"] for x in d["les_bilans"][chaine]["le_detail"] if (x["le_rang"], x["le_cote"]) == cote)


def le_titre(d: dict) -> str:
    return d["le_verdict"]["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = ("les nappes des graines 4, 5, 7 et 8 ne retrouvent aucun tour : leur chaîne atteint 5753_0 au premier ou au deuxième saut, "
            "elles sont au-dessus, sur un tour non publié")
    trois = "⚠ ce qui n'est PAS établi : où naît le décalage sur ces côtés ; un côté plus se lit contre des tours qui ne sont pas publiés."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(15, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "rectangles": [], "seuils": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "points hors de leur tour, par surface : la nappe de départ, puis la surface gardée à chaque saut ; hauteur plafonnée à "
                   f"{LE_PLAFOND}", petit, GRIS)
    cotes = les_cotes(d)
    largeur = (1000 - 20 * (len(cotes) - 1)) // max(1, len(cotes))
    for j, cote in enumerate(cotes):
        x0 = 50 + j * (largeur + 20)
        x1, y0, y1 = x0 + largeur, 76, 440
        cadres.append((x0, y0, x1, y1))
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        ecrire(x0 + 12, y0 + 8, f"graine {cote[0]}, côté {cote[1]}", moyen, ENCRE)
        haut, bas = y0 + 70, y1 - 40
        suites = {k: la_suite(d, k, cote) for k, _, _ in LES_CHAINES}
        n = max(len(s) for s in suites.values())
        pas = (largeur - 40) // max(1, n)
        ys = bas - round(LE_SEUIL / LE_PLAFOND * (bas - haut))
        art.line([x0 + 20, ys, x1 - 20, ys], fill=ALERTE, width=1)
        traces["seuils"].append((cote, ys))
        for i in range(n):
            gx = x0 + 20 + i * pas
            for c, (k, _, couleur) in enumerate(LES_CHAINES):
                v_ = suites[k][i] if i < len(suites[k]) else None
                if v_ is None:
                    continue
                bx = gx + 4 + c * (pas // 2 - 4)
                sommet = bas - round(min(v_, LE_PLAFOND) / LE_PLAFOND * (bas - haut))
                art.rectangle([bx, sommet, bx + pas // 2 - 8, bas], fill=couleur)
                traces["barres"].append((cote, k, i, v_, sommet, couleur))
                traces["rectangles"].append((j, bx, bx + pas // 2 - 8, sommet, bas))
            ecrire(gx + 6, bas + 6, "nappe" if i == 0 else f"s{i}", petit, GRIS)
        for c, (k, nom, couleur) in enumerate(LES_CHAINES):
            lx = x0 + 12 + c * 170
            art.rectangle([lx, y0 + 34, lx + 12, y0 + 46], fill=couleur)
            traces["rectangles"].append((j, lx, lx + 12, y0 + 34, y0 + 46))
            ecrire(lx + 18, y0 + 32, nom, petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_363.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "sur 4 côtés jugés, x ; il naît dans une croissance"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SUR 4 CÔTÉS JUGÉS, X ; IL NAÎT DANS UNE CROISSANCE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ un cadre par côté jugé", len(cadres) == d["les_bilans"]["la_chaine_qui_regrandit"]["les_cotes_juges"])
    attendu = [(c, k, i, x) for c in les_cotes(d) for i in range(max(len(la_suite(d, k2, c)) for k2, _, _ in LES_CHAINES))
               for k, _, _ in LES_CHAINES if i < len(la_suite(d, k, c)) for x in [la_suite(d, k, c)[i]]]
    v("★★★★ une barre par surface et par chaîne, à son compte, la nappe d'abord",
      sorted((tuple(c), k, i, x) for c, k, i, x, _, _ in traces["barres"]) == sorted((tuple(c), k, i, x) for c, k, i, x in attendu))
    v("★★★★ la chaîne mixte en bleu, la chaîne qui regrandit en orange",
      all(f == {"la_chaine_mixte": BLEU, "la_chaine_qui_regrandit": ORANGE}[k] for _, k, _, _, _, f in traces["barres"]))
    haut_bas = {}
    for j, (x0, y0, x1, y1) in enumerate(cadres):
        haut_bas[j] = (y0 + 70, y1 - 40)
    v("★★★★ la hauteur de chaque barre est son compte, plafonné",
      all(bas - s == round(min(x, LE_PLAFOND) / LE_PLAFOND * (bas - haut))
          for (c, _, _, x, s, _) in traces["barres"] for haut, bas in [haut_bas[les_cotes(d).index(c)]]))
    grand = json.loads(json.dumps(d))
    grand["les_bilans"]["la_chaine_qui_regrandit"]["le_detail"][0]["hors_de_son_tour"][1] = 3 * LE_PLAFOND
    tmp2 = tmp.with_name(".sonde_363_grand.png")
    _, _, cadres2, t2 = dessiner(grand, tmp2)
    tmp2.unlink(missing_ok=True)
    v("★★★★ une barre au-delà du plafond s'arrête au haut du cadre",
      [s for c, k, i, x, s, _ in t2["barres"] if x == 3 * LE_PLAFOND] == [cadres2[0][1] + 70])
    v("★★★★ le trait du seuil est à 50 points", all(haut_bas[j][1] - ys == round(LE_SEUIL / LE_PLAFOND * (haut_bas[j][1] - haut_bas[j][0]))
                                                  for j, (_, ys) in enumerate(traces["seuils"])))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    textes = {t for _, _, t, _ in poses}
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for t in textes))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "363_ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.png")
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
