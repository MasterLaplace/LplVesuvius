"""Sur PHercParis4 : l'écart entre deux surfaces justes d'une même chaîne, à un, deux ou trois tours publiés l'une de l'autre, et celui des sauts faux.

⚠⚠ **Ce que cette figure doit rendre évident.** Une ligne par nombre de tours, un point par paire à son écart ; les paires à un tour en
bleu, à deux tours en orange, à trois tours en gris, les sauts faux en rouge. Le seuil de la règle en trait plein s'il existe, le pas et
demi de `369` en trait gris.

  uv run python src/figures/figure_lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.py \\
      --sortie docs/images/370_lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.png

⚠ Tout vient de la mesure de `370`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
ROUGE = (170, 50, 50)
L_, H_ = 1100, 590
LA_BANDE = 470
GAUCHE, DROITE = 200, 1020
LES_LIGNES = ((1, "à un tour", BLEU), (2, "à deux tours", ORANGE), (3, "à trois tours", GRIS), ("faux", "sauts faux", ROUGE))
Y_LIGNE = {1: 120, 2: 185, 3: 250, "faux": 315}
Y_AXE = 360
RAYON = 5


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_points(d: dict) -> list[tuple[object, float]]:
    """Chaque paire, sous son nombre de tours, et chaque saut faux, à son écart ; ceux sans écart ne sont pas montrés."""
    out = [(p["les_tours"], p["lecart_median"]) for p in d["les_paires"]]
    out += [("faux", s["lecart_median"]) for s in d["les_sauts_faux"] if s["lecart_median"] is not None]
    return out


def la_borne(d: dict) -> int:
    """L'écart le plus grand montré, arrondi à la dizaine au-dessus, au moins le pas et demi de `369`."""
    haut = max([e for _, e in les_points(d)] + [d["les_seuils_de_369"]["le_double"]])
    return int(math.ceil(haut / 10.0) * 10)


def en_x(e: float, borne: int) -> int:
    return GAUCHE + round(e / borne * (DROITE - GAUCHE))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"un tour ou deux, sur PHercParis4 : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    s = d["les_seuils_de_369"]
    deux = (f"rapporté à côté, qui ne décide rien : au pas et demi de 369, {s['le_double']:g} voxels, {s['un_tour_dits_doubles']} paires à "
            f"un tour seraient dites doubles et {s['deux_tours_pas_dits_doubles']} à deux tours ne le seraient pas").replace(".", ",")
    trois = "⚠ ce qui n'est PAS établi : si un vrai saut double garde la surface d'une chaîne juste, ni ce que vaut le seuil sur PHerc0358."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"points": [], "seuils": [], "boites": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "écart de deux surfaces justes d'une même chaîne, par nombre de tours publiés entre elles, et des sauts faux (voxels)",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    borne = la_borne(d)
    art.line([GAUCHE, Y_AXE, DROITE, Y_AXE], fill=GRIS, width=1)
    for k in range(0, borne + 1, 10):
        x = en_x(k, borne)
        art.line([x, Y_AXE, x, Y_AXE + 4], fill=GRIS)
        ecrire(x - 6, Y_AXE + 8, str(k), petit, GRIS)
    ecrire(GAUCHE, Y_AXE + 28, "écart en voxels de PHercParis4", petit, GRIS)
    couleurs = {cle: c for cle, _, c in LES_LIGNES}
    for cle, nom, couleur in LES_LIGNES:
        y = Y_LIGNE[cle]
        art.line([GAUCHE, y, DROITE, y], fill=TRAIT)
        ecrire(x0 + 16, y - 8, nom, moyen, ENCRE)
    for cle, e in les_points(d):
        x, y = en_x(e, borne), Y_LIGNE[cle]
        art.ellipse([x - RAYON, y - RAYON, x + RAYON, y + RAYON], fill=couleurs[cle])
        traces["points"].append((cle, e, x, couleurs[cle]))
        traces["boites"].append((x - RAYON, x + RAYON, y - RAYON, y + RAYON))
    double = d["les_seuils_de_369"]["le_double"]
    xd = en_x(double, borne)
    for y in range(Y_LIGNE[1] - 20, Y_LIGNE["faux"] + 20, 8):
        art.line([xd, y, xd, y + 4], fill=GRIS)
    traces["seuils"].append(("369", double, xd))
    ecrire(xd + 6, y0 + 8, "pas et demi de 369", petit, GRIS)
    b = d["le_bilan"]
    if b["separe"] and b["le_seuil"] is not None:
        xs = en_x(b["le_seuil"], borne)
        art.line([xs, Y_LIGNE[1] - 20, xs, Y_LIGNE["faux"] + 20], fill=ENCRE, width=2)
        traces["seuils"].append(("la règle", b["le_seuil"], xs))
        ecrire(xs - 100, y0 + 8, "seuil de la règle", petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 54, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_370.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "UN TOUR OU DEUX, SUR PHERCPARIS4 : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendus = sorted([(p["les_tours"], p["lecart_median"]) for p in d["les_paires"]]
                      + [("faux", s["lecart_median"]) for s in d["les_sauts_faux"] if s["lecart_median"] is not None], key=str)
    v("★★★★ un point par paire sous son nombre de tours et par saut faux lisible, recomptés sur la mesure",
      sorted([(c, e) for c, e, _, _ in traces["points"]], key=str) == attendus, str(len(traces["points"])))
    v("★★★★ à un tour en bleu, à deux en orange, à trois en gris, les sauts faux en rouge",
      all(f == {1: BLEU, 2: ORANGE, 3: GRIS, "faux": ROUGE}[c] for c, _, _, f in traces["points"]))
    borne = la_borne(d)
    v("★★★★ chaque point à son écart, l'axe allant de 0 à la dizaine au-dessus du plus grand",
      all(x == GAUCHE + round(e / borne * (DROITE - GAUCHE)) for _, e, x, _ in traces["points"])
      and borne >= max(e for _, e, _, _ in traces["points"]) and borne - 10 < max(max(e for _, e, _, _ in traces["points"]),
                                                                                 d["les_seuils_de_369"]["le_double"]), str(borne))
    b = d["le_bilan"]
    regle = [s for s in traces["seuils"] if s[0] == "la règle"]
    v("★★★★ le seuil de la règle tracé à sa valeur s'il sépare, et seulement alors",
      (regle == [("la règle", b["le_seuil"], en_x(b["le_seuil"], borne))]) if b["separe"] else not regle, str(regle))
    haut = json.loads(json.dumps(d))
    haut["les_seuils_de_369"]["le_double"] = 55.0
    v("★★★ l'axe va au moins jusqu'au pas et demi de 369, même au-delà de tous les points", la_borne(haut) == 60, str(la_borne(haut)))
    sans = json.loads(json.dumps(d))
    sans["le_bilan"]["separe"] = False
    v("★★★★ sans séparation, aucun seuil de la règle n'est tracé",
      lambda: not [s_ for s_ in dessiner(sans, tmp)[3]["seuils"] if s_[0] == "la règle"])
    v("★★★★ le pas et demi de 369 tracé à sa valeur", ("369", d["les_seuils_de_369"]["le_double"],
                                                      en_x(d["les_seuils_de_369"]["le_double"], borne)) in traces["seuils"])
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["boites"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    s = d["les_seuils_de_369"]
    v("★★★★ la bande rapporte les seuils de 369", f"{s['un_tour_dits_doubles']} paires à un tour seraient dites doubles et "
                                                  f"{s['deux_tours_pas_dits_doubles']} à deux tours" in la_bande(d)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    dessiner(d, tmp)
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
                   / "370_lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.png")
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
