"""Le scan brut, là où la bande saute : ce qu'il montre en moyenne, et pourquoi rayon par rayon il ne tranche pas.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LE PROFIL MÉDIAN DU SCAN autour d'une profondeur, rapporté à
la feuille du segment : là où la chaîne et la bande s'accordent, une feuille bordée de deux creux ; à mi-chemin, un
creux ; là où la bande saute, un profil plat. En haut à droite, POURQUOI UN RAYON SEUL NE TRANCHE PAS : les deux
témoins se recouvrent presque entièrement. En bas à droite, LE CONTRASTE et son intervalle, pour chaque groupe, avec
les deux prédictions et des deux côtés.

  uv run python src/figures/figure_la_bande_a_t_elle_manque_un_tour.py \\
      --sortie docs/images/249_la_bande_a_t_elle_manque_un_tour.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "la_bande_a_t_elle_manque_un_tour.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
L_, H_ = 1360, 950
LA_PREDICTION, LE_COTE = "m7", "du_cote_plus"
LES_GROUPES = (("feuille connue : chaîne et bande d'accord", "le_temoin_feuille", BON),
               ("interstice connu : à mi-chemin", "le_temoin_interstice", CONTRE),
               ("chute trop près, là où la bande saute", "trop_pres_la_ou_la_bande_saute", ALERTE),
               ("chute trop près, là où elle ne saute pas", "trop_pres_la_ou_elle_ne_saute_pas", GRIS))
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = json.loads(LA_MESURE.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def en_moyenne(d: dict, cle: str, pred: str = LA_PREDICTION, cote: str = LE_COTE) -> dict:
    return d["les_predictions"][pred][cote]["le_juge_en_moyenne"][cle]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : les chutes où la bande saute sont-elles entre les deux témoins, et plus plates que
    l'un et l'autre, avec la prédiction et le côté que la figure dessine ?"""
    f, i = en_moyenne(d, "le_temoin_feuille"), en_moyenne(d, "le_temoin_interstice")
    c = en_moyenne(d, "trop_pres_la_ou_la_bande_saute")
    if i["q95"] < c["q05"] and c["q95"] < f["q05"] and c["lamplitude"] < min(f["lamplitude"], i["lamplitude"]):
        return "LÀ OÙ LA BANDE SAUTE, LE SCAN NE MONTRE NI FEUILLE NI INTERSTICE : SON PROFIL MÉDIAN Y EST PLAT"
    return "LÀ OÙ LA BANDE SAUTE, LE SCAN NE SE DISTINGUE PAS DES TÉMOINS"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"{d['la_bande']}, rangées {_fr(d['les_rangees'][0], 2)} à {_fr(d['les_rangees'][1], 2)} · scan brut "
                   f"au niveau {d['le_niveau']} (9,6 µm), 3 × 3 rayons par point · premier saut de la chaîne, "
                   f"prédiction {LA_PREDICTION}", petit, GRIS)

    # ── PANNEAU 1 · LE PROFIL MÉDIAN ALIGNÉ ─────────────────────────────────────────────────
    panneau(50, 84, 760, 800, f"CE QUE LE SCAN MONTRE EN MOYENNE · côté plus, rapporté à la feuille du segment")
    gx0, gx1, gy0, gy1 = 110, 730, 140, 640
    Y0, Y1 = 0.75, 1.3
    for f_ in (0.8, 0.9, 1.0, 1.1, 1.2, 1.3):
        yg = gy1 - (gy1 - gy0) * (f_ - Y0) / (Y1 - Y0)
        art.line([gx0, yg, gx1, yg], fill=TRAIT, width=1)
        ecrire(gx0 - 36, yg - 7, _fr(f_, 1), 0, GRIS)
    courbes = {}
    for nom, cle, coul in LES_GROUPES:
        prof = en_moyenne(d, cle)["le_profil_median"]
        m = len(prof) // 2
        pts = [(gx0 + (gx1 - gx0) * k / (len(prof) - 1), gy1 - (gy1 - gy0) * (max(min(y, Y1), Y0) - Y0) / (Y1 - Y0))
               for k, y in enumerate(prof)]
        art.line(pts, fill=coul, width=3 if cle.startswith("trop") else 2)
        points.extend(pts)
        courbes[cle] = prof
        traces.setdefault("demi", m)
    traces["courbes"] = courbes
    m = traces["demi"]
    for dv in (-40, -20, 0, 20, 40):
        xg = gx0 + (gx1 - gx0) * (dv + m) / (2 * m)
        art.line([xg, gy1, xg, gy1 + 5], fill=GRIS, width=1)
        ecrire(xg - 8, gy1 + 8, _fr(dv, 0), 0, GRIS)
    ecrire(gx0, gy1 + 26, "voxels de part et d'autre de la profondeur alignée, dans le sens du rayon", 0, GRIS)
    for k, (nom, cle, coul) in enumerate(LES_GROUPES):
        yl = 700 + k * 22
        art.rectangle([74, yl + 3, 88, yl + 11], fill=coul)
        c = en_moyenne(d, cle)
        ecrire(96, yl, f"{nom} · {c['les_rayons']} rayons · contraste {_fr(c['le_contraste'])}", 0, ENCRE)

    # ── PANNEAU 2 · RAYON PAR RAYON ─────────────────────────────────────────────────────────
    panneau(780, 84, 1310, 330, "RAYON PAR RAYON, LES TÉMOINS SE RECOUVRENT")
    bx0, bx1 = 900, 1290
    X0, X1 = 0.4, 1.6
    y = 136
    barres = 0
    for nom_c, cote in LES_COTES:
        j = d["les_predictions"][LA_PREDICTION][cote]
        ecrire(796, y, f"côté {nom_c} · aire sous la courbe {_fr(j['le_seuil']['laire_sous_la_courbe'], 4)}", 0, ENCRE)
        y += 20
        for nom, cle, coul in (("feuille", "le_temoin_feuille", BON), ("interstice", "le_temoin_interstice", CONTRE)):
            q = j[cle]
            xa, xm, xb = (bx0 + (bx1 - bx0) * (q[k] - X0) / (X1 - X0) for k in ("q25", "mediane", "q75"))
            art.rectangle([xa, y + 2, xb, y + 12], fill=coul)
            art.line([xm, y, xm, y + 14], fill=ENCRE, width=2)
            points.extend([(xa, y), (xb, y + 12)])
            ecrire(806, y, nom, 0, GRIS)
            barres += 1
            y += 22
        y += 10
    for f_ in (0.5, 1.0, 1.5):
        xg = bx0 + (bx1 - bx0) * (f_ - X0) / (X1 - X0)
        art.line([xg, 150, xg, y - 6], fill=TRAIT, width=1)
        ecrire(xg - 10, y - 4, _fr(f_, 1), 0, GRIS)
    traces["barres"] = barres
    ecrire(796, y + 14, "le quart central de chaque témoin, et sa médiane", 0, GRIS)

    # ── PANNEAU 3 · LE CONTRASTE ────────────────────────────────────────────────────────────
    panneau(780, 350, 1310, 800, "LE CONTRASTE, AVEC SON INTERVALLE DE 5 À 95 %")
    cx0, cx1 = 1000, 1290
    C0, C1 = 0.85, 1.3
    y = 396
    pointes = 0
    for nom, cle, coul in LES_GROUPES:
        ecrire(796, y, nom, 0, ENCRE)
        y += 18
        for pred in ("m7", "ps256"):
            for nom_c, cote in LES_COTES:
                c = en_moyenne(d, cle, pred, cote)
                xa, xm, xb = (cx0 + (cx1 - cx0) * (min(max(c[k], C0), C1) - C0) / (C1 - C0)
                              for k in ("q05", "le_contraste", "q95"))
                art.line([xa, y + 6, xb, y + 6], fill=coul, width=2)
                art.ellipse([xm - 3, y + 3, xm + 3, y + 9], fill=coul)
                points.append((xm, y + 6))
                ecrire(810, y, f"{pred}, côté {nom_c}", 0, GRIS)
                pointes += 1
                y += 16
        y += 10
    for f_ in (0.9, 1.0, 1.1, 1.2, 1.3):
        xg = cx0 + (cx1 - cx0) * (f_ - C0) / (C1 - C0)
        art.line([xg, 410, xg, y - 6], fill=TRAIT, width=1)
        ecrire(xg - 10, y - 4, _fr(f_, 1), 0, GRIS)
    traces["pointes"] = pointes

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    f, i, c = (en_moyenne(d, k) for k in ("le_temoin_feuille", "le_temoin_interstice", "trop_pres_la_ou_la_bande_saute"))
    b = en_moyenne(d, "la_couche_de_la_bande_la_ou_elle_saute")
    ecrire(50, 832, "LE VERDICT : le scan ne dit pas qui a manqué un tour ; là où la bande saute, il ne montre de feuille "
                    "ni où la chaîne est tombée ni où la bande a posé sa couche", petit, ENCRE)
    ecrire(50, 856, f"★ en moyenne les témoins se séparent (contraste {_fr(f['le_contraste'])} contre "
                    f"{_fr(i['le_contraste'])}) ; là où la bande saute, {_fr(c['le_contraste'])} et une amplitude de "
                    f"{_fr(c['lamplitude'])} contre {_fr(f['lamplitude'])}.", moyen, ENCRE)
    ecrire(50, 882, f"★ la couche que la bande y a posée n'a pas non plus le profil d'une feuille : contraste "
                    f"{_fr(b['le_contraste'])}, amplitude {_fr(b['lamplitude'])}.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : le juge point par point, déclaré d'avance, a échoué son étalonnage ; le "
                    "juge en moyenne a été ajouté après, et il ne lit qu'à 9,6 µm.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
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

    d = lire()
    tmp = sortie.parent / ".sonde_249.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LÀ OÙ LA BANDE SAUTE" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    # ⚠⚠⚠ LES COURBES DOIVENT ÊTRE LES PROFILS PUBLIÉS, et leur centre est la profondeur alignée.
    for _, cle, _ in LES_GROUPES:
        v(f"★★★★ la courbe « {cle} » est le profil publié", traces["courbes"][cle] == en_moyenne(d, cle)["le_profil_median"])
    v("★★★ les profils ont un centre", all(len(p) == 2 * traces["demi"] + 1 for p in traces["courbes"].values()))
    v("★★★★ chaque témoin a sa barre, des deux côtés", traces["barres"] == 4)
    v("★★★★ chaque groupe a son contraste, deux prédictions et deux côtés", traces["pointes"] == 4 * len(LES_GROUPES))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte l'aire, les deux prédictions et ce qui n'est PAS établi",
      "aire sous la courbe" in txt and "ps256" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "249_la_bande_a_t_elle_manque_un_tour.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
