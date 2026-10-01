"""Sur PHercParis4 : par statut que l'accord de trois chaînes donne à une surface, la part des surfaces lues qui sont sur le bon tour publié.

⚠⚠ **Ce que cette figure doit rendre évident.** Une barre par statut, à la part des surfaces lues sur le bon tour : validées en bleu,
contredites en orange, confirmées une fois en gris, sans témoin en gris clair ; au-dessus de chaque barre, le nombre de surfaces sur le bon
tour sur le nombre de surfaces lues ; en trait plein, les 90 % de la règle.

  uv run python src/figures/figure_une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.py \\
      --sortie docs/images/379_une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.png

⚠ Tout vient de la mesure de `379`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 560
LA_BANDE = 440
HAUT, BAS = 120, 350
LARGEUR = 110
X0, PAS_X = 230, 190
LES_STATUTS = (("validée", "validées", BLEU), ("contredite", "contredites", ORANGE),
               ("confirmée une fois", "confirmées une fois", GRIS), ("sans témoin", "sans témoin", CLAIR))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_barres(d: dict) -> list[tuple[str, int, int]]:
    """Chaque statut, ses surfaces lues sur le bon tour et ses surfaces lues, recomptés sur les côtés."""
    out = []
    for st, _, _ in LES_STATUTS:
        lues = [s for c in d["les_cotes"] for s in c["les_surfaces"] if s["le_statut"] == st and s["lue"]]
        out.append((st, sum(s["sur_le_bon_tour"] for s in lues), len(lues)))
    return out


def en_y(p: float) -> int:
    return BAS - round(p * (BAS - HAUT))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].partition(",")[0].upper()
    return f"l'accord de trois chaînes et le bon tour, sur PHercParis4 : {v['lissue'].rpartition(' ; ')[2].partition(',')[0]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    s = d["le_bilan_sans_correction"]["validée"]
    deux = (f"rapporté à côté, qui ne décide rien : en comptant chaque saut pour un tour, sans la correction de 369, "
            f"{s['sur_le_bon_tour']} des {s['lues']} surfaces validées lues sont sur le bon tour")
    trois = "⚠ ce qui n'est PAS établi : ce que la règle vaut sur PHerc0358, ni sur les côtés plus, que les tours publiés ne jugent pas."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 410)]
    traces = {"barres": [], "seuils": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "part des surfaces lues contre les tours publiés qui sont sur le tour que leur compte corrigé leur donne, par statut",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([140, BAS, 1000, BAS], fill=GRIS)
    for k in range(0, 11, 2):
        y = en_y(k / 10.0)
        art.line([136, y, 140, y], fill=GRIS)
        ecrire(90, y - 7, f"{10 * k} %", petit, GRIS)
    couleurs = {st: c for st, _, c in LES_STATUTS}
    noms = {st: n for st, n, _ in LES_STATUTS}
    for i, (st, bons, lues) in enumerate(les_barres(d)):
        xa = X0 + i * PAS_X
        p = bons / lues if lues else 0.0
        y = en_y(p)
        art.rectangle([xa, y, xa + LARGEUR, BAS], fill=couleurs[st])
        traces["barres"].append((st, bons, lues, y, couleurs[st]))
        ecrire(xa + 35, y - 18, f"{bons} / {lues}", petit, ENCRE)
        ecrire(xa + 4, BAS + 10, noms[st], petit, ENCRE)
    yp = en_y(d["les_constantes"]["la_part"])
    art.line([140, yp, 1000, yp], fill=ENCRE, width=2)
    traces["seuils"].append(("la part", d["les_constantes"]["la_part"], yp))
    ecrire(915, yp - 18, "90 % : la règle", petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_379.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "L'ACCORD DE TROIS CHAÎNES ET LE BON TOUR, SUR PHERCPARIS4 : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui, l'accord choisit"}
    v("★★★ le titre garde le mot de la règle, sans sa glose", le_titre(autre).endswith(": OUI"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : 3 surfaces validées lues, moins de 10"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : 3 SURFACES VALIDÉES LUES", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendus = []
    for st in ("validée", "contredite", "confirmée une fois", "sans témoin"):
        lues = [s for c in d["les_cotes"] for s in c["les_surfaces"] if s["le_statut"] == st and s["lue"]]
        attendus.append((st, sum(1 for s in lues if s["sur_le_bon_tour"]), len(lues)))
    v("★★★★ une barre par statut, ses surfaces sur le bon tour et ses lues recomptées sur les côtés, dans l'ordre",
      [(s, b, n) for s, b, n, _, _ in traces["barres"]] == attendus, str(traces["barres"]))
    v("★★★★ les comptes égaux au bilan", all(d["le_bilan"][s]["sur_le_bon_tour"] == b and d["le_bilan"][s]["lues"] == n
                                            for s, b, n in attendus))
    v("★★★★ validées en bleu, contredites en orange, confirmées une fois en gris, sans témoin en gris clair",
      [f for _, _, _, _, f in traces["barres"]] == [(58, 88, 120), (214, 150, 76), (140, 143, 148), (205, 203, 197)])
    v("★★★★ chaque barre à sa part, de 0 à 100 %",
      all(y == BAS - round((b / n if n else 0.0) * (BAS - HAUT)) for _, b, n, y, _ in traces["barres"]))
    v("★★★★ les 90 % de la règle tracés à leur valeur", traces["seuils"] == [("la part", 0.9, en_y(0.9))], str(traces["seuils"]))
    vide = json.loads(json.dumps(d))
    for c in vide["les_cotes"]:
        for s in c["les_surfaces"]:
            if s["le_statut"] == "sans témoin":
                s["lue"], s["sur_le_bon_tour"] = False, None
    v("★★★ un statut sans surface lue a une barre nulle, pas une erreur",
      lambda: [t for t in dessiner(vide, tmp)[3]["barres"] if t[0] == "sans témoin"][0][1:3] == (0, 0))
    s = d["le_bilan_sans_correction"]["validée"]
    v("★★★★ la bande rapporte les validées sans la correction de 369",
      f"{s['sur_le_bon_tour']} des {s['lues']} surfaces validées lues" in la_bande(d)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    dessiner(d, tmp)
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
                   / "379_une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.png")
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
