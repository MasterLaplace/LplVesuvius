"""De quoi est faite la contradiction que rien ne répare.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle : une absence TOTALE,
aucune pose ne se contredit sur la spirale nue. En haut à droite, le verdict apparié — le compte
bascule des deux côtés, sur les deux bras. En bas à gauche, la matière du rouleau, celle où `153`
prédisait l'effet : onze contre onze, et les deux bras pointent en sens CONTRAIRE quand on met leurs
niveaux en commun. En bas à droite, ce que la tranche établit tout de même : la part des
contradictions qu'un bras n'a pas su réparer, seule forme sous laquelle deux bras se comparent.

  uv run python src/figures/figure_la_contradiction_que_rien_ne_repare.py \\
      --json docs/mesures/la_contradiction_que_rien_ne_repare.json \\
      --sortie docs/images/167_la_contradiction_que_rien_ne_repare.png
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

LE_ROULEAU = "spirale écrasée et froissée 100 µm"


def lire(chemin: Path) -> dict:
    """Le JSON de `la_contradiction_que_rien_ne_repare.py`.

    ⚠⚠ Refuse une mesure sans le contrôle de la spirale nue, et sans le COMPTE apparié : la
    revendication de cette tranche est un compte de marches, et une figure qui n'en dessinerait que
    les niveaux rendrait lisible une comparaison que la tranche refuse de faire.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_bras_et_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_vide") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    for g in j["par_bras"]:
        if "lepuisee_sort_moins" not in g or "lepuisee_sort_davantage" not in g:
            raise ValueError(f"{chemin} : le compte apparié est absent de {g['nom']}")
        if g.get("part_des_contradictions_epuisees") is None:
            raise ValueError(f"{chemin} : la part des contradictions épuisées est absente")
    return d


def _fr(x: float) -> str:
    """Un nombre comme le dépôt l'écrit : virgule décimale, six chiffres, jamais complétés."""
    return f"{x:.6f}".replace(".", ",")


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def _sur_le_rouleau(j: dict, bras: str) -> dict | None:
    return next((g for g in j["par_bras_et_matiere"].get(bras, [])
                 if g["nom"] == LE_ROULEAU and g.get("marches_appariables")), None)


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    # ⚠⚠ (bout de la barre, bord droit de son graphe) : une barre qui deborde de son graphe
    # RECOUVRE le nombre ecrit a cote, et aucun controle de TEXTE ne peut le voir.
    barres: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    j = d["juger"]
    bras, tout = j["par_bras"], j["tout"]
    c = j["le_controle_de_la_spirale_nue"]

    ecrire(28, 20, "De quoi est faite la contradiction que rien ne répare — "
                   "l'hypothèse est RÉFUTÉE", gros, ENCRE)
    ecrire(28, 46, "`153` mesure que sur la matière du rouleau la VRAIE normale sort du plan du "
                   "tour, et que la mâchoire ne peut pas l'exprimer : elle semblait être en cause",
           petit, GRIS)

    # ---- panneau 1 : le controle est une absence TOTALE
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle — une absence TOTALE", moyen, ENCRE)
    m1 = "★" if c["il_est_vide"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{m1}  {c['nom']}", moyen, BON if c["il_est_vide"] else ALERTE)
    ecrire(x0 + 14, y0 + 52,
           f"{c['contradictions_reparees']} contradiction réparée, "
           f"{c['contradictions_epuisees']} épuisée, sur {c['decidables']} départs décidables",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 70,
           f"donc {c['marches_appariables']} marche appariable : il n'y a RIEN à comparer",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 104,
           "⚠ une seule contradiction y voudrait dire que la règle mesure", petit, GRIS)
    ecrire(x0 + 14, y0 + 120, "son propre bruit, et tout le reste serait illisible.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 90,
           "⚠⚠ L'APPARIEMENT EST DANS LA MARCHE, et c'est le seul", petit, ALERTE)
    ecrire(x0 + 14, y0 + ph - 74,
           "disponible : une marche qui s'épuise porte les DEUX", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 58,
           "populations — celles qu'elle a réparées, et celle qui l'a", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 42,
           f"arrêtée. {tout['marches_appariables']} marches sur "
           f"{tout['decidables']} en portent deux ; les autres n'en", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 26,
           "portent qu'une, et sont publiées À PART, jamais mêlées.", petit, GRIS)

    # ---- panneau 2 : le verdict apparie
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le verdict — un COMPTE de marches, jamais un niveau", moyen, ENCRE)
    x_barre = x0 + 152
    barre_max = pw - 280
    vmax = max(max(g["lepuisee_sort_davantage"], g["lepuisee_sort_moins"]) for g in bras) or 1
    for k, g in enumerate(bras):
        base = y0 + 30 + k * 86
        ecrire(x0 + 12, base - 18,
               f"{_court(g['nom'])} — {g['marches_appariables']} marches appariées", petit, ENCRE)
        for i, (cle, coul, lib) in enumerate(
                (("lepuisee_sort_davantage", ALERTE, "elle sort DAVANTAGE"),
                 ("lepuisee_sort_moins", CONTRE, "elle sort moins"))):
            yy = base + i * 22
            n = int(g[cle])
            w = (n / vmax) * barre_max
            ecrire(x0 + 12, yy - 1, lib, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy - 1, str(n), 0, coul)
        ecrire(x0 + 12, base + 46,
               f"et {g['elles_sont_egales']} écart exactement nul, compté à part", 0, GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "la revendication exigeait que RIEN ne sorte moins : elle tombe", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 20,
           "sur les DEUX bras, et le compte bascule des deux côtés", petit, ENCRE)

    # ---- panneau 3 : la matiere du rouleau, celle ou `153` predisait l'effet
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la matière du rouleau — là où `153` prédisait l'effet", moyen, ENCRE)
    # ⚠⚠⚠ L'ECHELLE SE DERIVE DES VALEURS REELLEMENT DESSINEES, jamais d'une autre population :
    # les niveaux du croisement rouleau depassent ceux des bras entiers, donc une echelle prise
    # sur `par_bras` ferait sortir la barre de son graphe et recouvrir le nombre a cote.
    _tires = [float(r[k]) for g in bras
              if (r := _sur_le_rouleau(j, g["nom"])) is not None
              for k in ("hors_plan_reparees", "hors_plan_epuisees")]
    hmax = max(_tires) if _tires else 1.0
    for k, g in enumerate(bras):
        r = _sur_le_rouleau(j, g["nom"])
        base = y0 + 26 + k * 122
        if r is None:
            ecrire(x0 + 12, base, f"{_court(g['nom'])} — aucune marche appariable", petit, GRIS)
            continue
        ecrire(x0 + 12, base,
               f"{_court(g['nom'])} — {r['marches_appariables']} marches appariées", petit, ENCRE)
        ecrire(x0 + 12, base + 20,
               f"{r['lepuisee_sort_davantage']} sortent davantage, "
               f"{r['elles_sont_egales']} à égalité, {r['lepuisee_sort_moins']} sortent moins",
               moyen, ALERTE if r["lepuisee_sort_davantage"] == r["lepuisee_sort_moins"]
               else ENCRE)
        x_b = x0 + 158
        b_max = pw - 300
        for i, (cle, coul, lib) in enumerate(
                (("hors_plan_reparees", CONTRE, "réparées"),
                 ("hors_plan_epuisees", ALERTE, "épuisées"))):
            yy = base + 46 + i * 20
            val = float(r[cle])
            w = (val / hmax) * b_max
            ecrire(x0 + 12, yy - 1, f"hors plan, {lib}", 0, GRIS)
            art.rectangle([x_b, yy, x_b + max(w, 1), yy + 13], fill=coul)
            points.append((x_b + w, yy + 6))
            barres.append((x_b + w, x_b + b_max))
            ecrire(x_b + b_max + 8, yy - 1, _fr(val), 0, coul)
    ecrire(x0 + 12, y0 + ph - 56,
           "⚠⚠ mis en commun, les deux bras pointent en sens CONTRAIRE — et", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 40,
           "aucun des deux n'est tranché par son propre compte apparié. C'est", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 24,
           "le compte qui tranche ; le niveau dit seulement à quelle échelle.", petit, GRIS)

    # ---- panneau 4 : ce que la tranche etablit tout de meme
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce qu'elle établit — la PART qu'un bras n'a pas su réparer", moyen, ENCRE)
    x_barre = x0 + 150
    barre_max = pw - 290
    for k, g in enumerate(bras):
        base = y0 + 30 + k * 76
        part = float(g["part_des_contradictions_epuisees"])
        ecrire(x0 + 12, base, _court(g["nom"]), petit, ENCRE)
        yy = base + 20
        w = part * barre_max
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 15], fill=ALERTE)
        points.append((x_barre + w, yy + 7))
        barres.append((x_barre + w, x_barre + barre_max))
        art.rectangle([x_barre, yy, x_barre + barre_max, yy + 15], outline=TRAIT, width=1)
        ecrire(x_barre + barre_max + 8, yy, _fr(part), 0, ALERTE)
        ecrire(x0 + 12, base + 42,
               f"{g['contradictions_epuisees']} épuisées sur "
               f"{g['contradictions_rencontrees']} rencontrées", 0, GRIS)
    ecrire(x0 + 12, y0 + 176,
           f"{tout['contradictions_rencontrees']} contradictions rencontrées en tout, "
           f"{tout['contradictions_epuisees']} épuisées", petit, ENCRE)
    ecrire(x0 + 12, y0 + 194,
           "le cadre vaut 1 : toutes les contradictions rencontrées", 0, GRIS)
    ecrire(x0 + 12, y0 + ph - 90,
           "⚠⚠ COMPARER LES COMPTES SERAIT COMPARER DES TOTAUX SUR DES", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 74,
           "POPULATIONS INÉGALES : la mâchoire seule rencontre deux fois plus", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 58,
           "de contradictions que la pince et en épuise moins de la moitié en", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 42,
           "compte. La part est la seule forme sous laquelle elles se", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 26,
           "comparent, et elle répond à une question bien posée.", petit, GRIS)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince, machoire = bras[0], bras[1]
    rp = _sur_le_rouleau(j, pince["nom"])
    ecrire(74, y + 12,
           f"✗  L'hypothèse est RÉFUTÉE : sur le bras livré, {pince['lepuisee_sort_davantage']} "
           f"marches disent que l'épuisée sort davantage du plan et "
           f"{pince['lepuisee_sort_moins']} disent le contraire.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"✗  Et sur la matière du rouleau, là où `153` le prédisait, le compte est "
           f"{rp['lepuisee_sort_davantage']} contre {rp['lepuisee_sort_moins']} "
           f"sur {rp['marches_appariables']} marches appariées.", moyen, ALERTE)
    ecrire(74, y + 64,
           "★★★★  Ce que cela retire est un candidat, et il était le dernier nommé : la "
           "contradiction irréparable n'est pas faite de la normale qui sort du plan.", moyen,
           ENCRE)
    ecrire(74, y + 90,
           f"★★★  Ce qu'elle établit : la pince échoue à réparer "
           f"{_fr(pince['part_des_contradictions_epuisees'])} des contradictions qu'elle "
           f"rencontre, la mâchoire seule "
           f"{_fr(machoire['part_des_contradictions_epuisees'])}.", moyen, BON)
    ecrire(74, y + 110,
           "★  Le contrôle tient : sur la spirale nue, aucune pose ne se contredit, donc la "
           "comparaison y est VIDE et la règle ne mesure pas son bruit.", moyen, ENCRE)

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
    # ⚠⚠⚠ C'EST L'OEIL QUI A TROUVE CE DEFAUT, et aucun controle de TEXTE ne pouvait le voir :
    # une barre dont l'echelle vient d'une autre population sort de son graphe et RECOUVRE le
    # nombre ecrit a cote. Le texte est a sa place, dans son cadre, et il est illisible.
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

    # ⚠⚠⚠ LA MOITIE QUI REFUTE EST CELLE QUI SE DESSINE LE MOINS SPONTANEMENT. Une figure qui ne
    # tracerait que « elle sort davantage » ferait lire une refutation comme une confirmation :
    # c'est le compte CONTRAIRE qui porte le verdict, donc c'est lui qu'il faut asserter lu.
    faux = copy.deepcopy(d)
    for g in faux["juger"]["par_bras"]:
        g["lepuisee_sort_moins"] = 4242
    _c, p2, _cd, _pt, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ le compte des marches qui CONTREDISENT la revendication est LU, pas supposé",
      any("4242" in t for _x, _y, t, _f in p2) and not any("4242" in t for t in tous),
      "c'est lui qui réfute, donc une figure qui l'omettrait ferait lire l'inverse")
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_bras"]:
        g["lepuisee_sort_davantage"] = 3131
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐ ... et celui des marches qui la SOUTIENNENT l'est aussi",
      any("3131" in t for _x, _y, t, _f in p3))
    # ⚠⚠ UN ECART EXACTEMENT NUL EST UNE TROISIEME REPONSE, jamais une moitie de l'une des deux.
    faux3 = copy.deepcopy(d)
    for g in faux3["juger"]["par_bras"]:
        g["elles_sont_egales"] = 5151
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⚠⚠ l'écart exactement nul est écrit, jamais fondu dans l'un des deux camps",
      any("5151" in t for _x, _y, t, _f in p4))

    # ⭐⭐⭐⭐ LA MATIERE DU ROULEAU EST CELLE OU `153` PREDISAIT L'EFFET : si la figure y lisait un
    # autre croisement, elle refuterait une prediction que personne n'a faite.
    faux4 = copy.deepcopy(d)
    for _b, l in faux4["juger"]["par_bras_et_matiere"].items():
        for g in l:
            if g["nom"] == LE_ROULEAU and g.get("marches_appariables"):
                g["marches_appariables"] = 6161
    _c, p5, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ le croisement lu est bien celui de la matière du ROULEAU",
      any("6161" in t for _x, _y, t, _f in p5) and not any("6161" in t for t in tous),
      LE_ROULEAU)
    faux5 = copy.deepcopy(d)
    for g in faux5["juger"]["par_bras"]:
        g["part_des_contradictions_epuisees"] = 0.717171
    _c, p6, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐ la part des contradictions épuisées est LUE",
      any("0,717171" in t for _x, _y, t, _f in p6))
    # ⚠⚠ LE CONTROLE EST UNE ABSENCE TOTALE : sa marque doit CHANGER s'il cesse d'etre vide.
    faux6 = copy.deepcopy(d)
    faux6["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] = False
    _c, p7, _cd, _pt, _b = dessiner(faux6, sortie)
    v("⭐⭐⭐⭐ un contrôle qui cesse d'être VIDE change la marque de la figure",
      any(t.startswith("✗") for _x, _y, t, _f in p7)
      and not any(t.startswith("✗  spirale") for t in tous),
      "une seule contradiction sur la spirale nue rendrait tout illisible")
    v("⚠ la population appariée est écrite à côté de chaque compte",
      all(any(f"{g['marches_appariables']} marches appariées" in t for t in tous)
          for g in d["juger"]["par_bras"]),
      f"{[g['marches_appariables'] for g in d['juger']['par_bras']]}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_167.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle de la spirale nue est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_controle_de_la_spirale_nue")))
    v("⚠⚠ une mesure sans le COMPTE apparié est REFUSÉE",
      refuse(lambda x: [g.pop("lepuisee_sort_moins") for g in x["juger"]["par_bras"]]),
      "une figure qui n'aurait que les niveaux ferait la comparaison que la tranche refuse")
    v("⚠ une mesure sans la part des contradictions épuisées est REFUSÉE",
      refuse(lambda x: [g.update(part_des_contradictions_epuisees=None)
                       for g in x["juger"]["par_bras"]]))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "la_contradiction_que_rien_ne_repare.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "167_la_contradiction_que_rien_ne_repare.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt, _b = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
