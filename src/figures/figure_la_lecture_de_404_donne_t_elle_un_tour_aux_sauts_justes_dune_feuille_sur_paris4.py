"""Sur PHercParis4 : les tours franchis que lisent les deux lectures, sur les sauts d'une feuille jugés justes et sur les sauts partis du tour −6.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, les sauts d'une feuille jugés justes, une colonne par tour de départ : en bleu
la lecture au même endroit, en gris celle de `404`. Si une lecture vaut, ses points tombent dans la bande grise, entre 0,5 et 1,5 tour.
À droite, la relecture des sauts partis du tour −6, une colonne par graine : là, le témoin d'une feuille sort de la bande.

  uv run python src/figures/figure_la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.py \
      --sortie docs/images/405_la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.png

⚠ Tout vient de la mesure de `405`.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (178, 181, 186)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ZONE = (222, 226, 230)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 640
LA_BANDE = 520
PY_BAS, PY_HAUT = 420, 130
LES_PANNEAUX = ((50, 70, 600, 500, 110, 580), (620, 70, 1150, 500, 680, 1130))
LES_PLAFONDS = (3.0, 6.0)


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_nombre(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",").replace("-", "−")


def dans(d: dict, k: float) -> bool:
    c = d["les_constantes"]
    return c["le_bas"] <= k < c["le_haut"]


def les_colonnes_justes(d: dict) -> list[tuple[int, list[float], list[float]]]:
    """Par tour de départ, du plus extérieur au plus intérieur : les tours franchis lus au même endroit, et par la lecture de `404`."""
    departs = sorted({x["le_depart"] for x in d["les_sauts_justes"]}, reverse=True)
    lus = lambda xs, l: [x[l]["les_tours_franchis"] for x in xs if x[l]["lue"]]  # noqa: E731
    return [(k, lus([x for x in d["les_sauts_justes"] if x["le_depart"] == k], "au_meme_endroit"),
             lus([x for x in d["les_sauts_justes"] if x["le_depart"] == k], "la_lecture_de_404")) for k in departs]


def les_colonnes_du_tour_moins_six(d: dict) -> list[tuple[int, list[tuple[int, float]], list[float]]]:
    """Par graine : les sauts partis du tour −6 lus au même endroit, avec leurs feuilles, et les tours franchis par la lecture de `404`."""
    rangs = sorted({x["le_rang"] for x in d["les_sauts_de_moins_six"]})
    xs = lambda r: [x for x in d["les_sauts_de_moins_six"] if x["le_rang"] == r]  # noqa: E731
    return [(r, [(x["le_nombre_de_feuilles"], x["au_meme_endroit"]["les_tours_franchis"]) for x in xs(r) if x["au_meme_endroit"]["lue"]],
             [x["la_lecture_de_404"]["les_tours_franchis"] for x in xs(r) if x["la_lecture_de_404"]["lue"]]) for r in rangs]


def les_bornes(valeurs: list[float], plafond: float = math.inf) -> tuple[float, float, float]:
    """Le bas, le haut et le pas de l'axe ; le haut ne passe pas `plafond`, et ce qui le dépasse est marqué au bord."""
    ymin = min(0.0, math.floor(min(valeurs, default=0.0) * 2) / 2)
    ymax = min(plafond, max(2.0, math.ceil(max(valeurs, default=2.0) * 2) / 2))
    pas = 0.5 if ymax - ymin <= 3 else 1.0
    return ymin, math.ceil(ymax / pas) * pas, pas


def le_temoin(d: dict, lecture: str) -> tuple[int, int]:
    k = [x[lecture]["les_tours_franchis"] for x in d["les_sauts_de_moins_six"] if x["le_nombre_de_feuilles"] == 1 and x[lecture]["lue"]]
    return sum(dans(d, x) for x in k), len(k)


def le_titre(d: dict) -> str:
    cols = les_colonnes_justes(d)
    a = [k for _, xs, _ in cols for k in xs]
    b = [k for _, _, xs in cols for k in xs]
    dits = d["le_verdict"]["lissue"].rpartition(" ; au même endroit : ")[2].split(" ; lecture de 404 : ")
    fin = f"{dits[0]} et {dits[1]}" if len(dits) == 2 else d["le_verdict"]["lissue"].rpartition(" ; ")[2]
    return (f"sauts jugés justes : {sum(dans(d, k) for k in a)} sur {len(a)} à un tour au même endroit, "
            f"{sum(dans(d, k) for k in b)} sur {len(b)} par la lecture de 404 ; {fin}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = f"rapporté à côté, qui ne décide rien (relecture) : {d['la_relecture']['lissue']}"
    trois = "⚠ ce qui n'est PAS établi : si, au tour −6, la faute est au tour −7 publié ou aux sauts eux-mêmes."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [p[:4] for p in LES_PANNEAUX]
    c = d["les_constantes"]
    traces = {"justes": [], "moins_six": [], "comptes": [], "zones": [], "au_bord": [], "les_hauts": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    def le_graphe(px0, px1, valeurs, n_colonnes, plafond):
        ymin, ymax, pas = les_bornes(valeurs, plafond)
        py = lambda y: PY_BAS - (min(y, ymax) - ymin) / (ymax - ymin) * (PY_BAS - PY_HAUT)  # noqa: E731
        haut_, bas_ = py(min(c["le_haut"], ymax)), py(max(c["le_bas"], ymin))
        art.rectangle([px0, haut_, px1, bas_], fill=ZONE)
        traces["zones"].append((ymin + (PY_BAS - bas_) / (PY_BAS - PY_HAUT) * (ymax - ymin),
                                ymin + (PY_BAS - haut_) / (PY_BAS - PY_HAUT) * (ymax - ymin)))
        for j in range(int(math.floor((ymax - ymin) / pas + 1e-9)) + 1):
            y = ymin + j * pas
            art.line([(px0, py(y)), (px1, py(y))], fill=TRAIT)
            ecrire(px0 - 34, py(y) - 7, le_nombre(y), petit, GRIS)
        y1 = py(1.0)
        art.line([(px0, y1), (px1, y1)], fill=GRIS)
        art.rectangle([px0, PY_HAUT, px1, PY_BAS], outline=GRIS)
        return py, (px1 - px0) / max(1, n_colonnes)

    def un_point(x, y, n, couleur, creux=False, v=None, haut=math.inf):
        if v is not None and v > haut:
            art.polygon([(x - 5, y + 8), (x + 5, y + 8), (x, y)], fill=couleur)
            ecrire(x + 7, y + 2, le_nombre(v), petit, couleur)
            traces["au_bord"].append(v)
            return
        if n == 2:
            art.rectangle([x - 5, y - 5, x + 5, y + 5], fill=ORANGE, outline=ENCRE)
        elif creux:
            art.ellipse([x - 3, y - 3, x + 3, y + 3], outline=couleur)
        else:
            art.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur)

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "chaque point : un saut lu ; en bleu la lecture au même endroit, en gris celle de 404 ; en carré orange, deux feuilles ; "
           "en gris clair, entre 0,5 et 1,5 tour", petit, GRIS)
    for x0, y0, x1, y1 in cadres:
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)

    (_, _, _, _, ax0, ax1), (_, _, _, _, bx0, bx1) = LES_PANNEAUX
    cols = les_colonnes_justes(d)
    ecrire(62, 78, "sauts d'une feuille jugés justes", moyen, ENCRE)
    ecrire(62, 100, "tours franchis, par tour de départ", petit, GRIS)
    py, larg = le_graphe(ax0, ax1, [k for _, a, b in cols for k in a + b], len(cols), LES_PLAFONDS[0])
    haut_a = les_bornes([k for _, a, b in cols for k in a + b], LES_PLAFONDS[0])[1]
    traces["les_hauts"].append(haut_a)
    for i, (k, a, b) in enumerate(cols):
        cx = ax0 + (i + 0.5) * larg
        for j, v in enumerate(a):
            un_point(cx - 12 + ((j % 5) - 2) * 3, py(v), 1, BLEU, v=v, haut=haut_a)
            traces["justes"].append(("au_meme_endroit", k, v, cx - 12 + ((j % 5) - 2) * 3, py(v)))
        for j, v in enumerate(b):
            un_point(cx + 12 + ((j % 5) - 2) * 3, py(v), 1, GRIS, creux=True, v=v, haut=haut_a)
            traces["justes"].append(("la_lecture_de_404", k, v, cx + 12 + ((j % 5) - 2) * 3, py(v)))
        na, nb = sum(dans(d, v) for v in a), sum(dans(d, v) for v in b)
        traces["comptes"].append((k, na, len(a), nb, len(b)))
        ecrire(cx - 8, PY_BAS + 6, le_nombre(k), petit, ENCRE)
        ecrire(cx - 16, PY_BAS + 22, f"{na}/{len(a)}", petit, BLEU)
        ecrire(cx - 16, PY_BAS + 38, f"{nb}/{len(b)}", petit, GRIS)
    ecrire(ax0, PY_BAS + 58, "tour de départ ; sous chaque colonne, les sauts entre 0,5 et 1,5 tour", petit, ENCRE)

    colsb = les_colonnes_du_tour_moins_six(d)
    w, t = le_temoin(d, "au_meme_endroit")
    w4, t4 = le_temoin(d, "la_lecture_de_404")
    ecrire(632, 78, "partis du tour −6, relus au même endroit", moyen, ENCRE)
    ecrire(632, 100, f"témoin d'une feuille entre 0,5 et 1,5 tour : {w} sur {t} ; par la lecture de 404, {w4} sur {t4}", petit, GRIS)
    vals_b = [v for _, a, b in colsb for _, v in a] + [v for _, _, b in colsb for v in b]
    py, larg = le_graphe(bx0, bx1, vals_b, len(colsb), LES_PLAFONDS[1])
    haut_b = les_bornes(vals_b, LES_PLAFONDS[1])[1]
    traces["les_hauts"].append(haut_b)
    for i, (r, a, b) in enumerate(colsb):
        cx = bx0 + (i + 0.5) * larg
        for j, (n, v) in enumerate(sorted(a)):
            un_point(cx - 12 + ((j % 3) - 1) * 6, py(v), n, BLEU, v=v, haut=haut_b)
            traces["moins_six"].append(("au_meme_endroit", r, n, v, cx - 12 + ((j % 3) - 1) * 6, py(v)))
        for j, v in enumerate(b):
            un_point(cx + 14 + ((j % 3) - 1) * 4, py(v), 1, GRIS, creux=True, v=v, haut=haut_b)
            traces["moins_six"].append(("la_lecture_de_404", r, None, v, cx + 14 + ((j % 3) - 1) * 4, py(v)))
        ecrire(cx - 4, PY_BAS + 6, str(r), petit, ENCRE)
    ecrire(bx0, PY_BAS + 28, "graine, côté moins", petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un_, deux_, trois_ = la_bande(d)
    ecrire(50, LA_BANDE + 10, un_, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux_, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois_, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_405.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    lu = lambda k: {"lue": True, "les_tours_franchis": k}  # noqa: E731
    autre = {"les_constantes": d["les_constantes"],
             "le_verdict": {"decidable": True, "lissue": "x ; au même endroit : oui ; lecture de 404 : en partie"},
             "les_sauts_justes": [{"le_depart": -1, "au_meme_endroit": lu(1.0), "la_lecture_de_404": lu(k)} for k in (1.0, 1.0, 3.0)]}
    v("★★★ le titre LIT la mesure", le_titre(autre)
      == "SAUTS JUGÉS JUSTES : 3 SUR 3 À UN TOUR AU MÊME ENDROIT, 2 SUR 3 PAR LA LECTURE DE 404 ; OUI ET EN PARTIE", le_titre(autre))
    lus = lambda l: [x for x in d["les_sauts_justes"] if x[l]["lue"]]  # noqa: E731
    for l_ in ("au_meme_endroit", "la_lecture_de_404"):
        v(f"★★★★ chaque saut juste lu par {l_} est un point, une fois", sum(p[0] == l_ for p in traces["justes"]) == len(lus(l_)))
    na, n = sum(x[1] for x in traces["comptes"]), sum(x[2] for x in traces["comptes"])
    nb, m = sum(x[3] for x in traces["comptes"]), sum(x[4] for x in traces["comptes"])
    v("★★★★ les comptes sous les colonnes somment à ceux du verdict",
      d["le_verdict"]["lissue"].startswith(f"sauts d'une feuille jugés justes : au même endroit, {na} sur {n} entre")
      and f"lecture de 404, {nb} sur {m}" in d["le_verdict"]["lissue"], f"{na} {n} {nb} {m}")
    v("★★★★ chaque colonne porte les sauts de son tour de départ",
      all(sum(1 for p in traces["justes"] if p[0] == "au_meme_endroit" and p[1] == k) == x[2]
          == sum(1 for s in lus("au_meme_endroit") if s["le_depart"] == k) for x in traces["comptes"] for k in [x[0]]))
    rel = [x for x in d["les_sauts_de_moins_six"] if x["au_meme_endroit"]["lue"]]
    v("★★★★ chaque saut parti du tour −6 et relu est un point, les sauts de deux feuilles en carré",
      sum(p[0] == "au_meme_endroit" for p in traces["moins_six"]) == len(rel)
      and sum(p[0] == "au_meme_endroit" and p[2] == 2 for p in traces["moins_six"]) == sum(x["le_nombre_de_feuilles"] == 2 for x in rel))
    w, t = le_temoin(d, "au_meme_endroit")
    v("★★★★ le témoin de la relecture est celui que la relecture publie", f"témoin : {w} sur {t} entre" in d["la_relecture"]["lissue"],
      f"{w} {t}")
    c = d["les_constantes"]
    v("★★★★ la bande grise va de la borne basse à la borne haute de la règle",
      all(abs(lo - c["le_bas"]) < 0.02 and abs(hi - c["le_haut"]) < 0.02 for lo, hi in traces["zones"]), str(traces["zones"]))
    x_ = [(p[3], p[4]) for p in traces["justes"]] + [(p[4], p[5]) for p in traces["moins_six"]]
    dehors = [(x, y) for x, y in x_ if not (any(a[0] < x < a[2] for a in cadres) and PY_HAUT <= y <= PY_BAS)]
    v("★★★★ aucun point ne sort de son graphe", not dehors, str(dehors[:3]))
    tous = [p[2] for p in traces["justes"]] + [p[3] for p in traces["moins_six"]]
    v("★★★★ chaque valeur au-delà du haut de son axe est marquée au bord, avec sa valeur",
      sorted(traces["au_bord"]) == sorted([p[2] for p in traces["justes"] if p[2] > traces["les_hauts"][0]]
                                          + [p[3] for p in traces["moins_six"] if p[3] > traces["les_hauts"][1]])
      and all(any(t_ == le_nombre(x) for _, _, t_, _ in poses) for x in traces["au_bord"]) and len(tous) > 0, str(traces["au_bord"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t_, _ in poses for x in glyphes_manquants(t_)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
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
                   / "405_la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.png")
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
