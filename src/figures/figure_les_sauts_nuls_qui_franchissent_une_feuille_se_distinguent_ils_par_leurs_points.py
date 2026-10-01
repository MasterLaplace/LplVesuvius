"""Sur PHerc0358 : la part des points qui franchissent une feuille de m7, pour les sauts nuls que les voisines disent restés et pour ceux qu'elles disent franchis.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux rangées de points sur une même échelle de 0 à 1 : les sauts nuls restés en bleu, les
sauts nuls franchis en orange ; si les deux nuées se chevauchent, la part ne les sépare pas.

  uv run python src/figures/figure_les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.py \\
      --sortie docs/images/393_les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.png

⚠ Tout vient de la mesure de `393`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 500
LA_BANDE = 380
X0, X1 = 220, 1000
LES_RANGEES = (("restes", "sauts nuls restés", 170, BLEU), ("franchis", "sauts nuls franchis", 270, ORANGE))
RAYON = 7


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def en_x(p: float) -> int:
    return round(X0 + p * (X1 - X0))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    nets = sum(1 for s in d["les_sauts_nuls"] if s["la_part_dune_feuille"] is not None and s["la_part_dune_feuille"] < 0.1)
    deux = (f"rapporté à côté, qui ne décide rien : {nets} des {len(d['les_sauts_nuls'])} sauts nuls ont moins d'un dixième de leurs points "
            f"à une feuille ; les autres sont des mélanges")
    trois = "⚠ ce qui n'est PAS établi : si un seuil trouvé ici vaudrait ailleurs."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 360)]
    traces = {"points": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"la part d'une feuille des sauts nuls : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "un point par saut nul de m7 : la part de ses points mesurés qui franchissent une feuille", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    for k in range(0, 11, 2):
        x = en_x(k / 10)
        art.line([x, 120, x, 310], fill=TRAIT)
        ecrire(x - 10, 318, f"{k / 10:.1f}".replace(".", ","), petit, GRIS)
    for cle, nom, y, couleur in LES_RANGEES:
        ecrire(x0 + 16, y - 8, nom, moyen, ENCRE)
        vus = {}
        for p in d["le_bilan"][cle]:
            x = en_x(p)
            n = vus.get(round(x / 6), 0)
            vus[round(x / 6)] = n + 1
            yy = y + (n % 3) * 10 - 10
            art.ellipse([x - RAYON, yy - RAYON, x + RAYON, yy + RAYON], fill=couleur)
            traces["points"].append((cle, p, x, couleur))

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
    tmp = sortie.parent / ".sonde_393.png"
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
    v("★★★★ un point par saut, restés puis franchis", [(c, p) for c, p, _, _ in traces["points"]]
      == [("restes", p) for p in d["le_bilan"]["restes"]] + [("franchis", p) for p in d["le_bilan"]["franchis"]])
    v("★★★★ restés en bleu, franchis en orange", all(f == (BLEU if c == "restes" else ORANGE) for c, _, _, f in traces["points"]))
    v("★★★★ chaque point est à sa part", all(x == en_x(p) for _, p, x, _ in traces["points"]))
    nets = sum(1 for s in d["les_sauts_nuls"] if s["la_part_dune_feuille"] is not None and s["la_part_dune_feuille"] < 0.1)
    v("★★★★ la bande compte les sauts nuls nets", f"{nets} des {len(d['les_sauts_nuls'])} sauts nuls" in la_bande(d)[1])
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
                   / "393_les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.png")
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
