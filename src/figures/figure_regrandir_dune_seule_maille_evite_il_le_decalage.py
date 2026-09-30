"""Sur PHercParis4, graines 4 à 8 : la surface gardée, la part des sauts justes à cheval, et la part des côtés où le décalage naît après la première surface lisible, pour la chaîne mixte, la chaîne qui regrandit d'une maille et celle qui regrandit de deux.

⚠⚠ **Ce que cette figure doit rendre évident.** Trois groupes de barres ; dans chacun, la chaîne mixte en bleu, la chaîne qui regrandit
d'une maille en vert, celle de deux mailles en orange. Sous chaque barre, ce qui la fait.

  uv run python src/figures/figure_regrandir_dune_seule_maille_evite_il_le_decalage.py \\
      --sortie docs/images/365_regrandir_dune_seule_maille_evite_il_le_decalage.png

⚠ Tout vient de la mesure de `365`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "regrandir_dune_seule_maille_evite_il_le_decalage.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
VERT = (96, 140, 110)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 150, 390
LARGEUR = 60
LES_CHAINES = (("la_chaine_mixte", "chaîne mixte", BLEU), ("dune_maille", "regrandie d'une maille", VERT),
               ("de_deux_mailles", "regrandie de deux mailles", ORANGE))
LES_GROUPES = (("s", "mailles gardées, en médiane", 230), ("c", "sauts justes à cheval", 550),
               ("n", "côtés où il naît après la référence", 870))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_barre(d: dict, groupe: str, cle: str) -> tuple[float, str]:
    b = d["les_bilans"][cle]
    if groupe == "s":
        plus = max(d["les_bilans"][k]["la_surface"] for k, _, _ in LES_CHAINES)
        return b["la_surface"] / plus, f"{b['la_surface']:g}".replace(".", ",")
    if groupe == "c":
        return b["les_justes_a_cheval"] / b["les_justes"], f"{b['les_justes_a_cheval']} sur {b['les_justes']}"
    n = b["la_naissance"]
    return n["apres_elle"] / n["les_cotes_juges"], f"{n['apres_elle']} sur {n['les_cotes_juges']}"


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    tete, _, suite = d["le_verdict"]["lissue"].partition(", et ")
    u = d["les_bilans"]["dune_maille"]
    fautes = sorted({c["le_rang"] for c in d["les_cotes"] if c["le_rang"] >= 4 for s in c["les_sauts"]
                     if s["la_justesse"] != "non jugé" and (s["la_justesse"] != "juste" or s["a_cheval"])})
    ou = f"tous sur la graine {fautes[0]}" if len(fautes) == 1 else "sur les graines " + ", ".join(str(r) for r in fautes)
    trois = (f"rapporté à côté, qui ne décide rien : regrandie d'une maille, la chaîne est juste sous {u['les_justes']} des {u['les_juges']} "
             f"sauts jugés ; ses sauts à cheval et faux sont {ou}")
    quatre = "⚠ ce qui n'est PAS établi : d'où vient le décalage que la graine 7 porte dès sa première surface lisible."
    return f"LE VERDICT DÉCLARÉ : {tete},", f"et {suite}" if suite else "", trois, quatre


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": [], "titres": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "sur PHercParis4, graines 4 à 8 ; les mailles sont rapportées à la plus grande des trois, le reste est une part",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    for i, (_, nom, couleur) in enumerate(LES_CHAINES):
        lx = x0 + 12 + i * 230
        art.rectangle([lx, y0 + 12, lx + 12, y0 + 24], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, y0 + 12, y0 + 24))
        ecrire(lx + 18, y0 + 10, nom, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    for groupe, titre, centre in LES_GROUPES:
        for i, (cle, _, couleur) in enumerate(LES_CHAINES):
            part, compte = la_barre(d, groupe, cle)
            gauche = centre - 3 * LARGEUR // 2 - 10 + i * (LARGEUR + 10)
            sommet = BAS - round(part * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((groupe, cle, part, compte, sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            ecrire(gauche + 8, BAS + 6, compte, petit, ENCRE)
        ecrire(centre - 100, BAS + 26, titre, moyen, ENCRE)
        traces["titres"].append((groupe, titre))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    for k, ligne in enumerate(la_bande(d)):
        if k < 3:
            ecrire(50, LA_BANDE + 10 + 18 * k, ligne, petit, ENCRE)
        else:
            ecrire(50, LA_BANDE + 10 + 18 * k + 8, ligne, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_365.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"]["lissue"] = "x, et y ; non, elle ne rend pas de surface"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "NON, ELLE NE REND PAS DE SURFACE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    v("★★★★ la bande tient dans la toile", LA_BANDE + 10 + 18 * 3 + 8 + 18 < H_)
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    b = d["les_bilans"]
    plus = max(b[k]["la_surface"] for k in ("la_chaine_mixte", "dune_maille", "de_deux_mailles"))
    attendu = []
    for g, _, _ in LES_GROUPES:
        for k in ("la_chaine_mixte", "dune_maille", "de_deux_mailles"):
            x = b[k]
            attendu.append((g, k) + {"s": (x["la_surface"] / plus, f"{x['la_surface']:g}".replace(".", ",")),
                                     "c": (x["les_justes_a_cheval"] / x["les_justes"], f"{x['les_justes_a_cheval']} sur {x['les_justes']}"),
                                     "n": (x["la_naissance"]["apres_elle"] / x["la_naissance"]["les_cotes_juges"],
                                           f"{x['la_naissance']['apres_elle']} sur {x['la_naissance']['les_cotes_juges']}")}[g])
    v("★★★★ trois barres par groupe, mixte, une maille, deux mailles, à leur part et à leur compte",
      [(g, k, round(p, 9), c) for g, k, p, c, _, _ in traces["barres"]] == [(g, k, round(p, 9), c) for g, k, p, c in attendu],
      str(traces["barres"]))
    v("★★★★ la mixte en bleu, une maille en vert, deux mailles en orange",
      all(f == {"la_chaine_mixte": BLEU, "dune_maille": VERT, "de_deux_mailles": ORANGE}[k] for _, k, _, _, _, f in traces["barres"]))
    v("★★★★ chaque groupe porte son nom", traces["titres"] == [("s", "mailles gardées, en médiane"), ("c", "sauts justes à cheval"),
                                                           ("n", "côtés où il naît après la référence")])
    v("★★★★ la hauteur de chaque barre est sa part", all(BAS - s == round(p * (BAS - HAUT)) for _, _, p, _, s, _ in traces["barres"]))
    textes = {t for _, _, t, _ in poses}
    v("★★★★ sous chaque barre, ce qui la fait", all(c in textes for _, _, _, c, _, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    fautes = sorted({c["le_rang"] for c in d["les_cotes"] if c["le_rang"] >= 4 for s in c["les_sauts"]
                     if s["la_justesse"] != "non jugé" and (s["la_justesse"] != "juste" or s["a_cheval"])})
    u = b["dune_maille"]
    v("★★★★ la bande rapporte la justesse et la graine des fautes, recomptées",
      f"juste sous {u['les_justes']} des {u['les_juges']} sauts jugés" in " ".join(la_bande(d))
      and (len(fautes) != 1 or f"sont tous sur la graine {fautes[0]}" in " ".join(la_bande(d))), str(fautes))
    un_faux = json.loads(json.dumps(d))
    next(c for c in un_faux["les_cotes"] if c["le_rang"] == 5)["les_sauts"].append(
        {"la_justesse": "faux : deux tours", "a_cheval": False, "depuis": "la croissance"})
    v("★★★★ un saut faux sans cheval compte parmi les fautes", "sont sur les graines 5, 7" in " ".join(la_bande(un_faux)),
      " ".join(la_bande(un_faux))[-120:])
    v("★★★★ la bande porte le verdict entier",
      " ".join(la_bande(d)[:2]) == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for t in textes))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "365_regrandir_dune_seule_maille_evite_il_le_decalage.png")
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
