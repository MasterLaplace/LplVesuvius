"""Sur PHerc0358 : la part lointaine de chaque paire « même feuille », au même compte, à un tour et à deux tours ou plus d'écart.

⚠⚠ **Ce que cette figure doit rendre évident.** Une ligne par groupe, un point par paire à la part de ses points en face à plus d'un
demi-pas ; le même compte en bleu, un tour en gris, deux tours ou plus en orange. Le quart de la règle en trait plein, et à droite de
chaque ligne le nombre de paires qui touchent.

  uv run python src/figures/figure_les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.py \\
      --sortie docs/images/375_les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.png

⚠ Tout vient de la mesure de `375`.
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
LA_MESURE = (RACINE / "docs" / "mesures"
             / "les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.json")

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
GAUCHE, DROITE = 230, 860
LES_LIGNES = (("même compte", "au même compte", BLEU), ("un tour", "à un tour", GRIS),
              ("deux tours ou plus", "à deux tours ou plus", ORANGE))
Y_LIGNE = {"même compte": 125, "un tour": 200, "deux tours ou plus": 275}
Y_AXE = 330
RAYON = 5
LE_PAS_VERTICAL = 7


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_quart(d: dict) -> float:
    return d["les_constantes"]["le_quart_de_points"]


def les_points(d: dict) -> list[tuple[str, float]]:
    """Chaque paire, sous son groupe, à sa part lointaine."""
    return [(p["le_groupe"], p["la_part_lointaine"]) for p in d["les_paires"]]


def la_borne(d: dict) -> float:
    """La part la plus grande montrée, au moins le quart de la règle, arrondie au dixième au-dessus."""
    haut = max([e for _, e in les_points(d)] + [le_quart(d)])
    return math.ceil(round(haut * 10.0, 9)) / 10.0


def en_x(e: float, borne: float) -> int:
    return GAUCHE + round(e / borne * (DROITE - GAUCHE))


def le_decalage(i: int) -> int:
    """Le décalage vertical du i-ème point d'une ligne, pour que les points d'une même part ne se couvrent pas tous."""
    return ((i % 3) - 1) * LE_PAS_VERTICAL


def le_compte(d: dict, groupe: str) -> tuple[int, int]:
    """Les paires du groupe qui touchent, et toutes celles du groupe, recomptées sur les paires."""
    parts = [e for g, e in les_points(d) if g == groupe]
    return sum(1 for e in parts if e >= le_quart(d)), len(parts)


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"deux feuilles qui se touchent, sur PHerc0358 : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    b = d["le_bilan"]
    deux = ("rapporté à côté, qui ne décide rien : part lointaine médiane "
            f"{b['même compte']['la_part_lointaine_mediane']:g} au même compte, {b['un tour']['la_part_lointaine_mediane']:g} à un tour, "
            f"{b['deux tours ou plus']['la_part_lointaine_mediane']:g} à deux tours ou plus").replace(".", ",")
    trois = "⚠ ce qui n'est PAS établi : pourquoi les comptes de la graine 8 s'écartent, ni laquelle des chaînes compte mal."
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
    ecrire(50, 46, "part des points en face à plus d'un demi-pas, pour chaque paire « même feuille », par écart de comptes corrigés",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    borne = la_borne(d)
    art.line([GAUCHE, Y_AXE, DROITE, Y_AXE], fill=GRIS, width=1)
    for k in range(0, round(borne * 10) + 1):
        x = en_x(k / 10.0, borne)
        art.line([x, Y_AXE, x, Y_AXE + 4], fill=GRIS)
        ecrire(x - 8, Y_AXE + 8, f"{k / 10.0:g}".replace(".", ","), petit, GRIS)
    ecrire(GAUCHE, Y_AXE + 28, "part lointaine des points en face", petit, GRIS)
    couleurs = {cle: c for cle, _, c in LES_LIGNES}
    for cle, nom, _ in LES_LIGNES:
        y = Y_LIGNE[cle]
        art.line([GAUCHE, y, DROITE, y], fill=TRAIT)
        ecrire(x0 + 16, y - 8, nom, moyen, ENCRE)
        touchent, toutes = le_compte(d, cle)
        ecrire(DROITE + 30, y - 8, f"{touchent} / {toutes} touchent", moyen, ENCRE)
        traces["comptes"].append((cle, touchent, toutes))
    rangs = {cle: 0 for cle in Y_LIGNE}
    for cle, e in sorted(les_points(d), key=lambda p: (p[0], p[1])):
        x, y = en_x(e, borne), Y_LIGNE[cle] + le_decalage(rangs[cle])
        rangs[cle] += 1
        art.ellipse([x - RAYON, y - RAYON, x + RAYON, y + RAYON], fill=couleurs[cle])
        traces["points"].append((cle, e, x, couleurs[cle]))
        traces["boites"].append((x - RAYON, x + RAYON, y - RAYON, y + RAYON))
    xq = en_x(le_quart(d), borne)
    art.line([xq, Y_LIGNE["même compte"] - 25, xq, Y_LIGNE["deux tours ou plus"] + 25], fill=ENCRE, width=2)
    traces["seuils"].append(("le quart", le_quart(d), xq))
    ecrire(xq + 6, y0 + 8, "un quart des points : la paire touche", petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_375.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "DEUX FEUILLES QUI SE TOUCHENT, SUR PHERC0358 : OUI", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendus = sorted((p["le_groupe"], p["la_part_lointaine"]) for p in d["les_paires"])
    v("★★★★ un point par paire sous son groupe, recomptés sur la mesure",
      sorted((c, e) for c, e, _, _ in traces["points"]) == attendus, str(len(traces["points"])))
    v("★★★★ le même compte en bleu, un tour en gris, deux tours ou plus en orange",
      all(f == {"même compte": (58, 88, 120), "un tour": (140, 143, 148), "deux tours ou plus": (214, 150, 76)}[c]
          for c, _, _, f in traces["points"]))
    v("★★★★ les lignes de haut en bas : même compte, un tour, deux tours ou plus",
      Y_LIGNE["même compte"] < Y_LIGNE["un tour"] < Y_LIGNE["deux tours ou plus"]
      and [c for c, _, _ in traces["comptes"]] == ["même compte", "un tour", "deux tours ou plus"])
    borne = la_borne(d)
    v("★★★★ chaque point à sa part, l'axe allant de 0 au dixième au-dessus de la plus grande",
      all(x == GAUCHE + round(e / borne * (DROITE - GAUCHE)) for _, e, x, _ in traces["points"])
      and borne >= max(e for _, e, _, _ in traces["points"]) and borne - 0.1 < max(e for _, e, _, _ in traces["points"]) + 1e-9,
      str(borne))
    bas = json.loads(json.dumps(d))
    for p in bas["les_paires"]:
        p["la_part_lointaine"] = 0.05
    v("★★★ l'axe va au moins jusqu'au quart de la règle, même au-delà de toutes les parts", la_borne(bas) == 0.3, str(la_borne(bas)))
    haut = json.loads(json.dumps(d))
    haut["les_paires"][0]["la_part_lointaine"] = 0.61
    v("★★★ l'axe arrondit la plus grande part au dixième au-dessus", la_borne(haut) == 0.7, str(la_borne(haut)))
    v("★★★★ le quart de la règle tracé à sa valeur", traces["seuils"] == [("le quart", 0.25, en_x(0.25, borne))], str(traces["seuils"]))
    recomptes = []
    for g in ("même compte", "un tour", "deux tours ou plus"):
        ps = [p["la_part_lointaine"] for p in d["les_paires"] if p["le_groupe"] == g]
        recomptes.append((g, sum(1 for e in ps if e >= 0.25), len(ps)))
    v("★★★★ les paires qui touchent, recomptées au quart sur les paires, et égales au bilan", traces["comptes"] == recomptes
      and all(d["le_bilan"][g]["touchent"] == t and d["le_bilan"][g]["les_paires"] == n for g, t, n in recomptes), str(recomptes))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["boites"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    b = d["le_bilan"]
    v("★★★★ la bande rapporte les parts médianes du bilan",
      f"{b['deux tours ou plus']['la_part_lointaine_mediane']:g} à deux tours ou plus".replace(".", ",") in la_bande(d)[1]
      and f"{b['même compte']['la_part_lointaine_mediane']:g} au même compte".replace(".", ",") in la_bande(d)[1]
      and f", {b['un tour']['la_part_lointaine_mediane']:g} à un tour,".replace(".", ",") in la_bande(d)[1])
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
                   / "375_les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.png")
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
