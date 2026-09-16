"""La croix paie-t-elle quand le marcheur écoute ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les DEUX contrôles : rien ne va de
travers sur la spirale nue, et la croix y lit exactement le double PAR PAS. En haut à droite, ce que
les deux instruments livrent, bras par bras. En bas à gauche, ce que la croix récupère contre ce
qu'elle perd, matière par matière. En bas à droite, le PRIX — les lectures par pas, et les poses
qu'elle ne peut pas faire.

  uv run python src/figures/figure_la_croix_paie_t_elle_quand_on_ecoute.py \\
      --json docs/mesures/la_croix_paie_t_elle_quand_on_ecoute.json \\
      --sortie docs/images/168_la_croix_paie_t_elle_quand_on_ecoute.png
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
CONTRE = (92, 108, 150)

SEGMENT, CROIX = "en segment", "en croix"


def _fr(x: float, n: int = 4) -> str:
    """Un nombre comme le dépôt l'écrit : virgule décimale, jamais de décimale ajoutée."""
    return f"{x:.{n}f}".rstrip("0").rstrip(".").replace(".", ",") if x is not None else "—"


def lire(chemin: Path) -> dict:
    """Le JSON de `la_croix_paie_t_elle_quand_on_ecoute.py`.

    ⚠⚠ Refuse une mesure sans les DEUX contrôles, et sans le coût PAR PAS : un total de lectures
    ferait passer une croix qui meurt tôt pour une croix économe, ce qui est exactement le piège
    que `R4-F162` nomme.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    c = j.get("le_controle_de_la_spirale_nue", {})
    if c.get("il_est_propre") is None:
        raise ValueError(f"{chemin} : le contrôle de propreté est absent")
    if c.get("le_surcout_y_est_exactement_double") is None:
        raise ValueError(f"{chemin} : le contrôle du surcoût exact est absent")
    for g in j["par_bras"]:
        for m in (SEGMENT, CROIX):
            if g.get(m, {}).get("lectures_par_pas") is None:
                raise ValueError(f"{chemin} : le coût PAR PAS est absent de {g['nom']}")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    j = d["juger"]
    bras, mat, tout = j["par_bras"], j["par_matiere"], j["tout"]
    c = j["le_controle_de_la_spirale_nue"]

    ecrire(28, 20, "La croix paie-t-elle quand le marcheur ÉCOUTE ? — elle coûte le double "
                   "et livre moins", gros, ENCRE)
    ecrire(28, 46, "`156` l'avait jugée sur un marcheur SOURD, avant que `162`–`165` ne lui "
                   "apprennent à écouter et à se reprendre : le jugement est refait", petit, GRIS)

    # ---- panneau 1 : les deux controles
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les DEUX contrôles", moyen, ENCRE)
    m1 = "★" if c["il_est_propre"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{m1}  rien ne va de travers sur la spirale nue", moyen,
           BON if c["il_est_propre"] else ALERTE)
    ecrire(x0 + 14, y0 + 50,
           f"{c['contaminees']} livraison contaminée, {c['poses_impossibles']} pose impossible, "
           f"sur {c['apparies']} départs", petit, ENCRE)
    m2 = "★" if c["le_surcout_y_est_exactement_double"] else "✗"
    ecrire(x0 + 14, y0 + 80, f"{m2}  et la croix y lit EXACTEMENT le double, par pas", moyen,
           BON if c["le_surcout_y_est_exactement_double"] else ALERTE)
    ecrire(x0 + 14, y0 + 108,
           f"×{_fr(c['surcout_de_la_croix'])} — deux barres au lieu d'une, sur une matière",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 124, "où aucune pose n'échoue", petit, ENCRE)
    b_ = c.get("sous_un_lecteur_bruite") or {}
    ecrire(x0 + 14, y0 + ph - 96,
           f"⚠⚠ ET LE CONTRÔLE EXACT VIT À BRUIT ZÉRO : sur la MÊME matière lisse,", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + ph - 80,
           f"un lecteur bruité rend {b_.get('poses_impossibles', '?')} poses impossibles sur "
           f"{b_.get('apparies', '?')} départs. « Spirale", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 64,
           "nue » et « rien ne va de travers » cessent d'être le même énoncé.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 40,
           f"⚠ Il n'exige pas non plus l'identité : {c['departs_identiques']}/{c['apparies']} "
           f"départs marchent le même", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 24,
           "nombre de pas — deux routes numériques vers une même normale.", petit, GRIS)

    # ---- panneau 2 : ce que les deux livrent
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que les deux instruments livrent — pas UTILISABLES", moyen, ENCRE)
    x_barre = x0 + 112
    barre_max = pw - 240
    vmax = max(max(g[SEGMENT]["utilisable"], g[CROIX]["utilisable"]) for g in bras) or 1
    for k, g in enumerate(bras):
        base = y0 + 30 + k * 82
        ecrire(x0 + 12, base - 18,
               f"{_court(g['nom'])} — {g['apparies']} départs appariés", petit, ENCRE)
        for i, (m, coul) in enumerate(((SEGMENT, CONTRE), (CROIX, ALERTE))):
            yy = base + i * 22
            n = int(g[m]["utilisable"])
            w = (n / vmax) * barre_max
            ecrire(x0 + 12, yy - 1, m, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy - 1, str(n), 0, coul)
        ecrire(x0 + 12, base + 46,
               f"récupère {g['la_croix_recupere']} départs, en perd {g['la_croix_perd']}", 0,
               ALERTE if g["la_croix_perd"] else GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "la victoire exigeait au moins autant sur CHAQUE départ apparié", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "elle n'est gagnée sur AUCUN bras", petit, ALERTE)

    # ---- panneau 3 : matiere par matiere
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce qu'elle récupère, et ce qu'elle perd — les trois bruits "
                          "ensemble", moyen, ENCRE)
    x_nom, x_b = x0 + 12, x0 + 128
    b_max = pw - 250
    nmax = max(max(g["la_croix_recupere"], g["la_croix_perd"]) for g in mat) or 1
    pas_bloc = max((ph - 84) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        base = y0 + 22 + k * pas_bloc
        ecrire(x_nom, base + 6, _court(g["nom"]), petit, ENCRE)
        for i, (cle, coul) in enumerate((("la_croix_recupere", BON),
                                         ("la_croix_perd", ALERTE))):
            yy = base + i * 15
            n = int(g[cle])
            w = (n / nmax) * b_max
            if n:
                art.rectangle([x_b, yy, x_b + max(w, 1), yy + 12], fill=coul)
            points.append((x_b + w, yy + 6))
            barres.append((x_b + w, x_b + b_max))
        ecrire(x_b + b_max + 8, base + 6,
               f"{g['la_croix_recupere']} / {g['la_croix_perd']}", 0,
               BON if g["la_croix_perd"] == 0 else ALERTE)
    ecrire(x0 + 12, y0 + ph - 56,
           "vert : départs récupérés · ambre : départs perdus", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "sur chaque matière qui se contredit, la croix perd plus qu'elle ne gagne",
           petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 20,
           "la victoire jointe n'est gagnée NULLE PART", petit, ALERTE)

    # ---- panneau 4 : le prix
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le PRIX — lectures PAR PAS, jamais en total", moyen, ENCRE)
    x_barre = x0 + 150
    barre_max = pw - 270
    lmax = max(max(g[SEGMENT]["lectures_par_pas"], g[CROIX]["lectures_par_pas"])
               for g in bras) or 1.0
    for k, g in enumerate(bras):
        base = y0 + 30 + k * 84
        ecrire(x0 + 12, base, f"{_court(g['nom'])} — ×{_fr(g['surcout_de_la_croix'])}",
               petit, ENCRE)
        for i, (m, coul) in enumerate(((SEGMENT, CONTRE), (CROIX, ALERTE))):
            yy = base + 20 + i * 20
            val = float(g[m]["lectures_par_pas"])
            w = (val / lmax) * barre_max
            ecrire(x0 + 12, yy - 1, m, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 13], fill=coul)
            points.append((x_barre + w, yy + 6))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy - 1, _fr(val, 1), 0, coul)
    a_, c_ = tout[SEGMENT], tout[CROIX]
    ecrire(x0 + 12, y0 + 188,
           f"poses impossibles PAR PAS : {_fr(a_['poses_impossibles_par_pas'])} en segment, "
           f"{_fr(c_['poses_impossibles_par_pas'])} en croix", petit, ENCRE)
    ecrire(x0 + 12, y0 + 206,
           f"({a_['poses_impossibles']} contre {c_['poses_impossibles']} en total, sur "
           f"{a_['pas']} et {c_['pas']} pas)", 0, GRIS)
    ecrire(x0 + 12, y0 + 224,
           "★ la croix se pose MIEUX, pas moins bien : `156` l'expliquait par l'inverse",
           0, BON)
    ecrire(x0 + 12, y0 + ph - 56,
           "⚠⚠ UN TOTAL FERAIT PASSER UNE CROIX QUI MEURT TÔT POUR UNE CROIX", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 40,
           "ÉCONOME : elle lit moins parce qu'elle marche moins. Le rapport est", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 24,
           "une somme de lectures divisée par une somme de pas.", petit, GRIS)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    p0 = bras[0]
    ecrire(74, y + 12,
           f"✗  La croix ne paie pas : sur le bras livré elle récupère "
           f"{p0['la_croix_recupere']} départs et en perd {p0['la_croix_perd']}, "
           f"pour ×{_fr(p0['surcout_de_la_croix'])} de lectures par pas.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"✗  Elle livre {p0[CROIX]['utilisable']} pas utilisables contre "
           f"{p0[SEGMENT]['utilisable']} au segment, et la victoire jointe n'est gagnée sur "
           f"aucun bras ni aucune matière.", moyen, ALERTE)
    ecrire(74, y + 64,
           "★★★★  Ce que cela ferme est la dernière voie INSTRUMENTALE nommée : pouvoir exprimer "
           "la normale hors du plan ne répare pas ce que rien ne répare.", moyen, ENCRE)
    ecrire(74, y + 90,
           f"★★★  Et le prix est mesuré là où il se prend : ×{_fr(p0['surcout_de_la_croix'])} "
           f"par pas, contre ×2 exactement là où rien ne rate. La différence est ce que les "
           f"poses ratées coûtent.", moyen, BON)
    ecrire(74, y + 110,
           f"★  Le contrôle tient : {c['contaminees']} livraison contaminée et "
           f"{c['poses_impossibles']} pose impossible sur la spirale nue, donc la comparaison "
           f"ne mesure pas son propre bruit.", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    # ⚠⚠⚠ LE CONTROLE QUE `167` A APPRIS DE L'OEIL : une barre dont l'echelle vient d'une autre
    # population sort de son graphe et RECOUVRE le nombre ecrit a cote. Le texte est a sa place,
    # dans son cadre, et il est illisible — aucun controle de TEXTE ne peut le voir.
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("⭐⭐⭐⭐ aucune barre ne déborde de son graphe, donc aucune ne recouvre son nombre",
      not debordantes, f"{len(barres)} barres, {debordantes}"[:180])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ⚠⚠⚠ LA MOITIE QUI REFUTE EST CELLE QUI SE DESSINE LE MOINS SPONTANEMENT : c'est le compte
    # des departs PERDUS qui fait tomber la victoire jointe.
    faux = copy.deepcopy(d)
    for g in faux["juger"]["par_bras"] + faux["juger"]["par_matiere"]:
        g["la_croix_perd"] = 4242
    _c, p2, _cd, _pt, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ le compte des départs que la croix PERD est LU, pas supposé",
      any("4242" in t for _x, _y, t, _f in p2) and not any("4242" in t for t in tous),
      "c'est lui qui refuse la victoire jointe")
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_bras"] + faux2["juger"]["par_matiere"]:
        g["la_croix_recupere"] = 3131
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐ ... et celui des départs qu'elle RÉCUPÈRE l'est aussi",
      any("3131" in t for _x, _y, t, _f in p3))
    # ⭐⭐⭐⭐ LE COUT EST CELUI PAR PAS : un total ferait passer une croix qui meurt tot pour une
    # croix econome, ce qui est `R4-F162` sous un costume.
    faux3 = copy.deepcopy(d)
    for g in faux3["juger"]["par_bras"]:
        g[CROIX]["lectures_par_pas"] = 717.1
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le coût PAR PAS est LU, et c'est lui qui est dessiné",
      any("717,1" in t for _x, _y, t, _f in p4))
    faux4 = copy.deepcopy(d)
    for g in faux4["juger"]["par_bras"]:
        g["surcout_de_la_croix"] = 5.1234
    _c, p5, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐ ... et le surcoût publié l'est aussi",
      any("5,1234" in t for _x, _y, t, _f in p5))
    # ⚠⚠ LES DEUX CONTROLES CHANGENT DE MARQUE, chacun de son cote.
    faux5 = copy.deepcopy(d)
    faux5["juger"]["le_controle_de_la_spirale_nue"]["il_est_propre"] = False
    _c, p6, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐⭐ un contrôle qui cesse d'être PROPRE change la marque de la figure",
      any(t.startswith("✗  rien ne va") for _x, _y, t, _f in p6)
      and not any(t.startswith("✗  rien ne va") for t in tous))
    faux6 = copy.deepcopy(d)
    faux6["juger"]["le_controle_de_la_spirale_nue"]["le_surcout_y_est_exactement_double"] = False
    _c, p7, _cd, _pt, _b = dessiner(faux6, sortie)
    v("⭐⭐⭐⭐ ... et celui du surcoût EXACT change la sienne, séparément",
      any(t.startswith("✗  et la croix") for _x, _y, t, _f in p7)
      and not any(t.startswith("✗  et la croix") for t in tous),
      "deux contrôles, deux marques : un seul les confondrait")
    v("⚠ la population appariée est écrite à côté de chaque total",
      all(any(f"{g['apparies']} départs appariés" in t for t in tous)
          for g in d["juger"]["par_bras"]),
      f"{[g['apparies'] for g in d['juger']['par_bras']]}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_168.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle de propreté est REFUSÉE",
      refuse(lambda x: x["juger"]["le_controle_de_la_spirale_nue"].pop("il_est_propre")))
    v("⚠⚠ une mesure sans le contrôle du surcoût EXACT est REFUSÉE",
      refuse(lambda x: x["juger"]["le_controle_de_la_spirale_nue"]
             .pop("le_surcout_y_est_exactement_double")))
    v("⚠⚠⚠ une mesure sans le coût PAR PAS est REFUSÉE",
      refuse(lambda x: [g[CROIX].update(lectures_par_pas=None)
                        for g in x["juger"]["par_bras"]]),
      "un total ferait passer une croix qui meurt tôt pour une croix économe")

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "la_croix_paie_t_elle_quand_on_ecoute.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "168_la_croix_paie_t_elle_quand_on_ecoute.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt, _b = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
