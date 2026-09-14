"""La croix marche-t-elle le tour ? — la première grille depuis `142` qui paie un instrument réparé.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, ce que chaque instrument fait au
tour : réussites et arrêts, contre la barre de `144`. En haut à droite, le panneau décisif — le
MÊME départ sous les deux règles, apparié à CHAQUE niveau de bruit, parce que c'est là que la
victoire est jointe et là qu'elle cesse de l'être. En bas à gauche, où le gain vit : matière par
matière, et la matière du rouleau qui reste au sol. En bas à droite, le prix — la croix coûte
exactement deux barres et le rejet ne coûte rien.

  uv run python src/figures/figure_la_croix_marche_t_elle_le_tour.py \\
      --json docs/mesures/la_croix_marche_t_elle_le_tour.json \\
      --sortie docs/images/156_la_croix_marche_t_elle_le_tour.png
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
    """Le JSON de `la_croix_marche_t_elle_le_tour.py`.

    ⚠⚠ Refuse une mesure sans son témoin interne : les quatre panneaux se lisent contre la barre de
    `144`, et une figure dessinée sans la preuve que cette barre se reproduit ressemble exactement à
    une figure dessinée avec.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("le_temoin_interne", {}).get("decidable"):
        raise ValueError(f"{chemin} : le témoin interne est indécidable")
    if not j.get("le_verdict", {}).get("decidable"):
        raise ValueError(f"{chemin} : le verdict est indécidable")
    if not j.get("le_gain_par_bruit", {}).get("par_bruit"):
        raise ValueError(f"{chemin} : le gain par bruit est absent")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr"))


def _bref(nom: str) -> str:
    return nom.replace("la pince de ", "").replace("la croix et le rejet", "croix+rejet") \
              .replace("la croix ", "croix ").replace("le rejet ", "rejet ")


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1360, 940
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
    pv, ver = j["par_variante"], j["le_verdict"]
    tin = j["le_temoin_interne"]
    temoin = ver["le_temoin"]

    ecrire(28, 20, "La croix marche-t-elle le tour ? La première grille depuis `142` "
                   "qui paie un instrument réparé", gros, ENCRE)
    ecrire(28, 46, f"{len(g['cases'])} cases · {g['departs']} départs par case · un tour · "
                   f"fenêtre du cap {g['fenetre']} (`144`) — témoin interne : "
                   f"{tin['par_bras']['la pince']['ici']} réussites et {tin['arrets_ici']} arrêts, "
                   f"contre {tin['par_bras']['la pince']['dans_147']} et "
                   f"{tin['arrets_dans_147']} dans `147`", petit,
           BON if tin["le_protocole_est_le_meme"] else ALERTE)

    # ---- panneau 1 : reussites et arrets par instrument
    x0, y0, pw, ph = 56, 122, 620, 292
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que chaque instrument fait au tour", moyen, ENCRE)
    rmax = max(x["la pince"]["reussites"] for x in pv) or 1
    # ⚠ Les colonnes d'etiquettes sont RESERVEES a droite des barres : une etiquette ecrite apres
    # une barre sans reserve sort du cadre des que la barre s'allonge.
    x_nom, x_barre = x0 + 14, x0 + 146
    barre_max = pw - 300
    for k, x in enumerate(pv):
        p = x["la pince"]
        yy = y0 + 30 + k * 62
        coul = TEMOIN if k == 0 else (BON if p["reussites"] > temoin["reussites_de_la_pince"]
                                      else ALERTE)
        w = (p["reussites"] / rmax) * barre_max
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 15], fill=coul)
        points.append((x_barre + w, yy + 7))
        wa = (p["arrets"] / rmax) * barre_max
        art.rectangle([x_barre, yy + 19, x_barre + max(wa, 1), yy + 30], fill=ALERTE)
        points.append((x_barre + wa, yy + 24))
        ecrire(x_nom, yy + 8, _bref(x["nom"]), petit, ENCRE)
        ecrire(x_barre + barre_max + 10, yy + 1, f"{p['reussites']:>3d} réussites", petit, coul)
        ecrire(x_barre + barre_max + 10, yy + 19, f"{p['arrets']:>3d} arrêts", petit, ALERTE)
    xb = x_barre + (temoin["reussites_de_la_pince"] / rmax) * barre_max
    art.line([xb, y0 + 24, xb, y0 + ph - 40], fill=ENCRE, width=1)
    ecrire(x0 + 14, y0 + ph - 32,
           f"le trait : la barre de `144`, {temoin['reussites_de_la_pince']} réussites · "
           f"ambre bas : les marches ARRÊTÉES, l'énoncé séparé de `149`", petit, GRIS)

    # ---- panneau 2 : l'appariement, bruit par bruit
    x0, y0, pw, ph = 712, 122, 592, 292
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le MÊME départ sous les deux règles, à chaque bruit", moyen, ENCRE)
    lignes = j["le_gain_par_bruit"]["par_bruit"]
    gmax = max(max(abs(y["gains"] or 0), abs(y["pertes"] or 0))
               for x in lignes for y in x["par_instrument"]) or 1
    x_zero = x0 + 250
    demi = 130
    art.line([x_zero, y0 + 20, x_zero, y0 + ph - 42], fill=TRAIT, width=1)
    k = 0
    for x in lignes:
        for y in x["par_instrument"]:
            yy = y0 + 24 + k * 22
            wg = ((y["gains"] or 0) / gmax) * demi
            wp = ((y["pertes"] or 0) / gmax) * demi
            if wg > 0:
                art.rectangle([x_zero, yy, x_zero + wg, yy + 12], fill=BON)
                points.append((x_zero + wg, yy + 6))
            if wp > 0:
                art.rectangle([x_zero - wp, yy, x_zero, yy + 12], fill=ALERTE)
                points.append((x_zero - wp, yy + 6))
            ecrire(x0 + 10, yy + 1, f"bruit {x['bruit']:>2g}  {_bref(y['nom']):<17}", petit, ENCRE)
            ecrire(x_zero + demi + 14, yy + 1,
                   f"{y['gains']:+d} / {-(y['pertes'] or 0):+d}   arrêts "
                   f"{y['arrets_du_temoin']}→{y['arrets']}", petit,
                   BON if not y["pertes"] and y["gains"] else GRIS)
            k += 1
    ecrire(x0 + 10, y0 + ph - 34,
           "vert : gagnées · ambre : PERDUES — une victoire est JOINTE, donc une seule barre",
           petit, GRIS)
    ecrire(x0 + 10, y0 + ph - 20,
           f"la meilleure gagne JOINTEMENT aux bruits "
           f"{ver['bruits_ou_la_meilleure_gagne_jointement']}, et nulle part ailleurs", petit,
           ENCRE)

    # ---- panneau 3 : ou le gain vit, matiere par matiere
    x0, y0, pw, ph = 56, 470, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "où le gain vit — 36 départs par matière", moyen, ENCRE)
    mats = [m["nom"] for m in pv[0]["par_matiere"]]
    par = {x["nom"]: {m["nom"]: m["la pince"] for m in x["par_matiere"]} for x in pv}
    vmax = max(v for x in par.values() for v in x.values()) or 1
    x_nom, x_barre = x0 + 14, x0 + 150
    barre_max = pw - 262
    for i, m in enumerate(mats):
        yy = y0 + 26 + i * 54
        ecrire(x_nom, yy + 12, _court(m), petit, ENCRE)
        for k, x in enumerate(pv):
            val = par[x["nom"]][m]
            w = (val / vmax) * barre_max
            coul = TEMOIN if k == 0 else (BON if val > par[pv[0]["nom"]][m]
                                          else (ALERTE if val < par[pv[0]["nom"]][m] else GRIS))
            art.rectangle([x_barre, yy + k * 8, x_barre + max(w, 1), yy + k * 8 + 6], fill=coul)
            points.append((x_barre + w, yy + k * 8 + 3))
        vals = [par[x["nom"]][m] for x in pv]
        ecrire(x_barre + barre_max + 10, yy + 12,
               " ".join(f"{v:>2d}" for v in vals), petit,
               ALERTE if max(vals) == 0 else ENCRE)
    ecrire(x0 + 14, y0 + ph - 32,
           "de haut en bas dans chaque groupe : `144`, croix, rejet, croix+rejet", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 18,
           "la matière du rouleau reste à ZÉRO sous les quatre instruments", petit, ALERTE)

    # ---- panneau 4 : le prix
    x0, y0, pw, ph = 712, 470, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le prix, et ce que chaque moitié achète", moyen, ENCRE)
    lref = temoin["lectures_medianes"] or 1
    lmax = max((x["la pince"]["lectures_medianes"] or 0) for x in pv) or 1
    x_nom, x_barre = x0 + 12, x0 + 146
    barre_max = pw - 300
    prix = {y["nom"]: y["prix"] for y in ver["par_instrument"]}
    for k, x in enumerate(pv):
        p = x["la pince"]
        yy = y0 + 30 + k * 46
        w = ((p["lectures_medianes"] or 0) / lmax) * barre_max
        gagne = p["reussites"] - temoin["reussites_de_la_pince"]
        coul = TEMOIN if k == 0 else (ALERTE if (p["lectures_medianes"] or 0) > 1.5 * lref
                                      else BON)
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
        points.append((x_barre + w, yy + 7))
        ecrire(x_nom, yy + 2, _bref(x["nom"]), petit, ENCRE)
        # ⚠ Le prix est LU du verdict, jamais recalcule ici : deux calculs d'un meme rapport
        # finiraient par ne pas s'accorder.
        px = prix.get(x["nom"])
        ecrire(x_barre + barre_max + 10, yy + 2,
               f"{'×1' if px is None else f'×{px:g}'}   {gagne:+d} réussites", petit, coul)
    ecrire(x0 + 12, y0 + ph - 96,
           f"la croix lit EXACTEMENT deux barres — ×{ver['le_prix_de_la_meilleure']:g} — et le "
           f"rejet ne coûte rien.", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 80,
           "lectures médianes : " + " · ".join(
               f"{_bref(x['nom'])} {x['la pince']['lectures_medianes']}" for x in pv), petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 112,
           "appuis écartés : " + " · ".join(
               f"{_bref(x['nom'])} {x['la pince']['appuis_rejetes']}" for x in pv
               if x["la pince"]["appuis_rejetes"]), petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 60,
           "la moitié CHÈRE ne paie pas sur une marche : la croix seule rend "
           f"{pv[1]['la pince']['reussites'] - temoin['reussites_de_la_pince']:+d} réussite pour "
           f"deux fois le prix,", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 44,
           f"et la moitié GRATUITE en rend "
           f"{pv[2]['la pince']['reussites'] - temoin['reussites_de_la_pince']:+d} pour rien.",
           petit, BON)

    # ---- bande de conclusion
    y = 790
    art.rectangle([56, y, L - 56, y + 122], fill=BANDE)
    cadres.append((56, y, L - 56, y + 122))
    m_ = next(k for k in ver["par_instrument"] if k["nom"] == ver["la_meilleure"])
    marque = "★★★★" if ver["un_instrument_repare_bat_le_temoin"] else "✗"
    ecrire(74, y + 12,
           f"{marque}  la victoire JOINTE de `147` n'est PAS acquise sur la grille entière : "
           f"« {_bref(ver['la_meilleure'])} » rend {m_['reussites_de_la_pince']} réussites contre "
           f"{temoin['reussites_de_la_pince']}, mais {m_['gains']} gagnées pour "
           f"{m_['pertes']} PERDUES.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★  Elle l'est aux bruits {ver['bruits_ou_la_meilleure_gagne_jointement']} — lus et "
           f"non choisis — et les {m_['pertes']} pertes sont TOUTES au bruit "
           f"{lignes[-1]['bruit']:g}, celui où `144`", moyen, BON)
    ecrire(74, y + 60, "        mesure que sa propre lecture cesse de séparer les causes.",
           moyen, BON)
    ecrire(74, y + 86,
           f"★★  Elle ARRÊTE moins — {m_['arrets_de_la_pince']} contre "
           f"{temoin['arrets_de_la_pince']} — ce que `149` et `150` faisaient attendre, et c'est "
           f"un énoncé SÉPARÉ. ✗ La barre de `140` reste au sol.", moyen, ENCRE)

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
    v("l'image est écrite et a la taille attendue", img.size == (1360, 940), f"{img.size}")
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
    faux["juger"]["le_verdict"]["le_temoin"]["reussites_de_la_pince"] = 77
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer la barre de `144` change ce que la bande DIT",
      any("77" in t for _x, _y, t, _f in p2) and not any("77" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["le_verdict"]["bruits_ou_la_meilleure_gagne_jointement"] = [3.0]
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et changer les bruits où la victoire est jointe aussi",
      any("[3.0]" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    faux3["juger"]["le_temoin_interne"]["arrets_dans_147"] = 999
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐ ... et le témoin interne est DIT en tête, pas supposé",
      any("999" in t for _x, _y, t, _f in p4))

    sans = copy.deepcopy(d)
    del sans["juger"]["le_temoin_interne"]
    tmp = sortie.parent / "_sans_temoin_156.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans témoin interne est REFUSÉE, jamais dessinée à moitié", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures" / "la_croix_marche_t_elle_le_tour.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "156_la_croix_marche_t_elle_le_tour.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
