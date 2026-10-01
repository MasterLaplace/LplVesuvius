"""Sur les côtés où le vote désigne une chaîne, sur PHercParis4 et sur PHerc0358 : les surfaces validées et contredites avant et après le recompte que la règle retient, et ce que la règle a trouvé.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté désigné, quatre barres : validées avant (gris) et après (bleu), contredites avant
(orange pâle) et après (orange). Dessous, le recompte retenu, ou pourquoi il n'y en a pas : aucun candidat, ou plusieurs.

  uv run python src/figures/figure_recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.py \\
      --sortie docs/images/382_recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.png

⚠ Tout vient de la mesure de `382`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (190, 188, 182)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
PALE = (232, 196, 150)
ORANGE = (214, 150, 76)
L_, H_ = 1300, 600
LA_BANDE = 470
HAUT, BAS = 140, 340
LARGEUR = 30
LES_BARRES = (("validée", "avant", CLAIR), ("validée", "apres", BLEU), ("contredite", "avant", PALE), ("contredite", "apres", ORANGE))
LES_ROULEAUX = (("les_cotes_de_paris4", "PHercParis4"), ("les_cotes_de_0358", "PHerc0358"))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_designes(d: dict) -> list[tuple[str, dict]]:
    """Les côtés où le vote désigne une chaîne, PHercParis4 d'abord, chacun dans l'ordre de la mesure."""
    return [(nom, c) for cle, nom in LES_ROULEAUX for c in d[cle] if c["la_chaine"] is not None]


def ce_que_la_regle_dit(c: dict) -> str:
    n = len(c["les_candidats_qui_font_tenir"])
    if c["le_retenu"] is not None:
        r = c["le_retenu"]
        return f"saut {r['le_saut']} recompté, {r['de']} en {r['a']}"
    return "aucun candidat" if n == 0 else f"{n} candidats : aucun retenu"


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].upper() if not v.get("decidable") else (
        f"le recompte de la chaîne désignée : {v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    b = d["le_bilan"]
    s, t = b["les_surfaces_de_la_chaine"], b["les_surfaces_des_trois"]
    deux = (f"rapporté à côté, qui ne décide rien : sur PHercParis4, {b['designees']} côtés désignés sur {b['les_cotes']}, "
            f"{b['recomptes']} recompté ; des surfaces nouvellement validées, {t['sur_le_bon_tour']} sur {t['lues']} lues sont au bon tour, "
            f"dont {s['sur_le_bon_tour']} sur {s['lues']} de la chaîne recomptée")
    trois = "⚠ ce qui n'est PAS établi : si un saut recompté franchit le nombre de feuilles que son nouveau compte dit."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1250, 450)]
    traces = {"barres": [], "rectangles": [], "dessous": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par côté désigné : validées avant (gris) et après (bleu), contredites avant (orange pâle) et après (orange)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS, width=1)
    designes = les_designes(d)
    plus = max((c[t][s] for _, c in designes for s, t, _ in LES_BARRES), default=0) or 1
    pas = (x1 - x0 - 60) // max(1, len(designes))
    for i, (rouleau, c) in enumerate(designes):
        gauche = x0 + 40 + i * pas
        for j, (s, t, couleur) in enumerate(LES_BARRES):
            n = c[t][s]
            g = gauche + j * (LARGEUR + 6)
            sommet = BAS - round(n / plus * (BAS - HAUT))
            if n:
                art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
                traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            traces["barres"].append((rouleau, c["le_rang"], c["le_cote"], s, t, n, sommet, couleur))
            ecrire(g + 6, sommet - 18, str(n), petit, ENCRE)
        ecrire(gauche, BAS + 10, f"{rouleau}, graine {c['le_rang']}, {c['le_cote']}", moyen, ENCRE)
        ecrire(gauche, BAS + 32, f"désignée : la {c['la_chaine']}", petit, GRIS)
        dit = ce_que_la_regle_dit(c)
        ecrire(gauche, BAS + 50, dit, petit, ENCRE)
        traces["dessous"].append((rouleau, c["le_rang"], c["le_cote"], dit))

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
    tmp = sortie.parent / ".sonde_382.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LE RECOMPTE DE LA CHAÎNE DÉSIGNÉE : EN PARTIE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    designes = [(n, c) for k, n in (("les_cotes_de_paris4", "PHercParis4"), ("les_cotes_de_0358", "PHerc0358")) for c in d[k] if c["la_chaine"]]
    attendu = [(n, c["le_rang"], c["le_cote"], s, t, c[t][s]) for n, c in designes
               for s, t in (("validée", "avant"), ("validée", "apres"), ("contredite", "avant"), ("contredite", "apres"))]
    v("★★★★ quatre barres par côté désigné, lues dans la mesure, PHercParis4 d'abord", [b_[:6] for b_ in traces["barres"]] == attendu,
      str(traces["barres"][:2]))
    v("★★★★ validées avant en gris, après en bleu ; contredites avant en orange pâle, après en orange",
      all(f == {("validée", "avant"): CLAIR, ("validée", "apres"): BLEU, ("contredite", "avant"): PALE, ("contredite", "apres"): ORANGE}[(s, t)]
          for _, _, _, s, t, _, _, f in traces["barres"]))
    plus = max(n for *_, n, _, _ in traces["barres"])
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté à la plus haute",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for *_, n, s, _ in traces["barres"]))
    dits = []
    for n, c in designes:
        k = len(c["les_candidats_qui_font_tenir"])
        r = c["le_retenu"]
        dits.append((n, c["le_rang"], c["le_cote"], f"saut {r['le_saut']} recompté, {r['de']} en {r['a']}" if r
                     else "aucun candidat" if k == 0 else f"{k} candidats : aucun retenu"))
    v("★★★★ sous chaque côté, le recompte retenu, ou aucun candidat, ou plusieurs", traces["dessous"] == dits, str(traces["dessous"]))
    deux = json.loads(json.dumps(d))
    for c in deux["les_cotes_de_0358"]:
        if c["la_chaine"]:
            c["le_retenu"] = None
            c["les_candidats_qui_font_tenir"] = [{}, {}, {}]
    v("★★★★ plusieurs candidats sans retenu sont dits tels", all(ce_que_la_regle_dit(c) == "3 candidats : aucun retenu"
                                                                 for c in deux["les_cotes_de_0358"] if c["la_chaine"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    b = d["le_bilan"]
    v("★★★★ la bande rapporte les côtés désignés et les surfaces lues au bon tour",
      f"{b['designees']} côtés désignés sur {b['les_cotes']}, {b['recomptes']} recompté" in la_bande(d)[1]
      and f"{b['les_surfaces_des_trois']['sur_le_bon_tour']} sur {b['les_surfaces_des_trois']['lues']} lues sont au bon tour" in la_bande(d)[1])
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
                   / "382_recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.png")
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
