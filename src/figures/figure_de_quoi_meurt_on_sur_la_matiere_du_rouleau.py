"""De quoi meurt-on sur la matière du rouleau, maintenant que le mur a reculé ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les trois comptes qui ne tombent
pas ensemble : boucler le tour, revenir sur la feuille, réussir. En haut à droite, le piège — chaque
compte de feuilles porté par la part du tour qui le rend lisible, et l'instrument qui en compte le
plus est celui dont les marches ont le moins bougé. En bas à gauche, de quoi on meurt. En bas à
droite, où les tours se bouclent, bruit par bruit, et de combien de feuilles ils ratent.

  uv run python src/figures/figure_de_quoi_meurt_on_sur_la_matiere_du_rouleau.py \\
      --json docs/mesures/de_quoi_meurt_on_sur_la_matiere_du_rouleau.json \\
      --sortie docs/images/158_de_quoi_meurt_on_sur_la_matiere_du_rouleau.png
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
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
TEMOIN = (150, 152, 156)


def lire(chemin: Path) -> dict:
    """Le JSON de `de_quoi_meurt_on_sur_la_matiere_du_rouleau.py`.

    ⚠⚠ Refuse une mesure sans le couple feuilles/part du tour : c'est lui qui rend les comptes
    lisibles, et une figure qui dessinerait les feuilles seules dirait exactement le contraire de ce
    que cette tranche mesure.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("le_verdict"):
        raise ValueError(f"{chemin} : le verdict est vide")
    if not j.get("le_compte_de_feuilles_recompense_limmobilite"):
        raise ValueError(f"{chemin} : le couple feuilles / part du tour est absent")
    if not j.get("par_bruit"):
        raise ValueError(f"{chemin} : le partage par bruit est absent")
    return d


def _bref(nom: str) -> str:
    return (nom.replace("la pince de ", "").replace("la croix et le rejet", "croix+rejet")
            .replace("la croix ", "croix ").replace("le rejet ", "rejet "))


def _bras(nom: str) -> str:
    return {"une machoire": "seule", "deux machoires libres": "libre",
            "la pince": "pince"}.get(nom, nom)


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1360, 960
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    j = d["juger"]
    ver = j["le_verdict"]
    im = j["le_compte_de_feuilles_recompense_limmobilite"]

    ecrire(28, 20, "De quoi meurt-on sur la matière du rouleau, maintenant que le mur a reculé ?",
           gros, ENCRE)
    ecrire(28, 46, f"la grille de `156` RELUE sur la seule matière écrasée à "
                   f"{d['matiere']['ecrasement']} et froissée à "
                   f"{d['matiere']['amplitude_um']:g} µm — {d['departs']} départs × "
                   f"{len(d['bruits'])} bruits, un tour, fenêtre {d['fenetre']}", petit, GRIS)

    # ---- panneau 1 : les trois comptes
    x0, y0, pw, ph = 56, 122, 620, 322
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "trois comptes qui ne tombent pas ensemble", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 8, f"{'instrument':<14}{'bras':>7}{'déc.':>6}{'tours':>7}"
                            f"{'feuilles':>10}{'jointes':>9}", petit, GRIS)
    tmax = max(x["tours_boucles"] for x in ver) or 1
    x_barre = x0 + 396
    barre_max = pw - 420
    # ⚠⚠ L'INTERLIGNE SE DÉRIVE DE LA PLACE, il ne se pose pas : un interligne posé redevient
    # faux au premier instrument ajouté, et il l'est devenu au douzième bras ici.
    pas_ligne = max(12, (ph - 84) // max(len(ver), 1))
    for k, x in enumerate(ver):
        yy = y0 + 28 + k * pas_ligne
        coul = BON if x["la_mort_a_change_de_nature"] else ENCRE
        ecrire(x0 + 12, yy, f"{_bref(x['instrument']):<14}{_bras(x['bras']):>7}"
                            f"{x['decidables']:>6}{x['tours_boucles']:>7}"
                            f"{x['memes_feuilles']:>10}{x['reussites_jointes']:>9}", petit, coul)
        if x["tours_boucles"]:
            w = (x["tours_boucles"] / tmax) * barre_max
            art.rectangle([x_barre, yy + 1, x_barre + w, yy + 10], fill=BON)
            points.append((x_barre + w, yy + 5))
    ecrire(x0 + 12, y0 + ph - 46,
           "vert : un tour BOUCLÉ là où aucun ne se bouclait — la mort a changé de nature",
           petit, BON)
    ecrire(x0 + 12, y0 + ph - 30,
           "seule une mâchoire SEULE y arrive, et seulement avec le rejet", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 14,
           "la pince et la paire libre : ZÉRO tour sous les quatre instruments", petit, ALERTE)

    # ---- panneau 2 : le compte recompense l'immobilite
    x0, y0, pw, ph = 712, 122, 592, 322
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "« même feuille » : le compte, et ce qu'il a parcouru", moyen, ENCRE)
    pts = [(x["part_du_tour_des_memes_feuilles"], x["memes_feuilles"], x)
           for x in ver if x["part_du_tour_des_memes_feuilles"] is not None]
    pmax = max(p for p, _n, _x in pts) or 1.0
    nmax = max(n for _p, n, _x in pts) or 1
    gx0, gy0, gw, gh = x0 + 56, y0 + 24, pw - 110, ph - 140
    art.line([gx0, gy0 + gh, gx0 + gw, gy0 + gh], fill=TRAIT, width=1)
    art.line([gx0, gy0, gx0, gy0 + gh], fill=TRAIT, width=1)
    for p, n, x in pts:
        px = gx0 + (p / pmax) * gw
        py = gy0 + gh - (n / nmax) * gh
        coul = BON if x["la_mort_a_change_de_nature"] else (
            ALERTE if x["bras"] == "la pince" else GRIS)
        art.ellipse([px - 4, py - 4, px + 4, py + 4], fill=coul)
        points.append((px, py))
    for i in range(3):
        val = pmax * i / 2
        ecrire(int(gx0 + (val / pmax) * gw) - 14, gy0 + gh + 6, f"{val:.3f}", petit, GRIS)
    for i in range(3):
        n = int(nmax * i / 2)
        ecrire(x0 + 12, int(gy0 + gh - (n / nmax) * gh) - 7, f"{n:>3d}", petit, GRIS)
    ecrire(x0 + 12, gy0 - 16, "marches « même feuille »", petit, GRIS)
    ecrire(gx0, gy0 + gh + 22, "part du tour parcourue par ces marches-là", petit, GRIS)
    y_ = y0 + ph - 74
    for bras, z in sorted(im.items()):
        ecrire(x0 + 12, y_, f"{_bras(bras):>6} : le plus de feuilles « {_bref(z['plus_de_feuilles'])} »"
                            f" {z['ses_feuilles']} à {z['sa_part_du_tour']}", petit,
               ALERTE if z["ce_ne_sont_pas_les_memes"] else ENCRE)
        y_ += 14
        ecrire(x0 + 12, y_, f"{'':>6}   va le plus loin « {_bref(z['va_le_plus_loin'])} » "
                            f"{z['ses_feuilles_a_lui']} à {z['sa_part_a_lui']}", petit, GRIS)
        y_ += 16

    # ---- panneau 3 : de quoi on meurt
    x0, y0, pw, ph = 56, 500, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "de quoi on meurt — la pose, ou la contrainte ?", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 8, f"{'instrument':<14}{'bras':>7}{'arrêts':>9}{'pose ✗':>9}"
                            f"{'contr.':>8}{'pas':>8}", petit, GRIS)
    pas_ligne = max(12, (ph - 80) // max(len(ver), 1))
    for k, x in enumerate(ver):
        yy = y0 + 28 + k * pas_ligne
        coul = ALERTE if x["elle_meurt_toujours_darret"] else BON
        ecrire(x0 + 12, yy,
               f"{_bref(x['instrument']):<14}{_bras(x['bras']):>7}"
               f"{x['arrets']:>6}/{x['decidables']:<3}{x['poses_refusees_mediane']:>8}"
               f"{x['refus_de_contrainte']:>8}{x['pas_median']:>8}", petit, coul)
    ecrire(x0 + 12, y0 + ph - 44,
           "ambre : TOUTES les marches décidables meurent d'arrêt · vert : plus toutes", petit,
           GRIS)
    ecrire(x0 + 12, y0 + ph - 28,
           "la pose refuse, la contrainte presque jamais — c'est l'énoncé de `149`, toujours vrai",
           petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 12,
           "et le rejet fait marcher la pince 2,571 fois plus loin sans la faire survivre",
           petit, ALERTE)

    # ---- panneau 4 : ou les tours se bouclent
    x0, y0, pw, ph = 712, 500, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "où les tours se bouclent — une mâchoire seule", moyen, ENCRE)
    lignes = j["par_bruit"]
    bmax = max(y["decidables"] for x in lignes for y in x["par_bruit"]) or 1
    x_nom, x_barre = x0 + 12, x0 + 150
    barre_max = pw - 300
    for k, x in enumerate(lignes):
        yy = y0 + 26 + k * 56
        ecrire(x_nom, yy + 12, _bref(x["nom"]), petit, ENCRE)
        for i, y in enumerate(x["par_bruit"]):
            w = (y["tours_boucles"] / bmax) * barre_max
            wt = (y["decidables"] / bmax) * barre_max
            art.rectangle([x_barre, yy + i * 15, x_barre + wt, yy + i * 15 + 12], fill=TRAIT)
            if w > 0:
                art.rectangle([x_barre, yy + i * 15, x_barre + w, yy + i * 15 + 12], fill=BON)
                points.append((x_barre + w, yy + i * 15 + 6))
            ecrire(x_barre + barre_max + 10, yy + i * 15 + 1,
                   f"bruit {y['bruit']:>2g} : {y['tours_boucles']}/{y['decidables']}", petit,
                   BON if y["tours_boucles"] else GRIS)
    seuls = [x for x in ver if x["derive_des_tours_boucles"] is not None]
    ecrire(x0 + 12, y0 + ph - 60,
           "gris : les marches décidables · vert : celles qui BOUCLENT le tour", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 44,
           "zéro au bruit 0 : le rejet travaille contre le BRUIT DE LECTURE (`156`)", petit, ENCRE)
    for i, x in enumerate(seuls):
        ecrire(x0 + 12, y0 + ph - 28 + i * 14,
               f"et ces tours ratent la feuille : dérive médiane "
               f"{x['derive_des_tours_boucles']} feuilles sous « {_bref(x['instrument'])} »",
               petit, ALERTE)

    # ---- bande de conclusion
    y = 822
    art.rectangle([56, y, L - 56, y + 112], fill=BANDE)
    cadres.append((56, y, L - 56, y + 112))
    r_ = next(x for x in ver if x["la_mort_a_change_de_nature"])
    t_ = next(x for x in ver if x["instrument"].startswith("la pince de") and x["bras"] == "la pince")
    z_ = im["la pince"]
    ecrire(74, y + 12,
           f"★★★★  La mort a changé de NATURE pour un seul bras : une mâchoire seule avec le rejet "
           f"boucle {r_['tours_boucles']} tours sur {r_['decidables']}, là où AUCUN ne se bouclait "
           f"depuis `142`.", moyen, BON)
    ecrire(74, y + 38,
           f"✗  Mais ces tours ratent la feuille de {r_['derive_des_tours_boucles']} feuilles en "
           f"médiane, et {r_['reussites_jointes']} seule réussite est JOINTE. Le tour n'est plus le "
           f"mur : la FEUILLE l'est.", moyen, ENCRE)
    ecrire(74, y + 64,
           f"⚠  La pince, elle, meurt de la même mort : {t_['arrets']}/{t_['decidables']} arrêts "
           f"avant comme après, avec PLUS de poses refusées et 2,571 fois plus de pas.", moyen,
           ALERTE)
    ecrire(74, y + 88,
           f"⚠⚠  Et « revenir sur la même feuille » récompense l'IMMOBILITÉ : "
           f"{z_['ses_feuilles']} marches à {z_['sa_part_du_tour']} de tour contre "
           f"{z_['ses_feuilles_a_lui']} à {z_['sa_part_a_lui']}.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 960), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    for x in faux["juger"]["le_verdict"]:
        if x["la_mort_a_change_de_nature"]:
            x["derive_des_tours_boucles"] = 88.88
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer la dérive des tours bouclés change ce que la bande DIT",
      any("88.88" in t for _x, _y, t, _f in p2)
      and not any("88.88" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["le_compte_de_feuilles_recompense_limmobilite"]["la pince"]["sa_part_du_tour"] \
        = 0.7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et la part du tour des « mêmes feuilles » est LUE, pas supposée",
      any("0.7777" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    for x in faux3["juger"]["par_bruit"]:
        for y in x["par_bruit"]:
            y["tours_boucles"] = 99
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐ ... et le partage par bruit aussi",
      any("99/" in t for _x, _y, t, _f in p4))

    sans = copy.deepcopy(d)
    del sans["juger"]["le_compte_de_feuilles_recompense_limmobilite"]
    tmp = sortie.parent / "_sans_couple_158.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans le couple feuilles / part du tour est REFUSÉE, jamais dessinée à moitié",
      ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "de_quoi_meurt_on_sur_la_matiere_du_rouleau.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "158_de_quoi_meurt_on_sur_la_matiere_du_rouleau.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
