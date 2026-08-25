#!/usr/bin/env python3
"""Un écart posé sur le bord de la fenêtre est une FLÈCHE, pas un point.

⚠⚠ **Le dessin porte toute l'idée, et le choix du symbole en est le cœur.** α est la pente
d'une droite entre deux mesures en log-log. Quand un écart est posé exactement sur la
demi-fenêtre, ce n'est pas une distance mesurée : c'est un **minorant** — le pic est au
moins là, peut-être bien plus loin. Le dessiner comme un point rond affirme une position ;
le dessiner comme une flèche vers le haut dit ce qu'on sait, et rien de plus.

⭐ Ce que la figure doit rendre évident, et qu'aucun tableau ne rend : selon **quel** appui
est une flèche, l'éventail des pentes vraies part d'un côté ou de l'autre. Un appui étroit
au bord ne peut que faire *baisser* α, donc il préserve une convergence. Deux appuis au bord
ouvrent l'éventail des deux côtés : il ne reste rien.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import police  # noqa: E402

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
MESURE = (86, 104, 132)
BORNE = (176, 128, 62)
PERDU = (196, 72, 60)
SAUVE = (74, 132, 96)


def _pale(c, f=0.16):
    """La couleur diluée dans le fond — un remplissage ne doit pas voler le trait."""
    return tuple(int(FOND[i] + (c[i] - FOND[i]) * f) for i in range(3))

NE_PAS_TRADUIRE: set[str] = set()

ANGLAIS = {
    "un écart au bord de la fenêtre est une flèche, pas un point":
        "a gap at the window edge is an arrow, not a point",
    "α est la pente entre deux appuis — un appui qui ne mesure rien n'en est pas un":
        "α is the slope between two footings — a footing that measures nothing is not one",
    "profondeur de fenêtre (µm)": "window depth (µm)",
    "écart au pic (µm)": "gap to the peak (µm)",
    "écart": "gap",
    "au pic": "to peak",
    "(µm)": "(µm)",
    "appui mesuré": "measured footing",
    "appui au bord — minorant": "footing at the edge — lower bound",
    "éventail des pentes vraies": "fan of true slopes",
    "les deux appuis au bord :": "both footings at the edge:",
    "α ne porte rien": "α carries nothing",
    "appui étroit au bord : α est un majorant,":
        "narrow footing at the edge: α is an upper bound,",
    "la convergence tient": "convergence holds",
    "verdict perdu": "verdict lost",
    "verdict conservé": "verdict held",
    "α mesuré ": "α measured ",
    "sur les ": "of the ",
    " séries jugeables : ": " judgeable series: ",
    " à deux appuis mesurés, ": " on two measured footings, ",
    " sauvées par le signe, ": " saved by the sign, ",
    " sans appui qui porte": " with no footing that holds",
    "aucune des ": "none of the ",
    " séries convergentes n'est perdue": " converging series is lost",
}


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())




def pente(p0: tuple[float, float], p1: tuple[float, float]) -> float:
    """La pente log-log entre deux appuis — la définition même de α."""
    return math.log(p1[1] / p0[1]) / math.log(p1[0] / p0[0])


def _couper(u: tuple[int, int], w: tuple[int, int],
            cadre: tuple[int, int, int, int]) -> tuple | None:
    """Le segment `u→w` réduit à sa portion dans `cadre`, ou None s'il n'y entre pas.

    ⚠ Découpage de Liang-Barsky, écrit ici plutôt qu'approché par un `min`/`max` sur les
    extrémités : rogner les bouts d'un segment oblique déplace sa PENTE, et c'est
    exactement la grandeur que la figure existe pour montrer.
    """
    x0, y0 = u
    dx, dy = w[0] - x0, w[1] - y0
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, x0 - cadre[0]), (dx, cadre[2] - x0),
                   (-dy, y0 - cadre[1]), (dy, cadre[3] - y0)):
        if pk == 0:
            if qk < 0:
                return None
            continue
        r = qk / pk
        if pk < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
    if t0 > t1:
        return None
    return ((int(x0 + t0 * dx), int(y0 + t0 * dy)),
            (int(x0 + t1 * dx), int(y0 + t1 * dy)))


def dessiner(cas: list[dict], recensement: dict, sortie: Path,
             anglais: bool = False) -> dict:
    """Deux panneaux côte à côte, un par cas, plus le recensement en pied.

    ⚠ Les deux panneaux partagent leurs échelles : deux cadres aux axes différents se
    comparent à l'œil comme s'ils étaient les mêmes, et c'est faux.
    """
    if len(cas) != 2:
        raise ValueError("deux cas exactement : celui qui perd et celui qui tient")
    p, pp, pg = police(13, 11, 15)
    tous = [q for c in cas for q in c["points"]]
    xmin = min(x for x, _ in tous)
    xmax = max(x for x, _ in tous)
    ymin = min(y for _, y in tous)
    ymax = max(y for _, y in tous)

    marge, larg, haut, ecart = 84, 372, 300, 74
    L = marge + larg * 2 + ecart + 34
    H = marge + haut + 168
    img = Image.new("RGB", (L, H), FOND)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)
    # ⚠⚠ Le nom d'une série est un CHEMIN de données, pas de la prose : il ne passe pas
    # par la table. Le faire passer obligerait à l'excuser dans le garde de langue, et
    # une exception muette est précisément le trou que `inchanges` a été écrit pour
    # fermer. Il est donc dessiné par le crayon BRUT, et la batterie vérifie qu'il sort
    # pixel pour pixel identique dans les deux langues.
    brut = ImageDraw.Draw(img)
    noms = []

    d.text((marge, 22), "un écart au bord de la fenêtre est une flèche, pas un point",
           fill=ENCRE, font=pg)
    d.text((marge, 43),
           "α est la pente entre deux appuis — un appui qui ne mesure rien n'en est pas un",
           fill=GRIS, font=pp)

    fleches = graduations = 0
    # ⚠ On note la FORME du domaine par panneau et non un compte de traits : un
    # compte serait satisfait par deux panneaux dessinés pareil, ce qui est
    # exactement l'erreur que la figure existe pour éviter.
    domaines: list[str] = []
    for i, c in enumerate(cas):
        gx = marge + i * (larg + ecart)

        def X(v, gx=gx):
            f = (math.log10(v) - math.log10(xmin * 0.8)) / \
                (math.log10(xmax * 1.25) - math.log10(xmin * 0.8))
            return gx + int(f * larg)

        def Y(v):
            f = (math.log10(v) - math.log10(ymin * 0.55)) / \
                (math.log10(ymax * 1.30) - math.log10(ymin * 0.55))
            return marge + haut - int(f * haut)

        d.line([(gx, marge + haut), (gx + larg, marge + haut)], fill=TRAIT)
        d.line([(gx, marge), (gx, marge + haut)], fill=TRAIT)
        for dec in (10, 100, 1000):
            for mult in (1, 2, 5):
                val = dec * mult
                if xmin * 0.8 <= val <= xmax * 1.25:
                    d.line([(X(val), marge + haut), (X(val), marge + haut + 4)], fill=GRIS)
                    d.text((X(val) - 10, marge + haut + 8), f"{val}", fill=GRIS, font=pp)
                    graduations += 1
                if i == 0 and ymin * 0.55 <= val <= ymax * 1.30:
                    d.line([(gx - 4, Y(val)), (gx, Y(val))], fill=GRIS)
                    d.text((gx - 34, Y(val) - 7), f"{val}", fill=GRIS, font=pp)
                    graduations += 1

        (x0, y0), (x1, y1) = c["points"]
        a = pente((x0, y0), (x1, y1))

        # ⚠⚠ Un rayon qui sort du cadre n'est pas seulement laid : il donne à lire une
        # pente que la figure ne montre pas jusqu'au bout, et le lecteur la prolonge dans
        # sa tête sans savoir où elle finit. On coupe au cadre, en gardant la direction.
        cadre = (gx + 1, marge + 1, gx + larg - 1, marge + haut - 1)

        def rayon(ax, ay, bx, by, couleur):
            u, w = (X(ax), Y(ay)), (X(bx), Y(by))
            seg = _couper(u, w, cadre)
            if seg:
                d.line([seg[0], seg[1]], fill=couleur, width=1)
                return 1
            return 0

        # ⚠⚠ L'EVENTAIL, qui est la vraie information. Un appui au bord peut monter, donc
        # la pente vraie balaie tout ce qui reste atteignable. On le dessine en rayons
        # depuis l'appui qui, lui, est fixe -- sinon le lecteur croirait la droite unique.
        couleur_ev = PERDU if not c["tient"] else SAUVE
        # ⚠⚠ **Un appui au bord PIVOTE autour de l'autre.** C'est ce qui rend le domaine
        # des pentes vraies dessinable : un appui fixe donne un sommet, et le domaine est
        # le coin qui s'ouvre depuis lui. Dessiner deux rayons libres a la place donnait
        # deux droites qui se croisent, ce qui se lit comme du bruit et pas comme un
        # domaine — mesure faite en regardant la premiere version de cette figure.
        if c["bord_etroit"] and c["bord_large"]:
            # ⚠⚠ AUCUN appui n'est fixe, donc il n'y a pas de coin : toute pente reste
            # possible. Le dire par un lavis sur TOUT le cadre est la seule forme honnete —
            # un coin, meme large, laisserait croire qu'une partie est exclue.
            d.rectangle([cadre[0], cadre[1], cadre[2], cadre[3]],
                        fill=_pale(couleur_ev))
            domaines.append("tout le cadre")
        elif c["bord_etroit"] or c["bord_large"]:
            fixe = (x1, y1) if c["bord_etroit"] else (x0, y0)
            mobile = (x0, y0) if c["bord_etroit"] else (x1, y1)
            haut_mobile = (mobile[0], mobile[1] * 2.6)
            # ⚠⚠ Le coin est dessiné dans un calque à la TAILLE DU PANNEAU puis collé :
            # PIL rogne alors tout seul ce qui sort. Rabattre le sommet sur le haut du
            # cadre aurait marché à l'œil et changé l'angle du coin — c'est-à-dire
            # l'étendue des pentes admissibles, la seule chose que ce coin dit.
            calque = Image.new("RGB", (larg - 2, haut - 2), FOND)
            ImageDraw.Draw(calque).polygon(
                [(X(fixe[0]) - cadre[0], Y(fixe[1]) - cadre[1]),
                 (X(mobile[0]) - cadre[0], Y(mobile[1]) - cadre[1]),
                 (X(haut_mobile[0]) - cadre[0], Y(haut_mobile[1]) - cadre[1])],
                fill=_pale(couleur_ev))
            img.paste(calque, (cadre[0], cadre[1]))
            domaines.append("coin")
            rayon(fixe[0], fixe[1], haut_mobile[0], haut_mobile[1], couleur_ev)

        d.line([(X(x0), Y(y0)), (X(x1), Y(y1))], fill=ENCRE, width=2)

        for (xv, yv), au_bord in ((c["points"][0], c["bord_etroit"]),
                                  (c["points"][1], c["bord_large"])):
            px, py = X(xv), Y(yv)
            if au_bord:
                # ⚠ La fleche pointe vers le HAUT parce que la valeur vraie est PLUS
                # GRANDE : le pic est au moins la. Vers le bas, elle dirait l'inverse.
                d.line([(px, py), (px, py - 26)], fill=BORNE, width=3)
                d.polygon([(px - 6, py - 22), (px + 6, py - 22), (px, py - 34)], fill=BORNE)
                d.ellipse([px - 4, py - 4, px + 4, py + 4], outline=BORNE, width=2)
                fleches += 1
            else:
                d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=MESURE)

        for k, ligne in enumerate(c["titre"]):
            d.text((gx, marge + haut + 54 + k * 18), ligne, fill=ENCRE, font=p)
        base = marge + haut + 54 + len(c["titre"]) * 18 + 4
        # ⚠ La position du second libellé se MESURE au lieu d'être posée à 108 px : en
        # anglais les deux se touchaient et se lisaient comme une seule phrase.
        gauche = "α mesuré " + f"{a:+.2f}"
        d.text((gx, base), gauche, fill=GRIS, font=pp)
        d.text((gx + int(brut.textlength(d.traduire(gauche), font=pp)) + 22, base),
               "verdict conservé" if c["tient"] else "verdict perdu",
               fill=SAUVE if c["tient"] else PERDU, font=pp)
        # ⚠ Le nom va AU-DESSUS du cadre et non dedans : posé à l'intérieur, il tombait sur
        # le domaine dans un panneau et sur une flèche dans l'autre, et le déplacer d'un
        # coin à l'autre n'aurait fait que déplacer la collision.
        brut.text((gx, marge - 18), c["nom"], fill=GRIS, font=pp)
        noms.append(c["nom"])

    d.text((marge + larg // 2 - 60, marge + haut + 26), "profondeur de fenêtre (µm)",
           fill=GRIS, font=pp)
    d.text((4, marge + haut // 2 - 20), "écart", fill=GRIS, font=pp)
    d.text((4, marge + haut // 2 - 4), "au pic", fill=GRIS, font=pp)
    d.text((4, marge + haut // 2 + 12), "(µm)", fill=GRIS, font=pp)

    r = recensement
    d.text((marge, H - 44),
           "sur les " + f"{r['series_jugees']}" + " séries jugeables : "
           + f"{r['exactes']}" + " à deux appuis mesurés, " + f"{r['sauvees']}"
           + " sauvées par le signe, " + f"{r['perdues']}" + " sans appui qui porte",
           fill=ENCRE, font=p)
    d.text((marge, H - 21),
           "aucune des " + f"{r['convergentes']}" + " séries convergentes n'est perdue",
           fill=SAUVE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"largeur": L, "hauteur": H, "fleches": fleches,
            "graduations": graduations, "noms": noms, "domaines": domaines,
            "bande_des_noms": (0, marge - 20, L, marge - 2),
            "intraduits": d.intraduits() if anglais else [],
            "inchanges": d.inchanges() if anglais else []}


def depuis_le_json(j: dict) -> tuple[list[dict], dict]:
    """Les deux cas et le recensement, tirés de la sortie d'`appui_de_pente`.

    ⚠ Les deux cas ne sont pas choisis à la main : le perdu est la première série dont
    **les deux** appuis sont au bord, le sauvé la première convergente qu'un signe protège.
    Les nommer en dur les figerait le jour où l'arbre change.
    """
    det = j["detail"]
    perdu = next((k for k, x in sorted(det.items())
                  if x["appui_etroit"] == "au_bord" and x["appui_large"] == "au_bord"), None)
    sauve = next((k for k, x in sorted(det.items())
                  if x["tient"] and x["borne"] in ("majorant", "minorant")), None)
    if not perdu or not sauve:
        raise ValueError("il faut un cas perdu et un cas sauvé dans le recensement")
    cas = []
    for k, titre in ((perdu, ["les deux appuis au bord :", "α ne porte rien"]),
                     (sauve, ["appui étroit au bord : α est un majorant,",
                              "la convergence tient"])):
        x = det[k]
        cas.append({"nom": Path(k).parent.name + "/" + Path(k).name,
                    "titre": titre,
                    "points": [(float(x["couches"][0]), float(x["ecarts_um"][0])),
                               (float(x["couches"][1]), float(x["ecarts_um"][1]))],
                    "bord_etroit": x["appui_etroit"] == "au_bord",
                    "bord_large": x["appui_large"] == "au_bord",
                    "tient": bool(x["tient"])})
    rec = {"series_jugees": j["series_jugees"],
           "exactes": j["par_borne"].get("exacte", 0),
           "sauvees": len(j["series_sauvees_par_le_signe"]),
           "perdues": len(j["series_qui_tombent"]),
           "convergentes": j["convergents"],
           "convergentes_perdues": len(j["convergents_qui_tombent"])}
    return cas, rec


def _verifier() -> int:
    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    v("la pente d'un doublement pour un doublement vaut 1",
      abs(pente((41, 48.0), (161, 192.0)) - 1.0) < 0.02,
      f"{pente((41, 48.0), (161, 192.0)):.4f}")
    v("une distance figée donne une pente nulle",
      abs(pente((41, 100.0), (161, 100.0))) < 1e-9)

    # --- le decoupage au cadre ----------------------------------------------------------
    cadre = (0, 0, 100, 100)
    v("un segment entièrement dedans n'est pas touché",
      _couper((10, 10), (90, 90), cadre) == ((10, 10), (90, 90)))
    v("un segment entièrement dehors est refusé",
      _couper((-50, -50), (-10, -10), cadre) is None)
    # ⚠⚠ Le controle qui compte : la PENTE doit survivre au decoupage. Rogner les bouts
    # d'un oblique par un min/max la deplacerait, et c'est la grandeur que la figure montre.
    seg = _couper((-100, -100), (200, 200), cadre)
    v("un segment coupé garde sa pente",
      seg is not None
      and abs((seg[1][1] - seg[0][1]) / (seg[1][0] - seg[0][0]) - 1.0) < 0.02,
      str(seg))
    v("un segment vertical hors cadre est refusé",
      _couper((-5, -50), (-5, 150), cadre) is None)

    faux = {"series_jugees": 132,
            "par_borne": {"exacte": 92, "majorant": 14, "aucune": 26},
            "series_sauvees_par_le_signe": ["data/spires/spire05"] * 7,
            "series_qui_tombent": ["x"] * 33, "convergents": 75,
            "convergents_qui_tombent": [],
            "detail": {
                "data/paris4_candidats/ps256_c0": {
                    "alpha": 1.0135, "appui_etroit": "au_bord", "appui_large": "au_bord",
                    "borne": "aucune", "tient": False, "couches": [41, 161],
                    "ecarts_um": [48.0, 192.0]},
                "data/spires/spire05": {
                    "alpha": 0.2995, "appui_etroit": "au_bord", "appui_large": "mesure",
                    "borne": "majorant", "tient": True, "couches": [31, 81],
                    "ecarts_um": [129.6, 172.8]}}}
    cas, rec = depuis_le_json(faux)
    v("le cas PERDU est celui dont les deux appuis sont au bord",
      cas[0]["bord_etroit"] and cas[0]["bord_large"] and not cas[0]["tient"])
    v("le cas SAUVÉ n'a que son appui étroit au bord",
      cas[1]["bord_etroit"] and not cas[1]["bord_large"] and cas[1]["tient"])
    v("le recensement reprend les comptes sans les recalculer",
      rec["exactes"] == 92 and rec["perdues"] == 33 and rec["convergentes"] == 75)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(cas, rec, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        # ⚠⚠ TROIS fleches et pas quatre : le cas sauve n'en a qu'une. Compter « au moins
        # une » laisserait passer un dessin qui met une fleche partout, ce qui effacerait
        # justement la difference entre les deux panneaux.
        v("il y a exactement trois flèches — deux à gauche, une à droite",
          r["fleches"] == 3, str(r["fleches"]))
        # ⚠⚠ Les DEUX formes doivent apparaitre, et pas deux fois la meme : un coin dit
        # « une part des pentes est exclue », un lavis dit « aucune ne l'est ». Compter des
        # traits laisserait passer deux panneaux dessines pareil.
        v("les deux formes de domaine sont dessinées, une par panneau",
          r["domaines"] == ["tout le cadre", "coin"], str(r["domaines"]))
        # ⚠ Un rayon coupe a zero longueur serait compte comme dessine. On verifie que le
        # cadre du panneau est le seul endroit ou l'encre des eventails apparait.
        im = Image.open(f).convert("RGB")
        # ⚠ Les couleurs PALES comptent aussi : c'est le lavis et le coin qui debordaient,
        # pas les traits, et la premiere version de ce controle ne regardait que les traits.
        encres = {PERDU, SAUVE, _pale(PERDU), _pale(SAUVE)}
        haut_cadre = r["bande_des_noms"][1]
        hors = [(x, y) for x in range(0, im.width, 3)
                for y in range(0, max(2, haut_cadre - 2), 2)
                if im.getpixel((x, y)) in encres]
        v("aucun domaine ne déborde au-dessus des cadres", not hors, str(hors[:4]))
        px = _pixels(Image.open(f).convert("RGB"))
        v("les appuis mesurés sont dessinés", MESURE in px)
        v("les appuis au bord portent leur couleur", BORNE in px)
        v("l'éventail perdu est dessiné", PERDU in px)
        v("l'éventail sauvé aussi", SAUVE in px)
        v("les deux axes portent des graduations", r["graduations"] >= 6,
          str(r["graduations"]))
        f2 = Path(td) / "en.png"
        r2 = dessiner(cas, rec, f2, anglais=True)
        v("aucun libellé ne reste en français", not r2["intraduits"],
          ", ".join(r2["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r2["inchanges"], ", ".join(r2["inchanges"]))
        # ⚠⚠ Le nom de serie ne doit PAS etre excuse dans le garde : il doit ne jamais y
        # entrer. On le verifie par les pixels plutot que par une liste d'exceptions --
        # la bande qui les porte doit etre identique octet pour octet dans les deux
        # langues, ce qu'une exception declaree ne prouverait pas.
        bande = tuple(r2["bande_des_noms"])
        a_fr = Image.open(f).convert("RGB").crop(bande).tobytes()
        a_en = Image.open(f2).convert("RGB").crop(bande).tobytes()
        v("les noms de série sortent identiques dans les deux langues", a_fr == a_en)
        v("... et il y en a bien deux", len(r2["noms"]) == 2, str(r2["noms"]))
        try:
            dessiner(cas[:1], rec, Path(td) / "un.png")
            v("un seul cas est refusé", False)
        except ValueError:
            v("un seul cas est refusé", True)
        # ⚠ Un recensement sans cas perdu ne doit pas rendre une figure a moitie vraie.
        try:
            depuis_le_json({**faux, "detail": {k: x for k, x in faux["detail"].items()
                                               if x["tient"]}})
            v("un recensement sans cas perdu est refusé", False)
        except ValueError:
            v("un recensement sans cas perdu est refusé", True)

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=Path("docs/appui_de_pente.json"))
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/51_appuis.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not a.json.is_file():
        print(f"absent : {a.json}", file=sys.stderr)
        return 2
    cas, rec = depuis_le_json(json.loads(a.json.read_text(encoding="utf-8")))
    r = dessiner(cas, rec, a.sortie, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ non traduits : " + ", ".join(r["intraduits"] + r["inchanges"]),
              file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, "
          f"{r['fleches']} flèches, domaines {r['domaines']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
