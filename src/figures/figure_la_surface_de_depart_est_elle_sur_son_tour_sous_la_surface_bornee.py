"""Sous la surface bornée, graine 8, quatrième saut, là où ses points posés sur 5753_-2 franchissent une feuille : sur quel tour publié est posée la surface d'où part le saut, et, à côté, la même lecture sous les autres surfaces à deux tours.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, la part des pieds lus sur le tour de départ qui y sont posés : un point orange
pour la question, un pour son contrôle, et les autres surfaces à deux tours en gris ; les deux traits sont le quart et les trois quarts.
À droite, sur quels tours les pieds de la question et du contrôle sont posés.

  uv run python src/figures/figure_la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.py \\
      --sortie docs/images/348_la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.png

⚠ Tout vient de la mesure de `348`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
GRIS_POINT = (150, 153, 158)
L_, H_ = 1360, 600
LA_BANDE = 510
LES_SEUILS = (0.25, 0.75)
LE_GAUCHE, LA_DROITE = 300, 660
LES_RANGEES = ("la question", "son contrôle", "les autres surfaces à deux tours")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_surface(d: dict) -> dict:
    c = d["les_constantes"]["la_surface"]
    return next(s for s in d["les_surfaces"] if all(s[k] == v for k, v in c.items()))


def les_autres(d: dict) -> list[tuple[dict, float]]:
    """Les autres surfaces à deux tours dont la question est lue, avec la part posée."""
    c = d["les_constantes"]["la_surface"]
    return [(s, s["la_surface"]["la_question"]["la_part_posee"]) for s in d["les_surfaces"]
            if not all(s[k] == v for k, v in c.items()) and s["la_surface"] is not None
            and s["la_surface"]["la_question"]["la_part_posee"] is not None]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    _, _, suite = v["lissue"].rpartition(" ; ")
    w0 = la_surface(d)["la_surface"]["le_tour_de_depart"]
    return f"{round(100 * v['la_part'])} % des pieds lus sur 5753_{w0} y sont posés ; {suite}".upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    v = d["le_verdict"]
    parts = [p for _, p in les_autres(d)]
    un = f"LE VERDICT DÉCLARÉ : {v['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : sous les {len(parts)} autres surfaces à deux tours qui sont lues, "
            f"{sum(p >= LES_SEUILS[1] for p in parts)} ont les trois quarts de ces pieds posés sur le tour de départ")
    trois = "⚠ ce qui n'est PAS établi : si la surface de départ est à cheval par elle-même, ou si 5753_-1 y est mal posé."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": [], "lignes": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    s = la_surface(d)
    a = s["la_surface"]
    w0 = a["le_tour_de_depart"]
    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, f"sous la surface bornée, graine 8, saut 4 : la surface de départ est-elle posée sur 5753_{w0}, le tour qu'elle retrouve ?",
           petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des pieds posés sur le tour de départ", moyen, ENCRE)
    X = lambda p: LE_GAUCHE + p * (LA_DROITE - LE_GAUCHE)  # noqa: E731
    haut, bas = y0 + 50, y1 - 70
    traces["zone"] = (haut, bas)
    ys = [y0 + 100, y0 + 190, y0 + 290]
    for nom, yr in zip(LES_RANGEES, ys):
        ecrire(x0 + 12, yr - 7, nom, 0, ENCRE)
        art.line([LE_GAUCHE, yr, LA_DROITE, yr], fill=TRAIT)
    for p in LES_SEUILS:
        art.line([X(p), haut, X(p), bas], fill=ALERTE, width=2)
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        ecrire(int(X(p)) - 10, bas + 4, f"{int(p * 100)} %", 0, ALERTE if p in LES_SEUILS else GRIS)
    ecrire(LE_GAUCHE, y1 - 44, f"des pieds lus sur 5753_{w0}, la part qui y est posée", 0, ENCRE)

    def point(nom, yr, x, orange, cle):
        rr = 7 if orange else 4
        art.ellipse([x - rr, yr - rr, x + rr, yr + rr], fill=ALERTE if orange else GRIS_POINT, outline=ENCRE if orange else None)
        traces["points"].append((nom, cle, x))
        traces["rectangles"].append((0, x - rr, x + rr, yr - rr, yr + rr))

    point(LES_RANGEES[0], ys[0], X(a["la_question"]["la_part_posee"]), True, "question")
    point(LES_RANGEES[1], ys[1], X(a["le_controle"]["la_part_posee"]), True, "contrôle")
    for k, (t, p) in enumerate(les_autres(d)):
        point(LES_RANGEES[2], ys[2] + ((k * 37) % 41 - 20), X(p), False, (t["la_chaine"], t["le_rang"], t["le_saut"]))

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "sur quels tours les pieds sont posés", moyen, ENCRE)
    tours = sorted({int(t) for g in (a["la_question"], a["le_controle"]) for t in g["les_tours_des_pieds"]}, reverse=True)
    cols = [x0 + 12, x0 + 130, x0 + 200] + [x0 + 280 + 90 * i for i in range(len(tours))]
    cols.append(cols[-1] + 90)
    tetes = ["", "points", f"lus sur {w0}"] + [f"posés sur {t}" for t in tours] + ["sans tour"]
    for x, t in zip(cols, tetes):
        ecrire(x, y0 + 44, t, 0, GRIS)
    y = y0 + 66
    for nom, g in (("la question", a["la_question"]), ("son contrôle", a["le_controle"])):
        cellules = [nom, str(g["les_points"]), str(g["les_pieds_lus"])] + [str(g["les_tours_des_pieds"].get(str(t), 0)) for t in tours] \
            + [str(g["sans_tour"])]
        for x, t in zip(cols, cellules):
            ecrire(x, y, t, 0, ALERTE)
        traces["lignes"].append(cellules)
        y += 22
    ecrire(x0 + 12, y + 16, "la question : les points posés sur le tour de trop qui franchissent une feuille ;", 0, GRIS)
    ecrire(x0 + 12, y + 32, "le contrôle : ceux posés sur le tour attendu qui en franchissent une ;", 0, GRIS)
    ecrire(x0 + 12, y + 48, "un pied est posé sur un tour à au plus un quart de pas le long de sa normale", 0, GRIS)
    ecart = str(a["la_question"]["lecart_median_en_pas"]).replace(".", ",")
    ecrire(x0 + 12, y + 80, f"écart médian entre les points de la question et leurs pieds : {ecart} pas", 0, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 26, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_348.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "la_part": 0.9, "lissue": "x ; oui, la surface de départ y est sur son tour"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "90 % DES PIEDS LUS SUR 5753_-2 Y SONT POSÉS ; OUI, LA SURFACE DE DÉPART Y EST "
                                                         "SUR SON TOUR", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : une lecture a échoué (x)"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : UNE LECTURE A ÉCHOUÉ (X)", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    a = la_surface(d)["la_surface"]
    pts = {p[1]: p[2] for p in traces["points"] if p[0] != LES_RANGEES[2]}
    X = lambda p: LE_GAUCHE + p * (LA_DROITE - LE_GAUCHE)  # noqa: E731
    v("★★★★ la question et son contrôle sont à leur part",
      abs(pts.get("question", -1) - X(a["la_question"]["la_part_posee"])) < 0.5
      and abs(pts.get("contrôle", -1) - X(a["le_controle"]["la_part_posee"])) < 0.5, str(pts))
    v("★★★★ la question est celle de la surface bornée, graine 8, saut 4",
      a["la_question"]["la_part_posee"] == d["le_verdict"].get("la_part", a["la_question"]["la_part_posee"])
      and (la_surface(d)["la_chaine"], la_surface(d)["le_rang"], la_surface(d)["le_saut"]) == ("bornée", 8, 4))
    gris = [p for p in traces["points"] if p[0] == LES_RANGEES[2]]
    attendus = [(s["la_chaine"], s["le_rang"], s["le_saut"]) for s in d["les_surfaces"]
                if (s["la_chaine"], s["le_rang"], s["le_saut"]) != ("bornée", 8, 4) and s["la_surface"] is not None
                and s["la_surface"]["la_question"]["la_part_posee"] is not None]
    v("★★★★ un point gris par autre surface dont la question est lue, et aucun autre", sorted(p[1] for p in gris) == sorted(attendus),
      str(len(gris)))
    tours = sorted({int(t) for g in (a["la_question"], a["le_controle"]) for t in g["les_tours_des_pieds"]}, reverse=True)
    v("★★★★ le tableau porte les pieds de la question et du contrôle, tour par tour",
      [x[1:] for x in traces["lignes"]] == [[str(g["les_points"]), str(g["les_pieds_lus"])]
                                            + [str(g["les_tours_des_pieds"].get(str(t), 0)) for t in tours] + [str(g["sans_tour"])]
                                            for g in (a["la_question"], a["le_controle"])])
    parts = [s["la_surface"]["la_question"]["la_part_posee"] for s in d["les_surfaces"]
             if (s["la_chaine"], s["le_rang"], s["le_saut"]) != ("bornée", 8, 4) and s["la_surface"] is not None
             and s["la_surface"]["la_question"]["la_part_posee"] is not None]
    v("★★★★ la bande rapporte à côté les autres surfaces, recomptées",
      f"sous les {len(parts)} autres surfaces à deux tours qui sont lues, {sum(p >= 0.75 for p in parts)} ont" in " ".join(la_bande(d)))
    moins = json.loads(json.dumps(d))
    une = next(s for s in moins["les_surfaces"] if (s["la_chaine"], s["le_rang"], s["le_saut"]) != ("bornée", 8, 4)
               and s["la_surface"] is not None and (s["la_surface"]["la_question"]["la_part_posee"] or 0.0) >= 0.75)
    une["la_surface"]["la_question"]["la_part_posee"] = 0.5
    v("★★★ une autre surface sous les trois quarts n'est pas comptée parmi elles",
      f"lues, {sum(p >= 0.75 for p in parts) - 1} ont" in " ".join(la_bande(moins)), la_bande(moins)[1])
    haut, bas = traces["zone"]
    v("★★★★ chaque point est dans la zone du graphe", all(haut < r[3] and r[4] < bas for r in traces["rectangles"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t, font=f) for x, y, t, f in poses]
    sous = [r for r in traces["rectangles"] if any(bb[0] < r[2] and r[1] < bb[2] and bb[1] < r[4] and r[3] < bb[3] for bb in boites)]
    v("★★★★ aucun point ne passe sous un texte", not sous, str(sous[:3]))
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
                   / "348_la_surface_de_depart_est_elle_sur_son_tour_sous_la_surface_bornee.png")
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
