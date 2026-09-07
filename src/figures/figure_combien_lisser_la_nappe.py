#!/usr/bin/env python3
"""Combien faut-il lisser la nappe ? Le balayage, et pourquoi il n'autorise rien.

⚠⚠⚠ CE QUE CETTE FIGURE EXISTE POUR MONTRER, et c'est un desaccord plutot qu'un resultat. Le
cout en ERREUR designe une fenetre bien plus large que celle qui tourne, avec un gain de vingt-
six micrometres qui TRANCHE hors echantillon. Le cout en BRAS — celui du but — dit l'inverse a
l'ancre dont la marche va quelque part : la portee y tombe de cinq a ZERO.

⚠⚠ La raison est dans la definition du premier cout : la mediane des erreurs par bras inclut les
bras ou la marche est DEJA PERDUE. Passer de cent vingt a soixante-dix micrometres sur une marche
perdue n'est pas un progres — les deux sont au-dela de la demi-feuille — donc un reglage choisi
la-dessus est choisi sur la qualite de ses echecs.

Usage :
    uv run python src/figures/figure_combien_lisser_la_nappe.py --verifier
    uv run python src/figures/figure_combien_lisser_la_nappe.py \\
        --sortie docs/images/75_combien_lisser_la_nappe.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402
from lecart_apparie import tranche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "combien_lisser_la_nappe.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
TURQUOISE = (26, 128, 128)
ROUGE = (188, 68, 52)
AMBRE = (185, 110, 25)
GRIS = (135, 135, 135)
PALE = (243, 231, 227)
CADRE = (200, 200, 200)
ANCRES = ((26, 128, 128), (54, 88, 132), (124, 80, 140), (76, 122, 84), (150, 110, 40))


def prose(m: dict) -> list[str]:
    e, eb = m["ecart_au_deploye"], m["ecart_du_deploye_au_brut"]
    plates = m["ancres_dont_la_portee_ne_bouge_jamais"]
    pire = m["ancres_dont_la_portee_empire"]
    return [
        f"le reglage est choisi HORS ECHANTILLON : chaque ancre est jugee a l'etage que les "
        f"{m['ancres'] - 1} AUTRES ont prefere. ⚠ un etage choisi sur les memes cas que ceux qui "
        "le jugent ne peut que gagner — il suffit d'en essayer neuf pour que l'un tombe bien.",
        f"⚠⚠⚠ PANNEAU A : le cout en ERREUR designe une fenetre bien plus large que celle qui "
        f"tourne, et le gain TRANCHE : {e['ecart_median_um']:+.1f} um sur "
        f"{e['pas_ameliores']}/{e['pas']} ancres, intervalle {e['intervalle_um']}. la famille a "
        f"ete ETENDUE jusqu'a ce que l'optimum ne soit plus au bord — il l'etait a la premiere "
        f"version, et un optimum au bord est un plancher de ce qu'on a essaye, jamais une "
        f"propriete de la matiere (l'optimum est-il au bord : "
        f"{'OUI' if m['loptimum_est_au_bord'] else 'non'}).",
        f"⚠⚠⚠ PANNEAU B DIT L'INVERSE, et c'est lui qui parle du but. la PORTEE empire a "
        f"l'ancre {', '.join(str(m['lignes'][i]['ancre']) for i in pire) if pire else '—'} — la "
        "seule dont la marche va quelque part — en tombant de cinq bras a ZERO. le cout en "
        "erreur est la MEDIANE des erreurs par bras, et cette mediane inclut les bras ou la "
        "marche est DEJA PERDUE : passer de 120 a 70 um sur une marche perdue n'est pas un "
        "progres, les deux sont au-dela de la demi-feuille.",
        f"⚠⚠ et le cout en BRAS ne peut RIEN discriminer ici : aux ancres "
        f"{', '.join(str(m['lignes'][i]['ancre']) for i in plates)} la portee est la MEME a tous "
        f"les etages, donc sa mediane ne separe pas et son « choix » est le premier de la liste. "
        "c'est une limite du materiau, pas de l'instrument — il faudrait des ancres dont la "
        "marche soit vivante.",
        f"⚠⚠⚠ DONC LE BALAYAGE N'AUTORISE PAS A CHANGER LE REGLAGE DEPLOYE, et la porte est fermee "
        f"par defaut : il faudrait que l'optimum ne soit pas au bord, que le gain tranche, ET "
        f"qu'aucune ancre ne voie sa portee diminuer. et ce qui RESTE de ce balayage est un fait "
        f"a garder : a l'ancre {m['lignes'][0]['ancre']}, la fenetre median_8 donne une portee "
        f"de {m['lignes'][0]['portees'][4]} — le plafond du corpus, celui que la borne atteint. "
        "une fenetre large PEUT atteindre la borne ; la largeur qui marche depend de l'ancre, et "
        "hors echantillon on ne la trouve pas.",
        f"⚠ pour memoire, le resultat de la tranche precedente se reproduit sur ces memes "
        f"ancres : l'etage deploye bat le brut de {eb['ecart_median_um']:+.1f} um sur "
        f"{eb['pas_ameliores']}/{eb['pas']} ancres, intervalle {eb['intervalle_um']} — "
        f"{'il tranche' if tranche(eb) else 'il ne tranche pas'}. lisser vaut mieux que ne pas "
        "lisser ; c'est COMBIEN qui n'est pas tranche.",
    ]


def panneau_couts(art, x0, y0, pw, ph, m, petit) -> None:
    """Le cout en erreur de chaque etage, une courbe par ancre."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "mediane des erreurs par bras · une courbe par ancre",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "cercle : l'etage que les AUTRES ancres ont choisi",
             fill=ROUGE, font=petit)
    noms = m["etages"]
    gauche, droite = x0 + 50, x0 + pw - 24
    base, sommet = y0 + ph - 46, y0 + 40
    tous = [c for x in m["lignes"] for c in x["couts_um"]]
    haut = max(tous) * 1.08

    def px(i: int) -> float:
        return gauche + (droite - gauche) * i / max(1, len(noms) - 1)

    def py(v: float) -> float:
        return base - (base - sommet) * v / haut

    # ⚠ La demi-feuille est dessinée : au-dessus, la marche est perdue, donc tout gain y est un
    # gain sur un échec. C'est la lecture que le panneau B rend explicite.
    art.rectangle([gauche - 8, sommet, droite + 8, py(67.75)], fill=PALE)
    art.line([gauche - 8, py(67.75), droite + 8, py(67.75)], fill=ROUGE)
    art.text((gauche + 4, py(67.75) - 14), "au-dessus : la marche est perdue", fill=ROUGE,
             font=petit)
    art.line([gauche, base, droite, base], fill=TEXTE)
    for i, x in enumerate(m["lignes"]):
        coul = ANCRES[i % len(ANCRES)]
        pts = [(px(j), py(c)) for j, c in enumerate(x["couts_um"])]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        j = noms.index(x["etage_choisi_par_les_autres"])
        art.ellipse([px(j) - 7, py(x["couts_um"][j]) - 7, px(j) + 7, py(x["couts_um"][j]) + 7],
                    outline=ROUGE, width=2)
        art.text((droite + 4, pts[-1][1] - 6), str(x["ancre"]), fill=coul, font=petit)
    for g in (50, 100):
        if g < haut:
            art.text((gauche - 44, py(g) - 6), f"{g:>4}", fill=DISCRET, font=petit)
    for j, n in enumerate(noms):
        art.text((px(j) - 16, base + 8), n.replace("median_", "m"), fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 16), "um · abscisse : l'etage de lissage (m = median)",
             fill=DISCRET, font=petit)


def panneau_portees(art, x0, y0, pw, ph, m, petit) -> None:
    """La portee de chaque etage, et la part de nappe reellement lissee."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "portee, une courbe par ancre · barres : part de nappe lissee",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "une fenetre large est REFUSEE pres des bords, donc elle "
             "s'applique moins", fill=DISCRET, font=petit)
    noms = m["etages"]
    gauche, droite = x0 + 44, x0 + pw - 24
    base, sommet = y0 + ph - 46, y0 + 40
    haut = max([p for x in m["lignes"] for p in x["portees"]]) + 1

    def px(i: int) -> float:
        return gauche + (droite - gauche) * i / max(1, len(noms) - 1)

    def py(v: float) -> float:
        return base - (base - sommet) * v / haut

    larg = (droite - gauche) / max(1, len(noms)) * 0.5
    # ⚠ Les barres portent une FRACTION, donc leur hauteur se lit sur toute la boîte du panneau
    # et non sur l'échelle des portées : mélanger les deux ferait lire une part de nappe comme
    # un nombre de bras.
    for j, part in enumerate(m["parts_lissees_par_etage"]):
        haut_barre = base - (base - sommet) * float(part)
        art.rectangle([px(j) - larg / 2, min(haut_barre, base), px(j) + larg / 2,
                       max(haut_barre, base)], fill=(234, 239, 241))
    art.line([gauche, base, droite, base], fill=TEXTE)
    for i, x in enumerate(m["lignes"]):
        coul = ANCRES[i % len(ANCRES)]
        pts = [(px(j), py(p)) for j, p in enumerate(x["portees"])]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        j = noms.index(x["etage_choisi_par_les_autres"])
        coul_c = ROUGE if x["portee_hors_echantillon"] < x["portee_deployee"] else TURQUOISE
        art.ellipse([px(j) - 7, py(x["portees"][j]) - 7, px(j) + 7, py(x["portees"][j]) + 7],
                    outline=coul_c, width=2)
        art.text((droite + 4, pts[-1][1] - 6), str(x["ancre"]), fill=coul, font=petit)
    for g in range(1, haut):
        art.text((gauche - 38, py(g) - 6), f"{g:>3}", fill=DISCRET, font=petit)
    for j, n in enumerate(noms):
        art.text((px(j) - 16, base + 8), n.replace("median_", "m"), fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             "bras atteints · cercle ROUGE : la portee EMPIRE a l'etage choisi",
             fill=ROUGE, font=petit)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 500, 34, 300
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Combien faut-il lisser la nappe ? Les deux couts se contredisent",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['ancres']} ancres · {len(m['etages'])} etages · choix HORS ECHANTILLON · "
             f"le balayage autorise un changement : "
             f"{'OUI' if m['le_balayage_autorise_un_changement'] else 'NON'}",
             fill=DISCRET, font=moyen)
    titres = ("A · le cout en ERREUR : la fenetre large gagne",
              "B · le cout en BRAS : elle detruit la seule marche vivante")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_couts(art, marge, 104, pw, ph, m, petit)
    panneau_portees(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"ancres": len(m["lignes"]), "etages": len(m["etages"]), "titres": titres,
            "panneau": pw, "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LA FIGURE EXISTE POUR PORTER UN DÉSACCORD : si les deux coûts s'accordaient, elle
    # dirait autre chose, et sa prose serait fausse. Le contrôle épingle le fait qu'ils ne
    # s'accordent pas — une ancre au moins voit sa portée empirer à l'étage choisi.
    v("les deux coûts se contredisent bien : une ancre au moins voit sa portée empirer",
      bool(m["ancres_dont_la_portee_empire"]),
      str(m["ancres_dont_la_portee_empire"]))
    # ⭐⭐⭐ ET LA PORTE EST FERMÉE : la figure annonce « NON » dans son sous-titre, donc le
    # contrôle exige que ce soit ce que la mesure dit.
    v("... et le balayage n'autorise donc PAS de changer le réglage",
      not m["le_balayage_autorise_un_changement"])
    # ⚠⚠ L'OPTIMUM N'EST PLUS AU BORD : c'était la première faute, corrigée en étendant la
    # famille. Si elle revenait, le panneau A publierait un plancher de balayage.
    v("l'optimum n'est pas au bord de la famille balayée",
      not m["loptimum_est_au_bord"], str(m["etages_au_bord"]))
    # ⚠⚠ ET UN ÉTAGE QUI NE LISSE RIEN DOIT ÊTRE VISIBLE : la part lissée est dessinée en
    # barres précisément pour qu'on ne lise pas « cette fenêtre gagne » sur une fenêtre refusée.
    v("la part de nappe lissée est publiée pour chaque étage, et décroît avec la largeur",
      len(m["parts_lissees_par_etage"]) == len(m["etages"])
      and m["parts_lissees_par_etage"][1:7] == sorted(m["parts_lissees_par_etage"][1:7],
                                                      reverse=True),
      str(dict(zip(m["etages"], m["parts_lissees_par_etage"]))))
    v("chaque ancre publie un coût par étage et une portée par étage",
      all(len(x["couts_um"]) == len(m["etages"]) and len(x["portees"]) == len(m["etages"])
          for x in m["lignes"]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les ancres sont dessinées", r["ancres"] == len(m["lignes"]), str(r["ancres"]))
        debord = [(t[:36], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        _, _, pt_ = police(17, 13, 11)
        trop = [(t, pt_.getbbox(t)[2]) for t in r["titres"] if pt_.getbbox(t)[2] >= r["panneau"]]
        v("chaque titre de panneau tient dans son panneau", not trop, str(trop))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_combien_lisser_la_nappe.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
