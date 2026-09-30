"""Sur PHercParis4, graines 4 à 8 : la part des sauts jugés qui sont justes, et la part des sauts justes à cheval, pour la chaîne mixte et pour la chaîne relancée depuis un point.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux groupes de barres : à gauche la part juste, à droite la part à cheval ; dans chaque
groupe, la chaîne mixte en bleu et la chaîne relancée en gris. Sous chaque barre, le compte qui la fait.

  uv run python src/figures/figure_la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.py \\
      --sortie docs/images/357_la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.png

⚠ Tout vient de la mesure de `357`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
GRIS_BARRE = (170, 172, 176)
L_, H_ = 1100, 560
LA_BANDE = 470
HAUT, BAS = 150, 390
LARGEUR = 90
LES_CHAINES = (("la_chaine_mixte", "chaîne mixte", BLEU), ("le_temoin", "chaîne relancée depuis un point", GRIS_BARRE))
LES_GROUPES = (("j", "les_justes", "les_juges", "sauts jugés qui sont justes", 300),
               ("c", "les_justes_a_cheval", "les_justes", "sauts justes à cheval", 750))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"sur phercparis4, graines 4 à 8 : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, str, str, str]:
    tete, _, suite = d["le_verdict"]["lissue"].partition(", contre ")
    juges = [s for c in d["les_cotes"] if c["le_rang"] >= 4 for s in c["les_sauts"] if s["la_justesse"] != "non jugé"]
    gardes = sum(s["depuis"] == "la spire" for s in juges)
    relances = sum(s["depuis"] == "la relance" for s in juges)
    cheval_relances = sum(s["depuis"] == "la relance" and s["la_justesse"] == "juste" and s["a_cheval"] for s in juges)
    b = d["les_bilans"]["graines_1_a_3"]
    un = f"LE VERDICT DÉCLARÉ : {tete},"
    deux = f"contre {suite}" if suite else ""
    relances_ = f"{relances} est relancé" if relances == 1 else f"{relances} sont relancés"
    trois = (f"rapporté à côté, qui ne décide rien : des {len(juges)} sauts jugés, {gardes} gardent leur spire et {relances_}, "
             f"dont {cheval_relances} à cheval ; sur les graines 1 à 3, {b['les_justes']} des {b['les_juges']} sauts jugés sont justes")
    quatre = "⚠ ce qui n'est PAS établi : si la chaîne mixte reste juste sur PHerc0358, où aucun tour publié ne la juge."
    return un, deux, trois, quatre


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
    ecrire(50, 46, "la hauteur d'une barre est une part ; sous elle, le compte qui la fait", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    ecrire(x0 + 12, y0 + 8, "graines 4 à 8, les sauts jugés par les tours publiés", moyen, ENCRE)
    lx = x0 + 560
    for i, (_, nom, couleur) in enumerate(LES_CHAINES):
        ly = y0 + 10 + i * 20
        art.rectangle([lx, ly + 2, lx + 12, ly + 14], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, ly + 2, ly + 14))
        ecrire(lx + 20, ly, nom, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    for _, haut, bas, titre, centre in LES_GROUPES:
        for i, (cle, _, couleur) in enumerate(LES_CHAINES):
            b = d["les_bilans"][cle]
            a, n = b[haut], b[bas]
            part = a / n if n else 0.0
            gauche = centre - LARGEUR - 10 if i == 0 else centre + 10
            sommet = BAS - round(part * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((titre, cle, a, n, sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            ecrire(gauche + 22, sommet - 18, f"{round(100 * part)} %", petit, ENCRE)
            ecrire(gauche + 16, BAS + 6, f"{a} sur {n}", petit, ENCRE)
        ecrire(centre - 90, BAS + 26, titre, moyen, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois, quatre = la_bande(d)
    ecrire(50, LA_BANDE + 8, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 24, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 40, trois, petit, ENCRE)
    ecrire(50, LA_BANDE + 60, quatre, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_357.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"]["lissue"] = "sur les graines 4 à 8, x ; non"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SUR PHERCPARIS4, GRAINES 4 À 8 : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    juges = [s for c in d["les_cotes"] if c["le_rang"] >= 4 for s in c["les_sauts"] if s["la_justesse"] != "non jugé"]
    justes = [s for s in juges if s["la_justesse"] == "juste"]
    recompte = (len(juges), len(justes), sum(s["a_cheval"] for s in justes))
    b = d["les_bilans"]["la_chaine_mixte"]
    v("★★★★ le bilan de la chaîne mixte se recompte sur ses sauts", (b["les_juges"], b["les_justes"], b["les_justes_a_cheval"]) == recompte,
      str(recompte))
    attendu = [(g[3], c[0], d["les_bilans"][c[0]][g[1]], d["les_bilans"][c[0]][g[2]], c[2]) for g in LES_GROUPES for c in LES_CHAINES]
    v("★★★★ une barre par chaîne et par part, au compte et à la couleur de sa chaîne",
      [(t, k, a, n, f) for t, k, a, n, _, f in traces["barres"]] == attendu, str(traces["barres"]))
    v("★★★★ la chaîne mixte est en bleu, la chaîne relancée en gris",
      all(f == {"la_chaine_mixte": BLEU, "le_temoin": GRIS_BARRE}[k] for _, k, _, _, _, f in traces["barres"]))
    parts = {k: [(a, n) for _, k2, a, n, _, _ in traces["barres"] if k2 == k] for k, _, _ in LES_CHAINES}
    v("★★★★ à gauche les justes sur les jugés, à droite les justes à cheval sur les justes",
      all(parts[k] == [(d["les_bilans"][k]["les_justes"], d["les_bilans"][k]["les_juges"]),
                       (d["les_bilans"][k]["les_justes_a_cheval"], d["les_bilans"][k]["les_justes"])] for k in parts), str(parts))
    v("★★★★ la hauteur de chaque barre est sa part", all(BAS - s == round(a / n * (BAS - HAUT)) for _, _, a, n, s, _ in traces["barres"]))
    v("★★★★ une part plus haute donne une barre plus haute",
      all((a / n > a2 / n2) == (s < s2) for (t, _, a, n, s, _), (t2, _, a2, n2, s2, _) in zip(traces["barres"][::2], traces["barres"][1::2])
          if a / n != a2 / n2))
    comptes = {t for _, _, t, _ in poses}
    v("★★★★ sous chaque barre, le compte qui la fait", all(f"{a} sur {n}" in comptes for _, _, a, n, _, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    gardes = sum(s["depuis"] == "la spire" for s in juges)
    v("★★★★ la bande rapporte à côté les spires gardées et les relances, recomptées",
      f"des {len(juges)} sauts jugés, {gardes} gardent leur spire et {len(juges) - gardes} " in " ".join(la_bande(d)))
    v("★★★★ la bande porte le verdict entier, en deux lignes", " ".join(la_bande(d)[:2]) == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
                   / "357_la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.png")
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
