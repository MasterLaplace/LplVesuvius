#!/usr/bin/env python3
"""Huit candidats, trois propriétés, et un résultat qui ne dépend d'aucune des trois.

⚠⚠ **La difficulté de cette figure est que les trois propriétés ne sont pas comparables.** La
planarité tient sur 0,0130 (les huit sont à 1,3 % les unes des autres), l'occupation varie
d'un facteur **trente-cinq**, le nombre de voisins d'un facteur trois. Les mettre sur une
échelle commune de 0 à 1 dessinerait huit barres de planarité identiques — vrai, mais illisible
— et sur une échelle propre à chacune, la planarité **remplirait** sa colonne comme si elle
variait autant que le reste. C'est faux dans l'autre sens, et c'est le mensonge le plus facile
à commettre ici.

⭐ Le remède : chaque colonne est tracée sur **sa propre étendue observée**, et cette étendue
est **écrite en toutes lettres au-dessus**. Le lecteur voit alors une barre pleine surmontée
de « 0,987 → 1,000 » et comprend seul que le remplissage ne veut rien dire. L'échelle est
dans le titre de la colonne, pas dans une note de bas de page.

⚠ Le résultat, lui, n'est pas une propriété continue : il se lit en deux blocs séparés par le
rouleau, et c'est **tout le propos**. Le fond des deux groupes est teinté différemment pour
qu'on le voie avant d'avoir lu un seul chiffre.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import police  # noqa: E402

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
BARRE = (86, 104, 132)
TRAVERSE = (176, 88, 62)      # α ≥ seuil : la surface est en travers de l'empilement
PLAT = (196, 168, 96)         # profil plat : aucune mesure possible
GROUPE_A = (243, 241, 236)
GROUPE_B = (247, 244, 238)

# ⚠ La table est complete ou la figure le DIT : `langue.Traduisant` collecte tout libelle
# non traduit et le fichier refuse de se taire dessus. Une figure a moitie traduite est pire
# qu une figure francaise dans un article anglais -- elle a l air relue.
ANGLAIS = {
    "Huit graines candidates de PHercParis4": "Eight candidate seeds on PHercParis4",
    "les propriétés varient beaucoup ; le résultat ne varie que par rouleau":
        "the properties vary widely; the outcome varies only by prediction",
    "planarité": "planarity",
    "occupation": "occupancy",
    "voisins": "neighbours",
    "résultat du test de convergence": "convergence test outcome",
    "condamnation au-delà de α = ": "condemned beyond α = ",
    "profil plat — aucun α mesurable": "flat profile — no α measurable",
    " candidats · ": " candidates · ",
    " avec un α, tous au-delà du seuil · ": " with an α, all beyond the threshold · ",
    " profils plats · aucune convergence": " flat profiles · no convergence",
}


def _pixels(im):
    """Les pixels d'une image, quelle que soit la version de Pillow.

    ⚠ `getdata` est déprécié depuis Pillow 12 et disparaît en 14 ; `get_flattened_data`
    n'existe pas avant. Une sonde qui échoue sur une dépréciation ne dit rien du dessin.
    """
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())




def etendues(lignes: list[dict], clefs: tuple[str, ...]) -> dict[str, tuple[float, float]]:
    """L'étendue observée de chaque propriété, pour que sa colonne soit tracée dessus.

    ⚠ Une étendue nulle (toutes les valeurs égales) est renvoyée telle quelle : le tracé doit
    la traiter comme un cas à part et non diviser par zéro, et surtout **ne pas** l'élargir
    artificiellement — une propriété constante doit se voir constante.
    """
    out = {}
    for c in clefs:
        v = [l[c] for l in lignes if isinstance(l.get(c), (int, float))]
        out[c] = (min(v), max(v)) if v else (0.0, 0.0)
    return out


def fraction(valeur: float, bornes: tuple[float, float]) -> float:
    """Où tombe une valeur dans son étendue, entre 0 et 1.

    ⚠ Étendue nulle → **1,0**, pas 0,0 : huit valeurs identiques doivent donner huit barres
    pleines et identiques. Rendre 0 dessinerait huit barres vides, ce qui se lit comme « cette
    propriété vaut zéro » alors qu'elle vaut peut-être son maximum.
    """
    lo, hi = bornes
    if hi <= lo:
        return 1.0
    return (valeur - lo) / (hi - lo)


def dessiner(lignes: list[dict], sortie: Path, seuil: float = 0.7,
             anglais: bool = False) -> dict:
    clefs = ("planarite", "occupation", "voisins")
    titres = {"planarite": "planarité", "occupation": "occupation", "voisins": "voisins"}
    et = etendues(lignes, clefs)

    marge, hl, x0 = 26, 34, 150
    largeur_col = 130
    # ⚠⚠ La place des etiquettes est MESUREE avec la police, jamais devinee. Ma premiere
    # version reservait 18 px « qui avaient l air d aller » : les valeurs debordaient sur la
    # colonne suivante et les alpha sortaient du cadre. Une marge estimee a l oeil est une
    # marge fausse des que la police change.
    mesure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    p, pp, pg = police(13, 11, 15)
    larg_val = max(mesure.textlength(t, font=pp) for t in ("0.000", "27", "1.000"))
    ecart = int(larg_val) + 14
    txt_plat = "profil plat — aucun α mesurable"
    larg_droite = max(mesure.textlength(f"{-1.23:+.2f}", font=pp),
                      mesure.textlength(txt_plat, font=pp) - 60) + 12
    x_alpha = x0 + 3 * (largeur_col + ecart) + 20
    larg_alpha = 210
    L = int(x_alpha + larg_alpha + larg_droite + marge)
    H = marge + 74 + len(lignes) * hl + 56

    img = Image.new("RGB", (L, H), FOND)
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)
    xmax = 0.0   # ⚠ le point le plus a droite reellement dessine, pour pouvoir l asserter
    # ⚠⚠ Le chevauchement entre colonnes est un defaut DIFFERENT du hors-cadre, et une
    # sonde a montre que le second ne l attrape pas : reduire l ecart retrecit aussi le
    # cadre, donc tout reste dedans en se recouvrant. Il faut mesurer la place libre
    # entre la fin d une etiquette et le debut de la colonne suivante.
    place_libre = ecart - 4 - larg_val
    d.text((marge, marge - 6), "Huit graines candidates de PHercParis4",
           fill=ENCRE, font=pg)
    d.text((marge, marge + 15),
           "les propriétés varient beaucoup ; le résultat ne varie que par rouleau",
           fill=GRIS, font=pp)

    y_head = marge + 46
    for i, c in enumerate(clefs):
        x = x0 + i * (largeur_col + ecart)
        d.text((x, y_head), titres[c], fill=ENCRE, font=p)
        lo, hi = et[c]
        fmt = "{:.0f}" if c == "voisins" else "{:.4f}"
        # ⚠⚠ L'echelle est ECRITE au-dessus de la colonne : sans elle, une barre pleine de
        # planarite se lirait comme une variation, alors que les huit tiennent a 1,3 %.
        d.text((x, y_head + 15), f"{fmt.format(lo)} → {fmt.format(hi)}", fill=GRIS, font=pp)
    d.text((x_alpha, y_head), "résultat du test de convergence", fill=ENCRE, font=p)
    d.text((x_alpha, y_head + 15), "condamnation au-delà de α = " + f"{seuil}",
           fill=GRIS, font=pp)

    y = y_head + 40
    groupe_precedent = None
    for l in lignes:
        pred = l["prediction"]
        if groupe_precedent is not None and pred != groupe_precedent:
            d.line([(marge, y - 3), (L - marge, y - 3)], fill=GRIS, width=1)
        fond = GROUPE_A if pred == lignes[0]["prediction"] else GROUPE_B
        d.rectangle([marge, y, L - marge, y + hl - 4], fill=fond)
        d.text((marge + 4, y + 8), f"{pred} c{l['candidat']}", fill=ENCRE, font=p)

        for i, c in enumerate(clefs):
            x = x0 + i * (largeur_col + ecart)
            d.rectangle([x, y + 10, x + largeur_col, y + hl - 12], outline=(220, 218, 213))
            v = l.get(c)
            if isinstance(v, (int, float)):
                w = max(2, int(largeur_col * fraction(float(v), et[c])))
                d.rectangle([x, y + 10, x + w, y + hl - 12], fill=BARRE)
                txt = f"{v:.0f}" if c == "voisins" else f"{v:.3f}"
                d.text((x + largeur_col + 4, y + 9), txt, fill=GRIS, font=pp)
                xmax = max(xmax, x + largeur_col + 4 + mesure.textlength(txt, font=pp))

        a = l.get("alpha")
        if isinstance(a, (int, float)):
            # ⚠ L'axe d'alpha commence a 0 et va a 1,4 : le seuil doit etre VISIBLE dedans,
            # sinon « au-dela du seuil » est une affirmation que la figure ne montre pas.
            xa = x_alpha + int(larg_alpha * min(1.0, max(0.0, a / 1.4)))
            xs = x_alpha + int(larg_alpha * (seuil / 1.4))
            d.line([(x_alpha, y + hl // 2), (x_alpha + larg_alpha, y + hl // 2)],
                   fill=(220, 218, 213), width=1)
            d.line([(xs, y + 8), (xs, y + hl - 10)], fill=GRIS, width=1)
            d.ellipse([xa - 5, y + hl // 2 - 5, xa + 5, y + hl // 2 + 5], fill=TRAVERSE)
            t = f"{a:+.2f}"
            d.text((x_alpha + larg_alpha + 4, y + 9), t, fill=TRAVERSE, font=pp)
            xmax = max(xmax, x_alpha + larg_alpha + 4 + mesure.textlength(t, font=pp))
        else:
            d.rectangle([x_alpha, y + 12, x_alpha + 60, y + hl - 14], fill=PLAT)
            d.text((x_alpha + 68, y + 9), txt_plat, fill=GRIS, font=pp)
            xmax = max(xmax, x_alpha + 68 + mesure.textlength(txt_plat, font=pp))
        groupe_precedent = pred
        y += hl

    mes = sum(1 for l in lignes if isinstance(l.get("alpha"), (int, float)))
    d.text((marge, y + 14),
           f"{len(lignes)}" + " candidats · " + f"{mes}"
           + " avec un α, tous au-delà du seuil · " + f"{len(lignes) - mes}"
           + " profils plats · aucune convergence",
           fill=ENCRE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"candidats": len(lignes), "avec_alpha": mes, "largeur": L, "hauteur": H,
            "bord_droit_dessine": round(xmax, 1), "deborde": xmax > L - 2,
            "place_entre_colonnes": round(place_libre, 1),
            "colonnes_se_chevauchent": place_libre < 0,
            "intraduits": d.intraduits(), "inchanges": d.inchanges(),
            "etendues": {k: list(v) for k, v in et.items()}}


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    # ⚠⚠ La sonde qui porte la figure : une propriete quasi constante ne doit pas etre
    # tracee comme si elle variait, et une propriete EXACTEMENT constante ne doit pas
    # disparaitre. Les deux erreurs sont silencieuses.
    e = etendues([{"planarite": 0.987}, {"planarite": 1.0}], ("planarite",))
    v("l'étendue observée est calculée", abs(e["planarite"][1] - 1.0) < 1e-9)
    v("une valeur au minimum donne une barre vide", fraction(0.987, e["planarite"]) == 0.0)
    v("... au maximum, une barre pleine", fraction(1.0, e["planarite"]) == 1.0)
    v("une étendue NULLE donne une barre pleine, pas vide", fraction(5.0, (5.0, 5.0)) == 1.0)
    v("... et n'est pas élargie artificiellement",
      etendues([{"x": 5.0}, {"x": 5.0}], ("x",))["x"] == (5.0, 5.0))

    import tempfile
    base = [{"prediction": "m7", "candidat": i, "planarite": 1.0 - 0.004 * i,
             "occupation": 0.75 - 0.08 * i, "voisins": 9 + 4 * i,
             "alpha": None, "verdict": "indecidable"} for i in range(5)]
    base += [{"prediction": "ps256", "candidat": i, "planarite": 0.9977 - 0.002 * i,
              "occupation": 0.02 + 0.22 * i, "voisins": 15 + 5 * i,
              "alpha": 1.01 + 0.08 * i, "verdict": "traverse"} for i in range(3)]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "c.png"
        r = dessiner(base, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les huit candidats sont dessinés", r["candidats"] == 8)
        v("les α mesurés sont comptés", r["avec_alpha"] == 3)
        im = Image.open(f).convert("RGB")
        px = _pixels(im)
        v("la couleur « en travers » apparaît", TRAVERSE in px)
        v("la couleur « profil plat » apparaît", PLAT in px)
        # ⚠ Controle : sans profil plat, la couleur du plat ne doit PAS etre dessinee,
        # sinon le marqueur ne distingue rien et la figure ment sur ce qu elle montre.
        f2 = Path(td) / "c2.png"
        dessiner([dict(x, alpha=1.0, verdict="traverse") for x in base], f2)
        v("... et disparaît quand aucun profil n'est plat",
          PLAT not in _pixels(Image.open(f2).convert("RGB")))
        # ⚠ Les deux groupes ont deux fonds : sans ca, « le resultat ne varie que par
        # rouleau » est une affirmation que la figure ne montre pas.
        v("les deux rouleaux ont deux fonds", GROUPE_A in px and GROUPE_B in px)
        v("l'image n'est pas dégénérée", r["largeur"] > 600 and r["hauteur"] > 300)
        # ⚠⚠ La sonde qui manquait : rien ne doit etre dessine hors du cadre. Ma premiere
        # version se contentait de verifier que l image etait grande, et les alpha etaient
        # coupes -- une figure qui a l air correcte tant qu on ne la REGARDE pas.
        v("rien n'est dessiné hors du cadre", not r["deborde"],
          f"bord {r['bord_droit_dessine']} pour une largeur {r['largeur']}")
        v("les étiquettes ne mordent pas la colonne suivante",
          not r["colonnes_se_chevauchent"], f"place {r['place_entre_colonnes']} px")
        v("... et la marge droite est réellement laissée",
          r["bord_droit_dessine"] <= r["largeur"] - 20,
          f"{r['bord_droit_dessine']} / {r['largeur']}")
        # ⚠ Controle : un texte long doit AGRANDIR l image, sinon la mesure ne sert a rien.
        long = [dict(x, alpha=None, verdict="indecidable") for x in base]
        v("une figure toute en profils plats reste dans son cadre",
          not dessiner(long, Path(td) / "c4.png")["deborde"])
        # ⚠⚠ La table anglaise doit etre COMPLETE : un libelle oublie sort en francais au
        # milieu d un article anglais, et rien ne le signale a la lecture d un PDF.
        ra = dessiner(base, Path(td) / "en.png", anglais=True)
        v("aucun libellé ne reste en français", not ra["intraduits"],
          ", ".join(ra["intraduits"]))
        # ⚠⚠ Le controle FORT, et le seul des deux qui attrape un nom commun oublie :
        # `intraduits` cherche des mots-temoins francais, et « voisins » n en contient
        # aucun -- sonde faite, la table amputee de cette cle restait verte. Ici on
        # demande a la table d avoir EU UN EFFET sur chaque libelle porteur d un mot.
        # ⚠ Les exceptions sont nommees une par une : les tolerer en silence rouvrirait
        # le trou. Ici, aucune -- cette figure ne dessine aucun nom propre.
        v("chaque libellé porteur d'un mot a été touché par la table",
          not ra["inchanges"], ", ".join(ra["inchanges"]))
        v("la version anglaise se dessine", (Path(td) / "en.png").stat().st_size > 0)
        v("... et reste dans son cadre", not ra["deborde"])
        f3 = Path(td) / "c3.png"
        r3 = dessiner(base[:1], f3)
        v("un seul candidat se dessine encore", f3.is_file() and r3["candidats"] == 1)

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=Path("docs/paris4_candidats.json"))
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/48_candidats.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    d = json.loads(a.json.read_text(encoding="utf-8"))
    lignes = d.get("lignes") or d.get("candidats_detail") or []
    if not lignes:
        print(f"aucune ligne de candidat dans {a.json}", file=sys.stderr)
        return 2
    r = dessiner(lignes, a.sortie, anglais=a.anglais)
    if a.anglais and r["intraduits"]:
        print("  ⚠ libellés non traduits : " + ", ".join(r["intraduits"]),
              file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, "
          f"{r['candidats']} candidats, {r['avec_alpha']} avec un α)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
