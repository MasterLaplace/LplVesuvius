"""La chaîne qui croît, avec et sans relance à chaque saut : les tours publiés qu'elle descend sur PHercParis4, graine par graine, et les sauts qu'elle tient au pas sur PHerc0358, côté par côté.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque graine de PHercParis4, deux barres : la descente sans relance
(`330`, grise) et avec relance (verte), avec ce qui arrête la seconde. À droite, pour chaque côté de PHerc0358, les sauts tenus sans
relance (`328`, gris) et avec (orange). Si les barres vertes baissent quand les orange montent, la relance échange la justesse contre la
tenue.

  uv run python src/figures/figure_une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.py \\
      --sortie docs/images/331_une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.png

⚠ Tout vient des mesures de `331`, `330` et `328`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.json"
LA_MESURE_330 = RACINE / "docs" / "mesures" / "jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.json"
LA_MESURE_328 = RACINE / "docs" / "mesures" / "combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
GRIS_BARRE = (190, 192, 196)
L_, H_ = 1360, 600
LA_BANDE = 510
LE_MAX = 8


def lire(chemin: Path = LA_MESURE, c330: Path = LA_MESURE_330, c328: Path = LA_MESURE_328) -> dict:
    d = json.loads(chemin.read_text())
    d["sans_relance_4"] = {g["le_rang"]: g["la_descente"] for g in json.loads(c330.read_text())["les_graines"]}
    d["sans_relance_0"] = {(c["le_rang"], c["le_cote"]): c["tient"] for c in json.loads(c328.read_text())["les_cotes"]["PHerc0358"]}
    return d


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    cs = d["les_cotes"]["PHerc0358"]
    plus = sum(1 for c in cs if c["tient"] > d["sans_relance_0"][(c["le_rang"], c["le_cote"])])
    moins = sum(1 for c in cs if c["tient"] < d["sans_relance_0"][(c["le_rang"], c["le_cote"])])
    return (f"la relance : {v['lissue'].split(' ; ')[-1]} ; sur PHerc0358, elle allonge {plus} côtés et en raccourcit "
            f"{moins}").upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "ecretes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, haut, col, cle):
        if not 0 <= haut <= LE_MAX:
            traces["ecretes"] += 1
        h = min(LE_MAX, max(0, haut))
        art.rectangle([x, gy1 - h / LE_MAX * (gy1 - gy0), x + 20, gy1], fill=col)
        traces["barres"].append(cle + (haut,))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "gris : sans relance (330, 328) ; couleur : avec une nappe qui croît relancée sur la feuille de chaque spire", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 760, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "PHercParis4 : les tours publiés descendus, côté moins", moyen, ENCRE)
    gy0, gy1 = y0 + 50, y1 - 70
    for q in (2, 4, 6, 8):
        yq = gy1 - q / LE_MAX * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, str(q), 0, GRIS)
    for n, g in enumerate(d["les_graines"]["PHercParis4"]):
        xa = x0 + 60 + n * 86
        barre(xa, d["sans_relance_4"][g["le_rang"]], GRIS_BARRE, ("PHercParis4", g["le_rang"], "sans"))
        barre(xa + 24, g["la_descente"], BON, ("PHercParis4", g["le_rang"], "avec"))
        ecrire(int(xa + 8), gy1 + 6, f"g{g['le_rang']}", 0, ENCRE)
        arret = g["les_cotes"]["moins"]["larret"]
        ecrire(int(xa), gy1 + 22 + (n % 2) * 14, {"un saut faux": "faux", "un tour manqué": "manqué", "non lue": "non lue",
                                                   "le bout de la chaîne": "bout"}.get(arret, arret[:7]), 0,
               ALERTE if arret == "un saut faux" else GRIS)

    x0, y0, x1, y1 = 790, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "PHerc0358 : les sauts tenus au pas", moyen, ENCRE)
    for q in (2, 4, 6, 8):
        yq = gy1 - q / LE_MAX * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, str(q), 0, GRIS)
    for n, c in enumerate(d["les_cotes"]["PHerc0358"]):
        xa = x0 + 60 + n * 90
        barre(xa, d["sans_relance_0"][(c["le_rang"], c["le_cote"])], GRIS_BARRE, ("PHerc0358", c["le_rang"], c["le_cote"], "sans"))
        barre(xa + 24, c["tient"], ALERTE, ("PHerc0358", c["le_rang"], c["le_cote"], "avec"))
        ecrire(int(xa), gy1 + 6, f"g{c['le_rang']} {c['le_cote']}", 0, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : sur quelle feuille tombe une nappe relancée de PHerc0358.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_331.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = dict(d, le_verdict={"decidable": True, "lissue": "x ; elle ne change rien"},
                 sans_relance_0={k: 9 for k in d["sans_relance_0"]})
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA RELANCE : ELLE NE CHANGE RIEN ; SUR PHERC0358, ELLE ALLONGE 0 CÔTÉS ET EN "
      f"RACCOURCIT {len(d['les_cotes']['PHerc0358'])}", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = ([("PHercParis4", g["le_rang"], s, h) for g in d["les_graines"]["PHercParis4"]
                for s, h in (("sans", d["sans_relance_4"][g["le_rang"]]), ("avec", g["la_descente"]))]
               + [("PHerc0358", c["le_rang"], c["le_cote"], s, h) for c in d["les_cotes"]["PHerc0358"]
                  for s, h in (("sans", d["sans_relance_0"][(c["le_rang"], c["le_cote"])]), ("avec", c["tient"]))])
    v("★★★ deux barres par graine et par côté, aux comptes mesurés", traces["barres"] == attendu)
    v("★★★ les barres sans relance viennent de 330 et de 328",
      d["sans_relance_4"] == {g["le_rang"]: g["la_descente"] for g in json.loads(LA_MESURE_330.read_text())["les_graines"]})
    v("★★★ aucune barre n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
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
                   / "331_une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.png")
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
