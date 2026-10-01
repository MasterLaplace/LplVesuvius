"""Sur la graine 4, côté moins, de PHerc0358 : de la dixième à la seizième surface de la compagne, son compte de m7 et le compte que lui donnent ses voisines sur la même feuille.

⚠⚠ **Ce que cette figure doit rendre évident.** Un point par surface de la compagne et par compte : le compte de `m7` de la compagne en bleu,
le compte de ses voisines en orange ; un trait au douzième saut, que `m7` compte nul. Avant lui, les deux comptes se confondent ; après, la
compagne compte un tour de moins.

  uv run python src/figures/figure_le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.py \\
      --sortie docs/images/391_le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.png

⚠ Tout vient de la mesure de `391`.
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
             / "le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 580
LA_BANDE = 460
X0, X1, HAUT, BAS = 160, 1000, 120, 380
RAYON = 7


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_points(d: dict) -> list[tuple[int, str, int]]:
    """Pour chaque surface de la compagne à partir de la dixième : son compte de m7, et celui de ses voisines s'il existe."""
    out = []
    for h_, w in d["le_compte_des_voisines"].items():
        h = int(h_)
        out.append((h, "la compagne", d["les_comptes_de_la_compagne"][h - 1]))
        if w is not None:
            out.append((h, "ses voisines", w))
    return out


def echelle(d: dict) -> tuple[int, int, int, int]:
    hs = [int(h) for h in d["le_compte_des_voisines"]]
    ws = [w for _, _, w in les_points(d)]
    return min(hs), max(hs), min(ws), max(ws)


def en_xy(d: dict, h: int, w: int) -> tuple[int, int]:
    h0, h1, w0, w1 = echelle(d)
    return (round(X0 + (h - h0) / max(1, h1 - h0) * (X1 - X0)), round(BAS - (w - w0) / max(1, w1 - w0) * (BAS - HAUT)))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    av = [a for a in d["les_avances"].values() if a is not None]
    deux = (f"rapporté à côté, qui ne décide rien : de la dixième à la seizième surface, les voisines avancent d'un tour à chaque saut "
            f"({sum(a == 1 for a in av)} sauts sur {len(av)}) ; m7 compte le douzième saut nul")
    trois = "⚠ ce qui n'est PAS établi : pourquoi m7 compte ce saut nul."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"points": [], "saut": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"graine 4, côté moins : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "par surface de la compagne : son compte de m7 (bleu) et le compte de ses voisines sur la même feuille (orange)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    h0, h1, w0, w1 = echelle(d)
    for w in range(w0, w1 + 1):
        _, y = en_xy(d, h0, w)
        art.line([X0 - 20, y, X1 + 20, y], fill=TRAIT)
        ecrire(x0 + 30, y - 7, f"{w} tours", petit, GRIS)
    for h in range(h0, h1 + 1):
        x, _ = en_xy(d, h, w0)
        ecrire(x - 6, BAS + 16, str(h), petit, GRIS)
    xs, _ = en_xy(d, d["le_saut"], w0)
    art.line([xs, HAUT - 20, xs, BAS + 8], fill=ALERTE, width=2)
    traces["saut"].append(xs)
    ecrire(xs + 6, HAUT - 26, f"saut {d['le_saut']} : m7 compte {d['le_nombre_de_feuilles_de_m7']} feuille", petit, ALERTE)
    for h, qui, w in les_points(d):
        x, y = en_xy(d, h, w)
        dx = -RAYON if qui == "la compagne" else RAYON
        couleur = BLEU if qui == "la compagne" else ORANGE
        art.ellipse([x + dx - RAYON, y - RAYON, x + dx + RAYON, y + RAYON], fill=couleur)
        traces["points"].append((h, qui, w, x + dx, y, couleur))
    ecrire(X0, BAS + 34, "surface de la compagne", petit, GRIS)

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
    tmp = sortie.parent / ".sonde_391.png"
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
    attendu = []
    for h_, w in d["le_compte_des_voisines"].items():
        attendu.append((int(h_), "la compagne", d["les_comptes_de_la_compagne"][int(h_) - 1]))
        if w is not None:
            attendu.append((int(h_), "ses voisines", w))
    v("★★★★ un point par surface pour la compagne, et un pour ses voisines quand elles existent", [t[:3] for t in traces["points"]] == attendu)
    v("★★★★ la compagne en bleu, ses voisines en orange", all(f == (BLEU if q == "la compagne" else ORANGE) for _, q, *_, f in traces["points"]))
    v("★★★★ chaque point est à son compte", all(y == en_xy(d, h, w)[1] for h, _, w, _, y, _ in traces["points"]))
    v("★★★★ le trait est au saut de la mesure", traces["saut"] == [en_xy(d, d["le_saut"], echelle(d)[2])[0]])
    av = [a for a in d["les_avances"].values() if a is not None]
    v("★★★★ la bande compte les avances d'un tour", f"({sum(a == 1 for a in av)} sauts sur {len(av)})" in la_bande(d)[1])
    deux = json.loads(json.dumps(d))
    k = next(iter(deux["les_avances"]))
    deux["les_avances"][k] = 0
    v("★★★★ une avance nulle n'est pas comptée parmi les avances d'un tour", f"({len(av) - 1} sauts sur {len(av)})" in la_bande(deux)[1])
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
                   / "391_le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.png")
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
