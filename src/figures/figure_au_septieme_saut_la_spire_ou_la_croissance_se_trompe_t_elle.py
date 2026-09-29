"""Aux trois sauts faux de la chaîne relancée depuis sa spire, ce que retrouvent la nappe relancée, la spire et la croissance hors des semis ; et la descente de chaque graine jugée sur les nappes relancées ou sur les spires seules.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, une ligne par saut faux et trois cases : le tour que retrouve la nappe
relancée, la spire, et la part posée par la croissance, contre `5753_-7` qu'on attend. Si la spire est grise là où la nappe et la
croissance sont orange, c'est la croissance qui retombe. À droite, pour chaque graine, la descente jugée sur les nappes (`333`) et sur les
spires seules.

  uv run python src/figures/figure_au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.py \\
      --sortie docs/images/334_au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.png

⚠ Tout vient de la mesure de `334`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CLAIR_BON = (160, 196, 180)
CASE_FAUSSE = (236, 204, 180)
CASE_BONNE = (196, 222, 208)
CASE_VIDE = (228, 228, 226)
L_, H_ = 1360, 560
LA_BANDE = 470
LE_MAX = 8
LES_PARTS = (("la_nappe_retrouve", "la nappe relancée"), ("la_spire_retrouve", "la spire"),
             ("la_croissance_retrouve", "la croissance hors des semis"))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"aux {v['f']} sauts faux, la spire est sur un mauvais tour {v['k']} fois, hors de tout tour {v['z']} fois : "
            f"{v['lissue'].split(' ; ')[-1]}").upper()


def la_case(retrouves: list[int], attendu: int) -> tuple[str, str]:
    """Le texte et le genre d'une case : le bon tour, un mauvais, ou aucun."""
    if attendu in retrouves:
        return ", ".join(f"{t}" for t in retrouves).replace("-", "−"), "bon"
    if retrouves:
        return ", ".join(f"{t}" for t in retrouves).replace("-", "−"), "faux"
    return "aucun tour", "vide"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": [], "barres": [], "ecretes": 0, "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "vert : le tour attendu ; orange : un autre tour ; gris : aucun tour à un quart de pas", petit, GRIS)

    x0, y0, x1, y1 = 50, 76, 740, 450
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "PHercParis4 : ce que retrouve chaque part, au saut faux", moyen, ENCRE)
    for n, (_, nom) in enumerate(LES_PARTS):
        ecrire(x0 + 140 + n * 180, y0 + 40, nom, 0, GRIS)
    for m, x in enumerate(d["les_sauts_faux"]):
        ya = y0 + 70 + m * 90
        ecrire(x0 + 12, ya + 14, f"graine {x['le_rang']}, saut {x['le_saut']}", 0, ENCRE)
        ecrire(x0 + 12, ya + 30, f"on attend {x['le_tour_attendu']}".replace("-", "−"), 0, GRIS)
        for n, (cle, _) in enumerate(LES_PARTS):
            texte, genre = la_case(x[cle], x["le_tour_attendu"])
            xa = x0 + 140 + n * 180
            traces["rectangles"].append((0, xa, xa + 160))
            art.rectangle([xa, ya, xa + 160, ya + 56], fill={"bon": CASE_BONNE, "faux": CASE_FAUSSE, "vide": CASE_VIDE}[genre])
            ecrire(xa + 10, ya + 20, texte, moyen, ENCRE)
            traces["cases"].append((x["le_rang"], cle, genre))

    x0, y0, x1, y1 = 770, 76, 1310, 450
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la descente, côté moins : sur les nappes / sur les spires", moyen, ENCRE)
    gy0, gy1 = y0 + 50, y1 - 70
    for q in (2, 4, 6, 8):
        yq = gy1 - q / LE_MAX * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, str(q), 0, GRIS)
    spires = {x["le_rang"]: x for x in d["les_descentes_des_spires"] if x["le_cote"] == "moins"}
    for n, g in enumerate(d["les_graines"]["PHercParis4"]):
        xa = x0 + 55 + n * 58
        for dx, h, col, cle in ((0, g["les_cotes"]["moins"]["la_descente"], CLAIR_BON, "nappes"),
                                (20, spires[g["le_rang"]]["la_descente"], BON, "spires")):
            if not 0 <= h <= LE_MAX:
                traces["ecretes"] += 1
            hh = min(LE_MAX, max(0, h))
            art.rectangle([xa + dx, gy1 - hh / LE_MAX * (gy1 - gy0), xa + dx + 17, gy1], fill=col)
            traces["barres"].append((g["le_rang"], cle, h))
            traces["rectangles"].append((1, xa + dx, xa + dx + 17))
        ecrire(int(xa + 8), gy1 + 6, f"g{g['le_rang']}", 0, ENCRE)
        arret = spires[g["le_rang"]]["larret"]
        ecrire(int(xa), gy1 + 22 + (n % 2) * 14, {"un saut faux": "faux", "un tour manqué": "manqué", "non lue": "non lue",
                                                   "le bout de la chaîne": "bout"}.get(arret, arret[:7]), 0,
               ALERTE if arret == "un saut faux" else GRIS)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : qu'une spire hors de tout tour soit sur le bon ; 5753_-7, lu là, ne la retrouve pas.",
           moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_334.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = dict(d, le_verdict={"decidable": True, "f": 5, "k": 4, "z": 1, "lissue": "x ; c'est la spire qui se trompe"})
    v("★★★ le titre LIT la mesure", le_titre(autre) == "AUX 5 SAUTS FAUX, LA SPIRE EST SUR UN MAUVAIS TOUR 4 FOIS, HORS DE TOUT TOUR 1 "
      "FOIS : C'EST LA SPIRE QUI SE TROMPE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(x["le_rang"], cle, la_case(x[cle], x["le_tour_attendu"])[1]) for x in d["les_sauts_faux"] for cle, _ in LES_PARTS]
    v("★★★ une case par saut faux et par part, au genre mesuré", traces["cases"] == attendu)
    v("★★★ une case verte seulement pour le tour attendu", la_case([-6, -7], -7)[1] == "bon" and la_case([-6], -7)[1] == "faux"
      and la_case([], -7)[1] == "vide")
    spires = {x["le_rang"]: x["la_descente"] for x in d["les_descentes_des_spires"] if x["le_cote"] == "moins"}
    v("★★★ deux barres par graine, sur les nappes et sur les spires", traces["barres"] == [
        (g["le_rang"], c, h) for g in d["les_graines"]["PHercParis4"]
        for c, h in (("nappes", g["les_cotes"]["moins"]["la_descente"]), ("spires", spires[g["le_rang"]]))])
    v("★★★ aucune barre n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2])]
    v("★★★★ aucune barre ni aucune case ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "334_au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.png")
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
