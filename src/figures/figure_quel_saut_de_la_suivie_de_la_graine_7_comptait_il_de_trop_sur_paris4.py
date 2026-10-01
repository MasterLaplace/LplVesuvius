"""Sur PHercParis4, graine 7, côté moins : le tour publié que chaque surface de la suivie retrouve, dans 385 et rognée, et le compte de m7 de chaque saut.

⚠⚠ **Ce que cette figure doit rendre évident.** Une courbe par chaîne, la suivie de `385` en bleu et la suivie rognée en orange : en abscisse
la surface, en ordonnée le tour publié qu'elle retrouve ; un saut de trois tours se voit comme une marche de trois. Sous chaque saut, le
nombre de feuilles que `m7` lui donne.

  uv run python src/figures/figure_quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.py \\
      --sortie docs/images/401_quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.png

⚠ Tout vient de la mesure de `401`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 620
LA_BANDE = 500
X0, PAS_X = 230, 90
Y0, PAS_Y = 120, 38
LES_JEUX = (("385", "suivie de 385", BLEU, -6), ("rognees", "suivie rognée", ORANGE, 6))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def en_x(h: int) -> int:
    return X0 + h * PAS_X


def en_y(t: int) -> int:
    return Y0 - t * PAS_Y


def les_points(d: dict, jeu: str) -> list[tuple[int, int]]:
    """Les surfaces de la suivie qui retrouvent un seul tour : (indice, tour), la nappe en tête."""
    return [(h, r[0]) for h, r in enumerate(d["les_chaines"]["suivie"][jeu]["les_tours"]) if len(r) == 1]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    r = d["les_chaines"]["suivie"]["rognees"]["les_sauts"]
    juges = [s for s in r if s["dit"] is not None]
    deux = (f"rapporté à côté, qui ne décide rien : rognée, la suivie a {sum(s['dit'] == 'juste' for s in juges)} sauts justes sur "
            f"{len(juges)} jugés, un tour à chaque saut")
    trois = "⚠ ce qui n'est PAS établi : ce que le rognage fait sur les autres côtés."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 480)]
    traces = {"points": [], "nombres": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"la suivie de la graine 7, côté moins : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "le tour publié que chaque surface retrouve ; sous chaque saut, le nombre de feuilles que m7 lui donne", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    for t in range(0, -8, -1):
        art.line([X0 - 10, en_y(t), en_x(8) + 10, en_y(t)], fill=TRAIT)
        ecrire(X0 - 60, en_y(t) - 7, f"{t}".replace("-", "−"), petit, GRIS)
    ecrire(70, en_y(-3) - 7, "tour publié", petit, ENCRE)
    for h in range(9):
        ecrire(en_x(h) - 4, en_y(-7) + 10, str(h), petit, GRIS)
    ecrire(en_x(4) - 30, en_y(-7) + 26, "surface (0 : la nappe)", petit, ENCRE)
    for jeu, nom, couleur, dx in LES_JEUX:
        pts = les_points(d, jeu)
        for (h, t), (h2, t2) in zip(pts, pts[1:]):
            art.line([en_x(h) + dx, en_y(t), en_x(h2) + dx, en_y(t2)], fill=couleur, width=3)
        for h, t in pts:
            art.ellipse([en_x(h) + dx - 5, en_y(t) - 5, en_x(h) + dx + 5, en_y(t) + 5], fill=couleur)
            traces["points"].append((jeu, h, t))
    for k, (jeu, nom, couleur, _) in enumerate(LES_JEUX):
        art.rectangle([en_x(6) + 60, 110 + k * 22, en_x(6) + 72, 122 + k * 22], fill=couleur)
        ecrire(en_x(6) + 80, 109 + k * 22, nom, petit, ENCRE)
    for k, (jeu, nom, couleur, _) in enumerate(LES_JEUX):
        y = en_y(-7) + 48 + k * 16
        ecrire(70, y, f"m7, {nom}", petit, couleur)
        for s in d["les_chaines"]["suivie"][jeu]["les_sauts"]:
            n = s["le_nombre_de_feuilles"]
            texte = "–" if n is None else str(n)
            ecrire(en_x(s["le_saut"]) - PAS_X // 2 - 3, y, texte, petit, ALERTE if s["dit"] in ("de_trop", "pas_assez") else couleur)
            traces["nombres"].append((jeu, s["le_saut"], texte))

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
    tmp = sortie.parent / ".sonde_401.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "OUI, Y", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    for jeu in ("385", "rognees"):
        attendu = [(jeu, h, r[0]) for h, r in enumerate(d["les_chaines"]["suivie"][jeu]["les_tours"]) if len(r) == 1]
        v(f"★★★★ un point par surface de la suivie {jeu} qui retrouve un seul tour, à son tour", [p for p in traces["points"] if p[0] == jeu]
          == attendu)
        v(f"★★★★ sous chaque saut de {jeu}, son nombre de feuilles", [(h, t) for j, h, t in traces["nombres"] if j == jeu]
          == [(s["le_saut"], "–" if s["le_nombre_de_feuilles"] is None else str(s["le_nombre_de_feuilles"]))
              for s in d["les_chaines"]["suivie"][jeu]["les_sauts"]])
    v("★★★★ les points tiennent dans le cadre", all(cadres[0][1] < en_y(t) < cadres[0][3] for _, _, t in traces["points"]))
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
                   / "401_quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.png")
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
