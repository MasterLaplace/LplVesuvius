"""Sur PHerc0358, à seize sauts : pour les sauts que m7 compte nuls, d'une feuille et de deux, de combien de tours les surfaces voisines des deux autres chaînes les font avancer.

⚠⚠ **Ce que cette figure doit rendre évident.** Trois groupes, un par nombre de feuilles que `m7` donne au saut ; dans chacun, une barre par
avance des voisines, de moins un tour ou moins (≤ −1) à deux tours ou plus (≥ 2) ; la barre de l'avance attendue (égale au nombre de feuilles) en bleu, les
autres en orange.

  uv run python src/figures/figure_les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.py \\
      --sortie docs/images/392_les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.png

⚠ Tout vient de la mesure de `392`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 580
LA_BANDE = 460
HAUT, BAS = 140, 350
LARGEUR = 40
LES_NOMBRES = ("0", "1", "2")
LES_AVANCES = (("≤ −1", lambda a: a <= -1), ("0", lambda a: a == 0), ("1", lambda a: a == 1), ("≥ 2", lambda a: a >= 2))
ATTENDUE = {"0": "0", "1": "1", "2": "≥ 2"}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_comptes(d: dict, n: str) -> list[tuple[str, int]]:
    """Pour les sauts de `n` feuilles dont l'avance est dite, combien par classe d'avance."""
    pa = {int(a): m for a, m in d["le_bilan"].get(n, {"par_avance": {}})["par_avance"].items()}
    return [(nom, sum(m for a, m in pa.items() if f(a))) for nom, f in LES_AVANCES]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    z = d["le_bilan"]["0"]
    return (f"sauts nuls de m7 : {z['par_avance'].get('0', 0)} sur {z['dits']} restés sur leur feuille : "
            f"{v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    u = d["le_bilan"]["1"]
    deux = (f"rapporté à côté, qui ne décide rien : contrôle, {u['par_avance'].get('1', 0)} des {u['dits']} sauts d'une feuille avancent "
            f"d'un tour chez les voisines")
    trois = "⚠ ce qui n'est PAS établi : pourquoi m7 compte un saut nul, ni ce que vaut l'avance quand les voisines comptent faux."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 440)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par nombre de feuilles que m7 donne au saut : de combien de tours les voisines le font avancer ; l'avance attendue en bleu",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS)
    for i, n in enumerate(LES_NOMBRES):
        cs = les_comptes(d, n)
        total = sum(m for _, m in cs) or 1
        gauche = x0 + 60 + i * 350
        for j, (nom, m) in enumerate(cs):
            g = gauche + j * (LARGEUR + 24)
            sommet = BAS - round(m / total * (BAS - HAUT))
            couleur = BLEU if nom == ATTENDUE[n] else ORANGE
            if m:
                art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
                traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            traces["barres"].append((n, nom, m, sommet, couleur))
            ecrire(g + 12, sommet - 18, str(m), petit, ENCRE)
            ecrire(g, BAS + 8, nom, petit, GRIS)
        ecrire(gauche, BAS + 34, f"m7 : {n} feuille{'s' if n == '2' else ''}, {sum(m for _, m in cs)} sauts", moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_392.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"]["0"] = {"dits": 9, "par_avance": {"0": 2}}
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SAUTS NULS DE M7 : 2 SUR 9 RESTÉS SUR LEUR FEUILLE : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    for n in ("0", "1", "2"):
        pa = {int(a): m for a, m in d["le_bilan"][n]["par_avance"].items()}
        attendu = [(n, "≤ −1", sum(m for a, m in pa.items() if a <= -1)), (n, "0", pa.get(0, 0)), (n, "1", pa.get(1, 0)),
                   (n, "≥ 2", sum(m for a, m in pa.items() if a >= 2))]
        v(f"★★★★ les quatre barres des sauts de {n} feuilles, recomptées", [b[:3] for b in traces["barres"] if b[0] == n] == attendu)
        v(f"★★★★ les barres des sauts de {n} feuilles somment aux sauts dits", sum(b[2] for b in traces["barres"] if b[0] == n)
          == d["le_bilan"][n]["dits"])
    v("★★★★ l'avance attendue en bleu, les autres en orange",
      all(f == (BLEU if nom == {"0": "0", "1": "1", "2": "≥ 2"}[n] else ORANGE) for n, nom, _, _, f in traces["barres"]))
    v("★★★★ la hauteur d'une barre est sa part des sauts de son groupe",
      all(BAS - s == round(m / (d["le_bilan"][n]["dits"] or 1) * (BAS - HAUT)) for n, _, m, s, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte le contrôle", f"{d['le_bilan']['1']['par_avance'].get('1', 0)} des {d['le_bilan']['1']['dits']} sauts d'une feuille"
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
                   / "392_les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.png")
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
