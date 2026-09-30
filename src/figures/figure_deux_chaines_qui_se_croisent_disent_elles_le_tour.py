"""Sur PHercParis4, graines 4 à 8 : pour chaque paire de surfaces de deux chaînes d'une maille qui se recouvrent, l'écart médian entre elles, selon qu'elles sont sur le même tour publié ou sur des tours voisins.

⚠⚠ **Ce que cette figure doit rendre évident.** Un point par paire, en voxels du niveau 2 : les paires sur le même tour en bleu, sur des
tours voisins en orange, et un trait au quart de pas qui décide « même feuille ». Si les couleurs sont de part et d'autre du trait, l'accord
de deux chaînes dit le tour.

  uv run python src/figures/figure_deux_chaines_qui_se_croisent_disent_elles_le_tour.py \\
      --sortie docs/images/367_deux_chaines_qui_se_croisent_disent_elles_le_tour.png

⚠ Tout vient de la mesure de `367`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "deux_chaines_qui_se_croisent_disent_elles_le_tour.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 110, 400
LE_PLAFOND = 16.0
RAYON = 4


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return f"{b['daccord']} paires sur {b['les_paires']} : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    e = d["le_bilan"]["lecart_median"]
    deux = (f"rapporté à côté, qui ne décide rien : écart médian {e['meme_tour']:g} voxel sur le même tour, {e['tours_voisins']:g} sur des "
            f"tours voisins ; les chaînes posent leurs points sur les plages de m7").replace(".", ",")
    trois = "⚠ ce qui n'est PAS établi : que « même feuille de m7 » veuille dire « même tour » ailleurs qu'ici, ni sur PHerc0358."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"points": [], "seuil": None}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "un point par paire de surfaces de deux graines qui se recouvrent : leur écart médian, en voxels du niveau 2", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    gx0, gx1 = x0 + 70, x1 - 30

    def y_de(e):
        return BAS - round(min(e, LE_PLAFOND) / LE_PLAFOND * (BAS - HAUT))
    for e in (0, 4, 8, 12, 16):
        art.line([gx0 - 5, y_de(e), gx0, y_de(e)], fill=GRIS)
        ecrire(gx0 - 30, y_de(e) - 7, f"{e}", petit, GRIS)
    art.line([gx0, HAUT, gx0, BAS], fill=GRIS)
    seuil = d["les_constantes"]["le_quart"]
    ys = y_de(seuil)
    art.line([gx0, ys, gx1, ys], fill=ALERTE, width=1)
    traces["seuil"] = ys
    ecrire(gx1 - 175, ys - 16, f"un quart de pas : {seuil:g}".replace(".", ","), petit, ALERTE)
    paires = sorted(d["les_paires"], key=lambda p: (not p["meme_tour"], p["lecart_median"]))
    pas = (gx1 - gx0 - 20) / max(1, len(paires))
    for i, p in enumerate(paires):
        x = round(gx0 + 10 + i * pas)
        y = y_de(p["lecart_median"])
        couleur = BLEU if p["meme_tour"] else ORANGE
        art.ellipse([x - RAYON, y - RAYON, x + RAYON, y + RAYON], fill=couleur)
        traces["points"].append((p["a"], p["b"], p["lecart_median"], p["meme_tour"], x, y, couleur))
    for i, (nom, couleur) in enumerate((("même tour publié", BLEU), ("tours publiés voisins", ORANGE))):
        lx = x0 + 110 + i * 200
        art.ellipse([lx, y0 + 12, lx + 10, y0 + 22], fill=couleur)
        ecrire(lx + 16, y0 + 9, nom, petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_367.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"daccord": 30, "les_paires": 40})
    autre["le_verdict"]["lissue"] = "x ; en partie"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "30 PAIRES SUR 40 : EN PARTIE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ un point par paire", len(traces["points"]) == len(d["les_paires"]) == d["le_bilan"]["les_paires"])
    v("★★★★ le même tour en bleu, les tours voisins en orange",
      all(f == (BLEU if mt else ORANGE) for _, _, _, mt, _, _, f in traces["points"]))
    v("★★★★ la hauteur de chaque point est son écart, plafonné",
      all(y == BAS - round(min(e, LE_PLAFOND) / LE_PLAFOND * (BAS - HAUT)) for _, _, e, _, _, y, _ in traces["points"]))
    grand = json.loads(json.dumps(d))
    grand["les_paires"][0]["lecart_median"] = 3 * LE_PLAFOND
    tmp2 = tmp.with_name(".sonde_367_grand.png")
    _, _, _, t2 = dessiner(grand, tmp2)
    tmp2.unlink(missing_ok=True)
    v("★★★★ un écart au-delà du plafond reste en haut du cadre", [y for _, _, e, _, _, y, _ in t2["points"] if e == 3 * LE_PLAFOND] == [HAUT])
    v("★★★★ le trait est au quart de pas de la mesure",
      traces["seuil"] == BAS - round(d["les_constantes"]["le_quart"] / LE_PLAFOND * (BAS - HAUT)))
    b = d["le_bilan"]
    sous = sum(1 for _, _, e, mt, _, _, _ in traces["points"] if e <= d["les_constantes"]["le_quart"])
    v("★★★★ les points sous le trait sont les paires « même feuille » du bilan",
      sous == b["la_table"]["meme_meme"] + b["la_table"]["voisin_meme"], str(sous))
    x0, y0, x1, y1 = cadres[0]
    v("★★★★ rien ne sort de son cadre", all(x0 < x - RAYON and x + RAYON < x1 and y0 < y - RAYON and y + RAYON < y1
                                            for _, _, _, _, x, y, _ in traces["points"]))
    v("★★★★ la bande rapporte les écarts médians du bilan",
      f"écart médian {b['lecart_median']['meme_tour']:g} voxel".replace(".", ",") in la_bande(d)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for _, _, t, _ in poses))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "367_deux_chaines_qui_se_croisent_disent_elles_le_tour.png")
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
