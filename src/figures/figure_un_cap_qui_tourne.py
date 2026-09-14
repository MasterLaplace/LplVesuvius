#!/usr/bin/env python3
"""Un cap qui tourne — ce qu'il fait marcher, de combien il tourne, et où ça change.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le seul verdict : les réussites de
la pince, règle par règle, contre la barre du cap statique. En haut à droite, la garde qui empêche le
faux — le taux RÉELLEMENT employé, avec l'enroulement tracé en référence : un cap annoncé tournant
dont la barre serait nulle serait un cap statique déguisé. En bas à gauche, OÙ ça change : les
réussites matière par matière, la ligne de `140` marquée. En bas à droite, ce que chaque règle sait
encore lire sous le bruit.

  uv run python src/figures/figure_un_cap_qui_tourne.py \\
      --json docs/mesures/un_cap_qui_tourne.json \\
      --sortie docs/images/147_un_cap_qui_tourne.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)
from la_pince_tient_elle_la_feuille import (AVANCE_EN_LONGUEUR_DONDE,  # noqa: E402
                                            LONGUEUR_DONDE_UM, RAYON_MM)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
STATIQUE = (140, 143, 148)
TOURNANT = (60, 110, 90)
ALERTE = (176, 92, 42)

# ⚠ L'enroulement n'est PAS écrit en dur : il est dérivé des constantes du module partagé, comme
# dans la batterie du producteur. Un nombre posé ici redeviendrait faux dès qu'une constante bouge.
ENROULEMENT = (AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM) / (RAYON_MM * 1000.0)


def lire(chemin: Path) -> dict:
    """Le JSON de `un_cap_qui_tourne.py`.

    ⚠⚠ Refuse une mesure dont les TÉMOINS INTERNES ne sont pas verts : ils sont la preuve que le
    module partagé n'a pas bougé en gagnant le cap tournant, et sans eux rien de cette image ne vaut.
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
        raise ValueError(f"{chemin} : les témoins internes sont ROUGES, le module partagé a bougé")
    c = j.get("le_cap_tourne_t_il", {})
    if not c.get("decidable"):
        raise ValueError(f"{chemin} : le verdict du cap tournant est indécidable")
    if not c.get("toutes_tournent_vraiment"):
        raise ValueError(f"{chemin} : un cap annoncé tournant ne tourne pas")
    if len(j.get("par_variante", [])) < 3:
        raise ValueError(f"{chemin} : il faut au moins trois règles à comparer")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
            .replace("cap statique", "statique").replace("tournant à l'", "→ ")
            .replace("tournant au ", "→ "))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1340, 900
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    g, j = d["sur_la_grille"], d["juger"]
    pv, c_ = j["par_variante"], j["le_cap_tourne_t_il"]
    st = c_["le_statique"]
    ecrire(28, 20, "Un cap qui tourne", gros, ENCRE)
    ecrire(28, 46, f"fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour · témoins "
                   f"internes verts : `144` et `145` se reproduisent à travers le module partagé "
                   f"· enroulement dérivé {ENROULEMENT:.6f} rad par pas", petit, GRIS)

    def couleur(x):
        return TOURNANT if x.get("cap") else STATIQUE

    # ── Haut gauche : le seul verdict ───────────────────────────────────────
    x0, y0, pw, ph = 60, 122, 600, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "réussites de la pince, par règle", moyen, ENCRE)
    hi = max(x["la pince"]["reussites"] for x in pv) * 1.10
    pas_y = (ph - 70) / max(len(pv), 1)

    def bx(v):
        return x0 + 200 + (float(v) / hi) * (pw - 250)

    for i, x in enumerate(pv):
        yy = y0 + 24 + i * pas_y
        art.rectangle([x0 + 200, yy, bx(x["la pince"]["reussites"]), yy + 18], fill=couleur(x))
        points.append((bx(x["la pince"]["reussites"]), yy))
        ecrire(x0 + 10, yy + 2, _court(x["nom"]), petit, couleur(x))
        ecrire(int(bx(x["la pince"]["reussites"])) + 6, yy + 2,
               f"{x['la pince']['reussites']}", petit, couleur(x))
    # ⚠ La barre n'est pas une décoration : c'est le témoin de `144`, la seule chose à battre.
    bar = bx(st["reussites_de_la_pince"])
    art.line([bar, y0 + 18, bar, y0 + ph - 44], fill=ALERTE, width=2)
    ecrire(x0 + 10, y0 + ph - 38,
           f"la barre est le cap statique de `144` : {st['reussites_de_la_pince']} réussites",
           petit, ALERTE)
    ecrire(x0 + 10, y0 + ph - 20, "en vert les caps qui tournent, en gris ceux qui ne tournent pas",
           petit, GRIS)

    # ── Haut droite : de combien ils tournent ───────────────────────────────
    x1, y1, pw1, ph1 = 700, 122, L - 700 - 60, 300
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "le taux RÉELLEMENT employé, en radians par pas", moyen, ENCRE)
    taux = [abs(x["la pince"]["taux_median_rad"] or 0.0) for x in pv]
    hi1 = max(max(taux), ENROULEMENT) * 1.35

    def tx(v):
        return x1 + 190 + (float(v) / hi1) * (pw1 - 250)

    for i, x in enumerate(pv):
        yy = y1 + 24 + i * pas_y
        t_ = abs(x["la pince"]["taux_median_rad"] or 0.0)
        art.rectangle([x1 + 190, yy, max(tx(t_), x1 + 191), yy + 18], fill=couleur(x))
        points.append((tx(t_), yy))
        ecrire(x1 + 10, yy + 2, _court(x["nom"]), petit, couleur(x))
        ecrire(int(tx(t_)) + 6, yy + 2, f"{t_:.6f}", petit, couleur(x))
    ref = tx(ENROULEMENT)
    art.line([ref, y1 + 18, ref, y1 + ph1 - 44], fill=ALERTE, width=2)
    ecrire(x1 + 10, y1 + ph1 - 38, f"la barre est l'enroulement, {ENROULEMENT:.6f} rad par pas",
           petit, ALERTE)
    ecrire(x1 + 10, y1 + ph1 - 20,
           "un cap annoncé tournant dont la barre serait nulle serait un statique déguisé",
           petit, GRIS)

    # ── Bas gauche : ce que le solde a COÛTÉ ───────────────────────────────
    x2, y2, pw2, ph2 = 60, 490, 600, 280
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "le MÊME départ sous les deux règles", moyen, ENCRE)
    ap = [x for x in j.get("apparie_au_statique", []) if x.get("decidable")]
    hi2 = max([max(x["gains"], x["pertes"]) for x in ap] + [1]) * 1.25
    mil = x2 + 300

    def gx(v):
        return mil + (float(v) / hi2) * (pw2 - 330) * 0.5

    art.line([mil, y2 + 34, mil, y2 + ph2 - 56], fill=TRAIT, width=1)
    ecrire(mil - 52, y2 + 14, "perdues", petit, ALERTE)
    ecrire(mil + 8, y2 + 14, "gagnées", petit, TOURNANT)
    for i, x in enumerate(ap):
        yy = y2 + 46 + i * 56
        ecrire(x2 + 10, yy - 16, _court(x["nom"]), petit, TOURNANT)
        art.rectangle([gx(-x["pertes"]), yy, mil, yy + 16], fill=ALERTE)
        art.rectangle([mil, yy, gx(x["gains"]), yy + 16], fill=TOURNANT)
        points.append((gx(-x["pertes"]), yy))
        points.append((gx(x["gains"]), yy))
        ecrire(int(gx(-x["pertes"])) - 16, yy + 1, f"{x['pertes']}", petit, ALERTE)
        ecrire(int(gx(x["gains"])) + 6, yy + 1,
               f"{x['gains']}   solde {x['solde']:+d}", petit, TOURNANT)
    ecrire(x2 + 10, y2 + ph2 - 44, f"{ap[0]['paires']} départs appariés — même matière, même "
                                   f"bruit, même angle", petit, GRIS)
    ecrire(x2 + 10, y2 + ph2 - 26,
           "un solde positif obtenu en perdant ailleurs n'ajoute rien, il DÉPLACE", petit, ALERTE)

    # ── Bas droite : ce que chaque règle lit encore ─────────────────────────
    x3, y3, pw3, ph3 = 700, 490, L - 700 - 60, 280
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "l'écart entre matières contre la dispersion dans une", moyen, ENCRE)
    for i, b in enumerate([y["bruit"] for y in pv[0]["par_bruit"]]):
        ecrire(x3 + 196 + i * 128, y3 + 12, f"bruit {b:g}", petit, GRIS)
    yy = y3 + 36
    for x in pv:
        ecrire(x3 + 10, yy, _court(x["nom"]), petit, couleur(x))
        for k, y in enumerate(x["par_bruit"]):
            ax = x3 + 190 + k * 128
            art.rectangle([ax, yy - 2, ax + 116, yy + 14],
                          fill=(TOURNANT if y["la_lecture_separe"] else BANDE))
            points.append((ax, yy))
            ecrire(ax + 6, yy, f"{y['ecart_entre_matieres']:.3f}/"
                               f"{y['dispersion_dans_une_matiere']:.3f}", petit,
                   FOND if y["la_lecture_separe"] else ENCRE)
        yy += 30
    ecrire(x3 + 10, yy + 8, "en vert, la lecture sépare encore les causes.", petit, GRIS)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 792
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    meilleure = next(y for y in c_["par_regle"] if y["nom"] == c_["la_meilleure"])
    gagne = c_["un_cap_qui_tourne_bat_le_statique"]
    pire = min(c_["par_regle"], key=lambda y: y["solde"] if y["solde"] is not None else 0)
    ecrire(44, by0 + 10,
           f"{'★' if gagne else '✗'} un cap qui TOURNE bat-il le cap statique ? {gagne} — "
           f"« {_court(c_['la_meilleure'])} » rend {meilleure['reussites_de_la_pince']} contre "
           f"{st['reussites_de_la_pince']}, mais {meilleure['gains']} gagnées pour "
           f"{meilleure['pertes']} perdues : elle DÉPLACE.", moyen, ENCRE)
    ecrire(44, by0 + 34,
           f"⚠⚠ et un cap qui tourne au taux qu'il LIT est franchement nuisible — "
           f"« {_court(pire['nom'])} » : {pire['gains']} gagnées pour {pire['pertes']} perdues, "
           f"solde {pire['solde']:+d}. Un cap existe pour être indépendant de la lecture.",
           petit, ENCRE)
    ecrire(44, by0 + 52,
           f"⚠ les trois caps tournants tournent vraiment (taux médian "
           f"{abs(meilleure['taux_median_rad']):.6f} rad par pas contre "
           f"{abs(st['taux_median_rad'] or 0.0):.6f} pour le statique, pour un enroulement de "
           f"{ENROULEMENT:.6f}) : ce n'est pas un statique déguisé.", petit, ENCRE)
    ecrire(44, by0 + 74,
           f"⚠ la barre de `140` — la matière du rouleau — reste au sol : "
           f"{meilleure['sur_la_matiere_de_140']} réussite(s) pour la meilleure, "
           f"{st['sur_la_matiere_de_140']} pour le statique.", petit, ENCRE)

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

    src = RACINE / "docs" / "mesures" / "un_cap_qui_tourne.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    v("⚠ l'enroulement de la figure est DÉRIVÉ des constantes, jamais posé",
      abs(ENROULEMENT - (AVANCE_EN_LONGUEUR_DONDE * LONGUEUR_DONDE_UM) / (RAYON_MM * 1000.0))
      < 1e-15, f"{ENROULEMENT:.6f} rad par pas")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        j = d["juger"]
        rouge = json.loads(json.dumps(d))
        rouge["juger"]["les_temoins_internes"]["le_protocole_est_le_meme"] = False
        fige = json.loads(json.dumps(d))
        fige["juger"]["le_cap_tourne_t_il"]["toutes_tournent_vraiment"] = False
        court = json.loads(json.dumps(d))
        court["juger"]["par_variante"] = court["juger"]["par_variante"][:2]
        for nom, contenu in (
                ("message", {"message": "précédent absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("témoins ROUGES", rouge),
                ("cap tournant qui ne tourne pas", fige),
                ("deux règles seulement", court),
                ("verdict indécidable", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True,
                    "les_temoins_internes": j["les_temoins_internes"],
                    "le_cap_tourne_t_il": {"decidable": False},
                    "par_variante": j["par_variante"]}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "147.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 5,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1340)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g_ for _x, _y, t_, _f in poses for g_ in glyphes_manquants(t_)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1340 and 0 <= y <= 900 for x, y in points), f"{len(points)} points")
        n_ = len(j["par_variante"])
        attendus = (2 * n_ + 2 * len([x for x in j["apparie_au_statique"] if x["decidable"]])
                    + n_ * len(j["par_variante"][0]["par_bruit"]))
        v("il y a de quoi regarder ce que la mesure contient", len(points) >= attendus,
          f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "147_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        # ⚠ La sonde déplace un nombre que la bande LIT vraiment : elle a d'abord bougé un champ
        # devenu inutile et passait donc sans rien prouver.
        for y in d2["juger"]["le_cap_tourne_t_il"]["par_regle"]:
            y["pertes"] = (y["pertes"] or 0) + 7
        troisieme = tmp / "147_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/un_cap_qui_tourne.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/147_un_cap_qui_tourne.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
