#!/usr/bin/env python3
"""Un suiveur n'a rien à quoi se comparer.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** En bas à gauche,
l'obstacle : les quinze lectures que `145` publie, triées. Les matières SANS aucune cause s'y mêlent
aux matières qui en portent deux, donc aucune ligne horizontale ne les sépare — et un suiveur ne voit
qu'un de ces nombres. En haut à gauche, pourquoi la référence absolue échoue : sur la spirale
ÉCRASÉE, la règle de l'enroulement lit 0,8107 là où les règles de cohérence lisent zéro. L'écrasement
excède l'enroulement, et c'est pourtant la forme qu'il faut suivre. En haut à droite, ce que ça coûte.

  uv run python src/figures/figure_un_suiveur_na_rien_a_quoi_se_comparer.py \\
      --json docs/mesures/un_suiveur_na_rien_a_quoi_se_comparer.json \\
      --sortie docs/images/146_un_suiveur_na_rien_a_quoi_se_comparer.png
"""
from __future__ import annotations

import argparse
import json
import statistics
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
SANS = (176, 92, 42)
AVEC = (60, 110, 90)
COUL = ((176, 92, 42), (86, 104, 132), (150, 96, 176))


def lire(chemin: Path) -> dict:
    """Le JSON de `un_suiveur_na_rien_a_quoi_se_comparer.py`.

    ⚠⚠ Refuse une mesure dont les TÉMOINS INTERNES ne sont pas verts : si les règles de `144` et
    `145` ne se reproduisent pas, c'est le protocole qui a bougé et rien de cette image ne vaut.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    t = j.get("les_temoins_internes", {})
    if not t.get("decidable"):
        raise ValueError(f"{chemin} : les témoins internes sont indécidables")
    if not t.get("le_protocole_est_le_meme"):
        raise ValueError(f"{chemin} : les témoins internes sont ROUGES, le protocole a bougé")
    o = j.get("les_lectures_se_recouvrent", {})
    if not o.get("decidable"):
        raise ValueError(f"{chemin} : l'obstacle est indécidable, `145` manque")
    if len(j.get("par_variante", [])) < 3:
        raise ValueError(f"{chemin} : il faut les trois règles à comparer")
    return d


def _lue(grille: dict, v: dict, bruit: float, nom: str) -> float | None:
    for c in grille["cases"]:
        if (c["bruit"] == bruit and c["nom"] == nom and c["bloc_du_cap"] == v["bloc"]
                and bool(c["corrige_le_bruit"]) is bool(v["corrige"])
                and bool(c.get("enroulement_du_cap", False)) is bool(v["enroulement"])):
            xs = [x["memoire_mediane"] for x in c["bras"]["la pince"]["suivis"]
                  if x.get("decidable") and x.get("memoire_mediane") is not None]
            return round(statistics.median(xs), 4) if xs else None
    return None


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
    o = j["les_lectures_se_recouvrent"]
    ecrire(28, 20, "Un suiveur n'a rien à quoi se comparer", gros, ENCRE)
    ecrire(28, 46, f"fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour · témoins "
                   f"internes verts : les règles de `144` et `145` se reproduisent · "
                   f"{o['inversions']} inversions sur {o['lectures']} lectures", petit, GRIS)

    # ── Haut gauche : pourquoi la référence absolue échoue ──────────────────
    x0, y0, pw, ph = 60, 122, 600, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la mémoire lue par matière, sans bruit", moyen, ENCRE)
    mats = sorted({c["nom"] for c in g["cases"]},
                  key=lambda n: (("froissée" in n) + ("écrasée" in n), n))
    mats = []
    for c in g["cases"]:
        if c["bruit"] == 0.0 and c["nom"] not in mats:
            mats.append(c["nom"])
    pas_x = (pw - 130) / max(len(mats) - 1, 1)

    def mx(i):
        return x0 + 70 + i * pas_x

    def my(v):
        return y0 + ph - 58 - float(v) * (ph - 122)

    for k in range(5):
        vv = k / 4.0
        art.line([x0 + 56, my(vv), x0 + pw - 12, my(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 14, int(my(vv)) - 7, f"{vv:.2f}", petit, GRIS)
    art.rectangle([x0 + 150, y0 + 6, x0 + pw - 10, y0 + 62], fill=FOND)
    for k, v in enumerate(g["variantes"]):
        xy = [(mx(i), my(u)) for i, n in enumerate(mats)
              if (u := _lue(g, v, 0.0, n)) is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=COUL[k % len(COUL)], width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=COUL[k % len(COUL)])
            points.append((a_, b_))
        ecrire(x0 + 156, y0 + 8 + k * 17, v["nom"], petit, COUL[k % len(COUL)])
    for i, nom in enumerate(mats):
        court = nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
        ecrire(int(mx(i)) - 3 * len(court), y0 + ph - 44, court, petit, ENCRE)
    ecrire(x0 + 14, y0 + ph - 22, "les matières, du plus lisse au plus froissé", petit, GRIS)

    # ── Haut droite : ce que chaque règle fait marcher ──────────────────────
    x1, y1, pw1, ph1 = 700, 122, L - 700 - 60, 300
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "réussites de la pince, par règle", moyen, ENCRE)
    vals = [x["la pince"]["reussites"] for x in pv]
    hi = max(vals) * 1.06
    pas_y = (ph1 - 110) / max(len(pv), 1)

    def bx(v):
        return x1 + 190 + (float(v) / hi) * (pw1 - 250)

    for k in range(4):
        # ⚠ Pas d'étiquette sous ces repères : chaque barre porte déjà SON nombre au bout.
        # Une graduation en plus recouvrirait la phrase qui explique la colonne des bruits.
        art.line([bx(hi * k / 3.0), y1 + 50, bx(hi * k / 3.0), y1 + ph1 - 54],
                 fill=TRAIT, width=1)
    for i, x in enumerate(pv):
        yy = y1 + 58 + i * pas_y
        art.rectangle([x1 + 190, yy, bx(x["la pince"]["reussites"]), yy + 18],
                      fill=COUL[i % len(COUL)])
        points.append((bx(x["la pince"]["reussites"]), yy))
        ecrire(x1 + 14, yy + 2, x["nom"], petit, COUL[i % len(COUL)])
        ecrire(int(bx(x["la pince"]["reussites"])) + 6, yy + 2,
               f"{x['la pince']['reussites']}", petit, COUL[i % len(COUL)])
    ecrire(x1 + 14, y1 + ph1 - 50, "et à quels bruits chacune sépare encore les causes :",
           petit, GRIS)
    yy = y1 + ph1 - 30
    for i, x in enumerate(pv):
        ecrire(x1 + 14 + i * 172, yy, f"{x['bruits_ou_elle_separe']}", petit, COUL[i % len(COUL)])

    # ── Bas gauche : l'obstacle ─────────────────────────────────────────────
    x2, y2, pw2, ph2 = 60, 490, 600, 280
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "les quinze lectures de `145`, triées", moyen, ENCRE)
    lec = sorted(
        [{"nom": m["nom"], "bruit": y["bruit"], "memoire": m["memoire"],
          "sans": "nue" in m["nom"]}
         for v in [next(x for x in pv if x["corrige"])] for y in v["par_bruit"]
         for m in y["par_matiere"] if m.get("memoire") is not None],
        key=lambda z: z["memoire"])
    pas_y2 = (ph2 - 72) / max(len(lec), 1)
    for i, z in enumerate(lec):
        yy = y2 + 34 + i * pas_y2
        coul = SANS if z["sans"] else AVEC
        art.rectangle([x2 + 14, yy, x2 + 14 + z["memoire"] * (pw2 - 240), yy + 8], fill=coul)
        points.append((x2 + 14 + z["memoire"] * (pw2 - 240), yy))
        court = z["nom"].replace("spirale ", "").replace("écrasée et froissée", "é+f")
        ecrire(x2 + pw2 - 218, yy - 3, f"{z['memoire']:.4f}  {court} · bruit {z['bruit']:g}",
               petit, coul)
    ecrire(x2 + 14, y2 + 14, "en orange : AUCUNE cause. en vert : une ou deux.", petit, GRIS)

    # ── Bas droite : la séparation, règle par règle ─────────────────────────
    x3, y3, pw3, ph3 = 700, 490, L - 700 - 60, 280
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "l'écart entre matières contre la dispersion dans une", moyen, ENCRE)
    bruits = [y["bruit"] for y in pv[0]["par_bruit"]]
    for i, b in enumerate(bruits):
        ecrire(x3 + 200 + i * 128, y3 + 16, f"bruit {b:g}", petit, GRIS)
    yy = y3 + 42
    for i, x in enumerate(pv):
        ecrire(x3 + 14, yy, x["nom"], petit, COUL[i % len(COUL)])
        for k, y in enumerate(x["par_bruit"]):
            ax = x3 + 194 + k * 128
            art.rectangle([ax, yy - 2, ax + 116, yy + 14],
                          fill=(AVEC if y["la_lecture_separe"] else BANDE))
            points.append((ax, yy))
            ecrire(ax + 6, yy, f"{y['ecart_entre_matieres']:.3f}/"
                               f"{y['dispersion_dans_une_matiere']:.3f}", petit,
                   FOND if y["la_lecture_separe"] else ENCRE)
        yy += 30
    ecrire(x3 + 14, yy + 10, "en vert, la lecture sépare encore les causes.", petit, GRIS)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 792
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    p_ = o["la_pire"]
    absolue = next(x for x in pv if x["enroulement"])
    brute = next(x for x in pv if not x["corrige"] and not x["enroulement"])
    ecrire(44, by0 + 10, f"✗ aucun seuil ABSOLU ne sépare les causes : {o['inversions']} "
                         f"inversions sur {o['lectures']} lectures — « {p_['sans_cause']} » à bruit "
                         f"{p_['bruit_sans_cause']:g} lit {p_['lecture_sans']:.4f} quand "
                         f"« {p_['avec_cause']} » à bruit {p_['bruit_avec_cause']:g} lit "
                         f"{p_['lecture_avec']:.4f}.",
           moyen, ENCRE)
    ecrire(44, by0 + 34, f"⚠ et la référence absolue que le suiveur possède — l'enroulement, "
                         f"avance sur rayon — ne suffit pas : "
                         f"{absolue['la pince']['reussites']} réussites contre "
                         f"{brute['la pince']['reussites']}.", petit, ENCRE)
    ecrire(44, by0 + 52, f"⚠ la raison est lisible en haut à gauche : sur la spirale ÉCRASÉE elle "
                         f"lit {_lue(g, absolue, 0.0, 'spirale écrasée'):.4f} quand les règles de "
                         f"cohérence lisent "
                         f"{_lue(g, brute, 0.0, 'spirale écrasée'):.4f}. L'écrasement excède "
                         f"l'enroulement, et c'est pourtant la forme qu'il faut suivre.",
           petit, ENCRE)
    ecrire(44, by0 + 74, "⚠ ce qui manque est donc de distinguer ce qui excède l'enroulement de "
                         "façon COHÉRENTE, qu'il faut suivre, de ce qui l'excède sans cohérence, "
                         "qu'il faut supprimer.", petit, ENCRE)

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

    src = RACINE / "docs" / "mesures" / "un_suiveur_na_rien_a_quoi_se_comparer.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        j = d["juger"]
        rouge = json.loads(json.dumps(d))
        rouge["juger"]["les_temoins_internes"]["le_protocole_est_le_meme"] = False
        court = json.loads(json.dumps(d))
        court["juger"]["par_variante"] = court["juger"]["par_variante"][:2]
        for nom, contenu in (
                ("message", {"message": "précédent absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("témoins ROUGES", rouge),
                ("deux règles seulement", court),
                ("obstacle indécidable", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True,
                    "les_temoins_internes": j["les_temoins_internes"],
                    "les_lectures_se_recouvrent": {"decidable": False},
                    "par_variante": j["par_variante"]}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        v("la lecture d'une case retrouve la bonne règle et la bonne matière",
          _lue(d["sur_la_grille"], j["par_variante"][0], 0.0, "spirale nue") is not None
          and _lue(d["sur_la_grille"], j["par_variante"][0], 0.0, "inexistante") is None)

        sortie = tmp / "146.png"
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
        attendus = (len(j["par_variante"]) * 5 + len(j["par_variante"])
                    + j["les_lectures_se_recouvrent"]["lectures"]
                    + len(j["par_variante"]) * len(j["par_variante"][0]["par_bruit"]))
        v("il y a de quoi regarder ce que la mesure contient", len(points) >= attendus,
          f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "146_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["les_lectures_se_recouvrent"]["inversions"] = 999
        troisieme = tmp / "146_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/un_suiveur_na_rien_a_quoi_se_comparer.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/146_un_suiveur_na_rien_a_quoi_se_comparer.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
