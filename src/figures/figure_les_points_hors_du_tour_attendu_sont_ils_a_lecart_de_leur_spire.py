"""Sur PHercParis4, graines 4 à 8, sous les croissances à cheval : où sont, par leur écart au départ rapporté à celui de leur spire, les points que les tours publiés posent hors du tour attendu, et ceux qu'ils posent sur l'attendu.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux groupes de barres : à gauche les points hors du tour attendu, à droite, le contrôle,
les points sur le tour attendu. Dans chaque groupe, la part des points lus près du départ, à l'écart de la spire, au-delà, de l'autre côté.
Si les deux groupes se ressemblent, les points hors de l'attendu sont où sont ceux de l'attendu.

  uv run python src/figures/figure_les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.py \\
      --sortie docs/images/361_les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.png

⚠ Tout vient de la mesure de `361`.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)
import les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire as m361  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
GRIS_BARRE = (170, 172, 176)
CLAIR = (214, 212, 206)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 150, 390
LARGEUR = 70
LES_ZONES = ((m361.PRES, ORANGE), (m361.SPIRE, BLEU), (m361.DELA, GRIS_BARRE), (m361.AUTRE, CLAIR))
LES_GROUPES = (("hors", "points hors du tour attendu", 300), ("attendu", "points sur le tour attendu", 800))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_points(d: dict, partie: str | None = None) -> dict[str, Counter]:
    """Sous les croissances à cheval jugées, les points hors du tour attendu et sur l'attendu, par zone."""
    out = {"hors": Counter(), "attendu": Counter()}
    for s, sens in m361.les_croissances_a_cheval(d["les_cotes"]):
        lu = m361.la_lecture(s, sens)
        if lu is None or m361.le_cote_de(lu)[3] < m361.LE_MINIMUM_DE_POINTS:
            continue
        lu = m361.la_lecture(s, sens, partie) if partie else lu
        out["hors"].update(lu["restes"])
        out["hors"].update(lu["au_dela"])
        out["attendu"].update(lu["attendu"])
    return out


def les_parts(c: Counter) -> tuple[dict[str, float], int]:
    lus = sum(n for z, n in c.items() if z != m361.INCONNU)
    return {z: (c.get(z, 0) / lus if lus else 0.0) for z, _ in LES_ZONES}, lus


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"sous {b['a_lecart_de_la_spire']} des {b['les_jugees']} croissances à cheval, les points hors de l'attendu sont à l'écart "
            f"de leur spire").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un, _, deux = d["le_verdict"]["lissue"].partition(" ; ")
    s, c = les_points(d, "semis")["hors"], les_points(d, "croissance")["hors"]
    trois = (f"rapporté à côté, qui ne décide rien : de ces points hors de l'attendu, {s.get(m361.SPIRE, 0)} semés depuis la spire et "
             f"{c.get(m361.SPIRE, 0)} de la croissance sont à l'écart de la spire")
    quatre = "⚠ ce qui n'est PAS établi : lequel se trompe, du tour publié ou de la surface de départ ; seul le scan le dira."
    return f"LE VERDICT DÉCLARÉ : {un} ;", deux, trois, quatre


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(14, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": [], "titres": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "sur PHercParis4, graines 4 à 8 : chaque point lu par son écart au départ, rapporté à celui de sa spire ; une barre est "
                   "une part des points lus", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    ecrire(x0 + 12, y0 + 8, "sous les croissances à cheval", moyen, ENCRE)
    for i, (zone, couleur) in enumerate(LES_ZONES):
        lx, ly = x0 + 420 + (i % 2) * 230, y0 + 10 + (i // 2) * 20
        art.rectangle([lx, ly + 2, lx + 12, ly + 14], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, ly + 2, ly + 14))
        ecrire(lx + 20, ly, zone, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    pts = les_points(d)
    for groupe, titre, centre in LES_GROUPES:
        parts, lus = les_parts(pts[groupe])
        for i, (zone, couleur) in enumerate(LES_ZONES):
            gauche = centre - 2 * LARGEUR - 15 + i * (LARGEUR + 10)
            sommet = BAS - round(parts[zone] * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((groupe, zone, parts[zone], sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            ecrire(gauche + 18, sommet - 18, f"{round(100 * parts[zone])} %", petit, ENCRE)
        ecrire(centre - 90, BAS + 8, f"{lus} points lus", petit, ENCRE)
        ecrire(centre - 110, BAS + 26, titre, moyen, ENCRE)
        traces["titres"].append((groupe, titre, lus))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    for k, ligne in enumerate(la_bande(d)):
        if k < 3:
            ecrire(50, LA_BANDE + 10 + 18 * k, ligne, petit, ENCRE)
        else:
            ecrire(50, LA_BANDE + 10 + 18 * k + 8, ligne, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_361.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"a_lecart_de_la_spire": 7, "les_jugees": 9})
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("SOUS 7 DES 9 CROISSANCES À CHEVAL"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    v("★★★★ la bande tient dans la toile", LA_BANDE + 10 + 18 * 3 + 8 + 18 < H_)
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    hors, att, jugees = Counter(), Counter(), 0
    for co in d["les_cotes"]:
        if co["le_rang"] < 4:
            continue
        sens = {"plus": 1, "moins": -1}[co["le_cote"]]
        for s in co["les_sauts"]:
            if not (s["la_justesse"] == "juste" and s["depuis"] == "la croissance" and s["a_cheval"] and s.get("en_plus")
                    and s.get("le_tour_de_depart") is not None):
                continue
            w0 = s["le_tour_de_depart"]
            h_, a_ = Counter(), Counter()
            for cle, n in s["en_plus"]["les_comptes"].items():
                tours, zone, _ = cle.split("|")
                w = {int(t) for t in tours.split(",") if t}
                if w0 + sens in w:
                    a_[zone] += n
                elif w0 in w or w0 + 2 * sens in w:
                    h_[zone] += n
            if sum(n for z, n in h_.items() if z != "inconnu") >= 10:
                hors.update(h_)
                att.update(a_)
                jugees += 1
    v("★★★★ les croissances lues sont les croissances jugées du bilan", jugees == d["le_bilan"]["les_jugees"], str(jugees))
    avec_peu = json.loads(json.dumps(d))
    cote = next(c for c in avec_peu["les_cotes"] if c["le_rang"] >= 4)
    w0 = 0
    cote["les_sauts"].append({"la_justesse": "juste", "depuis": "la croissance", "a_cheval": True, "le_tour_de_depart": w0,
                              "en_plus": {"lecart_de_la_spire": 10.0, "les_comptes": {f"{w0}|près du départ|croissance": 9}}})
    v("★★★★ une croissance à cheval à moins de 10 points lus hors de l'attendu n'est pas lue",
      les_points(avec_peu)["hors"] == les_points(d)["hors"])
    attendu = []
    for g, c in (("hors", hors), ("attendu", att)):
        lus = sum(n for z, n in c.items() if z != "inconnu")
        attendu += [(g, z, c.get(z, 0) / lus) for z, _ in LES_ZONES]
    v("★★★★ les parts par zone se recomptent sur les points, hors de l'attendu puis sur l'attendu",
      [(g, z, round(p, 9)) for g, z, p, _, _ in traces["barres"]] == [(g, z, round(p, 9)) for g, z, p in attendu], str(traces["barres"]))
    v("★★★★ chaque zone a sa couleur", all(f == dict(LES_ZONES)[z] for _, z, _, _, f in traces["barres"])
      and dict(LES_ZONES) == {"près du départ": ORANGE, "à l'écart de la spire": BLEU, "au-delà": GRIS_BARRE, "de l'autre côté": CLAIR})
    v("★★★★ chaque groupe porte son nom, à gauche les points hors de l'attendu",
      [(g, t) for g, t, _ in traces["titres"]] == [("hors", "points hors du tour attendu"), ("attendu", "points sur le tour attendu")])
    v("★★★★ la hauteur de chaque barre est sa part", all(BAS - s == round(p * (BAS - HAUT)) for _, _, p, s, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ le contrôle de la mesure se relit sur la figure : sur l'attendu, plus de la moitié à l'écart de la spire",
      d["le_bilan"]["le_controle"] == (attendu[5][2] > 0.5))
    v("★★★★ la bande porte le verdict entier", " ".join(la_bande(d)[:2]) == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    textes = {t for _, _, t, _ in poses}
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for t in textes))
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
                   / "361_les_points_hors_du_tour_attendu_sont_ils_a_lecart_de_leur_spire.png")
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
