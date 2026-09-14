#!/usr/bin/env python3
"""Lire la cause sous le bruit.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** En bas à droite, le
compromis que la mesure a trouvé et que je n'attendais pas : chaque variante est un point entre ce
qu'elle sait LIRE (le bruit le plus fort où elle sépare encore les causes) et ce qu'elle fait MARCHER
(les réussites). Retrancher le plancher du bruit gagne un cran de lecture et en perd onze de marche.
En haut à gauche, où chaque variante sépare encore ; en haut à droite, ce que chacune coûte ; en bas
à gauche, le mécanisme — à bruit 16 la lecture brute écrase toutes les matières entre 0,76 et 0,85,
la corrigée les rouvre.

  uv run python src/figures/figure_lire_la_cause_sous_le_bruit.py \\
      --json docs/mesures/lire_la_cause_sous_le_bruit.json \\
      --sortie docs/images/145_lire_la_cause_sous_le_bruit.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
BRUTE = (176, 92, 42)
CORRIGEE = (60, 110, 90)
PIEGE = (150, 96, 176)
SEPARE = (60, 110, 90)
PERD = (176, 92, 42)


def lire(chemin: Path) -> dict:
    """Le JSON de `lire_la_cause_sous_le_bruit.py`.

    ⚠⚠ Refuse une mesure dont le TÉMOIN INTERNE n'est pas vert : si « bloc 1, brut » ne reproduit
    pas `144`, c'est le protocole qui a bougé et aucune comparaison de cette image ne veut rien dire.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    t = j.get("le_temoin_interne", {})
    if not t.get("decidable"):
        raise ValueError(f"{chemin} : le témoin interne est indécidable")
    if not t.get("le_protocole_est_le_meme"):
        raise ValueError(f"{chemin} : le témoin interne est ROUGE, le protocole a bougé")
    if len(j.get("par_variante", [])) < 2:
        raise ValueError(f"{chemin} : il faut au moins deux variantes à comparer")
    if not j.get("contre_la_regle_brute"):
        raise ValueError(f"{chemin} : « contre_la_regle_brute » absent")
    return d


def _court(nom: str) -> str:
    return nom.replace("plancher retranché", "corrigé")


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1320, 900
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    g = d["sur_la_grille"]
    j = d["juger"]
    pv = j["par_variante"]
    cb = j["contre_la_regle_brute"]
    bruits = [x["bruit"] for x in pv[0]["par_bruit"]]
    ecrire(28, 20, "Lire plus loin et marcher mieux ne sont pas le même réglage", gros, ENCRE)
    ecrire(28, 46, f"fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour · le plancher "
                   f"de bruit retranché vaut exactement 1/√n, n étant le nombre d'incréments · "
                   f"témoin interne vert : « bloc 1, brut » reproduit `144`", petit, GRIS)

    # ── Haut gauche : où chaque variante sépare encore ──────────────────────
    x0, y0, pw, ph = 60, 122, 600, 290
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "où chaque variante sépare encore les causes", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 10, "écart ENTRE les matières / dispersion DANS une, par bruit :",
           petit, GRIS)
    for i, b in enumerate(bruits):
        ecrire(x0 + 268 + i * 108, y0 + 32, f"bruit {b:g}", petit, GRIS)
    yy = y0 + 54
    for x in pv:
        coul = PIEGE if x["bloc"] == 4 else (CORRIGEE if x["corrige"] else BRUTE)
        ecrire(x0 + 12, yy, _court(x["nom"]), petit, coul)
        for i, y in enumerate(x["par_bruit"]):
            ax = x0 + 262 + i * 108
            art.rectangle([ax, yy - 2, ax + 96, yy + 14],
                          fill=(SEPARE if y["la_lecture_separe"] else BANDE))
            points.append((ax, yy))
            ecrire(ax + 6, yy, f"{y['ecart_entre_matieres']:.3f}/"
                               f"{y['dispersion_dans_une_matiere']:.3f}", petit,
                   FOND if y["la_lecture_separe"] else ENCRE)
        yy += 26
    ecrire(x0 + 12, yy + 10, "en vert, l'écart entre matières dépasse la dispersion dans une :",
           petit, GRIS)
    ecrire(x0 + 12, yy + 26, "la lecture y sépare encore les causes.", petit, GRIS)

    # ── Haut droite : ce que chaque variante coûte ──────────────────────────
    x1, y1, pw1, ph1 = 700, 122, L - 700 - 60, 290
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "réussites de la pince, par variante", moyen, ENCRE)
    vals = [x["la pince"]["reussites"] for x in pv]
    hi, lo = max(vals) * 1.03, min(vals) * 0.92
    pas_y = (ph1 - 96) / max(len(pv), 1)

    def bx(v):
        return x1 + 250 + ((float(v) - lo) / max(hi - lo, 1e-9)) * (pw1 - 300)

    for k in range(4):
        vv = lo + (hi - lo) * k / 3.0
        art.line([bx(vv), y1 + 40, bx(vv), y1 + ph1 - 44], fill=TRAIT, width=1)
        ecrire(int(bx(vv)) - 10, y1 + ph1 - 38, f"{vv:.0f}", petit, GRIS)
    for i, x in enumerate(pv):
        coul = PIEGE if x["bloc"] == 4 else (CORRIGEE if x["corrige"] else BRUTE)
        yy = y1 + 48 + i * pas_y
        art.rectangle([x1 + 250, yy, bx(x["la pince"]["reussites"]), yy + 16], fill=coul)
        points.append((bx(x["la pince"]["reussites"]), yy))
        ecrire(x1 + 12, yy + 1, _court(x["nom"]), petit, coul)
        ecrire(int(bx(x["la pince"]["reussites"])) + 6, yy + 1,
               f"{x['la pince']['reussites']}", petit, coul)
    art.line([bx(cb["reussites_de_la_brute"]), y1 + 40, bx(cb["reussites_de_la_brute"]),
              y1 + ph1 - 44], fill=BRUTE, width=1)
    ecrire(x1 + 12, y1 + ph1 - 24, f"la barre verticale est la règle brute de `144` "
                                   f"({cb['reussites_de_la_brute']})", petit, GRIS)

    # ── Bas gauche : le mécanisme, à bruit le plus fort ─────────────────────
    x2, y2, pw2, ph2 = 60, 480, 600, 290
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    fort = max(bruits)
    ecrire(x2, y2 - 24, f"la mémoire lue matière par matière, à bruit {fort:g}", moyen, ENCRE)
    series = [(x, x["par_bruit"][-1]) for x in pv if x["bloc"] == 1]
    mats = [m["nom"] for m in series[0][1]["par_matiere"]]
    pas_x = (pw2 - 120) / max(len(mats) - 1, 1)
    vals2 = [m["memoire"] for _v, y in series for m in y["par_matiere"] if m["memoire"] is not None]
    hi2, lo2 = max(vals2) * 1.02, min(vals2) * 0.97

    def mx(i):
        return x2 + 66 + i * pas_x

    def my(v):
        return y2 + ph2 - 58 - ((float(v) - lo2) / max(hi2 - lo2, 1e-9)) * (ph2 - 120)

    for k in range(4):
        vv = lo2 + (hi2 - lo2) * k / 3.0
        art.line([x2 + 56, my(vv), x2 + pw2 - 12, my(vv)], fill=TRAIT, width=1)
        ecrire(x2 + 12, int(my(vv)) - 7, f"{vv:.3f}", petit, GRIS)
    art.rectangle([x2 + 150, y2 + 6, x2 + pw2 - 10, y2 + 46], fill=FOND)
    for v_, y in series:
        coul = CORRIGEE if v_["corrige"] else BRUTE
        xy = [(mx(i), my(m["memoire"])) for i, m in enumerate(y["par_matiere"])
              if m["memoire"] is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=coul)
            points.append((a_, b_))
        ecrire(x2 + 156, y2 + 8 + (0 if not v_["corrige"] else 18),
               f"{_court(v_['nom'])} — écart {y['ecart_entre_matieres']:.4f}", petit, coul)
    for i, nom in enumerate(mats):
        court = nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
        ecrire(int(mx(i)) - 3 * len(court), y2 + ph2 - 44, court, petit, ENCRE)
    ecrire(x2 + 12, y2 + ph2 - 24, "les matières, du plus lisse au plus froissé", petit, GRIS)

    # ── Bas droite : le compromis ───────────────────────────────────────────
    x3, y3, pw3, ph3 = 700, 480, L - 700 - 60, 290
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "lire loin contre marcher bien", moyen, ENCRE)
    portees = [max(x["bruits_ou_elle_separe"]) if x["bruits_ou_elle_separe"] else -1.0
               for x in pv]
    hi3, lo3 = max(vals) * 1.03, min(vals) * 0.92
    tous_b = sorted({p for p in portees if p >= 0.0})

    def px(p):
        return x3 + 70 + (tous_b.index(p) if p in tous_b else -1) * (pw3 - 140) / max(
            len(tous_b) - 1, 1)

    def py(v):
        return y3 + ph3 - 58 - ((float(v) - lo3) / max(hi3 - lo3, 1e-9)) * (ph3 - 120)

    for k in range(4):
        vv = lo3 + (hi3 - lo3) * k / 3.0
        art.line([x3 + 56, py(vv), x3 + pw3 - 12, py(vv)], fill=TRAIT, width=1)
        ecrire(x3 + 12, int(py(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    for b in tous_b:
        ecrire(int(px(b)) - 6, y3 + ph3 - 44, f"{b:g}", petit, GRIS)
    ecrire(x3 + 56, y3 + ph3 - 24, "bruit le plus fort où la lecture sépare encore", petit, GRIS)
    art.rectangle([x3 + 130, y3 + 6, x3 + pw3 - 10, y3 + 44], fill=FOND)
    for x, p in zip(pv, portees, strict=True):
        if p < 0.0:
            continue
        coul = PIEGE if x["bloc"] == 4 else (CORRIGEE if x["corrige"] else BRUTE)
        a_, b_ = px(p), py(x["la pince"]["reussites"])
        art.ellipse([a_ - 6, b_ - 6, a_ + 6, b_ + 6], fill=coul)
        points.append((a_, b_))
        # ⚠ Une étiquette posée à droite d'un point qui est déjà à droite sort du panneau : la
        # garde des cadres l'a dit. Elle passe à gauche quand le point est dans la moitié droite.
        libelle = _court(x["nom"])
        largeur = int(petit.getbbox(libelle)[2])
        if a_ + 10 + largeur > x3 + pw3 - 10:
            ecrire(int(a_) - 10 - largeur, int(b_) - 6, libelle, petit, coul)
        else:
            ecrire(int(a_) + 10, int(b_) - 6, libelle, petit, coul)
    ecrire(x3 + 136, y3 + 8, "en haut à droite serait le meilleur des deux :", petit, ENCRE)
    ecrire(x3 + 136, y3 + 24, "aucune variante n'y est.", petit, ENCRE)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 792
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    gagnante = next((x for x in cb["par_variante"] if x["bruits_gagnes"]), None)
    p_ = j.get("le_piege_du_bloc", {})
    ecrire(44, by0 + 10, f"★ retrancher le plancher du bruit fait lire la cause à un bruit où la "
                         f"règle brute échoue : {gagnante['bruits_gagnes'] if gagnante else '—'} "
                         f"gagné, avec un écart de "
                         f"{pv[1]['par_bruit'][-1]['ecart_entre_matieres']:.4f} contre une "
                         f"dispersion de "
                         f"{pv[1]['par_bruit'][-1]['dispersion_dans_une_matiere']:.4f}.",
           moyen, ENCRE)
    ecrire(44, by0 + 34, f"⚠ et il le PAIE : {gagnante['reussites_de_la_pince'] if gagnante else 0}"
                         f" réussites contre {cb['reussites_de_la_brute']} pour la règle brute. "
                         f"Lire plus loin pousse la mémoire vers le haut, et `143` mesure que la "
                         f"mémoire échange de la fidélité contre de la distance.", petit, ENCRE)
    ecrire(44, by0 + 52, f"⚠ le bloc n'achète rien : « {_court(p_.get('nom', ''))} » — la période "
                         f"du froissement — perd {p_.get('elle_perd_ce_que_la_brute_avait') or '—'}"
                         f", le piège annoncé se referme.", petit, ENCRE)
    ecrire(44, by0 + 74, "⚠ conséquence : diagnostiquer la cause et conduire le suiveur ne sont pas "
                         "le même réglage de la même grandeur.", petit, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile  # noqa: PLC0415

    from figure_commune import glyphes_manquants  # noqa: PLC0415

    src = RACINE / "docs" / "mesures" / "lire_la_cause_sous_le_bruit.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        j = d["juger"]
        rouge = json.loads(json.dumps(d))
        rouge["juger"]["le_temoin_interne"]["le_protocole_est_le_meme"] = False
        for nom, contenu in (
                ("message", {"message": "précédent absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("témoin ROUGE", rouge),
                ("une seule variante", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True, "le_temoin_interne": j["le_temoin_interne"],
                    "par_variante": j["par_variante"][:1],
                    "contre_la_regle_brute": j["contre_la_regle_brute"]}}),
                ("sans comparaison", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True, "le_temoin_interne": j["le_temoin_interne"],
                    "par_variante": j["par_variante"]}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "145.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 5,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1320)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g_ for _x, _y, t_, _f in poses for g_ in glyphes_manquants(t_)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1320 and 0 <= y <= 900 for x, y in points), f"{len(points)} points")
        # ⚠ Le compte attendu est DÉRIVÉ de ce que la mesure implique de dessiner.
        attendus = (len(j["par_variante"]) * len(j["par_variante"][0]["par_bruit"])
                    + len(j["par_variante"]) * 2
                    + 2 * len(j["par_variante"][0]["par_bruit"][0]["par_matiere"]))
        v("il y a de quoi regarder ce que la mesure contient", len(points) >= attendus,
          f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "145_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["contre_la_regle_brute"]["reussites_de_la_brute"] = 999
        troisieme = tmp / "145_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())
        d3 = json.loads(json.dumps(d))
        for x in d3["juger"]["par_variante"]:
            for y in x["par_bruit"]:
                y["la_lecture_separe"] = True
        quatrieme = tmp / "145_qua.png"
        dessiner(d3, quatrieme)
        v("⭐ le tableau de séparation lit la mesure lui aussi",
          quatrieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/lire_la_cause_sous_le_bruit.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/145_lire_la_cause_sous_le_bruit.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
