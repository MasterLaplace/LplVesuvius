#!/usr/bin/env python3
"""Jusqu'où la tangente d'une nappe reste-t-elle sur la nappe ?

⚠⚠ CE QUE LA FIGURE DOIT RENDRE ÉVIDENT : il y a un **plateau** puis une **falaise**, et pas
une pente. La forme décide du pas d'une chaîne tangentielle, donc elle vaut la peine d'être
regardée plutôt que résumée.

⚠ **Correction d'une conclusion que j'avais publiée une heure plus tôt** : sur trois points
(0, 476, 2381 µm) la dégradation paraissait progressive et monotone, et je l'ai écrit. Sur
six, elle ne l'est pas — l'amplitude MONTE jusqu'à 238 µm. Un échantillonnage grossier avait
rendu une forme fausse et parfaitement plausible. C'est la leçon de
[`43`](docs/archive/43_la_chaine_des_spires.md) §6quater sous un autre costume : les premiers
points ne discriminent pas, et une courbe se juge là où elle change.

⭐ Deux grandeurs sur un seul axe parce qu'elles disent la même chose de deux façons :
l'**amplitude** tombe (le profil s'aplatit) pendant que le **pic au bord** monte (la surface
sort de la fenêtre). Les tracer séparément laisserait croire à deux mesures indépendantes qui
se confirment, alors que c'est une seule dégradation vue de deux côtés.

⚠ L'axe des abscisses est en **micromètres**, jamais en pas de grille : un pas de grille ne
veut rien dire hors de la nappe qui l'a produit, et la question posée est physique.

⚠⚠ Et la figure porte sa propre limite : ces points mesurent une projection **pure**, sans
réoptimisation. Une vraie chaîne recollerait la nappe projetée sur la matière. C'est donc le
**plancher** de ce qu'une chaîne tangentielle peut faire, pas son plafond.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sys
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from figure_commune import police  # noqa: E402

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
AMPLITUDE = (74, 132, 96)
AU_BORD = (196, 72, 60)

ANGLAIS = {
    "jusqu'où la tangente reste-t-elle sur la feuille": "how far does the tangent stay on the sheet",
    "⚠ projection PURE, sans réoptimisation : c'est le plancher d'une chaîne, pas son plafond":
        "⚠ PURE projection, no re-optimisation: this is a chain's floor, not its ceiling",
    "amplitude du profil": "profile amplitude",
    "pic au bord de la pile": "peak at the stack edge",
    "déplacement le long de la tangente": "displacement along the tangent",
    "contrôle": "control",
    "nappe enchaînée, même distance": "chained sheet, same distance",
}




def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def monotone(valeurs: list[float], croissant: bool) -> bool:
    """La suite est-elle monotone ? — c'est l'énoncé que la figure prétend montrer.

    ⚠ Vérifié plutôt qu'affirmé : une figure qui annonce « progressif et monotone » sur des
    points qui ne le sont pas est une figure qui ment, et personne ne recompte trois nombres.
    """
    paires = zip(valeurs, valeurs[1:])
    return all((b >= a) if croissant else (b <= a) for a, b in paires)


def dessiner(points: list[dict], sortie: Path, anglais: bool = False,
             chaine: list[dict] | None = None) -> dict:
    """Amplitude et pic-au-bord contre le déplacement, sur un axe partagé.

    ⭐ `chaine` superpose des nappes **enchaînées** aux mêmes abscisses : la question que cette
    figure ne pouvait pas poser jusqu'ici est *« à distance égale, enchaîner vaut-il mieux que
    sauter ? »*, et elle se lit d'un coup d'œil si les deux vivent sur les mêmes axes.

    ⚠⚠ Les points enchaînés sont des **marqueurs**, jamais une courbe. Les relier suggérerait
    qu'on peut lire entre eux, alors que chacun est une chaîne DIFFÉRENTE, de longueur de
    maillon donnée : deux points voisins ne sont pas deux états d'une même expérience.
    """
    if len(points) < 2:
        raise ValueError("moins de deux points — une tendance a besoin d'au moins deux points")
    g1, g2, g3 = police(14, 12, 11)
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

    largeur, hauteur = 640, 356
    gx, gy = 76, 78
    gw, gh = largeur - gx - 40, hauteur - gy - 78
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)
    d.text((24, 16), T("jusqu'où la tangente reste-t-elle sur la feuille"), font=g1, fill=ENCRE)

    import math

    # ⚠⚠ ÉCHELLE LOGARITHMIQUE, et ce n'est pas une préférence. Les points couvrent 48 µm à
    # 2381 µm, un facteur cinquante : en linéaire les quatre premiers s'entassent dans le
    # premier dixième de l'axe et le PLATEAU — qui est le résultat — devient un pâté. Mesuré
    # sur le premier tirage à six points.
    #
    # ⚠ Le contrôle à 0 µm n'a pas de logarithme. Il est dessiné à part, à gauche, avec une
    # rupture d'axe visible : le fondre dans l'échelle demanderait de lui inventer une
    # abscisse, et une abscisse inventée sur un contrôle est exactement ce qu'un contrôle ne
    # doit pas avoir.
    positifs = [p for p in points if p["um"] > 0]
    controle = next((p for p in points if p["um"] <= 0), None)
    if not positifs:
        raise ValueError("aucun point à abscisse positive — un axe logarithmique en a besoin")
    lo, hi = math.log10(min(p["um"] for p in positifs)), math.log10(
        max(p["um"] for p in positifs))
    if hi <= lo:
        hi = lo + 1.0
    saut = 46 if controle else 0
    # ⚠ L'axe des y est FIXÉ de 0 à 1 pour les deux grandeurs : ce sont deux fractions, et les
    # mettre chacune à sa propre échelle ferait paraître identiques deux pentes qui ne le sont
    # pas — le piège le plus commun d'un graphe à deux courbes.
    def X(v):
        if v <= 0:
            return gx + 12
        return gx + saut + (gw - saut) * (math.log10(v) - lo) / (hi - lo)

    def Y(v):
        return gy + gh * (1.0 - max(0.0, min(1.0, v)))

    for k in range(5):
        y = gy + gh * k / 4
        d.line([(gx, y), (gx + gw, y)], fill=TRAIT, width=1)
        d.text((gx - 32, y - 7), f"{1.0 - k / 4:.2f}".replace(".", ","), font=g3, fill=GRIS)
    d.line([(gx, gy + gh), (gx + gw, gy + gh)], fill=GRIS, width=1)

    # ⚠⚠ TOUS les points ont leur trait, mais pas leur étiquette. À neuf points la zone
    # 238-476 µm en entassait cinq qui se recouvraient jusqu'à l'illisible : la figure cachait
    # exactement la région qu'elle existe pour montrer. La règle est calculable et donc
    # sondable — on n'écrit une étiquette que si elle ne touche pas la précédente.
    etiquettes_x = 0
    dernier = -1e9
    for i, p in enumerate(points):
        xp = X(p["um"])
        d.line([(xp, gy + gh), (xp, gy + gh + 5)], fill=GRIS, width=1)
        t = f"{p['um']:.0f}"
        w = d.textlength(t, font=g3)
        # ⚠ Le dernier point est toujours étiqueté : c'est la borne de l'axe, et un axe dont
        # on ne lit pas la fin ne se lit pas.
        force = i == len(points) - 1
        if xp - w / 2 >= dernier + 6 or force:
            d.text((xp - w / 2, gy + gh + 8), t, font=g3, fill=GRIS)
            dernier = xp + w / 2
            etiquettes_x += 1
    if controle:
        # La rupture d'axe, dessinée : deux barres obliques entre le contrôle et l'échelle.
        xb = gx + saut - 14
        for k in (0, 5):
            d.line([(xb + k, gy + gh + 6), (xb + k + 6, gy + gh - 4)], fill=GRIS, width=1)
    d.text((gx, gy + gh + 26), T("déplacement le long de la tangente") + " (µm)",
           font=g3, fill=GRIS)

    # ⚠⚠ La LÉGENDE est en haut, jamais au bout de la courbe. Premier tirage : les deux noms
    # de série débordaient du canevas et se superposaient à la dernière valeur — un libellé
    # coupé ne dit rien et fait douter du reste. Ici la place est connue d'avance.
    etiquettes_v = 0
    lx = gx
    for cle, couleur, nom in (("amplitude", AMPLITUDE, "amplitude du profil"),
                              ("au_bord", AU_BORD, "pic au bord de la pile")):
        d.rectangle([lx, 50, lx + 12, 58], fill=couleur)
        t = T(nom)
        d.text((lx + 17, 47), t, font=g3, fill=couleur)
        lx += 17 + int(d.textlength(t, font=g3)) + 22
    depassement = max(0, lx - (largeur - 24))

    for cle, couleur in (("amplitude", AMPLITUDE), ("au_bord", AU_BORD)):
        pts = [(X(p["um"]), Y(p[cle])) for p in points]
        d.line(pts, fill=couleur, width=2)
        # ⚠⚠ Chaque série a SON côté : l'amplitude écrit sous ses points, le pic au bord
        # écrit au-dessus. Alterner par index mélangeait les deux séries sur la même rangée,
        # et surtout collait les valeurs proches de zéro du pic au bord sur les graduations de
        # l'axe — les « 0,000 » se lisaient comme des abscisses. Séparer par SÉRIE range
        # chaque étiquette du côté où sa courbe laisse de la place.
        dessous = cle == "amplitude"
        pris = -1e9
        for i, ((x, y), p) in enumerate(zip(pts, points)):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur)
            t = f"{p[cle]:.3f}".replace(".", ",")
            w = d.textlength(t, font=g3)
            # ⚠ La dernière valeur s'écrit à GAUCHE de son point : à droite elle sortirait.
            tx = x - w - 8 if i == len(pts) - 1 else x + 7
            if tx < pris + 4 and i != len(pts) - 1:
                continue
            d.text((tx, y + 4 if dessous else y - 15), t, font=g3, fill=couleur)
            pris = tx + w
            etiquettes_v += 1

    # ⚠ Les marqueurs de chaîne sont dessinés APRÈS les courbes, donc au-dessus : un point
    # qui compte se cache sinon derrière la ligne qu'il conteste.
    chaine_traces = 0
    for pt in (chaine or []):
        if pt["um"] <= 0:
            continue
        xp = X(pt["um"])
        for cle, couleur in (("amplitude", AMPLITUDE), ("au_bord", AU_BORD)):
            if pt.get(cle) is None:
                continue
            yp = Y(pt[cle])
            # ⭐⭐ LE CONNECTEUR, et c'est lui qui porte la figure : un trait vertical du point
            # de la courbe (un seul bond) vers le losange (la même distance, enchaînée). Sans
            # lui il faut chercher lequel des deux marqueurs à cette abscisse est lequel ;
            # avec lui, l'écart SE VOIT. Deux étiquettes de plus ne le feraient pas — le
            # premier tirage en avait quatre qui se recouvraient.
            proche = min(points, key=lambda q: abs(q["um"] - pt["um"]))
            if proche.get(cle) is not None and abs(proche["um"] - pt["um"]) < pt["um"] * 0.2:
                d.line([(xp, Y(proche[cle])), (xp, yp)], fill=couleur, width=1)
            # Un losange : la même couleur que sa grandeur, une forme qui n'est pas un disque.
            d.polygon([(xp, yp - 6), (xp + 6, yp), (xp, yp + 6), (xp - 6, yp)],
                      outline=couleur, fill=FOND, width=2)
            chaine_traces += 1
    if chaine:
        d.rectangle([lx, 50, lx + 12, 58], outline=ENCRE, fill=FOND, width=2)
        te = T("nappe enchaînée, même distance")
        d.text((lx + 17, 47), te, font=g3, fill=ENCRE)
        depassement = max(depassement, lx + 17 + int(d.textlength(te, font=g3)) - (largeur - 24))

    d.text((X(points[0]["um"]) - 12, gy - 16), T("contrôle"), font=g3, fill=GRIS)
    d.line([(24, hauteur - 30), (largeur - 24, hauteur - 30)], fill=TRAIT, width=1)
    d.text((24, hauteur - 24),
           T("⚠ projection PURE, sans réoptimisation : c'est le plancher d'une chaîne, "
             "pas son plafond"), font=g3, fill=GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"points": len(points), "largeur": largeur, "hauteur": hauteur,
            "chaine_traces": chaine_traces,
            # ⚠⚠ Ce que la sonde peut vraiment vérifier : qu'aucun libellé ne dépasse du
            # canevas. Un texte coupé est invisible pour un test qui ne regarde que les
            # couleurs, et c'est exactement ce qui est passé au premier tirage.
            "depassement": int(depassement),
            # ⚠ Combien d'étiquettes ont réellement été écrites : c'est ce qui permet de
            # sonder que l'éclaircissage éclaircit vraiment, et qu'il n'écrit pas tout.
            "etiquettes_x": etiquettes_x, "etiquettes_valeurs": etiquettes_v,
            "amplitude_decroissante": monotone([p["amplitude"] for p in points], False),
            "au_bord_croissant": monotone([p["au_bord"] for p in points], True),
            "intraduits": intraduits, "inchanges": inchanges}


def points_du_depot(racine: Path, voxel_um: float = 2.4) -> list[dict]:
    """Les trois mesures, lues dans les profils écrits par la campagne."""
    out = []
    for d in sorted(racine.glob("profil_*/g*_n*/profil.json"),
                    key=lambda p: int(p.parent.parent.name.split("_")[1])):
        pas = int(d.parent.parent.name.split("_")[1])
        meta = json.loads((racine / f"pas_{pas}" / "meta.json").read_text(encoding="utf-8"))
        prof = json.loads(d.read_text(encoding="utf-8"))[0]
        out.append({"pas": pas, "um": float(meta["pas_voxels"]) * voxel_um,
                    "amplitude": float(prof["amplitude_mediane"]),
                    "au_bord": float(prof["au_bord_intensite"])})
    return out


def point_enchaine(profil: Path, meta: Path, voxel_um: float) -> dict:
    """Un point de nappe enchaînée : son profil, et la distance qu'elle a RÉELLEMENT parcourue.

    ⚠⚠ La distance ne vient PAS du nombre de maillons multiplié par le pas demandé. Un pas est
    un pas de GRILLE, donc ce qu'un maillon couvre suit la longueur des tangentes et dérive dès
    que le maillage cisaille : la chaîne à cinq maillons de 238 µm a parcouru 2 044 µm et non
    1 190. Poser un point de mesure à l'abscisse qu'on a demandée plutôt qu'à celle qu'on a
    parcourue mettrait la chaîne au mauvais endroit de l'axe — c'est-à-dire tricherait dans le
    sens qui l'avantage.
    """
    m = json.loads(meta.read_text(encoding="utf-8"))
    d = json.loads(profil.read_text(encoding="utf-8"))[0]
    # ⚠⚠ AUCUN REPLI sur `pas_voxels`. Pour une chaîne, `pas_voxels` est le DERNIER pas et
    # non le total : à cinq maillons de 95 µm il vaut 98, donc un repli poserait un point
    # parcouru de 479 µm à l abscisse 98 — au meilleur endroit possible de l axe, par accident.
    # Un maillage qui ne sait pas d où il vient n a pas sa place sur cette figure.
    if "parcouru_vox" not in m:
        raise ValueError(f"{meta} ne porte pas parcouru_vox — reprojeter la chaîne")
    um = float(m["parcouru_vox"]) * voxel_um
    return {"um": um, "amplitude": float(d["amplitude_mediane"]),
            "au_bord": float(d["au_bord_intensite"])}


def _verifier() -> int:
    import tempfile

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    v("une suite décroissante est vue décroissante", monotone([3.0, 2.0, 1.0], False))
    v("... et pas croissante", not monotone([3.0, 2.0, 1.0], True))
    v("une suite croissante est vue croissante", monotone([1.0, 2.0, 3.0], True))
    # ⚠ Un plateau est monotone au sens large : deux mesures égales ne réfutent pas une pente.
    v("un plateau est monotone", monotone([2.0, 2.0], False) and monotone([2.0, 2.0], True))
    v("une bosse ne l'est pas", not monotone([1.0, 3.0, 2.0], True))

    faux = [{"pas": 0, "um": 0.0, "amplitude": 0.19, "au_bord": 0.06},
            {"pas": 10, "um": 476.0, "amplitude": 0.11, "au_bord": 0.18},
            {"pas": 50, "um": 2381.0, "amplitude": 0.04, "au_bord": 0.61}]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(faux, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les trois points sont tracés", r["points"] == 3)
        # ⚠⚠ LE CONTRÔLE QUI PORTE LA FIGURE : elle annonce une dégradation monotone, donc
        # elle doit refuser de le dire si les points ne le sont pas.
        v("l'amplitude est vue décroissante", r["amplitude_decroissante"])
        v("le pic au bord est vu croissant", r["au_bord_croissant"])
        casse = [faux[0], {"pas": 10, "um": 476.0, "amplitude": 0.9, "au_bord": 0.01}, faux[2]]
        r2 = dessiner(casse, Path(td) / "b.png")
        v("... et une amplitude qui remonte est vue non monotone",
          not r2["amplitude_decroissante"])
        px = _pixels(Image.open(f).convert("RGB"))
        v("aucun libellé ne déborde du canevas", r["depassement"] == 0,
          f"{r['depassement']} px")
        # ⚠⚠ L'ÉCLAIRCISSAGE DOIT ÉCLAIRCIR, et il doit s'arrêter d'éclaircir. Sur neuf points
        # serrés la figure entassait cinq étiquettes qui se recouvraient jusqu'à l'illisible ;
        # une règle qui les supprimerait TOUTES serait le défaut symétrique. Les deux bornes
        # sont sondées sur un cas serré et un cas espacé.
        # ⚠ Sur un axe LOGARITHMIQUE, des points rapprochés ne se serrent que si l'axe est
        # étiré par un point lointain — ma première fixture allait de 200 à 232 µm et occupait
        # toute la largeur, donc elle ne serrait rien et le contrôle ne pouvait pas échouer.
        # C'est la forme des vraies données : une grappe, plus un point très loin.
        serre = [{"pas": i, "um": 200.0 + 10.0 * i, "amplitude": 0.2 - 0.01 * i,
                  "au_bord": 0.01 * i} for i in range(8)]
        serre.append({"pas": 9, "um": 2400.0, "amplitude": 0.04, "au_bord": 0.6})
        rs = dessiner(serre, Path(td) / "serre.png")
        v("des points serrés perdent des étiquettes", rs["etiquettes_x"] < len(serre),
          str(rs["etiquettes_x"]))
        v("... mais pas toutes", rs["etiquettes_x"] >= 2, str(rs["etiquettes_x"]))
        v("... et la borne de l'axe est toujours écrite", rs["etiquettes_x"] >= 2)
        espace = [{"pas": i, "um": 10.0 ** (i + 1), "amplitude": 0.2, "au_bord": 0.1}
                  for i in range(4)]
        re_ = dessiner(espace, Path(td) / "espace.png")
        v("des points espacés gardent toutes leurs étiquettes",
          re_["etiquettes_x"] == len(espace), str(re_["etiquettes_x"]))
        # ⭐ LA SUPERPOSITION : des nappes ENCHAÎNÉES aux mêmes abscisses, pour que « à
        # distance égale, enchaîner vaut-il mieux que sauter ? » se lise d'un coup d'œil.
        ch = [{"um": 286.0, "amplitude": 0.215, "au_bord": 0.041},
              {"um": 479.0, "amplitude": 0.149, "au_bord": 0.020}]
        rc = dessiner(faux, Path(td) / "ch.png", chaine=ch)
        v("chaque point enchaîné trace ses DEUX grandeurs", rc["chaine_traces"] == 4,
          str(rc["chaine_traces"]))
        v("sans chaîne, aucun marqueur", r["chaine_traces"] == 0)
        # ⚠ Un point enchaîné à abscisse nulle n'a pas de logarithme : il est SAUTÉ, jamais
        # rangé au bord comme le contrôle — un contrôle est une mesure, un point de chaîne à
        # zéro serait une chaîne qui n'a pas bougé.
        rz = dessiner(faux, Path(td) / "chz.png",
                      chaine=[{"um": 0.0, "amplitude": 0.2, "au_bord": 0.0}])
        v("un point enchaîné à zéro est sauté", rz["chaine_traces"] == 0)
        v("... et la légende de chaîne ne déborde pas", rc["depassement"] == 0,
          f"{rc['depassement']} px")

        # ⚠⚠ `point_enchaine` REFUSE un meta sans `parcouru_vox`. Pour une chaîne,
        # `pas_voxels` est le DERNIER pas et non le total : à cinq maillons de 95 µm il vaut
        # 98, donc un repli poserait un point parcouru de 479 µm à l'abscisse 98 — au meilleur
        # endroit possible de l'axe, par accident.
        mj = Path(td) / "m.json"
        pj = Path(td) / "p.json"
        pj.write_text(json.dumps([{"amplitude_mediane": 0.15, "au_bord_intensite": 0.02}]))
        mj.write_text(json.dumps({"pas_voxels": 41.0}))
        try:
            point_enchaine(pj, mj, 2.4)
            v("un meta sans parcouru_vox est refusé", False)
        except ValueError:
            v("un meta sans parcouru_vox est refusé", True)
        mj.write_text(json.dumps({"parcouru_vox": 200.0, "pas_voxels": 41.0}))
        pt = point_enchaine(pj, mj, 2.4)
        v("... et le cumul est lu, pas le dernier pas", abs(pt["um"] - 480.0) < 1e-9,
          str(pt["um"]))
        v("... avec son profil", abs(pt["amplitude"] - 0.15) < 1e-9)

        v("la courbe d'amplitude est tracée", AMPLITUDE in px)
        v("celle du pic au bord aussi", AU_BORD in px)
        try:
            dessiner([faux[0]], Path(td) / "c.png")
            v("un seul point est refusé", False)
        except ValueError:
            v("un seul point est refusé", True)
        r3 = dessiner(faux, Path(td) / "en.png", anglais=True)
        v("aucun libellé ne reste en français", not r3["intraduits"],
          ", ".join(r3["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r3["inchanges"], ", ".join(r3["inchanges"]))
        # ⚠⚠ Le débordement se vérifie AUSSI en anglais : « profile amplitude » et « peak at
        # the stack edge » sont plus longs que leurs équivalents français, donc une légende
        # qui tient en français peut sortir du canevas une fois traduite. Ma première version
        # de ce contrôle était écrite `if False else True` — une sonde incapable d'échouer,
        # dans une session qui n'a parlé que de ça.
        v("... et aucun ne déborde en anglais non plus", r3["depassement"] == 0,
          f"{r3['depassement']} px")

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--racine", type=Path, default=Path("data/portee_tangentielle"))
    p.add_argument("--voxel-um", type=float, default=2.4)
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/images/44_portee_tangentielle.png"))
    p.add_argument("--chaine", nargs="*", default=[],
                   help="des profils de nappes ENCHAÎNÉES à superposer : "
                        "<profil.json>:<meta.json> par point")
    p.add_argument("--anglais", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return _verifier()
    pts = points_du_depot(a.racine, a.voxel_um)
    if len(pts) < 2:
        print(f"refus : {len(pts)} point(s) dans {a.racine} — il en faut au moins deux",
              file=sys.stderr)
        return 3
    ch = [point_enchaine(Path(x.split(":")[0]), Path(x.split(":")[1]), a.voxel_um)
          for x in a.chaine]
    r = dessiner(pts, a.sortie, a.anglais, chaine=ch or None)
    print(f"écrit : {a.sortie}  ({r['points']} points, "
          f"amplitude {'décroissante' if r['amplitude_decroissante'] else '⚠ NON monotone'}, "
          f"pic au bord {'croissant' if r['au_bord_croissant'] else '⚠ NON monotone'})")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"points": pts, **{k: v for k, v in r.items()
                                                        if k.startswith(("amplitude", "au_bord"))}},
                                     indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
