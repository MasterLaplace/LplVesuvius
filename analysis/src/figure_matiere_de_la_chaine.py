#!/usr/bin/env python3
"""La nappe reste-t-elle POSÉE SUR LA MATIÈRE à mesure que la chaîne avance ?

⚠⚠ CE QUE LA FIGURE DOIT RENDRE ÉVIDENT, et c'est un fait que la géométrie ne pouvait pas
dire : la nappe **quitte sa feuille AVANT de se détruire**. Le pas d'une chaîne de 95 µm ne
décroche qu'au sixième maillon ([`44`](../docs/44_ou_la_chaine_se_trouve.md) §7), mais la part
de ses points qui trouvent encore de la matière tombe bien avant. L'horizon **utile** est donc
plus court que l'horizon **géométrique**, et les deux méritaient d'être vus ensemble.

⭐ Le témoin est dans la figure, pas à côté : le segment **publié** est sur sa feuille par
construction, donc sa part de points posés est la ligne que rien ne peut dépasser. Une courbe
tracée sans elle laisserait lire « 56 % » comme un échec ou comme un succès, au choix du
lecteur.

⚠⚠ Ce qui est compté comme « posé sur la matière », et pourquoi ce n'est PAS `recalés` : un
point qui bute sur la borne de recherche **a trouvé de la matière**, il n'a simplement pas pu
prouver que c'en était le sommet. L'exclure ferait passer une portée trop courte pour une
absence de feuille. Et les points **hors de la boîte téléchargée** sortent du dénominateur :
« je n'ai pas cette région » n'est pas « le rouleau est vide ici ».
"""
from __future__ import annotations

import argparse
import json
import sys
import pathlib
from pathlib import Path

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
POSE = (74, 132, 96)
BOND = (196, 72, 60)
REPERE = (176, 174, 168)

ANGLAIS = {
    "la nappe reste-t-elle posée sur la matière ?": "does the sheet stay on the material?",
    "part des points posés sur la matière": "share of points sitting on material",
    "distance parcourue le long de la tangente": "distance travelled along the tangent",
    "segment publié — la référence": "published segment — the reference",
    "bond direct, même distance": "direct jump, same distance",
    "chaîne de 95 µm": "95 µm chain",
    "chaîne CORRIGÉE sur la matière": "chain RE-SEATED on the material",
    "plancher du hasard": "chance floor",
    "⚠ le pas s'emballe ici": "⚠ the step runs away here",
}


def _police():
    from PIL import ImageFont
    for c in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return (ImageFont.truetype(c, 14), ImageFont.truetype(c, 12),
                    ImageFont.truetype(c, 11))
        except OSError:
            continue
    d = ImageFont.load_default()
    return d, d, d


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def fusionner(chemins) -> list[dict]:
    """Plusieurs JSON de campagne, recollés en une seule série.

    ⚠⚠ Une campagne longue se mesure en plusieurs passes — on ne relance pas cinquante minutes
    de recalage pour ajouter deux distances. Recoller les fichiers À LA MAIN dans un tube serait
    perdre le calcul, donc le recollage est ici, testé, et il **dédoublonne** : un même maillage
    mesuré dans deux passes (la source, typiquement) ne doit pas être tracé deux fois.

    ⚠ La clé de dédoublonnage est le NOM du maillage et non sa distance : deux maillages
    différents peuvent légitimement être à la même distance — une chaîne et son bond direct le
    sont toujours.
    """
    vus, out = set(), []
    for c in chemins:
        for r in json.loads(pathlib.Path(c).read_text(encoding="utf-8")):
            if r["maillage"] in vus:
                continue
            vus.add(r["maillage"])
            out.append(r)
    return sorted(out, key=lambda r: float(r["parcouru_um"]))


def part_posee(r: dict) -> float:
    """La part des points qui ont trouvé de la matière, parmi ceux qu'on pouvait interroger.

    ⚠⚠ Deux décisions, et chacune corrige une lecture fausse :

      - `borne` compte AVEC les posés. Un point qui bute sur la borne de recherche a bien
        trouvé de la matière ; il n'a pas prouvé qu'il en tenait le sommet. Le compter comme
        « sans matière » ferait passer une portée trop courte pour une feuille absente.
      - `hors_boite` sort du DÉNOMINATEUR. Un point hors de ce qu'on a téléchargé n'est ni posé
        ni décollé : il n'a pas été interrogé, et le mettre au dénominateur ferait baisser la
        courbe à mesure que la chaîne sort de la boîte — c'est-à-dire fabriquerait exactement
        le résultat qu'on cherche.
    """
    if "points" not in r:
        raise ValueError(f"{r.get('maillage')} : la campagne ne rapporte pas `points` — "
                         f"sans le total, aucune part n'est calculable")
    interroges = int(r["points"]) - int(r.get("hors_boite", 0))
    if interroges <= 0:
        return 0.0
    return (int(r["recales"]) + int(r.get("borne", 0))) / interroges


CORRIGEE = (58, 96, 168)
HASARD = (198, 168, 120)


def plancher_de(r: dict) -> float | None:
    """Le plancher du hasard porté par un rang, ou `None`.

    ⚠ La campagne écrit `-1` quand elle n'a PAS mesuré de plancher — un plancher de zéro serait
    un plancher mesuré à zéro, c'est-à-dire « rien de ce qu'on lit n'est du hasard », soit
    l'affirmation la plus flatteuse possible. Absence et zéro ne peuvent pas partager une valeur.
    """
    v = r.get("plancher")
    if v is None:
        return None
    v = float(v)
    return None if v < 0.0 else v


def avantage(r: dict) -> float | None:
    """⭐⭐ CE QUI DOIT ÊTRE PUBLIÉ : la part posée MOINS le plancher du hasard.

    ⚠⚠ Un pourcentage brut ne veut rien dire tout seul, et deux mesures du même dépôt le
    prouvent : 78,9 % contre un plancher de 48,4 est un résultat, 35,4 % contre un plancher de
    37,1 est du bruit — et le second est *plus grand* que la moitié du premier. Le nombre qui
    porte l'énoncé est l'ÉCART au hasard, pas la valeur.

    ⚠ Rend `None` quand aucun plancher n'a été mesuré : un avantage calculé contre un plancher
    absent serait la part brute, c'est-à-dire exactement la lecture qu'on cherche à empêcher.
    """
    pl = plancher_de(r)
    return None if pl is None else part_posee(r) - pl


def dessiner(rangs: list[dict], sortie: Path, anglais: bool = False,
             emballement_um: float | None = None,
             corrigee: list[dict] | None = None, nom_chaine: str | None = None) -> dict:
    """La part posée contre la distance, la source en repère et le bond en marqueur.

    ⭐ `corrigee` superpose une SECONDE chaîne — celle qui repose sa nappe sur la matière entre
    deux projections. Les deux vivent sur les mêmes axes parce que la question est « laquelle
    tient plus loin », et deux figures côte à côte laisseraient le lecteur comparer deux
    échelles au lieu de deux courbes.
    """
    if len(rangs) < 2:
        raise ValueError("moins de deux maillages — une tendance en demande au moins deux")
    g1, g2, g3 = _police()
    intraduits, inchanges = [], []

    def T(txt: str) -> str:
        if not anglais:
            return txt
        out = txt
        for fr, en in sorted(ANGLAIS.items(), key=lambda kv: -len(kv[0])):
            out = out.replace(fr, en)
        if out == txt and any(c.isalpha() for c in txt):
            inchanges.append(txt)
        if any(c in out for c in "éèêàùôîçâû"):
            intraduits.append(out)
        return out

    # ⚠ La SOURCE est le maillage à distance nulle : c'est le repère, pas un point de courbe.
    source = next((r for r in rangs if float(r["parcouru_um"]) <= 0.0), None)
    bonds = [r for r in rangs if r["maillage"] == "direct"]
    chaine = sorted((r for r in rangs
                     if float(r["parcouru_um"]) > 0.0 and r["maillage"] != "direct"),
                    key=lambda r: float(r["parcouru_um"]))
    if not chaine:
        raise ValueError("aucun maillon de chaîne — rien à tracer")

    largeur, hauteur = 660, 388
    gx, gy = 74, 84
    gw, gh = largeur - gx - 30, hauteur - gy - 82
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)
    d.text((24, 16), T("la nappe reste-t-elle posée sur la matière ?"), font=g1, fill=ENCRE)

    hi = max([float(r["parcouru_um"]) for r in chaine + bonds]
             + [float(r["parcouru_um"]) for r in (corrigee or [])] + [1.0]) * 1.06

    def X(v):
        return gx + gw * max(0.0, min(hi, v)) / hi

    def Y(v):
        return gy + gh * (1.0 - max(0.0, min(1.0, v)))

    for k in range(5):
        y = gy + gh * k / 4
        d.line([(gx, y), (gx + gw, y)], fill=TRAIT, width=1)
        d.text((gx - 40, y - 7), f"{100 - 25 * k} %", font=g3, fill=GRIS)
    d.line([(gx, gy + gh), (gx + gw, gy + gh)], fill=GRIS, width=1)

    # ⭐ Le repère de la SOURCE : la ligne que rien ne peut dépasser, parce qu'elle est la
    # même mesure sur une nappe qui EST sur sa feuille.
    repere = None
    if source is not None:
        repere = part_posee(source)
        d.line([(gx, Y(repere)), (gx + gw, Y(repere))], fill=REPERE, width=1)
        # ⚠ À GAUCHE, ce libellé heurtait le premier point de la courbe et l'étiquette du
        # bond. À droite la courbe est déjà descendue, donc la place est libre par construction.
        t = T("segment publié — la référence")
        d.text((gx + gw - d.textlength(t, font=g3), Y(repere) - 15), t, font=g3, fill=REPERE)

    emb_trace = 0
    if emballement_um and 0 < emballement_um <= hi:
        # ⚠⚠ L'horizon GÉOMÉTRIQUE, dessiné pour qu'on VOIE qu'il arrive trop tard. Sans lui,
        # la chute de la courbe se lit comme une conséquence de l'emballement, alors qu'elle
        # le précède.
        xe = X(emballement_um)
        for k in range(0, gh, 6):
            d.line([(xe, gy + k), (xe, gy + min(gh, k + 3))], fill=BOND, width=1)
        t = T("⚠ le pas s'emballe ici")
        d.text((min(xe + 5, gx + gw - d.textlength(t, font=g3)), gy - 16), t,
               font=g3, fill=BOND)
        emb_trace = 1

    pts = [(X(float(r["parcouru_um"])), Y(part_posee(r))) for r in chaine]
    if source is not None:
        pts.insert(0, (X(0.0), Y(repere)))
    d.line(pts, fill=POSE, width=2)
    for (x, y), r in zip(pts[1:] if source is not None else pts, chaine):
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=POSE)
        t = f"{part_posee(r) * 100:.0f} %"
        d.text((x - d.textlength(t, font=g3) / 2, y + 7), t, font=g3, fill=POSE)

    for r in bonds:
        x, y = X(float(r["parcouru_um"])), Y(part_posee(r))
        d.polygon([(x, y - 7), (x + 7, y), (x, y + 7), (x - 7, y)],
                  outline=BOND, fill=FOND, width=2)
        # ⚠ Au-DESSUS, cette étiquette se superposait à celle du maillon de même distance :
        # deux nombres différents au même endroit, ce qui est pire que pas de nombre du tout.
        t = f"{part_posee(r) * 100:.0f} %"
        d.text((x + 12, y + 8), t, font=g3, fill=BOND)

    # ⚠⚠ LE PLANCHER DU HASARD, tracé COMME UNE COURBE et non comme une ligne unique : il
    # dépend de la densité locale de matière, mesurée à onze points d'écart entre deux endroits
    # du même rouleau. Une ligne unique prêterait à un maillage la densité du quartier d'un
    # autre — et c'est précisément l'erreur qui aurait déclaré la chaîne « au-dessus du hasard ».
    # ⚠⚠ CHAQUE chaîne a SON plancher, et les deux se tracent. Deux chaînes qui n'ont pas
    # parcouru le même terrain n'ont pas la même densité locale de matière — mesuré à onze
    # points d'écart le long d'une seule chaîne. N'en tracer qu'un prêterait à la seconde le
    # quartier de la première, ce qui est l'erreur exacte que le plancher par maillage évite.
    plancher_traces = 0

    def _trace_plancher(source_rangs, etiquette: bool):
        nonlocal plancher_traces
        pts_ = [(X(float(q["parcouru_um"])), Y(plancher_de(q)))
                for q in sorted(source_rangs, key=lambda z: float(z["parcouru_um"]))
                if plancher_de(q) is not None]
        if len(pts_) > 1:
            d.line(pts_, fill=HASARD, width=2)
        for (x_, y_) in pts_:
            d.line([(x_ - 5, y_), (x_ + 5, y_)], fill=HASARD, width=2)
            plancher_traces += 1
        if pts_ and etiquette:
            t_ = T("plancher du hasard")
            x_, y_ = pts_[-1]
            d.text((min(x_ + 8, gx + gw - d.textlength(t_, font=g3)), y_ + 5), t_,
                   font=g3, fill=HASARD)

    _trace_plancher(rangs, True)
    if corrigee:
        _trace_plancher(corrigee, False)

    corr_traces = 0
    if corrigee:
        cc = sorted((r for r in corrigee if float(r["parcouru_um"]) > 0.0),
                    key=lambda r: float(r["parcouru_um"]))
        cpts = [(X(float(r["parcouru_um"])), Y(part_posee(r))) for r in cc]
        if source is not None:
            cpts.insert(0, (X(0.0), Y(repere)))
        if len(cpts) > 1:
            d.line(cpts, fill=CORRIGEE, width=2)
        for (x, y) in (cpts[1:] if source is not None else cpts):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=CORRIGEE)
            corr_traces += 1
        # ⚠ Seule la DERNIÈRE valeur est étiquetée : les deux courbes se croisent, donc
        # étiqueter chaque point mettrait deux nombres de deux séries au même endroit — le
        # défaut que la version précédente a déjà payé sur le bond direct.
        if cc:
            t = f"{part_posee(cc[-1]) * 100:.0f} %"
            x, y = cpts[-1]
            d.text((x - d.textlength(t, font=g3) - 8, y - 6), t, font=g3, fill=CORRIGEE)

    lx = 24
    depassement = 0
    # ⚠ Le nom de la série PORTE UN NOMBRE, donc il doit être celui de la chaîne tracée : la
    # même figure sert un pas de grille de 95 µm et un pas fixe de 96, et une légende qui
    # annonce la mauvaise valeur est une erreur publiée sous couvert de décoration.
    series = [(POSE, nom_chaine or "chaîne de 95 µm", True),
              (BOND, "bond direct, même distance", False)]
    if corrigee:
        series.insert(1, (CORRIGEE, "chaîne CORRIGÉE sur la matière", True))
    for couleur, nom, plein in series:
        if plein:
            d.rectangle([lx, 52, lx + 12, 60], fill=couleur)
        else:
            d.polygon([(lx + 6, 50), (lx + 13, 56), (lx + 6, 62), (lx - 1, 56)],
                      outline=couleur, fill=FOND, width=2)
        t = T(nom)
        d.text((lx + 18, 49), t, font=g3, fill=couleur)
        lx += 18 + int(d.textlength(t, font=g3)) + 24
    depassement = max(0, lx - (largeur - 24))

    # ⚠⚠ Les graduations PORTENT leur valeur. Le premier tirage dessinait les traits et pas
    # les nombres : un axe dont on ne peut pas lire les abscisses transforme un résultat
    # quantitatif en impression. Éclaircies quand elles se touchent, comme ailleurs.
    etiquettes_x = 0
    dernier = -1e9
    # ⚠⚠ La chaîne CORRIGÉE entre dans les graduations. Sans elle, l'axe s'étendait pour la
    # contenir mais ne portait de nombres que jusqu'au dernier point de la chaîne pure — donc
    # toute la moitié droite, celle où la comparaison se joue, n'avait aucune abscisse lisible.
    for r in sorted(chaine + bonds + list(corrigee or []),
                    key=lambda q: float(q["parcouru_um"])):
        um = float(r["parcouru_um"])
        x = X(um)
        d.line([(x, gy + gh), (x, gy + gh + 5)], fill=GRIS, width=1)
        t = f"{um:.0f}"
        w = d.textlength(t, font=g3)
        if x - w / 2 >= dernier + 6:
            d.text((x - w / 2, gy + gh + 8), t, font=g3, fill=GRIS)
            dernier = x + w / 2
            etiquettes_x += 1
    d.text((gx, gy + gh + 26), T("distance parcourue le long de la tangente") + " (µm)",
           font=g3, fill=GRIS)
    d.line([(24, hauteur - 34), (largeur - 24, hauteur - 34)], fill=TRAIT, width=1)
    d.text((24, hauteur - 28),
           T("part des points posés sur la matière") +
           " — " + T("segment publié — la référence"), font=g3, fill=GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"maillons": len(chaine), "bonds": len(bonds), "repere": repere,
            "etiquettes_x": etiquettes_x, "corrigee_traces": corr_traces,
            "plancher_traces": plancher_traces,
            "largeur": largeur, "hauteur": hauteur, "depassement": int(depassement),
            "emballement_trace": emb_trace,
            "parts": [part_posee(r) for r in chaine],
            "intraduits": intraduits, "inchanges": inchanges}


def _verifier() -> int:
    import tempfile

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    # ⚠⚠ `borne` compte AVEC les posés, `hors_boite` sort du dénominateur. Les deux décisions
    # sont sondées sur des chiffres dont on connaît la réponse à la main.
    v("un maillage entièrement posé rend 100 %",
      abs(part_posee({"points": 100, "recales": 100, "borne": 0, "hors_boite": 0}) - 1.0) < 1e-9)
    v("la borne compte comme posée",
      abs(part_posee({"points": 100, "recales": 60, "borne": 40, "hors_boite": 0}) - 1.0) < 1e-9)
    v("... et sans elle on lirait 60 %",
      abs(part_posee({"points": 100, "recales": 60, "borne": 0, "hors_boite": 0}) - 0.6) < 1e-9)
    v("hors boîte sort du dénominateur",
      abs(part_posee({"points": 100, "recales": 50, "borne": 0, "hors_boite": 50}) - 1.0) < 1e-9,
      str(part_posee({"points": 100, "recales": 50, "borne": 0, "hors_boite": 50})))
    v("... sinon la courbe tomberait en sortant de la boîte",
      abs(part_posee({"points": 100, "recales": 50, "borne": 0}) - 0.5) < 1e-9)
    v("un maillage entièrement hors boîte ne rend pas une part inventée",
      part_posee({"points": 100, "recales": 0, "borne": 0, "hors_boite": 100}) == 0.0)
    try:
        part_posee({"maillage": "m", "recales": 10, "borne": 0})
        v("sans le total, aucune part n'est calculée", False)
    except ValueError:
        v("sans le total, aucune part n'est calculée", True)

    faux = [
        {"maillage": "morceau_00", "parcouru_um": 0.0, "points": 100, "recales": 60,
         "borne": 20, "hors_boite": 0},
        {"maillage": "maillon_3", "parcouru_um": 286.0, "points": 100, "recales": 58,
         "borne": 21, "hors_boite": 0},
        {"maillage": "direct", "parcouru_um": 286.0, "points": 100, "recales": 50,
         "borne": 22, "hors_boite": 0},
        {"maillage": "maillon_6", "parcouru_um": 587.0, "points": 100, "recales": 32,
         "borne": 20, "hors_boite": 0},
    ]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(faux, f, emballement_um=580.0)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les deux maillons sont tracés", r["maillons"] == 2, str(r["maillons"]))
        # ⚠ Le BOND n'est pas un maillon : le ranger dans la courbe ferait lire un témoin
        # comme une étape de la chaîne, exactement l'erreur que le témoin existe pour éviter.
        v("le bond direct n'est PAS un maillon", r["bonds"] == 1)
        v("le repère vient de la source", abs(r["repere"] - 0.80) < 1e-9, str(r["repere"]))
        px = _pixels(Image.open(f).convert("RGB"))
        v("la courbe posée est tracée", POSE in px)
        v("le bond est tracé", BOND in px)
        v("le repère de la source est tracé", REPERE in px)
        v("l'horizon géométrique est tracé", r["emballement_trace"] == 1)
        # ⚠ Un horizon hors du domaine n'est pas dessiné au bord : il est SAUTÉ. Le coller à
        # la marge ferait croire que l'emballement tombe dans la fenêtre observée.
        r2 = dessiner(faux, Path(td) / "b.png", emballement_um=99999.0)
        v("un horizon hors domaine est sauté", r2["emballement_trace"] == 0)
        v("aucun libellé ne déborde", r["depassement"] == 0, f"{r['depassement']} px")
        # ⚠ Un axe dont on ne lit pas les abscisses transforme un résultat en impression.
        v("les abscisses portent leur valeur", r["etiquettes_x"] >= 2,
          str(r["etiquettes_x"]))
        # ⚠⚠ … et l'éclaircissage doit ÉCLAIRCIR : deux maillons à la même distance ne
        # peuvent pas écrire deux nombres au même endroit.
        serre = [dict(x) for x in faux]
        serre[2]["parcouru_um"] = 287.0
        rs = dessiner(serre, Path(td) / "serre.png")
        v("des abscisses confondues n'écrivent qu'une étiquette",
          rs["etiquettes_x"] < 3, str(rs["etiquettes_x"]))
        try:
            dessiner(faux[:1], Path(td) / "c.png")
            v("un seul maillage est refusé", False)
        except ValueError:
            v("un seul maillage est refusé", True)
        try:
            dessiner([faux[0], faux[2]], Path(td) / "d.png")
            v("une campagne sans maillon est refusée", False)
        except ValueError:
            v("une campagne sans maillon est refusée", True)
        # ⚠⚠ LE PLANCHER DU HASARD. Sans lui, « 35 % posé » peut vouloir dire à moitié
        # perdue comme complètement perdue. Il est tracé en COURBE parce qu'il dépend de la
        # densité locale — deux endroits du même rouleau en diffèrent de onze points.
        avec_pl = [dict(x) for x in faux]
        for k, val in zip(avec_pl, (0.48, 0.47, 0.46, 0.37)):
            k["plancher"] = val
        rp = dessiner(avec_pl, Path(td) / "pl.png")
        v("le plancher est tracé par point", rp["plancher_traces"] == 4,
          str(rp["plancher_traces"]))
        v("... dans sa propre couleur", HASARD in _pixels(
            Image.open(Path(td) / "pl.png").convert("RGB")))
        v("sans plancher mesuré, aucune trace", r["plancher_traces"] == 0)
        # ⚠⚠ La SECONDE chaîne a son propre plancher, et il se trace aussi : deux chaînes qui
        # n'ont pas parcouru le même terrain n'ont pas la même densité locale.
        corr_pl = [{"maillage": f"maillon_{k}", "parcouru_um": 300.0 * k, "points": 100,
                    "recales": 70 - 2 * k, "borne": 10, "hors_boite": 0,
                    "plancher": 0.40 - 0.01 * k} for k in range(1, 5)]
        rdp = dessiner(avec_pl, Path(td) / "deuxpl.png", corrigee=corr_pl)
        v("les DEUX planchers sont tracés",
          rdp["plancher_traces"] == len(avec_pl) + len(corr_pl),
          str(rdp["plancher_traces"]))
        # ⚠ La campagne écrit -1 quand elle n'a PAS mesuré : un plancher de zéro serait un
        # plancher MESURÉ à zéro, soit l'affirmation la plus flatteuse possible.
        v("un plancher absent est None", plancher_de({"maillage": "m"}) is None)
        v("... et -1 aussi", plancher_de({"plancher": -1.0}) is None)
        v("... mais zéro est une VALEUR", plancher_de({"plancher": 0.0}) == 0.0)
        sans = [dict(x) for x in faux]
        sans[0]["plancher"] = -1.0
        rs2 = dessiner(sans, Path(td) / "pl2.png")
        v("un rang sans plancher ne casse pas la courbe", rs2["plancher_traces"] == 0)
        # ⭐⭐ L'AVANTAGE sur le hasard, qui est le nombre à publier. Sondé sur les deux cas
        # réels du dépôt : le segment publié est loin au-dessus, la chaîne lointaine est
        # DESSOUS — et 35,4 % est pourtant plus grand que la moitié de 78,9 %.
        v("un avantage franc est positif",
          abs(avantage({"points": 100, "recales": 79, "borne": 0, "hors_boite": 0,
                        "plancher": 0.484}) - 0.306) < 1e-9)
        v("... et un avantage négatif l'est",
          avantage({"points": 100, "recales": 35, "borne": 0, "hors_boite": 0,
                    "plancher": 0.371}) < 0)
        # ⚠ Sans plancher, AUCUN avantage : le calculer contre un plancher absent rendrait la
        # part brute, c'est-à-dire exactement la lecture qu'on cherche à empêcher.
        v("sans plancher, aucun avantage",
          avantage({"points": 100, "recales": 35, "borne": 0, "hors_boite": 0}) is None)

        # ⭐ La SECONDE chaîne, celle qui repose sur la matière. L'axe doit s'étendre pour la
        # contenir, sinon ses points lointains seraient écrasés au bord et la comparaison
        # « laquelle tient plus loin » deviendrait illisible exactement où elle se joue.
        corr = [{"maillage": f"maillon_{i}", "parcouru_um": 300.0 * i, "points": 100,
                 "recales": 70 - 3 * i, "borne": 10, "hors_boite": 0} for i in range(1, 5)]
        rc = dessiner(faux, Path(td) / "deux.png", corrigee=corr)
        v("la chaîne corrigée est tracée", rc["corrigee_traces"] == 4,
          str(rc["corrigee_traces"]))
        # ⚠ Et l'axe porte les abscisses des DEUX chaînes : la moitié droite est celle où la
        # comparaison se joue, et un axe sans nombres y transforme un résultat en impression.
        v("... et l'axe porte plus de graduations qu'avec une seule chaîne",
          rc["etiquettes_x"] > r["etiquettes_x"],
          f"{rc['etiquettes_x']} vs {r['etiquettes_x']}")
        pxc = _pixels(Image.open(Path(td) / "deux.png").convert("RGB"))
        v("... dans sa propre couleur", CORRIGEE in pxc)
        v("sans elle, aucune trace corrigée", r["corrigee_traces"] == 0)
        # ⚠⚠ Le RECOLLAGE de plusieurs passes. Une campagne longue se mesure en plusieurs
        # fois, et la source apparaît dans chacune : la tracer deux fois mettrait deux points
        # à l'abscisse zéro.
        j1, j2 = Path(td) / "p1.json", Path(td) / "p2.json"
        j1.write_text(json.dumps(faux[:2]), encoding="utf-8")
        j2.write_text(json.dumps([faux[0], faux[3]]), encoding="utf-8")
        f2 = fusionner([j1, j2])
        v("deux passes se recollent", len(f2) == 3, str(len(f2)))
        v("... la source n'est pas doublée",
          sum(1 for x in f2 if x["maillage"] == "morceau_00") == 1)
        v("... et le résultat est trié par distance",
          [x["parcouru_um"] for x in f2] == sorted(x["parcouru_um"] for x in f2))
        # ⚠ Deux maillages DIFFÉRENTS à la même distance sont légitimes — une chaîne et son
        # bond direct le sont toujours — donc la clé est le nom, pas l'abscisse.
        j3 = Path(td) / "p3.json"
        j3.write_text(json.dumps([faux[1], faux[2]]), encoding="utf-8")
        v("deux maillages à la même distance sont gardés tous les deux",
          len(fusionner([j3])) == 2)
        # ⚠ Le nom de la série porte un NOMBRE : la même figure sert un pas de 95 et un de 96.
        rn = dessiner(faux, Path(td) / "nom.png", nom_chaine="chaîne de 96 µm, pas FIXE")
        v("le nom de la chaîne est remplaçable",
          _pixels(Image.open(Path(td) / "nom.png").convert("RGB")) != _pixels(
              Image.open(f).convert("RGB")))
        v("... sans faire déborder la légende", rn["depassement"] == 0,
          f"{rn['depassement']} px")
        v("... et sa légende ne déborde pas", rc["depassement"] == 0,
          f"{rc['depassement']} px")

        ra = dessiner(faux, Path(td) / "en.png", anglais=True, emballement_um=580.0,
                      corrigee=corr)
        v("la version anglaise ne laisse pas d'accent", not ra["intraduits"],
          ", ".join(ra["intraduits"][:2]))
        v("... ni de libellé intraduit", not ra["inchanges"], ", ".join(ra["inchanges"][:2]))
        v("... sans rien faire déborder", ra["depassement"] == 0)

    for nom, ok, det in ech:
        if not ok:
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))
    n, e = len(ech), sum(1 for _, ok, _ in ech if not ok)
    print(f"{'ALL PASS' if e == 0 else 'FAILURES'} ({e} failures, {n} checks)")
    return 1 if e else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("campagne", nargs="*",
                   help="le ou les JSON écrits par tools/recalage_de_la_chaine.sh")
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/images/44_matiere_de_la_chaine.png"))
    p.add_argument("--nom-chaine", help="le nom de la série — il porte un nombre, donc il "
                                        "doit être celui de la chaîne tracée")
    p.add_argument("--corrigee", nargs="*", default=[],
                   help="une seconde campagne : la chaîne qui repose sur la matière — "
                        "plusieurs JSON acceptés, recollés et dédoublonnés")
    p.add_argument("--emballement-um", type=float,
                   help="où le pas s'emballe, pour le tracer en repère")
    p.add_argument("--anglais", action="store_true")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return _verifier()
    if not a.campagne:
        p.error("le JSON de campagne est requis")
    rangs = fusionner(a.campagne)
    corr = fusionner(a.corrigee) if a.corrigee else None
    r = dessiner(rangs, a.sortie, a.anglais, a.emballement_um, corr, a.nom_chaine)
    print(f"écrit : {a.sortie}  ({r['maillons']} maillons, {r['bonds']} témoin(s), "
          f"référence {r['repere'] * 100:.0f} %)")
    print("  parts : " + "  ".join(f"{x * 100:.0f} %" for x in r["parts"]))
    av = [(x["maillage"], avantage(x)) for x in rangs if avantage(x) is not None]
    if av:
        print("  ⭐ avantage sur le hasard :")
        for nom, a_ in av:
            marque = "⚠⚠ au niveau du hasard" if a_ <= 0.02 else "⭐"
            print(f"     {nom:<14} {a_ * 100:+6.1f} points   {marque}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
