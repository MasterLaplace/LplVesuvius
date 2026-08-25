#!/usr/bin/env python3
"""Le plancher de détection, et de quel côté chaque fenêtre tombe.

⚠⚠ **Le dessin dit ce qu'un tableau de β cache.** La question n'est pas « de combien
l'amplitude croît » mais « à quelle profondeur elle passe le plancher », et c'est une
lecture d'intersection : deux points, une droite en log-log, une horizontale. Le point où
elles se croisent est la fenêtre à rendre.

⭐ Et il fallait le dessiner pour voir la chose qui compte : la cible tombe **entre** les
deux profondeurs déjà mesurées. Ce n'est donc pas une extrapolation, c'est une interpolation
— la distinction que ce dépôt paie cher quand elle est perdue.
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
SOUS = (196, 72, 60)
AU_DESSUS = (74, 132, 96)
PLANCHER = (28, 30, 34)
MARGE_C = (176, 128, 62)
CIBLE = (86, 104, 132)

ANGLAIS = {
    "le plancher de détection, et la fenêtre qu'il faut rendre":
        "the detection floor, and the window that must be rendered",
    "amplitude du relief contre la profondeur de fenêtre — échelles logarithmiques":
        "relief amplitude against window depth — logarithmic axes",
    "profondeur de fenêtre (couches)": "window depth (layers)",
    "amplitude du relief": "relief amplitude",
    "plancher de détection": "detection floor",
    "marge de recommandation": "recommendation margin",
    "cible ": "target ",
    " couches": " layers",
    "mesuré": "measured",
    "les deux fenêtres actuelles encadrent le plancher : la cible est une interpolation":
        "the two current windows bracket the floor: the target is an interpolation",
}


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())




def croisement(pts: list[tuple[float, float]], cible: float) -> float | None:
    """La profondeur à laquelle l'amplitude atteint `cible`, sur la droite log-log.

    ⚠ Recalculée ici depuis les points DESSINÉS, jamais recopiée du JSON : une figure dont
    le trait et l'annotation viennent de deux sources peut les montrer en désaccord sans que
    rien ne le signale.
    """
    if len(pts) < 2 or cible <= 0:
        return None
    (n0, a0), (n1, a1) = min(pts), max(pts)
    if a0 <= 0 or a1 <= 0 or n1 <= n0 or a1 == a0:
        return None
    b = math.log(a1 / a0) / math.log(n1 / n0)
    if b <= 0:
        return None
    return n0 * (cible / a0) ** (1.0 / b)


def dessiner(series: list[dict], plancher: float, marge: float, sortie: Path,
             anglais: bool = False) -> dict:
    if not series:
        raise ValueError("aucune série")
    p, pp, pg = police(13, 11, 15)
    tous = [q for s in series for q in s["points"]]
    xmin = min(x for x, _ in tous)
    xmax = max(x for x, _ in tous)
    ymin = min([y for _, y in tous] + [plancher])
    ymax = max([y for _, y in tous] + [plancher * marge])

    marge_px, larg, haut = 96, 540, 320
    L, H = marge_px + larg + 210, marge_px + haut + 110
    img = Image.new("RGB", (L, H), FOND)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)
    brut = ImageDraw.Draw(img)

    def X(v):
        f = (math.log10(v) - math.log10(xmin * 0.75)) / \
            (math.log10(xmax * 1.35) - math.log10(xmin * 0.75))
        return marge_px + int(f * larg)

    def Y(v):
        f = (math.log10(v) - math.log10(ymin * 0.7)) / \
            (math.log10(ymax * 1.5) - math.log10(ymin * 0.7))
        return marge_px + haut - int(f * haut)

    d.text((marge_px, 26), "le plancher de détection, et la fenêtre qu'il faut rendre",
           fill=ENCRE, font=pg)
    d.text((marge_px, 47),
           "amplitude du relief contre la profondeur de fenêtre — échelles logarithmiques",
           fill=GRIS, font=pp)

    d.line([(marge_px, marge_px + haut), (marge_px + larg, marge_px + haut)], fill=TRAIT)
    d.line([(marge_px, marge_px), (marge_px, marge_px + haut)], fill=TRAIT)
    graduations = 0
    for val in (20, 41, 81, 161, 321):
        if xmin * 0.75 <= val <= xmax * 1.35:
            d.line([(X(val), marge_px + haut), (X(val), marge_px + haut + 5)], fill=GRIS)
            brut.text((X(val) - 10, marge_px + haut + 9), f"{val}", fill=GRIS, font=pp)
            graduations += 1
    for val in (0.01, 0.02, 0.05, 0.1):
        if ymin * 0.7 <= val <= ymax * 1.5:
            d.line([(marge_px - 5, Y(val)), (marge_px, Y(val))], fill=GRIS)
            brut.text((marge_px - 42, Y(val) - 7), f"{val:g}", fill=GRIS, font=pp)
            graduations += 1

    # ⚠⚠ Le plancher est une LIGNE PLEINE et la marge une ligne pointillee : le premier est
    # une propriete de l'instrument, la seconde une prudence qu'on s'impose. Les dessiner
    # pareil les ferait lire comme deux seuils de meme nature.
    d.line([(marge_px, Y(plancher)), (marge_px + larg, Y(plancher))], fill=PLANCHER, width=2)
    d.text((marge_px + larg + 10, Y(plancher) - 7), "plancher de détection",
           fill=PLANCHER, font=pp)
    for t in range(marge_px, marge_px + larg, 10):
        d.line([(t, Y(plancher * marge)), (t + 5, Y(plancher * marge))], fill=MARGE_C)
    d.text((marge_px + larg + 10, Y(plancher * marge) - 7), "marge de recommandation",
           fill=MARGE_C, font=pp)

    cibles = []
    for i, s in enumerate(series):
        q = sorted(s["points"])
        for a, b in zip(q, q[1:]):
            d.line([(X(a[0]), Y(a[1])), (X(b[0]), Y(b[1]))], fill=CIBLE, width=2)
        for x, y in q:
            c = AU_DESSUS if y >= plancher else SOUS
            d.ellipse([X(x) - 5, Y(y) - 5, X(x) + 5, Y(y) + 5], fill=c)
        n = croisement(q, plancher * marge)
        if n:
            cibles.append(n)
        brut.text((marge_px + larg + 10, marge_px + 6 + i * 17), s["nom"], fill=GRIS, font=pp)

    if cibles:
        n0, n1 = min(cibles), max(cibles)
        # ⚠ Une BANDE et non un trait : trois séries donnent trois croisements, et n'en
        # dessiner qu'un ferait passer une dispersion pour une valeur.
        for xv in (n0, n1):
            for t in range(marge_px, marge_px + haut, 8):
                d.line([(X(xv), t), (X(xv), t + 4)], fill=CIBLE)
        d.text((X(n1) + 8, marge_px + haut - 24),
               "cible " + f"{n0:.0f}–{n1:.0f}" + " couches", fill=CIBLE, font=p)

    d.text((marge_px + larg // 2 - 90, marge_px + haut + 32),
           "profondeur de fenêtre (couches)", fill=GRIS, font=pp)
    # ⚠ Le libellé de l'axe vertical est posé AU-DESSUS de l'axe et non à côté : PIL ne
    # tourne pas le texte, et le découper en deux lignes courtes avait produit un fragment
    # (« amplitude ») identique dans les deux langues, que le garde de langue signale à
    # juste titre comme non touché par la table.
    d.text((marge_px - 44, marge_px - 22), "amplitude du relief", fill=GRIS, font=pp)
    d.text((marge_px, H - 28),
           "les deux fenêtres actuelles encadrent le plancher : la cible est une "
           "interpolation", fill=ENCRE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"largeur": L, "hauteur": H, "series": len(series), "graduations": graduations,
            "cibles": [round(x, 1) for x in sorted(cibles)],
            "intraduits": d.intraduits() if anglais else [],
            "inchanges": d.inchanges() if anglais else []}


def depuis_le_json(j: dict, prefixe: str = "data/paris4_candidats/ps256") -> list[dict]:
    """Les séries du recensement dont le nom commence par `prefixe`.

    ⚠ Un préfixe et non une liste écrite à la main : nommer les trois candidats en dur
    figerait la figure le jour où une quatrième trace arrive, et la figure resterait juste
    en apparence.
    """
    out = []
    for k, s in sorted(j["detail"].items()):
        if not k.startswith(prefixe):
            continue
        amp = s.get("amplitudes") or []
        prof = s.get("profondeurs") or []
        if len(amp) != len(prof) or len(amp) < 2:
            continue
        out.append({"nom": Path(k).name,
                    "points": [(float(n), float(a)) for n, a in zip(prof, amp)]})
    return out


def _verifier() -> int:
    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    # ⚠ Le croisement : amplitude doublant pour une fenetre doublant (β = 1), plancher a
    # mi-chemin -> la profondeur est le milieu geometrique.
    n = croisement([(41.0, 0.01), (161.0, 0.04)], 0.02)
    v("le croisement se calcule sur la droite log-log", n and abs(n - 82.0) < 1.0,
      f"{n:.2f}" if n else "None")
    v("une amplitude décroissante n'a pas de croisement",
      croisement([(41.0, 0.04), (161.0, 0.01)], 0.02) is None)
    v("un seul point n'a pas de croisement", croisement([(41.0, 0.01)], 0.02) is None)

    faux = {"detail": {
        "data/paris4_candidats/ps256_c0": {"profondeurs": [41, 161],
                                           "amplitudes": [0.0175, 0.0462]},
        "data/paris4_candidats/ps256_c2": {"profondeurs": [41, 161],
                                           "amplitudes": [0.0138, 0.0618]},
        "data/spires/spire05": {"profondeurs": [31, 81], "amplitudes": [0.09, 0.12]}}}
    s = depuis_le_json(faux)
    v("le préfixe sélectionne les candidats et rien d'autre", len(s) == 2,
      str([x["nom"] for x in s]))
    v("une série dont les listes ne s'accordent pas est écartée",
      depuis_le_json({"detail": {"data/paris4_candidats/ps256_cX":
                                 {"profondeurs": [41, 161], "amplitudes": [0.01]}}}) == [])

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(s, 0.02, 1.33, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les deux séries sont dessinées", r["series"] == 2)
        v("les deux axes portent des graduations", r["graduations"] >= 5,
          str(r["graduations"]))
        px = _pixels(Image.open(f).convert("RGB"))
        # ⚠⚠ Le controle qui porte la figure : les points SOUS le plancher et ceux
        # AU-DESSUS ne portent pas la meme couleur. Une figure ou tout est de la meme
        # teinte laisse le lecteur chercher le plancher au lieu de le voir.
        v("les points sous le plancher sont distingués", SOUS in px)
        v("... de ceux qui le dégagent", AU_DESSUS in px)
        v("le plancher est tracé", PLANCHER in px)
        v("la marge est tracée", MARGE_C in px)
        v("la bande de cible est chiffrée", len(r["cibles"]) == 2, str(r["cibles"]))
        # ⚠ La cible DOIT tomber entre les deux profondeurs mesurees -- c'est ce que la
        # figure affirme en pied. Si elle sortait de l'intervalle, la phrase serait fausse.
        v("la cible tombe entre les deux fenêtres mesurées",
          all(41 <= c <= 161 for c in r["cibles"]), str(r["cibles"]))
        f2 = Path(td) / "en.png"
        r2 = dessiner(s, 0.02, 1.33, f2, anglais=True)
        v("aucun libellé ne reste en français", not r2["intraduits"],
          ", ".join(r2["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r2["inchanges"], ", ".join(r2["inchanges"]))
        try:
            dessiner([], 0.02, 1.33, Path(td) / "v.png")
            v("une figure sans série est refusée", False)
        except ValueError:
            v("une figure sans série est refusée", True)

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=Path("docs/fenetre_utilisable.json"))
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/51_fenetre.png"))
    ap.add_argument("--prefixe", default="data/paris4_candidats/ps256")
    ap.add_argument("--plancher", type=float, default=0.02)
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not a.json.is_file():
        print(f"absent : {a.json}", file=sys.stderr)
        return 2
    j = json.loads(a.json.read_text(encoding="utf-8"))
    s = depuis_le_json(j, a.prefixe)
    if not s:
        print(f"aucune série sous « {a.prefixe} »", file=sys.stderr)
        return 2
    r = dessiner(s, a.plancher, float(j.get("marge_recommandation") or 1.33),
                 a.sortie, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ non traduits : " + ", ".join(r["intraduits"] + r["inchanges"]),
              file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, {r['series']} séries, "
          f"cibles {r['cibles']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
