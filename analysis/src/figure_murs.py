#!/usr/bin/env python3
"""L'espace de causes, mur par mur, et ce qu'il en reste.

⚠⚠ POURQUOI CETTE FIGURE. Le tableau de [`55`](../docs/55_les_murs_et_leurs_causes.md) dit
tout, et il le dit en trois écrans. Ce qu'on ne voit pas dans un tableau, c'est la **forme** :
que trois murs sur quatre n'ont plus rien d'ouvert, et que celui qui reste ouvert est aussi
celui où le plus de choses ont été éliminées.

⭐ Une barre par mur, une case par cause. Ce n'est pas une jauge de progression : rien ne dit
que l'espace est borné, et une cause **absente** du registre n'est pas une cause éliminée,
c'est une cause à laquelle personne n'a pensé. Ce que la figure montre est ce qui a été
**testé**, jamais ce qui est possible — et la note en bas le dit, parce qu'une barre invite
naturellement à la lire comme un pourcentage d'avancement.

⚠ Les comptes ne sont pas recopiés : ils viennent de `murs_et_causes.compte()`, et la
batterie exige qu'ils s'accordent avec le tableau. Deux dessins d'un même registre libres de
diverger, c'est la panne que le `55` existe pour empêcher.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw  # noqa: E402

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
COULEUR = {
    "confirmée": (74, 132, 96),
    "éliminée": (176, 178, 182),
    "ouverte": (198, 148, 52),
    "bloquée": (196, 72, 60),
}

ANGLAIS = {
    "l'espace de causes, mur par mur": "the space of causes, wall by wall",
    "une case = une cause candidate": "one cell = one candidate cause",
    "confirmée": "confirmed", "éliminée": "eliminated",
    "ouverte": "open", "bloquée": "blocked",
    "⚠ une cause absente n'est pas une cause éliminée : c'est une cause à laquelle personne n'a pensé":
        "⚠ a cause missing here is not an eliminated cause: it is one nobody thought of",
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


def dessiner(rangs: list[dict], sortie: Path, anglais: bool = False) -> dict:
    """Une barre par mur, une case par cause, dans l'ordre du registre."""
    if not rangs:
        raise ValueError("aucun mur — une figure vide serait une figure qui ment")
    from murs_et_causes import VERDICTS

    g1, g2, g3 = _police()
    intraduits, inchanges = [], []

    def T(txt: str) -> str:
        if not anglais:
            return txt
        out = txt
        # ⚠⚠ DU PLUS LONG AU PLUS COURT. Sans ça une entrée courte remplace un morceau d'une
        # entrée longue avant que celle-ci n'ait sa chance : « éliminée » a été substitué à
        # l'intérieur de la note de bas de page, qui est ressortie à moitié traduite et a fait
        # rougir la batterie. Trier par longueur rend l'ordre du dictionnaire sans importance.
        for fr, en in sorted(ANGLAIS.items(), key=lambda kv: -len(kv[0])):
            out = out.replace(fr, en)
        if out == txt and any(c.isalpha() for c in txt):
            inchanges.append(txt)
        if any(c in out for c in "éèêàùôîçâû"):
            intraduits.append(out)
        return out

    case, ecart = 22, 3
    marge, gauche = 24, 300
    largeur_max = max(sum(r["compte"].values()) for r in rangs)
    largeur = gauche + largeur_max * (case + ecart) + marge + 70
    haut = 74
    hauteur = haut + len(rangs) * (case + 16) + 78
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)
    d.text((marge, 16), T("l'espace de causes, mur par mur"), font=g1, fill=ENCRE)
    d.text((marge, 38), T("une case = une cause candidate"), font=g3, fill=GRIS)

    # ⚠ La légende AVANT les barres : sans elle, quatre gris se lisent comme un dégradé.
    x = gauche
    for v in VERDICTS:
        if not any(r["compte"].get(v) for r in rangs):
            continue
        d.rectangle([x, 40, x + 12, 52], fill=COULEUR[v])
        t = T(v)
        d.text((x + 17, 39), t, font=g3, fill=GRIS)
        x += 17 + int(d.textlength(t, font=g3)) + 18

    cases = 0
    y = haut
    for r in rangs:
        nom = r["mur"]
        nom = f"{nom[0].upper()}{nom[1:]}"
        lignes = nom if len(nom) <= 44 else nom[:43] + "…"
        d.text((marge, y + 4), lignes, font=g2, fill=ENCRE)
        x = gauche
        # ⚠ L'ordre des cases suit le VOCABULAIRE et non le registre — éliminées, confirmées,
        # ouvertes, bloquées — pour que le reste à faire tombe au même endroit sur chaque
        # ligne : tout à droite. Suivre l'ordre du registre mettrait l'ouverte au milieu d'un
        # mur et à la fin d'un autre, et l'œil ne pourrait plus les compter d'un coup.
        for v in VERDICTS:
            for _ in range(r["compte"].get(v, 0)):
                d.rectangle([x, y, x + case, y + case], fill=COULEUR[v])
                x += case + ecart
                cases += 1
        reste = r["compte"].get("ouverte", 0) + r["compte"].get("bloquée", 0)
        d.text((x + 8, y + 4),
               "—" if reste == 0 else f"{reste}", font=g2,
               fill=GRIS if reste == 0 else COULEUR["ouverte"])
        y += case + 16

    d.line([(marge, hauteur - 54), (largeur - marge, hauteur - 54)], fill=TRAIT, width=1)
    d.text((marge, hauteur - 48),
           T("⚠ une cause absente n'est pas une cause éliminée : c'est une cause à laquelle "
             "personne n'a pensé"), font=g3, fill=GRIS)
    total = {}
    for r in rangs:
        for v, n in r["compte"].items():
            total[v] = total.get(v, 0) + n
    d.text((marge, hauteur - 28),
           " · ".join(f"{total[v]} {T(v)}{'s' if total[v] > 1 else ''}"
                      for v in VERDICTS if total.get(v)), font=g2, fill=ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"murs": len(rangs), "cases": cases, "largeur": largeur, "hauteur": hauteur,
            "total": total, "intraduits": intraduits, "inchanges": inchanges}


def rangs_du_registre() -> list[dict]:
    """Un rang par mur, avec ses comptes — pris dans le registre, jamais recopiés."""
    from murs_et_causes import compte, lire, murs

    entrees = lire()
    return [{"mur": m, "compte": {k: v for k, v in
                                  compte([e for e in entrees if e["mur"] == m]).items() if v}}
            for m in murs(entrees)]


def _verifier() -> int:
    import tempfile

    from murs_et_causes import compte, lire

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    rangs = rangs_du_registre()
    v("le registre donne des murs", len(rangs) > 0)
    # ⚠⚠ LE CONTRÔLE QUI PORTE LA FIGURE : ses comptes sont ceux du tableau. Deux dessins d'un
    # même registre libres de diverger, c'est la panne que le `55` existe pour empêcher.
    ref = compte(lire())
    total = {}
    for r in rangs:
        for k, n in r["compte"].items():
            total[k] = total.get(k, 0) + n
    v("les comptes de la figure sont ceux du tableau",
      all(total.get(k, 0) == n for k, n in ref.items() if n), f"{total} contre {ref}")

    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(rangs, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("il y a une case par cause", r["cases"] == sum(ref.values()),
          f"{r['cases']} contre {sum(ref.values())}")
        px = _pixels(Image.open(f).convert("RGB"))
        for k, n in ref.items():
            if n:
                v(f"la couleur « {k} » est tracée", COULEUR[k] in px)
        # ⚠ Cas négatif : un registre sans ouverte ne doit poser AUCUNE case ambre.
        sans = [{"mur": "x", "compte": {"éliminée": 3}}]
        f2 = Path(td) / "b.png"
        dessiner(sans, f2)
        v("sans cause ouverte, aucune case ambre",
          COULEUR["ouverte"] not in _pixels(Image.open(f2).convert("RGB")))
        try:
            dessiner([], Path(td) / "c.png")
            v("une figure sans mur est refusée", False)
        except ValueError:
            v("une figure sans mur est refusée", True)
        f3 = Path(td) / "en.png"
        r3 = dessiner(rangs, f3, anglais=True)
        v("aucun libellé ne reste en français", not r3["intraduits"],
          ", ".join(r3["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r3["inchanges"], ", ".join(r3["inchanges"]))

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/images/55_espace_de_causes.png"))
    p.add_argument("--anglais", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return _verifier()
    rangs = rangs_du_registre()
    r = dessiner(rangs, a.sortie, a.anglais)
    print(f"écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, {r['murs']} murs, "
          f"{r['cases']} causes)")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"sortie": str(a.sortie), "murs": r["murs"],
                                      "cases": r["cases"], "total": r["total"]}, indent=2),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
