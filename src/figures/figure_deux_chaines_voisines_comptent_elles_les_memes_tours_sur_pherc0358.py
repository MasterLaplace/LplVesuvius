"""Sur PHerc0358 : parmi les paires de surfaces d'une chaîne suivie et de sa compagne que l'accord met sur la même feuille, combien ont chaque décalage de sauts.

⚠⚠ **Ce que cette figure doit rendre évident.** Une barre par décalage, le nombre de paires « même feuille » qui l'ont ; la barre du
décalage nul, le seul attendu, en bleu, les autres en orange.

  uv run python src/figures/figure_deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.py \\
      --sortie docs/images/368_deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.png

⚠ Tout vient de la mesure de `368`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"

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
HAUT, BAS = 130, 390
LARGEUR = 60


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_decalages(d: dict) -> list[tuple[int, int]]:
    """Chaque décalage de sauts, de la compagne à la suivie, présent chez les paires « même feuille », et son nombre, du plus petit au plus
    grand, le décalage nul toujours présent."""
    n = {int(k): v for k, v in d["le_bilan"]["les_decalages"].items()}
    n.setdefault(0, 0)
    return sorted(n.items())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return f"{b['tiennent']} paires sur {b['les_paires']} tiennent les comptes : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    t = d["le_bilan"]["la_table"]
    deux = (f"rapporté à côté, qui ne décide rien : au même saut, {t['meme_saut_meme_feuille']} paires sur la même feuille et "
            f"{t['meme_saut_autre_feuille']} sur une autre ; à des sauts différents, {t['autre_saut_meme_feuille']} sur la même feuille")
    trois = "⚠ ce qui n'est PAS établi : laquelle des deux chaînes a glissé, ni si un glissement se voit dans la chaîne seule."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "paires « même feuille » d'une chaîne suivie et de sa compagne, par décalage de sauts ; seul le décalage nul est attendu",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    decalages = les_decalages(d)
    plus = max(n for _, n in decalages) or 1
    pas = (x1 - x0 - 120) // max(1, len(decalages))
    for i, (k, n) in enumerate(decalages):
        gauche = x0 + 70 + i * pas
        sommet = BAS - round(n / plus * (BAS - HAUT))
        couleur = BLEU if k == 0 else ORANGE
        art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
        traces["barres"].append((k, n, sommet, couleur))
        traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
        ecrire(gauche + 24, sommet - 18, str(n), petit, ENCRE)
        ecrire(gauche + 20, BAS + 8, f"{k:+d}" if k else "0", moyen, ENCRE)
    ecrire(x0 + 70, BAS + 30, "décalage : sauts de la compagne moins sauts de la chaîne suivie", petit, GRIS)

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
    tmp = sortie.parent / ".sonde_368.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"tiennent": 9, "les_paires": 10})
    autre["le_verdict"]["lissue"] = "x ; oui, les deux chaînes comptent les mêmes tours"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "9 PAIRES SUR 10 TIENNENT LES COMPTES : OUI, LES DEUX CHAÎNES COMPTENT LES MÊMES TOURS",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    meme = [p for c in d["les_cotes"] for p in c["les_paires"] if p["meme_feuille"]]
    recompte = {}
    for p in meme:
        k = p["le_saut_compagnon"] - p["le_saut_suivi"]
        recompte[k] = recompte.get(k, 0) + 1
    recompte.setdefault(0, 0)
    v("★★★★ une barre par décalage, à son nombre de paires « même feuille », recompté sur les paires",
      [(k, n) for k, n, _, _ in traces["barres"]] == sorted(recompte.items()), str(traces["barres"]))
    v("★★★★ le décalage nul en bleu, les autres en orange", all(f == (BLEU if k == 0 else ORANGE) for k, _, _, f in traces["barres"]))
    plus = max(n for _, n, _, _ in traces["barres"])
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté au plus grand",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for _, n, s, _ in traces["barres"]))
    sans_nul = json.loads(json.dumps(d))
    sans_nul["le_bilan"]["les_decalages"] = {"-1": 3}
    v("★★★ le décalage nul reste montré, même à zéro", [k for k, _ in les_decalages(sans_nul)] == [-1, 0])
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    t = d["le_bilan"]["la_table"]
    v("★★★★ la bande rapporte la table du bilan", f"au même saut, {t['meme_saut_meme_feuille']} paires sur la même feuille" in la_bande(d)[1])
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
                   / "368_deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.png")
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
