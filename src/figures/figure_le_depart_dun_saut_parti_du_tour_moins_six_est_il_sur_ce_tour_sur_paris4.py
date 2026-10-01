"""Sur PHercParis4 : où est la surface de départ d'un saut là où son arrivée est lue, et combien le saut mesure contre l'écart des deux tours.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, l'écart de la surface de départ à son tour, au même endroit : une rangée pour
le témoin (les sauts d'une feuille jugés justes), une pour la cible (les sauts d'une feuille partis du tour −6). La bande grise est le
quart de pas où un départ est sur son tour. À droite, chaque saut placé par l'écart du tour suivant et par sa propre longueur : sur la
diagonale, un saut franchit l'écart de deux tours. Le témoin s'y range ; les sauts de la cible partis du tour −6 vont bien au-delà.

  uv run python src/figures/figure_le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.py \
      --sortie docs/images/406_le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.png

⚠ Tout vient de la mesure de `406`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.json"

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
A = (50, 70, 560, 500, 150, 540, 160, 420)
B = (580, 70, 1150, 500, 640, 1130, 140, 420)


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_nombre(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",").replace("-", "−")


def les_lus(d: dict, partie: str, feuilles: int | None = 1) -> list[dict]:
    return [x for x in d[partie] if x["au_depart"]["lue"] and (feuilles is None or x["le_nombre_de_feuilles"] == feuilles)]


def les_comptes(d: dict) -> tuple[int, int, int, int]:
    """Les départs sur leur tour, et les sauts lus : du témoin, puis de la cible d'une feuille."""
    t, c = les_lus(d, "les_sauts_justes"), les_lus(d, "les_sauts_de_moins_six")
    return sum(x["au_depart"]["sur_son_tour"] for x in t), len(t), sum(x["au_depart"]["sur_son_tour"] for x in c), len(c)


def le_titre(d: dict) -> str:
    w, t, k, n = les_comptes(d)
    return (f"départs sur leur tour au même endroit : témoin {w} sur {t}, partis du tour −6 {k} sur {n} ; "
            f"{d['le_verdict']['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    sur = [x for x in les_lus(d, "les_sauts_de_moins_six") if x["au_depart"]["sur_son_tour"]]
    hors = [x for x in les_lus(d, "les_sauts_de_moins_six") if not x["au_depart"]["sur_son_tour"]]
    plage = lambda xs: f"{le_nombre(min(xs))} à {le_nombre(max(xs))}" if xs else "aucun"  # noqa: E731
    deux = ("rapporté à côté, qui ne décide rien : partis du tour −6 et sur lui, les sauts d'une feuille mesurent "
            f"{plage([abs(x['au_depart']['le_saut_en_pas']) for x in sur])} pas ; hors de lui, leurs départs sont à "
            f"{plage([x['au_depart']['lecart_du_depart_en_pas'] for x in hors])} pas, vers l'extérieur")
    trois = "⚠ ce qui n'est PAS établi : là où le départ est sur le tour −6, si c'est le tour −7 publié ou le compte de m7 qui se trompe."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [A[:4], B[:4]]
    c = d["les_constantes"]
    q = c["le_quart_en_pas"]
    traces = {"departs": [], "sauts": [], "bande": None, "diagonale": None, "comptes": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "en bleu le témoin, les sauts d'une feuille jugés justes ; en orange les sauts partis du tour −6, en brun ceux dont le "
           "départ n'est pas sur lui ; en carré, deux feuilles", petit, GRIS)
    for x0, y0, x1, y1 in cadres:
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)

    _, _, _, _, ax0, ax1, ay0, ay1 = A
    temoin, cible = les_lus(d, "les_sauts_justes"), les_lus(d, "les_sauts_de_moins_six")
    xs = [x["au_depart"]["lecart_du_depart_en_pas"] for x in temoin + cible]
    borne = max(1.0, math.ceil(max(abs(v) for v in xs) * 4) / 4) if xs else 1.0
    px = lambda v: ax0 + (v + borne) / (2 * borne) * (ax1 - ax0)  # noqa: E731
    ecrire(62, 78, "l'écart du départ à son tour", moyen, ENCRE)
    ecrire(62, 100, "au même endroit que l'arrivée, en pas nominaux", petit, GRIS)
    art.rectangle([px(-q), ay0, px(q), ay1], fill=ZONE)
    traces["bande"] = (-q, q)
    for i in range(int(round(2 * borne / 0.25)) + 1):
        v = -borne + i * 0.25
        art.line([(px(v), ay0), (px(v), ay1)], fill=TRAIT)
        if i % 2 == 0:
            ecrire(px(v) - 8, ay1 + 6, le_nombre(v), petit, GRIS)
    art.rectangle([ax0, ay0, ax1, ay1], outline=GRIS)
    w, t, k, n = les_comptes(d)
    for j, (nom, xs_, y_c, (ok, tot), couleur) in enumerate((("témoin", temoin, ay0 + 70, (w, t), BLEU),
                                                              ("partis du tour −6", cible, ay0 + 190, (k, n), ORANGE))):
        ecrire(62, y_c - 20, nom, petit, ENCRE)
        ecrire(62, y_c - 4, f"{ok} sur {tot}", petit, couleur)
        traces["comptes"].append((ok, tot))
        for i, x in enumerate(xs_):
            v = x["au_depart"]["lecart_du_depart_en_pas"]
            fill = couleur if x["au_depart"]["sur_son_tour"] or j == 0 else ALERTE
            y = y_c + ((i % 9) - 4) * 6
            art.ellipse([px(v) - 3, y - 3, px(v) + 3, y + 3], fill=fill)
            traces["departs"].append((j, v, px(v), y, fill))
    ecrire(ax0, ay1 + 28, "écart du départ ; en gris, un quart de pas de part et d'autre", petit, ENCRE)

    _, _, _, _, bx0, bx1, by0, by1 = B
    tous = temoin + les_lus(d, "les_sauts_de_moins_six", None)
    gx = [abs(x["au_depart"]["lecart_du_suivant_en_pas"]) for x in tous]
    gy = [abs(x["au_depart"]["le_saut_en_pas"]) for x in tous]
    xmax, ymax = max(1.0, math.ceil(max(gx, default=1.0))), max(1.0, math.ceil(max(gy, default=1.0) * 2) / 2)
    qx = lambda v: bx0 + v / xmax * (bx1 - bx0)  # noqa: E731
    qy = lambda v: by1 - v / ymax * (by1 - by0)  # noqa: E731
    ecrire(592, 78, "chaque saut, contre l'écart des deux tours", moyen, ENCRE)
    ecrire(592, 100, "longueur du saut en ordonnée, écart du tour suivant en abscisse, en pas nominaux", petit, GRIS)
    for i in range(int(xmax) + 1):
        art.line([(qx(i), by0), (qx(i), by1)], fill=TRAIT)
        ecrire(qx(i) - 3, by1 + 6, str(i), petit, GRIS)
    for j in range(int(round(ymax * 2)) + 1):
        art.line([(bx0, qy(j / 2)), (bx1, qy(j / 2))], fill=TRAIT)
        ecrire(bx0 - 30, qy(j / 2) - 7, le_nombre(j / 2), petit, GRIS)
    m = min(xmax, ymax)
    art.line([(qx(0), qy(0)), (qx(m), qy(m))], fill=GRIS, width=2)
    traces["diagonale"] = (0.0, m)
    art.rectangle([bx0, by0, bx1, by1], outline=GRIS)
    for x in sorted(tous, key=lambda x: (x["de_moins_six"], x["le_nombre_de_feuilles"])):
        a = x["au_depart"]
        u, v = qx(abs(a["lecart_du_suivant_en_pas"])), qy(abs(a["le_saut_en_pas"]))
        if not x["de_moins_six"]:
            art.ellipse([u - 2, v - 2, u + 2, v + 2], fill=BLEU)
            genre = "témoin"
        elif x["le_nombre_de_feuilles"] == 2:
            art.rectangle([u - 5, v - 5, u + 5, v + 5], fill=ORANGE, outline=ENCRE)
            genre = "deux"
        else:
            art.ellipse([u - 5, v - 5, u + 5, v + 5], fill=ORANGE if a["sur_son_tour"] else ALERTE, outline=ENCRE)
            genre = "cible" if a["sur_son_tour"] else "hors"
        traces["sauts"].append((genre, abs(a["lecart_du_suivant_en_pas"]), abs(a["le_saut_en_pas"]), u, v))
    ecrire(bx0, by1 + 28, "écart du tour suivant ; sur la diagonale, le saut franchit un écart de tour", petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_406.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    lu = lambda s, n=1: {"le_nombre_de_feuilles": n, "au_depart": {"lue": True, "sur_son_tour": s}}  # noqa: E731
    autre = {"le_verdict": {"lissue": "x ; non"}, "les_sauts_justes": [lu(True)] * 3, "les_sauts_de_moins_six": [lu(False), lu(True), lu(True, 2)]}
    v("★★★ le titre LIT la mesure",
      le_titre(autre) == "DÉPARTS SUR LEUR TOUR AU MÊME ENDROIT : TÉMOIN 3 SUR 3, PARTIS DU TOUR −6 1 SUR 2 ; NON", le_titre(autre))
    w, t, k, n = les_comptes(d)
    v("★★★★ les comptes de la figure sont ceux du verdict",
      d["le_verdict"]["lissue"].startswith(f"départs sur le tour −6 au même endroit : {k} sur {n} ; témoin : {w} sur {t} sur leur tour")
      and traces["comptes"] == [(w, t), (k, n)])
    v("★★★★ chaque départ lu d'une feuille est un point à gauche, une fois", len(traces["departs"]) == t + n)
    v("★★★★ les départs en brun sont ceux de la cible qui ne sont pas sur le tour −6",
      sum(p[4] == ALERTE for p in traces["departs"]) == n - k)
    v("★★★★ la bande grise est le quart de pas de la règle",
      traces["bande"] == (-d["les_constantes"]["le_quart_en_pas"], d["les_constantes"]["le_quart_en_pas"]))
    tous = len(les_lus(d, "les_sauts_justes")) + len(les_lus(d, "les_sauts_de_moins_six", None))
    v("★★★★ chaque saut lu est un point à droite, les deux feuilles en carré",
      len(traces["sauts"]) == tous and sum(p[0] == "deux" for p in traces["sauts"])
      == sum(x["le_nombre_de_feuilles"] == 2 for x in les_lus(d, "les_sauts_de_moins_six", None)))
    v("★★★★ la diagonale part de zéro et monte d'un pour un", traces["diagonale"][0] == 0.0 and traces["diagonale"][1] > 0)
    dehors = [p for p in traces["departs"] if not (A[4] <= p[2] <= A[5] and A[6] <= p[3] <= A[7])]
    dehors += [p for p in traces["sauts"] if not (B[4] <= p[3] <= B[5] and B[6] <= p[4] <= B[7])]
    v("★★★★ aucun point ne sort de son graphe", not dehors, str(dehors[:3]))
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
                   / "406_le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.png")
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
