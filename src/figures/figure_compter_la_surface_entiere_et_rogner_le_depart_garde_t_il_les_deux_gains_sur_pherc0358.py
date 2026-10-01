"""Sur PHerc0358, à seize sauts : côté par côté, les surfaces validées et contredites des chaînes de 389, des chaînes rognées de 397, et des mêmes chaînes rognées comptées sur leurs surfaces entières.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux panneaux, les validées à gauche et les contredites à droite ; une rangée par côté qui
porte des surfaces jugées ; dans chaque rangée, trois barres : `389` en bleu, `397` en orange, les chaînes rognées comptées entières en vert.
Si compter la surface entière garde les deux gains, la barre verte est longue à gauche comme la bleue et courte à droite comme l'orange.

  uv run python src/figures/figure_compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.py \\
      --sortie docs/images/399_compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.png

⚠ Tout vient de la mesure de `399`, qui recopie les statuts de `389` et de `397`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.json"

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
LES_PANNEAUX = (("validée", "surfaces validées", 220, 560), ("contredite", "surfaces contredites", 700, 1060))
LES_JEUX = (("389", BLEU), ("397", ORANGE), ("399", VERT))
HAUT = 120
RANGEE = 40
EPAISSEUR = 11
LES_CHAINES = ("suivie", "compagne", "tierce")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_lignes(d: dict) -> list[dict]:
    """Par côté qui porte une surface validée ou contredite dans l'une des trois manières : ses statuts dans chacune."""
    out = []
    for c in d["les_cotes"]:
        k = f"{c['le_rang']} {c['le_cote']}"
        jeux = {"389": d["les_statuts_389"][k], "397": d["les_statuts_397"][k], "399": c["les_statuts"]}
        if any(j[s] for j in jeux.values() for s in ("validée", "contredite")):
            out.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], **jeux})
    return out


def les_surfaces(d: dict) -> int:
    return sum(len(c["les_sauts"][x]) for c in d["les_cotes"] for x in LES_CHAINES)


def le_titre(d: dict) -> str:
    v, b = d["le_verdict"], d["le_bilan"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return (f"comptées entières : {b['validee']} validées et {b['contredite']} contredites : {v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    n, b = les_surfaces(d), d["le_bilan"]
    p1 = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
    deux = (f"rapporté à côté, qui ne décide rien : sur les {n} surfaces des chaînes rognées, {p1(100 * b['contredite'] / n)} % sont "
            f"contredites et {p1(100 * b['validee'] / n)} % validées")
    trois = "⚠ ce qui n'est PAS établi : si une surface validée est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés."
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
    tmp = sortie.parent / ".sonde_399.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"]["validee"] = 99
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == f"COMPTÉES ENTIÈRES : 99 VALIDÉES ET {d['le_bilan']['contredite']} CONTREDITES : OUI, Y",
      le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    sommes = {"389": d["389"], "397": d["397"], "399": d["le_bilan"]}
    for jeu, _ in LES_JEUX:
        v(f"★★★★ les barres de {jeu} somment à son bilan",
          sum(b[4] for b in traces["barres"] if b[3] == jeu and b[2] == "validée") == sommes[jeu]["validee"]
          and sum(b[4] for b in traces["barres"] if b[3] == jeu and b[2] == "contredite") == sommes[jeu]["contredite"])
    v("★★★★ 389 en bleu, 397 en orange, 399 en vert", all(b[6] == {"389": BLEU, "397": ORANGE, "399": VERT}[b[3]] for b in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < 490)]
    v("★★★★ rien ne sort de son cadre ni ne passe sur la légende", not dehors, str(dehors[:3]))
    n = sum(len(c["les_sauts"][x]) for c in d["les_cotes"] for x in LES_CHAINES)
    v("★★★★ la bande rapporte les parts sur les surfaces", f"sur les {n} surfaces des chaînes rognées" in la_bande(d)[1])
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
                   / "399_compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.png")
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
