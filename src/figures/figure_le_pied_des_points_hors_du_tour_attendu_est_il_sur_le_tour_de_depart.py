"""Sur PHercParis4, graines 4 à 8, sous les croissances à cheval : sur quel tour publié est posé le pied, sur la surface de départ, des points à l'écart de leur spire, hors du tour attendu et sur l'attendu.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux groupes de barres : à gauche les pieds des points hors du tour attendu, à droite, le
contrôle, ceux des points sur l'attendu. Dans chaque groupe, la part des pieds posés sur le tour de départ, sur le tour d'avant, sur le
tour attendu, ailleurs.

  uv run python src/figures/figure_le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.py \\
      --sortie docs/images/362_le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.png

⚠ Tout vient de la mesure de `362`.
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
import le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart as m362  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.json"

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
LES_TOURS = (("depart", "sur le tour de départ", BLEU), ("avant", "sur le tour d'avant", ORANGE),
             ("attendu", "sur le tour attendu", GRIS_BARRE), ("ailleurs", "ailleurs", CLAIR))
LES_GROUPES = (("hors", "pieds des points hors du tour attendu", 300), ("attendu", "pieds des points sur le tour attendu", 800))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_tour_du_pied(pied: str, w0: int, sens: int) -> str | None:
    """Où est un pied posé, par rapport au tour de départ du saut ; None s'il n'est posé sur aucun tour."""
    if pied in (m362.SANS_PIED, ""):
        return None
    w = {int(t) for t in pied.split(",")}
    return "depart" if w0 in w else "avant" if w0 - sens in w else "attendu" if w0 + sens in w else "ailleurs"


def les_pieds(d: dict) -> dict[str, Counter]:
    """Sous les croissances à cheval jugées de `361`, les pieds posés, par tour, des points hors de l'attendu et sur l'attendu."""
    out = {"hors": Counter(), "attendu": Counter()}
    for s, sens in m361.les_croissances_a_cheval(d["les_cotes"]):
        lu = m361.la_lecture(s, sens)
        if lu is None or m361.le_cote_de(lu)[3] < m361.LE_MINIMUM_DE_POINTS:
            continue
        p = m362.les_pieds_de(s, sens)
        for g in ("hors", "attendu"):
            for pied, n in p[g].items():
                t = le_tour_du_pied(pied, s["le_tour_de_depart"], sens)
                if t is not None:
                    out[g][t] += n
    return out


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    h = d["le_bilan"]["hors"]
    return (f"{round(100 * h['sur_le_depart'] / h['poses'])} % des pieds sur le tour de départ : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un, _, deux = d["le_verdict"]["lissue"].partition(" ; ")
    p = les_pieds(d)["hors"]
    trois = (f"rapporté à côté, qui ne décide rien : des pieds posés hors du tour de départ, {p.get('avant', 0)} sont sur le tour d'avant "
             f"et {p.get('attendu', 0)} sur le tour attendu")
    quatre = "⚠ ce qui n'est PAS établi : où le retard est né, dans la nappe de départ ou dans une croissance plus tôt."
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
    ecrire(50, 46, "sur PHercParis4, graines 4 à 8, sous les croissances à cheval : le pied d'un point est le point de la surface de départ "
                   "en face de lui", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    ecrire(x0 + 12, y0 + 8, "les points à l'écart de leur spire", moyen, ENCRE)
    for i, (_, nom, couleur) in enumerate(LES_TOURS):
        lx, ly = x0 + 420 + (i % 2) * 230, y0 + 10 + (i // 2) * 20
        art.rectangle([lx, ly + 2, lx + 12, ly + 14], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, ly + 2, ly + 14))
        ecrire(lx + 20, ly, nom, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    pieds = les_pieds(d)
    for groupe, titre, centre in LES_GROUPES:
        c = pieds[groupe]
        total = sum(c.values())
        for i, (cle, _, couleur) in enumerate(LES_TOURS):
            part = c.get(cle, 0) / total if total else 0.0
            gauche = centre - 2 * LARGEUR - 15 + i * (LARGEUR + 10)
            sommet = BAS - round(part * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((groupe, cle, part, sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            ecrire(gauche + 18, sommet - 18, f"{round(100 * part)} %", petit, ENCRE)
        ecrire(centre - 90, BAS + 8, f"{total} pieds posés", petit, ENCRE)
        ecrire(centre - 135, BAS + 26, titre, moyen, ENCRE)
        traces["titres"].append((groupe, titre, total))

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
    tmp = sortie.parent / ".sonde_362.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"]["hors"] = {"sur_le_depart": 30, "poses": 40}
    autre["le_verdict"]["lissue"] = "x ; c'est le tour publié qui se contredit"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "75 % DES PIEDS SUR LE TOUR DE DÉPART : C'EST LE TOUR PUBLIÉ QUI SE CONTREDIT",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    v("★★★★ la bande tient dans la toile", LA_BANDE + 10 + 18 * 3 + 8 + 18 < H_)
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ le tour d'un pied, par rapport au tour de départ et au sens du saut",
      [le_tour_du_pied(p, -3, -1) for p in ("-3", "-2", "-4", "-6", "?", "", "-4,-3")]
      == ["depart", "avant", "attendu", "ailleurs", None, None, "depart"]
      and [le_tour_du_pied(p, -3, 1) for p in ("-4", "-2")] == ["avant", "attendu"])
    p = les_pieds(d)
    b = d["le_bilan"]
    v("★★★★ les pieds de la figure redonnent le bilan de la mesure, hors de l'attendu et sur l'attendu",
      (p["hors"].get("depart", 0), sum(p["hors"].values()), p["attendu"].get("depart", 0), sum(p["attendu"].values()))
      == (b["hors"]["sur_le_depart"], b["hors"]["poses"], b["attendu"]["sur_le_depart"], b["attendu"]["poses"]), str(p))
    avec_peu = json.loads(json.dumps(d))
    cote = next(c for c in avec_peu["les_cotes"] if c["le_rang"] >= 4)
    cote["les_sauts"].append({"la_justesse": "juste", "depuis": "la croissance", "a_cheval": True, "le_tour_de_depart": 0,
                              "en_plus": {"lecart_de_la_spire": 10.0,
                                          "les_comptes": {"0|à l'écart de la spire|croissance|1": 9,
                                                          f"{m361.m344.LE_SENS[cote['le_cote']]}|à l'écart de la spire|croissance|0": 40}}})
    v("★★★★ une croissance à cheval à moins de 10 points lus hors de l'attendu n'est pas lue", les_pieds(avec_peu) == p)
    attendu = [(g, k, p[g].get(k, 0) / sum(p[g].values())) for g, _, _ in LES_GROUPES for k, _, _ in LES_TOURS]
    v("★★★★ les parts par tour se recomptent sur les pieds",
      [(g, k, round(x, 9)) for g, k, x, _, _ in traces["barres"]] == [(g, k, round(x, 9)) for g, k, x in attendu], str(traces["barres"]))
    v("★★★★ chaque tour a sa couleur", all(f == {k: c for k, _, c in LES_TOURS}[k] for _, k, _, _, f in traces["barres"])
      and {k: c for k, _, c in LES_TOURS} == {"depart": BLEU, "avant": ORANGE, "attendu": GRIS_BARRE, "ailleurs": CLAIR})
    v("★★★★ chaque groupe porte son nom, à gauche les pieds des points hors de l'attendu",
      [(g, t) for g, t, _ in traces["titres"]] == [("hors", "pieds des points hors du tour attendu"),
                                                   ("attendu", "pieds des points sur le tour attendu")])
    v("★★★★ la hauteur de chaque barre est sa part", all(BAS - s == round(x * (BAS - HAUT)) for _, _, x, s, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte à côté les pieds du tour d'avant et du tour attendu, recomptés",
      f"{p['hors'].get('avant', 0)} sont sur le tour d'avant et {p['hors'].get('attendu', 0)} sur le tour attendu" in " ".join(la_bande(d)))
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
                   / "362_le_pied_des_points_hors_du_tour_attendu_est_il_sur_le_tour_de_depart.png")
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
