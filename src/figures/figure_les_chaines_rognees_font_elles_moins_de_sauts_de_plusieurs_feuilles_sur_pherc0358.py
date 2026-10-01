"""Sur PHerc0358, à seize sauts : côté par côté, les sauts que m7 compte de plusieurs feuilles et les sauts nuls, dans les chaînes de 389, les chaînes rognées de 397 et les mêmes comptées entières.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux panneaux, les sauts de plusieurs feuilles à gauche et les sauts nuls à droite ; une
rangée par côté qui a un saut de plusieurs feuilles dans l'une des trois mesures ; dans chaque rangée, trois barres : `389` en bleu, `397`
en orange, `399` en vert. Si le rognage évite les sauts de plusieurs feuilles, les barres orange et vertes sont plus courtes à gauche.

  uv run python src/figures/figure_les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.py \
      --sortie docs/images/402_les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.png

⚠ Tout vient de la mesure de `402`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
VERT = (92, 140, 96)
L_, H_ = 1200, 660
LA_BANDE = 540
LES_PANNEAUX = (("plusieurs", "sauts de plusieurs feuilles", 220, 560), ("nuls", "sauts nuls", 700, 1060))
LES_JEUX = (("389", BLEU), ("397", ORANGE), ("399", VERT))
HAUT = 120
RANGEE = 40
EPAISSEUR = 11
LES_CHAINES = ("suivie", "compagne", "tierce")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_lignes(d: dict) -> list[dict]:
    """Par côté qui a un saut de plusieurs feuilles dans l'une des trois mesures : ses comptes dans chacune."""
    out = []
    for k, jeux in d["par_cote"].items():
        if any(j["plusieurs"] for j in jeux.values()):
            rang, cote = k.split()
            out.append({"le_rang": int(rang), "le_cote": cote, **jeux})
    return out


def le_titre(d: dict) -> str:
    v, b = d["le_verdict"], d["le_bilan"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return (f"sauts de plusieurs feuilles : {b['389']['plusieurs']} dans 389, {b['397']['plusieurs']} rognées : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    b = d["le_bilan"]
    deux = (f"rapporté à côté, qui ne décide rien : les sauts nuls passent de {b['389']['nuls']} à {b['397']['nuls']} rognés, et "
            f"{b['399']['nuls']} comptés entiers")
    trois = "⚠ ce qui n'est PAS établi : si un saut que m7 compte de deux feuilles en franchit vraiment deux ; PHerc0358 n'a pas de tours."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 520)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "côté par côté : 389 en bleu, chaînes rognées de 397 en orange, les mêmes comptées sur leurs surfaces entières en vert",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    lignes = les_lignes(d)
    plus = max((r[j][k] for r in lignes for j, _ in LES_JEUX for k, _, _, _ in LES_PANNEAUX), default=1) or 1
    for _, nom, g, _ in LES_PANNEAUX:
        ecrire(g, HAUT - 34, nom, moyen, ENCRE)
        art.line([g, HAUT - 10, g, HAUT + len(lignes) * RANGEE], fill=GRIS)
    for i, r in enumerate(lignes):
        y = HAUT + i * RANGEE
        ecrire(70, y + 12, f"graine {r['le_rang']}, {r['le_cote']}", petit, ENCRE)
        for cle, _, g, dr in LES_PANNEAUX:
            for j, (jeu, couleur) in enumerate(LES_JEUX):
                n = r[jeu][cle]
                yy = y + 2 + j * (EPAISSEUR + 2)
                fin = g + round(n / plus * (dr - g))
                if n:
                    art.rectangle([g + 1, yy, fin, yy + EPAISSEUR], fill=couleur)
                    traces["rectangles"].append((g + 1, fin, yy, yy + EPAISSEUR))
                traces["barres"].append((r["le_rang"], r["le_cote"], cle, jeu, n, fin, couleur))
                if j == 2 or n:
                    ecrire(fin + 6, yy - 2, str(n), petit, couleur if n else GRIS)
    gx = 220
    for jeu, couleur in LES_JEUX:
        art.rectangle([gx, 494, gx + 14, 506], fill=couleur)
        ecrire(gx + 20, 494, {"389": "389", "397": "397, rognées", "399": "rognées, comptées entières"}[jeu], petit, ENCRE)
        gx += 220

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
    tmp = sortie.parent / ".sonde_402.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"]["397"]["plusieurs"] = 99
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == f"SAUTS DE PLUSIEURS FEUILLES : {d['le_bilan']['389']['plusieurs']} DANS 389, 99 ROGNÉES : OUI, Y",
      le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    for jeu, _ in LES_JEUX:
        v(f"★★★★ les barres de plusieurs feuilles de {jeu} somment à son bilan",
          sum(b[4] for b in traces["barres"] if b[3] == jeu and b[2] == "plusieurs") == d["le_bilan"][jeu]["plusieurs"])
        v(f"★★★★ les barres de sauts nuls de {jeu} sont celles de leurs côtés",
          all(b[4] == d["par_cote"][f"{b[0]} {b[1]}"][jeu]["nuls"] for b in traces["barres"] if b[3] == jeu and b[2] == "nuls"))
    v("★★★★ 389 en bleu, 397 en orange, 399 en vert", all(b[6] == {"389": BLEU, "397": ORANGE, "399": VERT}[b[3]] for b in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < 490)]
    v("★★★★ rien ne sort de son cadre ni ne passe sur la légende", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte les sauts nuls", f"passent de {d['le_bilan']['389']['nuls']} à {d['le_bilan']['397']['nuls']}" in la_bande(d)[1])
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
                   / "402_les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.png")
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
