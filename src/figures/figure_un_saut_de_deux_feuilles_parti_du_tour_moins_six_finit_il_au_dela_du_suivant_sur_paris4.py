"""Sur PHercParis4 : chaque saut parti du tour −6, placé par l'écart du tour −7 au tour −6 et par l'écart de sa surface d'arrivée au tour −6.

⚠⚠ **Ce que cette figure doit rendre évident.** Un point par saut lu de `404` : en abscisse, l'écart du tour −7 au tour −6 là où arrive
le saut ; en ordonnée, l'écart de sa surface d'arrivée au tour −6, tous deux en pas nominaux. Leur rapport compte les tours franchis. La
zone grise est celle où le témoin, les sauts d'une feuille, devait tomber : entre 0,5 et 1,5 tour. Si la lecture vaut, les ronds bleus y
sont presque tous. À droite, graine par graine, les écarts lus.

  uv run python src/figures/figure_un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.py \
      --sortie docs/images/404_un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.png

⚠ Tout vient de la mesure de `404`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ZONE = (222, 226, 230)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 640
LA_BANDE = 520
PX0, PX1, PY_BAS, PY_HAUT = 120, 620, 440, 110
LES_COLONNES = (676, 746, 856, 976)


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_nombre(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def la_plage(vals: list[float]) -> str:
    if not vals:
        return "aucun"
    lo, hi = min(vals), max(vals)
    return le_nombre(lo) if lo == hi else f"{le_nombre(lo)}-{le_nombre(hi)}"


def les_points(d: dict) -> list[dict]:
    """Les sauts lus, chacun une fois : l'écart du tour −7 en abscisse, celui de l'arrivée en ordonnée, orientée comme le tour −7."""
    out = []
    for s in d["les_sauts"]:
        lec = s["la_lecture"]
        if not lec["lue"]:
            continue
        es, et = lec["lecart_du_suivant_en_pas"], lec["lecart_au_depart_en_pas"]
        out.append({"le_rang": s["le_rang"], "n": s["le_nombre_de_feuilles"], "x": abs(es), "y": math.copysign(1.0, es) * et,
                    "k": lec["les_tours_franchis"]})
    return out


def le_temoin(d: dict) -> tuple[int, int]:
    """Les sauts d'une feuille lus entre les deux bornes de la règle, et combien en sont lus."""
    c = d["les_constantes"]
    k = [p["k"] for p in les_points(d) if p["n"] == 1]
    return sum(c["le_bas"] <= x < c["le_haut"] for x in k), len(k)


def le_temoin_en_trois(d: dict) -> tuple[int, int, int]:
    """Les sauts d'une feuille lus sous la borne basse, entre les deux bornes, et à la borne haute ou au-delà."""
    c = d["les_constantes"]
    k = [p["k"] for p in les_points(d) if p["n"] == 1]
    return sum(x < c["le_bas"] for x in k), sum(c["le_bas"] <= x < c["le_haut"] for x in k), sum(x >= c["le_haut"] for x in k)


def les_bornes(points: list[dict]) -> tuple[float, float, float]:
    xmax = max(1.0, math.ceil(max((p["x"] for p in points), default=1.0)))
    ymin = min(0.0, math.floor(min((p["y"] for p in points), default=0.0) * 2) / 2)
    ymax = max(0.5, math.ceil(max((p["y"] for p in points), default=0.5) * 2) / 2)
    return xmax, ymin, ymax


def la_zone(bas: float, haut: float, xmax: float, ymax: float) -> list[tuple[float, float]]:
    """Le coin entre les rapports `bas` et `haut`, coupé au haut du graphe."""
    poly, out = [(0.0, 0.0), (xmax, bas * xmax), (xmax, haut * xmax)], []
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        if y1 <= ymax:
            out.append((x1, y1))
        if (y1 <= ymax) != (y2 <= ymax):
            t = (ymax - y1) / (y2 - y1)
            out.append((x1 + t * (x2 - x1), ymax))
    return out


def les_rangees(d: dict) -> list[tuple[int, str, str, str]]:
    """Graine par graine : l'écart du tour −7, celui des arrivées d'une feuille, celui des arrivées de deux."""
    pts = les_points(d)
    return [(r, la_plage([p["x"] for p in pts if p["le_rang"] == r]), la_plage([p["y"] for p in pts if p["le_rang"] == r and p["n"] == 1]),
             la_plage([p["y"] for p in pts if p["le_rang"] == r and p["n"] == 2])) for r in sorted({p["le_rang"] for p in pts})]


def le_titre(d: dict) -> str:
    w, t = le_temoin(d)
    c = d["les_constantes"]
    return (f"témoin : {w} saut d'une feuille sur {t} entre {le_nombre(c['le_bas'])} et {le_nombre(c['le_haut'])} tour ; "
            f"{d['le_verdict']['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    pts = les_points(d)
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = ("rapporté à côté, qui ne décide rien : arrivées d'une feuille à "
            f"{la_plage([p['y'] for p in pts if p['n'] == 1])} pas du tour −6, de deux feuilles à {la_plage([p['y'] for p in pts if p['n'] == 2])} ; "
            f"le tour −7 à {la_plage([p['x'] for p in pts])} pas du tour −6")
    trois = "⚠ ce qui n'est PAS établi : si la faute est au tour −7 publié ou à la lecture elle-même ; ni ce que vaut un saut de deux feuilles."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 640, 500), (660, 70, 1150, 500)]
    c = d["les_constantes"]
    pts = les_points(d)
    xmax, ymin, ymax = les_bornes(pts)
    px = lambda x: PX0 + x / xmax * (PX1 - PX0)  # noqa: E731
    py = lambda y: PY_BAS - (y - ymin) / (ymax - ymin) * (PY_BAS - PY_HAUT)  # noqa: E731
    traces = {"points": [], "zone": [], "rangees": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "chaque point : un saut lu, parti du tour −6 ; la hauteur rapportée à la largeur compte les tours franchis ; "
           "en gris, où le témoin devait tomber", petit, GRIS)
    for x0, y0, x1, y1 in cadres:
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)

    zone = la_zone(c["le_bas"], c["le_haut"], xmax, ymax)
    traces["zone"] = zone
    art.polygon([(px(x), py(y)) for x, y in zone], fill=ZONE)
    for i in range(int(xmax) + 1):
        art.line([(px(i), PY_HAUT), (px(i), PY_BAS)], fill=TRAIT)
        ecrire(px(i) - 3, PY_BAS + 6, str(i), petit, GRIS)
    for j in range(int(round((ymax - ymin) * 2)) + 1):
        y = ymin + j / 2
        art.line([(PX0, py(y)), (PX1, py(y))], fill=TRAIT)
        ecrire(PX0 - 34, py(y) - 7, le_nombre(y), petit, GRIS)
    un = min(xmax, ymax)
    art.line([(px(0), py(0)), (px(un), py(un))], fill=GRIS, width=1)
    art.rectangle([PX0, PY_HAUT, PX1, PY_BAS], outline=GRIS)
    ecrire(62, 84, "écart de l'arrivée au tour −6, en pas nominaux", petit, ENCRE)
    ecrire(PX0, PY_BAS + 28, "écart du tour −7 au tour −6, au même endroit, en pas nominaux", petit, ENCRE)

    lx, ly = PX1 - 186, PY_HAUT + 8
    art.ellipse([lx - 5, ly + 1, lx + 5, ly + 11], fill=BLEU)
    ecrire(lx + 12, ly, "une feuille, le témoin", petit, ENCRE)
    art.rectangle([lx - 5, ly + 21, lx + 5, ly + 31], fill=ORANGE, outline=ENCRE)
    ecrire(lx + 12, ly + 20, "deux feuilles", petit, ENCRE)
    art.rectangle([lx - 6, ly + 41, lx + 6, ly + 51], fill=ZONE, outline=GRIS)
    ecrire(lx + 12, ly + 40, f"entre {le_nombre(c['le_bas'])} et {le_nombre(c['le_haut'])} tour", petit, ENCRE)
    art.line([(lx - 6, ly + 66), (lx + 6, ly + 66)], fill=GRIS)
    ecrire(lx + 12, ly + 60, "un tour juste", petit, ENCRE)

    for p in sorted(pts, key=lambda p: p["n"]):
        x, y = px(p["x"]), py(p["y"])
        if p["n"] == 2:
            art.rectangle([x - 6, y - 6, x + 6, y + 6], fill=ORANGE, outline=ENCRE)
        else:
            art.ellipse([x - 5, y - 5, x + 5, y + 5], fill=BLEU, outline=FOND)
        traces["points"].append({**p, "px": x, "py": y, "dans_la_zone": c["le_bas"] <= p["k"] < c["le_haut"]})

    ecrire(676, 84, "par graine, côté moins", moyen, ENCRE)
    ecrire(676, 106, "écarts au tour −6, en pas nominaux", petit, GRIS)
    for x_, t_ in zip(LES_COLONNES, ("graine", "tour −7", "une feuille", "deux feuilles")):
        ecrire(x_, 134, t_, petit, GRIS)
    rangees = les_rangees(d)
    for i, rangee in enumerate(rangees):
        y = 160 + i * 26
        for x_, t_, couleur in zip(LES_COLONNES, (str(rangee[0]), *rangee[1:]), (ENCRE, ENCRE, BLEU, ORANGE)):
            ecrire(x_, y, t_, petit, couleur)
        traces["rangees"].append(rangee)
    w, t = le_temoin(d)
    sous, entre, dessus = le_temoin_en_trois(d)
    traces["en_trois"] = (sous, entre, dessus)
    non_lus = sum(not s["la_lecture"]["lue"] for s in d["les_sauts"])
    k1 = [p["k"] for p in pts if p["n"] == 1]
    k2 = [p["k"] for p in pts if p["n"] == 2]
    y = 160 + len(rangees) * 26 + 22
    for i, ligne in enumerate((f"lus : {len(pts)} sauts, {t} d'une feuille et {len(k2)} de deux ; non lus : {non_lus}",
                               "témoin : {} sous {} tour, {} entre {} et {}, {} à {} et plus".format(
                                   sous, le_nombre(c["le_bas"]), entre, le_nombre(c["le_bas"]), le_nombre(c["le_haut"]), dessus,
                                   le_nombre(c["le_haut"])),
                               f"tours franchis par le témoin : {la_plage(k1)}",
                               f"tours franchis par les sauts de deux feuilles : {la_plage(k2)}")):
        ecrire(676, y + i * 22, ligne, petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_404.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    c = d["les_constantes"]
    lu = lambda n, k: {"le_rang": 1, "le_nombre_de_feuilles": n,  # noqa: E731
                       "la_lecture": {"lue": True, "lecart_du_suivant_en_pas": -1.0, "lecart_au_depart_en_pas": -k, "les_tours_franchis": k}}
    autre = {"les_constantes": c, "le_verdict": {"decidable": True, "lissue": "x ; oui"},
             "les_sauts": [lu(1, 1.0)] * 4 + [lu(1, 2.0), lu(2, 2.0)]}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "TÉMOIN : 4 SAUT D'UNE FEUILLE SUR 5 ENTRE 0,5 ET 1,5 TOUR ; OUI", le_titre(autre))
    w, t = le_temoin(d)
    v("★★★★ le témoin de la figure est celui du verdict", f"témoin : {w} sur {t} entre" in d["le_verdict"]["lissue"], f"{w} {t}")
    lus = [s for s in d["les_sauts"] if s["la_lecture"]["lue"]]
    v("★★★★ chaque saut lu est un point, une fois, et aucun saut non lu", len(traces["points"]) == len(lus), f"{len(traces['points'])} {len(lus)}")
    v("★★★★ les sauts de deux feuilles sont les carrés",
      sum(p["n"] == 2 for p in traces["points"]) == sum(s["le_nombre_de_feuilles"] == 2 for s in lus))
    v("★★★★ le témoin en trois parts somme à ses sauts lus, et sa part du milieu est celle du verdict",
      sum(traces["en_trois"]) == t and traces["en_trois"][1] == w, str(traces["en_trois"]))
    v("★★★★ les ronds dans la zone sont le témoin qui vaut",
      sum(p["dans_la_zone"] for p in traces["points"] if p["n"] == 1) == w)
    v("★★★★ la hauteur rapportée à la largeur redonne les tours franchis de chaque saut",
      all(abs(p["y"] / p["x"] - p["k"]) < 0.01 * max(1.0, abs(p["k"])) for p in traces["points"]),
      str([(p["y"], p["x"], p["k"]) for p in traces["points"]][:3]))
    v("★★★★ la zone est le coin entre les deux bornes de la règle",
      len(traces["zone"]) >= 3 and all(c["le_bas"] * x - 1e-9 <= y <= c["le_haut"] * x + 1e-9 for x, y in traces["zone"])
      and any(abs(y - c["le_bas"] * x) < 1e-9 and x > 0 for x, y in traces["zone"])
      and any(abs(y - c["le_haut"] * x) < 1e-9 and x > 0 for x, y in traces["zone"]), str(traces["zone"]))
    v("★★★★ la zone coupée au haut du graphe ne perd pas son coin",
      len(la_zone(0.5, 1.5, 5.0, 2.5)) == 4
      and all(abs(a - b) < 1e-9 for p, q in zip(la_zone(0.5, 1.5, 5.0, 2.5), [(0.0, 0.0), (5.0, 2.5), (5.0, 2.5), (5.0 / 3.0, 2.5)])
              for a, b in zip(p, q)), str(la_zone(0.5, 1.5, 5.0, 2.5)))
    v("★★★★ aucun point ne sort du graphe",
      all(PX0 <= p["px"] <= PX1 and PY_HAUT <= p["py"] <= PY_BAS for p in traces["points"]))
    rangs = sorted({s["le_rang"] for s in lus})
    v("★★★★ une rangée par graine lue, et l'écart du tour −7 y est celui des sauts",
      [r[0] for r in traces["rangees"]] == rangs
      and all(r[1] == la_plage([abs(s["la_lecture"]["lecart_du_suivant_en_pas"]) for s in lus if s["le_rang"] == r[0]])
              for r in traces["rangees"]))
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
                   / "404_un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.png")
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
