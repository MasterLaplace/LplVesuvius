"""Sur PHerc0358 : graine par graine, l'écart médian des nappes de départ des trois chaînes, deux à deux, et la part de leurs points au loin.

⚠⚠ **Ce que cette figure doit rendre évident.** Par graine, trois barres, une par couple de nappes, à la hauteur de leur écart médian : la
suivie et la compagne en bleu, la suivie et la tierce en orange, la compagne et la tierce en gris ; le quart de pas du juge de feuille en
trait plein ; au-dessus de chaque barre, la part des points à plus d'un demi-pas.

  uv run python src/figures/figure_les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.py \\
      --sortie docs/images/377_les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.png

⚠ Tout vient de la mesure de `377`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.json"

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
HAUT, BAS = 120, 350
LARGEUR = 44
LES_COUPLES = (("suivie|compagne", "la suivie et la compagne", BLEU), ("suivie|tierce", "la suivie et la tierce", ORANGE),
               ("compagne|tierce", "la compagne et la tierce", GRIS))
X_GRAINE = {6: 240, 7: 520, 8: 800}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_graines(d: dict) -> dict:
    """Les couples de nappes de chaque graine, lus sur son premier côté : les deux côtés d'une graine partent des mêmes nappes."""
    out = {}
    for c in d["les_cotes"]:
        out.setdefault(c["le_rang"], c["les_couples"])
    return out


def la_borne(d: dict) -> int:
    """Le plus grand écart médian montré, au moins le quart de pas, arrondi aux deux voxels au-dessus."""
    ecarts = [v["lecart_median"] for cs in les_graines(d).values() for v in cs.values() if v["lecart_median"] is not None]
    return 2 * math.ceil(max(ecarts + [d["les_constantes"]["le_quart"]]) / 2.0)


def en_y(e: float, borne: int) -> int:
    return BAS - round(e / borne * (BAS - HAUT))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].partition(",")[0].upper()
    return f"les nappes de la graine 8 sur des feuilles différentes : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    g8 = les_graines(d)[8]
    ct = g8["compagne|tierce"]
    deux = (f"rapporté à côté, qui ne décide rien : sur la graine 8, la compagne et la tierce sont sur la même feuille par la médiane, "
            f"{ct['lecart_median']:g} voxel, mais {round(100 * ct['la_part_lointaine'])} % de leurs points sont au loin").replace(".", ",")
    trois = "⚠ ce qui n'est PAS établi : où la nappe de la tierce passe d'une feuille à l'autre, ni si les surfaces des chaînes sont à cheval."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 410)]
    traces = {"barres": [], "seuils": [], "parts": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "écart médian des nappes de départ des trois chaînes, deux à deux, en voxels, et au-dessus la part des points au loin",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    borne = la_borne(d)
    art.line([140, BAS, 960, BAS], fill=GRIS)
    for k in range(0, borne + 1, 2):
        y = en_y(k, borne)
        art.line([136, y, 140, y], fill=GRIS)
        ecrire(112, y - 7, str(k), petit, GRIS)
    for i, (cle, nom, couleur) in enumerate(LES_COUPLES):
        art.rectangle([880, 150 + 30 * i, 894, 164 + 30 * i], fill=couleur)
        ecrire(902, 150 + 30 * i, nom, petit, ENCRE)
    for rang, couples in sorted(les_graines(d).items()):
        xg = X_GRAINE[rang]
        ecrire(xg - 25, BAS + 12, f"graine {rang}", moyen, ENCRE)
        for i, (cle, _, couleur) in enumerate(LES_COUPLES):
            v = couples[cle]
            if v["lecart_median"] is None:
                continue
            xa = xg - 70 + i * (LARGEUR + 4)
            y = en_y(v["lecart_median"], borne)
            art.rectangle([xa, y, xa + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((rang, cle, v["lecart_median"], y, couleur))
            part = f"{round(100 * v['la_part_lointaine'])} %"
            ecrire(xa + 4, y - 18, part, petit, ENCRE)
            traces["parts"].append((rang, cle, part))
    q = d["les_constantes"]["le_quart"]
    yq = en_y(q, borne)
    art.line([140, yq, 860, yq], fill=ENCRE, width=2)
    traces["seuils"].append(("le quart", q, yq))
    ecrire(146, yq - 18, "quart de pas : au-delà, feuilles différentes", petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_377.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LES NAPPES DE LA GRAINE 8 SUR DES FEUILLES DIFFÉRENTES : OUI", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : 1 des 6 couples, le contrôle échoue"}
    v("★★★ un titre indécidable LIT son issue, jusqu'à la première virgule", le_titre(autre) == "INDÉCIDABLE : 1 DES 6 COUPLES",
      le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    premiers = {}
    for c in d["les_cotes"]:
        if c["le_rang"] not in premiers:
            premiers[c["le_rang"]] = c["les_couples"]
    attendus = sorted((r, k, x["lecart_median"]) for r, cs in premiers.items() for k, x in cs.items() if x["lecart_median"] is not None)
    v("★★★★ une barre par couple lu de chaque graine, à son écart médian, recomptées sur le premier côté de chaque graine",
      sorted((r, k, e) for r, k, e, _, _ in traces["barres"]) == attendus and len(attendus) == 9, str(len(traces["barres"])))
    v("★★★★ la suivie et la compagne en bleu, la suivie et la tierce en orange, la compagne et la tierce en gris",
      all(f == {"suivie|compagne": (58, 88, 120), "suivie|tierce": (214, 150, 76), "compagne|tierce": (140, 143, 148)}[k]
          for _, k, _, _, f in traces["barres"]))
    borne = la_borne(d)
    v("★★★★ chaque barre à sa hauteur, l'axe allant de 0 aux deux voxels au-dessus du plus grand écart",
      all(y == BAS - round(e / borne * (BAS - HAUT)) for _, _, e, y, _ in traces["barres"])
      and borne >= max(e for _, _, e, _, _ in traces["barres"]) and borne - 2 < max(e for _, _, e, _, _ in traces["barres"]), str(borne))
    bas = json.loads(json.dumps(d))
    for c in bas["les_cotes"]:
        for x in c["les_couples"].values():
            x["lecart_median"] = 0.3
    v("★★★ l'axe va au moins jusqu'au quart de pas, même au-delà de tous les écarts", la_borne(bas) == 6, str(la_borne(bas)))
    v("★★★★ le quart de pas tracé à sa valeur", traces["seuils"] == [("le quart", 5.0, en_y(5.0, borne))], str(traces["seuils"]))
    v("★★★★ au-dessus de chaque barre, la part des points au loin, en pour cent arrondi",
      sorted(traces["parts"]) == sorted((r, k, f"{round(100 * x['la_part_lointaine'])} %") for r, cs in premiers.items()
                                        for k, x in cs.items() if x["lecart_median"] is not None))
    v("★★★ les graines de gauche à droite : 6, 7, 8", X_GRAINE[6] < X_GRAINE[7] < X_GRAINE[8]
      and [r for r, _, _, _, _ in traces["barres"]][::3] == [6, 7, 8])
    second = json.loads(json.dumps(d))
    dernier = [c for c in second["les_cotes"] if c["le_rang"] == 8][-1]
    dernier["les_couples"]["suivie|tierce"].update({"lecart_median": 3.0, "la_part_lointaine": 0.4462})
    premier = next(c for c in second["les_cotes"] if c["le_rang"] == 8)
    premier["les_couples"]["compagne|tierce"]["la_part_lointaine"] = 0.4462
    v("★★★ chaque graine lue sur son premier côté, et les parts arrondies au pour cent le plus proche",
      lambda: (8, "suivie|tierce", premiers[8]["suivie|tierce"]["lecart_median"])
      in [(r, k, e) for r, k, e, _, _ in dessiner(second, tmp)[3]["barres"]]
      and (8, "compagne|tierce", "45 %") in dessiner(second, tmp)[3]["parts"])
    trou = json.loads(json.dumps(d))
    trou["les_cotes"][0]["les_couples"]["suivie|tierce"]["lecart_median"] = None
    v("★★★ un couple non lu n'a pas de barre", lambda: len(dessiner(trou, tmp)[3]["barres"]) == len(traces["barres"]) - 1)
    ct = premiers[8]["compagne|tierce"]
    v("★★★★ la bande rapporte la compagne et la tierce de la graine 8, à leur médiane et à leur part lointaine",
      f"{ct['lecart_median']:g} voxel, mais {round(100 * ct['la_part_lointaine'])} % de leurs points".replace(".", ",") in la_bande(d)[1])
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
                   / "377_les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.png")
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
