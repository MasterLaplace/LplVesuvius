"""Sur PHerc0358, à seize sauts et aux comptes de m7 : côté par côté, les surfaces validées et contredites dans les huit premiers sauts et au-delà.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté où l'accord valide une surface, quatre barres : validées dans les huit premiers sauts
(bleu), validées au-delà (bleu foncé), contredites dans les huit premiers sauts (orange pâle), contredites au-delà (orange) ; dessous, le
plus grand compte validé.

  uv run python src/figures/figure_laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.py \\
      --sortie docs/images/389_laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.png

⚠ Tout vient de la mesure de `389`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
FONCE = (24, 44, 70)
PALE = (232, 196, 150)
ORANGE = (214, 150, 76)
L_, H_ = 1300, 580
LA_BANDE = 460
HAUT, BAS = 140, 340
LARGEUR = 30
LES_BARRES = (("validée", False, BLEU), ("validée", True, FONCE), ("contredite", False, PALE), ("contredite", True, ORANGE))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_cotes(d: dict) -> list[dict]:
    return [c for c in d["les_cotes"] if c["le_resume"]["validees"]]


def le_compte(c: dict, statut: str, au_dela: bool, huit: int) -> int:
    return sum(s["le_statut"] == statut and (s["le_saut"] > huit) == au_dela for s in c["les_surfaces"])


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"à seize sauts : {b['au_dela']} surfaces validées au-delà du huitième saut, sur {b['les_cotes_au_dela']} côtés, jusqu'à "
            f"{b['le_plus_loin_au_dela']} tours : {v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    h = d["les_constantes"]["les_huit"]
    cs = les_cotes(d)
    c_au_dela = sum(le_compte(c, "contredite", True, h) for c in cs)
    deux = (f"rapporté à côté, qui ne décide rien : l'accord valide {d['le_bilan']['validees']} surfaces en tout ; au-delà du huitième saut, "
            f"{c_au_dela} sont contredites")
    trois = "⚠ ce qui n'est PAS établi : si une surface validée au-delà du huitième saut est sur la bonne feuille."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1250, 440)]
    traces = {"barres": [], "rectangles": [], "dessous": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "validées dans les huit premiers sauts (bleu) et au-delà (bleu foncé) ; contredites dans les huit (orange pâle) et "
                   "au-delà (orange)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS)
    h = d["les_constantes"]["les_huit"]
    cs = les_cotes(d)
    plus = max((le_compte(c, st, ad, h) for c in cs for st, ad, _ in LES_BARRES), default=0) or 1
    pas = (x1 - x0 - 60) // max(1, len(cs))
    for i, c in enumerate(cs):
        gauche = x0 + 40 + i * pas
        for j, (st, ad, couleur) in enumerate(LES_BARRES):
            n = le_compte(c, st, ad, h)
            g = gauche + j * (LARGEUR + 4)
            sommet = BAS - round(n / plus * (BAS - HAUT))
            if n:
                art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
                traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            traces["barres"].append((c["le_rang"], c["le_cote"], st, ad, n, sommet, couleur))
            ecrire(g + 6, sommet - 18, str(n), petit, ENCRE)
        ecrire(gauche, BAS + 10, f"graine {c['le_rang']}, {c['le_cote']}", moyen, ENCRE)
        sous = f"jusqu'à {c['le_resume']['le_plus_loin']} tours"
        ecrire(gauche, BAS + 32, sous, petit, GRIS)
        traces["dessous"].append((c["le_rang"], c["le_cote"], sous))

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
    tmp = sortie.parent / ".sonde_389.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"au_dela": 2, "les_cotes_au_dela": 1, "le_plus_loin_au_dela": 9})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "À SEIZE SAUTS : 2 SURFACES VALIDÉES AU-DELÀ DU HUITIÈME SAUT, SUR 1 CÔTÉS, JUSQU'À 9 "
      "TOURS : EN PARTIE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    h = d["les_constantes"]["les_huit"]
    cs = [c for c in d["les_cotes"] if c["le_resume"]["validees"]]
    attendu = [(c["le_rang"], c["le_cote"], st, ad, sum(s["le_statut"] == st and (s["le_saut"] > h) == ad for s in c["les_surfaces"]))
               for c in cs for st, ad in (("validée", False), ("validée", True), ("contredite", False), ("contredite", True))]
    v("★★★★ quatre barres par côté, recomptées sur les surfaces", [b[:5] for b in traces["barres"]] == attendu, str(traces["barres"][:2]))
    v("★★★★ les validées au-delà somment au bilan", sum(n for _, _, st, ad, n, _, _ in traces["barres"] if st == "validée" and ad)
      == d["le_bilan"]["au_dela"])
    v("★★★★ les validées des deux parts somment aux validées du bilan",
      sum(n for _, _, st, _, n, _, _ in traces["barres"] if st == "validée") == d["le_bilan"]["validees"])
    v("★★★★ les couleurs : bleu, bleu foncé, orange pâle, orange",
      all(f == {("validée", False): BLEU, ("validée", True): FONCE, ("contredite", False): PALE, ("contredite", True): ORANGE}[(st, ad)]
          for _, _, st, ad, _, _, f in traces["barres"]))
    plus = max(n for *_, n, _, _ in traces["barres"])
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté à la plus haute",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for *_, n, s, _ in traces["barres"]))
    v("★★★★ sous chaque côté, le plus grand compte validé",
      traces["dessous"] == [(c["le_rang"], c["le_cote"], f"jusqu'à {c['le_resume']['le_plus_loin']} tours") for c in cs])
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "389_laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.png")
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
