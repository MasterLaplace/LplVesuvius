"""Sur PHerc0358 : l'écart des distances à leurs nappes des deux surfaces de chaque paire « même feuille », en sauts, au même compte, à un tour et à deux tours ou plus d'écart.

⚠⚠ **Ce que cette figure doit rendre évident.** Une ligne par groupe, un point par paire lue à l'écart de ses deux distances rapporté au
saut simple médian de `369` ; le même compte en bleu, un tour en gris, deux tours ou plus en orange. Le demi-saut de la règle en trait
plein, et à droite de chaque ligne le nombre de paires lues à la même distance.

  uv run python src/figures/figure_une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.py \\
      --sortie docs/images/376_une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.png

⚠ Tout vient de la mesure de `376`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 560
LA_BANDE = 440
GAUCHE, DROITE = 230, 800
LES_LIGNES = (("même compte", "au même compte", BLEU), ("un tour", "à un tour", GRIS),
              ("deux tours ou plus", "à deux tours ou plus", ORANGE))
Y_LIGNE = {"même compte": 125, "un tour": 200, "deux tours ou plus": 275}
Y_AXE = 330
RAYON = 5
LE_PAS_VERTICAL = 7


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_moitie(d: dict) -> float:
    return d["les_constantes"]["la_moitie"]


def les_points(d: dict) -> list[tuple[str, float]]:
    """Chaque paire lue, sous son groupe, à l'écart de ses distances en sauts."""
    return [(p["le_groupe"], p["en_sauts"]) for p in d["les_paires"] if p["en_sauts"] is not None]


def la_borne(d: dict) -> int:
    """Le plus grand écart montré, au moins le demi-saut de la règle, arrondi au saut entier au-dessus."""
    return max(1, math.ceil(round(max([e for _, e in les_points(d)] + [la_moitie(d)]), 9)))


def en_x(e: float, borne: int) -> int:
    return GAUCHE + round(e / borne * (DROITE - GAUCHE))


def le_decalage(i: int) -> int:
    """Le décalage vertical du i-ème point d'une ligne, pour que les points d'un même écart ne se couvrent pas tous."""
    return ((i % 3) - 1) * LE_PAS_VERTICAL


def le_compte(d: dict, groupe: str) -> tuple[int, int]:
    """Les paires lues du groupe à la même distance, et toutes les paires lues du groupe, recomptées sur les paires."""
    ecarts = [e for g, e in les_points(d) if g == groupe]
    return sum(1 for e in ecarts if e < la_moitie(d)), len(ecarts)


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].partition(",")[0].upper()
    return f"la même distance de la nappe, sur PHerc0358 : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    pl = d["le_bilan"]["deux tours ou plus"]
    deux = (f"rapporté à côté, qui ne décide rien : à deux tours ou plus, {pl['meme_distance']} des {pl['lues']} à la même distance, "
            f"{pl['meme_sens']} dans le sens des comptes, {pl['compte_les_tours']} dont l'écart arrondi en sauts vaut celui des comptes")
    trois = "⚠ ce qui n'est PAS établi : si les nappes de la graine 8 sont sur des feuilles différentes, ni laquelle des chaînes compte mal."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 410)]
    traces = {"points": [], "seuils": [], "boites": [], "comptes": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "écart des distances à leurs nappes des deux surfaces de chaque paire « même feuille », en sauts simples médians de 369",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    borne = la_borne(d)
    art.line([GAUCHE, Y_AXE, DROITE, Y_AXE], fill=GRIS, width=1)
    for k in range(0, borne + 1):
        x = en_x(k, borne)
        art.line([x, Y_AXE, x, Y_AXE + 4], fill=GRIS)
        ecrire(x - 4, Y_AXE + 8, str(k), petit, GRIS)
    ecrire(GAUCHE, Y_AXE + 28, "écart des distances, en sauts", petit, GRIS)
    couleurs = {cle: c for cle, _, c in LES_LIGNES}
    for cle, nom, _ in LES_LIGNES:
        y = Y_LIGNE[cle]
        art.line([GAUCHE, y, DROITE, y], fill=TRAIT)
        ecrire(x0 + 16, y - 8, nom, moyen, ENCRE)
        meme, lues = le_compte(d, cle)
        ecrire(DROITE + 30, y - 8, f"{meme} / {lues} à la même distance", moyen, ENCRE)
        traces["comptes"].append((cle, meme, lues))
    rangs = {cle: 0 for cle in Y_LIGNE}
    for cle, e in sorted(les_points(d), key=lambda p: (p[0], p[1])):
        x, y = en_x(e, borne), Y_LIGNE[cle] + le_decalage(rangs[cle])
        rangs[cle] += 1
        art.ellipse([x - RAYON, y - RAYON, x + RAYON, y + RAYON], fill=couleurs[cle])
        traces["points"].append((cle, e, x, couleurs[cle]))
        traces["boites"].append((x - RAYON, x + RAYON, y - RAYON, y + RAYON))
    xm = en_x(la_moitie(d), borne)
    art.line([xm, Y_LIGNE["même compte"] - 25, xm, Y_LIGNE["deux tours ou plus"] + 25], fill=ENCRE, width=2)
    traces["seuils"].append(("la moitié", la_moitie(d), xm))
    ecrire(xm + 6, y0 + 8, "un demi-saut : à la même distance en deçà", petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_376.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA MÊME DISTANCE DE LA NAPPE, SUR PHERC0358 : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : 3 des 4 paires, le contrôle échoue"}
    v("★★★ un titre indécidable LIT son issue, jusqu'à la première virgule", le_titre(autre) == "INDÉCIDABLE : 3 DES 4 PAIRES",
      le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendus = sorted((p["le_groupe"], p["en_sauts"]) for p in d["les_paires"] if p["en_sauts"] is not None)
    v("★★★★ un point par paire lue sous son groupe, recomptés sur la mesure",
      sorted((c, e) for c, e, _, _ in traces["points"]) == attendus, str(len(traces["points"])))
    v("★★★★ le même compte en bleu, un tour en gris, deux tours ou plus en orange",
      all(f == {"même compte": (58, 88, 120), "un tour": (140, 143, 148), "deux tours ou plus": (214, 150, 76)}[c]
          for c, _, _, f in traces["points"]))
    v("★★★★ les lignes de haut en bas : même compte, un tour, deux tours ou plus",
      Y_LIGNE["même compte"] < Y_LIGNE["un tour"] < Y_LIGNE["deux tours ou plus"]
      and [c for c, _, _ in traces["comptes"]] == ["même compte", "un tour", "deux tours ou plus"])
    borne = la_borne(d)
    v("★★★★ chaque point à son écart, l'axe allant de 0 au saut entier au-dessus du plus grand",
      all(x == GAUCHE + round(e / borne * (DROITE - GAUCHE)) for _, e, x, _ in traces["points"])
      and borne >= max(e for _, e, _, _ in traces["points"]) and borne - 1 < max(e for _, e, _, _ in traces["points"]), str(borne))
    bas = json.loads(json.dumps(d))
    for p in bas["les_paires"]:
        p["en_sauts"] = 0.1 if p["en_sauts"] is not None else None
    bas["les_constantes"]["la_moitie"] = 1.5
    v("★★★ l'axe va au moins jusqu'au seuil de la règle, même au-delà de tous les écarts", la_borne(bas) == 2, str(la_borne(bas)))
    haut = json.loads(json.dumps(d))
    haut["les_paires"][0]["en_sauts"] = 6.2
    pile = json.loads(json.dumps(d))
    pile["les_paires"][0]["en_sauts"] = 6.0
    v("★★★ l'axe arrondit le plus grand écart au saut entier au-dessus, et s'arrête sur un entier atteint",
      la_borne(haut) == 7 and la_borne(pile) == 6, f"{la_borne(haut)} {la_borne(pile)}")
    trou = json.loads(json.dumps(d))
    trou["les_paires"][0]["en_sauts"] = None
    v("★★★ une paire non lue n'est pas montrée", lambda: len(dessiner(trou, tmp)[3]["points"]) == len(traces["points"]) - 1)
    faux = json.loads(json.dumps(d))
    faux["le_bilan"]["deux tours ou plus"].update({"lues": 27, "meme_sens": 3, "compte_les_tours": 2, "meme_distance": 1})
    v("★★★ la bande lit chaque nombre du bilan à sa place",
      "1 des 27 à la même distance, 3 dans le sens des comptes, 2 dont l'écart" in la_bande(faux)[1], la_bande(faux)[1])
    v("★★★★ le demi-saut de la règle tracé à sa valeur", traces["seuils"] == [("la moitié", 0.5, en_x(0.5, borne))], str(traces["seuils"]))
    recomptes = []
    for g in ("même compte", "un tour", "deux tours ou plus"):
        ps = [p for p in d["les_paires"] if p["le_groupe"] == g and p["en_sauts"] is not None]
        recomptes.append((g, sum(1 for p in ps if abs(p["lecart_de_distance"]) < 0.5 * d["les_constantes"]["le_saut"]), len(ps)))
    v("★★★★ les paires à la même distance, recomptées au demi-saut sur les distances, et égales au bilan", traces["comptes"] == recomptes
      and all(d["le_bilan"][g]["meme_distance"] == m and d["le_bilan"][g]["lues"] == n for g, m, n in recomptes), str(recomptes))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["boites"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    ps = [p for p in d["les_paires"] if p["le_groupe"] == "deux tours ou plus" and p["en_sauts"] is not None]
    v("★★★★ la bande rapporte, recomptés sur les paires, le sens et le compte des tours à deux tours ou plus",
      f"{sum(p['meme_sens'] is True for p in ps)} dans le sens des comptes, {sum(p['compte_les_tours'] for p in ps)} dont l'écart"
      in la_bande(d)[1] and f"{sum(p['meme_distance'] for p in ps)} des {len(ps)} à la même distance" in la_bande(d)[1])
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
                   / "376_une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.png")
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
